"""Real-thread regressions for the finite FE-PAR-07 lifecycle stage."""

import threading
import time

import pytest
import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent, QThread, QTimer, Qt
from PySide6.QtWidgets import QDialog, QMainWindow, QMessageBox, QProgressDialog, QTabWidget, QVBoxLayout

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor
from src.core.file_list_executor import FileListExecutor
from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.panels.file_explorer_operation import ExplorerOperationReceiver
from src.ui import FeatureType, thread_manager


@pytest.fixture
def docks(qapp, qtbot, monkeypatch):
    """Isolate the singleton registry; always settle native workers before disposal."""
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(thread_manager, "_feature_locks", {
        feature: threading.Lock() for feature in FeatureType
    })
    for name in ("critical", "warning", "information"):
        monkeypatch.setattr(QMessageBox, name, lambda *_a, **_kw: QMessageBox.Ok)
    created = []

    def create(parent=None):
        host = parent or QMainWindow()
        dock = FileExplorerDock(host, dialog_mode=isinstance(host, QDialog))
        dock._current_search_params = {}
        if isinstance(host, QMainWindow):
            host.addDockWidget(Qt.LeftDockWidgetArea, dock)
        else:
            layout = host.layout() or QVBoxLayout(host)
            layout.addWidget(dock)
        host.resize(900, 650)
        host.show()
        created.append((host, dock))
        return dock

    yield create
    for _, dock in created:
        if shiboken6.isValid(dock) and dock._operation_running():
            dock._request_shutdown()
            qtbot.waitUntil(lambda: not shiboken6.isValid(dock) or not dock._operation_running(), timeout=4000)
    for host, dock in created:
        if shiboken6.isValid(dock):
            dock._close_progress_dialog()
            dock.deleteLater()
        if shiboken6.isValid(host):
            host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()
    assert thread_manager.get_stats()["total_threads"] == 0


def request(kind, path):
    if kind == "replace":
        files = UnifiedFileExplorerExecutor().execute_browse(str(path), filters={})["files"]
        return dict(files=files, search_text="needle", replace_text="changed",
                    search_options={}, replace_all=True)
    values = dict(directory=str(path), show_hidden=True, recursive=True, filters={}, conditions=[])
    if kind == "search":
        values.update(filename_pattern="", content_query="needle", search_options={})
    return values


def pause_at_first_checkpoint(dock, monkeypatch):
    entered = threading.Event()
    threads = []
    original = dock.executor.checkpoint

    def checkpoint():
        if not entered.is_set():
            threads.append(QThread.currentThread())
            dock.executor.pause()
            entered.set()
        return original()

    monkeypatch.setattr(dock.executor, "checkpoint", checkpoint)
    return entered, threads


def test_core_pause_waits_then_resume_or_cancel_wakes():
    for cancel in (False, True):
        executor = UnifiedFileExplorerExecutor()
        executor.prepare_operation()
        executor.pause()
        entered = threading.Event()
        finished = threading.Event()
        values = []

        def run():
            entered.set()
            values.append(executor.checkpoint())
            finished.set()

        worker = threading.Thread(target=run)
        worker.start()
        try:
            assert entered.wait(1)
            assert not finished.wait(0.05)
            executor.cancel() if cancel else executor.resume()
            assert finished.wait(1)
            assert values == [not cancel]
        finally:
            executor.cancel()
            worker.join(1)
        assert not worker.is_alive()


def test_prepared_search_does_not_reset_startup_cancellation(tmp_path):
    (tmp_path / "sample.txt").write_text("needle")
    executor = UnifiedFileExplorerExecutor()
    executor.prepare_operation()
    executor.cancel()
    result = executor.execute_search(**request("search", tmp_path), prepared=True)
    assert result["stats"]["cancelled"]
    assert result["files"] == []


def test_listing_checkpoint_and_directory_symlink_cycle(tmp_path):
    child = tmp_path / "child"
    child.mkdir()
    (child / "sample.txt").write_text("needle")
    (child / "loop").symlink_to(tmp_path, target_is_directory=True)
    result = FileListExecutor.list_files(str(tmp_path), recursive=True)
    assert len(result.files) == 3
    assert FileListExecutor.list_files(str(tmp_path), recursive=True, checkpoint=lambda: False).files == []


