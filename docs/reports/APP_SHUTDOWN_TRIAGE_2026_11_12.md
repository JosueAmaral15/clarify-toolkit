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

An isolated full-window lifecycle probe was attempted with temporary HOME,
offscreen Qt and the existing RAM/RSS/wall guards. The guard stopped the probe
when total system RAM reached 85%; the process tree itself peaked at only 74.3
MiB. It was not retried.

## Remaining evidence required

This correction closes the reproduced shortcut crash only. It does not yet prove
why the real launcher remains alive. A later run with sufficient RAM must:

1. launch the real application in a bounded subprocess group;
2. close it through the normal accepted MainWindow path;
3. capture active Qt threads, `QThreadPool`, timers and child processes;
4. assert that the Python process and launcher exit within the bounded timeout;
5. confirm that no new crash report or descendant process remains.

Until that test passes, `APP-SHUTDOWN-PROCESS-01` remains open.
