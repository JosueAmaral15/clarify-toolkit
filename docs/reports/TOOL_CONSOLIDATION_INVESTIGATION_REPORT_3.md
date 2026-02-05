# Tool Consolidation Investigation Report
## Phase 1: Understanding the Three Tools

**Date:** 2026-01-30  
**Programmer:** #3  
**Task:** Merge 3 extraction/conversion tools into 1 unified tool

---

## 📊 Executive Summary

**Current State:** 3 separate tools with overlapping purposes
**Goal:** 1 unified "Text to JSON + Advanced Extraction" tool
**Strategy:** Merge Advanced Extractor into Text to JSON Converter, remove Text Extractor

---

## 🔍 Tool Analysis

### 1. Text Extractor (`text_extractor_dock.py` - 577 lines)

**Purpose:** Extract JSX/HTML attributes and tag content for i18n purposes

**Features:**
- JSX attribute extraction (e.g., `label="Click Me"`)
- Tag content extraction (e.g., `<title>Page Title</title>`)
- Generic scope extraction with custom delimiters
- Hierarchical path building (`Component.Button.label`)
- Normalization (snake_case, camelCase, PascalCase, kebab-case)
- Drop standard HTML tags
- Nested JSON output
- **Inline extraction logic (~200 lines embedded in GUI)**

**Architecture:**
- Inherits from: `StandardToolDock`
- Backend: **No separate backend** - extraction logic is inline in GUI
- Extraction methods (inline):
  - `_extract_jsx_attributes()` (line 356)
  - `_extract_tag_content()` (line 405)
  - `_extract_generic_scope()` (line 439)

**Key Options:**
- Mode: JSX, Tag Content, Generic
- Case style: snake, camel, pascal, kebab
- Limit: character truncation
- Uppercase: UPPERCASE tokens
- Add key/value to path
- Drop standard HTML tags
- Nested JSON output
- Only strings (no expressions)
- **Exclude numeric keys** ⭐
- **Skip empty values** ⭐

**Input:** HTML/JSX files or directories  
**Output:** Paths text + JSON structure

---

### 2. Advanced Extractor (`advanced_extractor_dock.py` - 645 lines)

**Purpose:** Advanced JSX/HTML parameter extraction with comprehensive backend

**Features:**
- All features from Text Extractor PLUS:
- Output tabs (Paths + JSON separate views)
- Avoid keys section (with radio buttons: equals/contains)
- Quotation marks checkbox
- Match all checkbox
- Better generic delimiters UI
- Context menus
- Copy all button
- **External backend module (708 lines)** ✅
- **NEW: TypeScript export** ⭐ (added in Phase 1-2)
- **NEW: Exclude numeric keys** ⭐ (added in Phase 1-2)
- **NEW: Skip empty values** ⭐ (added in Phase 1-2)

**Architecture:**
- Inherits from: `BaseDock + FileInputMixin`
- Backend: `src/extractors/advanced_extractor.py` (708 lines) ✅
- Well-structured with 8 UI creation methods:
  - `_create_path_section()`
  - `_create_mode_section()`
  - `_create_delimiters_section()`
  - `_create_options_section()`
  - `_create_case_section()`
  - `_create_avoid_keys_section()`
  - `_create_buttons_section()`
  - `_create_output_tabs()`

**Key Options (26 total):**
- Everything from Text Extractor
- PLUS: Avoid keys (equals/contains mode)
- PLUS: Quotation marks
- PLUS: Match all
- PLUS: TypeScript export (NEW)
- PLUS: Exclude numeric (NEW)
- PLUS: Skip empty (NEW)

**Input:** HTML/JSX files or directories  
**Output:** Paths text + JSON structure (with output tabs)

**UI Superiority:**
- ✅ Output tabs (better UX)
- ✅ Avoid keys radio buttons
- ✅ Context menus
- ✅ Better organized sections
- ✅ 8 modular UI methods vs 1 monolithic method

---

### 3. Text to JSON Converter (`text_to_json_dock.py` - 584 lines)

**Purpose:** Convert various text formats to JSON (format converter)

