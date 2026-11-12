"""Subprocess proof that normal MainWindow close returns control to the shell."""

from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil


ROOT = Path(__file__).resolve().parents[1]


def test_normal_close_exits_process_without_surviving_descendants(tmp_path):
    if psutil.virtual_memory().percent >= 85:
        import pytest

        pytest.skip("system RAM is already at or above the 85% safety limit")

    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps({"confirm_on_exit": False}), encoding="utf-8")

    env = os.environ.copy()
    env.update(
        HOME=str(tmp_path),
        XDG_CONFIG_HOME=str(tmp_path / "config"),
        CLARIFY_SETTINGS_FILE=str(settings_path),
        CLARIFY_LOG_DIR=str(tmp_path / "logs"),
        CLARIFY_DIAGNOSTIC_AUTOCLOSE_MS="250",
        QT_QPA_PLATFORM="offscreen",
        OMP_NUM_THREADS="1",
    )
    process = subprocess.Popen(
        [sys.executable, "-X", "faulthandler", "-m", "src"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    tracked_descendants: set[int] = set()
    peak_rss = 0
    guard_reason = ""
    deadline = time.monotonic() + 45

    try:
        while process.poll() is None:
            try:
                parent = psutil.Process(process.pid)
                descendants = parent.children(recursive=True)
                tracked_descendants.update(child.pid for child in descendants)
                peak_rss = max(
                    peak_rss,
                    sum(item.memory_info().rss for item in (parent, *descendants)),
                )
            except psutil.Error:
                pass
            if psutil.virtual_memory().percent >= 85:
                guard_reason = "system RAM reached 85%"
                break
            if peak_rss > 600 * 1024 * 1024:
                guard_reason = "process tree exceeded 600 MiB"
                break
            if time.monotonic() >= deadline:
                guard_reason = "45-second timeout"
                break
            time.sleep(0.1)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)

    output = process.communicate(timeout=2)[0]
    assert not guard_reason, f"{guard_reason}; peak RSS={peak_rss / 1024**2:.1f} MiB\n{output}"
    assert process.returncode == 0, output
    assert "Initializing Clarify application" in output
    assert "Signal source has been deleted" not in output
    assert not list(tmp_path.rglob("crash_*.txt"))

    time.sleep(0.2)
    surviving = [pid for pid in tracked_descendants if psutil.pid_exists(pid)]
    assert not surviving, f"surviving Clarify descendants: {surviving}"
