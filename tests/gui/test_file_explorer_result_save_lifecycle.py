"""Lifecycle regressions for File Explorer result saving."""

# pylint: disable=no-name-in-module,protected-access

import builtins
import threading
from threading import Event, Lock

import pytest
from PySide6.QtCore import QCoreApplication, QThread

import src.gui.file_explorer_dock as dock_module
import src.gui.panels.result_export as export_module
from src.gui.file_explorer_dock import FileExplorerDock
from src.ui import FeatureType, thread_manager


@pytest.fixture(autouse=True)
def isolated_threads(monkeypatch, qtbot):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(
        thread_manager,
        "_feature_locks",
        {feature: threading.Lock() for feature in FeatureType},
    )
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.quit()
            info.thread.wait(3000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def build_dock(monkeypatch, tmp_path, name="source.txt"):
    dock = FileExplorerDock()
    source_path = str(tmp_path / name)
    dock.results_tree.populate({source_path: [(1, 0, "needle")]})
    feedback = {"info": [], "critical": []}
    monkeypatch.setattr(
        dock_module.QMessageBox,
        "information",
        lambda *_args: feedback["info"].append((_args, QThread.currentThread())),
    )
    monkeypatch.setattr(
        dock_module.QMessageBox,
        "critical",
        lambda *_args: feedback["critical"].append((_args, QThread.currentThread())),
    )
    return dock, feedback


def select_path(monkeypatch, output_path):
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(output_path), "Text Files (*.txt)"),
    )


def test_result_extraction_stays_gui_and_save_work_runs_off_gui(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    assert dock.results_tree.__class__.__module__ == "src.gui.panels.results_tree"
    output_path = tmp_path / "results.txt"
    expected = dock.results_tree.export_to_text()
    extraction_threads = []
    serialization_threads = []
    write_threads = []
    original_get_matches = dock.results_tree.get_matches_data
    original_lines = export_module.iter_match_result_lines
    original_open = builtins.open

    select_path(monkeypatch, output_path)

    def observed_get_matches():
        extraction_threads.append(QThread.currentThread())
        return original_get_matches()

    def observed_lines(matches):
        serialization_threads.append(QThread.currentThread())
        return original_lines(matches)

    def observed_open(*args, **kwargs):
        write_threads.append(QThread.currentThread())
        return original_open(*args, **kwargs)

    monkeypatch.setattr(dock.results_tree, "get_matches_data", observed_get_matches)
    monkeypatch.setattr(export_module, "iter_match_result_lines", observed_lines)
    monkeypatch.setattr(builtins, "open", observed_open)

    dock._save_results()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    gui_thread = QCoreApplication.instance().thread()
    assert extraction_threads == [gui_thread]
    assert serialization_threads and serialization_threads[0] is not gui_thread
    assert write_threads and write_threads[0] is not gui_thread
    assert feedback["info"] and feedback["info"][0][1] is gui_thread
    assert output_path.read_text(encoding="utf-8") == expected
    assert not thread_manager._threads


def test_one_save_per_dock_and_independent_docks(monkeypatch, qtbot, tmp_path):
    first, _first_feedback = build_dock(monkeypatch, tmp_path, name="first-source.txt")
    second, _second_feedback = build_dock(monkeypatch, tmp_path, name="second-source.txt")
    qtbot.addWidget(first)
    qtbot.addWidget(second)
    paths = iter((str(tmp_path / "first.txt"), str(tmp_path / "second.txt")))
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (next(paths), "Text Files (*.txt)"),
    )
    entered = Event()
    release = Event()
    lock = Lock()
    state = {"active": 0}
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        with lock:
            state["active"] += 1
            if state["active"] == 2:
                entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    try:
        first._save_results()
        second._save_results()
        qtbot.waitUntil(entered.is_set, timeout=3000)
        first_thread = first._worker_thread

        first._save_results()

        assert first._worker_thread is first_thread
        assert not first._launch_operation("browse", {})
        assert thread_manager.get_active_threads()[FeatureType.FILE_EXPLORER] == 2
        release.set()
        qtbot.waitUntil(
            lambda: not first._operation_running() and not second._operation_running(),
            timeout=3000,
        )
        assert not thread_manager._threads
    finally:
        release.set()


def test_cancelled_save_preserves_destination_log_and_controls(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    try:
        dock._save_results()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        assert not dock._progress_label.pause_button.isEnabled()
        assert not dock.btn_save_results.isEnabled()
        assert not dock.btn_export_csv.isEnabled()
        dock._on_progress_canceled()
        release.set()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

        assert output_path.read_text(encoding="utf-8") == "preserve me"
        assert not list(tmp_path.glob(".clarify-match-results-*.tmp"))
        assert dock.btn_save_results.isEnabled()
        assert dock.btn_export_csv.isEnabled()
        assert "save" in dock.operation_log.toPlainText().lower()
        assert "cancel" in dock.results_status.text().lower()
        assert not feedback["info"]
        assert not feedback["critical"]
    finally:
        release.set()


def test_io_error_is_reported_on_gui_without_replacing_destination(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    original_open = builtins.open

    def denied_open(path, *args, **kwargs):
        if str(path).endswith(".tmp"):
            raise PermissionError("denied")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied_open)

    dock._save_results()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert output_path.read_text(encoding="utf-8") == "preserve me"
    assert feedback["critical"]
    assert "denied" in feedback["critical"][0][0][-1]
    assert feedback["critical"][0][1] is QCoreApplication.instance().thread()
    assert "failed" in dock.results_status.text().lower()
    assert not list(tmp_path.glob(".clarify-match-results-*.tmp"))


def test_close_waits_for_save_and_discards_late_feedback(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.show()
    output_path = tmp_path / "results.txt"
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    dock._save_results()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    dock.close()

    assert dock.isVisible()
    release.set()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    qtbot.waitUntil(lambda: not dock.isVisible(), timeout=3000)
    assert not output_path.exists()
    assert not feedback["info"]
    assert not feedback["critical"]
    assert not thread_manager._threads


def test_save_preserves_views_filters_cache_and_bounded_log(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    output_path = tmp_path / "results.txt"
    select_path(monkeypatch, output_path)
    dock.results_stack.setCurrentIndex(1)
    dock.filter_panel.ed_extensions.setText(".txt,.md")
    dock.combo_target_scope.setCurrentIndex(1)
    cache = {"identity": "preserve"}
    dock._last_content_search_universe = cache
    previous_results = dock.results_tree.get_matches_data()

    dock._save_results()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert dock.results_stack.currentIndex() == 1
    assert dock.filter_panel.ed_extensions.text() == ".txt,.md"
    assert dock.combo_target_scope.currentIndex() == 1
    assert dock._last_content_search_universe is cache
    assert dock.results_tree.get_matches_data() is previous_results
    assert dock.operation_log.document().blockCount() <= 200
    assert feedback["info"]
    assert output_path.exists()


def test_empty_cancelled_dialog_and_shutdown_rejection_do_not_leak(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_tree.print_message("")

    dock._save_results()
    assert not dock._operation_running()
    assert feedback["info"]

    dock.results_tree.populate({"source": [(1, 0, "needle")]})
    feedback["info"].clear()
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: ("", ""),
    )
    dock._save_results()
    assert not dock._operation_running()
    assert not feedback["info"]
    assert not feedback["critical"]

    select_path(monkeypatch, tmp_path / "rejected.txt")
    thread_manager._shutdown = True
    dock._save_results()
    assert not dock._operation_running()
    assert feedback["critical"]
    assert not thread_manager._threads
