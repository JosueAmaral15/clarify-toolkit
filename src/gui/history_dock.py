#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
History Dock - Operation History Viewer

Displays a log of recent operations (search, replace, insert, translate, rewrite)
with timestamps, operation type, and files processed.

Features:
- Maintains up to 10 recent operations (configurable)
- Shows timestamp, operation type, query/text, and file count
- Toggleable via View → History menu
- Clear history button
- Export history to text file
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QFileDialog, QMessageBox
)
from .base_dock import BaseDock
from src.i18n.translator import tooltip_tr, tr


class HistoryDock(BaseDock):
    """
    Dock widget for viewing operation history.

    Tracks operations:
    - Search: query, files searched, matches found
    - Replace: query, replacement, files modified
    - Insert: text, mode, files modified
    - JSON Translate: dictionary file, files processed
    - JSON Rewriter: input file, transformations applied

    Maximum history entries: 10 (configurable)
    """

    # Signal emitted when history is cleared
    history_cleared = Signal()

    def __init__(self, parent: QWidget | None = None, max_entries: int = 10):
        self.max_entries = max_entries
        self.history: List[Dict[str, Any]] = []
        super().__init__("Operation History", parent)

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()  # v2.9.68

    def _create_widgets(self) -> None:
        """Create all widgets for the history dock."""
        # Header label
        self.lbl_header = QLabel(f"Recent Operations (max {self.max_entries} entries)")
        self.lbl_header.setStyleSheet("font-weight: bold; padding: 5px;")

        # Tree widget for history display
        self.tree_history = QTreeWidget()
        self.tree_history.setHeaderLabels([tr("history_dock.header_time"), tr("history_dock.header_operation"), tr("history_dock.header_details"), tr("history_dock.header_files")])
        self.tree_history.setColumnWidth(0, 150)  # Timestamp
        self.tree_history.setColumnWidth(1, 100)  # Operation type
        self.tree_history.setColumnWidth(2, 300)  # Details
        self.tree_history.setColumnWidth(3, 80)   # File count
        self.tree_history.setAlternatingRowColors(True)
        self.tree_history.setRootIsDecorated(False)

        # Prevent horizontal expansion from long details (v2.9.117)
        self.tree_history.setWordWrap(False)
        self.tree_history.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.tree_history.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        header = self.tree_history.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)  # Details column stretches

        # Action buttons
        self.btn_clear = QPushButton(tr("history.btn_clear"))
        self.btn_export = QPushButton(tr("history.btn_export"))
        self.btn_refresh = QPushButton(tr("history.btn_refresh"))

    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.lbl_header)
        main_layout.addWidget(self.tree_history)
        main_layout.addLayout(btn_layout)

        self.main_widget.setLayout(main_layout)

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips to all widgets (v2.9.68)."""
        # Header
        self.lbl_header.setToolTip(tooltip_tr("history.lbl_header"))

        # Tree widget
        self.tree_history.setToolTip(tooltip_tr("history.tree_history"))

        # Action buttons
        self.btn_clear.setToolTip(tooltip_tr("history.btn_clear"))
        self.btn_export.setToolTip(tooltip_tr("history.btn_export"))
        self.btn_refresh.setToolTip(tooltip_tr("history.btn_refresh"))

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_clear.clicked.connect(self._clear_history)
        self.btn_export.clicked.connect(self._export_history)
        self.btn_refresh.clicked.connect(self._refresh_display)

    # Public API

    def add_operation(self, operation_type: str, details: Dict[str, Any]) -> None:
        """
        Add a new operation to history.

        Args:
            operation_type: Type of operation (Search, Replace, Insert, Translate, Rewrite)
            details: Dictionary with operation details:
                - query: Search query or text content
                - replacement: Replacement text (for Replace)
                - files_processed: Number of files affected
                - matches_found: Number of matches (for Search)
                - mode: Insert mode (for Insert)
                - dictionary: Dictionary file path (for Translate)
                - transformations: List of transformations (for Rewriter)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "timestamp": timestamp,
            "operation": operation_type,
            "details": details
        }

        # Add to history (FIFO with max_entries limit)
        self.history.insert(0, entry)
        if len(self.history) > self.max_entries:
            self.history = self.history[:self.max_entries]

        # Update display
        self._refresh_display()

    def get_history(self) -> List[Dict[str, Any]]:
        """Return copy of history list."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear all history entries."""
        self._clear_history()

    # Private Methods

    def _clear_history(self) -> None:
        """Clear history and update display."""
        if not self.history:
            QMessageBox.information(self, tr("history.msg_empty_title"), tr("history.msg_already_empty"))
            return

        reply = QMessageBox.question(
            self, tr("history.msg_confirm_clear_title"),
            tr("history.msg_confirm_clear_msg"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.history.clear()
            self._refresh_display()
            self.history_cleared.emit()

    def _export_history(self) -> None:
        """Export history to text file."""
        if not self.history:
            QMessageBox.information(self, tr("history.msg_empty_title"), tr("history.msg_no_history"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "clarify_history.txt",
            "Text files (*.txt);;All files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("CLARIFY OPERATION HISTORY\n")
                f.write("=" * 80 + "\n\n")

                for entry in self.history:
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Operation: {entry['operation']}\n")

                    details = entry['details']
                    if 'query' in details:
                        f.write(f"Query: {details['query']}\n")
                    if 'replacement' in details:
                        f.write(f"Replacement: {details['replacement']}\n")
                    if 'mode' in details:
                        f.write(f"Mode: {details['mode']}\n")
                    if 'dictionary' in details:
                        f.write(f"Dictionary: {details['dictionary']}\n")
                    if 'transformations' in details:
                        f.write(f"Transformations: {', '.join(details['transformations'])}\n")
                    if 'files_processed' in details:
                        f.write(f"Files Processed: {details['files_processed']}\n")
                    if 'matches_found' in details:
                        f.write(f"Matches Found: {details['matches_found']}\n")

                    f.write("-" * 80 + "\n\n")

            QMessageBox.information(self, tr("history.msg_exported_title"), tr("history.msg_exported_msg").format(file_path))
        except Exception as e:
            QMessageBox.critical(self, tr("history.msg_export_error_title"), tr("history.msg_export_error_msg").format(str(e)))

    def _refresh_display(self) -> None:
        """Refresh the tree widget display."""
        self.tree_history.clear()

        for entry in self.history:
            timestamp = entry['timestamp']
            operation = entry['operation']
            details = entry['details']

            # Format details string
            detail_parts = []
            if 'query' in details:
                query_preview = details['query'][:50] + ("..." if len(details['query']) > 50 else "")
                detail_parts.append(f"Query: {query_preview}")
            if 'replacement' in details:
                repl_preview = details['replacement'][:30] + ("..." if len(details['replacement']) > 30 else "")
                detail_parts.append(f"→ {repl_preview}")
            if 'mode' in details:
                detail_parts.append(f"Mode: {details['mode']}")
            if 'dictionary' in details:
                import os
                dict_name = os.path.basename(details['dictionary'])
                detail_parts.append(f"Dict: {dict_name}")
            if 'transformations' in details:
                trans = ', '.join(details['transformations'])
                detail_parts.append(f"Trans: {trans}")
            if 'matches_found' in details:
                detail_parts.append(f"Matches: {details['matches_found']}")

            details_str = " | ".join(detail_parts)
            files_count = str(details.get('files_processed', '-'))

            # Truncate long details to prevent horizontal expansion (v2.9.117)
            details_display = details_str
            if len(details_str) > 100:
                details_display = details_str[:100] + "..."

            # Create tree item
            item = QTreeWidgetItem([timestamp, operation, details_display, files_count])
            # Add full details as tooltip if truncated
            if len(details_str) > 100:
                item.setToolTip(2, details_str)
            self.tree_history.addTopLevelItem(item)

        # Update header
        self.lbl_header.setText(f"Recent Operations ({len(self.history)}/{self.max_entries} entries)")

    def _execute_action(self) -> None:
        """Execute the main action (refresh display)."""
        self._refresh_display()
