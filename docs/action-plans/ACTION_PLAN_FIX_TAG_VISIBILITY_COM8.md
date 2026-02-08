# Action Plan: Fix Tag Visibility - Backend Only
**Programmer:** COM8 (Josué Amaral)  
**Date:** January 30, 2026  
**Branch:** COM8-documentation-reading  
**Protocol:** SIMPLICITY_PROTOCOL_3 (one issue per session)

---

## Problem Statement

**CRITICAL MISUNDERSTANDING IDENTIFIED:**

Current implementation shows formatting tags to users in UI:
- ❌ User sees `<1>Hello</1>` in input text box
- ❌ User sees `<3:FF0000>world</3>` in translation result box
- ❌ Tags visible throughout UI workflow
- ❌ "Remove formatting tags" checkbox exists (shouldn't be needed)

**Correct requirement:**
- ✅ Tags are 100% backend only (invisible to user)
- ✅ UI always shows plain text: "Hello world"
- ✅ Tags only exist during translation process internally
- ✅ Tags injected before API call, removed after response
- ✅ Formatting data stored separately in memory
- ✅ Formatting applied when saving DOCX (using stored data)

---

## Root Cause Analysis

**Where the mistake happened:**
1. Phase 1 Session 6: Integrated tags directly into UI text display
2. Phase 1 Session 7: Added "Remove tags" checkbox (workaround, not solution)
3. Phase 2 Sessions 1-7: Continued with visible tags approach
4. Never questioned if tags should be visible to user

**Why this happened:**
- Misunderstood user requirement about "tags for backend efficiency"
- Assumed tags visible to user for debugging/transparency
- Didn't ask clarifying questions about UI visibility

---

## Correct Architecture

### **Data Flow (Corrected):**

```
1. USER LOADS FILE
   ├─> document_parser.py: Extract plain text
   ├─> format_mapper.py: Extract formatting → TextSegment[]
   ├─> Store: self._format_segments (memory only)
   └─> Display: Plain text in UI (NO TAGS)

2. USER CLICKS TRANSLATE
   ├─> Get plain text from input box
   ├─> format_mapper.py: Inject tags using stored segments
   ├─> Tagged text: "<1>Hello</1> <3:FF0000>world</3>"
   ├─> Send to Google Translate API
   ├─> Receive translated: "<1>Hola</1> <3:FF0000>mundo</3>"
   ├─> format_mapper.py: Parse tags → new TextSegment[]
   ├─> Store: self._translated_segments (memory only)
   ├─> Extract plain text from segments
   └─> Display: Plain text in UI (NO TAGS)

3. USER CLICKS SAVE AS DOCX
   ├─> Use self._translated_segments (has formatting)
   ├─> format_mapper.py: create_docx_from_segments()
   └─> Save formatted DOCX file

4. USER CLICKS SAVE AS TXT
   ├─> Use plain text from UI
   └─> Save plain TXT file
```

---

## Implementation Plan

### **Session 1: Store Formatting Separately (UI Layer)**
**Objective:** Keep formatting in memory, show plain text in UI

**Changes to `google_translate_dock.py`:**
1. Add instance variables:
   ```python
   self._source_segments: List[TextSegment] = []  # Original formatting
   self._translated_segments: List[TextSegment] = []  # Translated formatting
   ```

2. Modify `_browse_file()`:
   - Extract formatting using FormatMapper → store in `self._source_segments`
   - Extract ONLY plain text → display in input text box (no tags)

3. Remove `chk_remove_tags` checkbox (no longer needed)

**Test:**
- Load DOCX with bold text → UI shows plain "Hello world" (no `<1>` tags)
- Internal: `self._source_segments` contains formatting data

**Commit:** "Session 1: Store formatting in memory, hide tags from UI"

---

### **Session 2: Inject Tags Before Translation Only**
**Objective:** Tags only exist during API call

**Changes to `google_translate_dock.py`:**
1. Modify `_translate()`:
   ```python
   # Get plain text from UI
   plain_text = self.text_input.toPlainText()
   
   # Inject tags using stored formatting (BACKEND ONLY)
   if self._source_segments:
       tagged_text = FormatMapper.inject_tags_into_text(plain_text, self._source_segments)
   else:
       tagged_text = plain_text
   
   # Send tagged text to Google Translate
   result = self._translator.translate(tagged_text, to_code, from_code)
   
   # Result contains tags: "<1>Hola</1> mundo"
   ```

2. Add method to FormatMapper:
   ```python
   @staticmethod
   def inject_tags_into_text(plain_text: str, segments: List[TextSegment]) -> str:
       """Reconstruct tagged text from plain text + segments."""
       # Rebuild tagged format from segments
       return ''.join(seg.to_tagged_text() for seg in segments)
   ```

**Test:**
- User clicks Translate
- Backend sends `<1>Hello</1>` to API (user doesn't see this)
- API returns `<1>Hola</1>`

**Commit:** "Session 2: Inject tags before API call only"

---

### **Session 3: Parse Tags and Hide After Translation**
**Objective:** Remove tags from UI after receiving translation

**Changes to `google_translate_dock.py`:**
1. Modify `_on_translation_completed()`:
   ```python
   def _on_translation_completed(self, result: TranslationResult):
       translated_with_tags = result.translated_text
       
       # Parse tags → extract formatting + plain text
       self._translated_segments = FormatMapper.parse_tagged_text(translated_with_tags)
       
       # Extract ONLY plain text for UI display
       plain_text = ''.join(seg.text for seg in self._translated_segments)
       
       # Display plain text (NO TAGS VISIBLE)
       self.text_output.setPlainText(plain_text)
       
       # Store detected language
       self._last_detected_lang = result.source_language
       
       # Update status
       self._update_status("google_translate.success")
   ```

2. Remove old tag removal logic (lines 536-541) - no longer needed

**Test:**
- After translation completes
- UI shows plain "Hola mundo" (no `<1>` tags visible)
- Internal: `self._translated_segments` contains formatting

**Commit:** "Session 3: Hide tags from translation output"

---

### **Session 4: Update Save Logic**
**Objective:** Use stored segments for DOCX, plain text for TXT

**Changes to `google_translate_dock.py`:**
1. Modify `_save_as_docx()`:
   ```python
   def _save_as_docx(self, file_path: str):
       """Save translation as formatted DOCX using stored segments."""
       if not self._translated_segments:
           # Fallback: plain text if no formatting
           plain_text = self.text_output.toPlainText()
           # Create segments from plain text
           self._translated_segments = [TextSegment(text=plain_text)]
       
       # Generate DOCX using formatting data
       FormatMapper.create_docx_from_segments(self._translated_segments, file_path)
   ```

2. Verify `_save_as_txt()` uses plain text from UI (already correct)

**Test:**
- Translate formatted document
- Save as DOCX → formatting preserved ✓
- Save as TXT → plain text only ✓
- User never saw tags in UI ✓

**Commit:** "Session 4: Use stored segments for DOCX export"

---

### **Session 5: Remove Obsolete Code**
**Objective:** Clean up tag checkbox and related code

**Changes to `google_translate_dock.py`:**
1. Remove `chk_remove_tags` widget (lines ~182-188)
2. Remove checkbox from layout (lines ~280-283)
3. Remove old tag removal logic (if any remains)
4. Update `_get_plain_text_for_display()` if exists

**Changes to `src/i18n/en.json`:**
1. Remove `chk_remove_tags` key (line ~709)
2. Remove `tooltip_remove_tags` key (line ~721)
3. Keep `status_docx_saved` (still needed)

**Test:**
- UI cleaner (no checkbox)
- All workflows still work
- No references to removed code

**Commit:** "Session 5: Remove obsolete tag checkbox UI"

---

### **Session 6: Add Helper Method to FormatMapper**
**Objective:** Utility for plain text extraction

**Changes to `format_mapper.py`:**
1. Add static method:
   ```python
   @staticmethod
   def extract_plain_text_from_segments(segments: List[TextSegment]) -> str:
       """Extract plain text from segments (no tags, no formatting)."""
       return ''.join(seg.text for seg in segments)
   ```

2. Update docstring examples to clarify backend-only usage

**Test:**
- Helper method returns clean plain text
- No tags in output

**Commit:** "Session 6: Add plain text extraction helper"

---

### **Session 7: Update Documentation**
**Objective:** Correct docs to reflect backend-only tags

**Changes:**
1. Update `DOCX_FORMATTING_FEATURE_GUIDE_COM8.md`:
   - Remove section showing tags in UI
   - Add "Tags are invisible to users (backend only)"
   - Update screenshots/examples (if any show tags)

2. Update `PHASE2_COMPLETE_FORMAT_RESTORATION_COM8.md`:
   - Add note: "CORRECTED: Tags now backend-only"

3. Create new doc: `FIX_TAG_VISIBILITY_REPORT_COM8.md`:
   - Explain the mistake
   - Document the fix
   - Lessons learned

**Test:**
- Documentation accurate
- No mention of visible tags in UI

**Commit:** "Session 7: Update docs - tags are backend only"

---

### **Session 8: Comprehensive Testing**
**Objective:** Verify complete workflow with hidden tags

**Test Cases:**
1. **Load DOCX with formatting**
   - UI shows: plain text only ✓
   - No tags visible ✓

2. **Translate**
   - Input shows: plain text ✓
   - Output shows: plain text ✓
   - Backend uses tags (verify with debug prints) ✓

3. **Save as DOCX**
   - Formatting preserved ✓
   - File opens correctly in Word/LibreOffice ✓

4. **Save as TXT**
   - Plain text only ✓
   - No tags in file ✓

5. **Edge cases**
   - Plain TXT file → translate → save ✓
   - Empty file ✓
   - Very long document ✓
   - Multiple formats combined ✓

**Create:** `FIX_VALIDATION_REPORT_COM8.md` with test results

**Commit:** "Session 8: Validation complete - tags hidden from users"

---

## Success Criteria

### **Must Have:**
- ✅ User NEVER sees tags in any UI element
- ✅ Tags only exist in memory during translation
- ✅ Formatting still preserved in DOCX output
- ✅ Plain text TXT output has no tags
- ✅ All existing features still work
- ✅ Documentation updated

### **Technical Verification:**
- ✅ `self._source_segments` stores original formatting
- ✅ `self._translated_segments` stores translated formatting
- ✅ UI text boxes show only plain text
- ✅ Tags injected before API call
- ✅ Tags removed after API response
- ✅ No "remove tags" checkbox in UI

### **User Experience:**
- ✅ Cleaner UI (no confusing tags)
- ✅ Same workflow as before
- ✅ Formatting still works transparently
- ✅ No breaking changes to functionality

---

## Timeline

**Estimated:** 8 sessions × 15-30 min = 2-4 hours total

**Session breakdown:**
- Sessions 1-4: Core functionality (critical)
- Session 5: Cleanup (important)
- Session 6: Helpers (nice to have)
- Session 7: Documentation (required)
- Session 8: Testing (critical)

---

## Risks & Mitigation

**Risk 1:** Breaking existing translation workflow
- **Mitigation:** Test after each session, keep backups

**Risk 2:** Losing formatting during text manipulation
- **Mitigation:** Store segments before any text changes

**Risk 3:** Tags still leak into UI edge cases
- **Mitigation:** Comprehensive testing in Session 8

---

## Notes

**Lesson learned:**
- Always ask clarifying questions about user-facing vs backend functionality
- "Tags for efficiency" meant backend optimization, not UI visibility
- User experience > implementation details

**Protocol compliance:**
- Following SIMPLICITY_PROTOCOL_3: one issue per session
- Each session has clear objective and test
- Commits after each successful session

---

**STATUS:** Ready to begin Session 1
**NEXT:** Store formatting in memory, hide tags from UI
