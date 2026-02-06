# Code Study Session 15 Notes
**Programmer:** #7  
**Date:** 2026-01-23  
**Phase:** 4.1 - Support Systems (Widgets Module)  
**Files Studied:** 12 files (3,358 lines)  
**Session Focus:** Complete widgets module - extracted reusable UI components

---

## 📋 Session Overview

**Objective:** Study all 12 widget files in `src/gui/widgets/` extracted during v2.9.114+ refactoring

**Files Analyzed:**
1. ✅ `__init__.py` (41 lines) - Exports 16 widget classes
2. ✅ `path_entry.py` (76 lines) - File/directory path input
3. ✅ `collapsible_section.py` (182 lines) - Animated expandable sections
4. ✅ `json_tree_widget.py` (169 lines) - JSON structure navigation
5. ✅ `syntax_highlighter.py` (186 lines) - Multi-language highlighting
6. ✅ `file_selection_widget.py` (280 lines) - File picker with pipeline
7. ✅ `operation_options_widget.py` (320 lines) - Set operations config
8. ✅ `preset_manager.py` (320 lines) - Save/load/export presets
9. ✅ `file_filter_panel.py` (392 lines) - Advanced file filters
10. ✅ `editor_tab.py` (398 lines) - Text editor with edit-only mode
11. ✅ `search_widgets.py` (476 lines) - 5 search UI components
12. ✅ `file_list_table_manager.py` (518 lines) - File list table display

**Total Lines Studied:** 3,358 lines  
**Design Patterns Identified:** 8 patterns  
**Key Discovery:** Component extraction refactoring (v2.9.114+) successfully DRYed code

---

## 🎯 Key Discoveries

### 1. Component Extraction Refactoring (v2.9.114+)

**Before Extraction:**
- Monolithic docks with embedded UI logic
- `file_list_dock.py`: 800+ lines (filters, presets, table all embedded)
- `set_operations_dock.py`: ~600-800 lines (file selection, options embedded)
- `editor_dock.py`: ~500-700 lines (tab management, syntax highlighting embedded)
- Code duplication across docks
- Harder to test and maintain

**After Extraction:**
- `file_list_dock.py`: 293 lines (coordination only)
- Extracted: `FileFilterPanel` (392 lines), `PresetManager` (320 lines), `FileListTableManager` (518 lines)
- `set_operations_dock.py`: ~200-300 lines (uses widgets)
- Extracted: `FileSelectionWidget` (280 lines), `OperationOptionsWidget` (320 lines)
- `editor_dock.py`: ~200-300 lines (uses widgets)
- Extracted: `EditorTab` (398 lines), `SyntaxHighlighter` (186 lines)

**Benefits:**
- ✅ **DRY Principle**: Extracted widgets reused across multiple docks
- ✅ **Testability**: Each widget can be tested independently
- ✅ **Maintainability**: Fix widget bug once → all users benefit
- ✅ **Clarity**: Smaller classes with focused responsibilities
- ✅ **Reusability**: `FileFilterPanel` used in multiple docks

**Refactoring Pattern:**
```
Monolithic Dock (800+ lines)
    ↓
Extract UI Components
    ↓
Reusable Widgets (100-500 lines each)
    ↓
Dock Coordinator (200-300 lines)
```

---

## 📁 File-by-File Analysis

### 1. `__init__.py` (41 lines)

**Purpose:** Package initialization - exports 16 widget classes

**Exported Classes:**
1. `PathEntry` - File/directory path input
2. `FileSelectionWidget` - File picker (2-file or multi-file pipeline)
3. `OperationOptionsWidget` - Set operations configuration
4. `FileFilterPanel` - Advanced file filters (regex, size, mtime, extensions)
5. `PresetManager` - Save/load/export/import presets
6. `FileListTableManager` - File list table display
7. `SyntaxHighlighter` - Multi-language syntax highlighting
8. `EditorTab` - Text editor with edit-only mode
9. `JsonTreeWidget` - JSON structure tree navigation
10. `FileNameQueryPanel` - Filename pattern search
11. `ContentQueryPanel` - Content search query
12. `SearchOptionsPanel` - Search options (case, regex, whole-word)
13. `ReplacePanel` - Replace options panel
14. `ConditionsGrid` - Search conditions grid
15. `CollapsibleSection` - Animated collapsible sections

**Design:** Clean public API via `__all__` list

---

### 2. `path_entry.py` (76 lines)

**Purpose:** Reusable path input widget with browse/remove buttons

**Extracted From:** `ai_processor_dock.py` (v2.9.114)

**Features:**
- File/directory selection via QFileDialog
- "Is File" checkbox to switch modes
- Browse button (80px max width)
- Remove button (red, bold, disabled for first path)
- Placeholder text with i18n support
- Callback on removal

**UI Components:**
- `lbl_path`: Path label ("Path 1:", "Path 2:", etc.)
- `ed_path`: Line edit for path input
- `btn_browse`: Browse button (triggers file/directory dialog)
- `chk_is_file`: Checkbox to mark as file vs directory
- `btn_remove`: Remove button (calls callback)

**Public API:**
```python
get_path() -> str              # Get path value
is_file() -> bool              # Check if marked as file
_browse()                      # Browse for file/directory
_remove()                      # Remove this entry
```

**Usage Pattern:**
```python
# AI Processor Dock uses multiple PathEntry widgets
path1 = PathEntry(1, on_remove_callback)
path2 = PathEntry(2, on_remove_callback)
# User can add/remove paths dynamically
```

**Design Pattern:** None (simple data widget)

---

### 3. `collapsible_section.py` (182 lines)

**Purpose:** Animated expandable/collapsible sections

**Version:** v2.9.117 - B.6 (Animation improvements)

**Features:**
- Click header to expand/collapse
- Smooth height animation (300ms default, QEasingCurve.InOutQuad)
- Customizable header colors
- Remembers state (checkable header button)
- Content widget container with frame

**UI Components:**
- `header_button`: QPushButton (checkable, triggers animation)
- `content_frame`: QFrame (animated via QPropertyAnimation)
- `content_layout`: VBoxLayout for content widget
- `_animation`: QPropertyAnimation on `maximumHeight` property

**Public API:**
```python
setContent(widget)             # Set content widget
setTitle(title)                # Set section title
setCollapsed(collapsed)        # Set state (no animation)
isCollapsed() -> bool          # Get collapsed state
setAnimationDuration(ms)       # Set animation speed
setHeaderStyle(collapsed_color, expanded_color)  # Customize colors
```

**Animation Logic:**
- **Collapsing:** Current height → 0 (then hide)
- **Expanding:** Show → 0 → content height → unlimited (16777215)
- **Easing Curve:** InOutQuad (smooth acceleration/deceleration)

**Usage Pattern:**
```python
section = CollapsibleSection("Advanced Options")
section.setContent(filter_panel)
section.setCollapsed(True)  # Start collapsed
```

**Design Pattern:** **Composite** (container for widget hierarchy)

**Key Implementation Detail:**
- Disconnect old `finished` signal before reconnecting (lines 144-147)
- Set `maximumHeight = 16777215` (unlimited) after expansion completes
- `setVisible(False)` after collapse completes to save resources

---

### 4. `json_tree_widget.py` (169 lines)

