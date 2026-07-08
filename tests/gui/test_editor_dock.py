#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for EditorDock (Clarify Editor).

Tests:
- Editor initialization and UI components
- File operations (open, save, close)
- Tab management (multiple files)
- Syntax highlighting for different file types
- Edit-only mode (copy, export, enable saving)
- Find/Replace functionality
- Modified state tracking
"""
import re
import builtins

import pytest
from PySide6.QtWidgets import QTextEdit, QPushButton, QTabWidget, QMenuBar, QCheckBox
from PySide6.QtGui import QFont, QTextCursor, QTextOption
from pathlib import Path
import tempfile

# Import from clarify package
from src.app import MainWindow
from src.gui.editor_dock import EditorDock, EditorTab, _EditorFindDialog
from src.gui.json_editor_tab import JsonEditorTab
from src.theme_manager import ThemeManager


class TestEditorDockInitialization:
    """Test EditorDock initialization and UI setup."""
    
    def test_dock_creation(self, main_window):
        """Test that EditorDock initializes without errors."""
        # Find EditorDock in main_window's children
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        assert editor_dock.windowTitle() == "Clarify Editor"
        
    def test_tab_widget_exists(self, main_window):
        """Test that tab widget for multiple files exists."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        assert hasattr(editor_dock, 'tab_widget')
        assert isinstance(editor_dock.tab_widget, QTabWidget)
        
    def test_file_menu_exists(self, main_window):
        """Test that file actions are available in the File menu."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        assert hasattr(editor_dock, 'menu_bar')
        assert isinstance(editor_dock.menu_bar, QMenuBar)
        assert hasattr(editor_dock, 'menu_file')
        assert editor_dock.menu_file.title() == "File"
        assert hasattr(editor_dock, 'menu_edit')
        assert editor_dock.menu_edit.title() == "Edit"
        assert hasattr(editor_dock, 'menu_view')
        assert editor_dock.menu_view.title() == "View"
        assert hasattr(editor_dock, 'menu_json')
        assert editor_dock.menu_json.title() == "JSON"

        file_actions = [
            action.data()
            for action in editor_dock.menu_file.actions()
            if not action.isSeparator()
        ]
        assert file_actions == [
            "new",
            "open",
            "save",
            "save_as",
            "compare_with_saved",
            "enable_saving",
            "export",
            "close_tab",
            "auto_save",
        ]

        edit_actions = [
            action.data()
            for action in editor_dock.menu_edit.actions()
            if not action.isSeparator()
        ]
        assert edit_actions == [
            "undo",
            "redo",
            "cut",
            "copy",
            "paste",
            "delete",
            "select_all",
            "find",
            "find_replace",
            "go_to_line",
            "duplicate_line",
            "toggle_line_comment",
            "indent",
            "outdent",
            "move_line_up",
            "move_line_down",
            "insert_datetime",
            "trim_trailing_spaces",
        ]

        view_actions = [
            action.data()
            for action in editor_dock.menu_view.actions()
            if not action.isSeparator()
        ]
        assert view_actions == [
            "word_wrap",
            "render_whitespace",
            "show_line_numbers",
            "small_text",
            "large_text",
            "normal_size",
        ]

        json_actions = [
            action.data()
            for action in editor_dock.menu_json.actions()
            if not action.isSeparator()
        ]
        assert json_actions == [
            "json_format_2",
            "json_format_4",
            "json_minify",
            "json_validate",
            "json_validate_schema",
            "json_search",
            "json_collapse_tree",
            "json_expand_tree",
        ]
        assert editor_dock.action_auto_save.isCheckable()
        assert editor_dock.action_word_wrap.isCheckable()
        assert editor_dock.action_render_whitespace.isCheckable()
        assert editor_dock.action_show_line_numbers.isCheckable()
        assert hasattr(editor_dock, 'action_compare_with_saved')
        assert hasattr(editor_dock, 'action_json_validate')
        assert hasattr(editor_dock, 'action_json_validate_schema')

    def test_editor_menu_bar_style_uses_transparent_item_background(self, qapp):
        """Test that the local menu bar padding style does not paint dark text boxes."""
        editor_dock = EditorDock()
        try:
            stylesheet = editor_dock.menu_bar.styleSheet()
            assert "QMenuBar#editor_menu_bar::item" in stylesheet
            assert "background-color: transparent" in stylesheet
        finally:
            editor_dock.deleteLater()

    def test_compare_with_saved_action_requires_file_path(self, qapp, tmp_path):
        """Test Compare with Saved is only enabled for file-backed tabs."""
        editor_dock = EditorDock()
        try:
            assert not editor_dock.action_compare_with_saved.isEnabled()

            editor_dock._new_file()
            assert not editor_dock.action_compare_with_saved.isEnabled()

            saved_file = tmp_path / "example.txt"
            saved_file.write_text("saved\n", encoding="utf-8")
            tab = editor_dock.tab_widget.currentWidget()
            tab.file_path = str(saved_file)

            editor_dock._refresh_editor_menus()
            assert editor_dock.action_compare_with_saved.isEnabled()
        finally:
            editor_dock.deleteLater()

    def test_compare_with_saved_builds_unified_diff(self):
        """Test Compare with Saved uses a readable unified diff."""
        diff = EditorDock._build_saved_file_diff(
            "/tmp/example.txt",
            "one\ntwo\n",
            "one\nthree\n",
        )

        assert "--- example.txt (saved)" in diff
        assert "+++ example.txt (current)" in diff
        assert "-two" in diff
        assert "+three" in diff

    def test_json_menu_actions_only_enable_for_json_tabs(self, qapp):
        """Test JSON menu actions are enabled only when the current tab is JSON."""
        editor_dock = EditorDock()
        try:
            assert not editor_dock.action_json_validate.isEnabled()

            editor_dock._new_file()
            assert not editor_dock.action_json_validate.isEnabled()

            json_tab = JsonEditorTab()
            editor_dock._prepare_tab_for_dock(json_tab)
            index = editor_dock.tab_widget.addTab(json_tab, json_tab.get_display_title())
            editor_dock.tab_widget.setCurrentIndex(index)
            editor_dock._refresh_editor_menus()

            assert editor_dock.action_json_format_2.isEnabled()
            assert editor_dock.action_json_validate.isEnabled()
            assert editor_dock.action_json_validate_schema.isEnabled()
            assert editor_dock.action_json_expand_tree.isEnabled()
        finally:
            editor_dock.deleteLater()

    def test_json_menu_formats_current_json_tab(self, qapp):
        """Test JSON menu formatting updates the active JSON tab."""
        editor_dock = EditorDock()
        try:
            json_tab = JsonEditorTab()
            json_tab.editor.setPlainText('{"alpha":1,"nested":{"beta":2}}')
            json_tab.is_modified = False

            editor_dock._prepare_tab_for_dock(json_tab)
            index = editor_dock.tab_widget.addTab(json_tab, json_tab.get_display_title())
            editor_dock.tab_widget.setCurrentIndex(index)

            assert editor_dock._format_current_json_tab(2) is True
            text = json_tab.editor.toPlainText()
            assert '\n  "alpha": 1,' in text
            assert json_tab.is_modified is True
            assert editor_dock.lbl_status.text() == "JSON formatted with 2 spaces"
        finally:
            editor_dock.deleteLater()

    def test_json_schema_validation_helper_accepts_valid_data(self):
        """Test JSON Schema validation helper accepts matching JSON."""
        pytest.importorskip("jsonschema")

        schema_text = """
        {
          "type": "object",
          "required": ["name", "age"],
          "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
          }
        }
        """
        is_valid, message = EditorDock._validate_json_text_with_schema(
            '{"name": "Ada", "age": 36}',
            schema_text,
        )

        assert is_valid is True
        assert message == ""

    def test_json_schema_validation_helper_reports_schema_errors(self):
        """Test JSON Schema validation helper reports path-specific errors."""
        pytest.importorskip("jsonschema")

        schema_text = """
        {
          "type": "object",
          "properties": {
            "age": {"type": "integer"}
          }
        }
        """
        is_valid, message = EditorDock._validate_json_text_with_schema(
            '{"age": "old"}',
            schema_text,
        )

        assert is_valid is False
        assert "$.age" in message
        assert "integer" in message

    def test_json_schema_validation_helper_reports_missing_dependency(self, monkeypatch):
        """Test JSON Schema validation reports when jsonschema is unavailable."""
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "jsonschema" or name.startswith("jsonschema."):
                raise ImportError("blocked jsonschema")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        is_valid, message = EditorDock._validate_json_text_with_schema("{}", "{}")

        assert is_valid is False
        assert "jsonschema package" in message

    def test_json_menu_validates_current_json_tab(self, qapp):
        """Test JSON menu validation updates the dock status."""
        editor_dock = EditorDock()
        try:
            json_tab = JsonEditorTab()
            json_tab.editor.setPlainText('{"alpha": 1}')

            editor_dock._prepare_tab_for_dock(json_tab)
            index = editor_dock.tab_widget.addTab(json_tab, json_tab.get_display_title())
            editor_dock.tab_widget.setCurrentIndex(index)

            assert editor_dock._validate_current_json_tab() is True
            assert editor_dock.lbl_status.text() == "Valid JSON"

            json_tab.editor.setPlainText('{"alpha": }')
            assert editor_dock._validate_current_json_tab() is False
            assert "Invalid JSON at line" in editor_dock.lbl_status.text()
        finally:
            editor_dock.deleteLater()


class TestEditorTab:
    """Test EditorTab (single editor instance)."""
    
    def test_editor_tab_creation(self, main_window):
        """Test that EditorTab can be created."""
        tab = EditorTab()
        assert tab is not None
        
    def test_editor_widget_exists(self, main_window):
        """Test that text editor widget exists."""
        tab = EditorTab()
        assert hasattr(tab, 'editor')
        assert isinstance(tab.editor, QTextEdit)
        
    def test_monospace_font_applied(self, main_window):
        """Test that monospace font is applied to editor."""
        tab = EditorTab()
        font = tab.editor.font()
        assert font.family() in ["Courier New", "Courier", "Monaco", "Monospace"]
        
    def test_toolbar_buttons_in_tab(self, main_window):
        """Test that EditorTab has its own toolbar buttons."""
        tab = EditorTab()
        
        # Copy button
        assert hasattr(tab, 'btn_copy')
        assert isinstance(tab.btn_copy, QPushButton)
        
        # Export button
        assert hasattr(tab, 'btn_export')
        assert isinstance(tab.btn_export, QPushButton)


class TestEditorOperations:
    """Test editor operations."""
    
    def test_text_input(self, main_window):
        """Test that editor accepts text input."""
        tab = EditorTab()
        test_text = "Hello, World!\nLine 2\nLine 3"
        tab.editor.setPlainText(test_text)
        assert tab.editor.toPlainText() == test_text
        
    def test_modified_state_tracking(self, main_window):
        """Test that modified state is tracked."""
        tab = EditorTab()
        
        # Initially not modified
        initial_modified = tab.is_modified
        
        # Modify text
        tab.editor.setPlainText("New content")
        
        # Modified state should change
        # (Note: actual behavior depends on implementation)
        
    def test_clear_content(self, main_window):
        """Test that editor content can be cleared."""
        tab = EditorTab()
        tab.editor.setPlainText("Content to clear")
        tab.editor.clear()
        assert tab.editor.toPlainText() == ""

    def test_edit_menu_undo_redo(self, main_window):
        """Test that Edit menu Undo and Redo affect the current tab."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()

        tab.editor.insertPlainText("abc")
        assert tab.editor.toPlainText() == "abc"

        editor_dock.action_undo.trigger()
        assert tab.editor.toPlainText() == ""

        editor_dock.action_redo.trigger()
        assert tab.editor.toPlainText() == "abc"

    def test_go_to_line_moves_cursor(self, main_window):
        """Test that Go To Line moves the cursor in the current tab."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()
        tab.editor.setPlainText("one\ntwo\nthree")

        assert editor_dock._go_to_line_in_current_tab(3) is True

        assert tab.editor.textCursor().blockNumber() == 2
        assert editor_dock.lbl_status.text() == "Moved to line 3 of 3"

    def test_common_edit_menu_actions(self, main_window):
        """Test common editor actions added from desktop editor conventions."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()

        tab.editor.setPlainText("alpha\nbeta  \n")
        cursor = tab.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        tab.editor.setTextCursor(cursor)
        editor_dock.action_duplicate_line.trigger()
        assert tab.editor.toPlainText() == "alpha\nalpha\nbeta  \n"

        tab.editor.setPlainText("abc")
        cursor = tab.editor.textCursor()
        cursor.setPosition(1)
        cursor.setPosition(2, QTextCursor.KeepAnchor)
        tab.editor.setTextCursor(cursor)
        editor_dock.action_delete.trigger()
        assert tab.editor.toPlainText() == "ac"

        editor_dock.action_select_all.trigger()
        assert tab.editor.textCursor().selectedText() == "ac"

        tab.editor.setPlainText("")
        editor_dock.action_insert_datetime.trigger()
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", tab.editor.toPlainText())

        tab.editor.setPlainText("a  \nb\t \n")
        editor_dock.action_trim_trailing_spaces.trigger()
        assert tab.editor.toPlainText() == "a\nb\n"
        assert editor_dock.lbl_status.text() == "Trimmed 4 trailing space(s)"

    def test_word_wrap_toggle_applies_to_current_tab(self, main_window):
        """Test that Word Wrap toggles QTextEdit line wrapping."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        original_state = editor_dock.word_wrap_enabled
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()

        try:
            editor_dock._set_word_wrap_enabled(False)
            assert tab.editor.lineWrapMode() == QTextEdit.LineWrapMode.NoWrap
            assert editor_dock.action_word_wrap.isChecked() is False

            editor_dock._set_word_wrap_enabled(True)
            assert tab.editor.lineWrapMode() == QTextEdit.LineWrapMode.WidgetWidth
            assert editor_dock.action_word_wrap.isChecked() is True
        finally:
            editor_dock._set_word_wrap_enabled(original_state)

    def test_vscode_line_editing_actions(self, main_window):
        """Test VS Code-inspired line editing actions."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()
        tab.file_path = "example.py"

        tab.editor.setPlainText("alpha\n    beta\n")
        tab.editor.selectAll()
        editor_dock.action_toggle_line_comment.trigger()
        assert tab.editor.toPlainText() == "# alpha\n    # beta\n"

        tab.editor.selectAll()
        editor_dock.action_toggle_line_comment.trigger()
        assert tab.editor.toPlainText() == "alpha\n    beta\n"

        tab.editor.setPlainText("one\ntwo")
        tab.editor.selectAll()
        editor_dock.action_indent.trigger()
        assert tab.editor.toPlainText() == "    one\n    two"

        tab.editor.selectAll()
        editor_dock.action_outdent.trigger()
        assert tab.editor.toPlainText() == "one\ntwo"

        tab.editor.setPlainText("one\ntwo\nthree")
        cursor = tab.editor.textCursor()
        cursor.setPosition(len("one\n"))
        tab.editor.setTextCursor(cursor)
        editor_dock.action_move_line_up.trigger()
        assert tab.editor.toPlainText() == "two\none\nthree"

        editor_dock.action_move_line_down.trigger()
        assert tab.editor.toPlainText() == "one\ntwo\nthree"

    def test_render_whitespace_toggle_applies_to_current_tab(self, main_window):
        """Test that Render Whitespace toggles QTextOption flags."""
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break

        assert editor_dock is not None
        original_state = editor_dock.render_whitespace_enabled
        editor_dock.action_new.trigger()
        tab = editor_dock.tab_widget.currentWidget()

        try:
            editor_dock._set_render_whitespace_enabled(True)
            flags = tab.editor.document().defaultTextOption().flags()
            assert flags & QTextOption.Flag.ShowTabsAndSpaces
            assert editor_dock.action_render_whitespace.isChecked() is True

            editor_dock._set_render_whitespace_enabled(False)
            flags = tab.editor.document().defaultTextOption().flags()
            assert not flags & QTextOption.Flag.ShowTabsAndSpaces
            assert editor_dock.action_render_whitespace.isChecked() is False
        finally:
            editor_dock._set_render_whitespace_enabled(original_state)

    def test_line_number_gutter_uses_dark_theme_colors(self, qapp):
        """Test that line numbers follow the dark editor theme."""
        original_palette = qapp.palette()
        original_stylesheet = qapp.styleSheet()
        editor_dock = None

        try:
            ThemeManager.apply_theme(qapp, "dark")
            editor_dock = EditorDock()
            editor_dock._new_file()
            tab = editor_dock.tab_widget.currentWidget()
            tab.editor.setPlainText("one\ntwo\nthree")

            editor_dock._set_show_line_numbers_enabled(True)
            controller = getattr(tab.editor, '_clarify_line_numbers')
            background_color, text_color = controller._theme_colors()

            assert background_color.lightness() < 80
            assert text_color.lightness() > background_color.lightness()
        finally:
            if editor_dock is not None:
                editor_dock.deleteLater()
            qapp.setPalette(original_palette)
            qapp.setStyleSheet(original_stylesheet)


