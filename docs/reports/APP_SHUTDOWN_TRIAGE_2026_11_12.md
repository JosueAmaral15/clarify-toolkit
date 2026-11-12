# Application Shutdown Triage - 2026-11-12

## Reported behavior

- Recent files under `~/.config/clarify/crashes` contain shutdown-time errors.
- When Clarify is launched from a terminal, closing the application window can
  leave the terminal command running instead of returning to the shell prompt.

## Reproduced defect

The newest reports repeatedly contain:

```text
RuntimeError: Signal source has been deleted
src/shortcut_manager.py: target.destroyed callback
```

`ShortcutManager` owned one shared Qt signal object. During application teardown,
Qt could delete that emitter before registered `QAction` and `QShortcut` targets.
Their later `destroyed` callbacks then emitted through an invalid C++ object.

## Narrow correction

- Route registry notifications through one validity-checked helper.
- Tolerate the race where Qt invalidates the emitter between the validity check
  and signal emission.
- Recreate the shared emitter only when a later live session requests it.
- Keep the existing shortcut inventory, actions, key sequences and consumers
  unchanged.

## Verification

- New teardown regression: 1 passed.
- Existing keyboard alias regressions: 3 passed.
- Existing shortcut-reference regressions: 10 passed.
- Python compilation, Pylint errors-only and `git diff --check`: passed.

An initial isolated full-window lifecycle probe was attempted with temporary
HOME, offscreen Qt and the existing RAM/RSS/wall guards. The guard stopped that
run when total system RAM reached 85%; the process tree itself peaked at only
74.3 MiB.

After system pressure fell, one bounded MainWindow construction/close cycle
completed with zero remaining widgets, zero remaining top-level windows and
208.4 MiB peak process-tree RSS. That probe does not itself enter the normal
application event loop, so a separate subprocess regression was added.

## End-to-End Process Evidence

`tests/test_application_shutdown_process.py` launches the actual
`python -m src` entry point with:

- a temporary HOME, XDG configuration root, settings file and log directory;
- offscreen Qt and no user documents or provider calls;
- an opt-in diagnostic timer that invokes `MainWindow.close()` from the real Qt
  event loop;
- the normal accepted-close preference (`confirm_on_exit=false`) to model a user
  who already accepted or disabled the exit prompt;
- 85% system-RAM, 600 MiB process-tree RSS and 45-second wall guards.

The regression does not call `app.quit()`, does not use `QThread.terminate()`
and does not kill a passing child. It requires status 0, the real MainWindow
startup marker, no shortcut signal-source error, no crash report and no
surviving descendant PID.

The isolated regression passed in 9.11 seconds. A preceding diagnostic run
correctly timed out while the default exit-confirmation dialog awaited input;
that was a test-harness interaction, not counted as product evidence. Seeding
the accepted preference exercised the same normal close path without bypassing
`MainWindow.closeEvent`.

Together with the shortcut-emitter correction and its 14 focused regressions,
this closes `APP-SHUTDOWN-PROCESS-01`. The Linux launcher waits on this same
module process; its separate environment/dependency-install branches were not
executed by this regression and remain launcher concerns rather than evidence of
a lingering application process.
