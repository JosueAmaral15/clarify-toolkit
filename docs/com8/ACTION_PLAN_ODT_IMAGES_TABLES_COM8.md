# ODT Image and Table Support - Action Plan (COM8)

**Date:** 2026-02-17  
**Programmer:** COM8  
**Request:** Add image and table preservation to ODT translation (like DOCX)

---

## Current Status

### DOCX Translation:
- ✅ **Images:** Preserved via `ImageManager` (docx_html_mapper.py)
- ✅ **Tables:** Preserved via `TableManager` (docx_html_mapper.py)
- ✅ **Implementation:** Session Phase 3 (Feb 16, 2026)

### ODT Translation:
- ❌ **Images:** NOT implemented
- ❌ **Tables:** NOT implemented  
- ⚠️ **Current:** Only text formatting (CSS) preserved

---

## Technical Analysis

### Architecture Comparison:

**DOCX Flow (with images/tables):**
```
DOCX file
  ↓
extract_html_from_docx()
  ├─ HTML content (with markers)
  ├─ CSSClassManager (formatting)
  ├─ ImageManager (images)
  └─ TableManager (tables)
  ↓
Google Translate (preserves HTML markers)
  ↓
create_docx_from_html()
  ├─ Reads CSS classes
  ├─ Restores images from ImageManager
  └─ Restores tables from TableManager
  ↓
Translated DOCX (with images/tables)
```

**ODT Flow (current - text only):**
```
ODT file
  ↓
HTMLFormatMapper.extract_html_from_odt()
  ├─ HTML content
  └─ CSSClassManager (formatting only)
  ↓
Google Translate (preserves HTML)
  ↓
HTMLFormatMapper._save_as_odt()
  └─ Reads CSS classes
  ↓
Translated ODT (text formatting only, NO images/tables)
```

---

## Required Implementation

### Goal: Add ImageManager and TableManager to ODT

**New ODT Flow (proposed):**
```
ODT file
  ↓
extract_html_from_odt() [ENHANCED]
  ├─ HTML content (with markers)
  ├─ CSSClassManager (formatting)
  ├─ ImageManager (images) ← NEW
  └─ TableManager (tables) ← NEW
  ↓
Google Translate (preserves HTML markers)
  ↓
_save_as_odt() [ENHANCED]
  ├─ Reads CSS classes
  ├─ Restores images from ImageManager ← NEW
  └─ Restores tables from TableManager ← NEW
  ↓
Translated ODT (with images/tables)
```

---

## Implementation Plan

### Phase 1: Research & Design (1-2 hours)

**Tasks:**
1. Study ODF library capabilities
   - `odf.draw` for images
   - `odf.table` for tables
2. Analyze DOCX ImageManager implementation
3. Analyze DOCX TableManager implementation
4. Design ODT equivalents
5. Create design document

**Questions to answer:**
- How does ODF store images? (embedded binary vs external?)
- How does ODF represent tables? (similar to HTML?)
- Can we reuse DOCX managers or need ODT-specific versions?
- What image formats does ODF support? (PNG, JPEG, SVG?)

---

### Phase 2: ImageManager for ODT (3-4 hours)

**Tasks:**
1. Create `ODTImageManager` class
2. Extract images from ODT during HTML extraction
3. Store images with unique IDs
4. Insert image markers in HTML (`<span data-image="IMG001">`)
5. Restore images during ODT creation
6. Test with sample ODT containing images

**Code locations:**
- Modify: `src/translation/html_format_mapper.py`
- Methods to enhance:
  - `extract_html_from_odt()` - add image extraction
  - `_save_as_odt()` - add image restoration

**Challenges:**
- ODF image format different from DOCX
- Image anchoring (inline vs positioned)
- Image size preservation

---

### Phase 3: TableManager for ODT (3-4 hours)

**Tasks:**
1. Create `ODTTableManager` class
2. Extract table structure from ODT
3. Store tables with unique IDs
4. Insert table markers in HTML (`<table data-table="TBL001">`)
5. Restore tables during ODT creation
6. Test with sample ODT containing tables

**Code locations:**
- Modify: `src/translation/html_format_mapper.py`
- Methods to enhance:
  - `extract_html_from_odt()` - add table extraction
  - `_save_as_odt()` - add table restoration

