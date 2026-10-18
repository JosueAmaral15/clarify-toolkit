"""FileExplorerDock lifecycle regressions for result-file content copying."""

# pylint: disable=no-name-in-module,protected-access

import threading
from threading import Event

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.panels.result_export import (
    MatchContentClipboardPlan,
    MatchContentClipboardResult,
    MatchContentClipboardStats,
)
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
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")
    dock = FileExplorerDock()
    qtbot.addWidget(dock)
    dock.results_tree.populate({str(source): [(1, 0, "content")]})
    return dock, source


def test_file_explorer_content_copy_reads_off_gui_and_logs(qtbot, monkeypatch, tmp_path):
    dock, source = build_dock(qtbot, tmp_path)
    threads = []
    original_execute = MatchContentClipboardPlan.execute

    def observed_execute(plan, checkpoint):
        threads.append(QThread.currentThread())
        return original_execute(plan, checkpoint)

    monkeypatch.setattr(MatchContentClipboardPlan, "execute", observed_execute)
    dock.results_tree._copy_all_content()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert threads and threads[0] is not QCoreApplication.instance().thread()
    assert QApplication.clipboard().text() == f"===== {source} =====\ncontent"
    assert "content clipboard" in dock.operation_log.toPlainText().lower()
    assert not thread_manager._threads


def test_file_explorer_close_discards_late_content(qtbot, monkeypatch, tmp_path):
    dock, _source = build_dock(qtbot, tmp_path)
    dock.show()
    entered = Event()
    release = Event()

    def delayed_execute(_plan, _checkpoint):
        entered.set()
        assert release.wait(2)
        return MatchContentClipboardResult("late content", MatchContentClipboardStats(copied=1))

    monkeypatch.setattr(MatchContentClipboardPlan, "execute", delayed_execute)
    QApplication.clipboard().setText("preserve")
    try:
        dock.results_tree._copy_all_content()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock.close()
        assert dock.isVisible()
        release.set()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
        qtbot.waitUntil(lambda: not dock.isVisible(), timeout=3000)
        assert QApplication.clipboard().text() == "preserve"
    finally:
        release.set()
