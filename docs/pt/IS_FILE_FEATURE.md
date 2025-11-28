# Funcionalidade "Is File" (Implementada)

## Visão Geral

A funcionalidade "Is File" é um checkbox presente em todos os painéis principais do Clarify que permite ao usuário especificar se deseja trabalhar com um **arquivo individual** ou um **diretório completo**.

## Localização

O checkbox "Is File?" está disponível nos seguintes painéis:

### 1. Search/Replace Panel
- **Localização**: Logo abaixo do campo "Path"
- **Linha no código**: 1814 (`src/app.py`)
- **Label**: "Is File?"

### 2. Insert Panel
- **Localização**: Logo abaixo do campo "Path"
- **Linha no código**: 2221 (`src/app.py`)
- **Label**: "Is File?"

### 3. JSON Translate Dock
- **Localização**: Logo abaixo do campo "Root path"
- **Linha no código**: 3273 (`src/app.py`)
- **Label**: "Is file?"

## Funcionalidade

### Quando Desmarcado (Padrão - Modo Diretório)
- O botão "Browse" abre um diálogo para selecionar **diretórios**
- A operação é aplicada recursivamente a **todos os arquivos** dentro do diretório
- Respeita padrões de inclusão/exclusão de arquivos
- Filtra arquivos com base em condições avançadas (se configuradas)

### Quando Marcado (Modo Arquivo)
- O botão "Browse" abre um diálogo para selecionar **arquivo individual**
- A operação é aplicada apenas ao **arquivo específico** selecionado
- Ignora padrões de inclusão/exclusão (não aplicável a arquivo único)
- Condições avançadas ficam desabilitadas (específico de diretório)

## Implementação Técnica

### Search/Replace Panel
```python
self.is_file = QCheckBox("Is File?")
g.addWidget(self.is_file, 1, 0)

def _browse(self):
    if self.is_file.isChecked():
        path, _ = QFileDialog.getOpenFileName(self, "Select dictionary", "", 
                                              "JSON/TS (*.json *.ts *.tsx *.js *.jsx);;All (*)")
    else:
        path = QFileDialog.getExistingDirectory(self, "Select folder (or cancel and type a file)")
    
    if path:
        self.ed_path.setText(path)
```

### Insert Panel
Mesma implementação que Search/Replace Panel.

### JSON Translate Dock
```python
self.is_file = QCheckBox("Is file?")
g.addWidget(self.is_file, 1, 0)

def _browse_root(self):
    if self.is_file.isChecked():
        path, _ = QFileDialog.getOpenFileName(self, "Select file (or Cancel to pick a folder)")
        if path:
            self.ed_path.setText(path)
    else:
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            self.ed_path.setText(folder)
```

### Lógica de Processamento
```python
# Em _run() ou métodos similares
if os.path.isfile(path):
    paths = [path]  # Arquivo único
else:
    paths = list(walk_files(path, includes, excludes))  # Diretório recursivo
```

## Casos de Uso

### Caso 1: Busca em Projeto Inteiro
**Cenário**: Buscar padrão em todos os arquivos TypeScript de um projeto.
- ✅ Desmarcar "Is File"
- Selecionar diretório raiz do projeto
- Configurar include: `*.ts, *.tsx`
- Executar busca

### Caso 2: Substituição em Arquivo Específico
**Cenário**: Substituir texto apenas em `config.json`.
- ✅ Marcar "Is File"
- Selecionar arquivo `config.json` específico
- Configurar padrão de busca/substituição
- Executar substituição

### Caso 3: Tradução JSON de Múltiplos Arquivos
**Cenário**: Traduzir todos os arquivos de um diretório `i18n/`.
- ✅ Desmarcar "Is File"
- Selecionar diretório `i18n/`
- Configurar dicionário de tradução
- Executar tradução em massa

### Caso 4: Tradução de Arquivo Único
**Cenário**: Traduzir apenas `en.json`.
- ✅ Marcar "Is File"
- Selecionar arquivo `en.json`
- Configurar dicionário de tradução
- Executar tradução individual

## Interface Visual

```
┌─────────────────────────────────────────────┐
│  Path: /home/user/project/src      [Browse]│
│  ☐ Is File?                                 │  ← Checkbox
│                                             │
│  [Quando desmarcado: seleciona diretório]  │
│  [Quando marcado: seleciona arquivo]       │
└─────────────────────────────────────────────┘
```

## Comportamento com Condições Avançadas

### Search/Replace e Insert Panels
O checkbox "Is File" também controla a habilitação das condições avançadas:

```python
def change_advanced_conditions(self):
    self.enable_buttons(not self.is_file.isChecked(), include_buttons = False)
```

Quando marcado:
- ✅ Condições avançadas são **desabilitadas**
- Campos de filename, path, extension, etc. ficam inacessíveis
- Faz sentido: arquivo único não precisa de filtros

Quando desmarcado:
- ✅ Condições avançadas são **habilitadas**
- Permite filtrar arquivos por nome, extensão, tamanho, etc.
- Útil para processar apenas subconjunto de arquivos

## Benefícios

1. **Flexibilidade**: Trabalhe com arquivo único ou projeto inteiro
2. **Eficiência**: Não precisa mover arquivo para diretório separado
3. **Segurança**: Teste em arquivo único antes de aplicar em massa
4. **UX Consistente**: Mesmo padrão em todos os painéis
5. **Performance**: Processamento otimizado para arquivo único

## Compatibilidade

- ✅ Windows: Funciona com ambos os diálogos (arquivo/diretório)
- ✅ Linux: Suporte completo a GTK/Qt file dialogs
- ✅ macOS: Suporte completo a Cocoa file dialogs

## Notas de Implementação

1. **Estado Inicial**: Sempre desmarcado (modo diretório por padrão)
2. **Persistência**: Estado não é salvo entre sessões
3. **Validação**: Código verifica `os.path.isfile()` em runtime
4. **Fallback**: Se checkbox marcado mas caminho é diretório, trata como diretório

## Histórico

- **Implementação Original**: Versões iniciais do Clarify
- **Padronização**: Adicionado a todos os painéis principais
- **Status Atual**: ✅ Completamente implementado e funcional

## Melhorias Futuras

Possíveis melhorias para versões futuras:

1. **Persistir Estado**: Salvar preferência do usuário
2. **Atalho de Teclado**: Toggle via Ctrl+F
3. **Indicador Visual**: Ícone diferente para arquivo vs diretório
4. **Drag & Drop**: Detectar automaticamente tipo do item arrastado
5. **Multi-Seleção**: Permitir selecionar múltiplos arquivos

## Conclusão

A funcionalidade "Is File" está **completamente implementada** e disponível em todos os painéis relevantes do Clarify. Não requer nenhuma ação adicional - já está pronta para uso!
