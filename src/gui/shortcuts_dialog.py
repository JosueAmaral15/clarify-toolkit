"""
Keyboard Shortcuts Customization Dialog

Allows users to view and customize keyboard shortcuts.
v2.9.33 - Comprehensive Keyboard Shortcuts System

Features:
- View all shortcuts organized by category
- Edit shortcuts by double-clicking
- Detect and warn about conflicts
- Reset individual or all shortcuts to defaults
- Validate against OS shortcuts
- Save/Cancel changes

Design Patterns:
- Command Pattern: Each shortcut change is a reversible command
- Observer Pattern: Cell changed signals trigger validation
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=unnecessary-lambda  # Lambda for signal connections
# pylint: disable=line-too-long  # Long tooltips

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.i18n.translator import tr
from src.shortcut_manager import ShortcutManager


class ShortcutsDialog(QDialog):
    """Dialog for customizing keyboard shortcuts."""

    shortcuts_changed = Signal(dict)  # Emits new custom shortcuts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("shortcuts_dialog.title"))
        self.setMinimumSize(800, 600)

        # Store changes temporarily until Save is clicked
        self._pending_changes: Dict[str, str] = {}
        self._original_shortcuts = ShortcutManager.get_custom_shortcuts()

        self._init_ui()
        self._load_shortcuts()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(tr("shortcuts_dialog.header"))
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel(tr("shortcuts_dialog.search_label"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(tr("shortcuts_dialog.search_placeholder"))
        self.search_box.textChanged.connect(self._filter_shortcuts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Shortcuts table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            tr("shortcuts_dialog.col_category"),
            tr("shortcuts_dialog.col_action"),
            tr("shortcuts_dialog.col_shortcut"),
            tr("shortcuts_dialog.col_description")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        layout.addWidget(self.table)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.status_label)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_reset_selected = QPushButton(tr("shortcuts_dialog.btn_reset_selected"))
        self.btn_reset_selected.setToolTip(tr("shortcuts_dialog.btn_reset_selected_tooltip"))
        self.btn_reset_selected.clicked.connect(self._reset_selected)

        self.btn_reset_all = QPushButton(tr("shortcuts_dialog.btn_reset_all"))
        self.btn_reset_all.setToolTip(tr("shortcuts_dialog.btn_reset_all_tooltip"))
        self.btn_reset_all.clicked.connect(self._reset_all)

        btn_layout.addWidget(self.btn_reset_selected)
        btn_layout.addWidget(self.btn_reset_all)
        btn_layout.addStretch()

        self.btn_save = QPushButton(tr("shortcuts_dialog.btn_save"))
        self.btn_save.setToolTip(tr("shortcuts_dialog.btn_save_tooltip"))
        self.btn_save.clicked.connect(self._save_changes)
        self.btn_save.setDefault(True)

        self.btn_cancel = QPushButton(tr("shortcuts_dialog.btn_cancel"))
        self.btn_cancel.setToolTip(tr("shortcuts_dialog.btn_cancel_tooltip"))
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        # Info label
        info = QLabel(tr("shortcuts_dialog.info_hint"))
        info.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        layout.addWidget(info)

    def _load_shortcuts(self):
        """Load all shortcuts into table."""
        self.table.setRowCount(0)

        # Get all shortcuts organized by category
        all_shortcuts = ShortcutManager.get_all_shortcuts()

        # Group by category
        categories = {}
        for action_name in all_shortcuts:
            category = ShortcutManager.get_category(action_name)
            if category not in categories:
                categories[category] = []
            categories[category].append(action_name)

        # Sort categories
        sorted_categories = sorted(categories.keys())

        # Populate table
        row = 0
        for category in sorted_categories:
            actions = sorted(categories[category])
            for action_name in actions:
                shortcut, description = all_shortcuts[action_name]

                self.table.insertRow(row)

                # Category
                item_cat = QTableWidgetItem(category)
                item_cat.setFlags(item_cat.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, item_cat)

                # Action name (hidden from user, technical name)
                item_action = QTableWidgetItem(action_name)
                item_action.setFlags(item_action.flags() & ~Qt.ItemIsEditable)
                item_action.setData(Qt.UserRole, action_name)  # Store technical name
                self.table.setItem(row, 1, item_action)

                # Shortcut
                item_shortcut = QTableWidgetItem(shortcut)
                item_shortcut.setTextAlignment(Qt.AlignCenter)

                # Highlight custom shortcuts
                if action_name in ShortcutManager.get_custom_shortcuts():
                    item_shortcut.setBackground(QColor(255, 255, 200))  # Light yellow

                # Mark pending changes
                if action_name in self._pending_changes:
                    item_shortcut.setText(self._pending_changes[action_name])
                    item_shortcut.setBackground(QColor(200, 255, 200))  # Light green

                self.table.setItem(row, 2, item_shortcut)

                # Description
                item_desc = QTableWidgetItem(description)
                item_desc.setFlags(item_desc.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 3, item_desc)

                row += 1

        self._update_status()

    def _filter_shortcuts(self, text: str):
        """Filter shortcuts based on search text."""
        text = text.lower()

        for row in range(self.table.rowCount()):
            match = False

            # Check all columns
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break

            self.table.setRowHidden(row, not match)

    def _on_item_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on shortcut cell."""
        row = item.row()
        col = item.column()

        # Only allow editing shortcut column
        if col != 2:
            return

        action_item = self.table.item(row, 1)
        action_name = action_item.data(Qt.UserRole)
        current_shortcut = self.table.item(row, 2).text()

        # Show edit dialog
        new_shortcut = self._show_edit_dialog(action_name, current_shortcut)

        if new_shortcut is not None:
            # Validate shortcut
            if self._validate_shortcut(action_name, new_shortcut):
                # Store pending change
                self._pending_changes[action_name] = new_shortcut

                # Update table
                self._load_shortcuts()

    def _show_edit_dialog(self, action_name: str, current_shortcut: str) -> Optional[str]:
        """Show dialog to edit a shortcut."""
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("shortcuts_dialog.edit_title").replace("{action}", action_name))
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Description
        _, description = ShortcutManager.get_default_shortcut(action_name)
        desc_label = QLabel(f"<b>{description}</b>")
        layout.addWidget(desc_label)

        # Current shortcut
        current_label = QLabel(tr("shortcuts_dialog.edit_current").replace("{shortcut}", current_shortcut))
        layout.addWidget(current_label)

        # Key sequence editor
        layout.addWidget(QLabel(tr("shortcuts_dialog.edit_new_label")))
        key_edit = QKeySequenceEdit()
        if current_shortcut:
            key_edit.setKeySequence(QKeySequence(current_shortcut))
        layout.addWidget(key_edit)

        # Warning label
        warning_label = QLabel("")
        warning_label.setStyleSheet("color: orange; font-weight: bold;")
        layout.addWidget(warning_label)

        # Check conflicts on change
        def check_conflicts():
            new_seq = key_edit.keySequence().toString()
            if not new_seq:
                warning_label.setText("")
                return

            # Check conflicts with other actions
            conflicts = ShortcutManager.get_conflicts(new_seq)
            conflicts = [c for c in conflicts if c != action_name]

            if conflicts:
                warning_label.setText(tr("shortcuts_dialog.edit_conflicts").replace("{actions}", ", ".join(conflicts)))
            elif ShortcutManager.is_os_shortcut(new_seq):
                warning_label.setText(tr("shortcuts_dialog.edit_os_warning"))
            else:
                warning_label.setText(tr("shortcuts_dialog.edit_no_conflicts"))
                warning_label.setStyleSheet("color: green; font-weight: bold;")

        key_edit.keySequenceChanged.connect(check_conflicts)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton(tr("shortcuts_dialog.edit_btn_ok"))
        btn_cancel = QPushButton(tr("shortcuts_dialog.edit_btn_cancel"))
        btn_clear = QPushButton(tr("shortcuts_dialog.edit_btn_clear"))

        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_clear.clicked.connect(lambda: key_edit.clear())

        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        if dialog.exec() == QDialog.Accepted:
            return key_edit.keySequence().toString()
        return None

    def _validate_shortcut(self, action_name: str, shortcut: str) -> bool:
        """Validate shortcut and show warnings if needed."""
        if not shortcut:
            return True  # Empty shortcut is valid (disables shortcut)

        # Check conflicts
        conflicts = ShortcutManager.get_conflicts(shortcut)
        conflicts = [c for c in conflicts if c != action_name]

        if conflicts:
            msg = tr("shortcuts_dialog.conflict_msg").replace("{actions}", ", ".join(conflicts))
            reply = QMessageBox.question(
                self,
                tr("shortcuts_dialog.conflict_title"),
                msg,
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        # Check OS shortcuts
        if ShortcutManager.is_os_shortcut(shortcut):
            msg = tr("shortcuts_dialog.os_conflict_msg").replace("{shortcut}", shortcut)
            reply = QMessageBox.question(
                self,
                tr("shortcuts_dialog.os_conflict_title"),
                msg,
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        return True

    def _reset_selected(self):
        """Reset selected shortcut to default."""
        selected_rows = set(item.row() for item in self.table.selectedItems())

        if not selected_rows:
            QMessageBox.information(self, tr("shortcuts_dialog.no_selection_title"), tr("shortcuts_dialog.no_selection_msg"))
            return

        for row in selected_rows:
            action_item = self.table.item(row, 1)
            action_name = action_item.data(Qt.UserRole)

            # Remove from pending changes
            if action_name in self._pending_changes:
                del self._pending_changes[action_name]

        self._load_shortcuts()
        self.status_label.setText(tr("shortcuts_dialog.status_reset_selected"))

    def _reset_all(self):
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            tr("shortcuts_dialog.reset_all_title"),
            tr("shortcuts_dialog.reset_all_msg"),
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._pending_changes.clear()
            self._load_shortcuts()
            self.status_label.setText(tr("shortcuts_dialog.status_reset_all"))

    def _save_changes(self):
        """Save changes and close dialog."""
        if not self._pending_changes:
            # No changes, just close
            self.accept()
            return

        # Merge pending changes with original custom shortcuts
        new_custom = self._original_shortcuts.copy()
        new_custom.update(self._pending_changes)

        # Emit signal with new custom shortcuts
        self.shortcuts_changed.emit(new_custom)

        self.accept()

    def _update_status(self):
        """Update status label."""
        num_custom = len(ShortcutManager.get_custom_shortcuts())
        num_pending = len(self._pending_changes)

        if num_pending > 0:
            msg = tr("shortcuts_dialog.status_unsaved").replace("{pending}", str(num_pending)).replace("{custom}", str(num_custom))
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        elif num_custom > 0:
            msg = tr("shortcuts_dialog.status_custom").replace("{custom}", str(num_custom))
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("color: blue;")
        else:
            self.status_label.setText(tr("shortcuts_dialog.status_default"))
            self.status_label.setStyleSheet("color: gray;")
