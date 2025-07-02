#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste específico para SpeechRecognition
"""

import speech_recognition as sr

def test_speech_recognition():
    print("Testando SpeechRecognition...")
    
    # Criar recognizer
    r = sr.Recognizer()
    
    # Configurar para português brasileiro
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    
    print(f"Configuração: energy_threshold={r.energy_threshold}, dynamic_energy_threshold={r.dynamic_energy_threshold}")
    
    # Listar microfones
    print(f"Microfones disponíveis: {len(sr.Microphone.list_microphone_names())}")
    
    # Testar gravação
    print("\nFale algo por 3 segundos...")
    
    try:
        with sr.Microphone() as source:
            print("Ajustando para ruído ambiente...")
            r.adjust_for_ambient_noise(source, duration=1)
            
            print("Ouvindo...")
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
            
            print("Reconhecendo...")
            text = r.recognize_google(audio, language='pt-BR')
            
            print(f"Texto reconhecido: '{text}'")
            return text
            
    except sr.WaitTimeoutError:
        print("Timeout - nenhum áudio detectado")
        return None
    except sr.UnknownValueError:
        print("Fala não reconhecida")
        return None
    except sr.RequestError as e:
        print(f"Erro na API: {e}")
        return None
    except Exception as e:
        print(f"Erro geral: {e}")
        return None

if __name__ == "__main__":
    test_speech_recognition() 