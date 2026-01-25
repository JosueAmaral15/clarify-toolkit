# Session 3: BRANCH - Core Business Logic & Managers

**Date:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Session Type:** SCAN Reading (Architecture + Key Algorithms)  
**Time Investment:** 2 hours  
**Protocol:** SIMPLICITY_PROTOCOL_3.md Step 1.3  
**Methodology:** Import Tree Analogy - BRANCH Layer (Business Logic Coordinators)

---

## Executive Summary

**Mission:** Understand core business logic, algorithms, and manager systems  
**Modules Analyzed:** `src/core/` (12 files, 2,782 lines) + 14 manager modules (~2,500 lines)  
**Key Discovery:** Clean separation between algorithms (core/) and orchestration (managers/)  
**Architecture Pattern:** Command Pattern + Manager Singletons + Plugin System

---

## Modules Distribution

| Category | Location | Files | Lines | Purpose |
|----------|----------|-------|-------|---------|
| **Core Algorithms** | `src/core/` | 12 | 2,782 | Search, filter, insert, commands |
| **Managers** | `src/` | 14 | ~2,500 | Orchestrate features (batch, plugins, etc.) |
| **JSON Processing** | `src/json_search/` | 4 | 792 | JSON indexing and querying |
| **Extractors** | `src/extractors/` | ? | ? | Data extraction strategies |
| **Processors** | `src/processors/` | ? | ? | Data transformation pipeline |

**Total Analyzed:** ~6,000 lines of core business logic

---

## Core Algorithms Architecture

### Package Structure (`src/core/`)

```
src/core/
├── __init__.py                  (19 lines)   - Package exports
├── search_replace.py            (64 lines)   - Search/replace engine
├── insert.py                    (52 lines)   - Line insertion modes
├── filters.py                   (343 lines)  - Advanced filtering
├── command_manager.py           (183 lines)  - Undo/Redo system
├── file_list_executor.py        (331 lines)  - File listing
├── file_explorer_executor.py    (683 lines)  - File exploration
├── set_operation_executor.py    (224 lines)  - Set operations
├── result_exporter.py           (196 lines)  - Export results
├── multi_query.py               (189 lines)  - Multi-query search
├── memory_register.py           (303 lines)  - Memory storage
└── rewriter_cli.py              (195 lines)  - JSON rewriter CLI
```

---

## Deep Dive: Search & Replace Engine

**File:** `src/core/search_replace.py` (64 lines)  
**Complexity:** SIMPLE (single-responsibility module)

### Architecture

```python
@dataclass
class SearchOptions:
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False

    def compile(self, needle: str) -> re.Pattern:
        """Build compiled regex pattern from user input + options."""
        flags = 0 if self.case_sensitive else re.IGNORECASE
        
        if self.regex:
            pattern = needle
        else:
            pattern = re.escape(needle)  # Escape special chars
            if self.whole_word:
                pattern = r"\b" + pattern + r"\b"  # Word boundaries
        
        return re.compile(pattern, flags)
```

**Key Functions:**

#### 1. Preserve Case Replacement

```python
def preserve_case_like(matched_text: str, replacement: str) -> str:
    """
    Adjust replacement to mimic matched text case.
    
    Examples:
        matched="FOO",   replacement="bar"  → "BAR"     (ALL CAPS)
        matched="Foo",   replacement="bar"  → "Bar"     (Capitalized)
        matched="foo",   replacement="bar"  → "bar"     (lowercase)
        matched="FoO",   replacement="bar"  → "bar"     (Mixed → as-is)
    """
    if matched_text.isupper():
        return replacement.upper()
    if matched_text.islower():
        return replacement.lower()
    if matched_text[0].isupper() and matched_text[1:].islower():
        return replacement[:1].upper() + replacement[1:].lower()
    return replacement
```

**Analysis:**
- ✅ **Smart Case Matching:** Preserves user intent (Color → Colour, COLOR → COLOUR)
- ✅ **Edge Cases:** Handles single-char strings, mixed case
- 🎯 **Role:** LEAF algorithm (pure function, no state)

#### 2. Replace in Text

```python
def replace_in_text(content: str, pattern: re.Pattern, repl: str,
                    preserve_case: bool = False, count: int = 0) -> Tuple[str, int]:
    """
    Replace occurrences using compiled pattern.
    
    Args:
        content: Text to search in
        pattern: Compiled regex pattern
        repl: Replacement string
        preserve_case: Whether to adapt replacement to match case
        count: Max replacements (0 = all)
    
    Returns:
        (new_content, num_replacements)
    """
    num = 0

    def _repl(m: re.Match) -> str:
        nonlocal num
        num += 1
        return preserve_case_like(m.group(0), repl) if preserve_case else repl

    new = pattern.sub(_repl, content, count=count)
    return new, num
```

