"""Bounded import updates for file and folder renames in Clarify Editor."""

from __future__ import annotations

import ast
import io
import os
import re
import stat
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from src.utils.atomic_files import (
    file_revision,
    write_existing_text_atomically,
)


PYTHON_EXTENSIONS = {".py", ".pyi"}
JAVASCRIPT_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
SUPPORTED_EXTENSIONS = PYTHON_EXTENSIONS | JAVASCRIPT_EXTENSIONS
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}


class ReferenceUpdateError(RuntimeError):
    """A safe reference analysis or update could not be completed."""


@dataclass(frozen=True)
class ReferenceUpdateLimits:
    """Hard limits for one local rename analysis."""

    max_files: int = 2_000
    max_entries: int = 20_000
    max_file_bytes: int = 2 * 1024 * 1024
    max_total_bytes: int = 32 * 1024 * 1024
    max_changes: int = 5_000
    max_issues: int = 200
    max_preview_changes: int = 200


@dataclass(frozen=True)
class ReferenceChange:
    """One parser-owned source span that will be changed."""

    line: int
    column: int
    start: int
    end: int
    old_text: str
    new_text: str
    language: str


@dataclass(frozen=True)
class ReferenceFileUpdate:
    """Immutable, revision-bound replacement for one regular file."""

    path: str
    original_text: str
    updated_text: str
    expected_revision: tuple
    changes: tuple[ReferenceChange, ...]


@dataclass(frozen=True)
class ReferenceUpdatePlan:
    """A previewable collection of bounded file updates."""

    root: str
    old_path: str
    new_path: str
    updates: tuple[ReferenceFileUpdate, ...]
    issues: tuple[str, ...]
    scanned_files: int
    scanned_bytes: int
    limits: ReferenceUpdateLimits

    @property
    def change_count(self) -> int:
        return sum(len(update.changes) for update in self.updates)

    def preview(self) -> str:
        """Return a bounded human-readable diff preview."""
        lines = []
        shown = 0
        for update in self.updates:
            relative = os.path.relpath(update.path, self.root)
            before_lines = update.original_text.lstrip("\ufeff").splitlines()
            after_lines = update.updated_text.lstrip("\ufeff").splitlines()
            for change in update.changes:
                if shown >= self.limits.max_preview_changes:
                    break
                before = before_lines[change.line - 1] if change.line <= len(before_lines) else change.old_text
                after = after_lines[change.line - 1] if change.line <= len(after_lines) else change.new_text
                lines.extend((f"{relative}:{change.line}", f"- {before}", f"+ {after}"))
                shown += 1
            if shown >= self.limits.max_preview_changes:
                break
        if shown < self.change_count:
            lines.append(f"... {self.change_count - shown} additional change(s) not shown")
        if self.issues:
            lines.append(f"Issues reported: {len(self.issues)}")
        return "\n".join(lines)


@dataclass(frozen=True)
class _AppliedFile:
    path: str
    original_text: str
    updated_text: str
    applied_revision: tuple


@dataclass
class AppliedReferenceUpdate:
    """Successfully applied transaction that can be rolled back once."""

    files: tuple[_AppliedFile, ...]
    _rolled_back: bool = field(default=False, init=False)

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(item.path for item in self.files)

    def rollback(self) -> None:
        """Restore all originals if none of the updated files changed afterward."""
        if self._rolled_back:
            raise ReferenceUpdateError("Reference updates were already rolled back")
        for item in self.files:
            try:
                current = os.lstat(item.path)
            except OSError as error:
                raise ReferenceUpdateError(
                    f"Cannot undo reference updates; file is unavailable: {item.path}"
                ) from error
            if file_revision(current) != item.applied_revision:
                raise ReferenceUpdateError(
                    f"Cannot undo reference updates; file changed afterward: {item.path}"
                )

        restored: list[tuple[_AppliedFile, tuple]] = []
        try:
            for item in reversed(self.files):
                write_existing_text_atomically(
                    item.path, item.original_text, item.applied_revision
                )
                restored.append((item, file_revision(os.lstat(item.path))))
        except (OSError, ValueError) as error:
            repair_errors = []
            for item, restored_revision in reversed(restored):
                try:
                    write_existing_text_atomically(
                        item.path, item.updated_text, restored_revision
                    )
                except (OSError, ValueError) as repair_error:
                    repair_errors.append(f"{item.path}: {repair_error}")
            detail = f"; repair failures: {'; '.join(repair_errors)}" if repair_errors else ""
            raise ReferenceUpdateError(f"Could not undo reference updates: {error}{detail}") from error
        self._rolled_back = True


