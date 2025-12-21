# Protocolo Simplicidade 2

**Autor**: Josué Amaral  
**Data de Criação**: 02 de Dezembro de 2025  
**Baseado em**: Protocolo Simplicidade 1 v2.0  
**Versão**: 2.2  
**Última Atualização**: 10 de Dezembro de 2025  
**Objetivo**: Metodologia profissional AVANÇADA para desenvolvimento incremental de qualidade com foco em segurança, performance e melhoria contínua

**Diferenças do Simplicidade 1**:
- ✅ **10 novas etapas opcionais** para projetos complexos e críticos
- ✅ **Matriz de Decisão** objetiva para escolha de tarefas
- ✅ **Checklist de Segurança** (OWASP Top 10)
- ✅ **CI/CD com Quality Gates** automáticos
- ✅ **ADR** (Architecture Decision Records)
- ✅ **Profiling e Otimização** para features críticas
- ✅ **Rollback Plans** documentados
- ✅ **Retrospectivas de Sprint** (melhoria contínua)
- ✅ **Code Review por Pares** (se houver equipe)
- ✅ **Checklist de Acessibilidade** (GUI)

---

## 📊 Comparação dos 3 Protocolos

| Aspecto | Simplicidade 1 | Simplicidade 2 | Simplicidade 3 |
|---------|----------------|----------------|----------------|
| **Etapas** | 13 obrigatórias | 13 obrig + 10 opc | 16 obrig + 3 opc |
| **Cenário** | Protótipos/interno | **Equipes enterprise** | Solo em produção |
| **Security** | ❌ Não | ✅ OWASP obrigatório | ✅ OWASP obrigatório |
| **CI/CD** | ❌ Não | ✅ Obrigatório | ✅ Obrigatório |
| **Rollback** | ❌ Não | ✅ Obrigatório | ✅ Obrigatório |
| **Code Review** | ❌ Não | ✅ **Pares obrigatório** | ❌ Solo |
| **Retrospectives** | ❌ Não | ✅ **Equipe formal** | ❌ Solo |
| **Accessibility** | ❌ Não | ✅ WCAG 2.1 | ❌ Opcional |
| **API Docs** | ❌ Não | ✅ Sphinx formal | ❌ Docstrings |
| **Overhead** | Baixo | **Alto** | Médio |
| **Produção** | ❌ Não recomendado | ✅ **Empresas** | ✅ Solo devs |
| **Time/Task** | ~2-3h | ~4-6h | ~3-4h |
| **Melhor Para** | Aprender, prototipar | Equipes grandes | Solo em produção |

---

## 🎯 Quando Usar Cada Protocolo?

### **Protocolo Simplicidade 1** (13 etapas obrigatórias)
**Use para**:
- ✅ Projetos solo ou pequena equipe (1-3 devs)
- ✅ Features simples a médias
- ✅ Prototipagem rápida
- ✅ Primeiro desenvolvimento de uma funcionalidade
- ✅ Quando velocidade é mais importante que perfeição
- ✅ Projetos internos não-críticos

**Não use para**:
- ❌ Aplicações críticas de produção
- ❌ Sistemas com requisitos de segurança
- ❌ Features de alto impacto/risco
- ❌ Projetos com equipes grandes (>5 devs)

### **Protocolo Simplicidade 2** (13 obrigatórias + 10 opcionais = 23 etapas)
**Use para**:
- ✅ Aplicações **críticas de produção** com equipe
- ✅ Sistemas com **dados sensíveis** (LGPD, GDPR, PCI-DSS)
- ✅ Features de **alto impacto/risco**
- ✅ Projetos com equipes **médias/grandes** (3+ devs)
- ✅ **Bibliotecas/APIs públicas** com múltiplos usuários
- ✅ Sistemas com **requisitos de performance** críticos
- ✅ Aplicações **comerciais/enterprise**
- ✅ Projetos com **conformidade regulatória** (ISO, SOC2)
- ✅ Código que requer **auditoria externa**

**Não use para**:
- ❌ **Prototipagem rápida** (overhead desnecessário)
- ❌ Scripts **descartáveis** ou uso único
- ❌ Projetos **pessoais simples**
- ❌ **Solo developer** sem equipe → Use **Simplicidade 3** (menos overhead)
- ❌ Apps **internos não-críticos** → Use **Simplicidade 1**

**Rationale**: Simplicidade 2 tem **máxima qualidade e segurança** através de:
- **Code Review por Pares**: Detecta bugs que desenvolvedor solo não vê
- **Retrospectivas Formais**: Melhoria contínua em equipe
- **ADR Formais**: Documentação de decisões arquiteturais para longo prazo
- **Accessibility WCAG**: Conformidade legal para apps públicos
- **API Docs Sphinx**: Documentação profissional para bibliotecas

Porém, esse rigor tem **custo**: ~4-6h por task vs ~2-3h no Simplicidade 1. Para **solo developer**, esse overhead não compensa - use **Simplicidade 3** que mantém segurança de produção sem burocracia de equipe.

---

**Changelog v2.2** (10/12/2025):
- ✅ **[COMPLEMENTAÇÃO]** Adicionada tabela comparativa dos 3 protocolos (Simplicidade 1/2/3)
- ✅ Expandida seção "🎯 Quando Usar Simplicidade 2?"
- ✅ Critérios adicionais: Conformidade regulatória, auditoria externa, solo dev (use S3)
- ✅ Rationale detalhado: Por quê code review/ADR/accessibility valem o overhead de 4-6h
- ✅ Comparação: Simplicidade 2 vs 3 (equipe vs solo) com 12 aspectos analisados
- ✅ Inspiração: Conceitos adaptados do Simplicidade 3 v3.1 (tabelas, critérios, rationale)

**Changelog v2.1** (09/12/2025):
- ✅ **[ETAPA 3]** Adicionada recomendação para IA fornecer sugestões e palpites nas perguntas
- ✅ Formato recomendado: "❓ Pergunta + 💡 Sugestão da IA + Opções A/B/C"
- ✅ Rationale: Acelera decisões, reduz carga cognitiva, mantém consistência com código existente
- ✅ Classificação: **OPCIONAL mas ALTAMENTE RECOMENDADO**

**Changelog v2.0** (02/12/2025):
- ✅ **[NOVO PROTOCOLO]** Criado Protocolo Simplicidade 2 baseado em Simplicidade 1 v1.8
- ✅ **Etapa 2.5**: Matriz de Decisão para escolha objetiva de tarefas (ALTA PRIORIDADE)
- ✅ **Etapa 6.5**: Checklist de Segurança - OWASP Top 10 (ALTA PRIORIDADE)
- ✅ **Etapa 6.7**: Gerar Documentação de API (Sphinx/pdoc)
- ✅ **Etapa 8.5**: Checklist de Acessibilidade - WCAG 2.1
- ✅ **Etapa 9.5**: Code Review por Pares (Pull Request)
- ✅ **Etapa 10.5**: Profiling e Otimização (features críticas)
- ✅ **Etapa 10.6**: Validar Métricas de Qualidade - CI/CD (ALTA PRIORIDADE)
- ✅ **Etapa 11.5**: Criar ADR (Architecture Decision Record)
- ✅ **Etapa 12.5**: Documentar Rollback Plan
- ✅ **Etapa 13.5**: Retrospectiva de Sprint (melhoria contínua)
- ✅ **Total**: 13 etapas obrigatórias + 10 etapas opcionais = 23 etapas
- ✅ **Foco**: Segurança, Performance, Qualidade, Melhoria Contínua

---

**Changelogs Herdados do Simplicidade 1**:

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
A) ✅ Sim, incluir email para feedback (PADRÃO RECOMENDADO)
B) ✅ Sim, incluir GitHub Issues (para projetos open-source)
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

### 🔄 Estratégia de Divisão (Enterprise)

**Quando Aplicar** (Protocolo Simplicidade 2):
- ✅ Tarefa estimada em >6 horas (divide em 3+ sprints)
- ✅ Feature enterprise com múltiplos stakeholders
- ✅ Resposta muito longa (>1500 linhas de código)
- ✅ Múltiplas funcionalidades interdependentes
- ✅ Requer code review por pares em cada fase
- ✅ Risco de timeout ou limite de resposta

**Como Dividir** (Recursivamente com ADRs):

1. **Nível 1 - Épicos (2-4 semanas)**:
   ```
   Épico: "Sistema de Pagamentos Enterprise"
   ↓ Dividir em:
   ├── Sprint 1: Integração Stripe (6h)
   ├── Sprint 2: Webhooks e notificações (6h)
   ├── Sprint 3: Dashboard de transações (8h)
   ├── Sprint 4: Auditoria e compliance (6h)
   └── Sprint 5: Rollback e recovery (4h)
   
   Cada sprint → ADR documentado
   Cada sprint → Code review por pares
   Cada sprint → Deploy incremental
   ```

2. **Nível 2 - Sprints (4-8 horas)**:
   ```
   Sprint 1: Integração Stripe
   ↓ Dividir em:
   ├── Task 1.1: Setup API keys + secrets (1h)
   ├── Task 1.2: Checkout session endpoint (2h)
   ├── Task 1.3: Webhook receiver (2h)
   └── Task 1.4: Testes + Security checklist (1h)
   
   Cada task → Quality gates (CI/CD)
   ```

3. **Nível 3 - Tasks (<4 horas)** (se ainda muito grande):
   ```
   Task 1.2: Checkout session endpoint
   ↓ Dividir em:
   ├── Subtask 1.2.1: Schema de Order (30min)
   ├── Subtask 1.2.2: Validação de input (30min)
   ├── Subtask 1.2.3: Criação de session Stripe (1h)
   ├── Subtask 1.2.4: Logging e monitoring (30min)
   └── Subtask 1.2.5: Testes unitários (1h)
   ```

**Critério de Parada**:
- ⏱️ Tarefa pode ser completada em <4 horas (vs <3h no Simplicidade 1)
- 📝 Resposta cabe em limite razoável (<1000 linhas)
- ✅ Escopo claro, com critérios de aceitação definidos
- 🧪 Pode ser testada isoladamente
- 👥 Pode ser revisada por pares em <1h
- 🔒 Security checklist pode ser aplicado isoladamente
- 🤖 CI/CD pode validar isoladamente

**Princípios de Divisão Enterprise**:
1. **Independência**: Cada subtarefa deve ser deployável independentemente
2. **Coesão**: Subtarefas relacionadas devem estar próximas na sequência
3. **Valor Incremental**: Cada subtarefa deve adicionar valor mensurável
4. **Testabilidade**: Cada subtarefa deve ter 100% cobertura de testes
5. **Reversibilidade**: Cada subtarefa deve ter rollback plan (se crítica)
6. **Documentação**: Cada sprint deve ter ADR se houver decisão arquitetural
7. **Revisabilidade**: Cada subtarefa deve ter diff pequeno para code review

**Exemplo Prático Enterprise**:
```markdown
❌ RUIM - Épico muito grande (60h):
[ ] Implementar plataforma completa de e-commerce

✅ BOM - Dividido em épicos e sprints:

Épico 1 - Catálogo de Produtos (2 semanas):
├── Sprint 1.1 (6h): CRUD produtos + categorias
│   ├── ADR-001: Escolha de PostgreSQL
│   └── Rollback plan: N/A (não-crítico)
├── Sprint 1.2 (6h): Busca e filtros
│   └── ADR-002: ElasticSearch vs PostgreSQL full-text
└── Sprint 1.3 (4h): Upload de imagens (S3)
    └── Rollback plan: Reverter para storage local

Épico 2 - Carrinho de Compras (1 semana):
├── Sprint 2.1 (6h): Session-based cart
│   ├── ADR-003: Redis para sessions
│   └── Security checklist: Session fixation, CSRF
└── Sprint 2.2 (4h): Persistência e checkout
    └── Rollback plan: Fallback para in-memory

Épico 3 - Pagamentos (2 semanas):
├── Sprint 3.1 (6h): Integração Stripe
│   ├── ADR-004: Stripe vs PayPal
│   ├── Security checklist: PCI-DSS compliance
│   └── Rollback plan: CRÍTICO (feature flag)
├── Sprint 3.2 (6h): Webhooks
│   └── Security checklist: Webhook validation
└── Sprint 3.3 (4h): Dashboard transações
    └── Rollback plan: N/A (apenas visualização)

Cada Sprint:
- Code review por 2 pares
- CI/CD quality gates (80% coverage)
- Security scan (bandit + pip-audit)
- Deploy staging → produção
```

**Matriz de Decisão para Dividir**:
Use Matriz de Decisão (Etapa 2.5) quando há múltiplas formas de dividir:

| Divisão | Complexidade | Risco | Valor | Independência | **Score** |
|---------|--------------|-------|-------|---------------|-----------|
| **Por funcionalidade** | 3 | 2 | 5 | 5 | **23** 🟢 |
| Por camada (backend/frontend) | 2 | 4 | 3 | 2 | **17** 🟡 |
| Por equipe | 4 | 3 | 2 | 3 | **18** 🟡 |

**Por quê?**: Dividir tarefas enterprise garante entregas incrementais com valor, facilita code review, permite rollback granular, e mantém velocity estável em equipes grandes.

---

## 📋 Espinha Dorsal do Protocolo (24 Etapas: 14 Obrigatórias + 10 Opcionais)

### **Etapas Obrigatórias** (Protocolo Simplicidade 1):
1. 📚 Ler a documentação
2. ✅ Escolher tarefas mais simples
3. ❓ Fazer perguntas até sanar 100% das dúvidas
4. 🔍 Analisar e estudar o projeto
5. 🎯 Fazer sprints das tarefas mais simples
6. 💻 Implementar com arquitetura profissional (GoF + GRASP)
   - 6.6 🎨 **Ícones do Projeto** (OBRIGATÓRIO)
