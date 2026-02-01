#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Insert Panel - Reusable Component

Provides UI for inserting text at specific lines with 5 modes:
- LEFT: Insert text at beginning of line
- RIGHT: Append text at end of line
- REPLACE: Replace entire line
- INSERT_ABOVE: Insert new line above target
- INSERT_BELOW: Insert new line below target

Pattern: Composite (GoF) + Observer (signals)
- Reusable component
- Signal-based communication
- QSettings persistence

Integration:
- Can be added to any dock/editor
- Emits insert_requested signal with parameters
- Parent handles actual insertion logic
"""

from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox,
    QComboBox, QGroupBox, QMessageBox
)

from src.core.insert import InsertMode, insert_at_line


class InsertPanel(QWidget):
    """
    Reusable insert panel widget.

    Signals:
        insert_requested(line_no, text, mode)

    Features:
    - Line number selection (1-based)
    - Multi-line text input
    - 5 insertion modes
    - QSettings persistence
    - Quick mode buttons

    Usage:
        panel = InsertPanel()
        panel.insert_requested.connect(self._handle_insert)
        layout.addWidget(panel)
    """

    # Signal emitted when insert is requested
    # Parameters: (line_no: int, text: str, mode: str)
    insert_requested = Signal(int, str, str)

    def __init__(self, parent=None, settings_prefix: str = "insert"):
        """
        Initialize insert panel.

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
        group = QGroupBox("Insert Text")
        group_layout = QVBoxLayout()

        # Line number input
        line_layout = QHBoxLayout()
        line_layout.addWidget(QLabel("Line:"))
        self.spin_line = QSpinBox()
        self.spin_line.setMinimum(1)
        self.spin_line.setMaximum(999999)
        self.spin_line.setValue(1)
        self.spin_line.setToolTip("Target line number (1-based)")
        self.spin_line.setMaximumWidth(100)
        line_layout.addWidget(self.spin_line)

        line_layout.addWidget(QLabel("Mode:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            InsertMode.LEFT,
            InsertMode.RIGHT,
            InsertMode.REPLACE,
            InsertMode.INSERT_ABOVE,
            InsertMode.INSERT_BELOW
        ])
        self.combo_mode.setToolTip(
            "Insertion modes:\n"
            "• LEFT: Insert at line start\n"
            "• RIGHT: Append at line end\n"
            "• REPLACE: Replace entire line\n"
            "• INSERT_ABOVE: New line above\n"
            "• INSERT_BELOW: New line below"
        )
        line_layout.addWidget(self.combo_mode)
        line_layout.addStretch()

        group_layout.addLayout(line_layout)

        # Text input
        group_layout.addWidget(QLabel("Text:"))
        self.text_insert = QTextEdit()
        self.text_insert.setPlaceholderText("Enter text to insert (supports multi-line)...")
        self.text_insert.setMaximumHeight(80)
        self.text_insert.setToolTip("Text to insert (can be multi-line)")
        group_layout.addWidget(self.text_insert)

        # Quick mode buttons
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(QLabel("Quick:"))

        self.btn_left = QPushButton("← Left")
        self.btn_left.setToolTip("Insert at line start (LEFT mode)")
        self.btn_left.clicked.connect(lambda: self._quick_insert(InsertMode.LEFT))
        quick_layout.addWidget(self.btn_left)

        self.btn_right = QPushButton("Right →")
        self.btn_right.setToolTip("Append at line end (RIGHT mode)")
        self.btn_right.clicked.connect(lambda: self._quick_insert(InsertMode.RIGHT))
        quick_layout.addWidget(self.btn_right)

        self.btn_replace = QPushButton("🔄 Replace")
        self.btn_replace.setToolTip("Replace entire line (REPLACE mode)")
        self.btn_replace.clicked.connect(lambda: self._quick_insert(InsertMode.REPLACE))
        quick_layout.addWidget(self.btn_replace)

        quick_layout.addStretch()
        group_layout.addLayout(quick_layout)

        # Main action buttons
        btn_layout = QHBoxLayout()
        self.btn_insert = QPushButton("📝 Insert")
        self.btn_insert.setToolTip("Execute insertion with selected mode")
        self.btn_insert.clicked.connect(self._execute_insert)
        btn_layout.addWidget(self.btn_insert)

        self.btn_preview = QPushButton("👁️ Preview")
        self.btn_preview.setToolTip("Preview how text will be inserted")
        self.btn_preview.clicked.connect(self._preview_insert)
        btn_layout.addWidget(self.btn_preview)

        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def _execute_insert(self):
        """Execute insert operation - emits signal."""
        line_no = self.spin_line.value()
        text = self.text_insert.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter text to insert.")
            return

        mode = self.combo_mode.currentText()

        # Save settings
        self._save_settings()

        # Emit signal for parent to handle
        self.insert_requested.emit(line_no, text, mode)

    def _quick_insert(self, mode: str):
        """Quick insert with specific mode."""
        self.combo_mode.setCurrentText(mode)
        self._execute_insert()

    def _preview_insert(self):
        """Preview how text will be inserted."""
        line_no = self.spin_line.value()
        text = self.text_insert.toPlainText().strip()
        mode = self.combo_mode.currentText()

        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter text to insert.")
            return

        # Create sample content for preview
        sample_content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        try:
            result = insert_at_line(sample_content, line_no, text, mode)
            QMessageBox.information(
                self,
                f"Preview: {mode} at Line {line_no}",
                f"Sample content BEFORE:\n{sample_content}\n\n"
                f"Sample content AFTER:\n{result}\n\n"
                f"Text inserted: '{text}'"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Preview Error",
                f"Error during preview:\n\n{str(e)}"
            )

    def _save_settings(self):
        """Save current options to QSettings."""
        self.settings.setValue(f"{self.settings_prefix}/line",
                              self.spin_line.value())
        self.settings.setValue(f"{self.settings_prefix}/mode",
                              self.combo_mode.currentText())
        self.settings.setValue(f"{self.settings_prefix}/last_text",
                              self.text_insert.toPlainText())

    def _load_settings(self):
        """Load saved options from QSettings."""
        self.spin_line.setValue(
            self.settings.value(f"{self.settings_prefix}/line", 1, int)
        )
        mode = self.settings.value(f"{self.settings_prefix}/mode",
                                   InsertMode.REPLACE, str)
        index = self.combo_mode.findText(mode)
        if index >= 0:
            self.combo_mode.setCurrentIndex(index)

        self.text_insert.setPlainText(
            self.settings.value(f"{self.settings_prefix}/last_text", "", str)
        )

    def get_line_number(self) -> int:
        """Get target line number."""
        return self.spin_line.value()

    def get_text(self) -> str:
        """Get insertion text."""
        return self.text_insert.toPlainText().strip()

    def get_mode(self) -> str:
        """Get insertion mode."""
        return self.combo_mode.currentText()

    def set_line_number(self, line: int):
        """Set target line number."""
        self.spin_line.setValue(line)

    def set_text(self, text: str):
        """Set insertion text."""
        self.text_insert.setPlainText(text)

    def set_mode(self, mode: str):
        """Set insertion mode."""
        index = self.combo_mode.findText(mode)
        if index >= 0:
            self.combo_mode.setCurrentIndex(index)

    def clear_text(self):
        """Clear text input."""
        self.text_insert.clear()
