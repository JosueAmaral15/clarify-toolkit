#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Insert Panel Module
-------------------
Provides the main insert interface panel for Clarify.

This module contains the InsertPanel class which implements:
  - File/directory path selection and browsing
  - Extension filtering and glob patterns (include/exclude)
  - Line lookup functionality with search query support
  - Manual line number specification
  - Multiple insertion modes (left, right, replace, insert-above, insert-below)
  - Advanced conditional filtering (filename, path, ext, size, mtime, content)
  - Dynamic condition rows with AND/OR logic operators
  - Live search preview with match highlighting
  - Integrated progress tracking and cancellation
  - Results display with save to file capability
  - Sort results alphabetically option

Author: Josué Amaral
Date: 2025
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern
# pylint: disable=too-many-instance-attributes  # Complex UI panel
# pylint: disable=too-many-public-methods  # UI event handlers
# pylint: disable=import-outside-toplevel  # Lazy imports
# pylint: disable=missing-class-docstring  # Internal classes
# pylint: disable=missing-function-docstring  # Internal UI methods
# pylint: disable=unnecessary-lambda  # Qt signal/slot pattern
# pylint: disable=unnecessary-pass  # Placeholder for future code
# pylint: disable=logging-fstring-interpolation  # F-strings clearer

from __future__ import annotations
import os
import re
import sys

from typing import List, Tuple

from PySide6.QtCore import QObject, Qt, Signal, Slot, QThread, QTimer
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPlainTextEdit, QPushButton, QScrollArea,
    QSpinBox, QSplitter, QVBoxLayout, QWidget
)

# Core functionality
from ...core import SearchOptions, Condition, filter_files_by_conditions, InsertMode, insert_at_line

# Utilities
from ...utils import walk_files, read_text, write_text
from ...utils.logger import get_logger
from ...i18n.translator import tr, tooltip_tr

# Components from this package
from .results_tree import ResultsTree
from .search_worker import SearchConditionRequest, SearchFileRequest, SearchWorker

# Progress management
from ..progress import OperationHistory

# Thread management
from ...ui import FeatureType, thread_manager

logger = get_logger(__name__)


class _InsertSearchReceiver(QObject):
    """GUI-thread receiver that rejects callbacks from superseded operations."""

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


