"""Qt integration for rename-aware Clarify Editor reference updates."""

from functools import partial

import pytest
from PySide6 import QtCore

from src.gui import editor_dock as module


@pytest.fixture
def rename_dock(qtbot, tmp_path, monkeypatch):
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
    monkeypatch.setattr(dock, "_confirm_reference_update_plan", lambda plan: True)
    monkeypatch.setattr(
        dock, "_report_reference_update_plan", lambda *args, **kwargs: None
    )
    return dock


def test_rename_previews_and_applies_python_import_updates(rename_dock, tmp_path, monkeypatch):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("from old import VALUE\n", encoding="utf-8")
    previews = []
    monkeypatch.setattr(
        rename_dock,
        "_confirm_reference_update_plan",
        lambda plan: previews.append(plan.preview()) or True,
    )

    assert rename_dock._rename_explorer_path(str(source), "new.py")

    assert previews and "from old import VALUE" in previews[0]
    assert consumer.read_text(encoding="utf-8") == "from new import VALUE\n"
    assert rename_dock._last_reference_update is not None


def test_declined_preview_leaves_references_unchanged(rename_dock, tmp_path, monkeypatch):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    monkeypatch.setattr(rename_dock, "_confirm_reference_update_plan", lambda plan: False)

    assert rename_dock._rename_explorer_path(str(source), "new.py")

    assert consumer.read_text(encoding="utf-8") == "import old\n"
    assert rename_dock._last_reference_update is None


def test_modified_open_tab_is_never_overwritten(rename_dock, tmp_path):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    assert rename_dock.open_file_path(str(consumer))
    tab = rename_dock.tab_widget.currentWidget()
    tab.editor.moveCursor(module.QTextCursor.End)
    tab.editor.insertPlainText("unsaved = True")

    assert rename_dock._rename_explorer_path(str(source), "new.py")

    assert consumer.read_text(encoding="utf-8") == "import old\n"
    assert "unsaved = True" in tab.editor.toPlainText()


def test_clean_open_consumer_is_reloaded_and_watcher_baseline_is_refreshed(
    rename_dock, tmp_path
):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    assert rename_dock.open_file_path(str(consumer))
    tab = rename_dock.tab_widget.currentWidget()

    assert rename_dock._rename_explorer_path(str(source), "new.py")

    assert tab.editor.toPlainText() == "import new\n"
    assert not tab.is_modified
    assert not tab.editor.document().isModified()
    assert tab._clarify_disk_path == str(consumer)
    assert str(consumer) in rename_dock._watched_file_paths


def test_undo_last_reference_update_is_conflict_aware(rename_dock, tmp_path, monkeypatch):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    assert rename_dock._rename_explorer_path(str(source), "new.py")
    monkeypatch.setattr(module.QMessageBox, "question", lambda *args, **kwargs: module.QMessageBox.Yes)

    assert rename_dock._undo_last_reference_update()

    assert consumer.read_text(encoding="utf-8") == "import old\n"
    assert rename_dock._last_reference_update is None


def test_folder_rename_refreshes_saved_session_paths(rename_dock, tmp_path):
    folder = tmp_path / "oldpkg"
    folder.mkdir()
    source = folder / "module.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    assert rename_dock.open_file_path(str(source))

    assert rename_dock._rename_explorer_path(str(folder), "newpkg")

    session = rename_dock._session_for_root(str(tmp_path))
    assert session is not None
    assert session["files"] == [str(tmp_path / "newpkg" / "module.py")]


def test_rename_checkpoints_dirty_recovery_under_new_path(rename_dock, tmp_path):
    source = tmp_path / "old.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    assert rename_dock.open_file_path(str(source))
    tab = rename_dock.tab_widget.currentWidget()
    tab.editor.moveCursor(module.QTextCursor.End)
    tab.editor.insertPlainText("unsaved = True\n")

    assert rename_dock._rename_explorer_path(str(source), "new.py")

    snapshots = rename_dock.recovery_store.list()
    assert len(snapshots) == 1
    assert snapshots[0].file_path == str(tmp_path / "new.py")
    assert "unsaved = True" in snapshots[0].content

