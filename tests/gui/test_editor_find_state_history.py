"""Bounded per-buffer Clarify Editor Find state regressions."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QDialog, QTextEdit

from src.editor_notes import TemporaryNoteStore
from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    """Create an EditorDock with private settings and managed stores."""
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(TemporaryNoteStore, root=tmp_path / "notes"),
    )
    widget = module.EditorDock()
    qtbot.addWidget(widget)
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def test_history_is_bounded_deduplicated_and_truncates_values():
    history = module._EditorFindHistory(max_entries=5)
    for index in range(7):
        history.remember(f"query-{index}", f"replacement-{index}")
    history.remember("query-4", "replacement-4")
    history.remember("x" * (module.MAX_QUERY_CHARS + 10), "y" * (module.MAX_QUERY_CHARS + 10))

    assert len(history.entries) == 5
    assert history.entries[1] == ("query-4", "replacement-4")
    assert len(history.entries[0][0]) == module.MAX_QUERY_CHARS
    assert len(history.entries[0][1]) == module.MAX_QUERY_CHARS


def test_reopen_restores_values_and_reports_nearest_without_moving_cursor(qapp):
    editor = QTextEdit("one xx one yy one")
    history = module._EditorFindHistory()
    history.remember("one", "ONE")
    cursor = editor.textCursor()
    cursor.setPosition(8)
    editor.setTextCursor(cursor)
    original_position = editor.textCursor().position()

    dialog = module._EditorFindDialog(editor, replace_enabled=True, history=history)

    assert dialog.find_input.text() == "one"
    assert dialog.replace_input.text() == "ONE"
    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=2, total=3)
    assert editor.textCursor().position() == original_position
    assert not editor.textCursor().hasSelection()
    dialog.close()
    qapp.processEvents()


def test_cursor_move_recalculates_nearest_result_without_navigation(qapp):
    editor = QTextEdit("one xx one yy one")
    history = module._EditorFindHistory()
    history.remember("one")
    dialog = module._EditorFindDialog(editor, history=history)
    cursor = editor.textCursor()
    cursor.setPosition(len(editor.toPlainText()))
    editor.setTextCursor(cursor)
    qapp.processEvents()

    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=3, total=3)
    assert editor.textCursor().position() == len(editor.toPlainText())
    assert not editor.textCursor().hasSelection()
    dialog.close()


def test_previous_values_and_selection_prefill_have_explicit_precedence(qapp):
    editor = QTextEdit("old newest selected")
    history = module._EditorFindHistory()
    history.remember("old", "OLD")
    history.remember("newest", "NEWEST")
    dialog = module._EditorFindDialog(editor, replace_enabled=True, history=history)

    assert dialog.find_input.text() == "newest"
    assert dialog.btn_previous_value.isVisibleTo(dialog)
    assert dialog.btn_previous_value.isEnabled()
    assert dialog._restore_previous_value()
    assert dialog.find_input.text() == "old"
    assert dialog.replace_input.text() == "OLD"
    dialog.close()
    qapp.processEvents()

    selected = module._EditorFindDialog(
        editor,
        replace_enabled=True,
        history=history,
        selection_query="selected",
    )
    assert selected.find_input.text() == "selected"
    assert not selected.btn_previous_value.isVisibleTo(selected)
    assert not selected._restore_previous_value()
    selected.close()


def test_find_only_does_not_erase_a_remembered_replacement(qapp):
    editor = QTextEdit("needle")
    history = module._EditorFindHistory()
    history.remember("needle", "replacement")
    dialog = module._EditorFindDialog(editor, history=history)

    dialog._find_next()
    dialog.close()
    qapp.processEvents()

    assert history.current() == ("needle", "replacement")


def test_clear_removes_buffer_values_but_preserves_options_and_line_bounds(qapp):
    editor = QTextEdit()
    editor.setPlainText("one\none\n")
    history = module._EditorFindHistory()
    dialog = module._EditorFindDialog(editor, replace_enabled=True, history=history)
    dialog.find_input.setText("one")
    dialog.replace_input.setText("ONE")
    dialog.chk_case_sensitive.setChecked(True)
    dialog.chk_whole_word.setChecked(True)
    dialog.radio_only_strings.setChecked(True)
    dialog.start_line.setValue(2)
    dialog.end_line.setValue(2)
    dialog._remember_current_values()

    dialog._clear_find_state()

    assert dialog.find_input.text() == ""
    assert dialog.replace_input.text() == ""
    assert history.entries == []
    assert dialog.matches == ()
    assert dialog.chk_case_sensitive.isChecked()
    assert dialog.chk_whole_word.isChecked()
    assert dialog.radio_only_strings.isChecked()
    assert dialog.start_line.value() == 2
    assert dialog.end_line.value() == 2
    dialog.close()
    qapp.processEvents()
    assert history.entries == []


def test_dock_histories_are_isolated_bounded_and_removed_with_tab(dock, monkeypatch):
    monkeypatch.setattr(module.QMessageBox, "question", lambda *args: module.QMessageBox.Discard)
    dock._new_file()
    first = dock.tab_widget.currentWidget()
    first_history = dock._find_history_for_tab(first)
    first_history.remember("first")
    dock._new_file()
    second = dock.tab_widget.currentWidget()
    second_history = dock._find_history_for_tab(second)
    second_history.remember("second")

    assert dock._find_history_for_tab(first).current() == ("first", "")
    assert dock._find_history_for_tab(second).current() == ("second", "")
    first_identity = dock._find_buffer_identity(first)
    second_identity = dock._find_buffer_identity(second)
    assert dock._close_tab(dock.tab_widget.indexOf(first))
    assert first_identity not in dock._find_history_by_buffer
    assert second_identity in dock._find_history_by_buffer

    for _index in range(dock.MAX_FIND_HISTORY_BUFFERS + 2):
        tab = type("TabIdentity", (), {})()
        dock._find_history_for_tab(tab)
    assert len(dock._find_history_by_buffer) == dock.MAX_FIND_HISTORY_BUFFERS


def test_find_dialog_uses_active_split_and_does_not_persist_private_values(dock, monkeypatch):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("primary selected")
    assert dock._show_split_view(tab, Qt.Orientation.Horizontal)
    cursor = dock.split_editor.textCursor()
    cursor.setPosition(8)
    cursor.setPosition(16, QTextCursor.MoveMode.KeepAnchor)
    dock.split_editor.setTextCursor(cursor)
    observed = {}

    class FakeDialog:
        def __init__(self, editor, replace_enabled, parent, **kwargs):
            observed.update(
                editor=editor,
                replace_enabled=replace_enabled,
                parent=parent,
                kwargs=kwargs,
            )
            self.find_input = type("Input", (), {"selectAll": lambda self: None})()

        def exec(self):
            return QDialog.DialogCode.Accepted

        def deleteLater(self):
            return None

    monkeypatch.setattr(module, "_EditorFindDialog", FakeDialog)
    dock._show_find_dialog(True)

    assert observed["editor"] is dock.split_editor
    assert observed["kwargs"]["selection_query"] == "selected"
    assert observed["kwargs"]["history"] is dock._find_history_for_tab(tab)
    settings_keys = {str(key) for key in dock.settings.allKeys()}
    assert not any("query" in key or "replacement" in key or "history" in key for key in settings_keys)


def test_tool_close_clears_private_history_after_success(dock, qapp):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    dock._find_history_for_tab(tab).remember("private query", "private replacement")

    assert dock.close()
    qapp.processEvents()
    assert dock._find_history_by_buffer == {}
