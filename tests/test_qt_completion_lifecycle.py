"""Bounded Qt completion ownership and cross-thread GC regressions."""

import gc
import threading
import weakref

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QThread, Qt

from src.theme_manager import ThemeManager
from src.ui import FeatureType, thread_manager
from test_file_explorer_lifecycle import docks
from test_file_explorer_target_scope import set_scope


@pytest.fixture
def registry(monkeypatch, qapp):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(thread_manager, "_feature_locks", {feature: threading.Lock() for feature in FeatureType})
    yield thread_manager
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    assert not thread_manager._threads


def test_registry_receiver_deletion_is_really_deferred(registry):
    thread = QThread()
    worker = QObject()
    destroyed = []
    assert registry.start_thread("ownership", thread, worker, FeatureType.FILE_EXPLORER, exclusive=False)
    receiver = registry._threads["ownership"].finished_receiver
    receiver.destroyed.connect(lambda: destroyed.append(True))
    reference = weakref.ref(receiver)
    registry._on_thread_finished("ownership")
    del receiver
    gc.collect()
    try:
        assert not destroyed, "Python ownership deleted a receiver before its DeferredDelete event"
        assert reference() is not None
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        assert destroyed == [True]
    finally:
        thread.deleteLater()
        worker.deleteLater()


@pytest.mark.parametrize("exclusive", [False, True])
@pytest.mark.parametrize("reuse_thread", [False, True])
def test_queued_old_completion_cannot_remove_reused_registration(registry, qapp, exclusive, reuse_thread):
    first = QThread()
    second = first if reuse_thread else QThread()
    workers = [QObject(), QObject()]
    feature = FeatureType.FILE_EXPLORER
    try:
        assert registry.start_thread("reused", first, workers[0], feature, exclusive=exclusive)
        first.started.connect(first.quit, Qt.DirectConnection)
        first.start()
        assert first.wait(2000)
        first.started.disconnect(first.quit)
        # Native finished is queued to the GUI. Explicit settlement wins first.
        registry._on_thread_finished("reused")
        assert registry.start_thread("reused", second, workers[1], feature, exclusive=exclusive)
        second.start()
        qapp.processEvents()
        assert second.isRunning()
        assert registry._threads.get("reused") is not None
        assert registry._threads["reused"].thread is second
        assert registry.can_start_feature(feature) is not exclusive
    finally:
        first.quit()
        second.quit()
        assert first.wait(2000) and second.wait(2000)
        registry._on_thread_finished("reused")
        for obj in set([first, second, *workers]):
            obj.deleteLater()


@pytest.mark.parametrize("view", [0, 1])
@pytest.mark.parametrize("mode", ["single", "multi", "cross"])
def test_completion_with_worker_gc_and_gui_gc(mode, view, tmp_path, docks, qtbot, qapp, monkeypatch):
    path = tmp_path / "synthetic.txt"
    path.write_text("alpha\nbeta\n", encoding="utf-8")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(path))
    dock.ed_exc.clear()
    dock.results_stack.setCurrentIndex(view)
    dock._user_manually_changed_view = True
    dock.content_panel.set_query("alpha" if mode == "single" else "alpha\nbeta")
    dock.search_options_panel.set_options({"multi_query": mode == "multi", "cross_line": mode == "cross"})
    original_checkpoint = dock.executor.checkpoint
    original_statistics = dock._update_statistics
    original_log = dock._append_operation_log
    worker_collections = []
    gui_collections = []
    paused = threading.Event()

    def checkpoint():
        if QThread.currentThread() != qapp.thread():
            if not paused.is_set():
                dock.executor.pause()
                paused.set()
            if len(worker_collections) < 6:
                gc.collect()
                worker_collections.append(True)
        return original_checkpoint()

    def statistics(*args):
        gc.collect()
        gui_collections.append(True)
        return original_statistics(*args)

    def log(*args):
        gc.collect()
        return original_log(*args)

    monkeypatch.setattr(dock.executor, "checkpoint", checkpoint)
    monkeypatch.setattr(dock, "_update_statistics", statistics)
    monkeypatch.setattr(dock, "_append_operation_log", log)
    for _ in range(3):
        paused.clear()
        dock._list_files()
        qtbot.waitUntil(paused.is_set, timeout=3000)
        gc.collect()
        assert dock._operation_running()
        dock.executor.resume()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
        assert list(dock.last_search_results) == [str(path)]
        assert dock.results_stack.currentIndex() == view
        assert not thread_manager._threads
        assert dock._operation_receiver is None and dock._worker is None
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        qapp.processEvents()
        gc.collect()
    assert worker_collections and len(gui_collections) == 3
    for theme in ("dark", "light", "system"):
        ThemeManager.apply_theme(qapp, theme)
        qapp.processEvents()
    assert dock.results_status.text().startswith("Found 1 file")
