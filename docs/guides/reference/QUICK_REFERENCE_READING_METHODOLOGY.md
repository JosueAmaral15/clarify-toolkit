# QUICK REFERENCE: Documentation Reading Methodology
## Single-Page Summary

**Recommended Approach**: 6-Sprint Pragmatic Model  
**Total Time**: 12-15 hours for complete understanding  
**Key Principle**: 80% knowledge (practical) > 100% memorization (impossible)

---

## 🎯 The 6 Pragmatic Sprints

### Sprint 1: CRITICAL (2-3h) 🔴
**What to read**: Architecture, project overview, core guides  
**Goal**: Understand what Clarify does and how it's organized  
**Success**: Can explain project to someone in 3 sentences  

**Files**:
- README.md
- docs/PROJECT_SUMMARY.md
- docs/architecture/ARCHITECTURE.md
- docs/guides/USER_MANUAL.md

---

### Sprint 2: HIGH (2-3h) 🟠
**What to read**: Design patterns, major features, analysis  
**Goal**: Understand architecture patterns and feature design  
**Success**: Can design new features following established patterns  

**Files**:
- docs/architecture/IMPORT_TREE_ANALOGY.md
- docs/specifications/FILE_EXPLORER_SPECIFICATION.md
- docs/guides/ (3-4 key guides)

---

### Sprint 3: MEDIUM (2-3h) 🟡
**What to read**: Features, internationalization, specific implementations  
**Goal**: Understand specific features deeply  
**Success**: Can work on features independently  

**Files**:
- docs/pt/ (feature documentation)
- docs/i18n/ (i18n implementation)

---

### Sprint 4: NORMAL (2h) 🟢
**What to read**: Integration, processes, migration  
**Goal**: Understand system integration and development processes  
**Success**: Know how components connect and work together  

**Files**:
- docs/plans/INTEGRATION_*.md
- docs/processes/

---

### Sprint 5: LOW (2h) 🔵
**What to read**: Planning, investigations, English docs  
**Goal**: Understand decisions and project history  
**Success**: Know why things are structured this way  

**Files**:
- Planning documents
- Investigation reports (completed issues)

---

### Sprint 6: OPTIONAL (1-2h) ⚪
**What to read**: Tutorials, archives, edge cases  
**Goal**: Know where to find specific information  
**Success**: Comfortable with documentation navigation  

**Files**:
- docs/tutorials/
- Edge case documentation

---

## ⏱️ Per-Session Ritual (Maximize Retention)

### Before Reading
- [ ] Clear workspace (no distractions)
- [ ] Fresh coffee/water
- [ ] Set timer (2-3h MAX)
- [ ] Set clear goal
- [ ] Fresh mental state

### During Reading
- [ ] Read priority order (numbered above)
- [ ] Note 3-5 key points per file
- [ ] Flag unclear sections
- [ ] 10min break every 60min
- [ ] Update progress tracker

### After Session
- [ ] Write 5-10 bullet summary
- [ ] List questions/clarifications
- [ ] Connect to previous learning
- [ ] Plan next session
- [ ] REST before next sprint

---

## 📚 Reading Strategy by File Type

| File Type | Strategy | Time |
|-----------|----------|------|
| **Architecture** | Read in full (100%) | 60-90min |
| **Recent Specs** (v2.9.100+) | Read in full (100%) | 5-10min each |
| **Older Specs** | Scan sections (30-50%) | 2-5min each |
| **Feature Docs** | Read if working on it (100%), else scan headers | 2-5min |
| **Process Docs** | Read related to task, skim others | 5-10min |
| **Reference Cards** | Scan headers, bookmark for later | 2-3min |
| **Historical Reports** | Scan for lessons learned | 2-5min |

---

## 🎓 Key Principles

1. **Pareto Principle**: 20% deep reading = 80% knowledge
   - Don't aim for 100% memorization
   - Focus on "know where to find" not "remember everything"

2. **Mental Model Over Memorization**
   - Understand relationships between components
   - Navigation matters more than memorization
   - Use grep to search when needed

3. **Session-Based Structure**
   - 2-3h sprints maximum
   - Protects focus and sleep
   - Prevents burnout

4. **Quality Checkpoints**
   - 5min validation after each sprint
   - Catch misunderstandings early
   - Prevents wasted time

5. **Pragmatism Over Perfectionism**
   - 80% done fast > 100% perfect never
   - Start with critical, expand as needed
   - Can come back for details later

