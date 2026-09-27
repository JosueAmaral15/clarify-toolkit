"""Run at most one update request without blocking the Qt event loop."""

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from ..update_checker import check_for_updates


class _UpdateSignals(QObject):
    completed = Signal(dict)


class _UpdateRequest(QRunnable):
    def __init__(self, version, force):
        super().__init__()
        self.version = version
        self.force = force
        self.signals = _UpdateSignals()

    def run(self):
        result = {"current_version": self.version, "success": False}
        try:
            available, info = check_for_updates(self.version, force=self.force)
            result.update(success=info is not None, update_available=available, release_info=info)
            if info:
                result["latest_version"] = info.get("version", "Unknown")
            else:
                result["error"] = "Could not retrieve release information. Check your connection."
        except Exception as exc:  # Network failures are reported to the GUI.
            result["error"] = str(exc)
        self.signals.completed.emit(result)


class UpdateCheckController(QObject):
    """Deliver results on the owner's thread and reject overlapping requests."""

    completed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.busy = False

    def start(self, version, force=False):
        if self.busy:
            return False
        self.busy = True
        request = _UpdateRequest(version, force)
        request.signals.completed.connect(self._completed)
        QThreadPool.globalInstance().start(request)
        return True

    @Slot(dict)
    def _completed(self, result):
        self.busy = False
        self.completed.emit(result)
