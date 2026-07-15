#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for JsonValidator and JsonEditorTab.

Tests:
- JsonValidator: validation, format, minify
- JsonEditorTab: load, save, validation, tree building, search
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gui.json_validator import JsonValidator, ValidationResult, ValidatorFactory


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult value object."""
    
    def test_valid_result(self):
        """Test valid JSON result."""
        result = ValidationResult(True)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_msg, "")
        self.assertEqual(result.line, -1)
        self.assertEqual(result.col, -1)
    
    def test_invalid_result(self):
        """Test invalid JSON result."""
        result = ValidationResult(False, "Unexpected token", 5, 12)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_msg, "Unexpected token")
        self.assertEqual(result.line, 5)
        self.assertEqual(result.col, 12)


class TestJsonValidator(unittest.TestCase):
    """Test JsonValidator class."""
    
    def setUp(self):
        """Setup validator instance."""
        self.validator = JsonValidator()
    
    def test_validate_valid_json(self):
        """Test validation of valid JSON."""
        valid_json = '{"name": "John", "age": 30, "active": true}'
        result = self.validator.validate(valid_json)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.error_msg, "")
    
    def test_validate_invalid_json_missing_comma(self):
        """Test validation of invalid JSON (missing comma)."""
        invalid_json = '{"name": "John" "age": 30}'
        result = self.validator.validate(invalid_json)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(result.line, 0)
        self.assertGreater(result.col, 0)
    
    def test_validate_invalid_json_trailing_comma(self):
        """Test validation of invalid JSON (trailing comma)."""
        invalid_json = '{"name": "John", "age": 30,}'
        result = self.validator.validate(invalid_json)
        
        self.assertFalse(result.is_valid)
    
    def test_validate_empty_string(self):
        """Test validation of empty string."""
        result = self.validator.validate("")
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_msg, "Empty JSON")
    
    def test_validate_complex_json(self):
        """Test validation of complex nested JSON."""
        complex_json = '''
        {
            "users": [
                {"name": "Alice", "roles": ["admin", "user"]},
                {"name": "Bob", "roles": ["user"]}
            ],
            "settings": {
                "theme": "dark",
                "notifications": true
            }
        }
        '''
        result = self.validator.validate(complex_json)
        
        self.assertTrue(result.is_valid)
    
    def test_format_json_2_spaces(self):
        """Test formatting JSON with 2 spaces indentation."""
        minified = '{"name":"John","age":30}'
        success, formatted = self.validator.format_json(minified, indent=2)
        
        self.assertTrue(success)
        self.assertIn('\n', formatted)
        self.assertIn('  "name"', formatted)
    
    def test_format_json_4_spaces(self):
        """Test formatting JSON with 4 spaces indentation."""
        minified = '{"name":"John","age":30}'
        success, formatted = self.validator.format_json(minified, indent=4)
        
        self.assertTrue(success)
        self.assertIn('\n', formatted)
        self.assertIn('    "name"', formatted)
    
    def test_format_invalid_json(self):
        """Test formatting invalid JSON."""
        invalid = '{"name": "John" "age": 30}'
        success, error = self.validator.format_json(invalid)
        
        self.assertFalse(success)
        self.assertIn("Invalid JSON", error)
    
    def test_minify_json(self):
        """Test minifying JSON."""
        formatted = '''
        {
            "name": "John",
            "age": 30
        }
        '''
        success, minified = self.validator.minify_json(formatted)
        
        self.assertTrue(success)
        self.assertNotIn('\n', minified)
        self.assertEqual(minified, '{"name":"John","age":30}')
    
    def test_minify_invalid_json(self):
        """Test minifying invalid JSON."""
        invalid = '{"name": "John" "age": 30}'
        success, error = self.validator.minify_json(invalid)
        
        self.assertFalse(success)
        self.assertIn("Invalid JSON", error)


class TestValidatorFactory(unittest.TestCase):
    """Test ValidatorFactory class."""
    
    def test_create_json_validator(self):
        """Test creating JSON validator."""
        validator = ValidatorFactory.create_validator('json')
        
        self.assertIsNotNone(validator)
        self.assertIsInstance(validator, JsonValidator)
    
    def test_create_json_validator_with_dot(self):
        """Test creating JSON validator with dot prefix."""
        validator = ValidatorFactory.create_validator('.json')
        
        self.assertIsNotNone(validator)
        self.assertIsInstance(validator, JsonValidator)
    
    def test_create_unsupported_validator(self):
        """Test creating unsupported validator type."""
        validator = ValidatorFactory.create_validator('xml')
        
        self.assertIsNone(validator)


class TestJsonEditorTabIntegration(unittest.TestCase):
    """Integration tests for JsonEditorTab (require Qt)."""
    
    @classmethod
    def setUpClass(cls):
        """Setup Qt application."""
        try:
            from PySide6.QtWidgets import QApplication
            import sys
            cls.app = QApplication.instance()
            if cls.app is None:
                cls.app = QApplication(sys.argv)
        except ImportError:
            raise unittest.SkipTest("PySide6 not available")
    
    def test_load_valid_json_file(self):
        """Test loading valid JSON file."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "Test", "value": 123}, f)
            temp_path = f.name
        
        try:
            tab = JsonEditorTab()
            success = tab.load_file(temp_path)
            
            self.assertTrue(success)
            self.assertEqual(tab.file_path, temp_path)
            self.assertFalse(tab.is_modified)
        finally:
            os.unlink(temp_path)
    
    def test_save_valid_json_file(self):
        """Test saving valid JSON file."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        # Create temporary file path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            tab = JsonEditorTab()
            tab.editor.setPlainText('{"name": "Test", "value": 456}')
            
            success, error_msg = tab.save_file(temp_path)
            
            self.assertTrue(success)
            self.assertEqual(error_msg, "")
            self.assertFalse(tab.is_modified)
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
                data = json.loads(content)
                self.assertEqual(data["name"], "Test")
                self.assertEqual(data["value"], 456)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_validation_state_changes(self):
        """Test validation state changes on text edit."""
        from src.gui.json_editor_tab import JsonEditorTab
        
        tab = JsonEditorTab()
        
        # Valid JSON
        tab.editor.setPlainText('{"valid": true}')
        tab._validate()
        
        self.assertIn("✓ Valid JSON", tab.lbl_validation.text())
        
        # Invalid JSON
        tab.editor.setPlainText('{"invalid": true')
        tab._validate()
        
        self.assertIn("✗ Invalid JSON", tab.lbl_validation.text())

    def test_invalid_json_creates_visual_diagnostic(self):
        """Test invalid JSON adds editor diagnostic selections."""
        from src.gui.json_editor_tab import JsonEditorTab

        tab = JsonEditorTab()
        tab.editor.setPlainText('{\n  "invalid": \n}')
        tab._validate()

        self.assertIn("✗ Invalid JSON", tab.lbl_validation.text())
        self.assertGreaterEqual(len(tab.editor.extraSelections()), 2)

    def test_valid_json_clears_visual_diagnostic(self):
        """Test valid JSON clears existing diagnostic selections."""
        from src.gui.json_editor_tab import JsonEditorTab

        tab = JsonEditorTab()
        tab.show_diagnostic(1, 1, "Synthetic error")
        self.assertGreaterEqual(len(tab.editor.extraSelections()), 1)

        tab.editor.setPlainText('{"valid": true}')
        tab._validate()

        self.assertIn("✓ Valid JSON", tab.lbl_validation.text())
        self.assertEqual(len(tab.editor.extraSelections()), 0)

    def test_schema_diagnostic_highlights_json_path(self):
        """Test schema diagnostics highlight the best matching JSON key."""
        from src.gui.json_editor_tab import JsonEditorTab

        tab = JsonEditorTab()
        tab.editor.setPlainText('{\n  "age": "old"\n}')
        tab.show_schema_diagnostic("$.age: 'old' is not of type 'integer'", ("age",))

        self.assertIn("✗ Schema error", tab.lbl_validation.text())
        self.assertGreaterEqual(len(tab.editor.extraSelections()), 2)
        self.assertTrue(
            any(
                '"age"' in selection.cursor.selectedText()
                for selection in tab.editor.extraSelections()
            )
        )


if __name__ == '__main__':
    unittest.main()
