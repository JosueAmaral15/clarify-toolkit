#!/usr/bin/env python3
"""Test script to verify dock widgets."""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow
from src.gui.json_translate_dock import JsonTranslateDock
from src.gui.json_rewriter_dock import JsonRewriterDock

app = QApplication(sys.argv)
main = QMainWindow()
main.setWindowTitle("Dock Test")
main.resize(1200, 800)

# Create and show JSON Translate dock
dock_translate = JsonTranslateDock(main)
main.addDockWidget(Qt.RightDockWidgetArea, dock_translate)
dock_translate.show()

# Create and show JSON Rewriter dock
dock_rewriter = JsonRewriterDock(main)
main.addDockWidget(Qt.RightDockWidgetArea, dock_rewriter)
dock_rewriter.show()

print(f"✅ JsonTranslateDock created")
print(f"   - Title: {dock_translate.windowTitle()}")
print(f"   - Widget: {dock_translate.widget()}")
print(f"   - Has layout: {dock_translate.widget().layout() is not None}")
if dock_translate.widget() and dock_translate.widget().layout():
    print(f"   - Layout items: {dock_translate.widget().layout().count()}")

print(f"\n✅ JsonRewriterDock created")
print(f"   - Title: {dock_rewriter.windowTitle()}")
print(f"   - Widget: {dock_rewriter.widget()}")
print(f"   - Has layout: {dock_rewriter.widget().layout() is not None}")
if dock_rewriter.widget() and dock_rewriter.widget().layout():
    print(f"   - Layout items: {dock_rewriter.widget().layout().count()}")

main.show()
print("\n🔍 Opening GUI - check if docks have content...")
sys.exit(app.exec())
