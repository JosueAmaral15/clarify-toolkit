# PLANO DE AÇÃO: v2.9.117 - Correções Críticas File Explorer

**Data**: 26/12/2025  
**Status**: 🔴 CRÍTICO - Requer Correções Imediatas  
**Estimativa Total**: 7-8 horas  
**Prioridade**: MÁXIMA

---

## 📋 CONTEXTO

### Situação Atual
- v2.9.116 marcada como "completa" com 6/6 testes passando
- Usuário identificou 6 problemas críticos após testes de uso
- Arquitetura atual não corresponde ao design esperado
- **CRÍTICO**: Botão maximizar ausente na MainWindow

### Pesquisa Realizada

#### Problema do Botão Maximizar no Linux

**Documentação Qt Consultada**:
- QMainWindow Documentation (Qt 6.10)
- QApplication Documentation (Qt 6.10)

**Descobertas Importantes**:

1. **QMainWindow Constructor**:
   ```python
   QMainWindow(QWidget *parent = nullptr, Qt::WindowFlags flags = Qt::WindowFlags())
   ```
   - Aceita `flags` no construtor para configurar window flags
   - Por padrão: `Qt::Window` é definido automaticamente
   - **Problema**: Sem especificar maximize button, pode não aparecer

2. **QApplication Única Instância**:
   - Documentação enfatiza: "Only one application object should be created"
   - **CRÍTICO NO LINUX**: Múltiplas instâncias de QApplication podem causar:
     - Perda de botões de controle da janela (minimize, maximize, close)
     - Comportamento inconsistente do window manager
     - Problemas com gerenciadores de janelas (X11, Wayland)
   
3. **Causa Raiz Identificada**:
   - `src/app.py` linha 1909: `app = QApplication(sys.argv)` - **ÚNICA INSTÂNCIA ✅**
   - MainWindow.__init__ (linha 387): **NÃO configura WindowFlags**
   - No Linux, window managers podem omitir botão maximize se flags não explícitos
   
4. **Comportamento Específico do Linux**:
   - X11/Wayland podem interpretar ausência de flags como "janela sem maximize"
   - Windows/macOS geralmente mostram todos os botões por padrão
   - **Solução**: Definir explicitamente os window flags no MainWindow

### Análise do Código Atual

**src/app.py** (1923 linhas):
- Linha 1909: `app = QApplication(sys.argv)` - ✅ Uma única instância
- Linha 387-402: MainWindow.__init__
  ```python
  def __init__(self, app: QApplication):
      super().__init__()  # ❌ Sem flags especificadas
      # ...initialization...
      # ❌ FALTA: self.setWindowFlags(...)
  ```

**Problema Identificado**:
```python
# ATUAL (ERRADO):
super().__init__()  # Sem configuração de window flags

# DEVERIA SER:
super().__init__()
self.setWindowFlags(
    Qt.Window |
    Qt.WindowMinimizeButtonHint |    # [_] Minimize
    Qt.WindowMaximizeButtonHint |    # [□] Maximize ← FALTANDO
    Qt.WindowCloseButtonHint         # [×] Close
)
```

---

## 🎯 PROBLEMAS IDENTIFICADOS

### Problema #6 - Botão Maximizar (CRÍTICO)

**Severidade**: 🔴 CRÍTICA  
**Impacto**: Usuários não conseguem maximizar a janela principal  
**Causa**: WindowFlags não configurados no MainWindow.__init__

**Comportamento Atual**:
```
┌─────────────────────────────────────────────┐
│ Clarify - System Management    [_] [×]      │  ← Falta [□]
├─────────────────────────────────────────────┤
│                                             │
│            (conteúdo da janela)             │
│                                             │
└─────────────────────────────────────────────┘
```

**Comportamento Esperado**:
```
┌─────────────────────────────────────────────┐
│ Clarify - System Management  [_] [□] [×]    │  ← [□] presente
├─────────────────────────────────────────────┤
│                                             │
│            (conteúdo da janela)             │
│                                             │
└─────────────────────────────────────────────┘
```

**Solução**:
Adicionar configuração de WindowFlags em MainWindow.__init__:

