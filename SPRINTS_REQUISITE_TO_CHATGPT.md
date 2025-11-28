# Sprints - requisite_to_ChatGPT Improvements

## Sprint 1: UX Básico e Interface (Prioridade Alta)
**Objetivo:** Melhorar usabilidade imediata e responsividade da interface

### 1.1 Execução com ENTER
- [ ] Adicionar suporte a `returnPressed` nos campos de entrada principais
- [ ] Conectar `ed_api.returnPressed` → `_save_key()`
- [ ] Conectar `ed_p1.returnPressed` → foco no próximo campo ou executar preview
- [ ] Conectar `ed_p2.returnPressed` → similar ao ed_p1
- [ ] Conectar `ed_ext.returnPressed` → foco no campo de texto
- [ ] Adicionar método `_execute_action()` para acionar submit quando em foco no `ed_text`
- **Arquivos:** `main.py` (método `_build_ui`, adicionar conexões de sinais)
- **Complexidade:** Baixa
- **Tempo estimado:** 2-3 horas

### 1.2 Splitter entre Resultados e Controles
- [ ] Substituir layout vertical por `QSplitter` (orientação vertical)
- [ ] Colocar todos os controles no painel superior do splitter
- [ ] Colocar `self.out` (área de resultados) no painel inferior
- [ ] Configurar proporção inicial (ex: 40% controles, 60% resultados)
- [ ] Permitir redimensionamento arrastável pelo usuário
- [ ] Salvar posição do splitter em preferences
- **Arquivos:** `main.py` (método `_build_ui`, `_load_prefs`, `_save_prefs`)
- **Complexidade:** Baixa-Média
- **Tempo estimado:** 2-4 horas

---

## Sprint 2: Filtros Avançados (Prioridade Alta)
**Objetivo:** Implementar filtragem de escopo com marcadores start/end mais robusta

### 2.1 Feature: Filtro de Escopo com Start/End Markers
✅ **JÁ IMPLEMENTADO PARCIALMENTE** - Melhorar implementação existente:

- [ ] **Validar regex antes de processar** - adicionar try/except em `_extract_between_markers`
- [ ] **Adicionar preview do escopo filtrado** - novo botão "Preview Scope" ao lado dos campos
- [ ] **Melhorar feedback visual** - destacar texto extraído vs texto filtrado
- [ ] **Adicionar contadores** - mostrar "X segmentos encontrados" quando `scope_match_all=True`
- [ ] **Modo de teste** - permitir testar regex sem processar arquivo completo
- [ ] **Preset de marcadores comuns:**
  - HTML tags: `<div>` ... `</div>`
  - JSON objects: `{` ... `}`
  - Python functions: `def ` ... `\n(?=\S)` (regex)
  - Code blocks: ` `````` ` ... ` `````` `
- **Arquivos:** `main.py` (método `_build_ui`, `_extract_between_markers`, novo `_preview_scope`)
- **Complexidade:** Média
- **Tempo estimado:** 4-6 horas

---

## Sprint 3: Múltiplos Paths (Prioridade Média)
**Objetivo:** Permitir adicionar múltiplos arquivos/diretórios simultaneamente (Path 1, 2, 3, N...)

### 3.1 Arquitetura de Múltiplos Paths
- [ ] **Criar classe `PathEntry`:**
  ```python
  class PathEntry:
      def __init__(self):
          self.ed_path = QLineEdit()
          self.btn_browse = QPushButton("Browse")
          self.btn_preview = QPushButton("Preview")
          self.chk_is_file = QCheckBox("Is File?")
          self.btn_remove = QPushButton("🗑️")  # Remove esta entrada
  ```

- [ ] **Criar `PathsManager`:**
  - Lista dinâmica de `PathEntry`
  - Botão "Add Path +" para adicionar novas entradas
  - Scroll area para múltiplas entradas
  - Validação de duplicatas

### 3.2 Modificar Worker para ZIP de Múltiplos Paths
- [ ] Alterar `SubmissionWorker.__init__` para aceitar `List[Tuple[str, bool]]` ao invés de path1/path2
- [ ] Implementar lógica de ZIP:
  ```python
  # Exemplo: paths = [("dir1/", False), ("file.txt", True), ("dir2/", False)]
  # Resultado: iterar todos os arquivos de dir1, dir2 e file.txt em paralelo
  ```
- [ ] Usar `itertools.zip_longest` para lidar com listas de tamanhos diferentes
- [ ] Adicionar campo "filler" opcional (o que enviar quando uma lista acaba antes da outra)

### 3.3 UI e Persistência
- [ ] Salvar/carregar lista de paths em preferences
- [ ] Adicionar tooltips explicando comportamento do ZIP
- [ ] Preview mostrando "Path 1: file1.txt, Path 2: file2.py, Path 3: file3.json"
- **Arquivos:** `main.py` (nova classe `PathEntry`, modificar `_build_ui`, `SubmissionWorker`, `_load_prefs`, `_save_prefs`)
- **Complexidade:** Alta
- **Tempo estimado:** 8-12 horas

