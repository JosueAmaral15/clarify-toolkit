# ACTION PLAN: Debug Visible Format Tags Bug - COM8

**Date**: 2026-02-08
**Session**: 76
**Programmer**: COM8
**Protocol**: SIMPLICITY_PROTOCOL_3

---

## 🎯 OBJECTIVE

Fix critical bug: Visible format tags in translated ODT output
Location: Paragraph 10, sub-section 3
Example: `Increase in toxic substances</113|65536><112|65536:525252,9,Arial|0,0>There are...`

---

## 📋 PROTOCOL PHASE: Investigation → Implementation

Following SIMPLICITY_PROTOCOL_3:
1. ✅ Read documentation (completed in previous sessions)
2. ✅ Study code (completed in previous sessions)
3. 🔄 **Fix bugs** (current phase)
4. ⏳ Test implementation (next)
5. ⏳ Document (next)

---

## 🔍 INVESTIGATION PLAN

### Phase 1: Understand the Bug Context
- [x] Read investigation results from last session
- [ ] Extract exact location details
- [ ] Identify what paragraph 10 contains
- [ ] Note characteristics:
  - Very long paragraph?
  - Complex nested formatting?
  - Multiple numbered sub-sections?

### Phase 2: Examine Current Placeholder System
- [ ] Review format tag placeholder protection (format_mapper.py:34-165)
- [ ] Review 4-pass restoration system (format_mapper.py:68-165)
- [ ] Check if orphan tag cleanup is working
- [ ] Identify where tags are becoming visible

### Phase 3: Trace Data Flow
- [ ] Extract paragraph 10 from ORIGINAL file
- [ ] See how it's formatted (XML structure)
- [ ] Run through extraction → segmentation → translation → restoration
- [ ] Find WHERE tags become visible (which step?)

### Phase 4: Reproduce Bug in Isolation
- [ ] Create minimal test case with paragraph 10
- [ ] Run translation on JUST that paragraph
- [ ] Verify bug reproduces
- [ ] Examine output XML structure

### Phase 5: Debug Root Cause
Possible causes to investigate:
- [ ] Segment parsing issue (`parse_tagged_text()`)
- [ ] Orphan tag not detected (restoration phase)
- [ ] Tag wrapping issue during ODT creation
- [ ] Placeholder not properly applied to all tags
- [ ] Restoration order issue (whitespace vs tags)
- [ ] Very long text breaks segmentation logic
- [ ] Numbered sub-sections confuse parser

### Phase 6: Analyze Similar Cases
- [ ] Check if other paragraphs have similar structure
- [ ] See if they also have visible tags (or just paragraph 10)
- [ ] Identify what makes paragraph 10 unique

---

## 🛠️ IMPLEMENTATION PLAN (After Investigation)

Will create detailed fix plan after root cause is identified.

Likely areas for fix:
- `format_mapper.py:1366-1700` - `parse_tagged_text()`
- `format_mapper.py:68-165` - Tag restoration (4-pass)
- `format_mapper.py:2740-2855` - ODT creation text processing

---

## ✅ SUCCESS CRITERIA

Investigation:
- [ ] Root cause identified with evidence
- [ ] Reproducible minimal test case created
- [ ] Exact location in code found

Fix:
- [ ] No visible tags in paragraph 10
- [ ] No visible tags ANYWHERE in document
- [ ] All other features still work (100% tabs, 86% line breaks)
- [ ] Translation quality unchanged
- [ ] User file test passes completely

---

## 📁 FILES TO INVESTIGATE

Primary:
- `src/translation/format_mapper.py` (core logic)
- `CAIT- Trabalho de Biologia - Josué 3001.odt` (original)
- `CAIT_FINAL_VERIFIED_COM8.odt` (output with bug)

Supporting:
- `docs/com8/INVESTIGATION_RESULTS_COM8.md` (bug report)
- `src/gui/google_translate_dock.py` (translation workflow)

---

## 📊 PROGRESS TRACKING

- [ ] Phase 1: Context (0/4)
- [ ] Phase 2: Placeholder system (0/4)
- [ ] Phase 3: Trace flow (0/4)
- [ ] Phase 4: Reproduce (0/4)
- [ ] Phase 5: Debug cause (0/7)
- [ ] Phase 6: Similar cases (0/3)

**Total**: 0/26 steps completed

---

## 🎯 NEXT STEPS

1. Start Phase 1: Understand bug context
2. Extract paragraph 10 from original file
3. Examine its XML structure
4. Trace through processing pipeline

---

**Status**: Ready to investigate
**Estimated time**: 1-2 hours for thorough investigation
