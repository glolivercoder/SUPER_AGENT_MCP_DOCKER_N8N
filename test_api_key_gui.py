#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste da API Key na GUI
-----------------------
Script para verificar se a API key está sendo carregada corretamente na GUI
"""

import os
import sys
import logging
from datetime import datetime

# Configurar API Key do OpenRouter se não estiver definida
if not os.getenv('OPENROUTER_API_KEY'):
    os.environ['OPENROUTER_API_KEY'] = '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'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_key_loading():
    """Testa se a API key está sendo carregada corretamente"""
    print("=== TESTE DE CARREGAMENTO DA API KEY ===")
    
    # 1. Verificar se a API key está definida no ambiente
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    print(f"1. API Key no ambiente: {'✓ Definida' if api_key else '✗ Não definida'}")
    if api_key:
        print(f"   Valor: {api_key[:20]}...{api_key[-10:]}")
    
    # 2. Testar OpenRouterManager diretamente
    try:
        from modules.openrouter_manager import OpenRouterManager
        manager = OpenRouterManager()
        print(f"2. OpenRouterManager API Key: {'✓ Carregada' if manager.api_key else '✗ Não carregada'}")
        if manager.api_key:
            print(f"   Valor: {manager.api_key[:20]}...{manager.api_key[-10:]}")
        
        # 3. Testar se a API key é válida
        is_valid = manager.check_api_key()
        print(f"3. API Key válida: {'✓ Sim' if is_valid else '✗ Não'}")
        
        # 4. Testar carregamento de modelos
        print("4. Testando carregamento de modelos...")
        models = manager.get_models()
        print(f"   Modelos carregados: {len(models)}")
        if models:
            print(f"   Primeiro modelo: {models[0].name}")
        
    except Exception as e:
        print(f"✗ Erro ao testar OpenRouterManager: {e}")
    
    # 5. Testar GUI com injeção de dependências (como no main.py)
    try:
        import tkinter as tk
        from GUI.gui_module import SuperAgentGUI
        
        print("5. Testando GUI com injeção de dependências...")
        root = tk.Tk()
        root.withdraw()  # Esconder janela
        
        app = SuperAgentGUI(root)
        
        # Simular injeção de dependências como no main.py
        setattr(app, 'openrouter_manager', manager)
        
        # Verificar se o OpenRouterManager foi injetado
        has_manager = hasattr(app, 'openrouter_manager') and app.openrouter_manager is not None
        print(f"   OpenRouterManager injetado: {'✓ Sim' if has_manager else '✗ Não'}")
        
        if has_manager:
            # Verificar se a API key está no manager da GUI
            gui_api_key = app.openrouter_manager.api_key if app.openrouter_manager else None
            print(f"   API Key na GUI: {'✓ Carregada' if gui_api_key else '✗ Não carregada'}")
            if gui_api_key:
                print(f"   Valor: {gui_api_key[:20]}...{gui_api_key[-10:]}")
            
            # Testar carregamento de modelos na GUI
            print("   Testando carregamento de modelos na GUI...")
            try:
                if app.openrouter_manager:
                    models = app.openrouter_manager.get_models()
                    print(f"   Modelos na GUI: {len(models)}")
                    if models:
                        print(f"   Primeiro modelo na GUI: {models[0].name}")
                else:
                    print("   ✗ OpenRouterManager é None")
            except Exception as e:
                print(f"   ✗ Erro ao carregar modelos na GUI: {e}")
        
        root.destroy()
        
    except Exception as e:
        print(f"✗ Erro ao testar GUI: {e}")

if __name__ == "__main__":
    test_api_key_loading() 