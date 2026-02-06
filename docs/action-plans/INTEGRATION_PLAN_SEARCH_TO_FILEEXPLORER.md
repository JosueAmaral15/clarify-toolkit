# Plano de Integração: Search/Replace → File Explorer

**Objetivo**: Integrar todas as funcionalidades do Tool Search/Replace no Tool File Explorer, criando uma ferramenta unificada e mais poderosa.

**Data**: 25/12/2025  
**Versão Alvo**: v2.9.116  
**Estimativa Total**: 6-8 horas de desenvolvimento

---

## 📊 ANÁLISE COMPARATIVA

### Search/Replace Panel (search_replace_panel.py)
**Funcionalidades Existentes:**
1. ✅ Seleção de diretório/arquivo (Browse)
2. ✅ Filtros de extensão (include/exclude patterns)
3. ✅ Busca por conteúdo (multi-linha, regex, case-sensitive, whole-word)
4. ✅ Busca por nome de arquivo
5. ✅ Substituição (Replace first/Replace all)
6. ✅ Preserve case na substituição
7. ✅ Condições avançadas (filename, path, ext, size, mtime, content)
8. ✅ Operadores lógicos (AND/OR) entre condições
9. ✅ Árvore de resultados (ResultsTree)
10. ✅ Save results to file
11. ✅ Status bar com estatísticas
12. ✅ Progress tracking integrado
13. ✅ Thread management (SearchWorker)
14. ✅ Hover expansion do painel de resultados
15. ✅ Histórico de operações

### File Explorer Dock (file_explorer_dock.py)
**Funcionalidades Existentes:**
1. ✅ Seleção de diretório (Browse)
2. ✅ Opções Unix-style (-la, -lh, -R)
3. ✅ File type filter (Any/Files Only/Directories Only)
4. ✅ Advanced filters panel (regex, size, mtime, extensions, depth, excludes)
5. ✅ Presets system (save/load/export/import)
6. ✅ Tabela de resultados (Name, Size, Modified, Permissions, Path)
7. ✅ Sort/filter na tabela
8. ✅ Export to CSV
9. ✅ Context menu ("Open in File Manager")
10. ✅ Estatísticas (count + total size)
11. ✅ Selection mode (multi-select)
12. ✅ Dialog mode (modal dialog)
13. ✅ Recent directories menu
14. ✅ Preview tooltips

---

## 🎯 FASE 1: PLANEJAMENTO E DESIGN (30 min)

### 1.1. Decidir Estrutura de UI