**Features:**
- **10 format converters:**
  1. Key-Value pairs (`key: value`, `key = value`)
  2. Lists (bullet points with `-`, `*`)
  3. CSV (with header, separator, format options)
  4. Python dict literals
  5. YAML-like format
  6. INI files
  7. TOML files
  8. Java Properties
  9. TOON (Token-Oriented Object Notation)
  10. Auto-detect format
  
- Live preview with debounce (type and see JSON instantly)
- Type inference (auto-detect types vs all strings)
- CSV advanced options (header, separator, array/object format)
- Templates dialog with examples
- Conversion history (last 10 conversions)
- Validate JSON
- Swap (JSON back to text)
- Copy result
- Open in editor

**Architecture:**
- Inherits from: `BaseDock`
- Backend: `src/text_to_json.py` (624 lines) ✅
- 12 conversion functions:
  - `detect_format()`
  - `convert_key_value_to_json()`
  - `convert_list_to_json()`
  - `convert_csv_to_json()`
  - `convert_python_dict_to_json()`
  - `convert_yaml_to_json()`
  - `convert_ini_to_json()`
  - `convert_toml_to_json()`
  - `convert_java_properties_to_json()`
  - `convert_toon_to_json()`
  - `convert_text_to_json()` (main entry point)
  - `parse_value()` (type inference)

**Input:** Text in various formats (key-value, CSV, YAML, INI, TOML, etc.)  
**Output:** JSON structure

**Key Difference:**
- **NOT a JSX/HTML parser** - it's a **format converter**
- Converts structured text formats to JSON
- Different use case than extractors!

---

## 🔄 Purpose Comparison

| Tool | Purpose | Input | Output | Backend |
|------|---------|-------|--------|---------|
| **Text Extractor** | Extract JSX/HTML attributes | `.jsx`, `.tsx`, `.html` files | Paths + JSON | ❌ Inline (200 lines in GUI) |
| **Advanced Extractor** | Extract JSX/HTML attributes (advanced) | `.jsx`, `.tsx`, `.html` files | Paths + JSON | ✅ External (708 lines) |
| **Text to JSON** | Convert text formats to JSON | Text (CSV, YAML, INI, etc.) | JSON | ✅ External (624 lines) |

**Key Discovery:**
- Text Extractor & Advanced Extractor: **Same purpose** (JSX/HTML attribute extraction)
- Text to JSON Converter: **Different purpose** (format conversion)

---

## 🎯 Consolidation Strategy

### User's Goal:
1. ❌ Remove Text Extractor from menu
2. ✅ Merge Advanced Extractor into Text to JSON Converter
3. 📊 Result: 1 unified tool

### Challenge Identified:
**Advanced Extractor and Text to JSON have DIFFERENT purposes!**

- **Advanced Extractor:** Extracts attributes from JSX/HTML CODE
- **Text to JSON:** Converts text FORMATS to JSON

**They are NOT overlapping tools!**

---

## 💡 Proposed Solutions

### Option A: Two Modes in One Tool (RECOMMENDED)

Create **"Text to JSON Converter with Advanced Extraction"** with 2 modes:

**Mode 1: Format Conversion** (existing Text to JSON)
- Convert CSV, YAML, INI, TOML, etc. to JSON
- All existing features preserved

**Mode 2: JSX/HTML Extraction** (Advanced Extractor)
- Extract attributes from JSX/HTML files
- All Advanced Extractor features
- Replaces both Text Extractor and Advanced Extractor

**UI Design:**
- **Tab 1:** "Format Conversion" (Text to JSON UI)
- **Tab 2:** "JSX/HTML Extraction" (Advanced Extractor UI)
- OR: Mode selector dropdown at top

**Advantages:**
- ✅ Consolidates 3 tools → 1 tool
- ✅ Clear separation of two different use cases
- ✅ Preserves all functionality
- ✅ Removes redundant Text Extractor
- ✅ User has one place for "text → JSON" tasks

**Disadvantages:**
- ⚠️ Tool becomes larger (more complex)
- ⚠️ May confuse users (two different purposes)

---

### Option B: Keep Separate, Remove Text Extractor Only

Keep Text to JSON and Advanced Extractor separate, remove Text Extractor.

**Result:** 2 tools instead of 3
- "Text to JSON Converter" (format conversion)
- "Advanced Extractor" (JSX/HTML extraction)

