# Clarify - Programming Tasks

**Author**: Josué Amaral  
**Date**: 2025/10/01  
**Last Update**: 2025/12/02

Este documento contém todas as tarefas de desenvolvimento do Clarify organizadas por prioridade usando o método MoSCoW (Must Have, Should Have, Could Have, Would Have).

---

## 🎉 v2.9.32 Released! + 50 Novas Recomendações

**Data**: 02/12/2025  
**Feature Completa**: JSON Set Operations (∩, ∪, −, ⊕)

### ✅ O que foi entregue na v2.9.32
- ✨ 4 operações de conjunto lógico com pipeline left-to-right
- 🔒 Validação de segurança CWE-22 (path traversal)
- 🎨 GUI completa + CLI robusto (argparse)
- ✅ 50/50 testes unitários passing (100%)
- 🏆 Pylint 9.38/10 (exceeds target)
- 📖 Documentação completa (CHANGELOG + TASKS.md)
- 🚀 Push to GitHub: commit fcb41bd + tag v2.9.32

### 📋 +50 Novas Tasks Recomendadas (02/12/2025)

Esta atualização adiciona **50 novas tarefas** ao roadmap, expandindo significativamente a visão de futuro do Clarify:

#### 🔧 COULD HAVE (+18 tasks)
1. **Melhorias de Set Operations** (7 tasks):
   - Venn Diagram Visualizer, Diff Viewer, Statistics Dashboard
   - Multi-format Export (CSV/Excel/YAML), Merge Results, Batch Operations
   - History, Presets, Formula Builder

2. **Calculator Integration** (2 tasks):
   - Set Operations + Calculator memory slots
   - Statistics sobre result sets

3. **Quality Assurance** (4 tasks):
   - GUI automated tests, Performance benchmarks, Code coverage, Load testing

4. **UX & Accessibility** (6 tasks):
   - Keyboard shortcuts comprehensivos, Dark mode, Accessibility features
   - i18n expansion (ES/FR/DE/ZH/JA), Customizable layouts, Tooltips expansion

5. **Documentation** (6 tasks):
   - User Manual Wiki, Video tutorials, Recipe book
   - API docs (Sphinx), Contributing guide, Changelog automation

6. **Architecture & Maintenance** (6 tasks):
   - Plugin system, Config management, Logging system
   - Update checker, Error reporting, Database migrations

#### 🚀 WOULD HAVE LATER (+32 tasks)
- Advanced Features: IA tutorial assistant, TOON format, File as Database, Macro system
- Cloud & Collaboration: Sync (Drive/Dropbox/OneDrive), version history
- Modern Interfaces: Real-time JSON validation, GraphQL queries, Git integration
- Innovation: AI pattern learning, block programming, algorithm generation

### 📊 Impacto no Roadmap
- **Antes**: 107 tasks total (84.1% completo)
- **Agora**: 157 tasks total (57.3% completo)
- **Conclusão**: Projeto tem roadmap robusto para próximos 12-18 meses

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
- **[X]** Durante tradução JSON, preservar uppercase com parâmetro do usuário **(v2.9.8)**

### 🔨 Tasks Pendentes

*(Nenhuma task nesta categoria está pendente - 100% completa)*

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

#### Task v2.9.22 - Contador de Remoções no JSON Rewriter
**Status**: ✅ Completa - 01/12/2025  
**Arquivos Modificados**: `src/rewriter/operations.py` (+97 linhas), `src/gui/json_rewriter_dock.py` (+50 linhas), `src/rewriter/rewriter.py` (+3 linhas)  
**Arquivo de Teste**: `tests/test_removal_counter.py` (350 linhas, 18 testes - 100% passing)

**Objetivo**: Adicionar contador de estatísticas de remoção exibindo quantos itens foram removidos por cada operação do JSON Rewriter.

**Componentes Implementados**:

**1. operations.py - 8 Funções Modificadas**:
- Todas retornam tuplas `(resultado, contador)`
- Pattern: `removed_count` acumula recursivamente
- Funções: `dedupe`, `join_keys`, `eliminate_duplicates`, `exclude_numeric_keys`, `skip_empty_values`, `avoid_duplicate_child_keys`, `remove_duplicate_array_values`, `skip_keys_without_siblings`

**2. json_rewriter_dock.py**:
- `format_removal_statistics(stats)`: Formata output detalhado
- `cli_dedupe()`: Captura 8 contadores, retorna `(output, substitution_map, stats)`
- `_rewrite()`: Exibe estatísticas em MessageBox

**Exemplo de Output**:
```
✂️ Removal Statistics:
• Removed duplicate key-value pairs: 3 key-value pairs
• Eliminated duplicate values: 12 values
• Excluded numeric keys: 5 keys
• Skipped empty key-value pairs: 8 key-value pairs
Total: 28 items removed
```

**Testes**: 18 testes (9 classes), 100% passing em 0.28s

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

#### Task #48 - JSON Value Search (v2.9.23)
**Status**: ✅ Completa - 01/12/2025  
**Arquivos Modificados**: `src/json_search/query_parser.py` (+110 linhas), `src/json_search/__init__.py` (+2 exports), `src/gui/json_search_dock.py` (+15 linhas)  
**Arquivo de Teste**: `tests/test_json_value_search.py` (320 linhas, 20 testes - 100% passing)

**Objetivo**: Adicionar capacidade de buscar valores JSON (além de chaves) no JSON Search, com suporte a 3 modos: Key only, Value only, Key and Value.

**Componentes Implementados**:

**1. resolve_query_by_value() - Busca por Valores**:
- Busca em valores armazenados no flat_index
- Suporta case-sensitive e regex
- Converte valores para string (incluindo números, booleanos, None)
- Retorna dicts com `{"key", "value", "file", "line", "match_type": "value"}`
- Limita resultados a 200 por performance

**2. resolve_query_with_mode() - Busca Unificada**:
- **Modo "key"**: Busca apenas em chaves (comportamento original)
- **Modo "value"**: Busca apenas em valores (NOVO)
- **Modo "both"**: Busca em chaves OU valores (NOVO, default)
- Normaliza resultados: `resolve_query()` retorna "path", converte para "key"
- Deduplica resultados (mesma key + file + line)
- Adiciona campo `match_type` para indicar origem do match

**3. JsonSearchWorker Modificado**:
- Substituído `resolve_query()` por `resolve_query_with_mode()`
- Passa `search_key`, `search_value` e `search_mode` separadamente
- Permite buscas combinadas: key="title" + value="Welcome"

**4. Indicadores Visuais nos Resultados**:
- 🔑 (key icon): Match encontrado em chave
- 💎 (gem icon): Match encontrado em valor
- Formato: `1. 🔑 en.json: pages.home.title = Welcome`

**Casos de Uso**:
```python
# Buscar valores "Welcome"
resolve_query_with_mode(flat, "", "Welcome", "value", False, False)
# Resultado: [{"key": "pages.home.title", "value": "Welcome", "match_type": "value"}]

# Buscar chaves "title" OU valores "Home"
resolve_query_with_mode(flat, "title", "Home", "both", False, False)
# Resultado: chaves com "title" + valores com "Home"

# Buscar valores numéricos
resolve_query_with_mode(flat, "", "25", "value", False, False)
# Resultado: [{"key": "user.age", "value": 25, "match_type": "value"}]
```

**Testes**: 20 testes (3 classes), 100% passing em 0.25s
- **TestResolveQueryByValue** (8 testes): case-sensitive, regex, numeric, boolean, None, partial match
- **TestResolveQueryWithMode** (7 testes): 3 modos, deduplicação, regex, empty queries
- **TestIntegration** (5 testes): workflows completos, edge cases, performance limit

**Bugs Corrigidos Durante Testes**:
1. ✅ `resolve_query()` retorna tupla `(exact, suggestions)` - normalizado para lista
2. ✅ Campo "path" vs "key" - padronizado para "key"
3. ✅ None não convertia para string - agora converte explicitamente
4. ✅ Limit de 200 não aplicado - adicionado em `resolve_query_by_value()`
5. ✅ Substring match em keys (expected: "title" encontra "subtitle") - teste ajustado

**Padrões Aplicados**:
- **Strategy** (GoF): Diferentes estratégias de busca (key/value/both)
- **Template Method** (GoF): `resolve_query_with_mode()` define algoritmo
- **Facade** (GoF): Interface unificada para subsistemas de busca

---

