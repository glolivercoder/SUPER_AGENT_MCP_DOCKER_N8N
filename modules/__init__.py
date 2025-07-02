# Módulos do SUPER_AGENT_MCP_DOCKER_N8N
"""
Pacote de módulos para o agente especialista SUPER_AGENT_MCP_DOCKER_N8N.

Módulos disponíveis:
- mcp_rag_module: Módulo principal MCP com capacidades RAG
- mcp_client: Cliente para comunicação MCP com IDEs
"""

from .mcp_rag_module import MCPRAGModule, create_app, run_server
from .mcp_client import MCPClient, IDEIntegration, ClineIntegration, HTTPMCPClient
from .openrouter_manager import OpenRouterManager, quick_task

__version__ = "1.0.0"
__all__ = [
    "MCPRAGModule",
    "MCPClient", 
    "IDEIntegration",
    "ClineIntegration",
    "HTTPMCPClient",
    "OpenRouterManager",
    "create_app",
    "run_server",
    "quick_task"
] 