**Purpose:** Tree navigation for JSON structures

**Extracted From:** `json_editor_tab.py` (v2.9.114 - Phase 2.6.1)

**Features:**
- Hierarchical tree view (QTreeWidget)
- Click node → emit line number signal
- Visual indicators: `{}` for objects, `[]` for arrays
- Color coding by type (6 types)
- Collapse/Expand all controls
- Alternating row colors

**UI Components:**
- QTreeWidget with 3 columns: Key, Value, Type
- Column widths: 200, 300, 80
- `line_map`: Dict[QTreeWidgetItem, int] - maps nodes to line numbers

**Signal:**
- `node_clicked(int)`: Emitted with line number when node clicked

**Public API:**
```python
build_tree(json_text)          # Parse JSON and build tree
_add_node(parent, key, value, line)  # Recursive node builder
```

**Type Color Coding:**
| Type | Color | Hex Code | Visual |
|------|-------|----------|--------|
| Object | Light Blue | #9CDCFE | {...} (N keys) |
| Array | Teal | #4EC9B0 | [...] (N items) |
| String | Orange | #CE9178 | "value" (truncated at 50 chars) |
| Number | Light Green | #B5CEA8 | 123.45 |
| Boolean | Blue | #569CD6 | true / false |
| Null | Gray | #808080 | null |

**Recursive Tree Building:**
```python
def _add_node(parent, key, value, line):
    if isinstance(value, dict):
        # Object: Add children recursively
        for child_key, child_value in value.items():
            _add_node(item, child_key, child_value, line + 1)
    elif isinstance(value, list):
        # Array: Add indexed children
        for i, child_value in enumerate(value):
            _add_node(item, f"[{i}]", child_value, line + 1)
    else:
        # Leaf node: String, Number, Boolean, Null
        # Set text and color, no children
```

**Design Pattern:** **Composite** (GoF) - Recursive tree structure

**Key Implementation Detail:**
- Line number tracking via `line_map` dict (used for jump-to-line feature)
- `expandAll()` called after building tree (line 92)
- String truncation at 50 characters with "..." suffix

---

### 5. `syntax_highlighter.py` (186 lines)

**Purpose:** Multi-language syntax highlighting

**Extracted From:** `editor_dock.py` (v2.9.114 - Phase 2.5.1)

**Supported Languages:**
- **HTML/JSX/TSX**: Tags, attributes, strings, comments
- **JSON**: Keys, values, numbers, brackets, booleans/null
- **Python**: Keywords (35 total), strings (4 types), comments, numbers
- **JavaScript/TypeScript**: Keywords (34 total), strings (3 types), comments, numbers

**UI Components:**
- Inherits from `QSyntaxHighlighter`
- Operates on `QTextDocument` (provided by QTextEdit)
- Uses `QTextCharFormat` for styling
- Uses `QRegularExpression` for pattern matching

**Text Formats (8 formats):**
| Format | Color | Style | Usage |
|--------|-------|-------|-------|
| `tag_format` | #569CD6 Blue | Bold | HTML/JSX tags |
| `attr_format` | #9CDCFE Light Blue | Normal | HTML attributes |
| `string_format` | #CE9178 Orange | Normal | Strings |
| `keyword_format` | #C586C0 Purple | Bold | Keywords |
| `comment_format` | #6A9955 Green | Italic | Comments |
| `json_key_format` | #9CDCFE Light Blue | Normal | JSON keys |
| `number_format` | #B5CEA8 Light Green | Normal | Numbers |
| `bracket_format` | #FFD700 Gold | Bold | JSON brackets |

**Highlighting Rules (file type dependent):**

**HTML/JSX/TSX Rules:**
- Tags: `</?[\w-]+` and `/?>`
- Attributes: `\b[\w-]+(?==)`
- Strings: `"[^"\\]*(\\.[^"\\]*)*"` and `'[^'\\]*(\\.[^'\\]*)*'`
- Comments: `<!--.*?-->`

**JSON Rules:**
- Keys: `"[\w\s.-]+"(?=\s*:)` (lookahead for colon)
- Strings: `"[^"\\]*(\\.[^"\\]*)*"`
- Numbers: `\b\d+\.?\d*\b`
- Brackets: `[{}\[\]]`
- Booleans/Null: `\b(true|false|null)\b`

**Python Rules:**
- Keywords: 35 keywords (def, class, if, for, True, False, None, etc.)
- Strings: `"""..."""`, `'''...'''`, `"..."`, `'...'`
- Comments: `#[^\n]*`
- Numbers: `\b\d+\.?\d*\b`

**JavaScript/TypeScript Rules:**
- Keywords: 34 keywords (const, let, var, function, async, await, etc.)
- Strings: `"..."`, `'...'`, `` `...` `` (template literals)
- Comments: `//[^\n]*` and `/\*.*?\*/`
- Numbers: `\b\d+\.?\d*\b`

**Public API:**
```python
__init__(document, file_type)  # Initialize with file type
highlightBlock(text)           # Apply highlighting to block
```

**Design Pattern:** **Strategy** (GoF) - Different highlighting strategies per file type

**Key Implementation Detail:**
- Regex patterns compiled once in `_setup_rules()` based on file type
- `highlightBlock()` iterates through rules and applies formats via `globalMatch()`
- Color scheme matches VS Code Dark+ theme

---

### 6. `file_selection_widget.py` (280 lines)

**Purpose:** Reusable file selection component

**Extracted From:** `set_operations_dock.py` (v2.9.114 - Phase 2.3.1)

**Features:**
- **Two-file mode**: File A + File B
- **Multiple files mode**: Pipeline processing (left-to-right)
- Browse/Add/Remove/Clear operations
- File change signals
- i18n support
- Accessibility labels

**UI Components:**
- `ed_file_a`: Line edit for File A
- `btn_browse_a`: Browse button for File A
- `ed_file_b`: Line edit for File B
- `btn_browse_b`: Browse button for File B
- `chk_multiple`: Checkbox to enable pipeline mode
- `list_files`: QListWidget (hidden by default)
- `btn_add_file`: Add file to list
- `btn_remove_file`: Remove selected file
- `btn_clear_files`: Clear file list

**Signal:**
- `files_changed(list)`: Emitted when file list changes

**Public API:**
```python
get_files() -> List[str]       # Get file list (A/B or multi-file)
set_files(files)               # Set file list programmatically
clear()                        # Clear all selections
is_multiple_mode() -> bool     # Check if pipeline mode enabled
```

**Mode Switching Logic:**
```python
# Two-file mode → Multiple files mode:
# 1. Show list_files, show add/remove/clear buttons
# 2. Populate list with File A and B if they exist
# 3. Emit files_changed signal

# Multiple files mode → Two-file mode:
# 1. Hide list_files, hide buttons
# 2. File A/B remain editable
```

**Usage Pattern:**
```python
# Set Operations Dock:
file_widget = FileSelectionWidget(
    title="Select Files",
    file_filter="JSON Files (*.json);;All Files (*)"
)
file_widget.files_changed.connect(self._on_files_changed)

# Get files for processing:
files = file_widget.get_files()
# Returns: ['file_a.json', 'file_b.json'] or ['f1.json', 'f2.json', 'f3.json']
```

