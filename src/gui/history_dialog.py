"""
Operation History Dialog
Dialog para visualizar e gerenciar histórico de operações.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


from pathlib import Path
from typing import Optional, Dict, Any
        from datetime import datetime

from PySide6.QtWidgets import (
from PySide6.QtCore import Qt, Signal

from src.i18n.translator import tr, tooltip_tr

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
