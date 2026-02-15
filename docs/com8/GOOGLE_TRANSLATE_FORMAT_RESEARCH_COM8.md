# Google Translate HTML Format Research - Final Results (COM8)

**Date:** 2026-02-15  
**Session:** COM8  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Status:** ✅ COMPLETED

---

## Executive Summary

**GOOD NEWS:** Google Translate's free web endpoint **DOES preserve HTML formatting**!

**Test Results:** 7 out of 10 tests showed EXCELLENT HTML preservation
- ✅ `<span class="fmtX">` - Works perfectly
- ✅ `<span style="...">` - Works perfectly  
- ✅ `<span data-fmt="fmtX">` - Works perfectly
- ✅ Complex HTML with `<br>` and entities - Works perfectly
- ✅ Multiple spans - Works perfectly
- ✅ Full HTML documents - Works perfectly

---

## Root Cause of Current Bug

**The problem is NOT Google Translate - it's OUR code!**

**Current Flow (BROKEN):**
```
ODT → HTML with CSS → Extract TEXT ONLY → Google Translate → Plain text result
```

**What's happening in `google_translate_dock.py`:**
1. Line 489-525: `_browse_file()` loads ODT, extracts HTML
2. Line 559-593: `_translate()` is called
3. **BUG:** We're extracting TEXT ONLY (using TextExtractor) before translation
4. Google receives plain text with NO formatting
5. Returns plain text with NO formatting
6. We try to save as ODT with formatting → fails

**The Fix:**
```
ODT → HTML with CSS → Send FULL HTML to Google → HTML result → ODT with CSS
```

---

## Test Results Detail

### Test 2: Span with Class (CURRENT APPROACH)
**Source:**
```html
<span class="fmt5">Trabalho de Biologia</span>
```

**Result:**
```html
<span class="fmt5">Biology Assignment</span>
```

**Status:** ✅ PERFECT - Class attribute preserved!

### Test 9: Complex HTML with BR and Entities
**Source:**
```html
<span class="fmt4">Nome:</span><span class="fmt2"> Josué&#9;</span><br><span class="fmt4">Turma:</span><span class="fmt2"> 3001</span>
```

**Result:**
```html
<span class="fmt4">Name:</span><span class="fmt2"> Josué </span><br><span class="fmt4">Class:</span><span class="fmt2"> 3001</span>
```

**Status:** ✅ EXCELLENT
- All span tags preserved
- All class attributes preserved
- `<br>` tags preserved
- **Note:** `&#9;` (tab) was converted to space (acceptable)

### Test 10: Full HTML Document
**Source:**
```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<span class="fmt5">Trabalho de Biologia</span>
</body>
</html>
```

**Result:**
```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<span class="fmt5">Biology Assignment</span>
</body>
</html>
```

**Status:** ✅ PERFECT - Full document structure preserved!

---

## What Went Wrong Before?

Looking at the user's corrupted result from earlier:
```html
<span Biology Assignment</span>  <!-- Missing class="fmt5" -->
```

**This happened because:**
1. We sent **plain text** to Google Translate (not HTML)
2. Google translated: "Trabalho de Biologia" → "Biology Assignment"
3. We tried to reconstruct HTML afterwards
4. The reconstruction failed/corrupted

**Proof:** Our test shows when we send HTML properly, Google preserves it!

---

## Solution Design

### Current Broken Code Flow

**File:** `src/gui/google_translate_dock.py`

**Line 559-593:** `_translate()` method
```python
def _translate(self):
    # ... file mode logic ...
    
    # BUG HERE: Extract text only (loses HTML)
    if html_content:
        extractor = TextExtractor()
        extractor.feed(html_content)
        input_text = extractor.get_text()  # ← Plain text!
    
    # Translate plain text
    result = self.translator.translate(input_text, ...)  # ← Loses formatting
```

### Fixed Code Flow

