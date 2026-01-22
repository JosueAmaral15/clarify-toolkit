# SESSION 1 - STEP 1.4: Development Protocols - NOTES

**Programmer**: #1  
**Date**: 2026-01-14  
**Time**: 16:45  
**Duration**: 60 minutes  
**Files Read**: 2 files

---

## 📖 Files Read

1. ✅ `docs/protocolos/SIMPLICITY_PROTOCOL_3.md` (11,653 lines) - **ALREADY READ** at session start
2. ✅ `docs/protocols/PROTOCOL_CHECKLIST.md` (438 lines) - **NEW**

**Total**: 12,091 lines of protocol documentation

**Note**: SIMPLICITY_PROTOCOL_3.md was read 100% at the beginning of this documentation reading sprint. This step focuses on extracting key operational insights.

---

## 🎯 Key Findings

### Protocol Overview

**Simplicity Protocol 3 v3.0**: Hybrid protocol for solo developers in production

- **Base**: Derived from Protocols 1 & 2
- **Audience**: Solo developers with real users
- **Philosophy**: Pragmatism over perfectionism, protect sleep
- **Structure**: 16 mandatory steps + optional steps
- **Versioning**: Created for Clarify project (production environment)

### Critical Principle

> **"Proteger o sono é proteger a qualidade. Um desenvolvedor solo não pode se dar ao luxo de debugar emergências às 3h da manhã."**
>
> — SIMPLICITY_PROTOCOL_3.md

---

## ✅ 16 Mandatory Steps (Executable Checklist)

### ⭐ CRITICAL Steps (Cannot Skip)

The protocol marks 5 steps with ⭐ as **ABSOLUTELY MANDATORY** in production:

1. **Etapa 6.5**: Security Checklist (OWASP)
2. **Etapa 9.1**: Test Safety (timeout, headless, mocks)
3. **Etapa 10.6**: CI/CD Quality Gates
4. **Etapa 11**: Organize Root Folder (cleanup before commit)
5. **Etapa 12.5**: Rollback Plans

**Violating these can cause:**
- ❌ Infinite test loops (Etapa 9.1) - 10+ hours wasted
- ❌ Commits with cache files (Etapa 11) - 70+ binary files
- ❌ Production vulnerabilities (Etapa 6.5) - security breaches
- ❌ Deploys without rollback (Etapa 12.5) - irrecoverable failures

---

## 📋 Complete 16-Step Breakdown

### **Etapa 1: Context Reading (5-10 min)**

**Mandatory checklist**:
- [ ] Read complete task description (issue, comments, specs)
- [ ] Read related documentation (README, API docs, technical specs)
- [ ] Check recent change history (CHANGELOG, git log)
- [ ] Identify key files to modify (src/, tests/, docs/)

**When to skip**: Never. Always read context before coding.

**Insight**: Study documentation BEFORE any coding (Step 1.0 in protocol).

---

### **Etapa 2: Planning Before Coding (5-15 min)**

**Mandatory checklist**:
- [ ] List files to create/modify
- [ ] Identify dependencies between changes
- [ ] Estimate complexity (Simple, Medium, Complex, Very Complex)
- [ ] Break task into sub-tasks if >1 hour
- [ ] Define implementation order

**When to skip**: Trivial tasks (<10 lines, no new logic).

**Optional**: Etapa 2.5 - Decision Matrix (when 10+ tasks to prioritize).

---

### **Etapa 3: Critical Questions (2-5 min)**

**Mandatory checklist**:
- [ ] What problem am I solving exactly?
- [ ] What are the edge cases?
- [ ] Which files/functions are affected?
- [ ] Are there breaking changes?
- [ ] Do I need to update tests?
- [ ] Do I need to update documentation?

**When to skip**: Never. Always ask questions before implementation.

**Insight**: Protocol emphasizes questioning assumptions.

---

### **Etapa 4: Light Technical Design (5-10 min)**

**Mandatory checklist**:
- [ ] Define main function/class signatures
- [ ] List expected inputs/outputs
- [ ] Identify necessary libraries/APIs
- [ ] Define data structures (dicts, classes, enums)
- [ ] Note main technical decisions

