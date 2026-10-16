"""Lifecycle regressions for AI Processor result saving."""

# pylint: disable=no-name-in-module  # Qt and Shiboken expose dynamic bindings.

from dataclasses import FrozenInstanceError
from threading import Event, Lock
import time

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread
from PySide6.QtWidgets import QMainWindow, QTabWidget
from shiboken6 import isValid

from src.ai_processor.processor import save_results
from src.app import MainWindow
import src.gui.ai_processor_dock as dock_module
from src.gui.ai_processor_dock import AIProcessorDock
import src.gui.workers.ai_processor_worker as worker_module
from src.ui import FeatureType, thread_manager


class LightHost(QMainWindow):
    """Minimal owner exercising the production tab-close contract."""

    _close_tab = MainWindow._close_tab

    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tool_tabs = {}

    def _restore_window_flags(self):
        return None

    def _save_tab_state(self):
        return None


@pytest.fixture(autouse=True)
def isolated_threads(monkeypatch, qtbot):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.wait(3000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def build_dock(monkeypatch, parent=None):
    """Create a provider-free dock and capture user-facing feedback."""
    dock = AIProcessorDock(parent)
    dock.last_responses = ["alpha", "beta"]
    feedback = {"info": [], "warning": [], "error": []}
    monkeypatch.setattr(dock, "show_info", lambda *args: feedback["info"].append(args))
    monkeypatch.setattr(
        dock,
        "show_warning",
        lambda *args: feedback["warning"].append(args),
    )
    monkeypatch.setattr(
        dock,
        "show_error",
        lambda *args: feedback["error"].append(args),
    )
    return dock, feedback


def select_path(monkeypatch, output_path):
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(output_path), "Text files (*.txt)"),
    )


def test_result_save_write_runs_off_gui_thread(monkeypatch, qtbot, tmp_path):
    dock, feedback = build_dock(monkeypatch)
    output_path = tmp_path / "results.txt"
    select_path(monkeypatch, output_path)
    save_threads = []

    def observed_save(*_args, **_kwargs):
        save_threads.append(QThread.currentThread())
        return True

    monkeypatch.setattr(worker_module, "save_results", observed_save)

    try:
        dock._save_results()
        qtbot.waitUntil(lambda: dock._result_save_worker is None, timeout=3000)

        assert save_threads
        assert save_threads[0] is not QCoreApplication.instance().thread()
        assert feedback["info"] == [("Saved", f"Results saved to {output_path}")]
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_shared_save_results_format_and_interrupt_contract(tmp_path):
    complete_path = tmp_path / "complete.txt"
    assert save_results(("alpha", "beta"), str(complete_path)) is True
    assert complete_path.read_text(encoding="utf-8") == ("=== Result 1 ===\nalpha\n\n=== Result 2 ===\nbeta\n\n")

    interrupted_path = tmp_path / "interrupted.txt"
    checks = iter((False, True))
    assert (
        save_results(
            ("alpha", "beta"),
            str(interrupted_path),
            interrupt_check=lambda: next(checks),
        )
        is False
    )
    assert interrupted_path.read_text(encoding="utf-8") == "=== Result 1 ===\nalpha\n\n"


def test_result_save_plan_is_immutable_and_bounded(monkeypatch, tmp_path):
    plan = worker_module.AIResultSavePlan(("alpha",), str(tmp_path / "results.txt"))
    with pytest.raises(FrozenInstanceError):
        plan.output_path = "changed"

    monkeypatch.setattr(worker_module, "MAX_AI_SAVE_RESULT_BYTES", 3)
    with pytest.raises(ValueError, match="4 MiB"):
        worker_module.AIResultSavePlan(("long",), str(tmp_path / "results.txt"))

    utf8_plan = worker_module.AIResultSavePlan(("éé",), str(tmp_path / "utf8.txt"))
    with pytest.raises(ValueError, match="4 MiB"):
        utf8_plan.execute(lambda: True)

    monkeypatch.setattr(worker_module, "MAX_AI_SAVE_RESULT_BYTES", 1024)
    monkeypatch.setattr(worker_module, "MAX_AI_SAVE_TOTAL_BYTES", 3)
    with pytest.raises(ValueError, match="20 MiB"):
        worker_module.AIResultSavePlan(("ab", "cd"), str(tmp_path / "total.txt"))


