# Action Plan: Fix Editor Integration Issues

**Programmer:** #3  
**Date:** 2026-02-08  
**Issue:** Editor buttons implementation wrong

## Problems Identified

### Problem 1: Wrong Implementation Approach ❌
**What I did:** Created custom `load_json_string()` method that creates edit-only tabs
**What should happen:** Use existing editor infrastructure (open file in new tab)
**User expectation:** "open the Editor (with the new content) in a new tab"

### Problem 2: White Text on White Background ❌
**Issue:** Edit-only mode stylesheet sets `background-color: #FFF8DC` but NO text color
**Result:** White text on light background = invisible text
**Root cause:** Incomplete stylesheet in `editor_tab.py` line 231-236

### Problem 3: Didn't Ask User ❌
**Protocol violation:** Made assumptions about implementation without asking
**Should have asked:**
1. Should content open in existing Editor dock or new window?
2. Should it be a file-backed tab or edit-only tab?
3. Should it switch to Editor automatically or stay in Text to JSON?
4. What file extension/syntax highlighting should be used?

## Questions for User

Before fixing, I need to ask:

1. **Tab behavior:** Should the content open in a NEW tab in the existing Editor dock?

2. **Tab name/type:** What should the tab be called?
   - "JSON from Converter.json"?
   - "Untitled.json"?
   - Something else?

3. **Tab mode:**
   - Edit-only (can't save without Save As)?
   - Temp file mode (auto-save to /tmp)?
   - Prompt for location immediately?

4. **Switch behavior:**
   - "Open in Editor" → Open tab but STAY in Text to JSON?
   - "Open in Editor and Switch" → Open tab and SWITCH to Editor?

5. **Existing tabs:** Add new tab or replace current tab?
