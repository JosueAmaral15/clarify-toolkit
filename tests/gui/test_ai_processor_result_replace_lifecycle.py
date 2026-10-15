"""Lifecycle regressions for AI Processor in-memory result replacement."""

# pylint: disable=no-name-in-module  # Qt and Shiboken expose dynamic bindings.

from dataclasses import FrozenInstanceError
from threading import Event, Lock
import time

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread
from PySide6.QtWidgets import QMainWindow, QTabWidget
from shiboken6 import isValid

from src.app import MainWindow
from src.core.search_replace import SearchOptions
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
    dock.text_results.setPlainText("alpha beta alpha")
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


def request_replace(dock, query="alpha", replacement="omega", **kwargs):
    dock._handle_replace_in_results(
        "",
        query,
        replacement,
        kwargs.pop("options", SearchOptions(case_sensitive=True)),
        kwargs.pop("preserve_case", False),
        kwargs.pop("count", 0),
    )


def test_result_replace_cpu_work_runs_off_gui_thread(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    replace_threads = []
    original_replace = worker_module.replace_in_text_bounded

    def observed_replace(*args, **kwargs):
        replace_threads.append(QThread.currentThread())
        return original_replace(*args, **kwargs)

    monkeypatch.setattr(worker_module, "replace_in_text_bounded", observed_replace)

    try:
        request_replace(dock)
        qtbot.waitUntil(lambda: dock._result_replace_worker is None, timeout=3000)

        assert replace_threads
        assert replace_threads[0] is not QCoreApplication.instance().thread()
        assert dock.text_results.toPlainText() == "omega beta omega"
        assert feedback["info"] == [("Replace Complete", "Replaced 2 occurrence(s) of 'alpha'")]
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_result_replace_plan_is_immutable_and_bounded(monkeypatch):
    plan = worker_module.AIResultReplacePlan(
        content="alpha",
        query="alpha",
        replacement="omega",
        case_sensitive=True,
        whole_word=False,
        use_regex=False,
        preserve_case=False,
        count=0,
    )

    with pytest.raises(FrozenInstanceError):
        plan.query = "changed"

    monkeypatch.setattr(worker_module, "MAX_AI_RESULT_QUERY_BYTES", 3)
    with pytest.raises(ValueError, match="query exceeds"):
        worker_module.AIResultReplacePlan(
            content="alpha",
            query="long",
            replacement="omega",
            case_sensitive=True,
            whole_word=False,
            use_regex=False,
            preserve_case=False,
            count=0,
        )


def test_one_replace_per_dock_and_independent_docks(monkeypatch, qtbot):
    first, first_feedback = build_dock(monkeypatch)
    second, _second_feedback = build_dock(monkeypatch)
    entered = Event()
    release = Event()
    state = {"active": 0}
    state_lock = Lock()

    def blocking_replace(content, _pattern, replacement, *_args, checkpoint, **_kwargs):
        with state_lock:
            state["active"] += 1
            if state["active"] == 2:
                entered.set()
        while not release.wait(0.01):
            if not checkpoint():
                return content, 0
        return content.replace("alpha", replacement), 2

    monkeypatch.setattr(worker_module, "replace_in_text_bounded", blocking_replace)

    try:
        request_replace(first)
        request_replace(second)
        qtbot.waitUntil(entered.is_set, timeout=3000)
        assert thread_manager.get_active_threads()[FeatureType.AI_FILE_PROCESSOR] == 2

        request_replace(first, replacement="ignored")
        assert first_feedback["warning"] == [
            (
                "Operation Running",
                "Wait for the current AI Processor operation to finish or cancel it.",
            )
        ]

        release.set()
        qtbot.waitUntil(
            lambda: (first._result_replace_worker is None and second._result_replace_worker is None),
            timeout=3000,
        )
        assert first.text_results.toPlainText() == "omega beta omega"
        assert second.text_results.toPlainText() == "omega beta omega"
        assert not thread_manager._threads
    finally:
        release.set()
        first.deleteLater()
        second.deleteLater()


def test_cancelled_replace_does_not_apply_late_result(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    entered = Event()

    def cancellable_replace(content, _pattern, replacement, *_args, checkpoint, **_kwargs):
        entered.set()
        while checkpoint():
            time.sleep(0.01)
        return content.replace("alpha", replacement), 2

    monkeypatch.setattr(worker_module, "replace_in_text_bounded", cancellable_replace)

    try:
        request_replace(dock)
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock._interrupt()
        qtbot.waitUntil(lambda: dock._result_replace_worker is None, timeout=3000)

        assert dock.text_results.toPlainText().startswith("alpha beta alpha")
        assert "Replacement cancelled." in dock.text_results.toPlainText()
        assert not feedback["info"]
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_tab_close_waits_for_replace_settlement_and_discards_callbacks(
    monkeypatch,
    qtbot,
):
    host = LightHost()
    dock, feedback = build_dock(monkeypatch, host)
    host.tabs.addTab(dock, "AI Processor")
    entered = Event()

    def cancellable_replace(content, _pattern, replacement, *_args, checkpoint, **_kwargs):
        entered.set()
        while checkpoint():
            time.sleep(0.01)
        return content.replace("alpha", replacement), 2

    monkeypatch.setattr(worker_module, "replace_in_text_bounded", cancellable_replace)

    request_replace(dock)
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(dock), timeout=3000)
    assert not feedback["info"]
    assert not feedback["error"]
    assert not thread_manager._threads

    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_invalid_regex_reports_error_without_changing_results(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)

    try:
        request_replace(
            dock,
            query="[",
            options=SearchOptions(case_sensitive=True, regex=True),
        )
        qtbot.waitUntil(lambda: dock._result_replace_worker is None, timeout=3000)

        assert dock.text_results.toPlainText() == "alpha beta alpha"
        assert len(feedback["error"]) == 1
        assert "Invalid regular expression" in feedback["error"][0][1]
        assert not thread_manager._threads
    finally:
        dock.deleteLater()


def test_embedded_panel_emits_current_replace_contract(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    dock.text_results.setPlainText("alpha alphabet ALPHA")
    panel = dock.search_replace_panel
    panel.ed_query.setPlainText("alpha")
    panel.ed_repl.setPlainText("omega")
    panel.chk_case.setChecked(False)
    panel.chk_word.setChecked(True)

    try:
        assert panel.emit_replace_request() is True
        qtbot.waitUntil(lambda: dock._result_replace_worker is None, timeout=3000)

        assert dock.text_results.toPlainText() == "omega alphabet omega"
        assert "Replaced 2 occurrence(s)" in feedback["info"][0][1]
    finally:
        dock.deleteLater()


def test_preserve_case_and_count_contract(monkeypatch, qtbot):
    dock, feedback = build_dock(monkeypatch)
    dock.text_results.setPlainText("ALPHA alpha alpha")

    try:
        request_replace(
            dock,
            options=SearchOptions(case_sensitive=False),
            preserve_case=True,
            count=2,
        )
        qtbot.waitUntil(lambda: dock._result_replace_worker is None, timeout=3000)

        assert dock.text_results.toPlainText() == "OMEGA omega alpha"
        assert "Replaced 2 occurrence(s)" in feedback["info"][0][1]
    finally:
        dock.deleteLater()


def test_document_character_bound_precedes_text_extraction(monkeypatch):
    dock, feedback = build_dock(monkeypatch)
    monkeypatch.setattr(dock_module, "MAX_AI_RESULT_TEXT_CHARS", 4)

    def unexpected_extraction():
        raise AssertionError("text extraction must not run beyond the character bound")

    monkeypatch.setattr(dock.text_results, "toPlainText", unexpected_extraction)

    try:
        request_replace(dock)
        assert "character safety limit" in feedback["error"][0][1]
        assert dock._result_replace_worker is None
    finally:
        dock.deleteLater()
