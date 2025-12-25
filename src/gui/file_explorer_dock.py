"""
File Explorer Dock (Unification of File List + Advanced File Search)

Unified dock panel for exploring and listing files with advanced filters.
Replaces separate File List (v2.9.11) and Advanced File Search tools.

v2.9.115 Integration:
- Consolidates redundant File List + Advanced File Search (80% overlap)
- Adds dialog mode (can function as Dock OR QDialog modal)
- Adds file type filter (Files Only / Directories Only / Any)
- Adds selection mode (return list of selected files)
- Maintains all existing features from both tools
"""

import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QMessageBox, QMenu,
    QComboBox, QDialog, QDialogButtonBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QSettings, QDate
from PySide6.QtGui import QAction
from .base_dock import BaseDock
from .widgets import FileFilterPanel, PresetManager, FileListTableManager
from src.core import FileListExecutor, FileInfo, ListResult
from src.i18n.translator import tooltip_tr, tr


class FileExplorerDock(BaseDock):
    """
    Unified dock/dialog widget for file exploration with advanced filters.
    
    Features (from File List):
    - Browse directory selection
    - Unix-style parameters: -la (all+long), -lh (human readable), -R (recursive)
    - Advanced filters panel (regex, size, mtime, extensions, depth, excludes)
    - Presets system (save/load/export/import)
    - Output table: Name | Size | Modified | Permissions | Path
    - Sort/filter capabilities
    - Export to CSV
    - Context menu: "Open in File Manager"
    - Statistics: count + total size
    
    New Features (from Advanced File Search):
    - File type filter (Files Only / Directories Only / Any)
    - Selection mode (multi-select and return selected files)
    - Dialog mode (can function as modal dialog)
    - Preview tooltips (hover shows full path)
    """
    
    def __init__(self, parent=None, dialog_mode: bool = False):
        """
        Initialize File Explorer.
        
        Args:
            parent: Parent widget
            dialog_mode: If True, behaves as modal dialog with OK/Cancel buttons
        """
        self.dialog_mode = dialog_mode
        self.selected_files: List[str] = []
        self.settings = QSettings("Clarify", "FileExplorer")
        self._load_preferences()
        
        # Always initialize as BaseDock (QDockWidget)
        # Dialog mode only adds OK/Cancel buttons, doesn't change widget type
        super().__init__("File Explorer", parent)
    
    def _setup_ui(self):
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()
    
    def _create_widgets(self):
        """Create UI widgets."""
        # Directory input
        self.ed_directory = QLineEdit()
        self.ed_directory.setPlaceholderText(tr("file_list.placeholder_directory"))
        self.btn_browse = QPushButton(tr("file_list.btn_browse"))
        self.btn_browse.clicked.connect(self._browse_directory)
        
        # Recent directories menu button
        self.btn_recent = QPushButton(tr("file_list.btn_recent"))
        self.btn_recent.clicked.connect(self._show_recent_menu)
        
        # Options
        self.chk_all = QCheckBox(tr("file_list.chk_all"))
        self.chk_all.setChecked(getattr(self, 'chk_all_state', False))
        
        self.chk_long = QCheckBox(tr("file_list.chk_long"))
        self.chk_long.setChecked(getattr(self, 'chk_long_state', True))
        
        self.chk_human = QCheckBox(tr("file_list.chk_human"))
        self.chk_human.setChecked(getattr(self, 'chk_human_state', True))
        
        self.chk_recursive = QCheckBox(tr("file_list.chk_recursive"))
        self.chk_recursive.setChecked(getattr(self, 'chk_recursive_state', False))
        
        # NEW: File type filter (from Advanced File Search)
        self.lbl_type = QLabel("Type:")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Any", "Files Only", "Directories Only"])
        self.combo_type.setToolTip("Filter by file type")
        
        # NEW: Selection mode (from Advanced File Search)
        if self.dialog_mode:
            self.chk_selection_mode = QCheckBox("Selection Mode")
            self.chk_selection_mode.setChecked(True)
            self.chk_selection_mode.setToolTip("Enable multi-selection to return selected files")
        
        # List/Search button
        self.btn_list = QPushButton(tr("file_list.btn_list"))
        self.btn_list.clicked.connect(self._list_files)
        
        # Advanced Filters Panel (extracted component)
        self.filter_panel = FileFilterPanel()
        
        # Preset Manager (extracted component)
        if not self.dialog_mode:  # Presets only in dock mode
            self.preset_manager = PresetManager(settings_group="FileExplorerDock")
            self.preset_manager.set_callbacks(
                get_filters=self._get_current_filters,
                apply_filters=self._apply_filters_to_widgets
            )
        
        # Table Manager (extracted component)
        self.table_manager = FileListTableManager()
        
        # NEW: Enable tooltips for preview (from Advanced File Search)
        self.table_manager.table.setMouseTracking(True)
        self.table_manager.table.itemEntered.connect(self._show_preview_tooltip)
        
        # Dialog mode buttons
        if self.dialog_mode:
            self.button_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            self.button_box.accepted.connect(self._accept_dialog)
            self.button_box.rejected.connect(self.reject)
    
    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets."""
        self.ed_directory.setToolTip(tooltip_tr("file_list.ed_directory"))
        self.btn_browse.setToolTip(tooltip_tr("file_list.btn_browse"))
        self.btn_recent.setToolTip(tooltip_tr("file_list.btn_recent"))
        self.chk_all.setToolTip(tooltip_tr("file_list.chk_all"))
        self.chk_long.setToolTip(tooltip_tr("file_list.chk_long"))
        self.chk_human.setToolTip(tooltip_tr("file_list.chk_human"))
        self.chk_recursive.setToolTip(tooltip_tr("file_list.chk_recursive"))
        self.btn_list.setToolTip(tooltip_tr("file_list.btn_list"))
    
    def _create_layout(self):
        """Create layout."""
        # Directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel(tr("file_list.lbl_directory")))
        dir_layout.addWidget(self.ed_directory)
        dir_layout.addWidget(self.btn_browse)
        dir_layout.addWidget(self.btn_recent)
        self.layout.addLayout(dir_layout)
        
        # Options row 1: Unix-style options
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(self.chk_all)
        opts_layout.addWidget(self.chk_long)
        opts_layout.addWidget(self.chk_human)
        opts_layout.addWidget(self.chk_recursive)
        opts_layout.addStretch()
        self.layout.addLayout(opts_layout)
        
        # Options row 2: Type filter + Selection mode (NEW)
        opts2_layout = QHBoxLayout()
        opts2_layout.addWidget(self.lbl_type)
        opts2_layout.addWidget(self.combo_type)
        if self.dialog_mode:
            opts2_layout.addWidget(self.chk_selection_mode)
        opts2_layout.addStretch()
        self.layout.addLayout(opts2_layout)
        
        # List button
        self.layout.addWidget(self.btn_list)
        
        # Advanced filters panel
        self.layout.addWidget(self.filter_panel)
        
        # Preset manager (only in dock mode)
        if not self.dialog_mode:
            self.layout.addWidget(self.preset_manager)
        
        # Table manager
        self.layout.addWidget(self.table_manager)
        
        # Dialog buttons (only in dialog mode)
        if self.dialog_mode:
            self.layout.addWidget(self.button_box)
    
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
        
        # Save to recent directories
        self._add_to_recent(directory)
        
        # Get options
        show_hidden = self.chk_all.isChecked()
        human_readable = self.chk_human.isChecked()
        recursive = self.chk_recursive.isChecked()
        long_format = self.chk_long.isChecked()
        
        # Get file type filter (NEW)
        type_filter = self.combo_type.currentText()
        
        # Get advanced filters
        filters = self._build_filters()
        
        # Add type filter to filters dict (NEW)
        if type_filter == "Files Only":
            filters['type'] = 'files'
        elif type_filter == "Directories Only":
            filters['type'] = 'dirs'
        else:
            filters['type'] = 'any'
        
        # Execute file listing using FileListExecutor
        result = FileListExecutor.list_files(
            directory=directory,
            show_hidden=show_hidden,
            recursive=recursive,
            filters=filters
        )
        
        # Show errors if any
        if result.errors:
            error_msg = "\n".join(result.errors[:5])  # Show first 5 errors
            if len(result.errors) > 5:
                error_msg += f"\n... and {len(result.errors) - 5} more errors"
            QMessageBox.warning(self, "Errors Encountered", error_msg)
        
        # Filter by type (NEW - post-processing since FileListExecutor might not support 'type')
        filtered_files = result.files
        if type_filter == "Files Only":
            filtered_files = [f for f in result.files if not f.is_dir]
        elif type_filter == "Directories Only":
            filtered_files = [f for f in result.files if f.is_dir]
        
        # Convert FileInfo objects to dicts for table
        files_data = []
        for file_info in filtered_files:
            # Format permissions
            perms = file_info.permissions
            if long_format:
                perms = f"{perms} {file_info.owner}:{file_info.group}"
            
            files_data.append({
                'name': file_info.name,
                'size': file_info.size,
                'mtime': file_info.mtime,
                'permissions': perms,
                'path': file_info.path,
                'is_dir': file_info.is_dir
            })
        
        # Enable multi-selection if in selection mode (NEW)
        if self.dialog_mode and hasattr(self, 'chk_selection_mode') and self.chk_selection_mode.isChecked():
            self.table_manager.table.setSelectionMode(QAbstractItemView.MultiSelection)
        else:
            self.table_manager.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Populate table
        self.table_manager.populate(files_data, human_readable=human_readable)
        
        # Save preferences after listing
        self._save_preferences()
    
    def _build_filters(self) -> Dict[str, Any]:
        """Build filter dictionary from filter panel."""
        panel_filters = self.filter_panel.get_filters()
        
        # Convert to format expected by FileListExecutor
        filters = {}
        
        # Regex filter
        if panel_filters.get('regex_enabled') and panel_filters.get('regex_pattern'):
            filters['regex'] = {
                'enabled': True,
                'pattern': panel_filters['regex_pattern']
            }
        
        # Size filter (convert to bytes)
        size_config = {}
        if panel_filters.get('size_min'):
            min_val = panel_filters['size_min']
            min_unit = panel_filters.get('size_min_unit', 'B')
            size_config['min'] = min_val * FileFilterPanel.SIZE_UNITS[min_unit]
        
        if panel_filters.get('size_max'):
            max_val = panel_filters['size_max']
            max_unit = panel_filters.get('size_max_unit', 'B')
            size_config['max'] = max_val * FileFilterPanel.SIZE_UNITS[max_unit]
        
        if size_config:
            filters['size'] = size_config
        
        # MTime filter (convert to date objects)
        mtime_config = {}
        if panel_filters.get('mtime_after_enabled') and panel_filters.get('mtime_after'):
            mtime_config['after'] = panel_filters['mtime_after']
        
        if panel_filters.get('mtime_before_enabled') and panel_filters.get('mtime_before'):
            mtime_config['before'] = panel_filters['mtime_before']
        
        if mtime_config:
            filters['mtime'] = mtime_config
        
        # Extensions filter
        if panel_filters.get('extensions'):
            filters['extensions'] = panel_filters['extensions']
        
        # Depth filter
        if panel_filters.get('depth', 0) > 0:
            filters['depth'] = panel_filters['depth']
        
        # Exclude directories
        exclude_dirs = panel_filters.get('exclude_dirs', [])
        if exclude_dirs:
            filters['exclude_dirs'] = exclude_dirs
        
        return filters
    
    def _get_current_filters(self) -> Dict[str, Any]:
        """Get current filter settings (for preset manager)."""
        return self.filter_panel.get_filters()
    
    def _apply_filters_to_widgets(self, filters: Dict[str, Any]):
        """Apply filter settings to widgets (for preset manager)."""
        self.filter_panel.set_filters(filters)
    
    def _load_preferences(self):
        """Load saved preferences."""
        self.chk_all_state = self.settings.value("show_hidden", False, type=bool)
        self.chk_long_state = self.settings.value("long_format", True, type=bool)
        self.chk_human_state = self.settings.value("human_readable", True, type=bool)
        self.chk_recursive_state = self.settings.value("recursive", False, type=bool)
        
        # Load recent directories
        self.recent_dirs = self.settings.value("recent_directories", [], type=list)
        if not isinstance(self.recent_dirs, list):
            self.recent_dirs = []
    
    def _save_preferences(self):
        """Save current preferences."""
        self.settings.setValue("show_hidden", self.chk_all.isChecked())
        self.settings.setValue("long_format", self.chk_long.isChecked())
        self.settings.setValue("human_readable", self.chk_human.isChecked())
        self.settings.setValue("recursive", self.chk_recursive.isChecked())
        self.settings.setValue("recent_directories", self.recent_dirs)
    
    def _add_to_recent(self, directory: str):
        """Add directory to recent list."""
        if directory in self.recent_dirs:
            self.recent_dirs.remove(directory)
        self.recent_dirs.insert(0, directory)
        self.recent_dirs = self.recent_dirs[:10]  # Keep last 10
        self._save_preferences()
    
    def _show_recent_menu(self):
        """Show recent directories menu."""
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
        """Clear recent directories list."""
        self.recent_dirs = []
        self._save_preferences()
        QMessageBox.information(self, "Cleared", "Recent directories list cleared.")
    
    def _show_preview_tooltip(self, item):
        """
        Show preview tooltip on hover (NEW from Advanced File Search).
        
        Args:
            item: QTableWidgetItem being hovered
        """
        if item is None:
            return
        
        row = item.row()
        # Get full path from column 4 (Path)
        path_item = self.table_manager.table.item(row, 4)
        if path_item:
            full_path = path_item.text()
            item.setToolTip(full_path)
    
    def _accept_dialog(self):
        """Accept dialog and collect selected files (NEW - dialog mode)."""
        if not self.dialog_mode:
            return
        
        # Get selected rows
        selected_rows = set(item.row() for item in self.table_manager.table.selectedItems())
        
        # Extract file paths
        self.selected_files = []
        for row in sorted(selected_rows):
            path_item = self.table_manager.table.item(row, 4)
            if path_item:
                self.selected_files.append(path_item.text())
        
        if not self.selected_files:
            QMessageBox.warning(self, "No Selection", "Please select at least one file.")
            return
        
        self.accept()
    
    def get_selected_files(self) -> List[str]:
        """
        Get list of selected files (NEW - dialog mode).
        
        Returns:
            List of selected file paths
        """
        return self.selected_files


def show_file_explorer_dialog(parent=None, initial_dir: str = "") -> Optional[List[str]]:
    """
    Show File Explorer as a modal dialog and return selected files.
    
    This is a helper function compatible with previous show_advanced_file_search().
    
    Args:
        parent: Parent widget
        initial_dir: Initial directory to display
    
    Returns:
        List of selected file paths, or None if canceled
    
    Example:
        >>> files = show_file_explorer_dialog(self, "/home/user/projects")
        >>> if files:
        ...     print(f"Selected {len(files)} files")
    """
    dialog = FileExplorerDock(parent, dialog_mode=True)
    dialog.ed_directory.setText(initial_dir or os.getcwd())
    dialog.resize(800, 600)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_selected_files()
    return None
