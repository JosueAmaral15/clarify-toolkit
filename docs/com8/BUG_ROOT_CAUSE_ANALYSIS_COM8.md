# Root Cause Analysis: Visible Format Tags Bug - COM8

**Date**: 2026-02-08
**Session**: 76
**Programmer**: COM8
**Status**: Investigation Complete ✅

---

## 🔴 THE BUG

**Symptom**: Format tags visible in translated ODT document

**Location**: Paragraph 19 (English translated output)

**Example**:
```
Increase in toxic substances</113|65536><112|65536:525252,9,Arial|0,0>There are plants...
```

**What user should see**:
```
3. Increase in toxic substances
There are plants...
```

---

## 🔍 INVESTIGATION FINDINGS

### Finding #1: Tags Are XML-Escaped Text
**Evidence**:
```xml
<ns0:span>...Increase in toxic substances&lt;/113|65536&gt;&lt;112|65536:525252,9,Arial|0,0&gt;</ns0:span>
```

The tags are stored as **literal text** with `<` and `>` escaped as `&lt;` and `&gt;`.

This means they're NOT XML elements - they're plain text!

### Finding #2: Original Has Proper Structure
**Original Portuguese (Paragraph 13)**:
- 10 properly formatted `<text:span>` elements
- Clear style names: `T11` (bold headers) and `T12` (body text)
- Structure:
  - Span 2 (T11): "1. Aumento das alergias"
  - Span 3 (T12): body text
  - Span 4 (T11): "2. Aumento de resistência aos antibióticos"
  - Span 5-6 (T12): body text
  - Span 7 (T11): "3. Aumento das substâncias tóxicas" ← This one!
  - Span 8 (T12): body text
  - Span 9 (T11): "4. Maior quantidade de resíduos de agrotóxicos"
  - Span 10 (T12): body text

**Translated English (Paragraph 19)**:
- Tags visible as plain text!
- Should be `<text:span>` elements but aren't

### Finding #3: Multiple Occurrences
**Two locations in same paragraph**:
1. After "Increase in toxic substances" (section 3 header)
2. After "Greater amount of pesticide residues" (section 4 header)

Both show: `</113|65536><112|65536:525252,9,Arial|0,0>`

This pattern is: **closing tag + opening tag** (transition between spans)

---

## 🧩 ROOT CAUSE ANALYSIS

### What Should Happen:
1. **Extract**: ODT → Tagged text with format tags
   - Result: `<113|65536:...>text</113|65536>`
2. **Protect**: Replace tags with placeholders
   - Result: `【FMT001】text【/FMT001】`
3. **Translate**: Send to Google Translate
   - Result: `【FMT001】translated text【/FMT001】`
4. **Restore whitespace**: First restoration pass
5. **Restore format tags**: Convert placeholders back to tags
   - Result: `<113|65536:...>translated text</113|65536>`
6. **Create ODT**: Convert tags to `<text:span>` elements
   - Result: Proper ODT with formatting

### What Actually Happened:

**Hypothesis #1: Placeholders Never Created** ❓
- Maybe some tags weren't matched by the regex?
- Tags in a special format that regex missed?
- Need to check: Does `replace_tags_with_placeholders()` match this pattern?

**Hypothesis #2: Google Deleted Placeholders** ❓
- Google completely removed the placeholders
- Restoration had nothing to restore
- Need to check: What did Google actually return?

**Hypothesis #3: Restoration Failed** ⭐ MOST LIKELY
- Placeholders were corrupted: `【FMT001】` → `【F MT001】`
- Restoration regex didn't match the corrupted version
- Original tags were left as-is
- Need to check: Are there orphaned/corrupted placeholders?

**Hypothesis #4: Between-Span Transitions** ⭐ VERY LIKELY
- The visible pattern is `</113|65536><112|65536:...>` (closing + opening)
- This is a transition point between two spans
- Maybe transitions aren't handled correctly?
- The closing tag and opening tag are ADJACENT (no space)
- Regex might not match this specific pattern

---

## 🎯 MOST LIKELY ROOT CAUSE

**Between-Span Transitions Not Properly Handled**

The pattern `</113|65536><112|65536:525252,9,Arial|0,0>` appears at:
- End of numbered header (e.g., "3. Aumento das substâncias tóxicas")
- Start of body text

This is a **span transition point** where:
1. Header span closes: `</113|65536>`
2. Body span opens immediately: `<112|65536:525252,9,Arial|0,0>`

**Why it fails**:
1. The `replace_tags_with_placeholders()` regex likely expects:
   - Paired tags: `<TAG>content</TAG>` ✅
   - NOT adjacent unpaired tags: `</TAG1><TAG2>` ❌

2. These transition tags are:
   - NOT paired (closing one style, opening another)
   - ADJACENT (no content between them)
   - AT paragraph breaks/line breaks

3. So they're LEFT AS-IS (not converted to placeholders)

4. During ODT creation, they're treated as literal text and XML-escaped

---

## 📊 EVIDENCE SUMMARY

| Aspect | Finding |
|--------|---------|
| Visible text | `</113|65536><112|65536:...>` |
| XML storage | `&lt;/113|65536&gt;&lt;112|65536:...&gt;` (escaped) |
| Location | Paragraph 19, after section headers 3 & 4 |
| Pattern | Closing tag + opening tag (no space) |
| Original | Proper `<text:span>` elements |
| Occurrences | 2 in same paragraph |
| Type | Span transition points |

---

## ✅ VERIFICATION NEEDED

To confirm root cause:
1. Check if `replace_tags_with_placeholders()` handles adjacent tags
2. Test regex with pattern: `</113|65536><112|65536:...>`
3. Check extraction phase - does it create this pattern?
4. Check if there are line breaks between the tags
5. Trace one instance through entire pipeline

---

## 🛠️ PROPOSED FIX

**Option 1: Fix Regex to Match Adjacent Tags**
- Modify `replace_tags_with_placeholders()` to handle:
  - Paired tags: `<TAG>content</TAG>`
  - Adjacent transitions: `</TAG1><TAG2>`
- Create separate placeholders for each

**Option 2: Pre-process to Add Markers**
- Insert a marker between adjacent tags before placeholder creation
- Example: `</TAG1><TAG2>` → `</TAG1>【TRANS】<TAG2>`
- Easier to match with regex
- Remove marker after restoration

**Option 3: Post-process to Clean Up**
- After ODT creation, scan for escaped tags in text
- Convert them to proper XML elements
- Risky - might miss edge cases

**Recommendation**: **Option 1** - Fix the regex to be more comprehensive

---

## 🔄 NEXT STEPS

1. ✅ Investigation complete
2. ⏳ Verify root cause with regex test
3. ⏳ Implement fix in `replace_tags_with_placeholders()`
4. ⏳ Test with user's file
5. ⏳ Verify NO visible tags anywhere
6. ⏳ Get user approval

---

**Investigated by**: COM8  
**Hours spent**: ~2 hours  
**Confidence level**: 85% (need regex verification)  
**Status**: Ready to fix
