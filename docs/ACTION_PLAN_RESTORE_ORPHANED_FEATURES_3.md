# Action Plan: Restore 3 Orphaned Format Converter Features

**Programmer:** #3  
**Date:** 2026-02-16  
**Branch:** COM3-documentation-study  
**Worktree:** clarify-COM3-study  

## Executive Summary

**Problem:** 3 features were implemented on Jan 29, 2026 (commit abec8a0) but removed on Feb 6, 2026 (commit dd8a6bb) with the note "doesn't exist". GUI checkboxes still exist but are non-functional.

**Features to Restore:**
1. `skip_empty` - Skip entries with empty/null values
2. `exclude_numeric` - Filter out numeric keys
3. `typescript_export` - Export as TypeScript interface

**Impact:** Users see checkboxes that do nothing, causing confusion and broken functionality.

---

## Investigation Summary

### Timeline Discovery

```
Jan 29, 2026 (abec8a0): "add 3 missing features to Advanced Extractor"
  ✅ Added skip_empty parameter (filters empty values)
  ✅ Added exclude_numeric parameter (filters numeric keys)
  ✅ Added typescript_export parameter (generates TS interfaces)
  ✅ Added 3 GUI checkboxes with tooltips
  ✅ Implemented json_to_typescript() method (63 lines)
  ✅ Integrated filters in _record_text_kv()

Feb 6, 2026 (dd8a6bb): "remove invalid parameters from AdvancedExtractor"
  ❌ Removed all 3 parameters from GUI → backend call
  ❌ Removed parameters from __init__ signature
  ❌ Note said: "doesn't exist" (MISTAKE - they DID exist!)
  ⚠️  GUI checkboxes left in place (orphaned UI elements)
```

### Current State

**GUI (unified_text_to_json_dock.py):**
- Line 831: `jsx_exclude_numeric_checkbox` ✅ EXISTS
- Line 841: `jsx_skip_empty_checkbox` ✅ EXISTS
- Line 823: `jsx_typescript_checkbox` ✅ EXISTS (need to verify)
- Lines 1398-1420: `_jsx_run_extraction()` ❌ NOT reading checkboxes
- Line 1401: AdvancedExtractor call ❌ NOT passing parameters

**Backend (advanced_extractor.py):**
- `__init__`: ❌ Missing 3 parameters
- `_record_text_kv()`: ❌ Missing skip_empty logic
- `_record_text_kv()`: ❌ Missing exclude_numeric logic
- `json_to_typescript()`: ❌ Missing method (63 lines)
- `run()`: ❌ Missing TypeScript export integration

---

## Restoration Strategy

### Phase 1: Backend Restoration (30 min)
Restore AdvancedExtractor functionality from commit abec8a0.

### Phase 2: GUI Integration (15 min)
Wire checkboxes to backend in _jsx_run_extraction().

### Phase 3: Testing (30 min)
Create comprehensive tests for all 3 features.

### Phase 4: Documentation (15 min)
Update feature documentation.

**Total Estimated Time:** 1.5 hours

---

## Phase 1: Backend Restoration

### Step 1.1: Add Parameters to __init__

**File:** `src/extractors/advanced_extractor.py`

**Location:** Line 234 (after existing parameters)

**Add to signature:**
```python
def __init__(
    self,
    # ... existing parameters ...
    typescript_export: bool = False,
    exclude_numeric: bool = False,
    skip_empty: bool = False,
):
```

**Add to docstring:**
```python
"""
Args:
    # ... existing args ...
    typescript_export: Export as TypeScript interface
    exclude_numeric: Filter out numeric keys
    skip_empty: Skip entries with empty/null values
"""
```

**Add to self assignments (around line 260):**
```python
# Features from Text Extractor consolidation
self.typescript_export = typescript_export
self.exclude_numeric = exclude_numeric
self.skip_empty = skip_empty
```

**Lines to add:** ~15 lines

---

### Step 1.2: Restore skip_empty Filter

**File:** `src/extractors/advanced_extractor.py`

**Location:** `_record_text_kv()` method, around line 428

**Current code:**
```python
def _record_text_kv(self, path_tokens: List[str], raw_value: str) -> Dict[str, Any]:
    """
    Build a small tree that, at path_tokens, adds a single key:value pair
    derived from raw_value. The key is normalized using current case settings;
    the value is the original raw_value.
    """
    # Apply limit to raw value first (if using old method) or normalize first (if using new method)
    if hasattr(self, '_apply_limit_to_key'):
        # New method: normalize first, then limit
        key = normalize_token(raw_value, self.case_style, self.to_upper) or "text"
        key = self._apply_limit_to_key(key)
    else:
        # Old method: limit raw value, then normalize
        trimmed = smart_truncate(raw_value, self.limit, self.avoid_cut)
        key = normalize_token(trimmed, self.case_style, self.to_upper) or "text"
    
    # Build nested dict
    result = {}
    # ... rest of method
```

