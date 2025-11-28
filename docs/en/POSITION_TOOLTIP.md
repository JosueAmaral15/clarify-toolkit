# Position Tooltip Feature (v2.5.1)

## Overview

The position tooltip feature provides detailed information about the line and column position of search/match results when hovering over items in the results panel.

## Features

### 1. Tooltip on Hover
When you hover your mouse over any match result, a tooltip appears showing:
- **File path**: Full path to the file
- **Line number**: Line where the match was found
- **Column number**: Column position where the match starts

Example tooltip:
```
File: /home/user/project/src/main.py
Line: 42
Column: 15
```

### 2. Status Bar Display
A status bar at the bottom of the results panel continuously updates to show the position information for the item currently under the mouse cursor.

Format: `📍 Position: Line X, Column Y | File: [path]`

Example:
```
📍 Position: Line 42, Column 15 | File: /home/user/project/src/main.py
```

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Search Results                              [💾 Save]      │
├─────────────────────────────────────────────────────────────┤
│  📊 Results: 45 matches in 12 file(s)                       │
│  ├─ /path/to/file1.py                                       │
│  │  ├─ 10:5  def test_function():          ← Hover here    │
│  │  └─ 25:10    return test_value                           │
│  ├─ /path/to/file2.py                                       │
│  │  ├─ 5:0  import test_module                              │
│  │  └─ 15:8  test_var = 42                                  │
│  ...                                                         │
├─────────────────────────────────────────────────────────────┤
│  📍 Position: Line 10, Column 5 | File: /path/to/file1.py  │ ← Status bar
└─────────────────────────────────────────────────────────────┘
```

## How It Works

### Implementation Details

1. **Mouse Tracking**: 
   - `ResultsTree` has mouse tracking enabled
   - `itemEntered` signal connected to `_on_item_hover` method

2. **Position Extraction**:
   - Result items store position as "line:col" at the beginning
   - Format: `"10:5  code snippet..."`
   - Parser extracts line and column from this format

3. **Tooltip Generation**:
   - When hovering over a match item (child of file item)
   - Extracts position from item text
   - Gets file path from parent item
   - Creates multiline tooltip with all info

4. **Status Bar Update**:
   - Status label widget passed to `ResultsTree` via `set_status_label()`
   - Updated continuously as mouse moves
   - Cleared when not hovering over match items

## Benefits

1. **No Need to Open File**: See exact position without opening the file
2. **Quick Reference**: Instantly know line and column for navigation
3. **Copy-Paste Friendly**: Can copy position info from tooltip
4. **Visual Feedback**: Status bar provides continuous position updates
5. **Non-Intrusive**: Only appears on hover, doesn't clutter UI

## Use Cases

### 1. Quick Position Check
Hover over a match to see where it is without opening the file.

### 2. Manual Navigation
Copy the line:column info to manually navigate in your editor.

### 3. Code Review
Quickly see positions of all matches for code review purposes.

### 4. Multi-Match Analysis
Compare positions of multiple matches to understand code structure.

### 5. Documentation
Reference exact positions when documenting code changes.

## Technical Details

### Files Modified
- `src/app.py`:
  - `ResultsTree.__init__()`: Added mouse tracking and signal connection
  - `ResultsTree._on_item_hover()`: New method for handling hover events
  - `ResultsTree.set_status_label()`: New method to connect status label
  - `SearchReplacePanel.__init__()`: Added status label widget
  - `InsertPanel.__init__()`: Added status label widget

### Dependencies
- Uses Qt's built-in `QTreeWidget.itemEntered` signal
- No external dependencies required

### Performance
- Minimal overhead: Only parses text on hover
- No impact on search/match performance
- Efficient string parsing (split and extract)

## Configuration

Currently, the feature is always enabled with no configuration options. Future enhancements could include:
- Option to disable tooltips
- Customizable status bar format
- Position format options (0-based vs 1-based)

## Compatibility

Works with:
- ✅ Search/Replace panel
- ✅ Insert panel
- ✅ All file types
- ✅ Regex and plain text searches
- ✅ All operating systems (Linux, Windows, macOS)

## Version History

- **v2.5.1**: Initial implementation
  - Tooltip on hover
  - Status bar at bottom of results panel
  - Works in both Search/Replace and Insert panels

## Testing

Comprehensive test suite in `test_position_tooltip.py`:
- Position extraction from text
- Tooltip formatting
- Status bar formatting
- Edge cases (0:0, large numbers)
- Invalid format handling
- Long file paths

All tests passing ✓
