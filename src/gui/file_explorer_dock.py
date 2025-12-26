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
import time
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QMessageBox, QMenu,
    QComboBox, QDialog, QDialogButtonBox, QAbstractItemView, QGroupBox,
    QProgressDialog, QSplitter, QScrollArea, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt, QSettings, QDate, QTimer, QObject, QEvent
from PySide6.QtGui import QAction
from .base_dock import BaseDock
from .widgets import (
    FileFilterPanel, PresetManager, FileListTableManager,
    FileNameQueryPanel, ContentQueryPanel, SearchOptionsPanel,
    ReplacePanel, ConditionsGrid, CollapsibleSection
)
from .panels import ResultsTree
from src.core import FileListExecutor, FileInfo, ListResult
from src.core.file_explorer_executor import (
    UnifiedFileExplorerExecutor, SearchResult, SearchMatch
)
from src.i18n.translator import tooltip_tr, tr


class HoverExpandFilter(QObject):
    """
    Event filter for hover expansion of results panel (v2.9.117 - C.1).
    
    Expands the right panel when mouse hovers over it,
    restores original size when mouse leaves.
    """
    
    def __init__(self, splitter: QSplitter, original_sizes: list):
        """
        Initialize hover expand filter.
        
        Args:
            splitter: The QSplitter to adjust
            original_sizes: Original sizes to restore [left, right]
        """
        super().__init__()
        self._splitter = splitter
        self._original_sizes = original_sizes
        self._is_expanded = False
    
    def eventFilter(self, obj, event):
        """Handle enter/leave events for hover expansion."""
        if event.type() == QEvent.Type.Enter:
            # Expand right panel
            if not self._is_expanded:
                total_width = sum(self._splitter.sizes())
                new_left = int(total_width * 0.15)  # 15% left
                new_right = total_width - new_left   # 85% right
                self._splitter.setSizes([new_left, new_right])
                self._is_expanded = True
        
        elif event.type() == QEvent.Type.Leave:
            # Restore original sizes
            if self._is_expanded:
                self._splitter.setSizes(self._original_sizes)
                self._is_expanded = False
        
        return False  # Don't filter the event


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
        
        # Initialize unified executor (v2.9.116)
        self.executor = UnifiedFileExplorerExecutor()
        self.executor.progress.connect(self._on_progress)
        self.executor.progress_detailed.connect(self._on_progress_detailed)
        self.executor.done.connect(self._on_execution_done)
        self.executor.error.connect(self._on_execution_error)
        
        # Progress dialog for long operations
        self.progress_dialog = None
        
        # Auto-search debounce timer (500ms delay)
        self.auto_search_timer = QTimer()
        self.auto_search_timer.setSingleShot(True)
        self.auto_search_timer.timeout.connect(self._trigger_auto_search)
        
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
        # ============================================================================
        # SECTION 1: Directory & Type (📁 - Always Expanded)
        # ============================================================================
        self.section_directory = QGroupBox("📁 Directory & Type")
        self.section_directory.setCheckable(False)
        self.section_directory.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
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
        
        # File type filter
        self.lbl_type = QLabel("Type:")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Any", "Files Only", "Directories Only"])
        self.combo_type.setToolTip("Filter by file type")
        
        # Selection mode (dialog only)
        if self.dialog_mode:
            self.chk_selection_mode = QCheckBox("Selection Mode")
            self.chk_selection_mode.setChecked(True)
            self.chk_selection_mode.setToolTip("Enable multi-selection to return selected files")
        
        # ============================================================================
        # SECTION 2: Search & Replace (🔍 - Always Expanded)
        # ============================================================================
        self.section_search = QGroupBox("🔍 Search & Replace")
        self.section_search.setCheckable(False)
        self.section_search.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # NEW: Integrated search widgets (v2.9.116)
        self.filename_panel = FileNameQueryPanel()
        self.content_panel = ContentQueryPanel()
        self.search_options_panel = SearchOptionsPanel()
        self.replace_panel = ReplacePanel()
        
        # Connect search widget signals
        self.filename_panel.pattern_changed.connect(self._on_search_params_changed)
        self.content_panel.query_changed.connect(self._on_search_params_changed)
        self.search_options_panel.options_changed.connect(self._on_search_params_changed)
        self.replace_panel.replace_first_requested.connect(self._on_replace_first)
        self.replace_panel.replace_all_requested.connect(self._on_replace_all)
        
        # ============================================================================
        # SECTION 3: Filters (⚙️ - Collapsible with Animation - v2.9.117 B.6)
        # ============================================================================
        self.section_filters = CollapsibleSection("⚙️ Filters")
        self.section_filters.setCollapsed(True)  # Start collapsed
        
        # Advanced Filters Panel (extracted component)
        self.filter_panel = FileFilterPanel()
        self.section_filters.setContent(self.filter_panel)
        
        # ============================================================================
        # SECTION 4: Advanced Conditions (🎯 - Collapsible with Animation - v2.9.117 B.6)
        # ============================================================================
        self.section_conditions = CollapsibleSection("🎯 Advanced Conditions")
        self.section_conditions.setCollapsed(True)  # Start collapsed
        
        # NEW: Conditions grid with AND/OR logic (v2.9.116)
        self.conditions_grid = ConditionsGrid()
        self.conditions_grid.conditions_changed.connect(self._on_conditions_changed)
        self.section_conditions.setContent(self.conditions_grid)
        
        # ============================================================================
        # SECTION 5: Presets (💾 - Collapsible with Animation, Dock Mode Only - v2.9.117 B.6)
        # ============================================================================
        if not self.dialog_mode:
            self.section_presets = CollapsibleSection("💾 Presets")
            self.section_presets.setCollapsed(True)  # Start collapsed
            
            # Preset Manager (extracted component)
            self.preset_manager = PresetManager(settings_group="FileExplorerDock")
            self.preset_manager.set_callbacks(
                get_filters=self._get_current_filters,
                apply_filters=self._apply_filters_to_widgets
            )
        
        # ============================================================================
        # Action Buttons (v2.9.117 - B.3: Separate Browse/Search)
        # ============================================================================
        self.btn_list_browse = QPushButton("📁 Browse")
        self.btn_list_browse.setToolTip("List all files in directory (no search)")
        self.btn_list_browse.clicked.connect(self._browse_files)
        self.btn_list_browse.setStyleSheet("QPushButton { background-color: #4a90e2; color: white; padding: 8px; font-weight: bold; }")
        
        self.btn_list_search = QPushButton("🔍 Search")
        self.btn_list_search.setToolTip("Search files by name/content patterns")
        self.btn_list_search.clicked.connect(self._search_files)
        self.btn_list_search.setStyleSheet("QPushButton { background-color: #27ae60; color: white; padding: 8px; font-weight: bold; }")
        
        # ============================================================================
        # Results Table
        # ============================================================================
        # Table Manager (extracted component)
        self.table_manager = FileListTableManager()
        
        # Enable tooltips for preview
        self.table_manager.table.setMouseTracking(True)
        self.table_manager.table.itemEntered.connect(self._show_preview_tooltip)
        
        # ============================================================================
        # Dialog Buttons (Dialog Mode Only)
        # ============================================================================
        if self.dialog_mode:
            self.button_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            self.button_box.accepted.connect(self._accept_dialog)
            self.button_box.rejected.connect(self.reject)
    
    def _apply_tooltips(self):
        """Apply internationalized tooltips to all widgets (v2.9.116)."""
        # Directory & Type section
        self.ed_directory.setToolTip(tooltip_tr("file_list.ed_directory"))
        self.btn_browse.setToolTip(tooltip_tr("file_list.btn_browse"))
        self.btn_recent.setToolTip(tooltip_tr("file_list.btn_recent"))
        self.chk_all.setToolTip(tooltip_tr("file_list.chk_all"))
        self.chk_long.setToolTip(tooltip_tr("file_list.chk_long"))
        self.chk_human.setToolTip(tooltip_tr("file_list.chk_human"))
        self.chk_recursive.setToolTip(tooltip_tr("file_list.chk_recursive"))
        # Action buttons tooltips (v2.9.117 - B.3)
        self.btn_list_browse.setToolTip(tooltip_tr("file_list.btn_browse"))
        self.btn_list_search.setToolTip(tooltip_tr("file_list.btn_search"))
        
        # Search & Replace section
        self.section_search.setToolTip(
            "Search for files by name pattern or content query. "
            "Leave empty to browse all files."
        )
        self.filename_panel.setToolTip(
            "Enter filename pattern (e.g., *.py, test_*.json). "
            "Supports wildcards: * (any chars), ? (single char)"
        )
        self.content_panel.setToolTip(
            "Search for text inside files. "
            "Supports multi-line queries and regex patterns."
        )
        self.search_options_panel.setToolTip(
            "Configure search behavior: case sensitivity, whole word matching, regex mode"
        )
        self.replace_panel.setToolTip(
            "Replace matched text in selected files. "
            "Select files in results table first."
        )
        
        # Filters section
        self.section_filters.setToolTip(
            "Advanced filters: regex patterns, size ranges, date ranges, "
            "file extensions, depth limits, exclusions"
        )
        
        # Conditions section
        self.section_conditions.setToolTip(
            "Apply complex filtering conditions with AND/OR logic. "
            "Combine multiple criteria for precise file selection."
        )
        
        # Presets section (if visible)
        if hasattr(self, 'section_presets'):
            self.section_presets.setToolTip(
                "Save and load filter configurations for reuse. "
                "Export/import presets to share with others."
            )
    
    def _create_layout(self):
        """Create horizontal splitter layout with controls on left, results on right (v2.9.117 - B.1)."""
        # ============================================================================
        # LEFT PANEL: All control sections in scroll area
        # ============================================================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # ----------------------------------------------------------------------------
        # SECTION 1: Directory & Type
        # ----------------------------------------------------------------------------
        section1_layout = QVBoxLayout()
        
        # Directory row
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel(tr("file_list.lbl_directory")))
        dir_layout.addWidget(self.ed_directory)
        dir_layout.addWidget(self.btn_browse)
        dir_layout.addWidget(self.btn_recent)
        section1_layout.addLayout(dir_layout)
        
        # Options row 1: Unix-style options
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(self.chk_all)
        opts_layout.addWidget(self.chk_long)
        opts_layout.addWidget(self.chk_human)
        opts_layout.addWidget(self.chk_recursive)
        opts_layout.addStretch()
        section1_layout.addLayout(opts_layout)
        
        # Options row 2: Type filter + Selection mode
        opts2_layout = QHBoxLayout()
        opts2_layout.addWidget(self.lbl_type)
        opts2_layout.addWidget(self.combo_type)
        if self.dialog_mode:
            opts2_layout.addWidget(self.chk_selection_mode)
        opts2_layout.addStretch()
        section1_layout.addLayout(opts2_layout)
        
        self.section_directory.setLayout(section1_layout)
        left_layout.addWidget(self.section_directory)
        
        # ----------------------------------------------------------------------------
        # SECTION 2: Search & Replace
        # ----------------------------------------------------------------------------
        section2_layout = QVBoxLayout()
        section2_layout.addWidget(self.filename_panel)
        section2_layout.addWidget(self.content_panel)
        section2_layout.addWidget(self.search_options_panel)
        section2_layout.addWidget(self.replace_panel)
        
        self.section_search.setLayout(section2_layout)
        left_layout.addWidget(self.section_search)
        
        # ----------------------------------------------------------------------------
        # SECTION 3: Filters (v2.9.117 - B.6: CollapsibleSection)
        # ----------------------------------------------------------------------------
        left_layout.addWidget(self.section_filters)
        
        # ----------------------------------------------------------------------------
        # SECTION 4: Advanced Conditions (v2.9.117 - B.6: CollapsibleSection)
        # ----------------------------------------------------------------------------
        left_layout.addWidget(self.section_conditions)
        
        # ----------------------------------------------------------------------------
        # SECTION 5: Presets (Dock Mode Only - v2.9.117 - B.6: CollapsibleSection)
        # ----------------------------------------------------------------------------
        if not self.dialog_mode:
            self.section_presets.setContent(self.preset_manager)
            left_layout.addWidget(self.section_presets)
        
        # ----------------------------------------------------------------------------
        # Action Buttons (v2.9.117 - B.3)
        # ----------------------------------------------------------------------------
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_list_browse)
        buttons_layout.addWidget(self.btn_list_search)
        buttons_layout.setSpacing(8)
        left_layout.addLayout(buttons_layout)
        left_layout.addStretch()  # Push everything to top
        
        # Wrap left panel in scroll area
        left_scroll = QScrollArea()
        left_scroll.setWidget(left_panel)
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # ============================================================================
        # RIGHT PANEL: Results with QStackedWidget (v2.9.117 - B.2)
        # ============================================================================
        # Create ResultsTree for search mode
        self.results_tree = ResultsTree()
        
        # Create QStackedWidget to switch between browse/search views
        self.results_stack = QStackedWidget()
        self.results_stack.addWidget(self.results_tree)     # Index 0: Search mode (tree)
        self.results_stack.addWidget(self.table_manager)    # Index 1: Browse mode (table)
        
        # Start in browse mode (table view)
        self.results_stack.setCurrentIndex(1)
        
        # ============================================================================
        # STATISTICS PANEL (v2.9.117 - B.4)
        # ============================================================================
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(8, 8, 8, 8)
        stats_layout.setSpacing(16)
        
        # Files count
        self.lbl_files_count = QLabel("📄 Files: 0")
        self.lbl_files_count.setStyleSheet("font-weight: bold; color: #2c3e50;")
        stats_layout.addWidget(self.lbl_files_count)
        
        # Directories count
        self.lbl_dirs_count = QLabel("📁 Dirs: 0")
        self.lbl_dirs_count.setStyleSheet("font-weight: bold; color: #2c3e50;")
        stats_layout.addWidget(self.lbl_dirs_count)
        
        # Total size
        self.lbl_total_size = QLabel("💾 Size: 0 B")
        self.lbl_total_size.setStyleSheet("font-weight: bold; color: #2c3e50;")
        stats_layout.addWidget(self.lbl_total_size)
        
        # Execution time
        self.lbl_exec_time = QLabel("⏱️ Time: 0.00s")
        self.lbl_exec_time.setStyleSheet("font-weight: bold; color: #2c3e50;")
        stats_layout.addWidget(self.lbl_exec_time)
        
        stats_layout.addStretch()
        
        # Export CSV button (v2.9.117 - B.5)
        self.btn_export_csv = QPushButton("💾 Export CSV")
        self.btn_export_csv.setToolTip("Export current results to CSV file")
        self.btn_export_csv.clicked.connect(self._export_results_csv)
        self.btn_export_csv.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        stats_layout.addWidget(self.btn_export_csv)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.results_stack)
        right_layout.addWidget(stats_frame)
        
        # ============================================================================
        # HORIZONTAL SPLITTER: Left (controls) + Right (results)
        # ============================================================================
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(left_scroll)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([300, 900])  # 25% left, 75% right
        self.splitter.setStretchFactor(0, 1)  # Left panel can shrink
        self.splitter.setStretchFactor(1, 3)  # Right panel gets 3x space
        
        # ============================================================================
        # HOVER EXPANSION (v2.9.117 - C.1)
        # ============================================================================
        # Store original sizes for restoration
        self._original_sizes = [300, 900]
        
        # Create and install hover event filter on right panel
        self._hover_filter = HoverExpandFilter(self.splitter, self._original_sizes)
        right_panel.installEventFilter(self._hover_filter)
        
        # Add splitter to main layout
        self.layout.addWidget(self.splitter)
        
        # ============================================================================
        # Dialog Buttons (Dialog Mode Only)
        # ============================================================================
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
    
    def _browse_files(self):
        """Browse all files in directory without search filters (v2.9.117 - B.3)."""
        # Clear search fields to ensure browse mode
        self.filename_panel.clear()
        self.content_panel.clear()
        # Execute list operation (will detect no search and use browse mode)
        self._list_files()
    
    def _search_files(self):
        """Search files with current patterns (v2.9.117 - B.3)."""
        # Validate that at least one search criteria is set
        filename_pattern = self.filename_panel.get_pattern()
        content_query = self.content_panel.get_query()
        
        if not filename_pattern and not content_query:
            QMessageBox.information(
                self,
                "No Search Criteria",
                "Please enter a filename pattern or content query to search.\n\n"
                "For browsing all files, use the Browse button instead."
            )
            return
        
        # Execute list operation (will detect search criteria and use search mode)
        self._list_files()
    
    def _list_files(self):
        """List or search files with unified executor (v2.9.116)."""
        # Start timer (v2.9.117 - B.4)
        start_time = time.time()
        
        directory = self.ed_directory.text().strip()
        
        if not directory:
            QMessageBox.warning(self, "Missing", "Please select a directory.")
            return
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "Invalid", f"Directory does not exist: {directory}")
            return
        
        if not os.access(directory, os.R_OK):
            QMessageBox.warning(self, "Permission Denied", f"Cannot read directory: {directory}")
            return
        
        # Save to recent directories
        self._add_to_recent(directory)
        
        # Get options
        show_hidden = self.chk_all.isChecked()
        human_readable = self.chk_human.isChecked()
        recursive = self.chk_recursive.isChecked()
        long_format = self.chk_long.isChecked()
        
        # Get file type filter
        type_filter = self.combo_type.currentText()
        
        # Get advanced filters
        filters = self._build_filters()
        
        # Add type filter to filters dict
        if type_filter == "Files Only":
            filters['type'] = 'files'
        elif type_filter == "Directories Only":
            filters['type'] = 'dirs'
        else:
            filters['type'] = 'any'
        
        # ============================================================================
        # UNIFIED EXECUTOR INTEGRATION (v2.9.116)
        # ============================================================================
        # Get search parameters from new widgets
        filename_pattern = self.filename_panel.get_pattern()
        content_query = self.content_panel.get_query()
        search_options = self.search_options_panel.get_options()
        conditions = self.conditions_grid.get_conditions()
        
        # Determine if this is a search or browse operation
        is_search = bool(filename_pattern or content_query)
        
        if is_search:
            # Execute search with UnifiedFileExplorerExecutor
            result = self.executor.execute_search(
                directory=directory,
                filename_pattern=filename_pattern,
                content_query=content_query,
                search_options=search_options,  # Pass as dict
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters,
                conditions=conditions
            )
            
            # ============================================================================
            # SEARCH MODE: Populate ResultsTree (v2.9.117 - B.2)
            # ============================================================================
            # Switch to tree view
            self.results_stack.setCurrentIndex(0)
            
            # Build matches dictionary for ResultsTree
            matches_dict = {}
            for search_result in result.get('files', []):
                file_info = search_result.file_info
                file_path = file_info.path
                
                if search_result.matches:
                    # Content search: show matches
                    matches_list = []
                    for match in search_result.matches:
                        snippet = match.snippet if hasattr(match, 'snippet') else ""
                        matches_list.append((match.line, match.column, snippet))
                    matches_dict[file_path] = matches_list
                else:
                    # Filename search: show file with line 1
                    matches_dict[file_path] = [(1, 0, f"📄 {file_info.name}")]
            
            # Populate ResultsTree
            self.results_tree.populate(matches_dict, sort_results=True)
            
            # Update statistics (v2.9.117 - B.4)
            files_list = result.get('files', [])
            self._update_statistics(files_list, time.time() - start_time)
            
        else:
            # ============================================================================
            # BROWSE MODE: Populate FileListTable (v2.9.117 - B.2)
            # ============================================================================
            # Switch to table view
            self.results_stack.setCurrentIndex(1)
            # Execute browse with UnifiedFileExplorerExecutor
            result = self.executor.execute_browse(
                directory=directory,
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters
            )
            
            # Process SearchResult objects (browse returns SearchResult with empty matches)
            files_data = []
            for search_result in result.get('files', []):
                # Access file_info from SearchResult
                file_info = search_result.file_info
                
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
            
            # Enable multi-selection if in selection mode
            if self.dialog_mode and hasattr(self, 'chk_selection_mode') and self.chk_selection_mode.isChecked():
                self.table_manager.table.setSelectionMode(QAbstractItemView.MultiSelection)
            else:
                self.table_manager.table.setSelectionMode(QAbstractItemView.SingleSelection)
            
            # Populate table
            self.table_manager.populate(files_data, human_readable=human_readable)
            
            # Update statistics (v2.9.117 - B.4)
            files_list = result.get('files', [])
            self._update_statistics(files_list, time.time() - start_time)
        
        # Show errors if any
        if result.get('errors'):
            error_msg = "\n".join(result['errors'][:5])  # Show first 5 errors
            if len(result['errors']) > 5:
                error_msg += f"\n... and {len(result['errors']) - 5} more errors"
            QMessageBox.warning(self, "Errors Encountered", error_msg)
        
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
    
    def _update_statistics(self, files_list: List, elapsed_time: float):
        """
        Update statistics panel with file counts, size, and execution time (v2.9.117 - B.4).
        
        Args:
            files_list: List of SearchResult objects
            elapsed_time: Execution time in seconds
        """
        file_count = 0
        dir_count = 0
        total_size = 0
        
        for search_result in files_list:
            file_info = search_result.file_info
            if file_info.is_dir:
                dir_count += 1
            else:
                file_count += 1
                total_size += file_info.size
        
        # Update labels
        self.lbl_files_count.setText(f"📄 Files: {file_count:,}")
        self.lbl_dirs_count.setText(f"📁 Dirs: {dir_count:,}")
        self.lbl_total_size.setText(f"💾 Size: {self._format_size_human(total_size)}")
        self.lbl_exec_time.setText(f"⏱️ Time: {elapsed_time:.2f}s")
    
    def _format_size_human(self, size: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _export_results_csv(self):
        """
        Export current results to CSV (v2.9.117 - B.5).
        Works for both browse mode (table) and search mode (tree).
        """
        current_index = self.results_stack.currentIndex()
        
        if current_index == 1:
            # Browse mode: Use FileListTableManager's export method
            self.table_manager.export_csv()
        else:
            # Search mode: Export ResultsTree matches to CSV
            self._export_tree_to_csv()
    
    def _export_tree_to_csv(self):
        """Export ResultsTree matches to CSV file (v2.9.117 - B.5)."""
        matches_data = self.results_tree.get_matches_data()
        
        if not matches_data:
            QMessageBox.information(self, "No Data", "No search results to export.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Search Results",
            "search_results.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(["File", "Line", "Column", "Match"])
                
                # Data: Iterate through files and matches
                for file_path, matches in matches_data.items():
                    for line, col, snippet in matches:
                        writer.writerow([file_path, line, col, snippet.strip()])
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Search results exported to:\n{filepath}\n\n"
                f"Total: {sum(len(m) for m in matches_data.values())} matches in {len(matches_data)} files"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export: {e}")
    
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
    
    # ============================================================================
    # New Signal Handlers (v2.9.116 Integration)
    # ============================================================================
    
    def _on_search_params_changed(self):
        """Handle search parameter changes (v2.9.116)."""
        # Debounce: restart timer on each change (500ms delay)
        if self.auto_search_timer.isActive():
            self.auto_search_timer.stop()
        
        # Only auto-search if directory is set
        if self.ed_directory.text().strip():
            self.auto_search_timer.start(500)  # 500ms debounce
    
    def _trigger_auto_search(self):
        """Execute auto-search after debounce delay."""
        filename_pattern = self.filename_panel.get_pattern()
        content_query = self.content_panel.get_query()
        
        # Only auto-search if there's actually a query
        if filename_pattern or content_query:
            self._list_files()
    
    def _on_replace_first(self):
        """Handle replace first occurrence (v2.9.116)."""
        query = self.content_panel.get_query()
        replacement = self.replace_panel.get_replacement()
        
        if not query:
            QMessageBox.warning(self, "No Query", "Please enter search text.")
            return
        
        # Get selected files from table
        selected_rows = set(item.row() for item in self.table_manager.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one file.")
            return
        
        # Collect file paths and create SearchResult objects
        from src.core.file_list_executor import FileInfo
        from src.core.file_explorer_executor import SearchResult
        
        search_results = []
        for row in sorted(selected_rows):
            path_item = self.table_manager.table.item(row, 4)  # Column 4 is path
            if path_item:
                file_path = path_item.text()
                # Create minimal FileInfo
                file_info = FileInfo(
                    name=os.path.basename(file_path),
                    path=file_path,
                    size=0,
                    mtime="",
                    permissions="",
                    owner="",
                    group="",
                    is_dir=False
                )
                # Create SearchResult with empty matches (will be found during replace)
                search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))
        
        # Get search options
        search_options = self.search_options_panel.get_options()
        
        # Execute replace first
        result = self.executor.execute_replace(
            files=search_results,
            search_query=query,
            replacement=replacement,
            search_options=search_options,
            replace_all=False  # Replace first only
        )
        
        # Show result
        if result.get('success'):
            files_modified = result.get('files_modified', 0)
            replacements_made = result.get('replacements_made', 0)
            QMessageBox.information(
                self, 
                "Replace Complete", 
                f"Modified {files_modified} file(s)\n{replacements_made} replacement(s) made"
            )
            
            # Refresh file list to show updated sizes/times
            self._list_files()
        else:
            error = result.get('error', 'Unknown error')
            QMessageBox.warning(self, "Replace Failed", f"Error: {error}")
    
    def _on_replace_all(self):
        """Handle replace all occurrences (v2.9.116)."""
        query = self.content_panel.get_query()
        replacement = self.replace_panel.get_replacement()
        
        if not query:
            QMessageBox.warning(self, "No Query", "Please enter search text.")
            return
        
        # Get selected files from table
        selected_rows = set(item.row() for item in self.table_manager.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one file.")
            return
        
        # Collect file paths and create SearchResult objects
        from src.core.file_list_executor import FileInfo
        from src.core.file_explorer_executor import SearchResult
        
        search_results = []
        for row in sorted(selected_rows):
            path_item = self.table_manager.table.item(row, 4)  # Column 4 is path
            if path_item:
                file_path = path_item.text()
                # Create minimal FileInfo
                file_info = FileInfo(
                    name=os.path.basename(file_path),
                    path=file_path,
                    size=0,
                    mtime="",
                    permissions="",
                    owner="",
                    group="",
                    is_dir=False
                )
                # Create SearchResult
                search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Confirm Replace All",
            f"Replace all occurrences in {len(search_results)} file(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Get search options
        search_options = self.search_options_panel.get_options()
        
        # Execute replace all
        result = self.executor.execute_replace(
            files=search_results,
            search_query=query,
            replacement=replacement,
            search_options=search_options,
            replace_all=True  # Replace all occurrences
        )
        
        # Show result
        if result.get('success'):
            files_modified = result.get('files_modified', 0)
            replacements_made = result.get('replacements_made', 0)
            QMessageBox.information(
                self, 
                "Replace Complete", 
                f"Modified {files_modified} file(s)\n{replacements_made} replacement(s) made"
            )
            
            # Refresh file list to show updated sizes/times
            self._list_files()
        else:
            error = result.get('error', 'Unknown error')
            QMessageBox.warning(self, "Replace Failed", f"Error: {error}")
    
    def _on_conditions_changed(self, conditions: list):
        """Handle advanced conditions changes."""
        # Could auto-filter results when conditions change
        pass
    
    def _on_progress(self, message: str):
        """Handle progress updates from executor (v2.9.116)."""
        # Show progress dialog if not already visible
        if not self.progress_dialog:
            self.progress_dialog = QProgressDialog(
                "Processing...", "Cancel", 0, 100, self
            )
            self.progress_dialog.setWindowTitle("File Explorer")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.canceled.connect(self.executor.cancel)
        
        # Update message
        self.progress_dialog.setLabelText(message)
    
    def _on_progress_detailed(self, current: int, total: int, message: str):
        """Handle detailed progress updates (v2.9.116)."""
        if self.progress_dialog:
            # Calculate percentage
            percentage = int((current / total) * 100) if total > 0 else 0
            self.progress_dialog.setValue(percentage)
            self.progress_dialog.setLabelText(f"{message}\n({current}/{total})")
    
    def _on_execution_done(self, results: dict):
        """Handle execution completion (v2.9.116)."""
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Results are already processed by _list_files() method
        # This is just for cleanup and optional status updates
        files_count = len(results.get('files', []))
        stats = results.get('stats', {})
        total_size = stats.get('total_size', 0)
        
        # Update status bar or show completion message (optional)
        # For now, just close the progress dialog
    
    def _on_execution_error(self, error: str):
        """Handle execution errors."""
        QMessageBox.warning(self, "Error", error)


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
