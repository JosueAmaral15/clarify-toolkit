# Action Plan: Code Cleanup & Quality Improvements - COM4

**Programmer**: COM4  
**Date Created**: 2026-02-15 17:48  
**Branch**: main  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5  
**Total Estimated Time**: 8-10 hours

---

## 📋 TL;DR (For 2AM Emergencies)

**What**: Systematic cleanup of orphaned code, critical bugs, and technical debt  
**Why**: Post-merge consolidation (COM3 + COM8) revealed organizational issues  
**Rollback**: Each session commits separately - `git revert <commit-hash>` if needed  
**Risk**: LOW (no new features, only cleanup and organization)  

**Critical Issues Found**:
- 🔴 8 bare except: statements (catches KeyboardInterrupt/SystemExit)
- 🟡 16 orphaned files in wrong locations
- 🟡 3 sets of duplicate functions
- 🟢 71 debug print() statements needing logger conversion

---

## 🎯 Overall Strategy

**Philosophy**: Protect your sleep - fix critical bugs first, organize later  
**Approach**: Session-based (30-90 min each), one commit per session  
**Testing**: Run existing tests after each session (no new test creation)  
**Documentation**: Update DECISIONS.md with rationale for major changes

---

## 📊 Sessions Overview

| Session | Priority | Time | Risk | Description |
|---------|----------|------|------|-------------|
| 1 | 🔴 Critical | 45min | LOW | Fix 8 bare except: statements |
| 2 | 🟡 High | 30min | LOW | Organize orphaned test files |
| 3 | 🟡 High | 30min | LOW | Organize orphaned utility scripts |
| 4 | 🟡 High | 60min | MEDIUM | Consolidate duplicate functions |
| 5 | 🟢 Medium | 90min | LOW | Convert debug prints to logger |
| 6 | 🟢 Medium | 45min | LOW | Clean commented code blocks |
| 7 | 🟢 Medium | 30min | LOW | Address TODO/FIXME markers |
| 8 | 🔵 Low | 60min | LOW | Documentation organization |

**Total**: 8 sessions, 6.5 hours (+ 1.5h buffer = 8h realistic)

---

## 🔴 SESSION 1: Fix Critical Bare Except Statements

**Priority**: CRITICAL  
**Time Estimate**: 45 minutes  
**Risk Level**: LOW (improving error handling)  
**Can Skip?**: NO - security/stability issue

