#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for text_to_json module (Task #49 - v2.9.24)

Tests cover:
- Format detection (10 formats)
- Key-value conversion
- List conversion
- CSV conversion (with options)
- Python dict conversion
- YAML conversion
- INI conversion
- TOML conversion
- Java Properties conversion
- TOON conversion
- Type inference
- Edge cases
- Integration scenarios
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from text_to_json import (
    detect_format, parse_value,
    convert_key_value_to_json, convert_list_to_json,
    convert_csv_to_json, convert_python_dict_to_json,
    convert_yaml_to_json, convert_ini_to_json,
    convert_toml_to_json, convert_java_properties_to_json,
    convert_toon_to_json, convert_text_to_json
)


class TestDetectFormat:
    """Test format detection."""
    
    def test_detect_python_dict(self):
        """Detect Python dict literal."""
        text = "{'name': 'John', 'age': 30}"
        assert detect_format(text) == 'python_dict'
    
    def test_detect_python_list(self):
        """Detect Python list literal."""
        text = "['apple', 'banana', 'orange']"
        assert detect_format(text) == 'python_dict'
    
    def test_detect_toon_inline_array(self):
        """Detect TOON inline array format."""
        text = "tags[3]: python,coding,llm"
        assert detect_format(text) == 'toon'
    
    def test_detect_toon_root_array(self):
        """Detect TOON root array format."""
        text = "[3]: apple,banana,orange"
        assert detect_format(text) == 'toon'
    
    def test_detect_ini(self):
        """Detect INI format."""
        text = "[section]\nkey=value"
        assert detect_format(text) == 'ini'
    
    def test_detect_csv(self):
        """Detect CSV format."""
        text = "name,age,city\nJohn,30,NYC"
        assert detect_format(text) == 'csv'
    
    def test_detect_list(self):
        """Detect bullet list format."""
        text = "- Item 1\n- Item 2\n- Item 3"
        assert detect_format(text) == 'list'
    
    def test_detect_yaml_with_indentation(self):
        """Detect YAML format (indentation)."""
        text = "user:\n  name: John\n  age: 30"
        assert detect_format(text) == 'yaml'
    
    def test_detect_java_properties(self):
        """Detect Java Properties format."""
        text = "user.name=John\nuser.age=30\napp.theme=dark"
        assert detect_format(text) == 'java_properties'
    
    def test_detect_key_value_fallback(self):
        """Detect key-value pairs (fallback)."""
        text = "name: John\nage: 30"
        result = detect_format(text)
        assert result in ('key_value', 'yaml')  # Could be either


class TestParseValue:
    """Test value parsing with type inference."""
    
    def test_parse_integer(self):
        """Parse integer value."""
        assert parse_value("42", infer_types=True) == 42
        assert parse_value("0", infer_types=True) == 0
        assert parse_value("-100", infer_types=True) == -100
    
    def test_parse_float(self):
        """Parse float value."""
        assert parse_value("3.14", infer_types=True) == 3.14
        assert parse_value("0.5", infer_types=True) == 0.5
        assert parse_value("-10.75", infer_types=True) == -10.75
    
    def test_parse_boolean(self):
        """Parse boolean values."""
        assert parse_value("true", infer_types=True) is True
        assert parse_value("false", infer_types=True) is False
        assert parse_value("yes", infer_types=True) is True
        assert parse_value("no", infer_types=True) is False
    
    def test_parse_null(self):
        """Parse null values."""
        assert parse_value("null", infer_types=True) is None
        assert parse_value("none", infer_types=True) is None
        assert parse_value("", infer_types=True) is None
    
    def test_parse_string_no_inference(self):
        """Parse as string when inference disabled."""
        assert parse_value("42", infer_types=False) == "42"
        assert parse_value("true", infer_types=False) == "true"
        assert parse_value("null", infer_types=False) == "null"
    
    def test_parse_string_with_spaces(self):
        """Parse string with spaces."""
        assert parse_value("  hello world  ", infer_types=True) == "hello world"


class TestConvertKeyValue:
    """Test key-value conversion."""
    
    def test_simple_key_value_colon(self):
        """Convert simple key: value pairs."""
        text = "name: John\nage: 30\ncity: NYC"
        result = convert_key_value_to_json(text, infer_types=True)
        assert result == {'name': 'John', 'age': 30, 'city': 'NYC'}
    
    def test_simple_key_value_equals(self):
        """Convert simple key=value pairs."""
        text = "name=John\nage=30\ncity=NYC"
        result = convert_key_value_to_json(text, infer_types=True)
        assert result == {'name': 'John', 'age': 30, 'city': 'NYC'}
    
    def test_key_value_with_types(self):
        """Convert with type inference."""
        text = "count: 42\nprice: 19.99\nactive: true\nvalue: null"
        result = convert_key_value_to_json(text, infer_types=True)
        assert result == {'count': 42, 'price': 19.99, 'active': True, 'value': None}
    
    def test_key_value_skip_comments(self):
        """Skip comments in key-value."""
        text = "name: John\n# This is a comment\nage: 30"
        result = convert_key_value_to_json(text, infer_types=True)
        assert result == {'name': 'John', 'age': 30}


