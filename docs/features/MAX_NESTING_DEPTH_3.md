# Max Nesting Depth Feature

**Programmer #3**  
**Date:** 2026-02-15  
**Commit:** 80828fc  
**Feature Type:** New Enhancement

---

## Overview

The **"Max nesting depth"** feature allows users to reduce JSON nesting depth by limiting the number of parent keys in extraction output paths. This is useful for simplifying deeply nested structures from complex JSX/HTML documents.

**Note:** This is different from the "Limit" field which truncates **key names** (character limit). This feature controls **nesting depth** (number of levels).

---

## Feature Location

**Location:** JSX Extraction section  
**Placement:** New row after "Include key/value" options, before "Options grid"

---

## UI Components

### 1. Checkbox: "Max nesting depth"
- **Default:** Unchecked (disabled)
- **Behavior:** Enables/disables the entire feature
- **Tooltip:** "Reduce JSON nesting depth by limiting number of parent keys in paths"

### 2. SpinBox: "Max keys"
- **Range:** 0-999
- **Default:** 0
- **State:** Disabled when checkbox unchecked
- **Tooltip:** "Maximum number of keys to keep (including leaf). 0 = keep only leaf"

### 3. ComboBox: "Mode"
- **Options:**
  - "Keep from start"
  - "Keep from end"
  - "Keep both ends" (default)
- **State:** Disabled when checkbox unchecked
- **Tooltip:**
  ```
  Start: keep first N parents
  End: keep last N parents
  Both: keep from both ends (CEIL(N/2) from start, FLOOR(N/2) from end)
  ```

---

## Behavior Specification

### How Limiting Works

Given a JSON extraction result:
```json
{
  "Root": {
    "FAQPage": {
      "div": {
        "div": {
          "div": {
            "button": {
              "h3": {
                "text": "Click me"
              }
            }
          }
        }
      }
    }
  }
}
```

**Path:** `Root → FAQPage → div → div → div → button → h3 → text`  
**Parents:** `[Root, FAQPage, div, div, div, button, h3]` (7 parents)  
**Leaf:** `text: "Click me"`

### Mode: "Keep from start"

Keeps the first N parents from the root.

**Limit = 3:**
```json
{
  "Root": {
    "FAQPage": {
      "text": "Click me"
    }
  }
}
```
**Kept:** Root, FAQPage (2 parents) + leaf  
**Removed:** div, div, div, button, h3

**Limit = 4:**
```json
{
  "Root": {
    "FAQPage": {
      "div": {
        "text": "Click me"
      }
    }
  }
}
```
**Kept:** Root, FAQPage, div (3 parents) + leaf

### Mode: "Keep from end"

Keeps the last N parents before the leaf.

**Limit = 3:**
```json
{
  "button": {
    "h3": {
      "text": "Click me"
    }
  }
}
```
**Kept:** button, h3 (2 parents) + leaf  
**Removed:** Root, FAQPage, div, div, div

**Limit = 4:**
```json
{
  "div": {
    "button": {
      "h3": {
        "text": "Click me"
      }
    }
  }
}
```
**Kept:** div, button, h3 (3 parents) + leaf

### Mode: "Keep both ends"

Keeps parents from BOTH the start and end, removing middle keys.

**Limit = 2:**
```json
{
  "Root": {
    "text": "Click me"
  }
}
```
**Kept:** Root (1 parent) + leaf  
**Calculation:** parents_to_keep=1, from_start=1, from_end=0

**Limit = 3:**
```json
{
  "Root": {
    "h3": {
      "text": "Click me"
    }
  }
}
```
**Kept:** Root (start), h3 (end) + leaf  
**Calculation:** parents_to_keep=2, from_start=1, from_end=1

**Limit = 4:**
```json
{
  "Root": {
    "FAQPage": {
      "h3": {
        "text": "Click me"
      }
    }
  }
}
```
**Kept:** Root, FAQPage (start), h3 (end) + leaf  
**Calculation:** parents_to_keep=3, from_start=2, from_end=1

**Limit = 5:**
```json
{
  "Root": {
    "FAQPage": {
      "button": {
        "h3": {
          "text": "Click me"
        }
      }
    }
  }
}
```
**Kept:** Root, FAQPage (start), button, h3 (end) + leaf  
**Calculation:** parents_to_keep=4, from_start=2, from_end=2

---

## Algorithm Details

### Keep Both Ends Algorithm

