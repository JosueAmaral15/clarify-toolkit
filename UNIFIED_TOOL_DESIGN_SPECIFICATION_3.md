# Unified Text to JSON Converter - Design Specification

**Date:** 2026-01-30  
**Programmer:** #3  
**Phase:** 2 - Design

---

## 🎯 Design Goals

**Merge:** Advanced Extractor + Text to JSON Converter  
**Remove:** Text Extractor (completely)  
**Result:** 1 unified "Text to JSON Converter" with 2 modes  
**UI Pattern:** Mode dropdown selector at top

---

## 🎨 UI Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Text to JSON Converter                                  [X] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Mode: [▼ Format Conversion ▼]                             │
│        ├─ Format Conversion                                 │
│        └─ JSX/HTML Extraction                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  [Current mode UI appears here dynamically]          │   │
│  │                                                       │   │
│  │  Either:                                              │   │
│  │  - Format Conversion UI (existing Text to JSON)      │   │
│  │  - JSX Extraction UI (Advanced Extractor)            │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 Mode Selector Design

**Position:** Top of window, below title  
**Type:** QComboBox dropdown  
**Options:**
1. "Format Conversion" (default)
2. "JSX/HTML Extraction"

**Behavior:**
- Switching mode completely replaces the UI below
- Each mode has its own layout
- Mode selection saved in settings (remember last used)

---

## 🔄 Mode 1: Format Conversion

**Source:** Existing Text to JSON Converter UI  
**Features:** All current features preserved

**UI Components:**
- Format selector dropdown (Key-Value, List, CSV, Python Dict, YAML, INI, TOML, Java Properties, TOON, Auto)
- Input text area
- Output text area
- Type inference checkbox
- CSV options (header, separator, format)
- Buttons: Convert, Templates, History, Validate, Swap, Copy, Open in Editor
- Live preview with debounce

**No changes to this mode - keep existing functionality 100%**

---

## 🔄 Mode 2: JSX/HTML Extraction

**Source:** Advanced Extractor UI  
**Features:** All Advanced Extractor features

**UI Components (from Advanced Extractor):**

### Section 1: Path Input
- Path input field (file or directory)
- Browse button
- Is file checkbox

### Section 2: Mode & Parameter
- Mode combo: JSX, Tags, Generic, Paths
- Parameter input field
- Is attribute checkbox

### Section 3: Generic Delimiters (shown when mode = Generic)
- Start regex field
- End regex field

### Section 4: Options (11 checkboxes in grid)
Row 1:
- Include key
- Include value
- Drop standard tags

Row 2:
- Only strings
- Quotation marks
- Match all

Row 3:
- TypeScript export ⭐
- Exclude numeric keys ⭐

Row 4:
- Skip empty values ⭐

### Section 5: Case & Limits
- Case style combo (snake, camel, pascal, kebab)
- Uppercase checkbox
- Limit input
- Avoid cut checkbox
- Indent spinner

### Section 6: Avoid Keys
- Avoid keys input field
- Radio buttons: Equals / Contains

### Section 7: Extensions
- Extensions input field

### Section 8: Action Buttons
- Extract button
- Clear button

### Section 9: Output Tabs
- Tab 1: Paths (plain text output)
- Tab 2: JSON (structured output)

**Context menus and all other Advanced Extractor features preserved**

---

## 🏗️ Technical Architecture

### Class Structure

