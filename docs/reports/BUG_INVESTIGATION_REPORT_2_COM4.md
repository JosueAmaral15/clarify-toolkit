# Bug Investigation Report #2 - COM4
**Date:** 2026-02-08  
**Branch:** main (0afd8b2)  
**Investigator:** Programmer #4 (COM4)  
**Status:** 🔴 CRITICAL BUGS FOUND

---

## Executive Summary

Found **3 critical bugs** in second investigation:

1. 🔴 **CRITICAL:** Missing logger import causes NameError (2 files)
2. 🔴 **MINOR:** DEBUG print statements violate protocol (3 lines)
3. ℹ️  **INFO:** test_extraction_cli_3.py in project root (should be in tests/)

---

## 🔴 Bug #1: Missing Logger Import (CRITICAL)

### Location
- `src/settings_manager.py` (lines 56, 68)
- `src/text_extractor/extractor.py` (line 129)

### Problem
Files use `logger` but don't import it. This causes **NameError** when error paths are executed.

### Evidence
```bash
$ python3 -c "from src.settings_manager import SettingsManager; s = SettingsManager('/invalid/path/config.json'); s.set('test', 'val'); s.save()"

Traceback (most recent call last):
  File "src/settings_manager.py", line 68, in save
    logger.error(f"Failed to save settings: {e}")
    ^^^^^^
NameError: name 'logger' is not defined
```

### Code Analysis

**src/settings_manager.py:**
```python
# Line 1-15: imports (NO logger import)
import json
import os
from pathlib import Path
from typing import Any, Optional, Dict

# Line 56: First logger usage
except Exception as e:
    logger.warning(f"Failed to load settings: {e}")  # ❌ NameError

# Line 68: Second logger usage
except Exception as e:
    logger.error(f"Failed to save settings: {e}")  # ❌ NameError
```

**src/text_extractor/extractor.py:**
```python
# Line 1-20: imports (NO logger import)
import os
import glob
from typing import List, Dict, Any, Optional, Tuple

# Line 129: logger usage
except Exception as e:
    logger.error(f"Error processing {file_path}: {e}")  # ❌ NameError
```

### Impact
- ❌ Crashes when error handling is triggered
- ❌ Error information is lost (exception within exception)
- ❌ Production code will fail under error conditions
- ℹ️  Not detected in normal operation (error paths only)

### Root Cause
Logger imports were removed or never added. Pylint detected this:
```
src/settings_manager.py:56:16: E0602: Undefined variable 'logger'
src/settings_manager.py:68:12: E0602: Undefined variable 'logger'
src/text_extractor/extractor.py:129:16: E0602: Undefined variable 'logger'
```

### Fix Required
Add logger imports to both files:
```python
from .utils.logger import get_logger
logger = get_logger(__name__)
```

---

## 🔴 Bug #2: DEBUG Print Statements (PROTOCOL VIOLATION)

### Location
`src/gui/unified_text_to_json_dock.py` (lines 1219, 1220, 1271)

### Problem
3 print() statements with DEBUG messages violate SIMPLICITY_PROTOCOL_3.

### Evidence
```python
# Line 1219
print(f"DEBUG _jsx_copy_all() | Paths tab has {len(paths_text)} chars")

# Line 1220  
print(f"DEBUG _jsx_copy_all() | JSON tab has {len(json_text)} chars")

# Line 1271
print(f"DEBUG _jsx_copy_all() | Combined {len(result)} characters (Paths + JSON)")
```

### Protocol Violation
From SIMPLICITY_PROTOCOL_3:
> "All debug output must use `logger.debug()` instead of `print()`"
> "Print statements only for CLI output (e.g., in `if __name__ == "__main__"` blocks)"

### Impact
- ⚠️  Pollutes stdout in production
- ⚠️  Not controlled by log level settings
- ⚠️  Violates project protocols

### Fix Required
Replace with logger.debug():
```python
logger.debug("_jsx_copy_all() | Paths tab has %d chars", len(paths_text))
logger.debug("_jsx_copy_all() | JSON tab has %d chars", len(json_text))
logger.debug("_jsx_copy_all() | Combined %d characters (Paths + JSON)", len(result))
```

---

## ℹ️ Issue #3: Test File in Project Root

### Location
`test_extraction_cli_3.py` (14KB)

### Problem
Test file exists in project root instead of `tests/` directory.

### Evidence
```bash
$ ls -la test*.py
-rwxrwxr-x 1 josue josue 14240 Feb  6 16:47 test_extraction_cli_3.py
```

### Impact
- ℹ️  Inconsistent with project structure
- ℹ️  Not auto-discovered by pytest
- ℹ️  File came from COM3 merge (Feb 6 16:47)

### Recommendation
Move to `tests/` directory or `tests/manual/` if it's a manual test.

---

## Additional Findings

### ✅ No Other Critical Issues
- ✅ No syntax errors (all Python files parse correctly)
- ✅ No merge conflicts or artifacts
- ✅ No empty Python files
- ✅ No wildcard imports (from X import *)
- ✅ No unresolved merge markers
- ✅ 1193 tests collected successfully

### Files Checked
1. ✅ Python syntax validation (all src/*.py files)
2. ✅ Import analysis (pylint import-error check)
3. ✅ Merge conflict artifacts (*.orig, *.rej, etc.)
4. ✅ Merge conflict markers (<<<<<<, =======, >>>>>>>)
5. ✅ Empty files check
6. ✅ TODO/FIXME markers (all legitimate)
7. ✅ Deprecated code markers (all legitimate)
8. ✅ Test collection (1193 tests found)

---

## Recommended Action Plan

### Priority 1 - CRITICAL (Prevents Crashes)
1. **Fix src/settings_manager.py**
   - Add logger import (lines 1-15)
   - Initialize logger after imports

2. **Fix src/text_extractor/extractor.py**
   - Add logger import (lines 1-20)
   - Initialize logger after imports

### Priority 2 - HIGH (Protocol Compliance)
3. **Fix src/gui/unified_text_to_json_dock.py**
   - Replace 3 print() with logger.debug()
   - Lines: 1219, 1220, 1271

### Priority 3 - LOW (Housekeeping)
4. **Move test_extraction_cli_3.py**
   - Move to tests/ or tests/manual/
   - Update any documentation referencing it

---

## Test Plan

### Before Fixes
```python
# Test logger error path
from src.settings_manager import SettingsManager
s = SettingsManager('/invalid/path/config.json')
s.set('test', 'value')
# Result: NameError: name 'logger' is not defined ❌
```

### After Fixes
```python
# Test logger error path
from src.settings_manager import SettingsManager
s = SettingsManager('/invalid/path/config.json')
s.set('test', 'value')
# Result: Logs error message, no crash ✅
```

---

## Files to Modify

1. `src/settings_manager.py` (add 2 lines)
2. `src/text_extractor/extractor.py` (add 2 lines)
3. `src/gui/unified_text_to_json_dock.py` (modify 3 lines)
4. `test_extraction_cli_3.py` (move file)

**Estimated Fix Time:** 10 minutes

---

## Conclusion

Found 3 bugs in second investigation pass:

**Critical:**
- ✅ Logger imports missing (2 files) - causes NameError in error paths
- ⚠️  DEBUG prints violate protocol (1 file, 3 lines)

**Low Priority:**
- ℹ️  Test file in wrong location (1 file)

**Recommendation:** Fix Priority 1 immediately to prevent production crashes
under error conditions.

