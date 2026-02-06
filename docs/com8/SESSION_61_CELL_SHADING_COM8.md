# Session 61: Cell Shading (Background Colors) - COM8

**Date**: 2026-01-30  
**Duration**: 75 minutes  
**Format Progress**: 38/62 (61.3%) → +1 shading format  
**Test Results**: 5/5 tests passing (100%)

---

## 📋 Session Objectives

Implement extraction and reconstruction of table cell background colors (shading) for both DOCX and ODT formats to preserve visual formatting when translating tables.

---

## 🎯 Implementation Summary

### What Was Added

#### 1. DOCX Shading Extraction
- Access cell's `tcPr` (table cell properties) element
- Find `w:shd` (shading) child element  
- Extract `w:fill` attribute containing hex color (e.g., `FF0000`)
- Store in `CellData.background_color` field

**Location**: `src/translation/format_mapper.py`, lines ~430-440

```python
# Extract cell-level formatting (Session 61)
from docx.oxml.ns import qn
tc = cell._element
tcPr = tc.tcPr
if tcPr is not None:
    shd = tcPr.find(qn('w:shd'))
    if shd is not None:
        fill = shd.get(qn('w:fill'))
        if fill and fill != 'auto':
            cell_data.background_color = fill
```

#### 2. ODT Shading Extraction
- Get cell's `stylename` attribute
- Look up style in styles dictionary
- Extract `TableCellProperties` element
- Read `background-color` attribute (format: `#RRGGBB`)
- Strip `#` and store hex color

**Location**: `src/translation/format_mapper.py`, lines ~547-565

```python
# Extract cell-level formatting (Session 61)
try:
    cell_style_name = cell.getAttribute('stylename')
    if cell_style_name and cell_style_name in styles:
        cell_style = styles[cell_style_name]
        cell_props = cell_style.getElementsByType(odf_style.TableCellProperties)
        
        if cell_props:
            props = cell_props[0]
            if hasattr(props, 'attributes'):
                for (ns, name), value in props.attributes.items():
                    if name == 'background-color':
                        if value and value != 'transparent':
                            cell_data.background_color = value.replace('#', '')
except (ValueError, KeyError):
    pass
```

#### 3. DOCX Shading Reconstruction
- Check if `CellData` has `background_color` set
- Create `w:shd` XML element using `OxmlElement`
- Set `w:fill` attribute to hex color
- Append to cell's `tcPr` (table cell properties)

**Location**: `src/translation/format_mapper.py`, lines ~1465-1475

```python
# Apply cell-level formatting (Session 61)
if cell_data.background_color:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    
    tcPr = docx_cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), cell_data.background_color)
    tcPr.append(shd)
```

#### 4. ODT Shading Reconstruction
- Check if `CellData` has `background_color` set
- Create unique cell style (family="table-cell")
- Add `TableCellProperties` with `backgroundcolor` attribute (format: `#RRGGBB`)
- Add style to document's automatic styles
- Apply style to cell via `stylename` attribute

**Location**: `src/translation/format_mapper.py`, lines ~1956-1965

```python
# Apply cell-level formatting (Session 61)
if cell_data.background_color:
    cell_style = odf_style.Style(name=f"cell_{row_idx}_{col_idx}", family="table-cell")
    cell_props = odf_style.TableCellProperties()
    cell_props.setAttribute("backgroundcolor", f"#{cell_data.background_color}")
    cell_style.addElement(cell_props)
    doc.automaticstyles.addElement(cell_style)
    odt_cell.setAttribute("stylename", cell_style)
```

---

## 🧪 Testing

### Test Suite: `test_cell_shading_session61.py`

**5 comprehensive tests, all passing:**

#### Test 1: DOCX Shading Extraction ✅
- Created 2×2 table with 3 colored cells (red, blue, green)
- Verified extraction of all background colors
- Confirmed `None` for unshaded cell

