# Code Study Session 6 Notes
**Programmer #7 - Source Code Study**  
**Date**: 2026-01-22  
**Session Focus**: Phase 3 - Utility Modules (src/utils/)  
**Files Studied**: 5 files (~400 lines)

---

## 📋 Session Overview

**Progress**:
- **Files Studied This Session**: 5 files
- **Lines of Code**: ~400 lines
- **Total Progress**: 28/196 files (14.3%)
- **Phase**: Phase 3 - Feature Modules (IN PROGRESS)

**Files Analyzed**:
1. `src/utils/file_utils.py` (68 lines) ✅
2. `src/utils/text_utils.py` (93 lines) ✅
3. `src/utils/normalization.py` (130 lines) ✅
4. `src/utils/logger.py` (150 lines partial) ✅
5. `src/utils/advanced_conditions.py` (106 lines) ✅

**Remaining in src/utils/**:
- `error_handler.py` (471 lines)
- `error_reporter.py` (255 lines)
- `update_checker.py` (286 lines)
- `file_finder.py` (417 lines)
- **Total remaining**: ~1,429 lines

---

## 🔍 Detailed Analysis

### 1. file_utils.py (68 lines) - File I/O Utilities

**Purpose**: Basic file discovery and I/O operations

#### **walk_files() Function** (Lines 9-43)

**Purpose**: Recursively yield files with glob filters

**Signature**:
```python
def walk_files(
    root: str,
    include_globs: Sequence[str] | None = None,
    exclude_globs: Sequence[str] | None = None
) -> Iterator[str]:
```

**Algorithm**:

**Helper Functions** (Lines 20-32):
```python
def _match_any(path: str, patterns: Sequence[str]) -> bool:
    if not patterns:
        return True  # No include filters = match all
    for pat in patterns:
        # Match full path OR basename
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
            return True
    return False

def _match_none(path: str, patterns: Sequence[str]) -> bool:
    """Return True if path matches NONE of the patterns (should not exclude)"""
    for pat in patterns:
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
            return False  # Matched an exclude pattern
    return True  # No exclusions matched
```

**Main Logic** (Lines 34-43):
```python
# If root is a file, check filters and yield if matches
if os.path.isfile(root):
    if _match_any(root, include_globs) and _match_none(root, exclude_globs):
        yield root
    return

# If root is directory, walk recursively
for dirpath, _dirnames, filenames in os.walk(root):
    for f in filenames:
        path = os.path.join(dirpath, f)
        if _match_any(path, include_globs) and _match_none(path, exclude_globs):
            yield path
```

**Key Features**:
- ✅ Works with both files and directories as root
- ✅ Matches on full path OR basename
- ✅ Include filters: "at least one must match"
- ✅ Exclude filters: "none must match"
- ✅ Uses fnmatch (shell-style wildcards: `*.py`, `test_*`)

**Example**:
```python
# Find all Python files except tests
for path in walk_files("src", include_globs=["*.py"], exclude_globs=["test_*"]):
    print(path)
```

---

#### **read_text() Function** (Lines 46-53)

**Purpose**: Read text with encoding fallback

```python
def read_text(path: str, max_bytes: Optional[int] = None) -> str:
    with open(path, "rb") as fh:
        data = fh.read() if max_bytes is None else fh.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")
```

**Fallback Strategy**:
1. Try UTF-8 first (most common)
2. Fall back to latin-1 with error replacement
3. latin-1 never fails (maps all 256 bytes)

**Use Case**: Robust file reading when encoding is unknown

---

#### **write_text() Function** (Lines 56-60)

**Purpose**: Write text with directory creation

```python
def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
```

**Key Feature**: Creates parent directories automatically

---

#### **safe_backup_file() Function** (Lines 63-68)

**Purpose**: Create `.bak` file if doesn't exist

```python
def safe_backup_file(path: str) -> None:
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
```

**Safe**: Won't overwrite existing backups

---

### 2. text_utils.py (93 lines) - Text Processing Utilities

**Purpose**: Masking, exclusions, regex compilation for text operations

#### **parse_exclusion_patterns() Function** (Lines 7-11)

**Purpose**: Parse comma-separated regex patterns

```python
def parse_exclusion_patterns(csv_regex: str) -> list[str]:
    if not csv_regex.strip():
        return []
    return [p.strip() for p in csv_regex.split(",") if p.strip()]
```

**Example**: `"pattern1, pattern2, pattern3"` → `["pattern1", "pattern2", "pattern3"]`

---

#### **mask_exclusions() Function** (Lines 14-38)

**Purpose**: Replace excluded regions with guard tokens

**Signature**:
```python
def mask_exclusions(text: str, patterns: list[str]) -> tuple[str, list[str]]:
    """
    Replace each region matched by exclusion regex with guard token @@XCL{n}@@.
    Returns (masked_text, guards) where guards[i] is the original match.
    """
```

**Algorithm**:
```python
guards: list[str] = []
token_prefix = "@@XCL"
token_suffix = "@@"

def _make_replacer(pat: str):
    rx = re.compile(pat, flags=re.DOTALL | re.MULTILINE)
    def _repl(m: re.Match) -> str:
        idx = len(guards)
        guards.append(m.group(0))  # Store original
        return f"{token_prefix}{idx}{token_suffix}"  # Return @@XCL0@@
    return rx, _repl

masked = text
for pat in patterns:
    rx, repl = _make_replacer(pat)
    masked = rx.sub(repl, masked)

return masked, guards
```

**Use Case**: Exclude regions from processing (e.g., code comments, strings)

**Example**:
```python
text = "Keep this /* exclude this */ keep this"
masked, guards = mask_exclusions(text, [r'/\*.*?\*/'])
# masked = "Keep this @@XCL0@@ keep this"
# guards = ["/* exclude this */"]
```

---

#### **unmask_exclusions() Function** (Lines 41-47)

**Purpose**: Restore masked regions

```python
def unmask_exclusions(text: str, guards: list[str]) -> str:
    token_prefix = "@@XCL"
    token_suffix = "@@"
    for i, original in enumerate(guards):
        text = text.replace(f"{token_prefix}{i}{token_suffix}", original)
    return text
