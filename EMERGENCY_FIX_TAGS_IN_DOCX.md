# Emergency Fix: Tags Appearing in DOCX Output

**Programmer:** COM8  
**Date:** January 30, 2026  
**Priority:** CRITICAL  
**Protocol:** SIMPLICITY_PROTOCOL_3

---

## Problem Statement

**Tags are appearing as literal text in saved DOCX files!**

User opens saved DOCX and sees:
```
Hello <1>world</1>!
```

Instead of:
```
Hello world!  (with 'world' formatted as bold)
```

---

## Root Cause

Testing shows `FormatMapper.create_docx_from_segments()` works correctly:
- ✅ Parses tags correctly
- ✅ Applies formatting correctly  
- ✅ Writes DOCX without tags when given proper segments

**The bug is:** Segments are being created with tags still in `.text` field!

Example of WRONG segment:
```python
TextSegment(text="<1>world</1>", format_bits=1)  # ❌ Tag in text!
```

Correct segment:
```python
TextSegment(text="world", format_bits=1)  # ✅ No tags in text
```

---

## Investigation Needed

Check these locations:

1. **Where segments are created from translation result**
   - `_on_translation_completed()` line ~551
   - Calls `FormatMapper.parse_tagged_text(result)`
   - Need to verify `result` has tags and segments extract them

2. **Where segments are stored from file loading**
   - `_browse_file()` line ~406
   - Calls `FormatMapper.parse_tagged_text(formatted_text_with_tags)`
   - Need to verify parsing works

3. **parse_tagged_text() implementation**
   - Should extract text WITHOUT tags
   - Pattern: `r'<(\d+)(?::([^>]+))?>(.*?)</\1>'`
   - Group 3 should be text without tags

---

## The Fix (1 Session)

### Session 7: Fix Tags in DOCX Output

**Objective:** Remove tags from segment text fields

**Steps:**

1. **Add debug logging** to see what's in segments:
   ```python
   print(f"DEBUG: segment.text = '{segment.text}'")
   print(f"DEBUG: segment.format_bits = {segment.format_bits}")
   ```

2. **Verify parse_tagged_text()** extracts text correctly:
   - Input: `"Hello <1>world</1>!"`
   - Expected segments:
     - `TextSegment(text="Hello ", format_bits=0)`
     - `TextSegment(text="world", format_bits=1)`  ← NO TAGS!
     - `TextSegment(text="!", format_bits=0)`

3. **Check if problem is in translation** (tags doubled?):
   - Google Translate might return: `"<1><1>world</1></1>"` (nested)
   - Or: `"< 1>world</ 1>"` (spaces)
   - Need to handle edge cases

4. **Possible fixes:**
   - **Fix A**: Improve `parse_tagged_text()` regex to handle edge cases
   - **Fix B**: Add `clean_tags()` step before writing DOCX
   - **Fix C**: Verify segments before passing to `create_docx_from_segments()`

**Test:**
- Load DOCX with bold text
- Translate
- Save as DOCX
- Open in Word → should see formatted text, NO tags

**Commit:** "Emergency fix: Remove tags from DOCX output"

---

## Success Criteria

- ✅ DOCX files have formatting (bold, italic, colors)
- ✅ DOCX files have NO visible tags (`<1>`, `<17:FF0000>`, etc.)
- ✅ User tags preserved (e.g., `<div>`, `<html>`)
- ✅ UI preview shows plain text (no numeric tags)

---

**NEXT:** Investigate and implement fix
