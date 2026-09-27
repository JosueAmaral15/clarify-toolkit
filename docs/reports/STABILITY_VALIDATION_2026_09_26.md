# Clarify Stability Validation - 2026-09-26

## Scope

Continuation of the technical follow-ups left after the 30-task program. Existing
worktree changes were preserved. No release, commit, push, live AI request, model
download, or AI Presence Monitor dispatch was performed.

## Changes

- Editor tests now instantiate the editor directly when a whole application is
  unnecessary, dispose Qt widgets between cases, and test Find/Replace controls.
  GUI fixtures disable automatic external update checks.
- Copy/Export feedback and auto-save status timers now use their owning Qt widget
  as context. Previously a delayed callback accessed a deleted button and opened
  the crash handler's modal dialog, explaining the later cumulative test timeout.
  A regression test copies, exports, deletes the tab, and lets the timer expire.
- Bundled plugins import the canonical `PluginBase`; the loader requires actual
  inheritance instead of accepting any class with an `activate` method. Activation
  follows menu construction. Menu lookup avoids invalid Qt wrapper lifetimes.
- Update requests run through a Qt thread pool with one request per window at a
  time, queued results, retry after failure, and suppression after window close.
  Manual checks report unavailable release information as an error, not "up to date".
- Logging tolerates unwritable directories; migration logging shares the selected
  directory, and update caching is optional. `CLARIFY_SETTINGS_FILE` supports an
  explicit alternate JSON settings file; other application stores are unchanged.
- Gemini uses `google-genai`, separate credentials per request and context-managed
  HTTP clients. Tutorial Assistant uses the existing `gemini-2.5-flash` default.
  The internet probe also closes its socket.
- Poetry's `dev` extra is installed, including Pylint. The lockfile replaces the
  legacy Gemini dependency. Existing unrelated installed packages were not purged.

## Reproduction

Run from the repository with its `.venv` and Poetry `dev` extra installed:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest \
  tests/gui/test_editor_dock.py tests/gui/test_update_check_controller.py \
  tests/test_plugin_system.py tests/test_gemini_clients.py \
  tests/test_startup_storage.py tests/test_logging_system.py \
  tests/test_ollama_client.py tests/test_editor_recovery.py \
  -q -o timeout_func_only=false --timeout-method=thread --timeout=20
```

Use an external `timeout -k 5s 120s` guard as well. Pylint validation is limited to
changed modules with `--errors-only --jobs=1 --extension-pkg-allow-list=PySide6
--generated-members=connect`; these options handle Qt's dynamic extension classes
and signals. They do not establish repository-wide lint cleanliness.

## Results

- 126 tests passed in 15.73 seconds, including the complete 69-test EditorDock
  suite, plugin/update integration, Gemini client cleanup, storage failures,
  logging, Ollama wrappers and editor recovery.
- Focused Pylint checks passed with the Qt options above. A subsequent wider pass
  identified an ambiguous shortcut-assignment branch; nesting its condition under
  the assignment preserves behavior and makes the control flow explicit.
  After that adjustment, the three menu/initialization tests and the EditorDock
  Pylint check passed again, and package artifacts were rebuilt.
- `compileall` for `src`, bundled plugins and changed tests passed.
- `poetry check`, `git diff --check`, wheel and sdist builds passed. The wheel
  contains the update controller and declares `google-genai`, not the legacy SDK.
- Earlier timed-out/failed runs were diagnostic and are not counted as passes.
  These results do not prove absence of memory leaks or validate every tool.

## Remaining Work

- Reconcile 36 legacy `**[]**` markers in `TASKS.md`. This is a marker count, not a
  confirmed count of unique unimplemented requirements. Examples include duplicate
  Calculator integration entries, an old sprint roadmap, partially delivered JSON
  validation, and future cloud/Git/macro/visual-search features.
- Live STT needs a backend: Whisper, Vosk, and SpeechRecognition are absent.
- Portuguese spellchecking needs the Aspell `pt_BR` dictionary; only English
  dictionaries are installed.
- Local visual analysis needs a multimodal model. Ollama currently lists
  `llama3.2:1b` and `tinyllama:latest`, not LLaVA.
- Live Gemini requests, real Slack/PostgreSQL operations, desktop visual review,
  whole-suite execution and release readiness are outside these focused checks.
- Review and separate the broad worktree before committing or publishing.
