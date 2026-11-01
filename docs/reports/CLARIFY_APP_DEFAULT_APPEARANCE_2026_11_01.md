# Clarify Default Appearance Evidence (2026-11-01)

## Scope

This bounded stage completed only `APP-DEFAULT-APPEARANCE-01`. It did not
implement settings reset, broader i18n parity, File Searcher, Editor UX or any
legacy backlog item.

## Reproduced defects

- A new `SettingsManager` profile defaulted to `system` and had no centralized
  window-opacity default.
- Startup and the transparency dialog independently fell back to 100% opacity.
- The UI called the control transparency while dividing the displayed value by
  100 and passing it directly to Qt as opacity. Interpreting the requested 96%
  as true transparency would therefore make the window almost invisible.
- Runtime theme selection wrote only a legacy INI file, while startup reapplied
  JSON settings afterward. This could discard the user's selected theme.
- Detached tool windows did not inherit the current main-window opacity and
  were absent from later preview updates.

## Delivered behavior

- New profiles use Dark and displayed window opacity 96%.
- The conversion is explicit: displayed 96% opacity becomes Qt opacity `0.96`
  (4% transparent). The dialog states both values and exposes accessible slider
  metadata.
- Existing JSON values remain authoritative, including explicit System, Light,
  Dark and custom opacity percentages.
- A valid legacy theme is migrated only when JSON has no stored theme choice.
- Runtime theme actions now persist to the active settings store and refresh
  theme-sensitive tab controls while retaining the legacy file for compatibility.
- Existing docks and detached hosts receive opacity updates; newly detached
  hosts inherit the current main-window opacity.

## Validation

All GUI tests ran serially through
`scripts/diagnostics/qt_lifecycle_probe.py` with temporary HOME, system RAM 85%,
process-tree RSS 600 MiB, wall 180 seconds and pytest timeout 20 seconds:

- `default-appearance`: 8 passed; peak tree RSS 197.0 MiB.
- `theme-manager`: 14 passed; peak tree RSS 69.2 MiB.
- `tool-dock-toggle`: 10 passed; peak tree RSS 203.6 MiB.
- `settings-shortcuts`: 4 passed; peak tree RSS 68.3 MiB. The module retains
  four pre-existing pytest warnings because its tests return booleans.
- One isolated full-window lifecycle cycle passed at 208.5 MiB, including
  Dark/Light/System runtime switching and zero remaining widgets/top-levels.

The focused set is 36 tests. No run had a native crash, timeout or resource
guard abort. Python compilation, nine AST parses, seven JSON catalog parses,
focused Pylint-E and `git diff --check` also passed.

`example.py` remained untracked and byte-identical at SHA-256
`058053d87c818d699cde0f00d670bca0e1c6ad857caa9758ea6a556d7c64fcee`.
