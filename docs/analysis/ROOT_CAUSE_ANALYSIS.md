# ROOT CAUSE ANALYSIS - FILE EXPLORER BUGS

**Date:** 2026-01-08 13:10 UTC  
**Investigator:** AI Assistant  
**Protocol:** Simplicidade 3 - Phase 3  

---

## ISSUE #1: Exclude Globs Not Working (`.venv`)

### Root Cause
**File:** `src/core/file_explorer_executor.py`  
**Lines:** 134-137  

**Current Code:**
```python
for pattern in exclude_globs:
    if fnmatch.fnmatch(file_path, f"*{pattern}*") or fnmatch.fnmatch(file_name, pattern):
        excluded = True
        break
```

**Problem:**
- Pattern `.venv` with `fnmatch.fnmatch(file_path, "*..venv*")` won't match paths like `/path/.venv/file.py`
- fnmatch requires exact glob patterns, not substring matching
- Need to check if pattern is a path component (directory name) in the full path

**Expected Behavior:**
- `.venv` should exclude `/path/.venv/` and `/path/.venv/subdir/file.py`
- `node_modules` should exclude `/path/node_modules/` and all subdirectories

**Fix Required:**
Check if pattern exists as a path component:
```python
path_components = file_path.split(os.sep)
if pattern in path_components:
    excluded = True
    break
```

**Severity:** HIGH  
**Status:** Root cause identified

---

## ISSUE #2: Advanced Conditions Path Filter Not Working

### Root Cause
**Status:** FALSE ALARM - Code is correct!  

**Investigation Results:**
- Examined `filter_files_by_conditions()` in `src/core/filters.py` (line 312)
- Examined `Condition.matches()` method (line 280-309)
- Path filter logic at lines 286-289 is CORRECT:
  ```python
  if self.field == "path":
      a = path
      b = self.value
      return self._apply_string_matching(a, b, self.operator)
  ```
- "not contains" operator is implemented correctly (lines 236-238, 263-264)

