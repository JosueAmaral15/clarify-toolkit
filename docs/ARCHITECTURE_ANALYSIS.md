# CLARIFY PROJECT ARCHITECTURE ANALYSIS
## Comprehensive Study of Core Systems and Managers

**Project Version**: 2.9.117 (Qt6/Linux compatibility improvements)  
**Author**: Josué Amaral  
**Language**: Python 3 with PySide6 GUI  
**Repository**: https://github.com/JosueAmaral15/clarify

---

## 1. APPLICATION INITIALIZATION FLOW

### 1.1 Entry Points

#### **`src/__main__.py`** (15 lines)
- **Purpose**: Module-level entry point allowing `python -m src`
- **Responsibility**: Imports and delegates to `app.main()`
- **Key Pattern**: Thin wrapper - minimal code, delegates to main app

```python
import sys
from .app import main
if __name__ == "__main__":
    sys.exit(main())
```

#### **`src/__init__.py`** (47 lines)
- **Purpose**: Package initialization and lazy imports
- **Responsibilities**:
  - Version metadata (`__version__ = "2.9.46"`)
  - Lazy import of main() to avoid GUI dependencies at module level
  - Package docstring with usage examples
- **Design Pattern**: **Lazy Loading** - defers PySide6 import until needed
- **Code Quality Observation**: Good separation of concerns, module works with/without GUI

#### **`src/app.py`** (2700+ lines)
- **Purpose**: Main application GUI orchestrator (MainWindow class)
- **Key Responsibility**: 
  - **Initialization**: Windows creation, all managers startup
  - **Orchestration**: Coordinates between UI docks and backend processors
  - **UI Management**: Menu bar, shortcuts, dock layout, theme application
- **Design Pattern**: **Composite + Facade** - MainWindow acts as facade to all systems
- **Initialization Steps**:
  1. Qt window flags configuration (v2.9.117 Linux fix)
  2. Call `InitializationManager.initialize_all(self, app)`
  3. Install global event filters (horizontal scroll handling)
  4. Restore layout from previous session
  5. Force UI geometry update and process events
  6. Apply accessibility features
  7. Restore tab state
  8. Initialize all tabs (force render non-visible tabs)
  9. Auto-check for updates

---

## 2. CORE MANAGER ARCHITECTURE

### Architecture Overview
```
MainWindow (Facade)
    ├── SettingsManager (Singleton)
    ├── ConfigManager (YAML-based configuration)
    ├── LayoutManager (Dock layout persistence)
    ├── ThemeManager (Light/Dark/System theming)
    ├── ShortcutManager (Keyboard shortcuts)
    ├── PluginLoader (Dynamic plugin system)
    ├── HistoryManager (Operation history)
    ├── MigrationManager (Version migrations)
    ├── UpdateChecker (GitHub Releases API)
    ├── AccessibilityManager (Screen reader & a11y)
    ├── TutorialAssistant (Gemini AI chatbot)
    └── Plugin System (Custom plugins)
```

---

### 2.1 SETTINGS MANAGER
**File**: `src/settings_manager.py` (150 lines)

#### Purpose
Persistent application settings storage with JSON serialization.

#### Class Structure
```python
class SettingsManager:
    DEFAULTS = {
        "theme": "system",
        "language": "en",
        "recent_files": [],
        "custom_shortcuts": {},
        # ... 12 more settings
    }
```

#### Key Responsibilities
1. **Load/Save**: JSON file at `~/.clarify_settings.json`
2. **Recent Files Management**: MRU list with max 10 items
3. **Custom Shortcuts**: Keyboard shortcut customization (v2.9.33)
4. **Defaults Merging**: New settings merged on load

#### Design Patterns
- **Singleton**: Global `_settings_instance` with `get_settings()` function
- **Strategy**: Different storage strategies possible (currently JSON)

#### Key Methods
```python
get(key, default)           # Dot notation: "theme", "recent_files"
set(key, value)             # Immediately persists
add_recent_file(path)       # MRU management with deduplication
get_custom_shortcuts()      # Returns Dict[str, str]
reset_to_defaults()         # Restore defaults and save
```

#### Code Quality Observations
- ✅ Simple, focused responsibility
- ✅ Error handling on load with graceful fallback
- ✅ File existence checks before read
- ⚠️ No thread safety (file writes not atomic)
- ⚠️ No validation of setting values (could be improved with schema)

---

### 2.2 LAYOUT MANAGER
**File**: `src/layout_manager.py` (297 lines)

#### Purpose
Manages customizable application layouts (dock positions, sizes, visibility).

#### Class Structure
```python
class LayoutManager:
    PRESET_COMPACT = "Compact"
    PRESET_STANDARD = "Standard"
    PRESET_ADVANCED = "Advanced"
    
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.settings = QSettings("Clarify", "ClarifyApp")  # Qt persistence
        self.docks = {}  # dock_name → QDockWidget
```

