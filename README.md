# 🚀 SUPER_AGENT_MCP_DOCKER_N8N

## Agente Especialista Multiplataforma

**SUPER_AGENT_MCP_DOCKER_N8N** é um agente especialista que integra e coordena Model Context Protocols (MCPs) para diferentes IDEs de código (Cline, RooCline, Windsurf, Cursor), utilizando modelos da API OpenRouter e especializado em Docker, N8N, Playwright/Puppeteer e deploys em produção.

## ✨ Características Principais

- **🎯 Módulo GUI**: Interface gráfica completa para monitoramento e gerenciamento
- **🧠 Módulo MCP RAG**: Sistema de Retrieval-Augmented Generation com protocolo MCP
- **🔌 Integração IDE**: Suporte nativo para Cline, RooCline, Windsurf e Cursor
- **📊 Monitoramento**: Sistema completo de logs, métricas e status em tempo real
- **🐳 Docker Ready**: Especialização em containerização e deploy
- **🔄 N8N Integration**: Automação de workflows
- **🎭 Web Automation**: Playwright e Puppeteer integrados
- **📚 RAG Inteligente**: Busca e recuperação de contexto em documentos

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- Git
- 4GB RAM mínimo (8GB recomendado)
- Sistema operacional: Windows, Linux ou macOS

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd SUPER_AGENT_MCP_DOCKER_N8N
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Instale Node.js (necessário para MCPs)**
```bash
# Ubuntu/Debian
sudo apt-get install nodejs npm

# macOS
brew install node

# Windows
# Baixe do site oficial nodejs.org
```

4. **Configure variáveis de ambiente**
```bash
# OBRIGATÓRIO - Para o OpenRouter Agent
export OPENROUTER_API_KEY=sua_chave_openrouter

# OPCIONAIS - Para funcionalidades extras
export OPENAI_API_KEY=sua_chave_openai
export ANTHROPIC_API_KEY=sua_chave_anthropic
```

5. **Configure o projeto**
```bash
# Verifica se tudo está configurado
python start_super_agent.py --status
```

6. **Inicie o sistema**
```bash
python start_super_agent.py
```

7. **Teste o OpenRouter Agent**
```bash
python example_openrouter_usage.py
```

## 🚀 Uso Rápido

### Inicialização Completa

```bash
# Inicia com GUI e servidor MCP
python start_super_agent.py

# Inicia apenas o servidor MCP (sem GUI)
python start_super_agent.py --no-gui

# Inicia apenas a GUI (sem servidor MCP)
python start_super_agent.py --no-mcp

# Customiza host e porta
python start_super_agent.py --host 0.0.0.0 --port 8080

# Verifica status dos serviços
python start_super_agent.py --status
```

### Usando o Módulo MCP RAG Diretamente

```python
import asyncio
from modules.mcp_client import HTTPMCPClient

async def exemplo_rag():
    async with HTTPMCPClient() as client:
        # Verifica se o serviço está ativo
        health = await client.health_check()
        print("Status:", health)
        
        # Inicializa o módulo
        await client.initialize_module()
        
        # Processa documentos
        result = await client.process_documents()
        print("Documentos processados:", result)
        
        # Faz consulta RAG
        query_result = await client.query_rag_http("Como usar Docker?")
        print("Resposta:", query_result["response"])

# Executa o exemplo
asyncio.run(exemplo_rag())
```

### Interface Gráfica

A GUI fornece 4 abas principais:

- **📊 Dashboard**: Métricas do sistema em tempo real (CPU, memória, disk)
- **⚙️ Módulos**: Controle dos módulos MCP RAG (iniciar/parar/status)
- **📝 Logs**: Visualização, filtro e exportação de logs
- **🔧 Configurações**: Ajustes de MCP, RAG e sistema

## 📁 Estrutura do Projeto

