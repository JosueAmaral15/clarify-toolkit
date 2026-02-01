"""
Results Tree Widget for Clarify
--------------------------------
Tree view for displaying search results similar to VS Code.
Supports context menu, copy operations, and file opening.

Phase 3.11 - Import Tree Analogy: FOLHA
Esta é uma FOLHA na árvore de importações:
- Não importa arquivos do projeto
- Importa apenas bibliotecas externas (PySide6, sys, os)
- Fornece funcionalidade atômica (widget especializado)
- Totalmente reutilizável e testável

Author: Josué Amaral
Date: 2025-12-24
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness

import os
import subprocess
import sys

from typing import Dict, List, Tuple

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMenu, QMessageBox,
    QTreeWidget, QTreeWidgetItem
)

from src.i18n.translator import tr


class ResultsTree(QTreeWidget):
    """
    Tree view similar to VS Code's search results:
        File
          line:col  text preview
    v2.9.2: Added context menu with copy, select all, open file(s) and multi-selection support.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels([tr("results_tree.header_match")])
        self.setRootIsDecorated(True)
        self.setColumnCount(1)
        self.setUniformRowHeights(True)
        self._matches_data: Dict[str, List[Tuple[int, int, str]]] = {}

        # Enable multi-selection with CTRL/Shift (v2.9.2)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)

        # Enable context menu (v2.9.2)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Enable mouse tracking for hover effects (v2.5.1)
        self.setMouseTracking(True)
        self.itemEntered.connect(self._on_item_hover)

        # Status label at bottom of tree (v2.5.1)
        self._status_label = None  # Will be set by parent

    def set_status_label(self, label):
        """Set the status label widget for showing position info (v2.5.1)."""
        self._status_label = label

    def _on_item_hover(self, item: QTreeWidgetItem, _column: int):
        """Show position info when hovering over match items (v2.5.1)."""
        if item and item.parent():  # This is a match item (has parent = file item)
            text = item.text(0)
            # Extract line:col from the beginning of text
            if ":" in text:
                try:
                    pos_part = text.split()[0]  # Get "line:col" part
                    line, col = pos_part.split(":")

                    # Get file path from parent
                    file_path = item.parent().text(0)

                    # Set tooltip
                    tooltip = f"File: {file_path}\nLine: {line}\nColumn: {col}"
                    item.setToolTip(0, tooltip)

                    # Update status label if available
                    if self._status_label:
                        self._status_label.setText(
                            f"📍 Position: Line {line}, Column {col} | File: {file_path}"
                        )
                except Exception:
                    pass
        else:
            # Clear status for non-match items
            if self._status_label:
                self._status_label.setText("")

    def populate(self, matches: Dict[str, List[Tuple[int, int, str]]], sort_results: bool = False):
        """Populate tree with search results."""
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._matches_data = matches  # Store for export

            # Calculate statistics
            total_files = len(matches)
            total_matches = sum(len(items) for items in matches.values())

            # Add summary header at the top
            if total_files > 0:
                summary = QTreeWidgetItem([f"📊 Results: {total_matches} matches in {total_files} file(s)"])
                summary.setForeground(0, QColor(0, 150, 0))  # Green color
                font = summary.font(0)
                font.setBold(True)
                summary.setFont(0, font)
                self.addTopLevelItem(summary)

            # Sort file paths if requested (v2.9.5)
            paths = sorted(matches.keys()) if sort_results else matches.keys()

            # Add file matches
            for path in paths:
                items = matches[path]
                top = QTreeWidgetItem([path])
                self.addTopLevelItem(top)

                # Sort items by line number if requested
                if sort_results:
                    items = sorted(items, key=lambda x: (x[0], x[1]))  # Sort by line, then col

                for line, col, snippet in items:
                    leaf = QTreeWidgetItem([f"{line}:{col}  {snippet.strip()}"])
                    top.addChild(leaf)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)

    def print_message(self, message: str = ""):
        """Display a simple message in the tree."""
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._matches_data = {}  # Clear data when showing message
            top = QTreeWidgetItem([message])
            self.addTopLevelItem(top)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)

    def get_matches_data(self) -> Dict[str, List[Tuple[int, int, str]]]:
        """Return current matches data for export."""
        return self._matches_data

    def export_to_text(self) -> str:
        """
        Export matches to formatted text string.
        Returns empty string if no matches.
        """
        if not self._matches_data:
            return ""

        lines = []
        total_files = len(self._matches_data)
        total_matches = sum(len(items) for items in self._matches_data.values())

        # Header
        lines.append("=" * 80)
        lines.append("CLARIFY - SEARCH RESULTS")
        lines.append("=" * 80)
        lines.append(f"Total files with matches: {total_files}")
        lines.append(f"Total matches: {total_matches}")
        lines.append("=" * 80)
        lines.append("")

        # Results by file
        for file_path, items in self._matches_data.items():
            lines.append(f"📁 {file_path}")
            lines.append(f"   Matches: {len(items)}")
            lines.append("-" * 80)

            for line_num, col, snippet in items:
                lines.append(f"   Line {line_num}, Col {col}:")
                lines.append(f"      {snippet.strip()}")

            lines.append("")

        return "\n".join(lines)

    def _show_context_menu(self, position):
        """Show context menu at cursor position (v2.9.2)."""
        menu = QMenu(self)

        # Get selected items
        selected_items = self.selectedItems()
        has_selection = len(selected_items) > 0

        # Copy action
        copy_action = menu.addAction("📋 Copy")
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(self._copy_selected)

        # Copy all action
        copy_all_action = menu.addAction("📋 Copy All Results")
        copy_all_action.setEnabled(bool(self._matches_data))
        copy_all_action.triggered.connect(self._copy_all)

        menu.addSeparator()

        # Select all action
        select_all_action = menu.addAction("✅ Select All")
        select_all_action.triggered.connect(self.selectAll)

        menu.addSeparator()

        # Open file(s) actions
        open_file_action = menu.addAction("📂 Open File")
        open_file_action.setEnabled(has_selection)
        open_file_action.triggered.connect(self._open_selected_files)

        open_all_action = menu.addAction("📂 Open All Files")
        open_all_action.setEnabled(bool(self._matches_data))
        open_all_action.triggered.connect(self._open_all_files)

        # Show menu at cursor position
        menu.exec_(self.mapToGlobal(position))

    def _copy_selected(self):
        """Copy selected items to clipboard (v2.9.2)."""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        lines = []
        for item in selected_items:
            # Skip summary header
            if item.text(0).startswith("📊 Results:"):
                continue

            # If it's a file item (no parent)
            if not item.parent():
                lines.append(f"\n📁 {item.text(0)}")
                lines.append("-" * 80)
            # If it's a match item (has parent)
            else:
                lines.append(f"   {item.text(0)}")

        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Show feedback
        if self._status_label:
            self._status_label.setText(f"✅ Copied {len(selected_items)} item(s) to clipboard")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _copy_all(self):
        """Copy all results to clipboard (v2.9.2)."""
        text = self.export_to_text()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            # Show feedback
            if self._status_label:
                total_matches = sum(len(items) for items in self._matches_data.values())
                self._status_label.setText(f"✅ Copied all results ({total_matches} matches) to clipboard")
                QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_selected_files(self):
        """Open selected files in system default application (v2.9.2)."""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Collect unique file paths from selection
        file_paths = set()
        for item in selected_items:
            # Skip summary header
            if item.text(0).startswith("📊 Results:"):
                continue

            # If it's a file item (no parent), use it directly
            if not item.parent():
                file_paths.add(item.text(0))
            # If it's a match item, get parent file path
            else:
                parent_text = item.parent().text(0)
                if not parent_text.startswith("📊"):
                    file_paths.add(parent_text)

        # Open each file
        opened_count = 0
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    if sys.platform.startswith("darwin"):
                        subprocess.run(["open", path], check=False)
                    elif os.name == "nt":
                        subprocess.run(["cmd", "/c", "start", "", path], check=False)
                    else:
                        subprocess.run(["xdg-open", path], check=False)
                    opened_count += 1
                except Exception as e:
                    print(f"Error opening {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_all_files(self):
        """Open all files from results in system default application (v2.9.2)."""
        if not self._matches_data:
            return

        # Ask for confirmation if many files
        file_count = len(self._matches_data)
        if file_count > 10:
            reply = QMessageBox.question(
                self,
                "Open Many Files",
                f"You are about to open {file_count} files. Continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        # Open each file
        opened_count = 0
        for path in self._matches_data.keys():
            if os.path.isfile(path):
                try:
                    if sys.platform.startswith("darwin"):
                        subprocess.run(["open", path], check=False)
                    elif os.name == "nt":
                        subprocess.run(["cmd", "/c", "start", "", path], check=False)
                    else:
                        subprocess.run(["xdg-open", path], check=False)
                    opened_count += 1
                except Exception as e:
                    print(f"Error opening {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))
