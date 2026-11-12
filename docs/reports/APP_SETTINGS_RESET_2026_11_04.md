# APP-SETTINGS-RESET-01 validation report

Started: 2026-11-04
Final validation: 2026-11-12
Base checkpoint: `be1d9b1`
Work branch: `COM-cf6e1fb7-9456-4851-bae8-8b6a410d738c`

## Reproduced gap

`SettingsManager.reset_to_defaults()` only rewrote the primary JSON store. It
had no user preview, category selection, confirmation, coordinated QSettings / YAML /
legacy reset, atomic backup, rollback, or hot-reload boundary. The YAML defaults
also still declared System rather than the documented Dark / 96% appearance.

## Delivered contract

- One translated `Settings > Reset Settings...` action in all seven catalogs.
- Explicit preview with global selection and six practical category choices.
- A second confirmation before mutation and clear protected-data disclosure.
- One private (`0600`) ZIP backup written through a temporary file, `fsync` and
  `os.replace` before any setting changes.
- Coordinated allow-list reset for JSON, YAML, QSettings and existing legacy INI
  preferences, with byte-faithful rollback on failure.
- Dark theme and 96% window opacity aligned across active stores. Only appearance
  is hot-reloaded; remaining selected categories receive restart guidance.
- Documents, recent files, paths, temporary notes, recovery snapshots, operational
  history, custom layouts, presets, plugins, credentials and API keys remain out
  of the mutation allow-list.

## Validation

All pytest runs used a temporary `HOME`, `QT_QPA_PLATFORM=offscreen`, core dumps
disabled, per-test timeout 20 seconds, wall limit 180 seconds, system RAM barrier
85%, and process-tree RSS barrier 600 MiB. GUI modules ran in separate processes.

- `tests/test_settings_reset.py`, `tests/test_config_manager.py`,
  `tests/test_sprint8_features.py`: 33 passed; peak tree RSS 78,728 KiB.
- `tests/gui/test_settings_reset_dialog.py`: 4 passed; peak 200,084 KiB.
- `tests/gui/test_default_appearance.py`: 8 passed; peak 202,832 KiB.
- `tests/gui/test_live_ui_actions.py`: 17 passed; peak 209,548 KiB.
- Pylint fatal/error-only: 10.00/10 for changed Python modules and tests.
- AST parse: 8 files; JSON parse: all seven catalogs; `git diff --check`: pass.

No native crash, resource-guard abort, live provider, real user document or full
MainWindow startup was used. The existing four `PytestReturnNotNoneWarning`
warnings in `tests/test_sprint8_features.py` remain unrelated and unchanged.
