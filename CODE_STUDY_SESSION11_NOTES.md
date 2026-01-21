# CODE STUDY SESSION 11 - Plugin & Extension System
**Date**: 2026-01-21  
**Programmer**: #4  
**Branch**: COM4-code-study  
**Focus**: Plugin architecture - Discovery, loading, interfaces, examples

---

## 📋 STUDY SCOPE

### Files Analyzed (5 files, 1,046 LOC)
1. **plugin_loader.py** (319 LOC) - Plugin discovery & loading system
2. **plugins/plugin_base.py** (282 LOC) - Plugin API interface
3. **plugins/example_export_csv.py** (32 LOC) - Example plugin
4. **extractors/__init__.py** (14 LOC) - Extractor interface exports
5. **processors/code_aware_translator.py** (399 LOC) - Processor example

**Total**: 1,046 LOC (vs predicted 800 - 31% higher)

**Note**: This session studies the plugin **architecture** (loader + base), not individual extractors/processors (those are separate subsystems). The extractor/processor files are included as **interface examples** showing plugin-like patterns.

---

## 🏗️ ARCHITECTURAL ANALYSIS

### 1. PLUGIN LOADER (`plugin_loader.py`)

**Purpose**: Dynamic plugin discovery, loading, and lifecycle management

#### Key Features
- **Auto-discovery** from `plugins/` directory
- **JSON metadata** (plugin.json per plugin)
- **Dynamic module loading** (importlib.util)
- **Event system** (emit_event to all active plugins)
- **QSettings integration** (enable/disable persistence)
- **Qt Signals** (plugin_loaded, plugin_activated, plugin_error)

#### Core Components

##### PluginMetadata (Lines 27-42)
```python
class PluginMetadata:
    id: str                  # Unique identifier
    name: str                # Display name
    version: str             # Semantic version (e.g., "1.0.0")
    description: str         # Purpose description
    author: str              # Author name
    entry_point: str         # Main file (default: "main.py")
    dependencies: List[str]  # Python packages needed
    enabled: bool            # Enable/disable flag
    plugin_dir: Path         # Plugin directory path
```

**Data source**: `plugins/<plugin_name>/plugin.json`

##### PluginLoader Class (Lines 45-319)
```python
class PluginLoader(QObject):
    # Qt Signals
    plugin_loaded = Signal(str)      # Emitted when plugin module loaded
    plugin_activated = Signal(str)   # Emitted when plugin activated
    plugin_error = Signal(str, str)  # Emitted on errors (id, message)
    
    # State
    plugins: Dict[str, Any]           # plugin_id → instance
    metadata: Dict[str, PluginMetadata]  # plugin_id → metadata
    settings: QSettings               # Enable/disable persistence
    plugin_dir: Path                  # Default: src/../plugins
```

#### Plugin Lifecycle

**1. Discovery** (Lines 85-127: `discover_plugins()`)
```python
Flow:
1. Scan plugins/ directory for subdirectories
2. For each subdir, check for plugin.json
3. Parse JSON → create PluginMetadata
4. Check QSettings for enabled state (overrides JSON)
5. Store in self.metadata
6. Return list of discovered metadata
```

**Graceful degradation**: Missing plugin.json → skip (no error), malformed JSON → print error + continue

**2. Loading** (Lines 129-189: `load_plugin()`)
```python
Flow:
1. Check if already loaded → return cached instance
2. Find entry_point file (e.g., main.py)
3. Load module dynamically (importlib.util.spec_from_file_location)
4. Find PluginBase subclass in module (introspection)
5. Instantiate plugin class
6. Store in self.plugins
7. Emit plugin_loaded signal
```

**Key technique**: Introspection to find plugin class
```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if (isinstance(attr, type) and 
        hasattr(attr, 'activate') and 
        attr.__name__ != 'PluginBase'):
        plugin_class = attr
        break
```

**3. Activation** (Lines 191-220: `activate_plugin()`)
```python
Flow:
1. Load plugin if not loaded
2. Check if enabled in metadata
3. Call plugin.activate(app) with MainWindow context
4. Emit plugin_activated signal
5. Catch/log exceptions (plugin errors don't crash app)
```

**Fail-safe**: Plugin activation errors are caught, logged, and don't block other plugins.

