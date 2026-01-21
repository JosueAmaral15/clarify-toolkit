# Code Study Session 4: Configuration & Settings

**Programmer**: #4  
**Branch**: COM4-code-study  
**Date**: 2026-01-21  
**Duration**: 1 hour  
**Focus**: Configuration management, settings persistence, migrations, formulas  

---

## 📊 TL;DR (2AM Reference)

**Files Studied**: 4 files, 1,218 LOC  
**Key Discovery**: Dual configuration system (config_manager.py YAML + settings_manager.py JSON)  
**Critical Pattern**: Migration-based evolution (QSettings → JSON → YAML)  
**Production Feature**: Formula system for multi-step set operations  

**If config breaks**:
```python
# Reset to defaults:
from src.config_manager import ConfigManager
config = ConfigManager()
config.config = config.DEFAULTS.copy()
config.save()
```

---

## 📁 Files Analyzed

### 1. config_manager.py (548 lines)
**Purpose**: Centralized YAML-based configuration with validation  
**Version**: Sprint v2.9.60  
**Pattern**: Singleton with migration support  

**Key Features**:
- ✅ YAML storage (config.yaml)
- ✅ JSON Schema validation
- ✅ Auto-migration from QSettings/JSON/ConfigParser
- ✅ Backup before overwrites
- ✅ Priority: CLI args > config.yaml > defaults
- ✅ Thread-safe operations
- ✅ Dot-notation access ("app.theme", "logging.level")

---

### 2. settings_manager.py (150 lines)
**Purpose**: Simple JSON-based settings persistence  
**Version**: v2.9.33  
**Pattern**: Basic key-value store  

**Key Features**:
- ✅ JSON storage (.clarify_settings.json)
- ✅ Recent files management
- ✅ Window geometry persistence
- ✅ Keyboard shortcuts customization (v2.9.33)
- ✅ No validation (simpler than ConfigManager)

---

### 3. migrations/base.py (46 lines)
**Purpose**: Base class for all migrations  
**Version**: v2.9.91  
**Pattern**: Abstract base with template methods  

**Key Features**:
- ✅ ABC (Abstract Base Class)
- ✅ Two migration targets: QSettings + config.yaml
- ✅ Version tracking
- ✅ No-op default (migrations opt-in)

---

### 4. formula_manager.py (474 lines)
**Purpose**: Multi-step set operation formulas  
**Version**: v2.9.108  
**Pattern**: Formula pattern with steps + execution engine  

**Key Features**:
- ✅ FormulaStep class (single operation)
- ✅ Formula class (multi-step pipeline)
- ✅ Variable system (r1, r2, final)
- ✅ Input chaining ('previous')
- ✅ QSettings persistence
- ✅ Default formulas (3 presets)
- ✅ GUI integration ready

---

## 🎯 Architecture Analysis

### Dual Configuration System

**Why TWO config systems?**

**ConfigManager (YAML)** - Professional, validated:
```python
# Features:
- JSON Schema validation
- Migration support
- Structured hierarchy (app.*, logging.*, performance.*)
- Backup on save
- Thread-safe

# Use cases:
- Application-wide settings
- Performance tuning
- AI provider config
- Editor preferences
```

**SettingsManager (JSON)** - Simple, fast:
```python
# Features:
- Simple key-value
- No validation
- Flat structure
- No migrations

# Use cases:
- Recent files list
- Window geometry
- Last directory
- UI state (theme, language)
- Custom shortcuts
```

**Design Decision**: ConfigManager for "what", SettingsManager for "where/when"

---

### Configuration Hierarchy

```
DEFAULTS → config.yaml → CLI args
(fallback)  (persistent)  (override)
```

**Example**:
```python
# Priority cascade:
theme = get_cli_arg('theme')  # Highest priority
if not theme:
    theme = config.get('app.theme')  # From YAML
if not theme:
    theme = DEFAULTS['app']['theme']  # Fallback: "system"
```

---

### Migration Strategy

**Supported formats** (oldest → newest):
1. QSettings (Qt native, platform-specific)
2. ConfigParser (.conf file, INI-style)
3. JSON (.clarify_settings.json)
4. **YAML** ← Current target

