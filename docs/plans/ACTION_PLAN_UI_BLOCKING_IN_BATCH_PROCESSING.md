# ACTION PLAN: Fix UI Blocking During Batch Processing

**Created:** 2026-01-12 (após estudo completo do código)  
**Protocol:** Protocolo Simplicidade 3 - Etapa 2 (Planejamento BLOQUEANTE)  
**Author:** GitHub Copilot CLI  
**Status:** 🟡 Planning Complete, Awaiting User Approval

---

## 1. CONTEXTO E PROBLEMA

### 1.1 Situação Atual

**Threading implementado corretamente:**
- Worker thread criado e movido com `moveToThread()` ✅
- Search executa no worker thread ✅  
- Batches emitidos pelo worker thread (100 items/batch) ✅
- Signals conectados corretamente (cross-thread) ✅

**Batch processing implementado:**
- Worker processa resultados e emite batches ✅
- UI recebe batches via signal `batch_ready` ✅
- `_on_batch_ready()` adiciona items incrementalmente ✅

**MAS o problema persiste:**
- Progress bar não aparece durante busca
- Aplicação congela por ~12.5 segundos
- Usuário reportou: "a progress bar funciona, mas o congelamento faz ela não aparecer"

### 1.2 Root Cause Identificado (após estudo do código)

**Arquivo:** `src/gui/file_explorer_dock.py`  
**Método:** `_on_batch_ready()` (linhas 1653-1728)  
**Problema:** Linhas 1702-1703:

```python
# Add batch items to tree (this is the UI operation, but only 100 items)
for file_path, matches_list in batch:
    self.results_tree.add_file_result(file_path, matches_list)
```

**O que acontece:**
1. Worker emite batch com 100 items
2. `_on_batch_ready()` executa no UI thread (correto para Qt signals)
3. Loop processa 100 items SEM retornar ao event loop
4. Cada `add_file_result()` cria QTreeWidgetItems (linhas 371-387 de results_tree.py)
5. **Criar 100 QTreeWidgetItems de uma vez BLOQUEIA o UI thread**
6. Event loop só processa ENTRE chamadas de `_on_batch_ready()`, não DURANTE
7. Se temos 1000 files = 10 batches de 100 = 10 blocos de congelamento

**Por que o event loop não processa durante o loop:**
- Qt event loop processa eventos quando o controle retorna ao loop
- `_on_batch_ready()` é um slot que bloqueia até terminar de executar
- Loop for dentro do slot não devolve controle ao event loop
- Resultado: progress bar não renderiza, UI congela

### 1.3 Evidências

**Debug output esperado:**
```
🔧 DEBUG: _on_batch_ready() batch 1/10 (100 items)
🔧 DEBUG: Batch 1 processed, returning to event loop
[AQUI o event loop deveria processar e atualizar progress bar]
🔧 DEBUG: _on_batch_ready() batch 2/10 (100 items)
...
```

**Mas o que realmente acontece:**
- Event loop processa DEPOIS de cada `_on_batch_ready()` completo
- Mas o método leva tempo demais processando 100 items
- User percebe como "congelamento"

---

## 2. ANÁLISE DE SOLUÇÕES

### Opção A: Adicionar `processEvents()` no loop (QUICK FIX) ⚡

**O que fazer:**
- Adicionar `QApplication.processEvents()` dentro do loop de batch
- Permite event loop processar a cada N items (ex: a cada 10)

**Implementação:**
```python
# Add batch items to tree
for idx, (file_path, matches_list) in enumerate(batch):
    self.results_tree.add_file_result(file_path, matches_list)
    
    # Process events every 10 items to keep UI responsive
    if (idx + 1) % 10 == 0:
        QApplication.processEvents()
```

**Prós:**
- ✅ Implementação simples (adicionar 2 linhas)
- ✅ Não muda arquitetura existente
- ✅ Mantém batch size de 100 (bom para performance)
- ✅ Qt recomenda este padrão para loops longos na UI

**Contras:**
- ⚠️ `processEvents()` pode causar reentrada (eventos processados durante loop)
- ⚠️ Risco de cancelamento durante processamento de batch
- ⚠️ Não é a solução "mais elegante" (mas funciona!)

**Complexidade:** 🟢 BAIXA (30 min)  
**Risco:** 🟡 MÉDIO (reentrada)  
**Recomendação:** ✅ **IDEAL para solo dev, pragmático, 80% done**

---

### Opção B: Reduzir batch size (SIMPLER FIX) 🔧

**O que fazer:**
- Reduzir batch_size de 100 para 20-30 items
- Mais batches, mas cada um processa mais rápido
- Event loop processa entre batches automaticamente

**Implementação:**
```python
# In file_explorer_worker.py, line 194:
self._emit_in_batches(matches_dict, batch_size=20)  # Was 100
```

**Prós:**
- ✅ Implementação trivial (mudar 1 número)
- ✅ Sem risco de reentrada
- ✅ Sem mudanças na lógica de processamento
- ✅ Cada batch termina rápido, event loop processa naturalmente

