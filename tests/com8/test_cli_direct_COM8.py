#!/usr/bin/env python3
"""
Direct CLI test - No GUI, just pure translation workflow
Tests the ACTUAL bug with user's file
"""

import sys
import os

# Setup paths
sys.path.insert(0, 'src')
os.environ['PYTHONPATH'] = os.path.abspath('src')

print("=" * 80)
print("CLI TEST - Direct Translation (Session 76.2)")
print("=" * 80)

# Import translation components
from translation.format_mapper import FormatMapper
from translation.google_translate import GoogleTranslateAPI
from translation.format_mapper import (
    replace_tags_with_placeholders,
    restore_tags_from_placeholders,
    protect_special_whitespace,
    restore_special_whitespace
)

input_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
output_file = "CAIT_CLI_TEST_FIXED_COM8.odt"

print(f"\n📄 Input:  {input_file}")
print(f"📄 Output: {output_file}")
print(f"🌐 Translation: Portuguese → English")
print()

try:
    # STEP 1: Extract formatted text
    print("Step 1: Extracting formatted text from ODT...")
    formatted_text = FormatMapper.extract_formatted_text_from_odt(input_file)
    print(f"  ✅ Extracted {len(formatted_text)} characters")
    
    # Count adjacent tags
    import re
    adjacent_count = len(re.findall(r'</\d+\|[^>]+><\d+\|[^>]+>', formatted_text))
    print(f"  ✅ Found {adjacent_count} adjacent tag pairs")
    
    # STEP 2: Protect format tags with placeholders
    print("\nStep 2: Protecting format tags with placeholders...")
    protected_text, tag_mapping = replace_tags_with_placeholders(formatted_text)
    
    paired = sum(1 for v in tag_mapping.values() if v.get('type') == 'paired')
    closing = sum(1 for v in tag_mapping.values() if v.get('type') == 'closing')
    opening = sum(1 for v in tag_mapping.values() if v.get('type') == 'opening')
    
    print(f"  ✅ Created {len(tag_mapping)} placeholders:")
    print(f"     - Paired: {paired}")
    print(f"     - Closing: {closing}")
    print(f"     - Opening: {opening}")
    
    # Verify no visible tags remain
    remaining = len(re.findall(r'</?[\d|:,\w]+>', protected_text))
    if remaining > 0:
        print(f"  ⚠️  WARNING: {remaining} tags not protected!")
    else:
        print(f"  ✅ All tags converted to placeholders")
    
    # STEP 3: Protect whitespace
    print("\nStep 3: Protecting special whitespace...")
    protected_text = protect_special_whitespace(protected_text)
    print("  ✅ Whitespace protected")
    
    # STEP 4: Translate
    print("\nStep 4: Translating with Google Translate API...")
    print("  ⏳ This may take 1-2 minutes...")
    
    api = GoogleTranslateAPI()
    result = api.translate_text(protected_text, "pt", "en")
    
    if not result.success:
        print(f"  ❌ Translation failed: {result.error_message}")
        sys.exit(1)
    
    translated_text = result.translated_text
    print(f"  ✅ Translation complete ({len(translated_text)} characters)")
    
    # STEP 5: Restore whitespace
    print("\nStep 5: Restoring whitespace...")
    translated_text = restore_special_whitespace(translated_text)
    print("  ✅ Whitespace restored")
    
    # STEP 6: Restore format tags
    print("\nStep 6: Restoring format tags from placeholders...")
    translated_text = restore_tags_from_placeholders(translated_text, tag_mapping)
    print("  ✅ Format tags restored")
    
    # CRITICAL CHECK: Look for visible tags or placeholders
    print("\n" + "=" * 80)
    print("CRITICAL CHECKS")
    print("=" * 80)
    
    # Check 1: Visible format tags (the original bug)
    visible_tags = re.findall(r'(?:^|[^<])</?[\d|:,\w]+>(?:[^>]|$)', translated_text)
    if visible_tags:
        print(f"\n❌ FOUND {len(visible_tags)} VISIBLE FORMAT TAG(S)!")
        print(f"   Examples: {visible_tags[:5]}")
        print("\n   BUG STILL PRESENT!")
    else:
        print(f"\n✅ NO visible format tags found!")
    
    # Check 2: Visible placeholders (should all be restored)
    visible_placeholders_unicode = re.findall(r'【[^】]*】', translated_text)
    visible_placeholders_ascii = re.findall(r'\[[FM][^]]*\]', translated_text)
    
    if visible_placeholders_unicode or visible_placeholders_ascii:
        total = len(visible_placeholders_unicode) + len(visible_placeholders_ascii)
        print(f"\n❌ FOUND {total} VISIBLE PLACEHOLDER(S)!")
        if visible_placeholders_unicode:
            print(f"   Unicode: {visible_placeholders_unicode[:5]}")
        if visible_placeholders_ascii:
            print(f"   ASCII: {visible_placeholders_ascii[:5]}")
        print("\n   RESTORATION INCOMPLETE!")
    else:
        print(f"✅ NO visible placeholders!")
    
    # STEP 7: Create ODT
    print("\n" + "=" * 80)
    print("Step 7: Creating ODT from translated segments...")
    segments = FormatMapper.parse_tagged_text(translated_text)
    print(f"  ✅ Parsed {len(segments)} segments")
    
    FormatMapper.create_odt_from_segments(segments, output_file)
    print(f"  ✅ Created: {output_file}")
    
    # STEP 8: Verify output file
    print("\nStep 8: Verifying output file...")
    import zipfile
    import xml.etree.ElementTree as ET
    
    with zipfile.ZipFile(output_file, 'r') as zf:
        content_xml = zf.read('content.xml').decode('utf-8')
    
    root = ET.fromstring(content_xml)
    ns = {
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
    }
    
    body = root.find('.//office:body/office:text', ns)
    paragraphs = body.findall('.//text:p', ns)
    
    print(f"  ✅ Output has {len(paragraphs)} paragraphs")
    
    # Scan for visible tags in final ODT
    bugs_found = 0
    for idx, p in enumerate(paragraphs, 1):
        text = ''.join(p.itertext())
        if re.search(r'</?\d+\|[\d:,\w]+>', text):
            bugs_found += 1
            print(f"  ❌ Paragraph {idx}: Visible tags found!")
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    if bugs_found == 0 and not visible_tags and not visible_placeholders_unicode and not visible_placeholders_ascii:
        print("\n🎉 SUCCESS! FIX WORKS!")
        print(f"   ✅ {adjacent_count} adjacent tag pairs handled correctly")
        print(f"   ✅ NO visible tags")
        print(f"   ✅ NO visible placeholders")
        print(f"   ✅ Output file clean")
    else:
        print("\n❌ FIX INCOMPLETE!")
        if bugs_found > 0:
            print(f"   ❌ {bugs_found} paragraphs with visible tags")
        if visible_tags:
            print(f"   ❌ Visible format tags in translated text")
        if visible_placeholders_unicode or visible_placeholders_ascii:
            print(f"   ❌ Visible placeholders not restored")
    
    print(f"\n📄 Output saved: {output_file}")
    print("   Open in LibreOffice to verify visually")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
