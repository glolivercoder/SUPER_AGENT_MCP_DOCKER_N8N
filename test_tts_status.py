#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste do Status do TTS - SUPER_AGENT_MCP_DOCKER_N8N
----------------------------------------------------
Testa se o TTS está funcionando corretamente

Autor: [Seu Nome]
Data: 02/07/2025
Versão: 0.1.0
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_tts_status():
    """Testa o status do TTS"""
    print("🔊 Testando status do TTS...")
    
    try:
        # Importar o módulo de voz
        from modules.voice_module import VoiceModule
        
        # Criar instância do módulo de voz
        voice_module = VoiceModule()
        
        # Verificar status
        status = voice_module.get_status()
        print(f"\n📊 Status do TTS:")
        print(f"  TTS Ready: {status['tts_ready']}")
        print(f"  STT Ready: {status['stt_ready']}")
        print(f"  STT Type: {status['stt_type']}")
        print(f"  Current Speaker: {status['current_speaker']}")
        print(f"  Available Speakers: {status['available_speakers']}")
        print(f"  Is Listening: {status['is_listening']}")
        
        # Verificar configurações
        config = voice_module.get_voice_config()
        print(f"\n⚙️ Configurações:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # Testar TTS diretamente
        print(f"\n🧪 Testando TTS...")
        if status['tts_ready']:
            print("✅ TTS está pronto - testando fala...")
            result = voice_module.test_voice("Teste de voz funcionando!")
            if result:
                print("✅ TTS funcionou corretamente!")
            else:
                print("❌ TTS falhou no teste!")
        else:
            print("❌ TTS não está pronto!")
            
        # Verificar se há vozes disponíveis
        speakers = voice_module.get_speakers()
        print(f"\n🎤 Vozes disponíveis ({len(speakers)}):")
        for i, speaker in enumerate(speakers):
            print(f"  {i+1}. {speaker}")
            
        # Testar pyttsx3 diretamente
        print(f"\n🔧 Testando pyttsx3 diretamente...")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            print(f"  Total de vozes no sistema: {len(voices)}")
            
            for i, voice in enumerate(voices):
                print(f"    {i+1}. {voice.name} ({voice.id})")
                if hasattr(voice, 'languages') and voice.languages:
                    print(f"       Languages: {voice.languages}")
                    
            # Testar fala
            print("  Testando fala...")
            engine.say("Teste direto do pyttsx3")
            engine.runAndWait()
            print("  ✅ Fala testada com sucesso!")
            
        except Exception as e:
            print(f"  ❌ Erro no pyttsx3: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao testar TTS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts_status() 