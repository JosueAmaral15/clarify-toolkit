# Session 2: BRANCH - GUI Architecture

**Date:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Session Type:** SCAN Reading (Structure + Key Patterns)  
**Time Investment:** 2 hours  
**Protocol:** SIMPLICITY_PROTOCOL_3.md Step 1.3  
**Methodology:** Import Tree Analogy - BRANCH Layer (Coordinators)

---

## Executive Summary

**Mission:** Understand how GUI components are organized, created, and communicate  
**Files Analyzed:** 86 Python files (~1.2MB of code)  
**Key Discovery:** 3-layer modular architecture (Base → Factory → Concrete Docks) with mixin pattern  
**Architecture Pattern:** Factory + Inheritance + Signal/Slot communication

---

## Files Distribution

| Category | Location | Files | Size | Purpose |
|----------|----------|-------|------|---------|
| **Base Classes** | `src/gui/` | 3 | ~35KB | BaseDock, Mixins, Factory |
| **Concrete Docks** | `src/gui/` | 30+ | ~600KB | Tool implementations |
| **Panels** | `src/gui/panels/` | 9 | 456KB | Search/Replace/Insert UI |
| **Widgets** | `src/gui/widgets/` | 9 | 356KB | Reusable components |
| **Progress** | `src/gui/progress/` | 4 | 76KB | Progress tracking |
| **Dialogs** | `src/gui/dialogs/` | 2 | 36KB | Popup dialogs |
| **Workers** | `src/gui/workers/` | 2 | ~30KB | Background threads |
| **Builders** | `src/gui/` | 3 | ~50KB | Menu, UI, Window builders |

**Total:** 86 files, ~1.6MB code

---

## GUI Architecture: 3-Layer Modular System

### Layer 1: Base Classes & Mixins (Foundation)

```
┌──────────────────────────────────────────────────────────┐
│                   BaseDock (QDockWidget)                 │
│  • Common dock functionality                             │
│  • Error/info/warning dialogs                            │
│  • Lifecycle methods (_setup_ui, _connect_signals)       │
└──────────────────────────────────────────────────────────┘
                          ↑
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ FileInput    │  │ ResultsOutput│  │ ActionButtons│
│ Mixin        │  │ Mixin        │  │ Mixin        │
│              │  │              │  │              │
│ • Browse btn │  │ • Results    │  │ • Process btn│
│ • File/dir   │  │ • Output box │  │ • Clear btn  │
│ • Extension  │  │              │  │              │
│   filter     │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐
│ OptionsGroup │  │ Validation   │
│ Mixin        │  │ Mixin        │
│              │  │              │
│ • Options    │  │ • Input      │
│ • Checkboxes │  │   validation │
│ • Combos     │  │ • Error msgs │
└──────────────┘  └──────────────┘
```

**File:** `src/gui/base_dock.py` (19,084 bytes)

**Key Classes:**

1. **BaseDock(QDockWidget)**
   ```python
   class BaseDock(QDockWidget):
       """Base class for all tool docks with common functionality."""
       
       def __init__(self, title: str, parent=None):
           super().__init__(title, parent)
           self.main_widget = QWidget()
           self.setWidget(self.main_widget)
           self.layout = QVBoxLayout(self.main_widget)
           self._setup_ui()          # Override in subclass
           self._connect_signals()   # Override in subclass
   ```

2. **FileInputMixin**
   - `create_file_input()` → Returns (label, line_edit, browse_btn, is_file_chk)
   - `create_extension_filter()` → Returns (label, line_edit) with `.py,.js,.tsx` default
   - `browse_file_or_directory()` → Opens file/directory picker dialog

3. **ProcessorWorkerBase(QThread)**
   - Signals: `progress`, `finished_ok`, `finished_error`
   - Base class for background processing threads

**Analysis:**
- ✅ **Mixin Pattern:** Reusable UI components via composition
- ✅ **Template Method:** `_setup_ui()` and `_connect_signals()` hooks
- ✅ **Qt Threading:** Workers extend `QThread` for async operations
- 🎯 **Role in Import Tree:** BRANCH - Provides building blocks for LEAFs (concrete docks)

---

### Layer 2: Factory Pattern (Creation & Configuration)

**File:** `src/gui/dock_factory.py` (9,245 bytes)

```
┌─────────────────────────────────────────────────────────┐
│                    DockFactory                          │
│                                                         │
│  create_dock()                                          │
│    1. Instantiate dock_class(parent, **kwargs)         │
│    2. Store in main_window as dock_attr_name           │
│    3. Add to main window in specified area             │
│    4. Connect signals (if provided)                    │
│    5. Set initial visibility (hidden by default)       │
│                                                         │
│  create_dock_lazy()                                     │
│    • Only create if doesn't exist yet                  │
│    • For infrequently used docks (History, Tutorials)  │
│                                                         │
│  Convenience Methods (16 total):                       │
│    • create_json_translate_dock()                      │
│    • create_ai_processor_dock()                        │
│    • create_file_explorer_dock()                       │
│    • create_case_converter_dock()                      │
│    • ... (12 more)                                     │
└─────────────────────────────────────────────────────────┘
```

