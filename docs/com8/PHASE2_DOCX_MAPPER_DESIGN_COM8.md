# Phase 2: DOCX HTML Mapper Design

**Date:** 2026-02-16  
**Programmer:** COM8  
**Status:** In Progress  

## Purpose

Detailed design for `src/translation/docx_html_mapper.py` - a new module that applies proven ODT translation techniques to DOCX format.

---

## Design Principles

1. **Mirror ODT Success:** Reuse 90% of html_format_mapper.py architecture
2. **Minimal Changes:** Only adapt for DOCX-specific differences (text splitting)
3. **Same HTML Format:** Identical markers (brk1, brk2, data-tab, CSS classes)
4. **Google Translate Compatible:** Proven to work with ODT
5. **Simple API:** Match ODT module's function signatures

---

## Module Overview

### File: `src/translation/docx_html_mapper.py`

**Purpose:** Bidirectional conversion between DOCX and HTML for translation

**Flow:**
```
DOCX File → extract_html_from_docx() → HTML String
                                          ↓
                                   Google Translate
                                          ↓
HTML String → create_docx_from_html() → DOCX File
```

**Key Innovation:** HTML as intermediate format (Google Translate optimized)

---

## Class Structure

### 1. FormatAttributes (REUSE - No Changes)

**Source:** Copy from html_format_mapper.py lines 47-140

**Purpose:** Store all formatting properties (bold, italic, font, color, etc.)

**Methods:**
- `to_css()` → Generate CSS declaration
- `__hash__()` → Enable deduplication
- `__eq__()` → Compare formats

**Status:** ✅ Proven, copy as-is

---

### 2. HTMLSegment (REUSE - No Changes)

**Source:** Copy from html_format_mapper.py line 144

**Purpose:** Represent one document element as HTML

```python
@dataclass
class HTMLSegment:
    text: str                    # Content (empty for tabs/breaks)
    css_class: str               # Format class (fmt1, fmt2, ...)
    tag_type: str                # 'div', 'span', 'br', 'line-break', 'tab'
    attributes: FormatAttributes # Original format object
    element_type: str = 'span'   # Extended type info
```

**Status:** ✅ Proven, copy as-is

---

### 3. CSSClassManager (REUSE - No Changes)

**Source:** Copy from html_format_mapper.py lines 152-239

**Purpose:** Bidirectional mapping between FormatAttributes and CSS class names

**Methods:**
- `get_class(format: FormatAttributes) -> str` → Get/create class name
- `get_format(class_name: str) -> FormatAttributes` → Lookup format
- `generate_stylesheet() -> str` → Create CSS for HTML <head>

**Data:**
- `format_to_class: Dict[FormatAttributes, str]` → Forward lookup
- `class_to_format: Dict[str, FormatAttributes]` → Reverse lookup
- `counter: int` → Class name generator (fmt1, fmt2, fmt3...)

**Status:** ✅ Proven, copy as-is

---

### 4. DocxHtmlMapper (NEW - Adapted from OdtHtmlMapper)

**Purpose:** Main extraction and HTML generation logic

**Source:** Adapt from html_format_mapper.py extract_html_from_odt()

#### 4.1. Constructor

```python
class DocxHtmlMapper:
    def __init__(self, docx_path: str):
        """Initialize mapper with DOCX file path."""
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.css_manager = CSSClassManager()
        self.segments: List[HTMLSegment] = []
```

#### 4.2. Main Extraction Method

```python
def extract_html_from_docx(self) -> str:
    """
    Extract DOCX content and convert to HTML.
    
    Returns:
        HTML string with CSS classes and invisible markers
    """
    # 1. Extract all segments
    self._extract_segments()
    
    # 2. Generate HTML string
    html = self._generate_html()
    
    return html
```

#### 4.3. Segment Extraction (NEW - DOCX-specific)

