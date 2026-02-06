# Action Plan: Fix Cancel Button Crash (Manual Debug)

## Problem Analysis

### What's Happening
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    if self._extraction_cleaning_up:
        return  # Check passes - flag is False
    if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
        # ✓ Check passes - object exists
        self._extraction_progress.setMaximum(total)        # Line 1029 - OK
        self._extraction_progress.setValue(current)        # Line 1030 - OK
        self._extraction_progress.setLabelText(f"...")     # Line 1031 - CRASH!
        # ✗ By this line, another thread set _extraction_progress = None
```

### Root Cause: TOCTOU (Time-Of-Check-Time-Of-Use)
1. Thread A (Signal Handler): Checks `_extraction_progress is not None` → True
2. Thread B (Cancel/Cleanup): Sets `_extraction_progress = None`
3. Thread A: Tries to call `setLabelText()` → **CRASH**

**The real issue:** Making **3 separate accesses** to `self._extraction_progress` without caching it locally!

## Solution: Cache Object Reference Locally

### Fix Pattern
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    """Handle detailed progress updates from extraction worker."""
    # Exit early if cleaning up
    if self._extraction_cleaning_up:
        return
    
    # Cache reference ONCE - atomic operation
    progress = self._extraction_progress
    
    # Check the cached reference
    if progress is None:
        return
    
    # Now safe to make multiple calls - we own a reference
    try:
        progress.setMaximum(total)
        progress.setValue(current)
        progress.setLabelText(f"[{current}/{total}] {message}")
    except RuntimeError:
        # Qt object was deleted while we had reference
        pass
```

## Step-by-Step Manual Fix

### Step 1: Fix `_on_extraction_progress()`
**File:** `src/gui/unified_text_to_json_dock.py`  
**Line:** ~1017

**Current code:**
```python
def _on_extraction_progress(self, message: str):
    """Handle progress updates from extraction worker."""
    if self._extraction_cleaning_up:
        return
    if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
        self._extraction_progress.setLabelText(message)
```

**Fixed code:**
```python
def _on_extraction_progress(self, message: str):
    """Handle progress updates from extraction worker."""
    if self._extraction_cleaning_up:
        return
    
    # Cache reference locally (atomic)
    progress = self._extraction_progress
    if progress is None:
        return
    
    try:
        progress.setLabelText(message)
    except RuntimeError:
        pass  # Qt object deleted
```

### Step 2: Fix `_on_extraction_progress_detailed()`
**File:** `src/gui/unified_text_to_json_dock.py`  
**Line:** ~1024

**Current code:**
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    """Handle detailed progress updates from extraction worker."""
    if self._extraction_cleaning_up:
        return
    if hasattr(self, '_extraction_progress') and self._extraction_progress is not None:
        self._extraction_progress.setMaximum(total)
        self._extraction_progress.setValue(current)
        self._extraction_progress.setLabelText(f"[{current}/{total}] {message}")
```

**Fixed code:**
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    """Handle detailed progress updates from extraction worker."""
    if self._extraction_cleaning_up:
        return
    
    # Cache reference locally (atomic)
    progress = self._extraction_progress
    if progress is None:
        return
    
    try:
        progress.setMaximum(total)
        progress.setValue(current)
        progress.setLabelText(f"[{current}/{total}] {message}")
    except RuntimeError:
        pass  # Qt object deleted
```

### Step 3: Fix `_on_extraction_finished()`
**File:** `src/gui/unified_text_to_json_dock.py`  
**Line:** ~1033

Check if this method also accesses `_extraction_progress` multiple times. If yes, apply same pattern:
1. Cache reference: `progress = self._extraction_progress`
2. Check cached reference: `if progress is None: return`
3. Use cached reference in try/except block

### Step 4: Verify Pattern in File Explorer (Working Reference)
**File:** `src/gui/file_explorer_dock.py`  
**Search for:** Similar progress handlers

Look for how File Explorer handles this - it's working correctly!

```bash
cd /home/josue/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify-COM3-study
grep -n "_progress_dialog" src/gui/file_explorer_dock.py | grep "def _on"
```

Copy the pattern they use.

## Why This Works

