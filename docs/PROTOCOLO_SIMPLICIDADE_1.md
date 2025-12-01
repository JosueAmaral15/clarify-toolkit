# Protocolo Simplicidade 1

**Autor**: Josué Amaral  
**Data de Criação**: 30 de Novembro de 2025  
**Versão**: 1.3  
**Última Atualização**: 01 de Dezembro de 2025  
**Objetivo**: Metodologia profissional para desenvolvimento incremental de qualidade

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

## 📋 Espinha Dorsal do Protocolo (12 Etapas)

**Resumo Executivo**:
1. 📚 Ler a documentação
2. ✅ Escolher tarefas mais simples
3. ❓ Fazer perguntas até sanar 100% das dúvidas
4. 🔍 Analisar e estudar o projeto
5. 🎯 Fazer sprints das tarefas mais simples
6. 💻 Implementar com arquitetura profissional (GoF + GRASP)
7. 🧪 Fazer testes (100% cobertura)
8. 🔗 **Verificar integração com programa principal**
9. ⌨️ **Verificar implementação CLI**
🔟 📝 Preencher documentação
1️⃣1️⃣ 🧹 Organizar pasta raiz
1️⃣2️⃣ 🚀 Fazer commit e push

### 1️⃣ **Ler a Documentação**
- Consultar `docs/TASKS.md` para entender o contexto do projeto
- Revisar especificações anteriores (`v2.9.X-SPECIFICATIONS.md`)
- Entender dependências e arquitetura existente
- Verificar exemplos em `tests/files/` quando aplicável

**Por quê?**: Evitar retrabalho e garantir coerência com o código existente.

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
[ ] Editor de texto integrado (MUITO COMPLEXO - 50h)
[ ] Busca com IA semântica (COMPLEXO - 20h)
[ ] Tooltip preview em hover (SIMPLES - 30min) ✅ COMEÇAR POR AQUI!
```

---

### 3️⃣ **Fazer Perguntas e Mais Perguntas ao Programador**
- **CRÍTICO**: Nunca assumir ou adivinhar requisitos
- Fazer **todas as perguntas necessárias** até sanar **100% das dúvidas**
- Validar entendimento antes de começar a implementar

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

**Exemplo Real (Task #23)**:
```
❓ "Pegar primeiras N palavras (quantas? 3-5?)?"
✅ Resposta: "Default pode ser 30 caracteres"

❓ "Converter para camelCase removendo acentos?"
✅ Resposta: "Sim, devem ser removidos acentos"

❓ "Conflitos de nomes: como resolver?"
✅ Resposta: "Se tiverem a mesma chave pai, não mexa. Linha menor vence."
```

**Por quê?**: Economiza tempo, evita retrabalho, garante que a solução atende exatamente o que foi pedido.

---

### 4️⃣ **Analisar e Estudar o Projeto**
- **CRÍTICO**: Após sanar todas as dúvidas, **estudar o código antes de implementar**
- Ler documentação relevante (README, docs/, comentários no código)
- Entender arquitetura existente e padrões utilizados
- Verificar dependências e imports necessários
- Identificar funções/classes reutilizáveis

**Checklist de Análise**:
1. **Leitura de Documentação**:
   - `docs/TASKS.md` - Contexto geral do projeto
   - `docs/vX.X.X-SPECIFICATIONS.md` - Especificações de versões anteriores
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

**Exemplo Real (Task #45 - Tutorials)**:
```
✅ Analisado: Outros docks (JsonTranslateDock, JsonRewriterDock)
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
- Manter foco: **uma sprint = uma versão (ex: v2.9.14)**

