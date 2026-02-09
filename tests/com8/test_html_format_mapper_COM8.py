#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test HTML Format Mapper - Phase 1 Testing

Tests the new HTML-based format extraction system.

Author: COM8
Date: February 9, 2026
Session: 77
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from translation.html_format_mapper import (
    HTMLFormatMapper,
    FormatAttributes,
    CSSClassManager,
    protect_special_whitespace,
    restore_special_whitespace
)


def test_format_attributes():
    """Test FormatAttributes CSS generation."""
    print("=" * 80)
    print("TEST 1: FormatAttributes CSS Generation")
    print("=" * 80)
    
    # Test character formatting
    fmt = FormatAttributes(
        bold=True,
        italic=True,
        font_family="Arial",
        font_size=12,
        font_color="525252"
    )
    
    css = fmt.to_css()
    print(f"Format: bold=True, italic=True, font=Arial 12pt, color=#525252")
    print(f"CSS: {css}")
    
    expected = "font-weight: bold; font-style: italic; font-family: Arial; font-size: 12pt; color: #525252"
    assert css == expected, f"CSS mismatch!\nExpected: {expected}\nGot: {css}"
    print("✅ PASS\n")


def test_css_class_manager():
    """Test CSS class deduplication."""
    print("=" * 80)
    print("TEST 2: CSS Class Manager Deduplication")
    print("=" * 80)
    
    manager = CSSClassManager()
    
    # Create same format twice
    fmt1 = FormatAttributes(bold=True, font_size=12)
    fmt2 = FormatAttributes(bold=True, font_size=12)
    fmt3 = FormatAttributes(italic=True, font_size=14)
    
    class1 = manager.get_or_create_class(fmt1)
    class2 = manager.get_or_create_class(fmt2)  # Should reuse fmt1
    class3 = manager.get_or_create_class(fmt3)
    
    print(f"Format 1 (bold, 12pt): {class1}")
    print(f"Format 2 (bold, 12pt): {class2} (should be same as Format 1)")
    print(f"Format 3 (italic, 14pt): {class3}")
    
    assert class1 == class2, f"Deduplication failed! {class1} != {class2}"
    assert class1 != class3, f"Different formats got same class! {class1} == {class3}"
    
    print(f"\nTotal classes created: {manager.counter - 1}")
    print("✅ PASS\n")


def test_css_generation():
    """Test complete CSS stylesheet generation."""
    print("=" * 80)
    print("TEST 3: CSS Stylesheet Generation")
    print("=" * 80)
    
    manager = CSSClassManager()
    
    fmt1 = FormatAttributes(bold=True, font_size=12)
    fmt2 = FormatAttributes(italic=True, font_color="FF0000")
    
    manager.get_or_create_class(fmt1)
    manager.get_or_create_class(fmt2)
    
    css = manager.generate_css()
    print("Generated CSS:")
    print(css)
    
    assert ".fmt1" in css, "Missing .fmt1 class"
    assert ".fmt2" in css, "Missing .fmt2 class"
    assert "font-weight: bold" in css, "Missing bold style"
    assert "font-style: italic" in css, "Missing italic style"
    
    print("\n✅ PASS\n")


def test_whitespace_protection():
    """Test HTML entity conversion."""
    print("=" * 80)
    print("TEST 4: Whitespace Protection")
    print("=" * 80)
    
    original = "Text\twith\ttabs\nand\nnewlines"
    protected = protect_special_whitespace(original)
    restored = restore_special_whitespace(protected)
    
    print(f"Original: {repr(original)}")
    print(f"Protected: {repr(protected)}")
    print(f"Restored: {repr(restored)}")
    
    assert '\t' not in protected, "Tabs not converted"
    assert '&#9;' in protected, "Tab entity not created"
    assert original == restored, "Round-trip failed"
    
    print("\n✅ PASS\n")


def test_odt_extraction():
    """Test ODT extraction to HTML."""
    print("=" * 80)
    print("TEST 5: ODT Extraction to HTML")
    print("=" * 80)
    
    # Use user's actual file
    test_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
    
    if not os.path.exists(test_file):
        print(f"⚠️  SKIP: Test file not found: {test_file}")
        return
    
    print(f"Extracting: {test_file}")
    
    try:
        html, css_manager_or_path = HTMLFormatMapper.extract_html_from_odt(test_file)
        
        print(f"\nExtraction complete!")
        print(f"HTML length: {len(html)} characters")
        
        # Check if CSS manager was saved to file
        if isinstance(css_manager_or_path, str):
            print(f"CSS mapping saved to: {css_manager_or_path}")
            print("(Large file - used JSON storage)")
        else:
            print(f"CSS classes created: {css_manager_or_path.counter - 1}")
            print("(Small file - kept in memory)")
        
        # Save HTML for inspection
        output_file = "test_extraction_output_COM8.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\nHTML saved to: {output_file}")
        print("You can open this file in a browser to verify formatting preservation")
        
        # Basic validation
        assert '<!DOCTYPE html>' in html, "Missing DOCTYPE"
        assert '<html>' in html, "Missing <html> tag"
        assert '<head>' in html, "Missing <head> tag"
        assert '<style>' in html, "Missing <style> tag"
        assert '<body>' in html, "Missing <body> tag"
        assert '.fmt' in html, "Missing CSS classes"
        
        # Check for content
        assert 'CAIT' in html or 'Transgênicos' in html or 'CONCEITO' in html, "Missing expected content"
        
        print("\n✅ PASS - HTML structure valid\n")
        
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TESTING HTML FORMAT MAPPER - PHASE 1")
    print("Session 77 - COM8")
    print("=" * 80 + "\n")
    
    try:
        test_format_attributes()
        test_css_class_manager()
        test_css_generation()
        test_whitespace_protection()
        test_odt_extraction()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)
        
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
