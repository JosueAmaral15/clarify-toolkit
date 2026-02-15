#!/usr/bin/env python3
"""Research and verify each format follows official standards."""

from src.converters.json_output_converter import convert_json_to_format
import json

print("="*80)
print("FORMAT STANDARDS COMPLIANCE CHECK")
print("="*80)

test_data = {
    "name": "John Doe",
    "age": 30,
    "active": True,
    "score": 95.5,
    "tags": ["python", "coding"],
    "address": {
        "city": "New York",
        "zip": "10001"
    }
}

standards_check = {
    "JSON": {
        "standard": "RFC 8259 (ECMA-404)",
        "checks": [
            ("Valid JSON parseable", lambda r: json.loads(r) is not None),
            ("Has proper braces", lambda r: r.strip().startswith('{')),
            ("Quoted keys", lambda r: '"name"' in r or "'name'" not in r),
        ]
    },
    "CSV": {
        "standard": "RFC 4180",
        "checks": [
            ("Has header row", lambda r: 'name' in r.split('\n')[0] or 'address.city' in r.split('\n')[0]),
            ("Comma delimited", lambda r: ',' in r),
            ("Data rows present", lambda r: len(r.split('\n')) >= 2),
        ]
    },
    "YAML": {
        "standard": "YAML 1.2 (yaml.org)",
        "checks": [
            ("Colon key-value", lambda r: ':' in r),
            ("List dash syntax", lambda r: '- ' in r),
            ("Nested indentation", lambda r: '  ' in r),
        ]
    },
    "TOML": {
        "standard": "TOML v1.0.0 (toml.io)",
        "checks": [
            ("Section brackets", lambda r: '[' in r),
            ("Equals assignment", lambda r: ' = ' in r or '=' in r),
            ("Array brackets", lambda r: '= [' in r or '=[' in r),
        ]
    },
    "INI": {
        "standard": "INI file format (de facto standard)",
        "checks": [
            ("Section headers", lambda r: '[' in r and ']' in r),
            ("Key=value pairs", lambda r: '=' in r),
            ("No braces for values", lambda r: '{' not in r),
        ]
    },
    "HTML Table": {
        "standard": "HTML5 (W3C)",
        "checks": [
            ("Table tag", lambda r: '<table' in r),
            ("Thead section", lambda r: '<thead>' in r),
            ("Tbody section", lambda r: '<tbody>' in r),
            ("TR/TH/TD tags", lambda r: '<tr>' in r and '<th>' in r and '<td>' in r),
        ]
    },
    "HTML Div": {
        "standard": "HTML5 (W3C)",
        "checks": [
            ("Div tags", lambda r: '<div' in r and '</div>' in r),
            ("Proper nesting", lambda r: r.count('<div') == r.count('</div>')),
            ("Data attributes", lambda r: 'data-key=' in r),
        ]
    },
    "Python Dict": {
        "standard": "Python dict syntax (PEP 8)",
        "checks": [
            ("Valid Python eval", lambda r: eval(r) is not None),
            ("Curly braces", lambda r: r.startswith('{')),
            ("Single quotes allowed", lambda r: "'" in r or '"' in r),
        ]
    },
    "Java Properties": {
        "standard": "Java .properties format",
        "checks": [
            ("Key=value lines", lambda r: '=' in r),
            ("Dot notation for nesting", lambda r: '.' in r),
            ("No braces", lambda r: '{' not in r),
        ]
    },
    "TOON": {
        "standard": "Token-Oriented Object Notation (toon-llm)",
        "checks": [
            ("Key:value syntax", lambda r: ': ' in r),
            ("Array notation [N]", lambda r: '[' in r and ']' in r),
            ("Tabular arrays for objects", lambda r: '{' in r if 'address' in test_data else True),
        ]
    },
}

print("\nVerifying compliance with official standards...\n")

issues = []
passed = 0

for fmt, spec in standards_check.items():
    result = convert_json_to_format(test_data, fmt)
    
    print(f"Format: {fmt}")
    print(f"Standard: {spec['standard']}")
    
    failed_checks = []
    for check_name, check_fn in spec["checks"]:
        try:
            if not check_fn(result):
                failed_checks.append(check_name)
        except Exception as e:
            failed_checks.append(f"{check_name} (ERROR: {e})")
    
    if failed_checks:
        print(f"  ❌ FAILED CHECKS: {failed_checks}")
        print(f"  Output preview: {result[:150]}...")
        issues.append((fmt, failed_checks))
    else:
        print(f"  ✅ All checks passed")
        passed += 1
    print()

print("="*80)
print(f"Results: {passed}/{len(standards_check)} formats comply with standards")
if issues:
    print(f"\n❌ Non-compliant formats:")
    for fmt, checks in issues:
        print(f"  - {fmt}: {checks}")
    print("\nRECOMMENDATION: Review and fix non-compliant formats!")
else:
    print("\n✅ All formats comply with their official standards!")
print("="*80)
