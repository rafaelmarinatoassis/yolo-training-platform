# YOLO Training Platform

Uma plataforma web completa para gerenciar datasets, treinar modelos YOLO (YOLOv8) e executar testes de inferência com interface web moderna e monitoramento em tempo real.

## 🚀 Funcionalidades

- **Gerenciamento de Datasets**: Upload, organização e validação de datasets YOLO
- **Treinamento de Modelos**: Treinamento YOLOv8 com monitoramento em tempo real
- **Testes e Inferência**: Suporte para imagens, vídeos, diretórios e webcam
- **Interface Web Moderna**: Dashboard responsivo com Bootstrap
- **Monitoramento em Tempo Real**: WebSocket para atualizações de métricas
- **API RESTful**: API completa para integração
- **Docker**: Containerização completa para deploy fácil

## 📋 Requisitos

### Desenvolvimento
- Python 3.10.11+
- 8GB+ RAM (recomendado)
- GPU compatível com CUDA (opcional, mas recomendado)

### Produção
- Docker & Docker Compose
- 16GB+ RAM (recomendado)
- GPU com drivers NVIDIA (opcional)

## 🛠️ Instalação

### Desenvolvimento Local

1. **Clone o repositório**
```bash
git clone <repository-url>
cd yolo-training-platform
```

2. **Crie um ambiente virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

5. **Execute a aplicação**
```bash
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

### Deploy com Docker

1. **Clone o repositório**
```bash
git clone <repository-url>
cd yolo-training-platform
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env para produção
```

3. **Execute com Docker Compose**
```bash
docker-compose up -d
```

A aplicação estará disponível em `http://localhost`

## 🏗️ Estrutura do Projeto

```
project/
├── app/                    # Código principal da aplicação
│   ├── __init__.py        # Factory da aplicação Flask
│   ├── models.py          # Modelos SQLAlchemy
│   ├── routes/            # Blueprints das rotas
│   │   ├── datasets.py    # API de datasets
│   │   ├── trainings.py   # API de treinamentos
│   │   ├── tests.py       # API de testes
│   │   └── ui.py          # Rotas da interface web
│   ├── services/          # Serviços de negócio
│   │   ├── storage.py     # Gerenciamento de arquivos
│   │   ├── trainer.py     # Serviço de treinamento
│   │   └── infer.py       # Serviço de inferência
│   ├── templates/         # Templates HTML Jinja2
│   └── static/           # Arquivos estáticos (CSS, JS)
├── data/                 # Dados da aplicação
│   ├── datasets/         # Datasets organizados
│   ├── models/           # Modelos treinados
│   └── tests/            # Resultados de testes
├── docker-compose.yml    # Orquestração Docker
├── Dockerfile           # Imagem Docker
├── requirements.txt     # Dependências Python
├── run.py              # Script principal
└── README.md           # Este arquivo
```

## 🎯 Como Usar

### 1. Criar um Dataset

1. Acesse "Criar Dataset" na sidebar
2. Defina o nome e classes do dataset
3. Faça upload dos arquivos:
   - **Train**: Imagens e labels obrigatórios
   - **Validation**: Imagens e labels obrigatórios
   - **Test**: Opcional
4. O sistema validará e gerará o arquivo YAML automaticamente

**Formato dos arquivos:**
- Imagens: ZIP com .jpg, .jpeg, .png, .bmp
- Labels: ZIP com .txt no formato YOLO (class x_center y_center width height)

### 2. Treinar um Modelo

1. Acesse "Treinamento" na sidebar
2. Selecione o dataset
3. Configure os parâmetros:
   - Épocas, batch size, learning rate
   - Data augmentation, early stopping
4. Inicie o treinamento
5. Monitore o progresso em tempo real

### 3. Testar um Modelo

1. Acesse "Testar Modelo" na sidebar
2. Selecione o modelo treinado
3. Escolha o tipo de entrada:
   - **Imagem**: Upload de imagem única
   - **Vídeo**: Upload de arquivo de vídeo
   - **Diretório**: ZIP com múltiplas imagens
   - **Webcam**: Teste em tempo real
4. Configure os parâmetros de inferência
5. Execute o teste e visualize os resultados

## 🔧 API REST

### Datasets