```python
class UnifiedTextToJsonDock(BaseDock):
    """
    Unified Text to JSON Converter with two modes:
    1. Format Conversion (CSV, YAML, INI → JSON)
    2. JSX/HTML Extraction (extract from code)
    """
    
    def __init__(self, parent=None):
        super().__init__(tr("text_to_json.title"), parent)
        self.current_mode = "format_conversion"  # Default
        
    def _setup_ui(self):
        """Setup main UI with mode selector."""
        main_layout = QVBoxLayout()
        
        # Mode selector at top
        mode_section = self._create_mode_selector()
        main_layout.addLayout(mode_section)
        
        # Container for dynamic mode UI
        self.mode_container = QWidget()
        self.mode_layout = QVBoxLayout(self.mode_container)
        main_layout.addWidget(self.mode_container)
        
        # Load default mode
        self._switch_mode(self.current_mode)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setWidget(container)
    
    def _create_mode_selector(self):
        """Create mode selector dropdown."""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(tr("text_to_json.mode", "Mode:")))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(tr("text_to_json.mode_format", "Format Conversion"), "format_conversion")
        self.mode_combo.addItem(tr("text_to_json.mode_extraction", "JSX/HTML Extraction"), "jsx_extraction")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        
        layout.addWidget(self.mode_combo)
        layout.addStretch()
        
        return layout
    
    def _on_mode_changed(self, index):
        """Handle mode switch."""
        mode_key = self.mode_combo.itemData(index)
        self._switch_mode(mode_key)
    
    def _switch_mode(self, mode_key):
        """Switch between modes by replacing UI."""
        # Clear current UI
        self._clear_mode_container()
        
        # Load new mode UI
        if mode_key == "format_conversion":
            self._load_format_conversion_ui()
        elif mode_key == "jsx_extraction":
            self._load_jsx_extraction_ui()
        
        self.current_mode = mode_key
    
    def _clear_mode_container(self):
        """Remove all widgets from mode container."""
        while self.mode_layout.count():
            item = self.mode_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _load_format_conversion_ui(self):
        """Load Format Conversion UI (from Text to JSON)."""
        # Copy existing Text to JSON UI creation code
        # All format conversion widgets
        pass
    
    def _load_jsx_extraction_ui(self):
        """Load JSX Extraction UI (from Advanced Extractor)."""
        # Copy existing Advanced Extractor UI creation code
        # All extraction widgets
        pass
```

---

## 📦 Backend Integration

### Mode 1: Format Conversion
- Uses: `src/text_to_json.py` (624 lines)
- No changes needed
- All conversion functions preserved

### Mode 2: JSX Extraction
- Uses: `src/extractors/advanced_extractor.py` (708 lines)
- No changes needed
- All extraction features preserved

---

## 🎛️ Menu Changes

### Before:
```
Tools
├── Text Extractor          ← REMOVE
├── Advanced Extractor      ← REMOVE
└── Text to JSON Converter  ← KEEP (but enhanced)
```

### After:
```
Tools
└── Text to JSON Converter  ← UNIFIED TOOL
    ├── Mode 1: Format Conversion
    └── Mode 2: JSX/HTML Extraction
```

---

## 💾 Settings Persistence

**Save in user settings:**
- Last used mode (format_conversion or jsx_extraction)
- Last used format (if format_conversion mode)
- Last used extraction options (if jsx_extraction mode)

**On launch:**
- Restore last used mode
- Restore last used settings for that mode

---

## 🔧 Implementation Plan

### Step 1: Create New Unified Class (2 hours)
- Create `unified_text_to_json_dock.py`
- Implement mode selector
- Implement mode switching logic
- Create empty placeholders for both modes

### Step 2: Integrate Format Conversion (1 hour)
- Copy UI creation from `text_to_json_dock.py`
- Adapt to work in `_load_format_conversion_ui()`
- Wire all buttons and events
- Test format conversion works

### Step 3: Integrate JSX Extraction (2 hours)
- Copy UI creation from `advanced_extractor_dock.py`
- Adapt to work in `_load_jsx_extraction_ui()`
- Wire extraction button and events
- Test JSX extraction works

### Step 4: Update Menu (30 min)
- Remove Text Extractor menu entry
- Remove Advanced Extractor menu entry
- Update Text to JSON menu entry to use new unified class

