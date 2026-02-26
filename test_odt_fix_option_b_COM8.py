#!/usr/bin/env python3
"""
Test Option B: ODT Fix - Preserve Original Structure

Tests the new create_odt_from_original() function that properly preserves
the original ODT structure (manifest.rdf, settings.xml, embedded objects, etc.)
instead of creating a minimal ODT from scratch.

Author: COM8
Date: 2026-02-20
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_original

# Test file
INPUT_FILE = "/home/josue/Documents/Acadêmico/Graduação UFF/Arquivos de estudo de Josué Amaral/4o Semestre/Sistemas Operacionais/AD1 - SISO - em elaboração.odt"
OUTPUT_FILE = "/tmp/AD1_SISO_option_b_COM8.odt"

def test_option_b():
    """Test ODT workflow with Option B (preserve structure)"""
    print("=" * 80)
    print("TESTING OPTION B: ODT Fix - Preserve Original Structure")
    print("=" * 80)
    
    # Step 1: Extract
    print("\n[Step 1] Extracting ODT to HTML...")
    html, css_manager, image_mgr, table_mgr = HTMLFormatMapper.extract_html_from_odt(INPUT_FILE)
    
    print(f"✓ Extracted HTML: {len(html)} chars")
    print(f"✓ CSS classes: {len(css_manager.class_to_format)}")
    print(f"✓ Images: {image_mgr.get_statistics()['total_images'] if image_mgr else 0}")
    print(f"✓ Tables: {table_mgr.get_statistics()['total_tables'] if table_mgr else 0}")
    
    # Step 2: No actual translation (identity test)
    print("\n[Step 2] Skipping translation (identity test)...")
    translated_html = html
    
    # Step 3: Create ODT with Option B
    print("\n[Step 3] Creating ODT with Option B (preserve original structure)...")
    create_odt_from_original(INPUT_FILE, translated_html, css_manager, OUTPUT_FILE, image_mgr, table_mgr)
    
    print(f"\n✓ Output saved: {OUTPUT_FILE}")
    
    # Step 4: Verify file structure
    print("\n[Step 4] Verifying ODT structure...")
    import zipfile
    
    with zipfile.ZipFile(INPUT_FILE, 'r') as original_zip:
        original_files = set(original_zip.namelist())
    
    with zipfile.ZipFile(OUTPUT_FILE, 'r') as output_zip:
        output_files = set(output_zip.namelist())
    
    print(f"  Original ODT: {len(original_files)} files")
    print(f"  Output ODT:   {len(output_files)} files")
    
    # Check critical files
    critical_files = [
        'content.xml',
        'styles.xml',
        'meta.xml',
        'META-INF/manifest.xml',
        'manifest.rdf',
        'settings.xml'
    ]
    
    print("\n  Critical file check:")
    for file in critical_files:
        in_original = file in original_files
        in_output = file in output_files
        status = "✓" if in_output else "✗"
        print(f"    {status} {file}: Original={in_original}, Output={in_output}")
    
    # Check if any important files are missing
    missing = original_files - output_files
    if missing:
        print(f"\n  ⚠️  Missing files ({len(missing)}):")
        for f in sorted(missing)[:10]:  # Show first 10
            print(f"    - {f}")
    else:
        print("\n  ✓ All original files preserved!")
    
    # Check if any extra files were added
    extra = output_files - original_files
    if extra:
        print(f"\n  ℹ️  Extra files ({len(extra)}):")
        for f in sorted(extra)[:10]:
            print(f"    + {f}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"\nNext: Open {OUTPUT_FILE} in LibreOffice to verify no corruption")

if __name__ == '__main__':
    test_option_b()