#### Key Responsibilities
1. **Dock Registration**: Register docks by name (`register_dock()`)
2. **Layout Persistence**: Save/load full window geometry and dock state
3. **Presets**: 3 built-in layouts (Compact, Standard, Advanced)
4. **Auto-Restoration**: `restore_last_layout()` at app startup

#### Layout Presets
| Preset | Visible Docks | Use Case |
|--------|---------------|----------|
| **Compact** | Editor only | Minimal, focused |
| **Standard** | Editor, Search, Replace, Rewriter | Balanced default |
| **Advanced** | All docks | Power users |

#### Design Patterns
- **Strategy**: Different preset strategies (apply_preset_compact, etc.)
- **Memento**: QSettings stores window state snapshots
- **Factory**: `get_saved_layouts()` returns custom layout names

#### Key Methods
```python
register_dock(name, widget)         # Track dock for management
save_layout(name)                   # Save current state
load_layout(name)                   # Restore saved state
apply_preset(name)                  # Switch to preset
restore_last_layout()               # Auto-restore on startup
```

#### Dependencies
- Qt Framework (QSettings, QMainWindow, QDockWidget)
- Logger (`from .utils.logger import get_logger`)

#### Code Quality Observations
- ✅ Clear separation: save/load vs presets vs restore
- ✅ Fallback to Standard preset if restore fails
- ✅ Proper group management with QSettings
- ⚠️ No validation if dock doesn't exist during load
- ⚠️ Could use context managers for settings groups

---

### 2.3 THEME MANAGER
**File**: `src/theme_manager.py` (524 lines)

#### Purpose
Apply consistent application-wide theming (Light, Dark, System).

#### Class Structure
```python
class ThemeManager:
    @staticmethod
    def apply_theme(app: QApplication, mode: ThemeMode):
        # ThemeMode = Literal["system", "light", "dark"]
```

#### Themes Provided
1. **Light Theme**
   - Background: #FAFAFA (off-white)
   - Text: #1E1E1E (dark gray)
   - Highlight: #0078D7 (VS Code blue)
   - Comprehensive QSS for all widget types

2. **Dark Theme**
   - Background: #2D2D30 (dark gray)
   - Text: #CCCCCC (light gray)
   - Highlight: #007ACC (VS Code blue accent)

3. **System Theme**
   - Use OS defaults via Qt Fusion style
   - Platform-native appearance

#### Design Patterns
- **Strategy**: Different theme application strategies
- **Static Utility**: All methods are static (no state)

#### Key Methods
```python
apply_theme(app, mode)              # Main entry point
_apply_light_theme(app)             # Light implementation
_apply_dark_theme(app)              # Dark implementation
_apply_system_theme(app)            # System implementation
```

#### Code Coverage
- QPalette styling (Window, Button, Text, Highlight, etc.)
- QSS stylesheets for:
  - GroupBox
  - LineEdit, PlainTextEdit, TextEdit, SpinBox
  - Buttons (normal, hover, pressed, disabled)
  - Checkboxes and Radio buttons
  - ComboBox, TreeWidget, etc.

#### Code Quality Observations
- ✅ Comprehensive palette coverage
- ✅ Static utility prevents accidental state issues
- ✅ Graceful application to full app at once
- ⚠️ Very large QSS strings (could be externalized to .qss files)
- ⚠️ Color codes hardcoded (no centralized color scheme)
- 💡 Could benefit from CSS-like hierarchy/inheritance

---

### 2.4 SHORTCUT MANAGER
**File**: `src/shortcut_manager.py` (316 lines)

#### Purpose
Define and manage keyboard shortcuts with customization support.

#### Class Structure
```python
class ShortcutManager:
    SHORTCUTS = {
        # File operations
        "new_file": ("Ctrl+N", "New file"),
        "open_file": ("Ctrl+O", "Open file"),
        # ... 40+ shortcuts total
    }
    
    OS_SHORTCUTS = {
        "Linux": ["Ctrl+Alt+T", "Ctrl+Alt+L", ...],
        "Windows": ["Win+L", "Ctrl+Shift+Esc", ...],
        "Darwin": ["Cmd+Q", "Cmd+H", ...],
    }
    
    _custom_shortcuts: Dict[str, str] = {}  # Overlay for customization
```

#### Shortcuts Organization
**File Operations**: new, open, save, close, exit  
**Edit Operations**: copy, paste, cut, select, undo, redo, find, replace  
**Navigation**: next/prev dock, jump to dock 1-9  
**View**: fullscreen, history toggle, zoom in/out  
**Processing**: process (F5), interrupt (Esc), clear  
**Help**: F1, tutorials, about  

