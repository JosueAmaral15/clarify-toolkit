# Phase B.1: Chunking Algorithm Design - COM8

**Session:** COM8  
**Date:** 2026-02-17  
**Duration:** 30 minutes (estimated)  
**Status:** 🔧 **IN PROGRESS**

---

## Problem Analysis

### Bug #1: HTTP 413 "Request Entity Too Large"

**Symptom:**
```
Translation failed after 3 attempts. Last error: Translation request failed: HTTP Error 413: Request Entity Too Large
```

**Cause:** Single API call with entire document (953KB Aula 07.docx → ~100-200KB HTML)

**Google Translate Limits:**
- **Official API:** 5000 chars per request
- **Web Scraping (current):** ~100-200KB estimated (undocumented)
- **User Safety Margin:** 4800 chars per chunk

---

## Design Requirements

### User Specifications

From user requirements:
1. **Chunk Size:** 4800 characters (5000 limit - 200 safety margin)
2. **Progress Display:** Both simple bar + detailed status
   - Bar: `[====> ] 50% (Page 5/10)`
   - Status: `Translating page 5 of 10... 30s remaining`
3. **Context Overlap:** 200 chars between chunks (Phase C)
4. **Error Handling:** Fail entire translation on any chunk failure
5. **Semantic Splitting:** Prefer paragraph boundaries (Phase C, fallback to chars)

### Technical Requirements

1. **Sentence Boundary Detection:** Break at last full stop before 4800 chars
2. **HTML Tag Preservation:** Don't break inside `<tag>...</tag>`
3. **Progress Callback:** Real-time updates to GUI
4. **Sequential Translation:** Maintain document order and context
5. **Memory Efficient:** Stream chunks, don't duplicate full document

---

## Algorithm Design

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Input: Full HTML Document (500KB)                          │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │ 1. Split into Chunks            │
         │    - 4800 char max              │
         │    - Break at sentence boundary │
         │    - Preserve HTML tags         │
         └─────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │ 2. Translate Each Chunk         │
         │    - Sequential order (1→2→3)   │
         │    - Progress callback per chunk│
         │    - Fail fast on error         │
         └─────────────────────────────────┘
                          │
                          ▼
         ┌─────────────────────────────────┐
         │ 3. Concatenate Results          │
         │    - Join translated chunks     │
         │    - Preserve HTML structure    │
         └─────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Output: Translated HTML Document                           │
└─────────────────────────────────────────────────────────────┘
```

### Chunking Algorithm (Phase B - Character-Based)

**Phase B Focus:** Simple character-based splitting with sentence boundaries

```python
def split_into_chunks(text: str, max_size: int = 4800) -> List[str]:
    """
    Split text into chunks of max_size, breaking at sentence boundaries.
    
    Phase B: Simple character-based splitting.
    Phase C: Add semantic splitting (paragraphs, tables).
    """
    chunks = []
    current_pos = 0
    text_len = len(text)
    
    while current_pos < text_len:
        # Calculate chunk end (max 4800 chars from current position)
        chunk_end = min(current_pos + max_size, text_len)
        
        # If not at end of document, find last sentence boundary
        if chunk_end < text_len:
            # Look for sentence endings: . ! ? followed by space or newline
            # Search backward from chunk_end (max 500 chars back)
            search_start = max(chunk_end - 500, current_pos)
            chunk_text = text[search_start:chunk_end]
            
            # Find last sentence boundary
            sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
            best_break = -1
            
            for ending in sentence_endings:
                pos = chunk_text.rfind(ending)
                if pos > best_break:
                    best_break = pos
            
            if best_break != -1:
                # Break after sentence ending (include the punctuation + space)
                chunk_end = search_start + best_break + 2
            # else: No sentence boundary found, use hard break at 4800
        
        # Extract chunk
        chunk = text[current_pos:chunk_end]
        chunks.append(chunk)
        
        # Move to next chunk
        current_pos = chunk_end
    
    return chunks