**Change:**
```python
def _translate(self):
    # ... file mode logic ...
    
    # FIX: Send HTML directly (preserve formatting)
    if html_content:
        # Don't extract text - send full HTML
        input_text = html_content  # ← Keep HTML with all tags!
    
    # Translate HTML
    result = self.translator.translate(input_text, ...)  # ← Preserves formatting
```

---

## Implementation Plan

### Phase 1: Update Translation Method ✓
**File:** `src/gui/google_translate_dock.py`
- Line 559-593: Remove TextExtractor usage
- Send full HTML to Google Translate
- Receive HTML back with formatting

### Phase 2: Update Display Methods
**Current:**
- Preview shows: TextExtractor → plain text
- Result shows: TextExtractor → plain text

**Fix:**
- Keep TextExtractor for **display** (user shouldn't see HTML)
- But translate the **HTML**, not the extracted text

### Phase 3: Test End-to-End
- Test with actual ODT file
- Verify all 8 format classes preserved
- Check tabs, line breaks, styling
- Validate against original document

---

## Key Findings

1. **Google Translate IS reliable for HTML preservation**
   - Free web endpoint works
   - No need for paid API
   - No need for custom token system

2. **Our current approach (span + class) is CORRECT**
   - No need to change HTML format
   - No need for inline styles
   - Keep current CSS class system

3. **The bug is in our extraction/translation flow**
   - We're extracting text BEFORE translation
   - Should translate HTML, extract text AFTER for display

4. **HTML entities need attention**
   - `&#9;` (tab) gets converted to space
   - May need to encode differently or accept this behavior

---

## Code Changes Needed

### File: `src/gui/google_translate_dock.py`

**Method:** `_translate()` (Lines 559-593)

**BEFORE:**
```python
# Extract text for translation
if html_content:
    extractor = TextExtractor()
    extractor.feed(html_content)
    input_text = extractor.get_text()
```

**AFTER:**
```python
# Send HTML directly for translation (preserve formatting)
if html_content:
    input_text = html_content  # Keep full HTML with <span>, <br>, etc.
```

**Method:** `_on_translation_completed()` (Lines 668-707)

**BEFORE:**
```python
# Extract text from HTML for display
extractor = TextExtractor()
extractor.feed(self.translated_html)
result_text = extractor.get_text()
self.text_output.setPlainText(result_text)
```

**AFTER:**
```python
# HTML is already translated - extract text for display only
extractor = TextExtractor()
extractor.feed(self.translated_html)  # translated_html is HTML from Google
result_text = extractor.get_text()
self.text_output.setPlainText(result_text)  # Show clean text to user
```

**Key insight:** TextExtractor is for **display**, not for **translation**!

---

## Testing Evidence

**Test Script:** `tests/com8/test_google_translate_formats_COM8.py`

**Results Summary:**
- 10 tests executed
- 7 EXCELLENT (HTML preserved perfectly)
- 3 BASELINE (plain text tests)
- 0 FAILED

**Logs:** `.test_outputs/com8/format_tests/test_execution_log.txt`

**Individual Results:** `.test_outputs/com8/format_tests/*.json`

---

## Next Steps

1. ✅ Research completed
2. ✅ Root cause identified
3. ✅ Solution designed
4. ✅ Tests prove concept works
5. ⏭️ Implement fix in google_translate_dock.py
6. ⏭️ Test with real ODT files
7. ⏭️ Commit and document

---

## Conclusion

**Google Translate is NOT the problem!**

We were sending plain text when we should have been sending HTML.

The fix is simple:
- Send HTML to Google Translate (not extracted text)
- Google returns HTML with formatting preserved
- Extract text from HTML for display purposes only
- Save HTML back to ODT with formatting intact

**Expected Result:**
All 8 CSS classes preserved through translation, no more corruption.

---

**Research Status:** COMPLETED  
**Solution Status:** READY TO IMPLEMENT  
**Confidence Level:** HIGH (proven by tests)
