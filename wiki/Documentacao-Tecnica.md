# 🏗️ Documentação Técnica

Este documento descreve a arquitetura, APIs e detalhes técnicos do YOLO Training Platform para desenvolvedores e administradores de sistema.

## 📐 **Arquitetura do Sistema**

### 🏛️ **Visão Geral**

```mermaid
graph TB
    subgraph "Frontend"
        UI[Bootstrap 5 + Chart.js]
        WS[WebSocket Client]
    end
    
    subgraph "Backend Flask"
        API[REST API Routes]
        SIO[SocketIO Server]  
        BL[Business Logic]
    end
    
    subgraph "Services"
        TS[Training Service]
        SS[Storage Service]
        IS[Inference Service]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        FS[File System]
    end
    
    subgraph "AI/ML"
        YOLO[YOLOv8 Ultralytics]
        TORCH[PyTorch]
        CUDA[CUDA GPU]
    end
    
    UI --> API
    UI --> WS
    WS --> SIO
    API --> BL
    SIO --> BL
    BL --> TS
    BL --> SS  
    BL --> IS
    TS --> DB
    SS --> FS
    TS --> YOLO
    YOLO --> TORCH
    TORCH --> CUDA
```

### 🗂️ **Estrutura de Diretórios**

```
yolo-training-platform/
├── app/                          # Aplicação Flask principal
│   ├── __init__.py              # Factory pattern + configurações
│   ├── models.py                # SQLAlchemy ORM models  
│   │
│   ├── routes/                  # Blueprints da API REST
│   │   ├── ui.py               # Rotas das páginas HTML
│   │   ├── datasets.py         # API de datasets CRUD
│   │   ├── trainings.py        # API de treinamentos + WebSocket
│   │   └── tests.py            # API de inferência/testes
│   │
│   ├── services/               # Camada de serviços de negócio
│   │   ├── trainer.py          # Gerenciamento de treinamentos
│   │   ├── storage.py          # Manipulação de arquivos
│   │   └── infer.py           # Inferência de modelos
│   │
│   └── templates/              # Templates Jinja2
│       ├── base.html          # Template base
│       ├── index.html         # Dashboard principal
│       └── ...               # Outras páginas
│
├── data/                       # Dados persistentes
│   ├── datasets/              # Datasets do usuário
│   ├── models/                # Modelos treinados
│   └── tests/                 # Resultados de testes
│
├── instance/                   # Configurações de instância
│   └── yolo_trainer.db        # Banco SQLite
│
├── wiki/                       # Documentação
├── scripts/                    # Utilitários e ferramentas
├── requirements.txt            # Dependências de produção
├── requirements-dev.txt        # Dependências de desenvolvimento
└── run.py                     # Ponto de entrada
```

### 🔧 **Stack Tecnológico**

#### 🐍 **Backend**
- **Flask 2.3+**: Framework web Python minimalista
- **SQLAlchemy 2.0+**: ORM para persistência de dados
- **Flask-SocketIO 5.3+**: WebSocket para comunicação real-time
- **Flask-CORS 4.0+**: Cross-Origin Resource Sharing
- **python-dotenv 1.0+**: Gerenciamento de variáveis de ambiente

#### 🤖 **AI/ML**
- **Ultralytics 8.0+**: Framework YOLOv8 oficial
- **PyTorch 2.8+**: Backend de deep learning
- **TorchVision 0.23+**: Transformações de imagem
- **OpenCV 4.8+**: Processamento de imagem
- **NumPy 1.24+**: Computação numérica
- **pandas 2.3+**: Manipulação de dados
- **Matplotlib 3.7+**: Visualização de gráficos
- **Seaborn 0.13+**: Visualização estatística

#### 🎨 **Frontend**
- **Bootstrap 5.3**: Framework CSS responsivo
- **Chart.js 3.x**: Gráficos interativos
- **Bootstrap Icons**: Biblioteca de ícones
- **Socket.IO Client**: Cliente WebSocket JavaScript

#### 🗄️ **Infraestrutura**
- **SQLite**: Banco de dados relacional embarcado
- **File System**: Armazenamento de datasets e modelos
- **Redis** (opcional): Cache e filas de tarefas
- **RQ** (opcional): Job queues para tarefas assíncronas

## 🗄️ **Modelo de Dados**

### 📊 **Esquema do Banco de Dados**

