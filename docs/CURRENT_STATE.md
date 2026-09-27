# Clarify - Current Documentation State

**Last verified**: 2026-06-08 (baseline); 2026-09-26 (stability notes below)
**Scope**: current checkout operational guidance for documentation under `docs/`.

This repository contains active documentation and a large archive of historical sprint, session, investigation, migration, and programmer reports. The historical files are useful context, but they may describe older entry points, paths, package versions, or planned features that no longer match the current tree.

## Operational Truth

Use these references as the current baseline before changing code or documentation:

- Primary launch command: `python -m src`
- Root GUI launchers: `clarify.sh`, `clarify.command`, `clarify.bat`
- Developer import validation: `python main.py test`
- Package metadata: `pyproject.toml`
- Application entry point: `src/__main__.py` -> `src.app.main`
- Main window class: `src.app.MainWindow`
- CLI parser: `src.cli.parser.build_parser`
- CLI commands: `search`, `replace`, `insert`, `translate`, `gtranslate`, `dedupe`
- Log file: `~/.clarify/logs/clarify.log`
- Crash reports: `~/.config/clarify/crashes/`

## September Stability Notes

- Gemini uses `google-genai`, declared and locked in Poetry; see Google's
  [migration guide](https://ai.google.dev/gemini-api/docs/migrate).
- Update checks run outside the GUI thread and allow only one request at a time.
- Logs support `CLARIFY_LOG_DIR`, temporary fallback, and console-only operation.
  JSON preferences support an explicit `CLARIFY_SETTINGS_FILE` override.
- `docs/TASKS.md` distinguishes the completed 30-task program from technical
  follow-ups and 36 legacy `**[]**` markers requiring reconciliation. A count of
  standard Markdown checkboxes alone is not a project-wide completion measure.
- Validation scope and environment dependencies are recorded in
  [the stability report](reports/STABILITY_VALIDATION_2026_09_26.md).

## Version Notes

The documentation and source comments currently mention several v2.9.x milestones. They are not synchronized as a single release value:

- `pyproject.toml` declares package version `2.9.0`.
- `src/__init__.py` declares `__version__ = "2.9.46"`.
- Active docs such as `README.md` and `docs/INDEX.md` historically describe the v2.9.111 feature-complete milestone.
- `CHANGELOG.md`, source comments, and action plans document later work through v2.9.117+ and v2.9.123-era fixes.

Until version metadata is deliberately normalized, do not use any one of those numbers as the global project version. Treat versioned specs and reports as historical milestone records.

## Active Documentation Set

For current operational guidance, prefer:

- `docs/CURRENT_STATE.md`
- `docs/INDEX.md`
- `docs/README.md`
- `docs/guides/PROJECT_STRUCTURE.md`
- `docs/guides/ROOT_STRUCTURE.md`
- `docs/wiki/`
- `docs/api/`
- `docs/processes/`
- `docs/protocols/`

## Historical Documentation

The following directories are primarily historical or investigative. Preserve them, but verify commands and paths against the current tree before using them:

- `docs/action-plans/`
- `docs/analysis/`
- `docs/bugfixes/`
- `docs/en/`
- `docs/investigations/`
- `docs/programmers/`
- `docs/pt/`
- `docs/reports/`
- `docs/sessions/`
- `docs/sprints/`
- `docs/study/`
- `docs/specifications/`

## Documentation Maintenance Rules

When updating docs:

1. Use `python -m src` in active user/developer instructions.
2. Use `python -m pip install -e .` as the non-Poetry install path.
3. Do not reintroduce root `clarify.py` as a current entry point unless the file is restored.
4. Keep historical versioned reports intact unless the task explicitly asks to revise history.
5. If a guide points to a file, verify that the target exists in the current checkout.
6. For GUI tests, keep the safe pattern: `QT_QPA_PLATFORM=offscreen` plus pytest timeout protection.
