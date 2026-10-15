"""Lifecycle regressions for SearchReplacePanel file replacements."""

# pylint: disable=no-name-in-module,protected-access

import time
from threading import Event
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

import src.core.file_explorer_executor as explorer_core
from src.gui.panels.search_replace_panel import SearchReplacePanel
from src.ui import FeatureType, thread_manager


@pytest.fixture(autouse=True)
def clean_thread_manager(qtbot):
    """Keep the singleton registry isolated across replacement tests."""
    thread_manager.resume_registration()
    assert not thread_manager._threads
    yield
    for thread_id, info in list(thread_manager._threads.items()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.wait(2000)
        else:
            thread_manager._on_thread_finished(thread_id, info.completion_token)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=2000)
    thread_manager.resume_registration()


@pytest.fixture
def quiet_messages(monkeypatch):
    information = Mock(return_value=QMessageBox.Ok)
    warning = Mock(return_value=QMessageBox.Ok)
    critical = Mock(return_value=QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "information", information)
    monkeypatch.setattr(QMessageBox, "warning", warning)
    monkeypatch.setattr(QMessageBox, "critical", critical)
    return information, warning, critical


def configure_replace(panel, root, query="cat", replacement="dog"):
    panel.ed_path.setText(str(root))
    panel.ed_extensions.setText(".txt")
    panel.ed_query.setPlainText(query)
    panel.ed_repl.setPlainText(replacement)


def cancelled_result(files_modified=0, replacements=0):
    return {
        "success": False,
        "cancelled": True,
        "replaced_count": replacements,
        "replacements_made": replacements,
        "files_modified": files_modified,
        "errors": [],
        "error": "Operation cancelled",
    }


def test_replace_uses_immutable_snapshot_off_gui(tmp_path, qtbot, monkeypatch, quiet_messages):
    target = tmp_path / "sample.txt"
    target.write_text("CAT CAT", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, tmp_path)
    panel.chk_preserve.setChecked(True)
    entered = Event()
    release = Event()
    observed = []
    original = explorer_core.UnifiedFileExplorerExecutor.execute_replace

    def capture(executor, **kwargs):
        observed.append(QThread.currentThread() is panel._replace_thread)
        entered.set()
        assert release.wait(2)
        return original(executor, **kwargs)

    monkeypatch.setattr(explorer_core.UnifiedFileExplorerExecutor, "execute_replace", capture)

    panel._do_replace(all_=True)
    assert panel._replace_thread.parent() is None
    qtbot.waitUntil(entered.is_set, timeout=2000)
    panel.ed_query.setPlainText("changed")
    panel.ed_repl.setPlainText("changed")
    release.set()

    qtbot.waitUntil(lambda: panel._replace_thread is None, timeout=3000)
    assert observed == [True]
    assert target.read_text(encoding="utf-8") == "DOG DOG"


def test_cancel_wakes_paused_replace_and_blocks_reuse(tmp_path, qtbot, monkeypatch, quiet_messages):
    target = tmp_path / "sample.txt"
    target.write_text("cat", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, tmp_path)
    entered = Event()

    def blocking(executor, **_kwargs):
        entered.set()
        while executor.checkpoint():
            time.sleep(0.005)
        return cancelled_result()

    monkeypatch.setattr(explorer_core.UnifiedFileExplorerExecutor, "execute_replace", blocking)
    panel._do_replace(all_=True)
    qtbot.waitUntil(entered.is_set, timeout=2000)
    worker = panel._replace_worker
    native = panel._replace_thread
    native.terminate = Mock(side_effect=AssertionError("terminate must not be called"))
    panel._set_replace_paused(panel._replace_generation, True)

    panel._do_replace(all_=True)

    assert panel._replace_worker is worker
    assert panel._operation_running()
    assert not panel.btn_replace_all.isEnabled()
    qtbot.waitUntil(lambda: panel._replace_thread is None, timeout=3000)
    native.terminate.assert_not_called()
    assert panel.btn_replace_all.isEnabled()
    assert target.read_text(encoding="utf-8") == "cat"


def test_two_panels_replace_independently(tmp_path, qtbot, monkeypatch, quiet_messages):
    target = tmp_path / "sample.txt"
    target.write_text("cat", encoding="utf-8")
    panels = [SearchReplacePanel(), SearchReplacePanel()]
    for panel in panels:
        qtbot.addWidget(panel)
        configure_replace(panel, target)
    entered = Event()
    executors = []

    def blocking(executor, **_kwargs):
        executors.append(executor)
        if len(executors) == 2:
            entered.set()
        while executor.checkpoint():
            time.sleep(0.005)
        return cancelled_result()

    monkeypatch.setattr(explorer_core.UnifiedFileExplorerExecutor, "execute_replace", blocking)
    for panel in panels:
        panel._do_replace(all_=True)

    qtbot.waitUntil(entered.is_set, timeout=3000)
    assert thread_manager.get_active_threads()[FeatureType.SEARCH_REPLACE] == 2
    assert panels[0]._replace_thread is not panels[1]._replace_thread
    for panel in panels:
        panel.cancel_operation()
    qtbot.waitUntil(lambda: all(panel._replace_thread is None for panel in panels), timeout=3000)