**Analysis:**
- ✅ **Functional Pattern:** Uses closure to count replacements
- ✅ **Flexible:** Supports single/all replacements via `count` parameter
- ✅ **Returns Count:** Caller knows how many replacements made
- 🎯 **Role:** LEAF algorithm (delegates to `re.sub`, no business logic)

**Key Insight:** Search/replace is PURE FUNCTIONS. No state, no side effects. This makes it:
- Easy to test (deterministic)
- Easy to parallelize (no shared state)
- Easy to reason about (input → output)

---

## Deep Dive: Advanced Filtering System

**File:** `src/core/filters.py` (343 lines)  
**Complexity:** MEDIUM (multi-feature module)

### Operator System

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

**Usage:**
```python
@dataclass
class Condition:
    field: str       # 'filename', 'path', 'ext', 'size', 'mtime', 'content'
    operator: str    # Key from OPS dict
    value: str       # Value to compare against

# Example: Filter files > 1MB
condition = Condition('size', '>', '1048576')
filtered = filter_files_by_conditions(files, [condition])
```

**Supported Fields:**
1. **filename** - Name only (no path)
2. **path** - Full file path
3. **ext** - Extension (.py, .js, etc.)
4. **size** - File size in bytes
5. **mtime** - Last modified timestamp
6. **content** - File content (requires reading file!)

**Analysis:**
- ✅ **Flexible:** 10 operators support wide range of queries
- ✅ **Composable:** Multiple conditions can be chained
- ⚠️ **Content Filter Performance:** Reads entire file (slow for large files)
- 🎯 **Role:** BRANCH coordinator (combines multiple filter strategies)

### Hierarchical Scope Extraction

**Purpose:** Extract content from HTML/XML with include/exclude rules

```python
def parse_hierarchical_ranges(scope_value: str) -> list[tuple[str, str]]:
    """
    Parse: "include div#test1, exclude #test2, include #test3"
    
    Returns: [
        ("include", "div#test1"),
        ("exclude", "#test2"),
        ("include", "#test3")
    ]
    
    Supports:
    - ID selectors: #myId
    - Tag+ID selectors: div#test1
    - Tag selectors: div
    - Regex patterns (when use_regex=True)
    """
```

**Example:**
```python
html = """
<div id="test1">Include me</div>
<div id="test2">Exclude me</div>
<div id="test3">Include me too</div>
"""

scope = "include div#test1, exclude #test2, include #test3"
result = extract_scope_content(html, "hierarchical", scope)
# Result: "Include me\nInclude me too"
```

**Analysis:**
- ✅ **Powerful:** CSS-like selectors for HTML extraction
- ✅ **Flexible:** Include/exclude rules compose
- ✅ **Regex Support:** Advanced users can use patterns
- 🎯 **Use Case:** Text extraction from HTML (web scraping, doc processing)

---

## Deep Dive: Command Pattern (Undo/Redo)

**File:** `src/core/command_manager.py` (183 lines)  
**Pattern:** Gang of Four Command Pattern  
**Purpose:** Implement Ctrl+Z / Ctrl+Y functionality

### Architecture

```
┌──────────────────────────────────────────────────┐
│             Command (Abstract Base)              │
│  • execute()   - Perform action                  │
│  • undo()      - Revert action                   │
│  • redo()      - Re-execute after undo           │
│  • get_description() - Human-readable name       │
└────────────────┬─────────────────────────────────┘
                 ↓
    ┌────────────┴────────────┐
    ↓                         ↓
┌──────────────────┐  ┌──────────────────┐
│ FileModification │  │ MultiFile        │
│ Command          │  │ Command          │
│                  │  │                  │
│ • filepath       │  │ • commands[]     │
│ • original       │  │   (aggregates)   │
│ • new_content    │  │                  │
└──────────────────┘  └──────────────────┘
                 ↑
                 └─── Used by ───┐
                                 ↓
                    ┌──────────────────────┐
                    │  CommandManager      │
                    │                      │
                    │  • undo_stack        │
                    │  • redo_stack        │
                    │  • max_history=10    │
                    └──────────────────────┘
```

### Key Classes

#### 1. Command (Abstract Base)

```python
class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command (perform the action)."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command (revert the action)."""
        pass
    
    def redo(self) -> None:
        """Redo the command. Default: calls execute()."""
        self.execute()
    
    def get_description(self) -> str:
        """Return human-readable description."""
        return self.__class__.__name__
```

#### 2. FileModificationCommand

