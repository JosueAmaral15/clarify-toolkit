#!/usr/bin/env python3
"""
Test Option B with TCC file (large, complex document)

Tests: 77 images, 10 tables, 105K chars

Author: COM8
Date: 2026-02-20
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_original

INPUT_FILE = "/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify-COM8/docs/TCC_THAYS_CRISTINA_FARIAS_VERÇOZA_COSTA_e_JOSUÉ_AMARAL.odt"
OUTPUT_FILE = "/tmp/TCC_option_b_COM8.odt"

def test_tcc():
    print("=" * 80)
    print("TESTING OPTION B WITH TCC FILE (Large Complex Document)")
    print("=" * 80)
    
    # Extract
    print("\n[Step 1] Extracting TCC ODT...")
    html, css_manager, image_mgr, table_mgr = HTMLFormatMapper.extract_html_from_odt(INPUT_FILE)
    
    stats = {
        'html_chars': len(html),
        'css_classes': len(css_manager.class_to_format),
        'images': image_mgr.get_statistics()['total_images'] if image_mgr else 0,
        'tables': table_mgr.get_statistics()['total_tables'] if table_mgr else 0
    }
    
    print(f"✓ HTML: {stats['html_chars']:,} chars")
    print(f"✓ CSS: {stats['css_classes']} classes")
    print(f"✓ Images: {stats['images']}")
    print(f"✓ Tables: {stats['tables']}")
    
    # Create with Option B
    print("\n[Step 2] Creating ODT with Option B...")
    create_odt_from_original(INPUT_FILE, html, css_manager, OUTPUT_FILE, image_mgr, table_mgr)
    
    # Verify
    print("\n[Step 3] Verifying structure...")
    import zipfile
    
    with zipfile.ZipFile(INPUT_FILE, 'r') as orig:
        orig_files = set(orig.namelist())
    
    with zipfile.ZipFile(OUTPUT_FILE, 'r') as out:
        out_files = set(out.namelist())
    
    print(f"  Original: {len(orig_files)} files")
    print(f"  Output:   {len(out_files)} files")
    
    critical = ['content.xml', 'styles.xml', 'meta.xml', 'META-INF/manifest.xml', 
                'manifest.rdf', 'settings.xml']
    
    all_present = all(f in out_files for f in critical)
    print(f"  Critical files: {'✓ All present' if all_present else '✗ Missing some'}")
    
    missing = orig_files - out_files
    if missing:
        print(f"  ⚠️  Missing: {len(missing)} files")
    else:
        print("  ✓ All original files preserved!")
    
    print(f"\n✓ Output: {OUTPUT_FILE}")
    print("\n" + "=" * 80)
    print("TEST COMPLETE - Attempt LibreOffice conversion...")
    print("=" * 80)
    
    # Try LibreOffice conversion
    import subprocess
    result = subprocess.run(
        ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '/tmp', OUTPUT_FILE],
        capture_output=True, text=True, timeout=120
    )
    
    if result.returncode == 0:
        print("\n✅ SUCCESS: LibreOffice converted without errors!")
        print(f"   PDF: /tmp/TCC_option_b_COM8.pdf")
    else:
        print(f"\n✗ LibreOffice conversion failed:")
        print(result.stderr)

if __name__ == '__main__':
    test_tcc()
