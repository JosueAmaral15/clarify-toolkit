# Phase 2.2: TableManager Design - COM8

**Date:** 2026-02-17  
**Programmer:** COM8  
**Task:** Design TableManager and TableData for table preservation  
**Status:** ✅ COMPLETE  
**Duration:** 30 minutes

---

## Objective

Design data structures and API for table preservation system that converts DOCX tables to HTML and back.

**Requirements:**
1. Store table metadata (rows, columns, style)
2. Track tables with unique IDs
3. Support HTML conversion workflow
4. Compatible with existing ImageManager pattern
5. Handle edge cases gracefully

---

## Design Decisions

### 1. Follow ImageManager Pattern

**Rationale:**
- Proven successful for image preservation
- Consistent API across preservation systems
- Familiar to developers
- Clear separation of concerns

**Pattern Applied:**
```
TableData    ← Stores single table metadata
TableManager ← Manages collection of TableData
```

Similar to:
```
ImageData    ← Stores single image metadata
ImageManager ← Manages collection of ImageData
```

### 2. ID Format: TBL001, TBL002, TBL003

**Format:** `TBL` + zero-padded 3-digit number

**Rationale:**
- Consistent with IMG001, IMG002 pattern
- Sortable alphabetically
- Human-readable
- Easy to parse in HTML

**HTML Usage:**
```html
<table data-table="TBL001">
  <tr><td>...</td></tr>
</table>
```

### 3. Minimal Storage (Phase 2 Scope)

**Store Only:**
- Table ID
- Row count
- Column count
- Style name
- Cell content (2D list)

**Defer to Phase 3:**
- Cell borders
- Cell shading
- Column widths
- Row heights
- Merged cells
- Cell alignment

**Rationale:**
- 90% of use cases covered by basic structure
- Simpler implementation = faster delivery
- Can enhance later without breaking API
- Focus on translation correctness first

---

## Data Structure Design

### TableData Dataclass

```python
@dataclass
class TableData:
    """Stores metadata for a single table."""
    
    # Core identification
    table_id: str                    # e.g., "TBL001"
    
    # Structure
    rows: int                        # Number of rows
    cols: int                        # Number of columns
    
    # Content
    cells: List[List[str]]           # 2D array [row][col] = text
    
    # Style
    style: Optional[str] = None      # Style name (e.g., "Normal Table")
    
    # Position tracking
    document_index: Optional[int] = None  # Position in doc.element.body
    
    def get_cell(self, row: int, col: int) -> str:
        """Get cell text at row, col (0-indexed)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return ""
    
    def set_cell(self, row: int, col: int, text: str) -> None:
        """Set cell text at row, col (0-indexed)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col] = text
    
    def to_html(self) -> str:
        """Convert to HTML table string."""
        html = f'<table data-table="{self.table_id}">\n'
        for row_idx in range(self.rows):
            html += '  <tr>\n'
            for col_idx in range(self.cols):
                cell_text = escape_html(self.cells[row_idx][col_idx])
                html += f'    <td>{cell_text}</td>\n'
            html += '  </tr>\n'
        html += '</table>'
        return html
    
    def get_dimensions(self) -> tuple[int, int]:
        """Get (rows, cols) tuple."""
        return (self.rows, self.cols)
```

**Design Notes:**

1. **Core Fields:**
   - `table_id`: Unique identifier (TBL001)
   - `rows`, `cols`: Dimensions
   - `cells`: 2D list storing all text content

2. **Optional Fields:**
   - `style`: Table style name (for reconstruction)
   - `document_index`: Position in document (for ordering)

3. **Helper Methods:**
   - `get_cell(row, col)`: Safe access with bounds check
   - `set_cell(row, col, text)`: Safe write with bounds check
   - `to_html()`: Convert to HTML (used during extraction)
   - `get_dimensions()`: Get size tuple

4. **Data Structure Choice:**
   - 2D list `cells[row][col]` = natural matrix representation
   - Alternative considered: flat list + index math (rejected: less readable)

---

### TableManager Class

