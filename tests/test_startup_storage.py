"""Optional diagnostic/cache writes must not block application startup."""

import logging
from pathlib import Path
from unittest.mock import patch

from src.migration_manager import MigrationManager
from src.settings_manager import SettingsManager
from src.update_checker import UpdateChecker


def test_migration_logging_survives_unwritable_file(tmp_path):
    isolated_logger = logging.Logger("test-migration")
    with patch("src.migration_manager.get_log_file", return_value=tmp_path / "clarify.log"), \
         patch("src.migration_manager.logging.getLogger", return_value=isolated_logger), \
         patch("logging.handlers.RotatingFileHandler", side_effect=PermissionError):
        manager = MigrationManager()
    assert any(isinstance(handler, logging.StreamHandler) for handler in manager.logger.handlers)


def test_settings_location_override_is_persistent(tmp_path, monkeypatch):
    path = tmp_path / "config" / "settings.json"
    monkeypatch.setenv("CLARIFY_SETTINGS_FILE", str(path))
    manager = SettingsManager()
    manager.set("theme", "dark")
    assert SettingsManager().get("theme") == "dark"
    assert manager.config_file == path


def test_update_without_writable_cache_retains_valid_release(monkeypatch, tmp_path):
    monkeypatch.setattr(UpdateChecker, "CACHE_FILE", tmp_path / "missing" / "cache.json")
    with patch.object(Path, "mkdir", side_effect=PermissionError):
        checker = UpdateChecker("2.9.0")
    info = {"version": "2.9.0"}
    monkeypatch.setattr(checker, "_fetch_latest_release", lambda: info)
    assert checker.check_for_updates(force=True) == (False, info)
