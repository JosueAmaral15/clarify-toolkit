# Phase 1.2: ImageManager Design - COM8

**Date:** 2026-02-16  
**Programmer:** COM8  
**Task:** Design ImageManager class for image preservation in DOCX translation  
**Status:** ✅ COMPLETE  
**Duration:** 35 minutes

---

## Objective

Design ImageManager class to handle image storage, deduplication, and reconstruction during DOCX translation workflow.

**Requirements:**
1. Store image binary data with unique IDs
2. Handle multiple references to same image (deduplication)
3. Generate HTML placeholders for translation
4. Reconstruct images in output DOCX
5. Preserve dimensions and format
6. Handle errors gracefully (corrupted images)

---

## Architecture Overview

### Class Hierarchy

```
ImageManager
  ├─ ImageData (dataclass) - Stores single image metadata + blob
  └─ Methods:
      ├─ add_image() - Store image with auto-generated ID
      ├─ get_image() - Retrieve image by ID
      ├─ generate_placeholder() - Create HTML marker
      └─ get_statistics() - Debug info
```

### Integration Points

**Existing System:**
```
DocxHtmlMapper
  ├─ _extract_segments() ← ADD image detection here
  ├─ _generate_html() ← ADD placeholder generation here
  └─ _css_manager (existing)
```

**New System:**
```
DocxHtmlMapper
  ├─ _image_manager (NEW) - Instance of ImageManager
  ├─ _extract_segments() - Detect images, call _image_manager.add_image()
  └─ _generate_html() - Call _image_manager.generate_placeholder()

HTMLToDocxParser
  ├─ handle_starttag() - Detect data-image attribute
  └─ _reconstruct_image() (NEW) - Call _image_manager.get_image()
```

---

## ImageData Dataclass

### Purpose
Store all metadata for a single image.

### Design

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ImageData:
    """Stores image binary data and metadata."""
    
    image_id: str              # 'IMG001', 'IMG002', etc.
    blob: bytes                # Raw PNG/JPEG/GIF binary data
    content_type: str          # 'image/png', 'image/jpeg', etc.
    width_emus: int            # Width in EMUs (914400 = 1 inch)
    height_emus: int           # Height in EMUs
    original_rId: str          # Original relationship ID (e.g., 'rId9')
    blob_hash: Optional[str]   # SHA256 hash for deduplication
    
    def get_format(self) -> str:
        """Extract format from content_type."""
        if 'png' in self.content_type:
            return 'png'
        elif 'jpeg' in self.content_type:
            return 'jpg'
        elif 'gif' in self.content_type:
            return 'gif'
        else:
            return 'unknown'
    
    def get_width_inches(self) -> float:
        """Convert EMUs to inches."""
        return self.width_emus / 914400
    
    def get_height_inches(self) -> float:
        """Convert EMUs to inches."""
        return self.height_emus / 914400
```

### Fields Explained

- **image_id:** Unique identifier (IMG001, IMG002, etc.)
  - Auto-generated sequentially
  - Used in HTML placeholder: `<span data-image="IMG001">`

- **blob:** Binary image data
  - Raw bytes from `image_part.blob`
  - Can be MB-sized (memory concern!)

- **content_type:** MIME type
  - Examples: `image/png`, `image/jpeg`, `image/gif`
  - Used to detect format during reconstruction

- **width_emus / height_emus:** Dimensions in EMUs
  - Preserved from original document
  - 914400 EMUs = 1 inch
  - Used to maintain exact size in output

- **original_rId:** Relationship ID
  - For debugging only
  - Multiple ImageData may have same rId (shared image)

- **blob_hash:** SHA256 hash of blob
  - Used for deduplication
  - If two images have same hash → same binary data → reuse

---

## ImageManager Class

### Purpose
Central manager for all images in document translation.

### Design

```python
import hashlib
from typing import Dict, Optional
from io import BytesIO

