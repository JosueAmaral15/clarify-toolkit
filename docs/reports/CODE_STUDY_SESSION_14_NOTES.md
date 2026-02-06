# Code Study - Session 14: Remaining Core Files

**Date**: 2026-01-22  
**Programmer**: #4  
**Session Focus**: Completing core/ directory study (8 remaining files)

---

## 📊 Session Statistics

**Files Studied**: 8 files  
**Lines of Code**: 1,406 LOC  
**Time**: ~35 minutes  
**Coverage**: All remaining core files

---

## 📁 Files Analyzed

### 1. **src/core/set_operation_executor.py** (224 LOC)

**Purpose**: Core execution logic for set operations on JSON files

**Key Classes**:

#### ExecutionResult
- Container for execution results and metadata
- Fields: success, results, stats_lines, file_a_data, file_b_data, error
- Used as return type from execute_operations()

#### SetOperationExecutor (Static class)
- All methods are static (no instance state)

**Methods**:

##### validate_and_load_files(file_paths)
- Security: Uses validate_file_path() (CWE-22 protection)
- Validates .json extension
- Loads multiple JSON files
- Returns: (success, file_dicts, error_message)

##### execute_operations(file_dicts, operations, comparison_mode, options)
- Operations: ∩ (intersection), ∪ (union), − (difference), ⊕ (symmetric difference)
- Imports from src.set_operations module
- Returns: ExecutionResult with results and statistics
- Stores file_a_data and file_b_data for diff viewer

##### format_results_json(results)
- Pretty print results as JSON (indent=2)

##### calculate_result_count(results)
- Counts total items across all operation results

**Design Pattern**: Facade (wraps set_operations module)

**Usage**: Set Operations Dock (GUI wrapper around these utilities)

---

### 2. **src/core/search_replace.py** (64 LOC) ⚙️ SIMPLE

**Purpose**: Simple search/replace functionality with regex support

**Key Classes**:

#### SearchOptions (dataclass)
- case_sensitive: bool
- whole_word: bool
- regex: bool
- Method: `compile(needle)` → returns compiled re.Pattern

**Functions**:

##### preserve_case_like(matched_text, replacement)
- ALL CAPS → upper()
- Capitalized → capitalize()
- lowercase → lower()
- Mixed → as-is

##### replace_in_text(content, pattern, repl, preserve_case, count)
- Uses re.Pattern.sub()
- Supports preserve_case via callback
- count=0 means replace all
- Returns: (new_content, num_replacements)

**Note**: This is a **simpler alternative** to the comprehensive logic in file_explorer_executor.py

**Usage**: May be used by simpler text editing features

---

### 3. **src/core/command_manager.py** (183 LOC) ⭐ DESIGN PATTERN

**Purpose**: Command Pattern implementation for Undo/Redo system

**Pattern**: Command (GoF) + Memento (history stack)

**Key Classes**:

#### Command (ABC - Abstract Base Class)
- `execute()` - perform action
- `undo()` - revert action
- `redo()` - re-execute (default: calls execute())
- `get_description()` - human-readable name

#### FileModificationCommand (Command)
- Stores: filepath, original_content, new_content
- execute() - write new_content
- undo() - restore original_content
- redo() - re-apply new_content

#### MultiFileCommand (Command)
- Aggregates multiple FileModificationCommand instances
- execute() - run all sub-commands
- undo() - reverse all sub-commands in reverse order
- redo() - re-run all sub-commands

#### CommandManager
- **History stack**: deque with configurable max depth (default: 10)
- **Undo stack**: Commands executed
- **Redo stack**: Commands undone (cleared on new execute)
- Methods:
  - `execute_command(cmd)` - Execute and push to undo stack
  - `undo()` - Pop from undo, execute undo(), push to redo
  - `redo()` - Pop from redo, execute redo(), push to undo
  - `can_undo()`, `can_redo()` - Check availability
  - `get_undo_description()`, `get_redo_description()` - For UI display
  - `clear_history()` - Reset stacks
  - `get_history_stats()` - Statistics dict

