#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Layout Manager Dialog for Clarify
----------------------------------
Dialog for managing saved layouts: load, delete, reset to defaults.

Phase 3.10 - Dialog Extraction
Author: Josué Amaral
Date: 2025-12-24
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
    QPushButton, QMessageBox, QLabel
)


class LayoutManagerDialog(QDialog):
    """Dialog for managing saved layouts (v2.9.84)."""
    
    def __init__(self, layout_manager, parent=None):
        """
        Initialize layout manager dialog.
        
        Args:
            layout_manager: LayoutManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.layout_manager = layout_manager
        self._build_ui()
    
    def _build_ui(self):
        """Build the dialog UI."""
        self.setWindowTitle("Manage Layouts")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Label
        label = QLabel(tr("layout_manager.lbl_saved_layouts"))
        layout.addWidget(label)
        
        # List widget
        self.list_widget = QListWidget()
        custom_layouts = self.layout_manager.get_saved_layouts()
        self.list_widget.addItems(custom_layouts)
        layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_load = QPushButton(tr("layout_manager.btn_load"))
        btn_delete = QPushButton(tr("layout_manager.btn_delete"))
        btn_reset = QPushButton(tr("layout_manager.btn_reset"))
        btn_close = QPushButton(tr("layout_manager.btn_close"))
        
        btn_layout.addWidget(btn_load)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Connect buttons
        btn_load.clicked.connect(self._load_selected)
        btn_delete.clicked.connect(self._delete_selected)
        btn_reset.clicked.connect(self._reset_all)
        btn_close.clicked.connect(self.accept)
    
    def _load_selected(self):
        """Load the selected layout."""
        current_item = self.list_widget.currentItem()
        if current_item:
            layout_name = current_item.text()
            if self.layout_manager.load_layout(layout_name):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Layout '{layout_name}' loaded."
                )
                self.accept()
    
    def _delete_selected(self):
        """Delete the selected layout."""
        current_item = self.list_widget.currentItem()
        if current_item:
            layout_name = current_item.text()
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete layout '{layout_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.layout_manager.delete_layout(layout_name)
                self.list_widget.takeItem(self.list_widget.row(current_item))
    
    def _reset_all(self):
        """Reset all layouts to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "This will delete all custom layouts and restore Standard preset. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.layout_manager.reset_to_defaults()
            self.list_widget.clear()
            QMessageBox.information(
                self,
                "Reset Complete",
                "Layouts reset to defaults."
            )
            self.accept()
    
    @staticmethod
    def show_layout_manager(layout_manager, parent=None):
        """
        Show layout manager dialog.
        
        Args:
            layout_manager: LayoutManager instance
            parent: Parent widget
        """
        dialog = LayoutManagerDialog(layout_manager, parent)
        dialog.exec()
