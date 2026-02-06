# Plano de Integração - Funcionalidades da Pasta 'add'

**Autor**: Josué Amaral  
**Data de Criação**: 24 de Novembro de 2025  
**Última Atualização**: 24 de Novembro de 2025  
**Status**: Fase 1 Concluída ✅ | Fase 2 Em Planejamento

---

## 📋 Resumo Executivo

Este documento detalha o plano completo de integração de **5 programas Python standalone** da pasta `add/` no projeto Clarify. A análise identificou **~4500 linhas de código** com funcionalidades valiosas que resolverão **8-10 tasks** do TASKS.md.

### Programas Analisados
1. ✅ **JSON Case Converter** (885 linhas) - Conversão camel/pascal/snake/kebab
2. ✅ **Text to JSON Extractor** (1675 linhas) - Extração JSX/código para JSON
3. ✅ **JSON Search** (560 linhas) - Busca avançada com indexação
4. ✅ **Translator GUI** (449 linhas) - Substituição de placeholders `{t.key}`
5. ✅ **ChatGPT File Processor** (2065 linhas) - AI processing massivo

### Métricas de Impacto
```
📊 Código Novo:           ~3200 linhas (8 módulos)
📊 Docks Novos:           4-5 docks no MainWindow
📊 Tasks Resolvidas:      8-10 de 97 (melhora 10-12%)
📊 Tempo Estimado:        40-45 dias (6 sprints)
📊 Releases Planejadas:   v3.0 → v3.1 → v3.2 → v3.3
```

### Prioridades de Implementação
🥇 **Sprint 1** (7 dias): JSON Case Converter  
🥈 **Sprint 2** (7 dias): JSON Search  
🥉 **Sprint 3** (7 dias): Text Extractor + Análise Translator GUI  
🏅 **Sprint 4-5** (14 dias): AI File Processor  
🎖️ **Sprint 6** (5 dias): Polish & Release v3.0.0

---

## Análise Completa das Funcionalidades

### 1. JSON Case Converter ✅ (add/JSON_case_converter/)
**Arquivo**: `json_case_converter.py` (885 linhas)

**Funcionalidades**:
- Conversão de chaves JSON entre diferentes estilos de case:
  - camelCase
  - PascalCase  
  - snake_case
  - kebab-case
- Suporta múltiplos formatos de entrada:
  - JSON puro
  - Módulos TS/JS (export default, module.exports)
  - Objetos literais sem chaves externas
  - Sintaxe híbrida (chaves sem aspas, comentários, etc.)
- Parser tolerante que remove comentários
- Quote automático de chaves não quotadas
- GUI com PySide6 e CLI

**Integração Planejada**:
- Criar novo Dock: `JsonCaseConverterDock`
- Localização: `src/app.py` após `JsonRewriterDock`
- Reutilizar classe `JSObjectCaseConverter` como módulo em `src/case_converter.py`
- **RELAÇÃO COM TASKS.md**: Implementa task "Incluir possibilidade de mudar case de palavras-chave"

---

### 2. Text to JSON Extractor ✅ (add/converting text structure to JSON/)
**Arquivo**: `main.py` (1675 linhas)

**Funcionalidades**:
- **Extração de parâmetros/atributos de JSX/código**:
  - Parser JSX completo (tags abertas/fechadas/self-closing)
  - Parser genérico com delimitadores regex customizáveis
  - Extração de atributos HTML/JSX (label, className, etc.)
  - Extração de conteúdo de tags
- **Normalização de valores**:
  - Conversão de case (snake, camel, pascal, kebab)
  - Uppercase opcional
  - Limitação de caracteres com avoid-cut (palavra inteira)
- **Construção de caminhos hierárquicos**:
  - Paths baseados em estrutura de componentes
  - Opção de incluir/excluir chave e valor no path
  - Filtragem de tags HTML padrão
- **Output flexível**:
  - Lista de paths (flat)
  - JSON nested/hierárquico
  - Suporte TS/JS (chaves sem aspas)
