# Phase 1.1: Image API Research - COM8

**Date:** 2026-02-16  
**Programmer:** COM8  
**Task:** Research python-docx image API for DOCX translation preservation  
**Status:** ✅ COMPLETE  
**Duration:** 45 minutes

---

## Objective

Investigate how python-docx handles images to design preservation strategy for Google Translate tool.

**Requirements:**
1. Understand how images are stored in DOCX files
2. Learn how to detect and extract images from runs
3. Access image binary data (blob)
4. Get image dimensions and format
5. Test image reconstruction from blob

---

## Test Setup

### Test Document Created

**File:** `docs/test_with_images_COM8.docx`

**Structure:**
- 6 paragraphs total
- 2 images:
  - Image 1: Inline in paragraph 2 (1.0" x 0.5")
  - Image 2: Standalone in paragraph 4 (2.0" x 1.0")
- Text before, between, and after images

**Test Image:** Simple PNG with blue rectangle and "TEST IMAGE" text (1236 bytes)

### Verification

```
Paragraph 0: 'Image Preservation Test Document' (heading)
Paragraph 1: 'This is a paragraph before the first image.'
Paragraph 2: 'Here is an inline image: [IMAGE] after the image.'  ← Image 1 inline
Paragraph 3: 'This is another paragraph with regular text.'
Paragraph 4: [IMAGE]                                              ← Image 2 standalone
Paragraph 5: 'This is the final paragraph after the second image.'
```

---

## Research Findings

### 1. Image Storage in DOCX

**Key Discovery:** Images are stored as `w:drawing` elements inside runs.

**Document Structure:**
```
Document
  └─ Paragraph
      └─ Run
          └─ run._element (XML)
              └─ w:drawing (one or more)
                  └─ Inline/Anchor shape
                      └─ a:blip (image reference)
                          └─ r:embed attribute → relationship ID
```

**Important:** Even though image appears in text, `run.text` is empty string for image runs!

### 2. Image Detection

**Method 1: Find all drawings in a run**

```python
drawings = run._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
if drawings:
    # Run contains one or more images
    for drawing in drawings:
        # Process each image
```

**Namespace:** `http://schemas.openxmlformats.org/wordprocessingml/2006/main` (w:)

**Observation:** One run can contain multiple images (rare but possible).

### 3. Image Data Extraction

**Step-by-Step Process:**

```python
from docx import Document

doc = Document('file.docx')

for para in doc.paragraphs:
    for run in para.runs:
        # 1. Find drawings
        drawings = run._element.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
        
        for drawing in drawings:
            # 2. Find blip (image reference)
            blips = drawing.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
            
            if blips:
                blip = blips[0]
                
                # 3. Get relationship ID
                embed_attr = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
                embed_id = blip.get(embed_attr)  # e.g., 'rId9'
                
                # 4. Get ImagePart from document relationships
                image_part = doc.part.related_parts[embed_id]
                
                # 5. Extract image data
                image_blob = image_part.blob            # bytes (PNG/JPEG/GIF data)
                content_type = image_part.content_type  # 'image/png', 'image/jpeg', etc.
                part_name = image_part.partname         # '/word/media/image1.png'
```

**Namespaces Used:**
- `w:` → `http://schemas.openxmlformats.org/wordprocessingml/2006/main`
- `a:` → `http://schemas.openxmlformats.org/drawingml/2006/main`
- `r:` → `http://schemas.openxmlformats.org/officeDocument/2006/relationships`

### 4. Image Metadata

**Format Detection:**

```python
content_type = image_part.content_type

if 'png' in content_type:
    format = 'png'
elif 'jpeg' in content_type:
    format = 'jpg'
elif 'gif' in content_type:
    format = 'gif'
else:
    format = 'unknown'
```

**Common Content Types:**
- `image/png` → PNG format
- `image/jpeg` → JPEG format
- `image/gif` → GIF format
- `image/tiff` → TIFF format (rare)

**Binary Signature Detection:**

```python
blob = image_part.blob

# PNG: starts with 0x89504e47
if blob[:4].hex() == '89504e47':
    format = 'png'

# JPEG: starts with 0xffd8ff
elif blob[:3].hex().startswith('ffd8ff'):
    format = 'jpg'
```

### 5. Image Dimensions

**Location:** `wp:extent` element inside `w:drawing`

**Extraction:**

```python
# Find extent element
extents = drawing.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent')

if extents:
    ext = extents[0]
    cx = ext.get('cx')  # Width in EMUs (English Metric Units)
    cy = ext.get('cy')  # Height in EMUs
    
    # Convert EMUs to inches
    # 914400 EMUs = 1 inch
    width_inches = int(cx) / 914400
    height_inches = int(cy) / 914400
```

**Namespace:** `http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing` (wp:)

**EMU (English Metric Units):**
- 914400 EMUs = 1 inch
- 36000 EMUs = 1 point
- 12700 EMUs = 1 pixel (at 72 DPI)

**Test Results:**
- Image 1: 914400 x 457200 EMUs = 1.00" x 0.50"
- Image 2: 1828800 x 914400 EMUs = 2.00" x 1.00"

### 6. Image Reconstruction

**Critical Test:** Can we rebuild image from extracted blob?

**Method:**

```python
from io import BytesIO
from docx import Document

# Extract blob (see above)
image_blob = image_part.blob

# Create new document
new_doc = Document()
p = new_doc.add_paragraph("Text: ")
run = p.add_run()

# Add image from BytesIO stream
image_stream = BytesIO(image_blob)
run.add_picture(image_stream, width=Inches(1.0))

new_doc.save('reconstructed.docx')
```

**Result:** ✅ **SUCCESS!**
- Image perfectly reconstructed from blob
- No quality loss
- Dimensions preserved (or resizable with `width`/`height` parameters)

