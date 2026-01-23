#!/usr/bin/env python3
"""Test that new code is being loaded"""

import sys
sys.path.insert(0, '.')

# Import the module
from src.gui.file_explorer_dock import FileExplorerDock

# Check if the source has our debug code
import inspect
source = inspect.getsource(FileExplorerDock._on_batch_ready)

if '[COM1-DEBUG] BATCH 1' in source:
    print("✅ SUCCESS: New debug code is present in loaded module!")
    print("The source code contains our print() statements")
else:
    print("❌ FAILURE: Old code still loaded!")
    print("Python is using cached bytecode")

# Show first 30 lines of the method
lines = source.split('\n')[:30]
print("\n" + "="*80)
print("First 30 lines of _on_batch_ready():")
print("="*80)
for i, line in enumerate(lines, 1):
    print(f"{i:3}. {line}")
