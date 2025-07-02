#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Backup - SUPER_AGENT_MCP_DOCKER_N8N
--------------------------------------------
Script para fazer backup de todos os módulos e configurações do projeto.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
import zipfile

def setup_logging():
    """Configura logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("BACKUP")

def create_backup():
    """Cria backup completo do projeto"""
    logger = setup_logging()
    
    # Timestamp para o backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    logger.info(f"Iniciando backup: {backup_dir}")
    
    # Diretórios e arquivos importantes para backup
    backup_items = [
        "modules/",
        "GUI/",
        "config/",
        "data/",
        "logs/",
        "main.py",
        "gui_main.py",
        "requirements.txt",
        "README.md",
        "SUPER_AGENT_MCP_DOCKER_N8N.md",
        "MEMORIES.json",
        "CHANGELOG.md",
        "install_voice.py"
    ]
    
    # Criar backup
    for item in backup_items:
        source = Path(item)
        if source.exists():
            destination = backup_dir / item
            
            if source.is_dir():
                # Copiar diretório
                shutil.copytree(source, destination, dirs_exist_ok=True)
                logger.info(f"Diretório copiado: {item}")
            else:
                # Copiar arquivo
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                logger.info(f"Arquivo copiado: {item}")
        else:
            logger.warning(f"Item não encontrado: {item}")
    
    # Criar arquivo de metadados do backup
    metadata = {
        "backup_timestamp": timestamp,
        "backup_date": datetime.now().isoformat(),
        "project_version": "0.1.0",
        "backup_items": backup_items,
        "total_size": get_directory_size(backup_dir)
    }
    
    metadata_file = backup_dir / "backup_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Criar arquivo ZIP do backup
    zip_filename = f"super_agent_backup_{timestamp}.zip"
    create_zip_backup(backup_dir, zip_filename)
    
    logger.info(f"Backup concluído: {zip_filename}")
    logger.info(f"Tamanho total: {get_directory_size(backup_dir)} bytes")
    
    return zip_filename

def get_directory_size(directory):
    """Calcula tamanho total de um diretório"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def create_zip_backup(backup_dir, zip_filename):
    """Cria arquivo ZIP do backup"""
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backup_dir.parent)
                zipf.write(file_path, arcname)

def main():
    """Função principal"""
    try:
        zip_filename = create_backup()
        print(f"\n✅ Backup criado com sucesso: {zip_filename}")
        print("📦 O arquivo ZIP contém todos os módulos e configurações")
        print("💾 Recomenda-se fazer commit e push após o backup")
        
    except Exception as e:
        print(f"\n❌ Erro durante backup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main() 