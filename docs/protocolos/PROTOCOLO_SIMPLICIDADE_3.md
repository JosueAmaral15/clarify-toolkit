# Protocolo Simplicidade 3 - Solo Developer em Produção

**Autor**: Josué Amaral  
**Data de Criação**: 02 de Dezembro de 2025  
**Versão**: 3.4  
**Última Atualização**: 01 de Janeiro de 2026  
**Objetivo**: Metodologia híbrida para **solo developer** com aplicação em **produção**

**Changelog v3.4** (01/01/2026):
- ✅ **[NOVO]** Stack Padrão Recomendado para Sites (Solo Developer)
- ✅ Mesma base moderna: Next.js 15 + React 19 + TypeScript
- ✅ Foco em baixa manutenção: ~15h/mês sustentável
- ✅ Deploy gratuito em Vercel (escalável conforme crescer)
- ✅ Documentação excepcional e comunidade massiva
- ✅ LTS Node.js 18+ (suporte até 2025)
- ✅ Plano de rollback obrigatório (3 alternativas)
- ✅ Tempo de manutenção estimado e gatilhos de rollback
- ✅ Quando NÃO usar: Desenvolvedor experiente Vue/Angular, prefere "boring tech"

**Changelog v3.3** (01/01/2026):
- ✅ **[CRÍTICO]** Adicionada Etapa 1.0: Busca e Leitura Completa de Documentação (PRIORITÁRIO)
- ✅ Foco solo: Documentação como "memória externa" do desenvolvedor
- ✅ Leitura obrigatória de OWASP checklist e rollback plans (críticos)
- ✅ Estrutura mínima solo: security/ e rollback/ obrigatórios
- ✅ Template de README com info de produção (deploy, uptime, contato)
- ✅ Template de OWASP-checklist.md (verificar ANTES de cada deploy)
- ✅ Checklist de 10 itens focado em solo developer
- ✅ Comentários no código: Documentar para "você do futuro"
- ✅ Rationale: Sem equipe, documentação é seu colega virtual

**Changelog v3.2** (01/01/2026):
- ✅ **[OBRIGATÓRIO]** Adicionada Etapa 1.5: Pesquisa de Tecnologias Adequadas ao Projeto
- ✅ Foco em **maturidade, documentação e comunidade ativa** (critérios solo)
- ✅ Priorização de versões **LTS (Long Term Support)** e tecnologias "boring"
- ✅ Avaliação de **facilidade de manutenção** (horas/semana estimadas)
- ✅ Análise de **longevidade** (5+ anos de suporte)
- ✅ **Plano de rollback obrigatório** (se stack não funcionar)
- ✅ Pesquisas específicas para solo developers (Indie Hackers, Reddit r/solopreneur)
- ✅ Template de documentação com histórico de atualizações
- ✅ Checklist expandido (13 itens) incluindo recursos de aprendizado
- ✅ Conceito "Choose Boring Technology" para projetos de longo prazo

**Changelog v3.1** (09/12/2025):

---

## 🎯 Por Quê Simplicidade 3 Existe?

### Contexto do Projeto
- 👤 **Solo Developer**: Você programa sozinho (sem equipe)
- 🚀 **Produção**: Aplicação tem usuários reais dependendo
- ⚠️ **Crítico**: Bugs afetam usuários, downtime tem impacto
- 📈 **Evolutivo**: Projeto de longo prazo, não é protótipo

### Por Quê NÃO Simplicidade 1?
❌ **Simplicidade 1** é **insuficiente para produção**:
- ❌ Sem security checklist → Vulnerabilidades podem ir para produção
- ❌ Sem CI/CD automation → Validação manual = erros humanos
- ❌ Sem rollback plan → Se quebrar em produção, você está sozinho debugando
- ❌ Sem profiling → Performance degrada sem você perceber
- ❌ Documentação básica → Você esquece decisões complexas após 3 meses

**Risco Real**: Aplicação simples hoje = dívida técnica gigante em 6 meses.

### Por Quê NÃO Simplicidade 2?
❌ **Simplicidade 2** tem **overhead de equipe** desnecessário para solo dev:
- ❌ **Code Review por Pares** (Etapa 9.5) → Você não tem pares
- ❌ **Sprint Retrospectives formais** (Etapa 13.5) → Overkill para uma pessoa
- ❌ **ADR formais** (Etapa 11.5) → Pode simplificar para notas de decisão
- ❌ **Accessibility WCAG** (Etapa 8.5) → Só se app for público/acessível
- ❌ **API Documentation Sphinx** (Etapa 6.6) → Docstrings são suficientes

**Problema Real**: Burocracia consome tempo de desenvolvimento sem ganho real para solo.

### ✅ Simplicidade 3 - Solução Híbrida

**Filosofia**: **Segurança e automação de produção** SEM overhead de equipe.

**Fórmula**:
```
Simplicidade 3 = Base Simplicidade 1 (13 etapas)
                 + 3 OBRIGATÓRIAS de produção (Security, CI/CD, Rollback)
                 + 3 OPCIONAIS pragmáticas (Matriz, Profiling, Notas ADR)
                 = 16-19 etapas totais
```

**Etapas OBRIGATÓRIAS Adicionais** (vs Simplicidade 1):
1. ⭐ **Etapa 6.5: Security Checklist OWASP** - CRÍTICO para produção
2. ⭐ **Etapa 10.6: CI/CD Quality Gates** - Automação essencial
3. ⭐ **Etapa 12.5: Rollback Plans** - Segurança em deploy

**Etapas OPCIONAIS Adaptadas** (quando fizer sentido):
4. 📊 **Etapa 2.5: Matriz de Decisão** - Quando tem 10+ tasks para priorizar
5. ⚡ **Etapa 10.5: Profiling** - Para features lentas (>1s)
6. 📝 **Etapa 11.5: Notas de Decisão** - ADR simplificado (não formal)

**Removidas do Simplicidade 2** (não fazem sentido solo):
- ❌ Etapa 9.5: Code Review por Pares
- ❌ Etapa 13.5: Sprint Retrospectives formais
- ❌ Etapa 8.5: Accessibility WCAG (a menos que app seja público)
- ❌ Etapa 6.7: API Documentation formal (docstrings suficientes)

---

## 📊 Comparação dos Protocolos

| Aspecto | Simplicidade 1 | Simplicidade 3 | Simplicidade 2 |
|---------|----------------|----------------|----------------|
| **Etapas** | 13 obrigatórias | 16 obrig + 3 opc | 13 obrig + 10 opc |
| **Cenário** | Protótipos/interno | **Solo em produção** | Equipes enterprise |
| **Security** | ❌ Não | ✅ OWASP obrigatório | ✅ OWASP obrigatório |
| **CI/CD** | ❌ Não | ✅ Obrigatório | ✅ Obrigatório |
| **Rollback** | ❌ Não | ✅ Obrigatório | ✅ Obrigatório |
| **Code Review** | ❌ Não | ❌ Solo | ✅ Pares |
| **Retrospectives** | ❌ Não | ❌ Solo | ✅ Equipe |
| **Overhead** | Baixo | **Médio** | Alto |
| **Produção** | ❌ Não recomendado | ✅ **IDEAL** | ✅ Sim |
| **Time/Task** | ~2-3h | ~3-4h | ~4-6h |

---

## 🎯 Quando Usar Simplicidade 3?

### ✅ Use Simplicidade 3 SE:
- ✅ Você programa **sozinho** (solo developer)
- ✅ Aplicação está ou vai para **produção**
- ✅ Tem **usuários reais** dependendo (não é protótipo)
- ✅ Bugs têm **impacto** (downtime, perda de dados)
- ✅ Projeto de **longo prazo** (>6 meses)
- ✅ Precisa **segurança** (dados de usuários, LGPD)
- ✅ Quer **automação** (CI/CD para não depender de memória)

### ❌ NÃO use Simplicidade 3 SE:
- ❌ Protótipo/POC descartável → Use **Simplicidade 1**
- ❌ Script de uso único → Use **Simplicidade 1**
- ❌ Equipe de 2+ pessoas → Use **Simplicidade 2** (tem code review)
- ❌ App interno não-crítico → Use **Simplicidade 1**
- ❌ Aprendendo/experimentando → Use **Simplicidade 1**

---

**Changelog v3.2** (01/01/2026):
- ✅ **[ETAPA 3]** Adicionado padrão de questionários editáveis para coleta de informações
- ✅ Formato solo: Documento simples e direto, sem burocracia
- ✅ IA deve fornecer opções "boring tech" e análise de manutenção (horas/mês)
- ✅ Após preenchimento, IA lê documento e implementa rapidamente
- ✅ Rationale: Solo dev precisa documentar decisões sem perder tempo
- ✅ Classificação: **RECOMENDADO para decisões complexas (stack, arquitetura)**

**Changelog v3.1** (09/12/2025):
- ✅ **[ETAPA 3]** Adicionada recomendação para IA fornecer sugestões e palpites nas perguntas
- ✅ Formato recomendado: "❓ Pergunta + 💡 Sugestão da IA + Opções A/B/C"
- ✅ Rationale: Acelera decisões, reduz carga cognitiva, mantém consistência com código existente
- ✅ Classificação: **OPCIONAL mas ALTAMENTE RECOMENDADO**

**Changelog v3.0** (02/12/2025):
- ✅ **[HÍBRIDO]** Criado Protocolo Simplicidade 3 para solo developer em produção
- ✅ Base: Simplicidade 1 (13 etapas) + 3 obrigatórias de produção
- ✅ **OBRIGATÓRIAS NOVAS**:
  - Etapa 6.5: Security Checklist OWASP (⭐ ALTA PRIORIDADE)
  - Etapa 10.6: CI/CD Quality Gates (⭐ ALTA PRIORIDADE)
  - Etapa 12.5: Rollback Plans (⭐ ALTA PRIORIDADE)
- ✅ **OPCIONAIS PRAGMÁTICAS**:
  - Etapa 2.5: Matriz de Decisão (quando 10+ tasks)
  - Etapa 10.5: Profiling e Otimização (features lentas)
  - Etapa 11.5: Notas de Decisão (ADR simplificado)
- ✅ **REMOVIDAS** (não fazem sentido solo):
  - ❌ Code Review por Pares (sem pares)
  - ❌ Sprint Retrospectives formais (overkill solo)
  - ❌ Accessibility WCAG (a menos que público)
  - ❌ API Documentation formal (docstrings suficientes)
- ✅ Rationale detalhado: Por quê não Simplicidade 1 ou 2
- ✅ Tabela comparativa dos 3 protocolos
- ✅ Total: 16 obrigatórias + 3 opcionais = 16-19 etapas

**Changelog v1.8** (02/12/2025):
- ✅ **[REORGANIZAÇÃO]** Revisão de Código integrada nas etapas CLI e GUI
- ✅ Etapa 7: Verificar Implementação CLI (inclui 9 critérios de qualidade)
- ✅ Etapa 8: Verificar Implementação GUI (inclui 9 critérios de qualidade)
- ✅ Etapa 9: Verificar Integração com Programa Principal (mantida como etapa separada)
- ✅ 9 Critérios: Omissão, Ambiguidade, Fato Incorreto, Redundância, Inconsistência, Falta de Integração, Menor Coesão, Maior Acoplamento, Informação Estranha
- ✅ Revisão integrada ao processo de verificação CLI/GUI
- ✅ Total de etapas: 12 → 13 (adicionada verificação de integração após GUI)

**Changelog v1.7** (02/12/2025):
- ✅ **[CRÍTICO]** Adicionada Etapa 8.5: Revisão de Código (ANTES dos testes)
- ✅ 9 Critérios de Qualidade: Omissão, Ambiguidade, Fato Incorreto, Redundância, Inconsistência, Falta de Integração, Menor Coesão, Maior Acoplamento, Informação Estranha
- ✅ Checklist completo de revisão (36 itens de verificação)
- ✅ Ferramentas recomendadas (pylint, vulture, radon, black, isort)
- ✅ Processo de revisão CLI e GUI detalhado
- ✅ Exemplos práticos de problemas e correções
- ✅ Integração com Etapa 9 (testar após revisar)
- ✅ Total de etapas: 12 → 13 (8.5 adicionada entre 8 e 9)

**Changelog v1.6**:
- ✅ **[AVANÇADO]** Adicionada Etapa 9.2: Testes em Threads/Processos com Monitoramento
- ✅ Execução de testes em processo separado (`multiprocessing.Process`)
- ✅ Logging em tempo real via `Queue` (progresso de cada teste)
- ✅ Cancelamento manual a qualquer momento (Ctrl+C gracioso)
- ✅ Timeout global + individual (dupla proteção)
- ✅ Estatísticas em tempo real (passed/failed/elapsed)
- ✅ Implementação completa de `test_runner_monitored.py` (~150 linhas)
- ✅ Checklist adicional opcional (6 itens)

**Changelog v1.5**:
- ✅ **[CRÍTICO]** Adicionada Etapa 9.1: Segurança em Testes
- ✅ 7 soluções obrigatórias para evitar loops infinitos e timeouts
- ✅ Timeout máximo obrigatório (30s por teste)
- ✅ Ambiente headless obrigatório para testes GUI (QT_QPA_PLATFORM=offscreen)
- ✅ Dry-run obrigatório antes de executar testes (syntax + import + collect)
- ✅ Checklist de segurança com 6 itens obrigatórios
- ✅ Regras de ouro e comandos seguros documentados
- ✅ Lições aprendidas do Task Example (loop infinito >1h)

**Changelog v1.4**:
- ✅ Reorganizada ordem final: Implementar → Integrar GUI → CLI → Testar → Organizar → Documentar → Commit
- ✅ Testes movidos para DEPOIS das verificações de integração (testar sistema integrado)
- ✅ Organizar pasta raiz movido para ANTES da documentação (documentar estado limpo)
- ✅ Lógica: Integrar → Testar integração → Limpar repositório → Documentar estado final

**Changelog v1.3**:
- ✅ Reorganizada ordem das etapas: Verificação de Integração GUI e CLI agora vêm ANTES da Documentação
- ✅ Nova ordem: Testes → Integração GUI → CLI → Documentação → Organizar → Commit
- ✅ Lógica: Verificar integração antes de documentar garante que a documentação reflete o estado real

**Changelog v1.2**:
- ✅ Adicionada Etapa 8: Verificar integração com programa principal
- ✅ Adicionada Etapa 9: Verificar implementação CLI com passagem de parâmetros
- ✅ Total de etapas: 10 → 12

---

## 🎯 Filosofia Central

> "Sempre vão ter tarefas complexas para fazer, mas também aquelas que são mais difíceis e aquelas que são mais fáceis. **Quero que você sempre comece pelas mais fáceis**."

**Princípio**: Do simples ao complexo, incremental, profissional e completo.

**NOVO v3.0**: + **Segurança e automação para produção** sem overhead de equipe.

---

## 🚫 Hierarquia de Prioridades Bloqueantes

> **CRÍTICO**: Ordem de prioridades que **BLOQUEIAM** desenvolvimento até serem resolvidas.

### 📊 Ordem (Do Mais ao Menos Crítico)

```
1️⃣ MAIS CRÍTICO: ❓ Dúvidas da IA → RESOLVER ANTES de continuar
2️⃣ BLOQUEANTE: 📚 Documentação (quando necessária) → ESCREVER ANTES de implementar  
3️⃣ BLOQUEANTE: ❌ Bugs/Erros → CORRIGIR ANTES de novas features
4️⃣ NORMAL: ✨ Novas Features → Após 1, 2, 3 resolvidos
```

### 2️⃣ Documentação é BLOQUEANTE

**Quando documentação bloqueia implementação**:
- ✅ API pública nova → Documentar ANTES
- ✅ Mudança arquitetural → Atualizar docs ANTES
- ✅ Breaking changes → Atualizar CHANGELOG IMEDIATAMENTE
- ✅ Nova dependência → Atualizar README ANTES

**[ESPECÍFICO SOLO]**:
> "Para solo developers, documentação é sua 'memória externa futura'. Você esquecerá por quê fez algo em 3 meses. Documente ANTES de implementar para validar seu design. Se não consegue documentar, o design está ruim. Documentação bloqueante previne retrabalho futuro."

**Análise custo-benefício (Solo)**:
- ⏱️ Tempo para documentar API: ~5-10 min
- ⏱️ Tempo economizado (evitando confusão futura): ~30-60 min
- 💰 ROI: 3x-6x (vale MUITO a pena)

**Fluxo MVP (Solo)**:
```
Tarefa → Dúvidas? (perguntar) → Documentar ANTES (5-10min) → Implementar → Testar
```

**Regra de Ouro Solo**: "Se levou mais tempo implementar que documentar, seu design está complexo demais. Simplifique."

---

## ⚠️ Regra de Ouro: Prioridade Absoluta para Erros no Workspace

> **CRÍTICO PARA IAs**: Antes de implementar novas funcionalidades ou continuar com tarefas, **todos os erros no workspace devem ser corrigidos POR VOCÊ (IA)**.

### 🤖 Esta Regra é Para Assistentes de IA

**Se você é uma IA (Cursor, GitHub Copilot, etc.):**
- ✅ **VOCÊ DEVE** corrigir todos os erros existentes ANTES de implementar novas funcionalidades
- ✅ **VOCÊ DEVE** resolver problemas de forma proativa, não esperar que humanos os corrijam
- ✅ **VOCÊ DEVE** tratar a correção de erros como prioridade máxima
- ✅ **VOCÊ DEVE** limpar o workspace antes de adicionar novo código

**Esta regra NÃO significa:**
- ❌ Que desenvolvedores humanos devem parar de implementar quando existem erros
- ❌ Que o projeto não pode avançar enquanto houver erros
- ❌ Que humanos precisam corrigir os erros manualmente

### 🚨 Tipos de Erros que Bloqueiam o Desenvolvimento

Considere a existência de erros no workspace (visíveis na aba "Problemas" do IDE) como **indesejável e bloqueante**. Caso aconteça alguma ocorrência dos seguintes tipos de erro, a **correção é prioridade absoluta** antes de continuar:

1. **❌ Problemas de Sintaxe**
   - Erros de parsing do código
   - Parênteses, chaves ou colchetes não fechados
   - Indentação incorreta (Python)
   - Ponto-e-vírgula faltando (JavaScript, C, Java)

2. **❌ Inconsistências de Código**
   - Variáveis declaradas mas não utilizadas
   - Imports não utilizados ou faltantes
   - Código morto (unreachable code)
   - Type mismatches (TypeScript, Python com type hints)

3. **❌ Omissões Inesperadas**
   - Funções declaradas mas não implementadas
   - Parâmetros obrigatórios faltando
   - Return statements ausentes quando esperados
   - Documentação obrigatória faltando

4. **❌ Fatos Incorretos**
   - Referências a variáveis inexistentes
   - Chamadas de funções com número errado de argumentos
   - Acesso a propriedades inexistentes
   - Imports de módulos inexistentes

5. **❌ Ambiguidades**
   - Warnings de type checking
   - Possíveis null/undefined references
   - Shadowing de variáveis
   - Conversões de tipo implícitas perigosas

6. **❌ Arquivos Faltosos**
   - Dependências não instaladas
   - Módulos importados mas não encontrados
   - Arquivos de configuração ausentes
   - Assets referenciados mas inexistentes

7. **❌ Falhas de Execução**
   - Build failures
   - Compilation errors
   - Testes falhando
   - Linter errors (quando configurado)

### ✅ Quando Pode Continuar

**SOMENTE** continue com o desenvolvimento de novas funcionalidades quando:

- ✅ **Zero erros** na aba "Problemas" do workspace
- ✅ **Todos os builds** completam com sucesso
- ✅ **Todos os testes** passam (se já existentes)
- ✅ **Linter/formatter** não reporta erros críticos
- ✅ **Type checker** não reporta erros (se aplicável)

### 📋 Checklist Antes de Cada Tarefa

```markdown
Antes de iniciar qualquer tarefa nova:

[ ] Verificar aba "Problemas" do IDE (0 erros)
[ ] Executar build do projeto (sucesso)
[ ] Executar testes existentes (todos passando)
[ ] Executar linter/formatter (sem erros críticos)
[ ] Verificar imports e dependências (todas resolvidas)
[ ] Confirmar que código está em estado limpo (commitável)
```

### ⏱️ Tempo Estimado para Correção

- **Erros de Sintaxe**: ~2-5 minutos por erro
- **Imports/Dependências**: ~5-10 minutos
- **Type Errors**: ~5-15 minutos por erro
- **Testes Falhando**: ~10-30 minutos (depende da complexidade)

**Regra Prática**: Se você tem >10 erros no workspace, **dedique 1-2 horas** para limpar tudo antes de prosseguir.

### 🎯 Rationale

**Por quê esta regra é crítica?**

1. **Prevenção de Cascata**: Um erro não corrigido pode gerar 10 novos erros
2. **Qualidade do Código**: Código com erros = dívida técnica imediata
3. **Confiabilidade**: Funcionalidades novas em cima de código quebrado = bugs garantidos
4. **Produtividade**: Corrigir erros antigos + novos é mais demorado que corrigir só os antigos
5. **Profissionalismo**: Código limpo e sem erros é requisito mínimo

**Mensagem para IAs**: 
> "Até que os erros não sejam sanados POR VOCÊ (IA), as tarefas e as funcionalidades não podem continuar sendo implementadas POR VOCÊ (IA). Corrija os erros primeiro, depois continue com a implementação."

---

## 📝 Padrão de Questionários Editáveis para Solo Developers

> **RECOMENDADO para decisões complexas**: Solo developers precisam documentar decisões importantes sem burocracia excessiva.

### 🎯 Quando Usar Questionários Editáveis (Solo)

**✅ Use questionários editáveis quando:**
- Decisão sobre **stack tecnológico** (escolha que afeta todo o projeto)
- Decisão sobre **arquitetura** (estrutura de pastas, padrões, etc.)
- Escolha de **bibliotecas críticas** (state management, routing, etc.)
- Planejamento de **features complexas** (múltiplas opções de implementação)
- Decisões com **impacto de longo prazo** (> 3 meses de projeto)
- Você quer **documentar para "você do futuro"** (por quê escolheu X e não Y)

**❌ NÃO use quando:**
- Decisão é trivial (qual cor de botão, nome de variável)
- Implementação é óbvia (só uma maneira razoável de fazer)
- Decisão pode ser revertida facilmente (< 1h de trabalho)

### 📋 Formato Solo-Friendly do Questionário

A IA deve criar um documento **simples e direto** (`.md`) sem burocracia:

```markdown
# Decisão: [Título] - [YYYY-MM-DD]

**Por quê este doc?** [Explicação breve do problema]

**O que você precisa decidir:** [Decisão principal em 1 linha]

---

### 🎯 OPÇÃO A: [Nome da Opção]

💡 **Recomendação da IA**: ✅ **Recomendada** (ou ⚙️ Condicional / ❌ Não recomendada)

**Resumo**: [1 frase sobre a opção]

**Vantagens**:
- ✅ [Vantagem 1]
- ✅ [Vantagem 2]

**Desvantagens**:
- ❌ [Desvantagem 1]
- ❌ [Desvantagem 2]

**Manutenção Estimada**: [~Xh/mês]

**Curva de Aprendizado**: 🟢 Fácil / 🟡 Moderada / 🔴 Íngreme

**Boring Tech?**: ✅ Sim (estável há 5+ anos) / ❌ Não (tecnologia nova/hype)

**Comunidade**: [Tamanho da comunidade: Pequena/Média/Grande]

**Exemplo de Projeto**: [Link para projeto real usando essa opção]

---

### 🎯 OPÇÃO B: [Nome]

[... mesmo formato ...]

---

### 🎯 OPÇÃO C (se houver)

[... mesmo formato ...]

---

## 📊 Comparação Rápida

| Critério | Opção A | Opção B | Opção C |
|----------|---------|---------|---------|
| **Manutenção/mês** | ~2h | ~5h | ~1h |
| **Curva Aprend.** | 🟢 Fácil | 🔴 Íngreme | 🟢 Fácil |
| **Boring Tech** | ✅ Sim | ❌ Não | ✅ Sim |
| **Comunidade** | Grande | Pequena | Média |
| **Deploy Grátis?** | ✅ Sim | ❌ Não | ✅ Sim |

**⭐ Melhor para Solo Dev**: Opção A (menor manutenção + comunidade grande)

---

## ✅ Sua Decisão

**Escolho:** _______ (A / B / C)

**Por quê:** _______

**Plano B (se não funcionar):** _______

**Tempo estimado para testar:** _______ (horas/dias)

**Gatilhos de Rollback** (quando desistir e mudar):
- [ ] Se levar >Xh para implementar feature simples
- [ ] Se bugs forem frequentes (>5 por semana)
- [ ] Se manutenção exceder Xh/semana
- [ ] Se não houver solução para problema Y na comunidade

---

## 🗓️ Registro para "Você do Futuro"

**Data da Decisão**: _______  
**Versão da Stack**: _______ (ex: Next.js 15.5.2)  
**Estado do Projeto**: _______ (ex: início / refatoração / produção)  
**Tempo de Projeto até Agora**: _______  
**O que estava tentando resolver**: _______

**Links Úteis**:
- Documentação oficial: _______
- Tutorial que ajudou: _______
- Thread no Stack Overflow: _______
- Discussão no Reddit: _______

---

**Status**: ⚙️ PENDENTE → ✅ DECIDIDO → 🚀 IMPLEMENTADO → 📈 VALIDADO

```

### 🔄 Fluxo Solo

**Passo 1: IA Cria Documento Simples**
```
IA identifica decisão complexa (ex: escolher state management)
     ↓
IA pesquisa opções (Zustand, Redux, Context API, etc.)
     ↓
IA cria DECISAO_STATE_MANAGEMENT_20260101.md
     ↓
IA preenche análise de cada opção (manutenção, curva aprend., etc.)
     ↓
IA marca recomendação (✅ Zustand - mais simples para solo)
     ↓
IA notifica: "Criei doc com 3 opções analisadas. Preencha sua decisão."
```

**Passo 2: Solo Dev Analisa e Decide (Sem Pressa)**
```
Você abre o doc, lê as 3 opções
     ↓
Você compara: manutenção, curva de aprendizado, comunidade
     ↓
Você vê que Opção A = 2h/mês vs Opção B = 5h/mês
     ↓
Você escolhe Opção A (menor manutenção)
     ↓
Você preenche "Por quê" e "Plano B"
     ↓
Você define gatilhos de rollback claros
     ↓
Você salva o arquivo
```

**Passo 3: IA Implementa Baseado na Sua Escolha**
```
Você notifica: "Decidi por Opção A (Zustand)"
     ↓
IA lê DECISAO_STATE_MANAGEMENT_20260101.md
     ↓
IA vê escolha + plano B + gatilhos de rollback
     ↓
IA instala Zustand e implementa
     ↓
IA mantém doc como referência futura ("por quê Zustand e não Redux?")
```

### 🎯 Diferencial Solo vs Enterprise

| Aspecto | Simplicity 3 (Solo) | Simplicity 2 (Enterprise) |
|---------|---------------------|---------------------------|
| **Formalidade** | Casual, direto | Formal com aprovações |
| **Foco** | Manutenção (h/mês) | ROI ($), Compliance |
| **Stakeholders** | Só você | Múltiplos com roles |
| **Decisão** | Imediata | 1-5 dias (aprovações) |
| **Boring Tech** | ✅ Prioridade | Não considerado |
| **Plano B** | Simples (1 alternativa) | Formal com análise de risco |
| **Rollback Triggers** | Pragmáticos (horas) | Corporativos (impacto) |
| **Tempo Preenchimento** | 5-10 min | 30-60 min (análises formais) |

### 💡 Dicas para Solo Developers

**✅ Priorize "Boring Technology":**
```
Boring Tech = Tecnologia madura (5+ anos) com:
- ✅ Grande comunidade
- ✅ Documentação excelente
- ✅ Poucos breaking changes
- ✅ Empregado por empresas grandes

Exemplo: React (boring ✅) vs Solid.js (hype ❌)
```

**✅ Calcule Manutenção em Horas/Mês:**
```
Stack com muita configuração = alta manutenção
Stack com defaults sensatos = baixa manutenção

Ex: Create React App (alta manutenção) vs Next.js (baixa manutenção)
```

**✅ Sempre Defina Plano B:**
```
Se escolher Opção A, sempre tenha Opção B como fallback

Ex: 
- Plano A: Next.js (se funcionar bem)
- Plano B: Vite + React (se Next.js for overkill)
```

**✅ Gatilhos de Rollback Pragmáticos:**
```
Não seja dogmático. Defina quando desistir:

"Se levar >20h para implementar auth básico → mudar para solução pronta"
"Se bugs de build ocorrerem >2x/semana → considerar stack mais estável"
```

### 📊 Exemplo Real: Escolher State Management

```markdown
# Decisão: State Management para App de Tarefas - 2026-01-01

**Por quê este doc?** Preciso escolher como gerenciar estado (tasks, filters, user)

**O que você precisa decidir:** Qual biblioteca de state management usar

---

### 🎯 OPÇÃO A: Zustand

💡 **Recomendação da IA**: ✅ **Recomendada para solo dev**

**Resumo**: State management minimalista baseado em hooks

**Vantagens**:
- ✅ API super simples (~50 linhas de código total)
- ✅ Zero boilerplate
- ✅ Bom para apps pequenos-médios

**Desvantagens**:
- ❌ Sem DevTools oficial (mas tem extensão)
- ❌ Comunidade menor que Redux

**Manutenção Estimada**: ~1h/mês

**Curva de Aprendizado**: 🟢 Fácil (30min para dominar básico)

**Boring Tech?**: ⚙️ Moderada (3 anos de existência, crescendo)

**Comunidade**: Média (15k stars GitHub)

**Exemplo de Projeto**: Vercel Dashboard usa Zustand

---

### 🎯 OPÇÃO B: Redux Toolkit

💡 **Recomendação da IA**: ⚙️ **Só se você já conhece Redux**

**Resumo**: State management com padrão Flux

**Vantagens**:
- ✅ Comunidade gigante (respostas fáceis no Stack Overflow)
- ✅ DevTools excelente

**Desvantagens**:
- ❌ Muito boilerplate (slices, actions, reducers...)
- ❌ Overkill para apps pequenos

**Manutenção Estimada**: ~5h/mês (refatorar slices)

**Curva de Aprendizado**: 🔴 Íngreme (1-2 semanas para dominar)

**Boring Tech?**: ✅ Sim (10+ anos de existência)

**Comunidade**: Grande (60k stars GitHub)

**Exemplo de Projeto**: Muitas empresas grandes (Uber, etc.)

---

### 🎯 OPÇÃO C: Context API (Built-in React)

💡 **Recomendação da IA**: ⚙️ **Só para estado super simples**

**Resumo**: Contexto nativo do React

**Vantagens**:
- ✅ Zero dependências externas
- ✅ Já conhece se conhece React

**Desvantagens**:
- ❌ Re-renders desnecessários em apps grandes
- ❌ Sem DevTools
- ❌ Difícil de escalar

**Manutenção Estimada**: ~0h/mês (nativo)

**Curva de Aprendizado**: 🟢 Fácil

**Boring Tech?**: ✅ Sim (parte do React)

**Comunidade**: Gigante (React)

---

## 📊 Comparação Rápida

| Critério | Zustand | Redux Toolkit | Context API |
|----------|---------|---------------|-------------|
| **Manutenção/mês** | ~1h | ~5h | ~0h |
| **Curva Aprend.** | 🟢 Fácil | 🔴 Íngreme | 🟢 Fácil |
| **Boring Tech** | ⚙️ Moderada | ✅ Sim | ✅ Sim |
| **Comunidade** | Média | Grande | Gigante |
| **Boilerplate** | Mínimo | Alto | Mínimo |

**⭐ Melhor para Solo Dev**: Zustand (menor manutenção + API simples)

---

## ✅ Sua Decisão

**Escolho:** A (Zustand)

**Por quê:** App é médio porte, quero baixa manutenção, API simples é prioridade

**Plano B (se não funcionar):** Context API (se app ficar muito simples)

**Tempo estimado para testar:** 2 dias (implementar 2-3 features)

**Gatilhos de Rollback**:
- [ ] Se levar >4h para implementar state de tasks → considerar Context API
- [ ] Se bugs de sincronização ocorrerem >3x → considerar Redux (mais previsível)
- [ ] Se precisar de time-travel debug frequente → Redux DevTools melhor

---

## 🗓️ Registro para "Você do Futuro"

**Data da Decisão**: 2026-01-01  
**Versão da Stack**: React 19, Zustand 4.5  
**Estado do Projeto**: Início (primeira semana)  
**Tempo de Projeto até Agora**: 3 dias  
**O que estava tentando resolver**: Gerenciar tasks, filters, user info

**Links Úteis**:
- Documentação oficial: https://github.com/pmndrs/zustand
- Tutorial que ajudou: https://youtu.be/ABC123
- Comparação Zustand vs Redux: https://example.com

---

**Status**: ✅ DECIDIDO (2026-01-01) → 🚀 IMPLEMENTADO (a fazer)
```

---

### ✅ Checklist Solo para IAs

Ao criar questionário para solo dev, a IA deve:

```markdown
[ ] Título com data (para "você do futuro")
[ ] Problema explicado em 1-2 linhas (contexto rápido)
[ ] Análise de manutenção (h/mês) para cada opção
[ ] Análise de curva de aprendizado (🟢🟡🔴)
[ ] Indicar se é "Boring Tech" ou "Hype"
[ ] Tamanho da comunidade (buscar respostas quando travar)
[ ] Comparação visual (tabela) para decisão rápida
[ ] Recomendação clara (qual a IA sugere para solo)
[ ] Espaço para Plano B (sempre ter fallback)
[ ] Gatilhos de rollback pragmáticos (quando desistir)
[ ] Seção "Para você do futuro" (por quê decidiu isso)
[ ] Links úteis (docs, tutorials, discussões)
```

### 🎓 Conclusão Solo

O padrão de questionários editáveis para solo developers:
- ✅ **Documenta** decisões importantes sem burocracia
- ✅ **Prioriza** manutenção e simplicidade (você está sozinho)
- ✅ **"Boring Tech"** como critério de escolha (estabilidade > hype)
- ✅ **Plano B sempre** (decisões reversíveis)
- ✅ **Registro histórico** ("por quê escolhi X em 2026")

**Regra Solo**: 
> "Se a decisão afeta >3 meses de projeto, documente em questionário editável. Você do futuro vai agradecer."

---

## 🔍 Busca Binária para Localização de Defeitos

> **IMPORTANTE PARA IAs**: Quando estiver lidando com correção de erros e eliminação de bugs, lembre-se de que existe a possibilidade de utilizar **busca binária** para localizar defeitos de maneira eficiente.

### 🎯 Conceito Central

A busca binária é uma técnica poderosa que reduz o espaço de busca pela metade a cada iteração, permitindo localizar defeitos em **O(log N) passos**, onde N é o número de linhas, comandos ou instruções do algoritmo.

**Exemplo Prático**: 
- Se um erro está na linha 48 de um arquivo com 512 linhas
- Busca linear: até 512 verificações
- Busca binária: apenas **9 verificações** (log₂(512) = 9)

### 📋 Metodologia de Busca Binária para Debugging

#### **1️⃣ Passo Inicial: Dividir o Código ao Meio**

Começando com um arquivo de N linhas onde existe um erro:
1. Comente metade do código (ex: linhas 257-512)
2. Execute/teste a metade restante (linhas 1-256)
3. Verifique se o erro persiste

**Decisão**:
- ✅ **Erro persiste**: O bug está na metade ativa (1-256)
- ❌ **Erro desaparece**: O bug está na metade comentada (257-512)

#### **2️⃣ Recursão: Continue Dividindo**

Uma vez identificada a metade com o problema, repita o processo:

**Iteração 2** (erro em 1-256):
- Comente linhas 129-256
- Teste linhas 1-128
- Identifique qual quarto contém o bug

**Iteração 3** (erro em 1-128):
- Comente linhas 65-128
- Teste linhas 1-64
- Identifique qual oitavo contém o bug

**Continue até** localizar exatamente a linha/bloco problemático.

#### **3️⃣ Exemplo Completo: 512 Linhas → Linha 48**

```
Iteração 1: [1-512]   → Testar [1-256]   ✅ Erro presente
Iteração 2: [1-256]   → Testar [1-128]   ✅ Erro presente  
Iteração 3: [1-128]   → Testar [1-64]    ✅ Erro presente
Iteração 4: [1-64]    → Testar [1-32]    ❌ Erro ausente → Bug em [33-64]
Iteração 5: [33-64]   → Testar [33-48]   ✅ Erro presente
Iteração 6: [33-48]   → Testar [33-40]   ✅ Erro presente
Iteração 7: [41-48]   → Testar [41-44]   ✅ Erro presente
Iteração 8: [45-48]   → Testar [45-46]   ✅ Erro presente
Iteração 9: [47-48]   → Testar [linha 47] ❌ Erro ausente → ✅ Bug na linha 48!
```

**Resultado**: 9 iterações para encontrar o bug em 512 linhas (vs. até 512 tentativas lineares).

### 🛠️ Técnicas de Implementação

#### **A) Comentários Temporários**
```python
# BUSCA BINÁRIA - Iteração 1: Testando [1-256]
# Linhas 257-512 temporariamente desabilitadas
# def funcao_suspeita():  
#     codigo_potencialmente_bugado()
#     mais_codigo()
```

#### **B) Flags de Debug**
```python
DEBUG_BINARY_SEARCH = True
RANGE_START = 1
RANGE_END = 256

if DEBUG_BINARY_SEARCH and not (RANGE_START <= current_line <= RANGE_END):
    return  # Pular execução fora do range de teste
```

#### **C) Git Bisect** (para bugs introduzidos em commits)
```bash
# Usar git bisect para encontrar commit que introduziu o bug
git bisect start
git bisect bad HEAD              # Commit atual tem bug
git bisect good v1.0.0           # Commit v1.0.0 não tinha bug
# Git automaticamente faz busca binária nos commits
```

#### **D) Testes Unitários Particionados**
```python
# Dividir suite de testes ao meio
pytest tests/test_module_part1.py  # Primeira metade
pytest tests/test_module_part2.py  # Segunda metade
# Identificar qual metade contém teste falhando
```

### 🎨 Aplicações Criativas da Busca Binária

A busca binária não se limita a linhas de código. Pode ser aplicada a:

1. **📦 Dependências/Imports**:
   - Comente metade dos imports
   - Identifique qual import causa conflito/erro
   
2. **🔧 Parâmetros de Configuração**:
   - Desabilite metade das configurações
   - Encontre configuração problemática

3. **🗃️ Dados de Entrada**:
   - Processe metade do dataset
   - Identifique qual subset causa erro

4. **⚙️ Features/Funcionalidades**:
   - Desabilite metade das features
   - Localize feature que causa regressão

5. **🧩 Módulos/Componentes**:
   - Desabilite metade dos módulos
   - Encontre módulo com bug

6. **📅 Histórico de Versões** (Git Bisect):
   - Teste versão no meio do histórico
   - Encontre commit que introduziu bug

