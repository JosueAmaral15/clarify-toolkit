"""
Operation History Dialog
Dialog para visualizar e gerenciar histórico de operações.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QLabel,
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path
from typing import Optional, Dict, Any
from src.i18n.translator import tr, tooltip_tr


class HistoryDialog(QDialog):
    """Dialog para exibir histórico de operações."""

    # Signal emitido quando usuário quer re-executar uma operação
    re_execute_requested = Signal(dict)

    def __init__(self, history_manager, parent=None):
        """
        Inicializa o dialog.

        Args:
            history_manager: Instância do HistoryManager
            parent: Widget pai
        """
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle(tr("history_dialog.title"))
        self.resize(800, 500)

        self._setup_ui()
        self._load_history()

    def _setup_ui(self):
        """Configura a interface."""
        layout = QVBoxLayout(self)

        # Label informativo
        info_label = QLabel(
            "📜 Last 50 operations (most recent first)\n" "Select an operation to view details or re-execute it"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Lista de operações
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_re_execute_clicked)
        layout.addWidget(self.list_widget)

        # Área de detalhes
        details_label = QLabel(tr("history_dialog.lbl_details"))
        layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(120)
        layout.addWidget(self.details_text)

        # Botões de ação
        buttons_layout = QHBoxLayout()

        self.btn_re_execute = QPushButton(tr("history_dialog.btn_re_execute"))
        self.btn_re_execute.setToolTip(tooltip_tr("history.tooltip_re_execute"))
        self.btn_re_execute.clicked.connect(self._on_re_execute_clicked)
        self.btn_re_execute.setEnabled(False)
        buttons_layout.addWidget(self.btn_re_execute)

        self.btn_export = QPushButton(tr("history_dialog.btn_export"))
        self.btn_export.setToolTip(tooltip_tr("history.tooltip_export"))
        self.btn_export.clicked.connect(self._on_export_clicked)
        buttons_layout.addWidget(self.btn_export)

        self.btn_clear = QPushButton(tr("history_dialog.btn_clear"))
        self.btn_clear.setToolTip(tooltip_tr("history.tooltip_clear"))
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        buttons_layout.addWidget(self.btn_clear)

        buttons_layout.addStretch()

        self.btn_close = QPushButton(tr("history_dialog.btn_close"))
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)

        layout.addLayout(buttons_layout)

    def _load_history(self):
        """Carrega histórico na lista."""
        self.list_widget.clear()
        self.details_text.clear()

        history = self.history_manager.get_history()

        if not history:
            self.list_widget.addItem(tr("history_dialog.no_operations"))
            self.btn_export.setEnabled(False)
            self.btn_clear.setEnabled(False)
            return

        # Adiciona cada operação
        for entry in history:
            display_text = self.history_manager.format_entry_display(entry)
            self.list_widget.addItem(display_text)

        self.btn_export.setEnabled(True)
        self.btn_clear.setEnabled(True)

    def _on_selection_changed(self, current_row: int):
        """
        Callback quando seleção muda.

        Args:
            current_row: Índice da linha selecionada
        """
        if current_row < 0:
            self.details_text.clear()
            self.btn_re_execute.setEnabled(False)
            return

        entry = self.history_manager.get_entry(current_row)

        if not entry:
            self.details_text.clear()
            self.btn_re_execute.setEnabled(False)
            return

        # Exibe detalhes
        details = self._format_details(entry)
        self.details_text.setPlainText(details)

        self.btn_re_execute.setEnabled(True)

    def _format_details(self, entry: Dict[str, Any]) -> str:
        """
        Formata detalhes da operação.

        Args:
            entry: Dicionário com dados da operação

        Returns:
            String formatada com detalhes
        """
        from datetime import datetime

        try:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            time_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")

            details = f"""Operation Type: {entry['operation_type']}
Executed: {time_str}
File 1: {entry['file1']}
File 2: {entry['file2']}
Comparison Mode: {entry['comparison_mode']}
Results: {entry['result_count']} items"""

            return details

        except Exception as e:
            return f"Error formatting details: {e}"

    def _on_re_execute_clicked(self):
        """Callback para re-executar operação."""
        current_row = self.list_widget.currentRow()

        if current_row < 0:
            return

        entry = self.history_manager.get_entry(current_row)

        if not entry:
            QMessageBox.warning(self, tr("history.reexecute_error_title"), tr("history.reexecute_no_data"))
            return

        # Verifica se arquivos ainda existem
        if not Path(entry["file1"]).exists():
            QMessageBox.warning(
                self, tr("history.file_not_found_title"), tr("history.file1_not_found").format(file=entry["file1"])
            )
            return

        if not Path(entry["file2"]).exists():
            QMessageBox.warning(
                self, tr("history.file_not_found_title"), tr("history.file2_not_found").format(file=entry["file2"])
            )
            return

        # Emite signal para re-executar
        self.re_execute_requested.emit(entry)

        # Fecha dialog
        self.accept()

    def _on_export_clicked(self):
        """Callback para exportar histórico."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export History", "operation_history.json", "JSON Files (*.json)"
        )

        if not filepath:
            return

        # Garante extensão .json
        filepath = str(Path(filepath).with_suffix(".json"))

        success = self.history_manager.export_history(filepath)

        if success:
            QMessageBox.information(
                self, tr("history.export_success_title"), tr("history.export_success").format(filepath=filepath)
            )
        else:
            QMessageBox.critical(self, tr("history.export_error_title"), tr("history.export_error"))

    def _on_clear_clicked(self):
        """Callback para limpar histórico."""
        reply = QMessageBox.question(
            self,
            tr("history.clear_title"),
            tr("history.clear_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            self._load_history()

            QMessageBox.information(self, tr("history.cleared_title"), tr("history.cleared"))
