#!/usr/bin/env python3
"""
Test to verify _apply_limit_to_key restoration.

Tests that the Limit feature now:
1. Normalizes FIRST (raw text → normalized key)
2. Then applies limit to the normalized key
3. Respects word boundaries (underscores/dashes) with avoid_cut
"""

import sys
sys.path.insert(0, '.')

from src.extractors.advanced_extractor import AdvancedExtractor
import json

# Test JSX with long text and long class names
TEST_JSX = '''
<div className="min-h-screen bg-gradient-to-r from-blue-600 to-purple-600">
  <h1 className="text-4xl font-bold mb-4 text-center">
    This is a very long heading text that should be limited properly after normalization
  </h1>
  <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
    Click Me To Submit The Form Now Please
  </button>
</div>
'''

print("=" * 80)
print("Testing _apply_limit_to_key restoration")
print("=" * 80)
print()

# Test 1: OLD behavior (before restoration) - would truncate raw text first
print("🔧 Expected NEW behavior after restoration:")
print("-" * 80)
print("Raw text: 'Click Me To Submit The Form Now Please'")
print("1. Normalize: 'click_me_to_submit_the_form_now_please' (full)")
print("2. Apply limit=20: 'click_me_to_submit_' (20 chars)")
print("3. With avoid_cut: 'click_me_to_submit' (cut at underscore)")
print()

# Test with limit on normalized keys
print("📊 Test 1: Limit on JSON keys (normalized text)")
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
    limit="20",  # Limit to 20 characters
    avoid_cut=True,  # Cut at word boundary
    avoid_cut_direction="before",
    to_upper=False,
    use_class_names=False
)

paths1, json1 = extractor1.process_text("test.tsx", TEST_JSX)
print("Keys in JSON (should be limited on normalized text):")
for key in json.dumps(json1, indent=2).split('\n')[5:10]:
    if '"' in key and ':' in key:
        print(f"  {key.strip()}")
print()

# Test 2: Limit on class names
print("📊 Test 2: Limit on class names (Tailwind CSS)")
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
    limit="25",  # Limit class names to 25 characters
    avoid_cut=True,
    avoid_cut_direction="before",
    to_upper=False,
    use_class_names=True  # Use class names
)

paths2, json2 = extractor2.process_text("test.tsx", TEST_JSX)
print("Class names in JSON (should be limited):")
print(json.dumps(json2, indent=2)[:800])
print()

# Test 3: Compare with/without avoid_cut
print("📊 Test 3: Limit with/without avoid_cut")
print("-" * 80)

# Without avoid_cut
extractor3a = AdvancedExtractor(
    param="*", mode="jsx", avoid_keys="", avoid_keys_parameter="contains",
    include_key=False, include_value=False, no_standard=False, convert_to_json=True,
    with_quotation_marks=True, indentation=2, case_style="snake",
    limit="20", avoid_cut=False, to_upper=False, use_class_names=False
)
_, json3a = extractor3a.process_text("test.tsx", TEST_JSX)

# With avoid_cut
extractor3b = AdvancedExtractor(
    param="*", mode="jsx", avoid_keys="", avoid_keys_parameter="contains",
    include_key=False, include_value=False, no_standard=False, convert_to_json=True,
    with_quotation_marks=True, indentation=2, case_style="snake",
    limit="20", avoid_cut=True, to_upper=False, use_class_names=False
)
_, json3b = extractor3b.process_text("test.tsx", TEST_JSX)

# Extract button key
def get_button_key(data):
    if 'test.tsx' in data and 'div' in data['test.tsx']:
        if 'button' in data['test.tsx']['div']:
            keys = list(data['test.tsx']['div']['button'].keys())
            return keys[0] if keys else None
    return None

key_without = get_button_key(json3a)
key_with = get_button_key(json3b)

print(f"Without avoid_cut (hard cut at 20): '{key_without}'")
print(f"   Length: {len(key_without) if key_without else 0}")
print(f"With avoid_cut (cut at boundary): '{key_with}'")
print(f"   Length: {len(key_with) if key_with else 0}")
print()

# Verify behavior
if key_with and key_with.endswith(('_', '-')):
    print("❌ ISSUE: Key ends with separator (should be removed)")
elif key_with and len(key_with) <= 20:
    print("✅ GOOD: Key respects word boundary and limit")
else:
    print("⚠️  CHECK: Verify output manually")
print()

print("=" * 80)
print("✅ _apply_limit_to_key restoration test complete!")
print("=" * 80)
print()
print("Key improvements from restoration:")
print("1. Normalizes FIRST (better predictability)")
print("2. Limits on normalized keys (respects underscores/dashes)")
print("3. Same logic for class names AND regular keys (consistency)")
print("=" * 80)
