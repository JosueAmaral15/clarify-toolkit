#!/usr/bin/env python3
"""
Session 57: Test table cell formatting extraction
Verify that bold, italic, colors, fonts are properly extracted from table cells
"""

from src.translation.format_mapper import FormatMapper, FormatBit
from docx import Document
from docx.shared import RGBColor, Pt

def test_basic_cell_formatting():
    """Test extraction of bold, italic, underline from table cells."""
    print("=" * 70)
    print("TEST 1: Basic Cell Formatting (Bold, Italic, Underline)")
    print("=" * 70)
    
    # Create table with formatted cells
    doc = Document()
    table = doc.add_table(rows=1, cols=3)
    
    # Cell 1: Bold
    cell = table.rows[0].cells[0]
    run = cell.paragraphs[0].add_run("Bold Text")
    run.bold = True
    
    # Cell 2: Italic
    cell = table.rows[0].cells[1]
    run = cell.paragraphs[0].add_run("Italic Text")
    run.italic = True
    
    # Cell 3: Bold + Italic
    cell = table.rows[0].cells[2]
    run = cell.paragraphs[0].add_run("Bold Italic")
    run.bold = True
    run.italic = True
    
    test_file = "/tmp/test_cell_basic_session57.docx"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract table
    doc = Document(test_file)
    table_segment = FormatMapper._extract_table_from_docx(doc.tables[0])
    
    # Check Cell 1: Bold
    cell_0 = table_segment.get_cell(0, 0)
    assert len(cell_0.text_segments) > 0, "Cell 0 has no segments"
    seg = cell_0.text_segments[0]
    assert seg.text == "Bold Text", f"Expected 'Bold Text', got '{seg.text}'"
    assert seg.has_format(FormatBit.BOLD), "Cell 0 should have BOLD"
    assert not seg.has_format(FormatBit.ITALIC), "Cell 0 should not have ITALIC"
    print(f"✓ Cell [0,0]: '{seg.text}' is BOLD")
    
    # Check Cell 2: Italic
    cell_1 = table_segment.get_cell(0, 1)
    seg = cell_1.text_segments[0]
    assert seg.text == "Italic Text", f"Expected 'Italic Text', got '{seg.text}'"
    assert seg.has_format(FormatBit.ITALIC), "Cell 1 should have ITALIC"
    assert not seg.has_format(FormatBit.BOLD), "Cell 1 should not have BOLD"
    print(f"✓ Cell [0,1]: '{seg.text}' is ITALIC")
    
    # Check Cell 3: Bold + Italic
    cell_2 = table_segment.get_cell(0, 2)
    seg = cell_2.text_segments[0]
    assert seg.text == "Bold Italic", f"Expected 'Bold Italic', got '{seg.text}'"
    assert seg.has_format(FormatBit.BOLD), "Cell 2 should have BOLD"
    assert seg.has_format(FormatBit.ITALIC), "Cell 2 should have ITALIC"
    print(f"✓ Cell [0,2]: '{seg.text}' is BOLD + ITALIC")
    
    print("\n✓ TEST 1 PASSED\n")
    return True


def test_color_and_font():
    """Test extraction of colors and fonts from table cells."""
    print("=" * 70)
    print("TEST 2: Colors and Fonts")
    print("=" * 70)
    
    # Create table with colors and fonts
    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    
    # Cell 1: Red text, Arial 14pt
    cell = table.rows[0].cells[0]
    run = cell.paragraphs[0].add_run("Red Arial")
    run.font.color.rgb = RGBColor(255, 0, 0)
    run.font.name = "Arial"
    run.font.size = Pt(14)
    
    # Cell 2: Blue text, Times New Roman 16pt
    cell = table.rows[0].cells[1]
    run = cell.paragraphs[0].add_run("Blue Times")
    run.font.color.rgb = RGBColor(0, 0, 255)
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    
    test_file = "/tmp/test_cell_colors_session57.docx"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract table
    doc = Document(test_file)
    table_segment = FormatMapper._extract_table_from_docx(doc.tables[0])
    
    # Check Cell 1: Red, Arial, 14pt
    cell_0 = table_segment.get_cell(0, 0)
    seg = cell_0.text_segments[0]
    assert seg.text == "Red Arial", f"Expected 'Red Arial', got '{seg.text}'"
    assert seg.has_format(FormatBit.FONT_COLOR), "Cell 0 should have FONT_COLOR"
    assert seg.has_format(FormatBit.FONT_FAMILY), "Cell 0 should have FONT_FAMILY"
    assert seg.has_format(FormatBit.FONT_SIZE), "Cell 0 should have FONT_SIZE"
    
    # Parse metadata
    meta = seg.metadata.split(',')
    assert 'FF0000' in meta, f"Expected red color FF0000 in {meta}"
    assert 'Arial' in meta, f"Expected Arial in {meta}"
    assert '14' in meta, f"Expected size 14 in {meta}"
    print(f"✓ Cell [0,0]: '{seg.text}' - Red (FF0000), Arial, 14pt")
    
    # Check Cell 2: Blue, Times New Roman, 16pt
    cell_1 = table_segment.get_cell(0, 1)
    seg = cell_1.text_segments[0]
    assert seg.text == "Blue Times", f"Expected 'Blue Times', got '{seg.text}'"
    
    meta = seg.metadata.split(',')
    assert '0000FF' in meta, f"Expected blue color 0000FF in {meta}"
    assert 'Times New Roman' in meta, f"Expected Times New Roman in {meta}"
    assert '16' in meta, f"Expected size 16 in {meta}"
    print(f"✓ Cell [0,1]: '{seg.text}' - Blue (0000FF), Times New Roman, 16pt")
    
    print("\n✓ TEST 2 PASSED\n")
    return True


