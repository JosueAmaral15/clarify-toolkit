# Phase 2: Format Restoration - DOCX Output with Formatting (COM8)

**Status**: 🚀 STARTING  
**Prerequisite**: Phase 1 COMPLETE ✅  
**Estimated Time**: 20-25 hours (7 sessions)  
**Goal**: Save translated DOCX files with formatting restored from tags

---

## Prerequisites Checklist

✅ Phase 1 complete (all 7 sessions done)  
✅ `FormatMapper` class exists and tested  
✅ Tags preserved through translation  
✅ User has tested Phase 1 features  
✅ Branch `COM8-documentation-reading` up to date

---

## Phase 2 Architecture Overview

### Current State (Phase 1)
```
Input DOCX → Extract with tags → Translate → Remove tags → Save TXT
Example: "Hello **world**" → "<1>world</1>" → "<1>mundo</1>" → "mundo"
```

### Target State (Phase 2)
```
Input DOCX → Extract with tags → Translate → Parse tags → Restore formatting → Save DOCX
Example: "Hello **world**" → "<1>world</1>" → "<1>mundo</1>" → "Hello **mundo**"
```

### Key Challenges

1. **Tag Parsing**: Convert `<1>mundo</1>` back into `TextSegment(text="mundo", format_bits=1)`
2. **DOCX Generation**: Create new document with `python-docx`
3. **Format Application**: Apply bold/italic/underline to runs based on format_bits
4. **Paragraph Handling**: Preserve paragraph breaks and structure
5. **Error Handling**: Handle malformed tags from translation

---

## Session Plan

### Session 1: Tag Parsing Enhancement (3 hours)
**Goal**: Parse tagged translation back into structured segments

**Tasks**:
- [ ] Review existing `parse_tagged_text()` in `format_mapper.py`
- [ ] Enhance to handle translation edge cases:
  - [ ] Tags with whitespace: `< 1>text</ 1>`
  - [ ] Nested tags (if they appear): `<1><2>text</2></1>`
  - [ ] Missing closing tags: `<1>text` → recover gracefully
- [ ] Add error recovery for malformed tags
- [ ] Test with real translation outputs (various languages)
- [ ] Add logging/debug prints for tag parsing
- [ ] Commit changes

**Testing**:
```python
from src.translation.format_mapper import FormatMapper

# Test cases
test1 = "Hello <1>mundo</1>!"
segments = FormatMapper.parse_tagged_text(test1)
assert len(segments) == 3
assert segments[1].format_bits == 1
assert segments[1].text == "mundo"

# Test malformed
test2 = "Hello <1>mundo!"
segments = FormatMapper.parse_tagged_text(test2)
# Should recover: treat as unformatted or apply formatting anyway?
```

**Deliverable**: Robust tag parser that handles translation quirks

---

### Session 2: Basic DOCX Writer (4 hours)
**Goal**: Create new DOCX from TextSegments with bold/italic/underline

**Tasks**:
- [ ] Create `create_docx_from_segments()` in `format_mapper.py`
- [ ] Initialize new `Document()` from python-docx
- [ ] Process segments sequentially:
  - [ ] Plain text (format_bits=0): add normal run
  - [ ] Bold (format_bits=1): add run with `.bold = True`
  - [ ] Italic (format_bits=2): add run with `.italic = True`
  - [ ] Bold+Italic (format_bits=3): add run with both
  - [ ] Underline (format_bits=4): add run with `.underline = True`
- [ ] Handle paragraph breaks (`\n\n` in text → new paragraph)
- [ ] Save to file path
- [ ] Test with simple examples
- [ ] Commit

**Testing**:
```python
from src.translation.format_mapper import FormatMapper, TextSegment
from docx import Document

# Create segments
segments = [
    TextSegment(text="Hello ", format_bits=0),
    TextSegment(text="mundo", format_bits=1),  # bold
    TextSegment(text="!", format_bits=0)
]

# Generate DOCX
output_path = "test_output.docx"
FormatMapper.create_docx_from_segments(segments, output_path)

# Verify
doc = Document(output_path)
para = doc.paragraphs[0]
assert len(para.runs) == 3
assert para.runs[1].bold == True
print("✓ DOCX generation working!")
```

**Deliverable**: Basic DOCX writer supporting bold/italic/underline

---

### Session 3: UI Integration - "Save As DOCX" Button (3 hours)
**Goal**: Add UI option to save translation as formatted DOCX

**Tasks**:
- [ ] Update `google_translate_dock.py`
- [ ] Modify `_save_as()` to detect output format:
  - [ ] If "Remove tags" is UNCHECKED → save as DOCX with formatting
  - [ ] If "Remove tags" is CHECKED → save as TXT (existing behavior)
- [ ] Update save dialog file filter:
  - [ ] "Word Documents (*.docx);;Text Files (*.txt);;All Files (*)"
- [ ] Parse tagged translation using `parse_tagged_text()`
- [ ] Generate DOCX using `create_docx_from_segments()`
- [ ] Handle errors gracefully (malformed tags → show warning)
- [ ] Update i18n strings if needed
- [ ] Test end-to-end workflow
- [ ] Commit

**User Workflow**:
1. Load `test.docx` with "Hello **world**"
2. Translate to Portuguese
3. Uncheck "Remove formatting tags"
4. Click "Save As..."
5. Choose "Word Documents (*.docx)"
6. Save as `translation_output.docx`
7. Open in Word/LibreOffice → verify "Olá **mundo**" with bold

**Deliverable**: Users can save DOCX with formatting restored

---

### Session 4: Advanced Formatting - Colors & Fonts (4 hours)
**Goal**: Support font color, size, family in tags with metadata

