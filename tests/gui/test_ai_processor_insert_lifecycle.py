"""Lifecycle regressions for AI Processor in-memory prompt insertion."""

# pylint: disable=no-name-in-module  # Qt and Shiboken expose dynamic bindings.

from dataclasses import FrozenInstanceError
from threading import Event, Lock

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread
from PySide6.QtWidgets import QMainWindow, QTabWidget
from shiboken6 import isValid

from src.app import MainWindow
from src.core.insert import InsertMode
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
    dock.ed_prompt.setPlainText("first\nsecond")
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


def request_insert(dock, line_no=2, text=" added", mode=InsertMode.RIGHT):
    dock._handle_insert_in_prompt(line_no, text, mode)


def test_prompt_insert_cpu_work_runs_off_gui_thread(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    insert_threads = []
    original_insert = worker_module.insert_at_line

    def observed_insert(*args, **kwargs):
        insert_threads.append(QThread.currentThread())
        return original_insert(*args, **kwargs)

    monkeypatch.setattr(worker_module, "insert_at_line", observed_insert)

    try:
        request_insert(dock)
        qtbot.waitUntil(lambda: dock._prompt_insert_worker is None, timeout=3000)

        assert insert_threads
        assert insert_threads[0] is not QCoreApplication.instance().thread()
        assert dock.ed_prompt.toPlainText() == "first\nsecond added"
        assert feedback["info"] == [
            (
                "Insert Complete",
                f"Inserted text at line 2 using {InsertMode.RIGHT} mode",
            )
        ]
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_prompt_insert_plan_is_immutable_and_bounded(monkeypatch):
    plan = worker_module.AIPromptInsertPlan(
        content="first\nsecond",
        line_no=2,
        text=" added",
        mode=InsertMode.RIGHT,
    )

    with pytest.raises(FrozenInstanceError):
        plan.line_no = 3

    monkeypatch.setattr(worker_module, "MAX_AI_INSERT_TEXT_BYTES", 3)
    with pytest.raises(ValueError, match="Insertion value exceeds"):
        worker_module.AIPromptInsertPlan(
            content="first",
            line_no=1,
            text="long",
            mode=InsertMode.RIGHT,
        )

    with pytest.raises(ValueError, match="Unknown insert mode"):
        worker_module.AIPromptInsertPlan(
            content="first",
            line_no=1,
            text="x",
            mode="unknown",
        )


def test_prompt_insert_plan_checks_utf8_output_and_cancellation(monkeypatch):
    utf8_plan = worker_module.AIPromptInsertPlan(
        content="éé",
        line_no=1,
        text="x",
        mode=InsertMode.RIGHT,
    )
    monkeypatch.setattr(worker_module, "MAX_AI_PROMPT_BYTES", 3)
    with pytest.raises(ValueError, match="Prompt text exceeds"):
        utf8_plan.execute(lambda: True)

    monkeypatch.setattr(worker_module, "MAX_AI_PROMPT_BYTES", 1024)
    cancelled_plan = worker_module.AIPromptInsertPlan(
        content="one",
        line_no=1,
        text=" two",
        mode=InsertMode.RIGHT,
    )
    checks = iter((True, False))
    assert cancelled_plan.execute(lambda: next(checks)) == "one"


def test_embedded_panel_emits_current_insert_contract(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    panel = dock.insert_panel
    panel.spin_line.setValue(2)
    panel.ed_text.setPlainText("!")
    panel.cb_mode.setCurrentText(InsertMode.RIGHT)

    try:
        assert panel.emit_insert_request() is True
        qtbot.waitUntil(lambda: dock._prompt_insert_worker is None, timeout=3000)

        assert dock.ed_prompt.toPlainText() == "first\nsecond!"
        assert "Inserted text at line 2" in feedback["info"][0][1]
    finally:
        dock.deleteLater()


def test_one_insert_per_dock_and_independent_docks(monkeypatch, qtbot):
    first, first_feedback = build_dock(monkeypatch)
    second, _second_feedback = build_dock(monkeypatch)
    entered = Event()
    release = Event()
    state = {"active": 0}
    state_lock = Lock()
    original_insert = worker_module.insert_at_line

    def blocking_insert(*args, **kwargs):
        with state_lock:
            state["active"] += 1
            if state["active"] == 2:
                entered.set()
        assert release.wait(2)
        return original_insert(*args, **kwargs)

    monkeypatch.setattr(worker_module, "insert_at_line", blocking_insert)

    try:
        request_insert(first)
        request_insert(second)
        qtbot.waitUntil(entered.is_set, timeout=3000)
        assert thread_manager.get_active_threads()[FeatureType.AI_FILE_PROCESSOR] == 2

        request_insert(first, text=" ignored")
        assert first_feedback["warning"] == [
            (
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
        ]

        release.set()
        qtbot.waitUntil(
            lambda: (first._prompt_insert_worker is None and second._prompt_insert_worker is None),
            timeout=3000,
        )
        assert first.ed_prompt.toPlainText() == "first\nsecond added"
        assert second.ed_prompt.toPlainText() == "first\nsecond added"
        assert not thread_manager._threads
    finally:
        release.set()
        first.deleteLater()
        second.deleteLater()


def test_cancelled_insert_does_not_apply_late_result(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    entered = Event()
    release = Event()
    original_insert = worker_module.insert_at_line

    def blocking_insert(*args, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_insert(*args, **kwargs)

    monkeypatch.setattr(worker_module, "insert_at_line", blocking_insert)

    try:
        request_insert(dock)
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock._interrupt()
        release.set()
        qtbot.waitUntil(lambda: dock._prompt_insert_worker is None, timeout=3000)

        assert dock.ed_prompt.toPlainText() == "first\nsecond"
        assert feedback["info"] == [("Insert Cancelled", "Prompt insertion was cancelled.")]
        assert not thread_manager._threads
    finally:
        release.set()
        dock.deleteLater()


def test_tab_close_waits_for_insert_settlement_and_discards_callbacks(
    monkeypatch,
    qtbot,
):
    host = LightHost()
    dock, feedback = build_dock(monkeypatch, host)
    host.tabs.addTab(dock, "AI Processor")
    entered = Event()
    release = Event()
    original_insert = worker_module.insert_at_line

    def blocking_insert(*args, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_insert(*args, **kwargs)

    monkeypatch.setattr(worker_module, "insert_at_line", blocking_insert)

    request_insert(dock)
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    release.set()
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(dock), timeout=3000)
    assert not feedback["info"]
    assert not feedback["error"]
    assert not thread_manager._threads

    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_invalid_mode_reports_error_without_changing_prompt(monkeypatch):
    dock, feedback = build_dock(monkeypatch)

    try:
        request_insert(dock, mode="unknown")

        assert dock.ed_prompt.toPlainText() == "first\nsecond"
        assert len(feedback["error"]) == 1
        assert "Unknown insert mode" in feedback["error"][0][1]
        assert dock._prompt_insert_worker is None
    finally:
        dock.deleteLater()


def test_document_character_bound_precedes_prompt_extraction(monkeypatch):
    dock, feedback = build_dock(monkeypatch)
    monkeypatch.setattr(dock_module, "MAX_AI_PROMPT_BYTES", 4)

    def unexpected_extraction():
        raise AssertionError("prompt extraction must not run beyond the character bound")

    monkeypatch.setattr(dock.ed_prompt, "toPlainText", unexpected_extraction)

    try:
        request_insert(dock)
        assert "character safety limit" in feedback["error"][0][1]
        assert dock._prompt_insert_worker is None
    finally:
        dock.deleteLater()
