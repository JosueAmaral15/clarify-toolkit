"""
Test DockFactory integration (Phase 3.3)

Tests that all 14 docks can be created successfully via their menu action methods.
Converted to pytest format for Sprint 1 (v2.9.115).
"""
import pytest
from PySide6.QtWidgets import QApplication
from src.app import MainWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup not needed - pytest-qt handles it


@pytest.fixture
def main_window(qapp, qtbot):
    """Create MainWindow instance for testing."""
    win = MainWindow(qapp)
    qtbot.addWidget(win)
    yield win
    # Don't call win.close() - let pytest-qt handle cleanup
    # This avoids Qt closeEvent issues during test teardown


# List of (method_name, dock_attribute) pairs to test
DOCK_TEST_CASES = [
    ('_open_trans', 'dock_translate'),
    ('_open_rewrite', 'dock_rewriter'),
    ('_open_text_extractor', 'dock_text_extractor'),
    ('_open_placeholder_replacer', 'dock_placeholder_replacer'),
    ('_open_ai_processor', 'dock_ai_processor'),
    ('_open_json_search', 'dock_json_search'),
    ('_open_case_converter', 'dock_case_converter'),
    ('_open_jsx_extractor', 'dock_jsx_extractor'),
    ('_open_text_to_json', 'dock_text_to_json'),
    ('_open_file_explorer', 'dock_file_explorer'),  # Fixed: was _open_file_list/dock_file_list
    ('_open_history', 'dock_history'),
    ('_open_tutorials', 'dock_tutorials'),
    ('_open_editor', 'dock_editor'),
    ('_open_google_translate', 'dock_google_translate')
]


@pytest.mark.parametrize("method_name,attr_name", DOCK_TEST_CASES)
def test_dock_creation(main_window, method_name, attr_name):
    """
    Test that calling a dock creation method creates the expected dock attribute.
    
    Args:
        main_window: MainWindow fixture
        method_name: Name of the method to call (e.g., '_open_trans')
        attr_name: Expected attribute name (e.g., 'dock_translate')
    """
    # Get method from main window
    method = getattr(main_window, method_name)
    
    # Call method to create dock
    method()
    
    # Verify dock attribute was created
    assert hasattr(main_window, attr_name), f"Missing attribute '{attr_name}' after calling {method_name}()"
    
    # Verify attribute is not None
    dock = getattr(main_window, attr_name)
    assert dock is not None, f"Attribute '{attr_name}' is None after calling {method_name}()"


def test_all_docks_count(main_window):
    """Test that all 14 expected docks can be created."""
    created_docks = []
    
    for method_name, attr_name in DOCK_TEST_CASES:
        method = getattr(main_window, method_name)
        method()
        
        if hasattr(main_window, attr_name):
            created_docks.append(attr_name)
    
    # Verify all 14 docks were created
    assert len(created_docks) == 14, f"Expected 14 docks, but created {len(created_docks)}: {created_docks}"

