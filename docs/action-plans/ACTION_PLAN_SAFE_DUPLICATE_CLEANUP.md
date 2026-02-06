# Action Plan: Safe Removal of Duplicate Doc Folders

**Date:** 2026-02-06  
**Branch:** COM3-documentation-study  
**Status:** PLANNING (Not Yet Executed)

---

## Objective

Remove duplicate doc folders from main merge **WITHOUT losing any relevant file content**.

---

## Current State

### Folder Structure (Both Exist)
```
OUR structure (COM3):
  docs/action-plans/     (16 files)
  docs/reports/          (64 files)
  docs/investigations/   (dir exists)
  docs/sessions/         (29 files)

THEIR structure (main):
  docs/plans/            (39 files)
  docs/code-study/       (26 files)
  docs/phases/           (18 files)
  docs/sprints/          (exists)
```

### Critical Files (MUST NOT LOSE)
- Our recent work:
  - docs/action-plans/ACTION_PLAN_FIX_CANCEL_CRASH_MANUAL.md
  - docs/investigations/CANCEL_BUTTON_NOT_STOPPING_WORKER.md
  - docs/investigations/TOCTOU_FIX_VERIFICATION.md
  - docs/reports/CANCEL_BUTTON_COMPLETE_FIX.md

---

## Safety Strategy

### Phase 1: Investigation (SAFE - Read Only)

#### Step 1.1: Identify Unique Files in Their Folders
```bash
# Files ONLY in docs/plans/ (not in docs/action-plans/)
comm -23 \
  <(ls docs/plans/ | sort) \
  <(ls docs/action-plans/ | sort) \
  > /tmp/unique_in_plans.txt

# Files ONLY in docs/code-study/ (not in docs/reports/ or docs/sessions/)
ls docs/code-study/ > /tmp/all_code_study.txt

# Files ONLY in docs/phases/ (not in docs/reports/ or docs/plans/)
ls docs/phases/ > /tmp/all_phases.txt
```

**Expected result:** List of files that exist ONLY in their folders

#### Step 1.2: Check for Content Differences
For files that exist in BOTH locations, compare content:

```bash
# Compare ACTION_PLAN files
for file in docs/action-plans/*.md; do
  basename=$(basename "$file")
  if [ -f "docs/plans/$basename" ]; then
    if ! diff -q "$file" "docs/plans/$basename" >/dev/null 2>&1; then
      echo "DIFF: $basename"
    fi
  fi
done > /tmp/files_with_diffs.txt
```

**Expected result:** List of files with actual content differences

#### Step 1.3: Verify Our Recent Work Exists
```bash
# Check critical files exist in OUR structure
test -f docs/action-plans/ACTION_PLAN_FIX_CANCEL_CRASH_MANUAL.md && echo "✓ Cancel crash plan found"
test -f docs/investigations/CANCEL_BUTTON_NOT_STOPPING_WORKER.md && echo "✓ Worker investigation found"
test -f docs/investigations/TOCTOU_FIX_VERIFICATION.md && echo "✓ TOCTOU verification found"
test -f docs/reports/CANCEL_BUTTON_COMPLETE_FIX.md && echo "✓ Cancel fix report found"
```

**Expected result:** All 4 files found (✓)

---

### Phase 2: Decision Matrix (SAFE - Planning Only)

For each file in their folders, decide:

**Case A: File exists in OUR folder with SAME content**
- Action: Safe to delete their version
- Risk: NONE (duplicate)

**Case B: File exists in OUR folder with DIFFERENT content**
- Action: MANUAL REVIEW required
- Risk: HIGH (may lose changes)
- Solution: Compare, merge if needed, or keep both

