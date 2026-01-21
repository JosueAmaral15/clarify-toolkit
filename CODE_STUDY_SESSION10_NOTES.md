# CODE STUDY SESSION 10 - Core Utilities & Managers
**Date**: 2026-01-21  
**Programmer**: #4  
**Branch**: COM4-code-study  
**Focus**: Infrastructure managers - Layout, Shortcuts, Themes, Statistics, Presets

---

## 📋 STUDY SCOPE

### Files Analyzed (5 files, 1,572 LOC)
1. **layout_manager.py** (298 LOC) - Layout persistence system
2. **shortcut_manager.py** (317 LOC) - Keyboard shortcuts management
3. **theme_manager.py** (525 LOC) - Application theming (Light/Dark/System)
4. **statistics_manager.py** (215 LOC) - JSON statistics calculation
5. **presets_manager.py** (222 LOC) - Operation presets storage

**Total**: 1,572 LOC (vs predicted 1,200 - 31% higher)

---

## 🏗️ ARCHITECTURAL ANALYSIS

### 1. LAYOUT MANAGER (`layout_manager.py`)

**Purpose**: Manages application layout persistence (dock positions, sizes, visibility)

#### Key Features
- **QSettings-based persistence** (Qt's cross-platform config storage)
- **3 built-in presets**: Compact, Standard, Advanced
- **Custom layout support** (save/load/delete user layouts)
- **Registry pattern** for docks (register_dock() before management)

#### Core API
```python
class LayoutManager:
    PRESETS = ["Compact", "Standard", "Advanced"]
    
    def __init__(self, main_window: QMainWindow)
    def register_dock(name: str, dock_widget) -> None
    def save_layout(layout_name: str) -> None
    def load_layout(layout_name: str) -> bool
    def apply_preset(preset_name: str) -> bool
    def restore_last_layout() -> bool
    def get_saved_layouts() -> List[str]
    def delete_layout(layout_name: str) -> bool
    def reset_to_defaults() -> None
```

#### Preset Behaviors
| Preset     | Visible Docks                        | Use Case           |
|------------|--------------------------------------|--------------------|
| **Compact** | Editor only                         | Minimalist workflow|
| **Standard**| Editor, Search, Replace, Rewriter   | Default balanced   |
| **Advanced**| All docks visible                   | Power users        |

#### Persistence Strategy
- **Geometry**: Window size/position (QMainWindow.saveGeometry())
- **State**: Dock positions/areas (QMainWindow.saveState())
- **Visibility**: Per-dock boolean flags (custom tracking)
- **Last layout**: Single string key for auto-restore

#### Design Patterns Identified
1. **Memento Pattern**: Save/restore QMainWindow state via QByteArray
2. **Registry Pattern**: register_dock() before operations
3. **Template Method**: apply_preset_X() methods use common save_layout()
4. **Fail-Safe Defaults**: If load fails, fallback to Standard preset

#### Integration Points
- **app.py**: Calls register_dock() for all docks during startup
- **Main menu**: "View > Layout" submenu loads presets
- **QSettings**: Cross-platform storage (Linux: ~/.config/Clarify/ClarifyApp.conf)

---

### 2. SHORTCUT MANAGER (`shortcut_manager.py`)

**Purpose**: Centralized keyboard shortcut management with customization

#### Key Features
- **86 pre-defined shortcuts** across 7 categories
- **Customization support** (custom shortcuts overlay defaults)
- **Conflict detection** (checks duplicates + OS shortcuts)
- **Per-category organization** (File, Edit, Tools, Navigation, View, Processing, Help)
- **Cross-platform awareness** (detects Linux/Windows/macOS conflicts)

#### Core API
```python
class ShortcutManager:
    SHORTCUTS: Dict[str, Tuple[str, str]]  # 86 default shortcuts
    OS_SHORTCUTS: Dict[str, List[str]]      # OS-specific conflicts
    _custom_shortcuts: Dict[str, str]       # User overrides
    
    @classmethod
    def get_shortcut(cls, action_name: str) -> Tuple[str, str]
    @classmethod
    def get_key_sequence(cls, action_name: str) -> QKeySequence
    @classmethod
    def add_shortcut_to_action(cls, action: QAction, action_name: str)
    @classmethod
    def set_custom_shortcut(cls, action_name: str, key_sequence: str) -> bool
    @classmethod
    def get_conflicts(cls, key_sequence: str) -> List[str]
    @classmethod
    def is_os_shortcut(cls, key_sequence: str) -> bool
    @classmethod
    def format_shortcuts_table(cls) -> str  # v2.9.33 comprehensive table
```

#### Shortcut Categories (86 total)
| Category       | Count | Examples                                       |
|----------------|-------|------------------------------------------------|
| **File Ops**   | 6     | Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+W, Ctrl+Q        |
| **Edit Ops**   | 8     | Ctrl+C/V/X, Ctrl+Z/Y, Ctrl+F/H, Ctrl+A        |
| **Tools**      | 11    | Ctrl+Shift+F (Search), Ctrl+Shift+R (Rewriter)|
| **Navigation** | 17    | Ctrl+Tab, Ctrl+1-9 (dock jumps), Ctrl+PgUp/Dn |
| **View**       | 6     | F11 (fullscreen), Ctrl++/- (zoom)             |
| **Processing** | 3     | F5 (run), Esc (cancel), Ctrl+L (clear)        |
| **Help**       | 4     | F1, Ctrl+K Ctrl+S, Ctrl+Shift+?               |

#### Customization Workflow
1. **Load defaults**: 86 shortcuts from SHORTCUTS dict
2. **Overlay custom**: load_custom_shortcuts() from settings
3. **Get effective**: get_shortcut() checks custom first, then default
4. **Conflict check**: get_conflicts() + is_os_shortcut() before saving
5. **Persist**: Save custom_dict to QSettings (not implemented here)

#### Design Patterns Identified
1. **Class-level Singleton**: All methods @classmethod, single state
2. **Template Method**: get_shortcut() logic shared by all accessors
3. **Strategy Pattern**: Custom shortcuts override defaults at runtime
4. **Registry Pattern**: SHORTCUTS dict as static registry
5. **Helper Facade**: ShortcutHelper wraps common widget operations

#### OS Conflict Detection
- **Linux**: Ctrl+Alt+T (terminal), Alt+F4 (close), Super+L (lock)
- **Windows**: Win+L (lock), Ctrl+Shift+Esc (task manager)
- **macOS**: Cmd+Q/H/M, Cmd+Space (Spotlight)

#### Integration Points
- **Dock widgets**: Call add_shortcut_to_action() for QAction buttons
- **Help dialog**: Display format_shortcuts_table() in help window
- **Settings UI**: Load/save custom shortcuts via get/set methods
- **Tooltips**: ShortcutHelper.add_tooltip_with_shortcut() shows shortcuts

---

### 3. THEME MANAGER (`theme_manager.py`)

**Purpose**: Application theming with light/dark/system modes

#### Key Features
- **3 theme modes**: Light, Dark, System (follows OS)
- **Fusion style base** (Qt's cross-platform style)
- **QPalette + QSS hybrid** (colors via palette, widgets via stylesheet)
- **Comprehensive widget coverage** (48 widget types styled)
- **File Explorer integration** (collapsible section styling)

#### Core API
```python
ThemeMode = Literal["system", "light", "dark"]

class ThemeManager:
    @staticmethod
    def apply_theme(app: QApplication, mode: ThemeMode)
    
    # Private methods (not exposed)
    @staticmethod
    def _apply_system_theme(app: QApplication)
    @staticmethod
    def _apply_light_theme(app: QApplication)
    @staticmethod
    def _apply_dark_theme(app: QApplication)
```

#### Theme Architecture
**System Theme**:
- Sets Fusion style
- Uses Qt's standardPalette() (OS native colors)
- Clears custom stylesheets

**Light Theme**:
- **Palette**: 18 color roles (Window #fafafa, Base #ffffff, Text #1e1e1e)
- **QSS**: 278 lines of custom CSS for widgets
- **Highlights**: Blue #0078d7 (Windows 10 accent)

**Dark Theme**:
- **Palette**: 18 color roles (Window #2d2d2e, Base #1e1e1e, Text #f0f0f0)
- **QSS**: 244 lines of custom CSS
- **Highlights**: Blue #007acc (VS Code accent)
- **StatusBar**: Blue background #007acc (distinctive)

#### Widget Coverage (48 types)
| Category          | Widgets Styled                                      |
|-------------------|-----------------------------------------------------|
| **Inputs**        | QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox     |
| **Buttons**       | QPushButton, QCheckBox, QRadioButton               |
| **Lists/Trees**   | QTreeView, QListView, QComboBox                    |
| **Containers**    | QGroupBox, QTabWidget, QTabBar, QDockWidget        |
| **Navigation**    | QMenuBar, QMenu, QScrollBar                        |
| **Status**        | QStatusBar                                         |
| **Custom**        | CollapsibleSection (File Explorer)                 |

#### Color Palette Comparison
| Role             | Light Theme       | Dark Theme        | Purpose            |
|------------------|-------------------|-------------------|--------------------|
| Window           | #fafafa (250)     | #2d2d30 (45)      | Main background    |
| Base             | #ffffff (255)     | #1e1e1e (30)      | Input backgrounds  |
| Text             | #1e1e1e (30)      | #f0f0f0 (240)     | Main text          |
| Highlight        | #0078d7 (Win10)   | #007acc (VS Code) | Selected items     |
| Button           | #f0f0f0 (240)     | #3c3c3c (60)      | Button background  |
| Disabled Text    | #969696 (150)     | #646464 (100)     | Disabled elements  |

#### QSS Architecture
**Light theme**: 278 lines QSS
- 14 widget types explicitly styled
- Focus states (2px blue border)
- Hover states (lightened backgrounds)
- Disabled states (grayed out)

**Dark theme**: 244 lines QSS
- Same 14 widget types
- Higher contrast ratios (WCAG compliant)
- Darker hover states
- Blue status bar (distinctive vs light theme's gray)

#### Design Patterns Identified
1. **Strategy Pattern**: 3 theme strategies (system/light/dark)
2. **Template Method**: apply_theme() delegates to _apply_X_theme()
3. **Facade Pattern**: Single entry point (apply_theme) hides complexity
4. **Static Utility Class**: No instance creation, all static methods
5. **Hybrid Styling**: QPalette (base colors) + QSS (widget details)

#### Integration Points
- **app.py**: Calls apply_theme() during startup
- **Settings dialog**: Theme selector dropdown
- **ConfigManager**: Persists theme choice in config.yaml
- **File Explorer**: CollapsibleSection uses objectName selectors

---

### 4. STATISTICS MANAGER (`statistics_manager.py`)

**Purpose**: Calculate JSON structure statistics for operations

#### Key Features
- **Recursive analysis** (traverses nested structures)
- **7 metrics tracked** (keys, depth, size, types, duplicates)
- **Type distribution** (string/number/boolean/null/array/object counts)
- **Comparative mode** (side-by-side 3-way comparison)
- **Human-readable formatting** (KB/MB/GB size formatting)

#### Core API
```python
class StatisticsManager:
    @staticmethod
    def calculate_statistics(data: Any) -> Dict[str, Any]
    
    @staticmethod
    def calculate_overlap_percentage(
        file1_stats: Dict, 
        file2_stats: Dict, 
        result_count: int
    ) -> float
    
    @staticmethod
    def format_size(size_bytes: int) -> str
    
    @staticmethod
    def format_statistics_text(stats: Dict, label: str) -> str
    
    @staticmethod
    def format_comparative_statistics(
        file1_stats: Dict,
        file2_stats: Dict,
        result_stats: Dict,
        overlap_pct: float
    ) -> str
```

#### Statistics Schema
```python
{
    "total_keys": int,           # All keys encountered (with duplicates)
    "unique_keys": int,          # Unique key names (converted from set)
    "duplicate_keys": int,       # total_keys - unique_keys
    "max_depth": int,            # Maximum nesting level
    "size_bytes": int,           # JSON.dumps() UTF-8 byte count
    "value_types": {
        "string": int,
        "number": int,
        "boolean": int,
        "null": int,
        "array": int,
        "object": int
    }
}
```

#### Analysis Algorithm
```python
def _analyze_recursive(data, stats, depth, seen_keys):
    # Update max_depth
    if depth > stats["max_depth"]:
        stats["max_depth"] = depth
    
    # Dispatch by type
    if isinstance(data, dict):
        stats["value_types"]["object"] += 1
        for key, value in data.items():
            stats["total_keys"] += 1
            stats["unique_keys"].add(key)  # Set for uniqueness
            _analyze_recursive(value, stats, depth + 1, seen_keys)
    
    elif isinstance(data, list):
        stats["value_types"]["array"] += 1
        for item in data:
            _analyze_recursive(item, stats, depth + 1, seen_keys)
    
    elif isinstance(data, str):
        stats["value_types"]["string"] += 1
    
    # ... other primitive types
```

#### Overlap Calculation
```python
# Formula: (result_count / total_keys_both_files) * 100
overlap = (result_count / (file1_keys + file2_keys)) * 100
```
- Used for intersection operations
- Shows how much commonality exists between two JSON files
- Clamped to [0, 100] range

#### Formatting Examples
**Size formatting**:
- `1023 B` → "1023 B"
- `1536 B` → "1.5 KB"
- `1572864 B` → "1.5 MB"
- `1610612736 B` → "1.5 GB"

**Comparative table** (3-column):
```
📊 COMPARATIVE STATISTICS

Overlap: 42.3%

                    File A      File B      Result
─────────────────────────────────────────────────────
Total Keys:         150         200         120
Unique Keys:        100         120         80
Duplicate Keys:     50          80          40
Max Depth:          5           6           5
Size:               15.2 KB     20.5 KB     12.3 KB
...
```

#### Design Patterns Identified
1. **Static Utility Class**: No instance state, all static methods
2. **Visitor Pattern**: _analyze_recursive() visits all nodes
3. **Accumulator Pattern**: stats dict accumulates during traversal
4. **Template Method**: format_X() methods share common logic
5. **Strategy Pattern**: Different formatting strategies (text vs comparative)

#### Integration Points
- **SetOperationsDock**: Displays stats after set operations
- **Results dialog**: Shows 3-way comparison (File A, File B, Result)
- **Export**: Includes statistics in exported reports
- **No persistence**: Calculated on-demand, not stored

---

### 5. PRESETS MANAGER (`presets_manager.py`)

**Purpose**: Manage saved operation presets (favorite configurations)

#### Key Features
- **QSettings persistence** (cross-platform storage)
- **3 default presets** (auto-created on first run)
- **CRUD operations** (create, read, update, delete)
- **Rename support** (with conflict detection)
- **No state** (loads from QSettings each time)

#### Core API
```python
class PresetsManager:
    SETTINGS_KEY = "operation_presets"
    DEFAULT_PRESETS: List[Dict]  # 3 built-in presets
    
    def __init__(self)
    def get_presets() -> List[Dict[str, Any]]
    def get_preset(name: str) -> Optional[Dict[str, Any]]
    def save_preset(preset: Dict[str, Any]) -> bool
    def delete_preset(name: str) -> bool
    def rename_preset(old_name: str, new_name: str) -> bool
    def create_preset_from_current(
        name, operation_type, comparison_mode, ...
    ) -> Dict[str, Any]
```

#### Preset Schema
```python
{
    "name": str,                      # Unique identifier
    "operation_type": str,            # "∩" / "∪" / "−" / "⊕"
    "comparison_mode": str,           # "key_value" / "full_path_value" / "key_only"
    "ignore_case_keys": bool,
    "ignore_case_values": bool,
    "skip_empty": bool,
    "arrays_ignore_order": bool,
    "favorite_files": List[str]       # File paths (optional)
}
```

#### Default Presets
| Preset Name                    | Operation | Mode            | Special Flags         |
|--------------------------------|-----------|-----------------|-----------------------|
| Quick Intersection (key_value) | ∩         | key_value       | None                  |
| Full Path Union                | ∪         | full_path_value | None                  |
| Difference (ignore case)       | −         | key_value       | ignore_case (both)    |

#### CRUD Operations
**Create/Update**:
```python
# If preset["name"] exists, updates it
# Otherwise, appends to list
def save_preset(preset: Dict) -> bool:
    presets = self.get_presets()
    existing_index = find_by_name(presets, preset["name"])
    if existing_index >= 0:
        presets[existing_index] = preset  # Update
    else:
        presets.append(preset)            # Create
    self._save_presets(presets)
```

**Delete**:
```python
# Filters out matching preset
def delete_preset(name: str) -> bool:
    presets = [p for p in presets if p["name"] != name]
    return len(presets) < original_count
```

**Rename**:
```python
# Checks for conflicts, then mutates preset["name"]
def rename_preset(old_name: str, new_name: str) -> bool:
    if any(p["name"] == new_name for p in presets):
        return False  # Conflict
    preset["name"] = new_name
```

#### Persistence Strategy
- **Storage**: QSettings value (single key "operation_presets")
- **Format**: List[Dict] (serialized by Qt)
- **Read pattern**: Load entire list each time (no caching)
- **Write pattern**: Overwrite entire list (no incremental updates)
- **Initialization**: _ensure_defaults() creates 3 presets if empty

#### Design Patterns Identified
1. **Repository Pattern**: Abstracts QSettings persistence
2. **Static Factory Method**: create_preset_from_current() builds preset dict
3. **Initialization Guard**: _ensure_defaults() runs once on first init
4. **Immutable Read**: get_presets() returns list, mutations via save/delete
5. **Named Uniqueness**: Preset name is unique identifier (not ID number)

#### Integration Points
- **SetOperationsDock**: "Presets" dropdown loads presets
- **Save preset dialog**: Calls create_preset_from_current()
- **QSettings**: Cross-platform storage (same location as LayoutManager)
- **No validation**: Assumes caller provides valid operation_type/mode

---

## 🎯 KEY INSIGHTS

### 1. Persistence Architecture (QSettings everywhere)
All 5 managers use **QSettings** for persistence:
- **LayoutManager**: `Layouts/<name>/{geometry, state, dock_*_visible}`
- **ShortcutManager**: Custom shortcuts (not shown, but designed for it)
- **PresetsManager**: `operation_presets` (single key, list of dicts)
- **ThemeManager**: Theme choice persisted by ConfigManager (not here)
- **StatisticsManager**: No persistence (calculated on-demand)

**QSettings location** (Linux):
```
~/.config/Clarify/ClarifyApp.conf
```

### 2. Manager Layering (Core vs UI)
| Manager               | Layer        | Dependencies                    |
|-----------------------|--------------|---------------------------------|
| **StatisticsManager** | Core (Leaf)  | None (pure Python)              |
| **PresetsManager**    | Core (Leaf)  | QSettings only                  |
| **ShortcutManager**   | Core (Leaf)  | QKeySequence, QAction           |
| **ThemeManager**      | Core (Leaf)  | QPalette, QApplication          |
| **LayoutManager**     | UI (Branch)  | QMainWindow, QDockWidget        |

**Import Tree position**: All are **Leaf** nodes (no internal dependencies)

### 3. Static vs Instance Design
| Manager               | Design         | Rationale                       |
|-----------------------|----------------|---------------------------------|
| **LayoutManager**     | Instance       | Needs QMainWindow reference     |
| **PresetsManager**    | Instance       | Needs QSettings instance        |
| **ShortcutManager**   | Static class   | Global shortcuts, no state      |
| **ThemeManager**      | Static class   | App-wide theming, no state      |
| **StatisticsManager** | Static class   | Pure computation, no state      |

### 4. Fail-Safe Design (Graceful Degradation)
All managers exhibit **fail-safe patterns**:
- **LayoutManager**: If load fails → apply Standard preset
- **ShortcutManager**: If no custom shortcut → use default
- **ThemeManager**: If mode unknown → apply system theme
- **PresetsManager**: If no presets → create 3 defaults
- **StatisticsManager**: If JSON invalid → size_bytes = 0

### 5. Two-Tier Styling (Theme Manager)
**QPalette** (base colors):
- Window, Base, Text, Button, Highlight
- 18 color roles × 2 themes = 36 colors

**QSS** (widget details):
- Borders, padding, hover states, focus states
- 278 lines (light) + 244 lines (dark) = 522 lines QSS

**Why hybrid?**
- QPalette: Fast, Qt-native, affects all widgets automatically
- QSS: Fine control, widget-specific styling, animations

### 6. Metrics vs Presets (Statistics vs Presets Manager)
| Manager               | Purpose            | Storage      | Timing            |
|-----------------------|--------------------|--------------|-------------------|
| **StatisticsManager** | Calculate metrics  | None         | On-demand (each op)|
| **PresetsManager**    | Store configs      | QSettings    | Persistent         |

**Complementary**: Statistics shows *results*, Presets stores *inputs*

---

## 🔍 DESIGN PATTERNS CATALOG

### Session 10 Patterns Identified (15 total)

#### Creational Patterns (2)
1. **Static Factory Method** (PresetsManager)
   - `create_preset_from_current()` builds preset dict
   - Encapsulates preset construction logic

2. **Initialization Guard** (PresetsManager)
   - `_ensure_defaults()` runs once on first init
   - Ensures 3 default presets exist

#### Structural Patterns (5)
3. **Facade Pattern** (ThemeManager, ShortcutManager)
   - Single entry point (`apply_theme()`, `get_shortcut()`)
   - Hides internal complexity (QPalette + QSS)

4. **Registry Pattern** (LayoutManager, ShortcutManager)
   - `register_dock()` before operations
   - `SHORTCUTS` dict as static registry

5. **Repository Pattern** (PresetsManager)
   - Abstracts QSettings persistence
   - Provides CRUD interface over storage

6. **Memento Pattern** (LayoutManager)
   - Save/restore QMainWindow state via QByteArray
   - Geometry and dock positions captured

7. **Hybrid Architecture** (ThemeManager)
   - QPalette (base colors) + QSS (widget details)
   - Two-tier styling system

#### Behavioral Patterns (8)
8. **Strategy Pattern** (ThemeManager, ShortcutManager)
   - 3 theme strategies (system/light/dark)
   - Custom shortcuts override defaults

9. **Template Method** (ThemeManager, LayoutManager, StatisticsManager)
   - `apply_theme()` delegates to `_apply_X_theme()`
   - `apply_preset_X()` methods use common `save_layout()`
   - `format_X()` methods share logic

10. **Visitor Pattern** (StatisticsManager)
    - `_analyze_recursive()` visits all JSON nodes
    - Type-specific dispatch (dict/list/primitives)

11. **Accumulator Pattern** (StatisticsManager)
    - Stats dict accumulates during traversal
    - In-place modification for performance

12. **Static Utility Class** (3 managers)
    - No instance creation needed
    - All methods static/classmethod

13. **Fail-Safe Defaults** (All managers)
    - Graceful degradation on errors
    - Fallback to safe defaults

14. **Class-level Singleton** (ShortcutManager)
    - Single state in class variables
    - No instance needed

15. **Conflict Detection** (ShortcutManager, PresetsManager)
    - `get_conflicts()` checks duplicate shortcuts
    - Rename checks for name conflicts

---

## 🔗 INTEGRATION POINTS

### 1. Startup Sequence (app.py)
```python
# Initialization order
app = QApplication([])
theme_manager.apply_theme(app, config.theme)  # Before MainWindow
main_window = MainWindow()
layout_manager = LayoutManager(main_window)
layout_manager.register_dock("editor", editor_dock)
layout_manager.register_dock("search", search_dock)
# ... register all docks
layout_manager.restore_last_layout()
main_window.show()
```

### 2. User Preferences Flow
```
ConfigManager (YAML) → Theme/Layout/Shortcuts
     ↓
Application startup → Load preferences
     ↓
QSettings (per-component) → Presets/Custom layouts
     ↓
Runtime changes → Save back to storage
```

### 3. Set Operations Integration (PresetsManager + StatisticsManager)
```python
# User flow:
1. Load preset from PresetsManager
2. Execute operation (SetOperationsDock)
3. Calculate statistics (StatisticsManager)
4. Display results + stats
5. Option to save as new preset (PresetsManager)
```

### 4. Layout vs Shortcuts vs Theme
| Aspect        | Layout               | Shortcuts            | Theme                |
|---------------|----------------------|----------------------|----------------------|
| **Scope**     | Dock positions       | Key bindings         | Colors/styles        |
| **Persistence**| QSettings            | QSettings (custom)   | ConfigManager (YAML) |
| **UI Control**| View > Layout        | Help > Shortcuts     | Settings > Appearance|
| **Presets**   | 3 built-in           | 86 defaults          | 3 modes              |

### 5. File Explorer Theming
**Collapsible sections** (special styling):
```python
# In ThemeManager QSS:
QPushButton[objectName="collapsible_header"] {
    background-color: #3498db;  # Blue header
    ...
}
QFrame[objectName="collapsible_content"] {
    border: 1px solid #d0d0d0;  # Content border
    ...
}
```
**Why object names?**
- Targets specific File Explorer widgets
- Doesn't affect other QPushButton/QFrame instances
- Requires widget.setObjectName("collapsible_header") in code

---

## 📊 CUMULATIVE STATISTICS

### Code Coverage Progress
- **Phase 3 Session 10**: 5 files, 1,572 LOC
- **Phase 3 Sessions 8-10**: 15 files, 4,492 LOC
- **Phase 2 (Sessions 4-7)**: 18 files, 4,847 LOC
- **Phase 1 (Sessions 1-3)**: 9 files, 6,947 LOC
- **Total studied**: 42 files, 16,286 LOC
- **Total codebase**: 279 Python files, 83,619 LOC
- **Coverage**: 19.5% (vs 17.6% before Session 10)

### Design Patterns Tally
- **Session 10**: 15 patterns identified
- **Phase 3 Sessions 8-10**: 35 patterns (15 + GUI 15 + Search 5)
- **Phase 2**: 44 patterns
- **Phase 1**: 27 patterns
- **Total cataloged**: 106 patterns

### Session Duration
- **Predicted**: 45 minutes
- **Actual**: ~35 minutes (5 small files, clear responsibilities)
- **Efficiency**: 123% (completed faster than estimated)

---

## 🎓 LEARNING OUTCOMES

### 1. Qt Persistence Ecosystem
**QSettings**:
- Cross-platform config storage (Linux: ~/.config, Windows: Registry)
- Automatic type conversion (Python dict ↔ Qt variant)
- Hierarchical keys (beginGroup/endGroup)
- Used by 4/5 managers in this session

**QMainWindow state**:
- `saveGeometry()` / `restoreGeometry()` → window size/position
- `saveState()` / `restoreState()` → dock positions/sizes/areas
- Serialized as QByteArray (opaque binary format)

### 2. Theming Architecture (Industry Best Practices)
**Two-tier approach**:
1. **QPalette**: Base colors (18 roles × 2 states = 36 colors)
2. **QSS**: Widget-specific styling (522 lines total)

**Why not pure QSS?**
- QPalette: Faster, Qt-native, affects all widgets automatically
- QSS: Fine control, but can't set base palette colors efficiently

**Color schemes**:
- Light: Windows 10 inspired (#0078d7 accent)
- Dark: VS Code inspired (#007acc accent, #2d2d30 background)

### 3. Keyboard Shortcut Systems
**86 shortcuts across 7 categories**:
- File (6), Edit (8), Tools (11), Navigation (17), View (6), Processing (3), Help (4)

**Customization pattern**:
1. Define defaults (SHORTCUTS dict)
2. Overlay custom (load_custom_shortcuts)
3. Get effective (get_shortcut checks custom first)
4. Conflict detection (OS shortcuts + duplicates)

**Qt integration**:
- QKeySequence: Cross-platform key representation
- QShortcut: Widget-level shortcut (no need for QAction)
- QAction.setShortcut(): Menu/toolbar shortcuts

### 4. Statistics Calculation (Visitor Pattern in JSON)
**Recursive traversal**:
```python
def visit(node, accumulator):
    if isinstance(node, dict):
        for key, value in node.items():
            count_key(key, accumulator)
            visit(value, accumulator)
    elif isinstance(node, list):
        for item in node:
            visit(item, accumulator)
    else:
        count_primitive(node, accumulator)
```

**Metrics tracked**:
- Structure: total_keys, unique_keys, max_depth
- Content: value_types (6 types)
- Size: JSON.dumps() byte count
- Duplicates: total_keys - unique_keys

### 5. Preset Management Patterns
**CRUD over QSettings**:
- Read: Load list, filter by name
- Create: Append to list, save
- Update: Find by name, replace, save
- Delete: Filter out, save

**Uniqueness by name** (not ID):
- Preset["name"] is unique identifier
- Rename checks for conflicts
- No auto-incrementing IDs

**Default presets**:
- Auto-created on first run
- _ensure_defaults() guards against re-creation

---

## 🚀 NEXT STEPS

### Session 11: Plugin & Extension System (45 min)
Files to study (~800 LOC):
1. `src/plugin_loader.py` - Plugin discovery & loading
2. `src/plugins/__init__.py` - Plugin interface
3. `src/processors/__init__.py` - Processor interface
4. `src/extractors/__init__.py` - Extractor interface
5. Example plugin/processor (1-2 files)

**Expected patterns**:
- Plugin Pattern (core architecture)
- Factory Pattern (plugin instantiation)
- Strategy Pattern (processor selection)
- Registry Pattern (plugin registration)
- Adapter Pattern (plugin interface wrapping)

### Phase 3 Completion
After Session 11:
1. Create **CODE_STUDY_PHASE3_SUMMARY.md** (consolidate Sessions 8-11)
2. Update cumulative statistics (total LOC, patterns, coverage)
3. Commit Phase 3 notes to COM4-code-study branch
4. Present completion report to user

### Decision Point
**Options after Phase 3**:
- **Option A**: Start v2.9.116 Phase 4 implementation (ACTION_PLAN ready)
- **Option B**: Continue studying (Phase 4 - more modules)
- **Option C**: Validation testing before implementation

**Recommendation**: Follow protocol's "incremental as needed" - we have 19.5% coverage, sufficient for Phase 4 implementation.

---

## 📝 METADATA

**Session 10 Metrics**:
- Files studied: 5
- LOC analyzed: 1,572
- Patterns identified: 15
- Duration: ~35 minutes
- Notes size: ~28KB (this file)

**Cumulative Progress**:
- Files: 42/279 (15.1%)
- LOC: 16,286/83,619 (19.5%)
- Patterns: 106 unique
- Study time: ~10h total (Phases 1-3)

**Quality Indicators**:
- ✅ All managers follow Import Tree Analogy (Leaf nodes)
- ✅ Consistent QSettings usage (cross-platform)
- ✅ Fail-safe defaults in all managers
- ✅ Static classes where appropriate (no unnecessary state)
- ✅ Repository pattern for persistence

---

**END OF SESSION 10 NOTES**
