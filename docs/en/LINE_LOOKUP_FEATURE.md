# Line Lookup Feature - Insert Panel

**Version**: 2.3.0  
**Date**: 2025-11-24  
**Author**: Josué Amaral

---

## 📋 Overview

The **Line Lookup** feature in the **Insert Panel** allows inserting text in files based on search patterns instead of static line numbers. This makes insertions dynamic and adaptable to frequently changing files.

### Problem Solved

**Before (v2.2.0)**:
- Required knowing exact line number
- Insertions broke when file changed
- Impossible to insert in multiple similar lines

**Now (v2.3.0)**:
- Searches patterns to find lines automatically
- Insertions work even with modified files
- Supports insertion in multiple lines at once

---

## 🎯 Operation Modes

### Mode 1: Manual (Traditional)

When **Search query** field is **empty**:

```
Search query: [                    ] (empty)
Line number:  [42                  ] ← Used
```

- Uses line number from spin box
- Classic behavior preserved
- Ideal when you know the exact line

### Mode 2: Lookup (New)

When **Search query** field contains **text**:

```
Search query: [def calculate        ] ← Used to search
Line number:  [42                  ] (ignored)
```

- Searches pattern in file lines
- Ignores manual line number
- Inserts in found lines

---

## ⚙️ Search Options

### 1. Case Sensitive

**When Active** (☑):
- "Function" ≠ "function" ≠ "FUNCTION"
- Exact search respecting case

**When Inactive** (☐):
- "Function" = "function" = "FUNCTION"
- Case-insensitive search

### 2. Whole Word

**When Active** (☑):
- Uses word boundaries (`\b`)
- "test" matches "test" but not "testing"

**When Inactive** (☐):
- Substring search
- "test" matches "test", "testing", "contest"

### 3. Regex

**When Active** (☑):
- Interprets query as regex
- Supports complex patterns: `^import.*from`, `\d+`, etc.

**When Inactive** (☐):
- Literal string search
- Special characters treated as literals

---

## 📍 Occurrence Modes

### First (First Occurrence)

Inserts **only** in the **first line** matching the pattern.

```python
# File:
import os
import sys
import re

# Query: "import"
# Occurrence: First
# Result: Inserts only at line 1 (import os)
```

### Last (Last Occurrence)

Inserts **only** in the **last line** matching the pattern.

```python
# File:
import os
import sys
import re

# Query: "import"
# Occurrence: Last
# Result: Inserts only at line 3 (import re)
```

### All (All Occurrences)

Inserts in **all lines** matching the pattern.

```python
# File:
import os
import sys
import re

# Query: "import"
# Occurrence: All
# Result: Inserts at lines 1, 2, and 3
```

**Note**: When using "All", insertions are processed bottom-to-top to avoid line number shifts.

---

## 🎨 User Interface

### Complete Layout

```
┌─────────────────────────────────────────────────────┐
│ Root path: [/path/to/files          ] [Browse...]   │
│ ☐ Is File?                                           │
│ Include globs: [*.ts;*.tsx;*.js;*.jsx;*.py;*.md]   │
│ Exclude globs: [node_modules;dist;build;.git]      │
├─────────────────────────────────────────────────────┤
│ ╔═══════════════════════════════════════════════╗  │
│ ║ Line Lookup (optional - leave empty for line) ║  │
│ ╠═══════════════════════════════════════════════╣  │
│ ║ Search query: [___________________________]   ║  │
│ ║ ☑ Case sensitive ☐ Whole word ☐ Regex        ║  │
│ ║ Occurrence: [First ▼]                         ║  │
│ ╚═══════════════════════════════════════════════╝  │
├─────────────────────────────────────────────────────┤
│ Line number (1-based): [1      ]                    │
│ (Manual - used only if search query is empty)       │
├─────────────────────────────────────────────────────┤
│ Insert text:                                         │
│ ┌─────────────────────────────────────────────┐    │
│ │ Text to insert here...                       │    │
│ └─────────────────────────────────────────────┘    │
│ Mode: [INSERT_ABOVE ▼]                              │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Practical Use Cases

### Case 1: Add Comment Before Functions

**Goal**: Insert docstring before all Python functions

```python
Query:        "def "
Case:         ☑ (sensitive)
Word:         ☐
Regex:        ☐
Occurrence:   All
Mode:         INSERT_ABOVE
Insert text:  """Function documentation."""
```

**Before**:
```python
def calculate(x, y):
    return x + y