```sql
-- Tabela de Datasets
CREATE TABLE dataset (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    classes TEXT,                    -- JSON array
    total_images INTEGER DEFAULT 0,
    train_images INTEGER DEFAULT 0, 
    val_images INTEGER DEFAULT 0,
    test_images INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    path VARCHAR(255),              -- Caminho no filesystem
    status VARCHAR(20) DEFAULT 'pending'  -- pending, validating, valid, invalid
);

-- Tabela de Treinamentos  
CREATE TABLE training (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dataset_id INTEGER REFERENCES dataset(id),
    model_version VARCHAR(10),      -- n, s, m, l, x
    epochs INTEGER DEFAULT 100,
    batch_size INTEGER DEFAULT 16,
    img_size INTEGER DEFAULT 640,
    learning_rate FLOAT DEFAULT 0.01,
    status VARCHAR(20),             -- pending, running, completed, failed, cancelled
    current_epoch INTEGER DEFAULT 0,
    total_epochs INTEGER,
    start_time DATETIME,
    end_time DATETIME,
    model_path VARCHAR(255),
    config_path VARCHAR(255),
    log_path VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
);

-- Tabela de Métricas por Época
CREATE TABLE training_metric (
    id INTEGER PRIMARY KEY,
    training_id INTEGER REFERENCES training(id),
    epoch INTEGER,
    loss FLOAT,
    precision FLOAT,
    recall FLOAT,
    map50 FLOAT,
    map95 FLOAT,
    val_loss FLOAT,
    learning_rate FLOAT,
    timestamp DATETIME
);

-- Tabela de Checkpoints
CREATE TABLE checkpoint (
    id INTEGER PRIMARY KEY, 
    training_id INTEGER REFERENCES training(id),
    epoch INTEGER,
    model_path VARCHAR(255),
    metrics TEXT,                   -- JSON com todas as métricas
    is_best BOOLEAN DEFAULT FALSE,
    created_at DATETIME
);

-- Tabela de Testes de Inferência
CREATE TABLE test (
    id INTEGER PRIMARY KEY,
    training_id INTEGER REFERENCES training(id),
    image_path VARCHAR(255),
    results TEXT,                   -- JSON com detecções
    confidence_threshold FLOAT,
    iou_threshold FLOAT,  
    inference_time FLOAT,
    created_at DATETIME
);
```

### 🔗 **Relacionamentos**
- `Dataset 1:N Training` - Um dataset pode ter múltiplos treinamentos
- `Training 1:N TrainingMetric` - Um treinamento tem métricas de cada época  
- `Training 1:N Checkpoint` - Um treinamento tem múltiplos checkpoints
- `Training 1:N Test` - Um treinamento pode ser testado múltiplas vezes

## 🔌 **API REST Reference**

### 🗂️ **Datasets API**

#### `GET /api/datasets`
Lista todos os datasets com paginação.

**Parâmetros:**
```json
{
  "page": 1,           // Página atual (opcional)
  "per_page": 10,      // Itens por página (opcional)  
  "status": "valid"    // Filtro por status (opcional)
}
```

