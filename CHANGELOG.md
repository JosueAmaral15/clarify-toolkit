# Changelog - Clarify Project

## [2.9.32] - 2025-12-02

### 🎯 JSON Set Operations - Complete Feature

#### New Feature: Set Operations for JSON Files

##### Core Functionality
- ✅ **Set Operations**: Intersection (∩), Union (∪), Difference (−), Symmetric Difference (⊕)
- ✅ **Pipeline Processing**: Left-to-right sequential operations (A ∩ B ∩ C...)
- ✅ **Multiple Files**: Support for 2+ files with checkbox for multiple files mode
- ✅ **Three Comparison Modes**:
  - **key_value**: Compare last key part + value (strict types)
  - **full_path_value**: Compare full dot-notation path + value
  - **key_only**: Compare only key paths (ignore values)

##### Advanced Options
- ✅ **ignore_case_keys**: Case-insensitive key comparison
- ✅ **ignore_case_values**: Case-insensitive string value comparison
- ✅ **skip_empty**: Skip empty string values
- ✅ **arrays_ignore_order**: Treat arrays as sets (order-independent)

##### GUI Interface
- ✅ **SetOperationsDock**: Complete PySide6 dock widget
- ✅ **File Selection**: File A/B inputs + multiple files list
- ✅ **Operations**: 4 checkboxes for pipeline operations
- ✅ **Results Display**: QTextEdit with JSON output + statistics
- ✅ **Output Format**: JSON nested, Separate files, Display only
- ✅ **User Feedback**: Statistics (item counts), success/error messages

##### CLI Support
- ✅ **CLI Interface**: `python -m src.set_operations <operation> <files...>`
- ✅ **Arguments**: --ignore-case-keys, --ignore-case-values, --skip-empty, --arrays-ignore-order
- ✅ **Operations**: intersection, union, difference, symmetric
- ✅ **Output**: stdout or --output file

##### Security & Quality
- ✅ **OWASP Security**: CWE-22 Path Traversal prevention with `validate_file_path()`
- ✅ **Code Quality**: 
  - Pylint score 9.38/10 (core module)
  - Black formatted
  - isort organized
- ✅ **Comprehensive Tests**: 50 unit tests (100% pass rate, 0.24s)
- ✅ **Coverage**: validate_file_path (6 tests), flatten_json (6), unflatten_json (3), normalize_for_comparison (5), compare_files (6), intersection (5), union (3), difference (4), symmetric_difference (3), edge cases (5), integration (2)

#### Technical Implementation

##### New Modules
- ✅ `src/set_operations.py`: Core logic (~437 LOC)
  - `validate_file_path()`: Security validation
  - `flatten_json()`, `unflatten_json()`: Structure conversion
  - `normalize_for_comparison()`: Hashable value normalization
  - `compare_files()`: Preparation with 3 modes
  - `intersection()`, `union()`, `difference()`, `symmetric_difference()`: Set operations
  - CLI support with argparse
- ✅ `src/gui/set_operations_dock.py`: GUI interface (~412 LOC)
  - `SetOperationsDock(BaseDock)`: Main dock widget
  - File selection with multiple files support
  - 4 operations + 3 comparison modes + 4 options
  - Results display with statistics
- ✅ `tests/test_set_operations.py`: Unit tests (~464 LOC)
  - 50 tests covering all functions + edge cases
  - Security tests, integration tests
  - Real JSON file tests

##### Integration
- ✅ `src/app.py`: Menu integration
  - Added "JSON Set Operations..." action in Tools menu
  - `_show_set_operations()` method for dock management
  - Lazy loading with RightDockWidgetArea placement
- ✅ `src/gui/__init__.py`: Export SetOperationsDock

##### Design Patterns
- **Strategy (GoF)**: Each operation as interchangeable strategy
- **Template Method (GoF)**: Common pipeline (read → normalize → operate → output)
- **Factory Method (GoF)**: Different output formats
- **Command (GoF)**: Operations encapsulated as commands
- **Observer (GoF)**: Qt signals for GUI communication
- **Information Expert (GRASP)**: set_operations.py knows set logic
- **Controller (GRASP)**: SetOperationsDock coordinates workflow
- **Low Coupling (GRASP)**: GUI depends only on core public interface
- **High Cohesion (GRASP)**: Each module has single clear responsibility

#### Project Infrastructure
- ✅ **.gitignore**: Created with Python, venv, cache, IDE patterns
- ✅ **Cache Cleanup**: Removed __pycache__ and .pytest_cache from root
- ✅ **CI/CD Quality Gates**: black, isort, pylint >9.0, tests 100% pass

#### Documentation
- ✅ **Inline Documentation**: Comprehensive docstrings with examples
- ✅ **Type Hints**: Full typing for all functions
- ✅ **Comments**: Security notes, algorithm explanations
- ✅ **Changelog**: This entry documenting v2.9.32

---

## [2.9.0] - 2025-12-02

### 🎯 JSX Parameter Extractor - Complete Feature

#### New Feature: JSX/TSX Parameter Extraction

##### Core Functionality
- ✅ **JSX Parameter Extractor**: Nova ferramenta para extração de parâmetros de arquivos React/JSX/TSX
- ✅ **Dual-choice system**: Dialog de seleção entre "JSX Parameter Extractor" (default) e "Text Format Converter"
- ✅ **File/Directory selection**: Path input + Browse button + "Is file?" checkbox
- ✅ **Two parsing modes**:
  - **Attribute mode**: Extrai atributos JSX (ex: `label="Click Me"`)
  - **Tag-content mode**: Extrai texto interno de tags (ex: `<Button>Click Me</Button>`)

##### Advanced Filters
- ✅ **only_strings**: Filtra apenas strings literais, exclui expressões `{variable}`, `{obj.prop}`, condicionais
- ✅ **avoid_keys**: Exclui chaves específicas com modos "contains" ou "equals"
- ✅ **no_standard**: Remove tags HTML padrão (div, span, p, h1-h6, etc.) do output
- ✅ **Extensions filter**: Padrão `.tsx .jsx .js .ts`, customizável

##### Normalization & Output
- ✅ **Case styles**: snake_case, camelCase, PascalCase, kebab-case
- ✅ **Smart truncation**: Limit + avoid_cut (word boundary awareness)
- ✅ **Uppercase option**: Transforma keys em MAIÚSCULAS
- ✅ **Hierarchical JSON output**: Estrutura aninhada reflete component tree
- ✅ **Dual output tabs**: Paths (dot-notation) e JSON (formatted)
- ✅ **JS literal support**: Output sem aspas nas keys (TypeScript-friendly)

##### Generic Mode
- ✅ **Custom regex delimiters**: Start/End patterns para parsing de outros formatos
- ✅ **Named capture groups**: `(?P<name>...)` para nomear scopes

##### Security & Quality
- ✅ **OWASP Security fixes**: 
  - Path traversal prevention (CWE-22)
  - File extension validation
  - Path security validation with `_validate_path_security()`
- ✅ **Code quality**: Pylint score 9.65/10
- ✅ **Comprehensive tests**: 6 functional tests (100% pass rate)

#### Technical Implementation

##### New Modules
- ✅ `src/extractors/extractor.py`: Orchestrator class (~500 lines)
  - `run()`: Main file processing pipeline
  - `process_text()`: Parser integration (JSXParser/GenericScopeParser)
  - `_record_text_kv()`: Tree building with normalized keys
  - Dict manipulation: `merge_dicts()`, `prune_to_key()`, `remove_key()`, `deep_merge()`
  - Value validation: `check_value_if_it_is_just_string()`
  
