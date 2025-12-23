# Protocolo Simplicidade 3 - Checklist Executável

**Versão**: 3.0  
**Projeto**: Clarify  
**Autor**: Josué Amaral  
**Data**: 04 de Dezembro de 2025

---

## 🎯 Objetivo

Este checklist garante conformidade com **todas as 16 etapas obrigatórias** do Protocolo Simplicidade 3 v3.0 (solo developer em produção).

**CRÍTICO**: Etapas marcadas como OBRIGATÓRIAS **NÃO SÃO OPCIONAIS**. Violar qualquer uma pode causar:
- ❌ Loop infinito em testes (Etapa 9.1)
- ❌ Commits com arquivos de cache (Etapa 11)
- ❌ Vulnerabilidades em produção (Etapa 6.5)
- ❌ Deploys sem rollback (Etapa 12.5)

---

## ✅ Checklist de Desenvolvimento

### Etapa 1: Leitura de Contexto (5-10 min)

- [ ] Ler task description completa (issue, comentários, specs)
- [ ] Ler documentação relacionada (README, API docs, specs técnicas)
- [ ] Verificar histórico de mudanças recentes (CHANGELOG, git log)
- [ ] Identificar arquivos-chave a modificar (src/, tests/, docs/)

**Quando pular**: Nunca. Sempre leia o contexto antes de codificar.

---

### Etapa 2: Planejamento Antes de Codificar (5-15 min)

- [ ] Listar arquivos a criar/modificar
- [ ] Identificar dependências entre mudanças
- [ ] Estimar complexidade (Simple, Medium, Complex, Very Complex)
- [ ] Quebrar task em sub-tasks se >1 hora
- [ ] Definir ordem de implementação

**Quando pular**: Tasks triviais (<10 linhas, sem lógica nova).

**OPCIONAL**: Etapa 2.5 - Matriz de Decisão (quando tiver 10+ tasks para priorizar).

---

### Etapa 3: Perguntas Críticas (2-5 min)

- [ ] Qual problema exatamente estou resolvendo?
- [ ] Quais são os edge cases?
- [ ] Quais arquivos/funções são afetados?
- [ ] Há breaking changes?
- [ ] Preciso atualizar testes?
- [ ] Preciso atualizar documentação?

**Quando pular**: Nunca. Sempre faça perguntas antes de implementar.

---

### Etapa 4: Design Técnico Leve (5-10 min)

- [ ] Definir assinatura de funções/classes principais
- [ ] Listar inputs/outputs esperados
- [ ] Identificar bibliotecas/APIs necessárias
- [ ] Definir estrutura de dados (dicts, classes, enums)
- [ ] Anotar decisões técnicas principais

**Quando pular**: Mudanças triviais (fix typo, ajuste CSS).

---

### Etapa 5: Implementação (60-80% do tempo)

- [ ] Seguir convenções de código do projeto
- [ ] Adicionar docstrings/comentários em lógica complexa
- [ ] Usar type hints em Python (quando aplicável)
- [ ] Validar inputs (evitar erros de runtime)
- [ ] Tratar erros explicitamente (try/except)

**Quando pular**: Nunca. Esta é a etapa principal.

---

### Etapa 6: Code Quality (5-10 min)

