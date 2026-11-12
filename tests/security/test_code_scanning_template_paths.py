"""Regressions for project-template output path containment."""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.template_manager import ProjectTemplate, TemplateManager
from src.utils.atomic_files import write_text_atomically


def _install_template(manager, files):
    template = ProjectTemplate(
        id="security-test",
        name="Security test",
        description="Temporary generated template",
        category="other",
        icon="test",
        config={},
        files=files,
        created_at=datetime.now().isoformat(),
        builtin=False,
    )
    manager._templates[template.id] = template
    return template.id


@pytest.mark.parametrize(
    "unsafe_path",
    ["", "../outside.txt", "nested/../../outside.txt", "/tmp/outside.txt", "C:\\outside.txt", "bad\nname"],
)
def test_template_preflight_rejects_unsafe_paths_without_creating_target(
    tmp_path, unsafe_path
):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    template_id = _install_template(
        manager,
        [
            {"path": "valid/first.txt", "content": "must not be written"},
            {"path": unsafe_path, "content": "unsafe"},
        ],
    )

    with pytest.raises(ValueError):
        manager.create_from_template(template_id, target)

    assert not target.exists()
    assert not (tmp_path / "outside.txt").exists()


def test_template_preflight_rejects_symlink_escape_before_writes(tmp_path):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    outside = tmp_path / "outside"
    target.mkdir()
    outside.mkdir()
    (target / "linked").symlink_to(outside, target_is_directory=True)
    template_id = _install_template(
        manager,
        [
            {"path": "safe.txt", "content": "must not be written"},
            {"path": "linked/escaped.txt", "content": "unsafe"},
        ],
    )

    with pytest.raises(ValueError, match="escapes"):
        manager.create_from_template(template_id, target)

    assert not (target / "safe.txt").exists()
    assert not (outside / "escaped.txt").exists()


def test_template_preserves_valid_nested_paths_and_uses_atomic_writes(tmp_path):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    template_id = _install_template(
        manager,
        [
            {"path": "src/main.py", "content": "print('safe')\n"},
            {"path": "docs\\README.md", "content": "# Safe\n"},
        ],
    )

    with patch(
        "src.template_manager.write_text_atomically",
        wraps=write_text_atomically,
    ) as atomic_write:
        assert manager.create_from_template(template_id, target)

    assert (target / "src" / "main.py").read_text(encoding="utf-8") == "print('safe')\n"
    assert (target / "docs" / "README.md").read_text(encoding="utf-8") == "# Safe\n"
    assert atomic_write.call_count == 2


def test_template_rejects_file_directory_conflict_during_preflight(tmp_path):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    template_id = _install_template(
        manager,
        [
            {"path": "conflict", "content": "file"},
            {"path": "conflict/child.txt", "content": "child"},
        ],
    )

    with pytest.raises(ValueError, match="parent file"):
        manager.create_from_template(template_id, target)

    assert not target.exists()


def test_template_rejects_existing_file_as_parent_before_other_writes(tmp_path):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    target.mkdir()
    (target / "blocked").write_text("existing file", encoding="utf-8")
    template_id = _install_template(
        manager,
        [
            {"path": "safe.txt", "content": "must not be written"},
            {"path": "blocked/child.txt", "content": "child"},
        ],
    )

    with pytest.raises(ValueError, match="parent is not a directory"):
        manager.create_from_template(template_id, target)

    assert not (target / "safe.txt").exists()
    assert (target / "blocked").read_text(encoding="utf-8") == "existing file"


def test_template_reports_partial_output_after_atomic_write_failure(tmp_path):
    manager = TemplateManager(tmp_path / "templates")
    target = tmp_path / "project"
    template_id = _install_template(
        manager,
        [
            {"path": "first.txt", "content": "first"},
            {"path": "second.txt", "content": "second"},
        ],
    )
    calls = 0

    def fail_second_write(path, content):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated write failure")
        write_text_atomically(path, content)

    with (
        patch("src.template_manager.write_text_atomically", fail_second_write),
        pytest.raises(RuntimeError, match=r"stopped after 1 file\(s\); partial output"),
    ):
        manager.create_from_template(template_id, target)

    assert (target / "first.txt").read_text(encoding="utf-8") == "first"
    assert not (target / "second.txt").exists()