- **Filtros avançados**:
  - Evitar chaves específicas (avoid keys com contains/equals)
  - Scope filtering (apenas dentro de tags específicas)
  - Only strings (aceitar apenas valores literais)
- GUI completa + CLI

**Integração Planejada**:
- Criar novo Dock: `TextToJsonExtractorDock`
- Localização: `src/app.py` após `JsonCaseConverterDock`
- Módulos separados:
  - `src/jsx_parser.py` - Parser JSX
  - `src/text_extractor.py` - Lógica de extração
- **RELAÇÃO COM TASKS.md**: Complementa JSON Rewriter e JSON Extractor com funcionalidades avançadas

---

### 3. Search JSON ✅ (add/searchJSON/)
**Arquivo**: `main.py` (560 linhas)

**Funcionalidades**:
- **Indexação avançada**:
  - Indexa arquivos .json, .ts, .tsx recursivamente
  - Extrai objetos top-level de TS/TSX (export const, export default)
  - Parser com suporte JSON5 (comentários, trailing commas)
  - Fallback para normalização JS→JSON
- **Sistema de busca**:
  - Queries compostas: `t.pages.testFormatDetail,hero.title`
  - Suporte a Case sensitive
  - Whole word matching
  - Regular expressions
- **Flattening de objetos**:
  - Converte objetos nested em dot-paths (`a.b.c`)
  - Mantém referência ao arquivo e linha
- **Interface**:
  - Painel "Resolved" (matches exatos)
  - Painel "Suggestions" (matches parciais)
  - Double-click para copiar path
  - Guess line number (estimativa de linha no código)
- **Target flexibility**:
  - Single file ou directory inteiro
  - Checkbox "Target is a file"
- GUI com PySide6 + reindexação on-demand

**Integração Planejada**:
- Criar novo Dock: `JsonSearchDock`
- Localização: `src/app.py` após `TextToJsonExtractorDock`
- Módulo: `src/json_search.py` com classe `ProjectIndexer`
- **RELAÇÃO COM TASKS.md**: 
  - Implementa "Possibilidade de buscar chaves e valores JSON"
  - Melhora "Busca avançada onde usuário pode buscar com múltiplas queries"

---

### 4. Translator GUI ✅ (add/translator_gui/)
**Arquivo**: `translator_gui.py` (449 linhas)

**Funcionalidades**:
- **Substituição de placeholders de tradução**:
  - Formato: `{t.pages.contact.title}` → "Contact Us"
  - Parse de dicionários TS/JS com export default
  - Parse de JSON/JSON5
  - Flatten de estrutura nested para mapping
- **Processamento**:
  - Arquivo único ou diretório recursivo
  - Scope filtering com regex (start/end delimiters)
  - Backups automáticos (.bak)
  - Worker thread (não trava GUI)
- **Safety**:
  - Dry-run preview (mostra o que seria substituído)
  - Progress logging detalhado
  - Ordenação por placeholder length (evita colisões)
- **Configuração**:
  - Root variable customizável (ex: `t`, `i18n`, `translations`)
  - Regex para delimitar regiões de substituição
- GUI com PySide6

**Integração Planejada**:
- **VERIFICAR REDUNDÂNCIA COM JSON TRANSLATE EXISTENTE**
- Se funcionalidades únicas:
  - Criar novo Dock: `PlaceholderReplacerDock`
  - Localização: `src/app.py` após `JsonSearchDock`
  - Módulo: `src/placeholder_replacer.py`
- Se redundante: extrair apenas funcionalidades ausentes
- **RELAÇÃO COM TASKS.md**:
  - Complementa "Adicionar funcionalidade de reversão de tradução JSON"
  - Pode substituir/melhorar JSON Translate existente

---

### 5. ChatGPT File Processor ✅ (add/requisite_to_ChatGPT/)
**Arquivos**: `main.py` (2065 linhas), `issue.py` (teste mínimo)

**Funcionalidades MASSIVAS**:
- **Multi-provider AI**:
  - OpenAI (ChatGPT) - 5 modelos
  - Google Gemini - 2 modelos
  - API key management com persistência
  - Verificação de chave + internet
