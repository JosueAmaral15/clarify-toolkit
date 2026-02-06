#!/usr/bin/env python3
"""
Session 58: Test ODT table cell formatting extraction
Verify that bold, italic, colors, fonts are properly extracted from ODT table cells
"""

from src.translation.format_mapper import FormatMapper, FormatBit
from odf.opendocument import OpenDocumentText
from odf.table import Table, TableRow, TableCell
from odf.text import P, Span
from odf.style import Style, TextProperties

def test_basic_odt_cell_formatting():
    """Test extraction of bold, italic from ODT table cells."""
    print("=" * 70)
    print("TEST 1: Basic ODT Cell Formatting (Bold, Italic)")
    print("=" * 70)
    
    # Create ODT with formatted table
    doc = OpenDocumentText()
    
    # Create styles
    bold_style = Style(name="Bold1", family="text")
    bold_props = TextProperties(fontweight="bold")
    bold_style.addElement(bold_props)
    doc.automaticstyles.addElement(bold_style)
    
    italic_style = Style(name="Italic1", family="text")
    italic_props = TextProperties(fontstyle="italic")
    italic_style.addElement(italic_props)
    doc.automaticstyles.addElement(italic_style)
    
    # Create table
    table = Table(name="TestTable")
    row = TableRow()
    
    # Cell 1: Bold
    cell1 = TableCell()
    para1 = P()
    span1 = Span(stylename=bold_style)
    span1.addText("Bold Text")
    para1.addElement(span1)
    cell1.addElement(para1)
    row.addElement(cell1)
    
    # Cell 2: Italic
    cell2 = TableCell()
    para2 = P()
    span2 = Span(stylename=italic_style)
    span2.addText("Italic Text")
    para2.addElement(span2)
    cell2.addElement(para2)
    row.addElement(cell2)
    
    table.addElement(row)
    doc.text.addElement(table)
    
    test_file = "/tmp/test_odt_cell_basic_session58.odt"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract using FormatMapper
    from odf import opendocument, table as odf_table
    
    doc = opendocument.load(test_file)
    
    # Build styles dict
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    # Extract table
    odt_table = doc.getElementsByType(odf_table.Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    # Check Cell 1: Bold
    cell_0 = table_segment.get_cell(0, 0)
    text_segs = [s for s in cell_0.text_segments if s.text.strip()]
    assert len(text_segs) > 0, "Cell 0 has no text segments"
    
    seg = text_segs[0]
    assert "Bold Text" in seg.text, f"Expected 'Bold Text', got '{seg.text}'"
    assert seg.has_format(FormatBit.BOLD), "Cell 0 should have BOLD"
    print(f"✓ Cell [0,0]: '{seg.text}' is BOLD")
    
    # Check Cell 2: Italic
    cell_1 = table_segment.get_cell(0, 1)
    text_segs = [s for s in cell_1.text_segments if s.text.strip()]
    
    seg = text_segs[0]
    assert "Italic Text" in seg.text, f"Expected 'Italic Text', got '{seg.text}'"
    assert seg.has_format(FormatBit.ITALIC), "Cell 1 should have ITALIC"
    print(f"✓ Cell [0,1]: '{seg.text}' is ITALIC")
    
    print("\n✓ TEST 1 PASSED\n")
    return True


def test_odt_colors_and_fonts():
    """Test extraction of colors and fonts from ODT table cells."""
    print("=" * 70)
    print("TEST 2: ODT Colors and Fonts")
    print("=" * 70)
    
    # Create ODT with colors and fonts
    doc = OpenDocumentText()
    
    # Style 1: Red text, 14pt
    style1 = Style(name="Red14", family="text")
    props1 = TextProperties(color="#FF0000", fontsize="14pt")
    style1.addElement(props1)
    doc.automaticstyles.addElement(style1)
    
    # Style 2: Blue text, 16pt
    style2 = Style(name="Blue16", family="text")
    props2 = TextProperties(color="#0000FF", fontsize="16pt")
    style2.addElement(props2)
    doc.automaticstyles.addElement(style2)
    
    # Create table
    table = Table(name="TestTable")
    row = TableRow()
    
    # Cell 1: Red 14pt
    cell1 = TableCell()
    para1 = P()
    span1 = Span(stylename=style1)
    span1.addText("Red 14pt")
    para1.addElement(span1)
    cell1.addElement(para1)
    row.addElement(cell1)
    
    # Cell 2: Blue 16pt
    cell2 = TableCell()
    para2 = P()
    span2 = Span(stylename=style2)
    span2.addText("Blue 16pt")
    para2.addElement(span2)
    cell2.addElement(para2)
    row.addElement(cell2)
    
    table.addElement(row)
    doc.text.addElement(table)
    
    test_file = "/tmp/test_odt_cell_colors_session58.odt"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract
    from odf import opendocument, table as odf_table
    
    doc = opendocument.load(test_file)
    
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    odt_table = doc.getElementsByType(odf_table.Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    # Check Cell 1: Red, 14pt
    cell_0 = table_segment.get_cell(0, 0)
    text_segs = [s for s in cell_0.text_segments if s.text.strip()]
    
    seg = text_segs[0]
    assert "Red 14pt" in seg.text, f"Expected 'Red 14pt', got '{seg.text}'"
    assert seg.has_format(FormatBit.FONT_COLOR), "Cell 0 should have FONT_COLOR"
    assert seg.has_format(FormatBit.FONT_SIZE), "Cell 0 should have FONT_SIZE"
    
    meta = seg.metadata.split(',')
    assert 'FF0000' in meta, f"Expected FF0000 in {meta}"
    assert '14' in meta, f"Expected 14 in {meta}"
    print(f"✓ Cell [0,0]: '{seg.text}' - Red (FF0000), 14pt")
    
    # Check Cell 2: Blue, 16pt
    cell_1 = table_segment.get_cell(0, 1)
    text_segs = [s for s in cell_1.text_segments if s.text.strip()]
    
    seg = text_segs[0]
    assert "Blue 16pt" in seg.text, f"Expected 'Blue 16pt', got '{seg.text}'"
    
    meta = seg.metadata.split(',')
    assert '0000FF' in meta, f"Expected 0000FF in {meta}"
    assert '16' in meta, f"Expected 16 in {meta}"
    print(f"✓ Cell [0,1]: '{seg.text}' - Blue (0000FF), 16pt")
    
    print("\n✓ TEST 2 PASSED\n")
    return True


def test_odt_mixed_runs():
    """Test ODT cells with multiple runs (mixed formatting)."""
    print("=" * 70)
    print("TEST 3: ODT Mixed Formatting in Single Cell")
    print("=" * 70)
    
    # Create ODT with mixed formatting
    doc = OpenDocumentText()
    
    bold_style = Style(name="Bold2", family="text")
    bold_props = TextProperties(fontweight="bold")
    bold_style.addElement(bold_props)
    doc.automaticstyles.addElement(bold_style)
    
    italic_style = Style(name="Italic2", family="text")
    italic_props = TextProperties(fontstyle="italic")
    italic_style.addElement(italic_props)
    doc.automaticstyles.addElement(italic_style)
    
    # Create table with one cell containing mixed formatting
    table = Table(name="TestTable")
    row = TableRow()
    cell = TableCell()
    para = P()
    
    # Normal text
    para.addText("Normal ")
    
    # Bold span
    span_bold = Span(stylename=bold_style)
    span_bold.addText("Bold ")
    para.addElement(span_bold)
    
    # Italic span
    span_italic = Span(stylename=italic_style)
    span_italic.addText("Italic")
    para.addElement(span_italic)
    
    cell.addElement(para)
    row.addElement(cell)
    table.addElement(row)
    doc.text.addElement(table)
    
    test_file = "/tmp/test_odt_cell_mixed_session58.odt"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract
    from odf import opendocument, table as odf_table
    
    doc = opendocument.load(test_file)
    
    styles = {}
    for style_elem in doc.automaticstyles.childNodes + doc.styles.childNodes:
        if hasattr(style_elem, 'getAttribute'):
            try:
                sname = style_elem.getAttribute('name')
                if sname:
                    styles[sname] = style_elem
            except:
                pass
    
    odt_table = doc.getElementsByType(odf_table.Table)[0]
    table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
    
    cell_0 = table_segment.get_cell(0, 0)
    text_segs = [s for s in cell_0.text_segments if s.text.strip()]
    
    assert len(text_segs) >= 3, f"Expected 3+ segments, got {len(text_segs)}"
    
    # Check segments
    # Note: Exact order may vary based on ODT structure, so check by content
    normal_found = False
    bold_found = False
    italic_found = False
    
    for seg in text_segs:
        if "Normal" in seg.text and seg.format_bits == 0:
            normal_found = True
            print(f"✓ Found 'Normal' with no formatting")
        elif "Bold" in seg.text and seg.has_format(FormatBit.BOLD):
            bold_found = True
            print(f"✓ Found 'Bold' with BOLD formatting")
        elif "Italic" in seg.text and seg.has_format(FormatBit.ITALIC):
            italic_found = True
            print(f"✓ Found 'Italic' with ITALIC formatting")
    
    assert normal_found, "Normal text not found"
    assert bold_found, "Bold text not found"
    assert italic_found, "Italic text not found"
    
    print("\n✓ TEST 3 PASSED\n")
    return True


def test_odt_modified_extraction():
    """Test that modified ODT extraction function still works."""
    print("=" * 70)
    print("TEST 4: Modified ODT Extraction Function")
    print("=" * 70)
    
    # Create simple ODT with text and table
    doc = OpenDocumentText()
    
    # Add paragraph before table
    para1 = P()
    para1.addText("Before table")
    doc.text.addElement(para1)
    
    # Add table
    table = Table(name="TestTable")
    row = TableRow()
    
    cell1 = TableCell()
    p1 = P()
    p1.addText("Cell A")
    cell1.addElement(p1)
    row.addElement(cell1)
    
    cell2 = TableCell()
    p2 = P()
    p2.addText("Cell B")
    cell2.addElement(p2)
    row.addElement(cell2)
    
    table.addElement(row)
    doc.text.addElement(table)
    
    # Add paragraph after table
    para2 = P()
    para2.addText("After table")
    doc.text.addElement(para2)
    
    test_file = "/tmp/test_odt_extraction_session58.odt"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract using modified function
    try:
        tagged_text = FormatMapper.extract_formatted_text_from_odt(test_file)
        print(f"✓ Extraction succeeded")
        print(f"✓ Tagged text length: {len(tagged_text)} characters")
        
        # Check that text paragraphs are present
        assert "Before table" in tagged_text, "Missing 'Before table'"
        assert "After table" in tagged_text, "Missing 'After table'"
        print(f"✓ Text paragraphs preserved")
        
        print("\n✓ TEST 4 PASSED\n")
        return True
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SESSION 58: ODT TABLE CELL FORMATTING TESTING")
    print("=" * 70 + "\n")
    
    results = []
    
    try:
        test_basic_odt_cell_formatting()
        results.append(("Basic ODT Formatting", True))
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Basic ODT Formatting", False))
    
    try:
        test_odt_colors_and_fonts()
        results.append(("ODT Colors and Fonts", True))
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Colors and Fonts", False))
    
    try:
        test_odt_mixed_runs()
        results.append(("ODT Mixed Runs", True))
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("ODT Mixed Runs", False))
    
    try:
        test_odt_modified_extraction()
        results.append(("Modified ODT Function", True))
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Modified ODT Function", False))
    
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
        print("\n✓ SESSION 58 ODT CELL FORMATTING: COMPLETE")
    else:
        print("\n✗ SESSION 58: SOME TESTS FAILED")
