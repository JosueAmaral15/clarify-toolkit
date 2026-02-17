# CLARIFY ARCHITECTURE - EXECUTIVE SUMMARY

## Quick Overview

**Clarify** is a sophisticated desktop application (Python + PySide6) for JSON/text processing with:
- **GUI Framework**: PySide6 (Qt6) with dockable widgets
- **Architecture**: Manager-based orchestration pattern
- **Core Size**: 14 managers + 1 main application class (2700+ LOC app.py)
- **Version**: 2.9.117 (Linux/Qt6 compatibility improvements)

---

## 1. INITIALIZATION FLOW (App Startup)

```
__main__.py → app.py:main() → MainWindow().__init__()
    ↓
InitializationManager.initialize_all(window, app)
    ├─ Load ConfigManager (YAML validation + migration)
    ├─ Load SettingsManager (JSON persistence)
    ├─ Apply ThemeManager (Light/Dark/System)
    ├─ Apply LayoutManager (Restore last window state)
    ├─ Load PluginLoader (Discover & activate plugins)
    ├─ Apply AccessibilityManager (a11y features)
    └─ Start UpdateChecker (Background thread)
```

---

## 2. THE 14 CORE MANAGERS

### Manager Quick Reference

| Manager | File | Lines | Purpose | Storage |
|---------|------|-------|---------|---------|
| **SettingsManager** | settings_manager.py | 150 | User preferences (theme, recent files) | JSON file |
| **ConfigManager** | config_manager.py | 450+ | Application configuration with validation | YAML file |
| **LayoutManager** | layout_manager.py | 297 | Dock/window layout persistence + presets | QSettings |
| **ThemeManager** | theme_manager.py | 524 | Light/Dark/System theming | Memory only |
| **ShortcutManager** | shortcut_manager.py | 316 | Keyboard shortcuts (~40 defined) | Memory only |
| **PluginLoader** | plugin_loader.py | 319 | Dynamic plugin system with signals | QSettings |
| **MigrationManager** | migration_manager.py | 272 | Auto-upgrade configs between versions | Logged |
| **HistoryManager** | history_manager.py | 200+ | Operation history (50 entries max) | QSettings |
| **UpdateChecker** | update_checker.py | 267 | GitHub Releases API with 24h cache | File cache |
| **AccessibilityManager** | accessibility_manager.py | 200+ | WCAG AAA compliance (focus, fonts) | QSettings |
| **TutorialAssistant** | tutorial_assistant.py | 238 | Gemini AI chatbot for tutorials | Memory |
| **InitializationManager** | (implicit) | N/A | Orchestrates startup sequence | N/A |

**Total**: ~3,200 lines of manager code (not including app.py)

---

## 3. KEY ARCHITECTURAL PATTERNS

### 🎯 Singleton Pattern
```python
# SettingsManager
_settings_instance = None
def get_settings() → SettingsManager:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
```

### 🏭 Factory Pattern
```python
# DockFactory creates widgets on-demand
DockFactory.create_json_translate_dock(self)
DockFactory.create_json_rewriter_dock(self)
# Only created when first requested
```

### 🔌 Plugin System (Registry + Observer)
```python
# Plugins auto-discovered from plugins/ folder
loader.discover_plugins()          # Find all
loader.activate_all_plugins()      # Load & init
loader.emit_event("file_opened", {"path": "..."})  # Trigger hooks
```

### 💾 Strategy Pattern
```python
# ConfigManager with priority: CLI args > config.yaml > defaults
# ThemeManager with 3 strategies: light, dark, system
# LayoutManager with 3 presets: compact, standard, advanced
```

### 🎭 Facade Pattern
```python
# MainWindow orchestrates everything
class MainWindow(QMainWindow):
    def __init__(self, app):
        InitializationManager.initialize_all(self, app)
        # All managers initialized in one call
```

---

## 4. CONFIGURATION MANAGEMENT PYRAMID

