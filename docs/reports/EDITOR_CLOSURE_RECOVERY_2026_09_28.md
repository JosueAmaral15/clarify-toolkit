# Clarify Editor: Recovery On Closure

Date: 2026-09-28. Task: CE-REC-01 (MUST).
Branch: `COM-e8a3ba95-8b6e-4792-ab9c-6458d4fadd5a`.
Base: FE04 `631994b` plus dispatch journal `4d28cfb` (includes header24 `136b44e`).
Local implementation checkpoint is recorded in the history/dispatch journal.

## Delivered

Reuses `UnsavedRecoveryStore` and File > Recover Unsaved. There is no second
store or temporary directory that disappears when the application exits.
The existing persistent location remains Qt AppDataLocation/editor-recovery.
Snapshots contain plaintext, with directory `0700` and files `0600`; this is not encryption.
Atomic replacement flushes the file and, where supported, its directory.
The existing retention is 24 hours by default, adjustable from 1 hour to 30 days.

Latest buffers are checkpointed synchronously before Dock Close, the actual
MainWindow tool-tab close contract, ancestor Close/Hide, DeferredDelete on the
dock/ancestor, and QApplication.aboutToQuit. Untitled, empty, modified and
generated edit-only buffers are included. Ordinary edits reset the 1500 ms debounce
even after a document was already marked modified. Parent event filters are
rewired on reparenting; Qt validity guards handle destruction-time ParentChange.

Closing the entire tool preserves buffers. Deliberate document-tab Save/Discard/
Cancel retains its existing meaning: Discard removes its snapshot; Cancel keeps
the tab; canceled/failed Save As cannot remove the tab. Discard I/O failure keeps
the tab and disk tracking. Removed tabs stop their timers and are deleteLater'd.
MainWindow delegates Editor tool-close to request_tab_close without a duplicate
Save/Discard dialog; other tools retain their existing contract.

Unchanged saved documents store only a path/title/extension, source revision
(device/inode/size/mtime/ctime), and cursor. No toPlainText extraction is used for
references, including large saved files. Restoration explicitly creates an
unsaved, disconnected buffer; it never writes the original. Missing/changed,
symlink-replaced, non-UTF8/NUL-containing and >2 MiB references fail explicitly,
remain recoverable/discardable entries, and direct users to File > Open for
manual inspection. References are not a copy of the old original. Unsaved buffer
snapshots still restore if their original disappeared or changed.

Limits remain 2 MiB UTF8/document, 20 snapshots and 20 MiB aggregate storage.
Qt UTF16 character count bounds extraction before allocating a Python string;
exact UTF8 bytes and bounded JSON overhead are then checked by the store.
Metadata has explicit bounds. Snapshot reads and reference reads are bounded;
regular-file/revision checks reject special files and concurrent source changes.
QLockFile uses tryLock(0), so another instance produces an honest busy error,
not an indefinite GUI wait or racing quota allocation. Quota exhaustion rejects
the write without silently evicting another valid draft. Retention/prune still
removes expired/corrupt/over-budget legacy entries.

Normal close is blocked on checkpoint failure and reports count in the status
row. Final shutdown/deferred deletion cannot be blocked; failed counts are logged,
never document contents. Earlier successful snapshots can survive a later failed
write, but are not a guarantee of the newest edit. Recovery dialog counts only
successful restores, preserves failed references, and excludes current active
buffers from Recover/Discard All. It never reports skipped buffers as saved.

Qt-owned slots/weakrefs prevent the application signal retaining the dock.
Close stops recovery/auto-save/validation timers and removes file watches;
late timer/file notifications are ignored. Show resumes ordinary settings and
watches. Canceled parent Close does not suspend the live editor. Tests include
collection of dock/controller Python wrappers after Qt deletion.

## Validation

