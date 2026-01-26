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


## Session 1 Results

✅ **Root Cause Found**: Duplicate Qt event (same as translation worker bug)  
✅ **Fix Applied**: Guard flag `_reversing` with 300ms debounce  
✅ **User Confirmed**: Text swap working correctly ✓  
✅ **New Issue Found**: Auto-detect swap logic needs improvement

### Auto-detect Swap Problem

**Current behavior**: 
- From: "Auto-detect" → To: "Português (PT)"
- When user clicks Reverse, nothing swaps (code skips swap when from_code == "auto")

**User requirement**:
After translation completes with auto-detect, the system KNOWS the detected language (e.g., "English"). This detected language should be used for reverse swap, not the "auto" code.

**Questions Before Implementing**:

1. **Where is detected language stored?**
   - Does TranslationResult contain detected language?
   - Is it stored in `_on_translation_completed()` result?
   - Should we add instance variable like `self._last_detected_lang`?

2. **Swap logic when From="Auto-detect":**
   - Scenario: From=Auto(detected EN) → To=PT, translate "hello" → "olá"
   - After Reverse: From=PT, To=EN, Input="olá"
   - Is this correct behavior?

3. **What if no translation done yet?**
   - User sets From=Auto-detect, To=PT
   - User clicks Reverse WITHOUT translating first
   - Should: (A) Do nothing? (B) Show warning? (C) Keep auto-detect and just swap text?

4. **Edge case: Multiple translations**
   - User translates "hello" (EN detected)
   - User manually changes input to "bonjour" (FR)
   - User clicks Reverse without translating again
   - Should use: (A) Last detected language (EN)? (B) Detect new language first?

Please answer these 4 questions before I implement.


## Question Answers Received

Q2: ✅ After reverse with auto-detect: From=PT, To=EN (detected), Input=swapped  
Q3: ✅ If reverse before translate: Keep auto-detect, just swap text  
Q4: ✅ If text changed without new translate: Keep auto-detect, just swap text  

## Investigation Results

✅ Found: `TranslationResult.source_language` contains detected language (from Google API)  
✅ Found: Google Translate returns detected language in `result[2]` (google_translate.py:164)  
❌ Problem: TranslationWorker signal doesn't pass source_language to dock!  
   - Line 57: Signal only has (str, bool, str) = (result, success, error)  
   - Line 129: source_language is lost when emitting signal

## Implementation Plan - Session 2

**Goal**: Pass detected language from worker to dock, use it for reverse swap

**Steps**:
1. Modify TranslationWorker signal to include source_language
2. Update signal emission in run() method
3. Update _on_translation_completed() signature to receive source_language
4. Store detected language in instance variable (self._last_detected_lang)
5. Update _reverse_translation() to use detected language when from_code=="auto"
6. Remove debug prints
7. Test and commit

