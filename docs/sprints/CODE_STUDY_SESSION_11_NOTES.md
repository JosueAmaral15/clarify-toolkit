# Code Study Session 11 Notes
**Programmer #7** | **Date**: 2026-01-22 | **Phase 3: Feature Modules (GUI Docks - Part 1/3)**

## Session Overview
**Module**: GUI Docks (Base Architecture & Selected Docks)  
**Files Analyzed**: 4 files in detail (~1,384 lines)  
**Total Dock Files**: 21 files (~13,291 lines)  
**Focus**: Base dock architecture, mixin pattern, factory pattern, representative dock implementations

---

## Files Analyzed

### 1. `src/gui/base_dock.py` (596 lines)
**Purpose**: Foundation for all tool docks with reusable components

#### Core Classes

**1. BaseDock (QDockWidget)** - Template Method Pattern
```python
class BaseDock(QDockWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self._setup_ui()        # Override in subclasses
        self._connect_signals()  # Override in subclasses
```

**Provided Methods**:
- `show_error(title, message)` - QMessageBox.critical
- `show_info(title, message)` - QMessageBox.information
- `show_warning(title, message)` - QMessageBox.warning

**Design Pattern**: Template Method (define skeleton, subclasses fill in details)

---

**2. FileInputMixin** - Reusable file/directory input widgets
```python
create_file_input(label_text, placeholder, with_is_file_checkbox=True) 
    → (label, line_edit, browse_button, is_file_checkbox)

create_extension_filter(default_extensions=".py,.js,.tsx")
    → (label, line_edit)

browse_file_or_directory(line_edit, is_file, file_filter)
```

**Key Feature**: `parse_extensions_to_globs(extensions_text)` (v2.9.0)
```python
>>> parse_extensions_to_globs(".py,.js")
['*.py', '*.js']
>>> parse_extensions_to_globs("py,js,tsx")  # Auto-adds '.'
['*.py', '*.js', '*.tsx']
```
- Handles comma/semicolon separators
- Auto-adds '.' prefix if missing
- Converts to glob patterns (`*.ext`)

---

**3. ProcessorWorkerBase (QThread)** - Background processing base class
```python
class ProcessorWorkerBase(QThread):
    progress = Signal(str)      # Progress messages
    finished_ok = Signal(object)  # Result data
    failed = Signal(str)        # Error messages
    
    def request_interrupt(self):
        self.interrupt_requested = True
    
    def check_interrupt(self) -> bool:
        return self.interrupt_requested
```

**Pattern**: Worker thread with interrupt support
- Subclasses override `run()` method
- Emit progress updates during processing
- Check `check_interrupt()` regularly for cancellation
- Emit `finished_ok` or `failed` when done

---

**4. ResultsOutputMixin** - Results panel with search & editor integration
```python
create_results_panel(label_text) 
    → (label, text_edit)

Features:
- Ctrl+F search shortcut
- Context menu with "Open in Editor" (v2.9.19 Task #6)
- append_result(text_edit, message)
- clear_results(text_edit)
```

