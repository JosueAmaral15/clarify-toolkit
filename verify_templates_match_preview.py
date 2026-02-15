#!/usr/bin/env python3
"""Verify each template output matches its preview/expected format."""

from src.converters.json_output_converter import convert_json_to_format

print("="*80)
print("TEMPLATE OUTPUT vs PREVIEW VERIFICATION")
print("="*80)

# Test data
test_data = {
    "user": {"name": "John Doe", "age": 30},
    "tags": ["python", "coding"]
}

templates = {
    "JSON": {
        "expected_features": ["{\n", '"user"', '"name"', '"age"', '"tags"'],
        "description": "Formatted JSON with newlines and indentation"
    },
    "CSV": {
        "expected_features": ["user.name,user.age", "John Doe,30"],
        "description": "CSV with flattened keys as headers"
    },
    "YAML": {
        "expected_features": ["user:", "  name:", "  age:", "tags:", "- python"],
        "description": "YAML with nested structure and list syntax"
    },
    "TOML": {
        "expected_features": ["[user]", "name =", "age =", "tags = ["],
        "description": "TOML with sections and assignments"
    },
    "INI": {
        "expected_features": ["[user]", "name =", "age ="],
        "description": "INI with sections"
    },
    "HTML Table": {
        "expected_features": ["<table", "<thead>", "<tr>", "<th>", "<td>"],
        "description": "HTML table with thead and tbody"
    },
    "HTML Div": {
        "expected_features": ['<div class="json-root">', 'data-key=', 'class="json-object"'],
        "description": "Nested divs with semantic classes"
    },
    "Python Dict": {
        "expected_features": ["{", "'user':", "'name':", "'age':"],
        "description": "Python dict literal"
    },
    "Java Properties": {
        "expected_features": ["user.name=", "user.age=", "tags[0]="],
        "description": "key=value with dot notation"
    },
    "TOON": {
        "expected_features": ["user.name:", "user.age:", "tags[2]:"],
        "description": "TOON format with arrays"
    },
}

print("\nChecking each template format...\n")

issues = []
passed = 0

for template_name, spec in templates.items():
    result = convert_json_to_format(test_data, template_name)
    
    missing = []
    for feature in spec["expected_features"]:
        if feature not in result:
            missing.append(feature)
    
    if missing:
        print(f"❌ {template_name:20s} - MISSING FEATURES!")
        print(f"   Description: {spec['description']}")
        print(f"   Missing: {missing}")
        print(f"   Actual output preview:")
        print("   " + result[:200].replace("\n", "\n   "))
        print()
        issues.append(template_name)
    else:
        print(f"✓ {template_name:20s} - Output matches expected format")
        passed += 1

print("\n" + "="*80)
print(f"Results: {passed}/{len(templates)} formats match expected output")
if issues:
    print(f"\n❌ Issues found in: {', '.join(issues)}")
    print("\nRECOMMENDATION: Research these formats and verify specifications!")
else:
    print("\n✅ All template outputs match expected formats!")
print("="*80)
