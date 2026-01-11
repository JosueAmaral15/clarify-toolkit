# PLANO DE AÇÃO: Correção "Open and Switch to Editor"

**Data:** 2026-01-11  
**Versão:** v2.9.121  
**Tipo:** Correção de Bugs  
**Tempo Estimado:** 20 minutos

---

## 🐛 BUGS IDENTIFICADOS

### Bug #1: Texto de Tradução Aparece como Objeto
**Sintoma:** Menu mostra objeto ao invés de "Abrir e Mudar para Editor"  
**Causa:** `tr()` usado sem import correto  
**Severidade:** 🔴 ALTA (UX quebrado)

### Bug #2: Sobrescreve Tab File Explorer
**Sintoma:** Editor abre POR CIMA do File Explorer na mesma tab  
**Causa:** Código troca widget da tab ao invés de mudar para outra tab  
**Severidade:** 🔴 CRÍTICA (comportamento incorreto)

---

## 📋 REQUISITOS (Confirmados pelo Usuário)

1. ✅ Se Editor existe como tab → Mudar para tab existente
2. ✅ Se Editor não existe → Criar nova tab (como File → Open Editor)
3. ✅ File Explorer permanece na sua tab original
4. ✅ Editor abre em tab SEPARADA (não sobrescrever)
5. ✅ Usar `main_window._show_editor()` ou método equivalente

---

## 🎯 TAREFAS INTERMEDIÁRIAS

### Fase 1: Diagnóstico (5 min)
- [ ] 1.1 Verificar imports de `tr()` nos arquivos modificados
- [ ] 1.2 Encontrar método `_show_editor()` no MainWindow
- [ ] 1.3 Entender como tabs são gerenciadas no Clarify
- [ ] 1.4 Identificar linha exata que causa sobrescrita da tab

### Fase 2: Correção Bug #1 - Tradução (3 min)
- [ ] 2.1 Adicionar `from src.i18n.translator import tr` em file_list_table_manager.py
- [ ] 2.2 Adicionar `from src.i18n.translator import tr` em results_tree.py (verificar se já existe)
- [ ] 2.3 Testar que tradução funciona

### Fase 3: Correção Bug #2 - Tab Switching (10 min)
- [ ] 3.1 Remover código que troca widget da tab atual
- [ ] 3.2 Implementar chamada a `main_window._show_editor()` ou equivalente
- [ ] 3.3 Garantir que Editor abre como nova tab se não existe
- [ ] 3.4 Garantir que muda para tab Editor se já existe
- [ ] 3.5 Verificar que File Explorer permanece intacto

### Fase 4: Validação (2 min)
- [ ] 4.1 Teste sintático (importar módulos)
- [ ] 4.2 Commit com mensagem clara
- [ ] 4.3 Push para repositório

---

## 📝 PLANO DE EXECUÇÃO DETALHADO

### FASE 1: DIAGNÓSTICO

#### Tarefa 1.1: Verificar imports de tr()
```bash
# Verificar se tr está importado
grep -n "^from.*import.*tr" src/gui/widgets/file_list_table_manager.py
grep -n "^from.*import.*tr" src/gui/panels/results_tree.py
```

**Resultado esperado:**
- file_list_table_manager.py: Pode não ter import
- results_tree.py: Já deve ter (linha ~7)

#### Tarefa 1.2: Encontrar _show_editor()
```bash
grep -n "def _show_editor" src/app.py
```

**Resultado esperado:** Método existe, provavelmente linha ~905

#### Tarefa 1.3: Entender gerenciamento de tabs
```bash
grep -n "tab_widget_main" src/app.py | head -20
grep -n "_add_tool_tab" src/app.py | head -10
```

**Resultado esperado:** 
- `tab_widget_main` é o QTabWidget principal
- `_add_tool_tab()` adiciona tool como nova tab
- `_show_editor()` usa `_add_tool_tab()`

