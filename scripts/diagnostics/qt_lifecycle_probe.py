"""Bounded Linux Qt lifecycle probe with temporary settings and updates disabled.

Run with the project virtualenv (requires psutil). Default: three MainWindow
cycles with deferred widget deletion. Use --mode theme for a simple-widget
control, or --cleanup queued to compare the old processEvents-only fixture.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]


def worker(args):
    import resource
    from unittest.mock import patch

    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    sys.path.insert(0, str(ROOT))
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication, QMessageBox, QTextEdit
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
        print(json.dumps({"cycle": cycle, "remaining_widgets": len(app.allWidgets()),
                          "top_levels": len(app.topLevelWidgets())}), flush=True)
    print("PROBE_COMPLETE", flush=True)
    return 0


def monitored(args):
    import psutil

    if psutil.virtual_memory().percent >= 85:
        print("Probe not started: system RAM is already at least 85%.", flush=True)
        return 125
    with tempfile.TemporaryDirectory(prefix="clarify-qt-probe-") as directory:
        env = os.environ.copy()
        env.update(HOME=directory, XDG_CONFIG_HOME=directory,
                   CLARIFY_SETTINGS_FILE=str(Path(directory) / "settings.json"),
                   CLARIFY_LOG_DIR=str(Path(directory) / "logs"),
                   QT_QPA_PLATFORM="offscreen", OMP_NUM_THREADS="1")
        command = [sys.executable, "-X", "faulthandler", str(Path(__file__).resolve()),
                   "--child", "--mode", args.mode, "--cleanup", args.cleanup,
                   "--cycles", str(args.cycles)]
        process = subprocess.Popen(command, cwd=ROOT, env=env, start_new_session=True)
        started = time.monotonic()
        peak_rss = 0
        reason = None
        try:
            while process.poll() is None:
                try:
                    parent = psutil.Process(process.pid)
                    rss = sum(p.memory_info().rss for p in
                              [parent] + parent.children(recursive=True))
                    peak_rss = max(peak_rss, rss)
                except psutil.Error:
                    rss = 0
                if psutil.virtual_memory().percent >= 85:
                    reason = "system RAM reached 85%"
                elif rss > 600 * 1024 * 1024:
                    reason = "process tree exceeded 600 MiB"
                elif time.monotonic() - started > 120:
                    reason = "120-second timeout"
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
        print(json.dumps({"exit": code, "peak_tree_rss_mib": round(peak_rss / 1024**2, 1),
                          "abort_reason": reason}), flush=True)
        return 125 if reason else code if code >= 0 else 128 - code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("theme", "window"), default="window")
    parser.add_argument("--cleanup", choices=("deferred", "queued"), default="deferred")
    parser.add_argument("--cycles", type=int, choices=range(1, 21), default=3)
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    return worker(args) if args.child else monitored(args)


if __name__ == "__main__":
    raise SystemExit(main())