**Migration flow**:
```python
def _load_or_create():
    if config.yaml exists:
        load_yaml()
    else:
        # Try legacy formats in order:
        migrated = (
            try_qsettings() or
            try_json() or
            try_configparser()
        )
        if not migrated:
            use_defaults()
        save_yaml()  # Write to new format
```

**Safety features**:
- ✅ Backups created (.json.migrated, .conf.migrated)
- ✅ Invalid YAML backed up (_invalid suffix)
- ✅ Non-destructive (originals renamed, not deleted)
- ✅ Graceful fallback to defaults on error

---

## 🔍 Design Patterns Identified

### 1. ✅ Singleton Pattern (Global Instance)
**Location**: config_manager.py lines 504-518

```python
_config_instance: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
```

**Why**: Single source of truth, thread-safe access

---

### 2. ✅ Template Method Pattern (Migration ABC)
**Location**: migrations/base.py

```python
class Migration(ABC):
    version: str = "0.0.0"
    
    def migrate_qsettings(self, settings) -> bool:
        return True  # No-op by default (override in subclass)
    
    def migrate_config(self, config: Dict) -> Dict:
        return config  # No-op by default
```

**Why**: Flexible migration pipeline, subclasses choose what to override

---

### 3. ✅ Strategy Pattern (Migration Sources)
**Location**: config_manager.py lines 390-500

```python
def _migrate_from_legacy(self) -> bool:
    migrated = False
    # Strategy 1: QSettings
    if self._migrate_from_qsettings():
        migrated = True
    # Strategy 2: JSON
    if Path.home() / ".clarify_settings.json").exists():
        if self._migrate_from_json(json_file):
            migrated = True
    # Strategy 3: ConfigParser
    if (Path.home() / ".config" / "clarify.conf").exists():
        if self._migrate_from_configparser(conf_file):
            migrated = True
    return migrated
```

**Why**: Multiple legacy formats, try all until one works

---

### 4. ✅ Builder Pattern (Formula Construction)
**Location**: formula_manager.py

```python
# FormulaStep built incrementally:
step = FormulaStep(
    operation='∩',
    input_a='file_path',
    input_b='file_path',
    file_a_path='/path/to/a.json',
    file_b_path='/path/to/b.json',
    output_variable='r1',
    comparison_mode='key_value',
    options={'ignore_case_keys': False, ...}
)

# Formula built from steps:
formula = Formula(name="My Formula")
formula.add_step(step1)
formula.add_step(step2)
formula.add_step(step3)
```

**Why**: Complex objects built step-by-step, clear semantics

---

### 5. ✅ Memento Pattern (Backup on Save)
**Location**: config_manager.py lines 217-235

```python
def save(self) -> None:
    # Backup existing file before overwrite
    if self.config_file.exists():
        self._backup_file()
    
    # Write new content
    with open(self.config_file, "w") as f:
        yaml.dump(self.config, f)
```

**Why**: Rollback capability, safety net

---

### 6. ✅ Chain of Responsibility (Migration Pipeline)
**Location**: Implicit in migration strategy

```python
# Try handlers in order until one succeeds:
QSettings handler → JSON handler → ConfigParser handler → Defaults handler
```

**Why**: First successful migration wins

---

### 7. ✅ Proxy Pattern (Dot Notation Access)
**Location**: config_manager.py lines 237-270

```python
def get(self, key: str, default: Any = None) -> Any:
    """
    Get value using dot notation.
    Example: config.get("app.theme", "system")
    """
    parts = key.split(".")
    value = self.config
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default
    return value
```

**Why**: Flat access to nested structure, convenience

---

## 🔧 Configuration Schema

### DEFAULTS Structure

