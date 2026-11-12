"""Core regression coverage for safe, transactional settings reset."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

import json
import stat
import zipfile
from pathlib import Path

import pytest
import yaml
from PySide6.QtCore import QSettings

from src.config_manager import ConfigManager
from src.settings_manager import SettingsManager
from src.settings_reset import SettingsResetError, SettingsResetService


def _factory(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    stores = {}

    def create(_organization: str, application: str):
        if application not in stores:
            stores[application] = QSettings(
                str(root / f"{application}.ini"), QSettings.IniFormat
            )
        return stores[application]

    return create, stores


def _service(tmp_path):
    json_path = tmp_path / "settings.json"
    json_path.write_text(
        json.dumps({
            "theme": "light", "window_opacity": 42, "language": "pt_BR",
            "custom_shortcuts": {"save": "Alt+S"},
            "recent_files": ["/private/document.txt"],
            "ai_processor/gemini_api_key": "secret",
        }),
        encoding="utf-8",
    )
    yaml_path = tmp_path / "config.yaml"
    config = ConfigManager(str(yaml_path))
    config.set("app.theme", "system")
    config.set("app.window_opacity", 51)
    config.set("credentials.token", "keep-me")
    settings = SettingsManager(str(json_path))
    factory, stores = _factory(tmp_path / "qsettings")
    legacy = tmp_path / "clarify.conf"
    legacy.write_text("[THEME]\nmode = light\n[PRIVATE]\ntoken = keep-me\n", encoding="utf-8")
    service = SettingsResetService(
        settings,
        config,
        qsettings_factory=factory,
        legacy_paths=(legacy, tmp_path / "missing.ini"),
        backup_dir=tmp_path / "backups",
    )
    return service, settings, config, stores, legacy


def test_global_reset_aligns_defaults_and_preserves_user_data(tmp_path):
    service, settings, config, stores, legacy = _service(tmp_path)
    app = service._qsettings_factory("Clarify", "ClarifyApp")  # pylint: disable=protected-access
    editor = service._qsettings_factory("Clarify", "EditorDock")  # pylint: disable=protected-access
    app.setValue("LastLayout", "Custom")
    app.setValue("Layouts/Custom/tabs", "user-layout")
    app.setValue("plugins/example/enabled", True)
    editor.setValue("indent_width", 8)
    editor.setValue("folder_sessions", "private-session")

    result = service.reset(category.category_id for category in service.categories())

    assert result.restart_required
    assert result.backup_path.exists()
    assert stat.S_IMODE(result.backup_path.stat().st_mode) == 0o600
    with zipfile.ZipFile(result.backup_path) as archive:
        assert json.loads(archive.read("manifest.json"))["format"] == 1
        assert json.loads(archive.read("settings.json"))["theme"] == "light"
        assert "ClarifyApp" in json.loads(archive.read("qsettings.json"))

    assert settings.get("theme") == "dark"
    assert settings.get("window_opacity") == 96
    assert settings.get("language") == "en"
    assert settings.get("recent_files") == ["/private/document.txt"]
    assert settings.get("ai_processor/gemini_api_key") == "secret"
    assert settings.get("custom_shortcuts") == {}
    assert config.get("app.theme") == "dark"
    assert config.get("app.window_opacity") == 96
    assert config.get("credentials.token") == "keep-me"
    assert app.value("LastLayout") is None
    assert app.value("language") == "en"
    assert app.value("Layouts/Custom/tabs") == "user-layout"
    assert app.value("plugins/example/enabled", type=bool) is True
    assert editor.value("indent_width") is None
    assert editor.value("folder_sessions") == "private-session"
    assert "mode = dark" in legacy.read_text(encoding="utf-8")
    assert "token = keep-me" in legacy.read_text(encoding="utf-8")
    assert not (tmp_path / "missing.ini").exists()
    assert set(stores) == {"ClarifyApp", "EditorDock", "FileExplorer", "FileList"}


def test_partial_reset_changes_only_selected_category(tmp_path):
    service, settings, config, _stores, legacy = _service(tmp_path)

    result = service.reset(["shortcuts"])

    assert result.categories == ("shortcuts",)
    assert result.restart_required
    assert settings.get("custom_shortcuts") == {}
    assert settings.get("theme") == "light"
    assert config.get("app.theme") == "system"
    assert "mode = light" in legacy.read_text(encoding="utf-8")


def test_failed_reset_rolls_back_every_mutated_file(tmp_path, monkeypatch):
    service, settings, config, _stores, legacy = _service(tmp_path)
    original_json = settings.config_file.read_bytes()
    original_yaml = config.config_file.read_bytes()
    original_legacy = legacy.read_bytes()

    def fail_yaml(_selected):
        raise OSError("simulated YAML failure")

    monkeypatch.setattr(service, "_apply_yaml", fail_yaml)
    with pytest.raises(SettingsResetError, match="previous settings were restored"):
        service.reset(["appearance"])

    assert settings.config_file.read_bytes() == original_json
    assert yaml.safe_load(config.config_file.read_text(encoding="utf-8")) == yaml.safe_load(original_yaml)
    assert legacy.read_bytes() == original_legacy
    assert settings.get("theme") == "light"
    assert config.get("app.theme") == "system"


def test_invalid_or_empty_category_is_rejected_before_backup(tmp_path):
    service, *_ = _service(tmp_path)

    with pytest.raises(ValueError):
        service.reset([])
    with pytest.raises(ValueError):
        service.reset(["credentials"])

    assert not service.backup_dir.exists()


def test_config_defaults_match_documented_appearance(tmp_path):
    config = ConfigManager(str(tmp_path / "new-config.yaml"))

    assert config.get("app.theme") == "dark"
    assert config.get("app.window_opacity") == 96
