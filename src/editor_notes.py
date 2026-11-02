"""Private, bounded storage for user-managed Clarify Editor notes."""

# pylint: disable=no-name-in-module  # Qt modules are generated dynamically.

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths

from .utils.atomic_files import write_text_atomically

DEFAULT_MAX_NOTES = 20
DEFAULT_MAX_NOTE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_EXPORT_NOTES = 20
MAX_EXPORT_BYTES = 24 * 1024 * 1024


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
            note_path = self._path(normalized_id)
            previous = self._read(note_path)
            previous_payload = note_path.read_bytes() if previous is not None else None
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
                if path != note_path and self._read(path) is not None
            ]
            if len(others) >= self.max_notes:
                raise TemporaryNoteError("Note count quota reached")
            try:
                total = sum(path.stat().st_size for path in others)
            except OSError as error:
                raise TemporaryNoteError("Could not inspect note storage") from error
            if total + len(payload) > self.max_total_bytes:
                raise TemporaryNoteError("Note storage quota reached")
            available_ids = [
                item.note_id for item in (self._read(path) for path in others) if item
            ]
            available_ids.append(normalized_id)
            order = self._ordered_ids_unlocked(available_ids)
            self._atomic_write(normalized_id, payload)
            try:
                self._write_order_unlocked(order)
            except Exception:
                if previous_payload is None:
                    note_path.unlink(missing_ok=True)
                else:
                    self._atomic_write(normalized_id, previous_payload)
                raise
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
            by_id = {note.note_id: note for note in notes}
            ordered_ids = self._ordered_ids_unlocked(by_id)
            ordered = [by_id[note_id] for note_id in ordered_ids]
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
            retained_ids = [note.note_id for note in retained]
            if retained_ids != ordered_ids:
                self._write_order_unlocked(retained_ids)
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
        self.discard_many([note_id])

    def discard_many(self, note_ids) -> int:
        """Delete notes as one staged operation, rolling back staging failures."""
        normalized = []
        for note_id in note_ids:
            value = self._normalized_id(note_id)
            if value not in normalized:
                normalized.append(value)
        if not normalized or not self.root.exists():
            return 0
        with self._locked():
            existing = [note_id for note_id in normalized if self._path(note_id).exists()]
            for note_id in existing:
                if self._read(self._path(note_id)) is None:
                    raise TemporaryNoteError("Cannot delete unavailable or corrupt note")
            previous_order = self._ordered_ids_unlocked(
                note.note_id
                for note in (
                    self._read(path) for path in self.root.glob("*.json")
                )
                if note is not None
            )
            staged: list[tuple[Path, Path]] = []
            try:
                for note_id in existing:
                    source = self._path(note_id)
                    temporary = self.root / f".{note_id}.delete-{uuid.uuid4().hex}.tmp"
                    os.replace(source, temporary)
                    staged.append((source, temporary))
                self._write_order_unlocked(
                    [note_id for note_id in previous_order if note_id not in existing]
                )
            except Exception as error:
                rollback_errors = []
                for source, temporary in reversed(staged):
                    try:
                        if temporary.exists():
                            os.replace(temporary, source)
                    except OSError as rollback_error:
                        rollback_errors.append(str(rollback_error))
                detail = "Could not delete notes atomically"
                if rollback_errors:
                    detail += "; rollback failed: " + "; ".join(rollback_errors)
                raise TemporaryNoteError(detail) from error
            for _source, temporary in staged:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass
            return len(existing)

    def reorder(self, note_ids) -> None:
        """Persist an explicit order using stable note identifiers."""
        normalized = [self._normalized_id(note_id) for note_id in note_ids]
        if len(normalized) != len(set(normalized)):
            raise TemporaryNoteError("Duplicate note identifier in order")
        with self._locked():
            existing = {
                note.note_id
                for note in (self._read(path) for path in self.root.glob("*.json"))
                if note is not None
            }
            if set(normalized) != existing:
                raise TemporaryNoteError("Note order does not match stored notes")
            self._write_order_unlocked(normalized)

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

    @property
    def _order_path(self) -> Path:
        return self.root / ".notes-order"

    def _ordered_ids_unlocked(self, note_ids) -> list[str]:
        available = list(dict.fromkeys(note_ids))
        available_set = set(available)
        stored = self._read_order_unlocked()
        ordered = [note_id for note_id in stored if note_id in available_set]
        ordered.extend(note_id for note_id in available if note_id not in ordered)
        return ordered

    def _read_order_unlocked(self) -> list[str]:
        path = self._order_path
        if not path.exists() or path.is_symlink():
            return []
        try:
            if path.stat().st_size > self.max_notes * 160 + 1024:
                return []
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, list) or len(value) > self.max_notes:
                return []
            normalized = [self._normalized_id(note_id) for note_id in value]
            if len(normalized) != len(set(normalized)):
                return []
            return normalized
        except (OSError, UnicodeError, ValueError, TypeError):
            return []

    def _write_order_unlocked(self, note_ids) -> None:
        normalized = [self._normalized_id(note_id) for note_id in note_ids]
        if len(normalized) > self.max_notes or len(normalized) != len(set(normalized)):
            raise TemporaryNoteError("Invalid note order")
        write_text_atomically(
            self._order_path,
            json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        )
        os.chmod(self._order_path, 0o600)

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


