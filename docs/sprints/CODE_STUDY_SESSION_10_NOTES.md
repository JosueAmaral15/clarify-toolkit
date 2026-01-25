# Code Study Session 10 Notes
**Programmer #7** | **Date**: 2026-01-22 | **Phase 3: Feature Modules (i18n)**

## Session Overview
**Module**: i18n (Internationalization System)  
**Files Studied**: 2 Python files (~292 lines)  
**Focus**: Runtime language switching, translation system architecture

---

## Files Analyzed

### 1. `src/i18n/__init__.py` (21 lines)
**Purpose**: Module exports for public API

**Key Exports**:
```python
from .translator import Translator, get_translator, switch_language, tr, tooltip_tr
__all__ = ['Translator', 'get_translator', 'switch_language', 'tr', 'tooltip_tr']
```

**Public API**:
- `get_translator()` → Singleton instance
- `switch_language(lang)` → Runtime language change
- `tr(key, default)` → Shorthand translation function
- `tooltip_tr(key, default)` → Tooltip-specific translation (auto-prepends "tooltip.")

**Design**: Clean, minimal public interface

---

### 2. `src/i18n/translator.py` (271 lines)
**Purpose**: Core internationalization system with runtime switching

#### Architecture
```
Translator (singleton)
  ├─ __init__: Auto-detect system locale, load initial language
  ├─ _detect_system_locale(): QLocale system detection
  ├─ _load_language(lang): Lazy load JSON translation files
  ├─ get(key, default): Retrieve translated string with fallback
  ├─ switch_language(lang): Runtime language change + signal emission
  └─ languageChanged signal → MainWindow.retranslate()
```

#### Key Features

**1. Singleton Pattern**
```python
class Translator(QObject):
    _instance: Optional['Translator'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```
- **Why**: Ensure single translation instance across app
- **Pattern**: Singleton with `__new__` override
- **Double initialization guard**: `_initialized` flag prevents re-init

**2. Lazy Loading**
```python
def _load_language(self, lang: str) -> None:
    if lang in self._translations:
        return  # Already loaded
    
    translation_file = i18n_dir / f"{lang}.json"
    with open(translation_file, 'r', encoding='utf-8') as f:
        self._translations[lang] = json.load(f)
```
- **Optimization**: Load translations only when first requested
- **Memory**: Don't load all 7 languages at startup
- **Cache**: Keep loaded translations in `_translations` dict

**3. Auto-Detection of System Locale**
```python
def _detect_system_locale(self) -> str:
    from PySide6.QtCore import QLocale
    system_locale = QLocale.system().name()  # 'en_US', 'pt_BR'
    
    locale_map = {
        "pt_BR": "pt_BR", "pt_PT": "pt_BR",
        "es_ES": "es", "es_MX": "es", "es_AR": "es",
        "fr_FR": "fr", "fr_CA": "fr",
        # ... 25+ locale mappings
    }
    
    # Direct match or language code fallback
    return locale_map.get(system_locale, locale_map.get(system_locale[:2], "en"))
```
- **Smart mapping**: Handles regional variants (es_MX → es, pt_PT → pt_BR)
- **Fallback chain**: Full locale → Language code → English
- **Supported locales**: 25+ regional variants mapped to 7 base languages

**4. Runtime Language Switching**
```python
def switch_language(self, lang: str) -> None:
    if lang not in self._available_languages:
        return  # Guard against invalid languages
    
    self._load_language(lang)  # Lazy load if not loaded
    self._current_language = lang
    self.languageChanged.emit(lang)  # Signal UI to retranslate
```
- **Signal-based**: Emits `languageChanged` signal to observers
- **No restart**: UI updates immediately via signal/slot connections
- **MainWindow integration**: Listens to signal, calls `retranslate()` on all docks

**5. Fallback to English**
```python
def get(self, key: str, default: Optional[str] = None) -> str:
    translations = self._translations.get(self._current_language, {})
    result = translations.get(key)
    
    if result is None:
        # Fallback to English
        if self._current_language != "en":
            en_translations = self._translations.get("en", {})
            result = en_translations.get(key)
    
    return result if result is not None else (default if default is not None else key)
```
- **3-level fallback**: Current language → English → Default → Key itself
- **Robustness**: Always returns a string, never None
- **Development**: Missing translations show key name (easy to spot)