---

## Sprint 4: Suporte a Múltiplas APIs AI (Prioridade Média-Alta)
**Objetivo:** Adicionar Claude Sonnet, Perplexity e listar todos os modelos disponíveis

### 4.1 Adicionar Claude (Anthropic)
- [ ] Instalar SDK: `pip install anthropic`
- [ ] Criar classe `ClaudeClient` (similar a `GeminiClient`):
  ```python
  class ClaudeClient:
      def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
          import anthropic
          self.client = anthropic.Anthropic(api_key=api_key)
          self.model = model
      
      def chat(self, system_prompt: str, user_prompt: str) -> str:
          response = self.client.messages.create(
              model=self.model,
              max_tokens=4096,
              system=system_prompt,
              messages=[{"role": "user", "content": user_prompt}]
          )
          return response.content[0].text
  ```
- [ ] Adicionar modelos ao `DEFAULT_MODELS_AVAILABLE`:
  ```python
  'CLAUDE': [
      {'name': 'claude-sonnet-4-20250514', 'label': 'Claude Sonnet 4'},
      {'name': 'claude-3-5-sonnet-20241022', 'label': 'Claude 3.5 Sonnet'},
      {'name': 'claude-3-opus-20240229', 'label': 'Claude 3 Opus'},
  ]
  ```
- [ ] Adicionar menu provider "Claude (Anthropic)"
- [ ] Implementar `_estimate_cost` para Claude (preços reais da API)

### 4.2 Adicionar Perplexity
- [ ] Perplexity usa OpenAI-compatible API:
  ```python
  class PerplexityClient:
      def __init__(self, api_key: str, model: str = "llama-3.1-sonar-large-128k-online"):
          from openai import OpenAI
          self.client = OpenAI(
              api_key=api_key,
              base_url="https://api.perplexity.ai"
          )
          self.model = model
  ```
- [ ] Adicionar modelos ao `DEFAULT_MODELS_AVAILABLE`:
  ```python
  'PERPLEXITY': [
      {'name': 'llama-3.1-sonar-large-128k-online', 'label': 'Sonar Large (Online)'},
      {'name': 'llama-3.1-sonar-small-128k-online', 'label': 'Sonar Small (Online)'},
      {'name': 'llama-3.1-sonar-large-128k-chat', 'label': 'Sonar Large (Chat)'},
  ]
  ```

### 4.3 Listar TODOS os Modelos Dinamicamente
- [ ] **OpenAI:** Usar `client.models.list()` (já implementado parcialmente)
- [ ] **Gemini:** Usar `genai.list_models()` com filtro:
  ```python
  models = [m for m in genai.list_models() 
            if "generateContent" in m.supported_generation_methods]
  ```
- [ ] **Claude:** API não lista modelos - usar lista hardcoded atualizada
- [ ] **Perplexity:** Usar endpoint `/models` ou lista hardcoded

- [ ] **Adicionar botão "Refresh Models"** no menu Model
- [ ] Cachear lista de modelos por 24h (salvar em config)
- [ ] Mostrar data de última atualização no submenu

### 4.4 Ajustar Menu Dinâmico de Providers/Models
- [ ] Reconstruir menu de modelos ao trocar provider
- [ ] Adicionar ícones aos providers (OpenAI 🟢, Gemini 🔵, Claude 🟣, Perplexity 🔶)
- [ ] Ordenar modelos por custo/capacidade

**Arquivos:** `main.py` (novas classes `ClaudeClient`, `PerplexityClient`, modificar `_make_client`, `_build_menu`, `_estimate_cost`)
**Complexidade:** Média-Alta
**Tempo estimado:** 10-15 horas

---

## Sprint 5: Polimento e Otimizações (Prioridade Baixa)
**Objetivo:** Refinar experiência do usuário e performance

### 5.1 Melhorias de Performance
- [ ] Implementar cache de resultados (evitar re-processar mesmo arquivo)
- [ ] Adicionar barra de progresso real (% de arquivos processados)
- [ ] Streaming de respostas (mostrar tokens conforme chegam) - API Stream
- [ ] Processar arquivos em paralelo (ThreadPoolExecutor) quando não há dependência

### 5.2 UX Avançado
- [ ] Dark mode toggle
- [ ] Temas customizáveis (salvar esquema de cores)
- [ ] Histórico de prompts (últimos 10 prompts usados)
- [ ] Templates de prompts salvos (ex: "Code Review", "Translate", "Summarize")
- [ ] Atalhos de teclado:
  - `Ctrl+Enter` → Submit
  - `Ctrl+K` → Clear Output
  - `Ctrl+Shift+C` → Copy Filtered
  - `F5` → Refresh API Status