**Advantages:**
- ✅ Clear separation of purposes
- ✅ Simpler implementation
- ✅ Less user confusion

**Disadvantages:**
- ❌ Doesn't fulfill user's goal of merging into 1 tool
- ❌ Still have 2 tools in menu

---

### Option C: Rename to Clarify Purpose

Keep both tools but rename for clarity:
- "Format Converter" (CSV/YAML/INI → JSON)
- "JSX/HTML Extractor" (extract from code)

**Advantages:**
- ✅ Clear naming
- ✅ Simple implementation

**Disadvantages:**
- ❌ Doesn't consolidate tools
- ❌ Doesn't fulfill user's goal

---

## ❓ Questions for User

**Question 1: Understanding the Goal**
You said to merge Advanced Extractor into Text to JSON Converter. Did you know they have **different purposes**?

- Text to JSON: Converts text formats (CSV, YAML, INI) → JSON
- Advanced Extractor: Extracts attributes from JSX/HTML code → JSON

Should we:
- **A)** Merge anyway (create 2-mode tool)
- **B)** Keep separate, just remove Text Extractor
- **C)** Re-evaluate the goal

---

**Question 2: Tool Purpose**
What do you want the final unified tool to be called?

- **A)** "Text to JSON Converter" (emphasizes conversion)
- **B)** "Text Processor" (broader name)
- **C)** "Text to JSON + Extractor" (describes both features)
- **D)** Something else?

---

**Question 3: UI Layout**
If we merge (Option A), how should the UI look?

- **A)** Tabs: "Format Conversion" tab + "JSX Extraction" tab
- **B)** Mode selector dropdown at top
- **C)** Sections with collapsible panels
- **D)** Something else?

---

## 📋 Feature Mapping

### Features to Keep (from Advanced Extractor):

**Extraction Features:**
- ✅ JSX attribute extraction
- ✅ Tag content extraction
- ✅ Generic scope extraction
- ✅ Hierarchical path building
- ✅ Output tabs (Paths + JSON)
- ✅ Avoid keys (equals/contains)
- ✅ TypeScript export
- ✅ Exclude numeric keys
- ✅ Skip empty values

**UI Features:**
- ✅ Output tabs
- ✅ Avoid keys radio buttons
- ✅ Context menus
- ✅ Copy all button
- ✅ 8 modular UI sections

**Backend:**
- ✅ `advanced_extractor.py` (708 lines)

---

### Features to Keep (from Text to JSON):

**Conversion Features:**
- ✅ 10 format converters
- ✅ Auto-detect format
- ✅ Type inference
- ✅ CSV advanced options
- ✅ Live preview with debounce
- ✅ Templates dialog
- ✅ Conversion history
- ✅ Validate JSON
- ✅ Swap (JSON → text)

**UI Features:**
- ✅ Format selector dropdown
- ✅ Type inference checkbox
- ✅ CSV options (header, separator, format)
- ✅ Templates button
- ✅ History button
- ✅ Debounced preview

**Backend:**
- ✅ `text_to_json.py` (624 lines)

---

### Features to Remove (from Text Extractor):

- ❌ Entire Text Extractor tool
- ❌ Inline extraction logic (replaced by Advanced Extractor backend)
- ❌ Menu entry for Text Extractor

---

## 🏗️ Architecture Comparison

### Current Architecture:

```
src/gui/
├── text_extractor_dock.py (577 lines) ← REMOVE
│   └── Inline extraction logic (~200 lines)
├── advanced_extractor_dock.py (645 lines) ← MERGE
│   └── Uses: src/extractors/advanced_extractor.py (708 lines)
└── text_to_json_dock.py (584 lines) ← EXPAND
    └── Uses: src/text_to_json.py (624 lines)

src/
├── extractors/
│   └── advanced_extractor.py (708 lines) ← KEEP
└── text_to_json.py (624 lines) ← KEEP
```

### Proposed Architecture (Option A):