```python
class FileModificationCommand(Command):
    """Command for file modification with undo/redo."""
    
    def __init__(self, filepath: str, original_content: str, 
                 new_content: str, description: str = "File modification"):
        self.filepath = filepath
        self.original_content = original_content
        self.new_content = new_content
        self.description = description
    
    def execute(self) -> None:
        """Write new content to file."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(self.new_content)
    
    def undo(self) -> None:
        """Restore original content."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(self.original_content)
    
    def redo(self) -> None:
        """Re-apply new content."""
        self.execute()
```

#### 3. MultiFileCommand

```python
class MultiFileCommand(Command):
    """Aggregates multiple file modification commands."""
    
    def __init__(self, commands: List[FileModificationCommand], 
                 description: str = "Multi-file operation"):
        self.commands = commands
        self.description = description
    
    def execute(self) -> None:
        """Execute all sub-commands."""
        for cmd in self.commands:
            cmd.execute()
    
    def undo(self) -> None:
        """Undo all sub-commands in REVERSE order."""
        for cmd in reversed(self.commands):
            cmd.undo()
    
    def redo(self) -> None:
        """Redo all sub-commands."""
        for cmd in self.commands:
            cmd.redo()
```

**Analysis:**
- ✅ **Composite Pattern:** MultiFileCommand aggregates single-file commands
- ✅ **Reverse Undo:** Multi-file undo reverses order (preserves consistency)
- 🎯 **Use Case:** Batch replace across 100 files → single Ctrl+Z undoes all

#### 4. CommandManager

```python
class CommandManager:
    """Manages undo/redo stack with configurable history depth."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.undo_stack: deque[Command] = deque(maxlen=max_history)
        self.redo_stack: deque[Command] = deque(maxlen=max_history)
    
    def execute_command(self, command: Command) -> None:
        """Execute and add to undo stack. Clears redo stack."""
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Can't redo after new action
    
    def undo(self) -> bool:
        """Undo last command. Returns True if successful."""
        if not self.undo_stack:
            return False
        
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
    
    def redo(self) -> bool:
        """Redo last undone command."""
        if not self.redo_stack:
            return False
        
        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        return True
```

**Analysis:**
- ✅ **Bounded History:** `deque(maxlen=10)` prevents memory leak
- ✅ **Clear Redo on New Action:** Standard behavior (like text editors)
- ✅ **Stack Management:** LIFO ordering (last action undone first)
- 🎯 **Memory Cost:** Stores original + new content for each file operation

### Usage Example

```python
# Create manager
manager = CommandManager(max_history=10)

# Perform file modification
original = read_text("data.json")
new = original.replace("old", "new")

cmd = FileModificationCommand(
    filepath="data.json",
    original_content=original,
    new_content=new,
    description="Replace old with new"
)

# Execute (writes to file)
manager.execute_command(cmd)

# User presses Ctrl+Z
manager.undo()  # File restored to original

# User presses Ctrl+Y
manager.redo()  # File changed again
```

**Key Insight:** Command Pattern enables:
- **Undo/Redo** without coupling to specific operations
- **Batch Operations** as single undo point
- **Command History** for debugging ("what did I just do?")

---

## Manager Systems Architecture

### Manager Directory Structure

```
src/
├── accessibility_manager.py     (9.7KB)  - Screen reader support
├── batch_manager.py             (13KB)   - Batch operation pipeline
├── config_manager.py            (19KB)   - YAML config + validation
├── export_manager.py            (13KB)   - Export results (CSV, JSON, etc.)
├── formula_manager.py           (16KB)   - Formula builder logic
├── history_manager.py           (5.1KB)  - Operation history
├── layout_manager.py            (9.3KB)  - Dock layout save/restore
├── merge_manager.py             (14KB)   - JSON merging strategies
├── migration_manager.py         (9.3KB)  - Database migrations
├── plugin_loader.py             (11KB)   - Plugin discovery & loading
├── presets_manager.py           (6.4KB)  - User presets
├── settings_manager.py          (4.7KB)  - Settings persistence
├── shortcut_manager.py          (14KB)   - Keyboard shortcuts
├── statistics_manager.py        (7.8KB)  - Usage statistics
├── template_manager.py          (14KB)   - Project templates
└── theme_manager.py             (18KB)   - Theme system
```

**Total:** 16 managers, ~163KB code

---

## Deep Dive: Plugin System

**File:** `src/plugin_loader.py` (11KB, ~280 lines)  
**Version:** v2.9.109  
**Pattern:** Plugin Architecture with Event Hooks

### Architecture