class ImageManager:
    """Manages image storage and reconstruction for DOCX translation."""
    
    def __init__(self):
        """Initialize image storage."""
        self._images: Dict[str, ImageData] = {}  # image_id → ImageData
        self._hash_to_id: Dict[str, str] = {}    # blob_hash → image_id
        self._next_id: int = 1                   # Counter for IMG001, IMG002, etc.
    
    def add_image(self, blob: bytes, content_type: str, 
                  width_emus: int, height_emus: int, 
                  original_rId: str) -> str:
        """
        Add image to storage with deduplication.
        
        Returns:
            image_id: Unique ID for this image (e.g., 'IMG001')
        """
        # Calculate hash for deduplication
        blob_hash = hashlib.sha256(blob).hexdigest()
        
        # Check if image already exists (same binary data)
        if blob_hash in self._hash_to_id:
            existing_id = self._hash_to_id[blob_hash]
            print(f"[ImageManager] Deduplication: reusing {existing_id} for {original_rId}")
            return existing_id
        
        # Generate new ID
        image_id = f"IMG{self._next_id:03d}"  # IMG001, IMG002, etc.
        self._next_id += 1
        
        # Store image data
        image_data = ImageData(
            image_id=image_id,
            blob=blob,
            content_type=content_type,
            width_emus=width_emus,
            height_emus=height_emus,
            original_rId=original_rId,
            blob_hash=blob_hash
        )
        
        self._images[image_id] = image_data
        self._hash_to_id[blob_hash] = image_id
        
        print(f"[ImageManager] Stored {image_id}: {content_type}, "
              f"{width_emus / 914400:.2f}\" x {height_emus / 914400:.2f}\", "
              f"{len(blob)} bytes")
        
        return image_id
    
    def get_image(self, image_id: str) -> Optional[ImageData]:
        """
        Retrieve image by ID.
        
        Returns:
            ImageData if found, None otherwise
        """
        return self._images.get(image_id)
    
    def generate_placeholder(self, image_id: str) -> str:
        """
        Generate HTML placeholder for image.
        
        Returns:
            HTML string: '<span data-image="IMG001"></span>'
        """
        return f'<span data-image="{image_id}"></span>'
    
    def get_statistics(self) -> dict:
        """
        Get storage statistics for debugging.
        
        Returns:
            Dict with counts and memory usage
        """
        total_images = len(self._images)
        unique_blobs = len(self._hash_to_id)
        total_bytes = sum(len(img.blob) for img in self._images.values())
        
        return {
            'total_images': total_images,
            'unique_blobs': unique_blobs,
            'duplicates': total_images - unique_blobs,
            'total_bytes': total_bytes,
            'total_mb': total_bytes / (1024 * 1024)
        }
    
    def clear(self):
        """Clear all stored images (for memory management)."""
        self._images.clear()
        self._hash_to_id.clear()
        self._next_id = 1
```

### Methods Explained

#### add_image()

**Purpose:** Store image with automatic deduplication.

**Logic:**
1. Calculate SHA256 hash of blob
2. Check if hash already exists in `_hash_to_id`
3. If exists → return existing image_id (reuse)
4. If new → generate new ID, store ImageData, update mappings
5. Return image_id

**Example:**
```python
# First call with rId9
image_id = manager.add_image(blob, 'image/png', 914400, 457200, 'rId9')
# Returns: 'IMG001'

# Second call with rId10 but SAME blob
image_id = manager.add_image(blob, 'image/png', 1828800, 914400, 'rId10')
# Returns: 'IMG001' (deduplicated!)
```

**Deduplication Benefits:**
- Saves memory (one blob instead of two)
- Reduces output file size (single image in media/)
- Maintains consistency (same image → same ID)

#### get_image()

**Purpose:** Retrieve stored image by ID.

**Usage:**
```python
image_data = manager.get_image('IMG001')
if image_data:
    run.add_picture(BytesIO(image_data.blob), 
                    width=Inches(image_data.get_width_inches()))
```

**Returns:** ImageData object or None if not found.

#### generate_placeholder()

**Purpose:** Create HTML marker for translation.

**Output:** `<span data-image="IMG001"></span>`

**Why empty span?**
- No text content → Google Translate ignores
- `data-image` attribute → preserved by Google
- Invisible to user → no artifacts

**Integration:**
```python
# In _generate_html()
if segment.type == 'image':
    html_parts.append(self._image_manager.generate_placeholder(segment.image_id))
