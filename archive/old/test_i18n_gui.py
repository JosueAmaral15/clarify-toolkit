#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI test for i18n system (Task #24 - v2.9.10)
Tests language switching in the MainWindow menu bar.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gui_i18n():
    """Test GUI with i18n."""
    from PySide6.QtWidgets import QApplication
    from src.app import MainWindow
    
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    
    print("=" * 60)
    print("GUI i18n Test (Task #24 - v2.9.10)")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Open the application window")
    print("2. Click: Settings → Language → Português (Brasil)")
    print("3. Observe menu text changes (File→Arquivo, Edit→Editar, etc.)")
    print("4. Click: Settings → Language → English")
    print("5. Observe menu text reverts to English")
    print("\n✓ If menus update correctly, language switching works!")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_gui_i18n()