#### Key Responsibilities
1. **Shortcut Registry**: Central SHORTCUTS dict
2. **Custom Shortcuts**: Support overrides via `_custom_shortcuts`
3. **OS Awareness**: Track platform shortcuts that might conflict
4. **QAction Integration**: Helper to apply shortcuts to UI actions

#### Design Patterns
- **Registry**: SHORTCUTS dict acts as shortcut registry
- **Overlay**: `_custom_shortcuts` overlays defaults
- **Static Utility**: All methods are @classmethod

#### Key Methods
```python
get_shortcut(action_name)           # Get (shortcut_str, description)
get_default_shortcut(action_name)   # Get default, ignoring customization
get_key_sequence(action_name)       # Get QKeySequence object
add_shortcut_to_action(action, name) # Apply to QAction
get_all_shortcuts()                 # Dict with all shortcuts
```

#### Code Quality Observations
- ✅ Comprehensive keyboard coverage (~40 shortcuts)
- ✅ OS-specific conflict tracking
- ✅ Customization support baked in
- ✅ Good separation: get_shortcut() vs get_default_shortcut()
- ⚠️ `_custom_shortcuts` is mutable class variable (threading risk)
- ⚠️ No persistence of custom shortcuts to disk yet
- 💡 Could benefit from shortcut validation/conflict detection

---

### 2.5 CONFIG MANAGER
**File**: `src/config_manager.py` (450+ lines)

#### Purpose
Centralized YAML-based configuration with validation, migration, and backup.

#### Class Structure
```python
class ConfigManager:
    DEFAULTS = {
        "app": {
            "theme": "system",
            "language": "en",
            "check_updates_on_startup": True,
        },
        "logging": {
            "level": "INFO",
            "max_file_size_mb": 10,
            "backup_count": 5,
        },
        "performance": {
            "thread_pool_size": 4,
            "max_file_size_mb": 50,
        },
        "ai": {
            "default_provider": "OpenAI",
            "remember_api_keys": False,  # Security!
        },
        "editor": {
            "font_family": "Consolas",
            "font_size": 12,
        },
        "paths": {
            "default_directory": str(Path.home()),
        },
    }
    
    SCHEMA = {...}  # JSON Schema for validation
```

#### Key Responsibilities
1. **YAML I/O**: Load/save config.yaml with comments
2. **Validation**: JSON Schema validation against SCHEMA
3. **Migration**: Automatic migration from QSettings/JSON
4. **Backup**: Creates timestamped backups before overwrites
5. **Dotted Access**: Supports "app.theme", "logging.level", etc.
6. **Error Handling**: Graceful fallback to defaults on error

#### Config File Location
`~/.config/clarify/config.yaml`

#### Design Patterns
- **Strategy**: Different storage backends (could extend)
- **Adapter**: Bridges old SettingsManager with new ConfigManager
- **Observer**: Could notify listeners of config changes
- **Template Method**: `_load_or_create()` handles initialization flow

#### Key Methods
```python
get(key, default)                   # Dot notation: "app.theme"
set(key, value, save=True)          # Update and optionally persist
save()                              # Persist to YAML
reset_to_defaults()                 # Clear and use defaults
get_all()                           # Return full config dict
migrate_from_qsettings()            # Upgrade from old format
```

#### Validation
- JSON Schema with:
  - Enum constraints ("system", "light", "dark")
  - Range constraints (thread_pool: 1-16, font_size: 8-24)
  - Pattern matching (language: "^[a-z]{2}(-[a-z]{2})?$")

#### Code Quality Observations
- ✅ Centralized, versioned config (not QSettings)
- ✅ Comprehensive validation via JSON Schema
- ✅ Auto-backup before overwrites
- ✅ Dotted key access is elegant
- ✅ Graceful migration from legacy formats
- ✅ Security-minded (remember_api_keys defaults to False)
- ⚠️ Large config definition (could be split)
- ⚠️ No hot-reload (changes require restart)
- ⚠️ No config diff/merge utilities

---

### 2.6 MIGRATION MANAGER
**File**: `src/migration_manager.py` (272 lines)

#### Purpose
Automatic version migrations for QSettings and config.yaml when app structure changes.

#### Class Structure
```python
class MigrationManager:
    CURRENT_VERSION = "2.9.91"
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.migrations_dir = Path(__file__).parent / "migrations"
```

#### Key Responsibilities
1. **Version Detection**: Read current app version from QSettings or config.yaml
2. **Migration Discovery**: Scan `src/migrations/` for v*.py files
3. **Migration Execution**: Run pending migrations in version order
4. **Backup Creation**: Automatic backups before migrations
5. **Logging**: All migrations logged to `~/.clarify/logs/migrations.log`

#### Migration System Design
```
migrations/
├── base.py              # Base Migration class
├── v2_9_90.py          # Migration for v2.9.90
├── v2_9_91.py          # Migration for v2.9.91
└── __init__.py
```

