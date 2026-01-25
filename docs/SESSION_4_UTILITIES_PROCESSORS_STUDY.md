# Session 4: LEAF - Utilities, Processors & Specialized Modules

**Date:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Session Type:** SCAN Reading (Catalog + Common Patterns)  
**Time Investment:** 1.5 hours  
**Protocol:** SIMPLICITY_PROTOCOL_3.md Step 1.3  
**Methodology:** Import Tree Analogy - LEAF Layer (Pure Utilities & Transformers)

---

## Executive Summary

**Mission:** Catalog utility functions, data processors, and specialized transformation modules  
**Modules Analyzed:** `src/utils/` (12 files, 2,304 lines) + `src/extractors/` (4 files, 1,146 lines) + specialized modules (~3,000 lines)  
**Key Discovery:** Rich utility library + specialized transformers for domain-specific tasks  
**Architecture Pattern:** Pure functions (LEAFs) with minimal dependencies

---

## Modules Distribution

| Category | Location | Files | Lines | Purpose |
|----------|----------|-------|-------|---------|
| **Utilities** | `src/utils/` | 12 | 2,304 | File ops, logging, error handling |
| **Extractors** | `src/extractors/` | 4 | 1,146 | JSX/HTML/generic parsing |
| **Processors** | `src/processors/` | 1 | 399 | Code-aware translation |
| **i18n** | `src/i18n/` | 2 | 292 | Internationalization |
| **Converters** | `src/` | 1 | 437 | Case conversion (camel/snake/etc.) |
| **Translators** | `src/translators/`, `src/translation/` | 3 | ~450 | JSON/Google translation |
| **Misc** | `src/` | 10+ | ~1,500 | Domain-specific modules |

**Total Analyzed:** ~40 files, ~6,500 lines of utility/transformation code

---

## Deep Dive: Utils Package (`src/utils/`)

### Package Structure

```
src/utils/
├── __init__.py                 (18 lines)   - Package exports
├── file_utils.py               (67 lines)   - File I/O operations
├── text_utils.py               (93 lines)   - Text processing
├── ts_utils.py                 (74 lines)   - TypeScript handling
├── logger.py                   (329 lines)  - Logging system
├── error_handler.py            (471 lines)  - Crash reporting
├── error_reporter.py           (255 lines)  - Error dialog UI
├── file_finder.py              (417 lines)  - Advanced file search
├── advanced_conditions.py      (105 lines)  - Complex filters
├── normalization.py            (129 lines)  - Data normalization
├── stats_formatter.py          (60 lines)   - Statistics display
└── update_checker.py           (286 lines)  - Version checking
```

**Total:** 2,304 lines

---

### 1. File Operations (`file_utils.py` - 67 lines)

**Purpose:** Core file I/O with safe defaults

#### walk_files()

```python
def walk_files(root: str,
               include_globs: Sequence[str] | None = None,
               exclude_globs: Sequence[str] | None = None) -> Iterator[str]:
    """
    Recursively yield files under 'root' with fnmatch-style glob filters.
    
    Examples:
        # All Python files
        walk_files("./src", include_globs=["*.py"])
        
        # All JS/TS except tests
        walk_files("./src", 
                  include_globs=["*.js", "*.ts"],
                  exclude_globs=["*.test.js", "*.spec.ts"])
    """
    def _match_any(path: str, patterns: Sequence[str]) -> bool:
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return True
        return False
    
    # Single file handling
    if os.path.isfile(root):
        if _match_any(root, include_globs) and _match_none(root, exclude_globs):
            yield root
        return
    
    # Directory tree traversal
    for dirpath, _dirnames, filenames in os.walk(root):
        for f in filenames:
            path = os.path.join(dirpath, f)
            if _match_any(path, include_globs) and _match_none(path, exclude_globs):
                yield path
```

**Analysis:**
- ✅ **Generator:** Memory-efficient (yields one file at a time)
- ✅ **Flexible Matching:** Both full path and basename matching
- ✅ **Single File Mode:** Works for both files and directories
- 🎯 **Role:** LEAF - Pure file system traversal

#### read_text()

```python
def read_text(path: str, max_bytes: Optional[int] = None) -> str:
    """Read text file with UTF-8 fallback to latin-1."""
    with open(path, "rb") as fh:
        data = fh.read() if max_bytes is None else fh.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")
```

