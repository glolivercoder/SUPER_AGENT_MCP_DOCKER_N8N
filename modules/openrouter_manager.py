#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter Manager - Gerenciador de Modelos LLM via OpenRouter
-------------------------------------------------------------
Módulo responsável por:
- Integração com API OpenRouter
- Seleção e teste de modelos LLM
- Filtros por empresa, preço, contexto
- Integração com RAG para contexto
- Chat direto com agentes
- Criação de PRDs e tasks
- Integração com N8N e Docker

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import json
import logging
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import openai
from dataclasses import dataclass

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

class OpenRouterManager:
    """Gerenciador principal do OpenRouter"""
    
    def __init__(self):
        self.logger = logging.getLogger("OpenRouterManager")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.models_cache = {}
        self.last_update = None
        self.cache_duration = 3600  # 1 hora
        
        # Configurar OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
            openai.base_url = f"{self.base_url}/chat/completions"
        
        # Categorias de agentes
        self.agent_types = {
            "chat": {
                "name": "Chat Direto",
                "description": "Chat direto com o agente com acesso à web",
                "system_prompt": "Você é um assistente especializado em desenvolvimento de software. Você tem acesso à web para buscar informações atualizadas e pode ajudar com programação, debugging, arquitetura de sistemas e boas práticas de desenvolvimento."
            },
            "prompt": {
                "name": "PRD Generator",
                "description": "Cria PRDs com técnicas modernas de programação e segurança",
                "system_prompt": "Você é um especialista em Product Requirements Documents (PRD) e desenvolvimento de software. Você cria PRDs detalhados com as melhores práticas modernas de programação, segurança de dados, arquitetura escalável e metodologias ágeis. Sempre inclua seções de segurança, performance, monitoramento e deploy."
            },
            "n8n": {
                "name": "N8N Workflow Generator",
                "description": "Cria workflows, nodes e credenciais para N8N",
                "system_prompt": "Você é um especialista em N8N (n8n.io) e automação de workflows. Você cria workflows eficientes, configura nodes, credenciais e usa Docker Compose para preparar ambientes. Você conhece todos os nodes disponíveis e melhores práticas de automação."
            },
            "deploy": {
                "name": "Deploy Manager",
                "description": "Deploy nos principais servidores (DigitalOcean, Cloudflare, Oracle)",
                "system_prompt": "Você é um especialista em deploy e DevOps. Você conhece DigitalOcean, Cloudflare Workers, Oracle Cloud Free Tier, EasyPanel e Docker. Você cria scripts de deploy, configurações de CI/CD e documentação completa para deploy em produção."
            }
        }
        
        self.logger.info("OpenRouter Manager inicializado")
    
    def check_api_key(self) -> bool:
        """Verifica se a API key está configurada"""
        if not self.api_key:
            self.logger.error("OPENROUTER_API_KEY não configurada")
            return False
        return True
    
    async def get_models(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """Obtém lista de modelos disponíveis"""
        if not self.check_api_key():
            return []
        
        # Verificar cache
        if not force_refresh and self.models_cache and self.last_update:
            time_diff = (datetime.now() - self.last_update).total_seconds()
            if time_diff < self.cache_duration:
                return list(self.models_cache.values())
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(f"{self.base_url}/models", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        
                        for model_data in data.get("data", []):
                            # Extrair empresa do nome do modelo se não estiver disponível
                            company = model_data.get("company", "Unknown")
                            if company == "Unknown":
                                # Tentar extrair empresa do nome do modelo
                                name = model_data.get("name", "")
                                if ":" in name:
                                    company = name.split(":")[0].strip()
                                elif " " in name and any(keyword in name.lower() for keyword in ["gpt", "claude", "gemini", "llama"]):
                                    # Detectar empresas conhecidas
                                    if "gpt" in name.lower():
                                        company = "OpenAI"
                                    elif "claude" in name.lower():
                                        company = "Anthropic"
                                    elif "gemini" in name.lower():
                                        company = "Google"
                                    elif "llama" in name.lower():
                                        company = "Meta"
                                    else:
                                        company = name.split(" ")[0]
                            
                            model = OpenRouterModel(
                                id=model_data["id"],
                                name=model_data["name"],
                                description=model_data.get("description", ""),
                                context_length=model_data.get("context_length", 0),
                                pricing=model_data.get("pricing", {}),
                                company=company,
                                is_free=self._is_model_free(model_data),
                                tags=model_data.get("tags", [])
                            )
                            models.append(model)
                            self.models_cache[model.id] = model
                        
                        self.last_update = datetime.now()
                        self.logger.info(f"Carregados {len(models)} modelos")
                        return models
                    else:
                        self.logger.error(f"Erro ao obter modelos: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Erro ao obter modelos: {e}")
            return []
    
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
                            agent_type: str = "chat", context_docs: Optional[List[str]] = None) -> Dict:
        """Chat com modelo específico"""
        if not self.check_api_key():
            return {"error": "API key não configurada"}
        
        try:
            # Preparar mensagens com contexto do agente
            system_prompt = self.agent_types.get(agent_type, {}).get("system_prompt", "")
            
            if context_docs:
                context_text = "\n\n".join(context_docs)
                system_prompt += f"\n\nContexto adicional:\n{context_text}"
            
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/your-repo",  # OpenRouter requer
                    "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"  # OpenRouter requer
                }
                
                payload = {
                    "model": model_id,
                    "messages": full_messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                self.logger.info(f"Enviando requisição para modelo: {model_id}")
                self.logger.debug(f"Headers: {headers}")
                self.logger.debug(f"Payload: {payload}")
                
                async with session.post(f"{self.base_url}/chat/completions", 
                                      headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "response": data["choices"][0]["message"]["content"],
                            "usage": data.get("usage", {}),
                            "model": model_id
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Erro na API OpenRouter: Status {response.status}, Response: {error_text}")
                        return {"error": f"Erro na API: {error_text}"}
                        
        except Exception as e:
            self.logger.error(f"Erro no chat: {e}")
            return {"error": str(e)}
    
    async def generate_prd(self, model_id: str, project_description: str, 
                          context_docs: Optional[List[str]] = None) -> Dict:
        """Gera PRD completo para projeto"""
        prompt = f"""
        Crie um Product Requirements Document (PRD) completo e detalhado para o seguinte projeto:
        
        {project_description}
        
        O PRD deve incluir:
        1. Visão Geral do Produto
        2. Objetivos e Metas
        3. Personas e Casos de Uso
        4. Funcionalidades Principais
        5. Requisitos Técnicos
        6. Arquitetura do Sistema
        7. Requisitos de Segurança
        8. Requisitos de Performance
        9. Estratégia de Deploy
        10. Cronograma e Milestones
        11. Critérios de Sucesso
        12. Riscos e Mitigações
        
        Use as melhores práticas modernas de desenvolvimento de software, segurança de dados e metodologias ágeis.
        """
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_with_model(model_id, messages, "prompt", context_docs)
    
    async def generate_tasks(self, model_id: str, prd_content: str, 
                           context_docs: Optional[List[str]] = None) -> Dict:
        """Gera arquivo de tasks baseado no PRD"""
        prompt = f"""
        Com base no seguinte PRD, crie um arquivo de tasks detalhado para desenvolvimento:
        
        {prd_content}
        
        Crie tasks organizadas por:
        1. Setup do Ambiente
        2. Backend Development
        3. Frontend Development
        4. Database Design
        5. API Development
        6. Security Implementation
        7. Testing
        8. Deploy
        9. Documentation
        
        Cada task deve ter:
        - ID único
        - Título claro
        - Descrição detalhada
        - Critérios de aceitação
        - Estimativa de tempo
        - Dependências
        - Status (TODO, IN_PROGRESS, DONE)
        """
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_with_model(model_id, messages, "prompt", context_docs)
    
    async def generate_n8n_workflow(self, model_id: str, workflow_description: str,
                                  context_docs: Optional[List[str]] = None) -> Dict:
        """Gera workflow N8N com Docker Compose"""
        prompt = f"""
        Crie um workflow N8N completo para:
        
        {workflow_description}
        
        Inclua:
        1. Workflow JSON completo
        2. Configuração de nodes
        3. Credenciais necessárias
        4. Docker Compose para N8N
        5. Instruções de deploy
        6. Monitoramento e logs
        
        Use as melhores práticas de automação e integração.
        """
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_with_model(model_id, messages, "n8n", context_docs)
    
    async def generate_deploy_script(self, model_id: str, project_info: str,
                                   target_platform: str, context_docs: Optional[List[str]] = None) -> Dict:
        """Gera script de deploy para plataforma específica"""
        prompt = f"""
        Crie um script de deploy completo para {target_platform}:
        
        {project_info}
        
        Inclua:
        1. Scripts de deploy
        2. Configurações de ambiente
        3. Docker Compose (se aplicável)
        4. Configurações de CI/CD
        5. Monitoramento e logs
        6. Backup e recovery
        7. Documentação de deploy
        
        Use as melhores práticas para {target_platform}.
        """
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_with_model(model_id, messages, "deploy", context_docs)
    
    def save_memory(self, prompt: str, response: str, agent_type: str, 
                   model_id: str, context_used: Optional[List[str]] = None):
        """Salva memória do prompt e resposta"""
        memory_file = Path("MEMORIES.json")
        
        try:
            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8') as f:
                    memories = json.load(f)
            else:
                memories = {
                    "version": "1.0.0",
                    "prompt_memories": [],
                    "last_update": datetime.now().isoformat()
                }
            
            memory_entry = {
                "id": f"mem_{len(memories.get('prompt_memories', [])) + 1}",
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "response": response,
                "agent_type": agent_type,
                "model_id": model_id,
                "context_used": context_used or [],
                "tags": self._extract_tags(prompt)
            }
            
            memories.setdefault("prompt_memories", []).append(memory_entry)
            memories["last_update"] = datetime.now().isoformat()
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Memória salva: {memory_entry['id']}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória: {e}")
    
    def _extract_tags(self, prompt: str) -> List[str]:
        """Extrai tags relevantes do prompt"""
        tags = []
        prompt_lower = prompt.lower()
        
        # Tags por tecnologia
        tech_keywords = {
            "python": ["python", "django", "flask", "fastapi"],
            "javascript": ["javascript", "node", "react", "vue", "angular"],
            "docker": ["docker", "container", "kubernetes"],
            "n8n": ["n8n", "workflow", "automation"],
            "deploy": ["deploy", "digitalocean", "cloudflare", "oracle", "aws"]
        }
        
        for tag, keywords in tech_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def get_memories(self, search_term: Optional[str] = None, 
                    agent_type: Optional[str] = None) -> List[Dict]:
        """Obtém memórias filtradas"""
        memory_file = Path("MEMORIES.json")
        
        if not memory_file.exists():
            return []
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
            
            prompt_memories = memories.get("prompt_memories", [])
            
            if search_term:
                search_lower = search_term.lower()
                prompt_memories = [m for m in prompt_memories if 
                                 search_lower in m.get("prompt", "").lower() or
                                 search_lower in m.get("response", "").lower()]
            
            if agent_type:
                prompt_memories = [m for m in prompt_memories if 
                                 m.get("agent_type") == agent_type]
            
            return prompt_memories
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar memórias: {e}")
            return []
    
    def get_agent_types(self) -> Dict[str, Dict]:
        """Retorna tipos de agentes disponíveis"""
        return self.agent_types
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do OpenRouter Manager"""
        return {
            "api_key_configured": bool(self.api_key),
            "models_cached": len(self.models_cache),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "agent_types": list(self.agent_types.keys())
        } 