#### Tarefa 1.4: Identificar linha que causa bug
**Localização:** 
- `src/gui/widgets/file_list_table_manager.py` linha ~346-352
- `src/gui/panels/results_tree.py` linha ~659-665

**Código problemático:**
```python
# ERRADO: Procura tab com nome "Editor" e troca widget
for i in range(tab_widget.count()):
    tab_name = tab_widget.tabText(i)
    if 'Editor' in tab_name or tab_widget.widget(i) == main_window.dock_editor:
        tab_widget.setCurrentIndex(i)  # ← Só muda index, não cria tab!
        break
```

**Problema:** 
- Se encontra tab File Explorer com index, muda para ela
- Mas depois mostra Editor Dock por cima (show/raise)
- Resultado: Editor sobrescreve File Explorer visualmente

---

### FASE 2: CORREÇÃO BUG #1 - TRADUÇÃO

#### Tarefa 2.1: Adicionar import em file_list_table_manager.py

**Arquivo:** `src/gui/widgets/file_list_table_manager.py`

**Ação:** Verificar se `tr` está importado. Se não, adicionar:
```python
from src.i18n.translator import tr
```

**Localização:** Junto com outros imports no topo do arquivo (linhas 1-40)

#### Tarefa 2.2: Verificar import em results_tree.py

**Arquivo:** `src/gui/panels/results_tree.py`

**Ação:** Verificar linha ~7. Deve ter:
```python
from ...i18n import tr
```

**Se não tiver:** Adicionar import correto.

#### Tarefa 2.3: Testar tradução

**Comando:**
```bash
python -c "
from src.i18n.translator import tr
resultado = tr('table_manager.action_open_and_switch')
print(f'Tradução: {resultado}')
assert resultado == 'Abrir e Mudar para Editor', f'Esperado PT-BR, recebeu: {resultado}'
print('✅ Tradução funcionando')
"
```

---

### FASE 3: CORREÇÃO BUG #2 - TAB SWITCHING

#### Tarefa 3.1: Identificar código problemático

**Arquivo 1:** `src/gui/widgets/file_list_table_manager.py`

**Linhas problemáticas:** ~343-361 (dentro de `_open_in_editor_and_switch()`)

```python
# CÓDIGO ATUAL (ERRADO):
# Switch to Editor tab in main window
if last_opened_filepath:
    # Find Editor tab and activate it
    if hasattr(main_window, 'tab_widget_main'):
        tab_widget = main_window.tab_widget_main
        # Search for Editor tab
        for i in range(tab_widget.count()):
            tab_name = tab_widget.tabText(i)
            if 'Editor' in tab_name or tab_widget.widget(i) == main_window.dock_editor:
                tab_widget.setCurrentIndex(i)
                break
    
    # Show and raise editor dock
    main_window.dock_editor.show()
    main_window.dock_editor.raise_()
```

**Problema:** 
- Procura tab com "Editor" no nome
- Se não encontra, não faz nada
- Depois `show()` e `raise_()` mostram dock por cima da tab atual

#### Tarefa 3.2: Implementar solução correta

**Solução:** Chamar `_show_editor()` que já gerencia tudo corretamente

**Código novo:**
```python
# Switch to Editor tab (create if doesn't exist)
if last_opened_filepath:
    # Use existing _show_editor() method which handles tab creation/switching
    if hasattr(main_window, '_show_editor'):
        main_window._show_editor()
    else:
        # Fallback: manual tab management
        if hasattr(main_window, 'tab_widget_main'):
            # Search for existing Editor tab
            tab_widget = main_window.tab_widget_main
            editor_tab_index = -1
            
            for i in range(tab_widget.count()):
                widget = tab_widget.widget(i)
                if widget == main_window.dock_editor:
                    editor_tab_index = i
                    break
            
            if editor_tab_index >= 0:
                # Editor tab exists, switch to it
                tab_widget.setCurrentIndex(editor_tab_index)
            else:
                # Editor tab doesn't exist, create it
                if hasattr(main_window, '_add_tool_tab'):
                    main_window._add_tool_tab(main_window.dock_editor, "Editor", "editor")
```

