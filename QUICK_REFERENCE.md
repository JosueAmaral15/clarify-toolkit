# CLARIFY ARCHITECTURE - QUICK REFERENCE GUIDE

## 📋 File Locations & Responsibilities

```
src/__init__.py                    → Package metadata + lazy main()
src/__main__.py                    → Module entry point (python -m src)
src/app.py                         → MainWindow + GUI orchestration (2700+ LOC)

MANAGERS:
src/settings_manager.py            → User preferences (JSON)
src/config_manager.py              → App configuration (YAML + validation)
src/layout_manager.py              → Window/dock layouts + presets
src/theme_manager.py               → Light/Dark/System themes
src/shortcut_manager.py            → Keyboard shortcuts registry
src/plugin_loader.py               → Dynamic plugin system
src/migration_manager.py           → Version migrations
src/history_manager.py             → Operation history
src/update_checker.py              → GitHub Releases API
src/accessibility_manager.py       → WCAG AAA features
src/tutorial_assistant.py          → Gemini AI chatbot
```

---

## 🚀 INITIALIZATION SEQUENCE

```
1. __main__.py
   ↓ import .app:main
   
2. app.py:main()
   ↓ QApplication(sys.argv)
   
3. MainWindow(app)
   └─ InitializationManager.initialize_all(window, app)
      ├─ ConfigManager (load YAML)
      ├─ SettingsManager (load JSON)
      ├─ LayoutManager (restore window state)
      ├─ ThemeManager.apply_theme()
      ├─ ShortcutManager (register 40+ shortcuts)
      ├─ PluginLoader (discover + activate)
      └─ AccessibilityManager (a11y features)
      
4. MainWindow._apply_accessibility()
5. MainWindow._restore_tab_state()
6. MainWindow._initialize_all_tabs()
7. MainWindow._auto_check_for_updates()
```

---

## 💾 STORAGE BACKENDS

| Backend | Location | Use | Priority |
|---------|----------|-----|----------|
| **YAML Config** | `~/.config/clarify/config.yaml` | Central config | 1 (highest) |
| **QSettings** | Registry/plist/dconf | Window geometry, dock state | 2 |
| **JSON Settings** | `~/.clarify_settings.json` | Recent files, shortcuts | 3 |
| **File Cache** | `~/.cache/clarify/` | Update check cache | 4 |

---

## 🎨 THEME SYSTEM

### Apply Theme
```python
from src.theme_manager import ThemeManager
ThemeManager.apply_theme(app, "dark")  # "dark" | "light" | "system"
```

### Color Scheme
- **Light**: #FAFAFA bg, #1E1E1E text, #0078D7 highlight
- **Dark**: #2D2D30 bg, #CCCCCC text, #007ACC highlight

---

## ⌨️ KEYBOARD SHORTCUTS

### Common Shortcuts
```
Ctrl+N          New file
Ctrl+O          Open file
Ctrl+S          Save file
Ctrl+F          Find/Search
Ctrl+H          Replace
Ctrl+E          Open Editor
Ctrl+1-9        Jump to dock 1-9
Ctrl+Tab        Next dock
Ctrl+Shift+Tab  Previous dock
F5              Process/Run
Esc             Interrupt/Cancel
F11             Toggle fullscreen
```

### Navigation
```
Ctrl+1  JSON Search
Ctrl+2  JSON Rewriter
Ctrl+3  Set Operations
Ctrl+4  AI Processor
Ctrl+5  Case Converter
Ctrl+6  Text Extractor
Ctrl+7  Text to JSON
Ctrl+8  Placeholder Replacer
Ctrl+9  JSON Translate
```

---

## 🔌 PLUGIN SYSTEM

### Plugin Structure
```
plugins/my-plugin/
├── plugin.json          # Metadata manifest
├── main.py              # Entry point class
└── requirements.txt     # Dependencies
```

### plugin.json Template
```json
{
    "id": "my-plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "Does something useful",
    "author": "You",
    "entry_point": "main.py",
    "dependencies": ["requests>=2.25"],
    "enabled": true
}
```

