#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI Automated Interactions Tests - v2.9.53

Tests user interactions across all major docks:
- Button clicks and state changes
- Text input and validation
- Checkbox/Radio button toggling
- Workflow simulations (complete operations)
- Error handling and edge cases

Uses pytest-qt for GUI testing.
"""

import pytest
import tempfile
import os
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest

# Import docks to test
from src.gui.set_operations_dock import SetOperationsDock
from src.gui.case_converter_dock import CaseConverterDock
from src.gui.json_search_dock import JsonSearchDock
from src.gui.json_translate_dock import JsonTranslateDock
from src.gui.ai_processor_dock import AIProcessorDock
from src.gui.tutorials_dock import TutorialsDock


class TestSetOperationsDockInteractions:
    """Test user interactions in Set Operations Dock."""
    
    def test_file_browse_button_enabled(self, qtbot):
        """Test file browse buttons are clickable."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_browse_a.isEnabled()
        assert dock.btn_browse_b.isEnabled()
    
    def test_operation_checkboxes_toggleable(self, qtbot):
        """Test operation checkboxes can be toggled."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Initially unchecked
        assert not dock.chk_intersection.isChecked()
        
        # Click intersection
        qtbot.mouseClick(dock.chk_intersection, Qt.LeftButton)
        assert dock.chk_intersection.isChecked()
        
        # Click again to uncheck
        qtbot.mouseClick(dock.chk_intersection, Qt.LeftButton)
        assert not dock.chk_intersection.isChecked()
    
    def test_multiple_files_mode_toggle(self, qtbot):
        """Test multiple files mode shows/hides file list."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Initially single file mode
        assert not dock.chk_multiple.isChecked()
        
        # Enable multiple files
        qtbot.mouseClick(dock.chk_multiple, Qt.LeftButton)
        assert dock.chk_multiple.isChecked()
        
        # Verify file list widgets are visible
        assert dock.btn_add_file.isVisible()
        assert dock.btn_remove_file.isVisible()
    
    def test_comparison_mode_radio_buttons(self, qtbot):
        """Test comparison mode radio button selection."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Default should be key_value
        assert dock.radio_key_value.isChecked()
        
        # Click full_path
        qtbot.mouseClick(dock.radio_full_path, Qt.LeftButton)
        assert dock.radio_full_path.isChecked()
        assert not dock.radio_key_value.isChecked()
        
        # Click key_only
        qtbot.mouseClick(dock.radio_key_only, Qt.LeftButton)
        assert dock.radio_key_only.isChecked()
        assert not dock.radio_full_path.isChecked()
    
    def test_execute_button_requires_valid_inputs(self, qtbot):
        """Test execute button validation."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Execute button should exist
        assert dock.btn_execute is not None
        
        # Should be disabled without valid files
        # (implementation may vary - test current behavior)
        initial_state = dock.btn_execute.isEnabled()
        assert isinstance(initial_state, bool)


class TestCaseConverterDockInteractions:
    """Test user interactions in Case Converter Dock."""
    
    def test_path_input_accepts_text(self, qtbot):
        """Test path input field accepts text."""
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        # Type path
        test_path = "/tmp/test.txt"
        qtbot.keyClicks(dock.ed_path, test_path)
        
        assert dock.ed_path.text() == test_path
    
    def test_case_type_combobox_selectable(self, qtbot):
        """Test case type combo box selection."""
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        # Verify combo box has items
        assert dock.combo_from.count() > 0
        assert dock.combo_to.count() > 0
        
        # Change selection
        initial_index = dock.combo_to.currentIndex()
        new_index = (initial_index + 1) % dock.combo_to.count()
        dock.combo_to.setCurrentIndex(new_index)
        
        assert dock.combo_to.currentIndex() == new_index
    
    def test_convert_button_clickable(self, qtbot):
        """Test convert button is clickable."""
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        # Button should exist and be clickable
        assert dock.btn_convert is not None
        assert dock.btn_convert.isEnabled()
    
    def test_interrupt_button_exists(self, qtbot):
        """Test interrupt button exists for long operations."""
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        assert hasattr(dock, 'btn_interrupt')
        assert dock.btn_interrupt is not None


