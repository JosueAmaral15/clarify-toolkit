# Action Plan: Add ODT Export with Formatting

**Programmer:** COM8  
**Date:** January 30, 2026  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3 (one feature per session)

---

## Objective

Add ability to save translation results as ODT format with formatting preserved (same as DOCX).

---

## Current State

**What works:**
- ✅ Load DOCX with formatting
- ✅ Load ODT as plain text (no formatting)
- ✅ Save as DOCX with formatting
- ✅ Save as TXT (plain text)

**What's needed:**
- ❌ Save as ODT with formatting

---

## Implementation Plan

### Session 10: Add ODT Export Functionality

**Objective:** Create `create_odt_from_segments()` method and integrate into save workflow

**Steps:**

1. **Research odfpy API** (5 min)
   - Check how to create ODT documents
   - Verify text formatting methods
   - Document API differences from python-docx

2. **Create `create_odt_from_segments()` method** (20 min)
   - Location: `src/translation/format_mapper.py`
   - Similar to `create_docx_from_segments()`
   - Apply formatting: bold, italic, underline, colors, sizes, fonts
   - Handle paragraph breaks

3. **Update `_save_as()` method** (10 min)
   - Location: `src/gui/google_translate_dock.py`
   - Detect `.odt` extension
   - Route to new ODT creation method
   - Update file dialog filters

4. **Test ODT export** (10 min)
   - Create ODT with formatting
   - Open in LibreOffice
   - Verify formatting preserved
   - Verify no tags visible

5. **Commit** (5 min)

**Total time:** ~50 minutes

---

## Technical Details

### odfpy API Research

**Key modules:**
```python
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import P, Span
```

**Basic structure:**
```python
doc = OpenDocumentText()

# Create styles
bold_style = Style(name="Bold", family="text")
bold_style.addElement(TextProperties(fontweight="bold"))
doc.styles.addElement(bold_style)

# Add text
paragraph = P()
span = Span(stylename=bold_style, text="Bold text")
paragraph.addElement(span)
doc.text.addElement(paragraph)

doc.save(output_path)
```

### Formatting Mapping

| Format | DOCX | ODT |
|--------|------|-----|
| Bold | `run.bold = True` | `fontweight="bold"` |
| Italic | `run.italic = True` | `fontstyle="italic"` |
| Underline | `run.underline = True` | `textunderlinestyle="solid"` |
| Color | `run.font.color.rgb = RGBColor(r,g,b)` | `color="#RRGGBB"` |
| Size | `run.font.size = Pt(12)` | `fontsize="12pt"` |
| Font | `run.font.name = "Arial"` | `fontfamily="Arial"` |

---

## Implementation

### Method Signature

```python
@staticmethod
def create_odt_from_segments(segments: List[TextSegment], output_path: str) -> None:
    """
    Create an ODT file from text segments with formatting.
    
    Args:
        segments: List of TextSegment objects with formatting info
        output_path: Path to save the output ODT file
    """
```

### Key Differences from DOCX

1. **Styles must be predefined** - Can't apply formatting directly to text
2. **Need to create style objects** - One for each unique format combination
3. **Use Span elements** - For formatted text within paragraphs
4. **Different API** - odfpy vs python-docx syntax

### Strategy

**Option A: Dynamic styles** (recommended)
- Create style for each unique format_bits + metadata combination
- Name styles: "format_1", "format_2_italic", "format_17_bold_red"
- Cache styles to avoid duplicates

**Option B: Predefined styles**
- Create all possible styles upfront (complex)
- 2^12 = 4096 possible combinations (too many)

**Recommended: Option A**

---

## Testing Plan

1. **Simple formatting:**
   - "Hello <1>world</1>!" → ODT with bold
   - Verify in LibreOffice

2. **Complex formatting:**
   - "<1>Bold</1> <2>italic</2> <17:FF0000>red bold</17>"
   - Verify all formats applied

3. **Multiline text:**
   - Text with paragraph breaks
   - Verify structure preserved

4. **User tags:**
   - "Use <div> tag" → "<div>" visible in ODT
   - Verify user tags NOT removed

5. **Complete workflow:**
   - Load DOCX → translate → save ODT
   - Verify formatting preserved

---

## Success Criteria

- ✅ ODT files created successfully
- ✅ Formatting applied correctly (bold, italic, underline, colors, sizes, fonts)
- ✅ No numeric tags visible in ODT
- ✅ User tags preserved
- ✅ Opens correctly in LibreOffice
- ✅ File dialog shows ODT option
- ✅ Same features as DOCX export

---

## File Dialog Update

**Current:**
```python
"Word Documents (*.docx);;Text Files (*.txt);;All Files (*)"
```

**Updated:**
```python
"Word Documents (*.docx);;OpenDocument (*.odt);;Text Files (*.txt);;All Files (*)"
```

---

## Commit Message Template

```
Session 10: Add ODT export with formatting

FEATURE: Save translation results as ODT format

IMPLEMENTATION:
✓ Created create_odt_from_segments() in format_mapper.py
  - Uses odfpy library
  - Dynamic style creation for each format combination
  - Supports bold, italic, underline, colors, sizes, fonts
  - Handles paragraph breaks

✓ Updated _save_as() in google_translate_dock.py
  - Detects .odt extension
  - Routes to ODT creation method

✓ Updated file dialog filters
  - Added "OpenDocument (*.odt)" option

TESTING:
✓ Simple formatting (bold, italic)
✓ Complex formatting (colors, fonts, sizes)
✓ Multiline text with paragraph breaks
✓ User tags preserved
✓ Opens correctly in LibreOffice

RESULT:
Users can now save translations as:
- DOCX (with formatting)
- ODT (with formatting) ← NEW
- TXT (plain text)

Protocol: SIMPLICITY_PROTOCOL_3 - one feature per session
```

---

## Questions Before Starting

1. **Should ODT support same formats as DOCX?**
   - Bold, italic, underline, colors, sizes, fonts? → YES or NO?

2. **Default format when no extension specified?**
   - Current: DOCX if has formatting, TXT otherwise
   - Keep same? → YES or NO?

3. **Handle ODT-specific features later?**
   - Tables, images, headers/footers in future phase? → YES or NO?

---

**Ready to proceed with Session 10?**