**4. Deactivation** (Lines 236-256: `deactivate_plugin()`)
```python
Flow:
1. Check if plugin is loaded
2. Call plugin.deactivate(app) if method exists
3. Catch/log exceptions
```

**Optional hook**: Plugins not required to implement deactivate().

#### Event System (Lines 271-286: `emit_event()`)
```python
def emit_event(event_name: str, data: Dict[str, Any]):
    # Broadcasts events to all active plugins
    for plugin_id, plugin in plugins.items():
        if metadata[plugin_id].enabled:
            if hasattr(plugin, 'on_event'):
                plugin.on_event(event_name, data)
```

**Common events** (from PluginBase docstring):
- `file_opened`: {"path": str}
- `file_saved`: {"path": str}
- `search_completed`: {"query": str, "results": list}
- `rewrite_completed`: {"input_path": str, "output_path": str}
- `ai_request_completed`: {"prompt": str, "response": str}

**Broadcasting pattern**: All plugins receive all events, filter by event_name internally.

#### Enable/Disable Persistence (Lines 258-269)
```python
def enable_plugin(plugin_id: str, enabled: bool):
    # Saves to QSettings
    settings.setValue(f"plugins/{plugin_id}/enabled", enabled)
    metadata[plugin_id].enabled = enabled
```

**Storage location**: `~/.config/Clarify/Clarify.conf` (Linux)

#### Design Patterns Identified
1. **Plugin Pattern**: Core architecture (dynamic loading + activation)
2. **Registry Pattern**: `self.plugins` dict stores loaded instances
3. **Lazy Loading**: Plugins loaded only when activated (or explicitly loaded)
4. **Observer Pattern**: Qt Signals for plugin events (plugin_loaded, plugin_activated)
5. **Event Bus**: `emit_event()` broadcasts to all plugins
6. **Graceful Degradation**: Errors in one plugin don't affect others
7. **Introspection**: Runtime discovery of plugin class via `dir()` + `isinstance()`
8. **Memento Pattern**: Enable/disable state persisted via QSettings
9. **Facade Pattern**: Simple public API (`activate_all_plugins()`) hides complexity

#### Integration Points
- **app.py**: Creates PluginLoader during startup
- **Main menu**: "Plugins" menu for enable/disable
- **Event emitters**: File operations, search, rewriter emit events
- **QSettings**: Shares settings with other managers

---

### 2. PLUGIN BASE (`plugins/plugin_base.py`)

**Purpose**: Base class + API for creating Clarify plugins

#### Key Features
- **Abstract interface** (activate() must be implemented)
- **Lifecycle hooks** (activate, deactivate, on_event)
- **UI helpers** (register_dock, add_menu_item)
- **Settings helpers** (get_setting, set_setting)
- **Message box helper** (show_message)

#### Plugin Structure (Lines 30-48)
```
plugins/
  my_plugin/
    plugin.json        # Metadata (required)
    main.py            # Entry point (inherits PluginBase)
    requirements.txt   # Optional pip dependencies
    README.md          # Documentation
```

#### PluginBase Class (Lines 24-282)
```python
class PluginBase:
    # Metadata (override in subclass)
    name: str = "Base Plugin"
    description: str = "Base class for Clarify plugins"
    version: str = "0.0.0"
    
    # State
    app: MainWindow          # Set during activation
    settings: QSettings
    _registered_docks: List[QDockWidget]
    _registered_actions: List[QAction]
```

#### Lifecycle Hooks

**activate(app)** (Lines 84-99) - **REQUIRED**
```python
def activate(self, app):
    """Called when plugin is loaded."""
    self.app = app
    raise NotImplementedError("Must implement activate()")
```

**Usage**:
- Register UI elements (docks, menu items)
- Connect to signals
- Initialize resources
- Load settings

**deactivate(app)** (Lines 101-127) - **OPTIONAL**
```python
def deactivate(self, app):
    """Called when plugin is unloaded (optional)."""
    # Default: cleanup registered UI elements
    for action in self._registered_actions:
        action.deleteLater()
    for dock in self._registered_docks:
        dock.deleteLater()
```

**Default behavior**: Removes all registered UI elements (fail-safe cleanup).

**on_event(event_name, data)** (Lines 129-144) - **OPTIONAL**
```python
def on_event(self, event_name: str, data: Dict[str, Any]):
    """Handle application events (optional)."""
    pass
```

