"""Bounded integrated command runner."""

import shlex
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
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


class TerminalDock(QWidget):
    """Run one explicit program at a time without an implicit shell."""

    MAX_OUTPUT_CHARS = 1_048_576

    def __init__(self, parent=None, working_directory=None):
        super().__init__(parent)
        self.setObjectName("TerminalDock")
        initial_directory = Path(working_directory or Path.cwd()).resolve()
        self._working_directory = initial_directory if initial_directory.is_dir() else Path.home()
        self._build_ui()
        self._create_process()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        directory_row = QHBoxLayout()
        directory_row.addWidget(QLabel(tr("terminal.directory", "Working directory:")))
        self.directory_edit = QLineEdit(str(self._working_directory))
        self.directory_edit.setReadOnly(True)
        directory_row.addWidget(self.directory_edit, 1)
        self.directory_button = QPushButton(tr("terminal.choose_directory", "Choose..."))
        self.directory_button.clicked.connect(self._choose_directory)
        directory_row.addWidget(self.directory_button)
        layout.addLayout(directory_row)

        command_row = QHBoxLayout()
        command_row.addWidget(QLabel(tr("terminal.command", "Command:")))
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("program --option value")
        self.command_edit.returnPressed.connect(self._run_command)
        command_row.addWidget(self.command_edit, 1)
        self.run_button = QPushButton(tr("terminal.run", "Run"))
        self.run_button.clicked.connect(self._run_command)
        command_row.addWidget(self.run_button)
        self.stop_button = QPushButton(tr("terminal.stop", "Stop"))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop_process)
        command_row.addWidget(self.stop_button)
        layout.addLayout(command_row)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.document().setMaximumBlockCount(5000)
        layout.addWidget(self.output, 1)

        self.status_label = QLabel(tr("terminal.ready", "Ready"))
        layout.addWidget(self.status_label)

    def _create_process(self):
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

    @staticmethod
    def parse_command(command):
        """Parse an explicit command line without invoking a shell."""
        parts = shlex.split(command, posix=True)
        if not parts:
            raise ValueError("Command is empty")
        return parts[0], parts[1:]

    def _choose_directory(self):
        selected = QFileDialog.getExistingDirectory(
            self,
            tr("terminal.choose_directory", "Choose working directory"),
            str(self._working_directory),
        )
        if selected:
            self._working_directory = Path(selected).resolve()
            self.directory_edit.setText(str(self._working_directory))

    def _run_command(self):
        if self.process.state() != QProcess.NotRunning:
            return

        try:
            program, arguments = self.parse_command(self.command_edit.text())
        except ValueError as exc:
            self.status_label.setText(str(exc))
            return

        self._append_output(f"$ {self.command_edit.text()}\n")
        self.process.setWorkingDirectory(str(self._working_directory))
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(tr("terminal.running", "Running"))
        self.process.start(program, arguments)

    def _read_output(self):
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        self._append_output(data)

    def _append_output(self, text):
        if not text:
            return
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)

        excess = self.output.document().characterCount() - self.MAX_OUTPUT_CHARS
        if excess > 0:
            cursor = self.output.textCursor()
            cursor.setPosition(0)
            cursor.setPosition(excess, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        self.output.ensureCursorVisible()

    def _stop_process(self):
        if self.process.state() == QProcess.NotRunning:
            return
        self.status_label.setText(tr("terminal.stopping", "Stopping"))
        self.process.terminate()
        QTimer.singleShot(2000, self._kill_if_running)

    def _kill_if_running(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()

    def _on_finished(self, exit_code, exit_status):
        self._read_output()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Finished with exit code {exit_code}")
        if exit_status == QProcess.NormalExit and exit_code == 0:
            notify_processing_completed()

    def _on_error(self, _error):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(self.process.errorString())

    def closeEvent(self, event):
        if self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(500):
                self.process.kill()
                self.process.waitForFinished(500)
        super().closeEvent(event)
