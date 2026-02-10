#!/usr/bin/env python3
"""
Complete test: Load ODT → Extract Preview → Create ODT with Formatting

This creates REAL output files that can be inspected.
Session: COM8
Date: 2026-02-10
"""

import sys
import os
sys.path.insert(0, 'src')

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html
from html.parser import HTMLParser
import html as html_module

# Test file
INPUT_FILE = 'docs/CAIT- Trabalho de Biologia - Josué 3001.odt'
OUTPUT_DIR = '.test_outputs/com8'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("COMPLETE TEST: ODT → Preview → ODT with Formatting")
print("="*70)
print()

# Step 1: Load ODT and extract HTML
print("Step 1: Loading ODT and extracting HTML...")
html_content, css_manager = HTMLFormatMapper.extract_html_from_odt(INPUT_FILE)
print(f"  ✓ Extracted {len(html_content)} chars of HTML")
print(f"  ✓ Found {len(css_manager.class_to_format)} CSS classes")

# Save HTML for inspection
html_output = os.path.join(OUTPUT_DIR, 'test_extracted_html_COM8.html')
with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"  ✓ Saved HTML to: {html_output}")
print()

# Step 2: Extract preview text (with fixes)
print("Step 2: Extracting preview text (with TextExtractor fixes)...")

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.current_tag = None
        self.current_class = None
        self.prev_class = None
        self.header_classes = ['fmt1', 'fmt3', 'fmt4', 'fmt5', 'fmt7']
    
    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text_parts.append('\n')
            self.current_tag = tag
            return
        
        if tag == 'span':
            new_class = None
            for attr, value in attrs:
                if attr == 'class':
                    new_class = value
                    break
            
            if self.prev_class and new_class and self.prev_class != new_class:
                prev_is_header = self.prev_class in self.header_classes
                new_is_header = new_class in self.header_classes
                
                if prev_is_header != new_is_header:
                    self.text_parts.append('\n')
            
            self.current_class = new_class
        
        self.current_tag = tag
    
    def handle_endtag(self, tag):
        if tag == 'span' and self.current_class:
            self.prev_class = self.current_class
        if tag == self.current_tag:
            self.current_tag = None
    
    def handle_data(self, data):
        if self.current_tag in ['style', 'script', 'head', 'title']:
            return
        
        if self.current_tag in ['span', 'p', 'div']:
            decoded = html_module.unescape(data)
            self.text_parts.append(decoded)
        elif data.strip():
            decoded = html_module.unescape(data)
            self.text_parts.append(decoded)
    
    def get_text(self):
        return ''.join(self.text_parts)

extractor = TextExtractor()
extractor.feed(html_content)
preview_text = extractor.get_text()

print(f"  ✓ Extracted {len(preview_text)} chars of preview text")
print(f"  ✓ Preview has {preview_text.count(chr(10)) + 1} lines")

# Check quality
has_css = '.fmt' in preview_text
has_tabs = '\t' in preview_text
has_breaks = '\n' in preview_text

print(f"  ✓ Has CSS visible: {has_css} {'❌ (BAD)' if has_css else '✅ (GOOD)'}")
print(f"  ✓ Has tabs: {has_tabs} {'✅ (GOOD)' if has_tabs else '❌ (BAD)'}")
print(f"  ✓ Has line breaks: {has_breaks} {'✅ (GOOD)' if has_breaks else '❌ (BAD)'}")

# Save preview text for inspection
preview_output = os.path.join(OUTPUT_DIR, 'test_preview_text_COM8.txt')
with open(preview_output, 'w', encoding='utf-8') as f:
    f.write(preview_text)
print(f"  ✓ Saved preview to: {preview_output}")
print()

# Step 3: Create ODT from HTML (simulate save)
print("Step 3: Creating ODT from HTML (simulating save)...")
odt_output = os.path.join(OUTPUT_DIR, 'test_output_with_formatting_COM8.odt')
create_odt_from_html(html_content, css_manager, odt_output)
print(f"  ✓ Created ODT: {odt_output}")
print()

# Step 4: Verify output ODT has formatting
print("Step 4: Verifying output ODT has formatting...")
from odf import opendocument, text, style

doc = opendocument.load(odt_output)
styles = list(doc.automaticstyles.childNodes)
paras = doc.text.getElementsByType(text.P)

print(f"  ✓ Automatic styles: {len(styles)}")
print(f"  ✓ Paragraphs: {len(paras)}")

# List styles
if styles:
    print(f"  ✓ Styles found:")
    for s in styles[:10]:
        if hasattr(s, 'getAttribute'):
            name = s.getAttribute('name')
            if name:
                print(f"     - {name}")

if len(styles) >= 8:
    print(f"  ✅ SUCCESS: Has {len(styles)} styles (formatting preserved!)")
else:
    print(f"  ❌ FAILURE: Only {len(styles)} styles (expected 8+)")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)
print()
print("Output files created:")
print(f"  1. {html_output}")
print(f"  2. {preview_output}")
print(f"  3. {odt_output}")
print()
print("You can now inspect these files:")
print("  - HTML: Contains CSS and formatting (internal format)")
print("  - Preview: Plain text, NO CSS visible (what user sees)")
print("  - ODT: Has all styles preserved (final output)")
print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
all_good = (not has_css) and has_tabs and has_breaks and (len(styles) >= 8)
if all_good:
    print("✅✅✅ ALL CHECKS PASSED!")
    print()
    print("The fixes are working correctly:")
    print("  ✅ No CSS in preview")
    print("  ✅ Tabs preserved")
    print("  ✅ Line breaks preserved")
    print("  ✅ Formatting preserved in ODT")
else:
    print("❌ SOME CHECKS FAILED")
    if has_css:
        print("  ❌ CSS visible in preview")
    if not has_tabs:
        print("  ❌ Tabs not preserved")
    if not has_breaks:
        print("  ❌ Line breaks not preserved")
    if len(styles) < 8:
        print(f"  ❌ Only {len(styles)} styles in ODT (expected 8+)")

print()
