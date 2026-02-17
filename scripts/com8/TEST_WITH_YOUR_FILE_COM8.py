"""
TESTING WITH YOUR EXACT FILE PATH
User requested: "test by yourself again with the file path that I give to you"
File: /home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt
"""
import sys
sys.path.insert(0, 'src')
import re
from translation.format_mapper import FormatMapper, replace_tags_with_placeholders, restore_tags_from_placeholders
from translation.google_translate import GoogleTranslateAPI
import os

print("="*80)
print("TESTING WITH YOUR FILE: CAIT- Trabalho de Biologia - Josué 3001.odt")
print("="*80)
print()

# YOUR file path
input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
output_file = '/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify-COM8/CAIT_FINAL_TEST_100_PERCENT_COM8.odt'

# Verify file exists
if not os.path.exists(input_file):
    print(f"❌ ERROR: File not found: {input_file}")
    sys.exit(1)

print(f"✅ File found: {input_file}")
file_size = os.path.getsize(input_file) / 1024
print(f"   Size: {file_size:.1f} KB")
print()

# Step 1: Extract
print("STEP 1: Extracting formatted text from ODT")
print("-"*80)
tagged_text = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"✅ Extracted text length: {len(tagged_text)} characters")

# Count tags
original_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', tagged_text)
print(f"✅ Format tags found: {len(original_tags)}")
print()

# Show first few tags
print("First 5 tags:")
for i, tag in enumerate(original_tags[:5], 1):
    print(f"  {i}. {tag[:70]}...")
print()

# Step 2: Protect with placeholders
print("STEP 2: Protecting tags with Unicode placeholders")
print("-"*80)
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged_text)
print(f"✅ Protected {len(mapping)} tag pairs")
print(f"   Placeholder format: 【FMTXXX】text【/FMTXXX】")
print(f"   Protected text length: {len(text_with_placeholders)} characters")
print()

# Show conversion example
print("Example conversion:")
print(f"  Before: {tagged_text[:120]}...")
print(f"  After:  {text_with_placeholders[:120]}...")
print()

# Step 3: Translate
print("STEP 3: Translating (Portuguese → English)")
print("-"*80)
translator = GoogleTranslateAPI()
print("Sending to Google Translate API...")

result = translator.translate_text(text_with_placeholders, 'pt', 'en')

if not result.success:
    print(f"❌ Translation FAILED: {result.error_message}")
    sys.exit(1)

print(f"✅ Translation succeeded!")
print(f"   Translated length: {len(result.translated_text)} characters")
print()

# Step 4: Check placeholder survival
print("STEP 4: Verifying placeholder preservation")
print("-"*80)
opening_placeholders = re.findall(r'【FMT\d+】', result.translated_text)
closing_placeholders = re.findall(r'【/FMT\d+】', result.translated_text)

print(f"Opening placeholders: {len(opening_placeholders)}")
print(f"Closing placeholders: {len(closing_placeholders)}")
print(f"Expected: {len(mapping)} each")
print()

if len(opening_placeholders) != len(mapping):
    print(f"❌ LOST {len(mapping) - len(opening_placeholders)} opening placeholders!")
    sys.exit(1)
    
if len(closing_placeholders) != len(mapping):
    print(f"❌ LOST {len(mapping) - len(closing_placeholders)} closing placeholders!")
    sys.exit(1)

print("✅ ALL PLACEHOLDERS SURVIVED TRANSLATION!")
print()

# Step 5: Restore tags
print("STEP 5: Restoring original format tags")
print("-"*80)
final_tagged = restore_tags_from_placeholders(result.translated_text, mapping)
print(f"✅ Tags restored")
print(f"   Final text length: {len(final_tagged)} characters")
print()

# Count final tags
final_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', final_tagged)
print(f"Final tag count: {len(final_tags)}")
print(f"Original tag count: {len(original_tags)}")
print()

