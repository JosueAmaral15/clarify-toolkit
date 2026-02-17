# Phase C.1: Advanced Chunking Design - COM8

**Session:** COM8  
**Date:** 2026-02-17  
**Duration:** 4-6 hours (estimated)  
**Status:** 🔧 **IN PROGRESS**

---

## Overview

**Phase C Goals:**
1. **Context Overlap (200 chars)** - Maintain translation quality across chunk boundaries
2. **Semantic Splitting** - Break at paragraph/table boundaries (not mid-sentence)
3. **HTML Tag Preservation** - Never break inside HTML tags
4. **Enhanced Error Handling** - Better error messages, recovery strategies

**Current State (Phase B):**
- ✅ Basic character-based chunking (4800 chars)
- ✅ Sentence boundary detection (. ! ?)
- ✅ Progress tracking with callbacks
- ⚠️ May break HTML tags
- ⚠️ No context overlap
- ⚠️ No semantic awareness

---

## User Requirements Review

From user specifications:

| Requirement | Phase B | Phase C |
|-------------|---------|---------|
| **Chunk Size** | 4800 chars ✅ | Same ✅ |
| **Progress Display** | Bar + status ✅ | Enhanced ✅ |
| **Context Overlap** | None ❌ | 200 chars ✅ |
| **Error Handling** | Fail fast ✅ | Same ✅ |
| **Semantic Splitting** | Focus Option B ⚠️ | Full Option C ✅ |

**User Quote:**
> "Option C: Mixed (semantic + fallback to chars) but focus on option B"

**Interpretation:** Implement semantic splitting (paragraphs, tables) with fallback to sentence boundaries when semantic split fails.

---

## Feature 1: Context Overlap (200 chars)

### Problem Statement

**Without Overlap:**
```
Chunk 1: "...The company announced profits. [END]"
Chunk 2: "[START] The CEO said..."
```

**Issue:** Translator loses context that "The CEO" belongs to "The company"

**With 200-char Overlap:**
```
Chunk 1: "...The company announced profits."
Chunk 2: "...The company announced profits. The CEO said..."
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              200 chars overlap (context)
```

**Benefit:** Translator sees context, improves pronoun resolution, coherence

### Algorithm Design

**Overlap Strategy:**
- Last 200 chars of Chunk N = First 200 chars of Chunk N+1
- Overlap region translated twice, second translation used
- Prevents context loss at boundaries

**Implementation:**

```python
def _split_into_chunks_with_overlap(
    text: str, 
    max_size: int = 4800, 
    overlap_size: int = 200
) -> List[tuple[str, int, int]]:
    """
    Split text into overlapping chunks.
    
    Returns:
        List of (chunk_text, start_pos, end_pos) tuples
        - start_pos: Position in original text (for deduplication)
        - end_pos: Position in original text
    """
    chunks = []
    current_pos = 0
    text_len = len(text)
    
    while current_pos < text_len:
        # Calculate chunk end
        chunk_end = min(current_pos + max_size, text_len)
        
        # Find sentence boundary (same as Phase B)
        if chunk_end < text_len:
            chunk_end = find_sentence_boundary(text, chunk_end)
        
        # Extract chunk with context overlap from previous chunk
        if current_pos > 0 and current_pos >= overlap_size:
            # Include 200 chars from previous chunk for context
            chunk_start = current_pos - overlap_size
        else:
            chunk_start = current_pos
        
        chunk_text = text[chunk_start:chunk_end]
        chunks.append((chunk_text, chunk_start, chunk_end))
        
        # Move to next chunk (overlap accounted for in start position)
        current_pos = chunk_end
    
    return chunks
```

**Deduplication After Translation:**

```python
def _deduplicate_overlaps(
    translated_chunks: List[str],
    chunk_positions: List[tuple[int, int]]
) -> str:
    """
    Remove overlapping regions from translated chunks.
    
    Strategy: Keep only non-overlapping portions of each chunk.
    """
    result_parts = []
    
    for i, (translated, (start, end)) in enumerate(zip(translated_chunks, chunk_positions)):
        if i == 0:
            # First chunk: use entire translation
            result_parts.append(translated)
        else:
            # Subsequent chunks: skip overlap region
            # Overlap is approximately 200 chars, but translation may change length
            # Estimate: ratio = len(translated) / (end - start)
            
            prev_end = chunk_positions[i-1][1]
            overlap_original = start - prev_end  # Should be 200 or 0
            
            if overlap_original > 0:
                # Calculate overlap in translated text (proportional)
                ratio = len(translated) / (end - start)
                overlap_translated = int(overlap_original * ratio)
                
                # Skip overlapping portion
                result_parts.append(translated[overlap_translated:])
            else:
                result_parts.append(translated)
    
    return ''.join(result_parts)
```

