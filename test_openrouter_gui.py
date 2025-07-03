#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste da GUI do OpenRouter
--------------------------
Script para testar se a GUI está carregando os modelos corretamente
"""

import os
import sys
import asyncio
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

def test_openrouter_gui():
    """Testa a GUI do OpenRouter"""
    print("=== TESTE DA GUI DO OPENROUTER ===")
    
    try:
        from modules.openrouter_manager import OpenRouterManager
        from GUI.openrouter_gui import OpenRouterGUI
        import tkinter as tk
        
        # Inicializar OpenRouterManager
        print("1. Inicializando OpenRouterManager...")
        openrouter_manager = OpenRouterManager()
        print(f"   OpenRouterManager inicializado: {openrouter_manager is not None}")
        
        # Testar carregamento de modelos
        print("2. Testando carregamento de modelos...")
        models = asyncio.run(openrouter_manager.get_models())
        print(f"   Modelos carregados: {len(models)}")
        
        if models:
            print("   Primeiros 3 modelos:")
            for i, model in enumerate(models[:3]):
                print(f"     {i+1}. {model['name']} ({model['company']})")
        
        # Testar GUI
        print("3. Testando GUI...")
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal
        
        gui = OpenRouterGUI(root)
        print(f"   GUI criada: {gui is not None}")
        
        # Testar carregamento de modelos na GUI
        print("4. Testando carregamento de modelos na GUI...")
        gui._load_models_async()
        print("   Método _load_models_async() executado")
        
        # Verificar se há modelos na GUI
        if hasattr(gui, 'models_tree'):
            models_count = len(gui.models_tree.get_children())
            print(f"   Modelos na GUI: {models_count}")
        
        root.destroy()
        print("5. Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openrouter_gui() 