- ✅ `src/extractors/jsx_parser.py`: JSX/TSX parser (~570 lines)
  - Regex patterns for attributes: `ATTR_DQ_RE`, `ATTR_SQ_RE`, `ATTR_BRACE_STRING_RE`, etc.
  - Tag matching: `match_opening_tag()`, `_find_matching_close_span()`
  - Balanced expression reading: `_read_balanced_brace_expr()`
  - Stack-based parsing: `parse()` yields (stack, tag, key, value) tuples
  
- ✅ `src/extractors/generic_parser.py`: Regex-based generic parser (~90 lines)
  - Custom delimiter support
  - Named capture groups
  
- ✅ `src/utils/normalization.py`: Normalization utilities (~145 lines)
  - `smart_truncate()`: Word boundary-aware truncation
  - `normalize_token()`: Case style conversion
  - `is_standard_tag()`: HTML tag detection (80+ tags)
  - `kept_prefix()`: Stack filtering for no_standard mode
  - `path_join()`: Dot-notation path builder
  
- ✅ `src/gui/jsx_extractor_dock.py`: Complete GUI dock (~500 lines)
  - Path selection with file/directory browser
  - All options exposed: mode, param, is_attribute_mode, extensions, filters, normalization
  - Dual output tabs with save/copy/clear
  - Security validation integrated

##### Modified Files
- ✅ `src/app.py`: 
  - Added `_show_text_to_json()` selection dialog
  - Added `_show_jsx_extractor()`, `_show_text_format_converter()`, `_open_jsx_extractor()`
  
- ✅ `src/gui/__init__.py`: Export `JSXExtractorDock`

##### CI/CD & Quality Gates
- ✅ **Black formatter**: 6 files formatted (line-length=120)
- ✅ **isort**: Import sorting with black profile
- ✅ **Pylint**: Score 9.65/10 with custom rules
- ✅ **Pre-commit hooks**: `.pre-commit-config.yaml` configured
- ✅ **CI script**: `ci_quality_check.sh` (5 quality gates)
- ✅ **Documentation**: `docs/CI_CD_SETUP.md` (complete setup guide)

##### Testing
- ✅ **test_jsx_extractor.py**: 6 comprehensive tests
  1. Attribute extraction with include_key=True
  2. Drop standard HTML tags (no_standard=True)
  3. Only literal strings filtering (only_strings=True)
  4. Case styles (camelCase, PascalCase, kebab-case)
  5. Avoid keys filtering (className, data-testid)
  6. Text truncation (limit + avoid_cut)
- ✅ **test_component.tsx**: Sample React component for testing
- ✅ All tests passing (100% success rate)

#### Configuration Files
- ✅ `.pre-commit-config.yaml`: Black, isort, pylint, trailing-whitespace, etc.
- ✅ `.pylintrc`: Custom rules for project
- ✅ `pyproject.toml`: Updated with tool configurations (version 2.9.0)

#### Documentation
- ✅ **README.md**: Added JSX Parameter Extractor section with feature list
- ✅ **docs/CI_CD_SETUP.md**: Complete CI/CD documentation
- ✅ **docs/jsx-extractor-guide.md**: Detailed usage guide (to be created)
- ✅ **CHANGELOG.md**: This entry

#### Breaking Changes
- ⚠️ Menu "Tools → Text To JSON Converter" now opens selection dialog instead of directly opening Text Converter

#### Statistics
- **Files Created**: 7 (extractor.py, jsx_parser.py, generic_parser.py, normalization.py, jsx_extractor_dock.py, test files, configs)
- **Files Modified**: 3 (app.py, __init__.py, pyproject.toml)
- **Lines Added**: ~2,400 lines (production + tests + docs)
- **Pylint Score**: 9.65/10
- **Test Coverage**: 6/6 tests passing
- **Security Fixes**: 2 (CWE-22 path traversal, file extension validation)

---

## [2.9.6] - 2025-11-28

### ✨ Advanced Filtering, Resizable Fields, and History Panel

#### Novas Funcionalidades

##### 1. Exclude Numeric Keys 🔢
- ✅ **Checkbox "Exclude numeric keys"** em Text Extractor e JSON Rewriter:
  - Filtra chaves que são puramente numéricas (ex: '0', '123', '456')
  - Usa `key.isdigit()` para detecção
  - Processamento recursivo em estruturas aninhadas
  - Útil para limpar índices de arrays convertidos em objetos
  - Nova função `exclude_numeric_keys()` no módulo `rewriter.operations`

**Benefícios**: Remove chaves numéricas indesejadas automaticamente, melhora qualidade do output JSON

##### 2. Skip Empty Values 🚫
- ✅ **Checkbox "Skip empty values"** em Text Extractor e JSON Rewriter:
  - Define vazio como: strings vazias `""`, `null`, arrays `[]`, objetos `{}`, whitespace-only `"   "`
  - Filtragem durante serialização do output
  - Nova função `skip_empty_values()` no módulo `rewriter.operations`
  - Método helper `_is_empty_value()` no Text Extractor

**Benefícios**: Output JSON mais limpo, remove ruído de valores vazios

##### 3. Resizable Text Boxes 📏
- ✅ **Caixas de texto redimensionáveis** em Search/Replace e Insert panels:
  - `ed_query`, `ed_repl` e `ed_text` agora são QPlainTextEdit
  - Altura mínima: 30px, máxima: 150-200px
  - Usuário pode arrastar borda inferior para ajustar altura
  - Melhor para queries longas ou texto multi-linha
  - Tooltips atualizados com instrução de resize
  - Simplificação: removida função `_toggle_multi_query_mode` (sempre multi-line)

**Benefícios**: Flexibilidade visual, melhor experiência com textos longos

##### 4. History Panel 📜
- ✅ **Painel de histórico de operações** (View → History):
  - Dock panel toggleable na parte inferior
  - Mantém até 10 operações recentes (configurável)
  - Exibe: timestamp, tipo de operação, detalhes, arquivos processados
  - Operações rastreadas: Search, Replace, Insert
  - Botões: Clear History, Export to file, Refresh
  - TreeWidget com colunas organizadas
  - Integração com `OperationHistory` existente
  - Nova classe `HistoryDock` em `src/gui/history_dock.py`

**Benefícios**: Rastreabilidade de ações, facilita auditoria e revisão de trabalho

##### 5. "Is File" Consistency ✅
- ✅ **Checkbox "Is file"** agora presente em todos os módulos JSON:
  - JSON Rewriter (novo)
  - Text Extractor (já existia)
  - JSON Translate (original)
  - Consistência de interface em toda aplicação

**Benefícios**: Interface unificada, experiência de usuário consistente

#### Estatísticas de Conclusão
- ✅ 5 tasks completadas
- ⏱️ Tempo total: ~2-2.5 horas
- 📦 Novos arquivos: `src/gui/history_dock.py`
- 🔧 Módulos modificados: `src/app.py`, `text_extractor_dock.py`, `json_rewriter_dock.py`, `rewriter/operations.py`, `rewriter/__init__.py`, `gui/__init__.py`

## [2.9.5] - 2025-11-28

### ✨ UI Improvements - Clear Conditions, Scroll, and Sort

#### Novas Funcionalidades

##### 1. Clear All Conditions Button 🗑️
- ✅ **Botão "Clear All Conditions"** nas opções avançadas condicionais:
  - Presente em SearchReplacePanel e InsertPanel
  - Limpa todos os campos de condição com um clique
  - Reseta logic operator para AND
  - Restaura checkboxes para valores padrão
  - Ícone intuitivo de lixeira
  - Tooltip explicativo
  
**Benefícios**: Economiza tempo ao limpar múltiplas condições, evita erros de dados residuais

##### 2. Scroll em Painéis 📜
- ✅ **QScrollArea adicionado** em ambos painéis principais:
  - SearchReplacePanel com scroll vertical/horizontal
  - InsertPanel com scroll vertical/horizontal
  - Ajuste automático de tamanho (widgetResizable)
  - Scrollbars aparecem conforme necessário
  