**Edge Cases:**
- First chunk: No overlap (nothing before it)
- Last chunk: May be < 200 chars (still works)
- Very short text: Overlap may exceed chunk size (skip overlap)

---

## Feature 2: Semantic Splitting

### Problem Statement

**Phase B (Character-Based):**
```html
<p>Long paragraph text... [BREAK HERE - MID PARAGRAPH!]
...rest of paragraph</p>
<table>...</table>
```

**Issue:** Breaking mid-paragraph loses semantic meaning, may corrupt HTML

**Phase C (Semantic):**
```html
<p>Long paragraph text...</p>  [BREAK AFTER PARAGRAPH]
<table>...</table>
```

**Benefit:** Preserves document structure, cleaner translations

### Algorithm Design

**Priority Order:**
1. **Table boundaries** - Never split tables (highest priority)
2. **Paragraph boundaries** - Prefer `</p>` or `\n\n` breaks
3. **Sentence boundaries** - Fallback to Phase B logic (. ! ?)
4. **Hard break** - Last resort at max_size

**HTML Structure Detection:**

```python
def _find_semantic_boundaries(text: str) -> List[int]:
    """
    Find semantic break points in HTML text.
    
    Returns:
        List of positions suitable for breaking (sorted)
    """
    boundaries = []
    
    # Find all paragraph ends: </p>
    for match in re.finditer(r'</p>', text):
        boundaries.append(match.end())
    
    # Find all table ends: </table>
    for match in re.finditer(r'</table>', text):
        boundaries.append(match.end())
    
    # Find all heading ends: </h1> to </h6>
    for match in re.finditer(r'</h[1-6]>', text):
        boundaries.append(match.end())
    
    # Find all list ends: </ul>, </ol>
    for match in re.finditer(r'</(ul|ol)>', text):
        boundaries.append(match.end())
    
    # Sort boundaries
    boundaries.sort()
    return boundaries
```

**Chunking with Semantic Awareness:**

```python
def _split_with_semantic_boundaries(
    text: str,
    max_size: int = 4800,
    overlap_size: int = 200
) -> List[tuple[str, int, int]]:
    """
    Split text at semantic boundaries (paragraphs, tables, etc.).
    """
    # Find all semantic boundaries
    semantic_boundaries = _find_semantic_boundaries(text)
    
    chunks = []
    current_pos = 0
    text_len = len(text)
    
    while current_pos < text_len:
        # Find best semantic boundary within max_size
        target_end = min(current_pos + max_size, text_len)
        
        # Look for semantic boundary near target_end
        best_boundary = None
        for boundary in semantic_boundaries:
            if current_pos < boundary <= target_end:
                best_boundary = boundary
            elif boundary > target_end:
                break  # Past our target range
        
        if best_boundary:
            # Use semantic boundary
            chunk_end = best_boundary
        else:
            # No semantic boundary found, fallback to sentence boundary
            chunk_end = find_sentence_boundary(text, target_end)
        
        # Add overlap logic here (same as Feature 1)
        # ...
        
        chunks.append((text[current_pos:chunk_end], current_pos, chunk_end))
        current_pos = chunk_end
    
    return chunks
```

---

## Feature 3: HTML Tag Preservation

### Problem Statement

**Phase B May Break:**
```html
<span class="fmt1">Very long text that exceeds 4800 cha[BREAK]rs and continues</span>
                                                         ^
                                                    Broken tag!
```

**Result:** Invalid HTML, parser fails

**Phase C Prevention:**
```html
<span class="fmt1">Very long text that exceeds 4800 chars and continues</span>[BREAK]
                                                                              ^
                                                                         Safe break
```

### Algorithm Design

**Tag Detection:**

```python
def _is_inside_html_tag(text: str, position: int) -> bool:
    """
    Check if position is inside an HTML tag.
    
    Returns:
        True if position is between < and >
    """
    # Look backward for nearest < and >
    last_open = text.rfind('<', 0, position)
    last_close = text.rfind('>', 0, position)
    
    # If last < is more recent than last >, we're inside a tag
    return last_open > last_close
```

**Safe Break Position:**

