# Code Study - Session 17: Standard GUI Docks (Part 3)

**Date**: 2026-01-22  
**Programmer**: #4  
**Session Focus**: Remaining standard docks (Calculator, Editor, JSON Search)

---

## 📊 Session Statistics

**Files Studied**: 3 files (focused analysis)  
**Lines Studied**: ~1,200 LOC (key components)  
**Total Available**: 1,831 LOC (calculator: 601, editor: 583, json_search: 647)  
**Time**: ~30 minutes  
**Coverage**: Architecture + critical methods

---

## 📁 Files Analyzed

### 1. **src/gui/calculator_dock.py** (601 LOC) ⭐ MEMORY SYSTEM

**Purpose**: Memory-based calculator with statistics for JSON result sets

**Architecture**:
- Extends **QWidget** (not BaseDock - simpler implementation)
- **5 memory slots**: A, B, C, D, E for storing results
- **Modular design**: Delegates to helper classes
- **QSettings persistence**: Memory survives sessions

**Helper Classes/Modules**:
- **CalculatorMemory** (src/calculator_memory.py): Memory slot management
- **StatisticsManager** (src/statistics_manager.py): Statistics calculation
- **CalculatorOperations** (src/calculator_operations.py): Operations (union, intersect, diff, etc.)
- **AccessibilityManager**: UI enhancements

**Key Features**:

#### Memory Slots (A-E)
- 5 slots for storing JSON data
- Each slot tracks:
  - **Source**: Where data came from (e.g., "Set Operations", "JSON Search")
  - **Count**: Number of items
  - **Size**: Total bytes
  - **Depth**: Max nesting level
  - **Unique keys**: Count of unique keys
  - **Duplicate keys**: Count of duplicate keys
  - **Types**: Distribution of data types

#### Statistics Display
- **QTableWidget**: 8 columns × 5 rows
- Columns: Slot | Source | Count | Size | Depth | Unique Keys | Dup Keys | Types
- Alternating row colors for readability
- Single-row selection

#### Slot Actions
- **Slot selector**: Combo box (A-E)
- `btn_store` - Store current result to selected slot
- `btn_recall` - Recall data from slot (emits data_recalled signal)
- `btn_clear` - Clear selected slot
- `btn_clear_all` - Clear all slots

#### Slot Operations
- **Compare**: Compare statistics between two slots (opens CompareDialog)
- **View Details**: View full statistics for selected slot (RecallDialog)
- **Operations** (combo box):
  - Union: A ∪ B
  - Intersection: A ∩ B
  - Difference: A - B
  - Symmetric Difference: A △ B
  - Merge: Combine arrays/objects
- **Operation Preview**: Preview before executing (OperationPreviewDialog)

#### Integration Signals
- `data_recalled = Signal(object)` - Emits JSON data when recalled
- `send_to_set_operations = Signal(dict, str)` - Sends data to Set Operations dock (v2.9.98)

**Key Methods**:

##### store_result(data, source) ⭐ MAIN STORAGE (line 370)
- Stores JSON data in current slot
- Calculates statistics via StatisticsManager
- Updates table display
- Saves to QSettings
- Returns True/False success

##### _refresh_table() (line 327)
- Updates all 5 rows with current slot data
- Formats size (bytes → KB/MB)
- Colors empty slots differently
- Updates UI state

##### _recall_slot() (line 400)
- Opens RecallDialog to show slot data
- User can:
  - View formatted JSON
  - Copy to clipboard
  - Send to Set Operations (emits signal)
- Emits data_recalled signal

##### _compare_slots() (line 493)
- Opens CompareDialog
- Calculates differences between two slots
- Shows side-by-side statistics
- Difference summary (total keys, unique keys, size, depth)

##### _execute_operation(operation) (line 518)
- Gets data from two slots (A & B, B & C, etc.)
- Calls CalculatorOperations method (union, intersect, etc.)
- Stores result in new slot
- Updates display

