# Public Repository Action Plan - 2026-11-13

## Objective

Make the public `main` branch reviewable and reproducible before using it for
the Alignerr CC-CLI project-creation evaluation. Keep product development and
the large security branch outside this bounded repair.

## Ordered Stages

1. Restore CI collection and dependency installation.
   - Install the locked project dependencies instead of a partial ad hoc set.
   - Exclude historical executable diagnostics that use local files, live
     providers, import-time writes, or `sys.exit()` from automated collection.
   - Run eligible test modules in isolated serial processes so a native Qt exit
     identifies the responsible module and cannot contaminate later modules.
2. Validate locally with bounded commands.
   - Verify collection, focused CI helper tests, lock consistency, workflow
     syntax, changed-file formatting, Gitleaks, and diff integrity.
3. Publish the CI repair through a dedicated pull request.
   - Inspect hosted checks before merge and record every failure honestly.
4. Re-audit the merged public repository.
   - Confirm the English README, MIT license, local links, Gitleaks status, and
     current GitHub security/check state.
5. Prepare Alignerr evidence.
   - Record the public URL, project summary, validation evidence, remaining
     work, and a realistic work queue exceeding twenty hours.
   - Do not start a timed task or submit an evaluation without the user's
     explicit action at that boundary.
6. Plan branch reconciliation separately.
   - Inventory unpublished branches by dependency and risk.
   - Integrate bounded chains through reviewed pull requests; never merge the
     accumulated development graph into `main` blindly.

## Rollback

- Before merge: close the pull request and delete only its dedicated branch.
- After merge: revert the merge commit through a new pull request.
- The repair must not modify user documents, credentials, recovery data, or
  unrelated worktree files.

## Completion Evidence

- Hosted CI reaches collection and reports test modules deterministically.
- Gitleaks reports no findings on Git history and the current working tree.
- `README.md` remains English and all checked local links resolve.
- The pull request, checks, merge decision, and residual failures are recorded
  in `history-chat.md` and the final report.