**Key Method:**
```python
@staticmethod
def create_dock(main_window: 'QMainWindow',
               dock_class,
               dock_attr_name: str,
               area: 'Qt.DockWidgetArea' = None,
               hide: bool = True,
               signal_connections: Optional[dict] = None,
               **dock_kwargs) -> 'QDockWidget':
    """
    Create and configure a dock widget.
    
    Example:
        dock = DockFactory.create_dock(
            self, JsonTranslateDock, 'dock_translate',
            area=Qt.RightDockWidgetArea,
            signal_connections={'finished': self._on_translate_done}
        )
    """
    # 1. Create instance
    dock = dock_class(parent=main_window, **dock_kwargs)
    
    # 2. Store reference
    setattr(main_window, dock_attr_name, dock)
    
    # 3. Add to window
    main_window.addDockWidget(area, dock)
    
    # 4. Connect signals
    if signal_connections:
        for signal_name, slot in signal_connections.items():
            getattr(dock, signal_name).connect(slot)
    
    # 5. Hide initially
    if hide:
        dock.hide()
    
    return dock
```

**Convenience Methods Pattern:**
```python
@staticmethod
def create_ai_processor_dock(main_window: 'QMainWindow') -> 'QDockWidget':
    """Create AI Processor dock."""
    from ..gui import AIProcessorDock
    return DockFactory.create_dock(
        main_window, AIProcessorDock, 'dock_ai_processor'
    )
```

**Analysis:**
- ✅ **Lazy Import:** Imports dock class only when creating (reduces startup time)
- ✅ **Consistent API:** All docks created the same way
- ✅ **Signal Connection:** Centralized signal wiring
- ✅ **Default Hidden:** User opens tools on demand
- 🎯 **Role:** BRANCH coordinator - Knows HOW to create docks, delegates WHAT they do

**16 Factory Methods:**
1. `create_json_translate_dock()`
2. `create_json_rewriter_dock()`
3. `create_text_extractor_dock()`
4. `create_placeholder_replacer_dock()`
5. `create_ai_processor_dock()`
6. `create_json_search_dock()`
7. `create_case_converter_dock()`
8. `create_jsx_extractor_dock()`
9. `create_text_to_json_dock()`
10. `create_file_list_dock()`
11. `create_file_explorer_dock()`
12. `create_history_dock()` ← Lazy
13. `create_tutorials_dock()` ← Lazy
14. `create_editor_dock()` ← Lazy
15. `create_google_translate_dock()`
16. `create_advanced_extractor_dock()`

---

### Layer 3: Concrete Dock Implementations (Features)

**Pattern:** Each tool is a self-contained dock widget

#### Example 1: Simple Dock (Case Converter - 260 lines)

**File:** `src/gui/case_converter_dock.py` (10,214 bytes)

```python
class CaseConverterDock(BaseDock):
    """
    Case converter tool dock.
    Converts text between camelCase, PascalCase, snake_case, kebab-case.
    """
    
    def __init__(self, parent=None):
        self.title = tr("dock.case_converter.title")
        super().__init__(self.title, parent)
    
    def _setup_ui(self):
        # Input section
        lbl_input = QLabel(tr("dock.case_converter.input"))
        self.txt_input = QTextEdit()
        
        # Output section
        lbl_output = QLabel(tr("dock.case_converter.output"))
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        
        # Options
        self.combo_from_case = QComboBox()
        self.combo_from_case.addItems(["Auto", "camelCase", "PascalCase", ...])
        
        self.combo_to_case = QComboBox()
        self.combo_to_case.addItems(["camelCase", "PascalCase", ...])
        
        # Button
        btn_convert = QPushButton(tr("dock.case_converter.convert"))
        btn_convert.clicked.connect(self._on_convert)
        
        # Layout assembly
        self.layout.addWidget(lbl_input)
        self.layout.addWidget(self.txt_input)
        self.layout.addWidget(self.combo_from_case)
        self.layout.addWidget(self.combo_to_case)
        self.layout.addWidget(btn_convert)
        self.layout.addWidget(lbl_output)
        self.layout.addWidget(self.txt_output)
    
    def _on_convert(self):
        # Get input
        text = self.txt_input.toPlainText()
        from_case = self.combo_from_case.currentText()
        to_case = self.combo_to_case.currentText()
        
        # Convert (delegates to src/case_converter.py)
        from src.case_converter import JSObjectCaseConverter
        converter = JSObjectCaseConverter()
        result = converter.convert(text, from_case, to_case)
        
        # Display result
        self.txt_output.setPlainText(result)
```

**Analysis:**
- ✅ **Self-Contained:** All UI and logic in one file
- ✅ **Follows Template:** `_setup_ui()` creates widgets, `_on_convert()` handles action
- ✅ **Delegates Business Logic:** Calls `src/case_converter.py` (separation of concerns)
- 🎯 **Role:** LEAF - Does specific task, no cross-imports to other docks

---

#### Example 2: Complex Dock (AI Processor - 1,193 lines)

**File:** `src/gui/ai_processor_dock.py` (51,476 bytes)

**Complexity:** 
- Multiple providers (OpenAI, Gemini)
- API key management
- File batch processing
- Progress tracking
- Worker thread for async API calls