**Contras:**
- ⚠️ Mais batches = mais overhead de signals (mas mínimo)
- ⚠️ Pode precisar tuning (20? 30? 50?)
- ⚠️ Não resolve 100% se items individuais são muito pesados

**Complexidade:** 🟢 MUITO BAIXA (5 min)  
**Risco:** 🟢 BAIXO  
**Recomendação:** ✅ **IDEAL como primeiro teste**

---

### Opção C: QTimer deferido (PROPER FIX) 🏗️

**O que fazer:**
- Usar QTimer para processar items um por vez
- Cada item processado em um "tick" do event loop
- 100% não-bloqueante

**Implementação:**
```python
def _on_batch_ready(self, batch: list, batch_num: int, total_batches: int):
    # Store batch in queue
    self._pending_items.extend(batch)
    
    # Start timer if not running
    if not self._batch_timer.isActive():
        self._batch_timer.start(0)  # Process ASAP

def _process_next_batch_item(self):
    if not self._pending_items:
        self._batch_timer.stop()
        return
    
    # Process one item
    file_path, matches_list = self._pending_items.pop(0)
    self.results_tree.add_file_result(file_path, matches_list)
    
    # Update progress
    # ...
```

**Prós:**
- ✅ Solução mais elegante e "Qt-correct"
- ✅ 100% não-bloqueante (cada item = um event loop tick)
- ✅ Progress bar atualiza suavemente

**Contras:**
- ⚠️ Implementação mais complexa (queue, timer, state management)
- ⚠️ Overhead de QTimer para cada item (pode ser lento)
- ⚠️ Cancelamento mais complexo
- ⚠️ Debugging mais difícil

**Complexidade:** 🔴 ALTA (2-3 horas)  
**Risco:** 🟡 MÉDIO (mais código = mais bugs)  
**Recomendação:** ❌ **Overkill para solo dev**

---

### Opção D: Hybrid - Batch menor + processEvents (BALANCED) ⚖️

**O que fazer:**
- Reduzir batch para 50 items (meio termo)
- Adicionar `processEvents()` a cada 10 items dentro do batch
- Dupla segurança

**Implementação:**
```python
# In worker:
self._emit_in_batches(matches_dict, batch_size=50)

# In _on_batch_ready:
for idx, (file_path, matches_list) in enumerate(batch):
    self.results_tree.add_file_result(file_path, matches_list)
    if (idx + 1) % 10 == 0:
        QApplication.processEvents()
```

**Prós:**
- ✅ Combina benefícios de A e B
- ✅ Batches menores = processamento mais rápido
- ✅ processEvents() garante responsividade dentro do batch
- ✅ Implementação simples (mudar 2 lugares)

**Contras:**
- ⚠️ Mesmos riscos de A (reentrada)
- ⚠️ Pode ser over-engineering se B já resolver

**Complexidade:** 🟢 BAIXA (30 min)  
**Risco:** 🟡 MÉDIO  
**Recomendação:** ⚠️ **Considerar se B não funcionar**

---

## 3. RECOMENDAÇÃO

### Abordagem Incremental (Protocolo Simplicidade 3 - Pragmatismo)

**FASE 1: Quick Win (5 min)**
1. Implementar **Opção B** primeiro (reduzir batch_size para 20)
2. Testar com 250 files
3. Se resolver: ✅ DONE (80% é melhor que 100% nunca)
4. Se não resolver: prosseguir para Fase 2

**FASE 2: Tuning (30 min)**
1. Se Fase 1 não resolver, implementar **Opção A** (processEvents)
2. Testar com processEvents a cada 10 items
3. Se resolver: ✅ DONE
4. Se não resolver: diagnosticar problema mais profundo

**FASE 3: Deep Fix (só se necessário)**
1. Se Fase 2 não resolver, considerar **Opção C** (QTimer)
2. Mas PERGUNTAR ao usuário primeiro (Perguntas Bloqueantes)

**Justificativa:**
- Solo dev em produção → priorizar soluções simples
- Protocolo Simplicidade: "80% done > 100% never"
- Testar hipótese mais simples primeiro (batch size)
- Escalar complexidade só se necessário

---

## 4. PERGUNTAS BLOQUEANTES

**Q1:** Prefere tentar Opção B primeiro (reduzir batch_size, 5 min) ou ir direto para Opção A (processEvents, 30 min)?

**Opções:**
- A) Testar Opção B primeiro (batch_size=20) - MAIS SIMPLES
- B) Implementar Opção A direto (processEvents) - MAIS ROBUSTO
- C) Implementar Opção D (hybrid) - MAIS SEGURO

**Q2:** Se Opção B não resolver, posso usar `processEvents()` (com risco de reentrada) ou prefere a solução QTimer (mais complexa)?

