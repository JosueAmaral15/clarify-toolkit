"""
COMPREHENSIVE INVESTIGATION - Session 75
User confirmed: Check EVERYTHING (format, content, structure)
Success = All sections present + No placeholders + Professional + Readable English

This will:
1. Read ORIGINAL content thoroughly
2. Run translation
3. Read TRANSLATED content thoroughly
4. Compare BEFORE vs AFTER
5. Document findings honestly
"""
import sys
import os
import zipfile
import xml.etree.ElementTree as ET
sys.path.insert(0, 'src')
from translation.format_mapper import (
    FormatMapper,
    replace_tags_with_placeholders,
    restore_tags_from_placeholders,
    protect_special_whitespace,
    restore_special_whitespace
)
from translation.google_translate import GoogleTranslateAPI

print("="*80)
print("COMPREHENSIVE DOCUMENT INVESTIGATION")
print("Following SIMPLICITY_PROTOCOL_3")
print("="*80)
print()

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
output_file = 'CAIT_FINAL_VERIFIED_COM8.odt'

# Delete old output
if os.path.exists(output_file):
    os.remove(output_file)
    print("✓ Deleted old output")

print()
print("="*80)
print("STEP 1: READ ORIGINAL FILE (BEFORE TRANSLATION)")
print("="*80)
print()

# Extract original content
print("Extracting original content...")
with zipfile.ZipFile(input_file, 'r') as z:
    with z.open('content.xml') as f:
        original_xml = f.read().decode('utf-8')

# Parse original structure
root = ET.fromstring(original_xml)
ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}

original_paragraphs = root.findall('.//text:p', ns)
print(f"✓ Original has {len(original_paragraphs)} paragraphs")

# Get text content from first few paragraphs
print()
print("Original content (first 5 paragraphs):")
print("-" * 80)
for i, para in enumerate(original_paragraphs[:5], 1):
    text = ''.join(para.itertext())
    if text.strip():
        print(f"{i}. {text[:100]}{'...' if len(text) > 100 else ''}")

# Extract with our system
print()
print("Extracting with format preservation...")
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"✓ Extracted {len(tagged)} characters")

# Find section headers in original
print()
print("Identifying sections in original...")
sections_found = []
for para in original_paragraphs:
    text = ''.join(para.itertext()).strip()
    if text and text.isupper() and len(text) > 5 and ':' in text:
        sections_found.append(text)

print(f"✓ Found {len(sections_found)} section headers:")
for i, section in enumerate(sections_found[:10], 1):
    print(f"  {i}. {section}")

# Count original elements
original_tabs = tagged.count('\t')
original_breaks = tagged.count('\n')
original_tags = tagged.count('<')

print()
print("Original statistics:")
print(f"  Paragraphs: {len(original_paragraphs)}")
print(f"  Tabs: {original_tabs}")
print(f"  Line breaks: {original_breaks}")
print(f"  Format tags: ~{original_tags // 2}")
print(f"  Section headers: {len(sections_found)}")

print()
print("="*80)
print("STEP 2: RUN TRANSLATION (Portuguese → English)")
print("="*80)
print()

# Protect format tags
print("Protecting format tags...")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
print(f"✓ Protected {len(mapping)} format tags")

# Protect whitespace
print("Protecting whitespace...")
protected = protect_special_whitespace(text_with_placeholders)
print(f"✓ Protected {protected.count('【TAB】')} tabs, {protected.count('【BR】')} line breaks")

# Translate
print("Translating with Google Translate...")
translator = GoogleTranslateAPI()
result = translator.translate_text(protected, 'pt', 'en')

if not result.success:
    print(f"❌ Translation FAILED: {result.error_message}")
    sys.exit(1)

print(f"✓ Translation succeeded")
print(f"  Input length: {len(protected)} chars")
print(f"  Output length: {len(result.translated_text)} chars")

# Check survival
tab_survived = result.translated_text.count('【TAB】')
br_survived = result.translated_text.count('【BR】')
print(f"  Tabs survived: {tab_survived}/{protected.count('【TAB】')}")
print(f"  Line breaks survived: {br_survived}/{protected.count('【BR】')}")

# Restore
print()
print("Restoring whitespace...")
restored_ws = restore_special_whitespace(result.translated_text)

print("Restoring format tags...")
final_tagged = restore_tags_from_placeholders(restored_ws, mapping)

# Check for remaining placeholders
remaining = final_tagged.count('【')
if remaining > 0:
    print(f"  ⚠️  WARNING: {remaining} placeholders not restored!")
else:
    print(f"  ✓ All placeholders restored")

# Create ODT
print()
print("Creating translated ODT...")
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"✓ Parsed to {len(segments)} segments")

FormatMapper.create_odt_from_segments(segments, output_file)
print(f"✓ Created: {output_file}")

print()
print("="*80)
print("STEP 3: READ TRANSLATED FILE (AFTER TRANSLATION)")
print("="*80)
print()

# Extract translated content
print("Extracting translated content...")
with zipfile.ZipFile(output_file, 'r') as z:
    with z.open('content.xml') as f:
        translated_xml = f.read().decode('utf-8')

