# Action Plan: Investigate Whitespace/Tab Loss Issues (COM8)

**Session:** COM8  
**Date:** 2026-02-15  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Branch:** COM8-documentation-reading  
**Programmer:** COM8

---

## Problem Statement

**Issues Found in Translated ODT:**

1. **Tabs converted to nothing:**
   - Original: `CAIT[TAB]13/11/12` 
   - Translated: `CAIT13/11/12` (no space!)
   - Expected: `CAIT 13/11/12` or `CAIT[TAB]13/11/12`

2. **Missing spaces between adjacent sections:**
   - "allergiesWhen" should be "allergies When"
   - "antibioticsTo" should be "antibiotics To"
   - "substancesThere" should be "substances There"
   - "residuesWith" should be "residues With"

**Impact:** Document readability is poor, words are merged together.

---

## Investigation Plan

### Phase 1: Understand HTML Entity Handling (30 min)
- [ ] Research how Google Translate API handles HTML entities
- [ ] Specifically check: `&#9;` (tab), `&#160;` (non-breaking space)
- [ ] Search online: "Google Translate API HTML entity preservation"
- [ ] Search online: "Google Translate removes tabs"
- [ ] Document findings

### Phase 2: Test HTML Entity Preservation (20 min)
- [ ] Create test with various entities:
  - `&#9;` (tab)
  - `&#160;` (non-breaking space)
  - `&nbsp;` (named entity)
  - Regular space
  - Multiple spaces
- [ ] Send each to Google Translate
- [ ] Document what gets preserved vs lost

### Phase 3: Investigate Missing Spaces Between Spans (30 min)
- [ ] Check translated HTML for cases like "allergiesWhen"
- [ ] Look at original HTML structure around these points
- [ ] Identify: Are adjacent `</span><span>` causing merges?
- [ ] Check if Google Translate is removing whitespace between tags

### Phase 4: Research Solutions (45 min)
- [ ] Online search: "preserve whitespace Google Translate API"
- [ ] Online search: "HTML formatting Google Translate"
- [ ] Check Google Cloud Translation API documentation
- [ ] Look for parameters/options to preserve formatting
- [ ] Research alternative approaches:
  - Use actual tab characters instead of entities?
  - Add explicit spaces between spans?
  - Use different entity encoding?

### Phase 5: Test Solutions (60 min)
- [ ] Test Solution A: Convert `&#9;` to `&nbsp;&nbsp;&nbsp;` (multiple non-breaking spaces)
- [ ] Test Solution B: Add space between adjacent `</span><span>` tags
- [ ] Test Solution C: Use actual tab character `\t` instead of `&#9;`
- [ ] Test Solution D: Use `<span> </span>` for spacing
- [ ] Document results for each

### Phase 6: Implement Best Solution (30 min)
- [ ] Choose best approach based on test results
- [ ] Modify `extract_html_from_odt()` if needed
- [ ] Modify HTML structure if needed
- [ ] Test with full document
- [ ] Verify improvements

### Phase 7: Final Verification (20 min)
- [ ] Run end-to-end test
- [ ] Read all paragraphs
- [ ] Check for tab preservation
- [ ] Check for missing spaces
- [ ] Document remaining issues

---

## Research Notes

### Google Translate API Behavior

**Research completed 2026-02-15**

**Official Documentation:**
- Google Cloud Translation API converts HTML entities to regular spaces
- Whitespace normalization is standard behavior
- No parameters exist to preserve HTML entities like &#9; or &#160;

**Online Search Results:**
- Multiple developers report same issue with tab/nbsp preservation
- Common workaround: Accept single space conversion
- Alternative: Use visible separators (|, -, etc.) instead of tabs

**Experimental Testing (10 test cases):**

| Test | Input | Output | Result |
|------|-------|--------|--------|
| 1 | `&#9;` (tab entity) | `<span> </span>` | ❌ Lost → single space |
| 2 | `&#160;` (nbsp entity) | `<span> </span>` | ❌ Lost → single space |
| 3 | `&nbsp;` (named entity) | `<span> </span>` | ❌ Lost → single space |
| 4 | `&nbsp;&nbsp;&nbsp;&nbsp;` (4x) | `<span>    </span>` | ⚠️ Converted to 4 regular spaces (collapse to 1) |
| 5 | Regular space in span | `<span> </span>` | ✓ Preserved |
| 6 | Multiple regular spaces | `<span> </span>` | ❌ Collapsed to 1 |
| 7 | Space BETWEEN tags | `</span> <span>` | ✓ Preserved |
| 8 | NO space between tags | `</span><span>` | ❌ Merged words! |
| 9 | `\t` (unicode tab) | `<span> </span>` | ❌ Lost → single space |
| 10 | `<pre>` tag with spaces | `<pre> 1 space` | ❌ Collapsed anyway |

**Key Findings:**

1. **ALL HTML entities → regular spaces:**
   - `&#9;`, `&#160;`, `&nbsp;` all become single space
   - Google Translate normalizes ALL whitespace entities

2. **Regular spaces inside spans preserved:**
   - `<span> </span>` → keeps space ✓
   - But multiple spaces collapse: `<span>    </span>` → `<span> </span>`

3. **Space BETWEEN tags is preserved:**
   - `<span>text1</span> <span>text2</span>` → keeps space ✓
   
4. **Adjacent tags WITHOUT space merge:**
   - `<span>text1</span><span>text2</span>` → "text1text2" ❌
   - **This is the ROOT CAUSE of "allergiesWhen" issue!**

5. **Even `<pre>` tag doesn't help**
   - Google Translate ignores HTML formatting hints

---

### HTML Entity Test Results

**To be filled in Phase 2:**

| Entity | Input | Output | Preserved? |
|--------|-------|--------|------------|
| `&#9;` | | | |
| `&#160;` | | | |
| `&nbsp;` | | | |
| ` ` (space) | | | |
| `  ` (2 spaces) | | | |

---

### Missing Space Analysis

**To be filled in Phase 3:**

*Examples found:*

*Original HTML structure:*

*Translated HTML structure:*

*Root cause:*

---

### Solution Tests

**To be filled in Phase 5:**

**Solution A: Multiple non-breaking spaces**
- Test: 
- Result:
- Pros/Cons:

**Solution B: Add explicit spaces**
- Test:
- Result:
- Pros/Cons:

**Solution C: Actual tab characters**
- Test:
- Result:
- Pros/Cons:

**Solution D: Space in separate span**
- Test:
- Result:
- Pros/Cons:

---

## Success Criteria

### Must Have
- [ ] Tabs visible in output (at least as spaces)
- [ ] No merged words (all sections separated)
- [ ] Document readable

### Nice to Have
- [ ] Tabs preserved as actual tabs
- [ ] Multiple spaces preserved
- [ ] Original spacing exactly preserved

---

## Timeline

- Phase 1: 30 min (research)
- Phase 2: 20 min (entity tests)
- Phase 3: 30 min (missing space investigation)
- Phase 4: 45 min (solution research)
- Phase 5: 60 min (solution testing)
- Phase 6: 30 min (implementation)
- Phase 7: 20 min (verification)
- **Total: ~4 hours**

---

## Status

**Current Phase:** Phase 1 - Research  
**Started:** 2026-02-15 20:00  
**Last Updated:** 2026-02-15 20:00