```

**Reverse Operation**: `@@XCL0@@` → original text from guards[0]

---

#### **_escape_variants_for_quotes() Function** (Lines 50-65)

**Purpose**: Generate regex-safe quote variants

**Problem**: Match values with real quotes OR escaped quotes

```python
def _escape_variants_for_quotes(s: str) -> list[str]:
    base = re.escape(s)
    variants = { base }
    
    if '"' in s:
        variants.add(re.escape(s.replace('"', '\\"')))
    if "'" in s:
        variants.add(re.escape(s.replace("'", "\\'")))
    if "\\\"" in s or "\\\'" in s:
        variants.add(re.escape(s.replace("\\\"", "\"").replace("\\\'", "'")))
    
    return list(variants)
```

**Example**:
```python
s = 'He said "hello"'
variants = _escape_variants_for_quotes(s)
# Returns: [
#     'He said "hello"',           # Original
#     'He said \\"hello\\"',       # Escaped version
# ]
```

**Use Case**: Match JSON values regardless of quote escaping

---

#### **compile_value_union_regex() Function** (Lines 68-93)

**Purpose**: Build alternation regex with named groups

```python
def compile_value_union_regex(value_to_key: dict[str, str]) -> re.Pattern:
    """
    Build single alternation regex with named groups for each value.
    Sort by length (desc) to prefer longest phrase first.
    """
    items = sorted(value_to_key.items(), key=lambda kv: len(kv[0]), reverse=True)
    
    parts = []
    idx = 0
    for val, _key in items:
        if not val:
            continue
        
        # Get quote variants
        variants = _escape_variants_for_quotes(val)
        if len(variants) == 1:
            body = variants[0]
        else:
            body = "(?:" + "|".join(variants) + ")"
        
        # Create named group
        gname = f"V{idx}"
        parts.append(f"(?P<{gname}>{body})")
        idx += 1
    
    if not parts:
        return re.compile(r"(?!x)x")  # Never-matching regex
    
    big = "|".join(parts)
    return re.compile(big)
