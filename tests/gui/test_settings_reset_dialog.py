"""GUI coverage for the translated reset preview and safe hot reload boundary."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

import json
from unittest.mock import Mock, patch

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMainWindow

from src.config_manager import ConfigManager
from src.gui.settings_reset_dialog import SettingsResetDialog, show_settings_reset
from src.gui.menu_builder import MenuBuilder
from src.i18n import get_translator, tr
from src.settings_manager import SettingsManager
from src.settings_reset import ResetResult, SettingsResetService


def _service(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    settings = SettingsManager(str(tmp_path / "settings.json"))
    config = ConfigManager(str(tmp_path / "config.yaml"))
    stores = {}

    def factory(_organization, application):
        stores.setdefault(
            application,
            QSettings(str(tmp_path / f"{application}.ini"), QSettings.IniFormat),
        )
        return stores[application]

    return SettingsResetService(
        settings, config, qsettings_factory=factory,
        legacy_paths=(), backup_dir=tmp_path / "backups",
    )


def test_dialog_previews_categories_and_protected_data(qtbot, tmp_path):
    dialog = SettingsResetDialog(None, _service(tmp_path))
    qtbot.addWidget(dialog)

    assert len(dialog.selected_categories()) == 6
    protected = dialog.findChild(QLabel, "settingsResetProtectedNotice")
    assert protected is not None
    assert "documents" in protected.text().lower()
    dialog.select_all.setChecked(False)
    assert dialog.selected_categories() == ()
    assert not dialog.buttons.button(QDialogButtonBox.Reset).isEnabled()


def test_show_reset_hot_reloads_only_when_appearance_selected(qtbot, tmp_path, monkeypatch):
    window = QMainWindow()
    qtbot.addWidget(window)
    window.settings = SettingsManager(str(tmp_path / "settings.json"))
    service = _service(tmp_path / "service")
    monkeypatch.setattr(
        service,
        "reset",
        lambda selected: ResetResult(tmp_path / "backup.zip", tuple(selected), True),
    )

    monkeypatch.setattr(SettingsResetDialog, "exec", lambda self: QDialog.Accepted)
    monkeypatch.setattr(SettingsResetDialog, "selected_categories", lambda self: ("appearance", "general"))
    with patch("src.gui.settings_reset_dialog.WindowSettings.apply_saved_settings") as apply, patch(
        "src.gui.settings_reset_dialog.QMessageBox.information"
    ):
        show_settings_reset(window, service)

    apply.assert_called_once_with(window)


def test_all_catalogs_contain_complete_reset_translation_tree():
    root = __import__("pathlib").Path(__file__).parents[2] / "src" / "i18n"
    expected = None
    for path in sorted(root.glob("*.json")):
        tree = json.loads(path.read_text(encoding="utf-8"))["settings_reset"]
        keys = set(tree) | {f"category.{key}" for key in tree["category"]}
        expected = keys if expected is None else expected
        assert keys == expected, path.name


def test_settings_menu_exposes_one_translated_reset_action(qtbot, tmp_path):
    window = QMainWindow()
    qtbot.addWidget(window)
    window.settings = SettingsManager(str(tmp_path / "settings.json"))
    window.settings.qsettings = QSettings(str(tmp_path / "qt.ini"), QSettings.IniFormat)
    window.translator = get_translator()
    for name in (
        "_switch_language", "_show_preferences", "_show_shortcuts",
        "_show_transparency_dialog", "_show_config_editor", "_toggle_error_reporting",
        "_toggle_system_info", "_toggle_auto_github", "_clear_recent_files",
    ):
        setattr(window, name, Mock())
    window._show_settings_reset = Mock()

    MenuBuilder._build_settings_menu(window, window.menuBar())
    assert window.act_reset_settings.text() == tr("settings_reset.action")
    window.act_reset_settings.trigger()
    window._show_settings_reset.assert_called_once_with()