```

**Key Features:**
- ✅ Max 4800 chars per chunk
- ✅ Break at sentence boundaries (. ! ?)
- ✅ Search backward max 500 chars for boundary
- ✅ Fallback to hard break if no boundary found
- ✅ Simple, no HTML parsing (Phase C)

### HTML Tag Preservation (Phase C)

**Phase B:** Not implemented (hard break may split tags)  
**Phase C:** Add tag-aware splitting

```python
# Phase C: Check if chunk_end is inside HTML tag
if is_inside_html_tag(text, chunk_end):
    # Move chunk_end to after closing tag
    chunk_end = find_next_tag_close(text, chunk_end)
```

**Deferred to Phase C** because:
- Adds complexity (HTML parsing)
- Phase B tests will reveal if critical issue
- User can proceed with 99% correct results (most breaks are outside tags)

---

## Progress Tracking Design

### Progress Callback Mechanism

**Signature:**
```python
def translate_text_chunked(
    text: str,
    from_lang: str = 'auto',
    to_lang: str = 'pt',
    progress_callback: Optional[Callable[[int, int, int, str], None]] = None
) -> TranslationResult:
    """
    Translate text with automatic chunking.
    
    Args:
        text: Text to translate
        from_lang: Source language code
        to_lang: Target language code
        progress_callback: Function(current_chunk, total_chunks, percentage, status_msg)
    
    Returns:
        TranslationResult with concatenated translation
    """
```

**Callback Parameters:**
- `current_chunk` (int): Current chunk number (1-based)
- `total_chunks` (int): Total number of chunks
- `percentage` (int): Progress percentage (0-100)
- `status_msg` (str): Human-readable status

**Example Callback:**
```python
def on_progress(current: int, total: int, percentage: int, status: str):
    print(f"[{'=' * (percentage // 5)}>{' ' * (20 - percentage // 5)}] {percentage}%")
    print(f"Chunk {current}/{total}: {status}")

# Output:
# [====>                ] 25%
# Chunk 3/12: Translating...
```

### Status Messages

```python
# Calculating chunks
"Preparing translation... (Analyzing document)"

# Translating chunk N
f"Translating chunk {current}/{total}... ({len(chunk)} chars)"

# Between chunks (brief pause for rate limiting)
f"Chunk {current}/{total} complete, continuing..."

# Completion
"Translation complete! (Processed {total} chunks)"
```

---

## Error Handling Strategy

### User Requirement: Fail Fast

**Policy:** Any chunk failure → abort entire translation

```python
for i, chunk in enumerate(chunks, start=1):
    result = self._translate_request(chunk, from_lang, to_lang)
    
    if not result.success:
        # Fail fast - return error immediately
        return TranslationResult(
            success=False,
            error_message=f"Translation failed at chunk {i}/{len(chunks)}: {result.error_message}"
        )
    
    translated_chunks.append(result.translated_text)
    progress_callback(i, len(chunks), ...)
```

**Rationale:**
- Partial translation is useless (missing middle section)
- User wants full document or nothing
- Phase C can add partial result recovery if needed

### Retry Mechanism

**Per-Chunk Retries:** Keep existing 3-attempt retry in `_translate_request()`

```python
# Inside translate_text_chunked loop
for attempt in range(3):
    result = self._translate_request(chunk, from_lang, to_lang)
    if result.success:
        break
    
    if attempt < 2:
        time.sleep(1.0 * (attempt + 1))  # Exponential backoff

if not result.success:
    # Failed after 3 attempts - abort all
    return TranslationResult(...)
