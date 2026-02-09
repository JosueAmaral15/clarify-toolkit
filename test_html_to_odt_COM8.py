#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test ODT Creation from HTML - Phase 2 Testing

Tests the HTML to ODT conversion (round-trip).

Author: COM8
Date: February 9, 2026
Session: 77 - Phase 2
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from translation.html_format_mapper import (
    HTMLFormatMapper,
    create_odt_from_html,
    protect_special_whitespace,
    restore_special_whitespace
)


def test_round_trip():
    """Test complete round-trip: ODT → HTML → ODT."""
    print("=" * 80)
    print("TEST: ODT Round-Trip Conversion")
    print("=" * 80)
    
    # Use user's actual file
    input_odt = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
    output_html = "test_roundtrip_step1_COM8.html"
    output_odt = "test_roundtrip_step2_COM8.odt"
    
    if not os.path.exists(input_odt):
        print(f"⚠️  SKIP: Test file not found: {input_odt}")
        return
    
    print(f"\n📄 Step 1: Extract ODT → HTML")
    print(f"   Input: {input_odt}")
    
    try:
        # Step 1: ODT → HTML
        html, css_manager = HTMLFormatMapper.extract_html_from_odt(input_odt)
        
        print(f"   ✅ Extraction complete")
        print(f"   - HTML length: {len(html)} characters")
        print(f"   - CSS classes: {css_manager.counter - 1}")
        
        # Save HTML for inspection
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   - Saved to: {output_html}")
        
        # Step 2: HTML → ODT
        print(f"\n📄 Step 2: Create ODT from HTML")
        print(f"   Output: {output_odt}")
        
        create_odt_from_html(html, css_manager, output_odt)
        
        print(f"   ✅ ODT creation complete")
        print(f"   - File saved: {output_odt}")
        
        # Verify file exists
        assert os.path.exists(output_odt), f"Output file not created: {output_odt}"
        
        file_size = os.path.getsize(output_odt)
        print(f"   - File size: {file_size:,} bytes")
        
        print("\n" + "=" * 80)
        print("✅ ROUND-TRIP TEST PASSED")
        print("=" * 80)
        print(f"\nNext steps:")
        print(f"1. Open the original file: {input_odt}")
        print(f"2. Open the output file: {output_odt}")
        print(f"3. Compare formatting visually")
        print(f"4. Check if all text is preserved")
        print(f"5. Check if all formatting is preserved (fonts, colors, bold, italic)")
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_translated_html():
    """Test with simulated translated HTML."""
    print("\n" + "=" * 80)
    print("TEST: Translated HTML to ODT")
    print("=" * 80)
    
    # Simulate Google Translate modifying the HTML
    # We'll translate CAIT biology text from Portuguese to English
    
    translated_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="generator" content="Clarify HTML Format Mapper">
    <meta name="odt-translation" content="true">
    <style>
.fmt1 { font-weight: bold; font-size: 14pt; line-height: 1.0; }
.fmt2 { font-size: 12pt; line-height: 1.0; }
.fmt3 { font-weight: bold; font-size: 12pt; line-height: 1.0; }
.fmt5 { font-weight: bold; font-style: italic; font-size: 16pt; line-height: 1.0; }
.fmt6 { font-style: italic; font-size: 9pt; color: #666666; }
.fmt7 { font-weight: bold; font-size: 9pt; color: #525252; }
.fmt8 { font-size: 9pt; color: #525252; }
    </style>
</head>
<body>
<span class="fmt1">CAIT</span>
<span class="fmt1">&#9;</span>
<span class="fmt2">&#9;&#9;&#9;&#9;&#9;&#9;&#9;&#9;&#9;</span>
<span class="fmt3">13/11/12</span>
<br>
<br>
<span class="fmt2">&#9;&#9;&#9;</span>
<span class="fmt5">Biology Work</span>
<br>
<br>
<span class="fmt2">Transgenics</span>
<br>
<span class="fmt6">CONCEPT: they are genetically modified foods with alteration of the genetic code, that is, genes from another are inserted into the organism. This procedure can even be done between organisms of different species (insertion of a virus gene into a plant, for example). The procedure can be performed with plants, animals and microorganisms.</span>
<br>
<br>
<span class="fmt7">RISKS TO AGRICULTURE: </span>
<span class="fmt8">transgenic species are protected by patents, which means that the farmer who decides to use them (if authorized in Brazil) will have to pay royalties to the company that owns the technology.</span>
<br>
</body>
</html>"""
    
    output_odt = "test_translated_output_COM8.odt"
    
    print(f"\n📄 Creating ODT from simulated translated HTML")
    print(f"   Output: {output_odt}")
    
    try:
        # Parse CSS to create manager
        from translation.html_format_mapper import CSSClassManager, FormatAttributes
        
        # Create CSS manager from style definitions
        css_manager = CSSClassManager()
        
        # Manually create format mappings based on CSS
        fmt1 = FormatAttributes(bold=True, font_size=14, line_spacing=1.0)
        fmt2 = FormatAttributes(font_size=12, line_spacing=1.0)
        fmt3 = FormatAttributes(bold=True, font_size=12, line_spacing=1.0)
        fmt5 = FormatAttributes(bold=True, italic=True, font_size=16, line_spacing=1.0)
        fmt6 = FormatAttributes(italic=True, font_size=9, font_color="666666")
        fmt7 = FormatAttributes(bold=True, font_size=9, font_color="525252")
        fmt8 = FormatAttributes(font_size=9, font_color="525252")
        
        css_manager.format_to_class[fmt1] = "fmt1"
        css_manager.format_to_class[fmt2] = "fmt2"
        css_manager.format_to_class[fmt3] = "fmt3"
        css_manager.format_to_class[fmt5] = "fmt5"
        css_manager.format_to_class[fmt6] = "fmt6"
        css_manager.format_to_class[fmt7] = "fmt7"
        css_manager.format_to_class[fmt8] = "fmt8"
        
        css_manager.class_to_format["fmt1"] = fmt1
        css_manager.class_to_format["fmt2"] = fmt2
        css_manager.class_to_format["fmt3"] = fmt3
        css_manager.class_to_format["fmt5"] = fmt5
        css_manager.class_to_format["fmt6"] = fmt6
        css_manager.class_to_format["fmt7"] = fmt7
        css_manager.class_to_format["fmt8"] = fmt8
        
        css_manager.counter = 9
        
        # Create ODT
        create_odt_from_html(translated_html, css_manager, output_odt)
        
        print(f"   ✅ ODT creation complete")
        
        # Verify file exists
        assert os.path.exists(output_odt), f"Output file not created: {output_odt}"
        
        file_size = os.path.getsize(output_odt)
        print(f"   - File saved: {output_odt}")
        print(f"   - File size: {file_size:,} bytes")
        
        print("\n" + "=" * 80)
        print("✅ TRANSLATED HTML TEST PASSED")
        print("=" * 80)
        print(f"\nNext steps:")
        print(f"1. Open the output file: {output_odt}")
        print(f"2. Verify English translation is present")
        print(f"3. Verify formatting is preserved (bold, italic, colors)")
        print(f"4. Check for any visible tags or placeholders (should be ZERO)")
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TESTING ODT CREATION FROM HTML - PHASE 2")
    print("Session 77 - COM8")
    print("=" * 80 + "\n")
    
    try:
        test_round_trip()
        test_translated_html()
        
        print("\n" + "=" * 80)
        print("ALL PHASE 2 TESTS PASSED ✅")
        print("=" * 80)
        print("\nReady for Phase 3: Integration with Google Translate workflow")
        
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
