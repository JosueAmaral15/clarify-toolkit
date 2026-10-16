# APP-THREAD-01 Stage 10 - AI Processor result saving

Date: 2026-10-16

## Scope

This bounded stage audits `AIProcessorDock._save_results` and the shared
`ai_processor.save_results` contract. It moves only immutable result
serialization and file IO off the Qt GUI thread. The file dialog, all widget
access and final user feedback remain on the GUI thread. Stages 7 through 9,
embedded panel behavior and provider-free operation remain unchanged.

InsertPanel file writes, JSON Editor, TOON, WQXR, Editor UX, i18n and the legacy
backlog are not included.

## Defect proof

The source path called `save_results(self.last_responses, path, mode="write")`
directly after the GUI file dialog. A Qt regression instrumented that shared call
and failed cleanly because it ran on `Qt mainThread`. The red run used a temporary
HOME and output path, reached 202.0 MiB peak tree RSS and had no native crash,
timeout or resource-guard abort.

The shared helper has no other current source consumer. It remains exported as a
public AI Processor API, so its existing arguments and output format were kept.

## Implementation

- The GUI snapshots `last_responses` and the selected path into a frozen plan.
  No worker reads a widget, model or mutable response list.
- The plan permits at most 1,000 results, 4 MiB UTF-8 per result, 20 MiB total
  serialized data and a 4 KiB path. Cheap character bounds run before worker
  creation; exact UTF-8 bounds run off the GUI thread.
- The shared `save_results` API now accepts an optional interruption callback and
  returns completion state. Calls using the original three arguments retain the
  same text format and overwrite/append behavior.
- The worker serializes to a private temporary file in the destination directory.
  It replaces the selected path only after complete validation and writing, so an
  IO failure or cooperative cancellation does not damage an existing destination.
- Process, in-memory Replace, prompt Insert and Save cannot overlap within one
  dock. Different docks retain independent registered workers.
- Interrupt and close request cooperative cancellation. Temporary files are
  removed, settlement occurs through native `QThread.finished`, close suppresses
  late feedback and no path uses `terminate()`.
- A cancellation arriving after the atomic replace is reported as success because
  the requested file has already been committed; cancellation before commit keeps
  the old destination and reports cancellation.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen, temporary output
files and provider-free workers. `/tmp/clarify_guard.py` enforced system RAM below
85%, process-tree RSS below 600 MiB and wall time below 180 seconds. Pytest used a
20-second timeout including fixtures. Every GUI module ran in a separate process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_ai_processor_result_save_lifecycle.py` | 9 | 207.1 |
| `tests/gui/test_ai_processor_discovery_lifecycle.py` | 10 | 206.7 |
| `tests/gui/test_ai_processor_result_replace_lifecycle.py` | 9 | 208.5 |
| `tests/gui/test_ai_processor_insert_lifecycle.py` | 9 | 208.4 |
| `tests/gui/test_ai_processor_lifecycle.py` | 4 | 207.3 |
| `tests/gui/test_ai_processor_ollama.py` | 1 | 199.2 |

Total: 42 distinct focused tests passed. The new tests cover thread affinity,
shared formatting/backward compatibility, immutable and bounded plans, atomic
publication, independent docks, one operation per dock, cancellation, IO errors,
dialog cancellation and tab-close settlement. No native crash, pytest timeout or
resource-guard abort occurred.

Python compilation, Pylint error-only checks, focused Black checks and
`git diff --check` passed. Full-file Black was intentionally not applied to the
two legacy modules because it would create unrelated formatting churn.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers
still need bounded audits. Cancellation is cooperative between result writes; a
single result write is limited to 4 MiB but cannot be interrupted inside Python's
individual `TextIO.write` call. No live provider or real user document was used,
and this stage does not claim global Qt lifecycle or CI/security gates resolved.