**Design Pattern:** None (data collection widget with signal emission)

**Key Implementation Detail:**
- `_on_files_changed()` emits signal whenever file list changes
- Connected to: `ed_file_a.textChanged`, `ed_file_b.textChanged`, `list_files.model().rowsInserted/Removed`
- Accessibility labels via `AccessibilityManager.set_accessible_widget()`

---

### 7. `operation_options_widget.py` (320 lines)

**Purpose:** Set operations configuration component

**Extracted From:** `set_operations_dock.py` (v2.9.114 - Phase 2.3.2)

**Features:**
- Operation checkboxes (4 operations)
- Comparison mode radio buttons (3 modes)
- Advanced options (4 checkboxes)
- Output format combo box (3 formats)
- Configuration save/load
- i18n support
- Accessibility labels

**UI Components:**

**Operations Group:**
- `chk_intersection`: Intersection (∩)
- `chk_union`: Union (∪)
- `chk_difference`: Difference (−)
- `chk_symmetric`: Symmetric Difference (⊕)

**Comparison Mode Group:**
- `radio_key_value`: Compare keys and values (strict types)
- `radio_full_path`: Compare full paths (dot notation, deep nested)
- `radio_key_only`: Compare only keys (ignore values)

**Options Group:**
- `chk_ignore_case_keys`: Treat 'Name' and 'name' as identical
- `chk_ignore_case_values`: Treat 'Hello' and 'hello' as identical
- `chk_skip_empty`: Skip null, empty string, empty array, empty object
- `chk_arrays_ignore_order`: Treat [1,2,3] and [3,2,1] as identical

**Output Format Group:**
- `combo_output`: JSON Nested / Separate Files / Display Only

**Signal:**
- `options_changed()`: Emitted when any option changes

**Public API:**
```python
get_selected_operations() -> List[str]  # Returns ['∩', '∪', '−', '⊕']
get_comparison_mode() -> str            # Returns 'key_value' / 'full_path' / 'key_only'
get_options() -> Dict[str, bool]        # Returns option flags
get_output_format() -> str              # Returns 'nested' / 'separate' / 'display'
set_configuration(config)               # Set from dict
clear()                                 # Clear all selections
```

**Usage Pattern:**
```python
# Set Operations Dock:
opts_widget = OperationOptionsWidget()
opts_widget.options_changed.connect(self._on_options_changed)

# Get configuration:
operations = opts_widget.get_selected_operations()  # ['∩', '∪']
mode = opts_widget.get_comparison_mode()            # 'key_value'
options = opts_widget.get_options()                 # {'ignore_case_keys': True, ...}
```

**Design Pattern:** None (configuration widget with signal emission)

**Key Implementation Detail:**
- All options emit `options_changed` signal when modified
- `set_configuration()` accepts dict and updates all UI components
- Accessibility labels describe each option's purpose

---

### 8. `preset_manager.py` (320 lines)

**Purpose:** Save/load/export/import filter presets

**Extracted From:** `file_list_dock.py` (v2.9.114 - Phase 2.4.3)

**Features:**
- Save presets to QSettings (persistent across sessions)
- Load presets from QSettings
- Delete presets with confirmation
- Export presets to JSON files (shareable)
- Import presets from JSON files
- Preset combo box with selection event
- Callback-based architecture (get/apply filters)

**UI Components:**
- `cmb_presets`: QComboBox listing presets
- `btn_save`: Save current filters as preset
- `btn_load`: Load selected preset
- `btn_delete`: Delete selected preset
- `btn_delete`: Delete selected preset (with confirmation)
- `btn_export`: Export preset to JSON file
- `btn_import`: Import preset from JSON file

**Signals:**
- `preset_loaded(dict)`: Emitted when preset loaded with filter dict
- `preset_saved(str)`: Emitted when preset saved with preset name

**Public API:**
```python
set_callbacks(get_filters, apply_filters)  # Set get/apply callbacks
save_preset()                              # Save current filters
load_preset()                              # Load selected preset
delete_preset()                            # Delete preset (with confirmation)
export_preset()                            # Export to JSON file
import_preset()                            # Import from JSON file
```

**Callback Architecture:**
```python
# Dock sets callbacks:
preset_manager.set_callbacks(
    get_filters=self._get_current_filters,    # Returns Dict[str, Any]
    apply_filters=self._apply_filters_to_ui   # Accepts Dict[str, Any]
)

# Preset Manager calls callbacks:
filters = self._get_filters_callback()        # Get current state
settings.setValue(preset_name, json.dumps(filters))  # Save

filters = json.loads(settings.value(preset_name))    # Load
self._apply_filters_callback(filters)                # Apply to UI
```

**Storage Format (QSettings):**
```
Organization: "Clarify"
Application: settings_group (e.g., "FileListDock")
Group: "Presets"
Key: preset_name
Value: JSON string of filter dict
```

**Export/Import JSON Format:**
```json
{
  "preset_name": "My Filter",
  "filters": {
    "regex": "*.json",
    "size_min": 1024,
    "extensions": ["json", "txt"]
  }
}
```

**Usage Pattern:**
```python
# File List Dock:
preset_mgr = PresetManager(settings_group="FileListDock")
preset_mgr.set_callbacks(self._get_filters, self._apply_filters)
preset_mgr.preset_loaded.connect(self._on_preset_loaded)

# User saves preset:
# 1. User configures filters
# 2. User clicks "Save Preset" → Input dialog for name
# 3. Preset Manager calls get_filters() → saves to QSettings
# 4. Combo box updated with new preset

# User loads preset:
# 1. User selects preset from combo box
# 2. Preset Manager loads from QSettings → calls apply_filters()
# 3. UI updates with saved filter values
```

**Design Pattern:** **Strategy** (callbacks define get/apply strategies)

**Key Implementation Detail:**
- QSettings path: `Clarify / settings_group / Presets / preset_name`
- JSON serialization for storage (ensures compatibility)
- Export/Import uses QFileDialog with JSON filter
- Delete requires confirmation via QMessageBox
- Combo box selection triggers auto-load (lines 59-62)

---

### 9. `file_filter_panel.py` (392 lines)

**Purpose:** Advanced file filtering widget

**Extracted From:** `file_list_dock.py` (v2.9.114 - Phase 2.4.1)

**Features:**
- Regex pattern matching (with enable checkbox)
- Size filters (min/max with units: B, KB, MB, GB)
- Modified time filters (after/before dates with enable checkboxes)
- Extension filters (comma-separated, with enable checkbox)
- Depth limit (0 = unlimited, 1-10 levels)
- Exclude directories (common + custom)
- Collapsible panel (QGroupBox.setCheckable)
- i18n support

**UI Components:**

**Row 0: Regex Filter**
- `ed_regex`: Line edit for pattern
- `chk_regex_enabled`: Enable checkbox

**Row 1-2: Size Filters**
- `ed_size_min`: Min size value
- `cmb_size_min_unit`: Unit combo (B/KB/MB/GB)
- `ed_size_max`: Max size value
- `cmb_size_max_unit`: Unit combo (B/KB/MB/GB)