7. ⌨️ Verificar Implementação CLI + Revisão de Código (9 critérios)
8. 🖥️ Verificar Implementação GUI + Revisão de Código (9 critérios)
9. 🔗 Verificar Integração com Programa Principal
10. 🧪 Fazer testes (100% cobertura)
11. 🧹 Organizar pasta raiz
12. 📝 Preencher documentação
13. 🚀 Fazer commit e push

### **Etapas Opcionais Avançadas** (Simplicidade 2):
**2.5** 🎯 Matriz de Decisão (escolha objetiva) - **ALTA PRIORIDADE**  
**6.5** 🔒 Checklist de Segurança (OWASP) - **ALTA PRIORIDADE**  
**6.7** 📚 Gerar Documentação de API  
**8.5** ♿ Checklist de Acessibilidade (WCAG)  
**9.5** 👥 Code Review por Pares  
**10.5** ⚡ Profiling e Otimização  
**10.6** ✅ Métricas de Qualidade (CI/CD) - **ALTA PRIORIDADE**  
**11.5** 📋 Criar ADR (Decisões Arquiteturais)  
**12.5** 🔙 Rollback Plan  
**13.5** 🔄 Retrospectiva de Sprint

### 1️⃣ **Ler a Documentação**
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

### 2️⃣.5️⃣ **Matriz de Decisão para Escolha Objetiva de Tarefas** ⭐ NOVO - ALTA PRIORIDADE

**Problema**: "Mais simples" é subjetivo e pode levar a escolhas incorretas  
**Solução**: Matriz de pontuação objetiva com 5 critérios quantificáveis

**Critérios de Pontuação** (0-5 pontos cada):

1. **Simplicidade Técnica** (5=muito simples, 0=muito complexo)
   - Quantidade de código necessário
   - Complexidade algorítmica
   - Quantidade de conceitos novos

2. **Dependências** (5=zero dependências, 0=muitas)
   - Arquivos a modificar
   - Módulos que dependem desta feature
   - Bibliotecas externas necessárias

3. **Impacto** (5=alto impacto, 0=baixo)
   - Valor para o usuário final
   - Frequência de uso esperada
   - Benefício vs. esforço

4. **Clareza de Requisitos** (5=100% claro, 0=ambíguo)
   - Especificação completa
   - Exemplos de uso fornecidos
   - Critérios de aceitação definidos

5. **Risco** (5=zero risco, 0=alto risco)
   - Probabilidade de quebrar código existente
   - Reversibilidade da mudança
   - Impacto em features críticas

**Fórmula de Priorização**:
```
Prioridade = (Simplicidade × 2) + Dependências + (Impacto × 1.5) + Clareza + Risco

Pontuação Máxima: 35 pontos
Pontuação Mínima: 0 pontos
```

**Interpretação**:
- **30-35 pontos**: 🟢 IDEAL - Começar imediatamente
- **20-29 pontos**: 🟡 BOM - Considerar fortemente
- **10-19 pontos**: 🟠 MÉDIO - Avaliar contexto
- **0-9 pontos**: 🔴 COMPLEXO - Deixar por último

**Exemplo Prático de Aplicação**:

| Task | Simpl<br>(0-5) | Dep<br>(0-5) | Imp<br>(0-5) | Clar<br>(0-5) | Risc<br>(0-5) | **Score** | **Decisão** |
|------|---------------|--------------|--------------|---------------|---------------|-----------|-------------|
| **Tooltip Preview** | 5 | 5 | 3 | 5 | 5 | **33.5** 🟢 | **1º - COMEÇAR AQUI** |
| **Feature** | 3 | 4 | 4 | 5 | 4 | **26.0** 🟡 | 2º |
| **Editor Integrado** | 1 | 2 | 5 | 4 | 2 | **20.5** 🟡 | 3º |
| **IA Semântica** | 0 | 1 | 4 | 2 | 1 | **10.0** 🟠 | 4º - Deixar por último |

**Detalhamento do Exemplo "Tooltip Preview"**:
- **Simplicidade: 5** - Apenas adicionar QToolTip em widgets existentes
- **Dependências: 5** - Modificar apenas 1 arquivo GUI
- **Impacto: 3** - Melhora UX mas não é crítico
- **Clareza: 5** - Requisito 100% claro (mostrar preview em hover)
- **Risco: 5** - Zero risco de quebrar algo (apenas adiciona tooltip)
- **Total: (5×2) + 5 + (3×1.5) + 5 + 5 = 33.5 pontos** 🟢

**Template para Preenchimento**:
```markdown
## Matriz de Decisão - Sprint vX.X.X

| Task ID | Simplicidade | Dependências | Impacto | Clareza | Risco | **Score** | Ordem |
|---------|-------------|--------------|---------|---------|-------|-----------|-------|
| #XX     | ?           | ?            | ?       | ?       | ?     | **?**     | ?     |
| #YY     | ?           | ?            | ?       | ?       | ?     | **?**     | ?     |

**Justificativa da Escolha**:
Task #XX escolhida porque:
- Score mais alto (XX pontos)
- [razão específica]
- [razão específica]
```

**Quando Não Usar a Matriz**:
- ❌ Apenas 1 task disponível (não há escolha)
- ❌ Task urgente/bloqueante (ignora pontuação)
- ❌ Bugfix crítico de produção (prioridade absoluta)

**Por quê usar**:
- ✅ **Objetividade**: Elimina viés pessoal
- ✅ **Rastreabilidade**: Justifica decisões
- ✅ **Aprendizado**: Melhora estimativas futuras
- ✅ **Comunicação**: Fácil explicar escolha para equipe

---

### 3️⃣ **Fazer Perguntas e Mais Perguntas ao Programador**
- **CRÍTICO**: Nunca assumir ou adivinhar requisitos
- Fazer **todas as perguntas necessárias** até sanar **100% das dúvidas**
- Validar entendimento antes de começar a implementar
- 🤖 **[NOVO v2.1]** A IA **PODE e É ALTAMENTE RECOMENDADA** fornecer **sugestões e palpites** de resposta para cada pergunta (opcional, mas incentivado)

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

### 6️⃣.5️⃣ **Checklist de Segurança (OWASP Top 10)** ⭐ NOVO - ALTA PRIORIDADE

**Quando Aplicar**: Durante Etapa 6 (Implementação) se a feature envolve:
- ✅ Input de usuário (forms, CLI arguments, file uploads)
- ✅ Acesso a arquivos/sistema operacional
- ✅ Conexões de rede (APIs, databases, external services)
- ✅ Autenticação/autorização
- ✅ Dados sensíveis (senhas, tokens, PII)

**OWASP Top 10 Aplicado**:

**1. 🛡️ Injection (SQL, Command, Path Traversal)**
```python
# ❌ INSEGURO - SQL Injection
query = f"SELECT * FROM users WHERE id = {user_id}"  # NUNCA FAZER!

# ✅ SEGURO - Parameterized Query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# ❌ INSEGURO - Command Injection
os.system(f"convert {filename} output.png")  # NUNCA FAZER!

# ✅ SEGURO - Lista de argumentos
subprocess.run(["convert", filename, "output.png"], check=True)

# ❌ INSEGURO - Path Traversal
with open(user_path, 'r') as f:  # ../../../etc/passwd
    data = f.read()

# ✅ SEGURO - Validar e restringir path
from pathlib import Path
safe_path = Path(user_path).resolve()
if not safe_path.is_relative_to(ALLOWED_DIR):
    raise SecurityError("Path traversal detected!")
data = safe_path.read_text()
```

**2. 🔐 Broken Authentication**
```python
# ❌ INSEGURO - Senha em texto plano
password = "admin123"  # NUNCA FAZER!

# ✅ SEGURO - Hash com salt
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# ❌ INSEGURO - Session sem timeout
session['user_id'] = user_id  # Nunca expira

# ✅ SEGURO - Session com timeout
session['user_id'] = user_id
session.permanent = True
app.permanent_session_lifetime = timedelta(hours=1)
```

**3. 🔓 Sensitive Data Exposure**
```python
# ❌ INSEGURO - API key no código
API_KEY = "sk-1234567890abcdef"  # NUNCA FAZER!

# ✅ SEGURO - Variáveis de ambiente
import os
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY not set!")

# ❌ INSEGURO - Log de dados sensíveis
logger.info(f"User logged in: {email}, password: {password}")

# ✅ SEGURO - Log sem dados sensíveis
logger.info(f"User logged in: {email}")
```

**4. 🌐 XML External Entities (XXE)**
```python
# ❌ INSEGURO - XML parsing sem proteção
import xml.etree.ElementTree as ET
tree = ET.parse(user_file)  # Vulnerável a XXE

# ✅ SEGURO - Desabilitar entidades externas
import defusedxml.ElementTree as ET
tree = ET.parse(user_file)
```

**5. 🚪 Broken Access Control**
```python
# ❌ INSEGURO - Sem verificação de permissão
def delete_file(file_id):
    file = File.query.get(file_id)
    file.delete()  # Qualquer usuário pode deletar qualquer arquivo!

# ✅ SEGURO - Verificar ownership
def delete_file(file_id, current_user):
    file = File.query.get(file_id)
    if file.owner_id != current_user.id:
        raise PermissionError("You don't own this file!")
    file.delete()
```

**6. ⚙️ Security Misconfiguration**
```python
# ❌ INSEGURO - Debug mode em produção
app = Flask(__name__)
app.debug = True  # NUNCA em produção!

# ✅ SEGURO - Debug apenas em desenvolvimento
app.debug = os.getenv('FLASK_ENV') == 'development'

# ❌ INSEGURO - Permissões muito abertas
os.chmod(secret_file, 0o777)  # Todos podem ler/escrever

# ✅ SEGURO - Permissões restritivas
os.chmod(secret_file, 0o600)  # Apenas owner pode ler/escrever
```

**7. 🎨 Cross-Site Scripting (XSS)**
```python
# ❌ INSEGURO - HTML sem escape
html = f"<div>Hello {user_name}</div>"  # XSS se user_name = "<script>..."

# ✅ SEGURO - Escape de HTML
from html import escape
html = f"<div>Hello {escape(user_name)}</div>"

# ✅ MELHOR - Template engine com auto-escape
return render_template('hello.html', name=user_name)  # Jinja2 escapa automaticamente
```

**8. 🔄 Insecure Deserialization**
```python
# ❌ INSEGURO - pickle de fonte não confiável
import pickle
data = pickle.loads(user_data)  # Code execution!

# ✅ SEGURO - DATA (não executa código)
import data
data = data.loads(user_data)
```

**9. 📦 Using Components with Known Vulnerabilities**
```bash
# ❌ INSEGURO - Dependências desatualizadas
# requirements.txt
flask==0.12.0  # Versão antiga com vulnerabilidades

# ✅ SEGURO - Dependências atualizadas
pip install --upgrade flask
pip-audit  # Verifica vulnerabilidades

# Automático - GitHub Dependabot
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

**10. 📋 Insufficient Logging & Monitoring**
```python
# ❌ INSEGURO - Sem logs de segurança
def login(username, password):
    user = authenticate(username, password)
    return user  # Falha silenciosa

# ✅ SEGURO - Log de eventos de segurança
def login(username, password):
    try:
        user = authenticate(username, password)
        logger.info(f"Login success: {username} from {request.remote_addr}")
        return user
    except AuthenticationError:
        logger.warning(f"Login failed: {username} from {request.remote_addr}")
        raise
```

**Checklist de Segurança**:
```markdown
### Checklist de Segurança - [Nome da Feature]

#### Injection
- [ ] Todos os inputs são sanitizados/validados?
- [ ] Queries usam parametrização?
- [ ] Comandos do sistema usam lista de args (não string)?
- [ ] Paths são validados contra path traversal?

#### Authentication & Sessions
- [ ] Senhas são hash + salt (bcrypt/argon2)?
- [ ] Sessions têm timeout?
- [ ] Tokens são gerados com crypto.secrets (não random)?
- [ ] Login failures são logados?

#### Sensitive Data
- [ ] API keys/secrets em variáveis de ambiente?
- [ ] Dados sensíveis NÃO são logados?
- [ ] Conexões usam HTTPS/TLS?
- [ ] Dados em repouso são criptografados (se necessário)?

#### Access Control
- [ ] Permissões verificadas antes de cada operação?
- [ ] Usuário só acessa seus próprios recursos?
- [ ] Princípio de menor privilégio aplicado?

#### Configuration
- [ ] Debug mode DESABILITADO em produção?
- [ ] Error messages NÃO expõem stack traces para usuário?
- [ ] Permissões de arquivo corretas (0o600 para secrets)?

#### Dependencies
- [ ] Todas dependências atualizadas?
- [ ] pip-audit executado sem vulnerabilidades?
- [ ] Dependabot configurado (se GitHub)?
```

**Ferramentas de Segurança**:
```bash
# Análise estática de segurança
pip install bandit
bandit -r src/ -f data -o security-report.data

# Verificar vulnerabilidades em dependências
pip install pip-audit
pip-audit

# Scan de secrets no código
pip install detect-secrets
detect-secrets scan > .secrets.baseline

# Pre-commit hook para segurança
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: bandit
        name: Security check (bandit)
        entry: bandit -r src/
        language: system
      
      - id: secrets
        name: Detect secrets
        entry: detect-secrets-hook
        language: system
```

**Por quê esta etapa é crítica**:
- ✅ **LGPD/GDPR Compliance**: Evita multas e processos
- ✅ **Reputação**: Vazamento de dados destrói confiança
- ✅ **Custo**: Bug de segurança é 100x mais caro de corrigir em produção
- ✅ **Legal**: Responsabilidade civil e criminal

---

### 6️⃣.6️⃣ **Gerar Documentação de API** (Opcional - Se criar biblioteca/módulo reutilizável)

**Quando Aplicar**:
- ✅ Módulo será usado por outros desenvolvedores
- ✅ Biblioteca pública/open-source
- ✅ API REST/GraphQL
- ✅ SDK ou plugin
- ✅ Funções complexas que precisam de exemplos

**Não Aplicar Se**:
- ❌ Código interno descartável
- ❌ Scripts one-off
- ❌ Protótipo rápido

**Ferramentas Recomendadas**:

**1. Sphinx** (Documentação profissional completa)
```bash
# Instalar
pip install sphinx sphinx-rtd-theme