- **File processing**:
  - Path 1 (iteração) + Path 2 (incluído em cada request)
  - File ou directory com filtro de extensões
  - Text field com modes: normal, line-by-line, send-once
  - Preview de arquivos
  - Auto-detect file/directory
- **Partitioning**:
  - Split por número de partes (N parts)
  - Split por tamanho (Bytes/KB/MB/GB)
  - Processa chunks iterativamente
- **Scope filtering**:
  - Start/End markers (plain text ou regex)
  - Whole word matching
  - Case sensitive
  - Include markers option
  - Match all ou first only
- **Output saving**:
  - Save ALL to single file (overwrite-first ou always-append)
  - Per-file saving: disabled/append/write/bak
  - Configurable suffix (.bak, etc.)
- **Token counter**:
  - Session + Lifetime statistics
  - Cost estimation por modelo
  - Chart visualizations (cost/input/output/total)
  - Persistent counter (saved to config)
  - Reset options
- **Advanced UI**:
  - Persistent tooltips com hover hysteresis
  - Menu com Provider/Model selection
  - Preferences (tooltips on/off)
  - Geometry saving
  - Interrupt request durante processamento
  - Filtered clipboard copy (remove metadata)
  - Strip code fences do output
- Worker thread + signals
- Config persistence (~/.config/chatgpt_file_processor.conf)
- Icon customizado (Base64)

**Integração Planejada**:
- **ANÁLISE DE IMPACTO**: Funcionalidade MUITO GRANDE
- **Opção 1**: Criar Dock separado `AiFileProcessorDock` (recomendado)
  - Mantém isolamento
  - Não interfere com fluxo existente
  - Usuário escolhe quando usar
- **Opção 2**: Integrar parcialmente com Smart Edit File (AI)
  - Merge com painel existente
  - Risco de complexidade excessiva
- **Módulos a criar**:
  - `src/ai_clients.py` - ChatGPTClient, GeminiClient
  - `src/ai_processor.py` - SubmissionWorker, lógica de processamento
  - `src/token_counter.py` - TokenCounterDialog, estatísticas
  - `src/persistent_tooltip.py` - Sistema de tooltips animados
- **RELAÇÃO COM TASKS.md**:
  - Implementa/melhora "Adicionar novo painel 'Smart file editing - AI'"
  - Implementa "Incluir Gemini na lista de IAs"
  - Implementa parcialmente "Query para IA sem arquivos/diretórios"

## Estratégia de Integração

### Fase 1: Análise Completa ✅ (CONCLUÍDA)
- [X] Identificar todos os arquivos Python
- [X] Ler e documentar funcionalidades de cada módulo
- [X] Identificar redundâncias com código existente
- [X] Mapear dependências e requisitos
- **Data de conclusão**: 24 de Novembro de 2025

### Fase 2: Priorização e Arquitetura (PRÓXIMA)
**Critérios de Priorização**:
1. **Impacto no TASKS.md** - Quantas tasks resolve?
2. **Complexidade** - Simples vs. Complexo
3. **Independência** - Standalone vs. Dependências
4. **Valor agregado** - Nova funcionalidade vs. Melhoria

**Ordem de Implementação**:

#### 🥇 Prioridade 1: JSON Case Converter
- **Impacto**: Resolve 1 task SHOULD HAVE
- **Complexidade**: ⭐⭐ Baixa-Média
- **Independência**: ✅ Totalmente standalone
- **LOC**: ~300 (após extração)
- **Tempo estimado**: 2-3 dias

#### 🥈 Prioridade 2: JSON Search
- **Impacto**: Resolve 2 tasks COULD HAVE
- **Complexidade**: ⭐⭐⭐ Média
- **Independência**: ✅ Standalone
- **LOC**: ~400
- **Tempo estimado**: 3-4 dias

#### 🥉 Prioridade 3: Text to JSON Extractor
- **Impacto**: Complementa JSON Rewriter/Extractor
- **Complexidade**: ⭐⭐⭐⭐ Alta
- **Independência**: ⚠️ Pode conflitar com JSON Rewriter
- **LOC**: ~800 (split em múltiplos módulos)
- **Tempo estimado**: 5-7 dias

