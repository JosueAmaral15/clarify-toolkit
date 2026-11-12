"""Regressions for command-injection code-scanning findings."""

from pathlib import Path

import yaml

from src.gui import desktop_services
from src.gui.progress.progress_bar_widget import (
    _MACOS_NOTIFICATION_SCRIPT,
    _notification_fallback_command,
)


ROOT = Path(__file__).parents[2]


def test_desktop_service_preserves_shell_metacharacters_as_url_data(
    monkeypatch, tmp_path
):
    source = tmp_path / "report & calc.exe.txt"
    source.write_text("safe", encoding="utf-8")
    observed = []
    monkeypatch.setattr(
        desktop_services.QDesktopServices,
        "openUrl",
        lambda url: observed.append(url.toLocalFile()) or True,
    )

    assert desktop_services.open_local_file(str(source)) is True
    assert observed == [str(source)]


def test_result_trees_do_not_route_paths_through_command_shells():
    for relative in ("src/gui/results_tree.py", "src/gui/panels/results_tree.py"):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert '["cmd", "/c", "start"' not in source
        assert "open_local_file(path)" in source


def test_macos_notification_uses_immutable_script_and_argv():
    title = 'done" & do shell script "touch /tmp/injected" & "'
    message = 'file" & do shell script "open -a Calculator" & "'

    command = _notification_fallback_command("Darwin", title, message)

    assert command == [
        "osascript",
        "-e",
        _MACOS_NOTIFICATION_SCRIPT,
        "--",
        title,
        message,
    ]
    assert title not in _MACOS_NOTIFICATION_SCRIPT
    assert message not in _MACOS_NOTIFICATION_SCRIPT


def test_benchmark_dispatch_inputs_are_choices_and_not_shell_expressions():
    workflow_path = ROOT / ".github/workflows/benchmarks.yml"
    workflow = yaml.load(workflow_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    dispatch_inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert dispatch_inputs["sizes"]["type"] == "choice"
    assert dispatch_inputs["runs"]["type"] == "choice"

    full_step = next(
        step
        for step in workflow["jobs"]["benchmark"]["steps"]
        if step["name"] == "🏃 Run benchmarks (Full)"
    )
    assert "${{ inputs." not in full_step["run"]
    assert '--sizes "$BENCHMARK_SIZES"' in full_step["run"]
    assert '--operations "$BENCHMARK_OPERATIONS"' in full_step["run"]
    assert '--runs "$BENCHMARK_RUNS"' in full_step["run"]
