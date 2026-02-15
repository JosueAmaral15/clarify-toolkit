# Action Plan: Test Google Translate HTML Format Compatibility (COM8)

**Session:** COM8  
**Date:** 2026-02-15  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Branch:** COM8-documentation-reading  
**Programmer:** COM8

---

## Problem Statement

Google Translate API is **corrupting our HTML structure** during translation:

**Issues Found:**
1. `<span class="fmt5">Trabalho de Biologia</span>` → `<span Biology Assignment</span>` (class removed!)
2. Text being placed outside span tags (losing formatting)
3. Class attributes randomly stripped from tags
4. Result: ODT formatting is lost after translation

**Evidence:**
- Sent: `<span class="fmt5">Trabalho de Biologia</span>`
- Received: `<span Biology Assignment</span>` 
- Missing: `class="fmt5"` attribute

---

## Research Questions

1. **What HTML formats does Google Translate preserve?**
   - Plain text with `<br>` tags?
   - Specific HTML tags (div, p, span, b, i)?
   - HTML with inline styles vs classes?
   - HTML entities (&#9;, &nbsp;)?

2. **What is Google's recommended format?**
   - Official documentation
   - Best practices from developers
   - Known limitations

3. **Alternative approaches:**
   - Placeholder/token system (e.g., `{FMT1}text{/FMT1}`)
   - Inline styles instead of classes
   - Different tag types
   - Post-processing to restore structure

---

## Action Plan Steps

### Phase 1: Research Online (30 min)
- [x] Search: "google translate api html format preservation"
- [x] Search: "google translate api keep html tags"
- [x] Look for official Google Cloud Translation API docs
- [x] Document findings in GOOGLE_TRANSLATE_FORMAT_RESEARCH_COM8.md
- [x] Found: Google supports text/html format
- [x] Found: "to the extent possible" disclaimer

### Phase 2: Design Test Formats (20 min)
Based on research, create 6-8 test HTML formats:

**Test 1: Current format (baseline - we know this fails)**
```html
<span class="fmt1">Bold text</span>
```

**Test 2: Inline styles instead of classes**
```html
<span style="font-weight: bold; font-size: 14pt;">Bold text</span>
```

**Test 3: Different tags (b, i, strong, em)**
```html
<b>Bold text</b> <i>Italic text</i>
```

**Test 4: DIV with classes**
```html
<div class="fmt1">Bold text</div>
```

**Test 5: Data attributes**
```html
<span data-fmt="fmt1">Bold text</span>
```

**Test 6: HTML comments as markers**
```html
<!--FMT1-->Bold text<!--/FMT1-->
```

**Test 7: Placeholder tokens**
```html
{FMT1}Bold text{/FMT1}
```

**Test 8: Mix of semantic tags + classes**
```html
<b class="fmt1">Bold text</b>
```

### Phase 3: Create Test Script (30 min)
- [ ] Create `tests/com8/test_google_translate_formats_COM8.py`
- [ ] Generate 8 test HTML snippets (one for each format)
- [ ] Each test has:
  - Source text (Portuguese): "Trabalho de Biologia" (bold, 16pt)
  - Expected format marker to preserve
  - Comparison function
- [ ] Save test HTMLs to `.test_outputs/com8/format_tests/`

### Phase 4: Manual Testing with Google Translate (60 min)
Since we need to test with actual Google Translate API:

**Option A: Use actual API (if configured)**
- [ ] Check if Google Translate API is configured in Clarify
- [ ] Run automated tests through API
- [ ] Capture results

**Option B: Manual web testing**
- [ ] Use Google Translate web interface
- [ ] Test each format manually
- [ ] Document which formats survive translation
- [ ] Take screenshots/copy results

**Option C: Simulate based on known behavior**
- [ ] Document expected behavior based on research
- [ ] Create validation tests for our chosen format

### Phase 5: Analyze Results (20 min)
For each format test:
- [ ] Did format markers survive? ✓/✗
- [ ] Was translation accurate? ✓/✗
- [ ] Were HTML entities preserved? ✓/✗
- [ ] Overall viability: High/Medium/Low

### Phase 6: Document Findings (20 min)
- [ ] Create comparison table
- [ ] Rank formats by preservation quality
- [ ] Document recommended approach
- [ ] Note any gotchas or limitations

### Phase 7: Implement Solution (variable)
Based on findings:
- [ ] Choose best format
- [ ] Modify `HTMLFormatMapper` to use new format
- [ ] Update extraction and creation methods
- [ ] Add format conversion layer if needed

### Phase 8: Test End-to-End (20 min)
- [ ] Test with actual ODT file
- [ ] Verify formatting preserved through full workflow
- [ ] Check all 8 format classes work
- [ ] Commit changes

---

## Research Notes

### Online Research Findings

*To be filled during Phase 1*

**Google Cloud Translation API Documentation:**
- 

**Known Issues from Community:**
- 

**Best Practices:**
- 

**Similar Projects/Solutions:**
- 

---

## Test Format Comparison Table

*To be filled during Phase 5*

| Format | Markers Preserved | Translation OK | Entities OK | Viability |
|--------|-------------------|----------------|-------------|-----------|
| 1. class= | ✗ | ✓ | ✓ | LOW |
| 2. inline style= | ? | ? | ? | ? |
| 3. semantic tags | ? | ? | ? | ? |
| 4. div class= | ? | ? | ? | ? |
| 5. data-* | ? | ? | ? | ? |
| 6. comments | ? | ? | ? | ? |
| 7. tokens | ? | ? | ? | ? |
| 8. tags+classes | ? | ? | ? | ? |

---

## Expected Challenges

1. **Translation accuracy with markers:**
   - HTML comments might confuse translation
   - Tokens might get translated as text
   - Need balance between preservation and accuracy

2. **Post-processing complexity:**
   - If markers get modified, need repair logic
   - Must map translated text back to original format
   - Edge cases with split/merged segments

3. **API limitations:**
   - May not have control over API behavior
   - Different APIs (Web vs Cloud) may behave differently
   - Rate limits for testing

---

## Success Criteria

1. **Find a format where:**
   - Format markers survive translation 100%
   - Translation accuracy maintained
   - HTML entities preserved
   - Easy to implement

2. **Validation:**
   - Full ODT → Translate → ODT workflow
   - All 8 format classes preserved
   - No visual differences in output

3. **Documentation:**
   - Clear explanation of chosen format
   - Rationale for decision
   - Implementation details

---

## Files to Create

1. **tests/com8/test_google_translate_formats_COM8.py**
   - Test script for format comparison

2. **.test_outputs/com8/format_tests/** directory
   - Test HTML files (8 formats)
   - Results from translation tests
   - Comparison reports

3. **docs/com8/GOOGLE_TRANSLATE_FORMAT_RESEARCH_COM8.md**
   - Detailed research findings
   - Format test results
   - Recommendations

---

## Timeline Estimate

- Phase 1 (Research): 30 min
- Phase 2 (Design): 20 min
- Phase 3 (Script): 30 min
- Phase 4 (Testing): 60 min
- Phase 5 (Analysis): 20 min
- Phase 6 (Document): 20 min
- Phase 7 (Implement): 60-120 min
- Phase 8 (Test): 20 min

**Total: 4-5 hours**

---

## Notes

- This is an investigation task, not just a fix
- May discover Google Translate simply doesn't support our use case
- Backup plan: Use different translation service or method
- Document everything for future reference

---

**Status:** Ready to start Phase 1 (Research)  
**Next Step:** Online research about Google Translate HTML format handling
