"""Lifecycle regressions for SearchReplacePanel result saving."""

# pylint: disable=no-name-in-module,protected-access

import builtins
from threading import Event, Lock

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QThread
from PySide6.QtWidgets import QMainWindow, QTabWidget
from shiboken6 import isValid

import src.gui.panels.result_export as export_module
import src.gui.panels.search_replace_panel as panel_module
from src.gui.panels.search_replace_panel import SearchReplacePanel
from src.ui import FeatureType, thread_manager


class LightHost(QMainWindow):
    """Minimal tab owner exercising the production close handshake."""

    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    def _close_tab(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, "request_tab_close") and not widget.request_tab_close():
            return
        self.tabs.removeTab(index)
        widget.deleteLater()


@pytest.fixture(autouse=True)
def isolated_threads(monkeypatch, qtbot):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.quit()
            info.thread.wait(3000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def build_panel(monkeypatch, tmp_path, parent=None, name="source.txt"):
    panel = SearchReplacePanel(parent)
    source_path = str(tmp_path / name)
    panel.results.populate({source_path: [(1, 0, "needle")]})
    feedback = {"info": [], "critical": []}
    monkeypatch.setattr(
        panel_module.QMessageBox,
        "information",
        lambda *_args: feedback["info"].append((_args, QThread.currentThread())),
    )
    monkeypatch.setattr(
        panel_module.QMessageBox,
        "critical",
        lambda *_args: feedback["critical"].append((_args, QThread.currentThread())),
    )
    return panel, feedback


def select_path(monkeypatch, output_path):
    monkeypatch.setattr(
        panel_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(output_path), "Text Files (*.txt)"),
    )


def test_result_extraction_stays_gui_and_save_work_runs_off_gui(
    monkeypatch,
    qtbot,
    tmp_path,
):
    panel, feedback = build_panel(monkeypatch, tmp_path)
    qtbot.addWidget(panel)
    output_path = tmp_path / "results.txt"
    expected = panel.results.export_to_text()
    extraction_threads = []
    serialization_threads = []
    write_threads = []
    original_get_matches = panel.results.get_matches_data
    original_lines = export_module.iter_match_result_lines
    original_open = builtins.open

    select_path(monkeypatch, output_path)

    def observed_get_matches():
        extraction_threads.append(QThread.currentThread())
        return original_get_matches()

    def observed_lines(matches):
        serialization_threads.append(QThread.currentThread())
        return original_lines(matches)

    def observed_open(*args, **kwargs):
        write_threads.append(QThread.currentThread())
        return original_open(*args, **kwargs)

    monkeypatch.setattr(panel.results, "get_matches_data", observed_get_matches)
    monkeypatch.setattr(export_module, "iter_match_result_lines", observed_lines)
    monkeypatch.setattr(builtins, "open", observed_open)

    panel._save_results()
    qtbot.waitUntil(
        lambda: getattr(panel, "_save_thread", None) is None,
        timeout=3000,
    )

    gui_thread = QCoreApplication.instance().thread()
    assert extraction_threads == [gui_thread]
    assert serialization_threads and serialization_threads[0] is not gui_thread
    assert write_threads and write_threads[0] is not gui_thread
    assert feedback["info"] and feedback["info"][0][1] is gui_thread
    assert output_path.read_text(encoding="utf-8") == expected
    assert not thread_manager._threads


def test_one_export_per_panel_and_independent_panels(monkeypatch, qtbot, tmp_path):
    first, _first_feedback = build_panel(monkeypatch, tmp_path, name="first-source.txt")
    second, _second_feedback = build_panel(monkeypatch, tmp_path, name="second-source.txt")
    qtbot.addWidget(first)
    qtbot.addWidget(second)
    paths = iter((str(tmp_path / "first.txt"), str(tmp_path / "second.txt")))
    monkeypatch.setattr(
        panel_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (next(paths), "Text Files (*.txt)"),
    )
    entered = Event()
    release = Event()
    lock = Lock()
    state = {"active": 0}
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        with lock:
            state["active"] += 1
            if state["active"] == 2:
                entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    try:
        first._save_results()
        second._save_results()
        qtbot.waitUntil(entered.is_set, timeout=3000)
        first_thread = first._save_thread
        assert first_thread.parent() is None
        assert second._save_thread.parent() is None

        first._save_results()

        assert first._save_thread is first_thread
        assert thread_manager.get_active_threads()[FeatureType.SEARCH_REPLACE] == 2
        release.set()
        qtbot.waitUntil(
            lambda: first._save_thread is None and second._save_thread is None,
            timeout=3000,
        )
        assert not thread_manager._threads
    finally:
        release.set()


