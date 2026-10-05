"""
Tests for AccessibilityManager (v2.9.35)
Tests focus indicators, font scaling, accessible names, contrast ratio calculation.

Author: Josué Amaral
Date: 2025-12-02
"""

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget

from src.accessibility_manager import AccessibilityManager


@pytest.fixture
def qapp(qapp):
    """Reuse pytest-qt's qapp fixture."""
    return qapp


@pytest.fixture
def test_settings(tmp_path):
    """Create temporary QSettings for testing."""
    settings_file = tmp_path / "test_settings.ini"
    settings = QSettings(str(settings_file), QSettings.IniFormat)
    yield settings
    settings.clear()


class TestAccessibilityManager:
    """Test suite for Accessibility Manager functionality."""

    def test_set_accessible_widget_name(self, qapp):
        """Test setting accessible name on widget."""
        button = QPushButton("Run")
        AccessibilityManager.set_accessible_widget(button, "Run Button")

        assert button.accessibleName() == "Run Button"

    def test_set_accessible_widget_with_description(self, qapp):
        """Test setting accessible name and description."""
        line_edit = QLineEdit()
        AccessibilityManager.set_accessible_widget(
            line_edit, "Input Path", "Enter file or directory path"
        )

        assert line_edit.accessibleName() == "Input Path"
        assert line_edit.accessibleDescription() == "Enter file or directory path"

    def test_set_accessible_widget_none(self, qapp):
        """Test that setting accessible name on None doesn't crash."""
        # Should not raise exception
        AccessibilityManager.set_accessible_widget(None, "Test")

    def test_apply_focus_indicators(self, qapp):
        """Test that focus indicators are applied to app stylesheet."""
        initial_stylesheet = qapp.styleSheet()

        AccessibilityManager.apply_focus_indicators(qapp)

        new_stylesheet = qapp.styleSheet()
        assert len(new_stylesheet) > len(initial_stylesheet)
        assert "*:focus" in new_stylesheet
        assert "007ACC" in new_stylesheet  # Focus color

    def test_get_font_size_default(self, test_settings):
        """Test getting default font size."""
        size = AccessibilityManager.get_font_size(test_settings)
        assert size == AccessibilityManager.DEFAULT_FONT_SIZE

    def test_set_font_size(self, test_settings):
        """Test setting font size."""
        AccessibilityManager.set_font_size(14, test_settings)

        size = AccessibilityManager.get_font_size(test_settings)
        assert size == 14

    def test_set_font_size_clamps_min(self, test_settings):
        """Test font size is clamped to minimum."""
        AccessibilityManager.set_font_size(5, test_settings)  # Below min (8)

        size = AccessibilityManager.get_font_size(test_settings)
        assert size == AccessibilityManager.MIN_FONT_SIZE

    def test_set_font_size_clamps_max(self, test_settings):
        """Test font size is clamped to maximum."""
        AccessibilityManager.set_font_size(30, test_settings)  # Above max (24)

        size = AccessibilityManager.get_font_size(test_settings)
        assert size == AccessibilityManager.MAX_FONT_SIZE

    def test_apply_font_size(self, qapp, test_settings):
        """Test applying font size to application."""
        initial_size = qapp.font().pointSize()

        AccessibilityManager.apply_font_size(qapp, 16)

        new_size = qapp.font().pointSize()
        assert new_size == 16
        assert new_size != initial_size

    def test_increase_font_size(self, qapp, test_settings):
        """Test increasing font size."""
        AccessibilityManager.set_font_size(12, test_settings)

        new_size = AccessibilityManager.increase_font_size(qapp, test_settings)

        assert new_size == 13
        assert qapp.font().pointSize() == 13

    def test_increase_font_size_at_max(self, qapp, test_settings):
        """Test increasing font size at maximum limit."""
        AccessibilityManager.set_font_size(AccessibilityManager.MAX_FONT_SIZE, test_settings)

        new_size = AccessibilityManager.increase_font_size(qapp, test_settings)

        assert new_size == AccessibilityManager.MAX_FONT_SIZE

    def test_decrease_font_size(self, qapp, test_settings):
        """Test decreasing font size."""
        AccessibilityManager.set_font_size(12, test_settings)

        new_size = AccessibilityManager.decrease_font_size(qapp, test_settings)

        assert new_size == 11
        assert qapp.font().pointSize() == 11

    def test_decrease_font_size_at_min(self, qapp, test_settings):
        """Test decreasing font size at minimum limit."""
        AccessibilityManager.set_font_size(AccessibilityManager.MIN_FONT_SIZE, test_settings)

        new_size = AccessibilityManager.decrease_font_size(qapp, test_settings)

        assert new_size == AccessibilityManager.MIN_FONT_SIZE

    def test_reset_font_size(self, qapp, test_settings):
        """Test resetting font size to default."""
        AccessibilityManager.set_font_size(20, test_settings)

        new_size = AccessibilityManager.reset_font_size(qapp, test_settings)

        assert new_size == AccessibilityManager.DEFAULT_FONT_SIZE
        assert qapp.font().pointSize() == AccessibilityManager.DEFAULT_FONT_SIZE

    def test_configure_tab_order(self, qapp):
        """Test configuring tab order for widgets."""
        widget1 = QLineEdit()
        widget2 = QPushButton("Browse")
        widget3 = QPushButton("Run")

        # Should not raise exception
        AccessibilityManager.configure_tab_order([widget1, widget2, widget3])

        # Qt's tab order is internal, we just verify no crash

    def test_configure_tab_order_empty_list(self, qapp):
        """Test tab order with empty list."""
        # Should not crash
        AccessibilityManager.configure_tab_order([])

    def test_configure_tab_order_single_widget(self, qapp):
        """Test tab order with single widget."""
        widget = QLineEdit()
        # Should not crash
        AccessibilityManager.configure_tab_order([widget])

    def test_contrast_ratio_dark_theme(self):
        """Test contrast ratio for dark theme colors (WCAG AAA)."""
        # Dark theme: #1E1E1E background, #F0F0F0 text
        ratio = AccessibilityManager.get_contrast_ratio(30, 30, 30, 240, 240, 240)

        # Should exceed WCAG AAA (7:1)
        assert ratio >= 7.0
        # v2.9.34 validation showed 13.2:1, but actual is ~14.6:1 (even better)
        assert 13.0 <= ratio <= 15.0

    def test_contrast_ratio_light_theme(self):
        """Test contrast ratio for light theme colors (WCAG AAA)."""
        # Light theme: #FAFAFA background, #1E1E1E text
        ratio = AccessibilityManager.get_contrast_ratio(250, 250, 250, 30, 30, 30)

        # Should exceed WCAG AAA (7:1)
        assert ratio >= 7.0
        # v2.9.34 validation showed 13.9:1, but actual is ~16:1 (even better)
        assert 13.0 <= ratio <= 16.5

    def test_contrast_ratio_identical_colors(self):
        """Test contrast ratio for identical colors (minimum 1:1)."""
        ratio = AccessibilityManager.get_contrast_ratio(128, 128, 128, 128, 128, 128)

        # Identical colors have 1:1 ratio
        assert 0.99 <= ratio <= 1.01

    def test_contrast_ratio_black_white(self):
        """Test contrast ratio for black and white (maximum 21:1)."""
        ratio = AccessibilityManager.get_contrast_ratio(0, 0, 0, 255, 255, 255)

        # Black/white has maximum 21:1 ratio
        assert 20.5 <= ratio <= 21.5

    def test_enable_screen_reader_support(self, qapp, capfd):
        """Test enabling screen reader support."""
        capfd.readouterr()

        # Should not crash
        AccessibilityManager.enable_screen_reader_support(qapp)

        # Qt's accessibility is enabled by default on modern systems
        # and no application attribute may be set after QApplication exists.
        assert "AA_UseDesktopOpenGL" not in capfd.readouterr().err