**Design Patterns**:
- **Facade**: CalculatorMemory, StatisticsManager, CalculatorOperations
- **Observer**: Qt signals for integration
- **Memento**: QSettings for persistence
- **Delegation**: All logic delegated to helper classes

**Integration Points**:
- ✅ **Set Operations Dock** (Session 16): Receives store_in_calculator_requested signal
- ✅ **Statistics**: Comprehensive statistics calculation
- ✅ **Dialogs**: RecallDialog, OperationPreviewDialog, CompareDialog

**Code Quality**:
- Excellent separation of concerns (UI vs Logic)
- Reusable helper classes
- Simple, focused dock implementation

---

### 2. **src/gui/editor_dock.py** (583 LOC) ⭐ TABBED EDITOR

**Purpose**: Integrated file editor with syntax highlighting

**Architecture**:
- Extends **BaseDock**
- **QTabWidget**: Multiple files in tabs
- **EditorTab** (Session 13): Extracted widget for each tab
- **SyntaxHighlighter** (Session 13): Syntax highlighting engine
- **QSettings**: Auto-save preference + recent files

**Key Features**:

#### File Operations
- `btn_new` - New file (Untitled-N tabs)
- `btn_open` - Open file dialog
- `btn_save` - Save current file (Ctrl+S)
- `btn_save_as` - Save with new name
- `btn_close_tab` - Close current tab
- **Recent files**: Track last 10 opened files

#### Tab Management
- **Closable tabs**: X button on each tab
- **Movable tabs**: Drag to reorder
- **Tab context menu**: Right-click for options
- **Tab titles**: Show filename (+ * if modified)
- **Tab switching**: Updates status bar

#### Edit Modes (v2.9.19 bugfix)
- **Normal mode**: Standard editing
- **Edit-only mode**: Sandbox for temp files
  - Used by "Open in Editor" from other docks
  - Prevents accidental save to system files
  - Shows [Edit Only] in tab title
- **Toggle**: Right-click tab → "Toggle Edit-Only Mode"

#### Auto-Save Feature
- `chk_auto_save` - Enable/disable auto-save
- **Timer-based**: Saves after N seconds of inactivity
- **Per-tab**: Each EditorTab has auto-save timer
- **QSettings**: Preference persists across sessions

#### Syntax Highlighting
- **File type detection**: By extension (.json, .html, .tsx, .py, etc.)
- **Color schemes**: Different colors per file type
- **Scope differentiation**: Keys, values, keywords, comments
- **Line numbers**: EditorTab includes line number area

#### Find/Replace (Basic)
- Standard QTextEdit find functionality
- Future: Enhanced search panel

**Key Methods**:

##### open_file_path(file_path, edit_only) ⭐ PUBLIC API (line 527)
- **Public method** called by other docks (e.g., ResultsOutputMixin)
- Opens file in new tab
- Sets edit_only mode if specified
- Adds to recent files
- **Critical for integration**: This is how "Open in Editor" works!

##### _create_tab_for_file(file_path, edit_only) (line 294)
- Creates EditorTab widget
- Reads file content
- Sets up syntax highlighting
- Configures edit-only mode if needed
- Connects signals (contentChanged, auto_save_triggered)

##### _save_file() (line 312)
- Saves current tab
- Handles edit-only mode (asks for location)
- Updates tab title
- Shows status message

##### _toggle_edit_only_for_tab(index) (line 213)
- Switches tab between normal/edit-only modes
- Updates tab title
- Used by context menu

##### _on_auto_saved(tab) (line 511)
- Called when tab auto-saves
- Updates status bar
- Visual feedback for user

##### has_unsaved_changes() (line 566)
- Checks all tabs for unsaved changes
- Used by main window before closing
- Prevents data loss

**Design Patterns**:
- **Strategy**: Different syntax highlighters per file type
- **Observer**: Tab signals (contentChanged, auto_save_triggered)
- **Composite**: EditorTab widgets composed in QTabWidget
- **Template Method**: BaseDock inheritance

