"""
JSON Output Format Converter

Converts JSON extraction output to various display formats:
- CSV (with recursive flattening)
- YAML
- TOML
- INI
- HTML Table
- Python Dict
- Java Properties
- TOON (using existing ToonAdapter)

Author: Programmer #3
Date: 2026-02-08
"""

import json
import csv
import io
from configparser import ConfigParser
from typing import Any, Dict, List, Union
from pprint import pformat


# Check library availability
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomllib  # Python 3.11+
    TOML_WRITE_AVAILABLE = False  # tomllib is read-only
except ImportError:
    TOML_WRITE_AVAILABLE = False

try:
    from .toon import ToonAdapter
    TOON_AVAILABLE = True
except ImportError:
    TOON_AVAILABLE = False


def flatten_json_recursive(
    data: Union[Dict, List, Any],
    parent_key: str = "",
    sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten nested JSON recursively with dot notation.
    
    Args:
        data: JSON data to flatten (dict, list, or primitive)
        parent_key: Parent key prefix for recursion
        sep: Separator for nested keys (default: ".")
    
    Returns:
        Flattened dictionary with dot-notation keys
    
    Example:
        >>> data = {"user": {"name": {"first": "John"}}}
        >>> flatten_json_recursive(data)
        {'user.name.first': 'John'}
        
        >>> data = {"items": [{"id": 1}, {"id": 2}]}
        >>> flatten_json_recursive(data)
        {'items[0].id': 1, 'items[1].id': 2}
    """
    items = []
    
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(flatten_json_recursive(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Handle arrays: enumerate items
                for i, item in enumerate(v):
                    array_key = f"{new_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        items.extend(flatten_json_recursive(item, array_key, sep=sep).items())
                    else:
                        items.append((array_key, item))
            else:
                items.append((new_key, v))
                
    elif isinstance(data, list):
        # Root-level array
        for i, item in enumerate(data):
            array_key = f"{parent_key}[{i}]" if parent_key else f"[{i}]"
            if isinstance(item, (dict, list)):
                items.extend(flatten_json_recursive(item, array_key, sep=sep).items())
            else:
                items.append((array_key, item))
    else:
        # Primitive value at root
        items.append((parent_key if parent_key else "value", data))
    
    return dict(items)


def convert_json_to_json(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to formatted JSON string.
    
    Args:
        data: JSON data (dict, list, or JSON string)
        **options: indent (int), ensure_ascii (bool)
    
    Returns:
        Formatted JSON string
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    indent = options.get('indent', 2)
    ensure_ascii = options.get('ensure_ascii', False)
    
    return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)


def convert_json_to_csv(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to CSV format with recursive flattening.
    
    Args:
        data: JSON data to convert
        **options: Not used currently
    
    Returns:
        CSV formatted string
    
    Note:
        Nested structures are flattened with dot notation (user.name.first).
        Arrays are enumerated (items[0], items[1]).
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Flatten the data
    flattened = flatten_json_recursive(data)
    
    # Write to CSV
    output = io.StringIO()
    if flattened:
        writer = csv.DictWriter(output, fieldnames=flattened.keys())
        writer.writeheader()
        writer.writerow(flattened)
    
    return output.getvalue()


def convert_json_to_yaml(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to YAML format.
    
    Args:
        data: JSON data to convert
        **options: default_flow_style (bool), sort_keys (bool)
    
    Returns:
        YAML formatted string
    
    Raises:
        ImportError: If pyyaml is not installed
    """
    if not YAML_AVAILABLE:
        raise ImportError(
            "pyyaml library is required for YAML conversion. "
            "Install it with: pip install pyyaml"
        )
    
    if isinstance(data, str):
        data = json.loads(data)
    
    default_flow_style = options.get('default_flow_style', False)
    sort_keys = options.get('sort_keys', False)
    
    return yaml.dump(data, default_flow_style=default_flow_style, sort_keys=sort_keys)


def convert_json_to_toml(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to TOML format.
    
    Args:
        data: JSON data to convert (must be dict at root)
        **options: Not used currently
    
    Returns:
        TOML formatted string
    
    Raises:
        ImportError: If toml library is not available
        TypeError: If data structure is not TOML-compatible
    
    Note:
        TOML has structural limitations (no root-level arrays, limited nesting).
        Requires 'toml' library (installed via: poetry add toml).
    """
    try:
        import toml as toml_lib
    except ImportError:
        raise ImportError(
            "toml library is required for TOML writing.\n"
            "Install it with: poetry add toml\n"
            "Or with pip: pip install toml"
        )
    
    if isinstance(data, str):
        data = json.loads(data)
    
    if not isinstance(data, dict):
        raise TypeError("TOML requires a dictionary at root level, not a list or primitive")
    
    # Attempt conversion (may fail for incompatible structures)
    output = io.StringIO()
    toml_lib.dump(data, output)
    return output.getvalue()


def convert_json_to_ini(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to INI format.
    
    Args:
        data: JSON data to convert (should be dict with nested dicts)
        **options: Not used currently
    
    Returns:
        INI formatted string
    
    Note:
        INI format requires sections (top-level keys) and simple key-value pairs.
        Complex nested structures are flattened with dot notation.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    config = ConfigParser()
    
    if isinstance(data, dict):
        for section, section_data in data.items():
            config.add_section(str(section))
            
            if isinstance(section_data, dict):
                # Flatten nested values
                flattened = flatten_json_recursive(section_data)
                for key, value in flattened.items():
                    config.set(str(section), str(key), str(value))
            else:
                # Single value
                config.set(str(section), "value", str(section_data))
    else:
        # Fallback: create a "data" section
        config.add_section("data")
        flattened = flatten_json_recursive(data)
        for key, value in flattened.items():
            config.set("data", str(key), str(value))
    
    output = io.StringIO()
    config.write(output)
    return output.getvalue()


def convert_json_to_html_table(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to HTML table format.
    
    Args:
        data: JSON data to convert
        **options: table_class (str), border (int)
    
    Returns:
        HTML table string
    
    Note:
        Nested structures are flattened with dot notation.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    table_class = options.get('table_class', 'data-table')
    border = options.get('border', 1)
    
    # Flatten the data
    flattened = flatten_json_recursive(data)
    
    # Build HTML table
    html = f'<table class="{table_class}" border="{border}">\n'
    html += '  <thead>\n    <tr>\n'
    
    # Headers
    for key in flattened.keys():
        html += f'      <th>{key}</th>\n'
    html += '    </tr>\n  </thead>\n'
    
    # Data row
    html += '  <tbody>\n    <tr>\n'
    for value in flattened.values():
        html += f'      <td>{value}</td>\n'
    html += '    </tr>\n  </tbody>\n'
    
    html += '</table>'
    return html


def convert_json_to_python_dict(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to Python dict literal representation.
    
    Args:
        data: JSON data to convert
        **options: indent (int), width (int)
    
    Returns:
        Python dict string representation
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    indent = options.get('indent', 2)
    width = options.get('width', 80)
    
    return pformat(data, indent=indent, width=width)


def convert_json_to_java_properties(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to Java Properties format (key=value).
    
    Args:
        data: JSON data to convert
        **options: Not used currently
    
    Returns:
        Java Properties formatted string (key=value lines)
    
    Note:
        Nested structures are flattened with dot notation.
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    # Flatten the data
    flattened = flatten_json_recursive(data)
    
    # Write as key=value
    lines = []
    for key, value in flattened.items():
        lines.append(f"{key}={value}")
    
    return '\n'.join(lines)


def convert_json_to_toon(data: Union[Dict, List, str], **options) -> str:
    """
    Convert JSON to TOON format (simple implementation without toon-llm).
    
    Args:
        data: JSON data to convert
        **options: Not used currently
    
    Returns:
        TOON formatted string
    
    Note:
        TOON format: key: value, key[N]: val1,val2,val3
        This is a simple implementation. For complex TOON features,
        use the ToonAdapter (requires toon-llm library).
    """
    if isinstance(data, str):
        data = json.loads(data)
    
    lines = []
    
    def convert_value(val):
        """Convert value to TOON format."""
        if isinstance(val, bool):
            return str(val).lower()
        elif isinstance(val, (int, float)):
            return str(val)
        elif isinstance(val, str):
            return val
        elif val is None:
            return "null"
        else:
            return str(val)
    
    def process_dict(d, prefix=""):
        """Process dictionary recursively."""
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Nested dict: recurse
                process_dict(value, full_key)
            elif isinstance(value, list):
                # Array: key[N]: val1,val2,val3
                if value:
                    array_values = [convert_value(v) for v in value]
                    lines.append(f"{full_key}[{len(value)}]: {','.join(array_values)}")
                else:
                    lines.append(f"{full_key}[0]: ")
            else:
                # Simple value
                lines.append(f"{full_key}: {convert_value(value)}")
    
    if isinstance(data, dict):
        process_dict(data)
    elif isinstance(data, list):
        # Root array
        if data:
            array_values = [convert_value(v) for v in data]
            lines.append(f"[{len(data)}]: {','.join(array_values)}")
        else:
            lines.append("[0]: ")
    else:
        # Primitive at root
        lines.append(f"value: {convert_value(data)}")
    
    return '\n'.join(lines)


def convert_json_to_format(
    data: Union[Dict, List, str],
    format_name: str,
    **options
) -> str:
    """
    Main entry point for JSON to format conversion.
    
    Args:
        data: JSON data to convert (dict, list, or JSON string)
        format_name: Target format name (case-insensitive)
        **options: Format-specific options
    
    Returns:
        Converted data as string
    
    Raises:
        ValueError: If format is not supported
        ImportError: If required library is not available
    
    Supported formats:
        - JSON (and all JSX/HTML templates default to JSON)
        - CSV
        - YAML
        - TOML
        - INI
        - HTML Table
        - Python Dict
        - Java Properties
        - TOON
        - Key-Value
        - List
    
    Example:
        >>> data = {"name": "Alice", "age": 30}
        >>> csv_output = convert_json_to_format(data, "CSV")
        >>> print(csv_output)
        name,age
        Alice,30
    """
    # Normalize format name
    format_normalized = format_name.strip().upper()
    
    # Map to converter functions
    converters = {
        "JSON": convert_json_to_json,
        "CSV": convert_json_to_csv,
        "YAML": convert_json_to_yaml,
        "TOML": convert_json_to_toml,
        "INI": convert_json_to_ini,
        "HTML TABLE": convert_json_to_html_table,
        "PYTHON DICT": convert_json_to_python_dict,
        "JAVA PROPERTIES": convert_json_to_java_properties,
        "TOON": convert_json_to_toon,
        "KEY-VALUE": convert_json_to_java_properties,  # Alias for Java Properties
        "LIST": convert_json_to_json,  # Lists are already JSON arrays
        # JSX/HTML templates are input examples, output as JSON
        "JSX BUTTON": convert_json_to_json,
        "JSX FORM": convert_json_to_json,
        "HTML DIV": convert_json_to_json,
        "JSX COMPONENT": convert_json_to_json,
    }
    
    converter = converters.get(format_normalized)
    if not converter:
        # Default to JSON for any unrecognized format
        return convert_json_to_json(data, **options)
    
    return converter(data, **options)
