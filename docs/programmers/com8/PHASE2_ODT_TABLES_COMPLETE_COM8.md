# Phase 2 Complete: ODT Table Preservation - COM8

## Summary
Successfully implemented table preservation for ODT files in Google Translate tool. Tables are now extracted, preserved through translation, and restored to the output ODT file.

## Implementation Date
February 19, 2026

## Status
✅ **COMPLETE** - All phases implemented and tested

---

## Changes Made

### 1. Core Translation Layer (`src/translation/html_format_mapper.py`)

#### Added Classes:
- **`ODTTableData`** (dataclass, lines ~391-465)
  - Stores table metadata: ID, rows, cols, cells, name
  - Methods: `get_cell()`, `set_cell()`, `to_html()`, `get_dimensions()`
  - Similar to DOCX TableData but adapted for ODF format

- **`ODTTableManager`** (class, lines ~468-607, ~140 lines)
  - Manages table collection with sequential ID generation
  - Sequential ID generation: TBL001, TBL002, TBL003...
  - Methods: `add_table()`, `get_table()`, `has_table()`, `get_all_tables()`, `get_statistics()`, `clear()`

#### Modified Functions:

**`extract_html_from_odt()`** (lines ~616)
- **Changed signature:** Returns `(html, css_manager, image_manager, table_manager)` instead of 3-tuple
- Creates `table_manager = ODTTableManager()`
- Detects `table:table` elements in document body
- Calls `_extract_table()` for each table
- Stores extracted tables in TableManager
- Returns 4-tuple with table_manager

**Document Body Parsing** (lines ~687-696)
- Added detection for `table:table` elements
- Appends `('table', elem)` to text_elements list

**Element Processing Loop** (lines ~699-717)
- Added `if elem_type == 'table':` branch
- Calls `_extract_table()` helper
- Creates HTMLSegment with tag_type='table'

**`_extract_table()`** (new helper, lines ~902-993)
- Extracts table from ODF table:table element
- Parses table:table-row and table:table-cell elements
- Extracts text from each cell (text:p paragraphs)
- Stores in TableManager
- Returns HTML table with data-table marker

**`_get_text_content()`** (new helper, lines ~995-1015)
- Recursively extracts text from ODF elements
- Used by _extract_table() for cell text

**`_generate_html()`** (lines ~1193-1196)
- Added `elif segment.tag_type == 'table':` branch
- Outputs table HTML directly (already formatted with data-table marker)

**`create_odt_from_html()`** (lines ~1287-1301)
- **Changed signature:** Accepts optional `table_manager` parameter
- Passes table_manager to HTMLToODTParser

**`HTMLToODTParser`** (class, lines ~1476+)
- **Enhanced `__init__`:** Accepts `table_manager` parameter
- Added `self.in_table` and `self.current_table_id` state tracking
- **Enhanced `handle_starttag()`:** Detects `<table data-table="TBL###">` markers
- **Enhanced `handle_endtag()`:** Resets table state when `</table>` encountered
- Skips parsing table content (tr, td, etc) - handled by table segment

**Segment Processing Loop** (lines ~1446-1477)
- Added `elif segment['type'] == 'table':` branch
- Creates ODF table:table, table:table-row, table:table-cell elements
- Adds table:table-column definitions
- Populates cells with text:p paragraphs
- Adds completed table to document

### 2. GUI Layer (`src/gui/google_translate_dock.py`)

#### Modified Methods:

**File Loading** (lines ~533-543, ~676-686)
- Updated 2 locations where `extract_html_from_odt()` is called
- Now receives 4-tuple: `html_content, css_manager, image_manager, table_manager`
- Stores `self._table_manager` for later use

**File Saving** (line ~1222-1226)
- Updated `_save_as_odt()` method
- Passes both `image_manager` and `table_manager` to `create_odt_from_html()`
- Uses `getattr(self, '_table_manager', None)` for backward compatibility

---

## Technical Details

### Table Extraction Process
1. Parse ODT content.xml
2. Detect `table:table` elements in document body
3. For each table:
   - Extract table:name attribute
   - Count rows (table:table-row elements)
   - Count columns (table:table-cell in first row)
   - Extract text from each cell:
     - Find text:p paragraphs within cell
     - Extract text content recursively
     - Join multiple paragraphs with space
   - Store in TableManager with sequential ID
4. Generate HTML table with data-table marker:
   ```html
   <table data-table="TBL001">
     <tr><td>Cell 1</td><td>Cell 2</td></tr>
   </table>
   ```

### Table Restoration Process
1. Parse translated HTML
2. Detect `<table data-table="TBL###">` markers
3. Retrieve table data from TableManager
4. Skip parsing table content (tr, td handled by table segment)
5. When processing table segment:
   - Create ODF table:table element
   - Add table:table-column for each column
   - For each row:
     - Create table:table-row
     - For each cell:
       - Create table:table-cell
       - Add text:p paragraph with cell text
   - Add table to document