---

## 📊 Expected Time Breakdown

| Sprint | Priority | Time | Content |
|--------|----------|------|---------|
| 1 | CRITICAL | 2-3h | Foundation |
| 2 | HIGH | 2-3h | Architecture |
| 3 | MEDIUM | 2-3h | Features |
| 4 | NORMAL | 2h | Integration |
| 5 | LOW | 2h | History |
| 6 | OPTIONAL | 1-2h | Deep dives |
| **TOTAL** | — | **12-15h** | **Complete understanding** |

---

## ✅ Success Metrics

- [ ] Can explain project purpose in 30 seconds
- [ ] Understand Import Tree Analogy (Root/Branches/Leaves)
- [ ] Know 10 core features and their docks
- [ ] Can navigate documentation using grep
- [ ] Know where to find specific information
- [ ] Understand project architecture
- [ ] Can start development work independently

---

## 🚀 Minimum Viable Path (If Time-Constrained)

**Just Sprints 1-3**: 6-9 hours  
**Gives**: 80% knowledge needed for development

1. ✅ Sprint 1 (2-3h) - Foundation
2. ✅ Sprint 2 (2-3h) - Architecture  
3. ✅ Sprint 3 (2-3h) - Features

Then expand to Sprints 4-6 as needed.

---

## 📌 Quick Bookmark Reference

**Most Important Files**:
```
docs/architecture/ARCHITECTURE.md        - System design
docs/protocolos/SIMPLICITY_PROTOCOL_3.md - Development process
docs/INDEX.md                             - Documentation map
docs/pt/                                  - Feature documentation
```

---

## 🔍 Quick Search Commands

```bash
# Find docs by keyword
grep -r "keyword" docs/ --include="*.md" -l

# Find by pattern (recent versions)
find docs/specifications/ -name "*v2.9.[1-9][0-9][0-9]*"

# Count files by category
find docs/pt -name "*.md" | wc -l

# View documentation index
cat docs/INDEX.md
```

---

## 💡 Pro Tips

1. **Don't read linearly** - Follow priority order
2. **Skim aggressively** - Not all docs need deep reading
3. **Use grep to search** - Don't manually browse all files
4. **Take breaks** - 107k lines is a marathon
5. **Connect concepts** - Link findings to architecture
6. **Question everything** - List unclear points for later
7. **Draw diagrams** - Visualize complex parts
8. **Review notes next day** - Reinforces learning
9. **Progressive depth** - Skim first, deep dive second
10. **Time-box strictly** - Never exceed 3h per sprint

---

## ⚠️ Common Mistakes to Avoid

| Mistake | Why Bad | Solution |
|---------|---------|----------|
| Reading sequentially | Wastes time on optional content | Use priority order |
| Trying to memorize all | Impossible and unnecessary | Focus on navigation |
| Marathon sessions (8h+) | Burnout, poor retention | Do 2-3h sprints |
| No quality checks | Misunderstandings accumulate | Validate after each sprint |
| Ignoring Import Tree Analogy | Architecture stays unclear | Study this concept early |
| Not using grep | Manual browsing is slow | Learn grep searching |
| Not taking breaks | Fatigue reduces comprehension | 10min per 60min reading |
| Ignoring unclear sections | Compounds misunderstanding | Flag and return later |

---

## 📞 If You Get Stuck

**Questions to ask**:
- Can I explain this to someone else? (No? → Re-read)
- How does this relate to architecture? (Unclear? → Review Import Tree)
- Is this critical or optional? (Optional? → Mark for later)
- Can I find this info quickly later? (No? → Bookmark now)

**Resources**:
- `docs/INDEX.md` - Documentation index
- `grep -r "term"` - Search across all docs
- Previous programmer notes - Learn from their experience
- Protocol checklist - Review best practices

---

## 🏁 Final Goal

**You are ready when**:
✅ Can design new features  
✅ Understand system architecture  
✅ Know where to find information  
✅ Can debug issues independently  
✅ Comfortable modifying code  

**This typically takes**: 9-15 hours with pragmatic approach  
**Actual benchmark**: Programmer #4 achieved it in **9h 15min** (62% faster than estimate!)

---

**Version**: 1.0  
**Based on**: Analysis of 4 ACTION_PLAN files + 9 other documentation files  
**Validated by**: 6 programmers' actual reading experiences  
**Status**: Ready to use

**Next Step**: Pick Sprint 1 and start reading!