```

**Key Feature**: Longest match first (greedy matching)

**Example**:
```python
value_to_key = {
    "hello world": "key1",
    "hello": "key2"
}
regex = compile_value_union_regex(value_to_key)
# Regex: (?P<V0>hello world)|(?P<V1>hello)
# Matches "hello world" before trying "hello" (longest first)
```

**Use Case**: Replace multiple values simultaneously (substitution map)

---

### 3. normalization.py (130 lines) - Token Normalization

**Purpose**: Normalize extracted tokens (for JSX/HTML parameter extraction)

**Author**: Josué Amaral (2025-12-02)

#### **STANDARD_HTML_TAGS Constant** (Lines 20-31)

**78 Standard HTML Tags**:
```python
STANDARD_HTML_TAGS = {
    'html','head','title','base','link','meta','style','script','noscript',
    'body','section','nav','article','aside','h1','h2','h3','h4','h5','h6',
    'header','footer','address','main','p','hr','pre','blockquote','ol','ul',
    'li','dl','dt','dd','figure','figcaption','div','a','em','strong','small',
    's','cite','q','dfn','abbr','ruby','rb','rt','rtc','rp','data','time',
    'code','var','samp','kbd','sub','sup','i','b','u','mark','bdi','bdo',
    'span','br','wbr','ins','del','picture','source','img','iframe','embed',
    'object','param','video','audio','track','map','area','table','caption',
    'colgroup','col','tbody','thead','tfoot','tr','td','th','form','label',
    'input','button','select','datalist','optgroup','option','textarea',
    'output','progress','meter','fieldset','legend','details','summary',
    'dialog','slot','template','canvas'
}
```

---

#### **is_standard_tag() Function** (Lines 34-36)

```python
def is_standard_tag(name: str) -> bool:
    return name.lower() in STANDARD_HTML_TAGS
```

**Use Case**: Distinguish custom components from standard HTML

---

#### **kept_prefix() Function** (Lines 39-52)

**Purpose**: Build path prefix up to deepest custom tag

```python
def kept_prefix(file_root: str, stack: list[str], drop_standard: bool) -> list[str]:
    if not drop_standard:
        return [file_root] + stack
    
    # Find deepest custom tag from right to left
    for i in range(len(stack) - 1, -1, -1):
        if not is_standard_tag(stack[i]):
            return [file_root] + stack[:i + 1]
    
    return [file_root]
```

**Example**:
```python
# stack = ["div", "MyComponent", "span", "AnotherComponent"]
# drop_standard = True
kept = kept_prefix("file", stack, True)
# Returns: ["file", "div", "MyComponent", "span", "AnotherComponent"]
# (keeps all because deepest custom tag is "AnotherComponent")

# stack = ["div", "span", "p"]  # All standard
kept = kept_prefix("file", stack, True)
# Returns: ["file"]  # Drops all standard tags
```

**Use Case**: Generate meaningful parameter names from component hierarchy

---

#### **smart_truncate() Function** (Lines 55-88)

**Purpose**: Truncate text at word boundaries

```python
def smart_truncate(text: str, limit: Optional[str], avoid_cut: bool) -> str:
    if not text or limit in (None, 'all', 'ALL', 'All'):
        return text
    
    try:
        n = int(limit)
    except Exception:
        return text
    
    if n <= 0 or len(text) <= n:
        return text
    
    sub = text[:n]
    
    if not avoid_cut:
        return sub
    
    # If ended on whitespace, strip trailing whitespace
    if sub[-1].isspace():
        return sub.rstrip()
    
    # Find last whitespace run before cut
    m = re.search(r'\s+\S*$', sub, flags=re.UNICODE)
    if m:
        cut = m.start()
        if cut > 0:
            return sub[:cut].rstrip()
    
    # Fallback: no whitespace found (very long first word)
    return sub
