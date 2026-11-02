"""Replacement contracts, resource bounds and active-view integration."""

import os
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox

import src.core.file_explorer_executor as core
from src.core.file_list_executor import FileInfo
from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.panels.file_explorer_worker import FileExplorerWorker
from src.gui.panels.results_tree import ITEM_TYPE_FILE, ITEM_TYPE_ROLE
from src.utils.atomic_files import file_revision, write_existing_text_atomically


def result_for(path):
    return core.SearchResult(FileInfo(path.name, str(path), 0, "", "", "", "", False), [], 0)


@pytest.mark.parametrize("text,query,replacement,options,expected", [
    ("CAT Cat cat cAt", "cat", "dog", {}, "DOG Dog dog dog"),
    ("Cat CAT cat", "cat", "", {}, "  "),
    ("Ab AB ab", r"(a)(b)", r"\2\1", {"regex": True}, "Ba BA ba"),
    ("ab AB", r"(?P<a>a)b", r"\g<a>x", {"regex": True}, "ax AX"),
    ("Cat", "cat", r"C:\Files\new", {}, r"C:\files\new"),
    ("cat cats cat", "cat", "dog", {"whole_word": True}, "dog cats dog"),
    ("a b cat", r"a|cat", "dog", {"regex": True, "whole_word": True}, "dog b dog"),
    ("Cat cat", "cat", "dog", {"case_sensitive": True}, "Cat dog"),
    ("AB", r"(?=A)", "x", {"regex": True}, "xAB"),
])
def test_preserve_case_and_regex(text, query, replacement, options, expected):
    executor = core.UnifiedFileExplorerExecutor()
    changed, count = executor._replace_in_text(text, query, replacement, True, True, options)
    assert changed == expected
    assert count > 0


def test_result_contract_crlf_permissions_and_deduplication(tmp_path):
    target = tmp_path / "file.txt"
    target.write_bytes(b"CAT\r\ncat\r\n")
    target.chmod(0o640)
    item = result_for(target)
    result = core.UnifiedFileExplorerExecutor().execute_replace(
        [item, item], "cat", "dog", preserve_case=True, replace_all=True
    )
    assert result == {"success": True, "cancelled": False, "replaced_count": 2,
                      "replacements_made": 2, "files_modified": 1, "errors": [], "error": ""}
    assert target.read_bytes() == b"DOG\r\ndog\r\n"
    assert target.stat().st_mode & 0o777 == 0o640
    assert not list(tmp_path.glob(".clarify-replace-*"))


@pytest.mark.parametrize("query,replacement,options", [
    ("", "new", {}), ("[", "new", {"regex": True}),
    ("(cat)", r"\2", {"regex": True}), ("cat", "new", {"multi_query": True}),
])
def test_invalid_request_keeps_original(tmp_path, query, replacement, options):
    target = tmp_path / "file.txt"
    target.write_bytes(b"cat")
    result = core.UnifiedFileExplorerExecutor().execute_replace(
        [result_for(target)], query, replacement, search_options=options
    )
    assert not result["success"]
    assert result["errors"]
    assert result["files_modified"] == 0
    assert target.read_bytes() == b"cat"


@pytest.mark.parametrize("bound", ["input", "output", "matches", "files"])
def test_resource_bounds_leave_file_unchanged(tmp_path, monkeypatch, bound):
    target = tmp_path / "file.txt"
    target.write_text("cat cat", encoding="utf-8")
    if bound == "input":
        monkeypatch.setattr(core, "MAX_REPLACE_FILE_BYTES", 3)
    elif bound == "output":
        monkeypatch.setattr(core, "MAX_REPLACE_FILE_BYTES", 10)
    elif bound == "matches":
        monkeypatch.setattr(core, "MAX_REPLACE_MATCHES", 1)
    else:
        monkeypatch.setattr(core, "MAX_REPLACE_FILES", 0)
    result = core.UnifiedFileExplorerExecutor().execute_replace(
        [result_for(target)], "cat", "replacement", replace_all=True
    )
    assert not result["success"]
    assert target.read_text() == "cat cat"


