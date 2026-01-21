# Code Study Session 8: JSON Search System
**Programmer**: COM4  
**Date**: 2026-01-21  
**Duration**: 45 minutes  
**Module**: `src/json_search/`  
**Files Studied**: 5 files, 792 LOC  

---

## Executive Summary

The **json_search** module provides a lightweight indexing and search system for JSON/TypeScript/JSX files, enabling fast key/value lookups across project files. It flattens nested JSON to dot-notation, extracts TypeScript object literals, and supports flexible query modes with regex, case sensitivity, and whole-word matching.

**Key Architecture**:
- **3-stage pipeline**: Scan → Parse → Flatten → Index → Query
- **2 file types**: JSON (native) + TS/TSX (via regex extraction)
- **3 query modes**: Key search, Value search, Both (OR combination)
- **4 search options**: Case sensitivity, Whole word, Regex, Composite queries

**Business Value**:
- Fast file-based search without external database
- TypeScript i18n key discovery
- Multi-file JSON comparison
- Development-time search tool

---

## Files Analyzed

### 1. `__init__.py` (46 LOC)
**Purpose**: Module interface and exports  
**Role**: Public API definition  
**Complexity**: Low (pure exports)

**Public API**:
```python
# Flattening
from .flattener import flatten_object

# TS/JS Extraction
from .ts_extractor import extract_top_level_objects_from_ts, guess_line_number

# Indexing
from .indexer import ProjectIndexer, FlatIndex

# Querying
from .query_parser import (
    parse_composite_query,
    resolve_query,
    match_with_options,
    resolve_query_by_value,
    resolve_query_with_mode
)
```

**Module Description** (line 1-22):
> "Provides functionality to search for keys and values in JSON/TS/TSX files"

**Features**:
- Index JSON/TS/TSX files from directories or single files
- Flatten nested JSON structures to dot-path notation
- Search with case sensitivity, whole word, and regex support
- Extract TypeScript object literals with json5 parsing
- Line number detection for search results

---

### 2. `flattener.py` (50 LOC)
**Purpose**: Convert nested JSON to flat dot-path notation  
**Role**: Data transformation utility  
**Complexity**: Low (simple recursion)

**Core Algorithm**:
```python
def flatten_object(obj: Any, prefix: str = "", out: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Flatten nested dict/list into dot-paths.
    
    Example:
        Input:  {"a": {"b": {"c": 1}}}
        Output: {"a.b.c": 1}
    """
    if out is None:
        out = {}
    
    if isinstance(obj, dict):
        # Recurse into dict
        for k, v in obj.items():
            next_key = f"{prefix}.{k}" if prefix else k
            flatten_object(v, next_key, out)
            
    elif isinstance(obj, list):
        # Flatten list with array indices
        for i, item in enumerate(obj):
            next_key = f"{prefix}[{i}]" if prefix else f"[{i}]"
            flatten_object(item, next_key, out)
            
    else:
        # Primitive value - store at current path
        out[prefix] = obj
    
    return out
```

**Array Indexing**:
```python
# Input:
{"users": [{"id": 1}, {"id": 2}]}

# Output:
{
    "users[0].id": 1,
    "users[1].id": 2
}
```

**Design Patterns**:
1. **Recursive Descent**: Traverses nested structures
2. **Accumulator Pattern**: `out` dict collects results
3. **Visitor Pattern**: Visits each node in tree
4. **Pure Function**: Immutable transformation

**Time Complexity**: O(n × d) where n=nodes, d=depth  
**Space Complexity**: O(n) for flat dict

**Edge Cases**:
```python
# Empty dict/list
flatten_object({})           # {}
flatten_object([])           # {}

# Nested arrays
flatten_object([[1, 2], 3])  # {"[0][0]": 1, "[0][1]": 2, "[1]": 3}

# Mixed types
flatten_object({"a": None, "b": True})  # {"a": None, "b": True}
```

---

### 3. `indexer.py` (155 LOC)
**Purpose**: Build searchable index from project files  
**Role**: Indexing engine  
**Complexity**: Medium (file I/O + parsing + error handling)

