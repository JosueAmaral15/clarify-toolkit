# Phase 1.2: ODT Success Techniques Analysis

**Date:** 2026-02-16  
**Programmer:** COM8  
**Status:** In Progress  

## Purpose

Document the proven techniques from `html_format_mapper.py` that achieved perfect ODT translation quality, and identify which techniques need adaptation for DOCX format.

---

## ODT Translation Architecture (PROVEN ✅)

### Overall Flow
```
ODT File → Extract to HTML → Google Translate API → Parse HTML → Create ODT File
```

### Key Innovation: HTML as Intermediate Format

**Why it works:**
- Google Translate is built to handle HTML (web translation)
- Preserves HTML structure naturally (tags, classes, attributes)
- No placeholder corruption (vs. format_mapper.py's failed approach)
- Industry-proven technology

---

## Core Techniques (From html_format_mapper.py)

### 1. **Dual BR System** - Distinguish Paragraph vs Line Breaks

**Problem:** ODT has two types of breaks:
- Paragraph break (Enter key) - creates new paragraph element
- Line break (Shift+Enter) - `<text:line-break/>` element within paragraph

**Solution:**
```html
<!-- Paragraph break -->
<br class="brk1">

<!-- Line break within paragraph -->
<br class="brk2">
```

**Why class names "brk1"/"brk2":**
- Meaningless words → Google won't translate them
- Distinct classes → easy to distinguish during reconstruction

**Location in code:**
- Line 397: `segments.append(HTMLSegment('', '', 'br', None, element_type='para-break'))`
- Line 403: `segments.append(HTMLSegment('', '', 'line-break', None, element_type='line-break'))`
- Line 618: `html_parts.append('<br class="brk1">')` (paragraph break)
- Line 620: `html_parts.append('<br class="brk2">')` (line break)

**Reconstruction:**
- Line 764: `if tag == 'br' and 'brk1' in classes:` → new paragraph
- Line 774: `if tag == 'br' and 'brk2' in classes:` → line-break element

---

### 2. **Invisible Tab Markers** - Preserve Tabs

**Evolution through 3 attempts:**

❌ **Attempt 1:** HTML entity `&#9;`
- Result: Google converts to space
- Reason: Google normalizes all HTML entities

❌ **Attempt 2:** Visible placeholder `⟨TAB⟩`
- Result: Visible in HTML output (Bug #10)
- User complaint: "⟨TAB⟩ is undesirable"

✅ **Attempt 3:** Invisible data attribute
```html
<span data-tab="1"></span>
```

**Why it works:**
- Empty span → nothing visible to user
- `data-*` attribute → preserved by Google
- Meaningless value "1" → won't be translated

**Location in code:**
- Line 407: `segments.append(HTMLSegment('', '', 'tab', None, element_type='tab'))`
- Line 622: `html_parts.append('<span data-tab="1"></span>')`

**Reconstruction:**
- Line 779: `if tag == 'span' and 'data-tab' in attrs:` → create Tab element

---

### 3. **CSS Class Mapping** - Format Preservation

**Architecture:**
```python
FormatAttributes → Hash → CSS Class Name (fmt1, fmt2, fmt3, ...)
                    ↓
              CSSClassManager (bidirectional mapping)
                    ↓
         HTML: <span class="fmt5">text</span>
                    ↓
              Google Translate (preserves CSS)
                    ↓
         Parse class="fmt5" → Lookup FormatAttributes → Apply to ODT
```

**Key Classes:**

**FormatAttributes** (Lines 47-140):
- Stores all formatting (bold, italic, font, color, alignment, etc.)
- `to_css()` method generates CSS declaration
- `__hash__` and `__eq__` enable deduplication

**CSSClassManager** (Lines 152-239):
- Maintains bidirectional mapping: `format → class` and `class → format`
- `get_class(format)` → returns "fmt1", "fmt2", etc.
- `get_format(class)` → returns FormatAttributes
- Generates CSS stylesheet for HTML `<head>`

**Why CSS classes:**
- Google preserves HTML structure perfectly
- Class names "fmt1", "fmt2" are meaningless → won't translate
- Efficient: same format → same class (deduplication)

**Location in code:**
- Lines 264-300: `extract_html_from_odt()` creates CSSClassManager
- Lines 597-650: `_generate_html()` uses CSS classes in HTML
- Lines 820-920: `HTMLToODTParser` reads CSS classes during reconstruction

---

### 4. **Segment-Based Processing** - Linear Document Model

**HTMLSegment dataclass** (Line 144):
```python
@dataclass
class HTMLSegment:
    text: str                    # Content
    css_class: str               # Format class (fmt1, fmt2, ...)
    tag_type: str                # 'div', 'span', 'br', 'line-break', 'tab'
    attributes: FormatAttributes # Original format
    element_type: str = 'span'   # Extended type info
```

**Why segments:**
- Flat list → easy to iterate and debug
- Each segment = one HTML element
- Types: 'div' (paragraph), 'span' (text run), 'br' (break), 'line-break', 'tab'
- Linear processing (no complex tree traversal)

**Processing flow:**
1. **Extraction** (Lines 322-424): ODT tree → flat segment list
2. **HTML Generation** (Lines 597-650): segments → HTML string
3. **Translation**: Google Translate API
4. **Parsing** (Lines 820-920): HTML string → segment list
5. **Reconstruction** (Lines 698-817): segments → ODT tree

---

### 5. **Google Translate API Behavior** - Tested & Documented

**Known behaviors (from testing):**
- ✅ Preserves HTML tags: `<div>`, `<span>`, `<br>`
- ✅ Preserves CSS classes: `class="fmt1"` → `class="fmt1"` (unchanged)
- ✅ Preserves attributes: `data-tab="1"` → `data-tab="1"` (unchanged)
- ✅ Preserves empty elements: `<span data-tab="1"></span>` (not collapsed)
- ❌ Converts entities to spaces: `&#9;` → ` `, `&nbsp;` → ` `
- ❌ Collapses multiple spaces: `"a    b"` → `"a b"`
- ⚠️ Translates meaningful class names: `class="para"` → `class="for"` (Portuguese)

**Test file:** `tests/com8/test_whitespace_preservation_COM8.py`

**Lesson:** Use meaningless identifiers ("fmt1", "brk1", "data-tab") to avoid translation

---

## DOCX vs ODT Structural Differences

### ODT Structure (odfpy library)

**Explicit element hierarchy:**
```python
document.text (root)
  ├─ text:p (paragraph)
  │   ├─ text:span (formatted run) → text content
  │   ├─ text:tab (tab element)
  │   ├─ text:line-break (line break element)
  │   └─ text:span (more text)
  └─ text:h (heading)
      └─ text:span → text content
```

**Extraction API:**
```python
para.getElementsByType(odf_text.Span)       # Get all spans
para.getElementsByType(odf_text.Tab)        # Get all tabs
para.getElementsByType(odf_text.LineBreak)  # Get all line breaks
```

**Key point:** Tabs and line-breaks are **separate elements** in the tree.

---

### DOCX Structure (python-docx library)

**Mixed element + character hierarchy:**
```python
document (Document)
  └─ paragraphs (list)
      └─ paragraph (Paragraph)
          └─ runs (list)
              └─ run (Run)
                  ├─ text (str) → may contain \t, \n, \r
                  ├─ font (Font object)
                  └─ _element (CT_R - XML element)
```

**Critical difference:** `run.text` is a **string** that may contain:
- `\t` - tab character
- `\n` or `\r` - line break characters
- Regular text

**Example:**
```python
run.text = "Hello\tWorld\nSecond Line"
# Contains: text + tab + text + line-break + text
```

**Implication:** Must **split `run.text`** at tab/line-break positions to create segments.

---

## Adaptations Needed for DOCX

### 1. Text Extraction → Requires Text Splitting

**ODT approach (works as-is):**
```python
for element in para.childNodes:
    if isinstance(element, odf_text.Span):
        text = str(element)
    elif isinstance(element, odf_text.Tab):
        segments.append(tab_segment)
```

**DOCX approach (needs adaptation):**
```python
for run in para.runs:
    text = run.text
    parts = split_by_special_chars(text)  # Split at \t, \n, \r
    
    for part in parts:
        if part.type == 'text':
            segments.append(text_segment)
        elif part.type == 'tab':
            segments.append(tab_segment)
        elif part.type == 'linebreak':
            segments.append(linebreak_segment)
```

**New function needed:**
```python
def split_run_text(text: str) -> List[Dict]:
    """Split run text into text/tab/linebreak parts."""
    parts = []
    current = ""
    
    for char in text:
        if char == '\t':
            if current:
                parts.append({'type': 'text', 'value': current})
                current = ""
            parts.append({'type': 'tab'})
        elif char in '\n\r':
            if current:
                parts.append({'type': 'text', 'value': current})
                current = ""
            parts.append({'type': 'linebreak'})
        else:
            current += char
    
    if current:
        parts.append({'type': 'text', 'value': current})
    
    return parts
```

---

### 2. DOCX Recreation → Insert Tab/LineBreak Elements

**ODT approach (simple):**
```python
if segment_type == 'tab':
    para.addElement(odf_text.Tab())
elif segment_type == 'line-break':
    para.addElement(odf_text.LineBreak())
```

**DOCX approach (verify with testing):**
```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Hypothesis 1: Use XML elements directly
if segment_type == 'tab':
    tab_element = OxmlElement('w:tab')
    run._element.append(tab_element)

# Hypothesis 2: python-docx might have built-in methods
if segment_type == 'tab':
    run.add_tab()  # If exists?

# Hypothesis 3: Create new run with special character
if segment_type == 'tab':
    run.text = '\t'  # Might work if preserved
```

**Action:** Test python-docx API to confirm correct method.

---

### 3. Format Extraction → Can Reuse from format_mapper.py

**Format detection in format_mapper.py (Lines 559-700):**
- Works with python-docx Run objects
- Extracts: bold, italic, font, size, color
- Can be copied to new `docx_html_mapper.py`

**Already works:**
```python
def extract_format_from_run(run) -> FormatAttributes:
    """Extract format from DOCX run."""
    return FormatAttributes(
        bold=run.bold,
        italic=run.italic,
        underline=run.underline,
        font_family=run.font.name if run.font.name else None,
        font_size=run.font.size.pt if run.font.size else None,
        # ... etc
    )
```

**Decision:** Reuse format detection code (proven to work).

---

### 4. Same HTML Markers → No Changes Needed

**All HTML markers work identically:**
- ✅ `<br class="brk1">` → paragraph break
- ✅ `<br class="brk2">` → line break
- ✅ `<span data-tab="1"></span>` → tab
- ✅ CSS classes → format preservation

**Reason:** Google Translate doesn't distinguish ODT vs DOCX source.

---

## Reusable Components

### Can Copy Directly (No Changes)

1. **FormatAttributes class** (Lines 47-140) ✅
2. **CSSClassManager class** (Lines 152-239) ✅
3. **HTMLSegment dataclass** (Line 144) ✅
4. **HTML generation logic** (Lines 597-650) ✅
5. **HTMLToODTParser class** (Lines 820-920) → Rename to HTMLToDocxParser

### Must Adapt

1. **extract_html_from_odt()** → **extract_html_from_docx()**
   - Change: Iterate `doc.paragraphs` instead of `document.text`
   - Change: Split `run.text` by `\t`, `\n`, `\r`
   - Keep: Same segment creation logic

2. **create_odt_from_html()** → **create_docx_from_html()**
   - Change: Use `Document()` instead of `OpenDocument()`
   - Change: Use `add_paragraph()`, `add_run()` instead of `addElement()`
   - Change: Research how to insert Tab/LineBreak elements in python-docx
   - Keep: Same HTML parsing logic

3. **Format application** (Lines 698-817)
   - Change: Use python-docx API to set bold, italic, font, etc.
   - Keep: Same format lookup from CSSClassManager

---

## Comparison Table

| Aspect | ODT (odfpy) | DOCX (python-docx) | Adaptation Needed |
|--------|-------------|-------------------|-------------------|
| Document root | `opendocument.load()` | `Document()` | ✅ Simple API change |
| Paragraph iteration | `document.text` children | `doc.paragraphs` | ✅ Simple API change |
| Text runs | `getElementsByType(Span)` | `para.runs` | ✅ Simple API change |
| Tabs | Separate `Tab` elements | `\t` in `run.text` | ⚠️ **Must split text** |
| Line breaks | Separate `LineBreak` elements | `\n`/`\r` in `run.text` | ⚠️ **Must split text** |
| Format extraction | Style objects | `run.font`, `run.bold` | ✅ Already works (format_mapper.py) |
| Creating paragraph | `addElement(P())` | `add_paragraph()` | ✅ Simple API change |
| Creating run | `addElement(Span())` | `add_run()` | ✅ Simple API change |
| Creating tab | `addElement(Tab())` | ❓ **Test needed** | ⚠️ **Research required** |
| Creating line-break | `addElement(LineBreak())` | ❓ **Test needed** | ⚠️ **Research required** |
| HTML markers | `<br class="brk1/brk2">` | Same | ✅ No changes |
| CSS classes | `class="fmt1"` | Same | ✅ No changes |
| Tab marker | `<span data-tab="1">` | Same | ✅ No changes |

---

## Risk Assessment

### Low Risk (Direct Port)
- ✅ HTML generation (proven approach)
- ✅ CSS class system (Google preserves)
- ✅ Segment architecture (language agnostic)
- ✅ Format extraction (already working in format_mapper.py)

### Medium Risk (API Differences)
- ⚠️ Text splitting logic (new function needed)
- ⚠️ DOCX API differences (simple but requires testing)

### High Risk (Unknown)
- ⚠️ **Tab/LineBreak insertion in python-docx** (needs research)
  - Might require XML manipulation
  - python-docx might not expose high-level API
  - Could require `run._element` access (XML level)

---

## Next Steps (Phase 1.3)

### Must Research Before Implementation

1. **How to insert Tab in python-docx:**
   - Test: `run.text = '\t'` (does it preserve?)
   - Test: XML manipulation (`OxmlElement('w:tab')`)
   - Find official documentation or examples

2. **How to insert LineBreak in python-docx:**
   - Test: `run.text = '\n'` (does it preserve?)
   - Test: `run.add_break()` (if method exists)
   - Test: XML manipulation (`OxmlElement('w:br')`)

3. **Verify paragraph breaks:**
   - Test: Create new paragraph vs. line-break within paragraph
   - Confirm distinction is preserved

### Test Script for Phase 1.3

```python
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Create test document
doc = Document()

# Test 1: Tab insertion
para1 = doc.add_paragraph()
run1 = para1.add_run("Before")
# Try method 1: direct text
run2 = para1.add_run("\t")
run3 = para1.add_run("After")

# Test 2: Line-break insertion
para2 = doc.add_paragraph()
run4 = para2.add_run("Line 1")
# Try method 2: add_break()
if hasattr(run4, 'add_break'):
    run4.add_break()
run5 = para2.add_run("Line 2")

# Save and inspect
doc.save('/tmp/docx_test.docx')

# Re-open and verify
doc2 = Document('/tmp/docx_test.docx')
for para in doc2.paragraphs:
    for run in para.runs:
        print(f"Run text: {repr(run.text)}")
```

---

## Conclusion

**Phase 1.2 Complete:**
- ✅ Documented all ODT success techniques
- ✅ Identified DOCX structural differences
- ✅ Created comparison table
- ✅ Identified reusable components (90% of code)
- ✅ Identified adaptations needed (mainly text splitting)
- ⚠️ Identified unknown: Tab/LineBreak insertion API

**Confidence Level:**
- HTML approach: **100%** (proven with ODT)
- Format extraction: **100%** (already working)
- Text splitting: **95%** (straightforward algorithm)
- DOCX reconstruction: **70%** (depends on python-docx API research)

**Next:** Phase 1.3 - Test python-docx Tab/LineBreak insertion methods.
