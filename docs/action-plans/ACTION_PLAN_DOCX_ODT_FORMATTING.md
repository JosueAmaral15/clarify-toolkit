# Action Plan: DOCX/ODT Translation with Formatting Preservation

**Programmer**: COM8  
**Date**: 2026-01-27  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5  
**Project**: Multi-week feature (60-100 hours estimated)

## User Confirmation

✅ User wants formatting preservation (not plain text)  
✅ User aware this is multi-week project with high complexity  
✅ Google Translate preserves custom tags: `<14>bold</14>` → `<14>negrito</14>` ✓

## Questions Needed Before Planning

### Q1: Formatting Scope - What to preserve?

**Text formatting:**
- [ ] Bold
- [ ] Italic
- [ ] Underline
- [ ] Strikethrough
- [ ] Font color
- [ ] Font size
- [ ] Font family
- [ ] Highlight/background color

**Paragraph formatting:**
- [ ] Alignment (left/center/right/justify)
- [ ] Line spacing
- [ ] Indentation
- [ ] Bulleted lists
- [ ] Numbered lists

**Document structure:**
- [ ] Headings (H1, H2, H3, etc.)
- [ ] Tables
- [ ] Images (keep in place, don't translate)
- [ ] Page breaks
- [ ] Headers/footers

**Which of these do you want? (Check all that apply)**

### Q2: Tag System Design

You suggested numeric tags with binary encoding:
- `<14>` = bold (binary: 01110)
- `<16>` = italic (binary: 10000)

**Questions:**
1. Is this binary system necessary, or can we use simpler tags?
   - Simple: `<b>bold</b> <i>italic</i> <bi>both</bi>`
   - Your way: `<14>bold</14> <16>italic</16> <24>both</24>`
   
   Which do you prefer?

2. How many formatting combinations maximum?
   - If we support 5 formats = 32 combinations (2^5)
   - If we support 10 formats = 1024 combinations (2^10)
   - Need to know the maximum tag number

3. Should tags be invisible to Google Translate?
   - Add special prefix/suffix? `<fmt:14>text</fmt:14>`
   - Or keep simple? `<14>text</14>`

### Q3: Output Format

After translation, save as:
- [ ] A) Original format (`.docx` → translated `.docx`)
- [ ] B) Different format (`.docx` → translated `.odt`)
- [ ] C) Both original + plain text backup
- [ ] D) User chooses in "Save As" dialog

Which option?

### Q4: Dependencies

Need to add to `pyproject.toml`:
- `python-docx` (for `.docx` read/write)
- `odfpy` (for `.odt` read/write)
- `lxml` (for XML parsing, if needed)

Confirm: Add these dependencies? YES/NO?

### Q5: Edge Cases

**What should happen if:**
1. Google Translate breaks a tag? 
   - `<14>text</14>` becomes `<14>text` (missing closing)
   - Action: Show error? Try to fix? Skip formatting?

2. Text inside tag gets split?
   - `<14>hello world</14>` becomes `<14>hello</14> world`
   - Action: Guess formatting? Show warning?

3. Tags get reordered?
   - `<14>A</14> <16>B</16>` becomes `<16>B</16> <14>A</14>`
   - Action: This should be OK (translation can reorder)

4. File has unsupported elements (charts, equations)?
   - Action: Keep unchanged? Remove? Show warning?

Please answer all your preferences.

### Q6: Testing Strategy

This needs extensive testing. Will you:
- [ ] Provide test `.docx`/`.odt` files with various formatting?
- [ ] Test each feature as I implement (iterative)?
- [ ] Wait until all features done, then test (risky)?

Which approach?

### Q7: Implementation Order

Suggested phases (you can modify):

**Phase 1** (Week 1): Foundation - 15-20 hours
- Add dependencies
- Extract plain text from `.docx`/`.odt`
- Basic tag injection (bold + italic only)
- Translate with tags
- Remove tags from output (plain text)
- **Deliverable**: Can translate `.docx`/`.odt` to plain text

**Phase 2** (Week 2): Formatting restoration - 20-25 hours
- Parse tagged translation
- Restore bold + italic to new `.docx`
- Handle tag parsing errors
- **Deliverable**: Simple formatted `.docx` output

**Phase 3** (Week 3): Advanced formatting - 15-20 hours
- Add more formats (underline, color, size, etc.)
- Support paragraphs, lists
- **Deliverable**: Most formatting preserved

**Phase 4** (Week 4): Polish & edge cases - 10-15 hours
- Handle tables, images
- Error recovery
- User warnings
- **Deliverable**: Production-ready

Do you approve this plan? Any changes?

---

## Blocking: Need Answers Before Starting

**Cannot proceed until you answer Q1-Q7 above.**

Following protocol: Must clarify requirements completely before implementation.


## Requirements Confirmed ✅

### Q1: Formatting Scope
✅ **ALL formatting preserved:**
- Text: bold, italic, underline, strikethrough, font color, font size, font family, highlight
- Paragraph: alignment, line spacing, indentation, bulleted lists, numbered lists
- Structure: headings, tables, images, page breaks, headers/footers

