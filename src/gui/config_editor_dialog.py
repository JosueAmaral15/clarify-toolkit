#!/usr/bin/env python3
"""
Configuration Editor Dialog - v2.9.90

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

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.i18n.translator import tr

try:
    from src.config_manager import get_config
except ImportError:
    import sys
    sys.path.insert(0, ".")
    from src.config_manager import get_config

import yaml


class ConfigEditorDialog(QDialog):
    """
    Visual YAML editor dialog for config.yaml.
    
    Usage:
        dialog = ConfigEditorDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            print("Config saved!")
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
        self.original_yaml = None
        self._setup_ui()
        self._load_current_config()
        
    def _setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle(tr("config_editor.title"))
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(tr("config_editor.header"))
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel(
            "Edite o YAML abaixo. A validação é automática ao salvar.\n"
            "⚠️ Algumas configurações requerem reiniciar o aplicativo."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Editor groupbox
        editor_group = QGroupBox(tr("config_editor.group_editor"))
        editor_layout = QVBoxLayout()
        
        # YAML text editor
        self.editor = QTextEdit()
        editor_font = QFont("Consolas", 10)
        self.editor.setFont(editor_font)
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        editor_layout.addWidget(self.editor)
        
        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)
        
        # Hot reload indicator
        self.reload_indicator = QLabel()
        self.reload_indicator.setStyleSheet("color: orange; font-weight: bold;")
        self.reload_indicator.setWordWrap(True)
        self.reload_indicator.hide()
        layout.addWidget(self.reload_indicator)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_preview = QPushButton(tr("config_editor.btn_preview"))
        self.btn_preview.setToolTip("Validar YAML antes de salvar")
        self.btn_preview.clicked.connect(self._preview_config)
        
        self.btn_reset = QPushButton(tr("config_editor.btn_reset"))
        self.btn_reset.setToolTip("Restaurar configurações padrão")
        self.btn_reset.clicked.connect(self._reset_to_defaults)
        
        self.btn_save = QPushButton(tr("config_editor.btn_save"))
        self.btn_save.setToolTip("Salvar configurações (cria backup)")
        self.btn_save.clicked.connect(self._save_config)
        
        self.btn_cancel = QPushButton(tr("config_editor.btn_cancel"))
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_preview)
        button_layout.addWidget(self.btn_reset)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
        
    def _load_current_config(self):
        """Load current config.yaml into editor."""
        try:
            config_dict = self.config.get_all()
            self.original_yaml = yaml.dump(
                config_dict,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            self.editor.setPlainText(self.original_yaml)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao Carregar",
                f"Não foi possível carregar config.yaml:\n{e}"
            )
            self.reject()
    
    def _preview_config(self):
        """Validate YAML and show preview."""
        yaml_text = self.editor.toPlainText()
        
        try:
            # Parse YAML
            config_dict = yaml.safe_load(yaml_text)
            
            # Validate with schema (will raise ValidationError if invalid)
            import jsonschema
            jsonschema.validate(config_dict, self.config.SCHEMA)
            
            # Show success + preview
            preview_text = yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
            QMessageBox.information(
                self,
                "✅ Validação OK",
                f"YAML válido!\n\nPreview:\n{preview_text[:500]}..."
            )
            
            # Check if requires restart
            self._check_restart_required(config_dict)
            
        except yaml.YAMLError as e:
            QMessageBox.warning(
                self,
                "❌ YAML Inválido",
                f"Erro de sintaxe YAML:\n{e}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "❌ Validação Falhou",
                f"Configuração inválida:\n{e}"
            )
    
    def _check_restart_required(self, new_config: dict):
        """Check if any changed settings require app restart."""
        current_config = self.config.get_all()
        restart_needed = []
        
        for key in self.REQUIRES_RESTART:
            parts = key.split(".")
            new_val = new_config
            cur_val = current_config
            
            for part in parts:
                new_val = new_val.get(part, None)
                cur_val = cur_val.get(part, None)
            
            if new_val != cur_val:
                restart_needed.append(key)
        
        if restart_needed:
            self.reload_indicator.setText(
                f"⚠️ Requer reiniciar o app: {', '.join(restart_needed)}"
            )
            self.reload_indicator.show()
        else:
            self.reload_indicator.setText("✅ Hot reload: mudanças aplicadas imediatamente")
            self.reload_indicator.show()
    
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
                f"Backup criado em: {self.config.config_file}.backup"
            )
            
            self.accept()
            
        except yaml.YAMLError as e:
            QMessageBox.critical(
                self,
                "❌ Erro ao Salvar",
                f"YAML inválido:\n{e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Erro ao Salvar",
                f"Não foi possível salvar:\n{e}"
            )
    
    def _reset_to_defaults(self):
        """Reset config to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirmar Reset",
            "Tem certeza que deseja restaurar configurações padrão?\n\n"
            "Todas as alterações serão perdidas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            defaults_yaml = yaml.dump(
                self.config.DEFAULTS,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            self.editor.setPlainText(defaults_yaml)
            QMessageBox.information(
                self,
                "✅ Reset Completo",
                "Editor restaurado para configurações padrão.\n"
                "Clique em 'Save' para aplicar."
            )
