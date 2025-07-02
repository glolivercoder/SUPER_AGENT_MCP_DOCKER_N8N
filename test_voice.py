#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para o módulo de voz
"""

from modules.voice_module import VoiceModule

def main():
    print("Iniciando teste do módulo de voz...")
    
    # Inicializar módulo
    vm = VoiceModule()
    
    # Verificar status
    status = vm.get_status()
    print(f"Status: {status}")
    
    # Testar TTS
    print("\nTestando TTS...")
    tts_result = vm.test_voice("Olá, este é um teste de voz em português brasileiro")
    print(f"TTS funcionou: {tts_result}")
    
    # Testar STT
    print("\nTestando STT - fale algo...")
    stt_result = vm.listen_once(3)
    print(f"STT resultado: {stt_result}")
    
    print("\nTeste concluído!")

if __name__ == "__main__":
    main() 