```
SUPER_AGENT_MCP_DOCKER_N8N/
├── GUI/                          # Interface gráfica
│   └── gui_module_manager_fe.py  # Gerenciador principal da GUI
├── modules/                      # Módulos principais
│   ├── mcp_rag_module.py        # Módulo MCP RAG completo
│   ├── mcp_client.py            # Cliente MCP para IDEs
│   └── __init__.py              # Inicialização do pacote
├── config/                       # Configurações
│   ├── mcp_config.json          # Configuração do MCP RAG
│   └── app_config.json          # Configuração da aplicação
├── documents/                    # Documentos para indexação RAG
├── data/                        # Dados e banco vetorial
├── logs/                        # Logs do sistema
├── start_super_agent.py         # Script principal de inicialização
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## ⚙️ Configuração

### Configuração do MCP RAG (`config/mcp_config.json`)

```json
{
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "vector_db_path": "./data/vectordb",
  "documents_path": "./documents",
  "mcp_host": "localhost",
  "mcp_port": 8000,
  "chunk_size": 500,
  "chunk_overlap": 50,
  "max_contexts": 10,
  "supported_extensions": [".txt", ".md", ".py", ".js", ".json", ".yaml", ".yml", ".dockerfile", ".ts", ".jsx", ".tsx"]
}
```

### Configuração da Aplicação (`config/app_config.json`)

```json
{
  "mcp_host": "localhost",
  "mcp_port": 8000,
  "gui_enabled": true,
  "auto_start_mcp": true,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "docs_directory": "./documents"
}
```

## 🔌 Integração com IDEs

### Integração com Cline

```python
from modules.mcp_client import MCPClient, ClineIntegration

async def integrar_com_cline():
    client = MCPClient()
    await client.connect()
    
    cline = ClineIntegration(client)
    
    # Melhora resposta do Cline com contexto RAG
    enhanced_response = await cline.enhance_cline_response(
        "Como implementar autenticação JWT?",
        "Projeto FastAPI com autenticação"
    )
    
    print(enhanced_response)
    await client.disconnect()
```

### WebSocket MCP para IDEs

```javascript
// Cliente JavaScript para integração com IDEs
const ws = new WebSocket('ws://localhost:8000/mcp');