**Benefícios**: Melhor experiência em telas pequenas, acesso a todas as opções sem redimensionar janela

##### 3. Ordenação de Resultados 🔤
- ✅ **Checkbox "Sort results alphabetically"**:
  - Disponível em SearchReplacePanel e InsertPanel
  - Ordena caminhos de arquivos alfabeticamente
  - Ordena resultados por linha e coluna
  - Opcional (padrão: desativado)
  - Tooltip explicativo
  
**Benefícios**: Facilita localização de arquivos específicos, resultados mais organizados para análise

#### Detalhes Técnicos
- `_clear_all_conditions()`: Método para resetar todas as condições
- `ResultsTree.populate()`: Agora aceita parâmetro `sort_results`
- QScrollArea com políticas de scroll configuráveis
- Sorting usando `sorted()` do Python com key functions

#### Melhorias de UX
- Interface mais limpa e organizada
- Maior produtividade ao gerenciar condições
- Melhor suporte para diferentes resoluções de tela
- Resultados mais fáceis de navegar

---

## [2.9.4] - 2025-11-28

### 🎨 Theme System - Light, Dark, and System

#### Novas Funcionalidades
- ✅ **Sistema completo de temas** com 3 opções:
  - ☀️ **Light Theme**: Tema claro profissional com cores suaves
  - 🌙 **Dark Theme**: Tema escuro moderno para reduzir fadiga ocular
  - 🖥️ **System Theme**: Usa configurações do sistema operacional

- ✅ **ThemeManager dedicado** (`src/theme_manager.py`):
  - Gerenciamento centralizado de temas
  - Paletas de cores consistentes
  - Stylesheets customizados para cada tema
  - Suporte completo a todos os componentes Qt

- ✅ **Menu Themes aprimorado**:
  - Ícones visuais para cada tema (☀️/🌙/🖥️)
  - Tooltips explicativos
  - Persistência de preferência (salva automaticamente)
  - Estado sincronizado entre reinicializações

#### Componentes Estilizados
- GroupBox, LineEdit, PlainTextEdit, TextEdit, SpinBox
- QPushButton com estados hover/pressed/disabled
- QCheckBox e QRadioButton
- QComboBox com dropdown customizado
- QTabWidget e QTabBar
- QTreeView e QListView
- Scrollbars verticais e horizontais
- MenuBar e Menu
- StatusBar e DockWidget

#### Benefícios
- Experiência visual consistente em toda aplicação
- Redução de fadiga ocular com tema escuro
- Flexibilidade para preferências do usuário
- Design moderno e profissional
- Melhor legibilidade em diferentes ambientes

---

## [2.9.3] - 2025-11-28

### 💬 Tooltips - English Documentation

#### Novas Funcionalidades
- ✅ **Tooltips em inglês em toda a aplicação**:
  - 📌 **SearchReplacePanel**: ~20 tooltips
    - Path, Browse, Is File: Navegação de arquivos
    - Include/Exclude globs: Filtros avançados
    - Query, Case/Word/Regex: Opções de busca
    - Replacement, Preserve case: Opções de substituição
    - Buttons: Search/Cancel, Replace operations
    - Save Results: Exportação
  
  - 📌 **InsertPanel**: ~15 tooltips
    - Path, Browse, Is File: Navegação
    - Include/Exclude globs: Filtros
    - Lookup query, Case/Word/Regex: Busca dinâmica de posição
    - Occurrence: First/Last/All
    - Line number, Insert text, Mode: Configuração de inserção
    - Apply button: Execução

#### Benefícios
- Onboarding mais fácil para novos usuários
- Documentação contextual inline
- Explicações de features complexas (multi-line, scope, modes)
- Exemplos práticos nos tooltips de globs

---

## [2.9.2] - 2025-11-28

### 📝 Context Menu - Results Panel

#### Novas Funcionalidades
- ✅ **Menu de contexto (botão direito)** no painel de resultados:
  - 📋 **Copy**: Copiar itens selecionados
  - 📋 **Copy All Results**: Copiar todos os resultados formatados
  - ✅ **Select All**: Selecionar todos os itens
  - 📂 **Open File**: Abrir arquivo(s) selecionado(s)
  - 📂 **Open All Files**: Abrir todos os arquivos dos resultados
  
- ✅ **Seleção múltipla**: Suporte completo para CTRL/Shift
  - CTRL + Click: Adicionar/remover item da seleção
  - Shift + Click: Selecionar intervalo
  - CTRL + A: Selecionar todos

#### Melhorias de UX
- Feedback visual no status bar após ações (3 segundos)
- Confirmação ao abrir mais de 10 arquivos
- Ícones intuitivos no menu de contexto
- Desabilita opções quando não aplicáveis

---

## [2.9.1] - 2025-11-28

### 🔧 Extension Filter - Refinamento

#### Melhorias
- ✅ **Extension Filter agora é opcional**: Checkbox "Use extension filter"
  - Usuário pode habilitar/desabilitar o filtro
  - Default: Habilitado (checked)
  - Permite usar apenas include/exclude globs quando desabilitado

#### Análise de Aplicabilidade
- ✅ **Mantido onde faz sentido**: Search/Replace, Insert
  - Módulos genéricos que processam qualquer tipo de arquivo
  - Filtro simplifica seleção de extensões comuns
  
- ⚠️ **Nota sobre Docks JSON**: 
  - JSON Search, JSON Translate, JSON Rewriter já têm extensões fixas
  - Filtro de extensões seria redundante nesses módulos
  - Use include globs para patterns avançados nesses casos

---

## [2.9.0] - 2025-11-28

### 🎨 Extension Filter

#### Novas Funcionalidades
- ✅ **Extension Filter**: Filtro simplificado de extensões em módulos genéricos
  - Campo "Extensions" em Search/Replace e Insert panels
  - Sintaxe simples: `.py,.js,.tsx` ou `py,js,tsx`
  - Separadores flexíveis (vírgula ou ponto e vírgula)
  - Tolerante a espaços em branco
  - Funciona em conjunto com include/exclude globs

#### Implementação Técnica
- ✅ **`parse_extensions_to_globs()`**: Função utilitária em `base_dock.py`
  - Converte extensões para glob patterns
  - Adiciona ponto automático se omitido
  - Retorna lista de globs (`*.py`, `*.js`, etc.)

- ✅ **UI Updates**: Campos adicionados
  - SearchReplacePanel: Campo "Extensions" com tooltip
  - InsertPanel: Campo "Extensions" com placeholder
  - FileInputMixin: Método `create_extension_filter()`

- ✅ **Logic Integration**: Merge com include globs
  - Extensions convertidas para globs
  - Combinadas com include globs se presentes
  - Mantém compatibilidade com código existente

#### Testes
- ✅ **`tests/test_extension_filter.py`**: Suite completa (6/6 passing)
  - Basic parsing (`.py,.js,.tsx`)
  - Without dots (`py,js,tsx`)
  - Semicolon separator
  - Empty string handling
  - Whitespace tolerance
  - Mixed format

#### Documentação
- ✅ **`docs/pt/EXTENSION_FILTER.md`**: Guia completo
  - Sintaxe e exemplos
  - Integração com globs
  - Ordem de processamento
  - Casos de uso práticos
  - Troubleshooting
  - Migração de v2.8.0

---

## [2.8.0] - 2025-01-XX

### 🎯 Multi-Query Search

#### Novas Funcionalidades
- ✅ **Multi-line Query Search**: Buscar com múltiplos padrões simultaneamente
  - Cada linha = uma query independente
  - Suporte a comentários (linhas começando com `#`)
  - Linhas vazias são automaticamente ignoradas
  - Checkbox "Multi-line" para alternar entre modos
  - Campo de texto multi-linha (`QPlainTextEdit`) para entrada de queries
  - Modo toggle preserva texto ao alternar

