# 🏠 YOLO Training Platform - Wiki

![YOLO Training Platform](https://img.shields.io/badge/YOLO-Training%20Platform-blue?style=for-the-badge&logo=artificial-intelligence)

Bem-vindo à documentação oficial do **YOLO Training Platform**! 🎯

Esta wiki contém toda a informação necessária para usar, configurar, desenvolver e contribuir com a plataforma de treinamento de modelos YOLO mais intuitiva do mercado.

## 📚 Índice da Documentação

### 🚀 **Para Começar**
- **[📋 Requisitos do Sistema](Requisitos-do-Sistema.md)** - Hardware e software necessários
- **[⚙️ Setup e Instalação](Setup-e-Instalacao.md)** - Guia completo de instalação
- **[🏃 Início Rápido](Inicio-Rapido.md)** - Primeiros passos em 5 minutos

### 👨‍💻 **Para Usuários**
- **[📖 Guia do Usuário](Guia-do-Usuario.md)** - Tutorial completo de uso
- **[🎯 Fluxo de Trabalho](Fluxo-de-Trabalho.md)** - Como usar a plataforma eficientemente
- **[🎨 Interface do Usuário](Interface-do-Usuario.md)** - Explicação detalhada das telas
- **[📊 Dashboard e Métricas](Dashboard-e-Metricas.md)** - Entendendo as métricas YOLO

### 🔧 **Para Desenvolvedores**
- **[🏗️ Arquitetura](Arquitetura.md)** - Estrutura do sistema
- **[📡 API Reference](API-Reference.md)** - Documentação completa da API
- **[🛠️ Configuração de Desenvolvimento](Configuracao-de-Desenvolvimento.md)** - Setup para desenvolver
- **[🧪 Testes](Testes.md)** - Como executar e criar testes

### 🆘 **Suporte**
- **[❓ FAQ](FAQ.md)** - Perguntas frequentes
- **[🐛 Solução de Problemas](Solucao-de-Problemas.md)** - Troubleshooting
- **[🔍 Logs e Debug](Logs-e-Debug.md)** - Como debugar problemas
- **[💡 Dicas e Truques](Dicas-e-Truques.md)** - Otimizações e melhores práticas

### 🤝 **Contribuição**
- **[🤲 Como Contribuir](Contribuicao.md)** - Guia para contribuidores
- **[📝 Padrões de Código](Padroes-de-Codigo.md)** - Convenções do projeto
- **[🚀 Roadmap](Roadmap.md)** - Planos futuros
- **[📜 Changelog](Changelog.md)** - Histórico de versões

## 🎯 O que é o YOLO Training Platform?

O **YOLO Training Platform** é uma aplicação web completa que simplifica todo o processo de treinamento de modelos de detecção de objetos YOLO (You Only Look Once). Desenvolvido com foco na usabilidade, oferece:

### ✨ **Características Principais**
- 🖥️ **Interface Web Moderna** - Bootstrap 5 responsivo
- ⚡ **Dashboard em Tempo Real** - Acompanhamento live de treinamentos
- 📁 **Gestão de Datasets** - Upload e validação automática
- 🔄 **WebSocket Updates** - Métricas atualizadas instantaneamente
- 📊 **Visualizações Interativas** - Gráficos Chart.js
- 🎯 **Integração YOLOv8** - Suporte completo Ultralytics
- 📚 **Métricas Educativas** - Explicações claras de Loss, mAP50, etc.

### 🛠️ **Stack Tecnológico**
- **Backend**: Flask 2.3+ (Python)
- **Frontend**: Bootstrap 5 + Chart.js
- **AI/ML**: Ultralytics YOLOv8 + PyTorch
- **Database**: SQLite (SQLAlchemy ORM)
- **Real-time**: WebSocket (SocketIO)
- **Deployment**: Gunicorn + Docker

## 🚀 **Início Rápido** 

```bash
# 1. Clone o repositório
git clone https://github.com/rafaelmarinatoassis/yolo-training-platform.git
cd yolo-training-platform

# 2. Crie ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# 3. Instale dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python run.py

# 5. Acesse http://localhost:5000
```

⏱️ **Tempo estimado**: 5-10 minutos

## 📖 **Primeiros Passos**

1. **[📋 Verifique os requisitos](Requisitos-do-Sistema.md)** - Python 3.8+, 4GB RAM
2. **[⚙️ Configure o ambiente](Setup-e-Instalacao.md)** - Instalação detalhada
3. **[📁 Crie seu primeiro dataset](Guia-do-Usuario.md#criando-datasets)** - Upload de imagens
4. **[🎯 Inicie um treinamento](Guia-do-Usuario.md#treinamento)** - Configure parâmetros
5. **[📊 Monitore o dashboard](Dashboard-e-Metricas.md)** - Acompanhe métricas

## 🆘 **Precisa de Ajuda?**

- 🐛 **Problemas técnicos**: [Solução de Problemas](Solucao-de-Problemas.md)
- ❓ **Dúvidas gerais**: [FAQ](FAQ.md)  
- 💬 **Issues no GitHub**: [Issues](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)
- 📧 **Contato**: [rafael@example.com](mailto:rafael@example.com)

## 🤝 **Contribuindo**

O YOLO Training Platform é um projeto open source! Contribuições são muito bem-vindas:

- 🐛 **Reportar bugs**: [Criar issue](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues/new)
- 💡 **Sugerir features**: [Feature request](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues/new)
- 🔧 **Contribuir código**: [Guia de contribuição](Contribuicao.md)
- 📖 **Melhorar documentação**: Editar esta wiki

## 🏆 **Projetos em Destaque**

Veja alguns projetos incríveis criados com o YOLO Training Platform:

- 🚗 **Detecção de Veículos** - Sistema de monitoramento de tráfego
- 🏥 **Análise Médica** - Detecção de anomalias em imagens
- 🏭 **Controle de Qualidade** - Inspeção automatizada industrial
- 🔒 **Segurança** - Sistema de detecção de intrusão

## 📈 **Estatísticas do Projeto**

- ⭐ **Stars no GitHub**: ![Stars](https://img.shields.io/github/stars/rafaelmarinatoassis/yolo-training-platform)
- 🍴 **Forks**: ![Forks](https://img.shields.io/github/forks/rafaelmarinatoassis/yolo-training-platform)
- 📊 **Issues**: ![Issues](https://img.shields.io/github/issues/rafaelmarinatoassis/yolo-training-platform)
- 🔄 **Pull Requests**: ![PRs](https://img.shields.io/github/issues-pr/rafaelmarinatoassis/yolo-training-platform)
- 📅 **Última atualização**: ![Last Commit](https://img.shields.io/github/last-commit/rafaelmarinatoassis/yolo-training-platform)

---

<div align="center">

**📚 Esta documentação é mantida pela comunidade**

[🔗 Editar esta página](https://github.com/rafaelmarinatoassis/yolo-training-platform/edit/main/wiki/Home.md) • [📝 Contribuir](Contribuicao.md) • [🐛 Reportar erro](https://github.com/rafaelmarinatoassis/yolo-training-platform/issues)

**Feito com ❤️ pela comunidade YOLO Training Platform**

</div>