#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter Manager - Versão Melhorada
Gerencia comunicação com a API OpenRouter para modelos de IA
"""

import asyncio
import aiohttp
import requests
import json
import time
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import logging

# Configurar logger
logger = logging.getLogger(__name__)

@dataclass
class OpenRouterModel:
    """Estrutura para modelo OpenRouter"""
    id: str
    name: str
    description: str
    context_length: int
    pricing: Dict[str, float]
    company: str
    is_free: bool
    tags: List[str]
    available: bool = True

class OpenRouterManager:
    """Gerencia comunicação com a API OpenRouter"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY', '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')
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = logger
        self.session = None
        self.rate_limits = {}
        
        # Tipos de agentes disponíveis
        self.agent_types = {
            "chat": {
                "name": "Chat Geral",
                "system_prompt": "Você é um assistente útil e amigável. Responda de forma clara e concisa."
            },
            "code": {
                "name": "Assistente de Código",
                "system_prompt": "Você é um especialista em programação. Forneça código limpo, bem documentado e eficiente."
            },
            "analysis": {
                "name": "Analista",
                "system_prompt": "Você é um analista especializado. Forneça análises detalhadas e insights valiosos."
            },
            "creative": {
                "name": "Criativo",
                "system_prompt": "Você é um assistente criativo. Ajude com ideias inovadoras e soluções criativas."
            }
        }
        
        # Banco de dados de memórias
        self.memories_file = Path("MEMORIES.json")
        self._load_memories()
    
    def _load_memories(self):
        """Carrega memórias do arquivo"""
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
            except Exception as e:
                self.logger.error(f"Erro ao carregar memórias: {e}")
                self.memories = []
        else:
            self.memories = []
    
    def _save_memories(self):
        """Salva memórias no arquivo"""
        try:
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar memórias: {e}")
    
    def check_api_key(self) -> bool:
        """Verifica se a API key está configurada"""
        return bool(self.api_key and self.api_key.startswith('sk-or-'))
    
    def get_models(self):
        """Carrega apenas modelos disponíveis da OpenRouter"""
        self.logger.info("Carregando modelos OpenRouter disponíveis...")
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            self.logger.info(f"[DEBUG] Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                models = []
                total_models = len(data.get("data", []))
                available_models = 0
                
                for model_data in data.get("data", []):
                    # Verificar se o modelo está disponível
                    if not self._is_model_available(model_data):
                        continue
                    
                    available_models += 1
                    
                    # Extrair empresa do nome do modelo
                    company = model_data.get("company", "Unknown")
                    if company == "Unknown":
                        parts = model_data.get("id", "").split("/")
                        if len(parts) > 1:
                            company = parts[0]
                    
                    # Verificar se é modelo gratuito
                    is_free = self._is_model_free(model_data)
                    
                    # Extrair tags
                    tags = model_data.get("tags", [])
                    
                    # Criar objeto OpenRouterModel
                    model = OpenRouterModel(
                        id=model_data.get("id", ""),
                        name=model_data.get("name", ""),
                        description=model_data.get("description", ""),
                        context_length=model_data.get("context_length", 0),
                        pricing=model_data.get("pricing", {}),
                        company=company,
                        is_free=is_free,
                        tags=tags,
                        available=True
                    )
                    models.append(model)
                
                self.logger.info(f"Modelos disponíveis: {available_models}/{total_models}")
                return models
            else:
                self.logger.error(f"Erro HTTP: {resp.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {e}")
            return []
    
    def _is_model_available(self, model_data: Dict) -> bool:
        """Verifica se o modelo está disponível para uso"""
        # Verificar se o modelo não está desabilitado
        if model_data.get("disabled", False):
            return False
        
        # Verificar se o modelo não está offline
        if model_data.get("offline", False):
            return False
        
        # Verificar se o modelo tem endpoint configurado
        if not model_data.get("endpoints"):
            return False
        
        # Verificar se o modelo não está em manutenção
        if model_data.get("maintenance", False):
            return False
        
        # Verificar se o modelo tem preços definidos (indica que está ativo)
        pricing = model_data.get("pricing", {})
        if not pricing:
            return False
        
        # Verificar se o modelo tem contexto definido
        if not model_data.get("context_length"):
            return False
        
        # Verificar se o modelo não está deprecated
        if model_data.get("deprecated", False):
            return False
        
        return True
    
    def _is_model_free(self, model_data: Dict) -> bool:
        """Verifica se o modelo é gratuito"""
        pricing = model_data.get("pricing", {})
        name = model_data.get("name", "").lower()
        
        # Obter preços (podem vir como string ou número)
        prompt_price = pricing.get("prompt", 0)
        completion_price = pricing.get("completion", 0)
        
        # Converter para float se for string
        try:
            prompt_price = float(prompt_price) if prompt_price is not None else 0
            completion_price = float(completion_price) if completion_price is not None else 0
        except (ValueError, TypeError):
            prompt_price = 0
            completion_price = 0
        
        # Critérios para modelo gratuito
        is_free = (
            prompt_price == 0 and completion_price == 0 or
            "free" in name or
            "gpt-4o-mini" in name or  # Modelo conhecido como gratuito
            pricing.get("free", False) or
            model_data.get("free", False)
        )
        
        return is_free
    
    def filter_models(self, models: List[OpenRouterModel], 
                     company: Optional[str] = None,
                     free_only: bool = False,
                     min_context: int = 0,
                     search_term: Optional[str] = None) -> List[OpenRouterModel]:
        """Filtra modelos por critérios"""
        filtered = models
        
        if company:
            filtered = [m for m in filtered if m.company.lower() == company.lower()]
        
        if free_only:
            filtered = [m for m in filtered if m.is_free]
        
        if min_context > 0:
            filtered = [m for m in filtered if m.context_length >= min_context]
        
        if search_term:
            search_lower = search_term.lower()
            filtered = [m for m in filtered if 
                       search_lower in m.name.lower() or 
                       search_lower in m.description.lower()]
        
        return filtered
    
    def get_companies(self, models: List[OpenRouterModel]) -> List[str]:
        """Obtém lista de empresas disponíveis"""
        companies = list(set(m.company for m in models))
        return sorted(companies)
    
    async def chat_with_model(self, model_id: str, messages: List[Dict], 
                            agent_type: str = "chat", context_docs: Optional[List[str]] = None,
                            tts_enabled: bool = False) -> Dict:
        """Chat com modelo específico com rate limiting"""
        if not self.check_api_key():
            return {"error": "API key não configurada"}
        
        try:
            # Preparar mensagens com contexto do agente
            system_prompt = self.agent_types.get(agent_type, {}).get("system_prompt", "")
            
            # Adicionar instruções para TTS se estiver habilitado
            if tts_enabled:
                tts_instructions = """
                
                IMPORTANTE - RESPOSTA PARA TTS:
                - NÃO use caracteres especiais como *, \\, /, #, @, $, %, ^, &, |, ~, `, +, =, {, }, [, ], <, >, ", ', ;, :, ?, !
                - Substitua esses caracteres por palavras descritivas (ex: "asterisco" em vez de *, "barra" em vez de /)
                - Use apenas texto limpo que pode ser lido naturalmente por um sistema de síntese de voz
                - Evite símbolos técnicos que seriam lidos literalmente pelo TTS
                - Mantenha a resposta clara e natural para leitura em voz alta
                """
                system_prompt += tts_instructions
            
            if context_docs:
                context_text = "\n\n".join(context_docs)
                system_prompt += f"\n\nContexto adicional:\n{context_text}"
            
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            payload = {
                "model": model_id,
                "messages": full_messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            self.logger.info(f"Enviando requisição para modelo: {model_id} (TTS: {'Sim' if tts_enabled else 'Não'})")
            
            # Usar requests para evitar problemas de conexão
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N",
                "Content-Type": "application/json"
            }
            
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "response": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "model": model_id
                }
            else:
                error_text = resp.text
                self.logger.error(f"Erro na API OpenRouter: Status {resp.status_code}, Response: {error_text}")
                return {"error": f"Erro na API: {error_text}"}
                
        except Exception as e:
            self.logger.error(f"Erro no chat: {e}")
            return {"error": str(e)}
    
    def save_memory(self, prompt: str, response: str, agent_type: str, 
                   model_id: str, context_used: Optional[List[str]] = None):
        """Salva interação na memória"""
        memory = {
            "timestamp": time.time(),
            "prompt": prompt,
            "response": response,
            "agent_type": agent_type,
            "model_id": model_id,
            "context_used": context_used or [],
            "tags": self._extract_tags(prompt)
        }
        
        self.memories.append(memory)
        self._save_memories()
    
    def _extract_tags(self, prompt: str) -> List[str]:
        """Extrai tags relevantes do prompt"""
        tags = []
        prompt_lower = prompt.lower()
        
        # Tags baseadas em palavras-chave
        if "código" in prompt_lower or "programação" in prompt_lower:
            tags.append("code")
        if "análise" in prompt_lower or "analisar" in prompt_lower:
            tags.append("analysis")
        if "criativo" in prompt_lower or "ideia" in prompt_lower:
            tags.append("creative")
        if "docker" in prompt_lower:
            tags.append("docker")
        if "n8n" in prompt_lower:
            tags.append("n8n")
        
        return tags
    
    def get_memories(self, search_term: Optional[str] = None, 
                    agent_type: Optional[str] = None) -> List[Dict]:
        """Busca memórias por termo ou tipo de agente"""
        filtered = self.memories
        
        if search_term:
            search_lower = search_term.lower()
            filtered = [m for m in filtered if 
                       search_lower in m["prompt"].lower() or 
                       search_lower in m["response"].lower()]
        
        if agent_type:
            filtered = [m for m in filtered if m["agent_type"] == agent_type]
        
        return filtered
    
    def get_agent_types(self) -> Dict[str, Dict]:
        """Retorna tipos de agentes disponíveis"""
        return self.agent_types
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do manager"""
        return {
            "api_key_configured": self.check_api_key(),
            "memories_count": len(self.memories),
            "agent_types": list(self.agent_types.keys())
        } 