class InsertPanel(QWidget):
    request_status = Signal(str)
    # Signal for external consumers (e.g., ai_processor_dock, json_editor_tab)
    # Parameters: (line_no, text, mode)
    insert_requested = Signal(int, str, str)

    def __init__(self, parent=None, progress_manager=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        self.processing_search = False
        # Older embedded consumers pass a settings-prefix string here. Keep the
        # constructor compatible without mistaking that identifier for a manager.
        self.settings_prefix = progress_manager if isinstance(progress_manager, str) else "insert"
        self.progress_manager = None if isinstance(progress_manager, str) else progress_manager
        self._current_task_id = None
        self._current_progress_widget = None
        self._processing_modal = None  # Modal de progresso (v2.7.0)
        self._search_thread = None
        self._search_worker = None
        self._search_receiver = None
        self._search_thread_id = None
        self._search_generation = 0
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
        self._close_action = None

        layout.addWidget(QLabel(tr("insert_panel.lbl_root_path")), 0, 0)
        self.ed_path = QLineEdit()
        self.ed_path.setToolTip(tooltip_tr("insert_panel.tooltip_path"))
        self.btn_browse = QPushButton(tr("insert_panel.btn_browse"))
        self.btn_browse.setToolTip(tooltip_tr("insert_panel.tooltip_browse"))
        layout.addWidget(self.ed_path, 0, 1, 1, 3)
        layout.addWidget(self.btn_browse, 0, 4)

        self.is_file = QCheckBox(tr("insert_panel.chk_is_file"))
        self.is_file.setToolTip(tooltip_tr("insert_panel.tooltip_is_file"))
        layout.addWidget(self.is_file, 1, 0)

        # Extension filter (v2.9.0, v2.9.1 - optional)
        self.chk_use_ext_filter = QCheckBox(tr("insert_panel.chk_use_ext_filter"))
        self.chk_use_ext_filter.setChecked(True)
        self.chk_use_ext_filter.setToolTip(tooltip_tr("insert_panel.tooltip_use_ext_filter"))
        layout.addWidget(self.chk_use_ext_filter, 2, 0)
        layout.addWidget(QLabel(tr("insert_panel.lbl_extensions")), 2, 1)
        self.ed_extensions = QLineEdit(".ts,.tsx,.js,.jsx,.py,.md")
        self.ed_extensions.setPlaceholderText(tr("insert_panel.placeholder_extensions"))
        self.ed_extensions.setToolTip(tooltip_tr("insert_panel.tooltip_extensions"))
        layout.addWidget(self.ed_extensions, 2, 2, 1, 3)

        # Sort results option (v2.9.5)
        self.chk_sort_results = QCheckBox(tr("insert_panel.chk_sort_results"))
        self.chk_sort_results.setChecked(False)
        self.chk_sort_results.setToolTip(tooltip_tr("insert_panel.tooltip_sort_results"))
        layout.addWidget(self.chk_sort_results, 2, 5)

        layout.addWidget(QLabel(tr("insert_panel.lbl_include_globs")), 3, 0)
        self.ed_inc = QLineEdit()
        self.ed_inc.setPlaceholderText(tr("insert_panel.placeholder_include"))
        self.ed_inc.setToolTip(tooltip_tr("insert_panel.tooltip_inc"))
        layout.addWidget(self.ed_inc, 3, 1, 1, 4)

        layout.addWidget(QLabel(tr("insert_panel.lbl_exclude_globs")), 4, 0)
        self.ed_exc = QLineEdit("node_modules;dist;build;.git")
        self.ed_exc.setToolTip(tooltip_tr("insert_panel.tooltip_exc"))
        layout.addWidget(self.ed_exc, 4, 1, 1, 4)

        # Search/Lookup section (new feature)
        gb_lookup = QGroupBox(tr("insert_panel.group_lookup"))
        g_lookup = QGridLayout(gb_lookup)
        g_lookup.addWidget(QLabel(tr("insert_panel.lbl_search_query")), 0, 0)
        self.ed_query = QLineEdit()
        self.ed_query.setPlaceholderText(tr("insert_panel.placeholder_query"))
        self.ed_query.setToolTip(tooltip_tr("insert_panel.tooltip_query"))
        g_lookup.addWidget(self.ed_query, 0, 1, 1, 3)

        self.chk_lookup_case = QCheckBox(tr("insert_panel.chk_case_sensitive"))
        self.chk_lookup_case.setToolTip(tooltip_tr("insert_panel.tooltip_lookup_case"))
        self.chk_lookup_word = QCheckBox(tr("insert_panel.chk_whole_word"))
        self.chk_lookup_word.setToolTip(tooltip_tr("insert_panel.tooltip_lookup_word"))
        self.chk_lookup_regex = QCheckBox(tr("insert_panel.chk_regex"))
        self.chk_lookup_regex.setToolTip(tooltip_tr("insert_panel.tooltip_lookup_regex"))
        g_lookup.addWidget(self.chk_lookup_case, 1, 0)
        g_lookup.addWidget(self.chk_lookup_word, 1, 1)
        g_lookup.addWidget(self.chk_lookup_regex, 1, 2)

        self.cb_lookup_occurrence = QComboBox()
        self.cb_lookup_occurrence.addItems(
            [tr("insert_panel.combo_first"), tr("insert_panel.combo_last"), tr("insert_panel.combo_all")]
        )
        self.cb_lookup_occurrence.setToolTip(tooltip_tr("insert_panel.tooltip_lookup_occurrence"))
        g_lookup.addWidget(QLabel(tr("insert_panel.lbl_occurrence")), 1, 3)
        g_lookup.addWidget(self.cb_lookup_occurrence, 1, 4)
        layout.addWidget(gb_lookup, 5, 0, 1, 5)

        layout.addWidget(QLabel(tr("insert_panel.lbl_line_number")), 6, 0)
        self.spin_line = QSpinBox()
        self.spin_line.setRange(1, 10_000_000)
        self.spin_line.setValue(1)
        self.spin_line.setToolTip(tooltip_tr("insert_panel.tooltip_line"))
        layout.addWidget(self.spin_line, 6, 1)

        layout.addWidget(QLabel(tr("insert_panel.lbl_insert_text")), 7, 0)
        self.ed_text = QPlainTextEdit()
        self.ed_text.setMinimumHeight(60)
        self.ed_text.setMaximumHeight(200)
        self.ed_text.setToolTip(tooltip_tr("insert_panel.tooltip_text"))
        layout.addWidget(self.ed_text, 7, 1, 1, 4)

        layout.addWidget(QLabel(tr("insert_panel.lbl_mode")), 8, 0)
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(
            [InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE, InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW]
        )
        self.cb_mode.setToolTip(tooltip_tr("insert_panel.tooltip_mode"))
        layout.addWidget(self.cb_mode, 8, 1)

        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._start_search_threaded)

        # Advanced conditions (same as Search/Replace, including `content`)
        gb3 = QGroupBox(tr("insert_panel.group_advanced"))
        g3 = QGridLayout(gb3)

        # Add AND/OR selector at the top
        lbl_logic = QLabel(tr("insert_panel.lbl_logic_operator"))
        self.combo_logic_op = QComboBox()
        self.combo_logic_op.addItems(["AND", "OR"])
        self.combo_logic_op.setToolTip(tooltip_tr("insert_panel.tooltip_logic_op"))
        self.combo_logic_op.currentTextChanged.connect(self._schedule_live_refresh)
        logic_layout = QHBoxLayout()
        logic_layout.addWidget(lbl_logic)
        logic_layout.addWidget(self.combo_logic_op)
        logic_layout.addStretch()
        g3.addLayout(logic_layout, 0, 0, 1, 8)

        # Add headers (now starting from row 1)
        g3.addWidget(QLabel(tr("insert_panel.lbl_field")), 1, 0)
        g3.addWidget(QLabel(tr("insert_panel.lbl_operator")), 1, 1)
        g3.addWidget(QLabel(tr("insert_panel.lbl_value")), 1, 2)
        g3.addWidget(QLabel(tr("insert_panel.lbl_scope")), 1, 3)
        g3.addWidget(QLabel(tr("insert_panel.lbl_scope_param")), 1, 4)
        g3.addWidget(QLabel(tr("insert_panel.lbl_case")), 1, 5)
        g3.addWidget(QLabel(tr("insert_panel.lbl_word")), 1, 6)
        g3.addWidget(QLabel(tr("insert_panel.lbl_regex")), 1, 7)

        # Dynamic condition rows (Task #5 - v2.9.7) - same as SearchReplacePanel
        self.cond_list: List[
            Tuple[QComboBox, QComboBox, QLineEdit, QComboBox, QLineEdit, QCheckBox, QCheckBox, QCheckBox, QPushButton]
        ] = []
        self.cond_grid = g3  # Store grid reference
        self.next_cond_row = 2  # Track next row (0=logic, 1=headers, 2+=conditions)

        # Buttons layout (v2.9.40.3: create BEFORE adding rows)
        self.buttons_layout_ref = QHBoxLayout()

        # Add initial 3 condition rows (minimum)
        for _ in range(3):
            self._add_condition_row()

        # Add Condition button
        btn_add_condition = QPushButton(tr("insert_panel.btn_add_condition"))
        btn_add_condition.setToolTip(tooltip_tr("insert_panel.tooltip_add_condition"))
        btn_add_condition.clicked.connect(self._add_condition_row)
        self.buttons_layout_ref.addWidget(btn_add_condition)

        # Clear All Conditions button (v2.9.5)
        btn_clear_conditions = QPushButton(tr("insert_panel.btn_clear_conditions"))
        btn_clear_conditions.setToolTip(tooltip_tr("insert_panel.tooltip_clear_conditions"))
        btn_clear_conditions.clicked.connect(self._clear_all_conditions)
        self.buttons_layout_ref.addWidget(btn_clear_conditions)

        self.buttons_layout_ref.addStretch()

        # Buttons already added to grid by _add_condition_row (v2.9.40.3)

        layout.addWidget(gb3, 9, 0, 1, 5)

        self.btn_apply = QPushButton(tr("insert_panel.btn_apply"))
        self.btn_apply.setToolTip(tooltip_tr("insert.tooltip_apply"))
        layout.addWidget(self.btn_apply, 10, 4)

        # Results on the right
        self.results = ResultsTree()

        # Results panel with save button
        results_layout = QVBoxLayout()
        results_header = QHBoxLayout()
        results_label = QLabel(tr("insert_panel.lbl_match_results"))
        results_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.btn_save_results = QPushButton(tr("insert_panel.btn_save_results"))
        self.btn_save_results.setToolTip(tooltip_tr("insert_panel.tooltip_save_results"))
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
        left_widget.setLayout(layout)
        scroll_area = QScrollArea()
        scroll_area.setWidget(left_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        splitter = QSplitter()
        splitter.addWidget(scroll_area)
        splitter.addWidget(results_widget)
        splitter.setSizes([500, 800])

        wroot = QVBoxLayout(self)
        wroot.setContentsMargins(0, 0, 0, 0)
        wroot.addWidget(splitter)

        self.is_file.stateChanged.connect(self.change_advanced_conditions)
        self.btn_browse.clicked.connect(self._browse)
        self.btn_apply.clicked.connect(self._apply)

    def change_advanced_conditions(self):
        self.enable_buttons(not self.is_file.isChecked(), include_buttons=False)

    def emit_insert_request(self):
        """
        Public method to emit insert_requested signal with current panel state.

        Useful for external consumers (e.g., ai_processor_dock, json_editor_tab)
        that want to perform insert operations on their own content using
        this panel's configuration.

        Returns:
            bool: True if signal was emitted, False if validation failed
        """
        try:
            # Get values from UI
            line_no = self.spin_line.value()
            text = self.ed_text.toPlainText().strip()
            mode = self.cb_mode.currentText()

            # Validation
            if not text:
                return False

            # Emit signal
            self.insert_requested.emit(line_no, text, mode)
            return True

        except Exception as e:
            logger.error(f"Failed to emit insert_requested: {e}")
            return False

    def _add_condition_row(self):
        """Add a new dynamic condition row (Task #5 - v2.9.7)"""
        row_i = self.next_cond_row

        # Create widgets
        cb_field = QComboBox()
        cb_field.addItems(["", "filename", "path", "ext", "size", "mtime", "content"])
        cb_field.currentTextChanged.connect(self._schedule_live_refresh)

        cb_op = QComboBox()
        cb_op.addItems(
            ["", "contains", "not contains", "equals", "not equals", "starts with", "ends with", ">", "<", ">=", "<="]
        )
        cb_op.currentTextChanged.connect(self._schedule_live_refresh)

        ed_val = QLineEdit()
        ed_val.textChanged.connect(self._schedule_live_refresh)

        cb_scope = QComboBox()
        cb_scope.addItems(["none", "brackets", "braces", "parentheses", "custom", "tag", "specific-tag"])
        cb_scope.currentTextChanged.connect(self._schedule_live_refresh)

        ed_scope_val = QLineEdit()
        ed_scope_val.setPlaceholderText(tr("insert_panel.placeholder_scope_param"))
        ed_scope_val.textChanged.connect(self._schedule_live_refresh)

        # Checkboxes for matching options
        chk_case = QCheckBox()
        chk_case.setChecked(True)  # Default: case sensitive
        chk_case.setToolTip(tooltip_tr("insert_panel.tooltip_case"))
        chk_case.stateChanged.connect(self._schedule_live_refresh)

        chk_word = QCheckBox()
        chk_word.setToolTip(tooltip_tr("insert_panel.tooltip_word"))
        chk_word.stateChanged.connect(self._schedule_live_refresh)

        chk_regex = QCheckBox()
        chk_regex.setToolTip(tooltip_tr("insert_panel.tooltip_regex"))
        chk_regex.stateChanged.connect(self._schedule_live_refresh)

        # Remove button (X)
        btn_remove = QPushButton(tr("insert_panel.btn_remove"))
        btn_remove.setFixedWidth(30)
        btn_remove.setToolTip(tooltip_tr("insert_panel.tooltip_remove_condition"))
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
                self, tr("insert_panel.warning_cannot_remove_title"), tr("insert_panel.warning_cannot_remove_msg")
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
        """Clear all advanced condition fields (v2.9.5, updated v2.9.7)"""
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
            path, _ = QFileDialog.getOpenFileName(
                self, "Select dictionary", "", "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
            )
            # self.enable_buttons(False, include_buttons = False)
        else:
            path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
            # self.enable_buttons(True, include_buttons = False)

        if path:
            self.ed_path.setText(path)


    def _conds(self) -> tuple[List[Condition], str]:
        """Return conditions and logic operator (AND/OR) - updated for v2.9.7"""
        out: List[Condition] = []
        if not self.is_file.isChecked():
            for widgets in self.cond_list:
                cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex = widgets[:8]
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

    def enable_buttons(self, state, include_buttons=True, include_advanced_conditions=True):
        if include_buttons:
            self.btn_browse.setEnabled(state)

        if include_advanced_conditions:
            for widgets in self.cond_list:
                cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex = widgets[:8]
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

    def reset_advanced_conditions(self):
        for widgets in self.cond_list:
            cb_field, cb_op, ed, cb_scope, ed_scope_val, chk_case, chk_word, chk_regex = widgets[:8]
            cb_field.setCurrentIndex(0)
            cb_op.setCurrentIndex(0)
            ed.clear()
            cb_scope.setCurrentIndex(0)
            ed_scope_val.clear()
            chk_case.setChecked(True)
            chk_word.setChecked(False)
            chk_regex.setChecked(False)

    def _snapshot_search_request(self) -> SearchFileRequest:
        """Read widget state once, before background discovery starts."""
        path = self.ed_path.text().strip()

        # v2.9.0, v2.9.1: Handle extension filter (optional)
        use_ext_filter = self.chk_use_ext_filter.isChecked()
        extensions_text = self.ed_extensions.text().strip() if use_ext_filter else ""
        ed_inc_text = self.ed_inc.text().strip()

        # Build include globs from extensions if enabled and provided
        if use_ext_filter and extensions_text:
            extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
            extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
            ext_globs = [f"*{ext}" for ext in extensions]

            if ed_inc_text:
                inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                inc.extend(ext_globs)
            else:
                inc = ext_globs
        else:
            if ed_inc_text:
                inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
            else:
                inc = ["*.*"]

        exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
        conditions, logic_operator = self._conds()
        return SearchFileRequest(
            root=path,
            include_globs=tuple(inc),
            exclude_globs=tuple(exc),
            conditions=tuple(
                SearchConditionRequest.from_condition(condition)
                for condition in conditions
            ),
            logic_operator=logic_operator,
        )

    def _iter_files(self) -> List[str]:
        """Return files synchronously for insertion and compatibility consumers."""
        return list(self._snapshot_search_request().iter_files())

    def _schedule_live_refresh(self):
        if not self._conds():  # only trigger if there's at least 1 valid rule
            return
        # Only do live preview when path is a directory:
        path_text = self.ed_path.text().strip()
        if not path_text or os.path.isfile(path_text):
            return
        self._debounce_timer.start()

    def _start_search_threaded(self):
        if self._operation_running():
            self.cancel_search()
            return

        words = "|".join(
            widgets[2].text().strip()
            for widgets in self.cond_list
            if widgets[2].text().strip()
        )
        if not words:
            return

        self.results.print_message("Loading...")
        try:
            pattern_text = SearchOptions(False, False, True).compile(rf"(?:{words})")
            request = self._snapshot_search_request()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.results.print_message(f"Invalid search: {exc}")
            logger.error("Insert search setup failed: %s", exc)
            return

        if self.progress_manager:
            import uuid

            self._current_task_id = f"insert_search_{uuid.uuid4().hex[:8]}"
            self._current_progress_widget = self.progress_manager.add_task(
                self._current_task_id, f"Match Search: {words[:30]}"
            )

        self._search_generation += 1
        generation = self._search_generation
        self._search_thread_id = f"insert_search:{id(self)}:{generation}"
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
        self._search_thread = QThread(self)
        self._search_worker = SearchWorker(
            pattern_text=pattern_text,
            iter_files_fn=request.iter_files,
            search_options_factory=lambda a, b, c: SearchOptions(a, b, c),
        )
        self._search_receiver = _InsertSearchReceiver(self, generation)
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
            FeatureType.INSERT,
            cancel_callback=worker.cancel,
            exclusive=False,
        ):
            worker.deleteLater()
            native.deleteLater()
            receiver.deleteLater()
            self._clear_search_references()
            self.results.print_message("Cannot start while the application is shutting down")
            return

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
        self.enable_buttons(False)
        native.start()

    def _operation_running(self):
        return self.processing_search or (
            self._search_thread is not None and self._search_thread.isRunning()
        )

    def cancel_search(self, generation=None):
        """Request cancellation without releasing controls before settlement."""
        if generation is not None and generation != self._search_generation:
            return
        if self._search_worker is None:
            return
        self._search_cancel_requested = True
        self._search_worker.cancel()

    def _set_search_paused(self, generation, paused):
        if generation != self._search_generation or self._search_worker is None:
            return
        self._search_worker.pause() if paused else self._search_worker.resume()

    def _on_search_progress(self, generation: int, current_path: str):
        """Legacy progress handler."""
        del current_path
        if generation != self._search_generation:
            return

    def _on_search_progress_detailed(
        self, generation: int, current: int, total: int, message: str
    ):
        """New detailed progress handler (v2.5.0)."""
        if generation != self._search_generation or self._discard_search_callbacks:
            return
        if self._current_progress_widget:
            self._current_progress_widget.update_progress(current, total, message)
            self._current_progress_widget.add_log(f"Processing: {message}")

    def _on_search_error(self, generation: int, msg: str):
        """Handle search errors."""
        if generation != self._search_generation or self._discard_search_callbacks:
            return
        if self._current_progress_widget:
            self._current_progress_widget.add_log(f"ERROR: {msg}")
        logger.error(msg)

    def _on_search_done(self, generation: int, matches: dict):
        """Handle search completion with history tracking (v2.5.0+)."""
        if (
            generation != self._search_generation
            or self._discard_search_callbacks
            or self._search_cancel_requested
        ):
            return
        sort_results = self.chk_sort_results.isChecked()
        self.results.populate(matches, sort_results)

        # Mark progress as complete (v2.5.0)
        if self._current_progress_widget:
            self._current_progress_widget.set_complete(success=True)
            self._current_progress_widget.add_log(f"Search completed: {len(matches)} files with matches")

        # Save to history (NEW - v2.5.0+)
        try:
            history = OperationHistory()
            history.add_operation(
                "insert_search",
                {
                    "path": self.ed_path.text(),
                    "files_matched": len(matches),
                    "total_matches": sum(len(items) for items in matches.values()),
                },
            )
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def _on_search_thread_finished(self, generation):
        """Release UI ownership only after native QThread settlement."""
        if generation != self._search_generation:
            return
        action = self._close_action
        self._close_action = None
        cancelled = self._search_cancel_requested
        self._clear_search_references()
        self.processing_search = False
        self.enable_buttons(
            True,
            include_advanced_conditions=not self.is_file.isChecked(),
        )
        if cancelled and self._current_progress_widget:
            self._current_progress_widget.set_complete(success=False)
            self._current_progress_widget.add_log("Search cancelled")
        if action:
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
        self._search_cancel_requested = False
        self._discard_search_callbacks = False
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

    def has_active_operation(self):
        """Expose bounded child ownership to a containing tool."""
        return self._operation_running()

    def request_parent_shutdown(self):
        """Cancel child work without independently closing the parent tab."""
        if not self._operation_running():
            return False
        self._discard_search_callbacks = True
        self.cancel_search()
        return True

    def closeEvent(self, event):
        if self._operation_running():
            self._close_action = ("close", self)
            self._discard_search_callbacks = True
            self.cancel_search()
            event.ignore()
            return
        super().closeEvent(event)

    def _files(self) -> List[str]:
        path = self.ed_path.text().strip()
        inc = [g.strip() for g in re.split(r"[;,]", self.ed_inc.text()) if g.strip()]
        exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
        files = list(walk_files(path, inc, exc))
        return filter_files_by_conditions(files, self._conds())

    def _find_line_by_query(self, text: str, query: str) -> List[int]:
        """
        Find line numbers matching the query.
        Returns list of 1-based line numbers.
        """
        if not query:
            return []

        case_sensitive = self.chk_lookup_case.isChecked()
        whole_word = self.chk_lookup_word.isChecked()
        use_regex = self.chk_lookup_regex.isChecked()

        lines = text.splitlines()
        matches = []

        for i, line in enumerate(lines, start=1):
            if self._line_matches_query(line, query, case_sensitive, whole_word, use_regex):
                matches.append(i)

        return matches

    def _line_matches_query(
        self, line: str, query: str, case_sensitive: bool, whole_word: bool, use_regex: bool
    ) -> bool:
        """
        Check if a line matches the query with given options.
        """
        try:
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = query
                if whole_word:
                    pattern = r"\b" + pattern + r"\b"
                return bool(re.search(pattern, line, flags))
            else:
                search_line = line if case_sensitive else line.lower()
                search_query = query if case_sensitive else query.lower()

                if whole_word:
                    pattern = r"\b" + re.escape(search_query) + r"\b"
                    flags = 0 if case_sensitive else re.IGNORECASE
                    return bool(re.search(pattern, line, flags))
                else:
                    return search_query in search_line
        except re.error:
            return False

    def _apply(self):
        query = self.ed_query.toPlainText().strip()
        manual_line = self.spin_line.value()
        insert_text = self.ed_text.toPlainText()
        mode = self.cb_mode.currentText()
        occurrence = self.cb_lookup_occurrence.currentText()

        count = 0
        skipped = 0

        for file_path in self._files():
            try:
                old = read_text(file_path)

                # Determine line number(s) to use
                if query:
                    # Use lookup/search mode
                    line_matches = self._find_line_by_query(old, query)

                    if not line_matches:
                        skipped += 1
                        continue

                    # Determine which occurrence to use
                    if occurrence == "First":
                        target_lines = [line_matches[0]]
                    elif occurrence == "Last":
                        target_lines = [line_matches[-1]]
                    else:  # "All"
                        target_lines = line_matches
                else:
                    # Use manual line number
                    target_lines = [manual_line]

                # Apply insertion to each target line
                new = old
                # When applying to multiple lines, process from bottom to top
                # to avoid line number shifts
                for line in sorted(target_lines, reverse=True):
                    new = insert_at_line(new, line, insert_text, mode)

                if new != old:
                    write_text(file_path, new)
                    count += 1
            except Exception as exc:
                logger.warning(f"{file_path}: {exc}")
                skipped += 1

        msg = f"Modified files: {count}"
        if skipped > 0:
            msg += f"\nSkipped files (no match): {skipped}"
        if query:
            msg += f"\n\nUsed search query: '{query}'"
            msg += f"\nOccurrence mode: {occurrence}"
        else:
            msg += f"\n\nUsed line number: {manual_line}"

        QMessageBox.information(self, tr("insert_panel.msg_insert_title"), msg)
        self._start_search_threaded()

    def _save_results(self):
        """Save match results to a text file."""
        matches_data = self.results.get_matches_data()

        if not matches_data:
            QMessageBox.information(
                self, tr("insert_panel.msg_no_results_title"), tr("insert_panel.msg_no_results_msg")
            )
            return

        # Ask user for file location
        default_filename = "clarify_insert_matches.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Match Results", default_filename, "Text Files (*.txt);;All Files (*)"
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
                tr("insert_panel.msg_results_saved_title"),
                f"Match results saved successfully!\n\n"
                f"File: {file_path}\n"
                f"Total files: {total_files}\n"
                f"Total matches: {total_matches}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, tr("insert_panel.msg_error_title"), tr("insert_panel.msg_error_save").format(str(e))
            )
