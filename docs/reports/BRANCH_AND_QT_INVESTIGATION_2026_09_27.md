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

## Follow-Up: Explicit Keep, Integrate Or Delete Review

Revalidated after the user's request to review branches before continuing.
Fetched origin without pruning; GitHub branch inventory matches local remote refs.
The comparison target here is **published origin/main `63071da`**, not local main.
There are nine local and ten remote branches, and no existing PRs.

### No Merge Needed: Deletion Candidates

Every ref below has zero commits absent from origin/main. Deleting these branch
names would not remove their committed work from main's history. Deletion is a
recommendation, not an action performed by this review.

| Branch name | Local candidate | Remote candidate | Caveat |
| --- | --- | --- | --- |
| COM1-documentation-reading | Yes | Yes | None found in registered worktrees |
| COM2 | No local branch | Yes | Already included in published main |
| COM3-before-cleanup | Yes | No remote branch | Historical cleanup pointer |
| COM3-documentation-study | Yes | Yes | Resolve stale local worktree registration first |
| COM6-documentation-reading-phases-6-7 | No local branch | Yes | Already included in published main |
| COM8-documentation-reading | Yes | Yes | Local/remote tips differ, but both are included; stale local worktree |
| COM9 | Yes | No remote branch | Already included in published main |
| COM10-documentation-reading-phases-6-7 | Yes | No remote branch | Already included in published main |

Total: **six local refs and five remote branch names** are already integrated.
Confirm no relocated checkout or collaborator still relies on a name before
deleting it. The three registered historical COM3/COM4/COM8 paths do not exist;
this does not establish that no relocated copy or uncommitted work exists elsewhere.

### Preserve Until Integration

- `COM-609038f3-58cb-4100-9b3b-b36177997cc2`, local and remote, is `135e37c`:
  three commits ahead of origin/main (`df4b12c`, `af77ee9`, `135e37c`), zero behind.
  Keep it; review and merge via PR only after the previously recorded gates pass.
- Local `COM4-code-study` equals remote `clarify-COM4-code-study` at `baa0032`.
  Preserve the latest tip and integrate once. All 22 contributing Markdown blobs
  were compared against every tracked blob in checkpoint HEAD: no byte-identical
  copies exist there. This does not exclude semantic overlap with other reports.
  Read-only merge simulation against `135e37c` still shows 22 additions and no
  conflict markers. Review/archive the documents rather than discard the branch.
- Remote `COM4-code-study` at `d3eda30` is strictly included in the newer COM4
  tip. Its name is redundant, but it is **not** merged into main. It can be removed
  after confirming the newer remote remains preserved and nobody depends on the
  old name; conservatively defer that deletion until COM4 integration completes.

### Keep As Permanent Branches

- Keep local and remote `main`. Local main's one unpublished-to-main commit is
  already preserved in the published checkpoint. Integrate via that PR, not a
  separate direct push or duplicate cherry-pick.
- Keep remote `gh-pages`: `.github/workflows/docs.yml` explicitly publishes there.
  It is not an application merge candidate.
- Do not create develop just to reduce branch count. Decide whether an ongoing
  integration branch is useful; it is unnecessary for deleting merged branches.

Recommended sequence: approve cleanup of already-integrated refs; verify stale
worktrees before pruning; resolve checkpoint gates; integrate checkpoint and
latest COM4 in separate reviewed PRs; remove their branch names after integration.
No merge, deletion, worktree prune, commit or push was performed in this follow-up.
Only this report and the required history log changed. No application tests were
needed for this read-only Git review; task count remains **30 open items**.

## Authorized Cleanup - Recovery Record

The user subsequently approved cleanup of the already-integrated branches.
This supersedes the earlier awaiting-approval status, not the pending merge gates.
The deleted-name candidates below were rechecked against published main. Their
commits remain reachable from main; these exact tips allow branch-name recovery.

| Branch | Local tip | Remote tip |
| --- | --- | --- |
| COM1-documentation-reading | 5a6e604b24e4565b74b78bf72f451f3b66fdfc31 | 5a6e604b24e4565b74b78bf72f451f3b66fdfc31 |
| COM2 | Not present | 2d36375fe1763dca3e80428f3388e31438b02481 |
| COM3-before-cleanup | 92d88881e19f38528ea4ae4427c8e550ac352ce6 | Not present |
| COM3-documentation-study | 413f90d4ca8dcf45407fe709014a0532d934b2a3 | 413f90d4ca8dcf45407fe709014a0532d934b2a3 |
| COM6-documentation-reading-phases-6-7 | Not present | 16b4261059aa9f24813b5c3c77d5807a006b4432 |
| COM8-documentation-reading | 0284999b6f2e8681eed4b15e0ba139f521e9579c | 855e30c6f81d4fca3166c53fe59ca3a4e1981187 |
| COM9 | 0041d8b04f764a2b02cd85136ca9270baf9fb966 | Not present |
| COM10-documentation-reading-phases-6-7 | 62f366b385d7ba658fa59e5b6a91be60da1adb2a | Not present |