```python
class AIProcessorDock(BaseDock, FileInputMixin):
    """
    AI processor tool using OpenAI or Gemini APIs.
    Processes files with custom prompts.
    """
    
    # Signals
    processing_started = Signal()
    processing_finished = Signal(dict)  # Results
    
    def __init__(self, parent=None):
        self.title = tr("dock.ai_processor.title")
        super().__init__(self.title, parent)
        self.worker = None  # Background worker thread
    
    def _setup_ui(self):
        # Provider selection
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["OpenAI", "Gemini"])
        
        # API key input (sensitive!)
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        
        # Model selection
        self.combo_model = QComboBox()
        # Populated dynamically based on provider
        
        # File input (uses FileInputMixin)
        lbl, self.txt_path, btn_browse, chk_file = self.create_file_input(
            tr("dock.ai_processor.path"),
            with_is_file_checkbox=True
        )
        btn_browse.clicked.connect(lambda: self.browse_file_or_directory(
            self.txt_path, chk_file.isChecked()
        ))
        
        # Extension filter (uses FileInputMixin)
        lbl_ext, self.txt_extensions = self.create_extension_filter(
            default_extensions=".py,.js,.tsx,.md"
        )
        
        # Prompt input
        lbl_prompt = QLabel(tr("dock.ai_processor.prompt"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlaceholderText(
            "Analyze this code and suggest improvements..."
        )
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        
        # Process button
        btn_process = QPushButton(tr("dock.ai_processor.process"))
        btn_process.clicked.connect(self._on_process)
        
        # Results output
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        
        # Layout assembly (50+ lines of layout code...)
    
    def _on_process(self):
        # Validation
        if not self.txt_api_key.text():
            self.show_error("Error", "API key required")
            return
        
        # Create worker thread
        self.worker = AIProcessorWorker(
            provider=self.combo_provider.currentText(),
            api_key=self.txt_api_key.text(),
            model=self.combo_model.currentText(),
            path=self.txt_path.text(),
            extensions=self.txt_extensions.text(),
            prompt=self.txt_prompt.toPlainText()
        )
        
        # Connect signals
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.finished_error.connect(self._on_error)
        
        # Start processing
        self.progress.setVisible(True)
        btn_process.setEnabled(False)
        self.worker.start()
    
    def _on_progress(self, message: str):
        # Update progress bar
        self.progress.setFormat(message)
    
    def _on_finished(self, results: dict):
        # Display results
        self.txt_results.setPlainText(json.dumps(results, indent=2))
        self.progress.setVisible(False)
        self.processing_finished.emit(results)


class AIProcessorWorker(ProcessorWorkerBase):
    """Background worker for AI processing."""
    
    def __init__(self, provider, api_key, model, path, extensions, prompt):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.path = path
        self.extensions = extensions
        self.prompt = prompt
    
    def run(self):
        try:
            # Import AI processor module
            from src.ai_processor import OpenAIClient, GeminiClient
            
            # Create client
            if self.provider == "OpenAI":
                client = OpenAIClient(self.api_key)
            else:
                client = GeminiClient(self.api_key)
            
            # Get files to process
            files = walk_files(self.path, include=self.extensions)
            total = len(files)
            
            results = []
            for i, file_path in enumerate(files):
                # Emit progress
                self.progress.emit(f"Processing {i+1}/{total}: {file_path}")
                
                # Process file
                text = read_text(file_path)
                response = client.process(text, self.prompt, self.model)
                results.append({
                    'file': file_path,
                    'response': response
                })
            
            # Emit success
            self.finished_ok.emit({'files_processed': total, 'results': results})
        
        except Exception as e:
            # Emit error
            self.finished_error.emit(str(e))
```

**Analysis:**
- ✅ **Worker Thread Pattern:** UI stays responsive during API calls
- ✅ **Signal/Slot Communication:** Worker → Dock via signals
- ✅ **Mixin Reuse:** `FileInputMixin` provides file selection UI
- ✅ **Sensitive Data:** Password input for API keys
- ✅ **Progress Tracking:** Real-time feedback to user
- 🎯 **Role:** LEAF executor with BRANCH coordination (manages worker thread)

---

#### Example 3: Mega Dock (File Explorer - 2,066 lines)

**File:** `src/gui/file_explorer_dock.py` (86,937 bytes!)

**Purpose:** Unified File List + Advanced Search (v2.9.115)

**Features:**
- File tree navigation
- Advanced search with regex
- File filtering (size, date, extension)
- Multi-file selection
- Context menu (open, delete, rename)
- Integration with main search panel

**Complexity Indicators:**
```python
class FileExplorerDock(BaseDock):
    # 32 signals defined!
    file_selected = Signal(str)
    files_selected = Signal(list)
    search_requested = Signal(dict)
    filter_changed = Signal(dict)
    # ... 28 more signals
    
    def __init__(self, parent=None):
        # 15+ instance variables
        self.file_tree = None
        self.search_panel = None
        self.filter_panel = None
        self.results_table = None
        self.worker_thread = None
        # ... 10 more
    
    def _setup_ui(self):
        # Creates 5 major UI sections:
        # 1. Toolbar (buttons for common actions)
        # 2. File tree (directory navigation)
        # 3. Search panel (advanced search options)
        # 4. Filter panel (file type, size, date filters)
        # 5. Results table (matches display)
```

**Analysis:**
- ⚠️ **High Complexity:** 2,066 lines in single file (refactoring candidate)
- ✅ **Feature Rich:** Combines multiple tools in one dock
- ✅ **Signal Heavy:** 32 signals for inter-component communication
- 🎯 **Role:** BRANCH coordinator (orchestrates tree, search, filter, results)

---

## Subdirectories: Specialized Components

### 1. Panels (`src/gui/panels/` - 456KB, 9 files)

**Purpose:** Main application panels (not dock widgets)

| File | Size | Purpose |
|------|------|---------|
| `search_replace_panel.py` | ~150KB | Main search/replace UI |
| `insert_panel.py` | ~80KB | Line insertion panel |
| `results_tree.py` | ~40KB | Search results tree widget |
| `search_worker.py` | ~35KB | Background search thread |
| `regex_insert_panel.py` | ~30KB | Regex insertion tool |
| `match_panel.py` | ~25KB | Match display widget |
| `file_explorer_worker.py` | ~20KB | File explorer thread |

**Key Pattern:**
```python
# panels/__init__.py exports
from .search_replace_panel import SearchReplacePanel
from .insert_panel import InsertPanel
from .results_tree import ResultsTree
from .search_worker import SearchWorker
from .match_panel import MatchPanel
```

