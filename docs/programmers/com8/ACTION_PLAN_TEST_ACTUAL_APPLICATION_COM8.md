# ACTION PLAN: Test Application with Real ODT File

**Programmer**: COM8  
**Date**: 2026-02-09  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: Need to test actual application with ODT file, not just isolated code

---

## PROBLEM STATEMENT

I fixed bugs in code but DID NOT test the actual application:
- ❌ Did not run ./clarify.sh
- ❌ Did not open Google Translate tool
- ❌ Did not load ODT file through UI
- ❌ Did not verify preview display
- ❌ Did not test translation
- ❌ Did not test Save As ODT
- ❌ Did not inspect resulting ODT file

**This violates protocol** - I must test the actual integration, not just isolated code!

---

## TESTING PLAN

### Phase 1: Launch Application
```bash
cd clarify-COM8
./clarify.sh
```

**Expected**: Application launches without errors

---

### Phase 2: Load ODT File
1. Open Google Translate tool (Tools → Google Translate)
2. Click "Browse" button
3. Select: `/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt`

**Check Preview Display:**
- [ ] NO CSS classes visible (`.fmt1`, `.fmt2`, etc.)
- [ ] Line breaks preserved
- [ ] Blank lines preserved
- [ ] Tab characters preserved
- [ ] Numbered list items on separate lines
- [ ] Headers separated from body text

**Expected Output Example:**
```
CAIT			13/11/12
Nome: Josué	
Turma: 3001

			Trabalho de Biologia

Transgênicos
CONCEITO: são alimentos...

RISCOS PARA A SAÚDE: ...

1. Aumento das alergias
Quando se insere um gene...
```

---

### Phase 3: Translate
1. Select: Portuguese → English
2. Click "Translate"
3. Wait for completion

**Check Translation Result:**
- [ ] NO CSS classes visible
- [ ] Line breaks preserved
- [ ] Formatting looks correct
- [ ] Translation completed successfully

---

### Phase 4: Save As ODT
1. Click "Save As..." button
2. Save to: `/home/josue/Documents/test_translation_COM8_VERIFY.odt`
3. **CAPTURE TERMINAL DEBUG OUTPUT**

**Expected Debug Output:**
```
[DEBUG] _save_as_odt called:
  _translated_html: True (length: XXXX)
  _css_manager: True (type: CSSClassManager)
  → Using HTML system
  → ODT created successfully
```

---

### Phase 5: Inspect Saved ODT
```bash
# Check ODT structure
python3 << 'EOF'
from odf import opendocument, text, style

doc = opendocument.load('/home/josue/Documents/test_translation_COM8_VERIFY.odt')

# Count styles
styles = list(doc.automaticstyles.childNodes)
print(f"Automatic styles: {len(styles)}")

# Count paragraphs
paras = doc.text.getElementsByType(text.P)
print(f"Paragraphs: {len(paras)}")

# Check if styles exist
for s in styles[:5]:
    if hasattr(s, 'getAttribute'):
        name = s.getAttribute('name')
        if name:
            print(f"  Style: {name}")

# Check first paragraph has formatting
if paras:
    first_para = paras[0]
    print(f"First paragraph has children: {len(first_para.childNodes)}")
EOF
```

**Expected Results:**
- Automatic styles: **8+** (fmt1-fmt8)
- Paragraphs: **Multiple** with formatting
- First paragraph has styled spans

**If FAILED:**
- Automatic styles: **0**
- Paragraphs: **1** (plain text only)
- → Bug 3 confirmed - needs fix

---

### Phase 6: Visual Verification
```bash
# Open saved file in LibreOffice
libreoffice /home/josue/Documents/test_translation_COM8_VERIFY.odt
```

**Visual Checks:**
- [ ] Bold text is bold
- [ ] Font sizes correct
- [ ] Colors preserved
- [ ] Layout matches original
- [ ] No visible format tags

---

## TESTING CHECKLIST

**Application Launch:**
- [ ] ./clarify.sh runs without errors
- [ ] GUI opens correctly

**File Loading:**
- [ ] ODT file loads
- [ ] Preview shows correct content
- [ ] NO CSS classes visible
- [ ] Line breaks preserved
- [ ] Tabs/indentation preserved
- [ ] Headers separated from body

**Translation:**
- [ ] Translation completes
- [ ] Result shows correct content
- [ ] NO CSS classes visible
- [ ] Formatting preserved

**Save As ODT:**
- [ ] Debug output captured
- [ ] Shows "Using HTML system"
- [ ] File created successfully

**ODT Inspection:**
- [ ] Has automatic styles (8+)
- [ ] Has multiple paragraphs
- [ ] Formatting preserved

**Visual Check:**
- [ ] Opens in LibreOffice
- [ ] Bold/italic/colors correct
- [ ] Layout matches original

---

## EXPECTED ISSUES

### Issue 1: Preview might still have bugs
- Even though code logic works in isolation
- UI integration might have issues

### Issue 2: Translation might fail
- Network issues
- Google Translate API changes

### Issue 3: Save might not use HTML system
- Debug output will show which path taken
- If uses OLD system → Bug 3 confirmed
- If uses FALLBACK → Bug 3 confirmed

---

## DOCUMENTATION TO CREATE

After testing, create:
```
docs/com8/TEST_RESULTS_ACTUAL_APPLICATION_COM8.md
```

Include:
- Screenshots (if possible)
- Terminal output
- Debug output from save
- ODT inspection results
- What worked / what failed
- Next steps if bugs found

---

## STATUS: Ready to test - need to actually run the application!

**Honest admission**: I should have done this BEFORE claiming bugs were fixed.

**What I'll do now**: Run every step, document results, report honestly what works and what doesn't.

EOF