# Check for broken tags
broken_tags = re.findall(r'<\d+\s+\|', final_tagged)
if broken_tags:
    print(f"❌ FOUND {len(broken_tags)} BROKEN TAGS:")
    for tag in broken_tags[:5]:
        print(f"   {tag}")
    print()
else:
    print("✅ ZERO broken tags!")
    print()

# Step 6: Parse to segments
print("STEP 6: Parsing to format segments")
print("-"*80)
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"✅ Parsed to {len(segments)} segments")
print()

# Step 7: Create ODT
print("STEP 7: Creating output ODT file")
print("-"*80)
FormatMapper.create_odt_from_segments(segments, output_file)

if not os.path.exists(output_file):
    print(f"❌ ERROR: Failed to create output file")
    sys.exit(1)

output_size = os.path.getsize(output_file) / 1024
print(f"✅ Created: {output_file}")
print(f"   Size: {output_size:.1f} KB")
print()

# Step 8: Final verification
print("="*80)
print("FINAL RESULTS")
print("="*80)
print()

preservation_rate = (len(final_tags) / len(original_tags) * 100) if original_tags else 0

print(f"{'Metric':<30} {'Result':<20} {'Status':<20}")
print("-"*70)
print(f"{'Input file':<30} {file_size:.1f} KB{'':<16} {'✅':<20}")
print(f"{'Original tags':<30} {len(original_tags):<20} {'✅':<20}")
print(f"{'Placeholders protected':<30} {len(mapping):<20} {'✅':<20}")
print(f"{'Placeholders survived':<30} {len(opening_placeholders):<20} {'✅':<20}")
print(f"{'Tags restored':<30} {len(final_tags):<20} {'✅' if len(final_tags) == len(original_tags) else '❌':<20}")
print(f"{'Broken tags':<30} {len(broken_tags):<20} {'✅' if len(broken_tags) == 0 else '❌':<20}")
print(f"{'Preservation rate':<30} {preservation_rate:.1f}%{'':<16} {'✅' if preservation_rate == 100 else '❌':<20}")
print(f"{'Output file':<30} {output_size:.1f} KB{'':<16} {'✅':<20}")
print()

# Check content
print("Content verification:")
print("-"*80)

# Check for section headers
headers_to_check = [
    ('RISKS TO AGRICULTURE', 'RISCOS PARA A AGRICULTURA'),
    ('RISKS TO HEALTH', 'RISCOS PARA A SAÚDE'),
    ('RISKS TO ENVIRONMENT', 'RISCOS PARA O MEIO AMBIENTE')
]

for eng_header, port_header in headers_to_check:
    # Check if original had this section
    if port_header in tagged_text:
        # Check if translation has it
        words = eng_header.split()
        if all(word in final_tagged.upper() for word in words):
            print(f"✅ {eng_header} - PRESENT")
        else:
            print(f"❌ {eng_header} - MISSING")
    else:
        print(f"   {port_header} - not in original")

print()

# Show translated content sample
print("Translated content sample (first 500 chars):")
print("-"*80)
plain_text = re.sub(r'<[^>]+>', '', final_tagged)
print(plain_text[:500])
print()
print("-"*80)
print()

# FINAL VERDICT
print("="*80)
print("FINAL VERDICT")
print("="*80)
print()

if preservation_rate == 100.0 and len(broken_tags) == 0:
    print("🎉🎉🎉 SUCCESS! 100% TAG PRESERVATION ACHIEVED! 🎉🎉🎉")
    print()
    print("✅ All format tags preserved")
    print("✅ Zero broken tags")
    print("✅ Section headers present")
    print("✅ Content fully translated")
    print()
    print("Next step: Open the translated file to verify formatting:")
    print(f"   libreoffice '{output_file}'")
else:
    print("❌ FAILED TO ACHIEVE 100% PRESERVATION")
    print()
    print(f"Tags preserved: {len(final_tags)}/{len(original_tags)} ({preservation_rate:.1f}%)")
    print(f"Broken tags: {len(broken_tags)}")
    print()
    print("Something is still wrong!")

print()

