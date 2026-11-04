"""Public File Searcher naming without changing File Explorer compatibility IDs."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

import json
from pathlib import Path

from PySide6.QtWidgets import QMainWindow

from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.information_structure_dock import InformationStructureDock
from src.gui.menu_builder import MenuBuilder
from src.gui.panels.results_tree import ResultsTree
from src.gui.tab_manager import TabManager
from src.i18n import get_translator, tr
from src.shortcut_manager import ShortcutManager


CATALOG_NAMES = {
    "en": {
        "file_list.progress_title": "File Searcher",
        "file_explorer.replace_busy": "Another File Searcher operation is running.",
        "file_explorer.history_search": "File Searcher Search",
        "file_explorer.history_browse": "File Searcher Browse",
        "file_explorer.history_replace_all": "File Searcher Replace All",
        "file_explorer.history_replace_first": "File Searcher Replace First",
        "file_list.title": "File Searcher",
        "menu.status.file_explorer": "Unified file searcher with advanced search",
        "menu.tools.file_explorer": "📁 File Searcher...",
    },
    "pt_BR": {
        "file_list.progress_title": "Pesquisador de Arquivos",
        "file_explorer.replace_busy": "Outra operação do Pesquisador de Arquivos está em andamento.",
        "file_explorer.history_search": "Pesquisa do Pesquisador de Arquivos",
        "file_explorer.history_browse": "Navegação do Pesquisador de Arquivos",
        "file_explorer.history_replace_all": "Substituir Tudo no Pesquisador de Arquivos",
        "file_explorer.history_replace_first": "Substituir Primeiro no Pesquisador de Arquivos",
        "file_list.title": "Pesquisador de Arquivos",
        "menu.status.file_explorer": "Pesquisador de arquivos unificado com busca avançada",
        "menu.tools.file_explorer": "📁 Pesquisador de Arquivos...",
    },
    "es": {
        "file_list.progress_title": "Buscador de Archivos",
        "file_explorer.replace_busy": "Hay otra operación del Buscador de Archivos en curso.",
        "file_explorer.history_search": "Búsqueda del Buscador de Archivos",
        "file_explorer.history_browse": "Navegación del Buscador de Archivos",
        "file_explorer.history_replace_all": "Reemplazar Todo en el Buscador de Archivos",
        "file_explorer.history_replace_first": "Reemplazar Primero en el Buscador de Archivos",
        "file_list.title": "Buscador de Archivos",
        "menu.status.file_explorer": "Buscador de archivos unificado con búsqueda avanzada",
        "menu.tools.file_explorer": "📁 Buscador de Archivos...",
    },
    "fr": {
        "file_list.progress_title": "Recherche de Fichiers",
        "file_explorer.replace_busy": "Une autre opération de recherche de fichiers est en cours.",
        "file_explorer.history_search": "Recherche de Fichiers",
        "file_explorer.history_browse": "Parcours de Fichiers",
        "file_explorer.history_replace_all": "Tout Remplacer dans la Recherche de Fichiers",
        "file_explorer.history_replace_first": "Remplacer le Premier dans la Recherche de Fichiers",
        "file_list.title": "Recherche de Fichiers",
        "menu.status.file_explorer": "Recherche de fichiers unifiée avec recherche avancée",
        "menu.tools.file_explorer": "📁 Recherche de Fichiers...",
    },
    "de": {
        "file_list.progress_title": "Dateisuche",
        "file_explorer.replace_busy": "Ein anderer Dateisuche-Vorgang wird ausgeführt.",
        "file_explorer.history_search": "Dateisuche",
        "file_explorer.history_browse": "Dateisuche Durchsuchen",
        "file_explorer.history_replace_all": "Alle in der Dateisuche Ersetzen",
        "file_explorer.history_replace_first": "Ersten in der Dateisuche Ersetzen",
        "file_list.title": "Dateisuche",
        "menu.status.file_explorer": "Einheitliche Dateisuche mit erweiterter Suche",
        "menu.tools.file_explorer": "📁 Dateisuche...",
    },
    "ja": {
        "file_list.progress_title": "ファイル検索",
        "file_explorer.replace_busy": "別のファイル検索操作が実行中です。",
        "file_explorer.history_search": "ファイル検索",
        "file_explorer.history_browse": "ファイル検索の参照",
        "file_explorer.history_replace_all": "ファイル検索ですべて置換",
        "file_explorer.history_replace_first": "ファイル検索で最初を置換",
        "file_list.title": "ファイル検索",
        "menu.status.file_explorer": "高度な検索機能付き統合ファイル検索",
        "menu.tools.file_explorer": "📁 ファイル検索...",
    },
    "zh": {
        "file_list.progress_title": "文件搜索器",
        "file_explorer.replace_busy": "另一个文件搜索器操作正在运行。",
        "file_explorer.history_search": "文件搜索器搜索",
        "file_explorer.history_browse": "文件搜索器浏览",
        "file_explorer.history_replace_all": "文件搜索器全部替换",
        "file_explorer.history_replace_first": "文件搜索器替换第一个",
        "file_list.title": "文件搜索器",
        "menu.status.file_explorer": "具有高级搜索的统一文件搜索器",
        "menu.tools.file_explorer": "📁 文件搜索器...",
    },
}


class _ToolsMenuWindow(QMainWindow):
    def __getattr__(self, name):
        if name.startswith("_show_"):
            return lambda: None
        raise AttributeError(name)


def test_all_catalogs_use_file_searcher_public_name():
    catalog_root = Path(__file__).parents[2] / "src" / "i18n"
    for language, expected in CATALOG_NAMES.items():
        catalog = json.loads((catalog_root / f"{language}.json").read_text(encoding="utf-8"))
        for key, value in expected.items():
            assert catalog[key] == value


def test_menu_tab_and_runtime_title_translate_without_identity_migration(qapp, qtbot):
    translator = get_translator()
    original_language = translator.current_language
    window = _ToolsMenuWindow()
    dock = FileExplorerDock()
    try:
        MenuBuilder._build_tools_menu(window, window.menuBar())
        registry = TabManager.SIMPLE_TOOLS["file_explorer"]
        assert registry == (
            "dock_file_explorer",
            "FileExplorerDock",
            "File Searcher",
            "file_explorer",
        )
        assert dock.settings.applicationName() == "FileExplorer"
        assert "open_file_list" in ShortcutManager.SHORTCUTS
        assert ShortcutManager.get_description("open_file_list") == "File Searcher"

        for language, expected in CATALOG_NAMES.items():
            translator.switch_language(language)
            qapp.processEvents()
            assert dock.windowTitle() == expected["file_list.title"]
            assert TabManager.translated_title("file_explorer") == expected["menu.tools.file_explorer"]
            window.act_open_file_explorer.setText(tr("menu.tools.file_explorer"))
            window.act_open_file_explorer.setStatusTip(tr("menu.status.file_explorer"))
            assert window.act_open_file_explorer.text() == expected["menu.tools.file_explorer"]
            assert window.act_open_file_explorer.statusTip() == expected["menu.status.file_explorer"]

        translator.switch_language("en")
        assert tr("tooltip.editor.chk_show_explorer") == "Show or hide the editor filesystem explorer"
    finally:
        translator.switch_language(original_language)
        dock.close()
        window.close()
        dock.deleteLater()
        window.deleteLater()
        qtbot.wait(10)


def test_public_integration_copy_uses_file_searcher(qapp, qtbot):
    tree = ResultsTree()
    structure = InformationStructureDock()
    try:
        tree._matches_data = {"/tmp/example.txt": [(1, 0, "needle")]}
        prompt = tree._build_ai_explanation_prompt(
            ["/tmp/example.txt"],
            {
                "skipped_binary": 0,
                "skipped_directory": 0,
                "skipped_missing": 0,
                "skipped_non_file": 0,
                "skipped_file_limit": 0,
                "skipped_error": 0,
            },
            "all",
        )
        assert "File Searcher" in prompt
        assert "File Explorer" not in prompt
        assert structure.mode_combo.itemText(0) == "Folder map from File Searcher"
        assert structure.path_input.placeholderText() == "Use File Searcher > Folder map from results"
    finally:
        tree.close()
        structure.close()
        tree.deleteLater()
        structure.deleteLater()
        qtbot.wait(10)