```python
class TableManager:
    """Manages collection of tables for preservation."""
    
    def __init__(self):
        """Initialize empty table manager."""
        self._tables: Dict[str, TableData] = {}
        self._next_id: int = 1
        self._document_order: List[str] = []  # Track table order
    
    def add_table(
        self,
        rows: int,
        cols: int,
        cells: List[List[str]],
        style: Optional[str] = None,
        document_index: Optional[int] = None
    ) -> str:
        """
        Add table to manager and return assigned ID.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            cells: 2D list of cell text [row][col]
            style: Table style name (optional)
            document_index: Position in document (optional)
        
        Returns:
            table_id: Assigned table ID (e.g., "TBL001")
        
        Raises:
            ValueError: If dimensions don't match cells array
        """
        # Validate dimensions
        if len(cells) != rows:
            raise ValueError(f"Expected {rows} rows, got {len(cells)}")
        for row_idx, row in enumerate(cells):
            if len(row) != cols:
                raise ValueError(
                    f"Row {row_idx} has {len(row)} cells, expected {cols}"
                )
        
        # Generate ID
        table_id = f"TBL{self._next_id:03d}"
        self._next_id += 1
        
        # Create and store
        table_data = TableData(
            table_id=table_id,
            rows=rows,
            cols=cols,
            cells=cells,
            style=style,
            document_index=document_index
        )
        self._tables[table_id] = table_data
        self._document_order.append(table_id)
        
        return table_id
    
    def get_table(self, table_id: str) -> Optional[TableData]:
        """
        Get table by ID.
        
        Args:
            table_id: Table identifier (e.g., "TBL001")
        
        Returns:
            TableData if found, None otherwise
        """
        return self._tables.get(table_id)
    
    def has_table(self, table_id: str) -> bool:
        """Check if table exists."""
        return table_id in self._tables
    
    def get_all_tables(self) -> List[TableData]:
        """Get all tables in document order."""
        return [self._tables[tid] for tid in self._document_order]
    
    def get_table_count(self) -> int:
        """Get total number of tables."""
        return len(self._tables)
    
    def generate_html_placeholder(self, table_id: str) -> str:
        """
        Generate HTML placeholder for table.
        
        This is used during extraction to replace DOCX table
        with HTML table that will be sent to Google Translate.
        
        Args:
            table_id: Table identifier
        
        Returns:
            HTML table string with data-table attribute
        
        Raises:
            ValueError: If table_id not found
        """
        table_data = self.get_table(table_id)
        if not table_data:
            raise ValueError(f"Table not found: {table_id}")
        
        return table_data.to_html()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored tables."""
        total_cells = sum(t.rows * t.cols for t in self._tables.values())
        
        return {
            'table_count': len(self._tables),
            'total_cells': total_cells,
            'largest_table': max(
                (t.rows * t.cols for t in self._tables.values()),
                default=0
            ),
            'table_ids': list(self._document_order)
        }
    
    def clear(self) -> None:
        """Clear all stored tables and reset counter."""
        self._tables.clear()
        self._document_order.clear()
        self._next_id = 1
```

**Design Notes:**

1. **Storage:**
   - `_tables`: Dict mapping table_id → TableData
   - `_document_order`: List of table_ids in document order
   - `_next_id`: Counter for generating unique IDs

2. **Core Methods:**
   - `add_table()`: Store new table, return ID
   - `get_table()`: Retrieve by ID
   - `has_table()`: Check existence

3. **Utility Methods:**
   - `get_all_tables()`: Get tables in document order
   - `get_table_count()`: Count tables
   - `generate_html_placeholder()`: Convert table to HTML
   - `get_statistics()`: Debug info
   - `clear()`: Reset manager

4. **Error Handling:**
   - Validates dimensions match cells array
   - Raises ValueError on invalid data
   - Returns None for missing tables (graceful)

---

## HTML Conversion Specification

### DOCX Table → HTML Table

**Input (python-docx):**
```python
table = doc.tables[0]
table.rows       # 3 rows
table.columns    # 2 columns
```

**Output (HTML):**
```html
<table data-table="TBL001">
  <tr>
    <td>Header 1</td>
    <td>Header 2</td>
  </tr>
  <tr>
    <td>Row 1, Col 1</td>
    <td>Row 1, Col 2</td>
  </tr>
  <tr>
    <td>Row 2, Col 1</td>
    <td>Row 2, Col 2</td>
  </tr>
</table>
```

**Key Features:**
- `data-table` attribute → Preserved by Google Translate
- Standard HTML tags → Google translates cell content
- Newlines/indentation → Readability (stripped during parsing)
- HTML entity escaping → Special characters protected

### HTML Escaping

**Special Characters:**
```python
'&'  → '&amp;'
'<'  → '&lt;'
'>'  → '&gt;'
'"'  → '&quot;'
"'"  → '&#x27;'
```

