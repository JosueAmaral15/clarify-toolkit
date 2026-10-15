# APP-THREAD-01 Stage 7 - AI Processor discovery and filtering

Date: 2026-10-15

## Scope

This bounded stage audits and moves `AIProcessorDock` recursive discovery and
advanced-condition filtering off the GUI thread. It preserves the Stage 6
per-dock worker lifecycle and does not include in-memory replacement, TOON,
WQXR, live providers, or other backlog items.

## Defect proof

The initial regression instrumented `os.walk()` and content reads. It failed
because directory traversal ran on the Qt GUI thread before the worker started.
The red run used temporary files and reached 201.2 MiB peak tree RSS without a
native crash.

An existing JSON Rewriter integration test later timed out in
`QMessageBox.critical()`. Source inspection proved that its mocked `cli_dedupe`
returned three values although the current API returns four. The dock caught the
unpack error and opened a modal dialog. The test now supplies the current
contract, stubs success/error dialogs, and asserts the forwarded conditions.

## Implementation

- The GUI snapshots paths, file flags, extensions and enabled conditions into
  frozen transfer objects without filesystem access.
- Semantic condition validation, recursive discovery, content reads and filtering
  run in the registered worker. Disabled filters are neither validated nor applied.
- Limits are 1,000 targets, 1 MiB aggregate path text, 128 extensions, 64 KiB
  aggregate extension text, 128 conditions, 100,000 discovered files and 4 MiB
  condition content per file.
- Discovery and filtering use cooperative checkpoints. Cancellation, invalid
  targets, size limits and content IO failures settle through the existing worker
  lifecycle before any provider call.
- Shared discovery/filter APIs retain their old behavior when the new optional
  checkpoint, limit and strict-error arguments are omitted.

## Validation

All tests used `.venv`, temporary HOME/settings, Qt offscreen, no live provider
and temporary files only. `/tmp/clarify_guard.py` enforced system RAM below 85%,
process-tree RSS below 600 MiB, wall time below 180 seconds and pytest timeouts
of 20 seconds including fixtures. GUI modules ran one module per process.

| Module | Tests | Peak tree RSS MiB |
| --- | ---: | ---: |
| `tests/gui/test_ai_processor_discovery_lifecycle.py` | 10 | 208.6 |
| `tests/gui/test_ai_processor_lifecycle.py` | 4 | 208.2 |
| `tests/gui/test_ai_processor_ollama.py` | 1 | 200.2 |
| `tests/test_ai_advanced_conditions.py` | 21 | 71.6 |
| `tests/test_and_or_operators.py` | 10 | 71.3 |
| `tests/test_file_explorer_conditions.py` | 60 | 201.3 |
| `tests/test_advanced_conditions_integration.py` | 11 | 197.0 |

Total: 117 distinct tests passed. No native crash, timeout or resource-guard
abort occurred in the final matrix.

## Remaining scope

`APP-THREAD-01` remains open. The next bounded candidate is the AI Processor
in-memory replacement path. Other synchronous consumers/workers also remain for
later audits. A single blocking filesystem or regex call cannot be interrupted
mid-call; cancellation is observed immediately before and after bounded units.
