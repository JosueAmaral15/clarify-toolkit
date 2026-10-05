"""
Initialization Manager for MainWindow

Centralizes initialization logic from MainWindow.__init__, reducing complexity.
Extracted from MainWindow as part of Phase 3.7 refactoring.

Groups initialization into logical sections:
- Core systems (logging, error handling, crash handler)
- Configuration (settings, translator, migrations)
- Managers (command manager, plugin loader, layout manager)
- UI components (build icon, UI, menu)

Author: Refactoring Phase 3.7
Date: 2024-12-24
Version: v2.9.114
"""
# pylint: disable=import-outside-toplevel  # Lazy imports for startup performance
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=protected-access  # Calling MainWindow internal methods intentionally

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from ..app import MainWindow


class InitializationManager:
    """
    Centralized initialization for MainWindow.

    Organizes the 1106-line __init__ into logical, testable sections.
    """

    @staticmethod
    def initialize_core_systems(main_window: 'MainWindow') -> None:
        """
        Initialize core systems: logging, error handling, crash handler.

        Args:
            main_window: MainWindow instance
        """
        from ..utils.logger import get_logger
        from ..utils.error_handler import install_crash_handler
        from ..utils.error_reporter import install_error_reporter
        from ..gui.error_report_dialog import ErrorReportDialog

        # Initialize logging system (v2.9.58)
        main_window.logger = get_logger("clarify.app.MainWindow")
        main_window.logger.info("Initializing Clarify application")

        # Initialize error reporter (v2.9.89)
        main_window.error_reporter = install_error_reporter(app_version="2.9.89")
        main_window.error_dialog = ErrorReportDialog(main_window)
        main_window.error_reporter.dialog = main_window.error_dialog
        main_window.logger.info("Error reporter installed")

        # Initialize crash handler (v2.9.61)
        main_window.crash_handler = install_crash_handler(
            show_dialog=True,
            report_crashes=False  # Opt-in only
        )
        main_window.logger.info("Crash handler installed")

    @staticmethod
    def initialize_configuration(main_window: 'MainWindow') -> None:
        """
        Initialize configuration: migrations, translator, settings.

        Args:
            main_window: MainWindow instance
        """
        from ..migration_manager import run_migrations
        from ..i18n.translator import get_translator
        from ..settings_manager import get_settings
        from PySide6.QtCore import QSettings

        # Run database migrations BEFORE loading config/settings (v2.9.91)
        migrations_ok = run_migrations()
        if not migrations_ok:
            main_window.logger.warning("Migrations failed, continuing with current version")

        # Initialize translator (Task #24 - v2.9.10)
        main_window.translator = get_translator()

        # Initialize settings manager
        main_window.settings = get_settings()
        main_window.translator.switch_language(main_window.settings.get("language", "en"))
        main_window.translator.languageChanged.connect(main_window._on_language_changed)

        # Initialize QSettings for accessibility (v2.9.40 - compatibility fix)
        main_window.settings.qsettings = QSettings("Clarify", "ClarifyApp")

    @staticmethod
    def initialize_managers(main_window: 'MainWindow') -> None:
        """
        Initialize managers: shortcuts, command manager, plugins, layouts.

        Args:
            main_window: MainWindow instance
        """
        from ..shortcut_manager import ShortcutManager
        from ..core.command_manager import CommandManager
        from ..plugin_loader import PluginLoader
        from ..layout_manager import LayoutManager

        # Load custom shortcuts (v2.9.33)
        custom_shortcuts = main_window.settings.get_custom_shortcuts()
        ShortcutManager.load_custom_shortcuts(custom_shortcuts)

        # Initialize Command Manager for Undo/Redo (Task #12 - v2.9.8)
        main_window.command_manager = CommandManager(max_history=10)

        # Plugin System (v2.9.109 - Enhanced with metadata and events)
        main_window.plugin_loader = PluginLoader(main_window)
        discovered = main_window.plugin_loader.discover_plugins()
        main_window.logger.info(f"[PluginSystem] Discovered {len(discovered)} plugin(s)")

        # Track tool tabs (v2.9.40 - Task: Tools as tabs)
        main_window.tool_tabs = {}  # Maps tool_name -> (widget, tab_index)

        # Initialize Layout Manager (v2.9.84)
        main_window.layout_manager = LayoutManager(main_window)
        main_window.logger.info("LayoutManager initialized")

    @staticmethod
    def build_ui_components(main_window: 'MainWindow') -> None:
        """
        Build UI components: icon, UI, menu, restore preferences.

        Args:
            main_window: MainWindow instance
        """
        from ..i18n.translator import tr

        # Set window title
        main_window.setWindowTitle(tr("app.title"))

        # Build components
        main_window._build_icon()
        main_window._build_ui()
        main_window._build_menu()
        activated = main_window.plugin_loader.activate_all_plugins()
        main_window.logger.info(f"[PluginSystem] Activated {activated} plugin(s)")
        main_window._restore_prefs()
        main_window._apply_saved_settings()

        # Register docks with LayoutManager (v2.9.84)
        main_window._register_docks_with_layout_manager()

    @staticmethod
    def initialize_all(main_window: 'MainWindow', app: 'QApplication') -> None:
        """
        Run all initialization steps in correct order.

        Args:
            main_window: MainWindow instance
            app: QApplication instance
        """
        # Store app reference
        main_window.app = app

        # Initialize in order (dependencies matter!)
        InitializationManager.initialize_core_systems(main_window)
        InitializationManager.initialize_configuration(main_window)
        InitializationManager.initialize_managers(main_window)
        InitializationManager.build_ui_components(main_window)
