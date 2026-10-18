"""Unit tests for bounded immutable match-result clipboard plans."""

from dataclasses import FrozenInstanceError

import pytest

import src.gui.panels.result_export as export_module
from src.gui.panels.result_export import MatchResultClipboardPlan


def sample_matches():
    return {
        "/tmp/alpha.txt": ((1, 2, "first"), (3, 4, "second")),
        "/tmp/beta.txt": ((5, 6, "third"),),
    }


def test_clipboard_plan_preserves_shared_text_format_and_totals():
    matches = sample_matches()
    plan = MatchResultClipboardPlan.from_matches(matches)

    result = plan.execute(lambda: True)

    assert result is not None
    assert result.text == export_module.format_match_results(matches)
    assert result.total_files == 2
    assert result.total_matches == 3


def test_clipboard_plan_is_immutable_and_snapshots_mutable_input():
    matches = {"/tmp/alpha.txt": [(1, 2, "first")]}
    plan = MatchResultClipboardPlan.from_matches(matches)
    matches["/tmp/alpha.txt"][0] = (9, 9, "changed")

    with pytest.raises(FrozenInstanceError):
        plan.total_matches = 10
    result = plan.execute(lambda: True)
    assert result is not None
    assert "first" in result.text
    assert "changed" not in result.text


def test_clipboard_plan_honors_cooperative_cancellation():
    plan = MatchResultClipboardPlan.from_matches(sample_matches())
    checks = iter((True, True, False))

    assert plan.execute(lambda: next(checks)) is None


def test_clipboard_plan_reuses_file_match_and_utf8_limits(monkeypatch):
    monkeypatch.setattr(export_module, "MAX_RESULT_EXPORT_MATCHES", 1)
    with pytest.raises(ValueError, match="match safety limit"):
        MatchResultClipboardPlan.from_matches(sample_matches())

    monkeypatch.setattr(export_module, "MAX_RESULT_EXPORT_MATCHES", 50_000)
    plan = MatchResultClipboardPlan.from_matches({"a": [(1, 1, "x")]})
    monkeypatch.setattr(export_module, "MAX_RESULT_EXPORT_TOTAL_BYTES", 8)
    with pytest.raises(ValueError, match="Clipboard results"):
        plan.execute(lambda: True)