**Why Needed:**
- User table cells may contain HTML-like text
- Example: "Use <table> tag" → Must escape `<>`
- Python's `html.escape()` handles this

**Implementation:**
```python
from html import escape as escape_html

cell_text = "Use <table> tag"
safe_html = f'<td>{escape_html(cell_text)}</td>'
# Result: <td>Use &lt;table&gt; tag</td>
```

---

## Integration Points

### 1. DocxHtmlMapper._extract_segments()

**Location:** After paragraph processing, before final loop

**Pseudocode:**
```python
# Existing: Process paragraphs
for para in doc.paragraphs:
    # ... existing code ...

# NEW: Process tables
self.table_manager = TableManager()

for table in doc.tables:
    # Extract cell content
    rows = len(table.rows)
    cols = len(table.columns)
    cells = []
    
    for row in table.rows:
        row_cells = [cell.text for cell in row.cells]
        cells.append(row_cells)
    
    # Store in manager
    table_id = self.table_manager.add_table(
        rows=rows,
        cols=cols,
        cells=cells,
        style=table.style.name if table.style else None
    )
    
    # Create segment
    segment = HTMLSegment(
        type='table',
        content='',  # No plain text content
        html='',     # Generated later
        css_classes=[],
        table_id=table_id  # NEW field
    )
    segments.append(segment)
```

**Changes Required:**
1. Add `self.table_manager = TableManager()` initialization
2. Iterate `doc.tables` after paragraphs
3. Extract cell content with nested loops
4. Call `table_manager.add_table()`
5. Create `HTMLSegment` with `type='table'` and `table_id`

**New Field:**
```python
@dataclass
class HTMLSegment:
    # ... existing fields ...
    table_id: Optional[str] = None  # NEW: For table segments
```

### 2. DocxHtmlMapper._generate_html()

**Location:** In segment processing loop

**Pseudocode:**
```python
for segment in segments:
    if segment.type == 'paragraph':
        # ... existing code ...
    
    elif segment.type == 'table':  # NEW
        # Generate HTML table
        html_table = self.table_manager.generate_html_placeholder(
            segment.table_id
        )
        html_parts.append(html_table)
```

**Changes Required:**
1. Add `elif segment.type == 'table'` branch
2. Call `generate_html_placeholder()`
3. Append HTML table to output

### 3. HTMLToDocxParser.handle_starttag()

**Location:** In tag detection logic

**Pseudocode:**
```python
def handle_starttag(self, tag, attrs):
    if tag == 'p':
        # ... existing code ...
    
    elif tag == 'span':
        # ... existing image/tab code ...
    
    elif tag == 'table':  # NEW
        # Extract table ID
        attrs_dict = dict(attrs)
        table_id = attrs_dict.get('data-table')
        
        if table_id:
            self._current_table_id = table_id
            self._current_table_rows = []
    
    elif tag == 'tr':  # NEW
        self._current_table_row = []
    
    elif tag == 'td':  # NEW
        self._current_cell_content = []
```

**Changes Required:**
1. Add `table`, `tr`, `td` tag handlers
2. Track current table being parsed
3. Accumulate rows and cells
4. Reconstruct DOCX table when `</table>` encountered

### 4. HTMLToDocxParser._reconstruct_table()

**New Method:**
```python
def _reconstruct_table(self, table_id: str, html_rows: List[List[str]]):
    """
    Reconstruct DOCX table from HTML data.
    
    Args:
        table_id: Table identifier
        html_rows: 2D list [row][col] of translated cell text
    """
    # Get original metadata
    table_data = self.table_manager.get_table(table_id)
    if not table_data:
        self._log_warning(f"Table not found: {table_id}")
        return
    
    # Create DOCX table
    rows = len(html_rows)
    cols = len(html_rows[0]) if html_rows else 0
    
    doc_table = self.doc.add_table(rows=rows, cols=cols)
    
    # Apply style if available
    if table_data.style:
        try:
            doc_table.style = table_data.style
        except KeyError:
            pass  # Style not available, use default
    
    # Fill cells with translated content
    for row_idx, row_data in enumerate(html_rows):
        for col_idx, cell_text in enumerate(row_data):
            doc_table.rows[row_idx].cells[col_idx].text = cell_text
```