```

#### get_statistics()

**Purpose:** Debug and monitor memory usage.

**Output:**
```python
{
    'total_images': 5,        # Total images in document
    'unique_blobs': 3,        # Unique binary blobs
    'duplicates': 2,          # Deduplicated images
    'total_bytes': 2457600,   # Total memory (bytes)
    'total_mb': 2.34          # Total memory (MB)
}
```

**Use Case:** Warn user if document has very large images (>50MB total).

---

## Integration with DocxHtmlMapper

### Modified _extract_segments()

**Current:** Extracts text, tabs, linebreaks only.

**New:** Also detect and extract images.

```python
def _extract_segments(self, doc: Document) -> List[HTMLSegment]:
    """Extract document structure including images."""
    segments = []
    
    for para in doc.paragraphs:
        for run in para.runs:
            # Check for images FIRST (before text)
            drawings = run._element.findall('.//{http://...}drawing')
            
            if drawings:
                # Process each image
                for drawing in drawings:
                    # Extract image data (see Phase 1.1 research)
                    blip = drawing.findall('.//a:blip')[0]
                    embed_id = blip.get('{...}embed')
                    image_part = doc.part.related_parts[embed_id]
                    
                    # Get dimensions
                    extent = drawing.findall('.//wp:extent')[0]
                    width_emus = int(extent.get('cx'))
                    height_emus = int(extent.get('cy'))
                    
                    # Store in ImageManager
                    image_id = self._image_manager.add_image(
                        blob=image_part.blob,
                        content_type=image_part.content_type,
                        width_emus=width_emus,
                        height_emus=height_emus,
                        original_rId=embed_id
                    )
                    
                    # Add image segment
                    segments.append(HTMLSegment(
                        type='image',
                        content='',  # No text content
                        format=None,
                        image_id=image_id  # NEW field in HTMLSegment
                    ))
            
            # Then process text (existing logic)
            text_parts = self._split_run_text(run.text)
            for part in text_parts:
                # ... existing code ...
        
        # Paragraph break
        segments.append(HTMLSegment(type='para_break', ...))
    
    return segments
```

### Modified HTMLSegment Dataclass

**Add image_id field:**

```python
@dataclass
class HTMLSegment:
    """Represents a document element (text, tab, linebreak, image, etc.)."""
    
    type: str                          # 'text', 'tab', 'linebreak', 'image', etc.
    content: str                       # Text content (empty for images)
    format: Optional[FormatAttributes] # Text formatting (None for images)
    image_id: Optional[str] = None     # NEW: Image ID ('IMG001', etc.)
```

### Modified _generate_html()

**Add image placeholder generation:**

```python
def _generate_html(self, segments: List[HTMLSegment]) -> str:
    """Generate HTML from segments including images."""
    html_parts = ['<html><head>', self._css_manager.generate_css(), '</head><body>']
    
    for segment in segments:
        if segment.type == 'text':
            # ... existing text handling ...
        
        elif segment.type == 'tab':
            html_parts.append('<span data-tab="1"></span>')
        
        elif segment.type == 'linebreak':
            html_parts.append('<br class="brk2">')
        
        elif segment.type == 'image':
            # NEW: Generate image placeholder
            placeholder = self._image_manager.generate_placeholder(segment.image_id)
            html_parts.append(placeholder)
        
        elif segment.type == 'para_break':
            html_parts.append('<br class="brk1">')
    
    html_parts.append('</body></html>')
    return ''.join(html_parts)
```

---

## Integration with HTMLToDocxParser

### Modified handle_starttag()

**Add image detection:**

```python
def handle_starttag(self, tag, attrs):
    """Process HTML opening tags including images."""
    
    if tag == 'span':
        attrs_dict = dict(attrs)
        
        # Check for tab
        if 'data-tab' in attrs_dict:
            self.pending_tab = True
        
        # Check for image (NEW)
        elif 'data-image' in attrs_dict:
            image_id = attrs_dict['data-image']
            self._reconstruct_image(image_id)
        
        # Check for format class
        elif 'class' in attrs_dict:
            class_name = attrs_dict['class']
            fmt = self._css_manager.get_format(class_name)
            if fmt:
                self.current_format = fmt
    
    # ... rest of existing code ...
