#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for InsertPanel (Insert Text Tool).

Tests:
- Panel initialization and UI components
- Line number input and insertion modes
- Line lookup feature (search-based position)
- Advanced conditions (filename, path, ext, size, mtime, content)
- File filtering (extensions, include/exclude globs)
- Dynamic condition rows (add/remove)
- Results display and save functionality
"""
import pytest
from PySide6.QtWidgets import (QLineEdit, QCheckBox, QPushButton, QPlainTextEdit, 
                                QComboBox, QSpinBox)
from pathlib import Path

# Import from clarify package
from src.app import MainWindow
from src.core import InsertMode


class TestInsertPanelInitialization:
    """Test InsertPanel initialization and UI setup."""
    
    def test_panel_creation(self, main_window):
        """Test that InsertPanel initializes without errors."""
        # window created by fixture
        panel = main_window.insert_panel
        
        assert panel is not None
        assert panel.isVisible()
        
    def test_essential_widgets_exist(self, main_window):
        """Test that all essential UI widgets are created."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Path widgets
        assert hasattr(panel, 'ed_path')
        assert isinstance(panel.ed_path, QLineEdit)
        assert hasattr(panel, 'btn_browse')
        assert isinstance(panel.btn_browse, QPushButton)
        assert hasattr(panel, 'is_file')
        assert isinstance(panel.is_file, QCheckBox)
        
        # Line number widget
        assert hasattr(panel, 'spin_line')
        assert isinstance(panel.spin_line, QSpinBox)
        assert panel.spin_line.minimum() == 1
        assert panel.spin_line.maximum() == 10_000_000
        
        # Insert text widget
        assert hasattr(panel, 'ed_text')
        assert isinstance(panel.ed_text, QPlainTextEdit)
        
        # Insert mode combo
        assert hasattr(panel, 'cb_mode')
        assert isinstance(panel.cb_mode, QComboBox)
        assert panel.cb_mode.count() == 5  # 5 insert modes
        
        # Apply button
        assert hasattr(panel, 'btn_apply')
        assert isinstance(panel.btn_apply, QPushButton)
        
    def test_insert_modes_available(self, main_window):
        """Test that all 5 insert modes are available."""
        # window created by fixture
        panel = main_window.insert_panel
        
        expected_modes = [
            InsertMode.LEFT,
            InsertMode.RIGHT,
            InsertMode.REPLACE,
            InsertMode.INSERT_ABOVE,
            InsertMode.INSERT_BELOW
        ]
        
        available_modes = [panel.cb_mode.itemText(i) for i in range(panel.cb_mode.count())]
        
        for mode in expected_modes:
            assert mode in available_modes
            
    def test_line_lookup_widgets_exist(self, main_window):
        """Test that line lookup section exists."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Lookup query field
        assert hasattr(panel, 'ed_query')
        assert isinstance(panel.ed_query, QLineEdit)
        
        # Lookup checkboxes
        assert hasattr(panel, 'chk_lookup_case')
        assert isinstance(panel.chk_lookup_case, QCheckBox)
        assert hasattr(panel, 'chk_lookup_word')
        assert isinstance(panel.chk_lookup_word, QCheckBox)
        assert hasattr(panel, 'chk_lookup_regex')
        assert isinstance(panel.chk_lookup_regex, QCheckBox)
        
        # Occurrence selector
        assert hasattr(panel, 'cb_lookup_occurrence')
        assert isinstance(panel.cb_lookup_occurrence, QComboBox)
        assert panel.cb_lookup_occurrence.count() == 3  # First, Last, All
        
    def test_advanced_conditions_section_exists(self, main_window):
        """Test that Advanced Conditions section exists."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Logic operator
        assert hasattr(panel, 'combo_logic_op')
        assert isinstance(panel.combo_logic_op, QComboBox)
        
        # Condition rows (minimum 3 initial)
        assert hasattr(panel, 'cond_list')
        assert len(panel.cond_list) >= 3
        
    def test_results_tree_exists(self, main_window):
        """Test that results tree is initialized."""
        # window created by fixture
        panel = main_window.insert_panel
        
        assert hasattr(panel, 'results')
        assert panel.results is not None
        
    def test_default_values(self, main_window):
        """Test default values of widgets."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Line number defaults to 1
        assert panel.spin_line.value() == 1
        
        # Extension filter enabled by default
        assert panel.chk_use_ext_filter.isChecked() is True
        assert panel.ed_extensions.text() == ".ts,.tsx,.js,.jsx,.py,.md"
        
        # Exclude defaults
        assert "node_modules" in panel.ed_exc.text()
        
        # Sort results disabled by default
        assert panel.chk_sort_results.isChecked() is False
        
        # Logic operator defaults to AND
        assert panel.combo_logic_op.currentText() == "AND"


class TestInsertPanelOperations:
    """Test InsertPanel operations."""
    
    def test_path_field_accepts_input(self, main_window):
        """Test that path field accepts text input."""
        # window created by fixture
        panel = main_window.insert_panel
        
        test_path = "/tmp/test_file.py"
        panel.ed_path.setText(test_path)
        assert panel.ed_path.text() == test_path
        
    def test_line_number_adjustable(self, main_window):
        """Test that line number can be adjusted."""
        # window created by fixture
        panel = main_window.insert_panel
        
        panel.spin_line.setValue(42)
        assert panel.spin_line.value() == 42
        
        panel.spin_line.setValue(1000)
        assert panel.spin_line.value() == 1000
        
    def test_insert_text_field_accepts_input(self, main_window):
        """Test that insert text field accepts multi-line input."""
        # window created by fixture
        panel = main_window.insert_panel
        
        test_text = "Line 1\nLine 2\nLine 3"
        panel.ed_text.setPlainText(test_text)
        assert panel.ed_text.toPlainText() == test_text
        
    def test_insert_mode_selection(self, main_window):
        """Test that insert mode can be selected."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Select each mode
        for i in range(panel.cb_mode.count()):
            panel.cb_mode.setCurrentIndex(i)
            assert panel.cb_mode.currentIndex() == i


