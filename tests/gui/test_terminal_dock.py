"""Tests for the bounded integrated terminal."""

from PySide6.QtCore import QProcess

from src.gui.terminal_dock import TerminalDock


def test_parse_command_preserves_quoted_arguments():
    assert TerminalDock.parse_command('printf "hello world"') == (
        "printf",
        ["hello world"],
    )


def test_terminal_runs_program_without_shell(qapp, tmp_path, monkeypatch):
    dock = TerminalDock(working_directory=tmp_path)
    completed = []
    monkeypatch.setattr("src.gui.terminal_dock.notify_processing_completed", lambda: completed.append(True))
    try:
        dock.command_edit.setText('/usr/bin/printf "terminal-ok"')
        dock._run_command()
        assert dock.process.waitForFinished(3000)
        dock._read_output()
        qapp.processEvents()

        assert "terminal-ok" in dock.output.toPlainText()
        assert dock.process.exitCode() == 0
        assert completed == [True]
    finally:
        dock.close()
        dock.deleteLater()


def test_terminal_output_is_capped(qapp, tmp_path):
    dock = TerminalDock(working_directory=tmp_path)
    try:
        dock._append_output("x" * (dock.MAX_OUTPUT_CHARS + 100))

        assert dock.output.document().characterCount() <= dock.MAX_OUTPUT_CHARS
    finally:
        dock.close()
        dock.deleteLater()


def test_close_stops_running_process(qapp, tmp_path):
    dock = TerminalDock(working_directory=tmp_path)
    dock.command_edit.setText("/usr/bin/sleep 5")
    dock._run_command()
    assert dock.process.waitForStarted(1000)

    dock.close()

    assert dock.process.state() == QProcess.NotRunning
    dock.deleteLater()
