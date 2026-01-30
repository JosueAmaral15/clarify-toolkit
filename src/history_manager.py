# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
# pylint: disable=import-outside-toplevel  # Avoid circular imports
# pylint: disable=broad-exception-caught  # History must handle all errors gracefully
"""
Operation History Manager
Gerencia histórico de operações de conjuntos executadas.
Armazena últimas 50 operações em QSettings.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QSettings


class HistoryManager:
    """Gerenciador de histórico de operações."""

    MAX_ENTRIES = 50
    SETTINGS_KEY = "operation_history"

    def __init__(self):
        """Inicializa o gerenciador."""
        self.settings = QSettings("Clarify", "Clarify")

    def add_operation(  # pylint: disable=too-many-positional-arguments
        self,
        operation_type: str,
        file1: str,
        file2: str,
        comparison_mode: str,
        result_count: int,
        result_data: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Adiciona operação ao histórico.

        Args:
            operation_type: Tipo da operação (∩, ∪, −, ⊕)
            file1: Caminho do arquivo 1
            file2: Caminho do arquivo 2
            comparison_mode: Modo de comparação
            result_count: Número de resultados
            result_data: Dados do resultado (opcional, para re-executar)
        """
        history = self.get_history()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "file1": file1,
            "file2": file2,
            "comparison_mode": comparison_mode,
            "result_count": result_count,
            "result_data": result_data or []
        }

        # Adiciona no início
        history.insert(0, entry)

        # Mantém apenas últimas 50 operações
        if len(history) > self.MAX_ENTRIES:
            history = history[:self.MAX_ENTRIES]

        self._save_history(history)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Obtém histórico completo.

        Returns:
            Lista de operações
        """
        history = self.settings.value(self.SETTINGS_KEY, [])

        # Garantir que retorna lista
        if not isinstance(history, list):
            return []

        return history

    def get_entry(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Obtém entrada específica.

        Args:
            index: Índice da entrada (0-based)

        Returns:
            Dicionário com dados da entrada ou None
        """
        history = self.get_history()

        if 0 <= index < len(history):
            return history[index]

        return None

    def clear_history(self) -> None:
        """Limpa todo o histórico."""
        self.settings.setValue(self.SETTINGS_KEY, [])

    def export_history(self, filepath: str) -> bool:
        """
        Exporta histórico para arquivo JSON.

        Args:
            filepath: Caminho do arquivo de destino

        Returns:
            True se sucesso, False se erro
        """
        import json
        from pathlib import Path

        try:
            history = self.get_history()

            # Adiciona metadados
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_operations": len(history),
                "operations": history
            }

            Path(filepath).write_text(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

            return True

        except Exception as e:
            print(f"Erro ao exportar histórico: {e}")
            return False

    def format_entry_display(self, entry: Dict[str, Any]) -> str:
        """
        Formata entrada para exibição no QListWidget.

        Args:
            entry: Dicionário com dados da entrada

        Returns:
            String formatada para exibição
        """
        try:
            # Parse timestamp
            timestamp = datetime.fromisoformat(entry["timestamp"])
            time_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")

            # Operação
            op = entry["operation_type"]

            # Nomes dos arquivos (apenas basename)
            from pathlib import Path
            file1_name = Path(entry["file1"]).name
            file2_name = Path(entry["file2"]).name

            # Modo
            mode = entry["comparison_mode"]

            # Resultados
            count = entry["result_count"]

            # Formato: [2024-12-22 14:30] A ∩ B (by_key) → 42 results
            return f"[{time_str}] {file1_name} {op} {file2_name} ({mode}) → {count} results"

        except Exception as e:
            return f"[Erro ao formatar: {e}]"

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        """
        Salva histórico no QSettings.

        Args:
            history: Lista de operações
        """
        self.settings.setValue(self.SETTINGS_KEY, history)