class TestLineLookupFeature:
    """Test line lookup (search-based positioning) feature."""
    
    def test_lookup_query_input(self, main_window):
        """Test that lookup query accepts text."""
        # window created by fixture
        panel = main_window.insert_panel
        
        query = "function searchMe"
        panel.ed_query.setText(query)
        assert panel.ed_query.text() == query
        
    def test_lookup_checkboxes_toggle(self, main_window):
        """Test that lookup option checkboxes can be toggled."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Case sensitive
        initial_case = panel.chk_lookup_case.isChecked()
        panel.chk_lookup_case.setChecked(not initial_case)
        assert panel.chk_lookup_case.isChecked() != initial_case
        
        # Whole word
        initial_word = panel.chk_lookup_word.isChecked()
        panel.chk_lookup_word.setChecked(not initial_word)
        assert panel.chk_lookup_word.isChecked() != initial_word
        
        # Regex
        initial_regex = panel.chk_lookup_regex.isChecked()
        panel.chk_lookup_regex.setChecked(not initial_regex)
        assert panel.chk_lookup_regex.isChecked() != initial_regex
        
    def test_occurrence_selector_options(self, main_window):
        """Test that occurrence selector has correct options."""
        # window created by fixture
        panel = main_window.insert_panel
        
        expected_options = ["First", "Last", "All"]
        actual_options = [panel.cb_lookup_occurrence.itemText(i) 
                         for i in range(panel.cb_lookup_occurrence.count())]
        
        assert actual_options == expected_options


class TestAdvancedConditionsInsertPanel:
    """Test Advanced Conditions in InsertPanel."""
    
    def test_add_condition_row(self, main_window):
        """Test that new condition rows can be added."""
        # window created by fixture
        panel = main_window.insert_panel
        
        initial_rows = len(panel.cond_list)
        panel._add_condition_row()
        assert len(panel.cond_list) == initial_rows + 1
        
    def test_condition_fields_available(self, main_window):
        """Test that condition fields include all expected options."""
        # window created by fixture
        panel = main_window.insert_panel
        
        if len(panel.cond_list) > 0:
            field_combo = panel.cond_list[0][0]
            
            # Get all field options
            fields = [field_combo.itemText(i) for i in range(field_combo.count())]
            
            # Expected fields
            expected = ["", "filename", "path", "ext", "size", "mtime", "content"]
            assert fields == expected
            
    def test_operators_available(self, main_window):
        """Test that operators are available for conditions."""
        # window created by fixture
        panel = main_window.insert_panel
        
        if len(panel.cond_list) > 0:
            operator_combo = panel.cond_list[0][1]
            
            # Get all operators
            operators = [operator_combo.itemText(i) for i in range(operator_combo.count())]
            
            # Expected operators
            expected = ["", "contains", "not contains", "equals", "not equals",
                       "starts with", "ends with", ">", "<", ">=", "<="]
            assert operators == expected
            
    def test_scope_options_available(self, main_window):
        """Test that scope options are available."""
        # window created by fixture
        panel = main_window.insert_panel
        
        if len(panel.cond_list) > 0:
            scope_combo = panel.cond_list[0][3]
            
            # Get all scope options
            scopes = [scope_combo.itemText(i) for i in range(scope_combo.count())]
            
            # Expected scopes
            expected = ["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag"]
            assert scopes == expected
            
    def test_clear_all_conditions(self, main_window):
        """Test that clear all conditions resets fields."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Set some values
        if len(panel.cond_list) > 0:
            panel.cond_list[0][2].setText("test_value")
            panel._clear_all_conditions()
            assert panel.cond_list[0][2].text() == ""
            
    def test_logic_operator_options(self, main_window):
        """Test that AND/OR logic operators are available."""
        # window created by fixture
        panel = main_window.insert_panel
        
        assert panel.combo_logic_op.count() == 2
        assert panel.combo_logic_op.itemText(0) == "AND"
        assert panel.combo_logic_op.itemText(1) == "OR"


