# Code Study - Session 18: Extractor Docks & Large Tools

**Date**: 2026-01-22  
**Programmer**: #4  
**Session Focus**: Extractor docks and specialized tools

---

## 📊 Session Statistics

**Files Studied**: 3 files (focused analysis)  
**Lines Studied**: ~1,000 LOC (architecture focus)  
**Total Available**: 1,746 LOC (advanced: 601, text: 577, jsx: 568)  
**Time**: ~30 minutes  
**Coverage**: Architecture + key features

---

## 📁 Files Analyzed

### 1. **src/gui/advanced_extractor_dock.py** (601 LOC) ⭐ COMPLEX EXTRACTOR

**Purpose**: Advanced parameter extraction from JSX/TSX and generic files with hierarchical JSON generation

**Architecture**:
- Extends **BaseDock + FileInputMixin**
- **Modular UI creation**: 7 section methods for organized layout
- **AdvancedExtractor** core logic (src/extractors/)
- **Dual mode**: JSX mode vs Generic mode

**Key Features**:

#### Extraction Modes
- **JSX/TSX Mode**: React/TypeScript component extraction
  - Extracts JSX attributes (e.g., `label="text"`)
  - Component hierarchy tracking
- **Generic Mode**: Custom delimiter-based extraction
  - User-defined start/end delimiters (regex)
  - File extension filter

#### Parameter Input
- **Parameter/Attribute field**: What to extract (e.g., "label", "title", "placeholder")
- **Attribute mode checkbox**: 
  - Checked: Extract attribute values (`label="value"` → value)
  - Unchecked: Extract tag contents (`<tag>content</tag>` → content)

#### Generic Mode Delimiters
- **Start delimiter**: Regex pattern (default: `<.*?>`)
- **End delimiter**: Regex pattern (default: `</.*?>`)
- **Extensions filter**: File types to process (e.g., `.html,.xml`)

#### 11 Processing Options (Checkboxes)
1. **Drop standard HTML tags**: Ignore div, span, p, etc.
2. **Add key to path**: Include parameter name in path
3. **Add value to path**: Include extracted value in path
4. **Only string literals**: Reject expressions (no `{variable}`)
5. **Validate empty**: Reject empty strings
6. **Remove numeric hierarchy**: Drop numeric indices from paths
7. **Collapse after removal**: Merge nested single children
8. **Deep merge**: Combine duplicate paths intelligently
9. **Uppercase keys**: Force uppercase normalization
10. **Avoid word cut**: Smart truncation at word boundaries
11. **Is file?**: Single file vs directory processing

#### Case Normalization
- **Case style combo**: snake_case, camelCase, PascalCase, kebab-case
- Applied to all extracted keys

#### Character Limits
- **Max length**: Character limit per value (spinner)
- **Max depth**: Hierarchy depth limit (spinner)

#### Avoid Keys Feature
- **Mode selector**: "Equals" vs "Contains"
- **Keys list**: Comma-separated keys to ignore
- Example: Ignore keys named "id" or containing "temp"

#### Output Tabs (QTabWidget)
- **Tab 1 - Paths**: Hierarchical text paths
  - Format: `component.subcomponent.label → "Text value"`
- **Tab 2 - JSON**: Structured JSON output
  - Hierarchical object representing component tree
- **Tab 3 - Log**: Processing log with statistics
  - Files processed, items extracted, errors

#### Actions
- `btn_run` - Execute extraction
- `btn_save` - Save all outputs (paths.txt, data.json, log.txt)
- `btn_copy_all` - Copy current tab content to clipboard
- **Context menu**: Right-click for copy options

**Key Methods**:

##### _run_extraction() ⭐ MAIN EXECUTION (line 402)
- Validates inputs (path, parameter)
- Determines mode (JSX vs Generic)
- Creates AdvancedExtractor instance
- Configures with 11+ options
- Processes files (single file or directory recursion)
- Generates outputs:
  - Text paths (hierarchical representation)
  - JSON structure (nested object)
  - Processing log (statistics)
