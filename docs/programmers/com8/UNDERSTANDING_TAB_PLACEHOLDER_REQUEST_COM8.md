# Understanding: Special Placeholder for Tabs

**User Request**: "make a special placeholder approach feature for the tags too"

## My Understanding:

Currently:
- ✅ Format TAGS use placeholders: `<113|65536>` → `【FMT001】` → `<113|65536>`
- ❌ TABS (`\t`) are sent directly to Google → Google converts them to spaces

**User wants:**
Apply the SAME placeholder protection to `\t` (tabs):
- Before: `text\tmore text` → Google → `text more text` (tab lost)
- After: `text【TAB】more text` → Google → `text【TAB】more text` → `text\tmore text` ✅

## Questions to Clarify:

### Question 1: What to protect?
- **Option A**: Only tabs (`\t`)
- **Option B**: Tabs + line breaks (`\t` + `\n`)
- **Option C**: All special whitespace (`\t`, `\n`, multiple spaces)

**My assumption**: Tabs only (`\t`), since line breaks (`\n`) are already working.

### Question 2: Placeholder format?
- **Option A**: `【TAB】` - Simple and clear
- **Option B**: `【WS001】` - Numbered like format tags
- **Option C**: `\u200B` - Zero-width Unicode marker

**My assumption**: `【TAB】` for consistency with format placeholders.

### Question 3: Where to apply?
- **Option A**: Only in TAGGED text (inside `<tag>\t</tag>`)
- **Option B**: Everywhere in the text (tagged + untagged)

**My assumption**: Everywhere, to preserve ALL tabs.

### Question 4: Restoration?
After translation, restore:
- `【TAB】` → `\t`
- Then `create_odt_from_segments()` converts `\t` → `<text:tab/>`

**My assumption**: Yes, this is the complete flow.

## Implementation Plan (if understanding is correct):

### Step 1: Protect tabs before translation
```python
def protect_special_whitespace(text: str) -> Tuple[str, Dict]:
    # Replace tabs with placeholders
    protected = text.replace('\t', '【TAB】')
    # Could also do: \n\n → 【PARA】, etc.
    return protected, mapping
```

### Step 2: Apply in translation workflow
In `TranslationWorker.run()`:
1. Replace format tags with `【FMT001】`
2. **NEW**: Replace tabs with `【TAB】`
3. Send to Google Translate
4. **NEW**: Restore tabs from `【TAB】` to `\t`
5. Restore format tags from `【FMT001】`

### Step 3: Test
- Original: `CAIT\t\t\t13/11/12`
- Protected: `CAIT【TAB】【TAB】【TAB】13/11/12`
- Translated: `CAIT【TAB】【TAB】【TAB】13/11/12`
- Restored: `CAIT\t\t\t13/11/12`
- Output ODT: Has `<text:tab/>` elements

## Expected Results:

BEFORE (current):
- Tabs: 14 → 0 (Google converts to spaces)

AFTER (with tab placeholders):
- Tabs: 14 → 14 ✅ (Protected from Google)

## Am I understanding correctly?

Please confirm:
1. ✅ You want tabs (`\t`) protected with placeholders
2. ✅ Just like format tags use `【FMT001】`, tabs use `【TAB】`
3. ✅ This prevents Google from converting tabs to spaces
4. ❓ Only tabs, or also line breaks and other whitespace?
5. ❓ Any other special characters to protect?

