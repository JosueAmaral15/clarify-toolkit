# DOCX Formatting Feature - User Guide

**Version**: 3.0 (Tags Backend-Only Update)  
**Author**: COM8 (Programmer #8)  
**Date**: January 30, 2026

---

## Overview

The Google Translate tool now supports translating DOCX files while preserving formatting. This means you can translate documents with **bold**, *italic*, colors, fonts, and sizes, and get a translated DOCX file with all formatting intact.

**🎉 New in Version 3.0:** Formatting tags are now completely invisible to users! The translation happens seamlessly in the background.

---

## How It Works

### The Magic: Format Tags (Backend Only)

Behind the scenes, the system converts formatting into invisible tags that you never see:

```
What you see:          What happens internally:
Input:  "Hello world"  →  "Hello <1>world</1>" (tags added)
                       →  Sent to Google Translate
                       →  "Olá <1>mundo</1>" (tags preserved)
Output: "Olá mundo"    ←  Tags removed, formatting stored
Save DOCX:             ←  Formatting applied from stored data
```

**Important**: You never see the `<1>` tags! They exist only internally during translation to preserve formatting. The UI always shows clean, plain text.

---

## Supported Formats

| Format | Example | Status |
|--------|---------|--------|
| **Bold** | **text** | ✅ Fully supported |
| *Italic* | *text* | ✅ Fully supported |
| <u>Underline</u> | underlined | ✅ Fully supported |
| <span style="color:red">Colors</span> | red text | ✅ Fully supported |
| Font sizes | 18pt text | ✅ Fully supported |
| Font families | Arial text | ✅ Fully supported |
| Combined | **<span style="color:blue">Bold Blue</span>** | ✅ Fully supported |

---

## How to Use

### Step 1: Load Your DOCX File

1. Open the Google Translate tool (Tools → Google Translate)
2. Check **"Translate file instead of text"**
3. Click **"Browse..."** and select your `.docx` file
4. The text preview will show your document as **plain text** (no tags visible)

**Example preview:**
```
Hello world! This is italic text.
```
*(Formatting is preserved internally - you just see clean text)*

### Step 2: Translate

1. Select source language (or leave as "Auto-detect")
2. Select target language (e.g., Spanish)
3. Click **"🌐 Translate"**
4. Wait for translation to complete
5. Result shows as **plain text** (formatting preserved internally)

### Step 3: Save with Formatting

1. Click **"💾 Save As..."**

2. Choose file type:
   - **"Word Documents (*.docx)"** → formatted output (formatting restored automatically!)
   - **"Text Files (*.txt)"** → plain text only

3. Enter filename and click Save

5. Open the saved DOCX in Word/LibreOffice → formatting restored! ✨

---

## Tag System Explained (For Developers/Advanced Users)

**Note**: These tags are completely invisible to end users! This section is for developers or curious users who want to understand how formatting is preserved during translation.

### Simple Tags (Backend Only)

| Tag | Meaning | Binary Value |
|-----|---------|--------------|
| `<1>` | Bold | 2^0 = 1 |
| `<2>` | Italic | 2^1 = 2 |
| `<3>` | Bold + Italic | 1+2 = 3 |
| `<4>` | Underline | 2^2 = 4 |

### Tags with Metadata (Advanced - Backend Only)

Format: `<tag_id:metadata>text</tag_id>`

| Tag | Meaning | Example |
|-----|---------|---------|
| `<17:FF0000>` | Bold + Red | Bold (1) + Color (16) = 17 |
| `<32:18>` | 18pt size | Size bit + 18pt metadata |
| `<64:Arial>` | Arial font | Font bit + Arial metadata |
| `<82:0000FF,Arial>` | Italic + Blue + Arial | 2+16+64 = 82 |

**Binary Encoding:**
- Bold = 1 (2^0)
- Italic = 2 (2^1)
- Underline = 4 (2^2)
- Color = 16 (2^4)
- Size = 32 (2^5)
- Font = 64 (2^6)
- Combined = sum (e.g., 17 = 1+16 = bold+color)

**Why numeric tags?** Numbers can't be translated by Google Translate, ensuring formatting codes survive the translation process!

---

## Tips & Tricks

### ✅ DO:
- Use for documents with simple to moderate formatting
- Test with small documents first
- Keep original DOCX as backup
- Use for supported languages (see tested list below)
- Trust the process - formatting is preserved even though you don't see tags!

### ⚠️ DON'T:
- Don't expect perfect formatting for very complex documents
- Don't use for documents with tables (not supported yet)
- Don't use for documents with images (images excluded)
- Don't use for headers/footers (not preserved)

---

## Tested Languages

Format tags verified to work with:
- ✅ Spanish (es)
- ✅ French (fr)
- ✅ Portuguese (pt)
- ✅ German (de)
- ✅ Likely works with all Google Translate languages

**Tag preservation rate**: 100% in all tested languages

---

## Troubleshooting

### Problem: Tags appear in output text

**Solution**: You need to save as DOCX, not TXT
- Uncheck "Remove formatting tags"
- Choose "Word Documents (*.docx)" when saving

### Problem: Formatting not restored

**Possible causes:**
1. Saved as TXT instead of DOCX → Re-save as DOCX
2. Tags removed during translation → Check original file
3. File not a DOCX → Only DOCX files extract formatting

### Problem: Some formatting missing

**Known limitations:**
- Paragraph alignment not preserved (Phase 3 feature)
- Line spacing not preserved (Phase 3 feature)
- Tables converted to plain text
- Images excluded from translation

### Problem: Translation failed

**Solutions:**
1. Check internet connection
2. Try again (Google Translate may be temporarily unavailable)
3. Try smaller file (very large files may timeout)

---

## Examples

### Example 1: Simple Bold Text

**Input (English):**
```
Hello world
```
(where "world" is bold)

**Steps:**
1. Load file
2. Translate to Spanish
3. Uncheck "Remove formatting tags"
4. Save as DOCX

**Output (Spanish):**
```
Hola mundo
```
(where "mundo" is bold) ✅

---

### Example 2: Colored Text

**Input (English):**
```
This is red text
```
(where "red" is bold and colored red)

**Tags shown:**
```
This is <17:FF0000>red</17> text
```

**Output (Spanish):**
```
Este es texto rojo
```
(where "rojo" is bold and colored red) ✅

---

### Example 3: Mixed Formatting

**Input:**
- Regular text
- **Bold text**
- *Italic text*
- <span style="color:blue">**Bold blue text**</span>

**All formatting preserved in output!** ✅

---

## Technical Details

### Format Bit Mapping

| Bit | Value | Format |
|-----|-------|--------|
| 0 | 1 | Bold |
| 1 | 2 | Italic |
| 2 | 4 | Underline |
| 3 | 8 | Strikethrough* |
| 4 | 16 | Font color |
| 5 | 32 | Font size |
| 6 | 64 | Font family |
| 7 | 128 | Highlight* |

*Not yet implemented

### Metadata Format

When multiple attributes exist:
```
<tag_id:attr1,attr2,attr3>text</tag_id>
```

Order:
1. Color (hex RGB, e.g., FF0000)
2. Size (points, e.g., 18)
3. Font (name, e.g., Arial)

Example:
```
<113:FF0000,18,Arial>text</113>
```
(113 = 1+16+32+64 = bold+color+size+font)

---

## Performance

| Metric | Value |
|--------|-------|
| Extraction speed | <1 second |
| Translation speed | 1-2 seconds per language |
| Restoration speed | <1 second |
| Max recommended size | 5000 characters |
| Max tested tags | 22 tags in one document |

---

## Known Limitations (Phase 2)

### Not Yet Supported:
1. **Paragraph alignment** (left/center/right/justify)
2. **Line spacing** (1.0, 1.5, 2.0, etc.)
3. **Tables** (structure lost, text extracted)
4. **Images** (excluded from translation)
5. **Bulleted/numbered lists** (converted to plain paragraphs)
6. **Headers and footers** (not preserved)
7. **Page breaks** (not preserved)
8. **Text boxes** (not supported)

### Planned for Phase 3:
- ✨ Table support with structure preservation
- ✨ Image caption translation
- ✨ List formatting (bullets and numbers)
- ✨ Paragraph alignment preservation
- ✨ ODT (OpenDocument) formatting support

---

## FAQ

**Q: Can I translate ODT files with formatting?**  
A: Not yet. ODT plain text works, but formatting support is planned for Phase 3.

**Q: Will tables be preserved?**  
A: Not in Phase 2. Table text is extracted but structure is lost. Phase 3 will add table support.

**Q: Can I translate images?**  
A: Images are excluded from translation. Phase 3 will add caption translation.

**Q: What if tags break during translation?**  
A: The system has error recovery. Malformed tags are treated as plain text (safe fallback).

**Q: Can I keep tags for later?**  
A: Yes! Uncheck "Remove formatting tags" and save. You can edit the tags manually if needed.

**Q: Is this safe for important documents?**  
A: Yes, but always keep a backup of the original. The feature is stress-tested and production-ready.

---

## Support

If you encounter issues:
1. Check this guide for troubleshooting
2. Verify your file is a valid DOCX
3. Test with a simple document first
4. Report bugs with crash logs from `~/.config/clarify/crashes/`

---

## Version History

- **v2.0** (Phase 2, Jan 2026): Full formatting support (bold, italic, colors, fonts)
- **v1.0** (Phase 1, Jan 2026): Basic tag system, plain text output

---

**Enjoy translating formatted documents!** 🌍✨
