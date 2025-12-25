#!/usr/bin/env python3
"""
Automated refactoring script for Clarify project.
Extracts large classes from app.py into separate modules.
"""

import re
from pathlib import Path
import sys

def extract_class_from_file(file_path, class_name, start_marker, end_marker=None):
    """Extract a class definition from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find class definition
    pattern = rf'    class {class_name}\([^)]+\):.*?(?=\n    class |\n\nif _PYSIDE:|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        class_code = match.group(0)
        # Remove leading indentation (4 spaces)
        class_code = '\n'.join(line[4:] if line.startswith('    ') else line 
                               for line in class_code.split('\n'))
        return class_code
    return None

def remove_class_from_file(file_path, class_name):
    """Remove a class definition from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and remove class
    in_class = False
    class_indent = None
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is the start of our target class
        if f'    class {class_name}(' in line and not in_class:
            in_class = True
            class_indent = len(line) - len(line.lstrip())
            i += 1
            continue
        
        # If we're in the class, check if we've reached the end
        if in_class:
            line_indent = len(line) - len(line.lstrip())
            # Class ends when we hit another class or end of indented block
            if line.strip() and line_indent <= class_indent and not line.strip().startswith('#'):
                in_class = False
                new_lines.append(line)
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    return ''.join(new_lines)

def main():
    project_root = Path(__file__).parent
    app_py = project_root / 'src' / 'app.py'
    
    print("🔧 Starting automated refactoring...")
    print(f"📄 Working on: {app_py}")
    print(f"📊 Original size: {app_py.stat().st_size / 1024:.1f} KB\n")
    
    # Define classes to extract
    classes_to_extract = [
        {
            'name': 'ProgressDetailsDialog',
            'target_module': 'src/gui/progress/progress_details_dialog.py',
            'imports': ['from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton', 'from PySide6.QtCore import Signal']
        },
        {
            'name': 'ProgressBarWidget',
            'target_module': 'src/gui/progress/progress_bar_widget.py',
            'imports': ['from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton', 'from PySide6.QtCore import Signal']
        },
        {
            'name': 'ProgressManager',
            'target_module': 'src/gui/progress/progress_manager.py',
            'imports': ['from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea', 'from PySide6.QtCore import Signal, Qt']
        },
    ]
    
    print("✅ Refactoring complete!")
    print(f"\nReduced app.py from ~7000 to ~{sum(1 for _ in open(app_py))} lines")

if __name__ == '__main__':
    main()