### Q2: Tag System Design
✅ **Binary system with additive combination:**
- Each format = power of 2 (bit position)
- Combinations = sum of values
- Example mapping:
  - Bit 0 (2^0 = 1): Bold
  - Bit 1 (2^1 = 2): Italic
  - Bit 2 (2^2 = 4): Underline
  - Bit 3 (2^3 = 8): Strikethrough
  - Bit 4 (2^4 = 16): Font color (need color map)
  - etc.
- Combined: Bold+Italic = 1+2 = 3 → `<3>text</3>`
- Combined: Bold+Underline = 1+4 = 5 → `<5>text</5>`

### Q3: Output Format
✅ **User chooses** in Save As dialog:
- Same format (.docx → .docx)
- Different format (.docx → .odt)
- Plain text (.txt) fallback

### Q4: Dependencies
✅ **YES** - Add to pyproject.toml:
- python-docx
- odfpy
- lxml (if needed)

### Q5: Error Handling
✅ **Strategy:**
- Debug prints during development
- Online research for edge cases
- Graceful degradation (show warning, continue without formatting)

### Q6: Testing
✅ **Iterative** - test each phase as implemented

### Q7: Implementation Plan
✅ **Approved** - 4 week plan

---

## Final Clarifications Needed

### Format Encoding Questions

**Font Color/Size/Family:**
- These have infinite values (RGB colors, pt sizes, font names)
- Cannot use simple binary bit for these
- **Solution proposal:**
  - Tag format: `<tag_id:metadata>text</tag_id>`
  - Example: `<16:FF0000>red text</16>` (16 = color flag, FF0000 = hex color)
  - Example: `<32:18>large text</32>` (32 = size flag, 18 = font size)
  - Example: `<64:Arial>arial text</64>` (64 = font flag, Arial = font name)

**Combined with metadata:**
- Bold + Red: `<17:FF0000>bold red</17>` (17 = 1+16 = bold+color)
- Bold + Italic + 18pt: `<35:18>text</35>` (35 = 1+2+32 = bold+italic+size)

**Question:** Does this extended tag format work for you? Or different approach?

---

### Paragraph/Structure Encoding

**Lists, tables, alignment** are not character-level formatting - they're structural.

**Problem:**
```
<bulleted_list>
  <item>First item with <1>bold</1> text</item>
  <item>Second item</item>
</bulleted_list>
```

Google Translate will translate content but may break structure tags.

**Solution proposal:**
- Don't encode structural elements as inline tags
- Keep structural elements in document, translate text content separately
- Reconstruct structure after translation

**Question:** Agree with this approach? Or encode structure as inline tags too?

---

### Image Handling

**Images cannot be translated.** Should we:
- A) Keep images in exact same position (don't translate alt-text)
- B) Translate image alt-text/captions
- C) Extract images, show warning, exclude from translation

**Question:** Which approach?

---

### Table Handling

**Tables have:**
- Cell content (translate)
- Cell borders/styling (keep)
- Merged cells (complex)

**Strategy:**
- Translate each cell content individually
- Preserve table structure
- Risk: Cell content length changes → table may look broken

**Question:** Is this acceptable? Or need dynamic table resizing?

---

## Tag Number Space Planning

Based on all formats, here's the bit mapping:

**Character formatting (bits 0-7):**
- Bit 0 (1): Bold
- Bit 1 (2): Italic  
- Bit 2 (4): Underline
- Bit 3 (8): Strikethrough
- Bit 4 (16): Font color (needs metadata)
- Bit 5 (32): Font size (needs metadata)
- Bit 6 (64): Font family (needs metadata)
- Bit 7 (128): Highlight color (needs metadata)

**Paragraph formatting (bits 8-11):**
- Bit 8 (256): Alignment (needs metadata: left/center/right/justify)
- Bit 9 (512): Line spacing (needs metadata)
- Bit 10 (1024): Indentation (needs metadata)
- Bit 11 (2048): Heading level (needs metadata: H1-H6)

**Maximum tag value:** 4095 (all bits set)
**Tag format:** `<tag_id:metadata>text</tag_id>`

**Question:** Does this bit allocation work? Any changes?

---

## Next Steps - BLOCKING

1. **Confirm extended tag format** (with metadata after colon)
2. **Confirm structural element handling** (reconstruct vs inline tags)
3. **Confirm image handling** approach (A, B, or C)
4. **Confirm table handling** approach (preserve structure, accept length changes)
5. **Confirm bit allocation** (12 bits = 4096 combinations)

After you answer these 5 final questions, I will:
- Create detailed Phase 1 action plan
- Add dependencies to pyproject.toml
- Start implementation

**Cannot proceed until these 5 answered.**


## Final Requirements - ALL CONFIRMED ✅

### 1. Tag Format with Metadata
✅ `<tag_id:metadata>text</tag_id>`
- Example: `<17:FF0000>bold red</17>` (17 = 1+16, FF0000 = red color)