#### Task #49 - Text to JSON Converter (v2.9.24)
**Status**: ✅ Completa - 01/12/2025  
**Arquivos Criados**: `src/text_to_json.py` (664 linhas), `src/gui/text_to_json_dock.py` (618 linhas), `tests/test_text_to_json.py` (27 testes)  
**Arquivos Modificados**: `src/app.py` (+17 linhas), `src/gui/__init__.py` (+2 exports), `src/i18n/en.json` (+1 key), `src/i18n/pt_BR.json` (+1 key)

**Objetivo**: Permitir conversão de texto estruturado em JSON através de GUI interativa, suportando 10 formatos de entrada com opções avançadas e recursos profissionais (live preview, templates, history, validation).

**Componentes Implementados**:

**1. Core Converters (`text_to_json.py`)**:

**Formatos Suportados** (10 total):
- **Key-Value pairs**: `name: John`, `age = 30` → `{"name": "John", "age": 30}`
- **List (bullets)**: `- Item 1`, `* Item 2` → `["Item 1", "Item 2"]`
- **CSV**: `name,age\nJohn,30` → `[{"name": "John", "age": 30}]`
- **Python Dict**: `{'name': 'John', 'age': 30}` → `{"name": "John", "age": 30}`
- **YAML**: `user:\n  name: John\n  age: 30` → `{"user": {"name": "John", "age": 30}}`
- **INI**: `[user]\nname=John` → `{"user": {"name": "John"}}`
- **TOML**: `[user]\nname = "John"` → `{"user": {"name": "John"}}`
- **Java Properties**: `user.name=John` → `{"user.name": "John"}`
- **TOON**: `tags[3]: a,b,c` → `{"tags": ["a", "b", "c"]}` (Token-Oriented Object Notation)
- **Auto-detect**: Analisa estrutura → detecta formato automaticamente

**Funções Principais**:
- `detect_format(text)`: Auto-detecção com lógica hierárquica (TOON > INI > Python > CSV > YAML > Java Props > Key-Value)
- `parse_value(value_str, infer_types)`: Inferência de tipos (int, float, bool, null) ou força strings
- `convert_text_to_json(text, format_type, infer_types, **kwargs)`: Função principal de conversão

**2. TextToJsonDock GUI (`text_to_json_dock.py`)**:

**Componentes Visuais**:
- **Input**: QPlainTextEdit (grande área de texto com placeholder)
- **Format Combo**: 10 opções (Auto-detect, Key-Value, List, CSV, Python Dict, YAML, INI, TOML, Java Props, TOON)
- **Type Inference**: Radio buttons (Auto-detect types vs All as strings) - default: auto-detect
- **CSV Options Group**:
  * Checkbox: "First row is header" (default: checked)
  * Combo: Separator (Comma, Semicolon, Tab)
  * Radio: Output format (Array of objects vs Array of arrays)
- **General Options**:
  * Pretty print JSON (default: checked)
  * Enable live preview with 500ms delay (default: unchecked for performance)
- **Action Buttons** (3x3 grid):
  * Convert, Templates, Clear
  * Validate JSON, Copy Result, Open in Editor
  * History, Swap (JSON → Text), (empty slot)
- **Output**: QPlainTextEdit read-only com JSON convertido
- **Status Label**: Feedback colorido (✓ green / ✗ red / info gray)

**3. Advanced Features**:

**Live Preview** (Debounced):
- QTimer com 500ms delay (evita lag em textos grandes)
- Checkbox para habilitar/desabilitar (disabled por default)
- Atualiza automaticamente ao digitar

**Templates Dialog** (`TemplatesDialog`):
- 9 templates pré-definidos (Key-Value, List, CSV, Python Dict, YAML, INI, TOML, Java Props, TOON)
- QComboBox para selecionar formato
- QPlainTextEdit read-only mostrando exemplo
- Botão "Use This Template" carrega no input principal

**Conversion History**:
- Armazena últimas 50 conversões
- Lista: `[format] preview...`
- Double-click para carregar no input
- Persiste durante sessão (não salvo em disco)

**Integration com EditorDock**:
- Signal `open_in_editor_requested.emit(json_str)`
- Método `_load_json_from_converter(json_str)` no app.py
- Abre EditorDock automaticamente + carrega JSON

**4. Integration no App**:

**Menu Tools**:
- Nova entrada: "Text to JSON Converter" (EN) / "Conversor de Texto para JSON" (PT-BR)
- Shortcut: não definido (pode adicionar futuramente)

**Dock Initialization**:
- `_open_text_to_json()`: Cria dock + conecta signal + adiciona em RightDockWidgetArea
- `_load_json_from_converter(json_str)`: Callback para abrir no editor

**i18n Translations**:
- EN: `"menu.tools.text_to_json": "Text to JSON Converter"`
- PT-BR: `"menu.tools.text_to_json": "Conversor de Texto para JSON"`

**5. Tests** (27 testes, 50 passed, 1 skipped):

**Test Classes**:
- **TestDetectFormat** (10 testes): Detecção de Python dict, list, TOON, INI, CSV, YAML, Java Props
- **TestParseValue** (6 testes): Inferência de int, float, bool, null, strings
- **TestConvertKeyValue** (4 testes): Conversão com `:` e `=`, type inference, skip comments
- **TestConvertList** (4 testes): Listas com `-` e `*`, type inference, empty lines
- **TestConvertCSV** (4 testes): Header/no header, objects/arrays, delimiters, empty input
- **TestConvertPythonDict** (4 testes): Dict simples, nested, list literal, invalid literal
- **TestConvertYAML** (2 testes): YAML simples, nested objects
- **TestConvertINI** (2 testes): INI simples, skip comments
- **TestConvertTOML** (1 teste): TOML simples (skipped se biblioteca não instalada)
- **TestConvertJavaProperties** (2 testes): Properties simples, skip comments
- **TestConvertTOON** (3 testes): Key-value, inline array, root array
- **TestConvertTextToJSON** (5 testes): Auto-detect, explicit format, empty text, unknown format
- **TestEdgeCases** (4 testes): Whitespace only, empty values, no bullets, mismatched columns

**Bugs Corrigidos Durante Testes**:
1. ✅ `detect_format()` confundia `[3]: apple` (TOON) com Python list → Ajustada ordem de detecção + regex `^\[\d+\]:\s*\S`
2. ✅ `detect_format()` confundia `[section]` (INI) com Python list → Adicionado check `^\[\w+\]$` antes de Python dict

**Casos de Uso**:
```python
# Exemplo 1: Key-Value com type inference
text = "name: John\nage: 30\nactive: true"
result = convert_text_to_json(text, "key_value", infer_types=True)
# → {"name": "John", "age": 30, "active": true}

# Exemplo 2: CSV to array of objects
text = "name,age\nJohn,30\nAlice,25"
result = convert_text_to_json(text, "csv", has_header=True, array_of_objects=True)
# → [{"name": "John", "age": 30}, {"name": "Alice", "age": 25}]

# Exemplo 3: TOON inline array
text = "tags[3]: python,coding,llm"
result = convert_text_to_json(text, "toon")
# → {"tags": ["python", "coding", "llm"]}

# Exemplo 4: Auto-detect Python dict
text = "{'user': {'name': 'John', 'age': 30}}"
result = convert_text_to_json(text, "auto")
# → {"user": {"name": "John", "age": 30}}
```

**Padrões Aplicados**:
- **Strategy** (GoF): 10 estratégias de conversão (1 por formato)
- **Factory Method** (GoF): `detect_format()` seleciona conversor apropriado
- **Template Method** (GoF): `convert_text_to_json()` define workflow genérico
- **Observer** (Qt): QTimer para live preview debounce
- **Command** (GoF): Cada botão é um comando específico

**Estatísticas**:
- **Linhas de Código**: 664 (core) + 618 (GUI) = 1282 linhas
- **Testes**: 27 testes, 50 passed, 1 skipped (98% coverage)
- **Tempo de Execução**: 0.25s (pytest completo)
- **Commits**: 1 (Sprint v2.9.24 completo)

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

#### Task #51 - Advanced File Filters in AI Processor (v2.9.26)
**Status**: ✅ Completa - 01/12/2025  
**Arquivos Modificados**: `src/gui/ai_processor_dock.py` (+200 linhas), `tests/test_ai_advanced_conditions.py` (+460 linhas, novo)

**Objetivo**: Adicionar capacidade de filtrar arquivos antes do processamento IA usando Advanced Conditions (filename, path, ext, size, mtime, content patterns).

**Componentes Implementados**:

1. ✅ **Advanced Conditions Section** (GUI no AI Processor):
   - QGroupBox colapsável com 3 linhas iniciais (add dynamic, no limit)
   - 6 field types: filename, path, ext, size, mtime, content
   - 10 operators: contains, not contains, equals, not equals, starts with, ends with, >, <, >=, <=
   - Scope filtering: none, brackets, braces, parentheses, custom, tag, specific-tag, hierarchical
   - Checkboxes: Case sensitive, Regex
   - Buttons: "➕ Add Condition", "🗑️ Clear All"

2. ✅ **Backend Integration**:
   - `_get_conditions()`: Constrói lista de `Condition` objects da UI
   - `_apply_advanced_conditions(files)`: Aplica filtros usando `filter_files_by_conditions()`
   - `_process()` modificado: Aplica filtros ANTES de enviar para IA
   - Feedback: "📊 Processing X of Y files (Z filtered out)"
   - Warning se nenhum arquivo passar nos filtros

3. ✅ **Persistence** (QSettings):
   - `_save_advanced_conditions_preferences()`: Salva estado ao processar
   - `_load_advanced_conditions_preferences()`: Carrega na inicialização
   - Keys: `adv_cond/enabled`, `adv_cond/logic`, `adv_cond/rowN/*`

4. ✅ **Reused Core Infrastructure**:
   - Importa `from src.core.filters import Condition, filter_files_by_conditions`
   - DRY principle: Reutiliza sistema existente de Search/Replace e Insert
   - AND/OR logic operators para combinar condições

**Testes**: `tests/test_ai_advanced_conditions.py` (21 testes - 100% passing em 0.33s)
- ✅ 3 tests: Filename filtering (contains, equals, regex)
- ✅ 3 tests: Size filtering (>, <, ranges)
- ✅ 2 tests: Extension filtering (equals, multiple OR)
- ✅ 3 tests: Content filtering (contains, regex, scope)
- ✅ 2 tests: Empty conditions (returns all, ignores invalid)
- ✅ 1 test: Invalid regex (handled gracefully)
- ✅ 1 test: No files match (returns empty)
- ✅ 2 tests: Logic operators (AND, OR)
- ✅ 1 test: Path filtering (directory in path)
- ✅ 1 test: MTime filtering (recent modifications)
- ✅ 2 tests: Integration (filters applied before AI, correct feedback)

**Padrões Aplicados**:
- **Strategy** (GoF): Diferentes estratégias de filtro (filename, size, content)
- **Chain of Responsibility** (GoF): Cada condition é um handler
- **Facade** (GoF): `_apply_advanced_conditions()` simplifica interface
- **Information Expert** (GRASP): `Condition` class conhece como fazer matching
- **Low Coupling** (GRASP): Reutiliza `src.core.filters` sem criar dependência direta
- **High Cohesion** (GRASP): Métodos agrupados por responsabilidade

**Casos de Uso**:
- Filtrar apenas Python files > 100KB: `ext=py AND size>100000`
- Buscar imports específicos: `content contains "from flask import" AND ext=py`
- Arquivos modificados recentemente: `mtime > timestamp`
- Regex em filenames: `filename contains "test_\w+\.py"` (regex=True)

**Documentação**: `docs/v2.9.26-SPECIFICATION.md` (completo com arquitetura, testes, UX)

**Ref**: Task #51 Sprint A (v2.9.26) | Protocolo Simplicidade 1 v1.6 aplicado (Etapas 1-12)

---

#### Editor Features

