# SUPER_AGENT_MCP_DOCKER_N8N

## Visão Geral

O SUPER_AGENT_MCP_DOCKER_N8N é um agente especializado projetado para integrar MCPs (Model Context Protocols) de diferentes IDEs como Cline, RooCline, Windsurf e Cursor. O agente coordena o armazenamento de comandos usados pelos MCPs, inicia serviços no diretório do projeto, analisa prompts para determinar a melhor arquitetura. Agora com sistema RAG avançado, integração OpenRouter e bibliotecas 100% gratuitas/opensource para speech-to-text e TTS.

## Funcionalidades Principais

### 1. Integração de MCPs
- **Suporte a múltiplas IDEs**: Cline, RooCline, Windsurf, Cursor
- **Compartilhamento de configurações** entre IDEs
- **Detecção automática** de MCPs instalados
- **Sincronização** de configurações e dados

### 2. Gerenciamento de Docker
- **Controle de contêineres** Docker
- **Deploy automático** de serviços N8N
- **Configuração via interface gráfica**
- **Monitoramento** de status dos contêineres

### 3. Sistema RAG Avançado (Retrieval Augmented Generation)
- **Documentações Técnicas Pré-carregadas**: Git, Docker, N8N, MCP Servers, Kubernetes, Cloud Deploy
- **Processamento Multi-formato**: PDF, TXT, MD, DOCX, HTML, JSON, URLs
- **Busca Rápida**: Índice otimizado com palavras-chave para acesso instantâneo
- **Cache Inteligente**: Sistema de cache para URLs e documentos frequentes
- **Integração GitHub**: Carregamento de repositórios e documentações

### 4. Integração OpenRouter
- **Catálogo Completo**: Acesso a TODOS os modelos LLM da OpenRouter
- **Filtros Avançados**: Dropdown por empresa, filtro de modelos gratuitos
- **Interface Intuitiva**: Seleção visual com informações de contexto e preços
- **Teste com RAG**: Interface para testar modelos usando contexto da base de conhecimento
- **Modelos Gratuitos**: Botão para mostrar apenas modelos sem custo

### 5. Fê Agent (Speech-to-Text) - 100% OPENSOURCE
- **Bibliotecas Gratuitas**: Vosk, Coqui STT, PocketSphinx (removidas dependências pagas)
- **Comandos Git por voz**: "Fê, fazer commit e push", "Fê, status", "Fê, analisar projeto"
- **Reconhecimento offline**: Funciona sem internet ou APIs pagas
- **Wake words**: ["fê", "fe", "hey fê", "Super Agent"]
- **TTS Gratuito**: pyttsx3 para síntese de voz local

### 6. Módulo de Voz Opensource
- **Síntese local**: pyttsx3 sem dependências cloud
- **Múltiplos engines**: SAPI, eSpeak, festival
- **Processamento offline**: Sem envio de dados para terceiros
- **Configuração flexível**: Velocidade, pitch, voz

### 7. Interface Gráfica Moderna
- **OpenRouter GUI**: Interface dedicada para seleção e teste de modelos LLM
- **RAG Management**: Upload de documentos, busca, visualização de estatísticas
- **Interface Tkinter** com tema moderno e dark mode
- **Abas organizadas**: MCPs, Docker, RAG, OpenRouter, Configurações
- **Monitoramento em tempo real**: Logs, estatísticas, status dos serviços

## Arquitetura do Sistema

### Estrutura de Diretórios

```
SUPER_AGENT_MCP_DOCKER_N8N/
├── config/                    # Configurações
│   ├── cursor_mcp_config.json
│   ├── docker_config.json
│   ├── faith_agent_config.json
│   └── voice_config.json
├── data/                      # Dados do sistema RAG
│   ├── documents.json
│   └── memories/
├── logs/                      # Logs do sistema
├── modules/                   # Módulos principais
│   ├── __init__.py
│   ├── mcp_manager.py
│   ├── docker_manager.py
│   ├── rag_system.py
│   ├── faith_agent.py
│   └── voice_module.py
├── GUI/                       # Interface gráfica
│   ├── __init__.py
│   └── gui_module.py
├── MEMORIES.json              # Sistema de memória
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências
└── README.md                  # Documentação básica
```

### Componentes Principais

#### 1. MCPManager
- Gerencia configurações de MCPs
- Detecta IDEs instaladas
- Compartilha configurações entre IDEs
- Monitora status dos MCPs

#### 2. DockerManager
- Controla contêineres Docker
- Gerencia deploy de N8N
- Configura volumes e redes
- Monitora recursos

