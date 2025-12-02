# Rollback Plan: JSX Parameter Extractor Feature

## 📋 Document Information

- **Feature**: JSX Parameter Extractor
- **Version**: 2.9.0
- **Date**: December 2, 2025
- **Author**: Josué Amaral
- **Status**: Production Ready
- **Rollback Difficulty**: Low (isolated feature, minimal dependencies)

---

## 🎯 Rollback Overview

This document provides procedures to safely rollback the JSX Parameter Extractor feature if issues arise in production. The rollback process is straightforward due to the modular architecture and isolated codebase.

### When to Rollback

Consider rollback if:
- ❌ Critical bugs affecting core application stability
- ❌ Security vulnerabilities discovered in extractor code
- ❌ Performance issues impacting overall application
- ❌ Data corruption or loss incidents
- ❌ Incompatibility with production environment

### Rollback Impact

✅ **Low Risk Rollback**:
- Feature is isolated in separate modules
- No changes to database schema
- No breaking changes to existing features
- Only affects "Tools → Text To JSON Converter" menu item

---

## 📁 Files Affected

### Files Added (10)

#### Source Code
1. `src/extractors/__init__.py` (~15 lines)
2. `src/extractors/extractor.py` (~500 lines)
3. `src/extractors/jsx_parser.py` (~570 lines)
4. `src/extractors/generic_parser.py` (~90 lines)
5. `src/utils/normalization.py` (~145 lines)
6. `src/gui/jsx_extractor_dock.py` (~520 lines)

#### Configuration
7. `.pre-commit-config.yaml` (~60 lines)
8. `.pylintrc` (~80 lines)
9. `ci_quality_check.sh` (~80 lines, executable)

#### Documentation
10. `docs/jsx-extractor-guide.md` (~900 lines)
11. `docs/CI_CD_SETUP.md` (~250 lines)
12. `docs/ROLLBACK_JSX_EXTRACTOR.md` (this file)

#### Tests
13. `test_component.tsx` (~30 lines)
14. `test_jsx_extractor.py` (~300 lines)

### Files Modified (3)

1. **`src/app.py`** (3 additions):
   - Import: `from .gui import JSXExtractorDock`
   - Method: `_show_text_to_json()` - added selection dialog
   - Methods: `_show_jsx_extractor()`, `_show_text_format_converter()`, `_open_jsx_extractor()`
   
2. **`src/gui/__init__.py`** (1 addition):
   - Export: `JSXExtractorDock` added to imports and `__all__`

3. **`pyproject.toml`** (2 modifications):
   - Version updated: `0.1.0` → `2.9.0`
   - Added: `[tool.black]`, `[tool.isort]`, `[tool.pylint.*]` configurations
   - Added: `[project.optional-dependencies]` with dev tools

4. **`README.md`** (1 section added):
   - Section: "JSX Parameter Extractor (NEW in v2.9.0)"

5. **`CHANGELOG.md`** (1 entry added):
   - Entry: "## [2.9.0] - 2025-12-02"

---

## 🔄 Rollback Procedures

### Option 1: Git Revert (Recommended)

**Prerequisites:**
- Git repository with clean working tree
- Commit hash of JSX Extractor feature known

**Steps:**

1. **Identify commit hash:**
   ```bash
   git log --oneline --grep="jsx-extractor"
   # Output: abc1234 feat(jsx-extractor): add JSX parameter extraction
   ```

2. **Create backup branch:**
   ```bash
   git checkout -b backup-before-rollback-jsx-extractor
   git checkout main
   ```

3. **Revert the commit:**
   ```bash
   git revert abc1234
   ```

4. **Verify revert:**
   ```bash
   git status
   git diff HEAD~1
   ```

5. **Test application:**
   ```bash
   python -m src
   # Verify app starts without errors
   # Check "Tools → Text To JSON Converter" menu
   ```

6. **Commit revert:**
   ```bash
   git commit -m "revert(jsx-extractor): rollback JSX Parameter Extractor feature due to [REASON]"
   ```

7. **Push to remote:**
   ```bash
   git push origin main
   ```

**Rollback Time:** ~5 minutes

---

### Option 2: Manual File Removal (Alternative)

Use this if git revert is not available or causes conflicts.

**Steps:**

1. **Create backup:**
   ```bash
   mkdir -p archive/jsx_extractor_backup_$(date +%Y%m%d_%H%M%S)
   cp -r src/extractors archive/jsx_extractor_backup_*/
   cp src/gui/jsx_extractor_dock.py archive/jsx_extractor_backup_*/
   cp src/utils/normalization.py archive/jsx_extractor_backup_*/
   ```