**Opção A: Collapsible Sections** (RECOMENDADO ✅)
```
┌─────────────────────────────────────────────────────────┐
│ File Explorer (Browse + Search + Replace)        [×]    │
├─────────────────────────────────────────────────────────┤
│ 📁 DIRECTORY & TYPE                              [▼]    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Root: [/home/user/project        ] [Browse] [Recent]│ │
│ │ Type: [Any ▼] Files: [✓] Dirs: [✓] Hidden: [ ]     │ │
│ │ Options: [✓]-l [✓]-h [✓]-a [ ]-R  Depth: [__]      │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 🔍 SEARCH & REPLACE                              [▼]    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ File Name: [*.py                        ] [Clear]   │ │
│ │ Content:   ┌────────────────────────────┐           │ │
│ │            │ def main():                │           │ │
│ │            │     pass                   │           │ │
│ │            └────────────────────────────┘           │ │
│ │ Options: [✓]Case [✓]Word [ ]Regex                  │ │
│ │ Replace:   ┌────────────────────────────┐           │ │
│ │            │ def start():               │           │ │
│ │            │     run()                  │           │ │
│ │            └────────────────────────────┘           │ │
│ │ [✓]Preserve Case  [Replace First] [Replace All]    │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ⚙️ FILTERS                                       [▼]    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Extensions: [✓]Include [.py, .js  ] [✓]Exclude [.] │ │
│ │ Size:       [>] [1024] KB  [<] [10240] KB          │ │
│ │ Modified:   [After] [2024-01-01]                   │ │
│ │ Depth:      [Max: 5]  Pattern: [src/**]           │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 🎯 ADVANCED CONDITIONS (AND/OR Logic)            [▼]    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Logic: [AND ▼]  [+ Add Condition] [Clear All]      │ │
│ │ ┌───┬────┬─────┬──────┬──────┬────┬────┬─────┬──┐  │ │
│ │ │Fld│Op  │Value│Scope │Param │Case│Word│Regex│×  │  │ │
│ │ ├───┼────┼─────┼──────┼──────┼────┼────┼─────┼──┤  │ │
│ │ │ext│=   │.py  │-     │-     │    │    │     │  │  │ │
│ │ │sz │>   │1024 │-     │-     │    │    │     │  │  │ │
│ │ │cnt│cont│TODO │all   │-     │✓   │    │     │  │  │ │
│ │ └───┴────┴─────┴──────┴──────┴────┴────┴─────┴──┘  │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 💾 PRESETS                                       [▼]    │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [My Preset 1 ▼] [Load] [Save] [Delete] [Export]    │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ [🔍 Search Files] [📋 List Files] [💾 Save Config]     │
├─────────────────────────────────────────────────────────┤
│ 📊 RESULTS (142 files, 2.5 MB)     [Table▼] [Export]  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Name         │ Size │ Modified    │ Path            │ │
│ ├──────────────┼──────┼─────────────┼─────────────────┤ │
│ │ main.py      │ 12KB │ 2024-12-25  │ /src/main.py    │ │
│ │ utils.py     │ 8KB  │ 2024-12-24  │ /src/utils.py   │ │
│ │ ...          │ ...  │ ...         │ ...             │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Opção B: Splitter Horizontal com Scroll** (Alternativa)
```
┌─────────────────────────────────────────────────────────┐
│ File Explorer                                    [×]    │
├───────────────────────────┬─────────────────────────────┤
│ ⬅️ CONFIGURATION (SCROLL) │ RESULTS ➡️                   │
│ ┌───────────────────────┐ │ ┌─────────────────────────┐ │
│ │ 📁 Directory          │ │ │ Name    │ Size │ Path   │ │
│ │ 🔍 Search             │ │ ├─────────┼──────┼────────┤ │
│ │ ⚙️  Filters            │ │ │ main.py │ 12KB │ /src/  │ │
│ │ 🎯 Conditions         │ │ │ util.py │ 8KB  │ /src/  │ │
│ │ 💾 Presets            │ │ │ ...     │ ...  │ ...    │ │
│ │                       │ │ │                         │ │
│ │ [Search] [List]       │ │ └─────────────────────────┘ │
│ └───────────────────────┘ │ Stats: 142 files, 2.5 MB  │
└───────────────────────────┴─────────────────────────────┘
```

**DECISÃO**: Usar **Opção A (Collapsible)** porque:
- ✅ **Visão holística**: Vê todas as opções ao mesmo tempo
- ✅ **Collapsible**: Expande/recolhe seções conforme necessário
- ✅ **Workflow contínuo**: Ajusta tudo sem alternar contexto
- ✅ **Menos cliques**: Não precisa trocar tabs
- ✅ **UX intuitiva**: Estado de cada seção visível (▼ = expandido)
- ✅ **Scroll vertical**: Natural para muitas opções

### 1.2. Identificar Componentes a Migrar

**Do Search/Replace para File Explorer:**
1. ✅ `ed_filename_query` (QLineEdit) - Busca por nome
2. ✅ `ed_query` (QPlainTextEdit) - Busca por conteúdo (multi-linha)
3. ✅ `ed_repl` (QPlainTextEdit) - Texto de substituição
4. ✅ Checkboxes: `chk_case`, `chk_word`, `chk_regex`, `chk_preserve`
5. ✅ Botões: `btn_search`, `btn_replace_one`, `btn_replace_all`
6. ✅ `ResultsTree` widget
7. ✅ `SearchWorker` thread
8. ✅ Advanced conditions grid (field, operator, value, scope, etc.)
9. ✅ Logic operator combo (AND/OR)
10. ✅ `btn_save_results`
11. ✅ `results_status` label
12. ✅ Event filter (hover expansion)

### 1.3. Definir Arquitetura de Classes

```python
# Nova estrutura
FileExplorerDock (BaseDock)
├── BrowseTab (QWidget)
│   ├── DirectorySelector
│   ├── FileTypeFilter
│   ├── UnixOptionsPanel
│   └── BasicFiltersPanel
├── SearchTab (QWidget)
│   ├── FileNameQueryPanel
│   ├── ContentQueryPanel (multi-line)
│   ├── SearchOptionsPanel (case, word, regex)
│   └── ReplacePanel (text, preserve case, buttons)
├── AdvancedTab (QWidget)
│   ├── ConditionsGrid (dynamic rows)
│   ├── LogicOperatorSelector
│   └── PresetsPanel
└── ResultsPanel (QWidget)
    ├── DisplayModeToggle (Table/Tree)
    ├── ResultsTable OR ResultsTree
    ├── StatisticsBar
    └── ContextMenu