**Estrutura de Sprint**:
```
Sprint v2.9.14 (Exemplo Task #23):
├── Task #23: Orphaned Keys Update (3h estimado)
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
        if type == "json":
            return JSONProcessor()
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
class TranslationDictionary:
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
class JsonRewriterDock(BaseDock):
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

### 7️⃣ **Fazer Testes**
- **Obrigatório**: Testes unitários para cada função pública
- **Meta**: 100% de cobertura das funcionalidades implementadas
- **Ferramentas**: `unittest` (nativo) ou `pytest`

**Categorias de Testes**:
1. **Happy Path**: Casos normais de uso
2. **Edge Cases**: Valores vazios, None, strings longas
3. **Error Handling**: Exceções esperadas
4. **Integration**: Fluxo completo

**Exemplo Task #23**:
```python
✅ test_extract_from_dict_simple()
✅ test_extract_from_obj_type()
✅ test_simple_substitution_same_value()
✅ test_different_values_no_substitution()
✅ test_apply_substitutions_tsx_file()
✅ test_update_multiple_files()
# ... 12 testes no total (100% passing)
```

---

### 8️⃣ **Verificar Integração com Programa Principal**
- **CRÍTICO**: Antes da documentação, **verificar se os componentes estão integrados ao programa principal**
- Não basta implementar o módulo/dock, ele precisa estar **acessível e funcional** no app
- Verificar menu, imports, inicialização e conexões

**Checklist de Integração GUI**:

1. **Import Correto no app.py**:
   ```python
   # ✅ Verificar se módulo foi importado
   from .gui import (
       CaseConverterDock, PlaceholderReplacerDock, JsonSearchDock,
       TextExtractorDock, AIProcessorDock, JsonTranslateDock,
       JsonRewriterDock, HistoryDock, FileListDock, TutorialsDock,
       EditorDock, TextToJsonDock  # ← NOVO módulo deve estar aqui
   )
   ```

2. **Export no __init__.py do Módulo**:
   ```python
   # src/gui/__init__.py
   from .text_to_json_dock import TextToJsonDock
   
   __all__ = [
       'CaseConverterDock', 'PlaceholderReplacerDock', 'JsonSearchDock',
       'TextExtractorDock', 'AIProcessorDock', 'JsonTranslateDock',
       'JsonRewriterDock', 'HistoryDock', 'FileListDock', 'TutorialsDock',
       'EditorDock', 'TextToJsonDock'  # ← NOVO módulo exportado
   ]
   ```

3. **Menu Item Criado e Conectado**:
   ```python
   # Em _build_menu() ou similar
   m_tools = bar.addMenu(tr("menu.tools"))
   
   # Criar QAction
   self.act_open_text_to_json = QAction(tr("menu.tools.text_to_json"), self)
   
   # Adicionar ao menu
   m_tools.addAction(self.act_open_text_to_json)
   
   # Conectar signal
   self.act_open_text_to_json.triggered.connect(lambda: self.dock_text_to_json.show())
   ```

4. **Dock Inicializado no __init__() ou método de setup**:
   ```python
   # Em __init__() da MainWindow
   def __init__(self):
       super().__init__()
       # ... outros docks ...
       self._open_text_to_json()  # ← Inicializar dock
   
   def _open_text_to_json(self):
       self.dock_text_to_json = TextToJsonDock(self)
       self.dock_text_to_json.open_in_editor_requested.connect(self._load_json_from_converter)
       self.addDockWidget(Qt.RightDockWidgetArea, self.dock_text_to_json)
       self.dock_text_to_json.hide()
   ```

5. **Signals Conectados** (se aplicável):
   ```python
   # Conectar signals customizados
   self.dock_text_to_json.open_in_editor_requested.connect(self._load_json_from_converter)
   
   def _load_json_from_converter(self, json_str: str):
       """Callback para abrir JSON no editor"""
       if not hasattr(self, 'dock_editor'):
           self._open_editor()
       self.dock_editor.load_json_string(json_str)
       self.dock_editor.show()
   ```

6. **Traduções i18n Adicionadas**:
   ```json
   // src/i18n/en.json
   {
     "menu.tools.text_to_json": "Text to JSON Converter"
   }
   
   // src/i18n/pt_BR.json
   {
     "menu.tools.text_to_json": "Conversor de Texto para JSON"
   }
   ```

**Checklist de Teste de Integração**:
- ✅ **Menu acessível**: Verificar se item aparece no menu Tools
- ✅ **Dock abre**: Clicar no menu deve abrir o dock corretamente
- ✅ **Funcionalidade básica**: Testar conversão simples
- ✅ **Signals funcionam**: Testar integração com outros componentes (ex: Open in Editor)
- ✅ **Sem erros no console**: Não deve haver ImportError, AttributeError, etc.
- ✅ **Tradução funcionando**: Menu em PT-BR deve mostrar texto traduzido

**Exemplo Real (Task #49 - Text to JSON Converter)**:
```python
✅ Import: from .gui import TextToJsonDock
✅ Export: __all__ = [..., 'TextToJsonDock']
✅ Menu: self.act_open_text_to_json = QAction(tr("menu.tools.text_to_json"), self)
✅ Init: self._open_text_to_json() chamado em __init__()
✅ Signal: open_in_editor_requested.connect(self._load_json_from_converter)
✅ i18n: EN "Text to JSON Converter", PT-BR "Conversor de Texto para JSON"
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

