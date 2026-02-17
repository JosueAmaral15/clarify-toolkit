# ACTION PLAN: Placeholder Approach for 100% Tag Preservation

**Created**: 2026-02-08  
**Session**: 75  
**Programmer**: COM8  
**User Request**: "I want this" - Placeholder approach

## Goal

Replace format tags with Unicode placeholders before translation, then restore them after.
**Target**: 100% tag preservation (up from current 93.8%)

## Strategy

```
BEFORE TRANSLATION:
<113|65536:525252,9,Arial|0,0>RISCOS PARA A AGRICULTURA: </113|65536>

STEP 1 - Replace with placeholders:
【FMT001】RISCOS PARA A AGRICULTURA: 【/FMT001】

STEP 2 - Google translates:
【FMT001】RISKS TO AGRICULTURE: 【/FMT001】

STEP 3 - Restore original tags:
<113|65536:525252,9,Arial|0,0>RISKS TO AGRICULTURE: </113|65536>
```

## Implementation Plan

### Phase 1: Create Placeholder System (30 min)
- [ ] Create helper function: `replace_tags_with_placeholders(tagged_text)`
  - Use regex to find all `<...>...</...>` tag pairs
  - Generate unique IDs (FMT001, FMT002, etc.)
  - Build mapping: `{placeholder → original_tag_info}`
  - Replace tags with `【FMTXXX】text【/FMTXXX】`
  - Return: (text_with_placeholders, mapping)

- [ ] Create helper function: `restore_tags_from_placeholders(translated_text, mapping)`
  - Find all `【FMTXXX】...【/FMTXXX】` in translated text
  - Look up original tags in mapping
  - Replace placeholders with original tags
  - Return: tagged_translated_text

- [ ] Unicode brackets choice:
  - Use `【】` (U+3010, U+3011) - Japanese corner brackets
  - Rarely used in regular text
  - Visually distinct
  - Google won't interpret as HTML

### Phase 2: Basic Testing (15 min)
- [ ] Test with chunk 6 (the problematic one)
  - Current: 0/2 tags preserved (both corrupted)
  - Expected: 2/2 tags preserved
  
- [ ] Test with simple cases
  - Verify placeholders survive translation
  - Verify restoration works correctly
  - Check translated text quality unchanged

### Phase 3: Integration (30 min)
- [ ] Modify `format_mapper.py`
  - Locate where translation happens
  - Add placeholder conversion before translation
  - Add tag restoration after translation
  - Keep old method as fallback option

- [ ] Add configuration option
  - `use_placeholder_protection = True` (default)
  - Allow switching back to direct tags if needed

### Phase 4: Full Testing (30 min)
- [ ] Test with full biology document
  - Expected: 65/65 tags preserved (100%)
  - Verify all 7 section headers present
  - Check content quality
  - Verify formatting restoration in LibreOffice

- [ ] Test edge cases:
  - Document with 100+ tags
  - Nested formatting (if exists)
  - Special characters in text
  - Very long documents

### Phase 5: Documentation (15 min)
- [ ] Document the approach in code comments
- [ ] Update test files
- [ ] Create comparison report (before/after)
- [ ] Commit with clear message

## Technical Details

### Placeholder Format
```python
# Opening tag with ID:
【FMT001】

# Closing tag with same ID:
【/FMT001】

# Why this works:
- Unicode, not ASCII
- Looks like brackets but isn't < >
- Google won't parse as HTML
- Easy to identify with regex
```

### Mapping Structure
```python
{
  'FMT001': {
    'opening': '<113|65536:525252,9,Arial|0,0>',
    'closing': '</113|65536>',
    'original_text': 'RISCOS PARA A AGRICULTURA: '
  },
  'FMT002': {
    ...
  }
}
```

### Regex Patterns
```python
# Find tag pairs:
pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]*)</(\d+(?:\|\d+)?)>'

# Find placeholders:
pattern = r'【FMT(\d+)】([^【]*)【/FMT\1】'
```

## Expected Results

### Before Placeholder Approach:
- Tags preserved: 61/65 (93.8%)
- Broken tags: 4
- Missing headers: "RISCOS PARA A AGRICULTURA", "RISCOS PARA A SAÚDE"
- Content loss: ~15%

### After Placeholder Approach:
- Tags preserved: 65/65 (100%) ✅
- Broken tags: 0 ✅
- Missing headers: 0 ✅
- Content loss: 0% ✅

## Risks & Mitigations

**Risk 1**: Text already contains 【】 brackets
- **Mitigation**: Escape existing 【】 in text first
- Convert `【` → `〖` before processing

**Risk 2**: Google translates placeholder IDs
- **Mitigation**: Use short numeric IDs (FMT001-FMT999)
- Numbers rarely translated

**Risk 3**: Placeholder order changes
- **Mitigation**: Each placeholder has unique ID
- Order-independent restoration

**Risk 4**: Placeholder split across lines
- **Mitigation**: Test with multiline text
- Adjust regex to handle \n inside placeholders

## Files to Modify

1. **src/translation/format_mapper.py** (~2700 lines)
   - Add new functions at top of file
   - Modify translation workflow
   - Lines to add: ~100-150

2. **test_odt_translation_cli.py**
   - Add test for placeholder approach
   - Compare with direct tag approach

## Success Criteria

✅ All 65 tags preserved in biology document
✅ All 7 section headers present and translated
✅ Content length matches or exceeds direct approach
✅ LibreOffice displays formatting correctly
✅ No broken tags or artifacts
✅ Translation quality unchanged or improved

## Timeline

- **Phase 1**: 30 min (create helpers)
- **Phase 2**: 15 min (basic tests)
- **Phase 3**: 30 min (integration)
- **Phase 4**: 30 min (full tests)
- **Phase 5**: 15 min (docs)
- **Total**: ~2 hours

## Next Steps

1. Create `replace_tags_with_placeholders()` function
2. Test with chunk 6 immediately
3. If successful, integrate into main workflow
4. Run full document test
5. Commit and celebrate 100% preservation! 🎉

---

**Ready to start Phase 1!**