**Usage**: React to app events (file opened, search completed, etc.)

#### UI Integration Helpers

**register_dock()** (Lines 148-168)
```python
def register_dock(app, dock: QDockWidget, area: str = "right"):
    """
    Register custom dock widget.
    
    Args:
        area: "left", "right", "top", "bottom"
    """
    area_map = {
        "left": Qt.LeftDockWidgetArea,
        "right": Qt.RightDockWidgetArea,
        "top": Qt.TopDockWidgetArea,
        "bottom": Qt.BottomDockWidgetArea
    }
    qt_area = area_map.get(area, Qt.RightDockWidgetArea)
    app.addDockWidget(qt_area, dock)
    self._registered_docks.append(dock)  # Track for cleanup
```

**add_menu_item()** (Lines 170-233)
```python
def add_menu_item(
    app, 
    menu_path: str,    # "Tools/My Plugin/Action"
    text: str,         # Action label
    callback: Callable,
    shortcut: Optional[str] = None
) -> QAction:
    """
    Add menu item to application.
    
    Creates nested menus if needed:
    - "Tools" → finds or creates top-level menu
    - "My Plugin" → finds or creates submenu
    - Creates QAction with callback
    """
```

**Smart menu resolution**:
- Case-insensitive matching for existing menus
- Removes `&` accelerator markers when comparing
- Creates hierarchy if missing

#### Settings Helpers (Lines 235-258)
```python
def get_setting(key: str, default: Any) -> Any:
    """Get plugin setting (prefixed with plugin name)."""
    plugin_key = f"plugins/{self.name}/{key}"
    return self.settings.value(plugin_key, default)

def set_setting(key: str, value: Any):
    """Save plugin setting."""
    plugin_key = f"plugins/{self.name}/{key}"
    self.settings.setValue(plugin_key, value)
```

**Namespacing**: Settings automatically prefixed with `plugins/<name>/` to avoid conflicts.

#### Message Helper (Lines 260-282)
```python
def show_message(title: str, message: str, icon: str = "information"):
    """Show QMessageBox to user."""
    icon_map = {
        "information": QMessageBox.Information,
        "warning": QMessageBox.Warning,
        "critical": QMessageBox.Critical,
        "question": QMessageBox.Question
    }
    # Shows modal dialog
```

#### Design Patterns Identified
1. **Template Method**: Base class defines skeleton, subclasses override activate()
2. **Hook Method**: deactivate() and on_event() are optional hooks
3. **Registry Pattern**: Tracks registered UI elements for cleanup
4. **Facade Pattern**: Helper methods hide Qt complexity
5. **Namespacing**: Settings prefixed with plugin name
6. **Resource Management**: Automatic cleanup in deactivate()
7. **Fail-Safe Defaults**: Default deactivate() cleans up UI elements

#### Integration Points
- **PluginLoader**: Calls activate() during plugin loading
- **QSettings**: Shares settings storage with other components
- **MainWindow**: Receives app reference for UI integration
- **Qt Signals**: Can connect to app signals in activate()

---

### 3. EXAMPLE PLUGIN (`plugins/example_export_csv.py`)

**Purpose**: Minimal working plugin example (CSV export)

#### Code Analysis (32 LOC)
```python
class ExportCSVPlugin(PluginBase):
    name = "Exportar JSON para CSV"
    description = "Exporta o JSON atual para um arquivo CSV."
    
    def activate(self, app):
        # Get current JSON
        data = app.get_current_json()
        if not data:
            QMessageBox.warning(app, "Exportar CSV", "Nenhum JSON carregado.")
            return
        
        # Show save dialog
        path, _ = QFileDialog.getSaveFileName(app, "Salvar CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        
        # Write CSV
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if isinstance(data, dict):
                writer.writerow(data.keys())
                writer.writerow(data.values())
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                writer.writerow(data[0].keys())
                for row in data:
                    writer.writerow(row.values())
            else:
                writer.writerow([str(data)])
        
        QMessageBox.information(app, "Exportar CSV", f"Arquivo salvo em: {path}")
```

#### Key Characteristics
- **Immediate execution**: activate() runs the export (no menu item)
- **Simple logic**: Dict → 2 rows, List[Dict] → table, other → single value
- **User interaction**: File dialog + message boxes
- **No deactivate**: Single-shot action, no cleanup needed
- **No on_event**: Doesn't listen to app events

