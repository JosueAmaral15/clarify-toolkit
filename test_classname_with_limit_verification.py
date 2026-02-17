#!/usr/bin/env python3
"""
Test className truncation with use_class_names=True
Verifies that when "HTML tags -> class name" checkbox is enabled,
className values ARE properly truncated.
"""

from src.extractors.advanced_extractor import AdvancedExtractor

JSX_INPUT = """
<div className="min-h-screen bg-gradient-to-r">
  <div className="container mx-auto">
    <div className="max-w-3xl">
      <h1 className="text-4xl font-bold">{t.pages.contact.quickLinks.faq}</h1>
    </div>
  </div>
  <div className="stillHaveQuestions">
    <h2>{t.pages.faq.cta.title}</h2>
  </div>
</div>
"""

print("Testing use_class_names=True with Limit=2")
print("="*60)

extractor = AdvancedExtractor(
    param="*",
    mode="jsx",
    avoid_keys="",
    avoid_keys_parameter="contains",
    include_key=True,
    include_value=True,
    no_standard=False,
    convert_to_json=True,
    with_quotation_marks=True,
    indentation=2,
    case_style='camel',
    limit="2",  # Limit=2
    avoid_cut=False,  # Hard cut
    avoid_cut_direction='before',
    to_upper=False,
    only_strings=False,
    is_attribute_mode=False,
    use_class_names=True  # ← CHECKBOX ENABLED
)

path_lines, data = extractor.process_text("FAQPage", JSX_INPUT)

import json
print(json.dumps(data, indent=2))

# Check that class names ARE truncated
def find_keys(obj, keys=None):
    if keys is None:
        keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(k)
            find_keys(v, keys)
    return keys

all_keys = find_keys(data)
print("\n" + "="*60)
print("All keys found:")
for k in all_keys:
    print(f"  '{k}' ({len(k)} chars)")

print("\n" + "="*60)
# Check for expected truncated class names
expected_truncations = {
    'mi': 'min-h-screen truncated',
    'bg': 'bg-gradient-to-r truncated',
    'co': 'container truncated',
    'ma': 'max-w-3xl truncated',
    'st': 'stillHaveQuestions truncated'
}

found = 0
for key in expected_truncations:
    if key in all_keys:
        print(f"✅ Found '{key}' - {expected_truncations[key]}")
        found += 1
    else:
        print(f"❌ Missing '{key}' - {expected_truncations[key]}")

print("\n" + "="*60)
if found >= 3:  # At least 3 truncated class names found
    print("✅ PASS: className truncation with use_class_names=True WORKS!")
else:
    print(f"❌ FAIL: Only {found}/5 expected truncations found")
