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

from __future__ import annotations

import json
from typing import Dict, Any, List, Callable, Optional
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QMessageBox, QInputDialog, QFileDialog
)


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
        combo_layout.addWidget(QLabel("Presets:"))
        
        self.cmb_presets = QComboBox()
        self.cmb_presets.addItem("-- No Preset --")
        self.cmb_presets.currentIndexChanged.connect(self._on_preset_selected)
        combo_layout.addWidget(self.cmb_presets, stretch=1)
        
        layout.addLayout(combo_layout)
        
        # Preset buttons row
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_preset)
        button_layout.addWidget(self.btn_save)
        
        self.btn_load = QPushButton("Load")
        self.btn_load.clicked.connect(self.load_preset)
        button_layout.addWidget(self.btn_load)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_preset)
        button_layout.addWidget(self.btn_delete)
        
        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.export_preset)
        button_layout.addWidget(self.btn_export)
        
        self.btn_import = QPushButton("Import")
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
            QMessageBox.warning(self, "Error", "Get filters callback not set!")
            return
        
        preset_name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter preset name:"
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
            self, "Saved", f"Preset '{preset_name}' saved successfully!"
        )
    
    def load_preset(self):
        """Load selected preset."""
        preset_name = self.cmb_presets.currentText()
        if preset_name == "-- No Preset --":
            QMessageBox.information(self, "No Preset", "Please select a preset to load.")
            return
        
        if not self._apply_filters_callback:
            QMessageBox.warning(self, "Error", "Apply filters callback not set!")
            return
        
        # Load from QSettings
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        preset_data = settings.value(preset_name, "")
        settings.endGroup()
        
        if not preset_data:
            QMessageBox.warning(self, "Load Failed", f"Preset '{preset_name}' not found.")
            return
        
        try:
            filters = json.loads(preset_data)
            self._apply_filters_callback(filters)
            self.preset_loaded.emit(filters)
            QMessageBox.information(
                self, "Loaded", f"Preset '{preset_name}' loaded successfully!"
            )
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Load Failed", f"Invalid preset data: {e}")
    
    def delete_preset(self):
        """Delete selected preset."""
        preset_name = self.cmb_presets.currentText()
        if preset_name == "-- No Preset --":
            QMessageBox.information(self, "No Preset", "Please select a preset to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Preset",
            f"Are you sure you want to delete preset '{preset_name}'?",
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
            self, "Deleted", f"Preset '{preset_name}' deleted successfully!"
        )
    
    def export_preset(self):
        """Export current filters to JSON file."""
        if not self._get_filters_callback:
            QMessageBox.warning(self, "Error", "Get filters callback not set!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Preset", "", "JSON Files (*.json)"
        )
        if not file_path:
            return
        
        filters = self._get_filters_callback()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(filters, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self, "Exported", f"Preset exported to:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export: {e}")
    
    def import_preset(self):
        """Import preset from JSON file."""
        if not self._apply_filters_callback:
            QMessageBox.warning(self, "Error", "Apply filters callback not set!")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Preset", "", "JSON Files (*.json)"
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
                self, "Save Preset?",
                "Do you want to save this as a new preset?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                preset_name, ok = QInputDialog.getText(
                    self, "Save Preset", "Enter preset name:"
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
            
            QMessageBox.information(self, "Imported", "Preset imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", f"Failed to import: {e}")
    
    def _load_preset_list(self):
        """Load preset names into combo box."""
        settings = QSettings("Clarify", self.settings_group)
        settings.beginGroup("Presets")
        preset_names = settings.childKeys()
        settings.endGroup()
        
        current_text = self.cmb_presets.currentText()
        self.cmb_presets.clear()
        self.cmb_presets.addItem("-- No Preset --")
        self.cmb_presets.addItems(sorted(preset_names))
        
        # Restore previous selection if still exists
        if current_text in preset_names:
            self.cmb_presets.setCurrentText(current_text)
    
    def _on_preset_selected(self):
        """Handle preset selection change."""
        if self.cmb_presets.currentText() != "-- No Preset --":
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
        return text if text != "-- No Preset --" else ""
    
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
