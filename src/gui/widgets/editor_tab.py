#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Editor Tab Widget - Single file editor tab

Extracted from editor_dock.py (v2.9.114 - Phase 2.5.2)
Provides a complete text editor tab with file I/O and syntax highlighting.

Features:
- Text editing with syntax highlighting
- File loading and saving
- Modified state tracking
- Edit-only mode (sandbox editing without file backing)
- Auto-save functionality
- Toolbar (copy, export, enable saving)
- Visual indicators for modes

Pattern: State (GoF) - edit_only_mode changes behavior
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # File I/O robustness

from __future__ import annotations
from typing import Optional
import os

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog,
    QMessageBox, QToolBar, QApplication
)
from PySide6.QtGui import QFont

from src.i18n.translator import tr, tooltip_tr
from .syntax_highlighter import SyntaxHighlighter


class EditorTab(QWidget):
    """
    Single editor tab for editing a file.

    Contains:
    - Text editor with syntax highlighting
    - File path tracking
    - Modified state tracking
    - Edit-only mode (sandbox editing without file backing)

    Pattern: State (GoF) - edit_only_mode changes save behavior
    """

    modified_changed = Signal(bool)  # Emitted when modified state changes
    edit_only_changed = Signal(bool)  # Emitted when edit-only mode changes
    auto_saved = Signal()  # Emitted when file is auto-saved

    def __init__(self, file_path: Optional[str] = None, parent=None, edit_only_mode: bool = False):
        """
        Initialize editor tab.

        Args:
            file_path: Optional path to file to load
            parent: Parent widget
            edit_only_mode: If True, editor is not backed by a file
        """
        super().__init__(parent)
        self.file_path = file_path
        self.is_modified = False
        self.edit_only_mode = edit_only_mode
        self.auto_save_enabled = False

        # Auto-save timer (3 seconds after last modification)
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.setInterval(3000)  # 3 seconds
        self.auto_save_timer.timeout.connect(self._auto_save)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar for edit-only features
        self._setup_toolbar()

        # Text editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setTabStopDistance(40)  # 4 spaces equivalent
        self.editor.textChanged.connect(self._on_text_changed)

        # Monospace font
        font = QFont("Courier New", 10)
        self.editor.setFont(font)

        layout.addWidget(self.editor)

        # Apply visual indicators if edit-only
        self._update_visual_indicators()

        # Syntax highlighter
        self.highlighter = None
        if file_path:
            self._setup_highlighter()

        # Apply tooltips
        self._apply_tab_tooltips()

    def _apply_tab_tooltips(self):
        """Apply internationalized tooltips to EditorTab widgets."""
        self.editor.setToolTip(tooltip_tr("editor.editor"))
        self.btn_copy.setToolTip(tooltip_tr("editor.btn_copy"))
        self.btn_export.setToolTip(tooltip_tr("editor.btn_export"))
        self.btn_enable_saving.setToolTip(tooltip_tr("editor.btn_enable_saving"))

    def _setup_toolbar(self):
        """Setup toolbar with edit-only mode buttons."""
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border: none; padding: 2px; }")

        # Copy to Clipboard button
        self.btn_copy = QPushButton(tr("editor_tab.btn_copy"))
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        toolbar.addWidget(self.btn_copy)

        # Export to File button
        self.btn_export = QPushButton(tr("editor_tab.btn_export"))
        self.btn_export.clicked.connect(self._export_to_file)
        toolbar.addWidget(self.btn_export)

        # Enable File Saving button (only visible in edit-only mode)
        self.btn_enable_saving = QPushButton(tr("editor_tab.btn_enable_saving"))
        self.btn_enable_saving.clicked.connect(self._enable_file_saving)
        toolbar.addWidget(self.btn_enable_saving)

        self.layout().addWidget(toolbar)
        self.toolbar = toolbar

        # Update button visibility
        self._update_toolbar_visibility()

    def _update_toolbar_visibility(self):
        """Update toolbar button visibility based on mode."""
        # Enable Saving button only visible in edit-only mode
        self.btn_enable_saving.setVisible(self.edit_only_mode)

        # Copy/Export always visible but more prominent in edit-only
        if self.edit_only_mode:
            self.btn_copy.setStyleSheet("font-weight: bold;")
            self.btn_export.setStyleSheet("font-weight: bold;")
        else:
            self.btn_copy.setStyleSheet("")
            self.btn_export.setStyleSheet("")

    def _copy_to_clipboard(self):
        """Copy editor content to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editor.toPlainText())
        # Visual feedback
        self.btn_copy.setText(tr("editor_tab.btn_copied"))
        QTimer.singleShot(1500, lambda: self.btn_copy.setText(tr("editor_tab.btn_copy")))

    def _export_to_file(self):
        """Export content to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("editor_tab.export_dialog_title"),
            "",
            tr("editor_tab.export_dialog_filter")
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())

            # Visual feedback
            self.btn_export.setText(tr("editor_tab.btn_exported"))
            QTimer.singleShot(1500, lambda: self.btn_export.setText(tr("editor_tab.btn_export")))
        except Exception as e:
            QMessageBox.critical(
                self,
                tr("editor_tab.export_error_title"),
                tr("editor_tab.export_error_message").format(e)
            )

    def _enable_file_saving(self):
        """Convert edit-only tab to normal file-backed editor."""
        reply = QMessageBox.question(
            self,
            tr("editor_tab.enable_saving_title"),
            tr("editor_tab.enable_saving_message"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Trigger Save As to get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                tr("editor_tab.save_as_dialog_title"),
                "",
                tr("editor_tab.export_dialog_filter")
            )

            if file_path:
                # Save content
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.editor.toPlainText())

                    # Update state
                    self.edit_only_mode = False
                    self.file_path = file_path
                    self.is_modified = False
                    self._setup_highlighter()
                    self._update_visual_indicators()
                    self._update_toolbar_visibility()
                    self.edit_only_changed.emit(False)
                    self.modified_changed.emit(False)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        tr("editor_tab.save_error_title"),
                        tr("editor_tab.save_error_message").format(e)
                    )

    def _update_visual_indicators(self):
        """Update visual indicators for edit-only mode."""
        if self.edit_only_mode:
            # Golden border indicator
            self.editor.setStyleSheet("""
                QTextEdit {
                    border: 3px solid #FFD700;
                    background-color: #FFF8DC;
                }
            """)
        else:
            # Normal border
            self.editor.setStyleSheet("")

    def toggle_edit_only_mode(self):
        """Toggle edit-only mode on/off."""
        if not self.edit_only_mode and self.file_path:
            # Cannot enable edit-only if file is already backed
            reply = QMessageBox.question(
                self,
                tr("editor_tab.edit_only_title"),
                tr("editor_tab.edit_only_message"),
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        self.edit_only_mode = not self.edit_only_mode
        self._update_visual_indicators()
        self._update_toolbar_visibility()
        self.edit_only_changed.emit(self.edit_only_mode)

    def _setup_highlighter(self):
        """Setup syntax highlighter based on file extension."""
        if not self.file_path:
            return

        ext = os.path.splitext(self.file_path)[1].lstrip('.')
        self.highlighter = SyntaxHighlighter(self.editor.document(), ext)

    def _on_text_changed(self):
        """Handle text changes."""
        if not self.is_modified:
            self.is_modified = True
            self.modified_changed.emit(True)

        # Reset auto-save timer if enabled
        if self.auto_save_enabled and self.file_path and not self.edit_only_mode:
            self.auto_save_timer.start()  # Restart 3s countdown

    def load_file(self, file_path: str) -> bool:
        """
        Load file content into editor.

        Args:
            file_path: Path to file to load

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.file_path = file_path
            self.editor.blockSignals(True)  # Prevent modified signal
            self.editor.setPlainText(content)
            self.editor.blockSignals(False)
            self.is_modified = False
            self.modified_changed.emit(False)

            # Setup highlighter
            self._setup_highlighter()

            return True
        except Exception:
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """
        Save editor content to file.

        Args:
            file_path: Optional path to save to (defaults to current file)

        Returns:
            True if successful, False otherwise
        """
        save_path = file_path or self.file_path
        if not save_path:
            return False

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())

            self.file_path = save_path
            self.is_modified = False
            self.modified_changed.emit(False)

            # Setup highlighter if new file
            if file_path:
                self._setup_highlighter()

            return True
        except Exception:
            return False

    def get_tab_title(self) -> str:
        """Get title for tab (filename or 'Untitled')."""
        if self.file_path:
            return os.path.basename(self.file_path)
        return "Untitled"

    def get_display_title(self) -> str:
        """Get display title with modified and edit-only indicators."""
        title = self.get_tab_title()

        # Edit-only indicator
        if self.edit_only_mode:
            title = "🔒 " + title

        # Modified indicator
        if self.is_modified:
            title += " *"

        return title

    def get_status_text(self) -> str:
        """Get status bar text with mode indicator."""
        status = "Text Editor"
        if self.edit_only_mode:
            status = "Edit-Only Mode"
        return status

    def set_auto_save(self, enabled: bool):
        """Enable or disable auto-save for this tab."""
        self.auto_save_enabled = enabled

        # Stop timer if disabling
        if not enabled:
            self.auto_save_timer.stop()
        # Start timer if enabling and file is modified
        elif self.file_path and not self.edit_only_mode and self.is_modified:
            self.auto_save_timer.start()

    def _auto_save(self):
        """Auto-save file if conditions are met."""
        # Only auto-save if:
        # 1. Auto-save is enabled
        # 2. File has a path (not untitled)
        # 3. Not in edit-only mode
        # 4. File is modified
        if not self.auto_save_enabled:
            return

        if not self.file_path:
            return

        if self.edit_only_mode:
            return

        if not self.is_modified:
            return

        # Perform save
        success = self.save_file()

        if success:
            self.auto_saved.emit()  # Signal for status update


__all__ = ['EditorTab']
