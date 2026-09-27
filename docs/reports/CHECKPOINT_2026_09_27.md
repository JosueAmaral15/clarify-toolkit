# Accumulated Work Checkpoint - 2026-09-27

User explicitly requested commit and push before Qt and branch investigation.
Branch: `COM-609038f3-58cb-4100-9b3b-b36177997cc2`.
Parent: `df4b12cfec3bea5ea6af903999e1fb7b906ad341` (previously local main).
This is a preservation checkpoint, not a release or approval to merge into main.

Scope: accumulated application, tests and documentation work, including the
36-marker audit and its fixes. Existing documentation/fixture moves are included;
the two binary fixtures are byte-identical moves, not new document contents.
The unrelated pre-existing `example.py` scratch file is excluded.

## Validation

- Previous exact source state: 315 focused tests passed in 24.28s, as recorded in
  LEGACY_TASK_AUDIT_2026_09_27.md. No application code changed before checkpoint.
- Fresh pre-commit runs were attempted with temporary home/settings, offscreen Qt,
  no core dumps, 180-second wall limit, 600 MiB process-tree ceiling and a system
  RAM stop at 85%. Runs of 315, 113 and 27 cases were stopped by that guard.
  They are incomplete runs, even where all case dots appeared before termination.
  Observed peak test-tree RSS: 328.0, 259.8 and 269.9 MiB respectively.
- AST parse passed for 119 staged Python files; all seven locale JSON files parse.
- Limited staged credential-pattern scan: no Google API key, GitHub token,
  OpenAI-style token or private-key header matches. This is not a full secrets
  audit or historical repository scan.
- Staged whitespace checks pass after whitespace-only normalization of five
  newly tracked text documents. No unrelated scratch files were staged.

Full suite, live providers, SAST/dependency scanning, Sonar and external coverage
are not certified by this checkpoint. Their missing evidence prevents promotion
to a primary/release branch under the requested protocol. The Qt lifecycle crash
remains open at checkpoint time. Do not force-push or delete existing branches.
