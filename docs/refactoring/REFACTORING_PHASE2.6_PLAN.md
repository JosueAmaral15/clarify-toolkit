# Plano de Refatoração - Fase 2.6: JSON Editor Tab

**Data**: 24/12/2024  
**Versão**: v2.9.114  
**Arquivo Alvo**: `src/gui/json_editor_tab.py` (957 linhas)

---

## 📊 Análise Inicial

### Estrutura Atual
```
src/gui/json_editor_tab.py (957 linhas)
├── JsonTreeWidget (116 linhas)       # Linhas 41-156
├── JsonSearchDialog (176 linhas)     # Linhas 157-332
└── JsonEditorTab (625 linhas)        # Linhas 333-957
```

### Classes Identificadas

#### 1. JsonTreeWidget (116 linhas)
- **Propósito**: Tree widget para navegação na estrutura JSON
- **Pattern**: Composite (GoF) - estrutura recursiva de árvore
- **Features**:
  - Click node → jump to line
  - Collapse/Expand controls
  - Visual indicators: {} objects, [] arrays
  - Color coding por tipo (Object, Array, String, Number, Boolean, Null)
- **Métodos**: `__init__`, `_on_item_clicked`, `build_tree`, `_add_node`
- **Signal**: `node_clicked(int)` - emite linha quando nó clicado
- **Candidato**: ✅ Extrair para `src/gui/widgets/json_tree_widget.py`

#### 2. JsonSearchDialog (176 linhas)
- **Propósito**: Dialog de busca para encontrar keys/values no JSON
- **Pattern**: Command (GoF) - encapsula operação de busca
- **Features**:
  - Find All com regex support
  - Case sensitive option
  - Keys Only / Values Only filters
  - Next/Previous navigation
  - Yellow highlight para matches
- **Métodos**: `__init__`, `_setup_ui`, `_connect_signals`, `_find_all`, `_find_next`, `_find_prev`, `_highlight_current_match`, `_clear_highlights`
- **Candidato**: ✅ Extrair para `src/gui/dialogs/json_search_dialog.py`

#### 3. JsonEditorTab (625 linhas)
- **Propósito**: Tab principal do editor JSON com todas as features
- **Patterns**: Facade (simplifica operações), Observer (signals)
- **Features**:
  - Real-time validation
  - Format JSON (2/4 spaces)
  - Tree view integration
  - Search dialog integration
  - Insert/Regex Insert panels
  - Load/Save files
  - Edit-only mode
- **Métodos**: ~30 métodos (muito complexo)
- **Decision**: ⚠️ **MANTER** - é a classe principal, mas simplificada com extrações

---

## 🎯 Estratégia de Refatoração

### Fase 2.6.1: JsonTreeWidget (~130 linhas)
**Extração de componente de navegação JSON**

**Arquivo destino**: `src/gui/widgets/json_tree_widget.py`

**Conteúdo**:
- Classe `JsonTreeWidget` completa
- Pattern: Composite (GoF)
- Signal: `node_clicked(int)`
- Métodos:
  - `__init__`: Setup tree com headers e colors
  - `_on_item_clicked`: Handle click events
  - `build_tree(json_text)`: Build tree from JSON
  - `_add_node(parent, key, value, line)`: Recursive node addition
