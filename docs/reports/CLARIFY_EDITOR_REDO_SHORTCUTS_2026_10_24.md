# Clarify Editor Redo Shortcuts

Date: 2026-10-24
Task: `CE-REDO-SHORTCUT-01`

## Reproduction

The pre-edit real-widget probe established three defects:

- the Editor Redo QAction exposed only `Ctrl+Y` and ignored the configured
  `ShortcutManager` value;
- `Ctrl+Y` and `Ctrl+Shift+Z` were consumed directly by `QTextEdit`, so neither
  key emitted the Editor QAction;
- when the split view was active, triggering the action still invoked
  `redo()` on the primary view.

The content happened to change for both native QTextEdit keys on this Linux Qt
runtime, but that bypassed the shared action, status and configurable contract.

## Repair

- `ShortcutManager` now supports bounded default aliases. Redo uses `Ctrl+Y`
  and `Ctrl+Shift+Z`; a user customization replaces that complete default set.
- Conflict detection and action registration inspect every active sequence.
- The Editor action uses the manager and `WidgetWithChildrenShortcut`, keeping
  it inside the Editor tool.
- Editor key filtering consumes a matching key once and triggers the same
  QAction, preventing the native text widget from performing a second Redo.
- Redo resolves `_active_editor_for_tab()` and refuses read-only views or an
  empty redo stack without reporting a false success.

The tests use Qt portable key combinations, which validates the application
mapping independently of localized key labels. A physical alternate keyboard
layout was not available in the offscreen environment.

## Validation

Each module ran in a separate process with temporary `HOME`, offscreen Qt,
system RAM limit 85%, process-tree RSS limit 600 MiB, wall limit 180 seconds,
and pytest timeout 20 seconds.

| Scope | Result | Peak tree RSS |
| --- | ---: | ---: |
| Focused Editor Redo behavior | 6 passed | 205.6 MiB |
| Shortcut alias manager | 3 passed | 67.2 MiB |
| Existing shortcut manager | 26 passed | 61.1 MiB |
| Existing Editor tabs and splits | 8 passed | 207.4 MiB |
| Existing Editor dock | 69 passed | 226.0 MiB |

Total: 112 distinct tests passed. The first focused run passed all six product
assertions but failed fixture teardown because a test-owned `QMainWindow`
deleted its dock child first. The test now detaches the dock before teardown;
the rerun passed. This was not a native crash or product lifecycle failure.

Python compilation, Pylint error checks, scoped Black checks and
`git diff --check` passed. No provider, real user document, native crash,
timeout or resource guard was involved.