**Tasks**:
- [ ] Update `extract_formatted_text_from_docx()` to detect:
  - [ ] Font color: `run.font.color.rgb` → extract RGB
  - [ ] Font size: `run.font.size` → extract pt value
  - [ ] Font family: `run.font.name` → extract name
- [ ] Generate extended tags with metadata:
  - [ ] `<17:FF0000>red bold</17>` (17 = 1+16, FF0000 = red)
  - [ ] `<34:Arial>italic arial</34>` (34 = 2+64, Arial = font)
- [ ] Update `parse_tagged_text()` to parse metadata
- [ ] Update `create_docx_from_segments()` to apply:
  - [ ] `run.font.color.rgb = RGBColor(...)`
  - [ ] `run.font.size = Pt(...)`
  - [ ] `run.font.name = "..."`
- [ ] Test with colorful documents
- [ ] Commit

**Testing**:
```python
# Create test DOCX with red bold text
doc = Document()
para = doc.add_paragraph()
run = para.add_run("Red Bold")
run.bold = True
run.font.color.rgb = RGBColor(255, 0, 0)  # Red
doc.save("test_colors.docx")

# Extract → should produce: "<17:FF0000>Red Bold</17>"
tagged = FormatMapper.extract_formatted_text_from_docx("test_colors.docx")
print(tagged)  # Verify metadata tag

# Translate → Parse → Restore
segments = FormatMapper.parse_tagged_text(tagged)
FormatMapper.create_docx_from_segments(segments, "output_colors.docx")

# Open output_colors.docx → verify red bold formatting
```

**Deliverable**: Colors, fonts, sizes preserved through translation

---

### Session 5: Paragraph Formatting - Alignment & Spacing (3 hours)
**Goal**: Preserve paragraph-level formatting (alignment, spacing)

**Tasks**:
- [ ] Detect paragraph alignment: `paragraph.alignment`
- [ ] Detect line spacing: `paragraph.paragraph_format.line_spacing`
- [ ] Encode as paragraph-level tags (bits 8-10)
- [ ] Apply to output paragraphs during DOCX generation
- [ ] Test with mixed alignment (center, right, justify)
- [ ] Commit

**Challenge**: Paragraph formatting applies to whole paragraph, not runs
**Solution**: Track paragraph-level format separately, apply when creating paragraph

**Deliverable**: Alignment and spacing preserved

---

### Session 6: Stress Testing & Edge Cases (3 hours)
**Goal**: Test with complex real-world documents

**Tasks**:
- [ ] Create/download test documents with:
  - [ ] Mixed formatting (bold + italic + colors)
  - [ ] Long paragraphs (1000+ words)
  - [ ] Multiple paragraphs with different alignments
  - [ ] Special characters (emoji, accents, Chinese, Arabic)
  - [ ] Edge cases (empty paragraphs, tabs, line breaks)
- [ ] Test translation with various language pairs:
  - [ ] EN → PT, ES, FR, DE, ZH, AR
- [ ] Document known bugs/limitations
- [ ] Fix critical issues found
- [ ] Commit fixes

**Testing Checklist**:
- [ ] Tags survive translation in all tested languages
- [ ] Formatting restored correctly
- [ ] No crashes with edge cases
- [ ] Error messages are user-friendly
- [ ] Output DOCX opens in Word/LibreOffice without corruption

**Deliverable**: Robust implementation tested with real documents

---

### Session 7: Documentation & Polish (2 hours)
**Goal**: Document feature, add tooltips, update README

**Tasks**:
- [ ] Update tooltip for "Remove formatting tags" checkbox:
  - [ ] "When checked: save as plain text (.txt)"
  - [ ] "When unchecked: save as formatted document (.docx)"
- [ ] Add status messages:
  - [ ] "Formatting detected: X tags applied"
  - [ ] "Formatting restored: saved as DOCX"
- [ ] Create `DOCX_FORMATTING_GUIDE.md`:
  - [ ] How the feature works
  - [ ] Supported formats (bold, italic, colors, etc.)
  - [ ] Known limitations
  - [ ] Troubleshooting
- [ ] Add to main README.md (Features section)
- [ ] Take screenshots for documentation
- [ ] Commit documentation

**Deliverable**: Feature fully documented and user-friendly

---

## Success Criteria

Phase 2 is complete when:

✅ Users can load `.docx` with formatting  
✅ Translation preserves formatting via tags  
✅ Saved `.docx` restores formatting (bold, italic, underline, colors, fonts)  
✅ Paragraph alignment/spacing preserved  
✅ Edge cases handled gracefully (malformed tags → warnings)  
✅ Tested with multiple languages  
✅ Documentation complete  
✅ All commits pushed to remote

---

## Known Limitations (Acceptable for Phase 2)

- ❌ ODT formatting not yet supported (deferred to Phase 3)
- ❌ Tables not handled (plain text extraction only)
- ❌ Images not handled (excluded from translation)
- ❌ Lists (bullet/numbered) treated as plain paragraphs
- ❌ Headers/footers not preserved
- ❌ Page breaks not preserved

These will be addressed in Phase 3 (Advanced Formatting).

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Google Translate breaks tags | Medium | High | Robust tag parser with error recovery |
| python-docx API complexity | Low | Medium | Follow official docs, test incrementally |
| Format restoration bugs | High | Medium | Extensive testing, debug prints |
| User expects perfect formatting | Medium | Low | Clear documentation of limitations |
| Performance issues (large files) | Low | Low | Test with large files, optimize if needed |

---

## Phase 3 Preview (Advanced Formatting)

After Phase 2 complete, Phase 3 will add:
- Tables (preserve structure, translate cells)
- Lists (bullet/numbered)
- Images (translate captions)
- Headers/footers
- ODT formatting support
- Complex document structures

**Estimated**: 15-20 hours (5-6 sessions)

---

**Ready to start Phase 2 Session 1?**