#### 6.1 Linting
- [ ] Rodar linter (pylint, flake8, mypy)
- [ ] Corrigir warnings críticos (score >8.5/10)
- [ ] Ignorar falsos positivos (adicionar # pylint: disable se necessário)

#### 6.2 Formatação
- [ ] Rodar formatter (black, autopep8)
- [ ] Verificar linha max (79-120 chars)
- [ ] Remover trailing whitespace

#### 6.3 Imports
- [ ] Organizar imports (stdlib, third-party, local)
- [ ] Remover imports não usados

#### ⭐ 6.5 Security Checklist OWASP (OBRIGATÓRIO - Solo em Produção)
- [ ] Input validation (SQL injection, XSS)
- [ ] Path traversal (CWE-22) - validar caminhos de arquivo
- [ ] Secrets não hardcoded (usar env vars)
- [ ] Dependências sem CVEs conhecidos (pip-audit, safety)

**Quando pular**: Nunca pule 6.5 em produção.

---

### Etapa 7: Dry-Run Manual (2-5 min)

- [ ] Executar código manualmente (não testes ainda)
- [ ] Verificar happy path funciona
- [ ] Testar 2-3 edge cases manualmente
- [ ] Validar output/comportamento esperado

**Quando pular**: Mudanças em testes apenas.

---

### Etapa 8: Testes Unitários (10-20% do tempo)

- [ ] Criar/atualizar testes para código novo
- [ ] Testar happy path
- [ ] Testar edge cases (valores extremos)
- [ ] Testar error handling
- [ ] Usar mocks/fixtures quando necessário

**Quando pular**: Protótipos descartáveis. Nunca pule em produção.

---

### Etapa 9: Execução de Testes (5-10 min)

#### ⭐ 9.1 Segurança em Testes (OBRIGATÓRIO)

**GUI Tests (pytest-qt)**:
- [ ] ✅ **Timeout obrigatório**: `pytest --timeout=30` (máximo 30s por teste)
- [ ] ✅ **Ambiente headless**: `QT_QPA_PLATFORM=offscreen pytest`
- [ ] ✅ **Mocks obrigatórios**: QMessageBox, QFileDialog em fixtures
- [ ] ✅ **Dry-run antes**: `pytest --collect-only` (verificar sintaxe)

**Unit Tests**:
- [ ] Rodar suite de testes completa: `pytest tests/`
- [ ] Verificar cobertura: `pytest --cov=src --cov-report=term`
- [ ] Target: >80% coverage em código crítico

**CRÍTICO**: Se violar 9.1, testes podem:
- ❌ Rodar 10+ horas (loop infinito)
- ❌ Bloquear CI/CD
- ❌ Travar terminal indefinidamente

**Exemplo v2.9.40.4**:
```bash
# ❌ ERRADO (causou loop infinito):
pytest tests/gui/test_editor_dock.py

# ✅ CORRETO (11.61s):
QT_QPA_PLATFORM=offscreen pytest tests/gui/ --timeout=30 -v
```

**Quando pular**: Nunca pule 9.1 em GUI tests.

---

### Etapa 10: Validação de Qualidade (5-10 min)

#### 10.1 Smoke Test
- [ ] Rodar aplicação localmente
- [ ] Testar feature principal implementada
- [ ] Verificar não quebrou features existentes

#### 10.2 Performance Check
- [ ] Validar operações <1s (interativas)
- [ ] Validar operações <5s (background)
- [ ] Usar `time` ou profiler se necessário

#### ⭐ 10.6 CI/CD Quality Gates (OBRIGATÓRIO - Solo em Produção)
- [ ] Testes automatizados passam (100%)
- [ ] Linting passa (score >8.5/10)
- [ ] Security scan passa (0 CVEs críticos)
- [ ] Build succeeds (sem erros)

**OPCIONAL**: Etapa 10.5 - Profiling (quando feature >1s).

**Quando pular**: Nunca pule 10.6 em produção.

---

### ⭐ Etapa 11: Organizar Pasta Raiz (OBRIGATÓRIO - 2 min)

**CRÍTICO**: Esta etapa **sempre foi esquecida** até v2.9.40.4.

**Comandos Obrigatórios** (ANTES de commit):
```bash
# 1. Remover __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Remover .pytest_cache
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# 3. Remover *.pyc, *.pyo
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# 4. Remover backups acidentais
rm -f *.backup_* *.bak *~ 2>/dev/null

# 5. Verificar limpeza
git status
```

**Checklist**:
- [ ] ✅ Remover `__pycache__/` recursivamente
- [ ] ✅ Remover `.pytest_cache/`
- [ ] ✅ Remover `*.pyc`, `*.pyo`
- [ ] ✅ Remover arquivos backup (`*.bak`, `*~`, `*.backup_*`)
- [ ] ✅ Verificar `git status` antes de commit

**PREVENÇÃO**: Adicionar ao `.gitignore`:
```gitignore
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.bak
*~
*.backup_*
```

**Consequência de pular**: Commits poluídos com 70+ arquivos binários (como aconteceu antes de v2.9.40.4).

**Quando pular**: Nunca. Sempre execute antes de `git commit`.

**OPCIONAL**: Etapa 11.5 - Notas de Decisão (ADR simplificado para decisões complexas).

---

### Etapa 12: Documentação (10-15 min)

#### 12.1 CHANGELOG.md
- [ ] Adicionar entrada com versão (v2.9.X.Y)
- [ ] Descrever problema/feature
- [ ] Listar arquivos modificados
- [ ] Documentar breaking changes (se houver)

#### 12.2 TASKS.md
- [ ] Marcar task como completa `[X]`
- [ ] Adicionar referência à versão
- [ ] Atualizar estatísticas se necessário

#### 12.3 Docstrings/Comentários
- [ ] Adicionar docstrings em funções públicas
- [ ] Comentar lógica complexa
- [ ] Atualizar comentários desatualizados

#### ⭐ 12.5 Rollback Plans (OBRIGATÓRIO - Solo em Produção)
- [ ] Documentar como reverter mudança se falhar
- [ ] Testar rollback em ambiente local
- [ ] Incluir comandos de rollback no CHANGELOG

**Exemplo**:
```markdown
## Rollback (se necessário)
git revert cea7797  # Reverte commit v2.9.40.4
git tag -d v2.9.40.4  # Remove tag local
git push origin :refs/tags/v2.9.40.4  # Remove tag remota
```

**Quando pular**: Nunca pule 12.5 em produção.

---

### Etapa 13: Commit + Tag + Push + Beeps (5 min)

#### 13.1 Git Commit
- [ ] Seguir Conventional Commits: `fix:`, `feat:`, `docs:`
- [ ] Mensagem descritiva (problema + solução)
- [ ] Listar arquivos modificados no corpo

#### 13.2 Git Tag
- [ ] Criar tag anotada: `git tag v2.9.X.Y -a -m "message"`
- [ ] Incluir changelog resumido na tag

#### 13.3 Git Push
- [ ] Push commit: `git push origin main`
- [ ] Push tag: `git push origin v2.9.X.Y`

#### 13.4 Beeps (OBRIGATÓRIO - Confirmação Acústica)
- [ ] Tocar beeps: `paplay beeps/three-beeps.mp3`
- [ ] Se headless: marcar como executado no commit message

**Quando pular**: Nunca. Beeps confirmam deploy bem-sucedido.

---

## 📊 Etapas Opcionais (Pragmáticas)

### Etapa 2.5: Matriz de Decisão (quando 10+ tasks)

**Quando usar**: Roadmap com muitas tasks competindo por prioridade.

**Template**:
| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Task A | High | Low | **P0** |
| Task B | Medium | High | P2 |

---

### Etapa 10.5: Profiling (quando feature >1s)

**Quando usar**: Feature lenta detectada em Etapa 10.2.

**Ferramentas**:
- Python: `cProfile`, `line_profiler`
- GUI: Qt profiler, QElapsedTimer

**Comandos**:
```bash
python -m cProfile -s cumtime src/app.py
```

---

### Etapa 11.5: Notas de Decisão (ADR simplificado)

**Quando usar**: Decisões arquiteturais complexas (ex: escolha de biblioteca, algoritmo).

**Template Simples**:
```markdown
# Decisão: [Título]
Data: YYYY-MM-DD
Status: Aceita/Rejeitada

## Contexto
[Por quê precisamos decidir?]

## Opções Consideradas
1. Opção A (prós/contras)
2. Opção B (prós/contras)

## Decisão
Escolhemos Opção A porque...

## Consequências
- Impacto 1
- Impacto 2
```

---

## 🚨 Violações Históricas (Lições Aprendidas)

### v2.9.40.4: Loop Infinito por Violação de Etapa 9.1

**Sintoma**: Testes GUI rodaram 10+ horas sem finalizar.

**Causa Raiz**:
- ❌ Não aplicado timeout (`--timeout=30`)
- ❌ Não configurado headless (`QT_QPA_PLATFORM=offscreen`)
- ❌ Não mockado `QMessageBox` em fixture

**Consequência**: Loop infinito, 10+ horas perdidas.

**Solução**: Aplicar **TODAS** as regras de Etapa 9.1.

**Performance**: 3000x improvement (10+ horas → 11.61s).

---

### v2.9.40.4: Commits Poluídos por Violação de Etapa 11

**Sintoma**: 70 arquivos `__pycache__/*.pyc` commitados acidentalmente.

**Causa Raiz**:
- ❌ Etapa 11 nunca executada antes desta versão
- ❌ `.gitignore` não ignorava `__pycache__/`

**Consequência**: Commits poluídos, histórico sujo.

**Solução**: 
1. Executar comandos de limpeza (Etapa 11)
2. Adicionar `.gitignore` preventivo

---

## 📝 Notas de Uso

### Para Novas Features

1. Seguir etapas 1-13 na ordem
2. Não pular etapas obrigatórias (⭐)
3. Usar etapas opcionais quando fizer sentido

### Para Hotfixes

1. Pular Etapa 2 (planejamento) se óbvio
2. Manter Etapa 6.5 (security) sempre
3. Manter Etapa 11 (organizar) sempre
4. Executar rapidamente (<30 min total)

### Para Refactoring

1. Manter Etapa 8 (testes) obrigatória
2. Adicionar Etapa 10.5 (profiling) se performance crítica
3. Documentar decisões em Etapa 11.5 (notas ADR)

---

## ✅ Checklist Rápido (Antes de Commit)

**Mínimo Absoluto**:
- [ ] ✅ Etapa 6.5: Security check (OWASP)
- [ ] ✅ Etapa 9.1: Testes com timeout + headless + mocks
- [ ] ✅ Etapa 11: Organizar pasta raiz (`__pycache__`, `.pytest_cache`)
- [ ] ✅ Etapa 12.5: Rollback plan documentado
- [ ] ✅ Etapa 13: Commit + Tag + Push + Beeps

**Se pular qualquer um**: Alto risco de bug em produção.

---

## 🎯 Meta de Conformidade

**Target**: 100% conformidade em commits para produção.

**Tracking**: Revisar este checklist a cada 10 commits.

**Review**: Atualizar checklist quando protocolo evoluir.

---

**Última Revisão**: 04 de Dezembro de 2025  
**Próxima Revisão**: Após 10 commits ou 1 mês  
**Status**: ✅ v2.9.40.4 foi o primeiro release 100% conforme (incluindo Etapa 11)
