# 📊 Sistema de Barras de Progresso (v2.5.0)

## Visão Geral

O sistema de barras de progresso fornece feedback visual em tempo real para todas as operações de processamento no Clarify. Cada operação (busca, substituição, inserção) executa em uma thread separada e exibe seu progresso na parte inferior da janela principal.

## Características Principais

### 1. **Execução Não-Bloqueante**
- Todas as operações executam em threads separadas da interface gráfica
- A GUI permanece responsiva durante processamentos longos
- Múltiplas operações podem executar simultaneamente

### 2. **Barras de Progresso Individuais**
- Cada operação tem sua própria barra de progresso
- Mostra progresso em tempo real (arquivo atual, porcentagem)
- Pode ser expandida para ver detalhes completos

### 3. **Gerenciamento Inteligente**
- Barras aparecem automaticamente ao iniciar processamento
- Área de progresso se esconde quando não há tarefas ativas
- Scroll automático para gerenciar múltiplas barras

### 4. **Janela de Detalhes Expandida**
- Clique no botão "↗" para expandir detalhes
- Mostra log completo de processamento
- Permite cancelar operação em andamento
- Pode ser minimizada de volta à barra compacta

## Interface do Usuário

### Localização

As barras de progresso aparecem na **parte inferior da janela principal**, abaixo das abas principais (Search/Replace e Insert).