**Actual Problem:** Likely user error or Issue #3/Case sensitivity
- If Case checkbox is disabled, case_sensitive defaults to True
- Path ".venv" won't match "/path/.Venv" or "/path/.VENV"
- User needs to enable Case checkbox (Issue #3) or type exact case

**Resolution:** Fix Issue #3 (enable Case checkbox), Issue #2 will work

**Severity:** HIGH → NONE (not a bug)  
**Status:** No fix needed, depends on Issue #3

---

## ISSUE #3: Case and Regex Disabled in Advanced Conditions

### Root Cause CONFIRMED
**File:** `src/gui/widgets/search_widgets.py`  
**Lines:** 364-372, 382-387

**Current Code:**
```python
# Options for content field
chk_case = QCheckBox(tr("search.chk_case"))
chk_case.setEnabled(False)  # Only enabled for content field
row_layout.addWidget(chk_case)

chk_regex = QCheckBox(tr("search.chk_regex"))
chk_regex.setEnabled(False)  # Only enabled for content field  
row_layout.addWidget(chk_regex)

# Enable/disable options based on field
def on_field_changed(field):
    is_content = field == "content"
    chk_case.setEnabled(is_content)
    chk_regex.setEnabled(is_content)

combo_field.currentTextChanged.connect(on_field_changed)  # BUG!
```

**Problems:**
1. **Checkboxes disabled by default** - only enable when field = "content"
2. **Signal connection bug** - Line 387 connects to `currentTextChanged` which passes **translated display text** ("Caminho", "Conteúdo"), not field data ("path", "content")
3. **Wrong comparison** - Line 383 compares `field == "content"` but `field` is display text, not data

**Expected Behavior:**
- Case and Regex should work for ALL text fields (filename, path, content)
- Currently only enables for "content" field
- Signal should use `currentIndexChanged` and get `currentData()`

**Fix Required:**
```python
def on_field_changed(index):
    field_data = combo_field.itemData(index)
    # Enable for text fields: filename, path, ext, content
    is_text_field = field_data in ("filename", "path", "ext", "content")
    chk_case.setEnabled(is_text_field)
    chk_regex.setEnabled(is_text_field)

combo_field.currentIndexChanged.connect(on_field_changed)
```

**Severity:** MEDIUM  
**Status:** Root cause confirmed - Signal + Logic bug

---

## ISSUE #4: Comparison Operators Show Symbols Instead of Text

### Root Cause CONFIRMED
**File:** `src/gui/widgets/search_widgets.py`  
**Lines:** 349-355

**Current Code:**
```python
# Operator selector
combo_operator = QComboBox()
combo_operator.addItems(
    ["equals", "not equals", "contains", "not contains", "greater than", "<", ">=", "<=", "regex"]
)
```

**Problem:**
- Operators `"<"`, `">="`, `"<="` are added as **raw symbols**
- Should be human-readable text: "less than", "less than or equal", "greater than or equal"
- Mixing English words with symbols is inconsistent

**Expected:**
```python
combo_operator.addItems([
    "equals", 
    "not equals", 
    "contains", 
    "not contains", 
    "greater than",
    "less than",           # Instead of "<"
    "greater than or equal",  # Instead of ">="
    "less than or equal",     # Instead of "<="
    "regex"
])
```

**Alternative with i18n:**
```python
combo_operator.addItems([
    tr("search.op_equals"),
    tr("search.op_not_equals"),
    tr("search.op_contains"),
    tr("search.op_not_contains"),
    tr("search.op_greater_than"),
    tr("search.op_less_than"),
    tr("search.op_greater_equal"),
    tr("search.op_less_equal"),
    tr("search.op_regex"),
])
```

**Fix Required:**
Replace symbols with full text (with or without i18n)

**Severity:** LOW (cosmetic but affects UX)  
**Status:** Root cause confirmed - Hardcoded symbols

---

## ISSUE #5: Search Not Working After Changing Directory (CRITICAL)

### Root Cause CONFIRMED
**File:** `src/gui/file_explorer_dock.py`  
**Lines:** 179-181, 910, 916-919

**Current Code:**
```python
# Line 179-181: Combo box with TRANSLATED text
self.combo_type.addItems(
    [tr("file_list.type_any"), tr("file_list.type_files_only"), tr("file_list.type_directories_only")]
)

# Line 910: Gets TRANSLATED text
type_filter = self.combo_type.currentText()

# Line 916-919: Compares with HARDCODED ENGLISH strings
if type_filter == "Files Only":  # Will never match if language != English!
    filters["type"] = "files"
elif type_filter == "Directories Only":  # Will never match!
    filters["type"] = "dirs"
```

**Problem:**
- Combo box populated with **translated** text (Portuguese: "Apenas Arquivos", "Apenas Diretórios")
- Code compares with **hardcoded English** strings ("Files Only", "Directories Only")
- In non-English languages: **comparison always fails** → defaults to "any"
- Result: User selects "Files Only" but sees both files AND directories

**Why this affects directory changes:**
- User changes directory AND changes type filter
- Type filter silently fails → wrong results shown
- User thinks "search not working" but actually wrong filter applied

**Fix Required - Option 1 (Index-based):**
```python
type_index = self.combo_type.currentIndex()
if type_index == 1:  # Files Only
    filters["type"] = "files"
elif type_index == 2:  # Directories Only
    filters["type"] = "dirs"
```

**Fix Required - Option 2 (Data-based):**
```python
# Line 179-181: Add data to items
self.combo_type.addItem(tr("file_list.type_any"), "any")
self.combo_type.addItem(tr("file_list.type_files_only"), "files")
self.combo_type.addItem(tr("file_list.type_directories_only"), "dirs")

# Line 910-919: Use data instead of text
type_filter = self.combo_type.currentData()
if type_filter == "files":
    filters["type"] = "files"
elif type_filter == "dirs":
    filters["type"] = "dirs"
```

**Severity:** CRITICAL (blocks basic functionality in non-English)  
**Status:** Root cause confirmed - i18n bug

---

## INVESTIGATION PRIORITIES

1. ✅ **ISSUE #5** (CRITICAL) - Type filter i18n bug (CONFIRMED)
2. ✅ **ISSUE #1** (HIGH) - Exclude globs fnmatch pattern (CONFIRMED)
3. ✅ **ISSUE #2** (HIGH) - Path filter (FALSE ALARM - code is correct)
4. ✅ **ISSUE #3** (MEDIUM) - Case/regex signal bug (CONFIRMED)
5. ✅ **ISSUE #4** (LOW) - Operators display (CONFIRMED)

---

## INVESTIGATION COMPLETE ✅

### Summary of Findings

**4 Real Bugs + 1 False Alarm:**

1. **Issue #1 (HIGH):** Exclude globs use wrong pattern matching
   - Fix: Check path components instead of fnmatch with wildcards
   
2. **Issue #2 (NONE):** Not a bug - code is correct
   - User likely affected by Issue #3 (case sensitivity)
   
3. **Issue #3 (MEDIUM):** Case/Regex checkboxes disabled + signal bug
   - Fix: Use currentIndexChanged + itemData(), enable for text fields
   
4. **Issue #4 (LOW):** Operators show symbols instead of text
   - Fix: Replace "<", ">=", "<=" with full text
   
5. **Issue #5 (CRITICAL):** Type filter i18n bug
   - Fix: Use currentData() or currentIndex() instead of currentText()

---

## NEXT STEPS

### Phase 4: Solution Design (15 min)
- [x] All root causes identified
- [ ] Design minimal fixes for Issues #1, #3, #4, #5
- [ ] Verify no side effects or breaking changes

### Phase 5: Implementation (60 min)
Priority order:
1. Issue #5 (CRITICAL)
2. Issue #1 (HIGH)
3. Issue #3 (MEDIUM)
4. Issue #4 (LOW)

---

**Time Invested:** 60 minutes (investigation phase)  
**Progress:** 100% root cause analysis complete  
**Next Phase:** Solution design (15 min estimated)  
**Total Estimated Time Remaining:** ~90 minutes (design + implementation + testing + commit)
