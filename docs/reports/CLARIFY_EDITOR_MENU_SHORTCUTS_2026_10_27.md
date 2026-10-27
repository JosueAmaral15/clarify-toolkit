# Clarify Editor File/Edit/View Shortcuts

## Scope

This stage implements only `CE-MENU-SHORTCUTS-01` from checkpoint `cac705c` on
branch `COM-c3cada21-2a3c-472d-89d7-6f3a6419f7bd`. It does not change Find
semantics, File Explorer behavior, application threading, TOON, WQXR or the
legacy backlog.

## Reproduction

- The Editor mixed direct `QKeySequence` assignments with centrally managed
  shortcuts. Several executable File/Edit/View actions had no shortcut and
  therefore could not be customized or included reliably in the F1 reference.
- Replace used the local legacy `Ctrl+R` route instead of the central `Ctrl+H`
  contract.
- `save_as` and the application-level Set Operations action both used
  `Ctrl+Shift+S` by default.
- A first keyboard regression proved that an Editor `QAction` associated only
  with a menu or toolbar did not receive its shortcut while focus was inside the
  document. The failing test reached the action only after mouse/menu dispatch.

## Delivered Contract

- Every visible File/Edit/View command is registered through
  `ShortcutManager`, including state actions. Common commands reuse the existing
  application action names; Editor-only commands use namespaced identifiers.
- All Editor shortcuts use `WidgetWithChildrenShortcut` and are associated with
  the `EditorDock`, so they work in its active document or split and remain
  isolated from other tools.
- Replace uses exactly `Ctrl+H`; the old `Ctrl+R` route no longer invokes it.
  Redo keeps `Ctrl+Y` and `Ctrl+Shift+Z` through the existing alias contract.
- Less frequent commands use conflict-free `Ctrl+K` chords. Set Operations now
  uses `Ctrl+K, Ctrl+Shift+S`, removing its collision with Save As.
- Live customization updates the existing `QAction` without a duplicate command
  route. The F1 shortcut reference continues to read the effective registry, so
  defaults, aliases, chords, custom values and conflicts stay synchronized.
- The visible Find/Replace shortcut text was updated in all seven translation
  catalogs; no broader translation-parity work was included.

## Validation

All Qt modules ran serially, one GUI module per process, through
`qt_lifecycle_probe.py`. Each run used a temporary HOME, offscreen Qt, pytest
timeout 20 seconds, wall limit 180 seconds, system RAM guard 85 percent and
process-tree RSS guard 600 MiB.

| Coverage | Result |
| --- | ---: |
| New Editor menu shortcut regressions | 8 passed |
| Shortcut manager, aliases and customizer | 52 passed |
| F1 effective-registry reference | 10 passed |
| Editor construction and action contracts | 69 passed |
| Redo and quick-toolbar regressions | 14 passed |
| Find modeless, Enter and history regressions | 24 passed |
| Layout, live UI, status and translation regressions | 70 passed |
| Recovery and temporary-note regressions | 67 passed |
| Existing shortcuts-dialog import guard | 22 skipped |

The isolated run executed 314 passing tests and 22 existing guarded skips,
peaking at 251.6 MiB. A post-format repetition of the four directly affected
modules passed 113 tests and peaked at 227.7 MiB. There was no native crash,
timeout or resource-guard abort.

Python compilation, seven JSON catalog parses, focused Pylint errors-only and
`git diff --check` passed. No provider, real user document, default branch or
dependency was changed. `example.py` stayed untracked and byte-identical.
