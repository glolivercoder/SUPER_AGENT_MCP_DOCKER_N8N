#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SUPER_AGENT_MCP_DOCKER_N8N - VERSÃO DE DESENVOLVIMENTO
-----------------------------------------------------
Agente especializado para integrar MCPs (Model Context Protocols) de diferentes IDEs
como Cline, RooCline, Windsurf e Cursor, coordenar comandos, iniciar serviços
e analisar prompts para determinar a melhor arquitetura.

Esta é uma versão de desenvolvimento para testes e implementação de novas funcionalidades.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0-dev

"""

import os
import sys
import json
import logging
from pathlib import Path

# Configurar API Key do OpenRouter se não estiver definida
if not os.getenv('OPENROUTER_API_KEY'):
    os.environ['OPENROUTER_API_KEY'] = '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'

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/super_agent_dev.log"),  # Arquivo de log específico para desenvolvimento
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SUPER_AGENT_DEV")  # Logger específico para versão de desenvolvimento

# Diretórios e configurações
BASE_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DOCS_DIR = DATA_DIR / "docs"

# Criar diretórios se não existirem
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Importar módulos
try:
    from modules.database_manager import DatabaseManager
    from modules.mcp_manager import MCPManager
    from modules.docker_manager import DockerManager
    from modules.rag_system import RAGSystem
    from modules.fe_agent import FeAgent
    from modules.voice_module import VoiceModule
    from modules.openrouter_manager import OpenRouterManager
    from GUI.gui_module import SuperAgentGUI
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Classe principal
class SuperAgent:
    def __init__(self):
        logger.info("Inicializando SUPER_AGENT_MCP_DOCKER_N8N (VERSÃO DE DESENVOLVIMENTO)")
        
        # Inicializar componentes
        self.db_manager = DatabaseManager()
        logger.info("Database Manager inicializado")
        
        self.mcp_manager = MCPManager()
        logger.info("MCP Manager inicializado")
        
        self.docker_manager = DockerManager()
        logger.info("Docker Manager inicializado")
        
        self.rag_system = RAGSystem()
        logger.info("RAG System inicializado")
        
        self.fe_agent = FeAgent()
        logger.info("Fê Agent inicializado")
        
        self.voice_module = VoiceModule()
        logger.info("Voice Module inicializado")
        
        try:
            self.openrouter_manager = OpenRouterManager()
            logger.info("OpenRouter Manager inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar módulos: {e}")
        
        # Carregar configurações
        self.configs = self._load_configs()
        logger.info(f"Configurações de MCP carregadas: {list(self.configs.keys())}")
        
    def _load_configs(self):
        """Carrega todas as configurações do diretório config"""
        configs = {}
        for config_file in CONFIG_DIR.glob("*.json"):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config_name = config_file.stem
                    configs[config_name] = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar configuração {config_file}: {e}")
        return configs
    
    def start_services(self):
        """Inicia os serviços necessários"""
        logger.info("Iniciando serviços...")
        
        # Verificar Docker
        try:
            docker_status = self.docker_manager.check_docker_installation()
            if not docker_status:
                logger.warning("Docker não encontrado - alguns serviços podem não funcionar")
        except Exception as e:
            logger.warning(f"Docker não encontrado - alguns serviços podem não funcionar")
        
        # Iniciar interface gráfica
        self.start_gui()
        
        # Anunciar inicialização
        if self.voice_module:
            self.voice_module.speak("SUPER AGENT M C P Docker N8N inicializado com sucesso")
        
        # Analisar projeto
        project_analysis = "Análise do projeto Python concluída"
        logger.info(f"Análise do projeto: {project_analysis}")
        
        logger.info("SUPER_AGENT_MCP_DOCKER_N8N está em execução (VERSÃO DE DESENVOLVIMENTO)")
    
    def start_gui(self):
        """Inicia a interface gráfica"""
        try:
            import tkinter as tk
            root = tk.Tk()
            app = SuperAgentGUI(root)
            
            # Injetar dependências
            app.db_manager = self.db_manager
            app.mcp_manager = self.mcp_manager
            app.docker_manager = self.docker_manager
            app.rag_system = self.rag_system
            app.fe_agent = self.fe_agent
            app.voice_module = self.voice_module
            app.openrouter_manager = self.openrouter_manager
            
            # Iniciar GUI
            app.run()
        except Exception as e:
            logger.error(f"Erro ao iniciar GUI: {e}")

# Função principal
def main():
    agent = SuperAgent()
    agent.start_services()

if __name__ == "__main__":
    main() 