def test_search_and_replace_share_one_panel_operation(tmp_path, qtbot, monkeypatch, quiet_messages):
    target = tmp_path / "sample.txt"
    target.write_text("cat", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, target)
    entered = Event()

    def blocking_read(_path):
        entered.set()
        while not panel._search_worker.is_cancelled:
            time.sleep(0.005)
        return "cat"

    monkeypatch.setattr("src.gui.panels.search_worker.read_text", blocking_read)
    panel._start_search_threaded()
    qtbot.waitUntil(entered.is_set, timeout=2000)

    panel._do_replace(all_=True)

    assert panel._replace_thread is None
    assert panel._search_cancel_requested
    qtbot.waitUntil(lambda: panel._search_thread is None, timeout=3000)
    assert target.read_text(encoding="utf-8") == "cat"


def test_tab_close_waits_and_suppresses_late_replace_feedback(tmp_path, qtbot, monkeypatch, quiet_messages):
    class Host(QMainWindow):
        def __init__(self):
            super().__init__()
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)

        def _close_tab(self, index):
            widget = self.tabs.widget(index)
            if hasattr(widget, "request_tab_close") and not widget.request_tab_close():
                return
            self.tabs.removeTab(index)

    target = tmp_path / "sample.txt"
    target.write_text("cat", encoding="utf-8")
    host = Host()
    panel = SearchReplacePanel(host)
    configure_replace(panel, target)
    host.tabs.addTab(panel, "Search/Replace")
    host.show()
    qtbot.addWidget(host)
    entered = Event()

    def blocking(executor, **_kwargs):
        entered.set()
        while executor.checkpoint():
            time.sleep(0.005)
        return cancelled_result()

    monkeypatch.setattr(explorer_core.UnifiedFileExplorerExecutor, "execute_replace", blocking)
    panel._do_replace(all_=True)
    qtbot.waitUntil(entered.is_set, timeout=2000)

    host._close_tab(0)

    assert host.tabs.count() == 1
    qtbot.waitUntil(lambda: panel._replace_thread is None, timeout=3000)
    qtbot.waitUntil(lambda: host.tabs.count() == 0, timeout=2000)
    for message in quiet_messages:
        message.assert_not_called()


@pytest.mark.parametrize(
    "query,replacement,regex",
    [("", "dog", False), ("[", "dog", True), ("cat", "too-large", False)],
)
def test_invalid_or_oversized_request_never_starts_or_writes(
    tmp_path, qtbot, monkeypatch, quiet_messages, query, replacement, regex
):
    target = tmp_path / "sample.txt"
    target.write_text("cat", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, target, query, replacement)
    panel.chk_regex.setChecked(regex)
    monkeypatch.setattr(explorer_core, "MAX_REPLACE_FILE_BYTES", 4)

    panel._do_replace(all_=True)

    assert panel._replace_thread is None
    assert target.read_text(encoding="utf-8") == "cat"


def test_discovery_limit_writes_nothing(tmp_path, qtbot, monkeypatch, quiet_messages):
    targets = [tmp_path / "a.txt", tmp_path / "b.txt"]
    for target in targets:
        target.write_text("cat", encoding="utf-8")
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, tmp_path)
    monkeypatch.setattr(explorer_core, "MAX_REPLACE_FILES", 1)

    panel._do_replace(all_=True)
    qtbot.waitUntil(lambda: panel._replace_thread is None, timeout=3000)

    assert [target.read_text(encoding="utf-8") for target in targets] == ["cat", "cat"]
    assert quiet_messages[1].called


def test_partial_error_is_reported_and_safe_file_is_atomic(tmp_path, qtbot, quiet_messages):
    target = tmp_path / "a.txt"
    target.write_text("cat", encoding="utf-8")
    target.chmod(0o640)
    link = tmp_path / "b.txt"
    link.symlink_to(target)
    panel = SearchReplacePanel()
    qtbot.addWidget(panel)
    configure_replace(panel, tmp_path)

    panel._do_replace(all_=True)
    qtbot.waitUntil(lambda: panel._replace_thread is None, timeout=3000)

    assert target.read_text(encoding="utf-8") == "dog"
    assert target.stat().st_mode & 0o777 == 0o640
    assert not list(tmp_path.glob(".clarify-replace-*"))
    assert quiet_messages[1].called
    assert "b.txt" in quiet_messages[1].call_args.args[2]


def test_external_replace_consumer_remains_signal_only(qtbot):
    panel = SearchReplacePanel(None, "ai_processor_search_replace")
    qtbot.addWidget(panel)
    configure_replace(panel, "/unused", "cat", "dog")
    received = []
    panel.replace_requested.connect(lambda *args: received.append(args))

    assert panel.emit_replace_request()

    assert len(received) == 1
    assert received[0][:3] == ("", "cat", "dog")
    assert panel._replace_thread is None
    assert not panel._operation_running()
