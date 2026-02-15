# ACTION PLAN: Deep Investigation of Google Translate Tag Corruption

**Created**: 2026-02-06  
**Session**: 75  
**Programmer**: COM8  
**User Challenge**: "I can't believe Google Translate modifies number tags! Did you test by yourself?"

## Problem Statement

Google Translate is DEFINITELY corrupting tags, but the behavior is inconsistent:
- Simple test cases: ✅ 100% tag preservation
- Real biology document: ❌ 93.8% preservation (4 tags lost/corrupted)

**Critical Finding**: Chunk 6 translation shows Google Translate **deleted the header text** entirely:
- **Input**: `<113|65536:...>RISCOS PARA A AGRICULTURA: </113|65536><112|65536:...>long text...</112|65536>`
- **Output**: `<113 |long text...</112|65536>` 
- Header text "RISCOS PARA A AGRICULTURA:" completely disappeared!
- Opening tag corrupted to `<113 |` (added space, removed metadata)

## Investigation Plan

### Phase 1: Reproduce the Exact Corruption
- [x] Test simple tags: PASS (100% preserved)
- [x] Test real document: FAIL (93.8% preserved)
- [x] Test chunk 6 isolated: FAIL (tags corrupted)
- [ ] Test variations to find the trigger:
  - Remove nbsp (\xa0) from header
  - Shorten the text after header
  - Change tag numbers
  - Add space between tags
  - Test without colon after header

### Phase 2: Understand the Pattern
- [ ] Test all 7 bold headers individually
- [ ] Compare working vs broken headers
- [ ] Check if it's header-specific or position-specific
- [ ] Test if tag complexity matters (long metadata strings)

### Phase 3: Find Workarounds
**Option A: Placeholder Approach (RECOMMENDED)**
- Replace tags with placeholder strings before translation
- Example: `<113|65536:...>text</113|65536>` → `【TAG001】text【/TAG001】`
- Google won't recognize as HTML, won't corrupt
- Restore tags after translation
- **Pros**: 100% tag protection guaranteed
- **Cons**: Need mapping table, more complex

**Option B: Simplify Tag Format**
- Remove all text metadata, keep only numbers
- Example: `<113|65536>text</113|65536>` instead of `<113|65536:525252,9,Arial|0,0>text</113|65536>`
- Test if simpler tags survive better
- **Risk**: May still corrupt in some contexts

**Option C: Pre-process Headers**
- Detect section headers (bold + short text + colon)
- Translate headers separately
- Keep them outside main translation
- **Pros**: Preserves critical structure
- **Cons**: Complex logic

**Option D: Use Different Translation Service**
- Try DeepL API (if available)
- Try LibreTranslate (open source, local)
- **Pros**: Might have better HTML/tag preservation
- **Cons**: Requires API keys / setup

### Phase 4: Implement Solution
- [ ] Choose best approach
- [ ] Implement with tests
- [ ] Verify with biology document
- [ ] Test with multiple documents

## Current Findings

### What Works (100% tag preservation):
- Short sentences with tags
- Simple adjacent tags
- Tags with long metadata
- Tags containing only numbers
- Tags with tabs (\t) inside - tabs converted to spaces but tags intact

### What Breaks (tags corrupted):
- Chunk 6: Bold header + long adjacent text
- Chunk 8: Bold header + adjacent text
- Pattern: `<113|bold>HEADER:</113|bold><112|normal>very long text...</112|normal>`
- Symptom: Header text DELETED, opening tag corrupted to `<113 |`

### Hypothesis:
Google Translate might be:
1. Trying to "fix" what it thinks is malformed HTML
2. Getting confused by adjacent tags with no space
3. Having issues with specific Portuguese text patterns
4. Hitting length limits and breaking tags at boundaries
5. Treating certain text patterns (CAPS + colon) as special

## Next Actions

1. **IMMEDIATE**: Test if placeholder approach works (Option A)
2. Then test simplified tags (Option B)
3. Compare results
4. User decides which approach to implement

## User Was Right

The user challenged me correctly:
- ✅ "Did you test by yourself?" - No, I only tested simple cases
- ✅ "Are you really investigating deeper?" - No, I assumed Google was the problem without proof
- ✅ "The possibility to change numbers is maybe null" - Correct! Numbers alone DO survive
- ✅ Tags ARE being corrupted, but we need to understand WHY and WHERE

**Lesson**: Don't accept surface-level testing. Test with real data in real conditions.
