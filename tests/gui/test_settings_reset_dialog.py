"""Focused GUI contracts for the settings reset action and preview."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QMainWindow, QMenuBar, QMessageBox

from src.app import MainWindow
from src.gui.menu_builder import MenuBuilder
from src.gui.settings_reset_dialog import SettingsResetDialog
from src.settings_manager import SettingsManager
from src.settings_reset import ResetSection, SettingsResetResult


class _Coordinator:
    def __init__(self, backup_path):
        self.backup_path = backup_path
        self.calls = []

    def reset(self, sections):
        self.calls.append(tuple(sections))
        return SettingsResetResult(tuple(sections), self.backup_path, False)


def test_dialog_previews_sections_and_confirms_selected_reset(
    qtbot, tmp_path, monkeypatch
):
    coordinator = _Coordinator(tmp_path / "backup")
    dialog = SettingsResetDialog(coordinator)
    qtbot.addWidget(dialog)
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)

    dialog.selected_radio.setChecked(True)
    dialog.section_checks[ResetSection.GENERAL].setChecked(False)
    dialog.section_checks[ResetSection.SHORTCUTS].setChecked(False)
    dialog.section_checks[ResetSection.ADVANCED].setChecked(False)

    assert "Appearance" in dialog.preview.toPlainText()
    assert "General" not in dialog.preview.toPlainText()
    dialog._confirm_reset()

    assert coordinator.calls == [(ResetSection.APPEARANCE,)]
    assert dialog.reset_result is not None
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_dialog_requires_at_least_one_selected_section(qtbot, tmp_path):
    dialog = SettingsResetDialog(_Coordinator(tmp_path / "backup"))
    qtbot.addWidget(dialog)
    dialog.selected_radio.setChecked(True)
    for check in dialog.section_checks.values():
        check.setChecked(False)

    assert not dialog.reset_button.isEnabled()
    assert dialog.selected_sections() == ()


def test_settings_menu_exposes_translated_reset_action(qtbot, tmp_path):
    window = QMainWindow()
    qtbot.addWidget(window)
    qsettings = QSettings(str(tmp_path / "settings.ini"), QSettings.IniFormat)
    called = []
    window.settings = SimpleNamespace(qsettings=qsettings)
    window.translator = SimpleNamespace(current_language="en")
    window._show_preferences = lambda: None
    window._show_shortcuts = lambda: None
    window._show_transparency_dialog = lambda: None
    window._show_settings_reset = lambda: called.append(True)
    window._show_config_editor = lambda: None
    window._toggle_error_reporting = lambda _checked: None
    window._toggle_system_info = lambda _checked: None
    window._toggle_auto_github = lambda _checked: None
    window._clear_recent_files = lambda: None

    menu_bar = QMenuBar(window)
    MenuBuilder._build_settings_menu(window, menu_bar)

    assert window.act_reset_settings.text() == "Reset Settings..."
    window.act_reset_settings.trigger()
    assert called == [True]


def test_main_window_applies_only_safe_runtime_reset_values(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr("pathlib.Path.home", lambda: home)
    settings = SettingsManager(str(home / "settings.json"))
    settings.qsettings = QSettings(str(home / "qt.ini"), QSettings.IniFormat)
    settings.update_multiple({"theme": "dark", "language": "en", "custom_shortcuts": {}})
    settings.qsettings.setValue("error_reporting/enabled", True)
    settings.qsettings.setValue("error_reporting/include_system_info", True)
    settings.qsettings.setValue("error_reporting/auto_open_github", False)
    settings.qsettings.sync()
    result = SettingsResetResult(
        (
            ResetSection.APPEARANCE,
            ResetSection.GENERAL,
            ResetSection.SHORTCUTS,
            ResetSection.ADVANCED,
        ),
        home / "backup",
        True,
    )

    class _AcceptedDialog:
        def __init__(self, _coordinator, _parent):
            self.reset_result = result

        def exec(self):
            return QDialog.DialogCode.Accepted

    language_calls = []
    shortcut_calls = []
    fake = SimpleNamespace(
        settings=settings,
        translator=SimpleNamespace(switch_language=language_calls.append),
        act_error_reporting_toggle=QAction(checkable=True),
        act_system_info_toggle=QAction(checkable=True),
        act_auto_github_toggle=QAction(checkable=True),
        _apply_shortcuts_to_menu=lambda: shortcut_calls.append("applied"),
    )
    with (
        patch("src.gui.settings_reset_dialog.SettingsResetDialog", _AcceptedDialog),
        patch("src.gui.window_settings.WindowSettings.apply_saved_settings") as appearance,
        patch("src.shortcut_manager.ShortcutManager.load_custom_shortcuts") as shortcuts,
        patch.object(QMessageBox, "information") as information,
    ):
        MainWindow._show_settings_reset(fake)

    appearance.assert_called_once_with(fake)
    assert language_calls == ["en"]
    shortcuts.assert_called_once_with({})
    assert shortcut_calls == ["applied"]
    assert fake.act_error_reporting_toggle.isChecked()
    assert fake.act_system_info_toggle.isChecked()
    assert not fake.act_auto_github_toggle.isChecked()
    assert "Restart Clarify" in information.call_args.args[2]
