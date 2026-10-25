"""Focused GUI regressions for the Clarify Editor Find panel."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial

from PySide6 import QtCore
from PySide6.QtWidgets import QTextEdit

from src.gui import editor_dock as module


def test_next_previous_are_circular_and_show_current_total(qapp):
    editor = QTextEdit("one one one")
    dialog = module._EditorFindDialog(editor)
    dialog.find_input.setText("one")

    assert len(dialog.matches) == 3
    assert dialog.lbl_status.text() == module.tr("editor.find_match_count").format(count=3)
    assert dialog._find_next() is True
    assert editor.textCursor().selectionStart() == 0
    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=1, total=3)
    assert dialog._find_previous() is True
    assert editor.textCursor().selectionStart() == 8
    assert dialog.lbl_status.text() == module.tr("editor.find_position").format(current=3, total=3)


def test_case_whole_word_and_regex_are_combined(qapp):
    editor = QTextEdit("cat catalog CAT")
    dialog = module._EditorFindDialog(editor)
    dialog.find_input.setText("cat")
    dialog.chk_case_sensitive.setChecked(True)
    dialog.chk_whole_word.setChecked(True)
    dialog.chk_regex.setChecked(True)

    assert [(match.start, match.end) for match in dialog.matches] == [(0, 3)]
    assert dialog._find_next() is True
    assert editor.textCursor().selectedText() == "cat"


def test_match_options_and_scope_survive_dialog_reopen(qapp):
    editor = QTextEdit("value")
    state = {}
    persisted = []
    dialog = module._EditorFindDialog(editor, state=state, state_changed=lambda value: persisted.append(value))
    dialog.chk_case_sensitive.setChecked(True)
    dialog.chk_whole_word.setChecked(True)
    dialog.chk_regex.setChecked(True)
    dialog.radio_only_comments.setChecked(True)
    dialog.chk_inverted.setChecked(True)
    dialog.cmb_inverted_unit.setCurrentIndex(dialog.cmb_inverted_unit.findData("interval"))
    dialog.close()

    reopened = module._EditorFindDialog(editor, state=state)
    assert reopened.chk_case_sensitive.isChecked()
    assert reopened.chk_whole_word.isChecked()
    assert reopened.chk_regex.isChecked()
    assert reopened.radio_only_comments.isChecked()
    assert reopened.chk_inverted.isChecked()
    assert reopened.cmb_inverted_unit.currentData() == "interval"
    assert persisted[-1]["scope"] == "comments"


def test_line_range_and_python_lexical_scopes(qapp):
    editor = QTextEdit()
    editor.setPlainText('name = "name"\nname = 2\n')
    dialog = module._EditorFindDialog(editor, file_path="sample.py")
    dialog.find_input.setText("name")
    dialog.start_line.setValue(2)
    dialog.end_line.setValue(2)
    assert [(match.start, match.end) for match in dialog.matches] == [(14, 18)]

    dialog.start_line.setValue(0)
    dialog.end_line.setValue(0)
    dialog.radio_only_strings.setChecked(True)
    assert [(match.start, match.end) for match in dialog.matches] == [(8, 12)]

    dialog.radio_only_variables.setChecked(True)
    assert [(match.start, match.end) for match in dialog.matches] == [
        (0, 4),
        (14, 18),
    ]


def test_unknown_scope_fallback_is_visible(qapp):
    editor = QTextEdit("name")
    dialog = module._EditorFindDialog(editor, file_path="notes.txt")
    dialog.radio_only_variables.setChecked(True)
    dialog.find_input.setText("name")

    assert len(dialog.matches) == 1
    assert module.tr("editor.find_scope_fallback") in dialog.lbl_status.text()


def test_regex_replace_all_uses_discovered_matches_and_groups(qapp):
    editor = QTextEdit("item-12 item-34 other")
    dialog = module._EditorFindDialog(editor, replace_enabled=True)
    dialog.chk_regex.setChecked(True)
    dialog.find_input.setText(r"item-(\d+)")
    dialog.replace_input.setText(r"value-\1")

    dialog._replace_all()

    assert editor.toPlainText() == "value-12 value-34 other"
    assert dialog.lbl_status.text() == module.tr("editor.replace_all_complete").format(count=2)


def test_matches_recalculate_when_document_changes(qapp):
    editor = QTextEdit("one")
    dialog = module._EditorFindDialog(editor)
    dialog.find_input.setText("one")
    assert len(dialog.matches) == 1

    editor.setPlainText("one one")

    assert len(dialog.matches) == 2


def test_editor_dock_persists_global_find_preferences(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    first = module.EditorDock()
    qtbot.addWidget(first)
    first._persist_find_state(
        {
            "case_sensitive": True,
            "whole_word": True,
            "regex": True,
            "scope": "strings",
            "inverted": True,
            "inverted_unit": "token",
        }
    )

    restored = module.EditorDock()
    qtbot.addWidget(restored)
    assert restored.find_state == {
        "case_sensitive": True,
        "whole_word": True,
        "regex": True,
        "scope": "strings",
        "inverted": True,
        "inverted_unit": "token",
    }
