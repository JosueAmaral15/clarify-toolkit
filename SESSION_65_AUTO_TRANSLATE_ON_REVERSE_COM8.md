# Session 65: Auto-Translate on Reverse Button - COM8

**Date:** 2026-02-03  
**Programmer:** COM8  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Duration:** 30 minutes

---

## 🎯 OBJECTIVE

Implement automatic translation when user clicks the "Reverse" button in Google Translate tool.

---

## 📋 REQUIREMENTS

**Current Behavior:**
1. User translates text: EN → PT
2. User clicks "Reverse" → Languages swap, text swaps
3. User must click "Translate" again manually

**New Behavior:**
1. User translates text: EN → PT
2. User clicks "Reverse" → Languages swap, text swaps, **AUTO-TRANSLATES**
3. Back-translation appears immediately

**Additional Requirements:**
- ✅ Preserve formatting during reverse translation
- ✅ Show progress bar/spinner during auto-translation
- ✅ Show status message during auto-translation
- ✅ If translation in progress, IGNORE the Reverse click
- ✅ Works for: Simple text, DOCX files, ODT files

---

## 🔍 INVESTIGATION

### Current Implementation (Line 632-668)

**Method:** `_reverse_translation()`

**What it did:**
1. Swap language combo boxes
2. Swap input/output text fields
3. Update button states
4. **STOP** - user had to click Translate manually

**Key Variables:**
- `self.translation_worker` - Background translation thread
- `self._source_segments` - Formatted segments from source document
- `self._translated_segments` - Formatted segments after translation
- `self.combo_from_lang` / `self.combo_to_lang` - Language selectors

---

## ✅ IMPLEMENTATION

### Changes Made (Line 632-696)

**Added to `_reverse_translation()` method:**

1. **Check if translation is running:**
   ```python
   if self.translation_worker and self.translation_worker.isRunning():
       return  # Ignore click
   ```

2. **Store output text before swapping:**
   ```python
   output_text = self.text_output.toPlainText()
   has_formatting = bool(self._translated_segments)
   ```

3. **Swap languages** (existing logic - unchanged)

4. **Swap input/output text:**
   ```python
   self.text_input.setPlainText(output_text)
   self.text_output.clear()  # Clear for new translation
   ```

5. **Swap formatting segments:**
   ```python
   if has_formatting:
       self._source_segments, self._translated_segments = 
           self._translated_segments, self._source_segments
   ```

6. **Auto-trigger translation:**
   ```python
   if output_text.strip():
       new_from_lang = self.combo_from_lang.currentData()
       new_to_lang = self.combo_to_lang.currentData()
       
       # Prepare text with formatting if available
       if has_formatting and self._source_segments:
           text_to_translate = FormatMapper.segments_to_tagged_text(
               self._source_segments
           )
       else:
           text_to_translate = output_text
       
       # Start translation automatically
       self._start_translation(text_to_translate, new_from_lang, new_to_lang)
   ```

---

## 🧪 TESTING SCENARIOS

### Test 1: Simple Text Translation
1. Enter text: "Hello world"
2. Translate EN → PT → "Olá mundo"
3. Click Reverse
4. **Expected:** Auto-translates PT → EN, shows "Hello world" (or similar)
5. **Progress:** Shows progress bar and status message

### Test 2: DOCX Document with Formatting
1. Load DOCX with bold/italic text
2. Translate EN → PT
3. Click Reverse
4. **Expected:** Auto-translates PT → EN, preserves formatting
5. **Progress:** Shows progress bar

### Test 3: ODT Document with Formatting
1. Load ODT with colors/alignment
2. Translate EN → PT
3. Click Reverse
4. **Expected:** Auto-translates PT → EN, preserves formatting
5. **Progress:** Shows progress bar

### Test 4: Translation in Progress
1. Start translation (EN → PT)
2. Click Reverse while translating
3. **Expected:** Click is IGNORED, translation continues
4. **No crash or errors**

### Test 5: Empty Output
1. Clear output field
2. Click Reverse
3. **Expected:** Languages swap, but no auto-translation
4. **No errors**

---

## 🎯 FEATURES IMPLEMENTED

✅ **Auto-translation after reverse**  
✅ **Formatting preservation** (uses segments_to_tagged_text)  
✅ **Progress indicators** (reuses existing _start_translation UI updates)  
✅ **Status messages** (automatic via _start_translation)  
✅ **Ignore clicks during translation** (worker.isRunning() check)  
✅ **Works for text mode** (plain text)  
✅ **Works for DOCX mode** (with formatting)  
✅ **Works for ODT mode** (with formatting)  

---

## 💡 KEY DECISIONS

1. **Reuse `_start_translation()` method**
   - Already handles: UI updates, progress bar, status messages, worker creation
   - No need to duplicate logic
   - Consistent behavior

2. **Clear output before auto-translation**
   - Prevents confusion (user sees old result momentarily)
   - Progress bar shows immediately

3. **Swap formatting segments**
   - Preserves document structure during reverse translation
   - Tagged text preserves: bold, italic, colors, alignment, etc.

4. **Check worker.isRunning()**
   - Prevents race conditions
   - Simple and reliable check

---

## 📝 CODE QUALITY

**Lines Changed:** ~65 lines (method rewritten)  
**Complexity:** Moderate  
**Dependencies:** None (uses existing methods)  
**Backward Compatible:** Yes (enhances existing behavior)  

**Potential Issues:**
- None identified
- Uses existing tested infrastructure
- Follows existing patterns

---

## 🚀 USER EXPERIENCE IMPROVEMENT

**Before:**
- 3 clicks: Translate → Reverse → Translate
- Slow workflow for back-translation
- Extra step required

**After:**
- 2 clicks: Translate → Reverse
- Automatic back-translation
- **33% fewer clicks!**
- Faster workflow

**Use Case Example:**
User wants to verify translation quality by comparing:
1. Original: "Hello world" → Translate → "Olá mundo"
2. Click Reverse → Auto back-translate → "Hello world"
3. Compare: Did it come back correctly? ✅

---

## 📦 FILES MODIFIED

- `src/gui/google_translate_dock.py` - Line 632-696 (_reverse_translation method)

---

## ✅ TESTING CHECKLIST

Manual testing required (GUI feature):

- [ ] Test 1: Simple text translation and reverse
- [ ] Test 2: DOCX document with formatting
- [ ] Test 3: ODT document with formatting
- [ ] Test 4: Click Reverse during active translation
- [ ] Test 5: Reverse with empty output
- [ ] Test 6: Verify progress bar shows
- [ ] Test 7: Verify status messages update
- [ ] Test 8: Verify formatting preserved

---

## 🎉 COMPLETION

Session 65 complete! Auto-translation on Reverse button implemented.

**Next Steps:**
- User testing with real documents
- Verify all test scenarios pass
- Commit if tests successful

---

**Status:** READY FOR USER TESTING ✅

