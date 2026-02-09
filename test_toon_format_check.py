#!/usr/bin/env python3
"""Check if TOON output matches template expectation."""

from src.converters.json_output_converter import convert_json_to_format

print("="*70)
print("TOON Template Example (from GUI):")
print("="*70)
print("""name: John Doe
age: 30
tags[3]: python,coding,llm
items[2]{id,name}:
  1,Apple
  2,Banana""")

print("\n" + "="*70)
print("My TOON Implementation Output:")
print("="*70)

# Test 1: Simple data matching template
test1 = {
    "name": "John Doe",
    "age": 30,
    "tags": ["python", "coding", "llm"],
    "items": [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"}
    ]
}

result1 = convert_json_to_format(test1, "TOON")
print(result1)

print("\n" + "="*70)
print("COMPARISON:")
print("="*70)

# Check differences
expected_features = {
    "Basic key:value": "name: John Doe" in result1,
    "Array syntax key[N]": "tags[3]:" in result1,
    "Comma-separated values": "python,coding,llm" in result1,
    "Nested object handling": "items" in result1,
    "Advanced syntax {id,name}": "{id,name}" in result1,  # This is the issue
    "Indented rows": "  1,Apple" in result1  # This too
}

for feature, present in expected_features.items():
    status = "✓" if present else "✗"
    print(f"{status} {feature}: {present}")

print("\n" + "="*70)
print("ISSUE IDENTIFIED:")
print("="*70)
print("My implementation does NOT support:")
print("1. Complex array syntax: items[2]{id,name}:")
print("2. Indented row data: '  1,Apple'")
print("")
print("My implementation outputs:")
print("- items[2]: (then flattens nested objects with dot notation)")
print("- items[0].id: 1")
print("- items[0].name: Apple")
print("")
print("Template shows ADVANCED TOON syntax I didn't implement!")