```
src/gui/
└── unified_text_tool_dock.py (NEW, ~900-1000 lines)
    ├── Tab 1: Format Conversion UI (from text_to_json_dock.py)
    ├── Tab 2: JSX Extraction UI (from advanced_extractor_dock.py)
    └── Uses both backends:
        ├── src/text_to_json.py (624 lines)
        └── src/extractors/advanced_extractor.py (708 lines)

src/
├── extractors/
│   └── advanced_extractor.py (708 lines) ← KEEP
└── text_to_json.py (624 lines) ← KEEP
```

---

## 📈 Complexity Analysis

**Text Extractor:**
- Lines: 577
- Backend: Inline (no separation)
- UI methods: 1 monolithic setup
- Features: 14

**Advanced Extractor:**
- Lines: 645 (GUI) + 708 (backend) = 1,353 total
- Backend: External module ✅
- UI methods: 8 modular methods ✅
- Features: 26 (including 3 new features)

**Text to JSON:**
- Lines: 584 (GUI) + 624 (backend) = 1,208 total
- Backend: External module ✅
- UI methods: Well-structured
- Features: 10 converters + live preview + history

**Unified Tool (estimated):**
- Lines: ~900-1,000 (GUI) + 708 (extractor) + 624 (converter) = 2,232-2,332 total
- Backend: Two external modules ✅
- UI: Tab-based or mode-based
- Features: 36+ (all features from both tools)

---

## ⏱️ Implementation Time Estimate

### Option A: Merge into One Tool (2-mode approach)

**Phase 1: Investigation** ✅ DONE (3-4 hours)
**Phase 2: Design** (1-2 hours)
- Design tab layout
- Map feature integration
- Plan menu structure

**Phase 3: Implementation** (4-6 hours)
- Create unified dock class
- Integrate Text to JSON UI (copy existing)
- Integrate Advanced Extractor UI (copy existing)
- Wire both backends
- Remove Text Extractor from menu
- Remove Advanced Extractor from menu

**Phase 4: Testing** (1-2 hours)
- Test format conversion mode
- Test JSX extraction mode
- Test switching between modes
- Verify all features work

**Total: 9-14 hours**

---

### Option B: Keep Separate, Remove Text Extractor Only

**Phase 1: Investigation** ✅ DONE
**Phase 2: Removal** (30 min)
- Comment out Text Extractor menu entry
- Add deprecation notice

**Phase 3: Testing** (30 min)
- Verify app launches
- Verify menu updated

**Total: 1 hour**

---

## 🚨 Risk Assessment

### Option A Risks:

**High Complexity:**
- Unified tool has 2 very different purposes
- May confuse users ("Why is JSX extraction in Text to JSON?")
- Larger codebase (harder to maintain)

**User Confusion:**
- Users might not understand the two modes
- "I want to convert CSV" → finds JSX extraction tab
- "I want to extract JSX" → opens "Text to JSON" (confusing name)

**Implementation Complexity:**
- Need to manage 2 backends in 1 GUI
- Tab switching logic
- Ensure features don't interfere

### Option B Risks:

**Doesn't Meet User Goal:**
- User asked to merge into 1 tool
- This keeps 2 separate tools

**Less Simplified Menu:**
- Still have 2 tools instead of 1

---

## 📝 Recommendations

**I recommend clarifying the goal with the user before proceeding.**

**My questions:**
1. Did you realize Advanced Extractor and Text to JSON have different purposes?
2. Do you still want to merge them into 1 tool?
3. If yes, what should the unified tool be called?
4. How should the UI be organized (tabs, mode selector, etc.)?

**My preference:** **Option B** (keep separate, remove Text Extractor only)
- Simpler implementation
- Clear separation of purposes
- Less user confusion
- Still achieves goal of removing redundant tool

**User's stated preference:** Option A (merge all into 1)
- Requires clarification on purpose difference

---

## ✅ Next Steps

**Awaiting user answers to questions above before proceeding to Phase 2 (Design).**

**Status:** Phase 1 complete (Investigation) ✅  
**Blockers:** Need user clarification on consolidation strategy
**Time spent:** 1 hour (investigation and report creation)

---

**Programmer #3 Note:**
Investigation revealed that Advanced Extractor and Text to JSON Converter serve DIFFERENT purposes (JSX extraction vs format conversion). User needs to clarify if they still want to merge these different tools into one, and if so, how the UI should be organized. Recommending Option B (keep separate, remove Text Extractor only) as simpler and clearer approach.
