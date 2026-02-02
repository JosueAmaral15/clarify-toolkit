#!/usr/bin/env python3
"""
Session 60: Test ODT table reconstruction
Verify that tables can be reconstructed from TableSegment to ODT with correct formatting
"""

from src.translation.format_mapper import FormatMapper, TableSegment, CellData, TextSegment, FormatBit
from odf.opendocument import OpenDocumentText, load as odt_load
from odf.table import Table, TableRow, TableCell
from odf.text import P, Span
from odf.style import Style, TextProperties

def test_basic_odt_table_reconstruction():
    """Test reconstructing a simple ODT table."""
    print("=" * 70)
    print("TEST 1: Basic ODT Table Reconstruction")
    print("=" * 70)
    
    # Create TableSegment manually
    table = TableSegment(2, 3)
    
    # Fill cells with text
    for row in range(2):
        for col in range(3):
            cell = CellData()
            cell.text_segments = [TextSegment(text=f"Cell [{row},{col}]")]
            table.set_cell(row, col, cell)
    
    # Reconstruct to ODT
    doc = OpenDocumentText()
    FormatMapper._reconstruct_table_to_odt(table, doc)
    
    test_file = "/tmp/test_odt_reconstruct_basic_session60.odt"
    doc.save(test_file)
    print(f"✓ Created reconstructed ODT: {test_file}")
    
    # Reload and verify
    doc = odt_load(test_file)
    from odf import table as odf_table
    
    tables = doc.getElementsByType(odf_table.Table)
    assert len(tables) == 1, f"Expected 1 table, got {len(tables)}"
    
    reloaded_table = tables[0]
    rows = reloaded_table.getElementsByType(odf_table.TableRow)
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
    
    print(f"✓ Table dimensions: 2 rows")
    
    # Check first row has 3 cells
    cells = rows[0].getElementsByType(odf_table.TableCell)
    assert len(cells) == 3, f"Expected 3 cols, got {len(cells)}"
    print(f"✓ Table dimensions: 3 columns")
    
    # Check cell contents
    from odf import text as odf_text
    cell_00 = cells[0]
    paras = cell_00.getElementsByType(odf_text.P)
    assert len(paras) > 0, "Cell [0,0] has no paragraphs"
    
    # Extract text
    text_parts = []
    for para in paras:
        for node in para.childNodes:
            if hasattr(node, 'data'):
                text_parts.append(node.data)
    text = "".join(text_parts)
    assert "Cell [0,0]" in text, f"Expected 'Cell [0,0]', got '{text}'"
    print(f"✓ Cell [0,0] content correct")
    
    print("\n✓ TEST 1 PASSED\n")
    return True


