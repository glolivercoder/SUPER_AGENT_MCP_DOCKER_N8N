#!/usr/bin/env python3
"""
Script de Backup Completo - SUPER_AGENT_MCP_DOCKER_N8N
Cria backup de todos os módulos da aplicação com data e hora
"""

import os
import shutil
import zipfile
from datetime import datetime
import json

def criar_backup_completo():
    """Cria backup completo de todos os módulos da aplicação"""
    
    # Data e hora atual para o nome do backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_completo_{timestamp}"
    backup_zip = f"super_agent_backup_completo_{timestamp}.zip"
    
    print(f"🔄 Iniciando backup completo - {timestamp}")
    print(f"📁 Diretório de backup: {backup_dir}")
    
    # Criar diretório de backup
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Lista de arquivos principais para backup
    arquivos_principais = [
        "main.py",
        "gui_main.py",
        "rag_system.py",
        "mcp_manager.py",
        "docker_manager.py",
        "install_voice.py",
        "requirements.txt",
        "README.md",
        "CHANGELOG.md",
        "MEMORIES.json",
        "TASK.md",
        "GITHUB_SETUP.md",
        "SUPER_AGENT_MCP_DOCKER_N8N.md",
        ".gitignore"
    ]
    
    # Lista de diretórios para backup
    diretorios_backup = [
        "modules",
        "GUI",
        "config",
        "data"
    ]
    
    # Lista de arquivos de teste e utilitários
    arquivos_teste = [
        "test_gui_openrouter.py",
        "test_gui_specific.py",
        "test_issues.py",
        "test_speech_recognition.py",
        "test_voice.py",
        "check_openrouter_key.py",
        "check_silero_languages.py",
        "install_vosk_models.py",
        "setup_openrouter.py",
        "setup_openrouter_fixed.py",
        "backup_modules.py"
    ]
    
    # Lista de arquivos de configuração
    arquivos_config = [
        "main.bat",
        "package-lock.json"
    ]
    
    # Copiar arquivos principais
    print("📄 Copiando arquivos principais...")
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            try:
                shutil.copy2(arquivo, os.path.join(backup_dir, arquivo))
                print(f"  ✅ {arquivo}")
            except Exception as e:
                print(f"  ❌ Erro ao copiar {arquivo}: {e}")
        else:
            print(f"  ⚠️  Arquivo não encontrado: {arquivo}")
    
    # Copiar arquivos de teste
    print("🧪 Copiando arquivos de teste...")
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            try:
                shutil.copy2(arquivo, os.path.join(backup_dir, arquivo))
                print(f"  ✅ {arquivo}")
            except Exception as e:
                print(f"  ❌ Erro ao copiar {arquivo}: {e}")
        else:
            print(f"  ⚠️  Arquivo não encontrado: {arquivo}")
    
    # Copiar arquivos de configuração
    print("⚙️  Copiando arquivos de configuração...")
    for arquivo in arquivos_config:
        if os.path.exists(arquivo):
            try:
                shutil.copy2(arquivo, os.path.join(backup_dir, arquivo))
                print(f"  ✅ {arquivo}")
            except Exception as e:
                print(f"  ❌ Erro ao copiar {arquivo}: {e}")
        else:
            print(f"  ⚠️  Arquivo não encontrado: {arquivo}")
    
    # Copiar diretórios
    print("📂 Copiando diretórios...")
    for diretorio in diretorios_backup:
        if os.path.exists(diretorio):
            try:
                destino = os.path.join(backup_dir, diretorio)
                shutil.copytree(diretorio, destino, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                print(f"  ✅ {diretorio}/")
            except Exception as e:
                print(f"  ❌ Erro ao copiar {diretorio}: {e}")
        else:
            print(f"  ⚠️  Diretório não encontrado: {diretorio}")
    
    # Criar arquivo de metadados do backup
    metadata = {
        "timestamp": timestamp,
        "data_hora": datetime.now().isoformat(),
        "versao": "1.0",
        "descricao": "Backup completo de todos os módulos da aplicação SUPER_AGENT_MCP_DOCKER_N8N",
        "arquivos_principais": len([f for f in arquivos_principais if os.path.exists(f)]),
        "arquivos_teste": len([f for f in arquivos_teste if os.path.exists(f)]),
        "diretorios": len([d for d in diretorios_backup if os.path.exists(d)]),
        "total_arquivos": sum(len([f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]) 
                            for d in diretorios_backup if os.path.exists(d))
    }
    
    with open(os.path.join(backup_dir, "backup_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    # Criar arquivo README do backup
    readme_content = f"""# Backup Completo SUPER_AGENT_MCP_DOCKER_N8N

**Data/Hora:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Timestamp:** {timestamp}

## Conteúdo do Backup

### Arquivos Principais
- main.py - Arquivo principal da aplicação
- gui_main.py - Interface gráfica principal
- rag_system.py - Sistema RAG
- mcp_manager.py - Gerenciador MCP
- docker_manager.py - Gerenciador Docker
- install_voice.py - Instalador de voz
- requirements.txt - Dependências Python
- README.md - Documentação principal
- CHANGELOG.md - Histórico de mudanças
- MEMORIES.json - Memórias da aplicação

### Diretórios
- modules/ - Todos os módulos da aplicação
- GUI/ - Interface gráfica
- config/ - Configurações
- data/ - Dados da aplicação

### Arquivos de Teste
- test_gui_openrouter.py
- test_gui_specific.py
- test_issues.py
- test_speech_recognition.py
- test_voice.py
- check_openrouter_key.py
- check_silero_languages.py
- install_vosk_models.py
- setup_openrouter.py
- setup_openrouter_fixed.py

## Como Restaurar

1. Extraia o arquivo ZIP
2. Copie os arquivos para o diretório do projeto
3. Execute: `python main.py`

## Status dos Módulos

- ✅ Database Manager
- ✅ MCP Manager  
- ✅ Docker Manager
- ✅ RAG System
- ✅ Fê Agent
- ✅ Voice Module
- ✅ OpenRouter Manager
- ✅ GUI Module

---
*Backup criado automaticamente pelo script de backup*
"""
    
    with open(os.path.join(backup_dir, "README_BACKUP.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # Criar arquivo ZIP
    print("📦 Criando arquivo ZIP...")
    try:
        with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Backup ZIP criado: {backup_zip}")
        
        # Calcular tamanho do ZIP
        zip_size = os.path.getsize(backup_zip) / (1024 * 1024)  # MB
        print(f"📊 Tamanho do backup: {zip_size:.2f} MB")
        
    except Exception as e:
        print(f"❌ Erro ao criar ZIP: {e}")
    
    # Limpar diretório temporário
    try:
        shutil.rmtree(backup_dir)
        print("🧹 Diretório temporário removido")
    except Exception as e:
        print(f"⚠️  Erro ao remover diretório temporário: {e}")
    
    print(f"\n🎉 Backup completo finalizado!")
    print(f"📁 Arquivo: {backup_zip}")
    print(f"🕐 Timestamp: {timestamp}")
    
    return backup_zip

if __name__ == "__main__":
    try:
        backup_file = criar_backup_completo()
        print(f"\n✅ Backup salvo como: {backup_file}")
    except Exception as e:
        print(f"❌ Erro durante o backup: {e}") 