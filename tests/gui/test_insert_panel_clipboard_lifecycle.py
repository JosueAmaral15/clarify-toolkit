"""Lifecycle regressions for InsertPanel result clipboard work."""

# pylint: disable=no-name-in-module,protected-access

import threading

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

import src.gui.panels.result_export as export_module
from src.gui.panels.insert_panel import InsertPanel
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


def test_embedded_insert_copy_uses_owner_worker_and_gui_clipboard(qtbot, monkeypatch, tmp_path):
    panel = InsertPanel()
    qtbot.addWidget(panel)
    panel.results.populate({str(tmp_path / "source.txt"): [(2, 3, "needle")]})
    expected = panel.results.export_to_text()
    threads = []
    original_lines = export_module.iter_match_result_lines

    def observed_lines(matches):
        threads.append(QThread.currentThread())
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", observed_lines)
    panel.results._copy_all()
    qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

    assert threads and threads[0] is not QCoreApplication.instance().thread()
    assert QApplication.clipboard().text() == expected
    assert not thread_manager._threads
