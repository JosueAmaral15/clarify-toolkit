#!/usr/bin/env python3
"""Final verification: All 15 formats output in correct format."""

from src.converters.json_output_converter import convert_json_to_format

test_data = {
    "user": {"name": "John Doe", "age": 30},
    "tags": ["python", "coding"]
}

print("="*80)
print("FINAL FORMAT VERIFICATION - All 15 Templates")
print("="*80)

tests = [
    ("JSON", lambda r: '{' in r and '"user"' in r, "JSON syntax"),
    ("CSV", lambda r: ',' in r and 'user.name' in r, "CSV with headers"),
    ("YAML", lambda r: 'user:' in r and 'name:' in r, "YAML syntax"),
    ("TOML", lambda r: '[user]' in r and 'name =' in r, "TOML sections"),
    ("INI", lambda r: '[user]' in r and 'name =' in r, "INI sections"),
    ("HTML Table", lambda r: '<table' in r and '<tr>' in r and '<td>' in r, "HTML table tags"),
    ("HTML Div", lambda r: '<div' in r and 'data-key=' in r and 'class="json-' in r, "HTML div structure"),
    ("Python Dict", lambda r: '{' in r and "'user'" in r, "Python dict syntax"),
    ("Java Properties", lambda r: '=' in r and 'user.name=' in r, "Properties format"),
    ("TOON", lambda r: ':' in r and 'user.name:' in r, "TOON format"),
    ("Key-Value", lambda r: '=' in r and 'user.name=' in r, "Key-value pairs"),
    ("List", lambda r: '{' in r or '[' in r, "Valid output"),
    ("JSX Button", lambda r: '{' in r and '"user"' in r, "JSON (JSX input template)"),
    ("JSX Form", lambda r: '{' in r and '"user"' in r, "JSON (JSX input template)"),
    ("JSX Component", lambda r: '{' in r and '"user"' in r, "JSON (JSX input template)"),
]

passed = 0
failed = 0

for format_name, validator, description in tests:
    try:
        result = convert_json_to_format(test_data, format_name)
        
        if validator(result):
            print(f"✓ {format_name:20s} - {description}")
            passed += 1
        else:
            print(f"✗ {format_name:20s} - WRONG FORMAT!")
            print(f"  Output: {result[:100]}")
            failed += 1
    except Exception as e:
        print(f"✗ {format_name:20s} - ERROR: {e}")
        failed += 1

print("\n" + "="*80)
print(f"Results: {passed}/15 passed, {failed}/15 failed")
if failed == 0:
    print("✅ ALL 15 FORMATS OUTPUT CORRECTLY!")
else:
    print(f"❌ {failed} formats have issues")
print("="*80)
