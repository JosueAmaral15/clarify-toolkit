"""
Advanced File Finder (Task #36 - v2.9.11)

Module for advanced file and directory search with conditions.
Provides GUI dialog with filters: filename regex, size range, date range, type filter.
"""

import os
import re
from datetime import datetime
from typing import List, Tuple, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDateTimeEdit, QCheckBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDateTime

from ..i18n.translator import tr


class AdvancedFileSearchDialog(QDialog):
    """Dialog for advanced file/directory search with conditions."""
    
    def __init__(self, parent=None, initial_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Advanced File Search")
        self.setModal(True)
        self.resize(800, 600)
        
        self.initial_dir = initial_dir or os.getcwd()
        self.results: List[Tuple[str, os.stat_result]] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Search directory
        dir_group = QGroupBox(tr("file_finder.group_search_directory"))
        dir_layout = QHBoxLayout()
        self.ed_directory = QLineEdit(self.initial_dir)
        self.ed_directory.setPlaceholderText(tr("file_finder.placeholder_directory"))
        btn_browse = QPushButton(tr("file_finder.btn_browse"))
        btn_browse.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.ed_directory)
        dir_layout.addWidget(btn_browse)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Filters group
        filter_group = QGroupBox(tr("file_finder.group_search_filters"))
        filter_layout = QVBoxLayout()
        
        # Filename pattern (regex)
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel(tr("file_finder.lbl_pattern")))
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText(tr("file_finder.placeholder_pattern"))
        self.chk_case_sensitive = QCheckBox(tr("file_finder.chk_case_sensitive"))
        pattern_layout.addWidget(self.ed_pattern)
        pattern_layout.addWidget(self.chk_case_sensitive)
        filter_layout.addLayout(pattern_layout)
        
        # File type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(tr("file_finder.lbl_type")))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Any", "Files only", "Directories only"])
        type_layout.addWidget(self.combo_type)
        type_layout.addStretch()
        filter_layout.addLayout(type_layout)
        
        # Size range (MB)
        size_layout = QHBoxLayout()
        self.chk_size_filter = QCheckBox(tr("file_finder.chk_size_filter"))
        self.spin_size_min = QSpinBox()
        self.spin_size_min.setRange(0, 100000)
        self.spin_size_min.setValue(0)
        self.spin_size_max = QSpinBox()
        self.spin_size_max.setRange(0, 100000)
        self.spin_size_max.setValue(1000)
        size_layout.addWidget(self.chk_size_filter)
        size_layout.addWidget(QLabel(tr("file_finder.lbl_size_min")))
        size_layout.addWidget(self.spin_size_min)
        size_layout.addWidget(QLabel(tr("file_finder.lbl_size_max")))
        size_layout.addWidget(self.spin_size_max)
        size_layout.addStretch()
        filter_layout.addLayout(size_layout)
        
        # Date range
        date_layout = QHBoxLayout()
        self.chk_date_filter = QCheckBox(tr("file_finder.chk_date_filter"))
        self.date_from = QDateTimeEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-30))
        self.date_to = QDateTimeEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDateTime(QDateTime.currentDateTime())
        date_layout.addWidget(self.chk_date_filter)
        date_layout.addWidget(QLabel(tr("file_finder.lbl_date_from")))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel(tr("file_finder.lbl_date_to")))
        date_layout.addWidget(self.date_to)
        date_layout.addStretch()
        filter_layout.addLayout(date_layout)
        
        # Recursive search
        self.chk_recursive = QCheckBox(tr("file_finder.chk_recursive"))
        self.chk_recursive.setChecked(True)
        filter_layout.addWidget(self.chk_recursive)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Search button
        btn_search = QPushButton(tr("file_finder.btn_search"))
        btn_search.clicked.connect(self._perform_search)
        layout.addWidget(btn_search)
        
        # Results table
        results_group = QGroupBox(tr("file_finder.group_results"))
        results_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            tr("file_finder.header_name"),
            tr("file_finder.header_path"),
            tr("file_finder.header_size"),
            tr("file_finder.header_modified")
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        # Task #41 - v2.9.13: Enable tooltips for preview
        self.table.setMouseTracking(True)
        self.table.itemEntered.connect(self._show_file_preview)
        results_layout.addWidget(self.table)
        
        # Results stats
        self.lbl_stats = QLabel(tr("file_finder.lbl_no_results"))
        results_layout.addWidget(self.lbl_stats)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_export = QPushButton(tr("file_finder.btn_export"))
        btn_export.clicked.connect(self._export_results)
        btn_close = QPushButton(tr("file_finder.btn_close"))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_export)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
    
    def _browse_directory(self):
        """Browse for search directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Search",
            self.ed_directory.text() or self.initial_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.ed_directory.setText(directory)
    
    def _perform_search(self):
        """Execute search with current filters."""
        directory = self.ed_directory.text().strip()
        
        if not directory:
            QMessageBox.warning(self, tr("file_finder.msg_missing_title"), tr("file_finder.msg_missing_directory"))
            return
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, tr("file_finder.msg_invalid_title"), tr("file_finder.msg_invalid_directory").format(directory=directory))
            return
        
        # Build search criteria
        pattern = self.ed_pattern.text().strip()
        if pattern:
            try:
                flags = 0 if self.chk_case_sensitive.isChecked() else re.IGNORECASE
                regex = re.compile(pattern, flags)
            except re.error as e:
                QMessageBox.warning(self, tr("file_finder.msg_invalid_regex_title"), tr("file_finder.msg_invalid_regex").format(error=e))
                return
        else:
            regex = None
        
        type_filter = self.combo_type.currentText()
        recursive = self.chk_recursive.isChecked()
        
        # Size filter (convert MB to bytes)
        if self.chk_size_filter.isChecked():
            size_min = self.spin_size_min.value() * 1024 * 1024
            size_max = self.spin_size_max.value() * 1024 * 1024
        else:
            size_min = size_max = None
        
        # Date filter
        if self.chk_date_filter.isChecked():
            date_min = self.date_from.dateTime().toPyDateTime().timestamp()
            date_max = self.date_to.dateTime().toPyDateTime().timestamp()
        else:
            date_min = date_max = None
        
        # Perform search
        self.results = []
        self._search_directory(
            directory, regex, type_filter, recursive,
            size_min, size_max, date_min, date_max
        )
        
        # Display results
        self._display_results()
    
    def _search_directory(
        self,
        directory: str,
        regex: Optional[re.Pattern],
        type_filter: str,
        recursive: bool,
        size_min: Optional[int],
        size_max: Optional[int],
        date_min: Optional[float],
        date_max: Optional[float]
    ):
        """Recursively search directory with filters."""
        try:
            entries = os.listdir(directory)
        except PermissionError:
            return
        
        for entry in entries:
            path = os.path.join(directory, entry)
            
            # Skip if can't stat
            try:
                stat = os.stat(path)
            except (PermissionError, FileNotFoundError):
                continue
            
            is_dir = os.path.isdir(path)
            is_file = os.path.isfile(path)
            
            # Apply type filter
            if type_filter == "Files only" and not is_file:
                continue
            if type_filter == "Directories only" and not is_dir:
                continue
            
            # Apply filename pattern
            if regex and not regex.search(entry):
                continue
            
            # Apply size filter (files only)
            if is_file and size_min is not None and size_max is not None:
                if not (size_min <= stat.st_size <= size_max):
                    continue
            
            # Apply date filter
            if date_min is not None and date_max is not None:
                if not (date_min <= stat.st_mtime <= date_max):
                    continue
            
            # Match - add to results
            self.results.append((path, stat))
            
            # Recurse into subdirectories
            if recursive and is_dir:
                self._search_directory(
                    path, regex, type_filter, True,
                    size_min, size_max, date_min, date_max
                )
    
    def _display_results(self):
        """Display search results in table."""
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        
        for path, stat in self.results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Name
            name = os.path.basename(path)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Path
            self.table.setItem(row, 1, QTableWidgetItem(path))
            
            # Size (MB)
            size_mb = stat.st_size / (1024 * 1024)
            size_item = QTableWidgetItem(f"{size_mb:.2f}")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, size_item)
            
            # Modified date
            mtime = datetime.fromtimestamp(stat.st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 3, QTableWidgetItem(mtime_str))
        
        self.table.setSortingEnabled(True)
        
        # Update stats
        total_size = sum(stat.st_size for _, stat in self.results)
        total_size_mb = total_size / (1024 * 1024)
        self.lbl_stats.setText(
            f"Found {len(self.results)} items | Total size: {total_size_mb:.2f} MB"
        )
    
    def _export_results(self):
        """Export results to CSV file."""
        if not self.results:
            QMessageBox.information(self, tr("file_finder.msg_no_results_title"), tr("file_finder.msg_no_results_export"))
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "search_results.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write("Name,Path,Size (bytes),Size (MB),Modified\n")
                
                # Data
                for path, stat in self.results:
                    name = os.path.basename(path)
                    size_mb = stat.st_size / (1024 * 1024)
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Escape commas in path/name
                    name = name.replace('"', '""')
                    path = path.replace('"', '""')
                    
                    f.write(f'"{name}","{path}",{stat.st_size},{size_mb:.2f},{mtime_str}\n')
            
            QMessageBox.information(
                self,
                tr("file_finder.msg_export_complete_title"),
                tr("file_finder.msg_export_complete").format(filepath=filepath)
            )
        except Exception as e:
            QMessageBox.critical(self, tr("file_finder.msg_export_failed_title"), tr("file_finder.msg_export_failed").format(error=e))
    
    def _show_file_preview(self, item: QTableWidgetItem):
        """Show file preview tooltip on hover (Task #41 - v2.9.13)."""
        if not item:
            return
        
        row = item.row()
        if row >= len(self.results):
            return
        
        filepath, stat = self.results[row]
        
        # Only show preview for files (not directories)
        if not os.path.isfile(filepath):
            item.setToolTip("Directory")
            return
        
        try:
            # Read first 3 lines (max 200 chars)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                char_count = 0
                for _ in range(3):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.rstrip())
                    char_count += len(line)
                    if char_count >= 200:
                        break
                
                preview = '\n'.join(lines)
                if char_count >= 200:
                    preview = preview[:200] + "..."
                
                item.setToolTip(preview if preview else "(empty file)")
        except Exception as e:
            item.setToolTip(f"Could not read file: {e}")


def show_advanced_file_search(parent=None, initial_dir: str = "") -> Optional[List[str]]:
    """
    Show advanced file search dialog.
    
    Args:
        parent: Parent widget
        initial_dir: Initial directory to search
    
    Returns:
        List of selected file paths, or None if cancelled
    """
    dialog = AdvancedFileSearchDialog(parent, initial_dir)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Get selected rows
        selected_rows = set(item.row() for item in dialog.table.selectedItems())
        if selected_rows:
            return [dialog.results[row][0] for row in sorted(selected_rows)]
        else:
            return [path for path, _ in dialog.results]
    return None