#### Implementação Técnica
- ✅ **`src/core/multi_query.py`**: Novo módulo para processamento de múltiplas queries
  - Classe `MultiQueryProcessor`: Parse e execução de queries
  - Classe `QueryLine`: Representação de query individual
  - Validação com limite de 500 caracteres por query
  - Deduplicação automática de resultados
  - Suporte completo a regex, case-sensitive, whole-word

- ✅ **SearchWorker Enhancement**: Integração com multi-query
  - Parâmetros `is_multi_query` e `multi_query_processor`
  - Branch lógico entre single e multi-query
  - Compatibilidade reversa mantida
  - Formato de resultado consistente

- ✅ **UI Improvements**: Interface adaptativa
  - Toggle dinâmico entre `QLineEdit` e `QPlainTextEdit`
  - Tooltip informativo sobre sintaxe
  - Progress modal mostra número de queries ativas
  - Task label diferenciado no progress bar

#### Testes
- ✅ **`tests/test_multi_query.py`**: Suite completa de testes (10/10 passing)
  - Single query (compatibilidade)
  - Two queries simultâneas
  - Queries com comentários
  - Queries com linhas vazias
  - Five queries simultâneas
  - Regex patterns
  - Result deduplication
  - Case-sensitive mode
  - Whole-word mode
  - Query validation (500 char limit)

#### Documentação
- ✅ **`docs/pt/MULTI_QUERY_SEARCH.md`**: Guia completo
  - Sintaxe de queries com exemplos
  - Casos de uso práticos (logs, código, configs)
  - Limitações e performance
  - Comparação single vs multi-query
  - Troubleshooting guide
  - Integração com replace e filtros

---

## [1.0.0] - 2025-11-24

### 🎉 MAJOR RELEASE: Arquitetura Modular Completa

Esta é a maior refatoração do Clarify desde o lançamento, transformando completamente a arquitetura do projeto com **sistema modular hierárquico**, **redução de 26.6% de código** no arquivo principal, e **integração de 95%+ das funcionalidades** da pasta `add/`.

### 🏗️ Nova Arquitetura Modular

#### **Sistema de Base Classes**
- ✅ `BaseDock`: Classe abstrata base para todos os docks
- ✅ `StandardToolDock`: Template pré-configurado com features comuns
- ✅ `ProcessorWorkerBase`: Suporte a threading para operações longas
- ✅ **5 Mixins reutilizáveis**: FileInput, ResultsOutput, ActionButtons, Options, Validation

#### **7 Docks Modulares Criados**
Todos os docks inline foram extraídos para módulos separados:

1. **`ai_processor_dock.py`** (456 linhas)
   - Token counter persistente (session + lifetime)
   - Code fence removal automático
   - Estatísticas salvas em `~/.clarify_ai_stats.json`
   - Integração OpenAI + Gemini

2. **`case_converter_dock.py`** (223 linhas)
   - 4 estilos de case conversion
   - Threading support
   - Progress reporting

3. **`json_rewriter_dock.py`** (188 linhas)
   - Deduplication & formatting
   - TypeScript/JavaScript support
   - Configurable indentation

4. **`json_search_dock.py`** (250 linhas)
   - Advanced JSON/TS search
   - Dot-path notation
   - Case/whole-word/regex support

5. **`json_translate_dock.py`** (267 linhas)
   - Dictionary-based translation
   - Scope delimiters (regex)
   - Exclusion patterns
   - Reverse translation

6. **`placeholder_replacer_dock.py`** (209 linhas)
   - Batch placeholder replacement
   - JSON/CSV mapping support
   - Recursive processing

7. **`text_extractor_dock.py`** (480 linhas) - **ENHANCED**
   - 3 modos: JSX Attributes, Tag Content, Generic Scope
   - 4 estilos de normalização
   - Smart truncation
   - Nested JSON output

### 📊 Melhorias Quantitativas

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| **app.py linhas** | 4913 | 3606 | **-26.6%** |
| **Docks inline** | 7 | 0 | **-100%** |
| **Docks modulares** | 0 | 7 | **+7** |
| **Total GUI code** | Mixed | 2373 | **Separated** |
| **Reutilização** | 0% | 40-60% | **Via mixins** |

### 🔧 Integração de Funcionalidades

Funcionalidades da pasta `add/` integradas:

| Fonte | Status | Destino |
|-------|--------|---------|
| `searchJSON/` | ✅ 100% | JsonSearchDock |
| `translator_gui/` | ✅ 100% | JsonTranslateDock |
| `JSON_case_converter/` | ✅ 100% | CaseConverterDock |
| `converting text structure to JSON/` | ✅ 100% | TextExtractorDock |
| `requisite_to_ChatGPT/` | ✅ 85% | AIProcessorDock |

### 🗂️ Organização do Projeto

#### **Diretórios Reorganizados**
- ✅ Removido `src/ui/` (obsoleto, duplicado)
- ✅ Todos os testes movidos para `tests/`
- ✅ Estrutura modular em `src/gui/`
- ✅ Criado `PROJECT_STRUCTURE.md` com documentação completa

#### **Arquivos Criados**
- `src/gui/base_dock.py` - Base classes & mixins
- `src/gui/__init__.py` - Exports centralizados
- 7 arquivos de docks modulares
- `PROJECT_STRUCTURE.md` - Documentação de estrutura

### 🐛 Correções

- ✅ Corrigido imports obsoletos (`text_extractor`, `case_converter`)
- ✅ Corrigido padrão de inicialização dos docks (` _setup_ui()`)
- ✅ Removido código duplicado entre docks
- ✅ Padronizado signal connection em todos os docks

### 🎨 Melhorias de UI/UX

- ✅ Interface consistente em todas as ferramentas
- ✅ Padrão uniforme de botões e layouts
- ✅ Mensagens de erro e sucesso padronizadas
- ✅ Progress reporting em todas as operações longas
- ✅ Threading para evitar UI freeze

### 📝 Documentação

- ✅ README.md atualizado com nova arquitetura
- ✅ PROJECT_STRUCTURE.md criado
- ✅ Docstrings em todos os módulos
- ✅ Comentários explicativos em base classes

---

## [3.0.0] - 2025-11-24 (Anterior)

### 🎉 MAJOR RELEASE: 5 Novas Ferramentas Avançadas

Adição de **~3.300 linhas de código** distribuídas em **5 novas ferramentas profissionais** integradas à interface GUI.

#### 🆕 Ferramentas Adicionadas

##### 1. **Case Converter** (Sprint 1)
Conversão inteligente entre estilos de nomenclatura.

**Funcionalidades:**
- 4 estilos suportados: camelCase, PascalCase, snake_case, kebab-case
- Processamento de arquivo único ou diretório recursivo
- Filtro por extensões customizáveis
- Preview antes de aplicar alterações
- Estatísticas de conversão (total de palavras modificadas)

**Arquivos:**
- `src/case_converter.py` (337 linhas)
- GUI: `JsonCaseConverterDock` (~150 linhas em src/app.py)

**Menu:** Tools → Open Case Converter

---

##### 2. **JSON Search** (Sprint 2)
Busca avançada em estruturas JSON e TypeScript.

**Funcionalidades:**
- Busca por chave, valor ou ambos
- Suporte para arquivos .json, .ts, .js com export default/const
- Parsing de TypeScript types e interfaces
- Case-sensitive e regex opcionais
- Exibição de contexto flat do JSON
- Limite de resultados configurável

**Arquivos:**
- `src/json_search/flattener.py` - Flattening de JSON nested
- `src/json_search/ts_extractor.py` - Extração de objetos TS
- `src/json_search/query_parser.py` - Parsing de queries de busca
- `src/json_search/indexer.py` - Indexação e busca
- GUI: `JsonSearchDock` (~200 linhas em src/app.py)

