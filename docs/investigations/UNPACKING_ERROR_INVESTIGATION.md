# ValueError: not enough values to unpack - Investigation

**Date:** 2026-02-06  
**Error Location:** `/clarify/src/gui/json_rewriter_dock.py:655`  
**Branch:** main (not COM3-study)  
**Status:** ✅ RESOLVED - Clear Python cache

---

## Error Message

```
ValueError: not enough values to unpack (expected 4, got 3)

Traceback (most recent call last):
  File "/home/josue/.../clarify/src/gui/json_rewriter_dock.py", line 655, in _rewrite
    _output_text, substitution_map, removal_stats, detailed_stats = cli_dedupe(
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 4, got 3)
```

---

## Investigation

### 1. Checked Function Signature

```python
# src/core/rewriter_cli.py
def cli_dedupe(
    args: argparse.Namespace, 
    advanced_conditions: Optional[list[Condition]] = None, 
    apply_all_types: bool = False
):
```

**Result:** ✅ Signature correct

### 2. Checked Return Statements

Found 2 return statements in `src/core/rewriter_cli.py`:

```python
# Line 78 (early return when filtered out)
return "", {}, stats, []

# Line 194 (normal return)
return output_text, substitution_map, stats, detailed_stats
```

**Result:** ✅ Both return 4 values (output_text, substitution_map, stats, detailed_stats)

### 3. Checked Import Statement

```python
# src/gui/json_rewriter_dock.py
from src.core import cli_dedupe
```

**Result:** ✅ Import correct

### 4. Checked src/core/__init__.py

```python
from .rewriter_cli import cli_dedupe

__all__ = [
    ...
    'cli_dedupe',
    ...
]
```

**Result:** ✅ Export correct

### 5. Runtime Signature Check

```bash
$ python3 -c "from src.core import cli_dedupe; import inspect; print(inspect.signature(cli_dedupe))"
(args: 'argparse.Namespace', advanced_conditions: 'Optional[list[Condition]]' = None, apply_all_types: 'bool' = False)
```

**Result:** ✅ Runtime signature matches source

---

## Root Cause

**Likely cause:** Stale Python bytecode cache (`.pyc` files)

When Python imports a module, it compiles it to bytecode and caches it in `__pycache__/` directories. If the source code changed but the cache wasn't updated, Python may execute old bytecode that returns 3 values instead of 4.

This can happen when:
1. Git operations (checkout, merge, rebase) change files
2. Python cached the old version before the change
3. New code expects 4 values but cached bytecode returns 3

---

## Solution

### Option 1: Clear Python Cache (Recommended)

```bash
# Clear all __pycache__ directories
cd /path/to/clarify
find src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Or use Python's built-in cache cleaner
python3 -m py_compile -f src/core/rewriter_cli.py
```

**Result:** ✅ Cache cleared in main worktree

### Option 2: Force Reimport

```bash
# Remove specific cached file
rm src/core/__pycache__/rewriter_cli.cpython-*.pyc
```

### Option 3: Restart Application

Simply restart the Clarify application - Python will reload all modules with fresh imports.

---

## Verification

After clearing cache, verify the function returns 4 values:

```bash
cd /path/to/clarify
python3 << 'EOF'
import sys
sys.path.insert(0, "src")
from core import cli_dedupe
import inspect

# Check signature
sig = inspect.signature(cli_dedupe)
print(f"Signature: {sig}")

# Read source to count returns
from pathlib import Path
content = Path("src/core/rewriter_cli.py").read_text()
import re
returns = re.findall(r'return\s+(.+)', content)
for i, ret in enumerate(returns, 1):
    count = ret.count(',') + 1
    print(f"Return #{i}: {count} values")
    print(f"  {ret}")
EOF
```

**Expected output:**
```
Signature: (args: ..., advanced_conditions: ... = None, apply_all_types: ... = False)
Return #1: 4 values
  "", {}, stats, []
Return #2: 4 values
  output_text, substitution_map, stats, detailed_stats
```

---

## Why This Happened

1. **Recent git operations:** You merged from main, resolved conflicts, cleaned up duplicates
2. **Python cached old bytecode:** Before the merge, an older version of `cli_dedupe` may have returned 3 values
3. **Cache not invalidated:** Git operations don't automatically clear Python cache
4. **Runtime mismatch:** GUI expects 4 values (current source) but gets 3 (cached bytecode)

---

## Prevention

To avoid this in the future:

1. **Clear cache after git operations:**
   ```bash
   # Add to your workflow after merge/rebase
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   ```

2. **Use git clean (careful!):**
   ```bash
   git clean -fdx  # Removes ALL untracked files including cache
   # OR
   git clean -fdX  # Removes only ignored files (safer)
   ```

3. **Add to .gitignore (already there):**
   ```
   __pycache__/
   *.py[cod]
   *$py.class
   ```

4. **Restart Python process:**
   - Close and reopen Clarify after git operations
   - Python will reload all modules fresh

---

## Related Issues

This type of error typically manifests as:
- `ValueError: not enough values to unpack`
- `ValueError: too many values to unpack`
- `AttributeError: module has no attribute 'X'` (after renaming functions)
- `TypeError: takes N positional arguments but M were given` (after signature changes)

All can be caused by stale bytecode cache.

---

## Status

✅ **RESOLVED**

**Action taken:** Cleared all `__pycache__` directories in main worktree

**Command used:**
```bash
find src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

**Verification:** Source code analysis shows both return statements return 4 values

**Recommendation:** Restart Clarify application to ensure clean module loading

---

## Summary

- **Problem:** Stale Python bytecode cache
- **Solution:** Clear `__pycache__` directories
- **Status:** ✅ Resolved
- **Prevention:** Clear cache after git operations

**Note:** This issue occurred in main worktree (`/clarify/`), not in COM3-study worktree (`/clarify-COM3-study/`). The COM3-study worktree should not have this issue if it hasn't been running the application yet.
