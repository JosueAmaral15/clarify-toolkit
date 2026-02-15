# ACTION PLAN: Add Comprehensive Debug Logging to Translation Process

**Programmer**: COM8  
**Date**: 2026-02-10  
**Protocol**: SIMPLICITY_PROTOCOL_3  
**Issue**: Need to track the ENTIRE translation process with debug logs

---

## PROBLEM STATEMENT

User correctly pointed out: I should add DEBUG LOGGING to track:
1. **BEFORE translation**: What HTML/text is sent to Google Translate
2. **DURING translation**: How Google Translate processes it
3. **AFTER translation**: What we receive back
4. **DURING save**: Which code path executes

This will reveal:
- Are format tags visible to the user?
- Is HTML preserved through translation?
- Which save system actually executes?

---

## DEBUG POINTS TO ADD

### Point 1: File Load (_browse_file)
```python
def _browse_file(self):
    # ... existing code ...
    if file_path.lower().endswith('.odt'):
        html_content, css_manager = HTMLFormatMapper.extract_html_from_odt(file_path)
        
        # DEBUG LOG
        print("\n[DEBUG] File loaded:")
        print(f"  HTML length: {len(html_content)}")
        print(f"  CSS classes: {len(css_manager.class_to_format) if css_manager else 0}")
        print(f"  HTML preview (first 300 chars): {html_content[:300]}")
        
        # Extract plain text for preview
        extractor = TextExtractor()
        extractor.feed(html_content)
        plain_text = extractor.get_text()
        
        # DEBUG LOG
        print(f"  Preview text length: {len(plain_text)}")
        print(f"  Preview contains CSS: {'.fmt' in plain_text}")
        print(f"  Preview contains HTML tags: {'<' in plain_text and '>' in plain_text}")
        print(f"  Preview first 200 chars: {plain_text[:200]}")
```

### Point 2: Translation Start (_translate)
```python
def _translate(self):
    # ... existing code ...
    if file_path.lower().endswith('.odt'):
        html_content, css_manager = HTMLFormatMapper.extract_html_from_odt(file_path)
        
        # DEBUG LOG
        print("\n[DEBUG] Starting translation:")
        print(f"  Text to translate is HTML: True")
        print(f"  HTML length: {len(html_content)}")
        print(f"  Contains <style>: {'<style>' in html_content}")
        print(f"  CSS manager stored: {self._css_manager is not None}")
        
        text_to_translate = html_content
```

### Point 3: Translation Worker (TranslationWorker.run)
```python
def run(self):
    # ... existing code ...
    is_html_format = '<!DOCTYPE html>' in self.text or '<html>' in self.text
    
    # DEBUG LOG
    print("\n[DEBUG] TranslationWorker:")
    print(f"  Input is HTML format: {is_html_format}")
    print(f"  Input length: {len(self.text)}")
    
    if is_html_format:
        print(f"  Protecting whitespace in HTML...")
        text_to_translate = protect_special_whitespace(self.text)
        print(f"  After protection: {len(text_to_translate)} chars")
    
    # ... translate ...
    
    # DEBUG LOG - After translation
    print("\n[DEBUG] Translation completed:")
    print(f"  Result length: {len(final_result)}")
    print(f"  Result is HTML: {'<!DOCTYPE' in final_result or '<html>' in final_result}")
    print(f"  Result first 300 chars: {final_result[:300]}")
```

### Point 4: Translation Result Display (_on_translation_completed)
```python
def _on_translation_completed(self, result, success, error, detected_lang):
    if success:
        is_html_format = '<!DOCTYPE html>' in result or '<html>' in result
        
        # DEBUG LOG
        print("\n[DEBUG] Translation result received:")
        print(f"  Is HTML format: {is_html_format}")
        print(f"  Result length: {len(result)}")
        
        if is_html_format:
            extractor = TextExtractor()
            extractor.feed(result)
            plain_text = extractor.get_text()
            
            # DEBUG LOG
            print(f"  Extracted plain text length: {len(plain_text)}")
            print(f"  Plain text contains CSS: {'.fmt' in plain_text}")
            print(f"  Plain text first 200 chars: {plain_text[:200]}")
            
            self._translated_html = result
```

### Point 5: Save As ODT (_save_as_odt)
**Already has debug logging!** (Added in previous commit)

---

## IMPLEMENTATION PLAN

### Step 1: Add Debug Flag
```python
# In google_translate_dock.py, add at top:
DEBUG_TRANSLATION = True  # Set to False to disable logs
```

### Step 2: Add Debug Helper Function
```python
def _debug_log(self, section: str, message: str):
    """Log debug information if debug mode enabled."""
    if DEBUG_TRANSLATION:
        print(f"\n[DEBUG {section}] {message}")
```

### Step 3: Add Logs at Each Point
- Modify `_browse_file()` - Add Point 1 logs
- Modify `_translate()` - Add Point 2 logs
- Modify `TranslationWorker.run()` - Add Point 3 logs
- Modify `_on_translation_completed()` - Add Point 4 logs
- `_save_as_odt()` - Already has logs

### Step 4: Create Debug Output File
```python
# Optional: Save debug log to file
import datetime

class DebugLogger:
    def __init__(self, enabled=True):
        self.enabled = enabled
        if enabled:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = f".test_outputs/com8/debug_translation_{timestamp}.log"
            self.log_lines = []
    
    def log(self, section, message):
        if self.enabled:
            line = f"[{section}] {message}"
            print(line)
            self.log_lines.append(line)
    
    def save(self):
        if self.enabled and self.log_lines:
            with open(self.log_file, 'w') as f:
                f.write('\n'.join(self.log_lines))
```

---

## EXPECTED DEBUG OUTPUT

When user loads file and translates:

```
[DEBUG File Load] 
  HTML length: 7475
  CSS classes: 8
  Preview text length: 2891
  Preview contains CSS: False
  Preview contains HTML tags: False
  Preview first 200 chars: CAIT										13/11/12
Nome: Josué	
...

[DEBUG Translation Start]
  Text to translate is HTML: True
  HTML length: 7475
  Contains <style>: True
  CSS manager stored: True

[DEBUG TranslationWorker]
  Input is HTML format: True
  Input length: 7475
  Protecting whitespace in HTML...
  After protection: 7492 chars

[DEBUG Translation completed]
  Result length: 7823
  Result is HTML: True
  Result first 300 chars: <!DOCTYPE html>...

[DEBUG Translation result received]
  Is HTML format: True
  Result length: 7823
  Extracted plain text length: 3012
  Plain text contains CSS: False
  Plain text first 200 chars: CAIT  13/11/12Name: Joshua...

[DEBUG _save_as_odt called]
  _translated_html: True (length: 7823)
  _css_manager: True (type: CSSClassManager)
  → Using HTML system
  → ODT created successfully
```

---

## BENEFITS

1. **Verify no CSS visible**: Check preview/result text doesn't contain `.fmt`
2. **Track HTML preservation**: Verify HTML survives translation
3. **Confirm code path**: See which save system executes
4. **Diagnose issues**: If something breaks, we see exactly where
5. **Document success**: Logs prove the system works correctly

---

## TESTING CHECKLIST

After adding logs:
- [ ] Load ODT file → Check debug output
- [ ] Verify preview text has no CSS/tags
- [ ] Translate → Check debug output shows HTML format
- [ ] Verify result text has no CSS/tags
- [ ] Save → Check debug output shows "Using HTML system"
- [ ] Verify ODT has 8 styles

---

## STATUS: Ready to implement debug logging

Should I add comprehensive debug logging now?