**Resposta:**
```json
{
  "datasets": [
    {
      "id": 1,
      "name": "Detecção de Carros",
      "description": "Dataset de veículos em rodovias",
      "classes": ["carro", "caminhao", "moto"],
      "total_images": 2500,
      "train_images": 1750,
      "val_images": 500, 
      "test_images": 250,
      "status": "valid",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

#### `POST /api/datasets`  
Cria um novo dataset via upload de ZIP.

**Parâmetros (multipart/form-data):**
- `file`: Arquivo ZIP com estrutura YOLO
- `name`: Nome do dataset
- `description`: Descrição (opcional)
- `classes`: Classes separadas por vírgula

**Resposta:**
```json
{
  "message": "Dataset criado com sucesso",
  "dataset_id": 2,
  "status": "validating"
}
```

#### `GET /api/datasets/{id}`
Retorna detalhes de um dataset específico.

#### `DELETE /api/datasets/{id}`  
Remove um dataset e todos os arquivos associados.

### 🎯 **Trainings API**

#### `GET /api/trainings`
Lista todos os treinamentos.

**Parâmetros:**
```json
{
  "page": 1,
  "per_page": 10,
  "status": "running",     // pending, running, completed, failed, cancelled
  "dataset_id": 1          // Filtro por dataset
}
```

#### `POST /api/trainings`
Inicia um novo treinamento.

**Payload:**
```json
{
  "name": "Carros v1.0",
  "dataset_id": 1,
  "model_version": "m",    // n, s, m, l, x  
  "epochs": 100,
  "batch_size": 16,
  "img_size": 640,
  "learning_rate": 0.01
}
```

**Resposta:**  
```json
{
  "message": "Treinamento iniciado",
  "training_id": 5,
  "status": "pending"
}
```

#### `GET /api/trainings/{id}`
Detalhes de um treinamento específico.

#### `GET /api/trainings/{id}/metrics`
Métricas históricas do treinamento.

```json
{
  "epochs": [
    {
      "epoch": 1,
      "loss": 4.25,
      "precision": 0.12,
      "recall": 0.08, 
      "map50": 0.05,
      "val_loss": 4.89,
      "learning_rate": 0.01,
      "timestamp": "2025-01-15T10:45:30Z"
    }
  ]
}
```

#### `GET /api/trainings/{id}/csv-data`
Dados do arquivo results.csv gerado pelo YOLO.

#### `POST /api/trainings/{id}/stop`
Para um treinamento em andamento.

#### `GET /api/trainings/{id}/download`
Download do modelo treinado (.pt file).

### 🧪 **Tests API**

#### `POST /api/tests`
Executa inferência em uma imagem.

**Payload (multipart/form-data):**
- `file`: Imagem para testar
- `training_id`: ID do modelo treinado  
- `confidence`: Threshold de confiança (0.0-1.0)
- `iou`: Threshold de IoU (0.0-1.0)

**Resposta:**
```json
{
  "test_id": 10,
  "detections": [
    {
      "class": "carro",
      "confidence": 0.89,
      "bbox": [120, 80, 240, 160],  // x1, y1, x2, y2
      "center": [180, 120],
      "area": 9600
    }
  ],
  "inference_time": 45.2,  // ms
  "image_url": "/api/tests/10/image"
}
```

#### `GET /api/tests/{id}/image`
Retorna imagem com bounding boxes desenhados.

## 🔄 **WebSocket API**

### 📡 **Eventos em Tempo Real**

#### Cliente → Servidor

**`join_training`** - Entrar na sala de um treinamento
```javascript
socket.emit('join_training', {
  training_id: 5
});
```

**`leave_training`** - Sair da sala de um treinamento  
```javascript
socket.emit('leave_training', {
  training_id: 5
});
```

#### Servidor → Cliente

**`training_update`** - Atualização de métricas
```javascript
socket.on('training_update', function(data) {
  // data = {
  //   training_id: 5,
  //   epoch: 25,
  //   metrics: {
  //     loss: 2.1,
  //     precision: 0.67,
  //     recall: 0.72,
  //     map50: 0.58
  //   },
  //   status: 'running',
  //   eta: 1200  // seconds remaining
  // }
});
```

**`training_completed`** - Treinamento finalizado
```javascript
socket.on('training_completed', function(data) {
  // data = {
  //   training_id: 5,
  //   final_metrics: {...},
  //   model_path: '/models/5/best.pt',
  //   duration: 3600  // total seconds
  // }
});
```

**`training_error`** - Erro durante treinamento
```javascript
socket.on('training_error', function(data) {
  // data = {
  //   training_id: 5,
  //   error: 'CUDA out of memory',
  //   traceback: '...'
  // }
});
```

## 🔧 **Services Layer**

### 🎯 **TrainingService**

Responsável por gerenciar o ciclo de vida dos treinamentos.

```python
class TrainingService:
    def __init__(self, storage_service):
        self.storage = storage_service
        self.active_trainings = {}  # {training_id: thread_info}
    
    def start_training(self, training_id):
        """Inicia treinamento em thread separada"""
        
    def cancel_training(self, training_id):
        """Cancela treinamento ativo"""
        
    def _run_training(self, training_id):
        """Loop principal de treinamento (executa em background)"""
        # 1. Carrega configurações do banco
        # 2. Instancia modelo YOLO
        # 3. Configura callbacks para métricas  
        # 4. Inicia treinamento
        # 5. Emite atualizações via WebSocket
        # 6. Salva checkpoints
        # 7. Finaliza e salva modelo
```

**Métodos Principais:**
- `start_training(training_id)` - Inicia novo treinamento
- `cancel_training(training_id)` - Para treinamento ativo
- `get_training_status(training_id)` - Status atual
- `list_active_trainings()` - Treinamentos em execução
- `cleanup_training(training_id)` - Limpeza de recursos

### 💾 **StorageService**

Gerencia armazenamento de arquivos e organização do filesystem.

```python
class StorageService:
    def __init__(self, data_root='data'):
        self.data_root = Path(data_root)
        
    def save_dataset(self, file, dataset_id):
        """Salva e extrai dataset ZIP"""
        
    def validate_dataset_structure(self, dataset_path):
        """Valida estrutura YOLO do dataset"""
        
    def get_training_dir(self, training_id):
        """Retorna diretório do treinamento"""
        
    def cleanup_dataset(self, dataset_id):
        """Remove arquivos do dataset"""
