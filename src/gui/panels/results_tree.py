"""
Results tree widget for displaying search matches.
Extracted from app.py (v2.9.114 - Phase 1.2).
"""

import os
import sys
from typing import Dict, List, Tuple

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QMessageBox,
    QApplication,
    QHeaderView,
    QCheckBox,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
)
from PySide6.QtCore import Qt, QTimer, QModelIndex, QRect, QRectF
from PySide6.QtGui import QColor, QPainter, QFontMetrics, QTextDocument, QAbstractTextDocumentLayout

from ...i18n import tr


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

    def __init__(self, parent=None):
        super().__init__(parent)
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
            self.populate(self._matches_data, sort_results=False)
            # Force viewport update
            self.viewport().update()

    def _on_item_hover(self, item: QTreeWidgetItem, column: int):
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
                        self._status_label.setText(f"📍 Position: Line {line}, Column {col} | File: {file_path}")
                except:
                    pass
        else:
            # Clear status for non-match items
            if self._status_label:
                self._status_label.setText("")

    def populate(self, matches: Dict[str, List[Tuple[int, int, str]]], sort_results: bool = False):
        """
        Populate tree with search results.

        Args:
            matches: Dictionary mapping file paths to list of (line, col, snippet) tuples
            sort_results: If True, sort files alphabetically and matches by line number (v2.9.5)
        """
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
                    # Truncate long snippets only if word wrap is disabled (v2.9.117)
                    snippet_clean = snippet.strip()
                    if not self._word_wrap_enabled and len(snippet_clean) > 120:
                        snippet_clean = snippet_clean[:120] + "..."

                    leaf = QTreeWidgetItem([f"{line}:{col}  {snippet_clean}"])

                    # Store full snippet in tooltip if truncated and word wrap is off
                    if not self._word_wrap_enabled and len(snippet.strip()) > 120:
                        leaf.setToolTip(0, f"Full content:\n{snippet.strip()}")

                    top.addChild(leaf)
            self.expandAll()
        finally:
            self.setUpdatesEnabled(True)

    def print_message(self, message: str = ""):
        """Display a single message in the tree."""
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
        copy_all_action = menu.addAction("📋 Copy All ReResposta: sults")
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
            if item.text(0).startswith("📊 Results:"):
                continue

            # If it's a file item (no parent)
            if not item.parent():
                file_path = item.text(0)
                # Add blank line before new file (except first one)
                if last_file is not None:
                    lines.append("")
                lines.append(file_path)
                last_file = file_path
            # If it's a match item (has parent)
            else:
                # Get file path from parent and match text
                file_path = item.parent().text(0)
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
                "Error",
                "Could not find main window to open editor"
            )
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
        
        # Open each file in editor
        opened_count = 0
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    main_window.open_file_in_editor(path)
                    opened_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Could not open file in editor: {path}\n{e}"
                    )
                    break
        
        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s) in editor")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))
    
    def _get_main_window(self):
        """Get reference to main window."""
        widget = self
        while widget is not None:
            if hasattr(widget, 'open_file_in_editor'):
                return widget
            widget = widget.parent()
        return None

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
                        os.system(f'open "{path}"')
                    elif os.name == "nt":
                        os.system(f'start "" "{path}"')
                    else:
                        os.system(f'xdg-open "{path}"')
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
                        os.system(f'open "{path}"')
                    elif os.name == "nt":
                        os.system(f'start "" "{path}"')
                    else:
                        os.system(f'xdg-open "{path}"')
                    opened_count += 1
                except Exception as e:
                    print(f"Error opening {path}: {e}")

        # Show feedback
        if self._status_label and opened_count > 0:
            self._status_label.setText(f"✅ Opened {opened_count} file(s)")
            QTimer.singleShot(3000, lambda: self._status_label.setText(""))

    def _open_file_location(self):
        """Open file location in file manager (v2.9.117 - C.2)."""
        import subprocess
        import platform

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

        # Open each file's location
        opened_count = 0
        for path in file_paths:
            if os.path.exists(path):
                directory = os.path.dirname(path) if os.path.isfile(path) else path

                try:
                    system = platform.system()
                    if system == "Windows":
                        subprocess.run(["explorer", "/select,", path])
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", "-R", path])
                    else:  # Linux
                        subprocess.run(["xdg-open", directory])
                    opened_count += 1
                except Exception as e:
                    print(f"Error opening location for {path}: {e}")

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
        file_paths = []
        for item in selected_items:
            # Skip summary header
            if item.text(0).startswith("📊 Results:"):
                continue

            # If it's a file item (no parent), use it directly
            if not item.parent():
                file_paths.append(item.text(0))
            # If it's a match item, get parent file path
            else:
                parent_text = item.parent().text(0)
                if not parent_text.startswith("📊") and parent_text not in file_paths:
                    file_paths.append(parent_text)

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