**Analysis:**
- ✅ **Separation:** Panels are NOT docks (integrated into main window)
- ✅ **Worker Pattern:** Each panel has corresponding worker thread
- 🎯 **Role:** LEAF components (used by MainWindow, not docks)

---

### 2. Widgets (`src/gui/widgets/` - 356KB, 9 files)

**Purpose:** Reusable UI components

| File | Size | Purpose |
|------|------|---------|
| `json_tree_widget.py` | ~80KB | JSON hierarchy viewer |
| `file_filter_panel.py` | ~60KB | File filtering UI |
| `file_list_table_manager.py` | ~50KB | File list management |
| `collapsible_section.py` | ~40KB | Expandable UI sections |
| `file_selection_widget.py` | ~35KB | File picker widget |
| `syntax_highlighter.py` | ~30KB | Code syntax highlighting |
| `editor_tab.py` | ~25KB | Editor tab widget |
| `search_widgets.py` | ~20KB | Search UI components |
| `path_entry.py` | ~16KB | Path input with autocomplete |

**Example - Collapsible Section:**
```python
class CollapsibleSection(QWidget):
    """
    Expandable/collapsible section widget.
    Used in complex docks to organize options.
    """
    
    collapsed = Signal()
    expanded = Signal()
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.toggle_button = QPushButton(f"▶ {title}")
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        self.toggle_button.clicked.connect(self._on_toggle)
        self.content_area.setVisible(False)  # Collapsed by default
    
    def _on_toggle(self):
        visible = not self.content_area.isVisible()
        self.content_area.setVisible(visible)
        
        # Update arrow
        arrow = "▼" if visible else "▶"
        self.toggle_button.setText(f"{arrow} {self.title}")
        
        # Emit signal
        if visible:
            self.expanded.emit()
        else:
            self.collapsed.emit()
```

**Analysis:**
- ✅ **Reusable:** Used across multiple docks
- ✅ **Self-Contained:** Each widget is independent
- 🎯 **Role:** LEAF building blocks (lowest level UI components)

---

### 3. Progress (`src/gui/progress/` - 76KB, 4 files)

**Purpose:** Progress tracking infrastructure (v2.9.114 - Phase 1.1)

| File | Lines | Purpose |
|------|-------|---------|
| `progress_manager.py` | ~400 | Centralized progress tracking |
| `progress_bar_widget.py` | ~250 | Progress bar with cancel button |
| `progress_details_dialog.py` | ~200 | Detailed progress popup |
| `operation_history.py` | ~150 | Past operations log |

**Architecture:**
```
┌─────────────────────────────────────┐
│      ProgressManager (Singleton)    │
│  • Track multiple operations        │
│  • Emit progress updates            │
│  • Store operation history          │
└──────────────┬──────────────────────┘
               ↓
    ┌──────────┴──────────┐
    ↓                     ↓
┌─────────────────┐  ┌────────────────────┐
│ ProgressBar     │  │ ProgressDetails    │
│ Widget          │  │ Dialog             │
│                 │  │                    │
│ • Inline bar    │  │ • Full details     │
│ • Cancel btn    │  │ • Multi-operation  │
│ • ETA display   │  │ • History view     │
└─────────────────┘  └────────────────────┘
```

**Usage Example:**
```python
# In any dock
from src.gui.progress import ProgressManager

def _on_process(self):
    # Start tracking operation
    op_id = ProgressManager.start_operation(
        name="AI Processing",
        total_steps=100
    )
    
    # Update progress
    for i in range(100):
        ProgressManager.update_operation(op_id, i, f"Processing file {i}")
    
    # Finish
    ProgressManager.complete_operation(op_id, success=True)
```

**Analysis:**
- ✅ **Singleton Pattern:** Centralized progress tracking
- ✅ **Observable:** Docks can query progress status
- ✅ **History:** Past operations stored for debugging
- 🎯 **Role:** BRANCH coordinator (manages progress for all docks)

---

### 4. Workers (`src/gui/workers/` - 2 files)

**Purpose:** Background processing threads

| File | Purpose |
|------|---------|
| `ai_processor_worker.py` | AI API calls (OpenAI, Gemini) |
| `__init__.py` | Worker exports |

**Analysis:**
- ✅ **Thread Safety:** All workers extend `ProcessorWorkerBase(QThread)`
- ✅ **Signal Communication:** Workers emit progress/finished/error signals
- 🎯 **Role:** LEAF executors (do actual work in background)

---

### 5. Dialogs (`src/gui/dialogs/` - 36KB, 2 files)

**Purpose:** Popup dialogs

| File | Purpose |
|------|---------|
| `json_search_dialog.py` | JSON search configuration popup |
| `__init__.py` | Dialog exports |

**Plus 25+ dialog files in main `src/gui/` directory:**
- `batch_dialog.py` - Batch operation configuration
- `case_validator_dialog.py` - Case conversion validation
- `config_editor_dialog.py` - Config file editor
- `diff_viewer_dialog.py` - File diff viewer
- `error_report_dialog.py` - Error reporting
- `history_dialog.py` - Operation history
- `layout_manager_dialog.py` - Layout save/load
- `merge_config_dialog.py` - Config merging
- `operation_preview_dialog.py` - Operation preview
- `plugin_manager_dialog.py` - Plugin management
- `preferences_dialog.py` - Application preferences
- `presets_dialog.py` - Preset management
- `recall_dialog.py` - Recall previous operations
- `shortcut_customizer.py` - Keyboard shortcut editor
- `shortcuts_dialog.py` - Shortcut reference
- `statistics_dialog.py` - Usage statistics
- `template_dialog.py` - Template selection
- `transparency_dialog.py` - Window transparency
- `tutorial_assistant_dialog.py` - Tutorial helper
- `update_notification_dialog.py` - Update notifications
- `venn_diagram_dialog.py` - Venn diagram generator

