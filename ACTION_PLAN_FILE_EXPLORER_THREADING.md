# ACTION PLAN: Restore Progress Bar for File Explorer Search

**Date:** 2026-01-12  
**Issue:** Progress bar not showing during File Explorer searches  
**Reported by:** User  
**Status:** 🔴 Planning Phase

---

## 1. PROBLEM STATEMENT

### 1.1 User Report
- **Symptom:** Progress bar does not appear when searching files in File Explorer
- **Question:** "Did you create a Thread for each processing, including the File Explorer Search, and the bar progress? Or you remove it?"
- **Expected:** Progress dialog should show during search operations (like it used to)
- **Actual:** No progress indication, UI appears frozen during large searches

### 1.2 Root Cause Analysis

**Investigation findings:**

1. ✅ **Progress dialog code EXISTS** (file_explorer_dock.py)
   - Lines: `_on_progress()`, `_on_progress_detailed()`, `QProgressDialog`
   - Signal connections: `self.executor.progress.connect(self._on_progress)`
   - Status: Code is INTACT, not removed

2. ✅ **Executor emits progress signals** (file_explorer_executor.py)
   - Line 303: `self.progress.emit(file_info.path)`
   - Line 304: `self.progress_detailed.emit(idx, total_files, file_info.path)`
   - Signal definitions (lines 79-80): `progress = Signal(str)`, `progress_detailed = Signal(int, int, str)`
   - Status: Signals are DEFINED and EMITTED

3. ❌ **PROBLEM: No threading used**
   - Line 965: `result = self.executor.execute_search(...)` - **SYNCHRONOUS CALL**
   - Executor runs in **main UI thread**
   - UI thread is **BLOCKED** during search
   - Progress dialog cannot render/update while UI is blocked

4. ✅ **Comparison: Search/Replace Panel WORKS**
   - Uses `QThread` + `SearchWorker` pattern
   - Line 734: `self._search_thread = QThread(self)`
   - Line 744: `self._search_worker.moveToThread(self._search_thread)`
   - Progress bar works perfectly because UI thread is free

**Conclusion:**
The progress bar code is still there, but it cannot work because the executor blocks the UI thread. We need to implement threading like Search/Replace Panel does.

---

## 2. SOLUTION DESIGN

### 2.1 Approach: Implement QThread-based Executor (Pattern from Search/Replace)

**Architecture:**
```
FileExplorerDock
    ↓
Creates → FileExplorerWorker (QObject)
    ↓
moveToThread() → QThread
    ↓
Signals → progress, progress_detailed, finished, error
    ↓
UI Thread receives signals → Updates progress dialog
```

### 2.2 Components to Create/Modify

#### **NEW FILE: `src/gui/panels/file_explorer_worker.py`**
- QObject-based worker (like SearchWorker)
- Methods: `execute_search()`, `execute_browse()`, `execute_replace()`
- Signals: `progress`, `progress_detailed`, `finished`, `error`
- Uses existing `FileExplorerExecutor` internally

#### **MODIFY: `src/gui/file_explorer_dock.py`**
- Import `FileExplorerWorker` and `QThread`
- Create thread + worker in `__init__` or on-demand
- Connect worker signals to existing `_on_progress()` methods
- Replace synchronous executor calls with async worker calls
- Handle thread cleanup on close

#### **NO CHANGES NEEDED:**
- ✅ `src/core/file_explorer_executor.py` - Already emits signals correctly
- ✅ Progress dialog code - Already exists and works
- ✅ Signal connections - Already set up correctly

### 2.3 Implementation Strategy

**Option A: On-Demand Thread Creation** (RECOMMENDED)
- Create thread + worker when search/browse/replace is triggered
- Destroy thread when operation completes
- Pros: Simpler, no persistent thread management
- Cons: Slight overhead on each operation (~10-50ms)

**Option B: Persistent Thread**
- Create thread in `__init__`, keep alive
- Reuse same thread for all operations
- Pros: No creation overhead
- Cons: More complex lifecycle management

**Decision: Use Option A** (on-demand) for simplicity and safety

---

## 3. DETAILED ACTION PLAN

### Phase 1: Create FileExplorerWorker (NEW FILE)

**File:** `src/gui/panels/file_explorer_worker.py`