# Executores
FileExplorerExecutor (merged)
├── list_files() - from FileListExecutor
├── search_content() - from SearchWorker
├── replace_content() - from SearchWorker
└── apply_advanced_conditions() - from filter_files_by_conditions
```

---

## 🔧 FASE 2: CRIAÇÃO DE COMPONENTES REUTILIZÁVEIS (1h)

### 2.1. Extrair Widgets de Search/Replace

**Arquivo**: `src/gui/widgets/search_widgets.py` (NOVO)

```python
"""
Search & Replace Widgets
------------------------
Reusable components extracted from search_replace_panel.py
"""

class FileNameQueryPanel(QWidget):
    """File name search input with clear button."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # ed_filename_query + clear button
        
class ContentQueryPanel(QWidget):
    """Multi-line content search with editor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # ed_query (QPlainTextEdit)
        # monospaced font
        # resizable
        
class SearchOptionsPanel(QWidget):
    """Checkboxes for search options (case, word, regex)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # chk_case, chk_word, chk_regex
        
class ReplacePanel(QWidget):
    """Replacement text editor with buttons."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # ed_repl (QPlainTextEdit)
        # chk_preserve
        # btn_replace_one, btn_replace_all
        
class ConditionsGrid(QWidget):
    """Dynamic grid of advanced conditions."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # combo_logic_op (AND/OR)
        # dynamic condition rows
        # add/remove buttons
```

**Tarefas**:
- [ ] Criar `search_widgets.py`
- [ ] Extrair `FileNameQueryPanel`
- [ ] Extrair `ContentQueryPanel`
- [ ] Extrair `SearchOptionsPanel`
- [ ] Extrair `ReplacePanel`
- [ ] Extrair `ConditionsGrid`
- [ ] Adicionar signals apropriados
- [ ] Testar cada widget isoladamente

### 2.2. Criar Executor Unificado

**Arquivo**: `src/core/file_explorer_executor.py` (NOVO)

```python
"""
File Explorer Executor
----------------------
Unified executor combining:
- File listing (from FileListExecutor)
- Content search (from SearchWorker)
- Content replacement (from SearchWorker)
- Advanced conditions (from filter_files_by_conditions)
"""

class FileExplorerExecutor:
    """Unified executor for file operations."""
    
    def list_files(self, directory, options):
        """List files in directory with filters."""
        # Migrate from FileListExecutor
        
    def search_content(self, directory, query, options, conditions):
        """Search file content with advanced filters."""
        # Migrate from SearchWorker.search()
        
    def replace_content(self, files, query, replacement, options):
        """Replace content in files."""
        # Migrate from SearchWorker.replace()
        
    def apply_conditions(self, files, conditions, logic_op):
        """Apply advanced conditional filtering."""
        # Use filter_files_by_conditions
```

**Tarefas**:
- [ ] Criar `file_explorer_executor.py`
- [ ] Migrar `list_files()` de FileListExecutor
- [ ] Migrar `search_content()` de SearchWorker
- [ ] Migrar `replace_content()` de SearchWorker
- [ ] Integrar `apply_conditions()` com filter_files_by_conditions
- [ ] Adicionar progress callbacks
- [ ] Testar executor isoladamente

---

## 🏗️ FASE 3: REFATORAÇÃO DO FILE EXPLORER (2h)

### 3.1. Criar Sistema de Tabs

**Arquivo**: `src/gui/file_explorer_dock.py`

```python
def _create_widgets(self):
    """Create tabbed UI."""
    # Create tab widget
    self.tabs = QTabWidget()
    
    # Tab 1: Browse
    self.browse_tab = self._create_browse_tab()
    self.tabs.addTab(self.browse_tab, "Browse")
    
    # Tab 2: Search & Replace
    self.search_tab = self._create_search_tab()
    self.tabs.addTab(self.search_tab, "Search & Replace")
    
    # Tab 3: Advanced
    self.advanced_tab = self._create_advanced_tab()
    self.tabs.addTab(self.advanced_tab, "Advanced")
    
    # Results panel (below tabs)
    self.results_panel = self._create_results_panel()
```

**Tarefas**:
- [ ] Adicionar QTabWidget ao layout principal
- [ ] Criar `_create_browse_tab()` - mover widgets existentes
- [ ] Criar `_create_search_tab()` - usar novos widgets
- [ ] Criar `_create_advanced_tab()` - conditions + presets
- [ ] Criar `_create_results_panel()` - table/tree toggle
- [ ] Ajustar layout com splitter vertical (tabs | results)

### 3.2. Integrar Widgets de Busca

```python
def _create_search_tab(self):
    """Create Search & Replace tab."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # File name query
    self.filename_panel = FileNameQueryPanel()
    layout.addWidget(QGroupBox("File Name Pattern", self.filename_panel))
    
    # Content query
    self.content_panel = ContentQueryPanel()
    layout.addWidget(QGroupBox("File Content Search", self.content_panel))
    
    # Search options
    self.search_opts_panel = SearchOptionsPanel()
    layout.addWidget(self.search_opts_panel)
    
    # Replace panel
    self.replace_panel = ReplacePanel()
    layout.addWidget(QGroupBox("Replace", self.replace_panel))
    
    # Buttons
    buttons = QHBoxLayout()
    self.btn_search = QPushButton("🔍 Search")
    self.btn_search.clicked.connect(self._execute_search)
    buttons.addWidget(self.btn_search)
    layout.addLayout(buttons)
    
    return widget
