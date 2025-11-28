# Advanced Conditions - Case Sensitive, Whole Word, and Regex

## 📋 Visão Geral

A partir da versão **v2.2.0**, as **Advanced Conditions** (Condições Avançadas) incluem três checkboxes poderosos que permitem um controle refinado sobre como as condições de busca são aplicadas:

- **Case Sensitive** (Sensível a maiúsculas/minúsculas)
- **Whole Word** (Palavra completa)
- **Regex** (Expressão regular)

Essas opções estão disponíveis em ambos os painéis:
- **Search/Replace Panel**
- **Insert Panel**

---

## 🎯 Funcionalidades

### 1. Case Sensitive (Sensível a Maiúsculas/Minúsculas)

**Checkbox marcado (padrão)**: A busca diferencia entre maiúsculas e minúsculas.

**Exemplo:**
```
Content: "Hello World"
Query: "Hello" ✓ Match
Query: "hello" ✗ No match
```

**Checkbox desmarcado**: A busca ignora a diferença entre maiúsculas e minúsculas.

**Exemplo:**
```
Content: "Hello World"
Query: "hello" ✓ Match
Query: "HELLO" ✓ Match
Query: "HeLLo" ✓ Match
```

### 2. Whole Word (Palavra Completa)

**Checkbox marcado**: A busca corresponde apenas a palavras completas, não partes de palavras.

**Exemplo:**
```
Content: "The cat is in the category"
Query: "cat" (whole word) ✓ Matches "cat" (standalone)
Query: "cat" (whole word) ✗ Does not match "cat" in "category"
```

**Checkbox desmarcado (padrão)**: A busca corresponde a qualquer ocorrência, mesmo dentro de palavras.

**Exemplo:**
```
Content: "The category has cats"
Query: "cat" ✓ Matches in "category"
Query: "cat" ✓ Matches in "cats"
```

### 3. Regex (Expressão Regular)

**Checkbox marcado**: O valor é tratado como uma expressão regular (regex pattern).

**Exemplo:**
```
Content: "Email: user@example.com and admin@domain.org"

Query: "\w+@\w+\.\w+" (regex) ✓ Matches email addresses
Query: "\d+" (regex) ✓ Matches numbers
Query: "^Email$" (regex) ✗ Does not match (strict pattern)
```

**Checkbox desmarcado (padrão)**: O valor é tratado como texto literal.

---

## 🔄 Combinações

As três opções podem ser combinadas para criar filtros muito poderosos:

### Exemplo 1: Case Insensitive + Whole Word
```
Content: "The CAT is in the category"
☐ Case Sensitive
☑ Whole Word
☐ Regex
Query: "cat"
Result: ✓ Matches "CAT" as whole word, ignoring case
```

### Exemplo 2: Regex + Case Insensitive
```
Content: "Hello World"
☐ Case Sensitive
☐ Whole Word
☑ Regex
Query: "hello"
Result: ✓ Matches "Hello" with regex, ignoring case
```

### Exemplo 3: Todas as três opções
```
Content: "The EMAIL address is user@example.com"
☐ Case Sensitive
☑ Whole Word
☑ Regex
Query: "email"
Result: ✓ Matches "EMAIL" as whole word, case-insensitive, using regex
```

---

## 💡 Casos de Uso

### 1. Buscar variáveis exatas (Case Sensitive + Whole Word)
```python
# Encontrar apenas "userName" completo, não "userNameField"
☑ Case Sensitive
☑ Whole Word
Query: "userName"
```

### 2. Buscar emails (Regex)
```
☑ Regex
Query: "\w+@\w+\.\w+"
Matches: test@example.com, user@domain.org
```

### 3. Buscar imports (Case Sensitive)
```javascript
☑ Case Sensitive
Query: "import React"
Matches: "import React" but not "import react"
```

### 4. Buscar tags HTML específicas (Whole Word)
```html
☑ Whole Word
Query: "div"
Matches: "<div>" but not "<divider>"
```

