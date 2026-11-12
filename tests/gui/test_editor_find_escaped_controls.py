"""Clarify Editor Find/Replace control-escape GUI regressions."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from PySide6.QtWidgets import QTextEdit

from src.gui import editor_dock as module


def _dialog(qtbot, text, *, replace=False, state=None):
    editor = QTextEdit()
    editor.setPlainText(text)
    qtbot.addWidget(editor)
    dialog = module._EditorFindDialog(
        editor,
        replace_enabled=replace,
        state=state,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    return dialog


def test_literal_escape_checkbox_updates_preview_and_counter(qtbot):
    dialog = _dialog(qtbot, "one\ntwo\nthree")
    dialog.chk_interpret_escapes.setChecked(True)
    dialog.find_input.setText(r"\n")

    assert len(dialog.matches) == 2
    assert "<LF>" in dialog.lbl_escape_preview.text()
    assert dialog.lbl_status.text() == module.tr("editor.find_match_count").format(
        count=2
    )


def test_invalid_escape_disables_navigation_without_moving_cursor(qtbot):
    dialog = _dialog(qtbot, "one two")
    cursor = dialog.editor.textCursor()
    cursor.setPosition(3)
    dialog.editor.setTextCursor(cursor)
    dialog.chk_interpret_escapes.setChecked(True)
    dialog.find_input.setText("trailing\\")

    assert dialog.matches == ()
    assert not dialog.btn_find_next.isEnabled()
    assert dialog.editor.textCursor().position() == 3
    assert module.tr("editor.find_error").split(":", 1)[0] in dialog.lbl_status.text()


def test_replace_all_changes_only_matched_newline_and_is_one_undo_step(qtbot):
    dialog = _dialog(qtbot, "one\ntwo\nthree", replace=True)
    dialog.chk_interpret_escapes.setChecked(True)
    dialog.find_input.setText(r"one\ntwo")
    dialog.replace_input.setText(r"one\ttwo")

    dialog._replace_all()

    assert dialog.editor.toPlainText() == "one\ttwo\nthree"
    dialog.editor.undo()
    assert dialog.editor.toPlainText() == "one\ntwo\nthree"


def test_regex_owns_its_escape_syntax_and_literal_setting_persists(qtbot):
    state = {}
    dialog = _dialog(qtbot, "one  two", state=state)
    dialog.chk_interpret_escapes.setChecked(True)
    assert state["interpret_escapes"] is True

    dialog.chk_regex.setChecked(True)
    dialog.find_input.setText(r"\s+")
    assert not dialog.chk_interpret_escapes.isEnabled()
    assert len(dialog.matches) == 1
    assert module.tr("editor.find_regex_escape_preview") in dialog.lbl_escape_preview.text()

    dialog.chk_regex.setChecked(False)
    assert dialog.chk_interpret_escapes.isEnabled()
    assert dialog.chk_interpret_escapes.isChecked()


def test_double_backslash_searches_literal_backslash_n(qtbot):
    dialog = _dialog(qtbot, r"literal \n marker")
    dialog.chk_interpret_escapes.setChecked(True)
    dialog.find_input.setText(r"\\n")

    assert len(dialog.matches) == 1
    match = dialog.matches[0]
    assert dialog.editor.toPlainText()[match.start : match.end] == r"\n"
