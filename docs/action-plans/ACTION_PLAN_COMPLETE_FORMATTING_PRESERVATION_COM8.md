# Action Plan: Implement ALL DOCX/ODT Formatting Preservation (COM8)

**Date:** February 1, 2026  
**Programmer:** COM8 (Programmer #8)  
**Goal:** Preserve ALL known formatting and styles in DOCX/ODT translation workflow

---

## Current Status (Session 16 Complete)

### ✅ Already Working (8 formats)
1. **Bold** - Text weight (font-weight: bold)
2. **Italic** - Text style (font-style: italic)
3. **Underline** - Text decoration (text-underline-style: solid)
4. **Font Color** - Text color with hex RGB (#FF0000)
5. **Font Size** - Text size in points (12pt, 14pt, etc.)
6. **Font Family** - Font name (Arial, Times New Roman, etc.)
7. **Blank Lines** - Paragraph spacing (\\n\\n)
8. **Plain Text** - Normal unformatted text

### ❌ Missing Formats (54+ formats to implement)

---

## Complete Format Inventory

### **CATEGORY 1: Character Formatting (12 formats)**

#### Already Done ✅
1. Bold
2. Italic
3. Underline
4. Font Color
5. Font Size
6. Font Family

#### To Implement (6 formats)
7. **Strikethrough** - Text with line through it
8. **Double Underline** - Text with double underline
9. **Highlight/Background Color** - Text background color
10. **Superscript** - Text raised above baseline (x²)
11. **Subscript** - Text lowered below baseline (H₂O)
12. **Small Caps** - Text in small capital letters

---

### **CATEGORY 2: Paragraph Formatting (10 formats)**

13. **Alignment** - Left, Center, Right, Justify
14. **Line Spacing** - Single, 1.5, Double, Exact (150%)
15. **Indentation** - First line, Left, Right indent (in cm/pt)
16. **Space Before** - Space before paragraph (in cm/pt)
17. **Space After** - Space after paragraph (in cm/pt)
18. **Keep Lines Together** - Prevent paragraph split across pages
19. **Keep With Next** - Keep paragraph with next paragraph
20. **Page Break Before** - Start paragraph on new page
21. **Widow/Orphan Control** - Prevent single lines at page breaks
22. **Bidirectional Text** - RTL/LTR text direction

---

### **CATEGORY 3: Heading & Styles (6 formats)**

23. **Heading 1** - Top-level heading (H1)
24. **Heading 2** - Second-level heading (H2)
25. **Heading 3** - Third-level heading (H3)
26. **Heading 4-6** - Lower-level headings (H4, H5, H6)
27. **Paragraph Style** - Named style (Normal, Body Text, etc.)
28. **Character Style** - Named character formatting

---

### **CATEGORY 4: Lists (6 formats)**

29. **Bulleted List** - Unordered list with bullets (•, ○, ■)
30. **Numbered List** - Ordered list (1, 2, 3 or i, ii, iii)
31. **Multi-level List** - Nested lists with indentation
32. **Custom Bullets** - User-defined bullet characters
33. **List Start Number** - Start numbering from specific value
34. **List Indentation** - Custom indent for list items

---

### **CATEGORY 5: Tables (8 formats)**

35. **Table Structure** - Rows and columns
36. **Cell Borders** - Border style, width, color
37. **Cell Shading** - Cell background color
38. **Cell Alignment** - Text alignment within cell (top, middle, bottom)
39. **Cell Merging** - Merged cells (colspan, rowspan)
40. **Table Width** - Fixed or percentage width
41. **Column Widths** - Individual column sizes
42. **Table Header Rows** - Repeat header on each page

---

### **CATEGORY 6: Images & Objects (5 formats)**

43. **Inline Images** - Images within text flow
44. **Image Size** - Width and height
45. **Image Position** - Alignment (left, center, right)
46. **Image Captions** - Text below/above image
47. **Text Wrapping** - How text flows around image (square, tight, etc.)

---

### **CATEGORY 7: Advanced Text (7 formats)**

48. **Hyperlinks** - Clickable links to URLs
49. **Bookmarks** - Internal document anchors
50. **Cross-references** - Links to other parts of document
51. **Footnotes** - Notes at bottom of page
52. **Endnotes** - Notes at end of document
53. **Comments** - Annotations/notes (may not translate)
54. **Track Changes** - Revision marks (may not translate)

---

### **CATEGORY 8: Page Layout (4 formats)**

55. **Page Breaks** - Explicit page separations
56. **Section Breaks** - Different formatting sections
57. **Columns** - Multi-column text layout
58. **Page Numbers** - Auto-generated page numbers (may not translate)

---

### **CATEGORY 9: Special Characters (4 formats)**

59. **Non-breaking Space** - Space that prevents line break
60. **Non-breaking Hyphen** - Hyphen that prevents line break
61. **Soft Hyphen** - Optional hyphen for word break
62. **Tab Characters** - Tab stops and alignment

---

## Implementation Strategy

### **Phase 1: Character Formatting (Sessions 17-22) - 6 formats**
**Goal:** Complete all character-level formatting  
**Estimated time:** 6 sessions × 30-45 min = 3-4.5 hours

- Session 17: Strikethrough
- Session 18: Highlight/Background color
- Session 19: Superscript
- Session 20: Subscript
- Session 21: Double underline
- Session 22: Small caps

---

### **Phase 2: Paragraph Formatting (Sessions 23-32) - 10 formats**
**Goal:** Complete all paragraph-level formatting  
**Estimated time:** 10 sessions × 30-45 min = 5-7.5 hours

- Session 23: Alignment (left, center, right, justify)
- Session 24: Line spacing (single, 1.5, double, exact)
- Session 25: Indentation (first line, left, right)
- Session 26: Space before/after paragraphs
- Session 27: Keep lines together
- Session 28: Keep with next
- Session 29: Page break before
- Session 30: Widow/orphan control
- Session 31: Bidirectional text (RTL/LTR)
- Session 32: Testing & validation (all paragraph formats)

---

### **Phase 3: Headings & Styles (Sessions 33-38) - 6 formats**
**Goal:** Preserve document structure and styles  
**Estimated time:** 6 sessions × 30-45 min = 3-4.5 hours

- Session 33: Heading 1-3
- Session 34: Heading 4-6
- Session 35: Paragraph styles
- Session 36: Character styles
- Session 37: Style mapping (source→target language)
- Session 38: Testing & validation (all styles)

---

### **Phase 4: Lists (Sessions 39-44) - 6 formats**
**Goal:** Preserve list structure and numbering  
**Estimated time:** 6 sessions × 45-60 min = 4.5-6 hours

- Session 39: Bulleted lists (basic)
- Session 40: Numbered lists (basic)
- Session 41: Multi-level lists (nested)
- Session 42: Custom bullets
- Session 43: List start number & indentation
- Session 44: Testing & validation (all lists)

**Challenge:** Lists require structural changes - segments must track list level

---

### **Phase 5: Tables (Sessions 45-52) - 8 formats**
**Goal:** Preserve table structure and formatting  
**Estimated time:** 8 sessions × 60-90 min = 8-12 hours

- Session 45: Basic table structure (rows/columns)
- Session 46: Cell borders (style, width, color)
- Session 47: Cell shading (background colors)
- Session 48: Cell alignment (top, middle, bottom)
- Session 49: Cell merging (colspan, rowspan)
- Session 50: Table & column widths
- Session 51: Table header rows (repeat)
- Session 52: Testing & validation (all tables)

**Challenge:** Major architectural change - need TableSegment data structure

---

### **Phase 6: Images & Objects (Sessions 53-57) - 5 formats**
**Goal:** Preserve images and positioning  
**Estimated time:** 5 sessions × 45-60 min = 3.75-5 hours

- Session 53: Extract images to temp files
- Session 54: Inline images with size preservation
- Session 55: Image position & alignment
- Session 56: Image captions
- Session 57: Text wrapping around images

**Challenge:** Binary data handling, image formats (PNG, JPG, etc.)

---

### **Phase 7: Advanced Text (Sessions 58-64) - 7 formats**
**Goal:** Preserve hyperlinks, footnotes, bookmarks  
**Estimated time:** 7 sessions × 45-60 min = 5.25-7 hours

- Session 58: Hyperlinks (URLs)
- Session 59: Bookmarks
- Session 60: Cross-references
- Session 61: Footnotes
- Session 62: Endnotes
- Session 63: Comments (preserve but don't translate)
- Session 64: Track changes (preserve but don't translate)

**Note:** Comments and track changes may be excluded (not translatable)

---

### **Phase 8: Page Layout (Sessions 65-68) - 4 formats**
**Goal:** Preserve page structure  
**Estimated time:** 4 sessions × 30-45 min = 2-3 hours

- Session 65: Page breaks
- Session 66: Section breaks
- Session 67: Multi-column layout
- Session 68: Testing & validation (page layout)

**Challenge:** Page-level features may not translate well

---

### **Phase 9: Special Characters (Sessions 69-72) - 4 formats**
**Goal:** Preserve special spacing and characters  
**Estimated time:** 4 sessions × 20-30 min = 1.33-2 hours

- Session 69: Non-breaking spaces
- Session 70: Non-breaking hyphens
- Session 71: Soft hyphens
- Session 72: Tab characters & stops

---

### **Phase 10: Final Testing & Documentation (Sessions 73-80)**
**Goal:** Comprehensive testing and user documentation  
**Estimated time:** 8 sessions × 45-60 min = 6-8 hours

- Session 73: Test all character formats (12 formats)
- Session 74: Test all paragraph formats (10 formats)
- Session 75: Test headings & styles (6 formats)
- Session 76: Test lists (6 formats)
- Session 77: Test tables (8 formats)
- Session 78: Test images & objects (5 formats)
- Session 79: Test advanced text (7 formats)
- Session 80: Test page layout & special chars (8 formats)

---

## Total Project Estimate

### By Phase
- **Phase 1 (Character):** 6 sessions = 3-4.5 hours
- **Phase 2 (Paragraph):** 10 sessions = 5-7.5 hours
- **Phase 3 (Headings/Styles):** 6 sessions = 3-4.5 hours
- **Phase 4 (Lists):** 6 sessions = 4.5-6 hours
- **Phase 5 (Tables):** 8 sessions = 8-12 hours
- **Phase 6 (Images):** 5 sessions = 3.75-5 hours
- **Phase 7 (Advanced):** 7 sessions = 5.25-7 hours
- **Phase 8 (Page Layout):** 4 sessions = 2-3 hours
- **Phase 9 (Special Chars):** 4 sessions = 1.33-2 hours
- **Phase 10 (Testing):** 8 sessions = 6-8 hours

### **TOTAL: 64 sessions (implementation) + 8 sessions (testing) = 72 sessions**
### **TOTAL TIME: 43-59 hours of development work**

---

## Technical Architecture Changes Needed

### **Current Architecture (Works for character formatting):**
```python
TextSegment:
  - text: str
  - format_bits: int (bold, italic, color, size, font)
  - metadata: str (color, size, font values)
  - paragraph_format: int (alignment, spacing)
  - paragraph_metadata: str
```

### **New Architecture (Needed for advanced features):**

```python
# Base segment
class TextSegment:
    text: str
    format_bits: int
    metadata: dict  # Changed from str to dict for complex data
    
# New segment types
class ParagraphSegment(TextSegment):
    alignment: str  # 'left', 'center', 'right', 'justify'
    line_spacing: float
    indent_first: float
    indent_left: float
    indent_right: float
    space_before: float
    space_after: float
    keep_together: bool
    keep_with_next: bool
    page_break_before: bool
    style_name: str
    
class ListItemSegment(ParagraphSegment):
    list_type: str  # 'bullet', 'number'
    list_level: int  # 0-9 for nesting
    list_number: int  # for numbered lists
    bullet_char: str  # for custom bullets
    
class TableCellSegment(TextSegment):
    row: int
    col: int
    colspan: int
    rowspan: int
    borders: dict  # top, bottom, left, right
    shading: str  # background color
    valign: str  # 'top', 'middle', 'bottom'
    
class ImageSegment:
    image_data: bytes
    image_format: str  # 'png', 'jpg', etc.
    width: float
    height: float
    position: str  # 'inline', 'left', 'center', 'right'
    caption: str
    wrap_style: str  # 'square', 'tight', etc.
    
class HyperlinkSegment(TextSegment):
    url: str
    tooltip: str
    
class FootnoteSegment(TextSegment):
    footnote_id: int
    footnote_text: str
```

### **Major Refactoring Needed:**
1. Change metadata from `str` to `dict` for complex data
2. Create segment type hierarchy
3. Update extraction to create appropriate segment types
4. Update parsing to reconstruct segment types from tags
5. Update DOCX/ODT output to handle all segment types
6. Tag system may need expansion beyond 12 bits

---

## Tag System Expansion

### **Current Tag System (12 bits):**
```
Bit 0-7: Character formatting (8 bits)
Bit 8-11: Paragraph formatting (4 bits)
Total: 4096 possible combinations
```

### **Extended Tag System (24 bits proposed):**
```
Bits 0-7: Character formatting (8 bits)
  0: Bold
  1: Italic
  2: Underline
  3: Strikethrough
  4: Font Color
  5: Font Size
  6: Font Family
  7: Highlight

Bits 8-15: Extended character formatting (8 bits)
  8: Superscript
  9: Subscript
  10: Double Underline
  11: Small Caps
  12: Hyperlink
  13: Footnote
  14: Reserved
  15: Reserved

Bits 16-23: Paragraph & structural (8 bits)
  16: Alignment
  17: Line Spacing
  18: Indentation
  19: Heading (H1-H6)
  20: List Item
  21: Table Cell
  22: Image
  23: Reserved
```

### **Tag Format Evolution:**
```
Current: <format_bits:metadata>text</format_bits>
Example: <113:FF0000,12,Arial>red bold Arial</113>

Extended: <format_bits:type:metadata>text</format_bits:type>
Example: <113:char:FF0000,12,Arial>text</113:char>
         <1048576:list:bullet,1>List item</1048576:list>
         <2097152:table:2,3,1,1>Cell text</2097152:table>
```

---

## Implementation Protocol

### **Per Session:**
1. Identify ONE format to implement
2. Research DOCX/ODT API for that format
3. Update extraction code (format_mapper.py)
4. Update output code (create_docx/odt_from_segments)
5. Test with sample file
6. Commit with descriptive message
7. Document in session report

### **Testing Requirements:**
- Test file with ONLY that format
- Test file with combined formats
- Visual verification in LibreOffice/Word
- Automated test in test suite

### **Documentation:**
- Update format support matrix
- Add examples to user guide
- Document limitations (if any)

---

## Priority Levels

### **HIGH PRIORITY (User expects these):**
- Alignment (Session 23)
- Line spacing (Session 24)
- Lists - bullets & numbers (Sessions 39-40)
- Tables - basic structure (Session 45)
- Hyperlinks (Session 58)

### **MEDIUM PRIORITY (Nice to have):**
- Strikethrough (Session 17)
- Highlight (Session 18)
- Headings (Session 33)
- Images (Sessions 53-57)
- Indentation (Session 25)

### **LOW PRIORITY (Rare use cases):**
- Small caps (Session 22)
- Keep with next (Session 28)
- Bidirectional text (Session 31)
- Comments (Session 63)
- Track changes (Session 64)

---

## Risk Assessment

### **HIGH RISK (Complex, may have issues):**
- **Tables:** Major architectural change, cell-by-cell translation complexity
- **Images:** Binary data handling, format conversion, Google Translate may strip them
- **Lists:** Nested structures, numbering continuity
- **Multi-column layout:** May not translate well

### **MEDIUM RISK (Moderate complexity):**
- **Hyperlinks:** URL translation may break links
- **Footnotes/Endnotes:** Position and numbering
- **Styles:** Style name translation, mapping issues

### **LOW RISK (Straightforward):**
- **Character formatting:** Similar to existing code
- **Paragraph formatting:** Metadata extension
- **Special characters:** Unicode handling

---

## Success Criteria

### **Phase Completion:**
- [ ] All formats in phase implemented
- [ ] All formats tested individually
- [ ] Combined format testing passed
- [ ] No regressions in existing formats
- [ ] Documentation updated
- [ ] User confirms: "it works!"

### **Project Completion:**
- [ ] All 62 formats implemented
- [ ] Comprehensive test suite (100+ tests)
- [ ] User guide updated
- [ ] Performance acceptable (<10s for typical document)
- [ ] Memory usage reasonable (<500MB for typical document)
- [ ] No crashes or errors
- [ ] User confirms: "All formatting preserved!"

---

## Exclusions (Will NOT implement)

### **Features that won't work in translation workflow:**
1. **Macros/VBA** - Security risk, language-dependent
2. **Form fields** - Interactive elements don't translate
3. **Embedded objects** (Excel, etc.) - Too complex
4. **Audio/Video** - Not text content
5. **SmartArt** - Complex graphics
6. **Charts** - Data visualization doesn't translate
7. **Equations** - Math notation preservation only
8. **Drawing shapes** - Not text content

---

## Questions for User

Before starting Phase 1, please answer:

1. **Should I implement ALL 62 formats?** YES or prioritize HIGH PRIORITY first?

2. **Timeline acceptable?** 43-59 hours = approximately 5-7 full working days

3. **Architecture change approved?** TextSegment → multiple segment types (major refactor)

4. **Testing frequency?** After every session or after each phase?

5. **Which format to start with?** Strikethrough (Session 17) or Alignment (higher priority)?

6. **Break points?** Should we pause after each phase for user testing?

---

## Next Steps

**If approved:**
1. Start with **Session 17: Strikethrough** (easiest character format)
2. Then **Session 18: Highlight/Background color**
3. Continue through Phase 1 (character formatting)
4. Re-evaluate after Phase 1 (6 sessions, 3-4.5 hours)

**If prioritization needed:**
1. Implement HIGH PRIORITY formats first (11 formats, ~16-24 hours)
2. Then MEDIUM PRIORITY (18 formats, ~27-36 hours)
3. Skip LOW PRIORITY (may never implement)

---

**Status:** Plan created, awaiting user approval  
**Current session:** Session 16 complete  
**Next session:** Session 17 (Strikethrough) or user-chosen priority

**READY TO PROCEED?**
