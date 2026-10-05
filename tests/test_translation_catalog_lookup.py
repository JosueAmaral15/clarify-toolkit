"""Mixed catalogue lookup and startup preference regressions."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.gui.initialization_manager import InitializationManager
from src.i18n.translator import Translator
from src.settings_manager import SettingsManager


def test_nested_catalogue_and_explicit_dotted_override():
    flattened = Translator._flatten_translations({
        "dialog": {"title": "nested", "button": {"save": "Save"}},
        "dialog.title": "explicit", "not_text": 3,
    })
    assert flattened == {"dialog.title": "explicit", "dialog.button.save": "Save"}


def test_non_english_startup_always_has_english_fallback(qapp, monkeypatch):
    monkeypatch.setattr(Translator, "_instance", None)
    monkeypatch.setattr(Translator, "_detect_system_locale", lambda self: "pt_BR")
    translator = Translator()
    assert translator.current_language == "pt_BR"
    assert translator._translations["en"]
    translator._translations["en"]["test.only_in_english"] = "fallback"
    assert translator.get("test.only_in_english") == "fallback"
    assert translator.get("test.unknown", "default") == "default"
    assert translator.get("test.unknown") == "test.unknown"
    translator.deleteLater()


@pytest.mark.parametrize("language", ["en", "pt_BR", "es", "fr", "de", "zh", "ja"])
def test_repaired_interface_keys_resolve_in_each_catalogue(language):
    path = Path("src/i18n") / f"{language}.json"
    catalogue = Translator._flatten_translations(json.loads(path.read_text(encoding="utf-8")))
    for key in (
        "plugin_manager.header_enabled", "tutorial_assistant.tooltip_thumbs_up",
        "history_dialog.no_operations", "history_dock.recent",
        "menu.file.new_template", "menu.plugins.manager", "menu.help.view_logs",
        "menu.help.check_updates", "tutorial_assistant.request_failed",
        "tutorial_assistant.waiting", "tutorial_assistant.thinking", "tutorial_assistant.busy",
        "tutorial_assistant.unavailable", "tutorial_assistant.ready", "tutorial_assistant.user",
        "tutorial_assistant.assistant", "tutorial_assistant.feedback_up", "tutorial_assistant.feedback_down",
        "tutorial_assistant.cleared", "tutorial_assistant.feedback_stats", "plugin_manager.counts",
        "plugin_manager.toggle_failed", "plugin_manager.refreshed",
    ):
        assert catalogue[key].strip() and catalogue[key] != key
    assert catalogue["history_dock.recent"].count("{}") == 2
    assert catalogue["tutorial_assistant.feedback_stats"].count("{}") == 2
    assert catalogue["plugin_manager.counts"].count("{}") == 2
    assert catalogue["plugin_manager.toggle_failed"].count("{}") == 1


def test_saved_language_applies_before_window_receives_changes(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(Translator, "_instance", None)
    monkeypatch.setattr(Translator, "_detect_system_locale", lambda self: "en")
    translator = Translator()
    settings = SettingsManager(str(tmp_path / "settings.json"))
    monkeypatch.setattr("src.i18n.translator.get_translator", lambda: translator)
    settings.set("language", "pt_BR")
    monkeypatch.setattr("src.migration_manager.run_migrations", lambda: True)
    monkeypatch.setattr("src.settings_manager.get_settings", lambda: settings)
    window = SimpleNamespace(logger=Mock(), _on_language_changed=Mock())
    InitializationManager.initialize_configuration(window)
    assert window.translator is translator
    assert translator.current_language == "pt_BR"
    window._on_language_changed.assert_not_called()
    translator.switch_language("en")
    window._on_language_changed.assert_called_once_with("en")
    translator.languageChanged.disconnect(window._on_language_changed)
    translator.deleteLater()