**Analysis:**
- ✅ **Modal Dialogs:** Block until user responds
- ✅ **Reusable:** Called from multiple docks
- 🎯 **Role:** LEAF helpers (simple input/output dialogs)

---

## Menu Builder Architecture

**File:** `src/gui/menu_builder.py` (24,943 bytes)

**Purpose:** Centralized menu creation (Phase 3.4 refactoring)

**Menus Created:**
1. **File Menu:**
   - New from Template (Ctrl+Shift+N)
   - Open Editor (Ctrl+E)
   - Exit

2. **Edit Menu:**
   - Undo (Ctrl+Z)
   - Redo (Ctrl+Y)
   - Clear History

3. **Tools Menu:** (16 tools!)
   - Search/Replace
   - Insert
   - JSON Translate
   - JSON Rewriter
   - Text Extractor
   - Placeholder Replacer
   - AI Processor
   - JSON Search
   - Case Converter
   - Text to JSON
   - Google Translate
   - Set Operations
   - Calculator
   - Formula Builder
   - File Explorer (Ctrl+Shift+F)
   - Advanced Extractor (Ctrl+Shift+E)

4. **View Menu:**
   - Toggle docks visibility
   - Layout management

5. **Themes Menu:**
   - Light
   - Dark
   - System (follows OS)

6. **Settings Menu:**
   - Preferences
   - Shortcuts
   - Plugin Manager

7. **Plugins Menu:**
   - Dynamically populated from installed plugins

8. **Help Menu:**
   - Tutorials
   - Documentation
   - Check for Updates

9. **About Menu:**
   - About Clarify
   - License

**Pattern:**
```python
class MenuBuilder:
    @staticmethod
    def build_all_menus(main_window) -> None:
        """Build all menus for the main window."""
        bar = main_window.menuBar()
        
        MenuBuilder._build_file_menu(main_window, bar)
        MenuBuilder._build_edit_menu(main_window, bar)
        MenuBuilder._build_tools_menu(main_window, bar)
        MenuBuilder._build_view_menu(main_window, bar)
        MenuBuilder._build_themes_menu(main_window, bar)
        MenuBuilder._build_settings_menu(main_window, bar)
        MenuBuilder._build_plugins_menu(main_window, bar)
        MenuBuilder._build_help_menu(main_window, bar)
        MenuBuilder._build_about_menu(main_window, bar)
        MenuBuilder._setup_shortcuts(main_window)
    
    @staticmethod
    def _build_tools_menu(main_window, bar) -> None:
        """Build Tools menu."""
        m_tools = bar.addMenu(tr("menu.tools"))
        
        # Create actions
        main_window.act_open_translate = QAction(tr("menu.tools.json_translate"), main_window)
        main_window.act_open_ai_processor = QAction(tr("menu.tools.ai_processor"), main_window)
        # ... 14 more actions
        
        # Connect to dock opening methods
        main_window.act_open_translate.triggered.connect(main_window._open_trans)
        main_window.act_open_ai_processor.triggered.connect(main_window._open_ai_processor)
        
        # Add to menu
        m_tools.addAction(main_window.act_open_translate)
        m_tools.addAction(main_window.act_open_ai_processor)
        # ... 14 more
```

**Analysis:**
- ✅ **Centralized:** All menu logic in one file (was ~300 lines in MainWindow)
- ✅ **i18n Ready:** All strings use `tr()` for translation
- ✅ **Keyboard Shortcuts:** Defined alongside menu items
- ✅ **Action Pattern:** QAction separates UI from behavior
- 🎯 **Role:** BRANCH coordinator (connects menu → dock opening methods)

---

## Signal/Slot Communication Patterns

### Pattern 1: Worker → Dock Communication

```python
# Worker thread
class SearchWorker(QThread):
    progress = Signal(str)          # Progress message
    match_found = Signal(dict)      # Individual match
    finished_ok = Signal(object)    # Final results
    finished_error = Signal(str)    # Error message
    
    def run(self):
        for file in files:
            self.progress.emit(f"Searching {file}...")
            matches = search_file(file)
            for match in matches:
                self.match_found.emit(match)
        
        self.finished_ok.emit(all_results)

# Dock
class SearchDock(BaseDock):
    def __init__(self):
        self.worker = SearchWorker()
        self.worker.progress.connect(self._on_progress)
        self.worker.match_found.connect(self._on_match_found)
        self.worker.finished_ok.connect(self._on_finished)
        self.worker.finished_error.connect(self._on_error)
    
    def _on_progress(self, message: str):
        self.status_label.setText(message)
    
    def _on_match_found(self, match: dict):
        self.results_tree.add_match(match)
    
    def _on_finished(self, results):
        self.show_info("Complete", f"Found {len(results)} matches")
```

**Benefits:**
- ✅ **Responsive UI:** Worker runs in background
- ✅ **Real-time Updates:** Progress shown as it happens
- ✅ **Error Handling:** Worker errors don't crash GUI

---

### Pattern 2: Dock → MainWindow Communication

```python
# Dock emits signal
class EditorDock(BaseDock):
    file_opened = Signal(str)  # Emitted when file is opened
    
    def _open_file(self, path: str):
        # Open file logic...
        self.file_opened.emit(path)

# MainWindow connects to signal
class MainWindow(QMainWindow):
    def __init__(self):
        self.dock_editor = DockFactory.create_editor_dock(self)
        self.dock_editor.file_opened.connect(self._on_file_opened)
    
    def _on_file_opened(self, path: str):
        # Update recent files list
        self.history_manager.add_recent_file(path)
        
        # Update window title
        self.setWindowTitle(f"Clarify - {path}")
```

