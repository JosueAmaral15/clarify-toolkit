"""Qt-bound progress controls and lifetime-scoped File Explorer signal routing."""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QLabel, QToolButton, QStyle

from src.i18n.translator import tr


class ExplorerProgressLabel(QLabel):
    """A bounded progress label with a familiar pause/resume icon."""

    pause_requested = Signal(bool)

    def __init__(self, text, parent):
        super().__init__(text, parent)
        self.setContentsMargins(0, 0, 36, 0)
        self.setMinimumHeight(32)
        self.pause_button = QToolButton(self)
        self.pause_button.setFixedSize(28, 28)
        self.pause_button.setCheckable(True)
        self.pause_button.setToolTip(tr("tooltip.pause_resume"))
        self.pause_button.setAccessibleName(tr("tooltip.pause_resume"))
        self.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pause_button.toggled.connect(self._toggled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.pause_button.move(max(0, self.width() - 32), 2)

    @Slot(bool)
    def _toggled(self, paused):
        icon = QStyle.SP_MediaPlay if paused else QStyle.SP_MediaPause
        self.pause_button.setIcon(self.style().standardIcon(icon))
        self.pause_requested.emit(paused)


class ExplorerOperationReceiver(QObject):
    """Discard stale queued events; complete only after the native thread exits."""

    def __init__(self, dock, generation):
        super().__init__(dock)
        self.dock = dock
        self.generation = generation
        self.result = None
        self.error = None

    def accepts_updates(self):
        return (self.generation == self.dock._operation_generation
                and self.dock._active_operation and not self.dock._discard_callbacks
                and not self.dock._cancel_requested)

    @Slot(str)
    def progress(self, message):
        if self.accepts_updates():
            self.dock._on_progress(message)

    @Slot(int, int, str)
    def progress_detailed(self, current, total, message):
        if self.accepts_updates():
            self.dock._on_progress_detailed(current, total, message)

    @Slot(list, int, int)
    def batch(self, items, number, total):
        if self.accepts_updates():
            self.dock._on_batch_ready(items, number, total)

    @Slot(str)
    def diagnostic(self, message):
        if self.accepts_updates():
            self.dock.results_status.setToolTip(str(message)[:500])

    @Slot(object)
    def completed(self, result):
        self.result = result

    @Slot(str)
    def failed(self, error):
        self.error = error

    @Slot()
    def thread_finished(self):
        self.dock._finish_operation(self.generation, self.result, self.error)
