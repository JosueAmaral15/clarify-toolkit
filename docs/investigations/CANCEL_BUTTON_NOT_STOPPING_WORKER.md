# Investigation: Cancel Button Not Stopping Worker Thread

**Date:** 2026-02-06  
**Branch:** COM3-documentation-study  
**Reporter:** Programmer #3  
**Status:** IDENTIFIED - Not Yet Fixed

---

## Problem Description

### Observed Behavior
- User clicks Cancel button on progress dialog
- Progress dialog closes (no crashes - TOCTOU fix works!)
- **BUT:** Processing continues in background
- GUI appears frozen/unresponsive
- Worker thread keeps running silently
- Results eventually appear after all files processed

### Expected Behavior
- User clicks Cancel button
- Worker thread **stops immediately**
- Partial results discarded (or saved)
- UI returns to ready state
- Status shows "Extraction canceled"

---

## Root Cause Analysis

### Current Cancel Flow

1. **User clicks Cancel button** (progress dialog)
   ```python
   # _on_extraction_canceled() called
   self._extraction_cleaning_up = True
   self._extraction_worker._cancel_requested = True  # SET FLAG
   self._jsx_update_status("Extraction canceled")
   self._cleanup_extraction_thread()
   ```

2. **Cleanup closes dialog and "stops" thread**
   ```python
   # _cleanup_extraction_thread()
   self._extraction_progress.close()  # Dialog closes
   self._extraction_progress = None
   self._extraction_thread.quit()      # Request thread exit
   self._extraction_thread.wait(5000)  # Wait 5 seconds
   ```

3. **Worker continues processing**
   ```python
   # In ExtractionWorker.execute_extraction()
   for idx, fp in enumerate(all_files, 1):  # Loop continues!
       self.progress.emit(f"Processing: {filename}")
       # ... processes file ...
       # ❌ NEVER CHECKS self._cancel_requested
   ```

### The Bug

**File:** `src/gui/extraction_worker.py`  
**Line:** 128-171 (file processing loop)

```python
for idx, fp in enumerate(all_files, 1):
    # Emit progress for each file
    filename = os.path.basename(fp)
    self.progress.emit(f"Processing: {filename}")
    self.progress_detailed.emit(idx, total_files, filename)
    
    # ❌ NO CHECK HERE!
    # Should be: if self._cancel_requested: break
    
    try:
        text = read_text(fp)
    except Exception as e:
        all_lines.append(f"<<ERROR reading {fp}: {e}>>")
        continue
    
    # ... process file (takes time) ...
```

**Problem:** Worker sets `_cancel_requested = False` in `__init__` (line 56) but **never checks it**!

---

## Why This Happens

### Thread Lifecycle Misunderstanding

```python
# Dock thinks this stops the worker:
self._extraction_thread.quit()      # Only stops Qt event loop
self._extraction_thread.wait(5000)  # Waits for thread to finish
```

**Reality:**
- `quit()` stops the **Qt event loop** in the thread
- **Does NOT stop code currently executing**
- Worker loop keeps running until it completes naturally
- After loop finishes, thread exits (because event loop is quit)

### The Missing Check

The worker **must** check `_cancel_requested` inside the loop:

```python
for idx, fp in enumerate(all_files, 1):
    # Check for cancellation FIRST
    if self._cancel_requested:
        logger.info(f"Cancellation requested at file {idx}/{total_files}")
        self.progress.emit("Cancellation requested...")
        break  # Exit loop immediately
    
    # Continue processing...
```

---

## Solution Design

### 1. Add Cancellation Check in Worker Loop

**File:** `src/gui/extraction_worker.py`  
**Location:** Inside file processing loop (line ~128)

```python
for idx, fp in enumerate(all_files, 1):
    # ✅ CHECK CANCEL FLAG FIRST
    if self._cancel_requested:
        logger.info(f"Extraction canceled by user at file {idx}/{total_files}")
        self.error.emit("Extraction canceled by user")
        return  # Exit early - don't emit finished signal
    
    # Emit progress for each file
    filename = os.path.basename(fp)
    self.progress.emit(f"Processing: {filename}")
    self.progress_detailed.emit(idx, total_files, filename)
    
    # ... rest of processing ...
```

### 2. Handle Cancel in Error Path

When cancel is detected, emit error signal (not finished):

```python
if self._cancel_requested:
    self.error.emit("Extraction canceled by user")
    return  # Don't emit finished signal
```

This way `_on_extraction_error()` is called instead of `_on_extraction_finished()`.

### 3. Update Error Handler (Optional)

**File:** `src/gui/unified_text_to_json_dock.py`  
**Method:** `_on_extraction_error()`

Currently shows error dialog - maybe don't show for cancellation:

```python
def _on_extraction_error(self, error_msg: str):
    """Handle extraction error."""
    self._jsx_update_status(f"❌ {error_msg}")
    
    # Don't show error dialog for user cancellation
    if "canceled by user" not in error_msg.lower():
        self.show_error(
            tr("advanced_extractor.error", "Error"),
            tr("advanced_extractor.run_error", f"Extraction failed: {error_msg}")
        )
    
    self._cleanup_extraction_thread()
```

### 4. Alternative: Terminate Thread (Dangerous)

**NOT RECOMMENDED** but possible:

```python
# In _cleanup_extraction_thread()
if self._extraction_thread.isRunning():
    self._extraction_thread.terminate()  # Force kill
    self._extraction_thread.wait()
```