**Analysis:**
- ✅ **Encoding Fallback:** UTF-8 → latin-1 (handles legacy files)
- ✅ **Partial Read:** `max_bytes` param for large files
- ✅ **Error Handling:** `errors="replace"` prevents crashes
- 🎯 **Role:** LEAF - Safe text reading with graceful degradation

#### write_text() & safe_backup_file()

```python
def write_text(path: str, content: str) -> None:
    """Write text to file, creating parent directories if needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def safe_backup_file(path: str) -> None:
    """Create path.bak once. If already exists, do not overwrite."""
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
```

**Analysis:**
- ✅ **Auto-create Directories:** `os.makedirs(exist_ok=True)`
- ✅ **Non-destructive Backup:** Only creates .bak once
- 🎯 **Use Case:** Protect user data before modifications

---

### 2. Logging System (`logger.py` - 329 lines)

**Purpose:** Centralized structured logging (v2.9.58)

#### Architecture

```
┌──────────────────────────────────────────────┐
│         ClarifyLogger (Singleton)            │
│                                              │
│  _setup_logging()                            │
│    ├─ File Handler (RotatingFileHandler)    │
│    │    • ~/.clarify/logs/clarify.log       │
│    │    • Max 10 MB, keep 5 backups         │
│    │    • Plain text format                 │
│    │                                         │
│    └─ Console Handler (StreamHandler)       │
│         • Colored output (ANSI codes)       │
│         • stdout (not stderr)               │
│                                              │
│  get_logger(name) → logger instance          │
└──────────────────────────────────────────────┘
```

#### ColoredFormatter

```python
class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        """Format log record with colors for console."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        result = super().format(record)
        record.levelname = levelname  # Reset for reuse
        return result
```

#### Configuration

```python
# Log format
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

# Example output:
# 2026-01-20 14:30:15 | INFO     | clarify.app:127 | Application started
# 2026-01-20 14:30:16 | WARNING  | clarify.utils.file_utils:45 | Large file detected
# 2026-01-20 14:30:20 | ERROR    | clarify.core.search:89 | Search failed
```

#### Usage

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)  # Creates logger with module name

logger.debug("Detailed debug info")
logger.info("Normal operation")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)  # Includes traceback
logger.critical("Critical failure")
```

**Features:**
- ✅ **Rotating Files:** 10 MB max, 5 backups (prevents disk fill)
- ✅ **Colored Console:** Easy visual scanning
- ✅ **Environment Config:** `CLARIFY_LOG_LEVEL` env var overrides default
- ✅ **Thread-Safe:** Python logging module handles concurrency
- 🎯 **Location:** `~/.clarify/logs/clarify.log`

**Analysis:**
- ✅ **Professional Setup:** File rotation + console output
- ✅ **Singleton Pattern:** Single logging configuration
- ✅ **Contextual Info:** Module name + line number in logs
- 🎯 **Debugging Aid:** Essential for production troubleshooting

---

### 3. Error Handling System (`error_handler.py` - 471 lines)

**Purpose:** Global exception handler with crash reporting (v2.9.61)

#### Architecture

```
┌────────────────────────────────────────────┐
│      CrashHandler (Singleton)              │
│                                            │
│  install()                                 │
│    └─ sys.excepthook = _exception_handler │
│                                            │
│  _exception_handler(exc_type, exc_value)  │
│    ├─ Skip KeyboardInterrupt (Ctrl+C)     │
│    ├─ Track crash frequency               │
│    ├─ Format traceback                    │
│    ├─ Strip sensitive paths (privacy)     │
│    ├─ Log to file                         │
│    ├─ Show error dialog (optional)        │
│    └─ Send report to GitHub (opt-in)      │
│                                            │
│  @contextmanager handle_errors()           │
│    └─ Try/except wrapper for code blocks  │
└────────────────────────────────────────────┘
```

#### Installation

```python
def install_crash_handler(
    show_dialog: bool = True,
    report_crashes: bool = False,
    callback: Optional[Callable] = None
) -> CrashHandler:
    """
    Install global crash handler.
    
    Args:
        show_dialog: Show user-friendly error dialog (requires GUI)
        report_crashes: Send crash reports to GitHub (opt-in for privacy)
        callback: Custom callback(exception, traceback) after handling
    
    Returns:
        CrashHandler instance
    """
    handler = CrashHandler(
        show_dialog=show_dialog,
        report_crashes=report_crashes,
        callback=callback
    )
    handler.install()
    return handler