class TestConvertList:
    """Test list conversion."""
    
    def test_simple_list_dash(self):
        """Convert list with - prefix."""
        text = "- Apple\n- Banana\n- Orange"
        result = convert_list_to_json(text, infer_types=True)
        assert result == ['Apple', 'Banana', 'Orange']
    
    def test_simple_list_asterisk(self):
        """Convert list with * prefix."""
        text = "* Item 1\n* Item 2\n* Item 3"
        result = convert_list_to_json(text, infer_types=True)
        assert result == ['Item 1', 'Item 2', 'Item 3']
    
    def test_list_with_type_inference(self):
        """Convert list with type inference."""
        text = "- 42\n- 3.14\n- true\n- null"
        result = convert_list_to_json(text, infer_types=True)
        assert result == [42, 3.14, True, None]
    
    def test_list_empty_lines(self):
        """Convert list skipping empty lines."""
        text = "- Item 1\n\n- Item 2\n\n- Item 3"
        result = convert_list_to_json(text, infer_types=True)
        assert result == ['Item 1', 'Item 2', 'Item 3']


class TestConvertCSV:
    """Test CSV conversion."""
    
    def test_csv_with_header_objects(self):
        """Convert CSV to array of objects."""
        text = "name,age,city\nJohn,30,NYC\nAlice,25,LA"
        result = convert_csv_to_json(text, has_header=True, infer_types=True, array_of_objects=True)
        assert len(result) == 2
        assert result[0] == {'name': 'John', 'age': 30, 'city': 'NYC'}
        assert result[1] == {'name': 'Alice', 'age': 25, 'city': 'LA'}
    
    def test_csv_no_header_arrays(self):
        """Convert CSV to array of arrays."""
        text = "John,30,NYC\nAlice,25,LA"
        result = convert_csv_to_json(text, has_header=False, infer_types=True, array_of_objects=False)
        assert result == [['John', 30, 'NYC'], ['Alice', 25, 'LA']]
    
    def test_csv_semicolon_delimiter(self):
        """Convert CSV with semicolon delimiter."""
        text = "name;age;city\nJohn;30;NYC"
        result = convert_csv_to_json(text, has_header=True, delimiter=';', infer_types=True)
        assert result[0] == {'name': 'John', 'age': 30, 'city': 'NYC'}
    
    def test_csv_empty_input(self):
        """Convert empty CSV."""
        text = ""
        result = convert_csv_to_json(text)
        assert result == []


class TestConvertPythonDict:
    """Test Python dict conversion."""
    
    def test_simple_dict(self):
        """Convert simple Python dict."""
        text = "{'name': 'John', 'age': 30}"
        result = convert_python_dict_to_json(text)
        assert result == {'name': 'John', 'age': 30}
    
    def test_nested_dict(self):
        """Convert nested Python dict."""
        text = "{'user': {'name': 'John', 'age': 30}, 'active': True}"
        result = convert_python_dict_to_json(text)
        assert result == {'user': {'name': 'John', 'age': 30}, 'active': True}
    
    def test_list_literal(self):
        """Convert Python list literal."""
        text = "[1, 2, 3, 4, 5]"
        result = convert_python_dict_to_json(text)
        assert result == [1, 2, 3, 4, 5]
    
    def test_invalid_literal(self):
        """Raise error for invalid Python literal."""
        text = "{'name': 'John', 'func': lambda x: x}"  # Lambda not allowed
        with pytest.raises(ValueError):
            convert_python_dict_to_json(text)


class TestConvertYAML:
    """Test YAML conversion."""
    
    def test_simple_yaml(self):
        """Convert simple YAML."""
        text = "name: John\nage: 30\ncity: NYC"
        result = convert_yaml_to_json(text, infer_types=True)
        assert 'name' in result
        assert result['name'] == 'John'
    
    def test_yaml_with_nested_object(self):
        """Convert YAML with nested object (simplified)."""
        text = "user:\n  name: John\n  age: 30"
        result = convert_yaml_to_json(text, infer_types=True)
        assert 'user' in result
        # Note: Simplified YAML parser may not fully handle nesting


