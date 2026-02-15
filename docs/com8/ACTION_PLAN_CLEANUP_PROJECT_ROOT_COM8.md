# ACTION PLAN: Clean Up Project Root and Organize Test Files

**Programmer**: COM8  
**Date**: 2026-02-09  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: Project root folder is cluttered with test files, scripts, and temporary outputs

---

## PROBLEM STATEMENT

Project root contains 40+ files that should be organized:
- Test scripts (*.py)
- Test outputs (*.odt, *.html, *.txt)
- Documentation (*.md)
- Investigation scripts

This violates project organization and makes root folder messy.

---

## CURRENT STATE (Files in Root)

### Test Scripts (~25 files)
```
test_*.py
check_*.py
investigate_*.py
debug_*.py
verify_*.py
trace_*.py
show_*.py
diagnostic_*.py
```

### Test Outputs (~10 files)
```
*.odt (CAIT_*.odt, test_*.odt)
*.html (test_*.html)
*.txt (COMPARISON_*.txt, FORMATTED_*.txt, TRANSLATED_*.txt)
*.sh (test_*.sh)
```

### Documentation (~5 files)
```
ACTION_PLAN_*.md
INVESTIGATION_*.md
TEST_FIX_INSTRUCTIONS_*.md
```

### Analysis Scripts (~5 files)
```
COMPARE_*.py
COMPLETE_*.py
COMPREHENSIVE_*.py
DETAILED_*.py
VISUAL_*.py
READ_*.py
TEST_WITH_*.py
```

---

## DESIRED STATE (Project Structure)

```
clarify-COM8/
├── main.py                    # Keep (entry point)
├── README.md                  # Keep (project docs)
├── CHANGELOG.md               # Keep (project docs)
├── CONTRIBUTING.md            # Keep (project docs)
├── SECURITY.md                # Keep (project docs)
├── pyproject.toml             # Keep (config)
├── poetry.lock                # Keep (config)
├── src/                       # Source code
├── tests/                     # Unit tests (pytest)
│   └── com8/                  # COM8 specific tests
│       ├── test_text_extractor_COM8.py
│       ├── test_html_format_mapper_COM8.py
│       ├── test_odt_translation_COM8.py
│       └── fixtures/          # Test data
│           ├── sample_input.odt
│           └── expected_output.html
├── docs/
│   └── com8/                  # COM8 documentation
│       ├── ACTION_PLAN_*.md
│       ├── INVESTIGATION_*.md
│       ├── SESSION_*.md
│       └── TESTING_*.md
├── scripts/                   # Utility scripts
│   └── com8/                  # COM8 investigation scripts
│       ├── investigate_*.py
│       ├── debug_*.py
│       ├── verify_*.py
│       └── compare_*.py
└── .test_outputs/             # Temporary test outputs (gitignored)
    └── com8/
        ├── *.odt
        ├── *.html
        └── *.txt
```

---

## SOLUTION PLAN

### Phase 1: Create Directory Structure
```bash
mkdir -p tests/com8/fixtures
mkdir -p scripts/com8
mkdir -p .test_outputs/com8
```

### Phase 2: Move Files

**2.1 Move Test Scripts → tests/com8/**
```bash
mv test_*.py tests/com8/
mv check_*.py tests/com8/
mv verify_*.py tests/com8/
```

**2.2 Move Investigation Scripts → scripts/com8/**
```bash
mv investigate_*.py scripts/com8/
mv debug_*.py scripts/com8/
mv trace_*.py scripts/com8/
mv show_*.py scripts/com8/
mv diagnostic_*.py scripts/com8/
mv COMPARE_*.py scripts/com8/
mv COMPLETE_*.py scripts/com8/
mv COMPREHENSIVE_*.py scripts/com8/
mv DETAILED_*.py scripts/com8/
mv VISUAL_*.py scripts/com8/
mv READ_*.py scripts/com8/
mv TEST_WITH_*.py scripts/com8/
```

**2.3 Move Documentation → docs/com8/** (already exists)
```bash
mv ACTION_PLAN_*.md docs/com8/
mv INVESTIGATION_*.md docs/com8/
mv TEST_FIX_INSTRUCTIONS_*.md docs/com8/
```

**2.4 Move Test Outputs → .test_outputs/com8/**
```bash
mv CAIT_*.odt .test_outputs/com8/
mv test_*.odt .test_outputs/com8/
mv test_*.html .test_outputs/com8/
mv test_*.txt .test_outputs/com8/
mv test_*.sh .test_outputs/com8/
mv *_COM8.txt .test_outputs/com8/
mv COMPARISON_*.txt .test_outputs/com8/
mv TRANSLATED_*.txt .test_outputs/com8/
mv FORMATTED_*.txt .test_outputs/com8/
```

### Phase 3: Update .gitignore
Add:
```
# Test outputs
.test_outputs/
*.odt
*.html
test_*.txt
*_COM8.txt
*_DEBUG_*.txt
```

### Phase 4: Create README in Each Directory

**tests/com8/README.md**
```markdown
# COM8 Test Files

Unit tests and integration tests for Google Translate ODT formatting features.

## Running Tests
pytest tests/com8/

## Test Files
- test_text_extractor_COM8.py - TextExtractor class tests
- test_html_format_mapper_COM8.py - HTML format system tests
```

**scripts/com8/README.md**
```markdown
# COM8 Investigation Scripts

Diagnostic and debugging scripts used during development.

These are NOT unit tests - they are one-off investigation tools.
```

**.test_outputs/com8/README.md**
```markdown
# Test Outputs

Temporary files generated during testing.
These files are gitignored and can be deleted safely.
```

---

## TESTING PLAN

### Test 1: Verify Application Still Works
```bash
cd clarify-COM8
./clarify.sh
# Open Google Translate tool
# Load ODT file
# Verify preview works
```

### Test 2: Verify Tests Still Run
```bash
cd tests/com8
pytest test_html_format_mapper_COM8.py -v
```

### Test 3: Verify Scripts Still Work
```bash
cd scripts/com8
PYTHONPATH=../../src python3 investigate_*.py
```

---

## FILES TO MODIFY

None - just move files and create directories

---

## EXECUTION CHECKLIST

- [ ] Create directory structure (Phase 1)
- [ ] Move test scripts (Phase 2.1)
- [ ] Move investigation scripts (Phase 2.2)
- [ ] Move documentation (Phase 2.3)
- [ ] Move test outputs (Phase 2.4)
- [ ] Update .gitignore (Phase 3)
- [ ] Create README files (Phase 4)
- [ ] Test application works
- [ ] Commit changes

---

## ESTIMATED FILES TO MOVE

- ~25 test scripts → tests/com8/
- ~10 investigation scripts → scripts/com8/
- ~3 documentation files → docs/com8/
- ~15 test outputs → .test_outputs/com8/

**Total: ~53 files cleaned from root**

---

## COMMIT MESSAGE

```
refactor: Organize project root - move COM8 test files to proper directories

- Created tests/com8/ for unit tests
- Created scripts/com8/ for investigation scripts  
- Created .test_outputs/com8/ for temporary test outputs
- Moved ~53 files from root to organized locations
- Updated .gitignore to ignore test outputs
- Added README files to new directories

Project root now contains only essential files:
- Entry points (main.py, launchers)
- Documentation (README, CHANGELOG, CONTRIBUTING, SECURITY)
- Configuration (pyproject.toml, poetry.lock, configs)

Session: COM8
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## STATUS: Ready to execute - awaiting user approval

**Question**: Should I proceed with the cleanup?