def test_odt_formatted_cell_reconstruction():
    """Test reconstructing ODT table with formatted cells."""
    print("=" * 70)
    print("TEST 2: ODT Formatted Cell Reconstruction")
    print("=" * 70)
    
    # Create table with formatted cells
    table = TableSegment(1, 3)
    
    # Cell [0,0]: Bold
    cell_0 = CellData()
    cell_0.text_segments = [TextSegment(text="Bold Text", format_bits=FormatBit.BOLD)]
    table.set_cell(0, 0, cell_0)
    
    # Cell [0,1]: Italic + Red
    cell_1 = CellData()
    cell_1.text_segments = [
        TextSegment(
            text="Red Italic",
            format_bits=FormatBit.ITALIC | FormatBit.FONT_COLOR,
            metadata="FF0000"
        )
    ]
    table.set_cell(0, 1, cell_1)
    
    # Cell [0,2]: Blue + 16pt
    cell_2 = CellData()
    cell_2.text_segments = [
        TextSegment(
            text="Blue 16pt",
            format_bits=FormatBit.FONT_COLOR | FormatBit.FONT_SIZE,
            metadata="0000FF,16"
        )
    ]
    table.set_cell(0, 2, cell_2)
    
    # Reconstruct
    doc = OpenDocumentText()
    FormatMapper._reconstruct_table_to_odt(table, doc)
    
    test_file = "/tmp/test_odt_reconstruct_formatted_session60.odt"
    doc.save(test_file)
    print(f"✓ Created reconstructed ODT: {test_file}")
    
    # Reload and verify
    doc = odt_load(test_file)
    from odf import table as odf_table, text as odf_text, style as odf_style
    
    # Build styles dictionary
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    tables = doc.getElementsByType(odf_table.Table)
    reloaded_table = tables[0]
    rows = reloaded_table.getElementsByType(odf_table.TableRow)
    cells = rows[0].getElementsByType(odf_table.TableCell)
    
    # Helper to get attribute from text properties
    def get_attr(text_prop, attr_name):
        if hasattr(text_prop, 'attributes'):
            for (ns, name), value in text_prop.attributes.items():
                if name == attr_name:
                    return value
        return None
    
    # Check Cell [0,0]: Bold
    cell = cells[0]
    paras = cell.getElementsByType(odf_text.P)
    spans = paras[0].getElementsByType(odf_text.Span)
    assert len(spans) > 0, "Cell 0 should have span"
    
    span_style_name = spans[0].getAttribute('stylename')
    assert span_style_name in styles, f"Style {span_style_name} not found"
    
    style = styles[span_style_name]
    text_props = style.getElementsByType(odf_style.TextProperties)
    assert len(text_props) > 0, "Cell 0 style should have TextProperties"
    
    fw = get_attr(text_props[0], 'font-weight')
    assert fw == 'bold', f"Expected bold, got {fw}"
    print(f"✓ Cell [0,0]: Bold preserved")
    
    # Check Cell [0,1]: Italic + Red
    cell = cells[1]
    paras = cell.getElementsByType(odf_text.P)
    spans = paras[0].getElementsByType(odf_text.Span)
    
    span_style_name = spans[0].getAttribute('stylename')
    style = styles[span_style_name]
    text_props = style.getElementsByType(odf_style.TextProperties)
    
    fs = get_attr(text_props[0], 'font-style')
    assert fs == 'italic', f"Expected italic, got {fs}"
    
    color = get_attr(text_props[0], 'color')
    assert color == '#FF0000', f"Expected #FF0000, got {color}"
    print(f"✓ Cell [0,1]: Italic + Red preserved")
    
    # Check Cell [0,2]: Blue + 16pt
    cell = cells[2]
    paras = cell.getElementsByType(odf_text.P)
    spans = paras[0].getElementsByType(odf_text.Span)
    
    span_style_name = spans[0].getAttribute('stylename')
    style = styles[span_style_name]
    text_props = style.getElementsByType(odf_style.TextProperties)
    
    color = get_attr(text_props[0], 'color')
    assert color == '#0000FF', f"Expected #0000FF, got {color}"
    
    size = get_attr(text_props[0], 'font-size')
    assert size == '16pt', f"Expected 16pt, got {size}"
    print(f"✓ Cell [0,2]: Blue + 16pt preserved")
    
    print("\n✓ TEST 2 PASSED\n")
    return True


