# MCP Servers Documentation para RAG

## Model Context Protocol (MCP)

### O que é MCP?
O Model Context Protocol (MCP) é um protocolo aberto que permite integração seamless entre aplicações AI e diversas fontes de dados e ferramentas. Desenvolvido pela Anthropic, facilita a comunicação entre clientes AI (como Claude Desktop, IDEs) e servidores de contexto.

### Componentes Principais
- **MCP Clients**: Aplicações que consomem contexto (Claude Desktop, Cursor, Cline)
- **MCP Servers**: Provedores de contexto e ferramentas
- **Protocol**: Especificação de comunicação entre cliente e servidor
- **Transports**: Métodos de comunicação (stdio, HTTP, WebSocket)

## Configuração de MCP Servers

### Claude Desktop Configuration
Arquivo de configuração: `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/db"
      }
    },
    "browser": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

### Cursor Configuration
Arquivo: `cursor_mcp_config.json`

```json
{
  "mcp": {
    "servers": {
      "supermemory": {
        "command": "node",
        "args": ["/path/to/supermemory/mcp-server.js"],
        "env": {
          "SUPERMEMORY_API_KEY": "your-api-key"
        }
      },
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/allowed/path"],
        "env": {}
      }
    }
  }
}
```

## MCP Servers Disponíveis

### Core Servers (Oficiais)

#### 1. Filesystem Server
```bash
npx -y @modelcontextprotocol/server-filesystem /allowed/directory
```
**Funcionalidades:**
- Leitura de arquivos e diretórios
- Escrita de arquivos (se permitido)
- Navegação de estrutura de pastas
- Busca de arquivos

**Configuração de Segurança:**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/safe/directory"],
    "env": {
      "FILESYSTEM_READONLY": "true"
    }
  }
}
```

#### 2. Git Server
```bash
npx -y @modelcontextprotocol/server-git /repository/path
```
**Funcionalidades:**
- Status do repositório
- Histórico de commits
- Diferenças entre arquivos
- Informações de branches

#### 3. Postgres Server
```bash
npx -y @modelcontextprotocol/server-postgres
```
**Variáveis de Ambiente:**
- `POSTGRES_CONNECTION_STRING`: String de conexão
- `POSTGRES_SCHEMA`: Schema padrão (opcional)

**Funcionalidades:**
- Consultas SQL
- Listagem de tabelas e schemas
- Metadados de banco

#### 4. Puppeteer Server (Browser)
```bash
npx -y @modelcontextprotocol/server-puppeteer
```
**Funcionalidades:**
- Navegação web automatizada
- Screenshots de páginas
- Extração de conteúdo HTML
- Interação com elementos

#### 5. SQLite Server
```bash
npx -y @modelcontextprotocol/server-sqlite /path/to/database.db
```
**Funcionalidades:**
- Consultas SQLite
- Backup de database
- Análise de schema

### Community Servers

#### 1. Supermemory MCP Server
```json
{
  "supermemory": {
    "command": "node",
    "args": ["/path/to/supermemory-mcp/dist/index.js"],
    "env": {
      "SUPERMEMORY_BASE_URL": "https://supermemory.ai",
      "SUPERMEMORY_API_KEY": "your-key"
    }
  }
}
```

#### 2. Docker MCP Server
```json
{
  "docker": {
    "command": "python",
    "args": ["/path/to/docker-mcp-server.py"],
    "env": {
      "DOCKER_HOST": "unix:///var/run/docker.sock"
    }
  }
}
```

#### 3. AWS MCP Server
```json
{
  "aws": {
    "command": "python",
    "args": ["-m", "aws_mcp_server"],
    "env": {
      "AWS_PROFILE": "default",
      "AWS_REGION": "us-east-1"
    }
  }
}
```

## Desenvolvimento de MCP Servers

### Estrutura Básica
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server(
  {
    name: 'my-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {}
    }
  }
);

// Definir tools
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'my_tool',
        description: 'Descrição da ferramenta',
        inputSchema: {
          type: 'object',
          properties: {
            param: { type: 'string' }
          }
        }
      }
    ]
  };
});

// Implementar tool
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'my_tool') {
    return {
      content: [
        {
          type: 'text',
          text: `Resultado: ${args.param}`
        }
      ]
    };
  }
});

// Iniciar servidor
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Python MCP Server
```python
import asyncio
from mcp import McpServer, types
from mcp.server.stdio import stdio_server

app = McpServer("my-python-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="python_tool",
            description="Ferramenta Python",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string"}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "python_tool":
        result = exec(arguments["code"])
        return [types.TextContent(type="text", text=str(result))]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

## MCP Resources

### Definindo Resources
```typescript
// Listar resources
server.setRequestHandler('resources/list', async () => {
  return {
    resources: [
      {
        uri: 'file:///example.txt',
        name: 'Example File',
        description: 'Um arquivo de exemplo',
        mimeType: 'text/plain'
      }
    ]
  };
});