**Add after normalization, before building dict:**
```python
def _record_text_kv(self, path_tokens: List[str], raw_value: str) -> Dict[str, Any]:
    """
    Build a small tree that, at path_tokens, adds a single key:value pair
    derived from raw_value. The key is normalized using current case settings;
    the value is the original raw_value.
    """
    # Skip empty values if enabled
    if self.skip_empty and (not raw_value or not raw_value.strip()):
        return {}
    
    # Normalize key from the raw value
    if hasattr(self, '_apply_limit_to_key'):
        # New method: normalize first, then limit
        key = normalize_token(raw_value, self.case_style, self.to_upper) or "text"
        key = self._apply_limit_to_key(key)
    else:
        # Old method: limit raw value, then normalize
        trimmed = smart_truncate(raw_value, self.limit, self.avoid_cut)
        key = normalize_token(trimmed, self.case_style, self.to_upper) or "text"
    
    # Exclude numeric keys if enabled
    if self.exclude_numeric and key.replace('_', '').isdigit():
        return {}
    
    # Build nested dict
    result = {}
    # ... rest of method
```

**Lines to add:** ~6 lines

**Note:** Check both numeric detection approaches:
- Simple: `key.isdigit()` - only pure digits like "123"
- Complex: `key.replace('_', '').isdigit()` - includes "12_34_56"

Need to verify which was used in original commit.

---

### Step 1.3: Restore TypeScript Export Method

**File:** `src/extractors/advanced_extractor.py`

**Location:** After `run()` method, around line 700

**Add complete method from commit abec8a0:**
```python
def json_to_typescript(self, json_data: Dict[str, Any], interface_name: str = "Root") -> str:
    """
    Convert JSON structure to TypeScript interface definition.
    
    Args:
        json_data: JSON dictionary to convert
        interface_name: Name for the root interface
        
    Returns:
        TypeScript interface definition as string
    """
    def infer_type(value: Any) -> str:
        """Infer TypeScript type from Python value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            if len(value) == 0:
                return "any[]"
            # Infer from first element
            elem_type = infer_type(value[0])
            return f"{elem_type}[]"
        elif isinstance(value, dict):
            return "object"
        else:
            return "any"
    
    def generate_interface(data: Dict[str, Any], name: str, indent: int = 0) -> str:
        """Recursively generate TypeScript interface."""
        indent_str = "  " * indent
        lines = [f"{indent_str}interface {name} {{"]
        
        nested_interfaces = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Nested object - create separate interface
                nested_name = f"{name}_{key.capitalize()}"
                nested_interfaces.append(generate_interface(value, nested_name, indent))
                lines.append(f"{indent_str}  {key}: {nested_name};")
            else:
                ts_type = infer_type(value)
                lines.append(f"{indent_str}  {key}: {ts_type};")
        
        lines.append(f"{indent_str}}}")
        
        # Add nested interfaces before parent
        result = "\n\n".join(nested_interfaces)
        if result:
            result += "\n\n"
        result += "\n".join(lines)
        
        return result
    
    return generate_interface(json_data, interface_name)
```

**Lines to add:** ~63 lines

---

### Step 1.4: Integrate TypeScript Export in run()

**File:** `src/extractors/advanced_extractor.py`

**Location:** `run()` method, around line 650-690

**Find the return statement:**
```python
def run(self, text_content: str, file_path: str = "TextInput") -> str:
    """
    Main extraction entry point.
    
    Args:
        text_content: Input text/JSX/HTML
        file_path: Source file identifier
        
    Returns:
        JSON string or TypeScript interface
    """
    # ... extraction logic ...
    
    # Build final JSON
    if self.convert_to_json:
        json_output = json.dumps(
            self.accumulated,
            indent=self.indentation if self.indentation > 0 else None,
            ensure_ascii=False
        )
        return json_output
    else:
        return str(self.accumulated)
```

