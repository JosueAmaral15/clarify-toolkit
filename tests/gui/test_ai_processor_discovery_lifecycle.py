"""Lifecycle regressions for AI Processor discovery and condition filtering."""

# pylint: disable=no-name-in-module  # Qt exposes dynamic bindings.

from dataclasses import FrozenInstanceError
from threading import Event
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication, QThread

import src.ai_processor.processor as processor_core
import src.core.filters as filter_core
import src.gui.workers.ai_processor_worker as worker_module
from src.gui.ai_processor_dock import AIProcessorDock
from src.ui import thread_manager


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


def build_content_filter_dock(monkeypatch, tmp_path):
    target = tmp_path / "input.txt"
    target.write_text("needle", encoding="utf-8")
    dock = AIProcessorDock()
    dock.ed_prompt.setPlainText("summarize")
    entry = dock.path_entries[0]
    entry.ed_path.setText(str(tmp_path))
    entry.chk_is_file.setChecked(False)
    dock.ed_extensions.setText(".txt")
    dock.adv_cond_group.setChecked(True)
    field, operator, value = dock.cond_rows[0][:3]
    field.setCurrentText("content")
    operator.setCurrentText("contains")
    value.setText("needle")
    monkeypatch.setattr(dock, "_get_client", lambda: object())
    monkeypatch.setattr(dock, "show_error", lambda *_args: None)
    monkeypatch.setattr(dock, "notify_processing_completed", lambda: False)
    monkeypatch.setattr(
        "src.gui.workers.ai_processor_worker.process_multiple_files",
        lambda *_args, **_kwargs: ["provider-free result"],
    )
    return dock


def test_discovery_and_content_filter_io_run_off_gui_thread(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    discovery_threads = []
    filter_threads = []
    validation_threads = []
    original_walk = processor_core.os.walk
    original_read = filter_core.read_text
    original_to_condition = worker_module.AIConditionRequest.to_condition

    def observed_walk(*args, **kwargs):
        discovery_threads.append(QThread.currentThread())
        yield from original_walk(*args, **kwargs)

    def observed_read(*args, **kwargs):
        filter_threads.append(QThread.currentThread())
        return original_read(*args, **kwargs)

    def observed_to_condition(request):
        validation_threads.append(QThread.currentThread())
        return original_to_condition(request)

    monkeypatch.setattr(processor_core.os, "walk", observed_walk)
    monkeypatch.setattr(filter_core, "read_text", observed_read)
    monkeypatch.setattr(
        worker_module.AIConditionRequest,
        "to_condition",
        observed_to_condition,
    )

    try:
        dock._process()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        gui_thread = QCoreApplication.instance().thread()
        assert discovery_threads
        assert filter_threads
        assert validation_threads
        assert all(thread is not gui_thread for thread in discovery_threads)
        assert all(thread is not gui_thread for thread in filter_threads)
        assert all(thread is not gui_thread for thread in validation_threads)
    finally:
        dock.deleteLater()


def test_processing_plan_is_immutable_and_independent_from_widgets(monkeypatch, tmp_path):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    try:
        plan = dock._snapshot_processing_plan()
        original_path = plan.targets[0].path
        original_value = plan.conditions[0].value

        dock.path_entries[0].ed_path.setText(str(tmp_path / "changed"))
        dock.cond_rows[0][2].setText("changed")

        assert plan.targets[0].path == original_path
        assert plan.conditions[0].value == original_value
        with pytest.raises(FrozenInstanceError):
            plan.filtering_enabled = False
    finally:
        dock.deleteLater()


def test_processing_plan_rejects_unbounded_target_snapshot(monkeypatch, tmp_path):
    monkeypatch.setattr(worker_module, "MAX_AI_TARGETS", 1)
    target = worker_module.AIPathTarget(str(tmp_path), False)

    with pytest.raises(ValueError, match="At most 1 paths"):
        worker_module.AIFileDiscoveryPlan(
            targets=(target, target),
            extensions=(),
            conditions=(),
            logic_operator="AND",
            filtering_enabled=False,
        )


def test_processing_plan_rejects_oversized_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(worker_module, "MAX_AI_EXTENSION_BYTES", 3)

    with pytest.raises(ValueError, match="extension exceeds"):
        worker_module.AIFileDiscoveryPlan(
            targets=(worker_module.AIPathTarget(str(tmp_path), False),),
            extensions=(".text",),
            conditions=(),
            logic_operator="AND",
            filtering_enabled=False,
        )


def test_disabled_conditions_are_not_validated_or_applied(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    provider = Mock(return_value=["provider-free result"])
    dock.adv_cond_group.setChecked(False)
    dock.cond_rows[0][2].setText("[")
    dock.cond_rows[0][5].setChecked(True)
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_called_once()
    finally:
        dock.deleteLater()


def test_discovery_limit_fails_before_provider(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    (tmp_path / "second.txt").write_text("needle", encoding="utf-8")
    provider = Mock(return_value=["must not run"])
    monkeypatch.setattr(worker_module, "MAX_AI_DISCOVERED_FILES", 1)
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_not_called()
        assert "safety limit" in dock.text_results.toPlainText()
    finally:
        dock.deleteLater()


def test_oversized_condition_content_fails_before_provider(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    provider = Mock(return_value=["must not run"])
    monkeypatch.setattr(worker_module, "MAX_AI_CONDITION_CONTENT_BYTES", 4)
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_not_called()
        assert "bounded input size" in dock.text_results.toPlainText()
    finally:
        dock.deleteLater()


def test_content_read_error_is_reported_before_provider(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    provider = Mock(return_value=["must not run"])
    monkeypatch.setattr(
        filter_core,
        "read_text",
        Mock(side_effect=PermissionError("content denied")),
    )
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_not_called()
        assert "content denied" in dock.text_results.toPlainText()
    finally:
        dock.deleteLater()


def test_cancel_during_discovery_settles_without_provider(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    provider = Mock(return_value=["must not run"])
    entered = Event()
    release = Event()

    def blocking_walk(directory):
        entered.set()
        assert release.wait(2)
        yield directory, [], ["input.txt"]

    monkeypatch.setattr(processor_core.os, "walk", blocking_walk)
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock._interrupt()
        release.set()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_not_called()
        assert not thread_manager._threads
    finally:
        release.set()
        dock.deleteLater()


def test_cancel_during_content_filtering_settles_without_provider(monkeypatch, tmp_path, qtbot):
    dock = build_content_filter_dock(monkeypatch, tmp_path)
    provider = Mock(return_value=["must not run"])
    entered = Event()
    release = Event()
    original_read = filter_core.read_text

    def blocking_read(*args, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_read(*args, **kwargs)

    monkeypatch.setattr(filter_core, "read_text", blocking_read)
    monkeypatch.setattr(worker_module, "process_multiple_files", provider)

    try:
        dock._process()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dock._interrupt()
        release.set()
        qtbot.waitUntil(lambda: dock.worker is None, timeout=3000)
        provider.assert_not_called()
        assert not thread_manager._threads
    finally:
        release.set()
        dock.deleteLater()