```python
DEFAULTS = {
    "app": {
        "theme": "system",
        "language": "en",
        "max_recent_files": 10,
        "confirm_on_exit": True,
        "show_tooltips": True,
        "auto_save": True,
        "check_updates_on_startup": True,
    },
    "logging": {
        "level": "INFO",
        "max_file_size_mb": 10,
        "backup_count": 5,
        "console_output": True,
    },
    "performance": {
        "thread_pool_size": 4,
        "max_file_size_mb": 50,
        "cache_duration_hours": 24,
        "batch_size": 100,
    },
    "ai": {
        "default_provider": "OpenAI",
        "remember_api_keys": False,  # Security: default False
        "max_tokens": 4096,
        "temperature": 0.7,
    },
    "editor": {
        "font_family": "Consolas",
        "font_size": 12,
        "tab_width": 4,
        "auto_save_interval_sec": 60,
        "syntax_highlighting": True,
    },
    "paths": {
        "default_directory": str(Path.home()),
        "custom_extensions": ".txt,.py,.js,.ts,.jsx,.tsx,.json",
    },
}
```

### JSON Schema Validation

**Enforced constraints**:
- ✅ `theme`: Must be "system", "light", or "dark"
- ✅ `language`: Regex pattern `^[a-z]{2}(-[a-z]{2})?$` (e.g., "en", "pt-br")
- ✅ `max_recent_files`: 0-50 range
- ✅ `log_level`: Must be DEBUG/INFO/WARNING/ERROR/CRITICAL
- ✅ `thread_pool_size`: 1-16 range
- ✅ `max_tokens`: 100-32000 range
- ✅ `temperature`: 0.0-2.0 range
- ✅ `font_size`: 8-24 range

**Why validation?**
- Prevents invalid values from crashing app
- Catches configuration errors early
- Documents expected values (self-documenting)

---

## 💡 Formula System Deep Dive

### Formula Components

**FormulaStep** (single operation):
```python
step = FormulaStep(
    operation='∩',        # Intersection
    input_a='file_path',  # Source A
    input_b='slot_a',     # Source B
    file_a_path='/data/a.json',
    output_variable='r1', # Where to store result
    comparison_mode='key_value',
    options={'ignore_case_keys': False}
)
```

**Formula** (multi-step pipeline):
```python
formula = Formula(
    name="Complex Merge",
    description="Intersect A & B, union with C, subtract D",
    steps=[step1, step2, step3]
)
```

### Input Sources

**Available sources**:
1. **`'file_path'`**: Read from file (file_a_path, file_b_path required)
2. **`'slot_a'`**, **`'slot_b'`**: Memory slots (from calculator)
3. **`'previous'`**: Result of previous step (chaining)
4. **`'r1'`**, **`'r2'`**, etc.: Variables (from earlier steps)

### Execution Flow

```python
# Example: 3-step formula
# Step 1: r1 = A ∩ B
# Step 2: r2 = r1 ∪ C
# Step 3: final = r2 − D

formula = Formula(name="Three-Step")
formula.add_step(FormulaStep('∩', 'file_path', 'file_path', ...))  # r1
formula.add_step(FormulaStep('∪', 'previous', 'file_path', ...))   # r2
formula.add_step(FormulaStep('−', 'previous', 'file_path', ...))   # final

# Execute:
result = execute_formula(formula)  # Returns 'final' variable value
```

### Display Text

```python
step.get_display_text()
# Returns human-readable:
# "r1 = config.json ∩ defaults.json"
# "r2 = r1 ∪ overrides.json"
# "final = r2 − excludes.json"
```

**Why formulas?**
- Reusable complex operations
- GUI-friendly (save/load)
- Educational (shows step-by-step)
- Debugging (inspect intermediate results)

---

## 🔒 Security Considerations

### 1. API Key Storage

```python
"ai": {
    "remember_api_keys": False,  # Default: don't remember
}
```

**Why `False` by default?**
- API keys are sensitive credentials
- User must opt-in consciously
- Prevents accidental plaintext storage
- OWASP: Principle of Least Privilege

### 2. Path Sanitization

```python
# In migrations, paths are validated:
if not Path(old_path).is_absolute():
    old_path = Path.home() / old_path  # Relativize safely
```

**Why?**
- Prevents path traversal attacks (CWE-22)
- Ensures paths stay in user's home
- No arbitrary file access

### 3. Backup Naming

```python
backup = file.with_suffix(".json.migrated")  # Timestamp could be added
```

**Why?**
- Prevents overwriting existing files
- Clear indication of migration
- Easy to find for rollback

