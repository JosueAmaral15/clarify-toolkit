"""Tests for isolated CI test-module discovery."""

from pathlib import Path

from scripts.ci.run_tests_by_module import discover_test_modules


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