#### Test 2: ODT Shading Extraction ✅
- Created ODT table with cell styles containing background colors
- Verified extraction matches DOCX behavior
- Handles `#RRGGBB` format correctly

#### Test 3: DOCX Shading Reconstruction ✅
- Built `TableSegment` with shaded cells
- Reconstructed to DOCX format
- Verified shading applied via XML inspection

#### Test 4: ODT Shading Reconstruction ✅
- Built `TableSegment` with shaded cells
- Reconstructed to ODT format
- Verified cell styles created with correct background colors

#### Test 5: Round-Trip Shading Preservation ✅
- **Critical test**: Full pipeline validation
- Original DOCX → Extract → Reconstruct → Verify
- Used 3 different colors (yellow, magenta, cyan)
- Confirmed 100% fidelity: All colors perfectly preserved

**Test Output Summary**:
```
Total: 5/5 tests passed
🎉 ALL TESTS PASSED! Cell shading implementation complete.
```

---

## 🐛 Issues Encountered & Resolutions

### Issue 1: Missing Import in ODT Reconstruction
**Problem**: `NameError: name 'odf_style' is not defined` in `_reconstruct_table_to_odt()`

**Cause**: Needed to import `odf.style` module to access `TableCellProperties`

**Solution**: Added imports to method header:
```python
from odf.style import Style, TextProperties, TableCellProperties
from odf import style as odf_style
```

### Issue 2: Test Loading ODT File Incorrectly
**Problem**: `TypeError: OpenDocumentText() takes 0 positional arguments but 1 was given`

**Cause**: `OpenDocumentText()` constructor doesn't accept file path directly

**Solution**: Use `load()` function from `odf.opendocument`:
```python
from odf.opendocument import load
doc = load(temp_path)
```

---

## 📊 Technical Details

### Color Format Differences
- **DOCX**: Hex RGB without `#` (e.g., `FF0000` for red)
- **ODT**: Hex RGB with `#` prefix (e.g., `#FF0000`)
- **Solution**: Normalize to DOCX format internally, add `#` when writing ODT

### Architecture Decision: Unique Cell Styles in ODT
Unlike text formatting (which uses style caching), each cell with background color gets unique style. This is because:
1. Cell-level properties less common than text formatting
2. Simpler implementation (no cache key management)
3. Minimal performance impact (typical tables have <100 cells)

Future optimization possible if tables with many identically-shaded cells become common.

### XML Structure (DOCX)
```xml
<w:tc>
  <w:tcPr>
    <w:shd w:fill="FF0000"/>  <!-- Red background -->
  </w:tcPr>
  <w:p>...</w:p>
</w:tc>
```

### ODT Structure
```xml
<table:table-cell table:style-name="cell_0_0">
  <text:p>...</text:p>
</table:table-cell>

<style:style style:name="cell_0_0" style:family="table-cell">
  <style:table-cell-properties fo:background-color="#FF0000"/>
</style:style>
```

---

## 📈 Progress Update

### Format Count: 38/62 (61.3%)

**New this session:**
- ✅ Cell background color (shading) - both DOCX and ODT

**Cumulative table support:**
- ✅ Table structure (rows, columns) - Session 56
- ✅ Character formatting in cells (12 formats) - Sessions 57-58
- ✅ Multi-paragraph cells - Sessions 57-58
- ✅ Cell background color - **Session 61**

**Remaining table features:**
- 🔲 Cell borders (top, bottom, left, right) - Planned Session 62
- 🔲 Cell merging (colspan, rowspan) - Planned Session 63

---

## ✅ Validation Checklist

- [x] DOCX shading extraction works
- [x] ODT shading extraction works
- [x] DOCX shading reconstruction works
- [x] ODT shading reconstruction works
- [x] Round-trip preservation verified
- [x] All 5 tests passing
- [x] No regression in previous tests (Sessions 56-60)
- [x] Code follows existing patterns
- [x] Minimal changes (surgical additions only)

