"""Lifecycle regressions for Format Converter extraction workers."""

# pylint: disable=no-name-in-module,protected-access

import time
from threading import Event
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from src.gui.extraction_worker import ExtractionWorker
from src.gui.unified_text_to_json_dock import UnifiedTextToJsonDock
from src.gui.window_settings import WindowSettings
from src.ui import FeatureType, thread_manager
from src.ui.thread_manager import ThreadInfo


class StubExtractor:
    """Minimal extractor contract for direct worker tests."""

    file_extensions = [".txt"]
    convert_to_json = True

    @staticmethod
    def process_text(_root, _text):
        return ["Root.value"], {"Root": {"value": "sample"}}

    @staticmethod
    def deep_merge(left, right):
        return {**left, **right}

    @staticmethod
    def json_to_js_literal(data, indent=2):
        del indent
        return str(data)


@pytest.fixture(autouse=True)
def clean_thread_manager(qtbot):
    thread_manager.resume_registration()
    assert not thread_manager._threads
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.wait(2000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=2000)
    thread_manager.resume_registration()


def configure_file_extraction(dock, path):
    dock.jsx_input_type_combo.setCurrentIndex(1)
    dock.jsx_path_edit.setText(str(path))
    dock.show_info = Mock()
    dock.notify_processing_completed = Mock(return_value=False)


def test_worker_cancel_before_text_suppresses_result():
    worker = ExtractionWorker(StubExtractor())
    finished = []
    cancelled = []
    worker.finished.connect(lambda *_args: finished.append(True))
    worker.cancelled.connect(lambda: cancelled.append(True))

    worker.cancel()
    worker.execute_extraction(text_content="sample", input_type_index=2)

    assert cancelled == [True]
    assert not finished


def test_worker_rejects_directory_over_file_limit(tmp_path, monkeypatch):
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    worker = ExtractionWorker(StubExtractor())
    errors = []
    finished = []
    worker.error.connect(errors.append)
    worker.finished.connect(lambda *_args: finished.append(True))
    monkeypatch.setattr(worker, "MAX_DISCOVERED_FILES", 1)

    worker.execute_extraction(path=str(tmp_path), input_type_index=0)

    assert errors == ["Extraction exceeds the 1-file safety limit"]
    assert not finished


def test_normal_extraction_settles_and_reenables_dock(tmp_path, qtbot):
    source = tmp_path / "sample.txt"
    source.write_text('<div title="Sample">Body</div>', encoding="utf-8")
    dock = UnifiedTextToJsonDock()
    configure_file_extraction(dock, source)
    qtbot.addWidget(dock)

    dock._jsx_run_extraction()

    assert not dock.jsx_run_btn.isEnabled()
    assert thread_manager.is_feature_running(FeatureType.TEXT_EXTRACTOR)
    qtbot.waitUntil(lambda: dock._extraction_thread is None, timeout=3000)
    qtbot.waitUntil(
        lambda: not thread_manager.is_feature_running(FeatureType.TEXT_EXTRACTOR),
        timeout=2000,
    )
    assert dock.jsx_run_btn.isEnabled()
    assert dock.jsx_paths_output.toPlainText()


def test_cancel_is_cooperative_and_blocks_reuse(tmp_path, qtbot, monkeypatch):
    source = tmp_path / "sample.txt"
    source.write_text("sample", encoding="utf-8")
    dock = UnifiedTextToJsonDock()
    configure_file_extraction(dock, source)
    qtbot.addWidget(dock)
    entered = Event()
    worker_threads = []

    def blocking_read(_path):
        worker_threads.append(QThread.currentThread())
        entered.set()
        while not dock._extraction_worker.is_cancelled:
            time.sleep(0.005)
        return "sample"

    monkeypatch.setattr("src.extractors.advanced_extractor.read_text", blocking_read)
    dock._jsx_run_extraction()
    worker = dock._extraction_worker
    native = dock._extraction_thread
    qtbot.waitUntil(entered.is_set, timeout=2000)
    assert worker_threads == [native]

    dock._jsx_run_extraction()
    assert dock._extraction_worker is worker
    native.terminate = Mock(side_effect=AssertionError("terminate must not be called"))
    dock._on_extraction_canceled()

    assert not dock.jsx_run_btn.isEnabled()
    qtbot.waitUntil(lambda: dock._extraction_thread is None, timeout=3000)
    native.terminate.assert_not_called()
    assert dock.jsx_run_btn.isEnabled()


