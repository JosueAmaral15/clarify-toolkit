"""
Menu Builder for MainWindow

Centralizes menu creation logic, reducing MainWindow complexity.
Extracted from MainWindow._build_menu() as part of Phase 3.4 refactoring.

Author: Refactoring Phase 3.4
Date: 2024-12-24
Version: v2.9.114
"""
# pylint: disable=import-outside-toplevel  # Lazy imports in menu builders
# pylint: disable=protected-access  # Accessing MainWindow internal methods
# pylint: disable=unnecessary-lambda  # Lambda wrappers for consistency
# pylint: disable=line-too-long  # Menu builder has long QAction lines
# pylint: disable=no-name-in-module  # Qt/Shiboken export extension types dynamically

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint: disable=no-name-in-module  # Qt dynamic modules
    from PySide6.QtGui import QAction, QActionGroup, QKeySequence
    from PySide6.QtWidgets import QMenuBar

    from ..app import MainWindow


class MenuBuilder:
    """Centralized menu builder for MainWindow."""

    @staticmethod
    def build_all_menus(main_window) -> None:
        """
        Build all menus for the main window.

        Args:
            main_window: MainWindow instance
        """
        menu_bar = main_window.menuBar()
        from PySide6.QtCore import QObject
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QAction, QActionGroup, QShortcut
        from PySide6.QtWidgets import QMenu
        from shiboken6 import isValid

        extensions = []
        for key, (menu, original_actions) in getattr(main_window, "_menu_baseline", {}).items():
            if not isValid(menu):
                continue
            for action in menu.actions():
                if action in original_actions:
                    continue
                submenu = next((child for child in menu.findChildren(QMenu, options=Qt.FindDirectChildrenOnly)
                                if child.menuAction() == action), None)
                if submenu is not None:
                    submenu.setParent(main_window)
                elif action.parent() == menu:
                    action.setParent(main_window)
                extensions.append((key, action, submenu))
        foreign_roots = [action for action in menu_bar.actions()
                         if action not in getattr(main_window, "_menu_bar_baseline", ())]
        for action in foreign_roots:
            menu_bar.removeAction(action)
            if action.parent() == menu_bar:
                action.setParent(main_window)

        states = {
            name: (action.isEnabled(), action.isChecked())
            for name, action in vars(main_window).items()
            if name.startswith("act_") and not name.startswith("act_lang_")
            and isinstance(action, QAction) and isValid(action)
        }
        # Defer destruction: a language action may still be emitting triggered.
        for obj in getattr(main_window, "_owned_menu_objects", ()):
            if isValid(obj):
                if isinstance(obj, (QAction, QShortcut)):
                    obj.setEnabled(False)
                obj.deleteLater()
        menu_bar.clear()
        previous = {id(obj) for obj in main_window.findChildren(QObject)}

        MenuBuilder._build_file_menu(main_window, menu_bar)
        MenuBuilder._build_edit_menu(main_window, menu_bar)
        MenuBuilder._build_tools_menu(main_window, menu_bar)
        MenuBuilder._build_view_menu(main_window, menu_bar)
        MenuBuilder._build_themes_menu(main_window, menu_bar)
        MenuBuilder._build_settings_menu(main_window, menu_bar)
        MenuBuilder._build_plugins_menu(main_window, menu_bar)
        MenuBuilder._build_help_menu(main_window, menu_bar)
        MenuBuilder._build_about_menu(main_window, menu_bar)
        MenuBuilder._setup_shortcuts(main_window)
        main_window._owned_menu_objects = [
            obj for obj in main_window.findChildren(QObject)
            if id(obj) not in previous
            and isinstance(obj, (QAction, QActionGroup, QShortcut, QMenu))
            and obj.parent() in (main_window, menu_bar)
        ]
        new_menus = {obj.property("clarify_menu_key"): obj
                     for obj in main_window.findChildren(QMenu)
                     if id(obj) not in previous and obj.property("clarify_menu_key")}
        main_window._menu_baseline = {key: (menu, set(menu.actions())) for key, menu in new_menus.items()}
        main_window._menu_bar_baseline = set(menu_bar.actions())
        for key, action, submenu in extensions:
            menu = new_menus[key]
            if submenu is not None:
                submenu.setParent(menu)
            menu.addAction(action)
        for action in foreign_roots:
            menu_bar.addAction(action)
        for name, (enabled, checked) in states.items():
            action = getattr(main_window, name, None)
            if isinstance(action, QAction):
                action.setEnabled(enabled)
                if action.isCheckable():
                    action.setChecked(checked)

    @staticmethod
    def _add_menu(owner, key, default=None):
        """Keep a stable identity for extension-preserving language rebuilds."""
        from ..i18n import tr
        menu = owner.addMenu(tr(key, default))
        menu.setProperty("clarify_menu_key", key)
        return menu

    @staticmethod
    def _build_file_menu(main_window, menu_bar) -> None:
        """Build File menu."""
        from ..i18n import tr
        from ..shortcut_manager import ShortcutManager
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_file = MenuBuilder._add_menu(menu_bar, "menu.file")
        m_file.setObjectName("m_file")  # For plugin access

        # New Project from Template (v2.9.63)
        main_window.act_new_from_template = QAction(tr("menu.file.new_template"), main_window)
        main_window.act_new_from_template.setToolTip(tr("menu.tooltip_new_from_template"))
        main_window.act_new_from_template.setShortcut("Ctrl+Shift+N")
        ShortcutManager.register_action(
            main_window.act_new_from_template,
            "new_project_template",
            category="File",
            managed=False,
        )
        m_file.addAction(main_window.act_new_from_template)
        main_window.act_new_from_template.triggered.connect(main_window._new_from_template)
        m_file.addSeparator()

        main_window.act_open_editor = QAction(tr("menu.file.open_editor"), main_window)
        main_window.act_open_editor.setToolTip(tr("menu.tooltip_open_editor"))
        main_window.act_open_editor.setShortcut("Ctrl+E")
        m_file.addAction(main_window.act_open_editor)
        main_window.act_open_editor.triggered.connect(lambda: main_window._show_editor())
        m_file.addSeparator()

        main_window.act_exit = QAction(tr("menu.file.exit"), main_window)
        ShortcutManager.register_action(main_window.act_exit, "exit")
        main_window.act_exit.triggered.connect(main_window.close)
        m_file.addAction(main_window.act_exit)

    @staticmethod
    def _build_edit_menu(main_window, menu_bar) -> None:
        """Build Edit menu with Undo/Redo (Task #12 - v2.9.8)."""
        from ..i18n import tr
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_edit = MenuBuilder._add_menu(menu_bar, "menu.edit")

        main_window.act_undo = QAction(tr("menu.edit.undo"), main_window)
        main_window.act_undo.setShortcut("Ctrl+Z")
        main_window.act_undo.setEnabled(False)
        main_window.act_undo.triggered.connect(main_window._undo)
        m_edit.addAction(main_window.act_undo)

        main_window.act_redo = QAction(tr("menu.edit.redo"), main_window)
        main_window.act_redo.setShortcut("Ctrl+Y")
        main_window.act_redo.setEnabled(False)
        main_window.act_redo.triggered.connect(main_window._redo)
        m_edit.addAction(main_window.act_redo)

        m_edit.addSeparator()
        act_clear_history = QAction(tr("menu.edit.clear_history"), main_window)
        act_clear_history.triggered.connect(main_window._clear_undo_history)
        m_edit.addAction(act_clear_history)

    @staticmethod
    def _build_tools_menu(main_window, menu_bar) -> None:
        """Build Tools menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_tools = MenuBuilder._add_menu(menu_bar, "menu.tools")
        main_window.tools_menu = m_tools

        # Fixed tabs accessibility (v2.9.40.2 - Task: menu for closed tabs)
        main_window.act_open_search_replace = QAction(tr("menu.tools.search_replace"), main_window)
        main_window.act_open_insert = QAction(tr("menu.tools.insert"), main_window)
        main_window.act_open_translate = QAction(tr("menu.tools.json_translate"), main_window)
        main_window.act_open_rewriter = QAction(tr("menu.tools.json_rewriter"), main_window)
        main_window.act_open_placeholder_replacer = QAction(tr("menu.tools.placeholder_replacer"), main_window)
        main_window.act_open_ai_processor = QAction(tr("menu.tools.ai_processor"), main_window)
        main_window.act_open_json_search = QAction(tr("menu.tools.json_search"), main_window)
        main_window.act_open_case_converter = QAction(tr("menu.tools.case_converter"), main_window)
        main_window.act_open_text_to_json = QAction(tr("menu.tools.text_to_json"), main_window)
        main_window.act_open_google_translate = QAction(tr("menu.tools.google_translate"), main_window)
        main_window.act_open_set_operations = QAction(tr("menu.tools.set_operations"), main_window)
        main_window.act_open_set_operations.setStatusTip(tr("menu.status.set_operations"))
        main_window.act_open_calculator = QAction(tr("menu.tools.calculator"), main_window)
        main_window.act_open_calculator.setStatusTip(tr("menu.status.calculator"))
        main_window.act_open_formula_builder = QAction(tr("menu.tools.formula_builder"), main_window)
        main_window.act_open_formula_builder.setStatusTip(tr("menu.status.formula_builder"))
        main_window.act_open_clock = QAction(
            tr("menu.tools.clock", "Clock, Stopwatch and Timer"), main_window
        )
        main_window.act_open_terminal = QAction(
            tr("menu.tools.terminal", "Terminal"), main_window
        )
        main_window.act_open_lynx = QAction(
            tr("menu.tools.lynx", "Lynx Text Browser"), main_window
        )
        main_window.act_open_information_structure = QAction(
            tr("menu.tools.information_structure", "Information Structure"), main_window
        )
        main_window.act_open_editorial_repair = QAction(
            tr("menu.tools.editorial_repair", "Editorial Repair"), main_window
        )
        main_window.act_open_boolean_logic = QAction(
            tr("menu.tools.boolean_logic", "Boolean Logic"), main_window
        )
        main_window.act_open_voice_programming = QAction(
            tr("menu.tools.voice_programming", "Voice Programming"), main_window
        )
        main_window.act_open_algorithm_analysis = QAction(
            tr("menu.tools.algorithm_analysis", "Algorithm Analysis"), main_window
        )
        main_window.act_open_file_explorer = QAction(tr("menu.tools.file_explorer"), main_window)
        main_window.act_open_file_explorer.setStatusTip(tr("menu.status.file_explorer"))
        main_window.act_open_file_explorer.setShortcut("Ctrl+Shift+F")
        main_window.act_open_advanced_extractor = QAction(tr("menu.tools.advanced_extractor"), main_window)
        main_window.act_open_advanced_extractor.setStatusTip(tr("menu.status.advanced_extractor"))
        main_window.act_open_advanced_extractor.setShortcut("Ctrl+Shift+E")

        # Group tools by user workflow while preserving the public actions.
        editing_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_editing", "Editing")
        json_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_json", "JSON")
        text_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_text_translation", "Text and Translation")
        ai_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_ai", "Artificial Intelligence")
        files_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_files", "Files")
        utilities_menu = MenuBuilder._add_menu(m_tools, "menu.tools.group_utilities", "Utilities")
        main_window.tool_group_menus = {
            "editing": editing_menu,
            "json": json_menu,
            "text_translation": text_menu,
            "ai": ai_menu,
            "files": files_menu,
            "utilities": utilities_menu,
        }

        editing_menu.addAction(main_window.act_open_insert)

        json_menu.addAction(main_window.act_open_translate)
        json_menu.addAction(main_window.act_open_rewriter)
        json_menu.addAction(main_window.act_open_placeholder_replacer)
        json_menu.addAction(main_window.act_open_json_search)
        json_menu.addAction(main_window.act_open_text_to_json)
        json_menu.addAction(main_window.act_open_set_operations)
        json_menu.addAction(main_window.act_open_advanced_extractor)

        text_menu.addAction(main_window.act_open_case_converter)
        text_menu.addAction(main_window.act_open_google_translate)
        text_menu.addAction(main_window.act_open_editorial_repair)

        ai_menu.addAction(main_window.act_open_ai_processor)
        ai_menu.addAction(main_window.act_open_voice_programming)
        ai_menu.addAction(main_window.act_open_algorithm_analysis)
        files_menu.addAction(main_window.act_open_file_explorer)
        files_menu.addAction(main_window.act_open_information_structure)
        utilities_menu.addAction(main_window.act_open_calculator)
        utilities_menu.addAction(main_window.act_open_formula_builder)
        utilities_menu.addAction(main_window.act_open_clock)
        utilities_menu.addAction(main_window.act_open_terminal)
        utilities_menu.addAction(main_window.act_open_lynx)
        utilities_menu.addAction(main_window.act_open_boolean_logic)

        # Connect actions
        main_window.act_open_search_replace.triggered.connect(main_window._show_search_replace)
        main_window.act_open_insert.triggered.connect(main_window._show_insert)
        main_window.act_open_translate.triggered.connect(main_window._show_translate)
        main_window.act_open_rewriter.triggered.connect(main_window._show_rewriter)
        main_window.act_open_placeholder_replacer.triggered.connect(main_window._show_placeholder_replacer)
        main_window.act_open_ai_processor.triggered.connect(main_window._show_ai_processor)
        main_window.act_open_json_search.triggered.connect(main_window._show_json_search)
        main_window.act_open_case_converter.triggered.connect(main_window._show_case_converter)
        main_window.act_open_text_to_json.triggered.connect(main_window._show_text_to_json)
        main_window.act_open_google_translate.triggered.connect(main_window._show_google_translate)
        main_window.act_open_set_operations.triggered.connect(main_window._show_set_operations)
        main_window.act_open_calculator.triggered.connect(main_window._show_calculator)
        main_window.act_open_formula_builder.triggered.connect(main_window._show_formula_builder)
        main_window.act_open_clock.triggered.connect(main_window._show_clock)
        main_window.act_open_terminal.triggered.connect(main_window._show_terminal)
        main_window.act_open_lynx.triggered.connect(main_window._show_lynx)
        main_window.act_open_information_structure.triggered.connect(
            main_window._show_information_structure
        )
        main_window.act_open_editorial_repair.triggered.connect(
            main_window._show_editorial_repair
        )
        main_window.act_open_boolean_logic.triggered.connect(main_window._show_boolean_logic)
        main_window.act_open_voice_programming.triggered.connect(
            main_window._show_voice_programming
        )
        main_window.act_open_algorithm_analysis.triggered.connect(
            main_window._show_algorithm_analysis
        )
        main_window.act_open_advanced_extractor.triggered.connect(main_window._show_advanced_extractor)
        main_window.act_open_file_explorer.triggered.connect(main_window._show_file_explorer)

    @staticmethod
    def _build_view_menu(main_window, menu_bar) -> None:
        """Build View menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_view = MenuBuilder._add_menu(menu_bar, "menu.view")

        main_window.act_toggle_history = QAction(tr("menu.view.history"), main_window, checkable=True)
        main_window.act_toggle_history.setToolTip(tr("menu.tooltip_toggle_history"))
        main_window.act_toggle_history.triggered.connect(main_window._toggle_history)
        m_view.addAction(main_window.act_toggle_history)

        # Layouts submenu (v2.9.84)
        m_layouts = MenuBuilder._add_menu(m_view, "menu.view.layouts")
        main_window.act_layout_compact = QAction(tr("menu.view.layouts.compact"), main_window)
        main_window.act_layout_standard = QAction(tr("menu.view.layouts.standard"), main_window)
        main_window.act_layout_advanced = QAction(tr("menu.view.layouts.advanced"), main_window)
        m_layouts.addAction(main_window.act_layout_compact)
        m_layouts.addAction(main_window.act_layout_standard)
        m_layouts.addAction(main_window.act_layout_advanced)
        m_layouts.addSeparator()
        main_window.act_layout_save = QAction(tr("menu.view.layouts.save"), main_window)
        main_window.act_layout_manage = QAction(tr("menu.view.layouts.manage"), main_window)
        m_layouts.addAction(main_window.act_layout_save)
        m_layouts.addAction(main_window.act_layout_manage)

        # Connect layout actions
        main_window.act_layout_compact.triggered.connect(lambda: main_window.layout_manager.apply_preset("Compact"))
        main_window.act_layout_standard.triggered.connect(lambda: main_window.layout_manager.apply_preset("Standard"))
        main_window.act_layout_advanced.triggered.connect(lambda: main_window.layout_manager.apply_preset("Advanced"))
        main_window.act_layout_save.triggered.connect(main_window._save_current_layout)
        main_window.act_layout_manage.triggered.connect(main_window._manage_layouts)

    @staticmethod
    def _build_themes_menu(main_window, menu_bar) -> None:
        """Build Themes menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_themes = MenuBuilder._add_menu(menu_bar, "menu.themes")

        main_window.act_theme_system = QAction(tr("menu.themes.system"), main_window, checkable=True)
        main_window.act_theme_light = QAction(tr("menu.themes.light"), main_window, checkable=True)
        main_window.act_theme_dark = QAction(tr("menu.themes.dark"), main_window, checkable=True)

        grp = [main_window.act_theme_system, main_window.act_theme_light, main_window.act_theme_dark]
        for action in grp:
            m_themes.addAction(action)
            action.triggered.connect(lambda _, x=action: main_window._apply_theme_action(x))

        main_window.act_theme_system.setChecked(True)

    @staticmethod
    def _build_settings_menu(main_window, menu_bar) -> None:
        """Build Settings menu."""
        from ..i18n import tr
        # pylint: disable=no-name-in-module  # Qt dynamic modules
        from PySide6.QtGui import QAction, QActionGroup

        m_settings = MenuBuilder._add_menu(menu_bar, "menu.settings")
        act_preferences = QAction(tr("menu.settings.preferences"), main_window)
        act_shortcuts = QAction(tr("menu.settings.shortcuts"), main_window)
        act_transparency = QAction(tr("menu.settings.transparency"), main_window)
        main_window.act_reset_settings = QAction(tr("settings_reset.action"), main_window)

        # Language submenu (Task #24 - v2.9.10, expanded v2.9.43)
        m_language = MenuBuilder._add_menu(m_settings, "menu.settings.language")

        # Create QActionGroup for radio button behavior (only one language selected at a time)
        lang_action_group = QActionGroup(main_window)
        lang_action_group.setExclusive(True)

        # Create language actions (7 languages: EN, PT-BR, ES, FR, DE, ZH, JA)
        main_window.act_lang_en = QAction("English", main_window, checkable=True)
        main_window.act_lang_pt = QAction("Português (Brasil)", main_window, checkable=True)
        main_window.act_lang_es = QAction("Español", main_window, checkable=True)
        main_window.act_lang_fr = QAction("Français", main_window, checkable=True)
        main_window.act_lang_de = QAction("Deutsch", main_window, checkable=True)
        main_window.act_lang_zh = QAction("中文 (简体)", main_window, checkable=True)
        main_window.act_lang_ja = QAction("日本語", main_window, checkable=True)

        # Add actions to action group (radio button behavior)
        lang_action_group.addAction(main_window.act_lang_en)
        lang_action_group.addAction(main_window.act_lang_pt)
        lang_action_group.addAction(main_window.act_lang_es)
        lang_action_group.addAction(main_window.act_lang_fr)
        lang_action_group.addAction(main_window.act_lang_de)
        lang_action_group.addAction(main_window.act_lang_zh)
        lang_action_group.addAction(main_window.act_lang_ja)

        # Add all actions to menu
        m_language.addAction(main_window.act_lang_en)
        m_language.addAction(main_window.act_lang_pt)
        m_language.addSeparator()
        m_language.addAction(main_window.act_lang_es)
        m_language.addAction(main_window.act_lang_fr)
        m_language.addAction(main_window.act_lang_de)
        m_language.addSeparator()
        m_language.addAction(main_window.act_lang_zh)
        m_language.addAction(main_window.act_lang_ja)

        # Connect actions to switch language
        main_window.act_lang_en.triggered.connect(lambda: main_window._switch_language("en"))
        main_window.act_lang_pt.triggered.connect(lambda: main_window._switch_language("pt_BR"))
        main_window.act_lang_es.triggered.connect(lambda: main_window._switch_language("es"))
        main_window.act_lang_fr.triggered.connect(lambda: main_window._switch_language("fr"))
        main_window.act_lang_de.triggered.connect(lambda: main_window._switch_language("de"))
        main_window.act_lang_zh.triggered.connect(lambda: main_window._switch_language("zh"))
        main_window.act_lang_ja.triggered.connect(lambda: main_window._switch_language("ja"))

        # Set current language checked (support all 7 languages)
        current_lang = main_window.translator.current_language
        lang_action_map = {
            "en": main_window.act_lang_en,
            "pt_BR": main_window.act_lang_pt,
            "es": main_window.act_lang_es,
            "fr": main_window.act_lang_fr,
            "de": main_window.act_lang_de,
            "zh": main_window.act_lang_zh,
            "ja": main_window.act_lang_ja
        }
        if current_lang in lang_action_map:
            lang_action_map[current_lang].setChecked(True)
        else:
            main_window.act_lang_en.setChecked(True)  # Fallback to English

        m_settings.addAction(act_preferences)
        m_settings.addAction(act_shortcuts)
        m_settings.addAction(act_transparency)
        m_settings.addAction(main_window.act_reset_settings)
        m_settings.addSeparator()

        # Advanced submenu (v2.9.89, expanded v2.9.90)
        m_advanced = MenuBuilder._add_menu(m_settings, "menu.settings.advanced")

        # Configuration File Editor (v2.9.90)
        main_window.act_config_editor = QAction(tr("menu.settings.advanced.config_file"), main_window)
        main_window.act_config_editor.setToolTip(tr("menu.tooltip_config_editor"))
        main_window.act_config_editor.triggered.connect(main_window._show_config_editor)
        m_advanced.addAction(main_window.act_config_editor)
        m_advanced.addSeparator()

        # Error Reporting submenu
        m_error_reporting = MenuBuilder._add_menu(m_advanced, "menu.settings.advanced.error_reporting")
        main_window.act_error_reporting_toggle = QAction(tr("menu.settings.advanced.enable_error_reporting"), main_window, checkable=True)
        main_window.act_error_reporting_toggle.setChecked(main_window.settings.qsettings.value("error_reporting/enabled", True, type=bool))
        main_window.act_error_reporting_toggle.triggered.connect(main_window._toggle_error_reporting)
        m_error_reporting.addAction(main_window.act_error_reporting_toggle)

        main_window.act_system_info_toggle = QAction(tr("menu.settings.advanced.include_system_info"), main_window, checkable=True)
        main_window.act_system_info_toggle.setChecked(main_window.settings.qsettings.value("error_reporting/include_system_info", True, type=bool))
        main_window.act_system_info_toggle.triggered.connect(main_window._toggle_system_info)
        m_error_reporting.addAction(main_window.act_system_info_toggle)

        main_window.act_auto_github_toggle = QAction(tr("menu.settings.advanced.auto_open_github"), main_window, checkable=True)
        main_window.act_auto_github_toggle.setChecked(main_window.settings.qsettings.value("error_reporting/auto_open_github", False, type=bool))
        main_window.act_auto_github_toggle.triggered.connect(main_window._toggle_auto_github)
        m_error_reporting.addAction(main_window.act_auto_github_toggle)

        m_settings.addSeparator()
        act_clear_recent = QAction(tr("menu.settings.clear_recent"), main_window)
        m_settings.addAction(act_clear_recent)

        # Connect actions
        act_preferences.triggered.connect(main_window._show_preferences)
        act_shortcuts.triggered.connect(main_window._show_shortcuts)
        act_transparency.triggered.connect(main_window._show_transparency_dialog)
        main_window.act_reset_settings.triggered.connect(main_window._show_settings_reset)
        act_clear_recent.triggered.connect(main_window._clear_recent_files)

    @staticmethod
    def _build_plugins_menu(main_window, menu_bar) -> None:
        """Build Plugins menu (v2.9.109 - Enhanced Plugin System)."""
        from ..i18n import tr
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_plugins = MenuBuilder._add_menu(menu_bar, "menu.plugins")

        # Plugin Manager submenu
        main_window.act_plugin_manager = QAction(tr("menu.plugins.manager"), main_window)
        main_window.act_plugin_manager.setToolTip(tr("menu.tooltip_plugin_manager"))
        main_window.act_plugin_manager.setStatusTip(tr("menu.status.plugin_manager"))
        m_plugins.addAction(main_window.act_plugin_manager)
        main_window.act_plugin_manager.triggered.connect(main_window._show_plugin_manager)

        m_plugins.addSeparator()

        # Installed plugins (dynamic menu based on discovered plugins)
        main_window.plugin_actions = {}
        if hasattr(main_window, "plugin_loader"):
            metadata_list = main_window.plugin_loader.get_all_metadata()
            if metadata_list:
                for metadata in metadata_list:
                    act = QAction(metadata.name, main_window)
                    act.setToolTip(f"{metadata.description}\nv{metadata.version} by {metadata.author}")
                    act.setStatusTip(f"Toggle {metadata.name} plugin")
                    act.setCheckable(True)
                    act.setChecked(metadata.enabled)
                    act.triggered.connect(lambda checked, pid=metadata.id: main_window._toggle_plugin(pid, checked))
                    main_window.plugin_actions[metadata.id] = act
                    m_plugins.addAction(act)
            else:
                act_no_plugins = QAction(tr("menu.plugins.no_plugins"), main_window)
                act_no_plugins.setEnabled(False)
                m_plugins.addAction(act_no_plugins)

    @staticmethod
    def sync_plugin_actions(main_window) -> None:
        """Reflect persisted plugin state after either UI entry point toggles it."""
        for metadata in main_window.plugin_loader.get_all_metadata():
            action = getattr(main_window, "plugin_actions", {}).get(metadata.id)
            if action is not None:
                blocked = action.blockSignals(True)
                action.setChecked(metadata.enabled)
                action.blockSignals(blocked)

    @staticmethod
    def _build_help_menu(main_window, menu_bar) -> None:
        """Build Help menu (Task #45 - v2.9.15)."""
        from ..i18n import tr
        from ..shortcut_manager import ShortcutManager
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_help = MenuBuilder._add_menu(menu_bar, "menu.help")

        main_window.act_open_tutorials = QAction(tr("menu.help.tutorials"), main_window)
        main_window.act_open_tutorials.setToolTip(tr("menu.tooltip_open_tutorials"))
        m_help.addAction(main_window.act_open_tutorials)
        main_window.act_open_tutorials.triggered.connect(main_window._show_tutorials)

        # AI Tutorial Assistant (v2.9.92)
        main_window.act_ai_assistant = QAction(tr("tutorial_assistant.window_title"), main_window)
        main_window.act_ai_assistant.setToolTip(tr("menu.tooltip_ai_assistant"))
        main_window.act_ai_assistant.setStatusTip(tr("menu.status.ai_assistant"))
        m_help.addAction(main_window.act_ai_assistant)
        main_window.act_ai_assistant.triggered.connect(main_window._show_ai_assistant)

        # Keyboard Shortcuts Help (v2.9.33)
        main_window.act_keyboard_shortcuts_help = QAction(tr("shortcuts.dialog.help_title"), main_window)
        main_window.act_keyboard_shortcuts_help.setToolTip(tr("menu.tooltip_keyboard_shortcuts"))
        main_window.act_keyboard_shortcuts_help.setStatusTip(tr("menu.status.keyboard_shortcuts_help"))
        ShortcutManager.register_action(main_window.act_keyboard_shortcuts_help, "help")
        main_window.act_keyboard_shortcuts_help.setShortcutContext(
            Qt.ShortcutContext.WindowShortcut
        )
        m_help.addAction(main_window.act_keyboard_shortcuts_help)
        main_window.act_keyboard_shortcuts_help.triggered.connect(main_window._show_keyboard_shortcuts_help)

        # Keyboard Shortcuts Customization (v2.9.62)
        main_window.act_customize_shortcuts = QAction(tr("shortcut_customizer.title"), main_window)
        main_window.act_customize_shortcuts.setToolTip(tr("menu.tooltip_customize_shortcuts"))
        main_window.act_customize_shortcuts.setStatusTip(tr("menu.status.customize_shortcuts"))
        ShortcutManager.register_action(
            main_window.act_customize_shortcuts,
            "keyboard_shortcuts",
        )
        m_help.addAction(main_window.act_customize_shortcuts)
        main_window.act_customize_shortcuts.triggered.connect(main_window._show_shortcuts)

        m_help.addSeparator()

        # View Logs (v2.9.64 - Logging System Integration)
        main_window.act_view_logs = QAction(tr("menu.help.view_logs"), main_window)
        main_window.act_view_logs.setToolTip(tr("menu.tooltip_view_logs"))
        m_help.addAction(main_window.act_view_logs)
        main_window.act_view_logs.triggered.connect(main_window._view_logs)

        # Update Checker (v2.9.45)
        main_window.act_check_updates = QAction(tr("menu.help.check_updates"), main_window)
        main_window.act_check_updates.setToolTip(tr("menu.tooltip_check_updates"))
        m_help.addAction(main_window.act_check_updates)
        main_window.act_check_updates.triggered.connect(main_window._check_for_updates_manual)

    @staticmethod
    def _build_about_menu(main_window, menu_bar) -> None:
        """Build About menu."""
        from ..i18n import tr
        from ..shortcut_manager import ShortcutManager
        from PySide6.QtGui import QAction  # pylint: disable=no-name-in-module

        m_about = MenuBuilder._add_menu(menu_bar, "menu.about")
        main_window.act_about = QAction(tr("menu.about.clarify"), main_window)
        ShortcutManager.register_action(main_window.act_about, "about")
        m_about.addAction(main_window.act_about)
        main_window.act_about.triggered.connect(main_window._about_dialog)

    @staticmethod
    def _setup_shortcuts(main_window) -> None:
        """Setup keyboard shortcuts."""
        from ..shortcut_manager import ShortcutManager
        # pylint: disable=no-name-in-module  # Qt dynamic modules
        from PySide6.QtGui import QShortcut

        # Tab navigation shortcuts (v2.9.113)
        shortcut_next_tab = QShortcut(main_window)
        ShortcutManager.register_shortcut(
            shortcut_next_tab,
            "next_dock_dynamic",
            label="Next tool",
            label_key="shortcuts.desc.next_tool_dynamic",
        )
        shortcut_next_tab.activated.connect(main_window._next_tab)

        shortcut_prev_tab = QShortcut(main_window)
        ShortcutManager.register_shortcut(
            shortcut_prev_tab,
            "prev_dock_dynamic",
            label="Previous tool",
            label_key="shortcuts.desc.prev_tool_dynamic",
        )
        shortcut_prev_tab.activated.connect(main_window._previous_tab)

        # Apply all shortcuts to menu items with tooltips (v2.9.33)
        main_window._apply_shortcuts_to_menu()
