# CE-TEMP-NOTE-LIFECYCLE-01 - Temporary Note Lifecycle

## Scope

This bounded stage changes only Clarify Editor temporary-note identity,
autosave, Save/Save As behavior, management actions and close-path settlement.
It does not change Find, File Explorer, APP-THREAD, TOON, WQXR or legacy work.

## Reproduced Defects

- Saving a buffer as a temporary note retained its normal `file_path`, dirty
  state and original tab title. A later Save or Ctrl+S could therefore write the
  original file instead of the note.
- Later edits did not update the note automatically.
- Restored notes were presented as unsaved buffers.
- Save As wrote a normal file but left temporary-note identity and storage.
- The manager used a dropdown and offered only restore/delete.

The clean pre-edit regression stopped on the retained source path: 1 failed,
peak tree RSS 200.2 MiB, with no native crash or guard abort.

## Implementation

- A successful `Save as Temporary Note` atomically stores the bounded buffer,
  detaches normal-file and folder-session identities, clears watcher/recovery
  references and displays the user title as a clean temporary-note tab.
- Each note owns a single-shot 500 ms autosave timer. Save and Ctrl+S call the
  same bounded atomic store operation without a file dialog. Pending notes are
  flushed before individual-tab, Editor, parent, deferred-delete and
  application-quit settlement.
- Clean stored notes are not duplicated into `UnsavedRecoveryStore`. If note
  autosave fails, the dirty buffer remains open and the existing recovery path
  can still preserve it; size, quota, corruption and I/O failures are reported.
- Save As first flushes current note content, writes the selected normal file,
  and only then discards note storage. Cancel or write failure leaves the note
  unchanged. If post-write note cleanup fails, the file copy remains on disk,
  but the tab is restored to note identity and the partial result is reported.
- Conversion updates normal path, watcher baseline, recent files, folder owner,
  dirty state and recovery only after the complete transaction succeeds.
- `Manage Temporary Notes` now uses a searchable, sorted, scrollable keyboard
  list with restore, rename, export and explicit-delete actions. Closing a tab
  never deletes the note; deletion preserves an open buffer as a dirty non-note.
- Timer callbacks revalidate live tab and note identity, preventing queued late
  delivery from recreating a converted or deleted note.

The existing private store remains the sole backend with atomic mode-0600
writes, mode-0700 directory, 2 MiB per note, 20 notes and 20 MiB total limits.
Retention remains manual by default and configurable by the existing setting.

## Validation

All Qt modules ran serially in separate offscreen processes with temporary
HOME, 85% system-RAM limit, 600 MiB tree-RSS limit, 180-second wall limit and
20-second pytest timeouts.

- 304 distinct tests passed across 16 isolated modules: 14 new lifecycle cases,
  old note contracts, note/recovery stores, every recovery close path, folder
  sessions, watchers/path copy, splits, Editor construction, toolbar/status,
  dock toggle, tab layouts and translation lookup.
- Peak tree RSS was 253.5 MiB. No native crash or guard abort occurred.
- One intermediate injected write-failure test timed out because its real
  offscreen error dialog remained open (`abort_reason=null`, 200.8 MiB). The
  fixture was corrected to stub only that modal, and the module then passed.
- `pylint --errors-only`, `compileall`, all seven catalog JSON parses, scoped
  feature-key checks and `git diff --check` passed.

No provider, real user document or heavy full-MainWindow fixture was used.
`example.py` remained untracked and byte-identical.