def test_shared_listing_preserves_noncyclic_directory_links(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "sample.txt").write_text("needle")
    alias = tmp_path / "alias"
    alias.symlink_to(folder, target_is_directory=True)
    paths = {item.path for item in FileListExecutor.list_files(str(tmp_path), recursive=True).files}
    assert str(alias / "sample.txt") in paths and str(folder / "sample.txt") in paths


@pytest.mark.parametrize("kind", ["search", "browse", "replace"])
def test_real_worker_pause_resume_responsiveness_and_cleanup(kind, tmp_path, docks, qtbot, qapp, monkeypatch):
    target = tmp_path / "sample.txt"
    target.write_text("needle")
    dock = docks()
    results = []
    monkeypatch.setattr(dock, f"_on_{kind}_finished", results.append)
    entered, threads = pause_at_first_checkpoint(dock, monkeypatch)
    assert dock._launch_operation(kind, request(kind, tmp_path))
    native = dock._worker_thread
    worker = dock._worker
    qtbot.waitUntil(entered.is_set, timeout=2000)
    assert threads[0] == native and threads[0] != qapp.thread()
    assert not dock._launch_operation("browse", request("browse", tmp_path))
    assert len(thread_manager._threads) == 1
    button = dock._progress_label.pause_button
    button.setChecked(True)
    beats = []
    timer = QTimer(dock)
    timer.setInterval(5)
    timer.timeout.connect(lambda: beats.append(True))
    timer.start()
    qtbot.wait(60)
    assert len(beats) >= 3 and not results
    assert target.read_text() == "needle"
    assert button.geometry().right() < dock._progress_label.width()
    assert button.width() == 28
    button.click()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    timer.stop()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    assert results and not shiboken6.isValid(worker) and not shiboken6.isValid(native)
    assert dock._worker is None and dock.progress_dialog is None
    assert not thread_manager.is_feature_running(FeatureType.FILE_EXPLORER)
    assert target.read_text() == ("changed" if kind == "replace" else "needle")


