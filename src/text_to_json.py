"""
Text to JSON Converter Module

Converts various text formats to JSON:
- Key-Value pairs (key: value, key = value)
- Lists (bullet points with -, *)
- CSV (comma-separated values)
- Python dict literals
- YAML-like format
- INI file format
- TOML format
- Java Properties
- TOON format (Token-Oriented Object Notation)

Author: Josué Amaral
Date: 2025-12-01
"""

import re
import ast
import json
from typing import Any, Dict, List, Optional, Union


def detect_format(text: str) -> str:
    """
    Automatically detect the format of input text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Format name: 'python_dict', 'csv', 'list', 'yaml', 'ini', 
                     'toml', 'java_properties', 'toon', 'key_value', 'unknown'
    """
    text = text.strip()
    if not text:
        return 'unknown'
    
    lines = text.split('\n')
    first_line = lines[0].strip()
    
    # TOON format (must check before Python dict - has higher priority)
    # TOON patterns: key[N]: values or [N]: values
    if re.match(r'^\w+\[\d+\]:', first_line) or re.match(r'^\[\d+\]:\s*\S', first_line):
        return 'toon'
    
    # INI format (sections with [section] - must check before Python dict)
    # INI has [section] on its own line, not [expression]
    if first_line.startswith('[') and first_line.endswith(']') and not first_line.startswith('[['):
        # Check if it's a section name (word characters only, no brackets inside)
        if re.match(r'^\[\w+\]$', first_line):
            return 'ini'
    
    # Python dict/list literal (must come after TOON and INI checks)
    if (first_line.startswith('{') or (first_line.startswith('[') and not re.match(r'^\[\d+\]:', first_line))):
        return 'python_dict'
    
    # TOML format (sections with [section] or [[array]])
    if first_line.startswith('[[') or (len(lines) > 2 and any(l.strip().startswith('[') for l in lines[:5])):
        # Check for TOML-specific patterns
        if any('=' in line and not line.strip().startswith('#') for line in lines[:10]):
            return 'toml'
    
    # CSV format (comma-separated with multiple columns)
    if ',' in first_line:
        fields = first_line.split(',')
        if len(fields) >= 2:
            # Check if subsequent lines also have commas
            if len(lines) > 1 and ',' in lines[1]:
                return 'csv'
    
    # List format (lines starting with - or *)
    bullet_count = sum(1 for line in lines[:10] if line.strip().startswith('-') or line.strip().startswith('*'))
    if bullet_count >= len(lines[:10]) * 0.5:  # At least 50% are bullets
        return 'list'
    
    # YAML format (key: value with indentation patterns)
    if ':' in first_line and not '=' in first_line:
        # Check for YAML-specific patterns (indentation, arrays with -)
        has_indentation = any(line.startswith('  ') or line.startswith('\t') for line in lines[1:5])
        if has_indentation:
            return 'yaml'
    
    # Java Properties (key=value or key: value, no sections)
    if '=' in first_line or ':' in first_line:
        # Check if it looks like properties (no indentation, simple format)
        has_sections = any(line.strip().startswith('[') for line in lines)
        if not has_sections:
            equals_count = sum(1 for line in lines[:10] if '=' in line)
            if equals_count >= len(lines[:10]) * 0.5:
                return 'java_properties'
    
    # Key-Value pairs (default if has : or =)
    if ':' in first_line or '=' in first_line:
        return 'key_value'
    
    return 'unknown'


def parse_value(value_str: str, infer_types: bool = True) -> Any:
    """
    Parse a string value into appropriate type.
    
    Args:
        value_str: String value to parse
        infer_types: If True, infer types (int, float, bool, null). If False, keep as string.
        
    Returns:
        Parsed value (str, int, float, bool, None)
    """
    value_str = value_str.strip()
    
    if not infer_types:
        return value_str
    
    # Empty string
    if value_str == '':
        return None
    
    # Boolean values
    if value_str.lower() in ('true', 'yes', 'on'):
        return True
    if value_str.lower() in ('false', 'no', 'off'):
        return False
    
    # Null values
    if value_str.lower() in ('null', 'none', 'nil'):
        return None
    
    # Try integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Return as string
    return value_str


def convert_key_value_to_json(text: str, infer_types: bool = True) -> Dict[str, Any]:
    """
    Convert key-value pairs to JSON.
    
    Supports formats:
    - key: value
    - key = value
    - key=value (no spaces)
    
    Args:
        text: Text with key-value pairs
        infer_types: Whether to infer types or keep all as strings
        
    Returns:
        Dictionary with parsed key-value pairs
    """
    result = {}
    
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        # Try colon separator
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = parse_value(value.strip(), infer_types)
        # Try equals separator
        elif '=' in line:
            key, value = line.split('=', 1)
            result[key.strip()] = parse_value(value.strip(), infer_types)
    
    return result


