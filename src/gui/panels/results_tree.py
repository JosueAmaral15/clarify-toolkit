"""
Results tree widget for displaying search matches.
Extracted from app.py (v2.9.114 - Phase 1.2).
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=invalid-name  # Qt method names
# pylint: disable=import-outside-toplevel  # Lazy imports
# pylint: disable=protected-access  # Access to MainWindow internals
# pylint: disable=logging-fstring-interpolation  # Performance not critical
# pylint: disable=subprocess-run-check  # Open commands don't need check

import os
import sys

from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QTimer, QModelIndex, QRect
from PySide6.QtGui import QColor, QPainter, QTextDocument
from PySide6.QtWidgets import (
    QApplication, QHeaderView, QMenu,
    QMessageBox, QStyledItemDelegate, QStyle,
    QStyleOptionViewItem, QTreeWidget, QTreeWidgetItem
)

from ...i18n import tr
from ...utils.logger import get_logger

logger = get_logger(__name__)

ITEM_TYPE_ROLE = int(Qt.ItemDataRole.UserRole)
PATH_ROLE = ITEM_TYPE_ROLE + 1
RESULT_PATH_ROLE = ITEM_TYPE_ROLE + 2
MATCH_DATA_ROLE = ITEM_TYPE_ROLE + 3

ITEM_TYPE_SUMMARY = "summary"
ITEM_TYPE_ROOT = "root"
ITEM_TYPE_DIRECTORY = "directory"
ITEM_TYPE_FILE = "file"
ITEM_TYPE_MATCH = "match"
ITEM_TYPE_MESSAGE = "message"


class WordWrapDelegate(QStyledItemDelegate):
    """Custom delegate to enable word wrap in QTreeWidget items (v2.9.118)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._word_wrap_enabled = False

    def set_word_wrap(self, enabled: bool):
        """Enable or disable word wrap."""
        self._word_wrap_enabled = enabled

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """Custom paint to support word wrap using QTextDocument."""
        if self._word_wrap_enabled:
            text = index.data(Qt.ItemDataRole.DisplayRole)
            if text:
                painter.save()

                # Draw background
                if option.state & QStyle.StateFlag.State_Selected:
                    painter.fillRect(option.rect, option.palette.highlight())

                # Create QTextDocument for proper text rendering with word wrap
                doc = QTextDocument()
                doc.setDefaultFont(option.font)

                # Remove trailing/leading whitespace and newlines to prevent extra spacing
                clean_text = text.strip().replace("\n", " ")
                doc.setPlainText(clean_text)

                # Use actual tree widget width instead of option.rect.width()
                tree = self.parent()
                if tree and hasattr(tree, "viewport"):
                    available_width = tree.viewport().width() - 40  # Subtract scrollbar + margins
                else:
                    available_width = option.rect.width() - 8 if option.rect.width() > 0 else 400

                doc.setTextWidth(available_width)

                # Remove spacing between blocks (paragraphs)
                doc.setDocumentMargin(0)

                # Set text color based on selection
                if option.state & QStyle.StateFlag.State_Selected:
                    painter.setPen(option.palette.highlightedText().color())
                else:
                    painter.setPen(option.palette.text().color())

                # Translate painter to draw position (no extra offset for tight spacing)
                painter.translate(option.rect.left(), option.rect.top())

                # Draw the text document
                doc.drawContents(painter)

                painter.restore()
                return

        # Default painting
        super().paint(painter, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        """Calculate size hint with word wrap using QTextDocument."""
        if self._word_wrap_enabled:
            text = index.data(Qt.ItemDataRole.DisplayRole)
            if text:
                # Use QTextDocument to calculate proper wrapped text height
                doc = QTextDocument()
                doc.setDefaultFont(option.font)

                # Remove trailing/leading whitespace and newlines to prevent extra spacing
                clean_text = text.strip().replace("\n", " ")
                doc.setPlainText(clean_text)

                # Use actual tree widget width instead of option.rect.width()
                tree = self.parent()
                if tree and hasattr(tree, "viewport"):
                    available_width = tree.viewport().width() - 40  # Subtract scrollbar + margins
                else:
                    available_width = option.rect.width() - 8 if option.rect.width() > 0 else 400

                doc.setTextWidth(available_width)

                # Remove spacing between blocks
                doc.setDocumentMargin(0)

                # Return FULL document height to accommodate all wrapped lines
                size = doc.size()
                height = int(size.height()) + 4  # Add small padding for readability
                return QRect(0, 0, int(size.width()) + 8, height).size()
        else:
            # When word wrap is OFF, also use compact height
            return QRect(0, 0, option.rect.width(), option.fontMetrics.height() + 4).size()

        return super().sizeHint(option, index)


class ResultsTree(QTreeWidget):
    """
    Tree view similar to VS Code's search results displaying:
        File
          line:col  text preview

    Features:
    - v2.5.1: Mouse hover with position info, status label integration
    - v2.9.2: Context menu with copy, select all, open file(s), multi-selection support
    - v2.9.5: Optional sorting by file path and line number
    """

    def __init__(self, parent=None, main_window=None):
        """
        Initialize results tree.

        Args:
            parent: Parent widget
            main_window: Optional explicit reference to main window (v2.9.121 bugfix)
        """
        super().__init__(parent)
        self._main_window_ref = main_window  # Store explicit main window reference
        self.setHeaderLabels([tr("results_tree.header_match")])
        self.setRootIsDecorated(True)
        self.setColumnCount(1)
        self.setUniformRowHeights(True)
        self.setStyleSheet(
            """
            QTreeWidget::item {
                padding-top: 0px;
                padding-bottom: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
            }
        """
        )
        self._matches_data: Dict[str, List[Tuple[int, int, str]]] = {}
        self._word_wrap_enabled = False  # Default: no word wrap

        # Word wrap disabled by default - allow horizontal scroll (v2.9.117)
        self.setWordWrap(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Use Interactive mode to allow horizontal scroll when word wrap is off
        # This fixes: path truncation, scroll bar not appearing, word wrap not working
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)

        # Set initial column width (user can resize manually)
        self.setColumnWidth(0, 800)  # Wider default for long paths

        # Allow manual resize
        self.header().setSectionsClickable(True)
        self.header().setSectionsMovable(False)

        # Set size policy to allow expansion
        from PySide6.QtWidgets import QSizePolicy

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(300)

        # Enable multi-selection with CTRL/Shift (v2.9.2)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)

        # Enable context menu (v2.9.2)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # DISABLED: Mouse tracking causes horizontal scrolling/jumping when hovering
        # The itemEntered signal triggers updates that affect column width
        # self.setMouseTracking(True)
        # self.itemEntered.connect(self._on_item_hover)

        # Status label at bottom of tree (v2.5.1)
        self._status_label = None  # Will be set by parent

        # Tree hierarchy state. Display text stays human-friendly; full paths live in item data.
        self._base_path: Optional[str] = None
        self._summary_item: Optional[QTreeWidgetItem] = None
        self._tree_root_item: Optional[QTreeWidgetItem] = None
        self._directory_items: Dict[str, QTreeWidgetItem] = {}

        # Custom delegate for word wrap (v2.9.118)
        self._delegate = WordWrapDelegate(self)
        self.setItemDelegate(self._delegate)

    def set_status_label(self, label):
        """Set the status label widget for showing position info (v2.5.1)."""
        self._status_label = label

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts like CTRL+C for copy."""
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._copy_selected()
            event.accept()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle resize to update word wrap when panel width changes."""
        super().resizeEvent(event)
        # Force recalculation of item heights when resizing with word wrap enabled
        if self._word_wrap_enabled:
            self.scheduleDelayedItemsLayout()
            self.viewport().update()

    def clear(self):  # pylint: disable=invalid-name  # Qt override
        """Clear visible items and internal result lookup state."""
        super().clear()
        if hasattr(self, "_matches_data"):
            self._matches_data = {}
        if hasattr(self, "_summary_item"):
            self._summary_item = None
        if hasattr(self, "_tree_root_item"):
            self._tree_root_item = None
        if hasattr(self, "_directory_items"):
            self._directory_items = {}

    def set_base_path(self, base_path: Optional[str]):
        """Set the preferred root path for hierarchical display."""
        self._base_path = self._normalize_path(base_path) if base_path else None

    def set_word_wrap(self, enabled: bool):
        """Toggle word wrap mode (v2.9.118 - fixed with custom delegate)."""
        self._word_wrap_enabled = enabled
        self.setWordWrap(enabled)

        # Update delegate
        self._delegate.set_word_wrap(enabled)

        if enabled:
            # Word wrap ON: Stretch to fit panel width and wrap text
            self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # Allow variable height for wrapped text
            self.setUniformRowHeights(False)
            # Tight spacing - no padding or margin
            self.setStyleSheet(
                """
                QTreeWidget::item {
                    padding-top: 0px;
                    padding-bottom: 0px;
                    margin-top: 0px;
                    margin-bottom: 0px;
                }
            """
            )
        else:
            # Word wrap OFF: use Interactive to allow horizontal scroll
            self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setColumnWidth(0, 800)  # Reset to default width
            # Back to uniform for performance
            self.setUniformRowHeights(True)
            # Tight spacing - no padding or margin
            self.setStyleSheet(
                """
                QTreeWidget::item {
                    padding-top: 0px;
                    padding-bottom: 0px;
                    margin-top: 0px;
                    margin-bottom: 0px;
                }
            """
            )

        # Refresh display if there's data
        if self._matches_data:
            self.populate(self._matches_data, sort_results=False, base_path=self._base_path)
            # Force viewport update
            self.viewport().update()

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Return an absolute normalized path without changing Unicode characters."""
        try:
            return os.path.abspath(os.path.normpath(os.fspath(path)))
        except (OSError, TypeError, ValueError):
            return os.path.normpath(str(path))

    @staticmethod
    def _display_name(path: str) -> str:
        """Return a compact label for a path, preserving roots such as '/'."""
        normalized = os.path.normpath(path)
        return os.path.basename(normalized) or normalized

    def _resolve_root_path(self, paths: List[str], base_path: Optional[str] = None) -> Optional[str]:
        """Resolve the tree root from an explicit base path or common result parent."""
        if base_path:
            return self._normalize_path(base_path)

        if self._base_path:
            return self._base_path

        if not paths:
            return None

        candidate_dirs = []
        for path in paths:
            normalized = self._normalize_path(path)
            if os.path.isdir(normalized):
                candidate_dirs.append(normalized)
            else:
                candidate_dirs.append(os.path.dirname(normalized) or normalized)

        try:
            root_path = os.path.commonpath(candidate_dirs)
        except ValueError:
            root_path = candidate_dirs[0]

        return root_path or os.path.abspath(os.curdir)

    def _set_item_metadata(
        self,
        item: QTreeWidgetItem,
        item_type: str,
        path: Optional[str] = None,
        result_path: Optional[str] = None,
        match_data: Optional[Tuple[int, int, str]] = None,
    ):
        """Attach stable metadata so actions never depend on visible labels."""
        item.setData(0, ITEM_TYPE_ROLE, item_type)
        if path:
            item.setData(0, PATH_ROLE, path)
            item.setToolTip(0, path)
        if result_path:
            item.setData(0, RESULT_PATH_ROLE, result_path)
            item.setToolTip(0, result_path)
        if match_data is not None:
            item.setData(0, MATCH_DATA_ROLE, match_data)

    def _item_type(self, item: Optional[QTreeWidgetItem]) -> Optional[str]:
        """Return the metadata item type."""
        if not item:
            return None
        return item.data(0, ITEM_TYPE_ROLE)

    def _is_summary_item(self, item: QTreeWidgetItem) -> bool:
        """Return True if item is the summary header."""
        item_type = self._item_type(item)
        return item_type == ITEM_TYPE_SUMMARY or item.text(0).startswith(("📊 Results:", "Results:"))

    def _result_path_for_item(self, item: Optional[QTreeWidgetItem]) -> Optional[str]:
        """Return the full result path represented by item or its result parent."""
        current = item
        while current is not None:
            result_path = current.data(0, RESULT_PATH_ROLE)
            if result_path:
                return result_path
            current = current.parent()

        if item and not item.parent() and not self._is_summary_item(item):
            text = item.text(0)
            if text and os.path.exists(text):
                return text
        return None

    def _collect_selected_result_paths(self, preserve_order: bool = False):
        """Collect unique full paths represented by current selection."""
        selected_items = self.selectedItems()
        if not selected_items:
            return [] if preserve_order else set()

        paths = []
        seen = set()
        for item in selected_items:
            if self._is_summary_item(item) or self._item_type(item) in {ITEM_TYPE_ROOT, ITEM_TYPE_MESSAGE}:
                continue
            path = self._result_path_for_item(item)
            if path and path not in seen:
                seen.add(path)
                paths.append(path)

        return paths if preserve_order else set(paths)

    def _root_label(self, root_path: str) -> str:
        """Build the visible root node label."""
        name = self._display_name(root_path)
        return tr("results_tree.root_label", "Root: {0}").format(name)

    def _ensure_summary(self, total_files: int, total_matches: int):
        """Create or update the summary header."""
        if total_files <= 0:
            return

        label = f"Results: {total_matches} matches in {total_files} file(s)"
        if self._summary_item is None:
            self._summary_item = QTreeWidgetItem([label])
            self._set_item_metadata(self._summary_item, ITEM_TYPE_SUMMARY)
            self.addTopLevelItem(self._summary_item)
        else:
            self._summary_item.setText(0, label)

        self._summary_item.setForeground(0, QColor(0, 150, 0))
        font = self._summary_item.font(0)
        font.setBold(True)
        self._summary_item.setFont(0, font)

    def _ensure_tree_root(self, root_path: str) -> QTreeWidgetItem:
        """Create the display root node if needed."""
        root_path = self._normalize_path(root_path)
        if self._tree_root_item is not None:
            return self._tree_root_item

        self._tree_root_item = QTreeWidgetItem([self._root_label(root_path)])
        self._set_item_metadata(self._tree_root_item, ITEM_TYPE_ROOT, path=root_path)
        font = self._tree_root_item.font(0)
        font.setBold(True)
        self._tree_root_item.setFont(0, font)
        self._tree_root_item.setExpanded(True)

        self.addTopLevelItem(self._tree_root_item)
        self._directory_items[root_path] = self._tree_root_item
        return self._tree_root_item

    @staticmethod
    def _find_child(parent: QTreeWidgetItem, text: str) -> Optional[QTreeWidgetItem]:
        """Find a direct child by visible text."""
        for index in range(parent.childCount()):
            child = parent.child(index)
            if child.text(0) == text:
                return child
        return None

    def _relative_parts(self, path: str, root_path: str) -> List[str]:
        """Split a result path into parts relative to root_path."""
        try:
            relative_path = os.path.relpath(path, root_path)
        except ValueError:
            relative_path = path

        if relative_path in ("", "."):
            return []

        if os.altsep:
            relative_path = relative_path.replace(os.altsep, os.sep)
        return [part for part in relative_path.split(os.sep) if part and part != "."]

    def _ensure_directory_item(self, parent: QTreeWidgetItem, name: str, path: str) -> QTreeWidgetItem:
        """Create or reuse a directory node."""
        path = self._normalize_path(path)
        if path in self._directory_items:
            return self._directory_items[path]

        item = self._find_child(parent, name)
        if item is None:
            item = QTreeWidgetItem([name])
            parent.addChild(item)

        self._set_item_metadata(item, ITEM_TYPE_DIRECTORY, path=path)
        self._directory_items[path] = item
        return item

    def _create_match_item(self, file_path: str, line: int, col: int, snippet: str) -> QTreeWidgetItem:
        """Create a match row under a file/path node."""
        snippet_clean = snippet.strip()
        truncated = False
        if not self._word_wrap_enabled and len(snippet_clean) > 120:
            snippet_clean = snippet_clean[:120] + "..."
            truncated = True

        leaf = QTreeWidgetItem([f"{line}:{col}  {snippet_clean}"])
        self._set_item_metadata(
            leaf,
            ITEM_TYPE_MATCH,
            result_path=file_path,
            match_data=(line, col, snippet),
        )

        tooltip = f"File: {file_path}\nLine: {line}\nColumn: {col}"
        if truncated:
            tooltip = f"{tooltip}\n\nFull content:\n{snippet.strip()}"
        leaf.setToolTip(0, tooltip)
        return leaf

    def _add_path_result(
        self,
        file_path: str,
        matches_list: List[Tuple[int, int, str]],
        root_path: str,
        sort_results: bool = False,
    ):
        """Add a file/path result to the hierarchical tree."""
        file_path = self._normalize_path(file_path)
        root_path = self._normalize_path(root_path)
        current = self._ensure_tree_root(root_path)

        parts = self._relative_parts(file_path, root_path)
        if parts:
            for index, part in enumerate(parts):
                is_leaf = index == len(parts) - 1
                node_path = self._normalize_path(os.path.join(root_path, *parts[: index + 1]))

                if is_leaf:
                    child = self._find_child(current, part)
                    if child is None:
                        child = QTreeWidgetItem([part])
                        current.addChild(child)

                    item_type = ITEM_TYPE_DIRECTORY if os.path.isdir(file_path) else ITEM_TYPE_FILE
                    self._set_item_metadata(child, item_type, path=file_path, result_path=file_path)
                    current = child
                else:
                    current = self._ensure_directory_item(current, part, node_path)
        else:
            current.setData(0, RESULT_PATH_ROLE, file_path)

        items = sorted(matches_list, key=lambda x: (x[0], x[1])) if sort_results else matches_list
        for line, col, snippet in items:
            current.addChild(self._create_match_item(file_path, line, col, snippet))
        current.setExpanded(True)

    def _on_item_hover(self, item: QTreeWidgetItem, _column: int):
        """Show position info when hovering over match items (v2.5.1)."""
        if item and self._item_type(item) == ITEM_TYPE_MATCH:
            text = item.text(0)
            # Extract line:col from the beginning of text
            if ":" in text:
                try:
                    match_data = item.data(0, MATCH_DATA_ROLE)
                    if match_data:
                        line, col, _snippet = match_data
                    else:
                        pos_part = text.split()[0]  # Get "line:col" part
                        line, col = pos_part.split(":")

                    file_path = self._result_path_for_item(item) or ""

                    # Set tooltip
                    tooltip = f"File: {file_path}\nLine: {line}\nColumn: {col}"
                    item.setToolTip(0, tooltip)

                    # Update status label if available
                    if self._status_label:
                        self._status_label.setText(f"📍 Position: Line {line}, Column {col} | File: {file_path}")
                except Exception:
                    pass
        else:
            # Clear status for non-match items
            if self._status_label:
                self._status_label.setText("")

    def populate(
        self,
        matches: Dict[str, List[Tuple[int, int, str]]],
        sort_results: bool = False,
        base_path: Optional[str] = None,
    ):
        """
        Populate tree with search results.

        Args:
            matches: Dictionary mapping file paths to list of (line, col, snippet) tuples
            sort_results: If True, sort files alphabetically and matches by line number (v2.9.5)
            base_path: Optional root path used to display results as a real directory tree
        """
        self.setUpdatesEnabled(False)
        try:
            normalized_matches = {
                self._normalize_path(path): list(items)
                for path, items in matches.items()
            }
            root_path = self._resolve_root_path(list(normalized_matches.keys()), base_path)

            self.clear()
            self._matches_data = normalized_matches  # Store for export
            self._base_path = root_path

            # Calculate statistics
            total_files = len(normalized_matches)
            total_matches = sum(len(items) for items in normalized_matches.values())

            # Add summary header at the top
            self._ensure_summary(total_files, total_matches)

            # Sort file paths if requested (v2.9.5)
            paths = sorted(normalized_matches.keys()) if sort_results else normalized_matches.keys()

            if root_path:
                for path in paths:
                    self._add_path_result(path, normalized_matches[path], root_path, sort_results=sort_results)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)

    def add_file_result(
        self,
        file_path: str,
        matches_list: List[Tuple[int, int, str]],
        base_path: Optional[str] = None,
    ):
        """
        Add a single file result to the tree incrementally (for batch processing).

        Args:
            file_path: Path to the file
            matches_list: List of (line, col, snippet) tuples for this file
            base_path: Optional root path used to keep incremental results under one root
        """
        if base_path:
            self.set_base_path(base_path)

        file_path = self._normalize_path(file_path)

        # Store in matches data for export
        if file_path not in self._matches_data:
            self._matches_data[file_path] = []
        self._matches_data[file_path].extend(matches_list)

        root_path = self._resolve_root_path([file_path], self._base_path)
        if root_path:
            self._base_path = root_path
            self._ensure_summary(
                len(self._matches_data),
                sum(len(items) for items in self._matches_data.values()),
            )
            self._add_path_result(file_path, matches_list, root_path)
            self.expandAll()

    def sort_results(self):
        """
        Sort all results in the tree alphabetically by file path.
        Called after batch processing is complete.
        """
        if self._matches_data:
            self.populate(self._matches_data, sort_results=True, base_path=self._base_path)

    def print_message(self, message: str = ""):
        """Display a single message in the tree."""
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self._matches_data = {}  # Clear data when showing message
            top = QTreeWidgetItem([message])
            self._set_item_metadata(top, ITEM_TYPE_MESSAGE)
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
        open_editor_action = menu.addAction("📝 Open in Editor")
        open_editor_action.setEnabled(has_selection)
        open_editor_action.triggered.connect(self._open_in_editor)

        # Open and switch to editor action (v2.9.121 - new feature)
        open_editor_switch_action = menu.addAction("🎯 " + tr("results_tree.action_open_and_switch"))
        open_editor_switch_action.setEnabled(has_selection)
        open_editor_switch_action.triggered.connect(self._open_in_editor_and_switch)

        open_file_action = menu.addAction("📂 Open File")
        open_file_action.setEnabled(has_selection)
        open_file_action.triggered.connect(self._open_selected_files)

        open_all_action = menu.addAction("📂 Open All Files")
        open_all_action.setEnabled(bool(self._matches_data))
        open_all_action.triggered.connect(self._open_all_files)

        menu.addSeparator()

        # Open location action (v2.9.117 - C.2)
        open_location_action = menu.addAction("🗂️ Open Location")
        open_location_action.setEnabled(has_selection)
        open_location_action.triggered.connect(self._open_file_location)

        # Properties action (v2.9.117 - C.2)
        properties_action = menu.addAction("🔍 Properties")
        properties_action.setEnabled(has_selection)
        properties_action.triggered.connect(self._show_file_properties)

        # Show menu at cursor position
        menu.exec_(self.mapToGlobal(position))

    def _copy_selected(self):
        """Copy selected items to clipboard with full file paths (v2.9.2)."""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        lines = []
        last_file = None

        for item in selected_items:
            # Skip summary header
            if self._is_summary_item(item):
                continue

            item_type = self._item_type(item)
            file_path = self._result_path_for_item(item)
            if not file_path:
                continue

            # If it's a result file/path item
            if item_type != ITEM_TYPE_MATCH:
                # Add blank line before new file (except first one)
                if last_file is not None:
                    lines.append("")
                lines.append(file_path)
                last_file = file_path
            # If it's a match item
            else:
                match_text = item.text(0)

                # If parent file wasn't selected, add it first
                if last_file != file_path:
                    if last_file is not None:
                        lines.append("")
                    lines.append(file_path)
                    last_file = file_path

                # Add match with simple indentation
                lines.append(f"   {match_text}")

        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Show feedback
        if self._status_label:
            self._status_label.setText(f"✅ Copied {len(selected_items)} item(s) to clipboard (CTRL+C)")
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

    def _open_in_editor(self):
        """Open selected files in Clarify editor."""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Get main window reference
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(
                self,
                tr("results_tree.error_title"),
                tr("results_tree.error_no_main_window")
            )
            return

        # Collect unique file paths from selection
        file_paths = self._collect_selected_result_paths()

        # Ensure dock_editor exists
        if not hasattr(main_window, 'dock_editor') or main_window.dock_editor is None:
            from src.gui.dock_factory import DockFactory
            DockFactory.create_editor_dock(main_window)

        # Open each file in editor
        opened_count = 0
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    main_window.dock_editor.open_file_path(path)
                    opened_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        tr("results_tree.error_title"),
                        tr("results_tree.error_open_editor").format(path, str(e))
                    )
                    break

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s) in editor")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_in_editor_and_switch(self):
        """Open selected files in Clarify editor and switch focus to editor (v2.9.121)."""
        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Get main window reference
        main_window = self._get_main_window()
        if not main_window:
            QMessageBox.warning(
                self,
                tr("results_tree.error_title"),
                tr("results_tree.error_no_main_window")
            )
            return

        # Collect unique file paths from selection
        file_paths = self._collect_selected_result_paths(preserve_order=True)

        # Ensure dock_editor exists
        if not hasattr(main_window, 'dock_editor') or main_window.dock_editor is None:
            from src.gui.dock_factory import DockFactory
            DockFactory.create_editor_dock(main_window)

        # Open each file in editor
        opened_count = 0
        last_opened_path = None
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    main_window.dock_editor.open_file_path(path)
                    opened_count += 1
                    last_opened_path = path  # Track last opened
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        tr("results_tree.error_title"),
                        tr("results_tree.error_open_editor").format(path, str(e))
                    )
                    break

        # Switch to Editor tab in main window (create if doesn't exist)
        if last_opened_path:
            # Use _show_editor() which properly handles tab creation/switching
            if hasattr(main_window, '_show_editor'):
                main_window._show_editor()

            # Focus on the last opened file's tab in editor
            if hasattr(main_window.dock_editor, 'tab_widget'):
                editor_tabs = main_window.dock_editor.tab_widget
                # Find tab with matching filepath
                for i in range(editor_tabs.count()):
                    tab = editor_tabs.widget(i)
                    if hasattr(tab, 'file_path') and tab.file_path == last_opened_path:
                        editor_tabs.setCurrentIndex(i)
                        break

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s) in editor and switched focus")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _get_main_window(self):
        """Get reference to main window."""
        # Try explicit reference first (v2.9.121 bugfix)
        if self._main_window_ref is not None:
            logger.debug(f"Using explicit main_window reference: {type(self._main_window_ref).__name__}")
            return self._main_window_ref

        # Fallback to parent chain traversal
        widget = self
        logger.debug(f"Starting search for main_window from {type(self).__name__}")
        max_iterations = 20  # Safety limit
        iteration = 0

        while widget is not None and iteration < max_iterations:
            logger.debug(f"Checking widget: {type(widget).__name__}, has dock_editor: {hasattr(widget, 'dock_editor')}")
            if hasattr(widget, 'dock_editor'):
                logger.debug(f"Found main_window: {type(widget).__name__}")
                return widget
            widget = widget.parent()
            iteration += 1

        logger.debug(f"Could NOT find main_window - reached None after {iteration} iterations")
        return None

    def _open_selected_files(self):
        """Open selected files in system default application (v2.9.2)."""
        import subprocess as sp

        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Collect unique file paths from selection
        file_paths = self._collect_selected_result_paths()

        # Open each file
        opened_count = 0
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    if sys.platform.startswith("darwin"):
                        sp.run(["open", path], check=False)
                    elif os.name == "nt":
                        sp.run(["cmd", "/c", "start", "", path], check=False)
                    else:
                        sp.run(["xdg-open", path], check=False)
                    opened_count += 1
                except Exception as e:
                    logger.error(f"Error opening {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_all_files(self):
        """Open all files from results in system default application (v2.9.2)."""
        import subprocess as sp

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
                        sp.run(["open", path], check=False)
                    elif os.name == "nt":
                        sp.run(["cmd", "/c", "start", "", path], check=False)
                    else:
                        sp.run(["xdg-open", path], check=False)
                    opened_count += 1
                except Exception as e:
                    logger.error(f"Error opening {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_file_location(self):
        """Open file location in file manager (v2.9.117 - C.2)."""
        import subprocess as sp
        import platform

        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Collect unique file paths from selection
        file_paths = self._collect_selected_result_paths()

        # Open each file's location
        opened_count = 0
        for path in file_paths:
            if os.path.exists(path):
                directory = os.path.dirname(path) if os.path.isfile(path) else path

                try:
                    system = platform.system()
                    if system == "Windows":
                        sp.run(["explorer", "/select,", path], check=False)
                    elif system == "Darwin":  # macOS
                        sp.run(["open", "-R", path], check=False)
                    else:  # Linux
                        sp.run(["xdg-open", directory], check=False)
                    opened_count += 1
                except Exception as e:
                    logger.error(f"Error opening location for {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} location(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _show_file_properties(self):
        """Show file properties dialog (v2.9.117 - C.2)."""
        from datetime import datetime
        import stat

        selected_items = self.selectedItems()
        if not selected_items:
            return

        # Collect file paths from selection
        file_paths = self._collect_selected_result_paths(preserve_order=True)

        if not file_paths:
            return

        # Show properties for first file
        path = file_paths[0]
        if os.path.exists(path):
            stat_info = os.stat(path)
            is_dir = os.path.isdir(path)

            # Format file info
            info_lines = [
                f"Path: {path}",
                f"Type: {'Directory' if is_dir else 'File'}",
                f"Size: {self._format_size(stat_info.st_size)}",
                f"Created: {datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}",
                f"Modified: {datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}",
                f"Accessed: {datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S')}",
            ]

            # Add permissions on Unix
            if hasattr(stat_info, "st_mode"):
                mode = stat_info.st_mode
                perms = stat.filemode(mode)
                info_lines.append(f"Permissions: {perms}")

            # Show in message box
            QMessageBox.information(self, "File Properties", "\n".join(info_lines))

    def _format_size(self, size: int) -> str:
        """Format size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
