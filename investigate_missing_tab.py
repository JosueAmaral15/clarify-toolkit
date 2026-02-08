"""
Investigation: Why only 13/14 tabs instead of 14/14?
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

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'

print("="*80)
print("INVESTIGATING: Why 13/14 tabs instead of 14/14?")
print("="*80)
print()

# Step 1: Count tabs in original
print("Step 1: Original document")
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
original_tabs = tagged.count('\t')
print(f"   Tabs in original: {original_tabs}")
print()

# Step 2: After format tag protection
print("Step 2: After format tag protection")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
tabs_after_fmt = text_with_placeholders.count('\t')
print(f"   Tabs remaining: {tabs_after_fmt}")
if tabs_after_fmt != original_tabs:
    print(f"   ⚠️  Lost {original_tabs - tabs_after_fmt} tabs during format tag protection!")
print()

# Step 3: After whitespace protection
print("Step 3: After whitespace protection")
protected = protect_special_whitespace(text_with_placeholders)
tab_placeholders = protected.count('【TAB】')
print(f"   【TAB】 placeholders created: {tab_placeholders}")
if tab_placeholders != original_tabs:
    print(f"   ⚠️  Expected {original_tabs}, got {tab_placeholders}")
    print(f"   Difference: {original_tabs - tab_placeholders} tabs not protected")
print()

# Step 4: Send to Google Translate
print("Step 4: Sending to Google Translate (pt→en)...")
translator = GoogleTranslateAPI()
result = translator.translate_text(protected, 'pt', 'en')

if result.success:
    tab_survived = result.translated_text.count('【TAB】')
    print(f"   【TAB】 survived translation: {tab_survived}/{tab_placeholders}")
    
    if tab_survived < tab_placeholders:
        lost = tab_placeholders - tab_survived
        print(f"   ❌ Google DELETED {lost} tab placeholder(s)!")
        print(f"   Loss rate: {lost/tab_placeholders*100:.1f}%")
    else:
        print(f"   ✅ All placeholders survived!")
else:
    print(f"   ❌ Translation failed: {result.error_message}")
    sys.exit(1)

print()

# Step 5: Check for corrupted variants
print("Step 5: Checking for corrupted tab placeholders...")
corrupted_variants = [
    ('【TA B】', 'space between letters'),
    ('【 TAB】', 'space before'),
    ('【TAB 】', 'space after'),
    ('【T AB】', 'space in middle'),
    ('【T A B】', 'multiple spaces'),
]

found_corrupted = 0
for variant, description in corrupted_variants:
    count = result.translated_text.count(variant)
    if count > 0:
        found_corrupted += count
        print(f"   Found {count}x {variant} ({description})")

if found_corrupted > 0:
    print(f"   Total corrupted: {found_corrupted}")
    print(f"   Total placeholders (exact + corrupted): {tab_survived + found_corrupted}")
else:
    print(f"   No corrupted variants found")

print()

# Step 6: Restoration
print("Step 6: After restoration...")
restored_ws = restore_special_whitespace(result.translated_text)
restored_tabs = restored_ws.count('\t')
print(f"   Tabs restored: {restored_tabs}")
print()

print("="*80)
print("ANALYSIS")
print("="*80)
print()

print(f"Original tabs:           {original_tabs}")
print(f"Protected as 【TAB】:     {tab_placeholders}")
print(f"Survived Google:         {tab_survived}")
print(f"Corrupted variants:      {found_corrupted}")
print(f"Total after Google:      {tab_survived + found_corrupted}")
print(f"Restored to \\t:          {restored_tabs}")
print()

if original_tabs == tab_placeholders == tab_survived + found_corrupted == restored_tabs:
    print("✅ 100% PERFECT! All tabs preserved!")
elif restored_tabs < original_tabs:
    lost = original_tabs - restored_tabs
    print(f"❌ Lost {lost} tab(s)")
    print()
    print("Root cause:")
    if tab_placeholders < original_tabs:
        print(f"   • {original_tabs - tab_placeholders} tabs not protected (bug in protect function)")
    if tab_survived + found_corrupted < tab_placeholders:
        print(f"   • Google deleted {tab_placeholders - (tab_survived + found_corrupted)} placeholder(s)")
    if restored_tabs < tab_survived + found_corrupted:
        print(f"   • {(tab_survived + found_corrupted) - restored_tabs} placeholders not restored (bug in restore function)")