def process(data):
    return data * 2
```

**After**:
```python
"""Function documentation."""
def calculate(x, y):
    return x + y

"""Function documentation."""
def process(data):
    return data * 2
```

---

### Case 2: Add Import After Last Import

**Goal**: Add new import after the last existing import

```python
Query:        "^import "
Case:         ☑
Word:         ☐
Regex:        ☑ (active)
Occurrence:   Last
Mode:         INSERT_BELOW
Insert text:  import newmodule
```

**Before**:
```python
import os
import sys
import re

def main():
    pass
```

**After**:
```python
import os
import sys
import re
import newmodule

def main():
    pass
```

---

### Case 3: Add Tag to End of TODO Lines

**Goal**: Add priority to all TODOs

```python
Query:        "TODO"
Case:         ☐ (insensitive - accepts TODO, todo, Todo)
Word:         ☑ (whole word - doesn't match TODONE)
Regex:        ☐
Occurrence:   All
Mode:         RIGHT
Insert text:   // PRIORITY: HIGH
```

**Before**:
```python
# TODO: Fix this bug
def process():
    pass

# TODO: Refactor code
def cleanup():
    pass
```

**After**:
```python
# TODO: Fix this bug // PRIORITY: HIGH
def process():
    pass

# TODO: Refactor code // PRIORITY: HIGH
def cleanup():
    pass
```

---

## 📊 Confirmation Message

After applying insertions, an informative message is displayed:

### Example 1: Lookup Mode with Matches

```
Modified files: 5
Skipped files (no match): 2

Used search query: 'def calculate'
Occurrence mode: First
```

### Example 2: Lookup Mode with All

```
Modified files: 12
Skipped files (no match): 0

Used search query: 'TODO'
Occurrence mode: All
```

### Example 3: Manual Mode

```
Modified files: 8
Skipped files (no match): 0

Used line number: 42
```

---

## 📈 Test Statistics

### Suite: `test_line_lookup_feature.py`

- **Total Tests**: 10
- **Passing Tests**: 10 ✅
- **Coverage**: 100%

#### Implemented Tests

1. `test_find_line_case_sensitive` - Case-sensitive search
2. `test_find_line_case_insensitive` - Case-insensitive search
3. `test_find_line_whole_word` - Whole word search
4. `test_find_line_regex` - Regex search
5. `test_insert_at_first_occurrence` - Insert at first occurrence
6. `test_insert_at_last_occurrence` - Insert at last occurrence
7. `test_insert_at_all_occurrences` - Insert at all occurrences
8. `test_no_match_skips_file` - File without match is skipped
9. `test_regex_with_whole_word` - Regex with whole word
10. `test_multiline_insertion` - Multi-line insertion

---

## ⚠️ Considerations and Limitations

### Performance

- Search in large files can be slow
- "All" mode with many matches processes multiple insertions
- Complex regex patterns increase processing time

### Recommendations

1. **Use specific patterns**: Avoid very generic patterns that match many lines
2. **Test on few files first**: Validate query before applying to many files
3. **Prefer Whole Word**: Reduces false positives
4. **Validate regex externally**: Use regex101.com to test complex patterns

### Behavior with "All" Occurrence

When using "All":
- Insertions are processed **bottom-to-top** (larger line to smaller)
- This avoids line number changes during processing
- Ensures all insertions are made at correct lines

### Files Without Match

- Files where no line matches the query are **skipped**
- Counted as "skipped" in final message
- Don't generate errors, just aren't modified

---

## 🔗 Compatibility

- **Backward Compatible**: Manual mode 100% preserved
- **Integration**: Works with Advanced Conditions (v2.1.0)
- **Minimum Version**: Python 3.7+
- **Dependencies**: `re` module (built-in)

---

## 📖 References

- [Python re module](https://docs.python.org/3/library/re.html)
- [CHANGELOG v2.3.0](../../CHANGELOG.md#230---2025-11-24)
- [Insert Modes](../INSERT_MODES.md)
- [Advanced Conditions](../ADVANCED_CONDITIONS.md)

---

**Version History**:
- v2.3.0 (2025-11-24): Feature implemented and documented