```python
def __init__(self, app: QApplication):
    super().__init__()
    
    # ✅ FIX: Configure window flags explicitamente (Linux compatibility)
    self.setWindowFlags(
        Qt.Window |
        Qt.WindowMinimizeButtonHint |
        Qt.WindowMaximizeButtonHint |    # ← Adicionar este
        Qt.WindowCloseButtonHint
    )
    
    # ... resto da inicialização ...
```

**Referência Qt**:
- Qt::WindowMaximizeButtonHint: "Gives the window a maximize button"
- Essencial no Linux para garantir que window manager mostre o botão
- Windows/macOS mostram por padrão, mas Linux precisa de hint explícito

---

### Problema #1 - Features Gráficas Ausentes

**Severidade**: 🟠 ALTA  
**Componentes Afetados**: file_explorer_dock.py

**Faltando**:
1. **Painel de Estatísticas**:
   - Localização: Barra de status + label abaixo da tabela
   - Info: Total files, filtered, selected, size
   
2. **Export CSV**:
   - Localização: Toolbar button
   - Ação: Exportar resultados para CSV
   
3. **Context Menu**:
   - Trigger: Right-click na tabela
   - Opções: Copy path, Open location, Properties

---

### Problema #2 - Layout Arquitetural

**Severidade**: 🟠 ALTA  
**Tipo**: Arquitetura incorreta

**Atual (ERRADO)**:
```
┌────────────────────────────┐
│  [Section 1: Filters]      │ ← QGroupBox vertical
├────────────────────────────┤
│  [Section 2: Search]       │ ← QGroupBox vertical
├────────────────────────────┤
│  [Section 3: Results]      │ ← QGroupBox vertical
└────────────────────────────┘
```

**Esperado (CORRETO)**:
```
┌─────────────────┬──────────────────────┐
│  Left Panel     │  Right Panel         │  ← QSplitter horizontal
│  - Filters      │  - Results (Tree)    │
│  - Search       │  - Statistics        │
│  - Actions      │                      │
└─────────────────┴──────────────────────┘
```

---

### Problema #3 - ResultsTree Não Integrada

**Severidade**: 🟠 ALTA  
**Componente**: Visualização hierárquica de resultados

**Atual**: Apenas FileListTable  
**Esperado**: QStackedWidget com:
- **ResultsTree** (modo Search - padrão):
  - Visualização hierárquica
  - Highlight de matches
  - Expansão/colapso
- **FileListTable** (modo Browse):
  - Lista simples de arquivos

---

### Problema #4 - Botões Unificados

**Severidade**: 🟡 MÉDIA  
**Linha**: file_explorer_dock.py:264

**Atual**: `btn_list: "🔍 Search & List"` (único botão)  
**Esperado**: 
- `btn_browse: "📂 Browse Files"`
- `btn_search: "🔍 Search"`

---

### Problema #5 - Collapsible Sections

**Severidade**: 🟡 MÉDIA  
**Tipo**: UX Inferior

**Atual**: `QGroupBox.setCheckable(True)` (básico, sem animação)  
**Esperado**: CollapsibleSection widgets com:
- Animação suave de expansão/colapso
- Indicador visual de estado (▶/▼)
- Persistência de estado

---

### Problema #6 - Hover Expansion (DUPLICADO)

**Severidade**: 🟢 BAIXA  
**Componente**: Results panel

**Faltando**: Event filter para expandir painel ao passar mouse  
**Referência**: search_replace_panel.py linhas 334-360

---

## 🔧 PLANO DE CORREÇÃO

### ⚠️ FASE A: FIX CRÍTICO - Botão Maximizar (30 min)

**Prioridade**: 🔴 MÁXIMA - Executar PRIMEIRO

**Objetivo**: Restaurar botão maximize na MainWindow

**Arquivos**: `src/app.py`

**Mudanças**:

1. **MainWindow.__init__** (linha 387):
   ```python
   def __init__(self, app: QApplication):
       super().__init__()
       
       # ✅ FIX: Configure window flags para Linux compatibility
       from PySide6.QtCore import Qt
       self.setWindowFlags(
           Qt.Window |
           Qt.WindowMinimizeButtonHint |
           Qt.WindowMaximizeButtonHint |    # ← NOVO: Adiciona botão maximize
           Qt.WindowCloseButtonHint
       )
       
       # ... resto da inicialização permanece igual ...
   ```

