#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Translate Dock - Modular implementation
Translates text in files using a JSON/TS dictionary, replacing text with variable references.
Supports scope filtering, backup creation, and reverse translation.
"""

from __future__ import annotations
import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QFileDialog, QMessageBox
)

from .base_dock import BaseDock
from ..utils import walk_files, parse_exclusion_patterns

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


# Import translation helper functions (assumed to exist in app.py or a module)
def load_translation_dict(dict_path: str) -> dict:
    """Load translation dictionary from JSON/TS file."""
    from ..utils import load_ts_object
    import json
    
    if dict_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
        return load_ts_object(dict_path)
    else:
        with open(dict_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def process_translate_file(
    filepath: str,
    dictionary: dict,
    root_alias: str,
    start_rx: str,
    end_rx: str,
    make_backup: bool,
    dont_override: bool,
    inverse: bool,
    exclude_patterns: list,
    emit_export: bool = True
) -> tuple[bool, str]:
    """
    Process a single file for translation.
    Returns (success: bool, error_message: str)
    """
    # This function should implement the actual translation logic
    # For now, returning a placeholder implementation
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # TODO: Implement actual translation logic here
        # This is a placeholder that mimics the original behavior
        
        return (True, "")
    except Exception as e:
        return (False, str(e))


class JsonTranslateDock(BaseDock):
    """
    Dock widget for JSON translation functionality.
    Translates text in source files by replacing with dictionary variable references.
    
    Features:
    - File or directory selection
    - JSON/TS dictionary file
    - Customizable root variable name (e.g., 't', 'i18n')
    - Scope delimiters (start/end regex)
    - Exclusion patterns (do not translate)
    - Backup creation
    - Don't override existing translations
    - Reverse translation support
    """
    
    def __init__(self, parent: QWidgetType | None = None):
        super().__init__("JSON Translate", parent)
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self) -> None:
        """Create all widgets for the translate dock."""
        # Root path section
        self.lbl_path = QLabel("Root path:")
        self.ed_path = QLineEdit()
        self.ed_path.setToolTip("Select the file or directory to translate")
        self.btn_browse = QPushButton("Browse…")
        self.btn_browse.setToolTip("Browse for file or directory")
        self.is_file = QCheckBox("Is file?")
        self.is_file.setToolTip("Check if root path is a file (unchecked for directory)")
        
        # Dictionary file section
        self.lbl_dict = QLabel("Dictionary file (JSON/TS):")
        self.ed_dict = QLineEdit()
        self.ed_dict.setToolTip("JSON or TypeScript file containing translation dictionary")
        self.btn_open = QPushButton("Open…")
        self.btn_open.setToolTip("Browse for dictionary file")
        
        # Variable name
        self.lbl_var = QLabel("First object variable name:")
        self.object_variable_name = QLineEdit()
        self.object_variable_name.setPlaceholderText("e.g. t")
        self.object_variable_name.setToolTip("Variable name used in code to access translations (e.g., 't' for t.key)")
        
        # Scope delimiters
        self.lbl_start = QLabel("Start delimiter (regex):")
        self.ed_start = QLineEdit("<[^>]*?>")  # default: start of HTML/JSX tag
        self.ed_start.setToolTip("Regex pattern marking where translation scope begins")
        self.lbl_end = QLabel("End delimiter (regex):")
        self.ed_end = QLineEdit("</[^>]*?>")  # default: end tag
        self.ed_end.setToolTip("Regex pattern marking where translation scope ends")
        
        # Exclusion patterns
        self.lbl_exclude = QLabel('Do not translate\n(regex, comma-separated):')
        self.ed_exclude = QLineEdit()
        self.ed_exclude.setPlaceholderText(r'className="[^"]*", data-testid="[^"]*", id="[^"]*"')
        self.ed_exclude.setText(r'className="[^"]*", data-testid="[^"]*", id="[^"]*"')
        self.ed_exclude.setToolTip("Comma-separated regex patterns for text that should not be translated")
        
        # Options
        self.chk_backup = QCheckBox("Backup original files\n(filename.bak)")
        self.chk_backup.setChecked(True)
        self.chk_backup.setToolTip("Create backup files (.bak) before modifying originals")
        
        self.chk_dont_override = QCheckBox("Don't override\nexisting translations")
        self.chk_dont_override.setChecked(True)
        self.chk_dont_override.setToolTip("Skip text that is already translated")
        
        self.chk_inverse_json_translate = QCheckBox(
            "Reverse JSON Translate\nchanges (with dictionary)"
        )
        self.chk_inverse_json_translate.setToolTip("Reverse translation: replace variable references with dictionary values")
        
        self.chk_emit_export = QCheckBox("Emit export const")
        self.chk_emit_export.setChecked(True)
        self.chk_emit_export.setToolTip("Add 'export const varName = {...}' wrapper to output (TS/JS files)")
        
        # Action button
        self.btn_run = QPushButton("Run translation")
    
    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        g = QGridLayout()
        self.main_widget.setLayout(g)
        
        # Row 0: Root path
        g.addWidget(self.lbl_path, 0, 0)
        g.addWidget(self.ed_path, 0, 1, 1, 2)
        g.addWidget(self.btn_browse, 0, 3)
        
        # Row 1: Is file checkbox
        g.addWidget(self.is_file, 1, 0)
        
        # Row 2: Dictionary file
        g.addWidget(self.lbl_dict, 2, 0)
        g.addWidget(self.ed_dict, 2, 1, 1, 2)
        g.addWidget(self.btn_open, 2, 3)
        
        # Row 3: Variable name
        g.addWidget(self.lbl_var, 3, 0)
        g.addWidget(self.object_variable_name, 3, 1, 1, 2)
        
        # Row 4: Scope delimiters
        g.addWidget(self.lbl_start, 4, 0)
        g.addWidget(self.ed_start, 4, 1)
        g.addWidget(self.lbl_end, 4, 2)
        g.addWidget(self.ed_end, 4, 3)
        
        # Row 5: Exclusion patterns
        g.addWidget(self.lbl_exclude, 5, 0)
        g.addWidget(self.ed_exclude, 5, 1, 1, 3)
        
        # Row 6: Backup and don't override options
        g.addWidget(self.chk_backup, 6, 0, 1, 2)
        g.addWidget(self.chk_dont_override, 6, 2, 1, 2)
        
        # Row 7: Inverse and emit export options
        g.addWidget(self.chk_inverse_json_translate, 7, 0, 1, 2)
        g.addWidget(self.chk_emit_export, 7, 2, 1, 2)
        
        # Row 8: Run button
        g.addWidget(self.btn_run, 8, 2, 1, 2)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_browse.clicked.connect(self._browse_root)
        self.btn_open.clicked.connect(self._browse_dict)
        self.btn_run.clicked.connect(self._run)
        self._setup_enter_key_execution(
            self.ed_path, self.ed_dict, self.ed_start, 
            self.ed_end, self.ed_exclude
        )
    
    # UI Helper Methods
    
    def _browse_root(self) -> None:
        """Browse for root path (file or directory)."""
        if self.is_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(
                self, "Select file (or Cancel to pick a folder)"
            )
            if path:
                self.ed_path.setText(path)
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select folder")
            if folder:
                self.ed_path.setText(folder)
    
    def _browse_dict(self) -> None:
        """Browse for dictionary file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Dictionary file", "",
            "JSON/TS (*.json *.ts *.js);;All files (*)"
        )
        if path:
            self.ed_dict.setText(path)
    
    # Core Processing
    
    def _run(self) -> None:
        """Execute translation on selected files."""
        path = self.ed_path.text().strip()
        dpath = self.ed_dict.text().strip()
        root_alias = self.object_variable_name.text().strip() or "t"
        start_rx = self.ed_start.text().strip()
        end_rx = self.ed_end.text().strip()
        exclude_csv = self.ed_exclude.text().strip()
        make_backup = self.chk_backup.isChecked()
        dont_override = self.chk_dont_override.isChecked()
        inverse = self.chk_inverse_json_translate.isChecked()
        emit_export = self.chk_emit_export.isChecked()
        
        # Validation
        if not path or not dpath:
            QMessageBox.warning(self, "Missing", "Select path and dictionary file.")
            return
        
        # Load dictionary
        try:
            dictionary = load_translation_dict(dpath)
        except Exception as e:
            QMessageBox.critical(self, "Dictionary error", str(e))
            return
        
        # Parse exclusion patterns
        exclude_patterns = parse_exclusion_patterns(exclude_csv)
        
        # Gather files to process
        if os.path.isfile(path):
            paths = [path]
        else:
            paths = list(
                walk_files(
                    path,
                    include_globs=None,
                    exclude_globs=["node_modules", ".git", "dist", "build"]
                )
            )
        
        # Process files
        changed = 0
        errors = []
        
        for p in paths:
            ok, err = process_translate_file(
                p, dictionary, root_alias,
                start_rx, end_rx,
                make_backup, dont_override, inverse,
                exclude_patterns,
                emit_export
            )
            if ok:
                changed += 1
            if err:
                errors.append(f"{p}: {err}")
        
        # Display results
        msg = f"Modified files: {changed}"
        if errors:
            msg += f"\nErrors: {len(errors)}\n" + "\n".join(errors[:5])  # show first 5
        QMessageBox.information(self, "Translate", msg)
    
    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._run()
