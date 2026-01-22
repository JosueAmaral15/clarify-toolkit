# Code Study - Session 1: Entry Points & Architecture

**Date**: 2026-01-22  
**Programmer**: #7  
**Branch**: COM7-read-docs  
**Phase**: 1 - Architecture Overview  
**Files Studied**: 4 files (~300 lines)

---

## Entry Points Discovered

### 1. `main.py` (171 lines) - TESTING ONLY
**Purpose**: Development validation script (NOT the application)
**Key Finding**: ⚠️ This is a RED HERRING - not the actual app!

**What it does**:
- Tests modular imports from `src/core/`, `src/utils/`, `src/rewriter/`
- Validates no circular dependencies
- Provides `python main.py test` for architecture validation

**Critical Comment** (lines 6-22):
> "THIS IS NOT THE MAIN APPLICATION! ... TO RUN THE ACTUAL APPLICATION, USE python clarify.py"

**Imports Tested**:
- `SearchOptions`, `preserve_case_like`, `replace_in_text` (core)
- `InsertMode`, `insert_at_line` (core)
- `Condition`, `filter_files_by_conditions`, `OPS` (core)
- `walk_files`, `read_text`, `write_text`, `safe_backup_file` (utils)
- `parse_exclusion_patterns`, `mask_exclusions`, `unmask_exclusions` (utils)
- `load_ts_object`, `dump_ts_object` (utils)
- `Obj`, `JSONNode`, `parse_json_preserving_duplicates_text` (rewriter)
- `dedupe`, `join_keys`, `eliminate_duplicates` (rewriter)

### 2. `src/__init__.py` (48 lines) - Package Metadata
**Purpose**: Package initialization with lazy imports

**Version**: 2.9.46  
**Author**: Josué Amaral  

**Key Pattern**: Lazy loading
```python
def main():
    from .app import main as app_main  # Avoids loading GUI at import
    return app_main()
```

**Why Lazy**: Prevents loading PySide6 dependencies until actually needed

### 3. `src/__main__.py` (15 lines) - Module Execution
**Purpose**: Standard Python module entry point

**Usage**: `python -m src`

**Implementation**: Direct import from app.py
```python
from .app import main
if __name__ == "__main__":
    sys.exit(main())
```

### 4. `src/app.py` (First 150 lines studied)
**Purpose**: **ACTUAL APPLICATION** - Main GUI + CLI entry point

**File Size**: ~2,700+ lines (only studied header so far)

**Key Metadata** (lines 1-54):
- Function: Character search, replacement, JSON organization
- Author: Josué Amaral
- Date: 2025/10/01
- Version referenced in multiple docs: v2.9.111+

**Core Features Listed**:
1. VS Code-like Search panel (case/word/regex, globs)
2. Replace (single/all) with preserve-case
3. Conditional filtering (filename/path/ext/size/mtime)
4. Insert text at line (5 modes)
5. JSON Translate (dictionary mapping)
6. JSON Rewriter (dedupe, join keys, eliminate duplicates)
7. CLI subcommands (search/replace/insert/translate/dedupe)

**Dependencies** (lines 69-150):
```python
# Logging
from .utils.logger import get_logger

# Error handling (v2.9.61)
from .utils.error_handler import install_crash_handler

# Core operations
from .core import SearchOptions, preserve_case_like, replace_in_text
from .core import InsertMode, insert_at_line
from .core import Condition, filter_files_by_conditions, OPS

# Utils
from .utils import walk_files, read_text, write_text, safe_backup_file
from .utils import parse_exclusion_patterns, mask_exclusions, unmask_exclusions
from .utils import load_ts_object, dump_ts_object

# JSON Rewriter (with BUG FIX comment)
from .rewriter import Obj, JSONNode, parse_json_preserving_duplicates_text
from .rewriter import dedupe, join_keys, eliminate_duplicates
... (many more)

# Case Converter
from .case_converter import JSObjectCaseConverter

# Theme Manager
from .theme_manager import ThemeManager

# i18n (Task #24 - v2.9.10)
from .i18n import get_translator, switch_language, tr, tooltip_tr

# JSON Search
from .json_search import ProjectIndexer, parse_composite_query

# AI Processor
from .ai_processor import OpenAIClient, GeminiClient, AVAILABLE_MODELS

# GUI Docks (hierarchical architecture)
from .gui import CaseConverterDock, PlaceholderReplacerDock, JsonSearchDock
from .gui import AIProcessorDock, JsonTranslateDock, JsonRewriterDock
from .gui import FileExplorerDock, EditorDock, DockFactory, MenuBuilder

# Progress Management (v2.9.114)
from .gui.progress import ProgressBarWidget, ProgressManager

# Search/Replace/Insert Panels (v2.9.114)
from .gui.panels import ...  (line 150 - incomplete)
```