```

**Tarefas**:
- [ ] Instanciar widgets de busca
- [ ] Conectar signals
- [ ] Implementar `_execute_search()`
- [ ] Implementar `_execute_replace()`
- [ ] Integrar com FileExplorerExecutor
- [ ] Adicionar validação de inputs

### 3.3. Adaptar Results Display

```python
def _create_results_panel(self):
    """Create unified results display."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Toggle between Table and Tree view
    header = QHBoxLayout()
    self.lbl_results = QLabel("Results")
    self.btn_toggle_view = QPushButton("Switch to Tree View")
    self.btn_toggle_view.clicked.connect(self._toggle_results_view)
    header.addWidget(self.lbl_results)
    header.addStretch()
    header.addWidget(self.btn_toggle_view)
    layout.addLayout(header)
    
    # Stack widget for Table/Tree
    self.results_stack = QStackedWidget()
    self.results_table = self.table_manager.table  # Existing table
    self.results_tree = ResultsTree()  # From search_replace_panel
    self.results_stack.addWidget(self.results_table)
    self.results_stack.addWidget(self.results_tree)
    layout.addWidget(self.results_stack)
    
    # Statistics bar
    self.results_status = QLabel("")
    layout.addWidget(self.results_status)
    
    return widget
```

**Tarefas**:
- [ ] Criar QStackedWidget para Table/Tree
- [ ] Adicionar toggle button
- [ ] Migrar ResultsTree de search_replace_panel
- [ ] Unificar statistics bar
- [ ] Implementar `_toggle_results_view()`
- [ ] Ajustar context menus para ambos views

---

## 🔄 FASE 4: MIGRAÇÃO DE LÓGICA (1.5h)

### 4.1. Migrar Search Logic

**De**: `search_replace_panel.py::_start_search_threaded()`  
**Para**: `file_explorer_dock.py::_execute_search()`

```python
def _execute_search(self):
    """Execute content search with advanced filters."""
    # 1. Collect all parameters
    directory = self.ed_directory.text()
    file_query = self.filename_panel.get_query()
    content_query = self.content_panel.get_query()
    options = self.search_opts_panel.get_options()
    conditions = self.conditions_grid.get_conditions()
    logic_op = self.conditions_grid.get_logic_operator()
    
    # 2. Validate
    if not directory or not (file_query or content_query):
        QMessageBox.warning(self, "Invalid Input", "...")
        return
    
    # 3. Execute in thread
    self.worker = QThread()
    self.executor = FileExplorerExecutor()
    self.executor.moveToThread(self.worker)
    
    # Connect signals
    self.executor.progress.connect(self._update_progress)
    self.executor.finished.connect(self._display_search_results)
    self.executor.error.connect(self._handle_error)
    
    # Start
    self.worker.started.connect(
        lambda: self.executor.search_content(
            directory, content_query, options, conditions
        )
    )
    self.worker.start()
```

**Tarefas**:
- [ ] Criar `_execute_search()`
- [ ] Coletar parâmetros de todos os tabs
- [ ] Validar inputs
- [ ] Criar thread com executor
- [ ] Conectar signals de progresso
- [ ] Implementar `_display_search_results()`
- [ ] Testar busca simples
- [ ] Testar busca com condições

### 4.2. Migrar Replace Logic

**De**: `search_replace_panel.py::_do_replace()`  
**Para**: `file_explorer_dock.py::_execute_replace()`

```python
def _execute_replace(self, all_: bool):
    """Execute replacement operation."""
    # 1. Get selected files from results
    if self.results_stack.currentIndex() == 0:  # Table view
        selected_files = self.table_manager.get_selected_files()
    else:  # Tree view
        selected_files = self.results_tree.get_selected_files()
    
    if not selected_files:
        QMessageBox.warning(self, "No Selection", "...")
        return
    
    # 2. Get replace parameters
    query = self.content_panel.get_query()
    replacement = self.replace_panel.get_replacement()
    preserve_case = self.replace_panel.get_preserve_case()
    options = self.search_opts_panel.get_options()
    
    # 3. Confirm
    msg = f"Replace {'all' if all_ else 'first'} in {len(selected_files)} files?"
    reply = QMessageBox.question(self, "Confirm", msg)
    if reply != QMessageBox.Yes:
        return
    
    # 4. Execute
    self.executor.replace_content(
        selected_files, query, replacement, options, all_
    )
```

**Tarefas**:
- [ ] Criar `_execute_replace()`
- [ ] Integrar com ambos views (Table/Tree)
- [ ] Adicionar confirmação
- [ ] Executar replacement
- [ ] Atualizar results após replace
- [ ] Adicionar undo/redo support
- [ ] Testar replace first
- [ ] Testar replace all

### 4.3. Migrar Advanced Conditions

**De**: `search_replace_panel.py::cond_list`  
**Para**: `advanced_tab` com `ConditionsGrid`

```python
def _create_advanced_tab(self):
    """Create Advanced Conditions tab."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Conditions grid
    self.conditions_grid = ConditionsGrid()
    layout.addWidget(self.conditions_grid)
    
    # Presets (only if not dialog_mode)
    if not self.dialog_mode:
        layout.addWidget(self.preset_manager)
    
    return widget
