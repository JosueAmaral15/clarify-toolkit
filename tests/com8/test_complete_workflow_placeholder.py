"""
Phase 4: Complete ODT translation workflow with placeholder approach
Testing the full integration
"""
import sys
sys.path.insert(0, 'src')
import re
from translation.format_mapper import FormatMapper, replace_tags_with_placeholders, restore_tags_from_placeholders
from translation.google_translate import GoogleTranslateAPI

print("="*80)
print("COMPLETE ODT TRANSLATION WORKFLOW WITH PLACEHOLDER PROTECTION")
print("="*80)
print()

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
output_file = 'CAIT_Biologia_Translated_COM8_PLACEHOLDER.odt'

# Step 1: Extract with formatting
print("Step 1: Extracting formatted text from ODT...")
tagged_text = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"✅ Extracted {len(tagged_text)} chars")
original_tag_count = len(re.findall(r'<\d+(?:\|\d+)?:[^>]+>', tagged_text))
print(f"   Tags found: {original_tag_count}")
print()

# Step 2: Replace tags with placeholders
print("Step 2: Replacing tags with placeholders...")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged_text)
print(f"✅ Protected {len(mapping)} tag pairs")
print(f"   Text length: {len(text_with_placeholders)} chars")
print()

# Step 3: Translate
print("Step 3: Translating (Portuguese → English)...")
translator = GoogleTranslateAPI()
result = translator.translate_text(text_with_placeholders, 'pt', 'en')

if not result.success:
    print(f"❌ Translation failed: {result.error_message}")
    sys.exit(1)

print(f"✅ Translation succeeded")
print(f"   Result length: {len(result.translated_text)} chars")
print()

# Step 4: Verify placeholders survived
print("Step 4: Verifying placeholder preservation...")
placeholders_found = len(re.findall(r'【FMT\d+】', result.translated_text))
print(f"   Placeholders found: {placeholders_found}/{len(mapping)}")

if placeholders_found != len(mapping):
    print(f"❌ WARNING: Lost {len(mapping) - placeholders_found} placeholders!")
else:
    print("✅ All placeholders preserved!")
print()

# Step 5: Restore tags
print("Step 5: Restoring original format tags...")
final_tagged = restore_tags_from_placeholders(result.translated_text, mapping)
print(f"✅ Tags restored")
final_tag_count = len(re.findall(r'<\d+(?:\|\d+)?:[^>]+>', final_tagged))
print(f"   Final tag count: {final_tag_count}/{original_tag_count}")
print()

# Step 6: Parse to segments
print("Step 6: Parsing tagged text to segments...")
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"✅ Parsed to {len(segments)} segments")
print()

# Step 7: Create output ODT
print("Step 7: Creating output ODT file...")
FormatMapper.create_odt_from_segments(segments, output_file)
print(f"✅ Created: {output_file}")

import os
output_size = os.path.getsize(output_file) / 1024
print(f"   File size: {output_size:.1f} KB")
print()

# Step 8: Verification
print("="*80)
print("VERIFICATION RESULTS")
print("="*80)
print(f"Tag preservation: {final_tag_count}/{original_tag_count} ({final_tag_count/original_tag_count*100:.1f}%)")

broken_tags = re.findall(r'<\d+\s+\|', final_tagged)
print(f"Broken tags: {len(broken_tags)}")

# Check for section headers
headers = ['RISKS', 'AGRICULTURE', 'HEALTH', 'ENVIRONMENT']
headers_found = sum(1 for h in headers if h in final_tagged.upper())
print(f"Section headers: {headers_found}/{len(headers)}")
print()

if final_tag_count == original_tag_count and len(broken_tags) == 0:
    print("🎉🎉🎉 SUCCESS: 100% TAG PRESERVATION! 🎉🎉🎉")
    print()
    print("Next steps:")
    print("1. Open the file in LibreOffice:")
    print(f"   libreoffice {output_file}")
    print("2. Verify formatting is correct (bold, fonts, etc.)")
    print("3. Compare with original document")
else:
    print("⚠️  Some issues detected")

print()
print("First 400 chars of translated text:")
print("-"*80)
plain = re.sub(r'<[^>]+>', '', final_tagged)
print(plain[:400])

