# Session 17 - Phase 3: Source Code Reading

**Programmer**: #1  
**Date**: 2026-01-21  
**Time Start**: 14:32 (-03 UTC)  
**Protocol**: SIMPLICITY_PROTOCOL_3 - Phase 3 (Source Code Reading)  
**Goal**: Read 100% of Python source code for deep implementation understanding

---

## 📊 Scope

**Target Files**: 196 Python files in `src/` (58,165 lines)
**Test Files**: 83 Python files in `tests/` (25,454 lines) - Will analyze if time permits
**Total**: 279 Python files, 83,619 lines of code

**Strategy**: 
- Follow Import Tree Analogy (ROOT → BRANCHES → LEAVES)
- Start with ROOT (app.py), then BRANCHES (managers, gui), then LEAVES (utils)
- Focus on understanding patterns, architecture, implementation details
- Strategic sampling for large files, comprehensive for critical files

---

## 📖 Phase 3: Python Source Code Analysis

### Reading Plan (Import Tree Order)

**1. ROOT Layer** (1 file, ~2,000 lines):
- [ ] src/app.py (MainWindow - orchestrator)

**2. BRANCHES Layer - Core** (~20 files, ~8,000 lines):
- [ ] src/core/ modules (12 files)
- [ ] src/managers/ (initialization, command, tab, etc.)

**3. BRANCHES Layer - GUI** (~50 files, ~25,000 lines):
- [ ] src/gui/base_dock.py (mixins, base classes)
- [ ] src/gui/docks/ (20+ dock implementations)
- [ ] src/gui/panels/ (search, replace, insert panels)
- [ ] src/gui/dialogs/ (various dialogs)

**4. LEAVES Layer - Utils** (~125 files, ~23,000 lines):
- [ ] src/utils/ (strategic sampling - no internal dependencies)

---


## 🎯 Reading Strategy

Given the scope (196 files, 58,165 lines), adopting **Strategic Deep-Dive** approach:

**Focus Areas**:
1. ✅ Validate architecture patterns documented in FASE_3
2. ✅ Identify critical implementation details
3. ✅ Find edge cases, gotchas, workarounds
4. ✅ Understand threading, performance, memory patterns
5. ✅ Sample representative files from each category

**Time Target**: 2-3 hours for strategic deep understanding

---

## 📖 BATCH 1: ROOT Layer - app.py (1,967 lines)

### File 1: src/app.py ✅ (Reading in progress)

**Structure Analysis**:
- **Total lines**: 1,967 lines
- **Type**: GUI entry point (MainWindow class expected)
- **Functions at module level**: 5 functions
  - load_prefs() (line 209)
  - save_prefs() (line 215)
  - apply_theme() (line 224)
  - read_translation_dict() (line 236)
  - main() (line 1935)

**Imports Analysis** (lines 56-100+):
- **Standard library**: argparse, base64, configparser, fnmatch, json, os, re, sys, dataclasses, datetime, typing
- **Logging**: .utils.logger.get_logger
- **Error handling**: .utils.error_handler.install_crash_handler (v2.9.61)
- **Core**: SearchOptions, preserve_case_like, replace_in_text, InsertMode, insert_at_line, Condition, filter_files_by_conditions, OPS
- **Utils**: walk_files, read_text, write_text, safe_backup_file, parse_exclusion_patterns, mask/unmask_exclusions, load/dump_ts_object
- **Rewriter**: Obj, JSONNode, parse_json_preserving_duplicates_text, freeze, find_object_block, ts_block_to_json_text, sanitize_keys_and_values, ts_process_full_preserving, dedupe, join_keys, eliminate_duplicates, merge_obj_values, avoid_duplicate_child_keys, exclude_numeric_keys, skip_empty_values, normalize_escaping, array_to_object_conversion

**Documentation** (lines 4-54):
- **Author**: Josué Amaral
- **Date**: 2025/10/01
- **Name**: TextWorkbench (internal name) vs Clarify (project name)
- **Purpose**: GUI + CLI for search/replace/insert + JSON translate/dedupe

**7 Core Features**:
1. VS Code-like Search panel (case/whole-word/regex, include/exclude globs)
2. Replace (single/all) with preserve-case
3. Conditional filtering (filename/path/extension/size/mtime operators)
4. Insert text at specific line (5 placement modes)
5. JSON Translate (map texts using JSON/TS dictionary)
6. JSON Rewriter (dedupe identical pairs, join keys, eliminate duplicates, TS/JS support)
7. CLI subcommands (headless processing)

**CLI Examples** (lines 35-41):
```bash
python clarify.py search ./src --query "foo" --include "*.ts;*.tsx" --cond "ext:equals:ts"
python clarify.py replace ./src --query "foo" --replacement "bar" --all
python clarify.py insert ./src --line 1 --text "HEADER" --mode insert_above --cond "content:contains:React"
python clarify.py translate ./web --dictionary dict.ts
python clarify.py dedupe en.ts --from-ts --join-keys --eliminate-duplicates --no-line-break -o en2.ts --indent 2
```


**Detailed Reading Notes** (lines 1-900):

### __init__ Method (lines 387-431):
- **Window Flags Fix** (v2.9.117): Explicit Linux/X11/Wayland compatibility
  - Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
  - Stored in `_desired_window_flags` to prevent QDockWidget interference
- **Initialization**: Delegated to InitializationManager (line 406) - validates Phase 3.7 pattern
- **Global Event Filter**: Shift+Scroll horizontal scrolling (v2.9.115, line 409)
- **Layout Restoration**: layout_manager.restore_last_layout() (v2.9.84, line 412)
- **UI Update Workaround**: updateGeometry() + processEvents() (lines 415-416) - Qt rendering fix
- **Accessibility**: _apply_accessibility() (v2.9.35, line 419)
- **Tab State Restoration**: _restore_tab_state() (v2.9.40, line 422)
- **Tab Initialization**: _initialize_all_tabs() (line 428) - prevents lazy rendering bug
- **Auto-Update Check**: _auto_check_for_updates() (v2.9.45, line 431)
- **Font Setup**: Monospaced font for editor widgets (lines 434-439)

### Icon Loading (lines 441-492):
- **3-Tier Fallback**:
  1. SVG icon from assets/icons/icon.svg
  2. PNG icon from assets/icons/icon.png  
  3. Embedded Base64 string (legacy fallback)
- **Error Handling**: Try-except at each level, empty icon on total failure
- **Base64 Icon**: 2048-char Base64 PNG embedded (line 469)

### Dock Creation Methods (lines 494-548):
**Pattern**: All use DockFactory lazy loading
- _open_trans(), _open_rewrite(), _open_text_extractor()
- _open_placeholder_replacer(), _open_ai_processor(), _open_json_search()
- _open_case_converter(), _open_jsx_extractor(), _open_text_to_json()
- _open_file_explorer(), _open_history(), _open_tutorials()
- _open_editor(), _open_google_translate()

### Tab Management (lines 562-700):
**Two patterns identified**:

**Pattern 1: Built-in panels** (Search/Replace, Insert):
- Check if tab exists at expected index
- If missing, recreate using internal classes (SearchReplacePanel, InsertPanel)
- Insert at specific index, set current, processEvents()

**Pattern 2: External docks** (all other tools):
- Delegate to TabManager.show_*() methods
- TabManager handles lazy creation and tab management
- Examples: translate, rewriter, text_extractor, ai_processor, json_search, etc.

**Special Cases**:
- Set Operations (line 656): Bi-directional connection with Calculator
- Calculator (line 669): Connects to Set Operations (send/receive data)
- Text-to-JSON (line 628): Shows converter selection dialog first
- Formula Builder (line 688): v2.9.108 feature

### About Dialog (lines 719-729):
- **Version**: Hardcoded as "2.9.64" (should be dynamic from __version__)
- **Content**: HTML formatted, GitHub link, copyright
- **Issue**: Version hardcoded - potential maintenance issue

### View Logs (lines 731-778):
- **Platform-specific opening**: xdg-open (Linux), open (macOS), os.startfile (Windows)
- **Error handling**: Warnings for missing file or failed opening
- **User guidance**: Shows path if auto-open fails

### Plugin System (lines 780-796):
- **Plugin Manager**: _show_plugin_manager() delegates to PluginManagerDialog (v2.9.109)
- **Event Emission**: _emit_plugin_event() broadcasts to all active plugins
- **Pattern**: Event-driven plugin architecture

### Update Checker (lines 798-900):
- **Auto-check** (line 800): On startup if enabled, respects 24h cache
- **Manual check** (line 820): Forces fresh check, shows ManualCheckDialog
- **Background check** (line 862): Silent operation, only shows if update found
- **Version skipping**: Users can opt out of specific versions
- **3-second delay**: QTimer.singleShot(3000) to avoid blocking startup (line 818)

**Key Patterns Observed So Far**:
1. ✅ **DockFactory Pattern**: All dock creation delegated to factory
2. ✅ **TabManager Pattern**: Tab lifecycle managed centrally
3. ✅ **InitializationManager Pattern**: Centralized startup logic
4. ✅ **Lazy Loading**: Docks created on-demand, not at startup
5. ✅ **Qt Workarounds**: processEvents(), updateGeometry() for rendering issues
6. ✅ **Platform Compatibility**: Explicit window flags for Linux/X11/Wayland
7. ✅ **Event-Driven Architecture**: Plugin system uses events, bi-directional signal connections
8. ✅ **Fallback Strategies**: 3-tier icon loading, error-tolerant update checks