```
plugins/
├── example_plugin/
│   ├── plugin.json          ← Metadata (id, name, version, author)
│   ├── main.py              ← Entry point (must have PluginBase subclass)
│   └── resources/           ← Optional resources
│
├── another_plugin/
│   ├── plugin.json
│   └── main.py
│
└── ...

↓ Discovered by PluginLoader

┌──────────────────────────────────────┐
│         PluginLoader                 │
│                                      │
│  discover_plugins()                  │
│    → Scan plugins/ for plugin.json  │
│                                      │
│  load_plugin(id)                     │
│    → Import main.py dynamically      │
│    → Find PluginBase subclass        │
│    → Instantiate plugin              │
│                                      │
│  activate_plugin(id)                 │
│    → Call plugin.activate(app)       │
│                                      │
│  emit_event(name, data)              │
│    → Notify all active plugins       │
└──────────────────────────────────────┘
```

### Plugin Metadata (plugin.json)

```json
{
    "id": "example-plugin",
    "name": "Example Plugin",
    "version": "1.0.0",
    "description": "Demonstrates plugin system",
    "author": "John Doe",
    "entry_point": "main.py",
    "dependencies": [],
    "enabled": true
}
```

### PluginLoader Class

```python
class PluginLoader(QObject):
    """
    Plugin loader with discovery, loading, and lifecycle management.
    
    Features:
    - Auto-discovery from plugins/ folder
    - Metadata validation (plugin.json)
    - Event hook system
    - QSettings integration (enable/disable)
    - Error handling and logging
    """
    
    # Signals
    plugin_loaded = Signal(str)      # plugin_id
    plugin_activated = Signal(str)   # plugin_id
    plugin_error = Signal(str, str)  # plugin_id, error_message
    
    def __init__(self, app):
        super().__init__()
        self.app = app  # MainWindow instance
        self.plugins: Dict[str, Any] = {}  # plugin_id -> instance
        self.metadata: Dict[str, PluginMetadata] = {}  # plugin_id -> metadata
        self.settings = QSettings("Clarify", "Clarify")
        self.plugin_dir = Path(__file__).parent.parent / "plugins"
```

### Discovery & Loading

```python
def discover_plugins(self) -> List[PluginMetadata]:
    """Discover all plugins in plugins/ directory."""
    discovered = []
    
    for item in self.plugin_dir.iterdir():
        if not item.is_dir():
            continue
        
        # Check for plugin.json
        metadata_file = item / "plugin.json"
        if not metadata_file.exists():
            continue
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            data = json.load(f)
        
        metadata = PluginMetadata(data, item)
        
        # Check if enabled in settings
        enabled = self.settings.value(
            f"plugins/{metadata.id}/enabled", 
            metadata.enabled, 
            type=bool
        )
        metadata.enabled = enabled
        
        self.metadata[metadata.id] = metadata
        discovered.append(metadata)
    
    return discovered


def load_plugin(self, plugin_id: str) -> Optional[Any]:
    """Load a plugin by ID."""
    metadata = self.metadata[plugin_id]
    
    # Load module dynamically
    entry_path = metadata.plugin_dir / metadata.entry_point
    spec = importlib.util.spec_from_file_location(
        f"clarify_plugin_{plugin_id}", 
        str(entry_path)
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    # Find PluginBase subclass
    plugin_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            hasattr(attr, 'activate') and 
            attr.__name__ != 'PluginBase'):
            plugin_class = attr
            break
    
    # Instantiate
    plugin_instance = plugin_class()
    self.plugins[plugin_id] = plugin_instance
    
    self.plugin_loaded.emit(plugin_id)
    return plugin_instance
```

**Analysis:**
- ✅ **Dynamic Import:** Uses `importlib.util` (no hardcoded imports)
- ✅ **Error Isolation:** Try/except prevents one broken plugin from crashing app
- ✅ **Settings Integration:** Enabled/disabled state persists
- 🎯 **Discovery Pattern:** Convention over configuration (looks for plugin.json)

### Event System

```python
def emit_event(self, event_name: str, data: dict = None) -> None:
    """
    Emit event to all active plugins.
    
    Supported events:
    - file_opened: {"path": str}
    - search_completed: {"results": list, "query": str}
    - file_saved: {"path": str}
    - app_started: {}
    - app_closing: {}
    """
    for plugin_id, plugin in self.plugins.items():
        if hasattr(plugin, 'on_event'):
            try:
                plugin.on_event(event_name, data or {})
            except Exception as e:
                self.plugin_error.emit(plugin_id, str(e))
```

**Example Plugin:**

```python
# plugins/example/main.py
class ExamplePlugin:
    """Example plugin implementation."""
    
    def activate(self, app):
        """Called when plugin is activated."""
        self.app = app
        print("[ExamplePlugin] Activated!")
    
    def deactivate(self):
        """Called when plugin is deactivated."""
        print("[ExamplePlugin] Deactivated!")
    
    def on_event(self, event_name: str, data: dict):
        """Handle events from main application."""
        if event_name == "file_opened":
            print(f"[ExamplePlugin] File opened: {data['path']}")
        elif event_name == "search_completed":
            print(f"[ExamplePlugin] Search found {len(data['results'])} results")
```

