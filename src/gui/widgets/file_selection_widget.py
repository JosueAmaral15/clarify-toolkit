#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Selection Widget - Reusable file selection component

Extracted from set_operations_dock.py (v2.9.114 - Phase 2.3.1)
Provides UI and logic for selecting one or multiple files with pipeline support.

Features:
- Two-file mode (File A/B)
- Multiple files mode (pipeline)
- Browse/Add/Remove/Clear operations
- Signals for file changes
"""

from __future__ import annotations

from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QWidget,
)

from src.i18n import tooltip_tr
from src.i18n.translator import tr
from src.accessibility_manager import AccessibilityManager


class FileSelectionWidget(QWidget):
    """Widget for selecting one or multiple files with pipeline support."""

    # Signal emitted when file list changes
    files_changed = Signal(list)  # List[str]

    def __init__(self,
                 title: str = "File Selection",
                 file_filter: str = "JSON Files (*.json);;All Files (*)",
                 parent: QWidget | None = None):
        """
        Initialize file selection widget.

        Args:
            title: Group box title
            file_filter: File dialog filter
            parent: Parent widget
        """
        super().__init__(parent)
        self.file_filter = file_filter
        self._setup_ui(title)
        self._connect_signals()
        self._apply_accessibility()

    def _setup_ui(self, title: str) -> None:
        """Setup UI components."""
        # Create group box
        file_group = QGroupBox(title)
        file_layout = QGridLayout()

        # File A
        file_layout.addWidget(QLabel(tr("file_selection.lbl_file_a")), 0, 0)
        self.ed_file_a = QLineEdit()
        self.ed_file_a.setPlaceholderText(tr("file_selection.placeholder_a"))
        self.ed_file_a.setToolTip(tooltip_tr("set_ops.file_a"))
        file_layout.addWidget(self.ed_file_a, 0, 1)
        self.btn_browse_a = QPushButton(tr("file_selection.btn_browse_a"))
        self.btn_browse_a.setMaximumWidth(100)
        self.btn_browse_a.setToolTip(tooltip_tr("set_ops.btn_browse_a"))
        file_layout.addWidget(self.btn_browse_a, 0, 2)

        # File B
        file_layout.addWidget(QLabel(tr("file_selection.lbl_file_b")), 1, 0)
        self.ed_file_b = QLineEdit()
        self.ed_file_b.setPlaceholderText(tr("file_selection.placeholder_b"))
        self.ed_file_b.setToolTip(tooltip_tr("set_ops.file_b"))
        file_layout.addWidget(self.ed_file_b, 1, 1)
        self.btn_browse_b = QPushButton(tr("file_selection.btn_browse_b"))
        self.btn_browse_b.setMaximumWidth(100)
        self.btn_browse_b.setToolTip(tooltip_tr("set_ops.btn_browse_b"))
        file_layout.addWidget(self.btn_browse_b, 1, 2)

        # Multiple files checkbox
        self.chk_multiple = QCheckBox(tr("file_selection.chk_multiple"))
        self.chk_multiple.setToolTip(tooltip_tr("set_ops.chk_multiple"))
        file_layout.addWidget(self.chk_multiple, 2, 0, 1, 3)

        # File list (hidden by default)
        self.list_files = QListWidget()
        self.list_files.setMaximumHeight(100)
        self.list_files.setVisible(False)
        file_layout.addWidget(self.list_files, 3, 0, 1, 3)

        # Buttons for file list
        file_btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton(tr("file_selection.btn_add_file"))
        self.btn_add_file.setToolTip(tooltip_tr("set_ops.btn_add_file"))
        self.btn_add_file.setVisible(False)
        self.btn_remove_file = QPushButton(tr("file_selection.btn_remove_file"))
        self.btn_remove_file.setToolTip(tooltip_tr("set_ops.btn_remove_file"))
        self.btn_remove_file.setVisible(False)
        self.btn_clear_files = QPushButton(tr("file_selection.btn_clear_files"))
        self.btn_clear_files.setToolTip(tooltip_tr("set_ops.btn_clear_files"))
        self.btn_clear_files.setVisible(False)
        file_btn_layout.addWidget(self.btn_add_file)
        file_btn_layout.addWidget(self.btn_remove_file)
        file_btn_layout.addWidget(self.btn_clear_files)
        file_btn_layout.addStretch()
        file_layout.addLayout(file_btn_layout, 4, 0, 1, 3)

        file_group.setLayout(file_layout)

        # Main layout
        main_layout = QGridLayout(self)
        main_layout.addWidget(file_group, 0, 0)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.btn_browse_a.clicked.connect(lambda: self._browse_file("a"))
        self.btn_browse_b.clicked.connect(lambda: self._browse_file("b"))
        self.chk_multiple.toggled.connect(self._toggle_multiple_files)
        self.btn_add_file.clicked.connect(self._add_file)
        self.btn_remove_file.clicked.connect(self._remove_file)
        self.btn_clear_files.clicked.connect(self._clear_files)

        # Emit signal when files change
        self.ed_file_a.textChanged.connect(self._on_files_changed)
        self.ed_file_b.textChanged.connect(self._on_files_changed)
        self.list_files.model().rowsInserted.connect(self._on_files_changed)
        self.list_files.model().rowsRemoved.connect(self._on_files_changed)

    def _apply_accessibility(self) -> None:
        """Apply accessibility labels."""
        AccessibilityManager.set_accessible_widget(
            self.ed_file_a, "File Selection - Input - File A",
            "First file for processing"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_browse_a, "File Selection - Button - Browse File A",
            "Browse and select first file"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_file_b, "File Selection - Input - File B",
            "Second file for processing"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_browse_b, "File Selection - Button - Browse File B",
            "Browse and select second file"
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_multiple, "File Selection - Checkbox - Multiple Files",
            "Enable pipeline processing with multiple files (left-to-right)"
        )

    def _browse_file(self, target: str) -> None:
        """
        Browse for file.

        Args:
            target: Target field ('a' or 'b')
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select File {target.upper()}", "", self.file_filter
        )

        if file_path:
            if target == "a":
                self.ed_file_a.setText(file_path)
            else:
                self.ed_file_b.setText(file_path)

    def _toggle_multiple_files(self, checked: bool) -> None:
        """Toggle multiple files mode."""
        self.list_files.setVisible(checked)
        self.btn_add_file.setVisible(checked)
        self.btn_remove_file.setVisible(checked)
        self.btn_clear_files.setVisible(checked)

        if checked:
            # Populate list with File A and B if they exist
            self.list_files.clear()
            if self.ed_file_a.text():
                self.list_files.addItem(self.ed_file_a.text())
            if self.ed_file_b.text():
                self.list_files.addItem(self.ed_file_b.text())
            self._on_files_changed()

    def _add_file(self) -> None:
        """Add file to multi-file list via file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add File", "", self.file_filter
        )

        if file_path:
            self.list_files.addItem(file_path)

    def _remove_file(self) -> None:
        """Remove selected file from multi-file list."""
        current_row = self.list_files.currentRow()
        if current_row >= 0:
            self.list_files.takeItem(current_row)

    def _clear_files(self) -> None:
        """Clear file list."""
        self.list_files.clear()

    def _on_files_changed(self) -> None:
        """Emit files_changed signal when file list changes."""
        files = self.get_files()
        self.files_changed.emit(files)

    # Public API

    def get_files(self) -> List[str]:
        """
        Get list of files to process.

        Returns:
            List of file paths from either 2-file mode (File A/B) or multi-file list.
        """
        if self.chk_multiple.isChecked():
            files = []
            for i in range(self.list_files.count()):
                files.append(self.list_files.item(i).text())
            return files
        else:
            files = []
            if self.ed_file_a.text():
                files.append(self.ed_file_a.text())
            if self.ed_file_b.text():
                files.append(self.ed_file_b.text())
            return files

    def set_files(self, files: List[str]) -> None:
        """
        Set file list programmatically.

        Args:
            files: List of file paths
        """
        if len(files) == 2:
            # Two-file mode
            self.chk_multiple.setChecked(False)
            self.ed_file_a.setText(files[0])
            self.ed_file_b.setText(files[1])
        elif len(files) > 2:
            # Multiple files mode
            self.chk_multiple.setChecked(True)
            self.list_files.clear()
            for file_path in files:
                self.list_files.addItem(file_path)
        elif len(files) == 1:
            # Single file
            self.chk_multiple.setChecked(False)
            self.ed_file_a.setText(files[0])
            self.ed_file_b.clear()

    def clear(self) -> None:
        """Clear all file selections."""
        self.ed_file_a.clear()
        self.ed_file_b.clear()
        self.list_files.clear()
        self.chk_multiple.setChecked(False)

    def is_multiple_mode(self) -> bool:
        """Check if multiple files mode is enabled."""
        return self.chk_multiple.isChecked()


__all__ = ['FileSelectionWidget']