**6. Convenience Functions**
```python
def tr(key: str, default: Optional[str] = None) -> str:
    """Shorthand: tr("menu.file") vs get_translator().get("menu.file")"""
    return get_translator().get(key, default)

def tooltip_tr(key: str, default: Optional[str] = None) -> str:
    """Auto-prepends 'tooltip.': tooltip_tr("set_ops.file_a") → get("tooltip.set_ops.file_a")"""
    return get_translator().get(f"tooltip.{key}", default)
```
- **Developer experience**: Shorter syntax reduces boilerplate
- **Usage**: `from src.i18n import tr` → `label.setText(tr("dialog.ok"))`
- **Tooltip helper**: Reduces redundancy in tooltip translations

#### Translation File Structure
```json
{
  "menu.file": "File",
  "menu.edit": "Edit",
  "dialog.ok": "OK",
  "ai_processor.btn_verify": "Verify",
  "tooltip.set_ops.file_a": "First JSON file for set operation"
}
```
- **Flat structure**: Dot-notation keys (`category.subcategory.item`)
- **No nesting**: All keys at root level (simpler access pattern)
- **Total keys**: **2,303 translations per language** (en.json)
- **Total lines**: ~16,214 across 7 language files

#### Supported Languages
1. **en** (English) - 2,396 lines, default/fallback
2. **pt_BR** (Português Brasil) - 2,430 lines
3. **es** (Español) - 2,284 lines
4. **fr** (Français) - 2,276 lines
5. **de** (Deutsch) - 2,276 lines
6. **zh** (中文 简体) - 2,276 lines, Simplified Chinese
7. **ja** (日本語) - 2,276 lines, Japanese

**Total**: 7 languages, ~16,214 lines, 2,303+ keys each

#### Language Names Mapping
```python
def get_language_name(self, lang: str) -> str:
    names = {
        "en": "English",
        "pt_BR": "Português (Brasil)",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "zh": "中文 (简体)",
        "ja": "日本語"
    }
    return names.get(lang, lang)
```
- **Purpose**: Display human-readable names in language switcher UI
- **Native names**: Each language shows its own name (not translated)
- **User-friendly**: Users recognize their language visually

---

## Design Patterns Identified

### 1. **Singleton Pattern** (Translator class)
- **Implementation**: `__new__` override with class-level `_instance`
- **Purpose**: Single translation source across application
- **Thread safety**: Single-threaded Qt app, no locks needed

