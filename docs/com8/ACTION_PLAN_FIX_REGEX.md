# Action Plan: Fix Tag Cleanup Regex (Session 75 continued)

**Problem:** Tag cleanup regex removes too much content

**Example:**
```
Input:  "<113 |\n\n<113|65536:...>HEALTH RISKS:"
Current: Removes everything, leaves empty
Needed:  Remove only "<113 |", keep rest
```

**Root Cause:**
Current regex: `r'<\s*\d+\s*\|[^>]*(?=\s)'` 
- Matches: `<113 |` + everything until space
- Removes: `<113 | broken tag content` ← TOO MUCH!

**Correct Approach:**
Only remove the malformed tag token itself, not subsequent content.

**Fix:**
```python
# Remove ONLY incomplete tags (no closing >)
# Match: < digits | anything-except-space-or-> $
cleaned = re.sub(r'<\s*\d+\s*\|[^\s>]*', '', text)
```

**Test:**  
- Input: `"text <113 | more text"`
- Output: `"text  more text"` ✅
- Input: `"<113 |\n\nNext paragraph"`
- Output: `"\n\nNext paragraph"` ✅

**Status:** Implementing now
