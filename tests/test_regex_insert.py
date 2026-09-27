#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for MemoryRegister and RegexInsertPanel (v2.9.111)

Tests memory register system and regex insert integration.
"""

import pytest
import re
from datetime import datetime

from src.core.memory_register import MemoryRegister, RegisterEntry, get_global_register


class TestMemoryRegister:
    """Tests for MemoryRegister core system."""
    
    def test_initialization(self):
        """Test register initialization."""
        register = MemoryRegister()
        assert register.max_registers == 100
        assert len(register.registers) == 0
        assert len(register.history) == 0
    
    def test_capture_simple(self):
        """Test simple regex capture."""
        register = MemoryRegister()
        text = '{"name": "John Doe"}'
        pattern = r'"name": "(.*?)"'
        
        num, values = register.capture(text, pattern)
        
        assert num == 2  # $0 (whole match) + $1 (group)
        assert values[0] == '"name": "John Doe"'  # $0
        assert values[1] == "John Doe"  # $1
        assert register.get(0) == '"name": "John Doe"'
        assert register.get(1) == "John Doe"
    
    def test_capture_multiple_groups(self):
        """Test capture with multiple groups."""
        register = MemoryRegister()
        text = '{"email": "john@example.com"}'
        pattern = r'"email": "(.*?)@(.*?)"'
        
        num, values = register.capture(text, pattern)
        
        assert num == 3  # $0 + $1 + $2
        assert register.get(1) == "john"
        assert register.get(2) == "example.com"
    
    def test_capture_no_match(self):
        """Test capture with no matches."""
        register = MemoryRegister()
        text = '{"name": "John"}'
        pattern = r'"age": (\d+)'
        
        num, values = register.capture(text, pattern)
        
        assert num == 0
        assert len(values) == 0
    
    def test_capture_invalid_pattern(self):
        """Test capture with invalid regex."""
        register = MemoryRegister()
        text = '{"name": "John"}'
        pattern = r'['  # Invalid regex
        
        with pytest.raises(re.error):
            register.capture(text, pattern)
    
    def test_replace_in_text(self):
        """Test replace_in_text with placeholders."""
        register = MemoryRegister()
        text = '{"name": "John Doe", "age": 30}'
        pattern = r'"name": "(.*?)"'
        
        register.capture(text, pattern)
        
        template = '"fullName": "$1"'
        result = register.replace_in_text(template)
        
        assert result == '"fullName": "John Doe"'
    
    def test_replace_multiple_placeholders(self):
        """Test replace with multiple placeholders."""
        register = MemoryRegister()
        text = '{"email": "john@example.com"}'
        pattern = r'"email": "(.*?)@(.*?)"'
        
        register.capture(text, pattern)
        
        template = '"username": "$1", "domain": "$2"'
        result = register.replace_in_text(template)
        
        assert '"username": "john"' in result
        assert '"domain": "example.com"' in result
    
    def test_get_with_default(self):
        """Test get with default value."""
        register = MemoryRegister()
        
        assert register.get(5, "default") == "default"
    
    def test_get_all(self):
        """Test get_all registers."""
        register = MemoryRegister()
        text = '{"name": "John"}'
        pattern = r'"name": "(.*?)"'
        
        register.capture(text, pattern)
        all_regs = register.get_all()
        
        assert 0 in all_regs
        assert 1 in all_regs
        assert len(all_regs) == 2
    
    def test_clear(self):
        """Test clear registers."""
        register = MemoryRegister()
        text = '{"name": "John"}'
        pattern = r'"name": "(.*?)"'
        
        register.capture(text, pattern)
        assert register.has_registers()
        
        register.clear()
        assert not register.has_registers()
    
    def test_history(self):
        """Test history storage."""
        register = MemoryRegister()
        text1 = '{"name": "John"}'
        pattern1 = r'"name": "(.*?)"'
        
        register.capture(text1, pattern1)
        assert register.get_history_count() == 1
        
        text2 = '{"age": 30}'
        pattern2 = r'"age": (\d+)'
        
        register.capture(text2, pattern2)
        assert register.get_history_count() == 2
    
    def test_export_import(self):
        """Test export/import registers."""
        register = MemoryRegister()
        text = '{"name": "John"}'
        pattern = r'"name": "(.*?)"'
        
        register.capture(text, pattern)
        exported = register.export_to_dict()
        
        # Create new register and import
        new_register = MemoryRegister()
        new_register.import_from_dict(exported)
        
        assert new_register.get(1) == "John"
        assert new_register.last_pattern == pattern
    
    def test_global_register(self):
        """Test global register singleton."""
        reg1 = get_global_register()
        reg2 = get_global_register()
        
        assert reg1 is reg2  # Same instance


class TestRegexInsertPanel:
    """Tests for RegexInsertPanel GUI component."""
    
    def test_panel_initialization(self, qapp):
        """Test panel initializes correctly."""
        from src.gui.panels import RegexInsertPanel
        
        panel = RegexInsertPanel()
        assert panel.ed_pattern is not None
        assert panel.table_registers is not None
        assert panel.ed_target_key is not None
        assert panel.ed_new_key is not None
        assert panel.ed_new_value is not None
        assert panel.combo_position is not None
        panel.deleteLater()
    
    def test_capture_updates_table(self, qapp, monkeypatch):
        """Test capture updates register table."""
        from src.gui.panels import RegexInsertPanel
        from PySide6.QtWidgets import QMessageBox
        
        # Mock QMessageBox to avoid blocking
        monkeypatch.setattr(QMessageBox, 'information', lambda *args, **kwargs: None)
        
        panel = RegexInsertPanel()
        panel.set_source_text('{"name": "John"}')
        panel.ed_pattern.setText(r'"name": "(.*?)"')
        
        panel._execute_capture()
        
        assert panel.table_registers.rowCount() == 2  # $0 and $1
        panel.deleteLater()
    
    def test_insert_signal(self, qapp, qtbot):
        """Test insert_requested signal emission."""
        from src.gui.panels import RegexInsertPanel
        
        panel = RegexInsertPanel()
        panel.set_source_text('{"name": "John"}')
        panel.ed_pattern.setText(r'"name": "(.*?)"')
        panel._execute_capture()
        
        # Set insert fields
        panel.ed_target_key.setText("user")
        panel.ed_new_key.setText("fullName")
        panel.ed_new_value.setText("$1")
        
        signal_received = []
        
        def on_insert(target, new_key, new_value, position):
            signal_received.append((target, new_key, new_value, position))
        
        panel.insert_requested.connect(on_insert)
        
        with qtbot.waitSignal(panel.insert_requested, timeout=1000):
            panel.btn_insert.click()
        
        assert len(signal_received) == 1
        target, new_key, new_value, position = signal_received[0]
        assert target == "user"
        assert new_key == "fullName"
        assert new_value == "John"  # $1 replaced
        
        panel.deleteLater()


class TestJSONEditorIntegration:
    """Tests for regex insert integration in JSON Editor."""
    
    def test_json_editor_has_regex_panel(self, qapp):
        """Test JSON Editor has regex insert panel."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        assert hasattr(editor, 'regex_insert_panel')
        assert hasattr(editor, 'btn_regex_insert')
        editor.deleteLater()
    
    def test_toggle_regex_panel(self, qapp):
        """Test toggling regex panel visibility."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        editor.show()
        
        # Initially hidden
        assert not editor.regex_insert_panel.isVisible()
        
        # Toggle visible
        editor._toggle_regex_insert_panel()
        assert editor.regex_insert_panel.isVisible()
        
        # Toggle hidden
        editor._toggle_regex_insert_panel()
        assert not editor.regex_insert_panel.isVisible()
        
        editor.deleteLater()
    
    def test_find_key_in_json(self, qapp):
        """Test finding key in JSON structure."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        json_obj = {
            "user": {
                "name": "John",
                "email": "john@example.com"
            }
        }
        
        found, path = editor._find_key_in_json(json_obj, "name")
        assert found == True
        assert path == ["user", "name"]
        
        found, path = editor._find_key_in_json(json_obj, "notfound")
        assert found == False
        
        editor.deleteLater()
    
    def test_parse_value(self, qapp):
        """Test value parsing to correct types."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        editor = JsonEditorTab()
        
        # String
        assert editor._parse_value("hello") == "hello"
        
        # Number
        assert editor._parse_value("42") == 42
        assert editor._parse_value("3.14") == 3.14
        
        # Boolean
        assert editor._parse_value("true") == True
        assert editor._parse_value("false") == False
        
        # Null
        assert editor._parse_value("null") is None
        
        # JSON object
        result = editor._parse_value('{"key": "value"}')
        assert isinstance(result, dict)
        assert result["key"] == "value"
        
        editor.deleteLater()


@pytest.fixture
def qapp():
    """Qt Application fixture."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture(autouse=True)
def dismiss_feedback_dialogs(monkeypatch):
    """Feedback dialogs must not block automated insert tests."""
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