class TestConvertINI:
    """Test INI conversion."""
    
    def test_simple_ini(self):
        """Convert simple INI file."""
        text = "[user]\nname=John\nage=30\n\n[app]\ntheme=dark"
        result = convert_ini_to_json(text, infer_types=True)
        assert 'user' in result
        assert result['user']['name'] == 'John'
        assert result['user']['age'] == 30
        assert result['app']['theme'] == 'dark'
    
    def test_ini_skip_comments(self):
        """Skip comments in INI."""
        text = "[user]\n# Comment\nname=John\n; Another comment\nage=30"
        result = convert_ini_to_json(text, infer_types=True)
        assert result['user'] == {'name': 'John', 'age': 30}


class TestConvertTOML:
    """Test TOML conversion."""
    
    def test_toml_simple(self):
        """Convert simple TOML (requires toml/tomli library)."""
        text = '[user]\nname = "John"\nage = 30'
        try:
            result = convert_toml_to_json(text)
            assert result['user']['name'] == 'John'
            assert result['user']['age'] == 30
        except ValueError as e:
            # Library not available, skip test
            if "TOML library not available" in str(e):
                pytest.skip("TOML library not installed")
            else:
                raise


class TestConvertJavaProperties:
    """Test Java Properties conversion."""
    
    def test_simple_properties(self):
        """Convert simple Java Properties."""
        text = "user.name=John\nuser.age=30\napp.theme=dark"
        result = convert_java_properties_to_json(text, infer_types=True)
        assert result == {'user.name': 'John', 'user.age': 30, 'app.theme': 'dark'}
    
    def test_properties_skip_comments(self):
        """Skip comments in Java Properties."""
        text = "# Comment\nuser.name=John\n! Another comment\nuser.age=30"
        result = convert_java_properties_to_json(text, infer_types=True)
        assert result == {'user.name': 'John', 'user.age': 30}


class TestConvertTOON:
    """Test TOON conversion."""
    
    def test_toon_simple_key_value(self):
        """Convert simple TOON key: value."""
        text = "name: John\nage: 30"
        result = convert_toon_to_json(text)
        assert result == {'name': 'John', 'age': 30}
    
    def test_toon_inline_array(self):
        """Convert TOON inline array."""
        text = "tags[3]: python,coding,llm"
        result = convert_toon_to_json(text)
        assert result == {'tags': ['python', 'coding', 'llm']}
    
    def test_toon_root_array(self):
        """Convert TOON root array."""
        text = "[3]: apple,banana,orange"
        result = convert_toon_to_json(text)
        assert result == ['apple', 'banana', 'orange']


class TestConvertTextToJSON:
    """Test main conversion function."""
    
    def test_auto_detect_key_value(self):
        """Auto-detect key-value format."""
        text = "name: John\nage: 30"
        result = convert_text_to_json(text, format_type='auto', infer_types=True)
        assert 'name' in result
        assert result['name'] == 'John'
    
    def test_auto_detect_csv(self):
        """Auto-detect CSV format."""
        text = "name,age\nJohn,30"
        result = convert_text_to_json(text, format_type='auto', infer_types=True)
        assert isinstance(result, list)
    
    def test_explicit_format_list(self):
        """Use explicit format (list)."""
        text = "- Apple\n- Banana"
        result = convert_text_to_json(text, format_type='list', infer_types=True)
        assert result == ['Apple', 'Banana']
    
    def test_empty_text(self):
        """Convert empty text."""
        text = ""
        result = convert_text_to_json(text, format_type='auto')
        assert result == {}
    
    def test_unknown_format_error(self):
        """Raise error for unknown format."""
        text = "some text"
        with pytest.raises(ValueError):
            convert_text_to_json(text, format_type='invalid_format')


class TestEdgeCases:
    """Test edge cases."""
    
    def test_text_with_only_whitespace(self):
        """Convert text with only whitespace."""
        text = "   \n  \n   "
        result = convert_text_to_json(text, format_type='auto')
        assert result == {}
    
    def test_key_value_with_empty_values(self):
        """Convert key-value with empty values."""
        text = "name: John\nage:\ncity: NYC"
        result = convert_key_value_to_json(text, infer_types=True)
        assert result['name'] == 'John'
        assert result['age'] is None  # Empty string becomes None
        assert result['city'] == 'NYC'
    
    def test_list_with_no_bullets(self):
        """Convert list without bullet prefixes."""
        text = "Item 1\nItem 2\nItem 3"
        result = convert_list_to_json(text, infer_types=True)
        assert result == ['Item 1', 'Item 2', 'Item 3']
    
    def test_csv_with_mismatched_columns(self):
        """Convert CSV with mismatched column counts."""
        text = "name,age,city\nJohn,30\nAlice,25,LA,extra"
        result = convert_csv_to_json(text, has_header=True, infer_types=True)
        assert len(result) == 2
        assert result[0] == {'name': 'John', 'age': 30}  # Missing city
        assert result[1]['name'] == 'Alice'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
