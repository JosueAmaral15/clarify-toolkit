#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Preset Manager Widget - File list filter presets

Extracted from file_list_dock.py (v2.9.114 - Phase 2.4.3)
Handles saving, loading, exporting, and importing filter presets.

Features:
- Save/load presets to QSettings
- Export/import presets to/from JSON files
- Preset combo box management
- Auto-load on selection
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=line-too-long  # Long preset descriptions
# pylint: disable=broad-exception-caught  # File I/O robustness

from __future__ import annotations

import json
from typing import Dict, Any, List, Callable, Optional
from PySide6.QtCore import Signal, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QInputDialog, QFileDialog
)
from src.i18n.translator import tr


class PresetManager(QWidget):
    """Widget for managing filter presets."""

    preset_loaded = Signal(dict)  # Emitted when preset is loaded with filter dict
    preset_saved = Signal(str)    # Emitted when preset is saved with preset name

    def __init__(self, parent=None, settings_group: str = "FileListDock"):
        """
        Initialize preset manager.

        Args:
            parent: Parent widget
            settings_group: QSettings group for storing presets
        """
        super().__init__(parent)
        self.settings_group = settings_group
        self._get_filters_callback: Optional[Callable[[], Dict[str, Any]]] = None
        self._apply_filters_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._setup_ui()
        self._load_preset_list()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Preset combo box row
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel(tr("preset_manager.lbl_presets")))

        self.cmb_presets = QComboBox()
        self.cmb_presets.addItem(tr("preset_manager.combo_no_preset"))
        self.cmb_presets.currentIndexChanged.connect(self._on_preset_selected)
        combo_layout.addWidget(self.cmb_presets, stretch=1)

        layout.addLayout(combo_layout)

        # Preset buttons row
        button_layout = QHBoxLayout()

        self.btn_save = QPushButton(tr("preset_manager.btn_save"))
        self.btn_save.clicked.connect(self.save_preset)
        button_layout.addWidget(self.btn_save)

        self.btn_load = QPushButton(tr("preset_manager.btn_load"))
        self.btn_load.clicked.connect(self.load_preset)
        button_layout.addWidget(self.btn_load)

        self.btn_delete = QPushButton(tr("preset_manager.btn_delete"))
        self.btn_delete.clicked.connect(self.delete_preset)
        button_layout.addWidget(self.btn_delete)

        self.btn_export = QPushButton(tr("preset_manager.btn_export"))
        self.btn_export.clicked.connect(self.export_preset)
        button_layout.addWidget(self.btn_export)

        self.btn_import = QPushButton(tr("preset_manager.btn_import"))
        self.btn_import.clicked.connect(self.import_preset)
        button_layout.addWidget(self.btn_import)

        layout.addLayout(button_layout)

    def set_callbacks(
        self,
        get_filters: Callable[[], Dict[str, Any]],
        apply_filters: Callable[[Dict[str, Any]], None]
    ):
        """
        Set callbacks for getting and applying filters.

        Args:
            get_filters: Function that returns current filter dict
            apply_filters: Function that applies filter dict to widgets
        """
        self._get_filters_callback = get_filters
        self._apply_filters_callback = apply_filters

    def save_preset(self):
        """Save current filters as a preset."""
        if not self._get_filters_callback:
            QMessageBox.warning(self, tr("preset_manager.error_title"), tr("preset_manager.error_callback_not_set"))
            return

        preset_name, ok = QInputDialog.getText(
            self, tr("preset_manager.dialog_save_title"), tr("preset_manager.dialog_save_message")
        )
        if not ok or not preset_name.strip():
            return

        preset_name = preset_name.strip()
        filters = self._get_filters_callback()

        # Save to QSettings
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        settings.setValue(preset_name, json.dumps(filters))
        settings.endGroup()

        # Update combo box
        self._load_preset_list()
        self.cmb_presets.setCurrentText(preset_name)

        # Emit signal
        self.preset_saved.emit(preset_name)

        QMessageBox.information(
            self, tr("preset_manager.saved_title"), tr("preset_manager.saved_message").format(preset_name)
        )

    def load_preset(self):
        """Load selected preset."""
        preset_name = self.cmb_presets.currentText()
        if preset_name == tr("preset_manager.combo_no_preset"):
            QMessageBox.information(self, tr("preset_manager.no_preset_title"), tr("preset_manager.no_preset_load_message"))
            return

        if not self._apply_filters_callback:
            QMessageBox.warning(self, tr("preset_manager.error_title"), tr("preset_manager.error_callback_not_set"))
            return

        # Load from QSettings
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        preset_data = settings.value(preset_name, "")
        settings.endGroup()

        if not preset_data:
            QMessageBox.warning(self, tr("preset_manager.load_failed_title"), tr("preset_manager.load_failed_message").format(preset_name))
            return

        try:
            filters = json.loads(preset_data)
            self._apply_filters_callback(filters)
            self.preset_loaded.emit(filters)
            QMessageBox.information(
                self, tr("preset_manager.loaded_title"), tr("preset_manager.loaded_message").format(preset_name)
            )
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, tr("preset_manager.load_failed_title"), tr("preset_manager.load_error_message").format(e))

    def delete_preset(self):
        """Delete selected preset."""
        preset_name = self.cmb_presets.currentText()
        if preset_name == tr("preset_manager.combo_no_preset"):
            QMessageBox.information(self, tr("preset_manager.no_preset_title"), tr("preset_manager.no_preset_delete_message"))
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, tr("preset_manager.delete_confirm_title"),
            tr("preset_manager.delete_confirm_message").format(preset_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Delete from QSettings
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        settings.remove(preset_name)
        settings.endGroup()

        # Update combo box
        self._load_preset_list()

        QMessageBox.information(
            self, tr("preset_manager.deleted_title"), tr("preset_manager.deleted_message").format(preset_name)
        )

    def export_preset(self):
        """Export current filters to JSON file."""
        if not self._get_filters_callback:
            QMessageBox.warning(self, tr("preset_manager.error_title"), tr("preset_manager.error_callback_not_set"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, tr("preset_manager.dialog_export_title"), "", tr("preset_manager.dialog_export_filter")
        )
        if not file_path:
            return

        filters = self._get_filters_callback()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(filters, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self, tr("preset_manager.exported_title"), tr("preset_manager.exported_message").format(file_path)
            )
        except Exception as e:
            QMessageBox.critical(self, tr("preset_manager.export_failed_title"), tr("preset_manager.export_failed_message").format(e))

    def import_preset(self):
        """Import preset from JSON file."""
        if not self._apply_filters_callback:
            QMessageBox.warning(self, tr("preset_manager.error_title"), tr("preset_manager.error_callback_not_set"))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("preset_manager.dialog_import_title"), "", tr("preset_manager.dialog_import_filter")
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                filters = json.load(f)

            # Apply filters
            self._apply_filters_callback(filters)
            self.preset_loaded.emit(filters)

            # Ask if user wants to save as new preset
            reply = QMessageBox.question(
                self, tr("preset_manager.import_overwrite_title"),
                tr("preset_manager.import_overwrite_message").format(""),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                preset_name, ok = QInputDialog.getText(
                    self, tr("preset_manager.dialog_save_title"), tr("preset_manager.dialog_save_message")
                )
                if ok and preset_name.strip():
                    preset_name = preset_name.strip()
                    settings = QSettings("Clarify", self.settings_group)
                    settings.beginGroup("Presets")
                    settings.setValue(preset_name, json.dumps(filters))
                    settings.endGroup()
                    self._load_preset_list()
                    self.cmb_presets.setCurrentText(preset_name)
                    self.preset_saved.emit(preset_name)

            QMessageBox.information(self, tr("preset_manager.imported_title"), tr("preset_manager.imported_message"))
        except Exception as e:
            QMessageBox.critical(self, tr("preset_manager.import_failed_title"), tr("preset_manager.import_failed_message").format(e))

    def _load_preset_list(self):
        """Load preset names into combo box."""
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        preset_names = settings.childKeys()
        settings.endGroup()

        current_text = self.cmb_presets.currentText()

        # Block signals to prevent premature load_preset() call before set_callbacks()
        self.cmb_presets.blockSignals(True)
        self.cmb_presets.clear()
        self.cmb_presets.addItem(tr("preset_manager.combo_no_preset"))
        self.cmb_presets.addItems(sorted(preset_names))

        # Restore previous selection if still exists
        if current_text in preset_names:
            self.cmb_presets.setCurrentText(current_text)

        # Re-enable signals
        self.cmb_presets.blockSignals(False)

    def _on_preset_selected(self):
        """Handle preset selection change."""
        if self.cmb_presets.currentText() != tr("preset_manager.combo_no_preset"):
            self.load_preset()

    def get_preset_names(self) -> List[str]:
        """Get list of saved preset names."""
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        preset_names = settings.childKeys()
        settings.endGroup()
        return preset_names

    def get_current_preset_name(self) -> str:
        """Get currently selected preset name."""
        text = self.cmb_presets.currentText()
        return text if text != tr("preset_manager.combo_no_preset") else ""

    def set_current_preset(self, preset_name: str):
        """Set current preset selection."""
        if preset_name:
            index = self.cmb_presets.findText(preset_name)
            if index >= 0:
                self.cmb_presets.setCurrentIndex(index)
        else:
            self.cmb_presets.setCurrentIndex(0)

    def refresh(self):
        """Refresh preset list from settings."""
        self._load_preset_list()


__all__ = ['PresetManager']
