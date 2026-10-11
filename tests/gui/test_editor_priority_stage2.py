"""Focused regressions for recent paths and typed-path opening."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial
import re

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QMainWindow, QTabWidget

from src.gui import editor_dock as module


@pytest.fixture
def editor_factory(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widgets = []

    def create():
        window = QMainWindow()
        tabs = QTabWidget(window)
        window.setCentralWidget(tabs)
        dock = module.EditorDock(window)
        tabs.addTab(dock, "Clarify Editor")
        qtbot.addWidget(window)
        widgets.append(window)
        return dock

    return create


def test_file_menu_exposes_typed_path_and_separate_recent_menus(editor_factory):
    dock = editor_factory()

    assert dock.action_open_path.menu() is None
    assert dock.menu_recent_files.parent() is dock.menu_file
    assert dock.menu_recent_folders.parent() is dock.menu_file
    assert dock.menu_recent_files.title() == module.tr("editor.menu_recent_files")
    assert dock.menu_recent_folders.title() == module.tr("editor.menu_recent_folders")


def test_recent_files_and_folders_persist_deduplicated_and_bounded(editor_factory, tmp_path):
    dock = editor_factory()
    folder = tmp_path / "folder"
    folder.mkdir()
    files = []
    for index in range(dock.max_recent + 2):
        path = folder / f"note-{index}.txt"
        path.write_text(str(index), encoding="utf-8")
        files.append(path)
        dock._add_recent_file(str(path))
    dock._add_recent_file(str(files[-1]))
    dock._add_recent_folder(str(folder))
    dock._add_recent_folder(str(folder))

    restored = editor_factory()

    assert restored.recent_files == [str(path) for path in reversed(files[-10:])]
    assert restored.recent_folders == [str(folder)]


def test_recent_menu_prunes_stale_paths_and_clear_is_independent(editor_factory, tmp_path):
    dock = editor_factory()
    folder = tmp_path / "folder"
    folder.mkdir()
    file_path = folder / "note.txt"
    file_path.write_text("content", encoding="utf-8")
    dock._add_recent_file(str(file_path))
    dock._add_recent_folder(str(folder))
    file_path.unlink()

    dock._refresh_recent_menus()
    assert dock.recent_files == []
    assert dock.recent_folders == [str(folder)]

    dock._clear_recent_folders()
    assert dock.recent_folders == []


@pytest.mark.parametrize("relative", ["folder/file with spaces.txt", "folder/unicodé.txt"])
def test_typed_path_resolves_relative_to_explorer_root(editor_factory, tmp_path, relative):
    dock = editor_factory()
    target = tmp_path / relative
    target.parent.mkdir(exist_ok=True)
    target.write_text("content", encoding="utf-8")

    assert dock._resolve_typed_file_path(relative) == str(target)
    assert dock._resolve_typed_file_path(str(target)) == str(target)


def test_typed_path_expands_home(editor_factory, tmp_path, monkeypatch):
    dock = editor_factory()
    target = tmp_path / "home-note.txt"
    target.write_text("content", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))

    assert dock._resolve_typed_file_path("~/home-note.txt") == str(target)


@pytest.mark.parametrize(
    ("value", "error_key"),
    [
        ("", "editor.open_path_empty"),
        ("missing.txt", "editor.open_path_missing"),
        ("folder", "editor.open_path_directory"),
    ],
)
def test_typed_path_validation_reports_specific_failures(editor_factory, tmp_path, value, error_key):
    dock = editor_factory()
    (tmp_path / "folder").mkdir()

    with pytest.raises(ValueError, match=module.tr(error_key).split(":")[0]):
        dock._resolve_typed_file_path(value)


def test_open_by_path_reuses_public_api_and_recent_history(editor_factory, tmp_path, monkeypatch):
    dock = editor_factory()
    target = tmp_path / "note.txt"
    target.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(
        module.QInputDialog,
        "getText",
        lambda *args, **kwargs: (str(target), True),
    )

    assert dock._open_file_by_path() is True
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget().file_path == str(target)
    assert dock.recent_files == [str(target)]

    assert dock._open_file_by_path() is True
    assert dock.tab_widget.count() == 1


def test_typed_path_rejects_symlink_and_oversized_input(editor_factory, tmp_path):
    dock = editor_factory()
    target = tmp_path / "target.txt"
    target.write_text("content", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    with pytest.raises(ValueError, match=module.tr("editor.open_path_symlink")):
        dock._resolve_typed_file_path(str(link))
    with pytest.raises(ValueError, match=module.tr("editor.open_path_too_long")):
        dock._resolve_typed_file_path("a" * (dock.MAX_TYPED_PATH_CHARS + 1))

    large = tmp_path / "large.txt"
    with large.open("wb") as stream:
        stream.seek(dock.MAX_TYPED_FILE_BYTES)
        stream.write(b"x")
    expected = module.tr("editor.open_path_too_large").format(limit=dock.MAX_TYPED_FILE_BYTES // (1024 * 1024))
    with pytest.raises(ValueError, match=re.escape(expected)):
        dock._resolve_typed_file_path(str(large))
