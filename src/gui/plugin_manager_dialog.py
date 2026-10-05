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
# pylint: disable=no-name-in-module  # Qt dynamic modules


from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtCore import Slot
from src.i18n.translator import get_translator, tr


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
        get_translator().languageChanged.connect(self.retranslateUi)

    @Slot()
    def retranslateUi(self):  # pylint: disable=invalid-name
        self.setWindowTitle(tr("plugin_manager.window_title"))
        self.lbl_header.setText(tr("plugin_manager.lbl_header"))
        self.table.setHorizontalHeaderLabels([tr(f"plugin_manager.header_{key}")
                                             for key in ("enabled", "name", "version", "author", "description")])
        self.btn_refresh.setText(f"🔄 {tr('plugin_manager.btn_refresh')}")
        self.btn_close.setText(f"✅ {tr('plugin_manager.btn_close')}")
        self._update_info_label()

    def _build_ui(self):
        """Build the dialog UI."""
        self.setWindowTitle(tr("plugin_manager.window_title"))
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout()

        # Header
        lbl_header = QLabel(tr("plugin_manager.lbl_header"))
        self.lbl_header = lbl_header
        lbl_header.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(lbl_header)

        # Plugin table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [
                tr("plugin_manager.header_enabled"),
                tr("plugin_manager.header_name"),
                tr("plugin_manager.header_version"),
                tr("plugin_manager.header_author"),
                tr("plugin_manager.header_description"),
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        self._populate_table()
        layout.addWidget(self.table)

        # Info label
        metadata_list = self.plugin_loader.get_all_metadata()
        enabled_count = len([m for m in metadata_list if m.enabled])
        self.lbl_info = QLabel(f"📦 {len(metadata_list)} plugin(s) discovered | " f"{enabled_count} enabled")
        layout.addWidget(self.lbl_info)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton(f"🔄 {tr('plugin_manager.btn_refresh')}")
        self.btn_refresh = btn_refresh
        btn_refresh.clicked.connect(self._refresh_plugins)
        btn_close = QPushButton(f"✅ {tr('plugin_manager.btn_close')}")
        self.btn_close = btn_close
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self._update_info_label()

    def _populate_table(self):
        """Populate the plugin table with metadata."""
        metadata_list = self.plugin_loader.get_all_metadata()
        self.table.setRowCount(len(metadata_list))

        for row, metadata in enumerate(metadata_list):
            # Checkbox for enabled/disabled
            chk = QCheckBox()
            chk.setChecked(metadata.enabled)
            chk.toggled.connect(lambda enabled, pid=metadata.id: self._toggle_plugin(pid, enabled))
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
        success = self.plugin_loader.set_plugin_enabled(plugin_id, enabled)
        for row, metadata in enumerate(self.plugin_loader.get_all_metadata()):
            checkbox = self.table.cellWidget(row, 0)
            checkbox.blockSignals(True)
            checkbox.setChecked(metadata.enabled)
            checkbox.blockSignals(False)
        from .menu_builder import MenuBuilder  # pylint: disable=import-outside-toplevel
        if self.parent_window is not None:
            MenuBuilder.sync_plugin_actions(self.parent_window)
        if not success:
            QMessageBox.warning(self, tr("dialog.plugin_manager.activation_failed"),
                                tr("plugin_manager.toggle_failed").format(plugin_id))
        self._update_info_label()

    def _refresh_plugins(self):
        """
        Refresh plugin list (v2.9.109).

        Re-discovers plugins and updates the table.
        """
        self.plugin_loader.discover_plugins()
        self._populate_table()
        self._update_info_label()

        QMessageBox.information(self, tr("dialog.plugin_manager.refreshed"), tr("plugin_manager.refreshed"))

    def _update_info_label(self):
        """Update the info label with current plugin counts."""
        metadata_list = self.plugin_loader.get_all_metadata()
        enabled_count = len([m for m in metadata_list if m.enabled])
        self.lbl_info.setText(tr("plugin_manager.counts").format(len(metadata_list), enabled_count))

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
