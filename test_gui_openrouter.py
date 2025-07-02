#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste da GUI com OpenRouter
"""

import os
import sys
import asyncio
import tkinter as tk
from pathlib import Path

# Configurar API Key do OpenRouter
os.environ['OPENROUTER_API_KEY'] = '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'

# Importar módulos
from modules.openrouter_manager import OpenRouterManager
from GUI.gui_module import SuperAgentGUI

def test_openrouter_manager():
    """Testa o OpenRouterManager diretamente"""
    print("=== Teste do OpenRouterManager ===")
    
    manager = OpenRouterManager()
    print(f"OpenRouter Manager criado: {manager}")
    print(f"API Key configurada: {manager.check_api_key()}")
    
    # Testar carregamento de modelos
    try:
        models = asyncio.run(manager.get_models())
        print(f"Modelos carregados: {len(models)}")
        print("Primeiros 3 modelos:")
        for i, model in enumerate(models[:3]):
            print(f"  {i+1}. {model.name} ({model.company})")
        return manager, models
    except Exception as e:
        print(f"Erro ao carregar modelos: {e}")
        return manager, []

def test_gui_injection():
    """Testa a injeção de dependências na GUI"""
    print("\n=== Teste da GUI ===")
    
    # Criar OpenRouterManager
    manager, models = test_openrouter_manager()
    
    # Criar GUI
    root = tk.Tk()
    app = SuperAgentGUI(root)
    
    # Injetar dependência
    app.openrouter_manager = manager
    print(f"OpenRouter Manager injetado na GUI: {app.openrouter_manager}")
    
    # Testar carregamento de modelos na GUI
    print("Testando carregamento de modelos na GUI...")
    try:
        # Simular carregamento assíncrono
        async def test_load():
            return await app._load_models_async()
        
        asyncio.run(test_load())
        print("Carregamento de modelos na GUI executado com sucesso")
    except Exception as e:
        print(f"Erro no carregamento de modelos na GUI: {e}")
    
    # Fechar GUI
    root.destroy()
    print("GUI fechada")

if __name__ == "__main__":
    test_openrouter_manager()
    test_gui_injection()
    print("\n=== Teste concluído ===") 