### The Problem with Multiple Accesses
```python
# WRONG - 3 separate accesses
if self._extraction_progress is not None:  # Access #1 - OK
    self._extraction_progress.setMaximum(total)    # Access #2 - OK
    self._extraction_progress.setValue(current)    # Access #3 - OK  
    self._extraction_progress.setLabelText(msg)    # Access #4 - CRASH!
    # Another thread set it to None between accesses!
```

### The Solution with Local Reference
```python
# CORRECT - Single atomic access
progress = self._extraction_progress  # Access #1 - Get reference
if progress is None:  # Check our copy
    return
# Now we hold a Python reference - safe even if other thread sets to None
progress.setMaximum(total)    # Safe
progress.setValue(current)    # Safe
progress.setLabelText(msg)    # Safe
```

**Key insight:** Python assignment is atomic. Once we have a local reference, we "own" that object until we're done, even if the instance variable is set to None by another thread.

## Testing Steps

1. **Apply the fixes** to all signal handlers
2. **Rebuild/restart** the application
3. **Start extraction** on large directory (100+ files)
4. **Click Cancel** button immediately
5. **Expected result:** Clean cancellation, no crashes
6. **Check logs:** No AttributeError crashes

## Additional Investigation (If Still Crashes)

### Check Thread Safety of Cleanup
**File:** `src/gui/unified_text_to_json_dock.py`  
**Method:** `_cleanup_extraction_thread()`

Look for:
- Is cleanup called from UI thread or worker thread?
- Are there multiple paths that can call cleanup simultaneously?
- Is there a lock/mutex protecting cleanup?

### Add Debug Logging
```python
def _on_extraction_progress_detailed(self, current: int, total: int, message: str):
    import threading
    print(f"[{threading.current_thread().name}] progress_detailed called")
    
    if self._extraction_cleaning_up:
        print(f"[{threading.current_thread().name}] Ignoring - cleaning up")
        return
    
    progress = self._extraction_progress
    print(f"[{threading.current_thread().name}] progress object: {progress}")
    
    if progress is None:
        print(f"[{threading.current_thread().name}] Ignoring - progress is None")
        return
    
    try:
        progress.setMaximum(total)
        progress.setValue(current)
        progress.setLabelText(f"[{current}/{total}] {message}")
        print(f"[{threading.current_thread().name}] Updated successfully")
    except RuntimeError as e:
        print(f"[{threading.current_thread().name}] RuntimeError: {e}")
```

Run test and watch console to see thread interleaving.

## Why My Previous Fixes Failed

1. **Cleanup flag approach:** Flag check passes, then object becomes None before use
2. **blockSignals approach:** Doesn't work for already-queued signals in Qt event loop
3. **disconnect approach:** Disconnect doesn't clear Qt's event queue

**The only solution:** Cache the object reference locally so it can't become None mid-operation.

## Success Criteria

- ✅ No AttributeError crashes when clicking Cancel
- ✅ No warnings about disconnect failures
- ✅ Clean shutdown of extraction thread
- ✅ Progress dialog closes properly
- ✅ UI remains responsive after cancel

## Commit Message Template

```
fix(jsx-extraction): cache progress dialog reference to prevent TOCTOU crash

Problem:
- Crash on cancel: 'NoneType' has no attribute 'setLabelText'
- Line 1031 in _on_extraction_progress_detailed
- Happening at line 1031, not 1029 (3rd access to object)

Root cause:
- TOCTOU race condition (Time-Of-Check-Time-Of-Use)
- Signal handler checks: _extraction_progress is not None
- Makes 3 separate accesses to _extraction_progress
- Cancel thread sets _extraction_progress = None between accesses
- Third access crashes because object is now None

Why previous fixes failed:
- Cleanup flag: Check passes, then object nullified before use
- blockSignals: Doesn't clear already-queued Qt signals
- disconnect: Doesn't prevent queued signal delivery

Solution:
- Cache object reference locally ONCE (atomic operation)
- Check cached reference (not instance variable)
- Use cached reference for all operations
- Even if instance var becomes None, we hold a valid reference

Changes:
- _on_extraction_progress: Cache progress locally
- _on_extraction_progress_detailed: Cache progress locally
- Added try/except for RuntimeError (Qt object deleted)
- Single atomic access to instance variable

Benefits:
- Thread-safe signal handling
- No more TOCTOU races
- Clean cancellation guaranteed
```

---

**Good luck with the fix! This is the real root cause.**
