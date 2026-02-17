#!/usr/bin/env python3
"""Comprehensive TOON format testing."""

from src.converters.json_output_converter import convert_json_to_format

print("="*70)
print("TOON FORMAT COMPREHENSIVE TEST")
print("="*70)

# Test 1: Template example data
print("\n1. Template Example Data:")
print("-"*70)
data1 = {
    "name": "John Doe",
    "age": 30,
    "tags": ["python", "coding", "llm"],
    "items": [
        {"id": 1, "name": "Apple"},
        {"id": 2, "name": "Banana"}
    ]
}
result1 = convert_json_to_format(data1, "TOON")
print(result1)

# Test 2: LLM example from docs (weather observations)
print("\n2. Array of Objects (Weather Data):")
print("-"*70)
data2 = {
    "weather_observations": [
        {"high_temp": 75, "low_temp": 50, "average_temp": 62.5},
        {"high_temp": 78, "low_temp": 52, "average_temp": 65.0},
        {"high_temp": 72, "low_temp": 48, "average_temp": 60.0}
    ]
}
result2 = convert_json_to_format(data2, "TOON")
print(result2)

# Test 3: Mixed arrays (primitives + objects)
print("\n3. Mixed Data Types:")
print("-"*70)
data3 = {
    "simple_array": [1, 2, 3],
    "string_array": ["a", "b", "c"],
    "object_array": [
        {"x": 10, "y": 20},
        {"x": 30, "y": 40}
    ],
    "nested": {
        "count": 5,
        "active": True
    }
}
result3 = convert_json_to_format(data3, "TOON")
print(result3)

# Test 4: Edge case - objects with different keys
print("\n4. Objects with Different Keys (should use common keys only):")
print("-"*70)
data4 = {
    "mixed_objects": [
        {"id": 1, "name": "A", "extra": "X"},
        {"id": 2, "name": "B"},
        {"id": 3, "name": "C", "other": "Y"}
    ]
}
result4 = convert_json_to_format(data4, "TOON")
print(result4)

print("\n" + "="*70)
print("✅ TOON FORMAT TESTS COMPLETE")
print("="*70)