---

## Architecture Insights

### Module Organization
```
src/
├── app.py (MAIN APPLICATION ~2700 lines)
├── __init__.py (package metadata, lazy loading)
├── __main__.py (module execution entry)
│
├── core/ (search, replace, insert, filters)
├── utils/ (file ops, text processing, TS/JS handling)
├── rewriter/ (JSON processing, deduplication)
├── i18n/ (internationalization - 7 languages)
├── ai_processor/ (OpenAI, Gemini integration)
├── gui/ (modular docks, panels, widgets)
│   ├── progress/ (v2.9.114 - progress management)
│   └── panels/ (v2.9.114 - search/replace/insert)
│
├── case_converter.py (camelCase/snake_case conversions)
├── theme_manager.py (dark/light themes)
├── json_search.py (project-wide JSON search)
├── placeholder_replacer.py (batch replacements)
└── ...
```

### Import Pattern: Modular + Organized
**Observation**: All imports go through organized modules (core, utils, rewriter, gui)
**Benefit**: Eliminates code duplication, clear separation of concerns

### Entry Point Flow
```
User Runs:
  python clarify.py
     ↓
  Loads src/__init__.py
     ↓
  Calls main() → lazy imports src.app.main()
     ↓
  src/app.py main() function executes
     ↓
  Initializes GUI/CLI based on arguments
```

**Alternative Entry**:
```
python -m src
     ↓
  Loads src/__main__.py
     ↓
  Directly imports src.app.main()
     ↓
  Same execution path
```

---

## Critical Comments Found

### Bug Fix Reference (line 94, app.py)
```python
# JSON Rewriter: types, parser, operations, serializer (includes BUG FIX)
from .rewriter import ...
```
**Note**: Documentation mentioned "CRITICAL BUG FIX for Obj type" - need to study rewriter module

### Lazy Loading Rationale (line 42, __init__.py)
```python
# Lazy import of main function to avoid loading GUI dependencies
```
**Why**: PySide6 is heavy (~50MB), shouldn't load if just importing package

---

## Next Steps for Session 2

### Continue app.py Study
- [ ] Read lines 151-500 (rest of imports + initialization)
- [ ] Understand MainWindow class structure
- [ ] Study menu system (MenuBuilder)
- [ ] Analyze dock management (DockFactory)

### Study Base Classes
- [ ] `gui/base_dock.py` (BaseDock architecture)
- [ ] `gui/dialogs/` structure
- [ ] Worker thread patterns

---

## Questions Raised

1. **What was the "CRITICAL BUG FIX" in rewriter/Obj**?
   - Need to check git history or bug reports
   
2. **How does DockFactory work**?
   - Mentioned in imports, seems to be factory pattern for docks
   
3. **What is ProgressManager** (v2.9.114)?
   - Recently added (Phase 1.1 comment), progress tracking system

4. **How many actual docks exist**?
   - Counted 13 in imports: CaseConverter, PlaceholderReplacer, JsonSearch, TextExtractor, AIProcessor, JsonTranslate, JsonRewriter, History, FileList, FileExplorer, Tutorials, Editor, TextToJson, JSXExtractor

---

**Status**: Phase 1 in progress (15% of app.py read)
**Files Remaining**: 192 Python files, ~57,865 lines
**Time Spent**: ~15 minutes
**Estimated Remaining**: 4-7 hours

