"""Tests for the dependency-audit lock exporter."""

import tomllib
from pathlib import Path

import pytest

from scripts.ci.export_locked_requirements import locked_requirements
from scripts.ci.run_tests_by_module import discover_test_modules


def test_locked_requirements_returns_sorted_unique_exact_versions(tmp_path: Path) -> None:
    lock_path = tmp_path / "poetry.lock"
    lock_path.write_text(
        """
[[package]]
name = "zeta"
version = "2.0.0"

[[package]]
name = "Alpha"
version = "1.0.0"

[[package]]
name = "zeta"
version = "2.0.0"
""",
        encoding="utf-8",
    )

    assert locked_requirements(lock_path) == ["Alpha==1.0.0", "zeta==2.0.0"]


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("unsafe;name", "1.0.0"),
        ("safe-name", "1.0.0\n--index-url=https://example.invalid"),
    ],
)
def test_locked_requirements_rejects_unsafe_values(tmp_path: Path, name: str, version: str) -> None:
    lock_path = tmp_path / "poetry.lock"
    lock_path.write_text(
        f'[[package]]\nname = "{name}"\nversion = "{version}"\n',
        encoding="utf-8",
    )

    with pytest.raises((ValueError, tomllib.TOMLDecodeError)):
        locked_requirements(lock_path)


def test_discover_test_modules_honors_collection_policy(tmp_path: Path) -> None:
    tests_root = tmp_path / "tests"
    tests_root.mkdir()
    (tests_root / "manual").mkdir()
    (tests_root / "conftest.py").write_text(
        'IGNORED_TEST_MODULES = ["test_ignored.py"]\n',
        encoding="utf-8",
    )
    (tests_root / "test_kept.py").touch()
    (tests_root / "test_ignored.py").touch()
    (tests_root / "manual" / "test_manual.py").touch()
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\ntestpaths = ["tests"]\nnorecursedirs = ["manual"]\n',
        encoding="utf-8",
    )

    assert discover_test_modules(tmp_path) == [Path("tests/test_kept.py")]
