"""Tests for key/value output controls on the supported extractor interfaces."""

import pytest

from src.gui.advanced_extractor_dock import AdvancedExtractorDock
from src.gui.unified_text_to_json_dock import UnifiedTextToJsonDock


@pytest.mark.parametrize(
    ("dock_class", "key_attribute", "value_attribute"),
    [
        (AdvancedExtractorDock, "include_key_checkbox", "include_value_checkbox"),
        (
            UnifiedTextToJsonDock,
            "jsx_include_key_checkbox",
            "jsx_include_value_checkbox",
        ),
    ],
)
def test_supported_extractor_surfaces_expose_independent_output_controls(
    qapp, dock_class, key_attribute, value_attribute
):
    dock = dock_class()
    try:
        key_checkbox = getattr(dock, key_attribute)
        value_checkbox = getattr(dock, value_attribute)

        assert key_checkbox.isChecked()
        assert value_checkbox.isChecked()

        key_checkbox.setChecked(False)
        assert not key_checkbox.isChecked()
        assert value_checkbox.isChecked()

        value_checkbox.setChecked(False)
        assert not value_checkbox.isChecked()
    finally:
        dock.deleteLater()
