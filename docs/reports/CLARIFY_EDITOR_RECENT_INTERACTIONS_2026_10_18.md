# Clarify Editor Recent Interactions - 2026-10-18

## Scope

This bounded stage implements four of the six newly prioritized Editor tasks:

- prefill Find and Find/Replace from the active text selection;
- preserve current-line indentation when Enter is pressed;
- provide VS Code-style smart Home and Shift+Home behavior;
- navigate Editor file tabs with configurable Ctrl+Alt+PageUp/PageDown actions.

Dock chrome and rename-aware import updates remain separate stages. The work did
not modify File Explorer workers, document recovery, user files, main or develop.

## Implementation

`EditorDock` reuses its existing per-editor event filter. Return/Enter inherits
only the indentation already present before the cursor, avoiding duplicated
whitespace when splitting inside the prefix. Home alternates between the first
non-whitespace character and physical column zero; Shift preserves the anchor.

Find and Find/Replace normalize Qt paragraph separators in the active selection,
bound the query with the existing `MAX_QUERY_CHARS`, and leave the saved Find
options unchanged. File-tab navigation is circular, scoped to the Editor's tab
widget and registered in `ShortcutManager`; tool navigation remains on
Ctrl+PageUp/PageDown. The two new labels exist in all seven translation catalogs.

## Validation

Each Qt module ran offscreen in its own process with a temporary HOME, 20-second
pytest timeouts, disabled core dumps and guards for system RAM 85%, process-tree
RSS 600 MiB and wall time 180 seconds.

- `tests/gui/test_editor_recent_interactions.py`: 7 passed, peak 204.6 MiB.
- `tests/gui/test_editor_priority_stage1.py`: 5 passed, peak 206.3 MiB.
- `tests/gui/test_editor_priority_stage3.py`: 8 passed, peak 198.8 MiB.
- `tests/gui/test_editor_dock.py`: 69 passed, peak 226.3 MiB.
- `tests/test_keyboard_shortcuts.py`: 26 passed, peak 62.7 MiB.

Total: 115 distinct passing tests. No native crash, timeout or guard abort
occurred. The first full Editor run found one stale exact-menu expectation; its
other 68 tests passed, and the expectation was updated for the two intentional
View actions before the clean 69-case rerun.

`py_compile`, `git diff --check`, Pylint errors-only for production files and the
new test, and JSON parsing/key-presence checks for all seven catalogs passed. The
older broad Editor test module still reports its pre-existing Pylint `E0611`
false positives for dynamic PySide6/Shiboken imports; this stage does not claim a
lint cleanup of that legacy module.

## Remaining Recent Work

- `CE-DOCK-CHROME-01`: replace misleading inner dock window controls with the
  correct dock/undock contract.
- `CE-RENAME-IMPORTS-01`: provide bounded language-aware reference previews and
  confirmed atomic updates after Explorer rename.
