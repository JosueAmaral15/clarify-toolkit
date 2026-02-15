#!/usr/bin/env python3
"""Show sample output for all 15 formats."""

from src.converters.json_output_converter import convert_json_to_format

test_data = {
    "user": {"name": "John Doe", "age": 30},
    "tags": ["python", "coding"]
}

formats = [
    "JSON", "CSV", "YAML", "TOML", "INI", 
    "HTML Table", "HTML Div", "Python Dict", "Java Properties", "TOON",
    "Key-Value", "List", "JSX Button", "JSX Form", "JSX Component"
]

for fmt in formats:
    print(f"\n{'='*70}")
    print(f"  {fmt}")
    print('='*70)
    result = convert_json_to_format(test_data, fmt)
    # Limit output to 400 chars for readability
    if len(result) > 400:
        print(result[:400] + "\n... (truncated)")
    else:
        print(result)
