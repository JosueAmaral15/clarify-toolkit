# 💾 Save Results Feature (v2.4.0)

## Overview

The save results feature allows you to export all search or match results to a formatted text file. This functionality is available in both the search/replace panel and the insert panel.

## User Interface

### Save Button

A new **"💾 Save Results"** button has been added to the results section header in both panels:

- **Search/Replace Panel**: Located above the "Search Results" tree
- **Insert Panel**: Located above the "Match Results" tree

### When the Button Is Available

The button remains always visible, but only works when there are results to save. If you click without results, an informative message will appear.

## Export Format

Results are saved in plain text format (`.txt`) with the following structure:

```
================================================================================
CLARIFY - SEARCH RESULTS
================================================================================
Total files with matches: 3
Total matches: 15
================================================================================

📁 /home/user/project/src/main.py
   Matches: 8
--------------------------------------------------------------------------------
   Line 10, Col 5:
      def calculate_total():
   Line 15, Col 8:
      return sum(values)
   Line 20, Col 4:
      result = calculate_total()
   ...

📁 /home/user/project/src/utils.py
   Matches: 5
--------------------------------------------------------------------------------
   Line 5, Col 0:
      import os
   Line 6, Col 0:
      import sys
   ...

📁 /home/user/project/tests/test_main.py
   Matches: 2
--------------------------------------------------------------------------------
   Line 12, Col 4:
      assert result == expected
   Line 18, Col 4:
      assert calculate_total() > 0
```

### Format Elements

1. **Header**: Includes title and overall statistics
   - Application name (CLARIFY - SEARCH RESULTS)
   - Total files with matches
   - Total matches found

2. **File Section**: For each file with matches
   - Full file path with 📁 emoji
   - Number of matches in the file
   - Separator line

3. **Match Details**: For each match
   - Line number and column
   - Code/text snippet where the match was found
   - Preserved indentation from original code

## How to Use

### Step by Step

1. **Run a Search or Insert**
   - In Search/Replace panel: Configure your search and click "Search"
   - In Insert panel: Configure your insert and click "Insert"

2. **Review Results**
   - Results will appear in the results tree
   - Verify the matches are correct

3. **Click "💾 Save Results"**
   - The button is located in the results section header
   - If there are no results, a message will inform you

4. **Choose Save Location**
   - A save file dialog will appear
   - Navigate to the desired directory
   - Type a filename (`.txt` extension will be added automatically)
   - Click "Save"

5. **Confirmation**
   - A confirmation message will appear indicating results were saved
   - The file will be ready to open or share

### Usage Example

**Scenario**: You want to document all occurrences of a specific function in your project.

1. Open the Search/Replace panel
2. Configure:
   - **Search for**: `calculate_total`
   - **Scope**: `Entire File`
   - **Match Options**: Enable "Match Whole Word"
3. Click "Search"
4. Review results in the tree
5. Click "💾 Save Results"
6. Save as: `calculate_total_occurrences.txt`
7. Open the file to review or share with the team

## Use Cases

### 1. Code Documentation

Export all occurrences of a function or class to create documentation or cross-references.

### 2. Code Review

Save search results to review offline or share with other developers.

### 3. Code Auditing

Document specific patterns found in code for audits or quality analysis.

### 4. TODO Tracking

Find and export all TODO, FIXME or similar comments for sprint planning.

### 5. Dependency Analysis

Identify and document all imports or dependencies of specific modules.

### 6. Refactoring Reports

Before refactoring, export all occurrences of old code to track changes.

## Technical Characteristics

### Encoding

- Files are saved with **UTF-8** encoding
- Supports special characters and Unicode
- Preserves formatting and indentation of original code

### File Sizes

- No theoretical limit on number of matches
- Large files may take a few seconds to generate
- Plain text format keeps files relatively small

### Error Handling

- Checks for results before allowing save
- Handles file permission errors
- Informs user about write problems

### Compatibility

- Works on Windows, macOS, and Linux
- `.txt` files can be opened in any text editor
- Format is compatible with text analysis and diff tools

## Limitations

1. **Text Format Only**
   - Currently, only `.txt` export is supported
   - No export to JSON, CSV, or other formats

2. **No Export Filters**
   - All results are exported
   - Cannot filter which files or matches to include

3. **No Additional Metadata**
   - Does not include search date/time
   - Does not include search parameters used
   - Does not include file version information

## Version

Feature introduced in Clarify version **2.4.0**.

## Modified Files

- `src/app.py`:
  - `ResultsTree` class: `get_matches_data()` and `export_to_text()` methods
  - `SearchReplacePanel` class: `_save_results()` method
  - `InsertPanel` class: `_save_results()` method

## Tests

See `test_save_results_feature.py` for complete automated tests of the feature.

## Feedback

If you have suggestions for improvements to the export format or additional features, please contact the developers.
