"""FE-PAR-03: exact targets, cache isolation and real-thread UI integration."""

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QFileDialog, QMessageBox, QAbstractItemView

import src.core.file_explorer_executor as core
from src.core.file_list_executor import FileListExecutor
from src.gui.panels.results_tree import ITEM_TYPE_ROLE, ITEM_TYPE_ROOT
from test_file_explorer_lifecycle import docks, pause_at_first_checkpoint
from test_file_explorer_replace import populate_dock, select_tree_file


def execute(executor, operation, directory, **kwargs):
    if operation == "search":
        return executor.execute_search(directory, content_query="needle", **kwargs)
    return executor.execute_browse(directory, **kwargs)


def paths(result):
    return [item.file_info.path for item in result["files"]]


@pytest.mark.parametrize("operation", ["browse", "search"])
@pytest.mark.parametrize("recursive", [False, True])
def test_single_file_never_discovers_siblings(operation, recursive, tmp_path, monkeypatch):
    target = tmp_path / ".env"
    sibling = tmp_path / "sibling.txt"
    target.write_text("needle")
    sibling.write_text("needle")

    def forbidden(*_a, **_kw):
        pytest.fail("Explicit file scope attempted folder discovery")

    monkeypatch.setattr(FileListExecutor, "list_files", forbidden)
    result = execute(core.UnifiedFileExplorerExecutor(), operation, str(target),
                     target_scope="file", recursive=recursive, show_hidden=False)
    assert paths(result) == [str(target)]


@pytest.mark.parametrize("operation", ["browse", "search"])
def test_selected_targets_cross_folders_without_expansion(operation, tmp_path, monkeypatch):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    chosen = [first / "chosen.txt", second / ".env"]
    for path in chosen + [first / "sibling.txt", second / "sibling.txt"]:
        path.write_text("needle")
    monkeypatch.setattr(FileListExecutor, "list_files", lambda *_a, **_kw: pytest.fail("Folder traversal"))
    result = execute(core.UnifiedFileExplorerExecutor(), operation, str(first), target_scope="selected",
                     target_paths=[str(chosen[1]), str(chosen[0]), str(chosen[1])], recursive=True)
    assert paths(result) == [str(chosen[1]), str(chosen[0])]
    assert not result["stats"]["errors"]


@pytest.mark.parametrize("operation", ["browse", "search"])
def test_selected_directory_does_not_expand_to_descendants(operation, tmp_path, monkeypatch):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "child.txt").write_text("needle")
    monkeypatch.setattr(FileListExecutor, "list_files", lambda *_a, **_kw: pytest.fail("Descendant traversal"))
    result = execute(core.UnifiedFileExplorerExecutor(), operation, "", target_scope="selected",
                     target_paths=[str(folder)], recursive=True)
    assert paths(result) == ([str(folder)] if operation == "browse" else [])


@pytest.mark.parametrize("scope", ["file", "selected"])
@pytest.mark.parametrize("operation", ["browse", "search"])
def test_incremental_candidates_can_only_narrow_explicit_target(scope, operation, tmp_path):
    target, sibling = tmp_path / "target.txt", tmp_path / "sibling.txt"
    target.write_text("needle")
    sibling.write_text("needle")
    request = dict(target_scope=scope, filters={"candidate_paths": [str(sibling), str(target)]})
    if scope == "selected":
        request["target_paths"] = [str(target)]
    result = execute(core.UnifiedFileExplorerExecutor(), operation, str(target), **request)
    assert paths(result) == [str(target)]
    request["filters"]["candidate_paths"] = []
    assert paths(execute(core.UnifiedFileExplorerExecutor(), operation, str(target), **request)) == []


@pytest.mark.parametrize("scope", ["file", "selected"])
@pytest.mark.parametrize("filters", [{"include_globs": ["*.md"]}, {"exclude_globs": ["*.txt"]},
                                     {"type": "dirs"}, {"size": {"min": 1000}}])
