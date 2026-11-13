#!/usr/bin/env python3
"""Run test modules serially in isolated processes while accumulating coverage."""

from __future__ import annotations

import argparse
import os
import runpy
import subprocess
import sys
import tomllib
from pathlib import Path


def discover_test_modules(project_root: Path) -> list[Path]:
    """Return collected test modules, excluding manual and quarantined scripts."""
    config = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    pytest_config = config["tool"]["pytest"]["ini_options"]
    test_roots = [project_root / item for item in pytest_config.get("testpaths", ["tests"])]
    excluded_dirs = set(pytest_config.get("norecursedirs", []))
    modules: list[Path] = []

    for test_root in test_roots:
        conftest = test_root / "conftest.py"
        ignored = set(runpy.run_path(str(conftest)).get("IGNORED_TEST_MODULES", [])) if conftest.exists() else set()
        for path in test_root.rglob("test_*.py"):
            relative_to_tests = path.relative_to(test_root)
            if any(part in excluded_dirs for part in relative_to_tests.parts[:-1]):
                continue
            if relative_to_tests.as_posix() in ignored:
                continue
            modules.append(path.relative_to(project_root))

    return sorted(modules, key=lambda path: path.as_posix().casefold())


def run(command: list[str], project_root: Path) -> int:
    """Run a child command in the project and return its exit status."""
    return subprocess.run(command, cwd=project_root, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--fail-under", type=int, default=70)
    parser.add_argument("--module", action="append", type=Path, default=[])
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    modules = discover_test_modules(project_root)
    if args.module:
        requested = {path.as_posix() for path in args.module}
        modules = [path for path in modules if path.as_posix() in requested]
    if not modules:
        print("No test modules discovered.", file=sys.stderr)
        return 2

    if run([sys.executable, "-m", "coverage", "erase"], project_root):
        return 2

    failures: list[tuple[Path, int]] = []
    is_github = os.environ.get("GITHUB_ACTIONS") == "true"
    for index, module in enumerate(modules, start=1):
        label = f"[{index}/{len(modules)}] {module.as_posix()}"
        print(f"::group::{label}" if is_github else label, flush=True)
        code = run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(module),
                "-q",
                "--tb=short",
                f"--timeout={args.timeout}",
                "--cov=src",
                "--cov-append",
                "--cov-report=",
                "--cov-fail-under=0",
            ],
            project_root,
        )
        if is_github:
            print("::endgroup::", flush=True)
        if code:
            failures.append((module, code))

    coverage_commands = [
        [sys.executable, "-m", "coverage", "report", f"--fail-under={args.fail_under}"],
        [sys.executable, "-m", "coverage", "html", "--fail-under=0"],
        [sys.executable, "-m", "coverage", "xml", "--fail-under=0"],
    ]
    coverage_codes = [run(command, project_root) for command in coverage_commands]

    if failures:
        print("Failed test modules:", file=sys.stderr)
        for module, code in failures:
            print(f"- {module}: exit {code}", file=sys.stderr)
    if failures or any(coverage_codes):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
