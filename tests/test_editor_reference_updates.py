"""Bounded language-aware reference updates after Editor Explorer renames."""

import os

import pytest

from src import editor_reference_updates as module
from src.editor_reference_updates import (
    ReferenceUpdateError,
    ReferenceUpdateLimits,
    analyze_rename_references,
    apply_reference_updates,
)


def _renamed_file(root, old_relative, new_relative, content="value = 1\n"):
    old_path = root / old_relative
    new_path = root / new_relative
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(content, encoding="utf-8")
    new_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.rename(new_path)
    return old_path, new_path


def test_python_imports_are_updated_without_touching_strings(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "pkg/old_name.py", "pkg/new_name.py")
    consumer = tmp_path / "consumer.py"
    consumer.write_text(
        "from pkg.old_name import Thing\n"
        "import pkg.old_name as old\n"
        "literal = 'pkg.old_name'\n",
        encoding="utf-8",
    )

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)

    assert plan.change_count == 2
    applied = apply_reference_updates(plan)
    assert consumer.read_text(encoding="utf-8") == (
        "from pkg.new_name import Thing\n"
        "import pkg.new_name as old\n"
        "literal = 'pkg.old_name'\n"
    )
    applied.rollback()
    assert "from pkg.old_name import Thing" in consumer.read_text(encoding="utf-8")


def test_relative_python_import_and_folder_prefix_are_updated(tmp_path):
    package = tmp_path / "oldpkg"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "old.py").write_text("VALUE = 1\n", encoding="utf-8")
    consumer = package / "consumer.py"
    consumer.write_text(
        "from .old import VALUE\nfrom oldpkg.old import VALUE as OTHER\n",
        encoding="utf-8",
    )
    new_package = tmp_path / "newpkg"
    package.rename(new_package)

    plan = analyze_rename_references(
        tmp_path, package, new_package, is_directory=True
    )
    apply_reference_updates(plan)

    updated = (new_package / "consumer.py").read_text(encoding="utf-8")
    assert "from .old import VALUE" in updated
    assert "from newpkg.old import VALUE as OTHER" in updated


def test_relative_python_file_import_is_updated(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    old_path, new_path = _renamed_file(tmp_path, "pkg/old.py", "pkg/new.py")
    consumer = tmp_path / "pkg" / "consumer.py"
    consumer.write_text("from .old import VALUE\n", encoding="utf-8")

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)
    apply_reference_updates(plan)

    assert consumer.read_text(encoding="utf-8") == "from .new import VALUE\n"


def test_javascript_esm_imports_are_updated_without_blind_replacement(tmp_path):
    old_path, new_path = _renamed_file(
        tmp_path, "lib/old.ts", "lib/new.ts", "export const value = 1;\n"
    )
    consumer = tmp_path / "app.ts"
    consumer.write_text(
        'import { value } from "./lib/old";\n'
        'export { value as other } from "./lib/old.ts";\n'
        'const literal = "./lib/old";\n'
        '// import ignored from "./lib/old";\n'
        '/*\nimport ignored_block from "./lib/old";\n*/\n'
        '`import ignored_template from "./lib/old";`;\n',
        encoding="utf-8",
    )

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)
    apply_reference_updates(plan)

    assert consumer.read_text(encoding="utf-8") == (
        'import { value } from "./lib/new";\n'
        'export { value as other } from "./lib/new.ts";\n'
        'const literal = "./lib/old";\n'
        '// import ignored from "./lib/old";\n'
        '/*\nimport ignored_block from "./lib/old";\n*/\n'
        '`import ignored_template from "./lib/old";`;\n'
    )


def test_utf8_bom_and_crlf_are_preserved(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    consumer = tmp_path / "consumer.py"
    consumer.write_bytes(b"\xef\xbb\xbffrom old import VALUE\r\n")

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)
    apply_reference_updates(plan)

    assert consumer.read_bytes() == b"\xef\xbb\xbffrom new import VALUE\r\n"