**Core Class**:
```python
class ProjectIndexer:
    """
    Indexes JSON/TS/TSX files from target path.
    
    Attributes:
        target_path: Path to file or directory
        target_is_file: Whether target_path is a single file
        flat: Flattened index mapping dot-paths to metadata
        files: List of indexed file paths
    """
    
    def __init__(self, target_path: str, target_is_file: bool)
    def rebuild(self) -> None  # Build/rebuild index
    def get_flat(self) -> FlatIndex  # Get flattened index
    def root_display(self) -> str  # Get display string
```

**FlatIndex Type**:
```python
FlatIndex = Dict[str, List[Dict[str, Any]]]

# Structure:
{
    "pages.home.title": [
        {"file": "en.json", "value": "Home", "line": 5},
        {"file": "pt.json", "value": "Início", "line": 5}
    ],
    "pages.about.title": [
        {"file": "en.json", "value": "About", "line": 10}
    ]
}
```

**rebuild() Algorithm**:
```python
def rebuild(self) -> None:
    # Step 1: Find files
    if self.target_is_file:
        files = [self.target_path]
    else:
        # Glob patterns
        patterns = ["**/*.json", "**/*.ts", "**/*.tsx"]
        
        # Ignore directories
        ignore_dirs = {
            "/node_modules/",
            "/.next/",
            "/dist/",
            "/build/",
            "/.git/"
        }
        
        files = []
        for pat in patterns:
            files.extend(glob.glob(os.path.join(target_path, pat), recursive=True))
        
        # Filter ignored
        files = [f for f in files if not any(token in f for token in ignore_dirs)]
    
    # Step 2: Parse each file
    new_flat: FlatIndex = {}
    
    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        text = open(fpath).read()
        
        if ext == ".json":
            # Parse JSON
            obj = json.loads(text)
            flat = flatten_object(obj)
            for path, value in flat.items():
                lineno = guess_line_number(text, path)
                new_flat.setdefault(path, []).append({
                    "file": fpath,
                    "value": value,
                    "line": lineno
                })
        
        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            # Extract TS/JS objects
            objects = extract_top_level_objects_from_ts(text)
            for obj in objects:
                flat = flatten_object(obj)
                for path, value in flat.items():
                    new_flat.setdefault(path, []).append({
                        "file": fpath,
                        "value": value,
                        "line": guess_line_number(text, path)
                    })
    
    self.flat = new_flat
```

**Design Patterns**:
1. **Builder Pattern**: Incrementally constructs index
2. **Strategy Pattern**: Different parsing per file type
3. **Fail-safe**: Continues on file errors (skip invalid files)
4. **Template Method**: Fixed rebuild structure, delegated parsing
5. **Accumulator Pattern**: Builds flat dict incrementally

**Ignore Patterns**:
- `node_modules/` - NPM dependencies
- `.next/` - Next.js build
- `dist/`, `build/` - Build outputs
- `.git/` - Git metadata

**Rationale**: Avoid indexing generated files (performance + noise reduction)

**Performance Characteristics**:
- **Time**: O(f × s) where f=files, s=avg file size
- **Space**: O(k) where k=total keys across all files
- **Bottleneck**: File I/O (not cached)

**Key Insight - Multi-file Support**:
```python
# Same key in multiple files → multiple entries
{
    "pages.home.title": [
        {"file": "en.json", "value": "Home", "line": 5},   # English
        {"file": "es.json", "value": "Inicio", "line": 5}, # Spanish
        {"file": "fr.json", "value": "Accueil", "line": 5} # French
    ]
}
```

**Use Case**: i18n key discovery across translation files

---

### 4. `query_parser.py` (300 LOC)
**Purpose**: Parse and execute search queries  
**Role**: Query engine  
**Complexity**: High (multiple search modes + options)

**Core Functions** (5):