```

### New Method: _reconstruct_image()

```python
def _reconstruct_image(self, image_id: str):
    """Reconstruct image in DOCX from stored data."""
    
    # Get image data from ImageManager
    image_data = self._image_manager.get_image(image_id)
    
    if not image_data:
        print(f"[HTMLToDocxParser] WARNING: Image {image_id} not found, skipping")
        return
    
    # Create BytesIO stream from blob
    from io import BytesIO
    from docx.shared import Inches
    
    image_stream = BytesIO(image_data.blob)
    
    # Add image to current run
    if not self.current_run:
        # No current run → create new paragraph and run
        para = self.doc.add_paragraph()
        self.current_run = para.add_run()
        self.current_para = para
    
    # Add picture with original dimensions
    try:
        self.current_run.add_picture(
            image_stream,
            width=Inches(image_data.get_width_inches())
            # Height automatically calculated to maintain aspect ratio
        )
        print(f"[HTMLToDocxParser] Reconstructed {image_id} "
              f"({image_data.get_format()}, {image_data.get_width_inches():.2f}\")")
    
    except Exception as e:
        print(f"[HTMLToDocxParser] ERROR reconstructing {image_id}: {e}")
    
    # Create new run for next content (images end runs)
    self.current_run = None
```

**Key Points:**
- Images end runs (like linebreaks do)
- Create new run after image
- Preserve original dimensions (width only → aspect ratio maintained)
- Handle errors gracefully (log warning, continue)

---

## Constructor Changes

### DocxHtmlMapper.__init__()

**Add ImageManager initialization:**

```python
def __init__(self):
    """Initialize mapper with CSS and Image managers."""
    self._css_manager = CSSClassManager()
    self._image_manager = ImageManager()  # NEW
```

### HTMLToDocxParser.__init__()

**Pass ImageManager reference:**

```python
def __init__(self, html: str, css_manager: CSSClassManager, 
             image_manager: ImageManager):  # NEW parameter
    """Initialize parser with HTML, CSS manager, and Image manager."""
    super().__init__()
    self.html = html
    self._css_manager = css_manager
    self._image_manager = image_manager  # NEW
    # ... rest of initialization ...
```

### Public API Update: create_docx_from_html()

**Pass ImageManager to parser:**

```python
def create_docx_from_html(html: str, css_manager: CSSClassManager,
                          image_manager: ImageManager) -> Document:  # NEW param
    """Create DOCX document from translated HTML."""
    parser = HTMLToDocxParser(html, css_manager, image_manager)  # Pass manager
    parser.feed(html)
    return parser.doc
```

---

## Memory Management Strategy

### Challenge
Images can be large (1-10MB each). Documents with 50+ images could consume 500MB+ RAM.

### Solutions

#### 1. Lazy Loading (Future Enhancement)
Store only image references, load blob on-demand:
```python
@dataclass
class ImageData:
    image_path: str  # Path to temp file
    # Load blob only when needed
```

#### 2. Compression (Future Enhancement)
Compress blobs in memory:
```python
import gzip
compressed_blob = gzip.compress(blob)
# Decompress during reconstruction
```

#### 3. Size Warnings (Immediate)
```python
def add_image(self, blob: bytes, ...) -> str:
    # Check individual image size
    if len(blob) > 10 * 1024 * 1024:  # 10MB
        print(f"[ImageManager] WARNING: Large image ({len(blob) / 1024 / 1024:.1f}MB)")
    
    # ... store image ...
    
    # Check total memory usage
    stats = self.get_statistics()
    if stats['total_mb'] > 100:  # 100MB total
        print(f"[ImageManager] WARNING: High memory usage ({stats['total_mb']:.1f}MB)")
```

#### 4. Clear After Use
```python
# In google_translate_dock.py after save
mapper._image_manager.clear()  # Free memory
```

**Recommendation for Phase 1:** Implement size warnings only. Lazy loading is Phase 2 optimization.

---

## Error Handling

### Possible Errors

1. **Corrupted image data**
   - Symptom: `image_part.blob` raises exception
   - Solution: Try/except, log warning, skip image

2. **Missing relationship**
   - Symptom: `embed_id not in doc.part.related_parts`
   - Solution: Check `if embed_id in ...`, skip if missing

3. **Invalid dimensions**
   - Symptom: `cx or cy is None or zero`
   - Solution: Use default dimensions (1.0" x 1.0")

4. **Image reconstruction failure**
   - Symptom: `run.add_picture()` raises exception
   - Solution: Try/except, log error, continue

### Error Handling Pattern

```python
try:
    # Extract image
    blip = drawing.findall('.//a:blip')[0]
    embed_id = blip.get('{...}embed')
    
    if embed_id not in doc.part.related_parts:
        print(f"[ImageManager] WARNING: Missing relationship {embed_id}")
        continue
    
    image_part = doc.part.related_parts[embed_id]
    blob = image_part.blob
    
    # Validate dimensions
    extent = drawing.findall('.//wp:extent')[0]
    width_emus = int(extent.get('cx') or 914400)  # Default 1"
    height_emus = int(extent.get('cy') or 914400)
    
    # Store image
    image_id = self._image_manager.add_image(...)
    
