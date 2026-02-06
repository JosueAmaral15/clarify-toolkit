# Investigação e Planejamento: Feature "Open in Editor" no File Explorer
**Data:** 2026-01-11  
**Protocolo:** Simplicidade 3  
**Fase:** Investigation & Root Cause Analysis  
**Desenvolvedor:** AI Assistant + Josué Amaral

---

## 📋 Índice

1. [Requisito do Usuário](#requisito-do-usuário)
2. [Etapa 1.0: Busca e Leitura de Documentação](#etapa-10-busca-e-leitura-de-documentação)
3. [Investigação Arquitetural](#investigação-arquitetural)
4. [Root Cause Analysis](#root-cause-analysis)
5. [Gap Analysis](#gap-analysis)
6. [Solution Design](#solution-design)
7. [Action Plan Detalhado](#action-plan-detalhado)
8. [Riscos e Mitigações](#riscos-e-mitigações)

---

## 🎯 Requisito do Usuário

### Descrição Original
> "Quando eu pesquisar por um arquivo, e ver o resultado em modo table, quando eu clicar em 'Open in Editor', eu quero abrir o conteúdo e o arquivo no editor do Clarify."

### Interpretação
**Comportamento Esperado:**
1. Usuário faz busca no File Explorer
2. Resultados aparecem em modo Table
3. Usuário clica com botão direito em um arquivo na tabela
4. Seleciona "Open in Editor" no menu de contexto
5. **ESPERADO:** Arquivo JSON abre no Editor Dock do Clarify com conteúdo carregado
6. **ATUAL:** [A INVESTIGAR]

### Critérios de Sucesso
- ✅ Arquivo JSON abre no Editor Dock
- ✅ Conteúdo do arquivo é carregado automaticamente
- ✅ Usuário pode editar o arquivo no Editor
- ✅ Mudanças podem ser salvas de volta no arquivo
- ✅ Funciona para ambos Table e Tree view (se aplicável)

---

## 📚 Etapa 1.0: Busca e Leitura de Documentação

### 1.1 Arquivos Identificados

**File Explorer:**
- ✅ `src/gui/file_explorer_dock.py` (1,789 linhas) - Dock principal
- ✅ `src/gui/widgets/file_list_table_manager.py` (428 linhas) - Gerencia tabela
- ✅ `src/core/file_explorer_executor.py` (628 linhas) - Executor de busca

**Editor:**
- ✅ `src/gui/editor_dock.py` - Editor Dock principal
- ✅ `src/gui/widgets/editor_tab.py` - Tabs do editor
- ✅ `src/gui/json_editor_tab.py` - Tab específica para JSON

**Testes Existentes:**
- ✅ `tests/test_open_in_editor.py` - **EXISTE TESTE!**
- ✅ `tests/test_docks_factory.py` - Factory de docks

**Documentação:**
- ✅ `CHANGELOG.md` - Menciona "Open in Editor"
- ✅ `docs/TASKS.md` - Possíveis tasks relacionadas
- ✅ `docs/study/FASE_3_ESTUDO_PROFUNDO.md` - Estudo arquitetural

### 1.2 Leitura de Código Crítico

**AGUARDANDO:** Leitura dos arquivos identificados para entender:
- Como menu de contexto funciona atualmente
- Como Editor Dock é invocado
- Como arquivos são abertos no editor
- Se "Open in Editor" já está parcialmente implementado

---

## 🔍 Investigação Arquitetural

### 2.1 Arquitetura Atual (Hipóteses)

```
File Explorer Dock
    ├── Table View (QTableWidget)
    │   ├── Context Menu
    │   │   ├── "Open in Editor" ← NOSSO FOCO
    │   │   ├── "Open Externally"
    │   │   ├── "Export CSV"
    │   │   └── ...
    │   └── Double-click behavior
    └── Tree View (QTreeWidget)
        └── Context Menu
            └── ...

Editor Dock
    ├── Tab Widget
    │   ├── JSON Editor Tab
    │   ├── Text Editor Tab
    │   └── ...
    └── API para abrir arquivos
        ├── open_file(path)
        ├── load_content()
        └── create_new_tab()
```

### 2.2 Pontos de Integração

**Possíveis pontos onde implementar:**
1. `file_explorer_dock.py` - Adicionar ação no menu de contexto
2. `file_list_table_manager.py` - Handler do menu de contexto
3. `app.py` - Coordenar comunicação entre docks
4. `editor_dock.py` - API para receber arquivos externos

---

## 🧪 Root Cause Analysis

### Estado Atual (A SER CONFIRMADO)

**Hipótese 1:** "Open in Editor" NÃO existe
- Menu de contexto não tem essa opção
- Precisa criar do zero

**Hipótese 2:** "Open in Editor" existe mas não funciona
- Opção existe no menu
- Mas não abre no Editor interno do Clarify
- Pode abrir em editor externo (sistema operacional)

**Hipótese 3:** "Open in Editor" funciona parcialmente
- Abre editor mas não carrega conteúdo
- Carrega conteúdo mas não funciona para todos tipos
- Funciona em alguns contextos mas não no File Explorer

**AÇÃO:** Preciso ler código para confirmar qual hipótese é correta.

---

## 📊 Gap Analysis

### O Que Existe vs O Que Falta

| Componente | Status | Notas |
|------------|--------|-------|
| File Explorer Table | ✅ Existe | Mostra resultados de busca |
| Context Menu | ❓ A verificar | Precisa ver quais ações existem |
| "Open in Editor" Action | ❓ A verificar | Pode existir mas não funcionar |
| Editor Dock | ✅ Existe | Editor principal do Clarify |
| Editor API | ❓ A verificar | Método para abrir arquivo externo? |
| Signal/Slot Connection | ❓ A verificar | Comunicação File Explorer → Editor |
| Testes | ✅ Existe | `test_open_in_editor.py` |

---

## 🎨 Solution Design (DRAFT)

### Abordagem Proposta

**Estratégia:** Criar comunicação entre File Explorer e Editor usando Signals/Slots do Qt

**Fluxo proposto:**
```python
# 1. File Explorer (src/gui/file_explorer_dock.py)
class FileExplorerDock:
    # Novo signal
    open_in_editor_requested = Signal(str)  # Emite caminho do arquivo
    
    def _create_context_menu(self):
        # Adicionar ação "Open in Editor"
        action = QAction("Open in Editor", self)
        action.triggered.connect(self._on_open_in_editor)
        menu.addAction(action)
    
    def _on_open_in_editor(self):
        selected_file = self.get_selected_file_path()
        self.open_in_editor_requested.emit(selected_file)

# 2. Main App (src/app.py)
class ClarifyApp:
    def _setup_docks(self):
        # Conectar signal do File Explorer ao Editor
        self.file_explorer.open_in_editor_requested.connect(
            self.editor_dock.open_file_from_external
        )

# 3. Editor Dock (src/gui/editor_dock.py)
class EditorDock:
    def open_file_from_external(self, file_path: str):
        """Abre arquivo vindo de dock externo."""
        # Carregar conteúdo
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Criar nova tab
        self.create_tab_with_content(file_path, content)
        
        # Mostrar dock se estiver escondido
        self.show()
        self.raise_()
```

### Arquivos a Modificar

1. **`src/gui/file_explorer_dock.py`**
   - Adicionar signal `open_in_editor_requested`
   - Adicionar ação no context menu
   - Implementar handler `_on_open_in_editor()`

2. **`src/gui/widgets/file_list_table_manager.py`**
   - Modificar `_show_context_menu()` se necessário
   - Garantir que seleção de arquivo está disponível

3. **`src/gui/editor_dock.py`**
   - Adicionar método `open_file_from_external(file_path)`
   - Garantir que conteúdo é carregado corretamente
   - Gerenciar tabs (criar nova ou usar existente?)

4. **`src/app.py`**
   - Conectar signal File Explorer → Editor
   - Garantir que ambos docks estão inicializados

5. **`tests/test_open_in_editor.py`**
   - Atualizar ou criar testes
   - Testar fluxo completo

---

## 📝 Action Plan Detalhado

### Phase 1: Investigation (CURRENT - 30min)
```markdown
[ ] 1.1. Ler src/gui/file_explorer_dock.py completo
[ ] 1.2. Ler src/gui/widgets/file_list_table_manager.py (menu contexto)
[ ] 1.3. Ler src/gui/editor_dock.py (API disponível)
[ ] 1.4. Ler tests/test_open_in_editor.py (entender expectativas)
[ ] 1.5. Confirmar hipótese (qual das 3 está correta)
[ ] 1.6. Documentar findings neste arquivo
```

**Tempo estimado:** 30 minutos  
**Output:** Seção "Findings" completa neste documento

---

### Phase 2: Root Cause Analysis (15min)
```markdown
[ ] 2.1. Identificar exatamente o que falta
[ ] 2.2. Verificar se há código órfão ou bugado
[ ] 2.3. Documentar estado atual vs estado desejado
[ ] 2.4. Criar diagrama de fluxo atual vs novo
```

**Tempo estimado:** 15 minutos  
**Output:** Diagrama de fluxo + Gap analysis atualizado

---

### Phase 3: Solution Design (20min)
```markdown
[ ] 3.1. Definir exatamente quais métodos criar/modificar
[ ] 3.2. Planejar estrutura de Signals/Slots
[ ] 3.3. Decidir comportamento (nova tab vs reusar tab)
[ ] 3.4. Verificar i18n (traduzir "Open in Editor"?)
[ ] 3.5. Planejar tratamento de erros (arquivo não encontrado, etc.)
[ ] 3.6. Criar checklist de implementação
```

**Tempo estimado:** 20 minutos  
**Output:** Design Document completo

---

### Phase 4: Implementation (45min)
```markdown
[ ] 4.1. Modificar file_explorer_dock.py (signal + ação menu)
[ ] 4.2. Modificar editor_dock.py (método open_file_from_external)
[ ] 4.3. Modificar app.py (conectar signal/slot)
[ ] 4.4. Adicionar i18n strings necessárias
[ ] 4.5. Tratar edge cases (arquivo não existe, permissões, etc.)
```

**Tempo estimado:** 45 minutos  
**Output:** Código funcional

---

### Phase 5: Testing (30min)
```markdown
[ ] 5.1. Testes manuais
  [ ] - Buscar arquivo no File Explorer
  [ ] - Clicar botão direito
  [ ] - Selecionar "Open in Editor"
  [ ] - Verificar que abre no Editor
  [ ] - Verificar que conteúdo está carregado
  [ ] - Testar com arquivo grande (>1MB)
  [ ] - Testar com arquivo inexistente
  [ ] - Testar com arquivo sem permissão

[ ] 5.2. Atualizar test_open_in_editor.py
  [ ] - Testar signal emission
  [ ] - Testar slot reception
  [ ] - Testar carregamento de conteúdo
  [ ] - Testar criação de tab

[ ] 5.3. Executar testes automatizados
  [ ] - pytest tests/test_open_in_editor.py
  [ ] - pytest tests/test_file_explorer_integration.py
```

**Tempo estimado:** 30 minutos  
**Output:** Todos testes passando

---

### Phase 6: Documentation & Commit (15min)
```markdown
[ ] 6.1. Atualizar CHANGELOG.md
[ ] 6.2. Documentar funcionalidade (se necessário)
[ ] 6.3. Commit com mensagem descritiva
[ ] 6.4. Push para repositório
```

**Tempo estimado:** 15 minutos  
**Output:** Feature commitada

---

## ⏱️ Time Budget

| Phase | Estimativa | Acumulado |
|-------|-----------|-----------|
| 1. Investigation | 30 min | 30 min |
| 2. Root Cause | 15 min | 45 min |
| 3. Design | 20 min | 1h 05min |
| 4. Implementation | 45 min | 1h 50min |
| 5. Testing | 30 min | 2h 20min |
| 6. Documentation | 15 min | **2h 35min** |

**Total estimado:** 2 horas e 35 minutos

---

## ⚠️ Riscos e Mitigações

### Risco 1: Editor não tem API para abrir arquivo externo
**Probabilidade:** Baixa  
**Impacto:** Alto  
**Mitigação:** Se não tiver, criar a API. Tempo adicional: +20min.

### Risco 2: Conflito de tabs (múltiplos arquivos abertos)
**Probabilidade:** Média  
**Impacto:** Médio  
**Mitigação:** Implementar lógica de reutilização de tabs ou sempre criar nova.

### Risco 3: Tipos de arquivo não JSON
**Probabilidade:** Média  
**Impacto:** Médio  
**Mitigação:** Detectar tipo de arquivo e usar editor apropriado (JSON vs Text).

### Risco 4: Arquivos muito grandes (>10MB)
**Probabilidade:** Baixa  
**Impacto:** Alto (pode travar UI)  
**Mitigação:** Adicionar warning para arquivos grandes + carregamento assíncrono.

### Risco 5: Permissões de leitura negadas
**Probabilidade:** Baixa  
**Impacto:** Médio  
**Mitigação:** Try/except com mensagem clara ao usuário.

---

## 🎯 Next Steps

**Aguardando confirmação do usuário para prosseguir:**
1. ✅ Protocolo Simplicidade 3 lido
2. ✅ Documento de investigação criado
3. ⏳ **ATUAL:** Aguardando OK para iniciar Phase 1 (leitura de código)

**Após OK:**
- Ler arquivos identificados
- Completar seções "Findings" e "Root Cause"
- Atualizar Solution Design
- Implementar feature

---

**Status:** 📋 INVESTIGAÇÃO INICIAL COMPLETA - AGUARDANDO LEITURA DE CÓDIGO  
**Próxima ação:** Ler arquivos críticos identificados  
**Tempo investido até agora:** ~15 minutos (criação deste documento)  
**Tempo restante estimado:** ~2h 20min
