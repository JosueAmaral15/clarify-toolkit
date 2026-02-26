# Action Plan: DOCX Translation with Structure Preservation - COM8

**Date:** 2026-02-16  
**Programmer:** COM8  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Task:** Implement DOCX translation with same quality as ODT translation  

---

## Problem Statement

### Current State:
- ❌ DOCX translation produces **corrupted output**
- ❌ Format tags visible in text: `<99|512:12,TimesNewRoman|1.0>`
- ❌ Tabs lost: "CAIT13/11/12" (no spaces between)
- ❌ Line breaks lost or merged
- ❌ Structure broken (text merged, formatting corrupted)

### User Report:
```
CAIT13/11/12
<99|512:12,TimesNewRoman|1.0>Class: 3001
Work Biology
[corrupted format tags throughout]
```

### Root Cause:
Current DOCX implementation uses **numeric tag system** (`format_mapper.py`) which:
- Google Translate corrupts/deletes tags
- Tags become visible in output
- No structure preservation (tabs, line-breaks)
- Different approach than successful ODT implementation

### Target State:
Apply **proven ODT approach** to DOCX:
- ✅ Perfect structure preservation (paragraphs, line-breaks, tabs)
- ✅ Complete format preservation (bold, italic, fonts, colors)
- ✅ Accurate translation
- ✅ No visible artifacts
- ✅ Same quality as ODT: 18P, 22LB, 14T preserved

---

## Test File

**File:** `docs/CAIT- Trabalho de Biologia - Josué 3001.docx`  
**Size:** 19KB  
**Language:** Portuguese → English  

**Expected Structure (from python-docx inspection):**
- Paragraphs: 18
- Non-empty: 13
- Empty: 5
- Tabs: 14
- Line breaks: 22

**Should Match ODT Results:**
- ODT: 18 paragraphs, 22 line-breaks, 14 tabs ✅
- DOCX: Should achieve same preservation

---

## Phase 1: Investigation & Analysis

### 1.1 Inspect Current DOCX Implementation ⏳
**Goal:** Understand existing code and why it fails

**Tasks:**
- [ ] Read `src/translation/format_mapper.py` (numeric tag system)
- [ ] Read `src/translation/document_parser.py` (DOCX parsing)
- [ ] Understand how current system works
- [ ] Document failure points
- [ ] Identify what can be reused vs needs replacement

**Deliverable:** Analysis document showing current flow and problems

### 1.2 Compare with ODT Success ⏳
**Goal:** Identify key differences

**Tasks:**
- [ ] Review `src/translation/html_format_mapper.py` (our success)
- [ ] List techniques that made ODT work:
  - HTML intermediate format
  - CSS class mapping
  - Invisible markers (brk1, brk2, data-tab)
  - Segment-based processing
- [ ] Identify what needs adaptation for DOCX

**Deliverable:** Comparison table ODT vs DOCX approaches

### 1.3 Study python-docx Library ⏳
**Goal:** Understand DOCX structure and capabilities

**Tasks:**
- [ ] Document DOCX element hierarchy:
  - Document → Paragraphs → Runs
  - Paragraph properties (alignment, spacing)
  - Run properties (bold, italic, font, color)
  - Special elements (Tab, LineBreak, etc.)
- [ ] Test extraction of all elements from test file
- [ ] Test creation of DOCX with all elements
- [ ] Document API capabilities and limitations

**Deliverable:** DOCX structure documentation with code examples

---

## Phase 2: Design

### 2.1 Architecture Design ⏳
**Goal:** Design DOCX mapper mirroring ODT approach

**Decisions:**
- **New file:** `src/translation/docx_html_mapper.py` (clean implementation)
- **Reuse:** HTMLSegment, CSSClassManager concepts
- **Same workflow:** DOCX → HTML → Translate → HTML → DOCX