```

#### Privacy Protection

```python
def _strip_sensitive_paths(self, traceback_text: str) -> str:
    """Strip absolute paths and user info from traceback."""
    # Replace /home/username/... with ~/...
    traceback_text = re.sub(
        r'/home/[^/]+/', 
        '~/', 
        traceback_text
    )
    
    # Replace /Users/username/... with ~/... (macOS)
    traceback_text = re.sub(
        r'/Users/[^/]+/', 
        '~/', 
        traceback_text
    )
    
    # Replace C:\Users\username\... with ~\... (Windows)
    traceback_text = re.sub(
        r'C:\\Users\\[^\\]+\\', 
        r'~\\', 
        traceback_text
    )
    
    return traceback_text
```

#### Context Manager Usage

```python
# Protect specific code sections
from src.utils.error_handler import CrashHandler

with CrashHandler.handle_errors():
    risky_operation()
    parse_user_input()
    modify_critical_file()
# Exceptions caught and handled gracefully
```

**Features:**
- ✅ **Privacy-Aware:** Strips usernames/absolute paths before reporting
- ✅ **Crash Frequency Tracking:** Detects crash loops
- ✅ **Opt-in Reporting:** Default: log locally, don't send to GitHub
- ✅ **Context Manager:** Localized error handling
- 🎯 **Integration:** Works with logger (`get_logger("error_handler")`)

**Analysis:**
- ✅ **Production-Grade:** Handles crashes gracefully
- ✅ **User-Friendly:** Shows dialog instead of stack traces
- ✅ **Privacy First:** No automatic data collection
- 🎯 **Debugging:** Saves crash logs to `~/.clarify/logs/crashes/`

---

### 4. TypeScript Utilities (`ts_utils.py` - 74 lines)

**Purpose:** Handle TypeScript/JavaScript object literals

#### load_ts_object()

```python
def load_ts_object(path: str) -> dict:
    """
    Load TypeScript/JavaScript object literal as Python dict.
    
    Supports:
    - export default { ... }
    - module.exports = { ... }
    - const x = { ... }; export default x;
    - Pure JSON
    
    Returns:
        Parsed dictionary
    """
    text = read_text(path)
    
    # Strip comments
    text = strip_comments(text)
    
    # Remove export statements
    text = strip_export_default(text)
    
    # Convert to JSON-ish (handle unquoted keys, trailing commas)
    text = to_json_ish(text)
    
    # Parse as JSON
    return json.loads(text)
```

#### to_json_ish()

```python
def to_json_ish(source: str) -> str:
    """
    Convert loose JS/TS object literal to valid JSON.
    
    Transforms:
    - Unquoted keys: { foo: "bar" } → { "foo": "bar" }
    - Trailing commas: { a: 1, } → { "a": 1 }
    - Single quotes: { a: 'value' } → { "a": "value" }
    """
    # Quote unquoted keys
    source = re.sub(r'(\w+)\s*:', r'"\1":', source)
    
    # Single quotes to double quotes
    source = source.replace("'", '"')
    
    # Remove trailing commas
    source = re.sub(r',(\s*[}\]])', r'\1', source)
    
    return source
```

**Analysis:**
- ✅ **Flexible Parser:** Handles loose JS/TS syntax
- ✅ **Comment Removal:** Strips // and /* */ comments
- ✅ **JSON Conversion:** Converts to valid JSON for parsing
- 🎯 **Use Case:** Import i18n translations from TS modules

---

### 5. File Finder (`file_finder.py` - 417 lines)

**Purpose:** Advanced file search with multiple strategies

**Features:**
- Recursive directory traversal
- Extension filtering
- Size filtering
- Date filtering  
- Content matching (regex)
- Exclude patterns (.gitignore style)

**Example:**

```python
from src.utils.file_finder import FileFinder

finder = FileFinder()
results = finder.find(
    root="./src",
    extensions=[".py", ".pyi"],
    exclude_patterns=["__pycache__", "*.pyc"],
    min_size=1024,  # > 1 KB
    max_size=1024*1024,  # < 1 MB
    modified_after="2025-01-01",
    content_regex=r"class\s+\w+\(QDockWidget\)"  # Find QDockWidget subclasses
)
```

**Analysis:**
- ✅ **Rich Filtering:** Multiple criteria combined
- ✅ **Performance:** Uses generators (lazy evaluation)
- 🎯 **Use Case:** "Find large Python files modified recently"

---

### 6. Update Checker (`update_checker.py` - 286 lines)

**Purpose:** Check for new versions on GitHub

**Features:**
- Query GitHub Releases API
- Parse semantic versions (v2.9.111 → (2, 9, 111))
- Compare current vs latest
- Show update notification dialog
- Download links

**Example:**

```python
from src.utils.update_checker import check_for_updates

