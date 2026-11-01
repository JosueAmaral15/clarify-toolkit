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
# pylint: disable=no-name-in-module  # Qt dynamic modules

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QGroupBox,
    QHBoxLayout, QLabel, QSlider, QVBoxLayout
)

from src.i18n.translator import tr
from src.appearance_defaults import (
    DEFAULT_WINDOW_OPACITY_PERCENT,
    normalize_opacity_percent,
)
from src.gui.window_settings import WindowSettings


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
        self.setWindowTitle(tr("transparency_dialog.window_title"))
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # Info label
        info_label = QLabel(
            "Window visibility uses opacity.\n"
            "0% = Fully transparent, 100% = Fully opaque"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Transparency group
        trans_group = QGroupBox(tr("transparency_dialog.group_transparency"))
        trans_layout = QVBoxLayout()

        # Slider
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel(tr("transparency_dialog.lbl_min")))

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self._get_saved_opacity())
        self.opacity_slider.setTickPosition(QSlider.TicksBelow)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.setAccessibleName("Window opacity percentage")
        self.opacity_slider.setAccessibleDescription(
            "Higher values make application windows more opaque and easier to read."
        )
        self.opacity_slider.valueChanged.connect(self._update_transparency_preview)
        slider_layout.addWidget(self.opacity_slider)

        slider_layout.addWidget(QLabel(tr("transparency_dialog.lbl_max")))
        trans_layout.addLayout(slider_layout)

        # Value display
        self.opacity_label = QLabel(self._opacity_summary(self.opacity_slider.value()))
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
        """Get saved opacity value from settings."""
        return normalize_opacity_percent(
            self.settings.get("window_opacity", DEFAULT_WINDOW_OPACITY_PERCENT)
        )

    @staticmethod
    def _opacity_summary(value: int) -> str:
        return f"Current opacity: {value}% ({100 - value}% transparent)"

    def _update_transparency_preview(self, value):
        """Update transparency in real-time for preview."""
        WindowSettings.apply_window_opacity_percent(self.main_window, value)
        self.opacity_label.setText(self._opacity_summary(value))

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
