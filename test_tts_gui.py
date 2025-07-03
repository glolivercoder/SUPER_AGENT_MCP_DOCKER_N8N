#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do TTS na GUI - SUPER_AGENT_MCP_DOCKER_N8N
-------------------------------------------------
Testa se o TTS está funcionando corretamente na interface gráfica

Autor: [Seu Nome]
Data: 02/07/2025
Versão: 0.1.0
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_tts_gui():
    """Testa o TTS na GUI"""
    print("🔊 Testando TTS na GUI...")
    
    try:
        # Importar módulos necessários
        from GUI.gui_module import SuperAgentGUI
        from modules.voice_module import VoiceModule
        from modules.openrouter_manager import OpenRouterManager
        from modules.rag_system import RAGSystem
        from modules.mcp_manager import MCPManager
        from modules.docker_manager import DockerManager
        from modules.fe_agent import FeAgent
        
        # Criar janela de teste
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal
        
        # Criar instância da GUI
        app = SuperAgentGUI(root)
        
        # Simular injeção de dependências como no main.py
        print("🔧 Simulando injeção de dependências...")
        
        # Criar módulos
        voice_module = VoiceModule()
        openrouter_manager = OpenRouterManager()
        rag_system = RAGSystem()
        mcp_manager = MCPManager()
        docker_manager = DockerManager()
        fe_agent = FeAgent()
        
        # Injetar dependências
        app.openrouter_manager = openrouter_manager
        app.rag_system = rag_system
        app.mcp_manager = mcp_manager
        app.docker_manager = docker_manager
        app.fe_agent = fe_agent
        app.voice_module = voice_module
        
        print("✅ Dependências injetadas")
        
        # Verificar se o módulo de voz foi injetado
        if hasattr(app, 'voice_module') and app.voice_module:
            print("✅ Módulo de voz injetado na GUI")
            
            # Testar TTS diretamente
            print("🧪 Testando TTS diretamente...")
            result = app.voice_module.speak("Teste de TTS na GUI")
            if result:
                print("✅ TTS funcionou diretamente!")
            else:
                print("❌ TTS falhou diretamente!")
                
            # Verificar status do TTS
            status = app.voice_module.get_status()
            print(f"📊 Status do TTS:")
            print(f"  TTS Ready: {status['tts_ready']}")
            print(f"  Current Speaker: {status['current_speaker']}")
            print(f"  Available Speakers: {status['available_speakers']}")
            
            # Verificar se há vozes disponíveis
            speakers = app.voice_module.get_speakers()
            print(f"🎤 Vozes disponíveis ({len(speakers)}):")
            for i, speaker in enumerate(speakers):
                print(f"  {i+1}. {speaker}")
                
        else:
            print("❌ Módulo de voz não foi injetado na GUI")
            
        # Verificar se há área de teste de TTS na GUI
        if hasattr(app, 'tts_test_entry'):
            print("✅ Área de teste de TTS encontrada na GUI")
            
            # Simular teste de TTS
            test_text = "Teste de voz na interface gráfica"
            print(f"🧪 Simulando teste com texto: '{test_text}'")
            
            # Verificar se o método de teste existe
            if hasattr(app, '_test_tts'):
                print("✅ Método de teste de TTS encontrado")
            else:
                print("❌ Método de teste de TTS não encontrado")
                
        else:
            print("❌ Área de teste de TTS não encontrada na GUI")
            
        # Verificar todas as abas da GUI
        if hasattr(app, 'notebook'):
            tabs = app.notebook.tabs()
            print(f"📑 Abas encontradas: {len(tabs)}")
            for i, tab in enumerate(tabs):
                tab_name = app.notebook.tab(tab, "text")
                print(f"  {i+1}. {tab_name}")
                
        # Verificar especificamente a aba de voz
        if hasattr(app, 'voice_tab'):
            print("✅ Aba de voz encontrada")
            
            # Verificar elementos da aba de voz
            voice_elements = []
            for widget in app.voice_tab.winfo_children():
                if hasattr(widget, 'winfo_name'):
                    voice_elements.append(widget.winfo_name())
                    
            print(f"🔧 Elementos na aba de voz: {len(voice_elements)}")
            for element in voice_elements[:10]:  # Mostrar apenas os primeiros 10
                print(f"  - {element}")
                
        else:
            print("❌ Aba de voz não encontrada")
            
        # Testar método de teste de TTS se existir
        if hasattr(app, '_test_tts'):
            print("🧪 Testando método _test_tts...")
            try:
                app._test_tts()
                print("✅ Método _test_tts executado com sucesso")
            except Exception as e:
                print(f"❌ Erro ao executar _test_tts: {e}")
                
        root.destroy()
        
    except Exception as e:
        print(f"❌ Erro ao testar TTS na GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts_gui() 