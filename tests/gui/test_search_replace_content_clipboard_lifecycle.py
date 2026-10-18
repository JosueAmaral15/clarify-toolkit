"""SearchReplacePanel lifecycle regressions for result-file content copying."""

# pylint: disable=no-name-in-module,protected-access

import threading
from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

from src.gui.panels.result_export import (
    MatchContentClipboardPlan,
    MatchContentClipboardResult,
    MatchContentClipboardStats,
)
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


def build_panel(qtbot, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("alpha", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    panel.results.populate({str(source): [(1, 0, "alpha")]})
    return panel, source


def test_content_copy_snapshots_on_gui_reads_off_gui_and_publishes(qtbot, monkeypatch, tmp_path):
    panel, source = build_panel(qtbot, tmp_path)
    snapshot_threads = []
    worker_threads = []
    original_get_matches = panel.results.get_matches_data
    original_execute = MatchContentClipboardPlan.execute

    def observed_get_matches():
        snapshot_threads.append(QThread.currentThread())
        return original_get_matches()

    def observed_execute(plan, checkpoint):
        worker_threads.append(QThread.currentThread())
        return original_execute(plan, checkpoint)

    monkeypatch.setattr(panel.results, "get_matches_data", observed_get_matches)
    monkeypatch.setattr(MatchContentClipboardPlan, "execute", observed_execute)
    QApplication.clipboard().setText("sentinel")

    panel.results._copy_all_content()
    qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

    gui_thread = QCoreApplication.instance().thread()
    assert snapshot_threads == [gui_thread]
    assert worker_threads and worker_threads[0] is not gui_thread
    assert QApplication.clipboard().text() == f"===== {source} =====\nalpha"
    assert "1 file(s)" in panel.results_status.text()
    assert not thread_manager._threads


def test_content_copy_close_discards_late_publication(qtbot, monkeypatch, tmp_path):
    panel, _source = build_panel(qtbot, tmp_path)
    panel.show()
    entered = Event()
    release = Event()

    def delayed_execute(_plan, _checkpoint):
        entered.set()
        assert release.wait(2)
        return MatchContentClipboardResult("late content", MatchContentClipboardStats(copied=1))

    monkeypatch.setattr(MatchContentClipboardPlan, "execute", delayed_execute)
    QApplication.clipboard().setText("preserve")
    try:
        panel.results._copy_all_content()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        panel.close()
        assert panel.isVisible()
        release.set()
        qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)
        qtbot.waitUntil(lambda: not panel.isVisible(), timeout=3000)
        assert QApplication.clipboard().text() == "preserve"
    finally:
        release.set()