**Opções:**
- A) Usar processEvents (rápido, risco médio)
- B) Usar QTimer (lento, mais seguro)
- C) Perguntar novamente depois de testar B

**Q3:** Batch size ideal para teste - qual você acha apropriado?

**Opções:**
- A) 20 items (mais batches, menos bloqueio por batch)
- B) 30 items (meio termo)
- C) 50 items (menos batches, mais rápido)
- D) Deixar você decidir baseado em testes

---

## 5. PLANO DE EXECUÇÃO (após respostas)

### Se Q1=A (Testar Opção B primeiro):

**Step 1:** Modificar batch_size no worker
- Arquivo: `src/gui/panels/file_explorer_worker.py`
- Linha: 194
- Mudança: `batch_size=100` → `batch_size=20` (ou valor de Q3)

**Step 2:** Testar com dataset pequeno (17 files)
```bash
cd /tmp/clarify_batch_test
# Criar alguns arquivos
```

**Step 3:** Testar com dataset grande (250 files)
```bash
cd /tmp/clarify_batch_test
# Usar arquivos existentes
```

**Step 4:** Observar:
- Progress bar aparece?
- UI congela?
- Tempo total de processamento
- Console debug output

**Step 5:** Se resolver → remover debug prints e commit
**Step 5 alternativo:** Se não resolver → implementar Opção A (processEvents)

---

### Se Q1=B (Implementar Opção A direto):

**Step 1:** Modificar `_on_batch_ready()` no file_explorer_dock
- Arquivo: `src/gui/file_explorer_dock.py`
- Linhas: 1702-1703
- Adicionar processEvents a cada 10 items

**Step 2:** Import QApplication no topo do arquivo
```python
from PySide6.QtWidgets import QApplication
```

**Step 3:** Testar com datasets pequeno/grande

**Step 4:** Observar mesmos critérios

---

### Se Q1=C (Hybrid):

**Step 1:** Implementar ambas mudanças (batch_size + processEvents)

**Step 2:** Testar

---

## 6. CRITÉRIOS DE SUCESSO

✅ **Sucesso completo:**
- Progress bar aparece imediatamente (< 100ms)
- Progress bar atualiza durante processamento
- UI não congela (cursor não vira "loading")
- User pode mover janela durante busca
- Tempo total ≤ 15s para 250 files (overhead aceitável)

⚠️ **Sucesso parcial:**
- Progress bar aparece mas "pula" (não atualiza suave)
- UI congela menos mas ainda congela um pouco
- → Considerar próxima fase

❌ **Falha:**
- Progress bar não aparece
- UI ainda congela completamente
- → Diagnosticar problema mais profundo (não é só batch processing)

---

## 7. ROLLBACK PLAN

Se algo der errado:

**Rollback para versão anterior:**
```bash
git checkout file_explorer_worker.py file_explorer_dock.py
```

**Ou reverter mudanças específicas:**
- Opção B: mudar `batch_size=20` de volta para `100`
- Opção A: remover bloco `processEvents()`

---

## 8. RISCOS E MITIGAÇÕES

### Risco 1: processEvents() causa reentrada
**Sintoma:** Cancelamento durante batch processing causa crash  
**Mitigação:** Adicionar flag `_processing_batch` para prevenir reentrada  
**Detecção:** Testar cancelamento durante busca

### Risco 2: Batch size muito pequeno degrada performance
**Sintoma:** Busca leva mais de 20s (vs 12.5s antes)  
**Mitigação:** Tuning do batch_size (testar 20, 30, 50)  
**Detecção:** Medir tempo total com `time.time()`

### Risco 3: Ainda bloqueia mesmo com mudanças
**Sintoma:** Progress bar não aparece mesmo com batch_size=20  
**Mitigação:** Diagnosticar problema mais profundo (pode ser QTreeWidget lento)  
**Detecção:** Adicionar profiling no `add_file_result()`

---

## 9. DOCUMENTAÇÃO

Após implementação, documentar:

**No código:**
```python
# v2.9.124: Reduced batch size from 100 to 20 to prevent UI blocking
# Each batch processes quickly enough to allow event loop to render progress bar
self._emit_in_batches(matches_dict, batch_size=20)
```

**No EXECUTION_PLAN:**
- Versão implementada (Opção A, B, C, ou D)
- Batch size escolhido
- Resultados dos testes
- Tempo de processamento antes/depois

---

## 10. CHECKLIST

- [ ] Usuário respondeu Q1, Q2, Q3
- [ ] EXECUTION_PLAN criado baseado nas respostas
- [ ] Mudanças implementadas
- [ ] Testado com 17 files
- [ ] Testado com 250 files
- [ ] Progress bar aparece e atualiza
- [ ] UI não congela
- [ ] Tempo total aceitável (≤ 15s)
- [ ] Debug prints removidos
- [ ] Código documentado
- [ ] Commit realizado

---

**PRÓXIMO PASSO:** Aguardar respostas para Q1, Q2, Q3, então criar EXECUTION_PLAN.

