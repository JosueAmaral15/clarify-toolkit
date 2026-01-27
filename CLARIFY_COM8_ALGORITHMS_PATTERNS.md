# CLARIFY COM8 - ALGORITHMS & PATTERNS DEEP DIVE

## 🔬 Core Algorithms Explained

---

## 1. JSON DEDUPLICATION ENGINE

### Algorithm: `dedupe()` from `rewriter/operations.py`

**Purpose**: Remove duplicate (key, value) pairs recursively

**Time Complexity**: O(n) where n = total key-value pairs  
**Space Complexity**: O(n) for seen set

```python
def dedupe(node: JSONNode, path: str = "root") -> Tuple[JSONNode, int]:
    """
    Process Structure:
    
    Input: {"key": "value", "key": "value", "nested": {"dup": 1, "dup": 1}}
    
    Step 1: For each key-value pair:
            - Recursively dedupe the value
            - Create signature: (key, freeze(value))
            - Check if signature in seen set
            
    Step 2: If duplicate found:
            - Increment removed_count
            - Log to DetailedStatCollector
            - Skip (don't add to output)
            
    Step 3: If new pair:
            - Add signature to seen set
            - Add to output Obj
            
    Output: Same structure, duplicates removed, count = 2
    """
    
    # For Obj (list of tuples allowing duplicates):
    # seen: Set[(key, frozen_value)] = all kept pairs
    # out: Obj = deduplicated output
    # recursively process each value
    
    # For lists: recursively dedupe each element
    # For primitives: return as-is
```

### Key Insight: Signature Freezing
```python
# freeze() creates immutable hash of complex objects
freeze({"nested": {"key": "value"}})
# → Creates hashable representation for duplicate detection
# → Handles JSON objects, arrays, primitives
# → Critical for identifying exact duplicates
```

---

## 2. JOIN_KEYS ALGORITHM

### Purpose: Merge duplicate keys with same value

**Algorithm**:
1. Group values by key
2. If single value → keep as-is
3. If all values identical → keep first, remove rest
4. If all values are Obj → merge recursively
5. Otherwise → keep unique values

```
Input:  {"user": {"id": 1}, "user": {"id": 1}, "user": {"id": 2}}
        
Step 1: Group by key
        "user" → [{"id": 1}, {"id": 1}, {"id": 2}]
        
Step 2: Check first two values: identical → merge
        First: {"id": 1}
        Second: {"id": 1} → Skip (duplicate)
        Third: {"id": 2} → Keep (different)
        
Output: {"user": {"id": 1}, "user": {"id": 2}}
        Combined: "user" now has 2 unique values
```

---

## 3. ELIMINATE_DUPLICATES ALGORITHM

### Purpose: Replace duplicates with first occurrence + references

**Threshold-Based Matching**:
- Threshold: 0.0 (no match) to 1.0 (exact match)
- Similarity = hash_similarity(value1, value2)
- If similarity >= threshold → considered duplicate

```
Input: {
  "user1": {"name": "Alice", "email": "alice@test.com"},
  "user2": {"name": "Alice", "email": "alice@test.com"}  // 100% similar
}

With threshold = 0.95:

Step 1: Create hash of first user1 object
Step 2: Compare user2 hash → 100% match ✓
Step 3: Create reference: {"$ref": "#/user1"}
Step 4: Replace user2 with reference

Output: {
  "user1": {"name": "Alice", "email": "alice@test.com"},
  "user2": {"$ref": "#/user1"}
}

Removed count: 1 object
Space saved: sizeof(user2 object)
```

---

## 4. REFERENCE SYSTEM

### Format Options:

**JSON Pointer ($ref)**:
```json
{"$ref": "/path/to/object"}
```
- Standard format
- Compatible with JSON Schema
- Supports nested paths

