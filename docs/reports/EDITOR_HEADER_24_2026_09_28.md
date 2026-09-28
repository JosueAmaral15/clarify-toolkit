# Clarify Editor: Folder Header With 24 Characters

Date: 2026-09-28
Task: CE-HDR-01, explicitly requested after the FE04 resource stop.
Implementation checkpoint: `136b44e` (local only).
Branch: `COM-34c8502f-6eaf-416e-92e1-cd30adadbf3f`, from stop journal `bdecb9a`.
Scope: folder label and task organization only; the FE04 draft remains separately
staged/validated, and CE-REC-01 recovery-on-close is not delivered by this change.

The current folder caption now allows 24 characters including trailing dots
(21 + `...` for longer names). It remains plain text, with the full path in its
tooltip. A private label applies additional font-metric elision when the sidebar
is narrower, and restores the capped caption when widened. Fonts do not scale
with viewport width. Folder selection, fallback, lazy navigation and hidden files
retain their behavior.

Serial guarded offscreen validation passed 22 Editor/layout/Explorer-to-editor
tests (4.55 s, peak 247.1 MiB), including nine header cases covering 23/24/25
characters, Unicode, literal markup, current/fallback roots, folder dialog cancel,
narrow-sidebar fit and re-expansion. AST parsing of changed code/tests passed.
The module was included in the four-module focused error lint run: exit 0,
peak 417.6 MiB, jobs=1 and dynamic PySide6 support. Not global lint or whole suite.

Wide and narrow offscreen captures were inspected: the label stays beside
EXPLORER without overlap or clipped text and leaves the document full-height.
The temporary capture process peaked at 190.3 MiB. This is not native desktop
theme certification. No real user file, provider or original document was used.

Guards remained 85% system RAM, 600 MiB validation tree RSS, 180 s wall,
20 s pytest timeout including fixtures, isolated settings/logs and no core dumps.
RAM at resumption was 43.1%; no user process was closed to create headroom.

Recovery already has private atomic snapshots, but immediate closure/session
buffering needs a dedicated follow-up. CE-REC-01 records this requirement without
duplicating the store or conflating it with global Undo/Redo. It is next after
validating/committing the previously interrupted FE04 stage, before FE05/06/08.
No push/main/develop promotion; unrelated `example.py` remains excluded.
