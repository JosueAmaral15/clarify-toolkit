"""Regression tests for top-level CLI argument routing."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run_module(*arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    return subprocess.run(
        [sys.executable, "-m", "src", *arguments],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return f"{result.stdout}\n{result.stderr}"


def test_top_level_help_exits_without_initializing_main_window():
    result = _run_module("--help")

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "search" in result.stdout
    assert "Initializing Clarify application" not in _combined_output(result)


def test_short_help_exits_without_initializing_main_window():
    result = _run_module("-h")

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "Initializing Clarify application" not in _combined_output(result)


def test_invalid_top_level_option_fails_without_initializing_main_window():
    result = _run_module("--not-a-clarify-option")

    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert "Initializing Clarify application" not in _combined_output(result)


def test_gui_flag_cannot_be_combined_with_subcommand():
    result = _run_module("--gui", "search", ".", "needle")

    assert result.returncode == 2
    assert "--gui cannot be combined with a CLI subcommand" in result.stderr
    assert "Initializing Clarify application" not in _combined_output(result)


def test_no_arguments_preserve_gui_default(monkeypatch, capsys):
    from src import app as app_module

    monkeypatch.setattr(app_module, "_PYSIDE", False)

    assert app_module.main([]) == 2
    assert "usage:" in capsys.readouterr().err
