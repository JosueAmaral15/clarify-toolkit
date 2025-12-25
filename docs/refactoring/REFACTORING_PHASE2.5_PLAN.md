# Plano de Refatoração - Fase 2.5: Editor Dock

**Data**: 24/12/2024  
**Versão**: v2.9.114  
**Arquivo Alvo**: `src/gui/editor_dock.py` (1069 linhas)

---

## 📊 Análise Inicial

### Estrutura Atual
```
src/gui/editor_dock.py (1069 linhas)
├── SyntaxHighlighter (148 linhas)    # Linhas 41-188
├── EditorTab (344 linhas)            # Linhas 189-533
└── EditorDock (535 linhas)           # Linhas 534-1069
```

### Classes Identificadas

#### 1. SyntaxHighlighter (148 linhas)
- **Propósito**: Syntax highlighting para múltiplos tipos de arquivo
- **Formatos**: HTML/JSX/TSX, JSON, Python, JavaScript/TypeScript
- **Métodos**: `__init__`, `_setup_formats`, `_setup_rules`, `highlightBlock`
- **Candidato**: ✅ Extrair para `src/gui/widgets/syntax_highlighter.py`

#### 2. EditorTab (344 linhas)
- **Propósito**: Tab individual de edição com file tracking
- **Features**: Load/save, modified state, edit-only mode, toolbar
- **Métodos**: ~15 métodos (load_file, save_file, etc.)
- **Candidato**: ✅ Extrair para `src/gui/widgets/editor_tab.py`

#### 3. EditorDock (535 linhas)
- **Propósito**: Container principal com tab management
- **Features**: Multiple tabs, recent files, find/replace, JSON editor
- **Candidato**: ⚠️ Manter (classe principal do dock)

---

## 🎯 Plano de Extração

### Fase 2.5.1: SyntaxHighlighter
**Linhas**: ~180 linhas (com docstrings)
**Arquivo**: `src/gui/widgets/syntax_highlighter.py`

**Componentes**:
- Classe `SyntaxHighlighter(QSyntaxHighlighter)`
- Formatos para cada linguagem
- Regras de matching regex
- Método `highlightBlock()`

**Benefícios**:
- Reutilizável em outros editores
- Fácil adicionar novos tipos de arquivo
- Testável independentemente

---

### Fase 2.5.2: EditorTab
**Linhas**: ~370 linhas (com docstrings)
**Arquivo**: `src/gui/widgets/editor_tab.py`

**Componentes**:
- Classe `EditorTab(QWidget)`
- Text editor com line numbers
- File I/O (load/save)
- Modified state tracking
- Edit-only mode
- Toolbar (copy, export, enable saving)

**Dependências**:
- SyntaxHighlighter (após Fase 2.5.1)

**Benefícios**:
- Widget reutilizável
- Lógica de file I/O isolada
- Facilita testes de edição

---

## 📐 Arquitetura Resultante

```
src/gui/widgets/
├── syntax_highlighter.py (180 linhas) ← NOVO (Fase 2.5.1)
└── editor_tab.py (370 linhas)         ← NOVO (Fase 2.5.2)

src/gui/
└── editor_dock.py (~520 linhas)       ← REDUZIDO (era 1069)
    └── EditorDock: Tab management, recent files, find/replace
```

**Redução Estimada**: ~550 linhas (-51%)

---

## 🔄 Ordem de Execução

### Passo 1: Fase 2.5.1 - SyntaxHighlighter
1. Criar `src/gui/widgets/syntax_highlighter.py`
2. Copiar classe `SyntaxHighlighter` completa
3. Adicionar docstrings e type hints
4. Testar imports
5. Commit: `refactor(v2.9.114): Phase 2.5.1 - Extract SyntaxHighlighter`
6. Tocar three-beeps.mp3

### Passo 2: Fase 2.5.2 - EditorTab
1. Criar `src/gui/widgets/editor_tab.py`
2. Copiar classe `EditorTab` completa
3. Atualizar import de SyntaxHighlighter
4. Adicionar docstrings e type hints
5. Testar imports
6. Commit: `refactor(v2.9.114): Phase 2.5.2 - Extract EditorTab`
7. Tocar three-beeps.mp3

### Passo 3: Integração
1. Atualizar `src/gui/editor_dock.py` imports
2. Remover classes extraídas
3. Atualizar `src/gui/widgets/__init__.py`
4. Testar funcionalidade completa
5. Commit: `refactor(v2.9.114): Phase 2.5 Integration - Complete editor_dock refactoring`
6. Tocar three-beeps.mp3

---

## ✅ Critérios de Sucesso

- [ ] SyntaxHighlighter extrai corretamente
- [ ] EditorTab extrai corretamente
- [ ] Imports funcionam sem erros
- [ ] editor_dock.py reduzido para ~520 linhas
- [ ] Funcionalidade preservada
- [ ] 3 commits realizados
- [ ] 3 beeps tocados
- [ ] Documentação atualizada

---

## 📊 Métricas Esperadas

```
Antes:  1069 linhas (editor_dock.py)
Depois:  520 linhas (editor_dock.py)
        +180 linhas (syntax_highlighter.py)
        +370 linhas (editor_tab.py)
────────────────────────────────────
Total extraído: 550 linhas
Redução: -51%
```

---

**Preparado por**: AI Assistant  
**Protocolo**: SIMPLICIDADE_3.md  
**Status**: 🚀 PRONTO PARA EXECUÇÃO

---

## ✅ STATUS FINAL: COMPLETO

**Data de conclusão**: $(date +%Y-%m-%d)

### Fase 2.5.1: SyntaxHighlighter ✅
- **Commit**: 89ddc25  
- **Arquivo**: src/gui/widgets/syntax_highlighter.py  
- **Linhas**: 190 (código + docstrings)  
- **Status**: Completo

### Fase 2.5.2: EditorTab ✅
- **Commit**: ab8c67b  
- **Arquivo**: src/gui/widgets/editor_tab.py  
- **Linhas**: 397 (código + docstrings)  
- **Status**: Completo

### Fase 2.5 Integration ✅
- **Commit**: 6cf2a3c  
- **Alterações**: Removidas 495 linhas de editor_dock.py  
- **Resultado**: 1069 → 581 linhas (-45.8%)  
- **Status**: Completo

## Métricas Finais

| Métrica | Valor |
|---------|-------|
| **Linhas originais** | 1069 |
| **Linhas finais** | 581 |
| **Redução** | **-45.8% (488 linhas)** |
| **Componentes extraídos** | 2 (SyntaxHighlighter, EditorTab) |
| **Total extraído** | 587 linhas |
| **Commits** | 3 |
| **Protocol seguido** | ✅ Análise → Extract → Test → Commit → Beep |

## Próximas Fases Disponíveis

- **Fase 2.6**: json_editor_tab.py (957 linhas)  
- **Fase 2.7**: search_replace_panel.py (910 linhas)  
- **Fase 3.0**: app.py (4533 linhas) 🎯 CRÍTICO