### Step 5: Add Deprecation Notices (15 min)
- Add deprecation comments to old files
- Keep old files in codebase (don't delete yet)

### Step 6: Testing (1 hour)
- Test mode switching
- Test format conversion mode (all 10 formats)
- Test JSX extraction mode (all features)
- Test settings persistence

**Total estimated time: 6-7 hours**

---

## ⚠️ Risk Mitigation

### Risk 1: UI Complexity
**Risk:** Mode switching may cause layout issues  
**Mitigation:**
- Use `deleteLater()` to properly clean up old widgets
- Test mode switching multiple times
- Ensure no memory leaks

### Risk 2: Feature Loss
**Risk:** Some features might not work after merge  
**Mitigation:**
- Copy UI code carefully, don't rewrite
- Test all features in both modes
- Keep old files as reference

### Risk 3: User Confusion
**Risk:** Users may not find JSX extraction in "Text to JSON Converter"  
**Mitigation:**
- Clear mode names ("JSX/HTML Extraction")
- Add tooltip to mode selector
- Update documentation

---

## ✅ Success Criteria

- [ ] Mode selector at top works
- [ ] Switching between modes works smoothly
- [ ] Format Conversion mode: All 10 formats work
- [ ] JSX Extraction mode: All 26 features work
- [ ] Settings persistence works
- [ ] No crashes or errors
- [ ] Old tools removed from menu
- [ ] App launches without errors

---

## 📝 File Changes

### New Files:
- `src/gui/unified_text_to_json_dock.py` (NEW, ~900-1000 lines)

### Modified Files:
- `src/gui/menu_builder.py` (update menu entries)
- `src/app.py` (if tool registration needed)

### Deprecated Files (keep in codebase):
- `src/gui/text_extractor_dock.py` (add deprecation notice)
- `src/gui/advanced_extractor_dock.py` (add deprecation notice)
- `src/gui/text_to_json_dock.py` (add deprecation notice)

### Unchanged Files:
- `src/extractors/advanced_extractor.py` (keep as-is)
- `src/text_to_json.py` (keep as-is)

---

## 🎨 UI Screenshots (Mockup)

### Mode: Format Conversion
```
┌─────────────────────────────────────────────────────────────┐
│ Mode: [▼ Format Conversion ▼]                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Format: [▼ Auto-detect ▼]                                  │
│                                                             │
│ ┌───────────────────────┐  ┌───────────────────────┐       │
│ │ Input Text:           │  │ Output JSON:          │       │
│ │                       │  │                       │       │
│ │ name: John            │  │ {                     │       │
│ │ age: 30               │  │   "name": "John",     │       │
│ │                       │  │   "age": 30           │       │
│ │                       │  │ }                     │       │
│ └───────────────────────┘  └───────────────────────┘       │
│                                                             │
│ [Convert] [Templates] [History] [Validate] [Swap] [Copy]   │
└─────────────────────────────────────────────────────────────┘
```

### Mode: JSX/HTML Extraction
```
┌─────────────────────────────────────────────────────────────┐
│ Mode: [▼ JSX/HTML Extraction ▼]                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Path: [/path/to/file.jsx    ] [Browse] [✓] Is File         │
│                                                             │
│ Mode: [▼ JSX ▼]  Parameter: [label   ]  [✓] Attribute      │
│                                                             │
│ Options:                                                    │
│  [✓] Include key      [✓] Only strings    [✓] TypeScript   │
│  [✓] Include value    [ ] Quotation marks [ ] Exclude numeric│
│  [ ] Drop standard    [ ] Match all       [ ] Skip empty    │
│                                                             │
│ Case: [▼ snake_case ▼]  Limit: [all]  Indent: [2]          │
│                                                             │
│ Avoid keys: [id,className] (•) Equals  ( ) Contains        │
│                                                             │
│ [Extract] [Clear]                                           │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ Paths ┊ JSON                                        │     │
│ │ Component.Button.label                              │     │
│ │ Component.Input.placeholder                         │     │
│ └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

**Phase 2 Design Complete! Ready for Phase 3 (Implementation)?**