// Ler resource
server.setRequestHandler('resources/read', async (request) => {
  const { uri } = request.params;
  
  if (uri === 'file:///example.txt') {
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: 'Conteúdo do arquivo'
        }
      ]
    };
  }
});
```

## MCP Tools

### Tool Categories

#### File Operations
```typescript
{
  name: 'read_file',
  description: 'Lê conteúdo de um arquivo',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Caminho do arquivo' }
    },
    required: ['path']
  }
}
```

#### Database Operations
```typescript
{
  name: 'execute_query',
  description: 'Executa consulta SQL',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Consulta SQL' },
      params: { type: 'array', description: 'Parâmetros da consulta' }
    },
    required: ['query']
  }
}
```

#### Web Operations
```typescript
{
  name: 'fetch_url',
  description: 'Busca conteúdo de URL',
  inputSchema: {
    type: 'object',
    properties: {
      url: { type: 'string', format: 'uri' },
      method: { type: 'string', enum: ['GET', 'POST'] },
      headers: { type: 'object' }
    },
    required: ['url']
  }
}
```

## Configuração Multiplataforma

### Windows
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx.cmd",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\allowed\\path"],
      "env": {}
    }
  }
}
```

### macOS/Linux
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
      "env": {}
    }
  }
}
```

## Debugging MCP Servers

### Logs do Cliente
```bash
# Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/mcp*.log

# Claude Desktop logs (Windows)
tail -f "%APPDATA%\Claude\logs\mcp*.log"
```

### Teste Manual
```bash
# Testar servidor MCP manualmente
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | node mcp-server.js
```

### Debug Mode
```json
{
  "mcpServers": {
    "debug-server": {
      "command": "node",
      "args": ["--inspect", "mcp-server.js"],
      "env": {
        "DEBUG": "mcp:*"
      }
    }
  }
}
```

## Segurança

### Boas Práticas
- Validar todas as entradas de usuário
- Usar princípio do menor privilégio
- Não expor credenciais em logs
- Implementar rate limiting
- Sanitizar paths de arquivo

### Validação de Input
```typescript
function validatePath(path: string): boolean {
  // Verificar se o path está dentro do diretório permitido
  const allowedDir = '/safe/directory';
  const resolvedPath = require('path').resolve(path);
  return resolvedPath.startsWith(allowedDir);
}
```

## Exemplo: MCP Server Completo

### Package.json
```json
{
  "name": "custom-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.4.0"
  },
  "bin": {
    "custom-mcp-server": "./dist/index.js"
  }
}
```

### Implementação
```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import fs from 'fs/promises';
import path from 'path';

class CustomMCPServer {
  private server: Server;
  
  constructor() {
    this.server = new Server(
      {
        name: 'custom-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {}
        }
      }
    );
    
    this.setupHandlers();
  }
  
  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler('tools/list', async () => {
      return {
        tools: [
          {
            name: 'list_files',
            description: 'Lista arquivos em um diretório',
            inputSchema: {
              type: 'object',
              properties: {
                directory: { 
                  type: 'string', 
                  description: 'Diretório para listar' 
                }
              },
              required: ['directory']
            }
          }
        ]
      };
    });
    
    // Handle tool calls
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;
      
      if (name === 'list_files') {
        try {
          const files = await fs.readdir(args.directory);
          return {
            content: [
              {
                type: 'text',
                text: `Arquivos em ${args.directory}:\n${files.join('\n')}`
              }
            ]
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `Erro: ${error.message}`
              }
            ],
            isError: true
          };
        }
      }
      
      throw new Error(`Ferramenta desconhecida: ${name}`);
    });
  }
  
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }
}

// Iniciar servidor
const server = new CustomMCPServer();
server.run().catch(console.error);
```

## Integração com IDEs

### VS Code Extension
```json
{
  "contributes": {
    "configuration": {
      "properties": {
        "mcp.servers": {
          "type": "object",
          "description": "Configuração de servidores MCP"
        }
      }
    }
  }
}
```

### Cursor Integration
```typescript
// cursor-mcp-integration.ts
interface CursorMCPConfig {
  servers: Record<string, {
    command: string;
    args: string[];
    env?: Record<string, string>;
  }>;
}

export class CursorMCPManager {
  private config: CursorMCPConfig;
  
  constructor(configPath: string) {
    this.loadConfig(configPath);
  }
  
  private async loadConfig(configPath: string) {
    const content = await fs.readFile(configPath, 'utf-8');
    this.config = JSON.parse(content);
  }
  
  async startServers() {
    for (const [name, serverConfig] of Object.entries(this.config.servers)) {
      await this.startServer(name, serverConfig);
    }
  }
}
``` 