```python
def _find_safe_break_position(text: str, target_pos: int) -> int:
    """
    Find safe position to break, avoiding splitting HTML tags.
    
    Strategy:
    1. If target_pos is safe, use it
    2. Otherwise, move forward to next tag close (>)
    3. If too far, move backward to previous tag close
    """
    if not _is_inside_html_tag(text, target_pos):
        return target_pos  # Already safe
    
    # Look forward for next >
    next_close = text.find('>', target_pos)
    if next_close != -1 and (next_close - target_pos) < 200:
        # Close tag is nearby, use it
        return next_close + 1
    
    # Look backward for previous >
    prev_close = text.rfind('>', 0, target_pos)
    if prev_close != -1:
        return prev_close + 1
    
    # No safe position found, use target (rare edge case)
    return target_pos
```

**Integration with Chunking:**

```python
# Inside _split_with_semantic_boundaries()
chunk_end = find_semantic_boundary(...)  # Phase C.2
chunk_end = _find_safe_break_position(text, chunk_end)  # Phase C.3
```

---

## Feature 4: Enhanced Error Handling

### Current (Phase B)

**Error Message:**
```
Translation failed at chunk 5/42 after 3 attempts. Last error: HTTP Error 413
```

**Issues:**
- No context about what failed
- No chunk content preview
- No recovery suggestions

### Phase C Improvements

**Enhanced Error Message:**
```
Translation failed at chunk 5/42:
  Position: chars 19200-24000 (of 201,600 total)
  Chunk size: 4800 chars
  Content preview: "<p>Transgenic organisms are...</p><table>..."
  Attempts: 3 (all failed)
  Last error: HTTP Error 413: Request Entity Too Large
  
Suggestions:
  - Chunk may still be too large (reduce max_chunk_size)
  - Network timeout (check connection)
  - Try translating smaller portion manually
```

**Implementation:**

```python
class ChunkTranslationError(Exception):
    """Enhanced error for chunk translation failures."""
    
    def __init__(
        self,
        chunk_number: int,
        total_chunks: int,
        chunk_start: int,
        chunk_end: int,
        chunk_text: str,
        attempts: int,
        last_error: str
    ):
        self.chunk_number = chunk_number
        self.total_chunks = total_chunks
        self.chunk_start = chunk_start
        self.chunk_end = chunk_end
        self.chunk_text = chunk_text
        self.attempts = attempts
        self.last_error = last_error
        
        # Generate preview (first 100 chars)
        preview = chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text
        
        message = f"""Translation failed at chunk {chunk_number}/{total_chunks}:
  Position: chars {chunk_start}-{chunk_end}
  Chunk size: {len(chunk_text)} chars
  Content preview: {preview}
  Attempts: {attempts}
  Last error: {last_error}"""
        
        super().__init__(message)
```

---

## Implementation Plan

### C.1: Design ✅ (This document)

### C.2: Context Overlap (90 min)

**Tasks:**
1. Implement `_split_into_chunks_with_overlap()` (30 min)
2. Implement `_deduplicate_overlaps()` (30 min)
3. Update `translate_text_chunked()` to use overlap (15 min)
4. Unit tests for overlap logic (15 min)

**Files:**
- `src/translation/google_translate.py` (+60 lines)
- `tests/com8/test_overlap_COM8.py` (new file, +200 lines)

### C.3: Semantic Splitting (90 min)

**Tasks:**
1. Implement `_find_semantic_boundaries()` (30 min)
2. Implement `_split_with_semantic_boundaries()` (30 min)
3. Update chunking logic to use semantic (15 min)
4. Unit tests for semantic splitting (15 min)

**Files:**
- `src/translation/google_translate.py` (+80 lines)
- `tests/com8/test_semantic_COM8.py` (new file, +250 lines)

### C.4: HTML Tag Preservation (60 min)

**Tasks:**
1. Implement `_is_inside_html_tag()` (15 min)
2. Implement `_find_safe_break_position()` (20 min)
3. Integrate with chunking (10 min)
4. Unit tests for tag preservation (15 min)

**Files:**
- `src/translation/google_translate.py` (+40 lines)
- `tests/com8/test_html_safety_COM8.py` (new file, +150 lines)

### C.5: Enhanced Error Handling (30 min)

**Tasks:**
1. Create `ChunkTranslationError` class (10 min)
2. Update error reporting in `translate_text_chunked()` (10 min)
3. Unit tests for error messages (10 min)

**Files:**
- `src/translation/google_translate.py` (+30 lines)
- `tests/com8/test_error_handling_COM8.py` (new file, +100 lines)

### C.6: Integration Testing (60 min)

**Tasks:**
1. Test with small file (test_table_COM8.docx) - verify no regression
2. Test with medium file (CAIT.docx) - verify semantic splitting
3. Test with large file (Aula 07.docx) - verify HTTP 413 fix
4. Test overlap with manual inspection
5. Test HTML tag preservation with complex HTML

**Manual Testing:** Yes (GUI + file translations)

