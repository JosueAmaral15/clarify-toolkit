# Clarify - Programming Tasks

**Author**: Josué Amaral  
**Date**: 2025/10/01  
**Last Update**: 2025/11/24

Este documento contém todas as tarefas de desenvolvimento do Clarify organizadas por prioridade usando o método MoSCoW (Must Have, Should Have, Could Have, Would Have).

---

## 📊 Legenda

- `[X]` - Tarefa completada
- `[]` - Tarefa pendente
- **MUST HAVE** - Funcionalidades críticas/essenciais
- **SHOULD HAVE** - Funcionalidades importantes mas não críticas
- **COULD HAVE** - Funcionalidades desejáveis se houver tempo
- **WOULD HAVE LATER** - Funcionalidades futuras de longo prazo

---

## 🔴 MUST HAVE (Alta Prioridade)

### ✅ Tasks Concluídas

- **[X]** Implementar threads para busca de arquivos
- **[X]** Incluir arquivos individuais e não apenas diretórios
- **[X]** Substituir texto do dropdown relativo ao painel de inserção
- **[X]** Resolver o erro: `json.decoder.JSONDecodeError: Expecting ':' delimiter: line 4629 column 21 (char 185171)`
- **[X]** Evitar override: impedir que JSON Translate sobrescreva nomes de traduções (ex: `{t.pages.Prac{t.pages.Navbar.blog}HistoryPage.blank}`)
- **[X]** Ajustar JSON Translate para traduzir apenas em escopo de código (ex: `children: React.ReactNode` não deve ser traduzido)
- **[X]** Nome da variável do primeiro objeto: permitir customização do nome root (ex: `t`, `i18n`, `translations`)
- **[X]** Adicionar possibilidade de usar expressões regulares em substituições para não substituir certos caracteres
- **[X]** **[CRÍTICO]** Corrigir problema sério no JSON Rewriter onde alguns dados são perdidos durante processamento, omitindo chaves e valores

### ✅ Tasks Concluídas

- **[X]** Adicionar determinação de escopo nas opções avançadas condicionais com múltiplas opções:
  - ✅ Apenas entre colchetes `[...]`
  - ✅ Apenas entre chaves `{...}`
  - ✅ Apenas entre parênteses `(...)`
  - ✅ Apenas entre delimitadores customizados (ex: `begin...end`)
  - ✅ Apenas entre tags HTML/XML (ex: `<div>...</div>`)
  - ✅ Apenas dentro de uma tag específica (ex: apenas dentro de `<script>`)
  - ✅ Implementado como opção em Advanced Conditions com campos Scope e Scope Param
  - ✅ Funciona em combinação com outras condições (filename, path, ext, size, mtime, content)
  - ✅ Suporta busca em múltiplos níveis de aninhamento
  - **Data de conclusão**: 24 de Novembro de 2025

### 🔨 Tasks Pendentes

- **[X]** Durante tradução JSON, preservar uppercase com parâmetro do usuário **(v2.9.8)**

---

## 🟡 SHOULD HAVE (Prioridade Média)

### ✅ Tasks Concluídas

- **[x]** Incluir 3 opções de checkbox nas opções avançadas condicionais: case sensitive, match whole word e regular expression *(v2.2.0)*
- **[x]** Incluir possibilidade de busca e lookup de caracteres no painel Insert para inserir caracteres com busca ao invés de somente definir número da linha, estaticamente *(v2.3.0)*
- **[x]** Incluir salvamento de todos os resultados do match panel como arquivo txt *(v2.4.0)*
- **[x]** Incluir barra de progresso para mostrar progresso do processamento *(v2.5.0)*

### 🔨 Tasks Pendentes

#### Interface e Usabilidade
- **[X]** Adicionar funcionalidade de reversão de tradução JSON (Swap Dictionaries + Undo with Backup) **(v2.9.8)**
- **[X]** Adicionar menu com botão direito no painel de matches: copy, copy all, select all, open file, open all files. Suportar CTRL/Shift para seleção múltipla *(v2.9.2 - Context Menu)*
- **[X]** Possibilidade de colocar resultados em arquivos separados (cada iteração) ou em arquivo único **(v2.9.7 - Save Results)**
- **[X]** Habilidade de inserir ranges incluídos/excluídos no Insert, mesmo usando regex **(v2.9.9 - Hierarchical Ranges)**
- **[X]** Corrigir mensagem de Loading (só aparece letra L)
- **[X]** Mostrar quantidade de resultados na primeira linha do match panel
- **[X]** Mostrar posição absoluta do caractere/palavra ao passar mouse sobre resultado no match panel
- **[X]** Adicionar busca por nome de arquivo com suporte a wildcards, prefix e regex **(v2.9.7 - Filename Search)**

#### UX/UI Improvements (v2.9.13)