```

**Chunk-Level vs. Document-Level:**
- Chunk retry: 3 attempts per chunk (existing logic)
- Document retry: No retry at document level (user can retry manually)

---

## Implementation Plan (Phase B)

### B.1: Design ✅ (This document)

**Deliverables:**
- [x] Algorithm design
- [x] Progress callback API
- [x] Error handling strategy
- [x] This documentation

### B.2: Implement Chunking (45 min)

**File:** `src/translation/google_translate.py`

**New Method:** `translate_text_chunked()`
- Split text into chunks (4800 chars, sentence boundaries)
- Translate each chunk sequentially
- Invoke progress callback
- Concatenate results
- Handle errors (fail fast)

**Modified Method:** `translate_text()` (keep for backward compatibility)
- Add size check: if len(text) > 4500, call `translate_text_chunked()`
- Else, use existing single-request logic
- Automatic chunking transparent to caller

**Lines:** ~100 lines new code

### B.3: Add Progress Callback (30 min)

**File:** `src/gui/google_translate_dock.py`

**Modified Method:** `_start_translation()`
- Pass progress callback to API
- Connect to existing progress bar + status label

**Callback Implementation:**
```python
def _on_chunk_progress(self, current: int, total: int, percentage: int, status: str):
    self.progress_bar.setValue(percentage)
    
    # Progress bar text: [====> ] 50% (Page 5/10)
    bar_text = f"Chunk {current}/{total}"
    
    # Status label: Translating chunk 5 of 10... (2341 chars)
    self.lbl_status.setText(status)
```

**Lines:** ~20 lines

### B.4: Update TranslationWorker (30 min)

**File:** `src/gui/google_translate_dock.py`

**Class:** `TranslationWorker` (QThread subclass)

**New Signal:** `chunk_progress = pyqtSignal(int, int, int, str)`

**Modified Method:** `run()`
- Pass callback to `translate_text()` / `translate_text_chunked()`
- Emit `chunk_progress` signal in callback
- Existing signals remain unchanged

**Lines:** ~15 lines

### B.5: Testing (60 min)

**Test Files:**
- Small file (test_table_COM8.docx): 1 chunk, verify no regression
- Medium file (CAIT docx): 2-3 chunks, verify progress display
- Large file (Aula 07.docx): 50+ chunks, verify HTTP 413 fix

**Manual Tests:**
1. Load small file → Translate → No progress (single chunk)
2. Load medium file → Translate → Progress bar animates
3. Load large file → Translate → Success (no HTTP 413)
4. Simulate error → Verify fail-fast behavior

---

## Performance Estimation

### Chunk Count Calculation

**Formula:** `num_chunks = ceil(document_size / 4800)`

**Examples:**
| Document | Size | Chunks | Time (3s/chunk) |
|----------|------|--------|-----------------|
| Small | 2KB | 1 | 3s |
| Medium | 20KB | 5 | 15s |
| Large (Aula 07) | 200KB | 42 | 126s (~2 min) |
| Huge | 500KB | 105 | 315s (~5 min) |

**Network Overhead:**
- Single request: 1-3 seconds
- Multi-chunk: 1-3 seconds × num_chunks + rate limiting delays

### Rate Limiting

**Current:** 1 second delay between retries (exponential backoff)

**Phase B:** Add inter-chunk delay (0.5s) to avoid rate limiting

```python
# After successful chunk translation
time.sleep(0.5)  # Rate limiting between chunks
```

**Impact:** +0.5s × num_chunks (e.g., +21s for 42 chunks)

---

## Edge Cases

### 1. Very Long Sentence (> 4800 chars)

**Problem:** No sentence boundary within 500 char search window  
**Solution:** Hard break at 4800 chars (fallback)  
**Impact:** May break mid-sentence, acceptable for Phase B

**Phase C Improvement:** Semantic splitting (break at paragraph boundary)

### 2. Single HTML Tag > 4800 Chars

**Example:** `<table data-table="TBL001">[10,000 cells]</table>`

**Problem:** Breaking inside tag corrupts HTML  
**Solution (Phase B):** Allow break, document may fail reconstruction  
**Solution (Phase C):** Semantic splitting (extract table, translate, reinsert)

**Mitigation:** Most tables < 4800 chars, low risk for Phase B

### 3. Empty Chunks

**Problem:** Splitting algorithm produces empty chunk (e.g., text ends exactly at boundary)  
**Solution:** Skip empty chunks in loop

```python
chunks = [c for c in chunks if c.strip()]  # Filter empty
```

### 4. Progress Callback Exceptions

**Problem:** User callback throws exception  
**Solution:** Wrap in try-except, continue translation

```python
if progress_callback:
    try:
        progress_callback(current, total, percentage, status)
    except Exception:
        pass  # Don't let callback errors abort translation
