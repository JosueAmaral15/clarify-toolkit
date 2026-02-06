#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File List Table Manager - Table display and interaction

Extracted from file_list_dock.py (v2.9.114 - Phase 2.4.4)
Handles table setup, population, sorting, context menu, and export.

Features:
- Table configuration and styling
- Populate table with FileInfo objects
- Quick filter on visible rows
- Context menu (open in file manager)
- Multi-selection support
- Export to CSV
- Statistics display
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=line-too-long  # Long UI strings
# pylint: disable=import-outside-toplevel  # Circular import avoidance
# pylint: disable=broad-exception-caught  # UI error handling
# pylint: disable=protected-access  # MainWindow internal access
# pylint: disable=logging-fstring-interpolation  # Not performance-critical

from __future__ import annotations

import os
import csv
import platform
import subprocess
from typing import List
from datetime import datetime
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QHeaderView,
    QMenu, QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction

from src.i18n.translator import tr
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileListTableManager(QWidget):
    """Manager for file list table display."""

    # Signals
    files_exported = Signal(str)  # Emitted when CSV export completes with filepath

    # Column indices
    COL_NAME = 0
    COL_SIZE = 1
    COL_MODIFIED = 2
    COL_PERMISSIONS = 3
    COL_PATH = 4

    def __init__(self, parent=None, main_window=None):
        """
        Initialize table manager.

        Args:
            parent: Parent widget
            main_window: Optional explicit reference to main window (v2.9.121 bugfix)
        """
        super().__init__(parent)
        self._main_window_ref = main_window  # Store explicit main window reference
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Quick filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(tr("table_manager.quick_filter")))

        self.ed_quick_filter = QLineEdit()
        self.ed_quick_filter.setPlaceholderText(tr("table_manager.placeholder_filter"))
        self.ed_quick_filter.textChanged.connect(self._apply_quick_filter)
        filter_layout.addWidget(self.ed_quick_filter, stretch=1)

        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            tr("table_manager.header_name"),
            tr("table_manager.header_size"),
            tr("table_manager.header_modified"),
            tr("table_manager.header_permissions"),
            tr("table_manager.header_path")
        ])

        # Configure columns
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_PATH, QHeaderView.ResizeMode.Stretch)

        # Prevent horizontal expansion from long paths (v2.9.117)
        self.table.setWordWrap(False)
        self.table.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Configure behavior
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.setSortingEnabled(True)

        # Connect context menu
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

        # Bottom toolbar
        toolbar_layout = QHBoxLayout()

        self.lbl_stats = QLabel(tr("table_manager.no_files_listed"))
        toolbar_layout.addWidget(self.lbl_stats, stretch=1)

        self.btn_export = QPushButton(tr("table_manager.btn_export_csv"))
        self.btn_export.clicked.connect(self.export_csv)
        toolbar_layout.addWidget(self.btn_export)

        layout.addLayout(toolbar_layout)

    def populate(self, files: List[dict], human_readable: bool = True):
        """
        Populate table with file information.

        Args:
            files: List of dicts with keys: name, size, mtime, permissions, path, is_dir
            human_readable: Whether to show sizes in human-readable format
        """
        self.clear()
        self.table.setSortingEnabled(False)

        total_size = 0
        file_count = 0
        dir_count = 0

        for file_info in files:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Name
            name = file_info.get('name', '')
            name_item = QTableWidgetItem(name)
            name_item.setToolTip(name)  # Show full name if truncated
            self.table.setItem(row, self.COL_NAME, name_item)

            # Size
            size = file_info.get('size', 0)
            is_dir = file_info.get('is_dir', False)

            if is_dir:
                size_str = "-"
                dir_count += 1
            else:
                if human_readable:
                    size_str = self._format_size_human(size)
                else:
                    size_str = str(size)
                total_size += size
                file_count += 1

            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # Tooltip: Just show the size value (user requirement: value only, no label)
            if is_dir:
                size_item.setToolTip("-")
            else:
                # Show human-readable + raw bytes
                size_item.setToolTip(f"{size_str} ({size:,} bytes)")
            self.table.setItem(row, self.COL_SIZE, size_item)

            # Modified time - convert Unix timestamp to readable format
            mtime = file_info.get('mtime')
            if mtime:
                if isinstance(mtime, (int, float)):
                    # Convert Unix timestamp to datetime
                    mtime_dt = datetime.fromtimestamp(mtime)
                    # Display format: YYYY-MM-DD HH:MM:SS (intelligible for users)
                    mtime_str = mtime_dt.strftime("%Y-%m-%d %H:%M:%S")
                    # Tooltip: Show full datetime with day of week for context
                    mtime_tooltip = mtime_dt.strftime("%A, %B %d, %Y at %I:%M:%S %p")
                elif isinstance(mtime, datetime):
                    # Already a datetime object
                    mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                    mtime_tooltip = mtime.strftime("%A, %B %d, %Y at %I:%M:%S %p")
                else:
                    # Fallback for other formats
                    mtime_str = str(mtime)
                    mtime_tooltip = mtime_str
            else:
                mtime_str = "-"
                mtime_tooltip = "No modification time available"

            mtime_item = QTableWidgetItem(mtime_str)
            mtime_item.setToolTip(mtime_tooltip)
            self.table.setItem(row, self.COL_MODIFIED, mtime_item)

            # Permissions
            perms = file_info.get('permissions', '')
            perms_item = QTableWidgetItem(perms)
            perms_item.setToolTip(perms)  # Show full permissions string
            self.table.setItem(row, self.COL_PERMISSIONS, perms_item)

            # Path
            path = file_info.get('path', '')
            path_item = QTableWidgetItem(path)
            path_item.setToolTip(path)  # Show full path (can be very long)
            self.table.setItem(row, self.COL_PATH, path_item)

        self.table.setSortingEnabled(True)

        # Update stats
        total_count = file_count + dir_count
        if human_readable:
            total_str = self._format_size_human(total_size)
        else:
            total_str = f"{total_size} bytes"

        self.lbl_stats.setText(
            f"Listed {total_count} items ({file_count} files, {dir_count} dirs) | Total size: {total_str}"
        )

    def clear(self):
        """Clear table contents."""
        self.table.setRowCount(0)
        self.lbl_stats.setText(tr("table_manager.no_files_listed"))
        self.ed_quick_filter.clear()

    def _apply_quick_filter(self, text: str):
        """Apply quick filter to visible rows."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, self.COL_NAME)
            if name_item:
                name = name_item.text().lower()
                self.table.setRowHidden(row, text not in name)

    def _show_context_menu(self, position):
        """Show context menu at position."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            return

        menu = QMenu(self)

        # Open in file manager action
        if len(selected_rows) == 1:
            action_text = tr("table_manager.action_open_file_manager")
        else:
            action_text = tr("table_manager.action_open_locations").format(len(selected_rows))

        action_open = QAction(action_text, self)
        action_open.triggered.connect(self._open_in_file_manager)
        menu.addAction(action_open)

        # Copy path action
        action_copy = QAction(tr("table_manager.action_copy_path"), self)
        action_copy.triggered.connect(self._copy_path)
        menu.addAction(action_copy)

        # Open in editor action
        action_editor = QAction("📝 " + tr("table_manager.action_open_editor"), self)
        action_editor.triggered.connect(self._open_in_editor)
        menu.addAction(action_editor)

        # Open and switch to editor action (v2.9.121 - new feature)
        action_editor_switch = QAction("🎯 " + tr("table_manager.action_open_and_switch"), self)
        action_editor_switch.triggered.connect(self._open_in_editor_and_switch)
        menu.addAction(action_editor_switch)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _open_in_editor(self):
        """Open selected file(s) in Clarify editor."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        # Get main window reference
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(
                self,
                tr("table_manager.error_title"),
                tr("table_manager.error_no_main_window")
            )
            return

        # Ensure dock_editor exists
        if not hasattr(main_window, 'dock_editor') or main_window.dock_editor is None:
            from src.gui.dock_factory import DockFactory
            DockFactory.create_editor_dock(main_window)

        for row in selected_rows:
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                filepath = path_item.text()
                # Only open files, not directories
                if os.path.isfile(filepath):
                    try:
                        main_window.dock_editor.open_file_path(filepath)
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            tr("table_manager.error_title"),
                            tr("table_manager.error_open_editor").format(filepath, e)
                        )
                        break

    def _open_in_editor_and_switch(self):
        """Open selected file(s) in Clarify editor and switch focus to editor (v2.9.121)."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        # Get main window reference
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(
                self,
                tr("table_manager.error_title"),
                tr("table_manager.error_no_main_window")
            )
            return

        # Ensure dock_editor exists
        if not hasattr(main_window, 'dock_editor') or main_window.dock_editor is None:
            from src.gui.dock_factory import DockFactory
            DockFactory.create_editor_dock(main_window)

        # Open all selected files
        last_opened_filepath = None
        for row in selected_rows:
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                filepath = path_item.text()
                # Only open files, not directories
                if os.path.isfile(filepath):
                    try:
                        main_window.dock_editor.open_file_path(filepath)
                        last_opened_filepath = filepath  # Track last opened
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            tr("table_manager.error_title"),
                            tr("table_manager.error_open_editor").format(filepath, e)
                        )
                        break

        # Switch to Editor tab in main window (create if doesn't exist)
        if last_opened_filepath:
            # Use _show_editor() which properly handles tab creation/switching
            if hasattr(main_window, '_show_editor'):
                main_window._show_editor()

            # Focus on the last opened file's tab in editor
            # Editor dock has tab_widget for multiple files
            if hasattr(main_window.dock_editor, 'tab_widget'):
                editor_tabs = main_window.dock_editor.tab_widget
                # Find tab with matching filepath
                for i in range(editor_tabs.count()):
                    tab = editor_tabs.widget(i)
                    if hasattr(tab, 'file_path') and tab.file_path == last_opened_filepath:
                        editor_tabs.setCurrentIndex(i)
                        break

    def _get_main_window(self):
        """Get reference to main window."""
        # Try explicit reference first (v2.9.121 bugfix)
        if self._main_window_ref is not None:
            logger.debug(f"Using explicit main_window reference: {type(self._main_window_ref).__name__}")
            return self._main_window_ref

        # Fallback to parent chain traversal
        widget = self
        logger.debug(f"Starting search for main_window from {type(self).__name__}")
        max_iterations = 20  # Safety limit to prevent infinite loops
        iteration = 0

        while widget is not None and iteration < max_iterations:
            logger.debug(f"Checking widget: {type(widget).__name__}, has dock_editor: {hasattr(widget, 'dock_editor')}")
            if hasattr(widget, 'dock_editor'):
                logger.debug(f"Found main_window: {type(widget).__name__}")
                return widget
            widget = widget.parent()
            iteration += 1

        logger.debug(f"Could NOT find main_window - reached None after {iteration} iterations")
        return None

    def _open_in_file_manager(self):
        """Open selected file(s) location in file manager."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))

        for row in selected_rows:
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                filepath = path_item.text()
                directory = os.path.dirname(filepath) if os.path.isfile(filepath) else filepath

                # Open file manager based on OS
                system = platform.system()
                try:
                    if system == "Windows":
                        # pylint: disable=no-member  # os.startfile is Windows-only
                        os.startfile(directory)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", directory], check=False)
                    else:  # Linux
                        subprocess.run(["xdg-open", directory], check=False)
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        tr("table_manager.error_title"),
                        tr("table_manager.error_file_manager").format(e)
                    )
                    break

    def _copy_path(self):
        """Copy selected path(s) to clipboard."""
        from PySide6.QtWidgets import QApplication

        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            return

        paths = []
        for row in selected_rows:
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                paths.append(path_item.text())

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(paths))

        QMessageBox.information(
            self,
            tr("table_manager.copied_title"),
            tr("table_manager.copied_message").format(len(paths))
        )

    def export_csv(self):
        """Export table to CSV file."""
        if not self.table.rowCount():
            QMessageBox.information(
                self,
                tr("table_manager.no_data_title"),
                tr("table_manager.no_data_message")
            )
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            tr("table_manager.export_dialog_title"),
            "file_list.csv",
            tr("table_manager.export_dialog_filter")
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(["Name", "Size", "Modified", "Permissions", "Path"])

                # Data
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(5):
                        item = self.table.item(row, col)
                        text = item.text() if item else ""
                        row_data.append(text)
                    writer.writerow(row_data)

            self.files_exported.emit(filepath)
            QMessageBox.information(
                self,
                tr("file_list_table.export_complete_title"),
                tr("file_list_table.export_complete").format(filepath=filepath)
            )
        except Exception as e:
            QMessageBox.critical(self, tr("file_list_table.export_failed_title"), tr("file_list_table.export_failed").format(error=e))

    def get_selected_paths(self) -> List[str]:
        """Get list of selected file paths."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))
        paths = []
        for row in selected_rows:
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                paths.append(path_item.text())
        return paths

    def get_all_paths(self) -> List[str]:
        """Get list of all file paths in table."""
        paths = []
        for row in range(self.table.rowCount()):
            path_item = self.table.item(row, self.COL_PATH)
            if path_item:
                paths.append(path_item.text())
        return paths

    def get_row_count(self) -> int:
        """Get number of rows in table."""
        return self.table.rowCount()

    @staticmethod
    def _format_size_human(size: int) -> str:
        """Convert size to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


__all__ = ['FileListTableManager']