**When to skip**: Trivial changes (fix typo, adjust CSS).

**Insight**: Design before code, but keep it lightweight.

---

### **Etapa 5: Implementation (60-80% of time)**

**Mandatory checklist**:
- [ ] Follow project code conventions
- [ ] Add docstrings/comments for complex logic
- [ ] Use type hints in Python (when applicable)
- [ ] Validate inputs (avoid runtime errors)
- [ ] Handle errors explicitly (try/except)

**When to skip**: Never. This is the main step.

**Insight**: 60-80% of time is actual coding, rest is quality/process.

---

### ⭐ **Etapa 6: Code Quality (5-10 min) - CRITICAL**

#### 6.1 Linting
- [ ] Run linter (pylint, flake8, mypy)
- [ ] Fix critical warnings (score >8.5/10)
- [ ] Ignore false positives (`# pylint: disable` if necessary)

#### 6.2 Formatting
- [ ] Run formatter (black, autopep8)
- [ ] Check max line length (79-120 chars)
- [ ] Remove trailing whitespace

#### 6.3 Imports
- [ ] Organize imports (stdlib, third-party, local)
- [ ] Remove unused imports

#### ⭐ 6.5 Security Checklist OWASP (MANDATORY)
- [ ] Input validation (SQL injection, XSS)
- [ ] Path traversal (CWE-22) - validate file paths
- [ ] Secrets not hardcoded (use env vars)
- [ ] Dependencies without known CVEs (pip-audit, safety)

**When to skip**: Never skip 6.5 in production.

**Clarify metric**: Pylint 9.38/10 (exceeds 8.5 target).

---

### **Etapa 7: Manual Dry-Run (2-5 min)**

**Mandatory checklist**:
- [ ] Execute code manually (not tests yet)
- [ ] Verify happy path works
- [ ] Test 2-3 edge cases manually
- [ ] Validate expected output/behavior

**When to skip**: Changes in tests only.

**Insight**: Manual smoke test before automated tests.

---

### **Etapa 8: Unit Tests (10-20% of time)**

**Mandatory checklist**:
- [ ] Create/update tests for new code
- [ ] Test happy path
- [ ] Test edge cases (extreme values)
- [ ] Test error handling
- [ ] Use mocks/fixtures when necessary

**When to skip**: Throwaway prototypes. Never skip in production.

**Clarify metric**: 97% test coverage (91/94 tests passing).

---

### ⭐ **Etapa 9: Test Execution (5-10 min) - CRITICAL**

#### ⭐ 9.1 Test Safety (MANDATORY)

**GUI Tests (pytest-qt)**:
- [ ] ✅ **Mandatory timeout**: `pytest --timeout=30` (max 30s per test)
- [ ] ✅ **Headless environment**: `QT_QPA_PLATFORM=offscreen pytest`
- [ ] ✅ **Mandatory mocks**: QMessageBox, QFileDialog in fixtures
- [ ] ✅ **Dry-run first**: `pytest --collect-only` (check syntax)

**Unit Tests**:
- [ ] Run full test suite: `pytest tests/`
- [ ] Check coverage: `pytest --cov=src --cov-report=term`
- [ ] Target: >80% coverage on critical code

**CRITICAL**: Violating 9.1 can cause:
- ❌ 10+ hour test runs (infinite loop)
- ❌ Blocked CI/CD pipelines
- ❌ Indefinitely frozen terminals

**Historical Example (v2.9.40.4)**:
```bash
# ❌ WRONG (caused infinite loop):
pytest tests/gui/test_editor_dock.py

# ✅ CORRECT (11.61s):
QT_QPA_PLATFORM=offscreen pytest tests/gui/ --timeout=30 -v
```

**Performance improvement**: 3000x (10+ hours → 11.61s)

**When to skip**: Never skip 9.1 on GUI tests.

---

### **Etapa 10: Quality Validation (5-10 min)**

#### 10.1 Smoke Test
- [ ] Run application locally
- [ ] Test main implemented feature
- [ ] Verify didn't break existing features

#### 10.2 Performance Check
- [ ] Validate interactive operations <1s
- [ ] Validate background operations <5s
- [ ] Use `time` or profiler if necessary

