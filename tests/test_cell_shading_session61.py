"""
Test suite for Session 61: Cell Shading (Background Colors)
Tests extraction and reconstruction of table cell background colors.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from odf.opendocument import OpenDocumentText
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf import style as odf_style
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))
from translation.format_mapper import FormatMapper


def test_docx_shading_extraction():
    """Test 1: Extract cell background colors from DOCX table"""
    print("\n" + "="*70)
    print("TEST 1: DOCX SHADING EXTRACTION")
    print("="*70)
    
    # Create test DOCX with shaded cells
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    
    # Add text to cells
    table.rows[0].cells[0].text = "Red cell"
    table.rows[0].cells[1].text = "Blue cell"
    table.rows[1].cells[0].text = "Green cell"
    table.rows[1].cells[1].text = "No shading"
    
    # Apply shading to cells using XML manipulation
    # Red cell (FF0000)
    tcPr = table.rows[0].cells[0]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), 'FF0000')
    tcPr.append(shd)
    
    # Blue cell (0000FF)
    tcPr = table.rows[0].cells[1]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), '0000FF')
    tcPr.append(shd)
    
    # Green cell (00FF00)
    tcPr = table.rows[1].cells[0]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), '00FF00')
    tcPr.append(shd)
    
    # Cell 1,1 has no shading
    
    # Save to temp file
    temp_path = "/tmp/test_shading.docx"
    doc.save(temp_path)
    
    # Extract table
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    # Verify shading extraction
    print("\n✓ Created 2x2 table with shading")
    print(f"  Cell [0,0] (Red): {table_segment.get_cell(0, 0).background_color}")
    print(f"  Cell [0,1] (Blue): {table_segment.get_cell(0, 1).background_color}")
    print(f"  Cell [1,0] (Green): {table_segment.get_cell(1, 0).background_color}")
    print(f"  Cell [1,1] (None): {table_segment.get_cell(1, 1).background_color}")
    
    assert table_segment.get_cell(0, 0).background_color == 'FF0000', "Red cell failed"
    assert table_segment.get_cell(0, 1).background_color == '0000FF', "Blue cell failed"
    assert table_segment.get_cell(1, 0).background_color == '00FF00', "Green cell failed"
    assert table_segment.get_cell(1, 1).background_color is None, "Unshaded cell should be None"
    
    print("\n✅ TEST 1 PASSED: DOCX shading extraction working")
    return True


def test_odt_shading_extraction():
    """Test 2: Extract cell background colors from ODT table"""
    print("\n" + "="*70)
    print("TEST 2: ODT SHADING EXTRACTION")
    print("="*70)
    
    # Create test ODT with shaded cells
    doc = OpenDocumentText()
    
    # Create cell styles with background colors
    red_style = odf_style.Style(name="red_cell", family="table-cell")
    red_props = odf_style.TableCellProperties()
    red_props.setAttribute("backgroundcolor", "#FF0000")
    red_style.addElement(red_props)
    doc.automaticstyles.addElement(red_style)
    
    blue_style = odf_style.Style(name="blue_cell", family="table-cell")
    blue_props = odf_style.TableCellProperties()
    blue_props.setAttribute("backgroundcolor", "#0000FF")
    blue_style.addElement(blue_props)
    doc.automaticstyles.addElement(blue_style)
    
    green_style = odf_style.Style(name="green_cell", family="table-cell")
    green_props = odf_style.TableCellProperties()
    green_props.setAttribute("backgroundcolor", "#00FF00")
    green_style.addElement(green_props)
    doc.automaticstyles.addElement(green_style)
    
    # Create table
    table = Table()
    
    # Row 1
    row1 = TableRow()
    cell1 = TableCell(stylename=red_style)
    p1 = P()
    p1.addText("Red cell")
    cell1.addElement(p1)
    row1.addElement(cell1)
    
    cell2 = TableCell(stylename=blue_style)
    p2 = P()
    p2.addText("Blue cell")
    cell2.addElement(p2)
    row1.addElement(cell2)
    table.addElement(row1)
    
    # Row 2
    row2 = TableRow()
    cell3 = TableCell(stylename=green_style)
    p3 = P()
    p3.addText("Green cell")
    cell3.addElement(p3)
    row2.addElement(cell3)
    
    cell4 = TableCell()  # No style
    p4 = P()
    p4.addText("No shading")
    cell4.addElement(p4)
    row2.addElement(cell4)
    table.addElement(row2)
    
    doc.text.addElement(table)
    
    # Save to temp file
    temp_path = "/tmp/test_shading.odt"
    doc.save(temp_path)
    
    # Extract table
    from odf.opendocument import load
    doc = load(temp_path)
    
    # Build styles dict
    styles = {}
    for style in doc.automaticstyles.getElementsByType(odf_style.Style):
        styles[style.getAttribute('name')] = style
    for style in doc.styles.getElementsByType(odf_style.Style):
        styles[style.getAttribute('name')] = style
    
    odt_table = doc.text.getElementsByType(Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    # Verify shading extraction
    print("\n✓ Created 2x2 ODT table with shading")
    print(f"  Cell [0,0] (Red): {table_segment.get_cell(0, 0).background_color}")
    print(f"  Cell [0,1] (Blue): {table_segment.get_cell(0, 1).background_color}")
    print(f"  Cell [1,0] (Green): {table_segment.get_cell(1, 0).background_color}")
    print(f"  Cell [1,1] (None): {table_segment.get_cell(1, 1).background_color}")
    
    assert table_segment.get_cell(0, 0).background_color == 'FF0000', "Red cell failed"
    assert table_segment.get_cell(0, 1).background_color == '0000FF', "Blue cell failed"
    assert table_segment.get_cell(1, 0).background_color == '00FF00', "Green cell failed"
    assert table_segment.get_cell(1, 1).background_color is None, "Unshaded cell should be None"
    
    print("\n✅ TEST 2 PASSED: ODT shading extraction working")
    return True


def test_docx_shading_reconstruction():
    """Test 3: Reconstruct DOCX table with cell shading"""
    print("\n" + "="*70)
    print("TEST 3: DOCX SHADING RECONSTRUCTION")
    print("="*70)
    
    # Create TableSegment with shading
    from translation.format_mapper import TableSegment, CellData, TextSegment
    
    table = TableSegment(num_rows=2, num_cols=2)
    
    # Cell [0,0]: Red background
    cell1 = CellData()
    cell1.text_segments = [TextSegment(text="Red cell")]
    cell1.background_color = "FF0000"
    table.set_cell(0, 0, cell1)
    
    # Cell [0,1]: Blue background
    cell2 = CellData()
    cell2.text_segments = [TextSegment(text="Blue cell")]
    cell2.background_color = "0000FF"
    table.set_cell(0, 1, cell2)
    
    # Cell [1,0]: Green background
    cell3 = CellData()
    cell3.text_segments = [TextSegment(text="Green cell")]
    cell3.background_color = "00FF00"
    table.set_cell(1, 0, cell3)
    
    # Cell [1,1]: No background
    cell4 = CellData()
    cell4.text_segments = [TextSegment(text="No shading")]
    table.set_cell(1, 1, cell4)
    
    # Reconstruct to DOCX
    doc = Document()
    docx_table = FormatMapper._reconstruct_table_to_docx(table, doc)
    
    # Verify shading was applied
    def get_cell_shading(cell):
        """Extract shading color from cell"""
        tcPr = cell._element.tcPr
        if tcPr is not None:
            shd = tcPr.find(qn('w:shd'))
            if shd is not None:
                return shd.get(qn('w:fill'))
        return None
    
    print("\n✓ Reconstructed table with shading")
    print(f"  Cell [0,0] shading: {get_cell_shading(docx_table.rows[0].cells[0])}")
    print(f"  Cell [0,1] shading: {get_cell_shading(docx_table.rows[0].cells[1])}")
    print(f"  Cell [1,0] shading: {get_cell_shading(docx_table.rows[1].cells[0])}")
    print(f"  Cell [1,1] shading: {get_cell_shading(docx_table.rows[1].cells[1])}")
    
    assert get_cell_shading(docx_table.rows[0].cells[0]) == "FF0000", "Red reconstruction failed"
    assert get_cell_shading(docx_table.rows[0].cells[1]) == "0000FF", "Blue reconstruction failed"
    assert get_cell_shading(docx_table.rows[1].cells[0]) == "00FF00", "Green reconstruction failed"
    assert get_cell_shading(docx_table.rows[1].cells[1]) is None, "Unshaded cell should have no shading"
    
    print("\n✅ TEST 3 PASSED: DOCX shading reconstruction working")
    return True


def test_odt_shading_reconstruction():
    """Test 4: Reconstruct ODT table with cell shading"""
    print("\n" + "="*70)
    print("TEST 4: ODT SHADING RECONSTRUCTION")
    print("="*70)
    
    # Create TableSegment with shading
    from translation.format_mapper import TableSegment, CellData, TextSegment
    
    table = TableSegment(num_rows=2, num_cols=2)
    
    # Cell [0,0]: Red background
    cell1 = CellData()
    cell1.text_segments = [TextSegment(text="Red cell")]
    cell1.background_color = "FF0000"
    table.set_cell(0, 0, cell1)
    
    # Cell [0,1]: Blue background
    cell2 = CellData()
    cell2.text_segments = [TextSegment(text="Blue cell")]
    cell2.background_color = "0000FF"
    table.set_cell(0, 1, cell2)
    
    # Cell [1,0]: Green background
    cell3 = CellData()
    cell3.text_segments = [TextSegment(text="Green cell")]
    cell3.background_color = "00FF00"
    table.set_cell(1, 0, cell3)
    
    # Cell [1,1]: No background
    cell4 = CellData()
    cell4.text_segments = [TextSegment(text="No shading")]
    table.set_cell(1, 1, cell4)
    
    # Reconstruct to ODT
    doc = OpenDocumentText()
    odt_table = FormatMapper._reconstruct_table_to_odt(table, doc)
    
    # Extract and verify shading
    def get_cell_background(cell):
        """Extract background color from ODT cell"""
        style_name = cell.getAttribute('stylename')
        if style_name:
            # Find style in automatic styles
            for style in doc.automaticstyles.getElementsByType(odf_style.Style):
                if style.getAttribute('name') == str(style_name):
                    props = style.getElementsByType(odf_style.TableCellProperties)
                    if props:
                        for (ns, name), value in props[0].attributes.items():
                            if name == 'background-color':
                                return value.replace('#', '')
        return None
    
    rows = odt_table.getElementsByType(TableRow)
    
    print("\n✓ Reconstructed ODT table with shading")
    cell_00 = rows[0].getElementsByType(TableCell)[0]
    cell_01 = rows[0].getElementsByType(TableCell)[1]
    cell_10 = rows[1].getElementsByType(TableCell)[0]
    cell_11 = rows[1].getElementsByType(TableCell)[1]
    
    bg_00 = get_cell_background(cell_00)
    bg_01 = get_cell_background(cell_01)
    bg_10 = get_cell_background(cell_10)
    bg_11 = get_cell_background(cell_11)
    
    print(f"  Cell [0,0] background: {bg_00}")
    print(f"  Cell [0,1] background: {bg_01}")
    print(f"  Cell [1,0] background: {bg_10}")
    print(f"  Cell [1,1] background: {bg_11}")
    
    assert bg_00 == "FF0000", "Red reconstruction failed"
    assert bg_01 == "0000FF", "Blue reconstruction failed"
    assert bg_10 == "00FF00", "Green reconstruction failed"
    assert bg_11 is None, "Unshaded cell should have no background"
    
    print("\n✅ TEST 4 PASSED: ODT shading reconstruction working")
    return True


def test_round_trip_shading():
    """Test 5: Full round-trip with shading preservation"""
    print("\n" + "="*70)
    print("TEST 5: ROUND-TRIP SHADING PRESERVATION")
    print("="*70)
    
    # Create original DOCX with shaded table
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    
    # Add content and shading
    table.rows[0].cells[0].text = "Yellow"
    tcPr = table.rows[0].cells[0]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), 'FFFF00')
    tcPr.append(shd)
    
    table.rows[0].cells[1].text = "Magenta"
    tcPr = table.rows[0].cells[1]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), 'FF00FF')
    tcPr.append(shd)
    
    table.rows[1].cells[0].text = "Cyan"
    tcPr = table.rows[1].cells[0]._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), '00FFFF')
    tcPr.append(shd)
    
    table.rows[1].cells[1].text = "Plain"
    
    # Save original
    temp_path = "/tmp/test_roundtrip.docx"
    doc.save(temp_path)
    
    print("\n✓ Created original DOCX with 4 cells (3 shaded)")
    
    # Step 1: Extract from DOCX
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    print("✓ Extracted to TableSegment")
    print(f"  Shading preserved: {table_segment.get_cell(0,0).background_color}, "
          f"{table_segment.get_cell(0,1).background_color}, "
          f"{table_segment.get_cell(1,0).background_color}, "
          f"{table_segment.get_cell(1,1).background_color}")
    
    # Step 2: Reconstruct to new DOCX
    new_doc = Document()
    new_table = FormatMapper._reconstruct_table_to_docx(table_segment, new_doc)
    
    # Save and reload
    output_path = "/tmp/test_roundtrip_output.docx"
    new_doc.save(output_path)
    
    print("✓ Reconstructed to new DOCX")
    
    # Step 3: Verify shading preserved
    final_doc = Document(output_path)
    final_table = final_doc.tables[0]
    
    def get_shading(cell):
        tcPr = cell._element.tcPr
        if tcPr is not None:
            shd = tcPr.find(qn('w:shd'))
            if shd is not None:
                return shd.get(qn('w:fill'))
        return None
    
    final_00 = get_shading(final_table.rows[0].cells[0])
    final_01 = get_shading(final_table.rows[0].cells[1])
    final_10 = get_shading(final_table.rows[1].cells[0])
    final_11 = get_shading(final_table.rows[1].cells[1])
    
    print("✓ Verified final output:")
    print(f"  Cell [0,0]: {final_00} (expected FFFF00)")
    print(f"  Cell [0,1]: {final_01} (expected FF00FF)")
    print(f"  Cell [1,0]: {final_10} (expected 00FFFF)")
    print(f"  Cell [1,1]: {final_11} (expected None)")
    
    assert final_00 == "FFFF00", "Yellow not preserved"
    assert final_01 == "FF00FF", "Magenta not preserved"
    assert final_10 == "00FFFF", "Cyan not preserved"
    assert final_11 is None, "Plain cell should have no shading"
    
    print("\n✅ TEST 5 PASSED: 100% round-trip fidelity for cell shading")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SESSION 61: CELL SHADING TEST SUITE")
    print("Testing extraction and reconstruction of table cell background colors")
    print("="*70)
    
    results = []
    
    try:
        results.append(("DOCX Extraction", test_docx_shading_extraction()))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Extraction", False))
    
    try:
        results.append(("ODT Extraction", test_odt_shading_extraction()))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ODT Extraction", False))
    
    try:
        results.append(("DOCX Reconstruction", test_docx_shading_reconstruction()))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Reconstruction", False))
    
    try:
        results.append(("ODT Reconstruction", test_odt_shading_reconstruction()))
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ODT Reconstruction", False))
    
    try:
        results.append(("Round-trip", test_round_trip_shading()))
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
        print("\n🎉 ALL TESTS PASSED! Cell shading implementation complete.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review implementation.")