**Row 3-4: Modified Time Filters**
- `dte_mtime_after`: QDateEdit (after date)
- `chk_mtime_after_enabled`: Enable checkbox
- `dte_mtime_before`: QDateEdit (before date)
- `chk_mtime_before_enabled`: Enable checkbox

**Row 5: Extensions Filter**
- `ed_extensions`: Comma-separated extensions
- `chk_use_ext_filter`: Enable checkbox

**Row 6: Depth Limit**
- `spn_depth`: QSpinBox (0 = unlimited, 1-10 levels)

**Row 7-8: Exclude Directories**
- `chk_exclude_common`: Exclude common dirs (node_modules, .git, etc.)
- `ed_exclude_custom`: Custom exclude patterns (comma-separated)

**Signal:**
- `filters_changed()`: Emitted when any filter changes

**Public API:**
```python
get_filters() -> Dict[str, Any]  # Get filter dict
apply_filters(filters)           # Apply filter dict to UI
clear_filters()                  # Clear all filters
validate_regex() -> bool         # Validate regex pattern
_size_to_bytes(value, unit) -> int  # Convert size to bytes
_format_size_human(bytes) -> str    # Format bytes to human-readable
```

**Filter Dict Structure:**
```python
{
    'regex': '*.json',
    'regex_enabled': True,
    'size_min': 1024,           # Bytes
    'size_max': 10485760,       # Bytes
    'mtime_after': datetime(2024, 1, 1),
    'mtime_after_enabled': True,
    'mtime_before': datetime(2024, 12, 31),
    'mtime_before_enabled': True,
    'extensions': ['json', 'txt'],
    'use_ext_filter': True,
    'max_depth': 3,
    'exclude_common': True,
    'exclude_custom': ['backup', 'temp']
}
```

**Size Unit Multipliers:**
```python
SIZE_UNITS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3
}
```

**Common Excluded Directories:**
```python
COMMON_EXCLUDES = [
    'node_modules', '.git', '.svn', '.hg', '__pycache__',
    '.pytest_cache', '.tox', 'venv', 'env', '.venv',
    'dist', 'build', '.cache', 'coverage', '.mypy_cache'
]
```

**Usage Pattern:**
```python
# File List Dock:
filter_panel = FileFilterPanel(title="Advanced Filters")
filter_panel.filters_changed.connect(self._on_filters_changed)

# Get filters for file listing:
filters = filter_panel.get_filters()
# Apply to FileManager.list_files():
files = file_manager.list_files(directory, filters)

# Load saved preset:
filter_panel.apply_filters(preset_filters)
```

**Design Pattern:** **Facade** (simplifies complex filtering logic)

**Key Implementation Detail:**
- Collapsible via `setCheckable(True)` and `setChecked(False)` (line 61-62)
- Size conversion via `_size_to_bytes()` with unit multipliers
- Date filtering uses QDateEdit with calendar popup
- Extension filter: split on comma, strip whitespace, filter empty
- Regex validation via `re.compile()` with try/except

---

### 10. `editor_tab.py` (398 lines)

**Purpose:** Single file editor tab with sandbox mode

**Extracted From:** `editor_dock.py` (v2.9.114 - Phase 2.5.2)

**Features:**
- Text editing with syntax highlighting (via SyntaxHighlighter)
- File loading and saving
- Modified state tracking (with signal emission)
- **Edit-only mode** (State Pattern - sandbox editing without file backing)
- Auto-save functionality (3-second timer after last modification)
- Toolbar (copy, export, enable saving)
- Visual indicators (golden border for edit-only mode)

**UI Components:**
- `editor`: QTextEdit (main text editor)
- `toolbar`: QToolBar with 3 buttons
- `btn_copy`: Copy to clipboard
- `btn_export`: Export to file
- `btn_enable_saving`: Convert edit-only → file-backed (only visible in edit-only mode)
- `highlighter`: SyntaxHighlighter instance
- `auto_save_timer`: QTimer (3 seconds single-shot)

**Signals:**
- `modified_changed(bool)`: Emitted when modified state changes
- `edit_only_changed(bool)`: Emitted when edit-only mode changes
- `auto_saved()`: Emitted when file is auto-saved

**Edit-Only Mode (State Pattern):**

**Normal Mode:**
- File backed by file path
- Ctrl+S saves to file
- Tab title: "filename.ext"
- Border: Normal
- "Enable Saving" button hidden

