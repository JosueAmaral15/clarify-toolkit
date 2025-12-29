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
import re
import time
import csv
from datetime import datetime
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QMenu,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QAbstractItemView,
    QGroupBox,
    QProgressDialog,
    QSplitter,
    QScrollArea,
    QStackedWidget,
    QFrame,
)
from PySide6.QtCore import Qt, QSettings, QDate, QTimer, QObject, QEvent
from PySide6.QtGui import QAction, QShortcut, QKeySequence
from .base_dock import BaseDock
from .widgets import (
    FileFilterPanel,
    PresetManager,
    FileListTableManager,
    FileNameQueryPanel,
    ContentQueryPanel,
    SearchOptionsPanel,
    ReplacePanel,
    ConditionsGrid,
    CollapsibleSection,
)
from .panels import ResultsTree
from src.core import FileListExecutor, FileInfo, ListResult
from src.core.file_explorer_executor import UnifiedFileExplorerExecutor, SearchResult, SearchMatch
from src.i18n.translator import tooltip_tr, tr
from src.utils.logger import get_logger

# Initialize logger for structured logging (Protocolo Simplicidade 3 - Etapa 6)
logger = get_logger(__name__)


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

        # Always initialize as BaseDock (QDockWidget)
        # Dialog mode only adds OK/Cancel buttons, doesn't change widget type
        super().__init__("File Explorer", parent)
        
        # Connect to language change signal for dynamic translation update
        from src.i18n.translator import get_translator
        get_translator().languageChanged.connect(self.retranslateUi)

    def _setup_ui(self):
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()

    def _create_widgets(self):
        """Create UI widgets."""
        # ============================================================================
        # SECTION 1: Directory & Type (📁 - Collapsible)
        # ============================================================================
        self.section_directory = CollapsibleSection(tr("file_list.section_directory"))
        self.section_directory.setCollapsed(False)  # Start expanded

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
        self.chk_all.setChecked(getattr(self, "chk_all_state", False))

        self.chk_long = QCheckBox(tr("file_list.chk_long"))
        self.chk_long.setChecked(getattr(self, "chk_long_state", True))

        self.chk_human = QCheckBox(tr("file_list.chk_human"))
        self.chk_human.setChecked(getattr(self, "chk_human_state", True))

        self.chk_recursive = QCheckBox(tr("file_list.chk_recursive"))
        self.chk_recursive.setChecked(getattr(self, "chk_recursive_state", False))

        # Sort results checkbox (from Search/Replace)
        self.chk_sort_results = QCheckBox(tr("file_list.chk_sort_results"))
        self.chk_sort_results.setChecked(False)
        self.chk_sort_results.setToolTip(tr("file_list.tooltip_sort_results"))

        # Extension filter (from Search/Replace) - CRITICAL FEATURE
        self.chk_use_ext_filter = QCheckBox(tr("file_list.chk_use_ext_filter"))
        self.chk_use_ext_filter.setChecked(True)
        self.chk_use_ext_filter.setToolTip(tr("file_list.tooltip_use_ext_filter"))

        self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
        self.ed_extensions.setPlaceholderText(tr("file_list.placeholder_extensions"))
        self.ed_extensions.setToolTip(tr("file_list.tooltip_extensions"))

        # Include/Exclude globs (from Search/Replace) - CRITICAL FEATURE
        self.ed_inc = QLineEdit()
        self.ed_inc.setPlaceholderText(tr("file_list.placeholder_include_globs"))
        self.ed_inc.setToolTip(tr("file_list.tooltip_include_globs"))

        self.ed_exc = QLineEdit("node_modules;dist;build;.git")
        self.ed_exc.setToolTip(tr("file_list.tooltip_exclude_globs"))

        # File type filter
        self.lbl_type = QLabel(tr("file_list.lbl_type"))
        self.combo_type = QComboBox()
        self.combo_type.addItems([tr("file_list.type_any"), tr("file_list.type_files_only"), tr("file_list.type_directories_only")])
        self.combo_type.setToolTip(tr("file_list.tooltip_type"))

        # Selection mode (dialog only)
        if self.dialog_mode:
            self.chk_selection_mode = QCheckBox(tr("file_list.chk_selection_mode"))
            self.chk_selection_mode.setChecked(True)
            self.chk_selection_mode.setToolTip(tr("file_list.tooltip_selection_mode"))

        # ============================================================================
        # SECTION 2: Search & Replace (🔍 - Collapsible)
        # ============================================================================
        self.section_search = CollapsibleSection(tr("file_list.section_search"))
        self.section_search.setCollapsed(False)  # Start expanded

        # NEW: Integrated search widgets (v2.9.116)
        self.filename_panel = FileNameQueryPanel()
        self.content_panel = ContentQueryPanel()
        self.search_options_panel = SearchOptionsPanel()
        self.replace_panel = ReplacePanel()

        # Connect search widget signals (only for Replace operations, not auto-search)
        # Auto-search DISABLED: search only happens when user clicks Browse/Search button
        self.replace_panel.replace_first_requested.connect(self._on_replace_first)
        self.replace_panel.replace_all_requested.connect(self._on_replace_all)

        # ============================================================================
        # SECTION 3: Filters (⚙️ - Collapsible with Animation - v2.9.117 B.6)
        # ============================================================================
        self.section_filters = CollapsibleSection(tr("file_list.section_filters"))
        self.section_filters.setCollapsed(True)  # Start collapsed

        # Advanced Filters Panel (extracted component)
        self.filter_panel = FileFilterPanel()
        self.section_filters.setContent(self.filter_panel)

        # ============================================================================
        # SECTION 4: Advanced Conditions (🎯 - Collapsible with Animation - v2.9.117 B.6)
        # ============================================================================
        self.section_conditions = CollapsibleSection(tr("file_list.section_conditions"))
        self.section_conditions.setCollapsed(True)  # Start collapsed

        # NEW: Conditions grid with AND/OR logic (v2.9.116)
        self.conditions_grid = ConditionsGrid()
        self.conditions_grid.conditions_changed.connect(self._on_conditions_changed)
        self.section_conditions.setContent(self.conditions_grid)

        # ============================================================================
        # SECTION 5: Presets (💾 - Collapsible with Animation, Dock Mode Only - v2.9.117 B.6)
        # ============================================================================
        if not self.dialog_mode:
            self.section_presets = CollapsibleSection(tr("file_list.section_presets"))
            self.section_presets.setCollapsed(True)  # Start collapsed

            # Preset Manager (extracted component)
            self.preset_manager = PresetManager(settings_group="FileExplorerDock")
            self.preset_manager.set_callbacks(
                get_filters=self._get_current_filters, apply_filters=self._apply_filters_to_widgets
            )

        # ============================================================================
        # Action Buttons (v2.9.117 - B.7: Unified Browse/Search)
        # ============================================================================
        self.btn_list = QPushButton(tr("file_list.btn_list"))
        self.btn_list.setToolTip(tr("file_list.tooltip_btn_list"))
        self.btn_list.clicked.connect(self._list_files_smart)
        self.btn_list.setObjectName("btn_list")  # For theme styling

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
            self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
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
        # Action button tooltip (v2.9.117 - B.7: Unified)
        self.btn_list.setToolTip(tooltip_tr("file_list.btn_list"))
    
    def retranslateUi(self):
        """Retranslate all UI elements when language changes (v2.9.117 - B.7)."""
        # Update window title
        self.setWindowTitle(tr("file_list.title"))
        
        # Update button text
        self.btn_list.setText(tr("file_list.btn_list"))
        
        # Update section titles
        self.section_directory.setTitle(tr("file_list.section_directory"))
        self.section_search.setTitle(tr("file_list.section_search"))
        self.section_filters.setTitle(tr("file_list.section_filters"))
        self.section_conditions.setTitle(tr("file_list.section_conditions"))
        if hasattr(self, 'section_presets'):
            self.section_presets.setTitle(tr("file_list.section_presets"))
        
        # Update checkboxes
        self.chk_sort_results.setText(tr("file_list.chk_sort_results"))
        self.chk_use_ext_filter.setText(tr("file_list.chk_use_ext_filter"))
        self.chk_word_wrap.setText(tr("file_list.chk_word_wrap"))
        if hasattr(self, 'chk_selection_mode'):
            self.chk_selection_mode.setText(tr("file_list.chk_selection_mode"))
        
        # Update labels
        self.lbl_type.setText(tr("file_list.lbl_type"))
        
        # Update ComboBox items
        current_index = self.combo_type.currentIndex()
        self.combo_type.clear()
        self.combo_type.addItems([
            tr("file_list.type_any"),
            tr("file_list.type_files_only"),
            tr("file_list.type_directories_only")
        ])
        self.combo_type.setCurrentIndex(current_index)
        
        # Update placeholders
        self.ed_extensions.setPlaceholderText(tr("file_list.placeholder_extensions"))
        self.ed_inc.setPlaceholderText(tr("file_list.placeholder_include_globs"))
        
        # Update tooltips
        self._apply_tooltips()

        # Search & Replace section
        self.section_search.setToolTip(tr("file_list.tooltip_section_search"))
        self.filename_panel.setToolTip(tr("file_explorer.tooltip_filename_panel"))
        self.content_panel.setToolTip(tr("file_explorer.tooltip_content_panel"))
        self.search_options_panel.setToolTip(tr("file_explorer.tooltip_search_options"))
        self.replace_panel.setToolTip(tr("file_explorer.tooltip_replace_panel"))

        # Filters section
        self.section_filters.setToolTip(tr("file_list.tooltip_section_filters"))

        # Conditions section
        self.section_conditions.setToolTip(tr("file_list.tooltip_section_conditions"))

        # Presets section (if visible)
        if hasattr(self, "section_presets"):
            self.section_presets.setToolTip(tr("file_explorer.tooltip_presets"))

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

        # Options row 2: Sort results checkbox
        opts2_layout = QHBoxLayout()
        opts2_layout.addWidget(self.chk_sort_results)
        opts2_layout.addStretch()
        section1_layout.addLayout(opts2_layout)

        # Options row 3: Extension filter (from Search/Replace)
        ext_row = QHBoxLayout()
        ext_row.addWidget(self.chk_use_ext_filter)
        ext_row.addWidget(QLabel(tr("file_list.lbl_extensions")))
        ext_row.addWidget(self.ed_extensions)
        ext_row.addStretch()
        section1_layout.addLayout(ext_row)

        # Options row 4: Include globs (from Search/Replace)
        inc_row = QHBoxLayout()
        inc_row.addWidget(QLabel(tr("file_list.lbl_include_globs")))
        section1_layout.addLayout(inc_row)
        section1_layout.addWidget(self.ed_inc)

        # Options row 5: Exclude globs (from Search/Replace)
        exc_row = QHBoxLayout()
        exc_row.addWidget(QLabel(tr("file_list.lbl_exclude_globs")))
        section1_layout.addLayout(exc_row)
        section1_layout.addWidget(self.ed_exc)

        # Options row 6: Type filter + Selection mode
        opts3_layout = QHBoxLayout()
        opts3_layout.addWidget(self.lbl_type)
        opts3_layout.addWidget(self.combo_type)
        if self.dialog_mode:
            opts3_layout.addWidget(self.chk_selection_mode)
        opts3_layout.addStretch()
        section1_layout.addLayout(opts3_layout)

        # Wrap in widget for CollapsibleSection
        section1_widget = QWidget()
        section1_widget.setLayout(section1_layout)
        self.section_directory.setContent(section1_widget)
        left_layout.addWidget(self.section_directory)

        # ----------------------------------------------------------------------------
        # SECTION 2: Search & Replace
        # ----------------------------------------------------------------------------
        section2_layout = QVBoxLayout()
        section2_layout.addWidget(self.filename_panel)
        section2_layout.addWidget(self.content_panel)
        section2_layout.addWidget(self.search_options_panel)
        section2_layout.addWidget(self.replace_panel)

        # Wrap in widget for CollapsibleSection
        section2_widget = QWidget()
        section2_widget.setLayout(section2_layout)
        self.section_search.setContent(section2_widget)
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
        # Action Button (v2.9.117 - B.7: Unified Browse/Search)
        # ----------------------------------------------------------------------------
        left_layout.addWidget(self.btn_list)
        left_layout.addStretch()  # Push everything to top

        # Wrap left panel in scroll area
        left_scroll = QScrollArea()
        left_scroll.setWidget(left_panel)
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # ============================================================================
        # RIGHT PANEL: Results with QStackedWidget (v2.9.117 - B.2)
        # ============================================================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # ============================================================================
        # CONTROLS ROW: View toggle + Word wrap (always visible - v2.9.118)
        # ============================================================================
        controls_row = QWidget()
        controls_layout = QHBoxLayout(controls_row)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # View toggle: Tree vs Table (v2.9.118)
        view_label = QLabel(tr("file_list.lbl_view"))
        controls_layout.addWidget(view_label)
        
        self.combo_view_mode = QComboBox()
        self.combo_view_mode.addItem(tr("file_list.view_tree"), 0)  # Index 0 in stacked widget
        self.combo_view_mode.addItem(tr("file_list.view_table"), 1)   # Index 1 in stacked widget
        self.combo_view_mode.setToolTip(tr("file_list.tooltip_view_mode"))
        self.combo_view_mode.currentIndexChanged.connect(self._switch_view_mode)
        controls_layout.addWidget(self.combo_view_mode)
        
        controls_layout.addSpacing(16)
        
        # Word wrap control checkbox (only for Tree view)
        self.chk_word_wrap = QCheckBox(tr("file_list.chk_word_wrap"))
        self.chk_word_wrap.setChecked(False)  # Default: scroll mode
        self.chk_word_wrap.setToolTip(tr("file_list.tooltip_word_wrap"))
        self.chk_word_wrap.toggled.connect(self._toggle_word_wrap)
        controls_layout.addWidget(self.chk_word_wrap)
        
        controls_layout.addStretch()
        
        # Add controls to right panel (before stacked widget)
        right_layout.addWidget(controls_row)

        # Create ResultsTree container (just the tree, no controls)
        results_tree_container = QWidget()
        results_tree_layout = QVBoxLayout(results_tree_container)
        results_tree_layout.setContentsMargins(0, 0, 0, 0)
        results_tree_layout.setSpacing(0)
        
        self.results_tree = ResultsTree()
        results_tree_layout.addWidget(self.results_tree)

        # Create status bar for position info (from Search/Replace)
        self.results_status = QLabel("")
        self.results_status.setObjectName("results_status")
        self.results_status.setMinimumHeight(25)

        # Connect status label to results tree
        self.results_tree.set_status_label(self.results_status)

        # Create QStackedWidget to switch between browse/search views
        self.results_stack = QStackedWidget()
        self.results_stack.addWidget(results_tree_container)  # Index 0: Search mode (tree)
        self.results_stack.addWidget(self.table_manager)  # Index 1: Browse mode (table)

        # Start in table mode (browse view)
        self.results_stack.setCurrentIndex(1)
        self.combo_view_mode.setCurrentIndex(1)  # Sync combo to table view

        # Add results stack to right panel
        right_layout.addWidget(self.results_stack)

        # Add status bar below results
        right_layout.addWidget(self.results_status)

        # ============================================================================
        # STATISTICS PANEL (v2.9.117 - B.4)
        # ============================================================================
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_frame.setObjectName("stats_frame")  # For theme styling

        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(8, 8, 8, 8)
        stats_layout.setSpacing(16)

        # Files count
        self.lbl_files_count = QLabel(tr("file_list.stats_files_init"))
        self.lbl_files_count.setObjectName("stats_label")
        stats_layout.addWidget(self.lbl_files_count)

        # Directories count
        self.lbl_dirs_count = QLabel(tr("file_list.stats_dirs_init"))
        self.lbl_dirs_count.setObjectName("stats_label")
        stats_layout.addWidget(self.lbl_dirs_count)

        # Total size
        self.lbl_total_size = QLabel(tr("file_list.stats_size_init"))
        self.lbl_total_size.setObjectName("stats_label")
        stats_layout.addWidget(self.lbl_total_size)

        # Execution time
        self.lbl_exec_time = QLabel(tr("file_list.stats_time_init"))
        self.lbl_exec_time.setObjectName("stats_label")
        stats_layout.addWidget(self.lbl_exec_time)

        stats_layout.addStretch()

        # Save Results button (from Search/Replace)
        self.btn_save_results = QPushButton(tr("file_list.btn_save_results"))
        self.btn_save_results.setToolTip(tr("file_list.tooltip_save_results"))
        self.btn_save_results.clicked.connect(self._save_results)
        self.btn_save_results.setObjectName("btn_save")  # For theme styling
        stats_layout.addWidget(self.btn_save_results)

        # Export CSV button (v2.9.117 - B.5)
        self.btn_export_csv = QPushButton(tr("file_list.btn_export_csv"))
        self.btn_export_csv.setToolTip(tr("file_list.tooltip_export_csv"))
        self.btn_export_csv.clicked.connect(self._export_results_csv)
        self.btn_export_csv.setObjectName("btn_export")  # For theme styling
        stats_layout.addWidget(self.btn_export_csv)

        # Add stats frame to right panel
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
        # HOVER EXPANSION DISABLED (user request - Dec 26, 2024)
        # ============================================================================
        # Hover expansion removed as it was distracting for users

        # Add splitter to main layout
        self.layout.addWidget(self.splitter)

        # ============================================================================
        # KEYBOARD SHORTCUTS (v2.9.118)
        # ============================================================================
        # ENTER: Execute Browse/Search command
        # Context: WidgetWithChildrenShortcut ensures shortcut only works when
        # File Explorer dock or its children have focus, avoiding conflicts with other tools
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut_enter.activated.connect(self._list_files_smart)
        
        # Also support Enter on numpad
        self.shortcut_enter_numpad = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.shortcut_enter_numpad.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.shortcut_enter_numpad.activated.connect(self._list_files_smart)

        # ============================================================================
        # Dialog Buttons (Dialog Mode Only)
        # ============================================================================
        if self.dialog_mode:
            self.layout.addWidget(self.button_box)

    def _browse_directory(self):
        """Browse for directory."""
        directory = QFileDialog.getExistingDirectory(
            self, tr("file_list.dialog_select_directory"), self.ed_directory.text() or os.getcwd(), QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.ed_directory.setText(directory)
    
    def _toggle_word_wrap(self, enabled: bool):
        """Toggle word wrap mode in results tree (v2.9.117)."""
        self.results_tree.set_word_wrap(enabled)
    
    def _switch_view_mode(self, index: int):
        """Switch between Tree and Table view manually (v2.9.118)."""
        view_index = self.combo_view_mode.itemData(index)
        self.results_stack.setCurrentIndex(view_index)
        
        # Enable/disable word wrap checkbox based on view
        # Word wrap only applies to Tree view
        is_tree_view = (view_index == 0)
        self.chk_word_wrap.setEnabled(is_tree_view)

    def _list_files_smart(self):
        """Smart file operation: auto-detect Browse or Search mode (v2.9.117 - B.7).
        
        Behavior:
        - If filename pattern OR content query is set: Search mode
        - If both are empty/default: Browse mode (list all files)
        """
        filename_pattern = self.filename_panel.get_pattern()
        content_query = self.content_panel.get_query()
        
        # Auto-detect mode based on filters
        has_search_criteria = bool(filename_pattern) or bool(content_query)
        
        if has_search_criteria:
            # Search mode: user provided filters
            logger.info("Smart mode: SEARCH (filters detected)", extra={
                "filename_pattern": filename_pattern,
                "content_query": bool(content_query)
            })
        else:
            # Browse mode: no filters, list all files
            logger.info("Smart mode: BROWSE (no filters)")
        
        # Execute unified operation (executor will handle both modes)
        self._list_files()

    def _list_files(self):
        """List or search files with unified executor (v2.9.116)."""
        # Start timer (v2.9.117 - B.4)
        start_time = time.time()

        directory = self.ed_directory.text().strip()

        if not directory:
            logger.warning("Empty directory path provided")
            QMessageBox.warning(self, tr("file_list.error_missing_title"), tr("file_list.error_missing_directory"))
            return

        # SECURITY OWASP A01: Path Traversal Prevention (CWE-22)
        # Normalize and validate directory path
        try:
            directory = os.path.abspath(directory)
        except (OSError, ValueError) as e:
            logger.error(f"Invalid directory path: {directory}", exc_info=True)
            QMessageBox.warning(self, tr("file_list.error_invalid_title"), tr("file_list.error_invalid_path").format(str(e)))
            return

        if not os.path.isdir(directory):
            logger.error(f"Directory does not exist: {directory}")
            QMessageBox.warning(self, tr("file_list.error_invalid_title"), tr("file_list.error_not_exist").format(directory))
            return

        if not os.access(directory, os.R_OK):
            logger.error(f"Permission denied for directory: {directory}")
            QMessageBox.warning(self, tr("file_list.error_permission_title"), tr("file_list.error_no_permission").format(directory))
            return

        logger.info(
            "Starting file explorer operation",
            extra={"directory": directory, "recursive": self.chk_recursive.isChecked()},
        )

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
            filters["type"] = "files"
        elif type_filter == "Directories Only":
            filters["type"] = "dirs"
        else:
            filters["type"] = "any"

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
            logger.info(
                f"Executing search operation",
                extra={
                    "filename_pattern": filename_pattern,
                    "content_query": content_query[:50] if content_query else None,
                    "recursive": recursive,
                    "case_sensitive": search_options.get("case_sensitive", False),
                },
            )
            # Execute search with UnifiedFileExplorerExecutor
            result = self.executor.execute_search(
                directory=directory,
                filename_pattern=filename_pattern,
                content_query=content_query,
                search_options=search_options,  # Pass as dict
                show_hidden=show_hidden,
                recursive=recursive,
                filters=filters,
                conditions=conditions,
            )

            # ============================================================================
            # SEARCH MODE: Populate ResultsTree (v2.9.117 - B.2)
            # ============================================================================
            # Switch to tree view (but respect manual override)
            # Only auto-switch if user hasn't manually selected a view
            if self.combo_view_mode.currentIndex() != 0:
                self.results_stack.setCurrentIndex(0)
                self.combo_view_mode.setCurrentIndex(0)  # Sync combo

            # Build matches dictionary for ResultsTree
            matches_dict = {}
            for search_result in result.get("files", []):
                file_info = search_result.file_info
                file_path = file_info.path

                if search_result.matches:
                    # Content search: show matches
                    matches_list = []
                    for match in search_result.matches:
                        snippet = match.snippet if hasattr(match, "snippet") else ""
                        matches_list.append((match.line, match.col, snippet))
                    matches_dict[file_path] = matches_list
                else:
                    # Filename search: show file with line 1
                    matches_dict[file_path] = [(1, 0, f"📄 {file_info.name}")]

            # Populate ResultsTree with sort option from checkbox
            sort_results = self.chk_sort_results.isChecked()
            self.results_tree.populate(matches_dict, sort_results=sort_results)

            # Update statistics (v2.9.117 - B.4)
            files_list = result.get("files", [])
            self._update_statistics(files_list, time.time() - start_time)

            # Save to history (History Integration from Search/Replace)
            try:
                from src.gui.progress import OperationHistory

                history = OperationHistory()

                total_matches = sum(len(items) for items in matches_dict.values())

                history.add_operation(
                    "file_explorer_search",
                    {
                        "directory": directory,
                        "filename_pattern": filename_pattern,
                        "content_query": content_query,
                        "files_matched": len(matches_dict),
                        "total_matches": total_matches,
                        "case_sensitive": self.search_options_panel.get_options().get("case_sensitive", False),
                        "whole_word": self.search_options_panel.get_options().get("whole_word", False),
                        "regex": self.search_options_panel.get_options().get("regex", False),
                    },
                )

                # Add to History Dock if available
                if hasattr(self, "dock_history"):
                    self.dock_history.add_operation(
                        "File Explorer Search",
                        {
                            "directory": directory,
                            "pattern": filename_pattern or content_query,
                            "files_found": len(matches_dict),
                            "matches_found": total_matches,
                        },
                    )
            except Exception as e:
                print(f"Failed to save history: {e}")

        else:
            # ============================================================================
            # BROWSE MODE: Populate FileListTable (v2.9.117 - B.2)
            # ============================================================================
            logger.info(f"Executing browse operation", extra={"recursive": recursive, "show_hidden": show_hidden})
            # Switch to table view (but respect manual override)
            # Only auto-switch if user hasn't manually selected a view
            if self.combo_view_mode.currentIndex() != 1:
                self.results_stack.setCurrentIndex(1)
                self.combo_view_mode.setCurrentIndex(1)  # Sync combo
            # Execute browse with UnifiedFileExplorerExecutor
            result = self.executor.execute_browse(
                directory=directory, show_hidden=show_hidden, recursive=recursive, filters=filters
            )

            # Process SearchResult objects (browse returns SearchResult with empty matches)
            files_data = []
            for search_result in result.get("files", []):
                # Access file_info from SearchResult
                file_info = search_result.file_info

                # Format permissions
                perms = file_info.permissions
                if long_format:
                    perms = f"{perms} {file_info.owner}:{file_info.group}"

                files_data.append(
                    {
                        "name": file_info.name,
                        "size": file_info.size,
                        "mtime": file_info.mtime,
                        "permissions": perms,
                        "path": file_info.path,
                        "is_dir": file_info.is_dir,
                    }
                )

            # Sort alphabetically if checkbox is enabled
            if self.chk_sort_results.isChecked():
                files_data.sort(key=lambda x: x['path'].lower())

            # Enable multi-selection if in selection mode
            if self.dialog_mode and hasattr(self, "chk_selection_mode") and self.chk_selection_mode.isChecked():
                self.table_manager.table.setSelectionMode(QAbstractItemView.MultiSelection)
            else:
                self.table_manager.table.setSelectionMode(QAbstractItemView.SingleSelection)

            # Populate table
            self.table_manager.populate(files_data, human_readable=human_readable)

            # Update statistics (v2.9.117 - B.4)
            files_list = result.get("files", [])
            self._update_statistics(files_list, time.time() - start_time)

            # Save to history (History Integration for browse mode)
            try:
                from src.gui.progress import OperationHistory

                history = OperationHistory()

                history.add_operation(
                    "file_explorer_browse",
                    {
                        "directory": directory,
                        "files_found": len(files_data),
                        "recursive": recursive,
                        "show_hidden": show_hidden,
                    },
                )

                # Add to History Dock if available
                if hasattr(self, "dock_history"):
                    self.dock_history.add_operation(
                        "File Explorer Browse", {"directory": directory, "files_found": len(files_data)}
                    )
            except Exception as e:
                print(f"Failed to save history: {e}")

        # Show errors if any
        if result.get("errors"):
            logger.warning(f"Operation completed with errors", extra={"error_count": len(result["errors"])})
            error_msg = "\n".join(result["errors"][:5])  # Show first 5 errors
            if len(result["errors"]) > 5:
                error_msg += f"\n... and {len(result['errors']) - 5} more errors"
            QMessageBox.warning(self, tr("file_list.errors_title"), error_msg)
        else:
            logger.info(f"Operation completed successfully", extra={"duration": time.time() - start_time})

        # Save preferences after listing
        self._save_preferences()

    def _build_filters(self) -> Dict[str, Any]:
        """Build filter dictionary from filter panel AND extension/glob fields."""
        panel_filters = self.filter_panel.get_filters()

        # Convert to format expected by FileListExecutor
        filters = {}

        # ============================================================================
        # EXTENSION FILTER (from Search/Replace) - IMPLEMENTATION
        # ============================================================================
        use_ext_filter = self.chk_use_ext_filter.isChecked()
        extensions_text = self.ed_extensions.text().strip() if use_ext_filter else ""

        if use_ext_filter and extensions_text:
            # Parse extensions (comma or semicolon separated)
            extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
            # Ensure extensions start with dot
            extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
            filters["extensions"] = extensions

        # ============================================================================
        # INCLUDE/EXCLUDE GLOBS (from Search/Replace) - IMPLEMENTATION
        # ============================================================================
        ed_inc_text = self.ed_inc.text().strip()
        ed_exc_text = self.ed_exc.text().strip()

        # Include globs (advanced patterns)
        if ed_inc_text:
            include_patterns = [p.strip() for p in re.split(r"[;,]", ed_inc_text) if p.strip()]
            filters["include_globs"] = include_patterns

        # Exclude globs (exclude patterns)
        if ed_exc_text:
            exclude_patterns = [p.strip() for p in re.split(r"[;,]", ed_exc_text) if p.strip()]
            filters["exclude_globs"] = exclude_patterns

        # ============================================================================
        # PANEL FILTERS (existing functionality)
        # ============================================================================
        # Regex filter
        if panel_filters.get("regex_enabled") and panel_filters.get("regex_pattern"):
            filters["regex"] = {"enabled": True, "pattern": panel_filters["regex_pattern"]}

        # Size filter (convert to bytes)
        size_config = {}
        if panel_filters.get("size_min"):
            min_val = panel_filters["size_min"]
            min_unit = panel_filters.get("size_min_unit", "B")
            size_config["min"] = min_val * FileFilterPanel.SIZE_UNITS[min_unit]

        if panel_filters.get("size_max"):
            max_val = panel_filters["size_max"]
            max_unit = panel_filters.get("size_max_unit", "B")
            size_config["max"] = max_val * FileFilterPanel.SIZE_UNITS[max_unit]

        if size_config:
            filters["size"] = size_config

        # MTime filter (convert to date objects)
        mtime_config = {}
        if panel_filters.get("mtime_after_enabled") and panel_filters.get("mtime_after"):
            mtime_config["after"] = panel_filters["mtime_after"]

        if panel_filters.get("mtime_before_enabled") and panel_filters.get("mtime_before"):
            mtime_config["before"] = panel_filters["mtime_before"]

        if mtime_config:
            filters["mtime"] = mtime_config

        # Extensions filter from panel (fallback if not using top-level filter)
        if not use_ext_filter and panel_filters.get("extensions"):
            filters["extensions"] = panel_filters["extensions"]

        # Depth filter
        if panel_filters.get("depth", 0) > 0:
            filters["depth"] = panel_filters["depth"]

        # Exclude directories
        exclude_dirs = panel_filters.get("exclude_dirs", [])
        if exclude_dirs:
            filters["exclude_dirs"] = exclude_dirs

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
        self.lbl_files_count.setText(tr("file_list.stats_files").format(f"{file_count:,}"))
        self.lbl_dirs_count.setText(tr("file_list.stats_dirs").format(f"{dir_count:,}"))
        self.lbl_total_size.setText(tr("file_list.stats_size").format(self._format_size_human(total_size)))
        self.lbl_exec_time.setText(tr("file_list.stats_time").format(f"{elapsed_time:.2f}"))

    def _format_size_human(self, size: int) -> str:
        """Format size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
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
            QMessageBox.information(self, tr("file_list.no_data_title"), tr("file_list.no_data_message"))
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            tr("file_list.dialog_export_csv_title"),
            tr("file_list.dialog_export_csv_default"),
            tr("file_list.dialog_export_csv_filter"),
        )

        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    tr("file_list.csv_header_file"),
                    tr("file_list.csv_header_line"),
                    tr("file_list.csv_header_column"),
                    tr("file_list.csv_header_match"),
                ])

                # Data: Iterate through files and matches
                for file_path, matches in matches_data.items():
                    for line, col, snippet in matches:
                        writer.writerow([file_path, line, col, snippet.strip()])

            QMessageBox.information(
                self,
                tr("file_list.export_complete_title"),
                tr("file_list.export_complete_message").format(
                    filepath, sum(len(m) for m in matches_data.values()), len(matches_data)
                ),
            )
        except Exception as e:
            QMessageBox.critical(self, tr("file_list.export_failed_title"), tr("file_list.export_failed_message").format(e))

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
            QMessageBox.information(self, tr("file_list.recent_none_title"), tr("file_list.recent_none_message"))
            return

        menu = QMenu(self)
        for directory in self.recent_dirs:
            action = QAction(directory, self)
            action.triggered.connect(lambda checked, d=directory: self.ed_directory.setText(d))
            menu.addAction(action)

        menu.addSeparator()
        clear_action = QAction(tr("file_list.recent_clear"), self)
        clear_action.triggered.connect(self._clear_recent)
        menu.addAction(clear_action)

        menu.exec(self.btn_recent.mapToGlobal(self.btn_recent.rect().bottomLeft()))

    def _clear_recent(self):
        """Clear recent directories list."""
        self.recent_dirs = []
        self._save_preferences()
        QMessageBox.information(self, tr("file_list.cleared_title"), tr("file_list.cleared_message"))

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
            QMessageBox.warning(self, tr("file_list.no_selection_title"), tr("file_list.no_selection_message"))
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
    # Auto-search Methods (DISABLED - v2.9.117 - B.7)
    # Search now only triggered by clicking Browse/Search button
    # ============================================================================

    # def _on_search_params_changed(self):
    #     """Handle search parameter changes (v2.9.116)."""
    #     # Debounce: restart timer on each change (500ms delay)
    #     if self.auto_search_timer.isActive():
    #         self.auto_search_timer.stop()
    #
    #     # Only auto-search if directory is set
    #     if self.ed_directory.text().strip():
    #         self.auto_search_timer.start(500)  # 500ms debounce
    #
    # def _trigger_auto_search(self):
    #     """Execute auto-search after debounce delay."""
    #     filename_pattern = self.filename_panel.get_pattern()
    #     content_query = self.content_panel.get_query()
    #
    #     # Only auto-search if there's actually a query
    #     if filename_pattern or content_query:
    #         self._list_files()

    def _on_replace_first(self):
        """Handle replace first occurrence (v2.9.116)."""
        query = self.content_panel.get_query()
        replacement = self.replace_panel.get_replacement()

        if not query:
            QMessageBox.warning(self, tr("file_list.no_query_title"), tr("file_list.no_query_message"))
            return

        # Get selected files from table
        selected_rows = set(item.row() for item in self.table_manager.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, tr("file_list.no_selection_title"), tr("file_list.no_selection_message"))
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
                    is_dir=False,
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
            replace_all=False,  # Replace first only
        )

        # Show result
        if result.get("success"):
            files_modified = result.get("files_modified", 0)
            replacements_made = result.get("replacements_made", 0)
            QMessageBox.information(
                self, "Replace Complete", f"Modified {files_modified} file(s)\n{replacements_made} replacement(s) made"
            )

            # Save to history (History Integration for replace operations)
            try:
                from src.gui.progress import OperationHistory

                history = OperationHistory()

                history.add_operation(
                    "file_explorer_replace_first",
                    {
                        "search_query": query,
                        "replacement": replacement,
                        "files_modified": files_modified,
                        "replacements_made": replacements_made,
                    },
                )

                # Add to History Dock if available
                if hasattr(self, "dock_history"):
                    self.dock_history.add_operation(
                        "File Explorer Replace First",
                        {"files_modified": files_modified, "replacements": replacements_made},
                    )
            except Exception as e:
                print(f"Failed to save history: {e}")

            # Refresh file list to show updated sizes/times
            self._list_files()
        else:
            error = result.get("error", "Unknown error")
            QMessageBox.warning(self, tr("file_list.replace_failed_title"), tr("file_list.replace_failed_message").format(error))

    def _on_replace_all(self):
        """Handle replace all occurrences (v2.9.116)."""
        query = self.content_panel.get_query()
        replacement = self.replace_panel.get_replacement()

        if not query:
            QMessageBox.warning(self, tr("file_list.no_query_title"), tr("file_list.no_query_message"))
            return

        # Get selected files from table
        selected_rows = set(item.row() for item in self.table_manager.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, tr("file_list.no_selection_title"), tr("file_list.no_selection_message"))
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
                    is_dir=False,
                )
                # Create SearchResult
                search_results.append(SearchResult(file_info=file_info, matches=[], match_count=0))

        # Confirm with user
        reply = QMessageBox.question(
            self,
            tr("file_list.confirm_replace_title"),
            tr("file_list.confirm_replace_message").format(len(search_results)),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
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
            replace_all=True,  # Replace all occurrences
        )

        # Show result
        if result.get("success"):
            files_modified = result.get("files_modified", 0)
            replacements_made = result.get("replacements_made", 0)
            QMessageBox.information(
                self, "Replace Complete", f"Modified {files_modified} file(s)\n{replacements_made} replacement(s) made"
            )

            # Save to history (History Integration for replace all operations)
            try:
                from src.gui.progress import OperationHistory

                history = OperationHistory()

                history.add_operation(
                    "file_explorer_replace_all",
                    {
                        "search_query": query,
                        "replacement": replacement,
                        "files_modified": files_modified,
                        "replacements_made": replacements_made,
                    },
                )

                # Add to History Dock if available
                if hasattr(self, "dock_history"):
                    self.dock_history.add_operation(
                        "File Explorer Replace All",
                        {"files_modified": files_modified, "replacements": replacements_made},
                    )
            except Exception as e:
                print(f"Failed to save history: {e}")

            # Refresh file list to show updated sizes/times
            self._list_files()
        else:
            error = result.get("error", "Unknown error")
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
                tr("file_list.progress_processing"), tr("file_list.progress_cancel"), 0, 100, self
            )
            self.progress_dialog.setWindowTitle(tr("file_list.progress_title"))
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
        files_count = len(results.get("files", []))
        stats = results.get("stats", {})
        total_size = stats.get("total_size", 0)

        # Update status bar or show completion message (optional)
        # For now, just close the progress dialog

    def _on_execution_error(self, error: str):
        """Handle execution errors."""
        QMessageBox.warning(self, tr("file_list.error_title"), error)

    def _save_results(self):
        """Save search results to a text file (from Search/Replace)."""
        # Get matches data from ResultsTree
        matches_data = self.results_tree.get_matches_data()

        if not matches_data:
            QMessageBox.information(self, tr("file_explorer.msg_no_results_title"), tr("file_explorer.msg_no_results"))
            return

        # Ask user for file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            tr("file_list.dialog_save_results_title"),
            tr("file_list.dialog_save_results_default"),
            tr("file_list.dialog_save_results_filter"),
        )

        if not file_path:
            return  # User cancelled

        try:
            # Export matches to text
            text_content = self.results_tree.export_to_text()

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            total_files = len(matches_data)
            total_matches = sum(len(items) for items in matches_data.values())

            QMessageBox.information(
                self,
                tr("file_list.results_saved_title"),
                tr("file_list.results_saved_message").format(file_path, total_files, total_matches),
            )

        except Exception as e:
            QMessageBox.critical(self, tr("file_list.error_title"), tr("file_list.error_save_failed").format(str(e)))


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