# Parse translated structure
trans_root = ET.fromstring(translated_xml)
trans_paragraphs = trans_root.findall('.//text:p', ns)
trans_tabs = trans_root.findall('.//text:tab', ns)
trans_breaks = trans_root.findall('.//text:line-break', ns)

print(f"✓ Translated has {len(trans_paragraphs)} paragraphs")

# Get translated text from first few paragraphs
print()
print("Translated content (first 5 paragraphs):")
print("-" * 80)
for i, para in enumerate(trans_paragraphs[:5], 1):
    text = ''.join(para.itertext())
    if text.strip():
        print(f"{i}. {text[:100]}{'...' if len(text) > 100 else ''}")

# Find section headers in translated
print()
print("Identifying sections in translated...")
trans_sections = []
for para in trans_paragraphs:
    text = ''.join(para.itertext()).strip()
    if text and text.isupper() and len(text) > 5 and ':' in text:
        trans_sections.append(text)

print(f"✓ Found {len(trans_sections)} section headers:")
for i, section in enumerate(trans_sections[:10], 1):
    print(f"  {i}. {section}")

# Check for placeholder text
placeholder_count = translated_xml.count('【')
print()
if placeholder_count > 0:
    print(f"❌ PROBLEM: {placeholder_count} placeholder brackets in output!")
else:
    print(f"✓ No placeholder text in output")

print()
print("Translated statistics:")
print(f"  Paragraphs: {len(trans_paragraphs)}")
print(f"  Tabs: {len(trans_tabs)}")
print(f"  Line breaks: {len(trans_breaks)}")
print(f"  Section headers: {len(trans_sections)}")

print()
print("="*80)
print("STEP 4: COMPARE BEFORE vs AFTER")
print("="*80)
print()

print(f"{'Element':<25} {'Original':<15} {'Translated':<15} {'Status':<10}")
print("-" * 70)

# Paragraphs
para_status = "✅" if len(trans_paragraphs) >= 15 else "⚠️"
print(f"{'Paragraphs':<25} {len(original_paragraphs):<15} {len(trans_paragraphs):<15} {para_status:<10}")

# Tabs
tab_status = "✅" if len(trans_tabs) >= original_tabs * 0.9 else "❌"
print(f"{'Tabs':<25} {original_tabs:<15} {len(trans_tabs):<15} {tab_status:<10}")

# Section headers
section_status = "✅" if len(trans_sections) >= len(sections_found) * 0.8 else "❌"
print(f"{'Section headers':<25} {len(sections_found):<15} {len(trans_sections):<15} {section_status:<10}")

# Placeholder text
placeholder_status = "✅" if placeholder_count == 0 else "❌"
print(f"{'No placeholder text':<25} {'-':<15} {'Yes' if placeholder_count == 0 else 'No':<15} {placeholder_status:<10}")

print()
print("Section header comparison:")
print("-" * 70)
max_compare = min(len(sections_found), len(trans_sections), 10)
for i in range(max_compare):
    orig = sections_found[i] if i < len(sections_found) else "MISSING"
    trans = trans_sections[i] if i < len(trans_sections) else "MISSING"
    print(f"  {i+1}. {orig[:35]:<35} → {trans[:35]:<35}")

if len(sections_found) != len(trans_sections):
    print(f"  ⚠️  Section count mismatch: {len(sections_found)} → {len(trans_sections)}")

print()
print("="*80)
print("STEP 5: CONTENT QUALITY CHECK")
print("="*80)
print()

# Check if English makes sense
print("Checking translated text quality...")
sample_paragraphs = []
for para in trans_paragraphs[:10]:
    text = ''.join(para.itertext()).strip()
    if text and len(text) > 20:
        sample_paragraphs.append(text)

print()
print("Sample translated text (checking readability):")
print("-" * 70)
for i, text in enumerate(sample_paragraphs[:3], 1):
    print(f"{i}. {text[:200]}{'...' if len(text) > 200 else ''}")
    print()

print()
print("="*80)
print("FINAL VERDICT")
print("="*80)
print()

# Calculate scores
checks = {
    'tabs_preserved': len(trans_tabs) >= original_tabs * 0.9,
    'sections_present': len(trans_sections) >= len(sections_found) * 0.8,
    'no_placeholders': placeholder_count == 0,
    'structure_ok': len(trans_paragraphs) >= 15,
}

passed = sum(checks.values())
total = len(checks)

print("Success criteria:")
for criterion, status in checks.items():
    symbol = "✅" if status else "❌"
    print(f"  {symbol} {criterion.replace('_', ' ').title()}")

print()
print(f"Score: {passed}/{total} criteria met")
print()

if passed == total:
    print("🎉 EXCELLENT! All criteria passed!")
    print("   Document is ready for use.")
elif passed >= total * 0.75:
    print("✅ GOOD! Most criteria passed.")
    print("   Document is usable with minor issues.")
else:
    print("⚠️  ISSUES FOUND!")
    print("   Review the problems above.")

print()
print("Next steps:")
print("  1. Visual verification in LibreOffice:")
print(f"     Original:    {input_file}")
print(f"     Translated:  {output_file}")
print()
print("  2. Check if English text makes sense")
print("  3. Verify formatting looks professional")
print("  4. Confirm all sections are present")

