"""Diagnostic command and guard checks without launching Qt, GDB or providers."""

from pathlib import Path
from types import SimpleNamespace

import psutil
import pytest

from scripts.diagnostics import qt_lifecycle_probe as probe


def args(**values):
    defaults = dict(mode="completion", gdb=False, cleanup="deferred", cycles=3)
    defaults.update(values)
    return SimpleNamespace(**defaults)


@pytest.mark.parametrize("native_exit,expected", [(0, 0), (1, 1), (-11, 139), (125, 125)])
@pytest.mark.parametrize("debugger", [False, True])
@pytest.mark.parametrize("mode", list(probe.TEST_MODULES))
def test_completion_command_preserves_exit_and_isolates_environment(monkeypatch, native_exit, expected, debugger, mode):
    calls = []
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(percent=40))
    monkeypatch.setattr(probe.shutil, "which", lambda _name: "/usr/bin/gdb")

    class FinishedProcess:
        def poll(self):
            return native_exit

        def wait(self):
            return native_exit

    def popen(command, **options):
        calls.append((command, options))
        assert Path(options["env"]["HOME"]).is_dir()
        return FinishedProcess()

    monkeypatch.setattr(probe.subprocess, "Popen", popen)
    options = args(mode=mode)
    options.gdb = debugger
    assert probe.monitored(options) == expected
    command, options = calls[0]
    assert probe.TEST_MODULES[mode] in command
    assert "--timeout=20" in command and "timeout_func_only=false" in command
    assert ("--return-child-result" in command) is debugger
    if debugger:
        assert "set debuginfod enabled off" in command and "thread apply all bt 24" in command
    assert options["start_new_session"] and options["preexec_fn"] is probe.disable_core_dumps
    assert options["env"]["QT_QPA_PLATFORM"] == "offscreen"
    assert options["env"]["CLARIFY_SETTINGS_FILE"].startswith(options["env"]["HOME"])
    assert not Path(options["env"]["HOME"]).exists()


def test_ram_barrier_does_not_launch(monkeypatch):
    monkeypatch.setattr(psutil, "virtual_memory", lambda: SimpleNamespace(percent=85))
    monkeypatch.setattr(probe.subprocess, "Popen", lambda *_a, **_kw: pytest.fail("must not launch"))
    assert probe.monitored(args()) == 125


def test_missing_debugger_does_not_launch(monkeypatch):
    monkeypatch.setattr(probe.shutil, "which", lambda _name: None)
    monkeypatch.setattr(probe.subprocess, "Popen", lambda *_a, **_kw: pytest.fail("must not launch"))
    options = args()
    options.gdb = True
    assert probe.monitored(options) == 2


@pytest.mark.parametrize("mode", list(probe.TEST_MODULES))
def test_completion_child_cannot_bypass_guards(monkeypatch, mode):
    monkeypatch.setattr(probe.sys, "argv", ["qt_lifecycle_probe.py", "--mode", mode, "--child"])
    with pytest.raises(SystemExit) as error:
        probe.main()
    assert error.value.code == 2
