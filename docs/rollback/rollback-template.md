# 🔄 Rollback Plan Template - Clarify Project

**Project**: Clarify - File Management & Text Processing Tool  
**Version**: v1.0.0  
**Created**: 2026-02-08  
**Protocol**: SIMPLICITY_PROTOCOL_3.md Step 12.5 (MANDATORY)  
**Solo Developer**: Required for emergency procedures  

---

## 📋 Overview

**Purpose**: Document how to safely rollback changes when things go wrong in production.

**When to use this plan**:
- Critical bug discovered in production
- Feature causing data corruption
- Performance degradation after deploy
- User reports of system failures
- Need to quickly revert to stable state

**Solo Developer Context**:
> "You're alone at 2AM when production breaks. This document is your lifeline."
> - SIMPLICITY_PROTOCOL_3.md

---

## 🎯 Quick Rollback Decision Matrix

| Severity | Symptoms | Action | Time Budget |
|----------|----------|--------|-------------|
| 🔴 **CRITICAL** | Data loss, crashes, security breach | Rollback immediately | <5 minutes |
| 🟡 **HIGH** | Major features broken, many users affected | Rollback within 30 min | <30 minutes |
| 🟢 **MEDIUM** | Minor bugs, workarounds possible | Fix forward or rollback | <2 hours |
| ⚪ **LOW** | Cosmetic issues, rare edge cases | Fix forward | Next sprint |

---

## 🚨 Emergency Rollback Procedure (CRITICAL)

**Use when**: Data loss, security breach, application won't start

### Step 1: Stop the Application (30 seconds)
```bash
# If running as service
sudo systemctl stop clarify

# If running in terminal
# Press Ctrl+C to stop

# Verify stopped
ps aux | grep clarify
```

### Step 2: Identify Last Stable Commit (60 seconds)
```bash
cd /path/to/clarify/

# View recent commits
git --no-pager log --oneline -10

# Find last known good commit (look for tags like 'v1.0.0' or recent stable)
# Example output:
# abc1234 fix: critical bug
# def5678 feat: new feature (← PROBLEM COMMIT)
# xyz9876 v1.0.0 stable (← ROLLBACK TO THIS)
```

### Step 3: Rollback Code (60 seconds)
```bash
# Option A: Soft rollback (can redo later)
git reset --soft <last-good-commit-hash>
# Example: git reset --soft xyz9876

# Option B: Hard rollback (cannot redo - use for emergencies)
git reset --hard <last-good-commit-hash>
# Example: git reset --hard xyz9876

# Option C: Revert specific commit (cleanest)
git revert <problematic-commit-hash>
# Example: git revert def5678
```

### Step 4: Restore Dependencies (if needed) (60 seconds)
```bash
# Reinstall exact versions from lock file
poetry install --sync

# OR if using pip
pip install -r requirements.txt --force-reinstall
```

### Step 5: Verify Rollback (60 seconds)
```bash
# Check files match expected state
git --no-pager diff

# Quick smoke test
python main.py --version
python -m pytest tests/ -x --tb=short  # Exit on first failure
```

### Step 6: Restart Application (30 seconds)
```bash
# If service
sudo systemctl start clarify
sudo systemctl status clarify

# If manual
python main.py &
```

### Step 7: Verify Stability (120 seconds)
- [ ] Application starts without errors
- [ ] Basic functionality works (open file, process text)
- [ ] No error messages in logs
- [ ] Can save/load files

**Total Time**: ~5-8 minutes

---

## 🔍 Standard Rollback Procedure (HIGH/MEDIUM)

**Use when**: Non-critical bugs, you have time to investigate

### Phase 1: Assessment (10 minutes)

```bash
# Check what changed
git --no-pager log --oneline --since="1 day ago"
git --no-pager diff HEAD~5..HEAD --stat

# Check logs for errors
tail -100 logs/clarify.log | grep -i error

# Check disk space
df -h

# Check running processes
ps aux | grep clarify
```

**Questions to ask**:
- [ ] When did the problem start?
- [ ] What was deployed recently?
- [ ] Can users work around the issue?
- [ ] Is data at risk?
- [ ] How many users are affected?

### Phase 2: Decision (5 minutes)

**Option A: Rollback** (if problem is severe)
- Critical functionality broken
- Many users affected
- No quick fix available
- Data corruption possible

**Option B: Fix Forward** (if problem is minor)
- Issue is isolated
- Few users affected
- Quick fix available (< 30 minutes)
- No data risk

**Option C: Feature Flag** (if possible)
- Disable problematic feature
- Keep other functionality working
- Fix in development

### Phase 3: Execute Rollback (if chosen) (15 minutes)

1. **Create rollback branch**:
   ```bash
   git checkout -b rollback-emergency-$(date +%Y%m%d-%H%M)
   ```

2. **Identify commits to revert**:
   ```bash
   # Find problematic commits
   git log --oneline --since="1 week ago"
   
   # Revert specific commits (safest)
   git revert <commit-hash1> <commit-hash2>
   ```

3. **Test rollback locally**:
   ```bash
   # Run critical tests
   pytest tests/test_critical.py -v
   
   # Manual smoke test
   python main.py
   # Test: Open file, process text, save result
   ```

4. **Deploy rollback**:
   ```bash
   git push origin rollback-emergency-*
   
   # Update production
   git pull origin rollback-emergency-*
   poetry install --sync
   ```