#### 🏅 Prioridade 4: Translator GUI
- **Impacto**: Pode ser redundante com JSON Translate
- **Complexidade**: ⭐⭐ Baixa-Média
- **Independência**: ⚠️ Analisar overlap com JSON Translate
- **LOC**: ~200 (funcionalidades únicas)
- **Tempo estimado**: 2-3 dias
- **Decisão**: Análise de redundância primeiro

#### 🎖️ Prioridade 5: ChatGPT File Processor
- **Impacto**: Resolve 3+ tasks COULD HAVE
- **Complexidade**: ⭐⭐⭐⭐⭐ Muito Alta
- **Independência**: ✅ Standalone mas MASSIVO
- **LOC**: ~1500+ (6+ módulos)
- **Tempo estimado**: 10-15 dias
- **Decisão**: Implementar como Dock separado

### Fase 3: Modularização (Por Prioridade)

#### Módulo 1: Case Converter
```
src/
├── case_converter.py        # JSObjectCaseConverter class
│   ├── to_camel()
│   ├── to_pascal()
│   ├── to_snake()
│   ├── to_kebab()
│   ├── parse_any()          # JSON/TS/JS parser
│   └── quote_unquoted_keys()
```

#### Módulo 2: JSON Search
```
src/
├── json_search/
│   ├── __init__.py
│   ├── indexer.py           # ProjectIndexer
│   ├── flattener.py         # flatten_object()
│   ├── query_parser.py      # parse_composite_query()
│   └── ts_extractor.py      # extract_top_level_objects_from_ts()
```

#### Módulo 3: Text Extractor
```
src/
├── text_extractor/
│   ├── __init__.py
│   ├── jsx_parser.py        # JSXParser class
│   ├── generic_parser.py    # GenericScopeParser
│   ├── extractor.py         # Extractor orchestrator
│   └── normalizer.py        # normalize_token(), case styles
```

#### Módulo 4: Placeholder Replacer (se não redundante)
```
src/
├── placeholder_replacer.py  # Functions for {t.key.path} → value
│   ├── parse_dictionary_file()
│   ├── flatten_dict()
│   ├── build_placeholder_map()
│   └── scoped_replace()
```

#### Módulo 5: AI File Processor
```
src/
├── ai/
│   ├── __init__.py
│   ├── clients.py           # ChatGPTClient, GeminiClient
│   ├── processor.py         # SubmissionWorker
│   ├── token_counter.py     # TokenCounterDialog, stats
│   ├── persistent_tooltip.py # AnimatedTooltip system
│   └── utils.py             # count_tokens(), slice_bytes_*()
```

### Fase 4: Integração GUI (Por Prioridade)

#### 4.1: JSON Case Converter Dock
```python
# src/app.py - após JsonRewriterDock (linha ~3400)

class JsonCaseConverterDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("JSON Case Converter", parent)
        # Input: file/directory selector
        # Options: target case (camel/pascal/snake/kebab)
        # Checkbox: Quote unquoted keys
        # Output: converted JSON/TS
        # Button: Convert
```

**Menu Integration**:
```python
# Tools → JSON Case Converter
act_case_converter = QAction("Case Converter", self)
act_case_converter.triggered.connect(self.show_case_converter_dock)
tools_menu.addAction(act_case_converter)
```

#### 4.2: JSON Search Dock
```python
# src/app.py - após JsonCaseConverterDock

class JsonSearchDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("JSON Search", parent)
        # Input: target (file/directory)
        # Query: composite query (t.pages.X,Y.Z)
        # Options: Case/Whole/Regex
        # Results: Resolved panel + Suggestions panel
        # Button: Reindex, Search
```

#### 4.3: Text Extractor Dock
```python
# src/app.py - após JsonSearchDock

class TextToJsonExtractorDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Text to JSON Extractor", parent)
        # Mode: JSX / Generic (regex delimiters)
        # Parameter: attribute/tag name
        # Options: include key/value, drop standard tags
        # Normalization: case, limit, avoid-cut
        # Output: paths + JSON
```