7. **🔄 Iterações de Loop**:
   - Execute metade das iterações
   - Identifique em qual iteração erro ocorre

### ✅ Checklist de Busca Binária para Debugging

```markdown
[ ] 1. Confirmar que erro é reproduzível consistentemente
[ ] 2. Identificar escopo total (N linhas/módulos/commits)
[ ] 3. Calcular número de iterações necessárias: log₂(N)
[ ] 4. Criar backup ou branch de testes
[ ] 5. Iteração 1: Comentar/desabilitar metade superior/inferior
[ ] 6. Executar teste e verificar se erro persiste
[ ] 7. Anotar resultado e reduzir escopo pela metade
[ ] 8. Repetir até isolar linha/bloco/commit exato
[ ] 9. Analisar código isolado para entender causa raiz
[ ] 10. Aplicar correção e validar com testes
[ ] 11. Remover código de debug/comentários temporários
```

### 🎯 Quando Usar Busca Binária para Debugging

**✅ Use quando:**
- Erro é reproduzível mas causa não é óbvia
- Codebase grande (>100 linhas)
- Suspeita de que bug está em região específica mas ampla
- Erro apareceu após mudanças grandes (múltiplos commits)
- Teste falha mas não há indicação clara do problema
- Performance degradou mas não sabe qual função é responsável

**❌ Não use quando:**
- Erro é esporádico/não reproduzível (race condition, timing issue)
- Stack trace já aponta linha exata do problema
- Código é muito pequeno (<50 linhas)
- Bug é óbvio após leitura rápida do código

### ⏱️ Eficiência da Busca Binária

| Tamanho (N) | Busca Linear | Busca Binária | Ganho |
|------------|--------------|---------------|-------|
| 32 linhas  | até 32 passos | 5 passos | 6.4x mais rápido |
| 128 linhas | até 128 passos | 7 passos | 18.3x mais rápido |
| 512 linhas | até 512 passos | 9 passos | 56.9x mais rápido |
| 1024 linhas | até 1024 passos | 10 passos | 102.4x mais rápido |
| 4096 linhas | até 4096 passos | 12 passos | 341.3x mais rápido |

### 💡 Dicas Práticas

1. **Documente o Processo**: Anote cada iteração e resultado
2. **Use Controle de Versão**: Crie branches para cada teste
3. **Automatize Quando Possível**: Scripts para comentar/descomentar blocos
4. **Combine com Logs**: Adicione prints para confirmar execução de blocos
5. **Teste Isoladamente**: Garanta que o teste é determinístico
6. **Valide Antes e Depois**: Confirme que bug existe antes e foi corrigido depois

### 🚀 Rationale

**Por quê a busca binária é poderosa para debugging?**

1. **⚡ Eficiência Algorítmica**: O(log N) vs O(N) - economia exponencial de tempo
2. **🎯 Isolamento Preciso**: Reduz incerteza sistematicamente
3. **🧠 Menor Carga Cognitiva**: Decisões simples (erro presente: sim/não)
4. **📊 Previsibilidade**: Sabe exatamente quantos passos serão necessários
5. **🔄 Aplicabilidade Universal**: Funciona para código, dados, configurações, histórico
6. **✅ Garantia de Sucesso**: Se o bug é reproduzível, a busca binária sempre encontra

**Mensagem para IAs**:
> "A criatividade no uso de busca binária não tem limites. Sempre considere se um problema de debugging pode ser reduzido a uma busca binária - você economizará tempo e encontrará bugs mais rapidamente."

---

## 🧠 Fator de Memória Associativa

> **IMPORTANTE PARA IAs**: Durante investigação e correção de erros, aplique o **Fator de Memória Associativa** para aprender com padrões passados e acelerar diagnósticos futuros.

**Versão:** 1.0  
**Data:** 2025-12-28

### 🎯 Visão Geral

O **Fator de Memória Associativa** é um conceito fundamental que integra os Protocolos Simplicidade, permitindo que a inteligência artificial aprenda com padrões de erros passados e aplique esse conhecimento na investigação e correção de defeitos futuros.

#### 🔍 O Que é Memória Associativa?

Memória associativa é a capacidade de:
- ✅ **Reconhecer padrões** recorrentes em erros e defeitos
- ✅ **Associar causas e efeitos** específicos em diferentes contextos
- ✅ **Generalizar soluções** a partir de casos específicos
- ✅ **Deduzir problemas** do geral para o específico
- ✅ **Induzir regras** do específico para o geral

#### 🎯 Objetivo

Permitir que a IA desenvolva uma "memória" de problemas e soluções, criando associações entre:
- Tipos de erro e suas causas raiz
- Sintomas observados e diagnósticos precisos
- Contextos de projeto e padrões de defeito
- Soluções aplicadas e sua eficácia

---

### 🐍 Conexão com Python Traceback

#### 📊 Como o Traceback Funciona

O Traceback do Python apresenta erros em uma estrutura **top-down** (de cima para baixo, ou de fora para dentro):

```python
Traceback (most recent call last):
  File "main.py", line 10, in <module>          # ← RAIZ (Orquestrador)
    processar_dados()
  File "processador.py", line 45, in processar_dados  # ← GALHO (Coordenador)
    validar_entrada(dados)
  File "validador.py", line 23, in validar_entrada    # ← FOLHA (Executor)
    assert len(dados) > 0                             # ← ERRO ESPECÍFICO
AssertionError: lista vazia
```

#### 🎯 Metodologia Top-Down de Investigação

**Nível 1: Orquestrador (main.py)**
- Onde o erro foi **disparado**?
- Qual o **contexto** de execução?
- Quais **dados** foram passados?

**Nível 2: Coordenador (processador.py)**
- Como os dados foram **transformados**?
- Qual **lógica de negócio** foi aplicada?
- Houve **validações intermediárias**?

**Nível 3: Executor (validador.py)**
- Qual **operação específica** falhou?
- Qual **pré-condição** foi violada?
- Qual a **causa raiz** técnica?

#### 🧠 Associação com Memória

A IA deve **lembrar** e **associar**:
- **Padrão observado**: `AssertionError` em validação de entrada
- **Causa comum**: Dados vazios não tratados em nível superior
- **Solução típica**: Adicionar verificação antes de chamar `validar_entrada()`
- **Prevenção futura**: Sempre validar lista não-vazia antes de processar

#### 🔄 Analogia com Árvore de Importações

A estrutura de Traceback espelha a Árvore de Importações:

```
main.py (RAIZ)
  └─ processador.py (GALHO)
       └─ validador.py (FOLHA) ← Erro aqui!
```

**Insight de Memória Associativa**:
- Erros em **folhas** geralmente indicam **pré-condições violadas**
- Erros em **galhos** geralmente indicam **lógica de coordenação incorreta**
- Erros na **raiz** geralmente indicam **integração ou orquestração problemática**

---

### 🔬 Abordagens Dedutiva e Indutiva

#### 📉 Abordagem Dedutiva (Geral → Específico)

**Conceito**: Partir de uma regra geral para identificar casos específicos.

**Exemplo Prático**:

**Regra Geral**: "Erros de `AttributeError` geralmente indicam que um objeto não foi inicializado corretamente"

**Aplicação Específica**:
```python
# Erro observado
AttributeError: 'NoneType' object has no attribute 'process'

# Dedução:
1. ✅ Regra geral: AttributeError → objeto não inicializado
2. ✅ Hipótese: variável retornou None ao invés de objeto
3. ✅ Investigação: verificar métodos que retornam o objeto
4. ✅ Solução: adicionar verificação de None ou corrigir inicialização
```

**Fluxo Dedutivo**:
```
Teoria Geral (conhecimento prévio)
         ↓
Hipótese Específica (baseada no erro)
         ↓
Teste da Hipótese (debugging)
         ↓
Confirmação/Refutação
```

#### 📈 Abordagem Indutiva (Específico → Geral)

**Conceito**: Observar casos específicos repetidos para criar uma regra geral.

**Exemplo Prático**:

**Observação 1**:
```python
# Projeto A
IndexError: list index out of range
# Causa: loop usando range(len(lista) + 1)
```

**Observação 2**:
```python
# Projeto B  
IndexError: list index out of range
# Causa: acesso a lista[i] sem verificar len(lista)
```

**Observação 3**:
```python
# Projeto C
IndexError: list index out of range
# Causa: iteração manual com índice incrementado incorretamente
```

**Indução (Regra Geral)**:
> "70% dos `IndexError` são causados por manipulação manual incorreta de índices.  
> **Solução preventiva**: Sempre preferir iteradores (`for item in lista`) ao invés de índices manuais."

**Fluxo Indutivo**:
```
Caso Específico 1
      +
Caso Específico 2
      +
Caso Específico 3
      ↓
Padrão Identificado
      ↓
Regra Geral (nova memória associativa)
      ↓
Aplicação Preventiva em Projetos Futuros
```

#### 🔄 Combinação Dedutiva-Indutiva (Neuro-Simbólica)

**Ciclo Completo de Aprendizado**:

1. **Dedutivo**: Aplicar regras gerais existentes para diagnosticar erro atual
2. **Validação**: Confirmar ou refutar a hipótese dedutiva
3. **Indutivo**: Se padrão novo é observado, adicionar à base de conhecimento
4. **Refinamento**: Atualizar regras gerais com novos casos específicos

**Exemplo de Ciclo**:
```
[Dedutivo] Regra: "TypeError geralmente indica tipo incompatível"
           ↓
[Aplicação] Erro: TypeError ao somar string + int
           ↓
[Validação] ✅ Confirmado: tentativa de soma incompatível
           ↓
[Indutivo] Novo padrão: "TypeError com '+' → verificar tipos antes de operação"
           ↓
[Memória] Armazenar: "Sempre validar tipos antes de operações matemáticas"
```

---

### 🐛 Taxonomia de Defeitos de Software

A taxonomia de defeitos de software identifica cinco categorias principais de problemas altamente indesejáveis e inesperados:

#### 1️⃣ Fato Incorreto

**Definição**: Informação no código que está errada ou desatualizada.

**Exemplos**:
```python
# ❌ Fato incorreto
PI = 3.14  # Valor impreciso

# ✅ Correção
PI = 3.14159265359  # Valor correto com precisão adequada
```

```python
# ❌ Fato incorreto  
MAX_UPLOAD_SIZE = 5 * 1024  # Comentário diz "5MB" mas código é 5KB

# ✅ Correção
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB correto
```

**Memória Associativa**:
- Sempre validar **constantes numéricas** contra requisitos
- Revisar **comentários** para garantir alinhamento com código
- Usar **testes de limites** para valores críticos

#### 2️⃣ Informação Estranha

**Definição**: Código, comentários ou lógica que não pertence ao contexto atual.

**Exemplos**:
```python
# ❌ Informação estranha
def calcular_preco(valor):
    # TODO: implementar desconto para clientes VIP
    # print("DEBUG: valor =", valor)  # Código de debug esquecido
    # import random  # Import não utilizado
    resultado = valor * 1.1
    return resultado
```

```python
# ✅ Correção
def calcular_preco(valor):
    """Calcula preço com taxa de 10%."""
    resultado = valor * 1.1
    return resultado
```

**Memória Associativa**:
- Remover **código comentado** não utilizado
- Eliminar **imports desnecessários** (use linter)
- Limpar **TODOs** concluídos ou movê-los para sistema de tarefas

#### 3️⃣ Ambiguidade

**Definição**: Código ou documentação que pode ser interpretado de múltiplas formas.

**Exemplos**:
```python
# ❌ Ambíguo
def processar(dados):
    """Processa os dados."""  # O que significa "processar"?
    return dados
```

```python
# ✅ Específico
def normalizar_e_validar_entrada_usuario(dados_brutos):
    """
    Normaliza entrada do usuário (lowercase, trim) e valida formato de email.
    
    Args:
        dados_brutos: String com email fornecido pelo usuário
        
    Returns:
        String com email normalizado e validado
        
    Raises:
        ValueError: Se formato de email é inválido
    """
    email_normalizado = dados_brutos.strip().lower()
    if "@" not in email_normalizado:
        raise ValueError("Email inválido: falta '@'")
    return email_normalizado
```

**Memória Associativa**:
- Usar **nomes descritivos** que explicam intenção
- Adicionar **docstrings detalhadas** com Args/Returns/Raises
- Incluir **exemplos de uso** na documentação
- Preferir **especificidade** sobre brevidade

#### 4️⃣ Inconsistência

**Definição**: Violação de padrões ou convenções estabelecidas no projeto.

**Exemplos**:
```python
# ❌ Inconsistente
def calcular_total(preco):  # snake_case
    return preco * 1.1

def CalcularDesconto(preco):  # PascalCase - INCONSISTENTE!
    return preco * 0.9

def calcPreco(valor):  # camelCase - INCONSISTENTE!
    return valor
```

```python
# ✅ Consistente
def calcular_total(preco):  # snake_case
    return preco * 1.1

def calcular_desconto(preco):  # snake_case
    return preco * 0.9

def calcular_preco_final(valor):  # snake_case
    return valor
```

**Mais Exemplos de Inconsistência**:
```python
# ❌ Ordem de parâmetros inconsistente
def enviar_email(destinatario, assunto, corpo): pass
def enviar_sms(corpo, numero): pass  # Ordem diferente!

# ✅ Ordem consistente
def enviar_email(destinatario, assunto, corpo): pass
def enviar_sms(destinatario, corpo): pass
```

**Memória Associativa**:
- Estabelecer **guia de estilo** no início do projeto
- Usar **linters** (pylint, flake8) para enforçar padrões
- Manter **consistência de nomenclatura** (snake_case para Python)
- Seguir **ordem de parâmetros** consistente em funções similares
- Aplicar **padrões de retorno** uniformes (sempre retornar tipo, nunca misturar None com valores)

#### 5️⃣ Omissão

**Definição**: Código ou lógica faltante que deveria existir.

**Exemplos**:
```python
# ❌ Omissão: falta validação de entrada
def dividir(a, b):
    return a / b  # ZeroDivisionError se b == 0!
```

```python
# ✅ Com validação
def dividir(a, b):
    if b == 0:
        raise ValueError("Divisor não pode ser zero")
    return a / b
```

```python
# ❌ Omissão: falta tratamento de exceção
dados = baixar_dados_api()  # Pode falhar por rede!
processar(dados)
```

```python
# ✅ Com tratamento
try:
    dados = baixar_dados_api()
except RequestException as e:
    logger.error(f"Falha ao baixar dados: {e}")
    dados = carregar_dados_cache()
processar(dados)
```

**Memória Associativa**:
- Sempre adicionar **validação de pré-condições**
- Implementar **tratamento de exceções** para operações que podem falhar
- Incluir **testes de borda** (edge cases) para detectar omissões
- Adicionar **logging** em operações críticas
- Documentar **limitações conhecidas** se algo não pode ser implementado

#### 🎯 Impacto no Desenvolvimento

Estes cinco tipos de defeitos são **altamente indesejáveis e inesperados** porque:

❌ **Não contribuem** para o atendimento dos requisitos do desenvolvedor  
❌ **Não satisfazem** as necessidades do cliente direto  
❌ **Não agregam valor** para os clientes do cliente (usuários finais)  
❌ **Introduzem riscos** de bugs em produção  
❌ **Reduzem confiabilidade** do sistema  
❌ **Aumentam custos** de manutenção e suporte

✅ **Objetivo dos Protocolos**: **Eliminar sistematicamente** estes cinco defeitos através de processos rigorosos de validação, revisão e testes.

---

### 🔄 Padrões de Erro e Memória Associativa

#### 🎯 Erros Independentes de Entrada

**Conceito**: Erros que ocorrem **sempre**, independentemente dos dados fornecidos.

**Exemplo**:
```python
# ❌ Erro sempre presente
def processar_lista(items):
    resultado = []
    for i in range(len(items) + 1):  # BUG: sempre causa IndexError
        resultado.append(items[i])
    return resultado
```

**Características**:
- ✅ Reproduzível em **100% dos casos**
- ✅ Não depende de **dados específicos**
- ✅ Indica erro **estrutural** na lógica
- ✅ Mais fácil de **diagnosticar e corrigir**

**Memória Associativa**:
> "Se erro ocorre em todos os testes com dados diferentes, o problema está na **lógica** e não nos **dados**."

#### 🎯 Erros em Escopo Específico

**Conceito**: Erros confinados a um módulo, função ou arquivo específico.

**Exemplo**:
```python
# Módulo: validador.py
def validar_cpf(cpf):
    # BUG: validação incorreta aqui
    return len(cpf) == 11  # Simplificação excessiva!

# Múltiplos lugares usando validador.py:
# - cadastro.py: falha na validação
# - login.py: falha na validação  
# - perfil.py: falha na validação
```

**Características**:
- ✅ **Um único local** com bug
- ✅ **Múltiplos sintomas** em diferentes partes do sistema
- ✅ Corrigir **uma vez** resolve **todos os casos**

**Memória Associativa**:
> "Se múltiplos componentes apresentam o mesmo erro, procure **dependência compartilhada** (import comum)."

#### 🎯 Erros por Importação de Código Bugado

**Conceito**: Algoritmos diferentes falham porque importam o mesmo módulo com defeito.

**Exemplo**:
```python
# utils.py (CÓDIGO BUGADO)
def formatar_data(data):
    return data.strftime("%d/%m/%Y")  # BUG: falha se data = None

# modulo_a.py
from utils import formatar_data
resultado_a = formatar_data(data_a)  # ❌ Falha

# modulo_b.py  
from utils import formatar_data
resultado_b = formatar_data(data_b)  # ❌ Falha

# modulo_c.py
from utils import formatar_data  
resultado_c = formatar_data(data_c)  # ❌ Falha
```

**Investigação com Memória Associativa**:

1. **Observação**: 3 módulos diferentes falham com mesmo `AttributeError`
2. **Padrão**: Todos importam `utils.formatar_data`
3. **Hipótese**: Bug está em `utils.py`, não nos módulos que o usam
4. **Validação**: Testar `formatar_data` isoladamente
5. **Correção**: Corrigir em `utils.py` uma única vez
6. **Verificação**: Todos os 3 módulos voltam a funcionar

**Memória Associativa**:
> "Padrão de erro idêntico em módulos diferentes → investigar **dependências compartilhadas** primeiro."

#### 📊 Base de Conhecimento de Padrões

A IA deve construir e manter uma **base de conhecimento associativa**:

| Padrão de Erro | Causa Provável | Estratégia de Investigação | Solução Típica |
|----------------|----------------|----------------------------|----------------|
| `AttributeError: 'NoneType'` | Variável não inicializada | Rastrear retorno de None | Adicionar verificação ou corrigir inicialização |
| `IndexError: list index out of range` | Loop com índices incorretos | Verificar ranges e len() | Usar iteradores ao invés de índices |
| `KeyError` | Chave não existe no dicionário | Verificar população do dict | Usar dict.get() ou validar chave existe |
| `TypeError: unsupported operand` | Tipos incompatíveis | Verificar tipos de variáveis | Adicionar conversão ou validação de tipo |
| `RecursionError: maximum recursion depth` | Recursão sem caso base | Analisar condição de parada | Adicionar/corrigir caso base |
| `ImportError` / `ModuleNotFoundError` | Dependência faltante | Verificar requirements | Instalar dependência |

**Atualização Contínua**:
- ✅ A cada erro resolvido, **adicionar** à base de conhecimento
- ✅ A cada padrão confirmado, **reforçar** associação
- ✅ A cada falso positivo, **refinar** regra de diagnóstico

---

### 🧠 Integração com Inteligência Artificial Neuro-Simbólica

#### 🎯 O Que é IA Neuro-Simbólica?

**IA Simbólica** (Dedutiva):
- Baseada em **regras explícitas** e **lógica formal**
- Exemplo: "Se error == 'AttributeError' então verificar inicialização"

**IA Neural** (Indutiva):
- Baseada em **aprendizado por padrões** de dados
- Exemplo: Rede neural treinada para reconhecer tipos de erro por sintomas

**IA Neuro-Simbólica** (Combinação):
- **Combina** regras explícitas com aprendizado de padrões
- **Une** dedução (top-down) com indução (bottom-up)
- **Permite** raciocínio transparente e adaptação contínua

#### 🔄 Analogia com HDC (Hyperdimensional Computing)

O problema statement menciona HDC como referência para unir conceitos:

**HDC**: Representa conceitos como vetores de alta dimensão, permitindo:
- ✅ Associação entre conceitos similares
- ✅ Composição de conceitos complexos
- ✅ Recuperação de memórias por similaridade

**Aplicação em Debugging**:
```
Vetor(Error) = Vetor(Tipo) + Vetor(Contexto) + Vetor(Stacktrace)

Similaridade(Error_Atual, Error_Histórico) → Recuperar Solução
```

#### 🎯 Ciclo Neuro-Simbólico de Debugging

```
1. [Simbólico] Aplicar regras gerais conhecidas (dedução)
                      ↓
2. [Neural] Buscar padrões similares em histórico (associação)
                      ↓
3. [Simbólico] Formular hipótese específica (diagnóstico)
                      ↓
4. [Neural] Validar hipótese com testes (indução)
                      ↓
5. [Simbólico] Aplicar correção baseada em regra
                      ↓
6. [Neural] Aprender novo padrão e atualizar base
```

#### 📊 Exemplo Prático Completo

**Situação**: Erro inesperado ao processar upload de arquivo

**Fase 1 - Dedução (Simbólica)**:
```
Traceback mostra: ValueError em parse_csv()
Regra geral: "ValueError geralmente indica formato de dados incorreto"
Hipótese: Arquivo CSV está malformado
```

**Fase 2 - Associação (Neural)**:
```
Buscar em histórico: erros similares com CSV
Padrão encontrado: 3 casos anteriores com encoding UTF-8/Latin1
Associação: "ValueError em CSV → problema de encoding"
```

**Fase 3 - Diagnóstico (Simbólico)**:
```
Hipótese refinada: Arquivo CSV usa encoding Latin1 mas código assume UTF-8
Teste: Tentar abrir com encoding='latin1'
```

**Fase 4 - Validação (Neural)**:
```
Teste confirma: arquivo abre com Latin1
Indução: "Padrão confirmado - arquivos CSV de sistema legado usam Latin1"
```

**Fase 5 - Correção (Simbólica)**:
```python
# Antes (bugado)
with open(arquivo, 'r') as f:
    dados = csv.reader(f)

# Depois (corrigido)
with open(arquivo, 'r', encoding='latin1') as f:
    dados = csv.reader(f)
```

**Fase 6 - Aprendizado (Neural)**:
```
Adicionar à base de conhecimento:
"CSV + ValueError + parse error → tentar encoding='latin1'"
Reforçar padrão: 4 casos confirmados
Criar regra preventiva: Sempre especificar encoding explicitamente
```

---

### 🔧 Aplicação Prática nos Protocolos

#### 📘 Integração no Protocolo Simplicidade 1

**Etapa 4: Correção de Erros**

Adicionar subsecção "Memória Associativa":

```markdown
### 🧠 Aplicar Memória Associativa

Antes de iniciar correção:

1. **Consultar Base de Conhecimento**
   - [ ] Buscar erros similares em histórico do projeto
   - [ ] Verificar padrões conhecidos para este tipo de erro
   - [ ] Revisar soluções aplicadas anteriormente

2. **Análise Dedutiva** (Geral → Específico)
   - [ ] Aplicar regras gerais do tipo de erro observado
   - [ ] Formular hipótese baseada em conhecimento prévio
   - [ ] Identificar escopo provável (folha/galho/raiz)

3. **Análise Indutiva** (Específico → Geral)
   - [ ] Identificar se erro se repete em múltiplos contextos
   - [ ] Procurar dependências compartilhadas
   - [ ] Verificar se erro é independente de entrada

4. **Correção e Aprendizado**
   - [ ] Aplicar correção baseada em análise
   - [ ] Validar que correção resolve problema
   - [ ] Adicionar caso à base de conhecimento
   - [ ] Atualizar regras gerais se necessário
```

#### 📕 Integração no Protocolo Simplicidade 2

**Etapa de Code Review**

Adicionar checklist de Taxonomia de Defeitos:

```markdown
### 🐛 Checklist de Taxonomia de Defeitos

Durante code review, verificar ausência de:

- [ ] **Fato Incorreto**: Valores, constantes ou comentários desatualizados
- [ ] **Informação Estranha**: Código comentado, TODOs obsoletos, imports não utilizados
- [ ] **Ambiguidade**: Nomes vagos, documentação incompleta
- [ ] **Inconsistência**: Violação de convenções de nomenclatura ou padrões
- [ ] **Omissão**: Falta de validações, tratamento de exceções, ou edge cases
```

#### 📗 Integração no Protocolo Simplicidade 3 (Solo Developer em Produção)

**Etapa de Produção - Análise de Logs**

Adicionar seção de análise de padrões:

```markdown
### 📊 Análise de Padrões em Logs de Produção

Ao investigar erros em produção (solo developer):

1. **Frequência de Ocorrência**
   - [ ] Erro é isolado ou recorrente?
   - [ ] Ocorre com dados específicos ou todos os dados?
   - [ ] Frequência aumentou recentemente? (regressão)

2. **Correlação com Deploy**
   - [ ] Erro começou após deploy específico?
   - [ ] Use git bisect para identificar commit causador
   - [ ] Reverta mudanças suspeitas e valide

3. **Análise de Escopo**
   - [ ] Erro está em módulo específico ou múltiplos?
   - [ ] Múltiplos módulos importam código bugado comum?
   - [ ] Traceback aponta para folha, galho ou raiz?

4. **Base de Conhecimento Pessoal** (específico para solo)
   - [ ] Erro já ocorreu antes? Qual foi a solução?
   - [ ] Padrão é conhecido? Aplicar solução padrão
   - [ ] Novo padrão? Documentar detalhadamente para referência futura
   - [ ] Manter registro pessoal em `docs/DEBUGGING_LOG.md`

5. **Prevenção Proativa** (específico para solo)
   - [ ] Criar testes de regressão para erros corrigidos
   - [ ] Documentar padrões específicos do projeto
   - [ ] Implementar monitoramento automático (alertas)
   - [ ] Adicionar logging estratégico em pontos críticos
```

**Base de Conhecimento Pessoal** (específico para Simplicidade 3):

```markdown
### 🗂️ Gestão de Conhecimento Solo

Para solo developers em produção:

1. **Registro de Bugs Resolvidos**
   - [ ] Manter `docs/DEBUGGING_LOG.md` atualizado
   - [ ] Formato: Data | Erro | Causa Raiz | Solução
   - [ ] Incluir snippets de código antes/depois
   - [ ] Adicionar tempo de resolução para métricas

2. **Automação de Memória**
   - [ ] Scripts para análise de logs comuns
   - [ ] Alerts para padrões de erro conhecidos
   - [ ] Dashboards de monitoramento (Grafana, etc.)
   - [ ] Testes automatizados para regressões

3. **Documentação Rápida**
   - [ ] Usar templates para documentar erros
   - [ ] Manter índice de erros por categoria
   - [ ] Links para commits de correção
   - [ ] Tags para busca rápida (error-type, component)

4. **Revisão Periódica** (mensal)
   - [ ] Analisar padrões de erros recorrentes
   - [ ] Atualizar scripts de prevenção
   - [ ] Refatorar código com problemas frequentes
   - [ ] Priorizar melhorias de arquitetura

Exemplo de `docs/DEBUGGING_LOG.md`:
```markdown
# Debugging Log - [Nome do Projeto]

## 2025-12-28 - ValueError em CSV parsing

**Erro**: `ValueError: could not convert string to float`  
**Módulo**: `data_processor.py:line 45`  
**Causa Raiz**: CSV com encoding Latin1 sendo lido como UTF-8  
**Solução**: Adicionar `encoding='latin1'` no open()  
**Tempo de Resolução**: 45min  
**Commits**: [`abc123f`](link), [`def456a`](link)  
**Teste de Regressão**: `test_csv_latin1_encoding()`  
**Tags**: #csv #encoding #latin1  

**Lição Aprendida**: Sempre especificar encoding explicitamente ao ler arquivos externos
```
```

---

### ✅ Checklist de Utilização

#### 🎯 Para Inteligências Artificiais

Ao investigar e corrigir erros, a IA deve:

**Fase de Análise**:
- [ ] Examinar Traceback de cima para baixo (raiz → folha)
- [ ] Identificar nível do erro (orquestrador/coordenador/executor)
- [ ] Consultar base de conhecimento para padrões similares
- [ ] Aplicar dedução: regras gerais → hipótese específica
- [ ] Buscar indução: múltiplos casos → padrão geral

**Fase de Investigação**:
- [ ] Verificar se erro é independente de entrada
- [ ] Identificar escopo específico do problema
- [ ] Procurar código compartilhado (imports comuns)
- [ ] Aplicar busca binária se necessário
- [ ] Usar git bisect para regressões

**Fase de Correção**:
- [ ] Validar ausência de Fato Incorreto
- [ ] Remover Informação Estranha
- [ ] Eliminar Ambiguidades
- [ ] Garantir Consistência com padrões do projeto
- [ ] Corrigir Omissões (validações, tratamento de erros)

**Fase de Aprendizado**:
- [ ] Adicionar caso à base de conhecimento
- [ ] Atualizar regras gerais se novo padrão identificado
- [ ] Documentar solução para referência futura
- [ ] **[Simplicidade 3]** Atualizar `docs/DEBUGGING_LOG.md`
- [ ] **[Simplicidade 3]** Criar teste de regressão
- [ ] Reforçar associações de padrões confirmados

#### 📊 Métricas de Sucesso

**Indicadores de Boa Memória Associativa**:
- ✅ **Tempo de diagnóstico reduzido** (menos tempo para identificar causa)
- ✅ **Taxa de correção aumentada** (mais erros corrigidos na primeira tentativa)
- ✅ **Prevenção efetiva** (menos erros recorrentes)
- ✅ **Base de conhecimento crescente** (mais padrões documentados)
- ✅ **Aplicação consistente** (soluções padronizadas)
- ✅ **[Simplicidade 3]** Tempo médio de resolução decrescente

---

### 🎓 Conclusão

O **Fator de Memória Associativa** transforma a abordagem de debugging de reativa para proativa:

- 🧠 **Aprende** com erros passados
- 🔍 **Reconhece** padrões recorrentes
- 🎯 **Aplica** soluções validadas
- 📈 **Evolui** continuamente
- 🚀 **Previne** problemas futuros
- 👤 **[Simplicidade 3]** Mantém conhecimento pessoal organizado

A integração de abordagens **dedutivas** (top-down) e **indutivas** (bottom-up), combinadas com a análise sistemática da **taxonomia de defeitos**, cria uma IA neuro-simbólica capaz de:

✅ Diagnosticar erros mais rapidamente  
✅ Aplicar soluções mais efetivas  
✅ Prevenir problemas recorrentes  
✅ Melhorar continuamente sua base de conhecimento  
✅ Atender melhor os requisitos de desenvolvedores e clientes  
✅ **[Simplicidade 3]** Manter solo developer produtivo e sem sobrecarga

---

## 🌐 Idioma do Código: Nomenclatura de Variáveis e Comentários

> **IMPORTANTE PARA IAs**: A escolha do idioma para nomes de variáveis e comentários deve ser definida logo no início do projeto, preferencialmente na primeira sessão de interação com o programador.

### 📋 Regra Padrão

**Por padrão**, ao programar com inteligência artificial:
- ✅ **Nomes de variáveis**: Devem estar em **português**
- ✅ **Comentários**: Devem estar em **português**
- ✅ **Docstrings**: Devem estar em **português**

**Justificativa**: Facilita a compreensão e manutenção do código para desenvolvedores que falam português como língua nativa, mantendo consistência com a documentação e comunicação do projeto.

### 🤔 Pergunta Obrigatória na Primeira Sessão

**A IA DEVE perguntar ao programador no primeiro momento (ou durante a primeira sessão)**:

```
❓ Preferências de Idioma para o Código

Para manter consistência no projeto, preciso definir o idioma padrão 
para nomes de variáveis e comentários no código:

💡 Sugestão: Português (recomendado para projetos nacionais)

Opções:
A) 🇧🇷 Português - Variáveis e comentários em português (PADRÃO)
B) 🇺🇸 Inglês - Variáveis e comentários em inglês
C) 🌍 Misto - Variáveis em inglês, comentários em português
D) ⚙️ Personalizado - Especificar preferência customizada

Qual sua preferência?
```

### ✅ Opções Disponíveis

#### Opção A: 🇧🇷 Português (PADRÃO RECOMENDADO)
```python
# ✅ Exemplo em Português
def calcular_preco_total(itens: List[Item]) -> float:
    """
    Calcula o preço total de uma lista de itens.
    
    Args:
        itens: Lista de itens a serem somados
        
    Returns:
        Preço total com impostos incluídos
    """
    preco_subtotal = sum(item.preco for item in itens)
    taxa_imposto = 0.15
    preco_final = preco_subtotal * (1 + taxa_imposto)
    return preco_final
```

#### Opção B: 🇺🇸 Inglês
```python
# ✅ Exemplo em Inglês
def calculate_total_price(items: List[Item]) -> float:
    """
    Calculates the total price of a list of items.
    
    Args:
        items: List of items to be summed
        
    Returns:
        Total price with taxes included
    """
    subtotal_price = sum(item.price for item in items)
    tax_rate = 0.15
    final_price = subtotal_price * (1 + tax_rate)
    return final_price
```

#### Opção C: 🌍 Misto (Variáveis em Inglês, Comentários em Português)
```python
# ✅ Exemplo Misto
def calculate_total_price(items: List[Item]) -> float:
    """
    Calcula o preço total de uma lista de itens.
    
    Args:
        items: Lista de itens a serem somados
        
    Returns:
        Preço total com impostos incluídos
    """
    subtotal_price = sum(item.price for item in items)
    tax_rate = 0.15  # Taxa de imposto de 15%
    final_price = subtotal_price * (1 + tax_rate)
    return final_price
```

### 📝 Registrar a Preferência

Após a resposta do programador, a IA deve:

1. **Registrar a preferência** em um local visível (ex: README.md, CONTRIBUTING.md)
2. **Aplicar consistentemente** em todo o código gerado
3. **Lembrar da preferência** em sessões futuras do mesmo projeto

**Exemplo de Registro no README.md**:
```markdown
## 🌐 Convenções de Código

- **Idioma do Código**: Português
- **Variáveis**: Nomes em português (ex: `usuario_ativo`, `calcular_total`)
- **Comentários**: Em português
- **Documentação**: Em português
```

### 🔄 Alteração de Preferência

O programador pode solicitar mudança de idioma a qualquer momento:
- ✅ "Mude para inglês a partir de agora"
- ✅ "Prefiro comentários em português, mas variáveis em inglês"
- ✅ "Use inglês apenas para APIs públicas"

**A IA deve confirmar a mudança** e atualizar a documentação de convenções.

### ⚠️ Exceções Comuns

Independente da escolha do idioma, **mantenha em inglês**:
- ✅ Nomes de bibliotecas e frameworks (ex: `import pandas`, `from flask import`)
- ✅ Palavras-chave da linguagem (ex: `def`, `class`, `if`, `for`)
- ✅ Nomes de APIs públicas (se o código for distribuído internacionalmente)
- ✅ Termos técnicos sem tradução adequada (ex: `callback`, `payload`, `refactoring`)

### 🎯 Rationale

**Por quê perguntar ao programador?**

1. **Contexto do Projeto**: Projetos nacionais vs. internacionais têm necessidades diferentes
2. **Equipe**: Time brasileiro pode preferir português; time internacional precisa inglês
3. **Legibilidade**: Código é lido mais vezes do que escrito - deve ser claro para quem mantém
4. **Consistência**: Definir padrão no início evita mistura confusa de idiomas
5. **Profissionalismo**: Demonstra atenção aos detalhes e respeito pelas preferências do desenvolvedor

**Por quê Português como padrão?**

Para projetos brasileiros/portugueses:
- ✅ Desenvolvedores leem e entendem mais rápido
- ✅ Facilita onboarding de novos membros do time
- ✅ Documentação e código no mesmo idioma = menos tradução mental
- ✅ Variáveis representam conceitos de negócio em português

**Quando preferir Inglês?**

- 🌍 Projeto open-source internacional
- 🌍 Equipe multicultural
- 🌍 Produto voltado para mercado global
- 🌍 Biblioteca/framework para distribuição pública

---

## 📧 Meios de Contato para Feedback do Usuário

> **IMPORTANTE PARA IAs**: Durante a primeira sessão de interação com o programador, a inteligência artificial deve perguntar se o desenvolvedor gostaria de incluir meios de contato no projeto para que os usuários possam fornecer feedback aos responsáveis.

### 📋 Contexto e Propósito

Projetos de software se beneficiam enormemente de feedback direto dos usuários. Comentários, sugestões, críticas, reclamações, elogios e opiniões são fundamentais para a evolução e melhoria contínua do projeto.

### 🤔 Pergunta Obrigatória na Primeira Sessão

**A IA DEVE perguntar ao programador no primeiro momento (ou durante a primeira sessão)**:

```
❓ Meios de Contato para Feedback do Usuário

Gostaria de incluir meios de contato no projeto para que os usuários
possam enviar feedback (comentários, sugestões, críticas, reclamações,
elogios e opiniões)?

💡 Sugestão: Sim (recomendado para projetos com usuários finais)

Opções:
A) ✅ Sim, incluir GitHub Issues (PADRÃO RECOMENDADO para projetos versionados)
B) ✅ Sim, incluir email para feedback (alternativa ou complemento)
C) ✅ Sim, incluir formulário de contato na aplicação
D) ✅ Sim, incluir múltiplos canais (email + issues + formulário)
E) ❌ Não, não incluir meios de contato

Qual sua preferência?
```

### ✅ Opções Disponíveis

#### Opção A: ✅ Email para Feedback (PADRÃO RECOMENDADO)

**O que incluir**:
- Email de contato dedicado para feedback
- Todos os tipos de feedback são bem-vindos:
  - 💬 Comentários gerais
  - 💡 Sugestões de melhorias
  - 🐛 Críticas construtivas
  - 😞 Reclamações sobre problemas
  - 🎉 Elogios e reconhecimento
  - 📝 Opiniões sobre funcionalidades

**Onde documentar**:
```markdown
## 📧 Feedback e Contato

Sua opinião é muito importante para nós! Envie seus comentários, 
sugestões, críticas, reclamações, elogios e opiniões para:

**Email**: feedback@seuprojeto.com

Todos os feedbacks são lidos e considerados para melhorias futuras.
```

**Exemplo de implementação (README.md)**:
```markdown
## 📮 Feedback

Adoraríamos ouvir sua opinião! Envie seus comentários, sugestões, 
críticas, reclamações, elogios e opiniões para:

- **Email**: contato@meuprojeto.com.br
- **Resposta**: Normalmente respondemos em até 48 horas

Seu feedback nos ajuda a melhorar continuamente!
```

#### Opção B: ✅ GitHub Issues

