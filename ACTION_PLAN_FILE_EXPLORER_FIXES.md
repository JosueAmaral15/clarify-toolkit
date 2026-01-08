# ACTION PLAN - FILE EXPLORER BUG FIXES

**Date:** 2026-01-08  
**Protocol:** Simplicidade 3  
**Status:** Planning Phase  
**Priority:** HIGH (5 critical bugs affecting user experience)

---

## 🎯 ISSUES IDENTIFIED

### Issue #1: Exclude Globs Not Working for New Inputs
**Symptom:** Adding `.venv` to exclude globs (comma-separated) doesn't filter out `.venv` directories  
**Impact:** Users see files they want to exclude  
**Severity:** HIGH  
**Component:** File filter system (glob pattern matching)

### Issue #2: Advanced Conditions Path Filter Not Working
**Symptom:** Logic: AND, condition "path not contains .venv" doesn't filter  
**Impact:** Advanced filtering broken, users can't exclude paths  
**Severity:** HIGH  
**Component:** Advanced conditions logic

### Issue #3: Case and Regex Disabled in Advanced Conditions
**Symptom:** Case-sensitive and Regex checkboxes are disabled/not working  
**Impact:** Users can't use case-sensitive or regex patterns  
**Severity:** MEDIUM  
**Component:** Advanced conditions UI state

### Issue #4: Comparison Operators Show Symbols Instead of Text
**Symptom:** "less than" → "<", "less than or equal" → "<=", "greater than or equal" → ">="  
**Impact:** Undesirable display, possibly translation issue  
**Severity:** LOW (cosmetic but affects UX)  
**Component:** Advanced conditions comparison operators display

### Issue #5: Search Not Working After Changing Directory
**Symptom:** After modifying Directory input in "Directory Type", search fails for new directories  
**Impact:** Critical - users can't search in different directories  
**Severity:** CRITICAL  
**Component:** Directory input handler / search initialization

---

## 📋 INVESTIGATION PLAN (Protocolo Simplicidade 3)

### Phase 1: Documentation Review (10 min)
- [x] Read File Explorer specification docs
- [ ] Review exclude globs implementation docs
- [ ] Review advanced conditions implementation docs
- [ ] Review directory search flow docs

### Phase 2: Code Study (30 min)
- [ ] Study exclude globs logic (file_filter_panel.py or file_explorer_executor.py)
- [ ] Study advanced conditions filtering (conditions_grid.py)
- [ ] Study comparison operators display (i18n or UI setup)
- [ ] Study directory input change handler (file_explorer_dock.py)
- [ ] Identify root causes for each issue

### Phase 3: Root Cause Analysis (15 min)
- [ ] Document root cause for Issue #1 (exclude globs)
- [ ] Document root cause for Issue #2 (path filter)
- [ ] Document root cause for Issue #3 (case/regex disabled)
- [ ] Document root cause for Issue #4 (operators display)
- [ ] Document root cause for Issue #5 (directory change)

### Phase 4: Solution Design (20 min)
- [ ] Design fix for Issue #1
- [ ] Design fix for Issue #2
- [ ] Design fix for Issue #3
- [ ] Design fix for Issue #4
- [ ] Design fix for Issue #5
- [ ] Verify no side effects

### Phase 5: Implementation (60 min)
- [ ] Fix Issue #5 first (CRITICAL - blocks basic functionality)
- [ ] Fix Issue #1 (HIGH - exclude globs)
- [ ] Fix Issue #2 (HIGH - advanced conditions)
- [ ] Fix Issue #3 (MEDIUM - case/regex)
- [ ] Fix Issue #4 (LOW - cosmetic)

### Phase 6: Testing (30 min)
- [ ] Test Issue #5: Change directory and search
- [ ] Test Issue #1: Add `.venv` to exclude globs
- [ ] Test Issue #2: Use "path not contains .venv" condition
- [ ] Test Issue #3: Enable case/regex in advanced conditions
- [ ] Test Issue #4: Verify operator text display
- [ ] Regression testing: Verify existing functionality still works

### Phase 7: Git Commit & Push (10 min)
- [ ] Stage all changes
- [ ] Commit with descriptive message
- [ ] Push to origin/main

**Total Estimated Time:** ~3 hours

---

## 🔍 INITIAL INVESTIGATION NOTES

### File Locations (From Study Phase)
- **File Explorer Dock:** `src/gui/file_explorer_dock.py` (1,789 lines)
- **Executor:** `src/core/file_explorer_executor.py` (628 lines)
- **Filter Panel:** `src/gui/widgets/file_filter_panel.py` (15,854 bytes)
- **Conditions Grid:** `src/gui/widgets/search_widgets.py` (ConditionsGrid)
- **Advanced Filters:** Applied in `_matches_advanced_filters()` method

### Known Design Patterns (From Study Phase)
- Exclude patterns: glob-based filtering
- Advanced conditions: AND/OR logic with field/operator/value
- Directory input: QLineEdit with browse button
- Search execution: ThreadManager + UnifiedFileExplorerExecutor

---

## 🎯 SUCCESS CRITERIA

All issues must be resolved:
1. ✅ Exclude globs (`.venv`) filters correctly
2. ✅ Advanced condition "path not contains .venv" works
3. ✅ Case and Regex checkboxes functional in advanced conditions
4. ✅ Comparison operators show full text (not symbols)
5. ✅ Search works after changing directory input

**Verification:**
- Manual testing of all 5 scenarios
- No regression in existing functionality
- All changes committed and pushed to git

---

## 📝 NOTES

- **Protocol Compliance:** Following Simplicidade 3 (study → understand → fix → test)
- **Priority Order:** Fix critical issues first (Issue #5), then high (Issues #1, #2)
- **No Breaking Changes:** Ensure backward compatibility
- **Documentation:** Update if significant logic changes
- **Git Hygiene:** Clean commit messages, logical grouping

---

**Next Step:** Begin Phase 1 - Documentation Review

**Created:** 2026-01-08 13:05 UTC  
**Expected Completion:** 2026-01-08 16:00 UTC (3 hours)