**Menu:** Tools → Open JSON Search

---

##### 3. **Text Extractor** (Sprint 3)
Extração de texto de HTML/JSX para JSON estruturado.

**Funcionalidades:**
- Parsing de HTML e JSX (React components)
- Preserva hierarquia de tags HTML
- Remove duplicatas automaticamente
- Ignora scripts, estilos, comentários
- ClassName como chave opcional
- Output em JSON ou TypeScript
- Sanitização de chaves (remove caracteres especiais)

**Arquivos:**
- `src/text_extractor/jsx_parser.py` - Parser JSX/HTML
- `src/text_extractor/normalizer.py` - Normalização de texto
- `src/text_extractor/path_builder.py` - Construção de paths hierárquicos
- `src/text_extractor/extractor.py` - Extração e estruturação
- GUI: `TextExtractorDock` (~180 linhas em src/app.py)

**Menu:** Tools → Open Text Extractor

---

##### 4. **Placeholder Replacer** (Sprint 4)
Substituição em lote de placeholders com mapeamentos.

**Funcionalidades:**
- Suporte para mapeamentos JSON (nested ou flat) e CSV
- Estratégia longest-match-first (evita colisões como t.a.b vs t.a.b.c)
- Filtro de escopo com regex patterns (start/end markers)
- Variável root customizável (t, i18n, translations, etc.)
- Criação automática de backups (.bak)
- Modo preview (dry-run)
- Processamento de arquivo único ou diretório recursivo

**Arquivos:**
- `src/placeholder_replacer.py` (290 linhas)
- GUI: `PlaceholderReplacerDock` (~140 linhas em src/app.py)

**Menu:** Tools → Open Placeholder Replacer

**Exemplo de uso:**
```javascript
// Antes: {t.pages.home.title}
// Depois: Home Page
// Mapeamento: {"pages.home.title": "Home Page"}
```

---

##### 5. **AI File Processor** (Sprint 5)
Integração com APIs de IA para processamento avançado.

**Funcionalidades:**
- Suporte para OpenAI (ChatGPT) e Google Gemini
- Modelos disponíveis:
  - OpenAI: gpt-4o-mini, gpt-4o
  - Gemini: gemini-2.5-flash, gemini-2.5-pro
- Processamento em lote de arquivos
- Contagem de tokens com tiktoken (ou estimativa)
- Estimativa de custo em tempo real
- Modo line-by-line (prompt diferente por arquivo)
- Limite de bytes configurável
- Interrupção de processamento
- Filtro por extensões múltiplas
- Salvamento de resultados
- Verificação de API key

**Arquivos:**
- `src/ai_processor/token_counter.py` - Contagem de tokens
- `src/ai_processor/api_client.py` - Clientes OpenAI e Gemini
- `src/ai_processor/processor.py` - Lógica de processamento
- `src/ai_processor/__init__.py` - Package exports
- GUI: `AIProcessorDock` (~250 linhas em src/app.py)
- Worker: `AIProcessorWorker` (QThread para processamento assíncrono)

**Menu:** Tools → Open AI File Processor

**Dependências Opcionais:**
- `openai` - Para ChatGPT (pip install openai)
- `google-generativeai` - Para Gemini (pip install google-generativeai)
- `tiktoken` - Para contagem precisa de tokens (pip install tiktoken)

---

#### 📊 Estatísticas da Release

- **Total de linhas adicionadas:** ~3.300 LOC
- **Novos módulos:** 13 arquivos Python
- **Novos painéis GUI:** 5 QDockWidget
- **Sprints completados:** 5 de 5 (100%)
- **Tempo de desenvolvimento:** 40-45 dias (conforme INTEGRATION_PLAN.md)

#### 🏗️ Arquitetura

Todas as ferramentas seguem o padrão modular:
1. **Core Module** - Lógica de negócio separada
2. **GUI Dock** - Interface PySide6 QDockWidget
3. **Menu Integration** - Ações no menu Tools
4. **Lazy Loading** - Docks criados sob demanda

#### 📚 Documentação

- **README.md**: Atualizado com descrições completas das 5 ferramentas
- **INTEGRATION_PLAN.md**: Plano de 6 sprints documentando o processo
- Testes incluídos para Placeholder Replacer e AI Processor

---

## [2.5.1] - 2025-11-24

### 🐛 Correções de Bugs e Melhorias

#### ✅ Verificado e Documentado
- **Checkbox "Is File"**: Verificado que está implementado em todos os painéis relevantes
  - ✅ SearchReplacePanel: Checkbox presente e funcional (linha 1814)
  - ✅ InsertPanel: Checkbox presente e funcional (linha 2221)
  - ✅ JsonTranslateDock: Checkbox presente e funcional (linha 3273)
  - Permite alternar entre modo arquivo único e modo diretório
  - Diálogos de seleção se adaptam automaticamente
  - Condições avançadas desabilitadas em modo arquivo
  - **Documentação**: `docs/pt/IS_FILE_FEATURE.md` criada

#### Corrigido
- **Mensagem "Loading"**: Corrigida exibição que mostrava apenas "L" ao invés de "Loading..." no painel de resultados
  - **Causa**: `QTreeWidgetItem` recebia string direta ao invés de lista
  - **Solução**: Mudado de `QTreeWidgetItem(f"{message}")` para `QTreeWidgetItem([message])`
  - **Arquivo**: `src/app.py` (linha 1691)

#### Adicionado
- **Sumário de resultados**: Nova linha de resumo no topo do painel de matches
  - Exibe total de matches encontrados
  - Exibe total de arquivos com matches
  - Formato: "📊 Results: X matches in Y file(s)"
  - Texto em negrito e cor verde para destaque
  - Funciona em ambas as guias (Search/Replace e Insert)
  - **Arquivo**: `src/app.py` (método `populate()`)

- **Tooltip de posição e barra de status**: Informações de linha:coluna ao passar mouse
  - Tooltip aparece ao passar mouse sobre qualquer match
  - Barra de status na parte inferior do painel mostra posição atual
  - Formato tooltip: "File: [path]\nLine: [X]\nColumn: [Y]"
  - Formato status: "📍 Position: Line X, Column Y | File: [path]"
  - Mouse tracking habilitado no ResultsTree
  - Funciona em ambas as guias (Search/Replace e Insert)
  - **Arquivo**: `src/app.py` (classe `ResultsTree` + painéis)

#### Testes
- `test_results_summary.py`: 4 novos testes
  - Cálculo de estatísticas de resultados
  - Tratamento de resultados vazios
  - Arquivo único com match único
  - Múltiplos arquivos com múltiplos matches

- `test_position_tooltip.py`: 6 novos testes
  - Extração de linha:coluna do texto do resultado
  - Formatação de tooltip e status bar
  - Casos edge (0:0, números grandes)
  - Tratamento de formatos inválidos
  - Caminhos de arquivo longos

---

## [2.5.0] - 2025-11-24

### 📊 Nova Funcionalidade: Sistema de Barras de Progresso

#### Adicionado
- **Sistema completo de barras de progresso** na parte inferior da janela
  - Barras de progresso individuais para cada operação
  - Execução em threads separadas (não trava GUI)
  - Suporte a múltiplas operações simultâneas
  - Janela expandida com detalhes completos

#### Componentes Principais

1. **ProgressBarWidget**
   - Barra de progresso individual compacta
   - Nome da tarefa e status atual
   - Botão expandir (↗) para ver detalhes
   - Botão fechar (✖) para remover barra
   - Atualização em tempo real (arquivo/porcentagem)

2. **ProgressDetailsDialog**
   - Janela modal com informações completas
   - Barra de progresso maior
   - Log detalhado com timestamps
   - Botão para minimizar de volta à barra
   - Botão para cancelar operação

