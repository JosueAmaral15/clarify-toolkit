#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
End-to-end test for DOCX translation using docx_html_mapper.py

Tests complete workflow with CAIT document:
1. Extract DOCX → HTML
2. Mock translation (identity function)
3. HTML → DOCX
4. Verify structure preservation (18P, 22LB, 14T)

Author: Josué Amaral (COM8)
Date: February 16, 2026
"""

import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from docx import Document
from translation.docx_html_mapper import (
    extract_html_from_docx,
    create_docx_from_html,
    translate_docx
)


def count_tabs_and_linebreaks(docx_path: str) -> tuple:
    """Count tabs and line-breaks in DOCX document."""
    doc = Document(docx_path)
    tab_count = 0
    lb_count = 0
    
    for para in doc.paragraphs:
        for run in para.runs:
            tab_count += run.text.count('\t')
            lb_count += run.text.count('\n') + run.text.count('\r')
    
    return tab_count, lb_count


def test_cait_document_structure_preservation():
    """Test DOCX translation preserves document structure."""
    print("=" * 70)
    print("DOCX Translation Test - CAIT Document")
    print("=" * 70)
    
    # Input file
    input_path = 'docs/CAIT- Trabalho de Biologia - Josué 3001.docx'
    
    if not os.path.exists(input_path):
        print(f"❌ ERROR: Test file not found: {input_path}")
        return False
    
    # Load original
    original_doc = Document(input_path)
    original_para_count = len(original_doc.paragraphs)
    original_tabs, original_lbs = count_tabs_and_linebreaks(input_path)
    
    print(f"\n📄 Original Document:")
    print(f"   Paragraphs: {original_para_count}")
    print(f"   Tabs: {original_tabs}")
    print(f"   Line-breaks: {original_lbs}")
    
    # Expected values
    EXPECTED_PARAS = 18
    EXPECTED_TABS = 14
    EXPECTED_LBS = 22
    
    print(f"\n✓ Expected:")
    print(f"   Paragraphs: {EXPECTED_PARAS}")
    print(f"   Tabs: {EXPECTED_TABS}")
    print(f"   Line-breaks: {EXPECTED_LBS}")
    
    # Verify original matches expected
    if original_para_count != EXPECTED_PARAS:
        print(f"\n⚠️  WARNING: Original has {original_para_count} paragraphs, expected {EXPECTED_PARAS}")
    if original_tabs != EXPECTED_TABS:
        print(f"⚠️  WARNING: Original has {original_tabs} tabs, expected {EXPECTED_TABS}")
    if original_lbs != EXPECTED_LBS:
        print(f"⚠️  WARNING: Original has {original_lbs} line-breaks, expected {EXPECTED_LBS}")
    
    # Create temp output file
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        print(f"\n🔄 Processing...")
        print(f"   Output: {output_path}")
        
        # Test 1: Extract HTML
        print("\n1️⃣  Extracting HTML...")
        html_string, css_manager, image_manager = extract_html_from_docx(input_path)
        print(f"   ✓ HTML extracted: {len(html_string)} chars")
        print(f"   ✓ CSS classes: {len(css_manager.class_to_format)}")
        
        # Optional: Save HTML for inspection
        html_debug_path = '/tmp/docx_test_debug.html'
        with open(html_debug_path, 'w', encoding='utf-8') as f:
            f.write(html_string)
        print(f"   ✓ Debug HTML saved: {html_debug_path}")
        
        # Test 2: Mock translation (identity)
        print("\n2️⃣  Mock translation (identity)...")
        translated_html = html_string  # No actual translation
        print(f"   ✓ HTML unchanged (structure test)")
        
        # Test 3: Create DOCX
        print("\n3️⃣  Creating DOCX from HTML...")
        create_docx_from_html(translated_html, output_path, css_manager, image_manager)
        print(f"   ✓ DOCX created")
        
        # Test 4: Verify output
        print("\n4️⃣  Verifying output structure...")
        output_doc = Document(output_path)
        output_para_count = len(output_doc.paragraphs)
        output_tabs, output_lbs = count_tabs_and_linebreaks(output_path)
        
        print(f"\n📄 Output Document:")
        print(f"   Paragraphs: {output_para_count}")
        print(f"   Tabs: {output_tabs}")
        print(f"   Line-breaks: {output_lbs}")
        
        # Validate
        print(f"\n📊 Validation:")
        success = True
        
        if output_para_count == EXPECTED_PARAS:
            print(f"   ✅ Paragraphs: {output_para_count} == {EXPECTED_PARAS}")
        else:
            print(f"   ❌ Paragraphs: {output_para_count} != {EXPECTED_PARAS}")
            success = False
        
        if output_tabs == EXPECTED_TABS:
            print(f"   ✅ Tabs: {output_tabs} == {EXPECTED_TABS}")
        else:
            print(f"   ❌ Tabs: {output_tabs} != {EXPECTED_TABS}")
            success = False
        
        if output_lbs == EXPECTED_LBS:
            print(f"   ✅ Line-breaks: {output_lbs} == {EXPECTED_LBS}")
        else:
            print(f"   ❌ Line-breaks: {output_lbs} != {EXPECTED_LBS}")
            success = False
        
        # Display first paragraph for manual check
        print(f"\n📝 First Paragraph Sample:")
        if output_doc.paragraphs:
            first_para_text = output_doc.paragraphs[0].text
            print(f"   Text: {repr(first_para_text)}")
            print(f"   Runs: {len(output_doc.paragraphs[0].runs)}")
            for i, run in enumerate(output_doc.paragraphs[0].runs[:5]):
                print(f"      Run {i}: {repr(run.text[:30])}")
        
        # Final result
        print("\n" + "=" * 70)
        if success:
            print("✅ TEST PASSED - Structure preserved perfectly!")
        else:
            print("❌ TEST FAILED - Structure mismatch detected")
        print("=" * 70)
        
        return success
        
    finally:
        # Cleanup (optional - keep for inspection)
        # os.unlink(output_path)
        print(f"\n💾 Output file kept for inspection: {output_path}")


def test_split_run_text():
    """Unit test for _split_run_text function."""
    from translation.docx_html_mapper import DocxHtmlMapper
    
    print("\n" + "=" * 70)
    print("Unit Test - _split_run_text()")
    print("=" * 70)
    
    # Create a dummy mapper to access the method
    mapper = DocxHtmlMapper.__new__(DocxHtmlMapper)
    
    tests = [
        ("", []),
        ("Plain text", [{'type': 'text', 'value': 'Plain text'}]),
        ("\t", [{'type': 'tab'}]),
        ("\t\t\t", [{'type': 'tab'}, {'type': 'tab'}, {'type': 'tab'}]),
        ("\n", [{'type': 'linebreak'}]),
        ("\n\n", [{'type': 'linebreak'}, {'type': 'linebreak'}]),
        ("Hello\tWorld", [
            {'type': 'text', 'value': 'Hello'},
            {'type': 'tab'},
            {'type': 'text', 'value': 'World'}
        ]),
        ("A\nB", [
            {'type': 'text', 'value': 'A'},
            {'type': 'linebreak'},
            {'type': 'text', 'value': 'B'}
        ]),
        ("\tHello\n", [
            {'type': 'tab'},
            {'type': 'text', 'value': 'Hello'},
            {'type': 'linebreak'}
        ]),
        ("A\tB\nC", [
            {'type': 'text', 'value': 'A'},
            {'type': 'tab'},
            {'type': 'text', 'value': 'B'},
            {'type': 'linebreak'},
            {'type': 'text', 'value': 'C'}
        ]),
    ]
    
    all_passed = True
    for input_text, expected in tests:
        result = mapper._split_run_text(input_text)
        passed = result == expected
        status = "✅" if passed else "❌"
        
        print(f"\n{status} Input: {repr(input_text)}")
        if not passed:
            print(f"   Expected: {expected}")
            print(f"   Got:      {result}")
            all_passed = False
        else:
            print(f"   Result: {result}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All unit tests PASSED")
    else:
        print("❌ Some unit tests FAILED")
    print("=" * 70)
    
    return all_passed


if __name__ == '__main__':
    print("\n🚀 DOCX HTML Mapper - Test Suite")
    print("Programmer: COM8")
    print("Date: 2026-02-16\n")
    
    # Run unit tests first
    unit_test_passed = test_split_run_text()
    
    # Run integration test
    integration_test_passed = test_cait_document_structure_preservation()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Unit Tests:        {'✅ PASSED' if unit_test_passed else '❌ FAILED'}")
    print(f"Integration Test:  {'✅ PASSED' if integration_test_passed else '❌ FAILED'}")
    print("=" * 70)
    
    sys.exit(0 if (unit_test_passed and integration_test_passed) else 1)