2. **Remove added files:**
   ```bash
   rm -rf src/extractors/
   rm src/gui/jsx_extractor_dock.py
   rm src/utils/normalization.py
   rm .pre-commit-config.yaml
   rm .pylintrc
   rm ci_quality_check.sh
   rm test_component.tsx
   rm test_jsx_extractor.py
   rm docs/jsx-extractor-guide.md
   rm docs/CI_CD_SETUP.md
   rm docs/ROLLBACK_JSX_EXTRACTOR.md
   ```

3. **Restore modified files:**

   **src/app.py:**
   ```bash
   git checkout HEAD~1 -- src/app.py
   # Or manually remove:
   # - Import JSXExtractorDock
   # - _show_jsx_extractor() method
   # - _show_text_format_converter() method
   # - _open_jsx_extractor() method
   # - Restore original _show_text_to_json() logic
   ```

   **src/gui/__init__.py:**
   ```bash
   git checkout HEAD~1 -- src/gui/__init__.py
   # Or manually remove JSXExtractorDock from imports and __all__
   ```

   **pyproject.toml:**
   ```bash
   git checkout HEAD~1 -- pyproject.toml
   # Or manually:
   # - Revert version to 0.1.0
   # - Remove [tool.black], [tool.isort], [tool.pylint.*] sections
   # - Remove [project.optional-dependencies] dev tools
   ```

   **README.md:**
   ```bash
   # Manually remove section "JSX Parameter Extractor (NEW in v2.9.0)"
   ```

   **CHANGELOG.md:**
   ```bash
   # Manually remove entry "## [2.9.0] - 2025-12-02"
   ```

4. **Test application:**
   ```bash
   python -m src
   # Verify app starts
   # Check menu works
   ```

5. **Commit changes:**
   ```bash
   git add -A
   git commit -m "rollback(jsx-extractor): manual removal of JSX Parameter Extractor"
   git push origin main
   ```

**Rollback Time:** ~15 minutes

---

### Option 3: Feature Flag Disable (Temporary)

For temporary disablement without code removal.

**Steps:**

1. **Modify src/app.py:**
   ```python
   # At top of file
   JSX_EXTRACTOR_ENABLED = False  # Feature flag
   
   # In _show_text_to_json()
   def _show_text_to_json(self) -> None:
       if not JSX_EXTRACTOR_ENABLED:
           # Old behavior - directly open text converter
           self._show_text_format_converter()
           return
       
       # New behavior - selection dialog
       dialog = QDialog(self)
       # ... rest of code
   ```

2. **Test:**
   ```bash
   python -m src
   # "Tools → Text To JSON Converter" now opens Text Converter directly
   ```

3. **Commit:**
   ```bash
   git commit -m "feat(jsx-extractor): disable via feature flag"
   git push origin main
   ```

**Rollback Time:** ~2 minutes  
**Note:** Files remain in codebase (technical debt)

---

## ✅ Post-Rollback Verification

### 1. Application Startup
```bash
python -m src
```
**Expected:** Application starts without errors

### 2. Menu Navigation
- Navigate to "Tools → Text To JSON Converter"
**Expected:** Opens Text Format Converter (old behavior)

### 3. Import Test
```bash
python -c "from src.app import main; main()"
```
**Expected:** No import errors

### 4. Compile Test
```bash
python -m py_compile src/app.py src/gui/*.py
```
**Expected:** No syntax errors

### 5. Existing Features
Test other tools:
- Search & Replace
- JSON Rewriter
- JSON Translator
- Case Converter
**Expected:** All working normally

### 6. No Orphaned Imports
```bash
grep -r "extractors" src/ --exclude-dir=extractors
grep -r "JSXExtractorDock" src/ --exclude=jsx_extractor_dock.py
grep -r "normalization" src/ --exclude-dir=utils
```
**Expected:** No matches (or only in comments/docs)

---

## 🔍 Rollback Testing Checklist

- [ ] Application starts without errors
- [ ] "Tools → Text To JSON Converter" menu works
- [ ] Text Format Converter opens and functions
- [ ] No import errors in console
- [ ] No syntax errors in compilation
- [ ] Existing features unaffected
- [ ] No orphaned imports remain
- [ ] Git history clean (no uncommitted changes)
- [ ] Documentation updated (if rollback is permanent)
- [ ] Team notified of rollback

---

## 📊 Impact Assessment

### User Impact
- ✅ **Zero downtime**: Rollback can be done without restart
- ✅ **No data loss**: Feature doesn't persist data
- ✅ **No user migrations**: No user settings to revert
- ⚠️ **Feature unavailable**: Users lose JSX extraction capability

### Developer Impact
- ✅ **Clean codebase**: Modular architecture allows clean removal
- ✅ **No dependencies**: Other features don't depend on JSX Extractor
- ✅ **Easy revert**: Can re-apply feature later if issues fixed