```
┌─────────────────────────────────────────┐
│  [Search/Replace] [Insert]              │  ← Abas principais
│                                          │
│  [Conteúdo do painel ativo]             │
│                                          │
├─────────────────────────────────────────┤
│  Active Tasks (2)                    [▼]│  ← Cabeçalho (colapsável)
│  ┌─────────────────────────────────┐   │
│  │ Search: pattern  [↗] [✖]        │   │  ← Barra 1
│  │ ████████░░░░░░░░░░ 45%          │   │
│  │ Processing: file50.py           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ Insert: text     [↗] [✖]        │   │  ← Barra 2
│  │ ████████████████░░ 80%          │   │
│  │ Processing: file80.py           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Componentes da Barra de Progresso

Cada barra contém:

1. **Nome da Tarefa**: Identificação da operação (ex: "Search: pattern")
2. **Botão Expandir (↗)**: Abre janela com detalhes completos
3. **Botão Fechar (✖)**: Remove a barra da interface
4. **Barra de Progresso**: Indicador visual de percentual completo
5. **Status**: Mensagem do arquivo/ação atual sendo processado

### Janela de Detalhes Expandida

Ao clicar no botão "↗", uma janela modal se abre mostrando:

```
┌────────────────────────────────────────────┐
│  Progress Details - Search: pattern        │
├────────────────────────────────────────────┤
│  Search: pattern                           │
│  ████████████████████ 75%                  │
│  Progress: 75/100 (75.0%) - file75.py     │
│                                            │
│  Processing Details:                       │
│  ┌────────────────────────────────────────┐│
│  │ [10:30:15] Processing: file1.py        ││
│  │ [10:30:16] Processing: file2.py        ││
│  │ [10:30:17] Processing: file3.py        ││
│  │ ...                                    ││
│  │ [10:30:45] Processing: file75.py       ││
│  └────────────────────────────────────────┘│
│                                            │
│  [↓ Minimize to Bar]  [✖ Cancel Task]     │
└────────────────────────────────────────────┘
```

Funcionalidades:
- **Barra de progresso maior**: Mais fácil de visualizar
- **Log detalhado**: Histórico completo com timestamps
- **Botão Minimizar**: Volta para barra compacta
- **Botão Cancelar**: Interrompe a operação

## Funcionalidades

### Auto-Hide

O sistema se esconde automaticamente quando não há tarefas:

- **Sem tarefas ativas**: Área de progresso completamente oculta
- **Primeira tarefa iniciada**: Área aparece automaticamente
- **Última tarefa concluída/fechada**: Área se esconde novamente

### Scroll para Múltiplas Barras

Quando há muitas operações simultâneas:

- Scroll vertical automático na área de barras
- Máximo de ~3-4 barras visíveis simultaneamente
- Scroll para ver todas as barras ativas

### Colapsar/Expandir Área

Clique no botão **[▼]** no cabeçalho para:

- **▼**: Mostrar todas as barras de progresso
- **▲**: Ocultar barras mas manter cabeçalho visível

Útil quando você quer recuperar espaço na tela mas continuar monitorando o número de tarefas ativas.

### Cancelamento de Operações

Duas formas de cancelar:

1. **Botão Cancelar na Janela de Detalhes**: Interrompe processamento imediatamente
2. **Thread continua até checkpoint**: Worker verifica flag de cancelamento entre arquivos

**Nota**: Cancelamento é seguro - não corrompe dados, apenas para de processar novos arquivos.

### Fechar Barras Manualmente

Clique no botão **[✖]** para remover uma barra da interface:

- Pode fechar barras completas para limpar interface
- Pode fechar barras de operações longas que não deseja mais monitorar
- Fechar não cancela a operação (só remove visualização)

## Integração com Operações

### Search Panel

Quando você clica em "Search":

1. Thread de busca inicia
2. Barra de progresso aparece: `"Search: <seu padrão>"`
3. Progresso atualiza a cada arquivo processado
4. Ao concluir: Status muda para "✓ Completed"
5. Resultados populam a árvore de matches

### Insert Panel

Quando você clica em "Insert" (com busca de linhas):

1. Thread de busca de matches inicia
2. Barra aparece: `"Match Search: <seu padrão>"`
3. Progresso atualiza durante busca
4. Ao concluir: Inserções são aplicadas
5. Resultados mostram arquivos modificados

### Operações Paralelas

Você pode:

- Iniciar uma busca
- Enquanto busca executa, iniciar uma inserção
- Ambas operações mostram progresso independente
- Threads não interferem entre si
- GUI permanece responsiva

## Arquitetura Técnica

### Classes Principais

#### `ProgressBarWidget`

Widget individual de barra de progresso.

**Responsabilidades**:
- Exibir progresso atual (barra + porcentagem)
- Mostrar status/mensagem atual
- Fornecer botões de expandir/fechar
- Emitir sinais quando usuário interage

**Sinais**:
- `expand_requested(task_id)`: Usuário quer ver detalhes
- `close_requested(task_id)`: Usuário quer fechar barra
- `cancel_requested(task_id)`: Usuário quer cancelar tarefa

#### `ProgressDetailsDialog`

Janela modal com detalhes completos.

**Responsabilidades**:
- Exibir progresso em formato maior
- Manter log de processamento com timestamps
- Permitir minimizar de volta à barra
- Permitir cancelar operação

**Métodos principais**:
- `update_progress(current, total, message)`: Atualiza barra e status
- `add_log(message)`: Adiciona entrada no log

#### `ProgressManager`

Gerenciador central de todas as barras.

**Responsabilidades**:
- Criar e destruir barras de progresso
- Gerenciar visibilidade da área
- Fornecer scroll quando necessário
- Manter contagem de tarefas ativas

**Métodos principais**:
- `add_task(task_id, task_name)`: Cria nova barra, retorna widget
- `remove_task(task_id)`: Remove barra do sistema
- `get_task_widget(task_id)`: Obtém referência ao widget

### Workers (Threads)

#### `SearchWorker`

Executado em thread separada para buscas.

**Novos Sinais** (v2.5.0):
- `progress_detailed(int, int, str)`: (current, total, message)

**Fluxo**:
1. Coleta lista de arquivos a processar (para saber total)
2. Para cada arquivo:
   - Emite `progress_detailed` com (índice, total, caminho)
   - Processa arquivo
3. Emite `done` com resultados finais

### Integração nos Painéis

#### `SearchReplacePanel` e `InsertPanel`

**Modificações** (v2.5.0):

1. **Construtor**: Aceita `progress_manager` como parâmetro
2. **Ao iniciar busca**:
   - Gera `task_id` único (UUID)
   - Chama `progress_manager.add_task()`
   - Guarda referência ao `ProgressBarWidget` criado
3. **Durante processamento**:
   - Conecta `worker.progress_detailed` ao método de atualização
   - Atualiza barra via `widget.update_progress()`
   - Adiciona logs via `widget.add_log()`
4. **Ao concluir**:
   - Marca barra como completa: `widget.set_complete(success=True)`
   - Não remove automaticamente (usuário fecha manualmente)

**Cancelamento**:
- Conecta `widget.cancel_requested` ao `worker.cancel()`
- Worker verifica flag entre arquivos e para processamento

## Casos de Uso

### 1. Monitorar Busca Longa

**Situação**: Busca em diretório grande (~10.000 arquivos)

**Fluxo**:
1. Iniciar busca
2. Barra aparece mostrando progresso
3. Ver arquivo atual sendo processado
4. Expandir para ver log se desejar
5. Aguardar conclusão
6. Fechar barra quando não precisar mais

### 2. Operações Paralelas

**Situação**: Múltiplas buscas simultâneas em diretórios diferentes

**Fluxo**:
1. Iniciar primeira busca (Barra 1 aparece)
2. Mudar para segundo diretório
3. Iniciar segunda busca (Barra 2 aparece)
4. Ambas executam independentemente
5. Scroll para ver todas as barras

### 3. Cancelar Operação Demorada

**Situação**: Busca está demorando mais que esperado

**Fluxo**:
1. Clicar em "↗" para expandir detalhes
2. Revisar log - ver que muitos arquivos grandes
3. Clicar em "✖ Cancel Task"
4. Operação para após arquivo atual
5. Barra mostra "✖ Failed" (cancelada)

### 4. Limpar Interface

**Situação**: Muitas barras completadas acumuladas

**Fluxo**:
1. Clicar em "✖" em cada barra completa
2. Barras desaparecem
3. Área de progresso se esconde quando última barra é fechada

## Configurações e Limites

### Limites do Sistema

- **Máximo de log**: 1000 linhas por tarefa (evita consumo excessivo de memória)
- **Altura máxima da área**: ~250px (cerca de 3-4 barras visíveis)
- **Truncamento de mensagens**: Caminhos longos são cortados para 60 caracteres

### Performance

- **Overhead mínimo**: Emissão de sinais é muito leve
- **GUI não trava**: Threads separadas garantem responsividade
- **Atualização eficiente**: Uma emissão por arquivo (não por linha)

## Problemas Conhecidos e Soluções

### Problema: Barra não atualiza

**Causa**: Worker não está emitindo `progress_detailed`

**Solução**: Verificar que worker está conectado corretamente:
```python
worker.progress_detailed.connect(self._on_progress_detailed)
```

### Problema: Cancelamento não funciona

**Causa**: Worker não verifica flag `_cancel`

**Solução**: Worker deve verificar flag regularmente:
```python
for item in items:
    if self._cancel:
        break
    # processar item
