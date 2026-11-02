"""Bounded storage tests for user-managed Clarify Editor notes."""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

from src.editor_notes import (
    TemporaryNoteError,
    TemporaryNoteStore,
    export_notes_bundle,
    export_notes_separately,
)


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


def test_note_order_is_persistent_by_identity_not_title(tmp_path):
    store = TemporaryNoteStore(tmp_path)
    store.save("one", title="Zulu", content="one")
    store.save("two", title="Alpha", content="two")
    assert [note.note_id for note in store.list()] == ["one", "two"]

    store.reorder(["two", "one"])
    store.save("two", title="Renamed", content="updated")

    reopened = TemporaryNoteStore(tmp_path)
    assert [note.note_id for note in reopened.list()] == ["two", "one"]
    reopened.discard("two")
    assert [note.note_id for note in reopened.list()] == ["one"]


def test_discard_many_rolls_back_when_staging_fails(tmp_path, monkeypatch):
    store = TemporaryNoteStore(tmp_path)
    store.save("one", title="One", content="one")
    store.save("two", title="Two", content="two")
    real_replace = os.replace

    def fail_second_stage(source, destination):
        if os.path.basename(source) == "two.json" and ".delete-" in os.path.basename(destination):
            raise OSError("injected staging failure")
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_second_stage)
    with pytest.raises(TemporaryNoteError, match="delete notes atomically"):
        store.discard_many(["one", "two"])

    assert [note.note_id for note in store.list()] == ["one", "two"]
    assert store.get("one").content == "one"
    assert store.get("two").content == "two"


def test_bundle_export_is_atomic_structured_and_non_destructive(tmp_path):
    store = TemporaryNoteStore(tmp_path / "notes")
    store.save("one", title="One", content="alpha", extension=".md")
    destination = tmp_path / "all-notes.json"

    export_notes_bundle(store.list(), destination)

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["format"] == "clarify-temporary-notes"
    assert payload["version"] == 1
    assert payload["notes"][0]["note_id"] == "one"
    assert payload["notes"][0]["content"] == "alpha"
    assert store.get("one").content == "alpha"


def test_separate_export_resolves_names_and_cleans_failed_stage(tmp_path, monkeypatch):
    store = TemporaryNoteStore(tmp_path / "notes")
    store.save("one", title="Same/Title", content="one", extension=".txt")
    store.save("two", title="Same/Title", content="two", extension=".txt")
    export_parent = tmp_path / "exports"
    export_parent.mkdir()

    exported = export_notes_separately(store.list(), export_parent)
    assert sorted(path.name for path in exported.iterdir()) == [
        "Same_Title-2.txt",
        "Same_Title.txt",
    ]
    assert {path.read_text(encoding="utf-8") for path in exported.iterdir()} == {"one", "two"}

    from src import editor_notes as notes_module
    real_write = notes_module.write_text_atomically
    calls = 0

    def fail_second_write(path, content):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected export failure")
        return real_write(path, content)

    monkeypatch.setattr(notes_module, "write_text_atomically", fail_second_write)
    with pytest.raises(TemporaryNoteError, match="export notes"):
        export_notes_separately(store.list(), export_parent)
    assert not list(export_parent.glob(".clarify-note-export-*"))
