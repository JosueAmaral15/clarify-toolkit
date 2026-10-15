# APP-THREAD-01 Stage 8 - AI Processor in-memory replacement

Date: 2026-10-15

## Scope

This bounded stage audits `AIProcessorDock._handle_replace_in_results` and moves
only immutable in-memory search/replace work off the Qt GUI thread. It preserves
the Stage 6 per-dock lifecycle, Stage 7 discovery/filter behavior and the public
`SearchReplacePanel.replace_requested` contract. It does not include TOON, WQXR,
Editor UX, i18n, live providers or user files.

## Defect proof

The red regression first exposed two pre-existing functional defects before it
could measure thread affinity:

- the consumer called Python's built-in `compile(needle, options)` rather than
  `SearchOptions.compile()`, so normal replacement could not run;
- the success path called an absent `AIProcessorDock.show_message()` method.

After test-only stubs bypassed those defects, the instrumented replacement ran on
the Qt main thread. The valid red assertion reported `Qt mainThread`, reached
202.2 MiB peak process-tree RSS and did not crash or trigger a guard.

## Implementation

- The GUI checks the `QTextDocument` character bound before extracting text and
  snapshots content, query, replacement, options and count into a frozen plan.
- The registered per-dock worker performs UTF-8 byte validation, explicit
  `SearchOptions.compile()` and bounded replacement away from the GUI thread.
- Content and output are limited to 4 MiB, query to 64 KiB and replacements to
  10,000. Cancellation checkpoints run before compilation, between matches and
  before publishing the final atomic result.
- One AI Processor dock permits one active parent or embedded operation. Separate
  docks retain independent non-exclusive workers and registry ownership.
- Completion is applied only after native `QThread.finished`. Cancel and close
  suppress late text/messages, wait for settlement and never use `terminate()`.
- The public embedded panel signal was exercised end to end with case sensitivity,
  whole-word matching, regex, preserve-case and count semantics retained.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen when applicable,
provider-free workers and no user documents. `/tmp/clarify_guard.py` enforced
system RAM below 85%, process-tree RSS below 600 MiB, wall time below 180 seconds
and pytest timeouts of 20 seconds including fixtures. Each GUI module ran in its
own process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_ai_processor_result_replace_lifecycle.py` | 9 | 209.6 |
| `tests/test_search_replace_bounded.py` | 4 | 70.4 |
| `tests/gui/test_ai_processor_lifecycle.py` | 4 | 209.2 |
| `tests/gui/test_ai_processor_discovery_lifecycle.py` | 10 | 209.0 |
| `tests/gui/test_ai_processor_ollama.py` | 1 | 200.3 |

Total: 28 distinct focused tests passed in the final resumed matrix. Pylint error
checks, `py_compile`, focused Black and `git diff --check` also passed. No native
crash, pytest timeout or resource-guard abort occurred in this final run.

An earlier post-format repetition stopped before collecting the discovery module
because unrelated global RAM reached the 85.0% guard while that test process used
95.3 MiB. It was not retried in that session. The user later explicitly resumed
the task with memory headroom; the complete matrix above then passed once without
lowering any guard.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers still
need bounded audits. Python's standard `re` engine cannot cooperatively interrupt
one match attempt already in progress; cancellation is observed immediately before
compilation, between matches and before result publication. Input limits and
off-GUI execution bound memory and preserve responsiveness, but do not constitute
a hard execution-time limit for a pathological regular expression.
