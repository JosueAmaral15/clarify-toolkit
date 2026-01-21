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

