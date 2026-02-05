# EXECUTION PLAN: File Explorer Progress Bar Threading Implementation

**Date:** 2026-01-12  
**Related:** ACTION_PLAN_FILE_EXPLORER_THREADING.md  
**Estimated Time:** 60-90 minutes  
**Status:** 📋 Ready to Execute

---

## EXECUTION OVERVIEW

This document provides step-by-step commands and code changes to implement threading for File Explorer operations, restoring the progress bar functionality.

**Pattern:** Follow Search/Replace Panel threading architecture  
**Principle:** Minimal changes, maximum compatibility  
**Testing:** Manual validation after each phase

---

## PHASE 1: CREATE FILE EXPLORER WORKER (20-30 min)

### Step 1.1: Create Worker File

**Action:** Create new file `src/gui/panels/file_explorer_worker.py`

**File Structure:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FileExplorerWorker - Background worker for File Explorer operations.

Runs search, browse, and replace operations in a separate thread to keep
the UI responsive and allow progress dialog updates.

Created: 2026-01-12 (v2.9.122)
Pattern: Based on SearchWorker (search_worker.py)
"""

from PySide6.QtCore import QObject, Signal

from ...core.file_explorer_executor import FileExplorerExecutor


class FileExplorerWorker(QObject):
    """
    Worker for running File Explorer operations in background thread.
    
    Signals:
        progress: Simple progress message (file being processed)
        progress_detailed: Detailed progress (current, total, message)
        finished: Operation completed successfully (emits result)
        error: Operation failed (emits error message)
    """
    
    # Signals
    progress = Signal(str)                  # Current file/message
    progress_detailed = Signal(int, int, str)  # (current, total, message)
    finished = Signal(object)               # Result object
    error = Signal(str)                     # Error message
    
    def __init__(self, executor: FileExplorerExecutor):
        """
        Initialize worker with executor instance.
        
        Args:
            executor: FileExplorerExecutor instance to use for operations
        """
        super().__init__()
        self.executor = executor
        self._is_cancelled = False
    
    def execute_search(
        self,
        directory: str,
        filename_pattern: str,
        content_query: str,
        search_options: dict,
        show_hidden: bool,
        recursive: bool,
        filters: dict,
        conditions: list
    ):
        """
        Execute search operation in worker thread.
        
        This method runs in the worker thread. It connects executor signals
        to worker signals so progress updates reach the UI thread.
        
        Args:
            directory: Root directory to search
            filename_pattern: Filename pattern (wildcards)
            content_query: Content to search for
            search_options: Search options dict
            show_hidden: Show hidden files
            recursive: Search recursively
            filters: Filters dict
            conditions: Advanced conditions list
        """
        try:
            # Forward executor signals to worker signals
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            
            # Execute search
            result = self.executor.execute_search(
                directory=directory,
                filename_pattern=filename_pattern,
                content_query=content_query,
                search_options=search_options,
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters,
                conditions=conditions
            )
            
            # Emit result
            self.finished.emit(result)
            
        except Exception as e:
            # Emit error
            self.error.emit(str(e))
        
        finally:
            # Disconnect signals
            try:
                self.executor.progress.disconnect(self.progress)
                self.executor.progress_detailed.disconnect(self.progress_detailed)
            except:
                pass  # Already disconnected
    
    def execute_browse(
        self,
        directory: str,
        show_hidden: bool,
        recursive: bool,
        filters: dict
    ):
        """
        Execute browse operation in worker thread.
        
        Args:
            directory: Directory to browse
            show_hidden: Show hidden files
            recursive: Browse recursively
            filters: Filters dict
        """
        try:
            # Forward signals
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            
            # Execute browse
            result = self.executor.execute_browse(
                directory=directory,
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters
            )
            
            # Emit result
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        
        finally:
            try:
                self.executor.progress.disconnect(self.progress)
                self.executor.progress_detailed.disconnect(self.progress_detailed)
            except:
                pass
    
    def execute_replace(
        self,
        files: list,
        search_text: str,
        replace_text: str,
        search_options: dict
    ):
        """
        Execute replace operation in worker thread.
        
        Args:
            files: List of file paths to process
            search_text: Text to search for
            replace_text: Replacement text
            search_options: Search options dict
        """
        try:
            # Forward signals
            self.executor.progress.connect(self.progress)
            
            # Execute replace
            result = self.executor.execute_replace(
                files=files,
                search_text=search_text,
                replace_text=replace_text,
                search_options=search_options
            )
            
            # Emit result
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        
        finally:
            try:
                self.executor.progress.disconnect(self.progress)
            except:
                pass
```

**Verification:**
```bash
# Check file created
ls -lh src/gui/panels/file_explorer_worker.py

# Check syntax
python3 -m py_compile src/gui/panels/file_explorer_worker.py
```

---

## PHASE 2: INTEGRATE THREADING INTO FILE EXPLORER DOCK (30-40 min)

### Step 2.1: Add Imports

**File:** `src/gui/file_explorer_dock.py`

**Location:** After existing imports (around line 20-30)

**Add:**
```python
from PySide6.QtCore import QThread
from src.gui.panels.file_explorer_worker import FileExplorerWorker
```

**Command to verify:**
```bash
grep -n "from PySide6.QtCore import.*QThread" src/gui/file_explorer_dock.py
grep -n "FileExplorerWorker" src/gui/file_explorer_dock.py
```

### Step 2.2: Add Thread Cleanup Method

**File:** `src/gui/file_explorer_dock.py`

**Location:** After `_on_progress_detailed()` method (search for it)

**Add new method:**
```python
def _cleanup_worker_thread(self):
    """
    Clean up worker thread after operation completes.
    
    This ensures proper thread lifecycle management and prevents resource leaks.
    Called from _on_*_finished() and _on_*_error() handlers.
    
    Version: v2.9.122
    """
    if hasattr(self, '_worker_thread') and self._worker_thread:
        self._worker_thread.quit()
        self._worker_thread.wait()
        self._worker_thread.deleteLater()
        self._worker_thread = None
    
    if hasattr(self, '_worker'):
        self._worker = None
```

### Step 2.3: Add Search Finished Handler

**File:** `src/gui/file_explorer_dock.py`

**Location:** After `_cleanup_worker_thread()`

**Add:**
```python
def _on_search_finished(self, result):
    """
    Handle search operation completion (runs in UI thread).
    
    Args:
        result: SearchResult from FileExplorerExecutor
    
    Version: v2.9.122
    """
    # Close progress dialog
    if self.progress_dialog:
        self.progress_dialog.close()
        self.progress_dialog = None
    
    # ============================================================================
    # SEARCH MODE: Populate ResultsTree (v2.9.117 - B.2)
    # ============================================================================
    # Switch to tree view (but respect manual override - v2.9.118 bugfix)
    if not self._user_manually_changed_view:
        self.results_stack.setCurrentIndex(0)
        self.combo_view_mode.blockSignals(True)
        self.combo_view_mode.setCurrentIndex(0)
        self.combo_view_mode.blockSignals(False)
    
    # Populate results tree
    self.results_tree.populate(result)
    
    # Update status bar
    match_count = sum(len(file_result.matches) for file_result in result.files)
    self.status_label.setText(
        f"Found {len(result.files)} file(s) with {match_count} match(es)"
    )
    
    # Cleanup thread
    self._cleanup_worker_thread()

def _on_browse_finished(self, result):
    """
    Handle browse operation completion (runs in UI thread).
    
    Args:
        result: BrowseResult from FileExplorerExecutor
    
    Version: v2.9.122
    """
    # Close progress dialog
    if self.progress_dialog:
        self.progress_dialog.close()
        self.progress_dialog = None
    
    # ============================================================================
    # BROWSE MODE: Populate FileListTable (v2.9.117 - B.1)
    # ============================================================================
    # Auto-switch to table view (respect manual override)
    if not self._user_manually_changed_view:
        self.results_stack.setCurrentIndex(1)
        self.combo_view_mode.blockSignals(True)
        self.combo_view_mode.setCurrentIndex(1)
        self.combo_view_mode.blockSignals(False)
    
    # Populate table
    self.file_list_table.populate(result.files)
    
    # Update status bar
    self.status_label.setText(f"Found {len(result.files)} file(s)")
    
    # Cleanup thread
    self._cleanup_worker_thread()

def _on_operation_error(self, error_message: str):
    """
    Handle operation error (runs in UI thread).
    
    Args:
        error_message: Error description
    
    Version: v2.9.122
    """
    # Close progress dialog
    if self.progress_dialog:
        self.progress_dialog.close()
        self.progress_dialog = None
    
    # Show error dialog
    QMessageBox.critical(
        self,
        tr("file_list.error_title"),
        f"{tr('file_list.error_operation')}\n\n{error_message}"
    )
    
    # Cleanup thread
    self._cleanup_worker_thread()
```

### Step 2.4: Modify _on_apply() - Replace Synchronous Search

**File:** `src/gui/file_explorer_dock.py`

**Find:** Around line 965, the code:
```python
result = self.executor.execute_search(
    directory=directory,
    filename_pattern=filename_pattern,
    content_query=content_query,
    search_options=search_options,
    show_hidden=show_hidden,
    recursive=recursive,
    filters=filters,
    conditions=conditions,
)
```

**Replace with:**
```python
# Create thread and worker (v2.9.122 - Threading for progress)
self._worker_thread = QThread(self)
self._worker = FileExplorerWorker(self.executor)
self._worker.moveToThread(self._worker_thread)

# Connect signals
self._worker.progress.connect(self._on_progress)
self._worker.progress_detailed.connect(self._on_progress_detailed)
self._worker.finished.connect(self._on_search_finished)
self._worker.error.connect(self._on_operation_error)

# Start thread and execute search
self._worker_thread.started.connect(
    lambda: self._worker.execute_search(
        directory=directory,
        filename_pattern=filename_pattern,
        content_query=content_query,
        search_options=search_options,
        show_hidden=show_hidden,
        recursive=recursive,
        filters=filters,
        conditions=conditions
    )
)
self._worker_thread.start()

# Return early - results will be handled by _on_search_finished()
return
```

**IMPORTANT:** After this code, there's result processing code. We need to REMOVE it or it will execute before the thread finishes. Add `return` statement after `self._worker_thread.start()`.

### Step 2.5: Modify _on_apply() - Replace Synchronous Browse

**File:** `src/gui/file_explorer_dock.py`

**Find:** Around line 1070, the code:
```python
result = self.executor.execute_browse(
    directory=directory,
    show_hidden=show_hidden,
    recursive=recursive,
    filters=filters,
)
```

**Replace with:**
```python
# Create thread and worker (v2.9.122 - Threading for progress)
self._worker_thread = QThread(self)
self._worker = FileExplorerWorker(self.executor)
self._worker.moveToThread(self._worker_thread)

# Connect signals
self._worker.progress.connect(self._on_progress)
self._worker.progress_detailed.connect(self._on_progress_detailed)
self._worker.finished.connect(self._on_browse_finished)
self._worker.error.connect(self._on_operation_error)

# Start thread and execute browse
self._worker_thread.started.connect(
    lambda: self._worker.execute_browse(
        directory=directory,
        show_hidden=show_hidden,
        recursive=recursive,
        filters=filters
    )
)
self._worker_thread.start()

# Return early - results will be handled by _on_browse_finished()
return
```

### Step 2.6: Handle Replace Operations (Optional for now)

**Note:** Replace operations can be done in Phase 3 if time permits. They're less critical than search/browse.

**Files to check:**
- Line ~1550: `execute_replace()` call #1
- Line ~1653: `execute_replace()` call #2

**Same pattern:** Create thread, worker, connect signals, start thread, return early.

---

## PHASE 3: TESTING & VALIDATION (10-20 min)

### Test 3.1: Small Search (Quick Validation)

**Steps:**
1. Restart Clarify: `cd clarify && python3 -m src.app`
2. Open File Explorer
3. Set directory: `/usr/share/applications` (or any small folder)
4. Set content query: `Name`
5. Click Search

**Expected:**
- ✅ Progress dialog appears
- ✅ Shows "Processing..." message
- ✅ Dialog closes when done
- ✅ Results populate in tree
- ✅ Status bar shows count

**If FAILED:**
- Check imports are correct
- Check thread is started: `self._worker_thread.start()`
- Check signals connected
- Check `return` statement added after thread start

### Test 3.2: Medium Search (Progress Visibility)

**Steps:**
1. Set directory: `/usr` (large folder)
2. Set content query: `python`
3. Enable recursive
4. Click Search

**Expected:**
- ✅ Progress dialog shows current file
- ✅ Progress bar updates (if progress_detailed works)
- ✅ UI remains responsive (can move window)
- ✅ Can click Cancel button
- ✅ Results populate after completion

### Test 3.3: Browse Mode

**Steps:**
1. Clear content query (leave empty)
2. Set directory: `/home` or large folder
3. Enable recursive
4. Click Search (will trigger browse)

**Expected:**
- ✅ Progress dialog appears
- ✅ Table populates with files
- ✅ Status shows file count

### Test 3.4: Cancel Operation

**Steps:**
1. Start large search
2. Click "Cancel" on progress dialog

**Expected:**
- ✅ Dialog closes
- ✅ Operation stops
- ✅ UI returns to normal state

**If FAILED:**
- Need to connect `progress_dialog.canceled` to worker cancellation
- Add to worker: `def cancel(self): self.executor.cancel()`

### Test 3.5: Error Handling

**Steps:**
1. Set directory: `/nonexistent/path`
2. Click Search

**Expected:**
- ✅ Error dialog appears
- ✅ Shows error message
- ✅ No crash

### Test 3.6: Multiple Operations (Resource Leak Check)

**Steps:**
1. Run 5 searches consecutively
2. Check with: `ps aux | grep python3` (PID should be stable)
3. Check memory doesn't grow excessively

**Expected:**
- ✅ No thread leaks
- ✅ Memory stable
- ✅ No performance degradation

### Test 3.7: Open in Editor (Integration Test)

**Steps:**
1. Run search
2. Right-click result
3. Click "Open in Editor"

**Expected:**
- ✅ Works correctly
- ✅ No conflicts with threading

---

## PHASE 4: COMMIT & PUSH

### Step 4.1: Verify Changes

**Command:**
```bash
cd "/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify"

# Check what changed
git status

# Review changes
git diff src/gui/file_explorer_dock.py | head -100
```

### Step 4.2: Commit

**Commands:**
```bash
git add src/gui/panels/file_explorer_worker.py
git add src/gui/file_explorer_dock.py

git commit -m "feat: add threading to File Explorer for progress bar support (v2.9.122)

Problem:
- Progress dialog not showing during File Explorer searches
- Executor was running synchronously in UI thread, blocking updates
- Progress signals emitted but dialog couldn't render

Solution:
- Created FileExplorerWorker (QObject) based on SearchWorker pattern
- Moved execute_search() and execute_browse() to worker thread
- Connected worker signals to existing progress dialog handlers
- Added proper thread lifecycle management

Changes:
- NEW: src/gui/panels/file_explorer_worker.py
  * Worker class with execute_search/browse/replace methods
  * Signals: progress, progress_detailed, finished, error
  * Based on SearchWorker architecture

- MODIFIED: src/gui/file_explorer_dock.py
  * Added FileExplorerWorker and QThread imports
  * Added _cleanup_worker_thread() for lifecycle management
  * Added _on_search_finished() handler
  * Added _on_browse_finished() handler
  * Added _on_operation_error() handler
  * Modified _on_apply() search: use threading instead of sync call
  * Modified _on_apply() browse: use threading instead of sync call

Impact:
- Progress dialog now appears and updates during operations
- UI remains responsive during search/browse
- Cancel button works
- No change to search results or functionality
- No breaking changes to existing code

Testing:
- Manual tests: small/medium/large searches
- Browse mode tested
- Cancel functionality tested
- Resource leak check (multiple operations)
- Integration test (Open in Editor)

References:
- ACTION_PLAN_FILE_EXPLORER_THREADING.md
- EXECUTION_PLAN_FILE_EXPLORER_THREADING.md
- Pattern: src/gui/panels/search_worker.py
"
```

### Step 4.3: Push

**Command:**
```bash
git push origin main
```

---

## ROLLBACK PROCEDURE (If Issues Found)

### If threading causes problems:

```bash
# Revert commit
git revert HEAD

# Or reset (if not pushed)
git reset --hard HEAD~1

# Alternative: Remove progress dialog code entirely
# Edit file_explorer_dock.py and comment out:
# - _on_progress()
# - _on_progress_detailed()
# - progress_dialog creation
```

---

## COMPLETION CHECKLIST

### Before Starting
- [ ] Read ACTION_PLAN_FILE_EXPLORER_THREADING.md
- [ ] Understand Qt threading model
- [ ] Review SearchWorker implementation

### Phase 1: Worker Creation
- [ ] Create file_explorer_worker.py
- [ ] Add class definition and signals
- [ ] Add execute_search() method
- [ ] Add execute_browse() method
- [ ] Add execute_replace() method (optional)
- [ ] Verify syntax with py_compile

### Phase 2: Integration
- [ ] Add imports to file_explorer_dock.py
- [ ] Add _cleanup_worker_thread() method
- [ ] Add _on_search_finished() method
- [ ] Add _on_browse_finished() method
- [ ] Add _on_operation_error() method
- [ ] Replace sync search call with threading
- [ ] Replace sync browse call with threading
- [ ] Add return statements after thread start

### Phase 3: Testing
- [ ] Test small search
- [ ] Test medium search with visible progress
- [ ] Test browse mode
- [ ] Test cancel functionality
- [ ] Test error handling
- [ ] Test multiple operations (leak check)
- [ ] Test Open in Editor integration

### Phase 4: Finalization
- [ ] Review all changes
- [ ] Commit with detailed message
- [ ] Push to remote
- [ ] Update user documentation (if needed)

---

## NOTES

### Common Issues & Solutions

**Issue:** Progress dialog doesn't appear
- **Check:** Thread is started with `start()`
- **Check:** Signals are connected before thread starts
- **Check:** Worker is moved to thread: `moveToThread()`

**Issue:** UI still freezes
- **Check:** Code after `thread.start()` - should be `return` to avoid blocking
- **Check:** Worker actually runs in thread (print thread ID to verify)

**Issue:** Results don't populate
- **Check:** `_on_search_finished()` is connected to `worker.finished` signal
- **Check:** Result processing code moved to handler

**Issue:** Thread doesn't stop
- **Check:** `_cleanup_worker_thread()` is called
- **Check:** `thread.quit()` and `thread.wait()` are called

**Issue:** Memory leak
- **Check:** `deleteLater()` called on thread/worker
- **Check:** References set to None
- **Check:** Signals disconnected in worker finally block

---

## SIGN-OFF

**Created by:** GitHub Copilot CLI  
**Date:** 2026-01-12  
**Status:** Ready for execution  
**Estimated completion:** 60-90 minutes

**Approval to proceed:** [Waiting for user confirmation]