class TestFileFilteringInsertPanel:
    """Test file filtering features in InsertPanel."""
    
    def test_extension_filter_toggle(self, main_window):
        """Test that extension filter can be enabled/disabled."""
        # window created by fixture
        panel = main_window.insert_panel
        
        initial_state = panel.chk_use_ext_filter.isChecked()
        panel.chk_use_ext_filter.setChecked(not initial_state)
        assert panel.chk_use_ext_filter.isChecked() != initial_state
        
    def test_include_globs_field(self, main_window):
        """Test that include globs field accepts patterns."""
        # window created by fixture
        panel = main_window.insert_panel
        
        pattern = "*.py,**/__init__.py"
        panel.ed_inc.setText(pattern)
        assert panel.ed_inc.text() == pattern
        
    def test_exclude_globs_field(self, main_window):
        """Test that exclude globs field accepts patterns."""
        # window created by fixture
        panel = main_window.insert_panel
        
        pattern = "node_modules,*.pyc,__pycache__"
        panel.ed_exc.setText(pattern)
        assert panel.ed_exc.text() == pattern


class TestResultsDisplayInsertPanel:
    """Test results display in InsertPanel."""
    
    def test_results_status_label(self, main_window):
        """Test that results status label exists."""
        # window created by fixture
        panel = main_window.insert_panel
        
        assert hasattr(panel, 'results_status')
        assert panel.results_status is not None
        
    def test_save_results_button(self, main_window):
        """Test that save results button exists."""
        # window created by fixture
        panel = main_window.insert_panel
        
        assert hasattr(panel, 'btn_save_results')
        assert isinstance(panel.btn_save_results, QPushButton)


class TestTooltipsInsertPanel:
    """Test that tooltips are set for accessibility."""
    
    def test_essential_tooltips(self, main_window):
        """Test that essential widgets have tooltips."""
        # window created by fixture
        panel = main_window.insert_panel
        
        # Essential widgets
        assert panel.ed_path.toolTip() != ""
        assert panel.btn_browse.toolTip() != ""
        assert panel.is_file.toolTip() != ""
        assert panel.spin_line.toolTip() != ""
        assert panel.ed_text.toolTip() != ""
        assert panel.cb_mode.toolTip() != ""
        assert panel.btn_apply.toolTip() != ""
        
        # Lookup widgets
        assert panel.ed_query.toolTip() != ""
        assert panel.chk_lookup_case.toolTip() != ""
        assert panel.chk_lookup_word.toolTip() != ""
        assert panel.chk_lookup_regex.toolTip() != ""
        assert panel.cb_lookup_occurrence.toolTip() != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
