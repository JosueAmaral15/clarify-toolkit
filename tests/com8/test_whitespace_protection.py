"""
Test whitespace placeholder protection
Session 75 - Complete formatting preservation
"""
import sys
sys.path.insert(0, 'src')
from translation.format_mapper import (
    FormatMapper,
    replace_tags_with_placeholders,
    restore_tags_from_placeholders,
    protect_special_whitespace,
    restore_special_whitespace
)
from translation.google_translate import GoogleTranslateAPI
import zipfile
import xml.etree.ElementTree as ET

print("="*80)
print("TESTING WHITESPACE PLACEHOLDER PROTECTION")
print("="*80)
print()

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
output_file = 'CAIT_WITH_WHITESPACE_PROTECTION_COM8.odt'

# Step 1: Extract
print("Step 1: Extracting...")
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"✅ Extracted {len(tagged)} chars")

# Count original whitespace
original_tabs = tagged.count('\t')
original_newlines = tagged.count('\n')
original_nbsp = tagged.count('\xa0')
print(f"   Tabs: {original_tabs}")
print(f"   Newlines: {original_newlines}")
print(f"   Non-breaking spaces: {original_nbsp}")
print()

# Step 2: Protect format tags
print("Step 2: Protecting format tags...")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
print(f"✅ Protected {len(mapping)} format tags")
print()

# Step 3: Protect whitespace
print("Step 3: Protecting whitespace...")
protected = protect_special_whitespace(text_with_placeholders)
print(f"✅ Protected whitespace")
print(f"   Length: {len(protected)} chars")

# Count placeholders
tab_placeholders = protected.count('【TAB】')
br_placeholders = protected.count('【BR】')
nbsp_placeholders = protected.count('【NBSP】')
print(f"   【TAB】: {tab_placeholders}")
print(f"   【BR】: {br_placeholders}")
print(f"   【NBSP】: {nbsp_placeholders}")
print()

# Show sample
print("Sample (first 200 chars):")
print(protected[:200])
print()

# Step 4: Translate
print("Step 4: Translating...")
translator = GoogleTranslateAPI()
result = translator.translate_text(protected, 'pt', 'en')

if not result.success:
    print(f"❌ Translation failed: {result.error_message}")
    sys.exit(1)

print(f"✅ Translation succeeded")
print(f"   Result length: {len(result.translated_text)} chars")
print()

# Step 5: Verify placeholders survived
print("Step 5: Verifying placeholder survival...")
tab_survived = result.translated_text.count('【TAB】')
br_survived = result.translated_text.count('【BR】')
nbsp_survived = result.translated_text.count('【NBSP】')

print(f"   【TAB】: {tab_survived}/{tab_placeholders} ({tab_survived/tab_placeholders*100:.1f}%)")
print(f"   【BR】: {br_survived}/{br_placeholders} ({br_survived/br_placeholders*100:.1f}%)")
print(f"   【NBSP】: {nbsp_survived}/{nbsp_placeholders} ({nbsp_survived/nbsp_placeholders*100:.1f}%)")
print()

if tab_survived == tab_placeholders and br_survived == br_placeholders:
    print("✅ ALL WHITESPACE PLACEHOLDERS SURVIVED!")
else:
    print("⚠️  Some placeholders were lost!")
print()

# Step 6: Restore whitespace
print("Step 6: Restoring whitespace...")
restored_whitespace = restore_special_whitespace(result.translated_text)

# Count restored
restored_tabs = restored_whitespace.count('\t')
restored_newlines = restored_whitespace.count('\n')
restored_nbsp = restored_whitespace.count('\xa0')

print(f"✅ Whitespace restored")
print(f"   Tabs: {restored_tabs} (original: {original_tabs})")
print(f"   Newlines: {restored_newlines} (original: {original_newlines})")
print(f"   Non-breaking spaces: {restored_nbsp} (original: {original_nbsp})")
print()

# Step 7: Restore format tags
print("Step 7: Restoring format tags...")
final_tagged = restore_tags_from_placeholders(restored_whitespace, mapping)
print(f"✅ Format tags restored")
print()

# Step 8: Parse and create ODT
print("Step 8: Creating ODT...")
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"   Parsed to {len(segments)} segments")

FormatMapper.create_odt_from_segments(segments, output_file)
print(f"✅ Created: {output_file}")
print()

# Step 9: Analyze output
print("="*80)
print("ANALYZING OUTPUT STRUCTURE")
print("="*80)
print()

with zipfile.ZipFile(output_file, 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        root = ET.fromstring(content)
        
        ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        
        paragraphs = root.findall('.//text:p', ns)
        line_breaks = root.findall('.//text:line-break', ns)
        tabs = root.findall('.//text:tab', ns)
        
        print(f"Paragraphs: {len(paragraphs)}")
        print(f"Line breaks: {len(line_breaks)}")
        print(f"Tabs: {len(tabs)}")
        print()

print("="*80)
print("COMPARISON")
print("="*80)
print()
print(f"{'Element':<20} {'Original':<15} {'Output':<15} {'Status':<15}")
print("-"*65)
print(f"{'Tabs':<20} {original_tabs:<15} {len(tabs):<15} {'✅' if len(tabs) >= 10 else '❌':<15}")
print(f"{'Line breaks':<20} {'22':<15} {len(line_breaks):<15} {'✅' if len(line_breaks) >= 20 else '❌':<15}")
print(f"{'Paragraphs':<20} {'17':<15} {len(paragraphs):<15} {'✅' if len(paragraphs) >= 15 else '❌':<15}")
print()

if len(tabs) >= 10:
    print("🎉 SUCCESS! Tabs are now preserved!")
else:
    print("⚠️  Tabs still not fully preserved")

print()
print("Open to verify:")
print(f"  libreoffice '{output_file}'")