```python
def limit_parent_keys(parents, limit, mode="both"):
    parents_to_keep = limit - 1  # Subtract 1 for leaf
    
    if parents_to_keep >= len(parents):
        return parents  # No limiting needed
    
    if parents_to_keep <= 0:
        return []  # Keep only leaf
    
    if mode == "start":
        return parents[:parents_to_keep]
    
    elif mode == "end":
        return parents[-parents_to_keep:]
    
    elif mode == "both":
        from_start = (parents_to_keep + 1) // 2  # CEIL(parents_to_keep / 2)
        from_end = parents_to_keep // 2          # FLOOR(parents_to_keep / 2)
        
        if from_end == 0:
            return parents[:from_start]
        else:
            return parents[:from_start] + parents[-from_end:]
```

### Pattern Observations

For "Keep both ends" mode:

| Limit | Parents to Keep | From Start (CEIL) | From End (FLOOR) | Pattern |
|-------|-----------------|-------------------|------------------|---------|
| 2 | 1 | 1 | 0 | [0] |
| 3 | 2 | 1 | 1 | [0, -1] |
| 4 | 3 | 2 | 1 | [0, 1, -1] |
| 5 | 4 | 2 | 2 | [0, 1, -2, -1] |
| 6 | 5 | 3 | 2 | [0, 1, 2, -2, -1] |

**Key insight:** When `parents_to_keep` is odd, we keep one more from the start than from the end.

---

## Implementation Details

### Code Structure

**File:** `src/gui/unified_text_to_json_dock.py`

#### 1. UI Components (Lines 753-803)

```python
# Limit parent keys row
limit_parent_keys_row = QHBoxLayout()

self.jsx_limit_parent_keys_checkbox = QCheckBox(...)
self.jsx_limit_parent_keys_spin = QSpinBox()  # 0-999, default 0
self.jsx_limit_parent_keys_mode_combo = QComboBox()  # 3 modes

# Connect checkbox to enable/disable controls
self.jsx_limit_parent_keys_checkbox.toggled.connect(
    self._jsx_on_limit_parent_keys_toggled
)
```

#### 2. Toggle Handler (Lines 1107-1110)

```python
def _jsx_on_limit_parent_keys_toggled(self, checked: bool) -> None:
    """Enable/disable limit parent keys controls based on checkbox state."""
    self.jsx_limit_parent_keys_spin.setEnabled(checked)
    self.jsx_limit_parent_keys_mode_combo.setEnabled(checked)
```

#### 3. Integration in Extraction Pipeline (Lines 1489-1510)

```python
def _on_extraction_finished(self, text_output: str, json_output: str):
    # Apply parent key limiting if enabled
    if json_output and self.jsx_limit_parent_keys_checkbox.isChecked():
        json_data = json.loads(json_output)
        limit = self.jsx_limit_parent_keys_spin.value()
        mode_text = self.jsx_limit_parent_keys_mode_combo.currentText()
        
        # Map display text to internal mode
        mode_map = {
            "Keep from start": "start",
            "Keep from end": "end",
            "Keep both ends": "both"
        }
        mode = mode_map.get(mode_text, "both")
        
        # Apply limiting
        json_data = self._apply_parent_key_limiting(json_data, limit, mode)
        json_output = json.dumps(json_data, indent=2, ensure_ascii=False)
```

#### 4. Core Algorithm (Lines 2063-2177, 115 lines)

**Main function:**
```python
def _apply_parent_key_limiting(self, data: Any, limit: int, mode: str) -> Any:
    """Recursively apply parent key limiting to JSON data."""
```

**Helper functions:**
- `limit_path_keys(path_parts, value)` → Apply limiting to single path
- `collect_paths(obj, current_path)` → Extract all (path, value) tuples
- `rebuild_dict(paths)` → Reconstruct JSON from limited paths

**Algorithm flow:**
1. Collect all paths from nested JSON structure
2. Apply limiting algorithm to each path
3. Rebuild JSON with limited paths

---

## Edge Cases

### 1. Limit = 0
**Behavior:** Keep only leaf values  
**Result:** All parent keys removed

```json
// Before
{"Root": {"FAQPage": {"div": {"text": "Click me"}}}}

// After (limit=0)
{"text": "Click me"}
```

### 2. Limit >= Total Path Length
**Behavior:** No limiting applied  
**Result:** Original structure preserved