#### ⭐ 10.6 CI/CD Quality Gates (MANDATORY)
- [ ] Automated tests pass (100%)
- [ ] Linting passes (score >8.5/10)
- [ ] Security scan passes (0 critical CVEs)
- [ ] Build succeeds (no errors)

**Optional**: Etapa 10.5 - Profiling (when feature >1s).

**When to skip**: Never skip 10.6 in production.

---

### ⭐ **Etapa 11: Organize Root Folder (2 min) - CRITICAL**

**CRITICAL**: This step **was always forgotten** until v2.9.40.4.

**Mandatory Commands** (BEFORE commit):
```bash
# 1. Remove __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Remove .pytest_cache
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# 3. Remove *.pyc, *.pyo
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# 4. Remove accidental backups
rm -f *.backup_* *.bak *~ 2>/dev/null

# 5. Verify cleanup
git status
```

**Checklist**:
- [ ] ✅ Remove `__pycache__/` recursively
- [ ] ✅ Remove `.pytest_cache/`
- [ ] ✅ Remove `*.pyc`, `*.pyo`
- [ ] ✅ Remove backup files (`*.bak`, `*~`, `*.backup_*`)
- [ ] ✅ Verify `git status` before commit

**PREVENTION**: Add to `.gitignore`:
```gitignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.bak
*~
*.backup_*
```

**Consequence of skipping**: Polluted commits with 70+ binary files (as happened before v2.9.40.4).

**When to skip**: Never. Always execute before `git commit`.

**Optional**: Etapa 11.5 - Decision Notes (simplified ADR for complex decisions).

---

### **Etapa 12: Documentation (10-15 min)**

#### 12.1 CHANGELOG.md
- [ ] Add entry with version (v2.9.X.Y)
- [ ] Describe problem/feature
- [ ] List modified files
- [ ] Document breaking changes (if any)

#### 12.2 TASKS.md
- [ ] Mark task as complete `[X]`
- [ ] Add version reference
- [ ] Update statistics if necessary

#### 12.3 Docstrings/Comments
- [ ] Add docstrings to public functions
- [ ] Comment complex logic
- [ ] Update outdated comments

#### ⭐ 12.5 Rollback Plans (MANDATORY)
- [ ] Document how to revert change if it fails
- [ ] Test rollback in local environment
- [ ] Include rollback commands in CHANGELOG

**Example**:
```markdown
## Rollback (if necessary)
git revert cea7797  # Reverts commit v2.9.40.4
git tag -d v2.9.40.4  # Removes local tag
git push origin :refs/tags/v2.9.40.4  # Removes remote tag
```

**When to skip**: Never skip 12.5 in production.

---

### **Etapa 13: Commit + Tag + Push + Beeps (5 min)**

#### 13.1 Git Commit
- [ ] Follow Conventional Commits: `fix:`, `feat:`, `docs:`
- [ ] Descriptive message (problem + solution)
- [ ] List modified files in body

#### 13.2 Git Tag
- [ ] Create annotated tag: `git tag v2.9.X.Y -a -m "message"`
- [ ] Include summarized changelog in tag

#### 13.3 Git Push
- [ ] Push commit: `git push origin main`
- [ ] Push tag: `git push origin v2.9.X.Y`

#### 13.4 Beeps (MANDATORY - Acoustic Confirmation)
- [ ] Play beeps: `paplay beeps/three-beeps.mp3`
- [ ] If headless: mark as executed in commit message

**When to skip**: Never. Beeps confirm successful deploy.

**Insight**: Acoustic feedback as deployment confirmation (unique to solo dev).

---

## 📊 Optional Steps (Pragmatic)

### **Etapa 2.5: Decision Matrix (when 10+ tasks)**

**When to use**: Roadmap with many competing tasks.

**Template**:
| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Task A | High | Low | **P0** |
| Task B | Medium | High | P2 |

---

### **Etapa 10.5: Profiling (when feature >1s)**

**When to use**: Slow feature detected in Step 10.2.

**Tools**:
- Python: `cProfile`, `line_profiler`
- GUI: Qt profiler, QElapsedTimer

**Commands**:
```bash
python -m cProfile -s cumtime src/app.py
```

