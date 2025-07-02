# OpenRouter Agent Manager - SUPER_AGENT_MCP_DOCKER_N8N
"""
Agente OpenRouter que gerencia todos os módulos MCP dinamicamente.
Instala, configura e controla MCPs baseado nas necessidades dos prompts.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import requests
import yaml

# Importações para agentes
try:
    from praisonaiagents import Agent, MCP
    PRAISON_AVAILABLE = True
except ImportError:
    PRAISON_AVAILABLE = False
    print("PraisonAI não disponível. Usando implementação própria.")

logger = logging.getLogger(__name__)

class MCPRegistry:
    """Registry de MCPs disponíveis e suas configurações"""
    
    def __init__(self):
        self.mcps = {
            # MCPs de Arquitetura de Código
            "filesystem": {
                "name": "Filesystem MCP",
                "category": "architecture",
                "command": "npx -y @modelcontextprotocol/server-filesystem",
                "description": "Gerencia arquivos e diretórios do projeto",
                "capabilities": ["read_file", "write_file", "list_directory", "create_directory"],
                "auto_install": True
            },
            "git": {
                "name": "Git MCP", 
                "category": "architecture",
                "command": "npx -y @modelcontextprotocol/server-git",
                "description": "Controla operações Git",
                "capabilities": ["git_status", "git_commit", "git_branch", "git_log"],
                "auto_install": True
            },
            "github": {
                "name": "GitHub MCP",
                "category": "architecture", 
                "command": "npx -y @modelcontextprotocol/server-github",
                "description": "Integração com GitHub API",
                "capabilities": ["create_issue", "list_repos", "create_pr"],
                "requires_token": True
            },
            
            # MCPs Gráficos/Design
            "figma": {
                "name": "Figma MCP",
                "category": "design",
                "command": "npx -y @figma/mcp-server",
                "description": "Integração com Figma para design",
                "capabilities": ["get_design", "export_assets", "create_frame"],
                "requires_token": True
            },
            "21dev": {
                "name": "21dev MCP",
                "category": "design",
                "command": "npx -y @21-dev/mcp-server",
                "description": "Ferramentas de desenvolvimento visual",
                "capabilities": ["generate_ui", "create_component"],
                "auto_install": False
            },
            
            # MCPs de IDE
            "cursor": {
                "name": "Cursor Official MCP",
                "category": "ide",
                "command": "npx -y @cursor/mcp-server",
                "description": "Controle oficial do Cursor IDE",
                "capabilities": ["open_file", "run_command", "get_selection"],
                "auto_install": True
            },
            "vscode": {
                "name": "VSCode MCP",
                "category": "ide", 
                "command": "npx -y @vscode/mcp-server",
                "description": "Integração com VSCode",
                "capabilities": ["open_workspace", "run_task", "install_extension"],
                "auto_install": False
            },
            
            # MCPs Especializados
            "docker": {
                "name": "Docker MCP",
                "category": "devops",
                "command": "npx -y @docker/mcp-server",
                "description": "Gerenciamento de containers Docker",
                "capabilities": ["list_containers", "build_image", "run_container"],
                "auto_install": True
            },
            "playwright": {
                "name": "Playwright MCP",
                "category": "testing",
                "command": "npx -y @modelcontextprotocol/server-playwright",
                "description": "Automação web com Playwright",
                "capabilities": ["navigate", "click", "screenshot"],
                "auto_install": True
            },
            "airbnb": {
                "name": "Airbnb MCP",
                "category": "api",
                "command": "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",
                "description": "Busca acomodações no Airbnb",
                "capabilities": ["airbnb_search"],
                "auto_install": False
            }
        }
        
        self.active_mcps: Dict[str, subprocess.Popen] = {}
        self.mcp_configs = {}
    
    def get_mcps_by_category(self, category: str) -> Dict[str, Dict]:
        """Retorna MCPs de uma categoria específica"""
        return {k: v for k, v in self.mcps.items() if v["category"] == category}
    
    def get_mcp_for_task(self, task_description: str) -> List[str]:
        """Sugere MCPs baseado na descrição da tarefa"""
        task_lower = task_description.lower()
        suggested_mcps = []
        
        # Palavras-chave para diferentes MCPs
        keywords = {
            "filesystem": ["arquivo", "diretório", "pasta", "ler", "escrever", "file", "directory"],
            "git": ["git", "commit", "branch", "repositório", "repo", "version"],
            "github": ["github", "issue", "pull request", "pr"],
            "figma": ["figma", "design", "ui", "interface"],
            "docker": ["docker", "container", "image", "dockerfile"],
            "playwright": ["browser", "web", "automation", "teste", "test"],
            "cursor": ["cursor", "ide", "editor"],
            "vscode": ["vscode", "visual studio code"]
        }
        
        for mcp_name, words in keywords.items():
            if any(word in task_lower for word in words):
                suggested_mcps.append(mcp_name)
        
        return suggested_mcps

class OpenRouterAgentManager:
    """Gerenciador principal do agente OpenRouter com MCPs"""
    
    def __init__(self, openrouter_api_key: str = None):
        self.api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key é obrigatória")
        
        self.registry = MCPRegistry()
        self.current_agent = None
        self.session_history = []
        
        # Configurações padrão
        self.default_model = "openai/gpt-4"
        self.fallback_models = [
            "openrouter/google/gemini-2.0-flash-exp:free",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
        
        logger.info("OpenRouter Agent Manager inicializado")
    
    async def analyze_prompt_and_suggest_mcps(self, prompt: str) -> Dict[str, Any]:
        """Analisa o prompt e sugere MCPs necessários"""
        suggested_mcps = self.registry.get_mcp_for_task(prompt)
        
        analysis = {
            "original_prompt": prompt,
            "suggested_mcps": suggested_mcps,
            "categories_needed": [],
            "auto_install_mcps": [],
            "requires_tokens": []
        }
        
        for mcp_name in suggested_mcps:
            mcp_info = self.registry.mcps.get(mcp_name, {})
            category = mcp_info.get("category", "unknown")
            
            if category not in analysis["categories_needed"]:
                analysis["categories_needed"].append(category)
            
            if mcp_info.get("auto_install", False):
                analysis["auto_install_mcps"].append(mcp_name)
            
            if mcp_info.get("requires_token", False):
                analysis["requires_tokens"].append(mcp_name)
        
        return analysis
    
    async def install_mcp(self, mcp_name: str) -> bool:
        """Instala um MCP específico"""
        if mcp_name not in self.registry.mcps:
            logger.error(f"MCP {mcp_name} não encontrado no registry")
            return False
        
        mcp_info = self.registry.mcps[mcp_name]
        command = mcp_info["command"]
        
        try:
            logger.info(f"Instalando MCP {mcp_name}...")
            
            # Para MCPs NPX, não precisamos instalar, apenas executar
            if command.startswith("npx"):
                logger.info(f"MCP {mcp_name} será executado sob demanda")
                return True
            
            # Para outros tipos de MCP, execute instalação específica
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"MCP {mcp_name} instalado com sucesso")
                return True
            else:
                logger.error(f"Erro ao instalar MCP {mcp_name}: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao instalar MCP {mcp_name}: {e}")
            return False
    
    async def start_mcp(self, mcp_name: str) -> bool:
        """Inicia um MCP específico"""
        if mcp_name in self.registry.active_mcps:
            logger.info(f"MCP {mcp_name} já está ativo")
            return True
        
        mcp_info = self.registry.mcps.get(mcp_name)
        if not mcp_info:
            logger.error(f"MCP {mcp_name} não encontrado")
            return False
        
        try:
            command = mcp_info["command"].split()
            logger.info(f"Iniciando MCP {mcp_name} com comando: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Verifica se o processo iniciou corretamente
            time.sleep(1)
            if process.poll() is None:  # Processo ainda rodando
                self.registry.active_mcps[mcp_name] = process
                logger.info(f"MCP {mcp_name} iniciado com sucesso (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"MCP {mcp_name} falhou ao iniciar: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar MCP {mcp_name}: {e}")
            return False
    
    async def stop_mcp(self, mcp_name: str) -> bool:
        """Para um MCP específico"""
        if mcp_name not in self.registry.active_mcps:
            logger.info(f"MCP {mcp_name} não está ativo")
            return True
        
        try:
            process = self.registry.active_mcps[mcp_name]
            process.terminate()
            
            # Aguarda até 5 segundos para término gracioso
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"MCP {mcp_name} foi forçado a parar")
            
            del self.registry.active_mcps[mcp_name]
            logger.info(f"MCP {mcp_name} parado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar MCP {mcp_name}: {e}")
            return False
    
    def create_agent_with_mcps(self, mcps: List[str], instructions: str = None) -> Any:
        """Cria agente PraisonAI com MCPs específicos"""
        if not PRAISON_AVAILABLE:
            logger.error("PraisonAI não está disponível")
            return None
        
        # Instruções padrão se não fornecidas
        if not instructions:
            instructions = f"""
            Você é um assistente especializado em desenvolvimento de software.
            Você tem acesso aos seguintes MCPs: {', '.join(mcps)}.
            
            Use os MCPs apropriados para resolver as tarefas solicitadas.
            Sempre explique suas ações e resultados de forma clara.
            """
        
        # Cria lista de ferramentas MCP
        tools = []
        for mcp_name in mcps:
            mcp_info = self.registry.mcps.get(mcp_name)
            if mcp_info:
                tools.append(MCP(mcp_info["command"]))
        
        # Cria o agente
        agent = Agent(
            instructions=instructions,
            llm=f"openrouter/{self.default_model}",
            tools=tools
        )
        
        return agent
    
    async def process_prompt(self, prompt: str, auto_install: bool = True) -> Dict[str, Any]:
        """Processa um prompt, instalando e configurando MCPs conforme necessário"""
        logger.info(f"Processando prompt: {prompt}")
        
        # Analisa prompt e sugere MCPs
        analysis = await self.analyze_prompt_and_suggest_mcps(prompt)
        
        result = {
            "prompt": prompt,
            "analysis": analysis,
            "mcps_installed": [],
            "mcps_started": [],
            "response": None,
            "error": None
        }
        
        try:
            # Auto-instala MCPs se habilitado
            if auto_install:
                for mcp_name in analysis["auto_install_mcps"]:
                    if await self.install_mcp(mcp_name):
                        result["mcps_installed"].append(mcp_name)
                    
                    if await self.start_mcp(mcp_name):
                        result["mcps_started"].append(mcp_name)
            
            # Cria e executa agente com MCPs
            if analysis["suggested_mcps"] and PRAISON_AVAILABLE:
                agent = self.create_agent_with_mcps(analysis["suggested_mcps"])
                if agent:
                    response = agent.start(prompt)
                    result["response"] = response
                else:
                    result["error"] = "Falha ao criar agente"
            else:
                # Fallback para execução sem agente
                result["response"] = await self.fallback_response(prompt, analysis)
            
            # Salva na história da sessão
            self.session_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar prompt: {e}")
            result["error"] = str(e)
        
        return result
    
    async def fallback_response(self, prompt: str, analysis: Dict) -> str:
        """Resposta fallback quando agente não está disponível"""
        return f"""
        Análise do prompt: {prompt}
        
        MCPs sugeridos: {', '.join(analysis['suggested_mcps'])}
        Categorias necessárias: {', '.join(analysis['categories_needed'])}
        
        Para uma resposta completa, instale PraisonAI:
        pip install "praisonaiagents[llm]"
        
        E configure sua chave OpenRouter:
        export OPENROUTER_API_KEY=sua_chave_aqui
        """
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do gerenciador"""
        return {
            "api_key_configured": bool(self.api_key),
            "praison_available": PRAISON_AVAILABLE,
            "total_mcps": len(self.registry.mcps),
            "active_mcps": list(self.registry.active_mcps.keys()),
            "session_prompts": len(self.session_history),
            "categories": list(set(mcp["category"] for mcp in self.registry.mcps.values()))
        }
    
    def list_available_mcps(self) -> Dict[str, Dict]:
        """Lista todos os MCPs disponíveis"""
        return self.registry.mcps
    
    async def shutdown(self):
        """Para todos os MCPs ativos"""
        logger.info("Parando todos os MCPs ativos...")
        
        for mcp_name in list(self.registry.active_mcps.keys()):
            await self.stop_mcp(mcp_name)
        
        logger.info("Shutdown concluído")

# Funções utilitárias
async def quick_mcp_task(task: str, api_key: str = None) -> str:
    """Função utilitária para executar tarefa rápida com MCPs"""
    manager = OpenRouterAgentManager(api_key)
    
    try:
        result = await manager.process_prompt(task)
        return result.get("response", "Sem resposta disponível")
    finally:
        await manager.shutdown()

def get_mcp_recommendations(task_description: str) -> List[str]:
    """Função utilitária para obter recomendações de MCPs"""
    registry = MCPRegistry()
    return registry.get_mcp_for_task(task_description)

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        # Configura API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Configure OPENROUTER_API_KEY")
            return
        
        manager = OpenRouterAgentManager(api_key)
        
        # Testa análise de prompt
        prompt = "Preciso listar os arquivos do projeto e fazer commit das mudanças"
        result = await manager.process_prompt(prompt)
        
        print("Resultado:", json.dumps(result, indent=2, ensure_ascii=False))
        
        # Status do sistema
        status = manager.get_status()
        print("Status:", json.dumps(status, indent=2, ensure_ascii=False))
        
        await manager.shutdown()
    
    asyncio.run(main()) 