```

**Algorithm**:
1. If limit is 'all' or None → return full text
2. Cut at character limit
3. If avoid_cut enabled:
   - If ended on whitespace → strip it
   - Else find last whitespace → cut before it
   - Fallback: hard cut (long first word)

**Example**:
```python
text = "This is a very long sentence that needs truncation"
result = smart_truncate(text, "20", avoid_cut=True)
# Result: "This is a very long" (cut at word boundary)
```

---

#### **normalize_token() Function** (Lines 91-124)

**Purpose**: Normalize string to snake/camel/pascal/kebab case

```python
def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    # Clean: Replace non-alphanumeric with space
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", s)
    words = [w for w in cleaned.strip().split() if w]
    
    if not words:
        token = ""
    else:
        if case_style == "snake":
            token = "_".join(w.lower() for w in words)
        elif case_style == "kebab":
            token = "-".join(w.lower() for w in words)
        elif case_style == "camel":
            head = words[0].lower()
            tail = [w[:1].upper() + w[1:].lower() for w in words[1:]]
            token = head + "".join(tail)
        elif case_style == "pascal":
            token = "".join(w[:1].upper() + w[1:].lower() for w in words)
        else:
            token = "_".join(w.lower() for w in words)  # Default: snake
    
    if to_upper:
        token = token.upper()
    
    return token
```

**Examples**:
```python
normalize_token("Hello World", "snake", False)   # "hello_world"
normalize_token("Hello World", "camel", False)   # "helloWorld"
normalize_token("Hello World", "pascal", False)  # "HelloWorld"
normalize_token("Hello World", "kebab", False)   # "hello-world"
normalize_token("Hello World", "snake", True)    # "HELLO_WORLD"
```

**Use Case**: Generate consistent variable names from text

---

#### **path_join() Function** (Lines 127-129)

```python
def path_join(parts: List[str]) -> str:
    """Join path parts with dots, filtering out empty strings."""
    return ".".join([p for p in parts if p])
```

**Example**: `["root", "", "child", "leaf"]` → `"root.child.leaf"`

---

### 4. logger.py (Partial - 150 lines) - Logging System

**Purpose**: Structured logging with rotation and colors

**Author**: Clarify team

#### **Configuration Constants** (Lines 39-48)

```python
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_DIR = Path.home() / ".clarify" / "logs"
DEFAULT_LOG_FILE = "clarify.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files
```

**Log Location**: `~/.clarify/logs/clarify.log`

---

#### **ColoredFormatter Class** (Lines 51-79)

**Purpose**: ANSI color codes for console output

```python
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        
        result = super().format(record)
        
        # Reset levelname (in case record is reused)
        record.levelname = levelname
        
        return result