**Test File:** `docs/test_reconstructed_COM8.docx` (verified manually)

---

## Key Insights

### Image Handling in python-docx

1. **Images are NOT in run.text**
   - `run.text` returns empty string for image runs
   - Must detect via `run._element` XML inspection

2. **One run = One or more images**
   - Typically one image per run
   - Multiple images in same run are possible (rare)

3. **Binary data is accessible**
   - `image_part.blob` gives raw PNG/JPEG/GIF bytes
   - No conversion needed → direct storage in memory

4. **Dimensions are flexible**
   - Original dimensions stored in `wp:extent`
   - Can resize during reconstruction with `width=` parameter
   - Aspect ratio maintained if only width OR height specified

5. **Relationship-based storage**
   - Images stored separately in `/word/media/` folder
   - Runs reference images via relationship ID (rId9, rId10, etc.)
   - Multiple runs can reference SAME image (rId9 appears twice in test)
   - → Need to track unique image parts, not just relationship IDs

### Translation Challenges

**Problem:** Google Translate must preserve image positions.

**Solution Strategy:**
1. Replace images with HTML placeholders during extraction
2. Store image blobs in memory with unique IDs
3. After translation, replace placeholders with reconstructed images

**HTML Placeholder Design:**

```html
<span data-image="IMG001"></span>
```

**Why this works:**
- Empty span → Google won't translate content (no content!)
- `data-image` attribute → Google preserves data-* attributes
- Invisible to user → No visual artifacts in translation

**Storage:**

```python
{
    'IMG001': {
        'blob': b'\x89PNG...',           # Binary data
        'content_type': 'image/png',     # Format
        'width_emus': 914400,            # Original width
        'height_emus': 457200,           # Original height
        'rId': 'rId9'                    # Original relationship ID
    }
}
```

---

## Comparison: Images vs Tabs/Linebreaks

### Similarities

- Both are XML elements inside runs
- Both need HTML placeholders
- Both preserved by Google Translate via HTML

### Differences

| Aspect | Tabs/Linebreaks | Images |
|--------|----------------|--------|
| Storage | Characters in `run.text` | Separate binary parts |
| Detection | Parse text string | XML element search |
| Size | 1 byte each | 1KB-1MB+ each |
| Reconstruction | Insert `\t` or `\n` | Create new relationship + add binary |
| HTML marker | `<span data-tab="1">` | `<span data-image="IMG001">` |
| Memory | Negligible | Need blob storage |

**Complexity:** Images are significantly more complex than tabs due to:
1. Binary data management (memory overhead)
2. Relationship management (document.part.rels)
3. Multiple formats (PNG, JPEG, GIF, TIFF)
4. Dimension preservation (EMU calculations)

---

## API Cheat Sheet

### Namespaces

```python
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}
```

### Detection

```python
drawings = run._element.findall(f'.//{{{NS["w"]}}}drawing')
```

### Extraction

```python
blips = drawing.findall(f'.//{{{NS["a"]}}}blip')
embed_id = blip.get(f'{{{NS["r"]}}}embed')
image_part = doc.part.related_parts[embed_id]
blob = image_part.blob
```

### Dimensions

```python
extents = drawing.findall(f'.//{{{NS["wp"]}}}extent')
width_emus = int(extents[0].get('cx'))
height_emus = int(extents[0].get('cy'))
```

### Reconstruction

```python
from io import BytesIO
stream = BytesIO(blob)
run.add_picture(stream, width=Inches(width_emus / 914400))
```

---

## Next Steps (Phase 1.2)

### Immediate Actions

1. **Design ImageManager class**
   - Storage: `{image_id: ImageData}` dictionary
   - Methods: `add_image()`, `get_image()`, `generate_placeholder()`

2. **Test edge cases:**
   - Multiple images in same paragraph
   - Very large images (>5MB)
   - Different formats (JPEG, GIF)
   - Images with captions/wrapping

3. **Integration planning:**
   - How to modify `_extract_segments()` to detect images?
   - Where to store ImageManager in DocxHtmlMapper?
   - How to pass images to translation flow?

### Questions to Answer

- Should we preserve original dimensions or allow resizing?
  → **Recommendation:** Preserve original (simpler, no quality issues)

- What if image relationship ID appears multiple times?
  → **Answer:** Store unique image_part.blob (deduplicate by content hash)

- What if image is corrupted or inaccessible?
  → **Strategy:** Log warning, skip image, continue with text

- Should we support floating images (not inline)?
  → **Phase 1 scope:** Inline only (most common case)

---

## Files Created/Modified

**Created:**
- `docs/test_image_COM8.png` (1236 bytes) - Simple test image
- `docs/test_with_images_COM8.docx` - Test document (2 images)
- `docs/test_reconstructed_COM8.docx` - Verification document
- `docs/com8/PHASE1_1_IMAGE_API_RESEARCH_COM8.md` (this file)

**Modified:** None

---

## Conclusion

**Status:** ✅ Phase 1.1 COMPLETE

**Key Achievement:** Proven that images can be extracted and reconstructed from blob data.

**Confidence Level:** HIGH
- API is well-documented
- Binary data access is straightforward
- Reconstruction works perfectly
- Only complexity is relationship management

**Risk Assessment:**
- **Low Risk:** Binary extraction, format detection, dimension preservation
- **Medium Risk:** Multiple images in same paragraph, memory management
- **High Risk:** Floating images, text wrapping, image positioning (out of scope for Phase 1)

**Ready for Phase 1.2:** ImageManager design

---

**Time Spent:** 45 minutes  
**Next Phase:** 1.2 (ImageManager Design) - Estimated 30-45 minutes