#### 1. `parse_composite_query()`:
```python
def parse_composite_query(raw: str) -> Tuple[str, Optional[str]]:
    """
    Parse composite query: "base.path,sub.path"
    
    The left side is the base path; right side is appended subpath.
    Leading 't.' or 't' is stripped (common convention).
    
    Examples:
        >>> parse_composite_query("t.pages.home,title")
        ("pages.home", "title")
        
        >>> parse_composite_query("auth.login")
        ("auth.login", None)
    """
    q = raw.strip()
    idx = q.find(",")
    
    if idx >= 0:
        left, right = q[:idx].strip(), q[idx + 1:].strip()
    else:
        left, right = q, None
    
    # Remove 't.' or 't' prefix
    if left.startswith("t."):
        left = left[2:]
    elif left == "t":
        left = ""
    
    base_path = left
    sub_path = right if right else None
    
    return base_path, sub_path
```

**Why Composite Queries?**
```python
# Simple query:
"pages.home.title"  # Search for exact key

# Composite query:
"pages.home,title"  # Base: "pages.home", Sub: "title"
# Result: "pages.home.title"

# Use case: Autocomplete/suggestions
# User types "pages.home" → show all sub-keys
# User adds ",title" → narrow to pages.home.title
```

**'t' Prefix Convention**:
```python
# Common in i18n systems: t.pages.home → t('pages.home')
"t.pages.home" → "pages.home"  # Strip prefix for search
"t" → ""  # Root level search
```

#### 2. `match_with_options()`:
```python
def match_with_options(candidate: str, needle: str,
                       case_sensitive: bool, whole_word: bool, regex: bool) -> bool:
    """
    Apply case/whole-word/regex rules to match a candidate path.
    """
    if regex:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.search(needle, candidate, flags) is not None
        except re.error:
            return False
    
    hay = candidate if case_sensitive else candidate.lower()
    ndl = needle if case_sensitive else needle.lower()
    
    if whole_word:
        # Compare token-by-token (dot-separated)
        tokens = hay.split(".")
        return ndl in tokens
    
    return ndl in hay
```

**Match Examples**:
```python
# Case sensitive
match_with_options("pages.Home", "home", case_sensitive=True, ...)   # False
match_with_options("pages.Home", "Home", case_sensitive=True, ...)   # True

# Whole word
match_with_options("pages.home.title", "home", whole_word=True, ...) # True
match_with_options("pages.homepage", "home", whole_word=True, ...)   # False

# Regex
match_with_options("pages.home", r"pages\.(home|about)", regex=True, ...) # True
```

#### 3. `resolve_query()`:
```python
def resolve_query(flat: FlatIndex, raw_query: str,
                  case_sensitive: bool, whole_word: bool, regex: bool):
    """
    Resolve query against flattened index.
    
    Returns:
        Tuple of (exact_matches, suggestions)
    """
    base_path, sub_path = parse_composite_query(raw_query)
    needle = f"{base_path}.{sub_path}" if sub_path else base_path
    
    exact: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []
    
    # Scan entire index
    for key, metas in flat.items():
        matched = match_with_options(key, needle, case_sensitive, whole_word, regex)
        
        if matched:
            # Exact match - include all occurrences
            for meta in metas:
                exact.append({
                    "path": key,
                    "file": meta["file"],
                    "value": meta["value"],
                    "line": meta.get("line")
                })
        else:
            # Suggestions: keys that start with base_path
            if base_path and key.startswith(base_path):
                for meta in metas:
                    suggestions.append({
                        "path": key,
                        "file": meta["file"],
                        "line": meta.get("line")
                    })
    
    # Deduplicate and limit
    exact = _dedup(exact)[:200]
    suggestions = _dedup(suggestions)[:200]
    
    return exact, suggestions
```

**Exact vs Suggestions**:
```python
# Query: "pages.home"
flat = {
    "pages.home.title": [...],       # Exact match
    "pages.home.subtitle": [...],    # Exact match
    "pages.home.hero.title": [...],  # Suggestion (starts with base)
    "pages.about.title": [...]       # No match
}
```