### Technical Debt
- **If using Option 1 (git revert)**: None
- **If using Option 2 (manual removal)**: None
- **If using Option 3 (feature flag)**: Dead code remains (cleanup needed later)

---

## 🛡️ Prevention Measures

### To Avoid Future Rollbacks

1. **Extended Testing Period**
   - Beta testing with select users
   - Longer QA cycle before production

2. **Phased Rollout**
   - Feature flag deployment
   - Gradual user base expansion
   - Monitoring metrics

3. **Enhanced Monitoring**
   - Error tracking (Sentry, Rollbar)
   - Performance monitoring
   - User feedback collection

4. **Better Documentation**
   - More comprehensive test cases
   - Edge case documentation
   - Known issues tracking

---

## 📞 Escalation Contacts

### Decision Authority
- **Minor issues**: Development lead (proceed with rollback)
- **Major incidents**: Product owner + dev lead (discussion required)
- **Security issues**: Immediate rollback (notify team)

### Communication Channels
- **Team Notification**: Slack #clarify-dev channel
- **User Notification**: Release notes, email newsletter
- **Incident Report**: Post-mortem document in `docs/incidents/`

---

## 📝 Rollback Log Template

Use this template to document actual rollback execution:

```markdown
### Rollback Execution Log

**Date/Time:** YYYY-MM-DD HH:MM:SS
**Performed By:** [Name]
**Reason:** [Brief description]
**Method Used:** [Option 1/2/3]
**Duration:** [X minutes]
**Issues Encountered:** [None / List issues]
**Verification Status:** [Pass / Fail]
**User Impact:** [None / Minimal / Significant]
**Follow-up Actions:** [List actions]

**Commit Hash (if applicable):** abc1234
**Branch:** main
**Tag:** v2.9.0-rollback (optional)

**Testing Results:**
- [ ] Application startup: Pass/Fail
- [ ] Menu navigation: Pass/Fail
- [ ] Existing features: Pass/Fail
- [ ] No errors: Pass/Fail

**Notes:** [Additional observations]
```

---

## 🔄 Re-Deployment Plan

If rollback was due to fixable issues:

### Steps to Re-Deploy

1. **Fix identified issues** in development branch
2. **Run full test suite** (including new tests for bug)
3. **Update documentation** with lessons learned
4. **Code review** with focus on issue area
5. **Deploy to staging** environment
6. **Extended testing** period (2x original)
7. **Gradual rollout** with monitoring
8. **Document changes** in CHANGELOG.md

### Success Criteria

- All original tests passing
- New tests for bug scenario passing
- No regressions in existing features
- Pylint score maintained (>= 9.0/10)
- Performance benchmarks met
- Security scan clean

---

## 📚 References

- **Feature Documentation**: `docs/jsx-extractor-guide.md`
- **CI/CD Setup**: `docs/CI_CD_SETUP.md`
- **Changelog Entry**: `CHANGELOG.md` (v2.9.0)
- **Test Suite**: `test_jsx_extractor.py`
- **Git History**: `git log --grep="jsx-extractor"`

---

## 📄 Appendix: File Diffs

### src/app.py Changes to Revert

**Lines to Remove:**
```python
# Around line 20 (imports)
from .gui import (..., JSXExtractorDock)

# Around line 4340 (method modification)
def _show_text_to_json(self) -> None:
    """Show Text to JSON Converter with selection dialog."""
    # ... entire selection dialog code ...
    
# Around line 4380 (new methods)
def _show_jsx_extractor(self) -> None:
    # ... entire method ...

def _show_text_format_converter(self) -> None:
    # ... entire method ...
    
def _open_jsx_extractor(self) -> None:
    # ... entire method ...
```

**Lines to Restore:**
```python
def _show_text_to_json(self) -> None:
    """Show Text to JSON Converter."""
    if not hasattr(self, "text_to_json"):
        self.text_to_json = TextToJsonDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.text_to_json)
        self.text_to_json.hide()
    self.text_to_json.setVisible(not self.text_to_json.isVisible())
    if self.text_to_json.isVisible():
        self.text_to_json.raise_()
```

### src/gui/__init__.py Changes to Revert

**Lines to Remove:**
```python
from .jsx_extractor_dock import JSXExtractorDock

__all__ = [..., 'JSXExtractorDock']
```

---

## ✅ Sign-Off

**Prepared By:** Josué Amaral  
**Reviewed By:** [To be filled]  
**Approved By:** [To be filled]  
**Date:** December 2, 2025

**Rollback Plan Status:** ✅ Approved for Production

---

**Version:** 1.0  
**Last Updated:** December 2, 2025  
**Next Review:** After first production deployment