**Tasks:**
- [ ] Design class structure (DocxHtmlMapper)
- [ ] Design segment types (reuse: div, span, br, line-break, tab)
- [ ] Plan format extraction (runs → formats)
- [ ] Plan HTML generation (same as ODT)
- [ ] Plan DOCX creation (HTML → python-docx elements)

**Deliverable:** Design document with class diagrams

### 2.2 Format Mapping Strategy ⏳
**Goal:** Map DOCX formats to CSS

**Tasks:**
- [ ] Map run properties to FormatAttributes:
  - bold → fmt.bold
  - italic → fmt.italic
  - underline → fmt.underline
  - font_name → fmt.font_family
  - font_size → fmt.font_size
  - font_color → fmt.font_color
- [ ] Map paragraph properties:
  - alignment → fmt.alignment
  - line_spacing → fmt.line_spacing
- [ ] Reuse CSSClassManager from ODT

**Deliverable:** Mapping specification

### 2.3 Special Elements Strategy ⏳
**Goal:** Handle tabs and line-breaks

**Tasks:**
- [ ] Tabs: Use `<span data-tab="1"></span>` (proven approach)
- [ ] Line-breaks: Use `<br class="brk2">` (proven approach)
- [ ] Paragraph breaks: Use `<br class="brk1">` (proven approach)
- [ ] Verify python-docx can create these elements

**Deliverable:** Special elements handling spec

---

## Phase 3: Implementation

### 3.1 Create DocxHtmlMapper Class ⏳
**Goal:** Core extraction functionality

**File:** `src/translation/docx_html_mapper.py`

**Tasks:**
- [ ] Create class structure
- [ ] Implement `extract_html_from_docx(file_path)`:
  - Load DOCX with python-docx
  - Iterate paragraphs
  - Extract runs with formatting
  - Create HTMLSegments
  - Generate HTML with markers
- [ ] Reuse CSSClassManager
- [ ] Add comprehensive docstrings

**Deliverable:** Extraction code (DOCX → HTML)

### 3.2 Implement Format Extraction ⏳
**Goal:** Extract all formatting from runs

**Tasks:**
- [ ] Create `_extract_run_format(run)` method
- [ ] Extract: bold, italic, underline, strikethrough
- [ ] Extract: font_name, font_size, font_color
- [ ] Extract: highlight_color (if available)
- [ ] Handle None values gracefully
- [ ] Map to FormatAttributes

**Deliverable:** Format extraction code

### 3.3 Implement Special Elements ⏳
**Goal:** Handle tabs and line-breaks

**Tasks:**
- [ ] Detect tabs in run.text (or as separate elements)
- [ ] Create 'tab' segments
- [ ] Detect line-breaks in run.text
- [ ] Create 'line-break' segments
- [ ] Split text at tab/line-break positions
- [ ] Maintain format across splits

**Deliverable:** Tab and line-break handling code

### 3.4 Implement HTML Generation ⏳
**Goal:** Generate clean HTML

**Tasks:**
- [ ] Reuse `_generate_html()` from ODT mapper
- [ ] Output:
  - `<span class="fmtX">text</span>` for formatted text
  - `<span data-tab="1"></span>` for tabs
  - `<br class="brk1">` for paragraph breaks
  - `<br class="brk2">` for line-breaks
- [ ] Add spaces between spans (prevent word merging)

**Deliverable:** HTML generation code

### 3.5 Implement DOCX Creation ⏳
**Goal:** Convert HTML back to DOCX

**Tasks:**
- [ ] Create `create_docx_from_html(html, css_manager, output_path)` function
- [ ] Parse HTML (reuse HTMLToODTParser concept)
- [ ] Create DOCX Document
- [ ] Create styles from CSS classes
- [ ] Build paragraphs:
  - 'br' (brk1) → new paragraph
  - 'line-break' (brk2) → add LineBreak() to current para
  - 'tab' → add Tab() to current para
  - 'text' → add Run with styling
- [ ] Save DOCX

**Deliverable:** DOCX creation code

---

## Phase 4: Testing

