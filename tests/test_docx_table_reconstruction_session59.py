#!/usr/bin/env python3
"""
Session 59: Test DOCX table reconstruction
Verify that tables can be reconstructed from TableSegment with correct formatting
"""

from src.translation.format_mapper import FormatMapper, TableSegment, CellData, TextSegment, FormatBit
from docx import Document
from docx.shared import RGBColor, Pt

def test_basic_table_reconstruction():
    """Test reconstructing a simple table."""
    print("=" * 70)
    print("TEST 1: Basic Table Reconstruction")
    print("=" * 70)
    
    # Create TableSegment manually
    table = TableSegment(2, 3)
    
    # Cell [0,0]: "Header 1"
    cell_00 = CellData()
    cell_00.text_segments = [TextSegment(text="Header 1")]
    table.set_cell(0, 0, cell_00)
    
    # Cell [0,1]: "Header 2"
    cell_01 = CellData()
    cell_01.text_segments = [TextSegment(text="Header 2")]
    table.set_cell(0, 1, cell_01)
    
    # Cell [0,2]: "Header 3"
    cell_02 = CellData()
    cell_02.text_segments = [TextSegment(text="Header 3")]
    table.set_cell(0, 2, cell_02)
    
    # Cell [1,0]: "Row 1 Col 1"
    cell_10 = CellData()
    cell_10.text_segments = [TextSegment(text="Row 1 Col 1")]
    table.set_cell(1, 0, cell_10)
    
    # Cell [1,1]: "Row 1 Col 2"
    cell_11 = CellData()
    cell_11.text_segments = [TextSegment(text="Row 1 Col 2")]
    table.set_cell(1, 1, cell_11)
    
    # Cell [1,2]: "Row 1 Col 3"
    cell_12 = CellData()
    cell_12.text_segments = [TextSegment(text="Row 1 Col 3")]
    table.set_cell(1, 2, cell_12)
    
    # Reconstruct to DOCX
    doc = Document()
    FormatMapper._reconstruct_table_to_docx(table, doc)
    
    test_file = "/tmp/test_reconstruct_basic_session59.docx"
    doc.save(test_file)
    print(f"✓ Created reconstructed DOCX: {test_file}")
    
    # Reload and verify
    doc = Document(test_file)
    assert len(doc.tables) == 1, f"Expected 1 table, got {len(doc.tables)}"
    
    reloaded_table = doc.tables[0]
    assert len(reloaded_table.rows) == 2, f"Expected 2 rows, got {len(reloaded_table.rows)}"
    assert len(reloaded_table.columns) == 3, f"Expected 3 cols, got {len(reloaded_table.columns)}"
    
    print(f"✓ Table dimensions: 2x3")
    
    # Check cell contents
    assert reloaded_table.rows[0].cells[0].text.strip() == "Header 1"
    assert reloaded_table.rows[0].cells[1].text.strip() == "Header 2"
    assert reloaded_table.rows[0].cells[2].text.strip() == "Header 3"
    assert reloaded_table.rows[1].cells[0].text.strip() == "Row 1 Col 1"
    assert reloaded_table.rows[1].cells[1].text.strip() == "Row 1 Col 2"
    assert reloaded_table.rows[1].cells[2].text.strip() == "Row 1 Col 3"
    
    print(f"✓ All cell contents correct")
    print("\n✓ TEST 1 PASSED\n")
    return True


