# Clarify Tool Dock Toggle - 2026-10-26

## Scope

This bounded stage implements `TOOL-DOCK-TOGGLE-01`. It does not add Editor
status indicators or toolbars, alter File Explorer behavior, resume
`APP-THREAD-01`, or start i18n-parity and legacy work.

## Proven Defect

`CE-DOCK-CHROME-01` correctly removed the misleading native `QDockWidget`
float/close buttons from tools embedded in the central `QTabWidget`. A guarded
pre-edit regression proved that no replacement existed: the workspace's
top-right corner widget was `None`. The failing process exited normally at
196.3 MiB with no native crash or guard abort.

## Implementation

`ToolWindowManager` now owns one icon-only, accessible toggle for the current
workspace tool. Detaching moves the existing widget instance into a managed
top-level host; it does not copy or reconstruct the tool. The detached header
contains only the explicit reattach action, while operating-system window
controls remain meaningful for the real top-level window.

Reattachment restores stable tab order, focus and saved geometry. Reopening an
already detached tool raises its window instead of duplicating or silently
redocking it. Session persistence counts detached File Explorer and Insert
tools as open. The layout manager also recognizes managed detached tools.

Closing a detached window first returns the same instance to the workspace and
then invokes `MainWindow._close_tab()`, preserving each tool's existing veto,
recovery and cooperative worker settlement. Accepted application shutdown
reattaches all tools before the existing parent/tool cleanup. Every QWidget
transition rejects calls outside the GUI thread.

The control and detached host update at runtime from six scoped translation
keys present in all seven existing catalogs. Theme styling remains inherited
from the application; no local palette or duplicate native dock chrome was
introduced.

## Validation

Each module ran in its own offscreen process with temporary HOME, disabled core
dumps, pytest timeout 20 seconds, system RAM 85%, process-tree RSS 600 MiB and
wall 180 second guards.

- `tests/gui/test_tool_dock_toggle.py`: 10 passed, peak 200.6 MiB.
- `tests/gui/test_tool_tab_chrome.py`: 4 passed, peak 195.5 MiB.
- `tests/test_tab_layouts.py`: 25 passed, peak 255.8 MiB.
- `tests/gui/test_editor_layout.py`: 20 passed, peak 249.5 MiB.
- `tests/gui/test_editor_recovery_lifecycle.py`: 53 passed, peak 218.3 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 214.7 MiB.
- `tests/gui/test_editor_dock.py`: 69 passed, peak 227.6 MiB.
- `tests/test_i18n_expansion.py`: 14 passed, peak 64.5 MiB.
- `tests/test_translation_catalog_lookup.py`: 10 passed, peak 187.1 MiB.

Total: 241 distinct passing tests. No native crash, timeout or guard abort
occurred. Compilation, Pylint errors-only, scoped Black, all i18n JSON parses
and `git diff --check` passed.

## Boundary

Detached state is intentionally settled back into the central workspace during
normal application shutdown. Persisting tools as detached across a new process
would require a separate, explicitly designed session contract and is not part
of this stage.