def test_odt_mixed_formatting():
    """Test ODT cell with mixed formatting."""
    print("=" * 70)
    print("TEST 3: ODT Mixed Formatting in Cell")
    print("=" * 70)
    
    # Create cell with mixed formatting
    table = TableSegment(1, 1)
    cell = CellData()
    cell.text_segments = [
        TextSegment(text="Normal "),
        TextSegment(text="Bold ", format_bits=FormatBit.BOLD),
        TextSegment(text="Italic", format_bits=FormatBit.ITALIC)
    ]
    table.set_cell(0, 0, cell)
    
    # Reconstruct
    doc = OpenDocumentText()
    FormatMapper._reconstruct_table_to_odt(table, doc)
    
    test_file = "/tmp/test_odt_reconstruct_mixed_session60.odt"
    doc.save(test_file)
    print(f"✓ Created reconstructed ODT: {test_file}")
    
    # Reload and verify
    doc = odt_load(test_file)
    from odf import table as odf_table, text as odf_text, style as odf_style
    
    # Build styles
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    tables = doc.getElementsByType(odf_table.Table)
    cell = tables[0].getElementsByType(odf_table.TableRow)[0].getElementsByType(odf_table.TableCell)[0]
    para = cell.getElementsByType(odf_text.P)[0]
    
    # Check we have plain text + 2 spans
    # Count nodes
    text_nodes = []
    span_nodes = []
    for node in para.childNodes:
        if hasattr(node, 'data'):
            text_nodes.append(node.data)
        elif hasattr(node, 'qname') and node.qname[1] == 'span':
            span_nodes.append(node)
    
    assert len(text_nodes) > 0, "Should have plain text nodes"
    assert len(span_nodes) >= 2, f"Should have 2+ spans, got {len(span_nodes)}"
    print(f"✓ Found {len(text_nodes)} text nodes and {len(span_nodes)} spans")
    
    print("\n✓ TEST 3 PASSED\n")
    return True


def test_odt_multi_paragraph():
    """Test ODT cell with multiple paragraphs."""
    print("=" * 70)
    print("TEST 4: ODT Multi-paragraph Cell")
    print("=" * 70)
    
    # Create cell with 2 paragraphs
    table = TableSegment(1, 1)
    cell = CellData()
    cell.text_segments = [
        TextSegment(text="First paragraph", format_bits=FormatBit.BOLD),
        TextSegment(text="\n"),  # Paragraph break
        TextSegment(text="Second paragraph", format_bits=FormatBit.ITALIC)
    ]
    table.set_cell(0, 0, cell)
    
    # Reconstruct
    doc = OpenDocumentText()
    FormatMapper._reconstruct_table_to_odt(table, doc)
    
    test_file = "/tmp/test_odt_reconstruct_multipara_session60.odt"
    doc.save(test_file)
    print(f"✓ Created reconstructed ODT: {test_file}")
    
    # Reload and verify
    doc = odt_load(test_file)
    from odf import table as odf_table, text as odf_text
    
    tables = doc.getElementsByType(odf_table.Table)
    cell = tables[0].getElementsByType(odf_table.TableRow)[0].getElementsByType(odf_table.TableCell)[0]
    paras = cell.getElementsByType(odf_text.P)
    
    assert len(paras) >= 2, f"Expected 2+ paragraphs, got {len(paras)}"
    print(f"✓ Cell has {len(paras)} paragraphs")
    
    print("\n✓ TEST 4 PASSED\n")
    return True


