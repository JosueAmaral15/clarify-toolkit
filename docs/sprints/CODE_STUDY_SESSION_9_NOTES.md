# Code Study Session 9 Notes
**Programmer #7 - Source Code Study**  
**Date**: 2026-01-22  
**Session Focus**: Phase 3 - AI Processor Module (src/ai_processor/)  
**Files Studied**: 5 files (~1,061 lines)

---

## 📋 Session Overview

**Progress**:
- **Files Studied This Session**: 5 files
- **Lines of Code**: ~1,061 lines
- **Total Progress**: 46/196 files (23.5%)
- **Phase**: Phase 3 - Feature Modules (AI Processor Module COMPLETE ✅)

**Files Analyzed**:
1. `src/ai_processor/__init__.py` (31 lines) ✅
2. `src/ai_processor/token_counter.py` (91 lines) ✅
3. `src/ai_processor/api_client.py` (342 lines) ✅
4. `src/ai_processor/processor.py` (324 lines) ✅
5. `src/ai_processor/template_engine.py` (273 lines) ✅

**AI Processor Module Status**: ✅ **100% COMPLETE** (5/5 files, ~1,061 lines)

---

## 🔍 Detailed Analysis

### Module Overview

**Purpose**: AI-powered batch file processing with multiple LLM providers

**Key Capabilities**:
- ✅ Multi-provider support (OpenAI GPT-4/5, Google Gemini, Anthropic Claude, Perplexity)
- ✅ Token counting and cost estimation
- ✅ Template engine with arithmetic expressions
- ✅ Batch file processing with progress tracking
- ✅ Code fence stripping (markdown cleanup)
- ✅ Marker-based content extraction
- ✅ API key validation
- ✅ Graceful fallback (simulated responses if no API key)

---

### 1. __init__.py (31 lines) - Module Exports

**Purpose**: Central import point for AI processor module

**Exports** (20+ functions/classes):
- **Token Counting**: count_tokens, estimate_cost, is_tiktoken_available
- **API Clients**: OpenAIClient, GeminiClient, ClaudeClient, PerplexityClient
- **Model Discovery**: list_openai_models, list_gemini_models, etc.
- **Utilities**: has_internet, is_openai_available, etc.
- **Processing**: process_file, process_multiple_files, save_results
- **File Operations**: read_file_safe, list_files_recursive
- **Text Processing**: strip_code_fences, extract_between_markers
- **Templates**: TemplateEngine, render_prompt, create_context

**Architecture**: Clean separation between clients, processing, and utilities

---

### 2. token_counter.py (91 lines) - Token Counting & Cost Estimation

**Purpose**: Count tokens and estimate API costs

#### **Dependencies**:
```python
try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False
```

**Graceful Degradation**: Falls back to heuristic (1 token ≈ 4 chars) if tiktoken not installed

---

#### **count_tokens() Function** (Lines 16-47)

**Purpose**: Count tokens for specific model

```python
def count_tokens(text: str, model: str = 'gpt-4o') -> int:
    if not text:
        return 0
    
    if not _TIKTOKEN_AVAILABLE:
        # Fallback: rough estimate (1 token ≈ 4 chars)
        return len(text) // 4
    
    try:
        # Map model names to tiktoken encodings
        if "gpt-4" in model.lower() or "gpt-5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif "gpt-3.5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            # Default: cl100k_base (GPT-4, GPT-3.5-turbo, text-embedding-ada-002)
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    except Exception:
        # Fallback if encoding fails
        return len(text) // 4
```

**Key Feature**: Triple fallback strategy (tiktoken → model-specific → heuristic)

**Supported Encodings**:
- `gpt-4`, `gpt-5` → `tiktoken.encoding_for_model("gpt-4")`
- `gpt-3.5` → `tiktoken.encoding_for_model("gpt-3.5-turbo")`
- Default → `cl100k_base` encoding

**Example**:
```python
text = "Hello, world! This is a test."
tokens = count_tokens(text, "gpt-4o")
# tokens ≈ 8 (with tiktoken) or 7 (heuristic: 29 chars / 4)
```

---

#### **estimate_cost() Function** (Lines 50-86)

**Purpose**: Estimate API cost in USD based on token counts

