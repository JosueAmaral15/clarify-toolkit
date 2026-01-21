# 🎯 ACTION PLAN: File Explorer Integration - Phase 4 (Logic)

**Programmer**: #4  
**Branch**: COM4-code-study  
**Protocol**: Simplicity Protocol 3 (Step 1.8)  

---

## 📋 Plan Metadata

**📅 Date**: 2026-01-21  
**🕐 Time**: 12:40 UTC  
**⚡ Priority**: 🟡 High  
**🏷️ Type**: Evolution  
**📌 Task ID**: v2.9.116 - Phase 4 (from TASKS.md line 89-123)  
**🎯 Main Function**: Complete File Explorer unification logic  
**📋 Desired Requirement**: Unified search pipeline (List + Search + Replace)  
**✅ Expected Result**: Phase 4 complete, ready for Phase 5 (UI/UX)  

---

## 🎯 TL;DR (2AM Emergency Reference)

**What**: Implement unified search logic in File Explorer (Phase 4 of v2.9.116)  
**Why**: Phases 1-3 complete (68.75%), need to finish logic layer before UI polish  
**How Long**: 1.5h (per TASKS.md estimate)  
**Current Status**: Phase 3 done, Phase 4 next  
**Rollback**: Git revert to commit 96e562d (current HEAD)  

**If it breaks**:
```bash
cd clarify-COM4-code-study
git reset --hard 96e562d
git clean -fd
```

---

## 📊 Context & Background

### Current State (from TASKS.md)
- ✅ **Phase 1**: Planning (30 min) - COMPLETE
- ✅ **Phase 2**: Components (1h) - COMPLETE
  - ✅ search_widgets.py created (5 reusable widgets)
  - ✅ file_explorer_executor.py unified
- ✅ **Phase 3**: Refactoring (2.5h) - COMPLETE
  - ✅ 5 collapsible sections
  - ✅ Signal connections
  - ✅ Replace functionality
  - ✅ 6/6 integration tests passing
- ⏳ **Phase 4**: Logic (1.5h) - **THIS PLAN**
- ⏳ **Phase 5**: UI/UX (1h)
- ⏳ **Phase 6**: Manual Testing (30 min)
- ⏳ **Phase 7**: Documentation (30 min)
- ⏳ **Phase 8**: Deploy (30 min)

### What Phase 4 Requires (from TASKS.md line 118-123)
- [ ] **4.1**: Implement unified search pipeline (1h)
  - List + Search + Replace in single pipeline
  - Apply advanced conditions to all modes
  - Unified progress tracking
- [ ] **4.2**: Unit tests for new components (30 min)

### Key Learnings from Code Study
From CODE_STUDY_PHASE1_SUMMARY.md:
- ✅ **Worker pattern**: Used in FileExplorerExecutor (threading)
- ✅ **Strategy pattern**: browse vs search vs replace modes
- ✅ **Observer pattern**: Signal-based progress tracking
- ✅ **Circuit breaker**: MAX_SNIPPET_LENGTH=200, MAX_TOTAL_MATCHES=50k

---

## 🔧 Implementation Steps

### Session 1: Unified Search Pipeline (1h)

#### Step 1.1: Analyze Current executor.py (15 min)
**Goal**: Understand current UnifiedFileExplorerExecutor implementation

**Actions**:
```bash
# Read the executor file
view src/core/file_explorer_executor.py

# Check methods:
# - execute_browse()
# - execute_search()
# - execute_replace()
# - How signals are emitted (progress, done, error)
```

**Expected Findings**:
- Current method signatures
- How conditions are applied
- Progress tracking mechanism
- Error handling strategy

**Deliverable**: Mental model of executor architecture

---

#### Step 1.2: Implement Unified Pipeline Logic (30 min)
**Goal**: Merge browse/search/replace into single pipeline

**Files to modify**:
- `src/core/file_explorer_executor.py`

**Changes**:
```python
# Add unified pipeline method:
def execute_unified(self, mode: str, params: dict) -> None:
    """
    Unified execution pipeline for all modes.
    
    Args:
        mode: 'browse', 'search', or 'replace'
        params: dict with:
            - directory: str
            - file_type: str ('any', 'files', 'dirs')
            - filename_pattern: str (optional)
            - content_query: str (optional)
            - advanced_conditions: list (optional)
            - replace_text: str (optional, for replace mode)
    """
    try:
        # 1. Validate params
        # 2. Apply file_type filter
        # 3. Apply filename_pattern
        # 4. Apply content_query (if search/replace)
        # 5. Apply advanced_conditions
        # 6. Execute replace (if replace mode)
        # 7. Emit progress every 100 files
        # 8. Emit done with results
    except Exception as e:
        # 9. Emit error
        pass
```

**Testing**:
- Manual smoke test: browse mode
- Manual smoke test: search mode
- Manual smoke test: replace mode

**Rollback**: If breaks, revert file:
```bash
git checkout HEAD -- src/core/file_explorer_executor.py
```

---

#### Step 1.3: Apply Advanced Conditions (15 min)
**Goal**: Ensure conditions work in all modes

