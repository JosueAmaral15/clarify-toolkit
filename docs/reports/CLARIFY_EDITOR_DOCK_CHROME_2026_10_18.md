# Clarify Editor Dock Chrome - 2026-10-18

## Scope

This bounded stage addresses `CE-DOCK-CHROME-01`, based on the controls marked
in `docs/Screenshot from 2026-10-18 02-14-46.png`. It does not add a new detach
feature, alter main-window controls, change Editor recovery or start rename-aware
import updates.

## Proven Defect

Clarify's tools inherit `QDockWidget`, but the current workspace places them
inside the central `QTabWidget`. A runtime probe of the real `EditorDock` showed:

- parent: the tab widget's internal `QStackedWidget`;
- dock area: `NoDockWidgetArea`;
- default features: `Closable|Movable|Floatable`;
- no custom title bar.

Those defaults render the two inner controls highlighted by the user. The close
control can hide the dock without using `MainWindow._close_tab()` and its
`request_tab_close()`/recovery contract. The float control is also incomplete:
in an isolated Qt probe it created a top-level window, but `setFloating(False)`
could not reattach it because the widget had never belonged to a main-window
dock area. Presenting either control therefore advertised behavior the tab
workspace does not safely support.

## Implementation

`TabManager.prepare_embedded_tool()` now prepares only `QDockWidget` instances
that enter the real `_add_tool_tab()` route. It stores their original native
features/title widget for a future explicit detach implementation, sets
`NoDockWidgetFeatures`, and installs a zero-height, non-interactive title widget.
Ordinary tab pages such as Insert are unchanged. Reopening a tool is idempotent.

Closing remains exclusively on the main tab bar, where `request_tab_close()` can
veto removal and preserve recovery. Main-window maximize/close flags are not
modified. An offscreen render of the real `EditorDock` showed the content starts
directly below the tool tab, with no inner float/close buttons; the host retained
both maximize and close flags.

## Validation

Each Qt module ran offscreen in a separate process with temporary HOME, disabled
core dumps, pytest timeout 20 seconds, and system RAM 85%, process-tree RSS
600 MiB and wall 180 second guards.

- `tests/gui/test_tool_tab_chrome.py`: 4 passed, peak 194.4 MiB.
- `tests/test_tab_layouts.py`: 25 passed, peak 253.6 MiB.
- `tests/gui/test_editor_layout.py`: 20 passed, peak 248.7 MiB.
- `tests/gui/test_editor_recovery_lifecycle.py`: 53 passed, peak 216.7 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak 214.3 MiB.

Total: 138 distinct passing tests. No native crash, timeout or guard abort
occurred. `py_compile`, Pylint errors-only and `git diff --check` passed.

## Boundary

A future detach feature must remove the tool from the tab model, provide one
explicit attach action, preserve layout/tool identity and route floating-window
close through the same settlement contract. Merely restoring Qt's native float
button would recreate the proven one-way behavior and is not part of this fix.
