"""Tests for Format Converter text-mode search and replacement."""

from PySide6.QtWidgets import QPlainTextEdit

from src.gui.unified_text_to_json_dock import TextSearchDialog, UnifiedTextToJsonDock


def test_ctrl_f_routes_to_search_only_in_text_mode(qapp, monkeypatch):
    dock = UnifiedTextToJsonDock()
    opened = []
    monkeypatch.setattr(dock, "_open_text_search", lambda: opened.append(True))
    try:
        dock.jsx_input_type_combo.setCurrentIndex(0)
        dock._on_search_shortcut()
        assert opened == []

        dock.jsx_input_type_combo.setCurrentIndex(2)
        dock._on_search_shortcut()
        assert opened == [True]
    finally:
        dock.deleteLater()


def test_enter_find_and_replace_current(qapp):
    editor = QPlainTextEdit("Alpha beta alpha")
    dialog = TextSearchDialog(text_widget=editor)
    try:
        dialog.search_input.setText("alpha")
        assert len(dialog.matches) == 2

        dialog._find_next()
        assert dialog.current_match_index == 1

        dialog.replace_input.setText("gamma")
        dialog._replace_current()
        assert editor.toPlainText() == "Alpha beta gamma"
    finally:
        dialog.deleteLater()
        editor.deleteLater()


def test_replace_all_respects_whole_word_and_case(qapp):
    editor = QPlainTextEdit("cat catalog Cat cat")
    dialog = TextSearchDialog(text_widget=editor)
    try:
        dialog.case_checkbox.setChecked(True)
        dialog.whole_word_checkbox.setChecked(True)
        dialog.search_input.setText("cat")
        dialog.replace_input.setText("dog")

        dialog._replace_all()

        assert editor.toPlainText() == "dog catalog Cat dog"
        assert dialog.matches == []
    finally:
        dialog.deleteLater()
        editor.deleteLater()


def test_regex_replace_all_expands_groups(qapp):
    editor = QPlainTextEdit("item-12 item-34")
    dialog = TextSearchDialog(text_widget=editor)
    try:
        dialog.regex_checkbox.setChecked(True)
        dialog.search_input.setText(r"item-(\d+)")
        dialog.replace_input.setText(r"value-\1")

        dialog._replace_all()

        assert editor.toPlainText() == "value-12 value-34"
    finally:
        dialog.deleteLater()
        editor.deleteLater()
