# APP-SETTINGS-RESET-01 validation report

Date: 2026-11-15
Base checkpoint: `be1d9b1`
Work branch: `COM-b65ec8c4-80ea-4b0a-b6d6-bf7efc273bbc`

## Reproduced defect

The existing `SettingsManager.reset_to_defaults()` changed only the main JSON
store, removed recent files, created no backup and left YAML and QSettings with
their previous values. There was no Settings action, category preview or
confirmation. An isolated regression also proved that an explicit
`ConfigManager` path could inspect and move legacy files from `HOME`.

## Delivered behavior

- `Settings > Reset Settings...` is translated in all seven catalogs.
- The dialog previews six practical categories, supports all or selected
  categories and requires a second confirmation before mutation.
- A private mode-0600 ZIP backup is flushed and atomically installed before any
  store is changed. A failed mutation restores JSON, YAML, legacy INI and
  QSettings snapshots; rollback failure is reported distinctly.
- Reset uses explicit allowlists. Documents, recent files, paths, temporary
  notes, recovery snapshots, operational history, custom layouts, presets,
  plugins, credentials and API keys are preserved.
- Dark and 96% opacity are shared defaults in JSON, YAML and QSettings. Only
  appearance is hot-reloaded; other selected categories receive restart
  guidance.
- Explicit ConfigManager paths no longer migrate HOME data unless the caller
  opts in with `migrate_legacy=True`.

## Validation

Every run used a temporary HOME, offscreen Qt, disabled core dumps, pytest
timeout 20 seconds, wall limit 180 seconds, system RAM limit 85% and process-tree
RSS limit 600 MiB. GUI modules ran one per process.

- Core reset, config and Sprint 8: 34 passed; peak tree RSS 76.9 MiB.
- Reset dialog: 4 passed; peak tree RSS 194.4 MiB.
- Default appearance: 8 passed; peak tree RSS 197.5 MiB.
- Live UI actions: 17 passed; peak tree RSS 203.2 MiB.
- Pylint fatal/error-only: 10.00/10.
- AST: 8 changed Python files; JSON: all 7 catalogs; diff check: passed.

The four `PytestReturnNotNoneWarning` warnings in `tests/test_sprint8_features.py`
pre-existed and are outside this task. No native crash, timeout, guard abort,
provider, browser, real user document or full unbounded GUI startup was used.