```python
def _extract_segments(self):
    """Extract all document content as flat segment list."""
    for para_idx, para in enumerate(self.doc.paragraphs):
        # Process all runs in paragraph
        for run in para.runs:
            # Extract format once for this run
            run_format = self._extract_format_from_run(run)
            css_class = self.css_manager.get_class(run_format)
            
            # Split run.text by tabs and line-breaks
            parts = self._split_run_text(run.text)
            
            for part in parts:
                if part['type'] == 'text':
                    self.segments.append(HTMLSegment(
                        text=part['value'],
                        css_class=css_class,
                        tag_type='span',
                        attributes=run_format,
                        element_type='span'
                    ))
                elif part['type'] == 'tab':
                    self.segments.append(HTMLSegment(
                        text='',
                        css_class='',
                        tag_type='tab',
                        attributes=None,
                        element_type='tab'
                    ))
                elif part['type'] == 'linebreak':
                    self.segments.append(HTMLSegment(
                        text='',
                        css_class='',
                        tag_type='line-break',
                        attributes=None,
                        element_type='line-break'
                    ))
        
        # After all runs, add paragraph break
        self.segments.append(HTMLSegment(
            text='',
            css_class='',
            tag_type='br',
            attributes=None,
            element_type='para-break'
        ))
```

**Key difference from ODT:**
- ODT: Iterate `getElementsByType()` - tabs/breaks are separate elements
- DOCX: Split `run.text` string - tabs/breaks are characters

#### 4.4. Text Splitting (NEW - DOCX-specific)

```python
def _split_run_text(self, text: str) -> List[Dict[str, str]]:
    """
    Split run text into text/tab/linebreak parts.
    
    Args:
        text: Run text potentially containing \t, \n, \r
    
    Returns:
        List of dicts: [
            {'type': 'text', 'value': 'Hello'},
            {'type': 'tab'},
            {'type': 'text', 'value': 'World'},
            {'type': 'linebreak'},
            ...
        ]
    
    Examples:
        "Hello\tWorld" → [text("Hello"), tab, text("World")]
        "\t\t\t" → [tab, tab, tab]
        "Plain text" → [text("Plain text")]
        "" → []
    """
    if not text:
        return []
    
    parts = []
    current = ""
    
    for char in text:
        if char == '\t':
            # Flush current text if any
            if current:
                parts.append({'type': 'text', 'value': current})
                current = ""
            parts.append({'type': 'tab'})
        
        elif char in '\n\r':
            # Flush current text if any
            if current:
                parts.append({'type': 'text', 'value': current})
                current = ""
            parts.append({'type': 'linebreak'})
        
        else:
            current += char
    
    # Flush remaining text
    if current:
        parts.append({'type': 'text', 'value': current})
    
    return parts
```

**Edge cases handled:**
- ✅ Empty string → return []
- ✅ Only tabs: "\t\t\t" → [tab, tab, tab]
- ✅ Only linebreaks: "\n\n" → [linebreak, linebreak]
- ✅ Mixed: "A\tB\nC" → [text, tab, text, linebreak, text]
- ✅ Leading/trailing special chars: "\tHello\n" → [tab, text, linebreak]

#### 4.5. Format Extraction (REUSE - from format_mapper.py)

```python
def _extract_format_from_run(self, run) -> FormatAttributes:
    """
    Extract formatting from DOCX run.
    
    Source: Adapted from format_mapper.py lines 559-700
    """
    from docx.shared import Pt, RGBColor
    
    format_attrs = FormatAttributes()
    
    # Character formatting
    format_attrs.bold = run.bold if run.bold is not None else False
    format_attrs.italic = run.italic if run.italic is not None else False
    format_attrs.underline = run.underline if run.underline is not None else False
    
    # Font properties
    if run.font.name:
        format_attrs.font_family = run.font.name
    
    if run.font.size:
        format_attrs.font_size = int(run.font.size.pt)
    
    if run.font.color and run.font.color.rgb:
        # Convert RGBColor to hex string
        rgb = run.font.color.rgb
        format_attrs.font_color = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    # Paragraph formatting (from paragraph, not run)
    # Note: Extract only if needed for this project
    
    return format_attrs
```

**Status:** ✅ Already works in format_mapper.py, copy and adapt

#### 4.6. HTML Generation (REUSE - No Changes)

```python
def _generate_html(self) -> str:
    """
    Generate HTML from segments.
    
    Source: Copy from html_format_mapper.py lines 597-650
    """
    html_parts = []
    
    # HTML header
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<style>')
    html_parts.append(self.css_manager.generate_stylesheet())
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    
    # Content
    for seg in self.segments:
        if seg.tag_type == 'div':
            html_parts.append(f'<div class="{seg.css_class}">{html.escape(seg.text)}</div>')
        
        elif seg.tag_type == 'span':
            html_parts.append(f'<span class="{seg.css_class}">{html.escape(seg.text)}</span>')
        
        elif seg.tag_type == 'br' and seg.element_type == 'para-break':
            html_parts.append('<br class="brk1">')
        
        elif seg.tag_type == 'line-break':
            html_parts.append('<br class="brk2">')
        
        elif seg.tag_type == 'tab':
            html_parts.append('<span data-tab="1"></span>')
    
    # HTML footer
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    return ''.join(html_parts)
```

