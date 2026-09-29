"""Tests for the grouped Tools menu."""

from PySide6.QtWidgets import QMainWindow

from src.gui.menu_builder import MenuBuilder


class _ToolsMenuWindow(QMainWindow):
    def __getattr__(self, name):
        if name.startswith("_show_"):
            return lambda: None
        raise AttributeError(name)


def test_tools_menu_uses_stable_functional_groups(qapp):
    window = _ToolsMenuWindow()
    try:
        menu_bar = window.menuBar()
        MenuBuilder._build_tools_menu(window, menu_bar)
        tools_menu = window.tools_menu
        groups = {
            menu.title(): menu
            for menu in window.tool_group_menus.values()
        }

        assert set(groups) == {
            "Editing",
            "JSON",
            "Text and Translation",
            "Artificial Intelligence",
            "Files",
            "Utilities",
        }
        assert window.act_open_translate in groups["JSON"].actions()
        assert window.act_open_search_replace not in groups["Editing"].actions()
        assert window.act_open_advanced_extractor in groups["JSON"].actions()
        assert window.act_open_google_translate in groups["Text and Translation"].actions()
        assert window.act_open_editorial_repair in groups["Text and Translation"].actions()
        assert window.act_open_ai_processor in groups["Artificial Intelligence"].actions()
        assert window.act_open_voice_programming in groups["Artificial Intelligence"].actions()
        assert window.act_open_algorithm_analysis in groups["Artificial Intelligence"].actions()
        assert window.act_open_file_explorer in groups["Files"].actions()
        assert window.act_open_information_structure in groups["Files"].actions()
        assert window.act_open_clock in groups["Utilities"].actions()
        assert window.act_open_terminal in groups["Utilities"].actions()
        assert window.act_open_lynx in groups["Utilities"].actions()
        assert window.act_open_boolean_logic in groups["Utilities"].actions()
    finally:
        window.deleteLater()
