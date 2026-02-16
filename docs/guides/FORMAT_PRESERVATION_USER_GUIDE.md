# Google Translate Tool - Format Preservation Guide

**Version:** 2.9.117+  
**Last Updated:** February 1, 2026  
**Feature:** Document formatting preservation through translation

---

## 🌟 Overview

The Google Translate tool in Clarify now **preserves formatting** when translating DOCX and ODT documents! This means your bold text stays bold, your headings stay as headings, and your colors stay colorful—even after translation.

### What's New?
- ✅ **35 formats preserved** across character, paragraph, and document styles
- ✅ **Works with DOCX and ODT** files
- ✅ **Automatic detection** - no extra steps needed
- ✅ **Production-tested** with comprehensive test suite

---

## 🚀 Quick Start

### Basic Workflow

1. **Open Google Translate tool**
   - Menu: `Tools → Google Translate`
   - Or use keyboard shortcut (if configured)

2. **Load your document**
   - Click "Open File" button
   - Select a DOCX or ODT file
   - Formatting is automatically detected ✨

3. **Select languages**
   - Source language: Auto-detect or choose
   - Target language: Select from dropdown

4. **Translate**
   - Click "Translate" button
   - Wait for translation to complete
   - Preview shows translated text

5. **Save with formatting**
   - Click "Save Translation"
   - Choose format: Word Documents (.docx) or OpenDocument (.odt)
   - Select save location
   - Done! Your formatting is preserved 🎉

---

## 📋 Supported Formats

### ✅ Character Formatting (12 formats)

| Format | DOCX | ODT | Example |
|--------|------|-----|---------|
| **Bold** | ✅ | ✅ | **Bold text** |
| **Italic** | ✅ | ✅ | *Italic text* |
| **Underline** | ✅ | ✅ | <u>Underlined</u> |
| **Strikethrough** | ✅ | ✅ | ~~Strikethrough~~ |
| **Font Color** | ✅ | ✅ | <span style="color:red">Red text</span> |
| **Font Size** | ✅ | ✅ | Small (8pt) or Large (24pt) |
| **Font Family** | ✅ | ✅ | Arial, Times New Roman, etc. |
| **Highlight** | ✅ | ✅ | Yellow highlighted text |
| **Superscript** | ✅ | ✅ | x² |
| **Subscript** | ✅ | ✅ | H₂O |
| **Double Underline** | ✅ | ✅ | Double underlined |
| **Small Caps** | ✅ | ✅ | SMALL CAPITALS |

### ✅ Paragraph Formatting (9 formats)

| Format | DOCX | ODT | Description |
|--------|------|-----|-------------|
| **Alignment** | ✅ | ✅ | Left, Center, Right, Justify |
| **Line Spacing** | ✅ | ✅ | Single, 1.5, Double, custom |
| **Indentation** | ✅ | ✅ | First line, left margin, right margin |
| **Space Before/After** | ✅ | ✅ | Paragraph spacing |
| **Keep Lines Together** | ✅ | ✅ | Prevent paragraph splitting |
| **Keep With Next** | ✅ | ✅ | Keep with following paragraph |
| **Page Break Before** | ✅ | ✅ | Start on new page |
| **Widow/Orphan Control** | ✅ | ✅ | Single line prevention |
| **Bidirectional Text** | ✅ | ✅ | RTL/LTR text direction |

### ✅ Headings & Structure (4 formats)

| Format | DOCX | ODT | Example |
|--------|------|-----|---------|
| **Heading 1** | ✅ | ✅ | # Main Title |
| **Heading 2** | ✅ | ✅ | ## Subtitle |
| **Heading 3** | ✅ | ✅ | ### Section |
| **Heading 4-6** | ✅ | ✅ | #### Subsection |

### ✅ Lists (3 formats)

| Format | DOCX | ODT | Example |
|--------|------|-----|---------|
| **Bullet Lists** | ✅ | ✅ | • Item 1<br>• Item 2 |
| **Numbered Lists** | ✅ | ✅ | 1. First<br>2. Second |
| **Multi-level Lists** | ✅ | ✅ | Nested bullets/numbers |

### ✅ Hyperlinks (3+ formats)