**Detailed Reading Notes** (lines 900-1967 - COMPLETE):

### Tab Management System (lines 916-1175):
**_add_tool_tab** (line 916):
- Checks if tool already open (`tool_tabs` dict tracking)
- Adds new tab via `tabs.addTab(widget, title)`
- Tracks in `self.tool_tabs[tool_name] = (widget, tab_index)`
- **Critical**: Restores window flags after adding tab (v2.9.117) - QDockWidget can interfere with MainWindow flags on Linux
- Saves tab state to QSettings

**_close_tab** (line 953):
- Checks for unsaved changes (Editor only)
- Shows save/discard/cancel dialog if needed
- Removes tab, restores window flags
- Updates tracking dict indices (shifts down for tabs after closed index)
- Saves state

**_initialize_all_tabs** (line 1012):
- **Critical Qt Workaround**: Forces rendering of all tabs
- Problem: Qt lazy-renders non-visible tab widgets → invisible widgets bug
- Solution: Temporarily activate each tab → processEvents() → force updateGeometry()
- Restores original tab after initialization
- Detailed logging for debugging

**_restore_window_flags** (line 1052):
- **Linux Fix** (v2.9.117): QDockWidget as tab interferes with window flags
- Compares current vs desired flags
- If modified: setWindowFlags() → show() (setWindowFlags hides window)

**_save_tab_state / _restore_tab_state** (lines 1103, 1122):
- **v2.9.112 Enhancement**: Don't save/restore fixed tabs if closed
- Tracks "fixed_tabs_open" for Search/Replace and Insert
- Dynamically reopens tool tabs using `_show_{tool_name}()` methods
- Validates saved index (handles closed tabs gracefully)

### Menu & Language System (lines 1176-1296):
**_build_menu** (line 1176):
- Delegates to MenuBuilder (Phase 3.4)

**_apply_theme_action** (line 1180):
- Radio button behavior (QActionGroup)
- Applies theme, persists to config file

**_switch_language** (line 1230):
- **Runtime language switching** (v2.9.10)
- Calls `switch_language(lang)` from i18n module
- Saves preference
- Debug logging

**_retranslate_ui** (line 1274):
- Retranslates window title, all menu action texts
- **Rebuilds entire menu bar** to update menu titles (line 1295-1296)

### Dock Navigation System (lines 1594-1915):
**keyPressEvent** (line 1594):
- **Ctrl+Tab**: Next dock (menu order)
- **Ctrl+Shift+Tab**: Previous dock (menu order)
- **Ctrl+PageDown**: Next dock (creation order)
- **Ctrl+PageUp**: Previous dock (creation order)
- **Ctrl+1-9**: Jump to specific dock by index
- **Ctrl+0**: Reset font size
- **F11**: Toggle fullscreen

**eventFilter** (line 1650):
- **Shift+Scroll**: Horizontal scrolling (v2.9.115)
- Finds scrollable parent widget with horizontalScrollBar
- Scrolls 3 steps at a time
- **Consumes event** to prevent vertical scroll

**wheelEvent** (line 1688):
- **Ctrl+Scroll**: Font size scaling (v2.9.35)
- Uses AccessibilityManager
- Shows status message with current font size

**Navigation Methods** (lines 1741-1915):
- `_get_all_docks()`: Finds all `dock_*` attributes
- `_get_visible_docks()`: Filters to visible only
- `_get_dock_by_menu_order()`: Returns docks in Tools menu order
- **Menu order** (line 1756-1768): json_search, rewriter, set_operations, ai_processor, case_converter, text_extractor, text_to_json, placeholder_replacer, translate
- `_navigate_next_dock()`: Menu order navigation with wraparound
- `_navigate_prev_dock()`: Reverse menu order
- `_navigate_next_dock_dynamic()`: Creation order navigation
- `_navigate_prev_dock_dynamic()`: Reverse creation order
- `_jump_to_dock()`: By index, opens if not visible
- `_focus_dock()`: Raises dock, activates window, sets focus, shows status

### Shortcuts System (lines 1298-1523):
**_show_shortcuts** (line 1298):
- Shows customization dialog
- Connects to `_on_shortcuts_changed` signal

**_apply_shortcuts_to_menu** (line 1479):
- Maps actions to shortcut names
- Uses ShortcutManager for lookup and application
- Updates tooltips with shortcut hints
- 14+ shortcuts mapped (File, Edit, Tools, View menus)

**Keyboard Shortcuts Help** (line 1392):
- Read-only view with search functionality
- Monospaced font display
- Filter-as-you-type
- Opens customization dialog from help

### Undo/Redo System (lines 1525-1580):
**_undo / _redo** (lines 1527, 1539):
- Delegates to CommandManager
- Shows information dialogs with operation description
- Warnings if nothing to undo/redo

**_update_undo_redo_state** (line 1565):
- Updates button enabled state
- Updates tooltips with descriptions ("Undo: <operation name>")

**_clear_undo_history** (line 1551):
- Confirmation dialog
- Clears command manager history

### Layout & Preferences (lines 1306-1390):
**_register_docks_with_layout_manager** (line 1306):
- Registers all docks by name
- Filters to existing docks only
- Forces update+repaint on each dock

**_save_current_layout** (line 1339):
- Input dialog for custom name
- Saves via LayoutManager
- Confirmation dialog

**_apply_accessibility** (line 1727):
- Focus indicators
- Screen reader support
- Saved font size

### Window Lifecycle (lines 1917-1928):
**closeEvent** (line 1917):
- Delegates to WindowSettings.handle_close_event()

**_build_ui** (line 1921):
- Delegates to UIBuilder.build_all(self)

**_restore_prefs** (line 1926):
- Delegates to WindowSettings.restore_prefs(self)

### main() Function (lines 1935-1963):
- **CLI Detection**: If argv[0] in subcommands → run as CLI
- **GUI Launch**:
  - Qt attribute: AA_UseDesktopOpenGL (line 1952)
  - Create QApplication
  - Create MainWindow (calls __init__ with all initialization)
  - Resize to 1200x400
  - show()
  - repaint() + processEvents() - force immediate rendering
  - app.exec() - enter event loop

---

## ✅ app.py COMPLETE (1,967 lines read)

### **Key Architecture Patterns Confirmed**:

1. **Delegation Pattern** ✅:
   - InitializationManager (startup)
   - MenuBuilder (menus)
   - WindowSettings (window lifecycle)
   - UIBuilder (UI construction)
   - TabManager (tab lifecycle for external docks)
   - DockFactory (dock creation)
   - ShortcutManager (keyboard shortcuts)
   - AccessibilityManager (a11y features)
   - LayoutManager (dock layouts)
   - CommandManager (undo/redo)

2. **Lazy Loading** ✅:
   - All docks created on-demand via `_open_*()` or `_show_*()` methods
   - DockFactory handles creation logic
   - No docks created in __init__

3. **Qt Workarounds** ✅:
   - processEvents() calls (lines 416, 572, 586, 1037, 1049, 1961)
   - updateGeometry() calls (line 415, 1042)
   - repaint() calls (line 1337, 1960)
   - Window flags restoration (Linux maximize button fix)
   - Tab initialization to prevent lazy rendering

4. **Platform-Specific Code** ✅:
   - Window flags for Linux/X11/Wayland (line 396-402)
   - Log viewer: xdg-open, open, os.startfile (lines 756-762)
   - Desktop OpenGL attribute (line 1952)

5. **i18n Integration** ✅:
   - tr() and tooltip_tr() throughout
   - Runtime language switching (line 1230-1244)
   - _retranslate_ui() rebuilds menus (line 1274)

6. **Plugin System** ✅:
   - Plugin manager dialog (line 782)
   - Event emission to plugins (line 787)

7. **State Persistence** ✅:
   - Tab state (open tools, current index, fixed tabs)
   - Window geometry and state
   - Custom shortcuts
   - Recent files
   - Theme preference
   - Language preference
   - Font size
   - Layout presets

8. **Error Handling** ✅:
   - Try-except in icon loading with 3-tier fallback
   - Try-except in log viewer
   - Silent failure in update checker

9. **Accessibility** ✅:
   - Font scaling (Ctrl+Scroll, Ctrl+0)
   - Focus indicators
   - Screen reader support
   - Keyboard navigation (Ctrl+Tab, Ctrl+1-9, F11)
   - Horizontal scrolling (Shift+Scroll)

10. **Update System** ✅:
    - Auto-check on startup (3-second delay)
    - Manual check with fresh fetch
    - Version skipping
    - Silent failures

**Critical Implementation Details**:
- Version hardcoded in About dialog (line 724) - should use __version__
- tab_search and search_panel dual references (line 436) - matches documentation
- Fixed tabs (Search/Replace, Insert) at indices 0-1, can be closed since v2.9.112
- Tool tabs tracked in dict with (widget, index) tuples
- Window flags must be restored after tab operations on Linux
- All tabs must be force-initialized to prevent invisible widgets
- Shift+Scroll handled at global level via event filter

**Design Quality**: ⭐⭐⭐⭐⭐
- Excellent separation of concerns
- Consistent delegation patterns
- Comprehensive error handling
- Platform-aware code
- Accessibility-first design
- Well-documented with comments explaining WHY

---


## 📖 BATCH 2: Core Modules - file_explorer_executor.py ✅ (683 lines read)

### File 2: src/core/file_explorer_executor.py (683 lines) ✅

**Purpose**: Unified File Explorer Executor - Merges List + Search + Replace logic (v2.9.116)

