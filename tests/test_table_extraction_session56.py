#!/usr/bin/env python3
"""
Session 56: Test table extraction architecture
Test that TableSegment and CellData classes work correctly
"""

from src.translation.format_mapper import FormatMapper, TableSegment, CellData, TextSegment
from docx import Document

def test_basic_table_structure():
    """Test creating and accessing table structure."""
    print("=" * 70)
    print("TEST 1: Basic Table Structure")
    print("=" * 70)
    
    table = TableSegment(2, 3)
    print(f"✓ Created {table.num_rows}x{table.num_cols} table")
    
    # Set cell content
    cell = CellData()
    cell.text_segments = [TextSegment(text="Test")]
    table.set_cell(0, 0, cell)
    print(f"✓ Set cell [0,0] content")
    
    # Get cell content
    retrieved = table.get_cell(0, 0)
    print(f"✓ Retrieved cell [0,0]: '{retrieved.text_segments[0].text}'")
    
    # Test placeholder
    placeholder = table.to_placeholder(1)
    print(f"✓ Generated placeholder: {placeholder}")
    
    assert placeholder == "{TABLE_1}", "Placeholder format incorrect"
    print("\n✓ TEST 1 PASSED\n")


def test_docx_table_extraction():
    """Test extracting table from actual DOCX file."""
    print("=" * 70)
    print("TEST 2: DOCX Table Extraction")
    print("=" * 70)
    
    # Create test DOCX with table
    doc = Document()
    doc.add_heading("Test Document with Table", level=1)
    doc.add_paragraph("This document contains a table:")
    
    # Add 2x3 table
    table = doc.add_table(rows=2, cols=3)
    table.style = 'Table Grid'
    
    # Fill cells
    cells_content = [
        ["Header 1", "Header 2", "Header 3"],
        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"]
    ]
    
    for row_idx, row_data in enumerate(cells_content):
        row_cells = table.rows[row_idx].cells
        for col_idx, content in enumerate(row_data):
            row_cells[col_idx].text = content
    
    doc.add_paragraph("Text after table.")
    
    # Save test file
    test_file = "/tmp/test_table_session56.docx"
    doc.save(test_file)
    print(f"✓ Created test DOCX: {test_file}")
    
    # Extract tables using our new method
    doc = Document(test_file)
    print(f"✓ Document has {len(doc.tables)} table(s)")
    
    if len(doc.tables) > 0:
        docx_table = doc.tables[0]
        table_segment = FormatMapper._extract_table_from_docx(docx_table)
        
        print(f"✓ Extracted table: {table_segment.num_rows}x{table_segment.num_cols}")
        
        # Check dimensions
        assert table_segment.num_rows == 2, f"Expected 2 rows, got {table_segment.num_rows}"
        assert table_segment.num_cols == 3, f"Expected 3 cols, got {table_segment.num_cols}"
        print(f"✓ Dimensions correct: 2x3")
        
        # Check first cell content
        cell_0_0 = table_segment.get_cell(0, 0)
        text_0_0 = "".join(seg.text for seg in cell_0_0.text_segments).strip()
        print(f"✓ Cell [0,0] text: '{text_0_0}'")
        assert "Header 1" in text_0_0, f"Expected 'Header 1', got '{text_0_0}'"
        
        # Check last cell
        cell_1_2 = table_segment.get_cell(1, 2)
        text_1_2 = "".join(seg.text for seg in cell_1_2.text_segments).strip()
        print(f"✓ Cell [1,2] text: '{text_1_2}'")
        assert "Row 1 Col 3" in text_1_2, f"Expected 'Row 1 Col 3', got '{text_1_2}'"
        
        print("\n✓ TEST 2 PASSED\n")
    else:
        print("✗ No tables found in document")
        return False
    
    return True


def test_modified_extraction():
    """Test that modified extraction function still works."""
    print("=" * 70)
    print("TEST 3: Modified Extraction Function")
    print("=" * 70)
    
    # Create simple DOCX with text and table
    doc = Document()
    doc.add_paragraph("Before table")
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "A"
    table.rows[0].cells[1].text = "B"
    doc.add_paragraph("After table")
    
    test_file = "/tmp/test_extraction_session56.docx"
    doc.save(test_file)
    
    # Extract using modified function
    try:
        tagged_text = FormatMapper.extract_formatted_text_from_docx(test_file)
        print(f"✓ Extraction succeeded")
        print(f"✓ Tagged text length: {len(tagged_text)} characters")
        
        # Check that text paragraphs are present
        assert "Before table" in tagged_text, "Missing 'Before table'"
        assert "After table" in tagged_text, "Missing 'After table'"
        print(f"✓ Text paragraphs preserved")
        
        print("\n✓ TEST 3 PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SESSION 56: TABLE ARCHITECTURE TESTING")
    print("=" * 70 + "\n")
    
    results = []
    
    try:
        test_basic_table_structure()
        results.append(("Basic Structure", True))
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        results.append(("Basic Structure", False))
    
    try:
        test_docx_table_extraction()
        results.append(("DOCX Extraction", True))
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        results.append(("DOCX Extraction", False))
    
    try:
        test_modified_extraction()
        results.append(("Modified Function", True))
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        results.append(("Modified Function", False))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f"\nResult: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✓ SESSION 56 ARCHITECTURE: COMPLETE")
    else:
        print("\n✗ SESSION 56: SOME TESTS FAILED")
