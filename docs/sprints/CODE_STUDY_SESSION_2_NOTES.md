# Code Study - Session 2: MainWindow & Base Architecture

**Date**: 2026-01-22  
**Programmer**: #7  
**Branch**: COM7-read-docs  
**Phase**: 1 - Architecture Overview (continued)  
**Files Studied**: 3 files (~950 lines)

---

## Files Analyzed

### 1. `src/app.py` (continued - lines 150-600)
**Total Size**: 1,967 lines
**Lines Studied**: 150-600 (~450 lines, 23% of file)

### 2. `src/gui/base_dock.py` (complete)
**Size**: 596 lines (100% studied)

### 3. `src/gui/dock_factory.py` (complete)
**Size**: 252 lines (100% studied)

---

## Architecture Discoveries

### MainWindow Class Structure (lines 386-600)

**Initialization Flow** (lines 388-431):
```python
class MainWindow(QMainWindow):
    def __init__(self, app: QApplication):
        super().__init__()
        
        # 1. Fix Linux window flags (v2.9.117 - CRITICAL BUG FIX)
        self._desired_window_flags = (
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |  # ← Missing on Linux!
            Qt.WindowCloseButtonHint
        )
        self.setWindowFlags(self._desired_window_flags)
        
        # 2. Initialize all core systems via InitializationManager (Phase 3.7)
        InitializationManager.initialize_all(self, app)
        
        # 3. Install horizontal scrolling (Shift+Scroll - v2.9.115)
        app.installEventFilter(self)
        
        # 4. Restore layout (v2.9.84)
        self.layout_manager.restore_last_layout()
        
        # 5. Force UI update (fix invisible widgets)
        self.updateGeometry()
        QApplication.processEvents()
        
        # 6. Apply accessibility (v2.9.35)
        self._apply_accessibility()
        
        # 7. Restore tabs from previous session (v2.9.40)
        self._restore_tab_state()
        
        # 8. Force initialize all tabs (prevent lazy render bugs)
        self._initialize_all_tabs()
        
        # 9. Auto-check for updates (v2.9.45)
        self._auto_check_for_updates()
```

**Key Insight**: MainWindow initialization is HIGHLY systematic with clear phases!

### InitializationManager Pattern

**Discovery**: MainWindow delegates ALL initialization to `InitializationManager.initialize_all()`
- Line 406: `InitializationManager.initialize_all(self, app)`
- Pattern: **Separation of Concerns** - keeps MainWindow.__init__ clean

**What it likely initializes**:
- Menu system (MenuBuilder)
- Tab system (QTabWidget)
- Dock management
- Settings/preferences
- Theme system
- i18n system
- Progress tracking

### Lazy Loading Pattern for Docks

**Tool Opening Methods** (lines 494-548):
```python
def _open_trans(self):
    DockFactory.create_json_translate_dock(self)

def _open_rewrite(self):
    DockFactory.create_json_rewriter_dock(self)

def _open_text_extractor(self):
    DockFactory.create_text_extractor_dock(self)
    
# ... 10+ more _open_* methods
```

**Pattern**: Factory Method
- Each tool has a lazy creation method
- Called only when user opens the tool
- Delegates to DockFactory for actual creation

### Tab Manager Pattern (v2.9.40)

**Lines 560-600**: Different pattern for tabs vs docks!

```python
def _show_search_replace(self):
    # Check if tab exists at index 0
    if self.tabs.count() > 0 and self.tabs.tabText(0) == "Search / Replace":
        self.tabs.setCurrentIndex(0)  # Switch to existing
    else:
        # Tab was closed, recreate at index 0
        self.tab_search = SearchReplacePanel(parent=self, progress_manager=self.progress_manager)
        self.tabs.insertTab(0, self.tab_search, "Search / Replace")
        self.tabs.setCurrentIndex(0)
```

**Key Difference**:
- **Docks**: Created once, hidden/shown (persistent)
- **Tabs**: Can be closed and recreated (dynamic)

**Why**: Tabs are more ephemeral, docks are permanent UI fixtures

