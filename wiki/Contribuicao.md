# 🤝 Como Contribuir

Obrigado por considerar contribuir com o **YOLO Training Platform**! 🎉 

Este guia te ajuda a começar como colaborador, desde reportar bugs até desenvolver novas funcionalidades.

## 🎯 **Como Você Pode Ajudar**

### 🐛 **Reportar Bugs**
- Encontrou um problema? [Crie uma issue](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues/new)
- Use o template de bug report
- Inclua logs, screenshots e passos para reproduzir

### 💡 **Sugerir Melhorias**  
- Tem uma ideia legal? [Abra um feature request](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues/new)
- Descreva o benefício da funcionalidade
- Forneça exemplos de uso

### 📝 **Melhorar Documentação**
- Corrigir erros de português/inglês
- Adicionar exemplos práticos
- Traduzir para outros idiomas
- Criar tutoriais em vídeo

### 🔧 **Contribuir com Código**
- Corrigir bugs existentes
- Implementar novas funcionalidades  
- Otimizar performance
- Adicionar testes

### 🎨 **Design e UX**
- Melhorar interface do usuário
- Criar ícones e ilustrações
- Otimizar experiência mobile
- Redesign de páginas

### 🧪 **Testes e QA**
- Testar em diferentes sistemas operacionais
- Validar com datasets diversos
- Reportar problemas de performance
- Criar casos de teste automatizados

## 🚀 **Começando a Contribuir**

### 1️⃣ **Setup do Ambiente de Desenvolvimento**

```bash
# 1. Fork o repositório no GitHub
# Clique em "Fork" no repositório principal

# 2. Clone seu fork
git clone https://github.com/SEU_USERNAME/yolo-training-platform.git
cd yolo-training-platform

# 3. Adicione o repositório upstream
git remote add upstream https://github.com/rafaelmarinatoassis/yolo-training-platform.git

# 4. Configure ambiente de desenvolvimento
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# 5. Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# 6. Verifique se tudo funciona
python run.py
```

### 2️⃣ **Criar Branch para sua Contribuição**

```bash
# 1. Atualize main
git checkout main
git pull upstream main

# 2. Crie branch para sua feature
git checkout -b feature/nome-da-sua-feature

# Exemplos de nomes de branch:
git checkout -b fix/training-memory-leak
git checkout -b feature/multi-user-support  
git checkout -b docs/update-installation-guide
git checkout -b ui/improve-dashboard-layout
```

### 3️⃣ **Fazer suas Alterações**

```bash
# 1. Implemente suas mudanças
# Edite os arquivos necessários...

# 2. Teste suas alterações
python -m pytest  # Executar testes
black .           # Formatar código
flake8 app/       # Verificar estilo

# 3. Adicione novos testes se necessário
# Crie testes em tests/
```

### 4️⃣ **Commit e Push**

```bash
# 1. Adicione arquivos modificados
git add .

# 2. Commit com mensagem descritiva
git commit -m "feat: adiciona suporte a múltiplos usuários"

# 3. Push para seu fork
git push origin feature/nome-da-sua-feature
```

### 5️⃣ **Criar Pull Request**

1. **Vá para seu fork no GitHub**
2. **Clique "Compare & pull request"**  
3. **Preencha o template de PR** (descrição detalhada)
4. **Aguarde review** da equipe
5. **Faça ajustes** se solicitado
6. **Celebrate** quando merged! 🎉

## 📋 **Padrões de Desenvolvimento**

### 🎨 **Estilo de Código**

**Python:**
```python
# Use Black para formatação automática
black .

# Siga PEP 8  
flake8 app/

# Type hints sempre que possível
def process_dataset(dataset_id: int) -> dict:
    """Process dataset and return statistics."""
    pass

# Docstrings no formato Google
def train_model(config: dict) -> str:
    """Train YOLO model with given configuration.
    
    Args:
        config: Dictionary containing training parameters
        
    Returns:
        Path to trained model file
        
    Raises:
        ValueError: If config is invalid
    """
    pass
```

**JavaScript:**
```javascript
// Use ES6+ features
const trainingData = await fetch(`/api/trainings/${id}`);

// Nomes descritivos
function updateTrainingMetrics(metrics) {
    // ...
}

// Comentários explicativos
// Update chart only if training is active
if (training.status === 'running') {
    updateChart(metrics);
}
```

**HTML/CSS:**
```html
<!-- Use classes Bootstrap quando possível -->
<div class="card shadow-sm">
    <div class="card-body">
        <h5 class="card-title">Training Progress</h5>
    </div>
</div>

<!-- CSS custom com prefixo -->
<style>
.yolo-dashboard {
    /* Estilos customizados */
}
</style>
```

### 📝 **Padrões de Commit**

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Formato: tipo(escopo): descrição

# Tipos principais:
feat: nova funcionalidade
fix: correção de bug  
docs: documentação
style: formatação (sem mudança de lógica)
refactor: refatoração
test: testes
chore: manutenção

