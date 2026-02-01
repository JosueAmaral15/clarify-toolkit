"""
Operation Presets Dialog
Dialog para gerenciar presets de operações.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=broad-exception-caught  # GUI robustness

from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QGroupBox, QHBoxLayout, QInputDialog,
    QLabel, QListWidget, QMessageBox, QPushButton,
    QTextEdit, QVBoxLayout
)


class PresetsDialog(QDialog):
    """Dialog para gerenciar presets de operações."""

    # Signal emitido quando usuário quer carregar um preset
    preset_load_requested = Signal(dict)

    def __init__(self, presets_manager, parent=None):
        """
        Inicializa o dialog.

        Args:
            presets_manager: Instância do PresetsManager
            parent: Widget pai
        """
        super().__init__(parent)
        self.presets_manager = presets_manager
        self.setWindowTitle("Operation Presets")
        self.resize(700, 500)

        self._setup_ui()
        self._load_presets()

    def _setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)

        # Label informativo
        info_label = QLabel(
            "📋 Saved presets for Set Operations\n"
            "Select a preset to view details or load it"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Lista de presets
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_load_clicked)
        layout.addWidget(self.list_widget)

        # Área de detalhes
        details_group = QGroupBox("Preset Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)

        layout.addWidget(details_group)

        # Botões de ação
        buttons_layout = QHBoxLayout()

        self.btn_load = QPushButton("✅ Load Preset")
        self.btn_load.setToolTip("Load selected preset into Set Operations")
        self.btn_load.clicked.connect(self._on_load_clicked)
        self.btn_load.setEnabled(False)
        buttons_layout.addWidget(self.btn_load)

        self.btn_rename = QPushButton("✏️ Rename")
        self.btn_rename.setToolTip("Rename selected preset")
        self.btn_rename.clicked.connect(self._on_rename_clicked)
        self.btn_rename.setEnabled(False)
        buttons_layout.addWidget(self.btn_rename)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setToolTip("Delete selected preset")
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        self.btn_delete.setEnabled(False)
        buttons_layout.addWidget(self.btn_delete)

        buttons_layout.addStretch()

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)

        layout.addLayout(buttons_layout)

    def _load_presets(self):
        """Carrega presets na lista."""
        self.list_widget.clear()
        self.details_text.clear()

        presets = self.presets_manager.get_presets()

        if not presets:
            self.list_widget.addItem("(No presets saved)")
            return

        # Adiciona cada preset
        for preset in presets:
            name = preset.get("name", "Unnamed")
            self.list_widget.addItem(name)

    def _on_selection_changed(self, current_row: int):
        """
        Callback quando seleção muda.

        Args:
            current_row: Índice da linha selecionada
        """
        if current_row < 0:
            self.details_text.clear()
            self.btn_load.setEnabled(False)
            self.btn_rename.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return

        # Obtém preset selecionado
        preset_name = self.list_widget.item(current_row).text()
        preset = self.presets_manager.get_preset(preset_name)

        if not preset:
            self.details_text.clear()
            self.btn_load.setEnabled(False)
            self.btn_rename.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return

        # Exibe detalhes
        details = self._format_details(preset)
        self.details_text.setPlainText(details)

        self.btn_load.setEnabled(True)
        self.btn_rename.setEnabled(True)
        self.btn_delete.setEnabled(True)

    def _format_details(self, preset: Dict[str, Any]) -> str:
        """
        Formata detalhes do preset.

        Args:
            preset: Dicionário com dados do preset

        Returns:
            String formatada com detalhes
        """
        try:
            # Mapeamento de símbolos para nomes
            op_names = {
                "∩": "Intersection",
                "∪": "Union",
                "−": "Difference",
                "⊕": "Symmetric Difference"
            }

            mode_names = {
                "key_value": "Key + Value",
                "full_path_value": "Full Path + Value",
                "key_only": "Key Only"
            }

            details = f"""Operation: {op_names.get(preset['operation_type'], preset['operation_type'])}
Comparison Mode: {mode_names.get(preset['comparison_mode'], preset['comparison_mode'])}

Options:
  • Ignore Case (Keys): {'Yes' if preset.get('ignore_case_keys', False) else 'No'}
  • Ignore Case (Values): {'Yes' if preset.get('ignore_case_values', False) else 'No'}
  • Skip Empty Values: {'Yes' if preset.get('skip_empty', True) else 'No'}
  • Ignore Array Order: {'Yes' if preset.get('arrays_ignore_order', False) else 'No'}"""

            # Adiciona arquivos favoritos se houver
            favorite_files = preset.get('favorite_files', [])
            if favorite_files:
                details += f"\n\nFavorite Files: {len(favorite_files)} file(s)"

            return details

        except Exception as e:
            return f"Error formatting details: {e}"

    def _on_load_clicked(self):
        """Callback para carregar preset."""
        current_row = self.list_widget.currentRow()

        if current_row < 0:
            return

        preset_name = self.list_widget.item(current_row).text()
        preset = self.presets_manager.get_preset(preset_name)

        if not preset:
            QMessageBox.warning(
                self,
                "Load Error",
                "Could not retrieve preset data."
            )
            return

        # Emite signal para carregar preset
        self.preset_load_requested.emit(preset)

        # Fecha dialog
        self.accept()

    def _on_rename_clicked(self):
        """Callback para renomear preset."""
        current_row = self.list_widget.currentRow()

        if current_row < 0:
            return

        old_name = self.list_widget.item(current_row).text()

        # Solicita novo nome
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Preset",
            "Enter new name:",
            text=old_name
        )

        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()

        # Verifica se nome já existe
        if new_name != old_name and self.presets_manager.get_preset(new_name):
            QMessageBox.warning(
                self,
                "Rename Error",
                f"A preset named '{new_name}' already exists."
            )
            return

        # Renomeia
        success = self.presets_manager.rename_preset(old_name, new_name)

        if success:
            self._load_presets()

            # Re-seleciona item renomeado
            items = self.list_widget.findItems(new_name, Qt.MatchExactly)
            if items:
                self.list_widget.setCurrentItem(items[0])
        else:
            QMessageBox.critical(
                self,
                "Rename Error",
                "Failed to rename preset."
            )

    def _on_delete_clicked(self):
        """Callback para deletar preset."""
        current_row = self.list_widget.currentRow()

        if current_row < 0:
            return

        preset_name = self.list_widget.item(current_row).text()

        # Confirmação
        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f"Are you sure you want to delete preset '{preset_name}'?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.presets_manager.delete_preset(preset_name)

            if success:
                self._load_presets()
                QMessageBox.information(
                    self,
                    "Preset Deleted",
                    f"Preset '{preset_name}' has been deleted."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Delete Error",
                    "Failed to delete preset."
                )
