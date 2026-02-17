# ACTION PLAN: Fix Paragraph Structure Loss

**Created**: 2026-02-08  
**Session**: 75  
**Programmer**: COM8  
**User Feedback**: "blank lines, alignment, and spacing not respected"

## User Is CORRECT!

Formatting losses confirmed:
- ❌ Paragraphs: 17 → 3 (lost 14!)
- ❌ Tabs: 14 → 0 (all replaced with spaces by Google)
- ❌ Line breaks: 22 → 0 (all lost!)
- ❌ Blank lines: 20 → 0 (all lost!)

## Root Cause Found

The `\n\n` newlines ARE preserved through translation!

**Tagged text has:**
```
</tag>\n\n<tag>
```

**But `parse_tagged_text()` IGNORES text between tags!**

It only captures text INSIDE tags:
```python
<113|...>text here</113>  # ✅ Captured
</113>\n\n<112|...>        # ❌ IGNORED!
```

Result: All `\n\n` between tags are lost → All blank lines lost → Paragraphs merge!

## Solution

Modify `parse_tagged_text()` to:
1. Capture text BETWEEN closing and opening tags
2. Treat `\n\n` as paragraph breaks
3. Create separate segments for untagged text
4. Preserve tabs and line breaks

## Implementation Plan

### Step 1: Fix `parse_tagged_text()` (30 min)
Currently at line ~1366-1530 in format_mapper.py

Add logic to capture text between tags:
```python
# Current regex only matches: <tag>text</tag>
# Need to also match: </tag>PLAIN TEXT<tag>

# After each </tag>, check if there's text before next <tag>
# If text contains \n\n, create new paragraph
# If text is just \n, create line break
# If text is spaces/tabs, preserve as whitespace segment
```

### Step 2: Modify `create_odt_from_segments()` (20 min)
Currently at line ~2248-2495

Handle special segment types:
- **Paragraph break**: Close current `<text:p>`, start new one
- **Line break**: Insert `<text:line-break/>`
- **Tab**: Insert `<text:tab/>` (not just space)

### Step 3: Handle Alignment (15 min)
Original had paragraph styles with alignment:
- P1, P2, P3, P5, P6, P7 styles

Need to:
- Extract alignment from original paragraph styles
- Store in segment metadata
- Apply to output paragraphs

### Step 4: Testing (30 min)
- Test with biology document
- Verify: 17 paragraphs → 17 paragraphs
- Verify: Tabs preserved as tabs
- Verify: Line breaks preserved
- Verify: Blank lines present
- Open in LibreOffice to verify visual layout

## Technical Details

### Problem in parse_tagged_text()
```python
# Current pattern (line ~1445):
pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]*?)</(\d+(?:\|\d+)?)>'

# This only captures text INSIDE tags
# Misses text BETWEEN tag pairs!
```

### Solution: Two-pass parsing
```python
# Pass 1: Extract ALL text (tagged + untagged)
# Pass 2: Create segments with proper breaks

# Identify paragraph breaks: \n\n
# Identify line breaks: \n
# Identify tabs: \t
```

### Segment Types Needed
```python
class TextSegment:
    text: str
    format_bits: int
    segment_type: str  # NEW: 'text', 'para_break', 'line_break', 'tab'
```

## Expected Results

### Before Fix:
```
Original: 17 paragraphs, 14 tabs, 22 line breaks
Output:   3 paragraphs, 0 tabs, 0 line breaks
Quality:  ❌ Everything merged
```

### After Fix:
```
Original: 17 paragraphs, 14 tabs, 22 line breaks
Output:   17 paragraphs, 14 tabs (as spaces OK), 22 line breaks
Quality:  ✅ Structure preserved
```

**Note**: Tabs converted to spaces by Google is acceptable.  
What matters is the visual spacing is preserved!

## Files to Modify

1. **src/translation/format_mapper.py**
   - Line ~1366-1530: `parse_tagged_text()` - Add between-tag text capture
   - Line ~2248-2495: `create_odt_from_segments()` - Handle paragraph breaks

## Success Criteria

✅ Output has 17 paragraphs (same as original)  
✅ Blank lines present between sections  
✅ Visual structure matches original  
✅ Line breaks within paragraphs preserved  
✅ User confirms: "Yes, now it's correct!"

---

**Status**: Ready to implement  
**Priority**: HIGH - User-reported issue  
**Estimated time**: 1.5 hours

