#!/usr/bin/env python3
"""
Test AD1 SISO File Translation - COM8
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html

def main():
    print("=" * 70)
    print("TESTING WITH AD1 - SISO FILE")
    print("=" * 70)
    
    input_file = "/home/josue/Documents/Acadêmico/Graduação UFF/Arquivos de estudo de Josué Amaral/4o Semestre/Sistemas Operacionais/AD1 - SISO - em elaboração.odt"
    output_file = "/tmp/AD1_SISO_translated_COM8.odt"
    
    mapper = HTMLFormatMapper()
    
    # Step 1: Extract
    print("\n1️⃣ Extracting from ODT...")
    html, css_manager, image_manager, table_manager = mapper.extract_html_from_odt(input_file)
    
    print(f"   ✓ HTML: {len(html):,} chars")
    
    img_stats = image_manager.get_statistics()
    print(f"   ✓ Images: {img_stats['total_images']}")
    print(f"   ✓ Total size: {img_stats['total_mb']:.2f} MB")
    
    table_stats = table_manager.get_statistics()
    print(f"   ✓ Tables: {table_stats['total_tables']}")
    print(f"   ✓ Total cells: {table_stats['total_cells']}")
    
    # Step 2: Simulate translation (identity)
    print("\n2️⃣ Simulating translation (identity)...")
    translated_html = html
    print(f"   ✓ Translation complete")
    
    # Step 3: Create ODT
    print("\n3️⃣ Creating output ODT...")
    create_odt_from_html(translated_html, css_manager, output_file, image_manager, table_manager)
    print(f"   ✓ Saved to: {output_file}")
    
    # Step 4: Verify output
    print("\n4️⃣ Verifying output...")
    html2, css2, img2, tbl2 = mapper.extract_html_from_odt(output_file)
    
    img_stats2 = img2.get_statistics()
    tbl_stats2 = tbl2.get_statistics()
    
    print(f"   ✓ Images: {img_stats2['total_images']} ({img_stats2['total_mb']:.2f} MB)")
    print(f"   ✓ Tables: {tbl_stats2['total_tables']} ({tbl_stats2['total_cells']} cells)")
    
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"\nOutput file: {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
