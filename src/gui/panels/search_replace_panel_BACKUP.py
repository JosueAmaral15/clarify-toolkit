#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Search/Replace Panel - Reusable Component

Provides UI for search and replace operations with:
- Case sensitivity toggle
- Whole word matching
- Regex support
- Preserve case option
- Replace count limit

Pattern: Composite (GoF) + Observer (signals)
- Reusable component
- Signal-based communication
- QSettings persistence

Integration:
- Can be added to any dock/editor
- Emits replace_requested signal with parameters
- Parent handles actual replacement logic
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QGroupBox, QMessageBox
)

from src.core.search_replace import SearchOptions, replace_in_text


class SearchReplacePanel(QWidget):
    """
    Reusable search/replace panel widget.
    
    Signals:
        replace_requested(needle, replacement, options, preserve_case, count)
    
    Features:
    - Case sensitive/insensitive matching
    - Whole word matching
    - Regex support
    - Preserve case (ALL CAPS, Capitalized, lower)
    - Replace count (0 = all occurrences)
    - QSettings persistence
    
    Usage:
        panel = SearchReplacePanel()
        panel.replace_requested.connect(self._handle_replace)
        layout.addWidget(panel)
    """
    
    # Signal emitted when replace is requested
    # Parameters: (needle: str, replacement: str, options: SearchOptions, 
    #              preserve_case: bool, count: int)
    replace_requested = Signal(str, str, SearchOptions, bool, int)
    
    def __init__(self, parent=None, settings_prefix: str = "search_replace"):
        """
        Initialize search/replace panel.
        
        Args:
            parent: Parent widget
            settings_prefix: QSettings key prefix for persistence
        """
        super().__init__(parent)
        self.settings_prefix = settings_prefix
        self.settings = QSettings("Clarify", "Clarify")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Group box
        group = QGroupBox("Search && Replace")
        group_layout = QGridLayout()
        
        # Search input
        group_layout.addWidget(QLabel("Find:"), 0, 0)
        self.ed_needle = QLineEdit()
        self.ed_needle.setPlaceholderText("Search text or regex pattern...")
        group_layout.addWidget(self.ed_needle, 0, 1, 1, 2)
        
        # Replace input
        group_layout.addWidget(QLabel("Replace:"), 1, 0)
        self.ed_replacement = QLineEdit()
        self.ed_replacement.setPlaceholderText("Replacement text...")
        group_layout.addWidget(self.ed_replacement, 1, 1, 1, 2)
        
        # Options row 1
        options_layout1 = QHBoxLayout()
        self.chk_case_sensitive = QCheckBox("Case sensitive")
        self.chk_case_sensitive.setToolTip("Match case exactly (A ≠ a)")
        options_layout1.addWidget(self.chk_case_sensitive)
        
        self.chk_whole_word = QCheckBox("Whole word")
        self.chk_whole_word.setToolTip("Match whole words only (cat won't match in 'category')")
        options_layout1.addWidget(self.chk_whole_word)
        
        self.chk_regex = QCheckBox("Regex")
        self.chk_regex.setToolTip("Treat search text as regular expression")
        options_layout1.addWidget(self.chk_regex)
        options_layout1.addStretch()
        
        group_layout.addLayout(options_layout1, 2, 0, 1, 3)
        
        # Options row 2
        options_layout2 = QHBoxLayout()
        self.chk_preserve_case = QCheckBox("Preserve case")
        self.chk_preserve_case.setToolTip(
            "Preserve case pattern:\n"
            "• ALL CAPS → ALL CAPS\n"
            "• Capitalized → Capitalized\n"
            "• lower → lower"
        )
        options_layout2.addWidget(self.chk_preserve_case)
        
        options_layout2.addWidget(QLabel("Count:"))
        self.spin_count = QSpinBox()
        self.spin_count.setMinimum(0)
        self.spin_count.setMaximum(999999)
        self.spin_count.setValue(0)
        self.spin_count.setSpecialValueText("All")
        self.spin_count.setToolTip("Number of replacements (0 = all occurrences)")
        self.spin_count.setMaximumWidth(100)
        options_layout2.addWidget(self.spin_count)
        options_layout2.addStretch()
        
        group_layout.addLayout(options_layout2, 3, 0, 1, 3)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_replace = QPushButton("🔄 Replace")
        self.btn_replace.setToolTip("Execute replacement operation")
        self.btn_replace.clicked.connect(self._execute_replace)
        btn_layout.addWidget(self.btn_replace)
        
        self.btn_test = QPushButton("🧪 Test Pattern")
        self.btn_test.setToolTip("Test regex pattern (shows compiled pattern)")
        self.btn_test.clicked.connect(self._test_pattern)
        btn_layout.addWidget(self.btn_test)
        
        btn_layout.addStretch()
        group_layout.addLayout(btn_layout, 4, 0, 1, 3)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def _execute_replace(self):
        """Execute replace operation - emits signal."""
        needle = self.ed_needle.text().strip()
        if not needle:
            QMessageBox.warning(self, "Empty Search", "Please enter search text.")
            return
        
        replacement = self.ed_replacement.text()
        
        # Build SearchOptions
        options = SearchOptions(
            case_sensitive=self.chk_case_sensitive.isChecked(),
            whole_word=self.chk_whole_word.isChecked(),
            regex=self.chk_regex.isChecked()
        )
        
        preserve_case = self.chk_preserve_case.isChecked()
        count = self.spin_count.value()
        
        # Save settings
        self._save_settings()
        
        # Emit signal for parent to handle
        self.replace_requested.emit(needle, replacement, options, preserve_case, count)
    
    def _test_pattern(self):
        """Test regex pattern - shows compiled pattern."""
        needle = self.ed_needle.text().strip()
        if not needle:
            QMessageBox.warning(self, "Empty Pattern", "Please enter search text.")
            return
        
        options = SearchOptions(
            case_sensitive=self.chk_case_sensitive.isChecked(),
            whole_word=self.chk_whole_word.isChecked(),
            regex=self.chk_regex.isChecked()
        )
        
        try:
            pattern = compile(needle, options)
            QMessageBox.information(
                self, 
                "Pattern Valid ✓", 
                f"Compiled regex pattern:\n\n{pattern.pattern}\n\n"
                f"Flags: {'IGNORECASE' if pattern.flags else 'None'}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Pattern Error ✗", 
                f"Invalid regex pattern:\n\n{str(e)}"
            )
    
    def _save_settings(self):
        """Save current options to QSettings."""
        self.settings.setValue(f"{self.settings_prefix}/case_sensitive", 
                              self.chk_case_sensitive.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/whole_word", 
                              self.chk_whole_word.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/regex", 
                              self.chk_regex.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/preserve_case", 
                              self.chk_preserve_case.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/count", 
                              self.spin_count.value())
        self.settings.setValue(f"{self.settings_prefix}/last_needle", 
                              self.ed_needle.text())
        self.settings.setValue(f"{self.settings_prefix}/last_replacement", 
                              self.ed_replacement.text())
    
    def _load_settings(self):
        """Load saved options from QSettings."""
        self.chk_case_sensitive.setChecked(
            self.settings.value(f"{self.settings_prefix}/case_sensitive", False, bool)
        )
        self.chk_whole_word.setChecked(
            self.settings.value(f"{self.settings_prefix}/whole_word", False, bool)
        )
        self.chk_regex.setChecked(
            self.settings.value(f"{self.settings_prefix}/regex", False, bool)
        )
        self.chk_preserve_case.setChecked(
            self.settings.value(f"{self.settings_prefix}/preserve_case", False, bool)
        )
        self.spin_count.setValue(
            self.settings.value(f"{self.settings_prefix}/count", 0, int)
        )
        self.ed_needle.setText(
            self.settings.value(f"{self.settings_prefix}/last_needle", "", str)
        )
        self.ed_replacement.setText(
            self.settings.value(f"{self.settings_prefix}/last_replacement", "", str)
        )
    
    def get_options(self) -> SearchOptions:
        """Get current SearchOptions."""
        return SearchOptions(
            case_sensitive=self.chk_case_sensitive.isChecked(),
            whole_word=self.chk_whole_word.isChecked(),
            regex=self.chk_regex.isChecked()
        )
    
    def get_needle(self) -> str:
        """Get search text."""
        return self.ed_needle.text().strip()
    
    def get_replacement(self) -> str:
        """Get replacement text."""
        return self.ed_replacement.text()
    
    def get_preserve_case(self) -> bool:
        """Get preserve case option."""
        return self.chk_preserve_case.isChecked()
    
    def get_count(self) -> int:
        """Get replace count."""
        return self.spin_count.value()
    
    def set_needle(self, text: str):
        """Set search text."""
        self.ed_needle.setText(text)
    
    def set_replacement(self, text: str):
        """Set replacement text."""
        self.ed_replacement.setText(text)
    
    def clear_inputs(self):
        """Clear both input fields."""
        self.ed_needle.clear()
        self.ed_replacement.clear()
