"""Lifecycle regressions for FileExplorerDock result clipboard work."""

# pylint: disable=no-name-in-module,protected-access

import threading
from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

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


def build_dock(qtbot, tmp_path):
    dock = FileExplorerDock()
    qtbot.addWidget(dock)
    dock.results_tree.populate({str(tmp_path / "source.txt"): [(1, 0, "needle")]})
    return dock


def test_file_explorer_copy_serializes_off_gui_and_logs_completion(qtbot, monkeypatch, tmp_path):
    dock = build_dock(qtbot, tmp_path)
    expected = dock.results_tree.export_to_text()
    threads = []
    original_lines = export_module.iter_match_result_lines

    def observed_lines(matches):
        threads.append(QThread.currentThread())
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", observed_lines)
    dock.results_tree._copy_all()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert threads and threads[0] is not QCoreApplication.instance().thread()
    assert QApplication.clipboard().text() == expected
    assert "clipboard" in dock.operation_log.toPlainText().lower()
    assert not thread_manager._threads


def test_file_explorer_close_cancels_copy_without_late_publication(qtbot, monkeypatch, tmp_path):
    dock = build_dock(qtbot, tmp_path)
    dock.show()
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)
    QApplication.clipboard().setText("preserve")
    try:
        dock.results_tree._copy_all()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock.close()
        assert dock.isVisible()
        release.set()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
        qtbot.waitUntil(lambda: not dock.isVisible(), timeout=3000)
        assert QApplication.clipboard().text() == "preserve"
    finally:
        release.set()
