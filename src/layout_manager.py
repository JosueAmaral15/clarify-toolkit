# pylint: disable=no-name-in-module  # PySide6 uses dynamic module structure
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

from typing import Dict, List
import json
from shiboken6 import isValid as is_valid
from PySide6.QtCore import QSettings, QByteArray
from PySide6.QtWidgets import QMainWindow, QDockWidget

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
        dock_widget.setProperty("clarify_tool_id", name)
        if not dock_widget.objectName():
            dock_widget.setObjectName("dock_" + name)
        logger.debug("Dock registered: %s", name)

    def _sync_tabs(self):
        self.docks = {name: widget for name, widget in self.docks.items() if is_valid(widget)}
        tabs = getattr(self.main_window, "tabs", None)
        if tabs is not None:
            for index in range(tabs.count()):
                widget = tabs.widget(index)
                name = widget.property("clarify_tool_id")
                if name:
                    self.register_dock(name, widget)
        return tabs

    def _is_open(self, widget, tabs):
        if tabs is None or tabs.indexOf(widget) >= 0:
            return True
        return isinstance(widget, QDockWidget) and bool(self.main_window.dockWidgetArea(widget))

    def _set_visibility(self, visible_names):
        tabs = self._sync_tabs()
        selected = tabs.currentWidget() if tabs is not None else None
        if tabs is not None and tabs.count():
            eligible = [i for i in range(tabs.count())
                        if tabs.widget(i).property("clarify_tool_id") in visible_names]
            # Never leave a live tab workspace blank when a preset's tools are closed.
            if not eligible:
                eligible = [max(0, tabs.currentIndex())]
            for index in range(tabs.count()):
                tabs.setTabVisible(index, index in eligible)
            index = tabs.indexOf(selected) if selected is not None else -1
            tabs.setCurrentIndex(index if index in eligible else eligible[0])
        for name, widget in self.docks.items():
            if self._is_open(widget, tabs) and (tabs is None or tabs.indexOf(widget) < 0):
                widget.setVisible(name in visible_names)

    def save_layout(self, layout_name: str) -> None:
        """
        Salva o layout atual com um nome específico.

        Args:
            layout_name: Nome do layout (ex: "my_custom_layout")
        """
        tabs = self._sync_tabs()
        tab_state = []
        if tabs is not None:
            for index in range(tabs.count()):
                widget = tabs.widget(index)
                name = widget.property("clarify_tool_id")
                if name:
                    item = {"id": name, "visible": tabs.isTabVisible(index)}
                    if hasattr(widget, "get_workspace_mode"):
                        item["mode"] = widget.get_workspace_mode()
                    tab_state.append(item)
        if len(tab_state) > 128:
            raise ValueError("A layout supports at most 128 registered tabs")
        encoded = json.dumps(tab_state)
        if len(encoded.encode("utf-8")) > 65536:
            raise ValueError("Layout tab metadata exceeds 64 KiB")
        # Salvar geometry e state do QMainWindow
        geometry = self.main_window.saveGeometry()
        state = self.main_window.saveState()

        # Salvar no QSettings
        self.settings.beginGroup(f"Layouts/{layout_name}")
        self.settings.setValue("geometry", geometry)
        self.settings.setValue("state", state)
        self.settings.setValue("tabs", encoded)
        current = tabs.currentWidget() if tabs is not None else None
        self.settings.setValue("active_tab", current.property("clarify_tool_id") if current else "")

        # Salvar visibilidade de cada dock
        for dock_name, dock_widget in self.docks.items():
            index = tabs.indexOf(dock_widget) if tabs is not None else -1
            visible = tabs.isTabVisible(index) if index >= 0 else not dock_widget.isHidden()
            self.settings.setValue(f"dock_{dock_name}_visible", visible)

        self.settings.endGroup()
        self.settings.setValue("LastLayout", layout_name)
        self.settings.sync()

        logger.info("Layout saved: %s", layout_name)

    def load_layout(self, layout_name: str) -> bool:
        """
        Carrega um layout salvo previamente.

        Args:
            layout_name: Nome do layout a carregar

        Returns:
            True se o layout foi carregado com sucesso, False caso contrário
        """
        tabs = self._sync_tabs()
        self.settings.beginGroup(f"Layouts/{layout_name}")

        # Verificar se o layout existe
        if not self.settings.contains("geometry"):
            self.settings.endGroup()
            logger.warning("Layout not found: %s", layout_name)
            return False

        # Restaurar geometry e state
        geometry = self.settings.value("geometry", type=QByteArray)
        state = self.settings.value("state", type=QByteArray)
        raw_tabs = self.settings.value("tabs", None)
        active_tab = self.settings.value("active_tab", "")
        try:
            records = None
            if not isinstance(active_tab, str) or len(active_tab) > 512:
                raise ValueError("Invalid layout active tab")
            if raw_tabs is not None:
                if (not isinstance(raw_tabs, str) or len(raw_tabs) > 65536
                        or len(raw_tabs.encode("utf-8")) > 65536):
                    raise ValueError("Invalid layout tab metadata")
                records = json.loads(raw_tabs)
                if not isinstance(records, list) or len(records) > 128:
                    raise ValueError("Invalid layout tab list")
                seen = set()
                for item in records:
                    if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                            or not item["id"] or len(item["id"]) > 512
                            or item["id"] in seen or not isinstance(item.get("visible"), bool)
                            or item.get("mode") not in (None, "compact", "advanced")):
                        raise ValueError("Invalid layout tab record")
                    seen.add(item["id"])
        except (ValueError, TypeError) as error:
            self.settings.endGroup()
            logger.warning("Cannot restore layout %s: %s", layout_name, error)
            return False

        if geometry and not self.main_window.restoreGeometry(geometry):
            self.settings.endGroup()
            return False
        if state and not self.main_window.restoreState(state):
            self.settings.endGroup()
            return False

        # Restaurar visibilidade dos docks
        for dock_name, dock_widget in self.docks.items():
            if not self._is_open(dock_widget, tabs):
                continue
            index = tabs.indexOf(dock_widget) if tabs is not None else -1
            if index < 0:
                visible = self.settings.value(f"dock_{dock_name}_visible", True, type=bool)
                dock_widget.setVisible(visible)

        if tabs is not None:
            if records is None:
                visible_names = set()
                for name in self.docks:
                    key = f"dock_{name}_visible"
                    if name == "file_explorer" and not self.settings.contains(key):
                        key = "dock_search_visible"
                    if self.settings.value(key, True, type=bool):
                        visible_names.add(name)
            else:
                # Reorder existing tabs only; a layout never starts unopened tools.
                position = 0
                for item in records:
                    widget = self.docks.get(item["id"])
                    index = tabs.indexOf(widget) if widget is not None else -1
                    if index >= 0:
                        tabs.tabBar().moveTab(index, position)
                        position += 1
                        if item.get("mode") is not None and hasattr(widget, "set_workspace_mode"):
                            widget.set_workspace_mode(item["mode"])
                visible_names = {item["id"] for item in records if item["visible"]}
                # Tools opened after this snapshot remain accessible.
                visible_names.update(name for name in self.docks if name not in seen)
            self._set_visibility(visible_names)
            widget = self.docks.get(active_tab)
            index = tabs.indexOf(widget) if widget is not None else -1
            if index >= 0 and tabs.isTabVisible(index):
                tabs.setCurrentIndex(index)

        self.settings.endGroup()

        # Salvar como último layout usado
        self.settings.setValue("LastLayout", layout_name)
        self.settings.sync()

        logger.info("Layout loaded: %s", layout_name)
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
        tabs = self._sync_tabs()
        editor = self.docks.get("editor")
        if (tabs is not None and (editor is None or tabs.indexOf(editor) < 0)
                and hasattr(self.main_window, "_show_editor")):
            self.main_window._show_editor()
        self._set_visibility({"editor"})

        # Salvar este preset
        self.save_layout(self.PRESET_COMPACT)

    def apply_preset_standard(self) -> None:
        """
        Aplica o preset Standard (layout padrão da aplicação).

        Layout equilibrado:
        - Editor: Visível (central)
        - File Explorer/Search-Replace: Visível se aberto
        - Insert: Oculto
        - Set Operations: Oculto
        - JSON Rewriter: Visível se aberto
        - Translate: Oculto
        """
        logger.info("Applying Standard preset")

        # Mostrar docks principais
        self._set_visibility({"editor", "file_explorer", "search", "replace", "rewriter"})

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
        self._sync_tabs()
        self._set_visibility(set(self.docks))

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
            logger.error("Invalid preset name: %s", preset_name)
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
            logger.warning("Cannot delete preset: %s", layout_name)
            return False

        self.settings.remove(f"Layouts/{layout_name}")
        self.settings.sync()

        logger.info("Layout deleted: %s", layout_name)
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
