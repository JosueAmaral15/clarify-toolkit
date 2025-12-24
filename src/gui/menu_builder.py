"""
Menu Builder for MainWindow

Centralizes menu creation logic, reducing MainWindow complexity.
Extracted from MainWindow._build_menu() as part of Phase 3.4 refactoring.

Author: Refactoring Phase 3.4
Date: 2024-12-24
Version: v2.9.114
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMenuBar, QActionGroup
    from PySide6.QtGui import QAction, QKeySequence
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
        bar = main_window.menuBar()
        
        MenuBuilder._build_file_menu(main_window, bar)
        MenuBuilder._build_edit_menu(main_window, bar)
        MenuBuilder._build_tools_menu(main_window, bar)
        MenuBuilder._build_view_menu(main_window, bar)
        MenuBuilder._build_themes_menu(main_window, bar)
        MenuBuilder._build_settings_menu(main_window, bar)
        MenuBuilder._build_plugins_menu(main_window, bar)
        MenuBuilder._build_help_menu(main_window, bar)
        MenuBuilder._build_about_menu(main_window, bar)
        MenuBuilder._setup_shortcuts(main_window)
    
    @staticmethod
    def _build_file_menu(main_window, bar) -> None:
        """Build File menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_file = bar.addMenu(tr("menu.file"))
        
        # New Project from Template (v2.9.63)
        main_window.act_new_from_template = QAction("New from Template...", main_window)
        main_window.act_new_from_template.setToolTip("Create project from template")
        main_window.act_new_from_template.setShortcut("Ctrl+Shift+N")
        m_file.addAction(main_window.act_new_from_template)
        main_window.act_new_from_template.triggered.connect(main_window._new_from_template)
        m_file.addSeparator()
        
        main_window.act_open_editor = QAction(tr("menu.file.open_editor"), main_window)
        main_window.act_open_editor.setToolTip("Open integrated file editor")
        main_window.act_open_editor.setShortcut("Ctrl+E")
        m_file.addAction(main_window.act_open_editor)
        main_window.act_open_editor.triggered.connect(lambda: main_window._show_editor())
        m_file.addSeparator()
        
        act_exit = QAction(tr("menu.file.exit"), main_window)
        act_exit.triggered.connect(main_window.close)
        m_file.addAction(act_exit)
    
    @staticmethod
    def _build_edit_menu(main_window, bar) -> None:
        """Build Edit menu with Undo/Redo (Task #12 - v2.9.8)."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_edit = bar.addMenu(tr("menu.edit"))
        
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
    def _build_tools_menu(main_window, bar) -> None:
        """Build Tools menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_tools = bar.addMenu(tr("menu.tools"))
        
        # Fixed tabs accessibility (v2.9.40.2 - Task: menu for closed tabs)
        main_window.act_open_search_replace = QAction("Search / Replace", main_window)
        main_window.act_open_insert = QAction("Insert", main_window)
        main_window.act_open_translate = QAction(tr("menu.tools.json_translate"), main_window)
        main_window.act_open_rewriter = QAction(tr("menu.tools.json_rewriter"), main_window)
        main_window.act_open_text_extractor = QAction(tr("menu.tools.text_extractor"), main_window)
        main_window.act_open_placeholder_replacer = QAction(tr("menu.tools.placeholder_replacer"), main_window)
        main_window.act_open_ai_processor = QAction(tr("menu.tools.ai_processor"), main_window)
        main_window.act_open_json_search = QAction(tr("menu.tools.json_search"), main_window)
        main_window.act_open_case_converter = QAction(tr("menu.tools.case_converter"), main_window)
        main_window.act_open_text_to_json = QAction(tr("menu.tools.text_to_json"), main_window)
        main_window.act_open_google_translate = QAction(tr("menu.tools.google_translate"), main_window)
        main_window.act_open_set_operations = QAction("JSON Set Operations...", main_window)
        main_window.act_open_set_operations.setStatusTip("Perform intersection, union, difference on JSON files (v2.9.32)")
        main_window.act_open_calculator = QAction("🧮 Calculator Memory...", main_window)
        main_window.act_open_calculator.setStatusTip("Store and recall JSON data in 5 memory slots (v2.9.98)")
        main_window.act_open_formula_builder = QAction("📐 Formula Builder...", main_window)
        main_window.act_open_formula_builder.setStatusTip("Build complex formulas with multiple operations (v2.9.108)")
        main_window.act_open_file_list = QAction("File List...", main_window)
        main_window.act_open_file_list.setStatusTip("Generate directory listings with filters (ls-like functionality)")
        main_window.act_advanced_file_search = QAction("Advanced File Search...", main_window)
        main_window.act_advanced_file_search.setStatusTip("Search files with advanced conditions (regex, size, date filters)")
        main_window.act_advanced_file_search.setShortcut("Ctrl+Shift+F")
        
        # Add actions to menu
        m_tools.addAction(main_window.act_open_search_replace)
        m_tools.addAction(main_window.act_open_insert)
        m_tools.addSeparator()
        m_tools.addAction(main_window.act_open_translate)
        m_tools.addAction(main_window.act_open_rewriter)
        m_tools.addAction(main_window.act_open_text_extractor)
        m_tools.addAction(main_window.act_open_placeholder_replacer)
        m_tools.addAction(main_window.act_open_ai_processor)
        m_tools.addAction(main_window.act_open_json_search)
        m_tools.addAction(main_window.act_open_case_converter)
        m_tools.addAction(main_window.act_open_text_to_json)
        m_tools.addAction(main_window.act_open_google_translate)
        m_tools.addAction(main_window.act_open_set_operations)
        m_tools.addAction(main_window.act_open_calculator)
        m_tools.addAction(main_window.act_open_formula_builder)
        m_tools.addSeparator()
        m_tools.addAction(main_window.act_open_file_list)
        m_tools.addAction(main_window.act_advanced_file_search)
        
        # Connect actions
        main_window.act_open_search_replace.triggered.connect(main_window._show_search_replace)
        main_window.act_open_insert.triggered.connect(main_window._show_insert)
        main_window.act_open_translate.triggered.connect(main_window._show_translate)
        main_window.act_open_rewriter.triggered.connect(main_window._show_rewriter)
        main_window.act_open_text_extractor.triggered.connect(main_window._show_text_extractor)
        main_window.act_open_placeholder_replacer.triggered.connect(main_window._show_placeholder_replacer)
        main_window.act_open_ai_processor.triggered.connect(main_window._show_ai_processor)
        main_window.act_open_json_search.triggered.connect(main_window._show_json_search)
        main_window.act_open_case_converter.triggered.connect(main_window._show_case_converter)
        main_window.act_open_text_to_json.triggered.connect(main_window._show_text_to_json)
        main_window.act_open_google_translate.triggered.connect(main_window._show_google_translate)
        main_window.act_open_set_operations.triggered.connect(main_window._show_set_operations)
        main_window.act_open_calculator.triggered.connect(main_window._show_calculator)
        main_window.act_open_formula_builder.triggered.connect(main_window._show_formula_builder)
        main_window.act_open_file_list.triggered.connect(main_window._show_file_list)
        main_window.act_advanced_file_search.triggered.connect(main_window._show_advanced_file_search)
    
    @staticmethod
    def _build_view_menu(main_window, bar) -> None:
        """Build View menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_view = bar.addMenu(tr("menu.view"))
        
        main_window.act_toggle_history = QAction(tr("menu.view.history"), main_window, checkable=True)
        main_window.act_toggle_history.setToolTip("Show/hide operation history panel")
        main_window.act_toggle_history.triggered.connect(main_window._toggle_history)
        m_view.addAction(main_window.act_toggle_history)
        
        # Layouts submenu (v2.9.84)
        m_layouts = m_view.addMenu(tr("menu.view.layouts"))
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
    def _build_themes_menu(main_window, bar) -> None:
        """Build Themes menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_themes = bar.addMenu(tr("menu.themes"))
        
        main_window.act_theme_system = QAction(tr("menu.themes.system"), main_window, checkable=True)
        main_window.act_theme_light = QAction(tr("menu.themes.light"), main_window, checkable=True)
        main_window.act_theme_dark = QAction(tr("menu.themes.dark"), main_window, checkable=True)
        
        grp = [main_window.act_theme_system, main_window.act_theme_light, main_window.act_theme_dark]
        for a in grp:
            m_themes.addAction(a)
            a.triggered.connect(lambda _, x=a: main_window._apply_theme_action(x))
        
        main_window.act_theme_system.setChecked(True)
    
    @staticmethod
    def _build_settings_menu(main_window, bar) -> None:
        """Build Settings menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction, QActionGroup
        
        m_settings = bar.addMenu(tr("menu.settings"))
        act_preferences = QAction(tr("menu.settings.preferences"), main_window)
        act_shortcuts = QAction(tr("menu.settings.shortcuts"), main_window)
        act_transparency = QAction(tr("menu.settings.transparency"), main_window)
        
        # Language submenu (Task #24 - v2.9.10, expanded v2.9.43)
        m_language = m_settings.addMenu(tr("menu.settings.language"))
        
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
        m_settings.addSeparator()
        
        # Advanced submenu (v2.9.89, expanded v2.9.90)
        m_advanced = m_settings.addMenu("Advanced")
        
        # Configuration File Editor (v2.9.90)
        main_window.act_config_editor = QAction("⚙️ Configuration File...", main_window)
        main_window.act_config_editor.setToolTip("Edit config.yaml with visual editor")
        main_window.act_config_editor.triggered.connect(main_window._show_config_editor)
        m_advanced.addAction(main_window.act_config_editor)
        m_advanced.addSeparator()
        
        # Error Reporting submenu
        m_error_reporting = m_advanced.addMenu("Error Reporting")
        main_window.act_error_reporting_toggle = QAction("Enable Error Reporting", main_window, checkable=True)
        main_window.act_error_reporting_toggle.setChecked(main_window.settings.qsettings.value("error_reporting/enabled", True, type=bool))
        main_window.act_error_reporting_toggle.triggered.connect(main_window._toggle_error_reporting)
        m_error_reporting.addAction(main_window.act_error_reporting_toggle)
        
        main_window.act_system_info_toggle = QAction("Include System Info", main_window, checkable=True)
        main_window.act_system_info_toggle.setChecked(main_window.settings.qsettings.value("error_reporting/include_system_info", True, type=bool))
        main_window.act_system_info_toggle.triggered.connect(main_window._toggle_system_info)
        m_error_reporting.addAction(main_window.act_system_info_toggle)
        
        main_window.act_auto_github_toggle = QAction("Auto-open GitHub Issues", main_window, checkable=True)
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
        act_clear_recent.triggered.connect(main_window._clear_recent_files)
    
    @staticmethod
    def _build_plugins_menu(main_window, bar) -> None:
        """Build Plugins menu (v2.9.109 - Enhanced Plugin System)."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_plugins = bar.addMenu(tr("menu.plugins"))
        
        # Plugin Manager submenu
        main_window.act_plugin_manager = QAction("🔌 Plugin Manager...", main_window)
        main_window.act_plugin_manager.setToolTip("Manage installed plugins")
        main_window.act_plugin_manager.setStatusTip("View, enable, disable, and configure plugins")
        m_plugins.addAction(main_window.act_plugin_manager)
        main_window.act_plugin_manager.triggered.connect(main_window._show_plugin_manager)
        
        m_plugins.addSeparator()
        
        # Installed plugins (dynamic menu based on discovered plugins)
        if hasattr(main_window, "plugin_loader"):
            metadata_list = main_window.plugin_loader.get_all_metadata()
            if metadata_list:
                for metadata in metadata_list:
                    status = "✅" if metadata.enabled else "❌"
                    act = QAction(f"{status} {metadata.name}", main_window)
                    act.setToolTip(f"{metadata.description}\nv{metadata.version} by {metadata.author}")
                    act.setStatusTip(f"Toggle {metadata.name} plugin")
                    act.setCheckable(True)
                    act.setChecked(metadata.enabled)
                    act.triggered.connect(lambda checked, pid=metadata.id: main_window._toggle_plugin(pid, checked))
                    m_plugins.addAction(act)
            else:
                act_no_plugins = QAction("No plugins installed", main_window)
                act_no_plugins.setEnabled(False)
                m_plugins.addAction(act_no_plugins)
    
    @staticmethod
    def _build_help_menu(main_window, bar) -> None:
        """Build Help menu (Task #45 - v2.9.15)."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_help = bar.addMenu(tr("menu.help"))
        
        main_window.act_open_tutorials = QAction(tr("menu.help.tutorials"), main_window)
        main_window.act_open_tutorials.setToolTip("Browse beginner and developer tutorials")
        m_help.addAction(main_window.act_open_tutorials)
        main_window.act_open_tutorials.triggered.connect(main_window._show_tutorials)
        
        # AI Tutorial Assistant (v2.9.92)
        main_window.act_ai_assistant = QAction("AI Tutorial Assistant", main_window)
        main_window.act_ai_assistant.setToolTip("Ask AI about Clarify tutorials")
        main_window.act_ai_assistant.setStatusTip("Chat with AI assistant for Clarify tutorials and troubleshooting (requires API key)")
        m_help.addAction(main_window.act_ai_assistant)
        main_window.act_ai_assistant.triggered.connect(main_window._show_ai_assistant)
        
        # Keyboard Shortcuts Help (v2.9.33)
        main_window.act_keyboard_shortcuts_help = QAction("Keyboard Shortcuts Help", main_window)
        main_window.act_keyboard_shortcuts_help.setToolTip("View all available keyboard shortcuts")
        main_window.act_keyboard_shortcuts_help.setStatusTip("View complete list of keyboard shortcuts organized by category")
        main_window.act_keyboard_shortcuts_help.setShortcut("F1")
        m_help.addAction(main_window.act_keyboard_shortcuts_help)
        main_window.act_keyboard_shortcuts_help.triggered.connect(main_window._show_keyboard_shortcuts_help)
        
        # Keyboard Shortcuts Customization (v2.9.62)
        main_window.act_customize_shortcuts = QAction("Customize Shortcuts...", main_window)
        main_window.act_customize_shortcuts.setToolTip("Customize keyboard shortcuts")
        main_window.act_customize_shortcuts.setStatusTip("Customize keyboard shortcuts for all actions and save custom profiles")
        main_window.act_customize_shortcuts.setShortcut("Ctrl+K Ctrl+S")
        m_help.addAction(main_window.act_customize_shortcuts)
        main_window.act_customize_shortcuts.triggered.connect(main_window._customize_shortcuts)
        
        m_help.addSeparator()
        
        # View Logs (v2.9.64 - Logging System Integration)
        main_window.act_view_logs = QAction("📄 View Logs", main_window)
        main_window.act_view_logs.setToolTip("Open log files in default editor")
        m_help.addAction(main_window.act_view_logs)
        main_window.act_view_logs.triggered.connect(main_window._view_logs)
        
        # Update Checker (v2.9.45)
        main_window.act_check_updates = QAction("🔄 Verificar Atualizações", main_window)
        main_window.act_check_updates.setToolTip("Check for new Clarify versions from GitHub")
        m_help.addAction(main_window.act_check_updates)
        main_window.act_check_updates.triggered.connect(main_window._check_for_updates_manual)
    
    @staticmethod
    def _build_about_menu(main_window, bar) -> None:
        """Build About menu."""
        from ..i18n import tr
        from PySide6.QtGui import QAction
        
        m_about = bar.addMenu(tr("menu.about"))
        act_about = QAction(tr("menu.about.clarify"), main_window)
        m_about.addAction(act_about)
        act_about.triggered.connect(main_window._about_dialog)
    
    @staticmethod
    def _setup_shortcuts(main_window) -> None:
        """Setup keyboard shortcuts."""
        from ..shortcut_manager import ShortcutManager
        from PySide6.QtGui import QShortcut, QKeySequence
        
        # Exit shortcut
        shortcut_exit = QShortcut(ShortcutManager.get_key_sequence("exit"), main_window)
        shortcut_exit.activated.connect(main_window.close)
        
        # Help shortcut
        shortcut_help = QShortcut(ShortcutManager.get_key_sequence("help"), main_window)
        shortcut_help.activated.connect(main_window._show_shortcuts)
        
        # About shortcut
        shortcut_about = QShortcut(ShortcutManager.get_key_sequence("about"), main_window)
        shortcut_about.activated.connect(main_window._about_dialog)
        
        # Tab navigation shortcuts (v2.9.113)
        shortcut_next_tab = QShortcut(QKeySequence("Ctrl+PgDown"), main_window)
        shortcut_next_tab.activated.connect(main_window._next_tab)
        
        shortcut_prev_tab = QShortcut(QKeySequence("Ctrl+PgUp"), main_window)
        shortcut_prev_tab.activated.connect(main_window._previous_tab)
        
        # Apply all shortcuts to menu items with tooltips (v2.9.33)
        main_window._apply_shortcuts_to_menu()