- Updates UI tabs with results

##### _create_*_section() methods (7 sections)
- Modular UI creation pattern
- Each section returns layout (QHBoxLayout/QVBoxLayout)
- Assembled in _setup_ui()
- Clean separation of concerns

##### _toggle_generic_fields(mode) (line 350)
- Shows/hides generic-specific controls
- Enables/disables based on JSX vs Generic mode
- Dynamic UI adaptation

##### _should_filter_line(line) (line 544)
- Filters output lines based on criteria
- Used for "avoid keys" functionality
- Supports "equals" and "contains" modes

**Design Patterns**:
- **Strategy**: JSX vs Generic extraction strategies
- **Facade**: AdvancedExtractor wraps complex logic
- **Template Method**: BaseDock inheritance
- **Builder**: Modular section creation
- **Observer**: Context menu signals

**Integration Points**:
- ✅ **Extractors**: AdvancedExtractor core logic
- ✅ **Normalization**: Case styles, truncation, HTML tag filtering
- ✅ **File I/O**: Directory recursion, file saving

**Code Quality**:
- Excellent modularity (7 section creation methods)
- Clear option organization (11 checkboxes grouped)
- Comprehensive output (3 tabs for different views)

---

### 2. **src/gui/text_extractor_dock.py** (577 LOC) ⭐ SIMPLIFIED EXTRACTOR

**Purpose**: Simplified version of advanced extractor with essential features

**Architecture**:
- Extends **StandardToolDock** (all mixins!)
- **Simpler UI**: QGridLayout for compact form
- **3 modes**: JSX, Tag, Generic
- **Focused feature set**: Core extraction without complexity

**Key Features**:

#### Input/Output
- Input path (file or directory)
- Output file path (JSON)
- Browse buttons for both

#### Extraction Modes (3 modes)
- **JSX mode**: Extract JSX attributes
- **Tag mode**: Extract tag contents
- **Generic mode**: Custom delimiters

#### Parameter Input
- **Parameter/Tag name**: What to extract
- Placeholder: "e.g., label, title, placeholder"

#### Normalization Options
- **Case style**: snake_case, camelCase, PascalCase, kebab-case
- **Character limit**: Max length or "all"

#### Advanced Options (QGroupBox)
- `chk_uppercase` - Force uppercase
- `chk_avoid_cut` - Smart word-boundary truncation (default: on)
- `chk_drop_standard` - Ignore standard HTML tags (default: on)
- Additional path/hierarchy options

**Key Differences from AdvancedExtractor**:
- **Simpler UI**: Single layout vs 7 sections
- **Fewer options**: ~6 vs 11 checkboxes
- **Single output**: JSON file vs 3 tabs
- **StandardToolDock**: Inherits all mixins (results panel, buttons, etc.)

**Use Case**: Quick extraction without advanced hierarchy control

---

### 3. **src/gui/jsx_extractor_dock.py** (568 LOC) ⭐ JSX SPECIALIST

**Purpose**: Specialized JSX/TSX parameter extractor (original implementation)

**Architecture**:
- Extends **BaseDock**
- **Focused on JSX**: No generic mode
- **Security**: Path traversal validation
- **Two parsers**: JSXParser, GenericScopeParser

**Key Features**:

#### Path Security (OWASP A01)
- **_validate_path_security()**: Prevents path traversal attacks
- Validates paths are within:
  - Home directory (~)
  - Current working directory
  - Temp directory
- Real path resolution (follows symlinks)
- **Critical**: Security-first design

#### JSX/TSX Extraction
- **JSXParser**: Dedicated JSX/TSX parser
- **GenericScopeParser**: Fallback for generic patterns
- Component hierarchy tracking
- Attribute extraction

