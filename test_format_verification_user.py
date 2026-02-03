#!/usr/bin/env python3
"""
USER VERIFICATION TEST - Session 64
Create a test DOCX that you can open and visually inspect
"""
import sys
sys.path.insert(0, 'src')

from translation.format_mapper import FormatMapper, TextSegment, FormatBit

print("="*70)
print("CREATING TEST DOCUMENT FOR USER VERIFICATION")
print("="*70)

# Create comprehensive test with all formats
segments = [
    # Title
    TextSegment("FORMAT VERIFICATION TEST", FormatBit.BOLD | FormatBit.FONT_SIZE, "16", 
                FormatBit.ALIGNMENT, "C"),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Character formats
    TextSegment("CHARACTER FORMATS:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This is bold", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This is italic", FormatBit.ITALIC, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This is underlined", FormatBit.UNDERLINE, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This is red text", FormatBit.FONT_COLOR, "FF0000", 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This is large text", FormatBit.FONT_SIZE, "18", 0, None),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Alignment tests
    TextSegment("ALIGNMENT TESTS:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Left aligned (default)", 0, None, FormatBit.ALIGNMENT, "L"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Center aligned text", 0, None, FormatBit.ALIGNMENT, "C"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Right aligned text", 0, None, FormatBit.ALIGNMENT, "R"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Justified text with more words to see the justification effect properly", 
                0, None, FormatBit.ALIGNMENT, "J"),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Heading tests
    TextSegment("HEADING TESTS:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Heading 1", 0, None, FormatBit.HEADING, "H1"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Heading 2", 0, None, FormatBit.HEADING, "H2"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Heading 3", 0, None, FormatBit.HEADING, "H3"),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Indentation test
    TextSegment("INDENTATION TEST:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This paragraph should be indented from the left margin by 72pt and have first line indent of 36pt. " +
                "The second line should show the left indent clearly.",
                0, None, FormatBit.INDENTATION, "36,72,0"),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Line spacing test
    TextSegment("LINE SPACING TEST:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Single spacing (line 1)", 0, None, FormatBit.LINE_SPACING, "1.0"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Single spacing (line 2)", 0, None, FormatBit.LINE_SPACING, "1.0"),
    TextSegment("\n\n", 0, None, 0, None),
    TextSegment("Double spacing (line 1)", 0, None, FormatBit.LINE_SPACING, "2.0"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Double spacing (line 2)", 0, None, FormatBit.LINE_SPACING, "2.0"),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Space before/after test
    TextSegment("SPACE BEFORE/AFTER TEST:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Paragraph with 24pt spacing before and after. Should have visible gaps.",
                0, None, FormatBit.SPACE_BEFORE_AFTER, "24,24"),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Normal paragraph for comparison - no extra spacing.", 0, None, 0, None),
    TextSegment("\n\n", 0, None, 0, None),
    
    # Page break test
    TextSegment("PAGE BREAK TEST:", FormatBit.BOLD, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("Text before page break", 0, None, 0, None),
    TextSegment("\n", 0, None, 0, None),
    TextSegment("This should start on a new page", 0, None, FormatBit.PAGE_BREAK_BEFORE, None),
    TextSegment("\n\n", 0, None, 0, None),
    
    # End
    TextSegment("END OF TEST", FormatBit.BOLD, None, FormatBit.ALIGNMENT, "C"),
]

output_path = "/tmp/FORMAT_VERIFICATION_TEST.docx"
print(f"\n📝 Creating test DOCX: {output_path}")

try:
    FormatMapper.create_docx_from_segments(segments, output_path)
    print(f"✅ SUCCESS! File created: {output_path}")
    print("\n" + "="*70)
    print("PLEASE OPEN THIS FILE IN MICROSOFT WORD OR LIBREOFFICE")
    print("="*70)
    print("\nCheck the following:")
    print("  1. Title is centered and bold")
    print("  2. Character formats (bold, italic, underline, red, large)")
    print("  3. Alignment (left, center, right, justified)")
    print("  4. Headings appear in proper heading styles")
    print("  5. Indented paragraph has left margin and first-line indent")
    print("  6. Line spacing differences are visible")
    print("  7. Space before/after paragraph has gaps")
    print("  8. Page break creates a new page")
    print("\n" + "="*70)
    print(f"\nCommand to open:")
    print(f"  libreoffice {output_path}")
    print(f"  # or")
    print(f"  xdg-open {output_path}")
    print("="*70)
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

