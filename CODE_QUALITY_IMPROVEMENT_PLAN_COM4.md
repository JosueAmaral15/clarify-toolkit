# Code Quality Improvement Plan - COM4

## Strategy
Fix all pylint issues gradually across sessions, following protocol.
- **One or few files per session**
- **Step-by-step, honest fixes**
- **Commit after each file/session**
- **Target: All 196 files at 10.00/10**

## Progress Tracking

### ✅ Session 1: COMPLETE (2026-01-29)
**File:** `src/app.py` (1,923 lines)
- **Before:** 0.47/10 (572 issues)
- **After:** 10.00/10 (0 issues)
- **Fixes:** 572 total
  - 267 whitespace
  - 117 unused imports
  - 65 import-outside-toplevel (suppressed)
  - 11 redefined-outer-name
  - 10 attribute-defined-outside-init
  - Others: logging, false positives, etc.
- **Commits:** 5dc8212, dd5a833, 9249de6, 66be9ec, 314df1f, 2d2690d
- **Time:** ~2 hours
- **Status:** ✅ PERFECT SCORE

### 📋 Session 2: PENDING
**Strategy:** Identify and fix next batch of files
- [ ] Scan all 196 files for scores
- [ ] Prioritize by: impact, size, score
- [ ] Pick 1-3 files for Session 2
- [ ] Apply same methodology as Session 1

## File Inventory

**Total Files:** 196 Python files in src/

**Known Files (src/ root - ~40 files):**
- ✅ app.py (10.00/10) - DONE
- ❓ accessibility_manager.py
- ❓ batch_manager.py
- ❓ calculator_memory.py
- ❓ calculator_operations.py
- ❓ case_converter.py
- ❓ cloud_sync.py
- ❓ config_manager.py
- ❓ diff_analyzer.py
- ❓ export_manager.py
- ❓ formula_manager.py
- ❓ history_manager.py
- ❓ layout_manager.py
- ❓ merge_manager.py
- ❓ migration_manager.py
- ❓ placeholder_replacer.py
- ❓ plugin_loader.py
- ❓ presets_manager.py
- ... (more to scan)

**Subdirectories:**
- src/docks/ (GUI docks)
- src/tabs/ (GUI tabs)
- src/json/ (JSON processing)
- src/ai/ (AI integration)
- src/gui/ (GUI components)
- src/utils/ (utilities)
- src/rewriter/ (rewriter logic)

## Methodology (Same as Session 1)

**Phase 1: Analysis**
1. Run pylint to get baseline score
2. Count issues by category
3. Identify quick wins vs architectural changes

**Phase 2: Quick Wins**
- Whitespace (trailing spaces, blank lines)
- Logging (f-string → % formatting)
- Unused imports/variables
- Missing docstrings

**Phase 3: Real Issues**
- Redefined names
- Attribute initialization
- Code style violations
- Complexity issues

**Phase 4: Suppressions**
- Document why suppressed
- Only suppress false positives or intentional patterns
- Never suppress real issues

**Phase 5: Verification**
- Syntax check
- Import test
- Score verification
- Commit and push

## Success Criteria
- ✅ Every file at 9.50/10 minimum (ideally 10.00/10)
- ✅ No real issues hidden by suppressions
- ✅ All changes committed with clear messages
- ✅ Protocol compliance maintained
- ✅ No breaking changes

## Next Session Preparation
- [ ] Scan all files for scores
- [ ] Create priority list
- [ ] Choose Session 2 targets
- [ ] Estimate time needed