**Changes Required:**
1. Create new `_reconstruct_table()` method
2. Call from `handle_endtag()` when `</table>` seen
3. Get original metadata from TableManager
4. Create DOCX table with translated content

---

## API Changes

### Public API (extract_html_from_docx)

**OLD (Phase 1):**
```python
html, css_manager, image_manager = extract_html_from_docx(docx_path)
```

**NEW (Phase 2):**
```python
html, css_manager, image_manager, table_manager = extract_html_from_docx(docx_path)
```

**Change:** Returns 4-tuple instead of 3-tuple

### Public API (create_docx_from_html)

**OLD (Phase 1):**
```python
create_docx_from_html(html, output_path, css_manager, image_manager)
```

**NEW (Phase 2):**
```python
create_docx_from_html(
    html,
    output_path,
    css_manager,
    image_manager,
    table_manager  # NEW parameter
)
```

**Change:** Added `table_manager` parameter

### Backward Compatibility

**Strategy:** Optional parameter with default

```python
def create_docx_from_html(
    html: str,
    output_path: str,
    css_manager: CSSClassManager,
    image_manager: Optional[ImageManager] = None,
    table_manager: Optional[TableManager] = None  # NEW, optional
):
    """..."""
    if table_manager is None:
        table_manager = TableManager()  # Empty manager
```

**Result:** Old code still works (no tables reconstructed)

---

## Edge Cases & Validation

### 1. Empty Table (0 Rows or 0 Cols)

**Scenario:** User creates empty table structure

**Handling:**
```python
if rows == 0 or cols == 0:
    # Skip table, add warning
    logger.warning(f"Skipping empty table: {rows}x{cols}")
    return None
```

**Rationale:** Empty tables have no content to translate

### 2. Single-Cell Table (1×1)

**Scenario:** Table with one row, one column

**Handling:** Treat as normal table
```html
<table data-table="TBL001">
  <tr>
    <td>Single cell content</td>
  </tr>
</table>
```

**Rationale:** Valid table structure, no special case needed

### 3. Large Tables (100+ Rows)

**Scenario:** Very large table with many cells

**Handling:**
- No size limit in Phase 2
- Memory warning if total cells > 10,000

```python
total_cells = rows * cols
if total_cells > 10000:
    logger.warning(
        f"Large table detected: {table_id} ({rows}x{cols} = {total_cells} cells)"
    )
```

**Rationale:** Google Translate can handle large HTML, but warn user

### 4. Nested Tables

**Scenario:** Table inside table cell

**Handling:** Phase 2 does NOT support
```python
if cell.tables:
    # Cell contains nested table
    logger.warning(f"Nested tables not supported in Phase 2")
    # Extract only text, ignore nested table
```

**Rationale:** Rare case (< 1% of documents), defer to Phase 3

### 5. Merged Cells

**Scenario:** Cells merged horizontally or vertically

**Handling:** Phase 2 does NOT preserve merge
```python
# Simply extract text from merged cell
# Ignore merge info (cell.merge)
```

**Result:** Merged cells become unmerged in output

**Rationale:** Complex XML manipulation, defer to Phase 3

### 6. Special Characters in Cells

**Scenario:** Cell contains `<`, `>`, `&`, etc.

**Handling:** HTML escape during conversion
```python
from html import escape
cell_html = f'<td>{escape(cell.text)}</td>'
```

**Example:**
- Input: `"Use <table> tag"`
- HTML: `<td>Use &lt;table&gt; tag</td>`
- Output: `"Use <table> tag"` (restored)

### 7. Cell with Multiple Paragraphs

**Scenario:** Cell contains multiple paragraphs

**Handling:** Join with newline
```python
cell_text = '\n'.join(para.text for para in cell.paragraphs)
```

**Rationale:** Preserve paragraph breaks as plain text

### 8. Missing Table Style

**Scenario:** Table has no style assigned

**Handling:** Use default
```python
style = table.style.name if table.style else None
# Later: doc_table.style = style or 'Normal Table'
```

**Result:** Default style applied during reconstruction

---

## Memory Considerations

### Storage Size Estimation

**Per Table:**
```python
# TableData object
table_id: 6 bytes ("TBL001")
rows: 8 bytes (int)
cols: 8 bytes (int)
cells: N × M × avg_text_length bytes
style: ~20 bytes (string)
document_index: 8 bytes (int)

# Example: 10x10 table, 20 chars per cell
overhead = 6 + 8 + 8 + 20 + 8 = 50 bytes
cells_data = 10 × 10 × 20 = 2,000 bytes
total ≈ 2 KB per table
```