def test_tab_close_waits_for_native_settlement(tmp_path, qtbot, monkeypatch):
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
    source.write_text("sample", encoding="utf-8")
    host = Host()
    dock = UnifiedTextToJsonDock(host)
    configure_file_extraction(dock, source)
    host.tabs.addTab(dock, "Format Converter")
    host.show()
    qtbot.addWidget(host)
    entered = Event()

    def blocking_read(_path):
        entered.set()
        while not dock._extraction_worker.is_cancelled:
            time.sleep(0.005)
        return "sample"

    monkeypatch.setattr("src.extractors.advanced_extractor.read_text", blocking_read)
    dock._jsx_run_extraction()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: dock._extraction_thread is None, timeout=3000)
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=2000)


def test_force_cleanup_preserves_text_extractor_worker():
    native = Mock()
    native.isRunning.return_value = True
    cancelled = []
    info = ThreadInfo(
        native,
        None,
        FeatureType.TEXT_EXTRACTOR,
        lambda: cancelled.append(True),
        False,
    )
    info.is_running = False
    original_threads = thread_manager._threads
    try:
        thread_manager._threads = {"extractor": info}
        thread_manager.force_cleanup()
        assert cancelled == [True]
        native.terminate.assert_not_called()
        assert thread_manager._threads == {"extractor": info}
    finally:
        thread_manager._threads = original_threads


def test_app_close_refuses_force_termination_for_extractor(monkeypatch):
    host = QMainWindow()
    event = QCloseEvent()
    monkeypatch.setattr(
        thread_manager,
        "get_active_threads",
        lambda: {FeatureType.TEXT_EXTRACTOR: 1},
    )

    def timeout(**_kwargs):
        thread_manager._shutdown = True
        return False

    monkeypatch.setattr(thread_manager, "wait_all_threads", timeout)
    monkeypatch.setattr(
        thread_manager,
        "is_feature_running",
        lambda feature: feature == FeatureType.TEXT_EXTRACTOR,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *_args: QMessageBox.Yes)
    forced = []
    monkeypatch.setattr(thread_manager, "force_cleanup", lambda: forced.append(True))

    WindowSettings.handle_close_event(host, event)

    assert not event.isAccepted()
    assert not forced
    assert thread_manager._shutdown is False


def test_app_close_waits_for_real_cooperative_extractor(tmp_path, qtbot, monkeypatch):
    class Settings:
        def __init__(self):
            self.values = {}

        def get(self, key, default=None):
            if key == "confirm_on_exit":
                return False
            return self.values.get(key, default)

        def set(self, key, value):
            self.values[key] = value

    source = tmp_path / "sample.txt"
    source.write_text("sample", encoding="utf-8")
    host = QMainWindow()
    host.settings = Settings()
    dock = UnifiedTextToJsonDock(host)
    configure_file_extraction(dock, source)
    entered = Event()

    def blocking_read(_path):
        entered.set()
        while not dock._extraction_worker.is_cancelled:
            time.sleep(0.005)
        return "sample"

    monkeypatch.setattr("src.extractors.advanced_extractor.read_text", blocking_read)
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Yes)
    dock._jsx_run_extraction()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    event = QCloseEvent()

    WindowSettings.handle_close_event(host, event)

    assert event.isAccepted()
    qtbot.waitUntil(lambda: dock._extraction_thread is None, timeout=2000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=2000)
