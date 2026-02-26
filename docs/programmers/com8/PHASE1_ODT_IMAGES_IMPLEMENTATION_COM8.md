# Phase 1: ODT Image Support Implementation - COM8

**Date:** 2026-02-17  
**Programmer:** COM8  
**Scope:** Implement ImageManager for ODT files (Option C)  
**Estimated Time:** 5-6 hours

---

## Implementation Plan

### Phase 1.1: Research & Design (30 min) ✅
**Status:** Starting

**Tasks:**
1. Study ODF image format
2. Analyze DOCX ImageManager (proven pattern)
3. Design ODTImageManager
4. Document approach

---

### Phase 1.2: Create ODTImageManager Class (2 hours)
**Status:** Pending

**Tasks:**
1. Create ImageData dataclass (adapt from DOCX)
2. Create ODTImageManager class
3. Implement methods:
   - `add_image()` - store image with deduplication
   - `get_image()` - retrieve by ID
   - `generate_placeholder()` - HTML marker
   - `get_statistics()` - memory tracking
   - `clear()` - cleanup

---

### Phase 1.3: Extract Images from ODT (1.5 hours)
**Status:** Pending

**Tasks:**
1. Modify `HTMLFormatMapper.extract_html_from_odt()`
2. Extract images from ODT Pictures/ folder
3. Store in ImageManager
4. Insert HTML markers: `<span data-image="IMG001"></span>`
5. Track image positions in document

---

### Phase 1.4: Restore Images to ODT (1.5 hours)
**Status:** Pending

**Tasks:**
1. Modify `HTMLFormatMapper._save_as_odt()`
2. Parse HTML for image markers
3. Retrieve images from ImageManager
4. Insert images into ODT Pictures/ folder
5. Create proper ODF draw:frame elements

---

### Phase 1.5: Integration & Testing (1 hour)
**Status:** Pending

**Tasks:**
1. Update `google_translate_dock.py`:
   - Store `image_manager` for ODT
   - Pass manager to translation worker
2. Create test ODT with images
3. Test translation workflow
4. Verify pagination still works

---

### Phase 1.6: Documentation (30 min)
**Status:** Pending

**Tasks:**
1. Create implementation summary
2. Update comparison table
3. Document limitations

---

## Technical Details

### ODF Image Format:

```xml
<!-- In content.xml -->
<text:p>
  <draw:frame text:anchor-type="as-char" svg:width="3in" svg:height="2in">
    <draw:image xlink:href="Pictures/image1.png" 
                xlink:type="simple" 
                xlink:show="embed"/>
  </draw:frame>
</text:p>
```

**Key Points:**
- Images stored in `Pictures/` folder inside ODT zip
- Referenced via `xlink:href="Pictures/imageN.png"`
- Size specified in inches/cm (svg:width, svg:height)
- Anchor types: `as-char` (inline), `paragraph`, `page`, `frame`

### ImageManager API (ODT Version):

```python
class ODTImageManager:
    def __init__(self):
        self._images: Dict[str, ODTImageData] = {}
        self._hash_to_id: Dict[str, str] = {}
        self._next_id: int = 1
    
    def add_image(self, blob: bytes, format: str, 
                  width_cm: float, height_cm: float,
                  original_href: str) -> str:
        """Add image, returns IMG001, IMG002, etc."""
        pass
    
    def get_image(self, image_id: str) -> Optional[ODTImageData]:
        """Retrieve image by ID."""
        pass
    
    def generate_placeholder(self, image_id: str) -> str:
        """Returns: '<span data-image="IMG001"></span>'"""
        pass
```

---

## Expected Output

### Before (Current):
```
ODT file with images → Translate → ODT file WITHOUT images ❌
```

### After (Phase 1 Complete):
```
ODT file with images → Translate → ODT file WITH images ✅
```

---

## Next Steps

After Phase 1 (Images) completes → Start Phase 2 (Tables)

---

**Status:** 🚧 IN PROGRESS - Phase 1.1  
**Current Task:** Research ODF image format  
**Next:** Create ODTImageManager class