class _IssueCollector:
    def __init__(self, limit: int):
        self.limit = limit
        self.items: list[str] = []
        self.omitted = 0

    def add(self, message: str) -> None:
        if len(self.items) < self.limit:
            self.items.append(message)
        else:
            self.omitted += 1

    def result(self) -> tuple[str, ...]:
        if self.omitted:
            return tuple(self.items + [f"{self.omitted} additional issue(s) omitted"])
        return tuple(self.items)


def _absolute(path) -> str:
    return os.path.abspath(os.path.normpath(os.fspath(path)))


def _inside(path: str, root: str) -> bool:
    try:
        return os.path.commonpath([root, path]) == root
    except ValueError:
        return False


def _validate_paths(root, old_path, new_path) -> tuple[str, str, str]:
    root_path = _absolute(root)
    old = _absolute(old_path)
    new = _absolute(new_path)
    try:
        root_info = os.lstat(root_path)
    except OSError as error:
        raise ReferenceUpdateError(f"Explorer root is unavailable: {root_path}") from error
    if stat.S_ISLNK(root_info.st_mode):
        raise ReferenceUpdateError("Explorer root must not be a symlink")
    if not stat.S_ISDIR(root_info.st_mode):
        raise ReferenceUpdateError("Explorer root must be a directory")
    canonical_root = os.path.realpath(root_path)
    if not _inside(old, canonical_root) or not _inside(new, canonical_root):
        raise ReferenceUpdateError("Renamed paths must remain inside the Explorer root")
    if not _inside(os.path.realpath(os.path.dirname(old)), canonical_root):
        raise ReferenceUpdateError("Original parent must remain inside the Explorer root")
    try:
        new_info = os.lstat(new)
    except OSError as error:
        raise ReferenceUpdateError(f"Renamed item is unavailable: {new}") from error
    if stat.S_ISLNK(new_info.st_mode):
        raise ReferenceUpdateError("Renamed item must not be a symlink")
    if not _inside(os.path.realpath(new), canonical_root):
        raise ReferenceUpdateError("Renamed item must not traverse a symlink outside the Explorer root")
    return canonical_root, old, new


def _module_name(root: str, path: str, is_directory: bool) -> str | None:
    relative = os.path.relpath(path, root)
    parts = list(Path(relative).parts)
    if not is_directory:
        suffix = Path(parts[-1]).suffix.lower()
        if suffix not in PYTHON_EXTENSIONS:
            return None
        parts[-1] = Path(parts[-1]).stem
        if parts[-1] == "__init__":
            parts.pop()
    if not parts or not all(part.isidentifier() for part in parts):
        return None
    return ".".join(parts)


def _map_module(name: str, old_module: str, new_module: str) -> str | None:
    if name == old_module:
        return new_module
    prefix = old_module + "."
    if name.startswith(prefix):
        return new_module + name[len(old_module) :]
    return None


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    for match in re.finditer("\n", text):
        offsets.append(match.end())
    return offsets


def _absolute_offset(offsets: list[int], position: tuple[int, int]) -> int:
    line, column = position
    return offsets[line - 1] + column


def _ast_offset(text: str, offsets: list[int], line: int, byte_column: int) -> int:
    line_start = offsets[line - 1]
    line_end = text.find("\n", line_start)
    if line_end < 0:
        line_end = len(text)
    line_text = text[line_start:line_end]
    prefix = line_text.encode("utf-8")[:byte_column].decode("utf-8")
    return line_start + len(prefix)