### Plugin Lifecycle
```python
# main.py
class MyPlugin:
    def on_activate(self):
        """Called when plugin is loaded."""
        pass
    
    def on_file_opened(self, path):
        """Hook: file opened."""
        pass
    
    def on_search_completed(self, results):
        """Hook: search finished."""
        pass
    
    def create_dock(self):
        """Return custom QDockWidget or None."""
        return None
```

### Plugin Discovery
```python
from src.plugin_loader import PluginLoader
loader = PluginLoader(app)
loader.discover_plugins()    # Find all in plugins/
loader.activate_all_plugins() # Load & init
```

---

## 🔄 CONFIGURATION MANAGEMENT

### ConfigManager Sections
```yaml
app:
  theme: system
  language: en
  check_updates_on_startup: true

logging:
  level: INFO
  max_file_size_mb: 10

performance:
  thread_pool_size: 4
  max_file_size_mb: 50

ai:
  default_provider: OpenAI
  remember_api_keys: false

editor:
  font_family: Consolas
  font_size: 12
```

### Usage
```python
from src.config_manager import ConfigManager
config = ConfigManager()
theme = config.get("app.theme", "system")      # Dotted notation
config.set("app.theme", "dark")                # Update
config.save()                                   # Persist
```

---

## 📜 MIGRATION SYSTEM

### Add Migration
1. Create `src/migrations/v2_X_X.py`
2. Implement Migration class
3. Call `MigrationManager.run_pending_migrations()` at startup

### Migration Template
```python
from src.migrations.base import Migration

class MigrationV2_10_0(Migration):
    version = "2.10.0"
    description = "Add new feature"
    
    def upgrade(self):
        # Migrate from old version
        config.set("new_key", "new_value", save=True)
```

---

## 🎯 LAYOUT/PRESETS

### Three Built-in Presets
```python
# Compact: Editor only
layout_manager.apply_preset("Compact")

# Standard: Editor, Search, Replace, Rewriter (default)
layout_manager.apply_preset("Standard")

# Advanced: All docks visible
layout_manager.apply_preset("Advanced")
```

### Save/Load Custom Layout
```python
layout_manager.save_layout("my_layout")
layout_manager.load_layout("my_layout")
layout_manager.get_saved_layouts()      # Returns list
layout_manager.delete_layout("my_layout")
```

---

## ♿ ACCESSIBILITY

### Set Accessible Widget
```python
from src.accessibility_manager import AccessibilityManager
AccessibilityManager.set_accessible_widget(
    widget=my_button,
    name="Run Operation",
    description="Execute the selected operation"
)
```

### Font Scaling
```python
AccessibilityManager.apply_font_size(app, 14)      # Set to 14pt
AccessibilityManager.increase_font_size(app)       # +1pt
AccessibilityManager.set_font_size(14, settings)   # Persist
```

### Focus Indicators
```python
# Applied globally via QSS in apply_focus_indicators()
# 2px solid #007ACC border on focus
AccessibilityManager.apply_focus_indicators(app)
```

---

## 🔍 UPDATE CHECKING

### Check for Updates
```python
from src.update_checker import UpdateChecker
checker = UpdateChecker("2.9.44")
has_update, info = checker.check_for_updates()

if has_update:
    print(f"New version: {info['version']}")
    print(f"URL: {info['url']}")
```

### Cache
- **Location**: `~/.cache/clarify/update_check.json`
- **TTL**: 24 hours
- **Force Refresh**: `checker.check_for_updates(force=True)`

---

## 📋 SETTINGS MANAGER

### Usage
```python
from src.settings_manager import get_settings
settings = get_settings()

# Get setting
theme = settings.get("theme", "system")

# Set and persist
settings.set("theme", "dark")

# Recent files
settings.add_recent_file("/path/to/file.json")
recent = settings.get_recent_files()
settings.clear_recent_files()

# Custom shortcuts
shortcuts = settings.get_custom_shortcuts()
settings.set_custom_shortcuts({"new_key": "Ctrl+Alt+N"})
```

---

## 📊 HISTORY MANAGER

### Add Operation
```python
from src.history_manager import HistoryManager
history = HistoryManager()

history.add_operation(
    operation_type="∩",        # Intersection
    file1="/path/file1.json",
    file2="/path/file2.json",
    comparison_mode="value",
    result_count=42,
    result_data=None
)
```