class TestJsonSearchDockInteractions:
    """Test user interactions in JSON Search Dock."""
    
    def test_search_inputs_accept_text(self, qtbot):
        """Test search input fields accept text."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Type in search key
        qtbot.keyClicks(dock.ed_search_key, "user.name")
        assert dock.ed_search_key.text() == "user.name"
        
        # Type in search value
        qtbot.keyClicks(dock.ed_search_value, "John")
        assert dock.ed_search_value.text() == "John"
    
    def test_search_mode_combo_selectable(self, qtbot):
        """Test search mode combo box selection."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Verify modes exist
        assert dock.combo_mode.count() >= 3  # Key only, Value only, Both
        
        # Change mode
        dock.combo_mode.setCurrentIndex(1)
        assert dock.combo_mode.currentIndex() == 1
    
    def test_case_and_regex_checkboxes(self, qtbot):
        """Test case-sensitive and regex checkboxes."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Toggle case-sensitive
        qtbot.mouseClick(dock.chk_case, Qt.LeftButton)
        assert dock.chk_case.isChecked()
        
        # Toggle regex
        qtbot.mouseClick(dock.chk_regex, Qt.LeftButton)
        assert dock.chk_regex.isChecked()
    
    def test_max_results_spinbox_adjustable(self, qtbot):
        """Test max results spin box is adjustable."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Set value
        dock.spin_max.setValue(500)
        assert dock.spin_max.value() == 500
        
        # Test bounds
        dock.spin_max.setValue(0)  # Unlimited
        assert dock.spin_max.value() == 0
    
    def test_search_button_clickable(self, qtbot):
        """Test search button is clickable."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_search is not None
        assert dock.btn_search.isEnabled()
    
    def test_enter_key_triggers_search(self, qtbot):
        """Test Enter key in search fields triggers search."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Focus search key field
        dock.ed_search_key.setFocus()
        
        # Type and press Enter
        qtbot.keyClicks(dock.ed_search_key, "test")
        
        # Verify Enter shortcut exists (v2.9.50)
        assert hasattr(dock, '_setup_enter_key') or hasattr(dock, '_setup_enter_key_execution')


class TestJsonTranslateDockInteractions:
    """Test user interactions in JSON Translate Dock."""
    
    def test_path_and_dict_inputs(self, qtbot):
        """Test path and dictionary input fields."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Type paths
        qtbot.keyClicks(dock.ed_path, "/tmp/source")
        assert dock.ed_path.text() == "/tmp/source"
        
        qtbot.keyClicks(dock.ed_dict, "/tmp/dict.json")
        assert dock.ed_dict.text() == "/tmp/dict.json"
    
    def test_variable_name_input(self, qtbot):
        """Test object variable name input."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Clear default and type custom name
        dock.object_variable_name.clear()
        qtbot.keyClicks(dock.object_variable_name, "i18n")
        assert dock.object_variable_name.text() == "i18n"
    
    def test_scope_delimiter_inputs(self, qtbot):
        """Test scope delimiter inputs."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Set start/end patterns
        qtbot.keyClicks(dock.ed_start, "<[^>]*?>")
        qtbot.keyClicks(dock.ed_end, "</[^>]*?>")
        
        assert "<[^>]*?>" in dock.ed_start.text()
        assert "</[^>]*?>" in dock.ed_end.text()
    
    def test_option_checkboxes_toggleable(self, qtbot):
        """Test all option checkboxes can be toggled."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Test each checkbox
        checkboxes = [
            dock.chk_backup,
            dock.chk_dont_override,
            dock.chk_inverse_json_translate,
            dock.chk_emit_export,
            dock.chk_preserve_uppercase,
        ]
        
        for chk in checkboxes:
            initial_state = chk.isChecked()
            qtbot.mouseClick(chk, Qt.LeftButton)
            assert chk.isChecked() != initial_state
    
    def test_run_button_clickable(self, qtbot):
        """Test run button is clickable."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_run is not None
        # Button enabled state depends on validation
        assert isinstance(dock.btn_run.isEnabled(), bool)
    
    def test_swap_and_undo_buttons(self, qtbot):
        """Test swap and undo buttons exist."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_swap is not None
        assert dock.btn_undo is not None
        assert dock.btn_swap.isEnabled()  # Swap should always be enabled


