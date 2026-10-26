"""Keyboard regressions for Clarify Editor Find navigation."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

import pytest
from PySide6 import QtCore, QtGui, QtWidgets

from src.gui import editor_dock as module


@pytest.fixture
def dialog(qtbot):
    editor = QtWidgets.QTextEdit()
    editor.setPlainText("one one one")
    qtbot.addWidget(editor)
    instance = module._EditorFindDialog(editor)
    qtbot.addWidget(instance)
    instance.show()
    instance.find_input.setText("one")
    instance.find_input.setFocus()
    return instance


@pytest.mark.parametrize(
    ("key", "modifiers"),
    [
        (QtCore.Qt.Key.Key_Return, QtCore.Qt.KeyboardModifier.NoModifier),
        (QtCore.Qt.Key.Key_Enter, QtCore.Qt.KeyboardModifier.KeypadModifier),
    ],
)
def test_enter_in_query_advances_exactly_once(dialog, qtbot, key, modifiers):
    qtbot.keyClick(dialog.find_input, key, modifiers)

    assert dialog.current_match_index == 0
    assert dialog.editor.textCursor().selectedText() == "one"
    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=1, total=3)


@pytest.mark.parametrize(
    ("key", "modifiers"),
    [
        (QtCore.Qt.Key.Key_Return, QtCore.Qt.KeyboardModifier.ShiftModifier),
        (
            QtCore.Qt.Key.Key_Enter,
            QtCore.Qt.KeyboardModifier.ShiftModifier | QtCore.Qt.KeyboardModifier.KeypadModifier,
        ),
    ],
)
def test_shift_enter_in_query_moves_previous_exactly_once(dialog, qtbot, key, modifiers):
    qtbot.keyClick(dialog.find_input, key, modifiers)

    assert dialog.current_match_index == 2
    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=3, total=3)


@pytest.mark.parametrize(
    "modifiers",
    [
        QtCore.Qt.KeyboardModifier.NoModifier,
        QtCore.Qt.KeyboardModifier.ShiftModifier,
    ],
)
def test_auto_repeat_enter_is_consumed_without_repeating_navigation(dialog, qtbot, modifiers):
    qtbot.keyClick(dialog.find_input, QtCore.Qt.Key.Key_Return)
    assert dialog.current_match_index == 0
    repeated = QtGui.QKeyEvent(
        QtCore.QEvent.Type.KeyPress,
        QtCore.Qt.Key.Key_Return,
        modifiers,
        "",
        True,
        2,
    )

    QtWidgets.QApplication.sendEvent(dialog.find_input, repeated)

    assert dialog.current_match_index == 0


def test_enter_is_not_captured_in_replace_or_line_bound_controls(qtbot):
    editor = QtWidgets.QTextEdit()
    editor.setPlainText("one one")
    qtbot.addWidget(editor)
    dialog = module._EditorFindDialog(editor, replace_enabled=True)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.find_input.setText("one")

    for modifiers in (
        QtCore.Qt.KeyboardModifier.NoModifier,
        QtCore.Qt.KeyboardModifier.ShiftModifier,
    ):
        dialog.replace_input.setFocus()
        qtbot.keyClick(
            dialog.replace_input,
            QtCore.Qt.Key.Key_Return,
            modifiers,
        )
        assert dialog.current_match_index == -1
        assert not editor.textCursor().hasSelection()

    dialog.start_line.setFocus()
    qtbot.keyClick(dialog.start_line, QtCore.Qt.Key.Key_Return)
    assert dialog.current_match_index == -1
    assert not editor.textCursor().hasSelection()


def test_enter_remains_native_in_editor_document(dialog, qtbot):
    cursor = dialog.editor.textCursor()
    cursor.movePosition(module.QTextCursor.End)
    dialog.editor.setTextCursor(cursor)
    dialog.editor.setFocus()

    qtbot.keyClick(dialog.editor, QtCore.Qt.Key.Key_Return)

    assert dialog.editor.toPlainText() == "one one one\n"
    assert not dialog.editor.textCursor().hasSelection()


def test_invalid_regex_enter_does_not_move_editor_cursor(dialog, qtbot):
    cursor = dialog.editor.textCursor()
    cursor.setPosition(4)
    dialog.editor.setTextCursor(cursor)
    dialog.chk_regex.setChecked(True)
    dialog.find_input.setText("[")
    dialog.find_input.setFocus()

    qtbot.keyClick(dialog.find_input, QtCore.Qt.Key.Key_Return)

    assert dialog.editor.textCursor().position() == 4
    assert module.tr("editor.find_error").split(":", 1)[0] in dialog.lbl_status.text()
