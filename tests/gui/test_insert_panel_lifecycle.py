"""Lifecycle regressions for InsertPanel background searches."""

# pylint: disable=no-name-in-module,protected-access

import time
from threading import Event, Thread
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from src.core import SearchOptions
from src.gui.panels.insert_panel import InsertPanel
from src.gui.panels.search_worker import SearchWorker
from src.gui.window_settings import WindowSettings
from src.ui import FeatureType, thread_manager
from src.ui.thread_manager import ThreadInfo


@pytest.fixture(autouse=True)
def clean_thread_manager(qtbot):
    """Keep the singleton registry isolated across lifecycle tests."""
    thread_manager.resume_registration()
    assert not thread_manager._threads
    yield
    for thread_id, info in list(thread_manager._threads.items()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.wait(2000)
        else:
            thread_manager._on_thread_finished(thread_id, info.completion_token)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=2000)
    thread_manager.resume_registration()


def configure_search(panel, root, value="needle"):
    panel.ed_path.setText(str(root))
    panel.ed_extensions.setText(".txt")
    field, operator, text = panel.cond_list[0][:3]
    field.setCurrentText("content")
    operator.setCurrentText("contains")
    text.setText(value)
    panel._debounce_timer.stop()


def test_search_uses_gui_snapshot_and_worker_thread(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panel = InsertPanel()
    qtbot.addWidget(panel)
    configure_search(panel, tmp_path)
    worker_thread_matches = []
    original_read = __import__("src.gui.panels.search_worker", fromlist=["read_text"]).read_text

    def observed_read(path):
        worker_thread_matches.append(QThread.currentThread() is panel._search_thread)
        return original_read(path)

    monkeypatch.setattr("src.gui.panels.search_worker.read_text", observed_read)
    panel._iter_files = Mock(side_effect=AssertionError("widgets must not be read by the worker"))

    panel._start_search_threaded()
    native = panel._search_thread

    assert native is not None
    assert thread_manager.is_feature_running(FeatureType.INSERT)
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    assert worker_thread_matches == [True]
    assert panel.results.get_matches_data()


def test_legacy_settings_prefix_is_not_used_as_progress_manager():
    panel = InsertPanel(None, "json_editor_insert")

    assert panel.settings_prefix == "json_editor_insert"
    assert panel.progress_manager is None


def test_cancel_wakes_a_paused_worker():
    worker = SearchWorker(
        SearchOptions(False, False, False).compile("needle"),
        lambda: ["unused.txt"],
        SearchOptions,
        search_mode="filename_only",
    )
    worker.pause()
    native = Thread(target=worker.run)
    native.start()
    time.sleep(0.05)

    assert native.is_alive()
    worker.cancel()
    native.join(timeout=1)

    assert not native.is_alive()
    assert worker.is_cancelled


def test_discovery_limit_reports_error_without_reading_files():
    worker = SearchWorker(
        SearchOptions(False, False, False).compile("needle"),
        lambda: ["one.txt", "two.txt"],
        SearchOptions,
        search_mode="filename_only",
    )
    worker.MAX_DISCOVERED_FILES = 1
    errors = []
    results = []
    worker.error.connect(errors.append)
    worker.done.connect(results.append)

    worker.run()

    assert errors == ["Search exceeds the 1-file safety limit"]
    assert results == [{}]


def test_cancel_waits_for_settlement_and_blocks_reuse(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panel = InsertPanel()
    qtbot.addWidget(panel)
    configure_search(panel, tmp_path)
    entered = Event()

    def blocking_read(_path):
        entered.set()
        while not panel._search_worker.is_cancelled:
            time.sleep(0.005)
        return "needle"

    monkeypatch.setattr("src.gui.panels.search_worker.read_text", blocking_read)
    panel._start_search_threaded()
    worker = panel._search_worker
    native = panel._search_thread
    qtbot.waitUntil(entered.is_set, timeout=2000)
    native.terminate = Mock(side_effect=AssertionError("terminate must not be called"))

    panel._start_search_threaded()

    assert panel._search_worker is worker
    assert panel.processing_search
    assert not panel.btn_browse.isEnabled()
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    native.terminate.assert_not_called()
    assert panel.btn_browse.isEnabled()


def test_two_panels_have_independent_operations(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panels = [InsertPanel(), InsertPanel()]
    for panel in panels:
        qtbot.addWidget(panel)
        configure_search(panel, tmp_path)
    entered = Event()
    calls = []

    def blocking_read(_path):
        calls.append(QThread.currentThread())
        if len(calls) == 2:
            entered.set()
        while not all(panel._search_worker.is_cancelled for panel in panels):
            time.sleep(0.005)
        return "needle"

    monkeypatch.setattr("src.gui.panels.search_worker.read_text", blocking_read)
    for panel in panels:
        panel._start_search_threaded()

    qtbot.waitUntil(entered.is_set, timeout=3000)
    assert thread_manager.get_active_threads()[FeatureType.INSERT] == 2
    assert panels[0]._search_thread is not panels[1]._search_thread
    for panel in panels:
        panel.cancel_search()
    qtbot.waitUntil(lambda: all(panel._search_thread is None for panel in panels), timeout=3000)


def test_tab_close_waits_for_search_settlement(tmp_path, qtbot, monkeypatch):
    class Host(QMainWindow):
        def __init__(self):
            super().__init__()
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)

        def _close_tab(self, index):
            widget = self.tabs.widget(index)
            if hasattr(widget, "request_tab_close") and not widget.request_tab_close():
                return
            self.tabs.removeTab(index)

    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    host = Host()
    panel = InsertPanel(host)
    configure_search(panel, tmp_path)
    host.tabs.addTab(panel, "Insert")
    host.show()
    qtbot.addWidget(host)
    entered = Event()

    def blocking_read(_path):
        entered.set()
        while not panel._search_worker.is_cancelled:
            time.sleep(0.005)
        return "needle"

    monkeypatch.setattr("src.gui.panels.search_worker.read_text", blocking_read)
    panel._start_search_threaded()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=2000)


def test_force_cleanup_preserves_insert_worker():
    native = Mock()
    native.isRunning.return_value = True
    cancelled = []
    info = ThreadInfo(native, None, FeatureType.INSERT, lambda: cancelled.append(True), False)
    info.is_running = False
    original_threads = thread_manager._threads
    try:
        thread_manager._threads = {"insert": info}
        thread_manager.force_cleanup()
        assert cancelled == [True]
        native.terminate.assert_not_called()
        assert thread_manager._threads == {"insert": info}
    finally:
        thread_manager._threads = original_threads


def test_app_close_refuses_force_termination_for_insert(monkeypatch):
    class Settings:
        @staticmethod
        def get(key, default=None):
            if key == "confirm_on_exit":
                return False
            return default

    host = QMainWindow()
    host.settings = Settings()
    event = QCloseEvent()
    monkeypatch.setattr(thread_manager, "get_active_threads", lambda: {FeatureType.INSERT: 1})

    def timeout(**_kwargs):
        thread_manager._shutdown = True
        return False

    monkeypatch.setattr(thread_manager, "wait_all_threads", timeout)
    monkeypatch.setattr(
        thread_manager,
        "is_feature_running",
        lambda feature: feature == FeatureType.INSERT,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *_args: QMessageBox.Yes)
    forced = []
    monkeypatch.setattr(thread_manager, "force_cleanup", lambda: forced.append(True))

    WindowSettings.handle_close_event(host, event)

    assert not event.isAccepted()
    assert not forced
    assert thread_manager._shutdown is False
