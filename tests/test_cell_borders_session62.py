"""
Test suite for Session 62: Cell Borders
Tests extraction and reconstruction of table cell borders.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from odf.opendocument import OpenDocumentText, load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from odf import style as odf_style
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('src'))
from translation.format_mapper import FormatMapper


def test_docx_border_extraction():
    """Test 1: Extract cell borders from DOCX table"""
    print("\n" + "="*70)
    print("TEST 1: DOCX BORDER EXTRACTION")
    print("="*70)
    
    # Create test DOCX with bordered cells
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    
    table.rows[0].cells[0].text = "All borders"
    table.rows[0].cells[1].text = "Top/Bottom"
    table.rows[1].cells[0].text = "Left only"
    table.rows[1].cells[1].text = "No borders"
    
    # Cell [0,0]: All 4 borders with different styles
    cell = table.rows[0].cells[0]
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:color'), 'FF0000')
    tcBorders.append(top)
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'double')
    bottom.set(qn('w:sz'), '16')
    bottom.set(qn('w:color'), '0000FF')
    tcBorders.append(bottom)
    
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'dashed')
    left.set(qn('w:sz'), '12')
    left.set(qn('w:color'), '00FF00')
    tcBorders.append(left)
    
    right = OxmlElement('w:right')
    right.set(qn('w:val'), 'thick')
    right.set(qn('w:sz'), '24')
    right.set(qn('w:color'), 'FF00FF')
    tcBorders.append(right)
    
    tcPr.append(tcBorders)
    
    # Cell [0,1]: Top and bottom only
    cell = table.rows[0].cells[1]
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:color'), '000000')
    tcBorders.append(top)
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:color'), '000000')
    tcBorders.append(bottom)
    
    tcPr.append(tcBorders)
    
    # Cell [1,0]: Left only
    cell = table.rows[1].cells[0]
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'thick')
    left.set(qn('w:sz'), '20')
    left.set(qn('w:color'), 'FFFF00')
    tcBorders.append(left)
    
    tcPr.append(tcBorders)
    
    # Cell [1,1]: No borders
    
    # Save and extract
    temp_path = "/tmp/test_borders.docx"
    doc.save(temp_path)
    
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    # Verify extraction
    print("\n✓ Created 2x2 table with various borders")
    
    cell_00 = table_segment.get_cell(0, 0)
    print(f"\nCell [0,0] (All borders): {len(cell_00.borders) if cell_00.borders else 0} sides")
    if cell_00.borders:
        for side, info in cell_00.borders.items():
            print(f"  {side}: {info['style']}, {info['width']}, {info['color']}")
    
    cell_01 = table_segment.get_cell(0, 1)
    print(f"\nCell [0,1] (Top/Bottom): {len(cell_01.borders) if cell_01.borders else 0} sides")
    if cell_01.borders:
        for side in cell_01.borders:
            print(f"  {side}")
    
    cell_10 = table_segment.get_cell(1, 0)
    print(f"\nCell [1,0] (Left only): {len(cell_10.borders) if cell_10.borders else 0} sides")
    if cell_10.borders:
        for side in cell_10.borders:
            print(f"  {side}")
    
    cell_11 = table_segment.get_cell(1, 1)
    print(f"\nCell [1,1] (No borders): {cell_11.borders}")
    
    # Assertions
    assert cell_00.borders is not None, "Cell [0,0] should have borders"
    assert len(cell_00.borders) == 4, "Cell [0,0] should have 4 borders"
    assert 'top' in cell_00.borders and cell_00.borders['top']['style'] == 'single'
    assert 'bottom' in cell_00.borders and cell_00.borders['bottom']['style'] == 'double'
    assert 'left' in cell_00.borders and cell_00.borders['left']['style'] == 'dashed'
    assert 'right' in cell_00.borders and cell_00.borders['right']['style'] == 'thick'
    
    assert cell_01.borders is not None and len(cell_01.borders) == 2
    assert 'top' in cell_01.borders and 'bottom' in cell_01.borders
    
    assert cell_10.borders is not None and len(cell_10.borders) == 1
    assert 'left' in cell_10.borders
    
    assert cell_11.borders is None, "Cell [1,1] should have no borders"
    
    print("\n✅ TEST 1 PASSED: DOCX border extraction working")
    return True


def test_docx_border_reconstruction():
    """Test 2: Reconstruct DOCX table with cell borders"""
    print("\n" + "="*70)
    print("TEST 2: DOCX BORDER RECONSTRUCTION")
    print("="*70)
    
    from translation.format_mapper import TableSegment, CellData, TextSegment
    
    table = TableSegment(num_rows=2, num_cols=2)
    
    # Cell [0,0]: All borders
    cell1 = CellData()
    cell1.text_segments = [TextSegment(text="All borders")]
    cell1.borders = {
        'top': {'style': 'single', 'width': '8', 'color': 'FF0000'},
        'bottom': {'style': 'double', 'width': '16', 'color': '0000FF'},
        'left': {'style': 'dashed', 'width': '12', 'color': '00FF00'},
        'right': {'style': 'thick', 'width': '24', 'color': 'FF00FF'}
    }
    table.set_cell(0, 0, cell1)
    
    # Cell [0,1]: Top/Bottom
    cell2 = CellData()
    cell2.text_segments = [TextSegment(text="Top/Bottom")]
    cell2.borders = {
        'top': {'style': 'single', 'width': '8', 'color': '000000'},
        'bottom': {'style': 'single', 'width': '8', 'color': '000000'}
    }
    table.set_cell(0, 1, cell2)
    
    # Cell [1,0]: Left only
    cell3 = CellData()
    cell3.text_segments = [TextSegment(text="Left only")]
    cell3.borders = {
        'left': {'style': 'thick', 'width': '20', 'color': 'FFFF00'}
    }
    table.set_cell(1, 0, cell3)
    
    # Cell [1,1]: No borders
    cell4 = CellData()
    cell4.text_segments = [TextSegment(text="No borders")]
    table.set_cell(1, 1, cell4)
    
    # Reconstruct
    doc = Document()
    docx_table = FormatMapper._reconstruct_table_to_docx(table, doc)
    
    # Verify borders
    def get_cell_borders(cell):
        """Extract borders from cell"""
        tcPr = cell._element.tcPr
        if tcPr is None:
            return None
        tcBorders = tcPr.find(qn('w:tcBorders'))
        if tcBorders is None:
            return None
        
        borders = {}
        for side in ['top', 'bottom', 'left', 'right']:
            border = tcBorders.find(qn(f'w:{side}'))
            if border is not None:
                borders[side] = {
                    'style': border.get(qn('w:val')),
                    'width': border.get(qn('w:sz')),
                    'color': border.get(qn('w:color'))
                }
        return borders if borders else None
    
    print("\n✓ Reconstructed table with borders")
    
    borders_00 = get_cell_borders(docx_table.rows[0].cells[0])
    print(f"\nCell [0,0]: {len(borders_00) if borders_00 else 0} borders")
    
    borders_01 = get_cell_borders(docx_table.rows[0].cells[1])
    print(f"Cell [0,1]: {len(borders_01) if borders_01 else 0} borders")
    
    borders_10 = get_cell_borders(docx_table.rows[1].cells[0])
    print(f"Cell [1,0]: {len(borders_10) if borders_10 else 0} borders")
    
    borders_11 = get_cell_borders(docx_table.rows[1].cells[1])
    print(f"Cell [1,1]: {borders_11}")
    
    # Assertions
    assert borders_00 is not None and len(borders_00) == 4
    assert borders_00['top']['style'] == 'single'
    assert borders_00['bottom']['style'] == 'double'
    
    assert borders_01 is not None and len(borders_01) == 2
    assert 'top' in borders_01 and 'bottom' in borders_01
    
    assert borders_10 is not None and len(borders_10) == 1
    assert 'left' in borders_10
    
    assert borders_11 is None
    
    print("\n✅ TEST 2 PASSED: DOCX border reconstruction working")
    return True


def test_odt_border_extraction():
    """Test 3: Extract cell borders from ODT table"""
    print("\n" + "="*70)
    print("TEST 3: ODT BORDER EXTRACTION")
    print("="*70)
    
    doc = OpenDocumentText()
    
    # Create cell styles with borders
    style1 = odf_style.Style(name="all_borders", family="table-cell")
    props1 = odf_style.TableCellProperties()
    props1.setAttribute("bordertop", "0.05cm solid #FF0000")
    props1.setAttribute("borderbottom", "0.10cm double #0000FF")
    props1.setAttribute("borderleft", "0.08cm dashed #00FF00")
    props1.setAttribute("borderright", "0.15cm solid #FF00FF")
    style1.addElement(props1)
    doc.automaticstyles.addElement(style1)
    
    style2 = odf_style.Style(name="top_bottom", family="table-cell")
    props2 = odf_style.TableCellProperties()
    props2.setAttribute("bordertop", "0.05cm solid #000000")
    props2.setAttribute("borderbottom", "0.05cm solid #000000")
    style2.addElement(props2)
    doc.automaticstyles.addElement(style2)
    
    # Create table
    table = Table()
    
    row1 = TableRow()
    cell1 = TableCell(stylename=style1)
    p1 = P()
    p1.addText("All borders")
    cell1.addElement(p1)
    row1.addElement(cell1)
    
    cell2 = TableCell(stylename=style2)
    p2 = P()
    p2.addText("Top/Bottom")
    cell2.addElement(p2)
    row1.addElement(cell2)
    table.addElement(row1)
    
    row2 = TableRow()
    cell3 = TableCell()
    p3 = P()
    p3.addText("No borders")
    cell3.addElement(p3)
    row2.addElement(cell3)
    table.addElement(row2)
    
    doc.text.addElement(table)
    
    # Save and extract
    temp_path = "/tmp/test_borders.odt"
    doc.save(temp_path)
    
    doc = load(temp_path)
    styles = {}
    for style in doc.automaticstyles.getElementsByType(odf_style.Style):
        styles[style.getAttribute('name')] = style
    
    odt_table = doc.text.getElementsByType(Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    # Verify extraction
    print("\n✓ Created ODT table with borders")
    
    cell_00 = table_segment.get_cell(0, 0)
    print(f"\nCell [0,0] (All borders): {len(cell_00.borders) if cell_00.borders else 0} sides")
    if cell_00.borders:
        for side, info in cell_00.borders.items():
            print(f"  {side}: {info['style']}, {info['width']}, {info['color']}")
    
    cell_01 = table_segment.get_cell(0, 1)
    print(f"\nCell [0,1] (Top/Bottom): {len(cell_01.borders) if cell_01.borders else 0} sides")
    
    cell_10 = table_segment.get_cell(1, 0)
    print(f"\nCell [1,0] (No borders): {cell_10.borders}")
    
    # Assertions
    assert cell_00.borders is not None and len(cell_00.borders) == 4
    assert 'top' in cell_00.borders
    assert 'bottom' in cell_00.borders and cell_00.borders['bottom']['style'] == 'double'
    assert 'left' in cell_00.borders and cell_00.borders['left']['style'] == 'dashed'
    
    assert cell_01.borders is not None and len(cell_01.borders) == 2
    assert 'top' in cell_01.borders and 'bottom' in cell_01.borders
    
    assert cell_10.borders is None
    
    print("\n✅ TEST 3 PASSED: ODT border extraction working")
    return True


def test_round_trip_borders():
    """Test 4: Full round-trip with border preservation"""
    print("\n" + "="*70)
    print("TEST 4: ROUND-TRIP BORDER PRESERVATION")
    print("="*70)
    
    # Create original DOCX with borders
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    
    table.rows[0].cells[0].text = "Red top border"
    cell = table.rows[0].cells[0]
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '12')
    top.set(qn('w:color'), 'FF0000')
    tcBorders.append(top)
    tcPr.append(tcBorders)
    
    table.rows[0].cells[1].text = "Blue all around"
    cell = table.rows[0].cells[1]
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top', 'bottom', 'left', 'right']:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'double')
        border.set(qn('w:sz'), '16')
        border.set(qn('w:color'), '0000FF')
        tcBorders.append(border)
    tcPr.append(tcBorders)
    
    temp_path = "/tmp/test_roundtrip_borders.docx"
    doc.save(temp_path)
    
    print("\n✓ Created original DOCX with borders")
    
    # Extract
    doc = Document(temp_path)
    docx_table = doc.tables[0]
    table_segment = FormatMapper._extract_table_from_docx(docx_table)
    
    print("✓ Extracted to TableSegment")
    print(f"  Cell [0,0] borders: {len(table_segment.get_cell(0,0).borders) if table_segment.get_cell(0,0).borders else 0}")
    print(f"  Cell [0,1] borders: {len(table_segment.get_cell(0,1).borders) if table_segment.get_cell(0,1).borders else 0}")
    
    # Reconstruct
    new_doc = Document()
    new_table = FormatMapper._reconstruct_table_to_docx(table_segment, new_doc)
    
    output_path = "/tmp/test_roundtrip_borders_output.docx"
    new_doc.save(output_path)
    
    print("✓ Reconstructed to new DOCX")
    
    # Verify
    final_doc = Document(output_path)
    final_table = final_doc.tables[0]
    
    def get_borders(cell):
        tcPr = cell._element.tcPr
        if not tcPr:
            return None
        tcBorders = tcPr.find(qn('w:tcBorders'))
        if not tcBorders:
            return None
        borders = {}
        for side in ['top', 'bottom', 'left', 'right']:
            border = tcBorders.find(qn(f'w:{side}'))
            if border is not None:
                borders[side] = border.get(qn('w:color'))
        return borders
    
    cell_0_borders = get_borders(final_table.rows[0].cells[0])
    cell_1_borders = get_borders(final_table.rows[0].cells[1])
    
    print("✓ Verified final output:")
    print(f"  Cell [0,0]: {len(cell_0_borders) if cell_0_borders else 0} border(s)")
    print(f"  Cell [0,1]: {len(cell_1_borders) if cell_1_borders else 0} border(s)")
    
    assert cell_0_borders is not None and len(cell_0_borders) == 1
    assert 'top' in cell_0_borders and cell_0_borders['top'] == 'FF0000'
    
    assert cell_1_borders is not None and len(cell_1_borders) == 4
    assert all(color == '0000FF' for color in cell_1_borders.values())
    
    print("\n✅ TEST 4 PASSED: 100% round-trip fidelity for cell borders")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SESSION 62: CELL BORDERS TEST SUITE")
    print("Testing extraction and reconstruction of table cell borders")
    print("="*70)
    
    results = []
    
    try:
        results.append(("DOCX Extraction", test_docx_border_extraction()))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Extraction", False))
    
    try:
        results.append(("DOCX Reconstruction", test_docx_border_reconstruction()))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("DOCX Reconstruction", False))
    
    try:
        results.append(("ODT Extraction", test_odt_border_extraction()))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ODT Extraction", False))
    
    try:
        results.append(("Round-trip", test_round_trip_borders()))
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
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
        print("\n🎉 ALL TESTS PASSED! Cell borders implementation complete.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review implementation.")