**Key Classes**:

1. **SearchMatch** (dataclass, line 34):
   - Fields: line, col, snippet, context_before (deprecated), context_after (deprecated)
   - Memory optimizations (v2.9.120):
     - snippet truncated to MAX_SNIPPET_LENGTH (200 chars, was unlimited)
     - context_before/after removed (rarely used, 3x memory overhead)
     - Fields kept for compatibility but not populated

2. **SearchResult** (dataclass, line 50):
   - Fields: file_info (FileInfo), matches (List[SearchMatch]), match_count (int)

3. **UnifiedFileExplorerExecutor** (QObject, line 59):
   - **Signals**: progress, progress_detailed, done, error
   - **State**: _cancel, _paused flags
   - **Methods**: cancel(), pause(), resume()

**Key Methods**:

**execute_browse** (line 101):
- Lists files with advanced filters
- Steps:
  1. Get base file list via FileListExecutor
  2. Apply type filter (files/dirs/any)
  3. Apply include/exclude glob filters
  4. Check exclude globs first (higher priority)
  5. **Path component check** (line 146): Correctly handles .venv, node_modules by checking if pattern exists as path component (fixes fnmatch issue)
  6. Create SearchResult objects with empty matches
  7. Calculate statistics

**execute_search** (line 181):
- Unified search operation (filename + content)
- **Critical Optimization** (line 217-278): Early vs Late conditions
  - **Early conditions** (size, ext, filename, path, mtime): Applied BEFORE content search to avoid unnecessary file I/O
  - **Late conditions** (content): Applied AFTER reading files
  - Separates conditions by type (line 223-232)
  - Logs filtered counts (line 263-271)
- **Memory Optimization** (v2.9.120):
  - MAX_TOTAL_MATCHES = 50,000 global limit (line 31)
  - Checks limit at line 296-301, emits warning and stops search
  - Logs memory optimization stats (line 341-352)
- Steps:
  1. List files (calls execute_browse)
  2. Apply early conditions (non-content)
  3. Apply filename pattern filter
  4. Content search with progress tracking
  5. Apply late conditions (content-based)
  6. Calculate statistics

**execute_replace** (line 356):
- Replace operation with progress tracking
- Opens files, calls _replace_in_text, writes back
- Tracks replaced_count, files_modified, errors
- Error handling per file (continues on error)

**_search_in_text** (line 412):
- Core search logic with regex support
- **Security**: ReDoS prevention (line 432-444)
  - Regex compilation with try-except
  - MAX_MATCHES_PER_FILE = 10,000 limit (line 447)
  - Allow cancellation in loop (line 450)
  - Catch regex matching errors (catastrophic backtracking) (line 478-482)
- **Memory Optimization** (v2.9.120, line 462-475):
  - Truncate snippets to 200 chars
  - Remove context_before/after
  - Comments explain 3x memory reduction
- Error handling: continues with next line on regex error

**_replace_in_text** (line 493):
- Replace with case sensitivity, whole word, regex support
- **Bug Fix** (line 524-533): Backslash escaping
  - In non-regex mode: escape backslashes (\S becomes \\\\S)
  - In regex mode: keep backslashes for backreferences (\1, \2)
  - Prevents "bad escape" errors
- **Security**: Regex DoS prevention (line 516-522)
- Supports preserve_case and replace_all flags

**_replace_preserve_case** (line 556):
- Iterates through matches
- Applies case pattern from original to replacement
- Respects count limit (first-only vs all)

**_apply_case_pattern** (staticmethod, line 586):
- **All uppercase**: UPPER() replacement
- **All lowercase**: lower() replacement
- **Title case**: Upper first, lower rest
- **Mixed**: return as-is

**_apply_conditions** (line 597):
- Filters results by advanced conditions
- Supports AND/OR logic operators
- Calls _check_condition for each condition
- Returns filtered list

**_check_condition** (line 639):
- Checks single condition against SearchResult
- **Fields supported**: filename, path, ext, size, mtime, content
- **Operators**: =, !=, contains, >, <, >=, <=
- Content field: checks match_count > 0 (already searched)
- Type-aware comparisons (string vs numeric)

**Critical Constants**:
- MAX_SNIPPET_LENGTH = 200 (line 30)
- MAX_TOTAL_MATCHES = 50,000 (line 31)
- MAX_MATCHES_PER_FILE = 10,000 (line 447)

**Security Considerations** ✅:
1. **ReDoS Prevention** (OWASP A03):
   - Regex compilation with try-except
   - MAX_MATCHES_PER_FILE limit
   - Cancellation support
   - Catch catastrophic backtracking errors
2. **Memory Protection**:
   - Global match limits
   - Snippet truncation
   - Context removal