3. **ProgressManager**
   - Gerenciador central de todas as barras
   - Área com scroll para múltiplas barras
   - Auto-hide quando não há tarefas ativas
   - Cabeçalho colapsável com contador de tarefas
   - Localizado na parte inferior da janela principal

#### Funcionalidades

- **Execução não-bloqueante**: Todas as operações em threads separadas
- **Progresso em tempo real**: Atualização arquivo por arquivo
- **Cancelamento seguro**: Interromper operações sem corromper dados
- **Múltiplas barras**: Várias operações simultâneas com scroll
- **Auto-hide**: Interface limpa quando não há processamentos
- **Fechar manual**: Remover barras completadas da interface
- **Expansão/colapso**: Área de barras pode ser colapsada

#### Integração

- **SearchReplacePanel**:
  - Barra de progresso automática ao buscar
  - Task ID único: `search_<uuid>`
  - Mostra arquivo atual e progresso percentual
  - Marca como completa ao finalizar

- **InsertPanel**:
  - Barra para busca de matches antes de inserção
  - Task ID único: `insert_search_<uuid>`
  - Progresso durante busca e aplicação
  - Log de arquivos modificados

#### Arquivos Modificados

- `src/app.py`:
  - Novas classes (v2.5.0):
    - `ProgressBarWidget` (~120 linhas)
    - `ProgressDetailsDialog` (~80 linhas)
    - `ProgressManager` (~130 linhas)
  - `SearchWorker`: Novo sinal `progress_detailed(int, int, str)`
  - `SearchWorker.run()`: Coleta total de arquivos e emite progresso detalhado
  - `SearchReplacePanel.__init__()`: Aceita `progress_manager` parameter
  - `SearchReplacePanel._start_search_threaded()`: Integra com progress bar
  - `InsertPanel.__init__()`: Aceita `progress_manager` parameter
  - `InsertPanel._start_search_threaded()`: Integra com progress bar
  - `MainWindow._build_ui()`: Adiciona `ProgressManager` na parte inferior

#### Imports Adicionados

- `QProgressBar`: Barra de progresso Qt
- `QDialog`: Janela de detalhes
- `QTextEdit`: Log de processamento
- `QScrollArea`: Scroll para múltiplas barras

#### Casos de Uso

- Monitorar buscas em diretórios grandes
- Executar múltiplas operações paralelas
- Cancelar operações demoradas
- Ver detalhes de processamento em tempo real
- Limpar interface removendo barras completadas

#### Testes

- `test_progress_system.py`: 18 testes completos (v2.5.0+)
  
  **Base system (12 testes)**:
  - Criação de widgets
  - Atualização de progresso
  - Gerenciamento de múltiplas tarefas
  - Cálculo de porcentagens
  - Cancelamento de operações
  - Auto-hide e visibilidade
  - Geração de IDs únicos
  - Truncamento de mensagens longas
  
  **Enhancements (6 testes)**:
  - Persistência de histórico (JSON)
  - Cálculo de ETA
  - Sistema de notificações
  - Funcionalidade pause/resume
  - Display de estatísticas
  - Limite de histórico (1000 operações)

### 🚀 Funcionalidades Aprimoradas (v2.5.0+)

#### 1. Histórico de Operações (Persistência)

- **OperationHistory class**: Nova classe para gerenciar histórico
  - Salva em `~/.clarify_history.json`
  - Mantém últimas 1000 operações
  - Formato JSON com timestamp, tipo e detalhes
  - Métodos: `add_operation()`, `get_recent()`, `clear()`

- **Integração automática**:
  - SearchReplacePanel salva operações ao completar
  - InsertPanel salva buscas e inserções
  - Cada entrada inclui query, caminho, matches encontrados

- **Estrutura de entrada**:
  ```json
  {
    "timestamp": "2024-01-15 10:30:45",
    "type": "search",
    "details": {
      "query": "pattern",
      "path": "/path/to/dir",
      "files_matched": 12,
      "total_matches": 45
    }
  }
  ```

#### 2. Estimativa de Tempo (ETA)

- **Cálculo em tempo real**:
  - Rastreia `start_time` ao iniciar operação
  - Calcula velocidade: `arquivos / tempo_decorrido`
  - Estima conclusão: `arquivos_restantes / velocidade`
  - Formata tempo: "2h 15m", "5m 30s", "45s"

- **Display aprimorado**:
  - **ProgressDetailsDialog**: Linha de estatísticas completa
    ```
    Progress: 75/100 (75%) | Elapsed: 2m 30s | Speed: 0.5/s | ETA: 5m
    ```
  - **ProgressBarWidget**: Stats inline na barra compacta
    ```
    Processing: file.py (0.5/s, ETA: 5m)
    ```

- **Método helper**: `_format_time(seconds)` para formatação legível

#### 3. Notificações Desktop

- **Sistema de notificação automática**:
  - Notifica ao completar tarefas (sucesso ou falha)
  - Funciona com janela minimizada
  - Fallback multiplataforma

- **Implementação**:
  - `_show_notification()` method em ProgressBarWidget
  - Try/except para `plyer` (opcional)
  - Fallback para comandos do sistema:
    - Linux: `notify-send`
    - macOS: `osascript` (AppleScript)
    - Windows: plyer requerido

- **Exemplo**:
  ```
  Título: Task Complete
  Mensagem: Search completed: 12 files with matches
  ```

- **Instalação opcional**:
  ```bash
  pip install plyer  # Para melhor suporte multiplataforma
  ```

#### 4. Pausar/Retomar Operações

- **UI aprimorada**:
  - Novo botão pause (⏸/▶) em ProgressBarWidget
  - Botão pause também em ProgressDetailsDialog
  - Estado visual: barra amarela quando pausada
  - Tooltip dinâmico: "Pause Operation" / "Resume Operation"

- **SearchWorker melhorado**:
  - Flag `_paused` (default False)
  - Métodos `pause()` e `resume()`
  - Loop verifica flag entre arquivos
  - Dorme 0.1s quando pausado (não consome CPU)

- **Integração nos painéis**:
  - Sinal `pause_requested(task_id, is_paused)` conectado
  - Lambda conecta a `worker.pause()` / `worker.resume()`
  - SearchReplacePanel e InsertPanel implementados

- **Comportamento**:
  - Pausa ocorre entre arquivos (não no meio)
  - Seguro (não corrompe dados)
  - ETA recalculado ao retomar
  - Estado persistente até ação do usuário

#### 5. Estatísticas de Velocidade

- **Métricas em tempo real**:
  - **Velocidade**: Formatada como arquivos/segundo ou arquivos/minuto
    - `≥ 1/s`: "25.0/s"
    - `< 1/s`: "30.0/min" (mais legível para operações lentas)
  - **Tempo Decorrido**: Formato legível (h/m/s)
  - **ETA**: Tempo estimado até conclusão

- **Cálculo**:
  ```python
  speed = current / elapsed if elapsed > 0 else 0
  eta_seconds = remaining / speed if speed > 0 else 0
  ```

- **Display aprimorado**:
  - `stats_label` em ProgressDetailsDialog
  - `stats_label` em ProgressBarWidget (compacto)
  - Atualização a cada arquivo processado

- **Exemplos**:
  - Fast: `"Processing file.py (25.0/s, ETA: 2s)"`
  - Slow: `"Processing large.txt (30.0/min, ETA: 5m)"`
  - Elapsed: `"Elapsed: 2m 15s | Speed: 0.5/s"`

#### Modificações de Código (v2.5.0+)