---

### **Etapa 11.5: Decision Notes (simplified ADR)**

**When to use**: Complex architectural decisions (e.g., library choice, algorithm).

**Simple Template**:
```markdown
# Decision: [Title]
Date: YYYY-MM-DD
Status: Accepted/Rejected

## Context
[Why do we need to decide?]

## Options Considered
1. Option A (pros/cons)
2. Option B (pros/cons)

## Decision
We chose Option A because...

## Consequences
- Impact 1
- Impact 2
```

---

## 🚨 Historical Violations (Lessons Learned)

### v2.9.40.4: Infinite Loop (Violation of Step 9.1)

**Symptom**: GUI tests ran 10+ hours without finishing.

**Root Cause**:
- ❌ No timeout applied (`--timeout=30`)
- ❌ Not configured headless (`QT_QPA_PLATFORM=offscreen`)
- ❌ QMessageBox not mocked in fixture

**Consequence**: Infinite loop, 10+ hours lost.

**Solution**: Apply **ALL** rules from Step 9.1.

**Performance**: 3000x improvement (10+ hours → 11.61s).

---

### v2.9.40.4: Polluted Commits (Violation of Step 11)

**Symptom**: 70 `__pycache__/*.pyc` files accidentally committed.

**Root Cause**:
- ❌ Step 11 never executed before this version
- ❌ `.gitignore` didn't ignore `__pycache__/`

**Consequence**: Polluted commits, dirty history.

**Solution**:
1. Execute cleanup commands (Step 11)
2. Add preventive `.gitignore`

---

## 📝 Usage Patterns

### For New Features

1. Follow steps 1-13 in order
2. Don't skip mandatory steps (⭐)
3. Use optional steps when it makes sense

### For Hotfixes

1. Skip Step 2 (planning) if obvious
2. Keep Step 6.5 (security) always
3. Keep Step 11 (cleanup) always
4. Execute quickly (<30 min total)

### For Refactoring

1. Keep Step 8 (tests) mandatory
2. Add Step 10.5 (profiling) if performance-critical
3. Document decisions in Step 11.5 (ADR notes)

---

## ✅ Quick Checklist (Before Commit)

**Absolute Minimum**:
- [ ] ✅ Step 6.5: Security check (OWASP)
- [ ] ✅ Step 9.1: Tests with timeout + headless + mocks
- [ ] ✅ Step 11: Organize root folder (`__pycache__`, `.pytest_cache`)
- [ ] ✅ Step 12.5: Documented rollback plan
- [ ] ✅ Step 13: Commit + Tag + Push + Beeps

**If skipping any**: High risk of production bug.

---

## 🎯 Compliance Goals

**Target**: 100% compliance on production commits.

**Tracking**: Review this checklist every 10 commits.

**Review**: Update checklist when protocol evolves.

---

## 💡 Key Insights

### Protocol Philosophy

1. **Pragmatism over Perfectionism** - Ship incrementally, improve iteratively
2. **Protect Sleep** - Avoid 3 AM debugging emergencies
3. **Study Before Code** - Always read documentation first (Step 1)
4. **Test Safety First** - Prevent infinite loops (Step 9.1)
5. **Clean Commits** - No cache files in history (Step 11)
6. **Rollback Capability** - Always have escape route (Step 12.5)
7. **Acoustic Confirmation** - Beeps as deployment signal (Step 13.4)

### Solo Developer Adaptations

**Differences from team protocols**:
- Fewer code reviews (self-review with checklists)
- More emphasis on rollback plans (no team backup)
- Acoustic feedback (beeps) for confirmation
- Mandatory security checks (OWASP) - no security team
- CI/CD quality gates enforced (no DevOps team)

### Clarify-Specific Metrics

**Compliance tracking**:
- Pylint: >8.5/10 (actual: 9.38/10)
- Test coverage: >80% critical code (actual: 97%)
- Test execution: <30s per test (with timeout)
- Security: 0 critical CVEs

---

## 📊 Progress Tracking