### Relocated Worktrees Found

A wider, bounded directory search found all three worktrees under the project's
sibling `old/Other work-trees-old/` directory. They are relocated archives, not
missing directories. Their indexes and tracked/untracked status were clean when
checked using the correct git-dir/work-tree pairs. No archive content was removed.

Before repair, their registration metadata and original `.git` link files were
archived in `.git/worktree-registration-backup-20260927-before-cleanup.tar.gz`.
`git worktree repair` restored all three paths. COM3 and COM8 were detached
at their existing commits before deleting the merged branch names; COM4 stays
attached. No worktree pruning is necessary or appropriate after this discovery.

### Cleanup Completed

All six local candidates and all five remote candidates in the recovery table
were deleted after each tip passed ancestry checks against both origin/main and
the current checkpoint. Local deletion used `git branch -d`, not `-D`. Remote
deletions were one atomic push with explicit expected-SHA leases: a concurrent
change to any targeted remote tip would reject the operation. No retained branch
history was rewritten. No merges or application source edits were made.

Post-operation inventory: **three local branches and five remote branches**:

| Remaining branch | Local | Remote |
| --- | --- | --- |
| main | df4b12c | 63071da |
| COM-609038f3-58cb-4100-9b3b-b36177997cc2 | 135e37c | 135e37c |
| COM4-code-study | baa0032 | d3eda30 |
| clarify-COM4-code-study | Not present | baa0032 |
| gh-pages | Not present | 3105fe2 |

All retained tips are unchanged. The old remote COM4 name remains intentionally
until the newer COM4 work is integrated. All three archived worktrees remain
available; COM3/COM8 are detached snapshots, COM4 remains on its branch.
`git worktree prune --dry-run --verbose` now produces no candidates.

Branch cleanup is finished; the broader integration task remains open. Remaining
work: resolve security/CI gates, review and integrate the checkpoint and latest
COM4, then remove those temporary branch names when appropriate. No develop
branch was created. TASKS.md still has 30 open items; this cleanup completes a
part of the existing Git integration item, not the entire item.

## Develop Bootstrap - Maintainer Decision

The maintainer explicitly requested develop after branch cleanup. It was created
locally and published at `63071dacf9fadd605f5fa5ab78643f132408e9b7`, exactly
origin/main, with tracking set to origin/develop. Creation used an expected-absent
remote lease to avoid overwriting an independently created branch. Main and the
default branch were not changed; checkpoint/COM4 were not merged.

The active policy is now COM-UUID -> reviewed develop PR -> reviewed main PR.
The external protocol sections 2602-2835, 11238-11380 and 11810-11846 were reread.
Develop is the user's selected integration layer, not an invented protocol rule.
The updated [Git guide](../guides/reference/GIT_WORKFLOW_QUICK_REFERENCE.md) and
CONTRIBUTING.md document the policy and gates; the old report copy is historical.

Work records use new branch `COM-3168ba3b-697a-41f5-ba9d-8e1b75a05ee2`, based on
checkpoint `135e37c` to preserve the pending cleanup records. This branch is
stacked on the checkpoint, not an independent documentation-only PR to develop.
The prior checkpoint branch remains unchanged. No PR or merge was created here.

GitHub protection queries for both main and develop returned HTTP 403, explicitly
requiring GitHub Pro or public repository visibility. Neither billing nor
visibility was changed. Protection cannot be claimed as enabled. This user-side
decision is now recorded under the existing integration/CI task, not a new task.
The [develop startup run](https://github.com/JosueAmaral15/clarify/actions/runs/36339841831)
completed with startup_failure; creating the branch did not repair CI. Remaining
security, coverage, quality and Qt gates are unchanged. No release readiness is
implied by this bootstrap, and there are still 30 open tasks.

Validation: local/remote develop tips equal published main, develop tracks
origin/develop, the main-to-develop content diff is empty, and local main remains
df4b12c. Local links in the active guide and diff whitespace checks pass. No
application code changed or application test suite was run for this branch/docs
operation. The documentation commit also preserves the previously uncommitted
review/cleanup records, excluding the unrelated example.py.
