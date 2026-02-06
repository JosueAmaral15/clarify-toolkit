# TOCTOU Fix Verification - Cancel Button Crash

**Date:** 2026-02-06  
**Branch:** COM3-documentation-study  
**Commit:** 7809b6f  
**Issue:** AttributeError: 'NoneType' has no attribute 'setLabelText' at line 1031

---

## Problem Analysis

### The Crash
```
Traceback (most recent call last):
  File ".../unified_text_to_json_dock.py", line 1031, in _on_extraction_progress_detailed
    self._extraction_progress.setLabelText(f"[{current}/{total}] {message}")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'setLabelText'
```

### Root Cause: TOCTOU Race Condition

**Time-Of-Check-Time-Of-Use** vulnerability:

```python
# Thread A (Signal Handler)
if self._extraction_progress is not None:  # Check passes
    self._extraction_progress.setMaximum(total)    # Access 1 - OK
    self._extraction_progress.setValue(current)    # Access 2 - OK
    # <-- Thread B runs here: self._extraction_progress = None
    self._extraction_progress.setLabelText(...)    # Access 3 - CRASH!
```

**Timeline:**
1. Thread A: Check passes (`_extraction_progress` is not None)
2. Thread A: Call setMaximum() - OK
3. Thread A: Call setValue() - OK
4. Thread B: Set `_extraction_progress = None` (cleanup/cancel)
5. Thread A: Call setLabelText() - **CRASH!** (object is now None)

### Why Previous Fixes Failed

**Attempt 1: Cleanup Flag** (commit 560fa4e)
- Added `_extraction_cleaning_up` flag
- Check flag before accessing object
- **Failed:** Check passes, then object becomes None before use

**Attempt 2: blockSignals()** (commit 3239b7d)
- Used `blockSignals(True)` to stop signal delivery
- **Failed:** Signals already in Qt event queue still delivered

**Attempt 3: disconnect()** (commit ecc8eb6)
- Disconnected signals before cleanup
- **Failed:** Doesn't clear queued signals

**All failed because:** They don't prevent the TOCTOU race between check and use.

---

## The Solution: Cache Object Reference

### Fix Pattern
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    """Handle detailed progress updates from extraction worker."""
    if self._extraction_cleaning_up:
        return
    
    # Cache reference locally - ATOMIC operation
    progress = self._extraction_progress
    
    # Check the CACHED reference (not instance variable)
    if progress is None:
        return
    
    # Use CACHED reference for all operations
    try:
        progress.setMaximum(total)      # Safe
        progress.setValue(current)       # Safe
        progress.setLabelText(...)       # Safe
    except RuntimeError:
        pass  # Qt object was deleted (rare edge case)
```

### Why This Works

1. **Single Atomic Access:** `progress = self._extraction_progress` is atomic
2. **Local Reference:** We now own a reference to the object
3. **Thread-Safe:** Even if another thread sets `self._extraction_progress = None`, our local `progress` variable still holds a valid reference
4. **Multiple Operations Safe:** All operations use the same cached reference

### Python Reference Counting
- When we assign `progress = self._extraction_progress`, Python increments the object's reference count
- Even if instance variable is set to None, the object won't be garbage collected while we hold our local reference
- This makes the pattern thread-safe

---

## Implementation Details

### Files Modified
- `src/gui/unified_text_to_json_dock.py`

### Methods Fixed

#### 1. `_on_extraction_progress()` (Line ~1017)
**Before:**
```python
def _on_extraction_progress(self, message: str):
    if self._extraction_cleaning_up:
        return
    if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
        self._extraction_progress.setLabelText(message)
```

**After:**
```python
def _on_extraction_progress(self, message: str):
    if self._extraction_cleaning_up:
        return
    
    progress = self._extraction_progress  # Cache once
    if progress is None:
        return
    
    try:
        progress.setLabelText(message)
    except RuntimeError:
        pass
