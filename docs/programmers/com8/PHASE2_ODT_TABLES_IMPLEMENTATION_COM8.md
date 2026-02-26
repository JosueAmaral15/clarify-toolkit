# Phase 2: ODT Table Preservation - Implementation Plan
## COM8 - 2026-02-19

---

## Overview

Implement table preservation for ODT files in Google Translate tool, following the proven pattern from:
1. DOCX tables (docx_html_mapper.py)
2. ODT images (Phase 1, completed)

**Goal:** Tables in ODT files should be preserved through translation workflow.

---

## Architecture Pattern

### Workflow:
```
ODT with tables → Extract (ODF → HTML) → Translate → Restore (HTML → ODF)
                     ↓                                      ↑
                 TableManager                          TableManager
                     ↓                                      ↑
                 HTML <table>                          HTML <table>
                 data-table="TBL001"                   data-table="TBL001"
```

### Key Components:
1. **ODTTableData** (dataclass) - Stores table metadata
2. **ODTTableManager** (class) - Manages table collection
3. **extract_html_from_odt()** - Detects and extracts tables
4. **create_odt_from_html()** - Restores tables to ODF
5. **HTMLToODTParser** - Handles data-table markers

---

## ODF Table Structure

### XML Structure:
```xml
<table:table table:name="Table1">
  <table:table-column table:number-columns-repeated="2"/>
  <table:table-row>
    <table:table-cell>
      <text:p>Cell A1</text:p>
    </table:table-cell>
    <table:table-cell>
      <text:p>Cell B1</text:p>
    </table:table-cell>
  </table:table-row>
  <table:table-row>
    <table:table-cell>
      <text:p>Cell A2</text:p>
    </table:table-cell>
    <table:table-cell>
      <text:p>Cell B2</text:p>
    </table:table-cell>
  </table:table-row>
</table:table>
```

### Key Elements:
- `table:table` - Main table container
- `table:table-row` - Row element
- `table:table-cell` - Cell element
- `table:table-column` - Column definition (optional)
- `text:p` - Paragraph within cell

### Namespace:
```python
from odf.namespaces import TABLENS
# "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
```

---

## Phase 2.1: Research & Design ✅ (30-45 min)

**Status:** Complete

**Findings:**
- ODF uses `table:table`, `table:table-row`, `table:table-cell`
- Each cell contains `text:p` paragraphs
- Similar structure to HTML tables
- DOCX TableManager exists and can be adapted
- Pattern identical to image preservation from Phase 1

---

## Phase 2.2: Table Extraction (1-2 hours)

### 2.2.1: Create ODTTableData Dataclass

**Location:** `src/translation/html_format_mapper.py` (after ODTImageManager)

```python
@dataclass
class ODTTableData:
    """Stores metadata for a single ODT table."""
    
    table_id: str                     # 'TBL001', 'TBL002', etc.
    rows: int                         # Number of rows
    cols: int                         # Number of columns
    cells: List[List[str]]            # 2D array [row][col] = text
    name: Optional[str] = None        # table:name attribute
    
    def get_cell(self, row: int, col: int) -> str:
        """Get cell text at row, col (0-indexed)."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return ""
    
    def to_html(self) -> str:
        """Convert to HTML table with data-table marker."""
        html_parts = [f'<table data-table="{self.table_id}">\n']
        for row_idx in range(self.rows):
            html_parts.append('  <tr>\n')
            for col_idx in range(self.cols):
                cell_text = self.cells[row_idx][col_idx]
                safe_text = html.escape(cell_text)
                html_parts.append(f'    <td>{safe_text}</td>\n')
            html_parts.append('  </tr>\n')
        html_parts.append('</table>')
        return ''.join(html_parts)
```

### 2.2.2: Create ODTTableManager Class

**Location:** `src/translation/html_format_mapper.py` (after ODTTableData)

