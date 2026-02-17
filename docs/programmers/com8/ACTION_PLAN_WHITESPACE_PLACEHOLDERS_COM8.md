# ACTION PLAN: Whitespace Placeholder Protection

**Session**: 75  
**Programmer**: COM8  
**User Request**: "make a special placeholder approach feature for the tags too"

## Requirements (Confirmed):

Protect from Google Translate conversion:
- ✅ Tabs (`\t`) → `【TAB】`
- ✅ Line breaks (`\n`) → `【BR】`
- ✅ Multiple consecutive spaces (2+) → `【SP2】`, `【SP3】`, etc.
- ✅ Non-breaking spaces (`\xa0`) → `【NBSP】`

Format: Simple placeholders (no numbering)
Apply: Everywhere in text

## Why This Is Needed:

Google Translate currently:
- Converts `\t` → regular space
- Sometimes removes `\n`
- Normalizes multiple spaces → single space
- May convert `\xa0` → regular space

Result: Document structure damaged

## Solution:

### Step 1: Create protection functions
```python
def protect_special_whitespace(text: str) -> str:
    # Order matters! Do longest patterns first
    text = text.replace('\xa0', '【NBSP】')  # Non-breaking space
    text = text.replace('\t', '【TAB】')     # Tab
    text = text.replace('\n', '【BR】')      # Line break
    
    # Multiple spaces: detect and replace
    import re
    def replace_spaces(match):
        count = len(match.group(0))
        return f'【SP{count}】'
    text = re.sub(r' {2,}', replace_spaces, text)
    
    return text

def restore_special_whitespace(text: str) -> str:
    # Restore in reverse order
    import re
    
    # Multiple spaces
    def restore_spaces(match):
        count = int(match.group(1))
        return ' ' * count
    text = re.sub(r'【SP(\d+)】', restore_spaces, text)
    
    # Simple replacements
    text = text.replace('【BR】', '\n')
    text = text.replace('【TAB】', '\t')
    text = text.replace('【NBSP】', '\xa0')
    
    return text
```

### Step 2: Integrate into translation workflow

In `TranslationWorker.run()` (google_translate_dock.py):

**Current flow:**
1. Replace format tags → `【FMT001】`
2. Translate
3. Restore format tags

**New flow:**
1. Replace format tags → `【FMT001】`
2. **NEW**: Replace whitespace → `【TAB】`, `【BR】`, etc.
3. Translate
4. **NEW**: Restore whitespace
5. Restore format tags

### Step 3: Add to format_mapper.py

Add functions alongside existing placeholder functions:
- Line ~112: After `restore_tags_from_placeholders()`
- Export both functions for use in GUI

### Step 4: Testing

Test case - Biology document:
```
Original: "CAIT\t\t\t13/11/12"
Protected: "CAIT【TAB】【TAB】【TAB】13/11/12"
Translated: "CAIT【TAB】【TAB】【TAB】13/11/12"
Restored: "CAIT\t\t\t13/11/12"
Output ODT: <text:tab/> elements present
```

## Expected Results:

| Element | Before | After | Improvement |
|---------|--------|-------|-------------|
| Tabs | 0 | 14 | ✅ +14 |
| Line breaks | 22 | 22 | ✅ Same (already working) |
| Paragraphs | 23 | 17-23 | ✅ Correct structure |
| Multiple spaces | Lost | Preserved | ✅ New |
| Non-breaking spaces | Lost | Preserved | ✅ New |

## Implementation Steps:

1. [ ] Add protection functions to format_mapper.py (10 min)
2. [ ] Integrate into TranslationWorker (15 min)
3. [ ] Test with biology document (10 min)
4. [ ] Verify ODT has proper tab elements (5 min)
5. [ ] Open in LibreOffice for visual check (5 min)
6. [ ] Commit changes (5 min)

**Total time**: ~50 minutes

## Success Criteria:

✅ All 14 tabs preserved in output  
✅ All line breaks preserved  
✅ Multiple spaces preserved  
✅ Non-breaking spaces preserved  
✅ Document structure matches original  
✅ User confirms: "Perfect!"

---

**Status**: Ready to implement  
**Priority**: HIGH - Completes formatting preservation  
**Estimated time**: 50 minutes

