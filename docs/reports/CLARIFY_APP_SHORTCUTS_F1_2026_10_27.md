# APP-SHORTCUTS-F1-01 - Effective Shortcut Reference

## Scope

This bounded stage implements only the application-wide F1 shortcut reference.
It does not change temporary-note behavior, Find, File Explorer, APP-THREAD,
TOON, WQXR or the legacy backlog.

## Reproduced Defects

- F1 had two independent activation routes: a Help-menu `QAction` and a second
  top-level `QShortcut`.
- The Help route entered a modal `QDialog.exec()` loop.
- Its contents came from `ShortcutManager.SHORTCUTS`, including declared but
  inactive entries, instead of the live effective bindings.
- Customization and runtime translation could leave the open reference stale.

The clean pre-edit regression failed on the duplicate F1 route: 1 failed,
peak tree RSS 195.2 MiB, with no native crash or guard abort. An earlier test
fixture attempted to close the synthetic MainWindow during teardown and had to
be terminated (`exit -15`, 193.4 MiB); this was a test-only teardown defect,
not a product crash, and the fixture was corrected before collecting evidence.

## Implementation

- Added a weak live-binding registry to `ShortcutManager` for effective
  `QAction` and `QShortcut` instances. Managed bindings refresh immediately
  after shortcut customization; unmanaged existing shortcuts retain their
  effective sequences.
- Registered the existing main-menu and Clarify Editor shortcut actions without
  adding parallel handlers or changing command ownership.
- Removed the duplicate F1, Exit and About top-level shortcuts where the menu
  action already owns the same route.
- Added one reusable non-modal shortcut reference generated exclusively from
  live registered bindings under the current MainWindow. It supports search,
  translated context grouping, accessibility names, focus restoration,
  conflict visibility, runtime translation and Esc-to-hide.
- Preserved child dialogs that own contextual F1: their WindowShortcut remains
  authoritative while that dialog is active.

Local, non-configurable shortcuts inside individual tools remain local. They
are not presented as centrally configurable commands and were not duplicated
into the application registry in this stage.

## Validation

All Qt modules ran serially in separate offscreen processes with temporary
HOME, 85% system-RAM limit, 600 MiB tree-RSS limit, 180-second wall limit and
20-second pytest timeouts.

- 308 distinct tests passed across 16 isolated modules: the new shortcut
  reference, central shortcut manager and aliases, live menus, Editor actions,
  layouts, toolbar, status, recovery, dock toggle, tab layouts and translation.
- 22 legacy `ShortcutsDialog` tests were skipped by their pre-existing import
  guard and are not counted as passing evidence.
- Peak tree RSS was 252.9 MiB. No native crash, timeout or guard abort occurred.
- `pylint --errors-only` passed for changed product files and the new regression
  module.
- `compileall`, seven translation-catalog JSON parses, required-key checks and
  `git diff --check` passed.

No live provider, real user document or full heavy-GUI startup fixture was
used. `example.py` remained untracked and byte-identical.