**"Open in Editor" Feature** (v2.9.19 - Task #6):
```python
_open_results_in_editor(text_edit):
    1. Get results content
    2. Auto-detect extension (_detect_content_extension)
    3. Create temp file with appropriate extension
    4. Get EditorDock from main window
    5. Open in edit-only mode (sandbox)
```

**Auto-Detection Logic**:
- JSON: Starts with `{` or `[`, valid JSON parse
- HTML: Starts with `<`, contains `<html`, `<div`, `<span`, `<body>`
- XML: Starts with `<`, not HTML
- TypeScript/JS: Contains `const `, `let `, `function `, ` => `
- Python: Contains `def `, `import `, `class `, `from `
- Default: `.txt`

**Integration**: Finds EditorDock via parent traversal, opens temp file in edit-only mode (sandbox prevents accidental save to source files)

---

**5. ActionButtonsMixin** - Button creation helper
```python
create_action_buttons(buttons: List[tuple])
    → QHBoxLayout

Example:
buttons = [
    ("Convert", self._convert),
    ("Interrupt", self._interrupt),
    ("Clear", self._clear)
]
btn_layout = self.create_action_buttons(buttons)
```

**Auto-naming**: Stores button references as `self.btn_<text>` (e.g., `self.btn_convert`)

---

**6. OptionsGroupMixin** - Checkbox & spinbox creation
```python
create_checkbox_group(options: List[tuple])
    → List[QCheckBox]

create_spinbox_input(label_text, min_val, max_val, default, step)
    → (label, spinbox)
```

---

**7. ValidationMixin** - Input validation helpers
```python
validate_file_path(path, must_exist=True) 
    → (is_valid, error_message)

validate_not_empty(text, field_name) 
    → (is_valid, error_message)

validate_file_writable(path) 
    → (is_valid, error_message)
```

**Auto-directory creation**: `validate_file_writable()` creates missing parent directories with `os.makedirs(exist_ok=True)`

---

**8. StandardToolDock** - All-in-one convenience class
```python
class StandardToolDock(
    BaseDock,
    FileInputMixin,
    ResultsOutputMixin,
    ActionButtonsMixin,
    OptionsGroupMixin,
    ValidationMixin
):
    """Standard tool dock with all common mixins."""
    
    def _setup_enter_key_execution(self, *line_edits):
        """Setup Enter key to trigger _execute_action."""
        for line_edit in line_edits:
            line_edit.returnPressed.connect(self._execute_action)
    
    def _execute_action(self):
        """Override to define action triggered by Enter key."""
        pass
```

**Pattern**: Multiple inheritance mixin composition
**Benefit**: One class inherits all functionality, no need to cherry-pick mixins

---

### 2. `src/gui/dock_factory.py` (252 lines)
**Purpose**: Factory pattern for dock creation (refactored from MainWindow v2.9.114)

#### DockFactory Class

**Static Methods**:

**1. create_dock()** - Standard dock creation
```python
DockFactory.create_dock(
    main_window, dock_class, dock_attr_name,
    area=Qt.RightDockWidgetArea,
    hide=True,
    signal_connections=None,
    **dock_kwargs
) → dock_instance

Example:
dock = DockFactory.create_dock(
    self, JsonTranslateDock, 'dock_translate',
    area=Qt.RightDockWidgetArea,
    signal_connections={'translationComplete': self.on_translation_done}
)
```

**Steps**:
1. Instantiate dock class with kwargs
2. Store in `main_window.{dock_attr_name}`
3. Add to main window dock area
4. Connect signals (if provided)
5. Hide initially (if `hide=True`)

**2. create_dock_lazy()** - Lazy initialization
```python
DockFactory.create_dock_lazy(
    main_window, dock_class, dock_attr_name,
    area=Qt.RightDockWidgetArea,
    **dock_kwargs
)
```

**Pattern**: Create dock only if it doesn't exist yet
- Checks `hasattr(main_window, dock_attr_name)`
- If exists, returns existing instance
- Otherwise, calls `create_dock()`

**Benefit**: Deferred creation until first access (faster startup)

---

**Refactoring Context** (v2.9.114 - Phase 3.3):
- **Before**: 95 lines of dock creation methods in MainWindow (lines 1266-1360)
- **After**: Centralized in DockFactory
- **Benefit**: Reduced duplication, easier to manage dock configurations

---

### 3. `src/gui/case_converter_dock.py` (260 lines)
**Purpose**: Convert text case styles (camelCase, PascalCase, snake_case, kebab-case)

#### Architecture

**Worker Thread**:
```python
class CaseConverterWorker(ProcessorWorkerBase):
    def __init__(self, files, target_style, source_style=None):
        self.files = files
        self.target_style = target_style
        self.source_style = source_style
    
    def run(self):
        for i, file_path in enumerate(self.files):
            if self.check_interrupt():
                break
            
            self.emit_progress(f"[{i+1}/{total}] Processing {basename}...")
            convert_file(file_path, file_path, self.target_style, output_format='js')
            self.emit_progress(f"✓ Converted {basename}")
        
        self.emit_success(results)
```

**Dock UI**:
```python
class CaseConverterDock(StandardToolDock):
    def _setup_ui(self):
        # Source case style combo (Auto, camelCase, PascalCase, snake_case, kebab-case)
        # Target case style combo (camelCase, PascalCase, snake_case, kebab-case)
        # File/directory input with browse button
        # Extension filter (.py,.js,.tsx by default)
        # Action buttons (Convert, Interrupt, Clear)
        # Results panel with "Open in Editor"
```

**Style Mapping**:
```python
style_map = {
    "camelCase": "camel",
    "PascalCase": "pascal",
    "snake_case": "snake",
    "kebab-case": "kebab"
}
```

**Features**:
- Auto-detect source case style (or specify manually)
- Recursive directory processing with extension filter
- Progress updates during conversion
- Interrupt with Escape key (v2.9.50.1)
- Enter key triggers conversion (`_setup_enter_key_execution`)
- Estimated word count (heuristic: count of ':' in objects)

---

### 4. `src/gui/history_dock.py` (278 lines)
**Purpose**: Operation history viewer (recent 10 operations)

#### Features

**Tracked Operations**:
- Search: query, files searched, matches found
- Replace: query, replacement, files modified
- Insert: text, mode, files modified
- JSON Translate: dictionary file, files processed
- JSON Rewriter: input file, transformations applied

**Data Structure**:
```python
entry = {
    "timestamp": "2026-01-22 20:30:15",
    "operation": "Search",
    "details": {
        "query": "searchterm",
        "files_processed": 42,
        "matches_found": 156
    }
}
```

**UI Components**:
- QTreeWidget with 4 columns (Timestamp, Operation, Details, Files)
- Clear, Export, Refresh buttons
- FIFO queue (max 10 entries, configurable)
- Alternating row colors for readability

**Display Optimizations** (v2.9.117):
```python
# Prevent horizontal expansion from long details
self.tree_history.setWordWrap(False)
self.tree_history.setTextElideMode(Qt.TextElideMode.ElideRight)
header.setSectionResizeMode(2, header.ResizeMode.Stretch)  # Details column

# Truncate long details
if len(details_str) > 100:
    details_display = details_str[:100] + "..."
    item.setToolTip(2, details_str)  # Full details in tooltip
```

**Export Feature**:
```python
def _export_history(self):
    # Export to text file with:
    # - Header banner
    # - Each operation with timestamp, type, all details
    # - Separator lines
    
    Format:
    ================================================================================
    CLARIFY OPERATION HISTORY
    ================================================================================
    
    Timestamp: 2026-01-22 20:30:15
    Operation: Search
    Query: searchterm
    Files Processed: 42
    Matches Found: 156
    --------------------------------------------------------------------------------
```

**Signal**: `history_cleared = Signal()` - Emitted when user clears history

---

## Design Patterns Identified

### 1. **Template Method Pattern** (BaseDock)
```python
class BaseDock(QDockWidget):
    def __init__(self, title, parent):
        # Common setup
        self._setup_ui()        # Subclass implements
        self._connect_signals()  # Subclass implements
```
- **Purpose**: Define skeleton algorithm, subclasses fill in steps
- **Usage**: All 21 docks inherit BaseDock

### 2. **Mixin Pattern** (7 mixins)
```python
class StandardToolDock(
    BaseDock,
    FileInputMixin,
    ResultsOutputMixin,
    ActionButtonsMixin,
    OptionsGroupMixin,
    ValidationMixin
):
```
- **Purpose**: Compose functionality from multiple sources
- **Benefit**: Reusable components, avoid duplication
- **Usage**: Most docks inherit StandardToolDock

### 3. **Factory Pattern** (DockFactory)
```python
DockFactory.create_dock(main_window, JsonTranslateDock, 'dock_translate')
```
- **Purpose**: Centralize object creation logic
- **Benefit**: Consistent creation, easier to manage configurations
- **Refactored**: v2.9.114 (from 95 lines in MainWindow)

### 4. **Worker Thread Pattern** (ProcessorWorkerBase)
```python
class MyWorker(ProcessorWorkerBase):
    def run(self):
        for item in items:
            if self.check_interrupt():
                break
            process(item)
            self.emit_progress(message)
        self.emit_success(result)
```
- **Purpose**: Offload heavy processing to background thread
- **Benefit**: Keep UI responsive during long operations
- **Pattern**: Qt Signal/Slot communication with main thread

### 5. **Observer Pattern** (Qt Signals)
```python
worker.progress.connect(lambda msg: self.append_result(text_edit, msg))
worker.finished_ok.connect(self._on_finished)
worker.failed.connect(self._on_failed)
```
- **Purpose**: Decouple worker from UI updates
- **Implementation**: Qt's Signal/Slot mechanism

### 6. **Strategy Pattern** (Case style conversion)
```python
style_map = {"camelCase": "camel", "PascalCase": "pascal", ...}
convert_file(file_path, file_path, target_style, output_format='js')
```
- **Purpose**: Select algorithm at runtime
- **Usage**: User selects case style from combo box

### 7. **Facade Pattern** (StandardToolDock)
```python
class StandardToolDock(BaseDock, FileInputMixin, ...):
    """Simplified interface to all common mixins."""
```
- **Purpose**: Provide simple interface to complex subsystem (6 mixins)
- **Benefit**: One class import instead of 6

---

## Dock Architecture Summary

### Inheritance Hierarchy
```
QDockWidget (Qt base class)
    ↓
BaseDock (common methods: show_error, show_info, show_warning)
    ↓
StandardToolDock (all mixins combined)
    ↓
CaseConverterDock, HistoryDock, etc. (21 specialized docks)
```

### Mixin Composition
```
StandardToolDock = BaseDock
                 + FileInputMixin (file browsing, extension filters)
                 + ResultsOutputMixin (results panel, search, open in editor)
                 + ActionButtonsMixin (button creation)
                 + OptionsGroupMixin (checkboxes, spinboxes)
                 + ValidationMixin (input validation)
```

### Common Dock Lifecycle
1. **Creation** (DockFactory):
   - Instantiate dock class
   - Store in MainWindow attribute
   - Add to dock area (Left/Right/Top/Bottom)
   - Connect signals
   - Hide initially (show on demand)

2. **UI Setup** (_setup_ui):
   - Create widgets (labels, line edits, buttons, etc.)
   - Arrange in layouts (QVBoxLayout, QHBoxLayout, QGridLayout)
   - Apply tooltips (tooltip_tr for i18n)

3. **Signal Connection** (_connect_signals):
   - Connect button clicks to handlers
   - Setup Enter key shortcuts
   - Setup Escape key for interrupt

4. **Processing**:
   - Validate inputs
   - Create worker thread (ProcessorWorkerBase subclass)
   - Connect signals (progress, finished_ok, failed)
   - Start worker
   - Disable/enable buttons during processing
   - Display progress in results panel

5. **Results Display**:
   - Append messages to QTextEdit
   - Show success/error dialog
   - "Open in Editor" for results inspection

---

## Key Discoveries

### 1. **Mixin-Based Architecture**
- **7 mixins** provide reusable components
- **StandardToolDock** combines all mixins (one-stop inheritance)
- **Benefit**: Massive code reuse across 21 docks

### 2. **"Open in Editor" Feature** (v2.9.19 - Task #6)
- **Auto-detection**: Smart extension detection from content
- **Sandbox mode**: edit-only, prevents accidental save to source
- **Integration**: Context menu + button, finds EditorDock via parent traversal
- **Temp files**: Creates temp file with appropriate extension

### 3. **Background Processing Pattern**
- **All heavy operations**: Use worker threads (ProcessorWorkerBase)
- **Interrupt support**: Check `interrupt_requested` flag regularly
- **UI responsiveness**: Qt Signal/Slot communication keeps UI smooth

### 4. **Extension Filter** (v2.9.0)
- **Smart parsing**: Handles `.py,.js` or `py,js` (auto-adds dot)
- **Multiple separators**: Comma or semicolon
- **Glob conversion**: `.py` → `*.py`

### 5. **History Tracking**
- **10 operations** tracked (configurable)
- **FIFO queue**: Oldest dropped when limit reached
- **Export**: Text file export with full details
- **Truncation**: Long details truncated in UI (full in tooltip)

### 6. **Enter Key Execution**
- **Pattern**: `_setup_enter_key_execution(*line_edits)`
- **Benefit**: User can press Enter in any input field to trigger main action
- **Standard**: Most docks implement `_execute_action()` for this

### 7. **Escape Key Interrupt** (v2.9.50.1)
- **CaseConverterDock**: Escape key interrupts processing
- **Pattern**: QShortcut connected to `_interrupt()` method
- **UX**: Quick cancellation without mouse click

---

## Integration Points

### 1. MainWindow Integration
```python
# In MainWindow.__init__
self.dock_case_converter = DockFactory.create_dock(
    self, CaseConverterDock, 'dock_case_converter',
    area=Qt.RightDockWidgetArea
)

# History dock tracks operations
self.history_dock.add_operation("Search", {
    "query": "searchterm",
    "files_processed": 42,
    "matches_found": 156
})
```

### 2. i18n Integration
```python
from src.i18n.translator import tr, tooltip_tr

self.btn_convert.setText(tr("case_converter.btn_convert"))
self.btn_convert.setToolTip(tooltip_tr("case.btn_convert"))
```

### 3. EditorDock Integration
```python
# ResultsOutputMixin._open_results_in_editor()
editor_dock = parent.findChild(EditorDock)
editor_dock.open_file_path(temp_path, edit_only=True)
```

### 4. Core Module Integration
```python
# CaseConverterDock → src.case_converter
from src.case_converter import convert_file, convert_string
convert_file(file_path, file_path, target_style, output_format='js')
```

---

## Complete Dock Inventory

**21 Total Docks** (~13,291 lines):

1. **base_dock.py** (596 lines) - Foundation, mixins ✅
2. **dock_factory.py** (252 lines) - Factory pattern ✅
3. **case_converter_dock.py** (260 lines) - Case style conversion ✅
4. **history_dock.py** (278 lines) - Operation history ✅
5. **placeholder_replacer_dock.py** (291 lines) - Placeholder replacement
6. **file_list_dock.py** (293 lines) - File list management
7. **tutorials_dock.py** (473 lines) - Tutorial system
8. **google_translate_dock.py** (518 lines) - Google Translate API
9. **formula_dock.py** (530 lines) - Formula calculator
10. **jsx_extractor_dock.py** (568 lines) - JSX extraction
11. **text_extractor_dock.py** (577 lines) - Text extraction
12. **editor_dock.py** (583 lines) - Code editor
13. **text_to_json_dock.py** (584 lines) - Text to JSON conversion
14. **json_translate_dock.py** (592 lines) - JSON translation
15. **advanced_extractor_dock.py** (601 lines) - Advanced extraction
16. **calculator_dock.py** (601 lines) - Calculator
17. **json_search_dock.py** (647 lines) - JSON search
18. **set_operations_dock.py** (734 lines) - Set operations (∩, ∪, −, ⊕)
19. **json_rewriter_dock.py** (1,054 lines) - JSON rewriter
20. **ai_processor_dock.py** (1,193 lines) - AI processor
21. **file_explorer_dock.py** (2,066 lines) - File explorer (largest!)

**Studied**: 4/21 (base_dock, dock_factory, case_converter, history)
**Remaining**: 17 docks

---

## Critical Code Sections

### ⚠️ **DON'T TOUCH**: Mixin Multiple Inheritance Order
```python
class StandardToolDock(
    BaseDock,
    FileInputMixin,
    ResultsOutputMixin,
    ActionButtonsMixin,
    OptionsGroupMixin,
    ValidationMixin
):
```
- **Why critical**: Method Resolution Order (MRO) matters
- **Breaking change**: Changing order could break method lookup
- **Best practice**: BaseDock first, mixins after

### ⚠️ **DON'T TOUCH**: Worker Interrupt Check Pattern
```python
for item in items:
    if self.check_interrupt():
        self.emit_progress("⚠️ Processing interrupted")
        break
    process(item)
```
- **Why critical**: Without regular checks, interrupt doesn't work
- **Pattern**: Check at top of every loop iteration
- **UX**: Escape key interrupts immediately

### ⚠️ **DON'T TOUCH**: Extension Parsing Regex
```python
extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
```
- **Why critical**: Supports both comma and semicolon separators
- **Robustness**: Handles trailing commas, spaces
- **Breaking change**: Simple `split(',')` breaks semicolon input

### ⚠️ **DON'T TOUCH**: Content Extension Detection
```python
def _detect_content_extension(self, content: str) -> str:
    # JSON: starts with '{' or '[', valid parse
    # HTML: starts with '<', contains html tags
    # TS/JS: contains 'const ', 'let ', 'function ', ' => '
    # Python: contains 'def ', 'import ', 'class '
    # Default: '.txt'
```
- **Why critical**: Order matters (HTML before XML, JSON before TS)
- **Heuristics**: Tested patterns work for most cases
- **Breaking change**: Wrong extension causes syntax highlighting issues

---

## Performance Characteristics

### Background Processing
- **Pattern**: All heavy operations use QThread workers
- **Benefit**: UI stays responsive during multi-file processing
- **Signal overhead**: Minimal (Qt's meta-object system is optimized)

### History Dock
- **Memory**: O(10) entries × ~500 bytes = ~5 KB (negligible)
- **Display**: O(10) tree items (instant refresh)
- **Export**: O(10) × 100 bytes = ~1 KB file

### Extension Parsing
- **Time**: O(n) where n = characters in extension string (~50ms for 1000 chars)
- **Typical**: `.py,.js,.tsx` → ~1ms

---

## Testing Observations

### Edge Cases Handled

1. **Empty input paths**: Validation catches before processing
2. **Non-existent paths**: `validate_file_path()` checks existence
3. **No matching files**: Returns error before worker creation
4. **Interrupt during processing**: Gracefully stops at next check
5. **Long detail strings**: Truncated in UI, full in tooltip
6. **Missing editor dock**: Shows warning, cleans up temp file

### Error Handling
```python
try:
    files = self._get_files()
    # Start worker
except Exception as e:
    self.show_error("Error", str(e))
```
- **Pattern**: Validate inputs in try/except, show QMessageBox on error
- **User experience**: Clear error messages, no crashes

---

## Reuse Opportunities

1. **Mixin pattern**: Can be extracted to standalone UI library
2. **Worker pattern**: Reusable template for any background processing
3. **Extension parsing**: Standalone utility function
4. **Content detection**: Useful for any file type detection
5. **Factory pattern**: Template for other object creation scenarios

---

## Don't Touch Zones

1. **Mixin inheritance order** (line 563-570): MRO-sensitive
2. **Worker interrupt pattern**: Regular `check_interrupt()` calls essential
3. **Extension parsing regex** (line 42): Handles multiple separators
4. **Content extension detection** (lines 348-384): Order-dependent heuristics
5. **Signal/Slot connections**: Qt meta-object system requires exact matching

---

## Questions Answered

### Q: How do docks inherit common functionality?
**A**: Mixin pattern + StandardToolDock convenience class. 7 mixins provide reusable components (FileInputMixin, ResultsOutputMixin, etc.), StandardToolDock combines all mixins in one class for easy inheritance.

### Q: How does "Open in Editor" work?
**A**: ResultsOutputMixin creates temp file with auto-detected extension, finds EditorDock via parent traversal, opens in edit-only mode (sandbox prevents accidental save).

### Q: How do long operations keep UI responsive?
**A**: Worker thread pattern (ProcessorWorkerBase). Heavy processing runs in QThread, emits signals for progress updates, main thread updates UI via Qt Signal/Slot mechanism.

### Q: How does DockFactory reduce duplication?
**A**: Centralizes dock creation (instantiate, store attribute, add to main window, connect signals, hide). Refactored from 95 lines in MainWindow (v2.9.114).

### Q: How does history tracking work?
**A**: FIFO queue (max 10 entries). HistoryDock.add_operation() inserts at front, drops oldest if over limit. QTreeWidget displays with 4 columns (Timestamp, Operation, Details, Files).

---

## Phase 3 Progress Update

**Module**: GUI Docks (Part 1/3)  
**Status**: 🔄 **IN PROGRESS**  
**Files**: 4/21 (19%)  
**Lines**: ~1,384/13,291 (10.4%)

**Studied Docks**:
- ✅ base_dock.py (596 lines) - Foundation
- ✅ dock_factory.py (252 lines) - Factory
- ✅ case_converter_dock.py (260 lines) - Example dock
- ✅ history_dock.py (278 lines) - Tracking system

**Remaining**: 17 docks (~11,907 lines)

**Phase 3 Overall**:
- ✅ Utils (9 files, ~2,304 lines)
- ✅ Rewriter (9 files, ~2,297 lines)
- ✅ AI Processor (5 files, ~1,061 lines)
- ✅ i18n (2 files, ~292 lines)
- 🔄 GUI docks (4/21 files, ~1,384/13,291 lines)

**Total Phase 3 Progress**: 29/~73 files (40%)

---

**Next Session**: Continue GUI docks (medium-sized: editor, json_search, set_operations, json_translate)

**Study Time This Session**: ~30 minutes  
**Cumulative Study Time**: ~5 hours
