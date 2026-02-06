# Action Plan: Fix ODT Formatting Preservation (COM8)

**Date:** January 30, 2026  
**Programmer:** COM8 (Programmer #8)  
**Issue:** ODT files not preserving all formatting after translation

---

## Current Status

### What Works ✅
- ODT files load without errors
- Text content is extracted and translated
- Basic structure preserved (paragraphs)

### What's Broken ❌
1. **Font family not saved** - All text appears in default font
2. **Font size not saved** - All text appears in default size
3. **Other formatting missing** - Colors, bold, italic, underline not preserved
4. **Blank lines disappearing** - Paragraph spacing lost

---

## Root Cause Analysis

### Session 11 Implementation
- ✅ Added `extract_formatted_text_from_odt()` - extracts formatting FROM ODT
- ✅ Tags are generated correctly (verified by backend)
- ❌ `create_odt_from_segments()` exists BUT may have bugs
- ❌ Style application in ODT output not verified

### Hypothesis
The problem is likely in `create_odt_from_segments()` (Session 10):
- Style creation may be incomplete
- Attribute names might be wrong (ODT uses different names than DOCX)
- Blank lines not being written as empty paragraphs

---

## Investigation Plan

### Phase 1: Verify Tag Extraction (Session 12)
**Goal:** Confirm ODT extraction creates correct tags

**Tasks:**
1. Add debug logging to `extract_formatted_text_from_odt()`
2. Load test ODT file with:
   - Bold text
   - Italic text
   - Red colored text (RGB #FF0000)
   - Arial font (12pt)
   - Multiple blank lines
3. Print tagged text to console
4. Verify tags match expected format:
   - `<1>bold</1>` for bold
   - `<2>italic</2>` for italic
   - `<113:FF0000,12,Arial>colored bold text</113>` for combined

**Expected Output:**
```
Tagged text: "Hello <1>bold</1> normal\n\n<2>italic</2>\n\n<113:FF0000,12,Arial>red bold Arial</113>"
```

**Success Criteria:**
- Tags present in extracted text ✓
- Metadata (color, size, font) in correct format ✓
- Blank lines represented as `\n\n` ✓

---

### Phase 2: Verify Tag Parsing (Session 12)
**Goal:** Confirm tags are parsed back into segments correctly

**Tasks:**
1. Add debug logging to `parse_tagged_text()`
2. Parse the tagged text from Phase 1
3. Print segments with formatting:
   ```
   Segment 1: text="Hello ", format_bits=0, metadata=None
   Segment 2: text="bold", format_bits=1, metadata=None
   Segment 3: text=" normal", format_bits=0, metadata=None
   Segment 4: text="\n\n", format_bits=0, metadata=None
   ```

**Success Criteria:**
- Segments have correct text ✓
- format_bits match expected values ✓
- Metadata (color, size, font) preserved ✓
- Blank line segments preserved ✓

---

### Phase 3: Debug ODT Output Generation (Session 13)
**Goal:** Fix `create_odt_from_segments()` to apply formatting correctly

**Tasks:**
1. Review `create_odt_from_segments()` implementation (lines 452-580 in format_mapper.py)
2. Compare with `create_docx_from_segments()` (working correctly)
3. Test ODT attribute names:
   - DOCX: `run.bold = True` → ODT: `style.addElement(TextProperties(fontweight='bold'))`
   - DOCX: `run.font.name = 'Arial'` → ODT: `TextProperties(fontfamily='Arial')`
   - DOCX: `run.font.size = Pt(12)` → ODT: `TextProperties(fontsize='12pt')`
4. Check style application is actually working
5. Verify blank lines: `P()` with no content should create blank paragraph

**Potential Issues to Check:**
- [ ] Style not being added to document's automatic styles
- [ ] Style reference not matching between creation and application
- [ ] Attribute names wrong (check odfpy documentation)
- [ ] Text not being added to Span correctly
- [ ] Empty paragraphs not being created for blank lines

**Debugging Strategy:**
```python
# Add prints in create_odt_from_segments()
print(f"Creating style: format_bits={segment.format_bits}, metadata={segment.metadata}")
print(f"Style name: {style_name}")
print(f"Applied to text: {segment.text[:50]}")
```

---

### Phase 4: Test Individual Formats (Session 14)
**Goal:** Test each format type individually

**Test Cases:**
1. **Bold only** - `<1>bold text</1>`
   - Expected: Text appears bold in saved ODT
   
2. **Italic only** - `<2>italic text</2>`
   - Expected: Text appears italic in saved ODT
   
3. **Font color only** - `<16:FF0000>red text</16>`
   - Expected: Text appears red in saved ODT
   
4. **Font size only** - `<32:12>12pt text</32>`
   - Expected: Text appears 12pt in saved ODT
   
5. **Font family only** - `<64:Arial>Arial text</64>`
   - Expected: Text appears in Arial font in saved ODT
   
6. **Combined** - `<113:FF0000,12,Arial>red bold Arial</113>`
   - Expected: All formats apply correctly

7. **Blank lines** - `Text\n\nText`
   - Expected: Visible space between paragraphs in saved ODT

**Success Criteria:**
- Each format works individually ✓
- Combined formats work together ✓
- Blank lines preserved ✓

---

### Phase 5: Compare DOCX vs ODT Output (Session 15)
**Goal:** Ensure ODT output matches DOCX quality

**Tasks:**
1. Translate same source to both DOCX and ODT
2. Open both files side-by-side
3. Visual comparison:
   - Bold/italic/underline appearance
   - Font families match
   - Font sizes match
   - Colors match (hex RGB → visual color)
   - Blank lines match

**Success Criteria:**
- ODT formatting matches DOCX formatting 100%

---

## Implementation Strategy

### Session 12: Debug Extraction & Parsing
- Add debug prints to extraction
- Test with simple ODT file
- Verify tags are correct
- Document findings

### Session 13: Fix ODT Output
- Review `create_odt_from_segments()`
- Fix style creation bugs
- Fix blank line handling
- Test basic formatting

### Session 14: Comprehensive Testing
- Test all format types individually
- Test combined formats
- Test edge cases (very long text, special characters)
- Create test report

### Session 15: Final Validation
- Side-by-side DOCX vs ODT comparison
- User acceptance testing
- Update documentation
- Close issue

---

## Technical Notes

### ODT Style Attribute Names (odfpy)
```python
from odf.style import Style, TextProperties, ParagraphProperties

# Text formatting
TextProperties(
    fontweight='bold',           # Bold
    fontstyle='italic',          # Italic
    textunderlinestyle='solid',  # Underline
    color='#FF0000',             # Font color (hex with #)
    fontsize='12pt',             # Font size (with 'pt')
    fontfamily='Arial'           # Font family
)

# Paragraph formatting
ParagraphProperties(
    textalign='center',          # Alignment: 'start', 'center', 'end', 'justify'
    lineheight='150%'            # Line spacing
)
```

### DOCX Style Application (python-docx) - WORKING
```python
run.bold = True
run.italic = True
run.underline = True
run.font.color.rgb = RGBColor(255, 0, 0)
run.font.size = Pt(12)
run.font.name = 'Arial'
```

### Key Differences
- ODT requires style objects, DOCX has inline properties
- ODT colors need '#' prefix, DOCX uses RGBColor object
- ODT sizes need 'pt' suffix, DOCX uses Pt() function
- ODT styles must be added to document.automaticstyles

---

## Expected Timeline

- **Session 12:** 30-45 minutes (debug extraction/parsing)
- **Session 13:** 45-60 minutes (fix ODT output)
- **Session 14:** 30-45 minutes (comprehensive testing)
- **Session 15:** 20-30 minutes (final validation)

**Total:** ~2.5-3 hours

---

## Success Criteria (Final)

- [ ] Bold text appears bold in saved ODT
- [ ] Italic text appears italic in saved ODT
- [ ] Underline text appears underlined in saved ODT
- [ ] Font colors preserved accurately
- [ ] Font sizes preserved accurately
- [ ] Font families preserved accurately
- [ ] Combined formats work correctly
- [ ] Blank lines visible in saved ODT
- [ ] ODT output quality matches DOCX output
- [ ] No crashes or errors during workflow
- [ ] User confirms: "it's working!"

---

## Questions for User

1. **Which formats are most important?** (Bold, colors, fonts, all?)
   - If answer is "all", proceed with full fix
   - If specific ones, prioritize those first

2. **Can you provide a test ODT file?**
   - Helps verify extraction is working
   - Can compare input vs output

3. **Test after each session or at the end?**
   - Iterative testing catches issues early
   - End testing is faster but riskier

---

**Status:** Plan created, ready to begin Session 12
**Next Step:** Start Phase 1 (Debug extraction with test file)