---

## 📝 Next Steps

### Session 62: Cell Borders (Estimated 90 minutes)
**Goal**: Extract and reconstruct cell borders for all 4 sides

**Scope**:
1. DOCX: Extract `w:tcBorders` element (top, bottom, left, right)
2. ODT: Extract border attributes from `TableCellProperties`
3. Store in `CellData.borders` dictionary: `{"top": "...", "left": "..."}`
4. DOCX reconstruction: Create `w:tcBorders` with child elements
5. ODT reconstruction: Set border attributes in cell style
6. Test suite: Border combinations, round-trip validation

**Complexity**:
- Borders more complex than shading (4 sides vs 1 color)
- Each border has style (solid/dashed/dotted), width, and color
- May simplify to preserve only "border present" vs detailed attributes

**Format count after Session 62**: 39/62 (62.9%)

### Session 63: Cell Merging (Estimated 90 minutes)
**Goal**: Handle merged cells (colspan/rowspan)

**Scope**:
1. DOCX: Detect merged cells via `vMerge` and `hMerge` attributes
2. ODT: Detect via `table:number-columns-spanned` and `table:number-rows-spanned`
3. Store in `CellData.row_span` and `col_span` fields
4. Reconstruction: Apply merge attributes to cells
5. Handle ghost cells (cells hidden by merge)
6. Test suite: Various merge patterns, round-trip

**Format count after Session 63**: 40/62 (64.5%)

### After Session 63: Integration
Once core table formatting complete (structure, text, shading, borders, merging), integrate into Google Translate workflow:
- Implement `{TABLE_N}` placeholder system
- Keep tables out of translation API
- Translate only text content within cells
- Reconstruct tables with translated text

---

## 🎓 Key Learnings

### 1. ODF API Has Quirks
- Constructor behavior different from docx (no file path in constructor)
- Must use `load()` function to open existing files
- Attribute names differ from XML attributes (e.g., `backgroundcolor` vs `background-color`)

### 2. XML Manipulation in python-docx
- `get_or_add_tcPr()` convenient method for cell properties
- `OxmlElement()` for creating new XML elements
- `qn()` (qualified name) required for namespace prefixes

### 3. Testing Strategy Pays Off
- Round-trip tests catch subtle issues
- Multiple color tests reveal edge cases (transparency, `auto` values)
- Clear test output accelerates debugging

### 4. Incremental Feature Addition
- Starting with simpler feature (shading) before complex one (borders) was correct choice
- Builds confidence and establishes patterns
- Allows early validation of architecture decisions

---

## 📊 Session Statistics

- **Implementation time**: ~45 minutes
- **Testing/debugging time**: ~20 minutes
- **Documentation time**: ~10 minutes
- **Lines added**: ~60 lines across 3 files
- **Tests created**: 5 comprehensive tests
- **Bugs fixed**: 2 (import, test loading)
- **Format coverage increase**: +1.6% (59.7% → 61.3%)

---

## 🔗 Related Sessions

- **Session 56**: Table architecture (TableSegment, CellData)
- **Session 57**: DOCX cell formatting extraction
- **Session 58**: ODT cell formatting extraction
- **Session 59**: DOCX table reconstruction
- **Session 60**: ODT table reconstruction
- **Session 62**: Cell borders (next)
- **Session 63**: Cell merging (after borders)

---

## ✨ Success Metrics

✅ **Implementation**: 100% complete (all 4 operations working)  
✅ **Testing**: 5/5 tests passing (100% pass rate)  
✅ **Round-trip fidelity**: 100% (colors preserved exactly)  
✅ **Code quality**: Clean, follows existing patterns  
✅ **Documentation**: Comprehensive session notes created  

**Session 61: COMPLETE ✅**

---

**Next session**: Session 62 - Cell Borders  
**Estimated time**: 90 minutes  
**Format target**: 39/62 (62.9%)
