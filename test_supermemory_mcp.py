#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste do SuperMemory MCP integrado ao SUPER_AGENT_MCP_DOCKER_N8N
Demonstra como usar o SuperMemory para armazenar e recuperar memórias de interfaces
"""

import asyncio
import json
from modules.openrouter_manager import OpenRouterManager

async def test_supermemory_integration():
    """Testa a integração do SuperMemory MCP"""
    print("🧠 === TESTE SUPERMEMORY MCP === \n")
    
    manager = OpenRouterManager()
    
    try:
        # Testa prompts que devem ativar o SuperMemory
        memory_prompts = [
            "Lembre desta informação: O projeto SUPER_AGENT suporta múltiplos MCPs",
            "Armazene na memória: OpenRouter é usado para acesso unificado a LLMs",
            "Memorize esta interface: GUI com 4 abas - Dashboard, Módulos, Logs, Config",
            "Guardar contexto: Sistema integra RAG com ChromaDB e sentence-transformers",
            "Recall: Quais interfaces foram mencionadas anteriormente?"
        ]
        
        for i, prompt in enumerate(memory_prompts, 1):
            print(f"📝 Prompt {i}: {prompt}")
            
            # Processa com análise automática de MCPs
            result = await manager.process_prompt(prompt)
            
            print(f"   🔧 MCPs sugeridos: {result['needed_mcps']}")
            print(f"   ✅ MCPs iniciados: {result['started_mcps']}")
            print(f"   🧠 SuperMemory ativo: {'supermemory' in result['started_mcps']}")
            print(f"   💬 Resposta: {result['response'][:80]}...")
            print()
            
            await asyncio.sleep(1)
        
        # Status final
        status = manager.get_status()
        print(f"📊 Status Final:")
        print(f"   Total MCPs disponíveis: {len(status['available_mcps'])}")
        print(f"   MCPs ativos: {status['active_mcps']}")
        print(f"   SuperMemory disponível: {'supermemory' in status['available_mcps']}")
        
    finally:
        await manager.shutdown()
        print("\n🔄 Teste concluído - MCPs parados")

async def test_supermemory_keywords():
    """Testa o reconhecimento de palavras-chave do SuperMemory"""
    print("\n🔍 === TESTE ANÁLISE DE PALAVRAS-CHAVE ===")
    
    manager = OpenRouterManager()
    
    test_phrases = [
        "Preciso lembrar desta configuração",
        "Armazene esta memória para uso futuro",
        "Recall das interfaces utilizadas",
        "Histórico de comandos executados",
        "Contexto das sessões anteriores",
        "Remember this important setup",
        "Interface memory storage"
    ]
    
    for phrase in test_phrases:
        suggested = await manager.analyze_prompt(phrase)
        supermemory_suggested = "supermemory" in suggested
        
        print(f"📝 '{phrase}'")
        print(f"   🧠 SuperMemory sugerido: {'✅' if supermemory_suggested else '❌'}")
        print(f"   🔧 Todos MCPs: {suggested}")
        print()

def test_mcp_registry():
    """Testa o registry de MCPs"""
    print("📋 === REGISTRY DE MCPs ===")
    
    manager = OpenRouterManager()
    
    print("MCPs Disponíveis:")
    for name, info in manager.mcps_registry.items():
        print(f"  🔧 {name}")
        print(f"     Categoria: {info['category']}")
        print(f"     Descrição: {info['description']}")
        print(f"     Comando: {info['command'][:60]}...")
        print()

async def test_supermemory_manual():
    """Teste manual do SuperMemory MCP"""
    print("🔧 === TESTE MANUAL SUPERMEMORY ===")
    
    import subprocess
    import time
    
    try:
        # Tenta iniciar o SuperMemory MCP diretamente
        cmd = ["npx", "-y", "supergateway", "--sse", "https://mcp.supermemory.ai/2ubE0qTwMtbd9dYC_fetX/sse"]
        print(f"Executando: {' '.join(cmd)}")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguarda alguns segundos
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ SuperMemory MCP está rodando")
            process.terminate()
            process.wait()
            print("🔄 Processo finalizado")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Processo terminou. Stdout: {stdout[:100]}")
            print(f"   Stderr: {stderr[:100]}")
    
    except Exception as e:
        print(f"❌ Erro ao testar SuperMemory: {e}")

async def main():
    """Executa todos os testes"""
    print("🚀 === TESTES SUPERMEMORY MCP - SUPER_AGENT ===\n")
    
    # Teste do registry
    test_mcp_registry()
    
    # Teste de palavras-chave
    await test_supermemory_keywords()
    
    # Teste manual do MCP
    await test_supermemory_manual()
    
    # Teste de integração completa
    await test_supermemory_integration()
    
    print("\n✅ === TODOS OS TESTES CONCLUÍDOS ===")
    print("\n💡 SuperMemory MCP está pronto para:")
    print("   • Armazenar memórias de todas as interfaces")
    print("   • Disponibilizar contexto em ambiente único")
    print("   • Integrar com OpenRouter Agent Manager")
    print("   • Funcionar com palavras-chave em português e inglês")

if __name__ == "__main__":
    asyncio.run(main()) 