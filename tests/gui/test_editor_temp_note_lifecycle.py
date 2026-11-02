"""Regressions for persistent Clarify Editor temporary-note identity."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial

import pytest
from PySide6 import QtCore

from src.editor_notes import TemporaryNoteError
from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
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
    return dock


def test_initial_note_save_detaches_original_and_adopts_clean_title(qtbot, tmp_path, monkeypatch):
    source = tmp_path / "source.py"
    source.write_text("original\n", encoding="utf-8")
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("note version\n")

    assert dock._save_current_as_temp_note("Reminder")

    assert source.read_text(encoding="utf-8") == "original\n"
    assert tab.file_path is None
    assert tab.get_tab_title() == "Reminder"
    assert dock.tab_widget.tabText(dock.tab_widget.indexOf(tab)) == "Reminder"
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert dock._tab_folder_identity(tab) == ""
    assert dock.temp_note_store.get(tab._clarify_temp_note_id).content == "note version\n"


def test_temp_note_autosaves_by_default_and_ctrl_s_never_opens_file_dialog(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("first", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id

    tab.editor.setPlainText("autosaved")
    qtbot.waitUntil(
        lambda: dock.temp_note_store.get(note_id).content == "autosaved",
        timeout=2500,
    )
    assert not tab.is_modified

    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: pytest.fail("Save must not open a file dialog"),
    )
    tab.editor.setPlainText("saved with Ctrl+S")
    assert dock._save_file()
    assert dock.temp_note_store.get(note_id).content == "saved with Ctrl+S"
    assert tab.file_path is None


def test_successful_save_as_converts_note_only_after_file_and_store_succeed(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("draft", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    tab.editor.setPlainText("published")
    destination = tmp_path / "published.txt"
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )

    assert dock._save_file_as()
    assert destination.read_text(encoding="utf-8") == "published"
    assert tab.file_path == str(destination)
    assert not hasattr(tab, "_clarify_temp_note_id")
    assert tab.get_tab_title() == "published.txt"
    with pytest.raises(TemporaryNoteError):
        dock.temp_note_store.get(note_id)


def test_cancelled_or_failed_save_as_preserves_note(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("draft", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id

    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: ("", ""),
    )
    assert not dock._save_file_as()
    assert tab._clarify_temp_note_id == note_id
    assert dock.temp_note_store.get(note_id).content == "draft"

    destination = tmp_path / "failed.txt"
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )
    monkeypatch.setattr(
        module.QMessageBox,
        "critical",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(tab, "save_file", lambda *_args, **_kwargs: False)
    assert not dock._save_file_as()
    assert tab._clarify_temp_note_id == note_id
    assert dock.temp_note_store.get(note_id).content == "draft"


def test_store_cleanup_failure_keeps_note_identity_after_file_copy(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("draft", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    destination = tmp_path / "copy.txt"
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )

    def fail_discard(_note_id):
        raise TemporaryNoteError("injected cleanup failure")

    monkeypatch.setattr(dock.temp_note_store, "discard", fail_discard)
    assert not dock._save_file_as()
    assert destination.read_text(encoding="utf-8") == "draft"
    assert tab.file_path is None
    assert tab._clarify_temp_note_id == note_id
    assert dock.temp_note_store.get(note_id).content == "draft"


def test_restore_and_immediate_tool_close_flush_latest_note(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    note = dock.temp_note_store.save("note-one", title="Reminder", content="old", extension=".md")
    tab = dock._restore_temp_note(note.note_id)

    assert tab.get_tab_title() == "Reminder"
    assert not tab.is_modified
    tab.editor.setPlainText("latest")
    assert dock.request_tab_close()
    assert dock.temp_note_store.get(note.note_id).content == "latest"


def test_individual_tab_close_flushes_note_and_keeps_it_for_reopen(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("old", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    tab.editor.setPlainText("latest")

    assert dock._close_tab(dock.tab_widget.indexOf(tab))
    assert dock.temp_note_store.get(note_id).content == "latest"
    restored = dock._restore_temp_note(note_id)
    assert restored.editor.toPlainText() == "latest"
    assert restored.get_tab_title() == "Scratch"


def test_application_quit_flushes_note_and_stops_owned_timers(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("old", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    tab.editor.setPlainText("latest")
    timer = tab._clarify_temp_note_autosave_timer
    assert timer.isActive()

    dock._recovery_lifecycle.application_quitting()

    assert dock.temp_note_store.get(note_id).content == "latest"
    assert dock._recovery_suspended
    assert not timer.isActive()


def test_autosave_failure_keeps_dirty_buffer_and_reports_error(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("old", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    tab.editor.setPlainText("latest")

    def fail_save(*_args, **_kwargs):
        raise TemporaryNoteError("injected write failure")

    monkeypatch.setattr(dock.temp_note_store, "save", fail_save)
    assert not dock._flush_temp_note_autosaves()
    assert tab.is_modified
    assert dock.temp_note_store.get(note_id).content == "old"
    assert dock.lbl_status.text() == module.tr("editor.status_temp_note_failure")


def test_delete_open_note_preserves_buffer_as_dirty_non_note(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("remember", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id

    assert dock._delete_temp_note(note_id, confirm=False)
    assert tab.editor.toPlainText() == "remember"
    assert not hasattr(tab, "_clarify_temp_note_id")
    assert tab.is_modified
    assert dock.tab_widget.tabText(dock.tab_widget.indexOf(tab)).endswith(" *")


def test_note_manager_is_searchable_list_with_per_item_actions(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    notes = [
        dock.temp_note_store.save("one", title="Alpha", content="a"),
        dock.temp_note_store.save("two", title="Beta", content="b"),
    ]
    dialog = module._TemporaryNotesDialog(notes, dock)
    qtbot.addWidget(dialog)

    assert dialog.note_list.count() == 2
    assert not dialog.note_list.isSortingEnabled()
    assert dialog.note_list.item(0).data(module.Qt.ItemDataRole.UserRole) == "one"
    assert dialog.note_list.item(1).data(module.Qt.ItemDataRole.UserRole) == "two"
    dialog.search_box.setText("beta")
    assert dialog.note_list.item(0).isHidden() != dialog.note_list.item(1).isHidden()
    assert dialog.restore_button.isEnabled()
    assert dialog.rename_button.isEnabled()
    assert dialog.export_button.isEnabled()
    assert dialog.delete_button.isEnabled()


def test_rename_and_export_keep_note_identity(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("remember", "Untitled.md")
    assert dock._save_current_as_temp_note("Before")
    note_id = tab._clarify_temp_note_id

    assert dock._rename_temp_note(note_id, "After")
    assert tab.get_tab_title() == "After"
    assert dock.temp_note_store.get(note_id).title == "After"
    assert dock.temp_note_store.get(note_id).extension == ".md"

    destination = tmp_path / "export.md"
    assert dock._export_temp_note(note_id, str(destination))
    assert destination.read_text(encoding="utf-8") == "remember"
    assert tab._clarify_temp_note_id == note_id
    assert tab.file_path is None


def test_json_note_save_as_uses_json_writer_and_converts_identity(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content('{"answer": 42}', "Untitled.json")
    assert isinstance(tab, module.JsonEditorTab)
    assert dock._save_current_as_temp_note("Payload")
    note_id = tab._clarify_temp_note_id
    destination = tmp_path / "payload.json"
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )

    assert dock._save_file_as()
    assert destination.read_text(encoding="utf-8") == '{"answer": 42}'
    assert tab.file_path == str(destination)
    assert not hasattr(tab, "_clarify_temp_note_id")
    with pytest.raises(TemporaryNoteError):
        dock.temp_note_store.get(note_id)


def test_queued_autosave_cannot_recreate_converted_note(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    tab = dock.load_generated_content("draft", "Untitled.txt")
    assert dock._save_current_as_temp_note("Scratch")
    note_id = tab._clarify_temp_note_id
    tab.editor.setPlainText("published")
    assert tab._clarify_temp_note_autosave_timer.isActive()
    destination = tmp_path / "published.txt"
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )

    assert dock._save_file_as()
    qtbot.wait(dock.TEMP_NOTE_AUTOSAVE_INTERVAL_MS + 100)

    assert dock.temp_note_store.list() == []
    assert not hasattr(tab, "_clarify_temp_note_id")
    assert tab.file_path == str(destination)
    with pytest.raises(TemporaryNoteError):
        dock.temp_note_store.get(note_id)