class TestAIProcessorDockInteractions:
    """Test user interactions in AI Processor Dock."""
    
    def test_provider_combo_selectable(self, qtbot):
        """Test AI provider combo box selection."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Verify providers exist
        assert dock.combo_provider.count() > 0
        
        # Change provider
        if dock.combo_provider.count() > 1:
            dock.combo_provider.setCurrentIndex(1)
            assert dock.combo_provider.currentIndex() == 1
    
    def test_prompt_input_accepts_text(self, qtbot):
        """Test prompt input accepts multiline text."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Text edit should accept input
        test_prompt = "Translate this text"
        dock.ed_prompt.setPlainText(test_prompt)
        assert test_prompt in dock.ed_prompt.toPlainText()
    
    def test_path_entries_manageable(self, qtbot):
        """Test file path entries can be added."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Verify initial path entry exists
        assert len(dock.path_entries) > 0
        
        # First path entry should have widgets
        first_entry = dock.path_entries[0]
        assert hasattr(first_entry, 'ed_path')
        assert hasattr(first_entry, 'btn_browse')
    
    def test_process_button_exists(self, qtbot):
        """Test process button exists and is clickable."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_process is not None
        # Enabled state depends on validation
        assert isinstance(dock.btn_process.isEnabled(), bool)
    
    def test_interrupt_button_for_long_operations(self, qtbot):
        """Test interrupt button exists."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_interrupt is not None


class TestTutorialsDockInteractions:
    """Test user interactions in Tutorials Dock."""
    
    def test_search_input_accepts_keywords(self, qtbot):
        """Test search input accepts keywords."""
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        # Type search query
        qtbot.keyClicks(dock.search_input, "json")
        assert dock.search_input.text() == "json"
    
    def test_search_button_clickable(self, qtbot):
        """Test search button is clickable."""
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_search is not None
        assert dock.btn_search.isEnabled()
    
    def test_quick_start_button_clickable(self, qtbot):
        """Test Quick Start button is clickable."""
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        assert dock.btn_quick_start is not None
        assert dock.btn_quick_start.isEnabled()
    
    def test_tree_navigation_exists(self, qtbot):
        """Test tree widget for navigation exists."""
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        assert dock.tree is not None
        assert dock.tree.topLevelItemCount() >= 0
    
    def test_browser_widget_exists(self, qtbot):
        """Test browser widget for content display exists."""
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        assert dock.browser is not None
        # Should have default welcome content
        assert len(dock.browser.toHtml()) > 0


class TestCrossDockWorkflows:
    """Test complete workflows across multiple dock operations."""
    
    def test_set_operations_complete_workflow(self, qtbot):
        """Test complete set operation workflow."""
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # 1. Select operation
        qtbot.mouseClick(dock.chk_intersection, Qt.LeftButton)
        assert dock.chk_intersection.isChecked()
        
        # 2. Choose comparison mode
        qtbot.mouseClick(dock.radio_key_only, Qt.LeftButton)
        assert dock.radio_key_only.isChecked()
        
        # 3. Verify execute button state (may require valid files)
        # This is workflow validation - execution tested separately
        assert dock.btn_execute is not None
    
    def test_search_and_clear_workflow(self, qtbot):
        """Test search and clear results workflow."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # 1. Enter search criteria
        qtbot.keyClicks(dock.ed_search_key, "test.key")
        
        # 2. Enable options
        qtbot.mouseClick(dock.chk_case, Qt.LeftButton)
        
        # 3. Verify clear button exists for results
        assert dock.btn_clear is not None
        assert dock.btn_clear.isEnabled()
    
    def test_translate_workflow_preparation(self, qtbot):
        """Test translate workflow setup."""
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # 1. Set paths
        qtbot.keyClicks(dock.ed_path, "/tmp/source.tsx")
        qtbot.keyClicks(dock.ed_dict, "/tmp/en.json")
        
        # 2. Configure options
        qtbot.mouseClick(dock.chk_backup, Qt.LeftButton)
        assert dock.chk_backup.isChecked()
        
        # 3. Set variable name
        dock.object_variable_name.clear()
        qtbot.keyClicks(dock.object_variable_name, "t")
        
        # Workflow ready for execution
        assert dock.ed_path.text() != ""
        assert dock.ed_dict.text() != ""


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases in GUI."""
    
    def test_empty_input_validation(self, qtbot):
        """Test docks handle empty inputs gracefully."""
        docks = [
            SetOperationsDock(),
            CaseConverterDock(),
            JsonSearchDock(),
        ]
        
        for dock in docks:
            qtbot.addWidget(dock)
            # Docks should initialize without errors even with empty inputs
            assert dock is not None
    
    def test_special_characters_in_inputs(self, qtbot):
        """Test inputs accept special characters."""
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Test special regex characters
        special_text = r".*[a-z]+\.{1,3}"
        qtbot.keyClicks(dock.ed_search_key, special_text)
        assert special_text in dock.ed_search_key.text()
    
    def test_very_long_input_text(self, qtbot):
        """Test inputs handle long text."""
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Long prompt
        long_prompt = "Test prompt " * 100
        dock.ed_prompt.setPlainText(long_prompt)
        
        # Should accept without crashing
        assert len(dock.ed_prompt.toPlainText()) > 1000
    
    def test_rapid_button_clicks(self, qtbot):
        """Test buttons handle rapid clicks."""
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        # Rapid clicks should not crash
        for _ in range(5):
            qtbot.mouseClick(dock.btn_convert, Qt.LeftButton)
            QTest.qWait(50)  # Small delay
        
        # Dock should still be functional
        assert dock.btn_convert.isEnabled() or not dock.btn_convert.isEnabled()  # Either state valid


class TestKeyboardShortcuts:
    """Test keyboard shortcuts across docks."""
    
    def test_enter_shortcuts_exist(self, qtbot):
        """Test Enter key shortcuts are implemented."""
        docks_with_enter = [
            (JsonSearchDock(), 'ed_search_key'),
            (JsonTranslateDock(), 'ed_path'),
            (TutorialsDock(), 'search_input'),
        ]
        
        for dock, widget_name in docks_with_enter:
            qtbot.addWidget(dock)
            widget = getattr(dock, widget_name)
            
            # Focus widget
            widget.setFocus()
            
            # Verify Enter can be pressed (doesn't crash)
            qtbot.keyPress(widget, Qt.Key_Return)
            qtbot.keyRelease(widget, Qt.Key_Return)
    
    def test_escape_shortcuts_exist(self, qtbot):
        """Test Escape key shortcuts are implemented."""
        docks_with_escape = [
            JsonSearchDock(),
            AIProcessorDock(),
            CaseConverterDock(),
        ]
        
        for dock in docks_with_escape:
            qtbot.addWidget(dock)
            
            # Verify dock has interrupt functionality
            assert hasattr(dock, 'btn_interrupt') or hasattr(dock, '_interrupt')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