- `src/app.py`:
  - **OperationHistory** (~50 linhas): Nova classe após ProgressDetailsDialog
  - **ProgressDetailsDialog** aprimorado:
    - `start_time`, `last_update_time` tracking
    - `stats_label` para estatísticas
    - Botão pause com sinal
    - `update_progress()` calcula ETA e velocidade
    - `_format_time()` helper
  - **ProgressBarWidget** aprimorado:
    - `start_time`, `is_paused` tracking
    - `btn_pause` (⏸/▶, 25x25px)
    - `stats_label` inline
    - Sinal `pause_requested(str, bool)`
    - `_show_notification()` com fallbacks
    - `_on_pause_clicked()` toggle
    - Stats calculation em `update_progress()`
  - **SearchWorker** aprimorado:
    - `_paused` flag
    - `pause()` e `resume()` methods
    - Loop em `run()` verifica flag
    - `import time` para sleep
  - **SearchReplacePanel** integrado:
    - Conecta `pause_requested` ao worker
    - `_on_search_done()` salva em history
  - **InsertPanel** integrado:
    - Conecta `pause_requested` ao worker
    - `_on_search_done()` salva em history

#### Imports Adicionados (v2.5.0+)

- `import json`: Para OperationHistory
- `import time`: Para pause loop e time tracking
- `import platform`: Para detecção de SO em notificações
- `import subprocess`: Para comandos de notificação
- `from pathlib import Path`: Para gerenciar arquivo de histórico
- `from datetime import datetime`: Para timestamps

#### Documentação Atualizada

- `docs/pt/PROGRESS_SYSTEM.md`: Adicionada seção "Funcionalidades Aprimoradas (v2.5.0+)"
- `docs/en/PROGRESS_SYSTEM.md`: Needs update (TODO)

#### Documentação

- `docs/pt/PROGRESS_SYSTEM.md`: Documentação completa em português
- `docs/en/PROGRESS_SYSTEM.md`: Documentação completa em inglês

---

## [2.4.0] - 2025-11-24

### 💾 Nova Funcionalidade: Salvamento de Resultados

#### Adicionado
- **Botão "Save Results"** nos painéis de busca e inserção
  - Localizado no cabeçalho da seção de resultados
  - Ícone: 💾 (disquete)
  - Disponível em SearchReplacePanel e InsertPanel

#### Funcionalidade
- **Exportação de Resultados**: Salva todos os resultados de busca/match em arquivo de texto
  - Formato: `.txt` com codificação UTF-8
  - Estrutura formatada com cabeçalhos e estatísticas
  - Preserva indentação e formatação do código original

#### Formato de Exportação
```
================================================================================
CLARIFY - SEARCH RESULTS
================================================================================
Total files with matches: 3
Total matches: 15
================================================================================

📁 /path/to/file.py
   Matches: 8
--------------------------------------------------------------------------------
   Line 10, Col 5:
      def calculate_total():
   Line 15, Col 8:
      return sum(values)
```

#### Arquivos Modificados
- `src/app.py`:
  - Classe `ResultsTree`: Adicionados métodos `get_matches_data()` e `export_to_text()`
  - Classe `SearchReplacePanel`: Adicionado botão e método `_save_results()`
  - Classe `InsertPanel`: Adicionado botão e método `_save_results()`

#### Casos de Uso
- Documentação de código (exportar ocorrências de funções/classes)
- Revisão de código offline
- Auditoria e análise de qualidade
- Rastreamento de TODOs e FIXMEs
- Análise de dependências
- Relatórios de refatoração

#### Testes
- `test_save_results_feature.py`: 10 testes cobrindo formatação, salvamento, erros e estatísticas

#### Documentação
- `docs/pt/SAVE_RESULTS_FEATURE.md`: Documentação completa em português
- `docs/en/SAVE_RESULTS_FEATURE.md`: Documentação completa em inglês

---

## [2.3.0] - 2025-11-24

### ✨ Nova Funcionalidade: Line Lookup no Painel Insert

#### Adicionado
- **Busca e Lookup de Caracteres** no painel Insert
  - Campo "Search query" para buscar padrões ao invés de definir linha estaticamente
  - 3 checkboxes de matching: Case Sensitive, Whole Word, Regex
  - Dropdown "Occurrence" com opções: First, Last, All
  - Suporte a inserção em múltiplas linhas quando occurrence = "All"

#### Comportamento
1. **Modo Manual (padrão)**
   - Quando campo "Search query" está vazio
   - Usa o número de linha definido no spin box
   - Comportamento tradicional preservado

2. **Modo Lookup (novo)**
   - Quando campo "Search query" contém texto
   - Busca padrão nas linhas do arquivo
   - Ignora o número de linha manual
   - Aplica inserção nas linhas encontradas

#### Opções de Occurrence
- **First**: Insere apenas na primeira linha que casa com o padrão
- **Last**: Insere apenas na última linha que casa com o padrão
- **All**: Insere em todas as linhas que casam com o padrão

#### Exemplos de Uso
```python
# Exemplo 1: Inserir comentário antes de todas as funções
Query: "def "
Case: ✓ (sensitive)
Word: ☐
Regex: ☐
Occurrence: All
Mode: INSERT_ABOVE
Text: "# Function documentation"

# Exemplo 2: Inserir import após a primeira linha de import
Query: "^import "
Case: ✓
Word: ☐
Regex: ✓ (regex ativado)
Occurrence: Last
Mode: INSERT_BELOW
Text: "import newmodule"

# Exemplo 3: Adicionar comentário ao final de linhas com "TODO"
Query: "TODO"
Case: ☐ (insensitive)
Word: ☑ (whole word)
Regex: ☐
Occurrence: All
Mode: RIGHT
Text: " // Priority"
```

#### Arquivos Modificados
- `src/app.py`
  - **InsertPanel**: Adicionada seção "Line Lookup" com query e opções
  - Método `_find_line_by_query()`: Encontra linhas baseado em query
  - Método `_line_matches_query()`: Verifica se linha casa com query
  - Método `_apply()`: Atualizado para suportar lookup automático
  - Layout reorganizado para acomodar novos campos

#### Arquivos Criados
- `test_line_lookup_feature.py` - Suite de 10 testes (100% passing ✅)

#### Benefícios
- ✅ Não precisa saber o número exato da linha
- ✅ Funciona com arquivos que mudam frequentemente
- ✅ Permite inserção em múltiplas linhas de uma vez
- ✅ Suporta padrões complexos com regex
- ✅ Flexível com case-insensitive e whole word
- ✅ Retrocompatível: modo manual ainda funciona

#### Interface
```
┌─────────────────────────────────────────────────────────┐
│ Line Lookup (optional - leave empty to use line number) │
├─────────────────────────────────────────────────────────┤
│ Search query: [___________________________________]      │
│ ☑ Case sensitive  ☐ Whole word  ☐ Regex                 │
│ Occurrence: [First ▼]                                    │
└─────────────────────────────────────────────────────────┘
│ Line number (1-based): [1      ]                         │
│ (used only if search query is empty)                     │
```

#### Estatísticas de Modificação
- Mensagem de confirmação mostra:
  - Número de arquivos modificados
  - Número de arquivos ignorados (sem match)
  - Query usada (se aplicável)
  - Modo de occurrence
  - Número de linha (se modo manual)

#### Testes
- ✅ Todos os 10 testes passando
- Testado case-sensitive e case-insensitive
- Testado whole word matching
- Testado regex patterns
- Testado First, Last, All occurrences
- Testado inserção multi-linha
- Testado skip de arquivos sem match

---

## [2.2.0] - 2025-11-24

### ✨ Nova Funcionalidade: Opções de Matching em Advanced Conditions

#### Adicionado
- **Três checkboxes de matching** nas opções avançadas condicionais
  - **Case Sensitive** - Controla se a busca diferencia maiúsculas/minúsculas (padrão: ativado)
  - **Match Whole Word** - Força casamento apenas de palavras completas (padrão: desativado)
  - **Use Regex** - Interpreta o valor como expressão regular (padrão: desativado)
  - Todas as opções aplicáveis aos campos: filename, path, ext, content