def test_explicit_scope_still_respects_filters(scope, filters, tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("needle")
    kwargs = dict(target_scope=scope, filters=filters)
    if scope == "selected":
        kwargs["target_paths"] = [str(target)]
    result = core.UnifiedFileExplorerExecutor().execute_browse(str(target), **kwargs)
    assert result["files"] == [] and not result["stats"]["errors"]


@pytest.mark.parametrize("operation", ["browse", "search"])
def test_explicit_scope_keeps_content_conditions(operation, tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("needle")
    condition = [{"field": "content", "operator": "contains", "value": "missing"}]
    result = execute(core.UnifiedFileExplorerExecutor(), operation, str(target),
                     target_scope="file", conditions=condition)
    assert result["files"] == []


@pytest.mark.parametrize("scope,target_paths", [("unknown", None), ("folder", []), ("file", []),
                                              ("selected", []), ("selected", "not-a-list"),
                                              ("selected", [""]), ("selected", ["bad\x00path"])])
def test_invalid_or_ambiguous_scopes_fail_closed(scope, target_paths, tmp_path, monkeypatch):
    monkeypatch.setattr(FileListExecutor, "list_files", lambda *_a, **_kw: pytest.fail("Invalid target scan"))
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query="needle", target_scope=scope, target_paths=target_paths,
    )
    assert result["files"] == [] and result["stats"]["errors"]


@pytest.mark.parametrize("limit", ["count", "path", "total"])
def test_target_bounds_reject_before_metadata_reads(limit, tmp_path, monkeypatch):
    target = str(tmp_path / "target.txt")
    supplied = [target]
    if limit == "count":
        supplied = [target] * (core.MAX_TARGET_PATHS + 1)
    elif limit == "path":
        monkeypatch.setattr(core, "MAX_TARGET_PATH_BYTES", 5)
    else:
        monkeypatch.setattr(core, "MAX_TARGET_TOTAL_BYTES", 5)
    monkeypatch.setattr(FileListExecutor, "_get_file_info", lambda *_a: pytest.fail("Unbounded metadata work"))
    result = core.UnifiedFileExplorerExecutor().execute_browse(
        "", target_scope="selected", target_paths=supplied,
    )
    assert not result["files"] and result["stats"]["errors"]


def test_selected_stale_paths_have_bounded_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "MAX_OPERATION_ERRORS", 2)
    result = core.UnifiedFileExplorerExecutor().execute_search(
        "", content_query="needle", target_scope="selected",
        target_paths=[str(tmp_path / str(index)) for index in range(10)],
    )
    assert not result["files"]
    assert len(result["stats"]["errors"]) == 2
    assert "remaining targets were not processed" in result["stats"]["errors"][-1]


def test_file_scope_rejects_directory_and_missing_file(tmp_path):
    executor = core.UnifiedFileExplorerExecutor()
    for target in (tmp_path, tmp_path / "missing"):
        result = executor.execute_browse(str(target), target_scope="file")
        assert not result["files"] and result["stats"]["errors"]


def test_file_target_preserves_binary_content_scope(tmp_path):
    target = tmp_path / "data.bin"
    target.write_bytes(b"\x00needle\x00")
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(target), content_query="needle", target_scope="file", search_options={"content_scope": "binary"},
    )
    assert paths(result) == [str(target)] and result["stats"]["binary_files_searched"] == 1


def set_scope(dock, scope):
    dock.combo_target_scope.setCurrentIndex(dock.combo_target_scope.findData(scope))


def select_paths(dock, view, chosen):
    dock.results_stack.setCurrentIndex(view)
    if view == 0:
        for path in chosen:
            select_tree_file(dock.results_tree, path)
    else:
        table = dock.table_manager.table
        for row in range(table.rowCount()):
            if table.item(row, 4).text() in {str(path) for path in chosen}:
                table.item(row, 4).setSelected(True)


@pytest.mark.parametrize("scope", ["folder", "file", "selected"])
def test_scope_controls_are_stable_and_retranslation_preserves_data(scope, tmp_path, docks):
    dock = docks()
    set_scope(dock, scope)
    assert dock.ed_directory.isEnabled() == (scope != "selected")
    assert dock.chk_recursive.isEnabled() == (scope == "folder")
    assert dock.chk_all.isEnabled() == (scope == "folder")
    assert dock.btn_recent.isEnabled() == (scope == "folder")
    assert dock.btn_browse.isEnabled() == (scope != "selected")
    assert dock.ed_directory.maxLength() == core.MAX_TARGET_PATH_BYTES
    dock.retranslateUi()
    assert dock.combo_target_scope.currentData() == scope
    if scope == "selected":
        assert dock.table_manager.table.selectionMode() == QAbstractItemView.ExtendedSelection


def test_file_picker_and_cancellation_keep_scope_and_path(tmp_path, docks, monkeypatch):
    dock = docks()
    target = tmp_path / "target.txt"
    target.write_text("needle")
    set_scope(dock, "file")
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_a: pytest.fail("Folder dialog in File mode"))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a: (str(target), ""))
    dock._browse_directory()
    assert dock.ed_directory.text() == str(target)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a: ("", ""))
    dock._browse_directory()
    assert dock.ed_directory.text() == str(target) and dock.combo_target_scope.currentData() == "file"
    set_scope(dock, "selected")
    dock._browse_directory()
    assert dock.ed_directory.text() == str(target)