```

---

## Backward Compatibility

### Existing `translate_text()` Behavior

**Before Phase B:**
```python
result = api.translate_text("Long text...", "auto", "en")
# Single request, may fail with HTTP 413
```

**After Phase B:**
```python
result = api.translate_text("Long text...", "auto", "en")
# Automatic chunking if len(text) > 4500
# Transparent to caller, same return type
```

**API Contract:**
- ✅ Same method signature
- ✅ Same return type (`TranslationResult`)
- ✅ Same success/error behavior
- ✅ No breaking changes

### New `translate_text_chunked()` API

**Optional API** for callers who want explicit control:

```python
def on_progress(current, total, pct, status):
    print(f"{pct}% - {status}")

result = api.translate_text_chunked(
    text="Very long text...",
    from_lang="auto",
    to_lang="en",
    progress_callback=on_progress
)
```

**Use Cases:**
- GUI with progress bar (Google Translate dock)
- CLI with progress output
- Batch processing with logging

---

## Testing Strategy

### Unit Tests (Phase B.5)

**File:** `tests/com8/test_chunking_COM8.py`

**Test Cases:**
1. `test_split_small_text()` - Text < 4800 chars → 1 chunk
2. `test_split_exact_boundary()` - Text = 4800 chars → 1 chunk
3. `test_split_large_text()` - Text = 10,000 chars → 3 chunks
4. `test_sentence_boundary()` - Break at `. ` not mid-word
5. `test_no_boundary_found()` - Hard break fallback
6. `test_multiple_punctuation()` - Prefer `.` over `,`
7. `test_empty_chunks_filtered()` - No empty chunks returned

**Mock Translation:** Use fake API to avoid network calls

### Integration Tests (Manual)

**Test Files:**
1. **test_table_COM8.docx** (2KB) - 1 chunk baseline
2. **CAIT Trabalho.docx** (20KB) - 5 chunks progress test
3. **Aula 07.docx** (953KB) - 42+ chunks HTTP 413 fix

**GUI Testing:**
1. Load file → Check chunk count in status
2. Translate → Watch progress bar animate
3. Verify translated output matches original structure
4. Retry failed translation → Verify state cleared (Phase A)

---

## Success Criteria

### Phase B Complete When:

- [x] B.1: Design documented (this file)
- [ ] B.2: Chunking algorithm implemented
- [ ] B.3: Progress callback working in GUI
- [ ] B.4: TranslationWorker updated
- [ ] B.5: All tests passing
- [ ] Large file (Aula 07.docx) translates successfully
- [ ] No HTTP 413 errors
- [ ] Progress bar displays correctly
- [ ] Documentation updated

### Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Max chunk size | 4800 chars | ⏳ Pending |
| Sentence boundary | 90%+ breaks | ⏳ Pending |
| Progress accuracy | ±5% | ⏳ Pending |
| Large file success | 100% | ⏳ Pending |
| Regression (small files) | 0 failures | ⏳ Pending |

---

## Next Steps

1. **Immediate:** Implement `split_into_chunks()` function (B.2)
2. **Then:** Add `translate_text_chunked()` method (B.2)
3. **Then:** Update GUI progress handling (B.3)
4. **Then:** Test with Aula 07.docx (B.5)
5. **Finally:** Document Phase B completion

**Estimated Time:** 2-3 hours total for Phase B

---

**Phase B.1 Status:** ✅ **COMPLETE** - Design Documented  
**Next:** Phase B.2 - Implement Chunking Algorithm
