"""Lifecycle regressions for AI Processor and its embedded operation panels."""

# pylint: disable=no-name-in-module  # Qt and Shiboken expose dynamic bindings.

import threading

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread, QTimer
from PySide6.QtWidgets import QMainWindow, QTabWidget
from shiboken6 import isValid

from src.app import MainWindow
from src.gui.ai_processor_dock import AIProcessorDock
from src.gui.base_dock import ProcessorWorkerBase
from src.ui import FeatureType, thread_manager


class ControlledWorker(ProcessorWorkerBase):
    """Provider-free worker that settles only after release or cancellation."""

    instances = []

    def __init__(self, *_args, **_kwargs):
        super().__init__()
        self.started_event = threading.Event()
        self.release_event = threading.Event()
        self.__class__.instances.append(self)

    def request_interrupt(self):
        super().request_interrupt()
        self.release_event.set()

    def run(self):
        self.started_event.set()
        self.release_event.wait(2)
        self.emit_success(["settled result"])


class LightHost(QMainWindow):
    _close_tab = MainWindow._close_tab

    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tool_tabs = {}

    def _restore_window_flags(self):
        return None

    def _save_tab_state(self):
        return None


@pytest.fixture(autouse=True)
def isolated_threads(monkeypatch, qtbot):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    ControlledWorker.instances = []
    yield
    for worker in ControlledWorker.instances:
        if isValid(worker):
            worker.request_interrupt()
    qtbot.waitUntil(
        lambda: all(not isValid(worker) or not worker.isRunning() for worker in ControlledWorker.instances),
        timeout=3000,
    )
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def build_dock(monkeypatch, tmp_path, parent=None):
    monkeypatch.setattr("src.gui.ai_processor_dock.AIProcessorWorker", ControlledWorker)
    monkeypatch.setattr(AIProcessorDock, "show_warning", lambda *_args: None)
    dock = AIProcessorDock(parent)
    target = tmp_path / "input.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("content", encoding="utf-8")
    dock.ed_prompt.setPlainText("summarize")
    dock.path_entries[0].ed_path.setText(str(target))
    dock.path_entries[0].chk_is_file.setChecked(True)
    monkeypatch.setattr(dock, "_get_client", lambda: object())
    monkeypatch.setattr(dock, "show_error", lambda *_args: None)
    monkeypatch.setattr(dock, "notify_processing_completed", lambda: False)
    return dock


def test_processing_is_registered_and_one_operation_per_dock(monkeypatch, tmp_path, qtbot):
    dock = build_dock(monkeypatch, tmp_path)
    completion_threads = []
    monkeypatch.setattr(
        dock,
        "_on_finished",
        lambda _result: completion_threads.append(QThread.currentThread()),
    )
    try:
        dock._process()
        first = ControlledWorker.instances[-1]
        qtbot.waitUntil(first.started_event.is_set, timeout=2000)
        assert thread_manager.get_active_threads()[FeatureType.AI_FILE_PROCESSOR] == 1

        dock._process()
        assert ControlledWorker.instances == [first]

        first.release_event.set()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        assert completion_threads == [QCoreApplication.instance().thread()]
    finally:
        dock.deleteLater()


def test_separate_docks_own_independent_workers(monkeypatch, tmp_path, qtbot):
    first_dock = build_dock(monkeypatch, tmp_path / "first")
    second_dock = build_dock(monkeypatch, tmp_path / "second")
    try:
        first_dock._process()
        second_dock._process()
        qtbot.waitUntil(lambda: len(ControlledWorker.instances) == 2, timeout=2000)
        assert thread_manager.get_active_threads()[FeatureType.AI_FILE_PROCESSOR] == 2
        for worker in ControlledWorker.instances:
            worker.release_event.set()
        qtbot.waitUntil(
            lambda: first_dock.worker is None and second_dock.worker is None,
            timeout=3000,
        )
    finally:
        first_dock.deleteLater()
        second_dock.deleteLater()


def test_tab_close_waits_for_settlement_and_discards_late_result(monkeypatch, tmp_path, qtbot):
    host = LightHost()
    dock = build_dock(monkeypatch, tmp_path, host)
    visible_results = []
    monkeypatch.setattr(dock, "_on_finished", visible_results.append)
    host.tabs.addTab(dock, "AI Processor")
    dock._process()
    worker = ControlledWorker.instances[-1]
    qtbot.waitUntil(worker.started_event.is_set, timeout=2000)

    host._close_tab(0)
    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(dock), timeout=3000)
    assert not visible_results
    assert not thread_manager._threads

    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_tab_close_waits_for_embedded_panel_settlement(monkeypatch, tmp_path, qtbot):
    host = LightHost()
    dock = build_dock(monkeypatch, tmp_path, host)
    host.tabs.addTab(dock, "AI Processor")
    child_state = {"active": True, "shutdown_requests": 0}

    monkeypatch.setattr(
        dock.search_replace_panel,
        "has_active_operation",
        lambda: child_state["active"],
    )

    def settle_child():
        child_state["shutdown_requests"] += 1
        QTimer.singleShot(25, lambda: child_state.update(active=False))
        return True

    monkeypatch.setattr(
        dock.search_replace_panel,
        "request_parent_shutdown",
        settle_child,
    )

    host._close_tab(0)

    assert child_state["shutdown_requests"] == 1
    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(dock), timeout=3000)

    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
