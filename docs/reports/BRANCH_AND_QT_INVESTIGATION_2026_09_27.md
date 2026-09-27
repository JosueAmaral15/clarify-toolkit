# Branch And Qt Investigation - 2026-09-27

## Scope And Checkpoint

The user requested commit/push before investigating branch integration, and
confirmed checkpointing all accumulated project work. Commit `af77ee9` was pushed
to `COM-609038f3-58cb-4100-9b3b-b36177997cc2`: 184 files, 16,124 insertions and
2,093 deletions. The unrelated pre-existing `example.py` remains excluded.
See [checkpoint validation](CHECKPOINT_2026_09_27.md) for limitations.

No merge, branch deletion, worktree pruning, force-push or main update was made.
Local main remains `df4b12c`; origin/main is `63071da`. The checkpoint is two
commits ahead of origin/main, including the already-local `df4b12c` commit.
Diagnostic/documentation follow-up commits on the COM branch are additional.

The requested external SIMPLICITY_PROTOCOL_3.md was reread in its Git/PR,
worktree, resource-safety and quality-gate sections. It requires COM-UUID working
branches and reviewed, validated promotion to main. The reviewed Git section
does not require a develop branch. Develop is an optional integration policy,
not a requirement attributed to the protocol.

## Branch Evidence

Fetched origin and compared ancestry, ahead/behind counts, patch equivalence
and three-way merge output. Counts below use local main `df4b12c` as the base.

| Branch | Tip | Only main | Only branch | Interpretation |
| --- | --- | ---: | ---: | --- |
| COM1-documentation-reading | 5a6e604 | 917 | 0 | Already included |
| COM10-documentation-reading-phases-6-7 | 62f366b | 969 | 0 | Already included |
| COM3-before-cleanup | 92d8888 | 358 | 0 | Already included |
| COM3-documentation-study | 413f90d | 59 | 0 | Already included |
| COM8-documentation-reading | 0284999 | 239 | 0 | Already included |
| COM9 | 0041d8b | 979 | 0 | Already included |
| COM4-code-study | baa0032 | 422 | 28 | Review historical documents |
| New checkpoint COM-UUID | af77ee9 | 0 | 1 | Review accumulated work |

Six of seven older local branches are already ancestors of main. Actual merge
commits include `2f17b7a` (COM8) and `8d95323` (COM3). There is no develop branch
locally or remotely. Remote-only COM2 and COM6 are also ancestors of main.

`origin/COM4-code-study` (`d3eda30`) is an ancestor of local COM4 (`baa0032`),
which equals `origin/clarify-COM4-code-study`. Do not integrate both names as
independent work. Although COM4 has 28 ancestry-exclusive commits (24 distinct
non-merge patches), its net merge contribution is **22 added Markdown files,
15,864 lines, no application source delta**. Commit counts are not missing-feature
counts. These are study notes/plans, protocol reports and historical test reports.
Some similarly named reports already exist; content must be compared before
discarding or archiving anything.

Read-only `git merge-tree <merge-base> main COM4-code-study` and the equivalent
against checkpoint HEAD each produced 22 additions, zero changed-in-both entries
and zero conflict markers. Base: `bca86dcd2f84dd37031a95b39f7b177473dca9e7`.
This is a textual conflict check, not an executed merge or acceptance test.

`origin/gh-pages` is generated site output and must not be merged into app source.
Three COM3/COM4/COM8 worktree registrations point to missing old directories and
are reported prunable. Verify relocated copies/backups before any cleanup.

## Promotion Blockers

