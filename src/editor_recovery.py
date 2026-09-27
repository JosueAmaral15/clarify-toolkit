"""Bounded local snapshots for unsaved Clarify Editor documents."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QStandardPaths


DEFAULT_RETENTION_HOURS = 24
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
        self.max_total_bytes = max(self.max_document_bytes, int(max_total_bytes))

    def save(
        self,
        snapshot_id: str,
        *,
        title: str,
        content: str,
        file_path: str = "",
        extension: str = ".txt",
    ) -> RecoverySnapshot:
        """Atomically save one text snapshot and enforce global bounds."""
        normalized_id = self._normalized_id(snapshot_id)
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
        )
        payload = json.dumps(asdict(snapshot), ensure_ascii=False).encode("utf-8")
        self.root.mkdir(parents=True, exist_ok=True)

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
        finally:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass

        self.prune()
        return snapshot

    def list(self) -> list[RecoverySnapshot]:
        """Return valid, recent snapshots newest first."""
        self.prune()
        snapshots = list(self._read_valid_snapshots())
        return sorted(snapshots, key=lambda item: item.updated_at, reverse=True)

    def discard(self, snapshot_id: str) -> None:
        """Delete one snapshot if present."""
        try:
            self._path(self._normalized_id(snapshot_id)).unlink()
        except FileNotFoundError:
            pass

    def discard_all(self) -> None:
        """Delete all recovery snapshots owned by this store."""
        if not self.root.exists():
            return
        for path in self.root.glob("*.json"):
            path.unlink(missing_ok=True)

    def prune(self) -> None:
        """Remove expired, corrupt, excessive, and over-budget snapshots."""
        if not self.root.exists():
            return

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.retention_hours)
        entries = []
        for path in self.root.glob("*.json"):
            snapshot = self._read(path)
            if snapshot is None:
                path.unlink(missing_ok=True)
                continue
            try:
                updated = datetime.fromisoformat(snapshot.updated_at)
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=timezone.utc)
            except ValueError:
                path.unlink(missing_ok=True)
                continue
            if updated < cutoff:
                path.unlink(missing_ok=True)
                continue
            entries.append((updated, path, path.stat().st_size))

        entries.sort(reverse=True)
        retained_bytes = 0
        for index, (_updated, path, size) in enumerate(entries):
            if index >= self.max_snapshots or retained_bytes + size > self.max_total_bytes:
                path.unlink(missing_ok=True)
            else:
                retained_bytes += size

    def _read_valid_snapshots(self) -> Iterable[RecoverySnapshot]:
        for path in self.root.glob("*.json"):
            snapshot = self._read(path)
            if snapshot is not None:
                yield snapshot

    def _read(self, path: Path) -> RecoverySnapshot | None:
        try:
            if path.stat().st_size > self.max_document_bytes + 64 * 1024:
                return None
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshot = RecoverySnapshot(**data)
            if snapshot.snapshot_id != path.stem:
                return None
            if len(snapshot.content.encode("utf-8")) > self.max_document_bytes:
                return None
            return snapshot
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            return None

    def _path(self, snapshot_id: str) -> Path:
        return self.root / f"{snapshot_id}.json"

    @staticmethod
    def _normalized_id(snapshot_id: str) -> str:
        normalized = "".join(char for char in snapshot_id if char.isalnum() or char in "-_")
        if not normalized or normalized != snapshot_id:
            raise RecoverySnapshotError("Invalid recovery snapshot identifier")
        return normalized
