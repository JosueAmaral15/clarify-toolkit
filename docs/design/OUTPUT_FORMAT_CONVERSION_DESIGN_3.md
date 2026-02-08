# Output Format Conversion Design - Programmer #3

**Date:** 2026-02-08  
**Status:** Phase 1 Investigation Complete → Phase 2 Design Complete  
**Estimated Implementation Time:** 2 hours

---

## 1. Problem Statement

**Current Behavior:**
- User selects template (CSV, YAML, TOML, HTML Table, etc.) from Templates dialog
- Template selection updates output tab name (e.g., "JSON" → "TOML")
- **BUG:** Output is always JSON format regardless of template selection
- Extraction always returns JSON, no format conversion exists

**Desired Behavior:**
- Template selection should convert extraction output to selected format
- Tab name matches actual output format
- Format selection persists across extractions
- Fallback to JSON on conversion errors

---

## 2. Investigation Findings (Phase 1)

### 2.1 Current Data Flow

```
User clicks "Extract/Convert"
    ↓
_jsx_run_extraction() creates ExtractionWorker
    ↓
ExtractionWorker.execute_extraction() runs in background thread
    ↓
AdvancedExtractor.process_text() or run()
    ↓ Returns: (path_lines, merged_json)
ExtractionWorker formats JSON (lines 86-96)
    ↓ Emits: finished(text_output, json_output)
_on_extraction_finished(text, json) receives outputs
    ↓
Display in output tabs (text → Paths, json → JSON tab)
    ↓ **NO FORMAT CONVERSION HAPPENS**
```

### 2.2 Template to Format Mapping

| Template Name | Output Format | File Extension | Complexity |
|--------------|---------------|----------------|------------|
| JSON | JSON | .json | ✅ Already done (default) |
| CSV | CSV | .csv | 🟡 Medium (flattening needed) |
| YAML | YAML | .yaml | 🟡 Medium (needs yaml lib) |
| TOML | TOML | .toml | 🟡 Medium (needs toml lib) |
| INI | INI | .ini | 🟢 Easy (ConfigParser) |
| Java Properties | Properties | .properties | 🟢 Easy (key=value) |
| TOON | TOON | .toon | 🔴 Hard (custom format) |
| HTML Table | HTML | .html | 🟡 Medium (table generation) |
| Python Dict | Python | .py | 🟢 Easy (repr/pprint) |
| JSX Extract | JSON | .json | ✅ Already JSON output |

**Total:** 10 formats (1 done, 9 to implement)

---

## 3. Design Decisions

### 3.1 User Requirements (Confirmed)

1. **Scope:** ALL templates should convert output format
2. **Nested Data Flattening:** Recursive dot notation (e.g., `user.name.first`)
3. **Error Handling:** Show error message, keep JSON output as fallback
4. **Persistence:** Remember last selected template across extractions
5. **Default:** JSON when no template selected

### 3.2 Architecture Design

**Selected Approach:** Convert in `_on_extraction_finished()` (not in worker)

✅ Worker emits raw JSON data  
✅ Dock has template selection context  
✅ Separation of concerns (extraction vs formatting)  
✅ Easy to add new formats without touching worker

```python
def _on_extraction_finished(self, text_output: str, json_output: str):
    selected_format = self._get_selected_output_format()
    
    try:
        if selected_format != "JSON":
            json_data = json.loads(json_output)
            converted_output = convert_json_to_format(json_data, selected_format)
        else:
            converted_output = json_output
    except Exception as e:
        converted_output = json_output
        self._show_conversion_error(selected_format, str(e))
    
    self.jsx_text_output.setPlainText(text_output)
    self.jsx_json_output.setPlainText(converted_output)
```

### 3.3 Converter Module Design

**New Module:** `src/converters/json_to_format.py`

Main entry point:
```python
def convert_json_to_format(json_data: dict|list, format_name: str, **options) -> str:
    """Converts JSON to specified format."""
```

Helper function:
```python
def flatten_json_recursive(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten nested JSON with dot notation (user.name.first)."""
```

