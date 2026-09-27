# Git Workflow - Quick Reference

Updated: 2026-09-27. Current Clarify policy, selected by the maintainer under
Simplicity 3. This replaces the old direct-to-main examples.

## Branch Roles

| Branch | Purpose | Changes enter through |
| --- | --- | --- |
| `COM-<UUID>` | AI task work | Scoped commits on the task branch |
| `develop` | Shared integration | Reviewed task PRs with validation evidence |
| `main` | Stable/default branch | Reviewed promotion PR from develop |
| `gh-pages` | Generated documentation | Documentation publishing workflow only |

Simplicity 3 requires COM-UUID branches for AI work and a reviewed PR even for
solo development. It does not mandate develop by name: the maintainer explicitly
selected the `COM-UUID -> develop -> main` policy on 2026-09-27. Human contributors
may use descriptive COM1-feature branches. Do not commit directly to develop or
main, bypass failed checks, or merge gh-pages into application branches.

## Start A Task

Inspect the worktree first. Preserve unrelated edits; do not automatically stash,
reset, clean, or switch a dirty worktree. A separate worktree is preferable when
another task is active.

```bash
git status --short --branch
git worktree list
git fetch origin
# Only in a clean worktree, create a new AI branch from published develop:
git switch --no-track -c "COM-$(python -c 'import uuid; print(uuid.uuid4())')" origin/develop
```

Update root `history-chat.md` before work and before ending the session. Stage
only intended files, review the staged diff, validate according to change risk,
and commit with a Conventional Commit message. Push the task branch when
authorized; never include unrelated scratch files or credentials.

```bash
git diff --cached --check
git diff --cached
# After validation and commit:
git push --set-upstream origin HEAD
```

Use PR base `develop` for task integration. Obtain approval before opening or
merging a PR when it has not already been authorized. Record self-review even
when working alone. Retain branch names until their work is integrated.

## Integration And Promotion Gates

Before merging into develop, review the full base-to-head diff, not only the last
commit. Record exact tested SHA, test commands/results, skips, limitations and
rollback approach. Use focused tests plus integration/GUI tests appropriate to
the affected behavior; incomplete or guarded runs are not passing evidence.

Before promotion from develop to main, additionally confirm:

- Local and external coverage evidence, with 80% new-code coverage as the
  protocol's recommended default and no unexplained regression.
- Approved SonarQube/SonarCloud quality gate, SAST, dependency and secret checks.
- Passing CI for the actual promotion candidate and reviewed changes.
- Updated documentation and a viable rollback plan. No deployment follows
  automatically from branch creation or a checkpoint push.

After the initial bootstrap, integrations into either permanent branch require
these applicable gates; develop is not an escape route for failed checks.
Run GUI validation serially with offscreen Qt, temporary settings, explicit
timeouts and active memory monitoring. Stop at 85% total system RAM. Do not
re-run large suites under memory pressure just to obtain a green result.

After successful integration and approval, verify ancestry against the published
target and inspect linked worktrees before deleting a task branch. Prefer normal
`git branch -d`; remote deletion needs authorization and a current tip check.
Never remove an archived worktree merely because its registration path is stale.

## Current Bootstrap And Limitations

`develop` was created locally and on origin at
`63071dacf9fadd605f5fa5ab78643f132408e9b7`, exactly the published main tip.
It tracks origin/develop. This created a reference to existing history; it did
not merge the checkpoint, release code or change main/default-branch settings.

The existing checkpoint COM branch remains pending integration. The branch
recording this setup is stacked on that checkpoint to preserve accumulated local
documentation changes. Its future PR must account for that ancestry: do not
describe the whole develop-to-branch diff as documentation-only before the
checkpoint is integrated. New independent tasks start from origin/develop.

GitHub returned HTTP 403 for main/develop protection on this private repository:
the current plan requires an upgrade or public visibility for that feature.
Neither was changed. PR/check discipline is currently procedural, **not enforced
by server protection**. Enabling protection requires a maintainer decision; once
available, require PRs/checks, disallow force pushes/deletion and avoid admin
bypass. For solo work, use documented self-review without requiring an impossible
second-person approval.

The bootstrap [develop CI run](https://github.com/JosueAmaral15/clarify/actions/runs/36339841831)
ended with startup_failure. Existing CI targets main/develop, but a trigger is
not proof of functioning gates. Dependency alerts, Qt investigation, CI repair
and external quality/coverage setup remain open. Do not merge pending work while
these promotion requirements lack evidence.

See [TASKS](../../TASKS.md), the
[branch investigation](../../reports/BRANCH_AND_QT_INVESTIGATION_2026_09_27.md),
and [Contributing](../../../CONTRIBUTING.md). The authoritative protocol reread
for this decision was the maintainer's external English SIMPLICITY_PROTOCOL_3.md;
the repository also contains a [protocol reference](../../protocols/simplicity/SIMPLICITY_PROTOCOL_3.md).
