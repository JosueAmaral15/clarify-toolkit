# APP-THREAD-01 - Stage 1 Worker Audit

Date: 2026-10-07

## Scope

This stage audited the existing worker ownership model and repaired one proven
unsafe lifecycle: Google Translate. It does not claim completion of the broader
application threading task.

## Findings

- File Explorer already owns one bounded operation per dock, uses cooperative
  pause/cancel, registers the native thread, and defers close until settlement.
- Tutorial Assistant registers its worker with `ThreadManager` and has focused
  close/cancel tests.
- Google Translate used direct `QThread` subclasses without global registration,
  re-enabled controls before native completion, and called `QThread.terminate()`
  on cancel and close. The application therefore could miss active translations
  during shutdown and could overlap work during the result/finished interval.
- `ThreadManager.force_cleanup()` still terminates legacy feature workers. These
  workers and synchronous GUI paths require separate, bounded audit stages; they
  were not silently treated as fixed here.
- Google Translate provider requests have a 10-second network timeout. Cancellation
  is cooperative before/after each request and during retry/inter-chunk waits; an
  in-flight blocking request cannot be interrupted safely and must reach its bound.

## Changes

- Added `FeatureType.GOOGLE_TRANSLATE` and registered text/notebook workers using
  a per-dock operation id.
- Added cancellation checkpoints to the shared chunked translation API without
  changing existing positional argument order.
- Kept the Translate action disabled until the native `finished` signal and
  suppressed result/error callbacks after cancellation.
- Deferred dock/tab closure until settlement and protected the worker from forced
  termination during application shutdown.
- Extended the bounded Qt probe with isolated Google Translate test modes.

## Validation

- `tests/test_google_translate_lifecycle.py`: 6 passed, peak tree RSS 202.8 MiB.
- `tests/test_google_translate_dock.py`: 27 passed, peak tree RSS 242.2 MiB.
- `tests/test_google_translate.py`: 18 passed, peak tree RSS 65.0 MiB.
- `tests/test_file_explorer_lifecycle.py`: 36 passed, peak tree RSS 210.9 MiB.
- `tests/test_qt_completion_lifecycle.py`: 11 passed, peak tree RSS 205.3 MiB.
- `tests/test_thread_management_system.py`: 7 passed, peak tree RSS 65.7 MiB.
- Total: 105 focused tests passed in isolated processes.
- Both runs used offscreen Qt, temporary HOME/config, RAM 85%, tree RSS 600 MiB,
  wall 180 seconds and per-test 20-second limits. No provider or user document was
  used; no guard abort or native crash occurred.

## Remaining APP-THREAD-01 Work

- Audit each legacy `QThread`/worker owner and remaining synchronous GUI I/O.
- Replace unsafe emergency termination only after each feature has a cooperative
  cancellation contract and bounded shutdown behavior.
- Validate parallel independent tool tabs, failure paths, queue/resource bounds,
  and application-wide shutdown in separate GUI processes.