#### 4. `resolve_query_by_value()`:
```python
def resolve_query_by_value(flat: FlatIndex, search_value: str,
                            case_sensitive: bool, regex: bool) -> List[Dict[str, Any]]:
    """
    Search for entries whose values match the search pattern.
    """
    results: List[Dict[str, Any]] = []
    
    for key_path, metadata_list in flat.items():
        for metadata in metadata_list:
            value = metadata.get("value")
            value_str = "None" if value is None else str(value)
            
            # Apply matching rules
            if regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                matched = re.search(search_value, value_str, flags) is not None
            else:
                # Substring match
                if case_sensitive:
                    matched = search_value in value_str
                else:
                    matched = search_value.lower() in value_str.lower()
            
            if matched:
                results.append({
                    "key": key_path,
                    "value": value,
                    "file": metadata["file"],
                    "line": metadata.get("line"),
                    "match_type": "value"
                })
    
    return results[:200]
```

**Value Search Example**:
```python
# Find all keys with value containing "Welcome"
flat = {
    "pages.home.title": [{"file": "en.json", "value": "Welcome Home", ...}],
    "pages.login.message": [{"file": "en.json", "value": "Welcome back", ...}],
    "pages.about.title": [{"file": "en.json", "value": "About Us", ...}]
}

resolve_query_by_value(flat, "Welcome", case_sensitive=False, regex=False)
# Returns: [
#     {"key": "pages.home.title", "value": "Welcome Home", ...},
#     {"key": "pages.login.message", "value": "Welcome back", ...}
# ]
```

#### 5. `resolve_query_with_mode()`:
```python
def resolve_query_with_mode(flat: FlatIndex, search_key: str, search_value: str,
                             search_mode: str, case_sensitive: bool, regex: bool):
    """
    Resolve query based on search mode (key, value, or both).
    """
    results = []
    
    if search_mode == "key":
        # Search keys only
        exact, _ = resolve_query(flat, search_key, case_sensitive, False, regex)
        for match in exact:
            results.append({...match_type": "key"})
    
    elif search_mode == "value":
        # Search values only
        value_results = resolve_query_by_value(flat, search_value, case_sensitive, regex)
        results.extend(value_results)
    
    else:  # "both"
        # Search keys OR values
        if search_key:
            key_results = resolve_query(...)
            results.extend(key_results)
        if search_value:
            value_results = resolve_query_by_value(...)
            results.extend(value_results)
    
    # Deduplicate
    return _dedup(results)[:200]
```

**Design Patterns**:
1. **Strategy Pattern**: 3 search modes (key, value, both)
2. **Query Object**: Encapsulates search criteria
3. **Builder Pattern**: Composite query construction
4. **Filter Pattern**: Result filtering and deduplication
5. **Limit Pattern**: 200-result cap prevents memory issues

**Performance**:
- **resolve_query()**: O(k) where k=keys in index
- **resolve_query_by_value()**: O(k × v) where v=avg value length
- **Deduplication**: O(r log r) where r=results (set operations)

**Result Limit Rationale**:
```python
results[:200]  # Cap at 200 results

# Why 200?
# - UI can't display 1000s of results effectively
# - Memory-efficient (prevents large lists)
# - Forces users to refine queries
# - Faster rendering
```

---

### 5. `ts_extractor.py` (241 LOC)
**Purpose**: Extract object literals from TypeScript/JavaScript  
**Role**: TS/JS parser  
**Complexity**: High (regex + brace matching + string handling)

**Supported Patterns**:
```typescript
// Pattern 1: export const with optional type
export const translations = { ... }
export const config: Config = { ... }

// Pattern 2: export default
export default { ... }
```

**Core Algorithm - Brace Matching**:
```python
def _find_matching_closing_brace(s: str, open_index: int) -> int:
    """
    Find matching '}' for '{' at open_index.
    Respects string literals and escape sequences.
    """
    depth = 0
    in_str: Optional[str] = None
    esc = False
    
    i = open_index
    while i < len(s):
        ch = s[i]
        
        # Handle string escapes
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            i += 1
            continue
        
        # Detect string start
        if ch in ("'", '"', "`"):
            in_str = ch
            i += 1
            continue
        
        # Track brace depth
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        
        i += 1
    
    return -1
