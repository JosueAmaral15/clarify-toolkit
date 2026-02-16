# Action Plan: Fix ODT Extraction - Missing Tabs, Spaces, Line Breaks

**Date:** 2026-02-06  
**Programmer:** COM8  
**Protocol:** SIMPLICITY_PROTOCOL_3  
**Issue:** START FROM SCRATCH - Fix root cause first

---

## 🚨 ROOT CAUSE FOUND

User identified: **Indentation, line breaks, and blank lines are missing from extraction**

**Example:**
```
Original ODT shows:
CAIT        [tabs]          13/11/12

Nome: Josué

Turma: 3001
```

**But extracted as:**
```
CAIT13/11/12
Nome: Josué
Turma: 3001
```

**All tabs and proper spacing GONE!**

---

## 🔍 INVESTIGATION RESULTS

### What the XML Actually Contains:
```xml
<text:p>
  <text:span>CAIT</text:span>
  <text:span><text:tab/></text:span>  ← TABS ARE HERE!
  <text:span><text:tab/><text:tab/>...</text:span>
  <text:span>13/11/12</text:span>
</text:p>
```

### What extract_formatted_text_from_odt() Returns:
```
<tag>CAIT</tag><tag>13/11/12</tag>  ← TABS MISSING!
```

### The Bug:
The `extract_formatted_text_from_odt()` function:
- ✅ Extracts text from each span
- ✅ Adds format tags around text
- ❌ **IGNORES `<text:tab/>` elements**
- ❌ **IGNORES `<text:line-break/>` elements**
- ❌ **IGNORES `<text:s/>` (spaces) elements**

### Impact:
- Tabs become nothing → words concatenate
- Line breaks disappear → paragraphs merge
- Multiple spaces collapse → formatting destroyed
- **Google Translate gets malformed input**
- **Output looks terrible**

---

## 💡 THE REAL PROBLEM

**I was fixing the WRONG thing!**

Before fixing tag artifact cleanup, translation quality, etc., I should have fixed:
1. **THIS BUG FIRST** - Extraction loses formatting
2. Then test translation with PROPER input
3. Then fix any remaining issues

**User was right** - the "content preview" itself is broken from the start!

---

## 📋 FIX STRATEGY

### Step 1: Fix extract_formatted_text_from_odt()

**Location:** `src/translation/format_mapper.py` line ~969-1342

**Need to handle:**
- `<text:tab/>` → Insert `\t` or multiple spaces
- `<text:line-break/>` → Insert `\n`
- `<text:s text:c="N"/>` → Insert N spaces
- Between spans → Insert space if no explicit whitespace

### Step 2: Fix extract_formatted_text_from_docx() (same issue?)

Check if DOCX extraction has same problems.

### Step 3: Test extraction quality

- [ ] Extract sample ODT
- [ ] Verify tabs preserved
- [ ] Verify line breaks preserved
- [ ] Verify blank lines preserved
- [ ] Compare with LibreOffice display

### Step 4: Re-test translation END-TO-END

After extraction is fixed:
- [ ] Extract (should be better now)
- [ ] Translate
- [ ] Create output
- [ ] Verify quality

---

## ⚠️ WHY I FAILED BEFORE

1. ❌ Didn't check if extraction itself was correct
2. ❌ Assumed extraction was working
3. ❌ Fixed downstream problems without fixing root cause
4. ❌ Didn't notice tabs/spaces missing
5. ❌ User had to point it out

**Lesson:** Always verify EACH STEP of pipeline separately!

---

## 🎯 CORRECT APPROACH

1. ✅ Create action plan (this document)
2. ⏳ Fix extraction to preserve tabs/line-breaks/spaces
3. ⏳ Test extraction thoroughly
4. ⏳ Re-test translation with corrected extraction
5. ⏳ Document actual remaining issues (if any)

---

**Status:** Starting fresh - fixing ROOT CAUSE first  
**Next:** Fix `extract_formatted_text_from_odt()` to handle `<text:tab/>`, `<text:line-break/>`, `<text:s/>`

---

**Created:** 2026-02-06 19:45  
**By:** COM8  
**Branch:** COM8-documentation-reading