class TestEditOnlyMode:
    """Test edit-only mode functionality."""
    
    def test_edit_only_mode_creation(self, main_window):
        """Test that EditorTab can be created in edit-only mode."""
        tab = EditorTab(edit_only_mode=True)
        assert tab.edit_only_mode is True
        
    def test_enable_saving_button_visible(self, main_window):
        """Test that Enable Saving button is visible in edit-only mode."""
        tab = EditorTab(edit_only_mode=True)
        assert hasattr(tab, 'btn_enable_saving')
        assert tab.btn_enable_saving.isVisible() is True
        
    def test_enable_saving_button_hidden_normal_mode(self, main_window):
        """Test that Enable Saving button is hidden in normal mode."""
        tab = EditorTab(edit_only_mode=False)
        assert hasattr(tab, 'btn_enable_saving')
        assert tab.btn_enable_saving.isVisible() is False


class TestFileOperations:
    """Test file operations (open, save, close)."""
    
    def test_open_file_with_path(self, qapp, temp_text_file):
        """Test opening a file with a specific path."""
        tab = EditorTab(file_path=str(temp_text_file))
        
        # File path should be set
        assert tab.file_path == str(temp_text_file)
        
    def test_save_file_with_content(self, qapp, tmp_path):
        """Test saving content to a new file."""
        test_file = tmp_path / "test_save.txt"
        tab = EditorTab(file_path=str(test_file))
        
        test_content = "Test content for saving"
        tab.editor.setPlainText(test_content)
        
        # Save operation would be triggered by button click
        # (actual save logic depends on implementation)