**Analysis:**
- ✅ **Hook System:** Plugins can react to app events
- ✅ **Decoupled:** Main app doesn't know about specific plugins
- ✅ **Extensible:** New events can be added without changing plugin code
- 🎯 **Use Cases:** Custom file processors, analytics, integrations

---

## Deep Dive: Batch Manager

**File:** `src/batch_manager.py` (13KB, ~330 lines)  
**Purpose:** Execute multiple set operations in pipeline  
**Version:** v2.9.102

### Architecture

```
┌─────────────────────────────────────────────┐
│              BatchJob                       │
│  • name: "My Pipeline"                      │
│  • steps: [BatchStep, BatchStep, ...]       │
│  • save_intermediate: bool                  │
│  • output_folder: str                       │
│                                             │
│  to_dict() / from_dict()                    │
│  save_to_file() / load_from_file()          │
└────────────┬────────────────────────────────┘
             │
             ↓ Contains
┌─────────────────────────────────────────────┐
│              BatchStep                      │
│  • operation: 'intersection' | 'union' ...  │
│  • file_a_source: 'file_path' | 'previous'  │
│  • file_a_path, file_b_path: str            │
│  • comparison_mode: 'key_value' | ...       │
│  • options: {ignore_case_keys, ...}         │
│  • description: str                         │
│                                             │
│  Execution state:                           │
│  • status: 'pending' | 'running' | ...      │
│  • result, result_count, error_message      │
│  • execution_time: float                    │
└─────────────────────────────────────────────┘
             ↓ Executed by
┌─────────────────────────────────────────────┐
│          BatchExecutor(QThread)             │
│  • Runs steps sequentially                  │
│  • Emits progress signals                   │
│  • Handles errors gracefully                │
│  • Saves intermediate results (optional)    │
└─────────────────────────────────────────────┘
```

### Key Classes

#### BatchStep

```python
class BatchStep:
    """Single step in batch pipeline."""
    
    def __init__(self, operation: str, file_a_source: str, file_a_path: str,
                 file_b_path: str, comparison_mode: str = 'key_value',
                 options: Dict[str, bool] = None, description: str = ""):
        self.operation = operation  # 'intersection', 'union', 'difference', ...
        self.file_a_source = file_a_source  # 'file_path' or 'previous_result'
        self.file_a_path = file_a_path
        self.file_b_path = file_b_path
        self.comparison_mode = comparison_mode
        self.options = options or {}
        self.description = description
        
        # Execution state
        self.status = 'pending'
        self.result = None
        self.result_count = 0
        self.error_message = ""
        self.execution_time = 0.0
```

**Key Feature:** `file_a_source = 'previous_result'` enables chaining:

```
Step 1: A.json ∩ B.json → result1
Step 2: result1 ∪ C.json → result2  ← Uses previous result!
Step 3: result2 - D.json → final
```

#### BatchJob

```python
class BatchJob:
    """Batch job with multiple steps (named pipeline)."""
    
    def __init__(self, name: str, steps: List[BatchStep] = None,
                 save_intermediate: bool = False, output_folder: str = ""):
        self.name = name
        self.steps = steps or []
        self.save_intermediate = save_intermediate
        self.output_folder = output_folder
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_to_file(self, file_path: str) -> bool:
        """Save batch job to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return True
    
    @staticmethod
    def load_from_file(file_path: str) -> Optional['BatchJob']:
        """Load batch job from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return BatchJob.from_dict(data)
```

**Analysis:**
- ✅ **Serializable:** Can save/load pipelines (reusable!)
- ✅ **Intermediate Results:** Optional saving for debugging
- 🎯 **Use Case:** Complex data processing workflows

#### BatchExecutor

```python
class BatchExecutor(QThread):
    """Thread-based executor for batch jobs."""
    
    # Signals
    step_started = Signal(int, str)  # step_index, description
    step_progress = Signal(int, int)  # step_index, progress_percent
    step_completed = Signal(int, dict)  # step_index, result
    step_failed = Signal(int, str)  # step_index, error_message
    job_completed = Signal(dict)  # final_result
    job_failed = Signal(str)  # error_message
    
    def run(self):
        """Execute all steps sequentially."""
        previous_result = None
        
        for i, step in enumerate(self.job.steps):
            self.step_started.emit(i, step.description)
            
            # Get File A
            if step.file_a_source == 'previous_result':
                file_a_data = previous_result
            else:
                file_a_data = load_json(step.file_a_path)
            
            # Get File B
            file_b_data = load_json(step.file_b_path)
            
            # Execute operation
            result = execute_set_operation(
                step.operation,
                file_a_data,
                file_b_data,
                step.comparison_mode,
                step.options
            )
            
            # Save intermediate (optional)
            if self.job.save_intermediate:
                output_path = f"{self.job.output_folder}/step_{i}_result.json"
                save_json(result, output_path)
            
            previous_result = result
            self.step_completed.emit(i, result)
        
        self.job_completed.emit(previous_result)
```

