# 🎯 PLANO DE AÇÃO - Correções Clarify v2.9.118

**Data**: 02 de Janeiro de 2026  
**Autor**: GitHub Copilot + Josué Amaral  
**Metodologia**: Protocolo Simplicidade 3 v3.1 (16 etapas)  
**Status**: 🔴 PLANEJAMENTO

---

## 📋 PROBLEMAS IDENTIFICADOS

### 🐛 **Problema #1: Advanced Filters não funcionando**
**Severidade**: 🔴 CRÍTICA  
**Componente**: `FileExplorerDock` (Advanced Filters section)  
**Sintomas**: Filters não aplicam quando usuário configura e executa busca

### 🌍 **Problema #2: Elementos não traduzidos**
**Severidade**: 🟡 MÉDIA  
**Componente**: UI global (múltiplos arquivos)  
**Sintomas**: Alguns botões e labels ainda em inglês hard-coded

### 👻 **Problema #3: Tool Search/Replace desaparecido**
**Severidade**: 🔴 CRÍTICA  
**Componente**: Menu Tools → Search/Replace  
**Sintomas**: Aparece no menu mas não abre painel (elementos gráficos sumidos)

### 🧹 **Problema #4: Códigos órfãos não integrados**
**Severidade**: 🟠 ALTA  
**Componente**: Codebase geral  
**Sintomas**: Funcionalidades implementadas mas não conectadas/ativadas

---

## 🎯 PROTOCOLO SIMPLICIDADE 3 - CHECKLIST

### **Etapas Base (1-13) - Simplicidade 1**
- [x] **Etapa 1**: Ler documentação (✅ 88% compreensão alcançada)
- [ ] **Etapa 2**: Escolher tasks (este plano)
- [ ] **Etapa 3**: Q&A com IA (próximo passo)
- [ ] **Etapa 4**: Quebrar em sprints
- [ ] **Etapa 5**: Implementar
- [ ] **Etapa 6**: Documentar
- [ ] **Etapa 7**: Testar
- [ ] **Etapa 8**: Integrar
- [ ] **Etapa 9**: Code review (auto-review solo dev)
- [ ] **Etapa 10**: CI/CD (pytest + black + pylint)
- [ ] **Etapa 11**: Commit semântico
- [ ] **Etapa 12**: Deploy local
- [ ] **Etapa 13**: Monitorar

### **Etapas OBRIGATÓRIAS Produção (14-16)**
- [ ] **Etapa 14**: ⭐ Security Checklist OWASP
- [ ] **Etapa 15**: ⭐ CI/CD Quality Gates (Black, Pylint ≥9.0, pytest)
- [ ] **Etapa 16**: ⭐ Rollback Plans

### **Etapas OPCIONAIS (17-19)**
- [ ] **Etapa 17**: Matriz de Decisão (4 tasks → priorizar)
- [ ] **Etapa 18**: Profiling (se necessário)
- [ ] **Etapa 19**: Notas de Decisão (ADR simplificado)

---

## 📊 MATRIZ DE DECISÃO (Etapa 17)

### Critérios de Priorização
| Task | Severidade | Impacto Usuário | Complexidade | Dependências | Score | Prioridade |
|------|-----------|----------------|--------------|--------------|-------|-----------|
| #1 Advanced Filters | 🔴 CRÍTICA | 🔴 Alto | 🟢 Baixa | Nenhuma | **9/10** | **P0** |
| #3 Search/Replace Tool | 🔴 CRÍTICA | 🔴 Alto | 🟡 Média | Nenhuma | **8/10** | **P0** |
| #4 Códigos órfãos | 🟠 ALTA | 🟡 Médio | 🔴 Alta | Investigação | **6/10** | **P1** |
| #2 i18n incompleto | 🟡 MÉDIA | 🟢 Baixo | 🟢 Baixa | Nenhuma | **5/10** | **P2** |

