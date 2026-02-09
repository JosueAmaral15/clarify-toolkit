"""
Phase 2: Test placeholder approach with FULL biology document
"""
import sys
sys.path.insert(0, 'src')
import re
from translation.format_mapper import FormatMapper
from translation.google_translate import GoogleTranslateAPI

# Import our placeholder functions
exec(open('test_placeholder_system.py').read().split('# ===')[0])

print("="*80)
print("PHASE 2: Full Document Test with Placeholder Approach")
print("="*80)
print()

# Extract original tagged text
print("Step 1: Extracting document...")
tagged = FormatMapper.extract_formatted_text_from_odt('/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt')
print(f"✅ Extracted: {len(tagged)} chars")

# Count original tags
original_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', tagged)
print(f"   Original tags: {len(original_tags)}")
print()

# Replace with placeholders
print("Step 2: Replacing tags with placeholders...")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
print(f"✅ Replaced: {len(mapping)} tag pairs")
print(f"   Text length: {len(text_with_placeholders)} chars")
print(f"   First placeholder: {list(mapping.keys())[0]}")
print(f"   Last placeholder: {list(mapping.keys())[-1]}")
print()

# Translate
print("Step 3: Translating (pt → en) with Google Translate...")
translator = GoogleTranslateAPI()
result = translator.translate_text(text_with_placeholders, 'pt', 'en')

if not result.success:
    print(f"❌ Translation failed: {result.error_message}")
    sys.exit(1)

print(f"✅ Translation succeeded")
print(f"   Translated length: {len(result.translated_text)} chars")
print()

# Check placeholder survival
print("Step 4: Verifying placeholder preservation...")
placeholders_in_translation = re.findall(r'【FMT\d+】', result.translated_text)
closing_placeholders = re.findall(r'【/FMT\d+】', result.translated_text)

print(f"   Opening placeholders found: {len(placeholders_in_translation)}")
print(f"   Closing placeholders found: {len(closing_placeholders)}")
print(f"   Expected: {len(mapping)} each")

if len(placeholders_in_translation) != len(mapping) or len(closing_placeholders) != len(mapping):
    print(f"❌ FAIL: Some placeholders were lost!")
    missing = len(mapping) - len(placeholders_in_translation)
    print(f"   Missing: {missing} placeholders")
else:
    print("✅ ALL PLACEHOLDERS PRESERVED!")
print()

# Restore tags
print("Step 5: Restoring original tags...")
final_tagged = restore_tags_from_placeholders(result.translated_text, mapping)
print(f"✅ Restoration complete")
print(f"   Final length: {len(final_tagged)} chars")
print()

# Verify tag restoration
print("Step 6: Verifying tag restoration...")
final_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', final_tagged)
print(f"   Final tag count: {len(final_tags)}")
print(f"   Original tag count: {len(original_tags)}")

preservation_rate = len(final_tags) / len(original_tags) * 100 if original_tags else 0
print(f"   Preservation rate: {preservation_rate:.1f}%")

# Check for broken tags
broken_tags = re.findall(r'<\d+\s+\|', final_tagged)
if broken_tags:
    print(f"❌ Found {len(broken_tags)} broken tags:")
    for tag in broken_tags[:3]:
        print(f"      {tag}")
else:
    print("✅ No broken tags!")
print()

# Check for section headers
print("Step 7: Verifying section headers...")
headers_to_check = ['RISKS', 'AGRICULTURE', 'HEALTH', 'ENVIRONMENT']
found_headers = []
for header in headers_to_check:
    if header in final_tagged.upper():
        found_headers.append(header)
        print(f"   ✅ Found: {header}")
    else:
        print(f"   ❌ Missing: {header}")

print()
print("="*80)
print("RESULTS SUMMARY")
print("="*80)
print(f"Tag preservation: {len(final_tags)}/{len(original_tags)} ({preservation_rate:.1f}%)")
print(f"Broken tags: {len(broken_tags)}")
print(f"Headers found: {len(found_headers)}/{len(headers_to_check)}")
print()

if preservation_rate == 100 and len(broken_tags) == 0:
    print("🎉🎉🎉 PERFECT: 100% TAG PRESERVATION WITH NO CORRUPTION! 🎉🎉🎉")
elif preservation_rate >= 99:
    print("✅ EXCELLENT: Near-perfect tag preservation!")
elif preservation_rate >= 95:
    print("✅ GOOD: High tag preservation rate")
else:
    print("⚠️  NEEDS IMPROVEMENT: Tag preservation below 95%")

print()
print("First 300 chars of translated text:")
print("-"*80)
print(final_tagged[:300])
print()