#### 4.4: AI File Processor Dock
```python
# src/app.py - após TextToJsonExtractorDock

class AiFileProcessorDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("AI File Processor", parent)
        # Provider: OpenAI / Gemini
        # Model: dropdown
        # Paths: Path 1 (iterate) + Path 2 (include)
        # Text: multiline with modes
        # Partitioning: enabled/disabled, mode, size
        # Scope filter: start/end markers
        # Output saving: single file / per-file
        # Token counter: session + lifetime
```

### Fase 5: Testes

#### 5.1: Testes Unitários
```
tests/
├── test_case_converter.py       # 8 tests (4 cases × 2 inputs)
├── test_json_search.py          # 12 tests (query types, filters)
├── test_text_extractor.py       # 15 tests (JSX + generic modes)
├── test_placeholder_replacer.py # 6 tests (if not redundant)
└── test_ai_processor.py         # 20+ tests (multi-provider, partitioning)
```

#### 5.2: Testes de Integração GUI
```
tests/integration/
├── test_docks_visibility.py     # Show/hide docks
├── test_menu_actions.py         # Menu triggers
└── test_progress_integration.py # Progress bars with new features
```

### Fase 6: Documentação

#### 6.1: Por Funcionalidade
- `docs/en/CASE_CONVERTER.md`
- `docs/pt/CASE_CONVERTER.md`
- `docs/en/JSON_SEARCH.md`
- `docs/pt/JSON_SEARCH.md`
- `docs/en/TEXT_EXTRACTOR.md`
- `docs/pt/TEXT_EXTRACTOR.md`
- `docs/en/AI_PROCESSOR.md`
- `docs/pt/AI_PROCESSOR.md`

#### 6.2: Atualizações Globais
- `README.md` - Adicionar seção "New Features v3.0"
- `CHANGELOG.md` - Criar entrada v3.0.0
- `TASKS.md` - Marcar tasks concluídas
- `docs/project_structure.txt` - Atualizar com novos módulos

## Próximos Passos Imediatos

### Step 1: JSON Case Converter (Dias 1-3)
1. ✅ Análise completa do código (**FEITO**)
2. [ ] Extrair classe `JSObjectCaseConverter` para `src/case_converter.py`
3. [ ] Criar `JsonCaseConverterDock` em `src/app.py`
4. [ ] Integrar menu Tools → Case Converter
5. [ ] Criar 8 testes unitários
6. [ ] Documentar em PT/EN
7. [ ] Marcar task "Incluir possibilidade de mudar case" como concluída

### Step 2: JSON Search (Dias 4-7)
1. [ ] Criar estrutura `src/json_search/`
2. [ ] Modularizar componentes (indexer, flattener, query, ts_extractor)
3. [ ] Criar `JsonSearchDock` em `src/app.py`
4. [ ] Integrar menu Tools → JSON Search
5. [ ] Criar 12 testes unitários
6. [ ] Documentar em PT/EN
7. [ ] Marcar task "Possibilidade de buscar chaves e valores JSON"

### Step 3: Análise de Redundância - Translator GUI (Dia 8)
1. [ ] Comparar funcionalidades com JSON Translate existente
2. [ ] Identificar features únicas do Translator GUI
3. [ ] Decisão: Integrar parcialmente OU criar dock separado
4. [ ] Documentar decisão arquitetural

### Step 4: Text Extractor (Dias 9-15)
1. [ ] Criar estrutura `src/text_extractor/`
2. [ ] Modularizar JSXParser + GenericParser + Extractor
3. [ ] Criar `TextToJsonExtractorDock` com GUI complexa
4. [ ] Integrar com JSON Rewriter (verificar conflitos)
5. [ ] Criar 15 testes unitários
6. [ ] Documentar em PT/EN

### Step 5: AI File Processor (Dias 16-30)
1. [ ] Criar estrutura `src/ai/` com 6 módulos
2. [ ] Implementar clients (OpenAI + Gemini)
3. [ ] Implementar partitioning + scope filtering
4. [ ] Criar sistema de persistent tooltips
5. [ ] Criar TokenCounterDialog com charts
6. [ ] Criar `AiFileProcessorDock` com GUI massiva
7. [ ] Integrar config persistence
8. [ ] Criar 20+ testes unitários
9. [ ] Documentar extensivamente em PT/EN
10. [ ] Marcar 3+ tasks de IA como concluídas

