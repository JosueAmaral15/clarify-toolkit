# Clarify Editor Status Info - 2026-10-26

## Scope

This bounded stage implements `CE-STATUS-INFO-01`. It does not add the quick
toolbar, alter File Explorer, resume `APP-THREAD-01`, or start broader i18n,
TOON, WQXR and legacy work.

## Proven Defect

The Clarify Editor status row contained only the transient operation message.
A guarded pre-edit regression proved that no persistent indentation, cursor or
language widgets existed: construction failed on the missing
`status_indent_label` attribute. The process exited normally at 200.8 MiB with
no native crash or guard abort.

## Implementation

The status row now has three fixed-width indicators for indentation mode and
width, active line and column, and detected language. The complete translated
text is retained as the accessible name and tooltip while only the visible
caption is elided, so long translations do not resize the editor layout.

The cursor indicator follows the active file tab or split view. Status refreshes
also cover indentation preference changes, Save As, Explorer rename, generated
content and runtime language changes. Existing tab, split, recovery, temporary
note, watcher and folder-session ownership remains unchanged.

Language detection reuses path, generated-content and syntax-highlighter
metadata. Known extensions are mapped without reading document content;
unknown explicit extensions fall back to `Plain Text`. Only metadata-free,
extensionless buffers inspect content, and then only the first document block,
bounded to 512 characters, for a common shebang. No parser, timer, worker or
whole-document extraction was added. Six templates are present in all seven
translation catalogs.

## Validation

Each Qt module ran in its own offscreen process with temporary HOME, disabled
core dumps, pytest timeout 20 seconds, system RAM 85%, process-tree RSS 600 MiB
and wall 180 second guards.

- `tests/gui/test_editor_status_info.py`: 9 passed, peak 212.3 MiB.
- `tests/gui/test_editor_layout.py`: 20 passed, peak 245.3 MiB.
- `tests/gui/test_editor_priority_stage1.py`: 6 passed, peak 209.5 MiB.
- `tests/gui/test_editor_priority_stage3.py`: 8 passed, peak 200.2 MiB.
- `tests/gui/test_editor_priority_stage4_tabs.py`: 8 passed, peak 209.1 MiB.
- `tests/gui/test_editor_priority_stage5_sessions.py`: 12 passed, peak 213.1 MiB.
- `tests/gui/test_editor_priority_stage5_notes.py`: 5 passed, peak 203.5 MiB.
- `tests/gui/test_editor_recovery_lifecycle.py`: 53 passed, peak 220.5 MiB.
- `tests/gui/test_editor_dock.py`: 69 passed, peak 228.0 MiB.
- `tests/gui/test_editor_smart_home_visual.py`: 7 passed, peak 202.3 MiB.
- `tests/gui/test_tool_dock_toggle.py`: 10 passed, peak 204.7 MiB.
- `tests/test_i18n_expansion.py`: 14 passed, peak 66.3 MiB.
- `tests/test_translation_catalog_lookup.py`: 10 passed, peak 187.2 MiB.

Total: 231 distinct passing tests. No native crash, timeout or guard abort
occurred. Compilation, Pylint errors-only, scoped Black for the new test and
diagnostic, all i18n JSON parses and `git diff --check` passed. Whole-file Black
was not applied to the pre-existing `editor_dock.py` because it would reformat
unrelated legacy code.

## Boundary

Language names such as Python, JSON and TypeScript remain conventional proper
names. The surrounding indicator and `Plain Text` fallback are translated.
Semantic content-based language classification would require a separate,
explicitly bounded feature and is not part of this stage.
