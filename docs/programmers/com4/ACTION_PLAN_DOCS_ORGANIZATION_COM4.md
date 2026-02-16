# Action Plan: Documentation Organization (COM4)

**Date**: 2026-02-16  
**Programmer**: COM4  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5  
**Session**: 8 (Documentation Organization)  

---

## Executive Summary

### Current State
- **774 total markdown files** across docs/ directory
- **160 files in root** (unorganized, should be categorized)
- **36 subdirectories** (some redundant/overlapping)
- **9 .txt files** and **2 .odt files** in root
- Largest subdirs: reports/ (122), com8/ (93), sprints/ (72), action-plans/ (55)

### Problem Analysis
1. **Root clutter**: 160+ files with no clear structure
2. **Redundant directories**: protocols/protocolos, reports/sessions, pt/en
3. **Mixed content**: Action plans, summaries, reports, guides all mixed
4. **No index**: No docs/README.md to navigate
5. **Programmer-specific content**: COM2, COM8 docs mixed with general docs
6. **Inconsistent naming**: UPPERCASE vs lowercase, underscores vs hyphens

### Goal
Organize 160 root-level files into logical structure:
- Category-based organization (by content type)
- Programmer-specific content in dedicated folders
- Create navigation index (docs/README.md)
- Consolidate redundant directories
- Establish clear documentation standards

### Time Estimate
**Total**: 3-4 hours (240 minutes)
- Phase 1: Analysis & Planning (30 min)
- Phase 2: Programmer-Specific Content (45 min)
- Phase 3: Action Plans & Reports (40 min)
- Phase 4: Session/Phase Summaries (40 min)
- Phase 5: Architecture & Specifications (30 min)
- Phase 6: Protocol & Guidelines (25 min)
- Phase 7: Cleanup & Index Creation (30 min)
- Phase 8: Validation & Documentation (20 min)

---

## Phase 1: Analysis & Planning (30 min)

### Objectives
- Analyze all 160 root files by category
- Define final directory structure
- Identify redundant directories to consolidate
- Create categorization rules

### Tasks
1. **Categorize root files** (15 min)
   - Run analysis script to classify files by type
   - Count files per category
   - Identify outliers and edge cases

2. **Design target structure** (10 min)
   - Define category directories
   - Decide on consolidation strategy
   - Document naming conventions

3. **Create backup** (5 min)
   - Git tag: `backup-before-docs-org-phase1`
   - Verify clean working tree

