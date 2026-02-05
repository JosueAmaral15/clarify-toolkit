# File Explorer Memory Consumption Investigation
**Date:** 2026-01-09  
**Reporter:** User  
**Issue:** High memory consumption during File Explorer search operations

## Problem Description

User reported excessive memory consumption when performing searches in File Explorer. The application becomes slow and uses significant RAM during search operations.

## Root Cause Analysis

### Investigation Steps

1. **Reviewed search execution code** - `src/core/file_explorer_executor.py`
2. **Analyzed data structures** - `SearchMatch` and `SearchResult` classes
3. **Identified memory leak pattern** - Lines 430-437

### Root Cause: Excessive Match Data Storage

**File:** `src/core/file_explorer_executor.py`  
**Lines:** 430-437

```python
matches.append(
    SearchMatch(
        line=line_num,
        col=col,
        snippet=line_text,           # ⚠️ STORES ENTIRE LINE
        context_before=lines[line_num - 2] if line_num > 1 else "",  # ⚠️ PREVIOUS LINE
        context_after=lines[line_num] if line_num < len(lines) else "",   # ⚠️ NEXT LINE
    )
)
```

**Problem:** For every match found, we store:
- `snippet`: The complete line containing the match (can be 500+ chars)
- `context_before`: The complete previous line (can be 500+ chars)
- `context_after`: The complete next line (can be 500+ chars)

### Impact Calculation

**Example scenario:** Search for "import" in a Python project
- **Files scanned:** 500 files
- **Matches per file:** 20 (average)
- **Total matches:** 10,000
- **Line length:** 80 chars (average)
- **Memory per match:** 80 * 3 = 240 bytes (just for text)
- **Total text memory:** 10,000 * 240 = 2.4 MB

With Python object overhead (dict, dataclass, references), this becomes **~10-15 MB** just for match text.

**Worse case:** Search for "the" in documentation files
- **Total matches:** 100,000+
- **Memory consumption:** 100-150 MB or more

### Additional Issues Found

1. **No limit on total matches across all files** - Only per-file limit (10,000)
2. **All file content loaded into memory** - Line 300: `text = read_text(file_info.path)`
3. **No streaming/chunking** - All results stored before display
4. **Context lines stored but rarely used** - UI might not even display them

## Current Safeguards

✅ **MAX_MATCHES_PER_FILE = 10,000** (line 416)
- Prevents catastrophic memory usage per file
- But doesn't limit total matches across all files

## Memory Usage Patterns

### Low Memory (Good)
- Search for unique strings: "MySpecificClassName"
- Result: 10-50 matches = ~50 KB

### Medium Memory (Acceptable)
- Search for function names: "process_data"
- Result: 500-1,000 matches = ~500 KB - 1 MB

### High Memory (Problem) ⚠️
- Search for common words: "import", "return", "def"
- Result: 10,000-50,000 matches = **10-50 MB**

### Critical Memory (Crash Risk) 🔴
- Search for single letters: "a", "e"
- Search in large codebase (1000+ files)
- Result: 100,000+ matches = **100+ MB** (can crash on low-memory systems)

## Proposed Solutions

### Solution 1: Truncate Snippet Text (Quick Fix) ⚡
**Effort:** 5 minutes  
**Impact:** 60-80% memory reduction

```python
MAX_SNIPPET_LENGTH = 200  # Characters

matches.append(
    SearchMatch(
        line=line_num,
        col=col,
        snippet=line_text[:MAX_SNIPPET_LENGTH] if len(line_text) > MAX_SNIPPET_LENGTH else line_text,
        context_before="",  # Remove context (rarely used)
        context_after="",   # Remove context (rarely used)
    )
)
```

**Pros:**
- Simple 1-line change
- Immediate impact
- No breaking changes

**Cons:**
- Still stores full snippets up to 200 chars
- Loses context lines (might be needed for UI)

---

### Solution 2: Store Only Match Position (Minimal Storage) 🎯
**Effort:** 30 minutes  
**Impact:** 95% memory reduction

```python
@dataclass
class SearchMatch:
    """Lightweight match information - stores position only."""
    line: int
    col: int
    match_length: int  # NEW: Length of matched text
    
    # Remove: snippet, context_before, context_after
    # These can be retrieved on-demand when displaying results
```

