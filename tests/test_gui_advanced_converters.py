"""
Integration Tests for GUI Advanced Converters (BSON/TOON)

Tests the integration of professional BSON/TOON converters into the
Format Converter GUI through json_output_converter.py

Author: Programmer #3
Date: 2026-02-16
Protocol: SIMPLICITY_PROTOCOL_3
Phase: 3 of 3 (GUI Integration Testing)
"""

import pytest
import json
import base64
from src.converters.json_output_converter import convert_json_to_format


class TestBsonIntegration:
    """Test BSON conversion through json_output_converter."""
    
    def test_bson_simple_object(self):
        """Test BSON conversion of simple object."""
        data = {"name": "Alice", "age": 30}
        result = convert_json_to_format(data, "BSON")
        
        # Should return base64 string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should be valid base64
        try:
            decoded = base64.b64decode(result)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")
    
    def test_bson_with_array(self):
        """Test BSON conversion with array."""
        data = {"items": [1, 2, 3], "user": "test"}
        result = convert_json_to_format(data, "BSON")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_bson_nested_structure(self):
        """Test BSON with nested objects."""
        data = {
            "user": {
                "name": "Bob",
                "profile": {"age": 25}
            }
        }
        result = convert_json_to_format(data, "BSON")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_bson_from_json_string(self):
        """Test BSON conversion from JSON string."""
        json_str = '{"test": "value"}'
        result = convert_json_to_format(json_str, "BSON")
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestToonIntegration:
    """Test TOON conversion through json_output_converter."""
    
    def test_toon_simple_object(self):
        """Test TOON conversion of simple object."""
        data = {"name": "Alice", "age": 30}
        result = convert_json_to_format(data, "TOON")
        
        assert "name: Alice" in result
        assert "age: 30" in result
    
    def test_toon_with_array(self):
        """Test TOON conversion with array."""
        data = {"tags": ["python", "coding", "llm"]}
        result = convert_json_to_format(data, "TOON")
        
        assert "tags" in result
        assert "python" in result or "[3]" in result
    
    def test_toon_nested_structure(self):
        """Test TOON with nested objects."""
        data = {
            "user": {
                "name": "Bob",
                "age": 25
            }
        }
        result = convert_json_to_format(data, "TOON")
        
        assert "user" in result
        assert "Bob" in result
    
    def test_toon_from_json_string(self):
        """Test TOON conversion from JSON string."""
        json_str = '{"test": "value", "count": 42}'
        result = convert_json_to_format(json_str, "TOON")
        
        assert "test: value" in result
        assert "count: 42" in result


class TestFormatFallback:
    """Test graceful handling of missing dependencies."""
    
    def test_json_fallback_works(self):
        """Test that JSON always works as fallback."""
        data = {"name": "Test"}
        
        # JSON should always work
        result = convert_json_to_format(data, "JSON")
        assert '"name"' in result
        assert '"Test"' in result
    
    def test_unrecognized_format_defaults_to_json(self):
        """Test that unknown formats default to JSON."""
        data = {"test": "value"}
        result = convert_json_to_format(data, "UNKNOWN_FORMAT")
        
        # Should return JSON
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data


class TestFormatNameNormalization:
    """Test case-insensitive format name handling."""
    
    def test_bson_case_insensitive(self):
        """Test BSON with various cases."""
        data = {"test": 1}
        
        result1 = convert_json_to_format(data, "BSON")
        result2 = convert_json_to_format(data, "bson")
        result3 = convert_json_to_format(data, "Bson")
        
        # All should produce valid base64
        assert len(result1) > 0
        assert len(result2) > 0
        assert len(result3) > 0
    
    def test_toon_case_insensitive(self):
        """Test TOON with various cases."""
        data = {"test": 1}
        
        result1 = convert_json_to_format(data, "TOON")
        result2 = convert_json_to_format(data, "toon")
        result3 = convert_json_to_format(data, "Toon")
        
        # All should produce valid TOON
        assert "test" in result1
        assert "test" in result2
        assert "test" in result3


class TestRoundtrip:
    """Test that conversions are reversible where possible."""
    
    def test_json_toon_readable(self):
        """Test that TOON output is human-readable."""
        data = {
            "name": "Alice",
            "age": 30,
            "active": True
        }
        
        toon_result = convert_json_to_format(data, "TOON")
        
        # TOON should be readable (key: value format)
        lines = toon_result.split('\n')
        assert len(lines) >= 3
        
        # Each line should have key-value structure
        for line in lines:
            if line.strip():
                assert ':' in line or '[' in line


class TestErrorHandling:
    """Test error handling for edge cases."""
    
    def test_empty_dict(self):
        """Test conversion of empty dictionary."""
        data = {}
        
        bson_result = convert_json_to_format(data, "BSON")
        assert isinstance(bson_result, str)
        
        toon_result = convert_json_to_format(data, "TOON")
        assert isinstance(toon_result, str)
    
    def test_empty_list(self):
        """Test conversion of empty list."""
        data = []
        
        bson_result = convert_json_to_format(data, "BSON")
        assert isinstance(bson_result, str)
        
        toon_result = convert_json_to_format(data, "TOON")
        assert isinstance(toon_result, str)
    
    def test_none_values(self):
        """Test handling of None values."""
        data = {"key": None}
        
        bson_result = convert_json_to_format(data, "BSON")
        assert isinstance(bson_result, str)
        
        toon_result = convert_json_to_format(data, "TOON")
        assert isinstance(toon_result, str)
        assert "null" in toon_result.lower()


# Run specific test with: pytest tests/test_gui_advanced_converters.py -v -k test_bson_simple
# Run all BSON tests: pytest tests/test_gui_advanced_converters.py -v -k Bson
# Run all TOON tests: pytest tests/test_gui_advanced_converters.py -v -k Toon
# Run all tests: pytest tests/test_gui_advanced_converters.py -v