@pytest.mark.parametrize("scope", ["file", "selected"])
@pytest.mark.parametrize("view", [0, 1])
@pytest.mark.parametrize("operation", ["browse", "search"])
def test_real_dock_operation_uses_snapshot_only(scope, view, operation, tmp_path, docks, qtbot, qapp, monkeypatch):
    first, second, ignored = [tmp_path / name for name in ("a.txt", "b.txt", "ignored.txt")]
    for target in (first, second, ignored):
        target.write_text("needle")
    dock = docks()
    populate_dock(dock, [first, second, ignored])
    set_scope(dock, scope)
    select_paths(dock, view, [second])
    dock.ed_directory.setText(str(first) if scope == "file" else "/invalid/unused/folder")
    dock.ed_exc.clear()
    dock.chk_recursive.setChecked(True)
    dock.content_panel.set_query("needle" if operation == "search" else "")
    dock._user_manually_changed_view = True
    captures = []
    original = getattr(dock.executor, f"execute_{operation}")

    def capture(**kwargs):
        captures.append((QThread.currentThread() != qapp.thread(), kwargs.copy()))
        return original(**kwargs)

    monkeypatch.setattr(dock.executor, f"execute_{operation}", capture)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    expected = first if scope == "file" else second
    if operation == "browse":
        assert [item["path"] for item in dock.last_browse_results] == [str(expected)]
    else:
        assert list(dock.last_search_results) == [str(expected)]
    assert captures[0][0] and captures[0][1]["target_scope"] == scope
    assert captures[0][1]["recursive"] is False
    if scope == "selected":
        assert captures[0][1]["target_paths"] == [str(second)]


@pytest.mark.parametrize("view", [0, 1])
def test_empty_selected_scope_never_falls_back_to_all_results(view, tmp_path, docks, monkeypatch):
    target = tmp_path / "target.txt"
    target.write_text("needle")
    dock = docks()
    populate_dock(dock, [target])
    set_scope(dock, "selected")
    dock.results_stack.setCurrentIndex(view)
    dock._list_files()
    assert not dock._operation_running()
    assert not getattr(dock, "_current_browse_params", None)


def test_tree_summary_root_and_match_selection_are_not_expanded(tmp_path, docks):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    for path in (first, second):
        path.write_text("needle")
    dock = docks()
    populate_dock(dock, [first, second])
    set_scope(dock, "selected")
    dock.results_stack.setCurrentIndex(0)
    tree = dock.results_tree
    for index in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(index)
        if item.data(0, ITEM_TYPE_ROLE) == ITEM_TYPE_ROOT:
            item.setSelected(True)
    assert dock._selected_result_paths() == []
    select_tree_file(tree, first)
    assert dock._snapshot_target()[3] == [str(first)]


@pytest.mark.parametrize("change", ["scope", "path", "recursive", "hidden", "selection", "view", "content_scope"])
def test_target_changes_invalidate_incremental_cache(change, tmp_path, docks):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    for path in (first, second):
        path.write_text("needle")
    dock = docks()
    populate_dock(dock, [first, second])
    dock.ed_directory.setText(str(tmp_path))
    if change in {"selection", "view"}:
        set_scope(dock, "selected")
        select_paths(dock, 1, [first])
    signature = dock._snapshot_target()[-1]
    dock._last_content_search_universe = dict(directory=str(tmp_path), content_query="needle",
                                           paths=[str(first)], target_signature=signature)
    if change == "scope":
        set_scope(dock, "file")
    elif change == "path":
        dock.ed_directory.setText(str(tmp_path / "other"))
    elif change == "recursive":
        dock.chk_recursive.toggle()
    elif change == "hidden":
        dock.chk_all.toggle()
    elif change == "selection":
        dock.table_manager.table.clearSelection()
    elif change == "view":
        dock.results_stack.setCurrentIndex(0)
    else:
        dock.search_options_panel.set_options({"content_scope": "binary"})
    assert dock._last_content_search_universe is None


def test_signature_prevents_reuse_across_files_in_same_parent(tmp_path, docks, qtbot):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    for path in (first, second):
        path.write_text("needle")
    dock = docks()
    dock.chk_reuse_previous.setChecked(True)
    set_scope(dock, "file")
    dock.ed_directory.setText(str(first))
    dock.content_panel.set_query("needle")
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    first_signature = dock._snapshot_target()[-1]
    assert dock._get_incremental_candidate_paths(str(tmp_path), "needle", first_signature) == [str(first)]
    dock.ed_directory.setText(str(second))
    assert dock._get_incremental_candidate_paths(str(tmp_path), "needle", dock._snapshot_target()[-1]) is None
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(second)]


def test_target_change_while_paused_cannot_restore_stale_cache(tmp_path, docks, qtbot, monkeypatch):
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    for path in (first, second):
        path.write_text("needle")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(first))
    dock.content_panel.set_query("needle")
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    dock._list_files()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    dock.ed_directory.setText(str(second))
    dock._worker.resume()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(first)]
    assert dock._last_content_search_universe is None


