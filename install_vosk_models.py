#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para baixar e instalar modelos Vosk para português brasileiro
"""

import os
import zipfile
import requests
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_file(url, filename):
    """Baixa um arquivo da URL"""
    try:
        logger.info(f"Baixando {filename}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Download concluído: {filename}")
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar {filename}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extrai arquivo ZIP"""
    try:
        logger.info(f"Extraindo {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"Extração concluída: {zip_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao extrair {zip_path}: {e}")
        return False

def install_vosk_models():
    """Instala modelos Vosk para português brasileiro"""
    
    # URLs dos modelos Vosk para português
    models = {
        "vosk-model-small-pt-0.3": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip",
        "vosk-model-small-pt-br-0.3": "https://alphacephei.com/vosk/models/vosk-model-small-pt-br-0.3.zip"
    }
    
    for model_name, url in models.items():
        zip_file = f"{model_name}.zip"
        
        # Verificar se já existe
        if os.path.exists(model_name):
            logger.info(f"Modelo {model_name} já existe, pulando...")
            continue
        
        # Baixar modelo
        if download_file(url, zip_file):
            # Extrair modelo
            if extract_zip(zip_file, "."):
                # Remover arquivo ZIP
                try:
                    os.remove(zip_file)
                    logger.info(f"Arquivo {zip_file} removido")
                except:
                    pass
            else:
                logger.error(f"Falha ao extrair {zip_file}")
        else:
            logger.error(f"Falha ao baixar {model_name}")

def main():
    """Função principal"""
    logger.info("Iniciando instalação dos modelos Vosk para português brasileiro...")
    
    # Criar diretório se não existir
    os.makedirs("models", exist_ok=True)
    
    # Instalar modelos
    install_vosk_models()
    
    logger.info("Instalação concluída!")
    logger.info("Modelos disponíveis:")
    
    # Listar modelos instalados
    for item in os.listdir("."):
        if item.startswith("vosk-model-"):
            logger.info(f"  - {item}")

if __name__ == "__main__":
    main() 