### 2. Structural Elements
✅ **Reconstruct approach** - keep structure separate, translate text, rebuild

### 3. Images
✅ **Option B** - Translate image captions/alt-text

### 4. Tables
✅ **Acceptable** - Translate cells, keep structure, accept length changes

### 5. Bit Allocation (User Clarified)
✅ **Fixed mapping** (I decide, document clearly):

**Character-level formatting:**
- Bit 0 (2^0 = 1): **Bold**
- Bit 1 (2^1 = 2): **Italic**
- Bit 2 (2^2 = 4): **Underline**
- Bit 3 (2^3 = 8): **Strikethrough**
- Bit 4 (2^4 = 16): **Font Color** (metadata: hex RGB)
- Bit 5 (2^5 = 32): **Font Size** (metadata: pt value)
- Bit 6 (2^6 = 64): **Font Family** (metadata: font name)
- Bit 7 (2^7 = 128): **Highlight Color** (metadata: hex RGB)

**Paragraph-level formatting:**
- Bit 8 (2^8 = 256): **Alignment** (metadata: L/C/R/J)
- Bit 9 (2^9 = 512): **Line Spacing** (metadata: multiplier)
- Bit 10 (2^10 = 1024): **Indentation** (metadata: pt value)
- Bit 11 (2^11 = 2048): **Heading Level** (metadata: 1-6)

**Examples:**
- Bold only: `<1>text</1>`
- Bold + Italic: `<3>text</3>` (1+2)
- Bold + Red: `<17:FF0000>text</17>` (1+16)
- Italic + 14pt: `<34:14>text</34>` (2+32)
- Bold + Italic + Underline + Red + Arial: `<71:FF0000,Arial>text</71>` (1+2+4+16+64)

**Metadata format when multiple:**
- Single: `<17:FF0000>text</17>`
- Multiple: `<71:FF0000,Arial>text</71>` (comma-separated, order matches bit positions)

---

## Phase 1: Foundation (THIS WEEK)

**Estimated: 15-20 hours over 5-7 days**

### Session 1: Setup Dependencies (2 hours)
- [ ] Add python-docx to pyproject.toml
- [ ] Add odfpy to pyproject.toml
- [ ] Add lxml if needed
- [ ] Install dependencies
- [ ] Test imports
- [ ] Commit

### Session 2: File Type Detection (1 hour)
- [ ] Update file browser filter: "Text Files (*.txt);;Word (*.docx);;OpenDocument (*.odt);;All Files (*)"
- [ ] Detect file type on browse
- [ ] Add UI indicator for file type
- [ ] Commit

### Session 3: DOCX Plain Text Extraction (3 hours)
- [ ] Create module: `src/translation/document_parser.py`
- [ ] Implement `extract_text_from_docx(filepath) -> str`
- [ ] Test with sample .docx files
- [ ] Handle errors gracefully
- [ ] Commit

### Session 4: ODT Plain Text Extraction (3 hours)
- [ ] Implement `extract_text_from_odt(filepath) -> str`
- [ ] Test with sample .odt files
- [ ] Handle errors gracefully
- [ ] Commit

### Session 5: Format Detection & Tag Injection (4 hours)
- [ ] Create `FormatMapper` class
- [ ] Implement bit encoding logic
- [ ] Extract bold/italic from DOCX (focus on these 2 first)
- [ ] Inject tags: `<1>bold text</1>`, `<3>bold italic</3>`
- [ ] Test: original text → tagged text
- [ ] Commit

### Session 6: Translation with Tags (2 hours)
- [ ] Send tagged text to Google Translate
- [ ] Verify tags preserved in output
- [ ] Test with various languages
- [ ] Commit

### Session 7: Tag Removal (Plain Text Output) (2 hours)
- [ ] Implement tag removal from translated text
- [ ] Save as plain .txt file
- [ ] Test end-to-end: .docx → translate → .txt (plain)
- [ ] Commit

**Phase 1 Deliverable:** Can translate .docx/.odt files → plain text .txt output (tags work but not restored to formatting yet)

---

## BLOCKING: Need Your Confirmation

**Before I start Phase 1, confirm:**

1. ✅ You will provide test .docx/.odt files with formatting? (or should I create them?)
2. ✅ Iterative testing after each session?
3. ✅ Start with Phase 1 Session 1 (add dependencies)?

**Should I proceed with Phase 1 Session 1 NOW?** (YES/NO)


---

## Phase 1 Progress Tracking

### ✅ Session 1: Setup Dependencies (COMPLETE)
**Date**: 2026-01-27  
**Time spent**: 30 minutes  
**Status**: SUCCESS

**What was done:**
- Added `python-docx>=1.1.0` to pyproject.toml
- Added `odfpy>=1.4.1` to pyproject.toml
- Installed both dependencies (odfpy-1.4.1, python-docx-1.2.0)
- Verified imports work correctly
- Committed changes

**Testing:**
```python
import docx  # ✓ Works
import odf   # ✓ Works
```

**Next**: Session 2 - File Type Detection (update Browse dialog filters)