def test_atomic_failure_and_stale_revision_leave_original(tmp_path, monkeypatch):
    target = tmp_path / "file.txt"
    target.write_text("cat")
    revision = file_revision(target.stat())
    monkeypatch.setattr(os, "replace", Mock(side_effect=OSError("write failed")))
    result = core.UnifiedFileExplorerExecutor().execute_replace([result_for(target)], "cat", "dog")
    assert not result["success"]
    assert target.read_text() == "cat"
    assert not list(tmp_path.glob(".clarify-replace-*"))
    target.write_text("offline edit")
    with pytest.raises(ValueError, match="changed"):
        write_existing_text_atomically(str(target), "dog", revision)
    assert target.read_text() == "offline edit"


@pytest.mark.parametrize("field", ["query", "replacement"])
def test_large_request_is_rejected_before_matching(tmp_path, monkeypatch, field):
    path = tmp_path / "file.txt"
    path.write_text("cat")
    monkeypatch.setattr(core, "MAX_REPLACE_FILE_BYTES", 5)
    query, replacement = ("long query", "dog") if field == "query" else ("cat", "long replacement")
    result = core.UnifiedFileExplorerExecutor().execute_replace([result_for(path)], query, replacement)
    assert not result["success"] and path.read_text() == "cat"


def test_error_limit_reports_unprocessed_files(tmp_path, monkeypatch):
    paths = [tmp_path / str(index) for index in range(3)]
    monkeypatch.setattr(core, "MAX_OPERATION_ERRORS", 2)
    result = core.UnifiedFileExplorerExecutor().execute_replace(
        [result_for(path) for path in paths], "cat", "dog"
    )
    assert len(result["errors"]) == 2
    assert "remaining files were not processed" in result["error"]


@pytest.mark.parametrize("link_type", ["symlink", "hardlink"])
def test_links_are_not_overwritten(tmp_path, link_type):
    target = tmp_path / "original.txt"
    target.write_text("cat")
    link = tmp_path / "link.txt"
    if link_type == "symlink":
        link.symlink_to(target)
    else:
        os.link(target, link)
    result = core.UnifiedFileExplorerExecutor().execute_replace([result_for(link)], "cat", "dog")
    assert not result["success"]
    assert target.read_text() == "cat"


