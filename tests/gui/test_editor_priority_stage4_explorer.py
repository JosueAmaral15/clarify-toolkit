"""Focused regressions for the Clarify Editor Explorer context menu."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial
from types import SimpleNamespace

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QLineEdit, QMessageBox

from src.gui import editor_dock as module


@pytest.fixture
def explorer_dock(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    dock._set_explorer_root(str(tmp_path))
    return dock


def wait_index(qtbot, dock, path):
    qtbot.waitUntil(lambda: dock.explorer_model.index(str(path)).isValid())
    return dock.explorer_model.index(str(path))


def actions_by_id(menu):
    return {action.data(): action for action in menu.actions() if not action.isSeparator()}


def test_context_actions_are_enabled_by_file_or_directory(explorer_dock, qtbot, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    file_path = folder / "note.txt"
    file_path.write_text("note", encoding="utf-8")
    folder_index = wait_index(qtbot, explorer_dock, folder)
    file_index = wait_index(qtbot, explorer_dock, file_path)

    file_actions = actions_by_id(explorer_dock._build_explorer_context_menu(file_index))
    folder_actions = actions_by_id(explorer_dock._build_explorer_context_menu(folder_index))

    assert file_actions["open"].isEnabled()
    assert file_actions["open_side"].isEnabled()
    assert not file_actions["new_file"].isEnabled()
    assert folder_actions["new_file"].isEnabled()
    assert folder_actions["new_folder"].isEnabled()
    assert not folder_actions["open"].isEnabled()
    assert file_actions["copy_absolute"].isEnabled()
    assert file_actions["copy_relative"].isEnabled()


def test_copy_absolute_and_relative_paths(explorer_dock, tmp_path):
    file_path = tmp_path / "folder" / "note.txt"
    file_path.parent.mkdir()
    file_path.write_text("note", encoding="utf-8")

    assert explorer_dock._copy_path(str(file_path))
    assert module.QApplication.clipboard().text() == str(file_path)
    relative = explorer_dock._relative_explorer_path(str(file_path))
    assert relative == "folder/note.txt"
    assert explorer_dock._copy_path(relative)
    assert module.QApplication.clipboard().text() == "folder/note.txt"


def test_create_items_is_exclusive_and_rejects_unsafe_names(explorer_dock, tmp_path):
    file_path = explorer_dock._create_explorer_item(tmp_path, "note.txt", folder=False)
    folder_path = explorer_dock._create_explorer_item(tmp_path, "folder", folder=True)
    assert (tmp_path / "note.txt").read_text(encoding="utf-8") == ""
    assert file_path == str(tmp_path / "note.txt")
    assert folder_path == str(tmp_path / "folder")

    with pytest.raises(FileExistsError):
        explorer_dock._create_explorer_item(tmp_path, "note.txt", folder=False)
    with pytest.raises(ValueError):
        explorer_dock._create_explorer_item(tmp_path, "../escape", folder=False)


def test_rename_updates_open_tab_identity_without_overwrite(explorer_dock, tmp_path, monkeypatch):
    original = tmp_path / "old.txt"
    original.write_text("content", encoding="utf-8")
    collision = tmp_path / "taken.txt"
    collision.write_text("taken", encoding="utf-8")
    assert explorer_dock.open_file_path(str(original))
    tab = explorer_dock.tab_widget.currentWidget()
    monkeypatch.setattr(module.QMessageBox, "warning", lambda *args: QMessageBox.Ok)

    assert explorer_dock._rename_explorer_path(str(original), "new.txt")
    assert tab.file_path == str(tmp_path / "new.txt")
    assert (tmp_path / "new.txt").read_text(encoding="utf-8") == "content"
    assert not explorer_dock._rename_explorer_path(str(tmp_path / "new.txt"), "taken.txt")
    assert collision.read_text(encoding="utf-8") == "taken"


def test_delete_uses_trash_and_never_follows_symlink(explorer_dock, tmp_path, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("keep", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    calls = []
    monkeypatch.setattr(
        module.QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.Yes,
    )
    monkeypatch.setattr(
        module.QFile,
        "moveToTrash",
        lambda path: (calls.append(path) or True, "/trash/link.txt"),
    )

    assert explorer_dock._delete_explorer_path(str(link))
    assert calls == [str(link)]
    assert target.read_text(encoding="utf-8") == "keep"


def test_open_to_side_reuses_tab_and_shared_document(explorer_dock, tmp_path):
    file_path = tmp_path / "note.txt"
    file_path.write_text("content", encoding="utf-8")

    assert explorer_dock._open_explorer_to_side(str(file_path))
    assert explorer_dock.tab_widget.count() == 1
    assert explorer_dock.split_editor.document() is (explorer_dock.tab_widget.currentWidget().editor.document())


def test_analyze_runs_local_preflight_but_not_provider(explorer_dock, tmp_path, monkeypatch):
    file_path = tmp_path / "sample.py"
    file_path.write_text("value = 1\n", encoding="utf-8")
    calls = []
    analysis = SimpleNamespace(
        path_input=QLineEdit(),
        run_preflight=lambda: calls.append("preflight"),
    )

    class Host:
        dock_algorithm_analysis = analysis

        @staticmethod
        def _show_algorithm_analysis():
            calls.append("show")

    monkeypatch.setattr(explorer_dock, "_analysis_host", lambda: Host())

    assert explorer_dock._analyze_explorer_path(str(file_path))
    assert analysis.path_input.text() == str(file_path)
    assert calls == ["show", "preflight"]