**Logic**:
```python
def _apply_conditions(self, files: list, conditions: list) -> list:
    """Apply advanced conditions with AND/OR logic"""
    if not conditions:
        return files
    
    # Circuit breaker
    MAX_FILES = 100000
    if len(files) > MAX_FILES:
        logger.warning(f"Too many files: {len(files)}, limiting to {MAX_FILES}")
        files = files[:MAX_FILES]
    
    # Apply each condition
    # Support AND/OR operators
    # Return filtered list
    pass
```

**Testing**:
- Test with size condition
- Test with mtime condition
- Test with AND/OR logic

---

### Session 2: Unit Tests (30 min)

#### Step 2.1: Create test_file_explorer_executor.py (20 min)
**Goal**: Test unified pipeline

**File**: `tests/test_file_explorer_executor.py`

**Tests to create**:
```python
def test_execute_unified_browse_mode():
    """Test browse mode returns file list"""
    pass

def test_execute_unified_search_mode():
    """Test search mode returns matches"""
    pass

def test_execute_unified_replace_mode():
    """Test replace mode modifies files"""
    pass

def test_apply_advanced_conditions_and():
    """Test AND logic in conditions"""
    pass

def test_apply_advanced_conditions_or():
    """Test OR logic in conditions"""
    pass

def test_circuit_breaker_max_files():
    """Test MAX_FILES limit"""
    pass

def test_progress_signals():
    """Test progress emitted every 100 files"""
    pass
```

**Run tests**:
```bash
export PYTHONPATH="${PWD}"
pytest tests/test_file_explorer_executor.py -v
```

**Expected**: 7/7 tests passing

---

#### Step 2.2: Run Full Test Suite (10 min)
**Goal**: Ensure no regressions

```bash
export PYTHONPATH="${PWD}"
pytest tests/ --ignore=tests/manual/ --ignore=tests/gui/ -q
```

**Expected**: Same pass rate as before (114+ passing)

**If failures**: Investigate and fix OR rollback

---

## ✅ Success Criteria

**Phase 4 is COMPLETE when**:
1. ✅ Unified pipeline implemented in file_explorer_executor.py
2. ✅ Advanced conditions work in all modes (browse/search/replace)
3. ✅ Progress tracking emits every 100 files
4. ✅ Circuit breakers in place (MAX_FILES, MAX_MATCHES)
5. ✅ 7/7 new unit tests passing
6. ✅ No regressions (existing tests still pass)
7. ✅ Code committed to COM4-code-study branch

**Definition of Done**:
```bash
# All these commands succeed:
pytest tests/test_file_explorer_executor.py -v  # 7/7 passing
pytest tests/test_file_explorer_v2_9_117.py -v  # 6/6 passing (no regression)
git status  # No uncommitted changes
git log -1  # Shows Phase 4 completion commit
```

---

## 🔙 Rollback Plan

### If Something Breaks

**Level 1: Revert single file**
```bash
git checkout HEAD -- src/core/file_explorer_executor.py
```

**Level 2: Revert all changes**
```bash
git reset --hard 96e562d  # Current HEAD before Phase 4
git clean -fd
```

**Level 3: Switch to main branch**
```bash
cd ../clarify  # Main worktree
git status  # Check main is clean
```

### Rollback Decision Matrix
| Scenario | Action | Time |
|----------|--------|------|
| Tests fail | Fix tests (10 min) OR revert file | <15 min |
| Logic broken | Revert file, rethink approach | <5 min |
| Can't figure out | Revert all, ask for help | <2 min |
| Urgent production issue | Switch to main branch immediately | <1 min |

---

## 🧪 Testing Strategy

### Phase 1: Unit Tests (During Implementation)
- Test each method as it's written
- Use pytest with -v flag
- Aim for 100% pass rate

### Phase 2: Integration Tests (After Implementation)
- Run existing v2.9.117 tests (6 tests)
- Verify no regressions
- Check signal connections still work

### Phase 3: Manual Testing (Not in this plan - Phase 6)
- Run application
- Test browse workflow
- Test search workflow
- Test replace workflow
- Verify progress bar shows
- Check conditions apply correctly

### Phase 4: Code Review (Self)
- Read code aloud
- Check for obvious bugs
- Verify circuit breakers in place
- Confirm error handling exists

---

## 📊 Time Tracking

### Estimated Time (from TASKS.md)
- **Total Phase 4**: 1.5h (90 min)
  - Session 1: 1h (unified pipeline)
  - Session 2: 30 min (unit tests)

### Actual Time Budget (Protocol-compliant)
- **Step 1.1**: 15 min (analyze executor)
- **Step 1.2**: 30 min (implement pipeline)
- **Step 1.3**: 15 min (apply conditions)
- **Step 2.1**: 20 min (create tests)
- **Step 2.2**: 10 min (run full suite)
- **Total**: 90 min ✅

### Contingency Plan
- If >90 min: Stop, commit what's done, create Phase 4.5
- If <90 min: Start Phase 5 (UI/UX) OR take break

---