def test_actual_save_is_atomic_and_uses_immutable_snapshot(monkeypatch, qtbot, tmp_path):
    dock, feedback = build_dock(monkeypatch)
    output_path = tmp_path / "results.txt"
    output_path.write_text("old content", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_save = worker_module.save_results

    def blocking_save(results, path, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_save(results, path, **kwargs)

    monkeypatch.setattr(worker_module, "save_results", blocking_save)

    try:
        dock._save_results()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock.last_responses[0] = "changed"
        assert output_path.read_text(encoding="utf-8") == "old content"
        release.set()
        qtbot.waitUntil(lambda: dock._result_save_worker is None, timeout=3000)

        saved = output_path.read_text(encoding="utf-8")
        assert "alpha" in saved
        assert "changed" not in saved
        assert feedback["info"] == [("Saved", f"Results saved to {output_path}")]
    finally:
        release.set()
        dock.deleteLater()


def test_one_save_per_dock_and_independent_docks(monkeypatch, qtbot, tmp_path):
    first, first_feedback = build_dock(monkeypatch)
    second, _second_feedback = build_dock(monkeypatch)
    first_path = tmp_path / "first.txt"
    second_path = tmp_path / "second.txt"
    paths = iter((str(first_path), str(second_path)))
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (next(paths), "Text files (*.txt)"),
    )
    entered = Event()
    release = Event()
    state = {"active": 0}
    state_lock = Lock()
    original_save = worker_module.save_results

    def blocking_save(results, path, **kwargs):
        with state_lock:
            state["active"] += 1
            if state["active"] == 2:
                entered.set()
        assert release.wait(2)
        return original_save(results, path, **kwargs)

    monkeypatch.setattr(worker_module, "save_results", blocking_save)

    try:
        first._save_results()
        second._save_results()
        qtbot.waitUntil(entered.is_set, timeout=3000)
        assert thread_manager.get_active_threads()[FeatureType.AI_FILE_PROCESSOR] == 2

        first._save_results()
        assert first_feedback["warning"] == [
            (
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
        ]

        release.set()
        qtbot.waitUntil(
            lambda: first._result_save_worker is None and second._result_save_worker is None,
            timeout=3000,
        )
        assert first_path.exists()
        assert second_path.exists()
        assert not thread_manager._threads
    finally:
        release.set()
        first.deleteLater()
        second.deleteLater()


def test_cancelled_save_preserves_existing_destination(monkeypatch, qtbot, tmp_path):
    dock, feedback = build_dock(monkeypatch)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()

    def cancellable_save(_results, path, *, interrupt_check, **_kwargs):
        entered.set()
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("partial")
        while not interrupt_check():
            time.sleep(0.01)
        return False

    monkeypatch.setattr(worker_module, "save_results", cancellable_save)

    try:
        dock._save_results()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock._interrupt()
        qtbot.waitUntil(lambda: dock._result_save_worker is None, timeout=3000)

        assert output_path.read_text(encoding="utf-8") == "preserve me"
        assert feedback["info"] == [("Save Cancelled", "Result saving was cancelled.")]
        assert not list(tmp_path.glob(".clarify-ai-results-*.tmp"))
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_save_io_error_is_reported_without_replacing_destination(monkeypatch, qtbot, tmp_path):
    dock, feedback = build_dock(monkeypatch)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    monkeypatch.setattr(
        worker_module,
        "save_results",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(PermissionError("denied")),
    )

    try:
        dock._save_results()
        qtbot.waitUntil(lambda: dock._result_save_worker is None, timeout=3000)

        assert output_path.read_text(encoding="utf-8") == "preserve me"
        assert feedback["error"] == [("Save Error", "denied")]
        assert not list(tmp_path.glob(".clarify-ai-results-*.tmp"))
    finally:
        dock.deleteLater()


def test_tab_close_waits_for_save_settlement_and_discards_callbacks(
    monkeypatch,
    qtbot,
    tmp_path,
):
    host = LightHost()
    dock, feedback = build_dock(monkeypatch, host)
    host.tabs.addTab(dock, "AI Processor")
    output_path = tmp_path / "results.txt"
    select_path(monkeypatch, output_path)
    entered = Event()

    def cancellable_save(_results, _path, *, interrupt_check, **_kwargs):
        entered.set()
        while not interrupt_check():
            time.sleep(0.01)
        return False

    monkeypatch.setattr(worker_module, "save_results", cancellable_save)

    dock._save_results()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(dock), timeout=3000)
    assert not output_path.exists()
    assert not feedback["info"]
    assert not feedback["error"]
    assert not thread_manager._threads

    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_cancelled_dialog_and_invalid_results_do_not_start_worker(
    monkeypatch,
    tmp_path,
):
    dock, feedback = build_dock(monkeypatch)
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: ("", ""),
    )

    try:
        dock._save_results()
        assert dock._result_save_worker is None
        assert feedback == {"info": [], "warning": [], "error": []}

        select_path(monkeypatch, tmp_path / "invalid.txt")
        dock.last_responses = [object()]
        dock._save_results()
        assert dock._result_save_worker is None
        assert feedback["error"] == [("Save Error", "AI results must contain only text")]
    finally:
        dock.deleteLater()
