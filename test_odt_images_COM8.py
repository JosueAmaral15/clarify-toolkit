#!/usr/bin/env python3
"""
Test script for ODT Image Preservation - Phase 1 COM8

Tests that images are preserved during ODT → HTML → Translation → ODT workflow.

Usage:
    python3 test_odt_images_COM8.py [odt_file]
"""
import sys
import os
import tempfile
import zipfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html


def test_odt_image_preservation(odt_path: str):
    """Test that images are preserved in ODT files."""
    
    print(f"\n{'='*70}")
    print(f"ODT IMAGE PRESERVATION TEST - Phase 1 COM8")
    print(f"{'='*70}")
    print(f"Input file: {odt_path}")
    print(f"File size: {os.path.getsize(odt_path):,} bytes\n")
    
    # Step 1: Extract images from ODT
    print("STEP 1: Extract HTML and Images from ODT")
    print("-" * 70)
    
    try:
        html_content, css_manager, image_manager = HTMLFormatMapper.extract_html_from_odt(odt_path)
        
        stats = image_manager.get_statistics()
        print(f"✓ Extraction successful")
        print(f"  - Total images: {stats['total_images']}")
        print(f"  - Total size: {stats['total_bytes']:,} bytes ({stats['total_mb']:.2f} MB)")
        print(f"  - Image formats: {stats.get('formats', 'N/A')}")
        print(f"  - HTML length: {len(html_content):,} characters")
        
        if stats['total_images'] == 0:
            print("\n⚠️  WARNING: No images found in ODT file!")
            print("   This file may not contain images, or they weren't detected.")
            return False
            
        print(f"\nImage details:")
        for img_id, img_data in image_manager._images.items():
            print(f"  - {img_id}: {img_data.format.upper()}, "
                  f"{img_data.width_cm:.2f}×{img_data.height_cm:.2f}cm, "
                  f"{len(img_data.blob):,} bytes")
        
    except Exception as e:
        print(f"✗ Extraction FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Verify image markers in HTML
    print(f"\nSTEP 2: Verify Image Markers in HTML")
    print("-" * 70)
    
    import re
    markers = re.findall(r'data-image="(IMG\d+)"', html_content)
    print(f"Found {len(markers)} image markers in HTML:")
    for marker in markers:
        print(f"  - {marker}")
    
    if len(markers) != stats['total_images']:
        print(f"⚠️  WARNING: Marker count ({len(markers)}) != image count ({stats['total_images']})")
    
    # Step 3: Simulate translation (identity - no change)
    print(f"\nSTEP 3: Simulate Translation (Identity)")
    print("-" * 70)
    translated_html = html_content  # Identity translation
    print(f"✓ Translation simulated (no changes)")
    
    # Step 4: Create ODT with images
    print(f"\nSTEP 4: Create ODT from Translated HTML")
    print("-" * 70)
    
    with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        create_odt_from_html(translated_html, css_manager, output_path, image_manager)
        print(f"✓ ODT created: {output_path}")
        print(f"  Output size: {os.path.getsize(output_path):,} bytes")
    except Exception as e:
        print(f"✗ ODT creation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify images in output ODT
    print(f"\nSTEP 5: Verify Images in Output ODT")
    print("-" * 70)
    
    try:
        with zipfile.ZipFile(output_path, 'r') as odt_zip:
            files = odt_zip.namelist()
            image_files = [f for f in files if f.startswith('Pictures/')]
            
            print(f"✓ Found {len(image_files)} files in Pictures/ folder:")
            for img_file in image_files:
                info = odt_zip.getinfo(img_file)
                print(f"  - {img_file}: {info.file_size:,} bytes")
            
            if len(image_files) != stats['total_images']:
                print(f"\n✗ FAIL: Expected {stats['total_images']} images, found {len(image_files)}")
                return False
            
            # Verify image data matches
            print(f"\nVerifying image data integrity:")
            all_match = True
            for img_id, img_data in image_manager._images.items():
                expected_path = f"Pictures/{img_id}.{img_data.format}"
                if expected_path in image_files:
                    saved_blob = odt_zip.read(expected_path)
                    if saved_blob == img_data.blob:
                        print(f"  ✓ {img_id}: Data matches ({len(saved_blob):,} bytes)")
                    else:
                        print(f"  ✗ {img_id}: Data MISMATCH!")
                        all_match = False
                else:
                    print(f"  ✗ {img_id}: NOT FOUND in output!")
                    all_match = False
            
            if not all_match:
                print(f"\n✗ FAIL: Some images don't match!")
                return False
                
    except Exception as e:
        print(f"✗ Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Cleanup and summary
    print(f"\n{'='*70}")
    print(f"TEST RESULT: ✓ SUCCESS - All images preserved!")
    print(f"{'='*70}")
    print(f"Input:  {odt_path}")
    print(f"Output: {output_path}")
    print(f"Images: {stats['total_images']} files, {stats['total_bytes']:,} bytes")
    print(f"\n⚠️  Note: Output file kept for manual inspection")
    
    return True


def main():
    """Main entry point."""
    
    if len(sys.argv) > 1:
        odt_file = sys.argv[1]
    else:
        # Use default test file
        odt_file = "docs/CAIT- Trabalho de Biologia - Josué 3001.odt"
    
    if not os.path.exists(odt_file):
        print(f"ERROR: File not found: {odt_file}")
        print(f"\nUsage: {sys.argv[0]} [odt_file]")
        return 1
    
    success = test_odt_image_preservation(odt_file)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
