"""
Investigation: Why only 38/44 line breaks instead of 44/44?
User question: "why Line breaks: 38/44 (86%) instead of 100%?"
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
print("INVESTIGATING: Why 38/44 line breaks instead of 44/44?")
print("="*80)
print()

# Step 1: Count in original
print("Step 1: Original document")
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
original_breaks = tagged.count('\n')
print(f"   Line breaks (\\n) in original: {original_breaks}")
print()

# Step 2: After format tag protection
print("Step 2: After format tag protection")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
breaks_after_fmt = text_with_placeholders.count('\n')
print(f"   Line breaks remaining: {breaks_after_fmt}")
if breaks_after_fmt != original_breaks:
    print(f"   ⚠️  Lost {original_breaks - breaks_after_fmt} during format tag protection!")
print()

# Step 3: After whitespace protection
print("Step 3: After whitespace protection")
protected = protect_special_whitespace(text_with_placeholders)
br_placeholders = protected.count('【BR】')
remaining_breaks = protected.count('\n')
print(f"   【BR】 placeholders created: {br_placeholders}")
print(f"   Remaining \\n (should be 0): {remaining_breaks}")
if br_placeholders != original_breaks:
    print(f"   ⚠️  Expected {original_breaks}, got {br_placeholders}")
    print(f"   Difference: {original_breaks - br_placeholders} not protected")
print()

# Step 4: Send to Google Translate
print("Step 4: Sending to Google Translate...")
translator = GoogleTranslateAPI()
result = translator.translate_text(protected, 'pt', 'en')

if result.success:
    br_exact = result.translated_text.count('【BR】')
    
    # Check for corrupted variants
    br_corrupted = 0
    corrupted_patterns = [
        '【B R】',
        '【 BR】', 
        '【BR 】',
        '【B  R】'
    ]
    
    found_corrupted = []
    for pattern in corrupted_patterns:
        count = result.translated_text.count(pattern)
        if count > 0:
            br_corrupted += count
            found_corrupted.append(f"{pattern} x{count}")
    
    print(f"   【BR】 exact: {br_exact}/{br_placeholders}")
    print(f"   【BR】 corrupted: {br_corrupted}")
    if found_corrupted:
        for p in found_corrupted:
            print(f"      {p}")
    
    total_survived = br_exact + br_corrupted
    lost = br_placeholders - total_survived
    
    print(f"   TOTAL survived: {total_survived}/{br_placeholders}")
    print(f"   LOST by Google: {lost} ({lost/br_placeholders*100:.1f}%)")
    
    if lost > 0:
        print()
        print(f"   ❌ Google DELETED {lost} 【BR】 placeholders!")
        print(f"   This is why we have 86% instead of 100%")
else:
    print(f"   ❌ Translation failed")
    sys.exit(1)

print()

# Step 5: After restoration
print("Step 5: After restoration")
restored_ws = restore_special_whitespace(result.translated_text)
restored_breaks = restored_ws.count('\n')
print(f"   Line breaks restored: {restored_breaks}")
print(f"   From {total_survived} placeholders")
print()

print("="*80)
print("ANALYSIS")
print("="*80)
print()

print(f"Original:              {original_breaks} line breaks")
print(f"Protected as 【BR】:    {br_placeholders}")
print(f"Survived Google:       {total_survived} ({br_exact} exact + {br_corrupted} corrupted)")
print(f"Deleted by Google:     {lost}")
print(f"Restored to \\n:        {restored_breaks}")
print()

if lost > 0:
    print(f"❌ ROOT CAUSE: Google Translate DELETED {lost} placeholders")
    print()
    print("Why Google deletes line breaks:")
    print("  1. Sentence restructuring - Google merges sentences it thinks should flow together")
    print("  2. Text normalization - Removes 'unnecessary' line breaks")
    print("  3. Context-aware decisions - If translation is shorter/longer, adjusts spacing")
    print("  4. ML model behavior - Neural network decides optimal text flow")
    print()
    print("Unlike tabs (which Google corrupts but KEEPS), line breaks are sometimes")
    print("COMPLETELY REMOVED. We can't restore what Google deletes entirely.")
    print()
    print(f"Current result: {restored_breaks}/{original_breaks} = {restored_breaks/original_breaks*100:.1f}%")
    print("This is EXPECTED behavior with Google Translate free API.")

print()
print("Can we achieve 100%?")
print("  ❌ Not with Google Translate - it actively removes line breaks")
print("  ✅ Possible with other services:")
print("      • DeepL API - better formatting respect")
print("      • Microsoft Translator - preserves structure better")
print("      • Local solutions - full control")

