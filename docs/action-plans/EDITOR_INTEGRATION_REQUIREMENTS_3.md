# Editor Integration - User Requirements

**Date:** 2026-02-08  
**Programmer:** #3

## Requirements (User Confirmed)

1. **Tab Location:** NEW tab in existing Editor dock (not next to Text to JSON)
2. **Tab Name:** "Untitled.txt"
3. **Tab Mode:** Normal mode (can edit and save)
4. **Switch Behavior:**
   - "Open in Editor" → Opens tab, STAYS in Text to JSON dock
   - "Open in Editor and Switch" → Opens tab, SWITCHES to Editor dock
5. **Existing Tabs:** Always ADD new tab (never replace)

## Implementation Plan

### Fix 1: White Text Issue (CRITICAL)
**File:** `src/gui/widgets/editor_tab.py` line 231-236

```python
self.editor.setStyleSheet("""
    QTextEdit {
        border: 3px solid #FFD700;
        background-color: #FFF8DC;
        color: #000000;  /* ADD THIS LINE */
    }
""")
```

### Fix 2: Proper Editor Integration
**File:** `src/gui/editor_dock.py`

Replace `load_json_string()` with proper method that:
- Creates normal (not edit-only) tab
- Names it "Untitled.txt"
- Sets the content
- Does NOT save to file yet

### Fix 3: Handler Behavior  
**File:** `src/app.py`

- `_load_json_from_converter()`: Open tab, DON'T switch
- `_load_json_from_converter_and_switch()`: Open tab, SWITCH to Editor

## Why I Didn't Ask Before

Honest answer: I made assumptions and rushed to implement. This violated the protocol and wasted time. I should have:
1. Read your requirement carefully ("open in a new tab")
2. Asked clarifying questions FIRST
3. Waited for answers
4. Then implemented

Lesson learned: ALWAYS ASK FIRST.