**Para projetos open-source**:
```markdown
## 🐛 Reportar Problemas ou Dar Feedback

Use as [GitHub Issues](https://github.com/seu-usuario/seu-projeto/issues) para:

- 🐛 Reportar bugs
- 💡 Sugerir novas funcionalidades
- 💬 Compartilhar feedback geral
- ❓ Fazer perguntas

**Templates disponíveis**:
- Bug Report
- Feature Request  
- Feedback Geral
```

#### Opção C: ✅ Formulário de Contato na Aplicação

**Para aplicações web/desktop**:
- Adicionar seção "Feedback" ou "Contato" na interface
- Formulário com campos:
  - Nome (opcional)
  - Email (para resposta)
  - Tipo: Comentário | Sugestão | Crítica | Reclamação | Elogio | Opinião
  - Mensagem
- Envio via email ou salvo em banco de dados

**Exemplo de implementação (GUI)**:
```python
# Menu: Help → Send Feedback
class FeedbackDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enviar Feedback")
        
        # Tipo de feedback
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems([
            "💬 Comentário",
            "💡 Sugestão",
            "🐛 Crítica/Bug",
            "😞 Reclamação",
            "🎉 Elogio",
            "📝 Opinião"
        ])
        
        # Email (opcional)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu@email.com (opcional)")
        
        # Mensagem
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText(
            "Compartilhe seus comentários, sugestões, críticas, "
            "reclamações, elogios ou opiniões..."
        )
        
        # Botão enviar
        self.send_button = QPushButton("Enviar Feedback")
        self.send_button.clicked.connect(self.send_feedback)
```

#### Opção D: ✅ Múltiplos Canais

**Combinar várias opções**:
```markdown
## 📞 Entre em Contato

Valorizamos seu feedback! Você pode nos contatar por:

### 📧 Email
- **Feedback Geral**: feedback@projeto.com
- **Suporte Técnico**: suporte@projeto.com
- Respondemos em até 48 horas

### 💬 GitHub Issues
- Reportar bugs: [Issues](https://github.com/user/projeto/issues)
- Sugerir funcionalidades: [Discussions](https://github.com/user/projeto/discussions)

### 🌐 Formulário de Contato
- Acesse: Menu → Ajuda → Enviar Feedback
- Ou: https://projeto.com/contato

### 📱 Redes Sociais
- Twitter: [@seuprojeto](https://twitter.com/seuprojeto)
- Discord: [Comunidade](https://discord.gg/seuprojeto)
```

#### Opção E: ❌ Não Incluir

**Quando escolher esta opção**:
- ⚠️ Projetos pessoais/internos sem usuários externos
- ⚠️ Protótipos descartáveis
- ⚠️ Scripts de uso único

**Consequência**: Usuários não terão canal direto para feedback, o que pode limitar a evolução do projeto.

### 📝 Registrar a Preferência

Após a resposta do programador, a IA deve:

1. **Adicionar seção de contato/feedback** no README.md
2. **Criar arquivo CONTATO.md** (se necessário) com detalhes
3. **Implementar formulário** (se aplicação com interface)
4. **Documentar** em CONTRIBUTING.md (para projetos open-source)

**Exemplo de registro (README.md)**:
```markdown
## 📬 Feedback e Contato

Este projeto valoriza feedback dos usuários! 

- **Email**: feedback@projeto.com
- **Tipos de feedback bem-vindos**: Comentários, sugestões, críticas, 
  reclamações, elogios e opiniões
- **Tempo de resposta**: Até 48 horas úteis

Seu feedback é essencial para melhorarmos continuamente!
```

### 🎯 Rationale

**Por quê perguntar sobre meios de contato?**

1. **Melhoria Contínua**: Feedback direto ajuda a identificar problemas e oportunidades
2. **Engajamento**: Usuários que podem dar feedback se sentem mais conectados ao projeto
3. **Qualidade**: Críticas e sugestões melhoram a qualidade do software
4. **Priorização**: Feedback ajuda a entender o que é mais importante para os usuários
5. **Reconhecimento**: Elogios motivam a equipe de desenvolvimento
6. **Transparência**: Canal aberto demonstra compromisso com os usuários

**Por quê Email como padrão?**

Para projetos com usuários:
- ✅ **Universal**: Todo mundo tem email
- ✅ **Simples**: Não requer conta ou cadastro adicional
- ✅ **Direto**: Comunicação privada e pessoal
- ✅ **Consolidado**: Todos os tipos de feedback em um único canal
- ✅ **Rastreável**: Histórico completo de comunicações
- ✅ **Profissional**: Canal formal e adequado para qualquer tipo de feedback

**Quando preferir outras opções?**

- 🌍 **GitHub Issues**: Projetos open-source (transparência pública)
- 🌍 **Formulário**: Apps com muitos usuários (organização e categorização)
- 🌍 **Múltiplos canais**: Projetos grandes (diferentes públicos, diferentes necessidades)
- 🌍 **Nenhum**: Projetos internos/pessoais sem usuários externos

### ⚠️ Considerações Importantes

**Gestão de Feedback**:
- ✅ Definir quem responderá aos feedbacks (responsável)
- ✅ Estabelecer tempo de resposta esperado (SLA)
- ✅ Criar processo para triagem e priorização
- ✅ Documentar feedbacks relevantes (issues, backlog)
- ✅ Agradecer sempre, mesmo para críticas

**Privacidade**:
- ✅ Informar como dados de contato serão usados
- ✅ Não compartilhar emails sem permissão
- ✅ Conformidade com LGPD/GDPR se aplicável

**Exemplo de boas práticas**:
```markdown
## 📧 Política de Feedback

**Comprometemos-nos a**:
- ✅ Responder todos os feedbacks em até 48 horas úteis
- ✅ Tratar todas as opiniões com respeito
- ✅ Considerar seriamente críticas e sugestões
- ✅ Manter privacidade dos dados de contato (LGPD)
- ✅ Agradecer contribuições construtivas

**Você pode esperar**:
- Resposta personalizada (não automática)
- Atualizações sobre sugestões implementadas
- Reconhecimento em changelogs (se desejar)
```

---

## 📊 Divisão Recursiva de Tarefas Complexas

> **IMPORTANTE**: Se a tarefa for muito longa ou complexa, e houver limites de tempo ou comprimento de resposta, a inteligência artificial deve dividir a tarefa em partes menores, recursivamente, até conseguir uma tarefa que possa fornecer uma resposta satisfatória e de acordo com o limite de resposta determinado.

### 🔄 Estratégia de Divisão (Solo Developer)

**Quando Aplicar** (Protocolo Simplicidade 3):
- ✅ Tarefa estimada em >4 horas (divide em 2-3 sprints)
- ✅ Feature crítica para produção
- ✅ Resposta muito longa (>1000 linhas de código)
- ✅ Múltiplas funcionalidades interdependentes
- ✅ Requer security checklist + CI/CD + rollback plan
- ✅ Risco de timeout ou limite de resposta
- ✅ **Solo**: Você precisa pausar e continuar depois (contexto)

**Como Dividir** (Recursivamente com Pragmatismo):

1. **Nível 1 - Features Deployáveis (3-4 horas cada)**:
   ```
   Feature Grande: "Sistema de Notificações em Tempo Real"
   ↓ Dividir em (solo, produção):
   ├── Sprint 1: WebSocket server básico (4h)
   │   ├── Security: Rate limiting
   │   ├── CI/CD: Connection tests
   │   └── Rollback: Feature flag
   ├── Sprint 2: Client subscription (3h)
   │   ├── Security: Token validation
   │   └── CI/CD: Integration tests
   └── Sprint 3: Persistência de notificações (3h)
       ├── Security: Data sanitization
       ├── CI/CD: Database tests
       └── Rollback: Database migration
   
   Cada sprint → Deployável em produção
   Cada sprint → Rollback plan se crítico
   ```

2. **Nível 2 - Tasks Testáveis (<3 horas)**:
   ```
   Sprint 1: WebSocket server básico
   ↓ Dividir em:
   ├── Task 1.1: Setup WebSocket library (30min)
   │   └── Security: Check vulnerabilities (pip-audit)
   ├── Task 1.2: Connection handler (1h)
   │   └── Security: Auth token validation
   ├── Task 1.3: Rate limiting (1h)
   │   └── Security: Prevent DDoS
   ├── Task 1.4: Testes + CI/CD (1h)
   └── Task 1.5: Deploy + monitoring (30min)
       └── Rollback: Feature flag WEBSOCKET_ENABLED
   ```

3. **Nível 3 - Subtasks (<1 hora)** (raramente necessário):
   ```
   Task 1.2: Connection handler
   ↓ Dividir em (se muito complexo):
   ├── Subtask 1.2.1: Accept connection (20min)
   ├── Subtask 1.2.2: Validate token (20min)
   └── Subtask 1.2.3: Store connection (20min)
   ```

**Critério de Parada Solo**:
- ⏱️ Tarefa pode ser completada em <3 horas
- 📝 Resposta cabe em limite razoável (<500 linhas)
- ✅ Escopo claro e bem definido
- 🧪 Pode ser testada isoladamente
- 🔒 Security checklist aplicável (10-15min)
- 🤖 CI/CD valida automaticamente
- 🔄 Rollback plan simples (se crítico)
- 💾 **Contexto recuperável**: Se parar, pode continuar depois

**Princípios de Divisão Solo**:
1. **Independência**: Cada subtarefa deve ser deployável sozinha
2. **Contexto**: Cada subtarefa deve ter contexto autoexplicativo
3. **Valor Incremental**: Cada subtarefa deve funcionar em produção
4. **Testabilidade**: Cada subtarefa deve ter testes automatizados
5. **Segurança**: Cada subtarefa deve passar security checklist
6. **Automação**: CI/CD valida tudo (você não esquece nada)
7. **Reversibilidade**: Features críticas têm rollback (você está sozinho)

**Exemplo Prático Solo em Produção**:
```markdown
❌ RUIM - Feature muito grande (12h):
[ ] Implementar sistema completo de billing

✅ BOM - Dividido para solo developer:

Sprint 1 (4h) - Estrutura base (não-crítico):
├── Task 1.1: Modelo de Invoice (1h)
│   └── CI/CD: Schema tests
├── Task 1.2: CRUD básico (2h)
│   ├── Security: Access control
│   └── CI/CD: Unit tests
└── Task 1.3: Documentação + deploy (1h)
    └── Rollback: N/A (não afeta usuários)

Sprint 2 (4h) - Integração Stripe (CRÍTICO):
├── Task 2.1: Setup Stripe API (1h)
│   ├── Security: API keys em env vars
│   └── CI/CD: Connection test
├── Task 2.2: Create payment intent (2h)
│   ├── Security: Amount validation, idempotency
│   └── CI/CD: Mock Stripe tests
└── Task 2.3: Deploy + rollback plan (1h)
    └── Rollback: FEATURE_STRIPE_ENABLED=false
    └── Monitoring: Alert se >5% erro

Sprint 3 (3h) - Webhooks (CRÍTICO):
├── Task 3.1: Webhook receiver (1.5h)
│   ├── Security: Signature validation (OWASP)
│   └── CI/CD: Webhook tests
├── Task 3.2: Event processing (1h)
│   └── Security: Idempotency check
└── Task 3.3: Deploy + monitoring (30min)
    └── Rollback: Desabilitar webhook endpoint

Cada Sprint:
- Security checklist (15min)
- CI/CD automático (GitHub Actions)
- Rollback plan se crítico
- Deploy em produção
- **Você sozinho pode completar**
```

**Quando Dividir vs Quando Simplificar**:

```markdown
Se tarefa é muito grande para dividir eficientemente:

❌ RUIM - Dividir demais:
[ ] Task: Adicionar botão "Salvar"
    ├── Subtask 1: Criar botão (10min)
    ├── Subtask 2: Adicionar evento (10min)
    └── Subtask 3: Testar (10min)
→ Overhead de divisão > benefício

✅ BOM - Tarefa atômica (30min total):
[ ] Task: Adicionar botão "Salvar" com handler

Regra prática:
- Tarefa <1h → Não dividir (atômica)
- Tarefa 1-3h → Avaliar (dividir se >3 componentes)
- Tarefa >3h → Sempre dividir
```

**Matriz de Decisão para Solo** (quando há múltiplas formas de dividir):

| Divisão | Solo-friendly | Deploy | Rollback | Contexto | **Score** |
|---------|---------------|--------|----------|----------|-----------|
| **Por feature deployável** | 5 | 5 | 5 | 4 | **33** 🟢 |
| Por camada (backend/frontend) | 3 | 2 | 2 | 3 | **17** 🟡 |
| Por prioridade (MVP → Nice-to-have) | 5 | 5 | 4 | 5 | **34** 🟢 |

**Por quê?**: Dividir tarefas para solo developer garante entregas incrementais com segurança, facilita retomar contexto, permite rollback rápido (você está sozinho em emergência), e mantém código deployável sempre.

---

## 📋 Espinha Dorsal do Protocolo (17 Etapas Obrigatórias)

**Resumo Executivo** (⭐ = NOVO vs Simplicidade 1):
1. 📚 Ler a documentação
   - 1.5 🔍 **Pesquisar tecnologias adequadas ao projeto** (OBRIGATÓRIO NO INÍCIO)
2. ✅ Escolher tarefas mais simples
   - 2.5 📊 [OPCIONAL] Matriz de Decisão (quando 10+ tasks)
3. ❓ Fazer perguntas até sanar 100% das dúvidas
4. 🔍 Analisar e estudar o projeto
5. 🎯 Fazer sprints das tarefas mais simples
6. 💻 Implementar com arquitetura profissional (GoF + GRASP)
   - 6.5 🔒 ⭐ **Security Checklist OWASP** (OBRIGATÓRIO)
   - 6.6 🎨 **Ícones do Projeto** (OBRIGATÓRIO)
7. ⌨️ Verificar Implementação CLI + Revisão de Código (9 critérios)
8. 🖥️ Verificar Implementação GUI + Revisão de Código (9 critérios)
9. 🔗 Verificar Integração com Programa Principal
🔟 🧪 Fazer testes (100% cobertura)
   - 10.5 ⚡ [OPCIONAL] Profiling e Otimização (se >1s)
   - 10.6 🤖 ⭐ **CI/CD Quality Gates** (OBRIGATÓRIO)
1️⃣1️⃣ 🧹 Organizar pasta raiz
   - 11.5 📝 [OPCIONAL] Notas de Decisão (ADR simplificado)
1️⃣2️⃣ 📝 Preencher documentação
   - 12.5 🔄 ⭐ **Rollback Plans** (OBRIGATÓRIO)
1️⃣3️⃣ 🚀 Fazer commit e push

**Total**: 14 base + 3 obrigatórias novas ⭐ + 3 opcionais = **17-20 etapas**

### 1️⃣ **Ler a Documentação**

> **🚨 CRÍTICO PARA IAs - PRIMEIRA AÇÃO OBRIGATÓRIA**: Antes de QUALQUER coisa, a IA **DEVE** procurar e ler **100% da documentação markdown local** existente no projeto.

#### 📖 **Etapa 1.0: Busca e Leitura Completa de Documentação** [PRIORITÁRIO]

**ANTES de começar qualquer tarefa**, a IA deve:

**Passo 1: Procurar por toda documentação markdown**

Buscar recursivamente por todos os arquivos `.md` no workspace:
```bash
find . -name "*.md" -type f | grep -v node_modules | grep -v venv
```

**Passo 2: Ler 100% do conteúdo encontrado**

A IA **DEVE LER COMPLETAMENTE**:
- ✅ `README.md` - Visão geral
- ✅ `TASKS.md` - Tarefas pendentes e concluídas
- ✅ `docs/REQUIREMENTS.md` - Requisitos
- ✅ `docs/ARCHITECTURE.md` - Stack e decisões técnicas
- ✅ `docs/vX.Y.Z-SPECIFICATIONS.md` - Especificações de versões
- ✅ `docs/CHANGELOG.md` - Histórico de mudanças
- ✅ `docs/plans/*.md` - Planos de ação
- ✅ `docs/security/OWASP-checklist.md` - **Checklist de segurança (crítico)**
- ✅ `docs/rollback/*.md` - **Planos de rollback (crítico)**
- ✅ **Qualquer outro arquivo `.md`**

**[ESPECÍFICO PARA SIMPLICIDADE 3 - SOLO]**:
- ✅ **Notas de Decisão**: Entender por quê você (desenvolvedor) escolheu X ao invés de Y
- ✅ **Planos de Rollback**: Como reverter mudanças se algo der errado
- ✅ **Security Checklist**: OWASP é obrigatório - ler antes de qualquer implementação

**Passo 3: Se NÃO encontrar documentação, perguntar**

```markdown
❓ **Documentação do Projeto**

Procurei por documentação markdown mas não encontrei arquivos `.md`.

**Você tem documentação do projeto?**
A) Sim, está em [localização específica]
B) Sim, mas em formato diferente (.txt, etc.)
C) Não, ainda não existe

**Se C (não existe):**
Vou criar estrutura mínima para solo developer em produção:

1. **Requisitos**:
   - Objetivo do projeto?
   - Funcionalidades principais?
   - Usuários/clientes?

2. **Contexto Técnico**:
   - Stack já definido?
   - Código existente?
   - Escala esperada?

Com essas informações, criarei:
- `README.md` (visão geral)
- `docs/REQUIREMENTS.md` (requisitos)
- `docs/TASKS.md` (tarefas)
- `docs/ARCHITECTURE.md` (decisões técnicas)
- `docs/security/OWASP-checklist.md` (segurança obrigatória)
```

**Passo 4: Criar estrutura solo em produção**

**Estrutura Mínima Obrigatória (Solo em Produção)**:
```
📁 Raiz do Projeto
├── README.md                    # Visão geral
├── TASKS.md                     # Tarefas
└── 📁 docs/
    ├── REQUIREMENTS.md          # Requisitos
    ├── ARCHITECTURE.md          # Stack e decisões
    ├── v0.1.0-SPECIFICATIONS.md # Primeira spec
    ├── 📁 security/             # OBRIGATÓRIO
    │   └── OWASP-checklist.md   # Checklist OWASP Top 10
    └── 📁 rollback/             # OBRIGATÓRIO
        └── rollback-template.md # Template de plano
```

**Template de README.md (Solo em Produção)**:
```markdown
# [Nome do Projeto]

**Versão**: 0.1.0  
**Status**: Em desenvolvimento  
**Developer**: [Seu nome]  
**Início**: [Data]

## 📋 Descrição

[Objetivo do projeto]

## 🚀 Produção

**Deploy**: [Onde está deployado]  
**Usuários**: [Quantos usuários ativos]  
**Uptime**: [SLA esperado]

## 🛠️ Stack Tecnológico

**Linguagem**: [Linguagem + versão LTS]  
**Framework**: [Framework + versão]  
**BD**: [Banco de dados]  
**Deploy**: [Plataforma]

**Por quê esta stack?** Ver [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 🔐 Segurança

- Checklist OWASP: [Ver](docs/security/OWASP-checklist.md)
- CI/CD Quality Gates: [Status]

## 🔄 Rollback

Em caso de problema, ver [planos de rollback](docs/rollback/)

## 📚 Documentação

- [REQUIREMENTS.md](docs/REQUIREMENTS.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [TASKS.md](TASKS.md)

## 🚨 Contato de Emergência

**Email**: [seu email]  
**Tempo de resposta**: [ex: 24h]
```

**Template de docs/security/OWASP-checklist.md**:
```markdown
# Checklist OWASP Top 10 - [Projeto]

**OBRIGATÓRIO**: Verificar ANTES de cada deploy.

## A01:2021 – Broken Access Control
- [ ] Autenticação implementada em todas as rotas sensíveis
- [ ] Autorização validada (usuário só acessa seus dados)
- [ ] CORS configurado corretamente

## A02:2021 – Cryptographic Failures
- [ ] Senhas hasheadas (bcrypt, Argon2)
- [ ] HTTPS em produção
- [ ] Tokens seguros (JWT com expiração)

## A03:2021 – Injection
- [ ] SQL: Queries parametrizadas (sem concatenação)
- [ ] Input sanitizado
- [ ] XSS prevenido (escape de HTML)

[... restante do OWASP Top 10 ...]
```

**Passo 5: Documentar continuamente (Solo)**

**Durante desenvolvimento**:
- ✅ **Atualizar TASKS.md**: Progresso diário
- ✅ **Criar SPECIFICATIONS.md**: Cada versão deployada
- ✅ **Atualizar OWASP-checklist.md**: ANTES de cada deploy
- ✅ **Criar Rollback Plans**: Para cada feature crítica
- ✅ **Comentar código**: Explicar "por quê" suas decisões

**Comentários úteis (Solo)**:
```python
# DECISÃO SOLO: Cache em memória ao invés de Redis
# Razão: Não preciso complexidade de Redis neste momento
# TODO: Migrar para Redis se escala passar de 10k usuários
# Tempo estimado: 2h, criar rollback plan antes
cache = {}
```

#### 📋 Checklist (Para IAs - Solo)

```markdown
[ ] 🔍 Busquei todos arquivos .md
[ ] 📖 Li 100% do conteúdo encontrado
[ ] 🔐 Li checklist OWASP (se existe)
[ ] 🔄 Li planos de rollback existentes
[ ] 📝 Se não há docs, perguntei e criei estrutura
[ ] 🎯 Entendi objetivo e contexto completo
[ ] 📋 Sei tarefas pendentes e concluídas
[ ] 🛠️ Conheço stack e por quê foi escolhido
[ ] 🏗️ Entendi decisões técnicas anteriores
[ ] ✅ Pronto para trabalhar com contexto completo
```

#### 🚀 Rationale (Solo em Produção)

**Por quê ler 100% é CRÍTICO para solo developer?**

1. ✅ **Você é Único Mantenedor**: Contexto é sua memória externa
2. ✅ **Sem Equipe para Perguntar**: Documentação é seu colega de equipe
3. ✅ **Produção Crítica**: Bugs afetam usuários reais - contexto evita erros
4. ✅ **Decisões Futuras**: Entender por quê você escolheu X meses atrás
5. ✅ **Onboarding Futuro**: Se contratar alguém, documentação é essencial
6. ✅ **Continuidade**: Se ficar doente/férias, alguém pode assumir

**Mensagem para IAs (Solo)**:
> "Para solo developers, documentação é CRÍTICA. Você não tem equipe para consultar. Ler 100% da documentação existente ANTES de codificar evita reintroduzir bugs já corrigidos ou quebrar decisões arquiteturais que você mesmo fez meses atrás. Documente para o 'você do futuro'."

**Regra de Ouro (Solo)**:
> **"Documente como se você fosse ser atropelado por um ônibus amanhã. Alguém precisa conseguir manter seu código."**

---

**Após completar a leitura**, prosseguir para:
- Consultar `TASKS.md` (ou arquivo equivalente definido pelo usuário) para ver as tarefas pendentes
- Consultar `docs/REQUIREMENTS.md` para entender o contexto do projeto
- Revisar especificações anteriores (`v2.9.X-SPECIFICATIONS.md`)
- Entender dependências e arquitetura existente
- Verificar exemplos em `tests/files/` quando aplicável

**📋 Sobre o Arquivo de Tarefas**:

O arquivo `TASKS.md` é o **arquivo padrão** para gerenciar tarefas do projeto, mas você pode usar qualquer arquivo no formato ASCII (`.txt`, `.md`, etc.) conforme sua preferência.

**Requisitos do Arquivo de Tarefas**:
- ✅ **Formato ASCII obrigatório**: `.md`, `.txt` ou similar (legível como texto plano)
- ❌ **NÃO aceito**: `.docx`, `.pdf`, ou formatos binários
- 📍 **Localização**: Raiz do projeto ou em `docs/` (ex: `TASKS.md`, `TODO.md`, `requirements.md`)
- 🔄 **Alternativo**: Se preferir outro nome/localização, especifique no início do projeto

**Se não existir arquivo de tarefas**:
1. A IA deve perguntar ao usuário: "Qual arquivo você usa para gerenciar tarefas?" 
2. Se não houver, sugerir criação do `TASKS.md` padrão
3. Confirmar localização e nome do arquivo com o usuário

**Por quê?**: Evitar retrabalho e garantir coerência com o código existente. O arquivo de tarefas centraliza o planejamento e progresso do projeto.

**📋 Sobre Planos de Ação**:

Além do `TASKS.md`, você pode criar **Planos de Ação** para tarefas que requerem guia passo a passo detalhado.

**O que são Planos de Ação?**
- 🎯 **Roteiros práticos** com passos intermediários numerados para tarefas complexas
- ⚡ **Mais urgente e detalhado** que items do TASKS.md
- 🔧 **Aplicável a**: Manutenção, Correção, Evolução, Adaptação
- 📋 **Criados ANTES** de iniciar a implementação
- 📖 **Consultados sempre** durante o desenvolvimento

**Diferença entre TASKS.md e Planos de Ação:**
- **TASKS.md**: Lista de tarefas gerais ("O QUE fazer") - ex: `[ ] Implementar autenticação OAuth2`
- **Plano de Ação**: Guia detalhado de execução ("COMO fazer") - ex:
  ```
  PLANO #01: Implementar OAuth2
  ├─ Passo 1: Instalar biblioteca passport.js
  ├─ Passo 2: Configurar estratégia Google OAuth
  ├─ Passo 3: Criar rotas /auth/google
  └─ Passo 4: Adicionar testes
  ```

**Quando usar Planos de Ação:**
- ✅ Tarefa complexa com múltiplas etapas interdependentes
- ✅ Bug crítico que requer diagnóstico passo a passo
- ✅ Refatoração que afeta múltiplos módulos
- ✅ Migração de tecnologia ou atualização de framework

**Especificidades para Simplicidade 3 (Solo Developer em Produção):**
- 🔒 **Segurança obrigatória**: Incluir análise OWASP para cada passo que toque código sensível
- 🔙 **Rollback Plan**: Cada plano de ação deve incluir estratégia de reversão (ver Etapa 12.5)
- ⚡ **Automation-first**: Priorizar passos que podem ser automatizados/testados
- 📊 **Métricas de produção**: Incluir validação de métricas (performance, disponibilidade)

**Organização dos Planos de Ação:**

**Opção 1**: Arquivo consolidado `docs/ACTION_PLANS.md`  
**Opção 2**: Diretório de planos individuais `docs/plans/`
```
docs/
├── TASKS.md
├── ACTION_PLANS.md [opcional - índice]
└── plans/
    ├── plan-001-oauth2.md
    ├── plan-002-migration.md
    └── plan-003-refactoring.md
```

**Recomendação**: Para solo developer em produção com múltiplas tarefas críticas, use `docs/plans/` para melhor organização e rastreabilidade.

**Campos Obrigatórios de um Plano de Ação:**
1. **📅 Data** (YYYY-MM-DD): Data de criação do plano
2. **🕐 Horário** (HH:MM): Horário de criação
3. **🎯 Função Principal**: Objetivo principal do plano
4. **📋 Requisito Desejado**: O que precisa ser alcançado
5. **✅ Resultado Esperado**: Critérios de sucesso mensuráveis
6. **📌 ID da Tarefa**: Vínculo com Task do TASKS.md (obrigatório)

**Template para Simplicidade 3 (Solo em Produção):**
```markdown
## 🎯 PLANO DE AÇÃO #[ID]: [Título]
**📅 Data**: YYYY-MM-DD
**🕐 Horário**: HH:MM
**⚡ Prioridade**: 🔴 Crítica | 🟡 Alta | 🟢 Normal
**🏷️ Tipo**: Manutenção | Correção | Evolução | Adaptação
**📌 ID da Tarefa**: Task #X do TASKS.md
**🎯 Função Principal**: [Objetivo do plano]
**📋 Requisito Desejado**: [O que deve ser alcançado]
**✅ Resultado Esperado**: [Critérios de sucesso]
**🔒 Impacto de Segurança**: Sim | Não
**💰 Impacto em Produção**: Crítico | Moderado | Baixo

### 📝 Contexto
[Por que este plano foi criado? Qual impacto no sistema em produção?]

### 🔙 Rollback Plan (OBRIGATÓRIO)
**Se algo der errado durante a execução:**
- [ ] **Passo de reversão 1**: [Como desfazer passo 1]
- [ ] **Passo de reversão 2**: [Como desfazer passo 2]
- [ ] **Dados afetados**: [Como recuperar/restaurar]
- [ ] **Tempo estimado de rollback**: [duração]

### 📋 Passos Intermediários
- [ ] **Passo 1**: [Descrição]
  - **Critério de conclusão**: [...]
  - **Tempo estimado**: [...]
  - **Checklist de segurança**: 
    - [ ] Validação de entrada
    - [ ] Codificação de saída
    - [ ] Autenticação/Autorização
  - **Testes automatizados**: [comandos]
  - **Rollback**: [como reverter este passo]
  
- [ ] **Passo 2**: [Descrição]
  - **Critério de conclusão**: [...]
  - **Dependências**: Passo 1
  - **Checklist de segurança**: [...]
  - **Validação em staging**: [comandos/URLs]
[...]

### 🔒 Análise de Segurança (OWASP)
- [ ] **A01:2021 – Broken Access Control**: Avaliado
- [ ] **A02:2021 – Cryptographic Failures**: Avaliado
- [ ] **A03:2021 – Injection**: Avaliado
[... outras categorias relevantes ...]

### 📊 Validação de Métricas de Produção
- [ ] **Performance**: Response time < Xms (monitorar por 24h)
- [ ] **Disponibilidade**: Uptime > 99.9%
- [ ] **Erros**: Error rate < 0.1%
- [ ] **Recursos**: CPU/Memória dentro dos limites

### ✅ Critérios de Conclusão
- [ ] Todos passos concluídos
- [ ] Testes automatizados passando (100% cobertura)
- [ ] OWASP checklist validado
- [ ] Documentação atualizada
- [ ] Rollback plan testado
- [ ] Validação em staging por 24h
- [ ] Deploy em produção com monitoramento
- [ ] Métricas de produção estáveis por 48h
```

**Fluxo de trabalho com Planos de Ação (Solo em Produção):**
1. Consultar TASKS.md para ver tarefas pendentes
2. Se tarefa complexa/crítica → **CRIAR Plano de Ação ANTES de começar**
3. Escolher localização: `docs/ACTION_PLANS.md` ou `docs/plans/plan-[ID]-[nome].md`
4. **Análise de segurança**: Aplicar OWASP checklist (Etapa 6.5)
5. **Criar Rollback Plan**: Garantir capacidade de reverter (Etapa 12.5)
6. **ANTES de implementar**: Revisar e validar todo o plano
7. **Executar em staging primeiro**: Validar por 24h mínimo
8. Executar passo a passo, **consultando o plano sempre que necessário**
9. **Deploy incremental**: Um passo por vez, com monitoramento
10. **Validar métricas**: 48h de estabilidade antes de considerar completo
11. Ao concluir → marcar task no TASKS.md como completa
12. Arquivar plano em `docs/plans/archive/` com lições aprendidas

**Por quê criar ANTES e consultar SEMPRE?**
- ✅ **Segurança First**: Análise OWASP antes evita vulnerabilidades
- ✅ **Rollback Preparado**: Ter estratégia de reversão desde o início
- ✅ **Evita Downtime**: Planejamento antecipado identifica riscos
- ✅ **Não se Perder**: Consultar durante o trabalho mantém foco na segurança
- ✅ **Validação Contínua**: Cada passo tem critérios claros de sucesso

**Benefícios para Solo Developer:**
- ✅ **Segurança**: Checklist obrigatório evita vulnerabilidades
- ✅ **Confiabilidade**: Rollback plan garante recuperação rápida
- ✅ **Qualidade**: Passos testáveis garantem funcionamento
- ✅ **Autonomia**: Processo completo documentado para você mesmo
- ✅ **Manutenibilidade**: Histórico detalhado facilita correções futuras

**⚠️ Quando um Plano de Ação é OBRIGATÓRIO em Simplicidade 3:**
- 🔒 Mudanças que afetam **autenticação, autorização ou dados sensíveis**
- 💰 Deploy em **produção com usuários ativos**
- 🗄️ **Migrações de banco de dados** ou mudanças de schema
- 🔄 **Atualizações de dependências críticas** (frameworks, bibliotecas de segurança)
- 🐛 **Bugs críticos** que afetam disponibilidade ou segurança

📖 **Detalhes completos sobre Planos de Ação**: Ver README.md do repositório, seção "🎯 Planos de Ação"

---

### 1️⃣.5️⃣ **Pesquisa de Tecnologias Adequadas ao Projeto** [OBRIGATÓRIO NO INÍCIO]

> **CRÍTICO PARA IAs**: No início do projeto (primeira sessão), a IA **DEVE** investigar e recomendar as tecnologias mais adequadas para o projeto com base nos requisitos fornecidos.

**Nota para Simplicidade 3 (Solo em Produção)**: Esta etapa foca em tecnologias **maduras, bem documentadas e com comunidade ativa** para facilitar manutenção solo de longo prazo.

#### 🎯 Quando Aplicar

**Momento ideal**: Logo após a primeira leitura do `TASKS.md` e `docs/REQUIREMENTS.md`, **antes de começar a implementação**.

**Aplicável a**:
- ✅ Projetos novos (sem código implementado ainda)
- ✅ Projetos em refatoração completa (mudança de stack tecnológico)
- ✅ Projetos em fase de planejamento (arquitetura ainda não definida)

**NÃO aplicável a**:
- ❌ Projetos com stack já definido e implementação em andamento
- ❌ Manutenção de funcionalidades em código existente
- ❌ Correção de bugs em código já produzido

#### 📋 Como Funciona (Solo Developer)

**Passo 1: Coletar Requisitos**

A IA deve solicitar:
- 📌 **Tarefas e funcionalidades desejadas** (podem estar em `docs/TASKS.md`)
- 📌 **Requisitos funcionais e não-funcionais** (podem estar em `docs/REQUIREMENTS.md`)
- 📌 **Tipo de aplicação** (web, desktop, mobile, CLI, API, etc.)
- 📌 **Público-alvo e escala esperada** (pequeno porte, médio porte, crescimento gradual)
- 📌 **Restrições técnicas** (linguagens preferidas, ambiente de deploy)
- 📌 **[Solo]** Experiência do desenvolvedor com tecnologias (evitar curva de aprendizado íngreme)
- 📌 **[Solo]** Capacidade de manutenção (preferir tecnologias simples e bem documentadas)

**Passo 2: Investigar Tecnologias Profissionais (Critérios Solo)**

**Critérios CRÍTICOS para solo developer em produção**:

1. **🛡️ Maturidade e Estabilidade**
   - Tecnologias com **versões estáveis** (evitar bleeding edge)
   - Histórico de **breaking changes mínimos**
   - **LTS (Long Term Support)** disponível

2. **📚 Documentação de Qualidade**
   - Documentação **oficial completa** e atualizada
   - **Exemplos práticos** abundantes
   - **Tutoriais** para casos de uso comuns

3. **👥 Comunidade Ativa**
   - **Stack Overflow** com muitas perguntas/respostas
   - **GitHub** com issues ativos e PRs regulares
   - **Discord/Slack** ou fóruns ativos

4. **🔧 Facilidade de Manutenção**
   - **Setup simples** (evitar configurações complexas)
   - **Debugging fácil** (ferramentas de dev maduras)
   - **Atualização segura** (processo de upgrade bem documentado)

5. **⚡ Performance Production-Ready**
   - Comprovadamente **usado em produção** por empresas
   - **Escalabilidade** adequada ao escopo do projeto
   - **Monitoramento e logging** nativos ou fáceis de adicionar

6. **🔐 Segurança**
   - **CVEs** rapidamente corrigidos
   - **Atualizações de segurança** regulares
   - **Boas práticas** bem documentadas

**Categorias de tecnologias** (mesmas, mas com foco em maturidade):
1. **🎨 Frontend**: React (LTS), Vue 3, Next.js, MUI, Bootstrap
2. **⚙️ Backend**: Django (LTS), FastAPI, Express, NestJS, Spring Boot
3. **🖥️ Desktop**: PyQt6 (LTS), Electron (stable), Qt
4. **📊 Visualização**: Chart.js, Recharts, Plotly
5. **🤖 IA/ML**: scikit-learn (stable), Transformers, OpenAI API (stable)
6. **💾 Banco de Dados**: PostgreSQL (LTS), MySQL (LTS), SQLite
7. **🔐 Autenticação**: OAuth2 (padrão), JWT, bcrypt
8. **🧪 Testes**: pytest, Jest (stable)

#### 🌐 **Stack Padrão Recomendado para Sites/Aplicações Web** [NOVO]

> **IMPORTANTE**: Quando se tratar da implementação de um **site ou aplicação web**, e o desenvolvedor **NÃO especificar** quais tecnologias deseja, a IA **PODE RECOMENDAR** o seguinte stack padrão moderno, maduro e fácil de manter:

**📦 Frontend Framework & Runtime**
- **Next.js 15.5.2** - Framework React com App Router e Server Components
- **React 19.1.1** - Biblioteca de UI
- **React DOM 19.1.1** - Renderização do React no navegador
- **TypeScript 5.9.2** - Superset JavaScript com tipagem estática
- **Node.js 18+ (LTS)** - Runtime JavaScript

**🔧 Bundlers & Build Tools**
- **Turbopack** - Bundler de nova geração do Next.js (700x mais rápido)
- **Turbo (turborepo)** - Sistema de build para monorepos
- **PostCSS 8.5.6** - Processamento de CSS
- **Autoprefixer 10.4.21** - Adiciona prefixos CSS automaticamente

**📊 State Management**
- **Zustand 4.5.7** - Gerenciamento de estado minimalista e eficiente
- **Immer 10.1.3** - Manipulação imutável de estado

**🎨 Styling**
- **Tailwind CSS 3.4.17** - Framework CSS utility-first
- **CSS Modules** - Modularização de CSS
- **clsx 2.1.1** - Utilitário para classes CSS condicionais
- **class-variance-authority 0.7.1** - Gerenciamento de variantes de componentes
- **tailwind-merge 3.3.1** - Merge inteligente de classes Tailwind
- **Lucide React 0.542.0** - Biblioteca de ícones

**🎵 Audio & Media** (se aplicável)
- **Cloudinary 1.41.3** - Processamento e armazenamento de mídia
- **@cloudinary/react 1.14.3** - Componentes React do Cloudinary
- **@cloudinary/url-gen 1.22.0** - Geração de URLs do Cloudinary
- **Web Audio API** - API nativa do navegador para gravação de áudio

**💳 Payments & Subscriptions** (se aplicável)
- **Stripe 14.25.0** - Processamento de pagamentos (backend)
- **@stripe/stripe-js 2.4.0** - SDK JavaScript do Stripe (frontend)

**🌐 HTTP & API**
- **Axios 1.11.0** - Cliente HTTP para requisições à API

**📄 PDF & Screenshots** (se aplicável)
- **jsPDF 3.0.3** - Geração de PDFs
- **html2canvas 1.4.1** - Conversão de HTML para canvas/imagem
- **Puppeteer 24.29.1** - Automação de browser headless