### 4.1 Unit Tests ⏳
**Goal:** Test individual components

**File:** `tests/com8/test_docx_html_mapper_COM8.py`

**Tests:**
- [ ] Test format extraction (bold, italic, fonts)
- [ ] Test tab detection and segmentation
- [ ] Test line-break detection and segmentation
- [ ] Test HTML generation
- [ ] Test CSS class management
- [ ] Test paragraph break handling

**Deliverable:** Unit test suite

### 4.2 End-to-End Test ⏳
**Goal:** Complete workflow test

**File:** `tests/com8/test_docx_end_to_end_COM8.py`

**Steps:**
1. Extract HTML from DOCX
2. Verify HTML structure (count BRs, tabs, etc.)
3. Translate HTML (Portuguese → English)
4. Create DOCX from translated HTML
5. Verify output structure:
   - Paragraph count: 18
   - Line-breaks: 22
   - Tabs: 14
   - Formats: preserved

**Success Criteria:**
- ✅ All structure preserved (18P, 22LB, 14T)
- ✅ All formatting preserved
- ✅ Translation accurate
- ✅ No visible artifacts
- ✅ Matches ODT quality

**Deliverable:** Passing end-to-end test

### 4.3 Output Verification ⏳
**Goal:** Manually verify output quality

**Protocol Requirement:** **READ THE OUTPUT BEFORE CLAIMING SUCCESS!**

**Tasks:**
- [ ] Open translated DOCX in LibreOffice/Word
- [ ] Verify first paragraph has tabs: "CAIT[TAB]...[TAB]13/11/12"
- [ ] Verify line breaks between sections (not merged)
- [ ] Verify formatting (bold headings, etc.)
- [ ] Compare side-by-side with original
- [ ] Count elements programmatically
- [ ] Document any discrepancies

**Deliverable:** Verification report with screenshots/samples

---

## Phase 5: Documentation

### 5.1 Code Documentation ⏳
**Goal:** Comprehensive inline documentation

**Tasks:**
- [ ] Add module docstring
- [ ] Add class docstrings
- [ ] Add method docstrings (Google style)
- [ ] Add inline comments for complex logic
- [ ] Document known limitations
- [ ] Add usage examples

**Deliverable:** Documented code

### 5.2 Technical Documentation ⏳
**Goal:** Explain how it works

**File:** `docs/com8/DOCX_TRANSLATION_TECHNICAL_COM8.md`

**Content:**
- Architecture overview
- Workflow diagram
- Format mapping details
- Special elements handling
- Comparison with ODT approach
- Known limitations
- Troubleshooting guide

**Deliverable:** Technical documentation

### 5.3 Testing Documentation ⏳
**Goal:** Document test results

**File:** `docs/com8/DOCX_TRANSLATION_TEST_RESULTS_COM8.md`

**Content:**
- Test file details
- Structure verification (tables/numbers)
- Format verification
- Translation quality samples
- Performance metrics
- Comparison with original

**Deliverable:** Test results document

---

## Phase 6: Integration & Cleanup

### 6.1 Integration with GUI ⏳
**Goal:** Make feature accessible

**Tasks:**
- [ ] Update `google_translate_dock.py` to support DOCX
- [ ] Add file type detection (.docx)
- [ ] Route to appropriate mapper (ODT vs DOCX)
- [ ] Update UI messages
- [ ] Add error handling

**Deliverable:** GUI integration

### 6.2 Deprecate Old Implementation ⏳
**Goal:** Remove broken code

**Tasks:**
- [ ] Document why old approach failed
- [ ] Mark `format_mapper.py` as deprecated (if not used elsewhere)
- [ ] Update imports in codebase
- [ ] Remove unused code
- [ ] Update documentation references

**Deliverable:** Clean codebase

### 6.3 Final Testing ⏳
**Goal:** Comprehensive validation

**Tasks:**
- [ ] Test with original file (CAIT document)
- [ ] Test with additional DOCX files (various formats)
- [ ] Test error handling (corrupt files, unsupported formats)
- [ ] Test performance (large documents)
- [ ] Verify no regressions in ODT translation

