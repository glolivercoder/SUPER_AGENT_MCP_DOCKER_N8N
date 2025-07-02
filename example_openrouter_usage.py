#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso do OpenRouter Agent Manager
Demonstra como usar o agente para gerenciar MCPs dinamicamente
"""

import asyncio
import os
import json
from modules.openrouter_manager import OpenRouterManager, quick_task

def setup_environment():
    """Configura variáveis de ambiente necessárias"""
    # Configure sua chave OpenRouter aqui ou via variável de ambiente
    api_key = "sua_chave_openrouter_aqui"  # Substitua pela sua chave real
    
    if api_key != "sua_chave_openrouter_aqui":
        os.environ["OPENROUTER_API_KEY"] = api_key
        return True
    
    # Verifica se já existe nas variáveis de ambiente
    if os.getenv("OPENROUTER_API_KEY"):
        return True
    
    print("❌ Configure OPENROUTER_API_KEY para usar este exemplo")
    print("   export OPENROUTER_API_KEY=sua_chave_aqui")
    return False

async def exemplo_basico():
    """Exemplo básico de uso do agente"""
    print("🤖 === EXEMPLO BÁSICO - OPENROUTER AGENT ===")
    
    manager = OpenRouterManager()
    
    try:
        # Lista prompts de exemplo
        prompts = [
            "Liste os arquivos do diretório atual",
            "Verifique o status do Git e faça commit das mudanças",
            "Abra o Cursor IDE e carregue o projeto atual",
            "Crie um container Docker para esta aplicação",
            "Faça uma busca no Airbnb por hotéis em São Paulo"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n📝 Prompt {i}: {prompt}")
            
            # Processa o prompt com MCPs apropriados
            result = await manager.process_prompt(prompt)
            
            print(f"   🔧 MCPs necessários: {result['needed_mcps']}")
            print(f"   ✅ MCPs iniciados: {result['started_mcps']}")
            print(f"   💬 Resposta: {result['response'][:100]}...")
            
            # Pequena pausa entre prompts
            await asyncio.sleep(1)
        
        # Mostra status final
        status = manager.get_status()
        print(f"\n📊 Status final:")
        print(f"   API configurada: {status['api_configured']}")
        print(f"   MCPs ativos: {status['active_mcps']}")
        print(f"   MCPs disponíveis: {status['available_mcps']}")
        
    finally:
        # Limpa recursos
        await manager.shutdown()
        print("\n🔄 Todos os MCPs foram parados")

async def exemplo_especifico_git():
    """Exemplo específico para operações Git"""
    print("\n🔀 === EXEMPLO ESPECÍFICO - GIT OPERATIONS ===")
    
    manager = OpenRouterManager()
    
    try:
        git_prompts = [
            "Mostre o status atual do repositório Git",
            "Liste os últimos 5 commits",
            "Verifique se há mudanças não commitadas",
            "Crie um novo branch chamado 'feature/openrouter-integration'"
        ]
        
        for prompt in git_prompts:
            print(f"\n🔀 Git: {prompt}")
            result = await manager.process_prompt(prompt)
            
            if "git" in result['started_mcps']:
                print("   ✅ MCP Git ativo e pronto")
            else:
                print("   ⚠️ MCP Git não foi iniciado para este prompt")
    
    finally:
        await manager.shutdown()

async def exemplo_funcao_utilitaria():
    """Exemplo usando função utilitária rápida"""
    print("\n⚡ === EXEMPLO FUNÇÃO UTILITÁRIA ===")
    
    # Função para tarefas rápidas sem gerenciar objeto manager
    tasks = [
        "Liste arquivos Python no projeto",
        "Verifique se Docker está rodando",
        "Abra o arquivo README.md no Cursor"
    ]
    
    for task in tasks:
        print(f"\n⚡ Tarefa: {task}")
        response = await quick_task(task)
        print(f"   📄 Resultado: {response[:80]}...")

def exemplo_analise_mcps():
    """Exemplo de análise de MCPs sem execução"""
    print("\n🔍 === ANÁLISE DE MCPs SEM EXECUÇÃO ===")
    
    manager = OpenRouterManager()
    
    test_prompts = [
        "Preciso editar um arquivo de configuração",
        "Quero fazer deploy da aplicação com Docker",
        "Preciso criar uma interface no Figma",
        "Vou testar a aplicação web com automação",
        "Quero fazer um commit e push para o GitHub"
    ]
    
    for prompt in test_prompts:
        suggested_mcps = asyncio.run(manager.analyze_prompt(prompt))
        print(f"\n📝 '{prompt}'")
        print(f"   🔧 MCPs sugeridos: {suggested_mcps}")

async def exemplo_completo():
    """Exemplo completo mostrando todas as funcionalidades"""
    print("🚀 === EXEMPLO COMPLETO - OPENROUTER AGENT MANAGER ===\n")
    
    if not setup_environment():
        return
    
    # Executar todos os exemplos
    await exemplo_basico()
    await exemplo_especifico_git() 
    await exemplo_funcao_utilitaria()
    exemplo_analise_mcps()
    
    print("\n✅ === TODOS OS EXEMPLOS CONCLUÍDOS ===")
    print("\n💡 Próximos passos:")
    print("   1. Configure OPENROUTER_API_KEY com sua chave real")
    print("   2. Instale Node.js para MCPs NPX funcionarem")
    print("   3. Execute: python start_super_agent.py")
    print("   4. Use a interface GUI para controlar o agente")
    print("   5. Experimente seus próprios prompts!")

if __name__ == "__main__":
    # Executa o exemplo completo
    asyncio.run(exemplo_completo()) 