**Status:** ✅ Proven, copy as-is

---

### 5. HTMLToDocxParser (NEW - Adapted from HTMLToODTParser)

**Purpose:** Parse translated HTML and recreate DOCX

**Source:** Adapt from html_format_mapper.py lines 820-920

```python
from html.parser import HTMLParser
from docx import Document
from docx.shared import Pt, RGBColor

class HTMLToDocxParser(HTMLParser):
    """Parse HTML and create DOCX document."""
    
    def __init__(self, css_class_manager: CSSClassManager):
        super().__init__()
        self.css_manager = css_class_manager
        self.doc = Document()
        self.current_para = None
        self.current_format = None
        self.text_buffer = []
    
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        
        if tag == 'div':
            # Create new paragraph
            self.current_para = self.doc.add_paragraph()
            
            # Set paragraph format from CSS class
            if classes:
                self.current_format = self.css_manager.get_format(classes[0])
        
        elif tag == 'span':
            # Check for tab marker
            if 'data-tab' in attr_dict:
                # Insert tab
                if self.current_para is None:
                    self.current_para = self.doc.add_paragraph()
                self.current_para.add_run('\t')
            
            else:
                # Set format for upcoming text
                if classes:
                    self.current_format = self.css_manager.get_format(classes[0])
        
        elif tag == 'br':
            if 'brk1' in classes:
                # Paragraph break - create new paragraph
                self.current_para = self.doc.add_paragraph()
                self.current_format = None
            
            elif 'brk2' in classes:
                # Line break within paragraph
                if self.current_para is None:
                    self.current_para = self.doc.add_paragraph()
                self.current_para.add_run('\n')
    
    def handle_data(self, data):
        """Handle text content."""
        if not data.strip():
            return  # Skip whitespace-only text
        
        if self.current_para is None:
            self.current_para = self.doc.add_paragraph()
        
        # Create run with text
        run = self.current_para.add_run(data)
        
        # Apply formatting
        if self.current_format:
            self._apply_format_to_run(run, self.current_format)
    
    def _apply_format_to_run(self, run, format_attrs: FormatAttributes):
        """Apply format attributes to DOCX run."""
        if format_attrs.bold:
            run.bold = True
        if format_attrs.italic:
            run.italic = True
        if format_attrs.underline:
            run.underline = True
        
        if format_attrs.font_family:
            run.font.name = format_attrs.font_family
        
        if format_attrs.font_size:
            run.font.size = Pt(format_attrs.font_size)
        
        if format_attrs.font_color:
            # Convert hex string to RGBColor
            hex_color = format_attrs.font_color
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            run.font.color.rgb = RGBColor(r, g, b)
    
    def get_document(self) -> Document:
        """Return the created DOCX document."""
        return self.doc
```

**Key difference from ODT:**
- ODT: `para.addElement(Tab())`, `para.addElement(LineBreak())`
- DOCX: `para.add_run('\t')`, `para.add_run('\n')`

**Status:** ✅ Simple API change, confident

---

## Public API Functions

### Function 1: extract_html_from_docx()

```python
def extract_html_from_docx(docx_path: str, output_html_path: Optional[str] = None) -> str:
    """
    Extract DOCX content and convert to HTML for translation.
    
    Args:
        docx_path: Path to input DOCX file
        output_html_path: Optional path to save HTML (for debugging)
    
    Returns:
        HTML string with CSS classes and invisible markers
    
    Example:
        html = extract_html_from_docx('document.docx')
        translated_html = google_translate(html)
    """
    mapper = DocxHtmlMapper(docx_path)
    html = mapper.extract_html_from_docx()
    
    if output_html_path:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    return html
```

### Function 2: create_docx_from_html()

