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
    "default-appearance": "tests/gui/test_default_appearance.py",
    "completion": "tests/test_qt_completion_lifecycle.py",
    "config-manager": "tests/test_config_manager.py",
    "editor-dock": "tests/gui/test_editor_dock.py",
    "editor-edit-only": "tests/test_edit_only_mode.py",
    "editor-find-core": "tests/test_editor_find.py",
    "editor-find-enter": "tests/gui/test_editor_find_enter.py",
    "editor-find-modeless": "tests/gui/test_editor_find_modeless.py",
    "editor-menu-shortcuts": "tests/gui/test_editor_menu_shortcuts.py",
    "editor-open-clean-state": "tests/gui/test_editor_open_clean_state.py",
    "editor-find-state-history": "tests/gui/test_editor_find_state_history.py",
    "editor-layout": "tests/gui/test_editor_layout.py",
    "editor-notes-store": "tests/test_editor_notes.py",
    "editor-find-scope-negation": "tests/gui/test_editor_find_scope_negation.py",
    "editor-priority-stage1": "tests/gui/test_editor_priority_stage1.py",
    "editor-priority-stage2": "tests/gui/test_editor_priority_stage2.py",
    "editor-priority-stage3": "tests/gui/test_editor_priority_stage3.py",
    "editor-priority-stage4-tabs": "tests/gui/test_editor_priority_stage4_tabs.py",
    "editor-priority-stage4-explorer": "tests/gui/test_editor_priority_stage4_explorer.py",
    "editor-priority-stage5-sessions": "tests/gui/test_editor_priority_stage5_sessions.py",
    "editor-priority-stage5-notes": "tests/gui/test_editor_priority_stage5_notes.py",
    "editor-quick-toolbar": "tests/gui/test_editor_quick_toolbar.py",
    "editor-recovery-lifecycle": "tests/gui/test_editor_recovery_lifecycle.py",
    "editor-recovery-reopen": "tests/gui/test_editor_recovery_reopen.py",
    "editor-recovery-retention": "tests/gui/test_editor_recovery_retention.py",
    "editor-recovery-store": "tests/test_editor_recovery.py",
    "editor-readonly-theme": "tests/gui/test_editor_readonly_theme.py",
    "editor-redo-shortcuts": "tests/gui/test_editor_redo_shortcuts.py",
    "editor-recent-interactions": "tests/gui/test_editor_recent_interactions.py",
    "editor-rename-imports": "tests/gui/test_editor_rename_imports.py",
    "editor-smart-home-visual": "tests/gui/test_editor_smart_home_visual.py",
    "editor-status-info": "tests/gui/test_editor_status_info.py",
    "editor-tab-copy-path": "tests/gui/test_editor_tab_copy_path.py",
    "editor-temp-note-lifecycle": "tests/gui/test_editor_temp_note_lifecycle.py",
    "editor-untitled-dense-names": "tests/gui/test_editor_untitled_dense_names.py",
    "shortcut-reference": "tests/gui/test_shortcut_reference.py",
    "shortcut-customizer": "tests/test_shortcut_customizer.py",
    "shortcuts-dialog": "tests/test_shortcuts_dialog.py",
    "explorer-lifecycle": "tests/test_file_explorer_lifecycle.py",
    "explorer-incremental": "tests/test_file_explorer_incremental_search.py",
    "explorer-presentation": "tests/test_file_explorer_presentation.py",
    "explorer-replace": "tests/test_file_explorer_replace.py",
    "explorer-search-replace-sections": "tests/gui/test_file_explorer_search_replace_sections.py",
    "explorer-target-scope": "tests/test_file_explorer_target_scope.py",
    "explorer-table-refresh": "tests/test_file_explorer_table_refresh.py",
    "explorer-top-options": "tests/test_file_explorer_top_options_and_globs.py",
    "explorer-workspace-i18n": "tests/test_explorer_workspace_mode_i18n.py",
    "google-translate-api": "tests/test_google_translate.py",
    "google-translate-dock": "tests/test_google_translate_dock.py",
    "google-translate-lifecycle": "tests/test_google_translate_lifecycle.py",
    "i18n-expansion": "tests/test_i18n_expansion.py",
    "keyboard-shortcut-aliases": "tests/test_keyboard_shortcut_aliases.py",
    "keyboard-shortcuts": "tests/test_keyboard_shortcuts.py",
    "live-ui": "tests/gui/test_live_ui_actions.py",
    "operation-options-signal": "tests/gui/test_operation_options_signal.py",
    "plugin-system": "tests/test_plugin_system.py",
    "set-operations": "tests/test_set_operations.py",
    "settings-shortcuts": "tests/test_sprint8_features.py",
    "settings-reset-core": "tests/test_settings_reset.py",
    "settings-reset-dialog": "tests/gui/test_settings_reset_dialog.py",
    "theme-manager": "tests/test_theme_manager.py",
    "tab-layouts": "tests/test_tab_layouts.py",
    "thread-manager": "tests/test_thread_management_system.py",
    "tool-dock-toggle": "tests/gui/test_tool_dock_toggle.py",
    "tool-tab-chrome": "tests/gui/test_tool_tab_chrome.py",
    "translation-catalog": "tests/test_translation_catalog_lookup.py",
    "tutorials-localization": "tests/gui/test_tutorials_localization.py",
    "unified-extraction-lifecycle": "tests/gui/test_unified_extraction_lifecycle.py",
    "unified-extractor-controls": "tests/gui/test_extractor_output_controls.py",
    "unified-editor-switch": "tests/gui/test_unified_text_to_json_editor_switch.py",
    "unified-search-replace": "tests/gui/test_unified_text_search_replace.py",
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