except Exception as e:
    print(f"[DocxHtmlMapper] ERROR processing image: {e}")
    print(f"  Skipping image, continuing with text")
    # Skip this image, continue with next run
```

**Philosophy:** Fail gracefully. One corrupted image should not crash entire translation.

---

## Testing Strategy

### Unit Tests

**File:** `tests/com8/test_image_manager_COM8.py`

**Tests:**
1. `test_add_single_image()` - Basic storage
2. `test_deduplication()` - Same blob → same ID
3. `test_generate_placeholder()` - HTML output
4. `test_get_statistics()` - Memory tracking
5. `test_multiple_images()` - Sequential IDs (IMG001, IMG002, IMG003)
6. `test_get_nonexistent_image()` - Returns None gracefully
7. `test_clear()` - Memory cleanup

### Integration Tests

**File:** `tests/com8/test_docx_images_end_to_end_COM8.py`

**Test Document:** `docs/test_with_images_COM8.docx`

**Test Flow:**
1. Load document with 2 images
2. Extract HTML (should have 2 `<span data-image="...">` placeholders)
3. Verify ImageManager has 2 images stored (or 1 if deduplicated)
4. Translate HTML (identity translation for testing)
5. Reconstruct DOCX
6. Verify output has 2 images at correct positions
7. Verify dimensions preserved

**Success Criteria:**
- 2 images in output (same count as input)
- Images at correct positions (para 2 and para 4)
- Dimensions preserved (1.0" x 0.5" and 2.0" x 1.0")

---

## Summary

### Classes Designed

1. **ImageData** (dataclass)
   - Stores blob + metadata for one image
   - Methods: `get_format()`, `get_width_inches()`, `get_height_inches()`

2. **ImageManager** (class)
   - Central storage with deduplication
   - Methods: `add_image()`, `get_image()`, `generate_placeholder()`, `get_statistics()`, `clear()`

### Integration Points

1. **DocxHtmlMapper**
   - Add `_image_manager` instance
   - Modify `_extract_segments()` to detect images
   - Modify `_generate_html()` to add placeholders

2. **HTMLToDocxParser**
   - Add `_image_manager` parameter
   - Modify `handle_starttag()` to detect `data-image`
   - Add `_reconstruct_image()` method

3. **HTMLSegment**
   - Add `image_id` field (Optional[str])

### Key Decisions

- **Deduplication:** SHA256 hash-based (saves memory)
- **Placeholder:** `<span data-image="IMG001"></span>` (invisible)
- **ID Format:** IMG001, IMG002, IMG003 (3-digit zero-padded)
- **Dimensions:** Preserve original width in inches (height auto-calculated)
- **Error Handling:** Graceful degradation (skip corrupted images)
- **Memory:** Size warnings (10MB per image, 100MB total)

### Code Reuse

- **90% new code** (images are fundamentally different from tabs)
- **Similar patterns:**
  - HTML placeholder approach (proven with tabs)
  - Manager class pattern (similar to CSSClassManager)
  - Dataclass for metadata (similar to FormatAttributes)

---

## Next Steps (Phase 1.3)

1. **Implement ImageData dataclass** (5 minutes)
2. **Implement ImageManager class** (20 minutes)
3. **Write unit tests** (15 minutes)
4. **Verify with test document** (10 minutes)

**Estimated Time:** 50 minutes

---

## Files Modified (Planned)

- `src/translation/docx_html_mapper.py`
  - Add ImageData, ImageManager classes (~150 lines)
  - Modify HTMLSegment (add image_id field)
  - Modify DocxHtmlMapper (add _image_manager)
  - Modify HTMLToDocxParser (add image reconstruction)

- `tests/com8/test_image_manager_COM8.py` (NEW)
  - Unit tests for ImageManager (~200 lines)

---

**Time Spent:** 35 minutes  
**Status:** ✅ Design complete, ready for implementation  
**Next Phase:** 1.3 (Implementation) - Estimated 50 minutes

---

**Programmer:** COM8  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3