3. **Error Handling**:
   - Try-except around regex operations
   - Continue on error (don't fail entire operation)
   - Detailed error logging

**Design Patterns** ✅:
- **Strategy Pattern**: Different search/replace strategies via options dict
- **Command Pattern**: execute_browse, execute_search, execute_replace as commands
- **Observer Pattern**: Qt Signals for progress/error reporting
- **Early Optimization**: Condition filtering before expensive I/O

**Code Quality**: ⭐⭐⭐⭐⭐
- Excellent security consciousness (ReDoS prevention)
- Memory-aware design (limits, truncation)
- Comprehensive error handling
- Clear separation of concerns
- Well-documented with comments explaining WHY

---


## 📖 BATCH 3: Core Modules - memory_register.py ✅ (303 lines read)

### File 3: src/core/memory_register.py (303 lines) ✅

**Purpose**: Memory Register System for Regex Capture & Reuse (v2.9.111)

**Design Patterns**:
- **Memento (GoF)**: Stores captured state (RegisterEntry)
- **Command (GoF)**: Encapsulated operations
- **Singleton**: Global register instance via get_global_register()

**Use Case**:
1. User defines regex to capture values: `r'"name": "(.*?)"'`
2. System finds matches and stores in registers ($0, $1, $2, ...)
3. User uses registers to insert new fields: `"fullName": "$1"`

**Key Classes**:

**RegisterEntry** (dataclass, line 36):
- Fields: index, value, source_text, pattern, timestamp
- Methods: to_dict(), from_dict() (serialization)
- Truncates source_text to 100 chars when exporting (memory optimization)

**MemoryRegister** (line 75):
- **Attributes**:
  - max_registers: Maximum number (default 100)
  - registers: Dict[int, RegisterEntry] - active registers
  - history: List[List[RegisterEntry]] - capture history
  - last_pattern: Last used regex pattern

**Key Methods**:

**capture()** (line 102):
- Captures values from text using regex with capture groups
- **Process**:
  1. Compile regex pattern (try-except for validation)
  2. Find all matches via finditer()
  3. **Clear current registers** (line 133)
  4. Process matches:
     - $0 = whole match (line 140-148)
     - $1, $2, ... = capture groups (line 151-164)
     - Limit to max_registers
     - Handle None groups (empty string)
  5. Store in history
  6. Return (num_captures, captured_values)
- **Example**: `text = '{"name": "John"}'`, `pattern = r'"name": "(.*?)"'` → $0 = `"name": "John"`, $1 = `"John"`

**get()** (line 174):
- Retrieves value from register by index
- Returns default if not found

**get_all()** (line 188):
- Returns all register values as Dict[int, str]

**replace_in_text()** (line 192):
- Replaces $N placeholders in template with register values
- **Critical**: Sorts indices descending (line 210) - avoids replacing $1 before $10
- Example: `template = '"fullName": "$1"'` → `'"fullName": "John"'`

**History Management**:
- **restore_from_history()** (line 233): Restores registers from history (index -1 = last)
- **get_history_count()** (line 229): Returns history entry count

**Persistence**:
- **export_to_dict()** (line 255): Exports to dictionary
- **import_from_dict()** (line 263): Imports from dictionary
- **export_to_json()** (line 272): Exports to JSON string
- **import_from_json()** (line 276): Imports from JSON string

**Global Singleton**:
- **get_global_register()** (line 292): Returns/creates global instance
- **reset_global_register()** (line 300): Resets global instance
- Pattern: Lazy initialization

**Implementation Quality**: ⭐⭐⭐⭐⭐
- Clean dataclass usage
- Proper error handling (re.error)
- History tracking for undo
- Serialization support (dict/JSON)
- Memory-conscious (truncate source_text in export)
- Descending sort prevents placeholder collision

**Security**: ✅
- Regex compilation in try-except
- Limits: max_registers = 100
- None-safe (handles None capture groups)

---


### File 4: src/core/filters.py (343 lines) ✅

**Purpose**: Advanced file filtering with conditions on filename, path, extension, size, mtime, and content. Supports hierarchical HTML/XML scope extraction.

**Key Features**:
- **AND/OR logic operators** for condition combining
- **Scope extraction**: brackets, braces, parentheses, custom delimiters, HTML tags, hierarchical ranges
- **Hierarchical filtering**: Include/exclude directives with CSS-like selectors (#id, tag#id)
- **Regex support**: Treat patterns as regex with flags
- **Case sensitivity**: Toggle for string matching
- **Whole word matching**: Word boundary support
- **Content filtering**: Reads files once per content-condition

**Global Operators** (line 11):
```python
OPS = {
    "contains", "not contains", "equals", "not equals",
    "starts with", "ends with", ">", "<", ">=", "<="
}
```

**Key Functions**:

**parse_hierarchical_ranges()** (line 25):
- Parses: `"include div#test1, exclude #test2, include #test3"`
- Returns: `[("include", "div#test1"), ("exclude", "#test2"), ("include", "#test3")]`
- Supports: #id, tag#id, tag, regex patterns

**apply_hierarchical_filter()** (line 62):
- Applies include/exclude filtering to HTML/XML
- **Regex mode**: Treats selectors as regex patterns
- **Selector mode**: Parses #id, tag#id, tag
- **Logic**: Include matches, then remove excluded matches
- Returns filtered text joined by newlines

**extract_scope_content()** (line 120):
- **Scope types**:
  - `"none"`: Return full text
  - `"hierarchical"`: Call apply_hierarchical_filter()
  - `"brackets"`: Extract [...] content (simple regex)
  - `"braces"`: Extract {...} content (depth-based parsing)
  - `"parentheses"`: Extract (...) content (depth-based)
  - `"custom"`: Custom delimiters (format: "begin,end")
  - `"tag"`: Extract any HTML/XML tag content
  - `"specific-tag"`: Extract specific tag content (e.g., "div")
- **Nested handling**: Braces/parentheses use depth counter (correct nesting)
- Returns concatenated content from all matches

**Condition** (dataclass, line 207):
- **Fields**:
  - field: filename, path, ext, size, mtime, content
  - operator: Any from OPS
  - value: Comparison value (string or numeric)
  - scope_type: Scope to extract before matching
  - scope_value: Additional parameter for scope
  - case_sensitive: Toggle (default True)
  - whole_word: Word boundary matching (default False)
  - use_regex: Treat value as regex (default False)

**_apply_string_matching()** (line 218):
- Handles regex + non-regex modes
- **Regex mode**:
  - Compiles pattern with flags (case insensitive if needed)
  - Adds word boundaries (\b) if whole_word enabled
  - Uses search() for contains, fullmatch() for equals, match() for starts with
- **Non-regex mode**:
  - Case-insensitive: lower() both strings
  - Whole word: Use \b regex even in non-regex mode
  - Standard string operations (in, ==, startswith, endswith)
- Returns boolean match result

**matches()** (line 280):
- Evaluates condition against file path
- **Field handlers**:
  - `filename`: Extract basename, call _apply_string_matching
  - `path`: Full path, call _apply_string_matching
  - `ext`: Extract extension (no dot), call _apply_string_matching
  - `size/mtime`: os.stat(), numeric comparison via OPS dict
  - `content`: read_text(), apply scope extraction, call _apply_string_matching
- **Scope integration**: Extracts scope content before matching (line 302-303)
- Exception-safe: Returns False on any error

**filter_files_by_conditions()** (line 312):
- Main filtering function
- **Logic operators**:
  - `"AND"`: all(c.matches(p) for c in conds) - default
  - `"OR"`: any(c.matches(p) for c in conds)
- Filters empty conditions (line 322)
- Exception-safe per file: skips failed files

**Implementation Quality**: ⭐⭐⭐⭐⭐
- **Sophisticated scope extraction**: Hierarchical HTML parsing with include/exclude
- **Flexible matching**: Regex, case-insensitive, whole word, scoped
- **Correct nesting**: Depth-based parsing for braces/parentheses
- **Performance**: Reads content once per file if needed
- **Error handling**: Try-except around all operations

**Security**: ✅
- Regex compilation in try-except (line 224-250)
- Exception-safe matches() (line 307)
- Exception-safe filter_files_by_conditions() (line 340)

**Design Patterns**:
- **Strategy Pattern**: Different scope extraction strategies
- **Composite Pattern**: Hierarchical filtering (include/exclude)

---


### File 5: src/core/command_manager.py (184 lines) ✅

**Purpose**: Command Pattern Implementation for Undo/Redo System (v2.9.8, Task #12)

**Design Pattern**: **Command (GoF)** + **Memento (GoF)**
- Encapsulates operations as objects
- Maintains history stack with configurable depth (default: 10 levels)

**Key Classes**:

**Command** (ABC, line 15):
- **Abstract methods**: execute(), undo()
- **Optional**: redo() (default: calls execute())
- **Utility**: get_description() → human-readable string

**FileModificationCommand** (line 40):
- Concrete command for single file modifications
- **State**: filepath, original_content, new_content, description
- **execute()**: Write new_content to file
- **undo()**: Restore original_content
- **redo()**: Re-execute (write new_content again)

**MultiFileCommand** (line 70):
- **Composite Pattern**: Aggregates multiple FileModificationCommand instances
- **execute()**: Execute all sub-commands
- **undo()**: Undo in **reverse order** (line 87) - Critical for correctness
- **redo()**: Redo all sub-commands
- **Description**: Shows file count

**CommandManager** (line 99):
- **Attributes**:
  - max_history: Bounded depth (default 10)
  - undo_stack: deque with maxlen (automatic eviction)
  - redo_stack: deque with maxlen

**execute_command()** (line 115):
- Executes command, adds to undo_stack
- **Clears redo_stack** (line 122) - branching timeline, can't redo after new action

**undo()** (line 124):
- Pops from undo_stack, calls command.undo()
- Pushes to redo_stack
- Returns True/False (success indicator)

**redo()** (line 137):
- Pops from redo_stack, calls command.redo()
- Pushes to undo_stack
- Returns True/False

**Utility Methods**:
- can_undo(), can_redo(): Boolean checks
- get_undo_description(), get_redo_description(): Preview next operation
- clear_history(): Empties both stacks
- get_history_stats(): Returns dict with availability, counts, max_history

**Memory Management** ✅:
- **Bounded history**: deque(maxlen=10) - automatic eviction of oldest
- Prevents infinite memory growth
- User-configurable max_history

**Implementation Quality**: ⭐⭐⭐⭐⭐
- Textbook Command pattern
- Correct Composite implementation (reverse undo)
- Bounded memory with deque
- Clean ABC design
- Exception-safe (caller handles exceptions)

**Usage in app.py**:
- Integrated in v2.9.8
- Ctrl+Z / Ctrl+Y shortcuts
- Menu items show descriptions (get_undo_description)

---


### File 6: src/core/insert.py (53 lines) ✅

**Purpose**: Text insertion at specific lines with multiple modes

**InsertMode** (class constants, line 4):
- LEFT: Insert left of line (prepend)
- RIGHT: Insert right of line (append)
- REPLACE: Replace entire line
- INSERT_ABOVE: Push line down and insert above
- INSERT_BELOW: Insert on next line (push rest down)

**insert_at_line()** (line 12):
- Inserts/modifies text at 1-based line_no
- Handles out-of-bounds: fills with empty lines
- Preserves trailing newline if original had one (line 52)
- Index clamping: max(0, min(len(lines), line_no - 1))

**Logic**:
- LEFT/RIGHT/REPLACE: Extend lines if idx >= len (lines 20-23, 28-31, 36-39)
- INSERT_ABOVE: lines.insert(idx, text) - shifts existing line down
- INSERT_BELOW: lines.insert(min(idx + 1, len(lines)), text) - after current line
- Raises ValueError for unknown modes

---

### File 7: src/core/search_replace.py (65 lines) ✅

**Purpose**: Search and replace with regex, case sensitivity, whole word options

**SearchOptions** (dataclass, line 8):
- case_sensitive: bool (default False)
- whole_word: bool (default False)
- regex: bool (default False)

**compile()** (line 14):
- Builds re.Pattern from user input + options
- **Flags**: IGNORECASE if not case_sensitive
- **Regex mode**: Use needle as-is
- **Non-regex mode**: re.escape(needle), add \b if whole_word
- Try-except: Raises ValueError on invalid regex

**preserve_case_like()** (line 29):
- Mimics case pattern from matched_text
- **ALL CAPS**: replacement.upper()
- **all lowercase**: replacement.lower()
- **Capitalized** (first upper, rest lower): capitalize()
- **Mixed**: Return as-is (no clear pattern)

**replace_in_text()** (line 48):
- Replaces occurrences using compiled pattern
- **Parameters**:
  - content: Text to search
  - pattern: Compiled re.Pattern
  - repl: Replacement string
  - preserve_case: Apply case mimicking
  - count: Max replacements (0 = all)
- **Returns**: (new_content, num_replacements)
- **Implementation**: Uses pattern.sub() with callback _repl
  - Callback increments counter, applies preserve_case_like if enabled

**Used by**: file_explorer_executor.py _replace_preserve_case()

---


### File 8: src/core/file_list_executor.py (331 lines) ✅

**Purpose**: Core file listing logic extracted from file_list_dock.py (v2.9.114 Phase 2.4.2)

**Separation of Concerns**: Business logic separated from GUI

**Key Classes**:

**FileInfo** (dataclass, line 30):
- Fields: name, path, size, mtime, permissions, owner, group, is_dir
- Directories have size=0, name appended with "/" (line 149)

**ListResult** (line 44):
- Attributes: files (List[FileInfo]), errors (List[str])
- **Auto-calculated** (line 57-59): total_size, file_count, dir_count
- Statistics computed in constructor (single-pass)

**FileListExecutor** (line 62):
- Static methods only - pure functional style

**list_files()** (line 66):
- **Parameters**: directory, show_hidden, recursive, filters (Dict)
- **Process**:
  1. Validate directory exists (line 81-82)
  2. Collect file paths via _collect_files
  3. Convert to FileInfo objects
  4. Handle errors (PermissionError, FileNotFoundError)
- **Returns**: ListResult with files and errors

**_collect_files()** (line 103):
- Recursive depth tracking (depth parameter)
- **Process**:
  1. List directory entries (sorted)
  2. Skip hidden files if not show_hidden
  3. Check directory exclusion (_should_exclude_directory)
  4. Apply filters to files (_matches_filters)
  5. Recurse into subdirectories respecting depth limit
- **Error handling**: Catches PermissionError, returns partial results

**_matches_filters()** (line 163):
- **Filters supported**:
  - **Regex**: filename pattern matching (try-except for invalid regex)
  - **Size**: min/max in bytes
  - **MTime**: after/before dates
  - **Extensions**: List of allowed extensions (normalized - no dots)
  - **Depth**: Max recursion depth
- **All filters are AND logic** (must match all)
- Exception-safe: Catches OSError on stat operations

**_should_exclude_directory()** (line 230):
- **Exclusion patterns**:
  - Direct match: dirname in exclude_dirs
  - Prefix match: "pattern*" → dirname.startswith(pattern)
  - Suffix match: "*pattern" → dirname.endswith(pattern)
- Used to skip .venv, node_modules, __pycache__, etc.

**_get_file_info()** (line 142):
- Calls os.stat() once per file
- Extracts: name, path, size, mtime, permissions, owner, group, is_dir
- Calls _format_permissions, _get_owner, _get_group

**_format_permissions()** (line 253):
- Unix-style permissions string (10 chars)
- Format: `drwxr-xr-x`
- File type: d (dir), l (link), - (file)
- Owner/Group/Other: rwx bits via stat.S_I* constants

**_get_owner()** / **_get_group()** (line 283, 291):
- Uses pwd.getpwuid() / grp.getgrgid()
- Falls back to UID/GID string if not found (KeyError/AttributeError)
- Platform: Unix/Linux-specific (uses pwd/grp modules)

**format_size_human()** (line 299):
- Converts bytes to B, KB, MB, GB, TB, PB
- 1024-based divisions
- Static utility method

**calculate_statistics()** (line 308):
- **Returns dict**:
  - total_size, total_size_human
  - file_count, dir_count, total_count
  - extensions: Dict[str, int] (extension → count)
- Extension breakdown for analysis

**Implementation Quality**: ⭐⭐⭐⭐⭐
- Clean separation of business logic from UI
- Exception-safe throughout
- Single-pass statistics
- Efficient depth tracking
- Platform-aware (pwd/grp for Unix)

**Design Patterns**:
- **Strategy Pattern**: Pluggable filters via dict
- **Template Method**: _collect_files recursive template

**Used by**: File Explorer, File List dock, possibly search operations

---


### File 9: src/core/multi_query.py (190 lines) ✅

**Purpose**: Support for multiple queries (one per line) for parallel searching

**QueryLine** (dataclass, line 14):
- Fields: raw_text, pattern (compiled), line_number (1-based)

**MultiQueryProcessor** (line 21):
- **Purpose**: Process multiple queries separated by lines
- **Features**: Comments (#), empty lines skipped, regex + non-regex modes, case sensitivity, whole word
- **Attributes**: multi_line_text, case_sensitive, whole_word, use_regex, queries (List[QueryLine])

**_parse_queries()** (line 49):
- Splits by newline, strips whitespace
- Skips empty lines and comments (line 57)
- **Error handling**: If regex compilation fails, escape as literal (line 67-75)
- Appends QueryLine with compiled pattern

**_compile_pattern()** (line 77):
- Non-regex: re.escape() (line 81)
- Whole word: Add \b boundaries (line 85)
- Flags: IGNORECASE if not case_sensitive

**search_in_text()** (line 91):
- Searches all queries via finditer()
- **Returns**: List[(line, col, snippet, query_line_number)]
- Calculates line/col from match positions
- Snippet: Full line containing match

**Utility Methods**:
- get_query_count(): len(queries)
- get_query_summary(): Display text ("1 query: ...", "N queries")
- validate(): Checks query length (<500 chars), returns (is_valid, error_message)

**split_multi_query()** (line 149):
- Utility to split text into query list (removes empty + comments)

**combine_query_results()** (line 165):
- Combines results from multiple queries
- **Deduplication**: Uses (line, col) as unique key
- Sorts by (line, col)
- Returns combined list without duplicates

**Used by**: Multi-query search dock (parallel search feature)

---

### File 10: src/core/result_exporter.py (197 lines) ✅

**Purpose**: Export results to multiple formats (CSV, Excel, YAML, TOML, JSON) - v2.9.114 Phase 2.3.4

**ResultExporter** (line 27):
- Static methods only

**FORMAT_MAP** (line 31):
- Maps filter strings to format codes: "CSV Files (*.csv)" → "csv"
- Formats: csv, xlsx, yaml, toml, json

**save_json()** (line 43):
- Saves JSON text string to file
- Returns (success, message) tuple

**export_multi_format()** (line 65):
- **Parameters**: data (dict), file_path, selected_filter, parent_widget (optional)
- **Process**:
  1. Determine format from filter
  2. Ensure correct extension (.csv, .xlsx, etc.)
  3. Call ExportManager.export() with:
     - flatten=True (for CSV/Excel/TOML)
     - include_metadata=True (timestamp + operation type)
     - parent_widget (for progress modal)
- **Error handling**: ImportError for missing dependencies (openpyxl, tomli-w)
- Returns (success, message)

**validate_export_data()** (line 115):
- Validates data before export
- Checks for None, empty data
- Returns (is_valid, error_message)

**ensure_extension()** (line 147):
- Adds extension if missing (.csv, .xlsx, etc.)
- Returns Path object

**save_json_dict()** (line 164):
- Saves dict as JSON with json.dump()
- indent=2, ensure_ascii=False

**format_json_for_display()** (line 183):
- Formats dict as pretty JSON string for UI display

**Used by**: Set operations dock, other result-generating features

---

### File 11: src/core/set_operation_executor.py (224 lines) ✅

**Purpose**: Core execution logic for set operations (∩, ∪, −, ⊕) - v2.9.114 Phase 2.3.3

**ExecutionResult** (line 32):
- Container for results + metadata
- Fields: success, results (dict), stats_lines, file_a_data, file_b_data, error

**SetOperationExecutor** (line 63):
- Static methods only

**validate_and_load_files()** (line 67):
- **Security**: Calls validate_file_path() for CWE-22 prevention
- Checks: file exists, readable, .json extension
- Loads JSON with json.load()
- Returns (success, file_dicts, error_message)
- **Error handling**: FileNotFoundError, JSONDecodeError, generic Exception

**execute_operations()** (line 104):
- **Parameters**: file_dicts, operations (list of symbols), comparison_mode, options (dict)
- **Comparison mode translation**: "full_path" → "full_path_value" (line 129-130)
- **Operations**:
  - ∩ (intersection): intersection(file_dicts, **exec_options)
  - ∪ (union): union(file_dicts, **exec_options)
  - − (difference): difference(file_dicts, **exec_options)
  - ⊕ (symmetric_difference): symmetric_difference(file_dicts[0], file_dicts[1], **exec_options) - requires exactly 2 files
- **Stats lines**: "✓ Intersection: N items"
- Stores file_a_data, file_b_data for diff viewer
- Returns ExecutionResult with success/error

**format_results_json()** (line 191):
- Pretty JSON formatting (indent=2, ensure_ascii=False)

**calculate_result_count()** (line 204):
- Sums item counts from all operation results
- Exception-safe

**Used by**: Set operations dock

---

### File 12: src/core/rewriter_cli.py (195 lines) ✅

**Purpose**: CLI execution logic for JSON/TS dedupe/rewrite operations - v2.9.114 Phase 2.2.2

**cli_dedupe()** (line 20):
- **Purpose**: Execute dedupe/rewrite based on args
- **Parameters**:
  - args: argparse.Namespace (or GUI-generated)
  - advanced_conditions: Optional list of Condition objects (Sprint B Feature #1)
  - apply_all_types: If True, apply filters to all files; if False, auto-detect .json
- **Returns**: (output_text, substitution_map, removal_stats, detailed_stats)

**Statistics Tracking** (line 45-56):
- Counters: dedupe, eliminate, numeric_keys, empty_values, duplicate_child, array_duplicates_consecutive, array_duplicates_all, no_siblings, advanced_filters_filtered

**Advanced Filters** (line 59-77, Sprint B Feature #1):
- Apply BEFORE processing
- Auto-detect JSON files unless apply_all_types=True
- Skip processing if file filtered out

**Processing Pipeline**:
1. **Read input** (line 79-81)
2. **Parse**: ts_process_full_preserving() or parse_json_preserving_duplicates_text() (line 84-89)
3. **Resolve references** (Sprint A v2.9.29, line 92-95) - if enabled
4. **Transformations** (line 98-136):
   - dedupe() - always
   - join_keys() - if enabled
   - eliminate_duplicates() + build substitution map (Task #23 v2.9.14, line 105-112)
   - exclude_numeric_keys() - if enabled
   - skip_empty_values() - if enabled
   - avoid_duplicate_child_keys() - if enabled
   - remove_duplicate_array_values() - consecutive or all (Task #8 v2.9.8, line 127-131)
   - skip_keys_without_siblings() (Task #35 v2.9.11, line 134-135)
   - **remove_duplicate_objects** (Task #52 v2.9.27 + Sprint A v2.9.29 + Sprint B Feature #4 v2.9.30, line 138-162):
     - **Reference mode** (Sprint A): create_references() with format types ($ref, #/path, etc.), relative paths
     - **Delete mode** (legacy): remove_duplicate_objects() with threshold, include_arrays, mode
   - enforce_consistent_case() (Task #9 v2.9.8, line 165-173) - camel, snake, pascal, kebab
5. **Serialize**: dump_ts_node() or dump_ts_obj() (line 176-181)
6. **Write output** (line 184-186)
7. **Collect detailed stats** (Sprint B Feature #3, line 189-190)

**Substitution Map** (Task #23, line 104-112):
- Extract keys+values BEFORE elimination
- Extract keys+values AFTER elimination
- Build map by VALUE EQUALITY (not string similarity)
- Maps removed keys to their replacements

**Reference Resolver** (Sprint A v2.9.29 + Sprint B Feature #4 v2.9.30):
- **create_references()**: Creates $ref, #/path references to duplicate objects
- **resolve_references()**: Resolves existing references FIRST
- **Formats**: "$ref", "#/path" (JSON Pointer), relative paths
- **Stats**: references_created, references_resolved, references_invalid

**Case Styles** (Task #9 v2.9.8):
- camel, snake, pascal, kebab
- Warns inconsistencies (prints first 10 warnings)

**Used by**: JSON Rewriter dock, CLI interface

---

## 📊 CORE MODULE SUMMARY (12 files, 4,732 lines) ✅

**Architecture**: Clean separation of business logic from UI (v2.9.114 Phase 2)

**Key Patterns**:
- **Command Pattern**: command_manager.py (undo/redo)
- **Memento Pattern**: memory_register.py (capture state)
- **Strategy Pattern**: filters.py (pluggable filtering), file_list_executor.py
- **Composite Pattern**: command_manager.py (MultiFileCommand)
- **Static Executors**: Separation of concerns (pure functions)

**Security** ✅:
- ReDoS prevention (file_explorer_executor.py, filters.py)
- Path validation (set_operation_executor.py - CWE-22)
- Exception-safe operations throughout
- Memory limits (file_explorer_executor.py)

**Notable Features**:
- Hierarchical HTML/XML filtering (filters.py)
- Memory Register with $N placeholders (memory_register.py)
- Multi-query parallel search (multi_query.py)
- Reference resolver for duplicate objects (rewriter_cli.py)
- Undo/Redo with bounded history (command_manager.py)
- Multi-format export (result_exporter.py)

---


---

# GUI LAYER (BRANCHES) - Architecture Analysis

## 📖 File 13: src/gui/base_dock.py (596 lines) ✅

**Purpose**: Foundation for Mixin Composition pattern - reusable components for tool docks

**Critical Architecture Pattern**: **Mixin Composition (75% code reduction)**

### Utility Functions:

**parse_extensions_to_globs()** (line 21):
- Converts ".py,.js" → ["*.py", "*.js"]
- Handles with/without dots, comma/semicolon separators
- Used for extension filtering (v2.9.0)

### Base Class:

**BaseDock** (line 47, extends QDockWidget):
- Foundation for all tool docks
- Attributes: main_widget, layout (QVBoxLayout)
- Template methods: _setup_ui(), _connect_signals() (override in subclasses)
- Utility methods: show_error(), show_info(), show_warning()

---

### Mixin 1: FileInputMixin (line 79)

**Purpose**: File/directory input with browse button

**create_file_input()** (line 82):
- Returns: (label, line_edit, browse_button, is_file_checkbox)
- is_file_checkbox optional (toggle file vs directory)

**create_extension_filter()** (line 107, v2.9.0):
- Default: ".py,.js,.tsx,.jsx,.ts,.md"
- Returns: (label, line_edit)
- Tooltip with usage instructions

**browse_file_or_directory()** (line 126):
- Opens QFileDialog (getOpenFileName or getExistingDirectory)
- Sets selected path to line_edit

---

### Mixin 2: ResultsOutputMixin (line 178)

**Purpose**: Results output panel with search, context menu, "Open in Editor"

**create_results_panel()** (line 181):
- Returns: (label, text_edit)
- QTextEdit with readOnly=True
- **Ctrl+F shortcut**: Opens search dialog
- **Context menu** (Qt.CustomContextMenu): "Open in Editor", Copy, Select All

**_show_search_dialog()** (line 208):
- Find Next/Previous with QTextEdit.find()
- Find Backward with QTextDocument.FindBackward
- Return key triggers Find Next

**_open_results_in_editor()** (line 288, Task #6 v2.9.19):
- **Auto-detects extension** via _detect_content_extension()
- Creates **temporary file** (tempfile.NamedTemporaryFile, delete=False)
- Opens in EditorDock with **edit_only=True** (sandbox mode)
- Cleans up temp file if editor not found

**_detect_content_extension()** (line 348):
- **JSON**: starts with { or [, validates with json.loads()
- **HTML**: starts with <, contains <html/<div/<span/<body
- **XML**: starts with <, generic fallback
- **TypeScript/JS**: contains const/let/function/=>
- **Python**: contains def/import/class/from
- **Default**: .txt

**_get_editor_dock()** (line 386):
- Traverses parent hierarchy to find main window
- Uses parent.findChild(EditorDock)

**add_open_in_editor_button()** (line 406):
- Adds button to layout, connects to _open_results_in_editor()
- Returns button instance

---

### Mixin 3: ActionButtonsMixin (line 433)

**Purpose**: Common action buttons creation

**create_action_buttons()** (line 436):
- Input: List[(button_text, callback), ...]
- Creates QHBoxLayout with QPushButtons
- **Stores references** as attributes: `btn_{text.lower().replace(' ', '_')}`
- Example: "Process File" → self.btn_process_file

---

### Mixin 4: OptionsGroupMixin (line 464)

**Purpose**: Option groups (checkboxes, spinboxes)

**create_checkbox_group()** (line 467):
- Input: List[(text, default_checked, tooltip), ...]
- Returns: List[QCheckBox]
- Applies default state and tooltips

**create_spinbox_input()** (line 491):
- Returns: (label, spinbox)
- Parameters: label_text, min_val, max_val, default, step

---

### Mixin 5: ValidationMixin (line 513)

**Purpose**: Input validation helpers

**validate_file_path()** (line 516):
- Checks: not empty, exists (if must_exist=True)
- Returns: (is_valid, error_message)

**validate_not_empty()** (line 531):
- Checks: text not empty
- Returns: (is_valid, error_message)

**validate_file_writable()** (line 542):
- Creates directory if missing (os.makedirs)
- Checks: os.access(path, os.W_OK)
- Returns: (is_valid, error_message)

---

### Composite Class:

**StandardToolDock** (line 563):
- **Multiple Inheritance**: BaseDock + 5 Mixins
- **75% code reduction** - shared logic extracted
- **_setup_enter_key_execution()** (line 578): Connects Enter key to _execute_action()
- **_execute_action()** (line 591): Template method for execution (override in subclasses)

**Usage Pattern**:
```python
class MyDock(StandardToolDock):
    def __init__(self, parent=None):
        super().__init__("My Tool", parent)
    
    def _setup_ui(self):
        # Use mixin methods
        lbl, edit, btn, chk = self.create_file_input("Input:")
        lbl2, results = self.create_results_panel()
        actions = self.create_action_buttons([("Process", self._process)])
        # ... layout composition
    
    def _process(self):
        # Validation
        valid, msg = self.validate_file_path(self.edit.text())
        if not valid:
            self.show_error("Error", msg)
            return
        # ... processing logic
```

---

### ProcessorWorkerBase (line 146):

**Purpose**: Base class for background QThread workers

**Signals**:
- progress (str): Progress messages
- finished_ok (object): Result data on success
- failed (str): Error message on failure

**Methods**:
- request_interrupt(): Sets interrupt_requested flag
- emit_progress(), emit_error(), emit_success(): Signal emitters
- check_interrupt(): Returns interrupt status

**Used by**: AI processor, file explorer, batch processing workers

---

### Design Patterns Validated:

1. **Mixin Composition** (GoF Decorator-like):
   - 5 mixins with single responsibility
   - Multiple inheritance for feature composition
   - No diamond problem (each mixin independent)

2. **Template Method** (GoF):
   - _setup_ui(), _connect_signals(), _execute_action() - overridden by subclasses

3. **Observer** (GoF):
   - Qt Signals/Slots for thread communication

4. **DRY Principle**:
   - 75% code reduction via mixins
   - Shared validation, UI components, patterns

**Implementation Quality**: ⭐⭐⭐⭐⭐
- Clean mixin design
- Single responsibility per mixin
- Comprehensive helper methods
- Task #6 (Open in Editor) fully integrated
- Auto-detection logic for extensions
- Proper error handling

**Used by**: 20+ dock classes (all tool docks inherit from StandardToolDock or BaseDock+mixins)

---


## 📖 File 14: src/gui/dock_factory.py (253 lines) ✅

**Purpose**: Factory pattern for creating and configuring GUI dock widgets (v2.9.114 Phase 3.3)

**Refactoring**: Extracted from app.py MainWindow class (lines 1266-1360, ~95 lines)

**DockFactory** (line 25):
- Static methods only
- Centralizes dock creation logic
- Reduces duplication

**create_dock()** (line 37):
- **Standard pattern**:
  1. Create dock instance (dock_class)
  2. Store in main_window as attribute (setattr)
  3. Add to main window (addDockWidget)
  4. Connect signals (optional)
  5. Set visibility (hide by default)
- **Parameters**:
  - main_window: QMainWindow
  - dock_class: Class to instantiate
  - dock_attr_name: Attribute name (e.g., 'dock_translate')
  - area: Qt.DockWidgetArea (default: RightDockWidgetArea)
  - hide: Initial visibility (default: True)
  - signal_connections: Dict[signal_name, slot]
  - **dock_kwargs: Constructor arguments
- **Returns**: Created dock widget

**create_dock_lazy()** (line 92):
- **Lazy initialization**: Creates dock only if not exists
- Checks: hasattr(main_window, dock_attr_name)
- Falls back to create_dock() if missing

**Convenience Methods** (lines 118-252):
- **14+ dock types**: translate, rewriter, text_extractor, placeholder_replacer, ai_processor, json_search, case_converter, jsx_extractor, text_to_json, file_list, file_explorer, history, tutorials, editor, google_translate, advanced_extractor
- **Pattern**: Import dock class, call create_dock/create_dock_lazy
- **Special cases**:
  - history_dock: BottomDockWidgetArea, max_entries=10, lazy
  - tutorials_dock, editor_dock: Lazy initialization

**Design Pattern**: **Factory (GoF)**
- Encapsulates object creation
- Centralizes configuration
- Reduces coupling

**Implementation Quality**: ⭐⭐⭐⭐⭐
- Clean separation of concerns
- Consistent API
- Lazy initialization support
- Signal connections support

**Used by**: app.py MainWindow (reduces ~95 lines of duplicated code)

---


## 📖 File 15: src/gui/file_explorer_dock.py (2,066 lines) ✅

**Purpose**: Unified File List + Advanced File Search (v2.9.115, 80% overlap consolidation)

**Major Achievement**: Consolidates two separate tools with 80% code overlap

**Key Features**:
- **Dual mode**: Dock (normal) or Dialog (modal selection)
- **Smart detection**: Auto-detects Browse vs Search mode based on filters
- **File type filter**: Files Only / Directories Only / Any
- **Selection mode**: Multi-select and return selected files
- **Unix-style options**: -la (all+long), -lh (human readable), -R (recursive)
- **Advanced filters**: regex, size, mtime, extensions, depth, excludes
- **Presets system**: Save/load/export/import filter configurations
- **Dual view**: Tree view (search results) vs Table view (file listings)
- **Collapsible sections**: Directory, Search/Replace, Filters, Conditions, Presets (v2.9.117 B.6)
- **Threading**: QThread worker for non-blocking UI (v2.9.122)
- **Batch processing**: Process results in batches of 100 items (v2.9.123)
- **Replace operations**: Replace first/all with search+replace integration

### Architecture:

**Composition** (extracted components - v2.9.116):
- FileFilterPanel: Advanced filters UI
- PresetManager: Save/load/export/import presets
- FileListTableManager: Table display management
- FileNameQueryPanel: Filename pattern input
- ContentQueryPanel: Content search input
- SearchOptionsPanel: Case, whole word, regex options
- ReplacePanel: Replacement text + buttons
- ConditionsGrid: AND/OR logic with multiple conditions
- CollapsibleSection: Animated section collapse/expand

**Worker Threading** (v2.9.122):
- FileExplorerWorker: QThread worker for executor
- Signals: progress, progress_detailed, batch_ready, finished, error
- Non-blocking UI during long operations

**Signals & Slots**:
```python
# From executor
executor.progress.connect(_on_progress)
executor.progress_detailed.connect(_on_progress_detailed)
executor.done.connect(_on_execution_done)
executor.error.connect(_on_execution_error)

# From worker
worker.progress.connect(_on_progress)
worker.batch_ready.connect(_on_batch_ready)  # NEW v2.9.123
worker.finished.connect(_on_search_finished)
worker.error.connect(_on_operation_error)
```

### Key Methods:

**_list_files_smart()** (line 857):
- Auto-detects mode: Search (if filename/content filters) or Browse (no filters)
- Unified button behavior (v2.9.117 B.7)

**_list_files()** (line 883):
- Main execution method
- **Security**: OWASP A01 Path Traversal Prevention (CWE-22, line 895-918)
  - os.path.abspath() normalization
  - os.path.isdir() validation
  - os.access(R_OK) permission check
- Threading integration (v2.9.122, line 972-1000)
- Creates QThread + FileExplorerWorker
- Connects signals for progress tracking

**_on_batch_ready()** (line 1653, v2.9.123):
- **Purpose**: Process results in batches to prevent UI freezing
- **Batch size**: 100 items per batch
- **Process**: Runs in UI thread, but doesn't block (processes one batch then returns)
- Allows event loop to handle paint, input events between batches
- Updates progress dialog with batch progress
- Cancellation support

**_on_replace_first()** / **_on_replace_all()** (lines 1439, 1519):
- Replace operations with executor
- History integration (OperationHistory)
- Confirmation dialogs
- Refresh file list after replace

**_format_permissions()** (line 813):
- Unix-style permissions: drwxr-xr-x
- Uses pwd/grp modules for owner:group
- Fallback for Windows (no pwd/grp)

### UI Sections (Collapsible with Animation - v2.9.117 B.6):

1. **Directory & Type** (📁): Directory input, Unix options, type filter
2. **Search & Replace** (🔍): Filename, content, options, replacement
3. **Filters** (⚙️): Advanced filters panel
4. **Advanced Conditions** (🎯): AND/OR logic conditions grid
5. **Presets** (💾, Dock only): Save/load/export/import presets

### View Modes (v2.9.118):

**Tree View** (default for search):
- Hierarchical display of search results
- Shows matches with context
- Word wrap control

**Table View** (default for browse):
- Columns: Name | Size | Modified | Permissions | Path
- Sort/filter capabilities
- Context menu: "Open in File Manager"

**Smart View Switching**:
- Auto-switches based on operation (unless user manually changed)
- User manual override respected (_user_manually_changed_view flag)

### Security & Quality:

**Security** ✅:
- Path Traversal Prevention (OWASP A01, CWE-22)
- Path normalization (os.path.abspath)
- Permission validation (os.access)
- Directory validation (os.path.isdir)

**Performance** ✅:
- Threading for non-blocking UI (v2.9.122)
- Batch processing (100 items/batch, v2.9.123)
- Progress dialogs with cancellation
- Lazy initialization of dialogs

**Structured Logging** ✅:
- logger.info/warning/error with extra context
- Logs directory, filters, operation mode
- Exception logging with exc_info=True

### Dialog Mode:

When dialog_mode=True:
- Adds OK/Cancel buttons (QDialogButtonBox)
- Selection mode enabled by default
- Multi-select file selection
- Returns selected_files list via _accept_dialog()

### State Management:

**Preferences** (QSettings):
- Last directory
- Recent directories list
- Unix options state
- View mode preference
- Filter configurations

**Synchronization**:
- last_search_results: Dict for tree view
- last_browse_results: List for table view
- last_was_search: Track operation type
- View synchronization methods

### Integration with Executor:

Uses **UnifiedFileExplorerExecutor** (from core):
- execute_browse(): List files with filters
- execute_search(): Search with filename/content patterns
- execute_replace(): Replace operations
- Unified API for both browse and search

### Code Quality: ⭐⭐⭐⭐⭐

- Excellent component extraction (8+ extracted components)
- Clean separation of concerns
- Security-conscious (OWASP compliance)
- Performance-aware (threading, batching)
- Comprehensive logging
- i18n support with retranslateUi()
- Accessibility considerations

---


## 📖 File 16: src/gui/json_rewriter_dock.py (1,054 lines) ✅

**Purpose**: JSON/TypeScript rewriter with deduplication, format conversion, and reference management

**Extends**: BaseDock

**Major Features**:
1. **Basic Options**:
   - From TS/JS: Parse TypeScript/JavaScript object literals
   - Emit export default: Add TS export wrapper
   - Join keys: Merge nested keys (user.name)
   - Eliminate duplicates: Remove duplicate values
   - No blank lines: Compact formatting
   - Configurable indentation (-1 to 16 spaces)

2. **Advanced Filtering** (10+ options):
   - Exclude numeric keys
   - Skip empty values
   - Avoid duplicate child keys
   - Normalize escaping
   - Convert arrays to objects
   - Skip keys without siblings
   - Remove consecutive array duplicates
   - Remove all array duplicates
   - Enforce consistent case (camelCase, PascalCase, snake_case, kebab-case)
   - Case validation with preview (chk_validate_case)

3. **Duplicate Objects** (Task #52):
   - Remove duplicate objects (chk_remove_dup_objects)
   - Include arrays in detection (chk_include_dup_arrays)
   - Similarity threshold (50-100%)
   - Mode: Remove or References

4. **Reference System**:
   - **Task #23**: Update orphaned references across project
   - **Sprint A v2.9.29**: Reference resolver
     - Radio: Delete duplicates (default) or Use references
     - Resolve existing references first (chk_resolve_refs)
   - **Sprint B Feature #4 v2.9.30**: Reference format configuration
     - Formats: $ref, #/ (JSON Pointer), @ (custom)
     - Include line numbers option
     - Use relative paths option
   - Project directory scanning with backup creation

5. **Advanced Filters** (Sprint B Feature #1):
   - Configure conditions BEFORE processing
   - 3 condition rows with AND logic
   - Fields: filename, path, ext, size, mtime, content
   - Operators: contains, equals, starts with, ends with, >, <, >=, <=
   - Scope: none, brackets, braces, parentheses, custom, tag, specific-tag, hierarchical
   - Case sensitive + regex toggles
   - Apply to all file types (chk_apply_all_types)

### Key Methods:

**_rewrite()** (line 524):
- Main execution method
- **Case validation flow** (line 535-599):
  - If chk_validate_case enabled:
    - Parses input file
    - Shows case_validator_dialog with preview + warnings
    - User accepts/cancels
    - Writes converted object directly (bypasses cli_dedupe case conversion)
    - Temporarily disables enforce_case to avoid double conversion
  - Returns early if validated
- **Normal flow**: Builds argparse.Namespace, calls cli_dedupe()
- Advanced filters integration (Sprint B Feature #1, line 615-635):
  - apply_conditions_to_files() filters files BEFORE processing
  - Logs filtered count
- Reference resolver integration (Sprint A, line 641-649)
- Shows removal statistics dialog with format_removal_statistics()
- Logs operation with structured logging

**_configure_reference_format()** (line 366, Sprint B Feature #4):
- QDialog with 3 format types: $ref, #/ (JSON Pointer), @ (custom)
- Include line numbers checkbox
- Use relative paths checkbox
- Saves to QSettings

**_open_advanced_filters_dialog()** (line 409, Sprint B Feature #1):
- QDialog with 3 condition rows
- Fields: filename, path, ext, size, mtime, content
- Operators: 11 options (contains, equals, comparisons)
- Scope: 8 types (none, brackets, braces, etc.)
- Case sensitive + regex toggles
- Loads existing conditions into UI
- Saves via get_conditions_from_ui(cond_rows)
- Feedback message shows configured filter count

**_open_input_file() / _open_output_file()** (line 329, 339):
- QFileDialog.getOpenFileName / getSaveFileName
- Filter: JSON files (*.json) or TypeScript files (*.ts, *.js)
- Sets ed_in / ed_out text

**_browse_project_directory()** (line 349):
- QFileDialog.getExistingDirectory for reference updates
- Sets ed_project_dir text

### Accessibility:

**Comprehensive Accessibility** (line 830-1054):
- AccessibilityManager.set_accessible_widget() for ALL widgets
- Names: "JSON Rewriter - Type - Widget Name"
- Descriptions: Detailed usage instructions
- Examples:
  - "JSON Rewriter - Checkbox - Eliminate Duplicates" / "Remove duplicate values and consolidate keys"
  - "JSON Rewriter - SpinBox - Similarity Threshold Percentage" / "Percentage threshold for detecting similar objects (0-100)"
- 60+ widgets with accessibility labels

### State Persistence:

**QSettings** (load/save preferences):
- Input/output file paths
- All checkbox states (20+ options)
- Indentation value
- Case style selection
- Duplicate threshold
- Reference format configuration (Sprint B Feature #4)
- Advanced filters configuration (Sprint B Feature #1)
  - Serializes Condition objects to JSON
  - Stores in QSettings as JSON string

### Integration with Core:

**cli_dedupe()** (from core):
- Builds argparse.Namespace with all options
- Passes advanced_conditions (Sprint B Feature #1)
- Passes apply_all_types flag
- Returns: (output_text, substitution_map, removal_stats, detailed_stats)

**format_removal_statistics()** (from utils):
- Displays removal statistics in dialog
- Shows counts for each transformation type

### Code Quality: ⭐⭐⭐⭐⭐

**Strengths**:
- Comprehensive feature coverage (20+ transformation options)
- Sprint A/B features fully integrated
- Excellent accessibility (60+ labeled widgets)
- State persistence with QSettings
- Clear separation of concerns (dialogs, core logic, UI)
- Structured logging
- Case validation with preview (chk_validate_case)

**Notable Patterns**:
- Radio buttons for mode selection (delete vs references)
- Conditional widgets (disable when parent unchecked)
- Dialog reuse for configuration
- Comprehensive error handling

---


## 📖 File 17: src/gui/initialization_manager.py (166 lines) ✅

**Purpose**: Centralizes MainWindow initialization logic (Phase 3.7 refactoring, v2.9.114)

**Problem Solved**: Reduced MainWindow.__init__ from 1106 lines to organized sections

**InitializationManager** (static class):
- No instance methods - all static
- Groups initialization into 4 logical sections

### Methods:

**initialize_core_systems()** (line 34):
- **Logging**: get_logger("clarify.app.MainWindow") (v2.9.58)
- **Error Reporter**: install_error_reporter(app_version="2.9.89") with ErrorReportDialog
- **Crash Handler**: install_crash_handler(show_dialog=True, report_crashes=False) - opt-in only (v2.9.61)

**initialize_configuration()** (line 64):
- **Migrations**: run_migrations() BEFORE loading config/settings (v2.9.91)
  - Returns migrations_ok bool
  - Logs warning if failed, continues anyway
- **Translator**: get_translator(), connects languageChanged signal (Task #24 v2.9.10)
- **Settings**: get_settings(), creates QSettings("Clarify", "ClarifyApp") for accessibility (v2.9.40)

**initialize_managers()** (line 92):
- **ShortcutManager**: Loads custom shortcuts (v2.9.33)
- **CommandManager**: Undo/Redo with max_history=10 (Task #12 v2.9.8)
- **PluginLoader**: Discovers + activates plugins (v2.9.109)
  - discover_plugins() → count
  - activate_all_plugins() → activated count
  - Prints plugin counts
- **tool_tabs**: Dict[str, (widget, tab_index)] for tracking tabs (v2.9.40)
- **LayoutManager**: Initialized (v2.9.84)

**build_ui_components()** (line 128):
- Sets window title via tr("app.title")
- Calls _build_icon(), _build_ui(), _build_menu()
- Restores preferences via _restore_prefs(), _apply_saved_settings()
- Registers docks with LayoutManager (_register_docks_with_layout_manager)

**initialize_all()** (line 151):
- **Master method**: Runs all steps in correct order
- Stores app reference
- Order matters for dependencies!
- Single entry point for complete initialization

### Design Pattern: **Facade (GoF)**
- Simplifies complex initialization
- Provides single interface for multi-step process
- Makes MainWindow cleaner and more testable

---

## 📖 File 18: src/gui/menu_builder.py (458 lines) ✅

**Purpose**: Centralizes menu creation logic (Phase 3.4 refactoring, v2.9.114)

**Problem Solved**: Extracts menu building from MainWindow, reducing coupling

**MenuBuilder** (static class):
- No instance methods - all static
- Builds 8 menus + shortcuts

### Master Method:

**build_all_menus()** (line 25):
- Entry point - calls all menu builders
- Builds: File, Edit, Tools, View, Themes, Settings, Plugins, Help, About
- Sets up shortcuts

### Menu Builders:

**_build_file_menu()** (line 46):
- **New from Template** (v2.9.63): Ctrl+Shift+N
- **Open Editor**: Ctrl+E → _show_editor()
- **Exit**: closes window

**_build_edit_menu()** (line 74, Task #12 v2.9.8):
- **Undo**: Ctrl+Z → _undo(), initially disabled
- **Redo**: Ctrl+Y → _redo(), initially disabled
- **Clear History**: → _clear_undo_history()

**_build_tools_menu()** (line 99):
- **16+ tool actions**: Search/Replace, Insert, Translate, Rewriter, Text Extractor, Placeholder Replacer, AI Processor, JSON Search, Case Converter, Text to JSON, Google Translate, Set Operations, Calculator, Formula Builder, File Explorer (Ctrl+Shift+F), Advanced Extractor (Ctrl+Shift+E)
- **Fixed tabs accessibility** (v2.9.40.2 - Task: menu for closed tabs)
- All tools have act_open_* actions with tooltips/shortcuts
- Connected to _show_* methods

**_build_view_menu()** (line 170):
- **Toggle History**: checkable action → _toggle_history()
- **Layouts submenu** (v2.9.84):
  - Presets: Compact, Standard, Advanced
  - Save current layout
  - Manage layouts dialog
  - Connected to layout_manager.apply_preset()

**_build_themes_menu()** (line 204):
- **3 themes**: System (default), Light, Dark
- Checkable actions (QAction with checkable=True)
- Mutually exclusive (not shown in excerpt, likely QActionGroup)
- Connected to _apply_theme_action()

**_build_settings_menu()** (line 223):
- **Preferences**: General settings
- **Shortcuts**: Customization
- **Transparency**: Window opacity
- **Language submenu** (Task #24 v2.9.10, expanded v2.9.43):
  - **7 languages**: English, Português (Brasil), Español, Français, Deutsch, 中文 (简体), 日本語
  - **QActionGroup**: Radio button behavior (exclusive, only one selected)
  - Checkable actions (act_lang_en, act_lang_pt, act_lang_es, act_lang_fr, act_lang_de, act_lang_zh, act_lang_ja)

### Pattern Observations:

**Action Creation Pattern**:
```python
act_name = QAction(tr("menu.key"), main_window)
act_name.setShortcut("Ctrl+X")
act_name.setToolTip(tr("menu.tooltip_key"))
menu.addAction(act_name)
act_name.triggered.connect(main_window._method)
```

**Exclusive Actions (Radio Buttons)**:
- Use QActionGroup with setExclusive(True)
- Add all related actions to group
- Only one can be checked at a time

**Design Pattern**: **Builder (GoF)**
- Step-by-step construction of complex menus
- Separates construction from representation
- Each _build_*_menu() is a builder step

### Code Quality: ⭐⭐⭐⭐⭐
- Clean separation of concerns
- i18n support (tr() for all strings)
- Consistent naming (act_*, m_*)
- Object names for plugin access (setObjectName)
- Tooltips and shortcuts well-documented

---