def test_cancelled_export_preserves_destination_and_cleans_temporary(
    monkeypatch,
    qtbot,
    tmp_path,
):
    panel, feedback = build_panel(monkeypatch, tmp_path)
    qtbot.addWidget(panel)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    try:
        panel._save_results()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        panel.cancel_operation()
        release.set()
        qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

        assert output_path.read_text(encoding="utf-8") == "preserve me"
        assert not list(tmp_path.glob(".clarify-match-results-*.tmp"))
        assert not feedback["info"]
        assert not feedback["critical"]
    finally:
        release.set()


@pytest.mark.parametrize("next_operation", ["search", "replace"])
def test_save_shares_the_search_and_replace_operation_gate(
    monkeypatch,
    qtbot,
    tmp_path,
    next_operation,
):
    panel, _feedback = build_panel(monkeypatch, tmp_path)
    qtbot.addWidget(panel)
    output_path = tmp_path / f"{next_operation}.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    try:
        panel._save_results()
        qtbot.waitUntil(entered.is_set, timeout=2000)

        if next_operation == "search":
            panel._start_search_threaded()
        else:
            panel._do_replace(all_=True)

        assert panel._save_cancel_requested
        assert panel._search_thread is None
        assert panel._replace_thread is None
        assert len(thread_manager._threads) == 1
        release.set()
        qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)
        assert output_path.read_text(encoding="utf-8") == "preserve me"
    finally:
        release.set()


def test_io_error_is_reported_on_gui_without_replacing_destination(
    monkeypatch,
    qtbot,
    tmp_path,
):
    panel, feedback = build_panel(monkeypatch, tmp_path)
    qtbot.addWidget(panel)
    output_path = tmp_path / "results.txt"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    original_open = builtins.open

    def denied_open(path, *args, **kwargs):
        if str(path).endswith(".tmp"):
            raise PermissionError("denied")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied_open)

    panel._save_results()
    qtbot.waitUntil(lambda: panel._save_thread is None, timeout=3000)

    assert output_path.read_text(encoding="utf-8") == "preserve me"
    assert feedback["critical"]
    assert "denied" in feedback["critical"][0][0][-1]
    assert feedback["critical"][0][1] is QCoreApplication.instance().thread()
    assert not list(tmp_path.glob(".clarify-match-results-*.tmp"))


def test_tab_close_waits_for_export_and_discards_late_feedback(
    monkeypatch,
    qtbot,
    tmp_path,
):
    host = LightHost()
    panel, feedback = build_panel(monkeypatch, tmp_path, host)
    host.tabs.addTab(panel, "Search/Replace")
    qtbot.addWidget(host)
    output_path = tmp_path / "results.txt"
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_lines = export_module.iter_match_result_lines

    def blocking_lines(matches):
        entered.set()
        assert release.wait(2)
        return original_lines(matches)

    monkeypatch.setattr(export_module, "iter_match_result_lines", blocking_lines)

    panel._save_results()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    host._close_tab(0)

    assert host.tabs.count() == 1
    release.set()
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=3000)
    qtbot.waitUntil(lambda: not isValid(panel), timeout=3000)
    assert not output_path.exists()
    assert not feedback["info"]
    assert not feedback["critical"]
    assert not thread_manager._threads
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_empty_cancelled_dialog_and_shutdown_rejection_do_not_leak(
    monkeypatch,
    qtbot,
    tmp_path,
):
    panel, feedback = build_panel(monkeypatch, tmp_path)
    qtbot.addWidget(panel)
    panel.results.print_message("")

    panel._save_results()
    assert panel._save_thread is None
    assert feedback["info"]

    panel.results.populate({"source": [(1, 0, "needle")]})
    feedback["info"].clear()
    monkeypatch.setattr(
        panel_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: ("", ""),
    )
    panel._save_results()
    assert panel._save_thread is None
    assert not feedback["info"]
    assert not feedback["critical"]

    select_path(monkeypatch, tmp_path / "rejected.txt")
    thread_manager._shutdown = True
    panel._save_results()
    assert panel._save_thread is None
    assert feedback["critical"]
    assert not thread_manager._threads
