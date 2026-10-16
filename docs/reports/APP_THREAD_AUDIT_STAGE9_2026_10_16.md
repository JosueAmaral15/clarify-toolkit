# APP-THREAD-01 Stage 9 - AI Processor in-memory prompt insertion

Date: 2026-10-16

## Scope

This bounded stage audits `AIProcessorDock._handle_insert_in_prompt` and moves
only immutable in-memory insertion work off the Qt GUI thread. It preserves the
public `InsertPanel.insert_requested(line_no, text, mode)` contract, shared
`insert_at_line` behavior, Stage 7 discovery/filtering and Stage 8 result
replacement. Save/export, TOON, WQXR, Editor UX, i18n and live providers are not
included.

## Defect proof

The first provisional regression aborted before the product method because the
new test omitted the `qtbot`/`QApplication` fixture. The native stack ended in
`StandardToolDock.__init__`; guard output was exit `-6`, 176.9 MiB peak tree RSS
and no resource trigger. Work stopped without retry in that session. This was a
test-harness defect, not an insertion crash.

After explicit user resumption, the fixture-only correction produced a valid red
assertion: instrumented `insert_at_line` ran on `Qt mainThread`. That run reached
201.3 MiB peak tree RSS without a native crash or guard abort. Source audit also
proved that the success path called an absent `AIProcessorDock.show_message()`
method.

## Implementation

- The GUI checks the prompt `QTextDocument` character bound before extraction and
  snapshots prompt content, line, inserted text and mode into a frozen plan.
- A registered non-exclusive worker validates UTF-8 bounds and calls the existing
  shared `insert_at_line`; CLI and JSON Editor consumers remain unchanged.
- Prompt input and output are limited to 4 MiB, inserted text to 1 MiB and line
  numbers to 1 through 10,000,000. Only the five existing `InsertMode` values are
  accepted.
- One dock permits one parent or embedded operation, while distinct docks retain
  independent workers. Process, Replace and Insert buttons reflect that gate.
- Cancellation is checked before and after the bounded insertion unit. Completion
  is applied to the prompt only after native `QThread.finished`; close suppresses
  late text and messages and never uses `terminate()`.
- Success now uses the existing `show_info()` API instead of the absent
  `show_message()` method.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen where applicable,
provider-free workers and no user documents. `/tmp/clarify_guard.py` enforced
system RAM below 85%, process-tree RSS below 600 MiB, wall time below 180 seconds
and pytest timeouts of 20 seconds including fixtures. Each GUI module ran in its
own process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_ai_processor_insert_lifecycle.py` | 9 | 210.1 |
| `tests/gui/test_ai_processor_result_replace_lifecycle.py` | 9 | 210.2 |
| `tests/gui/test_ai_processor_lifecycle.py` | 4 | 209.5 |
| `tests/gui/test_ai_processor_discovery_lifecycle.py` | 10 | 209.2 |
| `tests/gui/test_ai_processor_ollama.py` | 1 | 200.9 |
| `tests/gui/test_insert_panel_lifecycle.py` | 9 | 201.0 |
| `tests/test_line_lookup_feature.py` | 10 | 71.7 |

Total: 52 distinct focused tests passed. No native crash, pytest timeout or
resource-guard abort occurred after the fixture correction.

## Remaining scope

`APP-THREAD-01` remains open because other synchronous consumers and workers need
bounded audits. The standard `insert_at_line` call is bounded and runs off the GUI
thread, but cannot observe cancellation during that single call; cancellation is
observed immediately before it and before result publication. The initial harness
abort remains documented and is not represented as a product fix.
