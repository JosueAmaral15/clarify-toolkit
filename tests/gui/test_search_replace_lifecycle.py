"""Lifecycle regressions for SearchReplacePanel background searches."""

# pylint: disable=no-name-in-module,protected-access

import time
from dataclasses import FrozenInstanceError
from threading import Event
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from src.gui.panels.search_replace_panel import SearchReplacePanel
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


def configure_search(panel, root, query="needle"):
    panel.ed_path.setText(str(root))
    panel.ed_extensions.setText(".txt")
    panel.ed_query.setPlainText(query)


def test_valid_search_uses_gui_snapshot_and_worker_thread(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panel = SearchReplacePanel()
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

    assert panel._search_thread is not None
    assert thread_manager.is_feature_running(FeatureType.SEARCH_REPLACE)
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    assert worker_thread_matches == [True]
    assert panel.results.get_matches_data()


def test_invalid_regex_fails_before_thread_without_missing_signals(qtbot):
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    panel.ed_path.setText("/unused")
    panel.ed_query.setPlainText("[")
    panel.chk_regex.setChecked(True)

    panel._start_search_threaded()

    assert panel._search_thread is None
    assert not panel.processing_search


def test_condition_snapshot_is_immutable_and_independent(tmp_path, qtbot):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_search(panel, tmp_path)
    field, operator, value = panel.cond_list[0][:3]
    field.setCurrentText("content")
    operator.setCurrentText("contains")
    value.setText("needle")

    request = panel._snapshot_search_request()
    value.setText("changed-after-snapshot")

    with pytest.raises(FrozenInstanceError):
        request.conditions[0].value = "mutable"
    assert list(request.iter_files()) == [str(source)]


def test_cancel_waits_for_settlement_and_blocks_reuse(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panel = SearchReplacePanel()
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
    assert not panel.btn_replace_all.isEnabled()
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    native.terminate.assert_not_called()
    assert panel.btn_replace_all.isEnabled()


def test_two_panels_have_independent_operations(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("needle", encoding="utf-8")
    panels = [SearchReplacePanel(), SearchReplacePanel()]
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
    assert thread_manager.get_active_threads()[FeatureType.SEARCH_REPLACE] == 2
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
    panel = SearchReplacePanel(host)
    configure_search(panel, tmp_path)
    host.tabs.addTab(panel, "Search/Replace")
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


def test_legacy_settings_prefix_is_not_used_as_progress_manager():
    panel = SearchReplacePanel(None, "ai_processor_search_replace")

    assert panel.settings_prefix == "ai_processor_search_replace"
    assert panel.progress_manager is None


def test_force_cleanup_preserves_search_replace_worker():
    native = Mock()
    native.isRunning.return_value = True
    cancelled = []
    info = ThreadInfo(
        native,
        None,
        FeatureType.SEARCH_REPLACE,
        lambda: cancelled.append(True),
        False,
    )
    info.is_running = False
    original_threads = thread_manager._threads
    try:
        thread_manager._threads = {"search-replace": info}
        thread_manager.force_cleanup()
        assert cancelled == [True]
        native.terminate.assert_not_called()
        assert thread_manager._threads == {"search-replace": info}
    finally:
        thread_manager._threads = original_threads


def test_app_close_refuses_force_termination_for_search_replace(monkeypatch):
    class Settings:
        values = {}

        @staticmethod
        def get(key, default=None):
            if key == "confirm_on_exit":
                return False
            return default

        @classmethod
        def set(cls, key, value):
            cls.values[key] = value

    host = QMainWindow()
    host.settings = Settings()
    event = QCloseEvent()
    monkeypatch.setattr(
        thread_manager,
        "get_active_threads",
        lambda: {FeatureType.SEARCH_REPLACE: 1},
    )

    def timeout(**_kwargs):
        thread_manager._shutdown = True
        return False

    monkeypatch.setattr(thread_manager, "wait_all_threads", timeout)
    monkeypatch.setattr(
        thread_manager,
        "is_feature_running",
        lambda feature: feature == FeatureType.SEARCH_REPLACE,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *_args: QMessageBox.Yes)
    forced = []
    monkeypatch.setattr(thread_manager, "force_cleanup", lambda: forced.append(True))

    WindowSettings.handle_close_event(host, event)

    assert not event.isAccepted()
    assert not forced
    assert thread_manager._shutdown is False
