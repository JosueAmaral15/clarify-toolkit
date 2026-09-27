"""Read-only Lynx text browser integration."""

import shutil
from urllib.parse import urlparse

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.i18n.translator import tr
from src.processing_feedback import notify_processing_completed


class LynxDock(QWidget):
    """Fetch a URL through Lynx and display a bounded text rendering."""

    MAX_OUTPUT_CHARS = 2_097_152
    TIMEOUT_MS = 30_000

    def __init__(self, parent=None, executable=None):
        super().__init__(parent)
        self.setObjectName("LynxDock")
        self.executable = shutil.which("lynx") if executable is None else executable
        self._build_ui()
        self._create_process()
        self._update_availability()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel(tr("lynx.url", "URL:")))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")
        self.url_edit.returnPressed.connect(self._open_url)
        url_row.addWidget(self.url_edit, 1)
        self.open_button = QPushButton(tr("lynx.open", "Open"))
        self.open_button.clicked.connect(self._open_url)
        url_row.addWidget(self.open_button)
        self.stop_button = QPushButton(tr("lynx.stop", "Stop"))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop)
        url_row.addWidget(self.stop_button)
        layout.addLayout(url_row)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.document().setMaximumBlockCount(10_000)
        layout.addWidget(self.output, 1)
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def _create_process(self):
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)

    def _update_availability(self):
        available = bool(self.executable)
        self.url_edit.setEnabled(available)
        self.open_button.setEnabled(available)
        self.status_label.setText(
            tr("lynx.ready", "Ready")
            if available
            else tr("lynx.unavailable", "Lynx is not installed")
        )

    @staticmethod
    def validate_url(url):
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Enter a valid HTTP or HTTPS URL")
        return url.strip()

    @staticmethod
    def build_arguments(url):
        return ["-dump", "-nolist", "-nonumbers", url]

    def _open_url(self):
        if not self.executable or self.process.state() != QProcess.NotRunning:
            return
        try:
            url = self.validate_url(self.url_edit.text())
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        self.output.clear()
        self.open_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(tr("lynx.loading", "Loading"))
        self.process.start(self.executable, self.build_arguments(url))
        self._timeout_timer.start(self.TIMEOUT_MS)

    def _read_output(self):
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        if not data:
            return
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(data)
        excess = self.output.document().characterCount() - self.MAX_OUTPUT_CHARS
        if excess > 0:
            cursor = self.output.textCursor()
            cursor.setPosition(0)
            cursor.setPosition(excess, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()

    def _stop(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            QTimer.singleShot(1000, self._kill_if_running)

    def _kill_if_running(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()

    def _on_timeout(self):
        if self.process.state() != QProcess.NotRunning:
            self.status_label.setText(tr("lynx.timeout", "Timed out after 30 seconds"))
            self.process.kill()

    def _on_finished(self, exit_code, exit_status):
        self._timeout_timer.stop()
        self._read_output()
        self.open_button.setEnabled(bool(self.executable))
        self.stop_button.setEnabled(False)
        if self.status_label.text() != tr("lynx.timeout", "Timed out after 30 seconds"):
            self.status_label.setText(f"Finished with exit code {exit_code}")
        if exit_status == QProcess.NormalExit and exit_code == 0:
            notify_processing_completed()

    def _on_error(self, _error):
        self._timeout_timer.stop()
        self.open_button.setEnabled(bool(self.executable))
        self.stop_button.setEnabled(False)
        self.status_label.setText(self.process.errorString())

    def closeEvent(self, event):
        self._timeout_timer.stop()
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.process.waitForFinished(500)
        super().closeEvent(event)
