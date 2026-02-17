# ACTION PLAN: Create Test Script with Real Output Files

**Programmer**: COM8  
**Date**: 2026-02-10  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: Tests only run in memory - no output files to inspect

---

## PROBLEM

User asked: "Where are the output result files from your test?"

**Answer**: There are NONE!

My tests:
- ❌ Only ran in memory (Python scripts)
- ❌ Only printed to terminal
- ❌ Did NOT create output files
- ❌ Did NOT save preview text
- ❌ Did NOT create test ODT files

**This is inadequate testing!**

---

## SOLUTION: Create Comprehensive Test Script

### Test Script: `tests/com8/test_complete_preview_to_odt_COM8.py`

```python
#!/usr/bin/env python3
"""
Complete test: Load ODT → Extract Preview → Create ODT with Formatting

This creates REAL output files that can be inspected.
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
print("Step 2: Extracting preview text...")

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

print(f"  ✓ Has CSS visible: {has_css} (should be False)")
print(f"  ✓ Has tabs: {has_tabs} (should be True)")
print(f"  ✓ Has line breaks: {has_breaks} (should be True)")

# Save preview text for inspection
preview_output = os.path.join(OUTPUT_DIR, 'test_preview_text_COM8.txt')
with open(preview_output, 'w', encoding='utf-8') as f:
    f.write(preview_text)
print(f"  ✓ Saved preview to: {preview_output}")
print()

# Step 3: Create ODT from HTML (simulate save)
print("Step 3: Creating ODT from HTML...")
odt_output = os.path.join(OUTPUT_DIR, 'test_output_with_formatting_COM8.odt')
create_odt_from_html(html_content, css_manager, odt_output)
print(f"  ✓ Created ODT: {odt_output}")
print()

# Step 4: Verify output ODT has formatting
print("Step 4: Verifying output ODT...")
from odf import opendocument, text, style

doc = opendocument.load(odt_output)
styles = list(doc.automaticstyles.childNodes)
paras = doc.text.getElementsByType(text.P)

print(f"  ✓ Automatic styles: {len(styles)}")
print(f"  ✓ Paragraphs: {len(paras)}")

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
print("You can now inspect these files to verify:")
print("  - HTML contains CSS and formatting")
print("  - Preview text has NO CSS visible")
print("  - Output ODT has all styles preserved")
print()
```

---

## EXECUTION PLAN

1. Create the test script
2. Run it to generate output files
3. Provide file paths to user
4. User can inspect files directly

---

## OUTPUT FILES TO CREATE

1. `.test_outputs/com8/test_extracted_html_COM8.html`
   - The HTML extracted from source ODT
   - Should contain CSS in `<style>` section

2. `.test_outputs/com8/test_preview_text_COM8.txt`
   - Plain text preview (what user sees)
   - Should have NO CSS, NO HTML tags

3. `.test_outputs/com8/test_output_with_formatting_COM8.odt`
   - ODT created from HTML
   - Should have 8 automatic styles
   - Should preserve all formatting

---

## STATUS: Ready to create test with real output files

Should I create and run this test script now?
