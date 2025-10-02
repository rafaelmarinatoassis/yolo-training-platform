# 🚀 YOLO Training Platform

<div align="center">

![YOLO Training Platform](https://img.shields.io/badge/YOLO-Training%20Platform-blue?style=for-the-badge&logo=artificial-intelligence)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=for-the-badge&logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Plataforma web completa para treinamento de modelos YOLO com dashboard em tempo real**

[🎯 Características](#-características) • [🚀 Instalação](#-instalação) • [📖 Como Usar](#-como-usar) • [🎨 Screenshots](#-screenshots) • [🤝 Contribuir](#-contribuir)

</div>

---

## 📋 Sobre o Projeto

O **YOLO Training Platform** é uma plataforma web moderna e intuitiva para treinar modelos de detecção de objetos YOLO (You Only Look Once). Desenvolvida para tornar o machine learning acessível tanto para iniciantes quanto para especialistas, oferece uma interface visual completa com monitoramento em tempo real.

### 🎯 Características

- ✅ **Interface Web Moderna**: Interface Bootstrap 5 responsiva e intuitiva
- ✅ **Dashboard em Tempo Real**: Monitoramento live de métricas de treinamento
- ✅ **Gestão de Datasets**: Upload, validação e organização de conjuntos de dados
- ✅ **Integração YOLOv8**: Suporte completo aos modelos YOLO mais recentes
- ✅ **Métricas Educativas**: Explicações claras sobre Loss, mAP50, Precisão e Recall
- ✅ **WebSocket Live**: Atualizações em tempo real via WebSocket
- ✅ **Histórico Completo**: Acompanhamento de todos os treinamentos realizados
- ✅ **Navegação Intuitiva**: Fluxo de trabalho otimizado e fácil de usar

### 🏗️ Arquitetura

```
yolo-training-platform/
├── app/                          # Aplicação principal
│   ├── models.py                # Modelos de dados SQLAlchemy
│   ├── __init__.py              # Configuração da aplicação Flask
│   ├── routes/                  # Rotas da aplicação
│   │   ├── ui.py               # Rotas da interface web
│   │   ├── datasets.py         # API de datasets
│   │   └── trainings.py        # API de treinamentos
│   ├── services/               # Serviços de negócio
│   │   ├── trainer.py          # Serviço de treinamento YOLO
│   │   ├── storage.py          # Gerenciamento de arquivos
│   │   └── infer.py           # Inferência de modelos
│   └── templates/              # Templates HTML
│       ├── base.html          # Template base
│       ├── index.html         # Página inicial
│       ├── training_dashboard.html  # Dashboard principal
│       └── ...                # Outras páginas
├── data/                       # Dados do projeto
│   ├── datasets/              # Datasets organizados
│   ├── models/                # Modelos treinados
│   └── tests/                 # Testes realizados
├── instance/                   # Banco de dados SQLite
├── requirements.txt           # Dependências Python
└── run.py                    # Ponto de entrada da aplicação
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Git
- 4GB+ de RAM recomendado
- GPU NVIDIA (opcional, mas recomendado para treinamentos rápidos)

#### ✅ **Verificar se você tem os pré-requisitos instalados:**

```bash
# Verificar se Python está instalado
python --version
# ou
python3 --version

# Verificar se Git está instalado
git --version
```

**❌ Se algum comando não funcionar:**
- **Python**: Baixe em [python.org](https://www.python.org/downloads/) (marque "Add to PATH")
- **Git**: Baixe em [git-scm.com](https://git-scm.com/downloads)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/rafaelmarinatoassis/yolo-training-platform.git
cd yolo-training-platform

# 2. Crie e ative um ambiente virtual
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python run.py
```

**📦 Para desenvolvimento (opcional):**
```bash
# Instalar dependências de desenvolvimento (debugging, testes, etc.)
pip install -r requirements-dev.txt
```

### Instalação Detalhada

<details>
<summary>Clique para ver instruções detalhadas</summary>

#### 1. Preparação do Ambiente

```bash
# Verificar versão do Python
python --version

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

#### 2. Instalação de Dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

#### 3. Configuração do Banco de Dados

```bash
# O banco SQLite será criado automaticamente na primeira execução
# Localizado em: instance/yolo_trainer.db
```

#### 4. Estrutura de Diretórios

```bash
# Criar diretórios necessários (automático)
mkdir -p data/datasets data/models data/tests
```

</details>

### ⚡ **Início Rápido (Para Iniciantes)**

1. **Baixe e instale Python** em [python.org](https://www.python.org/downloads/) (marque "Add to PATH")
2. **Baixe e instale Git** em [git-scm.com](https://git-scm.com/downloads)
3. **Abra o Terminal/PowerShell** e execute os comandos da seção "Instalação Rápida"
4. **Aguarde as instalações** (pode demorar alguns minutos)
5. **Acesse** http://localhost:5000 no seu navegador

**💡 Primeira vez usando?** Não se preocupe! O processo é automatizado e a interface é intuitiva.

## 📖 Como Usar

### 1. Iniciando a Aplicação

```bash
python run.py
```

🌐 **Acesse:** `http://localhost:5000`

**⚠️ Importante:** Mantenha o terminal aberto enquanto usa a aplicação!

### 2. Fluxo de Trabalho

#### 📁 **Passo 1: Criar Dataset**
1. Acesse "Criar Dataset" na página inicial
2. Faça upload das imagens e labels
3. Configure as classes de detecção
4. Valide o dataset

#### 🎯 **Passo 2: Configurar Treinamento**
1. Vá para "Treinamento" no menu
2. Selecione o dataset criado
3. Configure parâmetros:
   - Número de épocas
   - Batch size
   - Tamanho da imagem
   - Modelo base (YOLOv8n, YOLOv8m, etc.)

#### 📊 **Passo 3: Monitorar Dashboard**
1. Após iniciar o treinamento, acesse o dashboard
2. Acompanhe métricas em tempo real:
   - **Loss**: Erro do modelo (menor = melhor)
   - **mAP50**: Precisão principal (maior = melhor)
   - **Precisão**: Detecções corretas / Total detectado
   - **Recall**: Objetos encontrados / Total existente

#### 📈 **Passo 4: Analisar Resultados**
1. Visualize gráficos de progresso
2. Analise métricas finais
3. Baixe o modelo treinado
4. Teste com novas imagens

### 3. Interface Principal

#### 🏠 Dashboard Principal
- Cards informativos com métricas atuais
- Explicações educativas de cada métrica
- Histórico de épocas em tabela
- Indicador de conexão em tempo real

#### 📊 Página de Detalhes
- Gráficos interativos Chart.js
- Métricas completas por época
- Visualizações do YOLO (curvas F1, P, R)
- Logs de treinamento em tempo real

#### 📋 Lista de Treinamentos
- Histórico completo de treinamentos
- Filtros por status e dataset
- Ações rápidas (cancelar, baixar, deletar)
- Estatísticas resumidas

## 🎨 Screenshots

### Dashboard Principal
<img width="1899" height="825" alt="image" src="https://github.com/user-attachments/assets/5ab29c89-0d32-4262-9541-3c72601b6e99" />
*Dashboard em tempo real com métricas explicadas*

### Página de Treinamento
<img width="1902" height="910" alt="image" src="https://github.com/user-attachments/assets/13f3c9a2-9dae-4eb6-af32-c87d98cc8157" />
<img width="1918" height="906" alt="image" src="https://github.com/user-attachments/assets/a4551754-138c-4ba1-800e-18cc4bceb720" />
*Configuração de parâmetros de treinamento*

### Gestão de Datasets
<img width="1918" height="909" alt="image" src="https://github.com/user-attachments/assets/fd79dca3-8c51-4cf8-84d5-512f44ce1158" />
*Interface de upload e gestão de datasets*

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 2.3+**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-SocketIO**: WebSocket para tempo real
- **Ultralytics YOLOv8**: Framework de detecção de objetos
- **pandas**: Manipulação de dados CSV
- **Pillow**: Processamento de imagens
- **PyTorch**: Framework de deep learning
- **OpenCV**: Processamento de imagem e vídeo
- **NumPy**: Computação científica
- **Matplotlib/Seaborn**: Visualização de dados
- **Redis/RQ**: Fila de tarefas para processamento assíncrono

### Frontend
- **Bootstrap 5.3**: Framework CSS responsivo
- **Chart.js 3.x**: Gráficos interativos
- **Bootstrap Icons**: Ícones modernos
- **Socket.IO Client**: Cliente WebSocket
- **JavaScript ES6**: Interatividade moderna

### Infraestrutura
- **SQLite**: Banco de dados local
- **Virtual Environment**: Isolamento de dependências
- **CORS**: Suporte para requisições cross-origin

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

```bash
# .env (opcional)
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATA_ROOT=data
MAX_UPLOAD_SIZE=100MB
```

### Configuração de GPU

**Para GPU NVIDIA (recomendado para treinamentos rápidos):**
```bash
# Verificar se CUDA está disponível
python -c "import torch; print('CUDA disponível:', torch.cuda.is_available())"

# Se não estiver disponível, instalar PyTorch com suporte CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verificar novamente
python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'Dispositivos:', torch.cuda.device_count())"
```

**Para CPU apenas (funciona, mas mais lento):**
```bash
# PyTorch CPU-only (já incluído no requirements.txt)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Configuração de Produção

<details>
<summary>Deploy para produção</summary>

```bash
# Instalar servidor WSGI
pip install gunicorn

# Executar com Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# Ou com Docker (Dockerfile incluído)
docker build -t yolo-training-platform .
docker run -p 5000:5000 yolo-training-platform
```

</details>

## 🐛 Solução de Problemas

### Problemas Comuns

<details>
<summary>❌ Erro de import do ultralytics</summary>

```bash
# Reinstalar ultralytics
pip uninstall ultralytics
pip install ultralytics

# Verificar instalação
python -c "import ultralytics; print(ultralytics.__version__)"
```

</details>

<details>
<summary>❌ WebSocket não conecta</summary>

```bash
# Verificar se eventlet está instalado
pip install eventlet

# Verificar portas disponíveis
netstat -an | findstr :5000
```

</details>

<details>
<summary>❌ Upload de dataset falha</summary>

```bash
# Verificar estrutura de diretórios
ls -la data/datasets/

# Verificar permissões
chmod -R 755 data/
```

</details>

### Logs de Debug

```bash
# Executar em modo debug
FLASK_DEBUG=True python run.py

# Logs detalhados no console
```

## 🤝 Contribuir

Contribuições são sempre bem-vindas! Veja como você pode ajudar:

### 1. Reportar Bugs
- Use a aba [Issues](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)
- Descreva o problema detalhadamente
- Inclua logs e screenshots se possível

### 2. Sugerir Melhorias
- Abra um [Feature Request](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues/new)
- Explique o benefício da funcionalidade
- Forneça exemplos de uso

### 3. Contribuir com Código

```bash
# 1. Fork o repositório
# 2. Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade

# 3. Commit suas mudanças
git commit -m "feat: adiciona nova funcionalidade"

# 4. Push para a branch
git push origin feature/nova-funcionalidade

# 5. Abra um Pull Request
```

### 4. Padrões de Commit

```bash
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: manutenção
```

## 📝 Roadmap

### 🔮 Versão 2.0
- [ ] Suporte a outros modelos (Detectron2, EfficientDet)
- [ ] Deploy automático via Docker
- [ ] API REST completa
- [ ] Autenticação de usuários
- [ ] Compartilhamento de modelos

### 🎯 Versão 1.5
- [ ] Suporte a vídeos
- [ ] Anotação integrada
- [ ] Exportação para diferentes formatos
- [ ] Métricas avançadas
- [ ] Relatórios PDF

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

```
MIT License

Copyright (c) 2025 YOLO Training Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 👥 Autores

- **Rafael Marina** - *Desenvolvimento inicial* - [@rafaelmarinatoassis](https://github.com/rafaelmarinatoassis)

## 🙏 Agradecimentos

- [Ultralytics](https://ultralytics.com/) pelo framework YOLOv8
- [Flask](https://flask.palletsprojects.com/) pela base web
- [Bootstrap](https://getbootstrap.com/) pelo design responsivo
- [Chart.js](https://www.chartjs.org/) pelos gráficos interativos

---

<div align="center">

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

[🐛 Reportar Bug](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues) • [💡 Sugerir Feature](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues) • [📖 Documentação](https://github.com/rafaelmarinatoassis/yolo-training-platform/wiki)

</div>