| Format | DOCX | ODT | Example |
|--------|------|-----|---------|
| **Web Links** | ✅ | ✅ | http://example.com |
| **Email Links** | ✅ | ✅ | mailto:user@example.com |
| **File Links** | ✅ | ✅ | file:///path/to/file |
| **Custom Schemes** | ✅ | ✅ | tel:, ftp:, etc. |

### ✅ Special Characters (4 formats)

| Character | DOCX | ODT | Description |
|-----------|------|-----|-------------|
| **Non-breaking Space** | ✅ | ✅ | Prevents line break between words |
| **Non-breaking Hyphen** | ✅ | ✅ | Hyphen that doesn't break |
| **Soft Hyphen** | ✅ | ✅ | Optional hyphenation point |
| **Tab Characters** | ✅ | ✅ | Preserved tabs |

### ❌ Not Yet Supported

| Format | Status | Reason |
|--------|--------|--------|
| **Tables** | ⏳ Future | Requires architecture changes |
| **Images** | ❌ Deferred | Can't translate binary data |
| **Page Layout** | ⏳ Future | Document-level features |
| **Custom Styles** | ⏳ Future | Complex style mapping needed |

---

## 💡 Tips & Best Practices

### For Best Results

1. **Use standard formatting**
   - Stick to common fonts (Arial, Times New Roman, etc.)
   - Standard bullet points work best
   - Avoid overly complex nested structures

2. **Test before large batches**
   - Try one document first
   - Verify formatting is preserved correctly
   - Then process similar documents

3. **Save in same format**
   - DOCX → DOCX works best
   - ODT → ODT works best
   - Cross-format (DOCX → ODT) works but may have minor differences