@pytest.mark.parametrize("kind", ["search", "browse", "replace"])
def test_cancel_while_paused_and_next_operation(kind, tmp_path, docks, qtbot, monkeypatch):
    target = tmp_path / "sample.txt"
    target.write_text("needle")
    dock = docks()
    results = []
    monkeypatch.setattr(dock, f"_on_{kind}_finished", results.append)
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    assert dock._launch_operation(kind, request(kind, tmp_path))
    qtbot.waitUntil(entered.is_set, timeout=2000)
    button = dock._progress_label.pause_button
    dock._on_progress_canceled()
    assert not button.isEnabled()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    cancelled = results[0].get("cancelled", results[0].get("stats", {}).get("cancelled"))
    assert cancelled and target.read_text() == "needle"
    monkeypatch.setattr(dock, "_on_browse_finished", results.append)
    assert dock._launch_operation("browse", request("browse", tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert results[-1]["stats"]["cancelled"] is False


def test_startup_cancel_is_not_lost(tmp_path, docks, qtbot, monkeypatch):
    (tmp_path / "sample.txt").write_text("needle")
    dock = docks()
    results = []
    monkeypatch.setattr(dock, "_on_browse_finished", results.append)
    assert dock._launch_operation("browse", request("browse", tmp_path))
    dock._on_progress_canceled()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert results[0]["stats"]["cancelled"] and results[0]["files"] == []


@pytest.mark.parametrize("action", ["cancel", "parent_close", "dock_delete"])
def test_cancel_during_atomic_commit_finishes_current_file_only(action, tmp_path, docks, qtbot, monkeypatch):
    import src.core.file_explorer_executor as core

    targets = [tmp_path / "a.txt", tmp_path / "b.txt"]
    for target in targets:
        target.write_text("needle")
    dock = docks()
    committed = threading.Event()
    release = threading.Event()
    original = core.write_existing_text_atomically
    results = []
    monkeypatch.setattr(dock, "_on_replace_finished", results.append)

    def write(path, text, revision):
        committed.set()
        assert release.wait(3)
        original(path, text, revision)

    monkeypatch.setattr(core, "write_existing_text_atomically", write)
    assert dock._launch_operation("replace", request("replace", tmp_path))
    native = dock._worker_thread
    try:
        qtbot.waitUntil(committed.is_set, timeout=2000)
        if action == "cancel":
            dock._on_progress_canceled()
        elif action == "parent_close":
            dock.parentWidget().close()
        else:
            dock.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
            assert not shiboken6.isValid(dock)
        assert native.isRunning()
    finally:
        release.set()
    qtbot.waitUntil(lambda: not shiboken6.isValid(native) or not native.isRunning(), timeout=3000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)
    if shiboken6.isValid(dock):
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert [target.read_text() for target in targets] == ["changed", "needle"]
    if action == "cancel":
        assert results[0]["files_modified"] == results[0]["replacements_made"] == 1
        assert results[0]["cancelled"]
    else:
        assert results == []
    assert sorted(path.name for path in tmp_path.iterdir()) == ["a.txt", "b.txt"]


@pytest.mark.parametrize("kind", ["browse", "search", "replace"])
def test_cancel_after_result_signal_before_native_settlement(kind, tmp_path, docks, qtbot, monkeypatch):
    target = tmp_path / "sample.txt"
    target.write_text("needle")
    dock = docks()
    results = []
    monkeypatch.setattr(dock, f"_on_{kind}_finished", results.append)
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    assert dock._launch_operation(kind, request(kind, tmp_path))
    qtbot.waitUntil(entered.is_set, timeout=2000)
    emitted, release = threading.Event(), threading.Event()

    def hold_result(_result):
        emitted.set()
        assert release.wait(3)

    dock._worker.finished.connect(hold_result, Qt.DirectConnection)
    dock._worker.resume()
    try:
        qtbot.waitUntil(emitted.is_set, timeout=2000)
        assert dock._operation_running() and dock.progress_dialog is not None
        dock._on_progress_canceled()
        label = dock.progress_dialog.labelText()
        dock._operation_receiver.progress("late progress")
        dock._operation_receiver.progress_detailed(1, 1, "late progress")
        assert dock.progress_dialog.labelText() == label
    finally:
        release.set()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    result = results[0]
    if kind == "replace":
        assert result["cancelled"] and result["files_modified"] == 1
        assert target.read_text() == "changed"
    else:
        assert result["stats"]["cancelled"] and result["files"] == []
        assert target.read_text() == "needle"


def test_warning_is_not_terminal_and_does_not_duplicate_completion(tmp_path, docks, qtbot, monkeypatch):
    dock = docks()
    results, failures = [], []
    monkeypatch.setattr(dock, "_on_browse_finished", results.append)
    monkeypatch.setattr(dock, "_on_operation_error", failures.append)

    def warning(**_kwargs):
        dock.executor.error.emit("warning " * 100)
        return {"files": [], "stats": {"errors": [], "cancelled": False}}

    monkeypatch.setattr(dock.executor, "execute_browse", warning)
    assert dock._launch_operation("browse", request("browse", tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert len(results) == 1 and not failures
    assert len(dock.results_status.toolTip()) == 500


@pytest.mark.parametrize("action", ["dock_close", "parent_close", "dock_delete", "parent_delete", "reject"])
def test_close_while_paused_suppresses_late_callbacks(action, tmp_path, docks, qtbot, monkeypatch):
    (tmp_path / "sample.txt").write_text("needle")
    host = QDialog() if action == "reject" else QMainWindow()
    dock = docks(host)
    results = []
    monkeypatch.setattr(dock, "_on_browse_finished", results.append)
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    assert dock._launch_operation("browse", request("browse", tmp_path))
    qtbot.waitUntil(entered.is_set, timeout=2000)
    native = dock._worker_thread
    calls = {
        "dock_close": dock.close, "parent_close": host.close,
        "dock_delete": dock.deleteLater, "parent_delete": host.deleteLater, "reject": dock.reject,
    }
    calls[action]()
    if "delete" in action:
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qtbot.waitUntil(lambda: not shiboken6.isValid(native) or not native.isRunning(), timeout=3000)
    qtbot.waitUntil(lambda: not shiboken6.isValid(dock) or not dock._active_operation, timeout=3000)
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    assert not results
    if action.endswith("delete"):
        assert not shiboken6.isValid(dock)
    elif action == "reject":
        assert host.result() == QDialog.Rejected and not host.isVisible()
    else:
        assert not (dock if action == "dock_close" else host).isVisible()


def test_stale_receiver_cannot_reopen_progress_or_add_results(docks):
    dock = docks()
    old = ExplorerOperationReceiver(dock, 1)
    dock._operation_generation = 2
    dock._active_operation = True
    old.progress("stale")
    old.progress_detailed(1, 1, "stale")
    old.batch([("/tmp/stale", [])], 1, 1)
    old.completed({"files": []})
    old.thread_finished()
    assert dock.progress_dialog is None and dock.results_tree.get_matches_data() == {}
    dock._active_operation = False
    current = ExplorerOperationReceiver(dock, 2)
    current.progress("late")
    assert dock.progress_dialog is None


def test_failure_settles_thread_and_registration_can_recover(tmp_path, docks, qtbot, monkeypatch):
    dock = docks()
    errors = []
    monkeypatch.setattr(dock, "_on_operation_error", errors.append)

    def fail(**_request):
        raise ValueError("bounded test failure")

    monkeypatch.setattr(dock.executor, "execute_browse", fail)
    thread_manager._shutdown = True
    assert not dock._launch_operation("browse", request("browse", tmp_path))
    assert not dock._active_operation
    thread_manager.resume_registration()
    assert dock._launch_operation("browse", request("browse", tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert errors == ["bounded test failure"]
    assert not thread_manager._threads


def test_two_docks_and_manager_wait_for_cancelled_live_workers(tmp_path, docks, qtbot, monkeypatch):
    (tmp_path / "sample.txt").write_text("needle")
    first, second = docks(), docks()
    for dock in (first, second):
        monkeypatch.setattr(dock, "_on_browse_finished", lambda _result: None)
        entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
        assert dock._launch_operation("browse", request("browse", tmp_path))
        qtbot.waitUntil(entered.is_set, timeout=2000)
    assert thread_manager.get_active_threads()[FeatureType.FILE_EXPLORER] == 2
    # Disabling the GUI event loop must not deadlock the worker's quit connection.
    assert thread_manager.wait_all_threads(2000)
    qtbot.waitUntil(lambda: not first._active_operation and not second._active_operation, timeout=3000)
    thread_manager.resume_registration()
    assert not thread_manager._threads


def test_parent_close_settles_all_its_paused_docks(tmp_path, docks, qtbot, monkeypatch):
    host = QMainWindow()
    first, second = docks(host), docks(host)
    for dock in (first, second):
        entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
        assert dock._launch_operation("browse", request("browse", tmp_path))
        qtbot.waitUntil(entered.is_set, timeout=2000)
    host.close()
    qtbot.waitUntil(lambda: not first._active_operation and not second._active_operation, timeout=3000)
    assert not host.isVisible() and not thread_manager._threads


def test_force_cleanup_never_terminates_live_file_explorer(monkeypatch):
    class LiveThread:
        def __init__(self):
            self.terminated = False
        def isRunning(self):
            return True
        def terminate(self):
            self.terminated = True

    from src.ui.thread_manager import ThreadInfo
    native = LiveThread()
    cancelled = []
    info = ThreadInfo(native, None, FeatureType.FILE_EXPLORER, lambda: cancelled.append(True), False)
    info.is_running = False
    monkeypatch.setattr(thread_manager, "_threads", {"protected": info})
    thread_manager.force_cleanup()
    assert cancelled and not native.terminated
    assert thread_manager.get_stats()["running_threads"] == 1
    assert thread_manager._threads == {"protected": info}


@pytest.mark.parametrize("exclusive", [True, False])
def test_failed_registration_does_not_retain_worker_or_lock(exclusive, docks):
    docks()

    class InvalidSignal:
        def connect(self, _callback):
            raise RuntimeError("unavailable signal")

    class InvalidThread:
        finished = InvalidSignal()

    assert not thread_manager.start_thread(
        "failed", InvalidThread(), None, FeatureType.FILE_EXPLORER, exclusive=exclusive,
    )
    assert not thread_manager._threads
    assert thread_manager.can_start_feature(FeatureType.FILE_EXPLORER)


@pytest.mark.parametrize("reply", [QMessageBox.Yes, QMessageBox.No])
def test_app_close_refuses_live_writer_and_restores_registration(reply, docks, monkeypatch):
    from PySide6.QtGui import QCloseEvent
    from src.gui.window_settings import WindowSettings

    dock = docks()
    host = dock.parentWidget()
    monkeypatch.setattr(thread_manager, "get_active_threads", lambda: {FeatureType.FILE_EXPLORER: 1})

    def timeout(**_kwargs):
        thread_manager._shutdown = True
        return False

    monkeypatch.setattr(thread_manager, "wait_all_threads", timeout)
    monkeypatch.setattr(thread_manager, "is_feature_running", lambda _feature: True)
    monkeypatch.setattr(QMessageBox, "warning", lambda *_a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *_a: reply)
    forced = []
    monkeypatch.setattr(thread_manager, "force_cleanup", lambda: forced.append(True))
    event = QCloseEvent()
    WindowSettings.handle_close_event(host, event)
    assert not event.isAccepted() and not forced
    assert thread_manager._shutdown is False


def test_repeated_real_browse_has_no_retained_worker_or_progress(tmp_path, docks, qtbot, qapp, monkeypatch):
    (tmp_path / "sample.txt").write_text("needle")
    dock = docks()
    monkeypatch.setattr(dock, "_on_browse_finished", lambda _result: None)
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    baseline = len(qapp.allWidgets())
    references = []
    for _ in range(10):
        assert dock._launch_operation("browse", request("browse", tmp_path))
        references.extend([dock._worker, dock._worker_thread, dock._operation_receiver, dock.progress_dialog])
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        assert not thread_manager._threads
    assert all(not shiboken6.isValid(obj) for obj in references)
    assert not dock.findChildren(QProgressDialog)
    assert len(qapp.allWidgets()) <= baseline


@pytest.mark.parametrize("view", [0, 1])
def test_real_search_batch_reaches_both_views_before_completion(view, tmp_path, docks, qtbot):
    target = tmp_path / "sample.txt"
    target.write_text("needle")
    dock = docks()
    dock.results_stack.setCurrentIndex(view)
    dock._current_search_params = dict(directory=str(tmp_path), filename_pattern="",
                                     content_query="needle", search_options={}, start_time=time.time())
    assert dock._launch_operation("search", request("search", tmp_path))
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    assert str(target) in dock.last_search_results
    assert dock.results_stack.currentIndex() == view
    if view == 1:
        assert dock.table_manager.table.rowCount() == 1


def test_main_window_tab_close_waits_for_paused_worker(tmp_path, docks, qtbot, monkeypatch):
    from src.app import MainWindow

    host = QMainWindow()
    host.tabs = QTabWidget(host)
    host.setCentralWidget(host.tabs)
    host.tool_tabs = {}
    host._restore_window_flags = lambda: None
    host._save_tab_state = lambda: None
    host._close_tab = lambda index: MainWindow._close_tab(host, index)
    dock = docks(host)
    host.removeDockWidget(dock)
    host.tabs.addTab(dock, "File Explorer")
    entered, _ = pause_at_first_checkpoint(dock, monkeypatch)
    assert dock._launch_operation("browse", request("browse", tmp_path))
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)
    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    assert not dock._active_operation and not thread_manager._threads