**Structure:**
```python
class FileExplorerWorker(QObject):
    # Signals
    progress = Signal(str)
    progress_detailed = Signal(int, int, str)
    finished = Signal(object)  # Emits result
    error = Signal(str)
    
    def __init__(self, executor):
        """Accept FileExplorerExecutor instance"""
        
    def execute_search(self, directory, filename_pattern, ...):
        """Run search in worker thread"""
        try:
            # Connect executor signals to worker signals
            self.executor.progress.connect(self.progress)
            self.executor.progress_detailed.connect(self.progress_detailed)
            
            # Run search
            result = self.executor.execute_search(...)
            
            # Emit result
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

**Tasks:**
- [ ] Create file with class definition
- [ ] Add signals (4 signals: progress, progress_detailed, finished, error)
- [ ] Add `__init__` accepting executor
- [ ] Add `execute_search()` method
- [ ] Add `execute_browse()` method  
- [ ] Add `execute_replace()` method
- [ ] Add signal forwarding from executor to worker
- [ ] Add exception handling with error signal
- [ ] Add docstrings

### Phase 2: Modify file_explorer_dock.py (Threading Integration)

**File:** `src/gui/file_explorer_dock.py`

**Section 2.1: Imports**
- [ ] Add: `from PySide6.QtCore import QThread`
- [ ] Add: `from src.gui.panels.file_explorer_worker import FileExplorerWorker`

**Section 2.2: Modify `_on_apply()` - Search Operation (Line ~965)**

Current code:
```python
result = self.executor.execute_search(...)  # BLOCKING
```

New code:
```python
# Create thread and worker
self._search_thread = QThread(self)
self._search_worker = FileExplorerWorker(self.executor)
self._search_worker.moveToThread(self._search_thread)

# Connect signals
self._search_worker.progress.connect(self._on_progress)
self._search_worker.progress_detailed.connect(self._on_progress_detailed)
self._search_worker.finished.connect(self._on_search_finished)
self._search_worker.error.connect(self._on_search_error)

# Start thread and trigger search
self._search_thread.started.connect(
    lambda: self._search_worker.execute_search(...)
)
self._search_thread.start()
```

**Tasks:**
- [ ] Replace synchronous `executor.execute_search()` call with threading pattern
- [ ] Store thread/worker references: `self._search_thread`, `self._search_worker`
- [ ] Connect worker signals to existing handlers
- [ ] Pass all search parameters correctly

**Section 2.3: Add `_on_search_finished()` Handler**

```python
def _on_search_finished(self, result):
    """Handle search completion (runs in UI thread)"""
    # Close progress dialog
    if self.progress_dialog:
        self.progress_dialog.close()
        self.progress_dialog = None
    
    # Process results (existing code from line ~977)
    if not self._user_manually_changed_view:
        self.results_stack.setCurrentIndex(0)
        # ... rest of existing result handling
    
    # Cleanup thread
    self._cleanup_thread()
```

**Tasks:**
- [ ] Create method
- [ ] Move result processing code from `_on_apply()` here
- [ ] Close progress dialog
- [ ] Call thread cleanup

**Section 2.4: Add `_on_search_error()` Handler**

```python
def _on_search_error(self, error_message):
    """Handle search errors"""
    # Close progress dialog
    if self.progress_dialog:
        self.progress_dialog.close()
        self.progress_dialog = None
    
    # Show error message
    QMessageBox.critical(self, "Search Error", error_message)
    
    # Cleanup thread
    self._cleanup_thread()
```

**Tasks:**
- [ ] Create method
- [ ] Show error dialog
- [ ] Close progress dialog
- [ ] Call thread cleanup

**Section 2.5: Add `_cleanup_thread()` Helper**

```python
def _cleanup_thread(self):
    """Clean up worker thread after operation"""
    if hasattr(self, '_search_thread') and self._search_thread:
        self._search_thread.quit()
        self._search_thread.wait()
        self._search_thread.deleteLater()
        self._search_thread = None
    
    if hasattr(self, '_search_worker'):
        self._search_worker = None