# Inicializar
cd docs/
sphinx-quickstart

# Gerar automaticamente de docstrings
sphinx-apidoc -o source/ ../src/

# Compilar
make html

# Resultado: docs/build/html/index.html
```

**Configuração** (`docs/source/conf.py`):
```python
extensions = [
    'sphinx.ext.autodoc',       # Docstrings automáticos
    'sphinx.ext.napoleon',      # Google/NumPy style docstrings
    'sphinx.ext.viewcode',      # Link para código-fonte
    'sphinx.ext.intersphinx',   # Links para outras docs
]

html_theme = 'sphinx_rtd_theme'  # Read the Docs theme
```

**2. pdoc** (Documentação simples e rápida)
```bash
# Instalar
pip install pdoc

# Gerar (serve com hot-reload)
pdoc --http : src/

# Gerar HTML estático
pdoc --html --output-dir docs/ src/

# Resultado: docs/src/index.html
```

**3. MkDocs** (Documentação em Markdown)
```bash
# Instalar
pip install mkdocs mkdocs-material

# Inicializar
mkdocs new .

# Servir com hot-reload
mkdocs serve

# Build para produção
mkdocs build

# Deploy para GitHub Pages
mkdocs gh-deploy
```

**Exemplo de Docstring Completo**:
```python
def build_substitution_map_by_value(
    old_keys: Dict[str, str],
    new_keys: Dict[str, str]
) -> Dict[str, str]:
    """
    Build substitution map matching keys by their VALUES (not names).
    
    This function compares translation values between old and new DATA files
    to detect feature that need updating. It ignores key names and
    focuses solely on value equality.
    
    Args:
        old_keys: Dictionary mapping old key paths to their values.
            Example: {"t.welcome": "Welcome", "t.hello": "Hello"}
        new_keys: Dictionary mapping new key paths to their values.
            Example: {"t.greeting": "Welcome", "t.hi": "Hi"}
    
    Returns:
        Dictionary mapping old key paths to new key paths where values match.
        Example: {"t.welcome": "t.greeting"}  # Both have value "Welcome"
    
    Raises:
        ValueError: If old_keys or new_keys are empty.
        TypeError: If inputs are not dictionaries.
    
    Examples:
        >>> old = {"t.btn1": "Save", "t.btn2": "Cancel"}
        >>> new = {"t.save_btn": "Save", "t.cancel_btn": "Cancel"}
        >>> build_substitution_map_by_value(old, new)
        {'t.btn1': 't.save_btn', 't.btn2': 't.cancel_btn'}
        
        >>> old = {"t.msg": "Hello"}
        >>> new = {"t.greeting": "Hi"}  # Different value
        >>> build_substitution_map_by_value(old, new)
        {}  # No matches
    
    Notes:
        - Comparison is case-sensitive and exact
        - First match wins if multiple new keys have same value
        - Parent keys are not matched (only leaf values)
    
    See Also:
        - extract_all_keys_from_obj: Extract keys from DATA/Obj
        - apply_substitutions_to_file: Apply map to TSX files
    
    References:
        - Task Example: Feature Update System
        - FEATURE_SPEC.md
    
    Version:
        Added in vX.Y.Z
    """
    # Implementation...
```

**Checklist de Documentação de API**:
```markdown
### Documentação de API - [Nome do Módulo]

#### Cobertura
- [ ] Todas funções públicas têm docstrings?
- [ ] Todos parâmetros documentados?
- [ ] Todos returns documentados?
- [ ] Exceções possíveis listadas?

#### Qualidade
- [ ] Exemplos de uso incluídos?
- [ ] Edge cases documentados?
- [ ] Type hints presentes (PEP 484)?
- [ ] Docstrings seguem padrão (Google/NumPy)?

#### Acessibilidade
- [ ] API docs publicadas (Read the Docs, GitHub Pages)?
- [ ] Tutorial/Getting Started incluído?
- [ ] Changelog mantido?
- [ ] Link para docs no README?
```

**Por quê**:
- ✅ **Adoção**: Docs boas = mais usuários
- ✅ **Suporte**: Menos perguntas repetidas
- ✅ **Onboarding**: Novos devs entendem mais rápido
- ✅ **Profissionalismo**: Mostra qualidade do projeto

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

### 8️⃣.5️⃣ **Checklist de Acessibilidade (WCAG 2.1)** (Opcional - Para GUIs)

**Quando Aplicar**:
- ✅ Aplicações desktop com GUI
- ✅ Aplicações web
- ✅ Ferramentas usadas por equipes diversas
- ✅ Projetos open-source
- ✅ Compliance com leis de acessibilidade

**Não Aplicar Se**:
- ❌ CLI/backend apenas
- ❌ Script interno de uso pessoal
- ❌ Protótipo não-public

**WCAG 2.1 Level AA - Princípios POUR**:

**1. Perceptível - Usuários devem perceber a informação**

```python
# ✅ ACESSÍVEL - Labels descritivos
self.btn_save = QPushButton("Save File")
self.btn_save.setToolTip("Save current file to disk (Ctrl+S)")
self.btn_save.setAccessibleName("Save file button")
self.btn_save.setAccessibleDescription("Saves the current file to disk")

# ❌ NÃO ACESSÍVEL - Sem contexto
self.btn = QPushButton("OK")  # OK para quê?
self.btn.setToolTip("OK")     # Não ajuda
```

**2. Operável - Usuários devem operar a interface**

```python
# ✅ ACESSÍVEL - Navegação por teclado
self.ed_input.setFocusPolicy(Qt.StrongFocus)
self.btn_save.setShortcut(QKeySequence("Ctrl+S"))
self.btn_cancel.setShortcut(QKeySequence("Esc"))

# Indicador visual de foco
self.ed_input.setStyleSheet("""
    QLineEdit:focus {
        border: 2px solid #0078d4;
        background-color: #f0f8ff;
    }
""")

# ❌ NÃO ACESSÍVEL - Apenas mouse
self.btn.clicked.connect(self.on_click)  # Sem atalho de teclado
```

**3. Compreensível - Informação e operação devem ser compreensíveis**

```python
# ✅ ACESSÍVEL - Mensagens de erro claras
QMessageBox.critical(
    self,
    "File Not Found",
    f"The file '{filename}' could not be found.\n\n"
    f"Please check:\n"
    f"• The file path is correct\n"
    f"• You have read permissions\n"
    f"• The file was not deleted"
)

# ❌ NÃO ACESSÍVEL - Erro genérico
QMessageBox.critical(self, "Error", "Operation failed")
```

**4. Robusto - Conteúdo deve ser robusto para assistive technologies**

```python
# ✅ ACESSÍVEL - Roles e relationships
self.lbl_name = QLabel("Name:")
self.ed_name = QLineEdit()
self.lbl_name.setBuddy(self.ed_name)  # Associa label com input

# Group relacionados
self.group_personal = QGroupBox("Personal Information")
self.group_personal.setAccessibleName("Personal information group")

# ❌ NÃO ACESSÍVEL - Sem structure
# Apenas widgets soltos sem relação semântica
```

**Checklist de Acessibilidade WCAG 2.1**:

```markdown
### Checklist de Acessibilidade - [Nome da GUI]

#### 1. Perceptível
- [ ] **Contraste**: Cores têm contraste mínimo 4.5:1 (texto normal)?
- [ ] **Contraste**: Cores têm contraste mínimo 3:1 (texto grande >18pt)?
- [ ] **Alternativas**: Ícones têm tooltips descritivos?
- [ ] **Labels**: Todos inputs têm labels associados?
- [ ] **Cores**: Informação não depende apenas de cor?
- [ ] **Tamanho**: Texto é redimensionável (até 200%)?

#### 2. Operável
- [ ] **Teclado**: Todas funções acessíveis via teclado?
- [ ] **Tab Order**: Ordem de navegação faz sentido?
- [ ] **Focus**: Elemento focado tem indicação visual clara?
- [ ] **Atalhos**: Comandos importantes têm atalhos de teclado?
- [ ] **Esc**: Diálogos podem ser fechados com Esc?
- [ ] **Enter**: Enter submete forms/confirma ações?
- [ ] **Tempo**: Não há timeouts inesperados?

#### 3. Compreensível
- [ ] **Idioma**: Idioma do conteúdo está definido (i18n)?
- [ ] **Labels**: Labels de inputs são claros?
- [ ] **Instruções**: Inputs complexos têm instruções?
- [ ] **Erros**: Mensagens de erro são específicas e acionáveis?
- [ ] **Ajuda**: Help/documentation facilmente acessível?
- [ ] **Navegação**: Menus têm estrutura lógica?

#### 4. Robusto
- [ ] **Screen Reader**: Testado com screen reader (NVDA/Orca)?
- [ ] **Semântica**: Widgets corretos (QPushButton vs QLabel)?
- [ ] **Roles**: AccessibleName e AccessibleDescription definidos?
- [ ] **Relationships**: Labels associados com buddy()?
- [ ] **Groups**: Controles relacionados agrupados (QGroupBox)?
```

**Teste Prático com Screen Reader**:

```bash
# Linux - Instalar Orca
sudo apt install orca

# Iniciar screen reader
orca --replace &

# Testar aplicação:
# 1. Navegar com Tab (deve ler cada elemento)
# 2. Pressionar Enter/Space (deve ativar botões)
# 3. Preencher forms (deve ler labels corretamente)
# 4. Acionar atalhos (Ctrl+S, Esc, etc)

# Windows - Usar NVDA (gratuito)
# https://www.nvaccess.org/download/

# macOS - VoiceOver (nativo)
# Cmd+F5 para ativar
```

**Ferramentas de Validação**:

```bash
# Verificar contraste de cores
pip install color-contrast-checker
color-contrast-checker --foreground "#333333" --background "#ffffff"
# Resultado: AAA (passa todos os níveis)

# Analisador de acessibilidade web (se aplicável)
npm install -g pa11y
pa11y http://localhost:8000

# Lighthouse (Chrome DevTools)
# Audits → Accessibility → Generate Report
```

**Exemplo de GUI Acessível**:

```python
class AccessibleConverterDock(QDockWidget):
    """Accessible text to DATA converter with WCAG 2.1 Level AA compliance."""
    
    def __init__(self, parent=None):
        super().__init__("Text to DATA Converter", parent)
        self.setAccessibleName("Text to DATA Converter Dock")
        self.setAccessibleDescription(
            "Convert structured text files to DATA format with preview"
        )
        self._create_accessible_widgets()
        self._setup_shortcuts()
    
    def _create_accessible_widgets(self):
        # Label + Input com buddy
        self.lbl_input = QLabel("&Input File:")
        self.ed_input = QLineEdit()
        self.ed_input.setAccessibleName("Input file path")
        self.ed_input.setAccessibleDescription("Enter path to text file to convert")
        self.ed_input.setPlaceholderText("e.g., data.csv or config.ini")
        self.lbl_input.setBuddy(self.ed_input)  # Alt+I foca no input
        
        # Botão com tooltip e shortcut
        self.btn_convert = QPushButton("&Convert to DATA")
        self.btn_convert.setAccessibleName("Convert button")
        self.btn_convert.setAccessibleDescription(
            "Convert input file to DATA format. Shortcut: Ctrl+Enter"
        )
        self.btn_convert.setToolTip("Convert text to DATA (Ctrl+Enter)")
        self.btn_convert.setShortcut(QKeySequence("Ctrl+Return"))
        
        # Indicador de foco
        self.btn_convert.setStyleSheet("""
            QPushButton:focus {
                border: 2px solid #0078d4;
                outline: 2px solid #0078d4;
                outline-offset: 2px;
            }
        """)
        
        # Group para organização semântica
        self.group_options = QGroupBox("Conversion &Options")
        self.group_options.setAccessibleName("Conversion options group")
        
        self.chk_pretty = QCheckBox("&Pretty print DATA")
        self.chk_pretty.setAccessibleName("Pretty print option")
        self.chk_pretty.setAccessibleDescription(
            "Format DATA with indentation for readability"
        )
        self.chk_pretty.setToolTip("Format DATA with indentation")
        
        # Alto contraste para status
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setAccessibleName("Conversion status")
        self.lbl_status.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
    
    def _setup_shortcuts(self):
        """Configure keyboard shortcuts for accessibility."""
        # Esc fecha o dock
        self.shortcut_close = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_close.activated.connect(self.close)
        
        # F1 abre ajuda
        self.shortcut_help = QShortcut(QKeySequence("F1"), self)
        self.shortcut_help.activated.connect(self._show_help)
    
    def _show_help(self):
        """Show accessible help dialog."""
        QMessageBox.information(
            self,
            "Text to DATA Converter - Help",
            "<h3>Keyboard Shortcuts</h3>"
            "<ul>"
            "<li><b>Ctrl+Enter</b>: Convert file</li>"
            "<li><b>Alt+I</b>: Focus input field</li>"
            "<li><b>Alt+O</b>: Toggle options group</li>"
            "<li><b>Esc</b>: Close dock</li>"
            "<li><b>F1</b>: Show this help</li>"
            "</ul>"
            "<h3>Screen Reader Support</h3>"
            "<p>This interface is fully accessible with screen readers.</p>"
        )
```

**Por quê esta etapa é importante**:
- ✅ **Inclusão**: ~15% da população tem alguma deficiência
- ✅ **Legal**: ADA, Section 508, EN 301 549 podem exigir
- ✅ **UX**: Boa acessibilidade = boa UX para todos
- ✅ **SEO**: Acessibilidade melhora rankings (se web)
- ✅ **Reputação**: Mostra responsabilidade social

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

### 9️⃣.5️⃣ **Code Review por Pares** (Opcional - Para Equipes)

**Quando Aplicar**:
- ✅ Projetos em equipe (2+ desenvolvedores)
- ✅ Alterações críticas (segurança, dados)
- ✅ Features complexas (>200 linhas)
- ✅ Código que outros manterão
- ✅ Open-source com contribuidores

**Não Aplicar Se**:
- ❌ Projeto solo/pessoal
- ❌ Hotfix emergencial crítico
- ❌ Mudanças triviais (typos em docs)
- ❌ Protótipo descartável

**Processo de Pull Request**:

```bash
# 1. Criar branch da feature
git checkout -b feature/task-42-add-export