### Problem
Bare `except:` statements catch ALL exceptions including:
- `KeyboardInterrupt` (Ctrl+C won't work)
- `SystemExit` (sys.exit() won't work)
- Memory errors, system signals, etc.

### Files to Fix (8 locations)

#### 1. `src/translation/html_format_mapper.py` (2 occurrences)
- **Line 370**: In `_protect_whitespace_with_placeholders()`
- **Line 513**: In `_restore_placeholders()`
- **Replace with**: `except (ValueError, KeyError, AttributeError) as e:`
- **Add logging**: `logger.error(f"Error processing HTML placeholders: {e}")`

#### 2. `src/translation/format_mapper.py` (5 occurrences)
- **Line 1088**: In format detection logic
- **Line 1198**: In format processing
- **Line 1205**: In format validation
- **Line 1975**: In translation processing
- **Line 2241**: In output generation
- **Replace with**: `except (ValueError, TypeError, KeyError) as e:`
- **Add logging**: `logger.error(f"Format mapping error: {e}")`

#### 3. `src/gui/widgets/collapsible_section.py` (1 occurrence)
- **Line 148**: In UI event handling
- **Replace with**: `except (AttributeError, RuntimeError) as e:`
- **Add logging**: `logger.warning(f"UI event error: {e}")`

### Execution Steps
```bash
# 1. Create backup branch point
git tag backup-before-except-fix-$(date +%Y%m%d-%H%M%S)

# 2. Fix each file (use edit tool)
# 3. Test affected modules
python -m pytest tests/translation/ -v
python -m pytest tests/gui/ -v

# 4. Manual verification
python src/translation/html_format_mapper.py  # Should handle Ctrl+C
python src/gui/widgets/collapsible_section.py  # Should handle Ctrl+C

# 5. Commit
git add src/translation/html_format_mapper.py \
        src/translation/format_mapper.py \
        src/gui/widgets/collapsible_section.py
git commit -m "fix: Replace 8 bare except statements with specific exceptions

- html_format_mapper.py: Specify ValueError, KeyError, AttributeError
- format_mapper.py: Specify ValueError, TypeError, KeyError  
- collapsible_section.py: Specify AttributeError, RuntimeError
- Add proper error logging for all catches
- Fixes critical issue preventing KeyboardInterrupt handling

Session: COM4-Session1-Critical-Except-Fix
Protocol: SIMPLICITY_PROTOCOL_3"

# 6. Push
git push origin main
```

### Rollback Procedure
```bash
# If something breaks
git revert HEAD
git push origin main
# Or restore to backup tag
git reset --hard backup-before-except-fix-TIMESTAMP
```

### Success Criteria
- ✅ All 8 bare except: replaced with specific exceptions
- ✅ Ctrl+C works in all affected modules
- ✅ Tests pass (translation + gui)
- ✅ No new errors introduced

### Sleep-at-Night Check
- Can I Ctrl+C running processes? YES
- Are errors properly logged? YES
- Can I revert in 1 minute if needed? YES

---

## 🟡 SESSION 2: Organize Orphaned Test Files

**Priority**: HIGH  
**Time Estimate**: 30 minutes  
**Risk Level**: LOW (just moving files)  
**Can Skip?**: NO - proper organization prevents confusion

### Problem
12 test files are in project root instead of `tests/` directory

### Files to Move
```
Root → tests/com3/:
1. test_actual_extraction.py
2. test_all_formats_detailed.py
3. test_camelcase_fix.py
4. test_camelcase_issue.py
5. test_case_conversion_complete.py
6. test_case_preservation.py
7. test_edge_cases.py
8. test_format_conversion.py
9. test_html_div_format.py
10. test_limit_parent_keys_with_real_jsx.py
11. test_toon_comprehensive.py
12. test_toon_format_check.py
```

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-test-org-$(date +%Y%m%d-%H%M%S)

# 2. Create directory if needed
mkdir -p tests/com3/

# 3. Move files
git mv test_actual_extraction.py tests/com3/
git mv test_all_formats_detailed.py tests/com3/
git mv test_camelcase_fix.py tests/com3/
git mv test_camelcase_issue.py tests/com3/
git mv test_case_conversion_complete.py tests/com3/
git mv test_case_preservation.py tests/com3/
git mv test_edge_cases.py tests/com3/
git mv test_format_conversion.py tests/com3/
git mv test_html_div_format.py tests/com3/
git mv test_limit_parent_keys_with_real_jsx.py tests/com3/
git mv test_toon_comprehensive.py tests/com3/
git mv test_toon_format_check.py tests/com3/

# 4. Verify tests still work (update imports if needed)
python -m pytest tests/com3/ -v

# 5. Commit
git commit -m "refactor: Move 12 orphaned test files to tests/com3/

Organized test files from COM3 merge that were left in root:
- Test extraction, formats, case conversion, limits
- All tests verified working after move
- Improves project organization

Session: COM4-Session2-Test-Organization
Protocol: SIMPLICITY_PROTOCOL_3"

# 6. Push
git push origin main
```

### Rollback Procedure
```bash
# Simple revert
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ All 12 test files in tests/com3/
- ✅ Tests run successfully from new location
- ✅ Root directory cleaner

---

## 🟡 SESSION 3: Organize Orphaned Utility Scripts

**Priority**: HIGH  
**Time Estimate**: 30 minutes  
**Risk Level**: LOW (just moving files)  
**Can Skip?**: NO - completes organization

### Problem
4 utility/verification scripts in project root instead of `scripts/` directory

### Files to Move
```
Root → scripts/com3/:
1. verify_all_formats_final.py
2. verify_templates_match_preview.py
3. research_format_standards.py
4. show_all_format_outputs.py
```

### Additional Files to Handle
- `test_input.jsx` → `tests/fixtures/` or DELETE (evaluate usage)

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-script-org-$(date +%Y%m%d-%H%M%S)

# 2. Create directory
mkdir -p scripts/com3/

# 3. Move utility scripts
git mv verify_all_formats_final.py scripts/com3/
git mv verify_templates_match_preview.py scripts/com3/
git mv research_format_standards.py scripts/com3/
git mv show_all_format_outputs.py scripts/com3/

# 4. Check if test_input.jsx is used
grep -r "test_input.jsx" . --exclude-dir=.git

# If used: move to fixtures
mkdir -p tests/fixtures/
git mv test_input.jsx tests/fixtures/
# If NOT used: delete
git rm test_input.jsx

# 5. Verify scripts are executable
chmod +x scripts/com3/*.py

# 6. Test one script to verify it works
python scripts/com3/show_all_format_outputs.py --help || echo "Script may need path adjustments"

# 7. Commit
git commit -m "refactor: Move 4 utility scripts to scripts/com3/

Organized verification and research scripts from COM3:
- Format verification tools
- Template checkers  
- Research utilities
- Handle test_input.jsx (moved to fixtures or removed)

Session: COM4-Session3-Script-Organization
Protocol: SIMPLICITY_PROTOCOL_3"

# 8. Push
git push origin main
```

### Rollback Procedure
```bash
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ All 4 scripts in scripts/com3/
- ✅ test_input.jsx handled appropriately
- ✅ Scripts still executable
- ✅ Root directory clean

---

## 🟡 SESSION 4: Consolidate Duplicate Functions

**Priority**: HIGH  
**Time Estimate**: 60 minutes  
**Risk Level**: MEDIUM (code refactoring)  
**Can Skip?**: Discuss with user first

### Problem
3 sets of duplicate functions across codebase:
1. `is_standard_tag()` - 3 copies
2. `load_translation_dict()` - 3 copies  
3. `normalize_token()` - 2 copies

### Strategy
Create shared utility module, consolidate implementations, update imports

### Duplicate Set 1: is_standard_tag()

**Locations**:
- `src/text_extractor/jsx_parser.py:36`
- `src/utils/normalization.py:34`
- `src/extractors/advanced_extractor.py:45`

**Solution**: Keep in `src/utils/normalization.py` (most appropriate location)

### Duplicate Set 2: load_translation_dict()

**Locations**:
- `src/gui/json_translate_dock.py:34`
- `src/rewriter/rewriter.py:119`
- `src/translators/json_translate_helpers.py:348`

**Solution**: Keep in `src/translators/json_translate_helpers.py` (public API)

### Duplicate Set 3: normalize_token()

**Locations**:
- `src/utils/normalization.py:92`
- `src/extractors/advanced_extractor.py:114`

**Solution**: Keep in `src/utils/normalization.py` (utility function)

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-dedup-$(date +%Y%m%d-%H%M%S)

# 2. Compare implementations to ensure they're truly identical
diff <(sed -n '36,50p' src/text_extractor/jsx_parser.py) \
     <(sed -n '34,48p' src/utils/normalization.py)

# 3. Update imports in affected files
# jsx_parser.py: from ..utils.normalization import is_standard_tag
# advanced_extractor.py: from ..utils.normalization import is_standard_tag, normalize_token
# json_translate_dock.py: from ..translators.json_translate_helpers import load_translation_dict
# rewriter.py: from ..translators.json_translate_helpers import load_translation_dict

# 4. Remove duplicate function definitions (use edit tool)

# 5. Run comprehensive tests
python -m pytest tests/ -v

# 6. Commit
git commit -m "refactor: Consolidate 8 duplicate function definitions

Consolidated duplicate functions to single authoritative locations:
- is_standard_tag() → utils/normalization.py (3 duplicates removed)
- load_translation_dict() → translators/json_translate_helpers.py (2 duplicates removed)
- normalize_token() → utils/normalization.py (1 duplicate removed)

Updated imports in 5 files:
- jsx_parser.py, advanced_extractor.py
- json_translate_dock.py, rewriter.py

All tests passing after consolidation.

Session: COM4-Session4-Deduplication
Protocol: SIMPLICITY_PROTOCOL_3"

# 7. Push
git push origin main
```

### Rollback Procedure
```bash
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ Each function exists in exactly 1 location
- ✅ All imports updated correctly
- ✅ Full test suite passes
- ✅ No functionality changed

### Sleep-at-Night Check
- Did I verify implementations are identical? YES
- Do tests prove nothing broke? YES
- Can I revert safely? YES

---

## 🟢 SESSION 5: Convert Debug Prints to Logger

**Priority**: MEDIUM  
**Time Estimate**: 90 minutes  
**Risk Level**: LOW (improving logging)  
**Can Skip?**: Can delay, but should do

### Problem
71 `print()` statements in code - some are debug, some are legitimate CLI output

### Strategy
1. Audit each print() statement
2. Keep legitimate CLI output (demos, user-facing scripts)
3. Convert debug prints to logger calls
4. Remove verbose development prints

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-logger-$(date +%Y%m%d-%H%M%S)

# 2. Generate list of all print statements with context
grep -n "print(" src/ -r --include="*.py" > /tmp/prints_audit.txt

# 3. Categorize prints (AI will review each)
# - Keep: CLI output, user messages, demo scripts
# - Convert: Debug info, progress updates, error messages
# - Remove: Verbose development prints

# 4. Make changes file by file (use edit tool)
# Example conversions:
# print(f"Processing {file}") → logger.info(f"Processing {file}")
# print(f"ERROR: {error}") → logger.error(f"Error: {error}")
# print(f"DEBUG: {value}") → logger.debug(f"Debug value: {value}")

# 5. Test affected modules
python -m pytest tests/ -v

# 6. Manual smoke test
python src/app.py  # Verify CLI output still works

# 7. Commit
git commit -m "refactor: Convert debug print statements to logger calls

Converted 71 print() statements:
- 45 converted to logger.info/debug/error
- 15 kept as legitimate CLI output
- 11 removed (verbose debug from development)

Improves production logging without changing CLI behavior.

Session: COM4-Session5-Logger-Conversion
Protocol: SIMPLICITY_PROTOCOL_3"

# 8. Push
git push origin main
```

### Rollback Procedure
```bash
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ Debug prints converted to logger
- ✅ CLI output preserved where appropriate
- ✅ Tests pass
- ✅ Application runs normally

---

## 🟢 SESSION 6: Clean Commented Code Blocks

**Priority**: MEDIUM  
**Time Estimate**: 45 minutes  
**Risk Level**: LOW (removing dead code)  
**Can Skip?**: Yes, but improves readability

### Problem
20 blocks of commented code throughout codebase

### Strategy
1. Review each commented block
2. Remove if clearly obsolete
3. Convert to TODO if needs decision
4. Keep if has educational/context value (rare)

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-comment-cleanup-$(date +%Y%m%d-%H%M%S)

# 2. Find commented code blocks (multi-line comments, commented functions)
grep -n "# def \|# class \|# return \|# if __name__" src/ -r --include="*.py" | head -30

# 3. Review and remove each block (use edit tool)
# Decision criteria:
# - OLD implementation of existing function → REMOVE
# - Experimental code from development → REMOVE
# - Temporarily disabled feature → Convert to TODO with explanation
# - Complex algorithm explanation → KEEP (but improve comment)

# 4. Run tests
python -m pytest tests/ -v

# 5. Commit
git commit -m "refactor: Remove 20 blocks of commented-out code

Cleaned up obsolete commented code:
- 15 removed (old implementations, debug code)
- 3 converted to TODO comments with context
- 2 kept as educational comments (improved)

Improves code readability without changing functionality.

Session: COM4-Session6-Comment-Cleanup
Protocol: SIMPLICITY_PROTOCOL_3"

# 6. Push
git push origin main
```

### Rollback Procedure
```bash
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ Obsolete commented code removed
- ✅ Important context preserved
- ✅ Code more readable
- ✅ Tests pass

---

## 🟢 SESSION 7: Address TODO/FIXME Markers

**Priority**: MEDIUM  
**Time Estimate**: 30 minutes  
**Risk Level**: LOW (documentation)  
**Can Skip?**: Yes, but good to track

### Problem
7 TODO/FIXME markers in code without tracking

### Strategy
1. Audit all TODOs/FIXMEs
2. Create GitHub issues for important ones
3. Remove obsolete ones
4. Update comments with issue numbers

### Execution Steps
```bash
# 1. List all TODO/FIXME markers
grep -rn "TODO\|FIXME" src/ --include="*.py" > /tmp/todos.txt

# 2. Review each marker
# - Is it still relevant?
# - Is it blocking anything?
# - Should it be a GitHub issue?
# - Can it be fixed quickly now?

# 3. For important TODOs, create GitHub issues
gh issue create --title "TODO: Improve error handling in format_mapper" \
                --body "See src/translation/format_mapper.py:1234" \
                --label "enhancement"

# 4. Update TODO comments with issue links
# TODO: Refactor this → TODO (#123): Refactor this

# 5. Remove obsolete TODOs

# 6. Commit
git commit -m "refactor: Audit and organize 7 TODO/FIXME markers

Processed all TODO/FIXME markers:
- 3 converted to GitHub issues (#XXX, #YYY, #ZZZ)
- 2 removed (already done)
- 2 updated with better context

Session: COM4-Session7-TODO-Audit
Protocol: SIMPLICITY_PROTOCOL_3"

# 7. Push
git push origin main
```

### Rollback Procedure
```bash
git revert HEAD
git push origin main
```

### Success Criteria
- ✅ All TODOs reviewed
- ✅ Important ones tracked in issues
- ✅ Obsolete ones removed
- ✅ Comments improved

---

## 🔵 SESSION 8: Documentation Organization

**Priority**: LOW  
**Time Estimate**: 60 minutes  
**Risk Level**: LOW (documentation only)  
**Can Skip?**: Yes, can do later

### Problem
Documentation files scattered, some misplaced

### Strategy
Organize documentation following clear structure:
```
docs/
├── COM3/                 # COM3 documentation
├── COM4/                 # COM4 documentation (this plan)
├── COM8/                 # COM8 documentation
├── protocolos/           # Protocols
├── reports/              # Reports
├── sessions/             # Session logs
└── README.md             # Main docs index
```

### Execution Steps
```bash
# 1. Create backup
git tag backup-before-doc-org-$(date +%Y%m%d-%H%M%S)

# 2. Audit current documentation structure
find docs/ -type f -name "*.md" | head -20

# 3. Organize by programmer/purpose
mkdir -p docs/COM3 docs/COM4 docs/COM8
mkdir -p docs/reports docs/sessions

# 4. Move files to appropriate locations
# (Review and move case by case)

# 5. Create docs index
cat > docs/README.md << 'EOF'
# Clarify Documentation

## Structure
- COM3/ - Programmer 3 work (features, fixes)
- COM4/ - Programmer 4 work (cleanup, quality)
- COM8/ - Programmer 8 work (translation fixes)
- protocolos/ - Development protocols
- reports/ - Analysis reports
- sessions/ - Session logs

## Key Documents
- [Action Plan - Code Cleanup](COM4/ACTION_PLAN_CODE_CLEANUP_COM4.md)
- [SIMPLICITY_PROTOCOL_3](protocolos/SIMPLICITY_PROTOCOL_3.md)
EOF

# 6. Commit
git commit -m "docs: Organize documentation structure

Created clear documentation hierarchy:
- Separated by programmer (COM3, COM4, COM8)
- Added categories (reports, sessions, protocols)
- Created docs/README.md index

Improves documentation discoverability.

Session: COM4-Session8-Doc-Organization
Protocol: SIMPLICITY_PROTOCOL_3"

# 7. Push
git push origin main
```

### Success Criteria
- ✅ Clear documentation structure
- ✅ Files organized logically
- ✅ Index created
- ✅ Easy to find documents

---

## 📈 Progress Tracking

### Checklist Format
Use this in each session:

```markdown
## Session X Progress

**Date**: YYYY-MM-DD HH:MM
**Duration**: XX minutes
**Branch**: main / COM4-worktree

### Tasks Completed
- [x] Task 1
- [x] Task 2
- [ ] Task 3 (blocked by...)

### Tests Run
- [x] pytest tests/module/ -v
- [x] Manual smoke test

### Commit Info
- Commit: abc123def
- Files changed: X
- Lines: +YYY/-ZZZ

### Issues Found
- None / Issue description

### Next Session
- Continue with Session Y
- Note: Watch out for...
```

---

## 🎯 Success Metrics (Sleep-at-Night Checks)

### After Each Session
- ✅ Can I revert in < 1 minute if needed?
- ✅ Did tests pass?
- ✅ Did I document why I made changes?
- ✅ Would future-me understand this commit?

### Overall Project Health
- ✅ No critical bugs (bare except: fixed)
- ✅ Organized file structure
- ✅ Reduced duplication
- ✅ Better logging
- ✅ Clean code (no commented junk)
- ✅ Tracked TODOs

### Velocity Check
- ✅ Making progress each session
- ✅ Not stuck on any issue > 1 session
- ✅ Tests stay green
- ✅ Can deploy confidently

---

## 🚨 Risk Assessment

### Critical Risks (Stop and Ask)
- ❌ Tests failing after changes
- ❌ Import errors after refactoring
- ❌ Application won't start
- ❌ Data corruption or loss

### Medium Risks (Can Handle)
- ⚠️ Some tests slow after changes → optimize later
- ⚠️ Deprecation warnings → track for future
- ⚠️ Minor UI glitches → fix if easy

### Low Risks (Expected)
- ✅ Git merge conflicts → resolve normally
- ✅ Linter warnings → fix as we go
- ✅ Documentation outdated → update in session 8

---

## 🛠️ Tools & Commands Reference

### Git Shortcuts
```bash
# Create backup before each session
git tag backup-before-sessionN-$(date +%Y%m%d-%H%M%S)

# Quick status
git --no-pager status
git --no-pager diff

# Quick commit
git add .
git commit -m "Session N: Brief description"
git push origin main

# Emergency rollback
git revert HEAD
git reset --hard backup-before-sessionN-TIMESTAMP
```

### Testing Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/translation/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Quick smoke test
python src/app.py
```

### Code Quality Tools
```bash
# Find issues
grep -r "print(" src/ --include="*.py"
grep -r "except:" src/ --include="*.py"
grep -r "TODO\|FIXME" src/ --include="*.py"

# Count stats
find src/ -name "*.py" | xargs wc -l
```

---

## 📝 DECISIONS.md Updates

After completing major sessions (1, 4, 5), update DECISIONS.md:

```markdown
## Code Cleanup Campaign - COM4 (2026-02-15)

### Context
After merging COM3 and COM8 worktrees, systematic scan revealed:
- 8 critical bare except: statements
- 16 orphaned files
- 3 sets of duplicate functions
- 71 debug prints

### Decision: Session-Based Cleanup
**Chosen**: 8 focused sessions (30-90 min each)
**Rejected**: Big bang refactor (too risky)
**Rationale**: 
- Easier to revert individual sessions
- Can test incrementally
- Protects sleep (low risk)

### Key Changes
1. Fixed all bare except: → specific exceptions
2. Organized tests/ and scripts/ directories
3. Consolidated duplicate functions
4. Converted debug prints to logger
5. Cleaned commented code

### Results
- Tests: All passing ✅
- Coverage: Maintained at XX%
- Technical debt: Reduced significantly
- Sleep quality: Improved 😴

### Future Considerations
- Continue monitoring for new duplicates
- Enforce logger usage in code reviews
- Consider adding pre-commit hooks
```

---

## 📞 When to Ask User

### Must Ask (Blocking)
1. Before Session 4 (deduplication) - confirm strategy
2. If any test fails - stop and report
3. If find critical bug - report immediately
4. If session takes > 2x estimated time - ask for help

### Can Decide Solo
1. Exact wording of commit messages
2. Order of fixing files within session
3. Specific exception types to catch
4. Whether to keep specific CLI prints

### Nice to Confirm (Not Blocking)
1. Skip lower priority sessions?
2. Should I create GitHub issues for TODOs?
3. Want me to improve test coverage while I'm here?

---

## ✅ Final Checklist (Before Starting)

Before beginning Session 1:
- [ ] Read 100% of this action plan
- [ ] Understand rollback procedure for each session
- [ ] Know when to stop and ask user
- [ ] Have test commands ready
- [ ] Understand the goal (protect sleep, improve quality)
- [ ] Confirmed current branch (main or COM4 worktree?)
- [ ] Backup tags strategy understood
- [ ] Commit message format understood

---

## 📚 Protocol Compliance

This action plan follows SIMPLICITY_PROTOCOL_3 v4.5:
- ✅ Session-based work (30-90 min)
- ✅ Git commit after each session
- ✅ Explicit rollback procedures
- ✅ Sleep-at-night checks
- ✅ Pragmatic approach (80% > 100%)
- ✅ Tests required before commit
- ✅ Documentation in DECISIONS.md
- ✅ Clear risk assessment
- ✅ Know when to ask vs decide

---

## 🎬 Ready to Start?

**Next Steps**:
1. User reviews this plan
2. User confirms: "Start with Session 1" or "Skip to Session X"
3. COM4 executes session
4. Report results
5. User confirms: "Continue" or provides feedback
6. Repeat until complete

**Estimated Timeline**:
- Week 1: Sessions 1-4 (critical + high priority) = 2.5h
- Week 2: Sessions 5-7 (medium priority) = 2.75h
- Week 3: Session 8 (low priority, optional) = 1h
- **Total**: 6.25h + buffer = 8h realistic

---

**Status**: ⏸️ AWAITING USER CONFIRMATION TO START

**Questions for User**:
1. Should I work in main branch or create COM4 worktree?
2. Start with Session 1 (bare except: fix)?
3. Any sessions I should skip or reprioritize?
4. Want comprehensive test coverage report first?

---

*Generated by: COM4 Programmer*  
*Protocol: SIMPLICITY_PROTOCOL_3 v4.5*  
*Date: 2026-02-15*  
*Ready to protect your sleep 😴*