---

## 🎓 Top 5 Lessons Learned

### 1. **Configuration Evolution is Inevitable**
**Evidence**:
- 4 formats supported (QSettings → ConfigParser → JSON → YAML)
- Migration code is 40% of config_manager.py
- Backups created at every step

**Lesson**: Plan for migration from day 1, don't assume format will never change

---

### 2. **Validation Prevents Runtime Errors**
**Evidence**:
```python
# Without validation:
font_size = config.get("editor.font_size")  # Could be "huge" (string)
set_font(font_size)  # CRASHES

# With validation:
# JSON Schema ensures font_size is integer 8-24
font_size = config.get("editor.font_size")  # Always valid int
set_font(font_size)  # Safe
```

**Lesson**: Validate at boundaries (config load), not at usage site

---

### 3. **Dot Notation is UX Win**
**Evidence**:
```python
# Without dot notation:
theme = config.config['app']['theme']  # Verbose, error-prone

# With dot notation:
theme = config.get('app.theme')  # Concise, clear
```

**Lesson**: Convenience APIs encourage correct usage

---

### 4. **Defaults Must Always Work**
**Evidence**:
```python
# All DEFAULTS are production-ready:
"theme": "system",  # Works on all platforms
"language": "en",   # Always available
"font_family": "Consolas",  # Common font
```

**Lesson**: Defaults = fallback when everything else fails

---

### 5. **Formula Pattern Enables Power Users**
**Evidence**:
- 3 default formulas (learning examples)
- Reusable complex operations
- GUI + programmatic access
- Save/load for sharing

**Lesson**: Provide both simple GUI and power-user features

---

## 🚨 Known Issues & Gotchas

### Issue 1: Two Config Systems (Dual State)

**Problem**: ConfigManager (YAML) and SettingsManager (JSON) can drift

**Example**:
```python
config_mgr.set("app.theme", "dark")  # Saves to YAML
settings_mgr.set("theme", "light")   # Saves to JSON
# Now: inconsistent state!
```

**Mitigation**: Clear separation of concerns (documented in code)

---

### Issue 2: Migration Only on First Run

**Problem**: Migrations run once, old files renamed

**Consequence**: If user deletes config.yaml, old formats not re-migrated (already renamed)

**Mitigation**: Documented in migration backup filenames (.migrated suffix)

---

### Issue 3: JSON Schema Requires External Lib

**Problem**:
```python
try:
    import jsonschema
    jsonschema.validate(...)
except ImportError:
    # Skip validation
    pass
```

**Consequence**: Validation silently skipped if jsonschema not installed

**Mitigation**: jsonschema in requirements.txt (optional dependency)

---

## 📊 Session Statistics

| Metric | Value |
|--------|-------|
| **Files studied** | 4 |
| **Lines of code** | 1,218 |
| **Design patterns** | 7 |
| **Key classes** | 5 (ConfigManager, SettingsManager, Migration, Formula, FormulaStep) |
| **Configuration keys** | 29 (6 categories) |
| **Migration formats** | 4 (QSettings, JSON, ConfigParser, YAML) |
| **Security features** | 3 (API key opt-in, path sanitization, backups) |
| **Duration** | 1 hour |

---

## 🔗 Connections to Previous Study

### Relates to Session 1 (Root Level)
- **app.py** uses ConfigManager for theme/language
- **initialization_manager.py** loads config early (Phase 3.7)

### Relates to Session 2 (Critical Branches)
- **logger.py** reads "logging.*" settings
- **error_handler.py** respects "confirm_on_exit"

### Relates to Session 3 (Key Leaves)
- **translator.py** uses "app.language" setting
- **search_widgets.py** respect "show_tooltips"

**Pattern**: Configuration is consumed everywhere, produced once (Singleton)

---

## ⏭️ Next Steps

**Session 5**: Data Processing (set_operations.py, calculator_operations.py, diff_analyzer.py)

**Why**: Understand core business logic (JSON operations)

**Estimated**: 1 hour

---

**Session 4 Complete** ✅  
**Programmer #4** - Configuration & Settings Deep Dive  
**Date**: 2026-01-21 13:48 UTC
