"""Focused lifecycle regressions for the Google Translate dock."""

# pylint: disable=no-name-in-module,protected-access

import time
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from src.gui.google_translate_dock import GoogleTranslateDock, TranslationWorker
from src.gui.window_settings import WindowSettings
from src.translation.google_translate import TranslationResult
from src.ui import FeatureType, thread_manager
from src.ui.thread_manager import ThreadInfo


class BlockingAPI:
    """Deterministic provider substitute that exits only after cancellation."""

    def __init__(self):
        self.entered = False

    def translate_text_chunked(self, *_args, cancel_callback=None, **_kwargs):
        self.entered = True
        while not cancel_callback():
            QThread.msleep(5)
        return TranslationResult(success=False, error_message="Translation cancelled")

    @staticmethod
    def get_cache_info():
        return {"entries": 0, "file_size_bytes": 0}


@pytest.fixture(autouse=True)
def clean_thread_manager(qtbot):
    """Keep the singleton registry isolated across lifecycle tests."""
    thread_manager.resume_registration()
    assert not thread_manager._threads
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.wait(2000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=2000)
    thread_manager.resume_registration()


def test_worker_suppresses_late_result_after_cancel():
    api = Mock()
    worker = TranslationWorker(api, "Hello", "en", "pt")

    def complete_after_cancel(*_args, **_kwargs):
        worker.cancel()
        return TranslationResult(
            success=True,
            translated_text="late result",
            source_language="en",
            target_language="pt",
        )

    api.translate_text_chunked.side_effect = complete_after_cancel
    worker.translation_completed = Mock()
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(time, "sleep", lambda _seconds: None)
        worker.run()

    worker.translation_completed.emit.assert_not_called()
    assert api.translate_text_chunked.call_args.kwargs["cancel_callback"]()


def test_cancel_is_cooperative_and_settles_before_reuse(qtbot):
    dock = GoogleTranslateDock()
    dock.api = BlockingAPI()
    dock.show()
    qtbot.addWidget(dock)

    dock._start_translation("Hello", "en", "pt")
    worker = dock.translation_worker
    qtbot.waitUntil(lambda: dock.api.entered, timeout=2000)
    assert thread_manager.is_feature_running(FeatureType.GOOGLE_TRANSLATE)

    dock._start_translation("second", "en", "pt")
    assert dock.translation_worker is worker

    terminate = Mock(side_effect=AssertionError("terminate must not be called"))
    worker.terminate = terminate
    dock._cancel_translation()
    assert not dock.btn_translate.isEnabled()
    assert not dock.btn_cancel.isEnabled()

    qtbot.waitUntil(lambda: dock.translation_worker is None, timeout=2000)
    qtbot.waitUntil(
        lambda: not thread_manager.is_feature_running(FeatureType.GOOGLE_TRANSLATE),
        timeout=2000,
    )
    terminate.assert_not_called()
    assert dock.btn_translate.isEnabled()


def test_close_is_deferred_until_worker_stops(qtbot):
    dock = GoogleTranslateDock()
    dock.api = BlockingAPI()
    dock.show()
    qtbot.addWidget(dock)

    dock._start_translation("Hello", "en", "pt")
    qtbot.waitUntil(lambda: dock.api.entered, timeout=2000)
    worker = dock.translation_worker
    worker.terminate = Mock(side_effect=AssertionError("terminate must not be called"))

    dock.close()
    assert dock.isVisible()
    assert dock.translation_worker is worker
    qtbot.waitUntil(lambda: dock.translation_worker is None, timeout=2000)
    qtbot.waitUntil(lambda: not dock.isVisible(), timeout=2000)
    worker.terminate.assert_not_called()


def test_tab_close_is_retried_after_worker_stops(qtbot):
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

    host = Host()
    dock = GoogleTranslateDock(host)
    dock.api = BlockingAPI()
    host.tabs.addTab(dock, "Google Translate")
    host.show()
    qtbot.addWidget(host)

    dock._start_translation("Hello", "en", "pt")
    qtbot.waitUntil(lambda: dock.api.entered, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: dock.translation_worker is None, timeout=2000)
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=2000)


def test_app_close_refuses_force_termination_for_translation(monkeypatch):
    host = QMainWindow()
    event = QCloseEvent()
    monkeypatch.setattr(
        thread_manager,
        "get_active_threads",
        lambda: {FeatureType.GOOGLE_TRANSLATE: 1},
    )

    def timeout(**_kwargs):
        thread_manager._shutdown = True
        return False

    monkeypatch.setattr(thread_manager, "wait_all_threads", timeout)
    monkeypatch.setattr(
        thread_manager,
        "is_feature_running",
        lambda feature: feature == FeatureType.GOOGLE_TRANSLATE,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *_args: QMessageBox.Yes)
    forced = []
    monkeypatch.setattr(thread_manager, "force_cleanup", lambda: forced.append(True))

    WindowSettings.handle_close_event(host, event)

    assert not event.isAccepted()
    assert not forced
    assert thread_manager._shutdown is False


def test_force_cleanup_preserves_google_translate_worker():
    native = Mock()
    native.isRunning.return_value = True
    cancelled = []
    info = ThreadInfo(
        native,
        None,
        FeatureType.GOOGLE_TRANSLATE,
        lambda: cancelled.append(True),
        False,
    )
    info.is_running = False
    original_threads = thread_manager._threads
    try:
        thread_manager._threads = {"google": info}
        thread_manager.force_cleanup()

        assert cancelled == [True]
        native.terminate.assert_not_called()
        assert thread_manager._threads == {"google": info}
    finally:
        thread_manager._threads = original_threads
