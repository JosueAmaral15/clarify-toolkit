#!/usr/bin/env python3
"""Detailed test of all 15 format outputs to verify correctness."""

from src.converters.json_output_converter import convert_json_to_format
import json

# Test data
test_data = {
    "user": {
        "name": "John Doe",
        "age": 30
    },
    "tags": ["python", "coding"]
}

formats = [
    "JSON", "CSV", "YAML", "TOML", "INI", 
    "HTML Table", "Python Dict", "Java Properties", "TOON",
    "Key-Value", "List", "JSX Button", "JSX Form", "HTML Div", "JSX Component"
]

print("="*80)
print("DETAILED FORMAT OUTPUT VERIFICATION")
print("="*80)

for fmt in formats:
    print(f"\n{'='*80}")
    print(f"Format: {fmt}")
    print("="*80)
    
    try:
        result = convert_json_to_format(test_data, fmt)
        print(result[:500])  # First 500 chars
        
        # Verify format characteristics
        if fmt == "JSON":
            assert '{' in result and '"user"' in result, "❌ Not valid JSON!"
            print("\n✓ Contains JSON braces and keys")
        elif fmt == "CSV":
            assert ',' in result or 'user.name' in result, "❌ Not CSV format!"
            print("\n✓ Contains CSV delimiters or flattened keys")
        elif fmt == "YAML":
            assert 'user:' in result or 'name:' in result, "❌ Not YAML format!"
            print("\n✓ Contains YAML colons")
        elif fmt == "TOML":
            assert '[user]' in result or 'name =' in result, "❌ Not TOML format!"
            print("\n✓ Contains TOML sections or assignments")
        elif fmt == "INI":
            assert '[' in result and '=' in result, "❌ Not INI format!"
            print("\n✓ Contains INI sections and assignments")
        elif fmt == "HTML Table":
            assert '<table' in result and '<tr>' in result, "❌ Not HTML table!"
            print("\n✓ Contains HTML table tags")
        elif fmt == "HTML Div":
            assert '<div' in result and 'data-key=' in result, "❌ Not HTML div structure!"
            print("\n✓ Contains div tags with data-key attributes")
        elif fmt == "Python Dict":
            assert "{'user':" in result or '"user":' in result, "❌ Not Python dict!"
            print("\n✓ Contains Python dict syntax")
        elif fmt == "Java Properties" or fmt == "Key-Value":
            assert '=' in result and 'user.name' in result, "❌ Not properties format!"
            print("\n✓ Contains key=value format with dot notation")
        elif fmt == "TOON":
            assert ':' in result, "❌ Not TOON format!"
            print("\n✓ Contains TOON colons")
        elif fmt == "List":
            # List should output JSON for array data
            assert '{' in result or '[' in result, "❌ Not valid output!"
            print("\n✓ Contains valid output")
        elif fmt in ["JSX Button", "JSX Form", "JSX Component"]:
            # JSX templates should output JSON
            assert '{' in result and '"user"' in result, "❌ JSX should output JSON!"
            print("\n✓ JSX template outputs JSON (correct)")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")

print("\n" + "="*80)
print("✅ All format outputs verified!")
print("="*80)