**Challenges:**
- ODF table format different from DOCX
- Cell formatting preservation
- Nested tables
- Table-in-table scenarios

---

### Phase 4: Integration & Testing (2-3 hours)

**Tasks:**
1. Update `google_translate_dock.py` ODT loading
   - Store `image_manager` and `table_manager`
2. Update GUI to pass managers to translation worker
3. Test with complex ODT files:
   - Images only
   - Tables only
   - Images + tables
   - Large files (with pagination)
4. Verify translation quality

**Test files needed:**
- ODT with inline images
- ODT with tables (simple + complex)
- ODT with both images and tables
- Large ODT (> 4.5KB) to test pagination

---

### Phase 5: Documentation (1 hour)

**Tasks:**
1. Create implementation summary
2. Update comparison table (DOCX vs ODT features)
3. Document limitations (if any)
4. Create user-facing documentation

---

## Estimated Time

| Phase | Time | Complexity |
|-------|------|------------|
| Phase 1: Research & Design | 1-2 hours | Medium |
| Phase 2: ImageManager | 3-4 hours | High |
| Phase 3: TableManager | 3-4 hours | High |
| Phase 4: Integration & Testing | 2-3 hours | Medium |
| Phase 5: Documentation | 1 hour | Low |
| **TOTAL** | **10-14 hours** | **High** |

---

## Technical Considerations

### ODF Library Capabilities:

```python
from odf import draw, table
from odf.draw import Frame, Image
from odf.table import Table, TableRow, TableCell
```

**Image Handling:**
- ODF stores images in `Pictures/` folder inside ODT zip
- Image references via `xlink:href="Pictures/image1.png"`
- Need to extract binary data and reconstruct

**Table Handling:**
- ODF tables similar to HTML tables
- Structure: `<table:table>` → `<table:table-row>` → `<table:table-cell>`
- Cell formatting via styles
- Need to preserve merged cells

---

## Risks & Challenges

### High Risk:
1. **ODF complexity:** ODF format is XML-based but complex
2. **Binary data:** Image extraction/restoration tricky
3. **Table translation:** Cells contain translatable text
4. **Time investment:** 10-14 hours is significant

### Medium Risk:
1. **Backward compatibility:** Don't break existing ODT translation
2. **Memory usage:** Large images may increase memory
3. **Performance:** Image/table processing adds overhead

### Low Risk:
1. **Testing:** Can reuse DOCX test strategy
2. **Documentation:** Similar to DOCX docs

---

## Alternative Approaches

### Option A: Full Implementation (Recommended)
- Implement both ImageManager and TableManager
- Feature parity with DOCX
- **Time:** 10-14 hours
- **Benefit:** Complete ODT translation support

### Option B: Tables Only (Faster)
- Implement TableManager only
- Skip images for now
- **Time:** 5-7 hours
- **Benefit:** Tables are more common than images

### Option C: Images Only (Simpler)
- Implement ImageManager only
- Skip tables for now
- **Time:** 5-6 hours
- **Benefit:** Images easier than tables

### Option D: Defer Implementation
- Keep ODT text-only for now
- Wait for user feedback
- **Time:** 0 hours
- **Benefit:** Focus on other features

---

## Recommendation

### Suggested Path: **Option A (Full Implementation)**

**Reasoning:**
1. Users expect feature parity between DOCX and ODT
2. DOCX implementation provides proven pattern to follow
3. Better to complete now than have partial implementation
4. Time investment (10-14 hours) is reasonable for feature completeness

**Prerequisites:**
- User confirmation to proceed
- Clarification on priority (urgent vs can wait)
- Sample ODT files with images/tables for testing

---

## Questions for User

Before proceeding, please clarify:

1. **Priority:** Is this urgent or can it wait?
2. **Scope:** Do you want both images AND tables, or one first?
3. **Test files:** Do you have ODT files with images/tables I can test with?
4. **Approach:** Which option (A/B/C/D) do you prefer?

---

**Status:** ⏸️ AWAITING USER INPUT  
**Next Step:** User decides on approach and priority  
**Estimated Time:** 10-14 hours (Option A) or 5-7 hours (Option B/C)
