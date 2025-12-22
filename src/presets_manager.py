"""
Operation Presets Manager
Gerencia presets salvos para operações de conjuntos.
Armazena configurações frequentes em QSettings.
"""
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QSettings


class PresetsManager:
    """Gerenciador de presets de operações."""
    
    SETTINGS_KEY = "operation_presets"
    
    # Default presets (criados na primeira inicialização)
    DEFAULT_PRESETS = [
        {
            "name": "Quick Intersection (key_value)",
            "operation_type": "∩",
            "comparison_mode": "key_value",
            "ignore_case_keys": False,
            "ignore_case_values": False,
            "skip_empty": True,
            "arrays_ignore_order": False,
            "favorite_files": []
        },
        {
            "name": "Full Path Union",
            "operation_type": "∪",
            "comparison_mode": "full_path_value",
            "ignore_case_keys": False,
            "ignore_case_values": False,
            "skip_empty": True,
            "arrays_ignore_order": False,
            "favorite_files": []
        },
        {
            "name": "Difference (ignore case)",
            "operation_type": "−",
            "comparison_mode": "key_value",
            "ignore_case_keys": True,
            "ignore_case_values": True,
            "skip_empty": True,
            "arrays_ignore_order": False,
            "favorite_files": []
        }
    ]
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.settings = QSettings("Clarify", "Clarify")
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Garante que presets padrão existam."""
        presets = self.get_presets()
        
        # Se não há presets, adiciona os padrão
        if not presets:
            for preset in self.DEFAULT_PRESETS:
                self.save_preset(preset)
    
    def get_presets(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de todos os presets.
        
        Returns:
            Lista de presets
        """
        presets = self.settings.value(self.SETTINGS_KEY, [])
        
        # Garantir que retorna lista
        if not isinstance(presets, list):
            return []
        
        return presets
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém preset específico por nome.
        
        Args:
            name: Nome do preset
        
        Returns:
            Dicionário com dados do preset ou None
        """
        presets = self.get_presets()
        
        for preset in presets:
            if preset.get("name") == name:
                return preset
        
        return None
    
    def save_preset(self, preset: Dict[str, Any]) -> bool:
        """
        Salva ou atualiza um preset.
        
        Args:
            preset: Dicionário com dados do preset
        
        Returns:
            True se sucesso, False se erro
        """
        if "name" not in preset:
            return False
        
        presets = self.get_presets()
        
        # Verifica se já existe preset com mesmo nome
        existing_index = -1
        for i, p in enumerate(presets):
            if p.get("name") == preset["name"]:
                existing_index = i
                break
        
        if existing_index >= 0:
            # Atualiza existente
            presets[existing_index] = preset
        else:
            # Adiciona novo
            presets.append(preset)
        
        self._save_presets(presets)
        return True
    
    def delete_preset(self, name: str) -> bool:
        """
        Deleta um preset.
        
        Args:
            name: Nome do preset a deletar
        
        Returns:
            True se deletado, False se não encontrado
        """
        presets = self.get_presets()
        
        # Filtra removendo preset com nome especificado
        original_count = len(presets)
        presets = [p for p in presets if p.get("name") != name]
        
        if len(presets) < original_count:
            self._save_presets(presets)
            return True
        
        return False
    
    def rename_preset(self, old_name: str, new_name: str) -> bool:
        """
        Renomeia um preset.
        
        Args:
            old_name: Nome atual do preset
            new_name: Novo nome
        
        Returns:
            True se renomeado, False se erro
        """
        presets = self.get_presets()
        
        # Verifica se novo nome já existe
        if any(p.get("name") == new_name for p in presets):
            return False
        
        # Renomeia preset
        for preset in presets:
            if preset.get("name") == old_name:
                preset["name"] = new_name
                self._save_presets(presets)
                return True
        
        return False
    
    def create_preset_from_current(
        self,
        name: str,
        operation_type: str,
        comparison_mode: str,
        ignore_case_keys: bool,
        ignore_case_values: bool,
        skip_empty: bool,
        arrays_ignore_order: bool,
        favorite_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Cria preset a partir de configurações atuais.
        
        Args:
            name: Nome do preset
            operation_type: Tipo de operação (∩/∪/−/⊕)
            comparison_mode: Modo de comparação
            ignore_case_keys: Ignorar case em chaves
            ignore_case_values: Ignorar case em valores
            skip_empty: Pular valores vazios
            arrays_ignore_order: Ignorar ordem em arrays
            favorite_files: Lista de arquivos favoritos (opcional)
        
        Returns:
            Dicionário com dados do preset
        """
        return {
            "name": name,
            "operation_type": operation_type,
            "comparison_mode": comparison_mode,
            "ignore_case_keys": ignore_case_keys,
            "ignore_case_values": ignore_case_values,
            "skip_empty": skip_empty,
            "arrays_ignore_order": arrays_ignore_order,
            "favorite_files": favorite_files or []
        }
    
    def _save_presets(self, presets: List[Dict[str, Any]]) -> None:
        """
        Salva presets no QSettings.
        
        Args:
            presets: Lista de presets
        """
        self.settings.setValue(self.SETTINGS_KEY, presets)