## Notas Importantes

- Não importar código da pasta `add/` diretamente
- Extrair e modularizar cada funcionalidade
- Manter consistência com arquitetura existente do Clarify
- Usar PySide6 para todas as GUIs
- Integrar com sistema de threads existente
- Seguir padrões de código do Clarify

## Considerações Técnicas

### Compatibilidade de Dependências

**Já Disponíveis no Clarify**:
- ✅ PySide6 (GUI framework)
- ✅ json (stdlib)
- ✅ re (stdlib)
- ✅ pathlib (stdlib)
- ✅ QThread, QTimer, Signal (threading/async)

**Novas Dependências Necessárias**:
```python
# requirements.txt additions
json5>=0.9.10           # Para JSON Search (parser TS/JS tolerante)
openai>=1.0.0           # Para AI Processor (ChatGPT)
google-generativeai     # Para AI Processor (Gemini)
tiktoken>=0.5.0         # Para token counting (AI)
plyer                   # Para desktop notifications (opcional)
```

### Conflitos Potenciais e Mitigações

#### 1. JSON Rewriter vs. Text Extractor
**Problema**: Ambos manipulam estruturas JSON/TS  
**Mitigação**: 
- Text Extractor foca em **extração** (input: código → output: JSON)
- JSON Rewriter foca em **transformação** (input: JSON → output: JSON reescrito)
- Namespaces separados, sem overlap de lógica

#### 2. JSON Translate vs. Translator GUI
**Problema**: Funcionalidades overlapping  
**Análise Detalhada Necessária**:
- JSON Translate: cria placeholders `{t.key.path}` e dicionário
- Translator GUI: substitui placeholders `{t.key.path}` → valores traduzidos
- **Conclusão**: São complementares! Um cria, outro substitui
- **Ação**: Manter ambos, documentar workflow bidirecional

#### 3. Multiple Search Systems
**Problema**: Search/Replace, JSON Search, Text Extractor têm busca  
**Mitigação**:
- Search/Replace: busca em **arquivos de texto** (genérico)
- JSON Search: busca em **estruturas JSON indexadas** (dot-paths)
- Text Extractor: **não é busca**, é extração de estrutura
- Propósitos diferentes, coexistem naturalmente

### Estimativas de Impacto

#### Tamanho do Código
```
src/app.py atual:           3765 linhas
+ Case Converter Dock:      +150 linhas
+ JSON Search Dock:         +200 linhas
+ Text Extractor Dock:      +300 linhas
+ AI Processor Dock:        +500 linhas
= Total src/app.py:         ~4915 linhas

Novos módulos:
src/case_converter.py:       300 linhas
src/json_search/*:           400 linhas (4 arquivos)
src/text_extractor/*:        800 linhas (4 arquivos)
src/placeholder_replacer.py: 200 linhas (se mantido)
src/ai/*:                   1500 linhas (6 arquivos)
= Total novo código:        ~3200 linhas

TOTAL PROJETO v3.0:         ~8000+ linhas (vs. 3765 atual)
```

#### Tasks Resolvidas
```
SHOULD HAVE:
✅ Mudar case de palavras-chave            (Case Converter)
✅ Possibilidade de buscar chaves JSON     (JSON Search)
✅ Salvamento em arquivo único/separado    (AI Processor)

COULD HAVE:
✅ Smart file editing - AI                 (AI Processor)
✅ Incluir Gemini na lista de IAs          (AI Processor)
✅ Query para IA sem arquivos              (AI Processor parcial)
✅ Busca avançada JSON                     (JSON Search)

WOULD HAVE:
✅ Tooltips na aplicação                   (AI Processor - sistema reutilizável)

Total: ~8-10 tasks marcadas como concluídas
Novo progresso: 26-28/97 tasks (27-29%)
```