```json
// Path length: 3 (Root → div → text)
// Limit: 5

// Result: No change
{"Root": {"div": {"text": "Click me"}}}
```

### 3. Limit = 1
**Behavior:** Keep only 1 key (varies by mode)

**Mode: Start**
```json
{"Root": {"text": "Click me"}}
```

**Mode: End**
```json
{"h3": {"text": "Click me"}}
```

**Mode: Both**
```json
{"Root": {"text": "Click me"}}  // Same as Start for limit=1
```

---

## Scope

### What Gets Affected
✅ **JSON output tab** - Parent keys are limited in the JSON structure

### What Doesn't Get Affected
❌ **Paths output tab** - Original full paths preserved (no limiting)  
❌ **History** - Stores original JSON before limiting

**Rationale:** Users may want to see full paths for debugging, but simplified JSON for export.

---

## Use Cases

### 1. Simplifying Deeply Nested JSX
**Problem:** React components with many nested divs create overly deep JSON  
**Solution:** Use "Keep both ends" to keep only meaningful structure

### 2. Extracting from Wrapper-Heavy HTML
**Problem:** HTML with repetitive wrapper divs  
**Solution:** Use "Keep from end" to focus on actual content structure

### 3. Focusing on Root-Level Organization
**Problem:** Need high-level structure without implementation details  
**Solution:** Use "Keep from start" to preserve top-level hierarchy

### 4. Creating Flattened Data Exports
**Problem:** External tools can't handle deep nesting  
**Solution:** Set low limit (2-3) to create shallow structure

---

## Testing

### Algorithm Tests (All Passed ✅)

**Test Suite:** 9 tests covering all modes and limits

| Mode | Limit | Parents (7 total) | Expected Result | Status |
|------|-------|-------------------|-----------------|--------|
| start | 3 | [0,1,2,3,4,5,6] | [0,1] + leaf | ✓ PASS |
| start | 4 | [0,1,2,3,4,5,6] | [0,1,2] + leaf | ✓ PASS |
| end | 3 | [0,1,2,3,4,5,6] | [5,6] + leaf | ✓ PASS |
| end | 4 | [0,1,2,3,4,5,6] | [4,5,6] + leaf | ✓ PASS |
| both | 2 | [0,1,2,3,4,5,6] | [0] + leaf | ✓ PASS |
| both | 3 | [0,1,2,3,4,5,6] | [0,6] + leaf | ✓ PASS |
| both | 4 | [0,1,2,3,4,5,6] | [0,1,6] + leaf | ✓ PASS |
| both | 5 | [0,1,2,3,4,5,6] | [0,1,5,6] + leaf | ✓ PASS |
| both | 6 | [0,1,2,3,4,5,6] | [0,1,2,5,6] + leaf | ✓ PASS |

### Manual Testing Checklist

**GUI Testing:**
- [ ] Checkbox enables/disables controls correctly
- [ ] SpinBox accepts values 0-999
- [ ] ComboBox shows 3 mode options
- [ ] Extraction applies limiting when enabled
- [ ] Paths tab unchanged (original paths preserved)
- [ ] JSON tab shows limited structure
- [ ] All 3 modes produce correct output
- [ ] Format conversion works with limited JSON
- [ ] History stores original (unlimited) JSON

---

## Known Limitations

1. **Paths tab not affected:** Full paths always shown (by design)
2. **History stores unlimited JSON:** May differ from displayed output if limiting was enabled
3. **No visual indicator:** Limited keys don't show ellipsis or markers (just removed)
4. **Applied after extraction:** Can't optimize extraction itself, only output

---

## Future Enhancements

**Possible improvements:**
1. Add ellipsis marker (`...`) for removed keys (visual indication)
2. Show count of removed keys in status message
3. Add preset buttons (e.g., "Very shallow", "Moderate", "Deep")
4. Apply limiting during extraction (performance optimization)
5. Add "Limit by depth" mode (alternative to key count)

---

## Conclusion

**Status:** ✅ **Feature Complete and Ready for Testing**

**What was implemented:**
- ✅ Full UI with 3 components (checkbox, spinbox, combobox)
- ✅ 3 limiting modes (start, end, both)
- ✅ Complete algorithm with edge case handling
- ✅ Integration in extraction pipeline
- ✅ All automated tests passing (9/9)

**Ready for:**
- GUI testing with real extractions
- User validation of behavior
- Feedback on mode naming and tooltips

---

**End of Feature Documentation**
