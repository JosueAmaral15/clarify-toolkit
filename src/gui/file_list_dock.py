"""
File List Dock (Task #33 - v2.9.11)

Dock panel for listing files with ls/dir-like parameters.
Displays detailed file information in a sortable table.
"""

import os
import stat
import pwd
import grp
import subprocess
import platform
from datetime import datetime
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction
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
        self.settings = QSettings("Clarify", "FileList")  # Task #42 - v2.9.13
        self._load_preferences()  # Task #42
    
    def _setup_ui(self):
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._setup_context_menu()  # Task #40 - v2.9.13
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Directory input
        self.ed_directory = QLineEdit()
        self.ed_directory.setPlaceholderText("Directory to list...")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse_directory)
        
        # Recent directories menu button (Task #42 - v2.9.13)
        self.btn_recent = QPushButton("Recent ▼")
        self.btn_recent.clicked.connect(self._show_recent_menu)
        
        # Options
        self.chk_all = QCheckBox("Show hidden files (-a)")
        self.chk_all.setToolTip("Show all files including hidden (dotfiles)")
        self.chk_all.setChecked(getattr(self, 'chk_all_state', False))  # Task #42
        
        self.chk_long = QCheckBox("Long format (-l)")
        self.chk_long.setToolTip("Show detailed information (permissions, size, modified)")
        self.chk_long.setChecked(getattr(self, 'chk_long_state', True))  # Task #42
        
        self.chk_human = QCheckBox("Human-readable sizes (-h)")
        self.chk_human.setToolTip("Show sizes in KB, MB, GB instead of bytes")
        self.chk_human.setChecked(getattr(self, 'chk_human_state', True))  # Task #42
        
        self.chk_recursive = QCheckBox("Recursive (-R)")
        self.chk_recursive.setToolTip("List subdirectories recursively")
        self.chk_recursive.setChecked(getattr(self, 'chk_recursive_state', False))  # Task #42
        
        # List button
        self.btn_list = QPushButton("List Files")
        self.btn_list.clicked.connect(self._list_files)
        
        # Quick filter (Task #39 - v2.9.12)
        self.ed_quick_filter = QLineEdit()
        self.ed_quick_filter.setPlaceholderText("Quick filter by filename...")
        self.ed_quick_filter.textChanged.connect(self._apply_quick_filter)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "Size", "Modified", "Permissions", "Path"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)  # Task #40 - Multi-select
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Task #40
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
        dir_layout.addWidget(self.btn_recent)  # Task #42 - v2.9.13
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
        
        # Quick filter
        layout.addWidget(self.ed_quick_filter)
        
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
    
    def _apply_quick_filter(self, text: str):
        """Apply quick filter to visible rows (Task #39 - v2.9.12)."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if name_item:
                name = name_item.text().lower()
                self.table.setRowHidden(row, text not in name)
    
    def _setup_context_menu(self):
        """Setup context menu for table (Task #40 - v2.9.13)."""
        self.table.customContextMenuRequested.connect(self._show_context_menu)
    
    def _show_context_menu(self, position):
        """Show context menu at position (Task #40 - v2.9.13)."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            return
        
        menu = QMenu(self)
        
        if len(selected_rows) == 1:
            action_text = "Open in File Manager"
        else:
            action_text = f"Open {len(selected_rows)} Locations in File Manager"
        
        action_open = QAction(action_text, self)
        action_open.triggered.connect(self._open_in_file_manager)
        menu.addAction(action_open)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def _open_in_file_manager(self):
        """Open selected file(s) location in file manager (Task #40 - v2.9.13)."""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()))
        
        for row in selected_rows:
            path_item = self.table.item(row, 4)  # Path column
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
                    QMessageBox.warning(self, "Error", f"Could not open file manager: {e}")
                    break
    
    def _load_preferences(self):
        """Load saved preferences (Task #42 - v2.9.13)."""
        # Load checkbox states
        self.chk_all_state = self.settings.value("show_hidden", False, type=bool)
        self.chk_long_state = self.settings.value("long_format", True, type=bool)
        self.chk_human_state = self.settings.value("human_readable", True, type=bool)
        self.chk_recursive_state = self.settings.value("recursive", False, type=bool)
        
        # Load recent directories
        self.recent_dirs = self.settings.value("recent_directories", [], type=list)
        if not isinstance(self.recent_dirs, list):
            self.recent_dirs = []
    
    def _save_preferences(self):
        """Save current preferences (Task #42 - v2.9.13)."""
        self.settings.setValue("show_hidden", self.chk_all.isChecked())
        self.settings.setValue("long_format", self.chk_long.isChecked())
        self.settings.setValue("human_readable", self.chk_human.isChecked())
        self.settings.setValue("recursive", self.chk_recursive.isChecked())
        self.settings.setValue("recent_directories", self.recent_dirs)
    
    def _add_to_recent(self, directory: str):
        """Add directory to recent list (Task #42 - v2.9.13)."""
        if directory in self.recent_dirs:
            self.recent_dirs.remove(directory)
        self.recent_dirs.insert(0, directory)
        self.recent_dirs = self.recent_dirs[:10]  # Keep last 10
        self._save_preferences()
    
    def _list_files(self):
        """List files with selected options."""
        directory = self.ed_directory.text().strip()
        
        if not directory:
            QMessageBox.warning(self, "Missing", "Please select a directory.")
            return
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "Invalid", f"Directory does not exist: {directory}")
            return
        
        # Save to recent directories (Task #42 - v2.9.13)
        self._add_to_recent(directory)
        
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
        
        # Save preferences after listing (Task #42 - v2.9.13)
        self._save_preferences()
        
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
    
    def _show_recent_menu(self):
        """Show recent directories menu (Task #42 - v2.9.13)."""
        if not self.recent_dirs:
            QMessageBox.information(self, "No Recent Directories", "No recent directories saved yet.")
            return
        
        menu = QMenu(self)
        for directory in self.recent_dirs:
            action = QAction(directory, self)
            action.triggered.connect(lambda checked, d=directory: self.ed_directory.setText(d))
            menu.addAction(action)
        
        menu.addSeparator()
        clear_action = QAction("Clear Recent", self)
        clear_action.triggered.connect(self._clear_recent)
        menu.addAction(clear_action)
        
        menu.exec(self.btn_recent.mapToGlobal(self.btn_recent.rect().bottomLeft()))
    
    def _clear_recent(self):
        """Clear recent directories list (Task #42 - v2.9.13)."""
        self.recent_dirs = []
        self._save_preferences()
        QMessageBox.information(self, "Cleared", "Recent directories list cleared.")
