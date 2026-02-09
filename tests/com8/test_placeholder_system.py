"""
Phase 1: Create and test placeholder replacement system
Session 75 - COM8
"""
import re
from typing import Dict, Tuple

def replace_tags_with_placeholders(tagged_text: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Replace format tags with Unicode placeholders.
    
    Args:
        tagged_text: Text with format tags like <113|65536:Arial|0,0>text</113|65536>
        
    Returns:
        (text_with_placeholders, mapping)
        - text_with_placeholders: Text with 【FMT001】text【/FMT001】
        - mapping: Dict mapping IDs to original tag info
    """
    mapping = {}
    counter = 1
    result = tagged_text
    
    # Pattern to match complete tag pairs: <opening>text</closing>
    # Captures: (opening_tag_content, text_inside, closing_tag_content)
    pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]*?)</(\d+(?:\|\d+)?)>'
    
    def replace_match(match):
        nonlocal counter
        opening_tag = match.group(1)
        text_inside = match.group(2)
        closing_tag = match.group(3)
        
        # Generate unique ID
        fmt_id = f"FMT{counter:03d}"
        counter += 1
        
        # Store original tag info
        mapping[fmt_id] = {
            'opening': f'<{opening_tag}>',
            'closing': f'</{closing_tag}>',
            'original_text': text_inside
        }
        
        # Return placeholder
        return f'【{fmt_id}】{text_inside}【/{fmt_id}】'
    
    # Replace all tag pairs with placeholders
    result = re.sub(pattern, replace_match, result)
    
    return result, mapping


def restore_tags_from_placeholders(translated_text: str, mapping: Dict[str, Dict[str, str]]) -> str:
    """
    Restore original format tags from placeholders.
    
    Args:
        translated_text: Text with 【FMT001】translated text【/FMT001】
        mapping: Dict mapping IDs to original tag info
        
    Returns:
        Text with restored tags: <113|65536:Arial|0,0>translated text</113|65536>
    """
    result = translated_text
    
    # Pattern to match placeholder pairs: 【FMT001】text【/FMT001】
    pattern = r'【(FMT\d+)】(.*?)【/\1】'
    
    def restore_match(match):
        fmt_id = match.group(1)
        translated_text_inside = match.group(2)
        
        if fmt_id not in mapping:
            # Placeholder not in mapping - keep as is (shouldn't happen)
            return match.group(0)
        
        tag_info = mapping[fmt_id]
        opening = tag_info['opening']
        closing = tag_info['closing']
        
        # Restore with original tags and translated text
        return f'{opening}{translated_text_inside}{closing}'
    
    # Replace all placeholders with original tags
    result = re.sub(pattern, restore_match, result, flags=re.DOTALL)
    
    return result


# ============================================================================
# TESTS
# ============================================================================

print("="*80)
print("PHASE 1: Testing Placeholder System")
print("="*80)
print()

# Test 1: Simple tag
print("Test 1: Simple single tag")
print("-"*80)
original = "<113|65536:525252,9,Arial|0,0>RISCOS PARA A AGRICULTURA: </113|65536>"
print(f"Original: {original}")

placeholders, mapping = replace_tags_with_placeholders(original)
print(f"With placeholders: {placeholders}")
print(f"Mapping: {mapping}")

# Simulate translation (just convert to uppercase for testing)
translated_placeholders = placeholders.upper()
print(f"After 'translation': {translated_placeholders}")

restored = restore_tags_from_placeholders(translated_placeholders, mapping)
print(f"Restored: {restored}")

success = '<113|65536:525252,9,Arial|0,0>RISCOS PARA A AGRICULTURA: </113|65536>' in original
print(f"✅ PASS" if restored.startswith('<113') else "❌ FAIL")
print()

# Test 2: Multiple tags
print("Test 2: Multiple adjacent tags")
print("-"*80)
original = "<113|65536:525252,9,Arial|0,0>Header</113|65536><112|65536:525252,9,Arial|0,0>Body text here</112|65536>"
print(f"Original: {original}")

placeholders, mapping = replace_tags_with_placeholders(original)
print(f"With placeholders: {placeholders}")
print(f"Number of mappings: {len(mapping)}")

translated_placeholders = placeholders.upper()
restored = restore_tags_from_placeholders(translated_placeholders, mapping)
print(f"Restored: {restored}")
print(f"✅ PASS" if '<113' in restored and '<112' in restored else "❌ FAIL")
print()

# Test 3: Real chunk 6 (the problematic one)
print("Test 3: Real chunk 6 that breaks with direct tags")
print("-"*80)
import sys
sys.path.insert(0, 'src')
from translation.format_mapper import FormatMapper

tagged = FormatMapper.extract_formatted_text_from_odt('/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt')
chunks = tagged.split('\n\n')
chunk6 = chunks[6]

print(f"Original length: {len(chunk6)} chars")
print(f"First 100 chars: {chunk6[:100]}")

placeholders, mapping = replace_tags_with_placeholders(chunk6)
print(f"\nWith placeholders: {placeholders[:150]}...")
print(f"Number of tags replaced: {len(mapping)}")

# Now translate with Google
from translation.google_translate import GoogleTranslateAPI
translator = GoogleTranslateAPI()

print("\nTranslating with placeholders...")
result = translator.translate_text(placeholders, 'pt', 'en')

if result.success:
    print("✅ Translation succeeded")
    print(f"Translated length: {len(result.translated_text)} chars")
    print(f"First 150 chars: {result.translated_text[:150]}...")
    
    # Check if placeholders survived
    placeholders_found = re.findall(r'【FMT\d+】', result.translated_text)
    print(f"\nPlaceholders in translation: {len(placeholders_found)}")
    print(f"Expected: {len(mapping)}")
    
    if len(placeholders_found) == len(mapping):
        print("✅ ALL PLACEHOLDERS SURVIVED!")
        
        # Restore tags
        final = restore_tags_from_placeholders(result.translated_text, mapping)
        print(f"\nRestored text length: {len(final)} chars")
        print(f"First 150 chars: {final[:150]}...")
        
        # Check for broken tags
        broken = re.findall(r'<\d+\s+\|', final)
        if broken:
            print(f"❌ FAIL: Still has broken tags: {broken}")
        else:
            print("✅ PASS: No broken tags!")
            
        # Count tags
        final_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', final)
        print(f"\nFinal tag count: {len(final_tags)}")
        print(f"Expected: {len(mapping)}")
        
        if len(final_tags) == len(mapping):
            print("✅✅✅ PERFECT: 100% TAG PRESERVATION!")
        else:
            print(f"⚠️  Mismatch: {len(final_tags)}/{len(mapping)} tags")
    else:
        print(f"❌ FAIL: Lost placeholders!")
else:
    print(f"❌ Translation failed: {result.error_message}")

print()
print("="*80)
print("PHASE 1 COMPLETE")
print("="*80)

