# Investigation Ideas - Google Translate Tag Corruption

## 🔬 **IDEA 1: Placeholder Approach (Most Promising)**

**Concept**: Replace tags with Unicode placeholders that Google won't recognize as HTML

```python
# Before translation:
<113|65536:Arial,9|0,0>RISCOS PARA A AGRICULTURA: </113|65536>

# Convert to:
【TAG001】RISCOS PARA A AGRICULTURA: 【/TAG001】

# Google translates:
【TAG001】RISKS TO AGRICULTURE: 【/TAG001】

# Restore after:
<113|65536:Arial,9|0,0>RISKS TO AGRICULTURE: </113|65536>
```

**Why this works**:
- Unicode brackets 【】 are treated as regular text
- Google won't try to "fix" or interpret them
- 100% tag preservation guaranteed

**Test Plan**:
1. Create tag-to-placeholder mapping
2. Replace all tags before translation
3. Translate with placeholders
4. Restore original tags with translated text
5. Compare with current approach

**Pros**: ✅ Bulletproof, ✅ Preserves all formatting
**Cons**: ⚠️ More complex code, ⚠️ Need unique IDs

---

## 🔬 **IDEA 2: Escape Tags as Text Entities**

**Concept**: Convert `<>` to HTML entities so Google sees them as text

```python
# Before:
<113|65536>text</113|65536>

# Escape to:
&lt;113|65536&gt;text&lt;/113|65536&gt;

# Google translates (keeps entities):
&lt;113|65536&gt;translated text&lt;/113|65536&gt;

# Unescape after:
<113|65536>translated text</113|65536>
```

**Test**: Does Google preserve HTML entities through translation?

---

## 🔬 **IDEA 3: Use data-* HTML Attributes**

**Concept**: Embed formatting as valid HTML data attributes

```html
<!-- Before: -->
<span data-fmt="113|65536:Arial,9|0,0">RISCOS</span>

<!-- Google might preserve valid HTML better -->
```

**Why**: Google might respect valid HTML structure better than custom tags

**Risk**: Google might still strip/modify HTML

---

## 🔬 **IDEA 4: JSON Encoding in Comments**

**Concept**: Hide formatting in HTML comments

```html
<!--FMT:113|65536-->RISCOS PARA A AGRICULTURA: <!--/FMT-->
```

**Test**: Does Google preserve or strip HTML comments?

---

## 🔬 **IDEA 5: Zero-Width Character Markers**

**Concept**: Use invisible Unicode markers around formatted text

```python
# Mark boundaries with zero-width characters:
\u200B<113|65536>\u200CRISCOS\u200B</113|65536>\u200C

# Zero-width chars prevent Google from merging/breaking tags
```

**Test**: Do zero-width characters protect tag boundaries?

---

## 🔬 **IDEA 6: Simplify Metadata to Numbers Only**

**Concept**: Remove ALL text from tags, use numeric codes

```python
# Current (breaks):
<113|65536:525252,9,Arial|0,0>text</113|65536>

# Simplified:
<113|65536>text</113|65536>

# Or even simpler:
<113>text</113>
```

**Test Cases**:
- Just char code: `<113>text</113>`
- Char + para: `<113|65536>text</113|65536>`
- With numeric metadata: `<113|65536:1,2,3|4,5>text</113|65536>`

**Question**: Which level of simplification works?

---

## 🔬 **IDEA 7: Split Translation by Formatting Segments**

**Concept**: Never send tags to Google - translate text segments separately

```python
# Parse first:
segments = [
  {text: "RISCOS PARA A AGRICULTURA: ", format: {...}},
  {text: "long paragraph text...", format: {...}}
]

# Translate each text individually:
for seg in segments:
  seg.text = translate(seg.text)  # No tags sent!

# Rebuild with original formatting
```

**Pros**: ✅ No tag corruption possible, ✅ Granular translation
**Cons**: ⚠️ Many API calls, ⚠️ Loses context between segments

---

## 🔬 **IDEA 8: Test Chunk 6 Variations**

**Scientific approach**: Change ONE variable at a time

```python
tests = [
  "Remove nbsp (\\xa0)",
  "Remove colon after header",
  "Add space between tags",
  "Shorten text to 100 chars",
  "Change RISCOS to PERIGOS",
  "Remove CAPS (Riscos instead of RISCOS)",
  "Use different tag numbers",
  "Swap bold/normal (112 for header, 113 for body)"
]
```

**Goal**: Find EXACT trigger that causes deletion

---

## 🔬 **IDEA 9: Try Different Translation Services**

**Test with**:
- DeepL API (paid, high quality)
- LibreTranslate (free, open source, local)
- Azure Translator
- AWS Translate

**Question**: Is this a Google-specific bug or universal?

---

## 🔬 **IDEA 10: Inspect Google's Internal Processing**

**Deep dive**:
1. Check network traffic - what exactly is sent/received?
2. Test Google Translate web interface manually with same text
3. Check if Google has HTML preservation modes/parameters
4. Test with `translate_html=true` parameter (if exists)

---

## 🎯 **RECOMMENDED PRIORITY**

### **High Priority** (Test First):
1. ⭐ **IDEA 1**: Placeholder approach - Most bulletproof
2. ⭐ **IDEA 6**: Simplify to numbers only - Easiest to test
3. ⭐ **IDEA 8**: Systematic chunk 6 variations - Find root cause

### **Medium Priority**:
4. **IDEA 7**: Split by segments - No tags in translation
5. **IDEA 2**: HTML entities - Simple escaping
6. **IDEA 9**: Try other services - Check if universal issue

### **Low Priority** (Experimental):
7. **IDEA 5**: Zero-width characters
8. **IDEA 3**: data-* attributes
9. **IDEA 4**: HTML comments

---

## 🤔 **My Recommendation**

**Start with a 2-hour focused investigation**:

**Hour 1**: Quick wins
- Test IDEA 6 variations (5 min each = 30 min)
- Test IDEA 1 basic prototype (30 min)

**Hour 2**: Deep dive on winner
- Implement best approach fully
- Test with full biology document
- Verify all 7 headers preserved

**Expected outcome**: 95%+ tag preservation (up from 93.8%)

---

## 💡 **Questions for You**

1. **Do you prefer**:
   - A) 100% reliability with more complexity (placeholder)?
   - B) Simpler code with 95% reliability (simplified tags)?

2. **Can we modify the tag format**?
   - Store font names separately?
   - Use numeric font IDs instead of "Arial"?

3. **Performance concerns**?
   - OK to make multiple API calls (segment approach)?
   - Or must be single translation call?

4. **Do you want me to**:
   - Test all ideas systematically?
   - Or implement the most promising one now?

---

## 📊 **What We Know So Far**

✅ **Works**:
- Simple sentences with tags
- Pure number tags
- Short text

❌ **Breaks**:
- Pattern: `<bold>CAPS HEADER:</bold><normal>very long text</normal>`
- Symptom: Header text deleted, tag corrupted

🎯 **Goal**: 100% tag preservation for ALL document types

