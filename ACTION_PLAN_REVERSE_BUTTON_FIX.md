# Action Plan: Fix Reverse Button Issues

**Programmer**: COM8  
**Date**: 2026-01-26  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5  
**Issue**: Reverse button not swapping languages and text correctly

## Problem Statement

The "Reverse Translation" button has TWO separate issues:
1. Languages (From/To dropdowns) are NOT swapping
2. Text (Input/Output) are NOT swapping

Current behavior: When clicking Reverse button, nothing happens.

## Root Cause Analysis Needed

Before fixing, need to investigate WHY the current code doesn't work:
- Lines 539-545: Language swap logic using `currentData()` and `findData()`
- Lines 548-552: Text swap logic using `toPlainText()` and `setPlainText()`

**Hypothesis**: Code logic looks correct, but maybe:
- Signal connections are interfering?
- ComboBox data not set correctly?
- Text widgets have issues?

## Action Plan: One Issue Per Session

### Session 1: Debug Language Swap (THIS SESSION)
**Goal**: Understand WHY languages don't swap

**Steps**:
1. Add debug prints to `_reverse_translation()` method:
   - Print `from_code` and `to_code` values
   - Print `from_index` and `to_index` values
   - Print current combo box states before/after
2. Test and analyze output
3. Identify root cause
4. Fix the language swap issue ONLY
5. Remove debug prints
6. Commit fix
7. User tests

**Exit criteria**: Languages swap correctly when clicking Reverse

---

### Session 2: Debug Text Swap (NEXT SESSION)
**Goal**: Understand WHY text doesn't swap

**Steps**:
1. Add debug prints for text swap logic
2. Test and identify root cause
3. Fix text swap issue ONLY
4. Remove debug prints
5. Commit fix
6. User tests

**Exit criteria**: Text swaps correctly when clicking Reverse

---

## Protocol Compliance

✅ One issue per session  
✅ Debug systematically with prints  
✅ Remove debug prints after fix  
✅ User tests before moving to next issue  
✅ Document findings in commits

## Current Status

- [ ] Session 1: Language swap (IN PROGRESS)
- [ ] Session 2: Text swap (PENDING)

