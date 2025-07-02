#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SUPER_AGENT_MCP_DOCKER_N8N
--------------------------
Agente especializado para integrar MCPs (Model Context Protocols) de diferentes IDEs
como Cline, RooCline, Windsurf e Cursor, coordenar comandos, iniciar serviços
e analisar prompts para determinar a melhor arquitetura.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import sys
import json
import logging
from pathlib import Path

# Importar módulos do sistema
from modules.mcp_manager import MCPManager
from modules.docker_manager import DockerManager
from modules.rag_system import RAGSystem
from modules.fe_agent import FeAgent
from modules.voice_module import VoiceModule
from modules.openrouter_manager import OpenRouterManager
from modules.database_manager import DatabaseManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "super_agent.log")),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("SUPER_AGENT")

class SuperAgent:
    """Classe principal do SUPER_AGENT_MCP_DOCKER_N8N"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.modules_dir = Path("modules")
        self.logger = logger
        self.mcp_configs = {}
        
        # Inicializar módulos
        self.database_manager = None
        self.mcp_manager = None
        self.docker_manager = None
        self.rag_system = None
        self.fe_agent = None
        self.voice_module = None
        self.openrouter_manager = None
        
        self.logger.info("Inicializando SUPER_AGENT_MCP_DOCKER_N8N")
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Inicializa todos os módulos do sistema"""
        try:
            # Criar diretório de logs se não existir
            os.makedirs("logs", exist_ok=True)
            
            # Inicializar Database Manager primeiro
            self.database_manager = DatabaseManager()
            self.logger.info("Database Manager inicializado")
            
            # Inicializar MCP Manager
            self.mcp_manager = MCPManager()
            self.logger.info("MCP Manager inicializado")
            
            # Inicializar Docker Manager
            self.docker_manager = DockerManager()
            self.logger.info("Docker Manager inicializado")
            
            # Inicializar RAG System
            self.rag_system = RAGSystem()
            self.logger.info("RAG System inicializado")
            
            # Inicializar Fê Agent
            self.fe_agent = FeAgent()
            self.logger.info("Fê Agent inicializado")
            
            # Inicializar Voice Module
            self.voice_module = VoiceModule()
            self._setup_voice_commands()
            self.logger.info("Voice Module inicializado")
            
            # Inicializar OpenRouter Manager com Database Manager
            self.openrouter_manager = OpenRouterManager(self.database_manager)
            self.logger.info("OpenRouter Manager inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar módulos: {e}")
    
    def _setup_voice_commands(self):
        """Configura comandos de voz personalizados"""
        def voice_command_handler(command, action):
            self.logger.info(f"Comando de voz recebido: {command} -> {action}")
            
            # Verificar se é comando do Fê Agent
            if any(wake_word in command.lower() for wake_word in ["fê", "fe"]):
                result = self.fe_agent.process_voice_command(command)
                if result["success"]:
                    self.voice_module.speak(result["message"])
                else:
                    self.voice_module.speak(f"Erro: {result['message']}")
                return
            
            # Comandos do sistema
            if action == "docker_status":
                if self.docker_manager.check_docker_installed():
                    self.voice_module.speak("Docker está instalado e funcionando")
                else:
                    self.voice_module.speak("Docker não foi encontrado")
            elif action == "mcp_status":
                mcps = self.mcp_manager.detect_installed_mcps()
                count = len(mcps)
                self.voice_module.speak(f"Encontrados {count} MCPs instalados")
            elif action == "unknown":
                # Tentar processar como comando do Fê Agent
                result = self.fe_agent.process_voice_command(command)
                if result["success"]:
                    self.voice_module.speak(result["message"])
                else:
                    self.voice_module.speak("Comando não reconhecido. Diga 'ajuda' para ver os comandos disponíveis.")
        
        self.voice_module.set_command_callback(voice_command_handler)
        
    def load_mcp_configs(self):
        """Carrega as configurações de MCPs de diferentes IDEs"""
        try:
            config_files = list(self.config_dir.glob("*.json"))
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.mcp_configs[config_file.stem] = config
            self.logger.info(f"Configurações de MCP carregadas: {list(self.mcp_configs.keys())}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações de MCP: {e}")
    
    def start_services(self):
        """Inicia os serviços necessários no diretório do projeto"""
        self.logger.info("Iniciando serviços...")
        
        # Verificar Docker
        if self.docker_manager.check_docker_installed():
            self.logger.info("Docker verificado com sucesso")
            # Opcional: iniciar N8N automaticamente
            # self.docker_manager.start_n8n()
        else:
            self.logger.warning("Docker não encontrado - alguns serviços podem não funcionar")
        
        # Inicializar Voice Module se habilitado
        if self.voice_module and self.voice_module.voice_config.get("enabled", False):
            self.voice_module.speak("SUPER AGENT M C P Docker N8N inicializado com sucesso!")
            
        # Análise inicial do projeto se Fê Agent estiver ativo
        if self.fe_agent and self.fe_agent.fe_config.get("enabled", False):
            if self.fe_agent.fe_config.get("project_analysis", True):
                analysis = self.fe_agent.analyze_project()
                if analysis["success"]:
                    self.logger.info(f"Análise do projeto: {analysis['message']}")
                else:
                    self.logger.warning(f"Erro na análise: {analysis['message']}")
        
    def analyze_prompt(self, prompt):
        """Analisa prompts para determinar a melhor arquitetura, estrutura de dados e bibliotecas UI"""
        self.logger.info(f"Analisando prompt: {prompt[:50]}...")
        
        analysis = {
            "arquitetura": "microservices",
            "estrutura_dados": "graph",
            "bibliotecas_ui": ["react", "material-ui"],
            "technologies": [],
            "ethical_analysis": None,
            "spiritual_guidance": None
        }
        
        # Análise técnica básica
        prompt_lower = prompt.lower()
        
        # Determinar arquitetura
        if any(word in prompt_lower for word in ["monolito", "simples", "pequeno"]):
            analysis["arquitetura"] = "monolithic"
        elif any(word in prompt_lower for word in ["micro", "distribuido", "escalavel"]):
            analysis["arquitetura"] = "microservices"
        elif any(word in prompt_lower for word in ["serverless", "lambda", "funcoes"]):
            analysis["arquitetura"] = "serverless"
        
        # Determinar estrutura de dados
        if any(word in prompt_lower for word in ["relacional", "sql", "tabelas"]):
            analysis["estrutura_dados"] = "relational"
        elif any(word in prompt_lower for word in ["nosql", "documento", "mongodb"]):
            analysis["estrutura_dados"] = "document"
        elif any(word in prompt_lower for word in ["grafo", "neo4j", "relacionamento"]):
            analysis["estrutura_dados"] = "graph"
        
        # Determinar tecnologias
        if "python" in prompt_lower:
            analysis["technologies"].append("Python")
        if "react" in prompt_lower or "frontend" in prompt_lower:
            analysis["technologies"].append("React")
        if "docker" in prompt_lower:
            analysis["technologies"].append("Docker")
        if "n8n" in prompt_lower or "automacao" in prompt_lower:
            analysis["technologies"].append("N8N")
        
        # Análise de desenvolvimento se Fê Agent estiver ativo
        if self.fe_agent and self.fe_agent.fe_config.get("project_analysis", True):
            project_analysis = self.fe_agent.analyze_project()
            if project_analysis["success"]:
                analysis["project_info"] = project_analysis["details"]
                analysis["git_suggestions"] = project_analysis["details"].get("suggestions", [])
        
        return analysis
    
    def run(self):
        """Método principal para executar o agente"""
        self.load_mcp_configs()
        self.start_services()
        self.logger.info("SUPER_AGENT_MCP_DOCKER_N8N está em execução")


if __name__ == "__main__":
    agent = SuperAgent()
    agent.run() 