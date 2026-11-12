"""Safe GUI-thread helpers for opening local files with the desktop shell."""

import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


def open_local_file(path: str) -> bool:
    """Open an existing file without passing its name through a command shell."""
    try:
        candidate = os.path.abspath(os.fspath(path))
    except (TypeError, ValueError, OSError):
        return False
    if not os.path.isfile(candidate):
        return False
    return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(candidate)))
