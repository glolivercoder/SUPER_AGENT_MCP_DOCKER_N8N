#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
from modules.openrouter_manager import OpenRouterManager

logging.basicConfig(level=logging.INFO)

async def test_openrouter_manager():
    print("=== TESTE DO OPENROUTER MANAGER CORRIGIDO ===\n")
    
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key:
        print("❌ ERRO: OPENROUTER_API_KEY não configurada")
        return
    
    print(f"✅ API Key configurada: {api_key[:10]}...")
    
    manager = OpenRouterManager()
    
    # Teste 1: Verificar créditos
    print("\n1. Verificando créditos da conta...")
    try:
        credits = await manager.check_credits()
        if "error" in credits:
            print(f"❌ Erro: {credits['error']}")
        else:
            print(f"✅ Créditos: {credits}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 2: Carregar modelos
    print("\n2. Carregando modelos...")
    try:
        models = await manager.get_models(force_refresh=True)
        print(f"✅ {len(models)} modelos carregados")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    await manager.close()
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    asyncio.run(test_openrouter_manager()) 