# Code Study Session 5: Data Processing

**Programmer**: #4  
**Branch**: COM4-code-study  
**Date**: 2026-01-21  
**Duration**: 1 hour  
**Focus**: Set operations, calculator operations, diff analyzer, export/history managers  

---

## 📊 TL;DR (2AM Reference)

**Files Studied**: 5 files, 1,500 LOC  
**Key Discovery**: Core business logic for JSON set operations (∩ ∪ − ⊕)  
**Critical Pattern**: Strategy + Template Method for operations  
**Production Feature**: Multi-format export (CSV, Excel, YAML, TOML)  

**If set operations fail**:
```python
# Check path security:
from src.set_operations import validate_file_path
if not validate_file_path(file):
    # CWE-22: Path traversal blocked
    
# Emergency fallback:
result = {"error": "operation_failed", "data": []}
```

---

## 📁 Files Analyzed

### 1. set_operations.py (439 lines)
**Purpose**: Core JSON set operations (∩ ∪ − ⊕)  
**Version**: v2.9.32  
**Pattern**: Strategy + Template Method  

**Key Features**:
- ✅ 4 set operations (intersection, union, difference, symmetric_difference)
- ✅ Security validation (CWE-22: Path Traversal)
- ✅ Flatten/unflatten JSON (dot notation)
- ✅ 3 comparison modes (key_value, full_path_value, key_only)
- ✅ Normalization options (case-insensitive, skip_empty, arrays_ignore_order)
- ✅ Pipeline processing (left-to-right A ∩ B ∩ C)
- ✅ Statistics tracking

---

### 2. calculator_operations.py (264 lines)
**Purpose**: Set operations for Calculator Memory slots  
**Version**: v2.9.101  
**Pattern**: Facade over set_operations  

**Key Features**:
- ✅ 4 operations (Add/Merge, Intersection, Union, Difference)
- ✅ Deep merge via MergeManager
- ✅ Tuple returns (success, data, message)
- ✅ Summary statistics
- ✅ Consistency with SetOperations dock

---

### 3. diff_analyzer.py (241 lines)
**Purpose**: Diff visualization for JSON comparison  
**Version**: v2.9.99  
**Pattern**: Analyzer with categorization  

**Key Features**:
- ✅ 4 diff categories (only_in_a, only_in_b, common, modified)
- ✅ Value comparison logic
- ✅ Flatten/unflatten support
- ✅ Visual diff preparation
- ✅ Integrated with Set Operations UI

---

### 4. export_manager.py (382 lines)
**Purpose**: Multi-format export (CSV, Excel, YAML, TOML)  
**Version**: v2.9.93  
**Pattern**: Static utility class with format strategies  

**Key Features**:
- ✅ CSV export (flat key-value)
- ✅ Excel export (XLSX with styling)
- ✅ YAML export (pyyaml)
- ✅ TOML export (tomli-w)
- ✅ JSON export (pretty-printed)
- ✅ Metadata injection (timestamp, tool version)
- ✅ Optional dependencies (graceful degradation)
- ✅ Progress modal integration

---

### 5. history_manager.py (174 lines)
**Purpose**: Operation history tracking  
**Version**: Unknown  
**Pattern**: Circular buffer with QSettings persistence  

**Key Features**:
- ✅ Last 50 operations stored
- ✅ QSettings persistence
- ✅ Re-execution capability (result_data stored)
- ✅ Export to JSON
- ✅ Import from JSON
- ✅ Clear history
- ✅ Timestamp tracking

---

## 🎯 Architecture Analysis

### Set Operations Pipeline

**Flow**:
```
JSON Files → Validate → Flatten → Normalize → Set Op → Unflatten → JSON Result
```

**Step-by-step**:
1. **Validate**: Check paths (CWE-22: Path Traversal)
2. **Flatten**: Nested JSON → dot notation `{"a": {"b": 1}}` → `{"a.b": 1}`
3. **Normalize**: Apply case-insensitive, skip_empty, array_ignore_order
4. **Set Operation**: Python set operations (& | - ^)
5. **Unflatten**: Dot notation → nested JSON (reverse step 2)
6. **Return**: JSON object with results

---

### Comparison Modes

**3 modes available**:

#### 1. `"key_value"` (default)
```python
# Compare: Last part of key + value
{"user.name": "John"} vs {"admin.name": "John"}
→ Match! (both have "name": "John")
```

**Use case**: Find same values across different paths

---

#### 2. `"full_path_value"`
```python
# Compare: Full path + value
{"user.name": "John"} vs {"admin.name": "John"}
→ No match (paths differ)
```