#### Performance
```
Impacto na inicialização:
+ Case Converter:        ~10ms (parser on-demand)
+ JSON Search:           ~50ms (indexação lazy)
+ Text Extractor:        ~20ms (parsers on-demand)
+ AI Processor:          ~30ms (clients não inicializados)
= Overhead total:        ~110ms (aceitável)

Uso de memória:
+ Case Converter:        ~2MB (classes)
+ JSON Search:           ~10MB (índice em memória para projeto médio)
+ Text Extractor:        ~5MB (parsers + cache)
+ AI Processor:          ~15MB (stats + history + tooltips)
= Total adicional:       ~32MB (aceitável para app desktop)
```

### Riscos e Contingências

#### Risco 1: Complexidade do AI Processor
**Probabilidade**: Alta  
**Impacto**: Alto  
**Mitigação**:
- Implementar em fases incrementais
- Começar com OpenAI only, adicionar Gemini depois
- Partitioning pode ser feature v3.1 (não v3.0)
- Tooltips persistentes podem ser feature separada

#### Risco 2: Tempo de Desenvolvimento
**Estimativa original**: 30 dias  
**Estimativa realista**: 40-45 dias (incluindo testes e docs)  
**Mitigação**:
- Implementar prioridades 1-2 primeiro (Case + Search)
- Release incremental: v3.0.0, v3.1.0, v3.2.0
- Não bloquear releases por funcionalidades de baixa prioridade

#### Risco 3: Quebra de Compatibilidade
**Probabilidade**: Baixa  
**Impacto**: Alto se ocorrer  
**Mitigação**:
- Todas as novas features são **adições**, não modificações
- Docks são opcionais (show/hide)
- Config files separados (~/.clarify_*, não sobrescreve)
- Testes de regressão antes de cada commit

## Cronograma Proposto

### Sprint 1 (Dias 1-7): Foundation
- ✅ Dia 1-2: Análise completa (**FEITO**)
- [ ] Dia 3-4: JSON Case Converter (implementação + testes)
- [ ] Dia 5-7: JSON Case Converter (integração GUI + docs)

### Sprint 2 (Dias 8-14): Search
- [ ] Dia 8-10: JSON Search (modularização + core logic)
- [ ] Dia 11-12: JSON Search (integração GUI)
- [ ] Dia 13-14: JSON Search (testes + docs)

### Sprint 3 (Dias 15-21): Extractor
- [ ] Dia 15: Análise de redundância Translator GUI
- [ ] Dia 16-18: Text Extractor (parsers + extractor core)
- [ ] Dia 19-20: Text Extractor (GUI complexa)
- [ ] Dia 21: Text Extractor (testes básicos + docs)

### Sprint 4-5 (Dias 22-35): AI Processor
- [ ] Dia 22-24: AI clients (OpenAI + Gemini)
- [ ] Dia 25-27: Core processor (worker + partitioning)
- [ ] Dia 28-29: Token counter + stats
- [ ] Dia 30-31: Persistent tooltips system
- [ ] Dia 32-33: GUI integration massiva
- [ ] Dia 34-35: Testes extensivos

### Sprint 6 (Dias 36-40): Polish & Release
- [ ] Dia 36-37: Testes de integração completos
- [ ] Dia 38-39: Documentação final (README, CHANGELOG)
- [ ] Dia 40: Release v3.0.0

### Releases Incrementais Planejadas
```
v3.0.0 (Sprint 1-2):  Case Converter + JSON Search
v3.1.0 (Sprint 3):    Text Extractor
v3.2.0 (Sprint 4-5):  AI Processor (OpenAI only)
v3.3.0 (Post):        AI Processor (Gemini + features avançadas)
```

## Status Atual

**Progresso Geral**: 20% (Análise completa de 5/5 módulos ✅)  
**Fase Atual**: Fase 1 concluída, Fase 2 planejada  
**Próxima Ação**: Iniciar implementação - JSON Case Converter (Sprint 1)  
**Data de Análise**: 24 de Novembro de 2025  
**Estimativa Release v3.0.0**: ~10 de Janeiro de 2026 (45 dias úteis)