#### 3. RAGSystem
- Processa documentos
- Mantém índice de busca
- Integra com GitHub
- Gerencia memórias

#### 4. FaithAgent
- Analisa prompts com perspectiva cristã
- Oferece orientação espiritual
- Integra versículos bíblicos
- Mantém diário de orações

#### 5. VoiceModule
- Sintetiza voz para respostas
- Reconhece comandos de voz
- Processa áudio em tempo real
- Suporta múltiplas vozes

## Sistema de Memória

O arquivo `MEMORIES.json` mantém o contexto persistente do agente:

```json
{
  "version": "1.0.0",
  "last_update": "2025-01-07T15:00:00Z",
  "user_preferences": {
    "default_ide": "cursor",
    "voice_enabled": true,
    "faith_mode": true,
    "theme": "dark"
  },
  "project_memories": [
    {
      "id": "proj_001",
      "name": "SUPER_AGENT_MCP_DOCKER_N8N",
      "description": "Agente principal para integração MCP",
      "created_at": "2025-01-07T10:00:00Z",
      "technologies": ["Python", "Docker", "N8N", "Tkinter"],
      "commands_used": [],
      "mcps_configured": []
    }
  ],
  "commands_history": [],
  "faith_memories": {
    "prayers": [],
    "verses_referenced": [],
    "spiritual_guidance": []
  },
  "voice_preferences": {
    "voice_model": "azure_neural",
    "speed": 1.0,
    "pitch": 0.0
  }
}
```

## Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- Docker Desktop
- Git
- Tkinter (geralmente incluído no Python)

## Documentações RAG Integradas

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

### Processamento de Documentos
- **Formatos Suportados**: PDF, TXT, MD, DOCX, HTML, JSON
- **URLs**: Extração automática de conteúdo web
- **GitHub**: Carregamento direto de repositórios e documentações
- **Cache**: Sistema inteligente para acesso rápido

### Dependências Python (100% Gratuitas)
```
requests>=2.28.0
pathlib>=1.0.1
python-dotenv>=1.0.0
# Speech-to-Text e TTS GRATUITOS/OPENSOURCE
pyttsx3>=2.90
speech-recognition>=3.10.0
vosk>=0.3.45
coqui-stt>=1.4.0
pocketsphinx>=5.0.3
pyaudio>=0.2.11
# RAG e processamento de documentos
pypdf2>=3.0.1
python-docx>=0.8.11
beautifulsoup4>=4.12.0
markdown>=3.5.0
# OpenRouter API integration
openai>=1.0.0
# Processamento de texto avançado
nltk>=3.8.0
spacy>=3.7.0
```

### Instalação
1. Clone o repositório
2. Instale dependências: `pip install -r requirements.txt`
3. Configure Docker
4. Execute: `python main.py`

## Uso Avançado

### Comandos de Voz do Fê Agent

#### Comandos Git Disponíveis
- **"Fê, fazer status"** - Executa `git status`
- **"Fê, commit e push"** - Workflow completo: `git add .` → `git commit` → `git push`
- **"Fê, commit 'mensagem' e push"** - Commit com mensagem personalizada
- **"Fê, analisar projeto"** - Análise completa do projeto com git log e estrutura
- **"Fê, ajuda"** - Lista todos os comandos disponíveis

#### Wake Words Configurados
```python
WAKE_WORDS = ["fê", "fe", "hey fê", "Super Agent"]
```

### OpenRouter Integration

#### Configuração da API
```python
# Variável de ambiente necessária
export OPENROUTER_API_KEY="your-api-key-here"

# Uso programático
from modules.advanced_rag_system import AdvancedRAGSystem
rag = AdvancedRAGSystem()
models = rag.get_openrouter_models()
```

#### Filtros Disponíveis
- **Por Empresa**: OpenAI, Anthropic, Google, Meta, Cohere, etc.
- **Modelos Gratuitos**: Filtro para mostrar apenas modelos sem custo
- **Por Contexto**: Tamanho da janela de contexto (tokens)
- **Busca por Nome**: Filtro de texto para encontrar modelos específicos

### Comandos Principais

1. **Iniciar Sistema RAG**:
   ```python
   from modules.advanced_rag_system import AdvancedRAGSystem
   rag = AdvancedRAGSystem()
   
   # Carregar documentações
   rag.add_document("path/to/doc.pdf", "documentation")
   rag.add_url_content("https://docs.docker.com", "docker")
   ```