**🧪 Testing**
- **Jest** - Framework de testes
- **jsdom** - Ambiente DOM para testes
- **@testing-library** - Utilitários para testes de componentes React

**✅ Code Quality & Linting**
- **ESLint 8.57.1** - Linter JavaScript/TypeScript
- **eslint-config-next 15.5.2** - Configuração ESLint do Next.js
- **Husky 9.1.7** - Git hooks para qualidade de código

**🛠️ Development Tools**
- **npm 10.9.2** - Gerenciador de pacotes
- **Git** - Controle de versão
- **VS Code** - Editor recomendado

**⚙️ Backend** (Repositório Separado)
- **Node.js** - Runtime backend
- **Express** - Framework web
- **MongoDB** - Banco de dados NoSQL
- **JWT** - Autenticação com tokens
- **Heroku** - Hospedagem do backend

**🚀 Infraestrutura & Deploy**
- **Vercel** - Hospedagem frontend (recomendado para Next.js)
- **Cloudinary CDN** - Entrega de conteúdo de áudio/mídia
- **HTTPS** - Protocolo seguro (requerido para gravação de áudio)

**🤖 APIs de IA** (Opcionais)
- **OpenAI API** - IA para feedback e avaliação
- **GPT-4o-mini** - Modelo específico da OpenAI
- **ElevenLabs API** - Síntese de voz

**🏗️ Build & Development** (Detalhes Adicionais)
- **Webpack** - Bundler alternativo (fallback do Turbopack)
- **JavaScript ES2017+** - Linguagem base
- **Chrome DevTools** - Debug de navegador

**🎨 CSS & Styling Core** (Detalhes Adicionais)
- **CSS Modules** - Sistema de modularização (já mencionado)

**📊 State Management Details** (Detalhes Adicionais)
- **Zustand DevTools** - Ferramentas de debug
- **Zustand Persist Middleware** - Middleware de persistência

**🌐 Browser APIs Nativas**
- **Web Audio API** - API de áudio (gravação e reprodução)
- **MediaRecorder API** - Gravação de áudio
- **Fetch API** - Requisições HTTP nativas
- **Cookies API** - Gerenciamento de cookies
- **LocalStorage API** - Armazenamento local
- **SessionStorage API** - Armazenamento de sessão
- **Navigator API** - Acesso a dispositivos
- **Permissions API** - Gerenciamento de permissões
- **Geolocation API** - Localização do usuário
- **Service Worker API** - Cache e offline (código legacy)

**🔐 Authentication & Security Details**
- **JWT (JSON Web Tokens)** - Especificação do sistema de autenticação
- **bcrypt** - Hash de senhas
- **HTTPS** - Protocolo seguro obrigatório

**🚀 Infrastructure Details**
- **Cloudinary CDN** - Sistema de delivery de mídia
- **GitHub** - Controle de versão
- **Git** - Sistema de versionamento

**⚙️ Backend Details**
- **Express** - Framework web backend
- **Heroku** - Hospedagem do backend
- **MongoDB** - Banco de dados NoSQL

**🧪 Testing Details**
- **@testing-library/jest-dom** - Matchers específicos do Jest
- **@testing-library/react** - Testes de componentes React
- **@testing-library/user-event** - Simulação de eventos de usuário

**✅ Por Quê Este Stack Para Solo Developer?**
- ✅ **Next.js 15**: Framework maduro, documentação excepcional
- ✅ **React 19**: Comunidade massiva, fácil encontrar soluções
- ✅ **TypeScript**: Previne bugs antes de ir para produção
- ✅ **Tailwind CSS**: Produtividade alta, menos CSS manual
- ✅ **Zustand**: Simples de entender e debugar sozinho
- ✅ **Turbopack**: Builds rápidos = menos espera
- ✅ **Vercel Deploy Gratuito**: Hospedagem simples e confiável
- ✅ **Ecossistema Completo**: Uma stack para 90% dos casos

**[ESPECÍFICO PARA SIMPLICIDADE 3 - SOLO]**:
- ✅ **Baixa Manutenção**: Next.js + Vercel = atualizações automáticas
- ✅ **Documentação Excelente**: Menos tempo procurando soluções
- ✅ **Comunidade Massiva**: Stack Overflow tem 100k+ questões React
- ✅ **Deploy Fácil**: `git push` e Vercel faz o resto
- ✅ **Escalável**: Começa grátis, escala conforme crescer
- ✅ **TypeScript Salva Vidas**: Erros de tipo antes de deploy
- ✅ **LTS Node.js 18+**: Suporte de longo prazo (até 2025)

**⏱️ Tempo de Manutenção Estimado (Solo)**:
- Atualizações de dependências: **~2h/mês** (automatizável)
- Monitoramento Vercel: **~10min/dia** (dashboards automáticos)
- Correção de bugs típicos: **~3h/semana** (comunidade ajuda)
- Total: **~15h/mês** de manutenção (sustentável para solo)

**🛡️ Plano de Rollback (Se Não Funcionar)**:
Se após **3 meses** este stack não atender expectativas:
- **Alternativa 1**: Migrar frontend para **Vue 3 + Nuxt** (similar)
- **Alternativa 2**: Simplificar para **React sem Next.js** (menos features)
- **Alternativa 3**: Migrar para **Python + Flask + React** (se prefere Python)
- **Esforço estimado**: 5-10 dias de migração

**Gatilhos de rollback**:
- Performance inadequada (<80 Lighthouse score)
- Complexidade insustentável (>20h/semana manutenção)
- Custos acima de $50/mês (escala não prevista)
- Bugs críticos não resolvidos pela comunidade em 72h

**⚠️ Quando NÃO Usar Este Stack Padrão**:
- ❌ Desenvolvedor especifica **explicitamente** outras tecnologias
- ❌ Desenvolvedor tem **experiência sólida** com Vue/Angular
- ❌ Projeto requer **Python/Django** backend
- ❌ Aplicação **desktop** ou **mobile nativa**
- ❌ Site **estático super simples** (HTML/CSS/JS puro suficiente)
- ❌ Desenvolvedor prefere **"boring technology"** (PHP, Ruby on Rails)

---

**Passo 3: Apresentar Recomendações (Foco Solo)**

Apresentar **2-3 stacks** priorizando:
- ✅ **Maturidade** (versões LTS preferidas)
- ✅ **Documentação** (qualidade e quantidade)
- ✅ **Facilidade de deploy** (Heroku, Vercel, Docker simples)
- ✅ **Comunidade ativa** (suporte rápido quando bloquear)
- ✅ **Curva de aprendizado** (se desenvolvedor não conhece)
- ✅ **Manutenção de longo prazo** (5+ anos)

**Template de recomendação (Solo)**:
```markdown
## 🎯 Stack Recomendada: [Nome da Stack]

### 📦 Tecnologias Principais
[Lista de tecnologias]

### ✅ Por Quê Esta Stack Para Solo Developer?
- **Maturidade**: [Versão, LTS, anos de mercado]
- **Documentação**: [Qualidade, exemplos, tutoriais]
- **Comunidade**: [Stack Overflow, GitHub, Discord]
- **Manutenção**: [Facilidade de atualização, debugging]
- **Deploy**: [Plataformas compatíveis, facilidade]

### 🏢 Casos de Uso Reais (Solo Devs)
- [Projeto 1] - desenvolvido por [Dev Solo X]
- [SaaS 2] - mantido por [Dev Solo Y]

### ⏱️ Tempo de Manutenção Estimado
- Atualizações de segurança: [X horas/mês]
- Bug fixes: [Y horas/semana]
- Monitoramento: [Z minutos/dia]

### 🛡️ Longevidade
- LTS até: [Data]
- Expectativa de suporte comunitário: [Anos]
```

**Passo 4: Validar e Documentar**

**[ESPECÍFICO PARA SIMPLICIDADE 3 - SOLO]**:
- ✅ **Decisão rápida**: Solo developer decide sozinho (sem reuniões)
- ✅ **Documentar em ARCHITECTURE.md**: Justificativa clara
- ✅ **Criar Nota de Decisão**: Documentar **por quê** escolheu (para você no futuro)
- ✅ **Rollback Plan**: Como migrar se stack não funcionar (ver Etapa 15.5)

#### 🌐 Pesquisas Online (Se Necessário)

**Fontes específicas para solo developers**:
- 📚 **GitHub Awesome Lists**: "awesome-[tecnologia]" (curadoria da comunidade)
- 📖 **"Best [tech] for solo developer"**: Pesquisas específicas
- 💬 **Reddit r/solopreneur, r/webdev**: Experiências de outros solos
- 📊 **Indie Hackers**: Stack de projetos solo bem-sucedidos
- 📰 **Dev.to "solo developer"**: Tutoriais e experiências

**O que pesquisar (Solo)**:
- "Best [tipo de app] stack for solo developer 2025"
- "[Tecnologia X] maintenance burden solo"
- "[Framework Y] vs [Framework Z] for small team"
- "Solo developer success stories [tecnologia]"
- "[Stack W] long term maintenance"

#### 📝 Documentar Stack Escolhido (Solo)

**Onde documentar**: `docs/ARCHITECTURE.md` (obrigatório)

**Template (Solo Developer)**:
```markdown
## 🛠️ Stack Tecnológico (Solo Developer em Produção)

**Linguagem Principal**: [Python, JavaScript, etc.]

**Stack**:
- Frontend: [React, etc.] - Versão: [LTS/Stable]
- Backend: [FastAPI, etc.] - Versão: [LTS/Stable]
- Banco de Dados: [PostgreSQL, etc.] - Versão: [LTS]
- Deploy: [Heroku, Vercel, Docker]
[...]

### 🎯 Justificativa da Escolha (Por Quê Escolhi)

**Maturidade**: [Por quê esta versão é estável]
**Documentação**: [Por quê é fácil encontrar soluções]
**Comunidade**: [Por quê consigo suporte rápido]
**Manutenção**: [Por quê consigo manter sozinho]
**Longevidade**: [Por quê vai durar 5+ anos]

### 🛡️ Plano de Rollback (Se Não Funcionar)

Se este stack não atender expectativas após [X meses]:
- **Alternativa 1**: Migrar para [Stack B]
- **Alternativa 2**: Migrar para [Stack C]
- **Esforço estimado**: [Y dias de migração]
- **Gatilhos de rollback**:
  - Performance inadequada (>5s response time)
  - Bugs críticos não resolvidos pela comunidade em 48h
  - Custos de infra >$XXX/mês
  - Complexidade de manutenção >10h/semana

### 📚 Recursos de Aprendizado
- Documentação oficial: [Link]
- Tutorial favorito: [Link]
- Stack Overflow: [Link de tag]
- Discord/Community: [Link]

### 🔄 Histórico de Atualizações
- [Data]: Setup inicial - Versão [X.Y.Z]
- [Data]: Upgrade para [Nova versão] - Tempo gasto: [Horas]
```

#### ✅ Checklist de Pesquisa de Tecnologias (Solo)

```markdown
[ ] Requisitos coletados (funcionalidades, escala, capacidade de manutenção)
[ ] Experiência do desenvolvedor com tecnologias avaliada
[ ] Investigação focada em maturidade e documentação
[ ] Pesquisas específicas para solo developers realizadas
[ ] 2-3 stacks recomendados (priorizando LTS/stable)
[ ] Maturidade e comunidade verificadas
[ ] Facilidade de manutenção avaliada (horas/semana estimadas)
[ ] Facilidade de deploy verificada
[ ] Longevidade analisada (LTS, anos de suporte)
[ ] Stack escolhido e decisão justificada
[ ] Plano de rollback documentado
[ ] Documentado em docs/ARCHITECTURE.md
[ ] Recursos de aprendizado salvos (docs, tutoriais, comunidade)
```

#### 🎯 Rationale (Simplicidade 3 - Solo em Produção)

**Por quê esta etapa é CRÍTICA para solo developers?**

1. ✅ **Você é Único Ponto de Falha**: Stack complexo = risco de não conseguir manter
2. ✅ **Sem Backup de Equipe**: Não tem quem perguntar se travar em bug obscuro
3. ✅ **Tempo é Limitado**: Manutenção deve ser <10h/semana para ser sustentável
4. ✅ **Longo Prazo**: Stack deve funcionar por 5+ anos sem grandes migrações
5. ✅ **Conhecimento Específico**: Tecnologias devem ter documentação e comunidade fortes
6. ✅ **Custo-Benefício**: Stack experimental pode custar meses de retrabalho

**Mensagem para IAs (Solo Developer)**:
> "Para solo developers em produção, PRIORIZE MATURIDADE sobre features. Um framework estável com comunidade ativa é 10x melhor que o mais novo framework com recursos avançados. Lembre-se: o desenvolvedor vai manter isso SOZINHO por ANOS."

**Regra de Ouro (Solo)**:
> **"Stack deve ser BORING (chato). Tecnologias maduras, previsíveis e bem documentadas. Inovação vem das funcionalidades, não do stack."**

📖 **Conceito "Choose Boring Technology"**: Ver artigo clássico de Dan McKinley sobre por quê escolher tecnologias maduras é estratégia vencedora para times pequenos.

---

### 1️⃣.8️⃣ **Planejamento e Organização com Sprints** [OBRIGATÓRIO ANTES DE IMPLEMENTAR]

> **CRÍTICO**: Antes de escrever código, a IA **DEVE** criar plano estruturado, definir sprints curtos, organizar tarefas em TASKS.md.

#### 🎯 Obrigatório para IA (Solo Developer)

A IA DEVE:
1. ✅ Criar/atualizar **docs/TASKS.md** com sprints de 1-3 dias
2. ✅ Quebrar funcionalidades em **tarefas de 1-4h** (máximo)
3. ✅ Documentar **arquitetura simples** em docs/ARCHITECTURE.md
4. ✅ Identificar **bloqueios** antes de começar
5. ✅ Priorizar tarefas por **valor/esforço** (quick wins primeiro)

#### 📋 Estrutura Mínima de TASKS.md (Solo)

```markdown
# Tasks - [Projeto]

**Status**: [Feature atual]
**Sprint Atual**: Sprint N (DD/MM - DD/MM)

## Sprint N: [Objetivo] 

**Meta**: [Entregável testável]

- [ ] Tarefa N.1: [Descrição clara] (Estimativa: 2h, Prioridade: Alta)
- [ ] Tarefa N.2: [Descrição clara] (Estimativa: 1h, Dependência: N.1)

## Backlog

- [ ] Feature futura 1 (Sprint N+1)
- [ ] Feature futura 2 (Sprint N+2)

## Bloqueios

- [ ] Dúvida: [Descrição] - Precisa resposta do desenvolvedor
```

#### 🚀 Específico para Solo (Simplicidade 3)

**Planejamento ágil solo**:
- ✅ **Sprints curtos**: 1-3 dias (não mais que isso)
- ✅ **Tarefas pequenas**: 1-4h por tarefa (foco e progresso visível)
- ✅ **MVP mindset**: Funcionalidade mínima testável por sprint
- ✅ **Documentação JIT** (Just-In-Time): Documentar só o necessário
- ✅ **Sem cerimônias**: Apenas atualizar TASKS.md diariamente

**Análise custo-benefício (Solo)**:
- ⏱️ Tempo para planejar sprint (3 dias): ~30-45 min
- ⏱️ Tempo economizado (evitando retrabalho): ~2-4 horas
- 💰 ROI: 3x-5x (vale MUITO a pena)

**Quick wins primeiro**:
```
Matriz Valor/Esforço:

Alto Valor, Baixo Esforço → SPRINT 1 (Quick Wins) ⭐
Alto Valor, Alto Esforço → SPRINT 2-3 (Planeje bem)
Baixo Valor, Baixo Esforço → BACKLOG (Se sobrar tempo)
Baixo Valor, Alto Esforço → NEVER (Não faça)
```

**Arquitetura simplificada**:
```markdown
## docs/ARCHITECTURE.md (Solo - Mínimo)

### Estrutura
- src/ - Código principal
- tests/ - Testes (quando houver)
- docs/ - Documentação

### Stack
- [Framework principal]: [Por quê escolhido - 1 linha]
- [Banco de dados]: [Por quê escolhido - 1 linha]

### Fluxo Principal
[Diagrama ASCII ou 3-5 passos]

DONE. Não complique.
```

#### ⏱️ Tempo Estimado (Solo)

- **Feature pequena**: ~15-30 min de planejamento
- **Feature média**: ~30-60 min de planejamento
- **Projeto novo**: ~1-2 horas de setup inicial

**ROI Solo**: Cada 30 min de planejamento economiza 2-3 horas de código mal estruturado

#### 📊 Checklist Obrigatório (Solo)

```markdown
[ ] 1. Li documentação existente (README, REQUIREMENTS, TASKS)
[ ] 2. Criei sprint atual (1-3 dias) com objetivo claro
[ ] 3. Quebrei em tarefas de 1-4h
[ ] 4. Identifiquei bloqueios/dúvidas
[ ] 5. Documentei arquitetura mínima (se projeto novo)
[ ] ✅ PLANEJAMENTO COMPLETO: Pode codificar
```

**Regra de Ouro Solo**:
> "Se você não consegue explicar seu plano em 5 minutos, ele está complexo demais. Simplifique."

**Mensagem para IAs (Solo Dev)**:
> "Solo developer não tem tempo para planning meetings. Mas PRECISA de organização. Crie sprints curtos (1-3 dias), tarefas pequenas (1-4h), documentação mínima. 30 minutos de planejamento economizam 3 horas de retrabalho. Organize-se, mas não se perca em cerimônias desnecessárias."

---

### 2️⃣ **Escolher as Tarefas Mais Simples**
- **Regra de Ouro**: Sempre começar pelas tarefas **mais fáceis de implementar**
- Mesmo em uma lista de tarefas complexas, **sempre há umas mais simples que outras**
- Proporcionalidade: equilibrar simplicidade vs. impacto

**Critérios de Simplicidade**:
- ✅ Menor número de dependências
- ✅ Escopo bem definido e claro
- ✅ Menor quantidade de arquivos a modificar
- ✅ Menor risco de quebrar funcionalidades existentes
- ✅ Pode ser testada isoladamente

**Exemplo Real**:
```
Lista de tasks complexas restantes:
[ ] Complex Feature Example (MUITO COMPLEXO - 50h)
[ ] Busca com IA semântica (COMPLEXO - 20h)
[ ] Tooltip preview em hover (SIMPLES - 30min) ✅ COMEÇAR POR AQUI!
```

---

### 2️⃣.5️⃣ **Matriz de Decisão Objetiva** [OPCIONAL]

**Quando Usar**: Quando tem 10+ tasks e não está óbvio qual é mais simples.

**O quê é**: Sistema de pontuação com 5 critérios (0-5 pontos cada):
1. **Simplicidade Técnica** (código, algoritmo, conceitos novos)
2. **Dependências** (arquivos a modificar, módulos afetados)
3. **Impacto** (valor usuário, frequência uso)
4. **Clareza** (requisitos definidos, exemplos)
5. **Risco** (quebrar código, reversibilidade)

**Fórmula**:
```
Prioridade = (Simplicidade × 2) + Dependências + (Impacto × 1.5) + Clareza + Risco
```

**Interpretação**:
- **30-35 pontos**: 🟢 IDEAL - Começar imediatamente
- **20-29 pontos**: 🟡 BOM
- **10-19 pontos**: 🟠 MÉDIO
- **0-9 pontos**: 🔴 COMPLEXO - Deixar por último

**Exemplo Rápido**:

| Task | Simpl | Dep | Imp | Clar | Risc | **Score** | Decisão |
|------|-------|-----|-----|------|------|-----------|---------|
| **Tooltip Preview** | 5 | 5 | 3 | 5 | 5 | **33.5** 🟢 | **ESCOLHER** |
| **Editor Integrado** | 1 | 2 | 5 | 4 | 2 | **20.5** 🟡 | Depois |

**Quando NÃO usar**:
- ❌ Apenas 1-3 tasks (óbvio qual é mais simples)
- ❌ Bugfix urgente (ignora pontuação)
- ❌ Task bloqueante (prioridade absoluta)

📘 **Detalhes completos**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 2.5 (template, exemplos)

---

### 2️⃣.6️⃣ **Organização Ordinal de Tarefas** [RECOMENDADO PARA SOLO]

> **Para Solo Developer em Produção**: Sistema pragmático para maximizar paralelização e eficiência.

**Quando Usar** (Simplicidade 3):
- ✅ Projetos **solo** com >10 tarefas interdependentes
- ✅ Necessidade de **alternar entre contextos** (pausar e retomar)
- ✅ Múltiplas **branches de feature** simultâneas
- ✅ Trabalho **assíncrono** (não linear)
- ✅ **Produção**: Necessidade de deploy incremental

#### 📊 Sistema Simplificado para Solo

**Numeração Pragmática**:
```markdown
## 🔴 MUST HAVE - Sprint v2.1.0

1. 🔴🟢 [ ] Setup CI/CD (0.5h) - Independente
2. 🔴🟢 [ ] Criar modelo User (1h) - Independente
3. 🔴🟡 [ ] API Login (2h) - Depende: #2
4. 🔴🔴 [ ] 2FA (3h) - Depende: #3

**Análise Solo**:
- Tasks #1 e #2: PARALELAS (posso alternar livremente)
- Tasks #3 e #4: SERIAIS (#3 antes de #4)
- Task #1: Posso fazer em qualquer momento (zero dependências)
```

**Hierarquia para Contextos Múltiplos**:
```markdown
A. Feature Autenticação (Branch: feat/auth)
   A.1. 🔴🟢 [ ] Modelo User (1h)
   A.2. 🔴🟡 [ ] Login JWT (2h) - Depende: A.1
   A.3. 🔴🔴 [ ] 2FA (3h) - Depende: A.2

B. Feature API (Branch: feat/api)
   B.1. 🔴🟢 [ ] Endpoints básicos (1.5h)
   B.2. 🔴🟡 [ ] Validação (1h) - Depende: B.1

**Estratégia Solo**:
1. Segunda-feira: A.1 (1h manhã)
2. Segunda-feira: B.1 (1.5h tarde) ← Mudo de contexto
3. Terça-feira: A.2 (2h manhã)
4. Terça-feira: B.2 (1h tarde) ← Paralelo
5. Quarta-feira: A.3 (3h) ← Volta para auth
```

#### ⚡ Benefícios para Solo em Produção

**Produtividade**:
- ✅ **Alternar contextos** quando bloqueado/cansado
- ✅ **Deploy incremental**: Merge A.1, A.2 sem esperar A.3
- ✅ **Rollback granular**: Reverter A.3 sem afetar A.1, A.2

**Organização Mental**:
- ✅ **Retomar trabalho**: Prefixo ordinal indica onde parou
- ✅ **Priorização clara**: Sabe quais tasks fazer primeiro
- ✅ **Pausar/Retomar**: Branch por grupo facilita contexto

**Exemplo Real** (Solo Developer):
```markdown
Sexta-feira 17h: Preciso parar no meio de A.2

TASKS.md:
A. Feature Autenticação (Branch: feat/auth)
   ✅ A.1. Modelo User (DONE - commit abc123)
   🟡 A.2. Login JWT (IN PROGRESS - 60% completo)
      → Próximo: Implementar refresh token
   ⚪ A.3. 2FA (BLOCKED - aguarda A.2)

Segunda-feira 9h: Retomo facilmente olhando TASKS.md
→ Sei exatamente onde continuar (A.2, refresh token)
→ Sei que A.3 está bloqueada até terminar A.2
```

#### 🔙 Rollback Plans e Organização Ordinal

Para produção solo, combine com Etapa 12.5 (Rollback Plans):

```markdown
A.2. Login JWT (2h) - CRÍTICO para produção

Rollback Plan:
- SE taxa de erro > 5%: Reverter APENAS A.2
- Manter A.1 (modelo) em produção
- Feature flag: ENABLE_JWT_LOGIN=false
- Fallback: Login básico (versão anterior)

Prefixo ordinal permite rollback GRANULAR:
✅ Reverter A.2 sem tocar A.1
❌ Sem prefixo: Reverter "feature autenticação" toda
```

#### 🤖 IA Como Assistente Solo

A IA pode sugerir organização ordinal:

```markdown
💡 **Sugestão da IA**: Identifiquei 8 tarefas no seu backlog

Análise de dependências:
- 3 tarefas INDEPENDENTES (1, 2, 5)
- 2 grupos PARALELOS (A.x, B.x)
- 1 dependência CRUZADA (C aguarda A.3)

Recomendação para maximizar produtividade:
1. Esta semana: Grupos A e B (parallel)
   - Segunda: A.1 (manhã) + B.1 (tarde)
   - Terça: A.2 (manhã) + B.2 (tarde)
2. Próxima semana: A.3 → C.1 (serial)

Prefere essa organização ou quer ajustar?
```

#### ✅ Quando NÃO Usar (Solo)

- ❌ Projeto <5 tarefas (overhead desnecessário)
- ❌ Sprint de 1 dia (linear é suficiente)
- ❌ Todas tarefas SERIAIS (sem paralelização possível)

📘 **Documentação Completa**: Ver `ORGANIZACAO_ORDINAL_TAREFAS.md` para:
- Hierarquia profunda para projetos complexos
- Leitura direita→esquerda (C.B.1.D.1)
- Fluxograma de decisão
- Exemplos completos

---

### 3️⃣ **Fazer Perguntas e Mais Perguntas ao Programador**
- **CRÍTICO**: Nunca assumir ou adivinhar requisitos
- Fazer **todas as perguntas necessárias** até sanar **100% das dúvidas**
- Validar entendimento antes de começar a implementar
- 🤖 **[NOVO v3.1]** A IA **PODE e É ALTAMENTE RECOMENDADA** fornecer **sugestões e palpites** de resposta para cada pergunta (opcional, mas incentivado)

**Formato Recomendado de Perguntas com Sugestões**:
```
❓ Pergunta: "Como deve se comportar quando [cenário X]?"
💡 Sugestão da IA: "Baseado no código existente, sugiro [opção A] porque [razão Y]."
Opções: A) [opção A] | B) [opção B] | C) [opção C]
```

**Por Quê Sugestões da IA São Importantes**:
- ✅ Acelera decisões quando o programador está indeciso
- ✅ IA tem contexto do código existente e pode sugerir padrões consistentes
- ✅ Reduz carga cognitiva do programador (ele apenas valida, não cria do zero)
- ✅ Mantém qualidade: IA sugere baseado em boas práticas já implementadas

**Categorias de Perguntas**:
1. **Requisitos Funcionais**:
   - "Como deve se comportar quando [cenário X]?"
   - "O que acontece se o usuário [ação Y]?"
   - "Qual é a prioridade entre [opção A] e [opção B]?"

2. **Requisitos Técnicos**:
   - "Devo usar [biblioteca X] ou criar do zero?"
   - "Qual é o formato esperado do output?"
   - "Há alguma restrição de performance?"

3. **Edge Cases**:
   - "E se o arquivo estiver vazio?"
   - "E se houver caracteres especiais?"
   - "Como tratar valores None/null?"

4. **Integração**:
   - "Precisa integrar com [módulo existente]?"
   - "Devo manter compatibilidade com [versão anterior]?"
   - "Onde salvar os resultados?"

5. **Validação de Entendimento**:
   - "Entendi que você quer [X]. Está correto?"
   - "Minha solução proposta é [Y]. Faz sentido?"
   - "Posso começar ou há algo que esqueci?"

**Exemplo Real (Task Example)**:
```
❓ "Pegar primeiras N palavras (quantas? 3-5?)?"
✅ Resposta: "Default pode ser 30 caracteres"

❓ "Converter para camelCase removendo acentos?"
✅ Resposta: "Sim, devem ser removidos acentos"

❓ "Conflitos de nomes: como resolver?"
✅ Resposta: "Se tiverem a mesma chave pai, não mexa. Linha menor vence."
```

**Por quê?**: Economiza tempo, evita retrabalho, garante que a solução atende exatamente o que foi pedido.

#### 🌐 **Pesquisas Online: Quando a IA Tem Muitas Dúvidas ou Dificuldades**

> **IMPORTANTE PARA IAs**: Se você está com **muitas dúvidas** sobre como resolver um determinado problema, ou tem **dificuldades significativas** para resolver esse mesmo problema, **lembre-se de que você pode efetuar pesquisas online**.

**Quando Realizar Pesquisas Online**:
- ✅ Quando há dúvidas técnicas complexas que não consegue resolver sozinho
- ✅ Quando encontra um problema crítico que não tem solução óbvia no código existente
- ✅ Quando precisa entender como implementar algo completamente novo
- ✅ Quando há um erro ou bug difícil de diagnosticar
- ✅ Quando precisa de exemplos práticos de implementação

**Onde Pesquisar** (em ordem de prioridade):
1. **📚 Documentação Oficial do GitHub de Projetos Relacionados**:
   - Repositórios similares ou que resolvem problemas parecidos
   - Issues e Pull Requests que discutem problemas similares
   - Wiki e documentação técnica de projetos open source relacionados

2. **📖 Plataformas de Documentação Online**:
   - Documentação oficial das bibliotecas e frameworks usados no projeto
   - Tutoriais e guias técnicos especializados
   - Blogs técnicos e artigos de desenvolvedores experientes

3. **💬 Plataformas de Perguntas e Respostas**:
   - **StackOverflow**: Principal plataforma para dúvidas de programação
   - **GitHub Discussions**: Para questões específicas de projetos
   - Outras comunidades técnicas relevantes para a tecnologia do projeto

**Por Quê Pesquisas Online São Importantes**:
- ✅ **Economiza tempo**: Problemas complexos já podem ter soluções documentadas
- ✅ **Melhores práticas**: Aprenda com implementações já validadas pela comunidade
- ✅ **Evita reinventar a roda**: Muitos problemas já foram resolvidos por outros desenvolvedores
- ✅ **Reduz erros**: Soluções testadas e aprovadas pela comunidade têm menos bugs
- ✅ **Atualização**: Descubra as abordagens mais modernas e eficientes

**Exemplo de Fluxo com Pesquisa Online**:
```
1. ❓ Tentei implementar [funcionalidade X] mas encontrei [problema Y]
2. 🔍 Pesquisei no GitHub: "similar implementation [funcionalidade X]"
3. 📚 Encontrei 3 projetos similares que resolvem isso de formas diferentes
4. 💡 Analisei os exemplos e identifiquei a abordagem mais adequada para nosso contexto
5. ✅ Implementei baseado nas melhores práticas encontradas
6. 📝 Documentei a fonte da solução para referência futura
```

**⚠️ Importante**: Sempre cite as fontes consultadas na documentação do projeto para referência futura e rastreabilidade.

---

### 4️⃣ **Analisar e Estudar o Projeto**
- **CRÍTICO**: Após sanar todas as dúvidas, **estudar o código antes de implementar**
- Ler documentação relevante (README, docs/, comentários no código)
- Entender arquitetura existente e padrões utilizados
- Verificar dependências e imports necessários
- Identificar funções/classes reutilizáveis

**Checklist de Análise**:
1. **Leitura de Documentação**:
   - `docs/REQUIREMENTS.md` - Contexto geral do projeto
   - `docs/SPECIFICATIONS.md` - Especificações de versões anteriores
   - `README.md` - Visão geral e instruções de uso
   - Docstrings de módulos relacionados

2. **Análise de Código Existente**:
   - Encontrar módulos similares ao que será implementado
   - Identificar padrões de design já utilizados (GoF, GRASP)
   - Verificar convenções de nomenclatura e estrutura
   - Localizar funções auxiliares reutilizáveis

3. **Mapeamento de Dependências**:
   - Quais módulos precisam ser importados?
   - Há conflitos de nomes ou versões?
   - Quais classes base ou mixins devem ser herdadas?
   - Onde os novos arquivos devem ser criados?

4. **Validação de Compatibilidade**:
   - A solução quebrará código existente?
   - É necessário refatorar algo antes de implementar?
   - Há testes que precisam ser atualizados?
   - A API pública será mantida?

**Exemplo Real (Task Example - Tutorials)**:
```
✅ Analisado: Outros docks (ComponentA, ComponentB)
✅ Identificado: Padrão BaseDock com FileInputMixin
✅ Verificado: QTreeWidget + QTextBrowser para navegação
✅ Estudado: Como outros módulos fazem markdown → HTML
✅ Localizado: Onde adicionar imports em app.py
✅ Confirmado: Estrutura de menu em _build_menu()
→ Resultado: Implementação em 2h ao invés de 5h (economia de 60%)
```

#### 🔀 **Princípio de Opções Paralelas (Multi-Choice)**

[Content: Same core as Protocol 1 PT with solo-specific adaptations]

**[ESPECÍFICO PARA SIMPLICIDADE 3 - SOLO]**:
> "Para solo developers, opções paralelas são um investimento de tempo que pode valer a pena A LONGO PRAZO. Pergunte-se: 'Vou querer trocar entre essas visualizações com frequência?' Se sim, implemente ambas. Se não, escolha uma por agora e adicione a segunda DEPOIS se necessário. Priorize features que você realmente usará. Não gaste 2h implementando opção que usará 1x por ano."

**Análise Custo-Benefício (Solo)**:
```markdown
**Antes de implementar opções paralelas, responda**:

1. **Frequência de uso**: Vou alternar entre opções regularmente?
   - ✅ Sim, diariamente/semanalmente → Vale a pena
   - ❌ Não, raramente → Escolher uma por agora

2. **Custo de implementação**: Quanto tempo adicional?
   - ✅ <30 min → Baixo custo, faça
   - ⚠️  30-60 min → Médio, avaliar benefício
   - ❌ >60 min → Alto custo, priorizar feature principal

3. **Manutenção futura**: Vou ter que testar/documentar 2x mais?
   - ✅ Sim → Certifique-se que vale a pena
   - ❌ Opções são independentes → Menos overhead

4. **Feedback de usuários**: Usuários pediram opções múltiplas?
   - ✅ Sim → Implementar ambas agora
   - ❌ Não → Esperar feedback, adicionar depois
```

**Estratégia Solo "MVP First"**:
1. Implementar opção principal (mais comum) PRIMEIRO
2. Lançar e coletar feedback
3. Se usuários pedirem opção alternativa, adicionar DEPOIS
4. Evita trabalho especulativo (pode nunca ser necessário)

**Por quê?**: Evita refatorações, economiza tempo, garante código consistente com a base existente.

---

### 5️⃣ **Fazer Sprints das Tarefas Mais Simples**
- Agrupar 2-4 tarefas relacionadas em um sprint
- Estimar tempo total: **máximo 3-4 horas** por sprint
- Manter foco: **uma sprint = uma versão (ex: vX.Y.Z)**

**⚠️ Importante - Divisão de Tarefas em Subtasks**:
> Tarefas devem ser divididas em partes menores **somente se realmente necessário**, isto é:
> - ✅ Quando há **maior probabilidade de estourar o tempo máximo** (>4h)
> - ✅ Quando há **maior possibilidade da resposta ser muito longa** (implementação complexa)
> - ❌ **NÃO dividir** se a tarefa é razoavelmente simples e cabe no limite de tempo
> 
> Esta decisão deve ser feita pela **inteligência artificial responsável pela programação** do projeto, baseada na complexidade real da tarefa.

**Estrutura de Sprint**:
```
Sprint vX.Y.Z (Exemplo Task Example):
├── Task Example: Feature Update (3h estimado)
│   ├── Subtask 1: Fazer perguntas ao programador (15min)
│   ├── Subtask 2: extract_all_keys_from_obj() (45min)
│   ├── Subtask 3: build_substitution_map_by_value() (45min)
│   ├── Subtask 4: Integração em cli_dedupe() (30min)
│   ├── Subtask 5: Testes unitários (60min)
│   └── Subtask 6: Documentação (30min)
└── Total: 3h45min ✅
```

---

### 6️⃣ **Implementar do Simples ao Complexo com Arquitetura Profissional**
- **Dentro de cada task**, começar pela parte mais fácil
- Construir incrementalmente: função auxiliar → função principal → integração
- Testar cada parte antes de avançar

**Ordem de Implementação**:
1. **Funções auxiliares** (ex: `extract_all_keys_from_obj()`)
2. **Funções principais** (ex: `build_substitution_map_by_value()`)
3. **Integração** (ex: atualizar `cli_dedupe()`)
4. **GUI/UX** (se aplicável)
5. **Otimizações** (último passo)

**Princípios de Arquitetura (Obrigatórios)**:

#### 🔄 **Reutilização de Código com Módulos**
- Criar módulos separados para cada responsabilidade
- Evitar duplicação (DRY - Don't Repeat Yourself)
- Funções genéricas reutilizáveis em múltiplos contextos

**Exemplo**:
```python
# ✅ BOM: Módulo reutilizável
# src/utils/file_utils.py
def read_file_safe(path: str) -> Optional[str]:
    """Função reutilizada em 10+ lugares"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None

# ❌ RUIM: Duplicar código em cada módulo
# (repete try/except 20 vezes)
```

#### 💬 **Comentários de Código Obrigatórios**

> **CRÍTICO**: Todo código implementado **DEVE** ser comentado quando a linguagem de programação permitir comentários.

[Content: Same extensive section as Protocol 1 - code comments guidelines, examples, etc.]

**Mensagem para IAs**:
> "Ao gerar código, SEMPRE adicione comentários explicativos. Comente o 'por quê', não apenas o 'o quê'. Um código bem comentado vale 10x mais que código limpo sem comentários."

**[ESPECÍFICO PARA SIMPLICIDADE 3 - SOLO]**:
> "Para solo developers, comentários são sua 'memória externa'. Você esquecerá por quê tomou certas decisões em 3 meses. Comente para o 'você do futuro'. Documente especialmente: decisões técnicas não-óbvias, workarounds temporários, e por quê escolheu biblioteca X ao invés de Y. Seu 'eu futuro' agradecerá."

#### 🌳 **Analogia da Árvore de Importações**

**Conceito**: A estrutura de importações de um programa pode ser visualizada como uma árvore, onde cada módulo importa outros módulos, formando uma hierarquia de dependências.

**Profundidade Ilimitada**: Esta árvore pode alcançar **qualquer nível ou altura** dependendo da complexidade do programa:
- **Programas Simples**: Árvore rasa (2-3 níveis)
  ```
  main.py
  └── utils.py
      └── helpers.py
  ```

- **Programas Médios**: Árvore moderada (4-6 níveis)
  ```
  app.py
  ├── controllers/
  │   └── user_controller.py
  │       └── services/
  │           └── user_service.py
  │               └── models/
  │                   └── user.py
  └── config.py
  ```

- **Programas Complexos**: Árvore profunda (7+ níveis)
  ```
  enterprise_app.py
  ├── api/
  │   ├── routes/
  │   │   └── v1/
  │   │       └── users.py
  │   │           └── handlers/
  │   │               └── authentication.py
  │   │                   └── providers/
  │   │                       └── oauth/
  │   │                           └── google.py
  │   │                               └── scopes.py
  ```

**Aplicação na Refatoração**:

1. **Identificar Profundidade Excessiva**:
   - ✅ Se árvore > 8 níveis → Considerar simplificação
   - ✅ Módulos muito profundos = difícil manutenção

2. **Detectar Dependências Circulares**:
   ```python
   # ❌ RUIM: Dependência circular
   # module_a.py
   from module_b import B
   
   # module_b.py
   from module_a import A  # Circular!
   ```

3. **Reorganizar por Coesão**:
   ```python
   # ✅ BOM: Agrupar imports relacionados
   # antes (disperso):
   from utils.string import normalize
   from helpers.text import clean
   from tools.format import sanitize
   
   # depois (coeso):
   from text_processing import normalize, clean, sanitize
   ```

4. **Reduzir Acoplamento**:
   - ✅ Imports diretos apenas do necessário
   - ✅ Evitar `from module import *` (aumenta acoplamento)
   - ✅ Usar interfaces/abstrações para desacoplar

5. **Visualizar para Entender**:
   - Use ferramentas como `pydeps`, `import-graph` (Python)
   - Identifique "hubs" (módulos muito importados)
   - Refatore módulos centrais para reduzir impacto

**Por quê importante**:
- ✅ **Compreensão**: Árvore clara = código mais fácil de entender
- ✅ **Manutenção**: Dependências organizadas = mudanças localizadas
- ✅ **Performance**: Menos imports desnecessários = startup mais rápido
- ✅ **Testes**: Módulos independentes = testes isolados
- ✅ **Refatoração**: Visualizar árvore ajuda a identificar oportunidades de melhoria

#### 📦 **Hierarquias e Encapsulamento**
- Usar classes quando há estado compartilhado
- Encapsular atributos privados (`_attribute`)
- Expor apenas interface pública necessária

**Exemplo**:
```python
# ✅ BOM: Encapsulamento adequado
class ReferenceUpdater:
    def __init__(self, project_dir: str):
        self._project_dir = project_dir
        self._substitutions = {}
    
    def update_references(self) -> Dict[str, int]:
        """Interface pública clara"""
        self._scan_files()  # Método privado
        self._build_map()   # Método privado
        return self._apply_changes()

# ❌ RUIM: Tudo exposto, sem estrutura
def do_everything(dir, old, new, backup, ext):
    # 200 linhas sem organização
```

#### 🎯 **Alta Coesão e Baixo Acoplamento**
- **Alta Coesão**: Cada módulo/classe tem uma única responsabilidade clara
- **Baixo Acoplamento**: Módulos independentes, comunicação por interfaces

**Exemplo**:
```python
# ✅ ALTA COESÃO: Cada classe faz UMA coisa
class KeyExtractor:
    """Apenas extrai chaves de estruturas"""
    def extract(self, data) -> Dict[str, str]: ...

class SubstitutionMapBuilder:
    """Apenas constrói mapa de substituições"""
    def build(self, old, new) -> Dict[str, str]: ...

class FileUpdater:
    """Apenas atualiza arquivos"""
    def update(self, files, map) -> int: ...

# ✅ BAIXO ACOPLAMENTO: Comunicação por interfaces
class ReferenceUpdater:
    def __init__(self, extractor: KeyExtractor, builder: SubstitutionMapBuilder):
        self._extractor = extractor  # Injeção de dependência
        self._builder = builder

# ❌ RUIM: Baixa coesão, alto acoplamento
class EverythingManager:
    def do_all(self):
        # Faz extração + construção + atualização + logging + GUI
        # Importa 20 módulos diferentes
        # Impossível testar isoladamente
```

#### 🏗️ **Padrões GoF (Gang of Four)**
Aplicar padrões de design quando apropriado:

1. **Strategy Pattern** (escolha de algoritmo em runtime):
```python
class CaseConverter:
    def __init__(self, strategy: CaseStrategy):
        self._strategy = strategy
    
    def convert(self, text: str) -> str:
        return self._strategy.apply(text)

class CamelCaseStrategy(CaseStrategy):
    def apply(self, text: str) -> str: ...

class SnakeCaseStrategy(CaseStrategy):
    def apply(self, text: str) -> str: ...
```

2. **Factory Pattern** (criação de objetos complexos):
```python
class ProcessorFactory:
    @staticmethod
    def create(type: str) -> Processor:
        if type == "data":
            return DATAProcessor()
        elif type == "ts":
            return TypeScriptProcessor()
```

3. **Observer Pattern** (notificação de eventos):
```python
class ProcessingModal(QDialog):
    cancel_requested = Signal()  # Observer pattern
    
    def _on_cancel_clicked(self):
        self.cancel_requested.emit()  # Notifica observadores
```

4. **Command Pattern** (undo/redo):
```python
class ReplaceCommand:
    def __init__(self, file: str, old: str, new: str):
        self._file = file
        self._old = old
        self._new = new
    
    def execute(self): ...
    def undo(self): ...
```

#### 🎨 **Padrões GRASP (General Responsibility Assignment Software Patterns)**

1. **Information Expert**: Atribua responsabilidade a quem tem a informação
```python
# ✅ BOM: Dictionary tem a info, então tem o método
class DataStore:
    def __init__(self, data: dict):
        self._data = data
    
    def get_value(self, key_path: str) -> Optional[str]:
        """Dictionary conhece sua estrutura"""
        return self._navigate_path(key_path)

# ❌ RUIM: Classe externa manipula estrutura interna
def get_value_from_dict(dict_data, key_path):
    # Acesso direto à estrutura interna do dict
```

2. **Creator**: Classe A cria B se A contém/agrega B
```python
# ✅ BOM: RewriterDock cria seus próprios widgets
class ComponentB(BaseDock):
    def __init__(self):
        self._create_widgets()  # Creator pattern
        self._setup_layout()
    
    def _create_widgets(self):
        self.ed_input = QLineEdit()  # Cria seus filhos
        self.btn_process = QPushButton()
```

3. **Controller**: Delegar operações do sistema a controlador
```python
# ✅ BOM: Controlador coordena operações
class RewriterController:
    def process_file(self, path: str):
        data = self._reader.read(path)
        processed = self._processor.process(data)
        self._writer.write(path, processed)

# ❌ RUIM: GUI faz tudo diretamente
class RewriterDock:
    def on_button_click(self):
        # 50 linhas de lógica de negócio na GUI
```

4. **Low Coupling**: Minimizar dependências
```python
# ✅ BOM: Interface genérica
def update_references(updater: ReferenceUpdater):
    """Aceita qualquer updater que implemente a interface"""
    updater.update()

# ❌ RUIM: Dependência concreta
def update_references(file_path: str, backup: bool, ext: list):
    """Muitos parâmetros, alto acoplamento"""
```

5. **High Cohesion**: Uma classe, uma responsabilidade
```python
# ✅ BOM: Alta coesão
class FileReader:
    """Apenas lê arquivos"""
    def read(self, path: str) -> str: ...

class DataValidator:
    """Apenas valida dados"""
    def validate(self, data: dict) -> bool: ...

# ❌ RUIM: Baixa coesão
class FileManager:
    def read(self): ...
    def write(self): ...
    def validate(self): ...
    def send_email(self): ...  # ?!
```

**Anti-padrão** ❌:
```python
# NÃO fazer tudo de uma vez:
def complex_function_with_everything():
    # 500 linhas de código
    # Múltiplas responsabilidades
    # Difícil de testar
    # Alto acoplamento
    # Sem reutilização
```

**Padrão Correto** ✅:
```python
# Módulo: src/rewriter/key_extractor.py
class KeyExtractor:
    """Alta coesão: só extrai chaves"""
    def extract_from_obj(self, data) -> Dict[str, str]:
        return self._recurse(data, prefix='t')

# Módulo: src/rewriter/substitution_builder.py
class SubstitutionMapBuilder:
    """Alta coesão: só constrói mapas"""
    def build_by_value(self, old, new) -> Dict[str, str]:
        return self._match_values(old, new)

# Módulo: src/rewriter/reference_updater.py
class ReferenceUpdater:
    """Baixo acoplamento: usa interfaces"""
    def __init__(self, extractor: KeyExtractor, builder: SubstitutionMapBuilder):
        self._extractor = extractor  # Injeção de dependência
        self._builder = builder
    
    def update_project(self, dir: str) -> Dict[str, int]:
        """Coordena mas não implementa tudo"""
        old = self._extractor.extract(self._read_old())
        new = self._extractor.extract(self._read_new())
        map = self._builder.build_by_value(old, new)
        return self._apply_to_files(dir, map)
```

---

### 6️⃣.5️⃣ **Security Checklist OWASP** ⭐ [OBRIGATÓRIO]

> **CRÍTICO PARA PRODUÇÃO**: Esta etapa é **OBRIGATÓRIA** no Simplicidade 3.

**Por quê obrigatório para produção**:
- ✅ Vulnerabilidades afetam **usuários reais**
- ✅ Você está **sozinho** - sem segundo par de olhos
- ✅ LGPD/GDPR se aplica a dados de usuários
- ✅ Checklist rápido (10-15min) previne problemas caros

**OWASP Top 10 - Checklist Simplificado**:

```markdown
## Security Checklist - Task #XX

### 1. Injection (SQL, Command, Code)
- [ ] Todas queries SQL usam **parametrização** (sem f-strings)?
- [ ] Comandos shell sanitizados (**shlex.quote()** ou evitados)?
- [ ] `eval()`, `exec()`, `__import__()` NÃO usados?

### 2. Autenticação
- [ ] Senhas NUNCA em plaintext (usar **bcrypt/argon2**)?
- [ ] Tokens/sessions têm **expiração** e **invalidação**?
- [ ] Rate limiting em endpoints de login (prevenir brute-force)?

### 3. Dados Sensíveis
- [ ] Dados sensíveis **NÃO** em logs (senhas, tokens, CPF)?
- [ ] Arquivos sensíveis têm **permissões corretas** (600/700)?
- [ ] Secrets em **variáveis de ambiente** (não hardcoded)?

### 4. XML/XXE (se usar XML)
- [ ] Parser XML tem **entity expansion desabilitado**?
- [ ] Validação de schema antes de parsear?

### 5. Controle de Acesso
- [ ] Permissões verificadas **antes** de operações críticas?
- [ ] Usuário não pode acessar dados de **outros usuários**?
- [ ] Paths validados (sem **path traversal**: `../../etc/passwd`)?

### 6. Configurações Inseguras
- [ ] **DEBUG=False** em produção?
- [ ] Secrets **NÃO** commitados no Git (.env no .gitignore)?
- [ ] Deps atualizadas (**pip-audit** sem vulnerabilidades)?

### 7. XSS (se tiver web/HTML)
- [ ] Output HTML **escapado** (usar template engine)?
- [ ] User input **sanitizado** antes de exibir?

### 8. Desserialização Insegura
- [ ] **pickle** evitado (ou validado se necessário)?
- [ ] DATA preferido sobre pickle para dados externos?

### 9. Deps Vulneráveis
- [ ] `pip-audit` executado e sem HIGH/CRITICAL?
- [ ] Dependências atualizadas (últimos 6 meses)?

### 10. Logs/Monitoring
- [ ] Operações críticas **logadas** (create, update, delete)?
- [ ] Logs **NÃO** contêm dados sensíveis?
```

**Exemplo INSEGURO vs SEGURO**:

```python
# ❌ INSEGURO - SQL Injection
def get_user(username):
    query = f"SELECT * FROM users WHERE name='{username}'"
    return db.execute(query)
# Ataque: username = "admin' OR '1'='1"

# ✅ SEGURO - Parametrizado
def get_user(username):
    query = "SELECT * FROM users WHERE name=?"
    return db.execute(query, (username,))

# ❌ INSEGURO - Command Injection
def backup_file(filename):
    os.system(f"tar -czf backup.tar.gz {filename}")
# Ataque: filename = "file.txt; rm -rf /"

# ✅ SEGURO - Lista de args
def backup_file(filename):
    subprocess.run(["tar", "-czf", "backup.tar.gz", filename], check=True)

# ❌ INSEGURO - Senha em log
logger.info(f"User {username} logged in with password {password}")

# ✅ SEGURO - Sem dados sensíveis
logger.info(f"User {username} logged in successfully")

# ❌ INSEGURO - Path Traversal
def read_file(user_path):
    with open(f"/app/data/{user_path}") as f:
        return f.read()
# Ataque: user_path = "../../etc/passwd"

# ✅ SEGURO - Validar path
def read_file(user_path):
    safe_path = os.path.abspath(f"/app/data/{user_path}")
    if not safe_path.startswith("/app/data/"):
        raise ValueError("Invalid path")
    with open(safe_path) as f:
        return f.read()
```

**Ferramentas Automáticas** (executar ANTES de commit):

```bash
# 1. Vulnerabilidades em dependências
pip install pip-audit
pip-audit
# Se reportar HIGH/CRITICAL, atualizar deps

# 2. Security linter
pip install bandit
bandit -r . -ll  # Low confidence + Low severity
# Revisar issues reportados

# 3. Secrets detectados
pip install detect-secrets
detect-secrets scan > .secrets.baseline
# Revisar se algum secret vazou
```

**Pre-commit Hook** (automatizar):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-ll']
  
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
```

**Quando PULAR o checklist** (raramente):
- ❌ Código interno sem dados sensíveis
- ❌ Script descartável de uso único
- ❌ Protótipo não-produção

**Tempo Estimado**: 10-15 minutos por task.

📘 **Checklist completo com 10 exemplos**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 6.5

---

### 6️⃣.6️⃣ **Ícones do Projeto** [OBRIGATÓRIO]

> **CRÍTICO PARA IAs**: Todo projeto deve incluir ícones adequados para garantir profissionalismo e identidade visual.

**Quando Aplicar**: Durante a implementação (Etapa 6), após definir a estrutura básica do projeto.

#### 📋 Requisito Obrigatório

A inteligência artificial **DEVE** produzir ou fazer download de um ícone para o projeto, seja:
- 🌐 Site/Aplicação Web
- 💻 Programa Desktop
- 📱 Aplicativo Mobile
- 🔧 Ferramenta/Utilitário

#### 🎨 Formatos de Ícone por Tecnologia

**Aplicações Web**:
- ✅ **favicon.ico** (16x16, 32x32, 48x48 px) - Compatibilidade universal
- ✅ **icon.svg** - Vetorial, escalável, moderno
- ✅ **icon-192.png** e **icon-512.png** - PWA/Android
- ✅ **apple-touch-icon.png** (180x180 px) - iOS

**Aplicações Desktop**:
- ✅ **icon.png** (256x256, 512x512 px) - Linux
- ✅ **icon.ico** (múltiplos tamanhos) - Windows
- ✅ **icon.icns** - macOS

**Aplicações Mobile**:
- ✅ **icon.png** (1024x1024 px) - iOS App Store
- ✅ **ic_launcher.png** (múltiplas densidades) - Android
- ✅ **adaptive-icon.xml** - Android adaptativo

#### 📁 Estrutura de Pastas (OBRIGATÓRIO)

Os ícones **DEVEM** ser organizados em uma pasta dedicada:

```
projeto/
├── assets/              # ✅ PREFERIDO (padrão para todos)
│   ├── icons/
│   │   ├── favicon.ico
│   │   ├── icon.svg
│   │   ├── icon-192.png
│   │   ├── icon-512.png
│   │   └── apple-touch-icon.png
│   └── ...
│
# OU alternativas conforme tecnologia:
├── public/              # ✅ React, Vue, Next.js
│   ├── favicon.ico
│   └── icons/
├── static/              # ✅ Flask, Django, Svelte
│   └── icons/
├── src/assets/          # ✅ Angular, Ionic
│   └── icons/
├── resources/           # ✅ Electron, Tauri
│   └── icons/
└── res/                 # ✅ Android nativo
    └── drawable/
```

**Regra de Ouro**: Sempre usar uma pasta específica para ícones, nunca arquivos soltos na raiz do projeto.

#### 🔧 Como Obter/Criar Ícones

A IA deve seguir esta ordem de prioridade:

1. **Perguntar ao Programador** (SEMPRE primeiro):
   ```
   ❓ Você já tem um ícone para o projeto?
   
   Opções:
   A) ✅ Sim, tenho (forneça o caminho/arquivo)
   B) 🎨 Não, crie um ícone simples para mim
   C) 🔍 Não, baixe um ícone gratuito adequado
   D) ⏭️ Pular por enquanto (não recomendado)
   ```

2. **Se A (Usuário fornece)**:
   - Validar formato e tamanho
   - Converter para formatos necessários (usar ferramentas como `convert`, `sharp`, `imagemagick`)
   - Organizar na pasta correta

3. **Se B (IA cria ícone simples)**:
   - Criar ícone SVG vetorial com iniciais do projeto
   - Exportar para formatos necessários (PNG, ICO)
   - Usar cores da identidade do projeto (se definidas)

4. **Se C (IA baixa ícone)**:
   - Usar fontes gratuitas e sem copyright:
     - ✅ [Heroicons](https://heroicons.com/) (MIT License)
     - ✅ [Lucide Icons](https://lucide.dev/) (ISC License)
     - ✅ [Tabler Icons](https://tabler-icons.io/) (MIT License)
     - ✅ [Iconoir](https://iconoir.com/) (MIT License)
   - Verificar licença antes de usar
   - Documentar fonte no README

5. **Se D (Pular)**:
   - ⚠️ Avisar que projeto ficará sem identidade visual
   - Adicionar task no TASKS.md para futuro: `[ ] Criar ícone do projeto`

#### 🎨 Exemplo de Ícone SVG Simples (Gerado pela IA)

```svg
<!-- assets/icons/icon.svg -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#4F46E5"/>
  <text x="50" y="65" font-family="Arial, sans-serif" font-size="48" 
        font-weight="bold" fill="white" text-anchor="middle">MP</text>
</svg>
```

#### 🔨 Ferramentas para Conversão de Ícones

**Python** (recomendado para automação):
```bash
# Instalar Pillow
pip install Pillow

# Converter SVG para PNG (via cairosvg)
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='icon.svg', write_to='icon.png', output_width=512)"

