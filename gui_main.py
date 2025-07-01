#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI Main - Inicializador da Interface Gráfica
---------------------------------------------
Arquivo principal para iniciar a interface gráfica do SUPER_AGENT_MCP_DOCKER_N8N
com todos os módulos integrados.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import messagebox

# Importar o agente principal e a GUI
from main import SuperAgent
from GUI.gui_module import SuperAgentGUI

def setup_logging():
    """Configura o sistema de logging"""
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join("logs", "super_agent_gui.log")),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("GUI_MAIN")
    logger.info("Sistema de logging configurado")
    return logger

def main():
    """Função principal para iniciar a aplicação"""
    logger = setup_logging()
    
    try:
        # Verificar se estamos no diretório correto
        if not os.path.exists("modules"):
            logger.error("Diretório 'modules' não encontrado. Execute a partir do diretório raiz do projeto.")
            messagebox.showerror(
                "Erro", 
                "Diretório 'modules' não encontrado.\nExecute a partir do diretório raiz do projeto."
            )
            return
        
        # Criar janela principal
        root = tk.Tk()
        root.withdraw()  # Esconder temporariamente
        
        # Mostrar splash screen
        splash = create_splash_screen()
        
        try:
            # Inicializar o Super Agent
            logger.info("Inicializando SUPER_AGENT_MCP_DOCKER_N8N...")
            splash.update_status("Inicializando SUPER_AGENT_MCP_DOCKER_N8N...")
            
            agent = SuperAgent()
            
            splash.update_status("Carregando configurações MCP...")
            agent.load_mcp_configs()
            
            splash.update_status("Iniciando serviços...")
            agent.start_services()
            
            # Criar interface gráfica integrada
            splash.update_status("Inicializando interface gráfica...")
            
            # Mostrar janela principal
            root.deiconify()
            
            # Criar GUI com referência ao agente
            gui = SuperAgentGUI(root)
            gui.agent = agent  # Passar referência do agente para a GUI
            
            # Configurar callbacks entre GUI e agente
            setup_gui_agent_integration(gui, agent)
            
            # Fechar splash screen
            splash.destroy()
            
            # Anúncio de inicialização via voz
            if agent.voice_module and agent.voice_module.voice_config.get("enabled", False):
                agent.voice_module.speak("Interface gráfica do Super Agent inicializada com sucesso!")
            
            logger.info("Interface gráfica inicializada com sucesso")
            
            # Iniciar loop principal
            gui.run()
            
        except Exception as e:
            splash.destroy()
            logger.error(f"Erro durante inicialização: {e}")
            messagebox.showerror("Erro de Inicialização", f"Erro durante inicialização:\n{str(e)}")
            
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        messagebox.showerror("Erro Fatal", f"Erro fatal na aplicação:\n{str(e)}")

