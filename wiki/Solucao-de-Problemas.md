# 🐛 Solução de Problemas

Este guia abrangente ajuda a diagnosticar e resolver problemas comuns no YOLO Training Platform.

## 🚨 **Problemas de Instalação**

### ❌ **"ModuleNotFoundError: No module named 'flask'"**

**Sintomas:**
```bash
python run.py
Traceback (most recent call last):
  File "run.py", line 4, in <module>
    from app import create_app, socketio
ModuleNotFoundError: No module named 'flask'
```

**Causa:** Ambiente virtual não ativado ou dependências não instaladas.

**Solução:**
```bash
# 1. Verificar se ambiente virtual está ativo
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD  
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate

# 2. Reinstalar dependências
pip install -r requirements.txt

# 3. Verificar instalação
pip list | grep -i flask
```

### ❌ **"Permission denied" ou "Access denied"**

**Sintomas:**
```bash
PermissionError: [Errno 13] Permission denied: 'data/datasets'
```

**Solução Windows:**
```powershell
# Executar como administrador
Right-click PowerShell → "Run as administrator"

# Ou ajustar permissões do diretório
icacls "C:\path\to\yolo-training-platform" /grant Users:F /T
```

**Solução Linux/Mac:**
```bash
# Ajustar permissões
sudo chown -R $USER:$USER .
chmod -R 755 data/

# Ou executar com sudo (não recomendado)
sudo python run.py
```

### ❌ **"python: command not found"**

**Sintomas:**
```bash
python --version
bash: python: command not found
```

**Solução:**