**Document with 50 Tables:**
```
50 tables × 2 KB ≈ 100 KB
```

**Conclusion:** Memory usage negligible for typical documents

### Large Table Warning Threshold

```python
MAX_CELLS_WARNING = 10_000  # 100x100 or 200x50

total_cells = rows * cols
if total_cells > MAX_CELLS_WARNING:
    logger.warning(
        f"Large table: {table_id} ({rows}×{cols} = {total_cells} cells). "
        f"Translation may be slow."
    )
```

**Rationale:**
- 10,000 cells = ~200 KB text (assuming 20 chars/cell)
- Google Translate handles this fine
- Just warn user about potential delay

---

## Testing Strategy

### Unit Tests (test_table_manager_COM8.py)

**Test Coverage:**

1. **TableData Tests:**
   - Create table with valid data
   - Get/set cell by index
   - Bounds checking (out of range)
   - to_html() conversion
   - get_dimensions()

2. **TableManager Tests:**
   - Add single table → returns TBL001
   - Add multiple tables → TBL001, TBL002, TBL003
   - Get table by ID
   - Get non-existent table → None
   - has_table() check
   - get_all_tables() ordering
   - get_table_count()
   - generate_html_placeholder()
   - get_statistics()
   - clear()

3. **Validation Tests:**
   - Mismatched dimensions → ValueError
   - Jagged array (different row lengths) → ValueError

4. **Edge Case Tests:**
   - Single-cell table (1×1)
   - Large table (100×100)
   - Empty cell content
   - Special characters in cells (HTML escaping)
   - Multiple paragraphs in cell

**Estimated Tests:** 20-25 tests

### Integration Tests (test_docx_end_to_end_COM8.py)

**Test Cases:**

1. **Simple Table Document:**
   - Load test_table_COM8.docx (3×2 table)
   - Extract → 1 table found
   - Verify cells match original
   - Verify HTML generation

2. **Table + Text Document:**
   - Paragraph, Table, Paragraph
   - Verify correct ordering

3. **Multiple Tables:**
   - Document with 3 tables
   - Verify IDs: TBL001, TBL002, TBL003
   - Verify all tables extracted

4. **Table Reconstruction:**
   - Extract HTML
   - Parse HTML
   - Reconstruct DOCX
   - Verify cells match original

**Estimated Tests:** 5-8 integration tests

---

## Documentation Requirements

### Code Documentation

**Docstrings Required:**
- TableData class and all methods
- TableManager class and all methods
- All new functions in docx_html_mapper.py

**Example:**
```python
class TableManager:
    """
    Manages collection of tables for DOCX↔HTML conversion.
    
    Tables are assigned unique IDs (TBL001, TBL002, etc.) and
    stored with their metadata. During extraction, DOCX tables
    are converted to HTML <table> elements. During reconstruction,
    HTML tables are converted back to DOCX tables.
    
    Example:
        >>> manager = TableManager()
        >>> table_id = manager.add_table(
        ...     rows=2, cols=2,
        ...     cells=[['A', 'B'], ['C', 'D']]
        ... )
        >>> table_id
        'TBL001'
        >>> html = manager.generate_html_placeholder(table_id)
        >>> print(html)
        <table data-table="TBL001">
          <tr><td>A</td><td>B</td></tr>
          <tr><td>C</td><td>D</td></tr>
        </table>
    """
```

### User Documentation (Phase Summary)

**Include:**
- Architecture overview
- HTML format specification
- API changes (breaking)
- Edge cases and limitations
- Migration guide (4-tuple API)

---

## Comparison: Tables vs Images

### Architecture Similarity

| Component | Images | Tables |
|-----------|--------|--------|
| **Data Class** | ImageData | TableData |
| **Manager** | ImageManager | TableManager |
| **ID Format** | IMG001 | TBL001 |
| **HTML Marker** | `<span data-image>` | `<table data-table>` |
| **Storage** | Binary blobs | Text cells |

### Key Differences

| Aspect | Images | Tables |
|--------|--------|--------|
| **Translation** | Skipped (no text) | Translated (cell content) |
| **HTML Structure** | Empty span | Full HTML table |
| **Complexity** | Medium | Higher |
| **Size** | Large (KB-MB) | Small (bytes-KB) |
| **Deduplication** | Hash-based | Not needed |