```

**Tarefas**:
- [ ] Mover conditions grid para Advanced tab
- [ ] Conectar com search execution
- [ ] Testar AND logic
- [ ] Testar OR logic
- [ ] Integrar com presets
- [ ] Validar todas as condições (filename, path, size, mtime, content)

---

## 🎨 FASE 5: AJUSTES DE UI/UX (1h)

### 5.1. Unificar Estilos

**Tarefas**:
- [ ] Aplicar tema consistente em todos os tabs
- [ ] Ajustar espaçamentos e margens
- [ ] Padronizar tamanhos de botões
- [ ] Aplicar ícones (emojis) consistentes
- [ ] Revisar tooltips (i18n)

### 5.2. Implementar Hover Expansion

```python
def eventFilter(self, obj, event):
    """Event filter for results panel hover expansion."""
    if obj == self.results_stack:
        if event.type() == QEvent.Enter:
            # Expand results panel
            if not self._is_expanded:
                self._original_sizes = self._splitter.sizes()
                # ... expand logic
        elif event.type() == QEvent.Leave:
            # Restore
            # ... restore logic
    return super().eventFilter(obj, event)
```

**Tarefas**:
- [ ] Migrar eventFilter de search_replace_panel
- [ ] Instalar filter no results_stack
- [ ] Ajustar expansion logic para novo layout
- [ ] Testar com ambos views (Table/Tree)

### 5.3. Adicionar Keyboard Shortcuts

```python
def _setup_shortcuts(self):
    """Setup keyboard shortcuts."""
    # Ctrl+F - Focus search
    QShortcut(QKeySequence("Ctrl+F"), self, self._focus_search)
    
    # Ctrl+H - Focus replace
    QShortcut(QKeySequence("Ctrl+H"), self, self._focus_replace)
    
    # Ctrl+Enter - Execute search
    QShortcut(QKeySequence("Ctrl+Return"), self, self._execute_search)
    
    # F3 - Next result
    QShortcut(QKeySequence("F3"), self, self._next_result)
    
    # Shift+F3 - Previous result
    QShortcut(QKeySequence("Shift+F3"), self, self._prev_result)