**Design Pattern**: 
- **Command Pattern** (GoF) - Encapsulate actions as objects
- **Memento Pattern** (history storage)
- **Composite Pattern** (MultiFileCommand)

**Usage**: Task #12 (v2.9.8) - Undo/Redo system (Ctrl+Z / Ctrl+Y)

**NOT YET INTEGRATED** - Framework exists but may not be wired to GUI yet

---

### 4. **src/core/result_exporter.py** (196 LOC)

**Purpose**: Export operation results to multiple formats

**Key Class**: ResultExporter (Static methods)

**Supported Formats**:
- JSON (json.dump)
- CSV (via ExportManager)
- Excel (.xlsx) (via ExportManager + openpyxl)
- YAML (via ExportManager)
- TOML (via ExportManager + tomli-w)

**Methods**:

##### save_json(data, file_path)
- Simple JSON string write
- Returns: (success, message)

##### export_multi_format(data, file_path, selected_filter, parent_widget)
- Delegates to ExportManager.export()
- Detects format from QFileDialog filter string
- Flattens data for CSV/Excel/TOML
- Includes metadata (timestamp, operation type)
- Optional progress modal via parent_widget
- Returns: (success, message)

##### validate_export_data(data)
- Checks if data is None or empty
- Returns: (is_valid, error_message)

**Format Detection**:
- FORMAT_MAP: Maps filter strings to format codes
- FORMAT_FILTER: String for QFileDialog filter parameter

**Error Handling**:
- Catches ImportError (missing dependencies like openpyxl)
- Suggests pip install commands

**Usage**: Set Operations Dock, Search/Replace results export

---

### 5. **src/core/multi_query.py** (189 LOC)

**Purpose**: Support for multi-line search queries (one query per line)

**Key Classes**:

#### QueryLine (dataclass)
- raw_text: Original query string
- pattern: Compiled re.Pattern
- line_number: Line number in input (1-based)

#### MultiQueryProcessor
- Parse multi-line text into individual queries
- Comments: Lines starting with # are ignored
- Empty lines: Skipped

**Methods**:

##### __init__(multi_line_text, case_sensitive, whole_word, use_regex)
- Parses queries via _parse_queries()