### Expected Categories
Based on initial analysis:
- **action-plans/** (10 files from root + existing 55)
- **sessions/** (41 files from root + existing 29)
- **programmers/com8/** (6 files from root + existing 93)
- **programmers/com2/** (minimal - existing 1)
- **protocols/** (9 files from root + consolidate protocolos/)
- **architecture/** (architecture + design files)
- **reports/** (keep existing 122, add summaries)
- **guides/** (tutorials, reference docs)
- **study/** (reading logs, comprehension docs)

### Success Criteria
- ✅ All 160 files categorized
- ✅ Target directory structure defined
- ✅ Migration strategy documented
- ✅ Git backup created

---

## Phase 2: Programmer-Specific Content (45 min)

### Objectives
Organize content created by specific programmers (COM2, COM8, etc.)

### Tasks

#### 2.1: Create programmers/ structure (5 min)
```bash
mkdir -p docs/programmers/com2
mkdir -p docs/programmers/com3
mkdir -p docs/programmers/com4
mkdir -p docs/programmers/com8
```

#### 2.2: Move COM8 content (20 min)
**From root** (6 files):
- CLARIFY_COM8_*.md → docs/programmers/com8/
- DOCX_FORMATTING_FEATURE_GUIDE_COM8.md → docs/programmers/com8/
- COORDINATION_SETUP_COM8.md → docs/programmers/com8/
- *_COM8.* files → docs/programmers/com8/

**Consolidate existing**:
- docs/com8/ → docs/programmers/com8/ (93 files)
- Keep internal structure

**Total**: ~100 files organized

#### 2.3: Move COM2 content (5 min)
- docs/COM2/ → docs/programmers/com2/
- PROGRAMMER_3_QUICK_REFERENCE.md → docs/programmers/com2/

#### 2.4: Create COM4 folder (10 min)
Move COM4-created cleanup documentation:
- ACTION_PLAN_CODE_CLEANUP_COM4.md (from root)
- SESSION_5_SKIP_NOTE_COM4.md (from root)
- COM3_MERGE_SUMMARY_COM4.md (from root)
- TODO_AUDIT_SUMMARY_COM4.md (from root)
- This action plan → docs/programmers/com4/

#### 2.5: Create COM3 placeholder (5 min)
- Create docs/programmers/com3/README.md
- Note: COM3 work was merged, no separate docs yet

### Success Criteria
- ✅ All programmer-specific content organized
- ✅ docs/programmers/ structure created
- ✅ ~100+ files moved
- ✅ Each programmer has dedicated folder

### Git Commit
```
refactor(docs): Organize programmer-specific documentation (Phase 2)

- Created docs/programmers/ structure for COM2/COM3/COM4/COM8
- Moved 100+ programmer-specific files from root and subdirs
- Consolidated docs/com8/ → docs/programmers/com8/
- Consolidated docs/COM2/ → docs/programmers/com2/
- Created docs/programmers/com4/ for cleanup docs

Session: COM4-Session8-Phase2
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 3: Action Plans & Reports (40 min)

### Objectives
Consolidate action plans, reports, and progress tracking documents

### Tasks

#### 3.1: Consolidate action-plans/ (15 min)
**From root** (10 files):
- ACTION_PLAN_*.md → docs/action-plans/
- Keep existing 55 files in docs/action-plans/

**Organize by type**:
```
docs/action-plans/
├── reading/           (documentation reading plans)
├── development/       (feature development plans)
├── cleanup/          (code cleanup plans)
└── investigation/    (bug investigation plans)
```

**Total**: 65+ action plans organized

#### 3.2: Consolidate reports/ (15 min)
**Keep existing structure** (122 files in docs/reports/)

**Add from root**:
- *_REPORT*.md files
- *_SUMMARY*.txt files
- ANALYSIS_*.txt files

**Clean up by date**:
- Group by year/month if too many files
- Archive old reports (2025 and earlier)

#### 3.3: Organize sprints/ (10 min)
**Keep existing** (72 files in docs/sprints/)

**Add from root**:
- SPRINT*.md files
- Move sprint-specific reports here

### Success Criteria
- ✅ All action plans in docs/action-plans/
- ✅ All reports consolidated in docs/reports/
- ✅ Sprint docs in docs/sprints/
- ✅ ~80+ files moved from root

### Git Commit
```
refactor(docs): Consolidate action plans and reports (Phase 3)

- Moved 10 action plans from root to docs/action-plans/
- Organized action plans by type (reading/dev/cleanup/investigation)
- Consolidated reports into docs/reports/
- Organized sprint documentation in docs/sprints/

Session: COM4-Session8-Phase3
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 4: Session/Phase Summaries (40 min)

### Objectives
Organize all session, phase, and step documentation

### Tasks

#### 4.1: Consolidate sessions/ (20 min)
**From root** (41 files matching SESSION|PHASE|STEP):
- SESSION_*.md → docs/sessions/
- PHASE_*.md → docs/sessions/phases/
- STEP_*.md → docs/sessions/steps/

**Organize by programmer**:
```
docs/sessions/
├── phases/           (PHASE_1_SUMMARY.md, etc.)
├── steps/            (STEP_1_0_READING_LOG.md, etc.)
├── general/          (generic session docs)
└── README.md         (index of all sessions)
```

**Existing**: 29 files in docs/sessions/

#### 4.2: Create session index (10 min)
Create docs/sessions/README.md:
- List all phases (1-11)
- List all steps (organized by protocol)
- Link to programmer-specific sessions
- Timeline view

#### 4.3: Archive old study logs (10 min)
Large files like STEP_1_0_READING_LOG.md (514KB):
- Move to docs/sessions/archive/ or compress
- Keep index references
- Document archive location

### Success Criteria
- ✅ All session docs in docs/sessions/
- ✅ Clear phase/step organization
- ✅ Session index created
- ✅ Large files archived
- ✅ ~70+ files organized

### Git Commit
```
refactor(docs): Organize session and phase documentation (Phase 4)

- Moved 41 session/phase/step files from root to docs/sessions/
- Created phase/ and step/ subdirectories
- Built comprehensive session index (docs/sessions/README.md)
- Archived large study logs to sessions/archive/

Session: COM4-Session8-Phase4
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 5: Architecture & Specifications (30 min)

### Objectives
Organize technical architecture and specification documents

### Tasks

#### 5.1: Consolidate architecture docs (15 min)
**From root**:
- ARCHITECTURE_*.md → docs/architecture/
- GUI_ARCHITECTURE_*.md → docs/architecture/gui/
- *_ARCHITECTURE*.md → docs/architecture/

**Merge with existing**:
- docs/architecture/ (4 files existing)
- docs/design/ (1 file) → merge into architecture/

**Organize by component**:
```
docs/architecture/
├── gui/              (GUI architecture docs)
├── core/             (core system architecture)
├── translation/      (translation system)
└── README.md         (architecture overview)
```

#### 5.2: Consolidate specifications (15 min)
**From root**:
- *_SPECIFICATION*.md → docs/specifications/
- FILE_EXPLORER_SPECIFICATION.md → docs/specifications/

**Existing**: 29 files in docs/specifications/

**Organize by feature**:
```
docs/specifications/
├── file-explorer/    (file explorer specs)
├── translation/      (translation features)
├── text-extraction/  (extraction features)
└── README.md         (spec index)
```

### Success Criteria
- ✅ All architecture docs consolidated
- ✅ All specifications organized
- ✅ Component-based structure
- ✅ ~15+ files moved from root

### Git Commit
```
refactor(docs): Consolidate architecture and specifications (Phase 5)

- Moved architecture docs from root to docs/architecture/
- Organized by component (gui/core/translation)
- Consolidated specifications in docs/specifications/
- Merged docs/design/ into architecture/

Session: COM4-Session8-Phase5
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 6: Protocol & Guidelines (25 min)

### Objectives
Organize protocol documentation and project guidelines

### Tasks

#### 6.1: Consolidate protocol docs (15 min)
**From root** (9 files):
- PROTOCOL_*.md → docs/protocols/
- FRAGMENT_TEMP*.md → docs/protocols/fragments/

**Consolidate directories**:
- docs/protocolos/ (1 file) → merge into docs/protocols/
- Remove docs/protocolos/ directory

**Organize**:
```
docs/protocols/
├── simplicity/       (SIMPLICITY_PROTOCOL_3.md)
├── compliance/       (compliance reports)
├── fragments/        (FRAGMENT_TEMP*.md)
└── README.md         (protocol index)
```

#### 6.2: Organize guidelines (10 min)
**From root**:
- *_GUIDELINES*.md → docs/guides/
- *_GUIDE*.md → docs/guides/
- RECIPES.md → docs/guides/
- TOOLTIP_GUIDELINES.md → docs/guides/

**Existing**: 5 files in docs/guides/

**Add quick references**:
- *_QUICK_REFERENCE*.md → docs/guides/reference/

### Success Criteria
- ✅ All protocol docs in docs/protocols/
- ✅ protocolos/ directory removed (consolidated)
- ✅ Guidelines organized in docs/guides/
- ✅ ~20+ files moved from root

### Git Commit
```
refactor(docs): Organize protocols and guidelines (Phase 6)

- Moved 9 protocol files from root to docs/protocols/
- Consolidated docs/protocolos/ into docs/protocols/
- Organized guidelines and guides in docs/guides/
- Created protocol index for easy navigation

Session: COM4-Session8-Phase6
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 7: Cleanup & Index Creation (30 min)

### Objectives
Final cleanup, index creation, and documentation standards

### Tasks

#### 7.1: Move remaining root files (10 min)
**Categorize stragglers**:
- Translation docs → docs/features/translation/
- I18n docs → docs/i18n/
- Testing docs → docs/testing/
- Investigation docs → docs/investigations/
- PT documentation → docs/pt/ (keep as-is)

**Handle special files**:
- .odt files → move to docs/archive/ or tests/fixtures/
- .txt files → convert to .md or archive

#### 7.2: Create main index (15 min)
Create **docs/README.md**:
```markdown
# Clarify Documentation Index

## For Developers
- [Architecture](architecture/) - System design and components
- [Specifications](specifications/) - Feature specifications
- [Protocols](protocols/) - Development protocols (SIMPLICITY_PROTOCOL_3)
- [Guides](guides/) - Development guides and best practices

## For Contributors
- [Action Plans](action-plans/) - Planning documents
- [Sessions](sessions/) - Development session logs
- [Sprints](sprints/) - Sprint planning and reports
- [Programmers](programmers/) - Programmer-specific documentation

## By Programmer
- [COM2](programmers/com2/) - Programmer 2 documentation
- [COM3](programmers/com3/) - Programmer 3 documentation
- [COM4](programmers/com4/) - Programmer 4 documentation (cleanup specialist)
- [COM8](programmers/com8/) - Programmer 8 documentation

## Resources
- [Study Materials](study/) - Learning resources and comprehension docs
- [Analysis](analysis/) - Code and architecture analysis
- [Reports](reports/) - Progress and completion reports
- [Testing](testing/) - Testing documentation

## Quick Links
- [Project Structure](PROJECT_STRUCTURE.md)
- [Root Structure](ROOT_STRUCTURE.md)
- [Quick Reference](QUICK_REFERENCE.md)
```

#### 7.3: Document organization standards (5 min)
Create **docs/ORGANIZATION_STANDARDS.md**:
- File naming conventions
- Directory structure rules
- Where to put new documentation
- Programmer-specific content guidelines

### Success Criteria
- ✅ All root files categorized (0 remaining)
- ✅ Main index created (docs/README.md)
- ✅ Organization standards documented
- ✅ Clean root directory

### Git Commit
```
refactor(docs): Final cleanup and create main index (Phase 7)

- Moved remaining files from root to appropriate directories
- Created comprehensive docs/README.md navigation index
- Documented organization standards in ORGANIZATION_STANDARDS.md
- Cleaned root directory (0 loose files)

Session: COM4-Session8-Phase7
Protocol: SIMPLICITY_PROTOCOL_3
```

---

## Phase 8: Validation & Documentation (20 min)

### Objectives
Validate organization, test links, finalize documentation

### Tasks

#### 8.1: Validate structure (10 min)
- Verify 0 files in docs/ root (except README.md and INDEX.md)
- Check all programmers/ folders have content
- Verify no broken moves (files still accessible)
- Count files: should still be ~774 total

#### 8.2: Test navigation (5 min)
- Review docs/README.md
- Check links work
- Verify folder structure makes sense
- Get user feedback on organization

#### 8.3: Final documentation (5 min)
Update this action plan with:
- Actual time spent per phase
- Issues encountered
- Final file counts
- Lessons learned

### Success Criteria
- ✅ All 160 root files organized
- ✅ Navigation working
- ✅ No files lost
- ✅ Documentation complete

### Git Commit
```
docs: Complete documentation organization (Session 8 - COM4)

Organized 160+ root files into logical structure:
- Created docs/programmers/ for COM2/COM3/COM4/COM8
- Consolidated action plans, reports, sessions
- Organized by content type (architecture/specs/protocols)
- Created comprehensive navigation index
- Established organization standards

Impact:
- 160 files moved from root
- 36 directories organized
- Main index created (docs/README.md)
- Zero loose files in root

Session: COM4-Session8-Complete
Protocol: SIMPLICITY_PROTOCOL_3
Time: 240 minutes (4 hours)
Programmer: COM4
```

---

## Risk Assessment

### Low Risk ✅
- Moving markdown files (no code impact)
- Creating new directories
- Adding README files

### Medium Risk ⚠️
- Consolidating redundant directories
- Large file moves (git history)
- Breaking relative links in docs

### High Risk ❌
- None (documentation only)

### Mitigation Strategies
1. **Git backup tags** before each phase
2. **Incremental commits** (one per phase)
3. **Verification** after each move
4. **Keep relative links** when moving files
5. **Test navigation** after completion

---

## Rollback Procedures

### Per-Phase Rollback
```bash
# Find phase tag
git tag | grep backup-before-docs-org

# Rollback to specific phase
git reset --hard backup-before-docs-org-phase3
```

### Complete Rollback
```bash
# Rollback all organization work
git reset --hard backup-before-docs-org-20260216-XXXXXX

# Or use backup tag from Session 7
git reset --hard backup-before-docs-org-$(date +%Y%m%d)
```

### Selective Rollback
```bash
# Rollback specific directory
git checkout HEAD~3 -- docs/programmers/

# Restore specific file
git checkout HEAD~1 -- docs/README.md
```

---

## Success Metrics

### Quantitative
- ✅ 0 files in docs/ root (except README.md)
- ✅ ~160 files organized
- ✅ 36 directories structured
- ✅ 100% navigation coverage

### Qualitative
- ✅ Easy to find documentation
- ✅ Clear programmer ownership
- ✅ Logical category structure
- ✅ Scalable for future docs

---

## Notes

### "Protect Your Sleep" Philosophy
- **Each phase is independent** - can pause between phases
- **Git tags before each phase** - safe rollback points
- **Small commits** - easy to review and revert
- **Incremental progress** - don't need to finish all 8 phases today
- **Document as you go** - capture decisions and reasoning

### Future Improvements
- Archive old documentation (2025 and earlier)
- Automate organization with scripts
- Add CI check for loose root files
- Create documentation templates

---

## Estimated Timeline

```
Phase 1: Analysis & Planning          [    30 min] ⏳
Phase 2: Programmer-Specific Content  [    45 min] ⏳
Phase 3: Action Plans & Reports       [    40 min] ⏳
Phase 4: Session/Phase Summaries      [    40 min] ⏳
Phase 5: Architecture & Specs         [    30 min] ⏳
Phase 6: Protocol & Guidelines        [    25 min] ⏳
Phase 7: Cleanup & Index              [    30 min] ⏳
Phase 8: Validation & Docs            [    20 min] ⏳
                                      ─────────────
Total:                                   240 min (4h)
```

### Recommended Schedule
- **Today**: Phases 1-2 (75 min - programmer content)
- **Tomorrow**: Phases 3-4 (80 min - plans & sessions)
- **Day 3**: Phases 5-6 (55 min - architecture & protocols)
- **Day 4**: Phases 7-8 (50 min - cleanup & validation)

Or complete in one 4-hour session if preferred.

---

**Ready to proceed with Phase 1?**
- Option A: Yes, start Phase 1 analysis (30 min)
- Option B: Review and adjust plan first
- Option C: Schedule for later (save plan and exit)

**Programmer**: COM4  
**Status**: READY  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5