```

**Tarefas**:
- [ ] Adicionar shortcuts principais
- [ ] Implementar navigation entre resultados
- [ ] Testar shortcuts em todos os tabs
- [ ] Documentar shortcuts em tooltips

---

## 🧪 FASE 6: TESTES E VALIDAÇÃO (1h)

### 6.1. Testes Funcionais

**Casos de Teste**:
1. ✅ Browse mode: listar arquivos sem busca
2. ✅ Search by filename: regex patterns
3. ✅ Search by content: multi-line queries
4. ✅ Search with case-sensitive
5. ✅ Search with whole-word
6. ✅ Search with regex
7. ✅ Replace first occurrence
8. ✅ Replace all occurrences
9. ✅ Replace with preserve case
10. ✅ Advanced conditions: AND logic
11. ✅ Advanced conditions: OR logic
12. ✅ Export results to CSV
13. ✅ Save results to file
14. ✅ Presets: save/load/export/import
15. ✅ Dialog mode: selection mode
16. ✅ Context menu: Open in File Manager
17. ✅ Toggle Table/Tree view
18. ✅ Hover expansion

**Tarefas**:
- [ ] Criar script de testes automatizados
- [ ] Executar todos os casos de teste
- [ ] Documentar bugs encontrados
- [ ] Corrigir bugs críticos

### 6.2. Testes de Performance

**Cenários**:
1. ⚡ Busca em 10.000 arquivos
2. ⚡ Busca com regex complexa
3. ⚡ Replace em 1.000 arquivos
4. ⚡ Load 50 condições avançadas
5. ⚡ Export 100.000 linhas para CSV

**Tarefas**:
- [ ] Criar dataset de teste
- [ ] Medir tempo de execução
- [ ] Identificar gargalos
- [ ] Otimizar operações lentas
- [ ] Adicionar caching onde apropriado

### 6.3. Testes de Regressão

**Verificar que funcionalidades antigas não quebraram**:
- [ ] File List: parâmetros Unix (-la, -lh, -R)
- [ ] Advanced filters: todas as opções
- [ ] Export to CSV: formato correto
- [ ] Recent directories: menu funcional
- [ ] Statistics: contagem e tamanho
- [ ] Dialog mode: retorno correto de seleção

---

## 📝 FASE 7: DOCUMENTAÇÃO (30 min)

### 7.1. Atualizar Documentação Técnica

**Arquivos a atualizar**:
- [ ] `PROJECT_STRUCTURE.md` - nova arquitetura
- [ ] `CHANGELOG.md` - v2.9.116 integration
- [ ] `docs/guides/file-explorer-guide.md` - novo manual
- [ ] `README.md` - features update

### 7.2. Criar Tutorial Interativo

**Arquivo**: `docs/tutorials/unified-file-explorer.md`

**Conteúdo**:
1. Introdução: O que mudou?
2. Tab Browse: Listar arquivos
3. Tab Search: Buscar conteúdo
4. Tab Advanced: Condições complexas
5. Replace: Substituir conteúdo
6. Results: Table vs Tree
7. Presets: Salvar configurações
8. Tips & Tricks
9. Troubleshooting

**Tarefas**:
- [ ] Escrever tutorial completo
- [ ] Adicionar screenshots
- [ ] Criar GIFs de demonstração
- [ ] Integrar com sistema de tutoriais do Clarify

### 7.3. Atualizar UI Tooltips (i18n)

**Arquivo**: `src/i18n/messages/en.json` + `pt.json`

```json
{
  "file_explorer": {
    "tab_browse": "Browse files and directories",
    "tab_search": "Search file content and replace",
    "tab_advanced": "Advanced filters and conditions",
    "btn_search": "Search for files matching criteria",
    "btn_replace_first": "Replace first occurrence per file",
    "btn_replace_all": "Replace all occurrences",
    "toggle_view": "Switch between Table and Tree view"
  }
}
```

**Tarefas**:
- [ ] Adicionar todas as novas strings
- [ ] Traduzir para português
- [ ] Aplicar tooltip_tr() em todos os widgets
- [ ] Testar troca de idioma

---

## 🚀 FASE 8: DEPLOY E CLEANUP (30 min)

### 8.1. Deprecar Search/Replace Panel

```python
# Em src/gui/ui_builder.py
def build_panels(main_window):
    """Build main panels."""
    # DEPRECATED: Search/Replace moved to File Explorer (v2.9.116)
    # main_window.tab_search = SearchReplacePanel(...)
    
    # NEW: File Explorer with integrated search/replace
    main_window.tab_file_explorer = FileExplorerDock(
        parent=main_window,
        dialog_mode=False
    )
    main_window.tabs.addTab(main_window.tab_file_explorer, "File Explorer")