```

### Problema: Múltiplas barras para mesma operação

**Causa**: `task_id` não é único

**Solução**: Usar UUID para garantir IDs únicos:
```python
import uuid
task_id = f"search_{uuid.uuid4().hex[:8]}"
```

## Versão

Sistema introduzido na versão **2.5.0** do Clarify.

## Arquivos Modificados

- `src/app.py`:
  - Novas classes: `ProgressBarWidget`, `ProgressDetailsDialog`, `ProgressManager`
  - `SearchWorker`: Novo sinal `progress_detailed`
  - `SearchReplacePanel`: Integração com `progress_manager`
  - `InsertPanel`: Integração com `progress_manager`
  - `MainWindow`: Adição do `ProgressManager` na UI

## Testes

Veja `test_progress_system.py` para testes automatizados completos (12 testes cobrindo todas as funcionalidades).

## Funcionalidades Aprimoradas (v2.5.0+)

### 1. **Histórico de Operações (Persistência)**

O sistema agora mantém um histórico persistente de todas as operações executadas.

**Características**:
- Histórico salvo em `~/.clarify_history.json`
- Mantém últimas 1000 operações
- Cada entrada inclui:
  - Timestamp (data e hora)
  - Tipo de operação (search, insert_search)
  - Detalhes (query, caminho, arquivos encontrados, etc.)

**Exemplo de entrada**:
```json
{
  "timestamp": "2024-01-15 10:30:45",
  "type": "search",
  "details": {
    "query": "def process",
    "path": "/home/user/project",
    "files_matched": 12,
    "total_matches": 45
  }
}
```

**Uso futuro**: Histórico pode ser usado para:
- Repetir buscas anteriores
- Análise de padrões de uso
- Auditoria de operações

### 2. **Estimativa de Tempo (ETA)**

Cálculo em tempo real do tempo estimado para conclusão.

**Como funciona**:
1. Sistema rastreia tempo decorrido desde início
2. Calcula velocidade: `arquivos processados / tempo decorrido`
3. Estima tempo restante: `arquivos restantes / velocidade`
4. Formata de forma legível: "2h 15m", "5m 30s", "45s"

**Interface**:
- **Dialog expandido**: Mostra linha de estatísticas
  ```
  Progress: 75/100 (75%) | Elapsed: 2m 30s | Speed: 0.5/s | ETA: 5m
  ```
- **Barra compacta**: Mostra stats inline
  ```
  Processing: file75.py (0.5/s, ETA: 5m)
  ```

**Precisão**:
- Mais precisa após ~10% de progresso
- Ajusta dinamicamente conforme velocidade varia
- Considera apenas tempo de processamento ativo

### 3. **Notificações Desktop**

Notificações automáticas quando operações longas completam.

**Características**:
- Notifica quando tarefa completa (sucesso ou falha)
- Funciona mesmo com janela minimizada
- Suporte multiplataforma:
  - **Linux**: `notify-send` (via libnotify)
  - **macOS**: `osascript` (AppleScript)
  - **Windows**: `plyer` (se instalado)

**Exemplo de notificação**:
```
Título: Task Complete
Mensagem: Search completed: 12 files with matches
```

**Configuração**:
- Notificações são automáticas (não requer configuração)
- Graceful fallback se sistema não suporta
- Falhas silenciosas (não interrompe aplicação)

**Instalação opcional** (para melhor suporte):
```bash
pip install plyer  # Suporte multiplataforma aprimorado
```

### 4. **Pausar/Retomar Operações**

Controle fino sobre execução de operações longas.

**Interface**:
- **Botão Pause (⏸)**: Na barra compacta e no dialog
- **Alternar para Resume (▶)**: Quando pausado
- **Estado visual**: Barra fica amarela quando pausada

**Comportamento**:
1. Clicar em ⏸: Operação pausa após arquivo atual
2. Worker entra em loop de espera (não consome CPU)
3. Progresso permanece visível (não avança)
4. Clicar em ▶: Retoma processamento do próximo arquivo
5. ETA é recalculado após retomar

**Notas técnicas**:
- Pausa é segura (não corrompe dados)
- Pausa ocorre entre arquivos (não no meio)
- Worker dorme 0.1s em loop enquanto pausado
- Estado de pausa persistente até retomar ou cancelar

**Casos de uso**:
- Pausar durante reunião/apresentação
- Reduzir uso de CPU temporariamente
- Revisar resultados parciais antes de continuar

### 5. **Estatísticas de Velocidade**

Métricas em tempo real de performance de processamento.

**Métricas exibidas**:
- **Velocidade**: Arquivos por segundo ou por minuto
  - `> 1/s`: Mostra como "X.X/s"
  - `< 1/s`: Mostra como "X.X/min" (mais legível)
- **Tempo Decorrido**: Formato legível (h/m/s)
- **ETA**: Tempo estimado até conclusão

**Cálculo**:
```python
speed = arquivos_processados / tempo_decorrido
eta = arquivos_restantes / speed
```

**Exemplos de display**:
- `"25.0/s"` → 25 arquivos por segundo (processamento rápido)
- `"30.0/min"` → 0.5 arquivos por segundo (arquivos grandes)
- `"Elapsed: 2m 15s"` → Tempo desde início
- `"ETA: 5m 30s"` → Previsão de conclusão

**Atualização**:
- Stats atualizam a cada arquivo processado
- Velocidade é média desde início (não instantânea)
- ETA ajusta dinamicamente

## Melhorias Futuras

Possíveis melhorias para versões futuras:

1. **Perfis de Busca**: Salvar e carregar configurações de busca favoritas
2. **Gráficos de Performance**: Visualizar velocidade ao longo do tempo
3. **Comparação de Histórico**: Comparar resultados de buscas similares
4. **Exportar Histórico**: Salvar relatórios de operações em PDF/CSV
5. **Priorização de Tarefas**: Sistema de filas com prioridades

## Feedback

Se você tiver sugestões para melhorias no sistema de progresso, entre em contato com os desenvolvedores.
