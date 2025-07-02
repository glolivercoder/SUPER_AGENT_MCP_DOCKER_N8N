#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import shutil
import zipfile
import asyncio
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SETUP_OPENROUTER")

# Adicionar módulos ao path
sys.path.append(str(Path(__file__).parent))

def setup_database():
    """Configura o banco de dados"""
    try:
        from modules.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        logger.info("Database Manager inicializado")
        return db_manager
    except Exception as e:
        logger.error(f"Erro ao inicializar Database Manager: {e}")
        return None

def save_api_key(db_manager, api_key):
    """Salva a API key no banco de dados"""
    try:
        success = db_manager.save_api_key("openrouter", api_key)
        if success:
            logger.info("✅ API key salva no banco de dados com sucesso")
            return True
        else:
            logger.error("❌ Erro ao salvar API key no banco de dados")
            return False
    except Exception as e:
        logger.error(f"Erro ao salvar API key: {e}")
        return False

def setup_openrouter(db_manager):
    """Configura o OpenRouter Manager"""
    try:
        from modules.openrouter_manager import OpenRouterManager
        openrouter_manager = OpenRouterManager(db_manager)
        
        if openrouter_manager.api_key:
            logger.info("✅ OpenRouter Manager inicializado com API key")
            return openrouter_manager
        else:
            logger.error("❌ API key não encontrada no OpenRouter Manager")
            return None
    except Exception as e:
        logger.error(f"Erro ao inicializar OpenRouter Manager: {e}")
        return None

def backup_modules():
    """Faz backup de todos os módulos do projeto"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"backup_20250702_{timestamp}")
        backup_dir.mkdir(exist_ok=True)
        
        # Diretórios para backup
        dirs_to_backup = ["modules", "GUI", "config", "data", "logs"]
        files_to_backup = ["main.py", "README.md"]
        
        logger.info(f"🔄 Iniciando backup para: {backup_dir}")
        
        # Backup de diretórios
        for dir_name in dirs_to_backup:
            if Path(dir_name).exists():
                shutil.copytree(dir_name, backup_dir / dir_name, dirs_exist_ok=True)
                logger.info(f"✅ Backup do diretório: {dir_name}")
        
        # Backup de arquivos
        for file_name in files_to_backup:
            if Path(file_name).exists():
                shutil.copy2(file_name, backup_dir / file_name)
                logger.info(f"✅ Backup do arquivo: {file_name}")
        
        # Criar arquivo de metadados
        metadata = {
            "backup_timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "api_key_saved": True,
            "directories_backed_up": dirs_to_backup,
            "files_backed_up": files_to_backup
        }
        
        with open(backup_dir / "backup_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Criar ZIP
        zip_path = f"super_agent_backup_{timestamp}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"✅ Backup completo criado: {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"Erro ao fazer backup: {e}")
        return None

async def test_openrouter_connection(openrouter_manager):
    """Testa a conexão com a OpenRouter"""
    try:
        logger.info("🔄 Testando conexão com OpenRouter...")
        
        models = await openrouter_manager.get_models(force_refresh=True)
        if models:
            logger.info(f"✅ Conexão bem-sucedida! {len(models)} modelos carregados")
            
            free_models = [m for m in models if m.is_free]
            logger.info(f"📊 Modelos gratuitos disponíveis: {len(free_models)}")
            
            for i, model in enumerate(free_models[:5]):
                logger.info(f"  {i+1}. {model.name} ({model.company})")
            
            return True
        else:
            logger.error("❌ Nenhum modelo carregado")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {e}")
        return False

async def load_all_models(openrouter_manager, db_manager):
    """Carrega todos os modelos da OpenRouter"""
    try:
        logger.info("🔄 Carregando todos os modelos da OpenRouter...")
        
        models = await openrouter_manager.get_models(force_refresh=True)
        if not models:
            logger.error("❌ Nenhum modelo carregado")
            return False
        
        companies = openrouter_manager.get_companies(models)
        free_models = [m for m in models if m.is_free]
        paid_models = [m for m in models if not m.is_free]
        
        logger.info(f"📊 Estatísticas dos modelos:")
        logger.info(f"  Total: {len(models)}")
        logger.info(f"  Gratuitos: {len(free_models)}")
        logger.info(f"  Pagos: {len(paid_models)}")
        logger.info(f"  Empresas: {len(companies)}")
        
        # Salvar estatísticas
        stats = {
            "total_models": len(models),
            "free_models": len(free_models),
            "paid_models": len(paid_models),
            "companies": companies,
            "last_update": datetime.now().isoformat()
        }
        
        db_manager.save_configuration("openrouter", "models_stats", json.dumps(stats))
        logger.info("✅ Estatísticas salvas no banco de dados")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelos: {e}")
        return False

async def main():
    """Função principal"""
    api_key = "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"
    
    logger.info("🚀 Iniciando setup completo da OpenRouter")
    
    # 1. Setup do banco de dados
    db_manager = setup_database()
    if not db_manager:
        return False
    
    # 2. Salvar API key
    if not save_api_key(db_manager, api_key):
        return False
    
    # 3. Setup do OpenRouter
    openrouter_manager = setup_openrouter(db_manager)
    if not openrouter_manager:
        return False
    
    # 4. Backup dos módulos
    backup_path = backup_modules()
    if not backup_path:
        logger.warning("⚠️ Backup não foi criado, mas continuando...")
    
    # 5. Carregar todos os modelos
    if not await load_all_models(openrouter_manager, db_manager):
        return False
    
    # 6. Testar conexão
    if not await test_openrouter_connection(openrouter_manager):
        return False
    
    logger.info("🎉 Setup completo realizado com sucesso!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n" + "="*60)
        print("✅ SETUP COMPLETO REALIZADO COM SUCESSO!")
        print("="*60)
        print("📋 Resumo do que foi feito:")
        print("  • API key salva no banco de dados")
        print("  • Backup de todos os módulos criado")
        print("  • Modelos da OpenRouter carregados")
        print("  • Conexão testada com sucesso")
        print("  • Estatísticas salvas no banco")
        print("\n🚀 Agora você pode usar a interface gráfica!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ SETUP FALHOU!")
        print("="*60)
        print("Verifique os logs acima para mais detalhes.")
        print("="*60)