```
                     CLI Arguments
                           ↓
                 ~/.config/clarify/config.yaml
                    (YAML with validation)
                           ↓
                      Defaults dict
                  (in ConfigManager)

Priority: CLI > YAML > Defaults
```

### ConfigManager Features
- **Centralized**: Single YAML file replaces scattered QSettings
- **Validated**: JSON Schema validation (enums, ranges, patterns)
- **Versioned**: Automatic migration system (v2.9.90 → v2.9.91)
- **Backed-up**: Auto-backup before overwrites
- **Dotted Access**: `config.get("app.theme", "system")`

### Default Sections
```yaml
app:
  theme: system              # system | light | dark
  language: en
  check_updates_on_startup: true

logging:
  level: INFO               # DEBUG | INFO | WARNING | ERROR | CRITICAL
  max_file_size_mb: 10

performance:
  thread_pool_size: 4
  max_file_size_mb: 50

ai:
  default_provider: OpenAI  # OpenAI | Gemini
  remember_api_keys: false  # Security: default false!

editor:
  font_family: Consolas
  font_size: 12
  tab_width: 4
```

---

## 5. PERSISTENCE LAYERS

### Three Storage Backends in Use

```
┌────────────────────────────────────────────────────────┐
│  Storage Layer Analysis                                 │
├────────────────────────────────────────────────────────┤
│ 1. QSettings (Qt Registry/NSDefaults/dconf)            │
│    - Theme preference                                   │
│    - Window geometry & dock state                       │
│    - Plugin enabled/disabled status                     │
│                                                         │
│ 2. JSON Files                                          │
│    - Recent files list                                 │
│    - Custom shortcuts                                  │
│    - Location: ~/.clarify_settings.json                │
│                                                         │
│ 3. YAML Files                                          │
│    - Central config: ~/.config/clarify/config.yaml    │
│    - Schemas: JSON Schema validation                   │
│    - Migrations: Automatic versioning                  │
│                                                         │
│ 4. File System Cache                                   │
│    - Update check cache: ~/.cache/clarify/             │
│    - TTL: 24 hours                                     │
│    - Offline friendly                                  │
└────────────────────────────────────────────────────────┘
```

---

## 6. PLUGIN SYSTEM ARCHITECTURE

### Plugin Structure
```
plugins/
├── json-validator/
│   ├── plugin.json          # Metadata & manifest
│   ├── main.py              # Entry point
│   ├── hooks.py             # Event handlers
│   └── requirements.txt      # Dependencies
└── another-plugin/
    ├── plugin.json
    └── main.py
```

### Plugin Lifecycle
```
Discover          Load           Activate          Event Loop
(find .json) → (import module) → (init) → (emit hooks)
     ↓              ↓              ↓              ↓
list[30 plugins]  [some in memory] [hooks connected] [plugins active]
```

### Hook System
Plugins can implement:
- `on_file_opened(path)`
- `on_search_completed(results)`
- `on_ui_loaded()`
- `on_app_closing()`

Plugins can provide:
- Custom docks (QDockWidget)
- Menu items
- Custom settings

---

## 7. MIGRATION SYSTEM

### Automatic Version Detection & Upgrade

```
app.py:main()
    ↓
MigrationManager.run_pending_migrations()
    ├─ Read current version from QSettings/config.yaml
    ├─ Compare with CURRENT_VERSION = "2.9.91"
    ├─ Create backup of current config
    ├─ Scan migrations/ folder for v*.py files
    ├─ Sort by version & execute pending
    └─ Update version after successful migration
```

### Migration File Structure
```python
# migrations/v2_9_91.py
class MigrationV2991(Migration):
    version = "2.9.91"
    description = "Add accessibility settings"
    
    def upgrade(self):
        settings.setValue("accessibility/high_contrast", False)
        config.set("app.new_key", value, save=True)
```

### Safety Features
- ✅ Auto-backup before running migrations
- ✅ Detailed logging to ~/.clarify/logs/migrations.log
- ✅ Graceful error handling (continue on error)
- ⚠️ No rollback (use backups for manual recovery)