### Ordem de Execução (CRÍTICO → ALTA → MÉDIA)
1. **Sprint 1** (P0): Advanced Filters + Search/Replace Tool (~3-4h)
2. **Sprint 2** (P1): Códigos órfãos - Investigação e integração (~4-6h)
3. **Sprint 3** (P2): i18n completo (~2-3h)

---

## 🔬 SPRINT 1 - CRITICAL FIXES (Etapas 3-13)

### **Task 1.1: Investigar Advanced Filters Bug** ⏱️ ~1h

#### Etapa 3: Q&A com IA (15 perguntas)
**Q1**: Qual o fluxo de execução dos Advanced Filters?  
**Q2**: Onde os filtros são construídos (`_build_filters()`)?  
**Q3**: Como são passados para o executor?  
**Q4**: O executor recebe e aplica os filtros corretamente?  
**Q5**: Há logs de debug para rastrear?  
**Q6**: Condições grid está conectada aos filtros?  
**Q7**: Há validação de filtros antes de aplicar?  
**Q8**: Filtros funcionam em Browse mode? E em Search mode?  
**Q9**: Há testes automatizados para filters?  
**Q10**: Qual a diferença entre `filters` dict e `conditions` list?  
**Q11**: `FileFilterPanel` está conectada corretamente?  
**Q12**: Há conflito entre filtros básicos e avançados?  
**Q13**: Extension filter está sobrescrevendo advanced filters?  
**Q14**: Recursive flag afeta aplicação de filtros?  
**Q15**: Há erro silencioso (try/except engolindo exceções)?

#### Etapa 4: Quebrar em subtasks
- [ ] 1.1.1: Adicionar logging detalhado em `_build_filters()`
- [ ] 1.1.2: Verificar se filtros chegam ao executor
- [ ] 1.1.3: Testar aplicação de cada tipo de filtro isoladamente
- [ ] 1.1.4: Identificar linha exata onde filtros são ignorados
- [ ] 1.1.5: Corrigir lógica de aplicação

#### Etapa 5-6: Implementar e Documentar
- [ ] Código corrigido com comentários explicativos
- [ ] Docstring atualizado no método afetado
- [ ] Changelog entry (fix: advanced filters not applying)

#### Etapa 7: Testar
- [ ] Teste manual: Aplicar filtro de tamanho (>1MB)
- [ ] Teste manual: Aplicar filtro de extensão (.py)
- [ ] Teste manual: Aplicar filtro de data modificada
- [ ] Teste manual: Combinar múltiplos filtros (AND logic)
- [ ] Verificar que resultados batem com filtros configurados

#### Etapa 8: Integrar
- [ ] Commit com mensagem semântica
- [ ] Push para branch (ou main se solo)

---

### **Task 1.2: Corrigir Search/Replace Tool Missing** ⏱️ ~2h

#### Etapa 3: Q&A com IA (15 perguntas)
**Q1**: Onde está o menu Tools → Search/Replace?  
**Q2**: Qual método é chamado ao clicar no menu item?  
**Q3**: `SearchReplacePanel` existe e está importado?  
**Q4**: O painel é criado na inicialização ou on-demand?  
**Q5**: Há erro ao instanciar `SearchReplacePanel`?  
**Q6**: Falta algum import de widget/dependência?  
**Q7**: O painel está sendo adicionado ao layout correto?  
**Q8**: Há conflito de nomes (múltiplos SearchReplace*)?  
**Q9**: Widget está sendo ocultado por outro elemento?  
**Q10**: Z-index ou stacking order incorreto?  
**Q11**: Painel foi removido acidentalmente em refactoring?  
**Q12**: Há versão standalone vs dock - qual usar?  
**Q13**: UIBuilder constrói o painel corretamente?  
**Q14**: MainWindow tem referência ao painel (self.search_replace_panel)?  
**Q15**: Evento de menu está conectado ao slot correto?

