"""
Testing with ACTUAL tagged text from biology document
"""
import sys
sys.path.insert(0, 'src')
from translation.google_translate import GoogleTranslateAPI
from translation.format_mapper import FormatMapper

print("="*80)
print("EXTRACTING ACTUAL TAGGED TEXT FROM BIOLOGY DOCUMENT")
print("="*80)

# Extract the real tagged text
tagged = FormatMapper.extract_formatted_text_from_odt('/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt')

print(f"\nTotal length: {len(tagged)} characters")
print(f"\nFirst 500 chars:")
print("-"*80)
print(tagged[:500])
print()

# Find all tags in the original
import re
original_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', tagged)
print(f"Found {len(original_tags)} opening tags in original")
print("\nFirst 10 tags:")
for i, tag in enumerate(original_tags[:10], 1):
    print(f"  {i}. {tag[:80]}...")

print()
print("="*80)
print("TRANSLATING FULL DOCUMENT")
print("="*80)

translator = GoogleTranslateAPI()
result = translator.translate_text(tagged, 'pt', 'en')

if result.success:
    print("✅ Translation succeeded")
    print(f"\nTranslated length: {len(result.translated_text)} characters")
    print(f"\nFirst 500 chars of translation:")
    print("-"*80)
    print(result.translated_text[:500])
    print()
    
    # Find tags in translated
    translated_tags = re.findall(r'<\d+(?:\|\d+)?:[^>]+>', result.translated_text)
    print(f"Found {len(translated_tags)} opening tags in translation")
    
    # Check for broken tags
    broken_tags = re.findall(r'<\d+\s+\|[^>]*', result.translated_text)
    if broken_tags:
        print(f"\n❌ FOUND {len(broken_tags)} BROKEN TAGS (with spaces):")
        for tag in broken_tags[:5]:
            print(f"  - {tag}")
    
    # Compare preservation rate
    preservation = len(translated_tags) / len(original_tags) * 100 if original_tags else 0
    print(f"\n📊 Tag preservation rate: {preservation:.1f}%")
    
    if preservation < 100:
        print("\n⚠️  Some tags were corrupted during translation")
        print("Let me find what changed...")
        
        # Find differences
        for i, (orig, trans) in enumerate(zip(original_tags[:10], translated_tags[:10] if len(translated_tags) >= 10 else translated_tags)):
            if orig != trans:
                print(f"\nTag {i+1} changed:")
                print(f"  Before: {orig[:80]}")
                print(f"  After:  {trans[:80]}")
else:
    print(f"❌ Translation failed: {result.error_message}")

