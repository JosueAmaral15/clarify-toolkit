"""Bounded storage tests for user-managed Clarify Editor notes."""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from src.editor_notes import TemporaryNoteError, TemporaryNoteStore


def test_note_round_trip_update_and_new_store_instance(tmp_path):
    store = TemporaryNoteStore(tmp_path)
    first = store.save("note-one", title="First", content="alpha", extension="txt")
    updated = store.save("note-one", title="Renamed", content="beta", extension=".md")

    restored = TemporaryNoteStore(tmp_path).get("note-one")
    assert restored.title == "Renamed"
    assert restored.content == "beta"
    assert restored.extension == ".md"
    assert updated.created_at == first.created_at
    assert restored.updated_at == updated.updated_at


def test_private_permissions_and_atomic_temp_cleanup(tmp_path):
    store = TemporaryNoteStore(tmp_path / "notes")
    store.save("one", title="One", content="content")

    assert os.stat(store.root).st_mode & 0o777 == 0o700
    assert os.stat(store.root / "one.json").st_mode & 0o777 == 0o600
    assert list(store.root.glob("*.tmp")) == []


def test_size_count_and_total_quotas_do_not_evict_existing_notes(tmp_path):
    store = TemporaryNoteStore(tmp_path, max_notes=1, max_note_bytes=64, max_total_bytes=1024)
    store.save("one", title="One", content="small")
    with pytest.raises(TemporaryNoteError, match="count quota"):
        store.save("two", title="Two", content="small")
    with pytest.raises(TemporaryNoteError, match="bounded extraction"):
        store.save("one", title="One", content="x" * 65)
    assert [note.note_id for note in store.list()] == ["one"]


def test_corrupt_and_unsafe_entries_are_pruned(tmp_path):
    store = TemporaryNoteStore(tmp_path)
    store.root.mkdir(exist_ok=True)
    (store.root / "corrupt.json").write_text("{", encoding="utf-8")
    (store.root / "wrong.json").write_text(
        json.dumps(
            {
                "note_id": "different",
                "title": "Wrong",
                "content": "x",
                "extension": ".txt",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        encoding="utf-8",
    )

    assert store.list() == []
    assert list(store.root.glob("*.json")) == []


def test_manual_retention_is_inert_and_positive_retention_prunes(tmp_path):
    store = TemporaryNoteStore(tmp_path)
    store.save("old", title="Old", content="old")
    path = store.root / "old.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    old = datetime.now(timezone.utc) - timedelta(days=31)
    payload["updated_at"] = old.isoformat()
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert store.expired(0) == []
    assert store.prune(0) == 0
    assert store.get("old").content == "old"
    assert [note.note_id for note in store.expired(30)] == ["old"]
    assert store.prune(30) == 1
    with pytest.raises(TemporaryNoteError, match="unavailable"):
        store.get("old")


def test_symlink_storage_root_is_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "notes"
    link.symlink_to(target, target_is_directory=True)
    store = TemporaryNoteStore(link)

    with pytest.raises(TemporaryNoteError, match="symlink"):
        store.save("one", title="One", content="content")
