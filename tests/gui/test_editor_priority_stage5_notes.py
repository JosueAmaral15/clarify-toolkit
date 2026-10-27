"""Focused GUI regressions for Clarify Editor temporary notes."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

import json
from datetime import datetime, timedelta, timezone
from functools import partial

from PySide6 import QtCore
from PySide6.QtWidgets import QMessageBox

from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch, settings=None):
    settings = settings or QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(module.TemporaryNoteStore, root=tmp_path / "notes"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock, settings


def test_save_note_does_not_settle_dirty_file_or_modify_original(qtbot, tmp_path, monkeypatch):
    source = tmp_path / "source.txt"
    source.write_text("original", encoding="utf-8")
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("note version")

    assert dock._save_current_as_temp_note("Reminder")
    assert not tab.is_modified
    assert tab.file_path is None
    assert tab.get_tab_title() == "Reminder"
    assert source.read_text(encoding="utf-8") == "original"
    assert dock.temp_note_store.get(tab._clarify_temp_note_id).content == "note version"


def test_restore_reuses_open_note_and_delete_preserves_buffer(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    note = dock.temp_note_store.save("note-one", title="Reminder", content="remember", extension=".md")

    tab = dock._restore_temp_note(note.note_id)
    assert tab.file_path is None
    assert not tab.is_modified
    assert tab.get_tab_title() == "Reminder"
    assert tab.editor.toPlainText() == "remember"
    assert dock._restore_temp_note(note.note_id) is tab
    assert dock.tab_widget.count() == 1

    assert dock._delete_temp_note(note.note_id, confirm=False)
    assert dock.tab_widget.count() == 1
    assert tab.editor.toPlainText() == "remember"
    assert not hasattr(tab, "_clarify_temp_note_id")


def test_retention_requires_confirmation_and_persists_choice(qtbot, tmp_path, monkeypatch):
    dock, settings = make_dock(qtbot, tmp_path, monkeypatch)
    dock.temp_note_store.save("old", title="Old", content="old")
    path = dock.temp_note_store.root / "old.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["updated_at"] = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(
        module.QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.No,
    )

    assert dock._set_temp_note_retention(30) is False
    assert dock.temp_note_store.get("old").content == "old"
    assert settings.value("temp_note_retention_days", 0, type=int) == 0

    monkeypatch.setattr(
        module.QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.Yes,
    )
    assert dock._set_temp_note_retention(30)
    assert dock.temp_note_store.list() == []
    assert settings.value("temp_note_retention_days", 0, type=int) == 30


def test_manual_retention_survives_new_instance_without_deletion(qtbot, tmp_path, monkeypatch):
    dock, settings = make_dock(qtbot, tmp_path, monkeypatch)
    dock.temp_note_store.save("one", title="One", content="content")
    assert dock._set_temp_note_retention(0)
    dock.close()

    restored, _settings = make_dock(qtbot, tmp_path, monkeypatch, settings)
    assert restored.temp_note_retention_days == 0
    assert restored.temp_note_store.get("one").content == "content"


def test_positive_retention_prunes_expired_notes_on_new_instance(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    settings.setValue("temp_note_retention_days", 30)
    store = module.TemporaryNoteStore(root=tmp_path / "notes")
    store.save("old", title="Old", content="old")
    path = store.root / "old.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["updated_at"] = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    path.write_text(json.dumps(payload), encoding="utf-8")

    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch, settings)

    assert dock.temp_note_retention_days == 30
    assert dock.temp_note_store.list() == []