---

## 4. Implementation Plan

### 4.1 Phase 3: Implementation (estimated 2 hours)

1. **Create converter module** (30 min)
   - [ ] Create `src/converters/` directory + `__init__.py`
   - [ ] Create `src/converters/json_to_format.py`
   - [ ] Implement `flatten_json_recursive()` helper
   - [ ] Implement `convert_json_to_format()` dispatcher

2. **Implement converters** (60 min)
   - [ ] JSON (json.dumps)
   - [ ] CSV (flatten + csv.DictWriter)
   - [ ] YAML (yaml library)
   - [ ] TOML (tomllib/toml library)
   - [ ] INI (ConfigParser)
   - [ ] HTML Table (HTML string generation)
   - [ ] Python Dict (pprint.pformat)
   - [ ] Java Properties (key=value)
   - [ ] TOON (custom format)

3. **Integrate with dock** (20 min)
   - [ ] Import converter in `unified_text_to_json_dock.py`
   - [ ] Modify `_on_extraction_finished()` to call converter
   - [ ] Add `_get_selected_output_format()` helper
   - [ ] Add error handling and notification
   - [ ] Store format in QSettings

4. **Handle template selection** (10 min)
   - [ ] Update format storage on template change
   - [ ] Restore format on app startup
   - [ ] Sync tab name

### 4.2 Phase 4: Testing (30 min)

**Protocol requirement: Test thoroughly before claiming completion**

- [ ] Test each format with real extraction data
- [ ] Test nested data flattening (verify dot notation)
- [ ] Test error handling (unconvertible structures, missing libraries)
- [ ] Test format persistence (restart app)

### 4.3 Phase 5: Documentation (10 min)

- [ ] Create `docs/features/OUTPUT_FORMAT_CONVERSION_3.md`
- [ ] Update this design document with implementation notes
- [ ] Commit with conventional commit message

**Total Estimated Time:** 2.5 hours

---

## 5. Technical Considerations

### 5.1 Flattening Strategy

**Nested JSON Example:**
```json
{
  "user": {
    "name": {"first": "John", "last": "Doe"},
    "emails": ["john@example.com", "jdoe@work.com"]
  }
}
```

**Flattened (Dot Notation):**
```
user.name.first = John
user.name.last = Doe
user.emails[0] = john@example.com
user.emails[1] = jdoe@work.com
```

**Arrays of objects:** Enumerate columns (`users[0].name`, `users[1].name`)

### 5.2 Error Handling Cases

1. **Unconvertible structure:** Show error, fallback to JSON
2. **Library missing (YAML/TOML):** Show install message, fallback to JSON
3. **Invalid JSON:** Show error, display raw string
4. **Format constraints:** Attempt conversion, show warning if data loss

### 5.3 Format Persistence

Use QSettings:
```python
# Store
settings = QSettings("Clarify", "FormatConverter")
settings.setValue("selected_output_format", format_name)

# Load
selected_format = settings.value("selected_output_format", "JSON")
```

---

## 6. Open Questions for Implementation

1. **TOON Format:** Study text_to_json.py lines 491-558 to understand reverse conversion
2. **JSX Extract Template:** Keep as JSON output (current behavior)
3. **TypeScript Export:** Only applies when format=JSON (remove quotes from keys)
4. **Library Installation:** Show error message, require manual installation

---

## 7. Next Session Checklist

**Before starting:**
- [ ] Read this design document completely
- [ ] Check pyproject.toml for yaml/toml dependencies
- [ ] Study TOON format from text_to_json.py

**During implementation:**
- [ ] Follow protocol: Ask questions before making decisions
- [ ] Test each converter individually
- [ ] Test with real extraction data
- [ ] Be honest about testing status

**After implementation:**
- [ ] Update this document with final notes
- [ ] Create feature documentation
- [ ] Commit with detailed message

---

**Programmer #3**  
**Status:** Design complete, ready for implementation  
**Next Phase:** Phase 3 Implementation (estimated 2 hours)