def test_atomic_replacement_preserves_extended_metadata(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("cat")
    if not hasattr(os, "setxattr"):
        pytest.skip("Extended attributes unavailable")
    try:
        os.setxattr(target, "user.clarify-test", b"metadata")
    except OSError:
        pytest.skip("Filesystem does not support user extended attributes")
    before = target.stat()
    result = core.UnifiedFileExplorerExecutor().execute_replace([result_for(target)], "cat", "dog")
    assert result["success"]
    assert os.getxattr(target, "user.clarify-test") == b"metadata"
    after = target.stat()
    assert (after.st_uid, after.st_gid) == (before.st_uid, before.st_gid)


def test_cancel_after_first_file_reports_partial_results(tmp_path):
    paths = [tmp_path / "first.txt", tmp_path / "second.txt"]
    for path in paths:
        path.write_text("cat")
    executor = core.UnifiedFileExplorerExecutor()
    executor.progress.connect(lambda message: executor.cancel() if "second.txt" in message else None)
    result = executor.execute_replace([result_for(path) for path in paths], "cat", "dog")
    assert result["cancelled"] and not result["success"]
    assert result["replacements_made"] == result["files_modified"] == 1
    assert [path.read_text() for path in paths] == ["dog", "cat"]


def test_worker_forwards_replacement_contract(qapp, tmp_path):
    executor = core.UnifiedFileExplorerExecutor()
    worker = FileExplorerWorker(executor)
    path = tmp_path / "file.txt"
    path.write_text("CAT CAT")
    results = []
    errors = []
    worker.finished.connect(results.append)
    worker.error.connect(errors.append)
    try:
        worker.execute_replace([result_for(path)], "cat", "dog", {}, True, True)
        assert not errors
        assert results[0]["success"] and results[0]["replacements_made"] == 2
        assert path.read_text() == "DOG DOG"
    finally:
        worker.deleteLater()


def populate_dock(dock, paths):
    dock.table_manager.populate([
        {"name": path.name, "size": 7, "mtime": 0, "permissions": "-rw-r--r--",
         "path": str(path), "is_dir": False} for path in paths
    ])
    dock.results_tree.populate({str(path): [(1, 0, "cat cat")] for path in paths},
                               base_path=str(paths[0].parent))


def select_tree_file(tree, path):
    def visit(item):
        if item.data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_FILE and tree._result_path_for_item(item) == str(path):
            item.setSelected(True)
            return True
        return any(visit(item.child(index)) for index in range(item.childCount()))
    assert any(visit(tree.topLevelItem(index)) for index in range(tree.topLevelItemCount()))


@pytest.mark.parametrize("view", [0, 1])
def test_replacement_uses_active_selection_only(qapp, tmp_path, view):
    paths = [tmp_path / "a.txt", tmp_path / "b.txt"]
    for path in paths:
        path.write_text("cat cat")
    dock = FileExplorerDock()
    try:
        populate_dock(dock, paths)
        dock.results_stack.setCurrentIndex(view)
        dock.table_manager.table.selectRow(0)
        select_tree_file(dock.results_tree, paths[1])
        expected = paths[1] if view == 0 else paths[0]
        assert [item.file_info.path for item in dock._selected_replacement_results()] == [str(expected)]
        if view == 0:
            dock.results_tree.clearSelection()
        else:
            dock.table_manager.table.clearSelection()
        assert dock._selected_replacement_results() == []
    finally:
        dock.deleteLater()


@pytest.mark.parametrize("replace_all", [False, True])
def test_dock_replacement_runs_off_gui_and_preserves_case(qapp, qtbot, tmp_path, monkeypatch, replace_all):
    path = tmp_path / "file.txt"
    path.write_text("CAT CAT")
    dock = FileExplorerDock()
    qtbot.addWidget(dock)
    populate_dock(dock, [path])
    dock.combo_target_scope.setCurrentIndex(
        dock.combo_target_scope.findData("selected")
    )
    dock.results_stack.setCurrentIndex(1)
    dock.table_manager.table.selectRow(0)
    dock.content_panel.set_query("cat")
    dock.replace_panel.set_replacement("dog")
    dock.replace_panel.chk_preserve_case.setChecked(True)
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Ok)
    threads = []
    completions = []
    monkeypatch.setattr(dock, "_on_replace_finished", completions.append)
    original = dock.executor.execute_replace
    def capture(**kwargs):
        threads.append(QThread.currentThread() == qapp.thread())
        return original(**kwargs)
    monkeypatch.setattr(dock.executor, "execute_replace", capture)
    dock._start_replace(replace_all)
    qtbot.waitUntil(lambda: bool(completions), timeout=5000)
    assert threads == [False]
    assert path.read_text() == ("DOG DOG" if replace_all else "DOG CAT")
    assert dock.progress_dialog is None


def test_cancelled_worker_never_starts_replace(qapp):
    executor = core.UnifiedFileExplorerExecutor()
    executor.execute_replace = Mock()
    worker = FileExplorerWorker(executor)
    results = []
    try:
        worker.configure_replace(files=[], search_text="cat", replace_text="dog", search_options={})
        worker.finished.connect(results.append)
        worker.cancel()
        worker.run_replace()
        executor.execute_replace.assert_not_called()
        assert results[0]["cancelled"] and results[0]["files_modified"] == 0
    finally:
        worker.deleteLater()


def test_declined_confirmation_never_starts_worker(qapp, tmp_path, monkeypatch):
    path = tmp_path / "file.txt"
    path.write_text("cat")
    dock = FileExplorerDock()
    try:
        populate_dock(dock, [path])
        dock.combo_target_scope.setCurrentIndex(
            dock.combo_target_scope.findData("selected")
        )
        dock.results_stack.setCurrentIndex(1)
        dock.table_manager.table.selectRow(0)
        dock.content_panel.set_query("cat")
        monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.No)
        dock._start_replace(True)
        assert not dock._operation_running()
        assert path.read_text() == "cat"
    finally:
        dock.deleteLater()