```

**Tarefas**:
- [ ] Comentar código antigo (não deletar ainda)
- [ ] Adicionar mensagem de migração
- [ ] Atualizar menus e shortcuts
- [ ] Remover tab "Search / Replace" do QTabWidget
- [ ] Manter código por 1 versão (rollback safety)

### 8.2. Atualizar Menu e Atalhos

```python
# Em src/gui/menu_builder.py
def build_tools_menu(main_window):
    """Build Tools menu."""
    # REMOVED: Search / Replace (now in File Explorer)
    # act_search = QAction("Search / Replace", main_window)
    
    # UPDATED:
    act_file_explorer = QAction("File Explorer (Browse/Search/Replace)", main_window)
    act_file_explorer.setShortcut("Ctrl+E")
    act_file_explorer.triggered.connect(main_window._show_file_explorer)
```

**Tarefas**:
- [ ] Atualizar menu Tools
- [ ] Atualizar shortcuts registry
- [ ] Remover atalhos antigos
- [ ] Testar navegação por menu

### 8.3. Commit e Release

```bash
git add -A
git commit -m "feat: integrate Search/Replace into File Explorer (v2.9.116)

INTEGRATION COMPLETE:
✅ Unified File Explorer with 3 tabs (Browse, Search, Advanced)
✅ All Search/Replace features migrated
✅ Table/Tree view toggle
✅ Advanced conditions with AND/OR logic
✅ Replace first/all with preserve case
✅ Progress tracking and threading
✅ Presets system
✅ Export to CSV
✅ Dialog mode support
✅ Hover expansion
✅ Keyboard shortcuts
✅ i18n support

DEPRECATED:
⚠️ search_replace_panel.py (code kept for 1 version, marked deprecated)

BREAKING CHANGES:
- Tab 'Search / Replace' removed from main tabs
- Use 'File Explorer' instead (Ctrl+E)

MIGRATION:
- All search/replace functionality preserved
- Better UI organization with tabs
- Faster workflow (no need to switch tools)

