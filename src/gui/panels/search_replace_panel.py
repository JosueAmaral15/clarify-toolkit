#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Search/Replace Panel Module
----------------------------
Provides the main search and replace interface panel for Clarify.

This module contains the SearchReplacePanel class which implements:
  - File/directory path selection and browsing
  - Extension filtering and glob patterns (include/exclude)
  - Advanced search with case sensitivity, whole word, and regex support
  - Multi-line query support with separate file name and content queries
  - Replace operations (single/all) with preserve case option
  - Advanced conditional filtering (filename, path, ext, size, mtime, content)
  - Dynamic condition rows with AND/OR logic operators
  - Integrated progress tracking and cancellation
  - Results display with save to file capability
  - Search history tracking

Author: Josué Amaral
Date: 2025
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern
# pylint: disable=too-many-instance-attributes  # Complex UI panel
# pylint: disable=too-many-public-methods  # UI event handlers
# pylint: disable=import-outside-toplevel  # Lazy imports
# pylint: disable=invalid-name  # Qt method names, single-letter layout vars
# pylint: disable=missing-function-docstring  # Internal UI methods
# pylint: disable=unnecessary-lambda  # Qt signal/slot pattern
# pylint: disable=unnecessary-pass  # Placeholder for future code
# pylint: disable=logging-fstring-interpolation  # F-strings clearer

from __future__ import annotations
import re
import sys

from typing import List, Tuple

from PySide6.QtCore import QEvent, QObject, Qt, Signal, Slot, QThread
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea,
    QSplitter, QVBoxLayout, QWidget
)

from src.i18n.translator import tr, tooltip_tr

# Core functionality
from ...core import Condition, SearchOptions, replace_in_text

# Utilities
from ...utils import read_text, write_text
from ...utils.logger import get_logger

# Components from this package
from .results_tree import ResultsTree
from .search_worker import SearchConditionRequest, SearchFileRequest, SearchWorker

# Progress management
from ..progress import OperationHistory

# Thread management
from ...ui import thread_manager, FeatureType, ProcessingModal

logger = get_logger(__name__)
_UNSET = object()


class _SearchReplaceReceiver(QObject):
    """GUI-thread receiver that rejects callbacks from superseded searches."""

    def __init__(self, panel, generation):
        super().__init__(panel)
        self.panel = panel
        self.generation = generation

    @Slot(str)
    def progress(self, current_path):
        self.panel._on_search_progress(self.generation, current_path)

    @Slot(int, int, str)
    def progress_detailed(self, current, total, message):
        self.panel._on_search_progress_detailed(
            self.generation, current, total, message
        )

    @Slot(str)
    def failed(self, message):
        self.panel._on_search_error(self.generation, message)

    @Slot(dict)
    def completed(self, matches):
        self.panel._on_search_done(self.generation, matches)

    @Slot()
    def thread_finished(self):
        self.panel._on_search_thread_finished(self.generation)


