"""Private, bounded storage for user-managed Clarify Editor notes."""

# pylint: disable=no-name-in-module  # Qt modules are generated dynamically.

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths

DEFAULT_MAX_NOTES = 20
DEFAULT_MAX_NOTE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 20 * 1024 * 1024


class TemporaryNoteError(ValueError):
    """Raised when a note cannot be stored or read safely."""


@dataclass(frozen=True)
class TemporaryNote:
    note_id: str
    title: str
    content: str
    extension: str
    created_at: str
    updated_at: str


class TemporaryNoteStore:
    """Store explicit notes atomically; retention is disabled by default."""

    def __init__(
        self,
        root: str | os.PathLike[str] | None = None,
        *,
        max_notes: int = DEFAULT_MAX_NOTES,
        max_note_bytes: int = DEFAULT_MAX_NOTE_BYTES,
        max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    ):
        base = root or Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / "editor-notes"
        self.root = Path(base)
        self.max_notes = max(1, int(max_notes))
        self.max_note_bytes = max(1, int(max_note_bytes))
        self.max_total_bytes = max(1, int(max_total_bytes))

    @contextmanager
    def _locked(self):
        if self.root.is_symlink():
            raise TemporaryNoteError("Note directory cannot be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        lock = QLockFile(str(self.root / ".notes.lock"))
        if not lock.tryLock(0):
            raise TemporaryNoteError("Note storage is busy or unavailable")
        try:
            yield
        finally:
            lock.unlock()

    def save(
        self,
        note_id: str,
        *,
        title: str,
        content: str,
        extension: str = ".txt",
    ) -> TemporaryNote:
        """Create or update one note without evicting another note."""
        normalized_id = self._normalized_id(note_id)
        if not isinstance(title, str) or not title.strip():
            raise TemporaryNoteError("A note title is required")
        if len(title.encode("utf-8")) > 4096:
            raise TemporaryNoteError("Note title exceeds limit")
        if not isinstance(content, str) or len(content) > self.max_note_bytes:
            raise TemporaryNoteError("Note exceeds bounded extraction limit")
        content_bytes = content.encode("utf-8")
        if len(content_bytes) > self.max_note_bytes:
            raise TemporaryNoteError("Note exceeds storage limit")
        if not isinstance(extension, str) or len(extension.encode("utf-8")) > 256:
            raise TemporaryNoteError("Note extension exceeds limit")
        extension = extension if extension.startswith(".") else f".{extension}"

        with self._locked():
            previous = self._read(self._path(normalized_id))
            now = datetime.now(timezone.utc).isoformat()
            note = TemporaryNote(
                note_id=normalized_id,
                title=title.strip(),
                content=content,
                extension=extension,
                created_at=previous.created_at if previous else now,
                updated_at=now,
            )
            payload = json.dumps(asdict(note), ensure_ascii=False).encode("utf-8")
            if len(payload) > self.max_note_bytes + 32 * 1024:
                raise TemporaryNoteError("Encoded note exceeds storage limit")
            others = [
                path
                for path in self.root.glob("*.json")
                if path != self._path(normalized_id) and self._read(path) is not None
            ]
            if len(others) >= self.max_notes:
                raise TemporaryNoteError("Note count quota reached")
            try:
                total = sum(path.stat().st_size for path in others)
            except OSError as error:
                raise TemporaryNoteError("Could not inspect note storage") from error
            if total + len(payload) > self.max_total_bytes:
                raise TemporaryNoteError("Note storage quota reached")
            self._atomic_write(normalized_id, payload)
            return note

    def list(self) -> list[TemporaryNote]:
        if not self.root.exists():
            return []
        with self._locked():
            notes = []
            for path in self.root.glob("*.json"):
                note = self._read(path)
                if note is None:
                    path.unlink(missing_ok=True)
                else:
                    notes.append(note)
            ordered = sorted(notes, key=lambda item: item.updated_at, reverse=True)
            retained = []
            retained_bytes = 0
            for note in ordered:
                path = self._path(note.note_id)
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                if len(retained) >= self.max_notes or retained_bytes + size > self.max_total_bytes:
                    path.unlink(missing_ok=True)
                    continue
                retained.append(note)
                retained_bytes += size
        return retained

    def get(self, note_id: str) -> TemporaryNote:
        normalized_id = self._normalized_id(note_id)
        if not self.root.exists():
            raise TemporaryNoteError("Note is unavailable")
        with self._locked():
            note = self._read(self._path(normalized_id))
            if note is None:
                raise TemporaryNoteError("Note is unavailable or corrupt")
            return note

    def discard(self, note_id: str) -> None:
        normalized_id = self._normalized_id(note_id)
        if not self.root.exists():
            return
        with self._locked():
            self._path(normalized_id).unlink(missing_ok=True)

    def expired(self, retention_days: int, *, now=None) -> list[TemporaryNote]:
        """Preview notes older than the configured updated-at cutoff."""
        days = max(0, int(retention_days))
        if days == 0:
            return []
        reference = now or datetime.now(timezone.utc)
        cutoff = reference - timedelta(days=days)
        expired = []
        for note in self.list():
            try:
                updated = datetime.fromisoformat(note.updated_at)
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if updated < cutoff:
                expired.append(note)
        return expired

    def prune(self, retention_days: int, *, now=None) -> int:
        expired = self.expired(retention_days, now=now)
        for note in expired:
            self.discard(note.note_id)
        return len(expired)

    def _atomic_write(self, note_id: str, payload: bytes) -> None:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{note_id}-", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary_name, 0o600)
            os.replace(temporary_name, self._path(note_id))
            if hasattr(os, "O_DIRECTORY"):
                directory_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        finally:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass

    def _read(self, path: Path) -> TemporaryNote | None:
        try:
            if path.is_symlink() or path.stat().st_size > self.max_note_bytes + 32 * 1024:
                return None
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(path, flags)
            with os.fdopen(descriptor, "rb") as handle:
                payload = handle.read(self.max_note_bytes + 32 * 1024 + 1)
            if len(payload) > self.max_note_bytes + 32 * 1024:
                return None
            note = TemporaryNote(**json.loads(payload.decode("utf-8")))
            self._normalized_id(note.note_id)
            if note.note_id != path.stem:
                return None
            if any(
                not isinstance(getattr(note, key), str)
                for key in (
                    "title",
                    "content",
                    "extension",
                    "created_at",
                    "updated_at",
                )
            ):
                return None
            if not note.title.strip() or len(note.title.encode("utf-8")) > 4096:
                return None
            if not note.extension.startswith(".") or len(note.extension.encode("utf-8")) > 256:
                return None
            if len(note.content.encode("utf-8")) > self.max_note_bytes:
                return None
            datetime.fromisoformat(note.created_at)
            datetime.fromisoformat(note.updated_at)
            return note
        except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
            return None

    def _path(self, note_id: str) -> Path:
        return self.root / f"{note_id}.json"

    @staticmethod
    def _normalized_id(note_id: str) -> str:
        if not isinstance(note_id, str):
            raise TemporaryNoteError("Invalid note identifier")
        normalized = "".join(character for character in note_id if character.isalnum() or character in "-_")
        if not normalized or normalized != note_id or len(note_id.encode("utf-8")) > 128:
            raise TemporaryNoteError("Invalid note identifier")
        return normalized