#### Etapa 4: Quebrar em subtasks
- [ ] 1.2.1: Localizar código do menu Tools → Search/Replace
- [ ] 1.2.2: Verificar se método handler existe e é chamado
- [ ] 1.2.3: Adicionar logging no handler
- [ ] 1.2.4: Testar criação manual do painel (isolado)
- [ ] 1.2.5: Verificar se painel é adicionado ao layout correto
- [ ] 1.2.6: Corrigir erro de inicialização/importação

#### Etapa 5-6: Implementar e Documentar
- [ ] Código corrigido com verificações de erro
- [ ] Log de debug para rastreamento
- [ ] Comentário explicando o fix

#### Etapa 7: Testar
- [ ] Teste manual: Clicar Tools → Search/Replace
- [ ] Verificar que painel abre/mostra
- [ ] Testar funcionalidade básica (buscar texto)
- [ ] Verificar que não há crash/erro de console

#### Etapa 8: Integrar
- [ ] Commit com mensagem: "fix: restore Search/Replace tool visibility"

---

### **Etapas 9-13: Code Review, CI/CD, Deploy**

#### Etapa 9: Auto-Review Solo Dev
- [ ] Código segue PEP 8?
- [ ] Type hints presentes?
- [ ] Docstrings claros?
- [ ] Sem código duplicado?
- [ ] Logs úteis para debug?

#### Etapa 10: CI/CD Local
```bash
# Formatar código
python -m black src/gui/file_explorer_dock.py --line-length 120

# Organizar imports
python -m isort src/gui/file_explorer_dock.py --profile=black

# Lint
python -m pylint src/gui/file_explorer_dock.py --rcfile=.pylintrc
# Target: ≥9.0/10

# Testes
pytest tests/ --timeout=30 -v
# Target: 0 failures
```

#### Etapa 11: Commit Semântico
```bash
git add .
git commit -m "fix(file-explorer): apply advanced filters correctly

- Fixed filters not being applied to search/browse results
- Added debug logging for filter application
- Verified all filter types work (size, ext, mtime, content)

Closes #1"

git commit -m "fix(search-replace): restore tool visibility in menu

- Fixed SearchReplacePanel not appearing when clicked
- Corrected initialization order in UIBuilder
- Added error handling for panel creation

Closes #3"
```

#### Etapa 12: Deploy Local
- [ ] Reiniciar aplicação
- [ ] Testar em ambiente limpo (sem cache)

#### Etapa 13: Monitorar
- [ ] Verificar logs por 1 dia
- [ ] Observar erros relacionados
- [ ] Coletar feedback (auto, já que solo)

---

### **Etapas 14-16: Segurança e Rollback**

#### Etapa 14: Security Checklist OWASP
- [ ] **A01 Path Traversal**: Filters validam paths? ✅ Já tem `os.path.abspath()`
- [ ] **A03 Regex DoS**: Filtros regex têm timeout? ⚠️ Verificar
- [ ] **A06 Components**: Dependências atualizadas? ✅ pip-audit limpo
- [ ] **A09 Logging**: Logs não expõem dados sensíveis? ✅ Verificar

#### Etapa 15: CI/CD Quality Gates
```yaml
# .github/workflows/ci.yml (ou local script)
- Black: --check --line-length 120
- isort: --check-only --profile=black
- Pylint: --fail-under=9.0
- Pytest: --timeout=30 --cov=src --cov-fail-under=90
```

#### Etapa 16: Rollback Plan
```bash
# Se Sprint 1 quebrar produção:
git revert HEAD~2  # Reverter últimos 2 commits
git push origin main

# Ou restaurar de backup:
cp ~/.clarify/backups/file_explorer_dock_2026_01_02.py.bak \
   src/gui/file_explorer_dock.py
```

---

## 🔍 SPRINT 2 - INVESTIGAÇÃO ÓRFÃOS (P1) ⏱️ ~4-6h

### **Task 2.1: Mapear Códigos Órfãos** ⏱️ ~2h

