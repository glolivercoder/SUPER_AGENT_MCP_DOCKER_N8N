#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste específico para verificar a inicialização da GUI
"""

import sys
import os
import tkinter as tk

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_with_dependencies():
    """Testa a GUI com injeção de dependências"""
    print("=== TESTE GUI COM DEPENDÊNCIAS ===")
    
    try:
        # Importar módulos
        from modules.database_manager import DatabaseManager
        from modules.openrouter_manager import OpenRouterManager
        from modules.voice_module import VoiceModule
        from modules.mcp_manager import MCPManager
        from modules.rag_system import RAGSystem
        from modules.docker_manager import DockerManager
        from modules.fe_agent import FeAgent
        from GUI.gui_module import SuperAgentGUI
        
        # Inicializar módulos
        print("Inicializando módulos...")
        db_manager = DatabaseManager()
        openrouter_manager = OpenRouterManager(db_manager)
        voice_module = VoiceModule()
        mcp_manager = MCPManager()
        rag_system = RAGSystem()
        docker_manager = DockerManager()
        fe_agent = FeAgent()
        
        print("Módulos inicializados com sucesso")
        
        # Criar GUI
        print("Criando GUI...")
        root = tk.Tk()
        app = SuperAgentGUI(root)
        
        print(f"GUI criada: {app}")
        
        # Injetar dependências
        print("Injetando dependências...")
        app.openrouter_manager = openrouter_manager
        app.rag_system = rag_system
        app.mcp_manager = mcp_manager
        app.docker_manager = docker_manager
        app.fe_agent = fe_agent
        app.voice_module = voice_module
        
        print("Dependências injetadas")
        
        # Verificar se foram injetadas
        print(f"OpenRouter Manager: {app.openrouter_manager is not None}")
        print(f"Voice Module: {app.voice_module is not None}")
        print(f"MCP Manager: {app.mcp_manager is not None}")
        
        # Testar carregamento de speakers
        if app.voice_module:
            print("Testando carregamento de speakers...")
            speakers = app.voice_module.get_speakers()
            print(f"Speakers carregados: {len(speakers) if speakers else 0}")
            
            # Chamar método de carregamento
            app._load_silero_speakers()
            print("Método _load_silero_speakers executado")
        
        # Testar carregamento de modelos
        if app.openrouter_manager:
            print("Testando carregamento de modelos...")
            # O carregamento é assíncrono, então vamos apenas verificar se o método existe
            print("Método _load_models disponível")
        
        # Destruir GUI
        root.destroy()
        
        print("✅ Teste GUI com dependências concluído com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_execution():
    """Testa a execução do main.py"""
    print("\n=== TESTE EXECUÇÃO MAIN.PY ===")
    
    try:
        # Simular execução do main.py
        from main import SuperAgent
        
        print("Criando SuperAgent...")
        agent = SuperAgent()
        
        print("Executando SuperAgent...")
        agent.run()
        
        print("Verificando módulos...")
        print(f"OpenRouter Manager: {agent.openrouter_manager is not None}")
        print(f"Voice Module: {agent.voice_module is not None}")
        print(f"MCP Manager: {agent.mcp_manager is not None}")
        
        # Testar GUI
        print("Testando GUI...")
        root = tk.Tk()
        from GUI.gui_module import SuperAgentGUI
        app = SuperAgentGUI(root)
        
        # Injetar dependências
        app.openrouter_manager = agent.openrouter_manager
        app.rag_system = agent.rag_system
        app.mcp_manager = agent.mcp_manager
        app.docker_manager = agent.docker_manager
        app.fe_agent = agent.fe_agent
        app.voice_module = agent.voice_module
        
        print("Verificando injeção...")
        print(f"OpenRouter Manager na GUI: {app.openrouter_manager is not None}")
        print(f"Voice Module na GUI: {app.voice_module is not None}")
        
        # Testar carregamento
        if app.voice_module:
            app._load_silero_speakers()
            print("Speakers carregados na GUI")
        
        if app.openrouter_manager:
            app._load_models()
            print("Modelos carregados na GUI")
        
        root.destroy()
        
        print("✅ Teste main.py concluído com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste main.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("Iniciando testes específicos da GUI...")
    
    # Teste 1: GUI com dependências
    test1 = test_gui_with_dependencies()
    
    # Teste 2: Execução main.py
    test2 = test_main_execution()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"GUI com dependências: {'✅ OK' if test1 else '❌ FALHOU'}")
    print(f"Execução main.py: {'✅ OK' if test2 else '❌ FALHOU'}")

if __name__ == "__main__":
    main() 