---

## 🎨 Interface Gráfica

As opções aparecem como colunas na tabela de Advanced Conditions:

```
Field    | Operator  | Value  | Scope | Scope Param | Case | Word | Regex
---------|-----------|--------|-------|-------------|------|------|------
content  | contains  | cat    | none  |             |  ☑   |  ☑   |  ☐
filename | contains  | test   | none  |             |  ☐   |  ☐   |  ☑
```

- **Case**: Checkbox para Case Sensitive
- **Word**: Checkbox para Whole Word
- **Regex**: Checkbox para Regex

**Tooltips:**
- Case: "Case sensitive"
- Word: "Match whole word"
- Regex: "Use regular expression"

---

## 🔧 Implementação Técnica

### Classe `Condition` (src/core/filters.py)

```python
@dataclass
class Condition:
    field: str
    operator: str
    value: str
    scope_type: str = "none"
    scope_value: str = ""
    case_sensitive: bool = True      # Default: case sensitive
    whole_word: bool = False         # Default: any occurrence
    use_regex: bool = False          # Default: literal text
```

### Lógica de Matching

```python
def _match_text(self, text: str, pattern: str, operator: str) -> bool:
    # Handle regex
    if self.use_regex:
        flags = 0 if self.case_sensitive else re.IGNORECASE
        if self.whole_word and operator in ("contains", "not contains"):
            pattern = r'\b' + pattern + r'\b'
        # ... regex matching logic
    
    # Handle literal text
    search_text = text if self.case_sensitive else text.lower()
    search_pattern = pattern if self.case_sensitive else pattern.lower()
    
    if self.whole_word and operator in ("contains", "not contains"):
        # Use word boundary regex
        flags = 0 if self.case_sensitive else re.IGNORECASE
        result = re.search(r'\b' + re.escape(search_pattern) + r'\b', 
                          search_text, flags) is not None
        # ... matching logic
```

---

## 📊 Estatísticas de Teste

A funcionalidade foi validada com **8 testes automatizados**:

✅ `test_case_sensitive_true` - Case sensitive matching
✅ `test_case_insensitive` - Case insensitive matching
✅ `test_whole_word_matching` - Whole word boundaries
✅ `test_regex_matching` - Regex patterns
✅ `test_combined_case_and_whole_word` - Combined options
✅ `test_regex_with_case_insensitive` - Regex + case flags
✅ `test_all_three_options_combined` - All three together
✅ `test_filename_with_checkboxes` - Works on filename field

**Teste:** `tests/test_advanced_conditions_checkboxes.py`

---

## 📝 Notas Importantes

1. **Default Behavior**:
   - Case Sensitive: **Marcado por padrão** (True)
   - Whole Word: **Desmarcado por padrão** (False)
   - Regex: **Desmarcado por padrão** (False)

2. **Scope Compatibility**:
   - Essas opções funcionam com **todos os scope types** (brackets, braces, parentheses, tags, etc.)
   - Podem ser combinadas com qualquer campo (content, filename, path, ext, etc.)

3. **Operadores Suportados**:
   - Todos os operadores são afetados por Case Sensitive
   - Whole Word aplica-se principalmente a "contains" e "not contains"
   - Regex funciona com todos os operadores de string

4. **Performance**:
   - Regex pode ser mais lento em grandes arquivos
   - Whole Word usa regex internamente (word boundaries \b)
   - Case insensitive requer conversão de strings

---

## 🔗 Referências

- **Implementação**: `src/core/filters.py` (classe `Condition`)
- **Interface**: `src/app.py` (Search/Replace e Insert panels)
- **Testes**: `tests/test_advanced_conditions_checkboxes.py`
- **Changelog**: v2.2.0 - Checkboxes em Advanced Conditions

---

**Versão**: v2.2.0  
**Data**: 25 de Novembro de 2025  
**Autor**: Josué Amaral
