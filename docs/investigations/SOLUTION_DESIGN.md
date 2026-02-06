# SOLUTION DESIGN - FILE EXPLORER BUG FIXES

**Date:** 2026-01-08 16:45 UTC  
**Protocol:** Simplicidade 3 - Phase 4  
**Status:** Designing minimal fixes

---

## DESIGN PRINCIPLES

Following Protocolo Simplicidade 3:
1. **Minimal changes** - Touch only what's necessary
2. **No breaking changes** - Maintain backward compatibility
3. **Surgical precision** - Fix the bug, nothing else
4. **Type-safe** - Proper type handling
5. **i18n-safe** - Work with all languages

---

## ISSUE #5: Type Filter i18n Bug (CRITICAL)

### Current Code
**File:** `src/gui/file_explorer_dock.py`  
**Lines:** 179-181, 910, 916-919

### Solution: Use QComboBox data instead of text

**Change 1 - Add data to combo items (lines 179-181):**
```python
# OLD:
self.combo_type.addItems(
    [tr("file_list.type_any"), tr("file_list.type_files_only"), tr("file_list.type_directories_only")]
)

# NEW:
self.combo_type.addItem(tr("file_list.type_any"), "any")
self.combo_type.addItem(tr("file_list.type_files_only"), "files")
self.combo_type.addItem(tr("file_list.type_directories_only"), "dirs")
```

**Change 2 - Use currentData() instead of currentText() (lines 910, 916-919):**
```python
# OLD:
type_filter = self.combo_type.currentText()

# Get advanced filters
filters = self._build_filters()

# Add type filter to filters dict
if type_filter == "Files Only":
    filters["type"] = "files"
elif type_filter == "Directories Only":
    filters["type"] = "dirs"

# NEW:
type_filter_data = self.combo_type.currentData()

# Get advanced filters
filters = self._build_filters()

# Add type filter to filters dict
if type_filter_data == "files":
    filters["type"] = "files"
elif type_filter_data == "dirs":
    filters["type"] = "dirs"
```

**Lines affected:** 2 locations (179-181, 910-920)  
**Complexity:** Low  
**Risk:** Minimal - data-based approach is standard Qt pattern  
**Testing:** Verify in Portuguese/English

---

## ISSUE #1: Exclude Globs Pattern Matching (HIGH)

### Current Code
**File:** `src/core/file_explorer_executor.py`  
**Lines:** 134-137

### Solution: Check if pattern exists as path component

**Change - Replace fnmatch with path component check:**
```python
# OLD:
for pattern in exclude_globs:
    if fnmatch.fnmatch(file_path, f"*{pattern}*") or fnmatch.fnmatch(file_name, pattern):
        excluded = True
        break

# NEW:
for pattern in exclude_globs:
    # Check if pattern exists as a path component (directory name)
    path_components = file_path.split(os.sep)
    if pattern in path_components:
        excluded = True
        break
    # Also check if pattern matches filename (for patterns like *.pyc)
    if fnmatch.fnmatch(file_name, pattern):
        excluded = True
        break
```

**Lines affected:** 134-137 (4 lines → 10 lines)  
**Complexity:** Low  
**Risk:** Minimal - more accurate pattern matching  
**Testing:** Verify `.venv`, `node_modules`, `*.pyc` work correctly

---

## ISSUE #3: Case/Regex Checkboxes Signal Bug (MEDIUM)

### Current Code
**File:** `src/gui/widgets/search_widgets.py`  
**Lines:** 364-372, 382-387

### Solution: Fix signal connection and enable for text fields

**Change 1 - Enable for all text fields (line 366, 371):**
```python
# OLD:
chk_case.setEnabled(False)  # Only enabled for content field
chk_regex.setEnabled(False)  # Only enabled for content field

# NEW:
chk_case.setEnabled(True)  # Enable by default for text fields
chk_regex.setEnabled(True)  # Enable by default for text fields
```