**Edit-Only Mode:**
- NO file backing (file_path can be None)
- Ctrl+S disabled (sandbox)
- Tab title: "🔒 filename.ext"
- Border: 3px golden (#FFD700)
- Background: Cornsilk (#FFF8DC)
- "Enable Saving" button visible
- **Use Case:** Experiment with text without affecting original file

**Visual Indicators (4 indicators):**
1. **Golden Border** (3px solid #FFD700)
2. **Cornsilk Background** (#FFF8DC)
3. **Lock Icon** (🔒 in tab title)
4. **"Enable Saving" Button** (visible only in edit-only mode)

**State Transition:**
```
Edit-Only Mode → Normal Mode:
1. User clicks "Enable File Saving" button
2. Confirmation dialog: "Convert to file-backed editor?"
3. If Yes: Save As dialog → Save content → Update state
4. file_path set, edit_only_mode = False
5. Update visual indicators, setup syntax highlighter
6. Emit edit_only_changed(False) and modified_changed(False)
```

**Auto-Save Logic:**
```python
# Conditions for auto-save:
1. auto_save_enabled = True
2. file_path is not None (not untitled)
3. NOT in edit_only_mode (sandbox mode)
4. is_modified = True

# Timer behavior:
- textChanged → Start 3-second timer
- textChanged again → Restart 3-second timer
- 3 seconds of no changes → _auto_save() called
- Save successful → emit auto_saved signal
```

**Public API:**
```python
load_file(file_path) -> bool           # Load file content
save_file(file_path=None) -> bool      # Save content to file
get_tab_title() -> str                 # Get filename or "Untitled"
get_display_title() -> str             # Get title with indicators
get_status_text() -> str               # Get status text
set_auto_save(enabled)                 # Enable/disable auto-save
toggle_edit_only_mode()                # Toggle edit-only mode
```

**Usage Pattern:**
```python
# Editor Dock creates multiple tabs:
tab1 = EditorTab(file_path="file.py")  # Normal mode
tab2 = EditorTab(edit_only_mode=True)   # Edit-only mode

# Connect signals:
tab1.modified_changed.connect(self._update_tab_title)
tab1.auto_saved.connect(self._show_status_message)
tab1.edit_only_changed.connect(self._update_ui)

# Load file:
success = tab1.load_file("config.json")

# Enable auto-save:
tab1.set_auto_save(True)
```

**Design Pattern:** **State** (GoF) - edit_only_mode changes behavior

**Key Implementation Detail:**
- `_update_visual_indicators()` applies golden border stylesheet (lines 225-237)
- `_on_text_changed()` sets `is_modified = True` and starts auto-save timer
- `blockSignals(True)` during `load_file()` to prevent modified signal (line 291)
- `_setup_highlighter()` based on file extension (line 263)
- Monospace font: "Courier New", 10pt (line 89)
- Tab stop distance: 40 (4 spaces equivalent, line 85)

---

### 11. `search_widgets.py` (476 lines)

**Purpose:** 5 reusable search/replace UI components

**Extracted From:** `search_replace_panel.py` (v2.9.116 integration)

**Components (5 classes):**

#### 1. `FileNameQueryPanel` (77 lines)
- Filename pattern input with regex support
- Signal: `pattern_changed(str)`, `clear_requested()`
- UI: Label + LineEdit + Clear button

#### 2. `ContentQueryPanel` (101 lines)
- Multi-line text editor for content search
- Signal: `query_changed(str)`
- UI: Label + QTextEdit (max height 80px)
- Monospaced font support

#### 3. `SearchOptionsPanel` (126 lines)
- Checkboxes for search options
- Signal: `options_changed(dict)`
- Options:
  - `chk_case_sensitive`: Case-sensitive matching
  - `chk_whole_word`: Match whole words only
  - `chk_regex`: Enable regex mode
  - `chk_recursive`: Search subdirectories
- Public API: `get_options() -> dict`, `set_options(dict)`, `clear()`

#### 4. `ReplacePanel` (156 lines)
- Replace text input with options
- Signal: `replace_changed(str)`
- UI: Label + QTextEdit (max height 60px) + Options
- Options:
  - `chk_preserve_case`: Preserve original case
  - `chk_backup`: Create backup files before replace
- Public API: `get_replace_text() -> str`, `get_options() -> dict`, `set_replace_text(str)`, `clear()`

#### 5. `ConditionsGrid` (remaining lines)
- Grid layout for early/late conditions
- Used for advanced filtering in file operations

**Usage Pattern:**
```python
# File Explorer Dock integrates search widgets:
filename_panel = FileNameQueryPanel()
content_panel = ContentQueryPanel()
options_panel = SearchOptionsPanel()
replace_panel = ReplacePanel()

# Connect signals:
filename_panel.pattern_changed.connect(self._on_pattern_changed)
options_panel.options_changed.connect(self._on_options_changed)

# Get values:
pattern = filename_panel.get_pattern()
query = content_panel.get_query()
options = options_panel.get_options()
# Returns: {'case_sensitive': True, 'whole_word': False, 'regex': True, 'recursive': True}
```

**Design Pattern:** **Composite** (combines multiple search UI components)

**Key Implementation Detail:**
- Extracted from `search_replace_panel.py` for reusability
- Each widget emits specific signal when value changes
- `clear()` methods for resetting state (v2.9.117)
- i18n support via `tr()` function

---

### 12. `file_list_table_manager.py` (518 lines)

**Purpose:** File list table display and interaction

**Extracted From:** `file_list_dock.py` (v2.9.114 - Phase 2.4.4)

**Features:**
- Table configuration and styling
- Populate table with file info (FileInfo objects)
- Quick filter on visible rows
- Context menu (open in file manager)
- Multi-selection support
- Export to CSV
- Statistics display (file count, dir count, total size)
- Human-readable size formatting
- DateTime formatting (intelligible for users)

**UI Components:**
- `ed_quick_filter`: LineEdit for filtering visible rows
- `table`: QTableWidget (5 columns, sortable, multi-selection)
- `lbl_stats`: QLabel showing statistics
- `btn_export`: QPushButton for CSV export

**Table Columns (5 columns):**
| Index | Column | Content | Alignment | Resize Mode |
|-------|--------|---------|-----------|-------------|
| 0 | Name | Filename | Left | ResizeToContents |
| 1 | Size | Human-readable size | Right | Fixed |
| 2 | Modified | DateTime (YYYY-MM-DD HH:MM:SS) | Left | Fixed |
| 3 | Permissions | Unix permissions (rwxr-xr-x) | Center | Fixed |
| 4 | Path | Full file path | Left | Stretch |

**Signal:**
- `files_exported(str)`: Emitted when CSV export completes with filepath

**Public API:**
```python
populate(files, human_readable=True)   # Populate table with file list
clear()                                # Clear table
export_csv()                           # Export to CSV file
_apply_quick_filter()                  # Filter visible rows
_show_context_menu()                   # Show context menu
_open_in_file_manager(path)            # Open file in OS file manager
_format_size_human(bytes) -> str       # Format bytes to human-readable
```

**File Info Dict Structure:**
```python
{
    'name': 'file.json',
    'size': 12345,                      # Bytes
    'mtime': 1706006400,                # Unix timestamp
    'permissions': 'rwxr-xr-x',
    'path': '/full/path/to/file.json',
    'is_dir': False
}
```

**Size Formatting:**
```python
# Human-readable format:
1234 bytes → "1.21 KB"
1048576 bytes → "1.00 MB"
1073741824 bytes → "1.00 GB"

# Tooltip shows both:
"1.21 KB (1,234 bytes)"
```

**DateTime Formatting:**
```python
# Display format (intelligible):
Unix timestamp 1706006400 → "2024-01-23 12:00:00"

# Tooltip format (contextual):
"Monday, January 23, 2024 at 12:00:00 PM"
```

**Quick Filter Logic:**
```python
# Filter on visible rows (case-insensitive):
filter_text = "json"
for row in range(table.rowCount()):
    name = table.item(row, COL_NAME).text()
    path = table.item(row, COL_PATH).text()
    visible = filter_text.lower() in name.lower() or filter_text.lower() in path.lower()
    table.setRowHidden(row, not visible)
```

**Context Menu:**
- "Open in File Manager" (Windows: explorer, macOS: open -R, Linux: xdg-open)
- Uses `subprocess.Popen()` with platform detection
- v2.9.121 bugfix: Explicit main_window reference to fix crash

**CSV Export Format:**
```csv
Name,Size (bytes),Modified,Permissions,Path
file.json,12345,2024-01-23 12:00:00,rwxr-xr-x,/full/path/to/file.json
...
```

**Statistics Display:**
```python
# Example:
"Files: 42 | Directories: 7 | Total Size: 12.34 MB"
```

**Usage Pattern:**
```python
# File List Dock:
table_manager = FileListTableManager(main_window=self._main_window_ref)
table_manager.files_exported.connect(self._on_files_exported)

# Populate table:
files = file_manager.list_files(directory, filters)
table_manager.populate(files, human_readable=True)

# Export to CSV:
table_manager.export_csv()
```

**Design Pattern:** **Facade** (simplifies table operations)

**Key Implementation Detail:**
- v2.9.121 bugfix: Explicit `main_window` parameter to fix QObject crash (lines 52, 61)
- Alternating row colors for readability
- Sortable columns via `setSortingEnabled(True)`
- Word wrap disabled, text elide mode middle (v2.9.117, lines 97-99)
- Context menu via `customContextMenuRequested` signal
- Platform-specific file manager commands:
  - Windows: `explorer /select,<path>`
  - macOS: `open -R <path>`
  - Linux: `xdg-open <dir>` (opens directory, not file)

---

## 🎨 Design Patterns Identified

### Pattern Summary (8 patterns)

| Pattern | Usage | Files | Purpose |
|---------|-------|-------|---------|
| **Strategy** | Syntax highlighting strategies | syntax_highlighter.py, preset_manager.py | Different highlighting per file type, callback-based get/apply |
| **State** | Edit-only mode behavior | editor_tab.py | Changes save behavior and visual indicators |
| **Composite** | Tree structure, widget hierarchies | json_tree_widget.py, collapsible_section.py, search_widgets.py | Recursive JSON tree, container widgets |
| **Facade** | Simplify complex operations | file_filter_panel.py, file_list_table_manager.py | Abstract filtering and table management |
| **Observer** | Signal emission on changes | All widgets | Qt Signal/Slot pattern for communication |
| **Template Method** | Implied in widget initialization | All widgets | `_setup_ui()` → `_connect_signals()` → `_apply_accessibility()` |
| **Adapter** | Callback architecture | preset_manager.py | Adapts preset manager to any dock's filter structure |
| **Decorator** | Syntax highlighter wraps QTextDocument | syntax_highlighter.py | Adds syntax highlighting to plain text editor |

### Pattern Details

#### 1. Strategy Pattern
**Files:** `syntax_highlighter.py`, `preset_manager.py`

**Purpose:** Switch algorithms/behaviors at runtime

**Implementation:**
```python
# syntax_highlighter.py:
class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, file_type: str):
        self.file_type = file_type
        self._setup_rules()  # Different rules per file type
    
    def _setup_rules(self):
        if self.file_type == "json":
            # JSON rules
        elif self.file_type in ["py", "python"]:
            # Python rules
        # ... more strategies

# preset_manager.py:
class PresetManager:
    def set_callbacks(self, get_filters, apply_filters):
        self._get_filters_callback = get_filters
        self._apply_filters_callback = apply_filters
    # Callbacks define get/apply strategies
```

#### 2. State Pattern
**Files:** `editor_tab.py`

**Purpose:** Change behavior based on state (edit-only mode)

**Implementation:**
```python
class EditorTab(QWidget):
    def __init__(self, edit_only_mode: bool = False):
        self.edit_only_mode = edit_only_mode
        self._update_visual_indicators()
        self._update_toolbar_visibility()
    
    # Behavior changes based on state:
    def save_file(self):
        if self.edit_only_mode:
            return False  # Cannot save in edit-only mode
        # ... normal save logic
    
    def _update_visual_indicators(self):
        if self.edit_only_mode:
            # Golden border, cornsilk background
        else:
            # Normal appearance
```

#### 3. Composite Pattern
**Files:** `json_tree_widget.py`, `collapsible_section.py`, `search_widgets.py`

**Purpose:** Build recursive tree/widget hierarchies

**Implementation:**
```python
# json_tree_widget.py:
def _add_node(self, parent, key, value, line):
    item = QTreeWidgetItem(parent or self)
    
    if isinstance(value, dict):
        # Object: Add children recursively
        for child_key, child_value in value.items():
            self._add_node(item, child_key, child_value, line + 1)
    # ... leaf nodes
```

#### 4. Facade Pattern
**Files:** `file_filter_panel.py`, `file_list_table_manager.py`

**Purpose:** Simplify complex subsystems

**Implementation:**
```python
# file_filter_panel.py:
class FileFilterPanel(QGroupBox):
    def get_filters(self) -> Dict[str, Any]:
        # Complex logic to gather 8+ filter types
        # Returns simple dict
        return {
            'regex': self._get_regex(),
            'size_min': self._get_size_min(),
            # ... 6 more filters
        }

# file_list_table_manager.py:
class FileListTableManager(QWidget):
    def populate(self, files, human_readable=True):
        # Complex table setup, formatting, statistics
        # Simple interface: just pass file list
```

#### 5. Observer Pattern (Qt Signal/Slot)
**Files:** All widgets

**Purpose:** Loose coupling via event emission

**Implementation:**
```python
# All widgets emit signals:
files_changed = Signal(list)
options_changed = Signal()
preset_loaded = Signal(dict)

# Docks connect to signals:
widget.files_changed.connect(self._on_files_changed)
```

#### 6. Template Method Pattern
**Files:** All widgets (implicit)

**Purpose:** Define common initialization skeleton

**Implementation:**
```python
# Common pattern across all widgets:
class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()         # Step 1: Create UI
        self._connect_signals()  # Step 2: Connect signals
        self._apply_accessibility()  # Step 3: Accessibility (if needed)
```

#### 7. Adapter Pattern
**Files:** `preset_manager.py`

**Purpose:** Adapt preset manager to different dock filter structures

**Implementation:**
```python
# Preset manager doesn't know filter structure:
class PresetManager:
    def set_callbacks(self, get_filters, apply_filters):
        # Callbacks adapt to any filter structure
        self._get_filters_callback = get_filters
        self._apply_filters_callback = apply_filters
    
    def save_preset(self):
        filters = self._get_filters_callback()  # Adapted to dock
        # ... save filters
    
    def load_preset(self):
        filters = # ... load filters
        self._apply_filters_callback(filters)  # Adapted to dock
```

#### 8. Decorator Pattern
**Files:** `syntax_highlighter.py`

**Purpose:** Add syntax highlighting to QTextDocument

**Implementation:**
```python
# SyntaxHighlighter decorates QTextDocument:
class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, file_type):
        super().__init__(document)  # Wraps document
        # Adds highlighting behavior without modifying QTextDocument
```

---

## 🔗 Integration Points

### Widget → Dock Usage

| Widget | Used By Docks | Purpose |
|--------|---------------|---------|
| `PathEntry` | ai_processor_dock | Multiple path inputs |
| `CollapsibleSection` | Multiple docks | Collapsible filter panels |
| `JsonTreeWidget` | json_editor_tab (panel) | JSON structure navigation |
| `SyntaxHighlighter` | editor_dock, json_editor_tab | Code highlighting |
| `FileSelectionWidget` | set_operations_dock | File A/B or pipeline selection |
| `OperationOptionsWidget` | set_operations_dock | Set operation configuration |
| `PresetManager` | file_list_dock, file_filter_dock | Save/load filter presets |
| `FileFilterPanel` | file_list_dock, file_explorer_dock | Advanced file filtering |
| `EditorTab` | editor_dock | Multi-tab text editing |
| `SearchWidgets` | file_explorer_dock, search_replace_panel | Search/replace UI |
| `FileListTableManager` | file_list_dock | File list display |

### Signal Flow Examples

**Example 1: File Selection**
```
User browses file → FileSelectionWidget.btn_browse_a.clicked
→ FileSelectionWidget._browse_file('a')
→ FileSelectionWidget.ed_file_a.setText(file_path)
→ FileSelectionWidget.files_changed.emit([file_path])
→ SetOperationsDock._on_files_changed(files)
→ SetOperationsDock updates button states
```

**Example 2: Preset Loading**
```
User selects preset → PresetManager.cmb_presets.currentIndexChanged
→ PresetManager._on_preset_selected()
→ PresetManager.load_preset()
→ PresetManager calls _apply_filters_callback(filters)
→ Dock._apply_filters(filters)
→ Dock updates FileFilterPanel, PresetManager
→ PresetManager.preset_loaded.emit(filters)
```

**Example 3: Auto-Save**
```
User types in editor → EditorTab.editor.textChanged
→ EditorTab._on_text_changed()
→ EditorTab.is_modified = True
→ EditorTab.modified_changed.emit(True)
→ EditorTab.auto_save_timer.start(3000)
→ 3 seconds pass → EditorTab._auto_save()
→ EditorTab.save_file()
→ EditorTab.auto_saved.emit()
→ Dock shows status message
```

---

## 🔍 Critical Code Sections

### 1. EditorTab Edit-Only Mode State Management

**File:** `editor_tab.py`  
**Lines:** 54-96, 185-257

**Why Critical:**
- State Pattern implementation - behavior changes based on edit_only_mode
- 4 visual indicators must stay synchronized
- Auto-save must be disabled in edit-only mode
- State transition requires user confirmation

**Key Logic:**
```python
def __init__(self, edit_only_mode: bool = False):
    self.edit_only_mode = edit_only_mode
    self._update_visual_indicators()  # Must be called
    self._update_toolbar_visibility()  # Must be called

def _enable_file_saving(self):
    # Convert edit-only → file-backed
    # 1. Confirm with user
    # 2. Save As dialog
    # 3. Update state: edit_only_mode = False, file_path = new_path
    # 4. Update visuals: _update_visual_indicators(), _update_toolbar_visibility()
    # 5. Emit signals: edit_only_changed(False), modified_changed(False)
```

**Don't Touch:**
- Visual indicator logic (lines 225-237) - golden border values are user-facing
- State transition flow (lines 185-223) - carefully orchestrated
- Signal emission order matters

### 2. PresetManager Callback Architecture

**File:** `preset_manager.py`  
**Lines:** 91-104, 106-136, 138-171

**Why Critical:**
- Callbacks must be set before use (else error)
- Filter dict structure is dock-dependent (preset manager is agnostic)
- QSettings key namespace must match settings_group

**Key Logic:**
```python
def set_callbacks(self, get_filters, apply_filters):
    # MUST be called by dock after initialization
    self._get_filters_callback = get_filters
    self._apply_filters_callback = apply_filters

def save_preset(self):
    if not self._get_filters_callback:
        # Error: callback not set
        return
    filters = self._get_filters_callback()  # Get from dock
    # Save to: Clarify / settings_group / Presets / preset_name
    settings.setValue(preset_name, json.dumps(filters))
```

**Don't Touch:**
- Callback validation (lines 108-110)
- QSettings namespace (lines 122-125)
- JSON serialization (lines 124, 151) - ensures compatibility

### 3. FileListTableManager Context Menu Platform Detection

**File:** `file_list_table_manager.py`  
**Lines:** 280-330 (context menu), 332-372 (_open_in_file_manager)

**Why Critical:**
- Platform-specific commands for Windows/macOS/Linux
- subprocess.Popen() usage - must handle errors
- v2.9.121 bugfix: Explicit main_window reference

**Key Logic:**
```python
def _open_in_file_manager(self, path: str):
    system = platform.system()
    
    if system == "Windows":
        subprocess.Popen(['explorer', '/select,', path])
    elif system == "Darwin":  # macOS
        subprocess.Popen(['open', '-R', path])
    else:  # Linux
        directory = os.path.dirname(path)
        subprocess.Popen(['xdg-open', directory])
```

**Don't Touch:**
- Platform detection logic (exact command syntax)
- subprocess.Popen() usage (not subprocess.run - needs async)
- v2.9.121 bugfix: `main_window` parameter (line 52)

### 4. SyntaxHighlighter Regex Rules

**File:** `syntax_highlighter.py`  
**Lines:** 88-171 (_setup_rules)

**Why Critical:**
- Regex patterns carefully crafted to avoid overlaps
- Order matters (first match wins in some cases)
- Pattern complexity affects performance

**Key Logic:**
```python
def _setup_rules(self):
    # JSON key pattern: lookahead for colon
    QRegularExpression(r'"[\w\s.-]+"(?=\s*:)')
    
    # String pattern: handle escaped quotes
    QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')
    
    # Python triple-quoted strings (must come before single quotes)
    QRegularExpression(r'""".*?"""')  # Before "..."
```

**Don't Touch:**
- Regex pattern order (triple quotes before single quotes)
- Lookahead patterns (JSON keys)
- Escape sequence handling in strings

### 5. FileFilterPanel Size Conversion

**File:** `file_filter_panel.py`  
**Lines:** 43-49 (SIZE_UNITS), size conversion methods

**Why Critical:**
- Size unit multipliers must be powers of 1024 (binary, not decimal)
- User input validation required
- Human-readable formatting must match storage format

**Key Logic:**
```python
SIZE_UNITS = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3
}

def _size_to_bytes(self, value: float, unit: str) -> int:
    return int(value * self.SIZE_UNITS[unit])

def _format_size_human(self, bytes: int) -> str:
    # Use 1024 divisor (binary), not 1000 (decimal)
```

**Don't Touch:**
- SIZE_UNITS values (must be powers of 1024)
- Size conversion logic (binary vs decimal ambiguity)

---

## 💡 Architectural Insights

### 1. Component Extraction Success Metrics

**Quantitative Improvements:**
- **file_list_dock.py:** 800+ lines → 293 lines (63% reduction)
- **set_operations_dock.py:** ~600-800 lines → ~200-300 lines (60% reduction)
- **editor_dock.py:** ~500-700 lines → ~200-300 lines (60% reduction)

**Qualitative Improvements:**
- **Reusability:** `FileFilterPanel` used in file_list_dock AND file_explorer_dock
- **Testability:** Each widget can be tested independently (unit tests easier)
- **Maintainability:** Fix widget bug once → all users benefit
- **Clarity:** Smaller classes with focused responsibilities

**Refactoring Pattern Applied:**
```
Phase 1: Identify monolithic code
↓
Phase 2: Extract UI logic to widgets
↓
Phase 3: Extract business logic to managers
↓
Phase 4: Dock becomes coordinator only
```

### 2. Widget Design Principles

**Principle 1: Single Responsibility**
- Each widget has ONE job
- `FileSelectionWidget`: Select files (not process them)
- `OperationOptionsWidget`: Configure options (not execute operations)
- `PresetManager`: Manage presets (not understand filter structure)

**Principle 2: Signal-Based Communication**
- Widgets emit signals when state changes
- Docks connect to signals and react
- Loose coupling → easy to replace/refactor

**Principle 3: Callback-Based Adaptation**
- `PresetManager` uses callbacks → adapts to any filter structure
- `FileListTableManager` uses main_window reference → adapts to any dock

**Principle 4: i18n from Day 1**
- All user-facing strings use `tr()` function
- Tooltips use `tooltip_tr()` function
- No hardcoded English strings

**Principle 5: Accessibility**
- All interactive widgets have accessible names/descriptions
- `AccessibilityManager.set_accessible_widget()` used consistently

### 3. State Management Patterns

**Pattern 1: Modified State Tracking (EditorTab)**
```python
# Track modified state:
self.is_modified = False

# Emit signal when state changes:
if not self.is_modified:
    self.is_modified = True
    self.modified_changed.emit(True)

# Reset on save:
self.is_modified = False
self.modified_changed.emit(False)
```

**Pattern 2: Mode Switching (FileSelectionWidget)**
```python
# Two-file mode vs multi-file mode:
if self.chk_multiple.isChecked():
    # Show multi-file UI
    self.list_files.setVisible(True)
    # Populate from File A/B
    if self.ed_file_a.text():
        self.list_files.addItem(self.ed_file_a.text())
```

**Pattern 3: Enable/Disable Cascading (FileFilterPanel)**
```python
# Extension filter checkbox controls field:
self.chk_use_ext_filter.toggled.connect(
    self.ed_extensions.setEnabled
)
```

### 4. Performance Considerations

**Optimization 1: Lazy Highlighting (SyntaxHighlighter)**
- Highlights per block, not entire document
- Uses `globalMatch()` for efficient regex matching
- Rules compiled once in `_setup_rules()`

**Optimization 2: Quick Filter (FileListTableManager)**
- Filters visible rows only, not data
- Uses `setRowHidden()` instead of rebuilding table
- Case-insensitive search via `.lower()`

**Optimization 3: Auto-Save Debouncing (EditorTab)**
- 3-second timer prevents excessive saves
- Timer restarts on each keystroke
- Only saves if modified and file-backed

### 5. Error Handling Patterns

**Pattern 1: Try/Catch with User Feedback**
```python
try:
    with open(file_path, 'w') as f:
        f.write(content)
except Exception as e:
    QMessageBox.critical(self, "Error", f"Failed: {e}")
    return False
return True
```

**Pattern 2: Validation Before Action**
```python
def save_preset(self):
    if not self._get_filters_callback:
        QMessageBox.warning(self, "Error", "Callback not set")
        return
    # ... proceed
```

**Pattern 3: Confirmation Dialogs for Destructive Actions**
```python
reply = QMessageBox.question(
    self, "Delete Preset?", "Are you sure?",
    QMessageBox.Yes | QMessageBox.No
)
if reply == QMessageBox.No:
    return
# ... proceed with deletion
```

---

## 📊 Widget Complexity Analysis

| Widget | Lines | Complexity | Reusability | Critical Code | Testing Priority |
|--------|-------|------------|-------------|---------------|------------------|
| `path_entry.py` | 76 | Low | High | None | Low |
| `collapsible_section.py` | 182 | Medium | High | Animation logic | Medium |
| `json_tree_widget.py` | 169 | Medium | Medium | Recursive tree build | Medium |
| `syntax_highlighter.py` | 186 | High | High | Regex rules | High |
| `file_selection_widget.py` | 280 | Medium | High | Mode switching | Medium |
| `operation_options_widget.py` | 320 | Low | Medium | None | Low |
| `preset_manager.py` | 320 | High | High | Callback architecture | High |
| `file_filter_panel.py` | 392 | High | High | Size conversion, regex validation | High |
| `editor_tab.py` | 398 | High | High | State management, auto-save | High |
| `search_widgets.py` | 476 | Medium | High | None | Medium |
| `file_list_table_manager.py` | 518 | High | Medium | Platform detection, CSV export | High |

**Complexity Factors:**
- State management (EditorTab)
- Callback architecture (PresetManager)
- Platform-specific code (FileListTableManager)
- Regex pattern complexity (SyntaxHighlighter, FileFilterPanel)
- Size conversion logic (FileFilterPanel)
- Animation logic (CollapsibleSection)

---

## 🔗 Dependencies

### External Dependencies (Qt)
- `PySide6.QtWidgets`: All widgets inherit from QWidget
- `PySide6.QtCore`: Signals, QTimer, QSettings, QDate, QRegularExpression
- `PySide6.QtGui`: QFont, QColor, QSyntaxHighlighter, QAction

### Internal Dependencies
- `src.i18n.translator`: `tr()`, `tooltip_tr()` for internationalization
- `src.accessibility_manager`: `AccessibilityManager.set_accessible_widget()`
- `src.gui.widgets.syntax_highlighter`: Used by `editor_tab.py`

### No Dependencies
- Widgets are self-contained
- No cross-widget dependencies (good design!)
- Docks depend on widgets, not vice versa

---

## 📝 Lessons Learned

### 1. Component Extraction Benefits

**Before:** Monolithic docks (800+ lines)
- Hard to understand
- Code duplication
- Hard to test
- Hard to reuse

**After:** Extracted widgets (100-500 lines each)
- Easy to understand
- DRY principle
- Easy to test
- High reusability

**Key Takeaway:** Component extraction is worth the effort

### 2. Callback Architecture for Flexibility

**PresetManager Example:**
- Preset manager doesn't know filter structure
- Callbacks adapt to any dock's needs
- Easy to add new docks with preset support

**Key Takeaway:** Callbacks enable flexible, reusable components

### 3. State Pattern for Mode Switching

**EditorTab Example:**
- Edit-only mode changes behavior and appearance
- Visual indicators keep user informed
- State transition requires user confirmation

**Key Takeaway:** State Pattern clarifies mode-based behavior

### 4. Signal/Slot for Loose Coupling

**All Widgets:**
- Widgets emit signals when state changes
- Docks connect to signals and react
- Easy to refactor without breaking

**Key Takeaway:** Signal/Slot enables loose coupling

### 5. i18n from Day 1

**All Widgets:**
- All strings use `tr()` function
- Easy to add new languages
- No refactoring needed later

**Key Takeaway:** i18n is easier when planned from start

---

## 🎯 Next Steps

### Immediate (Session 16)
1. ✅ Study widgets module (Session 15 COMPLETE)
2. ⏳ Study progress system (4 files, ~450 lines)
3. ⏳ Study key panels (insert_panel, search_replace_panel, results_tree)

### Short-Term (Sessions 17-18)
4. Study key dialogs (preferences_dialog, plugin_manager_dialog)
5. Study remaining dialogs (20+ files)

### Medium-Term (Sessions 19-20)
6. Study workers (2 files, known pattern)
7. Study other support files (10 files)

### Long-Term (Phase 5)
8. Create comprehensive docs/NOTES.md with all findings
9. Update comprehension assessment
10. Request merge authorization

---

## 📈 Progress Tracking

**Phase 4 Progress:**
- **Widgets:** 12/12 files ✅ (Session 15 COMPLETE)
- **Progress System:** 0/4 files ⏳
- **Panels:** 0/10 files ⏳
- **Dialogs:** 0/24 files ⏳
- **Workers:** 0/2 files ⏳
- **Other:** 0/10 files ⏳

**Overall Progress:**
- **Files Studied:** 81/196 (41.3%)
- **Phase 1:** 12 files ✅
- **Phase 2:** 11 files ✅
- **Phase 3:** 46 files ✅
- **Phase 4:** 12/66 files (18.2%)

**Estimated Time Remaining:**
- Phase 4: ~4-5 hours (54 files left)
- Tests: ~1 hour
- Git history: ~30 min
- NOTES.md: ~1 hour
- **Total:** ~6-7 hours to 100%

---

## ✅ Session 15 Complete!

**Achievement:** ✅ **Widgets Module 100% Studied!**

**Key Discoveries:**
1. Component extraction refactoring successfully DRYed code
2. 12 widgets enable high reusability across docks
3. Callback architecture (PresetManager) enables flexible adaptation
4. State Pattern (EditorTab) clarifies mode-based behavior
5. 8 design patterns identified across widgets

**Files Studied:** 12 files (3,358 lines)  
**Cumulative Total:** 81 files (41.3% of codebase)

**Next Session:** Progress system (4 files, ~450 lines)

---

**Programmer #7 | Session 15 | 2026-01-23**
