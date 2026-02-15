# Action Plan: Add Search Feature to Text to JSON Converter

**Programmer:** #3  
**Date:** 2026-02-06  
**Status:** ⏭️ Awaiting approval

---

## ✅ Requirements Understood

**Triggers:**
- Search button (near text input)
- CTRL+F hotkey

**Modal Dialog:**
- Search input field
- ☑️ Regex
- ☑️ Case sensitive
- ☑️ Whole word
- Find Next/Previous buttons
- Match counter

**Behavior:**
- Text mode only
- Highlight matches
- Navigate between matches

---

## Implementation Steps

1. **Create TextSearchDialog** - Modal with search UI
2. **Add Search Button** - Enable in Text mode only
3. **Add CTRL+F Shortcut** - Keyboard shortcut
4. **Implement Search Logic** - Find, highlight, navigate
5. **Test** - All features and edge cases

**File:** `src/gui/unified_text_to_json_dock.py` (+300-400 lines)  
**Time:** 2-3 hours

Ready to proceed!
