"""
Test suite for Session 63: Cell Merging (colspan/rowspan)
Tests extraction and reconstruction of merged table cells.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from odf.opendocument import OpenDocumentText, load
from odf.table import Table, TableRow, TableCell, CoveredTableCell
from odf.text import P
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))
from translation.format_mapper import FormatMapper


def test_docx_horizontal_merge():
    """Test 1: Extract horizontal merge (colspan) from DOCX"""
    print("\n" + "="*70)
    print("TEST 1: DOCX HORIZONTAL MERGE EXTRACTION")
    print("="*70)
    
    # Create test DOCX with horizontal merge
    doc = Document()
    table = doc.add_table(rows=2, cols=3)
    
    # Row 0: Merge columns 0-1 (colspan=2)
    table.rows[0].cells[0].text = "Merged 2 cols"
    table.rows[0].cells[2].text = "Normal"
    
    # Apply horizontal merge
    cell_0_0 = table.rows[0].cells[0]._element
    tcPr = cell_0_0.get_or_add_tcPr()
    hMerge = OxmlElement('w:hMerge')
    hMerge.set(qn('w:val'), 'restart')
    tcPr.append(hMerge)
    
    cell_0_1 = table.rows[0].cells[1]._element
    tcPr = cell_0_1.get_or_add_tcPr()
    hMerge = OxmlElement('w:hMerge')
    hMerge.set(qn('w:val'), 'continue')
    tcPr.append(hMerge)
    
    # Row 1: Normal cells
    table.rows[1].cells[0].text = "A"
    table.rows[1].cells[1].text = "B"
    table.rows[1].cells[2].text = "C"
    
    # Save and extract
    temp_path = "/tmp/test_hmerge.docx"
    doc.save(temp_path)
    
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    # Verify
    print("\n✓ Created 2x3 table with horizontal merge")
    cell_00 = table_segment.get_cell(0, 0)
    print(f"  Cell [0,0] colspan: {cell_00.col_span}")
    print(f"  Cell [0,0] rowspan: {cell_00.row_span}")
    
    cell_01 = table_segment.get_cell(0, 1)
    print(f"  Cell [0,1] colspan: {cell_01.col_span}")
    
    cell_10 = table_segment.get_cell(1, 0)
    print(f"  Cell [1,0] colspan: {cell_10.col_span}")
    
    assert cell_00.col_span == 2, "Cell [0,0] should have colspan=2"
    assert cell_00.row_span == 1, "Cell [0,0] should have rowspan=1"
    assert cell_01.col_span == 1, "Cell [0,1] should have colspan=1"
    assert cell_10.col_span == 1, "Cell [1,0] should have colspan=1"
    
    print("\n✅ TEST 1 PASSED: DOCX horizontal merge extraction working")
    return True


def test_docx_vertical_merge():
    """Test 2: Extract vertical merge (rowspan) from DOCX"""
    print("\n" + "="*70)
    print("TEST 2: DOCX VERTICAL MERGE EXTRACTION")
    print("="*70)
    
    # Create test DOCX with vertical merge
    doc = Document()
    table = doc.add_table(rows=3, cols=2)
    
    # Column 0: Merge rows 0-1 (rowspan=2)
    table.rows[0].cells[0].text = "Merged 2 rows"
    table.rows[2].cells[0].text = "Normal"
    
    # Apply vertical merge
    cell_0_0 = table.rows[0].cells[0]._element
    tcPr = cell_0_0.get_or_add_tcPr()
    vMerge = OxmlElement('w:vMerge')
    vMerge.set(qn('w:val'), 'restart')
    tcPr.append(vMerge)
    
    cell_1_0 = table.rows[1].cells[0]._element
    tcPr = cell_1_0.get_or_add_tcPr()
    vMerge = OxmlElement('w:vMerge')
    vMerge.set(qn('w:val'), 'continue')
    tcPr.append(vMerge)
    
    # Column 1: Normal cells
    table.rows[0].cells[1].text = "A"
    table.rows[1].cells[1].text = "B"
    table.rows[2].cells[1].text = "C"
    
    # Save and extract
    temp_path = "/tmp/test_vmerge.docx"
    doc.save(temp_path)
    
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    # Verify
    print("\n✓ Created 3x2 table with vertical merge")
    cell_00 = table_segment.get_cell(0, 0)
    print(f"  Cell [0,0] rowspan: {cell_00.row_span}")
    print(f"  Cell [0,0] colspan: {cell_00.col_span}")
    
    cell_10 = table_segment.get_cell(1, 0)
    print(f"  Cell [1,0] rowspan: {cell_10.row_span}")
    
    cell_20 = table_segment.get_cell(2, 0)
    print(f"  Cell [2,0] rowspan: {cell_20.row_span}")
    
    assert cell_00.row_span == 2, "Cell [0,0] should have rowspan=2"
    assert cell_00.col_span == 1, "Cell [0,0] should have colspan=1"
    assert cell_10.row_span == 1, "Cell [1,0] should have rowspan=1"
    assert cell_20.row_span == 1, "Cell [2,0] should have rowspan=1"
    
    print("\n✅ TEST 2 PASSED: DOCX vertical merge extraction working")
    return True


def test_odt_merge_extraction():
    """Test 3: Extract merges from ODT"""
    print("\n" + "="*70)
    print("TEST 3: ODT MERGE EXTRACTION")
    print("="*70)
    
    # Create ODT with both types of merges
    doc = OpenDocumentText()
    table = Table()
    
    # Row 0: Horizontal merge (colspan=2)
    row0 = TableRow()
    cell_merged_h = TableCell(numbercolumnsspanned=2)
    p = P()
    p.addText("Horizontal merge")
    cell_merged_h.addElement(p)
    row0.addElement(cell_merged_h)
    row0.addElement(CoveredTableCell())
    
    cell_normal = TableCell()
    p = P()
    p.addText("Normal")
    cell_normal.addElement(p)
    row0.addElement(cell_normal)
    table.addElement(row0)
    
    # Row 1: Vertical merge starts (rowspan=2)
    row1 = TableRow()
    cell_merged_v = TableCell(numberrowsspanned=2)
    p = P()
    p.addText("Vertical merge")
    cell_merged_v.addElement(p)
    row1.addElement(cell_merged_v)
    
    for text in ["A", "B"]:
        cell = TableCell()
        p = P()
        p.addText(text)
        cell.addElement(p)
        row1.addElement(cell)
    table.addElement(row1)
    
    # Row 2: Covered cell from vertical merge
    row2 = TableRow()
    row2.addElement(CoveredTableCell())
    
    for text in ["C", "D"]:
        cell = TableCell()
        p = P()
        p.addText(text)
        cell.addElement(p)
        row2.addElement(cell)
    table.addElement(row2)
    
    doc.text.addElement(table)
    
    # Save and extract
    temp_path = "/tmp/test_odt_merge.odt"
    doc.save(temp_path)
    
    doc = load(temp_path)
    styles = {}
    for style in doc.automaticstyles.getElementsByType(__import__('odf.style', fromlist=['Style']).Style):
        styles[style.getAttribute('name')] = style
    
    odt_table = doc.text.getElementsByType(Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    # Verify
    print("\n✓ Created ODT table with horizontal and vertical merges")
    cell_00 = table_segment.get_cell(0, 0)
    print(f"  Cell [0,0] colspan: {cell_00.col_span}, rowspan: {cell_00.row_span}")
    
    cell_10 = table_segment.get_cell(1, 0)
    print(f"  Cell [1,0] colspan: {cell_10.col_span}, rowspan: {cell_10.row_span}")
    
    assert cell_00.col_span == 2, "Cell [0,0] should have colspan=2"
    assert cell_00.row_span == 1, "Cell [0,0] should have rowspan=1"
    assert cell_10.col_span == 1, "Cell [1,0] should have colspan=1"
    assert cell_10.row_span == 2, "Cell [1,0] should have rowspan=2"
    
    print("\n✅ TEST 3 PASSED: ODT merge extraction working")
    return True


def test_docx_merge_reconstruction():
    """Test 4: Reconstruct DOCX with merged cells"""
    print("\n" + "="*70)
    print("TEST 4: DOCX MERGE RECONSTRUCTION")
    print("="*70)
    
    from translation.format_mapper import TableSegment, CellData, TextSegment
    
    table = TableSegment(num_rows=3, num_cols=3)
    
    # Cell [0,0]: Horizontal merge (2 cols)
    cell1 = CellData()
    cell1.text_segments = [TextSegment(text="Merged horizontal")]
    cell1.col_span = 2
    table.set_cell(0, 0, cell1)
    
    # Cell [0,1]: Covered by merge (still add empty data)
    cell2 = CellData()
    cell2.text_segments = [TextSegment(text="")]
    table.set_cell(0, 1, cell2)
    
    # Cell [0,2]: Normal
    cell3 = CellData()
    cell3.text_segments = [TextSegment(text="Normal")]
    table.set_cell(0, 2, cell3)
    
    # Cell [1,0]: Vertical merge (2 rows)
    cell4 = CellData()
    cell4.text_segments = [TextSegment(text="Merged vertical")]
    cell4.row_span = 2
    table.set_cell(1, 0, cell4)
    
    # Fill remaining cells
    for r in range(1, 3):
        for c in range(1, 3):
            if not (r == 2 and c == 0):  # Skip covered cell
                cell = CellData()
                cell.text_segments = [TextSegment(text=f"[{r},{c}]")]
                table.set_cell(r, c, cell)
    
    # Cell [2,0]: Covered by vertical merge
    cell5 = CellData()
    cell5.text_segments = [TextSegment(text="")]
    table.set_cell(2, 0, cell5)
    
    # Reconstruct
    doc = Document()
    docx_table = FormatMapper._reconstruct_table_to_docx(table, doc)
    
    # Verify merges
    def check_merge(cell, merge_type):
        """Check if cell has merge marker"""
        tcPr = cell._element.tcPr
        if tcPr is None:
            return None
        merge_elem = tcPr.find(qn(f'w:{merge_type}'))
        if merge_elem is not None:
            return merge_elem.get(qn('w:val'))
        return None
    
    print("\n✓ Reconstructed table with merges")
    
    h_merge_00 = check_merge(docx_table.rows[0].cells[0], 'hMerge')
    h_merge_01 = check_merge(docx_table.rows[0].cells[1], 'hMerge')
    v_merge_10 = check_merge(docx_table.rows[1].cells[0], 'vMerge')
    v_merge_20 = check_merge(docx_table.rows[2].cells[0], 'vMerge')
    
    print(f"  Cell [0,0] hMerge: {h_merge_00}")
    print(f"  Cell [0,1] hMerge: {h_merge_01}")
    print(f"  Cell [1,0] vMerge: {v_merge_10}")
    print(f"  Cell [2,0] vMerge: {v_merge_20}")
    
    assert h_merge_00 == 'restart', "Cell [0,0] should have hMerge=restart"
    assert h_merge_01 == 'continue', "Cell [0,1] should have hMerge=continue"
    assert v_merge_10 == 'restart', "Cell [1,0] should have vMerge=restart"
    assert v_merge_20 == 'continue', "Cell [2,0] should have vMerge=continue"
    
    print("\n✅ TEST 4 PASSED: DOCX merge reconstruction working")
    return True


def test_round_trip_merging():
    """Test 5: Full round-trip with merge preservation"""
    print("\n" + "="*70)
    print("TEST 5: ROUND-TRIP MERGE PRESERVATION")
    print("="*70)
    
    # Create original with complex merges
    doc = Document()
    table = doc.add_table(rows=3, cols=3)
    
    # Row 0: Merge columns 0-1
    table.rows[0].cells[0].text = "Merged H"
    cell = table.rows[0].cells[0]._element
    tcPr = cell.get_or_add_tcPr()
    hMerge = OxmlElement('w:hMerge')
    hMerge.set(qn('w:val'), 'restart')
    tcPr.append(hMerge)
    
    cell = table.rows[0].cells[1]._element
    tcPr = cell.get_or_add_tcPr()
    hMerge = OxmlElement('w:hMerge')
    hMerge.set(qn('w:val'), 'continue')
    tcPr.append(hMerge)
    
    table.rows[0].cells[2].text = "Normal"
    
    # Column 2: Merge rows 1-2
    table.rows[1].cells[2].text = "Merged V"
    cell = table.rows[1].cells[2]._element
    tcPr = cell.get_or_add_tcPr()
    vMerge = OxmlElement('w:vMerge')
    vMerge.set(qn('w:val'), 'restart')
    tcPr.append(vMerge)
    
    cell = table.rows[2].cells[2]._element
    tcPr = cell.get_or_add_tcPr()
    vMerge = OxmlElement('w:vMerge')
    vMerge.set(qn('w:val'), 'continue')
    tcPr.append(vMerge)
    
    # Fill other cells
    table.rows[1].cells[0].text = "A"
    table.rows[1].cells[1].text = "B"
    table.rows[2].cells[0].text = "C"
    table.rows[2].cells[1].text = "D"
    
    # Save
    temp_path = "/tmp/test_roundtrip_merge.docx"
    doc.save(temp_path)
    
    print("\n✓ Created original DOCX with merges")
    
    # Extract
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    print("✓ Extracted to TableSegment")
    print(f"  Cell [0,0]: colspan={table_segment.get_cell(0,0).col_span}")
    print(f"  Cell [1,2]: rowspan={table_segment.get_cell(1,2).row_span}")
    
    # Reconstruct
    new_doc = Document()
    new_table = FormatMapper._reconstruct_table_to_docx(table_segment, new_doc)
    
    output_path = "/tmp/test_roundtrip_merge_output.docx"
    new_doc.save(output_path)
    
    print("✓ Reconstructed to new DOCX")
    
    # Verify
    final_doc = Document(output_path)
    final_table = final_doc.tables[0]
    
    def get_merge(cell, merge_type):
        tcPr = cell._element.tcPr
        if tcPr is None:
            return None
        merge = tcPr.find(qn(f'w:{merge_type}'))
        return merge.get(qn('w:val')) if merge is not None else None
    
    h_00 = get_merge(final_table.rows[0].cells[0], 'hMerge')
    h_01 = get_merge(final_table.rows[0].cells[1], 'hMerge')
    v_12 = get_merge(final_table.rows[1].cells[2], 'vMerge')
    v_22 = get_merge(final_table.rows[2].cells[2], 'vMerge')
    
    print("✓ Verified final output:")
    print(f"  Cell [0,0] hMerge: {h_00}")
    print(f"  Cell [0,1] hMerge: {h_01}")
    print(f"  Cell [1,2] vMerge: {v_12}")
    print(f"  Cell [2,2] vMerge: {v_22}")
    
    assert h_00 == 'restart' and h_01 == 'continue', "Horizontal merge not preserved"
    assert v_12 == 'restart' and v_22 == 'continue', "Vertical merge not preserved"
    
    print("\n✅ TEST 5 PASSED: 100% round-trip fidelity for cell merging")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SESSION 63: CELL MERGING TEST SUITE")
    print("Testing extraction and reconstruction of merged table cells")
    print("="*70)
    
    results = []
    
    try:
        results.append(("DOCX Horizontal", test_docx_horizontal_merge()))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Horizontal", False))
    
    try:
        results.append(("DOCX Vertical", test_docx_vertical_merge()))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Vertical", False))
    
    try:
        results.append(("ODT Extraction", test_odt_merge_extraction()))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ODT Extraction", False))
    
    try:
        results.append(("DOCX Reconstruction", test_docx_merge_reconstruction()))
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Reconstruction", False))
    
    try:
        results.append(("Round-trip", test_round_trip_merging()))
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Round-trip", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Cell merging implementation complete.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review implementation.")
