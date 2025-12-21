#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Layout Manager - Gerenciador de layouts customizáveis da interface

Permite salvar/carregar layouts de docks, incluindo presets pré-configurados.
Suporta 3 modos: Compact, Standard, Advanced.

Author: Josué Amaral
Date: 2025-12-21
Version: 2.9.84
"""

from typing import Dict, List, Optional
from PySide6.QtCore import QSettings, QByteArray
from PySide6.QtWidgets import QMainWindow

from .utils.logger import get_logger

logger = get_logger(__name__)


class LayoutManager:
    """
    Gerencia layouts customizáveis da aplicação.
    
    Features:
    - Salvar/carregar state completo (dock positions, sizes, visibility)
    - 3 presets pré-configurados: Compact, Standard, Advanced
    - Persistência via QSettings
    - Restauração automática do último layout usado
    """
    
    # Nomes dos presets disponíveis
    PRESET_COMPACT = "Compact"
    PRESET_STANDARD = "Standard"
    PRESET_ADVANCED = "Advanced"
    
    # Lista de todos os presets
    PRESETS = [PRESET_COMPACT, PRESET_STANDARD, PRESET_ADVANCED]
    
    def __init__(self, main_window: QMainWindow):
        """
        Inicializa o LayoutManager.
        
        Args:
            main_window: Instância do QMainWindow principal
        """
        self.main_window = main_window
        self.settings = QSettings("Clarify", "ClarifyApp")
        
        # Docks disponíveis no sistema (mapeamento nome → dock widget)
        self.docks: Dict[str, any] = {}
        
        logger.info("LayoutManager initialized")
    
    def register_dock(self, name: str, dock_widget) -> None:
        """
        Registra um dock widget para gerenciamento.
        
        Args:
            name: Nome único do dock (ex: "editor", "search", "rewriter")
            dock_widget: Instância do QDockWidget
        """
        self.docks[name] = dock_widget
        logger.debug(f"Dock registered: {name}")
    
    def save_layout(self, layout_name: str) -> None:
        """
        Salva o layout atual com um nome específico.
        
        Args:
            layout_name: Nome do layout (ex: "my_custom_layout")
        """
        # Salvar geometry e state do QMainWindow
        geometry = self.main_window.saveGeometry()
        state = self.main_window.saveState()
        
        # Salvar no QSettings
        self.settings.beginGroup(f"Layouts/{layout_name}")
        self.settings.setValue("geometry", geometry)
        self.settings.setValue("state", state)
        
        # Salvar visibilidade de cada dock
        for dock_name, dock_widget in self.docks.items():
            self.settings.setValue(f"dock_{dock_name}_visible", dock_widget.isVisible())
        
        self.settings.endGroup()
        self.settings.sync()
        
        logger.info(f"Layout saved: {layout_name}")
    
    def load_layout(self, layout_name: str) -> bool:
        """
        Carrega um layout salvo previamente.
        
        Args:
            layout_name: Nome do layout a carregar
            
        Returns:
            True se o layout foi carregado com sucesso, False caso contrário
        """
        self.settings.beginGroup(f"Layouts/{layout_name}")
        
        # Verificar se o layout existe
        if not self.settings.contains("geometry"):
            self.settings.endGroup()
            logger.warning(f"Layout not found: {layout_name}")
            return False
        
        # Restaurar geometry e state
        geometry = self.settings.value("geometry", type=QByteArray)
        state = self.settings.value("state", type=QByteArray)
        
        if geometry and state:
            self.main_window.restoreGeometry(geometry)
            self.main_window.restoreState(state)
        
        # Restaurar visibilidade dos docks
        for dock_name, dock_widget in self.docks.items():
            visible = self.settings.value(f"dock_{dock_name}_visible", True, type=bool)
            dock_widget.setVisible(visible)
        
        self.settings.endGroup()
        
        # Salvar como último layout usado
        self.settings.setValue("LastLayout", layout_name)
        self.settings.sync()
        
        logger.info(f"Layout loaded: {layout_name}")
        return True
    
    def apply_preset_compact(self) -> None:
        """
        Aplica o preset Compact.
        
        Layout minimalista:
        - Editor: Visível (central)
        - Search: Oculto
        - Replace: Oculto
        - Insert: Oculto
        - Set Operations: Oculto
        - JSON Rewriter: Oculto
        - Outros: Ocultos
        """
        logger.info("Applying Compact preset")
        
        # Mostrar apenas Editor (se existir)
        visible_docks = ["editor"]
        
        for dock_name, dock_widget in self.docks.items():
            should_be_visible = dock_name in visible_docks
            dock_widget.setVisible(should_be_visible)
        
        # Salvar este preset
        self.save_layout(self.PRESET_COMPACT)
    
    def apply_preset_standard(self) -> None:
        """
        Aplica o preset Standard (layout padrão da aplicação).
        
        Layout equilibrado:
        - Editor: Visível (central)
        - Search: Visível
        - Replace: Visível
        - Insert: Oculto
        - Set Operations: Oculto
        - JSON Rewriter: Visível
        - Translate: Oculto
        """
        logger.info("Applying Standard preset")
        
        # Mostrar docks principais
        visible_docks = ["editor", "search", "replace", "rewriter"]
        
        for dock_name, dock_widget in self.docks.items():
            should_be_visible = dock_name in visible_docks
            dock_widget.setVisible(should_be_visible)
        
        # Salvar este preset
        self.save_layout(self.PRESET_STANDARD)
    
    def apply_preset_advanced(self) -> None:
        """
        Aplica o preset Advanced.
        
        Layout completo:
        - Todos os docks visíveis
        - Útil para power users
        """
        logger.info("Applying Advanced preset")
        
        # Mostrar todos os docks
        for dock_widget in self.docks.values():
            dock_widget.setVisible(True)
        
        # Salvar este preset
        self.save_layout(self.PRESET_ADVANCED)
    
    def apply_preset(self, preset_name: str) -> bool:
        """
        Aplica um preset pelo nome.
        
        Args:
            preset_name: Nome do preset (PRESET_COMPACT, PRESET_STANDARD, PRESET_ADVANCED)
            
        Returns:
            True se o preset foi aplicado, False se o nome é inválido
        """
        if preset_name == self.PRESET_COMPACT:
            self.apply_preset_compact()
            return True
        elif preset_name == self.PRESET_STANDARD:
            self.apply_preset_standard()
            return True
        elif preset_name == self.PRESET_ADVANCED:
            self.apply_preset_advanced()
            return True
        else:
            logger.error(f"Invalid preset name: {preset_name}")
            return False
    
    def restore_last_layout(self) -> bool:
        """
        Restaura o último layout usado (salvo em QSettings).
        
        Returns:
            True se restaurou com sucesso, False caso contrário
        """
        last_layout = self.settings.value("LastLayout", self.PRESET_STANDARD, type=str)
        
        # Tentar carregar o último layout
        if self.load_layout(last_layout):
            return True
        
        # Se falhou, aplicar Standard como fallback
        logger.info("Last layout not found, applying Standard preset")
        self.apply_preset_standard()
        return False
    
    def get_saved_layouts(self) -> List[str]:
        """
        Retorna lista de layouts salvos (exceto os 3 presets).
        
        Returns:
            Lista de nomes de layouts customizados
        """
        # Obter todas as chaves em Layouts/
        self.settings.beginGroup("Layouts")
        layout_names = self.settings.childGroups()
        self.settings.endGroup()
        
        # Filtrar apenas os customizados (não-presets)
        custom_layouts = [
            name for name in layout_names 
            if name not in self.PRESETS
        ]
        
        return custom_layouts
    
    def delete_layout(self, layout_name: str) -> bool:
        """
        Remove um layout salvo.
        
        Args:
            layout_name: Nome do layout a remover
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        # Não permitir deletar presets
        if layout_name in self.PRESETS:
            logger.warning(f"Cannot delete preset: {layout_name}")
            return False
        
        self.settings.remove(f"Layouts/{layout_name}")
        self.settings.sync()
        
        logger.info(f"Layout deleted: {layout_name}")
        return True
    
    def reset_to_defaults(self) -> None:
        """
        Reseta todos os layouts para os presets padrão.
        
        Remove todos os layouts customizados e restaura Standard.
        """
        logger.info("Resetting layouts to defaults")
        
        # Remover todos os layouts customizados
        custom_layouts = self.get_saved_layouts()
        for layout_name in custom_layouts:
            self.delete_layout(layout_name)
        
        # Aplicar Standard preset
        self.apply_preset_standard()
