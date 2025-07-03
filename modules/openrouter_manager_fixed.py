#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenRouter Manager - Gerenciador de Modelos LLM via OpenRouter (CORRIGIDO)
---------------------------------------------------------------------------
Gerencia conexões com a API OpenRouter para acessar diversos modelos LLM
com rate limiting, retry logic e connection pooling.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.1 - Corrigido para evitar suspensão da API
"""

import os
import json
import logging
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

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
    """Gerencia conexões com OpenRouter API com rate limiting"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = logging.getLogger("OpenRouterManager")
        
        # Cache de modelos
        self.models_cache = {}
        self.last_update = None
        self.cache_duration = 300  # 5 minutos
        
        # Rate limiting
        self.request_times = defaultdict(list)
        self.max_requests_per_minute = 15  # Limite conservador
        self.max_requests_per_day = 500    # Limite conservador
        
        # Connection pooling
        self.session = None
        self.session_created = None
        self.session_timeout = 300  # 5 minutos
        
        # Retry logic
        self.max_retries = 3
        self.base_delay = 2.0  # segundos
        
        # Headers padrão conforme documentação OpenRouter
        self.default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/super-agent-mcp-docker-n8n",
            "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
        }
        
        # Tipos de agente
        self.agent_types = {
            "chat": {
                "name": "Chat Geral",
                "description": "Conversa geral e assistente",
                "system_prompt": "Você é um assistente útil e amigável."
            },
            "prompt": {
                "name": "Análise de Prompts",
                "description": "Análise e otimização de prompts",
                "system_prompt": "Você é um especialista em análise e otimização de prompts."
            },
            "n8n": {
                "name": "Especialista N8N",
                "description": "Automação e workflows N8N",
                "system_prompt": "Você é um especialista em automação e workflows N8N."
            },
            "deploy": {
                "name": "Especialista em Deploy",
                "description": "Deploy e infraestrutura",
                "system_prompt": "Você é um especialista em deploy e infraestrutura."
            }
        }
        
        self.logger.info("OpenRouter Manager inicializado com rate limiting")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP com connection pooling"""
        now = datetime.now()
        
        # Criar nova sessão se não existir ou expirou
        if (self.session is None or 
            self.session_created is None or 
            (now - self.session_created).total_seconds() > self.session_timeout):
            
            if self.session:
                await self.session.close()
            
            # Configurar connection pooling
            connector = aiohttp.TCPConnector(
                limit=5,  # Limite de conexões simultâneas
                limit_per_host=3,  # Limite por host
                ttl_dns_cache=300,  # Cache DNS
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.default_headers
            )
            self.session_created = now
            
            self.logger.debug("Nova sessão HTTP criada")
        
        return self.session
    
    async def _check_rate_limit(self, endpoint: str) -> bool:
        """Verifica se não excedeu o rate limit"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        day_ago = now - timedelta(days=1)
        
        # Limpar timestamps antigos
        self.request_times[endpoint] = [
            t for t in self.request_times[endpoint] 
            if t > minute_ago
        ]
        
        # Verificar limite por minuto
        if len(self.request_times[endpoint]) >= self.max_requests_per_minute:
            return False
        
        # Verificar limite diário (simplificado)
        daily_requests = sum(
            len(times) for times in self.request_times.values()
        )
        if daily_requests >= self.max_requests_per_day:
            return False
        
        return True
    
    async def _wait_for_rate_limit(self, endpoint: str):
        """Aguarda até poder fazer nova requisição"""
        while not await self._check_rate_limit(endpoint):
            wait_time = 60  # Aguardar 1 minuto
            self.logger.warning(f"Rate limit atingido para {endpoint}. Aguardando {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Faz requisição com retry logic e backoff exponencial"""
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                # Verificar rate limit
                endpoint = url.split('/')[-1]
                await self._wait_for_rate_limit(endpoint)
                
                # Registrar requisição
                self.request_times[endpoint].append(datetime.now())
                
                # Fazer requisição
                async with session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return response
                    elif response.status == 429:  # Too Many Requests
                        retry_after = int(response.headers.get('Retry-After', 60))
                        self.logger.warning(f"Rate limit (429). Aguardando {retry_after}s...")
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status == 402:  # Payment Required
                        error_text = await response.text()
                        self.logger.error(f"Erro 402 - Saldo insuficiente: {error_text}")
                        raise Exception(f"Saldo insuficiente na conta OpenRouter: {error_text}")
                    elif response.status >= 500:  # Server Error
                        if attempt < self.max_retries - 1:
                            delay = self.base_delay * (2 ** attempt)
                            self.logger.warning(f"Erro {response.status}. Tentativa {attempt + 1}/{self.max_retries}. Aguardando {delay}s...")
                            await asyncio.sleep(delay)
                            continue
                    else:
                        return response
                        
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    self.logger.warning(f"Timeout. Tentativa {attempt + 1}/{self.max_retries}. Aguardando {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    self.logger.warning(f"Erro: {e}. Tentativa {attempt + 1}/{self.max_retries}. Aguardando {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
        
        raise Exception(f"Falha após {self.max_retries} tentativas")
    
    def check_api_key(self) -> bool:
        """Verifica se a API key está configurada"""
        return bool(self.api_key and self.api_key.startswith('sk-or-'))
    
    async def get_models(self, force_refresh: bool = False) -> List[OpenRouterModel]:
        """Obtém lista de modelos disponíveis com rate limiting"""
        if not self.check_api_key():
            return []
        
        # Verificar cache
        if not force_refresh and self.models_cache and self.last_update:
            time_diff = (datetime.now() - self.last_update).total_seconds()
            if time_diff < self.cache_duration:
                return list(self.models_cache.values())
        
        try:
            self.logger.info("Carregando modelos OpenRouter...")
            response = await self._make_request_with_retry('GET', f"{self.base_url}/models")
            
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
                self.logger.info(f"Carregados {len(models)} modelos com sucesso")
                return models
            else:
                error_text = await response.text()
                self.logger.error(f"Erro ao obter modelos: {response.status} - {error_text}")
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
        """Chat com modelo específico com rate limiting"""
        if not self.check_api_key():
            return {"error": "API key não configurada"}
        
        try:
            # Preparar mensagens com contexto do agente
            system_prompt = self.agent_types.get(agent_type, {}).get("system_prompt", "")
            
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
            
            self.logger.info(f"Enviando requisição para modelo: {model_id}")
            
            response = await self._make_request_with_retry(
                'POST', 
                f"{self.base_url}/chat/completions", 
                json=payload
            )
            
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
    
    async def check_credits(self) -> Dict[str, Any]:
        """Verifica créditos disponíveis na conta"""
        if not self.check_api_key():
            return {"error": "API key não configurada"}
        
        try:
            response = await self._make_request_with_retry('GET', f"{self.base_url}/auth/key")
            
            if response.status == 200:
                data = await response.json()
                return {
                    "success": True,
                    "usage": data.get("data", {}).get("usage", 0),
                    "limit": data.get("data", {}).get("limit"),
                    "is_free_tier": data.get("data", {}).get("is_free_tier", True)
                }
            else:
                error_text = await response.text()
                return {"error": f"Erro ao verificar créditos: {error_text}"}
                
        except Exception as e:
            return {"error": f"Erro ao verificar créditos: {e}"}
    
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
        
        # Tags baseadas em palavras-chave
        if any(word in prompt_lower for word in ["prd", "requirements", "document"]):
            tags.append("prd")
        if any(word in prompt_lower for word in ["task", "todo", "development"]):
            tags.append("tasks")
        if any(word in prompt_lower for word in ["n8n", "workflow", "automation"]):
            tags.append("n8n")
        if any(word in prompt_lower for word in ["deploy", "docker", "infrastructure"]):
            tags.append("deploy")
        if any(word in prompt_lower for word in ["chat", "conversation", "assistant"]):
            tags.append("chat")
        
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
            
            # Filtrar por termo de busca
            if search_term:
                search_lower = search_term.lower()
                prompt_memories = [
                    m for m in prompt_memories
                    if (search_lower in m.get("prompt", "").lower() or
                        search_lower in m.get("response", "").lower() or
                        any(search_lower in tag.lower() for tag in m.get("tags", [])))
                ]
            
            # Filtrar por tipo de agente
            if agent_type:
                prompt_memories = [
                    m for m in prompt_memories
                    if m.get("agent_type") == agent_type
                ]
            
            return prompt_memories
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar memórias: {e}")
            return []
    
    def get_agent_types(self) -> Dict[str, Dict]:
        """Obtém tipos de agente disponíveis"""
        return self.agent_types
    
    def get_status(self) -> Dict[str, Any]:
        """Obtém status do manager"""
        return {
            "api_key_configured": self.check_api_key(),
            "models_cached": len(self.models_cache),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "session_active": self.session is not None,
            "rate_limits": {
                "requests_per_minute": self.max_requests_per_minute,
                "requests_per_day": self.max_requests_per_day
            }
        }
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None 