- GitHub API reports all ten remote branches unprotected and no existing PRs.
- [Checkpoint Actions run](https://github.com/JosueAmaral15/clarify/actions/runs/36336564902)
  ended with `startup_failure`, zero jobs and no check runs. GitHub CLI suggests a
  possible workflow-file issue; the cause is unconfirmed. Do not attribute this
  to billing based on another project's history.
- All three workflow files parse as YAML; this does not validate GitHub schema or
  expressions. CI targets main/develop, installs selected test tools rather than
  all project dependencies, and contains unquoted `pip install PySide6>=6.9.3`
  style constraints that the shell interprets as redirection. Its coverage comment
  says 80% while the actual threshold is 70%; external coverage errors are ignored.
  The benchmark workflow has a PR-only job but no pull_request trigger.
- Sonar or an approved equivalent, external/local coverage, SAST/dependency gates
  and a completed relevant test run are not established by this checkpoint.
- [Dependabot alerts](https://github.com/JosueAmaral15/clarify/security/dependabot)
  report 23 open alerts on the default branch: 1 critical, 12 high, 7 moderate,
  3 low. The checkpoint lock still has anyio 4.12.1; the critical alert affects
  versions below 4.14.2. Reconcile all alerts against the checkpoint lock and
  update with compatibility tests. For example, default-branch httplib2 is no
  longer in the checkpoint lock. No dependencies were upgraded in this audit.

## Qt Evidence

The earlier combined test run crashed while recreating MainWindow and applying
the system theme (`app.setStyle("Fusion")`). Deferred-delete fixture cleanup and
isolated InsertPanel tests subsequently passed 315 focused cases. This narrows
the investigation but does not establish a production fix or a root cause.

Serial subprocess probes used offscreen Qt, temporary settings, disabled update
checks, modal-dialog stubs, no core dumps and resource guards:

| Probe | Result | Peak process-tree RSS |
| --- | --- | ---: |
| Simple widget, 12 cycles through dark/light/system | Exit 0 | 62.8 MiB |
| MainWindow, 5 cycles, deferred deletion | Exit 0 | 198.6 MiB |
| MainWindow, 5 cycles, queued deletion only | Exit 0 | 237.4 MiB |
| MainWindow, 3 cycles, explicit widget counts | Exit 0; zero remaining each cycle | 198.7 MiB |
| Committed-script candidate, simple widget, 3 cycles | Exit 0; zero remaining each cycle | 59.1 MiB |
| Same script, MainWindow, 2 cycles | Exit 0; zero remaining each cycle | 199.8 MiB |

An attempt combining 21 ResultsTree cases with four old-style MainWindow fixture
cycles was stopped at 85% system RAM before results. Fresh 315/113/27-case reruns
were also interrupted by that guard and are not passing test runs. No user
application was terminated to make room. Different RSS samples do not prove the
cause of the crash or a leak, and zero widgets does not prove zero native leaks.

The durable diagnostic is `scripts/diagnostics/qt_lifecycle_probe.py`:

```bash
.venv/bin/python scripts/diagnostics/qt_lifecycle_probe.py --mode theme --cycles 3
.venv/bin/python scripts/diagnostics/qt_lifecycle_probe.py --mode window --cycles 3
.venv/bin/python scripts/diagnostics/qt_lifecycle_probe.py --cleanup queued --cycles 3
```

It requires psutil, runs serially, stops at 85% system RAM, 600 MiB process-tree
RSS or 120 seconds, and returns 125 when guarded. These are sampled soft limits,
not a kernel memory cap. Run only when sufficient RAM is available. The previous
test-order/native-lifetime failure remains open; no theme production code was
changed during this investigation.

Follow-up checks: diagnostic AST parsing and diff whitespace validation passed;
a mocked 85% RAM reading returned 125 without starting a child. The canonical
task count was checked programmatically. These checks do not replace the suite.

## Proposed Integration Order

1. Repair CI startup and dependency/security blockers on COM branches. Establish
   reproducible serial test/coverage gates without exceeding the RAM policy.
2. Choose the branch policy before changing refs. Recommended for the accumulated
   work: create develop from origin/main as an integration branch; keep main stable
   and protect promotion by reviewed PR/checks. Simpler COM -> main remains valid
   if a permanent integration branch is unnecessary. Develop is not a workaround
   for failing checks.
3. Review the checkpoint PR independently, including its previously local parent,
   and integrate only after relevant gates pass. No release claim follows from
   the checkpoint push alone.
4. On a fresh COM integration branch, merge the latest COM4 once, review its 22
   historical documents and move retained material under `docs/archive/COM4/`.
   Repair links and label historical claims. Use a reviewed PR; preserving merge
   ancestry makes later branch cleanup verifiable. Do not resurrect root clutter
   or old production-readiness claims as current facts.
5. Validate the combined integration branch, then promote develop -> main by PR
   if that policy was chosen. Checkpoint/COM4 merge simulations are not enough.
6. Only after approval, remove confirmed redundant branches and stale worktree
   registrations. Preserve gh-pages and any unintegrated/moved work.

TASKS.md now tracks **30 open items**: 23 audited legacy requirements, three
environment validations, one Qt investigation, and three security/CI/integration
tasks. Security and CI are the next promotion priorities; Qt and LEG-24 remain
stability priorities before broader feature work. Live STT, Aspell pt_BR and
LLaVA still need their respective environment/user validation.