---

### Pattern 3: Inter-Dock Communication (via MainWindow)

```python
# Dock A
class SearchDock(BaseDock):
    open_in_editor_requested = Signal(str)  # Path to open
    
    def _on_open_in_editor(self):
        selected_file = self.results_tree.get_selected_file()
        self.open_in_editor_requested.emit(selected_file)

# MainWindow mediates
class MainWindow(QMainWindow):
    def __init__(self):
        # Connect search dock → editor dock
        self.dock_search.open_in_editor_requested.connect(self._open_file_in_editor)
    
    def _open_file_in_editor(self, path: str):
        # Ensure editor dock exists
        if not hasattr(self, 'dock_editor'):
            self._open_editor()
        
        # Load file
        self.dock_editor.load_file(path)
        self.dock_editor.show()
```

**Analysis:**
- ✅ **Loose Coupling:** Docks don't import each other
- ✅ **MainWindow Mediator:** Central coordination point
- ✅ **Signal Chain:** Search → MainWindow → Editor

---

## Initialization Flow (GUI Perspective)

**Recall from Session 1:**
```
InitializationManager.initialize_all()
  ├─ Phase 1: Core Systems (logging, errors)
  ├─ Phase 2: Configuration (settings, i18n)
  ├─ Phase 3: Managers (commands, plugins, layouts)
  └─ Phase 4: UI Components ← WE'RE HERE
```

### Phase 4 Deep Dive: `_build_ui()`

**Called by:** `InitializationManager.build_ui_components()`  
**Location:** `src/app.py` MainWindow class

```python
def _build_ui(self):
    """Build main user interface (v2.9.114 - Phase 1)."""
    
    # 1. Create central widget (tabs)
    self.tabs = QTabWidget()
    self.setCentralWidget(self.tabs)
    
    # 2. Create Search/Replace panel (v2.9.114 - Phase 1.2)
    from .gui.panels import SearchReplacePanel
    self.tab_search = SearchReplacePanel(self)
    self.tabs.addTab(self.tab_search, tr("tab.search_replace"))
    
    # 3. Create Insert panel (v2.9.114 - Phase 1.3)
    from .gui.panels import InsertPanel
    self.insert_panel = InsertPanel(self)
    self.tabs.addTab(self.insert_panel, tr("tab.insert"))
    
    # 4. Create tool docks (lazy - created when user opens them)
    # (Docks are NOT created here - created on demand via DockFactory)
    
    # 5. Connect panel signals
    self.tab_search.open_in_editor_requested.connect(self._load_file_in_editor)
    self.insert_panel.operation_completed.connect(self._on_insert_completed)
```

**Analysis:**
- ✅ **Tabs First:** Central widget is QTabWidget
- ✅ **Core Panels:** Search/Replace and Insert always created
- ✅ **Lazy Docks:** Tool docks created when user opens them (via menu)
- 🎯 **Why Lazy?** Faster startup (don't create 16+ docks if user won't use them)

---

### Dock Creation Flow (On Demand)

```
User clicks "Tools → AI Processor"
    ↓
Menu action triggered
    ↓
main_window._open_ai_processor()
    ↓
DockFactory.create_ai_processor_dock(main_window)
    ↓
    1. from ..gui import AIProcessorDock  (lazy import)
    2. dock = AIProcessorDock(parent=main_window)
    3. setattr(main_window, 'dock_ai_processor', dock)
    4. main_window.addDockWidget(Qt.RightDockWidgetArea, dock)
    5. dock.hide() initially
    6. dock.show() → User sees dock!
```

---

## Package Exports (`__init__.py`)

**File:** `src/gui/__init__.py` (2,417 bytes)

**Pattern:** Explicit `__all__` export list

```python
"""
GUI Package for Clarify

Contains all dock widgets and UI components with modular architecture.
"""

# Base classes and mixins
from .base_dock import (
    BaseDock, StandardToolDock, ProcessorWorkerBase,
    FileInputMixin, ResultsOutputMixin, ActionButtonsMixin,
    OptionsGroupMixin, ValidationMixin
)

# Dock Factory (v2.9.114 - Phase 3.3)
from .dock_factory import DockFactory

# Menu Builder (v2.9.114 - Phase 3.4)
from .menu_builder import MenuBuilder

# Window Settings (v2.9.114 - Phase 3.5)
from .window_settings import WindowSettings

# Tool docks (20+ imports)
from .case_converter_dock import CaseConverterDock
from .placeholder_replacer_dock import PlaceholderReplacerDock
from .json_search_dock import JsonSearchDock
# ... 17 more docks

__all__ = [
    # Base classes
    'BaseDock', 'StandardToolDock', 'ProcessorWorkerBase',
    # Mixins
    'FileInputMixin', 'ResultsOutputMixin', 'ActionButtonsMixin',
    # Dock Factory
    'DockFactory',
    # Menu Builder
    'MenuBuilder',
    # Window Settings
    'WindowSettings',
    # Tool docks (20+ exports)
    'CaseConverterDock', 'PlaceholderReplacerDock', 'JsonSearchDock',
    # ...
]
```

