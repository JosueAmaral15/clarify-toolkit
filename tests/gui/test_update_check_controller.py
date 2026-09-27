"""Update checks remain responsive and cannot accumulate concurrent requests."""

import threading

from PySide6.QtCore import QCoreApplication, QEvent, QThread, QThreadPool, QTimer

from src.gui import update_check_controller as module


def test_main_window_manual_check_and_plugin_menus(main_window, qtbot, monkeypatch):
    monkeypatch.setattr(
        module, "check_for_updates", lambda version, force: (False, {"version": version})
    )
    main_window._check_for_updates_manual()
    qtbot.waitUntil(lambda: not main_window._update_controller.busy)
    assert main_window._manual_update_dialog.btn_close.isEnabled()
    assert "up to date" in main_window._manual_update_dialog.lbl_status.text()
    for plugin_id in ("export_to_postgresql", "slack_notifications"):
        if main_window.plugin_loader.metadata[plugin_id].enabled:
            plugin = main_window.plugin_loader.get_plugin(plugin_id)
            assert plugin is not None
            assert plugin._registered_actions
            assert all(action.associatedObjects() for action in plugin._registered_actions)


def test_slow_request_keeps_event_loop_responsive_and_rejects_duplicates(qtbot, monkeypatch):
    release = threading.Event()
    started = threading.Event()
    worker_threads = []

    def check(version, force):
        worker_threads.append(QThread.currentThread())
        started.set()
        assert release.wait(3)
        return False, {"version": version}

    monkeypatch.setattr(module, "check_for_updates", check)
    controller = module.UpdateCheckController()
    results = []
    controller.completed.connect(results.append)
    try:
        assert controller.start("2.9.0", force=True)
        qtbot.waitUntil(started.is_set)
        assert not controller.start("2.9.0")
        ticks = []
        QTimer.singleShot(0, lambda: ticks.append(True))
        qtbot.waitUntil(lambda: bool(ticks))
        assert controller.busy and not results
        release.set()
        qtbot.waitUntil(lambda: bool(results))
        assert results[0]["success"]
        assert not results[0]["update_available"]
        assert not controller.busy
        assert worker_threads[0] != QThread.currentThread()
    finally:
        release.set()
        assert QThreadPool.globalInstance().waitForDone(3000)
        controller.deleteLater()


def test_failure_resets_busy_and_allows_retry(qtbot, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(module, "check_for_updates", fail)
    controller = module.UpdateCheckController()
    try:
        with qtbot.waitSignal(controller.completed) as signal:
            assert controller.start("2.9.0")
        assert not signal.args[0]["success"]
        assert signal.args[0]["error"] == "offline"
        assert not controller.busy
        with qtbot.waitSignal(controller.completed):
            assert controller.start("2.9.0")
    finally:
        assert QThreadPool.globalInstance().waitForDone(3000)
        controller.deleteLater()


def test_owner_can_be_deleted_during_request(qtbot, monkeypatch):
    release = threading.Event()
    started = threading.Event()

    def check(*args, **kwargs):
        started.set()
        assert release.wait(3)
        return False, None

    monkeypatch.setattr(module, "check_for_updates", check)
    controller = module.UpdateCheckController()
    results = []
    controller.completed.connect(results.append)
    try:
        controller.start("2.9.0")
        qtbot.waitUntil(started.is_set)
        controller.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    finally:
        release.set()
        assert QThreadPool.globalInstance().waitForDone(3000)
    QCoreApplication.processEvents()
    assert not results