Technical Details:
- Created unified FileExplorerExecutor
- Extracted reusable search widgets
- Merged ResultsTree and FileListTable
- 957 lines (search_replace_panel) + 485 lines (file_explorer) = ~800 lines (unified)
- Performance: Same or better (shared executor)

Refs: #INTEGRATION_PLAN_SEARCH_TO_FILEEXPLORER.md
Testing: 18 functional tests passed
"
```

**Tarefas**:
- [ ] Executar todos os testes finais
- [ ] Criar commit descritivo
- [ ] Criar tag de versão: `v2.9.116`
- [ ] Atualizar CHANGELOG.md
- [ ] Push para repositório

---

## 📋 CHECKLIST FINAL

### Funcionalidades Integradas
- [ ] Seleção de diretório/arquivo
- [ ] File type filter (Any/Files/Dirs)
- [ ] Unix-style options
- [ ] Extension filters (include/exclude)
- [ ] File name search (regex)
- [ ] Content search (multi-line, regex, case, word)
- [ ] Replace (first/all, preserve case)
- [ ] Advanced conditions (filename, path, ext, size, mtime, content)
- [ ] Logic operators (AND/OR)
- [ ] Results display (Table/Tree toggle)
- [ ] Statistics bar
- [ ] Export to CSV
- [ ] Save results to file
- [ ] Presets system
- [ ] Recent directories
- [ ] Context menu
- [ ] Progress tracking
- [ ] Thread management
- [ ] Hover expansion
- [ ] Keyboard shortcuts
- [ ] Dialog mode
- [ ] Selection mode

### Qualidade
- [ ] Todos os testes passando
- [ ] Sem regressões
- [ ] Performance OK
- [ ] UI consistente
- [ ] Tooltips traduzidos
- [ ] Documentação completa
- [ ] Tutorial criado

### Deploy
- [ ] Código antigo deprecado
- [ ] Menu atualizado
- [ ] Shortcuts atualizados
- [ ] Commit criado
- [ ] Tag de versão criada
- [ ] CHANGELOG atualizado

---

## 🎯 MÉTRICAS DE SUCESSO

1. ✅ **Redução de código**: ~40% (1442 → ~800 linhas)
2. ✅ **Zero regressões**: Todas as features antigas funcionam
3. ✅ **UX melhorada**: Menos troca entre tools
4. ✅ **Performance**: Tempo de busca ≤ versão anterior
5. ✅ **Testes**: 100% casos passando

---

## ⚠️ RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Quebra de funcionalidades antigas | Média | Alto | Manter código antigo por 1 versão |
| Performance degradada | Baixa | Médio | Benchmark antes/depois |
| UX confusa | Média | Médio | Criar tutorial detalhado |
| Bugs em edge cases | Alta | Baixo | Testes extensivos |

---

## 📅 CRONOGRAMA ESTIMADO

| Fase | Duração | Data Estimada |
|------|---------|---------------|
| 1. Planejamento | 30 min | 25/12 - 14:00 |
| 2. Componentes | 1h | 25/12 - 15:00 |
| 3. Refatoração | 2h | 25/12 - 17:00 |
| 4. Lógica | 1.5h | 25/12 - 18:30 |
| 5. UI/UX | 1h | 25/12 - 19:30 |
| 6. Testes | 1h | 25/12 - 20:30 |
| 7. Documentação | 30 min | 25/12 - 21:00 |
| 8. Deploy | 30 min | 25/12 - 21:30 |
| **TOTAL** | **8h** | **Conclusão: 25/12 - 22:00** |

---

## 🤝 PRÓXIMOS PASSOS

Após aprovação deste plano:

1. **Iniciar Fase 1**: Confirmar decisão de design (Tabs vs Splitter)
2. **Criar branch**: `feature/integrate-search-to-fileexplorer`
3. **Executar fases sequencialmente**: Commit após cada fase
4. **Review final**: Antes do merge
5. **Deploy**: Após aprovação

---

**Status**: 🟡 AGUARDANDO APROVAÇÃO  
**Autor**: GitHub Copilot  
**Data**: 25/12/2025
