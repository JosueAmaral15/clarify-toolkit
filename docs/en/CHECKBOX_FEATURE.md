# Checkbox Feature - Advanced Conditions Matching Options

**Version**: 2.2.0  
**Date**: 2025-11-24  
**Author**: Josué Amaral

---

## 📋 Overview

The **Checkbox Options** feature in **Advanced Conditions** allows precise control over how string searches are performed. Three independent options can be combined to create sophisticated search patterns:

1. **Case Sensitive** - Controls case differentiation
2. **Match Whole Word** - Forces matching of complete words only
3. **Use Regex** - Interprets value as regular expression

---

## 🎯 Available Checkboxes

### 1. Case Sensitive

**Default State**: ✅ Active (case-sensitive)

#### When Active
- Search differentiates between uppercase and lowercase
- "Hello" ≠ "hello" ≠ "HELLO"
- Traditional exact search behavior

#### When Inactive
- Search ignores case differences
- "Hello" = "hello" = "HELLO" = "HeLLo"
- Useful for flexible searches

#### Example
```python
# File contains: "Python Programming"

# Case Sensitive = True
"python" → ❌ Not found
"Python" → ✅ Found

# Case Sensitive = False
"python" → ✅ Found
"PYTHON" → ✅ Found
"PyThOn" → ✅ Found
```

---

### 2. Match Whole Word

**Default State**: ❌ Inactive

#### When Active
- Uses regex word boundaries (`\b`)
- Forces matching of complete words only
- Avoids partial matches within other words

#### When Inactive
- Normal substring search
- Matches any occurrence, even within other words

#### Example
```python
# File contains: "The cat is in the category"

# Whole Word = False
"cat" → ✅ Finds "cat" and also within "category"

# Whole Word = True
"cat" → ✅ Finds only "cat" (standalone word)
      → ❌ Doesn't match "cat" within "category"
```

#### Special Cases
```python
# File: "email-address user_name test123"

# Whole Word treats hyphens and underscores as delimiters
"email"   → ✅ Matches (followed by hyphen)
"address" → ✅ Matches (preceded by hyphen)
"user"    → ✅ Matches (followed by underscore)
"name"    → ✅ Matches (preceded by underscore)
"test"    → ✅ Matches (followed by number)
```

---

### 3. Use Regex

**Default State**: ❌ Inactive

#### When Active
- Interprets value as Python regular expression pattern
- Supports all features of Python's `re` module
- Allows complex search patterns

#### When Inactive
- Literal string search
- Special characters treated as literals

#### Basic Example
```python
# File: "Contact: user@example.com and admin@site.org"

# Regex = False
"@" → ✅ Finds the literal "@" character

# Regex = True
r"\w+@\w+\.\w+" → ✅ Finds emails using regex pattern
r"\d+"          → ✅ Finds digit sequences
r"^Contact"     → ✅ Checks if starts with "Contact"
```

#### Common Regex Patterns
```python
# Emails
r"\w+@\w+\.\w+"

# URLs
r"https?://[\w\.-]+\.\w+"

# Phone numbers
r"\(\d{3}\)\s?\d{3}-\d{4}"

# Dates (DD/MM/YYYY)
r"\d{2}/\d{2}/\d{4}"

# Specific words with variations
r"colou?r"  # matches "color" or "colour"

# Empty lines
r"^\s*$"
```

---

## 🔄 Checkbox Combinations

All three options can be combined to create powerful searches:

### Combination 1: Case Insensitive + Whole Word

```python
# File: "The CAT is in the CATEGORY"

# Case=False, Word=True
"cat" → ✅ Finds "CAT" (complete word, ignoring case)
      → ❌ Doesn't find in "CATEGORY"
```

### Combination 2: Regex + Case Insensitive

```python
# File: "Email: USER@EXAMPLE.COM"

# Regex=True, Case=False
r"user@example\.com" → ✅ Finds (ignores case difference)
r"[A-Z]+"            → ✅ Finds uppercase words
```

### Combination 3: Regex + Whole Word

```python
# File: "version 1.2.3 and v1.2.3"

# Regex=True, Word=True
r"\d+\.\d+\.\d+" → ✅ Finds "1.2.3" (standalone word)
                 → ✅ Also finds in "v1.2.3"
```

### Combination 4: All Options

```python
# File: "The EMAIL address is user@site.com"

# Case=False, Word=True, Regex=True
r"email" → ✅ Finds "EMAIL" as complete word, case-insensitive
```

---

## 📝 Application by Field

### Fields Supporting Checkboxes

| Field      | Case | Word | Regex | Description                        |
|------------|------|------|-------|------------------------------------|
| `filename` | ✅   | ✅   | ✅    | File name (without path)           |
| `path`     | ✅   | ✅   | ✅    | Complete file path                 |
| `ext`      | ✅   | ✅   | ✅    | File extension (without dot)       |
| `content`  | ✅   | ✅   | ✅    | File content                       |
| `size`     | ❌   | ❌   | ❌    | Size (numeric only)                |
| `mtime`    | ❌   | ❌   | ❌    | Modified date (numeric only)       |

**Note**: Numeric fields (`size`, `mtime`) don't use checkboxes as they operate with numeric comparisons.

---

## 🎨 User Interface

### Advanced Conditions Layout

