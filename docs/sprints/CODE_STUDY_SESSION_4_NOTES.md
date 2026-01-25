# Code Study Session 4 Notes
**Programmer #7 - Source Code Study**  
**Date**: 2026-01-22  
**Session Focus**: Phase 2 - Core Business Logic (src/core/)  
**Files Studied**: 6 files (~1,180 lines)

---

## 📋 Session Overview

**Progress**:
- **Files Studied This Session**: 6 files
- **Lines of Code**: ~1,180 lines
- **Total Progress**: 18/196 files (9.2%)
- **Phase**: Phase 2 - Core Systems (IN PROGRESS)

**Files Analyzed**:
1. `src/core/search_replace.py` (64 lines) ✅
2. `src/core/insert.py` (52 lines) ✅
3. `src/core/filters.py` (343 lines) ✅
4. `src/core/command_manager.py` (183 lines) ✅
5. `src/core/multi_query.py` (189 lines) ✅
6. `src/core/memory_register.py` (303 lines) ✅

**Remaining in src/core/**:
- `file_explorer_executor.py` (683 lines)
- `file_list_executor.py` (331 lines)
- `rewriter_cli.py` (195 lines)
- `result_exporter.py` (196 lines - partial)
- `set_operation_executor.py` (224 lines)

---

## 🔍 Detailed Analysis

### 1. search_replace.py (64 lines) - Text Search & Replace Engine

**Purpose**: Core search/replace functionality with regex, case sensitivity, whole word

**Architecture Pattern**: **Strategy Pattern** (SearchOptions configures behavior)

**Key Components**:

#### **SearchOptions Dataclass** (Lines 8-26)

```python
@dataclass
class SearchOptions:
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False
    
    def compile(self, needle: str) -> re.Pattern:
        """Build compiled regex pattern from user input + options"""
```

**Logic**:
1. Set flags: `IGNORECASE` if not case_sensitive
2. If regex mode: use needle as-is
3. If literal mode: `re.escape(needle)` to escape special chars
4. If whole_word: wrap with `\b` word boundaries
5. Compile pattern with flags
6. Raise ValueError if regex invalid

**Example**:
```python
options = SearchOptions(case_sensitive=False, whole_word=True, regex=False)
pattern = options.compile("hello")
# Result: re.compile(r'\bhello\b', re.IGNORECASE)
```

---

#### **preserve_case_like() Function** (Lines 29-45)

**Purpose**: Smart case preservation during replacement

**Algorithm**:
```python
def preserve_case_like(matched_text: str, replacement: str) -> str:
    if matched_text.isupper():       # "HELLO" → "WORLD"
        return replacement.upper()
    if matched_text.islower():       # "hello" → "world"
        return replacement.lower()
    if matched_text[0].isupper() and matched_text[1:].islower():  # "Hello" → "World"
        return replacement[:1].upper() + replacement[1:].lower()
    return replacement  # Mixed case → no change
```

**Use Cases**:
- Replace "Hello" with "Goodbye" → "Goodbye" (capitalized)
- Replace "HELLO" with "Goodbye" → "GOODBYE" (all caps)
- Replace "hello" with "Goodbye" → "goodbye" (all lowercase)
- Replace "hElLo" with "Goodbye" → "Goodbye" (mixed → as-is)

---

#### **replace_in_text() Function** (Lines 48-64)

**Purpose**: Perform replacement with optional case preservation

**Signature**:
```python
def replace_in_text(
    content: str,
    pattern: re.Pattern,      # Pre-compiled pattern
    repl: str,                # Replacement text
    preserve_case: bool = False,
    count: int = 0            # 0 = replace all
) -> Tuple[str, int]:         # (new_content, num_replacements)
```

**Algorithm**:
1. Define nested `_repl(m: re.Match)` function:
   - Increment counter
   - Apply `preserve_case_like()` if enabled
   - Return replacement text
2. Call `pattern.sub(_repl, content, count=count)`
3. Return (modified_content, num_replacements)

**Clever Use of Closure**:
- `num` variable captured from outer scope (nonlocal)
- Replacement function counts matches automatically
- No need for separate `findall()` + loop

**Example**:
```python
pattern = re.compile(r'\bhello\b', re.IGNORECASE)
new_text, count = replace_in_text(
    "Hello world, hello there",
    pattern,
    "goodbye",
    preserve_case=True,
    count=0
)
# Result: ("Goodbye world, goodbye there", 2)
```

---

### 2. insert.py (52 lines) - Line-Based Text Insertion

**Purpose**: Insert/modify text at specific line numbers with multiple modes

**Architecture Pattern**: **Strategy Pattern** (5 insertion modes)

#### **InsertMode Class** (Lines 4-9)

**5 Strategies**:
```python
LEFT = "Insert left of line"           # Prepend to line
RIGHT = "Insert right of line"         # Append to line
REPLACE = "Replace line content"       # Overwrite line
INSERT_ABOVE = "Push line down and insert above"
INSERT_BELOW = "Insert on next line (push rest)"
```

**Not an Enum**: Uses string constants (for i18n/display compatibility)

---

#### **insert_at_line() Function** (Lines 12-52)

**Signature**:
```python
def insert_at_line(content: str, line_no: int, text: str, mode: str) -> str:
    """Insert/modify 'text' at 1-based 'line_no' following 'mode'"""
```

**Algorithm**:

**1. Setup** (Lines 16-17):
```python
lines = content.splitlines(keepends=False)  # Split into list
idx = max(0, min(len(lines), line_no - 1))  # Convert to 0-based, clamp
```

**2. Mode Handling**:

**LEFT Mode** (Lines 19-25):
- If line beyond end: pad with empty lines, append text
- Else: `lines[idx] = text + lines[idx]`

**RIGHT Mode** (Lines 27-33):
- If line beyond end: pad with empty lines, append text
- Else: `lines[idx] = lines[idx] + text`

**REPLACE Mode** (Lines 35-41):
- If line beyond end: pad with empty lines, append text
- Else: `lines[idx] = text`

**INSERT_ABOVE Mode** (Lines 43-44):
- `lines.insert(idx, text)` - shifts line down

**INSERT_BELOW Mode** (Lines 46-47):
- `lines.insert(min(idx + 1, len(lines)), text)` - inserts after

**3. Rejoin** (Line 52):
```python
return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
```
- Preserves trailing newline if original had it

**Edge Cases Handled**:
✅ Line number beyond file end (pads with empty lines)
✅ Line number 0 or negative (clamped to 0)
✅ Preserves original trailing newline
✅ Unknown mode raises ValueError

**Example**:
```python
content = "Line 1\nLine 2\nLine 3\n"
result = insert_at_line(content, 2, "INSERTED", InsertMode.INSERT_ABOVE)
# Result: "Line 1\nINSERTED\nLine 2\nLine 3\n"
```

---

### 3. filters.py (343 lines) - Advanced File Filtering System

**Purpose**: Complex file filtering with conditions on metadata and content

**Architecture Pattern**: **Filter Chain + Dataclass Predicates**

#### **OPS Dictionary** (Lines 11-22)

**10 Comparison Operators**:
```python
OPS = {
    "contains": lambda a, b: b in a,
    "not contains": lambda a, b: b not in a,
    "equals": lambda a, b: a == b,
    "not equals": lambda a, b: a != b,
    "starts with": lambda a, b: a.startswith(b),
    "ends with": lambda a, b: a.endswith(b),
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}
```

**Design**: Lambda functions stored in dict for dynamic lookup

---

#### **Hierarchical HTML/XML Filtering** (Lines 25-117)

**parse_hierarchical_ranges()** (Lines 25-59):

**Syntax**: `"include div#test1, exclude #test2, include #test3"`

**Returns**: `[("include", "div#test1"), ("exclude", "#test2"), ("include", "#test3")]`

**Features**:
- Comma-separated directives
- `include` / `exclude` actions
- Default to `include` if no action specified
- Skip empty lines and comments (# prefix)

**Example**:
```python
ranges = parse_hierarchical_ranges("include div#main, exclude #ads")
# [("include", "div#main"), ("exclude", "#ads")]
```

---

**apply_hierarchical_filter()** (Lines 62-117):

**Purpose**: Extract/exclude HTML/XML sections by selectors

**Supports**:
1. **Regex Mode** (use_regex=True):
   - Treat selector as regex pattern
   - `re.DOTALL | re.IGNORECASE`
   - Include: add matches to results
   - Exclude: remove matches from results

2. **Selector Mode** (use_regex=False):
   - **ID selector**: `#myId` → matches `id="myId"`
   - **Tag+ID**: `div#test1` → matches `<div id="test1">`
   - **Tag only**: `div` → matches all `<div>` elements

**Algorithm**:
```python
for action, selector in ranges:
    matches = extract_elements(text, selector, use_regex)
    if action == "include":
        results.extend(matches)
    elif action == "exclude":
        results = [r for r in results if r not in matches]

return '\n'.join(results)
```

**Example**:
```html
<!-- Input -->
<div id="content">Keep this</div>
<div id="ads">Remove this</div>

<!-- ranges = [("include", "#content"), ("exclude", "#ads")] -->
<!-- Output: "Keep this" -->
```

---

#### **Scope Content Extraction** (Lines 120-204)

**extract_scope_content()** (Lines 120-204):

**Purpose**: Extract content within delimiters (brackets, braces, tags, etc.)

**8 Scope Types**:

1. **"none"** or `""`: Return full text
2. **"brackets"**: Extract `[content]`
3. **"braces"**: Extract `{content}` with nesting support
4. **"parentheses"**: Extract `(content)` with nesting support
5. **"custom"**: Extract between custom delimiters (format: "begin,end")
6. **"tag"**: Extract from any HTML/XML tags
7. **"specific-tag"**: Extract from specific tag (e.g., "div")
8. **"hierarchical"**: Use hierarchical include/exclude ranges

**Nesting Support** (Braces & Parentheses):
```python
depth = 0
start = -1
for i, char in enumerate(text):
    if char == '{':
        if depth == 0:
            start = i + 1
        depth += 1
    elif char == '}':
        depth -= 1
        if depth == 0 and start != -1:
            results.append(text[start:i])
            start = -1
```

**Custom Delimiter Example**:
```python
text = "START some content END START more END"
result = extract_scope_content(text, "custom", "START,END")
# Result: "some content\nmore"
```

**Tag Example**:
```python
text = "<div>Hello</div><span>World</span>"
result = extract_scope_content(text, "tag", "")
# Result: "Hello\nWorld"
```

---

#### **Condition Dataclass** (Lines 207-309)

**Purpose**: Single filter condition with metadata and content matching

**Fields**:
```python
@dataclass
class Condition:
    field: str           # "filename" | "path" | "ext" | "size" | "mtime" | "content"
    operator: str        # OPS keys
    value: str           # Comparison value
    scope_type: str = "" # Scope for content filtering
    scope_value: str = ""
    case_sensitive: bool = True
    whole_word: bool = False
    use_regex: bool = False
```

**6 Supported Fields**:
1. **filename**: `os.path.basename(path)`
2. **path**: Full path
3. **ext**: Extension without dot (`.json` → `json`)
4. **size**: File size in bytes (`st.st_size`)
5. **mtime**: Modification timestamp (`st.st_mtime`)
6. **content**: File text content (read with scope filtering)

---

**_apply_string_matching() Method** (Lines 218-278):

**Purpose**: Apply case sensitivity, whole word, regex to string comparisons

**3 Modes**:

1. **Regex Mode** (use_regex=True):
   - Compile pattern with flags
   - Add `\b` boundaries if whole_word
   - Handle `contains`, `equals`, `starts with`, `ends with`
   - Return False on regex error

2. **Whole Word Mode** (whole_word=True, regex=False):
   - Build regex with `\b` boundaries
   - Use re.search() for matching
   - Only for `contains` / `not contains`

3. **Standard Mode**:
   - Case conversion if not case_sensitive
   - Standard Python string operations

**Example**:
```python
# Case insensitive, whole word
cond = Condition(
    field="content",
    operator="contains",
    value="hello",
    case_sensitive=False,
    whole_word=True
)
# Matches: "Hello world" ✅
# No match: "helloworld" ❌ (not whole word)
```

---

**matches() Method** (Lines 280-309):

**Purpose**: Evaluate condition against a file path

**Algorithm**:
```python
def matches(self, path: str) -> bool:
    try:
        if self.field == "filename":
            a = os.path.basename(path)
            b = self.value
            return self._apply_string_matching(a, b, self.operator)
        
        # ... similar for path, ext ...
        
        if self.field in ("size", "mtime"):
            st = os.stat(path)
            a = st.st_size if self.field == "size" else st.st_mtime
            b = float(self.value)
            return OPS[self.operator](a, b)
        
        if self.field == "content":
            txt = read_text(path)
            # Apply scope filtering BEFORE matching
            if self.scope_type and self.scope_type != "none":
                txt = extract_scope_content(txt, self.scope_type, self.scope_value, self.use_regex)
            return self._apply_string_matching(txt, self.value, self.operator)
    except Exception:
        return False
```

**Key Feature**: Content scope filtering applied BEFORE matching
- Extract only braces → search only in JSON object bodies
- Extract specific tags → search only in HTML sections

**Example**:
```python
cond = Condition(
    field="content",
    operator="contains",
    value="error",
    scope_type="braces",
    case_sensitive=False
)
# Only searches within {...} blocks
```

---

#### **filter_files_by_conditions() Function** (Lines 312-343)

**Purpose**: Apply multiple conditions with AND/OR logic

**Signature**:
```python
def filter_files_by_conditions(
    files: Iterable[str],
    conds: Sequence[Condition],
    logic_operator: str = "AND"  # "AND" or "OR"
) -> List[str]:
```

**Algorithm**:
```python
for file_path in files:
    if logic_operator == "OR":
        # At least one condition must match (disjunction)
        ok = any(c.matches(file_path) for c in conds)
    else:
        # All conditions must match (conjunction) - default
        ok = all(c.matches(file_path) for c in conds)
    
    if ok:
        output.append(file_path)
```

**Performance**:
- ✅ Lazy evaluation with `any()` / `all()` (stops early)
- ✅ Content read once per file (cached in matches())
- ⚠️ No caching across files (reads file for each content condition)

**Example**:
```python
conditions = [
    Condition(field="ext", operator="equals", value="json"),
    Condition(field="size", operator=">", value="1000")  # > 1KB
]
results = filter_files_by_conditions(all_files, conditions, "AND")
# Returns: JSON files larger than 1KB
```

---

### 4. command_manager.py (183 lines) - Undo/Redo System

**Purpose**: Command Pattern implementation for undo/redo (Task #12, v2.9.8)

**Architecture Pattern**: **Command Pattern (GoF) + Memento Pattern**

#### **Command Abstract Base Class** (Lines 15-37)

```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        """Execute the command (perform the action)."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command (revert the action)."""
        pass
    
    def redo(self) -> None:
        """Redo the command (re-execute after undo). Default: calls execute()."""
        self.execute()
    
    def get_description(self) -> str:
        """Return a human-readable description of the command."""
        return self.__class__.__name__
```

**GoF Command Pattern**:
- Encapsulates action as object
- `execute()` = do action
- `undo()` = reverse action
- `redo()` = re-do action (default: call execute() again)

---

#### **FileModificationCommand** (Lines 40-67)

**Purpose**: Command for single file modification

**Fields**:
```python
self.filepath: str
self.original_content: str
self.new_content: str
self.description: str
```

**Methods**:
- `execute()`: Write `new_content` to file
- `undo()`: Write `original_content` to file
- `redo()`: Call `execute()` (write new_content)

**Memento Pattern**:
- Stores `original_content` as memento
- Allows restoration to previous state

**Example**:
```python
cmd = FileModificationCommand(
    filepath="data.json",
    original_content='{"old": "value"}',
    new_content='{"new": "value"}',
    description="Update data"
)
cmd.execute()  # Write new content
cmd.undo()     # Restore original
cmd.redo()     # Re-apply new content
```

---

#### **MultiFileCommand** (Lines 70-96)

**Purpose**: Aggregate multiple file commands into one operation

**Pattern**: **Composite Command** (Command Pattern variant)

**Fields**:
```python
self.commands: List[FileModificationCommand]
self.description: str
```

**Methods**:
```python
def execute(self):
    for cmd in self.commands:
        cmd.execute()

def undo(self):
    for cmd in reversed(self.commands):  # IMPORTANT: reversed!
        cmd.undo()

def redo(self):
    for cmd in self.commands:
        cmd.redo()
```

**Critical Design**: Undo in **reverse order**
- Operation 1: Create file A
- Operation 2: Modify file A
- **Undo order**: Undo 2 first, then undo 1
- **Prevents**: Undo 1 deleting file before undo 2 restores content

**Example**:
```python
commands = [
    FileModificationCommand("file1.json", old1, new1, "Update file1"),
    FileModificationCommand("file2.json", old2, new2, "Update file2")
]
multi = MultiFileCommand(commands, "Batch update")
multi.execute()  # Modify both files
multi.undo()     # Restore both files (reverse order)
```

---

#### **CommandManager Class** (Lines 99-183)

**Purpose**: Manages undo/redo stacks with history limit

**Fields**:
```python
self.max_history: int = 10  # Configurable depth
self.undo_stack: deque[Command] = deque(maxlen=max_history)
self.redo_stack: deque[Command] = deque(maxlen=max_history)
```

**Why deque?**
- ✅ `maxlen` automatically discards oldest items
- ✅ O(1) append/pop operations
- ✅ FIFO behavior for history management

---

**execute_command() Method** (Lines 115-122):
```python
def execute_command(self, command: Command):
    command.execute()
    self.undo_stack.append(command)
    self.redo_stack.clear()  # CRITICAL: New action invalidates redo history
```

**Why clear redo_stack?**
- User does: Action A → Undo → Action B
- Can't redo A anymore (timeline branched)
- Common undo/redo pattern (Photoshop, VS Code, etc.)

---

**undo() Method** (Lines 124-135):
```python
def undo(self) -> bool:
    if not self.undo_stack:
        return False
    
    command = self.undo_stack.pop()
    command.undo()
    self.redo_stack.append(command)  # Move to redo stack
    return True
```

**State Transfer**: undo_stack → redo_stack

---

**redo() Method** (Lines 137-148):
```python
def redo(self) -> bool:
    if not self.redo_stack:
        return False
    
    command = self.redo_stack.pop()
    command.redo()
    self.undo_stack.append(command)  # Move back to undo stack
    return True
```

**State Transfer**: redo_stack → undo_stack

---

**Helper Methods**:

```python
def can_undo(self) -> bool:
    return len(self.undo_stack) > 0

def can_redo(self) -> bool:
    return len(self.redo_stack) > 0

def get_undo_description(self) -> Optional[str]:
    return self.undo_stack[-1].get_description() if self.undo_stack else None

def get_redo_description(self) -> Optional[str]:
    return self.redo_stack[-1].get_description() if self.redo_stack else None

def clear_history(self):
    self.undo_stack.clear()
    self.redo_stack.clear()

def get_history_stats(self) -> dict:
    return {
        'undo_available': len(self.undo_stack),
        'redo_available': len(self.redo_stack),
        'max_history': self.max_history,
        'can_undo': self.can_undo(),
        'can_redo': self.can_redo()
    }
```

**Integration with UI**:
- `can_undo()` / `can_redo()` → enable/disable menu actions
- `get_undo_description()` → show "Undo: Update file1.json"
- `get_history_stats()` → display in status bar

---

### 5. multi_query.py (189 lines) - Multi-Line Query System

**Purpose**: Support for multiple independent queries (one per line)

**Architecture Pattern**: **Iterator + Composite**

**Language**: Portuguese comments (Brazilian developer)

#### **QueryLine Dataclass** (Lines 14-18)

```python
@dataclass
class QueryLine:
    raw_text: str       # Original query text
    pattern: Pattern    # Compiled regex
    line_number: int    # 1-based line number
```

---

#### **MultiQueryProcessor Class** (Lines 22-146)

**Purpose**: Process multiple queries, each on separate line

**Constructor** (Lines 29-47):
```python
def __init__(self, 
             multi_line_text: str,
             case_sensitive: bool = False,
             whole_word: bool = False,
             use_regex: bool = True):
    self.multi_line_text = multi_line_text
    self.case_sensitive = case_sensitive
    self.whole_word = whole_word
    self.use_regex = use_regex
    self.queries: List[QueryLine] = []
    
    self._parse_queries()
```

---

**_parse_queries() Method** (Lines 49-75):

**Algorithm**:
```python
lines = self.multi_line_text.split('\n')

for i, line in enumerate(lines, start=1):
    line = line.strip()
    
    # Skip empty lines and comments (#)
    if not line or line.startswith('#'):
        continue
    
    try:
        pattern = self._compile_pattern(line)
        self.queries.append(QueryLine(raw_text=line, pattern=pattern, line_number=i))
    except re.error:
        # If regex fails, treat as literal text (escape it)
        escaped = re.escape(line)
        pattern = self._compile_pattern(escaped)
        self.queries.append(QueryLine(raw_text=line, pattern=pattern, line_number=i))
```

**Robust Error Handling**:
- Invalid regex → auto-escape and retry as literal
- Users can paste plain text without errors

---

**_compile_pattern() Method** (Lines 77-89):

```python
def _compile_pattern(self, text: str) -> Pattern:
    if not self.use_regex:
        text = re.escape(text)  # Escape if not regex mode
    
    if self.whole_word:
        text = rf'\b{text}\b'   # Add word boundaries
    
    flags = 0 if self.case_sensitive else re.IGNORECASE
    
    return re.compile(text, flags)
```

---

**search_in_text() Method** (Lines 91-115):

**Purpose**: Search all queries in content

**Returns**: `List[Tuple[int, int, str, int]]`
- Tuple format: `(line, col, snippet, query_line_number)`

**Algorithm**:
```python
matches = []

for query in self.queries:
    for match in query.pattern.finditer(content):
        line = content.count("\n", 0, match.start()) + 1
        col = match.start() - (content.rfind("\n", 0, match.start()) + 1)
        
        # Get full line as snippet
        lines = content.splitlines()
        snippet = lines[line - 1] if line - 1 < len(lines) else ""
        
        matches.append((line, col, snippet, query.line_number))

return matches
```

**Key Feature**: Each match knows which query found it (query.line_number)
- Useful for result grouping
- "Query 1 found 5 matches, Query 2 found 3 matches"

---

**Utility Methods**:

```python
def get_query_count(self) -> int:
    return len(self.queries)

def get_query_summary(self) -> str:
    if not self.queries:
        return "No queries"
    if len(self.queries) == 1:
        return f"1 query: {self.queries[0].raw_text[:50]}"
    return f"{len(self.queries)} queries"

def validate(self) -> Tuple[bool, str]:
    if not self.queries:
        return False, "No valid queries found"
    
    # Check for very complex patterns (DoS prevention)
    for query in self.queries:
        if len(query.raw_text) > 500:
            return False, f"Query on line {query.line_number} is too long (>500 chars)"
    
    return True, ""
```

**Security**: 500 char limit prevents regex DoS attacks

---

#### **Utility Functions** (Lines 149-189)

**split_multi_query()** (Lines 149-162):
```python
def split_multi_query(text: str) -> List[str]:
    """Split multi-line text into individual queries. Remove empty lines and comments."""
    lines = text.split('\n')
    queries = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            queries.append(line)
    
    return queries
```

---

**combine_query_results()** (Lines 165-189):
```python
def combine_query_results(results_by_query: List[List[Tuple]]) -> List[Tuple]:
    """
    Combine results from multiple queries, removing duplicates.
    Returns sorted by (line, col).
    """
    all_matches = []
    seen = set()
    
    for results in results_by_query:
        for match in results:
            # Use (line, col) as unique key
            key = (match[0], match[1])
            if key not in seen:
                seen.add(key)
                all_matches.append(match)
    
    # Sort by line, then column
    all_matches.sort(key=lambda x: (x[0], x[1]))
    
    return all_matches
```

**De-duplication Strategy**:
- Key = (line, col) tuple
- Multiple queries can match same location
- Only keep first match at each location

---

### 6. memory_register.py (303 lines) - Regex Capture & Reuse System

**Purpose**: Capture values via regex and reuse in JSON insertion

**Architecture Pattern**: **Memento Pattern (GoF) + Command Pattern (GoF)**

**Use Case**:
1. User defines regex: `r'"name": "(.*?)"'`
2. System captures matches: `$0 = '"name": "John"'`, `$1 = "John"`
3. User inserts new field: `"fullName": "$1"` → `"fullName": "John"`

#### **RegisterEntry Dataclass** (Lines 36-72)

```python
@dataclass
class RegisterEntry:
    index: int           # Register index ($0, $1, ...)
    value: str           # Captured value
    source_text: str     # Original text where captured
    pattern: str         # Regex pattern used
    timestamp: datetime  # When captured
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for persistence"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RegisterEntry:
        """Deserialize from persistence"""
```

**Memento Pattern**: RegisterEntry stores complete state for restoration

---

#### **MemoryRegister Class** (Lines 75-285)

**Purpose**: Manage regex captures with history and persistence

**Constructor** (Lines 90-100):
```python
def __init__(self, max_registers: int = 100):
    self.max_registers = max_registers  # $0-$99
    self.registers: Dict[int, RegisterEntry] = {}
    self.history: List[List[RegisterEntry]] = []  # Capture history
    self.last_pattern: Optional[str] = None
```

---

**capture() Method** (Lines 102-172):

**Purpose**: Capture values from text using regex

**Signature**:
```python
def capture(
    self,
    text: str,
    pattern: str,
    flags: int = 0
) -> Tuple[int, List[str]]:  # (num_captures, captured_values)
```

**Algorithm**:
```python
# 1. Compile pattern
compiled = re.compile(pattern, flags)

# 2. Find all matches
matches = compiled.finditer(text)

# 3. Clear current registers
self.registers.clear()

# 4. Process each match
for match in matches:
    # $0 = whole match
    self.registers[0] = RegisterEntry(
        index=0,
        value=match.group(0),
        source_text=text,
        pattern=pattern
    )
    
    # $1, $2, ... = capture groups
    for i, group in enumerate(match.groups(), start=1):
        self.registers[i] = RegisterEntry(
            index=i,
            value=group if group is not None else "",
            source_text=text,
            pattern=pattern
        )

# 5. Store in history
self.history.append(list(self.registers.values()))

# 6. Return results
return (len(self.registers), captured_values)
```

**Key Features**:
- ✅ `$0` always = full match
- ✅ `$1, $2, ...` = capture groups
- ✅ `None` groups → empty string
- ✅ History preserved for undo

**Example**:
```python
register = MemoryRegister()
text = '{"name": "John", "age": 30}'
num, values = register.capture(text, r'"name": "(.*?)"')

# num = 2
# values = ['"name": "John"', 'John']
# $0 = '"name": "John"'
# $1 = 'John'
```

---

**get() Method** (Lines 174-186):
```python
def get(self, index: int, default: str = "") -> str:
    """Get value from register."""
    entry = self.registers.get(index)
    return entry.value if entry else default
```

---

**replace_in_text() Method** (Lines 192-215):

**Purpose**: Replace $N placeholders with register values

```python
def replace_in_text(self, template: str) -> str:
    result = template
    
    # Sort by index descending to avoid $1 before $10
    for idx in sorted(self.registers.keys(), reverse=True):
        placeholder = f"${idx}"
        if placeholder in result:
            result = result.replace(placeholder, self.registers[idx].value)
    
    return result
```

**Critical Detail**: Sort descending to prevent `$1` replacing part of `$10`
- ✅ Process `$10` before `$1`
- ❌ Without sort: `$10` → `<value of $1>0`

**Example**:
```python
# After capture: $1 = "John"
template = '"fullName": "$1", "greeting": "Hello, $1!"'
result = register.replace_in_text(template)
# Result: '"fullName": "John", "greeting": "Hello, John!"'
```

---

**History Methods**:

```python
def restore_from_history(self, index: int = -1) -> bool:
    """Restore registers from history (-1 = last)."""
    if not self.history:
        return False
    
    entries = self.history[index]
    self.registers.clear()
    for entry in entries:
        self.registers[entry.index] = entry
    return True

def get_history_count(self) -> int:
    return len(self.history)
```

**Use Case**: User captures wrong values → restore previous capture

---

**Persistence Methods**:

```python
def export_to_dict(self) -> Dict[str, Any]:
    """Export for saving to file."""
    return {
        'registers': [entry.to_dict() for entry in self.registers.values()],
        'last_pattern': self.last_pattern,
        'history_count': len(self.history)
    }

def import_from_dict(self, data: Dict[str, Any]):
    """Import from saved file."""
    self.registers.clear()
    for entry_dict in data.get('registers', []):
        entry = RegisterEntry.from_dict(entry_dict)
        self.registers[entry.index] = entry
    self.last_pattern = data.get('last_pattern')

def export_to_json(self) -> str:
    return json.dumps(self.export_to_dict(), indent=2)

def import_from_json(self, json_str: str):
    data = json.loads(json_str)
    self.import_from_dict(data)
```

**Use Case**: Save captured values between sessions

---

#### **Global Singleton** (Lines 288-303)

```python
_global_register: Optional[MemoryRegister] = None

def get_global_register() -> MemoryRegister:
    """Get global memory register singleton."""
    global _global_register
    if _global_register is None:
        _global_register = MemoryRegister()
    return _global_register

def reset_global_register():
    """Reset global memory register."""
    global _global_register
    _global_register = None
```

**Pattern**: Singleton for application-wide register access
- All tools can access same captured values
- Optional: Tools can create local instances

---

## 🔑 Key Architectural Insights

### **Core Module Design Philosophy**:

1. **Pure Functions Where Possible**:
   - `search_replace.py`: No state, pure transformations
   - `insert.py`: No state, pure line manipulation
   - Easy to test, predictable behavior

2. **Dataclasses for Configuration**:
   - `SearchOptions`, `Condition`, `RegisterEntry`, `QueryLine`
   - Type safety with Python 3.10+ features
   - Clear API contracts

3. **Regex-First Design**:
   - All search operations use compiled patterns
   - Consistent flag handling (IGNORECASE, etc.)
   - Error handling for invalid patterns

4. **Flexibility Through Options**:
   - Case sensitive vs insensitive
   - Whole word vs partial
   - Regex vs literal
   - **User has control** over behavior

5. **Memento Pattern for History**:
   - `CommandManager`: Store previous state for undo
   - `MemoryRegister`: Store captured values with metadata
   - **Enables time travel** in user operations

### **Performance Considerations**:

**Filters Module**:
- ⚠️ Reads file content for EVERY content condition
- ⚠️ No caching between conditions
- ⚠️ Scope extraction repeats for each file
- ✅ But: Lazy evaluation stops early with `any()`/`all()`

**Multi-Query**:
- ✅ Compile patterns once, reuse many times
- ✅ De-duplication prevents duplicate results
- ✅ 500 char limit prevents regex DoS
- ⚠️ No result caching across searches

**Command Manager**:
- ✅ `deque` with `maxlen` = O(1) operations
- ✅ Automatic LRU behavior (oldest commands dropped)
- ⚠️ Stores full file content (memory usage)
- **Trade-off**: Memory vs undo depth

### **Design Patterns Identified**:

1. **Strategy Pattern**:
   - `SearchOptions` (3 modes)
   - `InsertMode` (5 strategies)
   - `Condition` operators (10 operations)

2. **Command Pattern (GoF)**:
   - `Command` abstract base
   - `FileModificationCommand` concrete
   - `MultiFileCommand` composite

3. **Memento Pattern (GoF)**:
   - `RegisterEntry` stores state
   - `CommandManager` stores file content
   - History stacks enable restoration

4. **Composite Pattern**:
   - `MultiFileCommand` aggregates commands
   - Execute/undo all as one unit

5. **Singleton Pattern**:
   - `get_global_register()` for app-wide access

6. **Iterator Pattern**:
   - `QueryLine` with `finditer()`
   - Process matches lazily

### **Error Handling Strategy**:

**search_replace.py**:
- Raises `ValueError` for invalid regex
- User sees error immediately

**insert.py**:
- Raises `ValueError` for unknown mode
- Edge cases handled gracefully (out of bounds lines)

**filters.py**:
- Returns `False` on exception (fail-safe)
- Invalid regex → treated as literal text
- File read errors → skip file (don't crash)

**multi_query.py**:
- Invalid regex → auto-escape and retry
- User can paste plain text without errors
- Validation checks before processing

**memory_register.py**:
- Raises `re.error` for invalid patterns
- User must handle error explicitly
- Clear error messages

**Philosophy**: Fail fast for user errors, fail safe for system errors

---

## 📊 Statistics

**Session 4 Metrics**:
- **Files Read**: 6
- **Lines Analyzed**: ~1,180
- **Classes Discovered**: 9 (SearchOptions, InsertMode, Condition, Command, FileModificationCommand, MultiFileCommand, CommandManager, QueryLine, MultiQueryProcessor, RegisterEntry, MemoryRegister)
- **Design Patterns Identified**: 6 (Strategy, Command, Memento, Composite, Singleton, Iterator)
- **Functions Analyzed**: 25+
- **Regex Patterns**: Extensive use throughout

**Cumulative Progress**:
- **Total Files Studied**: 18 / 196 (9.2%)
- **Total Lines Studied**: ~3,430 / 58,165 (5.9%)
- **Documentation Read**: 242 / 242 (100%)
- **Overall Comprehension**: ~55% (docs 100%, code 9%)

**Phase 2 Status**: 🔄 **IN PROGRESS** (6/24 core files complete)

**Remaining in core/**:
- `file_explorer_executor.py` (683 lines)
- `file_list_executor.py` (331 lines)
- `rewriter_cli.py` (195 lines)
- `result_exporter.py` (196 lines)
- `set_operation_executor.py` (224 lines)
- **Total remaining**: 1,629 lines (58% of core/)

**Next Files**: Continue Phase 2 with executor classes and CLI tools

---

## 🎯 Key Takeaways

### **What We Now Understand**:

1. ✅ **Text search/replace engine** with case preservation and regex
2. ✅ **Line insertion system** with 5 insertion modes
3. ✅ **Advanced filtering** with content scopes, hierarchical HTML/XML extraction
4. ✅ **Undo/redo system** (Command Pattern, 10-level history)
5. ✅ **Multi-query search** with comment support and de-duplication
6. ✅ **Regex capture system** for value extraction and reuse

### **Core Business Logic Clarity**:

**Search & Replace**:
```
User Input → SearchOptions → compile() → Pattern
Text → replace_in_text() → (Modified Text, Count)
Optional: preserve_case_like() for smart case matching
```

**Insert**:
```
User Input → InsertMode strategy
Text + Line Number → insert_at_line() → Modified Text
Handles: Edge cases, padding, newline preservation
```

**Filter**:
```
Files → Conditions (field/operator/value) → filter_files_by_conditions()
Optional: Scope extraction (braces, tags, hierarchical)
Logic: AND (all match) or OR (any match)
```

**Undo/Redo**:
```
User Action → FileModificationCommand (stores original)
Execute → Add to undo_stack, clear redo_stack
Undo → Pop from undo_stack, push to redo_stack, restore original
Redo → Pop from redo_stack, push to undo_stack, reapply new
```

**Multi-Query**:
```
Multi-line Text → Parse (skip # comments) → List[QueryLine]
Each QueryLine → Compiled Pattern
Search → finditer() all patterns → Combine results (de-duplicate)
```

**Memory Register**:
```
Text + Regex → capture() → $0, $1, $2, ... (stored in registers)
Template with $N → replace_in_text() → Resolved text
History → restore_from_history() → Previous capture
Persistence → export_to_json() / import_from_json()
```

### **Still Unknown** (Phase 2 continued):

- ❓ How do file explorer executors work? (file_explorer_executor, file_list_executor)
- ❓ What does rewriter_cli do? (CLI vs GUI rewriter?)
- ❓ What's the result exporter format handling? (CSV, Excel, YAML, TOML)
- ❓ How do set operations work? (union, intersection, difference)

### **Don't Touch Zones** (Critical Code):

1. **SearchOptions.compile()** - Pattern compilation logic
   - Regex escaping, word boundaries, flags
   - Any change breaks all search/replace

2. **preserve_case_like()** - Case preservation algorithm
   - Tested logic for UPPER, lower, Capitalized
   - Don't modify without extensive testing

3. **CommandManager stacks** - Undo/redo state
   - `execute_command()` must clear redo_stack
   - `undo()`/`redo()` must transfer between stacks
   - Violating this breaks undo/redo contract

4. **MemoryRegister.replace_in_text()** - Descending sort
   - Must process `$10` before `$1`
   - Otherwise `$10` becomes `<$1 value>0`

5. **Condition.matches()** - Scope application order
   - Extract scope BEFORE matching
   - Changing order breaks content filtering

---

## 📝 Protocol Compliance Check

**SIMPLICITY_PROTOCOL_3 Step 1.2 Progress**:

- [x] Study entry points ✅
- [x] Study main application class ✅
- [x] Study initialization system ✅
- [x] Study UI construction ✅
- [~] Study core business logic (25% done - 6/24 files) 🔄
- [ ] Study utility modules (Phase 2 continued)
- [ ] Study feature modules (Phase 3)
- [ ] Study support systems (Phase 4)
- [ ] Create comprehensive NOTES.md (Phase 5)

**Current Status**: ~32% of Step 1.2 complete

---

**Session 4 Complete! 🎉**  
**Next**: Continue Phase 2 - Study remaining core/ modules (executors, CLI, exporters)