### C.7: Documentation (30 min)

**Tasks:**
1. Create PHASE_C_COMPLETE_SUMMARY_COM8.md
2. Update ACTION_PLAN_CRITICAL_TRANSLATION_BUGS_COM8.md
3. Document all changes in CHANGELOG

### C.8: Commit (15 min)

**Commit Message:**
```
feat(translation): Add pagination with semantic splitting (COM8)

Fixes #1 (HTTP 413 for large files) and #2 (state persistence)

Phase A: State Clearing
- Clear translation state on file load, translate start, and errors
- Prevents old results persisting in UI

Phase B: Basic Pagination
- Character-based chunking (4800 chars, sentence boundaries)
- Progress tracking with callbacks
- Automatic chunking for texts > 4500 chars
- 20 unit tests (all passing)

Phase C: Advanced Features
- 200-char context overlap (maintains translation quality)
- Semantic splitting (paragraphs, tables, headings)
- HTML tag preservation (never break mid-tag)
- Enhanced error messages with context

Testing:
- 60+ unit tests (all passing)
- Integration testing with 953KB file (Aula 07.docx)
- No HTTP 413 errors

Breaking Changes: None (backward compatible)
```

---

## Technical Details

### Overlap Deduplication Math

**Problem:** Translation may change text length

**Original Text:**
```
Chunk 1: "ABC" (3 chars) → Translated: "XYZ" (3 chars)
Chunk 2: "CDE" (3 chars, overlap "C") → Translated: "ZWR" (3 chars)
```

**Overlap Calculation:**
```python
original_overlap = 1 char  # "C" appears in both
translation_ratio = len(translated) / len(original)
chunk1_ratio = 3 / 3 = 1.0
chunk2_ratio = 3 / 3 = 1.0

translated_overlap_chunk2 = int(1 * 1.0) = 1 char  # Skip "Z"
result = "XYZ" + "WR" = "XYZWR"
```

**Edge Case:** Languages with very different lengths (e.g., Chinese → English)
- Solution: Use proportional calculation, not fixed char count
- Tested in Phase C.6

### Semantic Boundary Priority

**When multiple boundaries in range:**

```
Position:     4000   4200   4500   4700   4800 (max)
              |      |      |      |      |
Boundary:     </p>   </p>   <table...> </table>
Priority:     3      3      4      4
                                   ^
                                   Choose this (closest to max, highest priority)
```

**Priority Rules:**
1. `</table>` > `</p>` (tables are semantic units)
2. Closer to max_size > farther (minimize chunks)
3. After closing tag > before opening tag (don't split elements)

### HTML Safety Examples

**Safe Breaks:**
```html
<p>Text</p>[BREAK]<p>More</p>  ✅ Between elements
<span>Text</span> [BREAK]word  ✅ After tag close
word[BREAK] <span>Text</span>  ✅ Before tag open
```

**Unsafe Breaks (Prevented):**
```html
<span class=[BREAK]"fmt1">     ❌ Inside attribute
<span[BREAK] class="fmt1">     ❌ Inside opening tag
</spa[BREAK]n>                 ❌ Inside closing tag
<img src="url"[BREAK] />       ❌ Inside self-closing tag
```

---

## Success Criteria

### Phase C Complete When:

- [x] C.1: Design documented (this file)
- [ ] C.2: Overlap implemented and tested
- [ ] C.3: Semantic splitting implemented and tested
- [ ] C.4: HTML tag preservation implemented and tested
- [ ] C.5: Enhanced errors implemented
- [ ] C.6: All unit tests passing (60+ tests)
- [ ] C.7: Integration tests passing (Aula 07.docx translates)
- [ ] C.8: Documentation complete
- [ ] C.9: All phases committed

### Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **Context Quality** | 90%+ chunks have context | ⏳ |
| **Semantic Breaks** | 80%+ at paragraph/table | ⏳ |
| **HTML Safety** | 100% valid HTML | ⏳ |
| **Large File Success** | Aula 07.docx translates | ⏳ |
| **No Regression** | Small files still work | ⏳ |
| **Error Messages** | All include context | ⏳ |

---

## Next Steps

1. **Immediate:** Implement C.2 (overlap) - most impactful for quality
2. **Then:** Implement C.3 (semantic) - fixes HTML corruption
3. **Then:** Implement C.4 (HTML safety) - ensures validity
4. **Then:** Quick C.5 (errors) - polish
5. **Finally:** Test, document, commit

**Estimated Time:** 4-6 hours total for Phase C

---

**Phase C.1 Status:** ✅ **COMPLETE** - Design Documented  
**Next:** Phase C.2 - Implement Context Overlap