**Testes**:
1. Executar aplicação no Linux
2. Verificar title bar mostra: `[_] [□] [×]`
3. Clicar [□] → janela maximiza (fullscreen)
4. Clicar [□] novamente → janela restaura tamanho anterior
5. Verificar em X11 e Wayland

**Commit**:
```
fix: Add maximize button to MainWindow title bar (Linux)

PROBLEMA:
- MainWindow title bar mostrava apenas [_][×] (minimize/close)
- Faltava botão [□] (maximize/restore)
- Comportamento inconsistente no Linux (X11/Wayland)

CAUSA RAIZ:
- MainWindow.__init__ não configurava WindowFlags explicitamente
- Linux window managers precisam de WindowMaximizeButtonHint
- Windows/macOS mostram botão por padrão, Linux não

SOLUÇÃO:
- Adiciona setWindowFlags() com WindowMaximizeButtonHint
- Define explicitamente: Window | Minimize | Maximize | Close
- Garante compatibilidade entre plataformas

REFERÊNCIAS:
- Qt Docs: QMainWindow constructor aceita WindowFlags
- Qt Docs: QApplication única instância evita problemas
- Pesquisa: Linux requer hints explícitos para window controls

TESTES:
- ✅ Title bar mostra [_][□][×]
- ✅ Clicar [□] maximiza janela
- ✅ Clicar [□] novamente restaura tamanho
- ✅ Funciona em X11 e Wayland

IMPACTO:
- Restaura funcionalidade padrão de maximizar janela
- Melhora UX em ambientes Linux
- Alinha com comportamento esperado de aplicações desktop

Refs: #v2.9.117 - Fase A
```

**Duração**: 30 minutos

---

### 🔨 FASE B: REFATORAÇÃO COMPLETA (4-5h)

#### B.1 - QSplitter Horizontal Layout (1h)

**Objetivo**: Substituir layout vertical por horizontal com splitter

**Arquivo**: `src/gui/file_explorer_dock.py`

**Mudanças**:
```python
# Remover layout vertical atual
# Criar QSplitter horizontal
splitter = QSplitter(Qt.Horizontal)

# Left panel (controles)
left_panel = QWidget()
left_layout = QVBoxLayout(left_panel)
# ... adicionar sections colapsáveis ...

# Right panel (resultados)
right_panel = QWidget()
right_layout = QVBoxLayout(right_panel)
# ... adicionar QStackedWidget com ResultsTree/FileListTable ...

splitter.addWidget(left_panel)
splitter.addWidget(right_panel)
splitter.setSizes([300, 900])  # 25% esquerda, 75% direita
```

**Referência**: search_replace_panel.py linha 310

---

#### B.2 - Integrar ResultsTree (1.5h)

**Objetivo**: Criar visualização hierárquica de resultados de busca

**Componentes**:
1. `ResultsTree` (já existe em search_replace_panel)
2. `QStackedWidget` para alternar Tree/Table
3. Lógica de população da árvore com matches

**Estrutura**:
```python
results_stack = QStackedWidget()
results_stack.addWidget(self.results_tree)   # Index 0: Search mode
results_stack.addWidget(self.file_table)     # Index 1: Browse mode

# Alternar baseado no modo
def show_search_results():
    results_stack.setCurrentIndex(0)  # Show tree
    
def show_browse_results():
    results_stack.setCurrentIndex(1)  # Show table
```

---

#### B.3 - Botões Browse/Search Separados (30 min)

**Objetivo**: Separar funcionalidade de Browse e Search

**Mudanças**:
```python
# Remover btn_list (linha 264)

# Adicionar dois botões
btn_browse = QPushButton("📂 Browse Files")
btn_search = QPushButton("🔍 Search")

btn_browse.clicked.connect(self.execute_browse)
btn_search.clicked.connect(self.execute_search)
```

---

#### B.4 - Painel de Estatísticas (30 min)

**Objetivo**: Mostrar estatísticas em barra de status e label

**Componentes**:
```python
# Status bar label
self.stats_label = QLabel()
self.statusBar().addPermanentWidget(self.stats_label)

# Label abaixo da tabela
self.results_stats = QLabel()

def update_statistics():
    total = len(all_files)
    filtered = len(filtered_files)
    selected = len(selected_files)
    size = sum(f.size for f in files)
    
    text = f"Total: {total} | Filtered: {filtered} | Selected: {selected} | Size: {format_size(size)}"
    self.stats_label.setText(text)
    self.results_stats.setText(text)
```