**Design flaw**: Activates immediately instead of registering menu item. Better pattern:
```python
def activate(self, app):
    self.add_menu_item(app, "Tools/Export", "Export to CSV", self.export_csv)

def export_csv(self):
    # ... export logic here
```

#### Plugin Distribution
**Missing**: `plugin.json` file (required for PluginLoader to discover)

Example structure:
```json
{
  "id": "export_csv",
  "name": "Export to CSV",
  "version": "1.0.0",
  "description": "Export current JSON to CSV file",
  "author": "Josué Amaral",
  "entry_point": "example_export_csv.py",
  "dependencies": [],
  "enabled": true
}
```

#### Design Patterns Identified
1. **Template Method**: Inherits from PluginBase
2. **Strategy Pattern**: CSV export is one strategy (could have JSON, XML, etc.)
3. **Immediate Execution**: Runs on activation (anti-pattern for reusable plugins)

---

### 4. EXTRACTORS INTERFACE (`extractors/__init__.py`)

**Purpose**: Public API exports for extractor subsystem

#### Code Analysis (14 LOC)
```python
from .extractor import Extractor
from .generic_parser import GenericScopeParser
from .jsx_parser import JSXParser

__all__ = ["JSXParser", "GenericScopeParser", "Extractor"]
```

#### Design
- **Package interface pattern**: `__init__.py` exports public API
- **3 classes exposed**:
  1. **Extractor**: Base class (likely)
  2. **GenericScopeParser**: Generic code scope parser
  3. **JSXParser**: JSX/TSX-specific parser

**Note**: Individual extractor files not studied (out of scope for plugin session). They represent a **separate subsystem** (text extraction from code), not plugins.

#### Extractor Purpose (from file list)
- **extractor.py** (18,345 LOC) - Base extractor logic
- **jsx_parser.py** (20,723 LOC) - React/JSX parsing
- **generic_parser.py** (3,619 LOC) - Generic code parsing
- **advanced_extractor.py** (26,493 LOC) - Advanced extraction features

**Total extractors**: 69,180 LOC (largest subsystem in Clarify!)

#### Design Patterns Identified
1. **Package Pattern**: Clean public API via `__all__`
2. **Inheritance Hierarchy**: Extractor → GenericScopeParser → JSXParser (likely)
3. **Factory Pattern**: Import single module, get all extractor types

---

### 5. PROCESSOR EXAMPLE (`processors/code_aware_translator.py`)

**Purpose**: Code-aware JSON translation (visible text ↔ {t.path} placeholders)

#### Key Features (Lines 1-100)
- **Preserves code structure**: Only translates visible text, not code
- **JSX-aware**: Handles JSX text nodes, string literals
- **Placeholder format**: `{root.pages.home.title}` (configurable root)
- **Bidirectional**: Translate to placeholders, reverse to original text
- **Smart quote handling**: Normalizes curly quotes → straight quotes

#### Class Design (Lines 25-76)
```python
class CodeAwareJSONTranslator:
    # Regexes
    _re_jsx_tag = re.compile(r"<[^>]*>")  # JSX tag regions
    _re_placeholder = re.compile(r"\{([A-Za-z_]\w*)(?:\.[A-Za-z0-9_]+)+\}")
    _re_string = re.compile(...)  # String literals
    
    # Quote normalization table
    _SMART_TO_STRAIGHT = str.maketrans("''" + '""' + "‛‟", "'''" + '"""')
    
    def __init__(self, dictionary: dict, root_name: str = "t"):
        self.root = root_name  # Default: "t" → {t.path}
        self.flat = self._flatten(dictionary)  # Nested → flat paths
        
        # Build variants map (multiple textual forms → key)
        # Sorted by length (desc) to match longest phrases first
```

#### Translation Strategy
1. **Flatten dictionary**: `{"pages": {"home": {"title": "Welcome"}}}` → `"pages.home.title": "Welcome"`
2. **Generate variants**: Create multiple textual representations (normalized quotes, etc.)
3. **Sort by length**: Longest phrases match first (avoid partial overlaps)
4. **Scan text**: Find phrases, replace with `{root.path}`
5. **Protect regions**: Skip JSX tags, existing placeholders, code blocks

