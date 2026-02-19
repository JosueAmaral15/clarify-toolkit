#!/usr/bin/env python3
"""
Test script for ODT Table Preservation - Phase 2 COM8

Tests that tables are preserved during ODT → HTML → Translation → ODT workflow.

Usage:
    python3 test_odt_tables_COM8.py [odt_file]
"""
import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html


def create_test_odt_with_table(output_path: str):
    """Create a test ODT file with a simple table."""
    from odf.opendocument import OpenDocumentText
    from odf.text import P
    from odf.table import Table, TableColumn, TableRow, TableCell
    
    # Create document
    doc = OpenDocumentText()
    
    # Add intro paragraph
    p1 = P(text="Test document with table:")
    doc.text.addElement(p1)
    
    # Create 3×2 table
    table = Table(name="TestTable")
    
    # Add column definitions
    table.addElement(TableColumn())
    table.addElement(TableColumn())
    
    # Row 1: Header
    row1 = TableRow()
    cell1 = TableCell()
    cell1.addElement(P(text="Name"))
    row1.addElement(cell1)
    
    cell2 = TableCell()
    cell2.addElement(P(text="Age"))
    row1.addElement(cell2)
    
    table.addElement(row1)
    
    # Row 2
    row2 = TableRow()
    cell1 = TableCell()
    cell1.addElement(P(text="Alice"))
    row2.addElement(cell1)
    
    cell2 = TableCell()
    cell2.addElement(P(text="30"))
    row2.addElement(cell2)
    
    table.addElement(row2)
    
    # Row 3
    row3 = TableRow()
    cell1 = TableCell()
    cell1.addElement(P(text="Bob"))
    row3.addElement(cell1)
    
    cell2 = TableCell()
    cell2.addElement(P(text="25"))
    row3.addElement(cell2)
    
    table.addElement(row3)
    
    doc.text.addElement(table)
    
    # Add closing paragraph
    p2 = P(text="End of table")
    doc.text.addElement(p2)
    
    # Save
    doc.save(output_path)
    print(f"Created test ODT with table: {output_path}")


