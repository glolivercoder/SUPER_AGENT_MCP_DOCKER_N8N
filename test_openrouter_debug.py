#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de Debug do OpenRouter
----------------------------
Script para identificar problemas com o carregamento de modelos OpenRouter
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

def test_requests():
    print("\n=== TESTE SIMPLES COM REQUESTS ===")
    import requests
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Corpo (primeiros 500 chars): {resp.text[:500]}")
    except Exception as e:
        print(f"ERRO REQUESTS: {e}")

def test_openrouter_manager():
    """Testa o OpenRouterManager diretamente"""
    print("=== TESTE DO OPENROUTER MANAGER ===")
    
    try:
        from modules.openrouter_manager import OpenRouterManager
        
        # Verificar API key
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        print(f"API Key configurada: {'Sim' if api_key else 'Não'}")
        if api_key:
            print(f"API Key válida: {'Sim' if api_key.startswith('sk-or-') else 'Não'}")
        
        # Criar manager
        manager = OpenRouterManager()
        print(f"OpenRouter Manager criado: {manager}")
        print(f"API Key no manager: {'Sim' if manager.api_key else 'Não'}")
        
        return manager, True
        
    except Exception as e:
        print(f"Erro ao criar OpenRouter Manager: {e}")
        return None, False

async def test_models_loading(manager):
    """Testa o carregamento de modelos"""
    print("\n=== TESTE DE CARREGAMENTO DE MODELOS ===")
    
    try:
        print("Carregando modelos...")
        models = await manager.get_models()
        print(f"Modelos carregados: {len(models)}")
        
        if models:
            print("Primeiros 5 modelos:")
            for i, model in enumerate(models[:5]):
                print(f"  {i+1}. {model.name} ({model.company}) - Gratuito: {model.is_free}")
        
        return models
        
    except Exception as e:
        print(f"Erro ao carregar modelos: {e}")
        return []

def test_gui_integration():
    """Testa a integração com a GUI"""
    print("\n=== TESTE DE INTEGRAÇÃO COM GUI ===")
    
    try:
        import tkinter as tk
        from GUI.gui_module import SuperAgentGUI
        
        # Criar GUI
        root = tk.Tk()
        app = SuperAgentGUI(root)
        
        # Verificar se o manager foi injetado
        print(f"OpenRouter Manager na GUI: {hasattr(app, 'openrouter_manager')}")
        if hasattr(app, 'openrouter_manager'):
            print(f"Manager é None: {app.openrouter_manager is None}")
        
        # Fechar GUI
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"Erro na integração com GUI: {e}")
        return False

async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de debug do OpenRouter")
    print(f"Timestamp: {datetime.now()}")
    
    # Teste 1: OpenRouter Manager
    manager, success = test_openrouter_manager()
    
    if not success:
        print("❌ Falha na criação do OpenRouter Manager")
        return
    
    # Teste 2: Carregamento de modelos
    models = await test_models_loading(manager)
    
    # Teste 3: Integração com GUI
    gui_success = test_gui_integration()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"OpenRouter Manager: {'✅ OK' if success else '❌ FALHOU'}")
    print(f"Carregamento de modelos: {'✅ OK' if models else '❌ FALHOU'}")
    print(f"Integração com GUI: {'✅ OK' if gui_success else '❌ FALHOU'}")
    
    if models:
        print(f"  - Total de modelos: {len(models)}")
        free_models = [m for m in models if m.is_free]
        print(f"  - Modelos gratuitos: {len(free_models)}")
    
    # Fechar manager
    if manager:
        await manager.close()

    test_requests()

if __name__ == "__main__":
    asyncio.run(main()) 