#### Translation Scope (Lines 33-39)
```python
# Translate:
- JSX text nodes (between '>' and '<')
- String literals in code

# SKIP:
- Anything inside {...} expressions
- Inside JSX tags/attributes (<Tag ...>)
- Type annotations (React.ReactNode)
- Existing placeholders ({root.*})
```

#### Design Patterns Identified
1. **Strategy Pattern**: Code-aware translation is one strategy
2. **Template Method**: `_flatten()`, `_variants_for_value()` helper methods
3. **Regex Patterns**: Pre-compiled regexes for performance
4. **Normalization**: Quote normalization before matching
5. **Longest Match First**: Sorted variants prevent partial matches
6. **Fail-Safe**: Protects existing placeholders from re-translation

#### Import Tree Position (Lines 10-15)
```python
# Phase 3.11 - Import Tree Analogy: FOLHA (LEAF)
# - Não importa arquivos do projeto
# - Importa apenas bibliotecas padrão (re, typing)
# - Fornece funcionalidade atômica (processamento de texto)
# - Totalmente reutilizável e testável
```

**Verification**: CodeAwareJSONTranslator is a **Leaf** node (no internal dependencies).

#### Integration Points
- **JSON Translate dock**: Uses this processor for translation
- **AI Processor**: May use for prompt translation
- **Not a plugin**: This is a **processor** (internal module), not a plugin

---

## 🎯 KEY INSIGHTS

### 1. Plugin vs Processor vs Extractor (Terminology)

| Type         | Location       | Purpose                           | Loading        |
|--------------|----------------|-----------------------------------|----------------|
| **Plugin**   | `plugins/`     | User extensions (optional)        | Dynamic (runtime)|
| **Processor**| `src/processors/` | Internal text processing       | Static (import) |
| **Extractor**| `src/extractors/` | Parse code (JSX, TS, etc.)     | Static (import) |

**Key distinction**:
- **Plugins**: External, optional, dynamically loaded, use PluginBase API
- **Processors/Extractors**: Internal, required, statically imported, no plugin interface

**Why the confusion?**
- All three use **strategy-like patterns** (interchangeable algorithms)
- Processors/Extractors could be **refactored as plugins** in the future
- Current design: Processors/Extractors are **core features**, plugins are **extensions**

### 2. Plugin Lifecycle (5 States)

```
┌─────────────┐  discover_plugins()  ┌──────────────┐
│ Undiscovered│ ──────────────────>  │  Discovered  │
└─────────────┘                      └──────┬───────┘
                                            │ load_plugin()
                                            v
┌─────────────┐  unload_plugin()     ┌──────────────┐
│  Unloaded   │ <──────────────────  │    Loaded    │
└─────────────┘                      └──────┬───────┘
                                            │ activate_plugin()
                                            v
                                     ┌──────────────┐
                                     │   Activated  │
                                     └──────┬───────┘
                                            │ deactivate_plugin()
                                            v
                                     ┌──────────────┐
                                     │ Deactivated  │
                                     └──────────────┘
```

**Transitions**:
1. **Undiscovered → Discovered**: Scan plugins/ for plugin.json
2. **Discovered → Loaded**: Import module, instantiate class
3. **Loaded → Activated**: Call plugin.activate(app)
4. **Activated → Deactivated**: Call plugin.deactivate(app) (optional)
5. **Loaded/Deactivated → Unloaded**: Remove from memory

**Caching**: Loaded plugins stay in memory until unload_plugin().

### 3. Plugin API Surface (PluginBase)

**Required**:
- `activate(app)` - Must implement

**Optional**:
- `deactivate(app)` - Cleanup (has default)
- `on_event(name, data)` - Event handler

**Helpers** (8 methods):
- `register_dock()` - Add custom dock
- `add_menu_item()` - Add menu entry
- `get_setting()` - Read plugin setting
- `set_setting()` - Write plugin setting
- `show_message()` - Display message box
- `_registered_docks` - Track docks (internal)
- `_registered_actions` - Track actions (internal)

**Properties**:
- `name`, `description`, `version` - Metadata (override in subclass)

**Total API**: 3 hooks + 8 helpers = **11 methods**

### 4. Event System (Broadcast Pattern)