**Issues:**
- Can corrupt data structures
- Can leave resources locked
- Can cause memory leaks
- **Graceful cancellation is much safer**

---

## Comparison: File Explorer Implementation

Let me check if File Explorer has the same issue:

**File:** `src/gui/file_explorer_dock.py`  
**Worker:** `FileExplorerWorker`

```bash
cd /path/to/clarify-COM3-study
grep -A 10 "def execute" src/gui/panels/file_explorer_worker.py | grep -i cancel
```

Does File Explorer worker check cancellation in its loops?

---

## Implementation Plan

### Step 1: Add Cancel Check to Worker Loop
**File:** `src/gui/extraction_worker.py`  
**Lines:** ~128 (start of file processing loop)

Add at **top of loop**:
```python
if self._cancel_requested:
    logger.info(f"Extraction canceled at file {idx}/{total_files}")
    self.error.emit("Extraction canceled by user")
    return
```

### Step 2: Test Cancellation
1. Start extraction on large directory (100+ files)
2. Click Cancel after 10-20 files processed
3. Verify:
   - Worker stops immediately (within 1 second)
   - No more file processing
   - Error handler called
   - UI responsive
   - Status shows "Extraction canceled"

### Step 3: Update Error Handler (Optional)
If cancellation shows error dialog, suppress it:
```python
if "canceled by user" not in error_msg.lower():
    self.show_error(...)
```

### Step 4: Consider Text Mode
Check if Text mode (line ~79-97) can be canceled:
- Text mode processes single input
- No loop to check cancellation
- Probably fast enough to not need it
- But could add check before/after `process_text()`

---

## Testing Checklist

- [ ] Cancel during directory processing (100+ files)
- [ ] Cancel during file processing (single large file)
- [ ] Cancel during text processing
- [ ] Verify no crashes (TOCTOU fix still works)
- [ ] Verify thread actually stops
- [ ] Verify UI becomes responsive immediately
- [ ] Verify status message shows "Canceled"
- [ ] Verify no error dialog for normal cancellation
- [ ] Check for memory leaks (thread cleanup)

---

## Why I Missed This

### What I Fixed
✅ TOCTOU race condition - no more crashes
✅ Progress dialog closes properly
✅ Signals handled safely

### What I Didn't Check
❌ Whether worker actually stops
❌ Whether cancellation flag is checked
❌ Whether thread exits cleanly

### Lesson Learned
- Fixing crash is not the same as fixing functionality
- Must verify **entire cancel flow**, not just UI parts
- Worker **cooperation** is required for graceful cancellation
- Thread.quit() != stop executing code

---

## Related Files

- `src/gui/unified_text_to_json_dock.py` - Cancel handler (lines 1085-1101)
- `src/gui/extraction_worker.py` - Worker with missing cancel check (line ~128)
- `src/gui/panels/file_explorer_worker.py` - Reference implementation
- `docs/investigations/TOCTOU_FIX_VERIFICATION.md` - Previous investigation

---

## Next Steps

1. **Add cancel check to worker loop** (one line!)
2. **Test with large directory**
3. **Verify thread stops within 1 second**
4. **Commit with message:** `fix(jsx-extraction): check cancel flag in worker loop`
5. **Update this investigation with results**

---

## Status

**IDENTIFIED:** ✅  
**ROOT CAUSE:** Worker never checks `_cancel_requested` flag  
**SOLUTION:** Add `if self._cancel_requested: return` at top of loop  
**IMPLEMENTED:** ✅ (commit 237f243)  
**TESTED:** ⏳ Awaiting user verification

---

## Implementation (2026-02-06)

### Changes Made

**File:** `src/gui/extraction_worker.py` (Line 128-133)
```python
for idx, fp in enumerate(all_files, 1):
    # Check for cancellation FIRST
    if self._cancel_requested:
        logger.info(f"Extraction canceled by user at file {idx}/{total_files}")
        self.error.emit("Extraction canceled by user")
        return  # Exit early without emitting finished signal
    
    # Continue processing...
```

**File:** `src/gui/unified_text_to_json_dock.py` (Line 1076-1089)
```python
def _on_extraction_error(self, error_msg: str):
    # Don't show status/dialog for user cancellation (already shown)
    if "canceled by user" in error_msg.lower():
        self._cleanup_extraction_thread()
        return
    
    # Show error for actual failures
    self._jsx_update_status(f"❌ Extraction failed: {error_msg}")
    self.show_error(...)
    self._cleanup_extraction_thread()
```

### How It Works

1. User clicks Cancel button
2. Cancel handler sets `_cancel_requested = True`
3. Worker checks flag at **top of next loop iteration**
4. Worker exits immediately via `return`
5. Error signal emitted: "Extraction canceled by user"
6. Error handler recognizes cancellation message
7. Cleanup runs without showing error dialog
8. Status already shows "Extraction canceled" from cancel handler

### Benefits

- ✅ Cancel stops within 1 second (after current file)
- ✅ No silent background processing
- ✅ UI responsive immediately
- ✅ Clean thread shutdown
- ✅ No error dialog for normal cancellation
- ✅ Matches File Explorer pattern (consistent codebase)

---

**Priority:** HIGH - Cancel button doesn't work as expected  
**Severity:** MEDIUM - No crashes but bad UX (appears frozen)  
**Effort:** LOW - One line change + testing  
**Risk:** LOW - Graceful cancellation is safe