#### Tarefa 3.3: Implementar focus na tab do arquivo

**Após** mudar para tab Editor, focar na tab do arquivo dentro do Editor:

```python
    # Focus on the last opened file's tab within Editor
    if hasattr(main_window.dock_editor, 'tab_widget'):
        editor_tabs = main_window.dock_editor.tab_widget
        # Find tab with matching filepath
        for i in range(editor_tabs.count()):
            tab = editor_tabs.widget(i)
            if hasattr(tab, 'file_path') and tab.file_path == last_opened_filepath:
                editor_tabs.setCurrentIndex(i)
                break
```

#### Tarefa 3.4: Aplicar mesma correção em results_tree.py

**Arquivo 2:** `src/gui/panels/results_tree.py`

**Linhas:** ~657-675 (mesmo código problemático)

**Ação:** Aplicar mesma solução (chamar `_show_editor()`)

---

### FASE 4: VALIDAÇÃO

#### Tarefa 4.1: Teste sintático

```bash
python -c "
import sys
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

# Importar módulos corrigidos
from src.gui.widgets.file_list_table_manager import FileListTableManager
from src.gui.panels.results_tree import ResultsTree

print('✅ Imports bem-sucedidos')

# Verificar que tr está importado
from src.i18n.translator import tr
resultado = tr('table_manager.action_open_and_switch')
print(f'✅ Tradução: {resultado}')

print('✅ Código compilou sem erros!')
"
```

#### Tarefa 4.2: Commit

```bash
git add -A
git commit -m "fix: correct translation and tab switching for 'Open and Switch to Editor'

Bug #1: Translation object appearing instead of text
- Added missing 'from src.i18n.translator import tr' import
- Now correctly shows 'Abrir e Mudar para Editor' in PT-BR

Bug #2: Editor overwrites File Explorer tab
- Removed manual tab widget manipulation
- Now calls main_window._show_editor() which properly handles:
  * Creating Editor tab if doesn't exist
  * Switching to existing Editor tab if already open
  * NOT overwriting current tab (File Explorer remains intact)
- File Explorer stays in its original tab
- Editor opens/activates in separate tab

Files modified:
- src/gui/widgets/file_list_table_manager.py: Fix import + tab logic
- src/gui/panels/results_tree.py: Fix import + tab logic

Testing: Manual validation after restart required"
```

#### Tarefa 4.3: Push

```bash
git push origin main
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Após correção, usuário deve verificar:

- [ ] Menu mostra "Abrir e Mudar para Editor" (não objeto)
- [ ] File Explorer permanece em sua tab
- [ ] Editor abre em tab separada (ou muda para existente)
- [ ] Tab do arquivo dentro do Editor fica em foco
- [ ] Múltiplos arquivos: último arquivo focado
- [ ] Funciona em Table Mode
- [ ] Funciona em Tree Mode

---

## 🎯 RESULTADO ESPERADO

**Antes (Bugado):**
```
[File Explorer Tab] ← Usuário aqui
  → Clica "Open and Switch to Editor"
  → Objeto aparece no menu ❌
  → Editor sobrescreve File Explorer visualmente ❌
```

**Depois (Correto):**
```
[File Explorer Tab] ← Usuário aqui
  → Clica "Abrir e Mudar para Editor" ✅
  → [Editor Tab] criada/ativada
  → Usuário transferido para [Editor Tab] ✅
  → [File Explorer Tab] permanece intacta ✅
```

---

## ⏱️ TIMELINE

| Fase | Tempo | Acumulado |
|------|-------|-----------|
| 1. Diagnóstico | 5 min | 5 min |
| 2. Fix Tradução | 3 min | 8 min |
| 3. Fix Tab Switching | 10 min | 18 min |
| 4. Validação | 2 min | **20 min** |

---

**Status:** 📝 PLANEJAMENTO COMPLETO  
**Próximo passo:** Executar Fase 1 (Diagnóstico)