```

**Feature**: Color-coded log levels for better readability

---

#### **ClarifyLogger Class** (Lines 82-150)

**Pattern**: Singleton logger manager

```python
class ClarifyLogger:
    _instance: Optional['ClarifyLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            ClarifyLogger._initialized = True
```

**Singleton Pattern**: Ensures one logger configuration for entire app

---

**_setup_logging() Method** (Lines 104-150):

**Setup Process**:
1. Get log level from environment (`CLARIFY_LOG_LEVEL`) or default to INFO
2. Create log directory (`~/.clarify/logs/`)
3. Configure root logger (`clarify` namespace)
4. Add rotating file handler (10 MB max, 5 backups)
5. Add console handler with color formatter
6. Log initialization message

**File Handler**:
```python
file_handler = logging.handlers.RotatingFileHandler(
    filename=log_file,
    maxBytes=MAX_LOG_SIZE,     # 10 MB
    backupCount=BACKUP_COUNT,   # 5 files
    encoding='utf-8'
)
```

**Rotation**: `clarify.log` → `clarify.log.1` → ... → `clarify.log.5`

**Console Handler**:
```python
console_handler = logging.StreamHandler(sys.stdout)
console_formatter = ColoredFormatter(...)
console_handler.setFormatter(console_formatter)
```

**Output**: Both file and console simultaneously

---

**Usage**:
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.debug("Debug info", extra={"user": "admin"})
logger.error("Error occurred", exc_info=True)
```

**Features**:
- ✅ Structured logging (timestamp, level, module, line number)
- ✅ File rotation (prevents log bloat)
- ✅ Console colors (better UX)
- ✅ Thread-safe (Python logging is thread-safe)
- ✅ Environment-configurable log level

---

### 5. advanced_conditions.py (106 lines) - UI-Filter Bridge

**Purpose**: Bridge between UI widgets and core filter system

**Tasks**: Task #51 (AI Processor) + Sprint B Feature #1 (JSON Rewriter)

#### **get_conditions_from_ui() Function** (Lines 17-60)

**Purpose**: Build Condition objects from UI widget rows

**Signature**:
```python
def get_conditions_from_ui(cond_rows) -> list[Condition]:
    """
    Args:
        cond_rows: List of tuples (combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex)
                   Each tuple contains PySide6 widgets
    
    Returns:
        List of valid Condition objects (empty rows skipped)
    """
```

**Algorithm**:
```python
conditions = []

for combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex in cond_rows:
    # Extract values from widgets
    field = combo_field.currentText().strip()
    operator = combo_op.currentText().strip()
    value = ed_value.text().strip()
    scope_type = combo_scope.currentText().strip()
    case_sensitive = chk_case.isChecked()
    use_regex = chk_regex.isChecked()
    
    # Skip empty rows (no field/operator/value)
    if not field or not operator or not value:
        continue
    
    # Create Condition object
    cond = Condition(
        field=field,
        operator=operator,
        value=value,
        scope_type=scope_type,
        scope_value="",  # Not used yet
        case_sensitive=case_sensitive,
        whole_word=False,  # Not exposed in UI yet
        use_regex=use_regex
    )
    conditions.append(cond)

return conditions
```

**Key Feature**: Skips empty rows automatically

---

#### **apply_conditions_to_files() Function** (Lines 63-106)

**Purpose**: Apply conditions to file list with statistics

**Signature**:
```python
def apply_conditions_to_files(
    files: list[str],
    conditions: list[Condition],
    logic_op: str = "AND",
    enabled: bool = True
) -> tuple[list[str], int]:
    """
    Returns:
        Tuple of (filtered_files, num_filtered_out)
    """
```

**Algorithm**:
```python
# If filtering disabled, return all files
if not enabled:
    return files, 0

# If no conditions, return all files
if not conditions:
    return files, 0

# Apply filters using core module
original_count = len(files)
filtered_files = filter_files_by_conditions(files, conditions, logic_op)
filtered_out = original_count - len(filtered_files)

return filtered_files, filtered_out
```

**Key Feature**: Returns count of filtered files (for statistics display)

**Example**:
```python
files = ["file1.json", "file2.txt", "file3.json"]
conditions = [Condition(field="ext", operator="equals", value=".json")]
filtered, count = apply_conditions_to_files(files, conditions, "AND", True)
# filtered = ["file1.json", "file3.json"]
# count = 1  (file2.txt was filtered out)
```

---

## 🔑 Key Architectural Insights

### **Utils Module Design Philosophy**:

1. **Pure Functions**:
   - file_utils: Stateless I/O operations
   - text_utils: Functional text transformations
   - normalization: Pure token conversion
   - **Easy to test, no side effects**

2. **Robust Error Handling**:
   - `read_text()`: UTF-8 → latin-1 fallback
   - `smart_truncate()`: Handle 'all', None, non-integer limits
   - `normalize_token()`: Handle empty words gracefully

3. **Bridge Pattern** (advanced_conditions.py):
   - Decouples UI layer from core logic
   - Converts PySide6 widgets → Condition objects
   - Reusable across multiple docks

4. **Singleton Pattern** (logger.py):
   - One logging configuration for app
   - Prevents duplicate handlers
   - Thread-safe by design

5. **Generator Pattern** (file_utils.py):
   - `walk_files()` yields files lazily
   - Memory-efficient for large directories
   - Can be consumed with for-loop or list()

---

### **Design Patterns Identified**:

1. **Singleton** (ClarifyLogger):
   - Ensures one logger instance
   - Prevents handler duplication

2. **Bridge** (advanced_conditions):
   - Separates UI from business logic
   - Condition objects are UI-agnostic

3. **Template Method** (ColoredFormatter):
   - Extends logging.Formatter
   - Customizes format() method

4. **Strategy** (normalize_token):
   - 4 case strategies (snake, camel, pascal, kebab)
   - Selected via parameter

5. **Guard/Memento** (mask_exclusions):
   - Stores original values in guards list
   - Restores with unmask_exclusions()

---

### **Critical Utilities Summary**:

**File Operations**:
- `walk_files()`: Recursive traversal with glob filters
- `read_text()`: Robust reading with encoding fallback
- `write_text()`: Write with directory creation
- `safe_backup_file()`: Non-destructive backup

**Text Processing**:
- `mask_exclusions()` / `unmask_exclusions()`: Region protection
- `compile_value_union_regex()`: Multi-value matching (longest first)
- `_escape_variants_for_quotes()`: Handle quote variations

**Token Normalization**:
- `normalize_token()`: Convert to snake/camel/pascal/kebab
- `smart_truncate()`: Word-boundary truncation
- `kept_prefix()`: Build component path (drop standard tags)

**Logging**:
- `ClarifyLogger`: Singleton with file rotation
- `ColoredFormatter`: ANSI color console output
- Location: `~/.clarify/logs/clarify.log` (10 MB, 5 backups)

**UI Bridge**:
- `get_conditions_from_ui()`: Widgets → Condition objects
- `apply_conditions_to_files()`: Apply with statistics

---

### **Don't Touch Zones** (Critical Code):

1. **read_text() encoding fallback**:
   - UTF-8 → latin-1 order is critical
   - latin-1 must use `errors="replace"` for safety
   - Changing order breaks robustness

2. **mask_exclusions() token format**:
   - `@@XCL{n}@@` format must match unmask_exclusions()
   - Changing format breaks round-trip
   - Multiple patterns must process sequentially (not in parallel)

3. **compile_value_union_regex() sorting**:
   - MUST sort by length descending
   - Ensures longest match first (greedy)
   - Example: "hello world" before "hello"

4. **ClarifyLogger singleton pattern**:
   - `_initialized` flag prevents duplicate setup
   - Removing singleton causes duplicate handlers
   - Multiple file handlers = log duplication

5. **normalize_token() character cleaning**:
   - Regex `[^0-9A-Za-z]+` preserves alphanumeric only
   - Changing pattern breaks consistency
   - Must split on whitespace after cleaning

---

## 📊 Statistics

**Session 6 Metrics**:
- **Files Read**: 5
- **Lines Analyzed**: ~400
- **Functions Analyzed**: 15+
- **Design Patterns Identified**: 5 (Singleton, Bridge, Template Method, Strategy, Guard/Memento)
- **Utility Categories**: 4 (File I/O, Text Processing, Token Normalization, Logging)

**Cumulative Progress**:
- **Total Files Studied**: 28 / 196 (14.3%)
- **Total Lines Studied**: ~5,459 / 58,165 (9.4%)
- **Documentation Read**: 242 / 242 (100%)
- **Overall Comprehension**: ~57% (docs 100%, code 14%)

**Phase 3 Status**: 🔄 **IN PROGRESS** (5/~50 feature module files)

**Remaining in utils/**:
- `error_handler.py` (471 lines)
- `error_reporter.py` (255 lines)
- `update_checker.py` (286 lines)
- `file_finder.py` (417 lines)
- **Total**: ~1,429 lines

**Remaining in Phase 3**:
- src/rewriter/ (9 files, ~2,297 lines)
- src/gui/docks/ (many files)
- src/ai_processor/ (files TBD)
- **Estimated total**: ~20,000 lines remaining in Phase 3

---

## 🎯 Key Takeaways

### **What We Now Understand** (Utils Module):

1. ✅ **File I/O System**:
   - Recursive file discovery with glob filters
   - Robust text reading (UTF-8 → latin-1 fallback)
   - Safe backups and directory creation

2. ✅ **Text Processing**:
   - Exclusion masking (protect regions during processing)
   - Multi-value regex compilation (longest match first)
   - Quote variant handling (escaped vs real quotes)

3. ✅ **Token Normalization**:
   - 4 case styles (snake, camel, pascal, kebab)
   - Smart truncation (word boundaries)
   - Component path building (drop standard HTML tags)

4. ✅ **Logging System**:
   - Singleton pattern (one configuration)
   - File rotation (10 MB, 5 backups)
   - Console colors (ANSI codes)
   - Environment-configurable level

5. ✅ **UI-Core Bridge**:
   - Widget extraction to Condition objects
   - Reusable across multiple docks
   - Statistics tracking (filtered file count)

### **Utility Module Architecture**:

```
src/utils/
├── File Operations
│   ├── file_utils.py          # walk_files, read/write, backup
│   └── file_finder.py          # (not yet studied)
│
├── Text Processing
│   ├── text_utils.py          # masking, regex compilation
│   └── normalization.py       # token normalization, case styles
│
├── Error Handling
│   ├── error_handler.py       # (not yet studied)
│   └── error_reporter.py      # (not yet studied)
│
├── System
│   ├── logger.py              # structured logging with rotation
│   └── update_checker.py      # (not yet studied)
│
└── UI Bridge
    └── advanced_conditions.py # UI widgets → Condition objects
```

### **Utility Usage Patterns**:

**File Discovery**:
```python
from src.utils.file_utils import walk_files

for path in walk_files("src", include_globs=["*.py"], exclude_globs=["test_*"]):
    process(path)
```

**Text Masking**:
```python
from src.utils.text_utils import mask_exclusions, unmask_exclusions

masked, guards = mask_exclusions(text, [r'/\*.*?\*/'])  # Mask comments
processed = process_text(masked)
result = unmask_exclusions(processed, guards)  # Restore comments
```

**Token Normalization**:
```python
from src.utils.normalization import normalize_token

token = normalize_token("Hello World", "camel", False)  # "helloWorld"
```

**Logging**:
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Operation started", extra={"user": "admin"})
```

**Condition Bridge**:
```python
from src.utils.advanced_conditions import get_conditions_from_ui, apply_conditions_to_files

conditions = get_conditions_from_ui(self.cond_rows)
filtered, count = apply_conditions_to_files(files, conditions, "AND", True)
```

---

## 📝 Protocol Compliance Check

**SIMPLICITY_PROTOCOL_3 Step 1.2 Progress**:

- [x] Study entry points ✅
- [x] Study main application class ✅
- [x] Study initialization system ✅
- [x] Study UI construction ✅
- [x] Study core business logic ✅
- [~] Study utility modules (42% done - 5/12 files) 🔄
- [ ] Study feature modules (rewriter, gui/docks, ai_processor)
- [ ] Study support systems (Phase 4)
- [ ] Create comprehensive NOTES.md (Phase 5)

**Current Status**: ~48% of Step 1.2 complete

---

**Session 6 Complete! 🎉**  
**Next**: Continue Phase 3 - Study remaining utils/ files or move to rewriter/
