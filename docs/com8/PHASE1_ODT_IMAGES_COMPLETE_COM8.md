# Phase 1 Complete: ODT Image Support - COM8

## Summary
Successfully implemented image preservation for ODT files in Google Translate tool. Images are now extracted, preserved through translation, and restored to the output ODT file.

## Implementation Date
January 23, 2026

## Status
✅ **COMPLETE** - All phases implemented and tested

---

## Changes Made

### 1. Core Translation Layer (`src/translation/html_format_mapper.py`)

#### Added Classes:
- **`ODTImageData`** (dataclass, lines ~251-274)
  - Stores image metadata: ID, blob, format, dimensions
  - Similar to DOCX `ImageData` but adapted for ODF format

- **`ODTImageManager`** (class, lines ~277-388, ~140 lines)
  - Manages image storage with deduplication via SHA256 hashing
  - Sequential ID generation: IMG001, IMG002, IMG003...
  - Memory tracking (warns at >100MB)
  - Methods: `add_image()`, `get_image()`, `generate_placeholder()`, `get_statistics()`, `clear()`

#### Modified Functions:

**`extract_html_from_odt()`** (lines ~399-506)
- **Changed signature:** Returns `(html, css_manager, image_manager)` instead of `(html, css_manager)`
- Extracts images from ODT's Pictures/ folder before content parsing
- Stores images in ImageManager with deduplication
- Maps ODF image references to ImageManager IDs

**`_extract_paragraph()`** (line ~520+)
- **Changed signature:** Accepts `image_manager` parameter
- Detects `draw:frame` elements containing images
- Maps `Pictures/filename.ext` hrefs to `IMG###` IDs
- Inserts HTML placeholders: `<span data-image="IMG001"></span>`

**`_generate_html()`** (line ~859+)
- Handles `tag_type='image'` segments
- Generates HTML image markers for Google Translate preservation

**`create_odt_from_html()`** (lines ~951+)
- **Changed signature:** Accepts optional `image_manager` parameter
- Passes image_manager to HTMLToODTParser
- After saving ODT, reopens as ZIP and writes images to Pictures/ folder
- Creates proper ODF `draw:frame` and `draw:image` elements

**`HTMLToODTParser`** (class, lines ~1115+)
- **Changed `__init__`:** Accepts `image_manager` parameter
- **Enhanced `handle_starttag()`:** Detects `data-image` attributes
- **Added image segment handling:** Creates `type='image'` segments with metadata
- During ODT generation, converts image segments to proper ODF frame elements

### 2. GUI Layer (`src/gui/google_translate_dock.py`)

#### Modified Methods:

**File Loading** (lines ~533-542, ~676-684)
- Updated 2 locations where `extract_html_from_odt()` is called
- Now receives 3-tuple: `html_content, css_manager, image_manager`
- Stores `self._image_manager` for later use

**File Saving** (line ~1218-1224)
- Updated `_save_as_odt()` method
- Passes `image_manager` to `create_odt_from_html()`
- Uses `getattr(self, '_image_manager', None)` for backward compatibility

---

## Technical Details

### Image Extraction Process
1. Open ODT as ZIP file
2. Extract all files from `Pictures/` folder
3. For each image:
   - Calculate SHA256 hash for deduplication
   - Generate sequential ID (IMG001, IMG002, ...)
   - Store blob, format, dimensions in ImageManager
4. During paragraph parsing:
   - Detect `<draw:frame><draw:image xlink:href="Pictures/..."/></draw:frame>`
   - Map href to ImageManager ID
   - Insert HTML placeholder: `<span data-image="IMG###"></span>`

### Image Restoration Process
1. Parse translated HTML
2. Detect `<span data-image="IMG###"></span>` markers
3. Retrieve image blob from ImageManager
4. Create ODF `draw:frame` element with original dimensions
5. Add `draw:image` element with href="Pictures/IMG###.{ext}"
6. After saving ODT, reopen as ZIP
7. Write image blobs to Pictures/ folder

### Deduplication Logic
- Uses SHA256 hash of image blob data
- If same image appears multiple times, stored only once
- Different IDs reference same blob
- Reduces memory usage for documents with repeated images

### Dimensions
- ODF uses centimeters (cm) for dimensions
- Default: 7.62cm × 5.08cm (3in × 2in)
- Extracted from `svg:width` and `svg:height` attributes if available
- Preserved through translation workflow

---

## Testing

### Test Script: `test_odt_images_COM8.py`
- Creates test ODT with embedded 1×1 red pixel PNG (70 bytes)
- Tests full workflow: Extract → Translate → Save
- Verifies:
  - Image count matches
  - Image data integrity (byte-for-byte comparison)
  - Pictures/ folder created in output ODT
  - HTML markers preserved through translation

### Test Results:
```
✓ Extraction successful: 1 image, 70 bytes
✓ Image markers found in HTML: 1
✓ ODT created successfully
✓ Images verified in output: 1 file
✓ Data integrity: All images match
✓ SUCCESS - All images preserved!
```

---

## Architecture Notes

### Why HTML Placeholders?
Google Translate preserves HTML structure and attributes. By using `<span data-image="IMG001"></span>`, we:
1. Keep track of image positions through translation
2. Avoid sending binary data to Google
3. Maintain proper document structure

### Backward Compatibility
- Old code without image_manager still works (parameter is optional)
- Uses `getattr(self, '_image_manager', None)` in GUI
- Falls back gracefully if no images present

### Memory Management
- ImageManager tracks total memory usage
- Warns if >100MB stored
- Provides `clear()` method for cleanup
- Statistics available via `get_statistics()`

---

## Comparison: DOCX vs ODT

| Feature | DOCX | ODT |
|---------|------|-----|
| Image Manager | ✅ ImageManager | ✅ ODTImageManager |
| Deduplication | ✅ SHA256 | ✅ SHA256 |
| HTML Markers | ✅ data-image | ✅ data-image |
| Storage Location | word/media/ | Pictures/ |
| Format | OOXML | ODF |
| Frame Element | w:drawing | draw:frame |
| Dimensions | EMUs (English Metric Units) | cm (centimeters) |

---

## Files Modified

1. `src/translation/html_format_mapper.py` (+150 lines approx.)
2. `src/gui/google_translate_dock.py` (+6 lines, 3 locations)

## Files Created

1. `test_odt_images_COM8.py` - Image preservation test script
2. `docs/com8/PHASE1_ODT_IMAGES_COMPLETE_COM8.md` - This document

---

## Next Steps (Phase 2 - Tables)

Following the same pattern for table preservation:
1. Create ODTTableManager (similar to ImageManager)
2. Detect `table:table` elements
3. Convert to HTML `<table>` with data-table markers
4. Restore tables from markers after translation
5. Preserve table formatting (borders, cell styles, etc.)

**Estimated time:** 5-7 hours (similar to images)

---

## Lessons Learned

1. **ODF Structure:** Images in ODF use nested `draw:frame` → `draw:image` structure
2. **ZIP Manipulation:** Must reopen ODT to add Pictures/ files after odfpy save
3. **Testing Critical:** Creating test ODT with actual image essential for validation
4. **Pattern Reusability:** DOCX image pattern translated well to ODT
5. **Debugging Output:** Print statements in extraction helped track image flow

---

## Acknowledgments

- Protocol: SIMPLICITY_PROTOCOL_3.md
- Pattern reference: `docx_html_mapper.py` ImageManager implementation
- Test file: Created programmatically with odfpy + zipfile

---

**Phase 1 Status:** ✅ **COMPLETE AND TESTED**
**Ready for:** Git commit and Phase 2 (Tables)
