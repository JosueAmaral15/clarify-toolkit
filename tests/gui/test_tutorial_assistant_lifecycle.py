"""Fake assistant services and real Qt threads; no network or MainWindow startup."""

import threading
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QMainWindow
from shiboken6 import isValid

from src.app import MainWindow
from src.gui import tutorial_assistant_dialog as module
from src.gui.tutorials_dock import TutorialsDock
from src.i18n import get_translator, tr
from src.settings_manager import SettingsManager
from src.ui import FeatureType, thread_manager


@pytest.fixture
def context(qapp, monkeypatch, tmp_path):
    settings = SettingsManager(str(tmp_path / "settings.json"))
    service = Mock()
    service.is_available.return_value = True
    service.ask.return_value = ("fake answer", True)
    monkeypatch.setattr(module, "get_assistant", Mock(return_value=service))
    monkeypatch.setattr(module, "get_settings", lambda: settings)
    monkeypatch.setattr("src.settings_manager.get_settings", lambda: settings)
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(thread_manager, "_feature_locks", {f: threading.Lock() for f in FeatureType})
    get_translator().switch_language("en")
    parent = QMainWindow()
    parent.settings = settings
    yield parent, settings, service
    if isValid(parent):
        parent.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()
    get_translator().switch_language("en")
    assert not thread_manager._threads


@pytest.mark.parametrize("entry", ["main", "tutorials"])
def test_entry_uses_existing_settings_and_reuses_or_recreates_dialog(context, qapp, entry):
    parent, settings, _ = context
    settings.set("ai_processor/gemini_api_key", "fake-key-not-a-secret")
    owner = parent
    open_dialog = MainWindow._show_ai_assistant
    if entry == "tutorials":
        owner = TutorialsDock(parent)
        open_dialog = TutorialsDock._open_ai_assistant
    open_dialog(owner)
    first = owner._tutorial_assistant_dialog
    module.get_assistant.assert_called_once_with(api_key="fake-key-not-a-secret")
    open_dialog(owner)
    assert owner._tutorial_assistant_dialog is first
    first.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    assert not isValid(first)
    open_dialog(owner)
    assert owner._tutorial_assistant_dialog is not first


@pytest.mark.parametrize("counter", [None, "bad", -1, "3"])
def test_feedback_settings_round_trip_and_corrupt_counter(context, counter):
    parent, settings, _ = context
    settings.set("tutorial_assistant/thumbs_up", counter)
    dialog = module.TutorialAssistantDialog(parent)
    initial = 3 if counter == "3" else 0
    assert dialog.thumbs_up_count == initial
    dialog._thumbs_up()
    dialog._thumbs_down()
    reloaded = SettingsManager(str(settings.config_file))
    assert reloaded.get("tutorial_assistant/thumbs_up") == initial + 1
    assert reloaded.get("tutorial_assistant/thumbs_down") == 1


def test_unavailable_does_not_start_request(context):
    parent, _, service = context
    service.is_available.return_value = False
    dialog = module.TutorialAssistantDialog(parent)
    dialog.input_field.setText("test")
    dialog._send_message()
    service.ask.assert_not_called()
    assert not dialog.send_button.isEnabled()
    assert dialog.worker is None


@pytest.mark.parametrize("failure", [False, True])
def test_real_thread_completes_or_reports_exception(context, qtbot, failure):
    parent, _, service = context
    if failure:
        service.ask.side_effect = RuntimeError("fake provider failure")
    dialog = module.TutorialAssistantDialog(parent)
    dialog.input_field.setText("test")
    dialog._send_message()
    qtbot.waitUntil(lambda: dialog.worker is None and not thread_manager._threads, timeout=4000)
    expected = tr("tutorial_assistant.request_failed") if failure else "fake answer"
    assert expected in dialog.chat_display.toPlainText()
    assert dialog.send_button.isEnabled()
    assert dialog.clear_button.isEnabled()


def test_single_request_pending_close_then_reopen(context, qtbot):
    parent, _, service = context
    release = threading.Event()
    entered = threading.Event()

    def blocked(_query):
        entered.set()
        assert release.wait(4)
        return "completed", True

    service.ask.side_effect = blocked
    dialog = module.TutorialAssistantDialog(parent)
    other = module.TutorialAssistantDialog(parent)
    dialog.show()
    dialog.input_field.setText("first")
    dialog._send_message()
    try:
        qtbot.waitUntil(entered.is_set, timeout=2000)
        dialog.input_field.setText("duplicate")
        dialog._send_message()
        other.input_field.setText("other")
        other._send_message()
        assert other.worker is None
        assert other.status_label.text() == tr("tutorial_assistant.busy")
        get_translator().switch_language("pt_BR")
        assert dialog.status_label.text() == tr("tutorial_assistant.thinking")
        dialog.reject()
        assert dialog.isVisible()
        assert dialog._close_pending
        assert dialog.worker.isInterruptionRequested()
        assert dialog.status_label.text() == tr("tutorial_assistant.waiting")
        service.ask.assert_called_once_with("first")
    finally:
        release.set()
    qtbot.waitUntil(lambda: dialog.worker is None and not thread_manager._threads, timeout=4000)
    assert not dialog.isVisible()
    assert not dialog._close_pending
    dialog.show()
    service.ask.side_effect = None
    dialog.input_field.setText("reopened")
    dialog._send_message()
    qtbot.waitUntil(lambda: dialog.worker is None and not thread_manager._threads, timeout=4000)
    assert dialog.isVisible()
    assert "fake answer" in dialog.chat_display.toPlainText()


def test_parent_deletion_retains_thread_without_late_widget_callbacks(context, qtbot, qapp):
    parent, _, service = context
    release = threading.Event()
    entered = threading.Event()

    def blocked(_query):
        entered.set()
        assert release.wait(4)
        return "late response", True

    service.ask.side_effect = blocked
    dialog = module.TutorialAssistantDialog(parent)
    dialog.input_field.setText("delete parent")
    dialog._send_message()
    worker = dialog.worker
    try:
        qtbot.waitUntil(entered.is_set, timeout=2000)
        parent.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        assert not isValid(dialog)
        assert isValid(worker) and worker.isRunning()
        assert thread_manager.is_feature_running(FeatureType.TUTORIAL_ASSISTANT)
    finally:
        release.set()
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=4000)
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()
    assert not isValid(worker)


def test_runtime_labels_change_without_rewriting_chat(context):
    parent, _, _ = context
    dialog = module.TutorialAssistantDialog(parent)
    dialog._add_user_message("user text stays")
    original = dialog.chat_display.toPlainText()
    get_translator().switch_language("pt_BR")
    assert dialog.send_button.text() == tr("tutorial_assistant.btn_send")
    assert dialog.header.text() == tr("tutorial_assistant.header")
    assert dialog.thumbs_up_button.toolTip() == tr("tutorial_assistant.tooltip_thumbs_up")
    assert dialog.thumbs_down_button.toolTip() == tr("tutorial_assistant.tooltip_thumbs_down")
    assert dialog.chat_display.toPlainText() == original