class SearchReplacePanel(QWidget):
    """
    Left-hand panel: path + include/exclude + search & replace controls.
    Right-hand panel: results.
    Now with integrated progress bar system (v2.5.0).
    """

    request_preview = Signal(dict)  # emits {"matches": {path: [(line,col,snip), ...], ...}}
    # Signal for external consumers (e.g., ai_processor_dock, json_editor_tab)
    # Parameters: (file_name_query, file_content_query, replacement, options, preserve_case, count)
    replace_requested = Signal(str, str, str, object, bool, int)

    def __init__(self, parent=None, progress_manager=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.processing_search = False
        self.settings_prefix = (
            progress_manager if isinstance(progress_manager, str) else "search_replace"
        )
        self.progress_manager = None if isinstance(progress_manager, str) else progress_manager
        self._current_task_id = None
        self._current_progress_widget = None
        self._processing_modal = None  # Modal de progresso
        self._search_thread = None
        self._search_worker = None
        self._search_receiver = None
        self._search_thread_id = None
        self._search_generation = 0
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
        self._pending_search_result = _UNSET
        self._search_metadata = None
        self._close_action = None

        # Path row
        column = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("search_replace.lbl_root_path")))
        self.ed_path = QLineEdit()
        self.ed_path.setToolTip(tooltip_tr("search_replace.tooltip_path"))
        self.btn_browse = QPushButton(tr("search_replace.btn_browse"))
        self.btn_browse.setToolTip(tooltip_tr("search_replace.tooltip_browse"))
        row.addWidget(self.ed_path, 1)
        row.addWidget(self.btn_browse)
        column.addLayout(row)
        self.is_file = QCheckBox(tr("search_replace.chk_is_file"))
        self.is_file.setToolTip(tooltip_tr("search_replace.tooltip_is_file"))
        column.addWidget(self.is_file)
        root.addLayout(column)

        # File extension filter (v2.9.0, v2.9.1 - optional)
        row = QHBoxLayout()
        self.chk_use_ext_filter = QCheckBox(tr("search_replace.chk_use_ext_filter"))
        self.chk_use_ext_filter.setChecked(True)  # Default: enabled
        self.chk_use_ext_filter.setToolTip(tooltip_tr("search_replace.tooltip_use_ext_filter"))
        row.addWidget(self.chk_use_ext_filter)
        row.addWidget(QLabel(tr("search_replace.lbl_extensions")))
        self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
        self.ed_extensions.setPlaceholderText(tr("search_replace.placeholder_extensions"))
        self.ed_extensions.setToolTip(tooltip_tr("search_replace.tooltip_extensions"))
        row.addWidget(self.ed_extensions)
        root.addLayout(row)

        # Sort results option (v2.9.5)
        self.chk_sort_results = QCheckBox(tr("search_replace.chk_sort_results"))
        self.chk_sort_results.setChecked(False)
        self.chk_sort_results.setToolTip(tooltip_tr("search_replace.tooltip_sort_results"))
        root.addWidget(self.chk_sort_results)

        # Include/Exclude globs (advanced)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("search_replace.lbl_include_globs")))
        self.ed_inc = QLineEdit()
        self.ed_inc.setPlaceholderText(tr("search_replace.placeholder_include"))
        self.ed_inc.setToolTip(tooltip_tr("search_replace.tooltip_inc"))
        root.addLayout(row)
        root.addWidget(self.ed_inc)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("search_replace.lbl_exclude_globs")))
        self.ed_exc = QLineEdit("node_modules;dist;build;.git")
        self.ed_exc.setToolTip(tooltip_tr("search_replace.tooltip_exc"))
        root.addLayout(row)
        root.addWidget(self.ed_exc)

        # Search field + toggles (v2.9.112 - split into file name and file content)
        gb = QGroupBox(tr("search_replace.group_search"))
        grid = QGridLayout(gb)

        # File name query field
        grid.addWidget(QLabel(tr("search_replace.lbl_file_name_query")), 0, 0)
        self.ed_filename_query = QLineEdit()
        self.ed_filename_query.setPlaceholderText(tr("search_replace.placeholder_filename"))
        self.ed_filename_query.setToolTip(tooltip_tr("search_replace.tooltip_filename_query"))
        grid.addWidget(self.ed_filename_query, 0, 1, 1, 3)

        # File content query field
        grid.addWidget(QLabel(tr("search_replace.lbl_file_content_query")), 1, 0)
        self.ed_query = QPlainTextEdit()
        self.ed_query.setMinimumHeight(30)
        self.ed_query.setMaximumHeight(150)
        self.ed_query.setPlaceholderText(tr("search_replace.placeholder_content"))
        self.ed_query.setToolTip(tooltip_tr("search_replace.tooltip_query"))
        grid.addWidget(self.ed_query, 1, 1, 1, 3)

        # Checkboxes
        self.chk_case = QCheckBox(tr("search_replace.chk_case_sensitive"))
        self.chk_case.setToolTip(tooltip_tr("search_replace.tooltip_case"))
        self.chk_word = QCheckBox(tr("search_replace.chk_whole_word"))
        self.chk_word.setToolTip(tooltip_tr("search_replace.tooltip_word"))
        self.chk_regex = QCheckBox(tr("search_replace.chk_regex"))
        self.chk_regex.setToolTip(tooltip_tr("search_replace.tooltip_regex"))
        self.chk_multi_query = QCheckBox(tr("search_replace.chk_multi_line"))  # v2.8.0
        self.chk_multi_query.setToolTip(tooltip_tr("search_replace.tooltip_multi_query"))
        self.btn_search = QPushButton(tr("search_replace.btn_search_cancel"))
        self.btn_search.setToolTip(tooltip_tr("search_replace.tooltip_search"))

        grid.addWidget(self.chk_case, 2, 0)
        grid.addWidget(self.chk_word, 2, 1)
        grid.addWidget(self.chk_regex, 2, 2)
        grid.addWidget(self.chk_multi_query, 2, 3)  # v2.8.0
        grid.addWidget(self.btn_search, 3, 3)  # Moved to row 3

        root.addWidget(gb)

        # Replace extras (optional)
        gb2 = QGroupBox(tr("search_replace.group_replace"))
        g2 = QGridLayout(gb2)
        g2.addWidget(QLabel(tr("search_replace.lbl_replacement")), 0, 0)
        self.ed_repl = QPlainTextEdit()
        self.ed_repl.setMinimumHeight(30)
        self.ed_repl.setMaximumHeight(150)
        self.ed_repl.setToolTip(tooltip_tr("search_replace.tooltip_repl"))
        self.chk_preserve = QCheckBox(tr("search_replace.chk_preserve_case"))
        self.chk_preserve.setToolTip(tooltip_tr("search_replace.tooltip_preserve"))
        self.btn_replace_one = QPushButton(tr("search_replace.btn_replace_first"))
        self.btn_replace_one.setToolTip(tooltip_tr("search_replace.tooltip_replace_one"))
        self.btn_replace_all = QPushButton(tr("search_replace.btn_replace_all"))
        self.btn_replace_all.setToolTip(tooltip_tr("search_replace.tooltip_replace_all"))
        g2.addWidget(self.ed_repl, 0, 1, 1, 3)
        g2.addWidget(self.chk_preserve, 1, 0)
        g2.addWidget(self.btn_replace_one, 1, 2)
        g2.addWidget(self.btn_replace_all, 1, 3)
        root.addWidget(gb2)

        # Advanced conditions (collapsible style via group box)
        gb3 = QGroupBox(tr("search_replace.group_advanced"))
        g3 = QGridLayout(gb3)

        # Add AND/OR selector at the top
        lbl_logic = QLabel(tr("search_replace.lbl_logic_operator"))
        self.combo_logic_op = QComboBox()
        self.combo_logic_op.addItems(["AND", "OR"])
        self.combo_logic_op.setToolTip(tooltip_tr("search_replace.tooltip_logic_op"))
        logic_layout = QHBoxLayout()
        logic_layout.addWidget(lbl_logic)
        logic_layout.addWidget(self.combo_logic_op)
        logic_layout.addStretch()
        g3.addLayout(logic_layout, 0, 0, 1, 8)

        # Add headers (now starting from row 1)
        g3.addWidget(QLabel(tr("search_replace.lbl_field")), 1, 0)
        g3.addWidget(QLabel(tr("search_replace.lbl_operator")), 1, 1)
        g3.addWidget(QLabel(tr("search_replace.lbl_value")), 1, 2)
        g3.addWidget(QLabel(tr("search_replace.lbl_scope")), 1, 3)
        g3.addWidget(QLabel(tr("search_replace.lbl_scope_param")), 1, 4)
        g3.addWidget(QLabel(tr("search_replace.lbl_case")), 1, 5)
        g3.addWidget(QLabel(tr("search_replace.lbl_word")), 1, 6)
        g3.addWidget(QLabel(tr("search_replace.lbl_regex")), 1, 7)

        # Dynamic condition rows (Task #5 - v2.9.7)
        self.cond_list: List[
            Tuple[QComboBox, QComboBox, QLineEdit, QComboBox, QLineEdit, QCheckBox, QCheckBox, QCheckBox, QPushButton]
        ] = []
        self.cond_grid = g3  # Store grid reference for dynamic row management
        self.next_cond_row = 2  # Track next available row (0=logic, 1=headers, 2+=conditions)

        # Buttons layout (v2.9.40.3: create BEFORE adding rows)
        self.buttons_layout_ref = QHBoxLayout()

        # Add initial 3 condition rows (minimum)
        for _ in range(3):
            self._add_condition_row()

        # Add Condition button
        btn_add_condition = QPushButton(tr("search_replace.btn_add_condition"))
        btn_add_condition.setToolTip(tooltip_tr("search_replace.tooltip_add_condition"))
        btn_add_condition.clicked.connect(self._add_condition_row)
        self.buttons_layout_ref.addWidget(btn_add_condition)

        # Clear All Conditions button (v2.9.5)
        btn_clear_conditions = QPushButton(tr("search_replace.btn_clear_conditions"))
        btn_clear_conditions.setToolTip(tooltip_tr("search_replace.tooltip_clear_conditions"))
        btn_clear_conditions.clicked.connect(self._clear_all_conditions)
        self.buttons_layout_ref.addWidget(btn_clear_conditions)

        self.buttons_layout_ref.addStretch()

        # Buttons already added to grid by _add_condition_row (v2.9.40.3)

        root.addWidget(gb3)

        # Results on the right
        self.results = ResultsTree()

        # Install event filter for hover expansion (v2.9.115)
        self.results.installEventFilter(self)

        # Results panel with save button
        results_layout = QVBoxLayout()
        results_header = QHBoxLayout()
        results_label = QLabel(tr("search_replace.lbl_results"))
        results_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.btn_save_results = QPushButton(tr("search_replace.btn_save_results"))
        self.btn_save_results.setToolTip(tooltip_tr("search_replace.tooltip_save_results"))
        self.btn_save_results.clicked.connect(self._save_results)
        results_header.addWidget(results_label)
        results_header.addStretch()
        results_header.addWidget(self.btn_save_results)
        results_layout.addLayout(results_header)
        results_layout.addWidget(self.results)

        # Status bar at bottom showing position info (v2.5.1)
        self.results_status = QLabel("")
        self.results_status.setStyleSheet("padding: 4px; background-color: #f0f0f0; color: #333; font-size: 10pt;")
        self.results_status.setMinimumHeight(25)
        results_layout.addWidget(self.results_status)

        # Connect status label to results tree
        self.results.set_status_label(self.results_status)

        results_widget = QWidget()
        results_widget.setLayout(results_layout)

        # Wrap left panel in scroll area (v2.9.5)
        left_widget = QWidget()
        left_widget.setLayout(root)
        scroll_area = QScrollArea()
        scroll_area.setWidget(left_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        splitter = QSplitter()
        splitter.addWidget(scroll_area)
        splitter.addWidget(results_widget)
        splitter.setSizes([500, 800])

        # Store splitter and widget references for hover expansion (v2.9.115)
        self._splitter = splitter
        self._results_widget = results_widget
        self._original_sizes = [500, 800]  # Default sizes
        self._is_expanded = False

        wroot = QVBoxLayout(self)
        wroot.setContentsMargins(0, 0, 0, 0)
        wroot.addWidget(splitter)

        # Connect
        self.is_file.stateChanged.connect(self.change_advanced_conditions)
        self.btn_browse.clicked.connect(self._browse)
        self.btn_search.clicked.connect(self._start_search_threaded)
        self.btn_replace_one.clicked.connect(lambda: self._do_replace(all_=False))
        self.btn_replace_all.clicked.connect(lambda: self._do_replace(all_=True))


    def set_editor_fonts(self, font):
        """Set monospaced font for query and replacement editors (v2.9.115)."""
        self.ed_repl.setFont(font)
        self.ed_query.setFont(font)

    def eventFilter(self, obj, event):
        """
        Event filter for Results panel hover expansion (v2.9.115).

        When mouse enters Results panel: expand width to show full content.
        When mouse leaves Results panel: restore original width.

        Solves issue: Panel was moving left/right on mouse movement.
        """
        if obj == self.results:
            if event.type() == QEvent.Enter:
                # Mouse entered Results panel - expand to show more content
                if not self._is_expanded:
                    self._original_sizes = self._splitter.sizes()
                    left_size = self._original_sizes[0]
                    right_size = self._original_sizes[1]

                    # Expand right panel by 300px (take from left)
                    new_left = max(200, left_size - 300)  # Minimum 200px for left
                    new_right = right_size + (left_size - new_left)

                    self._splitter.setSizes([new_left, new_right])
                    self._is_expanded = True

            elif event.type() == QEvent.Leave:
                # Mouse left Results panel - restore original width
                if self._is_expanded:
                    self._splitter.setSizes(self._original_sizes)
                    self._is_expanded = False

        return False

    def change_advanced_conditions(self):
        self.enable_buttons(not self.is_file.isChecked(), include_buttons=False)

    def emit_replace_request(self):
        """
        Public method to emit replace_requested signal with current panel state.

        Useful for external consumers (e.g., ai_processor_dock, json_editor_tab)
        that want to perform replace operations on their own content using
        this panel's search/replace configuration.

        Returns:
            bool: True if signal was emitted, False if validation failed
        """
        try:
            # Get values from UI
            file_name_query = self.ed_filename_query.text().strip()
            file_content_query = self.ed_query.toPlainText().strip()
            replacement = self.ed_repl.toPlainText().strip()

            # Validation
            if not file_content_query and not file_name_query:
                return False

            # Build SearchOptions
            options = SearchOptions(
                case_sensitive=self.chk_case.isChecked(),
                whole_word=self.chk_word.isChecked(),
                regex=self.chk_regex.isChecked(),
            )

            preserve_case = self.chk_preserve.isChecked()
            count = 0  # 0 = replace all

            # Emit signal
            self.replace_requested.emit(file_name_query, file_content_query, replacement, options, preserve_case, count)
            return True

        except Exception as e:
            logger.error(f"Failed to emit replace_requested: {e}")
            return False

    def _add_condition_row(self):
        """Add a new dynamic condition row (Task #5 - v2.9.7)"""
        row_i = self.next_cond_row

        # Create widgets
        cb_field = QComboBox()
        cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])

        cb_op = QComboBox()
        cb_op.addItems(
            ["", "contains", "not contains", "equals", "not equals", "starts with", "ends with", ">", "<", ">=", "<="]
        )

        ed_val = QLineEdit()

        cb_scope = QComboBox()
        cb_scope.addItems(["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag"])

        ed_scope_val = QLineEdit()
        ed_scope_val.setPlaceholderText(tr("search_replace.placeholder_scope_value"))

        # Checkboxes for matching options
        chk_case = QCheckBox()
        chk_case.setChecked(True)  # Default: case sensitive
        chk_case.setToolTip(tooltip_tr("search_replace.tooltip_cond_case"))

        chk_word = QCheckBox()
        chk_word.setToolTip(tooltip_tr("search_replace.tooltip_cond_word"))

        chk_regex = QCheckBox()
        chk_regex.setToolTip(tooltip_tr("search_replace_panel.tooltip_regex_cond"))

        # Remove button (X)
        btn_remove = QPushButton("✖")
        btn_remove.setFixedWidth(30)
        btn_remove.setToolTip(tooltip_tr("search_replace.tooltip_remove_condition"))
        btn_remove.setStyleSheet("QPushButton { color: red; font-weight: bold; }")

        # Add widgets to grid
        self.cond_grid.addWidget(cb_field, row_i, 0)
        self.cond_grid.addWidget(cb_op, row_i, 1)
        self.cond_grid.addWidget(ed_val, row_i, 2)
        self.cond_grid.addWidget(cb_scope, row_i, 3)
        self.cond_grid.addWidget(ed_scope_val, row_i, 4)
        self.cond_grid.addWidget(chk_case, row_i, 5)
        self.cond_grid.addWidget(chk_word, row_i, 6)
        self.cond_grid.addWidget(chk_regex, row_i, 7)
        self.cond_grid.addWidget(btn_remove, row_i, 8)

        # Store reference
        widgets_tuple = (cb_field, cb_op, ed_val, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex, btn_remove)
        self.cond_list.append(widgets_tuple)

        # Connect remove button
        btn_remove.clicked.connect(lambda: self._remove_condition_row(widgets_tuple))

        # Increment row counter
        self.next_cond_row += 1

        # Move buttons layout to new bottom position (v2.9.40.3: use stored reference)
        self.cond_grid.removeItem(self.buttons_layout_ref)
        self.cond_grid.addLayout(self.buttons_layout_ref, self.next_cond_row, 0, 1, 8)

    def _remove_condition_row(self, widgets_tuple):
        """Remove a condition row (Task #5 - v2.9.7)"""
        # Enforce minimum of 3 rows
        if len(self.cond_list) <= 3:
            QMessageBox.warning(
                self, tr("search_replace.msg_cannot_remove_title"), tr("search_replace.msg_cannot_remove")
            )
            return

        # Remove from list
        if widgets_tuple in self.cond_list:
            self.cond_list.remove(widgets_tuple)

        # Remove widgets from grid and delete them
        for widget in widgets_tuple:
            self.cond_grid.removeWidget(widget)
            widget.deleteLater()

    def _clear_all_conditions(self):
        """Clear all advanced condition fields (v2.9.5)"""
        # Reset logic operator to AND
        self.combo_logic_op.setCurrentIndex(0)

        # Clear all condition rows (updated for v2.9.7 - tuple now has 9 elements)
        for widgets in self.cond_list:
            cb_field, cb_op, ed_val, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex = widgets[:8]
            cb_field.setCurrentIndex(0)  # Reset to empty
            cb_op.setCurrentIndex(0)  # Reset to empty
            ed_val.clear()  # Clear value
            cb_scope.setCurrentIndex(0)  # Reset to "none"
            ed_scope_val.clear()  # Clear scope param
            chk_case.setChecked(True)  # Default: case sensitive
            chk_word.setChecked(False)  # Default: not whole word
            chk_regex.setChecked(False)  # Default: not regex

    def _browse(self):
        if self.is_file.isChecked():
            # self.enable_buttons(False, include_buttons = False)
            path, _ = QFileDialog.getOpenFileName(
                self, "Select dictionary", "", "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
            )
        else:
            # self.enable_buttons(True, include_buttons = False)
            path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")

        if path:
            self.ed_path.setText(path)

    def _conds(self) -> tuple[List[Condition], str]:
        """Return conditions and logic operator (AND/OR)"""
        out: List[Condition] = []
        if not self.is_file.isChecked():
            for (
                cb_field,
                cb_op,
                ed,
                cb_scope,
                ed_scope_val,
                chk_case,
                chk_word,
                chk_regex,
                _btn_remove,
            ) in self.cond_list:
                field = cb_field.currentText().strip()
                operator = cb_op.currentText().strip()
                value = ed.text().strip()
                scope_type = cb_scope.currentText().strip()
                scope_val = ed_scope_val.text().strip()
                case_sensitive = chk_case.isChecked()
                whole_word = chk_word.isChecked()
                use_regex = chk_regex.isChecked()
                if field and operator and value:
                    out.append(Condition(field, operator, value, scope_type,
                                       scope_val, case_sensitive, whole_word, use_regex))
        logic_op = self.combo_logic_op.currentText()
        return out, logic_op

    def _snapshot_search_request(self) -> SearchFileRequest:
        """Read file-selection widgets once on the GUI thread."""
        path = self.ed_path.text().strip()

        # v2.9.0, v2.9.1: Handle extension filter (optional)
        use_ext_filter = self.chk_use_ext_filter.isChecked()
        extensions_text = self.ed_extensions.text().strip() if use_ext_filter else ""
        ed_inc_text = self.ed_inc.text().strip()

        # Build include globs from extensions if enabled and provided
        if use_ext_filter and extensions_text:
            # Parse extensions (comma or semicolon separated)
            extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
            # Ensure extensions start with dot
            extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
            # Convert to glob patterns
            ext_globs = [f"*{ext}" for ext in extensions]

            # Combine with user-provided include globs if any
            if ed_inc_text:
                inc = [glob_pat.strip() for glob_pat in re.split(r"[;,]", ed_inc_text)
                       if glob_pat.strip()]
                inc.extend(ext_globs)
            else:
                inc = ext_globs
        else:
            # No extension filter, use include globs or default
            if ed_inc_text:
                inc = [glob_pat.strip() for glob_pat in re.split(r"[;,]", ed_inc_text)
                       if glob_pat.strip()]
            else:
                inc = ["*.*"]  # Default: all files

        exc = [glob_pat.strip() for glob_pat in re.split(r"[;,]", self.ed_exc.text())
               if glob_pat.strip()]
        conds, logic_op = self._conds()
        return SearchFileRequest(
            root=path,
            include_globs=tuple(inc),
            exclude_globs=tuple(exc),
            conditions=tuple(
                SearchConditionRequest.from_condition(condition)
                for condition in conds
            ),
            logic_operator=logic_op,
        )

    def _iter_files(self) -> List[str]:
        """Return files synchronously for replace and compatibility consumers."""
        return list(self._snapshot_search_request().iter_files())

    def enable_buttons(self, state, include_buttons=True, include_advanced_conditions=True):
        if include_buttons:
            self.btn_browse.setEnabled(state)
            self.btn_replace_one.setEnabled(state)
            self.btn_replace_all.setEnabled(state)

        if include_advanced_conditions:
            for (
                cb_field,
                cb_op,
                ed,
                cb_scope,
                ed_scope_val,
                chk_case,
                chk_word,
                chk_regex,
                _btn_remove,
            ) in self.cond_list:
                cb_field.setEnabled(state)
                cb_op.setEnabled(state)
                ed.setEnabled(state)
                ed.setReadOnly(not state)
                cb_scope.setEnabled(state)
                ed_scope_val.setEnabled(state)
                ed_scope_val.setReadOnly(not state)
                chk_case.setEnabled(state)
                chk_word.setEnabled(state)
                chk_regex.setEnabled(state)

    def _start_search_threaded(self):
        if self._operation_running():
            self.cancel_search()
            return

        self.results.print_message("Loading...")
        filename_query = self.ed_filename_query.text().strip()
        content_query = self.ed_query.toPlainText().strip()
        if not filename_query and not content_query:
            QMessageBox.warning(
                self,
                tr("search_replace.msg_no_query_title"),
                tr("search_replace.msg_no_query"),
            )
            self.results.print_message("Search cancelled: no query provided")
            return

        search_mode = "both"
        if filename_query and not content_query:
            search_mode = "filename_only"
        elif content_query and not filename_query:
            search_mode = "content_only"

        is_multi_query = self.chk_multi_query.isChecked() and hasattr(
            self, "ed_query_multi"
        )
        query_text = (
            self.ed_query_multi.toPlainText() if is_multi_query else content_query
        )
        pattern_text = None
        multi_query_processor = None
        try:
            if is_multi_query:
                from src.core.multi_query import MultiQueryProcessor

                multi_query_processor = MultiQueryProcessor(
                    multi_line_text=query_text,
                    case_sensitive=self.chk_case.isChecked(),
                    whole_word=self.chk_word.isChecked(),
                    use_regex=self.chk_regex.isChecked(),
                )
                is_valid, error_msg = multi_query_processor.validate()
                if not is_valid:
                    raise ValueError(f"Invalid queries: {error_msg}")
                if not multi_query_processor.get_query_count():
                    raise ValueError(
                        "No valid queries found. Add at least one search pattern."
                    )
            elif search_mode != "filename_only":
                pattern_text = SearchOptions(
                    self.chk_case.isChecked(),
                    self.chk_word.isChecked(),
                    self.chk_regex.isChecked(),
                ).compile(query_text)
            request = self._snapshot_search_request()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._report_search_setup_error(str(exc))
            return

        self._dispose_processing_modal()
        self._processing_modal = ProcessingModal(
            title="Search/Replace Processing",
            parent=self,
            show_progress=True,
            show_cancel=True,
        )
        if is_multi_query:
            query_count = multi_query_processor.get_query_count()
            self._processing_modal.set_title(
                f"Searching Files ({query_count} queries)..."
            )
            self._processing_modal.set_status(
                f"Initializing multi-query search with {query_count} patterns..."
            )
        else:
            self._processing_modal.set_title("Searching Files...")
            self._processing_modal.set_status("Initializing search...")
        self._processing_modal.start_loading_animation()
        self._processing_modal.show()

        if self.progress_manager:
            import uuid

            self._current_task_id = f"search_{uuid.uuid4().hex[:8]}"
            query_count = (
                multi_query_processor.get_query_count() if is_multi_query else 0
            )
            task_label = (
                f"Multi-Search ({query_count} queries)"
                if is_multi_query
                else f"Search: {content_query[:30]}"
            )
            self._current_progress_widget = self.progress_manager.add_task(
                self._current_task_id, task_label
            )

        self._search_generation += 1
        generation = self._search_generation
        self._search_thread_id = f"search_replace:{id(self)}:{generation}"
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
        self._pending_search_result = _UNSET
        self._search_metadata = {
            "query": query_text,
            "path": request.root,
            "case_sensitive": self.chk_case.isChecked(),
            "whole_word": self.chk_word.isChecked(),
            "regex": self.chk_regex.isChecked(),
            "sort_results": self.chk_sort_results.isChecked(),
        }
        self._search_thread = QThread(self)
        self._search_worker = SearchWorker(
            pattern_text=pattern_text,
            iter_files_fn=request.iter_files,
            search_options_factory=lambda a, b, c: SearchOptions(a, b, c),
            is_multi_query=is_multi_query,
            multi_query_processor=multi_query_processor,
            search_mode=search_mode,
            filename_pattern=filename_query or None,
        )
        self._search_receiver = _SearchReplaceReceiver(self, generation)
        self._search_worker.moveToThread(self._search_thread)

        worker = self._search_worker
        native = self._search_thread
        receiver = self._search_receiver
        native.started.connect(worker.run)
        worker.done.connect(receiver.completed)
        worker.progress.connect(receiver.progress)
        worker.progress_detailed.connect(receiver.progress_detailed)
        worker.error.connect(receiver.failed)
        worker.done.connect(worker.deleteLater)
        worker.done.connect(native.quit, Qt.DirectConnection)
        native.finished.connect(receiver.thread_finished)
        native.finished.connect(native.deleteLater)

        if not thread_manager.start_thread(
            self._search_thread_id,
            native,
            worker,
            FeatureType.SEARCH_REPLACE,
            cancel_callback=worker.cancel,
            exclusive=False,
        ):
            worker.deleteLater()
            native.deleteLater()
            receiver.deleteLater()
            self._clear_search_references()
            self._processing_modal.mark_completed(
                success=False,
                message="Cannot start while the application is shutting down",
            )
            return

        self._processing_modal.cancel_requested.connect(
            lambda current=generation: self.cancel_search(current)
        )
        if self._current_progress_widget:
            self._current_progress_widget.cancel_requested.connect(
                lambda _task_id, current=generation: self.cancel_search(current)
            )
            self._current_progress_widget.pause_requested.connect(
                lambda _task_id, paused, current=generation: self._set_search_paused(
                    current, paused
                )
            )

        self.processing_search = True
        self._set_search_controls_enabled(False)
        native.start()

    def _report_search_setup_error(self, message):
        self.results.print_message(f"Search cancelled: {message}")
        logger.error("Search setup failed: %s", message)

    def _dispose_processing_modal(self):
        if self._processing_modal is None:
            return
        self._processing_modal.stop_loading_animation()
        self._processing_modal.hide()
        self._processing_modal.deleteLater()
        self._processing_modal = None

    def _set_search_controls_enabled(self, enabled):
        self.enable_buttons(
            enabled,
            include_advanced_conditions=not self.is_file.isChecked(),
        )
        for widget in (
            self.ed_path,
            self.is_file,
            self.chk_use_ext_filter,
            self.ed_extensions,
            self.ed_inc,
            self.ed_exc,
            self.ed_filename_query,
            self.ed_query,
            self.chk_case,
            self.chk_word,
            self.chk_regex,
            self.chk_multi_query,
            self.chk_sort_results,
            self.combo_logic_op,
        ):
            widget.setEnabled(enabled)
        if hasattr(self, "ed_query_multi"):
            self.ed_query_multi.setEnabled(enabled)

    def _operation_running(self):
        return self.processing_search or (
            self._search_thread is not None and self._search_thread.isRunning()
        )

    def cancel_search(self, generation=None):
        """Request cancellation without releasing ownership before settlement."""
        if generation is not None and generation != self._search_generation:
            return
        if self._search_worker is None:
            return
        self._search_cancel_requested = True
        self._search_worker.cancel()
        if self._processing_modal:
            self._processing_modal.set_status("Cancellation requested, please wait...")

    def _set_search_paused(self, generation, paused):
        if generation != self._search_generation or self._search_worker is None:
            return
        self._search_worker.pause() if paused else self._search_worker.resume()

    def _on_search_progress(self, generation: int, current_path: str):
        """Legacy progress handler - kept for compatibility."""
        del current_path
        if generation != self._search_generation:
            return

    def _on_search_progress_detailed(
        self, generation: int, current: int, total: int, message: str
    ):
        """New detailed progress handler (v2.5.0)."""
        if generation != self._search_generation or self._discard_search_callbacks:
            return
        # Update processing modal (v2.7.0)
        if self._processing_modal:
            progress = int((current / total * 100)) if total > 0 else 0
            self._processing_modal.set_progress(progress)
            self._processing_modal.set_status(f"Processing {current}/{total} files")
            self._processing_modal.log_message(message)

        # Update progress widget (v2.5.0) - mantido para compatibilidade
        if self._current_progress_widget:
            self._current_progress_widget.update_progress(current, total, message)
            self._current_progress_widget.add_log(f"Processing: {message}")

    def _on_search_error(self, generation: int, msg: str):
        """Handle search errors."""
        if generation != self._search_generation or self._discard_search_callbacks:
            return
        # Update processing modal (v2.7.0)
        if self._processing_modal:
            self._processing_modal.log_message(f"ERROR: {msg}")

        # Update progress widget (v2.5.0) - mantido para compatibilidade
        if self._current_progress_widget:
            self._current_progress_widget.add_log(f"ERROR: {msg}")
        logger.error(msg)

    def _on_search_done(self, generation: int, matches: dict):
        """Store completion data until the native thread has settled."""
        if generation == self._search_generation:
            self._pending_search_result = matches

    def _apply_search_result(self, matches, metadata):
        """Apply a settled result on the GUI thread."""
        self.results.populate(matches, metadata["sort_results"])
        if self._processing_modal:
            self._processing_modal.mark_completed(
                success=True,
                message=(
                    "Search completed successfully!\n"
                    f"Found matches in {len(matches)} file(s)."
                ),
            )
        if self._current_progress_widget:
            self._current_progress_widget.set_complete(success=True)
            self._current_progress_widget.add_log(
                f"Search completed: {len(matches)} files with matches"
            )

        try:
            history = OperationHistory()
            total_matches = sum(len(items) for items in matches.values())
            history.add_operation(
                "search",
                {
                    "query": metadata["query"],
                    "path": metadata["path"],
                    "files_matched": len(matches),
                    "total_matches": total_matches,
                    "case_sensitive": metadata["case_sensitive"],
                    "whole_word": metadata["whole_word"],
                    "regex": metadata["regex"],
                },
            )
            if hasattr(self, "dock_history"):
                self.dock_history.add_operation(
                    "Search",
                    {
                        "query": metadata["query"],
                        "files_processed": len(matches),
                        "matches_found": total_matches,
                    },
                )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Failed to save history: %s", exc)

    def _on_search_thread_finished(self, generation):
        """Release controls and ownership only after native settlement."""
        if generation != self._search_generation:
            return
        action = self._close_action
        self._close_action = None
        cancelled = self._search_cancel_requested
        discard = self._discard_search_callbacks
        result = self._pending_search_result
        metadata = self._search_metadata
        self._clear_search_references()
        self.processing_search = False
        self._set_search_controls_enabled(True)

        if cancelled or discard:
            if self._processing_modal:
                self._processing_modal.mark_completed(
                    success=False, message="Search cancelled."
                )
            if self._current_progress_widget:
                self._current_progress_widget.set_complete(success=False)
                self._current_progress_widget.add_log("Search cancelled")
        elif result is _UNSET or metadata is None:
            if self._processing_modal:
                self._processing_modal.mark_completed(
                    success=False, message="Search ended without a result."
                )
        else:
            self._apply_search_result(result, metadata)

        self._pending_search_result = _UNSET
        self._search_metadata = None
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
        if action:
            self._dispose_processing_modal()
            name, target = action
            if name == "tab":
                index = target.tabs.indexOf(self)
                if index >= 0:
                    target._close_tab(index)
            else:
                target.close()

    def _clear_search_references(self):
        receiver = self._search_receiver
        self._search_thread = None
        self._search_worker = None
        self._search_receiver = None
        self._search_thread_id = None
        if receiver is not None:
            receiver.deleteLater()

    def request_tab_close(self):
        if not self._operation_running():
            return True
        host = self.window()
        if hasattr(host, "tabs") and hasattr(host, "_close_tab"):
            self._close_action = ("tab", host)
        self._discard_search_callbacks = True
        self.cancel_search()
        return False

    def closeEvent(self, event):
        if self._operation_running():
            self._close_action = ("close", self)
            self._discard_search_callbacks = True
            self.cancel_search()
            event.ignore()
            return
        self._dispose_processing_modal()
        super().closeEvent(event)

    def _save_results(self):
        """Save search results to a text file."""
        matches_data = self.results.get_matches_data()

        if not matches_data:
            QMessageBox.information(
                self, tr("search_replace.msg_no_results_save_title"), tr("search_replace.msg_no_results_save")
            )
            return

        # Ask user for file location
        default_filename = "clarify_search_results.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Search Results", default_filename, "Text Files (*.txt);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        try:
            # Export matches to text
            text_content = self.results.export_to_text()

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            total_files = len(matches_data)
            total_matches = sum(len(items) for items in matches_data.values())

            QMessageBox.information(
                self,
                tr("search_replace.msg_results_saved_title"),
                tr("search_replace.msg_results_saved").format(
                    file_path=file_path, total_files=total_files, total_matches=total_matches
                ),
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                tr("search_replace.msg_error_save_title"),
                tr("search_replace.msg_error_save").format(error=str(e)),
            )

    def _do_replace(self, all_: bool):
        try:
            patt = SearchOptions(
                self.chk_case.isChecked(), self.chk_word.isChecked(), self.chk_regex.isChecked()
            ).compile(self.ed_query.toPlainText().strip())
        except ValueError as e:
            QMessageBox.critical(self, "Invalid pattern", str(e))
            return

        repl = self.ed_repl.toPlainText().strip()
        preserve = self.chk_preserve.isChecked()
        count_files = 0
        for p in self._iter_files():
            try:
                text = read_text(p)
                new, n = replace_in_text(text, patt, repl, preserve, 0 if all_ else 1)
                if n > 0:
                    write_text(p, new)
                    count_files += 1
            except Exception as e:
                logger.warning(f"{p}: {e}")

        # Add to History Dock (v2.9.6)
        try:
            if hasattr(self, "dock_history"):
                self.dock_history.add_operation(
                    "Replace",
                    {"query": self.ed_query.toPlainText().strip(), "replacement": repl, "files_processed": count_files},
                )
        except Exception as e:
            logger.error(f"Failed to save to history dock: {e}")

        QMessageBox.information(
            self,
            tr("search_replace.msg_replace_title"),
            tr("search_replace.msg_replace_success").format(count=count_files),
        )
        self.results.print_message()
