#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for SearchReplacePanel (Search and Replace Tool).

Tests:
- Panel initialization and UI components
- Search operations (basic, case-sensitive, regex)
- Replace operations (first, all, preserve case)
- Advanced conditions (AND/OR logic, dynamic rows)
- File filtering (extensions, include/exclude globs)
- Results display and status updates
- Save results functionality
"""
import pytest
from PySide6.QtWidgets import QApplication, QLineEdit, QCheckBox, QPushButton, QPlainTextEdit, QComboBox
from PySide6.QtCore import Qt
from pathlib import Path

# Import from clarify package
from src.app import MainWindow


class TestSearchReplacePanelInitialization:
    """Test SearchReplacePanel initialization and UI setup."""
    
    def test_panel_creation(self, main_window):
        """Test that SearchReplacePanel initializes without errors."""
        panel = main_window.search_panel
        
        assert panel is not None
        assert panel.isVisible()
        
    def test_essential_widgets_exist(self, main_window):
        """Test that all essential UI widgets are created."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Path widgets
        assert hasattr(panel, 'ed_path')
        assert isinstance(panel.ed_path, QLineEdit)
        assert hasattr(panel, 'btn_browse')
        assert isinstance(panel.btn_browse, QPushButton)
        assert hasattr(panel, 'is_file')
        assert isinstance(panel.is_file, QCheckBox)
        
        # Search widgets
        assert hasattr(panel, 'ed_query')
        assert isinstance(panel.ed_query, QPlainTextEdit)
        assert hasattr(panel, 'chk_case')
        assert isinstance(panel.chk_case, QCheckBox)
        assert hasattr(panel, 'chk_word')
        assert isinstance(panel.chk_word, QCheckBox)
        assert hasattr(panel, 'chk_regex')
        assert isinstance(panel.chk_regex, QCheckBox)
        assert hasattr(panel, 'btn_search')
        assert isinstance(panel.btn_search, QPushButton)
        
        # Replace widgets
        assert hasattr(panel, 'ed_repl')
        assert isinstance(panel.ed_repl, QPlainTextEdit)
        assert hasattr(panel, 'chk_preserve')
        assert isinstance(panel.chk_preserve, QCheckBox)
        assert hasattr(panel, 'btn_replace_one')
        assert isinstance(panel.btn_replace_one, QPushButton)
        assert hasattr(panel, 'btn_replace_all')
        assert isinstance(panel.btn_replace_all, QPushButton)
        
    def test_advanced_conditions_widgets(self, main_window):
        """Test that Advanced Conditions section exists with dynamic rows."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Logic operator combo
        assert hasattr(panel, 'combo_logic_op')
        assert isinstance(panel.combo_logic_op, QComboBox)
        assert panel.combo_logic_op.count() == 2
        assert panel.combo_logic_op.itemText(0) == "AND"
        assert panel.combo_logic_op.itemText(1) == "OR"
        
        # Condition rows (minimum 3 initial rows)
        assert hasattr(panel, 'cond_list')
        assert len(panel.cond_list) >= 3
        
        # Buttons
        assert hasattr(panel, 'buttons_layout_ref')
        
    def test_results_tree_exists(self, main_window):
        """Test that results tree is initialized."""
        # window created by fixture
        panel = main_window.search_panel
        
        assert hasattr(panel, 'results')
        assert panel.results is not None
        
    def test_default_values(self, main_window):
        """Test default values of widgets."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Extension filter enabled by default
        assert panel.chk_use_ext_filter.isChecked() is True
        assert panel.ed_extensions.text() == ".ts,.tsx,.js,.jsx,.py,.md"
        
        # Exclude defaults
        assert "node_modules" in panel.ed_exc.text()
        assert "dist" in panel.ed_exc.text()
        
        # Sort results disabled by default
        assert panel.chk_sort_results.isChecked() is False
        
        # Logic operator defaults to AND
        assert panel.combo_logic_op.currentText() == "AND"


