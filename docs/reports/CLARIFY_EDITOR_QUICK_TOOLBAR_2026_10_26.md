# Clarify Editor Quick Toolbar - 2026-10-26

## Scope

This bounded stage implements `CE-QUICK-TOOLBAR-01`. It does not alter File
Explorer, resume `APP-THREAD-01`, or start recovery, broader i18n, TOON, WQXR
and legacy work.

## Proven Defect

The Clarify Editor exposed only its local File/Edit/View/JSON menu row. Its
older per-tab toolbar belongs to edit-only tab internals and is deliberately
hidden by `EditorDock`; no shared quick toolbar existed. A guarded pre-edit
regression failed on the missing `quick_toolbar` attribute at 200.6 MiB, with
no native crash or guard abort.

## Implementation

A non-movable, non-floating `QToolBar` now sits directly below the menu. It
contains icon-only New, Open, Save, Undo, Redo, Cut, Copy, Paste, Find and Find
and Replace commands, grouped by separators. No extra command was added.

Every button uses the exact `QAction` already owned by the menus. Consequently,
enabled state, configurable shortcuts, handlers and active tab/split routing
remain one shared contract. A toolbar click emits that shared action once; no
parallel button callback exists.

Icons first use the desktop theme and then a Qt standard fallback, so the
toolbar does not add assets or dependencies. Fixed 20 px icons and Qt's native
toolbar overflow behavior keep the row bounded. Full translated labels remain
available as tooltips and accessible names while no text is painted beside an
icon.

The Editor's existing runtime language signal now retranslates its menu titles,
shared action labels/tooltips, quick-toolbar accessibility and status row. The
22 keys used by the ten commands and toolbar itself are present exactly once in
all seven catalogs. Existing unrelated duplicate Google Translate keys in
`es.json` were observed but intentionally left outside this stage.

## Validation

Each Qt module ran in its own offscreen process with temporary HOME, disabled
core dumps, pytest timeout 20 seconds, system RAM 85%, process-tree RSS 600 MiB
and wall 180 second guards.

- `tests/gui/test_editor_quick_toolbar.py`: 8 passed, peak 225.8 MiB.
- `tests/gui/test_editor_layout.py`: 20 passed, peak 247.5 MiB.
- `tests/gui/test_editor_dock.py`: 69 passed, peak 226.8 MiB.
- `tests/gui/test_editor_redo_shortcuts.py`: 6 passed, peak 209.0 MiB.
- `tests/gui/test_editor_find_state_history.py`: 9 passed, peak 202.2 MiB.
- `tests/gui/test_editor_priority_stage1.py`: 6 passed, peak 209.8 MiB.
- `tests/gui/test_editor_priority_stage3.py`: 8 passed, peak 200.2 MiB.
- `tests/gui/test_editor_priority_stage4_tabs.py`: 8 passed, peak 207.9 MiB.
- `tests/gui/test_editor_priority_stage5_sessions.py`: 12 passed, peak 215.2 MiB.
- `tests/gui/test_editor_priority_stage5_notes.py`: 5 passed, peak 203.8 MiB.
- `tests/gui/test_editor_recovery_lifecycle.py`: 53 passed, peak 218.7 MiB.
- `tests/gui/test_editor_status_info.py`: 9 passed, peak 212.0 MiB.
- `tests/gui/test_tool_dock_toggle.py`: 10 passed, peak 199.2 MiB.
- `tests/test_i18n_expansion.py`: 14 passed, peak 63.9 MiB.
- `tests/test_translation_catalog_lookup.py`: 10 passed, peak 185.8 MiB.

Total: 247 distinct passing tests. No native crash, timeout or guard abort
occurred. Compilation, Pylint errors-only, scoped Black, toolbar-key JSON
uniqueness and `git diff --check` passed.

Offscreen visual checks at 1100x720, the Editor's existing 573x520 minimum and
900x600 dark theme confirmed that menu, toolbar, workspace and status remain
separate, visible and non-overlapping.

## Boundary

The toolbar intentionally contains only the ten commands named by the task.
Adding customization, persistence, labels beside icons or more actions requires
a separate UX contract and is not part of this stage.
