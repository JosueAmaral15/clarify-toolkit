# Action Plan: Fix ODT Translation Format Restoration Bug - COM8

**Date:** 2026-02-06  
**Programmer:** COM8  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Phase:** Critical Bug Investigation & Fix

---

## 🎯 OBJECTIVE

Fix the critical bug where `create_odt_from_segments()` fails to restore formatting from tagged text, causing tags to appear as literal text in the output ODT file.

---

## 🐛 BUG DISCOVERED

### Symptoms:
1. ❌ Tags like `<113|N:X>` appear as literal text `&lt;113|` in output
2. ❌ Output file size dramatically reduced (40.8 KB → 4.5 KB = 10.9%)
3. ❌ Content lost (17 → 14 paragraphs, 31 → 24 spans)
4. ❌ Formatting not restored (tags should become `<text:span>` elements)

### Evidence:
```
Original:   formatted text with bold, italic, etc.
Translated: &lt;113 | technology. The most immediate consequence...
Expected:   <text:span text:style-name="Bold">technology</text:span>
```

### Impact: **CRITICAL**
- ODT → ODT translation completely broken
- Format preservation Sessions 64-72 work not functional for ODT output
- Users cannot use this feature in production

---

## 🔍 INVESTIGATION PLAN

### Phase 1: Code Analysis ⏳

**Step 1.1: Examine `create_odt_from_segments()` function**
- [ ] Read complete function code
- [ ] Identify where tags should be parsed
- [ ] Check if `parse_tagged_text()` is called before this function
- [ ] Verify segment structure expectations

**Questions:**
- Does the function expect segments or tagged text?
- Is there a parsing step missing?
- Is the workflow correct?

**Step 1.2: Check caller code (google_translate_dock.py)**
- [ ] Review how `create_odt_from_segments()` is called
- [ ] Check if tagged text is passed directly (wrong) vs segments (right)
- [ ] Verify the complete workflow chain

**Step 1.3: Test with simple example**
- [ ] Create minimal tagged text: `<113|1:B>Bold</113|1>`
- [ ] Parse to segments
- [ ] Create ODT from segments
- [ ] Verify if simple case works

### Phase 2: Root Cause Identification ⏳

**Hypothesis 1: Wrong input type**
- Function receives tagged text string instead of parsed segments
- Tags are treated as literal text, not formatting instructions

**Hypothesis 2: Parsing not happening**
- `parse_tagged_text()` not called in workflow
- Segments contain raw tagged text in `.text` field

**Hypothesis 3: Bug in `create_odt_from_segments()`**
- Function expects different segment format
- Tag parsing logic broken or missing

**Verification Steps:**
- [ ] Check what `test_odt_translation_cli.py` actually passed
- [ ] Print segment contents before ODT creation
- [ ] Compare with working DOCX workflow

---

## 🛠️ FIX STRATEGY

### Approach: Diagnose First, Then Fix

**Will NOT fix blindly** - must understand root cause completely.

### Expected Workflow (Correct):
```
1. Extract: ODT file → Tagged text string
2. Translate: Tagged text → Translated tagged text
3. Parse: Tagged text → List[TextSegment] (tags become format_bits)
4. Create: List[TextSegment] → ODT file (format_bits → XML elements)
```

### Actual Workflow (Current - Suspected Bug):
```
1. Extract: ODT file → Tagged text ✅
2. Translate: Tagged text → Translated tagged text ✅
3. Parse: Tagged text → ??? (step missing or broken?)
4. Create: ??? → ODT file ❌ (tags as literal text)
```

---

## 📊 EXECUTION STEPS

### Phase 1: Investigation 📍 CURRENT

#### Step 1: Examine create_odt_from_segments() code
- [ ] View complete function
- [ ] Identify tag handling logic
- [ ] Check segment processing
- [ ] Find where tags should convert to XML

#### Step 2: Examine parse_tagged_text() code
- [ ] View function implementation
- [ ] Check tag regex patterns
- [ ] Verify segment creation
- [ ] Test parsing with sample tagged text

#### Step 3: Trace actual workflow in test
- [ ] Review test_odt_translation_cli.py flow
- [ ] Add debug prints to see actual data
- [ ] Run with simple test case
- [ ] Capture intermediate values

#### Step 4: Compare with working DOCX workflow
- [ ] Check if DOCX has same structure
- [ ] Identify differences
- [ ] Find working reference code

### Phase 2: Simple Test Case Creation ⏳

Create minimal reproducible test:
- [ ] Input: Simple tagged text with one bold tag
- [ ] Parse to segments
- [ ] Create ODT
- [ ] Verify output
- [ ] Document results

### Phase 3: Root Cause Identification ⏳

Based on investigation:
- [ ] Confirm exact bug location
- [ ] Document why it fails
- [ ] Identify missing/broken code
- [ ] Plan precise fix

### Phase 4: Implementation (After Root Cause Found) ⏳

**Will only proceed after complete understanding**

Possible fixes:
- Option A: Ensure `parse_tagged_text()` called before `create_odt_from_segments()`
- Option B: Fix bug in `create_odt_from_segments()` tag handling
- Option C: Fix bug in `parse_tagged_text()` segment creation
- Option D: Correct workflow in caller code

### Phase 5: Testing ⏳