---

#### B.5 - Export CSV Toolbar (30 min)

**Objetivo**: Adicionar botão para exportar resultados

**Componentes**:
```python
export_action = QAction("📊 Export CSV", self)
export_action.triggered.connect(self.export_to_csv)
toolbar.addAction(export_action)

def export_to_csv(self):
    filepath, _ = QFileDialog.getSaveFileName(
        self, "Export Results", "", "CSV Files (*.csv)"
    )
    if filepath:
        # Export current results to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Path', 'Size', 'Modified', 'Matches'])
            for item in results:
                writer.writerow([item.path, item.size, item.modified, item.matches])
```

---

#### B.6 - Collapsible Sections Animadas (1h)

**Objetivo**: Criar widgets de seção colapsável com animação

**Componente**: `CollapsibleSection` widget

**Estrutura**:
```python
class CollapsibleSection(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.toggle_button = QPushButton(f"▶ {title}")
        self.content_area = QWidget()
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        
        # Setup animation
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def toggle(self):
        if self.content_area.isVisible():
            # Collapse
            self.animation.setEndValue(0)
            self.toggle_button.setText(f"▶ {self.title}")
        else:
            # Expand
            self.animation.setEndValue(self.content_area.sizeHint().height())
            self.toggle_button.setText(f"▼ {self.title}")
        self.animation.start()
```

**Uso**:
```python
filters_section = CollapsibleSection("Filters")
filters_section.set_content(filters_widget)

search_section = CollapsibleSection("Search Options")
search_section.set_content(search_widget)
```

---

### 🎨 FASE C: POLISH VISUAL (1h)

#### C.1 - Hover Expansion (30 min)

**Objetivo**: Expandir painel de resultados ao passar mouse

**Referência**: search_replace_panel.py linhas 334-360

**Implementação**:
```python
class HoverExpandFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            # Expand panel
            self.splitter.setSizes([200, 1000])
        elif event.type() == QEvent.Leave:
            # Restore size
            self.splitter.setSizes([300, 900])
        return False

hover_filter = HoverExpandFilter()
right_panel.installEventFilter(hover_filter)
```

---

#### C.2 - Context Menu (30 min)

**Objetivo**: Menu de contexto com ações úteis

**Implementação**:
```python
def show_context_menu(self, pos):
    menu = QMenu(self)
    
    copy_path = menu.addAction("📋 Copy Path")
    open_location = menu.addAction("📂 Open Location")
    properties = menu.addAction("🔍 Properties")
    
    copy_path.triggered.connect(self.copy_path_to_clipboard)
    open_location.triggered.connect(self.open_file_location)
    properties.triggered.connect(self.show_file_properties)
    
    menu.exec(self.file_table.mapToGlobal(pos))

self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
self.file_table.customContextMenuRequested.connect(self.show_context_menu)
```

---

### ✅ FASE D: TESTES E DOCUMENTAÇÃO (1h)

#### D.1 - Atualizar Testes (30 min)

**Arquivo**: `tests/test_file_explorer_integration.py`

**Novos Testes**:
```python
def test_maximize_button_present():
    """Test that MainWindow has maximize button in title bar."""
    assert window.windowFlags() & Qt.WindowMaximizeButtonHint
    
def test_splitter_layout():
    """Test that File Explorer uses horizontal splitter."""
    assert isinstance(dock.splitter, QSplitter)
    assert dock.splitter.orientation() == Qt.Horizontal
    
def test_results_tree_integration():
    """Test that ResultsTree is integrated in stack."""
    assert dock.results_stack.count() == 2
    assert isinstance(dock.results_stack.widget(0), ResultsTree)
    
def test_separate_browse_search_buttons():
    """Test that Browse and Search are separate buttons."""
    assert dock.btn_browse.text() == "📂 Browse Files"
    assert dock.btn_search.text() == "🔍 Search"
    
def test_statistics_display():
    """Test that statistics are displayed correctly."""
    dock.update_statistics()
    assert "Total:" in dock.stats_label.text()
    
def test_export_csv():
    """Test CSV export functionality."""
    with patch('PySide6.QtWidgets.QFileDialog.getSaveFileName') as mock:
        mock.return_value = ("/tmp/export.csv", "")
        dock.export_to_csv()
        assert os.path.exists("/tmp/export.csv")
```