**Change 2 - Fix signal and logic (lines 382-387):**
```python
# OLD:
def on_field_changed(field):
    is_content = field == "content"
    chk_case.setEnabled(is_content)
    chk_regex.setEnabled(is_content)

combo_field.currentTextChanged.connect(on_field_changed)

# NEW:
def on_field_changed(index):
    field_data = combo_field.itemData(index)
    # Enable for text fields: filename, path, ext, content
    is_text_field = field_data in ("filename", "path", "ext", "content")
    chk_case.setEnabled(is_text_field)
    chk_regex.setEnabled(is_text_field)

combo_field.currentIndexChanged.connect(on_field_changed)
```

**Lines affected:** 366, 371, 382-387 (10 lines)  
**Complexity:** Low  
**Risk:** Minimal - standard Qt signal pattern  
**Testing:** Verify checkboxes enable/disable correctly for each field

---

## ISSUE #4: Operators Display Symbols (LOW)

### Current Code
**File:** `src/gui/widgets/search_widgets.py`  
**Lines:** 349-355

### Solution: Replace symbols with full text

**Change - Use descriptive text instead of symbols:**
```python
# OLD:
combo_operator.addItems(
    ["equals", "not equals", "contains", "not contains", "greater than", "<", ">=", "<=", "regex"]
)

# NEW:
combo_operator.addItems([
    "equals",
    "not equals",
    "contains",
    "not contains",
    "greater than",
    "less than",  # was "<"
    "greater than or equal",  # was ">="
    "less than or equal",  # was "<="
    "regex"
])
```

**Lines affected:** 352 (1 line)  
**Complexity:** Trivial  
**Risk:** None - pure display change  
**Testing:** Visual verification only

---

## IMPLEMENTATION ORDER

Following priority:
1. **Issue #5** (CRITICAL) - 2 locations, ~10 lines
2. **Issue #1** (HIGH) - 1 location, ~6 lines
3. **Issue #3** (MEDIUM) - 2 locations, ~10 lines
4. **Issue #4** (LOW) - 1 location, ~1 line

**Total Lines Changed:** ~27 lines across 3 files  
**Estimated Time:** 30-40 minutes implementation + 20 minutes testing

---

## SIDE EFFECTS ANALYSIS

### Issue #5 Fix
- **Affects:** Type filter behavior
- **Risk:** None - data-based is more reliable than text-based
- **Compatibility:** Maintains same functionality, just fixes i18n

### Issue #1 Fix
- **Affects:** Exclude glob filtering
- **Risk:** Low - more accurate matching
- **Compatibility:** May exclude MORE files (correct behavior)
- **Note:** Users may notice files they didn't see before are now properly excluded

### Issue #3 Fix
- **Affects:** Case/Regex checkbox availability
- **Risk:** Low - enables features that should work
- **Compatibility:** Users can now use case/regex for all text fields

### Issue #4 Fix
- **Affects:** Operator display only
- **Risk:** None - cosmetic change
- **Compatibility:** No functional change

---

## TESTING STRATEGY

### Manual Tests

**Issue #5:**
1. Switch language to Portuguese
2. Select "Apenas Arquivos" (Files Only)
3. List files
4. Verify only files shown (no directories)

**Issue #1:**
1. Add `.venv` to exclude globs
2. Browse directory with `.venv/` subdirectory
3. Verify `.venv/` files are excluded

**Issue #3:**
1. Add condition: field=path, operator=contains
2. Verify Case checkbox is enabled
3. Verify Regex checkbox is enabled

**Issue #4:**
1. Open advanced conditions
2. Verify operators show "less than", not "<"
3. Verify "less than or equal", not "<="

### Regression Tests

- Verify existing exclude patterns still work (node_modules, dist, build, .git)
- Verify type filter works in English
- Verify conditions work for content field
- Verify operators work correctly (not just display)

---

## READY FOR IMPLEMENTATION ✅

All solutions designed, side effects analyzed, testing strategy defined.

**Next:** Phase 5 - Implementation

**Estimated Time:** 60 minutes (40 implementation + 20 testing)
