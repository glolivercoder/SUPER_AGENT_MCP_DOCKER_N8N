#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar problemas com OpenRouter e TTS
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openrouter():
    """Testa o carregamento dos modelos OpenRouter"""
    print("=== TESTE OPENROUTER ===")
    try:
        from modules.openrouter_manager import OpenRouterManager
        from modules.database_manager import DatabaseManager
        
        # Inicializar com database manager
        db_manager = DatabaseManager()
        orm = OpenRouterManager(db_manager)
        
        print(f"API Key configurada: {orm.check_api_key()}")
        
        # Testar carregamento assíncrono
        async def load_models():
            models = await orm.get_models()
            print(f"Modelos carregados: {len(models)}")
            if models:
                print("Primeiros 5 modelos:")
                for i, model in enumerate(models[:5]):
                    print(f"  {i+1}. {model.name} ({model.company})")
            return models
        
        # Executar teste assíncrono
        models = asyncio.run(load_models())
        return models
        
    except Exception as e:
        print(f"Erro no teste OpenRouter: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_voice_module():
    """Testa o carregamento dos speakers TTS"""
    print("\n=== TESTE VOICE MODULE ===")
    try:
        from modules.voice_module import VoiceModule
        
        vm = VoiceModule()
        status = vm.get_status()
        print(f"Status TTS: {status['tts_ready']}")
        print(f"Status STT: {status['stt_ready']}")
        
        speakers = vm.get_speakers()
        print(f"Speakers disponíveis: {len(speakers)}")
        if speakers:
            print("Primeiros 10 speakers:")
            for i, speaker in enumerate(speakers[:10]):
                print(f"  {i+1}. {speaker}")
        
        return vm, speakers
        
    except Exception as e:
        print(f"Erro no teste Voice Module: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_gui_integration():
    """Testa a integração com a GUI"""
    print("\n=== TESTE INTEGRAÇÃO GUI ===")
    try:
        from GUI.gui_module import SuperAgentGUI
        import tkinter as tk
        
        # Criar GUI
        root = tk.Tk()
        app = SuperAgentGUI(root)
        
        # Testar se voice_module está disponível
        print(f"Voice module na GUI: {app.voice_module is not None}")
        
        # Testar se openrouter_manager está disponível
        print(f"OpenRouter manager na GUI: {app.openrouter_manager is not None}")
        
        # Testar carregamento de speakers
        if app.voice_module:
            speakers = app.voice_module.get_speakers()
            print(f"Speakers na GUI: {len(speakers) if speakers else 0}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Erro no teste GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("Iniciando testes de diagnóstico...")
    
    # Teste OpenRouter
    models = test_openrouter()
    
    # Teste Voice Module
    voice_module, speakers = test_voice_module()
    
    # Teste GUI
    gui_ok = test_gui_integration()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"OpenRouter: {'✅ OK' if models else '❌ FALHOU'}")
    print(f"Voice Module: {'✅ OK' if voice_module else '❌ FALHOU'}")
    print(f"GUI Integration: {'✅ OK' if gui_ok else '❌ FALHOU'}")
    
    if models:
        print(f"  - Modelos OpenRouter: {len(models)}")
    if speakers:
        print(f"  - Speakers TTS: {len(speakers)}")

if __name__ == "__main__":
    main() 