#### Output Format
- **Hierarchical paths**: component.child.attribute
- **JSON structure**: Nested component tree
- **Statistics**: Files processed, items extracted

#### Normalization Utilities
- **normalize_token()**: Case normalization
- **smart_truncate()**: Word-boundary aware truncation
- **path_join()**: Hierarchical path construction
- **is_standard_tag()**: HTML tag filtering
- **STANDARD_HTML_TAGS**: Predefined list (div, span, p, etc.)

**Key Differences**:
- **JSX-only**: No generic mode clutter
- **Security focus**: Path validation built-in
- **Original implementation**: Base for AdvancedExtractor

**Use Case**: Secure JSX extraction in production environments

---

## 🎯 Key Insights

### Three Extractor Philosophy

**Why three extractors?**

1. **jsx_extractor_dock.py** - Original, secure, JSX-focused
2. **advanced_extractor_dock.py** - Feature-rich, dual-mode, power user
3. **text_extractor_dock.py** - Simplified, quick extraction

**Pattern**: **Progressive enhancement** for different user needs!

### Security in JSX Extractor

**jsx_extractor_dock.py** shows **security-first design**:
- Path traversal validation (OWASP A01)
- Real path resolution
- Allowed directory whitelist
- Prevents accessing system files

**Impact**: Safe for production use with untrusted paths!

### Modular UI Construction

**advanced_extractor_dock.py** demonstrates **excellent UI architecture**:
```python
_create_path_section()
_create_mode_section()
_create_delimiters_section()
_create_options_section()
_create_case_section()
_create_avoid_keys_section()
_create_buttons_section()
_create_output_tabs()
```

**Benefits**:
- Easy to maintain (each section isolated)
- Easy to test (sections can be tested independently)
- Easy to extend (add new sections without touching others)

### Dual Mode Complexity

**advanced_extractor_dock.py** manages **JSX + Generic modes**:
- **Dynamic UI**: Shows/hides controls based on mode
- **Single tool**: Replaces two separate tools
- **Trade-off**: More complex but more powerful

**Decision**: Complexity vs Usability - chosen power!

---

## 📊 Updated Study Progress

**Session 18 Stats**:
- Files studied: 3 files
- LOC studied: ~1,000 LOC (focused reading)
- Total: advanced_extractor (601), text_extractor (577), jsx_extractor (568)

**Total Progress**:
- **Files**: 79/196 (40.3%)
- **LOC**: ~27,781/38,754 (71.7%)
- **Remaining**: 117 files (59.7%), ~10,973 LOC (28.3%)

**Milestone**: Crossed 70% code coverage! 🎉

---

## 🚀 Next Steps

**Remaining Docks** (~6,000 LOC):
- formula_dock.py (~500 LOC) - Formula/expression evaluator
- case_converter_dock.py (~400 LOC) - Case style converter
- text_to_json_dock.py (~600 LOC) - Text to JSON converter
- google_translate_dock.py, json_translate_dock.py (~800 LOC)
- history_dock.py, placeholder_replacer_dock.py (~500 LOC each)
- tutorials_dock.py, file_list_dock.py (~500 LOC each)
- + specialty docks (~2,000 LOC)

**GUI Support Files** (~2,000 LOC):
- Dialogs (batch, case_validator, config_editor, diff_viewer, etc.)
- Panels, Workers, Factory, Initialization Manager

**Remaining Modules** (~3,000 LOC):
- Plugins system
- Utilities
- Tests (if needed for understanding)

**Options**:
- **A**: Continue dock studies (formula, case_converter, translators)
- **B**: Study GUI support files (dialogs, panels, workers)
- **C**: Complete Phase 4 implementation (10% remaining)
- **D**: Work on fixes/improvements (user focus)

**Recommendation**: Continue docks to reach 80% coverage, then focus on fixes

**Status**: Session 18 complete ✅  
**Key Finding**: Three extractors follow progressive enhancement pattern!
