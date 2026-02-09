#!/usr/bin/env python3
"""Test actual extraction with camelCase case style."""

import sys
sys.path.insert(0, 'src')

from extractors.advanced_extractor import AdvancedExtractor

# JSX test input with camelCase variables
jsx_input = """
const [expandedItems, setExpandedItems] = useState([]);
const filteredFAQs = data.filter(item => item.active);
const faqCategories = ["General", "Technical", "Billing"];

<FAQPage>
  <div className="container">
    <h1>{t.pages.contact.quickLinks.faq}</h1>
    <button onClick={() => setExpandedItems([...items])}>
      Expand All
    </button>
  </div>
</FAQPage>
"""

# Save to temp file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as f:
    f.write(jsx_input)
    temp_file = f.name

print("Testing ACTUAL extraction with camelCase case_style...\n")

# Create extractor with camelCase settings
extractor = AdvancedExtractor(
    param="*",  # match all
    mode="jsx",
    avoid_keys="",
    avoid_keys_parameter="contains",
    include_key=True,
    include_value=True,
    no_standard=False,
    convert_to_json=True,
    with_quotation_marks=True,
    indentation=2,
    case_style="camel",  # ← THE KEY TEST
    limit=None,
    avoid_cut=False,
    avoid_cut_direction="before",
    to_upper=False,
    only_strings=False,
    is_attribute_mode=False,
    start_regex=None,
    end_regex=None,
    root_alias="Root",
    file_extensions=[".jsx"]
)

# Process the file
extractor.process_files([temp_file])

# Get JSON output
json_output = extractor.get_json_output()

print("JSON Output:")
print(json_output)
print("\n" + "="*80 + "\n")

# Check for camelCase preservation
import json
data = json.loads(json_output)

# Extract all keys recursively
def extract_keys(obj, prefix=""):
    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(prefix + k)
            keys.extend(extract_keys(v, prefix + k + "."))
    return keys

all_keys = extract_keys(data)

print("Extracted Keys:")
for key in all_keys:
    print(f"  {key}")

print("\n" + "="*80 + "\n")

# Check for problematic lowercase keys
lowercase_issues = []
for key in all_keys:
    # Check if key contains what should be camelCase but is all lowercase
    if "expandeditems" in key.lower():
        lowercase_issues.append(("expandedItems expected", key))
    if "filteredfaqs" in key.lower() and "filtered_faqs" not in key.lower():
        lowercase_issues.append(("filteredFaQs expected", key))
    if "faqcategories" in key.lower() and "faq_categories" not in key.lower():
        lowercase_issues.append(("faqCategories expected", key))

if lowercase_issues:
    print("❌ FOUND ISSUES:")
    for expected, got in lowercase_issues:
        print(f"  Expected: {expected}")
        print(f"  Got: {got}")
    sys.exit(1)
else:
    print("✅ No lowercase issues found! camelCase appears to be preserved.")
    sys.exit(0)

# Cleanup
import os
os.unlink(temp_file)
