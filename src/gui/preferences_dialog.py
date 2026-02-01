#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Preferences Dialog for Clarify
-------------------------------
Dialog for managing application preferences including tooltips,
auto-save, exit confirmation, and update checker settings.

Phase 3.10 - Dialog Extraction
Author: Josué Amaral
Date: 2025-12-24
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QGroupBox,
    QDialogButtonBox, QMessageBox
)
from src.i18n.translator import tr


class PreferencesDialog(QDialog):
    """Dialog for managing application preferences."""

    def __init__(self, settings, parent=None):
        """
        Initialize preferences dialog.

        Args:
            settings: SettingsManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings = settings
        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI."""
        self.setWindowTitle(tr("dialog.preferences.title"))
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        # General settings group
        general_group = QGroupBox(tr("dialog.preferences.general"))
        general_layout = QVBoxLayout()

        # Tooltips checkbox
        self.chk_tooltips = QCheckBox(tr("dialog.preferences.show_tooltips"))
        self.chk_tooltips.setChecked(self.settings.get("show_tooltips", True))

        # Confirm exit checkbox
        self.chk_confirm_exit = QCheckBox(tr("dialog.preferences.confirm_exit"))
        self.chk_confirm_exit.setChecked(self.settings.get("confirm_on_exit", True))
        self.chk_confirm_exit.setToolTip(
            "Show confirmation dialog when closing the application. "
            "You can also disable this by checking 'Don't show this message again' "
            "in the exit confirmation dialog."
        )

        # Auto-save checkbox
        self.chk_auto_save = QCheckBox(tr("dialog.preferences.auto_save"))
        self.chk_auto_save.setChecked(self.settings.get("auto_save", True))

        # Update checker preference (v2.9.45)
        self.chk_check_updates = QCheckBox(tr("dialog.preferences.check_updates"))
        self.chk_check_updates.setChecked(
            self.settings.qsettings.value("update_checker/enabled", True, type=bool)
        )
        self.chk_check_updates.setToolTip(
            "Automatically check for new Clarify versions when app starts "
            "(checks at most once per 24 hours)"
        )

        # Add checkboxes to layout
        general_layout.addWidget(self.chk_tooltips)
        general_layout.addWidget(self.chk_confirm_exit)
        general_layout.addWidget(self.chk_auto_save)
        general_layout.addWidget(self.chk_check_updates)
        general_group.setLayout(general_layout)

        layout.addWidget(general_group)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def _save_and_close(self):
        """Save preferences and close dialog (v2.9.45: includes check_updates)."""
        # Save general settings
        self.settings.update_multiple({
            "show_tooltips": self.chk_tooltips.isChecked(),
            "confirm_on_exit": self.chk_confirm_exit.isChecked(),
            "auto_save": self.chk_auto_save.isChecked()
        })

        # Save update checker preference to QSettings (v2.9.45)
        self.settings.qsettings.setValue(
            "update_checker/enabled",
            self.chk_check_updates.isChecked()
        )

        self.accept()
        QMessageBox.information(
            self.parent(),
            tr("dialog.preferences.title"),
            tr("dialog.preferences.success")
        )

    @staticmethod
    def show_preferences(settings, parent=None):
        """
        Show preferences dialog.

        Args:
            settings: SettingsManager instance
            parent: Parent widget
        """
        dialog = PreferencesDialog(settings, parent)
        dialog.exec()
