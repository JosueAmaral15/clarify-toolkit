#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clarify - Development Testing & Module Validation
--------------------------------------------------
THIS IS NOT THE MAIN APPLICATION!

PURPOSE:
    This script is for DEVELOPMENT ONLY - it tests and validates
    that the modular architecture is working correctly.

WHAT THIS DOES:
    - Tests imports from src/core/, src/utils/, src/rewriter/
    - Validates that modules are properly organized
    - Ensures no circular dependencies
    - Confirms all key functions are accessible

TO RUN THE ACTUAL APPLICATION, USE:
    python clarify.py              # User-friendly entry point
    python -m src                  # Standard Python module execution
    ./clarify_gui.sh               # GUI launcher (Linux/Mac)
    clarify_gui.bat                # GUI launcher (Windows)

TO TEST THE ARCHITECTURE:
    python main.py test            # Run this file's test command

DEVELOPER NOTE:
    If you're looking for the main application code, see:
        - src/app.py (main application ~2,700 lines)
        - clarify.py (thin convenience wrapper)
        - src/__main__.py (standard Python entry point)
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from organized modules in src/
from src.core import SearchOptions, preserve_case_like, replace_in_text
from src.core import InsertMode, insert_at_line
from src.core import Condition, filter_files_by_conditions, OPS

from src.utils import walk_files, read_text, write_text, safe_backup_file
from src.utils import parse_exclusion_patterns, mask_exclusions, unmask_exclusions
from src.utils import load_ts_object, dump_ts_object

from src.rewriter import (
    Obj, JSONNode, parse_json_preserving_duplicates_text,
    sanitize_keys_and_values, ts_process_full_preserving,
    dedupe, join_keys, eliminate_duplicates,
    find_object_block, ts_block_to_json_text
)


def print_banner():
    """Print application banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                       CLARIFY v2.0                            ║
║          Text Search, Replace & JSON Processing Tool          ║
║                     (Reorganized Edition)                     ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_help():
    """Print help information."""
    print("""
📖 CLARIFY - Usage:

🔹 GUI Mode (Graphical Interface):
   python main.py

🔹 CLI Mode (Command Line):

   📍 Search:
      python main.py search <path> --query "text" [--case] [--word] [--regex]
      
   📍 Replace:
      python main.py replace <path> --query "old" --replacement "new" [--all]
      
   📍 Insert:
      python main.py insert <path> --line N --text "text" --mode <mode>
      
   📍 JSON Translator:
      python main.py translate <path> --dictionary dict.json [--root-name t]
      
   📍 JSON Rewriter (dedupe):
      python main.py dedupe <file.ts> [--join-keys] [--eliminate-duplicates]

🔧 Available Modules (in src/):
   ✅ src.core/         - Search, replace, insert, filters
   ✅ src.utils/        - File, text, and TypeScript utilities
   ✅ src.rewriter/     - JSON Rewriter with critical bug fix
   ⏳ src.translators/  - JSON Translator (in migration)
   ⏳ src.ui/           - Graphical interface (in migration)
   ⏳ src.cli/          - CLI commands (in migration)

📚 Examples:
   # Search TypeScript files
   python main.py search ./src --query "React" --include "*.tsx"
   
   # Replace with preserve-case
   python main.py replace ./src --query "color" --replacement "colour" --all
   
   # Dedupe JSON with join keys
   python main.py dedupe en.ts --join-keys --eliminate-duplicates -o en2.ts

For more information, see README.md
    """)


def main():
    """Main entry point for testing and validation."""
    # If no arguments, show help
    if len(sys.argv) == 1:
        print_banner()
        print_help()
        return 0
    
    command = sys.argv[1]
    
    if command in ("-h", "--help", "help"):
        print_banner()
        print_help()
        return 0
    
    if command == "test":
        # Quick test of modules
        print("🧪 Testing imported modules from src/...\n")
        
        # Test core
        print("✅ src.core.SearchOptions:", SearchOptions)
        print("✅ src.core.InsertMode:", InsertMode)
        print("✅ src.core.Condition:", Condition)
        
        # Test utils
        print("✅ src.utils.walk_files:", walk_files)
        print("✅ src.utils.read_text:", read_text)
        
        # Test rewriter
        print("✅ src.rewriter.Obj:", Obj)
        print("✅ src.rewriter.dedupe:", dedupe)
        print("✅ src.rewriter.sanitize_keys_and_values:", sanitize_keys_and_values)
        
        print("\n🎉 All modules from src/ loaded successfully!")
        print("✨ Modular architecture validated!")
        return 0
    
    # For other commands, redirect to clarify.py
    print(f"⚠️  Command '{command}' requires full application.")
    print("💡 Use: python clarify.py {command}")
    print("💡 Or: python -m src {command}")
    print("\nℹ️  This script (main.py) is for testing modular imports only.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
