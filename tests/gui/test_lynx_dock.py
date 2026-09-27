"""Tests for the optional Lynx text browser."""

import pytest
from PySide6.QtCore import QProcess

from src.gui.lynx_dock import LynxDock


def test_lynx_accepts_only_http_urls():
    assert LynxDock.validate_url("https://example.com/path") == "https://example.com/path"
    with pytest.raises(ValueError):
        LynxDock.validate_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        LynxDock.validate_url("example.com")


def test_lynx_arguments_use_read_only_dump_mode():
    assert LynxDock.build_arguments("https://example.com") == [
        "-dump",
        "-nolist",
        "-nonumbers",
        "https://example.com",
    ]


def test_missing_lynx_disables_navigation(qapp):
    dock = LynxDock(executable="")
    try:
        assert not dock.url_edit.isEnabled()
        assert not dock.open_button.isEnabled()
        assert "not installed" in dock.status_label.text()
    finally:
        dock.close()
        dock.deleteLater()


def test_invalid_url_does_not_start_process(qapp):
    dock = LynxDock(executable="/usr/bin/lynx")
    try:
        dock.url_edit.setText("file:///etc/passwd")
        dock._open_url()

        assert dock.process.state() == QProcess.NotRunning
        assert "HTTP or HTTPS" in dock.status_label.text()
    finally:
        dock.close()
        dock.deleteLater()
