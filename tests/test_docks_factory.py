"""Test DockFactory integration (Phase 3.3)"""
import sys
from PySide6.QtWidgets import QApplication
from src.app import MainWindow

app = QApplication(sys.argv)
win = MainWindow(app)

# Test each dock creation method
docks = [
    ('_open_trans', 'dock_translate'),
    ('_open_rewrite', 'dock_rewriter'),
    ('_open_text_extractor', 'dock_text_extractor'),
    ('_open_placeholder_replacer', 'dock_placeholder_replacer'),
    ('_open_ai_processor', 'dock_ai_processor'),
    ('_open_json_search', 'dock_json_search'),
    ('_open_case_converter', 'dock_case_converter'),
    ('_open_jsx_extractor', 'dock_jsx_extractor'),
    ('_open_text_to_json', 'dock_text_to_json'),
    ('_open_file_list', 'dock_file_list'),
    ('_open_history', 'dock_history'),
    ('_open_tutorials', 'dock_tutorials'),
    ('_open_editor', 'dock_editor'),
    ('_open_google_translate', 'dock_google_translate')
]

print("Testing DockFactory integration...")
for method_name, attr_name in docks:
    method = getattr(win, method_name)
    method()
    assert hasattr(win, attr_name), f'Missing {attr_name}'
    print(f'✓ {method_name} → {attr_name}')

print('\n✅ All 14 docks created successfully!')
print('DockFactory integration test PASSED')