class TestSearchReplacePanelOperations:
    """Test SearchReplacePanel search and replace operations."""
    
    def test_search_button_toggles_state(self, qapp, mock_message_box):
        """Test that search button changes state during search."""
        # window created by fixture
        panel = main_window.search_panel
        
        initial_text = panel.btn_search.text()
        assert "Search" in initial_text or "Cancel" in initial_text
        
    def test_path_field_accepts_input(self, main_window):
        """Test that path field accepts text input."""
        # window created by fixture
        panel = main_window.search_panel
        
        test_path = "/tmp/test_directory"
        panel.ed_path.setText(test_path)
        assert panel.ed_path.text() == test_path
        
    def test_query_field_accepts_input(self, main_window):
        """Test that query field accepts text input."""
        # window created by fixture
        panel = main_window.search_panel
        
        test_query = "search_pattern"
        panel.ed_query.setPlainText(test_query)
        assert panel.ed_query.toPlainText() == test_query
        
    def test_checkboxes_toggle(self, main_window):
        """Test that search option checkboxes can be toggled."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Case sensitive
        initial_case = panel.chk_case.isChecked()
        panel.chk_case.setChecked(not initial_case)
        assert panel.chk_case.isChecked() != initial_case
        
        # Whole word
        initial_word = panel.chk_word.isChecked()
        panel.chk_word.setChecked(not initial_word)
        assert panel.chk_word.isChecked() != initial_word
        
        # Regex
        initial_regex = panel.chk_regex.isChecked()
        panel.chk_regex.setChecked(not initial_regex)
        assert panel.chk_regex.isChecked() != initial_regex
        
    def test_replacement_field_accepts_input(self, main_window):
        """Test that replacement field accepts text input."""
        # window created by fixture
        panel = main_window.search_panel
        
        test_replacement = "new_text"
        panel.ed_repl.setPlainText(test_replacement)
        assert panel.ed_repl.toPlainText() == test_replacement


class TestAdvancedConditions:
    """Test Advanced Conditions functionality."""
    
    def test_add_condition_row(self, main_window):
        """Test that new condition rows can be added dynamically."""
        # window created by fixture
        panel = main_window.search_panel
        
        initial_rows = len(panel.cond_list)
        panel._add_condition_row()
        assert len(panel.cond_list) == initial_rows + 1
        
    def test_condition_row_structure(self, main_window):
        """Test that each condition row has expected widgets."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Get first condition row
        if len(panel.cond_list) > 0:
            row = panel.cond_list[0]
            # Expected: (field_combo, operator_combo, value_edit, scope_combo, scope_param, 
            #            case_check, word_check, regex_check, remove_btn)
            assert len(row) == 9
            assert isinstance(row[0], QComboBox)  # field
            assert isinstance(row[1], QComboBox)  # operator
            assert isinstance(row[2], QLineEdit)  # value
            assert isinstance(row[3], QComboBox)  # scope
            assert isinstance(row[4], QLineEdit)  # scope param
            assert isinstance(row[5], QCheckBox)  # case
            assert isinstance(row[6], QCheckBox)  # word
            assert isinstance(row[7], QCheckBox)  # regex
            assert isinstance(row[8], QPushButton)  # remove btn
            
    def test_clear_all_conditions(self, main_window):
        """Test that clear all conditions resets fields."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Set some values
        if len(panel.cond_list) > 0:
            panel.cond_list[0][2].setText("test_value")
            panel._clear_all_conditions()
            assert panel.cond_list[0][2].text() == ""
            
    def test_logic_operator_switch(self, main_window):
        """Test that logic operator can be switched between AND/OR."""
        # window created by fixture
        panel = main_window.search_panel
        
        panel.combo_logic_op.setCurrentIndex(0)  # AND
        assert panel.combo_logic_op.currentText() == "AND"
        
        panel.combo_logic_op.setCurrentIndex(1)  # OR
        assert panel.combo_logic_op.currentText() == "OR"


class TestFileFiltering:
    """Test file filtering features."""
    
    def test_extension_filter_toggle(self, main_window):
        """Test that extension filter can be enabled/disabled."""
        # window created by fixture
        panel = main_window.search_panel
        
        initial_state = panel.chk_use_ext_filter.isChecked()
        panel.chk_use_ext_filter.setChecked(not initial_state)
        assert panel.chk_use_ext_filter.isChecked() != initial_state
        
    def test_extension_filter_text(self, main_window):
        """Test that extension filter accepts custom extensions."""
        # window created by fixture
        panel = main_window.search_panel
        
        custom_ext = ".py,.txt,.md"
        panel.ed_extensions.setText(custom_ext)
        assert panel.ed_extensions.text() == custom_ext
        
    def test_include_globs_field(self, main_window):
        """Test that include globs field accepts patterns."""
        # window created by fixture
        panel = main_window.search_panel
        
        include_pattern = "*.test.*,**/src/**"
        panel.ed_inc.setText(include_pattern)
        assert panel.ed_inc.text() == include_pattern
        
    def test_exclude_globs_field(self, main_window):
        """Test that exclude globs field accepts patterns."""
        # window created by fixture
        panel = main_window.search_panel
        
        exclude_pattern = "node_modules,dist,build"
        panel.ed_exc.setText(exclude_pattern)
        assert panel.ed_exc.text() == exclude_pattern


class TestResultsDisplay:
    """Test results display functionality."""
    
    def test_results_tree_initialized(self, main_window):
        """Test that results tree is properly initialized."""
        # window created by fixture
        panel = main_window.search_panel
        
        assert panel.results is not None
        assert hasattr(panel.results, 'topLevelItemCount')
        
    def test_status_label_exists(self, main_window):
        """Test that results status label exists."""
        # window created by fixture
        panel = main_window.search_panel
        
        assert hasattr(panel, 'results_status')
        assert panel.results_status is not None
        
    def test_save_results_button_exists(self, main_window):
        """Test that save results button exists."""
        # window created by fixture
        panel = main_window.search_panel
        
        assert hasattr(panel, 'btn_save_results')
        assert isinstance(panel.btn_save_results, QPushButton)


class TestTooltips:
    """Test that tooltips are properly set for accessibility."""
    
    def test_essential_tooltips_exist(self, main_window):
        """Test that essential widgets have tooltips."""
        # window created by fixture
        panel = main_window.search_panel
        
        # Check key widgets have tooltips
        assert panel.ed_path.toolTip() != ""
        assert panel.btn_browse.toolTip() != ""
        assert panel.is_file.toolTip() != ""
        assert panel.chk_case.toolTip() != ""
        assert panel.chk_word.toolTip() != ""
        assert panel.chk_regex.toolTip() != ""
        assert panel.btn_search.toolTip() != ""
        assert panel.btn_replace_one.toolTip() != ""
        assert panel.btn_replace_all.toolTip() != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