**Integration Points**:
- ✅ **ResultsOutputMixin** (Session 15): open_file_path() called by _open_results_in_editor()
- ✅ **EditorTab** (Session 13): Core editing widget
- ✅ **SyntaxHighlighter** (Session 13): Syntax highlighting
- ✅ **Main Window**: has_unsaved_changes() prevents data loss

**v2.9.19 Bugfix Context** (from MEMORY_FIX_SUMMARY.md):
- **Problem**: "Open in Editor" from other docks opened in edit-only mode, but users couldn't see which mode they were in
- **Solution**: 
  1. Show [Edit Only] in tab title
  2. Add context menu to toggle mode
  3. Add keyboard shortcut (Ctrl+Shift+E)
- **Impact**: Users now have clear visual feedback + control

---

### 3. **src/gui/json_search_dock.py** (647 LOC) ⭐ INDEXING SEARCH

**Purpose**: Search keys and values in JSON and TypeScript files

**Architecture**:
- Extends **StandardToolDock** (all mixins!)
- **JsonSearchWorker** (QThread): Background indexing/search
- **ProjectIndexer**: Fast index-based search
- **QGridLayout**: Compact search form

**Key Features**:

#### Search Options
- `ed_search_key` - Search by key name
- `ed_search_value` - Search by value
- **Search mode** (combo box - Task #48 v2.9.23):
  - Keys Only
  - Values Only
  - Keys AND Values (both must match)
  - Keys OR Values (either matches)
- `chk_case_sensitive` - Case-sensitive search
- `chk_use_regex` - Regular expression search
- `spin_max_results` - Limit results (default: 1000)

#### File Selection
- **Directory input**: Search directory
- **Browse button**: Select directory
- **Recursive**: Search subdirectories
- **Extension filter**: .json, .ts, .tsx, .js, .jsx

#### Search Execution
- **Background worker**: JsonSearchWorker (prevents UI freeze)
- **Indexing**: ProjectIndexer.index_file() for each file
- **Progress updates**: Shows current file being indexed
- **Interrupt support**: Can cancel long searches
- **Result limiting**: Max results to prevent memory issues

#### Results Display
- **QTextEdit**: Shows search results
- **Format**: File path + matched key/value pairs
- **Line numbers**: Shows where matches occur
- **Export**: Save results to file

**Key Methods** (JsonSearchWorker):

##### run() ⭐ BACKGROUND SEARCH (line 37)
- Creates ProjectIndexer
- Indexes all files (emits progress per file)
- Calls resolve_query_with_mode() for search
- Parameters:
  - flat_index: Indexed data
  - search_key: Key pattern
  - search_value: Value pattern
  - search_mode: Keys/Values/AND/OR
  - case_sensitive: Boolean
  - use_regex: Boolean
- Limits results to max_results
- Emits success or error

**Key Functions** (src/json_search.py):

##### resolve_query_with_mode() ⭐ CORE SEARCH
- Implements search modes (Keys, Values, AND, OR)
- Uses match_with_options() for matching
- Returns list of matches with file/line info

##### ProjectIndexer.index_file()
- Parses JSON/TS files
- Builds flat index of all key-value pairs
- Optimized for fast search

**Design Patterns**:
- **Worker Thread**: JsonSearchWorker prevents UI blocking
- **Strategy**: Different search modes (Keys/Values/AND/OR)
- **Index**: ProjectIndexer for fast search
- **Observer**: Worker signals (progress, finished_ok, failed)

**Integration Points**:
- ✅ **Core**: ProjectIndexer, resolve_query_with_mode(), match_with_options()
- ✅ **AI Processor**: list_files_recursive() (shared utility)
- ✅ **Base Dock**: StandardToolDock mixins (results panel, buttons, etc.)
- ✅ **Accessibility**: AccessibilityManager

**Task #48 (v2.9.23)**: Added search modes
- Before: Only searched keys OR values (confusing)
- After: Explicit modes (Keys Only, Values Only, AND, OR)
- Impact: Users can now search with precision

---

## 🎯 Key Insights

### Calculator Dock: Perfect Delegation

**calculator_dock.py** demonstrates **excellent separation**:
- **UI layer**: Only handles widget creation + user interaction
- **Logic layer**: CalculatorMemory, StatisticsManager, CalculatorOperations
- **Persistence**: QSettings for memory slots
- **Integration**: Signals for loosely coupled communication

**Impact**: Logic can be reused elsewhere (e.g., CLI tool, API)

### Editor Dock: Integration Hub

**editor_dock.py** is the **integration point** for many features:
- **"Open in Editor"**: Called by 5+ docks (JSON Search, AI Processor, Set Ops, etc.)
- **Edit-only mode**: Critical for sandbox editing of temp files
- **Auto-save**: User experience enhancement
- **Recent files**: Productivity feature

**Pattern**: This dock is a **service provider** to other docks!

### JSON Search Dock: Index-Based Performance

**json_search_dock.py** shows **smart optimization**:
- **Indexing first**: Build flat index once, search multiple times
- **Background worker**: Long indexing doesn't freeze UI
- **Progress updates**: User knows what's happening
- **Result limiting**: Prevents memory exhaustion

**Trade-off**: Indexing takes time upfront, but searches are instant!

### Common Pattern: Worker Threads

**All complex docks use QThread workers**:
- **AI Processor**: AIProcessorWorker
- **JSON Search**: JsonSearchWorker
- **File Explorer**: FileExplorerWorker (from Session 15)
- **Pattern**: Consistent async execution strategy

**Benefit**: UI remains responsive during long operations!

---

## 📊 Updated Study Progress

**Session 17 Stats**:
- Files studied: 3 files
- LOC studied: ~1,200 LOC (focused reading)
- Total: calculator (601), editor (583), json_search (647)

**Total Progress**:
- **Files**: 76/196 (38.8%)
- **LOC**: ~26,781/38,754 (69.1%)
- **Remaining**: 120 files (61.2%), ~11,973 LOC (30.9%)

**Milestone**: Approaching 70% code coverage!

---

## 🚀 Next Steps

**Remaining Files** (~11,973 LOC):

**GUI Docks** (~7,000 LOC):
- advanced_extractor_dock.py (large)
- case_converter_dock.py, formula_dock.py, google_translate_dock.py
- history_dock.py, json_translate_dock.py, jsx_extractor_dock.py
- text_extractor_dock.py, text_to_json_dock.py, placeholder_replacer_dock.py
- tutorials_dock.py, file_list_dock.py
- + more specialty docks (~2,000 LOC)

**GUI Dialogs & Support** (~2,000 LOC):
- batch_dialog.py, case_validator_dialog.py, config_editor_dialog.py
- diff_viewer_dialog.py, error_report_dialog.py, history_dialog.py
- recall_dialog.py, operation_preview_dialog.py, presets_dialog.py
- dock_factory.py, initialization_manager.py, json_editor_tab.py
- panels.py, workers.py

**Remaining Modules** (~3,000 LOC):
- Plugins system (~20 files)
- Utilities not yet studied
- Test files (if needed)

**Options**:
- **A**: Continue GUI dock studies (large docks like advanced_extractor, text_extractor)
- **B**: Study dialogs & support files (understanding complete GUI architecture)
- **C**: Complete Phase 4 implementation (10% remaining)
- **D**: Work on fixes/improvements (per user focus)

**Recommendation**: 
- Option A or B to reach 80%+ coverage quickly
- Then Option D (fixes/improvements per user's stated focus)

**Status**: Session 17 complete ✅  
**Key Finding**: Worker thread pattern is consistent across all complex docks!