```python
def create_docx_from_html(
    html_string: str,
    output_docx_path: str,
    css_class_manager: CSSClassManager
) -> None:
    """
    Create DOCX file from translated HTML.
    
    Args:
        html_string: Translated HTML with CSS classes and markers
        output_docx_path: Path to save output DOCX file
        css_class_manager: Manager used during extraction (for format lookup)
    
    Example:
        mapper = DocxHtmlMapper('input.docx')
        html = mapper.extract_html_from_docx()
        translated_html = google_translate(html)
        create_docx_from_html(
            translated_html,
            'output.docx',
            mapper.css_manager
        )
    """
    parser = HTMLToDocxParser(css_class_manager)
    parser.feed(html_string)
    doc = parser.get_document()
    doc.save(output_docx_path)
```

### Function 3: translate_docx() (High-level wrapper)

```python
def translate_docx(
    input_docx_path: str,
    output_docx_path: str,
    translate_function: callable
) -> None:
    """
    Complete DOCX translation workflow.
    
    Args:
        input_docx_path: Path to input DOCX file
        output_docx_path: Path to save translated DOCX file
        translate_function: Function that translates HTML string
            Signature: translate_function(html: str) -> str
    
    Example:
        def my_translator(html):
            return google_translate_api(html, target='pt')
        
        translate_docx('input.docx', 'output.docx', my_translator)
    """
    # 1. Extract
    mapper = DocxHtmlMapper(input_docx_path)
    html = mapper.extract_html_from_docx()
    
    # 2. Translate
    translated_html = translate_function(html)
    
    # 3. Create
    create_docx_from_html(
        translated_html,
        output_docx_path,
        mapper.css_manager
    )
```

---

## Edge Cases and Solutions

### 1. Empty Paragraphs

**Case:** Paragraph with no runs
```python
para.runs == []
```

**Solution:** Add paragraph break segment anyway
```python
# After processing runs (even if none)
self.segments.append(HTMLSegment(..., element_type='para-break'))
```

**Result:** Empty paragraph preserved in output

---

### 2. Empty Runs

**Case:** Run with empty text
```python
run.text == ""
```

**Solution:** `_split_run_text()` returns empty list, no segments added

**Result:** No-op, correct behavior

---

### 3. Consecutive Tabs/LineBreaks

**Case:** `run.text = "\t\t\t"` (10 tabs in CAIT doc)

**Solution:** `_split_run_text()` creates N tab segments

**Result:** N tabs preserved in output ✅ (verified in Phase 1.3)

---

### 4. Mixed Content

**Case:** `run.text = "Hello\tWorld\nMore"`

**Solution:** Split into: [text, tab, text, linebreak, text]

**Result:** Structure preserved perfectly

---

### 5. Format Consistency

**Case:** Single run split into multiple segments

**Solution:** Extract format once before splitting, apply to all text segments from that run

```python
run_format = extract_format(run)  # Once
parts = split_run_text(run.text)
for part in parts:
    if part['type'] == 'text':
        segment.attributes = run_format  # Same format
```

**Result:** Format preserved across splits

---

### 6. Google Translate Edge Cases

**Known behaviors (from ODT testing):**
- ✅ Preserves `<br class="brk1">` and `<br class="brk2">`
- ✅ Preserves `<span data-tab="1"></span>`
- ✅ Preserves CSS classes: `class="fmt5"`
- ❌ Converts entities to spaces: `&#9;` → ` `
- ⚠️ Collapses multiple spaces

**Solution:** Use invisible markers, not entities (already designed)

**Result:** No Google-related issues expected

---

## Testing Strategy

### Test 1: Unit Tests

**File:** `tests/com8/test_docx_html_mapper_COM8.py`

**Tests:**
1. `test_split_run_text_empty()`
2. `test_split_run_text_plain()`
3. `test_split_run_text_tabs_only()`
4. `test_split_run_text_linebreaks_only()`
5. `test_split_run_text_mixed()`
6. `test_format_extraction()`
7. `test_css_class_generation()`

### Test 2: Integration Test

**File:** `tests/com8/test_docx_end_to_end_COM8.py`

**Test:** Complete workflow with CAIT document