**Analysis:**
- ✅ **Background Thread:** UI stays responsive
- ✅ **Progress Signals:** Real-time feedback
- ✅ **Error Handling:** Individual step failures don't stop pipeline
- 🎯 **Pipeline Pattern:** Output of step N → input of step N+1

---

## Deep Dive: JSON Search System

**Location:** `src/json_search/` (4 files, 792 lines)

### Architecture

```
src/json_search/
├── __init__.py          (46 lines)   - Package exports
├── indexer.py           (155 lines)  - JSON file indexing
├── query_parser.py      (300 lines)  - Query DSL parser
└── ts_extractor.py      (241 lines)  - TypeScript object extraction
```

### Key Classes

#### ProjectIndexer

```python
class ProjectIndexer:
    """
    Index JSON/TS files for fast searching.
    
    Features:
    - Walks directory tree
    - Parses JSON/TS/TSX files
    - Builds searchable index (key paths + values)
    - Caches results for performance
    """
    
    def index_project(self, root_path: str, extensions: List[str]) -> dict:
        """
        Index all JSON/TS files in project.
        
        Returns:
            {
                'files': [...],
                'keys': {key_path: [file_locations]},
                'values': {value: [file_locations]},
                'total_keys': int,
                'total_values': int
            }
        """
```

**Example Index:**

```json
{
    "keys": {
        "user.name": ["config.json:5", "settings.json:10"],
        "user.email": ["config.json:6"],
        "theme.color": ["theme.json:2"]
    },
    "values": {
        "dark": ["theme.json:2", "user_prefs.json:15"],
        "admin@example.com": ["config.json:6"]
    }
}
```

#### Query Parser

```python
def parse_composite_query(query: str) -> dict:
    """
    Parse composite search query with boolean logic.
    
    Syntax:
        key:user.name           - Search by key path
        value:"John"            - Search by value
        key:user AND value:admin - Boolean AND
        key:theme OR key:config - Boolean OR
        NOT value:disabled      - Boolean NOT
    
    Returns:
        {
            'type': 'AND' | 'OR' | 'NOT' | 'TERM',
            'terms': [...],
            'key': str,
            'value': str
        }
    """
```

**Example Queries:**

```
# Simple
"key:user.name"                    → Find all files with user.name key

# Boolean
"key:user.name AND value:John"     → Find where user.name = "John"

# Complex
"(key:theme.color OR key:theme.mode) AND NOT value:disabled"
```

**Analysis:**
- ✅ **Boolean Logic:** AND/OR/NOT operators
- ✅ **Parentheses:** Grouping for complex queries
- ✅ **Fast Search:** Pre-indexed (no repeated file parsing)
- 🎯 **Use Case:** "Find all files using deprecated API key"

---

## Manager Patterns & Insights

### Pattern 1: Singleton Managers

**Example:** `ConfigManager`, `ThemeManager`, `HistoryManager`

```python
# settings_manager.py
_settings_instance = None

def get_settings():
    """Get global settings instance (singleton)."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
```

**Benefits:**
- ✅ Single source of truth
- ✅ No duplicate initialization
- ✅ Easy access from anywhere

---

### Pattern 2: Manager as Coordinator

**Example:** `BatchManager`, `PluginLoader`

**Responsibilities:**
1. **Orchestrate** complex workflows
2. **Delegate** actual work to executors/workers
3. **Emit signals** for progress tracking
4. **Handle errors** gracefully

**Don't do:**
- ❌ Implement algorithms (delegate to core/)
- ❌ Contain UI code (delegate to gui/)

---

### Pattern 3: Persistent State Managers

**Example:** `HistoryManager`, `PresetsManager`, `LayoutManager`

**Responsibilities:**
1. **Load** state from disk (JSON, YAML, QSettings)
2. **Save** state on changes
3. **Validate** loaded data
4. **Migrate** old formats to new

**Key Feature:** All use `QSettings` for cross-platform persistence