def _python_changes(
    text: str,
    path: str,
    root: str,
    old_module: str | None,
    new_module: str | None,
    issues: _IssueCollector,
) -> list[ReferenceChange]:
    if not old_module or not new_module:
        return []
    try:
        tree = ast.parse(text, filename=path)
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (SyntaxError, IndentationError, tokenize.TokenError) as error:
        issues.add(f"{os.path.relpath(path, root)}: Python parse failed: {error}")
        return []

    offsets = _line_offsets(text)
    changes: list[ReferenceChange] = []
    importer_relative = os.path.relpath(path, root)
    importer_parts = list(Path(importer_relative).parts[:-1])

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                replacement = _map_module(alias.name, old_module, new_module)
                if replacement is None:
                    continue
                start = _ast_offset(text, offsets, alias.lineno, alias.col_offset)
                end = start + len(alias.name)
                if text[start:end] != alias.name:
                    issues.add(
                        f"{importer_relative}:{alias.lineno}: ambiguous import span"
                    )
                    continue
                changes.append(
                    ReferenceChange(
                        alias.lineno,
                        alias.col_offset,
                        start,
                        end,
                        alias.name,
                        replacement,
                        "python",
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                keep = len(importer_parts) - (node.level - 1)
                if keep < 0:
                    issues.add(
                        f"{importer_relative}:{node.lineno}: relative import escapes project package"
                    )
                    continue
                base_parts = importer_parts[:keep]
                absolute_name = ".".join(
                    base_parts + (node.module.split(".") if node.module else [])
                )
            else:
                base_parts = []
                absolute_name = node.module or ""

            old_parts = old_module.split(".")
            if (
                old_parts
                and absolute_name == ".".join(old_parts[:-1])
                and any(alias.name == old_parts[-1] for alias in node.names)
            ):
                issues.add(
                    f"{importer_relative}:{node.lineno}: imported name may be a module or exported symbol"
                )

            if not node.module:
                continue
            if node.level:
                mapped = _map_module(absolute_name, old_module, new_module)
                if mapped is None:
                    continue
                mapped_parts = mapped.split(".")
                if mapped_parts[: len(base_parts)] != base_parts:
                    issues.add(
                        f"{importer_relative}:{node.lineno}: relative import needs a level change"
                    )
                    continue
                replacement = ".".join(mapped_parts[len(base_parts) :])
                if not replacement:
                    issues.add(
                        f"{importer_relative}:{node.lineno}: relative import target is ambiguous"
                    )
                    continue
            else:
                replacement = _map_module(node.module, old_module, new_module)
                if replacement is None:
                    continue

            node_start = _ast_offset(text, offsets, node.lineno, node.col_offset)
            node_end = _ast_offset(text, offsets, node.end_lineno, node.end_col_offset)
            relevant = [
                token
                for token in tokens
                if node_start <= _absolute_offset(offsets, token.start) < node_end
            ]
            try:
                from_index = next(
                    index
                    for index, token in enumerate(relevant)
                    if token.type == tokenize.NAME and token.string == "from"
                )
                import_index = next(
                    index
                    for index, token in enumerate(relevant[from_index + 1 :], from_index + 1)
                    if token.type == tokenize.NAME and token.string == "import"
                )
                module_tokens = [
                    token
                    for token in relevant[from_index + 1 : import_index]
                    if token.type == tokenize.NAME
                ]
                first, last = module_tokens[0], module_tokens[-1]
            except (StopIteration, IndexError):
                issues.add(f"{importer_relative}:{node.lineno}: ambiguous from-import span")
                continue
            start = _absolute_offset(offsets, first.start)
            end = _absolute_offset(offsets, last.end)
            old_text = text[start:end]
            if old_text.replace(" ", "") != node.module:
                issues.add(f"{importer_relative}:{node.lineno}: formatted import is unsupported")
                continue
            changes.append(
                ReferenceChange(
                    first.start[0],
                    first.start[1],
                    start,
                    end,
                    old_text,
                    replacement,
                    "python",
                )
            )
    return changes


_ESM_IMPORT = re.compile(
    r"(?m)^[ \t]*(?:import|export)\b[^;\r\n]*?(?:\bfrom[ \t]*)?"
    r"(?P<quote>['\"])(?P<specifier>[^'\"\r\n]+)(?P=quote)"
)
_REQUIRE_CALL = re.compile(
    r"\brequire[ \t]*\([ \t]*(?P<quote>['\"])(?P<specifier>[^'\"\r\n]+)(?P=quote)"
)


def _javascript_code_mask(text: str) -> bytearray:
    """Mark positions outside comments, quoted strings and template literals."""
    mask = bytearray(b"\x01") * len(text)
    state = "code"
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                mask[index] = mask[index + 1] = 0
                state = "line_comment"
                index += 2
                continue
            if char == "/" and following == "*":
                mask[index] = mask[index + 1] = 0
                state = "block_comment"
                index += 2
                continue
            if char in {"'", '"', "`"}:
                mask[index] = 0
                state = {"'": "single", '"': "double", "`": "template"}[char]
                escaped = False
        else:
            mask[index] = 0
            if state == "line_comment" and char in "\r\n":
                state = "code"
                mask[index] = 1
            elif state == "block_comment" and char == "*" and following == "/":
                mask[index + 1] = 0
                state = "code"
                index += 2
                continue
            elif state in {"single", "double", "template"}:
                delimiter = {"single": "'", "double": '"', "template": "`"}[state]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == delimiter:
                    state = "code"
        index += 1
    return mask


def _reverse_renamed_path(path: str, old_path: str, new_path: str, is_directory: bool) -> str:
    if is_directory and _inside(path, new_path):
        return os.path.join(old_path, os.path.relpath(path, new_path))
    if not is_directory and path == new_path:
        return old_path
    return path


def _mapped_target(path: str, old_path: str, new_path: str, is_directory: bool) -> str | None:
    if is_directory and _inside(path, old_path):
        return os.path.join(new_path, os.path.relpath(path, old_path))
    if not is_directory:
        old_without_suffix = os.path.splitext(old_path)[0]
        if path == old_path:
            return new_path
        if path == old_without_suffix:
            return os.path.splitext(new_path)[0]
    return None


def _relative_specifier(importer: str, target: str) -> str:
    relative = os.path.relpath(target, os.path.dirname(importer)).replace(os.sep, "/")
    return relative if relative.startswith(".") else f"./{relative}"


def _javascript_changes(
    text: str,
    path: str,
    root: str,
    old_path: str,
    new_path: str,
    is_directory: bool,
    issues: _IssueCollector,
) -> list[ReferenceChange]:
    changes = []
    code_mask = _javascript_code_mask(text)
    old_importer = _reverse_renamed_path(path, old_path, new_path, is_directory)
    old_name = os.path.basename(old_path).split(".", 1)[0]
    for match in _ESM_IMPORT.finditer(text):
        first_code = match.start()
        while first_code < match.end() and text[first_code] in " \t":
            first_code += 1
        if first_code >= len(code_mask) or not code_mask[first_code]:
            continue
        specifier = match.group("specifier")
        line = text.count("\n", 0, match.start("specifier")) + 1
        column = match.start("specifier") - (text.rfind("\n", 0, match.start("specifier")) + 1)
        if not specifier.startswith(("./", "../")):
            if old_name and old_name in specifier.split("/"):
                issues.add(
                    f"{os.path.relpath(path, root)}:{line}: non-relative module specifier is ambiguous"
                )
            continue
        if "?" in specifier or "#" in specifier:
            issues.add(
                f"{os.path.relpath(path, root)}:{line}: import query/hash is unsupported"
            )
            continue
        old_target = _absolute(os.path.join(os.path.dirname(old_importer), specifier))
        new_target = _mapped_target(old_target, old_path, new_path, is_directory)
        if new_target is None:
            continue
        replacement = _relative_specifier(path, new_target)
        changes.append(
            ReferenceChange(
                line,
                column,
                match.start("specifier"),
                match.end("specifier"),
                specifier,
                replacement,
                "javascript",
            )
        )
    for match in _REQUIRE_CALL.finditer(text):
        if not code_mask[match.start()]:
            continue
        specifier = match.group("specifier")
        if not specifier.startswith(("./", "../")):
            continue
        old_target = _absolute(os.path.join(os.path.dirname(old_importer), specifier))
        if _mapped_target(old_target, old_path, new_path, is_directory) is not None:
            line = text.count("\n", 0, match.start()) + 1
            issues.add(
                f"{os.path.relpath(path, root)}:{line}: CommonJS require target is ambiguous"
            )
    return changes


def _apply_spans(text: str, changes: Iterable[ReferenceChange]) -> str:
    result = text
    for change in sorted(changes, key=lambda item: item.start, reverse=True):
        if result[change.start : change.end] != change.old_text:
            raise ReferenceUpdateError("Parser span no longer matches analyzed text")
        result = result[: change.start] + change.new_text + result[change.end :]
    return result


def _iter_source_files(root: str, max_entries: int):
    stack = [root]
    visited_entries = 0
    while stack:
        directory = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as error:
            raise ReferenceUpdateError(f"Cannot scan directory: {directory}: {error}") from error
        for entry in entries:
            visited_entries += 1
            if visited_entries > max_entries:
                raise ReferenceUpdateError(
                    f"Directory entry limit exceeded ({max_entries})"
                )
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if entry.name not in IGNORED_DIRECTORIES:
                        stack.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    if Path(entry.name).suffix.lower() in SUPPORTED_EXTENSIONS:
                        yield entry.path
            except OSError as error:
                raise ReferenceUpdateError(f"Cannot inspect path: {entry.path}: {error}") from error


def analyze_rename_references(
    root,
    old_path,
    new_path,
    *,
    is_directory: bool,
    excluded_paths: Iterable[os.PathLike | str] = (),
    limits: ReferenceUpdateLimits | None = None,
) -> ReferenceUpdatePlan:
    """Build an immutable update plan without modifying project files."""
    active_limits = limits or ReferenceUpdateLimits()
    canonical_root, old, new = _validate_paths(root, old_path, new_path)
    excluded = {_absolute(path) for path in excluded_paths}
    issues = _IssueCollector(active_limits.max_issues)
    old_module = _module_name(canonical_root, old, is_directory)
    new_module = _module_name(canonical_root, new, is_directory)
    updates = []
    scanned_files = 0
    scanned_bytes = 0
    total_changes = 0

    python_target = is_directory or Path(old).suffix.lower() in PYTHON_EXTENSIONS
    if python_target and (not old_module or not new_module):
        issues.add("Renamed path is not a valid Python module path")

    for path in _iter_source_files(canonical_root, active_limits.max_entries):
        normalized = _absolute(path)
        if normalized in excluded:
            issues.add(f"{os.path.relpath(path, canonical_root)}: skipped modified buffer")
            continue
        scanned_files += 1
        if scanned_files > active_limits.max_files:
            raise ReferenceUpdateError(
                f"Source file limit exceeded ({active_limits.max_files})"
            )
        try:
            info = os.lstat(path)
        except OSError as error:
            raise ReferenceUpdateError(f"Cannot inspect source file: {path}: {error}") from error
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            issues.add(f"{os.path.relpath(path, canonical_root)}: linked file skipped")
            continue
        if info.st_size > active_limits.max_file_bytes:
            raise ReferenceUpdateError(
                f"Per-file byte limit exceeded ({active_limits.max_file_bytes}): {path}"
            )
        scanned_bytes += info.st_size
        if scanned_bytes > active_limits.max_total_bytes:
            raise ReferenceUpdateError(
                f"Total byte limit exceeded ({active_limits.max_total_bytes})"
            )
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        try:
            descriptor = os.open(path, flags)
            with os.fdopen(descriptor, "rb") as handle:
                opened_info = os.fstat(handle.fileno())
                if not stat.S_ISREG(opened_info.st_mode):
                    raise ReferenceUpdateError(f"Source is not a regular file: {path}")
                if file_revision(opened_info) != file_revision(info):
                    raise ReferenceUpdateError(f"Source file changed before reading: {path}")
                raw = handle.read(active_limits.max_file_bytes + 1)
        except OSError as error:
            raise ReferenceUpdateError(f"Cannot read source file: {path}: {error}") from error
        if len(raw) > active_limits.max_file_bytes:
            raise ReferenceUpdateError(
                f"Per-file byte limit exceeded ({active_limits.max_file_bytes}): {path}"
            )
        if file_revision(os.lstat(path)) != file_revision(info):
            raise ReferenceUpdateError(f"Source file changed during analysis: {path}")
        if b"\x00" in raw:
            issues.add(f"{os.path.relpath(path, canonical_root)}: binary content skipped")
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            issues.add(
                f"{os.path.relpath(path, canonical_root)}: unsupported non-UTF-8 encoding"
            )
            continue
        has_bom = decoded.startswith("\ufeff")
        text = decoded[1:] if has_bom else decoded
        suffix = Path(path).suffix.lower()
        if suffix in PYTHON_EXTENSIONS:
            changes = _python_changes(
                text, path, canonical_root, old_module, new_module, issues
            )
        else:
            changes = _javascript_changes(
                text, path, canonical_root, old, new, is_directory, issues
            )
        if not changes:
            continue
        total_changes += len(changes)
        if total_changes > active_limits.max_changes:
            raise ReferenceUpdateError(
                f"Reference change limit exceeded ({active_limits.max_changes})"
            )
        updated = _apply_spans(text, changes)
        if has_bom:
            text = "\ufeff" + text
            updated = "\ufeff" + updated
        updates.append(
            ReferenceFileUpdate(
                path=path,
                original_text=text,
                updated_text=updated,
                expected_revision=file_revision(info),
                changes=tuple(sorted(changes, key=lambda item: item.start)),
            )
        )

    return ReferenceUpdatePlan(
        root=canonical_root,
        old_path=old,
        new_path=new,
        updates=tuple(updates),
        issues=issues.result(),
        scanned_files=scanned_files,
        scanned_bytes=scanned_bytes,
        limits=active_limits,
    )


def apply_reference_updates(plan: ReferenceUpdatePlan) -> AppliedReferenceUpdate:
    """Apply a plan atomically per file and roll back on a partial failure."""
    for update in plan.updates:
        try:
            current_revision = file_revision(os.lstat(update.path))
        except OSError as error:
            raise ReferenceUpdateError(
                f"File is unavailable since analysis: {update.path}"
            ) from error
        if current_revision != update.expected_revision:
            raise ReferenceUpdateError(
                f"File changed since analysis; update cancelled: {update.path}"
            )

    applied: list[_AppliedFile] = []
    try:
        for update in plan.updates:
            write_existing_text_atomically(
                update.path, update.updated_text, update.expected_revision
            )
            applied.append(
                _AppliedFile(
                    update.path,
                    update.original_text,
                    update.updated_text,
                    file_revision(os.lstat(update.path)),
                )
            )
    except (OSError, ValueError) as error:
        rollback_errors = []
        for item in reversed(applied):
            try:
                write_existing_text_atomically(
                    item.path, item.original_text, item.applied_revision
                )
            except (OSError, ValueError) as rollback_error:
                rollback_errors.append(f"{item.path}: {rollback_error}")
        detail = f"; rollback failures: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise ReferenceUpdateError(f"Reference update failed: {error}{detail}") from error
    return AppliedReferenceUpdate(tuple(applied))


__all__ = [
    "AppliedReferenceUpdate",
    "ReferenceChange",
    "ReferenceFileUpdate",
    "ReferenceUpdateError",
    "ReferenceUpdateLimits",
    "ReferenceUpdatePlan",
    "analyze_rename_references",
    "apply_reference_updates",
]