def _bounded_export_notes(notes) -> list[TemporaryNote]:
    selected = list(notes)
    if len(selected) > MAX_EXPORT_NOTES:
        raise TemporaryNoteError("Too many notes to export")
    total = 0
    for note in selected:
        if not isinstance(note, TemporaryNote):
            raise TemporaryNoteError("Invalid note export input")
        total += len(note.content.encode("utf-8"))
        if total > MAX_EXPORT_BYTES:
            raise TemporaryNoteError("Note export exceeds size limit")
    return selected


def export_notes_bundle(notes, destination) -> Path:
    """Export bounded notes as one versioned JSON document atomically."""
    selected = _bounded_export_notes(notes)
    output = Path(destination)
    payload = {
        "format": "clarify-temporary-notes",
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "notes": [asdict(note) for note in selected],
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if len(encoded.encode("utf-8")) > MAX_EXPORT_BYTES + 128 * 1024:
        raise TemporaryNoteError("Encoded note export exceeds size limit")
    try:
        write_text_atomically(output, encoded)
    except (OSError, UnicodeError, ValueError) as error:
        raise TemporaryNoteError("Could not export notes atomically") from error
    return output


def _safe_export_stem(title: str) -> str:
    stem = re.sub(r"[^\w .-]+", "_", title, flags=re.UNICODE).strip(" .")
    stem = stem or "Temporary Note"
    while len(stem.encode("utf-8")) > 160:
        stem = stem[:-1]
    return stem or "Temporary Note"


def export_notes_separately(notes, destination_directory) -> Path:
    """Publish separate note files through one staged directory rename."""
    selected = _bounded_export_notes(notes)
    parent = Path(destination_directory)
    if parent.is_symlink() or not parent.is_dir():
        raise TemporaryNoteError("Export destination must be a regular directory")
    staging = Path(tempfile.mkdtemp(prefix=".clarify-note-export-", dir=parent))
    os.chmod(staging, 0o700)
    used: set[str] = set()
    try:
        for note in selected:
            stem = _safe_export_stem(note.title)
            extension = note.extension if note.extension.startswith(".") else f".{note.extension}"
            candidate = f"{stem}{extension}"
            index = 2
            while candidate.casefold() in used:
                candidate = f"{stem}-{index}{extension}"
                index += 1
            used.add(candidate.casefold())
            write_text_atomically(staging / candidate, note.content)
        final = parent / (
            "Clarify Temporary Notes "
            + datetime.now().strftime("%Y%m%d-%H%M%S-")
            + uuid.uuid4().hex[:8]
        )
        os.rename(staging, final)
        return final
    except Exception as error:
        shutil.rmtree(staging, ignore_errors=True)
        raise TemporaryNoteError("Could not export notes as separate files") from error
