#!/usr/bin/env python3
"""
Debug: Test actual translation flow with real ODT file (COM8)
"""

import sys
sys.path.insert(0, 'src')

from translation.html_format_mapper import HTMLFormatMapper
from translation.google_translate import GoogleTranslateAPI

# Load actual ODT
odt_file = "docs/CAIT- Trabalho de Biologia - Josué 3001.odt"
print("="*80)
print("TESTING ACTUAL TRANSLATION FLOW")
print("="*80)

print(f"\n1. Loading ODT: {odt_file}")
html_content, css_manager = HTMLFormatMapper.extract_html_from_odt(odt_file)

print(f"\n2. Extracted HTML ({len(html_content)} chars)")
print("   First 500 chars:")
print(html_content[:500])

print(f"\n3. Translating with Google Translate...")
translator = GoogleTranslateAPI()
result = translator.translate_text(html_content[:1000], from_lang='pt', to_lang='en')  # First 1000 chars only

if result.success:
    print(f"\n4. Translation Result ({len(result.translated_text)} chars)")
    print("   First 500 chars:")
    print(result.translated_text[:500])
    
    # Check preservation
    print(f"\n5. Preservation Check:")
    print(f"   - Has <span> tags: {'<span' in result.translated_text}")
    print(f"   - Has class= attributes: {'class=' in result.translated_text}")
    print(f"   - Has <br> tags: {'<br' in result.translated_text}")
    
    # Save for inspection
    with open('.test_outputs/com8/actual_translation_debug.html', 'w') as f:
        f.write(result.translated_text)
    print(f"\n✓ Saved to: .test_outputs/com8/actual_translation_debug.html")
else:
    print(f"\n❌ Translation FAILED: {result.error_message}")

print("\n" + "="*80)