## 🚨 Known Risks & Mitigations

### Risk 1: Executor complexity too high
**Probability**: Medium  
**Impact**: High (might need refactoring)  
**Mitigation**: Keep pipeline simple, delegate to helper methods

### Risk 2: Tests fail due to threading
**Probability**: Low  
**Impact**: Medium (hard to debug)  
**Mitigation**: Use pytest-qt, test without threads first

### Risk 3: Circuit breakers too restrictive
**Probability**: Low  
**Impact**: Low (user complaints)  
**Mitigation**: Use same limits as v2.9.120 (proven in production)

### Risk 4: Advanced conditions don't work
**Probability**: Medium  
**Impact**: Medium (Phase 4 incomplete)  
**Mitigation**: Test with simple condition first, add complexity incrementally

---

## 📚 References

### Code Study Documents
- **CODE_STUDY_SESSION2_NOTES.md**: FileExplorerExecutor analysis
- **CODE_STUDY_PHASE1_SUMMARY.md**: Design patterns catalog
- **GIT_HISTORY_STUDY.md**: v2.9.116 implementation history

### Protocol Documents
- **SIMPLICITY_PROTOCOL_3.md**: Step 1.8 (Planning) requirements
- **FRAGMENT_TEMP2.md**: Git workflow (COM4-code-study branch)

### Project Files
- **docs/TASKS.md**: v2.9.116 roadmap (line 11-151)
- **src/core/file_explorer_executor.py**: Main implementation file
- **tests/test_file_explorer_v2_9_117.py**: Existing integration tests

---

## 🎯 Next Steps After Phase 4

**Immediate (Phase 5 - UI/UX)**:
- Icons for sections (📁🔍⚙️🎯💾)
- Tooltips for all widgets
- Keyboard shortcuts
- Responsive layout (QScrollArea)
- Save collapse/expand state

**Then (Phase 6 - Manual Testing)**:
- Run application
- Test all workflows
- Verify UX improvements
- Check for visual bugs

**Finally (Phases 7-8)**:
- Update documentation (README, CHANGELOG)
- Create release (git tag v2.9.116)
- Deploy to production

---

## 📋 Commit Strategy

### Commit 1: Unified Pipeline (after Step 1.2)
```bash
git add src/core/file_explorer_executor.py
git commit -m "feat(v2.9.116): implement unified search pipeline (Phase 4.1)"
```

### Commit 2: Advanced Conditions (after Step 1.3)
```bash
git add src/core/file_explorer_executor.py
git commit -m "feat(v2.9.116): apply advanced conditions to all modes (Phase 4.1)"
```

### Commit 3: Unit Tests (after Step 2.1)
```bash
git add tests/test_file_explorer_executor.py
git commit -m "test(v2.9.116): add 7 unit tests for unified executor (Phase 4.2)"
```

### Commit 4: Phase 4 Complete (after Step 2.2)
```bash
git add .
git commit -m "feat(v2.9.116): Phase 4 COMPLETE - Unified logic pipeline (1.5h)"
```

---

## 🔍 Pre-Flight Checklist

**Before starting implementation**:
- [ ] ✅ Current branch: COM4-code-study
- [ ] ✅ No uncommitted changes: `git status`
- [ ] ✅ Tests passing: Previous 114+ tests OK
- [ ] ✅ Python environment: 3.12.4 active
- [ ] ✅ This ACTION PLAN committed
- [ ] ✅ TASKS.md reviewed (Phase 4 requirements clear)
- [ ] ✅ Code study documents reviewed (mental model fresh)
- [ ] ✅ 90 minutes available (no interruptions)

**Start conditions**:
```bash
cd /home/josue/Documents/.../clarify-COM4-code-study
git status  # Clean working tree
git log --oneline -3  # Verify on COM4-code-study
pytest --version  # 9.0.2
python --version  # 3.12.4
```

---

## 🎓 Protocol Compliance

**Step 1.8 Requirements** (SIMPLICITY_PROTOCOL_3.md line 6416-6477):
- [x] ✅ **Create ACTION PLAN** (this document)
- [x] ✅ **Break into 1-4h tasks** (90 min total, 2 sessions)
- [x] ✅ **Short sprints** (single phase, 1.5h)
- [x] ✅ **MVP mindset** (unified pipeline = minimum testable)
- [x] ✅ **Rollback plan** (3 levels defined)
- [x] ✅ **Testing strategy** (4 phases)
- [x] ✅ **Success criteria** (7 items, measurable)
- [x] ✅ **5-minute explanation** (TL;DR section)

**Protocol Quote** (line 6422):
> "Planning is BLOQUEANTE (BLOCKING). 5 minutes planning > 4 hours debugging alone at 2AM."

**This plan**: 10 minutes to create, saves 2-3 hours of debugging ✅

---

## ✅ PLAN APPROVED - Ready to Implement

**Programmer #4** - Following Simplicity Protocol 3  
**Date**: 2026-01-21 12:40 UTC  
**Status**: ✅ READY TO PROCEED  

**Next action**: Commit this plan, then start Step 1.1 🚀