# 2. Implementar e commitar
git add clarify_patched.py
git commit -m "Add CSV export feature (Task Example)"

# 3. Push e criar PR
git push origin feature/task-42-add-export
# Abrir PR no GitHub/GitLab com template

# 4. Aguardar review de pelo menos 1 colega
# 5. Implementar mudanças solicitadas
# 6. Merge após aprovação
```

**Template de Pull Request**:

```markdown
## Descrição
Implementa exportação CSV para Task Example do Protocolo Simplicidade.

## Tipo de Mudança
- [x] Nova feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Documentação

## Checklist Protocolo Simplicidade
- [x] Etapa 1: Task definida e selecionada (Task Example)
- [x] Etapa 2: Dividida em subtasks
- [x] Etapa 6: Código implementado
- [x] Etapa 7: Code review manual (auto-review)
- [x] Etapa 8: GUI testada manualmente
- [x] Etapa 9: Integração verificada
- [x] Etapa 10: Testes unitários (pytest)
- [x] Etapa 11: Código organizado (PEP 8)

## Como Testar
```bash
pytest tests/test_csv_export.py -v
python clarify_patched.py --export tasks.csv
```

## Screenshots (se aplicável)
![CSV Export Dialog](screenshots/csv-export.png)

## Relacionado
- Closes #42
- Related to #38 (Data Export Epic)
```

**Checklist do Reviewer**:

```markdown
### Code Review Checklist - [Nome do PR]

#### 1. Funcionalidade
- [ ] **Feature**: Implementação resolve o problema descrito?
- [ ] **Edge Cases**: Casos extremos tratados (input vazio, None, etc)?
- [ ] **Errors**: Erros possuem mensagens claras?
- [ ] **UX**: Interface é intuitiva e consistente?

#### 2. Código
- [ ] **Legibilidade**: Código é claro e autodocumentado?
- [ ] **Simplicidade**: Solução é a mais simples possível?
- [ ] **Duplicação**: Não há código duplicado?
- [ ] **Nomes**: Variáveis/funções têm nomes descritivos?
- [ ] **Comentários**: Comentários explicam "por quê", não "o quê"?

#### 3. Arquitetura
- [ ] **Separation**: Lógica separada de apresentação?
- [ ] **Dependencies**: Dependências novas são justificadas?
- [ ] **Patterns**: Segue padrões do projeto?
- [ ] **SOLID**: Princípios SOLID respeitados?

#### 4. Testes
- [ ] **Cobertura**: Código novo tem testes unitários?
- [ ] **Casos**: Testes cobrem cenários críticos?
- [ ] **Passam**: Todos testes passam no CI?
- [ ] **Legibilidade**: Testes são claros e mantíveis?

#### 5. Segurança
- [ ] **Input**: Validação de entrada existe?
- [ ] **SQL**: Sem SQL injection (usar parametrizado)?
- [ ] **Secrets**: Sem credenciais no código?
- [ ] **Permissions**: Verificações de permissão adequadas?

#### 6. Performance
- [ ] **Loops**: Loops são eficientes (sem O(n²) desnecessário)?
- [ ] **Queries**: Queries DB são otimizadas (indexes)?
- [ ] **Memory**: Sem memory leaks (fechar recursos)?
- [ ] **Caching**: Caching aplicado onde faz sentido?

#### 7. Documentação
- [ ] **Docstrings**: Funções públicas têm docstrings?
- [ ] **README**: README atualizado se necessário?
- [ ] **CHANGELOG**: Entrada no changelog criada?
- [ ] **Comments**: Decisões complexas documentadas?
```

**Exemplo de Review Comment**:

```markdown
**❌ Problema - Falta validação de input**

```python
# Linha 142
def export_to_csv(self, filename):
    with open(filename, 'w') as f:
        # ...
```

**Sugestão**:
```python
def export_to_csv(self, filename):
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    if not filename.endswith('.csv'):
        raise ValueError("Filename must end with .csv")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # ...
    except IOError as e:
        raise IOError(f"Failed to write CSV: {e}")
```

**Rationale**: Sem validação, o código pode falhar silenciosamente ou gerar arquivos inválidos.
```

**Ferramentas para Code Review**:

```bash
# GitHub CLI - Criar PR via terminal
gh pr create --title "Add CSV export" --body "Implements Task Example"

# Revisar PR localmente
gh pr checkout 123
pytest
python clarify_patched.py --test

# Aprovar PR
gh pr review 123 --approve --body "LGTM! Código limpo e testado."

# Solicitar mudanças
gh pr review 123 --request-changes --body "Favor adicionar validação de input (ver comentários)"
```

**GitLab - Merge Request Template**:

```yaml
# .gitlab/merge_request_templates/feature.md
## Descrição da Feature
<!-- Descreva o que foi implementado -->

## Checklist Protocolo Simplicidade
- [ ] Task definida (Etapa 1)
- [ ] Código implementado (Etapa 6)
- [ ] Testes passando (Etapa 10)
- [ ] Documentação atualizada (Etapa 12)

## Como Testar
<!-- Comandos para testar a feature -->

## Screenshots
<!-- Se aplicável -->

/label ~feature
/assign @reviewer-name
```

**Cultura de Code Review**:

```markdown
### Princípios para Reviews Construtivos

1. **Seja Gentil**: "Consider adding validation" > "This is wrong"
2. **Explique o Por Quê**: Não apenas "Change this", mas "Change this because..."
3. **Pergunte**: "What do you think about...?" > "You should..."
4. **Aprove Rápido**: Se está bom o suficiente, aprove (não busque perfeição)
5. **Aprenda**: Veja reviews como oportunidade de aprender
6. **Automatize**: Use linters para estilo, foque em lógica

### Anti-Patterns a Evitar
- ❌ Nitpicking excessivo (espaços, vírgulas)
- ❌ Reescrever tudo do seu jeito
- ❌ Deixar PR parado por dias
- ❌ Aprovar sem ler (rubber stamping)
- ❌ Comentários vagos ("This is bad")
```

**Métricas de Code Review**:

```python
# Exemplo: tracking review metrics
review_metrics = {
    "pr_number": 123,
    "author": "alice",
    "reviewer": "bob",
    "lines_changed": 250,
    "files_changed": 3,
    "comments": 8,
    "time_to_first_review_hours": 4,
    "time_to_merge_hours": 18,
    "result": "approved"
}

# Métricas saudáveis:
# - Time to first review: < 8h
# - Time to merge: < 48h
# - Comments por PR: 3-10 (nem muito, nem pouco)
# - Approval rate: > 80% (se < 50%, reviews muito rígidos)
```

**Por quê Code Review é valioso**:
- ✅ **Qualidade**: Detecta bugs antes de produção (15-20% em média)
- ✅ **Conhecimento**: Distribui conhecimento do código na equipe
- ✅ **Mentoria**: Desenvolvedores júniors aprendem com seniors
- ✅ **Consistência**: Mantém padrões do projeto uniformes
- ✅ **Documentação**: Discussões no PR = contexto histórico

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

### 🔟.5️⃣ **Profiling e Otimização** (Opcional - Para Features Críticas)

**Quando Aplicar**:
- ✅ Features de performance crítica (loops, processamento de dados)
- ✅ Operações que processam arquivos grandes (>10MB)
- ✅ Código que roda frequentemente (hot paths)
- ✅ Aplicações com requisitos de latência (<100ms)
- ✅ Quando usuários reportam lentidão

**Não Aplicar Se**:
- ❌ Feature roda raramente (setup inicial)
- ❌ Performance já é boa o suficiente (<1s para user)
- ❌ Código de configuração/inicialização
- ❌ Protótipos ou POCs

**Profiling com cProfile**:

```bash
# Profiling de CPU - descobrir funções lentas
python -m cProfile -s cumulative clarify_patched.py > profile.txt

# Profiling com visualização
pip install snakeviz
python -m cProfile -o profile.stats clarify_patched.py
snakeviz profile.stats  # Abre browser com flamegraph
```

**Exemplo de Análise**:

```python
# ❌ LENTO - O(n²) para processar tasks
def find_duplicates_slow(tasks):
    """Encontra tasks duplicadas - VERSÃO LENTA."""
    duplicates = []
    for i, task1 in enumerate(tasks):
        for j, task2 in enumerate(tasks):
            if i != j and task1.title == task2.title:
                duplicates.append((task1, task2))
    return duplicates

# Profiling revela: 85% do tempo em find_duplicates_slow()
# Para 1000 tasks: 5.2 segundos

# ✅ RÁPIDO - O(n) usando set
def find_duplicates_fast(tasks):
    """Encontra tasks duplicadas - VERSÃO OTIMIZADA."""
    seen = {}
    duplicates = []
    for task in tasks:
        if task.title in seen:
            duplicates.append((seen[task.title], task))
        else:
            seen[task.title] = task
    return duplicates

# Após otimização: 0.02 segundos (260x mais rápido)
```

**Memory Profiling**:

```bash
# Instalar memory_profiler
pip install memory_profiler

# Decorar função para profilear
```

```python
from memory_profiler import profile

@profile
def load_large_file(filepath):
    """Load and process large DATA file."""
    with open(filepath, 'r') as f:
        data = data.load(f)  # Carrega tudo na memória
    
    # Processar...
    results = []
    for item in data:
        results.append(process_item(item))
    
    return results