**Pricing Table** (as of 2025):

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4o | $5.00 | $15.00 |
| gpt-5 (estimated) | $15.00 | $120.00 |
| gemini-2.5-flash | $0.10 | $0.40 |
| gemini-2.5-pro | $0.50 | $1.50 |

**Algorithm**:
```python
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    model_lower = model.lower()
    
    # GPT pricing
    if "gpt-4o-mini" in model_lower:
        return (input_tokens * 0.00015 + output_tokens * 0.00060) / 1000.0
    elif "gpt-4o" in model_lower:
        return (input_tokens * 0.00500 + output_tokens * 0.01500) / 1000.0
    elif "gpt-5" in model_lower:
        return (input_tokens * 0.01500 + output_tokens * 0.12000) / 1000.0
    
    # Gemini pricing (estimated)
    elif "gemini-2.5-flash" in model_lower or "gemini-flash" in model_lower:
        return (input_tokens * 0.00010 + output_tokens * 0.00040) / 1000.0
    elif "gemini-2.5-pro" in model_lower or "gemini-pro" in model_lower:
        return (input_tokens * 0.00050 + output_tokens * 0.00150) / 1000.0
    
    # Default fallback (gemini-pro pricing)
    return (input_tokens * 0.00050 + output_tokens * 0.00150) / 1000.0
```

**Example**:
```python
# Process 1000 files with GPT-4o-mini
input_tokens = 1000 * 500   # 500 tokens per file
output_tokens = 1000 * 200  # 200 tokens per response
cost = estimate_cost(input_tokens, output_tokens, "gpt-4o-mini")
# cost ≈ $0.195 ($0.075 input + $0.120 output)
```

**Note**: Prices in cents per 1000 tokens (divided by 1000.0 at end)

---

#### **is_tiktoken_available() Function** (Lines 89-91)

```python
def is_tiktoken_available() -> bool:
    return _TIKTOKEN_AVAILABLE
```

**Use Case**: Check if precise token counting is available (UI feedback)

---

### 3. api_client.py (342 lines) - Multi-Provider API Clients

**Purpose**: Unified interface for 4 LLM providers

#### **Provider Availability Checks** (Lines 10-26)

```python
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

try:
    import anthropic
    _CLAUDE_AVAILABLE = True
except ImportError:
    _CLAUDE_AVAILABLE = False
```

**Pattern**: Try-except imports for optional dependencies

---

#### **AVAILABLE_MODELS Constant** (Lines 29-49)

**Recommended Models by Provider**:

```python
AVAILABLE_MODELS = {
    'openai': [
        {'name': 'gpt-4o-mini', 'label': 'GPT-4o Mini (Recommended)'},
        {'name': 'gpt-4o', 'label': 'GPT-4o'},
    ],
    'gemini': [
        {'name': 'gemini-2.5-flash', 'label': 'Gemini 2.5 Flash (Recommended)'},
        {'name': 'gemini-2.5-pro', 'label': 'Gemini 2.5 Pro'},
    ],
    'claude': [
        {'name': 'claude-sonnet-4-20250514', 'label': 'Claude Sonnet 4 (Recommended)'},
        {'name': 'claude-3-5-sonnet-20241022', 'label': 'Claude 3.5 Sonnet'},
        {'name': 'claude-3-5-haiku-20241022', 'label': 'Claude 3.5 Haiku'},
    ],
    'perplexity': [
        {'name': 'llama-3.1-sonar-small-128k-online', 'label': 'Sonar Small (Online)'},
        {'name': 'llama-3.1-sonar-large-128k-online', 'label': 'Sonar Large (Online)'},
        {'name': 'llama-3.1-sonar-huge-128k-online', 'label': 'Sonar Huge (Online)'},
    ]
}
```

**Key Feature**: Static model list (for UI dropdowns)

---

#### **Utility Functions** (Lines 52-141)

**has_internet()** (Lines 52-58):
```python
def has_internet() -> bool:
    """Check if internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
```

**How It Works**: Try to connect to Google DNS (8.8.8.8 port 53) with 3-second timeout

**is_openai_available()**, **is_gemini_available()**, **is_claude_available()**:
- Simple checks if respective SDK is installed

