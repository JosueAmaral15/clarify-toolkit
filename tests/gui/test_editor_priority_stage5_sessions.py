"""Focused regressions for bounded Clarify Editor folder sessions."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

import json
from functools import partial

import pytest
from PySide6 import QtCore

from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root):
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=recovery_root),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock


def test_folder_session_restores_order_active_tab_and_shared_split(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    paths = []
    for name in ("a.txt", "b.txt", "c.txt"):
        path = folder / name
        path.write_text(name, encoding="utf-8")
        paths.append(path)
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    recovery_root = tmp_path / "recovery"
    first = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    for path in paths:
        assert first.open_file_path(str(path))
    first.tab_widget.tabBar().moveTab(2, 0)
    first.tab_widget.setCurrentWidget(first.tab_widget.widget(2))
    split_source = first.tab_widget.widget(1)
    assert first._show_split_view(split_source, QtCore.Qt.Vertical)
    assert first._checkpoint_unsaved_tabs()
    assert first._save_folder_session(str(folder))
    first.close()

    restored = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    actual = [restored.tab_widget.widget(index).file_path for index in range(restored.tab_widget.count())]
    assert actual == [str(paths[2]), str(paths[0]), str(paths[1])]
    assert restored.tab_widget.currentWidget().file_path == str(paths[1])
    assert restored._split_source_tab.file_path == str(paths[0])
    assert restored.split_editor.document() is restored._split_source_tab.editor.document()
    assert restored.editor_workspace_splitter.orientation() == QtCore.Qt.Vertical


def test_dirty_file_restores_from_recovery_without_overwriting_original(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    source = folder / "note.txt"
    source.write_text("original", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    recovery_root = tmp_path / "recovery"
    first = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    assert first.open_file_path(str(source))
    first.tab_widget.currentWidget().editor.setPlainText("unsaved change")
    assert first._checkpoint_unsaved_tabs()
    assert first._save_folder_session(str(folder))
    first.close()

    restored = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    tab = restored.tab_widget.currentWidget()
    assert restored.tab_widget.count() == 1
    assert tab.file_path is None
    assert tab.editor.toPlainText() == "unsaved change"
    assert tab._clarify_folder_source_path == str(source)
    assert source.read_text(encoding="utf-8") == "original"


def test_missing_and_outside_references_are_skipped_without_opening_siblings(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    valid = folder / "valid.txt"
    valid.write_text("valid", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    missing = folder / "missing.txt"
    payload = [
        {
            "root": str(folder),
            "files": [str(valid), str(missing), str(outside)],
            "active": str(outside),
            "split": {"path": str(outside), "orientation": "horizontal"},
        }
    ]
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    settings.setValue("folder_sessions", json.dumps(payload))

    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, tmp_path / "recovery")

    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget().file_path == str(valid)
    assert dock._split_source_tab is None
    assert "skipped 1" in dock.lbl_status.text()


def test_close_folder_aborts_and_preserves_tabs_on_recovery_checkpoint_failure(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, tmp_path / "recovery")
    source = folder / "open.txt"
    source.write_text("open", encoding="utf-8")
    assert dock.open_file_path(str(source))
    monkeypatch.setattr(dock, "_checkpoint_unsaved_tabs", lambda: False)

    assert dock._close_explorer_folder() is False
    assert dock.explorer_root_path == str(folder)
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget().file_path == str(source)
    assert dock.lbl_status.text() == module.tr("editor.status_folder_closed_recovery_failed")


def test_session_toggle_and_clear_preserve_tabs_and_recovery(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    source = folder / "note.txt"
    source.write_text("content", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    recovery_root = tmp_path / "recovery"
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    assert dock.open_file_path(str(source))
    assert dock._checkpoint_unsaved_tabs()
    assert dock._save_folder_session()
    snapshot_paths = sorted(recovery_root.glob("*.json"))

    dock._set_folder_sessions_enabled(False)
    assert settings.value("folder_sessions_enabled", True, type=bool) is False
    assert dock._clear_folder_sessions(confirm=False)
    assert dock.tab_widget.count() == 1
    assert sorted(recovery_root.glob("*.json")) == snapshot_paths
    assert json.loads(settings.value("folder_sessions", "", type=str)) == []


def test_corrupt_or_oversized_session_payload_is_ignored(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    settings.setValue("folder_sessions", "[" + "x" * module.EditorDock.MAX_FOLDER_SESSIONS_BYTES)

    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, tmp_path / "recovery")

    assert dock._folder_sessions == []
    assert dock.tab_widget.count() == 0


def test_folder_switch_isolates_tabs_dirty_recovery_order_active_and_split(qtbot, tmp_path, monkeypatch):
    folder_a = tmp_path / "workspace-a"
    folder_b = tmp_path / "workspace-b"
    folder_a.mkdir()
    folder_b.mkdir()
    paths_a = [folder_a / "a.txt", folder_a / "b.txt"]
    path_b = folder_b / "other.txt"
    for path in (*paths_a, path_b):
        path.write_text(path.stem, encoding="utf-8")

    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder_a))
    recovery_root = tmp_path / "recovery"
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    for path in paths_a:
        assert dock.open_file_path(str(path))

    dock.tab_widget.tabBar().moveTab(1, 0)
    dirty_tab = next(tab for tab in dock._all_tab_objects() if tab.file_path == str(paths_a[0]))
    split_tab = next(tab for tab in dock._all_tab_objects() if tab.file_path == str(paths_a[1]))
    dock.tab_widget.setCurrentWidget(dirty_tab)
    dirty_tab.editor.setPlainText("unsaved-a")
    assert dock._show_split_view(split_tab, QtCore.Qt.Vertical)

    assert dock._close_explorer_folder()
    assert dock.tab_widget.count() == 0
    assert dock._split_source_tab is None
    assert dock._set_explorer_root(str(folder_b))
    assert dock.open_file_path(str(path_b))
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget().file_path == str(path_b)

    assert dock._set_explorer_root(str(folder_a))
    assert [dock._tab_folder_identity(tab) for tab in dock._all_tab_objects()] == [
        str(paths_a[1]),
        str(paths_a[0]),
    ]
    assert dock.tab_widget.currentWidget().editor.toPlainText() == "unsaved-a"
    assert dock._tab_folder_identity(dock.tab_widget.currentWidget()) == str(paths_a[0])
    assert dock._tab_folder_identity(dock._split_source_tab) == str(paths_a[1])
    assert dock.editor_workspace_splitter.orientation() == QtCore.Qt.Vertical
    assert all(
        not dock._path_is_inside_root(dock._tab_folder_identity(tab), folder_b) for tab in dock._all_tab_objects()
    )


def test_folder_switch_does_not_claim_a_file_opened_outside_the_workspace(qtbot, tmp_path, monkeypatch):
    folder_a = tmp_path / "workspace-a"
    folder_b = tmp_path / "workspace-b"
    folder_a.mkdir()
    folder_b.mkdir()
    inside = folder_a / "inside.txt"
    outside = tmp_path / "outside.txt"
    inside.write_text("inside", encoding="utf-8")
    outside.write_text("outside", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder_a))
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, tmp_path / "recovery")
    assert dock.open_file_path(str(inside))
    assert dock.open_file_path(str(outside))
    outside_tab = dock.tab_widget.currentWidget()
    assert dock._tab_folder_root(outside_tab) == ""

    assert dock._close_explorer_folder()
    assert dock._all_tab_objects() == [outside_tab]
    assert dock._set_explorer_root(str(folder_b))
    assert dock._all_tab_objects() == [outside_tab]
    assert dock._tab_folder_root(outside_tab) == ""


@pytest.mark.parametrize(
    "error",
    [
        module.RecoverySnapshotError("synthetic quota failure"),
        OSError("synthetic I/O failure"),
    ],
)
def test_failed_folder_switch_checkpoint_keeps_root_tabs_and_existing_snapshots(qtbot, tmp_path, monkeypatch, error):
    folder_a = tmp_path / "workspace-a"
    folder_b = tmp_path / "workspace-b"
    folder_a.mkdir()
    folder_b.mkdir()
    source = folder_a / "draft.txt"
    source.write_text("original", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder_a))
    recovery_root = tmp_path / "recovery"
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    dock.recovery_store.save("existing", title="keep.txt", content="keep")
    assert dock.open_file_path(str(source))
    dock.tab_widget.currentWidget().editor.setPlainText("unsaved")

    def fail(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(dock.recovery_store, "save", fail)
    assert dock._set_explorer_root(str(folder_b)) is False
    assert dock.explorer_root_path == str(folder_a)
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.currentWidget().editor.toPlainText() == "unsaved"
    assert {item.snapshot_id for item in dock.recovery_store.list()} == {"existing"}
    assert dock.lbl_status.text() == module.tr("editor.status_folder_session_failed")


def test_removed_session_path_is_reported_without_deleting_reference_snapshot(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    source = folder / "removed.txt"
    source.write_text("original", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    recovery_root = tmp_path / "recovery"
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    assert dock.open_file_path(str(source))
    assert dock._close_explorer_folder()
    snapshot_ids = {item.snapshot_id for item in dock.recovery_store.list()}
    source.unlink()

    assert dock._set_explorer_root(str(folder))
    assert dock.tab_widget.count() == 0
    assert "skipped 1" in dock.lbl_status.text()
    assert {item.snapshot_id for item in dock.recovery_store.list()} == snapshot_ids


def test_recovery_list_io_failure_is_reported_without_deleting_snapshots(qtbot, tmp_path, monkeypatch):
    folder = tmp_path / "workspace"
    folder.mkdir()
    source = folder / "saved.txt"
    source.write_text("original", encoding="utf-8")
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(folder))
    recovery_root = tmp_path / "recovery"
    dock = make_dock(qtbot, tmp_path, monkeypatch, settings, recovery_root)
    assert dock.open_file_path(str(source))
    assert dock._close_explorer_folder()
    snapshots = sorted(recovery_root.glob("*.json"))

    def fail():
        raise OSError("synthetic recovery list failure")

    monkeypatch.setattr(dock.recovery_store, "list", fail)
    assert dock._set_explorer_root(str(folder))
    assert dock.tab_widget.count() == 0
    assert dock.lbl_status.text() == module.tr("editor.status_recovery_skipped").format(count=1)
    assert sorted(recovery_root.glob("*.json")) == snapshots