class TestAccessibilityIntegration:
    """Integration tests for accessibility features."""

    def test_full_accessibility_workflow(self, qapp, test_settings):
        """Test complete accessibility setup workflow."""
        # 1. Apply focus indicators
        AccessibilityManager.apply_focus_indicators(qapp)
        assert "*:focus" in qapp.styleSheet()

        # 2. Set font size
        AccessibilityManager.set_font_size(14, test_settings)
        AccessibilityManager.apply_font_size(qapp, 14)
        assert qapp.font().pointSize() == 14

        # 3. Create widget with accessible name
        button = QPushButton("Test")
        AccessibilityManager.set_accessible_widget(button, "Test Button", "Press to test")
        assert button.accessibleName() == "Test Button"

        # 4. Increase font
        new_size = AccessibilityManager.increase_font_size(qapp, test_settings)
        assert new_size == 15

        # 5. Reset font
        reset_size = AccessibilityManager.reset_font_size(qapp, test_settings)
        assert reset_size == AccessibilityManager.DEFAULT_FONT_SIZE

    def test_multiple_widgets_accessible_names(self, qapp):
        """Test setting accessible names on multiple widgets."""
        widgets = [
            (QLineEdit(), "Path Input", "Enter file path"),
            (QPushButton("Browse"), "Browse Button", "Open file browser"),
            (QPushButton("Run"), "Run Button", "Execute operation"),
        ]

        for widget, name, desc in widgets:
            AccessibilityManager.set_accessible_widget(widget, name, desc)
            assert widget.accessibleName() == name
            assert widget.accessibleDescription() == desc