```

**Estrutura de Armazenamento:**
```
data/
├── datasets/
│   └── {dataset_id}/
│       ├── dataset.yaml
│       ├── images/
│       └── labels/
├── models/
│   └── {training_id}/
│       ├── run/
│       │   ├── weights/
│       │   │   ├── best.pt
│       │   │   └── last.pt
│       │   ├── results.csv
│       │   └── *.png
│       └── config.yaml
└── tests/
    └── {test_id}/
        └── input_image.jpg
```

### 🔬 **InferenceService**

Executa inferência em imagens usando modelos treinados.

```python
class InferenceService:
    def __init__(self):
        self.loaded_models = {}  # Cache de modelos carregados
        
    def load_model(self, model_path):
        """Carrega modelo YOLO em memória"""
        
    def predict(self, image_path, model_path, conf=0.5, iou=0.5):
        """Executa inferência"""
        
    def draw_predictions(self, image, results):
        """Desenha bounding boxes na imagem"""
```

## ⚙️ **Configurações**

### 🔧 **app/__init__.py**
```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/yolo_trainer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max upload
    
    # Directories
    DATA_ROOT = os.environ.get('DATA_ROOT') or 'data'
    DATASETS_DIR = os.path.join(DATA_ROOT, 'datasets')
    MODELS_DIR = os.path.join(DATA_ROOT, 'models') 
    TESTS_DIR = os.path.join(DATA_ROOT, 'tests')
    
    # YOLO Settings
    DEFAULT_MODEL = 'yolov8m.pt'
    DEFAULT_EPOCHS = 100
    DEFAULT_BATCH_SIZE = 16
    DEFAULT_IMG_SIZE = 640
    
    # WebSocket
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
```

### 🌍 **Variáveis de Ambiente**
```bash
# .env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///instance/yolo_trainer.db
DATA_ROOT=data
MAX_UPLOAD_SIZE=500MB

# GPU Configuration  
CUDA_VISIBLE_DEVICES=0,1
TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6"

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=True
```

## 🔐 **Segurança**

### 🛡️ **Upload de Arquivos**
- Validação de extensões permitidas: `.zip`, `.jpg`, `.jpeg`, `.png`, `.txt`
- Limite de tamanho: 500MB por upload
- Sanitização de nomes de arquivo
- Validação de estrutura de diretórios
- Verificação de conteúdo de arquivos

### 🔒 **Paths e Filesystem**  
- Validação de paths para prevenir directory traversal
- Isolamento de dados por usuário (futura feature multi-tenant)
- Limpeza automática de arquivos temporários
- Backup automático de modelos importantes

### ⚡ **Rate Limiting**
```python
# Limites por endpoint (implementação futura)
@limiter.limit("10 per minute")  # Upload de datasets
@limiter.limit("5 per minute")   # Início de treinamentos  
@limiter.limit("100 per minute") # Consultas de métricas
```

## 📊 **Monitoring e Logs**

### 📋 **Estrutura de Logs**
```python
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Loggers específicos
dataset_logger = logging.getLogger('yolo.dataset')
training_logger = logging.getLogger('yolo.training')  
inference_logger = logging.getLogger('yolo.inference')
```

### 📈 **Métricas de Sistema**
- CPU e RAM usage durante treinamentos
- GPU utilização e temperatura  
- Disk I/O para datasets grandes
- Network usage para WebSocket connections
- Database query performance

## 🚀 **Performance**

### ⚡ **Otimizações Implementadas**
- **Lazy Loading**: Modelos carregados apenas quando necessário
- **Caching**: Cache de datasets validados e modelos em memória
- **Async Processing**: Treinamentos em threads separadas
- **Batch Processing**: Processamento de múltiplas imagens
- **Connection Pooling**: Pool de conexões de banco
- **Static File Caching**: Cache de assets estáticos

### 📊 **Benchmarks Típicos**
```
Dataset Upload (1000 imgs): ~30 segundos
Training YOLOv8m (100 epochs): ~2-4 horas (RTX 3070)
Inference per image: ~20-50ms (GPU) / ~200-500ms (CPU)
WebSocket latency: <10ms (localhost)
Database queries: <5ms (SQLite)
```

## 🔄 **Deploy e Produção**

### 🐳 **Docker**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
```

### ☸️ **Kubernetes** (exemplo)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yolo-training-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: yolo-training-platform
  template:
    metadata:
      labels:
        app: yolo-training-platform
    spec:
      containers:
      - name: app
        image: yolo-training-platform:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@postgres:5432/yolo"
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "8Gi"
          requests:
            memory: "4Gi"
```

---

**🔧 Próximo passo**: [Solução de Problemas](Solucao-de-Problemas.md)