"""Tests for bounded unsaved-document recovery storage."""

from datetime import datetime, timedelta, timezone
import json

import pytest

from src.editor_recovery import RecoverySnapshotError, UnsavedRecoveryStore


def test_snapshot_round_trip_and_atomic_temp_cleanup(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)
    store.save(
        "tab-1",
        title="Notes",
        content="Unsaved text",
        file_path="/tmp/notes.txt",
        extension=".txt",
    )

    assert store.list()[0].content == "Unsaved text"
    assert store.list()[0].file_path == "/tmp/notes.txt"
    assert list(tmp_path.glob("*.tmp")) == []


def test_snapshot_rejects_oversized_document(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_document_bytes=4)

    with pytest.raises(RecoverySnapshotError, match="exceeds recovery limit"):
        store.save("large", title="Large", content="12345")


def test_prune_removes_expired_snapshot(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, retention_hours=24)
    store.save("old", title="Old", content="text")
    path = tmp_path / "old.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=25)
    ).isoformat()
    path.write_text(json.dumps(data), encoding="utf-8")

    assert store.list() == []
    assert not path.exists()


def test_prune_keeps_only_newest_snapshot_count(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_snapshots=2)
    for snapshot_id in ("one", "two", "three"):
        store.save(snapshot_id, title=snapshot_id, content=snapshot_id)

    assert len(store.list()) == 2


def test_invalid_identifier_cannot_escape_recovery_root(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)

    with pytest.raises(RecoverySnapshotError, match="Invalid"):
        store.save("../escape", title="Unsafe", content="text")