def test_formatted_cell_reconstruction():
    """Test reconstructing table with formatted cells."""
    print("=" * 70)
    print("TEST 2: Formatted Cell Reconstruction")
    print("=" * 70)
    
    # Create table with formatted cells
    table = TableSegment(1, 3)
    
    # Cell [0,0]: Bold text
    cell_0 = CellData()
    seg_bold = TextSegment(text="Bold Text", format_bits=FormatBit.BOLD)
    cell_0.text_segments = [seg_bold]
    table.set_cell(0, 0, cell_0)
    
    # Cell [0,1]: Italic red text
    cell_1 = CellData()
    seg_italic = TextSegment(
        text="Red Italic",
        format_bits=FormatBit.ITALIC | FormatBit.FONT_COLOR,
        metadata="FF0000"
    )
    cell_1.text_segments = [seg_italic]
    table.set_cell(0, 1, cell_1)
    
    # Cell [0,2]: Blue 16pt text
    cell_2 = CellData()
    seg_blue = TextSegment(
        text="Blue 16pt",
        format_bits=FormatBit.FONT_COLOR | FormatBit.FONT_SIZE,
        metadata="0000FF,16"
    )
    cell_2.text_segments = [seg_blue]
    table.set_cell(0, 2, cell_2)
    
    # Reconstruct
    doc = Document()
    FormatMapper._reconstruct_table_to_docx(table, doc)
    
    test_file = "/tmp/test_reconstruct_formatted_session59.docx"
    doc.save(test_file)
    print(f"✓ Created reconstructed DOCX: {test_file}")
    
    # Reload and verify
    doc = Document(test_file)
    reloaded_table = doc.tables[0]
    
    # Check Cell [0,0]: Bold
    cell = reloaded_table.rows[0].cells[0]
    assert cell.text.strip() == "Bold Text"
    runs = cell.paragraphs[0].runs
    assert len(runs) > 0, "Cell 0 has no runs"
    assert runs[0].bold == True, "Cell 0 should be bold"
    print(f"✓ Cell [0,0]: Bold preserved")
    
    # Check Cell [0,1]: Italic + Red
    cell = reloaded_table.rows[0].cells[1]
    assert cell.text.strip() == "Red Italic"
    runs = cell.paragraphs[0].runs
    assert runs[0].italic == True, "Cell 1 should be italic"
    assert runs[0].font.color.rgb is not None, "Cell 1 should have color"
    rgb = runs[0].font.color.rgb
    assert rgb == RGBColor(255, 0, 0), f"Expected red, got {rgb}"
    print(f"✓ Cell [0,1]: Italic + Red preserved")
    
    # Check Cell [0,2]: Blue + 16pt
    cell = reloaded_table.rows[0].cells[2]
    assert cell.text.strip() == "Blue 16pt"
    runs = cell.paragraphs[0].runs
    rgb = runs[0].font.color.rgb
    assert rgb == RGBColor(0, 0, 255), f"Expected blue, got {rgb}"
    assert runs[0].font.size == Pt(16), f"Expected 16pt, got {runs[0].font.size}"
    print(f"✓ Cell [0,2]: Blue + 16pt preserved")
    
    print("\n✓ TEST 2 PASSED\n")
    return True


def test_mixed_formatting_in_cell():
    """Test reconstructing cell with multiple runs."""
    print("=" * 70)
    print("TEST 3: Mixed Formatting in Single Cell")
    print("=" * 70)
    
    # Create table with mixed formatting in one cell
    table = TableSegment(1, 1)
    
    cell = CellData()
    cell.text_segments = [
        TextSegment(text="Normal "),
        TextSegment(text="Bold ", format_bits=FormatBit.BOLD),
        TextSegment(text="Italic", format_bits=FormatBit.ITALIC)
    ]
    table.set_cell(0, 0, cell)
    
    # Reconstruct
    doc = Document()
    FormatMapper._reconstruct_table_to_docx(table, doc)
    
    test_file = "/tmp/test_reconstruct_mixed_session59.docx"
    doc.save(test_file)
    print(f"✓ Created reconstructed DOCX: {test_file}")
    
    # Reload and verify
    doc = Document(test_file)
    reloaded_table = doc.tables[0]
    cell = reloaded_table.rows[0].cells[0]
    
    # Should have 3 runs
    runs = cell.paragraphs[0].runs
    assert len(runs) >= 3, f"Expected 3+ runs, got {len(runs)}"
    
    # Check each run
    assert "Normal" in runs[0].text
    assert runs[0].bold != True, "Run 0 should not be bold"
    print(f"✓ Run 0: 'Normal' - no formatting")
    
    assert "Bold" in runs[1].text
    assert runs[1].bold == True, "Run 1 should be bold"
    print(f"✓ Run 1: 'Bold' - bold")
    
    assert "Italic" in runs[2].text
    assert runs[2].italic == True, "Run 2 should be italic"
    print(f"✓ Run 2: 'Italic' - italic")
    
    print("\n✓ TEST 3 PASSED\n")
    return True


def test_multi_paragraph_cell():
    """Test reconstructing cell with multiple paragraphs."""
    print("=" * 70)
    print("TEST 4: Multi-paragraph Cell")
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
    doc = Document()
    FormatMapper._reconstruct_table_to_docx(table, doc)
    
    test_file = "/tmp/test_reconstruct_multipara_session59.docx"
    doc.save(test_file)
    print(f"✓ Created reconstructed DOCX: {test_file}")
    
    # Reload and verify
    doc = Document(test_file)
    reloaded_table = doc.tables[0]
    cell = reloaded_table.rows[0].cells[0]
    
    # Should have 2 paragraphs
    paras = cell.paragraphs
    assert len(paras) >= 2, f"Expected 2+ paragraphs, got {len(paras)}"
    
    # Check paragraph 1
    para1_text = paras[0].text.strip()
    assert "First paragraph" in para1_text, f"Expected 'First paragraph', got '{para1_text}'"
    if paras[0].runs:
        assert paras[0].runs[0].bold == True, "Para 1 should be bold"
    print(f"✓ Paragraph 1: Bold")
    
    # Check paragraph 2
    para2_text = paras[1].text.strip()
    assert "Second paragraph" in para2_text, f"Expected 'Second paragraph', got '{para2_text}'"
    if paras[1].runs:
        assert paras[1].runs[0].italic == True, "Para 2 should be italic"
    print(f"✓ Paragraph 2: Italic")
    
    print("\n✓ TEST 4 PASSED\n")
    return True