- `GET /api/datasets` - Listar datasets
- `POST /api/datasets` - Criar dataset
- `GET /api/datasets/{id}` - Detalhes do dataset
- `PUT /api/datasets/{id}` - Atualizar dataset
- `DELETE /api/datasets/{id}` - Deletar dataset
- `GET /api/datasets/{id}/yaml` - Obter YAML do dataset

### Treinamentos

- `GET /api/trainings` - Listar treinamentos
- `POST /api/trainings` - Criar treinamento
- `GET /api/trainings/{id}` - Detalhes do treinamento
- `POST /api/trainings/{id}/cancel` - Cancelar treinamento
- `GET /api/trainings/{id}/metrics` - Métricas do treinamento
- `DELETE /api/trainings/{id}` - Deletar treinamento

### Testes

- `GET /api/tests` - Listar testes
- `POST /api/tests` - Criar teste
- `GET /api/tests/{id}` - Detalhes do teste
- `GET /api/tests/{id}/results` - Resultados do teste
- `DELETE /api/tests/{id}` - Deletar teste

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True

# Database
DATABASE_URL=sqlite:///yolo_trainer.db

# Storage
DATA_ROOT=data
MAX_UPLOAD_SIZE=2147483648  # 2GB

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Training
MAX_CONCURRENT_TRAININGS=2
DEFAULT_EPOCHS=100
DEFAULT_BATCH_SIZE=16
DEFAULT_IMG_SIZE=640

# Server
HOST=0.0.0.0
PORT=5000
```

### Banco de Dados

A aplicação usa SQLite por padrão para desenvolvimento. Para produção, recomenda-se PostgreSQL:

```bash
DATABASE_URL=postgresql://user:password@localhost/yolo_trainer
```

### Redis (Opcional)

Para monitoramento em tempo real e filas de trabalho em produção:

```bash
REDIS_URL=redis://localhost:6379/0
```

## 🐳 Docker

### Desenvolvimento

```bash
# Build e run com hot reload
docker-compose -f docker-compose.dev.yml up --build
```

### Produção

```bash
# Deploy completo com Nginx, Redis e Worker
docker-compose up -d
```

### Serviços Docker

- **app**: Aplicação Flask principal
- **redis**: Cache e filas de trabalho
- **worker**: Processamento assíncrono de treinamentos
- **nginx**: Proxy reverso e servidor de arquivos estáticos

## 📊 Monitoramento

### Logs

```bash
# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do worker
docker-compose logs -f worker

# Ver logs do nginx
docker-compose logs -f nginx
```

### Métricas

A aplicação expõe métricas via WebSocket em tempo real:
- Status de treinamentos
- Progresso de épocas
- Loss e mAP em tempo real
- Logs de treinamento

## 🔒 Segurança

### Produção

1. **Altere a SECRET_KEY**
2. **Configure HTTPS** com certificados SSL
3. **Use PostgreSQL** em vez de SQLite
4. **Configure firewall** para portas necessárias
5. **Limite upload de arquivos** conforme necessário
6. **Configure backup** dos dados importantes

### Rate Limiting

O Nginx está configurado com rate limiting:
- API geral: 10 req/s
- Upload: 1 req/s
- Burst permitido para picos

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de memória durante treinamento**
   - Reduza o batch size
   - Verifique RAM disponível
   - Use GPU se disponível

2. **Upload falha**
   - Verifique MAX_UPLOAD_SIZE
   - Confirme formato dos arquivos
   - Verifique espaço em disco

3. **WebSocket não conecta**
   - Verifique porta 5000
   - Confirme configuração do CORS
   - Teste sem proxy/firewall

4. **Modelo não treina**
   - Verifique dataset YAML
   - Confirme labels no formato correto
   - Verifique logs de erro

### Debug

```bash
# Ativar debug mode
export DEBUG=True

# Ver logs detalhados
export FLASK_ENV=development

# Verificar status dos containers
docker-compose ps

# Verificar logs específicos
docker-compose logs app
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Ultralytics](https://github.com/ultralytics/ultralytics) - Framework YOLO
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Socket.IO](https://socket.io/) - Comunicação em tempo real

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do email: support@yolo-trainer.com

---

**YOLO Training Platform** - Treine modelos YOLO com facilidade e elegância! 🚀