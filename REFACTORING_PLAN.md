# Plano de Refatoração do Clarify - v2.9.114

## Objetivo
Reduzir app.py de ~7000 linhas para ~2500 linhas, melhorando manutenibilidade e reutilização.

## Status Atual
- **app.py**: 6935 linhas
- **Arquivos grandes identificados**:
  - app.py (6934 linhas) ⚠️ PRIORIDADE
  - ai_processor_dock.py (1284 linhas)
  - json_rewriter_dock.py (1229 linhas)
  - set_operations_dock.py (1148 linhas)
  - editor_dock.py (1069 linhas)

## Fase 1: Extrair classes de app.py ✅ INICIADO

### 1.1 Progress Management (src/gui/progress/) - EM ANDAMENTO
- [x] OperationHistory (50 linhas) → operation_history.py
- [ ] ProgressDetailsDialog (120 linhas) → progress_details_dialog.py
- [ ] ProgressBarWidget (200 linhas) → progress_bar_widget.py
- [ ] ProgressManager (115 linhas) → progress_manager.py

**Impacto**: Redução de ~485 linhas

### 1.2 Search/Replace Components (src/gui/panels/)
- [ ] SearchWorker (100 linhas) → search_worker.py
- [ ] ResultsTree (300 linhas) → results_tree.py
- [ ] MatchPanel (100 linhas) → match_panel.py
- [ ] MatchListModel (20 linhas) → match_list_model.py
- [ ] SearchReplacePanel (800 linhas) → search_replace_panel.py

**Impacto**: Redução de ~1320 linhas

### 1.3 Insert Panel (src/gui/panels/)
- [ ] InsertPanel (950 linhas) → insert_panel.py

**Impacto**: Redução de ~950 linhas

### 1.4 Translation (src/translators/)
- [ ] CodeAwareJSONTranslator (380 linhas) → code_aware_translator.py

**Impacto**: Redução de ~380 linhas

**Total Fase 1**: ~3135 linhas reduzidas → app.py ficará com ~3800 linhas

## Fase 2: Refatorar outros arquivos grandes

### 2.1 ai_processor_dock.py (1284 linhas)
- [ ] Extrair classes de prompts para src/ai/prompts/
- [ ] Separar lógica de UI de lógica de negócio

### 2.2 json_rewriter_dock.py (1229 linhas)
- [ ] Mover operações para src/rewriter/operations/
- [ ] Separar UI de lógica de transformação

### 2.3 set_operations_dock.py (1148 linhas)
- [ ] Extrair operações de conjuntos para src/core/set_ops/
- [ ] Simplificar UI

## Fase 3: Melhorias estruturais

### 3.1 Criar módulos utilitários
- [ ] src/utils/file_utils.py - operações de arquivo comuns
- [ ] src/utils/ui_utils.py - helpers de UI
- [ ] src/utils/validation.py - validações reutilizáveis

### 3.2 Consolidar importações
- [ ] Criar __all__ em cada módulo
- [ ] Simplificar importações em app.py

## Estimativa
- **Tempo total**: 2-3 horas
- **Redução esperada**: app.py de 7000 → 2500 linhas
- **Benefícios**: 
  - ✅ Código mais testável
  - ✅ Melhor reutilização
  - ✅ IDE mais responsiva
  - ✅ Menos conflitos em git
  - ✅ Onboarding mais fácil

## Próximos Passos
1. Completar extração de progress management
2. Extrair SearchReplacePanel e componentes
3. Extrair InsertPanel
4. Testar aplicação completa
5. Commit final

---
Iniciado em: 2025-12-24
Status: 🟡 EM PROGRESSO (Fase 1.1)
