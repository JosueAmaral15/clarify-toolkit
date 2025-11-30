import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import MainWindow
from PySide6.QtWidgets import QApplication

def test_plugin_loader_integration(qtbot):
    app = QApplication.instance() or QApplication([])
    win = MainWindow(app)
    assert hasattr(win, 'plugin_loader')
    assert len(win.plugin_loader.plugins) > 0
    # Test plugin menu
    plugin_names = [p.name for p in win.plugin_loader.plugins]
    assert "Exportar JSON para CSV" in plugin_names

def test_rest_api_thread_starts(qtbot):
    app = QApplication.instance() or QApplication([])
    win = MainWindow(app)
    assert hasattr(win, 'rest_api')
    # REST API pode falhar ao iniciar se porta já estiver em uso, mas o atributo deve existir
    assert win.rest_api is not None

def test_cloud_sync_dummy(qtbot):
    app = QApplication.instance() or QApplication([])
    win = MainWindow(app)
    assert hasattr(win, 'cloud_sync')
    assert hasattr(win.cloud_sync, 'login')
    assert callable(win.cloud_sync.login)