**Windows:**
1. Baixar Python em [python.org](https://www.python.org/downloads/)
2. ✅ Marcar "Add Python to PATH" durante instalação
3. Reiniciar terminal/cmd

**Linux/Ubuntu:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# Via Homebrew
brew install python

# Ou baixar de python.org
```

### ❌ **"git: command not found"**

**Solução:**

**Windows:** Baixar em [git-scm.com](https://git-scm.com/downloads)

**Linux/Ubuntu:**
```bash
sudo apt install git
```

**macOS:**
```bash
# Via Homebrew  
brew install git

# Ou instalar Xcode Command Line Tools
xcode-select --install
```

## 🔥 **Problemas de Execução**

### ❌ **"Address already in use" - Porta 5000 ocupada**

**Sintomas:**
```
OSError: [Errno 48] Address already in use
```

**Solução Windows:**
```powershell
# Encontrar processo usando porta 5000
netstat -ano | findstr :5000
# TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    1234

# Matar processo (substituir 1234 pelo PID real)
taskkill /PID 1234 /F

# Ou usar porta diferente
set FLASK_RUN_PORT=5001
python run.py
```

**Solução Linux/Mac:**
```bash
# Encontrar e matar processo
lsof -ti:5000 | xargs kill -9

# Ou usar porta diferente  
export FLASK_RUN_PORT=5001
python run.py
```

### ❌ **"Failed to initialize CUDA" - Problemas com GPU**

**Sintomas:**
```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

**Diagnóstico:**
```bash
# Verificar CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
python -c "import torch; print('CUDA version:', torch.version.cuda)"
python -c "import torch; print('GPU count:', torch.cuda.device_count())"

# Verificar GPU
nvidia-smi  # Linux/Windows com NVIDIA drivers
```

**Soluções:**
```bash
# 1. Reinstalar PyTorch com CUDA correto
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 2. Ou usar CPU apenas (mais lento)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 3. Verificar drivers NVIDIA atualizados
# Windows: GeForce Experience ou site NVIDIA
# Linux: sudo apt install nvidia-driver-XXX
```

### ❌ **"CUDA out of memory"**

**Sintomas:**
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**Soluções imediatas:**
```bash
# 1. Reduzir batch size
# Editar parâmetros de treinamento:
# batch_size: 16 → 8 → 4 → 2

# 2. Usar imagem menor
# img_size: 640 → 416 → 320

# 3. Fechar outros programas usando GPU
# Chrome, jogos, outros modelos ML

# 4. Limpar cache CUDA
python -c "import torch; torch.cuda.empty_cache()"
```

**Soluções permanentes:**
- Upgrade GPU para 8GB+ VRAM
- Usar treinamento distribuído
- Usar CPU (lento mas funciona)

## 💾 **Problemas com Datasets**

### ❌ **"Dataset validation failed"**

**Sintomas:**
- Upload aparenta sucesso mas dataset fica com status "invalid"
- Mensagens de erro na validação

**Verificações:**
```bash
# 1. Estrutura correta?
dataset.zip
├── images/
│   ├── train/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── val/
│       ├── img3.jpg
│       └── img4.jpg
└── labels/
    ├── train/
    │   ├── img1.txt
    │   └── img2.txt
    └── val/
        ├── img3.txt
        └── img4.txt
```

**Problemas comuns:**
```bash
# ❌ Estrutura incorreta
dataset.zip
├── train/           # ERRADO: deveria ser images/train/
├── labels_train/    # ERRADO: deveria ser labels/train/

# ❌ Nomes não correspondem
images/train/photo1.jpg
labels/train/image1.txt  # ERRADO: deveria ser photo1.txt

# ❌ Formato YOLO incorreto
# ERRADO: 
0 120 80 200 150     # Coordenadas absolutas
# CORRETO:
0 0.5 0.4 0.3 0.6    # Coordenadas normalizadas (0-1)
```

**Solução:**
1. **Verificar estrutura** exata de pastas
2. **Verificar correspondência** nome imagem ↔ label
3. **Validar formato YOLO** das annotations
4. **Recriar ZIP** com estrutura correta

### ❌ **"Invalid YOLO format in labels"**

**Sintomas:**
Erro durante validação de labels.

**Formato correto YOLO:**
```
# Cada linha: class_id center_x center_y width height
0 0.5 0.5 0.4 0.6    # Objeto classe 0, centro (0.5,0.5), tamanho 0.4x0.6
1 0.2 0.3 0.1 0.2    # Objeto classe 1, centro (0.2,0.3), tamanho 0.1x0.2

# ✅ Valores entre 0 e 1
# ✅ center_x, center_y = centro do objeto  
# ✅ width, height = largura e altura
# ✅ class_id = índice da classe (0, 1, 2...)
```

**Erros comuns:**
```bash
# ❌ Coordenadas absolutas (pixels)
0 100 50 200 150

# ❌ Coordenadas x1,y1,x2,y2 (formato PASCAL VOC)
0 0.1 0.2 0.7 0.8

# ❌ Valores fora do range 0-1
0 1.2 0.5 0.4 0.6

# ❌ Classe inexistente
5 0.5 0.5 0.4 0.6    # Se só há 3 classes (0,1,2)
```

## 🎯 **Problemas de Treinamento**

### ❌ **Treinamento não inicia**

**Sintomas:**
- Status permanece "pending" por muito tempo
- Nenhuma atualização no dashboard

**Diagnóstico:**
```bash
# 1. Verificar logs
tail -f logs/app.log

# 2. Verificar processo Python
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows

# 3. Verificar espaço em disco
df -h  # Linux/Mac
dir C:\  # Windows

# 4. Verificar conectividade WebSocket
# Abrir DevTools do navegador → Console
# Deve mostrar: "Connected to server"
```

**Soluções:**
```bash
# 1. Restart da aplicação
Ctrl+C  # Parar servidor
python run.py  # Reiniciar

# 2. Limpar cache
rm -rf __pycache__/ app/__pycache__/  # Linux/Mac
del /s __pycache__  # Windows

# 3. Verificar permissões data/
chmod -R 755 data/  # Linux/Mac

# 4. Verificar espaço livre (min 2GB)
```

### ❌ **Loss não diminui / Modelo não aprende**

**Sintomas:**
```
Epoch 1: Loss = 4.2
Epoch 20: Loss = 4.1  
Epoch 50: Loss = 4.3
Epoch 100: Loss = 4.0  # Sem melhoria significativa
```

**Causas possíveis:**
1. **Dataset ruim** - annotations incorretas
2. **Learning rate alto** - modelo não converge  
3. **Batch size inadequado** - gradientes instáveis
4. **Dados insuficientes** - dataset muito pequeno

**Soluções:**

**1. Verificar qualidade dos dados:**
```bash
# Revisar algumas annotations manualmente
# Abrir imagem + label correspondente
# Verificar se bounding boxes fazem sentido
```

**2. Ajustar hiperparâmetros:**
```python
# Reduzir learning rate
learning_rate: 0.01 → 0.005 → 0.001

# Ajustar batch size
batch_size: 16 → 8 (para dados pequenos)
batch_size: 16 → 32 (para dados grandes)

# Aumentar épocas  
epochs: 100 → 200 → 300
```

**3. Usar modelo menor:**
```python
# Começar simples
model: YOLOv8x → YOLOv8n
# Aumentar gradualmente se funcionar
```

### ❌ **Overfitting detectado**

**Sintomas:**
```
Epoch 50:
  Train Loss: 0.5    ✅ Muito baixo
  Val Loss: 2.8      ❌ Alto
  
  Train mAP50: 0.95  ✅ Excelente  
  Val mAP50: 0.42    ❌ Ruim
```

**Soluções:**
```python
# 1. Early stopping mais agressivo
patience: 50 → 20

# 2. Mais data augmentation  
# (configurado automaticamente no YOLO)

# 3. Reduzir complexidade
model: YOLOv8l → YOLOv8m → YOLOv8s

# 4. Mais dados de validação
# Aumentar conjunto val/ no dataset
```

### ❌ **Treinamento muito lento**

**Sintomas:**
- Cada época demora > 10 minutos
- ETA mostra várias horas/dias

**Otimizações:**

**1. GPU:**
```bash
# Verificar se está usando GPU
python -c "import torch; print('Using GPU:', torch.cuda.is_available())"

# Verificar utilização
nvidia-smi  # Deve mostrar ~80-95% GPU usage
```

**2. Batch size:**
```python
# Aumentar batch size (se tiver VRAM)
batch_size: 8 → 16 → 32

# Monitorar VRAM usage
nvidia-smi  # Não deve exceder 90%
```

**3. Número de workers:**
```python
# Ajustar workers para carregamento de dados
# Automático no YOLO, mas pode verificar CPU usage
# htop (Linux) / Task Manager (Windows)
```

**4. SSD:**
```bash
# Mover dataset para SSD se estiver em HD
# Especialmente importante para datasets grandes
```

## 🌐 **Problemas de Interface Web**

### ❌ **Página não carrega / "This site can't be reached"**

**Diagnóstico:**
```bash
# 1. Servidor está rodando?
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows

# 2. Porta está aberta?
netstat -an | grep :5000  # Linux/Mac  
netstat -an | findstr :5000  # Windows

# 3. Firewall bloqueando?
# Windows: Windows Defender Firewall
# Linux: sudo ufw status
```

**Soluções:**
```bash
# 1. Restart servidor
Ctrl+C
python run.py

# 2. Tentar porta diferente
python run.py --port 5001
# Acessar: http://localhost:5001

# 3. Verificar binding
# Se só funciona localmente:
# Editar run.py: app.run(host='0.0.0.0', port=5000)
```

### ❌ **Dashboard não atualiza em tempo real**

**Sintomas:**
- Métricas não mudam durante treinamento
- Indicador mostra "Desconectado"

**Diagnóstico:**
```javascript
// Abrir DevTools (F12) → Console
// Deve mostrar:
"Connected to server"
"Joined training room: 5"

// Se mostrar erros WebSocket:
"WebSocket connection failed"
"Socket.IO disconnected"
```

**Soluções:**
```bash
# 1. Verificar se eventlet está instalado
pip install eventlet

# 2. Restart do servidor
Ctrl+C
python run.py

# 3. Limpar cache do navegador
Ctrl+Shift+Del  # Chrome/Firefox

# 4. Tentar navegador diferente
# Chrome, Firefox, Edge
```

### ❌ **Upload de dataset falha**

**Sintomas:**
- Barra de progresso trava em 50%
- Erro 413 "Payload Too Large"
- Timeout durante upload

**Soluções:**
```python
# 1. Verificar tamanho do arquivo
# Máximo: 500MB por padrão

# 2. Aumentar limite (app/__init__.py):
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB

# 3. Dividir dataset em partes menores
# Menos de 500MB por ZIP

# 4. Verificar conexão internet
# Upload grande requer conexão estável
```

## 🔧 **Problemas de Performance**

### ❌ **Sistema lento / Travando**

**Diagnóstico:**
```bash
# 1. CPU usage
top  # Linux/Mac
Task Manager  # Windows

# 2. RAM usage  
free -h  # Linux
Get-ComputerInfo | select TotalPhysicalMemory  # Windows

# 3. Disk I/O
iotop  # Linux (requer instalação)
Resource Monitor → Disk  # Windows

# 4. GPU usage (se aplicável)
nvidia-smi
```

**Soluções:**

**Alto CPU:**
```python
# Reduzir workers de dados
# Fechar outros programas
# Usar batch_size menor
```

**Alto RAM:**
```python  
# Reduzir batch_size: 32 → 16 → 8
# Fechar navegadores com muitas abas
# Restart do sistema
```

**Alto Disk I/O:**
```bash
# Mover para SSD
# Usar dataset menor para testes
# Aumentar RAM para cache
```

### ❌ **Navegador lento / Travando**

**Sintomas:**
- Interface web responsiva lenta
- Gráficos não carregam
- Abas travando

**Soluções:**
```bash
# 1. Limpar cache navegador
Ctrl+Shift+Del

# 2. Desabilitar extensões
# Chrome: chrome://extensions/
# Firefox: about:addons

# 3. Aumentar RAM disponível
# Fechar outras abas/programas

# 4. Usar navegador diferente
# Chrome, Firefox, Edge

# 5. Reduzir qualidade gráficos
# Menos pontos nos gráficos Chart.js
```

## 🔍 **Debugging e Logs**

### 📋 **Ativando Logs Detalhados**

```python
# 1. Modo debug (app/__init__.py)
app.config['DEBUG'] = True

# 2. Nível de log mais verboso
import logging
logging.basicConfig(level=logging.DEBUG)

# 3. Logs específicos YOLO
import ultralytics
ultralytics.checks()  # Mostra informações sistema
```

### 📊 **Verificando Status do Sistema**

```bash
# 1. Informações Python
python -c "
import sys, torch, ultralytics, flask
print(f'Python: {sys.version}')  
print(f'PyTorch: {torch.__version__}')
print(f'YOLO: {ultralytics.__version__}')
print(f'Flask: {flask.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
"

# 2. Espaço em disco
df -h .  # Linux/Mac
dir /-c .  # Windows

# 3. Processos ativos
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows
```

### 🆘 **Última solução: Reset completo**

```bash
# ⚠️ CUIDADO: Apaga todos os dados!

# 1. Parar servidor
Ctrl+C

# 2. Backup dados importantes
cp -r data/ backup_data/

# 3. Limpar tudo
rm -rf data/ instance/ logs/ __pycache__/
rm -rf .venv/

# 4. Reinstalar do zero
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# 5. Reiniciar
python run.py
```

## 📞 **Suporte e Comunidade**

Se nenhuma solução funcionou:

1. **📝 Criar Issue detalhado:** [GitHub Issues](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)
   - Incluir logs completos
   - Sistema operacional e versão  
   - Passos para reproduzir
   - Screenshots se aplicável

2. **💬 Discussões:** [GitHub Discussions](https://github.com/rafaelmarinatoassis/yolo-training-platform/discussions)

3. **📧 Email:** rafael@example.com

4. **🤖 AI Assistant:** Descreva seu problema detalhadamente

### 📋 **Template para reportar bugs:**

```markdown
**Sistema:**
- OS: Windows 11 / Ubuntu 22.04 / macOS 13
- Python: 3.10.8  
- GPU: NVIDIA RTX 3070 / Intel integrated / Apple M1

**Problema:**
Descrição clara do que está acontecendo...

**Passos para reproduzir:**
1. Fazer upload dataset
2. Configurar treinamento  
3. Clicar "Iniciar"
4. Erro aparece...

**Logs/Erros:**
```
Traceback completo aqui...
```

**Tentativas de solução:**
- Tentei reinstalar dependências
- Verificei GPU com nvidia-smi
- etc.
```

---

**🛠️ Próximo passo**: [Contribuição](Contribuicao.md)