# Exemplos:
git commit -m "feat(training): add multi-GPU support"
git commit -m "fix(ui): resolve dashboard refresh issue"
git commit -m "docs(api): update training endpoint documentation"
git commit -m "style(frontend): format JavaScript files with prettier"
git commit -m "refactor(storage): simplify dataset validation logic"
git commit -m "test(models): add unit tests for Training model"
git commit -m "chore(deps): update ultralytics to 8.1.0"
```

### 🧪 **Testes**

```python
# Estrutura de testes
tests/
├── unit/           # Testes unitários
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/    # Testes de integração
│   ├── test_api.py
│   └── test_workflows.py
└── fixtures/       # Dados de teste
    ├── sample_dataset.zip
    └── mock_training.json

# Exemplo de teste unitário
def test_dataset_validation():
    """Test dataset structure validation."""
    dataset = create_test_dataset()
    result = validate_dataset_structure(dataset.path)
    assert result.is_valid is True
    assert len(result.errors) == 0

# Executar testes
pytest                    # Todos os testes
pytest tests/unit/        # Apenas unitários  
pytest -k "training"      # Testes com "training" no nome
pytest --cov=app         # Com coverage
```

### 📊 **Code Review**

**Como revisor:**
- ✅ Funcionalidade atende aos requisitos?
- ✅ Código segue padrões do projeto?
- ✅ Testes adequados foram adicionados?
- ✅ Documentação foi atualizada?
- ✅ Performance não foi prejudicada?
- ✅ Não quebra funcionalidades existentes?

**Como contribuidor:**
- ✅ Teste em múltiplos navegadores/SOs
- ✅ Inclua screenshots se mudança visual
- ✅ Atualize documentação relacionada
- ✅ Responda reviews de forma construtiva
- ✅ Faça commits pequenos e focados

## 🏗️ **Arquitetura e Contribuições**

### 🎯 **Áreas que Precisam de Ajuda**

**🔥 Alta Prioridade:**
- **Multi-user support** - Sistema de autenticação
- **API REST completa** - Endpoints para automação
- **Docker deployment** - Containerização
- **Performance optimization** - Otimizações de velocidade
- **Mobile responsiveness** - Interface mobile

**⚡ Média Prioridade:**
- **Novos modelos AI** - Support para Detectron2, EfficientDet
- **Video training** - Support para detecção em vídeos
- **Advanced metrics** - Métricas ML avançadas
- **Export formats** - ONNX, TensorRT, CoreML
- **Data augmentation** - Mais opções de augmentation

**💡 Baixa Prioridade:**
- **Internationalization** - Múltiplos idiomas
- **Themes** - Dark mode, temas customizáveis  
- **Plugins system** - Arquitetura de plugins
- **Advanced scheduling** - Agendamento de treinamentos
- **Cloud integration** - AWS, GCP, Azure

### 🔧 **Como Adicionar Nova Funcionalidade**

**1. Backend (Flask):**
```python
# 1. Criar model se necessário (app/models.py)
class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # ...

# 2. Criar service (app/services/)  
class NewService:
    def __init__(self):
        pass
    
    def new_method(self):
        pass

# 3. Criar routes (app/routes/)
@new_bp.route('/api/new', methods=['POST'])
def create_new():
    # ...
    return jsonify(result)

# 4. Registrar blueprint (app/__init__.py)
from app.routes.new import new_bp
app.register_blueprint(new_bp)
```

**2. Frontend (HTML/JS):**
```javascript
// 1. Adicionar HTML (app/templates/)
<div id="new-feature">
    <!-- Nova interface -->
</div>

// 2. Adicionar JavaScript
function handleNewFeature() {
    fetch('/api/new', {
        method: 'POST',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Atualizar UI
    });
}

// 3. Integrar com WebSocket se necessário
socket.on('new_event', function(data) {
    // Handle real-time updates
});
```

**3. Testes:**
```python
# tests/test_new_feature.py
def test_new_functionality():
    """Test new feature works correctly."""
    # Setup
    # Execute  
    # Assert
    pass
```

## 📖 **Contribuindo com Documentação**

### ✍️ **Wiki e Docs**

```bash
# 1. Clone repositório
git clone https://github.com/rafaelmarinatoassis/yolo-training-platform.git

# 2. Edite arquivos Markdown em wiki/
# wiki/
# ├── Home.md
# ├── Setup-e-Instalacao.md  
# ├── Guia-do-Usuario.md
# └── ...

# 3. Preview local (opcional)
pip install mkdocs mkdocs-material
mkdocs serve

# 4. Commit e push
git add wiki/
git commit -m "docs: update user guide with new examples"
git push
```

### 🎥 **Tutoriais em Vídeo**

Se você cria conteúdo em vídeo:

1. **Grave tutorial** usando a plataforma
2. **Publique no YouTube/Vimeo**
3. **Crie pull request** adicionando link na documentação
4. **Formate assim:**

```markdown
## 📺 Tutoriais em Vídeo

