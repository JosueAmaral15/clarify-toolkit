#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for SearchReplacePanel and InsertPanel (v2.9.110)

Tests panels independently and their integration with docks.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSettings

from src.gui.panels import SearchReplacePanel, InsertPanel
from src.core.search_replace import SearchOptions
from src.core.insert import InsertMode


@pytest.fixture
def qapp():
    """Qt Application fixture."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def search_replace_panel(qapp):
    """SearchReplacePanel fixture."""
    panel = SearchReplacePanel()
    yield panel
    panel.deleteLater()


@pytest.fixture
def insert_panel(qapp):
    """InsertPanel fixture."""
    panel = InsertPanel()
    yield panel
    panel.deleteLater()


class TestSearchReplacePanel:
    """Tests for SearchReplacePanel component."""
    
    def test_panel_initialization(self, search_replace_panel):
        """Test panel initializes correctly."""
        assert search_replace_panel.ed_needle is not None
        assert search_replace_panel.ed_replacement is not None
        assert search_replace_panel.chk_case_sensitive is not None
        assert search_replace_panel.chk_whole_word is not None
        assert search_replace_panel.chk_regex is not None
        assert search_replace_panel.chk_preserve_case is not None
        assert search_replace_panel.spin_count is not None
    
    def test_get_options(self, search_replace_panel):
        """Test getting SearchOptions."""
        search_replace_panel.chk_case_sensitive.setChecked(True)
        search_replace_panel.chk_whole_word.setChecked(True)
        search_replace_panel.chk_regex.setChecked(False)
        
        options = search_replace_panel.get_options()
        assert options.case_sensitive == True
        assert options.whole_word == True
        assert options.regex == False
    
    def test_set_get_needle(self, search_replace_panel):
        """Test setting and getting needle text."""
        search_replace_panel.set_needle("test")
        assert search_replace_panel.get_needle() == "test"
    
    def test_set_get_replacement(self, search_replace_panel):
        """Test setting and getting replacement text."""
        search_replace_panel.set_replacement("replaced")
        assert search_replace_panel.get_replacement() == "replaced"
    
    def test_replace_requested_signal(self, search_replace_panel, qtbot):
        """Test replace_requested signal emission."""
        signal_received = []
        
        def on_replace(file_name_query, file_content_query, replacement, options, preserve_case, count):
            signal_received.append((file_name_query, file_content_query, replacement, options, preserve_case, count))
        
        search_replace_panel.replace_requested.connect(on_replace)
        search_replace_panel.set_file_content_query("foo")
        search_replace_panel.set_replacement("bar")
        
        # Simulate button click
        with qtbot.waitSignal(search_replace_panel.replace_requested, timeout=1000):
            search_replace_panel.btn_replace.click()
        
        assert len(signal_received) == 1
        file_name_query, file_content_query, replacement, options, preserve_case, count = signal_received[0]
        assert file_content_query == "foo"
        assert replacement == "bar"
        assert isinstance(options, SearchOptions)
    
    def test_clear_inputs(self, search_replace_panel):
        """Test clearing input fields."""
        search_replace_panel.set_file_name_query("test")
        search_replace_panel.set_file_content_query("foo")
        search_replace_panel.set_replacement("replaced")
        search_replace_panel.clear_inputs()
        
        assert search_replace_panel.get_file_name_query() == ""
        assert search_replace_panel.get_file_content_query() == ""
        assert search_replace_panel.get_replacement() == ""


class TestInsertPanel:
    """Tests for InsertPanel component."""
    
    def test_panel_initialization(self, insert_panel):
        """Test panel initializes correctly."""
        assert insert_panel.spin_line is not None
        assert insert_panel.combo_mode is not None
        assert insert_panel.text_insert is not None
        assert insert_panel.btn_insert is not None
        assert insert_panel.btn_left is not None
        assert insert_panel.btn_right is not None
        assert insert_panel.btn_replace is not None
    
    def test_get_set_line_number(self, insert_panel):
        """Test getting and setting line number."""
        insert_panel.set_line_number(10)
        assert insert_panel.get_line_number() == 10
    
    def test_get_set_text(self, insert_panel):
        """Test getting and setting insertion text."""
        insert_panel.set_text("inserted text")
        assert insert_panel.get_text() == "inserted text"
    
    def test_get_set_mode(self, insert_panel):
        """Test getting and setting insertion mode."""
        insert_panel.set_mode(InsertMode.RIGHT)
        assert insert_panel.get_mode() == InsertMode.RIGHT
    
    def test_insert_requested_signal(self, insert_panel, qtbot):
        """Test insert_requested signal emission."""
        signal_received = []
        
        def on_insert(line_no, text, mode):
            signal_received.append((line_no, text, mode))
        
        insert_panel.insert_requested.connect(on_insert)
        insert_panel.set_line_number(5)
        insert_panel.set_text("test")
        insert_panel.set_mode(InsertMode.REPLACE)
        
        # Simulate button click
        with qtbot.waitSignal(insert_panel.insert_requested, timeout=1000):
            insert_panel.btn_insert.click()
        
        assert len(signal_received) == 1
        line_no, text, mode = signal_received[0]
        assert line_no == 5
        assert text == "test"
        assert mode == InsertMode.REPLACE
    
    def test_clear_text(self, insert_panel):
        """Test clearing text input."""
        insert_panel.set_text("test")
        insert_panel.clear_text()
        assert insert_panel.get_text() == ""


class TestAIProcessorIntegration:
    """Tests for panel integration in AI Processor Dock."""
    
    def test_ai_processor_has_panels(self, qapp):
        """Test AI Processor Dock has both panels."""
        from src.gui.ai_processor_dock import AIProcessorDock
        
        dock = AIProcessorDock()
        assert hasattr(dock, 'search_replace_panel')
        assert hasattr(dock, 'insert_panel')
        assert isinstance(dock.search_replace_panel, SearchReplacePanel)
        assert isinstance(dock.insert_panel, InsertPanel)
        dock.deleteLater()
    
    def test_ai_processor_signals_connected(self, qapp):
        """Test signals are connected in AI Processor."""
        from src.gui.ai_processor_dock import AIProcessorDock
        
        dock = AIProcessorDock()
        assert dock.search_replace_panel.receivers(
            dock.search_replace_panel.replace_requested
        ) > 0
        assert dock.insert_panel.receivers(
            dock.insert_panel.insert_requested
        ) > 0
        dock.deleteLater()


class TestJSONEditorIntegration:
    """Tests for InsertPanel integration in JSON Editor."""
    
    def test_json_editor_has_insert_panel(self, qapp):
        """Test JSON Editor has insert panel."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        assert hasattr(editor, 'insert_panel')
        assert isinstance(editor.insert_panel, InsertPanel)
        assert hasattr(editor, 'btn_insert_panel')
        editor.deleteLater()
    
    def test_json_editor_signal_connected(self, qapp):
        """Test insert signal is connected in JSON Editor."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        assert editor.insert_panel.receivers(
            editor.insert_panel.insert_requested
        ) > 0
        editor.deleteLater()
    
    def test_json_editor_toggle_panel(self, qapp):
        """Test toggling insert panel visibility."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        
        # Initially hidden
        assert not editor.insert_panel.isVisible()
        
        # Toggle visible
        editor._toggle_insert_panel()
        assert editor.insert_panel.isVisible()
        
        # Toggle hidden
        editor._toggle_insert_panel()
        assert not editor.insert_panel.isVisible()
        
        editor.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