def convert_list_to_json(text: str, infer_types: bool = True) -> List[Any]:
    """
    Convert bullet list to JSON array.
    
    Supports:
    - Item 1
    * Item 2
    
    Args:
        text: Text with bullet list
        infer_types: Whether to infer types or keep all as strings
        
    Returns:
        List with parsed items
    """
    result = []
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Remove bullet prefix
        if line.startswith('-'):
            item = line[1:].strip()
        elif line.startswith('*'):
            item = line[1:].strip()
        else:
            item = line
        
        result.append(parse_value(item, infer_types))
    
    return result


def convert_csv_to_json(text: str, has_header: bool = True, 
                        delimiter: str = ',', infer_types: bool = True,
                        array_of_objects: bool = True) -> Union[List[Dict], List[List]]:
    """
    Convert CSV to JSON.
    
    Args:
        text: CSV text
        has_header: First line is header row
        delimiter: CSV delimiter (comma, semicolon, tab)
        infer_types: Whether to infer types
        array_of_objects: If True, return array of objects. If False, array of arrays.
        
    Returns:
        List of dictionaries (if array_of_objects) or list of lists
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    if not lines:
        return []
    
    if has_header and array_of_objects:
        headers = [h.strip() for h in lines[0].split(delimiter)]
        data_lines = lines[1:]
        
        result = []
        for line in data_lines:
            values = [v.strip() for v in line.split(delimiter)]
            obj = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    obj[header] = parse_value(values[i], infer_types)
            result.append(obj)
        
        return result
    else:
        # Array of arrays
        result = []
        start_idx = 1 if has_header else 0
        for line in lines[start_idx:]:
            values = [parse_value(v.strip(), infer_types) for v in line.split(delimiter)]
            result.append(values)
        
        return result


def convert_python_dict_to_json(text: str) -> Any:
    """
    Convert Python dict/list literal to JSON.
    
    Uses ast.literal_eval() for safe evaluation.
    
    Args:
        text: Python literal string
        
    Returns:
        Parsed Python object
        
    Raises:
        ValueError: If text is not a valid Python literal
    """
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid Python literal: {e}")


def convert_yaml_to_json(text: str, infer_types: bool = True) -> Any:
    """
    Convert YAML-like format to JSON.
    
    Simplified YAML parser supporting:
    - key: value
    - nested objects with indentation
    - arrays with - prefix
    
    Note: This is a simplified implementation. For full YAML support, use PyYAML library.
    
    Args:
        text: YAML-like text
        infer_types: Whether to infer types
        
    Returns:
        Parsed object (dict or list)
    """
    lines = text.split('\n')
    
    def parse_yaml_recursive(lines_list, start_idx, base_indent):
        result = {}
        i = start_idx
        
        while i < len(lines_list):
            line = lines_list[i]
            if not line.strip():
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # End of current level
            if indent < base_indent:
                break
            
            # Skip if more indented (will be processed recursively)
            if indent > base_indent:
                i += 1
                continue
            
            line_content = line.strip()
            
            # Array item
            if line_content.startswith('-'):
                # This should be handled by parent
                break
            
            # Key-value pair
            if ':' in line_content:
                key, value = line_content.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Check if next line is indented (nested object/array)
                if i + 1 < len(lines_list):
                    next_line = lines_list[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    
                    if next_indent > indent and not value:
                        # Nested object or array
                        if next_line.strip().startswith('-'):
                            # Array
                            array_items = []
                            j = i + 1
                            while j < len(lines_list):
                                item_line = lines_list[j]
                                item_indent = len(item_line) - len(item_line.lstrip())
                                if item_indent <= indent:
                                    break
                                if item_line.strip().startswith('-'):
                                    item_value = item_line.strip()[1:].strip()
                                    array_items.append(parse_value(item_value, infer_types))
                                j += 1
                            result[key] = array_items
                            i = j
                            continue
                        else:
                            # Nested object
                            nested_obj, next_i = parse_yaml_recursive(lines_list, i + 1, next_indent)
                            result[key] = nested_obj
                            i = next_i
                            continue
                
                # Simple value
                result[key] = parse_value(value, infer_types) if value else None
            
            i += 1
        
        return result, i
    
    obj, _ = parse_yaml_recursive(lines, 0, 0)
    return obj


def convert_ini_to_json(text: str, infer_types: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Convert INI format to JSON.
    
    Format:
    [section1]
    key1=value1
    key2=value2
    
    [section2]
    key3=value3
    
    Args:
        text: INI format text
        infer_types: Whether to infer types
        
    Returns:
        Dictionary with sections as keys
    """
    result = {}
    current_section = None
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#') or line.startswith(';'):
            continue
        
        # Section header
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            result[current_section] = {}
            continue
        
        # Key-value pair
        if current_section and ('=' in line or ':' in line):
            if '=' in line:
                key, value = line.split('=', 1)
            else:
                key, value = line.split(':', 1)
            
            result[current_section][key.strip()] = parse_value(value.strip(), infer_types)
    
    return result


