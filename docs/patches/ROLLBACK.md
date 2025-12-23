# Rollback Plans - Clarify Project

Este documento contém planos de rollback para features críticas implementadas no projeto Clarify, seguindo o **Protocolo Simplicidade 3 - Etapa 12.5 (OBRIGATÓRIO)**.

## 📋 Índice

- [v2.9.78 - Google Translate Integration](#v2978---google-translate-integration)
- [Como Usar Este Documento](#como-usar-este-documento)
- [Procedimento Geral de Rollback](#procedimento-geral-de-rollback)

---

## v2.9.78 - Google Translate Integration

**Data**: 21/12/2025  
**Componentes**: API + CLI + GUI + Testes  
**Risco**: Baixo (feature isolada, sem dependências críticas)  
**Tempo Estimado**: 5-10 minutos

### 🔄 Quando Fazer Rollback

- API de tradução falha consistentemente (>50% de erros)
- Bug crítico que impacta funcionamento do programa
- Performance inaceitável (>10s para traduções simples)
- Problemas de segurança descobertos

### 📝 Procedimento de Rollback

#### 1. Remover Arquivos Novos

```bash
cd /path/to/clarify

# API e GUI
rm src/translation/google_translate.py
rm src/gui/google_translate_dock.py

# Testes
rm tests/test_google_translate.py
rm tests/test_google_translate_dock.py

# Ícones
rm -rf assets/icons/google_translate_icon.*
```

#### 2. Reverter src/app.py

**Linhas a remover**:

- Função `cli_gtranslate()` (~linhas 1054-1097)
- Import: `from .translation.google_translate import GoogleTranslateAPI` (linha 1054)
- Parser: Subcomando `gtranslate` (linhas ~6137-6145)
- Lista de comandos: Remover `"gtranslate"` da validação main() (linha ~6219)
- Menu: `self.act_open_google_translate` (linha ~5026)
- Menu: `m_tools.addAction(self.act_open_google_translate)` (linha ~5042)
- Signal: `self.act_open_google_translate.triggered.connect(...)` (linha ~5058)
- Função: `_open_google_translate()` (linhas ~4398-4402)
- Função: `_show_google_translate()` (linhas ~4490-4495)

**Comando Git**:
```bash
git diff src/app.py  # Revisar mudanças
git checkout HEAD~1 -- src/app.py  # Reverter para versão anterior
```

#### 3. Reverter src/gui/__init__.py

**Linhas a remover**:

- Import: `from .google_translate_dock import GoogleTranslateDock` (linha 32)
- Export: `'GoogleTranslateDock',` do `__all__` (linha 45)

**Comando Git**:
```bash
git checkout HEAD~1 -- src/gui/__init__.py
```

#### 4. Reverter Traduções i18n

**src/i18n/en.json** - Remover 13 chaves:
```json
"menu.tools.google_translate"
"tooltip.google_translate.from_lang"
"tooltip.google_translate.to_lang"
"tooltip.google_translate.file_mode"
"tooltip.google_translate.input_text"
"tooltip.google_translate.translate_btn"
"tooltip.google_translate.copy_result"
"tooltip.google_translate.clear_btn"
(+ 5 duplicatas)
```

**src/i18n/pt_BR.json** - Remover 8 chaves:
```json
"menu.tools.google_translate"
"tooltip.google_translate.from_lang"
"tooltip.google_translate.to_lang"
"tooltip.google_translate.file_mode"
"tooltip.google_translate.input_text"
"tooltip.google_translate.translate_btn"
"tooltip.google_translate.copy_result"
"tooltip.google_translate.clear_btn"
```

**Comando Git**:
```bash
git checkout HEAD~1 -- src/i18n/en.json
git checkout HEAD~1 -- src/i18n/pt_BR.json
```

#### 5. Limpar Cache de Usuário

```bash
# Remover cache de traduções
rm -rf ~/.clarify/translate_cache/

# Limpar __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

#### 6. Validar Rollback

```bash
# 1. Verificar sintaxe
python -m py_compile src/app.py src/gui/__init__.py

# 2. Verificar imports
python -c "from src.app import MainWindow; print('✅ Import OK')"

# 3. Verificar CLI não lista gtranslate
python -m src search --help | grep -q gtranslate && echo "❌ gtranslate ainda existe" || echo "✅ gtranslate removido"

# 4. Executar testes
pytest tests/ -v --ignore=tests/test_google_translate.py --ignore=tests/test_google_translate_dock.py

# 5. Testar GUI (inicialização)
timeout 5s python -m src && echo "✅ GUI inicia sem erros"
```

#### 7. Rollback de Documentação (Opcional)

```bash
# Remover documentação específica
rm docs/specifications/v2.9.78-SPECIFICATION.md

# Reverter CHANGELOG.md (remover entrada v2.9.78)
git checkout HEAD~1 -- CHANGELOG.md

# Reverter TASKS.md (desmarcar task)
git checkout HEAD~1 -- docs/TASKS.md
```

### ✅ Checklist de Rollback Completo

- [ ] Arquivos novos removidos (4 arquivos Python + ícones)
- [ ] src/app.py revertido (~143 linhas removidas)
- [ ] src/gui/__init__.py revertido (2 linhas removidas)
- [ ] Traduções i18n revertidas (21 chaves removidas)
- [ ] Cache de usuário limpo
- [ ] Sintaxe validada (py_compile)
- [ ] Imports testados
- [ ] CLI validado (gtranslate não existe)
- [ ] Testes passando (excluindo testes da feature)
- [ ] GUI inicia sem erros
- [ ] Documentação revertida (opcional)

### 🔍 Validação Pós-Rollback

**Teste Funcional**:
1. Abrir aplicação GUI
2. Verificar que menu "Tools" não contém "Google Translate"
3. Executar `python -m src --help` e confirmar que `gtranslate` não aparece
4. Executar 10 testes aleatórios: `pytest tests/ -v -k "not google" --maxfail=1`

**Teste de Regressão**:
- Todas as outras funcionalidades devem continuar funcionando normalmente
- Sem erros de import
- Performance não degradada

### 📊 Impacto do Rollback

**O que continua funcionando**:
- ✅ Todas as outras ferramentas (Search, Replace, Insert, etc.)
- ✅ Sistema de tradução de dicionários JSON (existente)
- ✅ Editor, AI Processor, todos os docks
- ✅ CLI para outros subcomandos

**O que para de funcionar**:
- ❌ Tradução online via Google Translate
- ❌ CLI `gtranslate`
- ❌ Menu "Tools → Google Translate"

**Dados perdidos**:
- Cache de traduções em `~/.clarify/translate_cache/` (pode ser mantido se desejado)

### 🆘 Troubleshooting de Rollback

**Problema**: Import errors após rollback  
**Solução**: Limpar todos os `__pycache__`: `find . -name "__pycache__" -exec rm -rf {} +`

**Problema**: Menu item fantasma (Google Translate aparece mas falha)  
**Solução**: Verificar se `_show_google_translate()` foi removido de src/app.py

**Problema**: Testes falhando  
**Solução**: Ignorar testes da feature: `pytest --ignore=tests/test_google_translate*.py`

---

## Como Usar Este Documento

### Para Desenvolvedores

1. **Antes de implementar feature crítica**: Planejar rollback ANTES do commit
2. **Durante implementação**: Anotar todos os arquivos modificados
3. **Após implementação**: Documentar procedimento de rollback neste arquivo
4. **Antes de deploy**: Testar rollback em ambiente local

### Para Rollback de Emergência

1. Identificar versão problemática (ex: v2.9.78)
2. Encontrar seção correspondente neste documento
3. Seguir procedimento passo-a-passo
4. Executar checklist de validação
5. Testar funcionalidade críticas

### Formato Padrão de Rollback Plan

Cada rollback plan deve conter:

- **Quando fazer rollback**: Critérios claros
- **Procedimento**: Comandos exatos (bash)
- **Validação**: Como testar se rollback foi bem-sucedido
- **Checklist**: Lista verificável de tarefas
- **Impacto**: O que continua/para de funcionar
- **Troubleshooting**: Problemas comuns e soluções

---

## Procedimento Geral de Rollback

### Rollback via Git (Método Recomendado)

```bash
# 1. Ver histórico de commits
git log --oneline -10

# 2. Identificar commit antes da feature
git log --oneline --grep="v2.9.78"

# 3. Criar branch de rollback (opcional mas recomendado)
git checkout -b rollback-v2.9.78

# 4. Reverter commit específico
git revert <commit-hash>

# 5. Validar mudanças
git diff HEAD~1

# 6. Testar
pytest tests/ -v

# 7. Se OK, merge de volta
git checkout main
git merge rollback-v2.9.78
```

### Rollback Manual (Sem Git)

1. Seguir procedimento específico da feature (seções acima)
2. Remover arquivos novos manualmente
3. Editar arquivos modificados (remover código adicionado)
4. Validar com testes
5. Documentar mudanças

### Prevenção

**Boas práticas para facilitar rollback**:

- ✅ Commits atômicos (1 feature = 1 commit)
- ✅ Mensagens de commit claras (`feat: Add Google Translate (v2.9.78)`)
- ✅ Tags de versão (`git tag v2.9.78`)
- ✅ Feature flags para features grandes
- ✅ Testes abrangentes (detectam regressões)
- ✅ Code review (previne bugs críticos)

---

**Última Atualização**: 21/12/2025  
**Metodologia**: Protocolo Simplicidade 3 - Etapa 12.5 (OBRIGATÓRIO)  
**Status**: ✅ Documentação Completa