**Modify to:**
```python
def run(self, text_content: str, file_path: str = "TextInput") -> str:
    """
    Main extraction entry point.
    
    Args:
        text_content: Input text/JSX/HTML
        file_path: Source file identifier
        
    Returns:
        JSON string or TypeScript interface
    """
    # ... extraction logic ...
    
    # Build final output
    if self.convert_to_json:
        json_output = json.dumps(
            self.accumulated,
            indent=self.indentation if self.indentation > 0 else None,
            ensure_ascii=False
        )
        
        # Export as TypeScript if enabled
        if self.typescript_export:
            ts_interface = self.json_to_typescript(self.accumulated, "Root")
            return ts_interface
        
        return json_output
    else:
        return str(self.accumulated)
```

**Lines to modify:** ~5 lines (add if block)

---

## Phase 2: GUI Integration

### Step 2.1: Read Checkbox States

**File:** `src/gui/unified_text_to_json_dock.py`

**Location:** `_jsx_run_extraction()` method, around line 1390

**Current code (approximate):**
```python
def _jsx_run_extraction(self):
    """Run JSX extraction in worker thread."""
    # Read parameters
    param = self.jsx_param_edit.text().strip()
    mode = "jsx"
    # ... read other parameters ...
    
    avoid_cut = self.jsx_avoid_cut_checkbox.isChecked()
    avoid_cut_direction = self.jsx_avoid_cut_combo.currentText()
    to_upper = self.jsx_to_upper_checkbox.isChecked()
```

**Add after existing checkbox reads:**
```python
    # Read feature checkboxes
    typescript_export = self.jsx_typescript_checkbox.isChecked()
    exclude_numeric = self.jsx_exclude_numeric_checkbox.isChecked()
    skip_empty = self.jsx_skip_empty_checkbox.isChecked()
```

**Lines to add:** ~3 lines

---

### Step 2.2: Pass Parameters to AdvancedExtractor

**File:** `src/gui/unified_text_to_json_dock.py`

**Location:** `_jsx_run_extraction()` method, around line 1401

**Current code:**
```python
extractor = AdvancedExtractor(
    param=param,
    mode=mode,
    avoid_keys=avoid_keys,
    avoid_keys_parameter=avoid_keys_param,
    include_key=include_key,
    include_value=include_value,
    no_standard=no_standard,
    convert_to_json=True,
    with_quotation_marks=with_quotation_marks,
    indentation=indent,
    case_style=case_style,
    limit=limit,
    avoid_cut=avoid_cut,
    avoid_cut_direction=avoid_cut_direction,
    to_upper=to_upper,
    only_strings=only_strings,
    is_attribute_mode=is_attribute_mode,
    start_regex=start_regex,
    end_regex=end_regex,
    file_extensions=file_extensions,
    use_class_names=use_class_names  # Already restored
)
```

**Add parameters:**
```python
extractor = AdvancedExtractor(
    param=param,
    mode=mode,
    avoid_keys=avoid_keys,
    avoid_keys_parameter=avoid_keys_param,
    include_key=include_key,
    include_value=include_value,
    no_standard=no_standard,
    convert_to_json=True,
    with_quotation_marks=with_quotation_marks,
    indentation=indent,
    case_style=case_style,
    limit=limit,
    avoid_cut=avoid_cut,
    avoid_cut_direction=avoid_cut_direction,
    to_upper=to_upper,
    only_strings=only_strings,
    is_attribute_mode=is_attribute_mode,
    start_regex=start_regex,
    end_regex=end_regex,
    file_extensions=file_extensions,
    use_class_names=use_class_names,
    typescript_export=typescript_export,
    exclude_numeric=exclude_numeric,
    skip_empty=skip_empty
)
```

**Lines to add:** ~3 lines

---

### Step 2.3: Verify Checkbox Existence

**Action:** Confirm all 3 checkboxes exist in GUI

**Expected locations:**
- Line 823: `jsx_typescript_checkbox` (need to verify exact line)
- Line 831: `jsx_exclude_numeric_checkbox` ✅ CONFIRMED
- Line 841: `jsx_skip_empty_checkbox` ✅ CONFIRMED

**If missing:** Check commit abec8a0 for exact GUI code.

---

## Phase 3: Testing

### Step 3.1: Create Test for skip_empty

**File:** `test_skip_empty_restoration_3.py`

**Test cases:**
1. Normal extraction (skip_empty=False) - includes all values
2. Skip empty strings (skip_empty=True) - filters ""
3. Skip whitespace-only (skip_empty=True) - filters "   "
4. Keep non-empty values (skip_empty=True) - keeps "Hello"
5. Mixed content - filters empties, keeps non-empties