def test_odt_round_trip():
    """Test ODT extract → reconstruct round-trip."""
    print("=" * 70)
    print("TEST 5: ODT Round-trip (Extract → Reconstruct)")
    print("=" * 70)
    
    # Create original ODT with formatted table
    doc = OpenDocumentText()
    
    # Create styles
    bold_style = Style(name="BoldStyle", family="text")
    bold_props = TextProperties(fontweight="bold")
    bold_style.addElement(bold_props)
    doc.automaticstyles.addElement(bold_style)
    
    red_style = Style(name="RedStyle", family="text")
    red_props = TextProperties(color="#FF0000")
    red_style.addElement(red_props)
    doc.automaticstyles.addElement(red_style)
    
    # Create table
    odt_table = Table()
    row = TableRow()
    
    # Cell 1: Bold
    cell1 = TableCell()
    para1 = P()
    span1 = Span(stylename=bold_style)
    span1.addText("Bold")
    para1.addElement(span1)
    cell1.addElement(para1)
    row.addElement(cell1)
    
    # Cell 2: Red
    cell2 = TableCell()
    para2 = P()
    span2 = Span(stylename=red_style)
    span2.addText("Red")
    para2.addElement(span2)
    cell2.addElement(para2)
    row.addElement(cell2)
    
    odt_table.addElement(row)
    doc.text.addElement(odt_table)
    
    original_file = "/tmp/test_odt_roundtrip_original_session60.odt"
    doc.save(original_file)
    print(f"✓ Created original ODT: {original_file}")
    
    # Extract
    doc = odt_load(original_file)
    
    # Build styles
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    from odf import table as odf_table
    tables = doc.getElementsByType(odf_table.Table)
    table_segment = FormatMapper._extract_table_from_odt(tables[0], styles)
    print(f"✓ Extracted TableSegment: 1x2")
    
    # Reconstruct
    doc2 = OpenDocumentText()
    FormatMapper._reconstruct_table_to_odt(table_segment, doc2)
    
    reconstructed_file = "/tmp/test_odt_roundtrip_reconstructed_session60.odt"
    doc2.save(reconstructed_file)
    print(f"✓ Reconstructed ODT: {reconstructed_file}")
    
    # Verify
    doc2 = odt_load(reconstructed_file)
    
    # Build styles for reconstructed
    styles2 = {}
    for style_elem in doc2.automaticstyles.childNodes + doc2.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles2[sname] = style_elem
            except:
                pass
    
    from odf import text as odf_text, style as odf_style
    
    tables = doc2.getElementsByType(odf_table.Table)
    rows = tables[0].getElementsByType(odf_table.TableRow)
    cells = rows[0].getElementsByType(odf_table.TableCell)
    
    # Helper
    def get_attr(text_prop, attr_name):
        if hasattr(text_prop, 'attributes'):
            for (ns, name), value in text_prop.attributes.items():
                if name == attr_name:
                    return value
        return None
    
    # Check Cell 1: Bold
    paras = cells[0].getElementsByType(odf_text.P)
    spans = paras[0].getElementsByType(odf_text.Span)
    if spans:
        span_style_name = spans[0].getAttribute('stylename')
        style = styles2[span_style_name]
        text_props = style.getElementsByType(odf_style.TextProperties)
        fw = get_attr(text_props[0], 'font-weight')
        assert fw == 'bold', f"Expected bold, got {fw}"
        print(f"✓ Cell [0,0]: Bold preserved")
    
    # Check Cell 2: Red
    paras = cells[1].getElementsByType(odf_text.P)
    spans = paras[0].getElementsByType(odf_text.Span)
    if spans:
        span_style_name = spans[0].getAttribute('stylename')
        style = styles2[span_style_name]
        text_props = style.getElementsByType(odf_style.TextProperties)
        color = get_attr(text_props[0], 'color')
        assert color == '#FF0000', f"Expected #FF0000, got {color}"
        print(f"✓ Cell [0,1]: Red preserved")
    
    print("\n✓ TEST 5 PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SESSION 60: ODT TABLE RECONSTRUCTION TESTING")
    print("=" * 70 + "\n")
    
    results = []
    
    try:
        test_basic_odt_table_reconstruction()
        results.append(("Basic ODT Reconstruction", True))
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Basic ODT Reconstruction", False))
    
    try:
        test_odt_formatted_cell_reconstruction()
        results.append(("ODT Formatted Cells", True))
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Formatted Cells", False))
    
    try:
        test_odt_mixed_formatting()
        results.append(("ODT Mixed Formatting", True))
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Mixed Formatting", False))
    
    try:
        test_odt_multi_paragraph()
        results.append(("ODT Multi-paragraph", True))
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Multi-paragraph", False))
    
    try:
        test_odt_round_trip()
        results.append(("ODT Round-trip", True))
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Round-trip", False))
    
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
        print("\n✓ SESSION 60 ODT TABLE RECONSTRUCTION: COMPLETE")
    else:
        print("\n✗ SESSION 60: SOME TESTS FAILED")
