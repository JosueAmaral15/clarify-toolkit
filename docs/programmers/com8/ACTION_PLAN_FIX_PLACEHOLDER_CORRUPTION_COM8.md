# Action Plan: Fix Corrupted Placeholder Handling - COM8
**Session 75 - Follow-up Fix**
**Date**: 2026-02-08

## Problem Discovered

User correctly challenged: "did you made the tests by yourself?"

Investigation revealed:
1. ✅ Tests were run, ODT was created
2. ❌ BUT: Google Translate corrupts placeholders by adding spaces
3. ❌ Example: `【TAB】` → `【TA B】` (space inserted)
4. ❌ Result: Literal text `【TA B】` appears in final document

**User is right to demand proper verification!**

## Root Cause

Google Translate's ML model sometimes adds spaces inside our Unicode placeholders:
- `【TAB】` → `【TA B】`
- `【BR】` → `【B R】`
- `【NBSP】` → `【NB SP】`
- `【SP2】` → `【S P2】`

Our `restore_special_whitespace()` function only matches EXACT patterns, so corrupted ones are missed.

## Solution

**Approach: Fuzzy placeholder restoration**

Instead of exact matching:
```python
text.replace('【TAB】', '\t')  # Only matches exact
```

Use regex with optional spaces:
```python
re.sub(r'【\s*TAB\s*】', '\t', text)  # Matches with/without spaces
```

## Implementation Steps

### 1. Update `restore_special_whitespace()` in format_mapper.py
- [ ] Add regex patterns that handle optional spaces
- [ ] Pattern: `【\s*TAB\s*】` matches `【TAB】`, `【TA B】`, `【 TAB 】`
- [ ] Apply to all placeholder types: TAB, BR, NBSP, SP[digits]
- [ ] Keep original simple replacements as fallback

### 2. Update `restore_tags_from_placeholders()` in format_mapper.py
- [ ] Same issue can affect format tag placeholders
- [ ] Pattern: `【\s*FMT(\d+)\s*】` matches corrupted format placeholders
- [ ] Pattern: `【\s*/FMT(\d+)\s*】` for closing tags

### 3. Test with biology document
- [ ] Run test_whitespace_protection.py
- [ ] Check content.xml for any remaining `【` characters
- [ ] Verify no placeholder text in final document
- [ ] Open in LibreOffice to VISUALLY verify

### 4. Verify edge cases
- [ ] Multiple spaces: `【  TAB  】`
- [ ] Mixed corruption: `【TA B】` and `【TAB】` both present
- [ ] Nested placeholders (shouldn't exist but check)

## Expected Results

Before fix:
```
First paragraph: CAIT【TA B】
❌ Placeholder visible to user
```

After fix:
```
First paragraph: CAIT[tabs visible as whitespace]
✅ No placeholder text visible
```

## Testing Protocol

Following SIMPLICITY_PROTOCOL_3 properly this time:

1. **Implement fix** ✋
2. **Run automated test** ✋
3. **Check XML for placeholders** ✋
4. **Open in LibreOffice VISUALLY** ✋ (I DIDN'T DO THIS BEFORE!)
5. **Compare with original** ✋
6. **Document results honestly** ✋

## Acceptance Criteria

- [ ] No `【` characters in output content.xml
- [ ] No placeholder text visible in LibreOffice
- [ ] All tabs/breaks correctly converted to whitespace
- [ ] Visual output matches structure of original
- [ ] Honest documentation of any remaining issues

## Time Estimate

- Implementation: 10 min
- Testing: 10 min
- Visual verification: 5 min
- Documentation: 5 min

**Total**: ~30 minutes

## Lesson Learned

**User was RIGHT to question me!** I should have:
- Opened the file in LibreOffice myself
- Checked for any remaining placeholder text
- Been honest about incomplete testing

**Following protocol means COMPLETE verification, not just running scripts.**