def test_round_trip():
    """Test extract → reconstruct round-trip."""
    print("=" * 70)
    print("TEST 5: Round-trip (Extract → Reconstruct)")
    print("=" * 70)
    
    # Create original DOCX with formatted table
    doc = Document()
    original_table = doc.add_table(rows=2, cols=2)
    
    # Cell [0,0]: Bold
    cell = original_table.rows[0].cells[0]
    run = cell.paragraphs[0].add_run("Bold")
    run.bold = True
    
    # Cell [0,1]: Red
    cell = original_table.rows[0].cells[1]
    run = cell.paragraphs[0].add_run("Red")
    run.font.color.rgb = RGBColor(255, 0, 0)
    
    # Cell [1,0]: Italic
    cell = original_table.rows[1].cells[0]
    run = cell.paragraphs[0].add_run("Italic")
    run.italic = True
    
    # Cell [1,1]: Blue 14pt
    cell = original_table.rows[1].cells[1]
    run = cell.paragraphs[0].add_run("Blue 14pt")
    run.font.color.rgb = RGBColor(0, 0, 255)
    run.font.size = Pt(14)
    
    original_file = "/tmp/test_roundtrip_original_session59.docx"
    doc.save(original_file)
    print(f"✓ Created original DOCX: {original_file}")
    
    # Extract
    doc = Document(original_file)
    table_segment = FormatMapper._extract_table_from_docx(doc.tables[0])
    print(f"✓ Extracted TableSegment: {table_segment.num_rows}x{table_segment.num_cols}")
    
    # Reconstruct
    doc2 = Document()
    FormatMapper._reconstruct_table_to_docx(table_segment, doc2)
    
    reconstructed_file = "/tmp/test_roundtrip_reconstructed_session59.docx"
    doc2.save(reconstructed_file)
    print(f"✓ Reconstructed DOCX: {reconstructed_file}")
    
    # Verify reconstructed matches original
    doc2 = Document(reconstructed_file)
    recon_table = doc2.tables[0]
    
    # Check dimensions
    assert len(recon_table.rows) == 2
    assert len(recon_table.columns) == 2
    print(f"✓ Dimensions match: 2x2")
    
    # Check Cell [0,0]: Bold
    assert recon_table.rows[0].cells[0].text.strip() == "Bold"
    assert recon_table.rows[0].cells[0].paragraphs[0].runs[0].bold == True
    print(f"✓ Cell [0,0]: Bold preserved")
    
    # Check Cell [0,1]: Red
    assert recon_table.rows[0].cells[1].text.strip() == "Red"
    rgb = recon_table.rows[0].cells[1].paragraphs[0].runs[0].font.color.rgb
    assert rgb == RGBColor(255, 0, 0)
    print(f"✓ Cell [0,1]: Red preserved")
    
    # Check Cell [1,0]: Italic
    assert recon_table.rows[1].cells[0].text.strip() == "Italic"
    assert recon_table.rows[1].cells[0].paragraphs[0].runs[0].italic == True
    print(f"✓ Cell [1,0]: Italic preserved")
    
    # Check Cell [1,1]: Blue 14pt
    assert recon_table.rows[1].cells[1].text.strip() == "Blue 14pt"
    run = recon_table.rows[1].cells[1].paragraphs[0].runs[0]
    assert run.font.color.rgb == RGBColor(0, 0, 255)
    assert run.font.size == Pt(14)
    print(f"✓ Cell [1,1]: Blue 14pt preserved")
    
    print("\n✓ TEST 5 PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SESSION 59: DOCX TABLE RECONSTRUCTION TESTING")
    print("=" * 70 + "\n")
    
    results = []
    
    try:
        test_basic_table_reconstruction()
        results.append(("Basic Reconstruction", True))
    except Exception as e:
        print(f"✗ TEST 1 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Basic Reconstruction", False))
    
    try:
        test_formatted_cell_reconstruction()
        results.append(("Formatted Cells", True))
    except Exception as e:
        print(f"✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Formatted Cells", False))
    
    try:
        test_mixed_formatting_in_cell()
        results.append(("Mixed Formatting", True))
    except Exception as e:
        print(f"✗ TEST 3 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Mixed Formatting", False))
    
    try:
        test_multi_paragraph_cell()
        results.append(("Multi-paragraph", True))
    except Exception as e:
        print(f"✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Multi-paragraph", False))
    
    try:
        test_round_trip()
        results.append(("Round-trip", True))
    except Exception as e:
        print(f"✗ TEST 5 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        results.append(("Round-trip", False))
    
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
        print("\n✓ SESSION 59 DOCX TABLE RECONSTRUCTION: COMPLETE")
    else:
        print("\n✗ SESSION 59: SOME TESTS FAILED")