```

#### 2. `_on_extraction_progress_detailed()` (Line ~1024)
**Before:**
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    if self._extraction_cleaning_up:
        return
    if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
        self._extraction_progress.setMaximum(total)       # Access 1
        self._extraction_progress.setValue(current)        # Access 2
        self._extraction_progress.setLabelText(...)        # Access 3 - CRASH HERE
```

**After:**
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    if self._extraction_cleaning_up:
        return
    
    progress = self._extraction_progress  # Cache once
    if progress is None:
        return
    
    try:
        progress.setMaximum(total)       # Safe - using cached ref
        progress.setValue(current)        # Safe - using cached ref
        progress.setLabelText(...)        # Safe - using cached ref
    except RuntimeError:
        pass
```

---

## Testing

### Synthetic Test
Created test demonstrating the fix: `/tmp/test_toctou_fix.py`

**Test Results:**
```
=== OLD BROKEN Pattern ===
Signal handler: ✗ CRASHED: 'NoneType' object has no attribute 'setLabelText'

=== NEW FIXED Pattern ===
Signal handler: ✓ Completed successfully
```

### Real-World Test Plan
1. Start Clarify application
2. Open Text to JSON Converter tool
3. Browse to a large directory (100+ .tsx/.jsx files)
4. Click "Run Extraction"
5. **Immediately click "Cancel" button** while progress dialog shows
6. Expected: Clean cancellation without crashes

### Expected Behavior
- ✓ Progress updates show normally
- ✓ Cancel button stops extraction
- ✓ No AttributeError crashes
- ✓ Progress dialog closes cleanly
- ✓ UI remains responsive
- ✓ Thread shuts down properly

---

## Verification Checklist

- [x] **Step 1:** Fixed `_on_extraction_progress()` with cached reference
- [x] **Step 2:** Fixed `_on_extraction_progress_detailed()` with cached reference
- [x] **Step 3:** Verified `_on_extraction_finished()` doesn't need fix
- [x] **Step 4:** Checked File Explorer pattern (less safe than ours)
- [x] **Synthetic test:** Passes (old crashes, new works)
- [x] **Code review:** Pattern correctly implemented
- [x] **Commit message:** Detailed explanation of fix
- [ ] **Real-world test:** Pending user verification

---

## Lessons Learned

### TOCTOU is Subtle
- Even with checks, race conditions can occur
- Multiple accesses to shared state are dangerous
- Time gap between check and use is the vulnerability

### Thread Safety Patterns
- **Bad:** Multiple accesses to instance variable
- **Good:** Single access, cache locally, use cached reference
- **Best:** Use locks/mutexes for critical sections

### Qt Signal Handling
- `disconnect()` doesn't clear event queue
- `blockSignals()` doesn't prevent already-queued signals
- Defensive coding with cached references is necessary

### Debugging Race Conditions
1. Look for multiple accesses to same object
2. Identify which line actually crashes (not just first access)
3. Add synthetic delays to reproduce race condition
4. Cache references to prevent TOCTOU

---

## Related Commits

- `7809b6f` - **fix(jsx-extraction): cache progress reference to prevent TOCTOU crash** ✅ FINAL FIX
- `3239b7d` - fix(jsx-extraction): block Qt signals to prevent queued signal delivery
- `560fa4e` - fix(jsx-extraction): add cleanup flag to prevent cancel crash
- `ecc8eb6` - fix(jsx-extraction): prevent race condition crashes in progress handlers
- `6909e01` - fix(jsx-extraction): set progress dialog width constraints

---

## Status

**FIX APPLIED:** ✅  
**READY FOR TESTING:** ✅  
**PATTERN VERIFIED:** ✅ (synthetic test passes)  
**AWAITING:** Real-world user verification

---

**Next Steps:**
1. User tests Cancel button in real application
2. If crashes persist, add debug logging per action plan
3. Consider applying same pattern to File Explorer for consistency