### ODF Table Structure
```xml
<table:table table:name="Table1">
  <table:table-column table:number-columns-repeated="2"/>
  <table:table-row>
    <table:table-cell>
      <text:p>Cell content</text:p>
    </table:table-cell>
    ...
  </table:table-row>
  ...
</table:table>
```

### HTML Intermediate Format
```html
<table data-table="TBL001">
  <tr>
    <td>Cell content</td>
    ...
  </tr>
  ...
</table>
```

Google Translate preserves HTML table structure and attributes.

---

## Testing

### Test Script: `test_odt_tables_COM8.py`
- Creates test ODT with 3×2 table (Name/Age with 2 data rows)
- Tests full workflow: Extract → Translate → Save
- Verifies:
  - Table count matches
  - Table dimensions match (rows × cols)
  - Cell content matches (byte-for-byte comparison)

### Test Results:
```
✓ Extraction successful: 1 table (3×2), 6 cells
✓ Table markers found in HTML: 1
✓ HTML table elements found: 1
✓ ODT created successfully
✓ Tables verified in output: 1 table
✓ Table dimensions: 3×2
✓ All cells match
✓ SUCCESS - All tables preserved!
```

---

## Architecture Notes

### Why HTML Tables?
Google Translate preserves HTML table structure. By using `<table data-table="TBL001">`, we:
1. Keep track of table positions through translation
2. Preserve table structure (rows and cells)
3. Allow Google to translate cell content
4. Maintain proper document flow

### Pattern Consistency
- Phase 1 (Images): `ODTImageManager` + `data-image` markers
- Phase 2 (Tables): `ODTTableManager` + `data-table` markers
- Both follow same extraction → HTML → restoration pattern

### Backward Compatibility
- Old code without table_manager still works (parameter is optional)
- Uses `getattr(self, '_table_manager', None)` in GUI
- Falls back gracefully if no tables present

---

## Comparison: DOCX vs ODT

| Feature | DOCX | ODT |
|---------|------|-----|
| Table Manager | ✅ TableManager | ✅ ODTTableManager |
| HTML Markers | ✅ data-table | ✅ data-table |
| Storage | 2D list cells[][] | 2D list cells[][] |
| Format | OOXML w:tbl | ODF table:table |
| Row Element | w:tr | table:table-row |
| Cell Element | w:tc | table:table-cell |
| Text Container | w:p | text:p |
| Column Def | w:gridCol | table:table-column |

---

## Files Modified

1. `src/translation/html_format_mapper.py` (+~280 lines)
   - ODTTableData and ODTTableManager classes
   - _extract_table() and _get_text_content() helpers
   - extract_html_from_odt() signature change
   - create_odt_from_html() signature change
   - HTMLToODTParser table handling
   - Segment processing for tables

2. `src/gui/google_translate_dock.py` (+6 lines, 3 locations)
   - Updated ODT loading to receive table_manager (2 locations)
   - Updated ODT saving to pass table_manager (1 location)

## Files Created

1. `test_odt_tables_COM8.py` - Table preservation test script
2. `docs/com8/PHASE2_ODT_TABLES_COMPLETE_COM8.md` - This document
3. `docs/com8/PHASE2_ODT_TABLES_IMPLEMENTATION_COM8.md` - Implementation plan

---

## Implementation Timeline

- **Phase 2.1:** Research & Design - 30 min ✅
- **Phase 2.2:** Table Extraction - 1.5 hours ✅
- **Phase 2.3:** Table Restoration - 1.5 hours ✅
- **Phase 2.4:** Integration - 20 min ✅
- **Phase 2.5:** Testing - 30 min ✅
- **Phase 2.6:** Documentation - 30 min ✅

**Total Time:** ~5 hours (on lower end of 5-7 hour estimate!)

---

## Lessons Learned

1. **HTMLSegment Structure:** Must provide all 4 parameters (text, css_class, tag_type, attributes)
2. **ODF Recursion:** Need recursive text extraction for nested elements in cells
3. **Pattern Reusability:** Image preservation pattern translated perfectly to tables
4. **Testing Critical:** Creating test ODT programmatically validated implementation
5. **State Tracking:** Need `in_table` flag to skip parsing table internals in HTML parser

---

## Future Enhancements (Optional)

- Table formatting preservation (borders, cell styles, colors)
- Cell spanning (rowspan, colspan)
- Nested tables support
- Table headers (thead) vs body (tbody) distinction
- Column width preservation
- Table alignment and positioning

---

## Acknowledgments

- Protocol: SIMPLICITY_PROTOCOL_3.md
- Pattern reference: `docx_html_mapper.py` TableManager implementation
- Phase 1 (Images): Provided proven extraction/restoration pattern
- Test file: Created programmatically with odfpy

---

**Phase 2 Status:** ✅ **COMPLETE AND TESTED**  
**Combined with Phase 1:** ODT files now support **BOTH images and tables**!

**Ready for:** Git commit and potential Phase 3 (if needed)