2. **Buscar na Base de Conhecimento**:
   ```python
   # Busca rápida
   results = rag.search_knowledge("docker container commands")
   
   # Query com contexto usando OpenRouter
   answer = rag.query_with_context(
       question="Como criar um Dockerfile?",
       model_id="openai/gpt-4",
       context_docs=["docker_doc_id"]
   )
   ```

3. **Interface OpenRouter**:
   ```python
   from GUI.openrouter_gui import OpenRouterGUI
   gui = OpenRouterGUI()
   gui.run()  # Interface para seleção e teste de modelos
   ```

4. **Configurar MCP**:
   ```python
   from modules.mcp_manager import MCPManager
   manager = MCPManager()
   manager.detect_installed_mcps()
   ```

5. **Gerenciar Docker**:
   ```python
   from modules.docker_manager import DockerManager
   docker = DockerManager()
   docker.start_n8n()
   ```

### Integração com APIs

- **OpenRouter API**: Acesso a TODOS os modelos LLM disponíveis
- **GitHub API**: Para carregar repositórios e documentações  
- **APIs locais**: Speech-to-text e TTS 100% offline (Vosk, Coqui STT, pyttsx3)

## Módulos Especializados

### Fê Agent (Speech-to-Text para Git)

O Fê Agent oferece controle por voz 100% gratuito e offline:
- Comandos Git por voz em português
- Reconhecimento offline (sem internet)
- Múltiplos engines opensource disponíveis
- Workflow completo de Git automatizado

#### Bibliotecas Utilizadas:
- **Vosk**: Reconhecimento offline de alta qualidade
- **Coqui STT**: Engine opensource da Mozilla  
- **PocketSphinx**: CMU Sphinx toolkit
- **SpeechRecognition**: Interface unificada
- **pyttsx3**: Text-to-speech local

#### Comandos Disponíveis:
```python
VOICE_COMMANDS = {
    "status": ["status", "fazer status", "git status"],
    "commit_push": ["commit e push", "comitar e enviar"],
    "commit_msg_push": ["commit (.+) e push"],
    "analyze": ["analisar projeto", "análise"],
    "help": ["ajuda", "comandos", "help"]
}
```

### Advanced RAG System

O sistema RAG oferece acesso rápido a documentações técnicas:
- **Base de conhecimento**: Git, Docker, N8N, MCP, Kubernetes, Cloud
- **Processamento multi-formato**: PDF, MD, DOCX, HTML, URLs
- **Busca otimizada**: Índice de palavras-chave para acesso instantâneo
- **OpenRouter Integration**: Teste de modelos com contexto

#### Funcionalidades:
- **Document Processing**: Extração inteligente de conteúdo
- **URL Scraping**: Carregamento automático de documentações web
- **GitHub Integration**: Acesso direto a repositórios
- **Smart Caching**: Cache de documentos frequentes

### Voice Module Opensource

O módulo de voz utiliza apenas bibliotecas gratuitas:
- **Síntese local**: pyttsx3 sem dependências cloud
- **Engines disponíveis**: SAPI (Windows), eSpeak (Linux), nsss (macOS)
- **Configuração flexível**: Velocidade, pitch, volume
- **Processamento offline**: Sem envio de dados para terceiros

## Integração com IDEs

### Cursor
- Localização: `%APPDATA%\Cursor\mcps`
- Configuração automática
- Sync de extensões

### Cline
- Localização: `~/.config/cline/mcps`
- Compartilhamento de configs
- Backup automático

### Windsurf
- Configuração personalizada
- Integração com projetos
- Sync de workspace

### RooCline
- Setup automático
- Configuração de shortcuts
- Integração com Git

## Troubleshooting

### Problemas Comuns

1. **Docker não encontrado**:
   - Verificar instalação do Docker Desktop
   - Confirmar se Docker está no PATH

2. **MCPs não detectados**:
   - Verificar permissões de acesso
   - Confirmar IDEs instaladas

3. **Problemas de voz**:
   - Verificar drivers de áudio
   - Confirmar microfone funcionando

4. **Erros de memória**:
   - Verificar arquivo MEMORIES.json
   - Confirmar permissões de escrita

## Roadmap

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

## Contribuição

Para contribuir com o projeto:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## Licença

MIT License - veja arquivo LICENSE para detalhes.

## Suporte

Para suporte:
- Abra uma issue no GitHub
- Entre em contato via email
- Consulte a documentação oficial

---

*Desenvolvido com fé e dedicação para a comunidade de desenvolvedores.* 