- Color scheme:
  - Objects: Light blue (#9CDCFE)
  - Arrays: Teal (#4EC9B0)
  - Strings: Orange (#CE9178)
  - Booleans: Blue (#569CD6)
  - Numbers: Light green (#B5CEA8)
  - Null: Gray (#808080)

**Imports necessários**:
```python
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QColor
from typing import Optional, Dict, Any
import json
```

**Teste**:
```python
from src.gui.widgets import JsonTreeWidget
tree = JsonTreeWidget()
tree.build_tree('{"key": "value"}')
```

---

### Fase 2.6.2: JsonSearchDialog (~190 linhas)
**Extração de dialog de busca JSON**

**Arquivo destino**: `src/gui/dialogs/json_search_dialog.py`

**Conteúdo**:
- Classe `JsonSearchDialog` completa
- Pattern: Command (GoF)
- Métodos:
  - `__init__(editor, parent)`: Setup dialog
  - `_setup_ui()`: Create UI components
  - `_connect_signals()`: Connect button signals
  - `_find_all()`: Execute search (regex patterns)
  - `_find_next()`: Navigate to next match
  - `_find_prev()`: Navigate to previous match
  - `_highlight_current_match()`: Yellow highlight
  - `_clear_highlights()`: Clear all highlights
- Features:
  - Case sensitive checkbox
  - Keys Only / Values Only filters
  - Match counter: "Match X of Y"
  - Navigation buttons

**Imports necessários**:
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QMessageBox, QTextEdit
)
from PySide6.QtGui import QColor, QTextCursor, QTextCharFormat
from typing import List, Tuple
import re
```

**Teste**:
```python
from src.gui.dialogs import JsonSearchDialog
from PySide6.QtWidgets import QTextEdit
editor = QTextEdit()
dialog = JsonSearchDialog(editor)
```

---

### Fase 2.6 Integration
**Atualizar json_editor_tab.py para usar componentes extraídos**

**Mudanças**:
1. Remover definições de `JsonTreeWidget` e `JsonSearchDialog`
2. Adicionar imports:
   ```python
   from .widgets import JsonTreeWidget
   from .dialogs import JsonSearchDialog
   ```
3. Manter apenas classe `JsonEditorTab` (~625 linhas)
4. Verificar que todas as referências funcionam

**Testes**:
- Import do módulo: `from src.gui.json_editor_tab import JsonEditorTab`
- Instanciação: `tab = JsonEditorTab()`
- Tree navigation: Click em node → jump to line
- Search dialog: Open search → find matches

---

## 📈 Métricas Esperadas

| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **json_editor_tab.py** | 957 linhas | ~650 linhas | **-32%** |
| **Componentes extraídos** | 0 | 2 | +2 |
| **Total extraído** | 0 | ~307 linhas | - |

### Detalhamento
- JsonTreeWidget: ~130 linhas (41-156 + docstrings)
- JsonSearchDialog: ~190 linhas (157-332 + docstrings)
- Total extraído: **~320 linhas**

---

## 🔄 Ordem de Execução

### 1. Fase 2.6.1: JsonTreeWidget
- [ ] Criar `src/gui/widgets/json_tree_widget.py`
- [ ] Extrair classe completa (116 linhas)
- [ ] Adicionar docstrings e type hints
- [ ] Atualizar `src/gui/widgets/__init__.py`
- [ ] Testar import e instanciação
- [ ] Commitar: `refactor(v2.9.114): Phase 2.6.1 - Extract JsonTreeWidget`
- [ ] Tocar beep

### 2. Fase 2.6.2: JsonSearchDialog
- [ ] Criar `src/gui/dialogs/` directory (se não existir)
- [ ] Criar `src/gui/dialogs/__init__.py`
- [ ] Criar `src/gui/dialogs/json_search_dialog.py`
- [ ] Extrair classe completa (176 linhas)
- [ ] Adicionar docstrings e type hints
- [ ] Testar import e instanciação
- [ ] Commitar: `refactor(v2.9.114): Phase 2.6.2 - Extract JsonSearchDialog`
- [ ] Tocar beep

### 3. Fase 2.6 Integration
- [ ] Atualizar imports no json_editor_tab.py
- [ ] Remover classes extraídas
- [ ] Verificar: 957 → ~650 linhas
- [ ] Testar funcionalidade completa
- [ ] Commitar: `refactor(v2.9.114): Phase 2.6 Integration - Clean json_editor_tab`
- [ ] Tocar beep

---

## 🎯 Resultado Esperado

**Estrutura final**:
```
src/gui/widgets/
├── json_tree_widget.py      (novo - ~130 linhas)
└── ...

src/gui/dialogs/
├── __init__.py               (novo)
└── json_search_dialog.py     (novo - ~190 linhas)

src/gui/json_editor_tab.py    (reduzido - ~650 linhas)
```

**Benefícios**:
- ✅ Separação de responsabilidades (SRP)
- ✅ JsonTreeWidget reutilizável em outros editores
- ✅ JsonSearchDialog reutilizável com qualquer QTextEdit
- ✅ JsonEditorTab focado em lógica de negócio
- ✅ Facilita testes unitários
- ✅ Manutenção simplificada

---

## 📝 Notas

- **Pattern Composite**: JsonTreeWidget usa recursão para construir árvore
- **Pattern Command**: JsonSearchDialog encapsula operação de busca
- **Pattern Facade**: JsonEditorTab simplifica operações complexas
- **Pattern Observer**: Signals para comunicação entre componentes

**Próximas fases após 2.6**:
- Fase 2.7: search_replace_panel.py (910 linhas)
- Fase 3.0: app.py (4533 linhas) 🎯 CRÍTICO