```
┌─────────┬──────────┬───────┬────────┬──────────┬──────┬──────┬───────┐
│ Field   │ Operator │ Value │ Scope  │ Scope    │ Case │ Word │ Regex │
│         │          │       │        │ Param    │      │      │       │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│filename │contains  │ test  │ none   │          │  ☑   │  ☐   │  ☐   │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│content  │contains  │ email │brackets│          │  ☐   │  ☑   │  ☑   │
├─────────┼──────────┼───────┼────────┼──────────┼──────┼──────┼───────┤
│path     │equals    │/home/ │ none   │          │  ☑   │  ☐   │  ☐   │
└─────────┴──────────┴───────┴────────┴──────────┴──────┴──────┴───────┘
```

### Tooltips

- **Case**: "Case sensitive"
- **Word**: "Match whole word"
- **Regex**: "Use regular expression"

---

## ⚙️ Integration with Scope Feature

Checkboxes work perfectly with the Scope feature (v2.1.0):

```python
# Example: Search emails only within brackets, case-insensitive

Field:       content
Operator:    contains
Value:       r"\w+@\w+\.\w+"
Scope:       brackets
Scope Param: (empty)
Case:        ☐ (inactive - case insensitive)
Word:        ☐ (inactive)
Regex:       ☑ (active - use regex)
```

**Result**: Searches email pattern using regex, case-insensitively, only within `[...]`.

---

## 🧪 Practical Use Cases

### 1. Search Python Imports (Case Insensitive)

```python
Field:    content
Operator: starts with
Value:    from
Case:     ☐ False
Word:     ☐ False
Regex:    ☐ False
```

### 2. Search Specific Variables (Whole Word)

```python
Field:    content
Operator: contains
Value:    userId
Case:     ☑ True
Word:     ☑ True   # Doesn't match "userIdToken" or "getUserId"
Regex:    ☐ False
```

### 3. Validate Email Format (Regex)

```python
Field:    content
Operator: contains
Value:    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
Case:     ☑ True
Word:     ☐ False
Regex:    ☑ True
```

### 4. Search TODO Comments (Case Insensitive + Regex)

```python
Field:    content
Operator: contains
Value:    r"(TODO|FIXME|HACK|XXX):"
Case:     ☐ False  # Accepts "todo:", "Todo:", "TODO:"
Word:     ☐ False
Regex:    ☑ True
```

### 5. Files with Specific Extension (Case Insensitive)

```python
Field:    ext
Operator: equals
Value:    tsx
Case:     ☐ False  # Accepts ".tsx", ".TSX", ".Tsx"
Word:     ☐ False
Regex:    ☐ False
```

---

## 🔧 Technical Implementation

### Condition Class

```python
@dataclass
class Condition:
    field: str
    operator: str
    value: str
    scope_type: str = ""
    scope_value: str = ""
    case_sensitive: bool = True      # New in v2.2.0
    whole_word: bool = False         # New in v2.2.0
    use_regex: bool = False          # New in v2.2.0
```

### _apply_string_matching Method

The `_apply_string_matching()` method processes all flag combinations:

1. **Regex Mode**: If `use_regex=True`, compiles pattern with appropriate flags
2. **Whole Word**: Adds `\b` to pattern if needed
3. **Case Insensitive**: Applies `re.IGNORECASE` flag or `.lower()` to strings
4. **Operators**: Supports contains, equals, starts with, ends with, not contains, not equals

---

## 📊 Test Statistics

### Test Suite: `test_checkbox_feature.py`

- **Total Tests**: 10
- **Passing Tests**: 10 ✅
- **Coverage**: 100%

#### Implemented Tests

1. `test_case_sensitive_true` - Verifies case-sensitive matching
2. `test_case_insensitive` - Verifies case-insensitive matching
3. `test_whole_word_matching` - Verifies word boundaries
4. `test_regex_matching` - Verifies basic regex patterns
5. `test_regex_with_case_insensitive` - Combines regex + case
6. `test_whole_word_with_case_insensitive` - Combines word + case
7. `test_filename_matching_with_flags` - Tests application on filename
8. `test_operators_with_case_insensitive` - Tests various operators
9. `test_not_contains_with_whole_word` - Tests negative operator
10. `test_all_flags_combined` - Tests all flags together

---

## ⚠️ Limitations and Considerations

### Invalid Regex

If the user provides an invalid regex pattern, the condition returns `False`:

```python
# Invalid regex
r"[invalid(regex" → ❌ Compilation error, returns False
```

### Performance

- **Regex**: Complex patterns can be slower
- **Whole Word**: Adds internal regex overhead
- **Case Insensitive**: Minimal overhead (`.lower()`)

### Recommendations

1. Use regex only when necessary
2. Test regex patterns in external tool first (regex101.com)
3. For simple searches, prefer case-insensitive over regex
4. Combine whole word with case insensitive for flexible searches

---

## 🔗 Compatibility

- **Backward Compatible**: Default values preserve previous behavior
- **Minimum Version**: Python 3.7+
- **Dependencies**: `re` module (built-in)
- **Integration**: Works with Scope Feature (v2.1.0)

---

## 📚 References

- [Python re module](https://docs.python.org/3/library/re.html)
- [Regex Tutorial](https://www.regular-expressions.info/)
- [Word Boundaries](https://www.regular-expressions.info/wordboundaries.html)
- [CHANGELOG v2.2.0](../../CHANGELOG.md#220---2025-11-24)

---

**Version History**:
- v2.2.0 (2025-11-24): Feature implemented and documented