def create_splash_screen():
    """Cria tela de splash durante inicialização"""
    splash = tk.Toplevel()
    splash.title("SUPER_AGENT_MCP_DOCKER_N8N")
    splash.geometry("400x200")
    splash.resizable(False, False)
    
    # Centralizar na tela
    splash.update_idletasks()
    x = (splash.winfo_screenwidth() // 2) - (400 // 2)
    y = (splash.winfo_screenheight() // 2) - (200 // 2)
    splash.geometry(f"400x200+{x}+{y}")
    
    # Remover decorações da janela
    splash.overrideredirect(True)
    
    # Frame principal
    main_frame = tk.Frame(splash, bg="#2c3e50", relief="raised", bd=2)
    main_frame.pack(fill="both", expand=True)
    
    # Título
    title_label = tk.Label(
        main_frame, 
        text="SUPER_AGENT_MCP_DOCKER_N8N",
        font=("Arial", 16, "bold"),
        fg="white",
        bg="#2c3e50"
    )
    title_label.pack(pady=20)
    
    # Subtítulo
    subtitle_label = tk.Label(
        main_frame,
        text="Agente Especializado para Integração MCP",
        font=("Arial", 10),
        fg="#ecf0f1",
        bg="#2c3e50"
    )
    subtitle_label.pack(pady=5)
    
    # Barra de progresso simulada
    progress_frame = tk.Frame(main_frame, bg="#2c3e50")
    progress_frame.pack(pady=20)
    
    progress_bar = tk.Frame(progress_frame, bg="#34495e", width=300, height=20)
    progress_bar.pack()
    
    progress_fill = tk.Frame(progress_bar, bg="#3498db", height=20)
    progress_fill.place(x=0, y=0, width=0, height=20)
    
    # Status
    status_label = tk.Label(
        main_frame,
        text="Inicializando...",
        font=("Arial", 9),
        fg="#bdc3c7",
        bg="#2c3e50"
    )
    status_label.pack(pady=10)
    
    # Adicionar métodos à janela splash
    splash.status_label = status_label
    splash.progress_fill = progress_fill
    splash.progress_width = 0
    
    def update_status(status_text):
        splash.status_label.config(text=status_text)
        splash.progress_width = min(splash.progress_width + 60, 300)
        splash.progress_fill.config(width=splash.progress_width)
        splash.update()
    
    splash.update_status = update_status
    
    return splash

def setup_gui_agent_integration(gui, agent):
    """Configura integração entre GUI e agente"""
    # Adicionar referências aos módulos na GUI
    gui.mcp_manager = agent.mcp_manager
    gui.docker_manager = agent.docker_manager
    gui.rag_system = agent.rag_system
    gui.fe_agent = agent.fe_agent
    gui.voice_module = agent.voice_module
    
    # Configurar callbacks personalizados
    def on_mcp_action(action, data):
        """Callback para ações de MCP"""
        if action == "detect_mcps":
            mcps = agent.mcp_manager.detect_installed_mcps()
            if agent.voice_module:
                count = len(mcps)
                agent.voice_module.speak(f"Detectados {count} MCPs instalados")
            return mcps
        elif action == "share_config":
            source, target = data
            result = agent.mcp_manager.share_config(source, target)
            if agent.voice_module:
                if result:
                    agent.voice_module.speak("Configuração compartilhada com sucesso")
                else:
                    agent.voice_module.speak("Erro ao compartilhar configuração")
            return result
    
    def on_docker_action(action, data=None):
        """Callback para ações de Docker"""
        if action == "check_docker":
            result = agent.docker_manager.check_docker_installed()
            if agent.voice_module:
                if result:
                    agent.voice_module.speak("Docker está funcionando corretamente")
                else:
                    agent.voice_module.speak("Docker não foi encontrado")
            return result
        elif action == "start_n8n":
            port = data.get("port", 5678) if data else 5678
            result = agent.docker_manager.start_n8n(port=port)
            if agent.voice_module:
                if result:
                    agent.voice_module.speak(f"N8N iniciado na porta {port}")
                else:
                    agent.voice_module.speak("Erro ao iniciar N8N")
            return result
    
    def on_fe_action(action, data=None):
        """Callback para ações do Fê Agent"""
        if action == "git_command":
            command = data.get("command", "") if data else ""
            result = agent.fe_agent.process_voice_command(f"Fê, {command}")
            if agent.voice_module:
                agent.voice_module.speak(result["message"])
            return result
        elif action == "analyze_project":
            analysis = agent.fe_agent.analyze_project()
            if agent.voice_module:
                agent.voice_module.speak(analysis["message"])
            return analysis
        elif action == "git_status":
            result = agent.fe_agent.process_voice_command("Fê, status")
            if agent.voice_module:
                agent.voice_module.speak(result["message"])
            return result
    
    def on_voice_action(action, data=None):
        """Callback para ações de voz"""
        if action == "start_listening":
            agent.voice_module.start_continuous_listening()
            return True
        elif action == "stop_listening":
            agent.voice_module.stop_continuous_listening()
            return True
        elif action == "speak":
            text = data.get("text", "") if data else ""
            return agent.voice_module.speak(text)
    
    # Atribuir callbacks à GUI
    gui.on_mcp_action = on_mcp_action
    gui.on_docker_action = on_docker_action
    gui.on_fe_action = on_fe_action
    gui.on_voice_action = on_voice_action

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1) 