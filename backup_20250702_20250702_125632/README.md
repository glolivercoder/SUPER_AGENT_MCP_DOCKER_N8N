# SUPER_AGENT_MCP_DOCKER_N8N

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open Source](https://img.shields.io/badge/Open%20Source-100%25-brightgreen.svg)](https://opensource.org/)
[![Speech-to-Text](https://img.shields.io/badge/Speech--to--Text-Offline-orange.svg)](https://github.com/alphacep/vosk-api)

> **Agente especializado em integração MCPs, Docker/N8N, RAG avançado e comandos Git por voz - 100% gratuito e opensource**

## 🚀 Visão Geral

O SUPER_AGENT_MCP_DOCKER_N8N é um agente inteligente que integra MCPs (Model Context Protocols) de diferentes IDEs, gerencia Docker/N8N, oferece sistema RAG avançado com documentações técnicas e permite comandos Git por voz em português - tudo usando apenas bibliotecas gratuitas e opensource.

## ✨ Funcionalidades Principais

### 🤖 Integração MCP Completa
- **Suporte a múltiplas IDEs**: Cursor, Cline, Windsurf, RooCline
- **Configuração automática** de servidores MCP
- **Compartilhamento** de configurações entre IDEs
- **Detecção automática** de IDEs instalados

### 🐳 Gerenciamento Docker & N8N
- **Controle de contêineres** Docker
- **Deploy automático** de serviços N8N
- **Monitoramento** de status dos contêineres
- **Configuração via interface gráfica**

### 📚 Sistema RAG Avançado
- **Documentações técnicas integradas**: Git, Docker, N8N, MCP Servers, Kubernetes
- **Tecnologias de Cloud**: Cloudflare Workers, DigitalOcean, Oracle Free Tier
- **Processamento multi-formato**: PDF, TXT, MD, DOCX, HTML, JSON, URLs
- **Busca rápida**: Índice otimizado para acesso instantâneo
- **Cache inteligente**: Sistema de cache para documentos frequentes

### 🌐 Integração OpenRouter
- **Catálogo completo**: Acesso a TODOS os modelos LLM da OpenRouter
- **Filtros avançados**: Por empresa, modelos gratuitos, contexto
- **Interface intuitiva**: Seleção visual com informações detalhadas
- **Teste com RAG**: Interface para testar modelos usando contexto

### 🗣️ Fê Agent (Speech-to-Text) - 100% OPENSOURCE
- **Bibliotecas gratuitas**: Vosk, Coqui STT, PocketSphinx
- **Comandos Git por voz**: "Fê, fazer commit e push", "Fê, status"
- **Reconhecimento offline**: Funciona sem internet ou APIs pagas
- **Wake words**: ["fê", "fe", "hey fê", "Super Agent"]
- **TTS gratuito**: pyttsx3 para síntese de voz local

### 🖥️ Interface Gráfica Moderna
- **OpenRouter GUI**: Interface dedicada para seleção e teste de modelos LLM
- **RAG Management**: Upload de documentos, busca, visualização de estatísticas
- **Interface Tkinter** com tema moderno e dark mode
- **Monitoramento em tempo real**: Logs, estatísticas, status dos serviços

## 🛠️ Tecnologias Utilizadas

### Speech-to-Text & TTS (100% Gratuito)
- **[Vosk](https://alphacephei.com/vosk/)**: Reconhecimento offline de alta qualidade
- **[Coqui STT](https://stt.readthedocs.io/)**: Engine opensource da Mozilla
- **[PocketSphinx](https://cmusphinx.github.io/)**: CMU Sphinx toolkit
- **[pyttsx3](https://pypi.org/project/pyttsx3/)**: Text-to-speech local

### RAG & Processamento
- **PyPDF2**: Processamento de PDFs
- **python-docx**: Processamento de documentos Word
- **BeautifulSoup4**: Extração de conteúdo web
- **NLTK & spaCy**: Processamento de linguagem natural

### APIs & Integrações
- **OpenRouter API**: Acesso a todos os modelos LLM
- **GitHub API**: Carregamento de repositórios
- **Docker API**: Controle de contêineres

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Docker Desktop
- Git
- Microfone (para comandos de voz)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N.git
cd SUPER_AGENT_MCP_DOCKER_N8N

# 2. Instale as dependências (100% gratuitas)
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
export OPENROUTER_API_KEY="your-api-key-here"  # Opcional

# 4. Execute o agente
python main.py
```

## 🎯 Como Usar

### Comandos de Voz do Fê Agent

```bash
# Comandos Git disponíveis
"Fê, fazer status"                    # git status
"Fê, commit e push"                   # git add . && git commit && git push
"Fê, commit 'mensagem' e push"        # commit com mensagem personalizada
"Fê, analisar projeto"                # análise completa do projeto
"Fê, ajuda"                          # lista todos os comandos
```

### Wake Words Configurados
```python
WAKE_WORDS = ["fê", "fe", "hey fê", "Super Agent"]
```

### OpenRouter Integration

```python
# Configurar API key
export OPENROUTER_API_KEY="your-api-key-here"

# Usar via interface
from GUI.openrouter_gui import OpenRouterGUI
gui = OpenRouterGUI()
gui.run()
```

### Sistema RAG

```python
from modules.advanced_rag_system import AdvancedRAGSystem
rag = AdvancedRAGSystem()

# Buscar na base de conhecimento
results = rag.search_knowledge("docker container commands")

# Query com contexto usando OpenRouter
answer = rag.query_with_context(
    question="Como criar um Dockerfile?",
    model_id="openai/gpt-4",
    context_docs=["docker_doc_id"]
)
```

## 📚 Documentações Integradas

### Tecnologias Core
- **Git**: Comandos, workflows, branching, resolução de conflitos, hooks
- **Docker**: Containers, images, Dockerfile, Docker Compose, Swarm, networking
- **N8N**: Workflows, nodes, automação, deployment, integrações
- **MCP Servers**: Protocol, configuração, desenvolvimento, debugging

### Tecnologias de Deploy e Cloud
- **Kubernetes**: Pods, services, deployments, ingress, storage
- **Cloudflare Workers**: Edge computing, KV storage, Durable Objects
- **DigitalOcean**: Droplets, App Platform, Kubernetes, Spaces
- **Oracle Cloud Free Tier**: Compute, storage, networking, database

## 🏗️ Arquitetura

```
SUPER_AGENT_MCP_DOCKER_N8N/
├── config/                    # Configurações
│   ├── cursor_mcp_config.json
│   ├── docker_config.json
│   ├── fe_agent_config.json
│   └── voice_config.json
├── data/                      # Dados do sistema RAG
│   └── docs/                  # Documentações técnicas
├── modules/                   # Módulos principais
│   ├── __init__.py
│   ├── mcp_manager.py        # Gerenciamento MCP
│   ├── docker_manager.py     # Gerenciamento Docker
│   ├── advanced_rag_system.py # Sistema RAG
│   ├── fe_agent.py           # Fê Agent (Speech-to-Text)
│   └── voice_module.py       # Módulo de voz
├── GUI/                       # Interface gráfica
│   ├── __init__.py
│   ├── gui_module.py         # Interface principal
│   └── openrouter_gui.py     # Interface OpenRouter
├── logs/                      # Logs do sistema
├── temp/                      # Scripts temporários e protótipos
│   ├── temp_docker_manager.py
│   ├── temp_gui_module.py
│   ├── temp_main.py
│   ├── temp_mcp_manager.py
│   └── temp_rag_system.py
├── tests/                     # Testes automatizados e scripts de teste
│   └── test_fe_agent.py
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências (100% gratuitas)
├── README.md                  # Esta documentação
├── .gitignore                 # Arquivos ignorados pelo Git
├── CHANGELOG.md               # Histórico de mudanças
├── GITHUB_SETUP.md            # Instruções de setup do GitHub
├── gui_main.py                # Inicializador da interface gráfica
├── mcp_manager.py             # Gerenciamento MCP (atalho)
├── MEMORIES.json              # Memória persistente
├── rag_system.py              # Sistema RAG (atalho)
├── SUPER_AGENT_MCP_DOCKER_N8N.md # Documentação extra
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# OpenRouter (opcional)
export OPENROUTER_API_KEY="your-api-key-here"

# Docker
export DOCKER_HOST="unix:///var/run/docker.sock"

# N8N
export N8N_PORT=5678
export N8N_HOST=localhost
```

### Configuração de Voz

```json
{
  "voice_enabled": true,
  "wake_words": ["fê", "fe", "hey fê", "Super Agent"],
  "tts_engine": "pyttsx3",
  "stt_engine": "vosk",
  "language": "pt-BR"
}
```

## 🎨 Interface Gráfica

### Screenshots

- **Interface Principal**: Controle de todos os módulos
- **OpenRouter GUI**: Seleção e teste de modelos LLM
- **RAG Management**: Upload e busca de documentos
- **Docker Manager**: Controle de contêineres

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia as diretrizes:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Mantenha o código 100% opensource e gratuito
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Siga as convenções de código Python (PEP 8)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **[Vosk](https://alphacephei.com/vosk/)**: Reconhecimento de voz offline
- **[Coqui STT](https://stt.readthedocs.io/)**: Speech-to-text opensource
- **[OpenRouter](https://openrouter.ai/)**: Acesso a modelos LLM
- **[N8N](https://n8n.io/)**: Automação de workflows
- **[Docker](https://www.docker.com/)**: Containerização

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N/wiki)
- **Email**: seu-email@exemplo.com

## 🚀 Roadmap

### Versão 0.2.0
- [ ] Integração com mais IDEs
- [ ] Sistema de plugins
- [ ] API REST
- [ ] Deploy em nuvem

### Versão 0.3.0
- [ ] Machine Learning para análise de prompts
- [ ] Integração com Copilot
- [ ] Sistema de recomendações
- [ ] Analytics avançados

### Versão 1.0.0
- [ ] Versão estável para produção
- [ ] Documentação completa
- [ ] Testes automatizados
- [ ] Deploy package

---

**Desenvolvido com ❤️ para a comunidade de desenvolvedores - 100% gratuito e opensource!**

[![GitHub stars](https://img.shields.io/github/stars/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N.svg?style=social&label=Star)](https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N)
[![GitHub forks](https://img.shields.io/github/forks/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N.svg?style=social&label=Fork)](https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N/fork)
[![GitHub issues](https://img.shields.io/github/issues/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N.svg)](https://github.com/seu-usuario/SUPER_AGENT_MCP_DOCKER_N8N/issues) 