#### Key Methods
```python
get_current_version()               # Read version from QSettings/config
set_current_version(version)        # Update version after migration
discover_migrations()               # Scan and load all migrations
backup_before_migration()           # Create backup snapshots
run_pending_migrations()            # Execute all pending migrations
_version_tuple(version)             # Convert "2.9.91" → (2, 9, 91)
```

#### Design Patterns
- **Plugin System**: Migrations discovered dynamically
- **Strategy**: Each migration implements its own logic
- **Fail-Safe**: Backups used for manual recovery (no rollback)

#### Error Handling
- Non-fatal: Continues even if individual migration fails
- Logging: All operations logged to file + console
- Graceful Degradation: Falls back to defaults if migration fails

#### Code Quality Observations
- ✅ Good separation: migration discovery vs execution
- ✅ Versioning uses semantic tuple comparison
- ✅ Comprehensive logging setup
- ✅ Safe fallback to defaults on error
- ✅ Backups created before any changes
- ⚠️ No rollback capability (backups are manual recovery only)
- ⚠️ Could validate migration prerequisites
- 💡 Could benefit from dry-run mode

---

### 2.7 PLUGIN LOADER
**File**: `src/plugin_loader.py` (319 lines)

#### Purpose
Dynamic plugin system with discovery, loading, and lifecycle management.

#### Class Structure
```python
class PluginMetadata:
    """Metadata from plugin.json file."""
    def __init__(self, data: dict, plugin_dir: Path):
        self.id = data["id"]
        self.name = data["name"]
        self.version = data["version"]
        self.entry_point = data["entry_point"]
        self.dependencies = data["dependencies"]
        self.enabled = data["enabled"]

class PluginLoader(QObject):
    """Main plugin loader with QObject signals."""
    
    plugin_loaded = Signal(str)       # Signal: plugin_id
    plugin_activated = Signal(str)    # Signal: plugin_id
    plugin_error = Signal(str, str)   # Signal: plugin_id, error_msg
```

#### Plugin Structure
```
plugins/
├── my-plugin/
│   ├── plugin.json          # Metadata
│   ├── main.py              # Entry point
│   ├── hooks.py             # Event hooks
│   └── requirements.txt      # Dependencies
└── another-plugin/
    ├── plugin.json
    └── main.py
```

#### plugin.json Format
```json
{
    "id": "json-validator",
    "name": "JSON Validator",
    "version": "1.0.0",
    "description": "Validate JSON files",
    "author": "Someone",
    "entry_point": "main.py",
    "dependencies": ["jsonschema>=4.0"],
    "enabled": true
}
```

#### Key Responsibilities
1. **Discovery**: Scan `plugins/` for plugin.json files
2. **Loading**: Dynamically import plugin modules
3. **Lifecycle**: activate, deactivate, reload
4. **Event System**: Emit hooks (file_opened, search_completed, etc.)
5. **Settings**: Store enabled/disabled state in QSettings

#### Design Patterns
- **Factory**: `load_plugin()` creates plugin instances
- **Observer**: Signal system for plugin events
- **Registry**: `self.plugins` dict stores loaded plugins
- **Dependency Injection**: Pass app instance to plugins

#### Key Methods
```python
discover_plugins()                  # Find all plugins
load_plugin(plugin_id)              # Load single plugin
activate_plugin(plugin_id)          # Enable and initialize
deactivate_plugin(plugin_id)        # Disable
emit_event(event_name, data)        # Trigger hooks
get_all_plugins()                   # Return all loaded
```

#### Hook System
Plugins can implement hooks:
- `on_file_opened(path)`
- `on_search_completed(results)`
- `on_ui_loaded()`
- `on_app_closing()`

#### Code Quality Observations
- ✅ Good separation: metadata vs loading
- ✅ Signals for loose coupling
- ✅ Error handling with Signal emission
- ✅ Dynamic discovery (no hardcoding)
- ✅ QSettings for persistence
- ⚠️ Could validate dependencies
- ⚠️ No plugin isolation (runs in main process)
- ⚠️ Error recovery could be better
- 💡 Could add plugin sandboxing/permissions

---

### 2.8 ACCESSIBILITY MANAGER
**File**: `src/accessibility_manager.py` (200+ lines)

#### Purpose
Comprehensive accessibility features (WCAG AAA compliance).

#### Class Structure
```python
class AccessibilityManager:
    MIN_FONT_SIZE = 8
    DEFAULT_FONT_SIZE = 10
    MAX_FONT_SIZE = 24
```

#### Key Responsibilities
1. **Screen Reader Support**: Set accessible names/descriptions on widgets
2. **Focus Indicators**: Apply visible focus styling (2px blue border)
3. **Font Scaling**: Dynamic font size adjustment (Ctrl+Scroll)
4. **Tab Order**: Configure keyboard navigation
5. **Color Contrast**: Ensure WCAG AAA levels

