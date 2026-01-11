# PLANO DE EXECUÇÃO: Validar Fix "Open in Editor"

**Executor:** Qualquer pessoa  
**Tempo Estimado:** 30 minutos  
**Dificuldade:** 🟢 Fácil (seguir instruções)  
**Protocolo:** Simplicidade 3 - Delegação

---

## ⚠️ CONTEXTO RÁPIDO

**Problema:** Erro ao clicar "Open in Editor" no File Explorer  
**Fix:** Código já implementado (commits fcee742 + bab082b)  
**Motivo do erro persistir:** Clarify NÃO foi reiniciado após commits

**Solução:** ➡️ REINICIAR CLARIFY (isso resolve 99% dos casos)

---

## 📋 CHECKLIST RÁPIDO (30 min)

Execute na ordem. Marque [x] quando completar cada item.

### FASE 1: Preparação (5 min)

```bash
cd /home/josue/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify

# 1. Verificar commits
git log --oneline -3

# Esperado ver:
# 6d267a9 docs: add AI-powered...
# bab082b fix: apply same main_window...
# fcee742 fix: resolve 'Could not find main window'...
```

- [ ] Commits fcee742 e bab082b visíveis no git log

```bash
# 2. Limpar bytecode (forçar recompilação)
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "✅ Cache limpo"
```

- [ ] Bytecode limpo

---

### FASE 2: 🔴 REINICIAR CLARIFY (2 min)

```bash
# 1. Fechar Clarify completamente
# - Usar menu File → Quit
# - OU fechar janela (X)
# - OU matar processo:

ps aux | grep clarify
# Se aparecer processo, anotar PID e:
kill <PID>
# OU forçar tudo:
killall -9 python
```

- [ ] Clarify fechado (sem processos restantes)

```bash
# 2. Verificar que fechou
ps aux | grep clarify
# Esperado: Nenhuma linha com 'clarify' (exceto o grep)
```

- [ ] Confirmado: sem processos Clarify

```bash
# 3. REABRIR Clarify
cd /home/josue/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify
python -m clarify
```

- [ ] Clarify reaberto com sucesso
- [ ] Interface carregada completamente

---

### FASE 3: Verificar Código Novo Carregado (3 min)

```bash
# EM OUTRO TERMINAL (deixar Clarify aberto), executar:

cd /home/josue/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify

python -c "
import inspect
from src.gui.widgets.file_list_table_manager import FileListTableManager
from src.gui.panels.results_tree import ResultsTree

# Verificar FileListTableManager
sig1 = inspect.signature(FileListTableManager.__init__)
params1 = list(sig1.parameters.keys())

# Verificar ResultsTree
sig2 = inspect.signature(ResultsTree.__init__)
params2 = list(sig2.parameters.keys())

print('FileListTableManager.__init__:', params1)
print('ResultsTree.__init__:', params2)
print()

if 'main_window' in params1 and 'main_window' in params2:
    print('✅ CÓDIGO NOVO CARREGADO!')
    print('   Ambos têm parameter main_window')
    exit(0)
else:
    print('❌ CÓDIGO ANTIGO AINDA ATIVO!')
    print('   REINICIE Clarify novamente!')
    exit(1)
"
```

**Resultado esperado:**
```
FileListTableManager.__init__: ['self', 'parent', 'main_window']
ResultsTree.__init__: ['self', 'parent', 'main_window']

✅ CÓDIGO NOVO CARREGADO!
   Ambos têm parameter main_window
```

- [ ] ✅ Código novo confirmado na memória
- [ ] Se ❌, voltar à FASE 2 e reiniciar novamente

---

### FASE 4: Testar Table Mode (5 min)

**No Clarify:**

1. Menu → Tools → File Explorer
   - [ ] File Explorer abriu

2. Selecionar diretório: `/home/josue/Documents` (ou qualquer outro)
   - [ ] Diretório selecionado

3. Clicar em "Browse" ou "List Files"
   - [ ] Arquivos listados na tabela

4. **Botão direito** em qualquer arquivo
   - [ ] Context menu apareceu

5. Selecionar: **"Abrir no Editor"** (ou "Open in Editor")
   - [ ] ✅ Arquivo abriu no Editor Dock
   - [ ] ✅ Conteúdo carregado corretamente
   - [ ] ✅ **SEM mensagem de erro**

**Se erro ocorreu:**
- [ ] ❌ Erro: "Could not find main window..."
- [ ] Anotar mensagem exata: _______________________
- [ ] Copiar logs: `tail -50 ~/.clarify/logs/clarify.log`

6. Testar com múltiplos arquivos:
   - Selecionar 2-3 arquivos (Ctrl+Click)
   - Botão direito → "Abrir no Editor"
   - [ ] ✅ Todos abriram em tabs separadas

---

### FASE 5: Testar Tree Mode (5 min)

**No Clarify (File Explorer):**

1. Ir para seção "Search & Replace"
   - Campo "Content Query": digitar `import` (ou qualquer termo)
   - [ ] Termo digitado

2. Clicar em "Search"
   - [ ] Resultados aparecem em Tree View (árvore)
   - [ ] Estrutura: `📊 Results: X files, Y matches`

