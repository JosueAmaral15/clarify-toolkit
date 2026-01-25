# File Explorer Bug - Reproduction Instructions

## 🧪 Test Scenario

**Directory**: `/home/josue/Documents/Informática/Programação/Lingagens de programação/Python - My files/Utils/Math/binary_search`  
**Search Text**: `binary search`  
**Expected**: ≥2 files  
**Actual**: Only 1 file shown in table

## 📋 Steps to Reproduce:

1. **Open Clarify** application
2. **Open File Explorer** tool (Tools → File Explorer)
3. **Select Table view** mode (dropdown at top)
4. **Configure search**:
   - Directory: `/home/josue/.../binary_search`
   - Content search: `binary search`
   - Enable "Recursive" if needed
5. **Click Search** button
6. **Observe table results** - should show only 1 file (BUG!)

## 🔍 Debug Mode Enabled:

I've added comprehensive logging to `_sync_search_to_table()`. 

After reproducing the bug, check the logs at:
- `~/.local/share/Clarify/clarify.log`
- Or terminal output if running with `python main.py`

Look for lines with `[DEBUG]` prefix showing:
- Total files in `last_search_results`
- Loop iterations
- Files added vs filtered
- Final count sent to table

## 📝 What to Report:

Please share the debug log output showing:
```
[DEBUG] _sync_search_to_table() called with X files
[DEBUG] File paths: [...]
[DEBUG] Loop iteration 1: Processing /path/to/file1
[DEBUG] Loop iteration 2: Processing /path/to/file2
[DEBUG] Loop completed: X iterations, Y files added
```

This will reveal where files are being lost!