def convert_toml_to_json(text: str) -> Any:
    """
    Convert TOML format to JSON.
    
    Uses tomli/toml library for parsing.
    
    Args:
        text: TOML format text
        
    Returns:
        Parsed TOML as dict
        
    Raises:
        ValueError: If TOML parsing fails or library not available
    """
    try:
        # Try tomli (Python 3.11+)
        import tomli
        return tomli.loads(text)
    except ImportError:
        try:
            # Try toml library
            import toml
            return toml.loads(text)
        except ImportError:
            raise ValueError("TOML library not available. Install with: pip install tomli")


def convert_java_properties_to_json(text: str, infer_types: bool = True) -> Dict[str, Any]:
    """
    Convert Java Properties format to JSON.
    
    Format:
    key1=value1
    key2: value2
    # comment
    
    Args:
        text: Java Properties text
        infer_types: Whether to infer types
        
    Returns:
        Dictionary with properties
    """
    result = {}
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        # Key-value pair
        if '=' in line:
            key, value = line.split('=', 1)
        elif ':' in line:
            key, value = line.split(':', 1)
        else:
            continue
        
        result[key.strip()] = parse_value(value.strip(), infer_types)
    
    return result


def convert_toon_to_json(text: str) -> Any:
    """
    Convert TOON (Token-Oriented Object Notation) format to JSON.
    
    TOON is an LLM-optimized format:
    - key: value
    - key[N]: val1,val2,val3 (array with length)
    - [N]: val1,val2 (root array)
    - Tabular: key[N]{field1,field2}:
                 value1,value2
    
    Args:
        text: TOON format text
        
    Returns:
        Parsed TOON as dict/list/primitive
        
    Raises:
        ValueError: If TOON parsing fails
    """
    text = text.strip()
    
    # Simple key-value
    if ':' in text and not text.startswith('['):
        result = {}
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Array format: key[N]: values
            array_match = re.match(r'^(\w+)\[(\d+)\]:\s*(.*)$', line)
            if array_match:
                key = array_match.group(1)
                length = int(array_match.group(2))
                values_str = array_match.group(3)
                
                if values_str:
                    values = [parse_value(v.strip(), True) for v in values_str.split(',')]
                    result[key] = values
                else:
                    result[key] = []
                continue
            
            # Simple key-value
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = parse_value(value.strip(), True)
        
        return result
    
    # Root array: [N]: values
    root_array_match = re.match(r'^\[(\d+)\]:\s*(.*)$', text)
    if root_array_match:
        length = int(root_array_match.group(1))
        values_str = root_array_match.group(2)
        
        if values_str:
            values = [parse_value(v.strip(), True) for v in values_str.split(',')]
            return values
        else:
            return []
    
    # Fallback: try as key-value
    return convert_key_value_to_json(text, True)


def convert_text_to_json(text: str, format_type: str = 'auto', 
                         infer_types: bool = True, **kwargs) -> Any:
    """
    Main conversion function. Converts text to JSON based on format.
    
    Args:
        text: Input text
        format_type: Format type ('auto', 'key_value', 'list', 'csv', 'python_dict',
                     'yaml', 'ini', 'toml', 'java_properties', 'toon')
        infer_types: Whether to infer types (int, float, bool, null)
        **kwargs: Additional format-specific options
                  - has_header (CSV): First row is header (default: True)
                  - delimiter (CSV): CSV delimiter (default: ',')
                  - array_of_objects (CSV): Return array of objects vs arrays (default: True)
        
    Returns:
        Parsed JSON-compatible object
        
    Raises:
        ValueError: If format is unknown or conversion fails
    """
    text = text.strip()
    
    if not text:
        return {}
    
    # Auto-detect format
    if format_type == 'auto':
        format_type = detect_format(text)
    
    # Convert based on format
    if format_type == 'key_value':
        return convert_key_value_to_json(text, infer_types)
    
    elif format_type == 'list':
        return convert_list_to_json(text, infer_types)
    
    elif format_type == 'csv':
        return convert_csv_to_json(
            text,
            has_header=kwargs.get('has_header', True),
            delimiter=kwargs.get('delimiter', ','),
            infer_types=infer_types,
            array_of_objects=kwargs.get('array_of_objects', True)
        )
    
    elif format_type == 'python_dict':
        return convert_python_dict_to_json(text)
    
    elif format_type == 'yaml':
        return convert_yaml_to_json(text, infer_types)
    
    elif format_type == 'ini':
        return convert_ini_to_json(text, infer_types)
    
    elif format_type == 'toml':
        return convert_toml_to_json(text)
    
    elif format_type == 'java_properties':
        return convert_java_properties_to_json(text, infer_types)
    
    elif format_type == 'toon':
        return convert_toon_to_json(text)
    
    else:
        raise ValueError(f"Unknown format: {format_type}")