**Line Reference (#ref)**:
```json
{"#ref": "123:45"}
```
- Line:column format
- Faster lookup in large files
- Better for TypeScript/code

**Custom Reference (@ref)**:
```json
{"@ref": "object_name"}
```
- Human-readable
- Custom format support
- Easy to debug

### Resolution Process:
```
Reference: {"$ref": "/user/address/city"}
           
Step 1: Parse path segments: ["user", "address", "city"]
Step 2: Start at root, navigate: root["user"]["address"]["city"]
Step 3: Return resolved value
Step 4: Track line numbers for reporting

Output: Resolved value at original location
```

---

## 5. SEARCH & REPLACE WITH CASE PRESERVATION

### Case Preservation Algorithm

**Pattern Match Types**:
1. **Lowercase**: "hello" → preserve as lowercase
2. **Uppercase**: "HELLO" → preserve as UPPERCASE
3. **Title Case**: "Hello" → preserve Title Case (first letter uppercase)
4. **Mixed**: "hElLo" → preserve exact case

```python
def preserve_case_like(replacement: str, original: str) -> str:
    """
    Match case pattern of original to replacement
    
    Examples:
    - replace("Test", "hello") → "test" (original lowercase)
    - replace("Test", "HELLO") → "TEST" (original uppercase)
    - replace("Test", "Hello") → "Test" (original title case)
    - replace("Test", "HeLLo") → "TeST" (original mixed)
    """
    
    # Analyze original case pattern
    if original.isupper():
        return replacement.upper()
    elif original[0].isupper():
        return replacement.capitalize()
    else:
        return replacement.lower()
```

### Search Pipeline:
```
1. Compile regex from search term
2. Find all matches (with limits: 10K per file, 50K total)
3. Extract context (200 char snippet)
4. Apply memory registers ($0-$99 captures)
5. Create SearchMatch objects
6. Apply replacement with case preservation
7. Write back to file
8. Update undo history (max 10 levels)
```

---

## 6. ADVANCED FILTERING WITH HIERARCHICAL SCOPES

### Scope Types:

**HTML/XML Scopes**:
```html
<div class="container">
  <p>Paragraph text</p>      ← Scope: div > p
  <span>Span text</span>      ← Scope: div > span
</div>
```

**Line-based Scopes**:
```
Range: 10-50 (lines 10 to 50)
Range: 10+ (from line 10 onwards)
Range: -50 (up to line 50)
```

### Filter Logic:
```
File → Parse scope structure → Extract scope content → Apply regex
  ↓       (HTML/XML tags)         (text within bounds)     (match)
  ↓                               ↓
Filter includes:                Multiple conditions:
- Case sensitive/insensitive    - AND (all must match)
- Whole word matching           - OR (any can match)
- Regex patterns                - NOT (exclusion)
```

---

## 7. FORMAT CONVERSION STRATEGIES

### Strategy Pattern Implementation:

**JsonToToonConverter**:
```
JSON → Traverse tree → Encode values → Output TOON
```

**JsonToBsonConverter**:
```
JSON → Validate types → Encode binary → Output BSON
```

**JsonToYamlConverter**:
```
JSON → Build structure → Format YAML → Output YAML
```

### Type Mapping:
```
JSON Type       → TOML      → BSON          → YAML
number          → number    → int32/int64   → number
string          → string    → string        → string
boolean         → boolean   → boolean       → boolean
array           → array     → array         → sequence
object          → table     → document      → mapping
null            → (none)    → null          → null
```

---

## 8. JSON SEARCH ENGINE

### Query Parsing:

**Path-Based Queries**:
```
user.address.city = "New York"
↓
Parse path: ["user", "address", "city"]
Parse operator: "="
Parse value: "New York"
```

**Value-Based Queries**:
```
value > 100 AND tags contains "important"
↓
Operator: > (greater than)
Value: 100
Type: numeric
Match: ALL values > 100
```

### Indexing Strategy:
```
Original: {
  "users": [
    {"name": "Alice", "email": "a@b.com"},
    {"name": "Bob", "email": "b@b.com"}
  ]
}

Index: {
  "users[0].name" → "Alice"
  "users[0].email" → "a@b.com"
  "users[1].name" → "Bob"
  "users[1].email" → "b@b.com"
}

Query: "name = Alice"
Result: ["users[0].name"]
```

---

## 9. AI PROCESSOR PIPELINE

### Multi-Provider Support:

```
User Input
    ↓
Detect available provider (internet check)
    ↓
Load credentials from environment/settings
    ↓
Render prompt template (substitute variables)
    ↓
Count tokens → Estimate cost
    ↓
Split large inputs if needed (context window limits)
    ↓
Send to LLM with retry logic
    ↓
Parse response (JSON extraction)
    ↓
Export results (JSON/CSV/etc)
```

### Provider Decision Tree:
```
Has OPENAI_API_KEY? → Use OpenAI
  ↓ No
Has ANTHROPIC_API_KEY? → Use Claude
  ↓ No
Has GOOGLE_API_KEY? → Use Gemini
  ↓ No
→ Error: No API key found
```

### Token Counting:
```
Model: "gpt-4"
Input: "Describe this JSON: {data}"

Step 1: Load tiktoken encoder for model
Step 2: Encode input to tokens
Step 3: Count total tokens
Step 4: Estimate cost:
        - GPT-4: $0.03/1K input, $0.06/1K output
        - Claude: $0.003/1K input, $0.015/1K output
Step 5: Display to user before processing
```

---

## 10. REGEX CAPTURE MEMORY REGISTERS

### Register System ($0-$99):

```
Search pattern: (\w+):(\d+)
Input: "user:123 product:456"

Match 1:
  $0 = "user:123"     (entire match)
  $1 = "user"         (first capture)
  $2 = "123"          (second capture)

Match 2:
  $0 = "product:456"  (entire match)
  $1 = "product"      (first capture)
  $2 = "456"          (second capture)

Replace pattern: "$1-$2"
Output: "user-123 product-456"
```

### Register History:
```
Global register stores last 10 matches (v2.9.120 limit)

Allows composition:
  Search: find_pattern → Captures in registers
  Replace: use_registers → Build complex replacement
  
Example:
  Find: (\w+)=(\d+)
  Replace: "$2:$1"  (flip order)
  Input: "count=5"
  Output: "5:count"
```

---

## 11. MEMORY OPTIMIZATION (v2.9.120)

### Snippet Truncation:
```
Original snippet: "...very long text here that goes on and on and on..."
Max length: 200 chars

Process:
1. If len(snippet) > 200:
   - Find word boundary before 200th char
   - Truncate to word boundary
   - Append "..." if truncated
   
2. Preserve original file (don't modify)
3. Store only truncated snippet in memory
```

### Match Limiting:
```
Per-file: max 10,000 matches
  - ReDoS protection
  - Memory control
  - Performance guarantee

Total: max 50,000 matches across all files
  - System stability
  - Prevent memory explosion
  - Scalable to large codebases
```

### Context Removal:
```
v2.9.119: Stored before/after context (3x memory overhead)
v2.9.120: Removed context (rarely used)

Savings: 66% memory reduction per match
Trade-off: Context no longer available in results
```

---

## 12. UNDO/REDO SYSTEM

### Command Pattern:

```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> bool: pass
    
    @abstractmethod
    def undo(self) -> bool: pass
    
    @abstractmethod
    def get_description(self) -> str: pass
```

### History Management:
```
Deque (max 10 items)

Operation 1: Search/Replace file1
  ↓ Push
Operation 2: Delete duplicate
  ↓ Push
Operation 3: Merge keys
  ↓ Push (now 3 items)

User clicks Undo:
  ↓ Pop
Operation 3 undone

User clicks Undo again:
  ↓ Pop
Operation 2 undone

User clicks Redo:
  ↓ Re-execute Operation 2
```

---

## 13. PLUGIN HOOK SYSTEM

### Hook Points:

```python
class PluginBase:
    # Called when plugin loads
    def on_load(self):
        pass
    
    # Called after file processing
    def on_file_processed(self, file_path: str, data: Dict):
        pass
    
    # Provide menu actions
    def get_menu_actions(self) -> List[QAction]:
        return []
    
    # Handle settings
    def load_settings(self): pass
    def save_settings(self): pass
```

### Plugin Execution:
```
User selects menu item
    ↓
PluginManager finds matching plugin
    ↓
Call hook: on_file_processed(path, data)
    ↓
Plugin processes/modifies data
    ↓
Plugin saves results or returns modifications
    ↓
Continue normal workflow
```

---

## 14. INTERNATIONALIZATION (I18N)

### Translation System:

```python
# Load language
translator = Translator()
translator.set_language("pt_BR")

# Basic key
text = tr("menu.file.open")
# → "Abrir" (Portuguese)

# With variables
error = tr("error.file_not_found", file="data.json")
# → "Arquivo 'data.json' não encontrado"

# Language files structure:
# {
#   "menu": {
#     "file": {
#       "open": "Abrir",
#       "save": "Salvar"
#     }
#   },
#   "error": {
#     "file_not_found": "Arquivo '{file}' não encontrado"
#   }
# }
```

### Runtime Switching:
```
Language selection dropdown
    ↓
Emit signal: language_changed("es")
    ↓
Translator loads Spanish translations
    ↓
Emit signal: tr_updated()
    ↓
All UI elements refresh with new language
    ↓
Settings saved to persistent storage
```

---

## 15. ERROR HANDLING & CRASH REPORTING

### Crash Handler Pipeline:

```
Exception occurs
    ↓
CrashHandler.handle_exception()
    ↓
Step 1: Collect stack trace
Step 2: Strip sensitive paths (/home/user → ~)
Step 3: Strip API keys (detect patterns)
Step 4: Get system info (OS, Python version, etc)
    ↓
Step 5: Format error report
Step 6: Log locally (with rotation)
    ↓
Step 7: Ask user permission
Step 8: Create GitHub issue (optional)
    ↓
Step 9: Display error dialog to user
Step 10: Continue or exit gracefully
```

### Privacy Stripping:
```
Original: "/home/user/.config/clarify/settings.json:123"
Stripped: "~/.config/clarify/settings.json:123"

Original: "API_KEY=sk_test_12345"
Stripped: "API_KEY=***"

Original: "Error in user's_data_file.json"
Stripped: "Error in [file]"
```

---

## 📊 PERFORMANCE CHARACTERISTICS

### Time Complexity:

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| dedupe | O(n log n) | n = pairs, sorting by signature |
| join_keys | O(n) | Single pass through pairs |
| eliminate_duplicates | O(n²) | Compare all pairs (with limit) |
| search | O(m * r) | m = files, r = regex matches/file |
| convert_format | O(n) | n = JSON nodes |
| build_index | O(n) | n = JSON nodes |
| resolve_reference | O(d) | d = path depth |

### Space Complexity:

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| dedupe | O(n) | seen set |
| join_keys | O(n) | groups dict |
| eliminate_duplicates | O(k) | k = unique objects |
| search | O(m) | m = matches (max 50K) |
| index | O(n) | n = flattened nodes |
| memory_registers | O(100) | Fixed 100 registers |

### Optimization Techniques:

1. **Early Exit**: Stop after max matches
2. **Lazy Loading**: Read files only when needed
3. **Caching**: Index caching with TTL
4. **Parallel Processing**: Thread pool for file iteration
5. **Memory Pooling**: Reuse objects to reduce allocation

---

## 🎯 DESIGN LESSONS

### What Each Algorithm Teaches:

1. **dedupe()**: Hash-based deduplication, recursive processing
2. **join_keys()**: Grouping and merging strategies
3. **eliminate_duplicates()**: Threshold-based matching
4. **preserve_case_like()**: Pattern matching and preservation
5. **Advanced Filtering**: Hierarchical scope extraction
6. **Reference System**: Pointer-based data reduction
7. **Query Parser**: DSL implementation
8. **AI Pipeline**: Multi-provider abstraction
9. **Register System**: Capture and reuse patterns
10. **Memory Management**: Constraints-driven optimization

### Best Practices Demonstrated:

- ✅ Type hints for clarity
- ✅ Dataclasses for data structures
- ✅ Enums for configuration
- ✅ Factory patterns for creation
- ✅ Strategy patterns for algorithms
- ✅ Immutability where possible (freeze())
- ✅ Recursion for tree structures
- ✅ Generators for memory efficiency
- ✅ Signals for decoupling
- ✅ Error context in exceptions

---

## 📚 References

- **dedupe**: `src/rewriter/operations.py:1-50`
- **join_keys**: `src/rewriter/operations.py:75-150`
- **eliminate_duplicates**: `src/rewriter/operations.py:180-250`
- **preserve_case_like**: `src/core/search_replace.py`
- **Advanced Filtering**: `src/core/filters.py`
- **Reference System**: `src/rewriter/reference_resolver.py`
- **Query Parser**: `src/json_search/query_parser.py`
- **AI Pipeline**: `src/ai_processor/processor.py`
- **Register System**: `src/core/memory_register.py`
- **Memory Optimization**: `src/core/file_explorer_executor.py` (v2.9.120 notes)

---

This deep dive covers the core algorithms and patterns that make Clarify COM8 powerful and efficient. Each algorithm is optimized for specific use cases while maintaining consistency and reliability across the codebase.

