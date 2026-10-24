# Options Signal Crash Investigation

Date: 2026-10-24
Task: `CRASH-20261021-OPTIONS-SIGNAL-01`

## Result

The crash report contained only:

```text
TypeError: options_changed() only accepts 0 argument(s), 1 given!
```

The current Clarify Editor Find dialog is not the remaining faulty consumer.
Its `_on_options_changed(self, _checked=False)` slot accepts the `bool` emitted
by the option checkboxes, and its focused tests pass.

The exact failure was reproduced in `OperationOptionsWidget`. Its public
`options_changed = Signal()` has no arguments, but checkbox `toggled(bool)`,
button-group `buttonToggled(button, bool)`, and combo
`currentIndexChanged(int)` signals were connected directly to
`options_changed.emit`. Changing Intersection raised the recorded TypeError and
did not notify the consumer.

The concrete UI path is Set Operations, under Operation Options: changing any
operation or advanced checkbox, comparison radio, or output-format combo could
raise the exception. `SetOperationsDock` embeds the widget but does not
currently connect its public notification signal; the bad direct connection
raises before a downstream consumer is required.

## Minimal Fix

- Payload-bearing checkbox and combo signals now call a private adapter that
  emits the existing no-argument public signal.
- The button group emits only when the newly selected radio is checked. This
  avoids duplicate notifications for the unchecked and checked radio events.
- No public signal signature or Editor Find behavior changed.

## Validation

All Qt modules ran separately with temporary `HOME`, offscreen Qt, system RAM
limit 85%, process-tree RSS limit 600 MiB, wall limit 180 seconds, and pytest
timeout 20 seconds.

| Scope | Result | Peak tree RSS |
| --- | ---: | ---: |
| Operation option signal regression | 12 passed | 191.4 MiB |
| Existing Editor Find stage 3 | 8 passed | 198.3 MiB |
| Set operations domain | 50 passed | 63.5 MiB |

The original one-control reproduction now returns one notification and no
exception. No native crash, timeout, RAM guard, provider, or user document was
involved.

Static validation passed for Python compilation, Pylint errors, scoped Black
checks on the new test and diagnostic runner, and `git diff --check`. The
modified legacy widget was already not Black-formatted at the starting
checkpoint and was intentionally not reformatted beyond this fix.
