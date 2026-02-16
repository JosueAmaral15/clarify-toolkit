#!/usr/bin/env python3
"""Test case preservation in all formats."""

from src.converters.json_output_converter import convert_json_to_format

print("="*80)
print("CASE PRESERVATION TEST")
print("="*80)

# Test data with various case styles
test_data = {
    "userName": "John Doe",           # camelCase
    "UserAge": 30,                     # PascalCase
    "user_city": "New York",          # snake_case
    "USER_COUNTRY": "USA",            # SCREAMING_SNAKE_CASE
    "isActive": True,                  # camelCase boolean
    "NestedData": {                    # PascalCase nested
        "firstName": "John",           # camelCase
        "LastName": "Doe"              # PascalCase
    }
}

formats = ["JSON", "CSV", "YAML", "TOML", "INI", "HTML Table", "HTML Div", 
           "Python Dict", "Java Properties", "TOON"]

print("\nTest Data (notice the mixed case styles):")
print(test_data)
print("\n" + "="*80)

for fmt in formats:
    print(f"\n{fmt}:")
    print("-"*80)
    result = convert_json_to_format(test_data, fmt)
    print(result[:300])  # First 300 chars
    
    # Check if case is preserved
    checks = {
        "userName": "userName" in result or "user_name" in result.lower(),
        "UserAge": "UserAge" in result or "user_age" in result.lower(),
        "isActive": "isActive" in result or "is_active" in result.lower(),
        "firstName": "firstName" in result or "first_name" in result.lower(),
    }
    
    preserved = all(checks.values())
    
    if "userName" in result:
        print("\n✓ Case preserved (camelCase intact)")
    elif "username" in result.lower():
        print("\n⚠ Case NOT preserved (converted to lowercase or different case)")
    else:
        print("\n? Could not determine case preservation")

print("\n" + "="*80)
