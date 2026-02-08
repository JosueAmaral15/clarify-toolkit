# ACTION PLAN: Fix Adjacent Tags Bug - COM8

**Date**: 2026-02-08
**Session**: 76
**Programmer**: COM8
**Protocol**: SIMPLICITY_PROTOCOL_3 - Fix Implementation Phase

---

## 🎯 OBJECTIVE

Fix regex pattern to handle adjacent format tags at span transitions.

---

## 🔍 PROBLEM

Current regex only matches paired tags with content:
```python
pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]*?)</(\d+(?:\|\d+)?)>'
```

**Misses**: `</113|65536><112|65536:...>` (adjacent tags, no content)

---

## 🛠️ SOLUTION APPROACH

**Strategy**: Handle both paired tags AND individual unpaired tags

### Phase 1: Update replace_tags_with_placeholders()
- [ ] Keep existing paired tag matching (for normal content)
- [ ] Add second pass for individual unpaired tags
- [ ] Create placeholders for both opening and closing tags separately
- [ ] Maintain order (important for restoration)

### Phase 2: Update restore_tags_from_placeholders()
- [ ] Handle both paired placeholders: `【FMT001】text【/FMT001】`
- [ ] Handle individual placeholders: `【FMT_CLOSE001】【FMT_OPEN002】`
- [ ] Restore in correct order
- [ ] Maintain ultra-permissive regex for corruption

### Phase 3: Testing
- [ ] Create minimal test case with adjacent tags
- [ ] Test with user's actual file
- [ ] Verify NO visible tags in output
- [ ] Verify formatting still works
- [ ] Verify 100% tab preservation maintained

### Phase 4: Validation
- [ ] Run complete translation test
- [ ] Check all paragraphs for visible tags
- [ ] Visual inspection in LibreOffice
- [ ] Get user approval

---

## 📝 IMPLEMENTATION DETAILS

### Regex Pattern Changes

**Current (paired tags only)**:
```python
pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]*?)</(\d+(?:\|\d+)?)>'
```

**New approach** - Two-pass system:

**Pass 1: Paired tags** (keep existing):
```python
paired_pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]+?)</\1>'
# Matches: <TAG>content</TAG> (with backreference)
```

**Pass 2: Individual tags** (new):
```python
# Opening tags
opening_pattern = r'<(\d+(?:\|\d+)?:[^>]+)>'
# Matches: <113|65536:Arial|0,0>

# Closing tags  
closing_pattern = r'</(\d+(?:\|\d+)?)>'
# Matches: </113|65536>
```

### Placeholder Format

**Paired** (existing):
- Opening: `【FMT001】`
- Closing: `【/FMT001】`

**Individual** (new):
- Opening: `【FMTO001】` (O = Open)
- Closing: `【FMTC001】` (C = Close)

### Processing Order

1. **Replacement order**:
   - First: Replace paired tags (preserve existing behavior)
   - Second: Replace remaining individual tags

2. **Restoration order**:
   - First: Restore paired placeholders
   - Second: Restore individual placeholders
   - Third: Whitespace restoration (existing)

---

## ✅ SUCCESS CRITERIA

- [ ] No visible tags in translated output
- [ ] All formatting preserved
- [ ] Tab preservation: 100%
- [ ] Line break preservation: ≥86%
- [ ] Translation quality: unchanged
- [ ] User's file test passes
- [ ] No regression in other documents

---

## 🔄 ROLLBACK PLAN

If fix breaks existing functionality:
1. Keep git commit separate
2. Can revert with: `git revert <commit>`
3. Investigation stays documented
4. Try alternative approach

---

## 📊 PROGRESS TRACKING

- [x] Investigation complete
- [x] Root cause identified
- [x] Action plan created
- [ ] Implementation started
- [ ] Testing complete
- [ ] User approval

---

**Status**: Ready to implement
**Estimated time**: 30-60 minutes
**Risk level**: Low (targeted fix, good rollback)