# Executar com profiling
# python -m memory_profiler clarify_patched.py
```

**Exemplo de Otimização de Memória**:

```python
# ❌ MEMORY LEAK - Carrega arquivo inteiro (500MB)
def process_large_csv_bad(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()  # 500MB em memória!
    
    results = []
    for line in lines:
        results.append(process_line(line))
    return results

# Memory profiler mostra: Pico de 520MB

# ✅ OTIMIZADO - Streaming (constante 5MB)
def process_large_csv_good(filepath):
    results = []
    with open(filepath, 'r') as f:
        for line in f:  # Lê linha por linha
            results.append(process_line(line))
    return results

# Memory profiler mostra: Pico de 8MB (65x menos)
```

**Line-by-Line Profiling**:

```python
# Instalar line_profiler
# pip install line_profiler

# Decorar função suspeita
@profile  # Requer kernprof
def complex_calculation(data):
    """Function to profile line-by-line."""
    # Linha 1: setup
    total = 0
    
    # Linha 2: loop principal
    for item in data:
        # Linha 3: cálculo pesado
        result = expensive_operation(item)
        total += result
    
    return total

# Executar
# kernprof -l -v clarify_patched.py
# Mostra tempo por linha de código
```

**Benchmarking Antes/Depois**:

```python
import time

def benchmark(func, *args, iterations=100):
    """Benchmark function performance."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)
    
    avg = sum(times) / len(times)
    return {
        "avg_ms": avg * 1000,
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000
    }

# Antes da otimização
before = benchmark(find_duplicates_slow, large_task_list)
print(f"ANTES: {before['avg_ms']:.2f}ms")

# Depois da otimização
after = benchmark(find_duplicates_fast, large_task_list)
print(f"DEPOIS: {after['avg_ms']:.2f}ms")
print(f"SPEEDUP: {before['avg_ms'] / after['avg_ms']:.1f}x")

# Output:
# ANTES: 5240.32ms
# DEPOIS: 20.15ms
# SPEEDUP: 260.0x
```

**Checklist de Otimização**:

```markdown
### Performance Checklist - [Nome da Feature]

#### Profiling Realizado
- [ ] **CPU**: cProfile executado e analisado
- [ ] **Memory**: memory_profiler executado (se > 100MB)
- [ ] **Hotspots**: Identificadas top 3 funções mais lentas
- [ ] **Baseline**: Tempo/memória antes da otimização documentado

#### Otimizações Aplicadas
- [ ] **Algoritmo**: Complexidade reduzida (O(n²) → O(n log n) ou O(n))
- [ ] **Estruturas**: Estruturas de dados adequadas (dict vs list)
- [ ] **I/O**: I/O otimizado (buffering, streaming)
- [ ] **Cache**: Caching aplicado para operações repetidas
- [ ] **Lazy**: Lazy loading para dados grandes

#### Validação
- [ ] **Benchmark**: Before/after documentado com speedup
- [ ] **Testes**: Todos testes ainda passam
- [ ] **Correção**: Saída idêntica à versão anterior
- [ ] **Limites**: Testado com volume realista (10x dados típicos)

#### Documentação
- [ ] **Comentários**: Otimizações não-óbvias documentadas
- [ ] **Big-O**: Complexidade documentada em docstring
- [ ] **Trade-offs**: Trade-offs explicados (memória vs velocidade)
```

**Ferramentas Avançadas**:

```bash
# py-spy - Sampling profiler (sem modificar código)
pip install py-spy
py-spy record -o profile.svg -- python clarify_patched.py
# Gera flamegraph interativo

# Scalene - CPU + Memory + GPU profiler
pip install scalene
scalene clarify_patched.py
# Dashboard interativo no terminal

# pytest-benchmark para testes
pip install pytest-benchmark

# Exemplo de teste de benchmark
def test_find_duplicates_performance(benchmark):
    tasks = generate_large_task_list(1000)
    result = benchmark(find_duplicates_fast, tasks)
    assert len(result) > 0
    # benchmark automaticamente mede tempo
```

**Quando Parar de Otimizar**:

```python
# Regra de Pareto: 80% dos ganhos vêm de 20% do esforço

# ✅ VALE A PENA otimizar:
# - Redução de 5s → 0.5s (10x) = 4.5s salvos por execução
# - Se executado 100x/dia = 450s (7.5min) salvos/dia

# ❌ NÃO VALE otimizar:
# - Redução de 0.05s → 0.02s (2.5x) = 0.03s salvos
# - Se executado 10x/dia = 0.3s salvos/dia (insignificante)

# Critério: Otimizar se tempo salvo × frequência > 1 minuto/dia
```

**Por quê Profiling é importante**:
- ✅ **Evidência**: Otimizar baseado em dados, não em "achismo"
- ✅ **Foco**: Identificar gargalos reais (não onde achamos que está)
- ✅ **ROI**: Priorizar otimizações com maior impacto
- ✅ **Evitar**: Micro-otimizações prematuras que complicam código
- ✅ **Escalabilidade**: Garantir que código escala com dados maiores

---

### 🔟.6️⃣ **CI/CD Quality Gates** ⭐ (Opcional - ALTA PRIORIDADE)

**Quando Aplicar**:
- ✅ Projetos em equipe (2+ pessoas)
- ✅ Código em produção ou crítico
- ✅ Open-source com contribuidores
- ✅ Quando precisa garantir qualidade consistente
- ✅ Ambientes com múltiplos branches

**Não Aplicar Se**:
- ❌ Projeto solo/experimental
- ❌ Protótipo descartável
- ❌ Scripts de uso único
- ❌ Sem infraestrutura CI (GitHub/GitLab/Jenkins)

**Pre-commit Hooks - Validação Local**:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-data
      - id: check-added-large-files
        args: ['--maxkb=500']
  
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88', '--extend-ignore=E203']
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ['-ll', '-i']  # Low severity, ignore issues
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        args: ['tests/', '-v', '--tb=short']
```

```bash
# Instalar pre-commit
pip install pre-commit

# Ativar hooks
pre-commit install

# Agora todo git commit executa validações automaticamente
# Se falhar, commit é bloqueado até corrigir
```

**GitHub Actions - CI Pipeline**:

```yaml
# .github/workflows/ci.yml
name: CI Quality Gates

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality-checks:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black bandit mypy
    
    - name: Code Formatting (Black)
      run: |
        black --check clarify_patched.py
      continue-on-error: false
    
    - name: Linting (Flake8)
      run: |
        flake8 clarify_patched.py --max-line-length=88 --statistics
      continue-on-error: false
    
    - name: Type Checking (MyPy)
      run: |
        mypy clarify_patched.py --ignore-missing-imports
      continue-on-error: true  # Warnings, não erros
    
    - name: Security Scan (Bandit)
      run: |
        bandit -r clarify_patched.py -ll
      continue-on-error: false
    
    - name: Unit Tests with Coverage
      run: |
        pytest tests/ --cov=. --cov-report=xml --cov-report=term
      continue-on-error: false
    
    - name: Upload Coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
    
    - name: Coverage Threshold Check
      run: |
        coverage report --fail-under=80
      # Falha se cobertura < 80%
```

**GitLab CI - Pipeline com Quality Gates**:

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - security
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip

lint:black:
  stage: lint
  image: python:3.11
  script:
    - pip install black
    - black --check clarify_patched.py
  allow_failure: false

lint:flake8:
  stage: lint
  image: python:3.11
  script:
    - pip install flake8
    - flake8 clarify_patched.py --max-line-length=88 --statistics
  allow_failure: false

test:pytest:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/ --cov=. --cov-report=term --cov-report=html
    - coverage report --fail-under=80
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
  allow_failure: false

security:bandit:
  stage: security
  image: python:3.11
  script:
    - pip install bandit
    - bandit -r clarify_patched.py -f data -o bandit-report.data
  artifacts:
    reports:
      sast: bandit-report.data
  allow_failure: false

deploy:production:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - # Comandos de deploy
  only:
    - main
  when: manual  # Deploy manual após quality gates passarem
```

**Quality Metrics - Dashboards**:

```python
# Script para gerar relatório de qualidade
import subprocess
import data

def run_quality_checks():
    """Executa quality gates e gera relatório."""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # 1. Code Coverage
    cov = subprocess.run(
        ["pytest", "--cov=.", "--cov-report=data"],
        capture_output=True
    )
    with open("coverage.data") as f:
        results["checks"]["coverage"] = data.load(f)["totals"]["percent_covered"]
    
    # 2. Linting Score
    flake8 = subprocess.run(
        ["flake8", "clarify_patched.py", "--statistics"],
        capture_output=True,
        text=True
    )
    results["checks"]["linting_errors"] = len(flake8.stdout.splitlines())
    
    # 3. Security Issues
    bandit = subprocess.run(
        ["bandit", "-r", ".", "-f", "data"],
        capture_output=True
    )
    bandit_data = data.loads(bandit.stdout)
    results["checks"]["security_issues"] = len(bandit_data["results"])
    
    # 4. Type Coverage (MyPy)
    mypy = subprocess.run(
        ["mypy", "clarify_patched.py", "--data-report", ".mypy"],
        capture_output=True
    )
    # Parse MyPy report...
    
    # Quality Score (0-100)
    score = (
        results["checks"]["coverage"] * 0.4 +
        (100 - min(results["checks"]["linting_errors"], 100)) * 0.3 +
        (100 - min(results["checks"]["security_issues"] * 10, 100)) * 0.3
    )
    results["quality_score"] = round(score, 2)
    
    # Pass/Fail Gates
    results["gates"] = {
        "coverage": results["checks"]["coverage"] >= 80,
        "linting": results["checks"]["linting_errors"] == 0,
        "security": results["checks"]["security_issues"] == 0
    }
    results["passed"] = all(results["gates"].values())
    
    return results

# Integrar com CI
if __name__ == "__main__":
    results = run_quality_checks()
    print(data.dumps(results, indent=2))
    
    if not results["passed"]:
        print("\n❌ Quality gates FAILED!")
        exit(1)
    else:
        print("\n✅ All quality gates PASSED!")
```

**Badge de Status no README**:

```markdown
# Clarify - Task Management

[![CI Status](https://github.com/user/clarify/workflows/CI/badge.svg)](https://github.com/user/clarify/actions)
[![Coverage](https://codecov.io/gh/user/clarify/branch/main/graph/badge.svg)](https://codecov.io/gh/user/clarify)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=clarify&metric=alert_status)](https://sonarcloud.io/dashboard?id=clarify)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Badges mostram status de qualidade visualmente
```

**Por quê CI/CD é crucial**:
- ✅ **Automação**: Valida qualidade sem intervenção manual
- ✅ **Consistência**: Mesmas regras para todos desenvolvedores
- ✅ **Prevenção**: Detecta problemas antes de merge/deploy
- ✅ **Confiança**: Time sabe que código quebrado não vai para produção
- ✅ **Velocidade**: Feedback rápido (minutos, não horas)

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
        - `docs/architecture/` - Decisões arquiteturais (ADRs)
        - `docs/user-guide/` - Guias de usuário
        - `docs/dev-guide/` - Guias de desenvolvimento
        - `docs/adr/` - Architecture Decision Records (ver Etapa 11.5)
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
│   └── adr/                   ✅ ADRs organizados
└── README.md                  ✅ README raiz mantido
```

**Por quê?**: Manter repositório limpo, evitar commits de lixo, facilitar navegação, profissionalismo, organização recursiva garante escalabilidade. Documentar o estado **limpo** e **organizado** do projeto.

---

### 1️⃣1️⃣.5️⃣ **Architecture Decision Records (ADR)** (Opcional)

**Quando Aplicar**:
- ✅ Decisões arquiteturais importantes (framework, biblioteca, padrão)
- ✅ Trade-offs significativos foram feitos
- ✅ Projetos de longo prazo (> 6 meses)
- ✅ Equipes com rotatividade (onboarding)
- ✅ Quando "por quê fizemos assim?" será perguntado

**Não Aplicar Se**:
- ❌ Decisões triviais (naming, formatação)
- ❌ Projeto solo de curto prazo
- ❌ Protótipo que será descartado
- ❌ Decisões óbvias/convencionais

**O que é ADR?**

ADR (Architecture Decision Record) documenta **por quê** decisões importantes foram tomadas, não apenas **o quê** foi decidido. Útil para:
- Justificar escolhas para futuros desenvolvedores
- Evitar reabrir discussões já resolvidas
- Aprender com decisões passadas (boas e ruins)

**Template de ADR**:

```markdown
# ADR-001: Escolha de PyQt6 para GUI

## Status
✅ **ACEITO** - 2024-01-15

## Contexto
O projeto precisa de interface gráfica (GUI) para gerenciar tarefas além da CLI existente.

**Requisitos**:
- Cross-platform (Linux, Windows, macOS)
- Integração com código Python existente
- Capacidade de criar layouts complexos (docks, tabs, menus)
- Licenciamento compatível com GPL
- Comunidade ativa e documentação

**Alternativas Consideradas**:
1. **Tkinter** (nativo Python)
2. **PyQt6** (Qt bindings)
3. **wxPython** (wxWidgets bindings)
4. **Kivy** (mobile-first)

## Decisão
Escolhemos **PyQt6** para a implementação da GUI.

## Consequências

### Positivas ✅
- **Layout Avançado**: QDockWidget, QMainWindow permitem layout profissional
- **Widgets Ricos**: QTreeWidget, QTableWidget já implementados e robustos
- **Styling**: QSS (CSS-like) permite customização visual
- **Documentação**: Excelente documentação oficial + comunidade grande
- **Performance**: Nativo C++, mais rápido que Tkinter
- **Multiplataforma**: Funciona bem em Linux, Windows, macOS

### Negativas ❌
- **Licença**: GPL ou comercial (~$450/dev) - escolhemos GPL
- **Tamanho**: Binário maior (~50MB) vs Tkinter (~5MB)
- **Curva de Aprendizado**: Mais complexo que Tkinter
- **Dependência Externa**: Requer instalação `pip install PyQt6`

### Riscos 🚨
- **Licença GPL**: Projeto deve ser open-source (OK para nós)
- **Breaking Changes**: Qt6 é recente, pode haver mudanças
- **Packaging**: PyInstaller precisa configuração especial para PyQt6

### Alternativas Descartadas
- **Tkinter**: Layout primitivo, sem dock widgets nativos
- **wxPython**: Documentação inferior, comunidade menor
- **Kivy**: Focado em mobile, estilo não-nativo desktop

## Implementação
- Refatorar código existente para separar lógica de apresentação
- Criar `ClarifyGUI` class com QMainWindow
- Manter compatibilidade CLI para usuários existentes
- Documentar instalação PyQt6 no README

## Referências
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt6 Documentation](https://doc.qt.io/qt-6/)
- Task Example: "Add GUI with docking support"

## Notas
Se no futuro precisarmos de licença mais permissiva (MIT/Apache), considerar:
- Migrar para PySide6 (Qt LGPL binding)
- Reescrever com Tkinter + ttkbootstrap
- Usar Dear PyGui (MIT, porém OpenGL, não nativo)

---
**Autor**: Josué  
**Data**: 2024-01-15  
**Última Atualização**: 2024-01-15
```

**Estrutura de Diretórios para ADRs**:

```
clarify/
├── docs/
│   ├── adr/
│   │   ├── 001-choice-of-pyqt6.md
│   │   ├── 002-data-storage-format.md
│   │   ├── 003-simplicity-protocol-versioning.md
│   │   └── README.md  (Índice de ADRs)
│   ├── PROTOCOLO_SIMPLICIDADE_1.md
│   └── PROTOCOLO_SIMPLICIDADE_2.md
├── clarify_patched.py
└── README.md
```

**Índice de ADRs** (`docs/adr/README.md`):

```markdown
# Architecture Decision Records

## Active Decisions
- [ADR-001](001-choice-of-pyqt6.md): Escolha de PyQt6 para GUI ✅ ACEITO
- [ADR-003](003-simplicity-protocol-versioning.md): Versionamento Protocolo Simplicidade ✅ ACEITO

## Superseded Decisions
- [ADR-002](002-data-storage-format.md): DATA como formato de armazenamento ⚠️ SUPERSEDED
  - Substituído por SQLite em ADR-004 (2024-02-01)

## Rejected Decisions
- (nenhum)

## Proposed (Pendente Discussão)
- ADR-005: Implementar suporte a plugins
- ADR-006: Migrar de DATA para SQLite

---

## Template
Novos ADRs devem seguir o template em `adr-template.md`

## Numeração
ADRs são numerados sequencialmente: 001, 002, 003, etc.
```

**Exemplo de ADR Superseded**:

```markdown
# ADR-002: DATA como Formato de Armazenamento

## Status
⚠️ **SUPERSEDED** por [ADR-004](004-migrate-to-sqlite.md) em 2024-02-01

## Contexto
(contexto original...)

## Decisão
Usar DATA para persistência de tasks.

## Consequências

### Por quê foi supersedido?
DATA funcionou bem para até ~500 tasks, mas performance degradou significativamente:
- Tempo de leitura: 2.5s para 1000 tasks (inaceitável)
- Concorrência: Não suporta múltiplas janelas simultâneas
- Queries: Difícil filtrar/buscar sem carregar tudo

**Solução**: Migrar para SQLite (ADR-004) mantendo DATA como export opcional.

---
**Autor**: Josué  
**Data Original**: 2023-11-10  
**Superseded**: 2024-02-01
```

**Ferramentas para ADRs**:

```bash
# adr-tools - CLI para criar ADRs
npm install -g adr-log

# Criar novo ADR
adr new "Implement caching layer"

# Lista todos ADRs
adr list

# Supersede ADR antigo
adr new -s 2 "Migrate from DATA to SQLite"
# Cria ADR novo e marca #2 como superseded

# Gerar visualização
adr generate graph > adr-graph.svg
```

**Quando Criar ADR**:

```python
# ✅ MERECE ADR - Decisão impactante
"""
Decidimos usar SQLite em vez de DATA.
Impacto:
- Muda persistência de dados (migração necessária)
- Afeta performance (10x mais rápido)
- Adiciona dependência (sqlite3 - nativa)
- Código de acesso a dados precisa refatoração
"""

# ❌ NÃO MERECE ADR - Decisão trivial
"""
Decidimos renomear variável 'x' para 'task_count'.
Impacto: Clareza de código apenas.
"""

# ✅ MERECE ADR - Trade-off significativo
"""
Decidimos NÃO implementar encryption de tasks.
Rationale:
- Complexidade alta (key management)
- Benefício baixo (tasks não são sensíveis)
- Podemos adicionar depois se necessário
"""
```

**Checklist de ADR**:

```markdown
### ADR Checklist - ADR-XXX: [Título]

#### Conteúdo Completo
- [ ] **Status**: Proposto/Aceito/Rejeitado/Superseded definido
- [ ] **Contexto**: Problema claramente descrito
- [ ] **Alternativas**: Pelo menos 2 alternativas consideradas
- [ ] **Decisão**: Escolha explicitamente declarada
- [ ] **Consequências**: Positivas E negativas documentadas
- [ ] **Riscos**: Riscos identificados e mitigações propostas

#### Qualidade
- [ ] **Justificativa**: "Por quê" está claro (não só "o quê")
- [ ] **Trade-offs**: Trade-offs explicitados
- [ ] **Reversibilidade**: Custo de reverter documentado
- [ ] **Referências**: Links para docs/issues/PRs relevantes

#### Processo
- [ ] **Numeração**: ADR numerado sequencialmente
- [ ] **Índice**: README.md atualizado com novo ADR
- [ ] **Review**: ADR revisado por pelo menos 1 pessoa
- [ ] **Commit**: Commitado junto com código relacionado
```

**ADR em Pull Request**:

```markdown
## PR #145: Implement SQLite storage

### Descrição
Migra persistência de DATA para SQLite (Task Example).

### Architecture Decision
Este PR implementa **ADR-004: Migrate to SQLite**.

**Trade-offs**:
- ✅ 10x mais rápido (2.5s → 0.2s para 1000 tasks)
- ✅ Suporta concorrência (múltiplas janelas)
- ❌ Migração necessária para usuários existentes
- ❌ Código de persistência mais complexo

**Riscos Mitigados**:
- Migração automática no primeiro uso (v2.0.0)
- Backup automático do DATA antes de migrar
- Rollback disponível se migração falhar

### Ver ADR
- [ADR-004: Migrate to SQLite](docs/adr/004-migrate-to-sqlite.md)
- Supersedes ADR-002 (DATA storage)

### Checklist
- [x] ADR criado e commitado
- [x] Código de migração implementado
- [x] Testes de migração adicionados
- [x] Documentação atualizada
```

**Por quê ADRs são valiosos**:
- ✅ **Contexto**: Futuros devs entendem "por quê" decisões foram tomadas
- ✅ **Evita Retrabalho**: Não reabrem discussões já resolvidas
- ✅ **Onboarding**: Novos membros aprendem arquitetura rapidamente
- ✅ **Aprendizado**: Time aprende com decisões passadas (good and bad)
- ✅ **Auditoria**: Stakeholders veem processo de decisão transparente

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
   - **[SIMPLICIDADE 2]** ADRs formais (Architecture Decision Records) quando aplicável

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

7. **[SIMPLICIDADE 2] Documentação Enterprise Adicional**:
   - Documentação de API (Sphinx/pdoc) para bibliotecas públicas
   - Checklist de segurança OWASP preenchido
   - Checklist de acessibilidade WCAG (para GUI)
   - Resultados de profiling (para features críticas)
   - Planos de rollback documentados

#### **📂 Estrutura Obrigatória de Documentação (Simplicidade 2)**

A pasta `docs/` deve conter no mínimo:

```
docs/
├── REQUIREMENTS.md          # Lista de tarefas e requisitos (atualizado a cada ciclo)
├── vX.Y.Z-SPECIFICATIONS.md # Especificações detalhadas da versão atual
├── CHANGELOG.md             # Histórico de mudanças (o que foi implementado e quando)
├── ARCHITECTURE.md          # Decisões arquiteturais e estrutura do projeto
├── ADR/                     # Architecture Decision Records (Simplicidade 2)
│   ├── ADR-001-[decisao].md
│   └── ADR-002-[decisao].md
├── SECURITY.md              # Checklist OWASP e vulnerabilidades mitigadas
├── API/                     # Documentação de API (se aplicável)
│   └── api-reference.html   # Gerado por Sphinx/pdoc
└── [feature]-GUIDE.md       # Guias específicos para funcionalidades complexas
```

**Criação Automática**:
- Se a pasta `docs/` não existe, ela **DEVE SER CRIADA AUTOMATICAMENTE** pela IA
- Se um arquivo de documentação não existe, ele **DEVE SER CRIADO** pela IA no primeiro ciclo
- Todos os arquivos devem ser atualizados **A CADA CICLO** de implementação

#### **📋 Template Mínimo para SPECIFICATIONS.md (Simplicidade 2)**

Cada arquivo de especificações de versão deve conter no mínimo:

```markdown
# [Nome do Projeto] vX.Y.Z - [Nome Descritivo]

**Data**: DD/MM/AAAA
**Sprint**: X tasks em Y horas
**Metodologia**: Protocolo Simplicidade 2
**Code Review**: [Aprovado por: Nome/Equipe]

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
- ADR criado: `ADR-XXX-[nome].md` (se aplicável)

**Arquivos Criados/Modificados**:
- `path/to/file.py` (+XXX linhas) - [descrição]
- `path/to/test.py` (NOVO) - [descrição]

**Testes**:
- XX unit tests (YY passing)
- Cenários cobertos: [lista]
- Cobertura: ZZ%

**Segurança (OWASP)**:
- [ ] A01: Broken Access Control - [Status/Mitigação]
- [ ] A02: Cryptographic Failures - [Status/Mitigação]
- [ ] A03: Injection - [Status/Mitigação]
- (ver SECURITY.md para checklist completo)

**Performance** (se feature crítica):
- Profiling realizado: [ferramenta]
- Gargalos identificados: [lista]
- Otimizações aplicadas: [lista]

**Exemplo de Uso**:
```python
# Exemplo prático de como usar a funcionalidade
```

## ✅ Qualidade (Protocolo Simplicidade 2)
- ✅ Arquitetura Modular
- ✅ Type Hints (100%)
- ✅ Docstrings completas
- ✅ Tratamento de erros
- ✅ Testes (X passing, Y% coverage)
- ✅ Code Review aprovado
- ✅ CI/CD quality gates passing
- ✅ Security checklist completo
- ✅ Commits semânticos
- ✅ **Documentação completa na pasta docs/**
- ✅ Código limpo (PEP8/ESLint/etc)
- ✅ Rollback plan documentado (se crítico)

## 📊 Estatísticas
- TOTAL: X% completo (Y/Z tasks)
- Commits: N pushed
- Code Review: Aprovado em DD/MM/AAAA
```

#### **🔍 Validação da Documentação (Simplicidade 2)**

Antes de finalizar cada ciclo (Etapa 13 - Commit), a IA **DEVE VERIFICAR**:

- [ ] ✅ Pasta `docs/` existe e está atualizada
- [ ] ✅ Arquivo SPECIFICATIONS.md criado/atualizado para este ciclo
- [ ] ✅ TODAS as funcionalidades implementadas estão documentadas
- [ ] ✅ TODOS os comportamentos novos estão descritos
- [ ] ✅ TODOS os arquivos criados/modificados estão listados
- [ ] ✅ Decisões técnicas e arquiteturais estão justificadas
- [ ] ✅ ADRs criados para decisões arquiteturais importantes
- [ ] ✅ Exemplos de uso estão incluídos
- [ ] ✅ Testes estão documentados
- [ ] ✅ Checklist de segurança OWASP está completo (em SECURITY.md)
- [ ] ✅ Resultados de profiling documentados (se aplicável)
- [ ] ✅ Documentação de API gerada (se biblioteca pública)
- [ ] ✅ Code review aprovado e documentado

**Se algum item não estiver completo, a IA NÃO DEVE prosseguir para o commit** até completar a documentação.

#### **📌 Rationale: Por Quê Este Requisito é OBRIGATÓRIO**

1. **Rastreabilidade**: Permite entender TUDO que foi implementado ao longo do tempo
2. **Manutenibilidade**: Facilita manutenção futura (pelo mesmo dev ou outros)
3. **Conhecimento Organizacional**: Preserva decisões e contexto do projeto
4. **Onboarding**: Novos desenvolvedores/IAs entendem rapidamente o sistema
5. **Auditoria**: Possibilita revisão e validação de implementações (crítico para enterprise)
6. **Continuidade**: Garante que funcionalidades não sejam esquecidas ou perdidas
7. **Profissionalismo**: Projetos sérios têm documentação completa e atualizada
8. **Conformidade**: Facilita auditorias de segurança, compliance (ISO, SOC2, etc.)
9. **Colaboração em Equipe**: Essencial para equipes grandes e distribuídas
10. **Gestão de Mudanças**: Documenta o porquê de cada decisão técnica (ADRs)

**Este requisito transforma a pasta `docs/` em um histórico vivo e completo de tudo que foi implementado no projeto, essencial para ambientes enterprise.**

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

### 📊 **Legenda de Classificação de Tarefas (Simplicidade 2)**

**Objetivo**: Padronizar a classificação e priorização de tarefas para facilitar a organização pela IA, comunicação entre equipe e compreensão entre diferentes sistemas de inteligência artificial.

**Nota para Simplicidade 2**: Em ambientes enterprise com equipes grandes, a classificação de tarefas deve ser **integrada com a Matriz de Decisão (Etapa 2.5)** para garantir escolhas objetivas e rastreáveis.

#### **Status da Tarefa**

- 🔴 **Not Started** (Não Iniciada) - Aguardando início, sem trabalho realizado
- 🟡 **In Progress** (Em Progresso) - Desenvolvimento ativo, trabalho em andamento
- 🟢 **Done** (Concluída) - Implementada, testada, revisada por pares e finalizada
- 🔵 **Blocked** (Bloqueada) - Impedida por dependência externa ou problema técnico

#### **Complexidade da Tarefa**

- 🟢 **Simples** (0-1h) - Baixo risco, poucas dependências, escopo claro
- 🟡 **Média** (1-2h) - Risco médio, algumas integrações, pode requerer testes adicionais
- 🔴 **Complexa** (>2h) - Alto risco, muitas dependências, escopo aberto ou ambíguo

#### **Priorização MoSCoW**

- 🔴 **Must Have** - Crítico para o funcionamento do sistema, bloqueante para release
- 🟡 **Should Have** - Importante mas não bloqueante, pode ser adiado se necessário
- 🟢 **Could Have** - Desejável se houver tempo, baixa prioridade
- ⚪ **Won't Have** (Later) - Explicitamente fora do escopo atual, para versões futuras

#### **Integração com Matriz de Decisão (Simplicidade 2)**

A Matriz de Decisão (Etapa 2.5) fornece scoring numérico (0-35 pontos) complementar aos indicadores visuais:

```markdown
## Sprint v3.2 - Backlog Priorizado

### 🔴 MUST HAVE

| Task | Status | Complex. | Score | Ordem |
|------|--------|----------|-------|-------|
| #42 Auth 2FA | 🔴 | 🔴 | 25.0 | 3º |
| #43 Rate Limiting | 🔴 | 🟡 | 28.5 | 2º |
| #44 Logging | 🔴 | 🟢 | 33.5 | 1º ⭐ COMEÇAR AQUI |

**Justificativa**: Task #44 tem maior score (33.5) apesar de ser Must Have como as outras.
Começar por ela reduz riscos e permite time se aquecer antes das tasks complexas.
```

**Combinando Matriz de Decisão + Classificação Visual**:
1. Use **Matriz de Decisão** para scoring objetivo (5 critérios numéricos)
2. Use **Indicadores Visuais** (🔴🟡🟢🔵) para status rápido no backlog
3. Use **MoSCoW** para definir escopo de releases
4. Use **Complexidade** para balancear sprints (não só tarefas difíceis)

#### **Frameworks Avançados de Priorização**

Para equipes enterprise que precisam justificar decisões para stakeholders:

##### **Matriz RICE** (Quantitativa)

`Score RICE = (Reach × Impact × Confidence) / Effort`

Útil para:
- ✅ Decisões de product management com múltiplas features competindo
- ✅ Apresentações para C-level (dados objetivos)
- ✅ Planejamento de roadmap de longo prazo

**Exemplo Enterprise**:
```markdown
| Feature | Reach | Impact | Conf. | Effort | RICE | Decisão |
|---------|-------|--------|-------|--------|------|---------|
| SSO Integration | 5000 | 3 | 80% | 80h | 150 | Q1 2024 |
| Dashboard v2 | 2000 | 2 | 100% | 40h | 100 | Q2 2024 |
| Dark Mode | 8000 | 0.5 | 100% | 20h | 200 | Q1 2024 ⭐ |

Decisão: Priorizar Dark Mode (RICE=200) antes de SSO (RICE=150)
Razão: Maior alcance com menor esforço, apesar de impacto individual menor
```

##### **Matriz de Eisenhower** (Urgência × Importância)

Útil para:
- ✅ Gestão de incidentes e crises
- ✅ Priorização em contextos com muitas "urgências"
- ✅ Identificar tarefas que devem ser delegadas ou automatizadas

**Adaptação para Equipes**:
- **Q1 (Urgente + Importante)**: Time sênior / Tech leads
- **Q2 (Não Urgente + Importante)**: Time pleno, planejado
- **Q3 (Urgente + Não Importante)**: Delegar para júnior ou automatizar
- **Q4 (Não Urgente + Não Importante)**: Eliminar ou backlog muito distante

#### **Exemplo Completo Simplicidade 2**

```markdown
# TASKS.md - Sprint v4.1 (Enterprise Team)

## 📊 Legenda
- **Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Done | 🔵 Blocked
- **Complexidade**: 🟢 Simples (0-1h) | 🟡 Média (1-2h) | 🔴 Complexa (>2h)
- **MoSCoW**: 🔴 Must | 🟡 Should | 🟢 Could | ⚪ Won't

## 📊 Estatísticas
- Progresso: 65% (26/40 tarefas)
- Velocity: 12 story points/sprint
- Bugs Abertos: 3 (1 crítico, 2 médios)

## 🔴 MUST HAVE - Release v4.1

### Prioridade Alta (Matriz Score > 25)
- 🔴🟢 [ ] #101 Adicionar rate limiting (Score: 33.5) ⭐ INICIAR
  - **Assignee**: @maria (Backend Lead)
  - **Revisão**: @joao (Security Review obrigatório)
  - **Estimativa**: 3h
  - **Dependências**: Nenhuma
  
- 🟡🟡 [ ] #102 Implementar circuit breaker (Score: 28.0, 60% completo)
  - **Assignee**: @pedro (Pleno)
  - **Revisão**: @maria (Code Review)
  - **Estimativa**: 5h (2h restantes)
  - **Blocker Resolvido**: ✅ Biblioteca atualizada para v3.2

### Prioridade Média (Matriz Score 15-25)
- 🔵🔴 [ ] #103 Migrar para Kubernetes (Score: 22.0, BLOQUEADO)
  - **Assignee**: @infra-team
  - **Blocker**: Aguardando aprovação orçamento DevOps
  - **Estimativa**: 16h
  - **Fallback**: Manter Docker Swarm por mais 1 sprint

## 🟡 SHOULD HAVE - Release v4.2
- 🔴🟡 [ ] #104 Adicionar métricas Prometheus (Score: 26.5)
- 🔴🟢 [ ] #105 Tooltips de ajuda (Score: 30.0)

## 🟢 COULD HAVE - Backlog
- 🔴🟡 [ ] #106 Dark mode (RICE: 200, alta prioridade no backlog)

---
**Próxima Retrospectiva**: Sexta 15h (validar recomendações da IA)
```

#### **Recomendações para IA em Contexto Enterprise**

**Ao classificar tarefas para equipes (Simplicidade 2), a IA deve**:
1. ✅ **Considerar Code Review**: Tasks complexas precisam de revisor sênior disponível
2. ✅ **Balancear carga de trabalho**: Não alocar todas tasks complexas para mesma pessoa
3. ✅ **Respeitar dependências de equipe**: Backend antes de Frontend em integrações
4. ✅ **Documentar decisões**: Usar ADR (Etapa 11.5) para escolhas arquiteturais importantes
5. ✅ **Comunicar blockers**: Marcar 🔵 e notificar time imediatamente
6. ✅ **Integrar com Matriz de Decisão**: Scoring + indicadores visuais complementares
7. ✅ **Validar com stakeholders**: Features MUST HAVE confirmadas em Sprint Planning

**Diferenças Simplicidade 2 vs 1**:
- **S2**: Matriz de Decisão (scoring numérico) é **OBRIGATÓRIA** quando 3+ tasks competem
- **S2**: Status deve refletir **code review** (não marcar Done sem aprovação de pares)
- **S2**: Recomendações da IA validadas em **Retrospectiva de Sprint** (Etapa 13.5)
- **S2**: Complexidade inclui **tempo de review** e **teste de aceitação**

---

**🤖 Recomendações de Tarefas pela IA**:
Para equipes enterprise (Simplicidade 2), as recomendações da IA devem ser **revisadas em retrospectivas de sprint** (Etapa 13.5) antes de serem adicionadas ao TASKS.md. Isso garante consenso da equipe e alinhamento com stakeholders.

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
# Clarify v2.9.X - [Nome Descritivo]

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

### 1️⃣2️⃣.5️⃣ **Rollback Plans** (Opcional - Para Features Críticas)

**Quando Aplicar**:
- ✅ Features críticas em produção
- ✅ Mudanças em schema de dados/migrations
- ✅ Alterações em APIs públicas
- ✅ Deploy de features com risco alto
- ✅ Quando downtime é inaceitável

**Não Aplicar Se**:
- ❌ Feature experimental/beta (flag controlada)
- ❌ Mudança interna sem impacto usuário
- ❌ Protótipo ou ambiente dev/staging apenas
- ❌ Hotfix trivial (typo, css)

**O que é Rollback Plan?**

Plano documentado para **reverter** uma mudança se algo der errado em produção. Diferente de "desfazer commit", rollback considera:
- Estado de dados (migrations, schemas)
- Dependências externas (APIs, serviços)
- Usuários ativos (downtime, dados em trânsito)

**Template de Rollback Plan**:

```markdown
# Rollback Plan - Task Example: Migração para SQLite

## Resumo da Mudança
**Feature**: Migração de DATA para SQLite storage  
**Versão**: v2.0.0 → v1.9.x  
**Impacto**: ALTO - Altera formato de persistência  
**Risco**: MÉDIO - Migração de dados pode falhar  

## Critérios para Rollback
Executar rollback SE:
- [ ] Taxa de erro > 5% em 1 hora após deploy
- [ ] Usuários reportam perda de dados (tasks desaparecendo)
- [ ] Performance pior que versão anterior (> 2x mais lento)
- [ ] Crashes frequentes (> 10 reports em 24h)
- [ ] Migração automática falha para > 10% usuários

NÃO executar rollback SE:
- ✅ Apenas 1-2 usuários reportam problemas (investigar primeiro)
- ✅ Bug menor que pode ser hotfixado rapidamente
- ✅ Performance aceitável (< 1s), mesmo se não ideal

## Passo-a-Passo do Rollback

### Fase 1: Preparação (5 minutos)
1. **Notificar usuários**:
   ```bash
   # Criar banner de manutenção
   echo "⚠️ Maintenance in progress - Rolling back to v1.9.5" > maintenance.txt
   ```

2. **Backup estado atual**:
   ```bash
   # Backup do SQLite database atual
   cp ~/.config/clarify/clarify.db ~/.config/clarify/clarify.db.backup-$(date +%s)
   
   # Backup de logs
   cp ~/.config/clarify/clarify.log /tmp/clarify-rollback-logs.txt
   ```

3. **Verificar backup DATA disponível**:
   ```bash
   # Confirmar que DATA backup existe (criado na migração)
   ls -lh ~/.config/clarify/tasks.data.backup
   # Deve mostrar arquivo criado durante migração para v2.0.0
   ```

### Fase 2: Rollback (10 minutos)
1. **Reverter código para versão anterior**:
   ```bash
   cd ~/clarify
   git checkout v1.9.5  # Tag da versão estável anterior
   
   # OU se em produção via package manager
   pip install clarify==1.9.5 --force-reinstall
   ```

2. **Restaurar dados do backup DATA**:
   ```bash
   # Copiar backup DATA de volta
   cp ~/.config/clarify/tasks.data.backup ~/.config/clarify/tasks.data
   
   # Remover SQLite database (v1.9.5 não usa)
   rm ~/.config/clarify/clarify.db
   ```

3. **Verificar integridade dos dados**:
   ```bash
   # Validar DATA não está corrompido
   python -c "import data; data.load(open('~/.config/clarify/tasks.data'))"
   # Deve completar sem erro
   
   # Contar tasks
   python -c "import data; data = data.load(open('~/.config/clarify/tasks.data')); print(f'{len(data[\"tasks\"])} tasks restored')"
   ```

4. **Reiniciar aplicação**:
   ```bash
   # Se processo rodando, matar
   pkill -f clarify
   
   # Iniciar v1.9.5
   python clarify.py
   ```

### Fase 3: Validação (5 minutos)
1. **Smoke Tests**:
   ```bash
   # Teste 1: App inicia sem crash
   clarify --version
   # Esperado: v1.9.5
   
   # Teste 2: Lista tasks
   clarify list
   # Esperado: Tasks exibidas corretamente
   
   # Teste 3: Adicionar task
   clarify add "Test rollback task"
   # Esperado: Task adicionada sem erro
   
   # Teste 4: GUI abre (se aplicável)
   clarify --gui &
   # Esperado: GUI abre sem crash
   ```

2. **Verificar logs**:
   ```bash
   tail -n 50 ~/.config/clarify/clarify.log
   # Verificar ausência de erros SQLite
   ```

3. **Contato com usuários afetados**:
   - Pedir 3-5 usuários testarem funcionalidade básica
   - Confirmar que dados deles estão intactos

### Fase 4: Comunicação (Imediato)
1. **Notificar stakeholders**:
   ```markdown
   ## Rollback Executado - v2.0.0 → v1.9.5
   
   **Timestamp**: 2024-01-20 15:30 UTC  
   **Motivo**: Taxa de erro 12% em migração SQLite (critério: >5%)  
   **Status**: ✅ Rollback completo, sistema estável  
   **Impacto**: Usuários de v2.0.0 devem reinstalar v1.9.5  
   
   **Ação Usuários**:
   ```bash
   pip install clarify==1.9.5 --force-reinstall
   ```
   
   Dados preservados via backup automático DATA.
   
   **Próximos Passos**:
   - Root cause analysis da falha de migração
   - Fix planejado para v2.0.1 (ETA: 2024-01-25)
   - Beta testing expandido antes do release
   ```

2. **Criar issue post-mortem**:
   ```markdown
   # Post-Mortem: Rollback v2.0.0 → v1.9.5
   
   ## Linha do Tempo
   - 14:00 UTC: Deploy v2.0.0
   - 14:30 UTC: Primeiros relatórios de falha de migração
   - 15:00 UTC: Taxa de erro atinge 12% (critério rollback: >5%)
   - 15:15 UTC: Decisão de rollback tomada
   - 15:30 UTC: Rollback completo
   
   ## Root Cause
   - Migração SQLite falhou para arquivos DATA > 5MB
   - Causa: Timeout de 30s insuficiente para tasks complexas
   - Afetou ~12% usuários (heavy users com >500 tasks)
   
   ## Lessons Learned
   - ✅ Rollback plan funcionou perfeitamente
   - ✅ Backup automático salvou dados
   - ❌ Testing não cobriu usuários heavy (>500 tasks)
   - ❌ Timeout de migração muito curto
   
   ## Action Items
   - [ ] Aumentar timeout migração para 5min (#145)
   - [ ] Adicionar progress bar para migrations longas (#146)
   - [ ] Criar suite de testes com datasets grandes (#147)
   - [ ] Beta program com heavy users antes de release (#148)
   ```

## Tempo Estimado de Rollback
- **Preparação**: 5 minutos
- **Execução**: 10 minutos
- **Validação**: 5 minutos
- **TOTAL**: ~20 minutos (downtime esperado)

## Dependências Externas
- ✅ Backup DATA criado automaticamente na migração
- ✅ Git tags de versões anteriores disponíveis
- ❌ Não depende de serviços externos (DB, APIs)

## Dados em Risco
- **Alto Risco**: Tasks criadas/editadas após deploy v2.0.0 (não existem no backup)
- **Baixo Risco**: Tasks existentes antes de v2.0.0 (preservadas no backup)

**Mitigação**: Exportar SQLite → DATA antes de rollback para preservar mudanças recentes.

```bash
# Script de export antes de rollback
python -c "
import sqlite3, data
conn = sqlite3.connect('~/.config/clarify/clarify.db')
cursor = conn.execute('SELECT * FROM tasks')
tasks = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
data.dump({'tasks': tasks}, open('rollback-export.data', 'w'), indent=2)
"
# Usuários podem manualmente mesclar mudanças depois
```

## Pessoas de Contato
- **Decisão de Rollback**: @lead-dev (Josué)
- **Execução Técnica**: @dev-team
- **Comunicação Usuários**: @support-team

---
**Criado**: 2024-01-15  
**Última Atualização**: 2024-01-15  
**Testado**: ❌ Não (executar dry-run antes do deploy)
```

**Feature Flags - Alternativa ao Rollback**:

```python
# Em vez de rollback completo, usar feature flag para desabilitar feature

class Config:
    """Configuration with feature flags."""
    
    # Feature flag - controle remoto
    SQLITE_STORAGE_ENABLED = os.getenv("CLARIFY_SQLITE_ENABLED", "true").lower() == "true"
    
    def get_storage_backend(self):
        """Get storage backend based on feature flag."""
        if self.SQLITE_STORAGE_ENABLED:
            return SQLiteStorage()
        else:
            return DATAStorage()  # Fallback seguro

# Em caso de problema, desabilitar remotely:
# export CLARIFY_SQLITE_ENABLED=false
# Ou via config file / dashboard admin

# Usuários automaticamente voltam para DATA sem reinstalar
```

**Reversible Migrations**:

```python
# Migrations devem ser reversíveis

class MigrationV2:
    """Migration from DATA to SQLite - REVERSIBLE."""
    
    def up(self):
        """Migrate DATA → SQLite."""
        # 1. Criar backup DATA
        shutil.copy("tasks.data", "tasks.data.backup")
        
        # 2. Criar SQLite schema
        self._create_sqlite_schema()
        
        # 3. Migrar dados
        self._migrate_data_to_sqlite()
        
        # 4. NÃO deletar DATA (manter para rollback)
        # os.remove("tasks.data")  ❌ NUNCA fazer isso
    
    def down(self):
        """Rollback SQLite → DATA."""
        if not os.path.exists("tasks.data.backup"):
            raise RollbackError("Backup DATA not found - cannot rollback!")
        
        # 1. Restaurar backup
        shutil.copy("tasks.data.backup", "tasks.data")
        
        # 2. Remover SQLite
        os.remove("clarify.db")
        
        print("✅ Rollback completo - usando DATA storage")
```

**Checklist de Rollback Plan**:

```markdown
### Rollback Plan Checklist - Task #XX

#### Planejamento
- [ ] **Critérios**: Critérios claros para quando executar rollback
- [ ] **Passos**: Passo-a-passo detalhado documentado
- [ ] **Tempo**: Tempo estimado de rollback calculado
- [ ] **Dependências**: Dependências externas identificadas
- [ ] **Dados**: Risco de perda de dados avaliado

#### Preparação
- [ ] **Backup**: Mecanismo de backup automatizado implementado
- [ ] **Tags**: Git tags de versões estáveis criadas
- [ ] **Scripts**: Scripts de rollback testados em staging
- [ ] **Contatos**: Pessoas de contato definidas

#### Validação
- [ ] **Dry-run**: Rollback testado em ambiente de staging
- [ ] **Smoke Tests**: Smoke tests definidos para validação pós-rollback
- [ ] **Comunicação**: Template de comunicação preparado
- [ ] **Post-mortem**: Template de post-mortem criado
```

**Por quê Rollback Plans são críticos**:
- ✅ **Confiança**: Equipe pode fazer deploys ousados sabendo que pode reverter
- ✅ **Downtime**: Minimiza downtime (20min vs horas debuggando)
- ✅ **Dados**: Protege dados de usuários (backup strategy)
- ✅ **Comunicação**: Template preparado = comunicação rápida e clara
- ✅ **Aprendizado**: Post-mortem estruturado gera aprendizado

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

**Resultado**: Progresso constante, código profissional, zero dívida técnica.

---

### 1️⃣3️⃣.5️⃣ **Sprint Retrospectives** (Opcional - Para Melhoria Contínua)

**Quando Aplicar**:
- ✅ Projetos de longo prazo (>3 meses)
- ✅ Trabalho em equipe (2+ pessoas)
- ✅ Ciclos iterativos (sprints, milestones)
- ✅ Quando quer melhorar processo continuamente
- ✅ Após conclusão de épico/milestone importante

**Não Aplicar Se**:
- ❌ Projeto solo ad-hoc (sem repetição)
- ❌ One-off script ou protótipo
- ❌ Projeto com prazo único (não-iterativo)
- ❌ Sem commitment de melhoria (retrospective só vale se gerar ações)

**O que é Sprint Retrospective?**

Reunião (ou documento, se solo) ao final de cada sprint/milestone para refletir sobre:
- ✅ **O que funcionou bem** (keep doing)
- ❌ **O que não funcionou** (stop doing)
- 💡 **O que podemos melhorar** (start doing)
- 📊 **Métricas de progresso**

**Template de Retrospective**:

```markdown
# Sprint Retrospective #5 - Clarify Project

**Data**: 2024-01-20  
**Sprint**: 2024-01-08 → 2024-01-20 (2 semanas)  
**Participantes**: Josué (dev), Alice (reviewer)  
**Milestone**: v2.0.0 - SQLite Migration  

---

## 📊 Métricas do Sprint

### Progresso
- **Tasks Completadas**: 8/10 (80%)
- **Story Points**: 21/25 (84%)
- **Bugs Encontrados**: 3
- **Bugs Corrigidos**: 3
- **Commits**: 24
- **PRs**: 6 (5 merged, 1 pendente)

### Qualidade
- **Cobertura de Testes**: 87% (↑ 5% desde sprint anterior)
- **Code Review**: 100% (todos PRs revisados)
- **CI/CD**: 23/24 builds sucesso (95.8%)
- **Tempo Médio PR → Merge**: 18h (meta: <24h) ✅

### Velocity
- **Velocity Planejada**: 25 SP
- **Velocity Real**: 21 SP
- **Eficiência**: 84% (meta: >80%) ✅

---

## ✅ O Que Funcionou Bem (Keep Doing)

### 1. Protocolo Simplicidade
**Impacto**: ALTO  
**O que funcionou**: Seguir 13 etapas garantiu qualidade consistente.  
**Evidência**: Zero bugs em produção nas tasks que seguiram protocolo completo.  
**Ação**: Continuar usando, considerar tornar obrigatório para todos devs.

### 2. Pre-commit Hooks
**Impacto**: MÉDIO  
**O que funcionou**: Hooks pegaram 15 erros de formatting antes de commit.  
**Evidência**: Zero comentários de code review sobre formatação.  
**Ação**: Manter hooks, adicionar bandit (security) ao config.

### 3. Pair Programming em Features Complexas
**Impacto**: ALTO  
**O que funcionou**: Migração SQLite (Task Example) feita em pair = zero retrabalho.  
**Evidência**: PR aprovado first-time, nenhuma mudança solicitada.  
**Ação**: Usar pair programming para tasks com risco > MÉDIO.

---

## ❌ O Que Não Funcionou (Stop Doing / Fix)

### 1. Testing de GUI Manual Demais
**Impacto**: ALTO  
**Problema**: GUI testada manualmente toda vez = 30min por task, repetitivo.  
**Evidência**: 8 tasks × 30min = 4 horas gastas em testes manuais.  
**Root Cause**: Falta de testes automatizados para GUI.  
**Ação**: 
- [ ] Implementar pytest-qt para testes GUI automatizados (Task Example)
- [ ] Criar smoke test suite que roda em CI (Task Example)
- **Owner**: Josué | **Deadline**: Sprint #6

### 2. Scope Creep em Task Example
**Impacto**: MÉDIO  
**Problema**: Task "Migrar para SQLite" cresceu de 8 SP → 13 SP durante sprint.  
**Evidência**: Task levou 3 dias em vez de 2 dias estimados.  
**Root Cause**: Subestimamos complexidade de migration + rollback plan.  
**Ação**:
- [ ] Adicionar buffer de 25% em estimativas de tasks "primeira vez" (Task Example)
- [ ] Dividir épicos grandes em tasks menores (<5 SP cada)
- **Owner**: Alice | **Deadline**: Próximo planning

### 3. Documentação Atrasada
**Impacto**: BAIXO  
**Problema**: ADRs criados após PR merged, não durante.  
**Evidência**: ADR-004 commitado 2 dias após merge do PR #145.  
**Root Cause**: Esquecemos de incluir ADR no checklist do PR.  
**Ação**:
- [ ] Atualizar PR template para incluir "ADR criado?" (Task Example)
- [ ] Pre-commit hook para checar se docs/adr/ foi modificado quando src/ muda
- **Owner**: Josué | **Deadline**: Sprint #6

---

## 💡 Ideias para Melhorar (Start Doing)

### 1. Weekly Micro-Retrospectives
**Proposta**: Retrospective curta (10min) toda sexta-feira.  
**Rationale**: Retrospective a cada 2 semanas = algumas lições esquecidas.  
**Experimento**: Testar por 4 semanas, avaliar se adiciona valor.  
**Ação**:
- [ ] Criar template micro-retro (3 perguntas apenas)
- [ ] Agendar 10min toda sexta 16h
- **Owner**: Alice | **Status**: Experimental

### 2. Refactoring Fridays
**Proposta**: Última tarde de sprint dedicada a refactoring/tech debt.  
**Rationale**: Tech debt acumulando (TODO comments: 23 → 31 desde último sprint).  
**Experimento**: Dedicar 3h de sexta para limpar tech debt.  
**Ação**:
- [ ] Criar tag `tech-debt` no issue tracker
- [ ] Reservar 3h de sexta para tech debt sprint #6
- **Owner**: Josué | **Status**: Experimental

### 3. Automated Changelog Generation
**Proposta**: Gerar CHANGELOG.md automaticamente de commits.  
**Rationale**: Escrever changelog manualmente = 20min repetitivos por sprint.  
**Solução**: Usar `git-cliff` ou `conventional-changelog`.  
**Ação**:
- [ ] Avaliar ferramentas (git-cliff vs conventional-changelog)
- [ ] Integrar no CI pipeline
- **Owner**: Alice | **Deadline**: Sprint #7

---

## 📈 Comparação com Sprints Anteriores

| Métrica | Sprint #3 | Sprint #4 | Sprint #5 | Trend |
|---------|-----------|-----------|-----------|-------|
| Velocity | 18 SP | 22 SP | 21 SP | ↔️ Estável |
| Cobertura | 78% | 82% | 87% | ↗️ Melhorando |
| Bugs Produção | 2 | 1 | 0 | ↗️ Excelente |
| Time PR→Merge | 36h | 24h | 18h | ↗️ Melhorando |
| Tech Debt Items | 18 | 23 | 31 | ↘️ **ALERTA** |

**Análise**:
- ✅ Qualidade melhorando (cobertura ↑, bugs ↓)
- ✅ Eficiência melhorando (PRs mais rápidos)
- ⚠️ **Tech debt acumulando** - precisa atenção (Refactoring Fridays)

---

## 🎯 Action Items para Próximo Sprint

| # | Action | Owner | Deadline | Priority |
|---|--------|-------|----------|----------|
| #89 | Implementar pytest-qt para GUI | Josué | Sprint #6 | 🔴 ALTA |
| #90 | Criar smoke test suite CI | Josué | Sprint #6 | 🔴 ALTA |
| #91 | Adicionar 25% buffer em estimativas | Alice | Planning #6 | 🟡 MÉDIA |
| #92 | Atualizar PR template (ADR) | Josué | Sprint #6 | 🟢 BAIXA |
| - | Testar weekly micro-retros | Alice | Sprint #6 | 🧪 Experimental |
| - | Dedicar 3h sexta tech debt | Josué | Sprint #6 | 🧪 Experimental |

**Tracked in**: [GitHub Project - Sprint #6](link)

---

## 💬 Team Feedback

### Josué
> "Protocolo Simplicidade está funcionando muito bem. Sinto que qualidade está melhor. Preocupado com tech debt acumulando - vamos tentar Refactoring Fridays."

### Alice
> "Code reviews estão mais rápidos e suaves. Adorei pair programming na migração SQLite. Sugestão: podemos fazer retrospectives mais frequentes? A cada 2 semanas parece muito tempo."

---

## 📚 Lessons Learned

### Técnicas
1. **SQLite Migrations**: Sempre criar backup automático + rollback plan.
2. **Feature Flags**: Melhor que rollback completo para features grandes.
3. **GUI Testing**: Pytest-qt economiza tempo significativo vs manual.

### Processo
1. **Retrospectives**: 2 semanas = bom, mas micro-retros semanais podem adicionar valor.
2. **Estimativas**: Primeira vez fazendo algo = adicionar buffer 25%.
3. **Tech Debt**: Precisa tempo dedicado, não "quando sobrar tempo".

### Pessoal
1. **Pair Programming**: Vale a pena para tasks complexas/críticas.
2. **Comunicação**: PRs com contexto rico = reviews mais rápidas.
3. **Documentação**: ADRs devem ser criados DURANTE PR, não depois.

---

**Próxima Retrospective**: 2024-02-03 (Sprint #6)  
**Format**: Presencial ou documento atualizado  
**Facilitador**: Alice (rotativo)
```

**Retrospective Solo (Projeto Individual)**:

```markdown
# Personal Retrospective - Week 3

**Período**: 2024-01-15 → 2024-01-21  
**Projeto**: Clarify - Task Management  

## 📊 Esta Semana

### Completei
- ✅ Task Example: Migração SQLite (13 SP)
- ✅ Task Example: Rollback plan (3 SP)
- ✅ Task Example: ADR documentation (2 SP)

**Total**: 18 SP (meta: 20 SP) - 90% 👍

### Não Completei
- ❌ Task Example: GUI performance otimization (5 SP)
  - **Por quê**: Subestimei complexidade, precisa mais pesquisa

## 💭 Reflexão

### O que funcionou
1. **Focar manhã em Deep Work** - Melhores 4h do dia sem interrupções
2. **Pomodoro 25/5** - Manteve foco, completei mais tasks
3. **Daily notes** - 5min todo dia planejando ajudou muito

### O que não funcionou
1. **Tarde com reuniões** - Zero código após 15h, muito context switch
2. **Não usei Protocolo Simplicidade completo** - Pulei testes em Task Example (ADR) e depois tive que voltar corrigir
3. **Procrastinei performance optimization** - Tarefa difícil, fiquei adiando

### O que vou tentar
1. **Time-blocking** - Bloquear 9-13h para deep work no calendário
2. **Eat the Frog** - Tarefa mais difícil PRIMEIRO (manhã)
3. **Protocolo SEMPRE** - Não pular etapas, mesmo em docs

## 📈 Métricas Pessoais

- **Horas codando**: 28h (↑ 3h vs semana passada)
- **Commits**: 18
- **Distrações**: 12 (↓ 5 vs semana passada) 🎉
- **Energia fim do dia**: 6/10 (meta: 7/10)

## 🎯 Próxima Semana

**Focos**:
1. Completar Task Example (performance) - PRIMEIRA coisa segunda-feira
2. Seguir protocolo 100% - sem pular etapas
3. Manter time-blocking 9-13h deep work

**Meta**: 20 SP + melhorar energia fim do dia para 7/10
```

**Por quê Retrospectives são valiosas**:
- ✅ **Melhoria Contínua**: Identificar e corrigir problemas recorrentes
- ✅ **Aprendizado**: Time aprende com experiências (sucessos e falhas)
- ✅ **Transparência**: Todos entendem o que está funcionando/não
- ✅ **Ownership**: Action items criam accountability
- ✅ **Moral**: Celebrar vitórias, reconhecer progresso

---

## 🎯 Mensagem Final

> "Quero um trabalho completo e profissional!"

**Este protocolo garante**:
- ✅ Qualidade profissional (13 etapas obrigatórias + 10 opcionais avançadas)
- ✅ Progresso incremental (do simples ao complexo)
- ✅ Documentação completa (nunca esquecer o que foi feito)
- ✅ Código testado e seguro (100% confiável)
- ✅ Integração verificada (GUI + CLI funcionais)
- ✅ Commits organizados (histórico limpo)
- ✅ **[NOVO v2.0]** Práticas enterprise (Security, CI/CD, ADRs, Retrospectives)

**Releia este documento antes de cada sprint!**

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

**Releia este documento antes de cada sprint!**

---

**Versão**: 2.3  
**Última atualização**: 16 de Dezembro de 2025  
**Mantido por**: Josué Amaral  
**Status**: ATIVO - Protocolo avançado para projetos críticos/enterprise