def test_symlink_directories_and_excluded_dirty_files_are_not_traversed(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    dirty = tmp_path / "dirty.py"
    dirty.write_text("import old\n", encoding="utf-8")
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    external = outside / "external.py"
    external.write_text("import old\n", encoding="utf-8")
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)

    plan = analyze_rename_references(
        tmp_path,
        old_path,
        new_path,
        is_directory=False,
        excluded_paths={dirty},
    )

    assert plan.change_count == 0
    assert any("modified buffer" in issue for issue in plan.issues)
    assert external.read_text(encoding="utf-8") == "import old\n"


def test_invalid_python_module_name_is_reported_without_writes(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "not-valid.py")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)

    assert plan.change_count == 0
    assert any("Python module" in issue for issue in plan.issues)


def test_ambiguous_python_symbol_and_commonjs_require_are_reported(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "pkg/old.py", "pkg/new.py")
    python_consumer = tmp_path / "consumer.py"
    python_consumer.write_text("from pkg import old\n", encoding="utf-8")
    script = tmp_path / "consumer.js"
    script.write_text('const old = require("./pkg/old");\n', encoding="utf-8")

    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)

    assert plan.change_count == 0
    assert any("module or exported symbol" in issue for issue in plan.issues)
    assert any("CommonJS require" in issue for issue in plan.issues)


def test_file_and_total_budgets_abort_before_any_write(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n" * 20, encoding="utf-8")

    with pytest.raises(ReferenceUpdateError, match="byte limit"):
        analyze_rename_references(
            tmp_path,
            old_path,
            new_path,
            is_directory=False,
            limits=ReferenceUpdateLimits(max_file_bytes=16),
        )

    assert consumer.read_text(encoding="utf-8").startswith("import old")


def test_stale_plan_refuses_to_overwrite_external_change(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    consumer = tmp_path / "consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)
    consumer.write_text("external = True\n", encoding="utf-8")

    with pytest.raises(ReferenceUpdateError, match="changed since analysis"):
        apply_reference_updates(plan)

    assert consumer.read_text(encoding="utf-8") == "external = True\n"


def test_partial_write_failure_rolls_back_completed_files(tmp_path, monkeypatch):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    first = tmp_path / "a.py"
    second = tmp_path / "b.py"
    first.write_text("import old\n", encoding="utf-8")
    second.write_text("import old\n", encoding="utf-8")
    plan = analyze_rename_references(tmp_path, old_path, new_path, is_directory=False)
    real_write = module.write_existing_text_atomically

    def fail_second(path, content, revision):
        if path == str(second):
            raise OSError("simulated write failure")
        return real_write(path, content, revision)

    monkeypatch.setattr(module, "write_existing_text_atomically", fail_second)

    with pytest.raises(ReferenceUpdateError, match="simulated write failure"):
        apply_reference_updates(plan)

    assert first.read_text(encoding="utf-8") == "import old\n"
    assert second.read_text(encoding="utf-8") == "import old\n"


def test_paths_outside_root_and_symlink_roots_are_rejected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    old_path, new_path = _renamed_file(root, "old.py", "new.py")
    outside = tmp_path / "outside.py"

    with pytest.raises(ReferenceUpdateError, match="inside the Explorer root"):
        analyze_rename_references(root, outside, new_path, is_directory=False)

    linked_root = tmp_path / "linked-root"
    linked_root.symlink_to(root, target_is_directory=True)
    with pytest.raises(ReferenceUpdateError, match="symlink"):
        analyze_rename_references(
            linked_root, old_path, new_path, is_directory=False
        )


def test_directory_entry_budget_is_enforced(tmp_path):
    old_path, new_path = _renamed_file(tmp_path, "old.py", "new.py")
    for index in range(4):
        (tmp_path / f"ignored-{index}.txt").write_text("ignored", encoding="utf-8")

    with pytest.raises(ReferenceUpdateError, match="entry limit"):
        analyze_rename_references(
            tmp_path,
            old_path,
            new_path,
            is_directory=False,
            limits=ReferenceUpdateLimits(max_entries=2),
        )