---

## 8. THEME SYSTEM

### Three Built-in Themes

#### Light Theme
- Background: #FAFAFA (off-white)
- Text: #1E1E1E (dark gray)
- Highlight: #0078D7 (VS Code blue)
- 200+ lines of QSS for all widgets

#### Dark Theme
- Background: #2D2D30 (dark gray)
- Text: #CCCCCC (light gray)
- Highlight: #007ACC (VS Code blue)
- Same comprehensive QSS coverage

#### System Theme
- Uses OS defaults via Qt Fusion style
- Platform-native colors

### Theme Coverage
```python
# QPalette styling
Window, WindowText, Base, AlternateBase
Button, ButtonText
Text, Highlight, HighlightedText
Link, LinkVisited
Disabled states for all above

# QSS for specific widgets
QLineEdit, QPlainTextEdit, QTextEdit
QPushButton (normal, hover, pressed, disabled)
QCheckBox, QRadioButton
QComboBox, QTreeWidget, QListWidget
QProgressBar, QScrollBar
... and more
```

---

## 9. ACCESSIBILITY FEATURES

### WCAG AAA Compliance

#### Screen Reader Support
```python
AccessibilityManager.set_accessible_widget(
    widget=button,
    name="Run JSON Rewriter",
    description="Execute JSON rewrite operation with deduplication"
)
```

#### Focus Indicators
- 2px solid #007ACC border
- Applied globally via QSS
- Visible on Tab navigation

#### Font Scaling
- Range: 8-24 points
- Persistent to QSettings
- Hotkey: Ctrl+Scroll

#### Keyboard Navigation
- Full Tab order support
- Named keyboard shortcuts (40+)
- Jump-to-dock shortcuts (Ctrl+1 through Ctrl+9)

---

## 10. UPDATE CHECKING SYSTEM

### GitHub Releases Integration

```python
UpdateChecker(current_version="2.9.44")
    .check_for_updates()
    → (has_update, release_info)
    
# Returns:
{
    "version": "2.9.45",
    "url": "https://github.com/.../releases/tag/v2.9.45",
    "changelog_url": "https://github.com/.../CHANGELOG.md",
    "published_at": "2025-01-20T10:00:00Z",
    "body": "Release notes..."
}
```

### Caching Strategy
- **Cache File**: ~/.cache/clarify/update_check.json
- **TTL**: 24 hours
- **Benefit**: Avoids GitHub API rate limiting (60 req/hour unauthenticated)
- **Fallback**: Offline-friendly, returns cached result if API fails

### Semantic Versioning
```python
# Version comparison: (2, 9, 45) > (2, 9, 44) ✓
# Handles: 2.9 → 2.9.0 (padding with zeros)
# Safety: Invalid version format → assume not newer
```

---

## 11. LAYOUT/PRESET SYSTEM

### Three Presets

| Preset | Visible | Use Case | Saved? |
|--------|---------|----------|--------|
| **Compact** | Editor only | Focused work | QSettings |
| **Standard** | Editor, Search, Replace, Rewriter | Daily use | QSettings |
| **Advanced** | All docks | Power users | QSettings |

### Layout Persistence
```
QMainWindow.saveGeometry() → Stored in QSettings["Layouts/..."]
QMainWindow.saveState()    → Includes dock positions & sizes
Individual dock visibility → Stored per dock

RestoreGeometry() + RestoreState() on startup
```

### Custom Layouts
- Save current layout with custom name
- Load saved layouts
- Delete layouts
- List all saved layouts (excludes 3 presets)

---

## 12. KEYBOARD SHORTCUTS (40+)

### Categories

**File**: new, open, save, save_as, close_tab, exit  
**Edit**: copy, paste, cut, select_all, undo, redo, find, replace  
**Navigation**: next_dock, prev_dock, jump_dock_1-9  
**View**: fullscreen, toggle_history, zoom_in/out, reset_zoom  
**Processing**: process (F5), interrupt (Esc), clear (Ctrl+L)  
**Help**: F1, Ctrl+K Ctrl+S (shortcuts), Ctrl+Shift+? (tutorials)  