```python
def test_cait_document_translation():
    """Test DOCX translation with real document."""
    input_path = 'docs/CAIT- Trabalho de Biologia - Josué 3001.docx'
    output_path = '/tmp/cait_translated.docx'
    
    # Mock translation (identity function for structure test)
    def mock_translate(html):
        return html
    
    # Translate
    translate_docx(input_path, output_path, mock_translate)
    
    # Verify output structure
    original = Document(input_path)
    translated = Document(output_path)
    
    # Structure checks
    assert len(translated.paragraphs) == 18, "Must have 18 paragraphs"
    
    # Count tabs and line-breaks
    tab_count = 0
    lb_count = 0
    for para in translated.paragraphs:
        for run in para.runs:
            tab_count += run.text.count('\t')
            lb_count += run.text.count('\n')
    
    assert tab_count == 14, f"Must have 14 tabs, got {tab_count}"
    assert lb_count == 22, f"Must have 22 line-breaks, got {lb_count}"
```

### Test 3: Visual Inspection

**Process:**
1. Translate CAIT document
2. Open in LibreOffice/Word
3. Compare side-by-side with original
4. Check: tabs aligned, line-breaks visible, formatting preserved

---

## Implementation Checklist

### Phase 3.1: Core Classes (1 hour)
- [ ] Copy FormatAttributes class
- [ ] Copy HTMLSegment dataclass
- [ ] Copy CSSClassManager class
- [ ] Verify imports

### Phase 3.2: DocxHtmlMapper (2 hours)
- [ ] Implement constructor
- [ ] Implement _split_run_text()
- [ ] Implement _extract_format_from_run()
- [ ] Implement _extract_segments()
- [ ] Copy _generate_html()
- [ ] Implement extract_html_from_docx()

### Phase 3.3: HTMLToDocxParser (1.5 hours)
- [ ] Implement constructor
- [ ] Implement handle_starttag()
- [ ] Implement handle_data()
- [ ] Implement _apply_format_to_run()
- [ ] Implement get_document()

### Phase 3.4: Public API (0.5 hours)
- [ ] Implement extract_html_from_docx() function
- [ ] Implement create_docx_from_html() function
- [ ] Implement translate_docx() function
- [ ] Add docstrings

### Phase 3.5: Testing (2 hours)
- [ ] Write unit tests
- [ ] Write integration test
- [ ] Run tests and fix bugs
- [ ] Visual verification

**Total estimated time:** 7 hours

---

## File Structure

```
src/translation/
  ├── html_format_mapper.py      # ODT translation (existing, working)
  └── docx_html_mapper.py         # DOCX translation (new, to create)

tests/com8/
  ├── test_end_to_end_translation_COM8.py    # ODT tests (existing)
  ├── test_docx_html_mapper_COM8.py          # Unit tests (new)
  └── test_docx_end_to_end_COM8.py           # Integration test (new)

docs/com8/
  ├── PHASE1_1_CURRENT_DOCX_ANALYSIS_COM8.md
  ├── PHASE1_2_ODT_SUCCESS_TECHNIQUES_COM8.md
  ├── PHASE1_3_DOCX_API_RESEARCH_COM8.md
  ├── PHASE2_DOCX_MAPPER_DESIGN_COM8.md      # This file
  └── PHASE3_IMPLEMENTATION_SUMMARY_COM8.md  # After implementation
```

---

## Dependencies

```python
# Standard library
import html
from html.parser import HTMLParser
from typing import Dict, List, Optional

# Third-party (already in project)
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
```

**Status:** ✅ All dependencies already available

---

## Risks and Mitigation

### Risk 1: Unexpected run.text content

**Mitigation:** Comprehensive unit tests for _split_run_text()

**Status:** Low risk (tested in Phase 1.3)

### Risk 2: Format extraction differences

**Mitigation:** Reuse proven code from format_mapper.py

**Status:** Very low risk (already working)

### Risk 3: Google Translate changes HTML

**Mitigation:** Use same markers as ODT (proven to work)

**Status:** Very low risk (identical to ODT)

---

## Success Criteria

### Must Have
- ✅ 18 paragraphs (same as original)
- ✅ 14 tabs (all preserved)
- ✅ 22 line-breaks (all preserved)
- ✅ Format preservation (bold, font, color)
- ✅ No visible tags/placeholders in output

### Nice to Have
- ✅ Performance comparable to ODT
- ✅ Clear error messages
- ✅ Debug mode (save intermediate HTML)

---

## Phase 2 Complete ✅

**Confidence Level:** 100%

**Rationale:**
- 90% code reuse from proven ODT implementation
- Only 1 new function: _split_run_text() (simple algorithm)
- DOCX API simpler than ODT (verified in Phase 1.3)
- All edge cases identified and solutions designed

**Ready for Phase 3: Implementation** ✅