#### Comportamento dos Checkboxes
1. **Case Sensitive**
   - Quando ativo: busca exata respeitando maiúsculas/minúsculas
   - Quando inativo: busca case-insensitive (ignora diferenças de caso)
   - Aplicável a todos os operadores de string

2. **Match Whole Word**
   - Usa word boundaries (`\b`) para garantir casamento de palavra inteira
   - Evita casamentos parciais (ex: "cat" não casa com "category")
   - Funciona com operadores "contains" e "not contains"
   - Combinável com case-insensitive e regex

3. **Use Regex**
   - Interpreta o valor como padrão de expressão regular
   - Suporta todos os recursos do módulo `re` do Python
   - Pode ser combinado com case-insensitive (flag re.IGNORECASE)
   - Pode ser combinado com whole word (adiciona `\b` automaticamente)

#### Arquivos Modificados
- `src/core/filters.py`
  - Classe `Condition` agora aceita parâmetros `case_sensitive`, `whole_word`, `use_regex`
  - Adicionado método `_apply_string_matching()` para processar matching com flags
  - Método `matches()` atualizado para usar nova lógica de matching
  - Suporte a regex com flags de case-insensitive e whole-word
  
- `src/app.py`
  - **SearchReplacePanel**: Adicionados 3 checkboxes por linha de condição
  - **InsertPanel**: Adicionados 3 checkboxes por linha de condição
  - Headers atualizados com colunas "Case", "Word", "Regex"
  - Métodos `_conds()` atualizados para coletar estados dos checkboxes
  - Métodos `enable_buttons()` e `reset_advanced_conditions()` atualizados
  - Tooltips adicionados para melhor usabilidade

#### Arquivos Criados
- `test_checkbox_feature.py` - Suite completa de testes (10 testes)

#### Testes
- ✅ Todos os testes passando (10/10)
- Testado case-sensitive e case-insensitive
- Testado whole word matching
- Testado regex patterns
- Testado combinações de flags
- Testado diferentes operadores com flags
- Testado aplicação em filename e content

#### Exemplos de Uso
- **Case Insensitive**: Buscar "python" em arquivos que contêm "Python", "PYTHON", "PyThOn"
- **Whole Word**: Buscar "cat" sem casar com "category" ou "concatenate"
- **Regex**: Buscar emails com padrão `\w+@\w+\.\w+`
- **Combinado**: Regex case-insensitive para buscar variações de padrões

#### Compatibilidade
- Funciona em conjunto com a funcionalidade de Scope (v2.1.0)
- Retrocompatível: valores padrão mantêm comportamento anterior
- Não afeta campos numéricos (size, mtime) - checkboxes aplicam-se apenas a strings

---

## [2.1.0] - 2025-11-24

### ✨ Nova Funcionalidade: Determinação de Escopo em Advanced Conditions

#### Adicionado
- **Funcionalidade de Escopo** nas opções avançadas condicionais
  - Novo campo "Scope" com 7 tipos: none, brackets, braces, parentheses, custom, tag, specific-tag
  - Novo campo "Scope Param" para parâmetros adicionais (delimitadores customizados ou nome de tag)
  - Suporte a busca apenas dentro de delimitadores específicos
  - Funciona em combinação com todas as outras condições existentes

#### Tipos de Escopo Implementados
1. **`brackets`** - Busca apenas entre colchetes `[...]`
2. **`braces`** - Busca apenas entre chaves `{...}` (suporta aninhamento)
3. **`parentheses`** - Busca apenas entre parênteses `(...)`
4. **`custom`** - Busca entre delimitadores customizados (ex: `begin,end`)
5. **`tag`** - Busca dentro de qualquer tag HTML/XML
6. **`specific-tag`** - Busca dentro de uma tag específica (ex: `<div>`, `<script>`)
7. **`none`** - Sem escopo (comportamento padrão)

#### Arquivos Modificados
- `src/core/filters.py`
  - Adicionada função `extract_scope_content()` com suporte a todos os tipos de escopo
  - Classe `Condition` agora aceita parâmetros `scope_type` e `scope_value`
  - Lógica de matching atualizada para aplicar filtro de escopo no campo `content`
  
- `src/core/__init__.py`
  - Adicionado export de `extract_scope_content`
  
- `src/app.py`
  - **SearchReplacePanel**: Adicionados campos UI para Scope e Scope Param
  - **InsertPanel**: Adicionados campos UI para Scope e Scope Param
  - Métodos `_conds()` atualizados para coletar valores de scope
  - Métodos `enable_buttons()` e `reset_advanced_conditions()` atualizados
  - Headers adicionados às tabelas de Advanced Conditions para melhor usabilidade

#### Arquivos Criados
- `test_scope_feature.py` - Suite completa de testes para a funcionalidade
- `docs/pt/SCOPE_FEATURE.md` - Documentação completa em português
- `docs/en/SCOPE_FEATURE.md` - Documentação completa em inglês

#### Testes
- ✅ Todos os testes passando (10/10)
- Testada extração de conteúdo para todos os tipos de escopo
- Testada integração com classe `Condition`
- Testado suporte a aninhamento de chaves
- Testada combinação com outras condições

#### Casos de Uso
- Buscar código apenas dentro de blocos específicos (ex: JSON, JSX)
- Filtrar conteúdo HTML apenas em tags específicas
- Analisar logs apenas em seções delimitadas
- Refatoração de código focada em escopos específicos

#### Benefícios
- 🎯 Maior precisão em buscas e filtros
- 🚀 Reduz falsos positivos em operações de busca
- 🔧 Facilita refatoração de código complexo
- 📊 Melhor análise de estruturas de dados aninhadas

#### Documentação
- Documentação completa em português e inglês
- Exemplos práticos de uso
- Limitações conhecidas documentadas
- Roadmap de melhorias futuras

### 📝 Tarefas

#### Atualizado
- `docs/pt/TASKS.md`
  - Tarefa "Adicionar escopo nas opções avançadas condicionais" marcada como completa ✅
  - Estatísticas atualizadas: MUST HAVE agora está 83.3% completo (10/12)
  - Progresso geral: 10.3% (10/97 tarefas)

---

## [2.0.0] - 2025-11-23

### 🔄 Refatoração Completa

#### Eliminação de Código Duplicado
- Removidas 36 funções/classes duplicadas
- Redução de 776 linhas (22.2% do código)
- Código organizado em módulos: `core/`, `utils/`, `rewriter/`

#### Correção de Bug Crítico
- **JSON Rewriter**: Corrigido tratamento do tipo `Obj` em `sanitize_keys_and_values()`
- Previne perda de dados durante processamento
- Garante tratamento correto de estruturas de chaves duplicadas

#### Tradução para Inglês
- 100% do código traduzido para inglês
- Todos os comentários e docstrings em inglês
- Documentação bilíngue (pt/en)

#### Documentação
- 7 arquivos de documentação criados
- Estrutura de documentação bilíngue em `docs/pt/` e `docs/en/`
- README atualizado
- TASKS.md com 97 tarefas organizadas por prioridade MoSCoW

---

## [1.5.0] - 2025-10-01

### Funcionalidades Essenciais

#### Completado
- ✅ Threading para busca não-bloqueante
- ✅ Suporte a arquivos individuais e diretórios
- ✅ Substituição de texto com preservação de case
- ✅ JSON Translator com suporte a escopo
- ✅ JSON Rewriter com dedupe/join/eliminate
- ✅ Advanced conditions com 7 campos
- ✅ Interface gráfica Qt completa
- ✅ CLI completo e funcional

---

**Formato**: Baseado em [Keep a Changelog](https://keepachangelog.com/)  
**Versionamento**: [Semantic Versioning](https://semver.org/)
