# TESTING INSTRUCTIONS: Google Translate CSS Bug Fixes

**Programmer**: COM8  
**Date**: 2026-02-09  
**Commit**: e377a83  
**Protocol**: SIMPLICITY_PROTOCOL_3  

---

## ✅ FIXED BUGS

### Bug 1: CSS Classes Visible in File Preview
- **Status**: FIXED
- **Location**: `_browse_file()` line 489-519

### Bug 2: CSS Classes Visible in Translation Result
- **Status**: FIXED  
- **Location**: `_on_translation_completed()` line 668-707

---

## 🧪 TEST PHASE 1: CSS Display (Ready to test NOW)

### Test 1.1: Load ODT File
1. Launch application from COM8 worktree:
   ```bash
   cd ~/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify-COM8
   ./clarify.sh
   ```

2. Open Google Translate tool (Tools → Google Translate)

3. Click "Browse" and select:
   ```
   ~/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt
   ```

4. **CHECK FILE CONTENT PREVIEW**:
   - ❌ **BEFORE**: Shows `.fmt1 { font-weight: bold; ... } .fmt2 { ... } CAIT...`
   - ✅ **AFTER**: Should show ONLY: `CAIT 13/11/12 Nome: Josué Turma: 3001...`
   - ✅ **NO CSS CLASSES VISIBLE**

### Test 1.2: Translate File
1. Select languages: Portuguese → English
2. Click "Translate" button
3. Wait for translation to complete

4. **CHECK TRANSLATION RESULT**:
   - ❌ **BEFORE**: Shows CSS classes before translated text
   - ✅ **AFTER**: Should show ONLY translated text starting with "CAIT 13/11/12 Name: Joshua..."
   - ✅ **NO CSS CLASSES VISIBLE**

### Expected Results Phase 1
```
✅ Preview text: "CAIT 13/11/12 Nome: Josué Turma: 3001 Trabalho de Biologia..."
✅ Translation result: "CAIT 13/11/12 Name: Joshua Class: 3001 Biology Assignment..."
✅ NO .fmt1, .fmt2, or any CSS classes visible
```

---

## 🔍 TEST PHASE 2: ODT Formatting Preservation (Needs debug output)

### Test 2.1: Save Translated ODT
1. After translation completes, click "Save As..." button
2. Save to: `/home/josue/Documents/test_translation_COM8.odt`

### Test 2.2: Capture Debug Output
**CRITICAL**: Watch the terminal for debug output like this:
```
[DEBUG] _save_as_odt called:
  _translated_html: True (length: 1234)
  _css_manager: True (type: CSSClassManager)
  → Using HTML system
  → ODT created successfully
```

**Copy the ENTIRE debug output and send to me!**

### Test 2.3: Verify Saved File
```bash
python3 -c "
from odf import opendocument, text
doc = opendocument.load('/home/josue/Documents/test_translation_COM8.odt')
styles = doc.automaticstyles.childNodes
paras = doc.text.getElementsByType(text.P)
print(f'Automatic styles: {len(styles)}')
print(f'Paragraphs: {len(paras)}')
"
```

### Expected Results Phase 2
```
✅ Debug shows: "Using HTML system"
✅ Automatic styles: 8+ (should have fmt1, fmt2, etc.)
✅ Paragraphs: Multiple with formatting
```

**If Phase 2 FAILS**, send me:
1. Terminal debug output
2. Output from verification script
3. I'll fix Bug 3 based on actual evidence

---

## 📋 QUICK TEST CHECKLIST

**Phase 1 (You can verify immediately):**
- [ ] Load ODT → NO CSS in preview
- [ ] Translate → NO CSS in result
- [ ] Text looks clean and readable

**Phase 2 (Needs your debug output):**
- [ ] Save ODT → Capture terminal output
- [ ] Run verification script
- [ ] Send me the results

---

## 🐛 KNOWN REMAINING BUGS

### Bug 3: ODT Save Formatting Loss (PENDING YOUR TEST)
- Debug logging is in place
- Need your test output to diagnose
- Will fix after analyzing your results

### Bug 4: _css_manager Re-extraction (LOW PRIORITY)
- CSS manager extracted twice (wasteful but harmless)
- Can optimize later if needed

---

## 📞 WHAT TO SEND ME

After testing, please provide:

1. **Phase 1 Result**: "✅ CSS bug fixed" or "❌ Still seeing CSS"
2. **Phase 2 Debug Output**: Copy/paste terminal output from save
3. **Phase 2 Verification**: Output from Python verification script

Then I can fix Bug 3 if needed!

---

## 🎯 CURRENT STATUS

- ✅ Bug 1 & 2: CSS display - FIXED (commit e377a83)
- ⏳ Bug 3: ODT formatting - NEEDS YOUR DEBUG OUTPUT
- ⏸️ Bug 4: CSS manager duplication - LOW PRIORITY

**Ready for your testing!**
