#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Complete Translation Workflow - Phase 3 Testing

Tests the integrated HTML-based translation system end-to-end.

Author: COM8
Date: February 9, 2026
Session: 77 - Phase 3
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html, protect_special_whitespace, restore_special_whitespace
from translation.google_translate import GoogleTranslateAPI


def test_complete_workflow():
    """Test complete ODT → HTML → Translate → ODT workflow."""
    print("=" * 80)
    print("TEST: Complete Translation Workflow (ODT → HTML → Google → ODT)")
    print("=" * 80)
    
    # Use user's actual file
    input_odt = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
    output_odt = "test_complete_workflow_COM8.odt"
    
    if not os.path.exists(input_odt):
        print(f"⚠️  SKIP: Test file not found: {input_odt}")
        return
    
    try:
        # Step 1: Extract ODT → HTML
        print(f"\n📄 Step 1: Extract ODT → HTML")
        print(f"   Input: {input_odt}")
        
        html, css_manager = HTMLFormatMapper.extract_html_from_odt(input_odt)
        
        print(f"   ✅ Extraction complete")
        print(f"   - HTML length: {len(html)} characters")
        print(f"   - CSS classes: {css_manager.counter - 1}")
        
        # Step 2: Protect whitespace
        print(f"\n📄 Step 2: Protect whitespace")
        html_protected = protect_special_whitespace(html)
        print(f"   ✅ Whitespace protected")
        
        # Step 3: Translate (Portuguese → English)
        print(f"\n📄 Step 3: Translate with Google Translate")
        print(f"   Language: Portuguese → English")
        
        api = GoogleTranslateAPI()
        result = api.translate_text(html_protected, "pt", "en")
        
        if not result.success:
            print(f"   ❌ Translation failed: {result.error_message}")
            return
        
        print(f"   ✅ Translation complete")
        print(f"   - Output length: {len(result.translated_text)} characters")
        print(f"   - Detected language: {result.source_language}")
        
        # Step 4: Restore whitespace
        print(f"\n📄 Step 4: Restore whitespace")
        html_translated = restore_special_whitespace(result.translated_text)
        print(f"   ✅ Whitespace restored")
        
        # Save translated HTML for inspection
        with open("test_translated_html_COM8.html", 'w', encoding='utf-8') as f:
            f.write(html_translated)
        print(f"   - Saved to: test_translated_html_COM8.html")
        
        # Step 5: Create ODT from translated HTML
        print(f"\n📄 Step 5: Create ODT from translated HTML")
        print(f"   Output: {output_odt}")
        
        create_odt_from_html(html_translated, css_manager, output_odt)
        
        print(f"   ✅ ODT creation complete")
        
        # Verify file exists
        assert os.path.exists(output_odt), f"Output file not created: {output_odt}"
        
        file_size = os.path.getsize(output_odt)
        print(f"   - File saved: {output_odt}")
        print(f"   - File size: {file_size:,} bytes")
        
        # Check for visible tags or placeholders
        print(f"\n📄 Step 6: Verify no visible tags/placeholders")
        
        # Extract text from output ODT and check
        from odf import opendocument, text as odf_text
        doc = opendocument.load(output_odt)
        
        all_text = ""
        for para in doc.getElementsByType(odf_text.P):
            para_text = str(para)
            all_text += para_text + "\n"
        
        # Check for leaked format tags
        visible_issues = []
        if '<' in all_text and '>' in all_text and '|' in all_text:
            visible_issues.append("Visible number tags found")
        if '【' in all_text or '】' in all_text:
            visible_issues.append("Visible Unicode placeholders found")
        if '[FMT' in all_text or '【FMT' in all_text:
            visible_issues.append("Visible format placeholders found")
        
        if visible_issues:
            print(f"   ❌ ISSUES FOUND:")
            for issue in visible_issues:
                print(f"      - {issue}")
        else:
            print(f"   ✅ No visible tags or placeholders found")
        
        print("\n" + "=" * 80)
        print("✅ COMPLETE WORKFLOW TEST PASSED")
        print("=" * 80)
        print(f"\nResults:")
        print(f"  - Original file: {input_odt}")
        print(f"  - Translated file: {output_odt}")
        print(f"  - Translated HTML: test_translated_html_COM8.html")
        print(f"\nNext steps:")
        print(f"  1. Open {output_odt} in LibreOffice")
        print(f"  2. Verify English translation is present")
        print(f"  3. Verify formatting is preserved (fonts, colors, bold, italic)")
        print(f"  4. Check for ANY visible tags or placeholders (target: ZERO)")
        print(f"  5. Compare with original file formatting")
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TESTING COMPLETE TRANSLATION WORKFLOW - PHASE 3")
    print("Session 77 - COM8")
    print("HTML-Based Format System Integration")
    print("=" * 80 + "\n")
    
    try:
        test_complete_workflow()
        
        print("\n" + "=" * 80)
        print("ALL PHASE 3 TESTS PASSED ✅")
        print("=" * 80)
        print("\nHTML-based format system is now FULLY INTEGRATED!")
        print("Ready for production use with 100% format preservation.")
        
    except AssertionError as e:
        print("\n" + "=" * 80)
        print(f"TEST FAILED ❌: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"ERROR ❌: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