ws.onopen = function() {
    // Inicializa módulo
    ws.send(JSON.stringify({
        id: "1",
        method: "initialize",
        params: {}
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Resposta MCP:', response);
};

// Exemplo de consulta RAG
function queryRAG(query) {
    ws.send(JSON.stringify({
        id: Date.now().toString(),
        method: "query",
        params: {
            query: query,
            top_k: 5,
            context_window: 2000
        }
    }));
}
```

## 📊 API Endpoints

### Servidor MCP RAG

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Verificação de saúde do serviço |
| `/initialize` | POST | Inicializa o módulo MCP RAG |
| `/process_documents` | POST | Processa documentos para indexação |
| `/query` | POST | Realiza consulta RAG |
| `/mcp` | WebSocket | Comunicação MCP em tempo real |

### Exemplo de Consulta RAG via HTTP

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Como usar Docker Compose com volumes?",
       "top_k": 5,
       "context_window": 2000
     }'
```

### Resposta da API

```json
{
  "query": "Como usar Docker Compose com volumes?",
  "response": "Baseado nos documentos encontrados...",
  "contexts": [
    {
      "content": "Conteúdo relevante do documento...",
      "metadata": {
        "filename": "docker-guide.md",
        "filepath": "./documents/docker-guide.md"
      },
      "similarity": 0.87,
      "rank": 1
    }
  ],
  "total_contexts": 3
}
```

## 🧪 Desenvolvimento e Testes

### Executar Testes

```bash
pytest tests/ -v
```

### Formatação de Código

```bash
# Formatação automática
black modules/ GUI/

# Verificação de estilo
flake8 modules/ GUI/
```

### Adicionar Novos Documentos

1. **Coloque arquivos em `./documents/`**
   - Formatos suportados: `.txt`, `.md`, `.py`, `.js`, `.json`, `.yaml`, `.dockerfile`, `.ts`, `.jsx`, `.tsx`

2. **Processe via GUI**
   - Acesse: Módulos → "Processar Documentos"

3. **Processe via API**
```python
import asyncio
from modules.mcp_client import HTTPMCPClient

async def processar_documentos():
    async with HTTPMCPClient() as client:
        result = await client.process_documents()
        print(f"✅ Processados: {result['documents_processed']} documentos")

asyncio.run(processar_documentos())
```

## 🐳 Deploy com Docker

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . .

# Cria diretórios
RUN mkdir -p documents data logs config

# Porta do serviço
EXPOSE 8000

# Comando de inicialização
CMD ["python", "start_super_agent.py", "--no-gui", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  super-agent:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./documents:/app/documents
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    restart: unless-stopped

  # Opcional: N8N para automação
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - super-agent

volumes:
  n8n_data:
```

### Build e Execução

```bash
# Build da imagem
docker build -t super-agent .

# Execução simples
docker run -p 8000:8000 super-agent

# Execução com volumes
docker run -p 8000:8000 \
  -v $(pwd)/documents:/app/documents \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  super-agent

# Usando Docker Compose
docker-compose up -d
```

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Dependências
```bash
# Atualiza pip e reinstala dependências
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Porta em Uso
```bash
# Usa porta diferente
python start_super_agent.py --port 8001

# Verifica quais portas estão em uso
netstat -tlnp | grep :8000
```

#### 3. Modelo de Embedding Não Carrega
- ✅ Verifica conexão com internet
- ✅ Espaço em disco (modelos ~500MB)
- ✅ Reinicia o serviço

#### 4. GUI Não Inicia (Linux)
```bash
# Instala tkinter
sudo apt-get install python3-tk

# Verifica se funciona
python -c "import tkinter; print('✅ tkinter OK')"
```

#### 5. Permissões de Arquivo
```bash
# Linux/macOS
chmod +x start_super_agent.py

# Cria diretórios se necessário
mkdir -p documents data logs config
```

### Verificação do Sistema

```bash
# Status completo
python start_super_agent.py --status

# Teste de dependências
python -c "
try:
    import fastapi, uvicorn, sentence_transformers, chromadb
    print('✅ Dependências principais OK')
except ImportError as e:
    print(f'❌ Erro: {e}')
"

# Teste de memória disponível
python -c "
import psutil
mem = psutil.virtual_memory()
print(f'💾 Memória: {mem.available//1024//1024//1024}GB disponível')
print(f'📊 Uso: {mem.percent}%')
"
```

### Logs Importantes

```bash
# Log principal do sistema
tail -f logs/super_agent.log

# Log do módulo MCP RAG
tail -f logs/mcp_rag.log

# Logs em tempo real (se usando journald)
journalctl -f -u super-agent
```

## 🤖 OpenRouter Agent Manager

### Agente Inteligente com MCPs Dinâmicos

O **OpenRouter Agent Manager** é o coração inteligente do sistema, capaz de gerenciar MCPs automaticamente baseado no contexto dos prompts.

#### Funcionalidades Principais

- **🧠 Análise Inteligente**: Analisa prompts e sugere MCPs apropriados
- **🔄 Gestão Dinâmica**: Inicia/para MCPs conforme necessidade
- **🔌 Multi-MCP**: Suporta MCPs de diferentes categorias
- **🚀 Integração OpenRouter**: Acesso a vários LLMs via API unificada

#### MCPs Suportados

| Categoria | MCP | Descrição | Comando |
|-----------|-----|-----------|---------|
| **Arquitetura** | Filesystem | Gerencia arquivos/diretórios | `@modelcontextprotocol/server-filesystem` |
| **Arquitetura** | Git | Operações Git | `@modelcontextprotocol/server-git` |
| **Arquitetura** | GitHub | API GitHub | `@modelcontextprotocol/server-github` |
| **IDE** | Cursor | Controle oficial Cursor | `@cursor/mcp-server` |
| **IDE** | VSCode | Integração VSCode | `@vscode/mcp-server` |
| **Design** | Figma | Design e prototipação | `@figma/mcp-server` |
| **Design** | 21dev | Ferramentas visuais | `@21-dev/mcp-server` |
| **DevOps** | Docker | Containers e images | `@docker/mcp-server` |
| **Testing** | Playwright | Automação web | `@modelcontextprotocol/server-playwright` |
| **API** | Airbnb | Busca acomodações | `@openbnb/mcp-server-airbnb` |
| **Memory** | SuperMemory | Memórias de interfaces | `supergateway --sse <endpoint>` |

#### Configuração do OpenRouter

1. **Obtenha sua API Key**
   - Acesse [OpenRouter.ai](https://openrouter.ai)
   - Crie uma conta e gere sua API key

2. **Configure a variável de ambiente**
```bash
export OPENROUTER_API_KEY=sua_chave_aqui
```

3. **Instale Node.js** (necessário para MCPs NPX)
```bash
# Ubuntu/Debian
sudo apt-get install nodejs npm

# macOS
brew install node

# Windows
# Baixe do site oficial nodejs.org
```

#### Uso Básico

```python
import asyncio
from modules.openrouter_manager import OpenRouterManager

async def exemplo():
    manager = OpenRouterManager()
    
    # O agente analisa o prompt e escolhe MCPs apropriados
    result = await manager.process_prompt(
        "Liste os arquivos Python e faça commit das mudanças"
    )
    
    print(f"MCPs usados: {result['started_mcps']}")
    print(f"Resposta: {result['response']}")
    
    await manager.shutdown()

# Executa
asyncio.run(exemplo())
```

#### Função Utilitária Rápida

```python
from modules.openrouter_manager import quick_task

# Para tarefas rápidas
response = await quick_task("Verifique o status do Git")
print(response)
```

#### Interface GUI

O agente está integrado na interface gráfica:

1. **Inicie o sistema**
```bash
python start_super_agent.py
```

2. **Na aba "Módulos"**:
   - Clique em "Iniciar OpenRouter Agent"
   - Configure OPENROUTER_API_KEY se necessário
   - Use os controles para gerenciar MCPs

#### Exemplos de Prompts Inteligentes

```python
# Exemplo completo de uso
prompts = [
    "Liste arquivos e verifique status Git",  # Usa: filesystem + git
    "Abra projeto no Cursor e rode testes",   # Usa: cursor + playwright
    "Crie interface Figma e export assets",  # Usa: figma
    "Build Docker image e deploy",            # Usa: docker + git
    "Busque hotéis em Paris no Airbnb"       # Usa: airbnb
]

for prompt in prompts:
    result = await manager.process_prompt(prompt)
    print(f"Prompt: {prompt}")
    print(f"MCPs: {result['needed_mcps']}")
```

#### Análise Automática de Prompts

O agente usa palavras-chave para identificar MCPs necessários:

- **"arquivo", "file", "diretório"** → `filesystem`
- **"git", "commit", "branch"** → `git`
- **"cursor", "ide"** → `cursor`
- **"figma", "design", "ui"** → `figma`
- **"docker", "container"** → `docker`
- **"browser", "test", "automation"** → `playwright`
- **"memória", "memory", "lembrar", "interface"** → `supermemory`

#### SuperMemory MCP - Gestão de Memórias

O **SuperMemory MCP** é um sistema avançado que armazena memórias de todas as interfaces em um ambiente único, baseado na [documentação oficial](https://supermemory.ai/docs/supermemory-mcp/introduction).

**Características:**
- 🧠 **Memória Persistente**: Armazena contexto entre sessões
- 🔗 **Multi-Interface**: Unifica memórias de diferentes interfaces
- 🚀 **Acesso Rápido**: Recuperação instantânea de contextos
- 🔄 **Sincronização**: Mantém dados atualizados em tempo real

**Instalação:**
```bash
# Instalação automática via npx
npx install-mcp https://mcp.supermemory.ai/2ubE0qTwMtbd9dYC_fetX/sse --client claude

# Verificar instalação no Claude Desktop config
cat "$env:APPDATA\Claude\claude_desktop_config.json"
```

**Uso com OpenRouter Agent:**
```python
# Prompts que ativam SuperMemory automaticamente
prompts = [
    "Lembre desta configuração para próximas sessões",
    "Armazene na memória: projeto usa FastAPI + ChromaDB",
    "Recall das interfaces utilizadas anteriormente",
    "Contexto do histórico de comandos executados"
]

for prompt in prompts:
    result = await manager.process_prompt(prompt)
    # SuperMemory será automaticamente ativado
```

#### Execução de Exemplo

```bash
# Execute o exemplo completo
python example_openrouter_usage.py
```

#### Modelos OpenRouter Suportados

| Provider | Modelo | Descrição |
|----------|---------|-----------|
| OpenAI | `openai/gpt-4` | Modelo principal (padrão) |
| Google | `google/gemini-2.0-flash-exp:free` | Modelo gratuito rápido |
| Anthropic | `anthropic/claude-3-haiku` | Claude rápido |
| Meta | `meta-llama/llama-3.1-8b-instruct:free` | Llama gratuito |

#### Fallbacks Automáticos

O sistema inclui fallbacks automáticos:

1. Tenta modelo principal (`gpt-4`)
2. Se falhar, tenta modelos gratuitos
3. Se API não configurada, funciona localmente
4. Se MCP falhar, continua com outros

#### Monitoramento de MCPs

```python
# Verificar status
status = manager.get_status()
print(f"MCPs ativos: {status['active_mcps']}")
print(f"API configurada: {status['api_configured']}")

# Listar MCPs disponíveis
available = manager.mcps_registry
for name, info in available.items():
    print(f"{name}: {info['description']}")
```

## 📈 Monitoramento e Métricas

### Dashboard da GUI

A interface gráfica fornece:

- **📊 CPU, Memória, Disco**: Métricas em tempo real
- **🔄 Status dos Módulos**: Estado de cada serviço
- **📝 Logs Centralizados**: Todos os logs em uma interface
- **⚙️ Configuração Dinâmica**: Ajustes sem reiniciar

### API de Health Check

```bash
# Verifica saúde do serviço
curl http://localhost:8000/health

# Resposta esperada
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Métricas de Performance

```python
# Exemplo de monitoramento custom
import asyncio
from modules.mcp_client import HTTPMCPClient

async def monitor_performance():
    async with HTTPMCPClient() as client:
        import time
        start = time.time()
        
        result = await client.query_rag_http("Test query")
        
        end = time.time()
        print(f"⏱️ Tempo de resposta: {end-start:.2f}s")
        print(f"📄 Contextos encontrados: {len(result.get('contexts', []))}")

asyncio.run(monitor_performance())
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork o projeto**
2. **Crie uma branch** (`git checkout -b feature/nova-feature`)
3. **Commit suas mudanças** (`git commit -am 'Adiciona nova feature'`)
4. **Push para a branch** (`git push origin feature/nova-feature`)
5. **Abra um Pull Request**

### Padrões de Código

- **Python**: PEP 8, type hints quando possível
- **Documentação**: Docstrings em português
- **Commits**: Mensagens descritivas em português
- **Testes**: Sempre adicione testes para novas funcionalidades

### Estrutura de Commits

```
feat: adiciona nova funcionalidade X
fix: corrige problema Y
docs: atualiza documentação Z
style: formatação de código
refactor: refatora módulo W
test: adiciona testes para V
```

## 📝 Roadmap

### Versão 1.1 (Próxima)
- [ ] Integração completa com OpenRouter API
- [ ] Suporte a mais modelos de embedding
- [ ] Plugin system para IDEs
- [ ] API de webhooks

### Versão 1.2
- [ ] Interface web moderna (React/Vue)
- [ ] Suporte a múltiplos idiomas
- [ ] Clustering de documentos
- [ ] Métricas avançadas

### Versão 2.0
- [ ] Suporte a múltiplos tenants
- [ ] Integração com Kubernetes
- [ ] IA conversacional avançada
- [ ] Marketplace de plugins

## 📞 Suporte

- **🐛 Issues**: Use o sistema de issues do GitHub
- **📚 Documentação**: Consulte este README e comentários no código
- **📋 Logs**: Sempre inclua logs relevantes em relatórios de bugs
- **💬 Discussões**: Use GitHub Discussions para perguntas

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara do problema.

**Como Reproduzir**
1. Execute comando X
2. Acesse Y
3. Observe erro Z

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente**
- OS: [Windows 10, Ubuntu 20.04, etc.]
- Python: [3.8, 3.9, 3.10]
- Versão: [1.0.0]

**Logs**
```
Inclua logs relevantes aqui
```
```

---

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**SUPER_AGENT_MCP_DOCKER_N8N** - Desenvolvido com ❤️ para automação e produtividade de desenvolvedores.

🚀 **Versão Atual**: 1.0.0  
📅 **Última Atualização**: Janeiro 2024  
👥 **Maintainers**: Equipe de Desenvolvimento 

## Análise OpenMemory + OpenRouter

### ✅ Compatibilidade Confirmada

O **OpenMemory** é totalmente compatível com a **API OpenRouter**! A análise realizada mostra que:

- **OpenMemory usa OpenAI como provider padrão**
- **OpenRouter implementa a mesma API da OpenAI**
- **Basta configurar `api_base` e `api_key` para usar OpenRouter**

### 🔧 Configuração OpenRouter como Padrão

Para usar OpenRouter como backend padrão no OpenMemory:

```env
OPENAI_API_KEY=sk-...sua-chave-openrouter...
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

Ou via configuração JSON:

```json
{
  "mem0": {
    "llm": {
      "provider": "openai",
      "config": {
        "model": "gpt-4o-mini",
        "api_key": "sk-...sua-chave-openrouter...",
        "api_base": "https://openrouter.ai/api/v1"
      }
    },
    "embedder": {
      "provider": "openai", 
      "config": {
        "model": "text-embedding-3-small",
        "api_key": "sk-...sua-chave-openrouter...",
        "api_base": "https://openrouter.ai/api/v1"
      }
    }
  }
}
```

### 📋 MCPs Integrados

#### Padrão (OpenRouter):
- **OpenMemory MCP** - Sistema de memória unificado
- **Filesystem MCP** - Gerenciamento de arquivos
- **Git MCP** - Controle de versão
- **Cursor MCP** - Integração com IDE
- **Figma MCP** - Design e prototipagem
- **Docker MCP** - Containerização
- **Playwright MCP** - Testes automatizados
- **Airbnb MCP** - APIs e integrações

#### Opcional:
- **SuperMemory MCP** - Unificação de memórias entre interfaces