**Example:**
```python
def test_skip_empty_feature():
    """Test skip_empty filters empty values."""
    jsx_code = '''
    <div>
        <p>Hello</p>
        <p></p>
        <p>   </p>
        <p>World</p>
    </div>
    '''
    
    # Without skip_empty
    extractor1 = AdvancedExtractor(
        param="*",
        mode="jsx",
        skip_empty=False
    )
    result1 = json.loads(extractor1.run(jsx_code))
    # Should have 4 entries (including empty ones)
    
    # With skip_empty
    extractor2 = AdvancedExtractor(
        param="*",
        mode="jsx",
        skip_empty=True
    )
    result2 = json.loads(extractor2.run(jsx_code))
    # Should have 2 entries (only non-empty)
```

---

### Step 3.2: Create Test for exclude_numeric

**File:** `test_exclude_numeric_restoration_3.py`

**Test cases:**
1. Normal extraction - includes numeric keys like "123"
2. Exclude pure numeric (exclude_numeric=True) - filters "123"
3. Keep alphanumeric (exclude_numeric=True) - keeps "abc123"
4. Keep numeric with underscores? - depends on implementation
   - Need to verify: `"12_34".replace('_', '').isdigit()` or just `"12_34".isdigit()`

**Example:**
```python
def test_exclude_numeric_feature():
    """Test exclude_numeric filters numeric keys."""
    jsx_code = '''
    <div>
        <button>123</button>
        <button>Click Me</button>
        <button>Button2</button>
    </div>
    '''
    
    # Without exclude_numeric
    extractor1 = AdvancedExtractor(
        param="*",
        mode="jsx",
        exclude_numeric=False
    )
    result1 = json.loads(extractor1.run(jsx_code))
    # Should have "123" key
    
    # With exclude_numeric
    extractor2 = AdvancedExtractor(
        param="*",
        mode="jsx",
        exclude_numeric=True
    )
    result2 = json.loads(extractor2.run(jsx_code))
    # Should NOT have "123" key, should have "click_me" and "button_2"
```

---

### Step 3.3: Create Test for typescript_export

**File:** `test_typescript_export_restoration_3.py`

**Test cases:**
1. JSON output (typescript_export=False) - returns JSON string
2. TypeScript interface (typescript_export=True) - returns TS code
3. Nested objects - generates nested interfaces
4. Arrays - uses array type notation
5. Type inference - correct TS types for string/number/boolean

**Example:**
```python
def test_typescript_export_feature():
    """Test TypeScript interface generation."""
    jsx_code = '''
    <div>
        <h1>Hello World</h1>
        <p>Description text</p>
        <button>Click Me</button>
    </div>
    '''
    
    # JSON output
    extractor1 = AdvancedExtractor(
        param="*",
        mode="jsx",
        typescript_export=False
    )
    result1 = extractor1.run(jsx_code)
    assert result1.startswith("{")  # JSON string
    
    # TypeScript output
    extractor2 = AdvancedExtractor(
        param="*",
        mode="jsx",
        typescript_export=True
    )
    result2 = extractor2.run(jsx_code)
    assert "interface Root" in result2
    assert "hello_world: string;" in result2
```

---

### Step 3.4: Run All Tests

**Commands:**
```bash
cd clarify-COM3-study

# Run individual tests
python test_skip_empty_restoration_3.py
python test_exclude_numeric_restoration_3.py
python test_typescript_export_restoration_3.py

# Verify no regressions
python test_classname_restoration.py
python test_apply_limit_restoration.py
```

**Expected:** All tests pass ✅

---

## Phase 4: Documentation

### Step 4.1: Create Feature Documentation

**File:** `docs/features/ORPHANED_FEATURES_RESTORATION_3.md`

**Contents:**
```markdown
# Orphaned Features Restoration

**Programmer:** #3  
**Date:** 2026-02-16  

## Features Restored

### 1. skip_empty (Jan 29 → Feb 6 → Feb 16)
- **Added:** abec8a0 (Jan 29, 2026)
- **Removed:** dd8a6bb (Feb 6, 2026)
- **Restored:** [commit hash] (Feb 16, 2026)
- **Functionality:** Filters empty/whitespace-only values from output

### 2. exclude_numeric (Jan 29 → Feb 6 → Feb 16)
- **Added:** abec8a0 (Jan 29, 2026)
- **Removed:** dd8a6bb (Feb 6, 2026)
- **Restored:** [commit hash] (Feb 16, 2026)
- **Functionality:** Filters keys that are pure numbers (e.g., "123")

### 3. typescript_export (Jan 29 → Feb 6 → Feb 16)
- **Added:** abec8a0 (Jan 29, 2026)
- **Removed:** dd8a6bb (Feb 6, 2026)
- **Restored:** [commit hash] (Feb 16, 2026)
- **Functionality:** Exports result as TypeScript interface instead of JSON

## Root Cause Analysis

The Feb 6 commit removed these features claiming they "don't exist", but this was incorrect. They DID exist and were working. The removal was likely due to:
1. Not checking git history before making changes
2. Confusion about which parameters exist
3. Testing with wrong code path

## Prevention Measures

1. Always check git history before removing features
2. Search for orphaned UI elements (checkboxes without backend)
3. Test actual user workflow, not just backend methods
4. Document feature lifecycle clearly
```