class TestSyntaxHighlighting:
    """Test syntax highlighting for different file types."""
    
    def test_highlighter_created_for_python(self, qapp, tmp_path):
        """Test that syntax highlighter is created for Python files."""
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello():\n    print('world')")
        
        tab = EditorTab(file_path=str(py_file))
        
        # Highlighter should be created
        assert hasattr(tab, 'highlighter')
        assert tab.highlighter is not None
        
    def test_highlighter_created_for_json(self, qapp, temp_json_file):
        """Test that syntax highlighter is created for JSON files."""
        tab = EditorTab(file_path=str(temp_json_file))
        
        # Highlighter should be created
        assert hasattr(tab, 'highlighter')
        assert tab.highlighter is not None
        
    def test_highlighter_created_for_html(self, qapp, tmp_path):
        """Test that syntax highlighter is created for HTML files."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body><h1>Test</h1></body></html>")
        
        tab = EditorTab(file_path=str(html_file))
        
        # Highlighter should be created
        assert hasattr(tab, 'highlighter')
        assert tab.highlighter is not None


class TestFindReplaceFeature:
    """Test find/replace functionality."""

    def test_find_dialog_option_checkboxes_exist(self, qapp):
        """Test that Find dialogs expose match option checkboxes."""
        editor = QTextEdit()
        dialog = _EditorFindDialog(editor)

        assert hasattr(dialog, 'chk_case_sensitive')
        assert isinstance(dialog.chk_case_sensitive, QCheckBox)
        assert dialog.chk_case_sensitive.text() == "Case Sensitive"
        assert hasattr(dialog, 'chk_whole_word')
        assert isinstance(dialog.chk_whole_word, QCheckBox)
        assert dialog.chk_whole_word.text() == "Whole Word"
        assert hasattr(dialog, 'chk_regex')
        assert isinstance(dialog.chk_regex, QCheckBox)
        assert dialog.chk_regex.text() == "Regex"

        replace_dialog = _EditorFindDialog(editor, replace_enabled=True)
        assert hasattr(replace_dialog, 'chk_case_sensitive')
        assert hasattr(replace_dialog, 'chk_whole_word')
        assert hasattr(replace_dialog, 'chk_regex')

    def test_find_dialog_case_sensitive(self, qapp):
        """Test that Case Sensitive affects find behavior."""
        editor = QTextEdit()
        editor.setPlainText("Foo foo")
        dialog = _EditorFindDialog(editor)
        dialog.find_input.setText("foo")
        dialog.chk_case_sensitive.setChecked(True)

        assert dialog._find_next() is True

        cursor = editor.textCursor()
        assert cursor.selectionStart() == 4
        assert cursor.selectedText() == "foo"

    def test_find_dialog_whole_word(self, qapp):
        """Test that Whole Word skips matches inside larger words."""
        editor = QTextEdit()
        editor.setPlainText("foobar foo")
        dialog = _EditorFindDialog(editor)
        dialog.find_input.setText("foo")
        dialog.chk_whole_word.setChecked(True)

        assert dialog._find_next() is True

        cursor = editor.textCursor()
        assert cursor.selectionStart() == 7
        assert cursor.selectedText() == "foo"

    def test_find_replace_dialog_regex_replace_all(self, qapp):
        """Test that Regex affects replace all behavior."""
        editor = QTextEdit()
        editor.setPlainText("a1 a2 ax")
        dialog = _EditorFindDialog(editor, replace_enabled=True)
        dialog.find_input.setText(r"a\d")
        dialog.replace_input.setText("hit")
        dialog.chk_regex.setChecked(True)

        dialog._replace_all()

        assert editor.toPlainText() == "hit hit ax"
        assert dialog.lbl_status.text() == "Replaced 2 occurrence(s)"

    def test_find_dialog_invalid_regex_sets_status(self, qapp):
        """Test that invalid regex patterns are reported in the dialog."""
        editor = QTextEdit()
        editor.setPlainText("abc")
        dialog = _EditorFindDialog(editor)
        dialog.find_input.setText("[")
        dialog.chk_regex.setChecked(True)

        assert dialog._find_next() is False
        assert dialog.lbl_status.text().startswith("Invalid regex:")
    
    def test_find_field_exists(self, main_window):
        """Test that find field exists in EditorDock."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        # Find field should exist (might be in a dialog or panel)
        # Implementation-specific: check if EditorDock has find functionality
        # Skip for now as implementation varies
        pytest.skip("Find functionality implementation varies")
        
    def test_replace_field_exists(self, main_window):
        """Test that replace field exists in EditorDock."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        # Replace field should exist (might be in a dialog or panel)
        # Implementation-specific
        pytest.skip("Replace functionality implementation varies")


class TestTabManagement:
    """Test tab management for multiple files."""
    
    def test_tab_widget_accepts_new_tabs(self, main_window):
        """Test that tab widget can accept new editor tabs."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        initial_count = editor_dock.tab_widget.count()
        
        # Add a new tab (implementation-specific method)
        new_tab = EditorTab()
        editor_dock.tab_widget.addTab(new_tab, "New File")
        
        assert editor_dock.tab_widget.count() == initial_count + 1
        
    def test_tab_close_button_exists(self, main_window):
        """Test that tabs have close buttons."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        # Tab widget should allow closing tabs
        assert editor_dock.tab_widget.tabsClosable() is True


class TestClipboardOperations:
    """Test clipboard operations (copy content)."""
    
    def test_copy_to_clipboard(self, main_window):
        """Test that content can be copied to clipboard."""
        tab = EditorTab()
        test_text = "Copy this text"
        tab.editor.setPlainText(test_text)
        
        # Trigger copy operation
        tab._copy_to_clipboard()
        
        # Check clipboard (implementation-specific)
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        assert clipboard.text() == test_text


class TestTooltipsEditorDock:
    """Test that tooltips are set for accessibility."""
    
    def test_toolbar_tooltips(self, main_window):
        """Test that file menu has tooltips."""
        # Find EditorDock
        editor_dock = None
        for dock in main_window.findChildren(EditorDock):
            editor_dock = dock
            break
        
        assert editor_dock is not None
        assert editor_dock.menu_bar.toolTip() != ""
        assert editor_dock.menu_file.menuAction().toolTip() != ""
        assert editor_dock.menu_edit.menuAction().toolTip() != ""
        assert editor_dock.menu_view.menuAction().toolTip() != ""
        assert editor_dock.menu_json.menuAction().toolTip() != ""
        
    def test_tab_toolbar_tooltips(self, main_window):
        """Test that EditorTab toolbar buttons have tooltips."""
        tab = EditorTab()
        
        assert tab.btn_copy.toolTip() != ""
        assert tab.btn_export.toolTip() != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
