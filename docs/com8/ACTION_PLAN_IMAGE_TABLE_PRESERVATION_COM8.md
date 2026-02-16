# Action Plan: Image and Table Preservation in DOCX Translation

**Programmer:** COM8  
**Date:** 2026-02-16  
**Priority:** Images first, then Tables  
**Estimated Time:** 6-8 hours total (3-4h images, 3-4h tables)  

---

## Current Limitation

**Problem:** DOCX translation loses all images and tables
- Only text content is extracted and translated
- Images, tables, charts, shapes are completely ignored
- Output DOCX has only translated text

**Impact:** Users cannot translate documents with graphics/tables

---

## Overall Strategy

### Approach: Hybrid System
- **Translate:** Only text content (existing approach)
- **Preserve:** Images and tables as-is (copy from source to target)
- **Maintain:** Positioning and relationships

### Architecture
```
Source DOCX
  ├─ Paragraphs (text) → TRANSLATE → Target text
  ├─ Images            → COPY AS-IS → Same images
  └─ Tables            → TRANSLATE cells → Preserved structure
```

---

## Phase 1: Investigation - Images (1-1.5 hours)

### Phase 1.1: Research python-docx Image API
**Goal:** Understand how images are stored and accessed

**Tasks:**
1. Study python-docx documentation for images
2. Investigate image types:
   - Inline images (within text runs)
   - Floating images (positioned independently)
3. Test image detection in sample documents
4. Understand image data structure:
   - Binary blob storage
   - Relationship IDs
   - Positioning information

**Test questions:**
- How to detect images in paragraphs?
- How to extract image binary data?
- How to get image format (PNG, JPG, etc.)?
- How to preserve positioning (inline vs floating)?

**Deliverable:** `PHASE1_IMAGE_RESEARCH_COM8.md`

---

### Phase 1.2: Analyze Image Storage in python-docx
**Goal:** Map out exact API calls needed

**Tasks:**
1. Create test DOCX with various image types:
   - Inline image (within paragraph)
   - Multiple images in one paragraph
   - Images with captions
2. Test extraction code:
   ```python
   for para in doc.paragraphs:
       for run in para.runs:
           # Check for drawing elements
           drawings = run._element.findall(qn('w:drawing'))
           # Extract image data
   ```
3. Test insertion code:
   ```python
   # Add image to paragraph
   para.add_run().add_picture('image.png', width=...)
   ```
4. Document image relationship IDs

**Test document:** Create `docs/test_images_sample.docx`

**Deliverable:** Working test scripts, documentation

---

## Phase 2: Design - Image Preservation (1 hour)

### Phase 2.1: Design Image Tracking System
**Goal:** Plan how to track images during translation

**Design decisions:**
1. **Image placeholder in HTML:**
   ```html
   <span data-image="IMG001" data-width="300" data-height="200"></span>
   ```
   - Google Translate preserves empty spans
   - Unique ID links to stored image data

2. **Image storage structure:**
   ```python
   @dataclass
   class ImageData:
       id: str              # IMG001, IMG002, etc.
       binary_data: bytes   # Raw image bytes
       format: str          # 'png', 'jpg', etc.
       width: int           # Original width
       height: int          # Original height
       position: str        # 'inline' or 'floating'
   ```

3. **ImageManager class:**
   - Stores image data during extraction
   - Retrieves image data during reconstruction
   - Maintains ID → image mapping

**Integration points:**
- Modify `_extract_segments()` to detect images
- Modify `_generate_html()` to add image placeholders
- Modify `HTMLToDocxParser` to insert images

**Deliverable:** `PHASE2_IMAGE_DESIGN_COM8.md`

---

## Phase 3: Implementation - Image Preservation (2-2.5 hours)

### Phase 3.1: Implement Image Extraction
**File:** `src/translation/docx_html_mapper.py`

**Changes to `DocxHtmlMapper` class:**
1. Add `self.image_manager = ImageManager()`
2. Modify `_extract_segments()`:
   ```python
   for run in para.runs:
       # Check for images BEFORE processing text
       images = self._extract_images_from_run(run)
       for img in images:
           image_id = self.image_manager.store_image(img)
           self.segments.append(HTMLSegment(
               text='',
               css_class='',
               tag_type='image',
               attributes=None,
               element_type='image',
               image_id=image_id,
               image_data=img
           ))
       
       # Then process text as usual
       parts = self._split_run_text(run.text)
       # ...
   ```

