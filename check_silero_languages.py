#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para verificar idiomas disponíveis no Silero TTS
"""

import yaml
import os

def check_silero_languages():
    try:
        # Caminho para o arquivo de configuração do Silero
        config_path = os.path.join(
            os.path.expanduser('~'), 
            'AppData', 'Local', 'Programs', 'Python', 'Python311', 
            'Lib', 'site-packages', 'silero_tts', 'latest_silero_models.yaml'
        )
        
        print(f"Procurando configuração em: {config_path}")
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            print("Idiomas disponíveis no Silero TTS:")
            for language in config.get('tts_models', {}).keys():
                print(f"  - {language}")
                
            # Verificar se há português
            if 'pt' in config.get('tts_models', {}):
                print("\n✅ Português está disponível!")
                pt_models = config['tts_models']['pt']
                print("Modelos PT disponíveis:")
                for model_id in pt_models.keys():
                    print(f"  - {model_id}")
            else:
                print("\n❌ Português NÃO está disponível")
                
        else:
            print(f"❌ Arquivo de configuração não encontrado: {config_path}")
            
    except Exception as e:
        print(f"Erro ao verificar idiomas: {e}")

if __name__ == "__main__":
    check_silero_languages() 