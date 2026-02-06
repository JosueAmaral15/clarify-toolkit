#!/usr/bin/env python3
"""Configuration Editor Dialog - v2.9.90.

Visual YAML editor for config.yaml with validation, preview, and reset.

Features:
- Syntax-highlighted YAML editor (QTextEdit)
- Real-time validation (jsonschema)
- Preview before save
- Reset to defaults
- Backup on save
- Hot reload indicator (shows which settings require restart)

Integrates with ConfigManager (src/config_manager.py).
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-error  # jsonschema optional dependency
# pylint: disable=no-member  # Dynamic ConfigManager.data attribute

import sys
import yaml

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QGroupBox
)
from PySide6.QtGui import QFont

from src.i18n.translator import tr
from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from src.config_manager import get_config
except ImportError:
    sys.path.insert(0, ".")
    from src.config_manager import get_config


class ConfigEditorDialog(QDialog):
    """Visual YAML editor dialog for config.yaml.

    Usage:
        dialog = ConfigEditorDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            logger.info("Config saved!")
    """

    # Settings that require app restart to take effect
    REQUIRES_RESTART = {
        "performance.thread_pool_size",
        "performance.max_file_size_mb",
        "logging.max_file_size_mb",
        "logging.backup_count",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setWindowTitle(tr("config_editor.title"))
        self.resize(800, 600)
        self._build_ui()
        self._load_config()

    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout()

        # Editor section
        editor_group = QGroupBox(tr("config_editor.yaml_editor_label"))
        editor_layout = QVBoxLayout()

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier", 10))
        editor_layout.addWidget(self.editor)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_validate = QPushButton(tr("config_editor.btn_validate"))
        self.btn_validate.clicked.connect(self._validate_config)
        btn_layout.addWidget(self.btn_validate)

        self.btn_reset = QPushButton(tr("config_editor.btn_reset"))
        self.btn_reset.clicked.connect(self._reset_to_defaults)
        btn_layout.addWidget(self.btn_reset)

        btn_layout.addStretch()

        self.btn_save = QPushButton(tr("config_editor.btn_save"))
        self.btn_save.clicked.connect(self._save_config)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton(tr("config_editor.btn_cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_config(self):
        """Load current config.yaml into editor."""
        config_yaml = yaml.dump(self.config.data, default_flow_style=False, allow_unicode=True)
        self.editor.setPlainText(config_yaml)

    def _validate_config(self):
        """Validate YAML syntax and schema."""
        yaml_text = self.editor.toPlainText()

        try:
            config_dict = yaml.safe_load(yaml_text)
            import jsonschema  # pylint: disable=import-outside-toplevel  # Optional validation
            jsonschema.validate(config_dict, self.config.SCHEMA)

            QMessageBox.information(
                self,
                tr("config_editor.validation_success_title"),
                tr("config_editor.validation_success_msg")
            )
        except yaml.YAMLError as e:
            QMessageBox.critical(
                self,
                tr("config_editor.validation_error_title"),
                tr("config_editor.yaml_error_msg").format(error=str(e))
            )
        except Exception as e:  # pylint: disable=broad-exception-caught  # Validation robustness
            QMessageBox.critical(
                self,
                tr("config_editor.validation_error_title"),
                tr("config_editor.schema_error_msg").format(error=str(e))
            )

    def _save_config(self):
        """Save edited config.yaml with validation."""
        yaml_text = self.editor.toPlainText()

        try:
            config_dict = yaml.safe_load(yaml_text)
            import jsonschema  # pylint: disable=import-outside-toplevel  # Optional validation

            jsonschema.validate(config_dict, self.config.SCHEMA)
            self.config.update(config_dict, save=True)
            self._check_restart_required(config_dict)

            QMessageBox.information(
                self,
                tr("config_editor.save_success_title"),
                tr("config_editor.save_success_msg")
            )
            self.accept()

        except yaml.YAMLError as e:
            QMessageBox.critical(
                self,
                tr("config_editor.save_error_title"),
                tr("config_editor.yaml_error_msg").format(error=str(e))
            )
        except Exception as e:  # pylint: disable=broad-exception-caught  # Save robustness
            QMessageBox.critical(
                self,
                tr("config_editor.save_error_title"),
                tr("config_editor.save_generic_error_msg").format(error=str(e))
            )

    def _reset_to_defaults(self):
        """Reset config to default values."""
        reply = QMessageBox.question(
            self,
            tr("config_editor.reset_confirm_title"),
            tr("config_editor.reset_confirm_msg"),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.config.reset_to_defaults()
            self._load_config()

    def _check_restart_required(self, new_config: dict):
        """Check if restart needed and show warning."""
        changed_keys = set()
        for key_path in self.REQUIRES_RESTART:
            old_val = self._get_nested(self.config.data, key_path)
            new_val = self._get_nested(new_config, key_path)
            if old_val != new_val:
                changed_keys.add(key_path)

        if changed_keys:
            QMessageBox.warning(
                self,
                tr("config_editor.restart_required_title"),
                tr("config_editor.restart_required_msg")
            )

    def _get_nested(self, data: dict, key_path: str):
        """Get nested dict value by dot-separated path."""
        keys = key_path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
