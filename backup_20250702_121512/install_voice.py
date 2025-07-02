#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Instalação de Voz - SUPER_AGENT_MCP_DOCKER_N8N
--------------------------------------------------------
Script para instalar e configurar as dependências de voz gratuitas.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import sys
import subprocess
import platform

def install_package(package):
    """Instala um pacote Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao instalar {package}")
        return False

def check_system():
    """Verifica o sistema operacional"""
    system = platform.system().lower()
    print(f"Sistema detectado: {system}")
    return system

def install_voice_dependencies():
    """Instala dependências de voz"""
    print("🎤 Instalando dependências de voz...")
    
    # Dependências básicas
    packages = [
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.10.0"
    ]
    
    # Dependências específicas do sistema
    system = check_system()
    
    if system == "windows":
        print("📝 No Windows, PyAudio pode precisar de instalação manual")
        print("💡 Se houver erro, baixe de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        packages.append("pyaudio>=0.2.11")
    elif system == "linux":
        print("🐧 No Linux, instalando dependências do sistema...")
        os.system("sudo apt-get install portaudio19-dev python3-pyaudio")
        packages.append("pyaudio>=0.2.11")
    elif system == "darwin":  # macOS
        print("🍎 No macOS, instalando via Homebrew...")
        os.system("brew install portaudio")
        packages.append("pyaudio>=0.2.11")
    
    # Instalar pacotes
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resultado: {success_count}/{len(packages)} pacotes instalados")
    
    if success_count == len(packages):
        print("🎉 Todas as dependências de voz foram instaladas com sucesso!")
        return True
    else:
        print("⚠️  Algumas dependências não foram instaladas. Verifique os erros acima.")
        return False

def test_voice_modules():
    """Testa se os módulos de voz estão funcionando"""
    print("\n🧪 Testando módulos de voz...")
    
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition importado com sucesso")
        
        # Testar microfone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("✅ Microfone detectado")
            
    except ImportError as e:
        print(f"❌ Erro ao importar SpeechRecognition: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar microfone: {e}")
        return False
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ pyttsx3 inicializado com sucesso")
        
        # Listar vozes disponíveis
        voices = engine.getProperty('voices')
        print(f"📢 Vozes disponíveis: {len(voices)}")
        
        for i, voice in enumerate(voices[:3]):  # Mostrar apenas as primeiras 3
            print(f"  {i+1}. {voice.name} ({voice.id})")
            
    except ImportError as e:
        print(f"❌ Erro ao importar pyttsx3: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar pyttsx3: {e}")
        return False
    
    return True

def create_voice_config():
    """Cria arquivo de configuração de voz"""
    print("\n⚙️  Criando configuração de voz...")
    
    config_dir = "config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    voice_config = {
        "enabled": True,
        "language": "pt-BR",
        "voice_rate": 150,
        "voice_volume": 0.9,
        "wake_word": "assistente",
        "timeout": 5,
        "phrase_time_limit": 10,
        "energy_threshold": 4000,
        "dynamic_energy_threshold": True,
        "ambient_noise_duration": 1
    }
    
    import json
    config_file = os.path.join(config_dir, "voice_config.json")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(voice_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuração salva em: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False

def main():
    """Função principal"""
    print("🎤 SUPER_AGENT_MCP_DOCKER_N8N - Instalação de Voz")
    print("=" * 50)
    
    # Instalar dependências
    if not install_voice_dependencies():
        print("\n❌ Falha na instalação das dependências")
        return False
    
    # Testar módulos
    if not test_voice_modules():
        print("\n❌ Falha no teste dos módulos")
        return False
    
    # Criar configuração
    if not create_voice_config():
        print("\n❌ Falha na criação da configuração")
        return False
    
    print("\n🎉 Instalação de voz concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: py gui_main.py")
    print("2. Clique no botão 🎤 para ativar a voz")
    print("3. Diga 'assistente' seguido do comando")
    print("4. Comandos disponíveis: 'gerar prd', 'gerar tasks', 'gerar n8n', etc.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Instalação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 