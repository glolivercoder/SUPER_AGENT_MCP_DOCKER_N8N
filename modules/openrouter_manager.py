# OpenRouter Manager - SUPER_AGENT_MCP_DOCKER_N8N
"""
Gerenciador OpenRouter para MCPs dinâmicos
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests

logger = logging.getLogger(__name__)

class OpenRouterManager:
    """Gerenciador OpenRouter com MCPs"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.active_mcps = {}
        
        # MCPs Registry
        self.mcps_registry = {
            "filesystem": {
                "command": "npx -y @modelcontextprotocol/server-filesystem",
                "category": "architecture",
                "description": "Gerencia arquivos e diretórios"
            },
            "git": {
                "command": "npx -y @modelcontextprotocol/server-git", 
                "category": "architecture",
                "description": "Controle Git"
            },
            "cursor": {
                "command": "npx -y @cursor/mcp-server",
                "category": "ide", 
                "description": "Controle Cursor IDE"
            },
            "figma": {
                "command": "npx -y @figma/mcp-server",
                "category": "design",
                "description": "Integração Figma"
            },
            "docker": {
                "command": "npx -y @docker/mcp-server",
                "category": "devops", 
                "description": "Docker management"
            },
            "supermemory": {
                "command": "npx -y supergateway --sse https://mcp.supermemory.ai/2ubE0qTwMtbd9dYC_fetX/sse",
                "category": "memory",
                "description": "Armazena memórias de todas interfaces em ambiente único"
            }
        }
    
    async def analyze_prompt(self, prompt: str) -> List[str]:
        """Analisa prompt e sugere MCPs"""
        keywords = {
            "filesystem": ["arquivo", "file", "diretório", "pasta", "directory"],
            "git": ["git", "commit", "branch", "repo"],
            "cursor": ["cursor", "ide", "editor"],
            "figma": ["figma", "design", "ui"],
            "docker": ["docker", "container", "image"],
            "supermemory": ["memória", "memory", "lembrar", "remember", "interface", "histórico", "contexto", "recall"]
        }
        
        suggested = []
        prompt_lower = prompt.lower()
        
        for mcp, words in keywords.items():
            if any(word in prompt_lower for word in words):
                suggested.append(mcp)
        
        return suggested
    
    async def start_mcp(self, mcp_name: str) -> bool:
        """Inicia MCP específico"""
        if mcp_name in self.active_mcps:
            return True
            
        mcp_info = self.mcps_registry.get(mcp_name)
        if not mcp_info:
            return False
        
        try:
            cmd = mcp_info["command"].split()
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(1)
            if process.poll() is None:
                self.active_mcps[mcp_name] = process
                logger.info(f"MCP {mcp_name} iniciado")
                return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar {mcp_name}: {e}")
        
        return False
    
    async def stop_mcp(self, mcp_name: str) -> bool:
        """Para MCP específico"""
        if mcp_name not in self.active_mcps:
            return True
        
        try:
            process = self.active_mcps[mcp_name]
            process.terminate()
            process.wait(timeout=5)
            del self.active_mcps[mcp_name]
            logger.info(f"MCP {mcp_name} parado")
            return True
        except:
            return False
    
    async def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """Processa prompt com MCPs apropriados"""
        # Analisa MCPs necessários
        needed_mcps = await self.analyze_prompt(prompt)
        
        # Para MCPs desnecessários
        for mcp in list(self.active_mcps.keys()):
            if mcp not in needed_mcps:
                await self.stop_mcp(mcp)
        
        # Inicia MCPs necessários
        started_mcps = []
        for mcp in needed_mcps:
            if await self.start_mcp(mcp):
                started_mcps.append(mcp)
        
        # Chama OpenRouter se API key disponível
        response = "MCPs preparados"
        if self.api_key:
            try:
                response = await self._call_openrouter(prompt, started_mcps)
            except Exception as e:
                response = f"Erro OpenRouter: {e}"
        
        return {
            "prompt": prompt,
            "needed_mcps": needed_mcps,
            "started_mcps": started_mcps,
            "response": response
        }
    
    async def _call_openrouter(self, prompt: str, mcps: List[str]) -> str:
        """Chama API OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        enhanced_prompt = f"{prompt}\n\nMCPs disponíveis: {', '.join(mcps)}"
        
        payload = {
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": enhanced_prompt}]
        }
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def get_status(self) -> Dict:
        """Status do gerenciador"""
        return {
            "api_configured": bool(self.api_key),
            "active_mcps": list(self.active_mcps.keys()),
            "available_mcps": list(self.mcps_registry.keys())
        }
    
    async def shutdown(self):
        """Para todos os MCPs"""
        for mcp in list(self.active_mcps.keys()):
            await self.stop_mcp(mcp)

# Função utilitária
async def quick_task(task: str, api_key: str = None) -> str:
    """Executa tarefa rápida"""
    manager = OpenRouterManager(api_key)
    try:
        result = await manager.process_prompt(task)
        return result.get("response", "Sem resposta")
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    async def test():
        manager = OpenRouterManager()
        result = await manager.process_prompt("Liste os arquivos e faça commit")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        await manager.shutdown()
    
    asyncio.run(test()) 