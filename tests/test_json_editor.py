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

    def test_schema_completion_candidates_from_schema_text(self):
        """Test schema autocomplete candidates include nested properties."""
        from src.gui.json_editor_tab import JsonEditorTab

        schema_text = json.dumps({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "profile": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "roles": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"label": {"type": "string"}},
                            },
                        },
                    },
                },
            },
            "$defs": {
                "audit": {
                    "type": "object",
                    "properties": {"createdAt": {"type": "string"}},
                },
            },
        })

        success, candidates, message = (
            JsonEditorTab.schema_completion_candidates_from_schema_text(schema_text)
        )

        self.assertTrue(success)
        self.assertEqual(message, "")
        self.assertEqual(candidates, ["createdAt", "email", "label", "name", "profile", "roles"])

    def test_schema_completion_candidates_report_invalid_schema_json(self):
        """Test schema autocomplete candidate extraction reports schema parse errors."""
        from src.gui.json_editor_tab import JsonEditorTab

        success, candidates, message = (
            JsonEditorTab.schema_completion_candidates_from_schema_text('{"properties": }')
        )

        self.assertFalse(success)
        self.assertEqual(candidates, [])
        self.assertIn("Schema parse error", message)

    def test_schema_completion_rejects_too_large_schema_text(self):
        """Test schema autocomplete avoids parsing oversized schema text."""
        from src.gui.json_editor_tab import JsonEditorTab

        original_limit = JsonEditorTab.SCHEMA_COMPLETION_MAX_SCHEMA_CHARS
        JsonEditorTab.SCHEMA_COMPLETION_MAX_SCHEMA_CHARS = 10
        try:
            success, candidates, message = (
                JsonEditorTab.schema_completion_candidates_from_schema_text(
                    '{"type": "object"}'
                )
            )
        finally:
            JsonEditorTab.SCHEMA_COMPLETION_MAX_SCHEMA_CHARS = original_limit

        self.assertFalse(success)
        self.assertEqual(candidates, [])
        self.assertIn("too large", message)

    def test_schema_completion_candidate_extraction_is_bounded(self):
        """Test schema autocomplete caps candidate extraction."""
        from src.gui.json_editor_tab import JsonEditorTab

        original_limit = JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES
        JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES = 3
        try:
            schema_text = json.dumps({
                "type": "object",
                "properties": {
                    f"field_{index:02d}": {"type": "string"}
                    for index in range(10)
                },
            })
            success, candidates, message = (
                JsonEditorTab.schema_completion_candidates_from_schema_text(schema_text)
            )
        finally:
            JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES = original_limit

        self.assertTrue(success)
        self.assertEqual(candidates, ["field_00", "field_01", "field_02"])
        self.assertIn("limited to 3 candidates", message)

    def test_schema_completion_depth_is_bounded_without_recursion(self):
        """Test deep schemas are limited without recursive traversal."""
        from src.gui.json_editor_tab import JsonEditorTab

        schema = {"type": "object", "properties": {}}
        current = schema
        for index in range(10):
            child = {"type": "object", "properties": {}}
            current["properties"][f"level_{index}"] = child
            current = child

        original_depth = JsonEditorTab.SCHEMA_COMPLETION_MAX_DEPTH
        JsonEditorTab.SCHEMA_COMPLETION_MAX_DEPTH = 2
        try:
            success, candidates, message = (
                JsonEditorTab.schema_completion_candidates_from_schema_text(
                    json.dumps(schema)
                )
            )
        finally:
            JsonEditorTab.SCHEMA_COMPLETION_MAX_DEPTH = original_depth

        self.assertTrue(success)
        self.assertEqual(candidates, ["level_0", "level_1", "level_2"])
        self.assertIn("depth limit", message)

    def test_schema_completion_model_is_bounded(self):
        """Test direct candidate updates cannot overfill the completer model."""
        from src.gui.json_editor_tab import JsonEditorTab

        original_limit = JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES
        JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES = 2
        try:
            tab = JsonEditorTab()
            tab.set_schema_completion_candidates(["gamma", "alpha", "beta"])
        finally:
            JsonEditorTab.SCHEMA_COMPLETION_MAX_CANDIDATES = original_limit

        self.assertEqual(tab._schema_key_candidates, ["alpha", "gamma"])
        self.assertEqual(tab.schema_completion_model.rowCount(), 2)

    def test_schema_completion_inserts_inside_quoted_key(self):
        """Test schema completion replaces the current quoted key prefix."""
        from src.gui.json_editor_tab import JsonEditorTab

        tab = JsonEditorTab()
        tab.set_schema_completion_candidates(["email"])
        tab.editor.setPlainText('{\n  "em"\n}')
        cursor = tab.editor.textCursor()
        cursor.setPosition(tab.editor.toPlainText().find('"em"') + 3)
        tab.editor.setTextCursor(cursor)

        tab._insert_schema_completion("email")

        self.assertIn('"email"', tab.editor.toPlainText())

    def test_schema_completion_inserts_json_key_when_outside_quotes(self):
        """Test schema completion inserts a JSON key snippet outside quoted keys."""
        from src.gui.json_editor_tab import JsonEditorTab

        tab = JsonEditorTab()
        tab.set_schema_completion_candidates(["profile"])
        tab.editor.setPlainText("{\n  \n}")
        cursor = tab.editor.textCursor()
        cursor.setPosition(tab.editor.toPlainText().find("\n  ") + 3)
        tab.editor.setTextCursor(cursor)

        tab._insert_schema_completion("profile")

        self.assertIn('"profile": ', tab.editor.toPlainText())


if __name__ == '__main__':
    unittest.main()
