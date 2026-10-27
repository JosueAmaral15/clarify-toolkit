"""Regressions for the recent Clarify Editor interaction requests."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module
from src.shortcut_manager import ShortcutManager


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    """Create an EditorDock with private settings and recovery storage."""
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widget = module.EditorDock()
    qtbot.addWidget(widget)
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


@pytest.mark.parametrize("replace_enabled", [False, True])
def test_find_actions_prefill_the_selected_text(dock, replace_enabled):
    """Find and Replace both use the active selection as the query."""
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("alpha needle omega")
    cursor = editor.textCursor()
    cursor.setPosition(6)
    cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
    editor.setTextCursor(cursor)
    dock._show_find_dialog(replace_enabled)

    assert dock._find_dialog.find_input.text() == "needle"
    assert dock._find_dialog.replace_enabled is replace_enabled


def test_enter_preserves_the_current_line_indentation(dock, qtbot):
    """Enter inherits indentation and keeps the insertion undoable."""
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("    value")
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.keyClicks(editor, "next")

    assert editor.toPlainText() == "    value\n    next"
    assert editor.document().isUndoAvailable()


def test_enter_inside_indentation_does_not_duplicate_whitespace(dock, qtbot):
    """Splitting inside the prefix leaves one indentation prefix on the new line."""
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("    value")
    cursor = editor.textCursor()
    cursor.setPosition(2)
    editor.setTextCursor(cursor)

    qtbot.keyClick(editor, Qt.Key.Key_Enter)

    assert editor.toPlainText() == "  \n    value"


def test_home_toggles_between_text_and_physical_line_start(dock, qtbot):
    """Home follows the VS Code-style first-nonblank/column-zero cycle."""
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("    value")
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    qtbot.keyClick(editor, Qt.Key.Key_Home)
    assert editor.textCursor().positionInBlock() == 4
    qtbot.keyClick(editor, Qt.Key.Key_Home)
    assert editor.textCursor().positionInBlock() == 0


def test_shift_home_uses_the_same_destinations_and_keeps_anchor(dock, qtbot):
    """Shift+Home extends the selection through both smart destinations."""
    dock._new_file()
    editor = dock.tab_widget.currentWidget().editor
    editor.setPlainText("    value")
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    editor.setTextCursor(cursor)

    qtbot.keyClick(editor, Qt.Key.Key_Home, Qt.KeyboardModifier.ShiftModifier)
    assert editor.textCursor().selectedText() == "value"
    qtbot.keyClick(editor, Qt.Key.Key_Home, Qt.KeyboardModifier.ShiftModifier)
    assert editor.textCursor().selectedText() == "    value"


def test_file_tab_navigation_wraps_and_has_configurable_shortcuts(dock):
    """The new actions navigate only Editor file tabs and wrap at both ends."""
    for _index in range(3):
        dock._new_file()
    dock.tab_widget.setCurrentIndex(0)

    dock._previous_file_tab()
    assert dock.tab_widget.currentIndex() == 2
    dock._next_file_tab()
    assert dock.tab_widget.currentIndex() == 0

    assert ShortcutManager.get_shortcut("previous_file_tab")[0] == "Ctrl+Alt+PgUp"
    assert ShortcutManager.get_shortcut("next_file_tab")[0] == "Ctrl+Alt+PgDown"
    assert dock.action_previous_file_tab.shortcut() == ShortcutManager.get_key_sequence(
        "previous_file_tab"
    )
    assert dock.action_next_file_tab.shortcut() == ShortcutManager.get_key_sequence(
        "next_file_tab"
    )