# Criar ICO com múltiplos tamanhos
from PIL import Image
img = Image.open('icon.png')
img.save('favicon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48)])
```

**Node.js** (projetos web):
```bash
# Instalar sharp
npm install sharp

# Script de conversão
node -e "
const sharp = require('sharp');
sharp('icon.svg').resize(192, 192).toFile('icon-192.png');
sharp('icon.svg').resize(512, 512).toFile('icon-512.png');
"
```

**ImageMagick** (universal):
```bash
# Converter SVG para PNG
convert icon.svg -resize 192x192 icon-192.png

# Criar favicon.ico
convert icon.png -define icon:auto-resize=16,32,48 favicon.ico
```

#### 🗂️ Integração com o Projeto

**HTML (Web)**:
```html
<!-- index.html -->
<head>
  <!-- Favicon básico -->
  <link rel="icon" type="image/x-icon" href="/assets/icons/favicon.ico">
  
  <!-- SVG moderno (preferido) -->
  <link rel="icon" type="image/svg+xml" href="/assets/icons/icon.svg">
  
  <!-- PNG para diferentes tamanhos -->
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/icon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/icon-192.png">
  
  <!-- Apple Touch Icon -->
  <link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
  
  <!-- Android Chrome -->
  <link rel="manifest" href="/manifest.json">
</head>
```

**manifest.json (PWA)**:
```json
{
  "name": "Meu Projeto",
  "short_name": "MP",
  "icons": [
    {
      "src": "/assets/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/assets/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**Python (Desktop - PyQt/Tkinter)**:
```python
# PyQt6
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

app = QApplication([])
app.setWindowIcon(QIcon('assets/icons/icon.png'))

# Tkinter
import tkinter as tk
root = tk.Tk()
root.iconbitmap('assets/icons/icon.ico')  # Windows
# ou
root.iconphoto(True, tk.PhotoImage(file='assets/icons/icon.png'))  # Linux/Mac
```

**Electron (Desktop)**:
```javascript
// main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');

const win = new BrowserWindow({
  icon: path.join(__dirname, 'resources/icons/icon.png')
});
```

**React Native (Mobile)**:
```
// android/app/src/main/res/
mipmap-hdpi/ic_launcher.png      (72x72)
mipmap-mdpi/ic_launcher.png      (48x48)
mipmap-xhdpi/ic_launcher.png     (96x96)
mipmap-xxhdpi/ic_launcher.png    (144x144)
mipmap-xxxhdpi/ic_launcher.png   (192x192)

// ios/ProjectName/Images.xcassets/AppIcon.appiconset/
// Configurado via Xcode ou Contents.json
```

#### ⏰ Melhor Momento para Adicionar Ícones

**Recomendação**: **Durante Etapa 6 (Implementação)**, preferencialmente:

1. **Início do Projeto** (✅ IDEAL):
   - Ao criar estrutura inicial de pastas
   - Antes do primeiro commit
   - Facilita identidade visual desde o início

2. **MVP/Protótipo** (✅ BOM):
   - Após funcionalidades básicas funcionarem
   - Antes de mostrar para usuários/clientes
   - Garante profissionalismo mínimo

3. **Antes de Produção** (⚠️ ACEITÁVEL):
   - Durante preparação para deploy
   - Antes de publicar (App Store, Play Store, web)
   - Mínimo necessário, mas atrasado

4. **❌ NUNCA**: Deixar para "depois" sem data definida

#### 📋 Checklist de Ícones (Validação)

```markdown
## Checklist de Ícones - Projeto [Nome]

### Ícones Criados
- [ ] Ícone principal criado/obtido (fonte: [especificar])
- [ ] Licença verificada (se baixado de fonte externa)
- [ ] Formato vetorial disponível (SVG) ou fonte PNG de alta qualidade

### Formatos Necessários
- [ ] **favicon.ico** (16x16, 32x32, 48x48 px)
- [ ] **icon.svg** (vetorial)
- [ ] **icon-192.png** (192x192 px) - PWA
- [ ] **icon-512.png** (512x512 px) - PWA
- [ ] **apple-touch-icon.png** (180x180 px) - iOS
- [ ] Outros formatos específicos da tecnologia

### Organização
- [ ] Pasta `assets/icons/` criada
- [ ] Todos os ícones organizados na pasta correta
- [ ] Nenhum ícone solto na raiz do projeto

### Integração
- [ ] Ícone referenciado no HTML/código principal
- [ ] manifest.json atualizado (se PWA)
- [ ] Testado em navegador/aplicativo (ícone aparece)
- [ ] Documentado no README (se ícone de terceiros)

### Qualidade
- [ ] Ícone tem boa resolução (não pixelado)
- [ ] Cores adequadas ao projeto
- [ ] Visível em fundos claros E escuros (se aplicável)
- [ ] Reconhecível em tamanhos pequenos (16x16)
```

#### 🎯 Rationale: Por Quê Ícones São Obrigatórios

1. **Profissionalismo**: Projetos sem ícone parecem incompletos/amadores
2. **Identidade Visual**: Usuários reconhecem o app pelo ícone (branding)
3. **Experiência do Usuário**: Ícone ajuda a localizar o app entre várias abas/janelas
4. **Requisitos de Plataforma**: App stores (iOS/Android) EXIGEM ícones
5. **PWA**: Navegadores solicitam ícones para instalação
6. **Organização**: Facilita encontrar e gerenciar assets visuais
7. **Rastreabilidade**: Documentar fonte garante conformidade de licença

#### 🚨 Erros Comuns a Evitar

❌ **Não Fazer**:
- Deixar ícone na raiz do projeto (ex: `favicon.ico` solto)
- Usar ícone de baixa resolução (pixelado quando ampliado)
- Esquecer de referenciar no HTML/código
- Usar ícone com copyright sem permissão
- Criar apenas um tamanho (navegadores precisam de múltiplos)

✅ **Fazer**:
- Organizar em pasta dedicada (`assets/icons/`)
- Gerar múltiplos tamanhos (16, 32, 192, 512 px)
- Validar que ícone aparece corretamente
- Documentar fonte se ícone de terceiros
- Usar formato vetorial (SVG) quando possível

#### 📚 Recursos Úteis

**Geradores de Ícone Online** (gratuitos):
- [Favicon.io](https://favicon.io/) - Gera favicon de texto/imagem/emoji
- [RealFaviconGenerator](https://realfavicongenerator.net/) - Gera todos os formatos
- [Favicon Generator](https://www.favicon-generator.org/) - Simples e rápido

**Bancos de Ícones Gratuitos**:
- [Heroicons](https://heroicons.com/) - MIT License
- [Lucide Icons](https://lucide.dev/) - ISC License
- [Tabler Icons](https://tabler-icons.io/) - MIT License
- [Iconoir](https://iconoir.com/) - MIT License
- [Bootstrap Icons](https://icons.getbootstrap.com/) - MIT License

**Ferramentas de Conversão**:
- [ImageMagick](https://imagemagick.org/) - CLI universal
- [Pillow (Python)](https://pillow.readthedocs.io/) - Biblioteca de imagens
- [Sharp (Node.js)](https://sharp.pixelplumbing.com/) - Alto desempenho

#### 📝 Exemplo de Documentação no README

```markdown
## 🎨 Ícone do Projeto

**Fonte**: Criado pela IA usando iniciais do projeto  
**Licença**: Livre para uso (gerado para este projeto)  
**Localização**: `assets/icons/`

### Formatos Disponíveis
- `icon.svg` - Vetorial (preferido)
- `favicon.ico` - Navegadores (16, 32, 48 px)
- `icon-192.png` - PWA/Android
- `icon-512.png` - PWA/Android
- `apple-touch-icon.png` - iOS

### Cores
- Principal: `#4F46E5` (Azul Índigo)
- Texto: `#FFFFFF` (Branco)
```

#### ⏱️ Tempo Estimado

- **Criar ícone simples (IA)**: 5-10 minutos
- **Baixar e adaptar ícone**: 10-15 minutos
- **Converter para formatos necessários**: 5-10 minutos
- **Integrar no projeto**: 5-10 minutos
- **TOTAL**: 15-30 minutos

**Investimento pequeno, impacto grande na percepção de qualidade do projeto.**

---

### 6️⃣.7️⃣ **Scripts de Execução para Facilitar o Uso** [RECOMENDADO]

> **RECOMENDAÇÃO PARA IAs**: Quando se trata de um aplicativo ou programa escrito com uma linguagem de programação que é executável, é recomendado criar scripts em batch para Windows, Linux e Mac acessíveis na pasta principal ou diretório raiz, a fim de facilitar a execução do aplicativo.

**Quando Aplicar**: Durante a implementação (Etapa 6), especialmente após configurar a estrutura básica do projeto executável.

#### 📋 Contexto e Propósito

Scripts de execução na raiz do projeto facilitam significativamente o uso da aplicação, especialmente:
- ✅ **Desenvolvimento**: Acelera ciclo de desenvolvimento (executar sem configurar ambiente manualmente)
- ✅ **Onboarding**: Novos desenvolvedores conseguem rodar projeto imediatamente
- ✅ **Testes**: Facilita execução de testes e validação
- ✅ **Produção**: Em alguns casos, pode simplificar deployment (se não houver alternativas melhores como Docker, systemd, etc.)

#### 🎯 Quando Criar Scripts de Execução

**✅ CRIAR scripts SE:**
- ✅ Aplicação é executável (não é biblioteca)
- ✅ Requer configuração de ambiente (variáveis, paths, dependências)
- ✅ Tem múltiplos comandos de inicialização
- ✅ Precisa de setup antes de executar (migrations, build, etc.)
- ✅ Time/usuários precisam executar frequentemente

**❌ NÃO criar scripts SE:**
- ❌ Aplicação já tem CLI nativo bem documentado
- ❌ Usa ferramentas padrão da linguagem (npm start, cargo run, etc.)
- ❌ Deployment usa orquestração (Docker, Kubernetes) - scripts ficam no Dockerfile
- ❌ Projeto é biblioteca/framework (não executável)

#### 📝 Estrutura de Pastas Recomendada

```
projeto/
├── run.bat                 # ✅ Windows (execução principal)
├── run.sh                  # ✅ Linux/Mac (execução principal)
├── dev.bat                 # 🔄 Desenvolvimento Windows (opcional)
├── dev.sh                  # 🔄 Desenvolvimento Linux/Mac (opcional)
├── test.bat                # 🧪 Testes Windows (opcional)
├── test.sh                 # 🧪 Testes Linux/Mac (opcional)
├── build.bat               # 🏗️ Build Windows (opcional)
├── build.sh                # 🏗️ Build Linux/Mac (opcional)
└── README.md               # Documentação de uso dos scripts
```

**Regra de Ouro**: Scripts na raiz do projeto = acesso fácil. Scripts complexos podem ficar em `scripts/` com wrappers simples na raiz.

#### 💻 Exemplos de Scripts por Linguagem

##### **Python**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Script de execução para Linux/Mac

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando aplicação Python...${NC}"

# Verificar se ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Ambiente virtual não encontrado. Criando...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar/atualizar dependências
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}📦 Instalando dependências...${NC}"
    pip install -q -r requirements.txt
fi

# Executar aplicação
echo -e "${GREEN}✅ Executando aplicação...${NC}"
python src/main.py "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Script de execução para Windows

echo 🚀 Iniciando aplicação Python...

REM Verificar se ambiente virtual existe
if not exist "venv\" (
    echo ❌ Ambiente virtual não encontrado. Criando...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Instalar/atualizar dependências
if exist "requirements.txt" (
    echo 📦 Instalando dependências...
    pip install -q -r requirements.txt
)

REM Executar aplicação
echo ✅ Executando aplicação...
python src\main.py %*
```

##### **Node.js**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Script de execução para Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando aplicação Node.js...${NC}"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}📦 Instalando dependências...${NC}"
    npm install
fi

# Executar aplicação
echo -e "${GREEN}✅ Executando aplicação...${NC}"
npm start "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Script de execução para Windows

echo 🚀 Iniciando aplicação Node.js...

REM Verificar se node_modules existe
if not exist "node_modules\" (
    echo 📦 Instalando dependências...
    call npm install
)

REM Executar aplicação
echo ✅ Executando aplicação...
npm start %*
```

##### **Java**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Script de execução para Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando aplicação Java...${NC}"

# Compilar se necessário
if [ ! -d "target" ]; then
    echo -e "${GREEN}🏗️ Compilando projeto...${NC}"
    mvn clean package -DskipTests
fi

# Executar JAR
echo -e "${GREEN}✅ Executando aplicação...${NC}"
java -jar target/myapp.jar "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Script de execução para Windows

echo 🚀 Iniciando aplicação Java...

REM Compilar se necessário
if not exist "target\" (
    echo 🏗️ Compilando projeto...
    call mvn clean package -DskipTests
)

REM Executar JAR
echo ✅ Executando aplicação...
java -jar target\myapp.jar %*
```

##### **Go**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Script de execução para Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando aplicação Go...${NC}"

# Baixar dependências se necessário
if [ ! -f "go.sum" ]; then
    echo -e "${GREEN}📦 Baixando dependências...${NC}"
    go mod download
fi

# Executar aplicação
echo -e "${GREEN}✅ Executando aplicação...${NC}"
go run cmd/main.go "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Script de execução para Windows

echo 🚀 Iniciando aplicação Go...

REM Baixar dependências se necessário
if not exist "go.sum" (
    echo 📦 Baixando dependências...
    go mod download
)

REM Executar aplicação
echo ✅ Executando aplicação...
go run cmd\main.go %*
```

##### **Rust**

**run.sh (Linux/Mac)**:
```bash
#!/bin/bash
# Script de execução para Linux/Mac

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Iniciando aplicação Rust...${NC}"

# Compilar e executar
echo -e "${GREEN}✅ Executando aplicação (cargo run)...${NC}"
cargo run --release "$@"
```

**run.bat (Windows)**:
```batch
@echo off
REM Script de execução para Windows

echo 🚀 Iniciando aplicação Rust...

REM Compilar e executar
echo ✅ Executando aplicação (cargo run)...
cargo run --release %*
```

#### 🔧 Scripts Adicionais Úteis

##### **Script de Desenvolvimento** (modo watch/reload)

**dev.sh**:
```bash
#!/bin/bash
# Modo desenvolvimento com auto-reload

echo "🔄 Iniciando em modo desenvolvimento..."

# Python
# pip install watchdog
# watchmedo auto-restart --directory=./src --pattern=*.py python src/main.py

# Node.js
# npm run dev  # nodemon ou similar

# Go
# go install github.com/cosmtrek/air@latest
# air

# Rust
# cargo install cargo-watch
# cargo watch -x run
```

##### **Script de Testes**

**test.sh**:
```bash
#!/bin/bash
# Executar testes

echo "🧪 Executando testes..."

# Python
# pytest tests/ -v

# Node.js
# npm test

# Java
# mvn test

# Go
# go test ./...

# Rust
# cargo test
```

#### 📋 Checklist de Scripts de Execução

```markdown
## Checklist de Scripts - Projeto [Nome]

### Scripts Criados
- [ ] **run.sh** (Linux/Mac) - Script principal de execução
- [ ] **run.bat** (Windows) - Script principal de execução
- [ ] Permissões de execução configuradas (`chmod +x *.sh`)
- [ ] Scripts testados em cada plataforma

### Scripts Opcionais (conforme necessidade)
- [ ] **dev.sh/dev.bat** - Modo desenvolvimento com auto-reload
- [ ] **test.sh/test.bat** - Executar testes automatizados
- [ ] **build.sh/build.bat** - Compilar/build do projeto
- [ ] **install.sh/install.bat** - Instalar dependências
- [ ] **clean.sh/clean.bat** - Limpar artifacts de build

### Documentação
- [ ] README.md atualizado com instruções de uso dos scripts
- [ ] Exemplos de uso documentados
- [ ] Requisitos de sistema documentados (Python 3.9+, Node 18+, etc.)
- [ ] Troubleshooting básico incluído

### Funcionalidades dos Scripts
- [ ] Verificam se dependências estão instaladas
- [ ] Criam ambiente virtual/diretórios se necessário
- [ ] Mensagens de output claras e informativas
- [ ] Suportam passagem de argumentos (`./run.sh --help`)
- [ ] Tratam erros graciosamente
- [ ] Incluem cores no output (opcional, melhora UX)
```

#### 📝 Exemplo de Documentação no README

```markdown
## 🚀 Como Executar

### Requisitos
- Python 3.9+ (ou Node.js 18+, Java 17+, etc.)
- Git

### Execução Rápida

**Linux/Mac**:
```bash
./run.sh
```

**Windows**:
```batch
run.bat
```

### Scripts Disponíveis

| Script | Descrição | Plataforma |
|--------|-----------|------------|
| `run.sh` / `run.bat` | Executa a aplicação principal | Linux/Mac / Windows |
| `dev.sh` / `dev.bat` | Modo desenvolvimento (auto-reload) | Linux/Mac / Windows |
| `test.sh` / `test.bat` | Executa testes automatizados | Linux/Mac / Windows |
| `build.sh` / `build.bat` | Compila/builda o projeto | Linux/Mac / Windows |

### Argumentos

Passar argumentos para aplicação:
```bash
./run.sh --port 8080 --debug
```

### Troubleshooting

**Erro: Permission denied (Linux/Mac)**
```bash
chmod +x run.sh dev.sh test.sh build.sh
```

**Erro: Dependências não encontradas**
- Scripts instalam dependências automaticamente na primeira execução
- Se falhar, execute manualmente: `pip install -r requirements.txt` (Python) ou `npm install` (Node.js)
```

#### ⏱️ Tempo Estimado

- **Criar scripts básicos (run.sh/run.bat)**: 10-15 minutos
- **Adicionar scripts opcionais (dev, test, build)**: 5-10 minutos cada
- **Documentar no README**: 10-15 minutos
- **Testar em múltiplas plataformas**: 10-20 minutos
- **TOTAL**: 30-60 minutos

**Investimento: ~30-60 minutos. Benefício: Economiza horas de setup para cada desenvolvedor e usuário.**

#### 🎯 Rationale: Por Quê Scripts de Execução São Importantes

1. **Developer Experience (DX)**: Novo desenvolvedor clona repo, executa `./run.sh` e aplicação funciona
2. **Redução de Fricção**: Sem necessidade de ler documentação complexa para rodar projeto
3. **Consistência**: Todos executam da mesma forma, reduz "funciona na minha máquina"
4. **Automação**: Scripts podem configurar ambiente automaticamente (criar venv, instalar deps)
5. **Documentação Viva**: Scripts servem como documentação executável do processo de inicialização
6. **Onboarding**: Acelera entrada de novos membros no time
7. **CI/CD**: Scripts podem ser reutilizados em pipelines
8. **Cross-Platform**: Suporte explícito para Windows, Linux e Mac

#### ⚠️ Quando NÃO Usar Scripts na Raiz

**Use alternativas melhores quando disponíveis:**
- 🐳 **Docker/Docker Compose**: Para apps com múltiplas dependências (bancos, filas, etc.)
- 📦 **Package Managers Nativos**: `npm start`, `cargo run`, `go run` já são suficientes
- 🎯 **Task Runners**: Makefile, Just, Task para projetos complexos
- ☸️ **Orquestração**: Kubernetes, systemd para produção enterprise

**Combinação Recomendada**:
```
projeto/
├── docker-compose.yml      # 🐳 Para ambiente completo
├── Makefile                # 🎯 Para comandos complexos
├── run.sh                  # ✅ Wrapper simples que chama Make/Docker
└── README.md               # 📚 Documenta quando usar cada um
```

**Exemplo de wrapper**:
```bash
#!/bin/bash
# run.sh - Wrapper simples

if command -v docker &> /dev/null; then
    echo "🐳 Docker detectado, usando docker-compose..."
    docker-compose up
else
    echo "⚠️ Docker não encontrado, executando localmente..."
    make run
fi
```

---

### 7️⃣ **Verificar Implementação CLI + Revisão de Código**
- **CRÍTICO**: Verificar se a nova funcionalidade está disponível via **CLI (Command Line Interface)**
- **IMPORTANTE**: Durante a verificação, aplicar os **9 Critérios de Qualidade** ao código CLI
- Não basta implementar GUI, funcionalidades importantes devem ter **interface CLI** para automação
- Verificar subcomandos, argumentos, help text, integração e qualidade do código

**Checklist de Implementação CLI**:

1. **Import Correto no app.py**:
   ```python
   # ✅ Verificar se módulo foi importado
   from .gui import (
       ComponentJ, ComponentK, ComponentI,
       ComponentC, ComponentD, ComponentA,
       ComponentB, ComponentF, ComponentG, ComponentH,
       ComponentE, NewComponent  # ← NOVO módulo deve estar aqui
   )
   ```

2. **Export no __init__.py do Módulo**:
   ```python
   # src/gui/__init__.py
   from .text_to_data_dock import NewComponent
   
   __all__ = [
       'ComponentJ', 'ComponentK', 'ComponentI',
       'ComponentC', 'ComponentD', 'ComponentA',
       'ComponentB', 'ComponentF', 'ComponentG', 'ComponentH',
       'ComponentE', 'NewComponent'  # ← NOVO módulo exportado
   ]
   ```

3. **Menu Item Criado e Conectado**:
   ```python
   # Em _build_menu() ou similar
   m_tools = bar.addMenu(tr("menu.tools"))
   
   # Criar QAction
   self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
   
   # Adicionar ao menu
   m_tools.addAction(self.act_open_new_component)
   
   # Conectar signal
   self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
   ```

4. **Dock Inicializado no __init__() ou método de setup**:
   ```python
   # Em __init__() da MainWindow
   def __init__(self):
       super().__init__()
       # ... outros docks ...
       self._open_new_component()  # ← Inicializar dock
   
   def _open_new_component(self):
       self.dock_new_component = NewComponent(self)
       self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
       self.addDockWidget(Qt.RightDockWidgetArea, self.dock_new_component)
       self.dock_new_component.hide()
   ```

5. **Signals Conectados** (se aplicável):
   ```python
   # Conectar signals customizados
   self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
   
   def _load_data_from_source(self, data_str: str):
       """Callback para abrir DATA no editor"""
       if not hasattr(self, 'component_viewer'):
           self._open_component()
       self.component_viewer.load_data_string(data_str)
       self.component_viewer.show()
   ```

6. **Traduções i18n Adicionadas**:
   ```data
   // src/i18n/en.data
   {
     "menu.tools.text_to_data": "Text to DATA Converter"
   }
   
   // src/i18n/pt_BR.data
   {
     "menu.tools.text_to_data": "Conversor de Texto para DATA"
   }
   ```

**Checklist de Teste de Integração**:
- ✅ **Menu acessível**: Verificar se item aparece no menu Tools
- ✅ **Dock abre**: Clicar no menu deve abrir o dock corretamente
- ✅ **Funcionalidade básica**: Testar conversão simples
- ✅ **Signals funcionam**: Testar integração com outros componentes (ex: Open in Editor)
- ✅ **Sem erros no console**: Não deve haver ImportError, AttributeError, etc.
- ✅ **Tradução funcionando**: Menu em PT-BR deve mostrar texto traduzido

**Exemplo Real (Task Example - Text to DATA Converter)**:
```python
✅ Import: from .gui import NewComponent
✅ Export: __all__ = [..., 'NewComponent']
✅ Menu: self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
✅ Init: self._open_new_component() chamado em __init__()
✅ Signal: open_in_other_component_requested.connect(self._load_data_from_source)
✅ i18n: EN "Text to DATA Converter", PT-BR "Conversor de Texto para DATA"
✅ Teste: Menu abre dock, conversão funciona, signal para editor OK
```

**Perguntas para Validar Integração**:
1. ❓ "O novo módulo está importado no arquivo principal (app.py)?"
2. ❓ "O módulo está exportado no __init__.py da pasta?"
3. ❓ "Há um item de menu para acessar a funcionalidade?"
4. ❓ "O item de menu está conectado ao método correto?"
5. ❓ "O dock/componente é inicializado no startup da aplicação?"
6. ❓ "Signals customizados estão conectados?"
7. ❓ "Traduções foram adicionadas (EN e PT-BR)?"
8. ❓ "A funcionalidade está acessível sem erros?"

**Por quê?**: Garantir que o código implementado está **realmente utilizável** pelo usuário final, não apenas "funciona isoladamente".

---

### 8️⃣ **Verificar Implementação GUI + Revisão de Código**
- **CRÍTICO**: Verificar se os componentes estão **integrados ao programa principal** e acessíveis
- **IMPORTANTE**: Durante a verificação, aplicar os **9 Critérios de Qualidade** ao código GUI
- Não basta implementar o módulo/dock, ele precisa estar **acessível e funcional** no app
- Verificar menu, imports, inicialização, conexões e qualidade do código

**Parte A - Verificação Funcional GUI (Integração)**:

1. **Import Correto no app.py**:
   ```python
   # ✅ Verificar se módulo foi importado
   from .gui import (
       ComponentJ, ComponentK, ComponentI,
       ComponentC, ComponentD, ComponentA,
       ComponentB, ComponentF, ComponentG, ComponentH,
       ComponentE, NewComponent  # ← NOVO módulo deve estar aqui
   )
   ```

2. **Export no __init__.py do Módulo**:
   ```python
   # src/gui/__init__.py
   from .text_to_data_dock import NewComponent
   
   __all__ = [
       'ComponentJ', 'ComponentK', 'ComponentI',
       'ComponentC', 'ComponentD', 'ComponentA',
       'ComponentB', 'ComponentF', 'ComponentG', 'ComponentH',
       'ComponentE', 'NewComponent'  # ← NOVO módulo exportado
   ]
   ```

3. **Menu Item Criado e Conectado**:
   ```python
   # Em _build_menu() ou similar
   m_tools = bar.addMenu(tr("menu.tools"))
   
   # Criar QAction
   self.act_open_new_component = QAction(tr("menu.tools.text_to_data"), self)
   
   # Adicionar ao menu
   m_tools.addAction(self.act_open_new_component)
   
   # Conectar signal
   self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
   ```

4. **Dock Inicializado no __init__() ou método de setup**:
   ```python
   # Em __init__() da MainWindow
   def __init__(self):
       super().__init__()
       # ... outros docks ...
       self._open_new_component()  # ← Inicializar dock
   
   def _open_new_component(self):
       self.dock_new_component = NewComponent(self)
       self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
       self.addDockWidget(Qt.RightDockWidgetArea, self.dock_new_component)
       self.dock_new_component.hide()
   ```

5. **Signals Conectados** (se aplicável):
   ```python
   # Conectar signals customizados
   self.dock_new_component.open_in_other_component_requested.connect(self._load_data_from_source)
   
   def _load_data_from_source(self, data_str: str):
       """Callback para abrir DATA no editor"""
       if not hasattr(self, 'component_viewer'):
           self._open_component()
       self.component_viewer.load_data_string(data_str)
       self.component_viewer.show()
   ```

6. **Traduções i18n Adicionadas**:
   ```data
   // src/i18n/en.data
   {
     "menu.tools.text_to_data": "Text to DATA Converter"
   }
   
   // src/i18n/pt_BR.data
   {
     "menu.tools.text_to_data": "Conversor de Texto para DATA"
   }
   ```

**Checklist de Teste de Integração GUI**:
- ✅ **Menu acessível**: Verificar se item aparece no menu Tools
- ✅ **Dock abre**: Clicar no menu deve abrir o dock corretamente
- ✅ **Funcionalidade básica**: Testar conversão simples
- ✅ **Signals funcionam**: Testar integração com outros componentes (ex: Open in Editor)
- ✅ **Sem erros no console**: Não deve haver ImportError, AttributeError, etc.
- ✅ **Tradução funcionando**: Menu em PT-BR deve mostrar texto traduzido

**Parte B - Revisão de Qualidade do Código GUI (9 Critérios)**:

Durante a verificação do GUI, aplicar simultaneamente os seguintes critérios:

1. **❌ Omissão** - Verificar se GUI está completo:
   - [ ] Todos os widgets/controles necessários implementados?
   - [ ] Tratamento de erros em handlers (ex: FileNotFoundError)?
   - [ ] Cleanup de recursos (fechar arquivos, desconectar signals)?
   - [ ] Feedback visual para operações longas (QProgressBar, cursor busy)?

2. **🤔 Ambiguidade** - GUI deve ser claro:
   - [ ] Labels descritivos e claros?
   - [ ] Tooltips informativos nos controles?
   - [ ] Mensagens de erro descritivas (QMessageBox)?
   - [ ] Nomes de métodos intuitivos (_on_button_clicked vs _handle)?

3. **❗ Fato Incorreto** - Lógica GUI correta:
   - [ ] Signals conectados aos slots corretos?
   - [ ] Layouts corretos (QVBoxLayout, QHBoxLayout, QSplitter)?
   - [ ] Enable/disable de controles conforme estado?
   - [ ] Validação de entrada correta (QValidator)?

4. **♻️ Redundância** - Evitar repetição no GUI:
   - [ ] Widgets criados uma única vez?
   - [ ] Validações centralizadas (não duplicadas)?
   - [ ] Código de inicialização não repetido?

5. **⚠️ Inconsistência** - Padrão GUI consistente:
   - [ ] Nomenclatura uniforme (ed_ para QLineEdit, btn_ para QPushButton)?
   - [ ] Estilo de mensagens consistente?
   - [ ] Layout spacing/margin consistente?

6. **🔗 Falta de Integração** - GUI conectado:
   - [ ] Dock adicionado à MainWindow?
   - [ ] Menu item conectado ao dock.show()?
   - [ ] Signals customizados conectados?
   - [ ] Import presente em app.py?

7. **🧩 Menor Coesão** - Dock focado:
   - [ ] Dock faz apenas UI (não lógica de negócio)?
   - [ ] Lógica complexa em módulo separado?
   - [ ] Cada método tem responsabilidade única?

8. **🔗 Maior Acoplamento** - GUI desacoplado:
   - [ ] Dock não depende de implementação interna de outros docks?
   - [ ] Comunicação via signals/slots (não chamadas diretas)?
   - [ ] GUI testável independentemente (mock de lógica)?

9. **🗑️ Informação Estranha** - Código limpo:
   - [ ] Sem print() debug esquecidos?
   - [ ] Sem TODOs não resolvidos?
   - [ ] Sem widgets não utilizados?

**Exemplo de Revisão GUI Aplicada**:
```python
# ❌ ANTES - Omissão, Ambiguidade, Maior Acoplamento
class NewComponent(QDockWidget):
    def __init__(self):
        self.btn = QPushButton("Convert")  # Label vago
        self.btn.clicked.connect(self.convert)  # Sem tratamento de erro
    
    def convert(self):
        data = open(self.ed_file.text()).read()  # Sem validação, sem fechar
        data_str = my_convert(data)  # Lógica de negócio no GUI
        print(data_str)  # Debug esquecido

# ✅ DEPOIS - Completo, Claro, Desacoplado
class NewComponent(BaseDock):
    """Text to DATA Converter dock widget."""
    
    # Signal para comunicação
    open_in_other_component_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_widgets()
        self._setup_layout()
        self._connect_signals()
        
        # Controller para lógica de negócio
        self._converter = TextToJsonConverter()
    
    def _create_widgets(self):
        """Create UI widgets."""
        self.ed_file = QLineEdit()
        self.ed_file.setPlaceholderText("Enter file path or paste text")
        
        self.btn_convert = QPushButton("Convert to DATA")
        self.btn_convert.setToolTip("Convert text to DATA format")
        
        self.btn_open_component = QPushButton("Open in Editor")
        self.btn_open_component.setEnabled(False)  # Disabled até converter
    
    def _connect_signals(self):
        """Connect signals to slots."""
        self.btn_convert.clicked.connect(self._on_convert_clicked)
        self.btn_open_component.clicked.connect(self._on_open_component_clicked)
    
    def _on_convert_clicked(self):
        """Handle convert button click."""
        file_path = self.ed_file.text().strip()
        
        if not file_path:
            QMessageBox.warning(self, "Empty Input", "Please enter a file path or text.")
            return
        
        try:
            # Ler arquivo com context manager (garante fechar)
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = file_path  # Tratar como texto direto
            
            # Converter usando controller (desacoplamento)
            self._data_result = self._converter.convert(text)
            
            # Feedback visual
            QMessageBox.information(self, "Success", "Conversion successful!")
            self.btn_open_component.setEnabled(True)
        
        except FileNotFoundError:
            QMessageBox.critical(self, "File Not Found", f"File not found: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"Error: {str(e)}")
    
    def _on_open_component_clicked(self):
        """Handle open in editor button click."""
        if hasattr(self, '_data_result'):
            self.open_in_other_component_requested.emit(self._data_result)  # Signal
```

**Ferramentas Recomendadas GUI**:
```bash
# Verificar imports Qt não utilizados
grep -r "from PySide6" src/gui/ | cut -d: -f2 | sort | uniq

# Verificar signals não conectados (manual review)
grep -r "Signal(" src/gui/ | grep -v ".connect("

# Verificar widgets não utilizados (manual review)
grep -r "self\.\w\+ = Q" src/gui/

# Verificar debug prints (CRÍTICO)
grep -r "print(" src/gui/ --exclude="*_test.py"
```

**Perguntas para Validar GUI**:
1. ❓ "O dock está completamente integrado no menu e MainWindow?"
2. ❓ "Todos os signals estão conectados e funcionando?"
3. ❓ "Há tratamento de erros com feedback visual (QMessageBox)?"
4. ❓ "Lógica de negócio está separada do código GUI?"
5. ❓ "Código está livre de debug prints e TODOs não resolvidos?"
6. ❓ "Labels, tooltips e mensagens são claros e descritivos?"
7. ❓ "Recursos (arquivos, conexões) são fechados corretamente?"

**Exemplo Real (Task Example - Text to DATA Converter)**:
```python
✅ Import: from .gui import NewComponent
✅ Export: __all__ = [..., 'NewComponent']
✅ Menu: self.act_open_new_component.triggered.connect(lambda: self.dock_new_component.show())
✅ Init: self._open_new_component() chamado em __init__()
✅ Signal: open_in_other_component_requested.connect(self._load_data_from_source)
✅ i18n: EN "Text to DATA Converter", PT-BR "Conversor de Texto para DATA"
✅ Revisão: Sem debug prints, tratamento de erros OK, lógica desacoplada
✅ Teste: Menu abre dock, conversão funciona, signal para editor OK
```

---

### 9️⃣ **Verificar Integração com Programa Principal**
- **CRÍTICO**: Após implementar CLI e GUI, **verificar se tudo está integrado e funcionando no contexto do programa principal**
- Não basta ter código funcionando isoladamente, precisa estar **acessível e operacional** no aplicativo
- Verificar fluxo completo: menu → ação → resultado
- Testar manualmente a funcionalidade no programa rodando

**Checklist de Integração Completa**:

1. **Teste de Fluxo Completo GUI**:
   ```bash
   # Iniciar aplicativo
   python -m app --gui
   
   # Testar manualmente:
   [ ] Menu item aparece corretamente?
   [ ] Clicar no menu abre o dock?
   [ ] Dock exibe todos os controles?
   [ ] Funcionalidade básica funciona (conversão, busca, etc)?
   [ ] Signals entre componentes funcionam (ex: "Open in Editor")?
   [ ] Mensagens de erro aparecem quando apropriado?
   [ ] Tradução i18n funciona (mudar idioma e verificar)?
   ```

2. **Teste de Fluxo Completo CLI**:
   ```bash
   # Testar help
   python -m app convert --help
   
   # Testar funcionalidade
   python -m app convert test.txt --pretty -o output.data
   
   # Testar pipes
   echo "name: John" | python -m app convert -
   
   # Verificar:
   [ ] Help text aparece?
   [ ] Argumentos são reconhecidos?
   [ ] Funcionalidade executa sem erros?
   [ ] Output está correto?
   [ ] Exit codes corretos (0=success, 1=error)?
   ```

3. **Teste de Integração entre Componentes**:
   ```bash
   # Exemplo: Converter texto → Abrir no editor
   [ ] Clicar em "Open in Editor" no Text to DATA Converter abre o Editor?
   [ ] DATA é carregado corretamente no Editor?
   [ ] Editor pode salvar o resultado?
   
   # Exemplo: Busca → Abrir arquivo
   [ ] Clicar em resultado de busca abre arquivo correto?
   [ ] Posição do cursor vai para linha correta?
   ```

4. **Teste de Robustez**:
   ```bash
   # Cenários de erro
   [ ] Arquivo não encontrado exibe mensagem clara?
   [ ] Input inválido é tratado graciosamente?
   [ ] Operação cancelada não deixa estado inconsistente?
   [ ] Recursos são liberados corretamente (arquivos fechados, memória)?
   ```

5. **Teste de Performance** (se aplicável):
   ```bash
   # Arquivos grandes
   [ ] Processa arquivos >10MB sem travar?
   [ ] Interface permanece responsiva durante operação longa?
   [ ] Progress bar/feedback visual funciona?
   [ ] Cancelamento funciona durante operação longa?
   ```

**Exemplo Real de Problema de Integração**:
```python
# ❌ PROBLEMA ENCONTRADO NA INTEGRAÇÃO:
# Task Example - Text to DATA Converter CLI
# Problema: Extractor() estava sendo chamado sem 3 parâmetros obrigatórios

# ANTES (quebrava na integração):
def main():
    if args.command == 'convert':
        extractor = Extractor()  # ❌ TypeError: missing 3 required arguments

# DEPOIS (corrigido):
def main():
    if args.command == 'convert':
        extractor = Extractor(
            avoid_keys="",
            avoid_keys_parameter="equals",
            with_quotation_marks=False
        )  # ✅ Funciona!
```

**Perguntas para Validar Integração**:
1. ❓ "O usuário final consegue acessar a funcionalidade facilmente?"
2. ❓ "Todos os fluxos de uso funcionam end-to-end?"
3. ❓ "Há algum erro ou warning no console durante uso normal?"
4. ❓ "A funcionalidade está consistente com o resto do aplicativo?"
5. ❓ "Documentação (help text, tooltips) está clara e correta?"

**Por quê esta etapa é crítica?**:
- ✅ Detecta problemas que testes unitários não pegam
- ✅ Valida experiência real do usuário
- ✅ Garante que todo o trabalho é realmente utilizável
- ✅ Evita surpresas após commit (código testado ≠ código integrado)

---

### 🔟 **Fazer Testes**
- **Obrigatório**: Testes unitários para cada função pública
- **Meta**: 100% de cobertura das funcionalidades implementadas
- **Ferramentas**: `unittest` (nativo) ou `pytest`
- **CRÍTICO**: Testar o sistema **após integração** (GUI + CLI integrados)
- **IMPORTANTE**: Executar **APÓS** revisão de código (Etapas 7 e 8)

**Categorias de Testes**:
1. **Happy Path**: Casos normais de uso
2. **Edge Cases**: Valores vazios, None, strings longas
3. **Error Handling**: Exceções esperadas
4. **Integration**: Fluxo completo (incluindo integração GUI/CLI)
5. **Quality Validation**: Testes que validam ausência dos 9 problemas das Etapas 7 e 8

**Exemplo Task Example**:
```python
✅ test_extract_from_dict_simple()
✅ test_extract_from_obj_type()
✅ test_simple_substitution_same_value()
✅ test_different_values_no_substitution()
✅ test_apply_substitutions_tsx_file()
✅ test_update_multiple_files()
# ... 12 testes no total (100% passing)
```

**Por quê testar DEPOIS da integração e revisão?**:
- Garante que testes validam o **sistema integrado**, não componentes isolados
- Detecta problemas de integração durante os testes
- Valida que features realmente funcionam no contexto do aplicativo
- Evita falsos positivos (testes passam mas feature não está acessível)
- Código já foi revisado, então testes validam **código de qualidade**

**Por quê?**: Garantir qualidade, evitar regressões, facilitar manutenção futura.

---

#### 🛡️ **Etapa 9.1 - Segurança em Testes (CRÍTICO)**

**Problema Identificado** (Task Example - 01/12/2025):
- Testes GUI travaram em **loop infinito** por >1 hora sem timeout
- Nenhuma detecção automática de deadlock ou travamento
- Testes aguardavam display X11 inexistente (ambiente headless)

**Soluções Obrigatórias**:

1. **⏱️ Timeout Máximo Obrigatório** (30s por teste):
   ```bash
   # SEMPRE usar timeout em testes
   pytest tests/test_*.py --timeout=30 -v
   
   # Instalar plugin pytest-timeout se necessário
   pip install pytest-timeout
   ```

2. **🚨 Detecção de Loop Infinito** (warning em 10s):
   ```bash
   # Timeout mais agressivo para detectar loops
   timeout 10s pytest tests/test_specific.py || echo "⚠️ TIMEOUT: Possível loop infinito detectado!"
   ```

3. **🖥️ Ambiente Headless Obrigatório** (testes GUI sem display):
   ```bash
   # Usar Qt offscreen platform
   QT_QPA_PLATFORM=offscreen pytest tests/test_gui_*.py -v --timeout=30
   
   # OU usar pytest-xvfb para ambiente virtual X11
   pip install pytest-xvfb
   pytest tests/test_gui_*.py --xvfb-backend xvfb --timeout=30
   ```

4. **✅ Dry-Run Obrigatório** (antes de executar):
   ```bash
   # 1. Verificar sintaxe
   python -m py_compile tests/test_*.py && echo "✅ Sintaxe válida"
   
   # 2. Verificar imports
   python -c "from tests.test_module import *; print('✅ Imports OK')"
   
   # 3. Listar testes sem executar
   pytest tests/test_*.py --collect-only
   ```

5. **⏲️ Monitoramento de Tempo** (registrar duração):
   ```bash
   # Medir tempo total e salvar log
   time pytest tests/test_*.py -v --timeout=30 | tee test_output.log
   
   # Usar pytest-benchmark para métricas
   pytest tests/test_*.py --benchmark-only --timeout=30
   ```

**Por quê?**: Evitar travamentos infinitos, proteger tempo de desenvolvimento, garantir testes confiáveis.

---

### 🔟.5️⃣ **Profiling e Otimização** [OPCIONAL]

**Quando Usar**: Feature crítica está **lenta** (>1s para usuário).

**Ferramentas**:
```bash
# CPU profiling
python -m cProfile -s cumulative app.py > profile.txt

# Memory profiling
pip install memory_profiler
python -m memory_profiler app.py
```

**Exemplo**:
```python
# ❌ LENTO - O(n²) 5.2s para 1000 tasks
def find_duplicates_slow(tasks):
    for i, t1 in enumerate(tasks):
        for j, t2 in enumerate(tasks):
            if i != j and t1.title == t2.title:
                # duplicado

# ✅ RÁPIDO - O(n) 0.02s (260x faster)
def find_duplicates_fast(tasks):
    seen = {}
    for task in tasks:
        if task.title in seen:
            # duplicado
        seen[task.title] = task
```

**Quando Parar**: Otimizar só vale se **tempo salvo × frequência** > 1min/dia.

📘 **Detalhes**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 10.5

---

### 🔟.6️⃣ **CI/CD Quality Gates** ⭐ [OBRIGATÓRIO]

> **CRÍTICO PARA PRODUÇÃO**: Esta etapa é **OBRIGATÓRIA** no Simplicidade 3.

**Por quê obrigatório**:
- ✅ **Memória falha**: Você esquece de rodar testes manualmente
- ✅ **Automação 24/7**: CI valida **todo** commit automaticamente
- ✅ **Confiança**: Sabe que código quebrado não vai para produção
- ✅ **Rápido**: Feedback em minutos (não horas debugando)

**Pre-commit Hooks** (validação local):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-data
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        args: ['tests/', '-v']
```

```bash
# Instalar
pip install pre-commit
pre-commit install

# Agora todo `git commit` executa validações automaticamente
# Se falhar, commit é BLOQUEADO até corrigir
```

**GitHub Actions** (CI pipeline):

```yaml
# .github/workflows/ci.yml
name: CI Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install deps
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black bandit
    
    - name: Black formatting
      run: black --check .
    
    - name: Flake8 linting
      run: flake8 . --max-line-length=88
    
    - name: Bandit security
      run: bandit -r . -ll
    
    - name: Tests + Coverage
      run: |
        pytest --cov=. --cov-report=term
        coverage report --fail-under=80
      # Falha se cobertura < 80%
```

**GitLab CI**:

```yaml
# .gitlab-ci.yml
stages:
  - test

test:
  image: python:3.11
  script:
    - pip install -r requirements.txt pytest pytest-cov
    - pytest --cov=. --cov-report=term
    - coverage report --fail-under=80
```

**Badge no README** (status visual):

```markdown
[![CI](https://github.com/user/repo/workflows/CI/badge.svg)](https://github.com/user/repo/actions)
[![Coverage](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

**Tempo Setup**: ~30 minutos (uma vez). Depois automático.

📘 **Configurações completas**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 10.6

---

### 1️⃣1️⃣ **Organizar Pasta Raiz do Projeto**
- ✅ Imports validados (módulo carrega sem erros)
- 📝 **Limitação documentada**: Testes GUI requerem ambiente headless não configurado

---

#### 🔬 **Etapa 9.2 - Testes em Threads/Processos com Monitoramento (AVANÇADO)**

**Objetivo**: Controle total sobre execução de testes com possibilidade de **interromper**, **monitorar** e **registrar** progresso em tempo real.

**Quando Usar**:
- Testes GUI que podem travar
- Testes de longa duração (>1 min)
- Testes com dependências externas (rede, banco de dados)
- Necessidade de logging em tempo real
- Necessidade de cancelamento manual durante execução

**Implementação com `multiprocessing.Process`**:

```python
# tests/test_runner_monitored.py
import multiprocessing as mp
import time
import sys
from queue import Empty

def run_tests_in_process(test_module: str, queue: mp.Queue, timeout: int = 30):
    """
    Executa testes em processo separado com logging para queue.
    
    Args:
        test_module: Módulo de teste (ex: 'tests.test_file_list_dock')
        queue: Queue para comunicação de progresso
        timeout: Timeout em segundos
    """
    try:
        import pytest
        
        # Configurar logging em tempo real
        class QueueReporter:
            def __init__(self, queue):
                self.queue = queue
            
            def pytest_runtest_logreport(self, report):
                """Hook do pytest para capturar resultados."""
                if report.when == 'call':
                    status = '✅ PASS' if report.passed else '❌ FAIL'
                    self.queue.put({
                        'type': 'test_result',
                        'test': report.nodeid,
                        'status': status,
                        'duration': report.duration
                    })
        
        # Executar pytest com reporter customizado
        queue.put({'type': 'info', 'msg': f'Iniciando testes: {test_module}'})
        
        result = pytest.main([
            test_module,
            '-v',
            f'--timeout={timeout}',
            '--tb=short',
            '-p', 'no:cacheprovider'  # Desabilitar cache
        ])
        
        queue.put({'type': 'info', 'msg': f'Testes finalizados. Exit code: {result}'})
        queue.put({'type': 'exit', 'code': result})
        
    except Exception as e:
        queue.put({'type': 'error', 'msg': str(e)})
        queue.put({'type': 'exit', 'code': 1})

def monitor_test_execution(test_module: str, max_timeout: int = 300):
    """
    Monitora execução de testes com controle total.
    
    Args:
        test_module: Módulo de teste
        max_timeout: Timeout máximo em segundos (padrão: 5 min)
    
    Returns:
        dict: Resultado da execução com estatísticas
    """
    queue = mp.Queue()
    process = mp.Process(
        target=run_tests_in_process,
        args=(test_module, queue, 30)
    )
    
    print(f"🚀 Iniciando testes: {test_module}")
    print(f"⏱️  Timeout máximo: {max_timeout}s")
    print(f"📊 Monitoramento ativo. Pressione Ctrl+C para cancelar.\n")
    
    process.start()
    start_time = time.time()
    results = {'passed': 0, 'failed': 0, 'tests': []}
    
    try:
        while process.is_alive():
            elapsed = time.time() - start_time
            
            # Verificar timeout global
            if elapsed > max_timeout:
                print(f"\n⚠️  TIMEOUT GLOBAL ({max_timeout}s excedido)")
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                return {'status': 'timeout', 'elapsed': elapsed, 'results': results}
            
            # Ler mensagens da queue (não-bloqueante)
            try:
                msg = queue.get(timeout=0.5)
                
                if msg['type'] == 'test_result':
                    print(f"  {msg['status']} {msg['test']} ({msg['duration']:.2f}s)")
                    results['tests'].append(msg)
                    if '✅' in msg['status']:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                
                elif msg['type'] == 'info':
                    print(f"ℹ️  {msg['msg']}")
                
                elif msg['type'] == 'error':
                    print(f"❌ ERRO: {msg['msg']}")
                
                elif msg['type'] == 'exit':
                    process.join(timeout=2)
                    elapsed = time.time() - start_time
                    print(f"\n✅ Testes finalizados em {elapsed:.2f}s")
                    return {
                        'status': 'completed',
                        'exit_code': msg['code'],
                        'elapsed': elapsed,
                        'results': results
                    }
            
            except Empty:
                # Nenhuma mensagem, continuar monitorando
                pass
            
            # Mostrar progresso a cada 10s
            if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                print(f"⏳ Executando... {int(elapsed)}s ({results['passed']} passed, {results['failed']} failed)")
    
    except KeyboardInterrupt:
        print("\n⚠️  Cancelamento manual (Ctrl+C)")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
        elapsed = time.time() - start_time
        return {'status': 'cancelled', 'elapsed': elapsed, 'results': results}
    
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)

# Exemplo de uso:
if __name__ == '__main__':
    result = monitor_test_execution('tests/test_advanced_file_search.py', max_timeout=300)
    
    print(f"\n{'='*60}")
    print(f"Status: {result['status']}")
    print(f"Tempo: {result['elapsed']:.2f}s")
    print(f"Passed: {result['results']['passed']}")
    print(f"Failed: {result['results']['failed']}")
    print(f"{'='*60}")
```

**Uso Prático**:

```bash
# 1. Criar runner monitorado
cat > tests/run_tests_monitored.py << 'EOF'
# [código acima]
EOF

# 2. Executar com monitoramento
python tests/run_tests_monitored.py

# 3. Cancelar a qualquer momento (Ctrl+C)
# O processo será terminado graciosamente
```

**Vantagens**:
- ✅ **Controle total**: Pode cancelar testes a qualquer momento
- ✅ **Logging em tempo real**: Vê progresso de cada teste
- ✅ **Timeout global + individual**: Dupla proteção
- ✅ **Estatísticas**: Passa/falha em tempo real
- ✅ **Isolamento**: Testes rodam em processo separado (não travam o terminal)
- ✅ **Cleanup garantido**: `terminate()` + `kill()` forçado se necessário

**Configurações Opcionais**:

1. **Logging em Arquivo** (além de stdout):
   ```python
   # Adicionar ao run_tests_in_process:
   import logging
   logging.basicConfig(
       filename=f'test_{time.time()}.log',
       level=logging.INFO,
       format='%(asctime)s - %(message)s'
   )
   ```

2. **Notificação Sonora** (ao finalizar):
   ```python
   import os
   # No final de monitor_test_execution:
   os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
   ```

3. **Integração com CI/CD**:
   ```python
   # Retornar exit code correto:
   sys.exit(0 if result['status'] == 'completed' and result['results']['failed'] == 0 else 1)
   ```

**Checklist Adicional (Etapa 9.2 - Opcional)**:
```
[ ] Criar test_runner_monitored.py com multiprocessing
[ ] Definir timeout global (padrão: 5 min)
[ ] Definir timeout individual por teste (padrão: 30s)
[ ] Implementar logging em tempo real (Queue)
[ ] Testar cancelamento manual (Ctrl+C)
[ ] Verificar cleanup de processos (ps aux | grep pytest)
```

**Quando NÃO usar**:
- Testes simples e rápidos (<10s total)
- Testes sem GUI (backend puro)
- CI/CD com timeout nativo configurado
- Primeira execução de testes (overhead desnecessário)

---

### 1️⃣1️⃣ **Organizar Pasta Raiz do Projeto**
- **CRÍTICO**: Antes da documentação e do commit, **organizar a pasta raiz recursivamente**
- **OBRIGATÓRIO**: Arquivos devem estar organizados nas pastas corretas antes do commit
- Remover arquivos temporários, backups desnecessários
- Verificar se todos os arquivos estão nos lugares corretos
- Limpar cache e arquivos gerados (`__pycache__`, `.pyc`)
- Garantir que `.gitignore` está atualizado

**Checklist de Organização**:
1. **Remoção de Arquivos Temporários**:
   ```bash
   # Remover backups antigos
   rm -f *.backup_* *.bak *~
   
   # Limpar cache Python
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   find . -type f -name "*.pyo" -delete
   ```

2. **Verificação de Estrutura de Diretórios (OBRIGATÓRIO)**:
   - `src/` - código-fonte
   - `tests/` - **TODOS os arquivos de teste** (obrigatório)
   - `docs/` - **TODOS os documentos e arquivos markdown** (obrigatório)
   - Arquivos raiz organizados (README, setup.py, etc.)

3. **Organização Recursiva Obrigatória**:
   
   **⚠️ REGRA FUNDAMENTAL**: 
   > Antes do commit, os arquivos devem ser organizados nas pastas recursivamente. Isto é **obrigatório** para manter o ambiente limpo e organizado.

   **Regras Específicas por Tipo de Arquivo**:
   
   a) **Arquivos de Teste** → `tests/`
      - ✅ `test_*.py`, `*_test.py` → `tests/`
      - ✅ Estrutura de testes deve espelhar estrutura do código
      - ✅ Exemplo: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
   
   b) **Documentos e Markdown** → `docs/`
      - ✅ Todos arquivos `.md` (exceto README.md raiz) → `docs/`
      - ✅ Arquivos de documentação → `docs/`
      - ✅ **Organização recursiva dentro de `docs/`**:
        - `docs/api/` - Documentação de API
        - `docs/tutorials/` - Tutoriais
        - `docs/architecture/` - Decisões arquiteturais
        - `docs/user-guide/` - Guias de usuário
        - `docs/dev-guide/` - Guias de desenvolvimento
        - `docs/decisions/` - Notas de decisão (ver Etapa 11.5)
      - ✅ Criar subpastas que identificam contexto dos arquivos
   
   c) **Código-Fonte** → `src/` ou pasta apropriada
      - ✅ Organizar por módulos/features
      - ✅ Exemplo: `src/core/`, `src/utils/`, `src/api/`

**Exemplo Completo**:
```bash
# ANTES (pasta desorganizada):
├── src/
├── test_utils.py              ❌ teste fora de tests/
├── API_DOCS.md                ❌ doc fora de docs/
├── tutorial.md                ❌ doc fora de docs/
├── apply_v2913_patches.py     ❌ temporário
├── test_temp.py               ❌ teste temporário
├── backup_old/                ❌ backup antigo
├── __pycache__/               ❌ cache
└── file.py.backup_v2913       ❌ backup desnecessário

# DEPOIS (organizado recursivamente):
├── src/
│   ├── core/
│   └── utils/
├── tests/                     ✅ TODOS os testes
│   ├── unit/
│   │   └── test_utils.py     ✅ teste movido
│   └── integration/
├── docs/                      ✅ TODOS os documentos
│   ├── api/
│   │   └── API_DOCS.md       ✅ doc movido
│   ├── tutorials/
│   │   └── tutorial.md       ✅ doc movido
│   └── decisions/             ✅ Notas de decisão
└── README.md                  ✅ README raiz mantido
```

**Por quê?**: Manter repositório limpo, evitar commits de lixo, facilitar navegação, profissionalismo, organização recursiva garante escalabilidade. Documentar o estado **limpo** e **organizado** do projeto.

---

### 1️⃣1️⃣.5️⃣ **Notas de Decisão** [OPCIONAL]

**Quando Usar**: Decisão importante/não-óbvia foi tomada e você pode esquecer o "por quê" depois.

**O quê documentar**:
- ✅ Escolha de biblioteca/framework importante
- ✅ Trade-off significativo (performance vs simplicidade)
- ✅ Decisão de NÃO fazer algo (com rationale)
- ✅ Arquitetura/pattern escolhido

**Formato Simplificado** (ADR light):

```markdown
# Decisão: Usar PyQt6 em vez de Tkinter

**Data**: 2025-01-15
**Status**: ✅ Aceito

**Contexto**: Preciso GUI com dock widgets profissionais.

**Decisão**: Escolhi PyQt6.

**Por quê**:
- ✅ QDockWidget nativo (Tkinter não tem)
- ✅ Styling com QSS (CSS-like)
- ✅ Documentação excelente

**Trade-offs**:
- ❌ Licença GPL (OK, projeto é open-source)
- ❌ Binário maior (~50MB vs ~5MB Tkinter)

**Se mudar no futuro**: Considerar PySide6 (LGPL) se precisar licença permissiva.
```

**Onde guardar**:
```
docs/
├── decisions/
│   ├── 001-pyqt6-choice.md
│   ├── 002-data-storage.md
│   └── README.md
```

**Quando NÃO documentar**:
- ❌ Decisões triviais (naming, formatação)
- ❌ Escolhas óbvias/convencionais
- ❌ Código autoexplicativo

**Tempo**: 5-10 minutos por decisão importante.

📘 **ADR formal com template**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 11.5

---

### 1️⃣2️⃣ **Preencher Nova Documentação**
- **Atualizar arquivo de tarefas/requisitos**: Marcar tasks como `[X]` completas
- **Criar SPECIFICATIONS.md**: Documento detalhado da versão
- **Atualizar estatísticas**: Percentual de conclusão do projeto
- **🤖 [OPCIONAL] Gerenciar recomendações de novas tarefas pela IA**

---

### ⚠️ **REQUISITO OBRIGATÓRIO: Documentação Completa de Todas as Implementações da IA**

> **CRÍTICO PARA IAs**: Tudo aquilo que a inteligência artificial faz no projeto, em cada ciclo de implementação, em cada código, cada funcionalidade implementada, **DEVE SER DOCUMENTADO NA PASTA `docs/` COMO REQUISITO OBRIGATÓRIO** para demarcar as novas funcionalidades e novos comportamentos.

#### **🤖 Regra de Ouro para Assistentes de IA**

**Se você é uma IA implementando código:**
- ✅ **VOCÊ DEVE** documentar TODAS as implementações que realizar em cada ciclo
- ✅ **VOCÊ DEVE** criar/atualizar arquivos na pasta `docs/` para cada funcionalidade nova
- ✅ **VOCÊ DEVE** descrever TODOS os comportamentos novos implementados
- ✅ **VOCÊ DEVE** marcar claramente o que foi adicionado, modificado ou removido
- ✅ **VOCÊ DEVE** incluir exemplos de uso das novas funcionalidades
- ✅ **VOCÊ DEVE** documentar decisões técnicas e arquiteturais tomadas

#### **📝 O Que Deve Ser Documentado (OBRIGATÓRIO)**

Para **CADA ciclo de implementação**, a IA deve documentar na pasta `docs/`:

1. **Funcionalidades Implementadas**:
   - Nome e descrição detalhada de cada nova funcionalidade
   - Propósito e casos de uso
   - Comportamento esperado e edge cases

2. **Código Criado/Modificado**:
   - Arquivos novos criados (path completo + descrição)
   - Arquivos modificados (path + o que foi alterado)
   - Funções/classes principais adicionadas ou modificadas

3. **Arquitetura e Decisões Técnicas**:
   - Padrões de design aplicados (GoF, GRASP)
   - Estrutura de módulos e suas responsabilidades
   - Decisões arquiteturais e suas justificativas
   - **[SIMPLICIDADE 3]** Notas de decisão pragmáticas (ADR simplificado, não formal)

4. **Comportamentos e Integrações**:
   - Como a funcionalidade interage com o resto do sistema
   - Dependências criadas ou modificadas
   - Fluxos de dados e controle

5. **Testes Implementados**:
   - Quantidade e tipos de testes criados
   - Cenários de teste cobertos
   - Cobertura de testes alcançada

6. **Exemplos de Uso**:
   - Como utilizar a nova funcionalidade
   - Exemplos de código (CLI, API, GUI)
   - Casos de uso práticos

7. **[SIMPLICIDADE 3] Documentação Solo em Produção**:
   - Checklist de segurança OWASP preenchido (OBRIGATÓRIO)
   - Planos de rollback documentados (OBRIGATÓRIO)
   - Configuração de CI/CD e quality gates
   - Notas sobre como você resolveu problemas específicos (importante para lembrar depois)

#### **📂 Estrutura Obrigatória de Documentação (Simplicidade 3)**

A pasta `docs/` deve conter no mínimo:

```
docs/
├── REQUIREMENTS.md          # Lista de tarefas e requisitos (atualizado a cada ciclo)
├── vX.Y.Z-SPECIFICATIONS.md # Especificações detalhadas da versão atual
├── CHANGELOG.md             # Histórico de mudanças (o que foi implementado e quando)
├── ARCHITECTURE.md          # Decisões arquiteturais e estrutura do projeto
├── DECISIONS.md             # Notas de decisão técnica (ADR simplificado para solo dev)
├── SECURITY.md              # Checklist OWASP e vulnerabilidades mitigadas (OBRIGATÓRIO)
├── ROLLBACK.md              # Planos de rollback para features críticas (OBRIGATÓRIO)
└── [feature]-GUIDE.md       # Guias específicos para funcionalidades complexas
```

**Criação Automática**:
- Se a pasta `docs/` não existe, ela **DEVE SER CRIADA AUTOMATICAMENTE** pela IA
- Se um arquivo de documentação não existe, ele **DEVE SER CRIADO** pela IA no primeiro ciclo
- Todos os arquivos devem ser atualizados **A CADA CICLO** de implementação

#### **📋 Template Mínimo para SPECIFICATIONS.md (Simplicidade 3)**

Cada arquivo de especificações de versão deve conter no mínimo:

```markdown
# [Nome do Projeto] vX.Y.Z - [Nome Descritivo]

**Data**: DD/MM/AAAA
**Sprint**: X tasks em Y horas
**Metodologia**: Protocolo Simplicidade 3 (Solo Developer em Produção)

## 📋 Objetivos da Sprint
- Task #X: [descrição]
- Task #Y: [descrição]

## 🎯 Funcionalidades Implementadas

### Task #X: [Nome da Funcionalidade]
**Problema Original**:
- [Descrição do problema ou necessidade]

**Solução Implementada**:
- ✅ [Feature/função 1]: [descrição detalhada]
- ✅ [Feature/função 2]: [descrição detalhada]

**Comportamentos Novos**:
- [Comportamento 1]: [como funciona]
- [Comportamento 2]: [como funciona]

**Arquitetura**:
- Padrão [X] aplicado: [justificativa]
- Módulos criados: [lista com responsabilidades]
- Decisão técnica: [breve nota sobre escolha arquitetural importante]

**Arquivos Criados/Modificados**:
- `path/to/file.py` (+XXX linhas) - [descrição]
- `path/to/test.py` (NOVO) - [descrição]

**Testes**:
- XX unit tests (YY passing)
- Cenários cobertos: [lista]
- Cobertura: ZZ%

**Segurança (OWASP) - OBRIGATÓRIO**:
- [ ] A01: Broken Access Control - [Status/Mitigação]
- [ ] A02: Cryptographic Failures - [Status/Mitigação]
- [ ] A03: Injection - [Status/Mitigação]
- (ver SECURITY.md para checklist completo)

**Rollback Plan - OBRIGATÓRIO** (se feature crítica):
- Como reverter: [passos]
- Tempo estimado: [X minutos]
- Impacto: [descrição]
- (ver ROLLBACK.md para planos detalhados)

**CI/CD**:
- Quality gates: [passing/failing]
- Automated tests: [status]
- Deploy strategy: [descrição]

**Exemplo de Uso**:
```python
# Exemplo prático de como usar a funcionalidade
```

## ✅ Qualidade (Protocolo Simplicidade 3)
- ✅ Arquitetura Modular
- ✅ Type Hints (100%)
- ✅ Docstrings completas
- ✅ Tratamento de erros
- ✅ Testes (X passing, Y% coverage)
- ✅ CI/CD quality gates passing
- ✅ Security checklist OWASP completo
- ✅ Rollback plan documentado
- ✅ Commits semânticos
- ✅ **Documentação completa na pasta docs/**
- ✅ Código limpo (PEP8/ESLint/etc)

## 📊 Estatísticas
- TOTAL: X% completo (Y/Z tasks)
- Commits: N pushed
- CI/CD: Passing
```

#### **🔍 Validação da Documentação (Simplicidade 3)**

Antes de finalizar cada ciclo (Etapa 13 - Commit), a IA **DEVE VERIFICAR**:

- [ ] ✅ Pasta `docs/` existe e está atualizada
- [ ] ✅ Arquivo SPECIFICATIONS.md criado/atualizado para este ciclo
- [ ] ✅ TODAS as funcionalidades implementadas estão documentadas
- [ ] ✅ TODOS os comportamentos novos estão descritos
- [ ] ✅ TODOS os arquivos criados/modificados estão listados
- [ ] ✅ Decisões técnicas e arquiteturais estão justificadas
- [ ] ✅ Notas de decisão criadas para escolhas importantes (DECISIONS.md)
- [ ] ✅ Exemplos de uso estão incluídos
- [ ] ✅ Testes estão documentados
- [ ] ✅ **Checklist de segurança OWASP está completo (SECURITY.md) - OBRIGATÓRIO**
- [ ] ✅ **Plano de rollback documentado para features críticas (ROLLBACK.md) - OBRIGATÓRIO**
- [ ] ✅ Configuração CI/CD documentada

**Se algum item não estiver completo, a IA NÃO DEVE prosseguir para o commit** até completar a documentação.

#### **📌 Rationale: Por Quê Este Requisito é OBRIGATÓRIO (especialmente para Solo Developer)**

1. **Rastreabilidade**: Permite entender TUDO que foi implementado ao longo do tempo
2. **Memória Futura**: Você é solo - vai esquecer decisões após 3-6 meses sem ver o código
3. **Continuidade**: Se você precisar passar o projeto para outro dev, a documentação é essencial
4. **Debugging em Produção**: Documentação completa acelera diagnóstico de problemas
5. **Auditoria de Segurança**: Como solo dev em produção, você é responsável por segurança
6. **Rollback Rápido**: Documentação de rollback é essencial quando algo quebra às 3AM
7. **Profissionalismo**: Projetos sérios em produção exigem documentação completa
8. **Redução de Risco**: Solo dev não tem equipe para validar - documentação é sua rede de segurança
9. **Onboarding Futuro**: Se crescer e contratar, documentação facilita entrada de novos devs
10. **Compliance**: Muitos regulamentos exigem documentação de implementações

**Este requisito transforma a pasta `docs/` em seu "segundo cérebro" e rede de segurança como solo developer em produção.**

---

**📋 Gerenciamento do TASKS.md**:

**Regra Geral**:
- Se existe arquivo de tarefas/requisitos (ex: `TASKS.md`, `TODO.md`, `requirements.md`):
  - ✅ **Marcar tasks como completas** após implementação: `[ ]` → `[X]`
  - ✅ **Atualizar estatísticas** (percentuais, contadores)
  - ✅ **Adicionar notas de conclusão** (data, versão, descrição breve)
  - 🤖 **[OPCIONAL] Adicionar novas tarefas recomendadas pela IA** (ver detalhes em PROTOCOLO_SIMPLICIDADE_1.md - Etapa 12)
  
- Se **NÃO existe** arquivo de tarefas/requisitos:
  - ❓ **Perguntar ao usuário** qual o local/path do arquivo
  - ❓ **Perguntar sobre próximas tarefas e requisitos** caso não haja documento formal
  - ❓ **Sugerir criação** de `TASKS.md` como arquivo padrão

---

### 📊 **Legenda de Classificação de Tarefas (Simplicidade 3 - Solo Developer)**

**Objetivo**: Padronizar a classificação e priorização de tarefas para facilitar a organização pela IA quando você está trabalhando sozinho em produção.

**Nota para Simplicidade 3**: Como solo developer, você precisa de classificação **pragmática e rápida** que não adicione overhead desnecessário. A classificação deve ajudar a tomar decisões rápidas sem burocracia de equipe.

#### **Status da Tarefa**

- 🔴 **Not Started** (Não Iniciada) - Aguardando início, sem trabalho realizado
- 🟡 **In Progress** (Em Progresso) - Desenvolvimento ativo, trabalho em andamento
- 🟢 **Done** (Concluída) - Implementada, testada, validada em CI/CD e finalizada
- 🔵 **Blocked** (Bloqueada) - Impedida por dependência externa ou problema técnico

**Dica Solo**: Minimize tarefas 🔵 Blocked. Como você está sozinho, blockers são especialmente custosos. Se algo está bloqueado, veja se há workaround temporário ou outra tarefa para avançar.

#### **Complexidade da Tarefa**

- 🟢 **Simples** (0-1h) - Baixo risco, poucas dependências, escopo claro
- 🟡 **Média** (1-2h) - Risco médio, algumas integrações, pode requerer testes adicionais
- 🔴 **Complexa** (>2h) - Alto risco, muitas dependências, escopo aberto ou ambíguo

**Estratégia Solo**: Intercale tarefas complexas com simples. Após resolver uma 🔴 complexa, faça 2-3 🟢 simples para manter momentum e motivação. Evite acumular apenas tarefas complexas no sprint.

#### **Priorização MoSCoW**

- 🔴 **Must Have** - Crítico para o funcionamento do sistema, bloqueante para release
- 🟡 **Should Have** - Importante mas não bloqueante, pode ser adiado se necessário
- 🟢 **Could Have** - Desejável se houver tempo, baixa prioridade
- ⚪ **Won't Have** (Later) - Explicitamente fora do escopo atual, para versões futuras

**Dica Solo**: Seja rigoroso com MoSCoW. A tentação de fazer tudo é real quando você está sozinho. Use ⚪ Won't Have generosamente para evitar feature creep.

#### **Integração com Matriz de Decisão (Opcional)**

A Matriz de Decisão (Etapa 2.5) é **opcional** no Simplicidade 3, mas útil quando você tem 10+ tarefas para priorizar:

```markdown
## Sprint v2.5 - Backlog Solo Developer

### 🔴 MUST HAVE (Obrigatórias para Release)

| Task | Status | Complex. | Score | Nota |
|------|--------|----------|-------|------|
| #25 Security patch CVE-2024-1234 | 🔴 | 🟢 | 34.0 | Crítico! Começar hoje |
| #26 Rollback plan para deploy | 🔴 | 🟡 | 29.0 | Fazer antes do deploy |
| #27 Implementar backup automático | 🔴 | 🟡 | 27.5 | Produção requer |

**Decisão**: Começar por #25 (maior score + mais simples). Depois #26 e #27.
```

**Quando usar Matriz de Decisão**:
- ✅ Quando tem 10+ tarefas e não é óbvio por onde começar
- ✅ Quando várias tarefas são "Must Have" e precisa desempatar
- ✅ Quando quer justificar decisões para você mesmo (ou para cliente)
- ❌ Quando tem 1-5 tarefas óbvias (overhead desnecessário)

#### **Frameworks Avançados de Priorização (Opcional)**

Para solo developer em produção, mantenha priorização simples. Use frameworks avançados apenas quando realmente necessário:

##### **Matriz RICE** (Quando justificar para cliente/stakeholders)

Use quando cliente questiona prioridades ou quando você precisa defender decisões de roadmap.

**Exemplo Solo**:
```markdown
| Feature Solicitada | RICE Score | Decisão |
|-------------------|-----------|---------|
| API v2 com GraphQL | 50 | ✅ Próximo trimestre |
| Dark mode | 180 | ✅ Este mês (maior ROI) |
| Multi-idiomas (i18n) | 25 | ⚪ Backlog distante |

**Justificativa para cliente**: Dark mode tem 3.6x mais valor que API v2 
considerando alcance (mais usuários) e esforço (menos horas).
```

##### **Matriz de Eisenhower** (Gestão de Urgências)

**Adaptação Solo Developer**:
- **Q1 (Urgente + Importante)**: Fazer AGORA (bugs produção, incidentes)
- **Q2 (Importante + Não Urgente)**: AGENDAR (features planejadas, refatoração)
- **Q3 (Urgente + Não Importante)**: AUTOMATIZAR (deploys, relatórios, emails)
- **Q4 (Não Urgente + Não Importante)**: ELIMINAR (não gaste tempo aqui!)

**Exemplo Solo**:
```markdown
## Esta Semana - Matriz Eisenhower

### ⭐ Q1: FAZER AGORA
- 🔴🟢 [ ] Corrigir bug de segurança reportado (1h)
- 🔴🟡 [ ] Deploy de hotfix v2.3.1 (1.5h)

### 📅 Q2: AGENDAR (Segunda-feira)
- 🔴🟡 [ ] Implementar feature X solicitada por cliente (2h)
- 🔴🟢 [ ] Atualizar documentação da API (0.5h)

### 🤖 Q3: AUTOMATIZAR (não fazer manual!)
- [ ] Deploy manual → Implementar CD pipeline (investir 3h, economizar 30min/semana)
- [ ] Relatórios semanais → Script automático

### 🗑️ Q4: ELIMINAR
- [ ] ~~Refatorar código que funciona bem~~ (desnecessário agora)
- [ ] ~~Pesquisar framework novo X~~ (sem necessidade real)
```

#### **Exemplo Completo Simplicidade 3 (Solo Developer)**

```markdown
# TASKS.md - Projeto SaaS Solo em Produção

## 📊 Legenda
- **Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Done | 🔵 Blocked
- **Complexidade**: 🟢 Simples (0-1h) | 🟡 Média (1-2h) | 🔴 Complexa (>2h)
- **MoSCoW**: 🔴 Must | 🟡 Should | 🟢 Could | ⚪ Won't

## 📊 Status do Projeto
- **Versão Atual**: v3.2.1 em produção
- **Progresso**: 72% (29/40 features planejadas)
- **Usuários Ativos**: 1.245 (crescimento 15% mês)
- **Uptime**: 99.8% (últimos 30 dias)
- **Próximo Release**: v3.3.0 (15 dias)

## 🔴 MUST HAVE - Release v3.3.0

### Alta Prioridade (Crítico)
- 🔴🟢 [ ] #88 Implementar rate limiting (1h) ⭐ FAZER HOJE
  - **Razão**: Segurança, prevenir abuso da API
  - **CI/CD**: Incluir testes de carga
  - **Rollback Plan**: Flag feature toggle preparada
  
- 🟡🟡 [ ] #89 Adicionar health check endpoint (1.5h, 70% completo)
  - **Razão**: Monitoramento de uptime para Kubernetes
  - **Faltando**: Testes de integração + documentação
  - **Dependência**: Rate limiting deve estar funcionando

### Média Prioridade
- 🔵🔴 [ ] #90 Migrar banco para PostgreSQL 14 (4h, BLOQUEADO)
  - **Blocker**: Aguardando janela de manutenção (próximo domingo 3h-6h)
  - **Rollback Plan**: ✅ Snapshot do banco atual criado
  - **Fallback**: Se falhar, permanecer em PG 12 por mais 1 mês

## 🟡 SHOULD HAVE - Release v3.4.0 (backlog)
- 🔴🟡 [ ] #91 Dashboard de métricas (2h)
- 🔴🟢 [ ] #92 Melhorar mensagens de erro (0.5h)

## 🟢 COULD HAVE - Backlog Futuro
- 🔴🟡 [ ] #93 Dark mode (1.5h, RICE=180 - boa prioridade)
- 🔴🔴 [ ] #94 Integração com Slack (3h)

## ⚪ WON'T HAVE - Não fazer agora
- [ ] #95 Versão mobile app nativo (100h+, muito esforço)
  - **Alternativa**: PWA já funciona bem no mobile
- [ ] #96 Multi-tenancy (80h+, complexidade alta)
  - **Razão**: Apenas 1 cliente por enquanto, não justifica

---

## 🤖 Recomendações da IA (3/30 usadas)

### 🔴 MUST HAVE Sugeridas
- 🔴🟢 [ ] **[IA-001]** Adicionar logs estruturados (1h)
  - **Razão**: Facilitar debugging de incidentes em produção
  - **Integração**: Usar biblioteca já presente (loguru)

---

## 📝 Notas de Decisão (ADR Simplificado)

**#90 - Por quê PostgreSQL 14?**
- Performance: 20% mais rápido em queries complexas (benchmark interno)
- Segurança: Patches de segurança críticos não backportados para PG 12
- Suporte: PG 12 EOL em nov/2024 (6 meses)
- **Decisão**: Migrar agora com rollback plan robusto

---

**Próxima revisão**: Segunda-feira (revisar progresso, ajustar prioridades)
```

#### **Recomendações para IA ao Trabalhar com Solo Developer**

**Ao classificar tarefas para solo developer (Simplicidade 3), a IA deve**:

1. ✅ **Priorizar tarefas simples primeiro** - Solo dev precisa de wins rápidos para momentum
2. ✅ **Evitar acúmulo de blockers** - Sugerir workarounds ou tarefas alternativas
3. ✅ **Balancear complexidade** - Intercalar tarefas difíceis com fáceis
4. ✅ **Considerar energia/motivação** - Sexta à tarde? Tarefas simples. Segunda cedo? Tarefas complexas
5. ✅ **Documentar decisões importantes** - Solo dev esquece contexto após 3 meses
6. ✅ **Ser rigoroso com "Won't Have"** - Proteger contra feature creep
7. ✅ **Automatizar o que for repetitivo** - Solo dev não tem tempo para tarefas manuais
8. ✅ **Priorizar segurança e CI/CD** - Sem equipe para revisar, automação é essencial
9. ✅ **Sugerir rollback plans** - Solo dev não tem time para ajudar se algo der errado
10. ✅ **Manter classificação pragmática** - Não adicionar overhead de processo

**Diferenças Simplicidade 3 vs 2**:
- **S3**: Classificação deve ser **rápida** (não perder tempo em scoring elaborado)
- **S3**: Priorizar **automação** sobre processo manual (CI/CD, testes automáticos)
- **S3**: **Rollback plans obrigatórios** (não tem equipe para ajudar em incidentes)
- **S3**: Matriz de Decisão **opcional** (só quando realmente necessário, não overhead)
- **S3**: Recomendações da IA aceitas **diretamente** (não precisa consenso de equipe)

**Diferenças Simplicidade 3 vs 1**:
- **S3**: Adiciona **Security Checklist** obrigatório (produção requer)
- **S3**: Adiciona **CI/CD Quality Gates** obrigatório (automação essencial)
- **S3**: Adiciona **Rollback Plans** obrigatório (segurança em deploy)
- **S3**: Mantém classificação de S1, mas com foco em **produção crítica**

---

**🤖 Recomendações de Tarefas pela IA (Solo Developer)**:
Para solo developers (Simplicidade 3), as recomendações da IA são especialmente valiosas pois não há equipe para brainstorming. A IA age como um "segundo cérebro" sugerindo melhorias e oportunidades. Como você está sozinho, tem autonomia para aceitar/rejeitar recomendações rapidamente sem necessidade de consenso em equipe.

📘 **Detalhes completos da funcionalidade de recomendações**: Ver `PROTOCOLO_SIMPLICIDADE_1.md` - Etapa 12 - Seção "Recomendações de Tarefas pela IA"

**📁 Localização do Arquivo TASKS.md**:
- **Preferência padrão**: O arquivo `TASKS.md`, quando produzido, deve ser colocado em `docs/TASKS.md`
- **Criar pasta docs/**: Se a pasta `docs/` não existe no projeto, ela deve ser criada automaticamente
- **Flexibilidade**: O usuário ou programador pode optar por colocar em outro local se preferir
- **Exemplo de criação**:
  ```bash
  # Criar pasta docs se não existir
  mkdir -p docs
  
  # Criar ou atualizar TASKS.md
  echo "# Tasks" > docs/TASKS.md
  ```

**Exemplo de Marcação (REQUIREMENTS.md)**:
```markdown
## 🟢 COULD HAVE (Prioridade Baixa)

### ✅ Tasks Concluídas

#### Task Example - Editor de Arquivos Integrado (vX.Y.Z)
**Status**: ✅ Completa - 30/11/2025

**Objetivo**: Implementar editor de texto integrado com diferenciação de escopo por cores.

**Implementação**:
1. ✅ ComponentE com QTextEdit e syntax highlighting
2. ✅ Diferenciação de escopo por cores (HTML tags, DATA keys, etc.)
3. ✅ Abrir/salvar arquivos (.txt, .data, .html, .tsx, .py)
4. ✅ Integração com menu File → Open Editor

**Arquivos Criados**:
- `src/gui/editor_dock.py` (500+ linhas)
- `tests/test_editor_dock.py` (15 testes)

### 🔨 Tasks Pendentes
- **[]** Próxima task não implementada...
```

**Estrutura Mínima Recomendada**:
```markdown
# Projeto - Tasks

## Categorias
- MUST HAVE: [X/Y completas] (Z%)
- SHOULD HAVE: [X/Y completas] (Z%)
- COULD HAVE: [X/Y completas] (Z%)
- WOULD HAVE: [X/Y completas] (Z%)

## Estatísticas
- **TOTAL**: [X/Y completas] (Z%)
```

**Estrutura da Documentação de Versão**:
```markdown
# MyProject v2.9.X - [Nome Descritivo]

**Data**: DD/MM/AAAA
**Sprint**: X tasks em Y horas
**Metodologia**: Protocolo Simplicidade 1

## 📋 Objetivos da Sprint
- Task #X: [descrição]
- Task #Y: [descrição]

## 🎯 Tasks Implementadas
### Task #X: [Nome]
- **Problema**: [descrição do problema original]
- **Solução**: [como foi resolvido]
- **Arquivos Modificados**: [lista]
- **Testes**: [quantidade e status]

## ✅ Qualidade (Protocolo Simplicidade 1)
- ✅ Arquitetura Modular
- ✅ Type Hints (100%)
- ✅ Docstrings completas
- ✅ Tratamento de erros
- ✅ Testes (X passing)
- ✅ Commits semânticos
- ✅ Documentação completa
- ✅ Código limpo (PEP8)

## 📊 Estatísticas
- TOTAL: X% completo (Y/Z tasks)
- Commits: N pushed
```

---

### 1️⃣2️⃣.5️⃣ **Rollback Plans** ⭐ [OBRIGATÓRIO]

> **CRÍTICO PARA PRODUÇÃO**: Esta etapa é **OBRIGATÓRIA** no Simplicidade 3.

**Por quê obrigatório**:
- ✅ **Produção**: Bugs afetam usuários reais
- ✅ **Solo**: Você está sozinho para resolver emergências
- ✅ **Downtime**: Rollback rápido minimiza impacto
- ✅ **Confiança**: Deploy ousado sabendo que pode reverter

**Quando criar Rollback Plan**:
- ✅ Feature crítica (pagamento, autenticação, dados)
- ✅ Mudança em schema/migrations de dados
- ✅ Alteração em API pública
- ✅ Deploy de alto risco

**Template Simplificado**:

```markdown
# Rollback Plan - Task #XX: [Nome Feature]

## Critérios para Rollback
Executar rollback SE:
- [ ] Taxa de erro > 5% em 1h após deploy
- [ ] Usuários reportam perda de dados
- [ ] Crashes frequentes (>5 reports)
- [ ] Performance pior que versão anterior (>2x mais lento)

## Como Reverter (Passo-a-Passo)

### 1. Preparação (5min)
```bash
# Backup estado atual
cp data.db data.db.backup-$(date +%s)
cp app.log rollback-logs.txt
```

### 2. Rollback Código (5min)
```bash
# Voltar para versão anterior
git checkout v1.9.5
# OU
pip install app==1.9.5 --force-reinstall
```

### 3. Restaurar Dados (se necessário)
```bash
# Restaurar backup DATA/DB criado na migração
cp data.data.backup data.data
```

### 4. Validar (5min)
```bash
# Smoke tests
app --version  # Deve mostrar v1.9.5
app test-basic-flow
```

## Tempo Total Rollback
~15-20 minutos (downtime esperado)

## Backup Necessário
- ✅ Backup automático criado no deploy
- ✅ Git tag da versão anterior existe
- ❌ Não depende de serviços externos

## Dados em Risco
- **Alto**: Dados criados após deploy (não no backup)
- **Baixo**: Dados existentes (preservados no backup)

**Mitigação**: Exportar dados novos antes de rollback.
```

**Alternativa: Feature Flags** (melhor que rollback):

```python
# Desabilitar feature remotamente sem redeploy
FEATURE_NEW_EXPORT = os.getenv("ENABLE_NEW_EXPORT", "false") == "true"

def export_data():
    if FEATURE_NEW_EXPORT:
        return new_export()  # Nova implementação
    else:
        return old_export()  # Fallback seguro

# Em caso de problema: export ENABLE_NEW_EXPORT=false
# Usuários automaticamente voltam para versão antiga
```

**Checklist Rápido**:
```markdown
- [ ] Critérios de rollback definidos (quando executar?)
- [ ] Passos de rollback documentados (como reverter?)
- [ ] Backup automatizado (dados preservados?)
- [ ] Tempo de rollback estimado (<30min?)
- [ ] Feature flag considerada (alternativa melhor?)
```

**Tempo Criação**: 10-15 minutos por feature crítica.

📘 **Rollback Plans completos**: Ver `PROTOCOLO_SIMPLICIDADE_2.md` - Etapa 12.5

---

### 1️⃣3️⃣ **Fazer Commit e Push**
- **Formato**: Conventional Commits (OBRIGATÓRIO)
- **Idioma**: Todas as mensagens de commit devem ser **EXCLUSIVAMENTE EM INGLÊS** (requisito obrigatório)
- **Mensagem**: Descritiva, completa, com contexto
- **Frequência**: 1 commit por task ou grupo lógico de mudanças

**Tipos de Commit Padronizados** (OBRIGATÓRIOS):
- `feat`: Indica uma nova feature
  - Exemplo: `git commit -m "feat: add Header component"`
- `fix`: Indica uma correção de bug
  - Exemplo: `git commit -m "fix: remove wrong prop in Header"`
- `refactor`: Indica uma refatoração de código
  - Exemplo: `git commit -m "refactor: add title in Header"`
- `test`: Indica alterações em testes
  - Exemplo: `git commit -m "test: add test in title Header"`
- `style`: Indica alterações de estilo/formatação
  - Exemplo: `git commit -m "style: add Header title background"`
- `docs`: Indica alteração na documentação
  - Exemplo: `git commit -m "docs: add get started in readme"`
- `chore`: Indica alteração de ambiente de desenvolvimento
  - Exemplo: `git commit -m "chore: change eslint rules"`
- `build`: Indica alteração de dependências
  - Exemplo: `git commit -m "build: add sass"`
- `revert`: Indica reversão de commit anterior
  - Exemplo: `git commit -m "revert: back to adc1234 commit"`

⚠️ **IMPORTANTE**: Todas as mensagens de commit devem ser escritas **EXCLUSIVAMENTE EM INGLÊS**!

**Estrutura de Commit Message**:
```
<tipo>: <descrição curta> (<versão>)

<PROBLEMA ORIGINAL>:
- [Contexto do problema]
- [Por que era necessário resolver]

<SOLUÇÃO IMPLEMENTADA>:
✅ [Feature/função 1]
   - [Detalhe técnico]
✅ [Feature/função 2]
   - [Detalhe técnico]

✅ [TESTES]:
   - [Quantidade] unit tests ([status])
   - [Categorias testadas]

<ARQUIVOS MODIFICADOS>:
- [arquivo1.py] (+X linhas)
- [arquivo2.py] (~Y linhas)
- [tests/test_X.py] (NOVO - Z linhas)
- [docs/REQUIREMENTS.md] (estatísticas atualizadas)

<ESTATÍSTICAS ATUALIZADAS>:
- [CATEGORIA]: X → Y completas (A% → B%)
- TOTAL: X → Y completas (A% → B%)

<EXEMPLO DE USO>: (se aplicável)
  [Demonstração prática]

Refs: [documentação relacionada]
Closes: Task #X (vX.X.X)
```

**Exemplo Real** (Task Example):
```bash
git add src/ tests/ docs/REQUIREMENTS.md
git commit -m "feat: completar Task Example - Feature Update System (vX.Y.Z)

PROBLEMA ORIGINAL:
- Implementação vX.Y.Z usava string_similarity() (ERRADO)
- Não detectava valores duplicados, apenas similaridade de nomes
...

✅ SOLUÇÃO IMPLEMENTADA:
✅ extract_all_keys_from_obj()
   - Suporta tipo Obj E dict
   - Retorna Dict[str, str] (path → value)
...

Closes: Task Example (vX.Y.Z)"

git push
```

---

## 🏆 Critérios de Qualidade Profissional

Toda implementação deve cumprir **100% destes critérios**:

| # | Critério | Descrição | Validação |
|---|----------|-----------|-----------|
| 1 | **Arquitetura Modular** | Cada feature em módulo separado | Arquivo próprio em `src/` |
| 2 | **Type Hints** | 100% dos parâmetros tipados | `def func(x: int) -> str:` |
| 3 | **Docstrings** | Todas funções públicas documentadas | Args, Returns, Examples |
| 4 | **Tratamento de Erros** | Try/except com mensagens claras | `except Exception as e:` |
| 5 | **Testes** | Unitários + integração (100% coverage) | `tests/test_*.py` passing |
| 6 | **Commits Semânticos** | Conventional Commits | `feat:`, `fix:`, `docs:` |
| 7 | **Documentação** | REQUIREMENTS.md + SPECIFICATIONS.md | Atualizado e completo |
| 8 | **Código Limpo** | PEP8, nomes semânticos, DRY | Funções < 50 linhas |

---

## 📊 Aplicação Prática: Task Example (Exemplo Completo)

### Situação Inicial
```markdown
Tasks pendentes na categoria SHOULD HAVE:
[ ] Complex Feature Example (MUITO COMPLEXO)
[ ] Busca com IA semântica (MUITO COMPLEXO)
[⚠️] Feature Update (PARCIAL - mais simples!) ✅ ESCOLHIDA
[ ] Google Translate API integration (COMPLEXO)
```

### Sprint Planejada
```
vX.Y.Z: Completar Task Example
Estimativa: 3-4 horas
Complexidade: MÉDIA (mais simples que as outras)
```

### Execução (Protocolo Simplicidade 1)

**1. Ler Documentação** ✅
- Lido: `docs/FEATURE_SPEC.md` (662 linhas)
- Entendido: problema de string similarity vs. value equality

**2. Escolher Tarefa Simples** ✅
- Task Example é **mais simples** que editor de texto ou IA
- Escopo claro: 2 funções principais + integração

**3. Fazer Perguntas** ✅
- Perguntado: "Quantas palavras pegar? 3-5?"
- Resposta: "Default 30 caracteres"
- Perguntado: "Converter para camelCase?"
- Resposta: "Sim, remover acentos"
- Perguntado: "Conflitos de nomes?"
- Resposta: "Linha menor vence, não mexer se valores diferentes"

**4. Sprint** ✅
- 6 subtasks planejadas (incluindo perguntas)
- Tempo estimado: 3h45min

**5. Implementar com Arquitetura** ✅
```
Ordem executada:
1. extract_all_keys_from_obj() (função auxiliar - Alta Coesão)
2. build_substitution_map_by_value() (função principal - Baixo Acoplamento)
3. Atualizar cli_dedupe() (integração - Injeção de Dependência)
4. Criar testes (validação)
5. Documentação (finalização)

Padrões Aplicados:
- ✅ Módulos separados (Reutilização)
- ✅ Type hints em todas funções
- ✅ Information Expert (GRASP): cada função tem a info que precisa
- ✅ Baixo acoplamento: funções independentes
- ✅ Alta coesão: cada função faz UMA coisa
```

**6. Fazer Testes** ✅
```
12 unit tests criados:
- 4 testes para extract_all_keys_from_obj()
- 5 testes para build_substitution_map_by_value()
- 2 testes para apply_substitutions_to_file()
- 1 teste para update_references_in_project()
Resultado: 12/12 passing (100%)
```

**7. Documentação** ✅
```
Arquivos criados/atualizados:
- docs/REQUIREMENTS.md (Task Example marcada [X])
- docs/FEATURE_SPEC.md (já existia)
- tests/test_reference_updater.py (NOVO - 350 linhas)
Estatísticas: 59.6% → 60.6% (63 tasks completas)
```

**8. Commit e Push** ✅
```bash
Commit: 903bca4
Mensagem: 60 linhas (completa e detalhada)
Status: pushed para GitHub ✅
```

### Resultado Final
✅ **Task Example 100% completa**  
✅ **Protocolo Simplicidade 1: 10/10 etapas cumpridas** (v1.1 - 10 etapas)  
✅ **Tempo real: ~3h (dentro da estimativa)**  
✅ **Zero bugs detectados**  
✅ **Documentação profissional**

**Nota**: Este exemplo usa v1.1 do protocolo (10 etapas). A v1.2 adiciona mais 2 etapas (integração GUI e CLI).

---

## 🎓 Lições Aprendidas

### ✅ O Que Funciona
1. **Escolher o mais simples**: Task Example era mais fácil que editor de texto
2. **Incrementalidade**: Função auxiliar → principal → integração
3. **Testes primeiro**: Detectou 2 ajustes necessários antes de commitar
4. **Documentação completa**: Facilita manutenção futura

### ❌ Anti-padrões a Evitar
1. **Não começar pela tarefa mais difícil**
   - ❌ "Vou fazer o editor de texto primeiro (50h)"
   - ✅ "Vou fazer o tooltip preview primeiro (30min)"

2. **Não fazer tudo de uma vez**
   - ❌ "Vou implementar tudo em uma função gigante"
   - ✅ "Vou dividir em 3 funções testáveis"

3. **Não pular testes**
   - ❌ "Vou testar manualmente depois"
   - ✅ "Vou criar 12 unit tests agora"

4. **Não fazer commits genéricos**
   - ❌ `git commit -m "updates"`
   - ✅ `git commit -m "feat: Task Example com VALUE EQUALITY (60 linhas)"`

---

## 📚 Referências

- **REQUIREMENTS.md**: Lista completa de tarefas do projeto
- **vX.Y.Z-COMPARISON.md**: Primeiro exemplo do protocolo
- **vX.Y.Z-SPECIFICATIONS.md**: Sprint com 3 tasks simples
- **vX.Y.Z-SPECIFICATIONS.md**: Iterações rápidas
- **vX.Y.Z-SPECIFICATIONS.md**: 4 melhorias de UX
- **FEATURE_SPEC.md**: Exemplo de documentação detalhada

---

## 🔄 Ciclo Contínuo

O Protocolo Simplicidade 1 é um **ciclo iterativo**:

```
┌──────────────────────────────────────────────┐
│  1. Ler Documentação                         │
│  2. Escolher Tarefas Mais Simples            │
│  3. Fazer Perguntas ao Programador           │
│  4. Analisar e Estudar o Projeto             │
│  5. Planejar Sprint (2-4 tasks, 3-4h)        │
│  6. Implementar (arquitetura GoF + GRASP)    │
│  7. Verificar Integração GUI                 │
│  8. Verificar Implementação CLI              │
│  9. Testar (100% coverage)                   │
│  10. Organizar Pasta Raiz                    │
│  11. Documentar (TASKS + vX.X.X-SPECS)       │
│  12. Commit + Push (conventional)            │
└──────────────────────────────────────────────┘
           ↓
    ┌──────────────┐
    │   REPETIR    │ ← Sempre há tarefas mais simples!
    └──────────────┘
```

**Resultado**: Progresso constante, código profissional, zero dívida técnica, **seguro para produção**.

---

## 🎯 Mensagem Final

> "Quero um trabalho completo, profissional e **seguro para produção** - desenvolvendo sozinho!"

**Simplicidade 3 garante**:
- ✅ **Base sólida**: 13 etapas obrigatórias do Simplicidade 1
- ✅ **Segurança**: OWASP checklist obrigatório (vulnerabilidades = zero)
- ✅ **Automação**: CI/CD valida todo commit (memória não falha)
- ✅ **Proteção**: Rollback plans para features críticas
- ✅ **Pragmático**: SEM overhead de equipe (code review, retrospectives formais)
- ✅ **Priorização**: Matriz de decisão quando necessário
- ✅ **Performance**: Profiling para features lentas
- ✅ **Rastreabilidade**: Notas de decisão para escolhas importantes

**Simplicidade 3 é ideal para**:
- 👤 **Solo developer** (você sozinho)
- 🚀 **Produção** (usuários reais dependendo)
- ⚠️ **Crítico** (bugs têm impacto)
- 📈 **Longo prazo** (projeto evolutivo >6 meses)

**Quando usar outro protocolo**:
- Protótipo descartável → Use **Simplicidade 1**
- Equipe 2+ pessoas → Use **Simplicidade 2** (tem code review por pares)

**Releia este documento antes de cada sprint!**

---

## 📊 Organização Ordinal de Tarefas - Protocolos Simplicidade

**Versão**: 1.0  
**Data de Criação**: 27 de Dezembro de 2025  
**Autor**: Josué Amaral  
**Status**: ATIVO

---

### 🎯 Objetivo

Este documento define o sistema de **Organização Ordinal de Tarefas** para os Protocolos Simplicidade, permitindo que desenvolvedores humanos e inteligências artificiais identifiquem rapidamente:

- ✅ **Ordem de execução** das tarefas (do mais simples ao mais complexo)
- ✅ **Dependências** entre tarefas (quais devem ser feitas primeiro)
- ✅ **Paralelização** (quais podem ser executadas simultaneamente)
- ✅ **Organização hierárquica** (estrutura de árvore/grafo)

---

### 📊 Sistema de Prefixos Ordinais

#### Nível 1: Numeração Simples (Tarefas Independentes)

Para tarefas **independentes** que **não têm dependências** entre si:

```markdown
1. Tarefa A - Configurar ambiente de desenvolvimento
2. Tarefa B - Criar documentação inicial
3. Tarefa C - Definir arquitetura do sistema
```

**Características**:
- ✅ Podem ser executadas em **qualquer ordem**
- ✅ Podem ser feitas **paralelamente** em branches separadas
- ✅ Sem conflitos de dependência
- ✅ Numeração sequencial crescente (1, 2, 3...)

---

#### Nível 2: Hierarquia com Letras (Grupos de Tarefas)

Para organizar tarefas em **grupos lógicos** com **subgrupos**:

```markdown
🔴 MUST HAVE - Release v1.0.0

A. Infrastructure e Configuração
   A.1. Criar estrutura de diretórios
   A.2. Configurar dependências do projeto
   
B. Core - Estruturas de Dados
   B.1. Implementar classe Node
   B.2. Implementar ExpressionTree
   
C. Core - Conversões
   C.1. Implementar conversão número → árvore
   C.2. Implementar conversão árvore → RPN
```

**Características**:
- ✅ **Letra maiúscula** = Grupo/Categoria
- ✅ **Número após letra** = Subtarefa dentro do grupo
- ✅ Tarefas de **grupos diferentes** (A, B, C) são **paralelas**
- ✅ Tarefas do **mesmo grupo** podem ter dependências

---

#### Nível 3: Hierarquia Profunda (Dependências Complexas)

Para tarefas com **dependências explícitas** em estrutura de **árvore/grafo**:

```markdown
A.C.1. Implementar conversão número → árvore
   ├─ Deve ser feito DEPOIS de A.1, A.2, C.1
   └─ Estrutura: A (raiz) → C (intermediário) → 1 (folha)

B.C.2. Implementar conversão árvore → RPN
   B.C.2.1. Parser RPN (folha - fazer PRIMEIRO)
   B.C.2.2. Serializer RPN (folha - fazer PRIMEIRO)
   B.C.2. Implementar conversão (pai - fazer DEPOIS de 2.1 e 2.2)
```

**Leitura da hierarquia** (⭐ CRÍTICO):

A hierarquia deve ser lida da **DIREITA para ESQUERDA** (ordem inversa):

```
C.B.1.D.1
   │  │ │ └─ 1: Executar por ÚLTIMO (raiz da árvore)
   │  │ └─── D: Executar TERCEIRO
   │  └───── 1: Executar SEGUNDO
   └──────── B: Executar PRIMEIRO (folha da árvore)

Ordem de execução: B → 1 → D → 1 (da direita para esquerda)
```

**Interpretação**:
- ✅ **Mais à DIREITA** = Ancestrais (executar por ÚLTIMO)
- ✅ **Mais à ESQUERDA** = Descendentes (executar PRIMEIRO)
- ✅ **Organização bottom-up**: Base → Topo

**Exemplo Prático**:

```markdown
C.B.1.D.1 - Integrar Dash com Cytoscape

Ordem de execução (direita → esquerda):
1. PRIMEIRO:  Tarefa D.1 (criar componente básico Cytoscape)
2. SEGUNDO:   Tarefa 1.D (configurar layout)
3. TERCEIRO:  Tarefa B.1 (implementar estrutura de dados)
4. QUARTO:    Tarefa C (integração final Dash + Cytoscape)
```

---

### 🌳 Estrutura de Árvore/Grafo

#### Conceitos Fundamentais

**1. Nós Pai e Filhos**

```
B.C.2 (PAI - executar DEPOIS)
   ├── B.C.2.1 (FILHO - executar ANTES)
   └── B.C.2.2 (FILHO - executar ANTES)
```

**Regra**: 
- ✅ **Filhos devem ser completados ANTES do pai**
- ✅ Filhos são **pré-requisitos** do pai
- ✅ Pai **depende** dos filhos

**2. Irmãos (Parallel)**

```
B.C.2.1 (irmão)
B.C.2.2 (irmão)
```

**Regra**:
- ✅ Irmãos podem ser executados **paralelamente**
- ✅ Sem dependência entre si
- ✅ Podem estar em **branches separadas**

**3. Primos, Tios, Avós (Parallel vs Serial)**

```
A. Grupo A
   A.1. Tarefa A1
   A.2. Tarefa A2
   
B. Grupo B
   B.1. Tarefa B1
   B.2. Tarefa B2
```

**Regra**:
- ✅ **Grupos diferentes** (A, B) = **PARALLEL** (executar simultaneamente)
- ✅ **Primos** (A.1 e B.1) = **PARALLEL**
- ✅ **Tios/Sobrinhos** (A e B.1) = **Avaliar dependências explícitas**

---

### 🔄 Paralelização vs Serialização

#### Tarefas PARALELAS (podem ser simultâneas)

✅ **Quando paralelizar**:
- Tarefas de **grupos diferentes** (A.x, B.x, C.x)
- **Irmãos** no mesmo nível (X.1, X.2, X.3)
- **Primos** (A.1 e B.1)
- Tarefas **sem dependências** explícitas

**Exemplo**:
```markdown
✅ PARALLEL:
   A.1 (Criar modelo User)
   B.1 (Criar modelo Product)
   C.1 (Criar interface gráfica)
   
→ Podem ser feitas em 3 branches simultâneas
→ Zero conflitos
```

---

#### Tarefas SERIAIS (devem ser sequenciais)

❌ **Quando serializar**:
- Tarefas com **relação pai-filho**
- Tarefas com **dependências explícitas**
- Quando uma tarefa **usa o resultado** de outra

**Exemplo**:
```markdown
❌ SERIAL:
   B.C.2.1 (Parser RPN) ─┐
   B.C.2.2 (Serializer)  ├─→ B.C.2 (Conversão completa)
                         ┘
   
→ B.C.2.1 e B.C.2.2 DEVEM ser completadas ANTES de B.C.2
→ B.C.2 depende dos resultados de 2.1 e 2.2
```

---

### 🎯 Integração com Sistema de Classificação Existente

O sistema ordinal **complementa** (não substitui) as classificações existentes:

```markdown
🔴🟡 [ ] #3 B.1. Implementar classe Node (1h)
 │  │  │  │ └─ Prefixo ordinal (dependências)
 │  │  │  └─── ID da issue (#3)
 │  │  └────── Hierarquia (B = Grupo, 1 = Subtarefa)
 │  └───────── Complexidade (🟡 Média)
 └──────────── Prioridade (🔴 Must Have)

Razão: Base para toda manipulação de árvores
Features: Binary tree node com operador/valor
Tests: Unit tests para criação de nós
```

**Legenda Completa**:
- **Prioridade MoSCoW**: 🔴 Must | 🟡 Should | 🟢 Could | ⚪ Won't
- **Complexidade**: 🟢 Simples (0-1h) | 🟡 Média (1-2h) | 🔴 Complexa (>2h)
- **Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Done | 🔵 Blocked
- **Prefixo Ordinal**: Identifica ordem de execução e dependências

---

### 🤖 Instruções para Inteligências Artificiais

**Quando Sugerir Organização Ordinal**

A IA deve sugerir organização ordinal quando:

✅ **Projeto tem >10 tarefas** com interdependências
✅ **Múltiplos desenvolvedores** trabalhando simultaneamente
✅ **Tarefas bloqueantes** (uma depende de outra)
✅ **Risco de conflitos** no controle de versão
✅ **Necessidade de paralelização** para acelerar desenvolvimento

**Como a IA Deve Aplicar**

1. **Analisar dependências**:
   ```python
   # Pseudo-código
   tarefas = ler_tasks_md()
   grafo = construir_grafo_dependencias(tarefas)
   ordem = ordenacao_topologica(grafo)  # Bottom-up
   ```

2. **Identificar grupos paralelos**:
   ```python
   grupos_parallel = identificar_componentes_independentes(grafo)
   ```

3. **Atribuir prefixos ordinais**:
   ```python
   for grupo in grupos_parallel:
       letra = proxima_letra()  # A, B, C...
       for tarefa in grupo:
           tarefa.prefixo = f"{letra}.{tarefa.index}"
   ```

4. **Sugerir estratégia de branches**:
   ```markdown
   Recomendação de branches:
   - Branch feat/auth: A.1 → A.2 → A.3
   - Branch feat/api: B.1 → B.2 (parallel com auth)
   - Branch feat/ui: C.1 (aguardar merge de auth)
   ```

---

## 🌳 Analogia da Árvore de Importações

**Autor:** Josué Amaral  
**Data:** 24 de Dezembro de 2025  
**Contexto:** Phase 3.0 - Refactoring Architecture  
**Aplicável a:** Todas as linguagens de programação

---

### 📚 Visão Geral

Este documento descreve a **Analogia da Árvore de Importações**, um modelo mental para compreender e organizar a arquitetura de dependências em projetos de software. Esta analogia é aplicável a qualquer linguagem de programação que suporte importação/inclusão de módulos.

---

### 🌳 A Árvore de Importações

#### Conceito Fundamental

A estrutura de importações de um projeto pode ser visualizada como uma **árvore hierárquica**, onde:

```
                    📦 A (Raiz)
                   /           \
              📦 B              📦 C
             / | \               |
        📦 D 📦 E 📦 F         📦 G
         |    |    |            |
      [libs] [libs] [libs]   [libs]
```

#### Elementos da Árvore

**🌲 Raiz (Root)**
- **Arquivo Principal** (ex: `app.py`, `main.py`, `index.js`)
- **Características:**
  - Mais complexo e encapsulado
  - Orquestrador do sistema
  - Importa múltiplos módulos do projeto
  - Contém lógica de coordenação entre componentes
  - Decide "o quê" fazer, delegando "como" fazer

**🌿 Galhos (Branches)**
- **Módulos Intermediários** (ex: `gui/`, `core/`, `utils/`)
- **Características:**
  - Complexidade média
  - Importam outros módulos do projeto
  - Fornecem funcionalidade especializada
  - Abstraem detalhes de implementação

**🍃 Folhas (Leaves)**
- **Módulos Terminais** (ex: `button.py`, `validator.py`, `helpers.py`)
- **Características:**
  - Mais simples e específicos
  - **NÃO importam** arquivos do próprio projeto
  - **SIM importam** bibliotecas externas (Numpy, Pandas, etc.)
  - Fornecem funcionalidade atômica
  - São reutilizáveis e testáveis independentemente

---

### 📊 Exemplo Prático

#### Estrutura Hierárquica

```python
# A.py (RAIZ) - Arquivo principal
from B import feature_x
from C import feature_y

def main():
    """Orquestrador - coordena B e C"""
    result_x = feature_x.process()
    result_y = feature_y.process()
    combine(result_x, result_y)
```

```python
# B.py (GALHO) - Módulo intermediário
from D import validator
from E import transformer
from F import calculator

def feature_x():
    """Especialista - coordena D, E, F"""
    data = validator.validate_input()
    transformed = transformer.transform(data)
    return calculator.compute(transformed)
```

```python
# D.py (FOLHA) - Módulo terminal
import re  # Biblioteca padrão
import numpy as np  # Biblioteca externa

def validate_input(data):
    """Função atômica - não importa arquivos do projeto"""
    pattern = re.compile(r'^\d+$')
    return np.array([x for x in data if pattern.match(x)])
```

#### Características por Nível

| Nível | Arquivo | Importa Projeto | Importa Externo | Complexidade | Papel |
|-------|---------|-----------------|-----------------|--------------|-------|
| 0 (Raiz) | A | B, C | Raramente | Alta | Orquestrador |
| 1 (Galho) | B, C | D, E, F, G | Às vezes | Média | Coordenador |
| 2 (Folha) | D, E, F, G | ❌ Nunca | ✅ Sempre | Baixa | Executor |

---

### 🔄 Abordagens de Desenvolvimento

#### 🔽 Top-Down (De Cima para Baixo)

**Começa pela raiz e desce até as folhas**

```
Processo:
1. Definir A (o quê o sistema faz)
2. Identificar necessidades (B, C)
3. Decompor B em (D, E, F)
4. Implementar folhas (D, E, F, G)
```

**Vantagens:**
- ✅ Arquitetura clara desde o início
- ✅ Facilita planejamento de alto nível
- ✅ Identifica dependências cedo

**Desvantagens:**
- ❌ Pode criar interfaces sem implementação
- ❌ Dificulta testes iniciais
- ❌ Risco de over-engineering

---

#### 🔼 Bottom-Up (De Baixo para Cima)

**Começa pelas folhas e sobe até a raiz**

```
Processo:
1. Implementar D, E, F, G (componentes básicos)
2. Combinar em B, C (funcionalidades)
3. Orquestrar em A (sistema completo)
```

**Vantagens:**
- ✅ Componentes testáveis desde o início
- ✅ Reutilização natural
- ✅ Menos desperdício de código

**Desvantagens:**
- ❌ Arquitetura emerge tardiamente
- ❌ Risco de componentes não integráveis
- ❌ Dificuldade em visualizar o todo

---

#### ↔️ Middle-Out (Do Meio para Fora)

**Começa pelos galhos e expande em ambas direções**

```
Processo:
1. Identificar funcionalidade central (B)
2. ↓ Implementar componentes necessários (D, E, F)
3. ↑ Criar orquestrador (A)
4. Repetir para outras funcionalidades (C, G)
```

**Vantagens:**
- ✅ Balanceia visão geral e detalhes
- ✅ Iterativo e adaptável
- ✅ Reduz risco de ambas abordagens extremas

**Desvantagens:**
- ❌ Requer experiência para identificar "o meio"
- ❌ Pode criar inconsistências
- ❌ Exige refatorações frequentes

---

### 🎯 Princípios de Design

#### 1. **Princípio da Profundidade**

> "Quanto mais próximo da raiz, mais complexo e orquestrador.  
> Quanto mais próximo das folhas, mais simples e executor."

```
Raiz (A):     if condition: B.do() else: C.do()  ← Decisão
Galho (B):    return D.compute(E.prepare(data))  ← Coordenação
Folha (D):    return sum(numbers) / len(numbers) ← Execução
```

#### 2. **Princípio da Independência**

> "Folhas não dependem de outras folhas do projeto.  
> Folhas podem depender apenas de bibliotecas externas."

❌ **Errado:**
```python
# D.py (folha)
from E import helper  # Dependência entre folhas!
```

✅ **Correto:**
```python
# B.py (galho)
from D import function_d
from E import helper

def feature():
    return function_d(helper.prepare())  # Galho coordena folhas
```

#### 3. **Princípio da Responsabilidade Única**

> "Cada nível tem seu papel distinto."

| Nível | Responsabilidade | Pergunta que Responde |
|-------|------------------|----------------------|
| Raiz | Orquestração | "O que o sistema faz?" |
| Galho | Coordenação | "Como as partes se conectam?" |
| Folha | Execução | "Como fazer X especificamente?" |

---

### 📏 Métricas de Qualidade

#### Indicadores de Boa Arquitetura

✅ **Árvore Balanceada:**
- Profundidade 2-4 níveis
- Largura proporcional à complexidade
- Sem folhas que importam outras folhas

✅ **Separação Clara:**
```
Raiz:  Alta complexidade + Baixa execução
Folha: Baixa complexidade + Alta execução
```

✅ **Facilidade de Teste:**
- Folhas testáveis isoladamente
- Galhos testáveis com mocks
- Raiz testável com integração

#### Indicadores de Problemas

❌ **Árvore Degenerada (Linear):**
```
A → B → C → D → E → F  # Muito profundo!
```

❌ **Folhas Gordas:**
```python
# D.py - 500 linhas, importa E, F, G  # É galho, não folha!
```

❌ **Raiz Magra:**
```python
# A.py - 10 linhas  # Deveria orquestrar mais!
```

---

### 📖 Conclusão das Seções

A **Organização Ordinal de Tarefas** e a **Analogia da Árvore de Importações** fornecem modelos mentais poderosos para:

1. **Organizar** tarefas do mais simples ao mais complexo
2. **Compreender** arquitetura existente
3. **Planejar** novos módulos
4. **Refatorar** código organicamente
5. **Paralelizar** desenvolvimento para acelerar entregas
6. **Comunicar** decisões de design claramente

---

## 💡 Boas Práticas de Programação para IAs

> **Esta seção contém recomendações específicas para melhorar a qualidade do código gerado por inteligências artificiais.**

### 1. 📖 **Código Legível e Autodocumentado**

**Por quê importante**: IAs devem produzir código que humanos possam entender e manter facilmente.

**Práticas**:
- ✅ **Nomes descritivos**: Use nomes que explicam o propósito
  ```python
  # ❌ RUIM
  def proc(d, x):
      return d[x] if x in d else None
  
  # ✅ BOM
  def get_user_preference(preferences_dict, preference_key):
      """Retorna preferência do usuário ou None se não existir."""
      return preferences_dict.get(preference_key)
  ```

- ✅ **Funções pequenas e focadas**: Uma função = uma responsabilidade
  ```python
  # ❌ RUIM - Função faz múltiplas coisas
  def process_user_data(user):
      # valida
      # transforma
      # salva no banco
      # envia email
      # registra log
      pass  # 150 linhas
  
  # ✅ BOM - Funções especializadas
  def validate_user_data(user): pass
  def transform_user_data(user): pass
  def save_user_to_database(user): pass
  def send_welcome_email(user): pass
  def log_user_registration(user): pass
  ```

- ✅ **Evitar "números mágicos"**: Use constantes nomeadas
  ```python
  # ❌ RUIM
  if user.age > 18 and balance < 1000:
      apply_fee(balance * 0.05)
  
  # ✅ BOM
  MINIMUM_ADULT_AGE = 18
  BALANCE_THRESHOLD = 1000
  SERVICE_FEE_RATE = 0.05
  
  if user.age > MINIMUM_ADULT_AGE and balance < BALANCE_THRESHOLD:
      apply_fee(balance * SERVICE_FEE_RATE)
  ```

### 2. 🎯 **Convenções de Nomenclatura Consistentes**

**Por quê importante**: Consistência facilita navegação e compreensão do código.

**Práticas por linguagem**:

**Python**:
- ✅ `snake_case` para funções e variáveis
- ✅ `PascalCase` para classes
- ✅ `SCREAMING_SNAKE_CASE` para constantes
- ✅ `_private_method` para métodos privados

**JavaScript/TypeScript**:
- ✅ `camelCase` para funções e variáveis
- ✅ `PascalCase` para classes e componentes
- ✅ `SCREAMING_SNAKE_CASE` para constantes
- ✅ `_privateMethod` ou `#privateField` para privados

**Convenções gerais**:
- ✅ Verbos para funções: `get_user()`, `calculate_total()`, `validate_input()`
- ✅ Substantivos para classes: `UserManager`, `PaymentProcessor`
- ✅ Booleanos com prefixos: `is_valid`, `has_permission`, `can_edit`

### 3. 🛡️ **Tratamento de Erros Robusto**

**Por quê importante**: Código em produção deve lidar graciosamente com falhas.

**Práticas**:
- ✅ **Sempre validar entrada**:
  ```python
  def divide(a, b):
      if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
          raise TypeError("Argumentos devem ser números")
      if b == 0:
          raise ValueError("Divisor não pode ser zero")
      return a / b
  ```

- ✅ **Usar exceções específicas**:
  ```python
  # ❌ RUIM - Exceção genérica
  try:
      process_payment(amount)
  except Exception as e:
      print("Erro")
  
  # ✅ BOM - Exceções específicas
  try:
      process_payment(amount)
  except PaymentDeclinedError as e:
      notify_user("Pagamento recusado")
  except InsufficientFundsError as e:
      notify_user("Saldo insuficiente")
  except NetworkError as e:
      retry_payment(amount)
  ```

- ✅ **Logging adequado**:
  ```python
  import logging
  
  try:
      result = risky_operation()
  except Exception as e:
      logging.error(f"Falha em risky_operation: {e}", exc_info=True)
      raise  # Re-raise para permitir handling em nível superior
  ```

### 4. 🧪 **Estratégias de Teste Eficazes**

**Por quê importante**: Testes garantem que o código funciona e continua funcionando.

**Práticas**:
- ✅ **Testes unitários para lógica de negócio**:
  ```python
  def test_calculate_discount():
      # Arrange
      original_price = 100
      discount_rate = 0.2
      
      # Act
      final_price = calculate_discount(original_price, discount_rate)
      
      # Assert
      assert final_price == 80
  ```

- ✅ **Testar edge cases**:
  ```python
  def test_edge_cases():
      assert calculate_discount(0, 0.5) == 0  # Preço zero
      assert calculate_discount(100, 0) == 100  # Desconto zero
      assert calculate_discount(100, 1.0) == 0  # Desconto 100%
      
      with pytest.raises(ValueError):
          calculate_discount(100, -0.1)  # Desconto negativo
      
      with pytest.raises(ValueError):
          calculate_discount(-100, 0.1)  # Preço negativo
  ```

- ✅ **Mocks para dependências externas**:
  ```python
  from unittest.mock import Mock, patch
  
  def test_send_notification():
      with patch('email_service.send') as mock_send:
          notify_user("user@example.com", "Test message")
          mock_send.assert_called_once()
  ```

### 5. 🔒 **Segurança em Primeiro Lugar**

**Por quê importante**: Vulnerabilidades podem ter consequências graves.

**Práticas**:
- ✅ **Nunca confiar em input do usuário**:
  ```python
  # ❌ RUIM - SQL Injection
  query = f"SELECT * FROM users WHERE id = {user_id}"
  
  # ✅ BOM - Parametrização
  query = "SELECT * FROM users WHERE id = ?"
  cursor.execute(query, (user_id,))
  ```

- ✅ **Secrets em variáveis de ambiente**:
  ```python
  # ❌ RUIM
  API_KEY = "sk-1234567890abcdef"  # Hardcoded
  
  # ✅ BOM
  import os
  API_KEY = os.getenv('API_KEY')
  if not API_KEY:
      raise ValueError("API_KEY não configurada")
  ```

- ✅ **Sanitizar output para prevenir XSS**:
  ```python
  from html import escape
  
  # ❌ RUIM
  html = f"<div>Hello {user_name}</div>"
  
  # ✅ BOM
  html = f"<div>Hello {escape(user_name)}</div>"
  ```

### 6. ⚡ **Otimização de Performance**

**Por quê importante**: Código lento = usuários insatisfeitos.

**Práticas**:
- ✅ **Escolher estrutura de dados correta**:
  ```python
  # ❌ RUIM - Busca em lista O(n)
  if user_id in user_list:  # 1000 comparações
      # ...
  
  # ✅ BOM - Busca em set O(1)
  if user_id in user_set:  # 1 comparação
      # ...
  ```

- ✅ **Evitar loops desnecessários**:
  ```python
  # ❌ RUIM - Loop duplo O(n²)
  for item in list1:
      for item2 in list2:
          if item == item2:
              # ...
  
  # ✅ BOM - Set intersection O(n)
  common_items = set(list1) & set(list2)
  for item in common_items:
      # ...
  ```

- ✅ **Lazy loading quando apropriado**:
  ```python
  # ❌ RUIM - Carrega tudo na memória
  all_users = User.objects.all()  # 1 milhão de registros
  for user in all_users:
      process(user)
  
  # ✅ BOM - Iterator que carrega sob demanda
  for user in User.objects.iterator():
      process(user)
  ```

### 7. 📝 **Documentação Clara e Útil**

**Por quê importante**: Código é lido muito mais vezes do que é escrito.

**Práticas**:
- ✅ **Docstrings completos**:
  ```python
  def calculate_shipping(weight, distance, express=False):
      """
      Calcula o custo de envio baseado em peso e distância.
      
      Args:
          weight (float): Peso do pacote em kg
          distance (float): Distância em km
          express (bool): Se True, usa envio expresso (default: False)
      
      Returns:
          float: Custo de envio em reais
      
      Raises:
          ValueError: Se peso ou distância for negativo
      
      Examples:
          >>> calculate_shipping(2.5, 100)
          25.0
          >>> calculate_shipping(2.5, 100, express=True)
          37.5
      """
      if weight < 0 or distance < 0:
          raise ValueError("Peso e distância devem ser positivos")
      
      base_cost = weight * distance * 0.1
      return base_cost * 1.5 if express else base_cost
  ```

- ✅ **Comentários explicam "por quê", não "o quê"**:
  ```python
  # ❌ RUIM - Comenta o óbvio
  x = x + 1  # Incrementa x
  
  # ✅ BOM - Explica o motivo
  # Incrementa o contador para incluir o elemento atual na contagem
  # pois o range() exclui o último elemento
  x = x + 1
  ```

- ✅ **README com exemplos práticos**:
  ```markdown
  # Como usar
  
  ## Instalação
  ```bash
  pip install mypackage
  ```
  
  ## Exemplo básico
  ```python
  from mypackage import Calculator
  
  calc = Calculator()
  result = calc.add(2, 3)
  print(result)  # Output: 5
  ```
  ```

### 8. 🏗️ **Organização e Modularidade**

**Por quê importante**: Código organizado é mais fácil de manter e escalar.

**Práticas**:
- ✅ **Separação de responsabilidades**:
  ```
  project/
  ├── models/       # Estruturas de dados
  ├── services/     # Lógica de negócio
  ├── controllers/  # Coordenação de fluxo
  ├── views/        # Interface com usuário
  ├── utils/        # Funções auxiliares
  └── tests/        # Testes automatizados
  ```

- ✅ **DRY (Don't Repeat Yourself)**:
  ```python
  # ❌ RUIM - Código duplicado
  def process_order_a():
      validate()
      calculate()
      save()
  
  def process_order_b():
      validate()
      calculate()
      save()
  
  # ✅ BOM - Código reutilizado
  def process_order_common():
      validate()
      calculate()
      save()
  
  def process_order_a():
      process_order_common()
      # lógica específica A
  
  def process_order_b():
      process_order_common()
      # lógica específica B
  ```

- ✅ **Princípio da responsabilidade única**:
  ```python
  # ❌ RUIM - Classe faz muitas coisas
  class User:
      def __init__(self): pass
      def save_to_database(self): pass
      def send_email(self): pass
      def generate_pdf_report(self): pass
  
  # ✅ BOM - Classes especializadas
  class User:
      def __init__(self): pass
  
  class UserRepository:
      def save(self, user): pass
  
  class EmailService:
      def send(self, to, message): pass
  
  class ReportGenerator:
      def generate_pdf(self, user): pass
  ```

### 9. 🔄 **Controle de Versão Efetivo**

**Por quê importante**: Histórico limpo facilita debugging e colaboração.

**Práticas**:
- ✅ **Commits atômicos e descritivos**:
  ```bash
  # ❌ RUIM
  git commit -m "fixes"
  git commit -m "updates"
  
  # ✅ BOM
  git commit -m "feat: adiciona validação de email no formulário de cadastro"
  git commit -m "fix: corrige cálculo de desconto para valores acima de R$ 1000"
  ```

- ✅ **Branches para features**:
  ```bash
  # Criar branch para nova funcionalidade
  git checkout -b feature/user-authentication
  
  # Desenvolver e commitar
  git commit -m "feat: implementa login com JWT"
  
  # Merge após review
  git checkout main
  git merge feature/user-authentication
  ```

- ✅ **.gitignore apropriado**:
  ```gitignore
  # Python
  __pycache__/
  *.pyc
  .env
  venv/
  
  # JavaScript
  node_modules/
  dist/
  .env.local
  
  # IDEs
  .vscode/
  .idea/
  *.swp
  
  # OS
  .DS_Store
  Thumbs.db
  ```

### 10. 📦 **Gerenciamento de Dependências**

**Por quê importante**: Dependências mal gerenciadas causam problemas de compatibilidade.

**Práticas**:
- ✅ **Fixar versões**:
  ```
  # ❌ RUIM - requirements.txt
  flask
  requests
  
  # ✅ BOM - requirements.txt
  flask==2.3.2
  requests==2.31.0
  ```

- ✅ **Usar ambientes virtuais**:
  ```bash
  # Python
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  
  # Node.js
  npm install  # Usa package-lock.json
  ```

- ✅ **Verificar vulnerabilidades**:
  ```bash
  # Python
  pip install pip-audit
  pip-audit
  
  # Node.js
  npm audit
  npm audit fix
  ```

### 11. 🔄 **Refatoração Frequente de Código**

**Por quê importante**: Código que não é refatorado regularmente tende a se deteriorar com o tempo, tornando-se difícil de manter, entender e evoluir.

> **CRÍTICO PARA IAs**: Lembre-se **frequentemente** de refatorar o código durante o desenvolvimento para manter a qualidade e evitar acúmulo de dívida técnica.

**Práticas obrigatórias**:

- ✅ **Evitar arquivos excessivamente grandes**:
  ```
  # 🚨 ALERTAS DE TAMANHO
  - Arquivo > 500 linhas → Considere dividir
  - Arquivo > 1000 linhas → DEVE dividir
  - Classe > 300 linhas → Refatore em classes menores
  - Função > 50 linhas → Divida em funções auxiliares
  ```
  
  **Exemplo de refatoração**:
  ```python
  # ❌ RUIM - Arquivo com 1500 linhas
  # user_manager.py (tudo em um arquivo)
  class UserManager:
      def create_user(): pass  # 100 linhas
      def validate_user(): pass  # 150 linhas
      def authenticate_user(): pass  # 200 linhas
      def send_email(): pass  # 100 linhas
      # ... mais 950 linhas
  
  # ✅ BOM - Dividido em módulos especializados
  # user/
  #   __init__.py
  #   manager.py (200 linhas)
  #   validator.py (150 linhas)
  #   authenticator.py (200 linhas)
  #   notifications.py (100 linhas)
  ```

- ✅ **Aumentar coesão (Single Responsibility Principle)**:
  ```python
  # ❌ RUIM - Baixa coesão (faz muitas coisas diferentes)
  class OrderProcessor:
      def process_order(self):
          self.validate_payment()
          self.send_email()
          self.update_inventory()
          self.generate_invoice()
          self.log_analytics()
  
  # ✅ BOM - Alta coesão (cada classe tem uma responsabilidade)
  class PaymentValidator:
      def validate(self): pass
  
  class EmailNotifier:
      def send_order_confirmation(self): pass
  
  class InventoryManager:
      def update_stock(self): pass
  
  class InvoiceGenerator:
      def generate(self): pass
  
  class AnalyticsLogger:
      def log_order(self): pass
  ```

- ✅ **Melhorar legibilidade constantemente**:
  ```python
  # ❌ RUIM - Difícil de entender
  def p(d, x, y):
      return sum([d[i][x] * d[i][y] for i in range(len(d)) if x in d[i] and y in d[i]])
  
  # ✅ BOM - Auto-explicativo
  def calculate_correlation_between_features(dataset, feature_x, feature_y):
      """
      Calcula a correlação entre duas features em um dataset.
      
      Args:
          dataset: Lista de dicionários contendo features
          feature_x: Nome da primeira feature
          feature_y: Nome da segunda feature
      
      Returns:
          float: Soma dos produtos das features quando ambas existem
      """
      correlation_sum = 0
      for data_point in dataset:
          if feature_x in data_point and feature_y in data_point:
              correlation_sum += data_point[feature_x] * data_point[feature_y]
      return correlation_sum
  ```

- ✅ **Eliminar redundâncias e aumentar reutilização**:
  ```python
  # ❌ RUIM - Código duplicado (redundância)
  def get_active_users():
      users = db.query("SELECT * FROM users")
      active = [u for u in users if u.status == 'active' and u.verified == True]
      return active
  
  def get_active_admins():
      users = db.query("SELECT * FROM users")
      active = [u for u in users if u.status == 'active' and u.verified == True and u.role == 'admin']
      return active
  
  # ✅ BOM - Código reutilizável (DRY - Don't Repeat Yourself)
  def get_verified_active_users(role=None):
      """Retorna usuários ativos e verificados, opcionalmente filtrados por role."""
      users = db.query("SELECT * FROM users")
      filtered = [u for u in users if u.status == 'active' and u.verified == True]
      
      if role:
          filtered = [u for u in filtered if u.role == role]
      
      return filtered
  
  def get_active_users():
      return get_verified_active_users()
  
  def get_active_admins():
      return get_verified_active_users(role='admin')
  ```

- ✅ **Hierarquizar código em pastas e diretórios**:
  ```
  # ❌ RUIM - Tudo na raiz (difícil de navegar)
  project/
    main.py
    user_stuff.py
    payment_things.py
    email_sender.py
    validators.py
    helpers.py
    utils.py
    config.py
    constants.py
  
  # ✅ BOM - Hierarquia lógica (fácil de entender e manter)
  project/
    main.py
    config/
      __init__.py
      settings.py
      constants.py
    core/
      __init__.py
      models.py
      exceptions.py
    features/
      users/
        __init__.py
        manager.py
        validator.py
      payments/
        __init__.py
        processor.py
        validator.py
    services/
      email/
        __init__.py
        sender.py
        templates.py
    utils/
      __init__.py
      helpers.py
      formatters.py
  ```

- ✅ **Procurar por código órfão após refatoração** (⭐ **OBRIGATÓRIO**):
  
  > **CRÍTICO**: Após qualquer refatoração, é **OBRIGATÓRIO** procurar por código órfão - código que foi implementado mas não está mais sendo utilizado.
  
  **O que é código órfão?**
  - ❌ Funções não utilizadas (definidas mas nunca chamadas)
  - ❌ Variáveis não utilizadas (declaradas mas nunca referenciadas)
  - ❌ Imports não utilizados (importados mas nunca usados)
  - ❌ Código morto/inalcançável (unreachable code)
  - ❌ Classes não instanciadas (definidas mas nunca criadas)
  - ❌ Métodos não chamados (definidos mas nunca invocados)
  
  **Por quê procurar código órfão?**
  - ✅ **Reduz complexidade**: Menos código = mais fácil entender
  - ✅ **Melhora manutenção**: Não gastar tempo em código não usado
  - ✅ **Evita confusão**: Código órfão pode enganar desenvolvedores
  - ✅ **Performance**: Menos código = startup mais rápido
  - ✅ **Segurança**: Código órfão pode conter vulnerabilidades esquecidas
  
  **Ferramentas para detectar código órfão**:
  ```bash
  # Python - Código não utilizado (funções, classes, variáveis)
  pip install vulture
  vulture src/ --min-confidence 80
  # Saída: funções/classes/variáveis não utilizadas
  
  # Python - Imports não utilizados
  pip install autoflake
  autoflake --remove-all-unused-imports --check -r src/
  # Ou usar pylint
  pylint --disable=all --enable=unused-import src/
  
  # JavaScript/TypeScript - Código não utilizado
  npm install -g ts-prune  # Para TypeScript
  ts-prune
  # Ou ESLint
  npm run lint -- --rule 'no-unused-vars: error'
  
  # Para qualquer linguagem - Buscar definições não usadas
  # 1. Gerar lista de definições (funções, classes)
  # 2. Buscar referências a cada definição no código
  # 3. Se nenhuma referência encontrada → código órfão
  ```
  
  **Exemplo de uso (Python)**:
  ```python
  # Antes da refatoração - arquivo com 500 linhas
  
  # Refatoração: dividiu em 3 arquivos menores
  # Agora procurar código órfão:
  
  $ vulture src/ --min-confidence 80
  src/old_module.py:45: unused function 'process_legacy_format' (100% confidence)
  src/utils.py:123: unused function 'deprecated_helper' (90% confidence)
  src/models.py:67: unused class 'OldDataModel' (100% confidence)
  
  # Ação: Remover ou documentar por que manter
  # Se realmente não usado → DELETAR
  # Se será usado futuro → Marcar com comentário e issue
  ```
  
  **Checklist de código órfão** (executar APÓS refatoração):
  ```markdown
  - [ ] Executar vulture (Python) ou ts-prune (TypeScript)
  - [ ] Revisar funções não utilizadas (confirmar se realmente órfãs)
  - [ ] Remover imports não utilizados (autoflake ou ferramenta similar)
  - [ ] Verificar classes não instanciadas
  - [ ] Procurar código comentado antigo (também é código órfão)
  - [ ] Documentar se algum código "órfão" deve ser mantido (ex: API pública)
  ```
  
  **Quando NÃO remover**:
  - ✅ **APIs públicas**: Mesmo não usadas internamente, clientes externos podem usar
  - ✅ **Hooks/callbacks**: Podem ser chamados por frameworks
  - ✅ **Código de teste**: Helpers de teste podem parecer não usados
  - ✅ **Código planejado**: Se há issue/task para usar em breve, manter (mas documentar)

**Quando refatorar**:

1. **Durante implementação de nova feature**:
   - Antes de adicionar código novo, verifique se os arquivos existentes estão organizados
   - Se encontrar código mal estruturado, refatore ANTES de adicionar nova funcionalidade

2. **Após completar uma funcionalidade**:
   - Revise o código implementado
   - Identifique oportunidades de melhoria (DRY, SRP, nomes melhores)
   - Refatore imediatamente enquanto o contexto está fresco
   - **⭐ OBRIGATÓRIO**: Procure por código órfão (vulture, autoflake, etc.)

3. **Ao revisar código (Etapas 7 e 8)**:
   - Use os 9 critérios de qualidade como guia
   - Se detectar redundância, menor coesão ou maior acoplamento → Refatore

4. **Antes de fazer commit (Etapa 13)**:
   - Último checkpoint: código está o mais limpo possível?
   - Há algo que pode ser simplificado?

5. **Periodicidade mínima**:
   - ⚠️ **NUNCA** deixe passar mais de 3-5 funcionalidades sem refatorar
   - 🚨 Se projeto tem > 10 arquivos com > 500 linhas → PRIORIZE refatoração
   - ⭐ **Sempre procure código órfão após refatorar** (não opcional)

**Benefícios da refatoração frequente**:
- ✅ **Manutenção mais simples**: Código organizado é mais fácil de modificar
- ✅ **Menos bugs**: Código limpo tem menos lugares para bugs se esconderem
- ✅ **Onboarding rápido**: Novos desenvolvedores entendem o código mais rápido
- ✅ **Velocidade**: Paradoxalmente, refatorar frequentemente ACELERA o desenvolvimento
- ✅ **Validação facilitada**: Código modular é mais fácil de testar e verificar

**Ferramentas para identificar necessidade de refatoração**:
```bash
# Python - Complexidade ciclomática
pip install radon
radon cc . -a -nb  # Mostrar funções complexas

# Python - Código duplicado
pip install pylint
pylint --disable=all --enable=duplicate-code .

# Python - Código morto
pip install vulture
vulture .

# JavaScript - Análise de complexidade
npm install -g complexity-report
cr --format json src/
```

### 🎯 **Checklist Rápido para IAs**

Antes de gerar/commitar código, verificar:

- [ ] Nomes são descritivos e seguem convenções da linguagem?
- [ ] Funções têm responsabilidade única e são pequenas?
- [ ] Há tratamento de erros para casos excepcionais?
- [ ] Código está testado (unitários + edge cases)?
- [ ] Não há vulnerabilidades de segurança óbvias?
- [ ] Performance é aceitável (sem algoritmos O(n²) desnecessários)?
- [ ] Há documentação (docstrings, comentários úteis)?
- [ ] Código está organizado em módulos lógicos?
- [ ] **Código foi refatorado recentemente?** (arquivos < 500 linhas, sem duplicação)
- [ ] **Hierarquia de pastas está lógica?** (separação clara de responsabilidades)
- [ ] Commits são descritivos (conventional commits)?
- [ ] Dependências estão com versões fixadas?

### 📚 **Recursos Adicionais**

- **Clean Code** (Robert C. Martin) - Princípios de código limpo
- **SOLID Principles** - Orientação a objetos bem feita
- **Design Patterns** (GoF) - Soluções comuns para problemas comuns
- **OWASP Top 10** - Principais vulnerabilidades de segurança
- **PEP 8** (Python) - Guia de estilo Python
- **Google Style Guides** - Guias de estilo por linguagem

---

## 📚 Documentos Relacionados

- 📘 **PROTOCOLO_SIMPLICIDADE_1.md**: Base (13 etapas) - Para protótipos/interno
- 📕 **PROTOCOLO_SIMPLICIDADE_2.md**: Avançado (23 etapas) - Para equipes enterprise
- 📗 **PROTOCOLO_SIMPLICIDADE_3.md**: Híbrido (16 etapas) - **Solo dev em produção** ⭐

---

**Versão**: 3.2  
**Última atualização**: 16 de Dezembro de 2025  
**Mantido por**: Josué Amaral  
**Status**: ATIVO - Protocolo para solo developer em produção
