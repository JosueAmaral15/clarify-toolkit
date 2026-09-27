"""Tests for bounded, opt-in processing feedback."""

from src.processing_feedback import notify_processing_completed


class _Settings:
    def __init__(self, enabled):
        self.enabled = enabled

    def get(self, key, default=None):
        assert key == "completion_sound"
        return self.enabled


class _Application:
    def __init__(self):
        self.beep_count = 0

    def beep(self):
        self.beep_count += 1


def test_completion_feedback_is_silent_by_default():
    app = _Application()

    assert not notify_processing_completed(_Settings(False), app)
    assert app.beep_count == 0


def test_completion_feedback_emits_exactly_one_beep_when_enabled():
    app = _Application()

    assert notify_processing_completed(_Settings(True), app)
    assert app.beep_count == 1