### 🚀 Início Rápido
- [Como Criar Primeiro Dataset](https://youtube.com/watch?v=xxx) (5 min)
- [Configurando Treinamento](https://youtube.com/watch?v=yyy) (8 min)

### 🎯 Avançado  
- [Otimizando Performance](https://youtube.com/watch?v=zzz) (15 min)
- [Deploy em Produção](https://youtube.com/watch?v=www) (20 min)
```

## 🏆 **Reconhecimento de Contribuidores**

### 🌟 **Hall da Fama**

Contribuidores ativos ganham reconhecimento:

- **🏆 Top Contributor** - Badge no perfil GitHub
- **📝 Mentions no README** - Nome na seção de agradecimentos
- **🎯 Project Maintainer** - Acesso de commit direto
- **🎉 Release Credits** - Menção nas release notes

### 📊 **Tipos de Contribuição**

Valorizamos **todas** as formas de contribuição:

- 💻 **Code** - Commits, pull requests
- 📝 **Documentation** - Wiki, README, comentários
- 🐛 **Bug Reports** - Issues detalhados  
- 💡 **Ideas** - Feature requests, discussões
- 🎨 **Design** - UI/UX, logos, ilustrações
- 🧪 **Testing** - QA, beta testing
- 🌍 **Community** - Responder dúvidas, mentoring
- 📢 **Promotion** - Blog posts, talks, social media

## 🛡️ **Código de Conduta**

### 🤝 **Nossos Valores**

- **Respeito** - Tratamos todos com dignidade
- **Inclusão** - Welcoming para todos os backgrounds  
- **Colaboração** - Trabalhamos juntos construtivamente
- **Aprendizado** - Todos estamos sempre aprendendo
- **Qualidade** - Buscamos excelência no que fazemos

### ❌ **Comportamentos Inaceitáveis**

- Assédio de qualquer tipo
- Linguagem ofensiva ou discriminatória
- Ataques pessoais ou trolling
- Spam ou autopromoção excessiva
- Compartilhamento de informações privadas

### 📞 **Reportar Problemas**

Se você experienciar ou testemunhar comportamento inadequado:

1. **Email**: rafael@example.com
2. **Issue privada**: Marque como confidencial
3. **Resposta garantida**: Em até 24 horas

## 📞 **Contato e Comunidade**

### 💬 **Canais de Comunicação**

- **🐛 Bugs e Issues**: [GitHub Issues](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)
- **💡 Ideias e Discussões**: [GitHub Discussions](https://github.com/rafaelmarinatoassis/yolo-training-platform/discussions)  
- **📧 Email**: rafael@example.com
- **🐦 Twitter**: @yolotrainingplatform
- **📱 Discord**: [Convite](https://discord.gg/yolo-training-platform)

### 🗓️ **Reuniões da Comunidade**

- **📅 Weekly Sync**: Terças 19h (horário de Brasília)
- **🎯 Monthly Planning**: Primeira sexta do mês
- **🚀 Release Party**: Após cada major release

### 📊 **Roadmap Público**

Acompanhe nosso progresso:
- **GitHub Projects**: [Roadmap Público](https://github.com/rafaelmarinatoassis/yolo-training-platform/projects)
- **Milestones**: [Issues organizadas por versão](https://github.com/rafaelmarinatoassis/yolo-training-platform/milestones)

## 🎉 **Primeiros Passos para Novos Contribuidores**

### 🆕 **Issues "Good First Issue"**

Procure por issues marcadas com:
- `good first issue` - Perfeito para começar
- `help wanted` - Precisamos de ajuda
- `documentation` - Melhorias na documentação
- `bug` - Bugs confirmados para corrigir

### 🏃 **Seu Primeiro Contribution**

**Sugestões fáceis para começar:**

1. **📝 Corrigir typos** na documentação
2. **🐛 Reproduzir e confirmar bugs** reportados
3. **📖 Adicionar exemplos** no guia do usuário  
4. **🧪 Escrever testes** para funções existentes
5. **🎨 Melhorar mensagens** de erro do usuário

### 🤝 **Mentoring**

**Novo no open source?** Sem problema!

- **📚 Leia**: [First Contributions Guide](https://firstcontributions.github.io/)
- **💬 Pergunte**: Marque @rafaelmarinatoassis em issues
- **🎓 Aprenda**: Oferecemos mentoring para novos contribuidores
- **🏆 Celebre**: Todo contribution é valorizado!

---

<div align="center">

**🙏 Obrigado por considerar contribuir!**

Juntos, tornamos o machine learning mais acessível para todos.

[🚀 Começar a Contribuir](https://github.com/rafaelmarinatoassis/yolo-training-platform/fork) • [💬 Tirar Dúvidas](https://github.com/rafaelmarinatoassis/yolo-training-platform/discussions) • [📖 Ler Docs](Home.md)

**Feito com ❤️ pela comunidade YOLO Training Platform**

</div>