**Event flow**:
```
App event occurs (e.g., file opened)
    ↓
plugin_loader.emit_event("file_opened", {"path": "data.json"})
    ↓
For each active plugin:
    if plugin.on_event exists:
        plugin.on_event("file_opened", {"path": "data.json"})
```

**Characteristics**:
- **Broadcast**: All plugins receive all events
- **Optional**: Plugins not required to implement on_event()
- **Filtering**: Plugins filter by event_name internally
- **No return values**: Events are notifications (not commands)
- **Error isolation**: Exception in one plugin doesn't affect others

**Common events** (5 documented):
1. `file_opened` - File loaded in editor
2. `file_saved` - File saved to disk
3. `search_completed` - JSON search finished
4. `rewrite_completed` - JSON rewriter finished
5. `ai_request_completed` - AI processing done

### 5. Fail-Safe Design (Throughout)

**PluginLoader**:
- Missing plugin.json → Skip (no error)
- Malformed JSON → Print error + continue
- Plugin load error → Catch, log, emit signal
- Plugin activation error → Catch, log, don't crash
- Plugin event error → Catch, log, continue to next plugin

**PluginBase**:
- Default deactivate() → Cleanup UI elements
- Missing deactivate() → No error
- Missing on_event() → No error

**Result**: **One broken plugin never crashes the application.**

### 6. Settings Persistence (QSettings Integration)

**PluginLoader**:
- `plugins/<id>/enabled` - Boolean flag

**PluginBase**:
- `plugins/<name>/<key>` - Plugin-specific settings

**Storage location** (Linux):
```
~/.config/Clarify/Clarify.conf

[plugins]
export_csv/enabled=true
my_plugin/enabled=false
my_plugin/my_setting=value
```

**Shared storage**: Same QSettings instance as other managers (LayoutManager, PresetsManager).

---

## 🔍 DESIGN PATTERNS CATALOG

### Session 11 Patterns Identified (15 total)

#### Creational Patterns (2)
1. **Plugin Pattern** (PluginLoader)
   - Core architecture for dynamic plugin loading
   - Discovery → Load → Activate lifecycle

2. **Lazy Loading** (PluginLoader)
   - Plugins loaded only when activated
   - Reduces startup time

#### Structural Patterns (5)
3. **Facade Pattern** (PluginLoader, PluginBase)
   - Simple API hides Qt/importlib complexity
   - `activate_all_plugins()` one-liner

4. **Registry Pattern** (PluginLoader)
   - `self.plugins` dict stores loaded instances
   - `self.metadata` dict stores plugin info

5. **Package Pattern** (extractors/__init__.py)
   - `__all__` defines public API
   - Clean interface exports

6. **Introspection** (PluginLoader)
   - Runtime discovery of plugin class
   - `dir()` + `isinstance()` + `hasattr()`

7. **Namespacing** (PluginBase)
   - Settings prefixed with `plugins/<name>/`
   - Avoids conflicts between plugins

#### Behavioral Patterns (8)
8. **Template Method** (PluginBase)
   - Base class defines skeleton
   - Subclasses override activate()

9. **Hook Method** (PluginBase)
   - deactivate() and on_event() are optional hooks
   - Default implementations provided

10. **Observer Pattern** (PluginLoader Qt Signals)
    - plugin_loaded, plugin_activated, plugin_error
    - Observers can react to plugin events

11. **Event Bus** (PluginLoader.emit_event)
    - Broadcast events to all plugins
    - Decouples app from plugins

12. **Strategy Pattern** (Processors, Extractors)
    - Interchangeable algorithms
    - CodeAwareJSONTranslator is one strategy

13. **Graceful Degradation** (PluginLoader)
    - Errors in one plugin don't affect others
    - Fail-safe error handling

14. **Resource Management** (PluginBase.deactivate)
    - Automatic cleanup of UI elements
    - Tracks registered docks/actions

15. **Longest Match First** (CodeAwareJSONTranslator)
    - Sort variants by length (desc)
    - Prevents partial phrase matches

---

## 🔗 INTEGRATION POINTS

### 1. Startup Sequence (app.py)
```python
# During MainWindow.__init__
plugin_loader = PluginLoader(self)
plugin_loader.discover_plugins()
plugin_loader.activate_all_plugins()

# Emit events during app operations
plugin_loader.emit_event("file_opened", {"path": path})
```

