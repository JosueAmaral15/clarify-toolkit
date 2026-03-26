# Action Plan: Hyperlink Preservation Fix

**Date**: 2026-02-20  
**Author**: COM8  
**Issue**: Hyperlinks (URLs) are being stripped from ODT documents during translation

## Problem Analysis

### Current Behavior
- **Test**: Created ODT with links: `https://www.google.com.br`, `https://github.com`, etc.
- **Extraction**: Links completely removed from HTML output
- **Result**: Only link text remains (e.g., "Google" but no href)
- **Location**: Link URLs appear at bottom of document or disappear entirely

### Root Cause
File: `src/translation/html_format_mapper.py`, function `_extract_paragraph()` (lines 752-900)

**Missing Element Handler**: The code processes these ODT elements:
- ✅ `text:span` - Text formatting (bold, italic, etc.)
- ✅ `text:line-break` - Soft line breaks
- ✅ `text:tab` - Tab characters
- ✅ `text:s` - Multiple spaces
- ✅ `draw:frame` - Images (Phase 1 - COM8)
- ✅ `table:table` - Tables (Phase 2 - COM8)
- ❌ **`text:a` - Hyperlinks** ← NOT HANDLED!

### Technical Details

**ODT Structure** (from test document):
```xml
<text:p>
  Visit my website at 
  <text:a xlink:href="https://www.google.com.br">
    https://www.google.com.br
  </text:a>
  for more information.
</text:p>
```

**Current Output** (broken):
```html
<span class="fmt1">Visit my website at  for more information.</span>
```
Notice: The link text AND href are both missing!

**Expected Output**:
```html
<span class="fmt1">Visit my website at <a href="https://www.google.com.br">https://www.google.com.br</a> for more information.</span>
```

### Link Types to Support

1. **External links**: `https://www.google.com`, `http://example.org`
2. **Internal links**: `#section_id` (cross-references)
3. **Email links**: `mailto:user@example.com`
4. **File links**: `file:///path/to/file`

## Solution Plan

### Phase 1: Add Hyperlink Detection (30 min)

**Location**: `_extract_paragraph()` function, around line 854

**Implementation**:
1. Add check for `text:a` element in node processing loop
2. Extract href attribute using `xlink:href` namespace
3. Handle nested content (text:a can contain text:span with formatting)
4. Preserve link text and format

**Code Structure**:
```python
elif hasattr(node, 'qname') and node.qname[1] == 'a':
    # Hyperlink detected
    href = node.getAttribute('href')  # xlink:href
    
    # Save accumulated text before link
    if para_text:
        # ... save previous segment
    
    # Extract link content (may contain spans with formatting)
    link_text = ""
    link_fmt = current_fmt  # Inherit paragraph format
    
    for link_child in node.childNodes:
        if isinstance(link_child, ODFText):
            link_text += str(link_child)
        elif hasattr(link_child, 'qname') and link_child.qname[1] == 'span':
            # Link contains formatted text
            link_fmt = _extract_span_format(link_child, styles, para_fmt)
            for span_child in link_child.childNodes:
                if isinstance(span_child, ODFText):
                    link_text += str(span_child)
    
    # Create HTML hyperlink segment
    segments.append(HTMLSegment(
        text=f'<a href="{href}">{link_text}</a>',
        css_class='',
        tag_type='link',
        attributes=FormatAttributes()
    ))
```

### Phase 2: HTML Generation (15 min)

**Location**: `_generate_html()` function

**Issue**: Need to ensure HTML `<a>` tags are not escaped
- Check if link segments are properly handled
- Ensure tag_type='link' outputs raw HTML

### Phase 3: ODT Restoration (45 min)

**Challenge**: Recreating `text:a` elements in output ODT

**Location**: `create_odt_from_original()` function, segment processing loop

**Current Issue**:
- Parser reads HTML: `<a href="...">text</a>`
- But we don't have handler to convert back to ODF `text:a` element

**Implementation**:
1. Create `HTMLToODTParser` enhancement to detect `<a>` tags
2. Add 'link' segment type to parser
3. In ODT creation loop, handle 'link' segments:

```python
elif segment['type'] == 'link':
    if current_paragraph is None:
        current_paragraph = P()
    
    # Create text:a element
    from odf.text import A as Link
    link = Link(href=segment['href'])
    link.addText(segment['text'])
    current_paragraph.appendChild(link)
```

### Phase 4: Testing (30 min)

**Test Cases**:

1. **Simple external link**:
   - Input: `Visit <a href="https://google.com">Google</a>`
   - Extract → Translate → Restore → Verify href preserved

2. **Link with formatting**:
   - Input: Link with **bold** text
   - Verify: Bold format + href both preserved

3. **Multiple links in paragraph**:
   - Input: `See <a>GitHub</a> and <a>Stack Overflow</a>`
   - Verify: Both links preserved

4. **Internal cross-reference**:
   - Input: `See <a href="#fig1">Figure 1</a>`
   - Verify: Internal link works

5. **TCC document**:
   - Has 62 internal links (cross-references to figures)
   - Verify: All 62 links preserved after translation

**Test Script**: Create `test_hyperlinks_preservation_COM8.py`

## Implementation Steps

### Step 1: Create Test Script (5 min)
```bash
test_hyperlinks_preservation_COM8.py
├── Create ODT with various link types
├── Extract → HTML (check links present)
├── Translate (identity)
├── Restore → ODT
└── Verify: Open in LibreOffice, check links work
```

### Step 2: Fix Extraction (30 min)
- Modify `_extract_paragraph()` to handle `text:a`
- Add link segment to HTMLSegment types
- Test: Verify links appear in HTML

### Step 3: Fix HTML Generation (15 min)
- Update `_generate_html()` to output `<a>` tags correctly
- Ensure no double-escaping

### Step 4: Fix ODT Restoration (45 min)
- Update `HTMLToODTParser` to parse `<a>` tags
- Add link segment handler in `create_odt_from_original()`
- Use `odf.text.A` to create proper ODF links

### Step 5: Integration Testing (30 min)
- Test with test_hyperlinks_COM8.odt
- Test with TCC document (62 internal links)
- Verify LibreOffice opens and links are clickable

## Expected Outcome

✅ External links preserved: `https://google.com`  
✅ Internal links preserved: `#section_id`  
✅ Link text formatting preserved (bold, italic, etc.)  
✅ Multiple links per paragraph work  
✅ LibreOffice recognizes links (clickable, blue, underlined)  
✅ TCC document: All 62 cross-references intact  

## Questions for User

1. **Priority**: Is this a blocker for current work?
2. **Link Types**: Do you need email/file links, or just http/https?
3. **Testing**: Should I test with real TCC file (62 links) or just simple test?
4. **Format**: Should links inherit paragraph formatting or have their own?

## Estimated Time

- **Phase 1-2** (Extraction + HTML): 45 min
- **Phase 3** (ODT Restoration): 45 min  
- **Phase 4** (Testing): 30 min  
- **Total**: ~2 hours

## Notes

- This is similar to image/table handling we did before
- Need to preserve `xlink:href` namespace in ODT
- Google Translate should preserve HTML `<a>` tags (proven technology)
- May need to handle link color/underline in CSS classes