- **[X]** Adicionar menu de contexto na tabela File List com "Open in File Manager" (multi-select) **(v2.9.13 - Task #40)**
- **[X]** Adicionar tooltip preview em Advanced Search mostrando primeiras 3 linhas (max 200 chars) **(v2.9.13 - Task #41)**
- **[X]** Salvar preferências dos checkboxes e últimos 10 diretórios com QSettings **(v2.9.13 - Task #42)**
- **[X]** Adicionar label de estatísticas em JSON Translate mostrando contagem de arquivos/traduções **(v2.9.13 - Task #43)**

#### JSON Features

- **[X]** Incluir possibilidade de mudar case de palavras-chave (camelCase, PascalCase, snake_case, kebab-case) *(v3.0.0 - Case Converter)*
- **[X]** Incluir checkbox "is file" no JSON translate
- **[X]** Ajustar opção 'Emit Export default' do JSON Translate **(v2.9.7)**
- **[X]** Resultado do JSON Translate não deve conter três barras invertidas (`\\\`) **(v2.9.7 - Fix Backslash Escaping)**
- **[X]** Evitar valores vazios no output do JSON Extractor **(v2.9.6)**
- **[X]** Incluir 'avoid childs keys with the same name' no output do JSON Extractor **(v2.9.7 - Avoid Duplicate Child Keys)**
- **[X]** Adicionar opção 'not include number keys' no JSON Extractor **(v2.9.6)**
- **[X]** Ordenar todos os resultados, incluindo output do JSON Rewriter **(v2.9.5 - Parcial: implementado para SearchReplacePanel e InsertPanel)**
- **[X]** Corrigir issue de case onde output tem chaves com pascal-case ou camel-case inconsistente **(v2.9.9 - Case Validator Dialog)**  ```
- **[X]** Evitar chaves repetidas em arrays (remove duplicados consecutivos e totais) **(v2.9.8)**
  ```javascript
  whyItSWrong: ['Why it\'s wrong:', 'Why it\'s wrong:'] → ['Why it\'s wrong:']
  ```
- **[X]** Adicionar feature para substituir listas por objetos/dicionários em arquivos JSON com restrições de escopo (ex: apenas em `t.pages`) **(v2.9.10 - Task #21)**
- **[X]** Normalizar escaping excessivo automaticamente (detectar `\\\\'` ou mais → `\\'`) **(v2.9.10 - Task #22)**
- **[X]** Converter arrays para objetos com geração inteligente de chaves (camelCase, primeiras 30 chars, remove acentos) **(v2.9.10 - Task #21)**
- **[X]** Atualizar referências órfãs em arquivos do projeto após eliminação de duplicatas **(v2.9.14 - Task #23 COMPLETO)**
  - **SOLUÇÃO IMPLEMENTADA**: Sistema completo com VALUE EQUALITY (não string similarity)
  - **FUNÇÕES**: `extract_all_keys_from_obj()` (suporta tipo Obj) + `build_substitution_map_by_value()` (compara valores idênticos)
  - **REGRAS APLICADAS**: Linha menor vence, mesmo parent path prioritário, não mexa se valores diferentes
  - **TESTES**: 12 unit tests (100% passing) - `tests/test_reference_updater.py`
  - **DOCUMENTAÇÃO**: `docs/TASK_23_ORPHANED_KEYS_SPECIFICATION.md` (662 linhas)
- **[X]** Incluir possibilidade de filtrar extensões (ex: `.jsx`) em todos os módulos e funcionalidades *(v2.9.0 - Extension Filter)*;
- **[X]** Resolver issue de tradução quando texto tem parênteses (ex: `'Multiple Choice (Multiple)'`) **(v2.9.9 - Parentheses Support)**
- **[X]** Forçar aplicação e JSON translate a obedecer regras de sintaxe e case (enforce consistent case) **(v2.9.8)**
- **[X]** Incluir whole word, case sensitive e regex nas condições avançadas *(v2.2.0 - Implementado em Search/Replace e Insert panels)*
- **[X]** Adicionar tipo de filtro nas condições avançadas: operadores AND e OR *(v2.6.0 - Dropdown com AND/OR em ambos panels)*

#### System Features

- **[X]** Adicionar classe de modal screen para mostrar loading sem travar tela, permitindo minimizar/maximizar modal, continuar navegando e fazer processamento paralelo (com threads), mas sem permitir processar mesma feature simultaneamente *(v2.7.0 - ThreadManager + ProcessingModal)*
- **[X]** Corrigir reversão de JSON translate: fazer reverso de tradução (objeto para texto) com checkbox "Reverse JSON Translate" + botões "Swap Dictionaries" e "Undo with Backup" **(v2.9.8 - Task #10)**
- **[X]** Adicionar feature para interromper processamento: botão Cancel em ProcessingModal com ThreadManager.cancel_thread() e interrupt_check callbacks **(v2.7.0 + v3.0.0 - ThreadManager + AI Interrupt)**
- **[X]** Incluir possibilidade de listar arquivos com parâmetros ls/dir: FileListDock com -a, -l, -h, -R e busca avançada **(v2.9.11 - Task #33 + v2.9.11 - Task #36)**
- **[X]** Inserção de arquivos e diretórios de forma assíncrona e selecionável: ThreadManager com processamento paralelo por arquivo e feature **(v2.7.0 - ThreadManager)**
- **[X]** Incluir query para inteligência artificial sem arquivos/diretórios, apenas com texto do usuário *(v3.0.0 - AI File Processor)*
- **[X]** Identificar tags, chaves curvas, colchetes e parênteses para evitar erros no JSON Rewriter e uso de editor de texto ros ls/dir com ferramentas de busca avançadas
- **[X]** Incluir query para inteligência artificial sem arquivos/diretórios, apenas com texto do usuário *(v3.0.0 - AI File Processor)*
- **[X]** Identificar tags, chaves curvas, colchetes e parênteses para evitar erros no JSON Rewriter e uso de editor de texto *(v3.0.0 - Text Extractor)*
- **[X]** Incluir busca avançada onde usuário pode buscar com múltiplas queries separadas por novas linhas com possibilidade de usar regex (cada linha = nova query de busca) *(v2.8.0 - Multi-Query Search)*
- **[X]** Remover erros ` ```typescript` e ` ``` ` no output ao usar IA query *(v3.0.0 - AI File Processor com strip_code_fences)*
- **[X]** Incluir busca onde word key tem contagem de ocorrências (Top 5 files/keys, total count) **(v2.9.8)**
- **[X]** Interrupt Request no ChatGPT File Processor não funciona. Resolver issue *(v3.0.0 - AI File Processor com worker.request_interrupt())*
- **[X]** Skip keys without siblings: remover hierarquias seriais (cadeias) onde chaves não têm siblings **(v2.9.11 - Task #35)**
  - Remove estruturas como `{a: {b: {c: "val"}}}` (cadeia serial)
  - Mantém estruturas com siblings como `{a: {b: "v1", c: "v2"}}`
  - 7 testes unitários (100% passing)
- **[X]** Advanced File/Directory Search: busca avançada com múltiplos filtros **(v2.9.11 - Task #36)**
  - Filtros: filename regex, tamanho (MB), data modificação, tipo (file/dir/any)
  - Busca recursiva opcional
  - Exibição em tabela sortable
  - Exportação para CSV
- **[X]** File List com parâmetros ls/dir: listar arquivos com parâmetros Unix-like **(v2.9.11 - Task #33)**
  - Parâmetros: -a (show hidden), -l (long format), -h (human-readable), -R (recursive)
  - Exibe: Name, Size, Modified, Permissions (drwxr-xr-x), Owner:Group
  - Tabela sortable com exportação CSV
- **[X]** Keyboard shortcut para Advanced File Search: Ctrl+Shift+F **(v2.9.12 - Task #37)**
- **[X]** Quick filter no File List: filtro rápido por filename sem re-executar busca **(v2.9.12 - Task #39)**

---

## 🟢 COULD HAVE (Prioridade Baixa)

### ✅ Tasks Concluídas

#### Task #6 - Open in Editor from Results (v2.9.19)
**Status**: ✅ Completa - 30/11/2025  
**Arquivos Modificados**: `src/gui/base_dock.py`, 5 dock files  
**Arquivo de Teste**: `tests/test_open_in_editor.py` (24 testes - 100% passing)

**Objetivo**: Permitir reutilizar resultados de operações abrindo-os diretamente no editor integrado em modo sandbox (edit-only), facilitando análise, modificação e exportação de outputs.

**Componentes Implementados**:

1. ✅ **ResultsOutputMixin Enhancement** (`src/gui/base_dock.py` - 150+ linhas):
   - Context Menu no QTextEdit (right-click):
     * **📝 Open in Editor**: Abre conteúdo em edit-only mode
     * Copy / Select All (ações padrão)
   - Methods adicionados:
     * `_show_results_context_menu(text_edit, pos)`: Exibe menu contextual
     * `_open_results_in_editor(text_edit)`: Cria temp file + abre no EditorDock
     * `_detect_content_extension(content)`: Auto-detect formato (JSON/HTML/TS/PY/TXT)
     * `_get_editor_dock()`: Encontra EditorDock via parent traversal
     * `add_open_in_editor_button(text_edit, layout, text)`: Helper para criar toolbar button

2. ✅ **Auto-Detection de Extensão** (Smart Format Recognition):
   - **JSON**: Detecta `{` ou `[` + valida com `json.loads()`
   - **HTML**: Detecta `<html`, `<div`, `<span`, `<body>` tags
   - **XML**: Detecta `<root>` ou tags XML genéricas
   - **TypeScript**: Detecta `const`, `let`, `function`, `=>`
   - **Python**: Detecta `def`, `import`, `class`, `from`
   - **Fallback**: `.txt` para conteúdo não reconhecido

3. ✅ **Integration em 5 Docks** (Toolbar Button + Context Menu):
   - ✅ `json_search_dock.py`: Busca de chaves/valores JSON
   - ✅ `text_extractor_dock.py`: Extração de texto HTML/JSX
   - ✅ `case_converter_dock.py`: Conversão de case
   - ✅ `ai_processor_dock.py`: Respostas de IA (OpenAI/Gemini)
   - ✅ `placeholder_replacer_dock.py`: Substituição de placeholders

4. ✅ **Workflow Completo**:
   - **Passo 1**: Usuário executa operação (busca, extração, AI processing)
   - **Passo 2**: Resultados aparecem em `QTextEdit` read-only
   - **Passo 3**: Usuário clica em "📝 Open in Editor" button OU right-click → "Open in Editor"
   - **Passo 4**: Sistema auto-detecta formato (JSON/HTML/TXT/etc)
   - **Passo 5**: Cria arquivo temporário com extensão correta
   - **Passo 6**: Abre no EditorDock em **edit-only mode** (sandbox)
   - **Passo 7**: Usuário pode:
     * 📋 Copiar para clipboard
     * 💾 Exportar para arquivo
     * 🔓 Enable Saving (converter para file-backed)
     * ✏️ Editar livremente sem afetar arquivos originais

**Padrões de Projeto**:
- **Template Method**: `_open_results_in_editor()` define algoritmo
- **Strategy Pattern**: `_detect_content_extension()` seleciona estratégia de formato
- **Chain of Responsibility**: Parent traversal em `_get_editor_dock()`
- **Factory Pattern**: Criação de temp files com extensões dinâmicas
- **Observer**: Context menu signal/slot connection

**Testes** (`tests/test_open_in_editor.py` - 350 linhas):
- ✅ 2 testes de criação de results panel
- ✅ 2 testes de botão "Open in Editor"
- ✅ 7 testes de auto-detection (JSON/HTML/XML/TS/PY/TXT/invalid)
- ✅ 5 testes de integração EditorDock (empty, temp file, edit-only, error handling)
- ✅ 2 testes de _get_editor_dock()
- ✅ 2 testes de context menu integration
- ✅ 3 testes de múltiplos formatos (JSON/HTML/plain text)
- **Total**: 24/24 passing (100%)

**Benefícios**:
- 🎯 **Reusabilidade**: Resultados podem ser editados, salvos, ou integrados em workflows
- 🔒 **Segurança**: Edit-only mode previne modificações acidentais de arquivos
- 🎨 **UX**: Transição fluida entre result panels e editor
- 🧠 **Smart**: Auto-detection de formato para syntax highlighting correto
- ♻️ **DRY**: Código centralizado em `ResultsOutputMixin` reutilizado por 5 docks

**Integração com Task #5** (Edit-Only Mode):
- Usa `EditorDock.open_file_path(temp_path, edit_only=True)` criado em v2.9.18
- Aproveita visual indicators (🔒 icon, orange status, golden border)
- Herda toolbar buttons (Copy, Export, Enable Saving)
- Integração perfeita com close behavior customizado

---

#### Task #14 - Remove Chaves sem Siblings (v2.9.20)
**Status**: ✅ Completa - 30/11/2025 (Já implementada como Task #35 em v2.9.11)

**Objetivo**: Incluir possibilidade de remover chaves que não têm sibling key (chaves órfãs em hierarquias seriais).

**Conclusão**: Esta task foi **DUPLICADA** com Task #35 que foi implementada em v2.9.11. A funcionalidade já existe e está funcional:

1. ✅ **Função Backend**: `skip_keys_without_siblings(node)` em `src/rewriter/operations.py`
   - Remove hierarquias seriais (cadeias) onde cada nível tem apenas um filho
   - Exemplo: `{a: {b: {c: "value"}}}` → `{}` (serial chain removida)
   - Exemplo: `{a: {b: "val1", c: "val2"}}` → mantida (b e c são siblings)

2. ✅ **UI Checkbox**: `chk_skip_no_siblings` em `JsonRewriterDock`
   - Label: "Skip keys without siblings"
   - Tooltip: "Remove serial hierarchies (chains) where keys don't have siblings (Task #35)"
   - Localização: Row 4, Column 4 no grid layout

3. ✅ **Integração Backend**: 
   - `cli_dedupe()` verifica flag `args.skip_no_siblings`
   - Chama `rw.skip_keys_without_siblings(obj)` quando habilitado

**Referência**: Ver Task #35 (v2.9.11) na seção SHOULD HAVE para detalhes completos da implementação.

**Impacto**: Task #14 pode ser marcada como completa sem necessidade de código adicional.

---

#### Task #44 - Análise de Funcionalidades em `add/` (v2.9.15)
**Status**: ✅ Completa - 24/11/2025

**Objetivo**: Analisar diretório `add/` para identificar funcionalidades pendentes e implementar 2-3 mais simples.

**Resultado**: Todas as 5 funcionalidades do diretório `add/` já foram implementadas no Clarify v3.0.0 (24/11/2025):
1. ✅ JSON Case Converter → `src/case_converter.py` + `CaseConverterDock`
2. ✅ JSON Search → `src/json_search/` + `JsonSearchDock`
3. ✅ Translation Placeholder Replacer → `src/placeholder_replacer.py` + `PlaceholderReplacerDock`
4. ✅ Text Structure to JSON Extractor → `src/gui/text_extractor_dock.py`
5. ✅ ChatGPT File Processor → `src/gui/ai_processor_dock.py` (OpenAI + Gemini)

**Conclusão**: Nenhuma implementação adicional necessária. Todas as funcionalidades já integradas.

---

#### Task #45 - Sistema de Tutoriais + Menu Help (v2.9.15)
**Status**: ✅ Completa - 24/11/2025

**Objetivo**: Criar sistema de tutoriais com 3 tutoriais MVP, menu Help, e preparação para chatbot com IA.

**Implementação**:
1. ✅ **Estrutura de Diretórios**:
   - `docs/tutorials/{beginner,developers}/{basic,advanced}/`
   - Organização hierárquica para crescimento futuro

2. ✅ **Arquivos Core**:
   - `README.md` (73 linhas): Índice e boas-vindas
   - `index.json` (89 linhas): Metadata estruturada para chatbot Gemini Flash
   - `quickstart.md` (157 linhas): Guia de 5 minutos com 3 workflows de exemplo

3. ✅ **Tutoriais MVP** (beginner/basic):
   - `01-json-translate.md` (458 linhas): Internacionalização step-by-step
   - `02-search-replace.md` (452 linhas): Busca e substituição com regex
   - `03-json-rewriter.md` (468 linhas): Transformação JSON com dedupe

4. ✅ **TutorialsDock** (`src/gui/tutorials_dock.py` - 450+ linhas):
   - QTreeWidget com navegação hierárquica (Beginner/Developers → Basic/Advanced)
   - QTextBrowser para renderização markdown com CSS styling
   - Sistema de busca por keywords (título, descrição, keywords)
   - Suporte a links internos (.md) e externos (URLs)
   - Signal `tutorial_opened` para integração futura com chatbot
   - Padrões aplicados: Strategy, Factory, Information Expert (GRASP)

5. ✅ **Menu Help**:
   - Adicionado `Help → Tutorials` em `app.py`
   - Traduções EN/PT-BR em `i18n/`
   - Atalho no método `_show_tutorials()`

6. ✅ **Preparação Chatbot**:
   - `index.json` com FAQ, keywords, semantic_search_config
   - Estrutura pronta para Gemini Flash API
   - Metadata YAML frontmatter em cada tutorial

**Próximos Passos** (sprints futuros):
- Implementar 15-20 tutoriais adicionais (todos os módulos)
- Criar ChatbotDock com Gemini Flash integration
- Tutoriais avançados (regex, scope filtering, batch operations)
- Tutoriais para desenvolvedores (extending Clarify, plugin system)

---

#### Task #46 - Editor de Arquivos Integrado (v2.9.16)
**Status**: ✅ Completa - 30/11/2025

**Objetivo**: Implementar editor de texto integrado com diferenciação de escopo por cores (tipo Notepad).

**Implementação**:
1. ✅ **EditorDock** (`src/gui/editor_dock.py` - 700+ linhas):
   - Interface tabbed para múltiplos arquivos abertos simultaneamente
   - Botões: New, Open, Save, Save As, Close Tab
   - Status bar com indicador de arquivo atual
   - Recent files list (últimos 10 arquivos)
   - Atalhos de teclado (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+W, Ctrl+E)

2. ✅ **SyntaxHighlighter** (diferenciação de escopo por cores):
   - **HTML/JSX/TSX**: Tags azul bold (#569CD6), atributos light blue (#9CDCFE)
   - **JSON**: Keys light blue (#9CDCFE), brackets gold (#FFD700), values orange (#CE9178)
   - **Python**: Keywords purple bold (#C586C0), comments green italic (#6A9955), strings orange
   - **JavaScript/TypeScript**: Keywords purple, strings orange, comments green
   - **Números**: Light green (#B5CEA8) em todos os tipos
   - Suporte automático por extensão de arquivo

3. ✅ **EditorTab** (gerenciamento de abas):
   - Tracking de modified state (asterisco * no título quando modificado)
   - Signal `modified_changed` para atualização de UI
   - Load/save file com encoding UTF-8
   - Monospace font (Courier New, 10pt)
   - Tab stop distance: 40 pixels (≈4 espaços)

4. ✅ **Funcionalidades**:
   - Abrir/salvar arquivos (.txt, .json, .html, .tsx, .py, .js, .ts, etc.)
   - Prevenir abertura duplicada (switch para tab existente)
   - Confirmação ao fechar tab com mudanças não salvas
   - API pública `open_file_path()` para integração com outros módulos
   - Suporte a arquivos "Untitled" (sem path)

5. ✅ **Menu File**:
   - Adicionado `File → Open Editor` em `app.py`
   - Atalho: Ctrl+E
   - Traduções EN/PT-BR em `i18n/`
   - Método `_show_editor()` para exibir dock

6. ✅ **Arquitetura**:
   - Padrões aplicados: Strategy (syntax highlighting), Factory (tab creation), Observer (modified signal)
   - Herda de BaseDock (consistência com outros docks)
   - Low Coupling com app.py (comunicação via sinais)
   - High Cohesion (EditorTab, EditorDock, SyntaxHighlighter - responsabilidades claras)

**Arquivos Criados**:
- `src/gui/editor_dock.py` (700+ linhas)
- `tests/test_editor_dock.py` (15 testes estruturados)

**Próximos Passos** (melhorias futuras):
- Find/Replace functionality (Ctrl+F, Ctrl+H)
- Line numbers panel
- Code folding para blocos
- Auto-indentation por tipo de arquivo
- Context menu (copy, paste, select all)
- Syntax highlighting para mais linguagens (Ruby, Go, Rust)

---

#### Task #47 - Editores JSON com Recursos Avançados (v2.9.17)
**Status**: ✅ Completa - 30/11/2025

**Objetivo**: Implementar editor JSON avançado integrado ao EditorDock com validação em tempo real, tree view, formatação e busca.

**Implementação**:

1. ✅ **JsonValidator** (`src/gui/json_validator.py` - 160 linhas):
   - Validação em tempo real com `json.loads()`
   - Retorna `ValidationResult` (is_valid, error_msg, line, col)
   - **Format JSON**: Pretty print com 2/4 espaços de indentação
   - **Minify JSON**: Compacta JSON (remove espaços e quebras)
   - **ValidatorFactory**: Factory Method para criar validators por tipo
   - Pattern: **Strategy** (algoritmo de validação encapsulado, extensível para XML/YAML)

2. ✅ **JsonTreeWidget** (`src/gui/json_editor_tab.py` - 100+ linhas):
   - QTreeWidget para navegação hierárquica
   - Nodes clicáveis → move cursor para linha correspondente no editor
   - Collapse/Expand automático (botões no toolbar)
   - Visual indicators:
     * Objects: `{...} (N keys)` em light blue (#9CDCFE)
     * Arrays: `[...] (N items)` em teal (#4EC9B0)
     * Strings: `"value"` em orange (#CE9178)
     * Numbers: `123` em light green (#B5CEA8)
     * Booleans: `true/false` em blue (#569CD6)
     * Null: `null` em gray
   - Pattern: **Composite** (estrutura recursiva de árvore)

3. ✅ **JsonSearchDialog** (`src/gui/json_editor_tab.py` - 150+ linhas):
   - Find por key ou value dentro do JSON
   - Opções:
     * Case Sensitive
     * Keys Only (busca apenas chaves `"key":`)
     * Values Only (busca apenas valores `: "value"`)
   - Find Next/Previous com navegação circular
   - Highlight matches em amarelo (#FFFF00)
   - Results label: "Match N of M"
   - Pattern: **Command** (operação de busca como objeto, facilita undo/redo futuro)

4. ✅ **JsonEditorTab** (`src/gui/json_editor_tab.py` - 500+ linhas):
   - Editor completo para arquivos JSON
   - **Toolbar**:
     * Format JSON (2 spaces / 4 spaces / Minify)
     * Validate (manual validation trigger)
     * Search (abre JsonSearchDialog)
     * Collapse All / Expand All (tree controls)
   - **Splitter Layout**: Editor (70%) | Tree View (30%)
   - **Real-time Validation**:
     * Debounced validation (500ms após última digitação)
     * Visual indicators:
       - Valid: `✓ Valid JSON` (green #6A9955)
       - Invalid: `✗ Invalid JSON (line X, col Y): error` (red #F44747)
       - Border color: green (valid) / red (invalid)
   - **Save Behavior**:
     * Warning se JSON inválido, mas permite salvar
     * Retorna `(success: bool, error_msg: str)`
   - **Tab Title**: `🗎 filename.json *` (ícone JSON + asterisco se modificado)
   - **Signals**:
     * `modified_changed(bool)`: Emite quando estado de modificação muda
     * `validation_changed(bool, str)`: Emite quando validação muda
   - Pattern: **Facade** (interface unificada para subsistemas de validação, tree, search)
   - Pattern: **Observer** (signals para comunicação com EditorDock)

5. ✅ **EditorDock Modificações** (`src/gui/editor_dock.py`):
   - **Factory Method**: `_create_tab_for_file(path)`
     * Detecta extensão `.json` → cria `JsonEditorTab`
     * Outras extensões → cria `EditorTab` (text editor simples)
   - **Status Bar**: Mostra "JSON Editor" vs "Text Editor"
   - **Tab Icons**: Ícone 🗎 para arquivos JSON
   - **Save Handling**: Suporta ambos tipos de tabs (EditorTab e JsonEditorTab)
   - **Integration**: Mesmo dock, detecção automática, módulos separados (modularização)
   - Pattern: **Factory Method** (criação de tabs baseada em contexto)

**Arquivos Criados/Modificados**:
- `src/gui/json_validator.py` (novo - 160 linhas)
- `src/gui/json_editor_tab.py` (novo - 750+ linhas)
- `src/gui/editor_dock.py` (modificado - adicionado Factory Method)
- `src/gui/__init__.py` (modificado - exports)
- `tests/test_json_editor.py` (novo - 18 testes)

**Testes**:
- 18 unit tests (100% passing):
  * TestValidationResult: 2 tests
  * TestJsonValidator: 10 tests (validate, format, minify, edge cases)
  * TestValidatorFactory: 3 tests
  * TestJsonEditorTabIntegration: 3 tests (load, save, validation UI)

**Padrões de Design Aplicados**:
- **Strategy** (GoF): JsonValidator encapsula algoritmo de validação
- **Factory Method** (GoF): EditorDock cria tabs apropriados, ValidatorFactory cria validators
- **Composite** (GoF): JsonTreeWidget estrutura hierárquica recursiva
- **Command** (GoF): JsonSearchDialog operações de busca
- **Facade** (GoF): JsonEditorTab interface unificada
- **Observer** (GoF): Signals para comunicação entre componentes
- **Value Object** (DDD): ValidationResult objeto imutável
- **Information Expert** (GRASP): JsonEditorTab conhece seu próprio estado
- **Low Coupling** (GRASP): Comunicação via signals
- **High Cohesion** (GRASP): Responsabilidades claras por classe

**Funcionalidades Completas**:
- ✅ Validação JSON em tempo real (debounced 500ms)
- ✅ Format JSON com 2/4 espaços ou minify
- ✅ Tree view com navegação hierárquica clicável
- ✅ Collapse/Expand nodes
- ✅ Search por key/value com options (case sensitive, keys only, values only)
- ✅ Highlight matches em amarelo
- ✅ Visual indicators (green/red border, status label)
- ✅ Warning ao salvar JSON inválido (não bloqueia)
- ✅ Ícone JSON 🗎 em tabs
- ✅ Integração transparente com EditorDock existente

**Próximos Passos** (melhorias futuras):
- JSON schema validation
- Auto-completion para chaves
- Diff viewer para comparar JSONs
- Export tree view to CSV
- Undo/Redo específico para JSON operations

---

#### Task #5 - Edit-Only Mode: Sandbox Editing sem File Backing (v2.9.18)

**Data de Conclusão**: 30 de Novembro de 2025  
**Arquivos Modificados**: `src/gui/editor_dock.py`, `src/gui/json_editor_tab.py`  
**Arquivo de Teste**: `tests/test_edit_only_mode.py` (16 testes - 100% passing)

**Objetivo**: Permitir edições no editor sem conexão com arquivos no disco. Modo "sandbox" para preview, testes, ou edições temporárias que não devem ser salvas automaticamente.

**Componentes Implementados**:

1. ✅ **EditorTab Edit-Only Mode** (`src/gui/editor_dock.py` - 400+ linhas modificadas):
   - Flag `edit_only_mode` (State pattern: muda comportamento de save)
   - Toolbar com 3 botões:
     * **📋 Copy**: Copia conteúdo para clipboard
     * **💾 Export**: Exporta para arquivo
     * **🔓 Enable Saving**: Converte para file-backed editor (Save As dialog)
   - Visual indicators (4 tipos):
     * **Indicador #1**: Ícone 🔒 no título da tab
     * **Indicador #2**: Cor laranja (#FF8C00) no status bar
     * **Indicador #3**: Borda dourada (#FFD700) ao redor do editor
     * **Indicador #4**: Status text "Edit-Only Mode"
   - Methods:
     * `_copy_to_clipboard()`: Command pattern
     * `_export_to_file()`: Command pattern
     * `_enable_file_saving()`: Conversão edit-only → normal
     * `toggle_edit_only_mode()`: State transition
     * `_update_visual_indicators()`: Atualiza borda/background
     * `_update_toolbar_visibility()`: Atualiza buttons

2. ✅ **EditorDock Integration** (`src/gui/editor_dock.py` - 200+ linhas modificadas):
   - Untitled-N counter (múltiplas tabs sem conflito de nomes)
   - Context menu (right-click na tab):
     * "Enable Edit-Only Mode" / "Disable Edit-Only Mode"
   - Open dialog com checkbox:
     * "Open in Edit-Only Mode (no file changes)"
   - Modified save behavior (State pattern):
     * Normal mode: Save direto no arquivo
     * Edit-only mode: Prompt "Convert to file-backed?" → Save As
   - Close behavior customizado:
     * Normal tabs: Save / Discard / Cancel
     * Edit-only tabs: Save to File / Copy to Clipboard / Discard / Cancel (4 opções)
   - Methods:
     * `_new_file(edit_only=bool)`: Cria tab edit-only ou normal
     * `_toggle_edit_only_for_tab(index)`: Toggle via context menu
     * `_show_tab_context_menu(pos)`: QMenu com toggle action
     * `_on_tab_changed(index)`: Atualiza status bar com cor laranja se edit-only

3. ✅ **JsonEditorTab Edit-Only Support** (`src/gui/json_editor_tab.py` - 20 linhas):
   - Herda `edit_only_mode` flag de EditorTab (via constructor)
   - Signal `edit_only_changed = Signal(bool)`
   - Validação JSON continua funcionando em edit-only mode
   - Ícone combinado: 🔒🗎 (lock + JSON icon)
   - Methods:
     * `toggle_edit_only_mode()`: Emit signal para EditorDock

**Padrões de Projeto (GoF + GRASP)**:

- **State** (GoF): `edit_only_mode` flag altera comportamento de save (file-backed vs sandbox)
- **Strategy** (GoF): Diferentes estratégias de persistência (save to file vs clipboard/export)
- **Command** (GoF): Ações Copy/Export encapsuladas como métodos
- **Observer** (GoF): Signals `edit_only_changed` para comunicação entre componentes
- **Factory Method** (GoF): `_create_tab_for_file(file_path, edit_only)` cria tipo correto
- **Information Expert** (GRASP): EditorTab gerencia seu próprio estado edit_only
- **Low Coupling** (GRASP): Comunicação via signals, não dependências diretas
- **Protected Variations** (GRASP): Mudanças de modo não afetam código cliente

**Funcionalidades Completas**:
- ✅ Edit-only mode flag em EditorTab e JsonEditorTab
- ✅ 4 visual indicators (🔒 icon, orange status, golden border, status text)
- ✅ Toolbar buttons (Copy, Export, Enable Saving)
- ✅ Context menu toggle (right-click na tab)
- ✅ Open dialog checkbox (abrir arquivos em edit-only)
- ✅ Untitled-N counter (Untitled, Untitled-2, Untitled-3...)
- ✅ Save behavior: edit-only bloqueia save, abre confirmation dialog
- ✅ Close behavior: 4 opções para edit-only (Save/Clipboard/Discard/Cancel)
- ✅ JSON validation ativa em edit-only mode
- ✅ Undo/Redo preservado

**Testes** (16 testes - 100% passing):
1. `test_edit_only_flag`: Verifica flag set corretamente
2. `test_visual_indicators_lock_icon`: Testa 🔒 no título
3. `test_visual_indicators_golden_border`: Testa borda #FFD700
4. `test_visual_indicators_status_text`: Testa "Edit-Only Mode" text
5. `test_toolbar_buttons_visibility`: Testa botões existem
6. `test_copy_to_clipboard`: Testa Copy button funciona
7. `test_export_to_file`: Testa Export button cria arquivo
8. `test_toggle_edit_only_mode`: Testa toggle atualiza indicators
9. `test_new_file_untitled_counter`: Testa Untitled-1, Untitled-2, etc.
10. `test_open_file_with_edit_only_checkbox`: Testa checkbox no Open dialog
11. `test_save_blocked_in_edit_only`: Testa save mostra confirmation
12. `test_close_edit_only_with_clipboard`: Testa close com clipboard option
13. `test_json_editor_edit_only_flag`: Testa JsonEditorTab suporta flag
14. `test_json_validation_active_in_edit_only`: Testa validação JSON ativa
15. `test_state_transition_normal_to_edit_only`: Testa State pattern
16. `test_state_affects_save_behavior`: Testa save behavior muda com state

**Próximos Passos** (melhorias futuras):
- Keyboard shortcut Ctrl+Shift+E para toggle edit-only
- Histórico de tabs edit-only fechadas (recovery)
- Auto-save temporário em memória para edit-only tabs
- Diff view: comparar edit-only content com arquivo original

### 🔨 Tasks Pendentes

#### Editor Features

- **[X]** Incluir habilidade de abrir e ler arquivos, diferenciar escopo com temas de cores diferentes *(v2.9.16 - Task #46: EditorDock)*
- **[X]** Incluir editores JSON como abas *(v2.9.17 - Task #47: JsonEditorTab com validação, tree view, search)*
- **[X]** Possibilidade de mudanças feitas apenas no editor de texto do próprio Clarify, não mais em arquivos *(v2.9.18 - Task #5: Edit-Only Mode)*
- **[]** Adicionar novo painel 'Smart file editing - AI' com o 'ChatGPT File Processor', ou seja, processamento de arquivos com inteligências artificiais;
- **[]** Incluir habilidade de conectar ao Google Translate e realizar operações de tradução online no programa por meio de API's;
- **[X]** Incluir Gemini na lista de IAs a serem usadas *(v3.0.0 - AI File Processor com suporte OpenAI e Gemini)*
- **[]** Adicionar opções avançadas condicionais também no painel Smart Edit File (AI)
- **[]** Incluir todas features de Search/Replace e Insert no Smart Edit File (AI) e editores JSON
- **[X]** Adicionar feature onde resultado pode ser reutilizado no editor de texto do Clarify *(v2.9.19 - Task #6: Open in Editor from Results)*

#### JSON Advanced Features

- **[X]** Possibilidade de buscar chaves e valores JSON (ex: `t.auth.brandTitle`) *(v3.0.0 - JSON Search)*
- **[X]** Incluir 'is file' em outros lugares para pegar mais arquivos com caminhos de diretórios **(v2.9.6)**
- **[]** Adicionar feature para inserir novos chaves/valores em chaves existentes com regex e conceito de registrador de memória
- **[]** Incluir possibilidade de inserir novo valor em modo grupo, onde word keys podem ser usadas para inserir novo valor entre essas word keys, em linha separada ou coluna específica. Usuário pode entrar contagem de ocorrências tolerada (threshold)
- **[]** Adicionar possibilidade de reescrever JSON substituindo chave e objeto em outros lugares se valor da chave é mesmo e chaves têm diferentes
- **[]** Permitir usuário escolher className names ao invés de tag names para fazer chaves JSON. Usuário pode escolher pegar apenas diferença entre className names
- **[]** Quando usuário precisa reestruturar JSON e transformar texto em objeto JSON, aplicação deve permitir colar conteúdo de texto na GUI e então performar reestruturação
- **[]** Ao buscar outras chaves e objetos JSON (ex: `t.pages.contact.title` com word-key 'contact'), não apenas chaves devem ser encontradas, valores à direita das chaves também
- **[]** Ferramenta de busca pode incluir busca por nome de arquivo
- **[]** Para busca de arquivos/diretórios, ao invés de escrever ou buscar com ferramenta pobre, incluir possibilidade de buscar com condições avançadas tanto arquivos quanto diretórios (ex: com regex e estrutura de condições), incluindo simultaneamente. Muito útil para encontrar arquivos/diretórios com mais precisão

---

## 🔵 WOULD HAVE LATER (Longo Prazo / Futuro)

### ✅ Tasks Concluídas

*(Nenhuma task nesta categoria foi concluída ainda)*

### 🔨 Tasks Pendentes

#### UI/UX Improvements

- **[X]** Incluir botão 'clear all conditions' nas opções avançadas condicionais **(v2.9.5)**
- **[X]** Adicionar scroll nos painéis 'search/replace' e 'insert' **(v2.9.5)**
- **[X]** Incluir histórico de atividades como feature do Google Translate **(v2.9.6 - History Dock)**
- **[X]** Incluir possibilidade de adicionar nova linha de opções avançadas condicionais (mínimo 3, sem limite máximo) **(v2.9.7 - Dynamic Condition Lines)**
- **[X]** Fornecer habilidade de mudar aparência da aplicação para background transparente **(v2.9.9 - Transparency Slider)**
- **[X]** Mudar caixas de texto de insert, query e replacement para caixas redimensionáveis pelo usuário **(v2.9.6)**
- **[X]** Incluir tooltips na aplicação Clarify **(v2.9.3)**
- **[X]** Adicionar sistema de temas (Light, Dark, System) em toda a aplicação **(v2.9.4)**
- **[X]** Adicionar opções de undo e redo para mudanças feitas (Command Pattern, Ctrl+Z/Ctrl+Y, 10 níveis) **(v2.9.8)**
- **[X]** Traduzir aplicação para idiomas mais falados do mundo **(v2.9.10 - Task #24: Sistema i18n com EN/PT-BR)**

#### Advanced Features

- **[]** Além de fornecer tutoriais, modelos de uso de código, métodos Python disponíveis e código Python pronto para usuários que querem automatizar projetos no Clarify, aplicação pode aprender padrões de uso e apresentar ideias de algoritmos, passos ou instruções para completar tarefas repetitivas. Incluir programação em blocos e low-code;
- **[]** Incluir tutoriais de uso
- **[]** Incluir busca com ajuda de inteligência artificial (da mesma maneira como acontece com as pesquisas avançadas com IA no Visual Studio Code quando se pressiona CTRL+SHIFT+F).
- **[]** Embutir assistente virtual para uso com IA;
- **[]** Pesquisar possibilidade de embutir Clarify no gerenciador de aplicativos Linux e quanto se ganha fazendo isso. Uma vez instalado, compilar código antes de enviar;
- **[]** Adicionar backup de dados do usuário para undo/redo com ECC, ou usar arquitetura de comando Gof
- **[]** Adicionar backup de dados com arquitetura de comando, com Egg Cell Compactor e IA para armazenar todas mudanças feitas pelo usuário mesmo por longo período
- **[]** Permitir usuário fazer macros e algoritmos com features da aplicação para utilidades mais complexas, com código Python ou programação em blocos
- **[]** Quando usuário clicar em resultado de busca ou insert, aplicação deve abrir arquivo em editor próprio
- **[]** Fazer Clarify capaz de criar algoritmos para performar tarefas do usuário, e não apenas isso, também compilar ou traduzir para linguagem de programação (Python, React, Javascript). Esses algoritmos 

#### Calculator & Set Operations

- **[]** Calculator: Adicionar conceitos de calculadora como registrador de memória, adição, concatenação e recall de memória padrão com histórico de modificações. A ideia seria a seguinte: o registro de memória seria o resultado do processamento, por exemplo, de busca, do painel de resultado de buscas. A adição significa: adicione um resultado de busca com outro resultado de forma que estes se complementem, por exemplo, em ordem alfabética ou unindo resultados de um mesmo arquivo (quando é em formato de árvore) no painel de resultados. Concatenação iria concatenar um resultado a outro, colocando o segundo resultado debaixo do primeiro no painel de resultados. O recall de memória iria chamar resultados salvos e jogar no painel de resultados, como pesquisas pela palavra "span".
- **[]** Set: Adicionar operações de conjunto lógico de arquivos JSON como interseção, diferença, união e diferença exclusiva. Incluir checkboxes para incluir chaves e/ou valores nesta operação de conjunto, em que, por exemplo, se for escolhida a intersecção entre arquivo A e arquivo B, ambos JSON, se tem valores equivalentes tanto em A quanto em B no sentido de chave e valor (title: "Tarefas de Casa"), no sentido de caminhos de chave e valor (t.pages.home.features.title, title: "Tarefas de Casa"), e somente no sentido de caminhos de chave (t.pages.home.features.title);
- **[]** Verificar se na pasta add existe alguma funcionalidade que ainda não foi implementada;

---

## 📝 Notas de Implementação

### Tarefas Críticas Completadas

#### ✅ JSON Rewriter Bug Fix (Completada)
**Problema**: Perda de dados ao processar tipo `Obj` (lista de tuplas chave-valor).

**Solução Aplicada**: 
- **Arquivo**: `rewriter/rewriter.py`
- **Função**: `sanitize_keys_and_values()`
- **Linhas**: ~40-55
- **Fix**: Adicionado suporte para tipo `Obj` ANTES do tratamento de `dict`

```python
def walk(v):
    if isinstance(v, Obj):  # ⭐ CRITICAL FIX
        out = Obj()
        for k, x in v:
            nk = clean_key(k)
            if nk is None:
                continue
            vx = walk(x)
            if drop_empty_values and isinstance(vx, str) and not vx.strip():
                continue
            out.append((nk, vx))
        return out
    # ... continua com dict e list
```

**Status**: ✅ Corrigido e validado em 23/11/2025

---

## 📊 Estatísticas

### Por Categoria

| Categoria | Total | Completas | Pendentes | % Completo |
|-----------|-------|-----------|-----------|------------|
| MUST HAVE | 12 | 11 | 1 | 91.7% |
| SHOULD HAVE | 50 | 40 | 10 | 80.0% |
| COULD HAVE | 18 | 7 | 11 | 38.9% |
| WOULD HAVE LATER | 24 | 12 | 12 | 50.0% |
| **TOTAL** | **104** | **70** | **34** | **67.3%** |

### Notas

- Este é um projeto ambicioso com roadmap de longo prazo
- Funcionalidades MUST HAVE essenciais praticamente completas (91.7%)
- **v2.9.9**: Melhorias em tradução, validação de case, ranges hierárquicos e transparência
- **v3.0.0**: Adicionadas 5 ferramentas profissionais (Case Converter, JSON Search, Text Extractor, Placeholder Replacer, AI File Processor)
- Projeto funcional e utilizável no estado atual com ferramentas avançadas
- **64.4%** do projeto total completo (67 tasks completas) - em progressão constante
- Categorias SHOULD/COULD/WOULD são melhorias e features avançadas
- **v2.9.14**: Task #23 COMPLETA - Orphaned Keys Update System com VALUE EQUALITY (12 unit tests passing)
- **v2.9.15**: Tasks #44 e #45 COMPLETAS - Análise add/ + Sistema de Tutoriais com Help menu (3 tutoriais MVP, TutorialsDock, preparação chatbot)
- **v2.9.17**: Task #47 COMPLETA - JSON Editor avançado com validação tempo real, tree view, format, search (750+ linhas, 18 testes passing)
- **v2.9.16**: Task #46 COMPLETA - Editor Integrado com syntax highlighting diferenciado por cores (700+ linhas, tabs, save/load, Ctrl+E)
- **v2.9.17**: Task #47 COMPLETA - JSON Editor avançado integrado (validação, tree view, format, search - 750+ linhas, 18 testes)
- **v2.9.18**: Task #5 COMPLETA - Edit-Only Mode sandbox editing (600+ linhas, 16 testes, State+Strategy+Command patterns)
- **v2.9.13**: Melhorias de UX com context menus, tooltips, preferences persistentes e stats em tempo real
- **Correção 30/11/2025**: 4 tasks já implementadas foram marcadas corretamente (reverse translation, cancel processing, file list ls/dir, async file insertion)

### Marcos Importantes

- **v3.0.0 (24/11/2025)**: +6 tasks completadas (SHOULD HAVE)
  - Case Converter integrado
  - JSON Search com suporte TS
  - Text Extractor HTML/JSX
  - Placeholder Replacer com scope filtering
  - AI File Processor (OpenAI + Gemini)
  - Interrupção de processamento IA

---

## 🔗 Referências

- **Repositório**: [github.com/JosueAmaral15/clarify](https://github.com/JosueAmaral15/clarify)
- **Documentação Principal**: `README.md`
- **Status de Migração**: `docs/MIGRATION_FINAL_STATUS.md`
- **Estrutura do Projeto**: `docs/project_structure.txt`

---

---

## 🎯 Marcos Recentes

- **v2.9.13 (30/11/2025)**: +4 tasks completadas (SHOULD HAVE - UX/UI Improvements) - **100% COMPLETO** ✅
  - ✅ Task #40: Context Menu em File List com multi-select "Open in File Manager"
  - ✅ Task #41: Tooltip preview em Advanced Search (3 linhas, 200 chars max)
  - ✅ Task #42: Save preferences (checkboxes + últimos 10 diretórios com QSettings)
  - ✅ Task #43: Stats label em JSON Translate (contagem arquivos/traduções em tempo real)

- **v2.9.10 (30/11/2025)**: +4 tasks completadas (SHOULD HAVE + WOULD HAVE LATER) - **100% COMPLETO** ✅
  - ✅ Task #24: Sistema de internacionalização (i18n) com alternância runtime EN↔PT-BR
  - ✅ Task #22: Normalizar escaping excessivo automaticamente (`\\\\'` → `\\'`)
  - ✅ Task #21: Converter arrays para objetos com geração inteligente de chaves
  - ✅ Task #23: Atualizar referências órfãs após eliminação de duplicatas

- **v2.9.9 (29/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Task #17: Validated dynamic condition lines (already complete in v2.9.7)
  - ✅ Task #15: Case inconsistency validator (before/after preview dialog, apply/cancel)
  - ✅ Task #14: Hierarchical include/exclude ranges (syntax: "include div#test1, exclude #test2")
  - ✅ Task #16: Parentheses in translation (treated as part of translatable text)
  - ✅ Task #13: Auto-consolidate fragmented placeholders (merge adjacent refs into single unit)
  - ✅ Task #18: Transparent background slider (0-100%, persistent settings)

- **v2.9.8 (28/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Task #8: Remove duplicate array values (consecutive & all duplicates)
  - ✅ Task #9: Enforce consistent case (camelCase, PascalCase, snake_case, kebab-case)
  - ✅ Task #7: Preserve uppercase keys durante tradução JSON
  - ✅ Task #11: Occurrence count in JSON search (Top 5 files/keys, total)
  - ✅ Task #10: Reverse translation (Swap Dictionaries + Undo with Backup)
  - ✅ Task #12: Undo/Redo system (Command Pattern, Ctrl+Z/Y, 10 níveis)

- **v2.9.7 (28/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE)
  - ✅ Emit export const (backend integration)
  - ✅ Fix backslash escaping (esc_single normalization)
  - ✅ Avoid duplicate child keys (parent.child.child → parent.child)
  - ✅ Filename search (wildcards, prefix "filename:", regex)
  - ✅ Save results (single file, per file, per query)
  - ✅ Dynamic condition lines (Add/Remove buttons, min 3, no max)

- **v2.9.6 (28/11/2025)**: +5 tasks completadas (SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Exclude numeric keys (Text Extractor + JSON Rewriter)
  - ✅ Skip empty values (Text Extractor + JSON Rewriter)
  - ✅ Resizable text boxes (ed_query, ed_repl, ed_text)
  - ✅ History Panel (View → History com 10 entradas)
  - ✅ "Is File" consistency em todos os módulos JSON

- **v2.9.5 (28/11/2025)**: +3 tasks completadas (UI/UX Improvements)
  - ✅ Clear All Conditions button
  - ✅ Scroll em painéis principais
  - ✅ Ordenação alfabética de resultados

---
**Última atualização**: 30 de Novembro de 2025  
**Mantido por**: Josué Amaral Novembro de 2025  
**Mantido por**: Josué Amaral