**Case C: File ONLY in their folder (not in ours)**
- Action: MOVE to our folder (don't delete!)
- Risk: MEDIUM (new file we don't have)
- Solution: Copy to equivalent OUR folder first

**Case D: File in their folder, no equivalent in our structure**
- Action: CREATE equivalent folder, move file
- Risk: LOW (organizational issue)
- Solution: Decide proper location, move there

---

### Phase 3: Safe Execution Plan

#### Step 3.1: Backup First (CRITICAL)
```bash
# Create safety backup branch
git branch COM3-before-cleanup

# Tag current state
git tag merge-with-duplicates

# Verify backup exists
git branch | grep COM3-before-cleanup && echo "✓ Backup created"
```

#### Step 3.2: Handle Case C Files (MOVE, don't delete)
```bash
# For each unique file in their folders
while read file; do
  # Determine destination in our structure
  if [[ "$file" == *"ACTION_PLAN"* ]]; then
    dest="docs/action-plans/$file"
  elif [[ "$file" == *"REPORT"* ]] || [[ "$file" == *"SUMMARY"* ]]; then
    dest="docs/reports/$file"
  # ... more logic ...
  fi
  
  # MOVE (don't delete) if doesn't exist in our structure
  if [ ! -f "$dest" ]; then
    echo "Moving: $file -> $dest"
    git mv "docs/plans/$file" "$dest"
  fi
done < /tmp/unique_in_plans.txt
```

#### Step 3.3: Handle Case B Files (MANUAL REVIEW)
```bash
# For files with differences
while read file; do
  echo "=== DIFF: $file ==="
  echo "OUR version: docs/action-plans/$file"
  echo "THEIR version: docs/plans/$file"
  diff -u "docs/action-plans/$file" "docs/plans/$file" | head -50
  
  echo "Action: [K]eep ours, [M]erge, [B]oth? "
  # WAIT for user decision
done < /tmp/files_with_diffs.txt
```

**IMPORTANT:** Do NOT proceed automatically - require user confirmation!

#### Step 3.4: Remove Duplicate Folders (ONLY after Steps 3.2-3.3)
```bash
# Only delete if ALL files handled
git rm -r docs/plans/
git rm -r docs/code-study/  
git rm -r docs/phases/

# Verify our folders intact
ls docs/action-plans/ docs/reports/ docs/investigations/ docs/sessions/
```

#### Step 3.5: Verification Checklist
- [ ] All our recent work files exist
- [ ] No unique files lost from their folders
- [ ] Files with differences were reviewed
- [ ] Folder count reduced (no duplicates)
- [ ] Syntax check passes
- [ ] Can rollback if needed (backup branch exists)

---

## Execution Workflow

### DO NOT RUN AUTOMATICALLY!

**Human verification required at each step:**

```bash
# Step 1: Investigation
./investigate_duplicates.sh > /tmp/investigation_report.txt
cat /tmp/investigation_report.txt
# STOP - User reviews report

# Step 2: Backup
git branch COM3-before-cleanup
git tag merge-with-duplicates
# STOP - User confirms backup

# Step 3: Move unique files
# MANUAL EXECUTION - one file at a time
# STOP - User confirms each move

# Step 4: Review differences  
# MANUAL REVIEW - show diffs to user
# STOP - User decides keep/merge/both

# Step 5: Remove duplicates (ONLY after 3 & 4 complete)
git rm -r docs/plans/
# STOP - User confirms deletion

# Step 6: Commit
git commit -m "..."
# STOP - User reviews final state
```

---

## Investigation Scripts

### Script 1: Find Unique Files
```bash
#!/bin/bash
# find_unique_files.sh

echo "=== Files ONLY in docs/plans/ ==="
comm -23 \
  <(cd docs/plans && ls *.md 2>/dev/null | sort) \
  <(cd docs/action-plans && ls *.md 2>/dev/null | sort)

echo -e "\n=== Files ONLY in docs/code-study/ ==="
ls docs/code-study/*.md 2>/dev/null | xargs -n1 basename | while read f; do
  if ! find docs/reports docs/sessions -name "$f" 2>/dev/null | grep -q .; then
    echo "$f"
  fi
done

echo -e "\n=== Files ONLY in docs/phases/ ==="
ls docs/phases/*.md 2>/dev/null | xargs -n1 basename | while read f; do
  if ! find docs/reports docs/plans -name "$f" 2>/dev/null | grep -q .; then
    echo "$f"
  fi
done
```

### Script 2: Find Content Differences
```bash
#!/bin/bash
# find_content_diffs.sh

echo "=== Files with DIFFERENT content ==="

# Compare action-plans vs plans
for our_file in docs/action-plans/*.md; do
  basename=$(basename "$our_file")
  their_file="docs/plans/$basename"
  
  if [ -f "$their_file" ]; then
    if ! diff -q "$our_file" "$their_file" >/dev/null 2>&1; then
      echo "DIFF: $basename"
      echo "  Our: $our_file"
      echo "  Their: $their_file"
      echo "  Lines diff: $(diff "$our_file" "$their_file" | grep "^[<>]" | wc -l)"
    fi
  fi
done
```

### Script 3: Verify Critical Files
```bash
#!/bin/bash
# verify_critical_files.sh

echo "=== Verifying Our Critical Files ==="

critical_files=(
  "docs/action-plans/ACTION_PLAN_FIX_CANCEL_CRASH_MANUAL.md"
  "docs/investigations/CANCEL_BUTTON_NOT_STOPPING_WORKER.md"
  "docs/investigations/TOCTOU_FIX_VERIFICATION.md"
  "docs/reports/CANCEL_BUTTON_COMPLETE_FIX.md"
  "docs/investigations/MERGE_CONFLICT_RESOLUTION_POSTMORTEM.md"
)

all_found=true
for file in "${critical_files[@]}"; do
  if [ -f "$file" ]; then
    echo "✓ Found: $file"
  else
    echo "✗ MISSING: $file"
    all_found=false
  fi
done

if [ "$all_found" = true ]; then
  echo -e "\n✓ All critical files intact"
  exit 0
else
  echo -e "\n✗ CRITICAL FILES MISSING!"
  exit 1
fi
```

---

## Risk Assessment

### LOW RISK Actions
- ✓ Running investigation scripts (read-only)
- ✓ Creating backup branch
- ✓ Showing file differences to user

### MEDIUM RISK Actions
- ⚠️ Moving unique files (if wrong destination)
- ⚠️ Merging different content (if manual error)

### HIGH RISK Actions
- ❌ Deleting folders without verification
- ❌ Automatic conflict resolution
- ❌ Proceeding without backups

---

## Rollback Plan

If something goes wrong:

```bash
# Option 1: Reset to before cleanup
git reset --hard COM3-before-cleanup

# Option 2: Reset to merge point
git reset --hard merge-with-duplicates

# Option 3: Cherry-pick specific commit
git cherry-pick <commit-hash>

# Verify rollback worked
./verify_critical_files.sh
```

---

## Expected Outcome

### Before Cleanup
```
docs/
├── action-plans/    (16 files)
├── plans/           (39 files) ← DUPLICATE
├── reports/         (64 files)
├── code-study/      (26 files) ← DUPLICATE
├── sessions/        (29 files)
├── phases/          (18 files) ← DUPLICATE
└── (many loose files)
```

### After Cleanup
```
docs/
├── action-plans/    (X files - may increase if unique files moved)
├── reports/         (Y files - may increase if unique files moved)
├── investigations/  (Z files - includes our work)
├── sessions/        (W files - may increase if unique files moved)
└── (fewer loose files)
```

---

## User Approval Required

**Before proceeding, user must confirm:**

1. [ ] Investigation scripts run successfully
2. [ ] Backup branch created and verified
3. [ ] Unique files list reviewed (nothing critical)
4. [ ] Content differences reviewed (manual decisions made)
5. [ ] Critical files verified present
6. [ ] Understands rollback procedure
7. [ ] Ready to proceed with cleanup

---

## Status

**Current:** PLANNING PHASE  
**Next:** Run investigation scripts  
**Execute:** ONLY with explicit user approval at each step  
**Safety:** Backup branch + tag created before ANY deletions

---

**CRITICAL:** Do NOT execute automatically. User must review each phase output before proceeding to next phase.