### Retrieve History
```python
all_history = history.get_history()           # List of dicts
entry = history.get_entry(0)                  # First entry
formatted = history.format_entry_display(entry)
history.export_history("/tmp/history.json")
```

---

## 🤖 TUTORIAL ASSISTANT

### Usage
```python
from src.tutorial_assistant import TutorialAssistant
assistant = TutorialAssistant(api_key="YOUR_GEMINI_KEY")

response, success = assistant.ask("How do I use the rewriter?")
if success:
    print(response)
else:
    print("Error:", response)

assistant.reset_conversation()  # Clear history
```

---

## 🔧 SHORTCUT MANAGER

### Get Shortcut
```python
from src.shortcut_manager import ShortcutManager

# Get custom or default
shortcut, description = ShortcutManager.get_shortcut("open_file")
# Returns: ("Ctrl+O", "Open file")

# Get key sequence for action
key_seq = ShortcutManager.get_key_sequence("save_file")
action.setShortcut(key_seq)

# Get all shortcuts
all_shortcuts = ShortcutManager.get_all_shortcuts()
```

---

## 📐 PATTERN QUICK REFERENCE

| Pattern | Location | Example |
|---------|----------|---------|
| Singleton | SettingsManager | `get_settings()` |
| Factory | DockFactory | `create_json_translate_dock()` |
| Strategy | ThemeManager | 3 theme strategies |
| Registry | PluginLoader | plugin discovery |
| Facade | MainWindow | orchestrates all |
| Observer | PluginLoader | emit_event signals |

---

## 🚨 COMMON ISSUES

### Issue: Settings not persisting
**Fix**: Call `settings.save()` or `config.save()`

### Issue: Layout reverts to default
**Fix**: Ensure `layout_manager.save_layout()` called before exit

### Issue: Plugin not discovered
**Fix**: Check plugin.json exists and is valid JSON in plugins/ folder

### Issue: Theme not applying
**Fix**: Call `ThemeManager.apply_theme(app, mode)` before showing UI

### Issue: Migration failed
**Check**: Logs in `~/.clarify/logs/migrations.log`

---

## 📖 ADDING NEW FEATURES

### Add Manager
```python
# 1. Create src/new_manager.py
class NewManager:
    def __init__(self):
        pass
    
    def method(self):
        pass

# 2. Update InitializationManager
# Add to initialize_all()

# 3. Use in MainWindow
self.new_manager = NewManager()
```

### Add Shortcut
```python
# 1. Update ShortcutManager.SHORTCUTS
"my_action": ("Ctrl+Alt+M", "My action description")

# 2. Create action
action = QAction("My Action", self)

# 3. Apply shortcut
ShortcutManager.add_shortcut_to_action(action, "my_action")
```

### Add Theme
```python
# 1. Add to ThemeManager
def _apply_my_theme(app):
    palette = QPalette()
    # ... set colors

# 2. Update apply_theme()
elif mode == "my_theme":
    self._apply_my_theme(app)
```

---

## 🧪 TESTING

### Test Settings
```python
from src.settings_manager import SettingsManager, reset_settings_instance
reset_settings_instance()
settings = SettingsManager("/tmp/test_settings.json")
settings.set("test", "value")
```

### Test Config
```python
from src.config_manager import ConfigManager
config = ConfigManager("/tmp/test_config.yaml")
config.set("app.test", True, save=True)
```

### Test Plugin
```python
from src.plugin_loader import PluginLoader
loader = PluginLoader(app)
plugins = loader.discover_plugins()
assert len(plugins) > 0
```

---

## 📞 FREQUENTLY NEEDED IMPORTS

```python
# Settings & Config
from src.settings_manager import get_settings
from src.config_manager import ConfigManager

# Managers
from src.layout_manager import LayoutManager
from src.theme_manager import ThemeManager
from src.shortcut_manager import ShortcutManager
from src.plugin_loader import PluginLoader
from src.migration_manager import MigrationManager
from src.accessibility_manager import AccessibilityManager
from src.update_checker import UpdateChecker
from src.tutorial_assistant import TutorialAssistant

# UI
from src.gui import DockFactory, MenuBuilder
```

---

**Version**: 1.0  
**Last Updated**: 2025-01-20  
**Project**: Clarify v2.9.117