**Deliverable:** Final test report

---

## Success Criteria

### Functional Requirements:
- ✅ Exact paragraph count preserved (18 == 18)
- ✅ All line-breaks preserved (22 == 22)
- ✅ All tabs preserved (14 == 14)
- ✅ All formatting preserved (bold, italic, fonts, colors)
- ✅ Accurate translation (same quality as Google Translate)
- ✅ No visible artifacts (no format tags, no placeholders)
- ✅ Clean, professional output

### Quality Requirements:
- ✅ Matches ODT translation quality
- ✅ Code is well-documented
- ✅ Tests pass (unit + end-to-end)
- ✅ User validation: "it's working!"
- ✅ Protocol compliance (verify output before claiming success)

### Performance Requirements:
- ⏳ Translation time: < 30 seconds for 19KB file
- ⏳ No memory leaks
- ⏳ Handles large documents (> 1MB)

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Investigation | 3 sections | 1-2 hours |
| Phase 2: Design | 3 sections | 1 hour |
| Phase 3: Implementation | 5 sections | 3-4 hours |
| Phase 4: Testing | 3 sections | 1-2 hours |
| Phase 5: Documentation | 3 sections | 1 hour |
| Phase 6: Integration | 3 sections | 1 hour |
| **Total** | **20 sections** | **8-11 hours** |

---

## Risk Mitigation

### Risk 1: python-docx Limitations
**Risk:** Library may not support all format features  
**Mitigation:** Research library capabilities early (Phase 1.3)  
**Fallback:** Document limitations, partial feature support

### Risk 2: Different Structure than ODT
**Risk:** DOCX structure fundamentally different  
**Mitigation:** Study structure thoroughly (Phase 1.3)  
**Fallback:** Adapt HTML approach as needed

### Risk 3: Google Translate Behavior
**Risk:** May handle DOCX-generated HTML differently  
**Mitigation:** Test early with actual translation (Phase 4.2)  
**Fallback:** Adjust markers/placeholders if needed

### Risk 4: Format Loss
**Risk:** Some formats may not survive conversion  
**Mitigation:** Comprehensive testing (Phase 4)  
**Fallback:** Document limitations clearly

---

## Protocol Compliance Checklist

Following SIMPLICITY_PROTOCOL_3:

- [ ] **Read 100% of relevant code** before implementing
  - [ ] format_mapper.py (current implementation)
  - [ ] document_parser.py (DOCX parsing)
  - [ ] html_format_mapper.py (ODT success)
  - [ ] python-docx documentation

- [ ] **Create action plan** (this document) ✅

- [ ] **Test and verify output** after EACH phase
  - Protocol lesson learned: "why you didn't read the output?"
  - NEVER claim success without reading actual output
  - Compare with original: paragraph count, line-breaks, tabs

- [ ] **Document everything**
  - Technical documentation
  - Test results
  - Known limitations

- [ ] **User validation**
  - User must confirm: "it's working!"
  - Address all user feedback
  - Iterate until satisfied

- [ ] **Commit with clear messages**
  - Reference bug numbers
  - Explain what/why/how
  - Include test results

---

## Next Steps

1. **User Approval:** Get confirmation to proceed with this plan
2. **Start Phase 1.1:** Investigate current DOCX implementation
3. **Daily Updates:** Report progress and blockers
4. **Iterative Validation:** Test output after each major component

---

## Questions for User

Before proceeding:

1. **Approval:** Is this action plan acceptable?
2. **Priority:** Any specific aspects to focus on first?
3. **Scope:** Should we also test with other DOCX files, or just CAIT document?
4. **Timeline:** Any deadline or urgency?
5. **Old Code:** Should we keep `format_mapper.py` or completely replace it?

---

**Status:** ⏳ AWAITING USER APPROVAL TO PROCEED

**Programmer:** COM8  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3