### 9️⃣ **Verificar Implementação CLI com Passagem de Parâmetros**
- **CRÍTICO**: Verificar se a nova funcionalidade está disponível também via **CLI (Command Line Interface)**
- Não basta implementar GUI, funcionalidades importantes devem ter **interface CLI** para automação
- Verificar subcomandos, argumentos, help text e integração

**Checklist de Implementação CLI**:

1. **Subcomando Criado no Parser**:
   ```python
   # No arquivo principal (ex: __main__.py, app.py, clarify.py)
   def _build_cli_parser():
       parser = argparse.ArgumentParser(description="Clarify - JSON Management System")
       subparsers = parser.add_subparsers(dest='command')
       
       # Subcomandos existentes
       parser_search = subparsers.add_parser('search', help='Search in files')
       parser_replace = subparsers.add_parser('replace', help='Replace text')
       
       # ✅ NOVO subcomando para funcionalidade
       parser_text2json = subparsers.add_parser(
           'text2json',
           help='Convert text to JSON format'
       )
   ```

2. **Argumentos Definidos**:
   ```python
   # Argumentos obrigatórios e opcionais
   parser_text2json.add_argument(
       'input',
       help='Input text file or - for stdin'
   )
   parser_text2json.add_argument(
       '-f', '--format',
       choices=['auto', 'key-value', 'csv', 'yaml', 'ini', 'toml', 'toon'],
       default='auto',
       help='Input format (default: auto-detect)'
   )
   parser_text2json.add_argument(
       '-o', '--output',
       help='Output JSON file (default: stdout)'
   )
   parser_text2json.add_argument(
       '--no-infer-types',
       action='store_true',
       help='Keep all values as strings (disable type inference)'
   )
   parser_text2json.add_argument(
       '--pretty',
       action='store_true',
       help='Pretty-print JSON output with indentation'
   )
   ```

3. **Handler Function Implementada**:
   ```python
   def cli_text2json(args):
       """Handle text2json CLI subcommand."""
       from .text_to_json import convert_text_to_json
       
       # Ler input
       if args.input == '-':
           text = sys.stdin.read()
       else:
           with open(args.input, 'r', encoding='utf-8') as f:
               text = f.read()
       
       # Converter
       result = convert_text_to_json(
           text,
           format_type=args.format,
           infer_types=not args.no_infer_types
       )
       
       # Output
       if args.pretty:
           json_str = json.dumps(result, indent=2, ensure_ascii=False)
       else:
           json_str = json.dumps(result, ensure_ascii=False)
       
       if args.output:
           with open(args.output, 'w', encoding='utf-8') as f:
               f.write(json_str)
           print(f"✓ Converted to {args.output}")
       else:
           print(json_str)
   ```

4. **Dispatcher/Router Atualizado**:
   ```python
   def main():
       parser = _build_cli_parser()
       args = parser.parse_args()
       
       # Router para handlers
       if args.command == 'search':
           cli_search(args)
       elif args.command == 'replace':
           cli_replace(args)
       elif args.command == 'text2json':  # ← NOVO
           cli_text2json(args)
       else:
           # GUI mode
           run_gui()
   ```