```

**Why Brace Matching is Hard**:
```typescript
// Strings can contain braces:
const obj = {
    message: "Hello {name}",  // Not a nested object!
    template: `Value: ${value}`,  // Template literal
    escaped: "Quote: \"test\""  // Escape sequence
}
```

**Parsing Strategy - json5 + Fallback**:
```python
def _parse_js_like_object(obj_literal: str) -> Optional[Dict[str, Any]]:
    """
    Parse JavaScript-like object literal.
    
    Tries json5 first (handles single quotes, trailing commas, comments).
    Falls back to naive normalization for standard JSON parsing.
    """
    # Try json5 (best option)
    if HAS_JSON5:
        try:
            return json5.loads(obj_literal)
        except Exception:
            pass
    
    # Fallback: normalize to JSON
    s = obj_literal
    # 1. Convert template literals
    s = re.sub(r"`([^`$]*)`", lambda m: f'"{m.group(1)}"', s)
    # 2. Remove comments
    s = COMMENT_BLOCK_RE.sub("", s)
    s = COMMENT_LINE_RE.sub("", s)
    # 3. Quote unquoted keys
    s = UNQUOTED_KEY_RE.sub(lambda m: f'{m.group("prefix")}"{m.group("key")}":', s)
    # 4. Convert single quotes to double quotes
    s = s.replace("'", '"')
    # 5. Remove trailing commas
    s = TRAILING_COMMA_RE.sub(r"\1", s)
    # 6. Parse as JSON
    return json.loads(s)
```

**Normalization Steps**:
```typescript
// Original TypeScript:
export const config = {
    apiKey: 'abc123',  // Comment
    timeout: 5000,     // Trailing comma
    message: `Hello`   // Template literal
}

// Step 1: Convert template literals
{ apiKey: 'abc123', timeout: 5000, message: "Hello" }

// Step 2: Remove comments
{ apiKey: 'abc123', timeout: 5000, message: "Hello" }

// Step 3: Quote keys
{ "apiKey": 'abc123', "timeout": 5000, "message": "Hello" }

// Step 4: Convert single quotes
{ "apiKey": "abc123", "timeout": 5000, "message": "Hello" }

// Step 5: Remove trailing comma (none in this case)

// Step 6: Valid JSON! Can parse with json.loads()
```

**Line Number Guessing**:
```python
def guess_line_number(text: str, dot_path: str) -> Optional[int]:
    """
    Guess line number where a dot-path key appears.
    
    Strategy:
    1. Look for exact "key:" pattern at line start
    2. Fallback to any word-bounded occurrence
    """
    last_segment = dot_path.split(".")[-1].replace("[", "").replace("]", "")
    
    # Try exact pattern: "key": or key: at line start
    pattern1 = re.compile(r'(?m)^\s*(?:"|\')?%s(?:"|\')?\s*:' % re.escape(last_segment))
    match = pattern1.search(text)
    if match:
        return text.count("\n", 0, match.start()) + 1
    
    # Fallback: any word-bounded occurrence
    pattern2 = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(last_segment))
    match2 = pattern2.search(text)
    if match2:
        return text.count("\n", 0, match2.start()) + 1
    
    return None
```

**Why Guessing?**
- We flatten objects **after** parsing (lose line info)
- AST parsers would give exact positions but are heavy dependencies
- Guessing is "good enough" for search use case

**Design Patterns**:
1. **Regex Strategy**: Different patterns for different exports
2. **State Machine**: Brace matching with quote state tracking
3. **Graceful Degradation**: json5 → fallback → None
4. **Normalization**: Convert JS → JSON via transformations
5. **Heuristic**: Line number guessing (not exact)

**Dependencies**:
```python
try:
    import json5  # Optional
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False
```

**Why Optional?**
- json5 is external dependency (adds install burden)
- Fallback works for most cases
- Graceful degradation preserves functionality

**Limitations**:
```typescript
// Not supported:
const obj = {
    computed: [key]: "value",  // Computed properties
    method() { return 42; },    // Methods
    ...spread,                  // Spread operator
    [Symbol.key]: "value"       // Symbols
}