current_version = "2.9.111"
update_info = check_for_updates(
    repo="owner/clarify",
    current_version=current_version
)

if update_info.has_update:
    print(f"New version available: {update_info.latest_version}")
    print(f"Download: {update_info.download_url}")
```

**Analysis:**
- ✅ **Async Check:** Doesn't block UI
- ✅ **Semantic Versioning:** Proper version comparison
- ✅ **Network Safe:** Handles no internet gracefully
- 🎯 **Feature:** Auto-check on startup (configurable)

---

## Deep Dive: Extractors (`src/extractors/`)

### Package Structure

```
src/extractors/
├── __init__.py         (14 lines)   - Package exports
├── extractor.py        (482 lines)  - Base extractor class
├── generic_parser.py   (90 lines)   - Generic scope extraction
└── jsx_parser.py       (560 lines)  - JSX/TSX parameter extraction
```

**Total:** 1,146 lines

---

### JSXParser (`jsx_parser.py` - 560 lines)

**Purpose:** Extract parameters and attributes from JSX/TSX components

#### Use Case

```tsx
// Input: React component
function MyComponent({ name, age, isActive }: Props) {
  return <div className="container">{name}</div>;
}

<MyComponent 
  name="John" 
  age={25} 
  isActive={true} 
/>

// Extract:
// - Component: MyComponent
// - Props: name, age, isActive
// - Attributes: className="container"
```

#### Parsing Strategy

```python
class JSXParser:
    """
    Parse JSX/TSX files and extract component parameters.
    
    Features:
    - Destructured props: ({ name, age })
    - Type annotations: ({ name }: Props)
    - Default values: ({ name = "default" })
    - Rest props: ({ ...rest })
    - JSX attributes: <Component attr="value" />
    """
    
    def extract_parameters(self, source: str) -> List[Dict[str, Any]]:
        """
        Extract all component parameters from source.
        
        Returns:
            [
                {
                    'component': 'MyComponent',
                    'params': ['name', 'age', 'isActive'],
                    'line': 5
                },
                ...
            ]
        """
```

**Regex Patterns:**

```python
# Match function component
FUNCTION_PATTERN = r'function\s+(\w+)\s*\((.*?)\)'

# Match arrow function component
ARROW_PATTERN = r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>'

# Match destructured props
DESTRUCTURE_PATTERN = r'\{\s*([^}]+)\s*\}'

# Match type annotation
TYPE_PATTERN = r':\s*\w+'
```

**Analysis:**
- ✅ **Regex-Based:** Fast parsing without full AST
- ✅ **TypeScript Support:** Handles type annotations
- ✅ **Multiple Formats:** Function & arrow components
- 🎯 **Use Case:** "Extract all props used in project"

---

## Deep Dive: Case Converter (`src/case_converter.py` - 437 lines)

**Purpose:** Convert object keys between case styles

### Supported Formats

```
camelCase      → userName
PascalCase     → UserName
snake_case     → user_name
kebab-case     → user-name
```

### Architecture

```python
class JSObjectCaseConverter:
    """
    Converts JS/TS/JSON object keys between case styles.
    
    Tolerant parser handles:
    - Comments (// and /* */)
    - Unquoted keys
    - export default { ... }
    - module.exports = { ... }
    - Trailing commas
    """
    
    def convert(self, source: str, from_case: str, to_case: str) -> str:
        """
        Convert all keys in source from one case to another.
        
        Args:
            source: JS/TS/JSON source code
            from_case: Source case ('auto', 'camel', 'pascal', 'snake', 'kebab')
            to_case: Target case ('camel', 'pascal', 'snake', 'kebab')
        
        Returns:
            Converted source code
        """
```

### Case Detection

```python
@staticmethod
def split_token(s: str) -> List[str]:
    """
    Split a token into words, detecting case style automatically.
    
    Examples:
        "userName"    → ["user", "Name"]
        "UserName"    → ["User", "Name"]
        "user_name"   → ["user", "name"]
        "user-name"   → ["user", "name"]
        "HTTPSConnection" → ["HTTPS", "Connection"]
    """
    # Handle kebab and snake
    s = s.replace('-', ' ').replace('_', ' ')
    
    # Handle camelCase/PascalCase
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)  # fooBar → foo Bar
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)  # HTTPServer → HTTP Server
    
    words = [w for w in s.split() if w]
    return words
