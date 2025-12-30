#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Keyboard Shortcuts Customization Dialog
----------------------------------------
UI for customizing keyboard shortcuts with conflict detection and import/export.

Sprint: v2.9.62 - Keyboard Shortcuts Customization
Author: Josué Amaral
Date: 2025-12-10
"""

import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QHeaderView, QFileDialog,
    QGroupBox, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QKeyEvent
from src.i18n.translator import tr

from ..shortcut_manager import ShortcutManager


class KeySequenceEdit(QLineEdit):
    """Custom QLineEdit for capturing key sequences."""
    
    keySequenceChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(tr("shortcut_customizer.placeholder_keys"))
        self.setReadOnly(True)
        self._current_keys = []
        self._max_keys = 2  # Support Ctrl+K Ctrl+S style sequences
    
    def keyPressEvent(self, event: QKeyEvent):
        """Capture key press events."""
        # Ignore modifier keys alone
        if event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            return
        
        # Build key sequence string
        modifiers = event.modifiers()
        key = event.key()
        
        # Build key string
        key_parts = []
        if modifiers & Qt.ControlModifier:
            key_parts.append("Ctrl")
        if modifiers & Qt.ShiftModifier:
            key_parts.append("Shift")
        if modifiers & Qt.AltModifier:
            key_parts.append("Alt")
        if modifiers & Qt.MetaModifier:
            key_parts.append("Meta")
        
        # Add the actual key
        key_text = QKeySequence(key).toString()
        if key_text:
            key_parts.append(key_text)
        
        if key_parts:
            key_string = "+".join(key_parts)
            self._current_keys.append(key_string)
            
            # Limit to max_keys
            if len(self._current_keys) > self._max_keys:
                self._current_keys = self._current_keys[-self._max_keys:]
            
            # Join with space for multi-key sequences
            full_sequence = " ".join(self._current_keys)
            self.setText(full_sequence)
            self.keySequenceChanged.emit(full_sequence)
    
    def clear_sequence(self):
        """Clear the captured sequence."""
        self._current_keys.clear()
        self.clear()
    
    def focusOutEvent(self, event):
        """Reset on focus lost."""
        super().focusOutEvent(event)
        self._current_keys.clear()


class ShortcutCustomizerDialog(QDialog):
    """Dialog for customizing keyboard shortcuts."""
    
    shortcutsChanged = Signal(dict)  # Emits custom shortcuts dict
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("shortcut_customizer.title"))
        self.resize(800, 600)
        
        # Store modified shortcuts
        self._modified_shortcuts: Dict[str, str] = {}
        self._conflicts: Dict[str, List[str]] = {}
        
        # Load current custom shortcuts
        self._load_current_shortcuts()
        
        self._setup_ui()
        self._populate_table()
        self._update_stats()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header with description
        header = QLabel(
            "<b>Customize Keyboard Shortcuts</b><br>"
            "Double-click a shortcut to edit. Press <i>Escape</i> to clear."
        )
        layout.addWidget(header)
        
        # Filter and search
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel(tr("shortcut_customizer.lbl_category")))
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All", "File", "Edit", "Tools", "Navigation", "View", "Processing", "Help"
        ])
        self.category_filter.currentTextChanged.connect(self._filter_shortcuts)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addWidget(QLabel(tr("shortcut_customizer.lbl_search")))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(tr("shortcut_customizer.placeholder_search"))
        self.search_box.textChanged.connect(self._filter_shortcuts)
        filter_layout.addWidget(self.search_box, 1)
        
        self.show_conflicts_only = QCheckBox(tr("shortcut_customizer.chk_conflicts"))
        self.show_conflicts_only.stateChanged.connect(self._filter_shortcuts)
        filter_layout.addWidget(self.show_conflicts_only)
        
        layout.addLayout(filter_layout)
        
        # Shortcuts table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Action", "Description", "Default", "Custom", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.itemDoubleClicked.connect(self._edit_shortcut)
        layout.addWidget(self.table)
        
        # Statistics
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        # Import/Export group
        import_export_group = QGroupBox(tr("shortcut_customizer.group_import_export"))
        import_export_layout = QHBoxLayout(import_export_group)
        
        self.import_btn = QPushButton(tr("shortcut_customizer.btn_import"))
        self.import_btn.clicked.connect(self._import_shortcuts)
        import_export_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton(tr("shortcut_customizer.btn_export"))
        self.export_btn.clicked.connect(self._export_shortcuts)
        import_export_layout.addWidget(self.export_btn)
        
        buttons_layout.addWidget(import_export_group)
        
        buttons_layout.addStretch()
        
        # Reset buttons
        self.reset_all_btn = QPushButton(tr("shortcut_customizer.btn_reset_all"))
        self.reset_all_btn.clicked.connect(self._reset_all_shortcuts)
        buttons_layout.addWidget(self.reset_all_btn)
        
        self.reset_selected_btn = QPushButton(tr("shortcut_customizer.btn_reset_selected"))
        self.reset_selected_btn.clicked.connect(self._reset_selected_shortcut)
        buttons_layout.addWidget(self.reset_selected_btn)
        
        # OK/Cancel
        self.ok_btn = QPushButton(tr("shortcut_customizer.btn_ok"))
        self.ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton(tr("shortcut_customizer.btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_current_shortcuts(self):
        """Load current custom shortcuts from ShortcutManager."""
        self._modified_shortcuts = ShortcutManager.get_custom_shortcuts()
    
    def _populate_table(self):
        """Populate table with all shortcuts."""
        self.table.setRowCount(0)
        
        all_shortcuts = ShortcutManager.SHORTCUTS
        
        for row, (action_name, (default_shortcut, description)) in enumerate(sorted(all_shortcuts.items())):
            self.table.insertRow(row)
            
            # Action name
            self.table.setItem(row, 0, QTableWidgetItem(action_name))
            
            # Description
            self.table.setItem(row, 1, QTableWidgetItem(description))
            
            # Default shortcut
            self.table.setItem(row, 2, QTableWidgetItem(default_shortcut))
            
            # Custom shortcut
            custom = self._modified_shortcuts.get(action_name, "")
            custom_item = QTableWidgetItem(custom)
            self.table.setItem(row, 3, custom_item)
            
            # Status
            status = self._get_status(action_name, custom)
            status_item = QTableWidgetItem(status)
            
            # Color code status
            if "CONFLICT" in status:
                status_item.setBackground(Qt.red)
                status_item.setForeground(Qt.white)
            elif "Modified" in status:
                status_item.setBackground(Qt.yellow)
            elif "OS Conflict" in status:
                status_item.setBackground(Qt.darkYellow)
            
            self.table.setItem(row, 4, status_item)
    
    def _get_status(self, action_name: str, custom_shortcut: str) -> str:
        """Get status string for an action."""
        if not custom_shortcut:
            return "Default"
        
        # Check for conflicts
        conflicts = ShortcutManager.get_conflicts(custom_shortcut)
        conflicts = [c for c in conflicts if c != action_name]  # Remove self
        
        if conflicts:
            self._conflicts[action_name] = conflicts
            return f"CONFLICT: {', '.join(conflicts)}"
        
        # Check OS conflicts
        if ShortcutManager.is_os_shortcut(custom_shortcut):
            return "Modified (OS Conflict)"
        
        return "Modified"
    
    def _filter_shortcuts(self):
        """Filter shortcuts based on category and search."""
        category = self.category_filter.currentText()
        search_text = self.search_box.text().lower()
        show_conflicts = self.show_conflicts_only.isChecked()
        
        for row in range(self.table.rowCount()):
            action_name = self.table.item(row, 0).text()
            description = self.table.item(row, 1).text().lower()
            status = self.table.item(row, 4).text()
            
            # Category filter
            if category != "All":
                action_category = ShortcutManager.get_category(action_name)
                if action_category != category:
                    self.table.setRowHidden(row, True)
                    continue
            
            # Search filter
            if search_text and search_text not in action_name.lower() and search_text not in description:
                self.table.setRowHidden(row, True)
                continue
            
            # Conflicts filter
            if show_conflicts and "CONFLICT" not in status:
                self.table.setRowHidden(row, True)
                continue
            
            # Show row
            self.table.setRowHidden(row, False)
    
    def _edit_shortcut(self, item: QTableWidgetItem):
        """Edit a shortcut (double-click handler)."""
        row = item.row()
        action_name = self.table.item(row, 0).text()
        current_custom = self.table.item(row, 3).text()
        
        # Create dialog with key capture
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("shortcut_customizer.window_title").format(action_name=action_name))
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"<b>{self.table.item(row, 1).text()}</b>"))
        layout.addWidget(QLabel(f"Default: {self.table.item(row, 2).text()}"))
        
        key_edit = KeySequenceEdit(dialog)
        if current_custom:
            key_edit.setText(current_custom)
        layout.addWidget(QLabel(tr("shortcut_customizer.lbl_new_shortcut")))
        layout.addWidget(key_edit)
        
        # Conflict warning
        conflict_label = QLabel()
        conflict_label.setWordWrap(True)
        layout.addWidget(conflict_label)
        
        def check_conflicts():
            new_seq = key_edit.text()
            if new_seq:
                conflicts = ShortcutManager.get_conflicts(new_seq)
                conflicts = [c for c in conflicts if c != action_name]
                if conflicts:
                    conflict_label.setText(
                        f"⚠️ <b>Conflict:</b> This shortcut is already used by: {', '.join(conflicts)}"
                    )
                    conflict_label.setStyleSheet("color: red;")
                elif ShortcutManager.is_os_shortcut(new_seq):
                    conflict_label.setText(
                        f"⚠️ <b>OS Conflict:</b> This shortcut may conflict with system shortcuts"
                    )
                    conflict_label.setStyleSheet("color: orange;")
                else:
                    conflict_label.setText("✓ No conflicts")
                    conflict_label.setStyleSheet("color: green;")
            else:
                conflict_label.clear()
        
        key_edit.keySequenceChanged.connect(check_conflicts)
        check_conflicts()  # Initial check
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton(tr("shortcut_customizer.btn_clear"))
        clear_btn.clicked.connect(key_edit.clear_sequence)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        
        ok_btn = QPushButton(tr("shortcut_customizer.btn_dialog_ok"))
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton(tr("shortcut_customizer.btn_dialog_cancel"))
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec() == QDialog.Accepted:
            new_shortcut = key_edit.text()
            if new_shortcut:
                self._modified_shortcuts[action_name] = new_shortcut
            elif action_name in self._modified_shortcuts:
                del self._modified_shortcuts[action_name]
            
            self._refresh_row(row)
            self._update_stats()
    
    def _refresh_row(self, row: int):
        """Refresh a single row's status."""
        action_name = self.table.item(row, 0).text()
        custom = self._modified_shortcuts.get(action_name, "")
        
        # Update custom column
        self.table.item(row, 3).setText(custom)
        
        # Update status
        status = self._get_status(action_name, custom)
        status_item = self.table.item(row, 4)
        status_item.setText(status)
        
        # Update color
        if "CONFLICT" in status:
            status_item.setBackground(Qt.red)
            status_item.setForeground(Qt.white)
        elif "Modified" in status:
            status_item.setBackground(Qt.yellow)
            status_item.setForeground(Qt.black)
        elif "OS Conflict" in status:
            status_item.setBackground(Qt.darkYellow)
            status_item.setForeground(Qt.black)
        else:
            status_item.setBackground(Qt.white)
            status_item.setForeground(Qt.black)
    
    def _reset_selected_shortcut(self):
        """Reset selected shortcut to default."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, tr("shortcut_customizer.msg_no_selection_title"), tr("shortcut_customizer.msg_no_selection"))
            return
        
        action_name = self.table.item(current_row, 0).text()
        if action_name in self._modified_shortcuts:
            del self._modified_shortcuts[action_name]
            self._refresh_row(current_row)
            self._update_stats()
    
    def _reset_all_shortcuts(self):
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset All Shortcuts",
            "Are you sure you want to reset all shortcuts to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._modified_shortcuts.clear()
            self._conflicts.clear()
            self._populate_table()
            self._update_stats()
    
    def _update_stats(self):
        """Update statistics label."""
        total = len(ShortcutManager.SHORTCUTS)
        modified = len(self._modified_shortcuts)
        conflicts = len(self._conflicts)
        
        self.stats_label.setText(
            f"Total: {total} shortcuts | "
            f"Modified: {modified} | "
            f"Conflicts: {conflicts}"
        )
        
        if conflicts > 0:
            self.stats_label.setStyleSheet("color: red; font-weight: bold;")
        elif modified > 0:
            self.stats_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.stats_label.setStyleSheet("")
    
    def _import_shortcuts(self):
        """Import shortcuts from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Shortcuts",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            if not isinstance(imported, dict):
                raise ValueError("Invalid format: expected JSON object")
            
            # Validate imported shortcuts
            valid_actions = set(ShortcutManager.SHORTCUTS.keys())
            invalid_actions = set(imported.keys()) - valid_actions
            
            if invalid_actions:
                QMessageBox.warning(
                    self,
                    "Invalid Actions",
                    f"The following actions are not valid and will be skipped:\n"
                    f"{', '.join(invalid_actions)}"
                )
            
            # Apply valid shortcuts
            for action, shortcut in imported.items():
                if action in valid_actions:
                    self._modified_shortcuts[action] = shortcut
            
            self._populate_table()
            self._update_stats()
            
            QMessageBox.information(
                self,
                "Import Successful",
                f"Imported {len(imported)} shortcuts from {Path(file_path).name}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import shortcuts:\n{str(e)}"
            )
    
    def _export_shortcuts(self):
        """Export shortcuts to JSON file."""
        if not self._modified_shortcuts:
            QMessageBox.information(
                self,
                "No Custom Shortcuts",
                "You don't have any custom shortcuts to export."
            )
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Shortcuts",
            str(Path.home() / "clarify_shortcuts.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._modified_shortcuts, f, indent=2)
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self._modified_shortcuts)} custom shortcuts to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export shortcuts:\n{str(e)}"
            )
    
    def get_custom_shortcuts(self) -> Dict[str, str]:
        """Get the modified shortcuts dict."""
        return self._modified_shortcuts.copy()
    
    def accept(self):
        """Accept dialog and emit changes."""
        if self._conflicts:
            reply = QMessageBox.warning(
                self,
                "Conflicts Detected",
                f"There are {len(self._conflicts)} shortcut conflicts. "
                f"Do you want to save anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        self.shortcutsChanged.emit(self._modified_shortcuts)
        super().accept()