### Session 1 - Step 1.4: Development Protocols ✅
- [x] Read `docs/protocolos/SIMPLICITY_PROTOCOL_3.md` (already read - 11,653 lines)
- [x] Read `docs/protocols/PROTOCOL_CHECKLIST.md` (438 lines)
- [x] Extract operational insights
- [x] Understand 16 mandatory steps
- [x] Identify 5 critical steps (⭐)
- [x] Document historical violations
- [x] Create `SESSION_1_STEP_4_NOTES_1.md`

**Time spent**: 60 minutes  
**Lines processed**: 12,091 lines (11,653 + 438)  
**Next step**: SESSION 1 - SUMMARY (Consolidate Session 1 findings)

---

## 🔑 Action Items

### Immediate (Session 1 Summary)
1. Consolidate findings from Steps 1.1-1.4
2. Create comprehensive SESSION_1_SUMMARY_1.md
3. Update reading progress tracking

### Short-term (Session 2+)
1. Apply protocol checklist in practice
2. Review historical violations for lessons
3. Understand CI/CD pipeline implementation
4. Study security checklist application in Clarify

### Medium-term
1. Review all 16 steps in detail in SIMPLICITY_PROTOCOL_3.md
2. Understand optional steps use cases
3. Study ADR templates for decision documentation
4. Learn rollback procedures

---

## 📖 Protocol Versioning

**Current**: Simplicity Protocol 3 v3.0

**History**:
- **Protocol 1**: 13 mandatory steps (for prototypes/internal projects)
- **Protocol 2**: 23 steps (13 mandatory + 10 optional) (for enterprise teams)
- **Protocol 3**: 16 steps (hybrid) (for solo developers in production) ⭐

**Evolution**: Protocol 3 is specifically tailored for Clarify's solo developer + production user context.

---

## 🔧 Tools & Commands Summary

### Test Execution (Step 9.1)
```bash
# GUI tests (correct way)
QT_QPA_PLATFORM=offscreen pytest tests/gui/ --timeout=30 -v

# Unit tests with coverage
pytest tests/ --cov=src --cov-report=term

# Dry-run (syntax check)
pytest --collect-only
```

### Cleanup (Step 11)
```bash
# Remove all cache/temp files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
rm -f *.backup_* *.bak *~ 2>/dev/null

# Verify
git status
```

### Deployment (Step 13)
```bash
# Commit with Conventional Commits
git add .
git commit -m "feat: Add feature X"

# Tag
git tag v2.9.X.Y -a -m "Release notes"

# Push
git push origin main
git push origin v2.9.X.Y

# Beeps (acoustic confirmation)
paplay beeps/three-beeps.mp3
```

### Rollback (Step 12.5)
```bash
# Revert commit
git revert <commit-hash>

# Remove tag
git tag -d v2.9.X.Y
git push origin :refs/tags/v2.9.X.Y
```

---

## 🎓 Lessons from Historical Violations

### Lesson 1: Test Safety is Non-Negotiable
**Context**: v2.9.40.4 infinite loop  
**Takeaway**: Always apply timeout + headless + mocks on GUI tests  
**Impact**: 3000x performance improvement

### Lesson 2: Clean Before Commit
**Context**: v2.9.40.4 polluted commits  
**Takeaway**: Execute Step 11 cleanup BEFORE every commit  
**Impact**: Clean git history, no binary files

### Lesson 3: Checklists Save Time
**Context**: Repeated forgetting of Step 11  
**Takeaway**: Follow PROTOCOL_CHECKLIST.md every time  
**Impact**: Prevented future violations

---

## 📌 Golden Rules (Programmer #1)

1. **Always read context first** (Step 1) - No coding before understanding
2. **Never skip security** (Step 6.5) - Solo dev = sole defender
3. **Timeout every GUI test** (Step 9.1) - Prevent infinite loops
4. **Clean before commit** (Step 11) - Protect git history
5. **Document rollback** (Step 12.5) - Always have escape hatch
6. **Beep on deploy** (Step 13.4) - Confirm success

---

**End of Step 1.4 Notes**

**Protocol Compliance**: This session followed SIMPLICITY_PROTOCOL_3 Step 1.0 (Leitura de Contexto) - Read 100% of protocol documentation before starting work.

**Next**: Create SESSION_1_SUMMARY_1.md consolidating all findings from Steps 1.1-1.4.
