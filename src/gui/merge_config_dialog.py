#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge Configuration Dialog - Select merge mode and target file

Allows user to configure how Set Operations results will be merged
back to original files with mode selection and file picker.

v2.9.100 - Merge Results to File
Author: Josué Amaral
Date: 2025-12-23
"""

import os
from typing import Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QLabel, QPushButton, QFileDialog,
    QLineEdit, QCheckBox, QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MergeConfigDialog(QDialog):
    """Dialog for configuring merge operation parameters."""
    
    def __init__(self, default_file: str, parent=None):
        """
        Initialize MergeConfigDialog.
        
        Args:
            default_file: Default file path to merge to
            parent: Parent widget
        """
        super().__init__(parent)
        self.default_file = default_file
        self.selected_mode = "merge"
        self.selected_file = default_file
        self.auto_backup = True
        self.max_backups = 5
        
        self.setWindowTitle("Merge Configuration - v2.9.100")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # === Info Section ===
        info_label = QLabel(
            "Configure how Set Operations results will be merged back to the original file.\n"
            "Preview will be shown before applying changes."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #6A9955; font-style: italic;")
        layout.addWidget(info_label)
        
        # === File Selection ===
        file_group = QGroupBox("Target File")
        file_layout = QVBoxLayout()
        
        file_row = QHBoxLayout()
        self.ed_file = QLineEdit(self.default_file)
        self.ed_file.setReadOnly(True)
        self.ed_file.setToolTip("File to merge results into")
        
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.setToolTip("Select different target file")
        self.btn_browse.clicked.connect(self._browse_file)
        
        file_row.addWidget(self.ed_file)
        file_row.addWidget(self.btn_browse)
        file_layout.addLayout(file_row)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # === Merge Mode Selection ===
        mode_group = QGroupBox("Merge Mode")
        mode_layout = QVBoxLayout()
        
        self.radio_replace = QRadioButton("Replace")
        self.radio_replace.setToolTip(
            "Overwrite entire file with result data (creates backup first)"
        )
        font_bold = QFont()
        font_bold.setBold(True)
        label_replace = QLabel("Complete replacement - original content lost")
        label_replace.setStyleSheet("color: #CE9178; margin-left: 20px;")
        
        self.radio_merge = QRadioButton("Merge")
        self.radio_merge.setChecked(True)
        self.radio_merge.setToolTip(
            "Deep merge result into existing file (result keys overwrite original)"
        )
        label_merge = QLabel("Intelligent merge - preserves original keys not in result")
        label_merge.setStyleSheet("color: #6A9955; margin-left: 20px;")
        
        self.radio_new_file = QRadioButton("New File")
        self.radio_new_file.setToolTip(
            "Create new file with '_merged' suffix (original untouched)"
        )
        label_new = QLabel("Safest option - creates data_merged.json")
        label_new.setStyleSheet("color: #4EC9B0; margin-left: 20px;")
        
        mode_layout.addWidget(self.radio_replace)
        mode_layout.addWidget(label_replace)
        mode_layout.addSpacing(10)
        mode_layout.addWidget(self.radio_merge)
        mode_layout.addWidget(label_merge)
        mode_layout.addSpacing(10)
        mode_layout.addWidget(self.radio_new_file)
        mode_layout.addWidget(label_new)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # === Backup Options ===
        backup_group = QGroupBox("Backup Options")
        backup_layout = QVBoxLayout()
        
        self.chk_auto_backup = QCheckBox("Automatic backup before merge (recommended)")
        self.chk_auto_backup.setChecked(True)
        self.chk_auto_backup.setToolTip(
            "Creates .bak file with timestamp before overwriting (only for Replace/Merge modes)"
        )
        backup_layout.addWidget(self.chk_auto_backup)
        
        backup_row = QHBoxLayout()
        backup_label = QLabel("Maximum backups to keep:")
        backup_label.setToolTip("Older backups are automatically deleted")
        
        self.spin_max_backups = QSpinBox()
        self.spin_max_backups.setRange(1, 20)
        self.spin_max_backups.setValue(5)
        self.spin_max_backups.setToolTip("Number of backup files to retain per file")
        
        backup_row.addWidget(backup_label)
        backup_row.addWidget(self.spin_max_backups)
        backup_row.addStretch()
        backup_layout.addLayout(backup_row)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # === Action Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_preview = QPushButton("Preview Merge")
        self.btn_preview.setToolTip("Show preview before applying changes")
        self.btn_preview.clicked.connect(self._accept)
        self.btn_preview.setDefault(True)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setToolTip("Cancel merge operation")
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_preview)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
    
    def _browse_file(self):
        """Open file browser to select target file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Target File",
            os.path.dirname(self.default_file),
            "JSON Files (*.json)"
        )
        
        if file_path:
            self.ed_file.setText(file_path)
    
    def _accept(self):
        """Validate and accept dialog."""
        # Get selected mode
        if self.radio_replace.isChecked():
            self.selected_mode = "replace"
        elif self.radio_merge.isChecked():
            self.selected_mode = "merge"
        else:
            self.selected_mode = "new_file"
        
        # Get selected file
        self.selected_file = self.ed_file.text()
        
        # Validate file exists
        if not os.path.exists(self.selected_file):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Target file does not exist:\n{self.selected_file}"
            )
            return
        
        # Get backup options
        self.auto_backup = self.chk_auto_backup.isChecked()
        self.max_backups = self.spin_max_backups.value()
        
        # Warn if replace mode without backup
        if self.selected_mode == "replace" and not self.auto_backup:
            reply = QMessageBox.question(
                self,
                "No Backup",
                "You selected Replace mode without backup.\n"
                "Original file will be permanently overwritten.\n\n"
                "Continue without backup?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.accept()
    
    def get_config(self) -> Tuple[str, str, bool, int]:
        """
        Get merge configuration.
        
        Returns:
            Tuple of (mode, file_path, auto_backup, max_backups)
        """
        return (
            self.selected_mode,
            self.selected_file,
            self.auto_backup,
            self.max_backups
        )
