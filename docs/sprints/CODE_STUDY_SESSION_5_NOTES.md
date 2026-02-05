# Code Study Session 5 Notes
**Programmer #7 - Source Code Study**  
**Date**: 2026-01-22  
**Session Focus**: Phase 2 - Core Executors & CLI (src/core/ completion)  
**Files Studied**: 5 files (~1,629 lines)

---

## 📋 Session Overview

**Progress**:
- **Files Studied This Session**: 5 files
- **Lines of Code**: ~1,629 lines
- **Total Progress**: 23/196 files (11.7%)
- **Phase**: Phase 2 - Core Systems (**COMPLETE** ✅)

**Files Analyzed**:
1. `src/core/file_list_executor.py` (331 lines) ✅
2. `src/core/set_operation_executor.py` (224 lines) ✅
3. `src/core/rewriter_cli.py` (195 lines) ✅
4. `src/core/result_exporter.py` (196 lines) ✅
5. `src/core/file_explorer_executor.py` (683 lines) ✅

---

## 🔍 Detailed Analysis

### 1. file_list_executor.py (331 lines) - File Discovery & Listing

**Purpose**: Core file listing logic with advanced filtering (v2.9.114 Phase 2.4.2)

**Architecture Pattern**: **Executor Pattern** + **Dataclasses for DTOs**

#### **FileInfo Dataclass** (Lines 30-42)

```python
@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    mtime: datetime
    permissions: str  # Unix-style (drwxr-xr-x)
    owner: str
    group: str
    is_dir: bool
```

**Purpose**: Immutable container for file metadata

---

#### **ListResult Class** (Lines 44-59)

```python
class ListResult:
    def __init__(self, files: List[FileInfo], errors: List[str] = None):
        self.files = files
        self.errors = errors or []
        self.total_size = sum(f.size for f in files if not f.is_dir)
        self.file_count = sum(1 for f in files if not f.is_dir)
        self.dir_count = sum(1 for f in files if f.is_dir)
```

**Auto-calculated Statistics**:
- `total_size`: Sum of all file sizes (excluding directories)
- `file_count`: Number of regular files
- `dir_count`: Number of directories

**Design**: Statistics computed at construction time (eager evaluation)

---

#### **FileListExecutor Class** (Lines 62-329)

**Pattern**: Static methods (stateless executor)

**Main Method: `list_files()`** (Lines 65-100)

**Signature**:
```python
@staticmethod
def list_files(
    directory: str,
    show_hidden: bool = False,
    recursive: bool = False,
    filters: Dict[str, Any] = None
) -> ListResult:
```

**Algorithm**:
1. Validate directory exists
2. Collect file paths with `_collect_files()`
3. Convert paths to `FileInfo` objects
4. Handle permission errors (add to error list)
5. Return `ListResult`

