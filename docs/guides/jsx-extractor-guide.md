# JSX Parameter Extractor - Complete Guide

## 📖 Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Extraction Modes](#extraction-modes)
5. [Filter Options](#filter-options)
6. [Normalization](#normalization)
7. [Output Format](#output-format)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **JSX Parameter Extractor** is a powerful tool for extracting parameters and attributes from React/JSX/TSX files. It intelligently parses component hierarchies and generates structured JSON output representing your component tree.

### Key Features

- ✅ **Dual parsing modes**: Attribute extraction (key="value") or tag-content extraction
- ✅ **Smart filtering**: only_strings, avoid_keys, no_standard HTML tags
- ✅ **Case conversion**: snake_case, camelCase, PascalCase, kebab-case
- ✅ **Hierarchical output**: JSON structure mirrors component tree
- ✅ **File/directory support**: Process single files or entire directories
- ✅ **Generic mode**: Custom regex delimiters for non-JSX formats
- ✅ **Security**: Path traversal prevention, file extension validation

---

## Getting Started

### Accessing the Tool

1. Open Clarify application
2. Navigate to **Tools → Text To JSON Converter**
3. Select **"JSX Parameter Extractor"** from the dialog (default option)
4. Click OK

### Quick Start Example

```tsx
// Input file: Button.tsx
export default function Button({ label, onClick }) {
  return <button onClick={onClick}>{label}</button>;
}
```

**Settings:**
- Path: `Button.tsx`
- Parameter: `label`
- Is Attribute Mode: ✅ (checked)

**Output:**
```json
{
  "Button": {
    "button": {
      "label": {
        "label": "label"
      }
    }
  }
}
```

---

## User Interface

### Path Selection

#### Path Input
- **Field**: Text field displaying file or directory path
- **Browse Button**: Opens file/directory picker dialog
- **"Is file?" Checkbox**: 
  - ✅ Checked: Select single file
  - ☐ Unchecked: Select directory (recursive processing)

### Parameter & Mode

#### Parameter Name
- **Field**: `ed_param`
- **Description**: Name of the attribute/parameter to extract
- **Special value**: `*` or empty = match all parameters

#### Mode Selector
- **JSX Mode** (default): Parse JSX/TSX syntax (`<Tag attr="value">`)
- **Generic Mode**: Use custom regex delimiters (advanced)

#### "Treat as ATTRIBUTE?" Checkbox
- ✅ **Attribute Mode**: Extract `key="value"` pairs from tags
  - Example: `<Button label="Click Me" />` → extracts `label="Click Me"`
- ☐ **Tag-Content Mode**: Extract inner text of tags
  - Example: `<Button>Click Me</Button>` → extracts `"Click Me"`

### Generic Delimiters (Generic Mode Only)

- **Start Delimiter**: Regex pattern for scope start (e.g., `\{`)
- **End Delimiter**: Regex pattern for scope end (e.g., `\}`)
- **Use case**: Parse non-JSX formats (JSON, custom templates, etc.)

### Extensions Filter

- **Field**: Space-separated list of file extensions
- **Default**: `.tsx .jsx .js .ts`
- **Example**: `.tsx .jsx` (only TypeScript and JSX files)

### Options Group

#### Include Key
- ✅ Include parameter name in path
- Example: `Button.label.click_me` vs `Button.click_me`

#### Include Value
- ✅ Include original value in JSON output
- ☐ Empty dict `{}` as leaf value

#### Drop Standard HTML Tags
- ✅ Remove standard HTML tags from path (div, span, p, h1-h6, etc.)
- Keeps only custom component names (Button, Card, AuthGuard, etc.)
- **80+ standard tags filtered**: html, head, body, section, nav, article, etc.

#### Only Strings
- ✅ Filter out expressions, variables, function calls
- **Valid**: `"Click Me"`, `'Submit'`, `"Today's Practice"`
- **Invalid**: `{handleClick}`, `{user.name}`, `{count + 1}`
- Uses regex validation: no `{}`, `+`, `*`, `/`, property access, etc.

#### Include Quotation Marks in JSON
- ✅ Proper JSON format: `{"key": "value"}`
- ☐ JS literal format: `{key: "value"}` (TypeScript-friendly)

### Normalization Group

#### Case Style
- **snake_case**: `click_me`, `page_title`
- **camelCase**: `clickMe`, `pageTitle`
- **PascalCase**: `ClickMe`, `PageTitle`
- **kebab-case**: `click-me`, `page-title`

#### Uppercase
- ✅ Transform all keys to UPPERCASE: `CLICK_ME`, `PAGE_TITLE`

#### Limit
- **Field**: Character limit for normalized keys
- **Special value**: `all` = no limit
- **Example**: `10` = truncate to 10 characters

#### Avoid Cut
- ✅ Word boundary awareness: cut at last whitespace before limit
- ☐ Hard cut at exact limit

### JSON Options

#### Indentation
- **Field**: Number of spaces for JSON indentation
- **Range**: -1 to 16
- **-1**: Compact (single line)
- **2-4**: Typical (readable)

### Avoid Keys

#### Avoid Keys Input
- **Field**: Comma-separated list of keys to exclude
- **Example**: `className, data-testid, style`

#### Avoid Mode
- **Contains**: Exclude if key contains any avoid-key substring
- **Equals**: Exclude only if key exactly matches avoid-key

### Output Tabs

#### Paths Tab
- **Format**: Dot-notation paths
- **Example**:
  ```
  # File: Button.tsx
  Button.label.click_me
  Button.label.submit
  ```

#### JSON Tab
- **Format**: Hierarchical JSON or JS literal
- **Example**:
  ```json
  {
    "Button": {
      "label": {
        "click_me": "Click Me",
        "submit": "Submit"
      }
    }
  }
  ```

### Action Buttons

- **Extract**: Run extraction with current settings
- **Save Outputs**: Save paths.txt and result.json
- **Copy All**: Copy current tab content to clipboard
- **Clear**: Clear both output tabs

---

## Extraction Modes

### Attribute Mode (Default)

Extracts `key="value"` pairs from JSX attributes.

**Example:**
```tsx
<Button label="Click Me" variant="primary" onClick={handleClick} />
```

**Settings:**
- Parameter: `label`
- Is Attribute Mode: ✅

**Output:**
```json
{
  "Button": {
    "label": {
      "click_me": "Click Me"
    }
  }
}
```

**With `only_strings=false`:**
```json
{
  "Button": {
    "label": {
      "click_me": "Click Me"
    },
    "onClick": {
      "handle_click": "{handleClick}"
    }
  }
}
```

### Tag-Content Mode

Extracts inner text from tags.

**Example:**
```tsx
<h1>Page Title</h1>
<Button>Click Me</Button>
<Card>
  <p>Welcome to our app</p>
</Card>
```

**Settings:**
- Parameter: (any, not used in tag-content mode)
- Is Attribute Mode: ☐

**Output:**
```json
{
  "h1": "Page Title",
  "Button": "Click Me",
  "Card": {
    "p": "Welcome to our app"
  }
}
```

### Generic Mode

Use custom regex delimiters for non-JSX formats.

**Example (JSON-like):**
```
config {
  name: "MyApp"
  version: "1.0"
}
```

**Settings:**
- Mode: `generic`
- Start Delimiter: `\{`
- End Delimiter: `\}`
- Parameter: `name`

**Output:**
```json
{
  "config": {
    "name": {
      "my_app": "MyApp"
    }
  }
}
```

---

## Filter Options

### only_strings Filter

**Purpose**: Exclude expressions, variables, and function calls.

**Valid strings:**
- `"Hello World"` - double quotes
- `'Hello World'` - single quotes
- `"Today's Practice"` - quotes with apostrophe

**Invalid (filtered out):**
- `{variable}` - variable reference
- `{user.name}` - property access
- `{count + 1}` - expression
- `{handleClick}` - function reference
- `{"dynamic" + name}` - concatenation
- `{condition ? 'yes' : 'no'}` - conditional

**Regex patterns checked:**
- Braces `{}`
- Operators `+`, `*`, `/`, `=`, `|`, `&`, `[`, `]`
- Property access `obj.prop`
- Function calls `func(`
- Conditionals `? (`

### avoid_keys Filter

**Purpose**: Exclude specific keys from output.

**Mode: Contains**
```
Avoid Keys: className, data-testid
```
- Excludes: `className`, `data-testid-button`, `my-className`, etc.
- Checks: `x in key_matched` or `x in tag` or `x in value`

**Mode: Equals**
```
Avoid Keys: className, data-testid
```
- Excludes: only exact matches `className`, `data-testid`
- Checks: `x == key_matched` or `x == tag` or `x == value`

**Example:**
```tsx
<Button 
  label="Click" 
  className="btn-primary" 
  data-testid="submit-btn"
/>
```

With `avoid_keys="className, data-testid"` (contains):
- ✅ Extracts: `label="Click"`
- ❌ Filters: `className`, `data-testid`

### no_standard Filter

**Purpose**: Remove standard HTML tags from paths.

**Standard Tags (80+):**
- Structure: `html`, `head`, `body`, `div`, `span`, `section`, `article`, `aside`, `nav`, `main`, `header`, `footer`
- Text: `h1`-`h6`, `p`, `a`, `em`, `strong`, `small`, `code`, `pre`, `blockquote`
- Lists: `ul`, `ol`, `li`, `dl`, `dt`, `dd`
- Forms: `form`, `input`, `button`, `select`, `textarea`, `label`, `option`
- Media: `img`, `video`, `audio`, `canvas`, `svg`, `picture`, `source`
- Table: `table`, `tr`, `td`, `th`, `thead`, `tbody`, `tfoot`, `caption`
- And more...

**Example:**
```tsx
<div className="container">
  <AuthGuard>
    <div className="content">
      <StatsCard label="Stats" />
    </div>
  </AuthGuard>
</div>
```

**With `no_standard=false`:**
```
Component.div.AuthGuard.div.StatsCard.label
```

**With `no_standard=true`:**
```
Component.AuthGuard.StatsCard.label
```

---

## Normalization

### Case Styles

#### snake_case (Default)
- **Pattern**: `lowercase_with_underscores`
- **Example**: `"Click Me"` → `click_me`
- **Use case**: Python, databases, backend APIs

#### camelCase
- **Pattern**: `firstWordLowercaseRestCapitalized`
- **Example**: `"Click Me"` → `clickMe`
- **Use case**: JavaScript, TypeScript variables

#### PascalCase
- **Pattern**: `AllWordsCapitalized`
- **Example**: `"Click Me"` → `ClickMe`
- **Use case**: TypeScript types, React components

#### kebab-case
- **Pattern**: `lowercase-with-hyphens`
- **Example**: `"Click Me"` → `click-me`
- **Use case**: CSS classes, URLs, HTML attributes

### Smart Truncation

**Without avoid_cut:**
```
"Click Me Button" (limit=10) → "Click Me B"
```

**With avoid_cut:**
```
"Click Me Button" (limit=10) → "Click Me"  (cut at last whitespace)
```

**Algorithm:**
1. Truncate to limit characters
2. If avoid_cut=true, find last whitespace before limit
3. Cut at whitespace boundary
4. Strip trailing whitespace

### Uppercase Option

Applies AFTER case style normalization:
```
snake_case + uppercase: "Click Me" → "CLICK_ME"
camelCase + uppercase: "Click Me" → "CLICKME"
```

---

## Output Format

### Paths Tab

Dot-notation paths showing hierarchy:

```
# File: DashboardPage.tsx
DashboardPage.AuthGuard.StatsCard.label
DashboardPage.AuthGuard.Dashboard.label
DashboardPage.Button.label

# File: LoginPage.tsx
LoginPage.Card.Button.label
```

**Format:** `<FileRoot>.<Tag1>.<Tag2>...<Parameter>.<NormalizedValue>`

### JSON Tab

Hierarchical structure:

**JSON Format (with_quotation_marks=true):**
```json
{
  "DashboardPage": {
    "AuthGuard": {
      "StatsCard": {
        "label": {
          "statistics": "Statistics"
        }
      },
      "Dashboard": {
        "label": {
          "main_dashboard": "Main Dashboard"
        }
      }
    },
    "Button": {
      "label": {
        "click_me": "Click Me"
      }
    }
  }
}
```

**JS Literal Format (with_quotation_marks=false):**
```javascript
{
  DashboardPage: {
    AuthGuard: {
      StatsCard: {
        label: {
          statistics: "Statistics"
        }
      }
    }
  }
}
```

---

## Usage Examples

### Example 1: Extract All Labels from React App

**Goal:** Extract all `label` attributes from a React project.

**File structure:**
```
src/
  components/
    Button.tsx
    Card.tsx
    Dashboard.tsx
```

**Settings:**
- Path: `src/components/` (directory)
- Is file?: ☐ (unchecked - directory mode)
- Parameter: `label`
- Is Attribute Mode: ✅
- Extensions: `.tsx .jsx`
- only_strings: ✅
- no_standard: ✅
- Case style: `snake_case`

**Result:** All label values extracted, standard HTML tags removed, only literal strings included.

### Example 2: Extract Button Text (Tag Content)

**Goal:** Extract all button text for translation.

**Input:**
```tsx
<Button>Submit</Button>
<Button>Cancel</Button>
<Link>Go Back</Link>
```

**Settings:**
- Parameter: (not used)
- Is Attribute Mode: ☐ (tag-content mode)
- only_strings: ✅

**Output:**
```json
{
  "Button": {
    "submit": "Submit",
    "cancel": "Cancel"
  },
  "Link": {
    "go_back": "Go Back"
  }
}
```

### Example 3: PascalCase for TypeScript Types

**Goal:** Generate TypeScript translation keys.

**Settings:**
- Case style: `PascalCase`
- Include quotation marks: ☐ (JS literal)

**Output:**
```typescript
{
  Button: {
    label: {
      ClickMe: "Click Me",
      Submit: "Submit"
    }
  }
}
```

**Usage in code:**
```typescript
type TranslationKeys = {
  Button: {
    label: {
      ClickMe: string;
      Submit: string;
    };
  };
};
```

### Example 4: Exclude Test IDs and Class Names

**Goal:** Extract only semantic attributes, ignore styling.

**Settings:**
- avoid_keys: `className, data-testid, style, id`
- Avoid mode: `contains`

**Input:**
```tsx
<Button 
  label="Submit" 
  className="btn-primary" 
  data-testid="submit-button"
  aria-label="Submit form"
/>
```

**Output:**
```json
{
  "Button": {
    "label": {
      "submit": "Submit"
    },
    "aria-label": {
      "submit_form": "Submit form"
    }
  }
}
```

### Example 5: Custom Component Hierarchy

**Goal:** Preserve component tree structure without standard HTML.

**Input:**
```tsx
<AuthGuard>
  <div>
    <Dashboard label="Main">
      <StatsCard label="Users" />
      <StatsCard label="Revenue" />
    </Dashboard>
  </div>
</AuthGuard>
```

**Settings:**
- no_standard: ✅ (remove div)
- include_key: ✅
- include_value: ✅

**Output:**
```json
{
  "AuthGuard": {
    "Dashboard": {
      "label": {
        "main": "Main"
      },
      "StatsCard": {
        "label": {
          "users": "Users",
          "revenue": "Revenue"
        }
      }
    }
  }
}
```

---

## Best Practices

### 1. Start with Defaults
- Use default settings first
- Adjust filters based on output
- Iterative refinement

### 2. Use `only_strings` for Translation
- Essential when extracting for i18n
- Prevents extracting `{variable}` references
- Ensures only translatable text

### 3. `no_standard` for React Components
- Remove noise from standard HTML
- Focus on custom components
- Cleaner hierarchical structure

### 4. Choose Case Style by Use Case
- **snake_case**: Backend, databases, Python
- **camelCase**: Frontend, JavaScript/TypeScript
- **PascalCase**: TypeScript types, constants
- **kebab-case**: CSS, HTML attributes

### 5. Smart Truncation for Long Values
- Use `limit` to prevent overly long keys
- Enable `avoid_cut` for cleaner truncation
- Test with sample data first

### 6. Directory Processing
- Uncheck "Is file?" for batch processing
- Use extensions filter to target specific files
- Monitor output for unexpected results

### 7. Generic Mode for Custom Formats
- Requires regex knowledge
- Test delimiters on small samples first
- Use named capture groups: `(?P<name>...)`

---

## Troubleshooting

### Problem: No Output Generated

**Possible causes:**
1. Parameter name doesn't match any attributes
2. File has no JSX syntax
3. Filters too strict (only_strings, avoid_keys)

**Solutions:**
- Use `*` (wildcard) for parameter to match all
- Verify file contains JSX/TSX syntax
- Temporarily disable filters to see full output

### Problem: Too Many Results

**Solutions:**
- Use more specific parameter name
- Enable `only_strings` to filter expressions
- Add avoid_keys: `className, style, id`
- Enable `no_standard` to remove HTML tags

### Problem: Values Not Matching Expected Format

**Causes:**
- Wrong parsing mode (attribute vs tag-content)
- File encoding issues
- Nested expressions

**Solutions:**
- Toggle "Treat as ATTRIBUTE?" checkbox
- Ensure file is UTF-8 encoded
- Enable `only_strings` to filter complex expressions

### Problem: Path Traversal Error

**Message:** "Security Error: Path is outside allowed directories"

**Cause:** Trying to access files outside home/workspace

**Solution:** Only select files within home directory or current workspace

### Problem: JSON Parse Error (JS Literal)

**Cause:** Trying to parse JS literal format with JSON parser

**Solution:** Enable "Include quotation marks in JSON" for proper JSON

### Problem: Keys Too Long

**Solution:**
- Set `limit` to reasonable value (e.g., 20-30)
- Enable `avoid_cut` for cleaner truncation

### Problem: Duplicate Keys in Output

**Cause:** Multiple files/components with same value

**Expected behavior:** `deep_merge()` combines them

**Solution:** Use `include_key` to add hierarchy level

---

## Advanced Tips

### Extracting from Multiple Projects

```bash
# Process multiple directories
for dir in project1 project2 project3; do
  # Set Path to $dir/src/components
  # Run extraction
  # Save output to $dir-translations.json
done
```

### Integration with Translation Workflow

1. Extract parameters with JSX Extractor
2. Save JSON output
3. Import into translation management system
4. Use JSON Translator tool to apply translations back

### Custom Post-Processing

Output JSON can be processed with:
- `jq` (command-line JSON processor)
- Python scripts
- Node.js tools

**Example: Flatten nested JSON with jq**
```bash
jq -r 'paths(scalars) as $p | "\($p | join(".")): \(getpath($p))"' result.json
```

---

## Security Considerations

### Path Validation

All paths are validated with `_validate_path_security()`:
- Resolves symlinks with `os.path.realpath()`
- Checks if path starts with home directory or workspace
- Prevents `../../../etc/passwd` attacks (CWE-22)

### File Extension Validation

Save operations validate extensions:
- **paths.txt**: Must end with `.txt`
- **result.json**: Must end with `.json`
- Shows security warning for invalid extensions

### No Code Execution

Parser does NOT execute code:
- No `eval()` or `exec()`
- No `subprocess` calls
- Safe regex-based parsing only

---

## Performance Considerations

### Large Directories

- Processing 100+ files may take 10-30 seconds
- Status updates shown during extraction
- Consider filtering by extensions

### Large Files

- Files >10MB may be slow to parse
- JSX parser is regex-based (not AST)
- Generic mode may be faster for simple patterns

### Memory Usage

- Full file content loaded into memory
- JSON output stored in memory
- For very large projects, process in batches

---

## Related Tools

- **Text Format Converter**: Simple text → JSON conversion (no file parsing)
- **JSON Rewriter**: Deduplicate and clean JSON output
- **JSON Translator**: Apply translations back to code

---

## Support & Feedback

For issues, feature requests, or questions:
- GitHub Issues: [clarify/issues](https://github.com/JosueAmaral15/clarify/issues)
- Documentation: `docs/` folder
- Email: josueamaral15@gmail.com

---

**Last Updated:** December 2, 2025  
**Version:** 2.9.0