Final pytest groups ran serially using `.venv/bin/python`, isolated HOME/settings/
logs, QT_QPA_PLATFORM=offscreen, OMP=1, no core dumps, 20 s pytest deadlines including
fixtures, and `/tmp/clarify_guard.py`: system RAM 85%, process-tree RSS 600 MiB,
wall 180 s. Initial RAM 46.8%; later 43.7%. No user process was closed to free memory.

| Final Test Group | Passed | Duration | Peak Tree RSS |
| --- | --- | --- | --- |
| Store39 + new lifecycle53 + layout20 + converter handoff2 | 114 | 12.93s | 252.8 MiB |
| Existing Editor, excluding 2 full-MainWindow fixture cases | 67 | 7.00s | 204.1 MiB |
| Explorer scopes69 + lifecycle36 + cross-line48 | 153 | 10.71s | 217.8 MiB |

**334 distinct focused tests**, including 87 new cases. Earlier repetitions are
not counted twice. Tests cover immediate edit/close/new widget instance, a new
Python process reading durable storage, all Qt closure routes, multiple text/JSON/
empty/edit-only tabs, cursor restore, removed/changed origins, metadata-only large
references, permissions, retention, legacy/corrupt payloads, busy/count/byte/size/
I/O failures, atomic replacement failure, explicit recovery choices and cleanup.

Commands:

```bash
python /tmp/clarify_guard.py .venv/bin/python -m pytest \
  tests/test_editor_recovery.py tests/gui/test_editor_recovery_lifecycle.py \
  tests/gui/test_editor_layout.py tests/gui/test_unified_text_to_json_editor_switch.py \
  -q --timeout=20 --timeout-method=thread -o timeout_func_only=false
python /tmp/clarify_guard.py .venv/bin/python -m pytest \
  tests/gui/test_editor_dock.py -q -k 'not converter_switch' \
  --timeout=20 --timeout-method=thread -o timeout_func_only=false
python /tmp/clarify_guard.py .venv/bin/python -m pytest \
  tests/test_file_explorer_target_scope.py tests/test_file_explorer_lifecycle.py \
  tests/test_file_explorer_cross_line.py -q --timeout=20 \
  --timeout-method=thread -o timeout_func_only=false
```

AST parsing of 6 Python files, 2 JSON catalogs and diff checks passed. Production
Pylint-E covers store/controller/EditorDock/app, jobs1, persistent disabled;
the final run passed (exit0, peak process-tree RSS417.7 MiB), with no guard abort.

Investigation failures were not counted as success: global Python lacked sympy
and collected no tests; initial lifecycle/fixture teardown and empty-store folder
creation regressions were fixed and revalidated. One early lint invocation
overlapped the ending failed test run; final pytest groups were serial. An early
69-case Editor invocation inadvertently included 2 existing MainWindow startup
fixtures (update calls mocked, 220 MiB peak); subsequent canonical validation
excluded them. New app tool-close coverage executes the actual method via AST
against a lightweight Qt container, without constructing MainWindow.

## Limits And Next Stage

This is focused/offscreen evidence, not whole-suite, native desktop UX, packaging,
external coverage/security, or a global leak-free certification. Direct native
destruction without a Qt event, force kill/power loss, OOM, full/unavailable disk,
quota exhaustion and edits after the last successful checkpoint are not covered
by a guarantee. Synchronous filesystem calls are bounded in bytes but have no
execution deadline. Large saved references are retained without copying content;
automatic recovery reading is deliberately capped at2 MiB.

Monitoring hooks/status and checkpoint/journal were verified; ai-presence0.9.0
doctor is healthy except the previously failed reply-observer service, which was
not restarted. No live provider, secret or real user document was used.
`example.py` is unchanged/excluded. No push or main/develop promotion; CI/security
gates remain unresolved. Only one exact-session native continuation after commit.

Remaining finite queue: **FE-PAR-05,06,08**. Overall 33 open including 30 legacy
items outside automation. Finish the exact worker when this finite queue completes
or cannot continue safely; never dispatch again merely because delivery is uncertain.
