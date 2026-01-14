# 🎯 Programmer #3 - Quick Reference Card

**Status**: ✅ Documentation Reading COMPLETE (100%)  
**Date**: 2026-01-14  
**Time Invested**: 6h 45m  
**Files Read**: 53 unique files (~35,000 lines)

---

## 📚 Where to Find Information

| Need to know... | Read this |
|----------------|-----------|
| **Architecture & Safety** | `DOCUMENTATION_READING_SESSION_1_PROGRAMMER_3.md` |
| **Features & v2.10 Roadmap** | `DOCUMENTATION_READING_SESSION_2_PROGRAMMER_3.md` |
| **Migration History & Workflows** | `DOCUMENTATION_READING_SESSION_3_PROGRAMMER_3.md` |
| **Everything (Executive Summary)** | `COMPLETE_DOCUMENTATION_READING_SUMMARY_PROGRAMMER_3.md` |

---

## ⚠️ CRITICAL: Don't Touch Areas

1. **src/rewriter/rewriter.py (lines 40-55)**: Obj type bug fix - PRODUCTION CRITICAL
2. **GUI Tests Without Timeouts**: ALWAYS use `@pytest.mark.timeout(5)` (10h loop risk!)
3. **Root Cleanup Before Commit**: MANDATORY (70+ binaries committed without it)

---

## 🔒 Before Every Commit (Protocol 3)

```bash
# Step 6.5: Security check
# (Manual review: input validation, path traversal, no secrets)

# Step 9.1: GUI tests with timeouts
export QT_QPA_PLATFORM=offscreen
pytest --collect-only  # Dry-run first
timeout 30s pytest tests/

# Step 11: Root cleanup
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
git status  # Verify clean

# Step 12.5: Document rollback plan in CHANGELOG

# Step 13: Quality gates
black . --line-length 120
isort . --profile black
pylint src/ --fail-under=9.0
```

---

## 🏗️ Architecture (Import Tree)

```
Root (app.py) → "What to do?" (Orchestrator)
├── Branches (gui/, core/) → "How to connect?" (Coordinators)
└── Leaves (widgets, utils) → "How to do X?" (Executors)

Rule: Leaves NEVER import other project files
```

---

## 🚀 Major Features Quick Index

| Feature | Version | LOC | Tests | Key Pattern |
|---------|---------|-----|-------|-------------|
| Formula Builder | v2.9.108 | 1,433 | 19/19 | Template Method |
| Plugin System | v2.9.109 | ~1,200 | 15/15 | Observer |
| Reusable Panels | v2.9.110 | 700+ | 18/18 | Composite |
| Regex Insert + Memory | v2.9.111 | 1,140 | 14/20 | Memento |

---

## 📋 v2.10 Roadmap (59h total)

**SHOULD HAVE** (26h):
- v2.10.1: JSON Translation (8h) - Google Translate API
- v2.10.2: Reverse Conversion (6h) - JSON → CSV/TSV
- v2.10.4: Schema Validation (12h) - JSON Schema Draft 7

**COULD HAVE** (33h):
- v2.10.3: Advanced Search (10h)
- v2.10.5: Diff & Merge (15h)
- v2.10.6: Batch Operations UI (8h)

---

## 🎓 Design Patterns Used (12+)

**GoF**: Strategy, Template Method, Observer, Singleton, Memento, Factory, Composite, Command, Facade  
**GRASP**: Information Expert, Controller, Low Coupling, High Cohesion

---

## 👥 Common User Workflows

1. **React i18n**: Extract → Translate → Replace
2. **JSON Cleanup**: Load → Dedupe → Normalize → Save
3. **Code Refactoring**: Select → Convert Case → Process

---

## 📊 Quality Metrics

- **LOC**: 70,000+
- **Test Coverage**: 97%
- **Pylint**: ≥9.0/10
- **Type Hints**: 91.3%
- **Languages**: 7 (EN, PT-BR, ES, FR, DE, ZH, JA)

---

## 🌍 Keyboard Shortcuts

- **ENTER**: Execute action in any input field
- **Ctrl+F**: Search in results panels
- **Ctrl+Z/Y**: Undo/Redo (10 levels)
- **Ctrl+S**: Save results
- **Ctrl+Q**: Quit

---

## ✅ Development Readiness

- [x] Architecture understood
- [x] Safety patterns memorized
- [x] Critical areas identified
- [x] Features mapped
- [x] Quality gates known
- [x] User workflows learned

**Status**: 🎯 READY FOR DEVELOPMENT!

---

**Last Updated**: 2026-01-14  
**Programmer**: #3  
**Protocol 3 Compliance**: ✅ 100%
