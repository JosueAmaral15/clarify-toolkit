# ACTION PLAN: Dynamic Output Format Based on Template Selection
**Programmer #3** | Date: 2026-02-08

## Problem Statement
Currently:
- Template selection changes output tab name (JSON → HTML Table → CSV, etc.)
- BUT: Output format always stays as JSON
- User expects: Output format should match selected template

Example:
- Select "HTML Table" → Output should be actual HTML table
- Select "CSV" → Output should be CSV format
- Select "TOML" → Output should be TOML format

## Analysis Required

### 1. Understand Current Architecture
- [ ] Read extraction worker code (`ExtractionWorker`)
- [ ] Read advanced extractor code (`AdvancedExtractor`)
- [ ] Understand how JSON output is generated
- [ ] Check if output format is configurable

### 2. Identify Template-to-Format Mapping
Need to determine:
- Which templates represent OUTPUT formats vs INPUT examples
- Format conversion logic needed:
  * JSON → HTML Table
  * JSON → CSV
  * JSON → YAML
  * JSON → TOML
  * JSON → INI
  * etc.

### 3. Check Existing Conversion Functions
- [ ] Check if `src/text_to_json.py` has reverse converters
- [ ] Look for JSON-to-other-format utilities
- [ ] Identify what needs to be created

## Implementation Plan

### Phase 1: Investigation (Protocol Step B - Read & Understand)
1. Read `src/extractors/advanced_extractor.py` 100%
2. Read `src/gui/extraction_worker.py` 100%
3. Read `src/text_to_json.py` 100%
4. Understand data flow: Input → Extractor → Output
5. Document findings

### Phase 2: Design
1. Map templates to output formats:
   - JSON → JSON (default, no conversion)
   - HTML Table → HTML table structure
   - CSV → CSV rows
   - YAML → YAML format
   - TOML → TOML format
   - etc.

2. Design format converter interface:
   ```python
   def convert_json_to_format(json_data, format_name):
       # Returns formatted string
   ```

3. Identify where to inject format conversion:
   - In `_on_extraction_finished()`?
   - In `ExtractionWorker`?
   - New converter module?

### Phase 3: Implementation
1. Create format converter functions
2. Integrate with template selection
3. Update output display logic
4. Handle errors (invalid formats, conversion failures)

### Phase 4: Testing (Protocol Required)
1. Test each template format:
   - JSON (baseline)
   - HTML Table
   - CSV
   - YAML
   - TOML
   - INI
   - etc.
2. Test with real extraction data
3. Test error cases
4. Document results

### Phase 5: Documentation & Commit
1. Document implementation
2. Update user-facing documentation if needed
3. Commit with detailed message

## Questions to Answer Before Starting

1. **Scope**: Which templates should have output format conversion?
   - Option A: All templates?
   - Option B: Only data formats (CSV, YAML, TOML, INI)?
   - Option C: Exclude JSX/HTML templates (they are input examples)?
   
   answer:

2. **Format Priority**: If extraction has nested data, how to flatten for CSV/Table?
   - Option A: Flatten recursively (dot notation: "user.name")
   - Option B: Only top-level keys (ignore nested)
   - Option C: Multiple rows per nested item
   
   answer:

3. **Error Handling**: What if JSON structure can't convert to requested format?
   - Option A: Show error message, keep JSON output
   - Option B: Show error, clear output
   - Option C: Attempt best-effort conversion, show warning
   
   answer:

4. **Template Selection Persistence**: Should format selection persist across extractions?
   - Option A: Yes - remember last selected template
   - Option B: No - reset to JSON after each extraction
   
   answer:

5. **Default Behavior**: What's default format when no template selected?
   - Option A: JSON (current behavior)
   - Option B: Last used format
   - Option C: Ask user
   
   answer:

## Estimated Complexity
- **Investigation**: 30-45 minutes
- **Design**: 15-20 minutes  
- **Implementation**: 45-60 minutes
- **Testing**: 30-45 minutes
- **Total**: 2-3 hours

## Protocol Compliance Checklist
- [ ] Read all relevant code before implementation
- [ ] Ask clarifying questions before coding
- [ ] Test each feature thoroughly
- [ ] Document findings and decisions
- [ ] Commit with detailed messages
- [ ] Be honest about what's tested vs untested

## Next Steps
1. Get user confirmation on questions above
2. Begin Phase 1: Investigation
3. Read SIMPLICITY_PROTOCOL_3.md if needed
4. Document findings in reading notes

---
**Status**: PLANNING - Awaiting user answers to questions 1-5