#### Design Patterns
- **Static Utility**: All methods are @staticmethod
- **Strategy**: Different a11y features as separate methods

#### Key Methods
```python
set_accessible_widget(widget, name, description)
apply_focus_indicators(app)
get_font_size(settings)
set_font_size(size, settings)
apply_font_size(app, size)
increase_font_size(app, settings)
decrease_font_size(app, settings)
```

#### Accessibility Features
- **Focus Indicators**: 
  - 2px solid #007ACC border
  - Applied globally via QSS
  - Visible on Tab navigation

- **Font Scaling**:
  - Range: 8-24 points
  - Persisted to QSettings
  - Applied to entire app

- **Screen Readers**:
  - Accessible names (e.g., "Run JSON Rewriter")
  - Descriptions (e.g., "Execute rewrite operation")

#### Code Quality Observations
- ✅ WCAG AAA compliance mindset
- ✅ Good separation of concerns
- ✅ Font size bounds checking
- ⚠️ No keyboard shortcut cheat sheet
- ⚠️ Could add high contrast mode
- 💡 Could add screen reader testing utilities

---

### 2.9 UPDATE CHECKER
**File**: `src/update_checker.py` (267 lines)

#### Purpose
Check for new Clarify versions from GitHub Releases API.

#### Class Structure
```python
class UpdateChecker:
    GITHUB_API_URL = "https://api.github.com/repos/JosueAmaral15/clarify/releases/latest"
    CACHE_DURATION_HOURS = 24
    CACHE_FILE = Path.home() / ".cache" / "clarify" / "update_check.json"
```

#### Key Responsibilities
1. **Version Comparison**: Semantic version checking
2. **API Integration**: GitHub Releases API with User-Agent header
3. **Caching**: 24-hour cache to avoid rate limits
4. **Error Handling**: Offline-friendly, no console spam
5. **Release Info**: Return version, URL, changelog, publish date

#### Design Patterns
- **Strategy**: Cache-first lookup, fallback to API
- **Facade**: Simple check_for_updates() entry point

#### Key Methods
```python
check_for_updates(force=False)      # (has_update, release_info) tuple
_fetch_latest_release()             # Call GitHub API
_is_newer_version(latest)           # Semantic version comparison
_load_cache()                        # Check/load cache
_save_cache(has_update, info)       # Persist to cache
```

#### Return Format
```python
{
    "version": "2.9.45",
    "url": "https://github.com/.../releases/tag/v2.9.45",
    "changelog_url": "https://github.com/.../CHANGELOG.md#v2945",
    "published_at": "2025-01-20T10:00:00Z",
    "body": "Release notes..."
}
```

#### Error Handling
- Network errors: Return (False, None)
- 404: Silently ignored (no releases yet)
- Invalid version format: Assume not newer
- Offline: Use cached result or (False, None)

#### Code Quality Observations
- ✅ Semantic version comparison is correct
- ✅ Cache prevents rate limiting
- ✅ Graceful offline handling
- ✅ No console spam on errors
- ⚠️ Could use urllib3 for better retry
- ⚠️ Timeout is hardcoded (5 seconds)
- 💡 Could add update download/install

---

### 2.10 TUTORIAL ASSISTANT
**File**: `src/tutorial_assistant.py` (238 lines)

#### Purpose
AI-powered chatbot for helping users with Clarify tutorials using Gemini.

#### Class Structure
```python
class TutorialAssistant:
    def __init__(self, api_key: Optional[str] = None, 
                 base_path: Optional[Path] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.base_path = base_path or Path(...) / 'docs' / 'tutorials'
        self.available = bool(self.api_key) and _GEMINI_AVAILABLE
        
        self.conversation_history = []
        self.knowledge_base = {}
        self.tutorials_content = {}
```

#### Key Responsibilities
1. **Knowledge Base**: Load tutorials index from JSON
2. **Context Building**: Build AI context from tutorials
3. **Conversation**: Chat with session history (last 10 messages)
4. **Query Matching**: Find relevant tutorials by keywords
5. **Graceful Degradation**: Disable if API key or library missing

#### Design Patterns
- **Adapter**: Wraps Gemini API
- **Strategy**: Different response strategies for available/unavailable
- **Chain of Responsibility**: Search keywords in tutorials

#### Knowledge Base Structure
```
docs/tutorials/
├── index.json
├── getting-started.md
├── advanced-features.md
└── ...
```

```json
{
    "tutorials": [
        {
            "id": "basics",
            "title": "Getting Started",
            "file": "getting-started.md",
            "keywords": ["search", "replace", "basics"],
            "estimated_time": "5 min"
        }
    ],
    "faq": [
        {"question": "How to...", "answer": "..."}
    ]
}
```

#### Key Methods
```python
ask(user_query)                     # (response, success) tuple
_load_knowledge_base()              # Load tutorials index
_build_context(user_query)          # Build AI prompt context
reset_conversation()                # Clear history
```