def test_odt_table_preservation(odt_path: str):
    """Test that tables are preserved in ODT files."""
    
    print(f"\n{'='*70}")
    print(f"ODT TABLE PRESERVATION TEST - Phase 2 COM8")
    print(f"{'='*70}")
    print(f"Input file: {odt_path}")
    print(f"File size: {os.path.getsize(odt_path):,} bytes\n")
    
    # Step 1: Extract tables from ODT
    print("STEP 1: Extract HTML and Tables from ODT")
    print("-" * 70)
    
    try:
        html_content, css_manager, image_manager, table_manager = HTMLFormatMapper.extract_html_from_odt(odt_path)
        
        stats = table_manager.get_statistics()
        print(f"✓ Extraction successful")
        print(f"  - Total tables: {stats['total_tables']}")
        print(f"  - Table IDs: {stats['table_ids']}")
        print(f"  - Total cells: {stats['total_cells']}")
        print(f"  - HTML length: {len(html_content):,} characters")
        
        if stats['total_tables'] == 0:
            print("\n⚠️  WARNING: No tables found in ODT file!")
            print("   This file may not contain tables, or they weren't detected.")
            return False
            
        print(f"\nTable details:")
        for table_data in table_manager.get_all_tables():
            print(f"  - {table_data.table_id}: {table_data.rows}×{table_data.cols} table")
            print(f"    Name: {table_data.name or 'N/A'}")
            # Show first row as sample
            if table_data.rows > 0:
                first_row = [table_data.get_cell(0, col) for col in range(min(table_data.cols, 3))]
                print(f"    First row: {first_row}")
        
    except Exception as e:
        print(f"✗ Extraction FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Verify table markers in HTML
    print(f"\nSTEP 2: Verify Table Markers in HTML")
    print("-" * 70)
    
    import re
    markers = re.findall(r'data-table="(TBL\d+)"', html_content)
    print(f"Found {len(markers)} table markers in HTML:")
    for marker in markers:
        print(f"  - {marker}")
    
    if len(markers) != stats['total_tables']:
        print(f"⚠️  WARNING: Marker count ({len(markers)}) != table count ({stats['total_tables']})")
    
    # Verify table structure in HTML
    table_htmls = re.findall(r'<table[^>]*>.*?</table>', html_content, re.DOTALL)
    print(f"\nFound {len(table_htmls)} HTML <table> elements")
    for i, table_html in enumerate(table_htmls[:2]):  # Show first 2
        print(f"\nTable {i+1} preview:")
        lines = table_html.split('\n')[:5]
        for line in lines:
            print(f"    {line}")
        if len(lines) == 5:
            print(f"    ...")
    
    # Step 3: Simulate translation (identity - no change)
    print(f"\nSTEP 3: Simulate Translation (Identity)")
    print("-" * 70)
    translated_html = html_content  # Identity translation
    print(f"✓ Translation simulated (no changes)")
    
    # Step 4: Create ODT with tables
    print(f"\nSTEP 4: Create ODT from Translated HTML")
    print("-" * 70)
    
    with tempfile.NamedTemporaryFile(suffix='.odt', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        create_odt_from_html(translated_html, css_manager, output_path, image_manager, table_manager)
        print(f"✓ ODT created: {output_path}")
        print(f"  Output size: {os.path.getsize(output_path):,} bytes")
    except Exception as e:
        print(f"✗ ODT creation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Verify tables in output ODT
    print(f"\nSTEP 5: Verify Tables in Output ODT")
    print("-" * 70)
    
    try:
        # Re-extract from output to verify
        html_output, css_output, img_output, table_output = HTMLFormatMapper.extract_html_from_odt(output_path)
        
        stats_output = table_output.get_statistics()
        print(f"✓ Output ODT extracted successfully")
        print(f"  - Total tables: {stats_output['total_tables']}")
        print(f"  - Total cells: {stats_output['total_cells']}")
        
        if stats_output['total_tables'] != stats['total_tables']:
            print(f"\n✗ FAIL: Expected {stats['total_tables']} tables, found {stats_output['total_tables']}")
            return False
        
        # Verify table data matches
        print(f"\nVerifying table data integrity:")
        all_match = True
        for i, (orig_table, output_table) in enumerate(zip(
            table_manager.get_all_tables(),
            table_output.get_all_tables()
        )):
            print(f"  Table {i+1} ({orig_table.table_id}):")
            
            if orig_table.rows != output_table.rows:
                print(f"    ✗ Row count mismatch: {orig_table.rows} → {output_table.rows}")
                all_match = False
            elif orig_table.cols != output_table.cols:
                print(f"    ✗ Column count mismatch: {orig_table.cols} → {output_table.cols}")
                all_match = False
            else:
                # Check cell content
                cells_match = True
                for row in range(orig_table.rows):
                    for col in range(orig_table.cols):
                        orig_cell = orig_table.get_cell(row, col)
                        output_cell = output_table.get_cell(row, col)
                        if orig_cell != output_cell:
                            print(f"    ✗ Cell ({row},{col}) mismatch: '{orig_cell}' → '{output_cell}'")
                            cells_match = False
                            all_match = False
                
                if cells_match:
                    print(f"    ✓ Dimensions: {orig_table.rows}×{orig_table.cols}")
                    print(f"    ✓ All cells match")
        
        if not all_match:
            print(f"\n✗ FAIL: Some tables don't match!")
            return False
                
    except Exception as e:
        print(f"✗ Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 6: Summary
    print(f"\n{'='*70}")
    print(f"TEST RESULT: ✓ SUCCESS - All tables preserved!")
    print(f"{'='*70}")
    print(f"Input:  {odt_path}")
    print(f"Output: {output_path}")
    print(f"Tables: {stats['total_tables']} tables, {stats['total_cells']} cells")
    print(f"\n⚠️  Note: Output file kept for manual inspection")
    
    return True


def main():
    """Main entry point."""
    
    if len(sys.argv) > 1:
        odt_file = sys.argv[1]
        
        if not os.path.exists(odt_file):
            print(f"ERROR: File not found: {odt_file}")
            return 1
    else:
        # Create test file
        odt_file = "/tmp/test_with_table_COM8.odt"
        create_test_odt_with_table(odt_file)
        print()
    
    success = test_odt_table_preservation(odt_file)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