**Analysis:**
- ✅ **Clean Public API:** Only exports what's needed
- ✅ **Grouped Imports:** Base classes, mixins, factories, docks
- ✅ **Version Tracking:** Comments note refactoring phases
- 🎯 **Role:** BRANCH entry point (controls what's exposed from gui package)

---

## Design Patterns Identified

### 1. **Factory Pattern** (DockFactory)

**Purpose:** Centralize dock creation logic

**Benefits:**
- Consistent creation process
- Easy to add new docks
- Centralized configuration

**Implementation:**
```python
# Before (in MainWindow):
self.dock_translate = JsonTranslateDock(self)
self.addDockWidget(Qt.RightDockWidgetArea, self.dock_translate)
self.dock_translate.hide()

# After (using Factory):
DockFactory.create_json_translate_dock(self)
```

---

### 2. **Mixin Pattern** (FileInputMixin, etc.)

**Purpose:** Share UI component creation across docks

**Benefits:**
- Code reuse without inheritance
- Flexible composition
- Easy to add new mixins

**Implementation:**
```python
class MyDock(BaseDock, FileInputMixin, ResultsOutputMixin):
    def _setup_ui(self):
        # From FileInputMixin
        lbl, txt, btn, chk = self.create_file_input("Select file:")
        
        # From ResultsOutputMixin
        results_box = self.create_results_output()
```

---

### 3. **Template Method Pattern** (BaseDock)

**Purpose:** Define skeleton, let subclasses fill in details

**Benefits:**
- Consistent lifecycle
- Easy to extend
- Clear contract

**Implementation:**
```python
class BaseDock(QDockWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self._setup_ui()          # Override this
        self._connect_signals()   # Override this
    
    def _setup_ui(self):
        """Override to setup UI components."""
        pass
    
    def _connect_signals(self):
        """Override to connect signals."""
        pass
```

---

### 4. **Signal/Slot Pattern** (Qt Native)

**Purpose:** Event-driven communication

**Benefits:**
- Loose coupling
- Type-safe
- Thread-safe (Qt handles it)

**Implementation:**
```python
# Emitter
class Worker(QThread):
    progress = Signal(int)  # Signal definition
    
    def run(self):
        for i in range(100):
            self.progress.emit(i)  # Emit signal

# Receiver
class Dock(BaseDock):
    def __init__(self):
        self.worker = Worker()
        self.worker.progress.connect(self._on_progress)  # Connect slot
    
    def _on_progress(self, value: int):
        self.progress_bar.setValue(value)
```

---

### 5. **Worker Thread Pattern** (ProcessorWorkerBase)

**Purpose:** Keep UI responsive during long operations

**Benefits:**
- Non-blocking UI
- Progress updates
- Cancelable operations

**Implementation:**
```python
# Worker
class MyWorker(ProcessorWorkerBase):
    def run(self):
        for item in items:
            # Do heavy work
            result = process(item)
            self.progress.emit(f"Processed {item}")
        self.finished_ok.emit(results)

# Dock
class MyDock(BaseDock):
    def _on_process(self):
        self.worker = MyWorker()
        self.worker.progress.connect(self._update_status)
        self.worker.finished_ok.connect(self._show_results)
        self.worker.start()  # Run in background
```

---

## File Size Analysis

### Dock Complexity Distribution

```
Simple Docks (< 500 lines):
  case_converter_dock.py       260 lines  ✅ Good
  placeholder_replacer_dock.py 320 lines  ✅ Good
  
Medium Docks (500-1000 lines):
  json_search_dock.py          680 lines  ✅ Acceptable
  json_translate_dock.py       750 lines  ✅ Acceptable
  text_extractor_dock.py       820 lines  ✅ Acceptable
  
Large Docks (1000-1500 lines):
  ai_processor_dock.py        1,193 lines ⚠️ Consider refactoring
  json_rewriter_dock.py       1,280 lines ⚠️ Consider refactoring
  
Mega Docks (> 1500 lines):
  file_explorer_dock.py       2,066 lines ⚠️ REFACTORING NEEDED
```

**Refactoring Candidates:**
1. **file_explorer_dock.py** (2,066 lines)
   - Could split into: FileTreeWidget, SearchPanel, FilterPanel, ResultsPanel
   
2. **ai_processor_dock.py** (1,193 lines)
   - Could extract: ProviderManager, APIKeyManager, PromptBuilder
   
3. **json_rewriter_dock.py** (1,280 lines)
   - Could extract: OptionsPanel, PreviewPanel, ValidationPanel

---

## Insights & Learnings

### 1. **3-Layer Architecture is Clean**

✅ **Layer 1 (Base):** Provides building blocks (BaseDock, Mixins)  
✅ **Layer 2 (Factory):** Handles creation and configuration  
✅ **Layer 3 (Concrete):** Implements specific tools

**Benefit:** Easy to add new docks (just extend BaseDock, add factory method)

---

### 2. **Mixin Pattern Reduces Duplication**

✅ 5 mixins identified (FileInput, ResultsOutput, ActionButtons, OptionsGroup, Validation)  
✅ Used across 20+ docks  
✅ **Estimated Code Reuse:** ~1,000 lines of UI code shared

**Benefit:** Don't repeat file picker, results display, button layouts

---

### 3. **Factory Pattern Centralizes Creation**

✅ Before: 95 lines of dock creation scattered in MainWindow  
✅ After: 9,245 bytes in DockFactory (253 lines)  
✅ **16 convenience methods** for common docks

**Benefit:** Add new dock = add 5 lines to factory (not 20+ in MainWindow)

---

### 4. **Worker Thread Pattern is Consistent**

✅ All background operations use `ProcessorWorkerBase`  
✅ Standard signals: `progress`, `finished_ok`, `finished_error`  
✅ **UI never freezes** during long operations

**Benefit:** Professional UX (responsive GUI, progress feedback)

---

### 5. **Signal/Slot Enables Loose Coupling**

✅ Docks don't import each other  
✅ MainWindow mediates communication  
✅ **32 signals** in FileExplorerDock alone

**Benefit:** Can change dock implementations without breaking others

---

### 6. **Lazy Initialization Speeds Startup**

✅ Core panels created immediately (Search/Replace, Insert)  
✅ Tool docks created on demand (16+ docks)  
✅ **Estimated startup time savings:** 2-3 seconds

**Benefit:** Fast app launch (create only what user needs)

---

### 7. **Internationalization is First-Class**

✅ All UI strings use `tr()` function  
✅ Tooltips use `tooltip_tr()`  
✅ **7 languages supported** (en, pt-br, es, fr, de, zh, ja)

**Benefit:** Easy to add new translations (just update translation files)

---

### 8. **Progress Tracking is Centralized**

✅ `ProgressManager` singleton tracks all operations  
✅ `ProgressBarWidget` for inline display  
✅ `ProgressDetailsDialog` for full view  
✅ **Operation history** stored for debugging

**Benefit:** Consistent progress UX across all tools

---

### 9. **Refactoring Evidence Everywhere**

📝 "Phase 3.3", "Phase 3.4", "v2.9.114" in comments  
📝 "Extracted from MainWindow" notes  
📝 Backup files (`.backup`) show iterative changes

**Benefit:** Clear history of architectural improvements

---

### 10. **Some Docks Are Too Large**

⚠️ `file_explorer_dock.py` = 2,066 lines (mega file!)  
⚠️ Complex docks have 32+ signals  
⚠️ Hard to understand single-file mega-components

**Recommendation:** Split large docks into smaller components (ongoing work)

---

## Questions Answered

### Q1: How are docks created?

**A:** Via **DockFactory** pattern:
1. User clicks menu → `_open_xxx()` method
2. Method calls `DockFactory.create_xxx_dock(self)`
3. Factory: imports class, creates instance, adds to window, hides initially
4. Dock shown to user

---

### Q2: How do docks communicate?

**A:** Via **Signal/Slot** pattern:
1. Dock emits signal (e.g., `file_opened.emit(path)`)
2. MainWindow connects signal to slot (e.g., `dock.file_opened.connect(self._on_file_opened)`)
3. MainWindow mediates between docks (no direct dock-to-dock imports)

---

### Q3: How are UI components reused?

**A:** Via **Mixin** pattern:
1. `FileInputMixin` provides file selection UI
2. `ResultsOutputMixin` provides results display
3. Docks inherit multiple mixins: `class MyDock(BaseDock, FileInputMixin):`
4. Call mixin methods: `self.create_file_input("Select file:")`

---

### Q4: How do background operations work?

**A:** Via **Worker Thread** pattern:
1. Create worker: `worker = MyWorker(params)`
2. Connect signals: `worker.finished_ok.connect(self._on_done)`
3. Start thread: `worker.start()`
4. Worker emits `progress` during execution, `finished_ok`/`finished_error` when done
5. Qt handles thread safety automatically

---

### Q5: How is the GUI structured in Import Tree?

**A:**
- **ROOT:** `MainWindow` (orchestrator - decides which panels/docks to create)
- **BRANCH:** `DockFactory`, `MenuBuilder`, `InitializationManager` (coordinators)
- **LEAF:** Concrete docks, panels, widgets, workers (executors)

**Example:** FileExplorerDock is a BRANCH (coordinates tree, search, filter, results)  
But its sub-widgets (tree, search panel, etc.) are LEAFs

---

## Next Steps for Session 3

**Focus:** BRANCH - Core Business Logic  
**Target:** `src/core/`, batch_manager, plugin_loader, formula_manager  
**Key Questions:**
- How does the search algorithm work?
- What's the JSON processing pipeline?
- How does plugin isolation work?
- How is backward compatibility maintained?

**Reading Mode:** SCAN (understand architecture, not every algorithm detail)  
**Estimated Time:** 2 hours

---

## Appendix: GUI Module Statistics

### File Count by Type

```
Dock Widgets:      30 files
Dialogs:           25 files
Panels:             9 files
Widgets:            9 files
Progress:           4 files
Workers:            2 files
Builders:           3 files (Factory, Menu, Window)
Base Classes:       1 file (base_dock.py)
────────────────────────
TOTAL:             83 files (+ 3 __init__.py files = 86)
```

### Lines of Code Distribution

```
Panels:         ~5,500 lines (search, insert, results)
Widgets:        ~4,200 lines (json tree, file filter, syntax)
Docks:         ~12,000 lines (20+ tool docks)
Dialogs:        ~8,000 lines (25+ dialogs)
Progress:       ~1,000 lines (manager, widgets)
Base/Factory:   ~1,500 lines (base classes, factory, menu)
Workers:          ~500 lines (background threads)
────────────────────────
TOTAL:         ~32,700 lines of GUI code
```

### Complexity Hot Spots

```
Most Complex File:
  file_explorer_dock.py      2,066 lines, 32 signals, 15+ instance vars

Most Signals:
  file_explorer_dock.py      32 signals
  ai_processor_dock.py       12 signals

Most Mixins Used:
  AIProcessorDock            BaseDock + FileInputMixin + ResultsOutputMixin
  PlaceholderReplacerDock    BaseDock + FileInputMixin + ValidationMixin
```

---

## Session Completion

**Status:** ✅ COMPLETE  
**Time Spent:** 2 hours  
**Files Analyzed:** 86 GUI files (~1.6MB code, ~32,700 lines)  
**Understanding Level:** SCAN (architecture clear, key patterns identified)  
**Next Session:** Core Business Logic (src/core/, managers, plugins)

---

**Date Completed:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Protocol Compliance:** SIMPLICITY_PROTOCOL_3.md Step 1.3 ✅  
**Import Tree Progress:** ROOT + BRANCH (GUI layer) complete 🌳
