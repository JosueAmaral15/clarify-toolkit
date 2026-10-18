"""InsertPanel lifecycle regression for result-file content copying."""

# pylint: disable=no-name-in-module,protected-access

import threading

import pytest
from PySide6.QtCore import QCoreApplication, QThread
from PySide6.QtWidgets import QApplication

from src.gui.panels.result_export import MatchContentClipboardPlan
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


def test_insert_content_copy_uses_owner_worker_and_gui_clipboard(qtbot, monkeypatch, tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("content", encoding="utf-8")
    panel = InsertPanel()
    qtbot.addWidget(panel)
    panel.results.populate({str(source): [(1, 0, "content")]})
    threads = []
    original_execute = MatchContentClipboardPlan.execute

    def observed_execute(plan, checkpoint):
        threads.append(QThread.currentThread())
        return original_execute(plan, checkpoint)

    monkeypatch.setattr(MatchContentClipboardPlan, "execute", observed_execute)
    panel.results._copy_all_content()
    qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

    assert threads and threads[0] is not QCoreApplication.instance().thread()
    assert QApplication.clipboard().text() == f"===== {source} =====\ncontent"
    assert not thread_manager._threads
