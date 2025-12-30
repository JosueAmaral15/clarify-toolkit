#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Manager Dialog for Clarify
----------------------------------
Dialog for managing plugins: enable/disable, view metadata, refresh.

Phase 3.10 - Dialog Extraction
Author: Josué Amaral
Date: 2025-12-24
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from src.i18n.translator import tr


class PluginManagerDialog(QDialog):
    """
    Dialog for managing plugins (v2.9.109).
    
    Lists all discovered plugins with:
    - Name, version, author, description
    - Enable/disable toggle
    - Dependencies list
    """
    
    def __init__(self, plugin_loader, parent=None):
        """
        Initialize plugin manager dialog.
        
        Args:
            plugin_loader: PluginLoader instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.plugin_loader = plugin_loader
        self.parent_window = parent
        self._build_ui()
    
    def _build_ui(self):
        """Build the dialog UI."""
        self.setWindowTitle(tr("plugin_manager.window_title"))
        self.setMinimumSize(700, 400)
        
        layout = QVBoxLayout()
        
        # Header
        lbl_header = QLabel(tr("plugin_manager.lbl_header"))
        lbl_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(lbl_header)
        
        # Plugin table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Enabled", "Name", "Version", "Author", "Description"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        self._populate_table()
        layout.addWidget(self.table)
        
        # Info label
        metadata_list = self.plugin_loader.get_all_metadata()
        enabled_count = len([m for m in metadata_list if m.enabled])
        self.lbl_info = QLabel(
            f"📦 {len(metadata_list)} plugin(s) discovered | "
            f"{enabled_count} enabled"
        )
        layout.addWidget(self.lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton(f"🔄 {tr('plugin_manager.btn_refresh')}")
        btn_refresh.clicked.connect(self._refresh_plugins)
        btn_close = QPushButton(f"✅ {tr('plugin_manager.btn_close')}")
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _populate_table(self):
        """Populate the plugin table with metadata."""
        metadata_list = self.plugin_loader.get_all_metadata()
        self.table.setRowCount(len(metadata_list))
        
        for row, metadata in enumerate(metadata_list):
            # Checkbox for enabled/disabled
            chk = QCheckBox()
            chk.setChecked(metadata.enabled)
            chk.stateChanged.connect(
                lambda state, pid=metadata.id: self._toggle_plugin(pid, state == Qt.Checked)
            )
            self.table.setCellWidget(row, 0, chk)
            
            # Name
            self.table.setItem(row, 1, QTableWidgetItem(metadata.name))
            
            # Version
            self.table.setItem(row, 2, QTableWidgetItem(metadata.version))
            
            # Author
            self.table.setItem(row, 3, QTableWidgetItem(metadata.author))
            
            # Description
            self.table.setItem(row, 4, QTableWidgetItem(metadata.description))
    
    def _toggle_plugin(self, plugin_id: str, enabled: bool):
        """
        Toggle plugin enabled state (v2.9.109).
        
        Args:
            plugin_id: Plugin identifier
            enabled: Enable (True) or disable (False)
        """
        self.plugin_loader.enable_plugin(plugin_id, enabled)
        
        if enabled:
            # Activate plugin
            success = self.plugin_loader.activate_plugin(plugin_id)
            if not success:
                QMessageBox.warning(
                    self,
                    "Activation Failed",
                    f"Failed to activate plugin '{plugin_id}'. Check logs for details."
                )
        else:
            # Deactivate plugin
            self.plugin_loader.deactivate_plugin(plugin_id)
        
        # Update info label
        self._update_info_label()
    
    def _refresh_plugins(self):
        """
        Refresh plugin list (v2.9.109).
        
        Re-discovers plugins and updates the table.
        """
        self.plugin_loader.discover_plugins()
        self._populate_table()
        self._update_info_label()
        
        QMessageBox.information(
            self,
            "Plugins Refreshed",
            "Plugin list has been refreshed."
        )
    
    def _update_info_label(self):
        """Update the info label with current plugin counts."""
        metadata_list = self.plugin_loader.get_all_metadata()
        enabled_count = len([m for m in metadata_list if m.enabled])
        self.lbl_info.setText(
            f"📦 {len(metadata_list)} plugin(s) discovered | "
            f"{enabled_count} enabled"
        )
    
    @staticmethod
    def show_plugin_manager(plugin_loader, parent=None):
        """
        Show plugin manager dialog.
        
        Args:
            plugin_loader: PluginLoader instance
            parent: Parent widget
        """
        dialog = PluginManagerDialog(plugin_loader, parent)
        dialog.exec()
