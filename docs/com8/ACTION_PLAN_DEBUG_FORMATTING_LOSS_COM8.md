# ACTION PLAN: Debug ODT Formatting Loss Issue

**Programmer**: COM8  
**Date**: 2026-02-09  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: ODT file created without formatting/styles

---

## PROBLEM STATEMENT

User reports translated ODT file has NO formatting:
- File: `/home/josue/Documents/translation_20260209_151539.odt`
- Executed from: `clarify-COM8/clarify.sh` (correct worktree)
- Automatic Styles: 0 (should be 8)
- Styles: 0 (should have some)
- Paragraphs: 1 (should be ~40+)
- All text in single paragraph with no formatting

---

## INVESTIGATION PLAN

### Phase 1: Verify Code Path
1. Check if GUI is actually using new HTML system
2. Verify `_css_manager` is being set during load
3. Check if `_translated_html` is being stored
4. Verify save path is calling `create_odt_from_html()`

### Phase 2: Add Debug Logging
1. Add print statements to track execution
2. Log when ODT is loaded (HTML extraction)
3. Log when translation completes (HTML storage)
4. Log when save is triggered (ODT creation)

### Phase 3: Test Each Component
1. Test HTML extraction in isolation
2. Test translation worker with HTML
3. Test ODT creation from HTML
4. Identify where format is lost

### Phase 4: Fix Root Cause
1. Fix identified issue
2. Test with real file
3. Verify formatting preserved
4. Document fix

---

## STATUS: Starting Phase 1 - Code Path Verification
