"""Tests for clock utility state and timer cleanup."""

from src.gui.clock_dock import ClockDock, _format_duration


def test_format_duration_is_bounded_and_zero_padded():
    assert _format_duration(-1) == "00:00:00"
    assert _format_duration(3661) == "01:01:01"


def test_countdown_transitions_without_real_time_wait(qapp, monkeypatch):
    dock = ClockDock()
    completed = []
    monkeypatch.setattr("src.gui.clock_dock.notify_processing_completed", lambda: completed.append(True))
    try:
        dock.timer_seconds.setValue(2)
        dock._start_countdown()
        dock._countdown_timer.stop()

        dock._tick_countdown()
        assert dock.timer_label.text() == "00:00:01"
        dock._tick_countdown()
        assert dock.timer_label.text() == "00:00:00"
        assert completed == [True]
        assert not dock._countdown_timer.isActive()
    finally:
        dock.close()
        dock.deleteLater()


def test_stopwatch_reset_stops_timer_and_clears_state(qapp):
    dock = ClockDock()
    try:
        dock._start_stopwatch()
        assert dock._stopwatch_timer.isActive()

        dock._reset_stopwatch()

        assert not dock._stopwatch_timer.isActive()
        assert dock._stopwatch_elapsed_ms == 0
        assert dock.stopwatch_label.text() == "00:00:00.0"
    finally:
        dock.close()
        dock.deleteLater()