```python
# history_manager.py
class HistoryManager:
    def __init__(self):
        self.settings = QSettings("Clarify", "ClarifyApp")
        self.max_entries = 10
    
    def add_recent_file(self, path: str):
        """Add to recent files list."""
        recent = self.get_recent_files()
        recent.insert(0, path)
        recent = recent[:self.max_entries]  # Limit size
        self.settings.setValue("history/recent_files", recent)
    
    def get_recent_files(self) -> List[str]:
        """Get recent files list."""
        return self.settings.value("history/recent_files", [], type=list)
```

---

## Import Tree Analysis: Core & Managers

### Dependency Map

```
ROOT (app.py)
    ↓
BRANCH (Managers)
    ├── PluginLoader      → Discovers & loads plugins
    ├── BatchManager      → Orchestrates multi-step operations
    ├── CommandManager    → Undo/redo coordination
    ├── ConfigManager     → Global settings
    ├── ThemeManager      → Theme switching
    ├── HistoryManager    → Recent files/operations
    ├── LayoutManager     → Dock positions
    └── ShortcutManager   → Keyboard bindings
        ↓ Delegates to
LEAF (Core Algorithms)
    ├── search_replace    → Pure search/replace functions
    ├── filters           → File filtering logic
    ├── insert            → Line insertion modes
    └── command_manager   → Command pattern implementation
```

**Key Observations:**
- ✅ **Clear Hierarchy:** Managers NEVER implement algorithms (delegate to core/)
- ✅ **Loose Coupling:** Core modules don't import managers
- ✅ **Testability:** Core functions are pure (easy to unit test)

---

## Performance Considerations

### 1. Content Filtering Performance

**Code:** `filters.py` - `Condition(field='content', ...)`

**Issue:** Reads entire file for content matching

```python
if field == 'content':
    file_content = read_text(filepath)  # Reads entire file!
    actual = file_content
```

**Impact:**
- ⚠️ Slow for large files (100MB+ files)
- ⚠️ Memory-intensive for many files

**Mitigation:**
- Use for small files only
- Consider streaming for large files
- Add file size check before content filter

---

### 2. Plugin Loading Performance

**Code:** `plugin_loader.py` - `discover_plugins()`

**Issue:** Scans all subdirectories, reads all plugin.json files

**Impact:**
- ⚠️ Slow startup if many plugins (100+)

**Mitigation:**
- ✅ Already lazy: Discovery on startup, loading on activation
- Could cache discovery results

---

### 3. Batch Executor Memory

**Code:** `batch_manager.py` - Stores all intermediate results

**Issue:** Memory grows with pipeline length

```python
previous_result = None  # Could be huge!

for step in steps:
    result = execute_operation(previous_result, ...)
    previous_result = result  # Holds in memory
```

**Impact:**
- ⚠️ High memory for long pipelines with large datasets