// Template literal interpolation:
const obj = { msg: `Hello ${name}` }  // Extracted as "Hello ${name}" (literal)
```

---

## Design Patterns Summary

### Identified Patterns (12 total)

1. **Recursive Descent** (flattener.py)
   - Traverses nested structures depth-first
   - Accumulates results in dict

2. **Accumulator Pattern** (flattener.py, indexer.py)
   - `out` dict collects flattened paths
   - `new_flat` dict builds index incrementally

3. **Visitor Pattern** (flattener.py)
   - Visits each node in JSON tree
   - Applies transformation (flatten)

4. **Builder Pattern** (indexer.py, query_parser.py)
   - Incremental index construction
   - Composite query construction

5. **Strategy Pattern** (indexer.py, query_parser.py)
   - Different parsing per file type (.json vs .ts)
   - 3 search modes (key, value, both)
   - Match options (case, whole word, regex)

6. **Template Method** (indexer.py)
   - Fixed rebuild() structure
   - Delegated parsing logic

7. **Fail-safe Pattern** (indexer.py, ts_extractor.py)
   - Continues on file errors
   - Skips invalid JSON/TS

8. **Query Object** (query_parser.py)
   - Encapsulates search criteria
   - Composite query structure

9. **Filter Pattern** (query_parser.py)
   - Result filtering
   - Deduplication
   - 200-result limit

10. **State Machine** (ts_extractor.py)
    - Brace matching with quote state
    - `in_str`, `esc`, `depth` tracking

11. **Graceful Degradation** (ts_extractor.py)
    - json5 → fallback → None
    - Optional dependency handling

12. **Heuristic Pattern** (ts_extractor.py)
    - Line number guessing
    - Not exact, but useful

---

## Architecture Analysis

### Module Dependencies
```
json_search/__init__.py (Interface)
    ├── flattener.py (Utility)
    ├── indexer.py (Engine)
    │   ├── flattener.py
    │   └── ts_extractor.py
    ├── query_parser.py (Engine)
    └── ts_extractor.py (Parser)
```

### Data Flow
```
Files (JSON/TS/TSX)
    ↓
ProjectIndexer.rebuild()
    ↓
    1. Glob files (skip node_modules, dist, etc.)
    2. For each file:
        a. Read content
        b. Parse (JSON or TS extraction)
        c. Flatten nested structure
        d. Extract line numbers
        e. Add to FlatIndex
    ↓
FlatIndex: {"path": [{"file", "value", "line"}, ...]}
    ↓
Query Functions
    ↓
    resolve_query() → (exact_matches, suggestions)
    resolve_query_by_value() → value_matches
    resolve_query_with_mode() → unified_results
    ↓
Results: [{"key", "value", "file", "line", "match_type"}, ...]
```

### Integration with Clarify

**Used by**: File Explorer Dock (`file_explorer_dock.py`)

**Workflow**:
1. User opens File Explorer
2. Selects directory or file
3. ProjectIndexer.rebuild() scans files
4. User enters search query
5. resolve_query_with_mode() finds matches
6. Results displayed in table/tree

---

## Key Insights

### 1. Why Flatten JSON?
**Problem**: Nested JSON is hard to search
```python
# Nested structure:
{"pages": {"home": {"title": "Welcome"}}}

# How to search for "title"? Need recursive traversal every time
```

**Solution**: Flatten to dot-notation
```python
# Flattened:
{"pages.home.title": "Welcome"}

# Search: Simple dict lookup or string matching
```

**Trade-off**:
- **Pros**: Fast search (O(1) lookup), simple matching
- **Cons**: Preprocessing cost, extra memory

### 2. Why TypeScript Extraction?
**Problem**: Many projects use TS/JS for i18n keys
```typescript
// locales/en.ts
export const translations = {
    pages: {
        home: {
            title: "Welcome"
        }
    }
}
```

**Solution**: Extract object literals with regex + parsing
- No AST parser (heavy dependency)
- No TypeScript compiler (slow)
- Regex + brace matching (lightweight, fast enough)

**Trade-off**:
- **Pros**: No heavy dependencies, fast for simple cases
- **Cons**: Doesn't support all TS features (computed properties, methods)

### 3. Why 200-Result Limit?
```python
results[:200]  # Cap at 200 results
```

**Rationale**:
1. **UI Performance**: Can't display 1000s of results
2. **Memory**: Prevents large lists consuming RAM
3. **User Experience**: Forces query refinement
4. **Network**: If results sent to GUI, limit payload

**Alternative**: Pagination (not implemented)

### 4. Why Deduplication?
**Problem**: Same key can match multiple times
```python
# Query: "title" in key search mode
flat = {
    "pages.home.title": [
        {"file": "en.json", "value": "Home"},
        {"file": "es.json", "value": "Inicio"}
    ]
}

