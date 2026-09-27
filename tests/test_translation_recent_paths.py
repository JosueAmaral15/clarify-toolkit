"""Focused tests for recent paths shared by translation tools."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.gui.google_translate_dock import GoogleTranslateDock
from src.gui.json_translate_dock import JsonTranslateDock
from src.translation.recent_paths import (
    TranslationRecentPaths,
    record_translation_operation,
)


class FakeSettings:
    """Small QSettings-compatible store for isolated tests."""

    def __init__(self) -> None:
        self.values = {}

    def value(self, key, default=None, **_kwargs):
        return self.values.get(key, default)

    def setValue(self, key, value) -> None:
        self.values[key] = value


def test_recent_paths_are_separate_deduplicated_and_bounded(tmp_path):
    settings = FakeSettings()
    recent = TranslationRecentPaths(settings)
    sources = []
    for index in range(12):
        path = tmp_path / f"source-{index}.txt"
        path.write_text(str(index), encoding="utf-8")
        sources.append(str(path))
        recent.add("source", str(path))

    dictionary = tmp_path / "dictionary.json"
    dictionary.write_text("{}", encoding="utf-8")
    recent.add("dictionary", str(dictionary))
    recent.add("source", sources[-2])

    assert recent.get("source")[0] == sources[-2]
    assert len(recent.get("source")) == 10
    assert recent.get("dictionary") == [str(dictionary)]


def test_recent_paths_prune_missing_entries_and_clear(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.write_text("text", encoding="utf-8")
    settings = FakeSettings()
    settings.values["recent_source_paths"] = [str(tmp_path / "missing.txt"), str(existing)]
    recent = TranslationRecentPaths(settings)

    assert recent.get("source") == [str(existing)]
    assert settings.values["recent_source_paths"] == [str(existing)]

    recent.clear("source")
    assert recent.get("source") == []
    with pytest.raises(ValueError):
        recent.get("unknown")


def test_translation_history_records_metadata_in_both_histories():
    owner = Mock()
    owner.parentWidget.return_value.dock_history = Mock()
    persistent_history = Mock()
    details = {"source_path": "/tmp/source.txt", "files_processed": 1}

    with patch("src.gui.progress.OperationHistory", return_value=persistent_history):
        record_translation_operation(owner, "google_translate", "Google Translate", details)

    persistent_history.add_operation.assert_called_once_with("google_translate", details)
    owner.parentWidget.return_value.dock_history.add_operation.assert_called_once_with(
        "Google Translate", details
    )


def test_json_translate_selects_recent_sources_and_dictionaries(qapp, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("Hello", encoding="utf-8")
    dictionary = tmp_path / "dictionary.json"
    dictionary.write_text('{"hello": "Hello"}', encoding="utf-8")
    dock = JsonTranslateDock()
    dock.recent_paths = TranslationRecentPaths(FakeSettings())

    dock._select_recent_path("source", str(source))
    dock._select_recent_path("dictionary", str(dictionary))

    assert dock.ed_path.text() == str(source)
    assert dock.is_file.isChecked()
    assert dock.ed_dict.text() == str(dictionary)
    assert dock.btn_recent_path.toolTip()
    assert dock.btn_recent_dict.toolTip()
    assert dock.btn_recent_path.accessibleName()
    assert dock.btn_recent_dict.accessibleName()
    dock.deleteLater()


def test_json_translate_directory_browser_keeps_selection(qapp, tmp_path):
    dock = JsonTranslateDock()
    dock.recent_paths = TranslationRecentPaths(FakeSettings())
    dock.is_file.setChecked(False)

    with patch(
        "src.gui.json_translate_dock.QFileDialog.getExistingDirectory",
        return_value=str(tmp_path),
    ):
        dock._browse_root()

    assert dock.ed_path.text() == str(tmp_path)
    assert dock.recent_paths.get("source") == [str(tmp_path)]
    dock.deleteLater()


def test_google_translate_populates_and_selects_recent_file(qapp, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("Hello", encoding="utf-8")
    settings = FakeSettings()
    recent = TranslationRecentPaths(settings)
    recent.add("source", str(tmp_path))
    recent.add("source", str(source))
    dock = GoogleTranslateDock()
    dock.recent_paths = recent

    dock._refresh_recent_files()
    dock._select_recent_file(str(source))

    assert dock.ed_file_path.itemText(0) == str(source)
    assert dock.ed_file_path.count() == 1
    assert dock.ed_file_path.currentText() == str(source)
    assert dock.btn_recent_file.toolTip()
    assert dock.btn_recent_file.accessibleName()
    dock._clear_recent_files()
    assert recent.get("source") == []
    dock.deleteLater()
