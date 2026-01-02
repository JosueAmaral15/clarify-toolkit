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

from __future__ import annotations
import os
import re
import sys
from typing import List, Tuple, Dict, Optional

# PySide6 imports
from PySide6.QtCore import Qt, Signal, QThread, QEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QPlainTextEdit,
    QGroupBox,
    QSplitter,
    QScrollArea,
    QFileDialog,
    QMessageBox,
)

from src.i18n.translator import tr, tooltip_tr

# Core functionality
from ...core import SearchOptions, preserve_case_like, replace_in_text, Condition, filter_files_by_conditions

# Utilities
from ...utils import walk_files, read_text, write_text, parse_exclusion_patterns

# Components from this package
from .results_tree import ResultsTree
from .search_worker import SearchWorker

# Progress management
from ..progress import OperationHistory

# Thread management
from ...ui import thread_manager, FeatureType, ProcessingModal


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
        self.progress_manager = progress_manager
        self._current_task_id = None
        self._processing_modal = None  # Modal de progresso

    def set_editor_fonts(self, font):
        """Set monospaced font for query and replacement editors (v2.9.115)."""
        self.ed_repl.setFont(font)
        self.ed_query.setFont(font)

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
        g = QGridLayout(gb)

        # File name query field
        g.addWidget(QLabel(tr("search_replace.lbl_file_name_query")), 0, 0)
        self.ed_filename_query = QLineEdit()
        self.ed_filename_query.setPlaceholderText(tr("search_replace.placeholder_filename"))
        self.ed_filename_query.setToolTip(tooltip_tr("search_replace.tooltip_filename_query"))
        g.addWidget(self.ed_filename_query, 0, 1, 1, 3)

        # File content query field
        g.addWidget(QLabel(tr("search_replace.lbl_file_content_query")), 1, 0)
        self.ed_query = QPlainTextEdit()
        self.ed_query.setMinimumHeight(30)
        self.ed_query.setMaximumHeight(150)
        self.ed_query.setPlaceholderText(tr("search_replace.placeholder_content"))
        self.ed_query.setToolTip(tooltip_tr("search_replace.tooltip_query"))
        g.addWidget(self.ed_query, 1, 1, 1, 3)

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

        g.addWidget(self.chk_case, 2, 0)
        g.addWidget(self.chk_word, 2, 1)
        g.addWidget(self.chk_regex, 2, 2)
        g.addWidget(self.chk_multi_query, 2, 3)  # v2.8.0
        g.addWidget(self.btn_search, 3, 3)  # Moved to row 3

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

        return super().eventFilter(obj, event)

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
            print(f"[ERROR] Failed to emit replace_requested: {e}")
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
                btn_remove,
            ) in self.cond_list:
                f = cb_field.currentText().strip()
                o = cb_op.currentText().strip()
                v = ed.text().strip()
                scope_type = cb_scope.currentText().strip()
                scope_val = ed_scope_val.text().strip()
                case_sensitive = chk_case.isChecked()
                whole_word = chk_word.isChecked()
                use_regex = chk_regex.isChecked()
                if f and o and v:
                    out.append(Condition(f, o, v, scope_type, scope_val, case_sensitive, whole_word, use_regex))
        logic_op = self.combo_logic_op.currentText()
        return out, logic_op

    def _iter_files(self) -> List[str]:
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
                inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
                inc.extend(ext_globs)
            else:
                inc = ext_globs
        else:
            # No extension filter, use include globs or default
            if ed_inc_text:
                inc = [g.strip() for g in re.split(r"[;,]", ed_inc_text) if g.strip()]
            else:
                inc = ["*.*"]  # Default: all files

        exc = [g.strip() for g in re.split(r"[;,]", self.ed_exc.text()) if g.strip()]
        files = list(walk_files(path, inc, exc))
        conds, logic_op = self._conds()
        return filter_files_by_conditions(files, conds, logic_op)

    # def _do_search(self):
    #     try:
    #         patt = SearchOptions(self.chk_case.isChecked(),
    #                              self.chk_word.isChecked(),
    #                              self.chk_regex.isChecked()).compile(self.ed_query.text())
    #     except ValueError as e:
    #         QMessageBox.critical(self, "Invalid pattern", str(e)); return

    #     matches: Dict[str, List[Tuple[int,int,str]]] = {}
    #     for p in self._iter_files():
    #         try:
    #             text = read_text(p)
    #             lst: List[Tuple[int,int,str]] = []
    #             for m in patt.finditer(text):
    #                 line = text.count("\n", 0, m.start()) + 1
    #                 col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
    #                 snippet = text.splitlines()[line-1]
    #                 lst.append((line, col, snippet))
    #             if lst:
    #                 matches[p] = lst
    #         except Exception as e:
    #             print(f"[WARN] {p}: {e}", file=sys.stderr)
    #     self.results.populate(matches)

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
                btn_remove,
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
        if not self.processing_search:
            # Check if feature is already running
            if not thread_manager.can_start_feature(FeatureType.SEARCH_REPLACE):
                QMessageBox.warning(
                    self, tr("search_replace.msg_already_running_title"), tr("search_replace.msg_already_running")
                )
                return

            self.results.print_message("Loading...")

            # v2.9.112: Get file name and content queries
            filename_query = self.ed_filename_query.text().strip()
            content_query = self.ed_query.toPlainText().strip()

            # Validate: at least one field must be filled
            if not filename_query and not content_query:
                QMessageBox.warning(self, tr("search_replace.msg_no_query_title"), tr("search_replace.msg_no_query"))
                self.results.print_message("Search cancelled: no query provided")
                return

            # Determine search mode
            search_mode = "both"  # Default
            if filename_query and not content_query:
                search_mode = "filename_only"
            elif content_query and not filename_query:
                search_mode = "content_only"

            # Get query text (v2.8.0 - support multi-query)
            is_multi_query = self.chk_multi_query.isChecked() and hasattr(self, "ed_query_multi")
            if is_multi_query:
                query_text = self.ed_query_multi.toPlainText()
            else:
                query_text = content_query

            # v2.8.0: Prepare multi-query processor or single pattern
            pattern_text = None
            multi_query_processor = None

            if is_multi_query:
                # Import and create MultiQueryProcessor
                from src.core.multi_query import MultiQueryProcessor

                try:
                    multi_query_processor = MultiQueryProcessor(
                        multi_line_text=query_text,
                        case_sensitive=self.chk_case.isChecked(),
                        whole_word=self.chk_word.isChecked(),
                        use_regex=self.chk_regex.isChecked(),
                    )
                    # Validate queries
                    is_valid, error_msg = multi_query_processor.validate()
                    if not is_valid:
                        self.error.emit(f"Invalid queries: {error_msg}")
                        self.done.emit({})
                        return

                    # Check if there are any queries
                    if multi_query_processor.get_query_count() == 0:
                        self.error.emit("No valid queries found. Add at least one search pattern.")
                        self.done.emit({})
                        return
                except Exception as e:
                    self.error.emit(f"Multi-query error: {e}")
                    self.done.emit({})
                    return
            else:
                # Single query mode - compile pattern (only if content_query exists)
                if search_mode != "filename_only":
                    try:
                        pattern_text = SearchOptions(
                            self.chk_case.isChecked(), self.chk_word.isChecked(), self.chk_regex.isChecked()
                        ).compile(query_text)
                    except Exception as e:
                        self.error.emit(f"Invalid pattern: {e}")
                        self.done.emit({})
                        return
                    self.error.emit(f"Invalid pattern: {e}")
                    self.done.emit({})
                    return

            # Create processing modal (v2.7.0, v2.8.0 - multi-query info)
            self._processing_modal = ProcessingModal(
                title="Search/Replace Processing", parent=self, show_progress=True, show_cancel=True
            )
            if is_multi_query:
                query_count = multi_query_processor.get_query_count()
                self._processing_modal.set_title(f"Searching Files ({query_count} queries)...")
                self._processing_modal.set_status(f"Initializing multi-query search with {query_count} patterns...")
            else:
                self._processing_modal.set_title("Searching Files...")
                self._processing_modal.set_status("Initializing search...")
            self._processing_modal.start_loading_animation()
            self._processing_modal.show()

            # Create progress bar (v2.5.0, v2.8.0) - mantido para compatibilidade
            if self.progress_manager:
                import uuid

                self._current_task_id = f"search_{uuid.uuid4().hex[:8]}"
                if is_multi_query:
                    query_count = multi_query_processor.get_query_count()
                    task_label = f"Multi-Search ({query_count} queries)"
                else:
                    task_label = f"Search: {self.ed_query.toPlainText().strip()[:30]}"
                self._current_progress_widget = self.progress_manager.add_task(self._current_task_id, task_label)

            # Create thread and worker (v2.8.0 - multi-query support, v2.9.112 - filename search)
            self._search_thread = QThread(self)
            self._search_worker = SearchWorker(
                pattern_text=pattern_text,
                iter_files_fn=self._iter_files,
                search_options_factory=lambda a, b, c: SearchOptions(a, b, c),
                is_multi_query=is_multi_query,
                multi_query_processor=multi_query_processor,
                search_mode=search_mode,
                filename_pattern=filename_query if filename_query else None,
            )
            self._search_worker.moveToThread(self._search_thread)

            # Register thread with ThreadManager
            import uuid

            thread_id = f"search_replace_{uuid.uuid4().hex[:8]}"
            if not thread_manager.start_thread(
                thread_id=thread_id,
                thread=self._search_thread,
                worker=self._search_worker,
                feature=FeatureType.SEARCH_REPLACE,
                cancel_callback=lambda: self._search_worker.cancel(),
            ):
                QMessageBox.warning(
                    self, tr("search_replace_panel.msg_error_thread_title"), tr("search_replace_panel.msg_error_thread")
                )
                if self._processing_modal:
                    self._processing_modal.close()
                    self._processing_modal = None
                return

            # Connections
            self._search_thread.started.connect(self._search_worker.run)
            self._search_worker.done.connect(self._on_search_done)
            self._search_worker.progress.connect(self._on_search_progress)
            self._search_worker.progress_detailed.connect(self._on_search_progress_detailed)  # v2.5.0
            self._search_worker.error.connect(self._on_search_error)

            # Connect cancel from modal to worker (v2.7.0)
            if self._processing_modal:
                self._processing_modal.cancel_requested.connect(lambda: self._search_worker.cancel())

            # Connect cancel and pause from progress bar to worker (v2.5.0+)
            if self._current_progress_widget:
                self._current_progress_widget.cancel_requested.connect(lambda _: self._search_worker.cancel())
                self._current_progress_widget.pause_requested.connect(
                    lambda _, paused: self._search_worker.pause() if paused else self._search_worker.resume()
                )

            # Cleanup
            self._search_worker.done.connect(self._search_thread.quit)
            self._search_worker.done.connect(self._search_worker.deleteLater)
            self._search_thread.finished.connect(self._search_thread.deleteLater)

            self._search_thread.start()
            self.enable_buttons(False)
            self.processing_search = True
        else:
            # Cancela processamento em andamento
            if self._search_worker:
                self._search_worker.cancel()
            self.enable_buttons(True, include_advanced_conditions=True if not self.is_file.isChecked() else False)
            self.processing_search = False

    def _on_search_progress(self, current_path: str):
        """Legacy progress handler - kept for compatibility."""
        pass

    def _on_search_progress_detailed(self, current: int, total: int, message: str):
        """New detailed progress handler (v2.5.0)."""
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

    def _on_search_error(self, msg: str):
        """Handle search errors."""
        # Update processing modal (v2.7.0)
        if self._processing_modal:
            self._processing_modal.log_message(f"ERROR: {msg}")

        # Update progress widget (v2.5.0) - mantido para compatibilidade
        if self._current_progress_widget:
            self._current_progress_widget.add_log(f"ERROR: {msg}")
        print(msg)

    def _on_search_done(self, matches: dict):
        """Handle search completion with history tracking (v2.5.0+)."""
        sort_results = self.chk_sort_results.isChecked()
        self.results.populate(matches, sort_results)
        self.enable_buttons(True, include_advanced_conditions=True if not self.is_file.isChecked() else False)
        self.processing_search = False

        # Mark processing modal as complete (v2.7.0)
        if self._processing_modal:
            self._processing_modal.mark_completed(
                success=True, message=f"Search completed successfully!\nFound matches in {len(matches)} file(s)."
            )
            # Modal remains open for user to review logs and close manually

        # Mark progress as complete (v2.5.0)
        if self._current_progress_widget:
            self._current_progress_widget.set_complete(success=True)
            self._current_progress_widget.add_log(f"Search completed: {len(matches)} files with matches")

        # Save to history (NEW - v2.5.0+, v2.9.6 - HistoryDock integration)
        try:
            history = OperationHistory()
            query_text = self.ed_query.toPlainText().strip()
            total_matches = sum(len(items) for items in matches.values())

            history.add_operation(
                "search",
                {
                    "query": query_text,
                    "path": self.ed_path.text(),
                    "files_matched": len(matches),
                    "total_matches": total_matches,
                    "case_sensitive": self.chk_case.isChecked(),
                    "whole_word": self.chk_word.isChecked(),
                    "regex": self.chk_regex.isChecked(),
                },
            )

            # Add to History Dock (v2.9.6)
            if hasattr(self, "dock_history"):
                self.dock_history.add_operation(
                    "Search", {"query": query_text, "files_processed": len(matches), "matches_found": total_matches}
                )
        except Exception as e:
            print(f"Failed to save history: {e}")

        # Don't auto-remove progress bar - let user close it manually

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
                print(f"[WARN] {p}: {e}", file=sys.stderr)

        # Add to History Dock (v2.9.6)
        try:
            if hasattr(self, "dock_history"):
                self.dock_history.add_operation(
                    "Replace",
                    {"query": self.ed_query.toPlainText().strip(), "replacement": repl, "files_processed": count_files},
                )
        except Exception as e:
            print(f"Failed to save to history dock: {e}")

        QMessageBox.information(
            self,
            tr("search_replace.msg_replace_title"),
            tr("search_replace.msg_replace_success").format(count=count_files),
        )
        self.results.print_message()