---

## BaseDock Architecture

### Class Hierarchy
```python
QDockWidget (PySide6)
    ↓
BaseDock (base_dock.py)
    ↓
Specific Docks (JsonTranslateDock, JsonRewriterDock, etc.)
```

### BaseDock Features (lines 47-77)

```python
class BaseDock(QDockWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self._setup_ui()         # ← Override point 1
        self._connect_signals()   # ← Override point 2
    
    # Template methods (override in subclasses)
    def _setup_ui(self): pass
    def _connect_signals(self): pass
    
    # Utility methods (use in subclasses)
    def show_error(self, title, message): ...
    def show_info(self, title, message): ...
    def show_warning(self, title, message): ...
```

**Pattern**: **Template Method** (Gang of Four)
- Defines skeleton in base class
- Subclasses fill in the details via _setup_ui() and _connect_signals()

### Mixins for Reusability (lines 79-144)

#### FileInputMixin
```python
class FileInputMixin:
    def create_file_input(self, label_text, placeholder, with_is_file_checkbox):
        # Returns: (label, line_edit, browse_button, is_file_checkbox)
        ...
    
    def create_extension_filter(self, default_extensions):
        # Returns: (label, line_edit)
        ...
    
    def browse_file_or_directory(self, line_edit, is_file, file_filter, title):
        # Opens QFileDialog and sets result to line_edit
        ...
```

**Usage Pattern**:
```python
class SomeDock(BaseDock, FileInputMixin):
    def _setup_ui(self):
        lbl, ed, btn, chk = self.create_file_input("Input File:")
        btn.clicked.connect(lambda: self.browse_file_or_directory(ed, chk.isChecked()))
```

**Benefit**: Code reuse across 10+ docks that need file inputs!

#### ProcessorWorkerBase (lines 146-150)
```python
class ProcessorWorkerBase(QThread):
    progress = Signal(str)      # Progress messages
    finished_ok = Signal(object)  # Success result
    # ... (likely more signals: finished_error, cancelled)
```

**Pattern**: Observer (Qt Signals/Slots)
- Workers run in background threads
- Emit signals to update UI
- MainWindow connects to signals

---

## DockFactory Pattern

### Factory Method Implementation (lines 36-89)

```python
class DockFactory:
    @staticmethod
    def create_dock(main_window, dock_class, dock_attr_name,
                   area=None, hide=True, signal_connections=None, **kwargs):
        # 1. Create dock instance
        dock = dock_class(parent=main_window, **kwargs)
        
        # 2. Store in main_window as attribute
        setattr(main_window, dock_attr_name, dock)
        
        # 3. Add to dock area
        main_window.addDockWidget(area, dock)
        
        # 4. Connect signals (if provided)
        if signal_connections:
            for signal_name, slot in signal_connections.items():
                getattr(dock, signal_name).connect(slot)
        
        # 5. Set visibility
        if hide: dock.hide()
        
        return dock
```

**Brilliant Design**:
- ✅ Single place for all dock creation logic
- ✅ Consistent pattern across 13+ docks
- ✅ Optional signal connections
- ✅ Lazy initialization support (create_dock_lazy)

### Convenience Methods (lines 118-150)

Each dock type gets a dedicated factory method:
```python
@staticmethod
def create_json_translate_dock(main_window):
    from ..gui import JsonTranslateDock
    return DockFactory.create_dock(
        main_window, JsonTranslateDock, 'dock_translate'
    )
```

**Pattern**: One-liner creation, import inside function (lazy module loading)

**13+ Factory Methods**:
1. create_json_translate_dock
2. create_json_rewriter_dock
3. create_text_extractor_dock
4. create_placeholder_replacer_dock
5. create_ai_processor_dock
6. create_json_search_dock
7. create_case_converter_dock
8. create_jsx_extractor_dock
9. create_text_to_json_dock
10. create_file_explorer_dock
11. create_history_dock
12. create_tutorials_dock
13. create_editor_dock
14. create_google_translate_dock

---

## Import Strategy Insights