#### Conversation Management
- Maintains history: Last 10 messages (5 exchanges)
- Context: Tutorial titles, keywords, FAQ
- Matching: Find relevant tutorials by keyword search
- Limiting: Max 2 tutorial content blocks to avoid token overflow

#### Code Quality Observations
- ✅ Graceful missing dependency handling
- ✅ Good separation: knowledge base loading vs context building
- ✅ Conversation history management
- ✅ Keyword-based relevance matching
- ⚠️ Assumes tutorials_content can fit in context
- ⚠️ No error recovery for API timeouts
- 💡 Could add confidence scoring
- 💡 Could cache matching tutorials

---

### 2.11 HISTORY MANAGER
**File**: `src/history_manager.py` (200+ lines)

#### Purpose
Manage operation history for set operations and undo/redo.

#### Class Structure
```python
class HistoryManager:
    MAX_ENTRIES = 50
    SETTINGS_KEY = "operation_history"
    
    def __init__(self):
        self.settings = QSettings("Clarify", "Clarify")
```

#### Key Responsibilities
1. **Operation Logging**: Store operation details (type, files, mode, results)
2. **History Persistence**: Save to QSettings
3. **Entry Formatting**: Display-ready strings for UI
4. **Export**: Save history to JSON file

#### History Entry Structure
```python
{
    "timestamp": "2025-01-20T14:30:45.123456",
    "operation_type": "∩",           # Intersection
    "file1": "/path/to/file1.json",
    "file2": "/path/to/file2.json",
    "comparison_mode": "value",
    "result_count": 42,
    "result_data": [...]             # Optional, for re-execution
}
```

#### Design Patterns
- **Memento**: Each entry is a snapshot of operation state
- **Composite**: Stores complete operation context

#### Key Methods
```python
add_operation(operation_type, file1, file2, mode, count, data)
get_history()                       # Returns List[Dict]
get_entry(index)                    # Returns Dict or None
clear_history()                     # Remove all entries
export_history(filepath)            # Save to JSON
format_entry_display(entry)         # Format for UI display
```

#### Code Quality Observations
- ✅ Simple, focused responsibility
- ✅ Good data structure for UI binding
- ✅ Export capability for audit trail
- ⚠️ Limited to 50 entries (hard-coded)
- ⚠️ No filtering/search capability
- 💡 Could add undo/redo (store result_data)

---

## 3. KEY DESIGN PATTERNS OBSERVED

### 3.1 Singleton Pattern
- **SettingsManager**: Global `_settings_instance` via `get_settings()`
- **ConfigManager**: Could be singleton (currently implicit)
- **Theme**: Static methods (pseudo-singleton behavior)

### 3.2 Facade Pattern
- **MainWindow**: Orchestrates all managers and UI components
- **PluginLoader**: Abstracts plugin complexity

### 3.3 Strategy Pattern
- **LayoutManager**: Different preset strategies (Compact, Standard, Advanced)
- **ThemeManager**: Different theme application strategies
- **UpdateChecker**: Cache-first vs API strategies

### 3.4 Factory Pattern
- **DockFactory**: Creates dock widgets on-demand
- **PluginLoader**: Creates plugin instances dynamically

### 3.5 Observer Pattern
- **PluginLoader**: Signal-based event system
- **UpdateChecker**: Could emit signals on update available
- **ConfigManager**: Could notify listeners of changes

### 3.6 Adapter Pattern
- **TutorialAssistant**: Wraps Gemini API
- **ConfigManager**: Bridges old SettingsManager with new YAML-based config

### 3.7 Template Method Pattern
- **ConfigManager._load_or_create()**: Orchestrates load/migrate/save flow
- **MigrationManager.run_pending_migrations()**: Orchestrates discovery → backup → execute

### 3.8 Registry Pattern
- **PluginLoader**: Maintains registry of loaded plugins
- **ShortcutManager**: SHORTCUTS dict is a registry
- **LayoutManager**: docks dict tracks registered docks

### 3.9 Lazy Loading Pattern
- **`__init__.py`**: Defers PySide6 import
- **MainWindow**: Lazy-loads tabs and docks on demand
- **DockFactory**: Creates widgets only when requested

### 3.10 Static Utility Pattern
- **ThemeManager**: All static methods
- **AccessibilityManager**: All static methods
- **ShortcutManager**: All @classmethod methods

---

## 4. CONFIGURATION MANAGEMENT FLOW

