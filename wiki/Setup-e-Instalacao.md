# ⚙️ Setup e Instalação

## 📋 Requisitos do Sistema

### 🖥️ **Requisitos Mínimos**
- **Sistema Operacional**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 ou superior
- **RAM**: 4GB (8GB recomendado)
- **Armazenamento**: 2GB livre
- **Internet**: Para download de dependências

### 🚀 **Requisitos Recomendados**
- **Sistema Operacional**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10 ou superior
- **RAM**: 16GB ou mais
- **GPU**: NVIDIA com suporte CUDA (para treinamentos rápidos)
- **Armazenamento**: 10GB+ livre (para datasets grandes)

### 🔧 **Software Necessário**
- **Git**: Para clonar o repositório
- **Python**: Com pip incluído
- **CUDA** (opcional): Para aceleração GPU

## 📥 **Instalação Passo a Passo**

### 1️⃣ **Verificar Pré-requisitos**

#### Windows
```powershell
# Verificar Python
python --version
# Deve retornar Python 3.8+ 

# Verificar Git  
git --version
# Deve retornar versão do Git

# Verificar pip
pip --version
```

#### Linux/macOS
```bash
# Verificar Python
python3 --version
# ou
python --version

# Verificar Git
git --version

# Verificar pip
pip3 --version
# ou  
pip --version
```

#### ❌ **Se algum não estiver instalado:**

**Python:**
- Windows: [python.org/downloads](https://www.python.org/downloads/) 
- macOS: `brew install python` ou python.org
- Ubuntu: `sudo apt install python3 python3-pip`

**Git:**
- Windows: [git-scm.com](https://git-scm.com/downloads)
- macOS: `brew install git` ou Xcode tools
- Ubuntu: `sudo apt install git`

### 2️⃣ **Clonar o Repositório**

```bash
# Clone o repositório
git clone https://github.com/rafaelmarinatoassis/yolo-training-platform.git

# Entre no diretório
cd yolo-training-platform

# Verifique o conteúdo
ls -la  # Linux/Mac
dir     # Windows
```

### 3️⃣ **Configurar Ambiente Virtual**

#### Windows (PowerShell)
```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Se houver erro de política, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar ativação
where python
# Deve mostrar path dentro do .venv
```

#### Windows (CMD)
```cmd
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual  
.venv\Scripts\activate.bat

# Verificar ativação
where python
```

#### Linux/macOS
```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar ativação
which python
# Deve mostrar path dentro do .venv
```

### 4️⃣ **Instalar Dependências**

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências principais
pip install -r requirements.txt

# Verificar instalação
pip list

# Testar imports principais
python -c "import flask, ultralytics, pandas; print('✅ Instalação bem-sucedida!')"
```

### 5️⃣ **Configuração de GPU (Opcional)**

#### Para NVIDIA GPU:
```bash
# Verificar CUDA disponível
python -c "import torch; print('CUDA disponível:', torch.cuda.is_available())"

# Se não tiver CUDA, instalar PyTorch com CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verificar novamente
python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'GPUs:', torch.cuda.device_count())"
```

### 6️⃣ **Executar a Aplicação**

```bash
# Executar servidor de desenvolvimento
python run.py
```

**Saída esperada:**
```
 * Running on http://localhost:5000
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
```

### 7️⃣ **Verificar Funcionamento**

1. **Abra o navegador** em `http://localhost:5000`
2. **Verifique a página inicial** - deve carregar sem erros
3. **Teste a navegação** - clique nos menus
4. **Verifique o console** - não deve ter erros

## 🛠️ **Configurações Avançadas**

### 🔒 **Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do projeto:

```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria
DATA_ROOT=data
MAX_UPLOAD_SIZE=500MB
DATABASE_URL=sqlite:///instance/yolo_trainer.db
```

### 🗄️ **Configuração do Banco de Dados**

```bash
# O banco SQLite é criado automaticamente
# Localização: instance/yolo_trainer.db

# Para resetar o banco (cuidado - apaga tudo!):
rm instance/yolo_trainer.db  # Linux/Mac
del instance\yolo_trainer.db # Windows
```

### 📁 **Estrutura de Diretórios**

```
yolo-training-platform/
├── .venv/                  # Ambiente virtual
├── app/                    # Aplicação Flask
├── data/                   # Dados do usuário
│   ├── datasets/          # Datasets organizados
│   ├── models/            # Modelos treinados
│   └── tests/             # Testes realizados
├── instance/               # Banco de dados
├── wiki/                   # Documentação
├── requirements.txt        # Dependências
├── requirements-dev.txt    # Dependências desenvolvimento
├── run.py                  # Arquivo principal
└── .env                    # Configurações (criar)
```

## 🐳 **Instalação com Docker**

### 📦 **Usando Docker Compose**
```bash
# Clone o repositório
git clone https://github.com/rafaelmarinatoassis/yolo-training-platform.git
cd yolo-training-platform

# Execute com Docker Compose
docker-compose up -d

# Acesse http://localhost:5000
```

### 🔨 **Build manual**
```bash
# Build da imagem
docker build -t yolo-training-platform .

# Executar container
docker run -p 5000:5000 -v $(pwd)/data:/app/data yolo-training-platform

# Parar container
docker stop yolo-training-platform
```

## 🔧 **Desenvolvimento**

### 📚 **Dependências de Desenvolvimento**
```bash
# Instalar ferramentas de desenvolvimento
pip install -r requirements-dev.txt

# Inclui: black, flake8, pytest, jupyter, etc.
```

### 🧪 **Executar Testes**
```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=app

# Testes específicos
pytest tests/test_models.py
```

### 🎨 **Formatação de Código**
```bash
# Formatar código com black
black .

# Verificar estilo com flake8
flake8 app/

# Type checking com mypy
mypy app/
```

## 🚨 **Solução de Problemas Comuns**

### ❌ **Erro: ModuleNotFoundError**
```bash
# Verificar se ambiente virtual está ativo
# Windows: .venv\Scripts\Activate.ps1
# Linux/Mac: source .venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### ❌ **Erro: Port already in use**
```bash
# Windows: encontrar processo usando porta 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac: matar processo na porta 5000  
lsof -ti:5000 | xargs kill -9

# Ou usar porta diferente
python run.py --port 5001
```

### ❌ **Erro: Permission denied**
```bash
# Linux/Mac: ajustar permissões
chmod +x run.py
sudo chown -R $USER:$USER data/

# Windows: executar como administrador
```

### ❌ **Erro: CUDA out of memory**
```bash
# Reduzir batch size no treinamento
# Usar modelo menor (YOLOv8n ao invés de YOLOv8x)
# Fechar outros programas que usam GPU
```

## 📞 **Suporte**

- 📖 **Documentação**: [Wiki completa](Home.md)
- 🐛 **Bugs**: [Issues do GitHub](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/rafaelmarinatoassis/yolo-training-platform/discussions)
- 📧 **Email**: rafael@example.com

---

**⭐ Próximo passo**: [Guia do Usuário](Guia-do-Usuario.md)