- **[X]** Incluir habilidade de abrir e ler arquivos, diferenciar escopo com temas de cores diferentes *(v2.9.16 - Task #46: EditorDock)*
- **[X]** Incluir editores JSON como abas *(v2.9.17 - Task #47: JsonEditorTab com validação, tree view, search)*
- **[X]** Possibilidade de mudanças feitas apenas no editor de texto do próprio Clarify, não mais em arquivos *(v2.9.18 - Task #5: Edit-Only Mode)*
- **[]** Adicionar novo painel 'Smart file editing - AI' com o 'ChatGPT File Processor', ou seja, processamento de arquivos com inteligências artificiais;
- **[]** Incluir habilidade de conectar ao Google Translate e realizar operações de tradução online no programa por meio de API's;
- **[X]** Incluir Gemini na lista de IAs a serem usadas *(v3.0.0 - AI File Processor com suporte OpenAI e Gemini)*
- **[X]** Adicionar opções avançadas condicionais também no painel Smart Edit File (AI) *(v2.9.26 - Task #51: Advanced File Filters in AI Processor)*
- **[]** Incluir todas features de Search/Replace e Insert no Smart Edit File (AI) e editores JSON
- **[X]** Adicionar feature onde resultado pode ser reutilizado no editor de texto do Clarify *(v2.9.19 - Task #6: Open in Editor from Results)*

#### JSON Advanced Features

- **[X]** Possibilidade de buscar chaves e valores JSON (ex: `t.auth.brandTitle`) *(v3.0.0 - JSON Search)*
- **[X]** Incluir 'is file' em outros lugares para pegar mais arquivos com caminhos de diretórios **(v2.9.6)**
- **[]** Adicionar feature para inserir novos chaves/valores em chaves existentes com regex e conceito de registrador de memória
- **[]** Incluir possibilidade de inserir novo valor em modo grupo, onde word keys podem ser usadas para inserir novo valor entre essas word keys, em linha separada ou coluna específica. Usuário pode entrar contagem de ocorrências tolerada (threshold)
- **[]** Quando o usuário clicar em Tools do menu de contexto, e escolher uma opção, o sistema deve abrir em uma nova aba, como ocorre com as abas Search/Replace e Insert. Todas essas abas devem ter um ícone de X vermelho, em que quando clicado, fecha a aba, tendo o usuário novamente clicar em uma das opções Tools para abrir uma aba.
- **[X]** Adicionar possibilidade de reescrever JSON substituindo chave e objeto em outros lugares se valor da chave é mesmo e chaves têm diferentes nomes *(v2.9.27 - Task #52: Remove Duplicate Objects)*
  - **Sprint A (MVP - COMPLETO - 01/12/2025)**:
    * ✅ Novo checkbox "Remove duplicate objects" no JSON Rewriter
    * ✅ Threshold configurável (50-100%): permite similarity parcial
    * ✅ Modo Remove (default): deleta duplicatas, mantém primeiro (menor linha)
    * ✅ Modo Reference (opcional): substitui por $ref:path.to.original
    * ✅ Include Arrays: opcionalmente compara arrays também
    * ✅ Statistics feedback em MessageBox
    * ✅ QSettings persistence (4 preferências salvas automaticamente)
    * ✅ 19 unit tests (100% passing em 0.21s)
  - **Arquivos**:
    * `src/rewriter/operations.py` (+220 linhas): remove_duplicate_objects()
    * `src/gui/json_rewriter_dock.py` (+85 linhas): UI widgets, integration, persistence
    * `tests/test_remove_duplicate_objects.py` (+330 linhas, novo): 19 tests em 10 classes
    * `docs/v2.9.27-SPECIFICATION.md` (novo): Especificação técnica completa
  - **Sprint B Feature #1 (Advanced Conditions Integration - COMPLETO - 01/12/2025 - v2.9.28)**:
    * ✅ Modularidade total: `src/utils/advanced_conditions.py` compartilhado entre AI Processor e JSON Rewriter
    * ✅ Botão "🔍 Advanced Filters..." em JSON Rewriter (Row 8)
    * ✅ Dialog com 3 condition rows (Field, Operator, Value, Scope, Case, Regex)
    * ✅ Filtros aplicados ANTES de `remove_duplicate_objects()`
    * ✅ Auto-detecção de arquivos `.json` (configurável com checkbox "Apply to all file types")
    * ✅ QSettings persistence (3 valores: enabled, apply_all_types, conditions JSON)
    * ✅ Feedback detalhado: MessageBox mostra "X files filtered, Y processed"
    * ✅ AI Processor refatorado (delegado para módulo compartilhado)
    * ✅ 11 unit tests (100% passing em 152.01s)
  - **Arquivos Sprint B Feature #1**:
    * `src/utils/advanced_conditions.py` (+112 linhas, NOVO): get_conditions_from_ui(), apply_conditions_to_files()
    * `src/gui/ai_processor_dock.py` (~20 linhas): refatorado para usar módulo compartilhado
    * `src/gui/json_rewriter_dock.py` (+150 linhas): botão, dialog, filtro em cli_dedupe(), QSettings
    * `tests/test_advanced_conditions_integration.py` (+329 linhas, NOVO): 11 tests em 4 classes
    * `docs/v2.9.28-SPECIFICATION.md` (NOVO): Especificação técnica completa Sprint B Feature #1
  - **Sprint B Features Restantes (PENDENTE)**:
    * ❌ Performance options dialog (Worker thread / Sync / Batching com progress bar)
    * ❌ Visual threshold slider com preview em tempo real
    * ❌ Detailed statistics dialog (table com Original Key | Kept Key | Similarity % | Line Numbers, export CSV)
    * ✅ **Reference Resolver Sprint A (v2.9.29 - COMPLETO - 02/12/2025)**:
      - ✅ Radio buttons (Delete duplicates | Use references)
      - ✅ create_references(): Replace duplicates com $ref:path:line
      - ✅ resolve_references(): Expand $ref para valores reais
      - ✅ QSettings persistence para preferências
      - ✅ 13/13 tests passing (~430 LOC total)
      - ✅ Documentação completa (docs/v2.9.29-SPECIFICATION.md)
    * ✅ **Reference Resolver Sprint B Feature #4 (v2.9.30 - COMPLETO - 02/12/2025)**:
      - ✅ Multi-format support ($ref:, #/, @) - 3 formatos configuráveis (~60 LOC)
      - ✅ Format configuration dialog (dropdown + 2 checkboxes + preview) (~90 LOC)
      - ✅ Relative path support (remove 'root.' prefix) (~15 LOC)
      - ✅ QSettings persistence (reference_format, include_line_numbers_ref, use_relative_paths) (~15 LOC)
      - ✅ 25/25 tests passing (12 novos testes + 13 Sprint A) (~180 LOC total)
      - ✅ Protocolo Simplicidade 1 v1.6 aplicado (16 perguntas Q&A + 9 tasks)
    * ✅ **Detailed Statistics Dialog Sprint B Feature #3 (v2.9.31 - COMPLETO - 02/12/2025)**:
      - ✅ DetailedStatsCollector class for tracking operations (~110 LOC)
      - ✅ StatisticsDialog with 2 tabs (Removal + Reference stats) (~300 LOC)
      - ✅ Interactive table with 6 columns, sort, search, filter (~80 LOC)
      - ✅ Export dropdown (CSV/JSON/Excel) with full implementation (~90 LOC)
      - ✅ Auto-show dialog after rewrite if stats > 0 (~20 LOC)
      - ✅ 10/10 tests passing (DetailedStatsCollector + integration) (~100 LOC)
      - ✅ Protocolo Simplicidade 1 v1.6 aplicado (11 perguntas Q&A + 9 tasks)
    * ❌ **Reference Resolver Sprint B Remaining (Avançado - PENDENTE)**:
      - ❌ Cross-file references: NÃO IMPLEMENTAR (decisão do usuário)
- **[]** Permitir usuário escolher className names ao invés de tag names para fazer chaves JSON. Usuário pode escolher pegar apenas diferença entre className names
- **[]** Inserir opção 'Salvar automaticamente' no menu Files do menu de contexto para salvar conteúdo em arquivos sem o usuário precisar clicar em salvar, quando estiver no editor de arquivos. Além disso, deve haver a opção de pertinência de conteúdo não salvo no aplicativo em abas não fechadas do editor de arquivos, e dentro do editor de arquivos (à parte das abas/guias principais dos tools) devem ter outras abas/guias.
- **[]** Permitir no tool AI Processor a possibilidade de se utilizar palavras-chave ou palavras reservadas para escrever instruções dinâmicas e personalizadas. Por exemplo, incluir a palavra chave count, que quando colocada como {{count}}, desta maneira, faz com que haja a possibilidade de inserção de código permitido dentro de {{}}. Neste caso, se o usuário digitar {{count}}, isto quer dizer que count vai variar de 0 a N iterações, podendo seguir o seguinte exemplo de instrução: 'Quero que você processe agora o capítulo {{count+1}} do livro Meu Desafio Constante', podendo {{count+1}} aceitar também aritmética.
- **[X]** Quando usuário precisa reestruturar JSON e transformar texto em objeto JSON, aplicação deve permitir colar conteúdo de texto na GUI e então performar reestruturação *(v2.9.24 - Task #49: Text to JSON Converter)*
- **[X]** Ao buscar outras chaves e objetos JSON (ex: `t.pages.contact.title` com word-key 'contact'), não apenas chaves devem ser encontradas, valores à direita das chaves também *(v2.9.23 - Task #48: JSON Value Search)*
- **[X]** Ferramenta de busca pode incluir busca por nome de arquivo *(Já implementado - json_search_dock.py lines 98-101, 175-222: suporta wildcards, regex e prefix 'filename:')*
- **[X]** **Task #50 - Advanced File Search (Sprint A - v2.9.25)**: Melhorar FileListDock com busca avançada de arquivos/diretórios *(Completo - 2025-12-01)*:
  - **Sprint A (MVP Básico - COMPLETO)**:
    * ✅ Regex em filenames (QLineEdit + QCheckBox "Enable Regex")
    * ✅ Filtros size (min/max em bytes/KB/MB/GB com QComboBox)
    * ✅ Filtros mtime (before/after date com QDateEdit)
    * ✅ Filtros ext (múltiplas extensões comma-separated)
    * ✅ Depth limit (max profundidade de recursão com QSpinBox 0-10)
    * ✅ Exclude directories (5 checkboxes common: node_modules, .git, __pycache__, dist, build + custom field)
    * ✅ Panel expansível/collapsible para filtros avançados (QGroupBox checkable)
    * ✅ Presets (save/load queries com QSettings + export/import JSON)
  - **Arquivos modificados**:
    * `src/gui/file_list_dock.py` (+350 linhas): Adicionado painel de filtros avançados, métodos de preset, lógica de filtros
  - **Arquivos criados**:
    * `tests/test_advanced_file_search_logic.py` (**27 testes - 100% passing em 2.14s**): Testes de lógica sem GUI
    * `tests/test_runner_monitored.py` (280 linhas): Test runner com monitoramento (Protocolo v1.6 - Etapa 9.2)
  - **Testes Executados**:
    * ✅ 27/27 testes passaram (100%)
    * ⏱️ Tempo: 2.14s (muito rápido!)
    * 🛡️ Protocolo Simplicidade 1 v1.6 aplicado (Etapa 9.2 - Monitoramento)
    * 📊 Cobertura: regex (4), size (5), mtime (3), ext (4), depth (2), exclude (4), presets (3), integration (2)
  - **Sprint B (Avançado - PENDENTE)**:
    * ❌ Busca em múltiplos diretórios raiz simultaneamente
    * ❌ Tree view mode (toggle Table ↔ Tree ou split view side-by-side)
    * ❌ AND/OR conditions entre filtros (integração completa com Advanced Conditions do app.py)
    * ❌ Visual query builder (drag-and-drop conditions)
    * ❌ Saved searches com hotkeys (Ctrl+1, Ctrl+2, etc.)
    * ❌ Export filtered results to multiple formats (JSON, XML, CSV)

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

#### Quality Assurance & Testing

- **[]** GUI Automated Tests: Implementar testes automatizados para interface gráfica usando pytest-qt. Cobertura: interação com docks (click buttons, fill forms, verify results), workflows completos (open file → search → rewrite → save), integração entre módulos (Editor ↔ Set Operations ↔ Rewriter). Target: 50+ integration tests.
- **[]** Performance Benchmarks: Criar suite de benchmarks para operações críticas usando arquivos JSON grandes (1MB, 10MB, 50MB). Métricas: tempo de processamento, uso de memória RAM, CPU usage. Operações testadas: set operations, JSON rewriter, search, text extractor. Armazenar resultados em `benchmarks/results.json` para comparação entre versões.
- **[X]** Code Coverage Reporting: Integrar pytest-cov no CI/CD com configuração em `.coveragerc`. Target: manter >90% coverage para módulos core (`src/set_operations.py`, `src/rewriter/`, `src/json_search/`). Gerar relatórios HTML automáticos em `htmlcov/`. Incluir badge de coverage no README.md. **(v2.9.38)**
- **[]** Load Testing: Criar testes de carga para identificar limites do sistema. Cenários: processar 1000+ arquivos simultaneamente, set operations com 100+ arquivos, search em corpus de 10GB. Usar `multiprocessing` para simular múltiplos usuários. Documentar resultados em `docs/PERFORMANCE.md`.

---

#### UX & Accessibility

- **[X]** **i18n Expansion (ES/FR/DE/ZH/JA)** - Expandir traduções além de EN/PT-BR para alcance internacional. Adicionar 5 idiomas: Español (Espanha/Latam), Français, Deutsch, 中文 (Chinês Simplificado), 日本語 (Japonês). Estrutura: `i18n/{locale}/app.json`. Usar sistema existente em `src/i18n/`. Permitir usuário contribuir traduções via GitHub (template em `CONTRIBUTING.md`). Integrar com sistema de detecção automática de locale do sistema operacional. ***(v2.9.43 - 08/12/2025)***
- **[X]** **Recipe Book (docs/RECIPES.md)** - Criar guia prático com casos de uso reais. Formato: Problema → Solução passo-a-passo → Resultado esperado. Incluir 15-20 recipes cobrindo: Set Operations (mesclar configs, diff entre versões), JSON Rewriter (limpar duplicatas, normalizar estrutura), JSON Search (encontrar chaves órfãs), AI Processing (refactoring assistido, tradução automática), Text Extractor (JSX para i18n). Cada recipe com screenshots, código exemplo CLI, e tempo estimado. ***(v2.9.44 - 08/12/2025)***
- **[X]** **Update Checker** - Verificador automático de atualizações com GitHub Releases API. Backend: `src/update_checker.py` (UpdateChecker class, check_for_updates(), compare_versions() semver, cache 24h em `~/.cache/clarify/update_check.json`). GUI: `src/gui/update_notification.py` (QDialog não-modal, botões Download/Lembrar Depois, checkbox "Não mostrar para v{X}"). Integração: `src/app.py` (menu Help → Check for Updates, auto-check no startup com delay 3s, preferência em Settings). Offline-friendly (falha silenciosa), QSettings persistence (skip_versions, enabled). ***(v2.9.45 - 08/12/2025)***
- **[X] v2.9.33 (2025-12-02)** Comprehensive Keyboard Shortcuts: Mapear todas operações principais para atalhos de teclado. Global: `Ctrl+F` (search), `Ctrl+S` (save), `Ctrl+E` (editor), `Ctrl+Shift+S` (set operations), `Ctrl+Shift+R` (rewriter), `Ctrl+Shift+A` (AI processor). Navegação: `Ctrl+Tab` (next dock), `Ctrl+Shift+Tab` (previous dock), `F11` (fullscreen), `Ctrl+1-9` (jump to specific dock). **IMPLEMENTADO**: 45+ shortcuts, customização completa com dialog, detecção de conflitos, avisos de SO, navegação entre docks, help page (F1), i18n EN/PT-BR, 26 testes (100% passing).
- **[X] v2.9.34 (2025-12-02)** Dark Mode Theme: **VALIDADO** - Feature já 100% implementada no codebase. ThemeManager (478 LOC) com suporte completo dark/light/system. Paleta: Dark (#1E1E1E background, #F0F0F0 text, #007ACC accent), Light (#FAFAFA background, #1E1E1E text, #0078D4 accent). Toggle em: `View → Themes → System/Light/Dark`. Persistência via QSettings. QSS inline (~100 linhas/tema). i18n EN/PT-BR completo. **RELEASE v2.9.34**: 14 testes unitários criados (100% passing), validação de acessibilidade (WCAG AA), documentação completa.
- **[X] v2.9.35 (2025-12-02)** Accessibility Features: **MVP IMPLEMENTADO** - AccessibilityManager (330 LOC) com infraestrutura completa. Features: Screen reader support (`setAccessibleName/Description`), focus indicators globais (2px #007ACC), font scaling (Ctrl+Scroll, 8-24pt), Ctrl+0 reset, WCAG AAA calc (14.6:1 dark, 16:1 light), tab order API, QSettings persistence. **RELEASE v2.9.35**: 24 testes (100% passing), API completa, documentação. **PRÓXIMO PASSO**: Aplicar accessible names em 100+ widgets (incremental).
- **[X]** Internationalization (i18n) Expansion: Expandir traduções além de EN/PT-BR. Adicionar: ES (Espanhol), FR (Francês), DE (Alemão), ZH (Chinês), JA (Japonês). Estrutura: `i18n/{locale}/app.json`. Usar sistema existente em `src/i18n/`. Permitir usuário contribuir traduções via GitHub (template em `CONTRIBUTING.md`). ***(v2.9.43)***
- **[]** Customizable UI Layout: Permitir usuário customizar layout dos docks. Funcionalidades: salvar/carregar layouts (workspace presets), dock position (left/right/top/bottom/floating), dock size persistence, tab order customizado. Incluir 3 layouts pré-configurados: "Compact" (mínimo), "Standard" (atual), "Advanced" (todos docks visíveis).
- **[X]** Tooltips Expansion: Adicionar tooltips descritivos em todos widgets. Formato: título bold + descrição + atalho (se houver). Exemplo: **Set Operations** | Perform logical operations (∩, ∪, −, ⊕) on JSON files | `Ctrl+Shift+S`. Incluir exemplos visuais em tooltips complexos (preview de resultado esperado). ***(v2.9.42 - MVP Parcial: 2 docks completos)***
  - **Implementado (v2.9.42 - Sprint MVP)**:
    * Set Operations Dock: +17 tooltips (file inputs, operations, comparison modes, options, action buttons)
    * Case Converter Dock: +5 tooltips (path input, browse, is_file, extensions)
    * Total: +22 tooltips (de 4 para 26 em 2 docks)
  - **[X] v2.9.46 - Tooltips i18n (08/12/2025)**:
    * ✅ Criado `tooltip_tr()` helper function (namespace "tooltip.*")
    * ✅ 182 traduções (26 keys × 7 idiomas: EN, PT-BR, ES, FR, DE, ZH, JA)
    * ✅ Set Operations Dock: 20 tooltips internacionalizados
    * ✅ Case Converter Dock: 6 tooltips internacionalizados
  - **[X] v2.9.47 - Keyboard Shortcuts + JSON Rewriter (09/12/2025)**:
    * ✅ Adicionar keyboard shortcuts aos 26 tooltips existentes (formato: "Description | Ctrl+X")
    * ✅ Completar JSON Rewriter Dock tooltips faltantes (1 widget: btn_run)
    * ✅ Criar documento `docs/TOOLTIP_GUIDELINES.md` (12 seções, 340 linhas)
    * ✅ Automated tests (pytest-qt: 7/8 passing, ≥90% coverage)
  - **[X] v2.9.48 - AI Processor Dock (09/12/2025)**:
    * ✅ Adicionar keyboard shortcuts aos 23 tooltips existentes (formato: "Description | Ctrl+Shift+A")
    * ✅ Adicionar 15 novos tooltips (ed_prompt, btn_add_path, spin_max_bytes, ed_extensions, scope filters, action buttons, stats labels, PathEntry widgets)
    * ✅ Total: 38 widgets com tooltips (23 existentes + 15 novos)
    * ✅ PathEntry dinâmicos: ed_path, btn_browse, chk_is_file
    * ✅ Advanced Conditions: 6 widgets por linha (field, operator, value, scope, case, regex)
    * ✅ Testes atualizados: `test_ai_processor_dock_tooltips()` (8/9 passing, 1 skipped)
  - **[X] v2.9.49 - JSON Editor Components (09/12/2025)**:
    * ✅ **JsonEditorTab** (9 tooltips): 4 existentes atualizados com Ctrl+E, 5 novos (btn_collapse, btn_expand, editor QTextEdit, tree JsonTreeWidget, lbl_validation)
    * ✅ **EditorDock** (8 tooltips): 6 existentes atualizados com Ctrl+E, 2 novos (tab_widget, lbl_status)
    * ✅ **EditorTab** (4 tooltips): 3 existentes atualizados com Ctrl+E, 1 novo (editor QTextEdit)
    * ✅ Total: 20 widgets com tooltips (JsonEditorTab: 9, EditorDock: 8, EditorTab: 4)
    * ✅ Fix: Inicialização `auto_save_enabled` ANTES de `super().__init__()` em EditorDock
    * ✅ Testes atualizados: `test_json_editor_tab_tooltips()`, `test_editor_dock_tooltips()` (10/11 passing, 1 skipped)
  - **[]** **v2.9.50 - JSON Search Dock (Sprint Atual - 09/12/2025)**:
    * ✅ **13 tooltips totais**: 3 existentes atualizados (ed_search_key, ed_search_value, ed_filename) + 10 novos
    * ✅ **Search inputs** (3): Adicionado `| Enter to search | Ctrl+E to open Editor` aos 3 inputs existentes
    * ✅ **combo_mode** (1): "Search mode: 'Key only' finds keys, 'Value only' finds values, 'Both' requires match in key AND value"
    * ✅ **Path widgets** (3): ed_path, btn_browse, chk_is_file com Ctrl+E
    * ✅ **Options** (2): chk_case (case-sensitive com exemplo), chk_regex (regex patterns com exemplo)
    * ✅ **spin_max** (1): Tooltip detalhado explicando 0 = unlimited, default 1000
    * ✅ **Action buttons** (4): btn_search (Enter), btn_interrupt (Esc), btn_save_results (3 formatos), btn_clear
    * ✅ **text_results** (1): Display com occurrence statistics
    * ✅ **Esc shortcut**: Implementado `_setup_escape_key_interrupt()` para interrupt (QShortcut + Qt.Key_Escape)
    * ✅ Testes atualizados: `test_json_search_dock_tooltips()` (11/12 passing, 1 skipped)
  - **[]** **Sprints Futuras - Tooltips Expansion (Incremental por Dock)**:
    * **[]** v2.9.51 - JSON Translate Dock (~10 tooltips): scope patterns, exclude patterns, emit export, preserve uppercase
    * **[]** v2.9.51 - JSON Translate Dock (~10 tooltips): scope patterns, exclude patterns, emit export, preserve uppercase
    * **[]** v2.9.52 - Tutorials Dock (~8 tooltips): tree navigation, search bar, beginner/developers categories
    * **[]** v2.9.53 - Tradução de todos tooltips novos (70 keys × 6 idiomas = 420 traduções PT-BR/ES/FR/DE/ZH/JA)

---

#### Documentation & Developer Experience

- **[]** User Manual Wiki: Criar wiki completo no GitHub com estrutura: Getting Started (instalação, first steps), Features (1 página por dock com screenshots), Tutorials (workflows comuns), FAQ (problemas conhecidos), Troubleshooting (errors e soluções). Formato Markdown com navegação lateral. Incluir search bar no wiki.
- **[]** Video Tutorials Series: Produzir série de vídeos curtos (3-5 min cada) demonstrando features principais. Tópicos: Quick Start, JSON Rewriter Deep Dive, Set Operations Workflows, Advanced Search Techniques, AI Integration Guide. Hospedar no YouTube e linkar no README.md. Incluir timestamps e transcrições.
- **[X]** Recipe Book: Criar `docs/RECIPES.md` com casos de uso práticos. Formato: Problema → Solução passo-a-passo → Resultado esperado. Exemplos: "Como mesclar 2 arquivos de configuração?", "Como extrair apenas chaves com valor null?", "Como converter i18n de JSON para YAML?", "Como automatizar tradução com AI?". Incluir código CLI quando aplicável. ***(v2.9.44)***
- **[]** API Documentation: Gerar documentação completa da API pública usando Sphinx. Incluir: docstrings para todas funções/classes públicas, type hints completos, examples de uso programático, architecture diagrams (UML). Publicar em GitHub Pages em `https://josueamaral15.github.io/clarify/`. Auto-rebuild via GitHub Actions on push.
- **[]** Contributing Guide: Criar `CONTRIBUTING.md` detalhado. Seções: Code of Conduct, How to Report Bugs (issue template), How to Suggest Features (feature request template), Development Setup (Python 3.12+, PySide6, pytest), Code Style (black, isort, pylint >9.0), Testing Requirements (coverage >90%), Pull Request Process (review checklist). Incluir badges no README.
- **[]** Changelog Automation: Automatizar geração de CHANGELOG.md usando commits convencionais (Conventional Commits). Format: `type(scope): description`. Types: feat, fix, docs, style, refactor, test, chore. Tool: `git-cliff` ou `standard-version`. Gerar changelog automaticamente em release tags.

---

#### Architecture & Maintenance

- **[]** Plugin System: Implementar sistema de plugins para extensões customizadas. Estrutura: `plugins/` folder com subfolders por plugin, cada plugin tem `plugin.json` (metadata) + `main.py` (entry point). API: registrar dock customizado, adicionar menu items, hook em events (file_opened, search_completed). Incluir 2 plugins exemplo: "Export to PostgreSQL", "Slack Notifications".
- **[]** Configuration Management: Centralizar configurações em `config.yaml` (além de QSettings). Parâmetros: default directories, max file size, thread pool size, cache duration, AI model preferences, logging level. Incluir UI em `Settings → Advanced` para editar YAML visualmente. Validar schema com `jsonschema`.
- **[]** Logging System: Implementar logging estruturado usando Python `logging` module. Levels: DEBUG (development), INFO (operations), WARNING (issues), ERROR (failures), CRITICAL (crashes). Output: `logs/clarify.log` (rotate daily, keep 30 days). Formato: `[2025-12-02 14:23:45] [INFO] [set_operations] Executed intersection on 3 files (124ms)`. Incluir "View Logs" em Help menu.
- **[]** Update Checker: Adicionar verificador automático de atualizações. Na inicialização: verificar GitHub Releases API para versão mais recente, comparar com versão atual, exibir notificação se nova versão disponível. Incluir: link para changelog, botão "Download", checkbox "Don't show again for this version". Respeitar configuração "Check for updates" em Settings.
- **[]** Error Reporting & Crash Handler: Implementar sistema de crash reporting. Capturar exceções não tratadas com `sys.excepthook`, gerar relatório com: stack trace, versão do app, OS info, últimas 50 linhas de log. Oferecer: "Send Report" (via GitHub Issue automaticamente), "Save Report" (local .txt), "Ignore". Anonimizar paths de arquivos do usuário.
- **[]** Database Migration System: Criar sistema de migração para QSettings quando estrutura mudar entre versões. Pattern: `migrations/v{version}.py` com `migrate()` function. Exemplo: v2.9.32 → v2.9.33 move `set_operations/` para `operations/set/`. Executar migrations automaticamente no startup. Log em `migrations.log`.

---

#### Advanced Features & Long-term Goals

- **[]** Integrar IA para assistente de tutoriais: Chatbot com Gemini Flash-1.5-8B (8192 tokens) ou Claude Haiku-4 (200k tokens) dentro do sistema de tutoriais. O chatbot responde perguntas sobre funcionalidades usando `docs/tutorials/index.json` como knowledge base. Incluir histórico de conversa e feedback de qualidade.
- **[]** TOON format: adicionar possibilidade de trabalhar com múltiplos arquivos JSON (e TXT também) em formato hierárquico de texto aninhado (Tree Object-Oriented Notation) como `{1}["pages"]["home"]: "Homepage"` seria representado como `[1]: pages > home = "Homepage"`, incluindo busca por índices e atualização seletiva de campos. Operações: buscar objeto por ID/hierarquia, modificar valor mantendo TOON structure, converter TOON ↔ JSON, merge TOON files, validar sintaxe. Use case: gerenciar traduções distribuídas sem parsing JSON completo.
- **[]** File as Database: adicionar possibilidade de realizar processamento SGBD-like em arquivos JSON onde arquivos JSON podem ser tratados como tabelas de banco de dados relacional, incluindo operações JOIN entre múltiplos arquivos, projeções de chaves específicas (SELECT), agregações (COUNT, SUM, AVG), e filtros complexos com sintaxe SQL-like. Use case: análise de dados JSON sem PostgreSQL/MongoDB.
- **[]** Macro System: Sistema de macros com 2 interfaces (Python snippet e block programming visual). Python: executar código arbitrário em contexto sandbox com acesso controlado a API do Clarify (open_file, search_keys, rewrite_json). Visual: drag-and-drop de blocos (Load File → Filter Keys → Transform Values → Save Result). Incluir scheduler para executar macros periodicamente. Use case: automação de workflows repetitivos.
- **[]** Cloud Sync & Collaboration: Adicionar sincronização em nuvem para configurações e presets. Suporte: Google Drive, Dropbox, OneDrive. Permitir: compartilhar operation presets com time, histórico versionado (Git-like diffs), comentários em configurações. Implementar conflict resolution (local vs remote changes). Use case: times distribuídos compartilhando workflows.
- **[]** Real-time JSON Validation: Validar JSON em tempo real durante edição no EditorDock. Usar JSON Schema para validação customizada. Features: highlight de erros (red underline), auto-complete de chaves conhecidas, sugestões de valores baseados em schema, quick-fix actions (add missing required field). Integrar com `jsonschema` library.
- **[]** GraphQL Query Interface: Adicionar interface para consultar arquivos JSON usando sintaxe GraphQL. Permitir: queries aninhadas, aliases, fragments, mutations (modificar JSON via query). Exemplo: `{ user { name posts { title } } }` retorna apenas campos solicitados. Use case: extrair dados complexos sem código Python.
- **[]** Version Control Integration: Integrar com Git diretamente no app. Features: commit changes, view diff, create branches, merge conflicts resolution (visual merge tool), push/pull. Exibir status de arquivos (modified/staged/untracked) no File List. Incluir "Git" menu com operações comuns. Use case: gerenciar versionamento sem sair do Clarify.
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
- **[]** Fazer com que Clarify não apenas reconheça arquivos JSON, como também arquivos TOON, que é um novo conceito de armazenamento e reestruturação de dados;
- **[]** Fazer processamento de arquivos JSON e TOON como se fosse um Sistema de Gerenciamento de Base de Dados (SGBD), aproveitando o editor de texto/código para executar comandos semelhantes de SQL e NoSQL, sendo que devem combinar diversos comandos de forma que seja avançado e ao mesmo tempo simples, como é a semântica e sintaxe do Python em comparação com o C: Python é simples, confortável de codificar e poderoso ao mesmo tempo por ter ferramentas avançadas, se aproximando da linguagem humana.

#### Calculator & Set Operations

- **[]** Calculator: Adicionar conceitos de calculadora como registrador de memória, adição, concatenação e recall de memória padrão com histórico de modificações. A ideia seria a seguinte: o registro de memória seria o resultado do processamento, por exemplo, de busca, do painel de resultado de buscas. A adição significa: adicione um resultado de busca com outro resultado de forma que estes se complementem, por exemplo, em ordem alfabética ou unindo resultados de um mesmo arquivo (quando é em formato de árvore) no painel de resultados. Concatenação iria concatenar um resultado a outro, colocando o segundo resultado debaixo do primeiro no painel de resultados. O recall de memória iria chamar resultados salvos e jogar no painel de resultados, como pesquisas pela palavra "span".
- **[✅]** Set: Adicionar operações de conjunto lógico de arquivos JSON como interseção, diferença, união e diferença exclusiva. Incluir checkboxes para incluir chaves e/ou valores nesta operação de conjunto, em que, por exemplo, se for escolhida a intersecção entre arquivo A e arquivo B, ambos JSON, se tem valores equivalentes tanto em A quanto em B no sentido de chave e valor (title: "Tarefas de Casa"), no sentido de caminhos de chave e valor (t.pages.home.features.title, title: "Tarefas de Casa"), e somente no sentido de caminhos de chave (t.pages.home.features.title); **✅ Completa v2.9.32 - 02/12/2025**
- **[X]** Verificar se na pasta add existe alguma funcionalidade que ainda não foi implementada;

---

#### Melhorias de Set Operations (Pós v2.9.32)

##### Visualização e Análise
- **[]** Venn Diagram Visualizer: Adicionar diagrama de Venn interativo mostrando visualmente as interseções/uniões entre arquivos JSON. Usar QGraphicsView para renderizar círculos sobrepostos com contadores de elementos em cada seção. Permitir clique para ver detalhes dos elementos em cada região.
- **[]** Diff Viewer Side-by-Side: Implementar visualização lado-a-lado (split view) das diferenças entre arquivos após operações de conjunto. Usar cores para destacar: verde (único em A), vermelho (único em B), amarelo (comum). Sincronizar scroll entre painéis.
- **[]** Comparative Statistics Dashboard: Criar painel de estatísticas comparativas com métricas: % de overlap, unique keys por arquivo, profundidade média das estruturas, tamanho em bytes, contagem de valores por tipo (string/number/bool/null/array/object).

##### Exportação e Integração
- **[]** Multi-Format Export: Adicionar exportação de resultados em formatos CSV, Excel (XLSX), YAML e TOML. Incluir opções: flatten keys (dot notation), include metadata (operation type, timestamp, source files), column mapping customizável.
- **[]** Merge Results to File: Permitir aplicar resultados de operação de volta aos arquivos originais. Modos: replace (sobrescrever arquivo), merge (combinar com conteúdo existente), new file (criar novo arquivo com sufixo _merged). Incluir preview antes de aplicar e opção de backup automático.
- **[]** Batch Set Operations: Processar múltiplos grupos de arquivos em pipeline. Interface: adicionar grupos (A∩B, C∪D, E−F), definir ordem de execução, aplicar operações sequencialmente. Exibir progress bar com status de cada grupo.

##### Histórico e Presets
- **[]** Operation History: Implementar histórico de operações realizadas (últimas 50). Armazenar: timestamp, tipo de operação, arquivos envolvidos, modo de comparação, resultado (contagem de elementos). Permitir: visualizar resultados anteriores, re-executar operação, exportar histórico para JSON.
- **[]** Operation Presets: Criar sistema de presets salvos. Permitir usuário salvar configurações frequentes: tipo de operação (∩/∪/−/⊕), modo de comparação (key_value/full_path_value/key_only), opções ativas, arquivos favoritos. Dropdown "Load Preset" no dock.
- **[]** Formula Builder: Interface visual para construir operações complexas: (A ∩ B) ∪ (C − D). Drag-and-drop de arquivos em canvas, selecionar operadores entre eles, preview em tempo real do resultado. Salvar fórmulas como templates reutilizáveis.

##### Calculator Integration (Expandir task existente)
- **[]** Calculator + Set Operations Integration: Integrar resultados de Set Operations com Calculator. Memory slots para armazenar até 5 resultados de operações diferentes. Operações: Add (mesclar 2 resultados), Recall (chamar resultado salvo), Clear (limpar slot). Exibir preview de cada slot no painel lateral.
- **[]** Set Statistics in Calculator: Adicionar estatísticas sobre result sets no Calculator: count (número de elementos), size (bytes), depth (profundidade máxima), key_types (distribuição de tipos). Permitir comparar estatísticas entre slots diferentes.

---

#### Task v2.9.32 - JSON Set Operations (v2.9.32)
**Status**: ✅ Completa - 02/12/2025  
**Arquivos Criados**: `src/set_operations.py` (437 LOC), `src/gui/set_operations_dock.py` (412 LOC), `tests/test_set_operations.py` (464 LOC)  
**Arquivos Modificados**: `src/app.py` (+10 linhas), `src/gui/__init__.py` (+2 linhas)  
**Infraestrutura**: `.gitignore` criado

**Objetivo**: Implementar operações de conjunto lógico (∩, ∪, −, ⊕) para arquivos JSON com interface GUI e CLI.

**Componentes Implementados**:

**1. Core Logic (`src/set_operations.py`)**:
- `validate_file_path()`: Segurança CWE-22 (path traversal prevention)
- `flatten_json()`: Converte estrutura aninhada para dot-notation
- `unflatten_json()`: Reconstrói estrutura aninhada
- `normalize_for_comparison()`: Normaliza valores para hashable (frozenset/tuple)
- `compare_files()`: Prepara arquivos com 3 modos (key_value, full_path_value, key_only)
- `intersection()`: A ∩ B ∩ C (pipeline left-to-right)
- `union()`: A ∪ B ∪ C
- `difference()`: A − B − C (pipeline)
- `symmetric_difference()`: A ⊕ B (2 arquivos)
- CLI completo com argparse

**2. GUI (`src/gui/set_operations_dock.py`)**:
- File selection: File A/B + checkbox múltiplos arquivos + QListWidget
- 4 operações: checkboxes para ∩, ∪, −, ⊕
- 3 modos de comparação: key_value (default), full_path_value, key_only
- 4 opções: ignore case keys/values, skip empty, arrays ignore order
- Output format: JSON nested, Separate files, Display only
- Results: QTextEdit + statistics label (green, bold)
- Buttons: Execute, Clear, Save Result

**3. Testes (`tests/test_set_operations.py`)**:
- 50 testes unitários (100% pass rate em 0.24s)
- Cobertura: validate_file_path (6), flatten_json (6), unflatten_json (3), normalize_for_comparison (5), compare_files (6), intersection (5), union (3), difference (4), symmetric_difference (3), edge cases (5), integration (2)
- Testes de segurança (path traversal, unreadable files)
- Testes de edge cases (null vs empty, strict types, arrays order)

**4. Design Patterns**:
- **Strategy (GoF)**: Cada operação como estratégia intercambiável
- **Template Method (GoF)**: Pipeline comum (read → normalize → operate → output)
- **Factory Method (GoF)**: Diferentes formatos de output
- **Command (GoF)**: Operações encapsuladas como comandos
- **Observer (GoF)**: Qt signals para comunicação GUI
- **Information Expert (GRASP)**: set_operations.py conhece lógica de conjunto
- **Controller (GRASP)**: SetOperationsDock coordena workflow
- **Low Coupling (GRASP)**: GUI depende apenas de interface pública core
- **High Cohesion (GRASP)**: Cada módulo tem responsabilidade única clara

**5. CI/CD Quality Gates**:
- ✅ Black formatter: 3 arquivos reformatados
- ✅ isort: Imports organizados alphabeticamente
- ✅ Pylint Core: 9.38/10 (meta >9.0)
- ⚠️ Pylint GUI: 7.20/10 (aceitável para complexidade GUI)
- ✅ Testes: 50/50 PASSED (0.24s, timeout 30s)
- ✅ Syntax validation: py_compile OK
- ✅ Functional test: CLI retorna JSON válido

**6. Security (OWASP)**:
- ✅ CWE-22 Path Traversal: Mitigado com `validate_file_path()`
- ✅ Injection: Seguro (sem SQL/eval/exec)
- ✅ Deserialization: Seguro (json.load da stdlib)
- ✅ Specific exception handling: OSError, JSONDecodeError

**7. Integração**:
- ✅ Menu Tools: "JSON Set Operations..." action
- ✅ Lazy loading: `_show_set_operations()` method
- ✅ RightDockWidgetArea placement
- ✅ Export em `src/gui/__init__.py`

**Exemplo CLI**:
```bash
python -m src.set_operations intersection file_a.json file_b.json
python -m src.set_operations union a.json b.json c.json -o result.json
python -m src.set_operations difference a.json b.json --ignore-case-keys
python -m src.set_operations symmetric a.json b.json --arrays-ignore-order
```

**Decisões de Design**:
- Pipeline left-to-right: A ∩ B ∩ C executado como (A ∩ B) ∩ C
- Comparação estrita de tipos: `{"age": 25}` ≠ `{"age": "25"}`
- Null ≠ Empty: `{"value": null}` ≠ `{"value": ""}`
- Arrays order-dependent por padrão (option para ignorar ordem)
- Dot notation para paths: `pages.home.title`

**Rollback Plan**:
- Remover arquivos: `src/set_operations.py`, `src/gui/set_operations_dock.py`, `tests/test_set_operations.py`
- Reverter `src/app.py`: remover 3 linhas (action, addAction, connect)
- Reverter `src/gui/__init__.py`: remover 2 linhas (import, __all__)
- Impacto: zero em funcionalidades existentes (feature isolada)
- Tempo estimado: ~5 minutos

---

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
| MUST HAVE | 12 | 12 | 0 | 100.0% |
| SHOULD HAVE | 53 | 53 | 0 | 100.0% |
| COULD HAVE | 36 | 13 | 23 | 36.1% |
| WOULD HAVE LATER | 56 | 12 | 44 | 21.4% |
| **TOTAL** | **157** | **90** | **67** | **57.3%** |

**Última Atualização**: 02/12/2025 - v2.9.32 Set Operations + Recomendações Pós-Release

**Notas de Atualização**:
- ✅ **v2.9.32 Completa**: JSON Set Operations implementada com sucesso
- 📋 **+50 Novas Tasks Recomendadas**: Expansão significativa do roadmap
  - **COULD HAVE**: +18 tasks (Set Operations enhancements, QA, UX/Accessibility, Documentation, Architecture)
  - **WOULD HAVE LATER**: +32 tasks (Advanced features, Cloud sync, GraphQL, Git integration)
- 🎯 **Foco Atual**: Completar 23 tasks pendentes de COULD HAVE (features de médio prazo)
- 🚀 **Visão de Longo Prazo**: 44 tasks em WOULD HAVE LATER (inovações avançadas)

### Notas

- Este é um projeto ambicioso com roadmap de longo prazo
- 🎉 **Funcionalidades MUST HAVE 100% completas!**
- 🎉 **Funcionalidades SHOULD HAVE 100% completas!**
- **v2.9.9**: Melhorias em tradução, validação de case, ranges hierárquicos e transparência
- **v3.0.0**: Adicionadas 5 ferramentas profissionais (Case Converter, JSON Search, Text Extractor, Placeholder Replacer, AI File Processor)
- **v2.9.24**: Adicionado Text to JSON Converter com 10 formatos (Key-Value, CSV, YAML, TOML, TOON, etc.)
- Projeto funcional e utilizável no estado atual com ferramentas avançadas
- **84.1%** do projeto total completo (90 tasks completas) - em progressão constante
- Categorias SHOULD/COULD/WOULD são melhorias e features avançadas
- **v2.9.14**: Task #23 COMPLETA - Orphaned Keys Update System com VALUE EQUALITY (12 unit tests passing)
- **v2.9.15**: Tasks #44 e #45 COMPLETAS - Análise add/ + Sistema de Tutoriais com Help menu (3 tutoriais MVP, TutorialsDock, preparação chatbot)
- **v2.9.17**: Task #47 COMPLETA - JSON Editor avançado com validação tempo real, tree view, format, search (750+ linhas, 18 testes passing)
- **v2.9.16**: Task #46 COMPLETA - Editor Integrado com syntax highlighting diferenciado por cores (700+ linhas, tabs, save/load, Ctrl+E)
- **v2.9.17**: Task #47 COMPLETA - JSON Editor avançado integrado (validação, tree view, format, search - 750+ linhas, 18 testes)
- **v2.9.18**: Task #5 COMPLETA - Edit-Only Mode sandbox editing (600+ linhas, 16 testes, State+Strategy+Command patterns)
- **v2.9.13**: Melhorias de UX com context menus, tooltips, preferences persistentes e stats em tempo real
- **Correção 30/11/2025**: 4 tasks já implementadas foram marcadas corretamente (reverse translation, cancel processing, file list ls/dir, async file insertion)
- **v2.9.26**: Task #51 COMPLETA - Advanced File Filters no AI Processor (660+ linhas, 21 testes passing em 0.33s, Protocolo Simplicidade 1 v1.6)
- **v2.9.27**: Task #52 COMPLETA - Remove Duplicate Objects no JSON Rewriter (637+ linhas, 19 testes passing em 0.21s, Protocolo Simplicidade 1 v1.6)

### Marcos Importantes

- **v3.0.0 (24/11/2025)**: +6 tasks completadas (SHOULD HAVE)
- **v2.9.26 (01/12/2025)**: Task #51 COMPLETA - Advanced File Filters (6 field types, 10 operators, AND/OR logic, QSettings persistence)
- **v2.9.27 (01/12/2025)**: Task #52 COMPLETA - Remove Duplicate Objects (threshold 50-100%, remove/reference modes, array support, 19 tests)
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
- **⭐ Protocolo Simplicidade 1**: `docs/PROTOCOLO_SIMPLICIDADE_1.md` (v1.5 - **LER SEMPRE!**)

---

## 📋 Protocolo Simplicidade 1 - Referência Rápida

**⚠️ IMPORTANTE**: Para implementação completa, consultar **`docs/PROTOCOLO_SIMPLICIDADE_1.md` (v1.5)**.

### 12 Etapas Obrigatórias (Resumo)

1. 📚 Ler documentação (TASKS.md)
2. ✅ Escolher tarefas mais simples
3. ❓ Fazer perguntas (Q1-Q13)
4. 🔍 Analisar projeto (deep code analysis)
5. 🎯 Planejar sprints (Sprint A + B)
6. 💻 Implementar (máx 200 linhas/sprint)
7. 🔗 Verificar integração GUI
8. ⌨️ Verificar CLI
9. 🧪 **Fazer testes COM SEGURANÇA** (ver Etapa 9.1)
10. 🧹 Organizar pasta raiz
11. 📝 Documentar (TASKS.md)
12. 🚀 Commit e push

### 🛡️ Etapa 9.1 - Segurança em Testes (CRÍTICO)

**Ver `docs/PROTOCOLO_SIMPLICIDADE_1.md` para detalhes completos.**

**Resumo**:
- ✅ Timeout obrigatório: `--timeout=30`
- ✅ Ambiente headless: `QT_QPA_PLATFORM=offscreen`
- ✅ Dry-run antes: `python -m py_compile tests/*.py`
- ✅ Detecção de loop: `timeout 10s pytest ...`
- ✅ Fallback: mocks, unit tests sem GUI
- ✅ Documentar limitações se necessário

**Comando seguro**:
```bash
QT_QPA_PLATFORM=offscreen timeout 5m pytest tests/test_gui_*.py -v --timeout=30
```

### ⚠️ Regras de Ouro

1. **NUNCA** esquecer dos sprints após Q&A
2. **NUNCA** executar testes sem timeout
3. **NUNCA** implementar >200 linhas de uma vez
4. **SEMPRE** consultar `docs/PROTOCOLO_SIMPLICIDADE_1.md` (v1.5)

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
