"""Regression coverage for new-profile appearance defaults and persistence."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from configparser import ConfigParser
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget

from src.app import MainWindow
from src.appearance_defaults import opacity_percent_to_qt
from src.gui.tool_window_manager import ToolWindowManager
from src.gui.transparency_dialog import TransparencyDialog
from src.gui.window_settings import WindowSettings
from src.settings_manager import SettingsManager


class _FakeWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.act_theme_system = QAction(self, checkable=True)
        self.act_theme_light = QAction(self, checkable=True)
        self.act_theme_dark = QAction(self, checkable=True)


def test_new_profile_uses_dark_and_96_percent_opacity(tmp_path):
    settings = SettingsManager(str(tmp_path / "missing.json"))

    assert settings.get("theme") == "dark"
    assert settings.get("window_opacity") == 96
    assert not settings.has_saved_value("theme")
    assert not settings.has_saved_value("window_opacity")


def test_existing_profile_values_remain_authoritative(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"theme": "system", "window_opacity": 73}', encoding="utf-8")

    settings = SettingsManager(str(path))

    assert settings.get("theme") == "system"
    assert settings.get("window_opacity") == 73
    assert settings.has_saved_value("theme")
    assert settings.has_saved_value("window_opacity")


def test_startup_applies_default_opacity_as_qt_opacity(qapp, qtbot, tmp_path):
    window = _FakeWindow(SettingsManager(str(tmp_path / "missing.json")))
    qtbot.addWidget(window)

    with patch("src.theme_manager.ThemeManager.apply_theme") as apply_theme:
        WindowSettings.apply_saved_settings(window)

    apply_theme.assert_called_once_with(qapp, "dark")
    assert window.act_theme_dark.isChecked()
    assert opacity_percent_to_qt(96) == pytest.approx(0.96)
    assert window.windowOpacity() == pytest.approx(0.96, abs=1 / 255)


def test_startup_preserves_explicit_system_theme_and_opacity(qapp, qtbot, tmp_path):
    path = tmp_path / "settings.json"
    path.write_text('{"theme": "system", "window_opacity": 73}', encoding="utf-8")
    window = _FakeWindow(SettingsManager(str(path)))
    qtbot.addWidget(window)

    with patch("src.theme_manager.ThemeManager.apply_theme") as apply_theme:
        WindowSettings.apply_saved_settings(window)

    apply_theme.assert_called_once_with(qapp, "system")
    assert window.act_theme_system.isChecked()
    assert window.windowOpacity() == pytest.approx(0.73, abs=1 / 255)


def test_transparency_dialog_displays_and_applies_opacity_semantics(qtbot, tmp_path):
    window = _FakeWindow(SettingsManager(str(tmp_path / "missing.json")))
    dialog = TransparencyDialog(window)
    qtbot.addWidget(window)
    qtbot.addWidget(dialog)

    assert dialog.opacity_slider.value() == 96
    assert "96%" in dialog.opacity_label.text()

    dialog.opacity_slider.setValue(80)
    assert window.windowOpacity() == pytest.approx(0.80, abs=1 / 255)
    assert "20%" in dialog.opacity_label.text()

    dialog._cancel_and_close()
    assert window.windowOpacity() == pytest.approx(0.96, abs=1 / 255)


def test_runtime_theme_action_persists_to_active_settings(qapp, tmp_path, monkeypatch):
    settings = SettingsManager(str(tmp_path / "settings.json"))
    window = SimpleNamespace(
        settings=settings,
        act_theme_system=QAction(checkable=True),
        act_theme_light=QAction(checkable=True),
        act_theme_dark=QAction(checkable=True),
        _apply_tab_close_button_style=lambda: None,
    )
    legacy = ConfigParser()
    monkeypatch.setattr("src.app.load_prefs", lambda: legacy)
    monkeypatch.setattr("src.app.save_prefs", lambda _cfg: None)

    with patch("src.app.apply_theme") as apply_theme:
        MainWindow._apply_theme_action(window, window.act_theme_light)

    apply_theme.assert_called_once_with(qapp, "light")
    assert settings.get("theme") == "light"
    assert SettingsManager(str(tmp_path / "settings.json")).get("theme") == "light"


def test_legacy_theme_is_migrated_only_without_json_choice(tmp_path, monkeypatch):
    legacy_dir = tmp_path / ".config"
    legacy_dir.mkdir()
    (legacy_dir / "clarify.conf").write_text("[THEME]\nmode = light\n", encoding="utf-8")
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    missing = SettingsManager(str(tmp_path / "new.json"))
    WindowSettings.restore_prefs(SimpleNamespace(settings=missing))
    assert missing.get("theme") == "light"

    explicit_path = tmp_path / "existing.json"
    explicit_path.write_text('{"theme": "system"}', encoding="utf-8")
    explicit = SettingsManager(str(explicit_path))
    WindowSettings.restore_prefs(SimpleNamespace(settings=explicit))
    assert explicit.get("theme") == "system"


def test_new_detached_window_inherits_main_window_opacity(qtbot):
    main = QMainWindow()
    main.tabs = QTabWidget(main)
    main.setCentralWidget(main.tabs)
    main.tool_tabs = {}
    main._save_tab_state = lambda: None
    main._restore_window_flags = lambda: None
    main.setWindowOpacity(0.73)
    tool = QWidget()
    tool.setProperty("clarify_tool_id", "test-tool")
    main.tabs.addTab(tool, "Test")
    qtbot.addWidget(main)

    manager = ToolWindowManager(main)
    main.tool_window_manager = manager
    assert manager.detach_tool(tool)
    detached = manager._detached[tool].window

    assert detached.windowOpacity() == pytest.approx(0.73, abs=1 / 255)
    WindowSettings.apply_window_opacity_percent(main, 81)
    assert detached.windowOpacity() == pytest.approx(0.81, abs=1 / 255)
    manager.attach_tool(tool)