### 2. Plugin Directory Structure
```
clarify/
  plugins/                    # User plugins (dynamic)
    my_plugin/
      plugin.json             # Metadata (required)
      main.py                 # Entry point (PluginBase subclass)
      requirements.txt        # pip dependencies
      README.md
    export_csv/
      plugin.json
      example_export_csv.py
  
  src/
    plugin_loader.py          # Plugin system
    plugins/
      plugin_base.py          # Base class
    processors/               # Internal processors (static)
      code_aware_translator.py
    extractors/               # Internal extractors (static)
      jsx_parser.py
      extractor.py
```

### 3. Plugin vs Core Feature
| Aspect          | Plugin                     | Core Feature (Processor/Extractor) |
|-----------------|----------------------------|------------------------------------|
| **Location**    | `plugins/<name>/`          | `src/processors/`, `src/extractors/`|
| **Loading**     | Dynamic (PluginLoader)     | Static (import)                    |
| **Interface**   | PluginBase                 | Direct class usage                 |
| **Required**    | Optional                   | Required for app                   |
| **Distribution**| Separate packages          | Bundled with app                   |

### 4. Event Flow (file_opened example)
```python
# 1. User opens file in editor
editor_dock.load_file("data.json")

# 2. Emit event
plugin_loader.emit_event("file_opened", {"path": "data.json"})

# 3. All plugins receive event
for plugin in active_plugins:
    plugin.on_event("file_opened", {"path": "data.json"})

# 4. Plugins react (optional)
class MyPlugin(PluginBase):
    def on_event(self, event_name, data):
        if event_name == "file_opened":
            print(f"File opened: {data['path']}")
            # Could: auto-save, log activity, update UI, etc.
```

### 5. Settings Hierarchy
```
QSettings ("Clarify", "Clarify")
├── Layouts/                    # LayoutManager
│   └── Standard/
│       ├── geometry
│       └── state
├── operation_presets           # PresetsManager
├── plugins/                    # PluginLoader + PluginBase
│   ├── export_csv/
│   │   └── enabled
│   └── my_plugin/
│       ├── enabled
│       └── custom_setting
└── LastLayout                  # LayoutManager
```

---

## 📊 CUMULATIVE STATISTICS

### Code Coverage Progress
- **Phase 3 Session 11**: 5 files, 1,046 LOC
- **Phase 3 Sessions 8-11**: 20 files, 5,538 LOC
- **Phase 2 (Sessions 4-7)**: 18 files, 4,847 LOC
- **Phase 1 (Sessions 1-3)**: 9 files, 6,947 LOC
- **Total studied**: 47 files, 17,332 LOC
- **Total codebase**: 279 Python files, 83,619 LOC
- **Coverage**: 20.7% (vs 19.5% before Session 11)

### Design Patterns Tally
- **Session 11**: 15 patterns identified
- **Phase 3 Sessions 8-11**: 50 patterns (15 + 15 + 15 + 5)
- **Phase 2**: 44 patterns
- **Phase 1**: 27 patterns
- **Total cataloged**: 121 patterns

### Session Duration
- **Predicted**: 45 minutes
- **Actual**: ~40 minutes (5 files, focused on architecture)
- **Efficiency**: 113% (completed faster than estimated)

---

## 🎓 LEARNING OUTCOMES

### 1. Dynamic Module Loading (importlib.util)
**Python technique** for runtime module import:
```python
spec = importlib.util.spec_from_file_location("module_name", "/path/to/file.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module  # Register in sys.modules
spec.loader.exec_module(module)  # Execute module code
```

**Use cases**:
- Plugin systems
- Hot-reloading
- Dynamic feature loading
- Conditional imports based on config

**Clarify usage**: Loads plugins from arbitrary directories at runtime.

### 2. Plugin Architecture Patterns
**Discovery**:
- Scan directory for metadata files
- Parse metadata (JSON, YAML, etc.)
- Validate structure

**Loading**:
- Dynamic import
- Introspection to find plugin class
- Instantiation

**Activation**:
- Call lifecycle hook (activate)
- Provide app context
- Error handling

**Best practices**:
1. **Metadata file**: Separate from code (plugin.json)
2. **Base class**: Define interface (PluginBase)
3. **Error isolation**: Catch per-plugin exceptions
4. **Settings persistence**: Enable/disable flags
5. **Event system**: Decouple plugins from app

