#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste Simples da API OpenRouter
-------------------------------
Testa a API diretamente para verificar se está funcionando
"""

import os
import requests
import json

# Configurar API Key
api_key = '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'

def test_openrouter_api():
    """Testa a API do OpenRouter diretamente"""
    print("=== TESTE DIRETO DA API OPENROUTER ===")
    
    # URL da API
    url = "https://openrouter.ai/api/v1/models"
    
    # Headers conforme documentação oficial
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/super-agent-mcp-docker-n8n",
        "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
    }
    
    try:
        print("1. Fazendo requisição para a API...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"2. Status Code: {response.status_code}")
        print(f"3. Headers de resposta: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"4. ✅ Sucesso! Modelos encontrados: {len(data.get('data', []))}")
            
            # Mostrar alguns modelos
            models = data.get('data', [])
            if models:
                print("\n5. Primeiros 3 modelos:")
                for i, model in enumerate(models[:3]):
                    print(f"   {i+1}. {model.get('name', 'N/A')} ({model.get('id', 'N/A')})")
            
            return True
        else:
            print(f"4. ❌ Erro! Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"4. ❌ Erro na requisição: {e}")
        return False

def test_chat_completion():
    """Testa chat completion"""
    print("\n=== TESTE DE CHAT COMPLETION ===")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/super-agent-mcp-docker-n8n",
        "X-Title": "SUPER_AGENT_MCP_DOCKER_N8N"
    }
    
    payload = {
        "model": "openrouter/cypher-alpha:free",
        "messages": [
            {"role": "user", "content": "Olá! Como você está?"}
        ],
        "max_tokens": 50
    }
    
    try:
        print("1. Testando chat completion...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"2. Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("3. ✅ Chat completion funcionou!")
            print(f"   Resposta: {data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
            return True
        else:
            print(f"3. ❌ Erro no chat completion: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"3. ❌ Erro no chat completion: {e}")
        return False

if __name__ == "__main__":
    # Testar API de modelos
    models_ok = test_openrouter_api()
    
    # Testar chat completion
    chat_ok = test_chat_completion()
    
    print(f"\n=== RESUMO ===")
    print(f"API de Modelos: {'✅ OK' if models_ok else '❌ FALHOU'}")
    print(f"Chat Completion: {'✅ OK' if chat_ok else '❌ FALHOU'}") 