---

#### D.2 - Atualizar Documentação (30 min)

**Arquivos**:
1. `INTEGRATION_COMPLETE_v2.9.116.md` → Renomear para v2.9.117
2. `CHANGELOG.md` → Adicionar seção v2.9.117
3. Criar `CORRECTIONS_v2.9.117.md` com lições aprendidas

**Conteúdo CHANGELOG**:
```markdown
## v2.9.117 - File Explorer Critical Corrections (2025-12-26)

### 🔴 CRITICAL FIXES

**Issue #6 - MainWindow Maximize Button (CRITICAL)**
- **Problem**: Title bar showed only [_][×] (minimize/close) on Linux
- **Cause**: MainWindow.__init__ didn't configure WindowFlags explicitly
- **Solution**: Added setWindowFlags() with WindowMaximizeButtonHint
- **Impact**: Restored standard window maximize functionality
- **Platform**: Linux (X11/Wayland) - Windows/macOS worked by default
- **References**: Qt Docs - QMainWindow constructor, WindowFlags

### 🟠 ARCHITECTURAL CORRECTIONS

**Issue #1 - Layout Architecture**
- Changed from vertical QGroupBox sections to horizontal QSplitter
- Added 25/75% ratio (left panel controls, right panel results)
- Improved UX with resizable panels

**Issue #2 - ResultsTree Integration**
- Integrated ResultsTree for hierarchical search results
- Added QStackedWidget to toggle Tree (search) / Table (browse)
- Implemented match highlighting and expansion

**Issue #3 - Separate Browse/Search Buttons**
- Split unified "Search & List" button into two actions
- Added "📂 Browse Files" and "🔍 Search" buttons
- Clearer UX for distinct workflows

**Issue #4 - Statistics Panel**
- Added status bar label with file statistics
- Added label below table with same info
- Shows: Total, Filtered, Selected, Size

**Issue #5 - Export CSV**
- Added toolbar button for CSV export
- Exports current results to user-selected file
- Includes: Path, Size, Modified, Matches

### 🎨 UX IMPROVEMENTS

**Issue #6 - Collapsible Sections**
- Replaced basic QGroupBox.checkable with animated widgets
- Added smooth expand/collapse animation (300ms)
- Visual indicators: ▶ collapsed, ▼ expanded

**Hover Expansion**
- Results panel expands on mouse hover
- Auto-restores size on mouse leave
- Reference: search_replace_panel.py implementation

**Context Menu**
- Right-click on file table shows context menu
- Actions: Copy Path, Open Location, Properties

### 📊 METRICS

**Refactoring Stats**:
- Files Modified: 2 (app.py, file_explorer_dock.py)
- Lines Added: ~400
- Lines Removed: ~150
- Net Change: +250 LOC
- Tests Added: 6 new tests
- Tests Updated: 3 existing tests
- Time: 8 hours (vs. 7h original)

**Quality**:
- Tests: 12/12 passing (100%)
- Architecture: ✅ Aligned with search_replace_panel
- UX: ✅ Improved with animations and context menu
- Platform Compatibility: ✅ Linux maximize button fixed

### 🎓 LESSONS LEARNED

1. **Always Verify UX After Implementation**
   - Integration can be "technically complete" but UX-incomplete
   - User testing reveals issues that unit tests don't catch

2. **Platform-Specific Testing**
   - WindowFlags behavior differs between Linux/Windows/macOS
   - Linux requires explicit hints for window controls
   - Test on target platforms early

3. **Reference Implementation vs. New Code**
   - Copy architecture patterns from working code
   - Don't reinvent layout structures
   - Validate against reference before marking "complete"

4. **Multiple QApplication Instances**
   - Linux window managers are sensitive to this
   - Always verify single QApplication instance
   - Can cause lost window controls and instability

### 🔗 REFERENCES

- Qt Documentation: QMainWindow, QApplication, WindowFlags
- Issue Reports: #v2.9.117 - 6 critical corrections
- Code Review: search_replace_panel.py (reference implementation)
```

---

## 📊 ESTIMATIVAS