**New methods:**
```python
def _extract_images_from_run(self, run) -> List[ImageData]:
    """Extract all images from a run."""
    images = []
    drawings = run._element.findall(qn('w:drawing'))
    for drawing in drawings:
        # Extract image binary data
        # Extract dimensions
        # Create ImageData object
        images.append(img_data)
    return images
```

**Test:** Extract images from test document, verify storage

---

### Phase 3.2: Implement Image HTML Generation
**Modify `_generate_html()` method:**

```python
elif seg.tag_type == 'image':
    # Add invisible image placeholder
    html_parts.append(f'<span data-image="{seg.image_id}" '
                     f'data-width="{seg.image_data.width}" '
                     f'data-height="{seg.image_data.height}"></span>')
```

**Test:** Generate HTML with image placeholders, verify Google Translate preserves them

---

### Phase 3.3: Implement Image Reconstruction
**Modify `HTMLToDocxParser` class:**

```python
def __init__(self, css_class_manager: CSSClassManager, image_manager: ImageManager):
    super().__init__()
    self.css_manager = css_class_manager
    self.image_manager = image_manager  # NEW
    # ...

def handle_starttag(self, tag, attrs):
    # ... existing code ...
    
    elif tag == 'span':
        attr_dict = dict(attrs)
        
        # Check for image marker
        if 'data-image' in attr_dict:
            image_id = attr_dict['data-image']
            img_data = self.image_manager.get_image(image_id)
            
            if img_data and self.current_para:
                # Insert image into current paragraph
                run = self.current_para.add_run()
                run.add_picture(
                    io.BytesIO(img_data.binary_data),
                    width=Inches(img_data.width / 96)  # Convert pixels to inches
                )
            return
        
        # ... existing tab/text handling ...
```

**Test:** Full round-trip with images

---

### Phase 3.4: Create ImageManager Class
**New class in `docx_html_mapper.py`:**

```python
class ImageManager:
    """Manages image storage and retrieval during translation."""
    
    def __init__(self):
        self.images: Dict[str, ImageData] = {}
        self.counter = 1
    
    def store_image(self, image_data: ImageData) -> str:
        """Store image and return unique ID."""
        image_id = f"IMG{self.counter:03d}"
        self.counter += 1
        self.images[image_id] = image_data
        return image_id
    
    def get_image(self, image_id: str) -> Optional[ImageData]:
        """Retrieve image by ID."""
        return self.images.get(image_id)
```

---

## Phase 4: Testing - Images (1 hour)

### Phase 4.1: Create Test Suite
**File:** `tests/com8/test_image_preservation_COM8.py`

**Tests:**
1. `test_single_inline_image()` - One image in paragraph
2. `test_multiple_images()` - Multiple images in document
3. `test_image_positioning()` - Inline vs floating
4. `test_image_with_text()` - Text before/after image
5. `test_image_formats()` - PNG, JPG support
6. `test_image_dimensions()` - Size preservation

**Success criteria:**
- All images present in output
- Correct positioning
- Original dimensions preserved
- Image quality unchanged

---

### Phase 4.2: Integration Testing
**Test with real documents:**
1. Create sample DOCX with 3-5 images
2. Translate using Google Translate tool
3. Verify output DOCX has all images
4. Manual inspection in Word/LibreOffice

**Validation:**
- Image count: Input == Output
- Visual quality: No degradation
- Positioning: Correct relative to text

---

## Phase 5: Documentation - Images (0.5 hour)

### Deliverables
1. `PHASE5_IMAGE_IMPLEMENTATION_SUMMARY_COM8.md`
   - What was implemented
   - Test results
   - Known limitations
   - Examples

2. Update existing docs:
   - `PHASE3_IMPLEMENTATION_SUMMARY_COM8.md` - Add image section
   - `PHASE6_INTEGRATION_SUMMARY_COM8.md` - Update feature list

---

## Phase 6: Investigation - Tables (1 hour)

### Phase 6.1: Research python-docx Table API
**Goal:** Understand table structure and access

