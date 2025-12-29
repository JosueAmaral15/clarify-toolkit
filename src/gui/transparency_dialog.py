#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transparency Dialog for Clarify
--------------------------------
Dialog for configuring window transparency with live preview.

Phase 3.10 - Dialog Extraction
Author: Josué Amaral
Date: 2025-12-24
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QGroupBox, QDialogButtonBox
)
from PySide6.QtCore import Qt


class TransparencyDialog(QDialog):
    """Dialog for configuring window transparency with live preview."""
    
    def __init__(self, main_window, parent=None):
        """
        Initialize transparency dialog.
        
        Args:
            main_window: MainWindow instance (for preview updates)
            parent: Parent widget (defaults to main_window if None)
        """
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.settings = main_window.settings
        self.opacity_slider = None
        self.opacity_label = None
        self._build_ui()
    
    def _build_ui(self):
        """Build the dialog UI."""
        self.setWindowTitle("Window Transparency")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            "Adjust the transparency level for all windows and docks.\n"
            "0% = Fully transparent, 100% = Fully opaque"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Transparency group
        trans_group = QGroupBox(tr("transparency_dialog.group_transparency"))
        trans_layout = QVBoxLayout()
        
        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("0%"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self._get_saved_opacity())
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.valueChanged.connect(self._update_transparency_preview)
        slider_layout.addWidget(self.opacity_slider)
        
        slider_layout.addWidget(QLabel("100%"))
        trans_layout.addLayout(slider_layout)
        
        # Value display
        self.opacity_label = QLabel(f"Current: {self.opacity_slider.value()}%")
        self.opacity_label.setAlignment(Qt.AlignCenter)
        self.opacity_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        trans_layout.addWidget(self.opacity_label)
        
        trans_group.setLayout(trans_layout)
        layout.addWidget(trans_group)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self._cancel_and_close)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
    
    def _get_saved_opacity(self):
        """Get saved opacity value from settings (default 100%)."""
        return int(self.settings.get("window_opacity", 100))
    
    def _update_transparency_preview(self, value):
        """Update transparency in real-time for preview."""
        opacity = value / 100.0
        self.main_window.setWindowOpacity(opacity)
        self.opacity_label.setText(f"Current: {value}%")
        
        # Apply to all existing docks
        dock_names = [
            'dock_translate', 'dock_rewriter', 'dock_text_extractor',
            'dock_placeholder_replacer', 'dock_ai_processor',
            'dock_json_search', 'dock_case_converter', 'dock_history'
        ]
        for dock_name in dock_names:
            if hasattr(self.main_window, dock_name):
                dock = getattr(self.main_window, dock_name)
                if dock:
                    dock.setWindowOpacity(opacity)
    
    def _save_and_close(self):
        """Save transparency setting and close dialog."""
        value = self.opacity_slider.value()
        self.settings.set("window_opacity", value)
        self.accept()
    
    def _cancel_and_close(self):
        """Restore previous transparency and close dialog."""
        saved_opacity = self._get_saved_opacity()
        self._update_transparency_preview(saved_opacity)
        self.reject()
    
    @staticmethod
    def show_transparency_dialog(main_window):
        """
        Show transparency dialog.
        
        Args:
            main_window: MainWindow instance
        """
        dialog = TransparencyDialog(main_window)
        dialog.exec()