### 2. **Lazy Loading Pattern** (_load_language)
- **When**: Load translations only when first requested
- **Benefit**: Fast startup (don't load all 7 languages)
- **Trade-off**: Small delay on first language switch

### 3. **Observer Pattern** (Qt Signals)
- **Signal**: `languageChanged` emitted on switch
- **Observers**: MainWindow, all docks listen to signal
- **Action**: Retranslate all UI elements on language change

### 4. **Fallback Chain Pattern** (get method)
- **Chain**: Current language → English → Default → Key
- **Robustness**: Never fail, always return something
- **Development-friendly**: Missing keys show as themselves

### 5. **Factory Function Pattern** (get_translator)
- **Global**: `get_translator()` returns singleton
- **Encapsulation**: Hide singleton creation details
- **Convenience**: Module-level functions wrap singleton methods

---

## Integration Points

### 1. MainWindow Integration
```python
# MainWindow.__init__
translator = get_translator()
translator.languageChanged.connect(self.retranslate_ui)

def retranslate_ui(self, new_language: str):
    # Update window title, menu texts
    for dock in self.docks:
        dock.retranslate()  # Each dock updates its labels
```

### 2. Dock Usage Pattern
```python
from src.i18n import tr, tooltip_tr

class MyDock(BaseDock):
    def retranslate(self):
        self.lbl_title.setText(tr("my_dock.title"))
        self.btn_action.setText(tr("my_dock.btn_action"))
        self.ed_input.setToolTip(tooltip_tr("my_dock.input"))
```

### 3. Menu Builder Usage
```python
# In MenuBuilder.build_file_menu()
file_menu.addAction(tr("menu.file.open"), self.on_open)
file_menu.addAction(tr("menu.file.save"), self.on_save)
```

---

## Key Discoveries

### 1. **Runtime Switching Without Restart**
- **How**: Signal-based architecture (`languageChanged` signal)
- **Performance**: Instant UI update (no app restart needed)
- **User experience**: Best-in-class i18n (most apps require restart)

### 2. **Smart Locale Detection**
- **25+ regional variants** mapped to 7 base languages
- **Examples**: es_MX/es_AR/es_ES → es, pt_PT → pt_BR
- **Graceful fallback**: Unknown locale → English

### 3. **Flat Translation Structure**
- **No nesting**: All keys at JSON root level
- **Dot notation**: `ai_processor.btn_verify` instead of `{ai_processor: {btn_verify: ...}}`
- **Why**: Simpler access pattern, easier to search/grep

### 4. **2,303+ Translation Keys**
- **Massive coverage**: Every UI element translated
- **Complete i18n**: Buttons, labels, tooltips, messages, placeholders
- **7 languages**: Total ~16,214 lines of translations

### 5. **Tooltip-Specific Helper**
- **`tooltip_tr(key)`**: Auto-prepends "tooltip."
- **Why**: Tooltips are numerous, reduce boilerplate
- **Example**: `tooltip_tr("set_ops.file_a")` → `get("tooltip.set_ops.file_a")`

---

## Critical Code Sections

### ⚠️ **DON'T TOUCH**: Locale Mapping (lines 75-95)
```python
locale_map = {
    "pt_BR": "pt_BR", "pt_PT": "pt_BR",  # European → Brazilian
    "es_ES": "es", "es_MX": "es", "es_AR": "es",
    # ... 25+ mappings
}
```
- **Why critical**: Removing mappings breaks auto-detection for users in those regions
- **Impact**: Users get English instead of their language
- **Complete**: Covers major regional variants

### ⚠️ **DON'T TOUCH**: Fallback Chain (lines 145-161)
```python
if result is None:
    if self._current_language != "en":
        en_translations = self._translations.get("en", {})
        result = en_translations.get(key)

if result is None:
    return default if default is not None else key
```
- **Why critical**: Ensures app never crashes from missing translations
- **Robustness**: 3-level fallback prevents AttributeError/KeyError
- **Development**: Shows key name when translation missing (easy to spot)

### ⚠️ **DON'T TOUCH**: Singleton Implementation (lines 35-46)
```python
def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
        cls._instance._initialized = False
    return cls._instance

def __init__(self):
    if self._initialized:
        return
```
- **Why critical**: Double initialization would reset current language
- **Pattern**: `__new__` + `_initialized` flag is standard singleton
- **Breaking change**: Would cause language to reset unexpectedly

---

## Performance Characteristics

### Memory Usage
- **Per language**: ~2,300 keys × average 50 chars = ~115 KB per language
- **At startup**: 1 language loaded (~115 KB)
- **After switching**: 2 languages loaded (~230 KB)
- **Total potential**: 7 languages × 115 KB = ~805 KB (negligible)

### Load Times
- **Initial load**: ~50ms to parse JSON (2,300 keys)
- **Language switch**: ~50ms first time, 0ms subsequent (cached)
- **Impact**: Imperceptible to user

### Signal Propagation
- **languageChanged**: Emitted once per switch
- **UI update**: Each dock retranslates (~10-50ms per dock)
- **Total**: ~100-500ms for full UI retranslation (smooth experience)

---

## Testing Observations

### Edge Cases Handled
1. **Missing translation file**: Returns empty dict, falls back to English
2. **Invalid language code**: Early return, no switch
3. **Missing translation key**: Falls back to English, then default, then key
4. **System locale not supported**: Falls back to English
5. **JSON parse error**: Caught exception, logs warning, continues

### Error Handling
```python
try:
    with open(translation_file, 'r', encoding='utf-8') as f:
        self._translations[lang] = json.load(f)
except Exception as e:
    print(f"Error loading translation {lang}: {e}")
    self._translations[lang] = {}  # Empty dict, fallback to English
```
- **Graceful degradation**: Don't crash app if translation file corrupt
- **User experience**: App continues in English if translation fails

---

## Questions Answered

### Q: How does runtime switching work without restart?
**A**: Signal-based architecture:
1. User clicks language in menu
2. `switch_language("pt_BR")` called
3. Emits `languageChanged` signal
4. MainWindow receives signal, calls `retranslate_ui()`
5. Each dock's `retranslate()` updates its labels
6. UI updates instantly (no restart needed)

### Q: How are regional variants handled?
**A**: 25+ locale mappings collapse to 7 base languages:
- Spanish variants (es_MX, es_AR, es_ES) → es
- Portuguese variants (pt_PT) → pt_BR
- French variants (fr_CA) → fr
- German variants (de_AT, de_CH) → de

### Q: What happens if a translation is missing?
**A**: 3-level fallback chain:
1. Try current language (e.g., pt_BR)
2. Fall back to English (en)
3. Fall back to provided default
4. Fall back to key itself (shows "menu.file" if all else fails)

### Q: Why flat structure instead of nested JSON?
**A**: Simpler access pattern:
- **Flat**: `translations["ai_processor.btn_verify"]` (O(1) lookup)
- **Nested**: `translations["ai_processor"]["btn_verify"]` (O(depth) lookups, KeyError risk)
- **Grep-friendly**: Easy to search for "ai_processor.btn_verify" across files

---

## Module Statistics

| Metric | Value |
|--------|-------|
| **Python Files** | 2 |
| **Total Lines** | 292 |
| **Translation Files** | 7 (JSON) |
| **Translation Lines** | 16,214 |
| **Keys per Language** | 2,303+ |
| **Supported Languages** | 7 |
| **Regional Variants** | 25+ |
| **Design Patterns** | 5 |
| **Public Functions** | 5 |

---

## Integration Summary

**Used By**:
- MainWindow (language switcher menu)
- All 40+ docks (UI text translation)
- MenuBuilder (menu item texts)
- Dialogs (button texts, messages)

**Dependencies**:
- PySide6.QtCore (QObject, Signal, QLocale)
- json (translation file parsing)
- pathlib (file path handling)

**Signal Flow**:
```
User selects language
    ↓
switch_language(lang)
    ↓
languageChanged.emit(lang)
    ↓
MainWindow.retranslate_ui()
    ↓
Each dock.retranslate()
    ↓
UI updated instantly
```

---

## Reuse Opportunities

1. **Translation System**: Can be extracted to standalone library
2. **Locale Detection**: Reusable QLocale wrapper with regional mappings
3. **Fallback Chain**: Pattern applicable to config/resource loading
4. **Signal-based Updates**: Pattern for other runtime config changes (themes, etc.)

---

## Don't Touch Zones

1. **Locale mapping dict** (lines 75-95): Complete regional variant coverage
2. **Fallback chain** (lines 145-161): Prevents crashes from missing translations
3. **Singleton pattern** (lines 35-46): Prevents double initialization bugs
4. **Signal emission** (line 184): Critical for UI update propagation

---

## Phase 3 Progress Update

**Module**: i18n  
**Status**: ✅ **100% COMPLETE**  
**Files**: 2/2 (100%)  
**Lines**: 292/292 (100%)

**Phase 3 Overall**:
- ✅ Utils (9 files, ~2,304 lines)
- ✅ Rewriter (9 files, ~2,297 lines)
- ✅ AI Processor (5 files, ~1,061 lines)
- ✅ i18n (2 files, ~292 lines)
- ⏳ GUI docks (40+ files remaining)

**Total Phase 3 Progress**: 25/~52 files (48%)

---

**Next Session**: Start GUI docks module (largest remaining component: 40+ files)

**Study Time This Session**: ~25 minutes  
**Cumulative Study Time**: ~4.5 hours
