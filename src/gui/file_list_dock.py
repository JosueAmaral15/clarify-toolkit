"""
File List Dock (Task #33 - v2.9.11, Task #50 - v2.9.25)

Dock panel for listing files with ls/dir-like parameters.
Displays detailed file information in a sortable table.

v2.9.114 Refactoring (Phase 2.4):
- Extracted FileFilterPanel (advanced filters UI)
- Extracted PresetManager (preset save/load/export/import)
- Extracted FileListTableManager (table display and context menu)
- Extracted FileListExecutor (core file listing logic)
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=attribute-defined-outside-init  # Qt widget creation pattern

import os
from typing import Dict, Any

from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QMessageBox, QMenu, QMainWindow
)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction

from src.core import FileListExecutor
from src.i18n.translator import tooltip_tr, tr

from .base_dock import BaseDock
from .widgets import FileFilterPanel, PresetManager, FileListTableManager


class FileListDock(BaseDock):
    """
    Dock widget for listing files with ls/dir parameters.

    Features:
    - Browse directory selection
    - ls/dir parameters: -la (all+long), -lh (human readable), -R (recursive)
    - Advanced filters panel (regex, size, mtime, extensions, depth, excludes)
    - Presets system (save/load/export/import)
    - Output table: Name, Size, Modified, Permissions, Path
    - Sort/filter capabilities
    - Export to CSV
    """

    def __init__(self, parent=None):
        self.settings = QSettings("Clarify", "FileList")
        self._load_preferences()

        # Store reference to main window for child components (v2.9.121 bugfix)
        self._main_window_ref = None
        if parent is not None:
            # Try to find main window in parent chain
            widget = parent
            while widget is not None:
                # Check if it's MainWindow by looking for characteristic that ALWAYS exists
                # dock_editor is lazy-loaded, so check for QMainWindow type + tab widget
                if isinstance(widget, QMainWindow) or hasattr(widget, 'tab_widget_main'):
                    self._main_window_ref = widget
                    break
                # Fallback: check for dock_editor (if already created)
                if hasattr(widget, 'dock_editor'):
                    self._main_window_ref = widget
                    break
                widget = widget.parent() if hasattr(widget, 'parent') else None

        super().__init__("File List", parent)

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

        # List button
        self.btn_list = QPushButton(tr("file_list.btn_list"))
        self.btn_list.clicked.connect(self._list_files)

        # Advanced Filters Panel (extracted component)
        self.filter_panel = FileFilterPanel()

        # Preset Manager (extracted component)
        self.preset_manager = PresetManager(settings_group="FileListDock")
        self.preset_manager.set_callbacks(
            get_filters=self._get_current_filters,
            apply_filters=self._apply_filters_to_widgets
        )

        # Table Manager (extracted component)
        self.table_manager = FileListTableManager(parent=self, main_window=self._main_window_ref)

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

        # Options
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(self.chk_all)
        opts_layout.addWidget(self.chk_long)
        opts_layout.addWidget(self.chk_human)
        opts_layout.addWidget(self.chk_recursive)
        opts_layout.addStretch()
        self.layout.addLayout(opts_layout)

        # List button
        self.layout.addWidget(self.btn_list)

        # Advanced filters panel
        self.layout.addWidget(self.filter_panel)

        # Preset manager
        self.layout.addWidget(self.preset_manager)

        # Table manager
        self.layout.addWidget(self.table_manager)

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
            QMessageBox.warning(self, tr("file_list.msg_missing_title"), tr("file_list.msg_missing_directory"))
            return

        if not os.path.isdir(directory):
            QMessageBox.warning(
                self, tr("file_list.msg_invalid_title"),
                tr("file_list.msg_invalid_directory").format(directory)
            )
            return

        # Save to recent directories
        self._add_to_recent(directory)

        # Get options
        show_hidden = self.chk_all.isChecked()
        human_readable = self.chk_human.isChecked()
        recursive = self.chk_recursive.isChecked()
        long_format = self.chk_long.isChecked()

        # Get advanced filters
        filters = self._build_filters()

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
            QMessageBox.warning(self, tr("file_list_dock.errors_title"), error_msg)

        # Convert FileInfo objects to dicts for table
        files_data = []
        for file_info in result.files:
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

        # Populate table
        self.table_manager.populate(files_data, human_readable=human_readable)

        # Save preferences after listing
        self._save_preferences()

    def _build_filters(self) -> Dict[str, Any]:
        """Build filter dictionary from filter panel."""
        # get_filters() already returns the correct format for FileListExecutor
        return self.filter_panel.get_filters()

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
            QMessageBox.information(self, tr("file_list.msg_no_recent_title"), tr("file_list.msg_no_recent_msg"))
            return

        menu = QMenu(self)
        for directory in self.recent_dirs:
            action = QAction(directory, self)
            action.triggered.connect(lambda checked, d=directory: self.ed_directory.setText(d))
            menu.addAction(action)

        menu.addSeparator()
        clear_action = QAction(tr("file_list_dock.action_clear_recent"), self)
        clear_action.triggered.connect(self._clear_recent)
        menu.addAction(clear_action)

        menu.exec(self.btn_recent.mapToGlobal(self.btn_recent.rect().bottomLeft()))

    def _clear_recent(self):
        """Clear recent directories list."""
        self.recent_dirs = []
        self._save_preferences()
        QMessageBox.information(self, tr("file_list.msg_cleared_title"), tr("file_list.msg_cleared_msg"))