5. **Help Text Documentado**:
   ```python
   parser_text2json = subparsers.add_parser(
       'text2json',
       help='Convert structured text to JSON',
       description='''
       Convert various text formats to JSON:
       - Key-Value pairs (name: value)
       - CSV (comma-separated values)
       - YAML-like format
       - INI files
       - TOML files
       - TOON (Token-Oriented Object Notation)
       - Auto-detect format
       
       Examples:
         clarify text2json data.csv --format csv --pretty
         clarify text2json config.ini -o output.json
         echo "name: John\\nage: 30" | clarify text2json -
       '''
   )
   ```

**Checklist de Validação CLI**:
- ✅ **Subcomando existe**: `python -m clarify text2json --help` mostra ajuda
- ✅ **Argumentos funcionam**: Flags obrigatórios e opcionais aceitos
- ✅ **Help text completo**: Descrição, exemplos, opções documentadas
- ✅ **Stdin/stdout suportado**: Aceita `-` para pipe/redirect
- ✅ **Error handling**: Trata erros com mensagens claras (não traceback)
- ✅ **Exit codes**: 0 para sucesso, 1 para erro
- ✅ **Performance**: Funciona com arquivos grandes (>100MB)

**Exemplos de Uso CLI** (devem funcionar):
```bash
# Converter CSV para JSON
clarify text2json data.csv --format csv --pretty -o output.json

# Usar stdin (pipe)
cat config.ini | clarify text2json - --format ini

# Auto-detect formato
clarify text2json input.txt --pretty

# Converter YAML com type inference
clarify text2json config.yaml --format yaml -o config.json

# Converter sem inferência de tipos
clarify text2json data.txt --no-infer-types
```

**Exemplo Real (Funcionalidades Existentes)**:
```bash
# ✅ CLI search (já implementado)
clarify search ./src --query "foo" --include "*.py"

# ✅ CLI replace (já implementado)
clarify replace ./src --query "foo" --replacement "bar" --all

# ✅ CLI dedupe (já implementado)
clarify dedupe en.ts --from-ts --join-keys -o en2.ts

# ❓ CLI text2json (NOVO - precisa implementar?)
clarify text2json data.csv --format csv --pretty -o output.json
```

**Quando NÃO Implementar CLI**:
- ❌ Funcionalidades puramente visuais (syntax highlighting, color picker)
- ❌ Docks de navegação/exploração (tutorials, file list)
- ❌ Features interativas que requerem feedback em tempo real
- ❌ Funcionalidades GUI-only explicitamente (preferences dialog)

**Quando IMPLEMENTAR CLI**:
- ✅ Conversões de formato (text → JSON, case converter)
- ✅ Processamento de arquivos (replace, translate, dedupe)
- ✅ Extração/busca (search, extract keys, JSON query)
- ✅ Validação (JSON validator, syntax check)
- ✅ Batch operations (processar múltiplos arquivos)

**Perguntas para Validar CLI**:
1. ❓ "A funcionalidade é útil para automação/scripts?"
2. ❓ "Pode processar arquivos em batch?"
3. ❓ "Seria útil em CI/CD pipelines?"
4. ❓ "Pode ser usada sem interface gráfica?"
5. ❓ "Se SIM para qualquer pergunta acima → Implementar CLI"

**Por quê?**: 
- Permitir **automação** de tarefas repetitivas
- Integração com **scripts** e **pipelines CI/CD**
- Uso em **servidores sem GUI** (headless environments)
- **Power users** preferem CLI para velocidade
- Torna a ferramenta mais **profissional e versátil**

---

### 🔟 **Preencher Nova Documentação**
- **Atualizar arquivo de tarefas/requisitos**: Marcar tasks como `[X]` completas
- **Criar vX.X.X-SPECIFICATIONS.md**: Documento detalhado da versão
- **Atualizar estatísticas**: Percentual de conclusão do projeto

**📋 Marcação de Tarefas em Arquivo de Requisitos**:

**Regra Geral**:
- Se existe arquivo de tarefas/requisitos (ex: `TASKS.md`, `TODO.md`, `requirements.md`):
  - ✅ **Marcar tasks como completas** após implementação: `[ ]` → `[X]`
  - ✅ **Atualizar estatísticas** (percentuais, contadores)
  - ✅ **Adicionar notas de conclusão** (data, versão, descrição breve)
  
- Se **NÃO existe** arquivo de tarefas/requisitos:
  - ❓ **Perguntar ao usuário** qual o local/path do arquivo
  - ❓ **Perguntar sobre próximas tarefas e requisitos** caso não haja documento formal
  - ❓ **Sugerir criação** de arquivo de controle de tarefas

**Exemplo de Marcação (TASKS.md)**:
```markdown
## 🟢 COULD HAVE (Prioridade Baixa)

### ✅ Tasks Concluídas

#### Task #46 - Editor de Arquivos Integrado (v2.9.16)
**Status**: ✅ Completa - 30/11/2025

**Objetivo**: Implementar editor de texto integrado com diferenciação de escopo por cores.

**Implementação**:
1. ✅ EditorDock com QTextEdit e syntax highlighting
2. ✅ Diferenciação de escopo por cores (HTML tags, JSON keys, etc.)
3. ✅ Abrir/salvar arquivos (.txt, .json, .html, .tsx, .py)
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

### 9️⃣ **Organizar Pasta Raiz do Projeto**
- **CRÍTICO**: Antes do commit e push, **organizar a pasta raiz**
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

2. **Verificação de Estrutura de Diretórios**:
   ```
   ✅ src/ - Código-fonte organizado por módulos
   ✅ tests/ - Testes unitários espelhando src/
   ✅ docs/ - Documentação atualizada
   ✅ archive/ - Versões antigas (se necessário)
   ❌ Raiz - Não deixar arquivos soltos (test.py, temp.txt, etc.)
   ```

3. **Validação de .gitignore**:
   ```gitignore
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   
   # Backups
   *.backup*
   *.bak
   *~
   
   # IDE
   .vscode/
   .idea/
   
   # Temporários
   tmp/
   temp/
   *.tmp
   ```

4. **Git Status Clean**:
   ```bash
   git status
   # Verificar se apenas arquivos relevantes estão staged
   # Não commitar: __pycache__, .pyc, backups, temporários
   ```

**Exemplo Real (v2.9.15)**:
```bash
# ANTES (pasta bagunçada):
├── src/
├── apply_v2913_patches.py  ❌ temporário
├── test_temp.py           ❌ teste descartável
├── backup_old/            ❌ backup antigo
├── __pycache__/           ❌ cache
└── file.py.backup_v2913   ❌ backup desnecessário

# DEPOIS (organizado):
├── src/          ✅
├── tests/        ✅
├── docs/         ✅
└── README.md     ✅
```

**Por quê?**: Manter repositório limpo, evitar commits de lixo, facilitar navegação, profissionalismo.

---

### 1️⃣2️⃣ **Fazer Commit e Push**
- **Formato**: Conventional Commits (feat/fix/docs/refactor/test)
- **Mensagem**: Descritiva, completa, com contexto
- **Frequência**: 1 commit por task ou grupo lógico de mudanças

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
- [docs/TASKS.md] (estatísticas atualizadas)

<ESTATÍSTICAS ATUALIZADAS>:
- [CATEGORIA]: X → Y completas (A% → B%)
- TOTAL: X → Y completas (A% → B%)

<EXEMPLO DE USO>: (se aplicável)
  [Demonstração prática]

Refs: [documentação relacionada]
Closes: Task #X (vX.X.X)
```