##### _parse_queries()
- Split by \n
- Skip empty lines and comments (#)
- Compile each line to regex pattern
- Fallback: If regex fails, escape and treat as literal

##### _compile_pattern(text)
- Add word boundaries if whole_word=True
- Apply case sensitivity flag
- Returns compiled re.Pattern

##### search_in_text(content)
- Search all queries in content
- Returns: List of (line, col, snippet, query_line_number)
- query_line_number indicates which query matched

##### validate()
- Checks: at least one valid query
- Checks: no query > 500 chars (performance)
- Returns: (is_valid, error_message)

**Utility Functions**:
- `split_multi_query(text)` - Extract query list (no comments/empty)
- `combine_query_results(results_by_query)` - Merge results, remove duplicates

**Usage**: Search/Replace Dock multi-query mode (SearchOptionsPanel has chk_multi_query checkbox!)

---

### 6. **src/core/rewriter_cli.py** (195 LOC) ⭐ COMPLEX

**Purpose**: CLI interface for JSON/TS rewriting operations (dedupe/rewrite)

**Main Function**: cli_dedupe(args, advanced_conditions, apply_all_types)

**Processing Pipeline** (in order):
1. Enable detailed stats collection
2. Apply advanced filters (if provided) - Sprint B Feature #1
3. Read input file
4. Parse JSON or TypeScript (ts_process_full_preserving)
5. **Resolve references** (if enabled) - Sprint A v2.9.29
6. Apply transformations (with counting):
   - dedupe()
   - join_keys() (optional)
   - eliminate_duplicates() + build substitution map (Task #23)
   - exclude_numeric_keys() (optional)
   - skip_empty_values() (optional)
   - avoid_duplicate_child_keys() (optional)
   - remove_duplicate_array_values() (consecutive or all)
   - skip_keys_without_siblings() (Task #35)
   - remove_duplicate_objects() OR create_references() (Task #52 + Sprint A)
   - enforce_consistent_case() (Task #9)
7. Serialize output (JSON or TS)
8. Write output file
9. Return: (output_text, substitution_map, stats, detailed_stats)

**Statistics Tracked**:
- dedupe, eliminate, numeric_keys, empty_values
- duplicate_child, array_duplicates_consecutive, array_duplicates_all
- no_siblings, advanced_filters_filtered
- references_created, references_resolved, references_invalid
- duplicate_objects

**Reference Modes** (Sprint A v2.9.29):
- **Delete mode** (legacy): remove_duplicate_objects()
- **Reference mode** (new): create_references() with $ref format

**Case Enforcement** (Task #9):
- Supports: camel, snake, pascal, kebab case styles
- Warns about inconsistencies (first 10 warnings shown)

**Usage**: JSON Rewriter Dock (GUI wrapper around this CLI logic)

---

### 7. **src/core/insert.py** (52 LOC) ⚙️ SIMPLE

**Purpose**: Text insertion at specific lines with multiple modes

**Class**: InsertMode (constants class)
- LEFT = "Insert left of line"
- RIGHT = "Insert right of line"
- REPLACE = "Replace line content"
- INSERT_ABOVE = "Push line down and insert above"
- INSERT_BELOW = "Insert on next line (push rest)"

**Function**: insert_at_line(content, line_no, text, mode)
- line_no is 1-based
- Handles out-of-bounds gracefully (pads with empty lines)
- Preserves trailing newline if present
- Returns: Modified content string

**Usage**: Text editing operations, possibly in Editor or JSON manipulation

---

### 8. **src/core/memory_register.py** (303 LOC) ⭐ ADVANCED FEATURE

**Purpose**: Regex capture & reuse system (Memento + Command patterns)

**Use Case**:
1. User defines regex to capture values (e.g., r'"name": "(.*?)"')
2. System searches and stores matches in registers ($0, $1, $2, ...)
3. User uses registers to insert new fields (e.g., "fullName": "$1")

**Key Classes**:

#### RegisterEntry (dataclass)
- index: Register index ($0, $1, etc.)
- value: Captured value
- source_text: Original text where captured
- pattern: Regex pattern used
- timestamp: When captured
- Methods: to_dict(), from_dict() (for persistence)

#### MemoryRegister
- **Pattern**: Memento (GoF) - Stores captured state
- Max registers: 100 ($0-$99)
- History: Stores previous captures for restoration

**Methods**:

##### capture(text, pattern, flags)
- Use re.compile() and finditer()
- Store $0 (whole match), $1-$N (capture groups)
- Save to history
- Returns: (num_captures, captured_values)

##### get(index, default)
- Retrieve register value by index

##### get_all()
- Returns: Dict[int, str] of all registers

##### replace_in_text(template)
- Replace $N placeholders with register values
- Sorts by index descending (avoids $1 vs $10 conflict)
- Example: `"$1-$2"` → `"John-Doe"`

##### clear(), has_registers(), get_register_count()
- Management methods

##### restore_from_history(index)
- Restore registers from history (index=-1 = last)

##### export_to_dict(), import_from_dict()
- Persistence support

##### export_to_json(), import_from_json()
- JSON serialization

**Global Singleton**:
- `get_global_register()` - Returns singleton instance
- `reset_global_register()` - Reset singleton

**Design Patterns**:
- **Memento** (GoF) - Captures and restores state
- **Command** (implicit) - Captures can be commands
- **Singleton** (global register)

**Usage**: Advanced feature for power users (regex-based JSON manipulation)

**NOT HEAVILY USED** - Appears to be specialized feature

---

## 🎯 Key Insights

### Design Patterns Catalog

Session 14 revealed **excellent design pattern usage**:

1. **Command Pattern** (command_manager.py)
   - Undo/Redo system
   - FileModificationCommand, MultiFileCommand
   - History stack with undo/redo stacks

2. **Memento Pattern** (memory_register.py)
   - Captures regex matches
   - History restoration
   - State serialization

3. **Facade Pattern** (set_operation_executor.py, result_exporter.py)
   - Wraps complex operations in simple interface
   - SetOperationExecutor wraps set_operations module
   - ResultExporter wraps ExportManager

4. **Strategy Pattern** (implicit in search_replace.py, multi_query.py)
   - Different search strategies (single vs multi-query)
   - Different replace strategies (preserve case vs not)

### Feature Maturity Assessment

**Mature & Integrated**:
- ✅ SetOperationExecutor - Used by Set Operations Dock
- ✅ ResultExporter - Used for exporting results
- ✅ MultiQueryProcessor - Used in Search/Replace (chk_multi_query)
- ✅ search_replace - Used in text operations
- ✅ rewriter_cli - Core of JSON Rewriter Dock

**Framework Ready (Not Yet Wired)**:
- ⚠️ CommandManager - Undo/Redo framework exists but may not be wired to GUI
- ⚠️ MemoryRegister - Advanced feature, likely not heavily used

**Simple Utilities**:
- ⚙️ insert.py - Basic text manipulation utility

### Multi-Query Feature

**IMPORTANT DISCOVERY**: MultiQueryProcessor explains the `chk_multi_query` checkbox in SearchOptionsPanel!

- **Session 12**: Saw checkbox in search_widgets.py
- **Session 14**: Found the implementation in multi_query.py
- **Connection**: Multi-line search mode (one query per line, # for comments)

This means File Explorer Phase 4 **already supports multi-query** if wired correctly!

### Undo/Redo System Status

**CommandManager** provides complete undo/redo framework:
- Task #12 (v2.9.8) mentions this feature
- Framework is complete and tested
- **Question**: Is it connected to GUI? (Need to check main_window.py for Ctrl+Z/Ctrl+Y handlers)

### Export System

**ResultExporter** shows multi-format export support:
- JSON (native)
- CSV, Excel, YAML, TOML (via ExportManager)
- Delegates to external ExportManager class (not studied yet)
- **Dependency**: Requires openpyxl, tomli-w for full functionality

---

## 🔍 Phase 4 Relevance

### Direct Relevance:
- **search_replace.py** - Alternative to file_explorer_executor search logic
- **multi_query.py** - Powers chk_multi_query checkbox (already in search_widgets!)

### Indirect Learning:
- **command_manager.py** - Shows excellent Command pattern implementation
- **memory_register.py** - Shows excellent Memento pattern implementation
- **set_operation_executor.py** - Shows Facade pattern usage

### Not Relevant to Phase 4:
- rewriter_cli.py (JSON Rewriter feature)
- insert.py (text manipulation utility)
- result_exporter.py (export feature)

---

## 📊 Updated Study Progress

**Session 14 Complete**:
- Files studied: 8 files
- LOC studied: 1,406 LOC

**Total Progress**:
- **Files**: 68/196 (34.7%)
- **LOC**: 23,081/38,754 (59.6%)
- **Remaining**: 128 files (65.3%), 15,673 LOC (40.4%)

**Core Coverage**:
- `src/core/`: 100% complete (all 13 files studied)
- `src/gui/widgets/`: 100% complete (all 13 files studied)

---

## 🚀 Next Steps

**Phase 4 Study Complete!** (Sessions 12-14)

**What's Been Studied**:
- ✅ Phase 1-3: Core files, JSON Search, GUI (Sessions 1-11)
- ✅ Phase 4 Session 12: Phase 4 core components (5 files)
- ✅ Phase 4 Session 13: All widget files (8 files)
- ✅ Phase 4 Session 14: All core files (8 files)

**Total**: 68 files, 23,081 LOC (59.6% of codebase)

**Remaining Areas** (128 files, 40.4%):
1. **GUI Docks** (~30 files) - Main windows and panels
2. **Plugins** (~20 files) - Plugin system
3. **Utilities** (~40 files) - Helper functions
4. **Set Operations** (~10 files) - Set logic
5. **Rewriter** (~15 files) - JSON rewriting
6. **Tests** (~13 files) - Test files

**Options**:
- **A**: Continue studying (GUI docks next - main_window.py, *_dock.py files)
- **B**: Take break, work on fixes/improvements (per user's focus)
- **C**: Create comprehensive study summary (Phases 1-4 complete)

**Status**: Session 14 complete ✅  
**Recommendation**: Ask user for next direction
