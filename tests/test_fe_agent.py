#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do Fê Agent
-----------------
Script para testar as funcionalidades do Fê Agent para comandos Git via voz.

Uso: python test_fe_agent.py
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar o diretório dos módulos ao path
sys.path.append(str(Path(__file__).parent))

from modules.fe_agent import FeAgent

def setup_logging():
    """Configura logging para testes"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_fe_agent_commands():
    """Testa comandos do Fê Agent"""
    print("🤖 Testando Fê Agent - Assistente de Desenvolvimento\n")
    
    # Inicializar Fê Agent
    fe_agent = FeAgent()
    
    # Lista de comandos para testar
    test_commands = [
        "Fê, fazer status",
        "Fê, analisar projeto",
        "Fê, commit e push",
        "Fê, commit 'Nova funcionalidade implementada' e push",
        "Fê, ajuda",
        "fe status",
        "hey fê, fazer pull",
        "Fê, adicionar e salvar",
        "comando inválido"
    ]
    
    print("📋 Comandos que serão testados:")
    for i, cmd in enumerate(test_commands, 1):
        print(f"  {i}. {cmd}")
    print()
    
    # Executar testes
    for i, command in enumerate(test_commands, 1):
        print(f"🧪 Teste {i}: '{command}'")
        print("=" * 50)
        
        try:
            result = fe_agent.process_voice_command(command)
            
            print(f"✅ Sucesso: {result['success']}")
            print(f"💬 Mensagem: {result['message']}")
            
            if 'details' in result and result['details']:
                print(f"📄 Detalhes: {result['details']}")
            
            if 'suggestions' in result and result['suggestions']:
                print(f"💡 Sugestões: {result['suggestions']}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        print("\n" + "-" * 50 + "\n")
    
    # Testar análise de projeto
    print("🔍 Testando Análise de Projeto")
    print("=" * 50)
    
    try:
        analysis = fe_agent.analyze_project()
        print(f"✅ Sucesso: {analysis['success']}")
        print(f"💬 Mensagem: {analysis['message']}")
        
        if analysis['success'] and 'details' in analysis:
            details = analysis['details']
            print("\n📊 Detalhes da Análise:")
            print(f"  • Caminho: {details.get('project_path', 'N/A')}")
            print(f"  • Tipo: {details.get('project_type', 'N/A')}")
            
            if 'git_status' in details:
                git_info = details['git_status']
                print(f"  • Git: {'Sim' if git_info.get('is_git_repo') else 'Não'}")
                if git_info.get('is_git_repo'):
                    print(f"  • Arquivos modificados: {git_info.get('files_changed', 0)}")
            
            if 'file_stats' in details:
                print(f"  • Tipos de arquivo: {list(details['file_stats'].keys())}")
                
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Testar ajuda
    print("❓ Testando Sistema de Ajuda")
    print("=" * 50)
    
    try:
        help_info = fe_agent.get_help()
        print(f"✅ Sucesso: {help_info['success']}")
        print(f"💬 Mensagem: {help_info['message']}")
        
        if 'details' in help_info:
            details = help_info['details']
            print("\n📚 Comandos Disponíveis:")
            
            if 'comandos_git' in details:
                git_cmds = details['comandos_git']
                print("  🔧 Comandos Git Básicos:")
                for cmd in git_cmds.get('básicos', []):
                    print(f"    • {cmd}")
                
                print("  🔄 Comandos Compostos:")
                for cmd in git_cmds.get('compostos', []):
                    print(f"    • {cmd}")
            
            if 'exemplos' in details:
                print("  💡 Exemplos de Uso:")
                for exemplo in details['exemplos']:
                    print(f"    • {exemplo}")
                    
    except Exception as e:
        print(f"❌ Erro na ajuda: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testes do Fê Agent Concluídos!")
    print("=" * 50)

def demonstrate_voice_workflow():
    """Demonstra workflow típico de uso por voz"""
    print("\n🎤 Demonstração de Workflow por Voz")
    print("=" * 50)
    
    print("Exemplo de conversa típica com o Fê Agent:")
    print()
    
    scenarios = [
        {
            "user": "Fê, fazer status",
            "description": "Verificar status do repositório Git"
        },
        {
            "user": "Fê, adicionar e salvar",
            "description": "Adicionar arquivos modificados e fazer commit"
        },
        {
            "user": "Fê, commit 'Implementei nova funcionalidade' e push",
            "description": "Commit com mensagem personalizada e push"
        },
        {
            "user": "Fê, analisar projeto",
            "description": "Análise completa do projeto atual"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. 👤 Usuário: \"{scenario['user']}\"")
        print(f"   📝 Ação: {scenario['description']}")
        print(f"   🤖 Fê Agent: Executaria o comando e forneceria feedback por voz")
        print()

if __name__ == "__main__":
    setup_logging()
    
    print("🚀 SUPER_AGENT_MCP_DOCKER_N8N - Teste do Fê Agent")
    print("=" * 60)
    print()
    
    try:
        test_fe_agent_commands()
        demonstrate_voice_workflow()
        
    except KeyboardInterrupt:
        print("\n❌ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Obrigado por testar o Fê Agent!")
    print("Para usar em produção, execute: python gui_main.py") 