**list_openai_models()** (Lines 76-97):
```python
def list_openai_models(api_key: str) -> list:
    if not _OPENAI_AVAILABLE or not api_key:
        return []
    
    try:
        client = OpenAI(api_key=api_key)
        models = client.models.list()
        
        # Filter for chat models only (gpt-*)
        chat_models = []
        for model in models.data:
            model_id = model.id
            if model_id.startswith('gpt-'):
                chat_models.append({
                    'name': model_id,
                    'label': model_id.upper()
                })
        
        return sorted(chat_models, key=lambda x: x['name'])
    except Exception:
        return []
```

**Key Feature**: Filters for chat models only (excludes embeddings, etc.)

**list_gemini_models()** (Lines 100-123):
- Similar pattern, filters for models with `generateContent` capability

**list_claude_models()**, **list_perplexity_models()**:
- Return static lists (APIs don't provide model listing endpoints)

---

#### **OpenAIClient Class** (Lines 144-186)

**Constructor**:
```python
def __init__(self, api_key: Optional[str], model: str = 'gpt-4o-mini'):
    self.api_key = api_key
    self.model = model
    self.available = bool(api_key) and _OPENAI_AVAILABLE
    self.client = OpenAI(api_key=api_key) if self.available else None
```

**verify_key() Method** (Lines 153-168):
```python
def verify_key(self) -> Tuple[bool, str]:
    """Verify API key is valid."""
    if not _OPENAI_AVAILABLE:
        return False, "OpenAI SDK not installed (pip install openai)"
    if not self.api_key:
        return False, "No API key provided"
    if not has_internet():
        return False, "No internet connection"
    
    try:
        models = self.client.models.list()
        if not models or not getattr(models, "data", None):
            return False, "Could not list models"
        return True, "✅ Valid key, internet OK, OpenAI access confirmed"
    except Exception as e:
        return False, f"❌ Key validation error: {str(e)}"
```

**Key Feature**: 4-level validation (SDK → key → internet → API access)

**chat() Method** (Lines 170-186):
```python
def chat(self, system_prompt: str, user_prompt: str) -> str:
    if not self.available:
        return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"
    
    try:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,  # Low temperature for consistency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"<<API ERROR: {str(e)}>>"
```

**Temperature**: 0.2 (low = more consistent/deterministic)

**Graceful Degradation**: Returns simulated response if no key (for testing UI)

---

#### **GeminiClient Class** (Lines 189-240)

**Constructor**:
```python
def __init__(self, api_key: Optional[str], model: str = 'gemini-2.5-flash'):
    self.api_key = api_key
    self.model = model
    self.available = bool(api_key) and _GEMINI_AVAILABLE
    
    if self.available:
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.model)
        except Exception:
            self.available = False
            self._model = None
    else:
        self._model = None
```

**Key Difference**: Must configure SDK globally + create model instance

**chat() Method** (Lines 229-240):
```python
def chat(self, system_prompt: str, user_prompt: str) -> str:
    if not self.available or not self._model:
        return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"
    
    try:
        # Gemini doesn't have roles the same way; fold system+user into single prompt
        prompt = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}"
        response = self._model.generate_content(prompt)
        return getattr(response, "text", "") or ""
    except Exception as e:
        return f"<<API ERROR: {str(e)}>>"
```

**Key Difference**: Gemini doesn't separate system/user roles, so prompts are concatenated

---

#### **ClaudeClient Class** (Lines 243-290)

**Similar Pattern**: Initialize client, verify key, chat with system+user messages

**Key Feature**: Uses Anthropic's `anthropic.Anthropic` client

---

#### **PerplexityClient Class** (Lines 292-342)

**Key Detail**: Perplexity uses OpenAI-compatible API

```python
def __init__(self, api_key: Optional[str], model: str = 'llama-3.1-sonar-small-128k-online'):
    self.api_key = api_key
    self.model = model
    self.available = bool(api_key) and _OPENAI_AVAILABLE
    
    # Perplexity uses OpenAI-compatible API endpoint
    self.client = OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai"  # Custom base URL!
    ) if self.available else None
```

**Clever Trick**: Reuse OpenAI SDK with custom base_url

---

### 4. processor.py (324 lines) - File Processing Logic

**Purpose**: Core batch processing operations

#### **extract_between_markers() Function** (Lines 14-86)

**Purpose**: Extract content between start/end markers (with regex support)

**Parameters**:
- `start_marker`, `end_marker`: Markers to search for
- `start_regex`, `end_regex`: Treat markers as regex (default: False)
- `start_case_sensitive`, `end_case_sensitive`: Case sensitivity flags
- `include_markers`: Include markers in extracted text (default: False)
- `match_all`: Extract all matches vs only first (default: True)

**Algorithm**:
```python
def extract_between_markers(text, start_marker, end_marker, ...) -> str:
    # 1. Build start pattern
    if start_regex:
        start_pat = start_marker
    else:
        start_pat = re.escape(start_marker)  # Escape for literal match
    
    # 2. Build end pattern (same logic)
    if end_regex:
        end_pat = end_marker
    else:
        end_pat = re.escape(end_marker)
    
    # 3. Compile with independent case flags
    flags_start = 0 if start_case_sensitive else re.IGNORECASE
    flags_end = 0 if end_case_sensitive else re.IGNORECASE
    
    start_re = re.compile(start_pat, flags_start)
    end_re = re.compile(end_pat, flags_end)
    
    # 4. Find non-overlapping segments
    out = []
    i = 0
    while i <= len(text):
        m_start = start_re.search(text, i)
        if not m_start:
            break
        m_end = end_re.search(text, m_start.end())
        if not m_end:
            break
        
        # Extract segment
        if include_markers:
            seg = text[m_start.start(): m_end.end()]
        else:
            seg = text[m_start.end(): m_end.start()]
        
        out.append(seg)
        i = m_end.end()
        
        if not match_all:
            break  # Only first match
    
    return "".join(out) if out else text  # Return original if no match
```

**Use Cases**:
- Extract code from markdown: `extract_between_markers(text, "```python", "```")`
- Extract JSON from logs: `extract_between_markers(text, "{", "}", start_regex=False)`
- Extract XML tags: `extract_between_markers(text, "<data>", "</data>")`

**Example**:
```python
text = "Before ```python\ncode here\n``` After"
result = extract_between_markers(text, "```python", "```", include_markers=False)
# result = "\ncode here\n"
```

---

#### **read_file_safe() Function** (Lines 89-110)

**Purpose**: Safely read file with encoding fallback

```python
def read_file_safe(file_path: str, max_bytes: Optional[int] = None) -> str:
    try:
        with open(file_path, 'rb') as f:
            data = f.read() if max_bytes is None else f.read(max_bytes)
        
        # Try UTF-8 first, fallback to latin-1
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('latin-1', errors='replace')
    except Exception as e:
        return f"<<ERROR reading {file_path}: {str(e)}>>"
```

**Key Feature**: Same pattern as utils/file_utils.py (UTF-8 → latin-1 fallback)

**max_bytes Parameter**: Useful for large files (preview first N bytes)

---

#### **list_files_recursive() Function** (Lines 113-130)

**Purpose**: List all files in directory recursively

```python
def list_files_recursive(directory: str, extensions: List[str]) -> List[str]:
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if not extensions or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files
```

**Extension Filter**: Empty list = all files

**Example**:
```python
# Find all Python files
files = list_files_recursive("src", ['.py'])

# Find all files (no filter)
files = list_files_recursive("docs", [])
```

---

#### **strip_code_fences() Function** (Lines 133-150)

**Purpose**: Remove markdown code fences from AI responses

**Algorithm**:
```python
def strip_code_fences(text: str) -> str:
    # Remove opening fence with optional language
    text = re.sub(r'^```[a-z]*\n', '', text, flags=re.MULTILINE)
    
    # Remove closing fence
    text = re.sub(r'\n```$', '', text, flags=re.MULTILINE)
    
    return text.strip()
```

**Use Case**: AI models often wrap code in markdown fences

**Example**:
```python
text = "```python\nprint('hello')\n```"
result = strip_code_fences(text)
# result = "print('hello')"
```

---

#### **process_file() Function** (Lines 153-200)

**Purpose**: Process single file with AI

**Parameters**:
- `file_path`: File to process
- `client`: AI client (OpenAIClient, GeminiClient, etc.)
- `system_prompt`: System instructions
- `user_prompt_template`: User prompt with {{variables}}
- `context`: Template variables (count, filename, total, etc.)

**Algorithm**:
```python
def process_file(file_path, client, system_prompt, user_prompt_template, context):
    # 1. Read file content
    content = read_file_safe(file_path)
    
    # 2. Render user prompt with template variables
    context['content'] = content
    context['filename'] = os.path.basename(file_path)
    context['filepath'] = file_path
    user_prompt = render_prompt(user_prompt_template, context)
    
    # 3. Send to AI
    response = client.chat(system_prompt, user_prompt)
    
    # 4. Strip code fences if present
    response = strip_code_fences(response)
    
    return response
```

**Template Variables**:
- `{{content}}`: File content
- `{{filename}}`: File name (basename)
- `{{filepath}}`: Full file path
- `{{count}}`: Current file index
- `{{total}}`: Total file count

---

#### **process_multiple_files() Function** (Lines 203-260)

**Purpose**: Batch process multiple files with progress callback

**Parameters**:
- `files`: List of file paths
- `client`: AI client
- `system_prompt`: System instructions
- `user_prompt_template`: User prompt template
- `progress_callback`: Optional callback(current, total, status)

**Algorithm**:
```python
def process_multiple_files(files, client, system_prompt, user_prompt_template, progress_callback):
    results = []
    total = len(files)
    
    for i, file_path in enumerate(files):
        # Update progress
        if progress_callback:
            progress_callback(i, total, f"Processing {os.path.basename(file_path)}")
        
        # Process file
        context = {'count': i, 'total': total}
        try:
            response = process_file(file_path, client, system_prompt, user_prompt_template, context)
            results.append({
                'file': file_path,
                'success': True,
                'response': response
            })
        except Exception as e:
            results.append({
                'file': file_path,
                'success': False,
                'error': str(e)
            })
    
    # Final progress update
    if progress_callback:
        progress_callback(total, total, "Complete")
    
    return results
```

**Key Feature**: Progress callback for UI updates

**Example**:
```python
def progress(current, total, status):
    print(f"[{current}/{total}] {status}")

results = process_multiple_files(
    files=["file1.txt", "file2.txt"],
    client=OpenAIClient(api_key="sk-..."),
    system_prompt="You are a helpful assistant.",
    user_prompt_template="Summarize this file: {{content}}",
    progress_callback=progress
)
```

---

#### **save_results() Function** (Lines 263-324)

**Purpose**: Save batch processing results to files

**Parameters**:
- `results`: List of result dictionaries
- `output_dir`: Output directory path
- `output_format`: 'individual' or 'combined'

**Output Formats**:
1. **'individual'**: One file per input file
   - `output_dir/input_filename.result.txt`

2. **'combined'**: Single file with all results
   - `output_dir/combined_results.txt`

**Algorithm**:
```python
def save_results(results, output_dir, output_format='individual'):
    os.makedirs(output_dir, exist_ok=True)
    
    if output_format == 'individual':
        # Save each result separately
        for result in results:
            if result['success']:
                input_filename = os.path.basename(result['file'])
                output_filename = f"{input_filename}.result.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['response'])
    
    elif output_format == 'combined':
        # Combine all results into single file
        output_path = os.path.join(output_dir, "combined_results.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"=== {result['file']} ===\n\n")
                if result['success']:
                    f.write(result['response'])
                else:
                    f.write(f"ERROR: {result['error']}")
                f.write("\n\n")
```

---

### 5. template_engine.py (273 lines) - Dynamic Prompt Templating

**Purpose**: Template engine with arithmetic expressions (NO eval()!)

#### **Supported Variables**:

- `{{count}}` - Current file index (0-based)
- `{{count+N}}` - Addition
- `{{count-N}}` - Subtraction
- `{{count*N}}` - Multiplication
- `{{count/N}}` - Integer division
- `{{filename}}` - Current file name (basename)
- `{{filepath}}` - Current file full path
- `{{total}}` - Total number of files

**Security Note**: NO eval() or arbitrary code execution!

---

#### **TemplateEngine Class** (Lines 33-200)

**Design Patterns**:
- **Strategy Pattern**: Different substitution strategies per variable type
- **Template Method Pattern**: `_substitute()` defines algorithm steps

**Constructor** (Lines 47-49):
```python
def __init__(self):
    pass  # Stateless
```

---

#### **render() Method** (Lines 51-73)

**Purpose**: Render template with variable substitution

```python
def render(self, template: str, context: Dict[str, Any]) -> str:
    def replace_variable(match):
        variable_expr = match.group(1).strip()
        return self._substitute(variable_expr, context)
    
    return self.VARIABLE_PATTERN.sub(replace_variable, template)
```

**Pattern**: `\{\{([^}]+)\}\}` (matches `{{anything}}`)

**Example**:
```python
engine = TemplateEngine()
context = {'count': 0, 'total': 5, 'filename': 'test.txt'}
result = engine.render("File {{count+1}}/{{total}}: {{filename}}", context)
# result = "File 1/5: test.txt"
```

---

#### **_substitute() Method** (Lines 75-91)

**Purpose**: Substitute single variable expression

```python
def _substitute(self, expression: str, context: Dict[str, Any]) -> str:
    # Check if expression contains arithmetic
    if any(op in expression for op in self.SAFE_OPERATORS):
        return self._evaluate_arithmetic(expression, context)
    else:
        # Simple variable lookup
        return self._lookup_variable(expression, context)
```

**SAFE_OPERATORS**: `['+', '-', '*', '/']` (whitelist only!)

---

#### **_lookup_variable() Method** (Lines 93-109)

**Purpose**: Look up simple variable

```python
def _lookup_variable(self, var_name: str, context: Dict[str, Any]) -> str:
    value = context.get(var_name)
    
    if value is None:
        return f"{{{{UNDEFINED:{var_name}}}}}"  # Preserve undefined
    
    return str(value)
```

**Key Feature**: Preserves undefined variables (for debugging)

---

#### **_evaluate_arithmetic() Method** (Lines 111-200)

**Purpose**: Evaluate arithmetic expression safely (NO eval()!)

**Algorithm**:
```python
def _evaluate_arithmetic(self, expression: str, context: Dict[str, Any]) -> str:
    # 1. Find operator
    operator = None
    for op in self.SAFE_OPERATORS:
        if op in expression:
            operator = op
            break
    
    if not operator:
        return f"{{{{INVALID_EXPR:{expression}}}}}"
    
    # 2. Split by operator
    parts = expression.split(operator, 1)
    if len(parts) != 2:
        return f"{{{{INVALID_EXPR:{expression}}}}}"
    
    left_str, right_str = parts[0].strip(), parts[1].strip()
    
    # 3. Resolve left side (variable)
    left_value = context.get(left_str)
    if left_value is None:
        return f"{{{{UNDEFINED:{left_str}}}}}"
    
    # 4. Parse right side (number or variable)
    try:
        if right_str.isdigit():
            right_value = int(right_str)
        else:
            right_value = context.get(right_str)
            if right_value is None:
                return f"{{{{UNDEFINED:{right_str}}}}}"
    except ValueError:
        return f"{{{{INVALID_EXPR:{expression}}}}}"
    
    # 5. Perform arithmetic
    try:
        left_int = int(left_value)
        right_int = int(right_value)
        
        if operator == '+':
            result = left_int + right_int
        elif operator == '-':
            result = left_int - right_int
        elif operator == '*':
            result = left_int * right_int
        elif operator == '/':
            result = left_int // right_int  # Integer division
        else:
            return f"{{{{INVALID_OPERATOR:{operator}}}}}"
        
        return str(result)
    except (ValueError, TypeError, ZeroDivisionError) as e:
        return f"{{{{EVAL_ERROR:{expression}:{str(e)}}}}}"
```

**Security Features**:
- ✅ Whitelist operators only (`+`, `-`, `*`, `/`)
- ✅ NO eval() or exec()
- ✅ Integer arithmetic only (no float)
- ✅ Division by zero handled

**Examples**:
```python
context = {'count': 5, 'total': 10}

# Addition
render("{{count+1}}", context)  # "6"

# Subtraction
render("{{total-count}}", context)  # "5"

# Multiplication
render("{{count*2}}", context)  # "10"

# Division
render("{{total/2}}", context)  # "5" (integer division)

# Invalid
render("{{count&total}}", context)  # "{{INVALID_EXPR:count&total}}"
```

---

#### **Module Functions** (Lines 203-273)

**render_prompt()**:
```python
def render_prompt(template: str, context: Dict[str, Any]) -> str:
    engine = TemplateEngine()
    return engine.render(template, context)
```

**create_context()**:
```python
def create_context(count: int, total: int, filename: str = "", filepath: str = "") -> Dict[str, Any]:
    return {
        'count': count,
        'total': total,
        'filename': filename,
        'filepath': filepath
    }
```

**has_templates()**:
```python
def has_templates(text: str) -> bool:
    return '{{' in text and '}}' in text
```

**preview_template()**:
```python
def preview_template(template: str, sample_context: Dict[str, Any]) -> str:
    return render_prompt(template, sample_context)
```

---

## 🔑 Key Architectural Insights

### **AI Processor Design Philosophy**:

1. **Multi-Provider Strategy**:
   - Unified interface (all clients have `chat()` method)
   - Graceful degradation (simulated responses if no key)
   - Provider-specific adaptations (Gemini's prompt format)

2. **Cost-Conscious**:
   - Token counting (tiktoken or heuristic)
   - Cost estimation before processing
   - Model recommendations (cheaper options highlighted)

3. **Safety-First**:
   - NO eval() in template engine (whitelist operators)
   - Encoding fallback (UTF-8 → latin-1)
   - Exception handling everywhere
   - Simulated responses for testing

4. **User-Friendly**:
   - Progress callbacks (UI integration)
   - API key validation (immediate feedback)
   - Multiple output formats (individual, combined)
   - Template preview (test before running)

---

### **Design Patterns Identified**:

1. **Strategy Pattern** (API Clients):
   - Common interface: `chat(system_prompt, user_prompt)`
   - Different implementations: OpenAI, Gemini, Claude, Perplexity
   - Runtime provider selection

2. **Template Method Pattern** (TemplateEngine):
   - `_substitute()` defines algorithm
   - `_lookup_variable()` and `_evaluate_arithmetic()` are steps

3. **Adapter Pattern** (Perplexity):
   - Adapts Perplexity API to OpenAI interface
   - Uses OpenAI SDK with custom base_url

4. **Factory Pattern** (Implied):
   - Client creation based on provider name
   - Model listing functions return standardized format

5. **Singleton Pattern** (Gemini):
   - Global SDK configuration (`genai.configure(api_key)`)
   - One configuration per process

---

### **Critical Code Sections** (Don't Touch):

1. **token_counter.py - count_tokens() fallback**:
   - Triple fallback (tiktoken → model-specific → heuristic) is critical
   - Heuristic (1 token ≈ 4 chars) is last resort, DO NOT change ratio

2. **api_client.py - has_internet()**:
   - 8.8.8.8:53 (Google DNS) is reliable, don't change
   - 3-second timeout is balanced (not too short, not too long)

3. **template_engine.py - SAFE_OPERATORS whitelist**:
   - ONLY `+`, `-`, `*`, `/` allowed
   - Adding operators requires security review
   - NEVER use eval() or exec()

4. **processor.py - strip_code_fences()**:
   - Regex patterns match common AI output formats
   - Changing patterns could break code extraction

5. **api_client.py - Temperature 0.2**:
   - Low temperature for consistency (not creativity)
   - Changing could make batch processing inconsistent

---

### **Security Considerations**:

**Input Validation**:
- ✅ Template engine whitelist operators (NO eval())
- ✅ File path validation (read_file_safe error handling)
- ✅ API key validation (verify_key before use)

**Network Safety**:
- ✅ 3-second timeout for internet check
- ✅ Exception handling for all API calls
- ✅ Graceful degradation (simulated responses)

**Cost Control**:
- ✅ Token counting before processing
- ✅ Cost estimation visible to user
- ✅ Model recommendations (cheaper first)

---

## 📊 Statistics

**Session 9 Metrics**:
- **Files Read**: 5
- **Lines Analyzed**: ~1,061
- **Functions/Classes Analyzed**: 25+
- **Design Patterns Identified**: 5 (Strategy, Template Method, Adapter, Factory, Singleton)

**AI Processor Module Complete**:
- **Total Files**: 5 (100%)
- **Total Lines**: ~1,061
- **Categories**: Token Counting (1), API Clients (1), Processing (1), Templates (1), Init (1)

**Cumulative Progress**:
- **Total Files Studied**: 46 / 196 (23.5%)
- **Total Lines Studied**: ~10,246 / 58,165 (17.6%)
- **Documentation Read**: 242 / 242 (100%)
- **Overall Comprehension**: ~62% (docs 100%, code 24%)

**Phase 3 Status**: 🔄 **IN PROGRESS** (23/~50 feature module files)
- ✅ **Utils module**: 100% COMPLETE (9/9 files)
- ✅ **Rewriter module**: 100% COMPLETE (9/9 files)
- ✅ **AI processor module**: 100% COMPLETE (5/5 files)
- ⏳ **GUI docks**: 0% (40+ files)
- ⏳ **i18n system**: 0%

---

## 🎯 Key Takeaways

### **What We Now Understand** (AI Processor Module Complete):

1. ✅ **Multi-Provider Support**:
   - 4 providers: OpenAI, Gemini, Claude, Perplexity
   - Unified interface (Strategy pattern)
   - Provider-specific adaptations

2. ✅ **Token Counting & Cost Estimation**:
   - tiktoken for precise counting (with fallback)
   - Cost estimation for major models
   - Model recommendations (cost-effective first)

3. ✅ **Template Engine**:
   - Dynamic variable substitution
   - Arithmetic expressions (NO eval()!)
   - Whitelist security model

4. ✅ **Batch Processing**:
   - Process multiple files with progress tracking
   - Multiple output formats (individual, combined)
   - Error handling per file

5. ✅ **Safety Features**:
   - API key validation
   - Internet connectivity check
   - Graceful degradation (simulated responses)
   - Exception handling everywhere

### **AI Processor Module Architecture**:

```
src/ai_processor/
├── Core
│   └── processor.py          # Batch processing logic
│
├── API Clients
│   └── api_client.py         # Multi-provider clients
│
├── Template Engine
│   └── template_engine.py    # Safe templating (NO eval)
│
├── Token Counting
│   └── token_counter.py      # Token counting & cost estimation
│
└── Init
    └── __init__.py           # Module exports
```

### **Typical Workflow**:

```python
# 1. Create client
client = OpenAIClient(api_key="sk-...", model="gpt-4o-mini")

# 2. Verify key
is_valid, message = client.verify_key()
print(message)

# 3. List files
files = list_files_recursive("data", ['.txt'])

# 4. Process files
results = process_multiple_files(
    files=files,
    client=client,
    system_prompt="You are a helpful assistant.",
    user_prompt_template="Summarize: {{content}}",
    progress_callback=lambda c, t, s: print(f"[{c}/{t}] {s}")
)

# 5. Save results
save_results(results, "output", output_format='individual')
```

### **Reuse Opportunities**:

- ✅ **TemplateEngine**: Reusable for any templating needs (NO eval security!)
- ✅ **Token counting**: Can be used for any LLM integration
- ✅ **API clients**: Reusable wrappers for LLM providers
- ✅ **extract_between_markers()**: Generic text extraction utility

---

## 📝 Protocol Compliance Check

**SIMPLICITY_PROTOCOL_3 Step 1.2 Progress**:

- [x] Study entry points ✅
- [x] Study main application class ✅
- [x] Study initialization system ✅
- [x] Study UI construction ✅
- [x] Study core business logic ✅
- [x] Study utility modules ✅ **100% COMPLETE**
- [x] Study rewriter modules ✅ **100% COMPLETE**
- [x] Study AI processor ✅ **100% COMPLETE**
- [ ] Study GUI docks (Phase 3 next)
- [ ] Study i18n system (Phase 3)
- [ ] Study support systems (Phase 4)
- [ ] Create comprehensive NOTES.md (Phase 5)

**Current Status**: ~62% of Step 1.2 complete

---

**Session 9 Complete! 🎉**  
**AI Processor Module: 100% COMPLETE! ✅**  
**Next**: Continue Phase 3 - Study GUI docks (40+ files) or i18n system
