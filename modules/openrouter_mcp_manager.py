# OpenRouter MCP Manager - SUPER_AGENT_MCP_DOCKER_N8N
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

class OpenRouterMCPManager:
    """Gerenciador principal do OpenRouter com MCPs"""
    
    def __init__(self, openrouter_api_key: str = None):
        self.api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("OpenRouter API key não configurada")
        
        self.registry = MCPRegistry()
        self.session_history = []
        
        # Configurações OpenRouter
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.default_model = "openai/gpt-4"
        self.fallback_models = [
            "openrouter/google/gemini-2.0-flash-exp:free",
            "anthropic/claude-3-haiku",
            "meta-llama/llama-3.1-8b-instruct:free"
        ]
        
        logger.info("OpenRouter MCP Manager inicializado")
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analisa prompt via OpenRouter para determinar MCPs necessários"""
        analysis_prompt = f"""
        Analise o seguinte prompt e determine quais MCPs são necessários:
        
        Prompt: {prompt}
        
        MCPs disponíveis:
        {json.dumps(self.registry.mcps, indent=2, ensure_ascii=False)}
        
        Responda em JSON com:
        - mcps_needed: lista de MCPs necessários
        - reasoning: explicação da escolha
        - priority: ordem de prioridade
        """
        
        try:
            response = await self._call_openrouter(analysis_prompt)
            
            # Tenta extrair JSON da resposta
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # Fallback para análise local
                analysis = {
                    "mcps_needed": self.registry.get_mcp_for_task(prompt),
                    "reasoning": "Análise local baseada em palavras-chave",
                    "priority": "medium"
                }
        except Exception as e:
            logger.error(f"Erro na análise via OpenRouter: {e}")
            analysis = {
                "mcps_needed": self.registry.get_mcp_for_task(prompt),
                "reasoning": "Fallback para análise local",
                "priority": "medium"
            }
        
        return analysis
    
    async def _call_openrouter(self, prompt: str, model: str = None) -> str:
        """Chama a API do OpenRouter"""
        if not self.api_key:
            raise ValueError("OpenRouter API key não configurada")
        
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/SUPER_AGENT_MCP_DOCKER_N8N",
            "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na chamada OpenRouter: {e}")
            
            # Tenta modelos fallback
            for fallback_model in self.fallback_models:
                try:
                    payload["model"] = fallback_model
                    response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                except:
                    continue
            
            raise e
    
    async def install_mcp(self, mcp_name: str) -> bool:
        """Instala um MCP específico"""
        if mcp_name not in self.registry.mcps:
            logger.error(f"MCP {mcp_name} não encontrado no registry")
            return False
        
        mcp_info = self.registry.mcps[mcp_name]
        
        # Para MCPs NPX, verifica se Node.js está disponível
        if mcp_info["command"].startswith("npx"):
            try:
                result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error("Node.js não está instalado. Necessário para MCPs NPX.")
                    return False
                logger.info(f"Node.js disponível: {result.stdout.strip()}")
                return True
            except FileNotFoundError:
                logger.error("Node.js não encontrado no PATH")
                return False
        
        return True
    
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
            logger.info(f"Iniciando MCP {mcp_name}...")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguarda um pouco para verificar se iniciou
            time.sleep(2)
            if process.poll() is None:
                self.registry.active_mcps[mcp_name] = process
                logger.info(f"MCP {mcp_name} iniciado (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"MCP {mcp_name} falhou: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar MCP {mcp_name}: {e}")
            return False
    
    async def stop_mcp(self, mcp_name: str) -> bool:
        """Para um MCP específico"""
        if mcp_name not in self.registry.active_mcps:
            return True
        
        try:
            process = self.registry.active_mcps[mcp_name]
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            del self.registry.active_mcps[mcp_name]
            logger.info(f"MCP {mcp_name} parado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao parar MCP {mcp_name}: {e}")
            return False
    
    async def process_with_mcps(self, prompt: str, mcps: List[str] = None) -> Dict[str, Any]:
        """Processa prompt com MCPs específicos via OpenRouter"""
        if not mcps:
            analysis = await self.analyze_prompt(prompt)
            mcps = analysis.get("mcps_needed", [])
        
        # Prepara ferramentas MCP para OpenRouter
        tools = []
        active_mcps = []
        
        for mcp_name in mcps:
            if mcp_name in self.registry.mcps:
                mcp_info = self.registry.mcps[mcp_name]
                
                # Inicia MCP se necessário
                if await self.start_mcp(mcp_name):
                    active_mcps.append(mcp_name)
                    
                    # Adiciona capacidades como ferramentas
                    for capability in mcp_info.get("capabilities", []):
                        tools.append({
                            "type": "function",
                            "function": {
                                "name": capability,
                                "description": f"{capability} via {mcp_info['name']}",
                                "parameters": {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                }
                            }
                        })
        
        # Constrói prompt enriquecido
        enhanced_prompt = f"""
        {prompt}
        
        MCPs ativos: {', '.join(active_mcps)}
        Capacidades disponíveis: {', '.join([tool['function']['name'] for tool in tools])}
        
        Use as ferramentas MCP apropriadas para resolver esta tarefa.
        """
        
        try:
            # Chama OpenRouter com ferramentas
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "user", "content": enhanced_prompt}
                ],
                "tools": tools if tools else None
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            message = result["choices"][0]["message"]
            
            # Processa tool calls se existirem
            if "tool_calls" in message:
                tool_results = []
                for tool_call in message["tool_calls"]:
                    # Simula execução da ferramenta MCP
                    tool_result = await self._execute_mcp_tool(
                        tool_call["function"]["name"],
                        json.loads(tool_call["function"]["arguments"])
                    )
                    tool_results.append(tool_result)
                
                return {
                    "response": message.get("content", ""),
                    "tool_calls": message["tool_calls"],
                    "tool_results": tool_results,
                    "active_mcps": active_mcps
                }
            else:
                return {
                    "response": message["content"],
                    "active_mcps": active_mcps
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar com MCPs: {e}")
            return {
                "error": str(e),
                "fallback_response": "Erro na integração OpenRouter/MCP"
            }
    
    async def _execute_mcp_tool(self, tool_name: str, arguments: Dict) -> str:
        """Simula execução de ferramenta MCP"""
        # Em uma implementação real, isso faria chamadas reais aos MCPs
        return f"Executou {tool_name} com argumentos {arguments}"
    
    async def manage_mcps_dynamically(self, prompt: str) -> Dict[str, Any]:
        """Gerencia MCPs dinamicamente baseado no prompt"""
        logger.info(f"Gerenciamento dinâmico para: {prompt}")
        
        result = {
            "original_prompt": prompt,
            "analysis": None,
            "mcps_installed": [],
            "mcps_started": [],
            "mcps_stopped": [],
            "response": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. Analisa o prompt
            analysis = await self.analyze_prompt(prompt)
            result["analysis"] = analysis
            
            needed_mcps = analysis.get("mcps_needed", [])
            
            # 2. Para MCPs não necessários
            for mcp_name in list(self.registry.active_mcps.keys()):
                if mcp_name not in needed_mcps:
                    if await self.stop_mcp(mcp_name):
                        result["mcps_stopped"].append(mcp_name)
            
            # 3. Instala e inicia MCPs necessários
            for mcp_name in needed_mcps:
                if await self.install_mcp(mcp_name):
                    result["mcps_installed"].append(mcp_name)
                
                if await self.start_mcp(mcp_name):
                    result["mcps_started"].append(mcp_name)
            
            # 4. Processa o prompt com MCPs ativos
            response = await self.process_with_mcps(prompt, needed_mcps)
            result["response"] = response
            
            # 5. Salva na história
            self.session_history.append(result)
            
        except Exception as e:
            logger.error(f"Erro no gerenciamento dinâmico: {e}")
            result["error"] = str(e)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Status do gerenciador"""
        return {
            "api_configured": bool(self.api_key),
            "total_mcps": len(self.registry.mcps),
            "active_mcps": list(self.registry.active_mcps.keys()),
            "session_history_count": len(self.session_history),
            "categories": list(set(mcp["category"] for mcp in self.registry.mcps.values()))
        }
    
    async def shutdown(self):
        """Para todos os MCPs"""
        for mcp_name in list(self.registry.active_mcps.keys()):
            await self.stop_mcp(mcp_name)

# Função utilitária
async def quick_agent_task(task: str, api_key: str = None) -> str:
    """Executa tarefa rápida com gerenciamento automático de MCPs"""
    manager = OpenRouterMCPManager(api_key)
    try:
        result = await manager.manage_mcps_dynamically(task)
        return result.get("response", {}).get("response", "Sem resposta")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        manager = OpenRouterMCPManager()
        
        # Testa o gerenciamento dinâmico
        prompt = "Preciso listar arquivos do projeto e fazer commit no git"
        result = await manager.manage_mcps_dynamically(prompt)
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        await manager.shutdown()
    
    asyncio.run(main()) 