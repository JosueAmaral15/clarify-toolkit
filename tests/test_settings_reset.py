"""Core regressions for backed-up, data-preserving settings reset."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

import json
import stat
from pathlib import Path

import pytest
import yaml
from PySide6.QtCore import QSettings

from src.config_manager import ConfigManager
from src.settings_manager import SettingsManager
from src.settings_reset import (
    ALL_RESET_SECTIONS,
    ResetSection,
    SettingsResetCoordinator,
    SettingsResetError,
)


def _coordinator(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    settings = SettingsManager(str(home / "settings.json"))
    settings.qsettings = QSettings(str(home / "qt.ini"), QSettings.IniFormat)
    config = ConfigManager(
        str(home / ".config" / "clarify" / "config.yaml"),
        migrate_legacy=False,
    )
    coordinator = SettingsResetCoordinator(
        settings,
        config=config,
        qsettings=settings.qsettings,
        backup_root=home / "backups",
        home=home,
    )
    return home, settings, config, settings.qsettings, coordinator


def test_global_reset_preserves_user_data_and_aligns_stores(tmp_path):
    home, settings, config, qsettings, coordinator = _coordinator(tmp_path)
    settings.update_multiple({
        "theme": "light", "window_opacity": 61, "language": "pt_BR",
        "recent_files": ["/private/document.txt"], "window_geometry": "geometry",
        "last_directory": "/private/project", "tabs_open_tools": ["editor"],
        "credential_token": "keep-me", "custom_shortcuts": {"open": "Alt+O"},
    })
    config.update({
        "app.theme": "light", "app.window_opacity": 61,
        "app.language": "pt-br", "logging.level": "DEBUG",
        "ai.local_credential": "keep-me",
    })
    qsettings.setValue("theme", "light")
    qsettings.setValue("window_opacity", 61)
    qsettings.setValue("language", "pt_BR")
    qsettings.setValue("error_reporting/enabled", False)
    qsettings.setValue("layouts/custom", "keep-me")
    qsettings.sync()
    legacy = home / ".config" / "clarify.conf"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("[THEME]\nmode = light\n[SECRET]\ntoken = keep-me\n", encoding="utf-8")
    protected = home / ".config" / "clarify" / "recovery" / "snapshot.json"
    protected.parent.mkdir(parents=True)
    protected.write_text("protected", encoding="utf-8")

    result = coordinator.reset(ALL_RESET_SECTIONS)

    assert result.restart_required
    assert settings.get("theme") == "dark"
    assert settings.get("window_opacity") == 96
    assert settings.get("language") == "en"
    assert settings.get("recent_files") == ["/private/document.txt"]
    assert settings.get("window_geometry") == "geometry"
    assert settings.get("last_directory") == "/private/project"
    assert settings.get("tabs_open_tools") == ["editor"]
    assert settings.get("credential_token") == "keep-me"
    assert settings.get("custom_shortcuts") == {}
    assert config.get("app.theme") == "dark"
    assert config.get("app.window_opacity") == 96
    assert config.get("app.language") == "en"
    assert config.get("logging.level") == "INFO"
    assert config.get("ai.local_credential") == "keep-me"
    assert qsettings.value("theme") == "dark"
    assert qsettings.value("window_opacity", type=int) == 96
    assert qsettings.value("layouts/custom") == "keep-me"
    assert "mode = dark" in legacy.read_text(encoding="utf-8")
    assert "token = keep-me" in legacy.read_text(encoding="utf-8")
    assert protected.read_text(encoding="utf-8") == "protected"

    manifest = json.loads((result.backup_path / "manifest.json").read_text())
    json_entry = next(
        item for item in manifest["stores"] if item["source"].endswith("settings.json")
    )
    backed_up_json = json.loads(
        (result.backup_path / json_entry["backup"]).read_text(encoding="utf-8")
    )
    assert backed_up_json["theme"] == "light"
    assert backed_up_json["recent_files"] == ["/private/document.txt"]
    assert stat.S_IMODE(result.backup_path.stat().st_mode) == 0o700
    for backup in result.backup_path.iterdir():
        assert stat.S_IMODE(backup.stat().st_mode) == 0o600


def test_section_reset_changes_only_selected_category(tmp_path):
    _, settings, config, qsettings, coordinator = _coordinator(tmp_path)
    settings.update_multiple({
        "theme": "light", "window_opacity": 55, "language": "pt_BR",
        "custom_shortcuts": {"save": "Alt+S"},
    })
    config.update({"app.theme": "light", "app.language": "pt-br"})
    qsettings.setValue("theme", "light")
    qsettings.setValue("language", "pt_BR")
    qsettings.sync()

    result = coordinator.reset((ResetSection.APPEARANCE,))

    assert not result.restart_required
    assert settings.get("theme") == "dark"
    assert settings.get("window_opacity") == 96
    assert settings.get("language") == "pt_BR"
    assert settings.get("custom_shortcuts") == {"save": "Alt+S"}
    assert config.get("app.theme") == "dark"
    assert config.get("app.language") == "pt-br"
    assert qsettings.value("theme") == "dark"
    assert qsettings.value("language") == "pt_BR"


def test_failed_mutation_rolls_back_all_existing_stores(tmp_path, monkeypatch):
    _, settings, config, qsettings, coordinator = _coordinator(tmp_path)
    settings.update_multiple({"theme": "light", "recent_files": ["keep"]})
    config.set("app.theme", "light")
    qsettings.setValue("theme", "light")
    qsettings.sync()
    before_json = settings.config_file.read_bytes()
    before_yaml = config.config_file.read_bytes()
    before_qt = Path(qsettings.fileName()).read_bytes()

    monkeypatch.setattr(
        coordinator,
        "_reset_qsettings",
        lambda _selected: (_ for _ in ()).throw(OSError("simulated QSettings failure")),
    )
    with pytest.raises(SettingsResetError, match="simulated QSettings failure"):
        coordinator.reset((ResetSection.APPEARANCE,))

    assert settings.config_file.read_bytes() == before_json
    assert config.config_file.read_bytes() == before_yaml
    assert Path(qsettings.fileName()).read_bytes() == before_qt
    assert settings.get("theme") == "light"
    assert settings.get("recent_files") == ["keep"]
    assert config.get("app.theme") == "light"


def test_unsafe_store_aborts_before_preference_mutation(tmp_path):
    _, settings, _, _, coordinator = _coordinator(tmp_path)
    original = tmp_path / "original.json"
    original.write_text('{"theme": "light"}', encoding="utf-8")
    settings.config_file.unlink(missing_ok=True)
    settings.config_file.symlink_to(original)
    settings.settings["theme"] = "light"

    with pytest.raises(SettingsResetError, match="Unsafe settings store"):
        coordinator.reset((ResetSection.APPEARANCE,))

    assert settings.get("theme") == "light"
    assert original.read_text(encoding="utf-8") == '{"theme": "light"}'


def test_direct_settings_reset_retains_state_and_unknown_data(tmp_path):
    settings = SettingsManager(str(tmp_path / "settings.json"))
    settings.update_multiple({
        "theme": "light", "recent_files": ["keep"],
        "window_geometry": "keep", "unknown_session": {"keep": True},
    })

    settings.reset_to_defaults()

    assert settings.get("theme") == "dark"
    assert settings.get("recent_files") == ["keep"]
    assert settings.get("window_geometry") == "keep"
    assert settings.get("unknown_session") == {"keep": True}


def test_explicit_config_path_does_not_migrate_home_legacy(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    legacy = home / ".clarify_settings.json"
    legacy.write_text('{"theme": "light"}', encoding="utf-8")
    monkeypatch.setattr("src.config_manager.Path.home", lambda: home)

    config = ConfigManager(str(tmp_path / "isolated" / "config.yaml"))

    assert config.get("app.theme") == "dark"
    assert legacy.exists()
    assert not legacy.with_suffix(".json.migrated").exists()


def test_config_reset_preserves_unknown_nested_values(tmp_path):
    config = ConfigManager(str(tmp_path / "config.yaml"))
    config.set("app.theme", "light", save=False)
    config.set("ai.credential", "keep", save=False)
    config.set("plugin.custom", True)

    config.reset_to_defaults()

    loaded = yaml.safe_load(config.config_file.read_text(encoding="utf-8"))
    assert loaded["app"]["theme"] == "dark"
    assert loaded["app"]["window_opacity"] == 96
    assert loaded["ai"]["credential"] == "keep"
    assert loaded["plugin"]["custom"] is True