- [ ] Test with simple case
- [ ] Test with complex case (original biology document)
- [ ] Verify tag preservation 100%
- [ ] Verify file size reasonable
- [ ] Verify formatting in LibreOffice
- [ ] Run Session 72 automated tests

### Phase 6: Documentation ⏳

- [ ] Update this action plan with findings
- [ ] Document the bug and fix
- [ ] Create test report
- [ ] Update CHANGELOG

---

## 🔗 RELATED FILES

**Primary Investigation Targets:**
- `src/translation/format_mapper.py` (~2700 lines)
  - Line ~2248: `create_odt_from_segments()` function
  - Line ~1366: `parse_tagged_text()` function
  - Line ~1387: Tag normalization logic (Session 70)

**Caller Code:**
- `src/gui/google_translate_dock.py` (~830 lines)
  - Line ~470-478: ODT extraction and translation workflow
  - Need to check where segments are created and passed

**Test Code:**
- `test_odt_translation_cli.py` (just created)
  - Line 75: Parse tagged text
  - Line 140: Create ODT from segments
  - Workflow may have bug in this test itself

---

## ⚠️ CRITICAL QUESTIONS TO ANSWER

1. **What does `create_odt_from_segments()` actually expect?**
   - Segments with `text` field containing plain text?
   - Segments with `format_bits` set from parsed tags?
   - Or does it expect to parse tags itself?

2. **What does `parse_tagged_text()` actually return?**
   - TextSegment objects with parsed formatting?
   - Or segments with tagged text still in `.text` field?

3. **Is the test code workflow correct?**
   - Does it match how google_translate_dock.py does it?
   - Are we missing a step?

4. **Why did Session 72 tests pass if this is broken?**
   - Do those tests only test parsing, not ODT creation?
   - Or is there a different code path?

---

## ✅ COMPLETION CRITERIA

**Investigation Complete When:**
- [ ] Root cause identified with certainty
- [ ] Bug location pinpointed (file, function, line)
- [ ] Understand why it fails
- [ ] Know exact fix needed

**Fix Complete When:**
- [ ] Code changes implemented
- [ ] Simple test case passes
- [ ] Complex test case (biology doc) passes
- [ ] Tags preserve 100% (or document known limitations)
- [ ] File size reasonable
- [ ] No tag artifacts in output

**Testing Complete When:**
- [ ] Original biology document translates correctly
- [ ] Output opens in LibreOffice with formatting
- [ ] Session 72 tests still pass
- [ ] No regressions

**Documentation Complete When:**
- [ ] Action plan updated with findings
- [ ] Bug and fix documented
- [ ] Test report created
- [ ] Code comments added if needed

---

## 📝 INVESTIGATION RESULTS

### Investigation Completed: 2026-02-06

**Root Cause:** Google Translate API breaks/corrupts format tags during translation

**Bug Location:** External (Google Translate) + insufficient error recovery in `parse_tagged_text()`

**Why It Fails:**
1. Google Translate sometimes modifies tags during translation:
   - Adds spaces: `<113|65536:meta>` → `<113 | 65536 : meta>`
   - **Removes closing tags completely**: `</113|65536>` disappears
   - Splits/merges sentences differently
   
2. Example from actual translation:
   ```
   ORIGINAL:
   <113|65536:525252,9,Arial|0,0>RISCOS PARA A AGRICULTURA: </113|65536><112|65536:...>
   
   TRANSLATED (BROKEN):
   <113 | technology. The most immediate consequence...
   ```
   - Closing tag `</113|65536>` is MISSING
   - Opening tag for next segment is MISSING
   - Text becomes orphaned with unclosed tag

3. `parse_tagged_text()` has some recovery:
   - Line 1387-1405: Normalizes spaces in tags ✅
   - Line 1432: Regex pattern requires closing tags
   - Line 1475-1479: Treats unclosed tags as plain text ✅ (working as designed)
   - **BUT**: Unclosed tags appear as literal text `<113 |` in output

**Segments Affected:** 2 out of 33 (6%)

**Tag Artifacts Found:**
- Segment 14: `\n\n<113 | technology. The most immediate...`
- Segment 17: `\n\n<113 |\n\n`

**File Size Impact:**
- These orphaned text segments have no formatting applied
- Content is preserved but not in correct format
- Some content may be concatenated incorrectly

---

**Status:** Phase 1 - Investigation starting  
**Protocol Compliance:** ✅ Action plan created FIRST before any fixes  
**Next Step:** Examine `create_odt_from_segments()` and `parse_tagged_text()` code

---

**Created:** 2026-02-06  
**By:** COM8  
**Branch:** COM8-documentation-reading


## 💡 FIX STRATEGY

### Problem Summary
Google Translate API corrupts tags in ~6% of cases, causing orphaned text.

### RECOMMENDED SOLUTION: Enhanced Tag Cleanup

**Approach:** Add artifact removal in parse_tagged_text() for plain text segments

**Implementation:**
- Location: src/translation/format_mapper.py line ~1475-1479  
- Strip broken tag patterns: `<\d+ |`, `< \d+`, `<\d+:`
- Log warnings for debugging
- Graceful degradation (formatting lost, content preserved)

**Pros:** Simple, handles Google unpredictability, minimal changes
**Cons:** Some formatting lost when tags break (unavoidable with Google Translate)

---

**Status:** Root cause identified - Ready for implementation  
**Next:** Implement Option A tag cleanup