### Custom Shortcuts
- Stored in Settings Manager
- Overlay defaults without changing SHORTCUTS dict
- Could be expanded from UI

---

## 13. CODE QUALITY SCORECARD

### Strengths ✅
- Good separation of concerns (14 focused managers)
- Consistent design patterns throughout
- Comprehensive error handling & graceful fallbacks
- Logging infrastructure (file + console)
- Multiple persistence layers (QSettings, JSON, YAML, file cache)
- Extensible plugin system
- WCAG AAA accessibility mindset
- Automatic versioning & migrations

### Weaknesses ⚠️
- No thread safety (mutable class variables)
- Potential circular dependencies between managers
- Large files (app.py: 2700+ lines)
- Hard-coded values scattered (colors, timeouts, limits)
- No validation of setting values
- No hot-reload (changes require restart)
- QSS strings too large (should be external .qss files)

### Code Smells 🚨
- `ShortcutManager._custom_shortcuts` as mutable class variable
- Non-atomic file writes (race conditions possible)
- Some print() statements instead of logger calls
- Hard-coded cache durations
- Large monolithic app.py

---

## 14. RECOMMENDATIONS

### Immediate (HIGH)
1. **Thread Safety**: Add locks to SettingsManager, ShortcutManager
2. **File Safety**: Make config saves atomic (write temp → rename)
3. **Code Quality**: Use logger instead of print() everywhere
4. **Circular Deps**: Audit and break manager dependencies

### Short Term (MEDIUM)
1. **Split app.py**: Break into smaller modules (UI factory, event handlers, etc.)
2. **Externalize Config**: Move DEFAULTS & SCHEMA to external YAML/JSON
3. **Hot Reload**: Support theme/config changes without restart
4. **Validation**: Add schema validation to all set() methods

### Long Term (LOW)
1. **Plugin Sandboxing**: Isolate plugins (security)
2. **Auto-Update**: Download & install updates automatically
3. **Performance**: Profile and optimize hot paths
4. **Documentation**: Auto-generate from docstrings

---

## 15. METRICS

| Metric | Value |
|--------|-------|
| Core Managers | 14 |
| Manager Code | ~3,200 lines |
| app.py Size | 2,700+ lines |
| Total Critical Code | ~10,650 lines |
| Keyboard Shortcuts | 40+ |
| Theme Presets | 3 |
| Built-in Plugins | 0 (extensible) |
| Version | 2.9.117 |

---

## QUICK START FOR DEVELOPERS

### Adding a New Manager
1. Create `src/new_manager.py` with class `NewManager`
2. Implement `__init__()` and key methods
3. Update `InitializationManager.initialize_all()`
4. Document in this architecture guide

### Creating a Plugin
1. Create `plugins/my-plugin/` directory
2. Create `plugin.json` with metadata
3. Create `main.py` with plugin class
4. Implement hooks (on_file_opened, etc.)
5. Place in plugins/ folder
6. Auto-discovered on startup

### Adding a Theme
1. Add methods to `ThemeManager`
2. Add option to Settings UI
3. Call `ThemeManager.apply_theme(app, "new_theme")`

### Adding a Shortcut
1. Add entry to `ShortcutManager.SHORTCUTS`
2. Create action in UI
3. Call `ShortcutManager.add_shortcut_to_action(action, "action_name")`

---

## CONCLUSION

Clarify demonstrates **solid enterprise software architecture** with:
- Clear separation of concerns
- Consistent, recognizable design patterns
- Good error handling and persistence
- Extensible plugin system
- Accessibility-first mindset

**Main improvement opportunity**: Break up app.py and add thread safety.

**Status**: Production-ready with good foundation for future growth.

---

**Document Version**: 1.0  
**Analysis Date**: 2025-01-20  
**Project Version**: 2.9.117  
**Author**: Josué Amaral  