### 5.3 Validações e Segurança
- [ ] Validar tamanho total de tokens antes de enviar (alertar se > limite do modelo)
- [ ] Sanitizar entrada do usuário (evitar injection em prompts)
- [ ] Confirmar antes de enviar > 100 arquivos
- [ ] Rate limiting visual (mostrar quantos requests/min estão sendo feitos)

**Arquivos:** `main.py` (múltiplos métodos)
**Complexidade:** Variável (Baixa a Média)
**Tempo estimado:** 8-12 horas

---

## Resumo de Prioridades

| Sprint | Funcionalidade | Prioridade | Tempo | Complexidade |
|--------|----------------|------------|-------|--------------|
| 1.1 | Execução com ENTER | 🔴 Alta | 2-3h | Baixa |
| 1.2 | Splitter UI | 🔴 Alta | 2-4h | Baixa-Média |
| 2.1 | Filtro de Escopo (melhorias) | 🔴 Alta | 4-6h | Média |
| 3 | Múltiplos Paths (ZIP) | 🟡 Média | 8-12h | Alta |
| 4.1 | Claude API | 🟡 Média-Alta | 4-6h | Média |
| 4.2 | Perplexity API | 🟡 Média-Alta | 3-4h | Baixa-Média |
| 4.3 | Listar Todos os Modelos | 🟡 Média-Alta | 3-5h | Média |
| 5 | Polimento/Otimizações | 🟢 Baixa | 8-12h | Variável |

**Total estimado:** 34-52 horas de desenvolvimento

---

## Ordem de Execução Recomendada

1. **Sprint 1.1** (ENTER key) - Quick win, melhora UX imediatamente
2. **Sprint 1.2** (Splitter) - Melhora visual da interface
3. **Sprint 2.1** (Filtro de escopo) - Funcionalidade crítica já parcialmente implementada
4. **Sprint 4.1-4.3** (APIs) - Aumenta valor da ferramenta significativamente
5. **Sprint 3** (Múltiplos paths) - Feature complexa mas muito útil
6. **Sprint 5** (Polimento) - Refinamentos finais

---

## Notas de Implementação

### Para Sprint 1.1 (ENTER):
```python
# Em _build_ui(), após criar cada QLineEdit:
self.ed_api.returnPressed.connect(self._save_key)
self.ed_p1.returnPressed.connect(lambda: self.ed_p2.setFocus())
self.ed_p2.returnPressed.connect(lambda: self.ed_ext.setFocus())
self.ed_ext.returnPressed.connect(lambda: self.ed_text.setFocus())
# Para ed_text, usar keyPressEvent override para detectar Ctrl+Enter
```

### Para Sprint 1.2 (Splitter):
```python
# Substituir layout vertical por splitter
splitter = QSplitter(Qt.Vertical)
top_widget = QWidget()
top_layout = QVBoxLayout(top_widget)
# ... adicionar todos os controles ao top_layout
splitter.addWidget(top_widget)
splitter.addWidget(self.out)  # área de resultados
splitter.setStretchFactor(0, 2)  # controles
splitter.setStretchFactor(1, 3)  # resultados
root.addWidget(splitter)
```

### Para Sprint 4.1 (Claude):
```python
# Instalar: pip install anthropic
# Pricing (exemplo, verificar site oficial):
# Claude Sonnet 4: $3/MTok input, $15/MTok output
# Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
# Claude 3 Opus: $15/MTok input, $75/MTok output
```

---

## Dependências Adicionais

```bash
# Sprint 4 - APIs
pip install anthropic  # Claude
# Perplexity usa openai (já instalado)

# Sprint 5 - Otimizações (opcional)
pip install aiohttp  # Para async requests
pip install cachetools  # Para cache de resultados
```

---

## Checklist de Testes por Sprint

### Sprint 1:
- [ ] ENTER funciona em todos os campos de entrada
- [ ] Splitter redimensiona corretamente
- [ ] Posição do splitter é salva/carregada

### Sprint 2:
- [ ] Regex inválido não trava o app
- [ ] Preview de escopo mostra texto correto
- [ ] Marcadores com escape especial funcionam

### Sprint 3:
- [ ] Adicionar/remover paths dinamicamente
- [ ] ZIP funciona com listas de tamanhos diferentes
- [ ] Preferences salvam todos os paths

### Sprint 4:
- [ ] API keys de cada provider são validadas corretamente
- [ ] Custo estimado está correto para cada modelo
- [ ] Troca de provider/model não quebra a UI
- [ ] Refresh de modelos funciona sem travar a UI

### Sprint 5:
- [ ] Cache evita re-processar arquivos idênticos
- [ ] Atalhos de teclado funcionam em todos os contextos
- [ ] Templates de prompts salvam/carregam corretamente
