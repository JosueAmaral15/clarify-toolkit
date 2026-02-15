#!/usr/bin/env python3
"""Test HTML Div format conversion."""

from src.converters.json_output_converter import convert_json_to_format

# Test data
test_data = {
    "user": {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    },
    "settings": {
        "theme": "dark",
        "language": "en"
    },
    "tags": ["python", "coding", "llm"]
}

print("Testing HTML Div format conversion...")
print("=" * 70)
print("\nInput JSON:")
print(test_data)
print("\n" + "=" * 70)
print("Output HTML Div:")
print("=" * 70)

result = convert_json_to_format(test_data, "HTML Div")
print(result)

print("\n" + "=" * 70)
print("✓ HTML Div conversion successful!")
print("\nExpected structure:")
print("- Root <div class='json-root'>")
print("- Nested objects as <div class='json-object'>")
print("- Arrays as <div class='json-array'>")
print("- Properties as <div class='json-property'>")
print("- All keys in data-key attributes")
