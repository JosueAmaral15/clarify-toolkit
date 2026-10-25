"""Clarify Editor comment scope and inverted-search GUI regressions."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

import pytest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit

from src.gui import editor_dock as module


def _editor(text):
    editor = QTextEdit()
    editor.setPlainText(text)
    return editor


def _select_unit(dialog, unit):
    index = dialog.cmb_inverted_unit.findData(unit)
    assert index >= 0
    dialog.cmb_inverted_unit.setCurrentIndex(index)


def test_inverted_search_defaults_to_line_and_enables_unit_control(qapp):
    dialog = module._EditorFindDialog(_editor("alpha\nhit\n"))

    assert not dialog.chk_inverted.isChecked()
    assert dialog.cmb_inverted_unit.currentData() == "line"
    assert not dialog.cmb_inverted_unit.isEnabled()

    dialog.chk_inverted.setChecked(True)
    assert dialog.cmb_inverted_unit.isEnabled()
    dialog.close()


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        ("line", ["alpha", "beta", "gamma", "delta"]),
        ("token", ["alpha", "beta", "gamma", "delta"]),
        ("interval", ["alpha\nbeta", "gamma\ndelta"]),
    ],
)
def test_inverted_units_are_explicit_and_navigable(qapp, unit, expected):
    text = "alpha\nbeta\nhit\ngamma\ndelta\nhit\n"
    editor = _editor(text)
    dialog = module._EditorFindDialog(editor)
    dialog.find_input.setText("hit")
    dialog.chk_inverted.setChecked(True)
    _select_unit(dialog, unit)

    assert [text[match.start : match.end] for match in dialog.matches] == expected
    assert dialog._find_next()
    assert editor.textCursor().selectedText().replace("\u2029", "\n") == expected[0]
    dialog.close()


def test_comment_scope_and_negative_regex_work_without_cursor_side_effects(qapp):
    text = 'value = "marker"  # comment marker\ndef function():\n    pass\n'
    editor = _editor(text)
    dialog = module._EditorFindDialog(editor, file_path="sample.py")
    dialog.radio_only_comments.setChecked(True)
    dialog.find_input.setText("marker")
    assert [text[item.start : item.end] for item in dialog.matches] == ["marker"]

    dialog.radio_all_text.setChecked(True)
    dialog.chk_regex.setChecked(True)
    dialog.find_input.setText(r"^(?!\s*def).*")
    cursor = editor.textCursor()
    cursor.setPosition(5)
    editor.setTextCursor(cursor)
    original_position = editor.textCursor().position()
    assert [text[item.start : item.end] for item in dialog.matches] == [
        'value = "marker"  # comment marker',
        "    pass",
    ]
    assert editor.textCursor().position() == original_position
    dialog.close()


def test_invalid_regex_reports_error_without_moving_cursor(qapp):
    editor = _editor("alpha beta")
    cursor = editor.textCursor()
    cursor.setPosition(4)
    editor.setTextCursor(cursor)
    dialog = module._EditorFindDialog(editor)
    dialog.chk_regex.setChecked(True)
    dialog.find_input.setText("(")

    assert dialog.matches == ()
    assert module.tr("editor.find_error").split(":", 1)[0] in dialog.lbl_status.text()
    assert editor.textCursor().position() == 4
    assert not editor.textCursor().hasSelection()
    dialog.close()


def test_inverted_replace_is_disabled_and_never_changes_text(qapp):
    editor = _editor("alpha\nhit\nbeta\n")
    dialog = module._EditorFindDialog(editor, replace_enabled=True)
    dialog.find_input.setText("hit")
    dialog.replace_input.setText("changed")
    dialog.chk_inverted.setChecked(True)

    assert not dialog.btn_replace.isEnabled()
    assert not dialog.btn_replace_all.isEnabled()
    assert module.tr("editor.find_inverted_replace_disabled") in dialog.lbl_status.text()
    original = editor.toPlainText()
    dialog._replace_current()
    dialog._replace_all()
    assert editor.toPlainText() == original
    dialog.close()


def test_clear_preserves_comment_scope_inversion_and_line_bounds(qapp):
    editor = _editor("# marker\nvalue\n")
    dialog = module._EditorFindDialog(editor, file_path="sample.py")
    dialog.radio_only_comments.setChecked(True)
    dialog.chk_inverted.setChecked(True)
    _select_unit(dialog, "token")
    dialog.start_line.setValue(1)
    dialog.end_line.setValue(2)
    dialog.find_input.setText("marker")

    dialog._clear_find_state()

    assert dialog.find_input.text() == ""
    assert dialog.radio_only_comments.isChecked()
    assert dialog.chk_inverted.isChecked()
    assert dialog.cmb_inverted_unit.currentData() == "token"
    assert dialog.start_line.value() == 1
    assert dialog.end_line.value() == 2
    dialog.close()