```
App Startup
    ↓
Check Version (MigrationManager.get_current_version)
    ↓
Run Pending Migrations (MigrationManager.run_pending_migrations)
    ↓
Load Config (ConfigManager._load_or_create)
    ├─ Try load config.yaml
    ├─ If not found, try migrate from QSettings/JSON
    └─ Validate against JSON Schema
    ↓
Load Settings (SettingsManager.load)
    ├─ Try load ~/.clarify_settings.json
    └─ Merge with defaults
    ↓
Apply Theme (ThemeManager.apply_theme)
    ↓
Apply Layout (LayoutManager.restore_last_layout)
    ↓
Load Plugins (PluginLoader.discover_plugins + activate)
    ↓
Apply Accessibility (AccessibilityManager.apply_font_size)
    ↓
Auto-check Updates (UpdateChecker.check_for_updates)
```

---

## 5. PLUGIN SYSTEM ARCHITECTURE

### Plugin Discovery Flow
```
PluginLoader.__init__
    ↓
discover_plugins() scans plugins/ folder
    ├─ For each directory with plugin.json:
    │   ├─ Load metadata
    │   ├─ Check if enabled in QSettings
    │   └─ Store in self.metadata
    └─ Return list of PluginMetadata
    
↓

load_plugin(plugin_id)
    ├─ Get metadata
    ├─ Dynamic import from entry_point
    ├─ Cache in self.plugins
    └─ Emit plugin_loaded signal
    
↓

activate_all_plugins()
    ├─ For each enabled plugin:
    │   ├─ Load via load_plugin()
    │   ├─ Call plugin.on_activate()
    │   └─ Emit plugin_activated signal
    └─ Connect event listeners
```

### Plugin Hook System
```python
# Plugin implements hooks:
class MyPlugin:
    def on_file_opened(self, path):
        # Custom logic
        
    def on_search_completed(self, results):
        # Custom logic
        
    def create_dock(self):
        # Return custom QDockWidget

# App calls:
loader.emit_event("file_opened", {"path": "/data.json"})
# Which calls:
for plugin in self.plugins.values():
    if hasattr(plugin, "on_file_opened"):
        plugin.on_file_opened(path)
```

---

## 6. MIGRATION SYSTEM

### Version Detection & Execution
```
MigrationManager.run_pending_migrations()
    ├─ current_version = get_current_version()  # e.g., "2.9.90"
    ├─ target_version = CURRENT_VERSION         # e.g., "2.9.91"
    ├─ backup_before_migration()                # Create backups
    ├─ discover_migrations()                    # Load v*.py files
    │   └─ Sort by version
    ├─ For each migration > current_version:
    │   ├─ Run migration.upgrade()
    │   ├─ Catch exceptions, log errors
    │   └─ Update version
    └─ set_current_version(target_version)
```

### Migration File Structure
```python
# migrations/v2_9_91.py
from src.migrations.base import Migration

class MigrationV2991(Migration):
    version = "2.9.91"
    description = "Add new settings for accessibility"
    
    def upgrade(self):
        """Upgrade from 2.9.90 to 2.9.91."""
        if HAS_QT:
            settings = QSettings(...)
            # Add new key
            settings.setValue("accessibility/high_contrast", False)
        
        # Update config.yaml
        config = get_config()
        config.set("app.new_feature", True, save=True)
    
    def downgrade(self):
        """Rollback (not used currently)."""
        pass
```

---

## 7. CODE QUALITY ASSESSMENT

### Strengths
✅ **Good Separation of Concerns**: Each manager has clear responsibility  
✅ **Consistent Patterns**: Managers follow recognizable patterns (Singleton, Factory, etc.)  
✅ **Error Handling**: Graceful fallbacks (e.g., defaults on config error)  
✅ **Logging**: Comprehensive logging infrastructure  
✅ **Persistence**: Multiple storage backends (QSettings, JSON, YAML)  
✅ **Extensibility**: Plugin system for custom functionality  
✅ **Accessibility**: Dedicated a11y manager  
✅ **Version Management**: Automatic migrations  

### Weaknesses
⚠️ **Thread Safety**: No locks on shared state (SettingsManager, ShortcutManager)  
⚠️ **Circular Dependencies**: Potential circular imports between managers  
⚠️ **Configuration Bloat**: ConfigManager.DEFAULTS could be externalized  
⚠️ **Global State**: Singleton patterns create hidden dependencies  
⚠️ **Missing Validation**: Input validation in managers could be better  
⚠️ **Hard-coded Values**: Color codes, timeouts, file paths scattered throughout  
⚠️ **Large Files**: app.py is 2700+ lines (too large, should split)  
⚠️ **Hot Reload**: No support for live config/theme changes without restart  

### Code Smells
- Mutable class variables (`ShortcutManager._custom_shortcuts`)
- Very large QSS strings in ThemeManager
- No atomic file operations (race conditions possible)
- Error messages to stdout instead of logger
- Hardcoded cache durations and limits

---

## 8. CRITICAL ALGORITHMS