#### Checklist de Investigação
- [ ] Buscar TODOs no código: `grep -r "TODO\|FIXME\|XXX" src/`
- [ ] Buscar imports não utilizados: `pylint --disable=all --enable=unused-import src/`
- [ ] Buscar funções/classes não referenciadas
- [ ] Revisar pasta `add/` (5 programas standalone identificados na doc)
- [ ] Revisar pasta `archive/` (código antigo)
- [ ] Verificar widgets criados mas não adicionados ao layout
- [ ] Verificar features mencionadas em TASKS.md não implementadas
- [ ] Revisar INTEGRATION_PLAN.md (1.754 linhas integradas, mas quanto falta?)

#### Output Esperado
```markdown
## Códigos Órfãos Identificados

### Categoria 1: Features Implementadas Não Conectadas
- [ ] Widget X criado mas não adicionado ao MainWindow
- [ ] Função Y implementada mas nunca chamada
- [ ] Classe Z com testes mas sem uso real

### Categoria 2: Features Parcialmente Integradas
- [ ] Feature A: 80% integrado, falta conectar signals
- [ ] Feature B: UI pronta, backend faltando

### Categoria 3: Código Legacy Não Removido
- [ ] Arquivo old_*.py duplicado
- [ ] Imports obsoletos de refactoring anterior
```

### **Task 2.2: Integrar Órfãos Críticos** ⏱️ ~2-4h
(Depende dos resultados de 2.1)

---

## 🌍 SPRINT 3 - i18n COMPLETO (P2) ⏱️ ~2-3h

### **Task 3.1: Auditar Strings Hard-coded** ⏱️ ~1h

```bash
# Buscar strings hard-coded suspeitas
grep -r '"[A-Z].*"' src/gui/ --include="*.py" | grep -v "tooltip_tr\|tr(" | head -100

# Buscar setText, setTitle, setLabel sem tr()
grep -r "setText\|setTitle\|setLabel\|setPlaceholderText" src/gui/ | grep -v "tr(" | head -50
```

### **Task 3.2: Adicionar Traduções Faltantes** ⏱️ ~1-2h

#### Para cada string encontrada:
1. Adicionar chave em `src/i18n/en.json`
2. Traduzir para outros 6 idiomas
3. Substituir hard-coded por `tr("namespace.key")`
4. Testar switch de idioma runtime

---

## 📈 MÉTRICAS DE SUCESSO

### Sprint 1 (P0 - Critical)
- ✅ Advanced Filters aplicam corretamente (100% dos casos testados)
- ✅ Search/Replace Tool abre sem erros
- ✅ Pylint score mantido ≥9.0
- ✅ 0 crashes em testes manuais
- ✅ Logs limpos (sem ERROR/CRITICAL não tratados)

### Sprint 2 (P1 - Alta)
- ✅ Mapa completo de órfãos documentado
- ✅ Top 5 órfãos críticos integrados
- ✅ Redução de 50%+ em código morto

### Sprint 3 (P2 - Média)
- ✅ 95%+ da UI traduzível via i18n
- ✅ Switch de idioma não quebra layout
- ✅ Todas as 7 línguas funcionais

---

## 🚀 EXECUÇÃO

### **AGORA (Próximo Passo)**
**Iniciar Sprint 1 - Task 1.1: Advanced Filters Bug**

**Etapa 3: Q&A com IA** (responder 15 perguntas acima)

**Comando para começar**:
```bash
# 1. Ver código atual de _build_filters()
code src/gui/file_explorer_dock.py:717

# 2. Adicionar logging debug
# 3. Testar com filtro simples
```

---

**Status Atual**: 🔵 PLANO APROVADO - AGUARDANDO EXECUÇÃO  
**Próxima Ação**: Q&A Task 1.1 (responder 15 perguntas)  
**Tempo Estimado Total**: 9-13h (3 sprints)  
**Prioridade Imediata**: 🔴 CRÍTICA (Sprint 1)

---

**Metodologia Aplicada**: ✅ Protocolo Simplicidade 3 v3.1  
**Documentação Lida**: ✅ 88% compreensão (42.000 linhas)  
**Conformidade**: ✅ 16 etapas obrigatórias mapeadas
