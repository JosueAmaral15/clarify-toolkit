# File Explorer Table Mode Bug Investigation - COM1

**Branch**: COM1-file-explorer-fixes  
**Date**: 2026-01-22  
**Investigator**: COM1 (Programmer #1)  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5

---

## 🎯 Bug Description

**Component**: File Explorer Tool - Table Mode  
**Severity**: HIGH (Data Loss - Missing Results)  
**Status**: 🔍 INVESTIGATING

### User Report:
> "Table mode doesn't retrieve all results. Only returns one occurrence instead of multiple files"

### Reproduction Case:
- **Directory**: `/home/josue/.../binary_search`
- **Search Text**: `binary search`
- **Expected**: ≥2 files with matches
- **Actual**: Only 1 file shown

---

## 🔍 Investigation Steps

### ✅ Step 1: Code Study Completed
- 100% File Explorer code studied (SESSION_17)
- UnifiedFileExplorerExecutor understood
- Recent bug fixes known (v2.9.118-120)

### ⏳ Step 2-7: Ongoing
- Reproduce bug
- Analyze table population
- Check search logic
- Compare Tree vs Table
- Root cause
- Fix + tests

---

## 📊 Hypothesis
- Table view loop truncating results
- Off-by-one error in population
- Previous fix introduced regression

**Estimated Time**: 1-2 hours


---

## 🔍 Investigation Update - Critical Finding

### Code Analysis Completed:

**✅ Data Flow Traced:**
1. `execute_search()` (executor) → finds ALL files ✅
2. `FileExplorerWorker._emit_in_batches()` → emits ALL files in batches ✅
3. `_on_batch_ready()` (dock) → adds ALL files to tree ✅
4. `ResultsTree.add_file_result()` → stores ALL files in `_matches_data` ✅
5. `ResultsTree.get_matches_data()` → returns ALL files ✅
6. `_sync_search_to_table()` → loops through ALL files in `last_search_results` ✅

**All components are CORRECT!** No truncation in data processing.

### 🚨 HYPOTHESIS: View Mode Auto-Switch Issue

**Key Finding** (line 1692-1696):
```python
# Switch to tree view (respect manual override)
if not self._user_manually_changed_view:
    self.results_stack.setCurrentIndex(0)  # ← FORCES TREE VIEW!
    self.combo_view_mode.blockSignals(True)
    self.combo_view_mode.setCurrentIndex(0)
    self.combo_view_mode.blockSignals(False)
```

**Problem**: 
- When search completes with batches, it **FORCES Tree view** (line 1693)
- User must **manually switch to Table view** after search
- Table sync ONLY happens when switching views (line 668-670)

**Test Scenario**:
1. User starts in Table mode
2. Performs search
3. Results arrive → **AUTO-SWITCH to Tree view**
4. User sees Tree view (not Table!)
5. If user manually switches to Table → `_sync_search_to_table()` is called
6. But if user expects Table to auto-populate → FAILS!

### 🎯 Root Cause Identified:

**NOT a data loss bug!** It's a **view mode behavior issue**:
- Table mode doesn't auto-populate after search
- Tree view is always shown first
- User must manually switch to see table results

### 💡 Potential Solutions:

**Option A**: Remember user's preferred view mode and restore it after search
**Option B**: Auto-sync table view even when not visible
**Option C**: Show results in both views simultaneously

**Need user confirmation**: Is the bug that:
1. Table shows only 1 file when you switch to it? OR
2. Table doesn't auto-populate (you must switch away and back)?


---

## ✅ USER CLARIFICATION RECEIVED

**User confirms:**
> "The file data and metadata is shown in the table mode, but the result 
> have only one occurrence instead of two."

### 🎯 CORRECTED UNDERSTANDING:

**NOT a view switching issue!**

**The REAL bug:**
- User performs search in **Table mode**
- Table DOES populate with results
- File data and metadata ARE shown
- **BUT**: Only 1 file appears when there should be 2+ files

**This IS a data truncation bug!**

### 🔍 New Hypothesis:

Since the table sync code loops correctly through all files, the bug must be:

**Option 1**: `last_search_results` dictionary only contains 1 file (data loss earlier)
**Option 2**: `_matches_advanced_filters()` is rejecting files incorrectly
**Option 3**: Exception in loop causes early exit (OSError/FileNotFoundError)
**Option 4**: Table manager's `populate()` method has a limit

### 🚀 Next Steps:

1. **Reproduce bug locally** with test files
2. **Add debug logging** to see exactly how many files are in `last_search_results`
3. **Check filters** - are they accidentally rejecting files?
4. **Inspect table manager** - does it have row limits?