# Without dedup: 2 results for same key
# With dedup: 1 result per unique (key, file, line)
```

**Strategy**:
```python
signature = (result["key"], result["file"], result["line"])
if signature not in seen:
    seen.add(signature)
    deduped.append(result)
```

### 5. Why Composite Queries?
**Use Case**: Autocomplete/suggestions
```python
# User types: "pages.home"
# System shows: All sub-keys (title, subtitle, hero.title)

# User narrows: "pages.home,title"
# System shows: Exact match (pages.home.title)
```

**Query Syntax**:
```
"base.path,sub.path" → "base.path.sub.path"
```

**Benefits**:
- Supports autocomplete UX
- Separates base context from search term
- Common in i18n tools (ICU, react-intl)

### 6. Why Ignore node_modules?
```python
ignore_dirs = {"/node_modules/", "/.next/", "/dist/", "/build/", "/.git/"}
```

**Rationale**:
- **Performance**: node_modules can have 10,000+ files
- **Relevance**: Dependencies shouldn't pollute search results
- **Speed**: Reduces indexing time from minutes to seconds

**Example**:
- Project: 500 source files, 50,000 dependency files
- Without filter: 50,500 files indexed (~2 min)
- With filter: 500 files indexed (~2 sec)

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| `flatten_object()` | O(n × d) | n=nodes, d=depth |
| `rebuild()` | O(f × s) | f=files, s=avg file size |
| `resolve_query()` | O(k) | k=keys in index |
| `resolve_query_by_value()` | O(k × v) | v=avg value length |
| `match_with_options()` | O(n) | n=candidate length (regex worst case) |
| Brace matching | O(n) | n=object literal length |

### Space Complexity

| Structure | Space | Notes |
|-----------|-------|-------|
| Flattened dict | O(n) | n=total keys |
| FlatIndex | O(k × m) | k=unique keys, m=avg occurrences per key |
| Results | O(r) | r=result count (capped at 200) |

### Benchmark Estimates

**Small Project** (10 files, 500 KB):
- Indexing: ~0.5 seconds
- Query: ~50ms

**Medium Project** (100 files, 5 MB):
- Indexing: ~2 seconds
- Query: ~100ms

**Large Project** (1000 files, 50 MB, without node_modules):
- Indexing: ~10 seconds
- Query: ~200ms

**Bottlenecks**:
1. **File I/O**: Disk reads dominate indexing time
2. **JSON Parsing**: `json.loads()` is CPU-bound
3. **TS Extraction**: Regex + brace matching slower than JSON parsing
4. **Value Search**: O(k × v) can be slow for large indexes

---

## Integration with Phase 4 Implementation

### How File Explorer Uses json_search

**Current** (from file_explorer_dock.py study):
```python
# File Explorer has search logic but it's not using json_search module
# ACTION_PLAN_PHASE4_FILE_EXPLORER.md proposes:
# "Unified search pipeline using json_search module"
```

**Proposed Integration**:
```python
from json_search import ProjectIndexer, resolve_query_with_mode

class FileExplorerDock:
    def __init__(self):
        self.indexer = None
    
    def on_directory_selected(self, path):
        # Build index
        self.indexer = ProjectIndexer(path, target_is_file=False)
        self.indexer.rebuild()
    
    def on_search_query(self, key_query, value_query, mode):
        # Execute search
        flat = self.indexer.get_flat()
        results = resolve_query_with_mode(
            flat,
            key_query,
            value_query,
            mode,  # "key", "value", or "both"
            case_sensitive=self.case_checkbox.isChecked(),
            regex=self.regex_checkbox.isChecked()
        )
        
        # Display results
        self.display_results(results)
