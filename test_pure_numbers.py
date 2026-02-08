"""
DEEP INVESTIGATION: Does Google Translate modify pure number tags?
Testing various tag formats to see what gets corrupted
"""
import sys
sys.path.insert(0, 'src')
from translation.google_translate import GoogleTranslateAPI

translator = GoogleTranslateAPI()

print("="*80)
print("TESTING: Does Google Translate corrupt PURE NUMBER tags?")
print("="*80)
print()

# Test cases with ONLY numbers (no text metadata)
test_cases = [
    {
        "name": "Pure numbers - simple",
        "text": "This is <113|65536>bold text</113|65536> in a sentence.",
    },
    {
        "name": "Pure numbers - multiple tags",
        "text": "<113|65536>First</113|65536> normal <97|66048>second</97|66048> text.",
    },
    {
        "name": "Pure numbers - complex",
        "text": "Test <113|65536>text</113|65536> with <97|66048>multiple</97|66048> <99|66048>formats</99|66048> here.",
    },
    {
        "name": "With text metadata (current format)",
        "text": "This is <113|65536:525252,9,Arial|0,0>bold text</113|65536> sentence.",
    },
    {
        "name": "Numbers with colons only",
        "text": "Test <113:65536>bold</113:65536> format.",
    },
    {
        "name": "Just numbers no separator",
        "text": "Simple <11365536>text</11365536> here.",
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: {test['name']}")
    print("-"*80)
    print(f"Input:  {test['text']}")
    
    # Translate
    result = translator.translate_text(test['text'], 'pt', 'en')
    
    if result.success:
        print(f"Output: {result.translated_text}")
        
        # Check if tags are preserved
        import re
        input_tags = re.findall(r'<[^>]+>', test['text'])
        output_tags = re.findall(r'<[^>]+>', result.translated_text)
        
        if input_tags == output_tags:
            print("✅ ALL TAGS PERFECTLY PRESERVED!")
        else:
            print(f"❌ CORRUPTION DETECTED!")
            print(f"   Input tags:  {input_tags}")
            print(f"   Output tags: {output_tags}")
            
            # Show what changed
            missing = [t for t in input_tags if t not in output_tags]
            broken = [t for t in output_tags if t not in input_tags]
            if missing:
                print(f"   Missing: {missing}")
            if broken:
                print(f"   Broken:  {broken}")
    else:
        print(f"❌ Translation failed: {result.error_message}")
    
    print()

print("="*80)
print("CONCLUSION:")
print("="*80)
print("If pure number tags are preserved 100%, we should switch to that format!")
print("If they're also corrupted, the problem is Google Translate itself.")
print()

