# ACTION PLAN: Fix CSS Classes Visible in File Preview

**Programmer**: COM8  
**Date**: 2026-02-09  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: User sees CSS classes (.fmt1, .fmt2, etc.) in File Content Preview

---

## PROBLEM STATEMENT

When user loads an ODT file in Google Translate tool, the File Content (Preview) shows:
```
.fmt1 { font-weight: bold; font-size: 14pt; line-height: 1.0; }
.fmt2 { font-size: 12pt; line-height: 1.0; }
...
CAIT 13/11/12 Nome: Josué...
```

**Expected**: Should show ONLY text content, no CSS classes
**Actual**: Shows CSS classes first, then text content

---

## ROOT CAUSE ANALYSIS

### Issue Location
File: `src/gui/google_translate_dock.py`  
Method: `_browse_file()` - Line 478-510 (ODT loading)

### Current Code Flow
1. Load ODT → Extract HTML (with `<style>` section containing CSS)
2. Use `TextExtractor` HTMLParser to get plain text
3. `TextExtractor.handle_data()` extracts ALL text data
4. Problem: It extracts text from `<style>` section too!

### The Bug
```python
class TextExtractor(HTMLParser):
    def handle_data(self, data):
        if data.strip():
            self.text_parts.append(data.strip())  # ← Extracts EVERYTHING including CSS!
```

---

## SOLUTION PLAN

### Step 1: Fix TextExtractor to Skip Style Content
Add tracking of current tag context:
```python
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_style = False  # Track if inside <style> tag
    
    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            self.in_style = True
    
    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False
    
    def handle_data(self, data):
        # Skip data inside <style> tags
        if not self.in_style and data.strip():
            self.text_parts.append(data.strip())
```

### Step 2: Apply Same Fix in TWO Locations
1. `_browse_file()` method (line 492-506) - File loading preview
2. `_on_translation_completed()` method (line 672-687) - Translation result display

### Step 3: Test
1. Load ODT file
2. Verify preview shows NO CSS classes
3. Translate file
4. Verify result shows NO CSS classes
5. Save and verify formatting preserved

---

## FILES TO MODIFY

1. **src/gui/google_translate_dock.py**
   - Update `TextExtractor` class in `_browse_file()` (2 occurrences)
   - Update `TextExtractor` class in `_on_translation_completed()`

---

## TESTING CHECKLIST

- [ ] Load ODT file → Preview shows no CSS
- [ ] Translate → Result shows no CSS
- [ ] Save as ODT → Formatting preserved
- [ ] Open saved file → All styles intact

---

---

## ADDITIONAL BUGS DISCOVERED

### Bug 2: CSS Also Visible in Translation Result Display
**Location**: `_on_translation_completed()` - Line 672-687  
**Problem**: Same `TextExtractor` bug (duplicate code)  
**Note**: Line 678 has WRONG attempted fix:
```python
if self.get_starttag_text() and 'style' not in self.get_starttag_text():
```
This doesn't work because `get_starttag_text()` returns `None` in `handle_data()` context!

**Fix**: Apply same solution as Bug 1

---

### Bug 3: ODT Save - Formatting Loss (NEEDS USER DEBUG)
**Location**: `_save_as_odt()` - Line 936-941  
**Status**: Debug logging added but NOT TESTED by user yet  
**Evidence**: User reported file `/home/josue/Documents/translation_20260209_151539.odt` has:
- 0 automatic styles
- 1 paragraph (plain text only)
- No formatting preserved

**Possible Causes**:
1. `self._translated_html` is None (HTML not stored)
2. `self._css_manager` is None (CSS manager not preserved)
3. Condition falls through to OLD system or FALLBACK
4. `create_odt_from_html()` has bug (less likely - tested in isolation)

**Action Required**: User needs to translate + save and provide debug output showing:
```
[DEBUG] _save_as_odt called:
  _translated_html: True/False (length: ???)
  _css_manager: True/False (type: ???)
  → Using HTML system / OLD segment system / FALLBACK plain text
```

---

### Bug 4: Potential _css_manager Persistence Issue
**Problem**: `_css_manager` is set in TWO places:
1. `_browse_file()` line 486 - When user loads ODT
2. `_translate()` line 567 - When user clicks Translate (re-extracts from file!)

**Risk**: If user loads file → switches language → translates, `_css_manager` is extracted twice from same file (wasteful but harmless). However, this creates tight coupling between load and translate.

**Question**: Should we re-use the `_css_manager` from `_browse_file()` instead of re-extracting?

---

## CORRECT IMPLEMENTATION REFERENCE

The `HTMLToODTParser` class (line 755-776) in `html_format_mapper.py` **already has the correct implementation**:

```python
def handle_starttag(self, tag, attrs):
    self.current_tag = tag
    # ... extract class

def handle_data(self, data):
    # Skip whitespace in head/style
    if self.current_tag in ['style', 'head', 'title']:
        return
```

This is the pattern to use for `TextExtractor` in both locations!

---

## REVISED SOLUTION PLAN

### Step 1: Fix TextExtractor (Both Locations)
Update `TextExtractor` to track current tag:

```python
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.current_tag = None  # Track current tag
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
    
    def handle_endtag(self, tag):
        if tag == self.current_tag:
            self.current_tag = None
    
    def handle_data(self, data):
        # Skip data inside style/script/head tags
        if self.current_tag in ['style', 'script', 'head', 'title']:
            return
        if data.strip():
            self.text_parts.append(data.strip())
    
    def get_text(self):
        return ' '.join(self.text_parts)  # Line 492-506
        # OR
        return '\n'.join(self.text_parts)  # Line 672-687
```

### Step 2: Apply Fix in TWO Locations
1. **`_browse_file()`** method (line 492-506) - File loading preview
2. **`_on_translation_completed()`** method (line 672-687) - Translation result
   - Remove WRONG fix at line 678

### Step 3: Request User Testing for Bug 3
Ask user to:
1. Load ODT file
2. Translate
3. Save as ODT
4. Provide debug output from terminal

---

## FILES TO MODIFY

1. **src/gui/google_translate_dock.py**
   - Fix `TextExtractor` in `_browse_file()` (line 492-506)
   - Fix `TextExtractor` in `_on_translation_completed()` (line 672-687)
   - Remove broken fix at line 678

---

## TESTING CHECKLIST

**Phase 1: CSS Display (Can test immediately)**
- [ ] Load ODT file → Preview shows NO CSS classes
- [ ] Translate → Result shows NO CSS classes
- [ ] Text starts with "CAIT 13/11/12 Nome: Josué..."

**Phase 2: ODT Formatting (Requires user test + debug output)**
- [ ] User translates and saves ODT
- [ ] User provides debug output
- [ ] Analyze which code path was taken
- [ ] Fix actual bug if identified
- [ ] Verify formatting preserved in saved ODT

---

## STATUS: Comprehensive analysis complete - waiting for user approval

**Questions for User**:
1. Should I fix Bugs 1 & 2 (CSS in preview/result) now?
2. After fixing, should I request your testing for Bug 3 (ODT save)?
3. Should I optimize Bug 4 (_css_manager reuse)?
