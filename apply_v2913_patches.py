#!/usr/bin/env python3
"""
Script para aplicar patches da v2.9.13
Aplica as 4 tasks de forma controlada
"""

import os
import sys

# Task #40 + #42: file_list_dock.py
FILE_LIST_PATCHES = [
    # Imports
    {
        "old": """import os
import stat
import pwd
import grp
from datetime import datetime
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from .base_dock import BaseDock""",
        "new": """import os
import stat
import pwd
import grp
import subprocess
import platform
from datetime import datetime
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction
from .base_dock import BaseDock"""
    },
    # __init__
    {
        "old": """    def __init__(self, parent=None):
        super().__init__("File List", parent)
    
    def _setup_ui(self):
        \"\"\"Setup UI components.\"\"\"
        self._create_widgets()
        self._create_layout()""",
        "new": """    def __init__(self, parent=None):
        super().__init__("File List", parent)
        self.settings = QSettings("Clarify", "FileList")  # Task #42 - v2.9.13
        self._load_preferences()  # Task #42
    
    def _setup_ui(self):
        \"\"\"Setup UI components.\"\"\"
        self._create_widgets()
        self._create_layout()
        self._setup_context_menu()  # Task #40 - v2.9.13"""
    }
]

# Task #41: file_finder.py
FILE_FINDER_PATCHES = [
    {
        "old": """        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        results_layout.addWidget(self.table)""",
        "new": """        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        # Task #41 - v2.9.13: Enable tooltips for preview
        self.table.setMouseTracking(True)
        self.table.itemEntered.connect(self._show_file_preview)
        results_layout.addWidget(self.table)"""
    }
]

# Task #43: json_translate_dock.py  
JSON_TRANSLATE_PATCHES = [
    {
        "old": """        self.chk_preserve_uppercase = QCheckBox("Preserve uppercase keys")
        self.chk_preserve_uppercase.setToolTip("Preserve keys that are already UPPERCASE (e.g., HOME_TITLE stays HOME_TITLE)")
        
        # Action buttons (Task #10 - v2.9.8)
        self.btn_run = QPushButton("Run translation")""",
        "new": """        self.chk_preserve_uppercase = QCheckBox("Preserve uppercase keys")
        self.chk_preserve_uppercase.setToolTip("Preserve keys that are already UPPERCASE (e.g., HOME_TITLE stays HOME_TITLE)")
        
        # Stats label (Task #43 - v2.9.13)
        self.lbl_stats = QLabel("Ready")
        self.lbl_stats.setStyleSheet("color: gray; font-style: italic;")
        self.lbl_stats.setWordWrap(True)
        
        # Action buttons (Task #10 - v2.9.8)
        self.btn_run = QPushButton("Run translation")"""
    }
]

def apply_patch(filepath, patches):
    """Aplica uma lista de patches em um arquivo"""
    print(f"\\nAplicando patches em: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ Arquivo não encontrado: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for i, patch in enumerate(patches, 1):
        if patch["old"] in content:
            content = content.replace(patch["old"], patch["new"])
            print(f"  ✅ Patch {i}/{len(patches)} aplicado")
        else:
            print(f"  ⚠️  Patch {i}/{len(patches)} não encontrado (pode já estar aplicado)")
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  💾 Arquivo atualizado")
        return True
    else:
        print(f"  ℹ️  Nenhuma mudança necessária")
        return False

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("v2.9.13 - Aplicando patches das 4 tasks")
    print("=" * 60)
    
    files_modified = 0
    
    # Task #40 + #42: file_list_dock.py
    filepath = os.path.join(base_dir, "src/gui/file_list_dock.py")
    if apply_patch(filepath, FILE_LIST_PATCHES):
        files_modified += 1
    
    # Task #41: file_finder.py
    filepath = os.path.join(base_dir, "src/utils/file_finder.py")
    if apply_patch(filepath, FILE_FINDER_PATCHES):
        files_modified += 1
    
    # Task #43: json_translate_dock.py
    filepath = os.path.join(base_dir, "src/gui/json_translate_dock.py")
    if apply_patch(filepath, JSON_TRANSLATE_PATCHES):
        files_modified += 1
    
    print("\\n" + "=" * 60)
    print(f"✅ Patches aplicados! {files_modified} arquivo(s) modificado(s)")
    print("=" * 60)
    print("\\nPróximos passos:")
    print("1. Revisar mudanças: git diff")
    print("2. Testar manualmente as features")
    print("3. Commitar separadamente as 4 tasks")
    print("4. Push para GitHub")

if __name__ == "__main__":
    main()