```python
class ODTTableManager:
    """Manages collection of tables for ODT↔HTML conversion."""
    
    def __init__(self):
        self._tables: Dict[str, ODTTableData] = {}
        self._document_order: List[str] = []
        self._next_id: int = 1
    
    def add_table(
        self,
        rows: int,
        cols: int,
        cells: List[List[str]],
        name: Optional[str] = None
    ) -> str:
        """Add table and return assigned ID."""
        # Validate dimensions
        if len(cells) != rows:
            raise ValueError(f"Expected {rows} rows, got {len(cells)}")
        
        # Generate ID
        table_id = f"TBL{self._next_id:03d}"
        self._next_id += 1
        
        # Store
        table_data = ODTTableData(
            table_id=table_id,
            rows=rows,
            cols=cols,
            cells=cells,
            name=name
        )
        self._tables[table_id] = table_data
        self._document_order.append(table_id)
        
        return table_id
    
    def get_table(self, table_id: str) -> Optional[ODTTableData]:
        """Get table by ID."""
        return self._tables.get(table_id)
    
    def get_statistics(self) -> dict:
        """Get storage statistics."""
        return {
            'total_tables': len(self._tables),
            'table_ids': list(self._document_order)
        }
```

### 2.2.3: Update extract_html_from_odt()

**Signature Change:**
```python
# OLD:
def extract_html_from_odt(odt_path: str) -> Tuple[str, CSSClassManager, ODTImageManager]:

# NEW:
def extract_html_from_odt(odt_path: str) -> Tuple[str, CSSClassManager, ODTImageManager, ODTTableManager]:
```

**Logic to Add:**
1. Create `table_manager = ODTTableManager()`
2. After parsing content.xml, iterate through document body
3. Detect `table:table` elements
4. For each table:
   - Count rows and columns
   - Extract cell text from each `table:table-cell → text:p`
   - Store in table_manager
   - Replace in content with HTML marker
5. Return `(html, css_manager, image_manager, table_manager)`

### 2.2.4: Add Table Detection in Content Parser

**New Helper Function:**
```python
def _extract_table(table_element, table_manager: ODTTableManager) -> str:
    """
    Extract table from ODF element.
    
    Args:
        table_element: odf.table.Table element
        table_manager: ODTTableManager to store table
    
    Returns:
        HTML table string with data-table marker
    """
    from odf.table import TableRow, TableCell
    from odf.text import P
    
    # Get table name
    table_name = table_element.getAttribute('name')
    
    # Extract rows
    rows_elements = table_element.getElementsByType(TableRow)
    rows = len(rows_elements)
    
    # Determine columns (from first row)
    if rows > 0:
        first_row_cells = rows_elements[0].getElementsByType(TableCell)
        cols = len(first_row_cells)
    else:
        cols = 0
    
    # Extract cell text
    cells = []
    for row_elem in rows_elements:
        row_cells = []
        cell_elements = row_elem.getElementsByType(TableCell)
        
        for cell_elem in cell_elements:
            # Extract text from paragraphs in cell
            paragraphs = cell_elem.getElementsByType(P)
            cell_text = ' '.join(str(p) for p in paragraphs)
            row_cells.append(cell_text)
        
        cells.append(row_cells)
    
    # Store in manager
    table_id = table_manager.add_table(
        rows=rows,
        cols=cols,
        cells=cells,
        name=table_name
    )
    
    # Return HTML
    table_data = table_manager.get_table(table_id)
    return table_data.to_html()
```

---

## Phase 2.3: Table Restoration (1-2 hours)

### 2.3.1: Update create_odt_from_html()

**Signature Change:**
```python
# OLD:
def create_odt_from_html(html: str, css_manager, output_path: str, 
                         image_manager: Optional[ODTImageManager] = None):

# NEW:
def create_odt_from_html(html: str, css_manager, output_path: str,
                         image_manager: Optional[ODTImageManager] = None,
                         table_manager: Optional[ODTTableManager] = None):
```

**Pass to Parser:**
```python
parser = HTMLToODTParser(css_manager, image_manager, table_manager)
```

### 2.3.2: Update HTMLToODTParser

**Constructor:**
```python
def __init__(self, css_manager, image_manager=None, table_manager=None):
    super().__init__()
    self.css_manager = css_manager
    self.image_manager = image_manager
    self.table_manager = table_manager  # NEW
    self.segments = []
    self.current_tag = None
    self.current_class = None
    self.in_table = False  # NEW: Track if parsing table
    self.current_table_id = None  # NEW
```