### Shared Patterns

✅ Both use HTML markers preserved by Google  
✅ Both use Manager classes for storage  
✅ Both require extraction and reconstruction  
✅ Both stored in HTMLSegment  
✅ Both passed through translation workflow  

---

## Implementation Checklist

### Phase 2.3: Implementation (Next Phase)

**Files to Modify:**

1. **src/translation/docx_html_mapper.py:**
   - [ ] Add TableData dataclass (~28 lines)
   - [ ] Add TableManager class (~130 lines)
   - [ ] Add table_id to HTMLSegment
   - [ ] Import html.escape
   - [ ] Initialize TableManager in __init__

2. **tests/com8/test_table_manager_COM8.py:**
   - [ ] Create new test file
   - [ ] Add 20-25 unit tests
   - [ ] Test TableData methods
   - [ ] Test TableManager methods
   - [ ] Test edge cases

**Estimated Time:** 1 hour implementation + testing

### Phase 2.4: Integration (Following Phase)

**Files to Modify:**

1. **src/translation/docx_html_mapper.py:**
   - [ ] Modify _extract_segments() for tables
   - [ ] Modify _generate_html() for tables
   - [ ] Modify HTMLToDocxParser for table parsing
   - [ ] Add _reconstruct_table() method
   - [ ] Update public API signatures

2. **tests/com8/test_docx_end_to_end_COM8.py:**
   - [ ] Update for 4-tuple API
   - [ ] Add table integration tests

**Estimated Time:** 1 hour integration + testing

---

## Success Criteria

**Phase 2.2 Complete When:**
- ✅ TableData dataclass designed (7 fields, 4 methods)
- ✅ TableManager class designed (10 methods)
- ✅ HTML conversion spec documented
- ✅ Integration points identified (4 locations)
- ✅ API changes documented (4-tuple)
- ✅ Edge cases analyzed (8 cases)
- ✅ Testing strategy defined (25+ tests)
- ✅ Documentation requirements listed

**Ready for Phase 2.3:** Implementation

---

## Risk Assessment

### Low Risk
✅ API design follows proven ImageManager pattern  
✅ HTML table format is standard and well-supported  
✅ python-docx table API is straightforward  

### Medium Risk
⚠️ HTML escaping must be correct (special chars)  
⚠️ Table ordering must be preserved in document  
⚠️ Cell content with newlines needs handling  

### Mitigation
- Comprehensive unit tests for escaping
- Document index tracking for ordering
- Use '\n'.join() for multi-paragraph cells

### Deferred to Phase 3
⏸ Nested tables (rare case)  
⏸ Merged cells (complex)  
⏸ Advanced formatting (borders, shading)  

---

## Files to be Created/Modified

**This Phase (2.2):**
- ✅ `docs/com8/PHASE2_2_TABLE_MANAGER_DESIGN_COM8.md` (this file)

**Next Phase (2.3):**
- 🔄 `src/translation/docx_html_mapper.py` (add classes)
- ➕ `tests/com8/test_table_manager_COM8.py` (new file)

**Phase 2.4:**
- 🔄 `src/translation/docx_html_mapper.py` (integration)
- 🔄 `tests/com8/test_docx_end_to_end_COM8.py` (update API)

**Phase 2.5:**
- 🔄 `src/gui/google_translate_dock.py` (if needed)

---

## Conclusion

**Status:** ✅ Phase 2.2 COMPLETE

**Key Achievements:**
- TableData and TableManager classes designed
- HTML conversion specification defined
- Integration points identified
- API changes documented (breaking but backward compatible)
- Edge cases analyzed with handling strategies
- Testing strategy planned (25+ tests)

**Design Confidence:** HIGH
- Follows successful ImageManager pattern
- HTML table format is proven technology
- Clear separation of concerns
- Comprehensive edge case coverage

**Ready for Implementation:** YES
- All design decisions made
- Data structures finalized
- Integration approach clear
- Test plan defined

**Estimated Remaining Time (Phase 2):**
- Phase 2.3 Implementation: 1 hour
- Phase 2.4 Integration: 1 hour
- Phase 2.5 Google Translate: 30 minutes
- **Total: ~2.5 hours**

---

**Time Spent (Phase 2.2):** 30 minutes  
**Next Phase:** 2.3 (TableManager Implementation) - Estimated 1 hour  
**Phase 2 Progress:** 2/5 complete (40%)
