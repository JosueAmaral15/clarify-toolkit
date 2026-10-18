"""Lifecycle regressions for SearchReplacePanel result clipboard work."""

# pylint: disable=no-name-in-module,protected-access

import threading
from threading import Event, Lock

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

import src.gui.panels.result_export as export_module
from src.gui.panels.search_replace_panel import SearchReplacePanel
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


def build_panel(tmp_path, name="source.txt"):
    panel = SearchReplacePanel()
    panel.results.populate({str(tmp_path / name): [(1, 0, "needle")]})
    return panel


def test_copy_extracts_on_gui_serializes_off_gui_and_publishes(qtbot, monkeypatch, tmp_path):
    panel = build_panel(tmp_path)
    qtbot.addWidget(panel)
    expected = panel.results.export_to_text()
    extraction_threads = []
    serialization_threads = []
    original_get_matches = panel.results.get_matches_data
    original_lines = export_module.iter_match_result_lines

    def observed_get_matches():
        extraction_threads.append(QThread.currentThread())
        return original_get_matches()

    def observed_lines(matches):
        serialization_threads.append(QThread.currentThread())
        return original_lines(matches)

    monkeypatch.setattr(panel.results, "get_matches_data", observed_get_matches)
    monkeypatch.setattr(export_module, "iter_match_result_lines", observed_lines)
    QApplication.clipboard().setText("sentinel")

    panel.results._copy_all()
    qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

    gui_thread = QCoreApplication.instance().thread()
    assert extraction_threads == [gui_thread]
    assert serialization_threads and serialization_threads[0] is not gui_thread
    assert QApplication.clipboard().text() == expected
    assert "1 matches" in panel.results_status.text()
    assert not thread_manager._threads


def test_copy_gate_is_per_panel_and_rejects_overlap(qtbot, monkeypatch, tmp_path):
    first = build_panel(tmp_path, "first.txt")
    second = build_panel(tmp_path, "second.txt")
    qtbot.addWidget(first)
    qtbot.addWidget(second)
    entered = Event()
    release = Event()
    lock = Lock()
    active = {"count": 0}
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        with lock:
            active["count"] += 1
            if active["count"] == 2:
                entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)
    try:
        first.results._copy_all()
        second.results._copy_all()
        qtbot.waitUntil(entered.is_set, timeout=3000)
        first_thread = first._save_thread

        first.results._copy_all()

        assert first._save_thread is first_thread
        assert "already running" in first.results_status.text()
        assert thread_manager.get_active_threads()[FeatureType.SEARCH_REPLACE] == 2
        release.set()
        qtbot.waitUntil(
            lambda: first._save_thread is None and second._save_thread is None,
            timeout=3000,
        )
    finally:
        release.set()


def test_close_cancels_copy_and_discards_late_clipboard(qtbot, monkeypatch, tmp_path):
    panel = build_panel(tmp_path)
    qtbot.addWidget(panel)
    panel.show()
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
        panel.results._copy_all()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        panel.close()
        assert panel.isVisible()
        release.set()
        qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)
        qtbot.waitUntil(lambda: not panel.isVisible(), timeout=3000)
        assert QApplication.clipboard().text() == "preserve"
    finally:
        release.set()