### 3. Qt Signals for Plugin Communication
**Pattern**:
```python
class PluginLoader(QObject):
    plugin_loaded = Signal(str)      # Notify UI
    plugin_activated = Signal(str)   # Update status
    plugin_error = Signal(str, str)  # Show errors
```

**Benefits**:
- Loose coupling (observers react to signals)
- UI can display plugin status
- No direct callback dependencies

**Clarify usage**: Plugin manager UI can display loading progress.

### 4. Introspection Techniques
**Find plugin class** (without knowing name):
```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if (isinstance(attr, type) and          # Is a class
        hasattr(attr, 'activate') and       # Has activate method
        attr.__name__ != 'PluginBase'):     # Not base class
        plugin_class = attr
        break
```

**Alternative approaches**:
1. **Naming convention**: Require class name = "Plugin"
2. **Decorator**: `@register_plugin` marks plugin class
3. **Metaclass**: Auto-registration on class definition

**Clarify choice**: Introspection (most flexible, no naming constraints).

### 5. Plugin vs Internal Module Design
**When to use plugins**:
- **User-extensible** features
- **Optional** functionality
- **Third-party** contributions
- **Runtime** enable/disable

**When to use internal modules**:
- **Core** features (always needed)
- **Performance-critical** (avoid dynamic loading overhead)
- **Tightly coupled** to app architecture
- **Security-sensitive** (avoid arbitrary code execution)

**Clarify design**:
- **Plugins**: User extensions (export CSV, custom workflows)
- **Processors**: Core text processing (translation, code-aware)
- **Extractors**: Core parsing (JSX, TypeScript)

**Rationale**: Keep core features fast and secure, allow user extensions for flexibility.

---

## 🚀 NEXT STEPS

### Phase 3 Complete! (4/4 Sessions Done)
- ✅ Session 8: JSON Search System (792 LOC)
- ✅ Session 9: GUI Dock Components (2,128 LOC)
- ✅ Session 10: Core Utilities & Managers (1,572 LOC)
- ✅ Session 11: Plugin & Extension System (1,046 LOC)

**Total Phase 3**: 20 files, 5,538 LOC, 50 patterns

### Create Phase 3 Summary
1. **Consolidate findings** from Sessions 8-11
2. **Update cumulative statistics** (coverage, patterns)
3. **Integration map** (how subsystems connect)
4. **Commit to COM4-code-study branch**

### Decision Point (After Phase 3 Summary)
**Options**:
- **Option A**: Start v2.9.116 Phase 4 implementation (ACTION_PLAN ready)
- **Option B**: Continue studying (Phase 4 - more modules)
- **Option C**: Validation testing before implementation

**Current coverage**: 20.7% (47/279 files, 17,332/83,619 LOC)

**Recommendation**: **Option A** - We have sufficient understanding:
- Core architecture (Phase 1)
- Configuration & data processing (Phase 2)
- JSON search, GUI, utilities, plugins (Phase 3)
- **Action plan ready** (ACTION_PLAN_PHASE4_FILE_EXPLORER.md)
- **Protocol guideline**: "incremental as needed" - we have what's needed for Phase 4

---

## 📝 METADATA

**Session 11 Metrics**:
- Files studied: 5
- LOC analyzed: 1,046
- Patterns identified: 15
- Duration: ~40 minutes
- Notes size: ~32KB (this file)

**Phase 3 Complete**:
- Sessions: 4 (8, 9, 10, 11)
- Files: 20
- LOC: 5,538
- Patterns: 50
- Duration: ~3.5 hours

**Cumulative Progress**:
- Files: 47/279 (16.8%)
- LOC: 17,332/83,619 (20.7%)
- Patterns: 121 unique
- Study time: ~10.5h total (Phases 1-3)
- Phases complete: 3/3

**Quality Indicators**:
- ✅ Plugin system follows industry patterns (discovery → load → activate)
- ✅ Fail-safe design (one broken plugin doesn't crash app)
- ✅ Clean API (PluginBase provides simple interface)
- ✅ Settings persistence integrated with QSettings
- ✅ Event system for loose coupling
- ✅ Introspection for flexibility (no naming constraints)

---

**END OF SESSION 11 NOTES**
**END OF PHASE 3 STUDY**
