"""Bounded local snapshots for unsaved Clarify Editor documents."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QLockFile, QStandardPaths


DEFAULT_RETENTION_HOURS = 30 * 24
DEFAULT_MAX_SNAPSHOTS = 20
DEFAULT_MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 20 * 1024 * 1024


class RecoverySnapshotError(ValueError):
    """Raised when a recovery snapshot cannot be stored safely."""


@dataclass(frozen=True)
class RecoverySnapshot:
    snapshot_id: str
    title: str
    content: str
    file_path: str
    extension: str
    updated_at: str
    kind: str = "buffer"
    source_signature: tuple[int, ...] | None = None
    cursor_position: int = 0


@dataclass(frozen=True)
class RecoveryPruneReport:
    """Counts why snapshots were removed during one bounded inventory pass."""

    expired: int = 0
    invalid: int = 0
    over_count: int = 0
    over_total_bytes: int = 0

    @property
    def over_quota(self) -> int:
        return self.over_count + self.over_total_bytes

    @property
    def removed(self) -> int:
        return self.expired + self.invalid + self.over_quota


class UnsavedRecoveryStore:
    """Persist recent unsaved buffers with strict retention and size limits."""

    def __init__(
        self,
        root: str | os.PathLike[str] | None = None,
        *,
        retention_hours: int = DEFAULT_RETENTION_HOURS,
        max_snapshots: int = DEFAULT_MAX_SNAPSHOTS,
        max_document_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES,
        max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    ):
        base = root or Path(
            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        ) / "editor-recovery"
        self.root = Path(base)
        self.retention_hours = max(1, int(retention_hours))
        self.max_snapshots = max(1, int(max_snapshots))
        self.max_document_bytes = max(1, int(max_document_bytes))
        self.max_total_bytes = max(1, int(max_total_bytes))
        self._last_prune_report = RecoveryPruneReport()

    def save(
        self,
        snapshot_id: str,
        *,
        title: str,
        content: str,
        file_path: str = "",
        extension: str = ".txt",
        kind: str = "buffer",
        source_signature: tuple[int, ...] | None = None,
        cursor_position: int = 0,
    ) -> RecoverySnapshot:
        """Atomically save one text snapshot and enforce global bounds."""
        with self._locked():
            return self._save_unlocked(snapshot_id, title=title, content=content,
                                       file_path=file_path, extension=extension, kind=kind,
                                       source_signature=source_signature, cursor_position=cursor_position)

    @contextmanager
    def _locked(self):
        if self.root.is_symlink():
            raise RecoverySnapshotError("Recovery directory cannot be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        lock = QLockFile(str(self.root / '.recovery.lock'))
        if not lock.tryLock(0):
            raise RecoverySnapshotError("Recovery storage is busy or unavailable")
        try:
            yield
        finally:
            lock.unlock()

    def _save_unlocked(self, snapshot_id: str, *, title: str, content: str,
                       file_path: str, extension: str, kind: str,
                       source_signature: tuple[int, ...] | None,
                       cursor_position: int) -> RecoverySnapshot:
        normalized_id = self._normalized_id(snapshot_id)
        if not isinstance(content, str) or len(content) > self.max_document_bytes:
            raise RecoverySnapshotError("Document exceeds recovery limit")
        if kind not in ("buffer", "reference") or (kind == "reference" and (content or not file_path)):
            raise RecoverySnapshotError("Invalid recovery snapshot kind")
        if source_signature is not None and (
            not isinstance(source_signature, (list, tuple)) or len(source_signature) != 5
            or any(not isinstance(value, int) or value < 0 for value in source_signature)
        ):
            raise RecoverySnapshotError("Invalid recovery source revision")
        if not isinstance(cursor_position, int) or cursor_position < 0:
            raise RecoverySnapshotError("Invalid recovery cursor position")
        for value, limit in ((title, 4096), (file_path, 4096), (extension, 256)):
            if not isinstance(value, str) or len(value.encode("utf-8")) > limit:
                raise RecoverySnapshotError("Recovery metadata exceeds limit")
        content_bytes = content.encode("utf-8")
        if len(content_bytes) > self.max_document_bytes:
            raise RecoverySnapshotError(
                f"Document exceeds recovery limit of {self.max_document_bytes} bytes"
            )

        snapshot = RecoverySnapshot(
            snapshot_id=normalized_id,
            title=title or "Untitled",
            content=content,
            file_path=file_path or "",
            extension=extension if extension.startswith(".") else f".{extension}",
            updated_at=datetime.now(timezone.utc).isoformat(),
            kind=kind,
            source_signature=source_signature,
            cursor_position=max(0, int(cursor_position)),
        )
        payload = json.dumps(asdict(snapshot), ensure_ascii=False).encode("utf-8")
        if len(payload) > self.max_document_bytes + 64 * 1024:
            raise RecoverySnapshotError("Encoded recovery snapshot exceeds storage limit")
        self._prune_unlocked()
        existing = [path for path in self.root.glob("*.json") if path != self._path(normalized_id)]
        if len(existing) >= self.max_snapshots:
            raise RecoverySnapshotError("Recovery document quota reached")
        if sum(path.stat().st_size for path in existing) + len(payload) > self.max_total_bytes:
            raise RecoverySnapshotError("Recovery storage quota reached")

        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{normalized_id}-", suffix=".tmp", dir=self.root
        )
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary_name, 0o600)
            os.replace(temporary_name, self._path(normalized_id))
            if hasattr(os, 'O_DIRECTORY'):
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

        return snapshot

    def save_reference(self, snapshot_id: str, *, title: str, file_path: str,
                       extension: str = ".txt", cursor_position: int = 0,
                       source_signature: tuple[int, ...] | None = None) -> RecoverySnapshot:
        """Keep session identity without copying a saved document's contents."""
        return self.save(snapshot_id, title=title, content="", file_path=file_path,
                         extension=extension, kind="reference", cursor_position=cursor_position,
                         source_signature=source_signature)

    @staticmethod
    def source_signature(file_path: str) -> tuple[int, ...] | None:
        """Identify a regular source revision without reading its contents."""
        try:
            info = os.stat(file_path, follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode):
                return None
            return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        except OSError:
            return None

    def read_reference(self, snapshot: RecoverySnapshot) -> str:
        """Read a small unchanged original; never silently recover a newer revision."""
        if snapshot.kind != "reference" or snapshot.source_signature is None:
            raise RecoverySnapshotError("Recovery original is unavailable")
        signature = tuple(snapshot.source_signature)
        if self.source_signature(snapshot.file_path) != signature:
            raise RecoverySnapshotError("Recovery original is missing or changed")
        if signature[2] > self.max_document_bytes:
            raise RecoverySnapshotError("Original exceeds bounded recovery read limit")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(snapshot.file_path, flags)
        with os.fdopen(fd, "rb") as handle:
            info = os.fstat(handle.fileno())
            revision = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            if revision != signature:
                raise RecoverySnapshotError("Recovery original changed before reading")
            payload = handle.read(self.max_document_bytes + 1)
        if len(payload) > self.max_document_bytes or self.source_signature(snapshot.file_path) != signature:
            raise RecoverySnapshotError("Recovery original changed during reading")
        if b'\x00' in payload:
            raise RecoverySnapshotError("Recovery original is not UTF-8 text")
        try:
            return payload.decode("utf-8")
        except UnicodeError as error:
            raise RecoverySnapshotError("Recovery original is not UTF-8 text") from error

    def list(self) -> list[RecoverySnapshot]:
        """Return valid, recent snapshots newest first."""
        if not self.root.exists():
            self._last_prune_report = RecoveryPruneReport()
            return []
        with self._locked():
            self._last_prune_report = self._prune_unlocked()
            snapshots = list(self._read_valid_snapshots())
        return sorted(snapshots, key=lambda item: item.updated_at, reverse=True)

    def list_with_report(
        self,
    ) -> tuple[list[RecoverySnapshot], RecoveryPruneReport]:
        """Return recent snapshots and bounded cleanup reasons from this pass."""
        snapshots = self.list()
        return snapshots, self._last_prune_report

    def discard(self, snapshot_id: str) -> None:
        """Delete one snapshot if present."""
        self._normalized_id(snapshot_id)
        if not self.root.exists():
            return
        with self._locked():
            self._path(self._normalized_id(snapshot_id)).unlink(missing_ok=True)

    def discard_all(self) -> None:
        """Delete all recovery snapshots owned by this store."""
        if not self.root.exists():
            return
        with self._locked():
            for path in self.root.glob("*.json"):
                path.unlink(missing_ok=True)

    def prune(self) -> RecoveryPruneReport:
        """Remove expired, corrupt, excessive, and over-budget snapshots."""
        if not self.root.exists():
            return RecoveryPruneReport()
        with self._locked():
            return self._prune_unlocked()

    def _prune_unlocked(self) -> RecoveryPruneReport:
        if not self.root.exists():
            return RecoveryPruneReport()

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        entries = []
        expired = 0
        invalid = 0
        over_count = 0
        over_total_bytes = 0
        for path in self.root.glob("*.json"):
            snapshot = self._read(path)
            if snapshot is None:
                path.unlink(missing_ok=True)
                invalid += 1
                continue
            try:
                updated = datetime.fromisoformat(snapshot.updated_at)
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
            except ValueError:
                path.unlink(missing_ok=True)
                invalid += 1
                continue
            if updated < cutoff:
                path.unlink(missing_ok=True)
                expired += 1
                continue
            entries.append((updated, path, path.stat().st_size))

        entries.sort(reverse=True)
        retained_bytes = 0
        for index, (_updated, path, size) in enumerate(entries):
            if index >= self.max_snapshots:
                path.unlink(missing_ok=True)
                over_count += 1
            elif retained_bytes + size > self.max_total_bytes:
                path.unlink(missing_ok=True)
                over_total_bytes += 1
            else:
                retained_bytes += size
        return RecoveryPruneReport(
            expired=expired,
            invalid=invalid,
            over_count=over_count,
            over_total_bytes=over_total_bytes,
        )

    def _read_valid_snapshots(self) -> Iterable[RecoverySnapshot]:
        for path in self.root.glob("*.json"):
            snapshot = self._read(path)
            if snapshot is not None:
                yield snapshot

    def _read(self, path: Path) -> RecoverySnapshot | None:
        try:
            if path.is_symlink() or path.stat().st_size > self.max_document_bytes + 64 * 1024:
                return None
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
            fd = os.open(path, flags)
            with os.fdopen(fd, "rb") as handle:
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode):
                    return None
                payload = handle.read(self.max_document_bytes + 64 * 1024 + 1)
            if len(payload) > self.max_document_bytes + 64 * 1024:
                return None
            data = json.loads(payload.decode('utf-8'))
            snapshot = RecoverySnapshot(**data)
            if any(not isinstance(getattr(snapshot, key), str) for key in
                   ("snapshot_id", "title", "content", "file_path", "extension", "updated_at", "kind")):
                return None
            self._normalized_id(snapshot.snapshot_id)
            if snapshot.snapshot_id != path.stem:
                return None
            if snapshot.kind not in ("buffer", "reference"):
                return None
            if any(len(value.encode('utf-8')) > limit for value, limit in
                   ((snapshot.title, 4096), (snapshot.file_path, 4096), (snapshot.extension, 257))):
                return None
            if snapshot.kind == "reference" and (snapshot.content or not snapshot.file_path):
                return None
            if not isinstance(snapshot.cursor_position, int) or snapshot.cursor_position < 0:
                return None
            if snapshot.source_signature is not None and (
                not isinstance(snapshot.source_signature, (list, tuple))
                or len(snapshot.source_signature) != 5
                or any(not isinstance(value, int) or value < 0 for value in snapshot.source_signature)
            ):
                return None
            if len(snapshot.content.encode("utf-8")) > self.max_document_bytes:
                return None
            return snapshot
        except (UnicodeError, ValueError, TypeError, AttributeError, RecursionError):
            return None

    def _path(self, snapshot_id: str) -> Path:
        return self.root / f"{snapshot_id}.json"

    @staticmethod
    def _normalized_id(snapshot_id: str) -> str:
        if not isinstance(snapshot_id, str):
            raise RecoverySnapshotError("Invalid recovery snapshot identifier")
        normalized = "".join(char for char in snapshot_id if char.isalnum() or char in "-_")
        if not normalized or normalized != snapshot_id or len(snapshot_id.encode("utf-8")) > 128:
            raise RecoverySnapshotError("Invalid recovery snapshot identifier")
        return normalized
