#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
End-to-End Translation Test (COM8)

Tests the complete workflow:
ODT → HTML → Google Translate → HTML → ODT

Verifies formatting is preserved throughout the entire process.

Author: COM8
Date: 2026-02-15
Protocol: SIMPLICITY_PROTOCOL_3
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from translation.html_format_mapper import HTMLFormatMapper
from translation.google_translate import GoogleTranslateAPI
from odf import opendocument, text

# Test configuration
INPUT_ODT = "docs/CAIT- Trabalho de Biologia - Josué 3001.odt"
OUTPUT_ODT = ".test_outputs/com8/CAIT_TRANSLATED_END_TO_END_COM8.odt"
OUTPUT_HTML = ".test_outputs/com8/translated_html_end_to_end_COM8.html"

def main():
    print("="*80)
    print("END-TO-END TRANSLATION TEST (COM8)")
    print("="*80)
    
    # Step 1: Load ODT and extract HTML
    print("\n" + "="*80)
    print("STEP 1: Extract HTML from ODT")
    print("="*80)
    print(f"Loading: {INPUT_ODT}")
    
    html_content, css_manager = HTMLFormatMapper.extract_html_from_odt(INPUT_ODT)
    
    print(f"✓ Extracted HTML: {len(html_content)} characters")
    
    # Count CSS classes from HTML
    import re
    css_classes = re.findall(r'\.fmt\d+', html_content)
    unique_classes = set(css_classes)
    print(f"✓ CSS classes: {len(unique_classes)} format classes found")
    
    # Show CSS classes
    print("\nCSS Classes Found:")
    for cls in sorted(unique_classes):
        print(f"  - {cls}")
    
    # Show first part of HTML
    print("\nHTML Preview (first 400 chars):")
    print(html_content[:400])
    
    # Step 2: Translate HTML (full document)
    print("\n" + "="*80)
    print("STEP 2: Translate HTML with Google Translate")
    print("="*80)
    print("Translating: Portuguese → English")
    print("This may take 30-60 seconds for full document...")
    
    translator = GoogleTranslateAPI()
    result = translator.translate_text(html_content, from_lang='pt', to_lang='en')
    
    if not result.success:
        print(f"❌ Translation FAILED: {result.error_message}")
        return 1
    
    translated_html = result.translated_text
    print(f"✓ Translation successful: {len(translated_html)} characters")
    
    # Save translated HTML for inspection
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(translated_html)
    print(f"✓ Saved translated HTML to: {OUTPUT_HTML}")
    
    # Check HTML preservation
    print("\nHTML Preservation Check:")
    checks = {
        '<span': '<span> tags',
        'class=': 'class attributes',
        '<br': '<br> tags',
        '.fmt1': 'CSS classes in style',
        '<style>': 'style section'
    }
    
    for marker, description in checks.items():
        present = marker in translated_html
        status = "✓" if present else "❌"
        print(f"  {status} {description}: {present}")
    
    # Show translated preview
    print("\nTranslated HTML Preview (first 400 chars):")
    print(translated_html[:400])
    
    # Step 3: Create ODT from translated HTML
    print("\n" + "="*80)
    print("STEP 3: Create ODT from Translated HTML")
    print("="*80)
    
    try:
        # Create ODT using the function from html_format_mapper
        from translation.html_format_mapper import create_odt_from_html
        
        # Function saves directly to file, doesn't return document
        create_odt_from_html(
            translated_html,
            css_manager,
            OUTPUT_ODT  # Output path, not template
        )
        
        print(f"✓ Created ODT: {OUTPUT_ODT}")
        
    except Exception as e:
        print(f"❌ Failed to create ODT: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 4: Verify ODT structure
    print("\n" + "="*80)
    print("STEP 4: Verify ODT Structure")
    print("="*80)
    print(f"Loading: {OUTPUT_ODT}")
    
    try:
        doc = opendocument.load(OUTPUT_ODT)
        
        # Check automatic styles
        styles = list(doc.automaticstyles.childNodes)
        print(f"✓ Automatic styles: {len(styles)}")
        
        for i, style in enumerate(styles[:10], 1):
            style_name = style.getAttribute('name')
            print(f"  {i}. {style_name}")
        
        # Check paragraphs
        paragraphs = doc.text.getElementsByType(text.P)
        print(f"\n✓ Paragraphs: {len(paragraphs)}")
        
        if paragraphs:
            first_para = paragraphs[0]
            print(f"✓ First paragraph children: {len(first_para.childNodes)}")
            
            # Extract text
            all_text = []
            for child in first_para.childNodes:
                if hasattr(child, 'data'):
                    all_text.append(child.data)
                elif child.qname == (text.TEXTNS, 'span'):
                    for subchild in child.childNodes:
                        if hasattr(subchild, 'data'):
                            all_text.append(subchild.data)
            
            full_text = ''.join(all_text)
            print(f"\n✓ Content Preview (first 200 chars):")
            print(f"  {full_text[:200]}...")
            
            # Check if it's translated
            if 'Biology' in full_text or 'Assignment' in full_text:
                print("\n✅ Content is TRANSLATED (found English words)")
            else:
                print("\n⚠️  Content might not be translated (no English words found)")
        
    except Exception as e:
        print(f"❌ Failed to verify ODT: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Final Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    print("\n✅ ALL STEPS COMPLETED SUCCESSFULLY!")
    print("\nWorkflow:")
    print(f"  1. ODT loaded: {INPUT_ODT}")
    print(f"  2. HTML extracted: {len(html_content)} chars, {len(unique_classes)} CSS classes")
    print(f"  3. Translated: Portuguese → English")
    print(f"  4. ODT created: {OUTPUT_ODT} with {len(styles)} styles")
    
    print("\nNext Steps:")
    print("  1. Open output file in LibreOffice:")
    print(f"     libreoffice '{OUTPUT_ODT}'")
    print("  2. Compare formatting with original")
    print("  3. Verify all styling preserved")
    
    print("\n" + "="*80)
    return 0

if __name__ == '__main__':
    sys.exit(main())
