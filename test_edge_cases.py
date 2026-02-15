#!/usr/bin/env python3
"""
Test edge cases for format conversion.
- Empty data
- Deeply nested structures
- Large arrays
- Special characters

Programmer: #3
Date: 2026-02-08
"""

from src.converters.json_output_converter import convert_json_to_format, flatten_json_recursive

print("=" * 70)
print("EDGE CASES TEST")
print("=" * 70)

test_cases = [
    {
        "name": "Empty dict",
        "data": {},
        "formats": ["JSON", "CSV", "YAML"]
    },
    {
        "name": "Empty array",
        "data": [],
        "formats": ["JSON", "List"]
    },
    {
        "name": "Deeply nested (5 levels)",
        "data": {"a": {"b": {"c": {"d": {"e": "deep"}}}}},
        "formats": ["JSON", "CSV", "Java Properties"]
    },
    {
        "name": "Large array (100 items)",
        "data": {"items": [f"item_{i}" for i in range(100)]},
        "formats": ["CSV", "TOON"]
    },
    {
        "name": "Special characters",
        "data": {"key": "value with spaces", "special": "!@#$%^&*()", "unicode": "こんにちは"},
        "formats": ["JSON", "CSV", "YAML"]
    },
    {
        "name": "Mixed types",
        "data": {"string": "text", "number": 42, "float": 3.14, "bool": True, "null": None},
        "formats": ["JSON", "Java Properties", "TOON"]
    },
    {
        "name": "Array of objects",
        "data": {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]},
        "formats": ["CSV", "YAML"]
    }
]

passed = 0
failed = 0

for test in test_cases:
    print(f"\n{'=' * 70}")
    print(f"Test: {test['name']}")
    print(f"{'=' * 70}")
    print(f"Data: {test['data']}")
    
    for fmt in test['formats']:
        try:
            output = convert_json_to_format(test['data'], fmt)
            print(f"  ✓ {fmt:20s} - OK ({len(output):4d} chars)")
            passed += 1
        except Exception as e:
            print(f"  ✗ {fmt:20s} - FAILED: {str(e)[:50]}")
            failed += 1

print(f"\n{'=' * 70}")
print("EDGE CASES RESULTS")
print(f"{'=' * 70}")
print(f"✓ Passed: {passed}")
print(f"✗ Failed: {failed}")

if failed == 0:
    print("\n✅ ALL EDGE CASES PASSED!")
    exit(0)
else:
    print(f"\n⚠ {failed} edge cases failed")
    exit(1)