### 8.1 Semantic Version Comparison (UpdateChecker)
```python
def _is_newer_version(self, latest: str) -> bool:
    current_parts = [int(x) for x in self.current_version.split('.')]
    latest_parts = [int(x) for x in latest.split('.')]
    
    # Pad with zeros: "2.9" → "2.9.0"
    while len(current_parts) < 3:
        current_parts.append(0)
    while len(latest_parts) < 3:
        latest_parts.append(0)
    
    # Tuple comparison: (major, minor, patch)
    return tuple(latest_parts) > tuple(current_parts)
```

### 8.2 Dotted Key Access (ConfigManager)
```python
def get(self, key: str, default: Any = None) -> Any:
    parts = key.split('.')
    value = self.config
    
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return default
    
    return value if value is not None else default
```

### 8.3 File Time Tracking (HistoryManager)
```python
"timestamp": datetime.now().isoformat()
# ISO 8601: "2025-01-20T14:30:45.123456"
# Later parsed: datetime.fromisoformat(timestamp_str)
```

---

## 9. TODO/FIXME COMMENTS IN CODE

### Found in ConfigManager
- None currently visible, but code is clean

### Found in MigrationManager
- Migration discovery needs better error handling
- No rollback capability (documented as limitation)

### Found in UpdateChecker
- Could add timeout configuration
- Could retry on transient errors

### Found in ThemeManager
- QSS could be externalized to .qss files
- Color scheme not centralized

---

## 10. RECOMMENDATIONS FOR IMPROVEMENT

### Immediate (HIGH PRIORITY)
1. **Thread Safety**: Add locks to SettingsManager and ShortcutManager
2. **Circular Dependencies**: Audit and break cycles between managers
3. **File Operations**: Make settings/config saves atomic (write to temp, then rename)
4. **Error Handling**: Use logger instead of print() everywhere

### Short Term (MEDIUM PRIORITY)
1. **Config Externalization**: Move DEFAULTS and SCHEMA to external YAML
2. **Hot Reload**: Support live theme/config changes without restart
3. **Input Validation**: Add schema validation to all set() methods
4. **Large Files**: Split app.py into smaller modules

### Long Term (LOW PRIORITY)
1. **Update Installer**: Auto-download and install updates
2. **Plugin Security**: Sandbox plugins to prevent malicious code
3. **Performance Profiling**: Identify and optimize hot paths
4. **Documentation**: Auto-generate from code docstrings

---

## 11. ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────┐
│                  MainWindow (Facade)                 │
│         Orchestrates all managers and UI             │
└─────────────────────────────────────────────────────┘
        │
        ├─ SettingsManager (Singleton)
        │  └─ JSON: ~/.clarify_settings.json
        │
        ├─ ConfigManager
        │  └─ YAML: ~/.config/clarify/config.yaml
        │
        ├─ MigrationManager
        │  └─ Migrations: src/migrations/
        │
        ├─ LayoutManager
        │  ├─ QSettings: App/window state
        │  └─ Presets: Compact, Standard, Advanced
        │
        ├─ ThemeManager
        │  ├─ Light theme
        │  ├─ Dark theme
        │  └─ System theme
        │
        ├─ ShortcutManager
        │  ├─ 40+ shortcuts registry
        │  └─ Custom overrides
        │
        ├─ PluginLoader (QObject)
        │  ├─ Plugin discovery
        │  ├─ Lifecycle management
        │  └─ Event signals
        │
        ├─ UpdateChecker
        │  ├─ GitHub Releases API
        │  └─ 24h cache
        │
        ├─ TutorialAssistant
        │  ├─ Gemini AI
        │  └─ Knowledge base
        │
        ├─ HistoryManager
        │  └─ QSettings: operation_history
        │
        ├─ AccessibilityManager
        │  ├─ Screen reader support
        │  ├─ Focus indicators
        │  └─ Font scaling
        │
        └─ GUI Components
           ├─ DockFactory
           ├─ TabManager
           ├─ ResultsTree
           └─ Various docks/tabs
```

---

## 12. INITIALIZATION CHECKLIST

When MainWindow.__init__() runs:
1. ✅ Window flags configured (Linux compatibility)
2. ✅ InitializationManager.initialize_all() called
3. ✅ Global event filter installed (Shift+Scroll)
4. ✅ Layout restored from previous session
5. ✅ UI geometry updated
6. ✅ Accessibility features applied
7. ✅ Tab state restored
8. ✅ All tabs initialized (prevents rendering issues)
9. ✅ Update check started (async, non-blocking)

---

## CONCLUSION

The Clarify project demonstrates solid software engineering principles with clear separation of concerns, consistent design patterns, and good error handling. The manager-based architecture scales well and is easy to extend. Key improvements would focus on thread safety, configuration externalization, and hot-reload capabilities.

**Version**: 2.9.117  
**Analysis Date**: 2025-01-20  
**Scope**: 14 core managers + app.py (2700+ LOC)  
**Total Code**: ~10,650 lines in managers alone
