# 🚀 Clarify GUI Launchers

Este diretório contém scripts de lançamento para iniciar o Clarify em modo gráfico (GUI) de forma simples e rápida, independentemente do sistema operacional.

## 📋 Arquivos Disponíveis

### 🐧 Linux
**Arquivo**: `clarify_gui.sh`

**Como usar**:
1. Tornar executável (se ainda não estiver):
   ```bash
   chmod +x clarify_gui.sh
   ```
2. Executar de uma das seguintes formas:
   - Duplo clique no arquivo no gerenciador de arquivos
   - Ou via terminal:
     ```bash
     ./clarify_gui.sh
     ```

### 🪟 Windows
**Arquivo**: `clarify_gui.bat`

**Como usar**:
- Simplesmente dê duplo clique no arquivo `clarify_gui.bat`
- Ou execute via CMD/PowerShell:
  ```cmd
  clarify_gui.bat
  ```

### 🍎 macOS
**Arquivo**: `clarify_gui.command`

**Como usar**:
1. Tornar executável (primeira vez apenas):
   ```bash
   chmod +x clarify_gui.command
   ```
2. Duplo clique no arquivo no Finder
   - Se o macOS bloquear por questões de segurança:
     - Vá em **Preferências do Sistema** → **Segurança e Privacidade**
     - Clique em "Abrir Assim Mesmo" / "Open Anyway"
   - Ou execute via Terminal:
     ```bash
     ./clarify_gui.command
     ```

## ✅ Pré-requisitos

Todos os scripts verificam automaticamente e oferecem instalar:

1. **Python 3.10+** (obrigatório)
   - Linux: `sudo apt install python3` ou `sudo dnf install python3`
   - Windows: [python.org/downloads](https://www.python.org/downloads/)
   - macOS: `brew install python3` ou [python.org/downloads](https://www.python.org/downloads/)

2. **PySide6** (obrigatório para GUI)
   - Os scripts oferecem instalação automática
   - Ou instale manualmente: `pip3 install PySide6`

## 🎯 Funcionalidades dos Scripts

Os launchers fazem automaticamente:
- ✅ Verificam se Python está instalado
- ✅ Verificam se PySide6 está instalado
- ✅ Oferecem instalar PySide6 caso não esteja
- ✅ Navegam para o diretório correto do projeto
- ✅ Executam `python -m src` (modo GUI)
- ✅ Exibem mensagens de erro caso algo falhe
- ✅ Pausam antes de fechar em caso de erro

## 🔧 Solução de Problemas

### "Python não encontrado"
- **Certifique-se de que Python 3.10+ está instalado**
- Windows: Reinstale Python marcando "Add Python to PATH"
- Linux/Mac: Instale via gerenciador de pacotes

### "PySide6 não instalado"
- Os scripts oferecem instalação automática
- Se falhar, instale manualmente:
  ```bash
  pip3 install PySide6
  # ou
  pip3 install --user PySide6
  ```

### macOS: "Desenvolvedor não verificado"
- Clique com botão direito no arquivo → **Abrir**
- Ou vá em Preferências do Sistema → Segurança

### Permissão negada (Linux/Mac)
```bash
chmod +x clarify_gui.sh  # ou clarify_gui.command
```

## 📝 Notas

- Os scripts **não modificam** seu sistema além de instalar PySide6 se solicitado
- Funcionam de qualquer local onde estejam (navegam automaticamente para o diretório do projeto)
- São seguros para distribuição

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se Python 3.10+ está instalado: `python3 --version`
2. Verifique se PySide6 está instalado: `python3 -c "import PySide6"`
3. Execute manualmente: `python3 -m src` no diretório do projeto
4. Consulte a documentação principal em `README.md`

---

**Dica**: Para criar atalhos na área de trabalho, basta copiar o arquivo apropriado para sua área de trabalho!
