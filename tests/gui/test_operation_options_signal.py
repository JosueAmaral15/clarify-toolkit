"""Regression tests for payload-bearing operation-option signals."""

import pytest

from src.gui.widgets.operation_options_widget import OperationOptionsWidget


@pytest.mark.parametrize(
    "control_name",
    [
        "chk_intersection",
        "chk_union",
        "chk_difference",
        "chk_symmetric",
        "chk_ignore_case_keys",
        "chk_ignore_case_values",
        "chk_skip_empty",
        "chk_arrays_ignore_order",
    ],
)
def test_checkbox_payload_emits_one_no_argument_notification(qtbot, control_name):
    widget = OperationOptionsWidget()
    qtbot.addWidget(widget)
    notifications = []
    widget.options_changed.connect(lambda: notifications.append(True))

    getattr(widget, control_name).setChecked(True)

    assert notifications == [True]


def test_output_index_payload_emits_one_no_argument_notification(qtbot):
    widget = OperationOptionsWidget()
    qtbot.addWidget(widget)
    notifications = []
    widget.options_changed.connect(lambda: notifications.append(True))

    widget.combo_output.setCurrentIndex(1)

    assert notifications == [True]


@pytest.mark.parametrize("radio_name", ["radio_full_path", "radio_key_only"])
def test_radio_switch_emits_once_for_the_new_selection(qtbot, radio_name):
    widget = OperationOptionsWidget()
    qtbot.addWidget(widget)
    notifications = []
    widget.options_changed.connect(lambda: notifications.append(True))

    getattr(widget, radio_name).setChecked(True)

    assert notifications == [True]


def test_signal_remains_valid_after_widget_close_and_reopen(qtbot):
    first = OperationOptionsWidget()
    qtbot.addWidget(first)
    first.close()

    reopened = OperationOptionsWidget()
    qtbot.addWidget(reopened)
    notifications = []
    reopened.options_changed.connect(lambda: notifications.append(True))

    reopened.chk_union.setChecked(True)

    assert notifications == [True]