4. **Keep backups**
   - Always keep original documents
   - Translation creates new files (doesn't overwrite)

### Performance Tips

- **Small documents** (< 10 pages): Instant
- **Medium documents** (10-50 pages): Few seconds
- **Large documents** (50+ pages): May take 30+ seconds
- **Very large documents** (100+ pages): Consider splitting

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### "Formatting looks different after translation"

**Possible causes:**
1. **Font not available** - Target system doesn't have the same font
   - Solution: Use common fonts (Arial, Times, Calibri)

2. **ODT → DOCX conversion** - Minor differences between formats
   - Solution: Save in same format as source

3. **Complex nested formatting** - Edge case formatting
   - Solution: Simplify formatting before translation

#### "Some text lost formatting"

**Possible causes:**
1. **Unsupported format** - Using tables, images, or page layout features
   - Solution: Check "Supported Formats" section above

2. **Custom styles** - Document uses custom paragraph/character styles
   - Solution: Apply formatting directly (not via styles)

#### "Translation is slow"

**Possible causes:**
1. **Large document** - 50+ pages with lots of formatting
   - Solution: Be patient, or split document

2. **Internet connection** - Google Translate API needs connectivity
   - Solution: Check network connection

3. **Complex formatting** - Every format adds processing time
   - Solution: Normal behavior for formatted documents

#### "Can't open saved file"

**Possible causes:**
1. **Wrong extension** - Saved with incorrect file extension
   - Solution: Use the format dropdown in save dialog

2. **Corrupted save** - Save process interrupted
   - Solution: Translate and save again

3. **Application compatibility** - Older MS Word/LibreOffice version
   - Solution: Update your office software

---

## 📖 Example Workflows

### Workflow 1: Simple Business Letter

**Scenario:** Translate a formatted business letter from English to Spanish

```
1. Letter has:
   - Bold company name
   - Italic greeting
   - Underlined important dates
   - Justified alignment

2. Steps:
   - Open letter.docx in Google Translate tool
   - Select: English → Spanish
   - Click "Translate"
   - Save as: carta.docx

3. Result:
   ✅ All formatting preserved
   ✅ Text translated to Spanish
   ✅ Ready to send!
```

### Workflow 2: Academic Paper

**Scenario:** Translate research paper with headings and citations

```
1. Paper has:
   - Heading 1 (Title)
   - Heading 2 (Sections)
   - Italic citations
   - Hyperlinks to references
   - Double-spaced text

2. Steps:
   - Open paper.docx
   - Select: English → Portuguese
   - Translate
   - Save as: artigo.docx

3. Result:
   ✅ Heading hierarchy preserved
   ✅ Citations stay italic
   ✅ Links still clickable
   ✅ Spacing maintained
```

### Workflow 3: Formatted Instructions

**Scenario:** Translate technical manual with lists

```
1. Manual has:
   - Numbered steps
   - Bullet point warnings
   - Bold safety notes
   - Multi-level nested lists

2. Steps:
   - Open manual.odt
   - Select: English → German
   - Translate
   - Save as: anleitung.odt

3. Result:
   ✅ Numbered steps preserved
   ✅ Bullets maintained
   ✅ Bold text stays bold
   ✅ Nesting structure intact
```

---

## 🎯 Advanced Features

### Hyperlink Preservation

Hyperlinks are fully preserved through translation:

```
Source:      Visit our [website](https://example.com) for more info.
Translated:  Visite nuestro [sitio web](https://example.com) para más información.
Result:      ✅ Link still works, text translated, URL unchanged
```

**Supported link types:**
- Web links (http://, https://)
- Email links (mailto:)
- File links (file:///)
- Custom schemes (tel:, ftp:, etc.)

### Special Character Handling

Special Unicode characters are automatically preserved:

- **Non-breaking spaces:** Keep words together on same line
- **Non-breaking hyphens:** Prevent word breaks at hyphens
- **Soft hyphens:** Optional hyphenation points
- **Tabs:** Preserved exactly

### Multi-format Support

**DOCX (Microsoft Word):**
- Full support for .docx files
- Compatible with Word 2007+
- Native format for Windows users

**ODT (OpenDocument):**
- Full support for .odt files
- Compatible with LibreOffice, OpenOffice
- Open standard format

**Cross-format conversion:**
- DOCX → ODT: Works well
- ODT → DOCX: Works well
- Minor differences possible (fonts, spacing)

---

## ❓ FAQ

**Q: Does this work with Google Docs files?**  
A: Not directly. Export your Google Doc as .docx first, then translate.

**Q: Can I translate .doc (old Word format)?**  
A: Convert to .docx first using Word or LibreOffice.

**Q: What about PDF files?**  
A: Not supported. Convert PDF to DOCX/ODT first (many tools available).

**Q: Does formatting slow down translation?**  
A: Slightly. Formatted documents take a few seconds longer to process.

**Q: Can I batch translate multiple documents?**  
A: Current version processes one document at a time. Batch feature planned.

**Q: Will my custom fonts be preserved?**  
A: Font names are preserved. Target system must have the font installed to display correctly.

**Q: What happens to comments and tracked changes?**  
A: Not currently preserved. Remove before translating.

**Q: Can I translate only part of a document?**  
A: Current version translates entire document. Use copy/paste for partial translation.

---

## 🆘 Getting Help

### Need More Help?

1. **Check this guide** - Most questions answered here
2. **Check troubleshooting section** - Common issues solved
3. **Review examples** - See workflows that match your use case
4. **Report bugs** - If something doesn't work, report it

### Reporting Issues

Include these details:
- Document format (DOCX or ODT)
- Source and target languages
- Formatting that didn't preserve
- Steps to reproduce
- Error messages (if any)

---

## 📊 Version History

**Version 2.9.117+ (February 2026)**
- ✅ Initial release of format preservation
- ✅ 35 formats supported
- ✅ DOCX and ODT support
- ✅ Comprehensive testing

**Planned Future Enhancements:**
- ⏳ Table support
- ⏳ Batch translation
- ⏳ Custom style preservation
- ⏳ Progress bars for large documents

---

## 🎉 Conclusion

Format preservation makes translating documents easier than ever! Your formatting is automatically detected and preserved through the entire translation process.

**Quick checklist:**
- ✅ Load DOCX or ODT file
- ✅ Select languages
- ✅ Translate
- ✅ Save in same format
- ✅ Formatting preserved!

**Enjoy formatted translations!** 🌍✨

---

*For technical documentation, see: `FINAL_PROJECT_STATUS_COM8.md`*  
*For developer details, see: `src/translation/format_mapper.py`*
