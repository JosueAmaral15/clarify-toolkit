"""
File List Dock (Task #33 - v2.9.11)

Dock panel for listing files with ls/dir-like parameters.
Displays detailed file information in a sortable table.
"""

import os
import stat
import pwd
import grp
from datetime import datetime
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from .base_dock import BaseDock


class FileListDock(BaseDock):
    """
    Dock widget for listing files with ls/dir parameters.
    
    Features:
    - Browse directory selection
    - ls/dir parameters: -la (all+long), -lh (human readable), -R (recursive)
    - Output table: Name, Size, Modified, Permissions
    - Sort/filter capabilities
    - Export to CSV
    """
    
    def __init__(self, parent=None):
        super().__init__("File List", parent)
    
    def _setup_ui(self):
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Directory input
        self.ed_directory = QLineEdit()
        self.ed_directory.setPlaceholderText("Directory to list...")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse_directory)
        
        # Options
        self.chk_all = QCheckBox("Show hidden files (-a)")
        self.chk_all.setToolTip("Show all files including hidden (dotfiles)")
        
        self.chk_long = QCheckBox("Long format (-l)")
        self.chk_long.setToolTip("Show detailed information (permissions, size, modified)")
        self.chk_long.setChecked(True)  # Default to long format
        
        self.chk_human = QCheckBox("Human-readable sizes (-h)")
        self.chk_human.setToolTip("Show sizes in KB, MB, GB instead of bytes")
        self.chk_human.setChecked(True)
        
        self.chk_recursive = QCheckBox("Recursive (-R)")
        self.chk_recursive.setToolTip("List subdirectories recursively")
        
        # List button
        self.btn_list = QPushButton("List Files")
        self.btn_list.clicked.connect(self._list_files)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "Size", "Modified", "Permissions", "Path"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        # Stats label
        self.lbl_stats = QLabel("No files listed")
        
        # Export button
        self.btn_export = QPushButton("Export to CSV...")
        self.btn_export.clicked.connect(self._export_csv)
    
    def _create_layout(self):
        """Create layout."""
        layout = QVBoxLayout()
        
        # Directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.ed_directory)
        dir_layout.addWidget(self.btn_browse)
        layout.addLayout(dir_layout)
        
        # Options
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(self.chk_all)
        opts_layout.addWidget(self.chk_long)
        opts_layout.addWidget(self.chk_human)
        opts_layout.addWidget(self.chk_recursive)
        opts_layout.addStretch()
        layout.addLayout(opts_layout)
        
        # List button
        layout.addWidget(self.btn_list)
        
        # Table
        layout.addWidget(self.table)
        
        # Stats
        layout.addWidget(self.lbl_stats)
        
        # Export
        layout.addWidget(self.btn_export)
        
        self.setLayout(layout)
    
    def _browse_directory(self):
        """Browse for directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.ed_directory.text() or os.getcwd(),
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.ed_directory.setText(directory)
    
    def _list_files(self):
        """List files with selected options."""
        directory = self.ed_directory.text().strip()
        
        if not directory:
            QMessageBox.warning(self, "Missing", "Please select a directory.")
            return
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "Invalid", f"Directory does not exist: {directory}")
            return
        
        # Get options
        show_hidden = self.chk_all.isChecked()
        long_format = self.chk_long.isChecked()
        human_readable = self.chk_human.isChecked()
        recursive = self.chk_recursive.isChecked()
        
        # Clear table
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        
        # Collect files
        files = self._collect_files(directory, show_hidden, recursive)
        
        # Populate table
        total_size = 0
        for filepath in files:
            try:
                st = os.stat(filepath)
            except (PermissionError, FileNotFoundError):
                continue
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Name
            name = os.path.basename(filepath)
            if os.path.isdir(filepath):
                name += "/"
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Size
            if os.path.isfile(filepath):
                size = st.st_size
                total_size += size
                if human_readable:
                    size_str = self._human_readable_size(size)
                else:
                    size_str = str(size)
            else:
                size_str = "-"
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 1, size_item)
            
            # Modified
            mtime = datetime.fromtimestamp(st.st_mtime)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 2, QTableWidgetItem(mtime_str))
            
            # Permissions
            if long_format:
                perms = self._format_permissions(st.st_mode)
                owner = self._get_owner(st.st_uid)
                group = self._get_group(st.st_gid)
                perms_str = f"{perms} {owner}:{group}"
            else:
                perms_str = self._format_permissions(st.st_mode)
            self.table.setItem(row, 3, QTableWidgetItem(perms_str))
            
            # Path
            self.table.setItem(row, 4, QTableWidgetItem(filepath))
        
        self.table.setSortingEnabled(True)
        
        # Update stats
        count = self.table.rowCount()
        if human_readable:
            total_str = self._human_readable_size(total_size)
        else:
            total_str = f"{total_size} bytes"
        self.lbl_stats.setText(f"Listed {count} items | Total size: {total_str}")
    
    def _collect_files(self, directory: str, show_hidden: bool, recursive: bool) -> List[str]:
        """Collect files from directory."""
        files = []
        
        try:
            entries = os.listdir(directory)
        except PermissionError:
            return files
        
        for entry in sorted(entries):
            # Skip hidden files if not showing all
            if not show_hidden and entry.startswith('.'):
                continue
            
            filepath = os.path.join(directory, entry)
            files.append(filepath)
            
            # Recurse into subdirectories
            if recursive and os.path.isdir(filepath):
                files.extend(self._collect_files(filepath, show_hidden, True))
        
        return files
    
    def _human_readable_size(self, size: int) -> str:
        """Convert size to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _format_permissions(self, mode: int) -> str:
        """Format permissions string (Unix-style)."""
        perms = ''
        
        # File type
        if stat.S_ISDIR(mode):
            perms += 'd'
        elif stat.S_ISLNK(mode):
            perms += 'l'
        else:
            perms += '-'
        
        # Owner permissions
        perms += 'r' if mode & stat.S_IRUSR else '-'
        perms += 'w' if mode & stat.S_IWUSR else '-'
        perms += 'x' if mode & stat.S_IXUSR else '-'
        
        # Group permissions
        perms += 'r' if mode & stat.S_IRGRP else '-'
        perms += 'w' if mode & stat.S_IWGRP else '-'
        perms += 'x' if mode & stat.S_IXGRP else '-'
        
        # Other permissions
        perms += 'r' if mode & stat.S_IROTH else '-'
        perms += 'w' if mode & stat.S_IWOTH else '-'
        perms += 'x' if mode & stat.S_IXOTH else '-'
        
        return perms
    
    def _get_owner(self, uid: int) -> str:
        """Get owner name from UID."""
        try:
            return pwd.getpwuid(uid).pw_name
        except (KeyError, AttributeError):
            return str(uid)
    
    def _get_group(self, gid: int) -> str:
        """Get group name from GID."""
        try:
            return grp.getgrgid(gid).gr_name
        except (KeyError, AttributeError):
            return str(gid)
    
    def _export_csv(self):
        """Export table to CSV file."""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No Data", "No files to export.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export File List",
            "file_list.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write("Name,Size,Modified,Permissions,Path\n")
                
                # Data
                for row in range(self.table.rowCount()):
                    items = []
                    for col in range(5):
                        item = self.table.item(row, col)
                        text = item.text() if item else ""
                        # Escape commas
                        text = text.replace('"', '""')
                        items.append(f'"{text}"')
                    f.write(",".join(items) + "\n")
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"File list exported to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export: {e}")
