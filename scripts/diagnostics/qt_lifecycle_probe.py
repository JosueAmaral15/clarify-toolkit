"""Bounded Linux Qt lifecycle probe with temporary settings and updates disabled.

Run with the project virtualenv (requires psutil). Default: three MainWindow
cycles with deferred widget deletion. Use --mode theme for a simple-widget
control, or --cleanup queued to compare the old processEvents-only fixture.
Use --mode completion --gdb for isolated Explorer completion/GC regressions
with native backtraces on a crash, without constructing the full MainWindow.
Use --mode explorer-lifecycle --gdb for the existing module that aborted on
2026-09-29, or --mode live-ui for the focused menu/dock repair regressions.
Never run these test modules together with other GUI modules.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
TEST_MODULES = {
    "accessibility": "tests/test_accessibility.py",
    "completion": "tests/test_qt_completion_lifecycle.py",
    "explorer-lifecycle": "tests/test_file_explorer_lifecycle.py",
    "google-translate-api": "tests/test_google_translate.py",
    "google-translate-dock": "tests/test_google_translate_dock.py",
    "google-translate-lifecycle": "tests/test_google_translate_lifecycle.py",
    "live-ui": "tests/gui/test_live_ui_actions.py",
    "plugin-system": "tests/test_plugin_system.py",
    "theme-manager": "tests/test_theme_manager.py",
    "thread-manager": "tests/test_thread_management_system.py",
    "tutorials-localization": "tests/gui/test_tutorials_localization.py",
}


def disable_core_dumps():
    import resource

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def worker(args):
    from unittest.mock import patch

    disable_core_dumps()
    sys.path.insert(0, str(ROOT))
    # pylint: disable=no-name-in-module  # PySide6 extension types are dynamic.
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication, QMessageBox, QTextEdit

    # pylint: enable=no-name-in-module
    from src.theme_manager import ThemeManager

    app = QApplication([])
    if args.mode == "window":
        from src.app import MainWindow

        patch.object(MainWindow, "_auto_check_for_updates", lambda self: None).start()
        patch.object(QMessageBox, "exec", lambda self: QMessageBox.Yes).start()
        patch.object(QMessageBox, "question", lambda *unused: QMessageBox.Yes).start()

    for cycle in range(args.cycles):
        print(json.dumps({"cycle": cycle, "phase": "construct"}), flush=True)
        widget = MainWindow(app) if args.mode == "window" else QTextEdit()
        widget.show()
        app.processEvents()
        for theme in ("dark", "light", "system"):
            print(json.dumps({"cycle": cycle, "theme": theme}), flush=True)
            ThemeManager.apply_theme(app, theme)
            app.processEvents()
        widget.close()
        widget.deleteLater()
        if args.cleanup == "deferred":
            QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        app.processEvents()
        del widget
        gc.collect()
        print(
            json.dumps(
                {"cycle": cycle, "remaining_widgets": len(app.allWidgets()), "top_levels": len(app.topLevelWidgets())}
            ),
            flush=True,
        )
    print("PROBE_COMPLETE", flush=True)
    return 0


def monitored(args):
    import psutil

    if args.gdb and shutil.which("gdb") is None:
        print("Probe not started: gdb is not installed.", flush=True)
        return 2
    if psutil.virtual_memory().percent >= 85:
        print("Probe not started: system RAM is already at least 85%.", flush=True)
        return 125
    with tempfile.TemporaryDirectory(prefix="clarify-qt-probe-") as directory:
        env = os.environ.copy()
        env.update(
            HOME=directory,
            XDG_CONFIG_HOME=directory,
            CLARIFY_SETTINGS_FILE=str(Path(directory) / "settings.json"),
            CLARIFY_LOG_DIR=str(Path(directory) / "logs"),
            QT_QPA_PLATFORM="offscreen",
            OMP_NUM_THREADS="1",
        )
        command = [
            sys.executable,
            "-X",
            "faulthandler",
            str(Path(__file__).resolve()),
            "--child",
            "--mode",
            args.mode,
            "--cleanup",
            args.cleanup,
            "--cycles",
            str(args.cycles),
        ]
        if args.mode in TEST_MODULES:
            command = [
                sys.executable,
                "-X",
                "faulthandler",
                "-m",
                "pytest",
                TEST_MODULES[args.mode],
                "-q",
                "--maxfail=1",
                "--timeout=20",
                "--timeout-method=thread",
                "-o",
                "timeout_func_only=false",
            ]
        if args.gdb:
            command = [
                "gdb",
                "-q",
                "-nx",
                "-nh",
                "-batch",
                "--return-child-result",
                "-iex",
                "set debuginfod enabled off",
                "-ex",
                "set pagination off",
                "-ex",
                "set print thread-events off",
                "-ex",
                "run",
                "-ex",
                "thread apply all bt 24",
                "--args",
                *command,
            ]
        process = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True, preexec_fn=disable_core_dumps)
        started = time.monotonic()
        wall_limit = 180 if args.mode in TEST_MODULES else 120
        peak_rss = 0
        reason = None
        try:
            while process.poll() is None:
                try:
                    parent = psutil.Process(process.pid)
                    rss = sum(p.memory_info().rss for p in [parent] + parent.children(recursive=True))
                    peak_rss = max(peak_rss, rss)
                except psutil.Error:
                    rss = 0
                if psutil.virtual_memory().percent >= 85:
                    reason = "system RAM reached 85%"
                elif rss > 600 * 1024 * 1024:
                    reason = "process tree exceeded 600 MiB"
                elif time.monotonic() - started > wall_limit:
                    reason = f"{wall_limit}-second timeout"
                if reason:
                    break
                time.sleep(0.25)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
        print(
            json.dumps({"exit": code, "peak_tree_rss_mib": round(peak_rss / 1024**2, 1), "abort_reason": reason}),
            flush=True,
        )
        return 125 if reason else code if code >= 0 else 128 - code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("theme", "window", *TEST_MODULES), default="window")
    parser.add_argument(
        "--gdb", action="store_true", help="Capture native backtraces with installed GDB (no downloads)"
    )
    parser.add_argument("--cleanup", choices=("deferred", "queued"), default="deferred")
    parser.add_argument("--cycles", type=int, choices=range(1, 21), default=3)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child and args.mode in TEST_MODULES:
        parser.error("test modules must run through the monitored parent")
    return worker(args) if args.child else monitored(args)


if __name__ == "__main__":
    raise SystemExit(main())
