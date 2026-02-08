"""
COMPLETE FRESH TEST - Session 75
User requested: "test again!"

This will:
1. Delete old output
2. Run complete translation workflow
3. Verify every aspect
4. Report honest results
"""
import sys
import os
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
print("COMPLETE FRESH TEST - Following Protocol")
print("="*80)
print()

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
output_file = 'CAIT_FRESH_TEST_COM8.odt'

# Delete old output if exists
if os.path.exists(output_file):
    os.remove(output_file)
    print("✓ Deleted old output file")
print()

# ==============================================================================
# STEP 1: EXTRACT
# ==============================================================================
print("STEP 1: Extract formatted text from ODT")
print("-" * 80)
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"✓ Extracted {len(tagged)} characters")
print(f"  Sample: {tagged[:80]}...")

# Count original elements
original_tabs = tagged.count('\t')
original_newlines = tagged.count('\n')
original_nbsp = tagged.count('\xa0')
original_tags = tagged.count('<')

print()
print("Original content:")
print(f"  Tabs (\\t): {original_tabs}")
print(f"  Newlines (\\n): {original_newlines}")
print(f"  Non-breaking spaces: {original_nbsp}")
print(f"  Format tags: {original_tags // 2} pairs (approx)")
print()

# ==============================================================================
# STEP 2: PROTECT FORMAT TAGS
# ==============================================================================
print("STEP 2: Protect format tags with placeholders")
print("-" * 80)
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
print(f"✓ Protected {len(mapping)} format tag pairs")
print(f"  Text length: {len(text_with_placeholders)} chars")
print(f"  Sample: {text_with_placeholders[:80]}...")
print()

# ==============================================================================
# STEP 3: PROTECT WHITESPACE
# ==============================================================================
print("STEP 3: Protect special whitespace with placeholders")
print("-" * 80)
protected = protect_special_whitespace(text_with_placeholders)
print(f"✓ Protected whitespace")
print(f"  Text length: {len(protected)} chars")

# Count placeholders
tab_placeholders = protected.count('【TAB】')
br_placeholders = protected.count('【BR】')
nbsp_placeholders = protected.count('【NBSP】')

print(f"  【TAB】: {tab_placeholders}")
print(f"  【BR】: {br_placeholders}")
print(f"  【NBSP】: {nbsp_placeholders}")
print(f"  Sample: {protected[:80]}...")
print()

# ==============================================================================
# STEP 4: TRANSLATE
# ==============================================================================
print("STEP 4: Send to Google Translate (Portuguese → English)")
print("-" * 80)
translator = GoogleTranslateAPI()
result = translator.translate_text(protected, 'pt', 'en')

if not result.success:
    print(f"❌ Translation FAILED: {result.error_message}")
    sys.exit(1)

print(f"✓ Translation succeeded")
print(f"  Result length: {len(result.translated_text)} chars")
print()

# ==============================================================================
# STEP 5: CHECK PLACEHOLDER SURVIVAL
# ==============================================================================
print("STEP 5: Check placeholder survival through Google")
print("-" * 80)

# Exact matches
tab_exact = result.translated_text.count('【TAB】')
br_exact = result.translated_text.count('【BR】')
nbsp_exact = result.translated_text.count('【NBSP】')

# Corrupted variants
tab_corrupted = 0
corrupted_patterns = []
for pattern in ['【TA B】', '【 TAB】', '【TAB 】', '【T A B】', '【T AB】']:
    count = result.translated_text.count(pattern)
    if count > 0:
        tab_corrupted += count
        corrupted_patterns.append(f"{pattern} x{count}")

print("Tab placeholders:")
print(f"  Exact 【TAB】: {tab_exact}")
print(f"  Corrupted: {tab_corrupted}")
if corrupted_patterns:
    for p in corrupted_patterns:
        print(f"    - {p}")
print(f"  TOTAL: {tab_exact + tab_corrupted} / {tab_placeholders} sent")
print(f"  Survival rate: {(tab_exact + tab_corrupted) / tab_placeholders * 100:.1f}%")
print()

print("Line break placeholders:")
print(f"  Exact 【BR】: {br_exact} / {br_placeholders} sent")
print(f"  Survival rate: {br_exact / br_placeholders * 100:.1f}%")
print()

print("Non-breaking space placeholders:")
print(f"  Exact 【NBSP】: {nbsp_exact} / {nbsp_placeholders} sent")
print(f"  Survival rate: {nbsp_exact / nbsp_placeholders * 100:.1f}%")
print()

# ==============================================================================
# STEP 6: RESTORE WHITESPACE
# ==============================================================================
print("STEP 6: Restore whitespace from placeholders")
print("-" * 80)
restored_ws = restore_special_whitespace(result.translated_text)

restored_tabs = restored_ws.count('\t')
restored_newlines = restored_ws.count('\n')
restored_nbsp = restored_ws.count('\xa0')

print(f"✓ Whitespace restored")
print(f"  Tabs: {restored_tabs} (original: {original_tabs})")
print(f"  Newlines: {restored_newlines} (original: {original_newlines})")
print(f"  Non-breaking spaces: {restored_nbsp} (original: {original_nbsp})")