```

**Tasks:**
- [ ] Create method
- [ ] Quit thread gracefully
- [ ] Wait for thread to finish
- [ ] Delete thread/worker objects

**Section 2.6: Modify `_on_apply()` - Browse Operation (Line ~1070)**

**Tasks:**
- [ ] Apply same threading pattern to `execute_browse()` call
- [ ] Create `_on_browse_finished()` handler
- [ ] Create `_on_browse_error()` handler
- [ ] Use same cleanup pattern

**Section 2.7: Handle Replace Operations (Lines ~1550, ~1653)**

**Tasks:**
- [ ] Apply threading pattern to both `execute_replace()` calls
- [ ] Create `_on_replace_finished()` handler
- [ ] Create `_on_replace_error()` handler
- [ ] Use same cleanup pattern

### Phase 3: Testing & Validation

**Manual Tests:**
- [ ] **Small search** (10-50 files): Progress dialog shows briefly
- [ ] **Medium search** (100-1000 files): Progress updates visible
- [ ] **Large search** (5000+ files): Progress tracks correctly, UI responsive
- [ ] **Browse mode**: Progress works for directory listing
- [ ] **Replace operation**: Progress shows during replace
- [ ] **Cancel operation**: Click cancel on progress dialog, operation stops
- [ ] **Multiple searches**: Run search, wait for finish, run another (no resource leaks)
- [ ] **Error handling**: Invalid directory, shows error dialog
- [ ] **Open in Editor**: Works during and after search

**Automated Tests (if time permits):**
- [ ] Create `tests/manual/test_file_explorer_threading.py`
- [ ] Test thread creation/cleanup
- [ ] Test signal emissions
- [ ] Test memory leaks (run 100 searches)

---

## 4. RISK ANALYSIS

### 4.1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Thread leaks (not cleaned up) | Medium | High | Implement thorough cleanup in `_cleanup_thread()` |
| Race conditions in result handling | Low | Medium | All result processing in `_on_*_finished()` on UI thread |
| Progress dialog doesn't update | Low | Low | Test with various search sizes |
| Breaks existing functionality | Low | High | Extensive manual testing after implementation |
| Thread doesn't stop on cancel | Medium | Medium | Connect progress dialog cancel to thread.quit() |

### 4.2 Rollback Plan

If threading causes critical issues:
1. Revert to synchronous executor calls
2. Remove progress dialog (accept blocking behavior)
3. Alternative: Use QTimer-based chunked processing (more complex)

---

## 5. ACCEPTANCE CRITERIA

### 5.1 Must Have (P0)
- ✅ Progress dialog appears during search operations
- ✅ Progress bar updates show current file being processed
- ✅ UI remains responsive during search (can move window, click cancel)
- ✅ Search results populate correctly after completion
- ✅ No thread leaks (test with 10+ consecutive searches)
- ✅ Cancel button stops search operation
- ✅ Error handling works (shows error dialog)

### 5.2 Should Have (P1)
- ✅ Browse mode shows progress
- ✅ Replace operations show progress
- ✅ Progress detailed shows "file X of Y"
- ✅ No crashes or hangs

### 5.3 Nice to Have (P2)
- ⭕ Progress estimates time remaining
- ⭕ Automated tests for threading

---

## 6. IMPLEMENTATION TIMELINE

**Estimated Time:** 60-90 minutes

1. **Phase 1: Create FileExplorerWorker** (20-30 min)
   - Write class, add methods, test signals

2. **Phase 2: Integrate Threading** (30-40 min)
   - Modify `_on_apply()` for search/browse
   - Add result handlers
   - Add cleanup logic
   - Handle replace operations

3. **Phase 3: Testing** (10-20 min)
   - Manual tests with various search sizes
   - Test cancel functionality
   - Test error handling
   - Verify no resource leaks

---

## 7. REFERENCES

### 7.1 Files to Examine
- ✅ `src/gui/panels/search_replace_panel.py` (lines 734, 744) - Threading pattern reference
- ✅ `src/gui/panels/search_worker.py` - Worker class structure
- ✅ `src/gui/file_explorer_dock.py` (line 965) - Current synchronous call
- ✅ `src/core/file_explorer_executor.py` (lines 303-304) - Signal emissions

### 7.2 Qt Documentation
- QThread: https://doc.qt.io/qt-6/qthread.html
- moveToThread(): https://doc.qt.io/qt-6/qobject.html#moveToThread
- Signal/Slot across threads: https://doc.qt.io/qt-6/threads-qobject.html

---

## 8. NOTES

### 8.1 Why This Happened
The File Explorer likely never had threading, or it was removed during a refactoring. The progress dialog code was left in place expecting signals to arrive, but since the executor runs synchronously, the UI thread blocks and the dialog can't render.

### 8.2 Similar Issue in Other Modules?
**Check these modules for same problem:**
- ⚠️ JSON Comparator (if has progress)
- ⚠️ Batch operations (if has progress)
- ✅ Search/Replace Panel - Already uses threading (reference implementation)

---

## 9. SIGN-OFF

**Created by:** GitHub Copilot CLI  
**Reviewed by:** [Pending]  
**Approved by:** [Pending]  

**Next Step:** Create EXECUTION_PLAN_FILE_EXPLORER_THREADING.md before implementation