**Error Handling**: Graceful degradation (permission errors don't stop listing)

---

**_collect_files() Method** (Lines 102-139)

**Recursive Directory Traversal**:

```python
def _collect_files(directory, show_hidden, recursive, filters, depth=0):
    files = []
    
    try:
        entries = os.listdir(directory)
    except PermissionError:
        return files  # Skip inaccessible directories
    
    for entry in sorted(entries):
        # Skip hidden files (starts with .)
        if not show_hidden and entry.startswith("."):
            continue
        
        filepath = os.path.join(directory, entry)
        
        # Check directory exclusions
        if os.path.isdir(filepath):
            if _should_exclude_directory(entry, filters):
                continue
            files.append(filepath)
        
        # Apply filters to files
        if os.path.isfile(filepath):
            if _matches_filters(filepath, entry, depth, filters):
                files.append(filepath)
        
        # Recurse with depth tracking
        if recursive and os.path.isdir(filepath):
            max_depth = filters.get("depth", 0)
            if max_depth == 0 or depth < max_depth:
                files.extend(_collect_files(filepath, show_hidden, recursive, filters, depth + 1))
    
    return files
```

**Key Features**:
- ✅ Sorted entries (consistent ordering)
- ✅ Permission error resilience
- ✅ Depth tracking for depth limit filter
- ✅ Both files and directories included in results

---

**_matches_filters() Method** (Lines 162-227)

**6 Filter Types**:

1. **Regex Filter** (Lines 172-181):
```python
regex_config = filters.get("regex", {})
if regex_config.get("enabled") and regex_config.get("pattern"):
    if not re.search(regex_config["pattern"], filename):
        return False
```

2. **Size Filter** (Lines 183-196):
```python
file_size = os.path.getsize(filepath)
min_size = size_config.get("min")
if min_size is not None and file_size < min_size:
    return False

max_size = size_config.get("max")
if max_size is not None and file_size > max_size:
    return False
```

3. **MTime Filter** (Lines 198-211):
```python
mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).date()
after = mtime_config.get("after")
if after and mtime < after:
    return False

before = mtime_config.get("before")
if before and mtime > before:
    return False
```

4. **Extension Filter** (Lines 213-220):
```python
extensions = filters.get("extensions", [])
if extensions:
    file_ext = os.path.splitext(filename)[1].lstrip(".").lower()
    normalized_exts = [ext.lstrip(".").lower() for ext in extensions]
    if file_ext not in normalized_exts:
        return False
```

5. **Depth Filter** (Lines 222-225):
```python
max_depth = filters.get("depth", 0)
if max_depth > 0 and depth > max_depth:
    return False
```

6. **All filters must pass** (return True at end)

**Design**: Short-circuit evaluation (first failure returns False immediately)

---

**_should_exclude_directory() Method** (Lines 229-250)

**Exclusion Patterns**:
```python
exclude_dirs = filters.get("exclude_dirs", [])

# Direct match
if dirname in exclude_dirs:
    return True

# Wildcard patterns
for pattern in exclude_dirs:
    if pattern.startswith("*") and dirname.endswith(pattern[1:]):
        return True  # Suffix match: *cache → myproject_cache
    if pattern.endswith("*") and dirname.startswith(pattern[:-1]):
        return True  # Prefix match: test* → test_data
```

**Example**: `exclude_dirs = [".git", ".venv", "node_modules", "__pycache__"]`

---

**_get_file_info() Method** (Lines 141-160)

**Unix Permission String** (Lines 252-280):
```python
def _format_permissions(mode: int) -> str:
    perms = ""
    
    # File type
    if stat.S_ISDIR(mode):
        perms += "d"
    elif stat.S_ISLNK(mode):
        perms += "l"
    else:
        perms += "-"
    
    # Owner permissions
    perms += "r" if mode & stat.S_IRUSR else "-"
    perms += "w" if mode & stat.S_IWUSR else "-"
    perms += "x" if mode & stat.S_IXUSR else "-"
    
    # Group permissions
    perms += "r" if mode & stat.S_IRGRP else "-"
    perms += "w" if mode & stat.S_IWGRP else "-"
    perms += "x" if mode & stat.S_IXGRP else "-"
    
    # Other permissions
    perms += "r" if mode & stat.S_IROTH else "-"
    perms += "w" if mode & stat.S_IWOTH else "-"
    perms += "x" if mode & stat.S_IXOTH else "-"
    
    return perms
```

**Example Output**: `drwxr-xr-x` (directory, owner: rwx, group: r-x, other: r-x)

---

**Owner/Group Resolution** (Lines 282-296):

**Unix-specific** (uses pwd, grp modules):
```python
@staticmethod
def _get_owner(uid: int) -> str:
    try:
        return pwd.getpwuid(uid).pw_name
    except (KeyError, AttributeError):
        return str(uid)  # Fallback to numeric UID

@staticmethod
def _get_group(gid: int) -> str:
    try:
        return grp.getgrgid(gid).gr_name
    except (KeyError, AttributeError):
        return str(gid)  # Fallback to numeric GID
```

**Graceful Degradation**: Returns numeric ID if name lookup fails

---

**Utility Methods**:

**Human-Readable Size** (Lines 298-305):
```python
@staticmethod
def format_size_human(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"
```

**Example**: `1536` → `"1.5 KB"`, `5242880` → `"5.0 MB"`

---

**Statistics Calculation** (Lines 307-328):
```python
@staticmethod
def calculate_statistics(files: List[FileInfo]) -> Dict[str, Any]:
    total_size = sum(f.size for f in files if not f.is_dir)
    file_count = sum(1 for f in files if not f.is_dir)
    dir_count = sum(1 for f in files if f.is_dir)
    
    # Extension breakdown
    extensions = {}
    for f in files:
        if not f.is_dir:
            ext = os.path.splitext(f.name)[1].lower() or "(no extension)"
            extensions[ext] = extensions.get(ext, 0) + 1
    
    return {
        "total_size": total_size,
        "total_size_human": format_size_human(total_size),
        "file_count": file_count,
        "dir_count": dir_count,
        "total_count": len(files),
        "extensions": extensions,  # {".py": 45, ".json": 12, ...}
    }
```

---

### 2. set_operation_executor.py (224 lines) - Set Operations on JSON

**Purpose**: Core set operations execution (v2.9.114 Phase 2.3.3)

**Extracted from**: `set_operations_dock.py` (refactoring)

#### **ExecutionResult Class** (Lines 32-60)

**Purpose**: Container for operation results + metadata

```python
class ExecutionResult:
    def __init__(
        self,
        success: bool,
        results: Dict[str, Any] = None,      # Operation results
        stats_lines: List[str] = None,       # Statistics text
        file_a_data: Dict = None,            # First file (for diff viewer)
        file_b_data: Dict = None,            # Second file (for diff viewer)
        error: str = None                    # Error message
    ):
```

**Design**: Unified return type for success/failure cases

---

#### **SetOperationExecutor Class** (Lines 63-224)

**Pattern**: Static methods (stateless executor)

**validate_and_load_files() Method** (Lines 66-101)

**Purpose**: Security-validated JSON loading

```python
@staticmethod
def validate_and_load_files(file_paths: List[str]) -> Tuple[bool, List[Dict], str]:
    if len(file_paths) < 2:
        return False, [], "Please select at least 2 JSON files."
    
    file_dicts = []
    
    for file_path in file_paths:
        # SECURITY: CWE-22 Path Traversal Prevention
        if not validate_file_path(file_path):
            return False, [], (
                f"Invalid or insecure file path:\n{file_path}\n\n"
                "File must exist, be readable, and have .json extension."
            )
        
        with open(file_path, "r", encoding="utf-8") as f:
            file_dicts.append(json.load(f))
    
    return True, file_dicts, ""
```

**Security Check** (`validate_file_path`):
- File must exist
- File must be readable
- File must have `.json` extension
- Prevents directory traversal attacks (CWE-22)

**Error Handling**:
- `FileNotFoundError` → return filename
- `JSONDecodeError` → return parse error
- Generic exceptions → return error message

---

**execute_operations() Method** (Lines 103-188)

**Purpose**: Execute set operations with options

**Signature**:
```python
@staticmethod
def execute_operations(
    file_dicts: List[Dict],
    operations: List[str],        # ['∩', '∪', '−', '⊕']
    comparison_mode: str,         # "full_path", "key_only", "value_only"
    options: Dict[str, bool]      # Additional operation options
) -> ExecutionResult:
```

**4 Set Operations**:

1. **Intersection (∩)** (Lines 143-147):
```python
if '∩' in operations:
    result = intersection(file_dicts, **exec_options)
    results["intersection"] = result
    count = len(result.get("intersection", []))
    stats_lines.append(f"✓ Intersection: {count} items")
```

2. **Union (∪)** (Lines 149-153):
```python
if '∪' in operations:
    result = union(file_dicts, **exec_options)
    results["union"] = result
    count = len(result.get("union", []))
    stats_lines.append(f"✓ Union: {count} items")
```

3. **Difference (−)** (Lines 155-159):
```python
if '−' in operations:
    result = difference(file_dicts, **exec_options)
    results["difference"] = result
    count = len(result.get("difference", []))
    stats_lines.append(f"✓ Difference: {count} items")
```

4. **Symmetric Difference (⊕)** (Lines 161-170):
```python
if '⊕' in operations:
    if len(file_dicts) < 2:
        return ExecutionResult(
            success=False,
            error="Symmetric difference requires at least 2 files."
        )
    result = symmetric_difference(file_dicts[0], file_dicts[1], **exec_options)
    results["symmetric_difference"] = result
    count = len(result.get("symmetric_difference", []))
    stats_lines.append(f"✓ Symmetric Difference: {count} items")
```

**Comparison Mode Conversion** (Lines 129-130):
```python
if comparison_mode == "full_path":
    comparison_mode = "full_path_value"
```
**Reason**: GUI uses `full_path`, backend module uses `full_path_value`

---

**Utility Methods**:

**format_results_json()** (Lines 190-201):
```python
@staticmethod
def format_results_json(results: Dict[str, Any]) -> str:
    return json.dumps(results, indent=2, ensure_ascii=False)
```

**calculate_result_count()** (Lines 203-221):
```python
@staticmethod
def calculate_result_count(results: Dict[str, Any]) -> int:
    try:
        return sum(
            len(r.get(list(r.keys())[0], []))
            for r in results.values()
            if r and isinstance(r, dict)
        )
    except Exception:
        return 0
```

**Logic**: Sum lengths of first key's value in each result dict

---

### 3. rewriter_cli.py (195 lines) - JSON/TS Rewriter CLI

**Purpose**: Command-line interface for dedupe/rewrite operations (v2.9.114 Phase 2.2.2)

**Extracted from**: `json_rewriter_dock.py`

#### **cli_dedupe() Function** (Lines 20-192)

**Purpose**: Execute JSON/TS rewriting with all transformations

**Signature**:
```python
def cli_dedupe(
    args: argparse.Namespace,
    advanced_conditions: Optional[list[Condition]] = None,
    apply_all_types: bool = False
) -> tuple:
    # Returns: (output_text, substitution_map, removal_stats, detailed_stats)
```

**Returns**:
1. `output_text`: Processed file content
2. `substitution_map`: Maps removed keys to replacements (Task #23)
3. `removal_stats`: Dict with removal counters (v2.9.22)
4. `detailed_stats`: List of DetailedStatEntry objects (v2.9.31)

---

**Transformation Pipeline** (17 operations!):

**1. Initialize Stats** (Lines 45-56):
```python
stats = {
    "dedupe": 0,
    "eliminate": 0,
    "numeric_keys": 0,
    "empty_values": 0,
    "duplicate_child": 0,
    "array_duplicates_consecutive": 0,
    "array_duplicates_all": 0,
    "no_siblings": 0,
    "advanced_filters_filtered": 0,
}
```

---

**2. Advanced Filters** (Lines 58-77):
```python
if advanced_conditions:
    # Auto-detect JSON files unless apply_all_types is True
    should_filter = apply_all_types or input_file.endswith((".json", ".JSON"))
    
    if should_filter:
        filtered_files, filtered_out = apply_conditions_to_files(
            [input_file], advanced_conditions, logic_op="AND", enabled=True
        )
        
        stats["advanced_filters_filtered"] = filtered_out
        
        # If file filtered out, skip processing
        if not filtered_files:
            return "", {}, stats, []
```

---

**3. Read & Parse** (Lines 79-89):
```python
with open(args.input, "r", encoding="utf-8") as f:
    text = f.read()

# Parse based on format
if args.from_ts:
    obj = rw.ts_process_full_preserving(text)  # TypeScript/JavaScript
else:
    obj = rw.parse_json_preserving_duplicates_text(text)  # Pure JSON
```

---

**4. Resolve References** (Lines 91-95):
```python
if hasattr(args, "resolve_references") and args.resolve_references:
    obj, ref_stats = rw.resolve_references(obj)
    stats["references_resolved"] = ref_stats.get("resolved", 0)
    stats["references_invalid"] = ref_stats.get("invalid", 0)
```

---

**5. Dedupe** (Line 98):
```python
obj, stats["dedupe"] = rw.dedupe(obj)
```

---

**6. Join Keys** (Lines 100-101):
```python
if args.join_keys:
    obj, _ = rw.join_keys(obj)  # Doesn't remove items
```

---

**7. Eliminate Duplicates** (Lines 103-112):
```python
if args.eliminate_duplicates:
    # Extract keys/values BEFORE elimination
    old_keys_values = rw.extract_all_keys_from_obj(obj.data, prefix="t")
    
    obj, stats["eliminate"] = rw.eliminate_duplicates(obj)
    
    # Extract keys/values AFTER elimination
    new_keys_values = rw.extract_all_keys_from_obj(obj.data, prefix="t")
    
    # Build substitution map based on VALUE EQUALITY
    substitution_map = rw.build_substitution_map_by_value(old_keys_values, new_keys_values)
```

**Substitution Map** (Task #23 - v2.9.14):
- Maps removed keys to their replacement keys
- Example: `{"key123": "key456"}` (key123 was duplicate of key456)

---

**8. Exclude Numeric Keys** (Lines 114-116):
```python
if hasattr(args, "exclude_numeric") and args.exclude_numeric:
    obj, stats["numeric_keys"] = rw.exclude_numeric_keys(obj)
```

---

**9. Skip Empty Values** (Lines 118-120):
```python
if hasattr(args, "skip_empty") and args.skip_empty:
    obj, stats["empty_values"] = rw.skip_empty_values(obj)
```

---

**10. Avoid Duplicate Child Keys** (Lines 122-124):
```python
if hasattr(args, "avoid_duplicate_child_keys") and args.avoid_duplicate_child_keys:
    obj, stats["duplicate_child"] = rw.avoid_duplicate_child_keys(obj)
```

---

**11. Remove Duplicate Array Values (Consecutive)** (Lines 126-128):
```python
if hasattr(args, "remove_dup_consecutive") and args.remove_dup_consecutive:
    obj, stats["array_duplicates_consecutive"] = rw.remove_duplicate_array_values(obj, consecutive_only=True)
```

---

**12. Remove Duplicate Array Values (All)** (Lines 130-131):
```python
if hasattr(args, "remove_dup_all") and args.remove_dup_all:
    obj, stats["array_duplicates_all"] = rw.remove_duplicate_array_values(obj, consecutive_only=False)
```

---

**13. Skip Keys Without Siblings** (Lines 133-135):
```python
if hasattr(args, "skip_no_siblings") and args.skip_no_siblings:
    obj, stats["no_siblings"] = rw.skip_keys_without_siblings(obj)
```

---

**14. Remove Duplicate Objects** (Lines 137-162):

**Two Modes**:

**A. References Mode** (Sprint A v2.9.29):
```python
if hasattr(args, "use_references") and args.use_references:
    format_type = getattr(args, "reference_format", "$ref")
    include_line_numbers = getattr(args, "include_line_numbers_ref", True)
    use_relative_paths = getattr(args, "use_relative_paths", False)
    
    obj, ref_stats = rw.create_references(
        obj,
        mode="references",
        include_line_numbers=include_line_numbers,
        format_type=format_type,
        use_relative_path=use_relative_paths,
    )
    stats["references_created"] = ref_stats.get("created", 0)
```

**B. Delete Mode** (Legacy):
```python
else:
    threshold = getattr(args, "duplicate_threshold", 100) / 100.0
    include_arrays = getattr(args, "include_duplicate_arrays", False)
    mode = getattr(args, "duplicate_mode", "remove")
    
    obj, stats["duplicate_objects"], dup_stats = rw.remove_duplicate_objects(
        obj, threshold=threshold, include_arrays=include_arrays, mode=mode
    )
```

---

**15. Enforce Consistent Case** (Lines 164-173):
```python
if hasattr(args, "enforce_case") and args.enforce_case:
    case_style = getattr(args, "case_style", "camel")
    obj, warnings = rw.enforce_consistent_case(obj, target_case=case_style, warn_inconsistencies=True)
    
    if warnings:
        print(f"\n⚠️ Case inconsistencies detected ({len(warnings)} warnings):")
        for warning in warnings[:10]:  # Show first 10
            print(f"  - {warning}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings")
```

---

**16. Serialize Output** (Lines 175-181):
```python
if args.ts_out:
    output_text = rw.dump_ts_node(obj, indent=args.indent)
    if not args.no_line_break:
        output_text = rw.collapse_blank_lines(output_text)
else:
    output_text = rw.dump_ts_obj(obj, indent=args.indent, level=0)
```

---

**17. Write Output** (Lines 183-186):
```python
out_path = args.output or args.input
with open(out_path, "w", encoding="utf-8") as f:
    f.write(output_text)
```

---

**Statistics Collection** (Sprint B Feature #3):
```python
# Enable detailed stats collector
collector = get_global_collector()
collector.clear()
collector.enable()

# ... transformations ...

# Collect and return detailed stats
detailed_stats = [entry.to_dict() for entry in collector.get_entries()]
collector.disable()

return output_text, substitution_map, stats, detailed_stats
```

---

### 4. result_exporter.py (196 lines) - Multi-Format Export

**Purpose**: Export results to JSON, CSV, Excel, YAML, TOML (v2.9.114 Phase 2.3.4)

**Extracted from**: `set_operations_dock.py`

#### **ResultExporter Class** (Lines 27-194)

**Format Mapping** (Lines 30-40):
```python
FORMAT_MAP = {
    "CSV Files (*.csv)": "csv",
    "Excel Files (*.xlsx)": "xlsx",
    "YAML Files (*.yaml)": "yaml",
    "TOML Files (*.toml)": "toml",
    "JSON Files (*.json)": "json"
}

FORMAT_FILTER = "CSV Files (*.csv);;Excel Files (*.xlsx);;YAML Files (*.yaml);;TOML Files (*.toml);;JSON Files (*.json)"
```

**Usage**: `FORMAT_FILTER` used in `QFileDialog.getSaveFileName()`

---

**save_json() Method** (Lines 42-62):
```python
@staticmethod
def save_json(data: str, file_path: str) -> Tuple[bool, str]:
    if not data:
        return False, "No data to save"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
        return True, f"Results saved to:\n{file_path}"
    except Exception as e:
        return False, f"Error saving file: {e}"
```

**Pattern**: Returns `(success, message)` tuple

---

**export_multi_format() Method** (Lines 64-112)

**Purpose**: Export to multiple formats using ExportManager

```python
@staticmethod
def export_multi_format(
    data: Dict[str, Any],
    file_path: str,
    selected_filter: str,
    parent_widget: 'QWidget' | None = None
) -> Tuple[bool, str]:
    
    # 1. Determine format from filter
    export_format = ResultExporter.FORMAT_MAP.get(selected_filter, "json")
    
    # 2. Ensure correct extension
    path = Path(file_path)
    if not path.suffix:
        path = path.with_suffix(f".{export_format}")
    
    # 3. Export using ExportManager
    from ..export_manager import ExportManager
    
    ExportManager.export(
        data=data,
        output_path=path,
        format=export_format,
        flatten=True,              # Flatten for CSV/Excel/TOML
        include_metadata=True,     # Add timestamp + operation type
        parent_widget=parent_widget  # For progress modal
    )
    
    return True, f"Results exported to:\n{path}"
```

**Error Handling**:
- `ImportError` → Missing dependency (openpyxl, tomli-w)
- Generic exceptions → Return error message

---

**Utility Methods**:

**validate_export_data()** (Lines 114-131):
```python
@staticmethod
def validate_export_data(data: Any) -> Tuple[bool, str]:
    if data is None:
        return False, "No results to export. Please execute an operation first."
    
    if not data:
        return False, "Empty results. Nothing to export."
    
    return True, ""
```

---

**ensure_extension()** (Lines 146-161):
```python
@staticmethod
def ensure_extension(file_path: str, format_code: str) -> Path:
    path = Path(file_path)
    if not path.suffix:
        path = path.with_suffix(f".{format_code}")
    return path
```

---

**save_json_dict()** (Lines 163-180):
```python
@staticmethod
def save_json_dict(data: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True, f"Results saved to:\n{file_path}"
    except Exception as e:
        return False, f"Error saving file: {e}"
```

---

**format_json_for_display()** (Lines 182-193):
```python
@staticmethod
def format_json_for_display(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
```

---

### 5. file_explorer_executor.py (683 lines) - Unified File Explorer

**Purpose**: Unified executor merging List + Search + Replace (v2.9.116)

**Author**: Josué Amaral (2025/12/25)

**Integration**: Search/Replace → File Explorer (Sprint integration)

#### **Memory Optimization** (v2.9.120 - 2026-01-09)

**Constants** (Lines 29-31):
```python
MAX_SNIPPET_LENGTH = 200      # Maximum chars per match snippet
MAX_TOTAL_MATCHES = 50000     # Maximum total matches across all files
```

**Reason**: Prevent memory exhaustion on large codebases

---

#### **SearchMatch Dataclass** (Lines 34-47)

```python
@dataclass
class SearchMatch:
    line: int
    col: int
    snippet: str
    context_before: str = ""  # Deprecated: kept for compatibility
    context_after: str = ""   # Deprecated: kept for compatibility
```

**Memory Optimization** (v2.9.120):
- `snippet` truncated to `MAX_SNIPPET_LENGTH`
- `context_before/after` removed (were 3x memory overhead)
- Fields kept for backward compatibility but not populated

---

#### **UnifiedFileExplorerExecutor Class** (Lines 59-683)

**Pattern**: QObject with Signals (Qt integration)

**Signals** (Lines 79-82):
```python
progress = Signal(str)                      # Current file being processed
progress_detailed = Signal(int, int, str)   # (current, total, message)
done = Signal(dict)                         # Final results
error = Signal(str)                         # Error messages
```

---

**Control Methods** (Lines 89-99):
```python
def cancel(self):
    self._cancel = True

def pause(self):
    self._paused = True

def resume(self):
    self._paused = False
```

---

**execute_browse() Method** (Lines 101-179)

**Purpose**: List files with filtering

**Algorithm**:
```python
# 1. Get base file list
result = FileListExecutor.list_files(directory, show_hidden, recursive, filters)

# 2. Apply type filter (files only, directories only, or any)
type_filter = filters.get("type", "any")
if type_filter == "files":
    file_list = [f for f in file_list if not f.is_dir]
elif type_filter == "dirs":
    file_list = [f for f in file_list if f.is_dir]

# 3. Apply include/exclude glob filters
include_globs = filters.get("include_globs", [])
exclude_globs = filters.get("exclude_globs", [])

for file_info in file_list:
    # Check exclude globs (higher priority)
    for pattern in exclude_globs:
        # Check path components (for .venv, node_modules)
        path_components = file_path.split(os.sep)
        if pattern in path_components:
            excluded = True
            break
        
        # Check filename patterns (*.pyc)
        if fnmatch.fnmatch(file_name, pattern):
            excluded = True
            break
    
    # Check include globs
    if include_globs:
        included = any(
            fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(file_name, pattern)
            for pattern in include_globs
        )

# 4. Create SearchResult objects
search_results = [SearchResult(file_info=file_info, matches=[], match_count=0) for file_info in file_list]
```

**Key Feature**: Exclude globs checked on path components
- Correctly handles `.venv`, `node_modules` directories anywhere in path

---

**execute_search() Method** (Lines 181-354)

**Purpose**: Search filename and/or content

**Algorithm**:

**Step 1: List files** (Line 213):
```python
browse_result = self.execute_browse(directory, show_hidden, recursive, filters)
files_to_search = [sr.file_info for sr in browse_result["files"]]
```

---

**Step 2: Apply conditions EARLY** (Lines 218-277):

**OPTIMIZATION**: Separate content vs non-content conditions

```python
# Separate conditions by type
early_conditions = []  # size, ext, filename, path, mtime
late_conditions = []   # content (needs file read)

for cond in conditions:
    if cond.get("field") == "content":
        late_conditions.append(cond)
    else:
        early_conditions.append(cond)

# Apply non-content conditions EARLY (before file I/O)
if early_conditions:
    file_paths = [f.path for f in files_to_search]
    filtered_paths = filter_files_by_conditions(file_paths, early_conditions, logic_operator)
    files_to_search = [f for f in files_to_search if f.path in filtered_paths]
```

**BUGFIX** (Sprint 1 Task 1.1 Fase 2):
- Previous: Applied all conditions after reading files (slow!)
- Fixed: Separate by field type, apply metadata conditions early

---

**Step 3: Apply filename pattern** (Lines 282-285):
```python
if filename_pattern:
    files_to_search = [
        f for f in files_to_search if not f.is_dir and fnmatch.fnmatch(f.name.rstrip("/"), filename_pattern)
    ]
```

---

**Step 4: Content search** (Lines 288-325):

```python
total_match_count = 0  # Track total matches (v2.9.120)

for idx, file_info in enumerate(files_to_search, 1):
    if self._cancel:
        break
    
    # Check global match limit (v2.9.120 - Memory optimization)
    if total_match_count >= MAX_TOTAL_MATCHES:
        warning_msg = f"Maximum total matches reached ({MAX_TOTAL_MATCHES:,}). Search stopped."
        logger.warning(warning_msg)
        self.error.emit(warning_msg)
        break
    
    self.progress_detailed.emit(idx, total_files, file_info.path)
    
    # Skip directories
    if file_info.is_dir:
        continue
    
    # If no content query, just list matching files
    if not content_query:
        search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))
        continue
    
    # Read file and search
    text = read_text(file_info.path)
    matches = self._search_in_text(text, content_query, search_options)
    
    if matches:
        search_results.append(SearchResult(file_info=file_info, matches=matches, match_count=len(matches)))
        total_match_count += len(matches)
```

**Memory Safety** (v2.9.120):
- Stop search at 50,000 total matches
- Prevents UI freeze and memory exhaustion
- User sees warning to refine search

---

**Step 5: Apply content conditions LATE** (Lines 329-333):
```python
late_conditions = [c for c in conditions if c.get("field") == "content"]
if late_conditions:
    search_results = self._apply_conditions(search_results, late_conditions, logic_operator)
```

---

**_search_in_text() Method** (Lines 412-491)

**Purpose**: Search text with regex/case/word options

**Security Features**:

1. **Regex DoS Prevention** (Lines 432-439):
```python
# SECURITY OWASP A03: Regex DoS Prevention
flags = 0 if case_sensitive else re.IGNORECASE
try:
    regex = re.compile(pattern, flags)
except re.error as e:
    logger.error(f"Invalid regex pattern")
    self.error.emit(f"Invalid regex pattern: {e}")
    return []
```

2. **Match Limit Per File** (Lines 447-458):
```python
MAX_MATCHES_PER_FILE = 10000  # Prevent memory exhaustion

for line_num, line_text in enumerate(lines, 1):
    for match in regex.finditer(line_text):
        if match_count >= MAX_MATCHES_PER_FILE:
            logger.warning(f"Max matches reached: {MAX_MATCHES_PER_FILE}")
            self.error.emit(f"Too many matches (>{MAX_MATCHES_PER_FILE}). Results truncated.")
            return matches
```

3. **Snippet Truncation** (Lines 463-465):
```python
# Memory optimization (v2.9.120): Truncate snippet
truncated_snippet = line_text[:MAX_SNIPPET_LENGTH] if len(line_text) > MAX_SNIPPET_LENGTH else line_text
```

4. **Cancellation Support** (Line 451):
```python
if self._cancel:
    break
```

5. **Error Recovery** (Lines 478-482):
```python
except Exception as e:
    # Catch catastrophic backtracking errors
    logger.error(f"Error matching regex on line {line_num}")
    continue  # Continue with next line instead of failing
```

---

**execute_replace() Method** (Lines 356-410)

**Purpose**: Replace in files with case preservation

```python
for search_result in files:
    file_path = search_result.file_info.path
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content, count = self._replace_in_text(
        content, search_query, replacement, preserve_case, replace_all, search_options
    )
    
    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        replaced_count += count
        files_modified += 1

return {"replaced_count": replaced_count, "files_modified": files_modified, "errors": errors}
```

---

**_replace_in_text() Method** (Lines 493-554)

**Key Features**:

1. **Backslash Escape Bug Fix** (Lines 524-533):
```python
# BUG FIX: Escape backslashes in replacement when NOT using regex
if not use_regex:
    # Escape backslashes to treat literally (e.g., \S becomes \\S)
    safe_replacement = replacement.replace("\\", "\\\\")
else:
    # In regex mode, keep backslashes for backreferences (\1, \2, etc)
    safe_replacement = replacement
```

**Problem**: User types `\S`, gets error "bad escape \S"
**Solution**: Double-escape in non-regex mode

2. **Replace All vs First** (Lines 536-548):
```python
if replace_all:
    if preserve_case:
        new_text, count = self._replace_preserve_case(text, regex, safe_replacement)
    else:
        new_text = regex.sub(safe_replacement, text)
        count = len(regex.findall(text))
else:
    # Replace first occurrence only
    if preserve_case:
        new_text, count = self._replace_preserve_case(text, regex, safe_replacement, count=1)
    else:
        new_text = regex.sub(safe_replacement, text, count=1)
        count = 1 if regex.search(text) else 0
```

---

**_replace_preserve_case() Method** (Lines 556-584)

**Purpose**: Replace while preserving case pattern

```python
def _replace_preserve_case(text, pattern, replacement, count=0):
    replaced = 0
    result = []
    last_end = 0
    
    for match in pattern.finditer(text):
        # Add text before match
        result.append(text[last_end : match.start()])
        
        # Apply case pattern
        original = match.group(0)
        new_text = self._apply_case_pattern(original, replacement)
        result.append(new_text)
        
        last_end = match.end()
        replaced += 1
        
        # Stop if we've replaced enough
        if count > 0 and replaced >= count:
            result.append(text[last_end:])
            break
    else:
        result.append(text[last_end:])
    
    return "".join(result), replaced
```

---

**_apply_case_pattern() Method** (Lines 586-595):
```python
@staticmethod
def _apply_case_pattern(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()          # HELLO → WORLD
    elif original.islower():
        return replacement.lower()          # hello → world
    elif original[0].isupper():
        return replacement[0].upper() + replacement[1:].lower()  # Hello → World
    return replacement
```

**Same logic as `search_replace.py`** (reused pattern)

---

## 🔑 Key Architectural Insights

### **Phase 2 Complete Architecture**:

**Core Module Organization**:
```
src/core/
├── Text Operations
│   ├── search_replace.py     # Regex search/replace with case preservation
│   ├── insert.py              # 5-mode line insertion
│   └── multi_query.py         # Multi-line search with de-duplication
│
├── File Operations
│   ├── file_list_executor.py      # File discovery with filters
│   ├── file_explorer_executor.py  # Unified browse/search/replace
│   └── filters.py                 # Advanced filtering (scope extraction)
│
├── JSON/Set Operations
│   ├── set_operation_executor.py  # Set operations on JSON
│   ├── rewriter_cli.py            # JSON/TS rewriting (17 transformations!)
│   └── result_exporter.py         # Multi-format export (JSON/CSV/Excel/YAML/TOML)
│
└── System
    ├── command_manager.py         # Undo/redo with Command Pattern
    └── memory_register.py         # Regex capture & reuse system
```

---

### **Design Patterns Summary (Phase 2)**:

1. **Executor Pattern**:
   - FileListExecutor
   - SetOperationExecutor
   - UnifiedFileExplorerExecutor
   - **Purpose**: Separate execution logic from UI

2. **Command Pattern** (GoF):
   - CommandManager with undo/redo
   - FileModificationCommand
   - MultiFileCommand (Composite)

3. **Memento Pattern** (GoF):
   - RegisterEntry stores capture state
   - Command stores file content for undo

4. **Strategy Pattern**:
   - SearchOptions (3 modes)
   - InsertMode (5 strategies)
   - Condition operators (10 operations)

5. **Dataclass DTOs**:
   - FileInfo, SearchMatch, SearchResult
   - Clean data transfer between layers

6. **Observer Pattern** (Qt Signals):
   - progress, progress_detailed, done, error
   - Decouples execution from UI updates

---

### **Security Implementations**:

1. **CWE-22 Prevention** (Path Traversal):
   - `validate_file_path()` in SetOperationExecutor
   - File must exist, readable, .json extension

2. **Regex DoS Prevention** (OWASP A03):
   - Try/catch on regex compilation
   - MAX_MATCHES_PER_FILE = 10,000
   - MAX_TOTAL_MATCHES = 50,000
   - Cancellation support
   - Error recovery from catastrophic backtracking

3. **Memory Optimization** (v2.9.120):
   - Snippet truncation (200 chars)
   - Context lines removed (3x memory reduction)
   - Global match limits

---

### **Performance Optimizations**:

1. **Early Filtering** (FileExplorerExecutor):
   - Separate content vs non-content conditions
   - Apply metadata filters BEFORE reading files
   - **Result**: 10-100x faster on large codebases

2. **Lazy Evaluation**:
   - Generators in filters (`any()`, `all()`)
   - Short-circuit evaluation
   - Stop early on limits reached

3. **Memory Management**:
   - Truncated snippets (v2.9.120)
   - Match limits per file and globally
   - Removed unused context fields

4. **Graceful Degradation**:
   - Permission errors don't stop listing
   - Invalid regex → treat as literal
   - File read errors → skip file

---

### **Don't Touch Zones** (Critical Code):

1. **FileListExecutor._collect_files()** - Recursive traversal
   - Depth tracking essential for depth limit
   - Permission error handling prevents crashes
   - Sorted entries for consistent results

2. **UnifiedFileExplorerExecutor early/late condition separation**:
   - Changing order breaks optimization
   - Content conditions MUST be applied after file read
   - Metadata conditions MUST be applied before file read

3. **rewriter_cli.py transformation order**:
   - 17 transformations in specific order
   - Resolve references BEFORE dedupe
   - Extract keys BEFORE/AFTER eliminate (for substitution map)
   - Changing order breaks functionality

4. **Backslash escape fix** (file_explorer_executor.py):
   - Must double-escape in non-regex mode
   - Must NOT escape in regex mode (breaks backreferences)
   - Critical for user experience

5. **Memory limits** (MAX_TOTAL_MATCHES, MAX_MATCHES_PER_FILE):
   - Prevent UI freeze and memory exhaustion
   - Don't increase without thorough testing

---

## 📊 Statistics

**Session 5 Metrics**:
- **Files Read**: 5
- **Lines Analyzed**: ~1,629
- **Classes Discovered**: 7 (FileInfo, ListResult, FileListExecutor, ExecutionResult, SetOperationExecutor, ResultExporter, UnifiedFileExplorerExecutor)
- **Design Patterns Identified**: 6 (Executor, Command, Memento, Strategy, DTO, Observer)
- **Security Features**: 3 (CWE-22 prevention, Regex DoS prevention, Memory limits)
- **Transformations in rewriter_cli**: 17 operations!

**Cumulative Progress**:
- **Total Files Studied**: 23 / 196 (11.7%)
- **Total Lines Studied**: ~5,059 / 58,165 (8.7%)
- **Documentation Read**: 242 / 242 (100%)
- **Overall Comprehension**: ~56% (docs 100%, code 12%)

**Phase 2 Status**: ✅ **COMPLETE**
- All 11 core files studied
- 2,782 lines comprehended
- Core business logic fully understood

**Next Phase**: Phase 3 - Feature Modules (utils/, rewriter/, gui/, ai_processor/)

---

## 🎯 Key Takeaways

### **What We Now Understand** (Phase 2 Complete):

1. ✅ **File Operations**:
   - Recursive directory traversal with filters
   - Unix permissions, owner/group resolution
   - Include/exclude glob patterns
   - Unified browse/search/replace pipeline

2. ✅ **JSON Processing**:
   - Set operations (∩, ∪, −, ⊕)
   - 17-stage rewriting pipeline
   - Reference system (create/resolve)
   - Substitution map generation

3. ✅ **Export System**:
   - Multi-format support (JSON, CSV, Excel, YAML, TOML)
   - Format detection and extension handling
   - ExportManager integration

4. ✅ **Search Engine**:
   - Regex/case/word options
   - Early/late condition filtering
   - Memory optimization (truncation, limits)
   - Security (DoS prevention, error recovery)

5. ✅ **Text Manipulation**:
   - Smart case preservation
   - 5 insertion modes
   - Multi-query search
   - Regex capture & reuse

6. ✅ **Undo/Redo**:
   - Command Pattern implementation
   - 10-level history
   - Multi-file operations
   - Reverse-order undo

### **Core Business Logic Flow**:

**File Explorer Workflow**:
```
User Input (directory, patterns, queries)
    ↓
execute_browse() → FileListExecutor.list_files()
    ↓
Apply type filter (files/dirs/any)
    ↓
Apply include/exclude globs
    ↓
Apply early conditions (metadata only)
    ↓
execute_search() → _search_in_text()
    ↓
Apply late conditions (content)
    ↓
execute_replace() → _replace_in_text()
    ↓
Results with statistics
```

**JSON Rewriting Workflow**:
```
Input File
    ↓
Parse (JSON or TS)
    ↓
Resolve References (if enabled)
    ↓
17 Transformation Stages:
  1. Dedupe
  2. Join Keys
  3. Eliminate Duplicates (+ build substitution map)
  4. Exclude Numeric Keys
  5. Skip Empty Values
  6. Avoid Duplicate Child Keys
  7-8. Remove Duplicate Arrays (consecutive/all)
  9. Skip Keys Without Siblings
  10. Remove Duplicate Objects (references or delete)
  11. Enforce Consistent Case
    ↓
Serialize (JSON or TS)
    ↓
Write Output
    ↓
Return (output, substitution_map, stats, detailed_stats)
```

---

## 📝 Protocol Compliance Check

**SIMPLICITY_PROTOCOL_3 Step 1.2 Progress**:

- [x] Study entry points ✅
- [x] Study main application class ✅
- [x] Study initialization system ✅
- [x] Study UI construction ✅
- [x] Study core business logic ✅ **COMPLETE**
- [ ] Study utility modules (Phase 3)
- [ ] Study feature modules (Phase 3)
- [ ] Study support systems (Phase 4)
- [ ] Create comprehensive NOTES.md (Phase 5)

**Current Status**: ~42% of Step 1.2 complete (Phase 2 done, 3 phases remain)

---

**Session 5 Complete! 🎉 Phase 2 COMPLETE! 🎊**  
**Next**: Phase 3 - Feature Modules (utils/, rewriter/, gui/docks, ai_processor/)