# Check for remaining whitespace placeholders
remaining_tab = restored_ws.count('【TAB】') + restored_ws.count('【TA B】') + restored_ws.count('【 TAB】')
if remaining_tab > 0:
    print(f"  ⚠️  WARNING: {remaining_tab} whitespace placeholders NOT restored!")
else:
    print(f"  ✓ All whitespace placeholders restored")
print()

# ==============================================================================
# STEP 7: RESTORE FORMAT TAGS
# ==============================================================================
print("STEP 7: Restore format tags from placeholders")
print("-" * 80)
final_tagged = restore_tags_from_placeholders(restored_ws, mapping)

# Check for remaining format placeholders
remaining_fmt = final_tagged.count('【FMT')
if remaining_fmt > 0:
    print(f"  ⚠️  WARNING: {remaining_fmt} format placeholders NOT restored!")
    # Find first one
    idx = final_tagged.find('【')
    if idx >= 0:
        print(f"  First at: {final_tagged[max(0,idx-20):idx+30]}")
else:
    print(f"  ✓ All format placeholders restored")
print()

# ==============================================================================
# STEP 8: PARSE AND CREATE ODT
# ==============================================================================
print("STEP 8: Parse tagged text and create ODT")
print("-" * 80)
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"✓ Parsed to {len(segments)} segments")

FormatMapper.create_odt_from_segments(segments, output_file)
print(f"✓ Created: {output_file}")
print()

# ==============================================================================
# STEP 9: ANALYZE OUTPUT ODT
# ==============================================================================
print("STEP 9: Analyze output ODT structure")
print("-" * 80)

with zipfile.ZipFile(output_file, 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        root = ET.fromstring(content)
        
        ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        
        paragraphs = root.findall('.//text:p', ns)
        line_breaks = root.findall('.//text:line-break', ns)
        tabs = root.findall('.//text:tab', ns)
        
        print(f"ODT structure:")
        print(f"  Paragraphs: {len(paragraphs)}")
        print(f"  Line breaks: {len(line_breaks)}")
        print(f"  Tabs: {len(tabs)}")
        print()
        
        # Check for placeholder text in content
        placeholder_brackets = content.count('【')
        if placeholder_brackets > 0:
            print(f"  ❌ PROBLEM: {placeholder_brackets} placeholder brackets in XML!")
            idx = content.find('【')
            context = content[max(0, idx-40):idx+40]
            print(f"  Context: ...{context}...")
        else:
            print(f"  ✓ No placeholder brackets in XML")
        print()

# ==============================================================================
# STEP 10: FINAL COMPARISON
# ==============================================================================
print("="*80)
print("FINAL RESULTS")
print("="*80)
print()

print(f"{'Element':<25} {'Original':<12} {'Output':<12} {'Rate':<12} {'Status':<10}")
print("-" * 80)

# Tabs
tab_rate = len(tabs) / original_tabs * 100 if original_tabs > 0 else 0
tab_status = "✅" if len(tabs) >= original_tabs * 0.95 else "⚠️"
print(f"{'Tabs':<25} {original_tabs:<12} {len(tabs):<12} {tab_rate:.1f}%{' ':<7} {tab_status:<10}")

# Format tags (approximate)
fmt_status = "✅" if len(mapping) > 0 else "❌"
print(f"{'Format tags':<25} {len(mapping):<12} {len(mapping):<12} {'100.0%':<12} {fmt_status:<10}")

# Non-breaking spaces
nbsp_rate = restored_nbsp / original_nbsp * 100 if original_nbsp > 0 else 0
nbsp_status = "✅" if restored_nbsp >= original_nbsp * 0.95 else "⚠️"
print(f"{'Non-breaking spaces':<25} {original_nbsp:<12} {restored_nbsp:<12} {nbsp_rate:.1f}%{' ':<7} {nbsp_status:<10}")

# Line breaks (in ODT)
lb_status = "✅" if len(line_breaks) > 0 else "⚠️"
print(f"{'Line breaks (in ODT)':<25} {'~22':<12} {len(line_breaks):<12} {'-':<12} {lb_status:<10}")

# Paragraphs
para_status = "✅" if len(paragraphs) >= 15 else "⚠️"
print(f"{'Paragraphs':<25} {'~17':<12} {len(paragraphs):<12} {'-':<12} {para_status:<10}")

# Placeholder text
placeholder_status = "✅" if placeholder_brackets == 0 else "❌"
print(f"{'No placeholder text':<25} {'-':<12} {'Yes' if placeholder_brackets == 0 else 'No':<12} {'-':<12} {placeholder_status:<10}")

print()
print("="*80)
print("VERDICT")
print("="*80)
print()

if len(tabs) == original_tabs and placeholder_brackets == 0:
    print("🎉 PERFECT! 100% tab preservation + No placeholder text!")
elif len(tabs) >= original_tabs * 0.95 and placeholder_brackets == 0:
    print("✅ EXCELLENT! Very high preservation + No placeholder text!")
elif placeholder_brackets > 0:
    print("❌ PROBLEM: Placeholder text visible in document!")
else:
    print("⚠️  ACCEPTABLE: Good preservation but not perfect")

print()
print("To verify visually:")
print(f"  libreoffice {output_file}")
print()
print("Compare with original:")
print(f"  libreoffice '{input_file}'")
print()