```

### Conversion Functions

```python
def to_camel(self, s: str) -> str:
    """Convert to camelCase."""
    words = self.split_token(s)
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    # "user_name" → "userName"

def to_pascal(self, s: str) -> str:
    """Convert to PascalCase."""
    words = self.split_token(s)
    return ''.join(w.capitalize() for w in words)
    # "user_name" → "UserName"

def to_snake(self, s: str) -> str:
    """Convert to snake_case."""
    words = self.split_token(s)
    return '_'.join(w.lower() for w in words)
    # "userName" → "user_name"

def to_kebab(self, s: str) -> str:
    """Convert to kebab-case."""
    words = self.split_token(s)
    return '-'.join(w.lower() for w in words)
    # "userName" → "user-name"
```

**Analysis:**
- ✅ **Auto-Detection:** Detects source case automatically
- ✅ **Acronym Handling:** "HTTPSConnection" → "https-connection"
- ✅ **Reversible:** Converting back preserves meaning
- 🎯 **Use Case:** "Convert API response from snake_case to camelCase"

---

## Deep Dive: i18n System (`src/i18n/`)

### Package Structure

```
src/i18n/
├── __init__.py       (21 lines)  - Package exports
├── translator.py     (271 lines) - Translation engine
└── locales/
    ├── en.json       - English (default)
    ├── pt_BR.json    - Brazilian Portuguese
    ├── es.json       - Spanish
    ├── fr.json       - French
    ├── de.json       - German
    ├── zh.json       - Chinese
    └── ja.json       - Japanese
```

**Total:** 292 lines (7 supported languages)

---

### Translator (`translator.py`)

**Purpose:** Runtime language switching with Qt signals

#### Architecture

```
┌────────────────────────────────────────────┐
│      Translator (QObject Singleton)        │
│                                            │
│  load_translation(lang_code)               │
│    ├─ Read locales/{lang_code}.json       │
│    ├─ Store in self._translations         │
│    └─ Emit languageChanged signal         │
│                                            │
│  tr(key, **kwargs)                         │
│    ├─ Look up key in current translations │
│    ├─ Fallback to English if missing      │
│    ├─ Format with kwargs (f-string style) │
│    └─ Return translated string            │
│                                            │
│  Switch Language:                          │
│    translator.languageChanged.connect()    │
│    → MainWindow._on_language_changed()     │
│    → Update all UI strings                │
└────────────────────────────────────────────┘
```

#### Usage

```python
from src.i18n import tr, tooltip_tr, switch_language

# Translate UI strings
window_title = tr("app.title")  # "Clarify"
button_text = tr("btn.search")   # "Search"

# With parameters
message = tr("msg.files_found", count=42)  
# English: "Found 42 files"
# Portuguese: "Encontrados 42 arquivos"

# Tooltips
tooltip = tooltip_tr("tooltip.search_case_sensitive")

# Switch language at runtime
switch_language("pt_BR")  # Changes entire UI to Portuguese
```

#### Translation File Format

```json
{
  "app": {
    "title": "Clarify",
    "version": "Version {version}"
  },
  "menu": {
    "file": "File",
    "edit": "Edit",
    "tools": "Tools"
  },
  "btn": {
    "search": "Search",
    "replace": "Replace",
    "cancel": "Cancel"
  },
  "msg": {
    "files_found": "Found {count} files",
    "operation_complete": "Operation completed successfully"
  },
  "tooltip": {
    "search_case_sensitive": "Enable case-sensitive search"
  }
}
```

**Key Features:**
- ✅ **Nested Keys:** Organized by category (`app.title`, `menu.file`)
- ✅ **Parameterization:** `{count}` placeholders replaced at runtime
- ✅ **Fallback:** Missing translations fall back to English
- ✅ **Hot Reload:** Change language without restarting app
- 🎯 **Signal Integration:** Qt signal/slot updates entire UI instantly

**Analysis:**
- ✅ **7 Languages:** English, Portuguese, Spanish, French, German, Chinese, Japanese
- ✅ **Professional:** Follows i18n best practices
- ✅ **Extensible:** Add new language = add new JSON file
- 🎯 **Completeness:** ~300 keys translated per language

---

## Specialized Modules Overview

### 1. JSON Translation (`src/translators/`)

**Files:**
- `json_translate_helpers.py` (15 KB)
- `__init__.py` (960 bytes)

**Purpose:** Translate text values in JSON using dictionary

**Example:**

```python
# Dictionary (dict.json)
{
  "Hello": "Hola",
  "World": "Mundo",
  "Good morning": "Buenos días"
}

