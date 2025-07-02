# MCP Client - SUPER_AGENT_MCP_DOCKER_N8N
"""
Cliente MCP para comunicação com IDEs (Cline, RooCline, Windsurf, Cursor)
e integração com o módulo RAG.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable
import websockets
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class MCPClient:
    """Cliente para comunicação via Model Context Protocol"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.websocket = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
    async def connect(self) -> bool:
        """Conecta ao servidor MCP"""
        try:
            uri = f"ws://{self.host}:{self.port}/mcp"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # Inicia task para receber mensagens
            asyncio.create_task(self._message_receiver())
            
            # Inicializa o módulo
            await self.initialize()
            
            logger.info(f"Conectado ao servidor MCP em {uri}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor MCP: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta do servidor MCP"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Desconectado do servidor MCP")
    
    async def _message_receiver(self):
        """Recebe mensagens do servidor"""
        try:
            while self.is_connected:
                message = await self.websocket.recv()
                data = json.loads(message)
                await self._handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            logger.info("Conexão MCP fechada")
        except Exception as e:
            logger.error(f"Erro ao receber mensagem: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Processa mensagem recebida"""
        message_id = data.get("id")
        
        # Se é uma resposta a uma requisição pendente
        if message_id and message_id in self.pending_requests:
            future = self.pending_requests.pop(message_id)
            if "error" in data:
                future.set_exception(Exception(data["error"]["message"]))
            else:
                future.set_result(data.get("result"))
        
        # Se é uma notificação ou mensagem não solicitada
        elif "method" in data:
            method = data["method"]
            if method in self.message_handlers:
                await self.message_handlers[method](data)
    
    async def send_request(self, method: str, params: Optional[Dict] = None, timeout: float = 30.0) -> Any:
        """Envia requisição e aguarda resposta"""
        if not self.is_connected:
            raise Exception("Cliente não está conectado")
        
        message_id = str(uuid.uuid4())
        message = {
            "id": message_id,
            "method": method,
            "params": params or {}
        }
        
        # Cria future para aguardar resposta
        future = asyncio.Future()
        self.pending_requests[message_id] = future
        
        try:
            # Envia mensagem
            await self.websocket.send(json.dumps(message))
            
            # Aguarda resposta com timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            self.pending_requests.pop(message_id, None)
            raise Exception(f"Timeout na requisição {method}")
        except Exception as e:
            self.pending_requests.pop(message_id, None)
            raise e
    
    async def initialize(self) -> Dict[str, Any]:
        """Inicializa o módulo MCP RAG"""
        return await self.send_request("initialize")
    
    async def query_rag(self, query: str, top_k: int = 5, context_window: int = 2000) -> Dict[str, Any]:
        """Realiza consulta RAG"""
        params = {
            "query": query,
            "top_k": top_k,
            "context_window": context_window
        }
        return await self.send_request("query", params)
    
    async def process_documents(self) -> Dict[str, Any]:
        """Processa documentos para indexação"""
        return await self.send_request("process_documents")
    
    async def get_status(self) -> Dict[str, Any]:
        """Obtém status do módulo"""
        return await self.send_request("get_status")
    
    def register_handler(self, method: str, handler: Callable):
        """Registra handler para método específico"""
        self.message_handlers[method] = handler

class IDEIntegration:
    """Integração específica para IDEs"""
    
    def __init__(self, ide_type: str, mcp_client: MCPClient):
        self.ide_type = ide_type
        self.mcp_client = mcp_client
        self.context_cache: Dict[str, Any] = {}
        
    async def provide_context(self, file_path: str, cursor_position: int = 0) -> str:
        """Fornece contexto relevante para o arquivo atual"""
        try:
            # Lê conteúdo do arquivo atual
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrai contexto ao redor do cursor
            lines = content.split('\n')
            cursor_line = cursor_position
            
            # Pega contexto local (5 linhas antes e depois)
            start_line = max(0, cursor_line - 5)
            end_line = min(len(lines), cursor_line + 5)
            local_context = '\n'.join(lines[start_line:end_line])
            
            # Monta query para RAG baseada no contexto local
            query = f"Contexto do arquivo {file_path}:\n{local_context}"
            
            # Consulta RAG para contexto relacionado
            rag_result = await self.mcp_client.query_rag(query, top_k=3)
            
            # Formata resposta
            context = f"""
=== CONTEXTO LOCAL ({file_path}) ===
{local_context}

=== CONTEXTO RELACIONADO ===
{rag_result['response']}
"""
            
            return context
            
        except Exception as e:
            logger.error(f"Erro ao fornecer contexto: {e}")
            return f"Erro ao obter contexto: {e}"
    
    async def suggest_completion(self, partial_code: str, file_type: str) -> List[str]:
        """Sugere completions baseados no contexto RAG"""
        try:
            query = f"Sugestões de código para {file_type}: {partial_code}"
            rag_result = await self.mcp_client.query_rag(query, top_k=3)
            
            # Extrai sugestões dos contextos encontrados
            suggestions = []
            for context in rag_result['contexts']:
                # Processa contexto para extrair sugestões relevantes
                content = context['content']
                if partial_code.lower() in content.lower():
                    # Adiciona linhas relevantes como sugestões
                    lines = content.split('\n')
                    for line in lines:
                        if partial_code.lower() in line.lower() and line.strip():
                            suggestions.append(line.strip())
            
            return suggestions[:5]  # Retorna top 5 sugestões
            
        except Exception as e:
            logger.error(f"Erro ao sugerir completion: {e}")
            return []
    
    async def explain_error(self, error_message: str, code_context: str) -> str:
        """Explica erro baseado no contexto do projeto"""
        try:
            query = f"Erro: {error_message}\nCódigo: {code_context}"
            rag_result = await self.mcp_client.query_rag(query, top_k=5)
            
            explanation = f"""
=== ANÁLISE DO ERRO ===
Erro: {error_message}

=== CONTEXTOS RELACIONADOS ===
{rag_result['response']}

=== SUGESTÕES DE SOLUÇÃO ===
Baseado nos documentos do projeto, verifique:
1. Dependências e imports
2. Configurações similares em outros arquivos
3. Padrões de uso no projeto
"""
            
            return explanation
            
        except Exception as e:
            logger.error(f"Erro ao explicar erro: {e}")
            return f"Não foi possível analisar o erro: {e}"

class ClineIntegration(IDEIntegration):
    """Integração específica para Cline"""
    
    def __init__(self, mcp_client: MCPClient):
        super().__init__("cline", mcp_client)
    
    async def enhance_cline_response(self, user_query: str, project_context: str) -> str:
        """Melhora resposta do Cline com contexto RAG"""
        enhanced_query = f"Pergunta do usuário: {user_query}\nContexto do projeto: {project_context}"
        rag_result = await self.mcp_client.query_rag(enhanced_query)
        
        return f"""
{rag_result['response']}

--- Contextos do projeto utilizados ---
{len(rag_result['contexts'])} documentos relevantes consultados.
"""

class HTTPMCPClient:
    """Cliente HTTP para comunicação com o módulo MCP RAG"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.base_url = f"http://{host}:{port}"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do serviço"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def initialize_module(self) -> Dict[str, Any]:
        """Inicializa módulo via HTTP"""
        async with self.session.post(f"{self.base_url}/initialize") as response:
            return await response.json()
    
    async def process_documents(self) -> Dict[str, Any]:
        """Processa documentos via HTTP"""
        async with self.session.post(f"{self.base_url}/process_documents") as response:
            return await response.json()
    
    async def query_rag_http(self, query: str, top_k: int = 5, context_window: int = 2000) -> Dict[str, Any]:
        """Realiza consulta RAG via HTTP"""
        payload = {
            "query": query,
            "top_k": top_k,
            "context_window": context_window
        }
        async with self.session.post(f"{self.base_url}/query", json=payload) as response:
            return await response.json()

# Funções utilitárias para facilitar uso
async def quick_rag_query(query: str, host: str = "localhost", port: int = 8000) -> str:
    """Função utilitária para consulta RAG rápida"""
    async with HTTPMCPClient(host, port) as client:
        result = await client.query_rag_http(query)
        return result.get("response", "Sem resposta disponível")

async def initialize_mcp_rag(host: str = "localhost", port: int = 8000) -> bool:
    """Função utilitária para inicializar módulo RAG"""
    try:
        async with HTTPMCPClient(host, port) as client:
            health = await client.health_check()
            if health.get("status") == "healthy":
                await client.initialize_module()
                return True
        return False
    except Exception as e:
        logger.error(f"Erro ao inicializar MCP RAG: {e}")
        return False

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        # Teste de conexão WebSocket
        client = MCPClient()
        if await client.connect():
            
            # Teste de consulta
            result = await client.query_rag("Como usar Docker?")
            print("Resultado RAG:", result)
            
            # Teste de status
            status = await client.get_status()
            print("Status:", status)
            
            await client.disconnect()
        
        # Teste de cliente HTTP
        async with HTTPMCPClient() as http_client:
            health = await http_client.health_check()
            print("Health check:", health)
    
    asyncio.run(main()) 