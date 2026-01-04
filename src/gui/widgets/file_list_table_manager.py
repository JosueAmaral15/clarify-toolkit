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

from __future__ import annotations

import os
import csv
import platform
import subprocess
from typing import List, Callable, Optional
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QHeaderView,
    QMenu, QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction

from src.i18n.translator import tr


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
    
    def __init__(self, parent=None):
        """Initialize table manager."""
        super().__init__(parent)
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
            name_item.setToolTip(f"{tr('table_manager.tooltip_name')}: {name}")
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
            size_item.setToolTip(f"{tr('table_manager.tooltip_size')}: {size_str} ({size} bytes)" if not is_dir else tr('table_manager.tooltip_size_dir'))
            self.table.setItem(row, self.COL_SIZE, size_item)
            
            # Modified time
            mtime = file_info.get('mtime')
            if isinstance(mtime, datetime):
                mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            else:
                mtime_str = str(mtime) if mtime else "-"
            mtime_item = QTableWidgetItem(mtime_str)
            mtime_item.setToolTip(f"{tr('table_manager.tooltip_modified')}: {mtime_str}")
            self.table.setItem(row, self.COL_MODIFIED, mtime_item)
            
            # Permissions
            perms = file_info.get('permissions', '')
            perms_item = QTableWidgetItem(perms)
            perms_item.setToolTip(f"{tr('table_manager.tooltip_permissions')}: {perms}")
            self.table.setItem(row, self.COL_PERMISSIONS, perms_item)
            
            # Path
            path = file_info.get('path', '')
            path_item = QTableWidgetItem(path)
            path_item.setToolTip(f"{tr('table_manager.tooltip_path')}: {path}")
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
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
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
                        os.startfile(directory)
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", directory])
                    else:  # Linux
                        subprocess.run(["xdg-open", directory])
                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        tr("table_manager.error_title"), 
                        tr("table_manager.error_file_manager").format(e)
                    )
                    break
    
    def _copy_path(self):
        """Copy selected path(s) to clipboard."""
        from PySide6.QtGui import QClipboard
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
        if self.table.rowCount() == 0:
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