# Input JSON
{
  "greeting": "Hello",
  "message": "Good morning"
}

# Output JSON
{
  "greeting": "Hola",
  "message": "Buenos días"
}
```

**Features:**
- Scope support (translate only specific paths)
- Placeholder protection (don't translate `{variables}`)
- Masked content (protect regex patterns, code snippets)

---

### 2. Google Translate Integration (`src/translation/`)

**File:** `google_translate.py` (9.8 KB)

**Purpose:** Integrate Google Translate API for translation

**Features:**
- Auto-detect source language
- Translate to 100+ languages
- Batch translation
- Rate limiting
- Error handling (network failures, API limits)

**Usage:**

```python
from src.translation.google_translate import GoogleTranslator

translator = GoogleTranslator(api_key="YOUR_API_KEY")
result = translator.translate("Hello, world!", target_lang="es")
# Result: "¡Hola, mundo!"
```

---

### 3. Code-Aware Translator (`src/processors/`)

**File:** `code_aware_translator.py` (399 lines)

**Purpose:** Translate comments/strings in code without breaking syntax

**Features:**
- Detect code vs text
- Preserve code structure
- Translate only comments and strings
- Language detection (Python, JS, TS, etc.)

**Example:**

```python
# Input (English comments in Spanish code)
def calcular_suma(a, b):
    # Calculate the sum of two numbers
    return a + b

# Output (Spanish comments)
def calcular_suma(a, b):
    # Calcular la suma de dos números
    return a + b
