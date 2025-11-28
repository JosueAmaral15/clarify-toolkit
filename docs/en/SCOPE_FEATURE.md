# Scope Feature in Advanced Conditions

**Implementation Date**: November 24, 2025  
**Version**: 2.1  
**Status**: ✅ Implemented and Tested

---

## Overview

The **scope determination** feature allows you to apply filtering conditions only to content within specific delimiters, rather than searching the entire file. This is extremely useful for:

- Searching only within specific code blocks
- Filtering content within specific HTML/XML tags
- Focusing on sections delimited by custom markers
- Analyzing nested data structures

---

## How to Use

### Graphical Interface

In the **Advanced Conditions** of the Search/Replace and Insert panels, you now have two new fields:

1. **Scope**: Dropdown with available scope types
2. **Scope Param**: Text field for additional parameters (when needed)

### Available Scope Types

| Scope Type | Description | Requires Scope Param? | Example |
|------------|-------------|----------------------|---------|
| `none` | No scope (default - searches entire file) | No | - |
| `brackets` | Only between brackets `[...]` | No | `[text here]` |
| `braces` | Only between braces `{...}` | No | `{text here}` |
| `parentheses` | Only between parentheses `(...)` | No | `(text here)` |
| `custom` | Between custom delimiters | Yes | `begin,end` |
| `tag` | Inside any HTML/XML tag | No | `<any>text</any>` |
| `specific-tag` | Inside a specific tag | Yes | `div` for `<div>text</div>` |

---

## Usage Examples

### Example 1: Search Only in JSON Blocks

**Scenario**: You have files with comments and JSON blocks, and want to search only within JSON blocks (between braces).

**Configuration**:
- Field: `content`
- Operator: `contains`
- Value: `"translation"`
- Scope: `braces`
- Scope Param: *(empty)*

**Result**: Searches only within `{...}` ignoring text outside braces.

---

### Example 2: Search Only in Script Tags

**Scenario**: You want to find HTML files containing specific code only within `<script>` tags.

**Configuration**:
- Field: `content`
- Operator: `contains`
- Value: `console.log`
- Scope: `specific-tag`
- Scope Param: `script`

**Result**: Searches only within `<script>...</script>`, ignoring the rest of the HTML.

---

### Example 3: Custom Delimiters

**Scenario**: You have files with sections delimited by `BEGIN` and `END`, and want to search only in those sections.

**Configuration**:
- Field: `content`
- Operator: `contains`
- Value: `TODO`
- Scope: `custom`
- Scope Param: `BEGIN,END`

**Result**: Searches only between `BEGIN` and `END`.

---

### Example 4: Combination with Other Conditions

You can combine scope with other conditions:

**Line 1**:
- Field: `ext`
- Operator: `equals`
- Value: `tsx`

**Line 2**:
- Field: `content`
- Operator: `contains`
- Value: `useState`
- Scope: `braces`

**Result**: `.tsx` files containing `useState` within `{...}` blocks.

---

## Behavior with Nesting

### Nested Braces and Parentheses

The feature supports proper nesting:

```javascript
{
  outer: {
    inner: "nested value"
  }
}
```

**Behavior**: Extracts all content from the outer block, including inner blocks.

### Brackets

For simple brackets (non-nested):

```javascript
[item1] text [item2]
```

**Behavior**: Extracts `item1` and `item2` separately.

---

## Technical Implementation

### Modified Files

1. **`src/core/filters.py`**
   - Added `extract_scope_content()` function
   - `Condition` class now accepts `scope_type` and `scope_value`
   - Matching logic updated to apply scope filter

2. **`src/app.py`**
   - `SearchReplacePanel` and `InsertPanel` updated
   - Added UI fields for Scope and Scope Param
   - Updated `_conds()`, `enable_buttons()` and `reset_advanced_conditions()` methods

3. **`src/core/__init__.py`**
   - Added export of `extract_scope_content`

### Main Function

```python
def extract_scope_content(text: str, scope_type: str, scope_value: str = "") -> str:
    """
    Extract content within specified scope delimiters.
    
    Args:
        text: The full text to extract from
        scope_type: Type of scope ("brackets", "braces", "custom", "tag", "specific-tag", "" for no scope)
        scope_value: Additional value for custom delimiters or specific tag name
    
    Returns:
        Concatenated content within all matching scopes
    """
```

---

## Tests

A complete test suite was created in `test_scope_feature.py`:

- ✅ Content extraction between brackets
- ✅ Content extraction between braces
- ✅ Content extraction between parentheses
- ✅ Custom delimiters
- ✅ Generic HTML/XML tags
- ✅ Specific HTML/XML tags
- ✅ Integration with `Condition` class
- ✅ Nested braces

**Status**: All tests passing ✅

---

## Known Limitations

1. **Regex in Scope Param**: Currently, the Scope Param field doesn't support regex, only literal strings.

2. **Self-Closing Tags**: Self-closing HTML tags (e.g., `<img />`) are not considered in `tag` or `specific-tag` mode.

3. **Performance**: For very large files with many nested blocks, there may be performance impact. It's recommended to combine with other conditions (extension, size) to optimize.

---

## Advanced Use Cases

### 1. React Code Refactoring

Search for specific props only within JSX (between braces):

```
Field: content
Operator: contains
Value: onClick
Scope: braces
```

### 2. Log Analysis

Search for errors only in specific log sections:

```
Field: content
Operator: contains
Value: ERROR
Scope: custom
Scope Param: [ERROR START],[ERROR END]
```

### 3. HTML Data Extraction

Search content only in divs with specific class (use regex in value):

```
Field: content
Operator: contains
Value: <your search term>
Scope: specific-tag
Scope Param: div
```

---

## Future Roadmap

Possible future improvements:

- [ ] Regex support in Scope Param
- [ ] HTML attribute-based scope (e.g., only within `<div class="content">`)
- [ ] Multiple simultaneous scope types (e.g., braces AND brackets)
- [ ] Negative scope (everything EXCEPT within delimiters)
- [ ] Preview visualization of extracted content before applying condition

---

## Support and Feedback

To report bugs or suggest improvements related to this feature:

- **GitHub Issues**: [github.com/JosueAmaral15/clarify/issues](https://github.com/JosueAmaral15/clarify/issues)
- **Documentation**: `docs/en/SCOPE_FEATURE.md` (this file)

---

**Developed by**: GitHub Copilot (Claude Sonnet 4.5)  
**Date**: November 24, 2025  
**Clarify Version**: 2.1
