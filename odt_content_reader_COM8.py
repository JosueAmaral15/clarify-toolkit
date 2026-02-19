#!/usr/bin/env python3
"""
ODT Content Reader - COM8
Reads and displays ODT file content using appropriate libraries
"""

import sys
from pathlib import Path
from odf import text, teletype
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.draw import Frame, Image

def read_odt_content(file_path: str, show_tables: bool = True, show_images: bool = True):
    """
    Read and display ODT file content
    
    Args:
        file_path: Path to ODT file
        show_tables: Show table content
        show_images: Show image information
    """
    print("=" * 80)
    print(f"READING ODT FILE: {Path(file_path).name}")
    print("=" * 80)
    
    try:
        doc = load(file_path)
        print(f"✓ File loaded successfully")
        
        # Statistics
        paragraph_count = 0
        table_count = 0
        image_count = 0
        text_content = []
        
        # Extract all text content
        all_text = teletype.extractText(doc.text)
        
        print(f"\n{'─' * 80}")
        print("FILE STATISTICS")
        print('─' * 80)
        
        # Count elements
        for element in doc.getElementsByType(text.P):
            paragraph_count += 1
        
        for element in doc.getElementsByType(Table):
            table_count += 1
            
        for element in doc.getElementsByType(Frame):
            # Check if frame contains an image
            if element.getElementsByType(Image):
                image_count += 1
        
        print(f"Paragraphs: {paragraph_count}")
        print(f"Tables: {table_count}")
        print(f"Images: {image_count}")
        print(f"Total characters: {len(all_text):,}")
        print(f"Total words: {len(all_text.split()):,}")
        
        # Show text content preview
        print(f"\n{'─' * 80}")
        print("TEXT CONTENT (First 500 chars)")
        print('─' * 80)
        preview = all_text[:500]
        print(preview)
        if len(all_text) > 500:
            print(f"\n... ({len(all_text) - 500:,} more characters)")
        
        # Show tables if requested
        if show_tables and table_count > 0:
            print(f"\n{'─' * 80}")
            print(f"TABLES ({table_count} found)")
            print('─' * 80)
            
            for idx, table in enumerate(doc.getElementsByType(Table), 1):
                print(f"\nTable {idx}:")
                
                # Get table name
                table_name = table.getAttribute('name')
                if table_name:
                    print(f"  Name: {table_name}")
                
                # Count rows and columns
                rows = table.getElementsByType(TableRow)
                print(f"  Rows: {len(rows)}")
                
                if rows:
                    first_row = rows[0]
                    cells = first_row.getElementsByType(TableCell)
                    print(f"  Columns: {len(cells)}")
                    
                    # Show first row content
                    print(f"  First row:")
                    for cell_idx, cell in enumerate(cells[:5], 1):  # Max 5 cells
                        cell_text = teletype.extractText(cell).strip()
                        if len(cell_text) > 30:
                            cell_text = cell_text[:27] + "..."
                        print(f"    [{cell_idx}] {cell_text}")
                    
                    if len(cells) > 5:
                        print(f"    ... and {len(cells) - 5} more columns")
        
        # Show images if requested
        if show_images and image_count > 0:
            print(f"\n{'─' * 80}")
            print(f"IMAGES ({image_count} found)")
            print('─' * 80)
            
            img_idx = 0
            for frame in doc.getElementsByType(Frame):
                images = frame.getElementsByType(Image)
                if images:
                    img_idx += 1
                    
                    # Get frame/image attributes
                    width = frame.getAttribute('width')
                    height = frame.getAttribute('height')
                    
                    print(f"\nImage {img_idx}:")
                    
                    # Try to get image href
                    for img in images:
                        href = img.getAttribute('href')
                        if href:
                            print(f"  Path: {href}")
                            break
                    
                    if width:
                        print(f"  Width: {width}")
                    if height:
                        print(f"  Height: {height}")
        
        print(f"\n{'═' * 80}")
        print("✅ CONTENT READ SUCCESSFULLY")
        print('═' * 80)
        
        return {
            'paragraphs': paragraph_count,
            'tables': table_count,
            'images': image_count,
            'characters': len(all_text),
            'words': len(all_text.split()),
            'full_text': all_text
        }
        
    except Exception as e:
        print(f"\n❌ ERROR reading file: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_odt_files(file1: str, file2: str):
    """Compare two ODT files"""
    print("=" * 80)
    print("COMPARING ODT FILES")
    print("=" * 80)
    
    print(f"\n📄 File 1: {Path(file1).name}")
    stats1 = read_odt_content(file1, show_tables=False, show_images=False)
    
    print(f"\n📄 File 2: {Path(file2).name}")
    stats2 = read_odt_content(file2, show_tables=False, show_images=False)
    
    if stats1 and stats2:
        print(f"\n{'═' * 80}")
        print("COMPARISON RESULTS")
        print('═' * 80)
        
        def compare_stat(name, val1, val2):
            match = "✓" if val1 == val2 else "✗"
            diff = val2 - val1
            diff_str = f"({diff:+d})" if diff != 0 else ""
            print(f"{match} {name:15} {val1:8,} → {val2:8,} {diff_str}")
        
        compare_stat("Paragraphs:", stats1['paragraphs'], stats2['paragraphs'])
        compare_stat("Tables:", stats1['tables'], stats2['tables'])
        compare_stat("Images:", stats1['images'], stats2['images'])
        compare_stat("Characters:", stats1['characters'], stats2['characters'])
        compare_stat("Words:", stats1['words'], stats2['words'])

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} <odt_file>              # Read single file")
        print(f"  {sys.argv[0]} <file1> <file2>         # Compare two files")
        return 1
    
    file1 = sys.argv[1]
    
    if len(sys.argv) == 2:
        # Single file mode
        read_odt_content(file1)
    else:
        # Compare mode
        file2 = sys.argv[2]
        compare_odt_files(file1, file2)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
