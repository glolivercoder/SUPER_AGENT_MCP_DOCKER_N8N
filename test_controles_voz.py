#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste dos Controles de Voz - SUPER_AGENT_MCP_DOCKER_N8N
-------------------------------------------------------
Testa se os controles de voz iniciam como ativos por padrão

Autor: [Seu Nome]
Data: 02/07/2025
Versão: 0.1.0
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_voice_controls():
    """Testa se os controles de voz iniciam como ativos por padrão"""
    print("🧪 Testando controles de voz...")
    
    try:
        # Importar a GUI
        from GUI.gui_module import SuperAgentGUI
        
        # Criar janela de teste
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal
        
        # Criar instância da GUI
        gui = SuperAgentGUI(root)
        
        # Verificar estado inicial do botão de microfone
        mic_text = gui.mic_button.cget("text")
        mic_bg = gui.mic_button.cget("bg")
        voice_status = gui.voice_status_label.cget("text")
        
        print(f"📱 Botão de microfone:")
        print(f"   Texto: {mic_text}")
        print(f"   Cor de fundo: {mic_bg}")
        print(f"   Status esperado: 🔴 (ativo)")
        print(f"   Cor esperada: #27ae60 (verde)")
        
        # Verificar botões de controle de voz
        stop_state = gui.stop_voice_button.cget("state")
        pause_state = gui.pause_voice_button.cget("state")
        resume_state = gui.resume_voice_button.cget("state")
        control_status = gui.voice_control_status.cget("text")
        
        print(f"\n🎛️ Botões de controle de voz:")
        print(f"   Stop: {stop_state}")
        print(f"   Pause: {pause_state}")
        print(f"   Resume: {resume_state}")
        print(f"   Status: {control_status}")
        print(f"   Esperado: Stop=normal, Pause=normal, Resume=disabled, Status='Pronto'")
        
        # Verificar status de voz
        print(f"\n🎤 Status de voz:")
        print(f"   Atual: {voice_status}")
        print(f"   Esperado: 'Voz: Ativada - Diga algo...'")
        
        # Verificar se a inicialização automática foi configurada
        has_auto_start = hasattr(gui, '_start_voice_listening_auto')
        print(f"\n🔄 Inicialização automática:")
        print(f"   Método configurado: {has_auto_start}")
        print(f"   Esperado: True")
        
        # Resultados dos testes
        tests_passed = 0
        total_tests = 7
        
        print(f"\n🧪 Executando testes...")
        
        if mic_text == "🔴":
            print("✅ Teste 1: Botão de microfone com texto correto")
            tests_passed += 1
        else:
            print("❌ Teste 1: Botão de microfone com texto incorreto")
            
        if mic_bg == "#27ae60":
            print("✅ Teste 2: Botão de microfone com cor correta")
            tests_passed += 1
        else:
            print("❌ Teste 2: Botão de microfone com cor incorreta")
            
        if voice_status == "Voz: Ativada - Diga algo...":
            print("✅ Teste 3: Status de voz correto")
            tests_passed += 1
        else:
            print("❌ Teste 3: Status de voz incorreto")
            
        if stop_state == "normal":
            print("✅ Teste 4: Botão Stop habilitado")
            tests_passed += 1
        else:
            print("❌ Teste 4: Botão Stop desabilitado")
            
        if pause_state == "normal":
            print("✅ Teste 5: Botão Pause habilitado")
            tests_passed += 1
        else:
            print("❌ Teste 5: Botão Pause desabilitado")
            
        if control_status == "Status: Pronto":
            print("✅ Teste 6: Status de controle correto")
            tests_passed += 1
        else:
            print("❌ Teste 6: Status de controle incorreto")
            
        if has_auto_start:
            print("✅ Teste 7: Método de inicialização automática configurado")
            tests_passed += 1
        else:
            print("❌ Teste 7: Método de inicialização automática não configurado")
        
        # Resumo final
        print(f"\n📊 Resumo dos testes:")
        print(f"   Testes aprovados: {tests_passed}/{total_tests}")
        print(f"   Taxa de sucesso: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            print("🎉 Todos os testes passaram! Controles de voz configurados corretamente.")
            return True
        else:
            print("⚠️ Alguns testes falharam. Verificar configurações.")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    print("🚀 Iniciando teste dos controles de voz...")
    success = test_voice_controls()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Teste falhou!")
        sys.exit(1) 