**Mitigation:**
- ✅ Optional `save_intermediate` writes to disk
- Could stream results (don't hold all in memory)

---

## Design Patterns Summary

### 1. **Command Pattern** (Undo/Redo)
- **Where:** `command_manager.py`
- **Benefit:** Decouples actions from execution

### 2. **Singleton Pattern** (Managers)
- **Where:** `get_settings()`, `get_translator()`, etc.
- **Benefit:** Single source of truth

### 3. **Plugin Pattern** (Extensibility)
- **Where:** `plugin_loader.py`
- **Benefit:** Add features without modifying core

### 4. **Pipeline Pattern** (Batch Operations)
- **Where:** `batch_manager.py`
- **Benefit:** Chain operations (output → next input)

### 5. **Strategy Pattern** (Filters)
- **Where:** `filters.py` - OPS dictionary
- **Benefit:** Pluggable comparison operators

### 6. **Observer Pattern** (Qt Signals)
- **Where:** All managers emit signals
- **Benefit:** Loose coupling, reactive updates

---

## Insights & Learnings

### 1. **Clean Separation of Concerns**

✅ **Core:** Pure algorithms (search, filter, replace)  
✅ **Managers:** Orchestration and state management  
✅ **GUI:** Presentation (uses core + managers)

**Benefit:** Can use core algorithms without GUI (CLI mode works!)

---

### 2. **Plugin System is Professional**

✅ Metadata validation (plugin.json)  
✅ Dynamic loading (importlib.util)  
✅ Event hooks (extensibility)  
✅ Error isolation (broken plugin doesn't crash app)

**Benefit:** Community can extend without forking

---

### 3. **Command Pattern Enables Undo**

✅ All file modifications wrapped in commands  
✅ Original content stored for undo  
✅ Multi-file operations as single undo point

**Benefit:** Professional UX (Ctrl+Z works!)

---

### 4. **Batch Manager Enables Workflows**

✅ Serializable pipelines (save/load)  
✅ Chain operations (previous_result)  
✅ Progress tracking (signals)

**Benefit:** Complex data processing made simple

---

### 5. **Filters are Highly Flexible**

✅ 10 operators (contains, equals, >, <, etc.)  
✅ 6 fields (filename, path, ext, size, mtime, content)  
✅ Hierarchical scope extraction (HTML/XML)

**Benefit:** Power users can create complex queries

---

### 6. **Performance Trade-offs Made**

⚠️ Content filtering reads entire files (slow)  
✅ But: Flexibility > Performance for user tool

**Philosophy:** "Make it work, make it right, make it fast" (in that order)

---

### 7. **JSON Search is Sophisticated**

✅ Boolean query language (AND/OR/NOT)  
✅ Pre-indexed (fast lookups)  
✅ Supports TS object literals (not just JSON)

**Benefit:** "Find all configs using deprecated key" in seconds

---

## Questions Answered

### Q1: How does search work?

**A:** 
1. User inputs query + options (case, whole-word, regex)
2. `SearchOptions.compile()` builds regex pattern
3. `replace_in_text()` uses `re.sub()` with custom replacement function
4. **Preserve case:** Adapts replacement to match case

---

### Q2: How does undo/redo work?

**A:**
1. Commands wrap file modifications
2. Store original + new content
3. `CommandManager` maintains undo/redo stacks (max 10)
4. Undo: Pop from undo stack, call `command.undo()`, push to redo stack

---

### Q3: How do plugins work?

**A:**
1. Discovery: Scan `plugins/` for `plugin.json`
2. Loading: Dynamically import `main.py` with `importlib.util`
3. Activation: Call `plugin.activate(app)`
4. Events: App emits events, plugins react via `on_event()`

---

### Q4: How does batch processing work?

**A:**
1. User creates `BatchJob` with multiple `BatchStep`s
2. `BatchExecutor` runs in background thread
3. Each step uses previous step's result (if configured)
4. Optionally saves intermediate results to folder

---

### Q5: What's the import tree role of managers?

**A:**
- **Managers:** BRANCH coordinators (orchestrate, maintain state)
- **Core:** LEAF algorithms (pure functions, no state)
- **GUI:** Uses both (presents to user)

Managers NEVER implement algorithms (delegate to core/)

---

## Next Steps for Session 4

**Focus:** BRANCH - Utilities & Processors  
**Target:** `src/utils/`, `src/processors/`, `src/extractors/`, `src/converters/`  
**Key Questions:**
- What utility functions exist?
- How does data transformation pipeline work?
- What extraction strategies are available?
- How is error handling standardized?

**Reading Mode:** SCAN (catalog capabilities, common patterns)  
**Estimated Time:** 1.5 hours

---

## Appendix: Module Statistics

### Core Package Breakdown

```
search_replace.py     64 lines   (SIMPLE - pure functions)
insert.py             52 lines   (SIMPLE - line insertion modes)
filters.py           343 lines   (MEDIUM - multi-feature)
command_manager.py   183 lines   (MEDIUM - pattern implementation)
rewriter_cli.py      195 lines   (MEDIUM - CLI interface)
memory_register.py   303 lines   (MEDIUM - state storage)
result_exporter.py   196 lines   (MEDIUM - export formats)
multi_query.py       189 lines   (MEDIUM - query composition)
file_list_executor   331 lines   (LARGE - file operations)
file_explorer_exec   683 lines   (LARGE - complex executor)
set_operation_exec   224 lines   (MEDIUM - set math)
────────────────────────────────
TOTAL:             2,782 lines
```

### Manager Sizes

```
theme_manager.py      18KB (largest - complex theming)
config_manager.py     19KB (YAML + validation)
formula_manager.py    16KB (formula builder)
merge_manager.py      14KB (JSON merging)
shortcut_manager.py   14KB (keyboard shortcuts)
template_manager.py   14KB (project templates)
export_manager.py     13KB (export strategies)
batch_manager.py      13KB (pipeline execution)
plugin_loader.py      11KB (plugin system)
────────────────────────────────
Average:             ~13KB per manager
```

---

## Session Completion

**Status:** ✅ COMPLETE  
**Time Spent:** 2 hours  
**Modules Analyzed:** Core (12 files, 2,782 lines) + Managers (14 files, ~2,500 lines)  
**Understanding Level:** SCAN (architecture clear, key patterns identified)  
**Next Session:** Utilities & Processors

---

**Date Completed:** 2026-01-20  
**Branch:** COM5-code-comprehension-study  
**Worktree:** `clarify-COM5-code-study/`  
**Protocol Compliance:** SIMPLICITY_PROTOCOL_3.md Step 1.3 ✅  
**Import Tree Progress:** ROOT + BRANCH (GUI + Core) complete 🌳