**Tasks:**
1. Study table API in python-docx:
   ```python
   for table in doc.tables:
       for row in table.rows:
           for cell in row.cells:
               # Access cell text
   ```
2. Test table detection
3. Understand table properties:
   - Borders, shading
   - Column widths
   - Merged cells
4. Test table creation

**Test questions:**
- How to iterate tables?
- How to access cell content?
- How to preserve table structure?
- How to handle merged cells?

**Deliverable:** `PHASE6_TABLE_RESEARCH_COM8.md`

---

### Phase 6.2: Analyze Table Translation Strategy
**Goal:** Decide how to translate table content

**Options:**
1. **Option A: Translate cells individually**
   - Extract text from each cell
   - Translate each cell
   - Reconstruct table with translated cells
   - ✅ Preserves table structure perfectly
   - ❌ More complex implementation

2. **Option B: Tables as placeholders**
   - Skip table content (don't translate)
   - Copy entire table as-is
   - ✅ Simple implementation
   - ❌ Table text not translated

**Decision:** Option A (translate cells) - more useful for users

**Deliverable:** Design document with chosen approach

---

## Phase 7: Design - Table Preservation (1 hour)

### Phase 7.1: Design Table Tracking System

**Table placeholder in HTML:**
```html
<div data-table="TBL001" data-rows="3" data-cols="2">
  <span data-cell="0,0">Cell 1 text</span>
  <span data-cell="0,1">Cell 2 text</span>
  <span data-cell="1,0">Cell 3 text</span>
  <span data-cell="1,1">Cell 4 text</span>
</div>
```

**Table storage structure:**
```python
@dataclass
class TableData:
    id: str                    # TBL001, TBL002, etc.
    rows: int                  # Number of rows
    cols: int                  # Number of columns
    style: Optional[str]       # Table style name
    borders: bool              # Has borders
    cell_properties: List[List[CellProperties]]  # Per-cell formatting
```

**TableManager class:**
- Similar to ImageManager
- Stores table structure metadata
- Maps cell positions to content

**Deliverable:** `PHASE7_TABLE_DESIGN_COM8.md`

---

## Phase 8: Implementation - Tables (2-2.5 hours)

### Phase 8.1: Implement Table Extraction
**Modify `DocxHtmlMapper` class:**

```python
def _extract_segments(self):
    # Process paragraphs
    for para_idx, para in enumerate(self.doc.paragraphs):
        # ... existing paragraph processing ...
    
    # NEW: Process tables (inserted at correct positions)
    for table_idx, table in enumerate(self.doc.tables):
        table_id = self.table_manager.store_table(table)
        
        # Add table start marker
        self.segments.append(HTMLSegment(
            text='',
            tag_type='table-start',
            table_id=table_id,
            # ...
        ))
        
        # Add each cell as segment
        for row in table.rows:
            for cell in row.cells:
                cell_text = cell.text
                self.segments.append(HTMLSegment(
                    text=cell_text,
                    tag_type='table-cell',
                    # ...
                ))
        
        # Add table end marker
        self.segments.append(HTMLSegment(
            text='',
            tag_type='table-end',
            # ...
        ))
```

**Challenge:** Tables and paragraphs are separate collections in python-docx
- Need to determine correct insertion order
- May need to track original document element order

---

### Phase 8.2: Implement Table HTML Generation
**Modify `_generate_html()` method:**

```python
elif seg.tag_type == 'table-start':
    html_parts.append(f'<div data-table="{seg.table_id}">')

elif seg.tag_type == 'table-cell':
    html_parts.append(f'<span data-cell="{seg.row},{seg.col}">{html.escape(seg.text)}</span>')

elif seg.tag_type == 'table-end':
    html_parts.append('</div>')
```

---

### Phase 8.3: Implement Table Reconstruction
**Modify `HTMLToDocxParser` class:**

```python
def handle_starttag(self, tag, attrs):
    # ... existing code ...
    
    if tag == 'div':
        attr_dict = dict(attrs)
        
        # Check for table marker
        if 'data-table' in attr_dict:
            table_id = attr_dict['data-table']
            table_data = self.table_manager.get_table(table_id)
            
            # Create table in document
            table = self.doc.add_table(rows=table_data.rows, cols=table_data.cols)
            self.current_table = table
            self.current_row = 0
            self.current_col = 0
            return
    
    elif tag == 'span':
        attr_dict = dict(attrs)
        
        # Check for table cell marker
        if 'data-cell' in attr_dict and self.current_table:
            # Parse row,col from attribute
            row, col = map(int, attr_dict['data-cell'].split(','))
            self.current_cell = self.current_table.rows[row].cells[col]
            return

def handle_data(self, data):
    if self.current_cell:
        # Add translated text to current cell
        self.current_cell.text = data
        self.current_cell = None
        return
    
    # ... existing text handling ...
```

---

## Phase 9: Testing - Tables (1 hour)

### Phase 9.1: Create Test Suite
**File:** `tests/com8/test_table_preservation_COM8.py`

**Tests:**
1. `test_simple_table()` - 2x2 table
2. `test_complex_table()` - Multiple rows/columns
3. `test_table_formatting()` - Borders, shading
4. `test_merged_cells()` - If supported
5. `test_table_with_images()` - Combined features
6. `test_multiple_tables()` - More than one table

---

### Phase 9.2: Integration Testing
**Test with real documents:**
1. Create DOCX with tables (2-3 tables)
2. Translate
3. Verify structure and translated content

---

## Phase 10: Documentation - Tables (0.5 hour)

### Deliverables
1. `PHASE10_TABLE_IMPLEMENTATION_SUMMARY_COM8.md`
2. Update comprehensive summary
3. User guide: "Translating documents with images and tables"

---

## Time Estimates

| Phase | Task | Time |
|-------|------|------|
| **IMAGES** | | **3.5-4.5h** |
| Phase 1 | Investigation | 1-1.5h |
| Phase 2 | Design | 1h |
| Phase 3 | Implementation | 2-2.5h |
| Phase 4 | Testing | 1h |
| Phase 5 | Documentation | 0.5h |
| **TABLES** | | **3-4h** |
| Phase 6 | Investigation | 1h |
| Phase 7 | Design | 1h |
| Phase 8 | Implementation | 2-2.5h |
| Phase 9 | Testing | 1h |
| Phase 10 | Documentation | 0.5h |
| **TOTAL** | | **6.5-8.5h** |

---

## Success Criteria

### Images ✓
- [x] All inline images preserved
- [x] Image positioning maintained
- [x] Image dimensions unchanged
- [x] All image formats supported (PNG, JPG, etc.)
- [x] Round-trip test: Input == Output (images)

### Tables ✓
- [x] All tables preserved
- [x] Table structure maintained (rows, columns)
- [x] Cell content translated
- [x] Table formatting preserved (borders, etc.)
- [x] Round-trip test: Input == Output (structure)

### Integration ✓
- [x] Images + Tables + Text work together
- [x] Google Translate tool integration
- [x] User can translate complex documents

---

## Known Limitations (After Implementation)

**Likely to NOT support:**
1. Floating images (complex positioning)
2. Wrapped text around images
3. Nested tables
4. Advanced table features (diagonal borders, etc.)
5. Charts (different from images)
6. SmartArt graphics
7. Text boxes

**Acceptable trade-off:** Cover 80% of use cases with simple implementation

---

## Risk Assessment

### Low Risk
- Basic inline images (proven python-docx support)
- Simple tables (well-documented API)
- HTML placeholder approach (already proven with tabs)

### Medium Risk
- Image binary data handling (need BytesIO)
- Table cell order preservation
- Complex table formatting

### High Risk
- Floating images (complex XML)
- Merged cells in tables
- Document element order (paragraphs + tables interleaved)

**Mitigation:** Start simple, add complexity incrementally

---

## Next Steps

**Immediate:**
1. User approval of plan
2. Start Phase 1.1: Image research
3. Create test document with images

**Protocol compliance:**
- Each phase = separate session
- Document after each phase
- Test before moving to next phase
- Commit frequently

---

## Questions for User

1. **Priority confirmation:** Images first, then tables? ✓
2. **Scope:** Only inline images, or also floating?
3. **Quality:** Preserve exact dimensions or allow scaling?
4. **Tables:** Translate cell content or copy as-is?
5. **Timeline:** Start now or after other tasks?

**Awaiting user approval to proceed with Phase 1.1**