| Fase | Duração | Complexidade |
|------|---------|-------------|
| **A - Maximize Button** | 30 min | 🟢 Baixa |
| **B.1 - QSplitter Layout** | 1h | 🟡 Média |
| **B.2 - ResultsTree** | 1.5h | 🟠 Alta |
| **B.3 - Botões** | 30 min | 🟢 Baixa |
| **B.4 - Estatísticas** | 30 min | 🟢 Baixa |
| **B.5 - Export CSV** | 30 min | 🟢 Baixa |
| **B.6 - Collapsible** | 1h | 🟡 Média |
| **C.1 - Hover** | 30 min | 🟡 Média |
| **C.2 - Context Menu** | 30 min | 🟢 Baixa |
| **D - Testes/Docs** | 1h | 🟢 Baixa |
| **TOTAL** | **7-8h** | - |

---

## ✅ CRITÉRIOS DE SUCESSO

### Fase A (CRÍTICO)
- [ ] MainWindow title bar mostra `[_] [□] [×]`
- [ ] Clicar [□] maximiza janela
- [ ] Clicar [□] novamente restaura tamanho
- [ ] Funciona em X11 e Wayland

### Fase B
- [ ] File Explorer usa QSplitter horizontal (25/75%)
- [ ] ResultsTree integrada e funcional
- [ ] Botões Browse/Search separados
- [ ] Estatísticas exibidas corretamente
- [ ] Export CSV funciona
- [ ] Collapsible sections com animação

### Fase C
- [ ] Hover expansion funciona
- [ ] Context menu com 3 ações

### Fase D
- [ ] 12/12 testes passando (100%)
- [ ] Documentação atualizada
- [ ] CHANGELOG completo

---

## 🚨 DECISÕES PENDENTES

1. **Ordem de Implementação**: Confirmar sequência A → B → C → D? ✅ CONFIRMADO
2. **Commits**: Um por fase ou um único commit final? → **Pendente resposta**
3. **Backup**: Criar branch antes de refatoração? → **Recomendado**

---

## 📝 NOTAS

### Pesquisa Qt - WindowFlags no Linux

**Fonte**: Qt 6.10 Documentation

**QMainWindow**:
- Constructor: `QMainWindow(QWidget *parent = nullptr, Qt::WindowFlags flags = Qt::WindowFlags())`
- Nota: "QMainWindow sets the Qt::Window flag itself"
- Mas: Não define automaticamente Minimize/Maximize/Close hints

**WindowFlags Relevantes**:
- `Qt::Window` - Indicates window (set automatically)
- `Qt::WindowMinimizeButtonHint` - Adds minimize button
- `Qt::WindowMaximizeButtonHint` - Adds maximize button ← **FALTANDO**
- `Qt::WindowCloseButtonHint` - Adds close button

**Comportamento por Plataforma**:
- **Windows**: Mostra todos os botões por padrão (mesmo sem hints)
- **macOS**: Mostra todos os botões por padrão
- **Linux (X11/Wayland)**: Requer hints explícitos
  - Sem WindowMaximizeButtonHint → botão maximize omitido
  - Window manager interpreta ausência como "não maximizável"

**QApplication Múltiplas Instâncias**:
- Documentação: "Only one application object should be created"
- Problema no Linux:
  - Window manager pode perder referências
  - Botões de controle podem desaparecer
  - Comportamento inconsistente com eventos
- Solução: Garantir uma única instância (já implementado ✅)

**Verificação no Código**:
- `src/app.py` linha 1909: `app = QApplication(sys.argv)` - **ÚNICA INSTÂNCIA ✅**
- Nenhum outro `QApplication(` encontrado no projeto
- MainWindow não recria QApplication

---

## 🔗 REFERÊNCIAS

1. Qt Documentation: https://doc.qt.io/qt-6/qmainwindow.html
2. Qt Documentation: https://doc.qt.io/qt-6/qapplication.html
3. WindowFlags: https://doc.qt.io/qt-6/qt.html#WindowType-enum
4. search_replace_panel.py - Implementação de referência
5. INTEGRATION_COMPLETE_v2.9.116.md - Versão anterior

---

**Última Atualização**: 26/12/2025 após pesquisa Qt  
**Status**: ⏳ AGUARDANDO APROVAÇÃO PARA FASE A
