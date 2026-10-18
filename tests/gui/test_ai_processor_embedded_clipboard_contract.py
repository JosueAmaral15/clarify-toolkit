"""AI Processor contract for embedded result clipboard ownership."""

# pylint: disable=protected-access

from src.gui.ai_processor_dock import AIProcessorDock


def test_ai_processor_uses_child_panel_clipboard_handlers(qtbot):
    dock = AIProcessorDock()
    qtbot.addWidget(dock)

    search_handler = dock.search_replace_panel.results._copy_all_handler
    insert_handler = dock.insert_panel.results._copy_all_handler

    assert search_handler.__self__ is dock.search_replace_panel
    assert search_handler.__func__ is dock.search_replace_panel._copy_all_results.__func__
    assert insert_handler.__self__ is dock.insert_panel
    assert insert_handler.__func__ is dock.insert_panel._copy_all_results.__func__
    assert not dock._operation_running()
