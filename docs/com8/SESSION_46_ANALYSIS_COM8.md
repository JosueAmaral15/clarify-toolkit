# Session 46: Image Preservation Analysis (COM8)

**Date:** February 1, 2026  
**Status:** 🔍 ANALYZED - Architecture decision needed

---

## Investigation Summary

Successfully investigated image structures in both DOCX and ODT formats:

### DOCX Images
- Stored as `<w:drawing>` elements inside runs
- Contains `<wp:inline>` for inline images
- Image data in relationships (`rId`)
- Binary blob stored in document package
- Size/position metadata in XML

### ODT Images  
- Wrapped in `<draw:frame>` elements
- Contains `<draw:image>` with href
- Image stored in Pictures/ directory
- Size in frame attributes (cm units)
- Anchor type determines positioning

---

## Implementation Challenges

### Challenge 1: Binary Data
**Problem:** Images are binary data, can't pass through Google Translate as text  
**Options:**
- A) Base64 encode in tags (makes text huge, 33% size increase)
- B) External image registry (requires API changes)
- C) Placeholder text only (loses images)

### Challenge 2: Google Translate Limitations
**Problem:** Google Translate only handles text  
**Reality:** Images physically cannot be translated

### Challenge 3: Text Flow
**Problem:** Images affect paragraph layout  
**Issue:** Tag system designed for inline formatting, not block-level elements

---

## Recommended Approach

### Defer Full Image Preservation

**Reasoning:**
1. Images cannot be translated (they're pictures)
2. Current architecture (text-only) works perfectly for text
3. Adding images would complicate the system significantly
4. User can manually reinsert images after translation

### Minimal Implementation: Image Placeholders

If needed, implement simple placeholder system:

```
<IMAGE_PLACEHOLDER>
- Extract: Detect images, insert `[Image: {size}]` text
- Translate: Placeholder text gets translated
- Output: No actual image, just placeholder text
- User workflow: Manually reinsert images from original
```

**Benefit:** Documents text flow preservation  
**Limitation:** Images lost (acceptable for translation workflow)

---

## Phase 6 Status

**Images (5 formats from action plan):**
- ❌ Inline images - Deferred
- ❌ Image size - Deferred  
- ❌ Image positioning - Deferred
- ❌ Image wrapping - Deferred
- ❌ Image alt text - Deferred

**Rationale:** Images don't translate. System optimized for text.

---

## Alternative: Post-Processing Tool

**Better solution:** Separate tool for image reinsertion

```python
# Pseudocode
def reinsert_images(original_doc, translated_doc):
    """
    Extract images from original_doc
    Find corresponding positions in translated_doc
    Reinsert images at correct locations
    """
    # This would be a separate utility
```

**Benefits:**
- Keeps translation pipeline simple
- Handles images in specialized tool
- User has control over image placement

---

## Recommendation for Session 46

**Option A:** Skip images, move to other features  
**Option B:** Implement simple placeholder system  
**Option C:** Create separate image reinsertion tool

**Suggested: Option A** - Focus on text formatting (project goal)

Move to **Phase 9: Special Characters** instead:
- Non-breaking spaces
- Soft hyphens  
- Tab characters
- These ARE text and CAN be translated

---

## Decision Point

**Continue with images?** ❌ Not recommended  
**Alternative direction?** ✅ Special characters (Phase 9)

**Reason:** Stay focused on text preservation through translation.  
Images are orthogonal to translation problem.

---

**Current Progress:** 28/62 formats (45.2%)  
**Viable target:** ~35-40 formats (text-focused features)  
**Status:** Excellent progress on core functionality

