#!/usr/bin/env python3
"""
Test Hyperlink Preservation in ODT Translation

Demonstrates the bug: Hyperlinks are stripped during extraction.

Author: COM8
Date: 2026-02-20
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_original
from odf.opendocument import OpenDocumentText
from odf.text import P, A as Link
import zipfile

def create_test_odt():
    """Create test ODT with various hyperlink types"""
    doc = OpenDocumentText()
    
    # Test 1: External link with same text as URL
    p1 = P()
    p1.addText('Visit ')
    link1 = Link(href='https://www.google.com.br')
    link1.addText('https://www.google.com.br')
    p1.appendChild(link1)
    p1.addText(' for search.')
    doc.text.addElement(p1)
    
    # Test 2: External link with different display text
    p2 = P()
    p2.addText('Search using ')
    link2 = Link(href='https://www.google.com')
    link2.addText('Google')
    p2.appendChild(link2)
    p2.addText(' engine.')
    doc.text.addElement(p2)
    
    # Test 3: Multiple links in one paragraph
    p3 = P()
    p3.addText('Resources: ')
    link3a = Link(href='https://github.com')
    link3a.addText('GitHub')
    p3.appendChild(link3a)
    p3.addText(' and ')
    link3b = Link(href='https://stackoverflow.com')
    link3b.addText('Stack Overflow')
    p3.appendChild(link3b)
    p3.addText(' are useful.')
    doc.text.addElement(p3)
    
    # Test 4: Internal link (cross-reference)
    p4 = P()
    p4.addText('See ')
    link4 = Link(href='#section1')
    link4.addText('Section 1')
    p4.appendChild(link4)
    p4.addText(' for details.')
    doc.text.addElement(p4)
    
    # Test 5: Email link
    p5 = P()
    p5.addText('Contact: ')
    link5 = Link(href='mailto:test@example.com')
    link5.addText('test@example.com')
    p5.appendChild(link5)
    doc.text.addElement(p5)
    
    output = '/tmp/test_hyperlinks_COM8.odt'
    doc.save(output)
    return output

def analyze_original_odt(odt_path):
    """Analyze hyperlinks in original ODT"""
    print("=" * 80)
    print("STEP 1: ANALYZING ORIGINAL ODT")
    print("=" * 80)
    
    from odf import opendocument
    doc = opendocument.load(odt_path)
    
    links = []
    for element in doc.getElementsByType(Link):
        href = element.getAttribute('href')
        text = ''.join([str(child) for child in element.childNodes])
        links.append((href, text))
    
    print(f"\n✓ Found {len(links)} hyperlinks in original ODT:\n")
    for i, (href, text) in enumerate(links, 1):
        print(f"  {i}. href=\"{href}\"")
        print(f"     text=\"{text}\"")
        print()
    
    return links

def test_extraction(odt_path):
    """Test extraction to HTML"""
    print("=" * 80)
    print("STEP 2: TESTING EXTRACTION TO HTML")
    print("=" * 80)
    
    html, css_mgr, img_mgr, tbl_mgr = HTMLFormatMapper.extract_html_from_odt(odt_path)
    
    print("\n--- EXTRACTED HTML ---")
    print(html)
    print("\n--- ANALYSIS ---")
    
    # Check for links
    has_a_tags = '<a href=' in html.lower()
    has_urls = any(url in html for url in ['google.com', 'github.com', 'stackoverflow.com'])
    
    print(f"✓ Contains <a> tags: {has_a_tags}")
    print(f"✓ Contains URL strings: {has_urls}")
    
    if not has_a_tags:
        print("\n❌ BUG CONFIRMED: Hyperlinks are stripped during extraction!")
        print("   Links are NOT preserved as <a href=...> in HTML.")
    else:
        print("\n✅ Hyperlinks preserved in HTML")
    
    return html, css_mgr, img_mgr, tbl_mgr

def test_restoration(odt_path, html, css_mgr, img_mgr, tbl_mgr):
    """Test restoration to ODT"""
    print("\n" + "=" * 80)
    print("STEP 3: TESTING RESTORATION TO ODT")
    print("=" * 80)
    
    output_path = '/tmp/test_hyperlinks_restored_COM8.odt'
    
    try:
        create_odt_from_original(odt_path, html, css_mgr, output_path, img_mgr, tbl_mgr)
        print(f"\n✓ ODT created: {output_path}")
    except Exception as e:
        print(f"\n✗ Restoration failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return output_path

def verify_restored_odt(output_path, original_links):
    """Verify links in restored ODT"""
    print("\n" + "=" * 80)
    print("STEP 4: VERIFYING RESTORED ODT")
    print("=" * 80)
    
    from odf import opendocument
    doc = opendocument.load(output_path)
    
    restored_links = []
    for element in doc.getElementsByType(Link):
        href = element.getAttribute('href')
        text = ''.join([str(child) for child in element.childNodes])
        restored_links.append((href, text))
    
    print(f"\n✓ Found {len(restored_links)} hyperlinks in restored ODT")
    
    if len(restored_links) == 0:
        print("\n❌ BUG CONFIRMED: All hyperlinks lost during translation workflow!")
        print("   Original had", len(original_links), "links, restored has 0.")
    elif len(restored_links) < len(original_links):
        print(f"\n⚠️  PARTIAL LOSS: {len(original_links) - len(restored_links)} links missing")
        print(f"   Original: {len(original_links)} links")
        print(f"   Restored: {len(restored_links)} links")
    else:
        print(f"\n✅ All {len(restored_links)} hyperlinks preserved!")
    
    # Compare links
    if restored_links:
        print("\nRestored links:")
        for i, (href, text) in enumerate(restored_links, 1):
            print(f"  {i}. href=\"{href}\" text=\"{text}\"")

def test_with_libreoffice(output_path):
    """Test if LibreOffice can open and display links"""
    print("\n" + "=" * 80)
    print("STEP 5: LIBREOFFICE VERIFICATION")
    print("=" * 80)
    
    import subprocess
    
    # Try to convert to PDF (checks if file is valid)
    try:
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '/tmp', output_path],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("\n✅ LibreOffice successfully processed the document")
            print(f"   PDF: /tmp/test_hyperlinks_restored_COM8.pdf")
        else:
            print("\n⚠️  LibreOffice conversion failed:")
            print(result.stderr)
    except Exception as e:
        print(f"\n⚠️  Could not test with LibreOffice: {e}")

def main():
    print("\n" + "=" * 80)
    print("HYPERLINK PRESERVATION TEST")
    print("=" * 80)
    print("\nThis test demonstrates the hyperlink bug in ODT translation.\n")
    
    # Create test ODT
    odt_path = create_test_odt()
    print(f"✓ Created test ODT: {odt_path}\n")
    
    # Step 1: Analyze original
    original_links = analyze_original_odt(odt_path)
    
    # Step 2: Extract to HTML (where bug occurs)
    html, css_mgr, img_mgr, tbl_mgr = test_extraction(odt_path)
    
    # Step 3: Restore to ODT
    output_path = test_restoration(odt_path, html, css_mgr, img_mgr, tbl_mgr)
    
    if output_path:
        # Step 4: Verify restored ODT
        verify_restored_odt(output_path, original_links)
        
        # Step 5: Test with LibreOffice
        test_with_libreoffice(output_path)
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n📋 Summary:")
    print(f"   Original ODT:  {len(original_links)} hyperlinks")
    print(f"   Test document: {odt_path}")
    print(f"   Restored ODT:  {output_path if output_path else 'FAILED'}")
    print("\n📖 See ACTION_PLAN_HYPERLINK_FIX_COM8.md for fix plan\n")

if __name__ == '__main__':
    main()
