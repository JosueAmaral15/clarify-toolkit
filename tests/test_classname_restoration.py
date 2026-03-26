#!/usr/bin/env python3
"""
Test className extraction feature after restoration.

Tests that use_class_names parameter properly extracts and uses
className/class attributes from JSX/HTML as JSON keys.
"""

import sys
sys.path.insert(0, '.')

from src.extractors.advanced_extractor import AdvancedExtractor

# Sample JSX with className attributes
TEST_JSX = '''
<div className="container mx-auto">
  <h1 className="text-4xl font-bold mb-4">FAQ Page</h1>
  <div className="faq-section">
    <button className="accordion">
      <h3 className="question-title">What is PTEasy?</h3>
    </button>
    <div className="answer">
      <p className="answer-text">PTEasy is a platform.</p>
    </div>
  </div>
</div>
'''

print("=" * 80)
print("Testing className extraction feature (restored)")
print("=" * 80)
print()

# Test WITHOUT use_class_names (should use tag names)
print("1️⃣ Test WITHOUT use_class_names:")
print("-" * 80)
extractor1 = AdvancedExtractor(
    param="*",
    mode="jsx",
    avoid_keys="",
    avoid_keys_parameter="contains",
    include_key=False,
    include_value=False,
    no_standard=False,
    convert_to_json=True,
    with_quotation_marks=True,
    indentation=2,
    case_style="snake",
    limit=None,
    avoid_cut=False,
    to_upper=False,
    only_strings=False,
    is_attribute_mode=False,
    use_class_names=False  # ❌ Disabled
)

paths1, json1 = extractor1.process_text("test.tsx", TEST_JSX)
print("Sample keys (should be tag names):")
import json
data1 = json1 if isinstance(json1, dict) else (json.loads(json1) if json1 else {})
if 'test' in data1 and 'div' in data1['test']:
    keys = list(data1['test']['div'].keys())[:3]
    print(f"  {keys}")
    print(f"  ✓ Uses tag names: {any('div' in str(k) or 'h1' in str(k) for k in keys)}")
else:
    print(f"  Structure: {list(data1.keys())}")
print()

# Test WITH use_class_names (should use class names)
print("2️⃣ Test WITH use_class_names:")
print("-" * 80)
extractor2 = AdvancedExtractor(
    param="*",
    mode="jsx",
    avoid_keys="",
    avoid_keys_parameter="contains",
    include_key=False,
    include_value=False,
    no_standard=False,
    convert_to_json=True,
    with_quotation_marks=True,
    indentation=2,
    case_style="snake",
    limit=None,
    avoid_cut=False,
    to_upper=False,
    only_strings=False,
    is_attribute_mode=False,
    use_class_names=True  # ✅ Enabled
)

paths2, json2 = extractor2.process_text("test.tsx", TEST_JSX)
print("Sample keys (should be class names):")
data2 = json2 if isinstance(json2, dict) else (json.loads(json2) if json2 else {})
if data2:
    # Check for class-based keys
    keys_str = json.dumps(data2, indent=2)[:500]
    has_container = 'container' in keys_str
    has_text_4xl = 'text-4xl' in keys_str or 'font-bold' in keys_str
    has_faq_section = 'faq-section' in keys_str
    
    print(f"  Contains 'container-mx-auto': {has_container}")
    print(f"  Contains 'text-4xl-font-bold-mb-4' or similar: {has_text_4xl}")
    print(f"  Contains 'faq-section': {has_faq_section}")
    print()
    print("JSON structure preview:")
    print(keys_str)
    
    if has_container and has_faq_section:
        print()
        print("✅ ✅ ✅ SUCCESS: className extraction is FULLY WORKING! ✅ ✅ ✅")
    else:
        print()
        print("❌ FAIL: Class names not found in output")
else:
    print(f"  Structure: {list(data2.keys())}")
    print("  JSON preview:")
    print(json.dumps(data2, indent=2)[:500])

print()
print("=" * 80)