**Use case**: Exact structure matching

---

#### 3. `"key_only"`
```python
# Compare: Just the key (ignore value)
{"user.name": "John"} vs {"user.name": "Jane"}
→ Match! (both have "user.name")
```

**Use case**: Find common structure (any value)

---

### Normalization Options

```python
options = {
    'ignore_case_keys': False,      # "Name" == "name"
    'ignore_case_values': False,    # "John" == "JOHN"
    'skip_empty': True,             # Skip "" values
    'arrays_ignore_order': False    # [1,2,3] == [3,2,1]
}
```

**Why each option?**
- **ignore_case_keys**: Handle inconsistent casing in JSON keys
- **ignore_case_values**: Compare text values case-insensitively
- **skip_empty**: Ignore placeholder/empty values
- **arrays_ignore_order**: Treat arrays as sets (order doesn't matter)

---

## 🔍 Design Patterns Identified

### 1. ✅ Strategy Pattern (Set Operations)
**Location**: set_operations.py

```python
# Each operation is a strategy:
def intersection(file_dicts, **options) -> Dict:
    """A ∩ B ∩ C ..."""
    pass

def union(file_dicts, **options) -> Dict:
    """A ∪ B ∪ C ..."""
    pass

def difference(file_dicts, **options) -> Dict:
    """A - B - C ..."""
    pass

def symmetric_difference(file_a, file_b, **options) -> Dict:
    """A ⊕ B"""
    pass
```

**Why**: Different operations, same interface (`**options`)

---

### 2. ✅ Template Method Pattern (Operation Pipeline)
**Location**: set_operations.py lines 195-253

```python
def compare_files(file_dicts, **options) -> Tuple:
    """Template method for all operations"""
    # Step 1: Prepare (flatten + normalize)
    prepared = []
    for obj in file_dicts:
        flat = flatten_json(obj)
        norm = normalize(flat, options)
        prepared.append(norm)
    
    # Step 2: Return prepared sets (subclass executes set op)
    return prepared, stats
```

**Why**: Common pipeline, operation-specific logic in separate functions

---

### 3. ✅ Facade Pattern (CalculatorOperations)
**Location**: calculator_operations.py

```python
class CalculatorOperations:
    """Facade over set_operations.py"""
    
    @staticmethod
    def intersection(data_a, data_b, mode):
        # Internal: Use set_operations logic
        from .set_operations import flatten_json, normalize
        # ... complex logic hidden
        return (success, result, message)  # Simple tuple return
```

**Why**: Simplifies complex set_operations API for Calculator use case

---

### 4. ✅ Command Pattern (History Entries)
**Location**: history_manager.py lines 21-60

```python
entry = {
    "operation_type": "∩",      # Command type
    "file1": "/path/a.json",    # Arguments
    "file2": "/path/b.json",
    "comparison_mode": "key_value",
    "result_data": [...]        # Result (for replay)
}
history.append(entry)  # Store command
```

**Why**: Operations can be replayed, logged, exported

---

### 5. ✅ Adapter Pattern (Export Format Adapters)
**Location**: export_manager.py

```python
# Adapts JSON data to different formats:
@staticmethod
def export_to_csv(data, path):
    """Adapt to CSV"""
    flat = flatten_dict(data)  # Adapter step
    with open(path, 'w') as f:
        writer = csv.writer(f)
        for k, v in flat.items():
            writer.writerow([k, v])

@staticmethod
def export_to_excel(data, path):
    """Adapt to Excel"""
    flat = flatten_dict(data)  # Same adapter step
    wb = openpyxl.Workbook()
    # ... Excel-specific logic

@staticmethod
def export_to_yaml(data, path):
    """Adapt to YAML"""
    # No flattening needed, YAML handles nested
    yaml.dump(data, f)
```

**Why**: Single data structure, multiple output formats

---

### 6. ✅ Circular Buffer Pattern (History Storage)
**Location**: history_manager.py lines 53-60

```python
history.insert(0, new_entry)  # Add at start (newest first)

if len(history) > MAX_ENTRIES:
    history = history[:MAX_ENTRIES]  # Keep only last 50
```

**Why**: Fixed memory usage, automatic cleanup

---

### 7. ✅ Fluent Interface (Optional - not used yet)
**Potential**: Set operations could be chained

```python
# NOT IMPLEMENTED (but architecture supports it):
result = (SetOperations()
    .load('a.json')
    .intersect('b.json')
    .union('c.json')
    .difference('d.json')
    .export('result.csv'))
```

**Why mention**: Architecture is ready for this enhancement

---

## 🔧 Security Analysis

### CWE-22: Path Traversal Prevention

**Location**: set_operations.py lines 26-64

```python
def validate_file_path(file_path: str) -> bool:
    """
    Security validation against path traversal attacks.
    
    Checks:
    1. File must exist
    2. Must be a file (not directory)
    3. Must have .json extension
    4. Must be readable (permissions)
    5. Path is absolute (no ../ tricks)
    """
    abs_path = Path(file_path).resolve()  # Resolves ../ and symlinks
    
    if not abs_path.exists(): return False
    if not abs_path.is_file(): return False
    if abs_path.suffix.lower() != ".json": return False
    if not os.access(abs_path, os.R_OK): return False
    
    return True
```

**Attack examples prevented**:
```python
# ❌ Path traversal:
validate_file_path("../../etc/passwd")  # False (not .json)

# ❌ Directory access:
validate_file_path("/home/user/")  # False (not a file)

# ❌ Symlink to /etc:
validate_file_path("/tmp/symlink.json")  # False (resolves to actual path, checked)

# ✅ Legitimate file:
validate_file_path("/home/user/data.json")  # True
```

**OWASP Compliance**: ✅ Prevents CWE-22 (Improper Limitation of Pathname)

---

## 💡 Flatten/Unflatten Deep Dive

### Why Flatten?

**Problem**: Nested JSON is hard to compare
```json
{
  "user": {
    "profile": {
      "name": "John",
      "age": 30
    }
  }
}
```

**Solution**: Flatten to dot notation
```json
{
  "user.profile.name": "John",
  "user.profile.age": 30
}
```

**Benefit**: Now can use Python `set()` operations directly

---

### Flatten Algorithm

```python
def flatten_json(obj, parent_key="", sep="."):
    items = []
    
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep).items())
    
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(v, new_key, sep).items())
    
    else:
        # Leaf value (primitive)
        return {parent_key: obj}
    
    return dict(items)
```

**Handles**:
- Nested dicts: `a.b.c`
- Arrays: `items.0`, `items.1`, `items.2`
- Mixed: `users.0.name`, `users.1.name`

---

### Unflatten Algorithm

**Reverse process**:
```python
{"user.profile.name": "John"} → {"user": {"profile": {"name": "John"}}}
```

**Implementation** (simplified):
```python
def unflatten(flat_dict):
    result = {}
    for key, value in flat_dict.items():
        parts = key.split('.')
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result
```

---

## 📊 Export Manager Deep Dive

### Multi-Format Support

**Why multiple formats?**
1. **CSV**: Excel compatibility, simple format
2. **Excel**: Professional reports, styling
3. **YAML**: Human-readable config files
4. **TOML**: Modern config format (Rust, Python)
5. **JSON**: Standard interchange format

---

### Optional Dependencies

```python
try:
    import openpyxl
    _EXCEL_AVAILABLE = True
except ImportError:
    _EXCEL_AVAILABLE = False

# Later:
if not _EXCEL_AVAILABLE:
    raise ImportError("openpyxl required. Install: pip install openpyxl")
```

**Why this pattern?**
- ✅ Core functionality works without optional deps
- ✅ Clear error messages
- ✅ User installs only what they need
- ✅ Smaller base installation

**Dependencies**:
- **Required**: None (JSON is built-in)
- **Optional**: openpyxl (Excel), pyyaml (YAML), tomli-w (TOML)

---

### Metadata Injection

```python
metadata = {
    '_metadata': {
        'exported_at': '2026-01-21T13:48:00',
        'operation': 'intersection',
        'export_tool': 'Clarify v2.9.93'
    }
}
result = {**metadata, **data}
```

**Why metadata?**
- Track when/how data was created
- Tool versioning (reproducibility)
- Operation context (debugging)
- Compliance (audit trails)

---

### Excel Styling

```python
# Header styling:
header_font = Font(bold=True, size=12)
header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")

ws['A1'].font = header_font
ws['A1'].fill = header_fill

# Auto-adjust columns:
ws.column_dimensions['A'].width = 50
ws.column_dimensions['B'].width = 80
```

**Why**: Professional-looking exports, better UX

---

## 🎓 Top 5 Lessons Learned

### 1. **Flatten/Unflatten Enables Set Operations**
**Evidence**:
```python
# Without flattening:
a = {"user": {"name": "John"}}
b = {"user": {"name": "John"}}
a == b  # False (dict comparison is shallow)

# With flattening:
flat_a = {"user.name": "John"}
flat_b = {"user.name": "John"}
set(flat_a.items()) & set(flat_b.items())  # {("user.name", "John")}
```

**Lesson**: Transform complex data into simple sets

---

### 2. **Security Validation at Boundaries**
**Evidence**: validate_file_path() checks 5 conditions before ANY file access

**Lesson**: Validate early, fail fast, prevent attacks

---

### 3. **Template Method + Strategy = Flexibility**
**Evidence**:
- compare_files() = template (prepare data)
- intersection/union/difference = strategies (execute set op)

**Lesson**: Separate common logic from variant logic

---

### 4. **Optional Dependencies Improve Adoption**
**Evidence**: ExportManager works with 0 optional deps (JSON only)

**Lesson**: Core features always available, advanced features opt-in

---

### 5. **History = Undo + Learning + Debugging**
**Evidence**:
```python
# User executes operation
result = intersection(a, b)

# Later, user forgets settings:
history_mgr.get_entry(0)
# Returns: {"operation": "∩", "files": ["a.json", "b.json"], 
#           "mode": "key_value", "result_data": [...]}

# Can re-execute or learn from past
```

**Lesson**: Logging operations enables time travel

---

## 🚨 Known Issues & Gotchas

### Issue 1: Unflatten Loses Type Information

**Problem**:
```python
# Original:
{"items": [1, 2, 3]}

# Flattened:
{"items.0": 1, "items.1": 2, "items.2": 3}

# Unflattened:
{"items": {"0": 1, "1": 2, "2": 3}}  # ❌ Now a dict, not array!
```

**Consequence**: Array structure lost after flatten/unflatten

**Mitigation**: Store type hints during flatten (not implemented yet)

---

### Issue 2: Large File Memory Usage

**Problem**: All files loaded into memory simultaneously

```python
# If files are 100MB each:
files = [load(f1), load(f2), load(f3)]  # 300MB in RAM!
```

**Mitigation**: Not implemented (could use streaming or chunking)

---

### Issue 3: Circular Buffer Doesn't Persist on Crash

**Problem**: History stored in QSettings, written on app exit

**Consequence**: If app crashes, recent history lost

**Mitigation**: Could write after each operation (performance trade-off)

---

## 📊 Session Statistics

| Metric | Value |
|--------|-------|
| **Files studied** | 5 |
| **Lines of code** | 1,500 |
| **Design patterns** | 7 |
| **Key classes** | 5 (SetOps, CalcOps, DiffAnalyzer, ExportMgr, HistoryMgr) |
| **Operations** | 4 (∩ ∪ − ⊕) |
| **Export formats** | 5 (CSV, Excel, YAML, TOML, JSON) |
| **Security checks** | 5 (CWE-22 validation) |
| **Comparison modes** | 3 (key_value, full_path_value, key_only) |
| **Duration** | 1 hour |

---

## 🔗 Connections to Previous Sessions

### Session 1 (Root Level)
- **app.py**: Coordinates set operations via docks

### Session 2 (Critical Branches)
- **file_explorer_dock.py**: Uses export_manager for CSV export

### Session 3 (Key Leaves)
- **translator.py**: Export supports i18n (metadata in user language)

### Session 4 (Configuration)
- **config_manager.py**: Export format preferences stored
- **history_manager.py**: Uses QSettings (like config)

**Pattern**: Data processing is leaf-level (no dependencies on UI)

---

## ⏭️ Next Steps

**Session 6**: Text Extraction (extractor.py, jsx_parser.py, generic_parser.py, normalizer.py)

**Why**: Understand how search content extraction works

**Estimated**: 45 minutes

---

## 📝 Quick Reference

### Set Operations Cheat Sheet

```python
# Intersection (A ∩ B) - Common elements
result = intersection([a, b], comparison_mode="key_value")

# Union (A ∪ B) - All elements
result = union([a, b], comparison_mode="key_value")

# Difference (A − B) - Only in A
result = difference([a, b], comparison_mode="key_value")

# Symmetric Difference (A ⊕ B) - In A or B, not both
result = symmetric_difference(a, b, comparison_mode="key_value")
```

### Export Cheat Sheet

```python
from src.export_manager import ExportManager

# CSV
ExportManager.export_to_csv(data, Path("out.csv"))

# Excel (requires openpyxl)
ExportManager.export_to_excel(data, Path("out.xlsx"))

# YAML (requires pyyaml)
ExportManager.export_to_yaml(data, Path("out.yaml"))

# TOML (requires tomli-w)
ExportManager.export_to_toml(data, Path("out.toml"), flatten=True)
```

---

**Session 5 Complete** ✅  
**Programmer #4** - Data Processing Deep Dive  
**Date**: 2026-01-21 13:58 UTC