**Exemplo Real** (Task #23):
```bash
git add src/ tests/ docs/TASKS.md
git commit -m "feat: completar Task #23 - Orphaned Keys Update System (v2.9.14)

PROBLEMA ORIGINAL:
- Implementação v2.9.10 usava string_similarity() (ERRADO)
- Não detectava valores duplicados, apenas similaridade de nomes
...

✅ SOLUÇÃO IMPLEMENTADA:
✅ extract_all_keys_from_obj()
   - Suporta tipo Obj E dict
   - Retorna Dict[str, str] (path → value)
...

Closes: Task #23 (v2.9.14)"

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
| 7 | **Documentação** | TASKS.md + vX.X.X-SPECIFICATIONS.md | Atualizado e completo |
| 8 | **Código Limpo** | PEP8, nomes semânticos, DRY | Funções < 50 linhas |

---

## 📊 Aplicação Prática: Task #23 (Exemplo Completo)

### Situação Inicial
```markdown
Tasks pendentes na categoria SHOULD HAVE:
[ ] Editor de texto integrado (MUITO COMPLEXO)
[ ] Busca com IA semântica (MUITO COMPLEXO)
[⚠️] Orphaned Keys Update (PARCIAL - mais simples!) ✅ ESCOLHIDA
[ ] Google Translate API integration (COMPLEXO)
```

### Sprint Planejada
```
v2.9.14: Completar Task #23
Estimativa: 3-4 horas
Complexidade: MÉDIA (mais simples que as outras)
```

### Execução (Protocolo Simplicidade 1)

**1. Ler Documentação** ✅
- Lido: `docs/TASK_23_ORPHANED_KEYS_SPECIFICATION.md` (662 linhas)
- Entendido: problema de string similarity vs. value equality

**2. Escolher Tarefa Simples** ✅
- Task #23 é **mais simples** que editor de texto ou IA
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
- docs/TASKS.md (Task #23 marcada [X])
- docs/TASK_23_ORPHANED_KEYS_SPECIFICATION.md (já existia)
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
✅ **Task #23 100% completa**  
✅ **Protocolo Simplicidade 1: 10/10 etapas cumpridas** (v1.1 - 10 etapas)  
✅ **Tempo real: ~3h (dentro da estimativa)**  
✅ **Zero bugs detectados**  
✅ **Documentação profissional**

**Nota**: Este exemplo usa v1.1 do protocolo (10 etapas). A v1.2 adiciona mais 2 etapas (integração GUI e CLI).

---

## 🎓 Lições Aprendidas

### ✅ O Que Funciona
1. **Escolher o mais simples**: Task #23 era mais fácil que editor de texto
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
   - ✅ `git commit -m "feat: Task #23 com VALUE EQUALITY (60 linhas)"`

---

## 📚 Referências

- **TASKS.md**: Lista completa de tarefas do projeto
- **v2.9.10-ANTES-DEPOIS.md**: Primeiro exemplo do protocolo
- **v2.9.11-SPECIFICATIONS.md**: Sprint com 3 tasks simples
- **v2.9.12-SPECIFICATIONS.md**: Iterações rápidas
- **v2.9.13-SPECIFICATIONS.md**: 4 melhorias de UX
- **TASK_23_ORPHANED_KEYS_SPECIFICATION.md**: Exemplo de documentação detalhada

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
│  7. Testar (100% coverage)                   │
│  8. Documentar (TASKS + vX.X.X-SPECS)        │
│  9. Organizar Pasta Raiz                     │
│  10. Verificar Integração GUI                │
│  11. Verificar Implementação CLI             │
│  12. Commit + Push (conventional)            │
└──────────────────────────────────────────────┘
           ↓
    ┌──────────────┐
    │   REPETIR    │ ← Sempre há tarefas mais simples!
    └──────────────┘
```

**Resultado**: Progresso constante, código profissional, zero dívida técnica.

---

## 🎯 Mensagem Final

> "Quero um trabalho completo e profissional!"

**Este protocolo garante**:
- ✅ Qualidade profissional (12 etapas obrigatórias)
- ✅ Progresso incremental (do simples ao complexo)
- ✅ Documentação completa (nunca esquecer o que foi feito)
- ✅ Código testado (100% confiável)
- ✅ Integração verificada (GUI + CLI funcionais)
- ✅ Commits organizados (histórico limpo)

**Releia este documento antes de cada sprint!**

---

**Versão**: 1.3  
**Última atualização**: 01 de Dezembro de 2025  
**Mantido por**: Josué Amaral  
**Status**: ATIVO - Protocolo oficial do projeto Clarify
