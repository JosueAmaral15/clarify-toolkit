"""FE-PAR-04: bounded block matching, diagnostics and real Qt worker flows."""

import threading
import os
import builtins
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMessageBox

import src.core.file_explorer_executor as core
from src.gui.widgets.search_widgets import SearchOptionsPanel
from test_file_explorer_lifecycle import docks
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import set_scope, select_paths


def search(path, query="alpha\nbeta", executor=None, **options):
    return (executor or core.UnifiedFileExplorerExecutor()).execute_search(
        str(path), content_query=query, target_scope="file", search_options={"cross_line": True, **options}
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("query", ["alpha\nbeta", "alpha\r\nbeta"])
def test_literal_block_positions_and_line_normalization(newline, query, tmp_path):
    path = tmp_path / "target.txt"
    path.write_bytes(newline.join(["intro", "xx alpha", "beta", "alpha", "beta"]).encode())
    result = search(path, query)
    matches = result["files"][0].matches
    assert [(match.line, match.col) for match in matches] == [(2, 3), (4, 0)]
    assert "alpha\\nbeta" in matches[0].snippet
    assert all("\n" not in match.snippet and len(match.snippet) <= core.MAX_SNIPPET_LENGTH for match in matches)
    assert not result["stats"]["partial"]
    assert not core.UnifiedFileExplorerExecutor().execute_search(
        str(path), content_query=query, target_scope="file", search_options={}
    )["files"]


@pytest.mark.parametrize("case_sensitive,whole_word,count", [(False, False, 3), (True, False, 2),
                                                          (False, True, 2), (True, True, 1)])
def test_case_and_whole_word_options(case_sensitive, whole_word, count, tmp_path):
    path = tmp_path / "target.txt"
    path.write_text("ALPHA\nBETA\nalpha\nbeta\nxxalpha\nbetaxx")
    result = search(path, case_sensitive=case_sensitive, whole_word=whole_word)
    assert result["stats"]["total_matches"] == count


def test_regex_dot_all_multiline_anchors_and_alternation_boundaries(tmp_path):
    path = tmp_path / "target.txt"
    path.write_text("intro\nalpha\nbeta\nend")
    result = search(path, r"^alpha.*?beta$", regex=True)
    assert [(m.line, m.col) for m in result["files"][0].matches] == [(2, 0)]
    path.write_text("xxalpha beta alpha betaXX")
    result = search(path, "alpha|beta", regex=True, whole_word=True)
    assert [m.col for m in result["files"][0].matches] == [8, 13]


def test_unicode_columns_are_characters_and_snippet_contains_far_match(tmp_path):
    path = tmp_path / "target.txt"
    path.write_text("intro\n" + "\u00e9" * 300 + "alpha\nbeta")
    result = search(path)
    match = result["files"][0].matches[0]
    assert (match.line, match.col) == (2, 300)
    assert "alpha\\nbeta" in match.snippet and len(match.snippet) <= core.MAX_SNIPPET_LENGTH


def test_utf8_sample_boundary_is_not_mistaken_for_binary(tmp_path):
    path = tmp_path / "target.txt"
    path.write_text("x" * (core.TEXT_SAMPLE_BYTES - 1) + "\u00e9\nalpha\nbeta")
    assert core.UnifiedFileExplorerExecutor._classify_content_file(str(path)) == "text"
    assert search(path)["stats"]["total_matches"] == 1


@pytest.mark.parametrize("payload", [b"x\xff", b"x" * (core.TEXT_SAMPLE_BYTES - 1) + b"\xc3"])
def test_incomplete_or_invalid_utf8_sample_is_binary(payload, tmp_path):
    path = tmp_path / "target.bin"
    path.write_bytes(payload)
    assert core.UnifiedFileExplorerExecutor._classify_content_file(str(path)) == "binary"
    assert search(path)["stats"]["errors"]


@pytest.mark.parametrize("query,options", [("", {}), (None, {}), (["alpha"], {}),
                                          ("[", {"regex": True}), ("alpha", {"multi_query": True}),
                                          ("alpha", {"content_scope": "binary"}),
                                          ("alpha", {"content_scope": "both"})])
def test_invalid_configuration_fails_before_discovery(query, options, tmp_path, monkeypatch):
    monkeypatch.setattr(core.FileListExecutor, "list_files", lambda *_a, **_kw: pytest.fail("Unexpected traversal"))
    result = core.UnifiedFileExplorerExecutor().execute_search(
        str(tmp_path), content_query=query, search_options={"cross_line": True, **options}
    )
    assert result["files"] == [] and result["stats"]["errors"] and result["stats"]["partial"]


@pytest.mark.parametrize("query,allowed", [("abcd", True), ("abcde", False), ("\u00e9\u00e9", True),
                                         ("\u00e9\u00e9x", False)])
def test_query_byte_limits(query, allowed, tmp_path, monkeypatch):
    monkeypatch.setattr(core, "MAX_CROSS_LINE_QUERY_BYTES", 4)
    path = tmp_path / "target.txt"
    path.write_text(query)
    result = search(path, query)
    assert bool(result["stats"]["errors"]) != allowed
    assert result["stats"]["total_matches"] == int(allowed)


@pytest.mark.parametrize("size,allowed", [(8, True), (9, False)])
def test_file_byte_limits_never_use_unbounded_reader(size, allowed, tmp_path, monkeypatch):
    monkeypatch.setattr(core, "MAX_CROSS_LINE_FILE_BYTES", 8)
    monkeypatch.setattr(core, "read_text", lambda *_a: pytest.fail("Unbounded read"))
    path = tmp_path / "target.txt"
    path.write_text("a" * size)
    result = search(path, "a")
    assert bool(result["stats"]["errors"]) != allowed
    assert result["stats"]["total_matches"] == (size if allowed else 0)


def test_growth_after_stat_does_not_truncate_or_search_prefix(tmp_path, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("a" * 100)
    monkeypatch.setattr(core, "MAX_CROSS_LINE_FILE_BYTES", 8)
    monkeypatch.setattr(core.os, "fstat", lambda _fd: SimpleNamespace(st_size=0))
    result = search(path, "a")
    assert not result["files"] and "4 MiB limit" in result["stats"]["errors"][0]


def test_cancel_during_bounded_read_closes_file_and_returns_no_prefix(tmp_path, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("a" * 100000)
    executor = core.UnifiedFileExplorerExecutor()
    calls = []
    handles = []

    def capture_open(*args, **kwargs):
        handle = builtins.open(*args, **kwargs)
        handles.append(handle)
        return handle

    monkeypatch.setattr(core, "open", capture_open, raising=False)

    def checkpoint():
        calls.append(1)
        if len(calls) == 2:
            executor.cancel()
        return not executor._cancel

    monkeypatch.setattr(executor, "checkpoint", checkpoint)
    assert executor._read_cross_line_text(str(path)) is None
    assert executor._cancel and len(calls) == 2
    assert len(handles) == 1 and handles[0].closed
    path.unlink()


def test_binary_and_late_nul_are_explicit_errors(tmp_path):
    for index, data in enumerate([b"\x00alpha\nbeta", b"x" * (core.TEXT_SAMPLE_BYTES + 1) + b"\x00alpha\nbeta"]):
        path = tmp_path / f"{index}.bin"
        path.write_bytes(data)
        result = search(path)
        assert not result["files"] and "binary" in result["stats"]["errors"][0]


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX special file")
def test_special_file_is_rejected_before_read_or_content_condition(tmp_path):
    path = tmp_path / "pipe"
    os.mkfifo(path)
    result = core.UnifiedFileExplorerExecutor().execute_search(
        "", content_query="alpha\nbeta", target_scope="selected", target_paths=[str(path)],
        conditions=[{"field": "content", "operator": "contains", "value": "alpha"}],
        search_options={"cross_line": True}
    )
    assert not result["files"] and "regular file" in result["stats"]["errors"][0]


def test_per_file_limit_keeps_bounded_partial_results_and_diagnostics(tmp_path, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("a\na\na\na")
    monkeypatch.setattr(core, "MAX_CROSS_LINE_MATCHES", 2)
    result = search(path, "a")
    assert result["stats"]["total_matches"] == 2
    assert result["stats"]["match_limit_reached"] and result["stats"]["partial"]
    assert "results are partial" in result["stats"]["errors"][0]
    path.write_text("a\na")
    assert not search(path, "a")["stats"]["partial"]


def test_global_match_budget_never_overshoots_and_reports_skipped_files(tmp_path, monkeypatch):
    paths = [tmp_path / f"{index}.txt" for index in range(3)]
    for path in paths:
        path.write_text("a\na")
    monkeypatch.setattr(core, "MAX_TOTAL_MATCHES", 3)
    result = core.UnifiedFileExplorerExecutor().execute_search(
        "", content_query="a", target_scope="selected", target_paths=list(map(str, paths)),
        search_options={"cross_line": True}
    )
    assert [item.match_count for item in result["files"]] == [2, 1]
    assert result["stats"]["total_matches"] == 3 and result["stats"]["partial"]
    assert any("Search stopped" in error for error in result["stats"]["errors"])


def test_error_budget_stops_remaining_targets(tmp_path, monkeypatch):
    paths = [tmp_path / f"{index}.bin" for index in range(4)]
    for path in paths:
        path.write_bytes(b"\x00alpha\nbeta")
    monkeypatch.setattr(core, "MAX_OPERATION_ERRORS", 2)
    result = core.UnifiedFileExplorerExecutor().execute_search(
        "", content_query="alpha\nbeta", target_scope="selected", target_paths=list(map(str, paths)),
        search_options={"cross_line": True}
    )
    assert len(result["stats"]["errors"]) == 2
    assert "remaining files were not searched" in result["stats"]["errors"][-1]


def test_zero_width_regex_line_and_eof_positions(tmp_path):
    path = tmp_path / "target.txt"
    path.write_text("a\nb\n")
    result = search(path, r"^", regex=True)
    assert [(m.line, m.col) for m in result["files"][0].matches] == [(1, 0), (2, 0), (3, 0)]


def test_cross_line_mode_round_trip_retranslation_and_mutual_exclusion(qapp):
    panel = SearchOptionsPanel()
    values = []
    panel.options_changed.connect(values.append)
    try:
        assert not panel.get_options()["cross_line"]
        panel.set_options({"cross_line": True, "case_sensitive": True, "regex": True})
        panel.retranslateUi()
        assert panel.get_options()["cross_line"] and panel.get_options()["regex"]
        panel.chk_multi_query.setChecked(True)
        assert not panel.get_options()["cross_line"] and panel.get_options()["multi_query"]
        panel.chk_cross_line.setChecked(True)
        assert panel.get_options()["cross_line"] and not panel.get_options()["multi_query"]
        assert not any(value["multi_query"] and value["cross_line"] for value in values)
        panel.set_options({})
        assert not panel.get_options()["cross_line"]
    finally:
        panel.deleteLater()


@pytest.mark.parametrize("scope", ["file", "selected"])
@pytest.mark.parametrize("view", [0, 1])
def test_real_worker_block_positions_both_views_and_exact_targets(scope, view, tmp_path, docks, qtbot,
                                                                qapp, monkeypatch):
    chosen, sibling = tmp_path / "chosen.txt", tmp_path / "sibling.txt"
    for path in (chosen, sibling):
        path.write_text("intro\nxx alpha\nbeta")
    dock = docks()
    populate_dock(dock, [chosen, sibling])
    set_scope(dock, scope)
    select_paths(dock, view, [chosen])
    dock.ed_directory.setText(str(chosen))
    dock.ed_exc.clear()
    dock.content_panel.set_query("alpha\nbeta")
    dock.search_options_panel.set_options({"cross_line": True})
    dock._user_manually_changed_view = True
    captures = []
    original = dock.executor._search_cross_line

    def capture(*args):
        captures.append(QThread.currentThread() != qapp.thread())
        return original(*args)

    monkeypatch.setattr(dock.executor, "_search_cross_line", capture)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert captures == [True]
    assert list(dock.last_search_results) == [str(chosen)]
    assert dock.last_search_results[str(chosen)][0][:2] == (2, 3)
    assert "alpha\\nbeta" in dock.last_search_results[str(chosen)][0][2]
    assert dock.results_stack.currentIndex() == view


@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.parametrize("view", [0, 1])
def test_real_worker_pause_at_block_read_then_resume_or_cancel(cancel, view, tmp_path, docks, qtbot, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("alpha\nbeta")
    dock = docks()
    set_scope(dock, "file")
    dock.results_stack.setCurrentIndex(view)
    dock._user_manually_changed_view = True
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query("alpha\nbeta")
    dock.search_options_panel.set_options({"cross_line": True})
    entered = threading.Event()
    original = dock.executor._read_cross_line_text

    def pause_read(value):
        dock.executor.pause()
        entered.set()
        return original(value)

    monkeypatch.setattr(dock.executor, "_read_cross_line_text", pause_read)
    dock._list_files()
    qtbot.waitUntil(entered.is_set, timeout=3000)
    qtbot.wait(30)
    assert dock._operation_running()
    dock._on_progress_canceled() if cancel else dock.executor.resume()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert not dock.executor._paused
    assert bool(dock.last_search_results) != cancel
    if cancel:
        assert dock._last_content_search_universe is None


def test_mode_change_invalidates_empty_incremental_cache(tmp_path, docks, qtbot):
    path = tmp_path / "target.txt"
    path.write_text("alpha\nbeta")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query("alpha\nbeta")
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert dock._last_content_search_universe["paths"] == []
    dock.search_options_panel.chk_cross_line.setChecked(True)
    assert dock._last_content_search_universe is None
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert list(dock.last_search_results) == [str(path)]


def test_partial_gui_result_has_diagnostic_and_no_incremental_cache(tmp_path, docks, qtbot, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("a\na\na")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.content_panel.set_query("a")
    dock.search_options_panel.chk_cross_line.setChecked(True)
    monkeypatch.setattr(core, "MAX_CROSS_LINE_MATCHES", 2)
    dock._list_files()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert "partial" in dock.results_status.toolTip()
    assert dock._last_content_search_universe is None
    assert len(dock.last_search_results[str(path)]) == 2


def test_cross_line_replacement_rejected_before_confirmation_or_write(tmp_path, docks, monkeypatch):
    path = tmp_path / "target.txt"
    path.write_text("alpha\nbeta")
    executor = core.UnifiedFileExplorerExecutor()
    files = executor.execute_browse(str(path), target_scope="file")["files"]
    result = executor.execute_replace(files, "alpha\nbeta", "changed", search_options={"cross_line": True})
    assert not result["success"] and "Cross-line block replacement" in result["error"]
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(path))
    dock.content_panel.set_query("alpha\nbeta")
    dock.search_options_panel.chk_cross_line.setChecked(True)
    monkeypatch.setattr(QMessageBox, "question", lambda *_a: pytest.fail("Unexpected confirmation"))
    dock._start_replace(True)
    assert not dock._operation_running() and path.read_text() == "alpha\nbeta"