5. **Monitor**:
   ```bash
   tail -f logs/clarify.log
   # Watch for 5-10 minutes
   ```

### Phase 4: Post-Rollback (30 minutes)

1. **Document incident**:
   ```markdown
   # Rollback Log Entry
   **Date**: 2026-02-08 02:30 AM
   **Severity**: HIGH
   **Problem**: Feature X caused crashes when processing large files
   **Commits Reverted**: abc1234, def5678
   **Rollback Time**: 15 minutes
   **Data Loss**: None
   **Root Cause**: Memory leak in new parser
   ```

2. **Create fix task**:
   - [ ] Add to TASKS.md with HIGH priority
   - [ ] Write failing test to reproduce bug
   - [ ] Fix properly in development
   - [ ] Test thoroughly before redeploying

3. **Communication**:
   - [ ] Update README.md if feature was announced
   - [ ] Note in CHANGELOG.md

---

## 💾 Data Rollback Procedures

### Config Files

**Backup Location**: `backups/config/`

```bash
# Automatic backup before changes
cp config/settings.json backups/config/settings-$(date +%Y%m%d-%H%M).json

# Restore from backup
cp backups/config/settings-20260208-1430.json config/settings.json
```

### User Data

**Backup Location**: User's responsibility (application doesn't store critical data)

**Clarify Data Files**:
- Recent files list: `~/.config/clarify/recent_files.json`
- Settings: `~/.config/clarify/settings.json`
- History: `~/.config/clarify/history.json`

```bash
# Backup user config
cp ~/.config/clarify/*.json ~/clarify-backup-$(date +%Y%m%d)/

# Restore user config
cp ~/clarify-backup-20260208/*.json ~/.config/clarify/
```

### Database Rollback

**Status**: N/A - Clarify uses no database

---

## 🧪 Rollback Testing Checklist

**Test rollback procedure quarterly** to ensure it works:

- [ ] Create test branch with intentional bug
- [ ] Deploy to test environment
- [ ] Practice emergency rollback (time it)
- [ ] Verify all steps work
- [ ] Document any issues found
- [ ] Update this document if needed

**Last Tested**: _________  
**Time Taken**: _________  
**Issues Found**: _________  

---

## 📊 Rollback History

| Date | Version | Reason | Method | Time | Data Loss | Status |
|------|---------|--------|--------|------|-----------|--------|
| 2026-02-08 | v1.0.0 | Template creation | N/A | N/A | None | ✅ Template |
| | | | | | | |

---

## 🎯 Known Safe Commits

**Stable Release Points** (safe to rollback to):

| Commit Hash | Version | Date | Notes |
|-------------|---------|------|-------|
| 0da9bbd | v1.0.0 | 2026-02-08 | Phase 1 fixes complete, tests passing |
| 0817f0b | v0.9.9 | 2026-02-06 | Logger fixes, stable |
| e9da6df | v0.9.8 | 2026-02-05 | COM3 merge, comprehensive tests |

**Update this table** after each successful deploy.

---

## ⚠️ Rollback Risks

### Low Risk Rollback
- Last 1-2 commits
- No database schema changes
- No config format changes
- Time: <10 minutes

### Medium Risk Rollback
- Last week of commits
- Config format changed
- Dependencies updated
- Time: 10-30 minutes
- Risk: May need manual config migration

### High Risk Rollback
- Multiple weeks/months
- Major refactoring
- Breaking changes deployed
- Time: 1-4 hours
- Risk: May require data migration, config rewrite

**Recommendation**: Don't rollback more than 1 week unless absolutely necessary.

---

## 📞 Emergency Contacts

**Solo Developer**: Josue  
**Response Time**: Best effort (solo project)  
**Backup Plan**: Community GitHub issues  

**When to Ask for Help**:
- Rollback doesn't work
- Data corruption suspected
- Security breach
- Uncertain about procedure

---

## 🔐 Rollback Authorization

**Who can rollback?**: Solo developer (you)  
**Approval needed?**: No (emergency procedure)  
**Documentation?**: YES - log all rollbacks in this file  

---

## 💡 Lessons Learned

Document rollback experiences here:

### Rollback #1: _________
**Date**: _________  
**Reason**: _________  
**What went wrong**: _________  
**What went right**: _________  
**Changes to procedure**: _________  

---

## 📚 Related Documents

- **TASKS.md**: Track rollback-related fixes
- **CHANGELOG.md**: Document version history
- **OWASP-checklist.md**: Security review before redeploying
- **Investigation Reports**: Root cause analysis

---

## 🎯 Rollback Prevention

**Better than rollback: Don't need to rollback**

### Pre-Deploy Checklist
- [ ] All tests passing (pytest tests/)
- [ ] Manual smoke test completed
- [ ] OWASP checklist reviewed
- [ ] Git commit with clear message
- [ ] Tag stable versions (git tag v1.0.0)

### Deployment Best Practices
- [ ] Deploy in low-usage hours
- [ ] Monitor logs for 30 minutes post-deploy
- [ ] Have this rollback plan open during deploy
- [ ] Keep terminal window ready for quick rollback

---

**Document Status**: ✅ Active  
**Last Updated**: 2026-02-08  
**Next Review**: 2026-05-08 (3 months)  
**Protocol Compliance**: ✅ Step 12.5 SATISFIED  