---

### Step 4.2: Update Action Plan with Results

**File:** `ACTION_PLAN_RESTORE_ORPHANED_FEATURES_3.md` (this file)

**Add at end:**
```markdown
## Execution Results

### Phase 1: Backend Restoration
- ✅ Step 1.1: Parameters added to __init__ (XX lines)
- ✅ Step 1.2: skip_empty filter restored (XX lines)
- ✅ Step 1.3: TypeScript method restored (63 lines)
- ✅ Step 1.4: TypeScript integration added (XX lines)
- **Status:** COMPLETE (XX min)

### Phase 2: GUI Integration
- ✅ Step 2.1: Checkbox states read (XX lines)
- ✅ Step 2.2: Parameters passed to backend (3 lines)
- ✅ Step 2.3: Checkboxes verified to exist
- **Status:** COMPLETE (XX min)

### Phase 3: Testing
- ✅ Step 3.1: skip_empty tests created and passing
- ✅ Step 3.2: exclude_numeric tests created and passing
- ✅ Step 3.3: typescript_export tests created and passing
- ✅ Step 3.4: No regressions detected
- **Status:** COMPLETE (XX min)

### Phase 4: Documentation
- ✅ Step 4.1: Feature documentation created
- ✅ Step 4.2: Action plan updated with results
- **Status:** COMPLETE (XX min)

### Final Commit
```bash
git add -A
git commit -m "feat: restore 3 orphaned Format Converter features

Restored features lost in commit dd8a6bb (Feb 6):
- skip_empty: Filter empty/whitespace values
- exclude_numeric: Filter numeric keys  
- typescript_export: Export as TypeScript interface

These features were originally added in abec8a0 (Jan 29) but
incorrectly removed with note 'doesn't exist'. GUI checkboxes
remained orphaned.

Backend changes (advanced_extractor.py):
- Added 3 parameters to __init__
- Restored skip_empty logic in _record_text_kv()
- Restored exclude_numeric logic in _record_text_kv()
- Restored json_to_typescript() method (63 lines)
- Integrated TypeScript export in run()

GUI changes (unified_text_to_json_dock.py):
- Connected 3 checkboxes to backend
- Pass parameters to AdvancedExtractor

Tests:
- test_skip_empty_restoration_3.py: ✅ PASS
- test_exclude_numeric_restoration_3.py: ✅ PASS
- test_typescript_export_restoration_3.py: ✅ PASS
- All previous tests: ✅ PASS

Total restoration: ~90 lines of code
Time: XX minutes
"

git push origin COM3-documentation-study
```
```

---

## Summary

**Orphaned Features Found:**
1. ✅ use_class_names (RESTORED - commit 6bcd20e)
2. ✅ _apply_limit_to_key() (RESTORED - commit 9c3cf2e)
3. ⏳ skip_empty (TO RESTORE)
4. ⏳ exclude_numeric (TO RESTORE)
5. ⏳ typescript_export (TO RESTORE)

**Total Lines to Restore:** ~90 lines
- Backend: ~87 lines
- GUI: ~3 lines
- Tests: ~150 lines (new)
- Docs: ~100 lines (new)

**Estimated Time:** 1.5 hours

**Risk Assessment:** LOW
- Features existed before and worked
- GUI already has checkboxes
- Only need to reconnect backend to frontend
- No breaking changes to existing functionality

---

## Notes

1. **Git History Lesson:** Always check git history before removing features
2. **Orphaned UI Pattern:** Checkboxes exist but do nothing - clear sign of orphaned code
3. **Testing Strategy:** Test actual user workflow, not just backend methods
4. **Documentation:** Feature lifecycle should be tracked in git commits

## References

- Original implementation: commit abec8a0 (Jan 29, 2026)
- Incorrect removal: commit dd8a6bb (Feb 6, 2026)
- Previous restorations: commits 6bcd20e, 9c3cf2e (Feb 16, 2026)
