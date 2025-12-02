#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from typing import Dict, List, Optional

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

from src.shortcut_manager import ShortcutManager


class ShortcutsDialog(QDialog):
    """Dialog for customizing keyboard shortcuts."""

    shortcuts_changed = Signal(dict)  # Emits new custom shortcuts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Keyboard Shortcuts")
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
        header = QLabel("Customize keyboard shortcuts for all actions")
        header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(header)

        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter shortcuts...")
        self.search_box.textChanged.connect(self._filter_shortcuts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Shortcuts table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut", "Description"])
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

        self.btn_reset_selected = QPushButton("Reset Selected")
        self.btn_reset_selected.setToolTip("Reset selected shortcut to default")
        self.btn_reset_selected.clicked.connect(self._reset_selected)

        self.btn_reset_all = QPushButton("Reset All")
        self.btn_reset_all.setToolTip("Reset all shortcuts to defaults")
        self.btn_reset_all.clicked.connect(self._reset_all)

        btn_layout.addWidget(self.btn_reset_selected)
        btn_layout.addWidget(self.btn_reset_all)
        btn_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.setToolTip("Save changes and close")
        self.btn_save.clicked.connect(self._save_changes)
        self.btn_save.setDefault(True)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setToolTip("Discard changes and close")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        # Info label
        info = QLabel("💡 Double-click on any shortcut to edit it")
        info.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        layout.addWidget(info)

    def _load_shortcuts(self):
        """Load all shortcuts into table."""
        self.table.setRowCount(0)

        # Get all shortcuts organized by category
        all_shortcuts = ShortcutManager.get_all_shortcuts()

        # Group by category
        categories = {}
        for action_name in all_shortcuts.keys():
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
        dialog.setWindowTitle(f"Edit Shortcut: {action_name}")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Description
        _, description = ShortcutManager.get_default_shortcut(action_name)
        desc_label = QLabel(f"<b>{description}</b>")
        layout.addWidget(desc_label)

        # Current shortcut
        current_label = QLabel(f"Current: {current_shortcut}")
        layout.addWidget(current_label)

        # Key sequence editor
        layout.addWidget(QLabel("New shortcut:"))
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
                warning_label.setText(f"⚠️ Conflicts with: {', '.join(conflicts)}")
            elif ShortcutManager.is_os_shortcut(new_seq):
                warning_label.setText(f"⚠️ This might conflict with OS shortcut")
            else:
                warning_label.setText("✓ No conflicts detected")
                warning_label.setStyleSheet("color: green; font-weight: bold;")

        key_edit.keySequenceChanged.connect(check_conflicts)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_clear = QPushButton("Clear")

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
            reply = QMessageBox.question(
                self,
                "Shortcut Conflict",
                f"This shortcut is already used by:\n\n{', '.join(conflicts)}\n\n"
                "Do you want to use it anyway? (This will cause conflicts)",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        # Check OS shortcuts
        if ShortcutManager.is_os_shortcut(shortcut):
            reply = QMessageBox.question(
                self,
                "OS Shortcut Warning",
                f"The shortcut '{shortcut}' might conflict with your operating system.\n\n"
                "Do you want to use it anyway?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return False

        return True

    def _reset_selected(self):
        """Reset selected shortcut to default."""
        selected_rows = set(item.row() for item in self.table.selectedItems())

        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a shortcut to reset.")
            return

        for row in selected_rows:
            action_item = self.table.item(row, 1)
            action_name = action_item.data(Qt.UserRole)

            # Remove from pending changes
            if action_name in self._pending_changes:
                del self._pending_changes[action_name]

        self._load_shortcuts()
        self.status_label.setText("✓ Selected shortcuts reset to defaults")

    def _reset_all(self):
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset All Shortcuts",
            "Are you sure you want to reset ALL shortcuts to defaults?\n\n"
            "This will discard all your customizations.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._pending_changes.clear()
            self._load_shortcuts()
            self.status_label.setText("✓ All shortcuts reset to defaults")

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
            self.status_label.setText(
                f"⚠️ {num_pending} unsaved change(s) | " f"{num_custom} custom shortcut(s) active"
            )
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        elif num_custom > 0:
            self.status_label.setText(f"ℹ️ {num_custom} custom shortcut(s) active")
            self.status_label.setStyleSheet("color: blue;")
        else:
            self.status_label.setText("Using default shortcuts")
            self.status_label.setStyleSheet("color: gray;")