def test_file_revision_change_invalidates_empty_incremental_universe(tmp_path, docks, qtbot):
    target = tmp_path / "target.txt"
    target.write_text("missing")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert dock._last_content_search_universe["paths"] == []
    target.write_text("needle now")
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(target)]


def test_content_scope_change_cannot_reuse_empty_file_universe(tmp_path, docks, qtbot):
    target = tmp_path / "data.bin"
    target.write_bytes(b"\x00needle\x00")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")
    dock.search_options_panel.set_options({"content_scope": "text"})
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert dock._last_content_search_universe["paths"] == []
    dock.search_options_panel.set_options({"content_scope": "binary"})
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(target)]


@pytest.mark.parametrize("size", [(640, 480), (1200, 750)])
def test_scope_controls_fit_resized_panel(size, tmp_path, docks, qtbot):
    target = tmp_path / "target.txt"
    target.write_text("needle")
    dock = docks()
    populate_dock(dock, [target])
    set_scope(dock, "selected")
    select_paths(dock, 1, [target])
    dock.parentWidget().resize(*size)
    qtbot.wait(30)
    combo = dock.combo_target_scope
    label = dock.lbl_target_scope
    count = dock.lbl_target_count
    assert combo.isVisible() and count.isVisible()
    assert combo.parentWidget().rect().contains(combo.geometry())
    assert not combo.geometry().intersects(label.geometry())
    assert not combo.geometry().intersects(count.geometry())
    assert count.fontMetrics().horizontalAdvance(count.text()) <= count.width()
    assert combo.fontMetrics().horizontalAdvance(combo.currentText()) + 24 <= combo.width()
    viewport = dock._controls_scroll.viewport()
    position = viewport.mapFromGlobal(combo.mapToGlobal(combo.rect().topLeft()))
    assert viewport.rect().contains(combo.rect().translated(position))
    count_position = viewport.mapFromGlobal(count.mapToGlobal(count.rect().topLeft()))
    assert count_position.x() + count.fontMetrics().horizontalAdvance(count.text()) <= viewport.width()


@pytest.mark.parametrize("approved", [True, False])
def test_explicit_file_replacement_ignores_sibling_selection_and_requires_confirmation(
    approved, tmp_path, docks, qtbot, qapp, monkeypatch,
):
    target, sibling = tmp_path / "target.txt", tmp_path / "sibling.txt"
    target.write_text("needle")
    sibling.write_text("needle")
    dock = docks()
    populate_dock(dock, [target, sibling])
    set_scope(dock, "file")
    select_paths(dock, 1, [sibling])
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")
    dock.replace_panel.set_replacement("changed")
    questions = []
    threads = []
    original = dock.executor.execute_replace

    def replace(**request):
        threads.append(QThread.currentThread() != qapp.thread())
        return original(**request)

    monkeypatch.setattr(dock.executor, "execute_replace", replace)

    def confirm(*args):
        questions.append(args[2])
        return QMessageBox.Yes if approved else QMessageBox.No

    monkeypatch.setattr(QMessageBox, "question", confirm)
    dock._start_replace(True)
    if approved:
        qtbot.waitUntil(lambda: bool(threads), timeout=5000)
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=5000)
    assert questions and str(target) in questions[0] and str(sibling) not in questions[0]
    assert len(questions) == (2 if approved else 1)
    assert target.read_text() == ("changed" if approved else "needle")
    assert sibling.read_text() == "needle"
    assert threads == ([True] if approved else [])


@pytest.mark.parametrize("operation", ["browse", "search", "replace"])
def test_whitespace_in_explicit_filename_is_never_trimmed(operation, tmp_path, docks, qtbot, monkeypatch):
    target = tmp_path / "name.txt "
    sibling = tmp_path / "name.txt"
    target.write_text("needle")
    sibling.write_text("needle")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle" if operation != "browse" else "")
    if operation == "replace":
        dock.replace_panel.set_replacement("changed")
        monkeypatch.setattr(QMessageBox, "question", lambda *_a: QMessageBox.Yes)
        dock._start_replace(True)
    else:
        dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    if operation == "browse":
        assert [item["path"] for item in dock.last_browse_results] == [str(target)]
    elif operation == "search":
        assert list(dock.last_search_results) == [str(target)]
    else:
        assert target.read_text() == "changed"
    assert sibling.read_text() == "needle"


def test_folder_replacement_never_expands_to_outside_selection(
    tmp_path, docks, qtbot, monkeypatch,
):
    folder = tmp_path / "folder"
    folder.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("needle")
    dock = docks()
    populate_dock(dock, [outside])
    select_paths(dock, 1, [outside])
    dock.ed_directory.setText(str(folder))
    dock.content_panel.set_query("needle")
    monkeypatch.setattr(QMessageBox, "question", lambda *_a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *_a: QMessageBox.Ok)
    dock._start_replace(True)
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=5000)
    assert outside.read_text() == "needle"
