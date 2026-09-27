"""Example plugin: Export JSON to CSV format."""
# pylint: disable=no-name-in-module  # PySide6 has dynamic module structure
# pylint: disable=import-error  # Example plugin - imports may not resolve in all contexts
# pylint: disable=too-few-public-methods  # Example plugin - single activate method sufficient
# pylint: disable=wrong-import-position  # Path manipulation required before local imports
import sys
import os
import csv

from PySide6.QtWidgets import QFileDialog, QMessageBox

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from plugins.plugin_base import PluginBase


class ExportCSVPlugin(PluginBase):
    """Plugin to export current JSON data to CSV format."""
    name = "Exportar JSON para CSV"
    description = "Exporta o JSON atual para um arquivo CSV."

    def activate(self, app):
        """Export JSON to CSV file."""
        data = app.get_current_json()
        if not data:
            QMessageBox.warning(app, "Exportar CSV", "Nenhum JSON carregado.")
            return
        path, _ = QFileDialog.getSaveFileName(app, "Salvar CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if isinstance(data, dict):
                    writer.writerow(data.keys())
                    writer.writerow(data.values())
                elif isinstance(data, list) and data and isinstance(data[0], dict):
                    writer.writerow(data[0].keys())
                    for row in data:
                        writer.writerow(row.values())
                else:
                    QMessageBox.warning(app, "Exportar CSV", "Formato de dados não suportado.")
                    return
        except (IOError, OSError, PermissionError) as e:
            QMessageBox.critical(app, "Erro", f"Falha ao salvar CSV: {e}")
            return
        QMessageBox.information(app, "Exportar CSV", f"Arquivo salvo em: {path}")