def test_mixed_runs_in_cell():
    """Test cells with multiple runs (mixed formatting)."""
    print("=" * 70)
    print("TEST 3: Mixed Formatting in Single Cell")
    print("=" * 70)
    
    # Create table with mixed formatting in one cell
    doc = Document()
    table = doc.add_table(rows=1, cols=1)
    
    cell = table.rows[0].cells[0]
    para = cell.paragraphs[0]
    
    # Run 1: Normal
    run1 = para.add_run("Normal ")
    
    # Run 2: Bold
    run2 = para.add_run("Bold ")
    run2.bold = True
    
    # Run 3: Italic
    run3 = para.add_run("Italic")
    run3.italic = True
    
    test_file = "/tmp/test_cell_mixed_session57.docx"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract table
    doc = Document(test_file)
    table_segment = FormatMapper._extract_table_from_docx(doc.tables[0])
    
    cell_0 = table_segment.get_cell(0, 0)
    
    # Should have 4 segments: "Normal ", "Bold ", "Italic", "\n"
    # Filter out newline segments
    text_segs = [s for s in cell_0.text_segments if s.text.strip()]
    
    assert len(text_segs) >= 3, f"Expected 3+ text segments, got {len(text_segs)}"
    
    # Check Run 1: Normal (no formatting)
    seg1 = text_segs[0]
    assert seg1.text == "Normal ", f"Expected 'Normal ', got '{seg1.text}'"
    assert seg1.format_bits == 0, "Run 1 should have no formatting"
    print(f"✓ Run 1: '{seg1.text}' - No formatting")
    
    # Check Run 2: Bold
    seg2 = text_segs[1]
    assert seg2.text == "Bold ", f"Expected 'Bold ', got '{seg2.text}'"
    assert seg2.has_format(FormatBit.BOLD), "Run 2 should be BOLD"
    print(f"✓ Run 2: '{seg2.text}' - BOLD")
    
    # Check Run 3: Italic
    seg3 = text_segs[2]
    assert seg3.text == "Italic", f"Expected 'Italic', got '{seg3.text}'"
    assert seg3.has_format(FormatBit.ITALIC), "Run 3 should be ITALIC"
    print(f"✓ Run 3: '{seg3.text}' - ITALIC")
    
    print("\n✓ TEST 3 PASSED\n")
    return True


def test_multi_paragraph_cell():
    """Test cells with multiple paragraphs."""
    print("=" * 70)
    print("TEST 4: Multiple Paragraphs in Cell")
    print("=" * 70)
    
    # Create table with multi-paragraph cell
    doc = Document()
    table = doc.add_table(rows=1, cols=1)
    
    cell = table.rows[0].cells[0]
    
    # First paragraph
    para1 = cell.paragraphs[0]
    run1 = para1.add_run("First paragraph")
    run1.bold = True
    
    # Add second paragraph
    para2 = cell.add_paragraph()
    run2 = para2.add_run("Second paragraph")
    run2.italic = True
    
    test_file = "/tmp/test_cell_multipara_session57.docx"
    doc.save(test_file)
    print(f"✓ Created test file: {test_file}")
    
    # Extract table
    doc = Document(test_file)
    table_segment = FormatMapper._extract_table_from_docx(doc.tables[0])
    
    cell_0 = table_segment.get_cell(0, 0)
    
    # Should have segments from both paragraphs
    text_segs = [s for s in cell_0.text_segments if s.text.strip()]
    
    assert len(text_segs) >= 2, f"Expected 2+ text segments, got {len(text_segs)}"
    
    # Check first paragraph
    seg1 = text_segs[0]
    assert "First paragraph" in seg1.text, f"Expected 'First paragraph' in '{seg1.text}'"
    assert seg1.has_format(FormatBit.BOLD), "First paragraph should be BOLD"
    print(f"✓ Paragraph 1: '{seg1.text}' - BOLD")
    
    # Check second paragraph
    seg2 = text_segs[1]
    assert "Second paragraph" in seg2.text, f"Expected 'Second paragraph' in '{seg2.text}'"
    assert seg2.has_format(FormatBit.ITALIC), "Second paragraph should be ITALIC"
    print(f"✓ Paragraph 2: '{seg2.text}' - ITALIC")
    
    print("\n✓ TEST 4 PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SESSION 57: TABLE CELL FORMATTING TESTING")
    print("=" * 70 + "\n")
    
    results = []
    
    try:
        test_basic_cell_formatting()
        results.append(("Basic Formatting", True))
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Basic Formatting", False))
    
    try:
        test_color_and_font()
        results.append(("Colors and Fonts", True))
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Colors and Fonts", False))
    
    try:
        test_mixed_runs_in_cell()
        results.append(("Mixed Runs", True))
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Mixed Runs", False))
    
    try:
        test_multi_paragraph_cell()
        results.append(("Multi-paragraph", True))
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Multi-paragraph", False))
    
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
        print("\n✓ SESSION 57 CELL FORMATTING: COMPLETE")
    else:
        print("\n✗ SESSION 57: SOME TESTS FAILED")