3. **Botão direito** em nome de arquivo na árvore
   - [ ] Context menu apareceu

4. Selecionar: **"Abrir no Editor"**
   - [ ] ✅ Arquivo abriu no Editor Dock
   - [ ] ✅ **SEM mensagem de erro**

**Se erro ocorreu:**
- [ ] ❌ Erro: "results_tree.error_no_main_window" (não traduzido)
- [ ] OU: "Não foi possível encontrar a janela principal..." (traduzido)
- [ ] Anotar mensagem exata: _______________________

5. Testar em linha de match:
   - **Botão direito** em `line 42: código aqui`
   - Selecionar "Abrir no Editor"
   - [ ] ✅ Arquivo abre e cursor vai para linha do match

---

### FASE 6: Teste de Regressão (5 min)

**No File Explorer (Table Mode):**

1. Botão direito em arquivo → "Abrir no Gerenciador de Arquivos"
   - [ ] ✅ Gerenciador de arquivos abriu corretamente

2. Botão direito em arquivo → "Copiar Caminho"
   - Colar em editor (Ctrl+V)
   - [ ] ✅ Caminho completo colado

3. Clicar em "Export to CSV" (se visível)
   - [ ] ✅ CSV exportado com sucesso

---

### FASE 7: Validação Final (5 min)

```bash
# Monitorar logs enquanto testa (opcional)
tail -f ~/.clarify/logs/clarify.log | grep -E "\[DEBUG\]|main_window"

# Quando fizer "Open in Editor", deve aparecer:
# [DEBUG] Using explicit main_window reference: MainWindow
```

**Checklist Final:**

- [ ] Table Mode: "Open in Editor" funcionou sem erro
- [ ] Tree Mode: "Open in Editor" funcionou sem erro  
- [ ] Múltiplos arquivos funcionaram
- [ ] Context menu original funciona (Open in File Manager, Copy Path)
- [ ] Mensagens em português (se erro ocorreu)
- [ ] Logs confirmam: "Using explicit main_window reference"

---

## 📊 RESULTADO

Marque o resultado final:

- [ ] ✅ **SUCESSO TOTAL** - Tudo funcionou perfeitamente
- [ ] ⚠️ **SUCESSO PARCIAL** - Funcionou mas com ressalvas: _____________
- [ ] ❌ **FALHA** - Erro persiste

**Se SUCESSO:**
```
✅ Validação completa!
Fix confirmado funcionando em ambos os modos (Table + Tree).
Próximo passo: Usar normalmente.
```

**Se FALHA:**
1. Copiar últimas 100 linhas do log:
   ```bash
   tail -100 ~/.clarify/logs/clarify.log > debug_log.txt
   ```
2. Fazer screenshot do erro
3. Reportar ao desenvolvedor com:
   - [ ] Mensagem de erro exata
   - [ ] debug_log.txt anexado
   - [ ] Screenshot anexado
   - [ ] Output do comando "Verificar Código Novo Carregado" (FASE 3)

---

## 🚨 TROUBLESHOOTING RÁPIDO

**Problema:** Código novo não carrega (FASE 3 falha)

**Solução:**
```bash
# 1. Limpar TUDO
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 2. Matar TODOS processos Python
killall -9 python

# 3. Aguardar 5 segundos
sleep 5

# 4. Reabrir Clarify
python -m clarify
```

**Problema:** Git não está atualizado

**Solução:**
```bash
git fetch origin
git log origin/main --oneline -5

# Se commits fcee742 e bab082b NÃO aparecem:
git pull origin main

# Então reiniciar Clarify
```

**Problema:** Erro persiste mesmo após reiniciar

**Ação:**
1. ⚠️ Pode ser bug diferente (não relacionado a restart)
2. Executar FASE 3 e confirmar que código novo está carregado
3. Se código novo está carregado MAS erro persiste:
   - Reportar como bug novo
   - Anexar logs completos
   - Descrever cenário exato que falha

---

## 📄 DOCUMENTOS DE REFERÊNCIA

Se precisar de mais detalhes:

- `INVESTIGATION_RESTART_VALIDATION.md` - Investigação técnica completa (30 KB)
- `OPEN_IN_EDITOR_FIX.md` - Documentação do fix (10 KB)
- `TESTE_OPEN_IN_EDITOR.md` - Instruções detalhadas de teste (4.5 KB)

---

## ⏱️ TIMELINE ESPERADO

| Fase | Tempo | Acumulado |
|------|-------|-----------|
| 1. Preparação | 5 min | 5 min |
| 2. Reiniciar | 2 min | 7 min |
| 3. Verificar código | 3 min | 10 min |
| 4. Testar Table | 5 min | 15 min |
| 5. Testar Tree | 5 min | 20 min |
| 6. Regressão | 5 min | 25 min |
| 7. Validação | 5 min | **30 min** |

---

**ÚLTIMA ATUALIZAÇÃO:** 2026-01-11 16:08 UTC  
**EXECUTOR:** _____________________ (preencher nome)  
**DATA EXECUÇÃO:** ___/___/_____ (preencher quando executar)  
**RESULTADO:** [ ] ✅ SUCESSO  [ ] ❌ FALHA

---

**Pronto para executar? Comece pela FASE 1!** 🚀