```

**Benefits**:
- Reuses tested search logic
- Supports multi-file search
- Line number navigation
- TypeScript support

---

## Recommendations

### For Current Implementation

1. **Add Caching**:
   ```python
   class ProjectIndexer:
       def __init__(self, ...):
           self._cache_mtime = {}  # Track file modification times
       
       def rebuild(self):
           # Only reindex changed files
           for fpath in self.files:
               current_mtime = os.path.getmtime(fpath)
               if fpath not in self._cache_mtime or self._cache_mtime[fpath] != current_mtime:
                   # Re-index this file
                   self._cache_mtime[fpath] = current_mtime
   ```

2. **Add Incremental Indexing**:
   ```python
   def add_file(self, fpath: str) -> None:
       """Add single file to index without full rebuild."""
       # Parse file
       # Merge into self.flat
   
   def remove_file(self, fpath: str) -> None:
       """Remove file from index."""
       # Remove all entries with file=fpath
   ```

3. **Add Progress Reporting**:
   ```python
   def rebuild(self, progress_callback=None) -> None:
       for i, fpath in enumerate(self.files):
           # ... index file ...
           if progress_callback:
               progress_callback(i+1, len(self.files), fpath)
   ```

4. **Add Statistics**:
   ```python
   def get_stats(self) -> Dict[str, Any]:
       return {
           "total_files": len(self.files),
           "total_keys": len(self.flat),
           "json_files": sum(1 for f in self.files if f.endswith(".json")),
           "ts_files": sum(1 for f in self.files if f.endswith((".ts", ".tsx")))
       }
   ```

5. **Add Async Support**:
   ```python
   async def rebuild_async(self) -> None:
       """Async version for non-blocking indexing."""
       # Use asyncio.to_thread() for file I/O
   ```

### For Phase 4 Integration

1. **Unified Search API**:
   ```python
   # File Explorer should delegate to json_search
   def execute_search(self, query_params):
       return resolve_query_with_mode(self.indexer.get_flat(), **query_params)
   ```

2. **Index on Background Thread**:
   ```python
   # Don't block GUI during indexing
   worker = IndexerWorker(path)
   worker.finished.connect(self.on_index_ready)
   worker.start()
   ```

3. **Incremental UI Updates**:
   ```python
   # Show results as they're found (streaming)
   for result in stream_results(flat, query):
       self.add_result_to_table(result)
       QApplication.processEvents()  # Keep UI responsive
   ```

---

## Testing Coverage

**Test Files** (expected but not verified):
- `tests/test_json_search.py` or `tests/json_search/`

**Recommended Test Cases**:
1. ✅ Basic flattening (dict, list, nested)
2. ✅ TS object extraction (const, default, type annotations)
3. ✅ Indexing (single file, directory, ignored directories)
4. ✅ Query parsing (composite, simple, t-prefix stripping)
5. ✅ Search modes (key, value, both)
6. ✅ Match options (case, whole word, regex)
7. ❓ Brace matching edge cases (nested strings, templates)
8. ❓ Line number guessing accuracy
9. ❓ Large file performance (>10MB JSON)
10. ❓ Invalid JSON/TS handling
11. ❓ Unicode in keys/values
12. ❓ Deduplication correctness

---

## Session Statistics

**Files Studied**: 5  
**Total LOC**: 792  
**Design Patterns**: 12  
**Key Algorithms**: 5 (Flatten, Index, Parse TS, Query, Match)  
**Public Functions**: 10  
**Classes**: 1 (ProjectIndexer)  

**Cumulative Progress** (Sessions 1-8):
- **Files studied**: 34 (29 + 5)
- **LOC analyzed**: 12,586 (11,794 + 792)
- **Design patterns**: 80 (68 + 12)
- **Code coverage**: 15.0% of codebase (12,586 / 83,619)

---

## Next Steps

**Session 9** (1h): GUI Dock Components
- `gui/set_operations_dock.py`
- `gui/json_validator.py`
- `gui/json_editor_tab.py`
- `gui/results_tree.py`
- `gui/operation_preview_dialog.py`

**Focus**: Understand dock integration patterns, UI/business logic separation, Signal/slot patterns, Worker thread usage.

---

**End of Session 8 Notes**
