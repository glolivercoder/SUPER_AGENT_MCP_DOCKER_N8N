#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicialização do SUPER_AGENT_MCP_DOCKER_N8N
Inicia todos os módulos necessários: GUI, MCP RAG, e outros serviços.
"""

import asyncio
import logging
import multiprocessing
import os
import sys
import time
import signal
from pathlib import Path
from typing import List, Dict, Any

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from modules.mcp_rag_module import run_server as run_mcp_server
    from GUI.gui_module_manager_fe import main as run_gui
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Verifique se as dependências estão instaladas: pip install -r requirements.txt")
    sys.exit(1)

# Configuração de logging
def setup_logging():
    """Configura sistema de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'super_agent.log'),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

class SuperAgentOrchestrator:
    """Orquestrador principal do SUPER_AGENT_MCP_DOCKER_N8N"""
    
    def __init__(self):
        self.processes: Dict[str, multiprocessing.Process] = {}
        self.is_running = False
        self.config = self.load_config()
        
        # Cria diretórios necessários
        self.create_directories()
        
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração global"""
        import json
        
        config_file = Path("config/app_config.json")
        default_config = {
            "mcp_host": "localhost",
            "mcp_port": 8000,
            "gui_enabled": True,
            "auto_start_mcp": True,
            "documents_directory": "./documents",
            "logs_directory": "./logs",
            "data_directory": "./data"
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return {**default_config, **user_config}
            except Exception as e:
                logger.warning(f"Erro ao carregar config: {e}. Usando padrão.")
        
        return default_config
    
    def create_directories(self):
        """Cria diretórios necessários"""
        directories = [
            self.config["documents_directory"],
            self.config["logs_directory"],
            self.config["data_directory"],
            "config"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório criado/verificado: {directory}")
    
    def start_mcp_server(self):
        """Inicia o servidor MCP RAG"""
        try:
            logger.info("Iniciando servidor MCP RAG...")
            host = self.config["mcp_host"]
            port = self.config["mcp_port"]
            
            # Função para executar em processo separado
            def run_mcp():
                try:
                    run_mcp_server(host, port)
                except Exception as e:
                    logger.error(f"Erro no servidor MCP: {e}")
            
            process = multiprocessing.Process(target=run_mcp, name="MCP_RAG_Server")
            process.start()
            
            self.processes["mcp_server"] = process
            logger.info(f"Servidor MCP iniciado em {host}:{port} (PID: {process.pid})")
            
            # Aguarda um pouco para o servidor inicializar
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor MCP: {e}")
            return False
    
    def start_gui(self):
        """Inicia a interface gráfica"""
        if not self.config["gui_enabled"]:
            logger.info("GUI desabilitada na configuração")
            return False
        
        try:
            logger.info("Iniciando interface gráfica...")
            
            def run_gui_process():
                try:
                    run_gui()
                except Exception as e:
                    logger.error(f"Erro na GUI: {e}")
            
            process = multiprocessing.Process(target=run_gui_process, name="GUI_Manager")
            process.start()
            
            self.processes["gui"] = process
            logger.info(f"GUI iniciada (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar GUI: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Verifica se todas as dependências estão instaladas"""
        required_packages = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sentence_transformers", "Sentence transformers"),
            ("chromadb", "Vector database"),
            ("websockets", "WebSocket support"),
            ("aiohttp", "HTTP client"),
            ("tkinter", "GUI framework")
        ]
        
        missing_packages = []
        for package, description in required_packages:
            try:
                if package == "tkinter":
                    import tkinter
                else:
                    __import__(package)
                logger.debug(f"✓ {package} ({description})")
            except ImportError:
                missing_packages.append((package, description))
                logger.error(f"✗ {package} ({description})")
        
        if missing_packages:
            logger.error("Pacotes faltando:")
            for package, description in missing_packages:
                logger.error(f"  - {package}: {description}")
            logger.error("Execute: pip install -r requirements.txt")
            return False
        
        logger.info("✓ Todas as dependências estão instaladas")
        return True
    
    def setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        def signal_handler(signum, frame):
            logger.info(f"Recebido sinal {signum}. Parando serviços...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    
    def start(self):
        """Inicia todos os serviços"""
        logger.info("=" * 50)
        logger.info("INICIANDO SUPER_AGENT_MCP_DOCKER_N8N")
        logger.info("=" * 50)
        
        # Verifica dependências
        if not self.check_dependencies():
            return False
        
        # Configura handlers de sinal
        self.setup_signal_handlers()
        
        # Inicia servidor MCP se configurado
        if self.config["auto_start_mcp"]:
            if not self.start_mcp_server():
                logger.error("Falha ao iniciar servidor MCP")
                return False
        
        # Inicia GUI
        if not self.start_gui():
            logger.warning("Falha ao iniciar GUI")
        
        self.is_running = True
        logger.info("=" * 50)
        logger.info("SUPER_AGENT_MCP_DOCKER_N8N INICIADO COM SUCESSO")
        logger.info("=" * 50)
        
        return True
    
    def stop(self):
        """Para todos os serviços"""
        logger.info("=" * 50)
        logger.info("PARANDO SUPER_AGENT_MCP_DOCKER_N8N")
        logger.info("=" * 50)
        
        for name, process in self.processes.items():
            if process and process.is_alive():
                logger.info(f"Parando {name}...")
                process.terminate()
                
                # Aguarda término gracioso
                process.join(timeout=5)
                
                # Force kill se necessário
                if process.is_alive():
                    process.kill()
                    logger.warning(f"{name} foi forçado a parar")
                else:
                    logger.info(f"✓ {name} parado")
        
        self.processes.clear()
        self.is_running = False
        logger.info("=" * 50)
        logger.info("SUPER_AGENT_MCP_DOCKER_N8N PARADO")
        logger.info("=" * 50)
    
    def status(self) -> Dict[str, Any]:
        """Retorna status dos serviços"""
        status_info = {
            "is_running": self.is_running,
            "processes": {},
            "config": self.config
        }
        
        for name, process in self.processes.items():
            status_info["processes"][name] = {
                "alive": process.is_alive() if process else False,
                "pid": process.pid if process and process.is_alive() else None
            }
        
        return status_info
    
    def monitor(self):
        """Monitora os serviços em execução"""
        logger.info("Iniciando monitoramento dos serviços...")
        
        try:
            while self.is_running:
                # Verifica se processos estão vivos
                for name, process in list(self.processes.items()):
                    if process and not process.is_alive():
                        logger.warning(f"Processo {name} morreu. Removendo da lista.")
                        self.processes.pop(name)
                
                # Aguarda antes da próxima verificação
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")

def print_banner():
    """Mostra banner do sistema"""
    banner = """
    ███████╗██╗   ██╗██████╗ ███████╗██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗
    ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
    ███████╗██║   ██║██████╔╝█████╗  ██████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
    ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
    ███████║╚██████╔╝██║     ███████╗██║  ██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
    ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
    
    ██╗  ██╗ ██████╗██████╗     ██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗     ███╗   ██╗ █████╗ ███╗   ██╗
    ██║ ██╔╝██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗    ████╗  ██║██╔══██╗████╗  ██║
    █████╔╝ ██║     ██████╔╝    ██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝    ██╔██╗ ██║╚█████╔╝██╔██╗ ██║
    ██╔═██╗ ██║     ██╔═══╝     ██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗    ██║╚██╗██║██╔══██╗██║╚██╗██║
    ██║  ██╗╚██████╗██║         ██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║    ██║ ╚████║╚█████╔╝██║ ╚████║
    ╚═╝  ╚═╝ ╚═════╝╚═╝         ╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═══╝ ╚════╝ ╚═╝  ╚═══╝
    
    🚀 Agente Especialista Multiplataforma - MCP, Docker, N8N & AI
    """
    print(banner)

def main():
    """Função principal"""
    print_banner()
    
    # Verifica argumentos da linha de comando
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SUPER_AGENT_MCP_DOCKER_N8N - Agente Especialista Multiplataforma",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--no-gui", action="store_true", help="Inicia sem interface gráfica")
    parser.add_argument("--no-mcp", action="store_true", help="Inicia sem servidor MCP")
    parser.add_argument("--host", default="localhost", help="Host do servidor MCP")
    parser.add_argument("--port", type=int, default=8000, help="Porta do servidor MCP")
    parser.add_argument("--status", action="store_true", help="Mostra status e sai")
    parser.add_argument("--version", action="version", version="SUPER_AGENT_MCP_DOCKER_N8N v1.0.0")
    
    args = parser.parse_args()
    
    # Cria orquestrador
    orchestrator = SuperAgentOrchestrator()
    
    # Atualiza configuração com argumentos
    if args.no_gui:
        orchestrator.config["gui_enabled"] = False
    if args.no_mcp:
        orchestrator.config["auto_start_mcp"] = False
    if args.host:
        orchestrator.config["mcp_host"] = args.host
    if args.port:
        orchestrator.config["mcp_port"] = args.port
    
    # Se é só para mostrar status
    if args.status:
        status = orchestrator.status()
        print("\n" + "=" * 50)
        print("STATUS SUPER_AGENT_MCP_DOCKER_N8N")
        print("=" * 50)
        print(f"Sistema executando: {'✓ SIM' if status['is_running'] else '✗ NÃO'}")
        print(f"Host MCP: {status['config']['mcp_host']}")
        print(f"Porta MCP: {status['config']['mcp_port']}")
        print("\nProcessos:")
        for name, proc_info in status['processes'].items():
            status_text = '✓ ATIVO' if proc_info['alive'] else '✗ INATIVO'
            pid_text = f"(PID: {proc_info['pid']})" if proc_info['pid'] else ""
            print(f"  {name}: {status_text} {pid_text}")
        print("=" * 50)
        return 0
    
    try:
        # Inicia os serviços
        if orchestrator.start():
            print(f"\n🌐 Servidor MCP: http://{orchestrator.config['mcp_host']}:{orchestrator.config['mcp_port']}")
            print(f"📊 Interface GUI: {'Iniciada' if orchestrator.config['gui_enabled'] else 'Desabilitada'}")
            print(f"🚀 Sistema iniciado com sucesso!")
            print(f"\n💡 Use Ctrl+C para parar o sistema")
            
            # Se GUI não está habilitada, faz monitoramento
            if not orchestrator.config["gui_enabled"]:
                orchestrator.monitor()
            else:
                # Aguarda processos terminarem
                for process in orchestrator.processes.values():
                    if process:
                        process.join()
        else:
            logger.error("❌ Falha ao iniciar serviços")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        return 1
    finally:
        orchestrator.stop()
    
    return 0

if __name__ == "__main__":
    # Configura multiprocessing para Windows
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    
    exit_code = main()
    sys.exit(exit_code) 