**Changes required:**
1. Remove `snippet`, `context_before`, `context_after` from `SearchMatch`
2. Add `match_length` field to know how much to highlight
3. Update UI to read file on-demand when displaying match details
4. Cache recently viewed file contents (LRU cache)

**Pros:**
- 95%+ memory reduction
- Scales to millions of matches
- Fast search operations

**Cons:**
- Requires UI refactor
- Need to re-read files when viewing details
- More disk I/O (but still fast with caching)

---

### Solution 3: Limit Total Matches (Safety Net) 🛡️
**Effort:** 10 minutes  
**Impact:** Prevents crashes

```python
MAX_TOTAL_MATCHES = 50000  # Across ALL files

total_match_count = 0

for idx, file_info in enumerate(files_to_search, 1):
    matches = self._search_in_text(text, content_query, search_options)
    
    total_match_count += len(matches)
    if total_match_count > MAX_TOTAL_MATCHES:
        self.error.emit(f"Maximum total matches reached ({MAX_TOTAL_MATCHES}). Refine your search.")
        break
```

**Pros:**
- Prevents memory exhaustion
- Clear user feedback
- Works with existing code

**Cons:**
- Arbitrary limit feels restrictive
- User might miss legitimate results

---

### Solution 4: Streaming Results (Advanced) 🚀
**Effort:** 2-4 hours  
**Impact:** Constant memory usage

Use Qt signals to emit results as they're found, instead of accumulating:

```python
# Emit each match immediately
self.match_found.emit(file_info, match)

# Don't store in list
# UI appends to table incrementally
```

**Pros:**
- Constant memory usage
- Immediate visual feedback
- True streaming architecture

**Cons:**
- Major refactor required
- Changes UI threading model
- Complex implementation

---

## Recommended Approach

### Phase 1: Quick Fixes (Today) ⚡
1. **Implement Solution 3** - Add global match limit (10 min)
2. **Implement Solution 1** - Truncate snippets to 200 chars (5 min)
3. **Remove context lines** - Set to empty strings (1 min)

**Total effort:** ~20 minutes  
**Memory reduction:** 70-80%  
**Risk:** Very low

### Phase 2: Optimal Solution (Next Session) 🎯
1. **Implement Solution 2** - Store only positions
2. **Add LRU cache** for file content when viewing
3. **Update UI** to load details on-demand

**Total effort:** 1-2 hours  
**Memory reduction:** 95%+  
**Risk:** Medium (requires testing)

### Phase 3: Advanced (Future) 🚀
1. **Implement Solution 4** - Streaming architecture
2. Requires full UI refactor
3. Best for v3.0 release

## Testing Strategy

1. **Create test case** with common search terms
2. **Measure memory** before/after using `memory_profiler`
3. **Search patterns to test:**
   - Common: "import", "return", "the"
   - Rare: "MySpecificClassName123"
   - Single char: "a"
4. **Verify limits** work correctly
5. **Check UI** still displays results properly

## Success Criteria

- ✅ Memory usage < 50 MB for 10,000 matches
- ✅ No crashes on searches with 100,000+ matches
- ✅ Search remains fast (< 5 seconds for typical project)
- ✅ UI remains responsive during search
- ✅ Results still display correctly

## Files to Modify

1. **`src/core/file_explorer_executor.py`** (lines 30-38, 414-437)
   - Update `SearchMatch` dataclass
   - Add global match limit
   - Truncate snippets

2. **UI files** (if doing Phase 2)
   - Display logic for match details
   - On-demand file reading

## Additional Observations

- **Current code has good practices:**
  - Per-file limit (10,000)
  - Cancellation support
  - Error handling
  
- **Missing safeguards:**
  - No global match limit
  - No memory usage monitoring
  - No progress indication for large result sets

## References

- **File:** `src/core/file_explorer_executor.py`
- **Class:** `UnifiedFileExplorerExecutor`
- **Method:** `_search_in_text()` (lines 381-454)
- **Dataclass:** `SearchMatch` (lines 30-38)

---

**Status:** ⏳ INVESTIGATION COMPLETE - AWAITING USER DECISION  
**Priority:** 🔴 HIGH (affects user experience)  
**Next Step:** Implement Phase 1 quick fixes