### Conditional PySide6 Import (app.py lines 169-194)

```python
_PYSIDE = True
try:
    from PySide6.QtCore import Qt, QAbstractTableModel, ...
    from PySide6.QtWidgets import QApplication, QMainWindow, ...
except Exception:
    _PYSIDE = False
    # Create stub classes
    class QWidget: pass
    class QMainWindow: pass
    # ...
```

**Why**: CLI commands work WITHOUT PySide6!
- Headless server usage
- Docker containers without X server
- Testing in CI/CD without display

### Lazy Imports in Factory (dock_factory.py line 122)

```python
def create_json_translate_dock(main_window):
    from ..gui import JsonTranslateDock  # ← Import INSIDE function
    return DockFactory.create_dock(...)
```

**Benefits**:
- Only load dock modules when actually used
- Faster startup time
- Lower memory footprint if user doesn't open all tools

---

## Critical Bug References Found

### 1. Linux Window Flags (v2.9.117) - SOLVED

**Location**: app.py lines 390-402

**Problem**: Maximize button [□] missing on Linux
**Root Cause**: Linux window managers require explicit `WindowMaximizeButtonHint`
**Solution**: Store desired flags + restore after operations
**Impact**: CRITICAL - users couldn't maximize window

**Comment**:
> "Fix: Configure window flags for Linux compatibility (v2.9.117)  
> Linux window managers (X11/Wayland) require explicit WindowMaximizeButtonHint  
> to show the maximize button [□] in the title bar alongside [_] and [×]"

### 2. Invisible Widgets Bug - SOLVED

**Location**: app.py lines 414-428

**Problem**: Widgets invisible on startup
**Root Cause**: Qt doesn't render non-visible tabs until activated
**Solution**: Force initialize all tabs + processEvents()

**Comments**:
- Line 415: "Force UI update to ensure widgets are properly rendered"
- Line 425: "Qt doesn't render widgets in non-visible tabs until they're activated"
- Line 426: "This causes invisible widgets bug - force show all tabs once"

---

## Design Patterns Identified

1. **Template Method**: BaseDock._setup_ui() / _connect_signals()
2. **Factory Method**: DockFactory.create_*_dock() methods
3. **Mixin**: FileInputMixin, ProcessorWorkerBase
4. **Observer**: Qt Signals/Slots (progress, finished_ok, etc.)
5. **Lazy Initialization**: Docks created on-demand, not at startup
6. **Separation of Concerns**: InitializationManager handles setup

---

## Questions Raised

1. **What does InitializationManager.initialize_all() do exactly?**
   - Need to study src/gui/initialization_manager.py
   
2. **How does TabManager work?**
   - Different from DockFactory (tabs vs docks)
   - Need to study src/gui/tab_manager.py
   
3. **What is ProgressManager?**
   - Passed to SearchReplacePanel and InsertPanel
   - v2.9.114 feature (Phase 1.1)
   
4. **How does the theme system integrate?**
   - ThemeManager.apply_theme() called
   - Dark/light/system modes
   
5. **What's in the menu system?**
   - MenuBuilder imported but not seen yet
   - Likely builds File/Edit/Tools/View/Help menus

---

## Next Steps for Session 3

### Priority Files to Study
- [ ] `src/gui/initialization_manager.py` (understand full init flow)
- [ ] `src/gui/tab_manager.py` (tab creation pattern)
- [ ] `src/gui/progress/*.py` (progress system - v2.9.114)
- [ ] `src/gui/menu_builder.py` (menu construction)
- [ ] `src/theme_manager.py` (theme switching)

### Understand Core Systems
- [ ] Settings persistence (QSettings)
- [ ] i18n runtime (how tr() works)
- [ ] Worker thread management
- [ ] Signal/slot architecture

---

**Status**: Phase 1 ongoing (35% of app.py read, 2 support files complete)
**Total Files Studied**: 7 files (~1,250 lines)
**Files Remaining**: 189 files (~56,915 lines)
**Time Spent**: ~30 minutes
**Estimated Remaining**: 3.5-6.5 hours