```

---

## Common Patterns Across Utilities

### Pattern 1: Graceful Degradation

**Example:** `read_text()` with encoding fallback

```python
def read_text(path: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")
```

**Benefits:**
- ✅ Never crashes on encoding errors
- ✅ Handles legacy files
- ✅ Replaces invalid chars instead of failing

---

### Pattern 2: Optional Dependencies

**Example:** PySide6 import handling

```python
try:
    from PySide6.QtCore import Qt
except ImportError:
    Qt = None  # CLI mode works without Qt
```

**Benefits:**
- ✅ CLI works without GUI libraries
- ✅ Lighter Docker images
- ✅ Testable in CI without X11

---

### Pattern 3: Privacy Protection

**Example:** Error handler stripping paths

```python
def _strip_sensitive_paths(self, text: str) -> str:
    # /home/username/ → ~/
    text = re.sub(r'/home/[^/]+/', '~/', text)
    return text
```

**Benefits:**
- ✅ No usernames in crash reports
- ✅ No absolute paths leaked
- ✅ GDPR-friendly

---

### Pattern 4: Flexible Input Formats

**Example:** TypeScript utilities

```python
def load_ts_object(path: str) -> dict:
    """
    Load from:
    - export default { ... }
    - module.exports = { ... }
    - const x = { ... }
    - Pure JSON
    """
```

**Benefits:**
- ✅ Works with multiple export styles
- ✅ No manual format conversion needed
- ✅ Developer-friendly (just works)

---

## Performance Considerations

### 1. File Walking Generators

**Pattern:**

```python
def walk_files(...) -> Iterator[str]:
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            yield path  # Yield instead of append to list
```

**Benefits:**
- ✅ Memory-efficient (one file at a time)
- ✅ Early termination possible
- ✅ Works with millions of files

---

### 2. Lazy Import in Extractors

**Pattern:**

```python
# Don't import heavy dependencies at module level
def extract_jsx_params(source: str):
    from .jsx_parser import JSXParser  # Import only when needed
    parser = JSXParser()
    return parser.extract(source)
```

**Benefits:**
- ✅ Faster startup time
- ✅ Smaller memory footprint
- ✅ Conditional feature loading

---

### 3. Caching in Update Checker

**Pattern:**

```python
# Check for updates max once per day
last_check = settings.get("last_update_check")
if (datetime.now() - last_check).days < 1:
    return  # Skip check
```

**Benefits:**
- ✅ Reduces API calls
- ✅ Respects GitHub rate limits
- ✅ Better user experience (no delays)

---

## Utility Function Catalog

### File Operations

| Function | Module | Purpose |
|----------|--------|---------|
| `walk_files()` | file_utils | Recursive file traversal with filters |
| `read_text()` | file_utils | Safe text reading (UTF-8 fallback) |
| `write_text()` | file_utils | Write with auto-create directories |
| `safe_backup_file()` | file_utils | Create .bak file once |

### Text Processing

| Function | Module | Purpose |
|----------|--------|---------|
| `parse_exclusion_patterns()` | text_utils | Parse glob patterns |
| `mask_exclusions()` | text_utils | Protect content from replacement |
| `unmask_exclusions()` | text_utils | Restore protected content |
| `compile_value_union_regex()` | text_utils | Create regex from value list |

### TypeScript Handling

| Function | Module | Purpose |
|----------|--------|---------|
| `load_ts_object()` | ts_utils | Load TS/JS object as Python dict |
| `dump_ts_object()` | ts_utils | Save Python dict as TS/JS object |
| `strip_export_default()` | ts_utils | Remove export statements |
| `to_json_ish()` | ts_utils | Convert loose JS to valid JSON |

### Error Handling

| Function | Module | Purpose |
|----------|--------|---------|
| `install_crash_handler()` | error_handler | Global exception handler |
| `CrashHandler.handle_errors()` | error_handler | Context manager for errors |
| `install_error_reporter()` | error_reporter | Error dialog UI |

### Logging

| Function | Module | Purpose |
|----------|--------|---------|
| `get_logger()` | logger | Get logger instance |
| `ColoredFormatter` | logger | ANSI colored console output |

---

## Import Tree Analysis: Utilities

### Dependency Map

```
LEAF (Pure Utilities)
    ├── file_utils       → No dependencies (os, shutil only)
    ├── text_utils       → No dependencies (re only)
    ├── ts_utils         → Uses: file_utils, text_utils
    ├── logger           → No dependencies (logging, pathlib)
    └── normalization    → No dependencies (re only)

LEAF (Extractors)
    ├── extractor        → No cross-dependencies
    ├── generic_parser   → Uses: extractor
    └── jsx_parser       → Uses: extractor

LEAF (Converters)
    └── case_converter   → No dependencies (re, json only)

LEAF (i18n)
    ├── translator       → Uses: Qt (QObject, Signal)
    └── JSON files       → No dependencies

BRANCH (Error Handling)
    ├── error_handler    → Uses: logger (minimal)
    └── error_reporter   → Uses: Qt (for dialogs)
```

**Key Observation:**
- ✅ **Minimal Dependencies:** Utilities mostly use standard library
- ✅ **No Circular Imports:** Clear dependency direction
- ✅ **Leaf Pattern:** Most are pure functions (no state)

---

## Design Patterns Summary

### 1. **Singleton Pattern** (Logger, Translator)
- One instance shared across app
- Thread-safe initialization
- Global access via `get_logger()`, `get_translator()`

### 2. **Strategy Pattern** (Case Converters)
- Multiple conversion strategies
- Pluggable (add new case style easily)
- Dict of functions: `{'camel': to_camel, 'snake': to_snake}`

### 3. **Template Method Pattern** (Extractors)
- Base `Extractor` class defines algorithm
- Subclasses (`JSXParser`) implement details
- Reusable extraction workflow

### 4. **Fallback Pattern** (Encoding, Import)
- Try primary approach
- Fall back to alternative on failure
- Never crash (graceful degradation)

### 5. **Generator Pattern** (File Walking)
- Yield items one at a time
- Memory-efficient
- Lazy evaluation

---

## Insights & Learnings

### 1. **Utilities Are Pure LEAFs**

✅ Most utilities are pure functions (input → output)  
✅ Minimal dependencies (mostly standard library)  
✅ Easy to test (deterministic, no state)

**Benefit:** Can use utilities anywhere (CLI, GUI, tests)

---

### 2. **Logging is Professional**

✅ File rotation (prevents disk fill)  
✅ Colored console (easy debugging)  
✅ Contextual info (module, line number)  
✅ Environment config (CLARIFY_LOG_LEVEL)

**Benefit:** Production-ready logging system

---

### 3. **Error Handling is Privacy-Aware**

✅ Strips usernames from crash reports  
✅ Opt-in crash reporting (default: local only)  
✅ Clear error messages (not raw stack traces)

**Benefit:** GDPR-compliant, user-friendly

---

### 4. **i18n is First-Class**

✅ 7 languages supported  
✅ ~300 translated keys  
✅ Hot reload (change language instantly)  
✅ Parameterization (`{count}` in translations)

**Benefit:** International audience ready

---

### 5. **Extractors Handle Real-World Code**

✅ JSX/TSX parsing without full AST  
✅ Handle comments, type annotations  
✅ Multiple export formats

**Benefit:** Works with messy real-world code

---

### 6. **Case Converter is Smart**

✅ Auto-detects source case  
✅ Handles acronyms (HTTPSConnection)  
✅ Reversible conversions

**Benefit:** Automated code refactoring possible

---

### 7. **TypeScript Support is Extensive**

✅ Load TS/JS objects as Python dicts  
✅ Handle export statements  
✅ Convert loose syntax to valid JSON

**Benefit:** Seamless integration with TS projects

---

## Questions Answered

### Q1: What utility functions are available?

**A:** 
- **File:** walk_files, read_text, write_text, safe_backup_file
- **Text:** parse_exclusion_patterns, mask/unmask
- **TS:** load_ts_object, dump_ts_object
- **Logging:** get_logger (colored, rotating files)
- **Errors:** install_crash_handler (privacy-aware)

---

### Q2: How does logging work?

**A:**
1. `get_logger(__name__)` returns logger instance
2. Logs to file (`~/.clarify/logs/clarify.log`) AND console
3. File rotation: 10 MB max, keep 5 backups
4. Colored console output (green=INFO, red=ERROR)
5. Environment var `CLARIFY_LOG_LEVEL` overrides default

---

### Q3: How does i18n work?

**A:**
1. Translations stored in `src/i18n/locales/{lang}.json`
2. `tr(key)` looks up translation in current language
3. `switch_language("pt_BR")` changes language
4. Signal emitted → MainWindow updates all UI strings
5. Fallback to English if key missing

---

### Q4: How does error handling work?

**A:**
1. `install_crash_handler()` at app startup
2. Sets `sys.excepthook` to custom handler
3. Catches unhandled exceptions
4. Strips sensitive paths (privacy)
5. Shows user-friendly dialog
6. Logs to crash file
7. Optional: send to GitHub (opt-in only)

---

### Q5: What's the import tree role of utilities?

**A:**
- **Utilities:** LEAF (pure functions, no business logic)
- **Extractors:** LEAF (parse, no orchestration)
- **Converters:** LEAF (transform, no state)
- **Used by:** Core, Managers, GUI (everything uses utilities)

Utilities are the FOUNDATION (lowest level, no dependencies on app logic)

---

## Next Steps for Session 5

**Focus:** Synthesis & Complete Understanding  
**Target:** Create comprehensive code map, identify patterns, document architecture  
**Deliverables:**
- Complete codebase map (ROOT → BRANCH → LEAF)
- Design patterns catalog
- Key insights & learnings
- Development workflow understanding
- Extension points for new features

**Session Type:** Synthesis (connect all sessions)  
**Estimated Time:** 1 hour

---

## Appendix: Module Statistics

### Utilities Breakdown

```
logger.py             329 lines  (Logging system)
error_handler.py      471 lines  (Crash handling)
file_finder.py        417 lines  (Advanced search)
update_checker.py     286 lines  (Version checking)
error_reporter.py     255 lines  (Error dialogs)
normalization.py      129 lines  (Data normalization)
advanced_conditions   105 lines  (Complex filters)
text_utils.py          93 lines  (Text processing)
ts_utils.py            74 lines  (TypeScript handling)
file_utils.py          67 lines  (File I/O)
stats_formatter.py     60 lines  (Statistics)
__init__.py            18 lines  (Exports)
────────────────────────────────
TOTAL:              2,304 lines
```

### Extractors Breakdown

```
jsx_parser.py        560 lines  (JSX/TSX parsing)
extractor.py         482 lines  (Base extractor)
generic_parser.py     90 lines  (Generic extraction)
__init__.py           14 lines  (Exports)
────────────────────────────────
TOTAL:             1,146 lines
```

### Specialized Modules

```
case_converter.py              437 lines
json_translate_helpers.py      ~400 lines
google_translate.py            ~250 lines
code_aware_translator.py       399 lines
translator.py                  271 lines
────────────────────────────────
TOTAL:                       ~1,750 lines
```

---

## Session Completion

**Status:** ✅ COMPLETE  
**Time Spent:** 1.5 hours  
**Modules Analyzed:** ~40 files, ~6,500 lines  
**Understanding Level:** SCAN (catalog complete, patterns identified)  
**Next Session:** Synthesis - Complete codebase understanding

---

**Date Completed:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Protocol Compliance:** SIMPLICITY_PROTOCOL_3.md Step 1.3 ✅  
**Import Tree Progress:** ROOT + BRANCH + LEAF layers complete 🌳

**Total Code Study:** 157+ files, ~48,000+ lines analyzed across 4 sessions