**Update handle_starttag:**
```python
def handle_starttag(self, tag, attrs):
    # ... existing code ...
    
    # NEW: Handle table tags
    if tag == 'table':
        for attr, value in attrs:
            if attr == 'data-table' and self.table_manager:
                self.in_table = True
                self.current_table_id = value
                # Add table segment
                table_data = self.table_manager.get_table(value)
                if table_data:
                    self.segments.append({
                        'type': 'table',
                        'table_id': value,
                        'table_data': table_data
                    })
                return
    
    # Skip content inside tables (handled separately)
    if self.in_table and tag in ['tr', 'td', 'th']:
        return
```

**Update handle_endtag:**
```python
def handle_endtag(self, tag):
    if tag == 'table':
        self.in_table = False
        self.current_table_id = None
        return
    
    # ... existing code ...
```

### 2.3.3: Add Table Segment Handling in create_odt_from_html()

**In segment processing loop:**
```python
elif segment['type'] == 'table':
    # Phase 2 - COM8: Handle table restoration
    if current_paragraph is not None:
        doc.text.addElement(current_paragraph)
        current_paragraph = None
    
    table_data = segment['table_data']
    
    # Create ODF table
    from odf.table import Table, TableColumn, TableRow, TableCell
    from odf.text import P
    
    odt_table = Table(name=table_data.name or f"Table{table_data.table_id}")
    
    # Add column definitions
    for _ in range(table_data.cols):
        odt_table.addElement(TableColumn())
    
    # Add rows and cells
    for row_idx in range(table_data.rows):
        row = TableRow()
        for col_idx in range(table_data.cols):
            cell = TableCell()
            cell_text = table_data.get_cell(row_idx, col_idx)
            p = P(text=cell_text)
            cell.addElement(p)
            row.addElement(cell)
        odt_table.addElement(row)
    
    doc.text.addElement(odt_table)
```

---

## Phase 2.4: Integration (30 min)

### Update GUI (google_translate_dock.py)

**File Loading (2 locations):**
```python
# OLD:
html_content, css_manager, image_manager = HTMLFormatMapper.extract_html_from_odt(file_path)

# NEW:
html_content, css_manager, image_manager, table_manager = HTMLFormatMapper.extract_html_from_odt(file_path)

# Store:
self._table_manager = table_manager  # NEW
```

**File Saving:**
```python
# OLD:
create_odt_from_html(self._translated_html, self._css_manager, output_path, image_mgr)

# NEW:
table_mgr = getattr(self, '_table_manager', None)
create_odt_from_html(self._translated_html, self._css_manager, output_path, image_mgr, table_mgr)
```

---

## Phase 2.5: Testing (1 hour)

### Create test_odt_tables_COM8.py

**Test Flow:**
1. Create test ODT with 2×2 table
2. Extract HTML and tables
3. Verify table count and structure
4. Simulate translation
5. Restore to ODT
6. Verify tables preserved

**Expected Output:**
```
✓ Extraction: 1 table found (2×2)
✓ HTML markers: data-table="TBL001" detected
✓ Translation: simulated
✓ Restoration: ODT created
✓ Verification: Table structure matches
✓ SUCCESS: All tables preserved!
```

---

## Phase 2.6: Documentation & Commit (30 min)

### Create PHASE2_ODT_TABLES_COMPLETE_COM8.md

Document:
- Implementation summary
- Architecture details
- Test results
- Comparison with DOCX tables
- Files modified

### Git Commit

```
Phase 2 Complete: ODT Table Preservation - COM8

Implemented table preservation for ODT files following Phase 1 image pattern.

- Created ODTTableData and ODTTableManager
- Modified extract_html_from_odt() to detect table:table elements
- Added _extract_table() helper function
- Updated create_odt_from_html() to restore tables
- Enhanced HTMLToODTParser for data-table markers
- Updated GUI integration (google_translate_dock.py)
- Created test_odt_tables_COM8.py with full workflow test

Test Result: ✓ SUCCESS - All tables preserved!

Protocol: SIMPLICITY_PROTOCOL_3.md
Programmer: COM8
```

---

## Time Estimates

- **Phase 2.1:** Research & Design - ✅ Complete (30 min)
- **Phase 2.2:** Table Extraction - 1-2 hours
- **Phase 2.3:** Table Restoration - 1-2 hours  
- **Phase 2.4:** Integration - 30 min
- **Phase 2.5:** Testing - 1 hour
- **Phase 2.6:** Documentation - 30 min

**Total:** 5-7 hours

---

## Next Session Start

Begin with Phase 2.2.1: Create ODTTableData dataclass

**Command:** Proceed to implementation
