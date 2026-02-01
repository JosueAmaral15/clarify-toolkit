#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Search Dialog - Find keys/values in JSON

Extracted from json_editor_tab.py (v2.9.114 - Phase 2.6.2)
Provides search functionality for JSON content with regex support.

Features:
- Find All with regex patterns
- Case sensitive option
- Keys Only / Values Only filters
- Next/Previous navigation
- Yellow highlight for matches
- Match counter: "Match X of Y"

Pattern: Command (GoF) - encapsulates search operation as object
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=line-too-long  # Long regex patterns

from __future__ import annotations
import re

from typing import List, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCursor, QTextCharFormat
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox,
    QPushButton, QTextEdit, QVBoxLayout
)

from src.i18n.translator import tr


class JsonSearchDialog(QDialog):
    """
    Search dialog for finding keys/values in JSON.

    Pattern: Command (GoF)
    - Encapsulates search operation as object
    - Easy to add undo/redo, history

    Features:
    - Case sensitive search
    - Keys only / Values only filters
    - Regex pattern matching
    - Navigation between matches
    - Visual highlighting
    """

    def __init__(self, editor: QTextEdit, parent=None):
        """
        Initialize search dialog.

        Args:
            editor: QTextEdit to search in
            parent: Parent widget
        """
        super().__init__(parent)
        self.editor = editor
        self.current_match_index = -1
        self.matches: List[Tuple[int, int]] = []  # [(start, length), ...]

        self.setWindowTitle(tr("json_search_dialog.window_title"))
        self.setMinimumWidth(500)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup search dialog UI."""
        layout = QVBoxLayout(self)

        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(tr("json_search.lbl_find")))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("json_search.placeholder"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Options
        options_layout = QHBoxLayout()
        self.chk_case_sensitive = QCheckBox(tr("json_search.chk_case_sensitive"))
        self.chk_keys_only = QCheckBox(tr("json_search.chk_keys_only"))
        self.chk_values_only = QCheckBox(tr("json_search.chk_values_only"))
        options_layout.addWidget(self.chk_case_sensitive)
        options_layout.addWidget(self.chk_keys_only)
        options_layout.addWidget(self.chk_values_only)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Results label
        self.lbl_results = QLabel(tr("json_search.lbl_results"))
        self.lbl_results.setStyleSheet("color: #6A9955;")
        layout.addWidget(self.lbl_results)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_find = QPushButton(tr("json_search.btn_find_all"))
        self.btn_next = QPushButton(tr("json_search.btn_next"))
        self.btn_prev = QPushButton(tr("json_search.btn_prev"))
        self.btn_close = QPushButton(tr("json_search.btn_close"))

        self.btn_next.setEnabled(False)
        self.btn_prev.setEnabled(False)

        btn_layout.addWidget(self.btn_find)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        """Connect button signals."""
        self.btn_find.clicked.connect(self._find_all)
        self.btn_next.clicked.connect(self._find_next)
        self.btn_prev.clicked.connect(self._find_prev)
        self.btn_close.clicked.connect(self.close)
        self.search_input.returnPressed.connect(self._find_all)

    def _find_all(self):
        """
        Find all matches in editor.

        Pattern: Command (GoF) - execute search command
        """
        search_text = self.search_input.text()
        if not search_text:
            return

        # Clear previous highlights
        self._clear_highlights()
        self.matches.clear()
        self.current_match_index = -1

        # Get editor text
        text = self.editor.toPlainText()

        # Case sensitivity
        if self.chk_case_sensitive.isChecked():
            search_flags = 0
        else:
            search_flags = re.IGNORECASE

        # Search pattern
        if self.chk_keys_only.isChecked():
            # Search only in keys: "key":
            pattern = rf'"{re.escape(search_text)}"(?=\s*:)'
        elif self.chk_values_only.isChecked():
            # Search only in values: : "value"
            pattern = rf':\s*"[^"]*{re.escape(search_text)}[^"]*"'
        else:
            # Search everywhere
            pattern = re.escape(search_text)

        # Find all matches
        try:
            for match in re.finditer(pattern, text, search_flags):
                self.matches.append((match.start(), len(match.group())))
        except re.error:
            QMessageBox.warning(self, tr("json_search_dialog.msg_invalid_pattern_title"), tr("json_search_dialog.msg_invalid_pattern"))
            return

        # Update results label
        self.lbl_results.setText(f"{len(self.matches)} matches found")

        # Enable navigation buttons
        if self.matches:
            self.btn_next.setEnabled(True)
            self.btn_prev.setEnabled(True)
            self.current_match_index = 0
            self._highlight_current_match()
        else:
            self.btn_next.setEnabled(False)
            self.btn_prev.setEnabled(False)

    def _find_next(self):
        """Navigate to next match."""
        if not self.matches:
            return

        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._highlight_current_match()

    def _find_prev(self):
        """Navigate to previous match."""
        if not self.matches:
            return

        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self._highlight_current_match()

    def _highlight_current_match(self):
        """Highlight current match in editor with yellow background."""
        if not self.matches or self.current_match_index < 0:
            return

        start, length = self.matches[self.current_match_index]

        # Move cursor to match
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(start + length, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)

        # Highlight with yellow background
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#FFFF00"))  # Yellow
        cursor.mergeCharFormat(fmt)

        # Update results label
        self.lbl_results.setText(f"Match {self.current_match_index + 1} of {len(self.matches)}")

    def _clear_highlights(self):
        """Clear all highlights in editor."""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor())  # Clear background
        cursor.mergeCharFormat(fmt)


__all__ = ['JsonSearchDialog']
