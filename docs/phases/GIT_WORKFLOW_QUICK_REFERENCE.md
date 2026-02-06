# Git Workflow - Quick Reference Card

**Last Updated**: 2026-01-18  
**For**: Clarify Project - Branch-Based Workflow  
**Audience**: All programmers working on the project

---

## ⚡ Daily Workflow (Most Common)

```bash
# 1. Switch to your branch
git checkout COM<N>

# 2. Make changes
vim <file>

# 3. Stage all changes
git add -A

# 4. Commit with descriptive message
git commit -m "docs: update feature documentation"

# 5. Push to remote
git push origin COM<N>
```

---

## 🌿 Creating New Branch

### **Pattern 1: COM-UUID** (Protocol Standard)
```bash
# Linux/Mac
git checkout -b COM-$(uuidgen | tr '[:upper:]' '[:lower:]')

# Python (cross-platform)
git checkout -b COM-$(python -c "import uuid; print(uuid.uuid4())")

# Example result: COM-a5e531b2-5d4f-a827-b3c8-24a52b27f281
```

### **Pattern 2: COM<N>-feature** (Recommended ⭐)
```bash
# Feature
git checkout -b COM2-add-search-filter

# Bug fix
git checkout -b COM2-fix-threading-bug

# Refactor
git checkout -b COM5-refactor-ui-components
```

**Use Pattern 2 for most work!**

---

## 📦 Common Tasks

### **Sync with Main**
```bash
# Get latest main changes
git fetch origin main

# Merge main into your branch
git merge origin/main

# Or rebase (cleaner history)
git rebase origin/main
```

### **Save Work in Progress**
```bash
# Stash changes
git stash save "WIP: implementing feature X"

# Switch branches
git checkout main

# Later, restore stashed work
git checkout COM2
git stash pop
```

### **View Status**
```bash
# Check current branch and changes
git status

# View commit history
git log --oneline

# See what changed
git diff
```

### **Undo Changes**
```bash
# Discard unstaged changes to file
git checkout -- <file>

# Unstage file (keep changes)
git reset HEAD <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) ⚠️
git reset --hard HEAD~1
```

---

## 🔀 Merge to Main

### **Standard Merge**
```bash
# 1. Ensure branch is up-to-date
git checkout COM2
git fetch origin main
git merge origin/main

# 2. Push your branch
git push origin COM2

# 3. Ask user/AI to merge COM2 → main
# Or merge manually:
git checkout main
git merge COM2
git push origin main
```

### **If Conflicts Occur**
```bash
# Merge shows conflicts
git merge origin/main
# Auto-merging file.py
# CONFLICT (content): Merge conflict in file.py

# 1. Open conflicted files and resolve
vim file.py

# 2. Stage resolved files
git add file.py

# 3. Complete merge
git commit -m "merge: resolve conflicts with main"

# 4. Push
git push origin COM2
```

---

## 🧹 Cleanup After Merge

```bash
# Switch to main
git checkout main

# Pull merged changes
git pull origin main

# Delete local branch
git branch -d COM2

# Delete remote branch
git push origin --delete COM2
```

---

## 📝 File Naming

### ✅ **Correct**
```
SESSION_1_SUMMARY.md
CODE_STUDY_PHASE1_REPORT.md
ACTION_PLAN_FIX_BUG.md
```

### ❌ **Incorrect**
```
SESSION_1_SUMMARY_2.md         # No suffixes (unless conflict)
docs/COM2/SESSION_1_SUMMARY.md # No programmer folders
session_1_summary.md           # Use SCREAMING_SNAKE_CASE
```

**Exception**: Keep `_2` suffix when conflicts exist with other programmer's version.

---

## 🎯 Commit Message Format

**Format**: `<type>: <description>`

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

**Examples:**
```bash
git commit -m "feat: add search filter to JSON dock"
git commit -m "fix: resolve threading issue in search worker"
git commit -m "docs: update README with new installation steps"
git commit -m "refactor: extract validation logic to mixin"
```

---

## 🚨 Emergency Commands

### **Abort Merge**
```bash
git merge --abort
```

### **Undo Last Commit (Keep Changes)**
```bash
git reset --soft HEAD~1
```

### **Restore Deleted File**
```bash
git checkout HEAD -- <file>
```

### **View Stashed Work**
```bash
git stash list
git stash show stash@{0}
```

### **Force Push (Use Carefully!)**
```bash
# Only on YOUR branch, NEVER on main
git push --force origin COM2
```

---

## 📊 Useful One-Liners

```bash
# View all branches
git branch -a

# See which files changed
git diff --name-only

# Find who wrote a file
git log --follow <filename>

# See line-by-line authors
git blame <filename>

# List recent commits
git log --oneline -10

# See commit details
git show <commit-hash>

# Check if branch is up-to-date with main
git fetch origin main
git log COM2..origin/main

# View all remote branches
git branch -r
```

---

## ✅ Pre-Merge Checklist

Before merging to main:

- [ ] All tests pass (`pytest` / `npm test`)
- [ ] Code quality checks pass (`pylint`, `black`, `eslint`)
- [ ] No debug statements (print, console.log)
- [ ] Documentation updated (README, docstrings)
- [ ] CHANGELOG.md updated
- [ ] Commit messages are descriptive
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts

**Quick verify:**
```bash
git status                        # No uncommitted changes
git log --oneline COM2 ^main      # Review commits
pytest tests/                     # Tests pass
pylint src/ --rcfile=.pylintrc    # Quality check
git diff origin/main              # Review all changes
```

---

## 🔗 References

- Full documentation: `PROJECT_UPDATE_FILE_RENAMING_STANDARDIZATION.md`
- Protocol: `docs/protocolos/SIMPLICITY_PROTOCOL_3.md`
- Contributing: `CONTRIBUTING.md`

---

**Remember**: Pattern 2 (`COM<N>-feature`) is recommended for daily work! ⭐

**Questions?** Check full documentation or ask project maintainer.
