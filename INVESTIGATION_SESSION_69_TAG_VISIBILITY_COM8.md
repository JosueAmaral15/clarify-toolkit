# Investigation Session 69: Tag Visibility in Translated Document - COM8

**Date:** 2026-02-05  
**Programmer:** COM8  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3

---

## 🎯 OBJECTIVE

Investigate why formatting tags like `<113 |` and `</112|65536>` are visible in the translated ODT document.

---

## 📋 PROBLEM STATEMENT

**User Report:**
When translating an ODT document from Portuguese to English, the output contains:
1. Visible tags: `<113 |`, `</112|65536>`
2. Lost formatting: Alignment and indentation not preserved
3. Some text not translated: Portuguese sentence remains

**Critical Realization:**
- Tags should NEVER be visible to the user
- Tags are for internal processing only
- Something in the workflow is exposing internal tags to the final output

---

## 🔬 INVESTIGATION PLAN

Focus on **ONE ISSUE**: Why are tags visible in the saved ODT file?

### Phase 1: Understand the Workflow
1. Trace: Original ODT → Extract → Tag → Translate → Parse → Save
2. Identify where tags should be added
3. Identify where tags should be removed
4. Find where the process breaks

### Phase 2: Test Each Step Independently
1. Test extraction: Does it work correctly?
2. Test tagging: Are tags formatted correctly?
3. Test translation: Do tags survive translation?
4. Test parsing: Does it remove tags?
5. Test save: Does it create clean output?

### Phase 3: Create Minimal Reproduction
1. Create simple test document
2. Run through workflow
3. Check each intermediate result
4. Find exact point of failure

---

## 🔍 HYPOTHESIS

**Possible Root Causes:**
1. Tags are created but not properly removed before display
2. Parse method fails to extract tags correctly
3. Save method writes tagged text instead of clean text
4. Google Translate API returns mangled tags

**Most Likely:**
The `create_odt_from_segments()` method is receiving segments with `.text` that still contains tags,
instead of clean text. This suggests the parsing step or segment creation is failing.

---

## 🧪 INVESTIGATION STEPS

### Step 1: Check what's sent to Google Translate
```python
# In _translate() method, what does text_to_translate contain?
# Should contain: <113|65536:L>text</113>
# Let's verify this
```

### Step 2: Check what comes back from Google Translate
```python
# In _on_translation_completed(), what does result contain?
# Should still have tags: <113|65536:L>translated text</113>
# Or are tags broken?
```

### Step 3: Check parsing
```python
# FormatMapper.parse_tagged_text(result)
# Does this correctly extract tags and create clean segments?
# Segment.text should NOT contain tags!
```

### Step 4: Check what's saved
```python
# In _save_as_odt(), what do segments contain?
# self._translated_segments[i].text should be clean text
# NOT contain any < > characters
```

---

## 📝 NEXT ACTIONS

1. Add debug logging to trace the workflow
2. Create test script to reproduce issue
3. Check each transformation step
4. Identify exact point where tags leak into output

---

**Status:** Investigation started - gathering evidence


---

## ✅ ROOT CAUSE FOUND

**Problem:** Tags with pipe `|` and colon `:` are not being normalized by the whitespace removal regex!

**Evidence:**
```python
# Current regex (line 1386):
re.sub(r'<\s*(\d+)\s*:\s*([^>]+)\s*>', r'<\1:\2>', tagged_text)

# This handles: < 1 : FF0000 > → <1:FF0000>
# But NOT: < 113 | 65536 : L > → <113|65536:L>
# The pipe character is not considered!
```

**Test Results:**
- Input: `<113|65536:L>text</113|65536>` → ✅ Parses correctly
- Input: `< 113 | 65536:L >text</ 113 >` → ❌ Treated as plain text (tags visible!)
- Input: `<113|65536:L>text</112|65536>` → ❌ Mismatched tag (tags visible!)

**What Happens:**
1. Google Translate adds spaces: `<113|65536:L>` becomes `< 113 | 65536:L >`
2. Normalization regex doesn't handle pipes, so spaces remain
3. Parse pattern `r'<([\d|]+)(?::([^>]+))>([\s\S]*?)</\1>'` requires exact match
4. Pattern fails because of spaces and mismatched closing tag
5. Parser treats entire string as plain text
6. Tags become visible in output!

**Solution:** Fix the normalization regex to handle pipes and spaces correctly.

---

## 📝 NEXT SESSION

**Session 70: Fix Tag Normalization Regex**
- Update regex to handle `|` characters
- Handle spaces around pipes
- Test with all tag formats
- Verify Google Translate compatibility

