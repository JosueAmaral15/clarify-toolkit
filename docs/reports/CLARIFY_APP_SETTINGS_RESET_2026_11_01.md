# APP-SETTINGS-RESET-01 Evidence - 2026-11-01

## Scope

Implemented only `APP-SETTINGS-RESET-01` from checkpoint `be1d9b1` on branch
`COM-8c89d334-1b1a-44f8-9fa4-ce64287b9d3e`.

## Reproduced defects

- `SettingsManager.reset_to_defaults()` replaced the complete JSON dictionary,
  deleting recent files and unknown session keys.
- `ConfigManager.reset_to_defaults()` restored `system` and had no opacity key,
  diverging from the documented Dark/96% defaults.
- No single action coordinated JSON, YAML, QSettings and legacy preferences or
  created a complete backup before reset.
- An explicit temporary `ConfigManager` path still searched the real HOME for
  legacy settings. During the audit this moved `~/.clarify_settings.json` once;
  it was immediately restored. Its restored SHA-256 is
  `64994a40111d92e6244a970c1c5d0e5632a9b3e44fb1c490c59a1886b093b7bc`,
  and `~/.clarify_settings.json.migrated` is absent.

## Delivered contract

- `Settings > Reset Settings...` is translated in all seven catalogues.
- The dialog previews Appearance, General, Shortcuts and Advanced and supports
  a global or selected-section reset with a separate confirmation.
- A private `0700` backup bundle with `0600` files and SHA-256 manifest is
  published atomically before any reset mutation. Individual files and total
  backup size are bounded.
- Only known preference leaves are reset. Recent files, geometry, directories,
  session keys, documents, temporary notes, recovery snapshots, operational
  history, plugins, credentials, layouts and unknown keys are preserved.
- JSON, YAML, QSettings and existing legacy theme preferences converge on Dark
  and 96% opacity. Write failure triggers rollback and is reported honestly.
- Appearance, language, shortcuts and safe reporting toggles hot-reload.
  Advanced settings display explicit restart guidance.
- Explicit `ConfigManager` paths no longer inspect or move HOME legacy files
  unless migration is requested explicitly.

## Guarded validation

Each GUI module ran in a separate offscreen process with temporary data and
guards at system RAM 85%, process-tree RSS 600 MiB, wall 180 seconds and pytest
20 seconds including fixtures.

- `settings-reset-core`: 7 passed, peak 66.7 MiB.
- `settings-reset-dialog`: 4 passed, peak 195.8 MiB.
- `config-manager`: 24 passed, peak 69.1 MiB.
- `default-appearance`: 8 passed, peak 197.5 MiB.
- `settings-shortcuts`: 4 passed, peak 68.4 MiB; four pre-existing
  `PytestReturnNotNoneWarning` warnings remain.
- `translation-catalog`: 10 passed, peak 186.8 MiB.
- Python compilation, seven translation JSON parses, focused Pylint-E and
  `git diff --check` passed.

No native crash, timeout, memory guard abort, provider call or user-document
operation occurred in final validation.
