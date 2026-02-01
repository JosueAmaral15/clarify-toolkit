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

import sys
import jsonschema

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QMessageBox, QGroupBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import yaml

from src.i18n.translator import tr, tooltip_tr
    from src.config_manager import get_config
    from src.config_manager import get_config

    def _save_config(self):
        """Save edited config.yaml with validation."""
        yaml_text = self.editor.toPlainText()

        try:
            # Parse and validate
            config_dict = yaml.safe_load(yaml_text)
            import jsonschema

            jsonschema.validate(config_dict, self.config.SCHEMA)

            # Update config manager (creates backup automatically)
            self.config.update(config_dict, save=True)

            # Check restart
            self._check_restart_required(config_dict)

            QMessageBox.information(
                self,
                "✅ Salvo",
                "Configuração salva com sucesso!\n\n"
                f"Arquivo: {self.config.config_file}\n"
                f"Backup criado em: {self.config.config_file}.backup",
            )

            self.accept()

        except yaml.YAMLError as e:
            QMessageBox.critical(self, "❌ Erro ao Salvar", f"YAML inválido:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro ao Salvar", f"Não foi possível salvar:\n{e}")

    def _reset_to_defaults(self):
        """Reset config to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirmar Reset",
            "Tem certeza que deseja restaurar configurações padrão?\n\n" "Todas as alterações serão perdidas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            defaults_yaml = yaml.dump(
                self.config.DEFAULTS, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            self.editor.setPlainText(defaults_yaml)
            QMessageBox.information(
                self,
                "✅ Reset Completo",
                "Editor restaurado para configurações padrão.\n" "Clique em 'Save' para aplicar.",
            )
