#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de Gerenciamento de MCPs
------------------------------
Responsável por gerenciar MCPs (Model Context Protocols) de diferentes IDEs
como Cline, RooCline, Windsurf e Cursor.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import json
import shutil
import logging
from pathlib import Path

logger = logging.getLogger("MCP_MANAGER")

class MCPManager:
    """Gerenciador de MCPs para diferentes IDEs"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.mcp_configs = {}
        self.supported_ides = ["cline", "roocline", "windsurf", "cursor"]
        self.logger = logger
        
    def load_configs(self):
        """Carrega as configurações de MCPs de diferentes IDEs"""
        try:
            config_files = list(self.config_dir.glob("*.json"))
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.mcp_configs[config_file.stem] = config
            self.logger.info(f"Configurações de MCP carregadas: {list(self.mcp_configs.keys())}")
            return self.mcp_configs
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações de MCP: {e}")
            return {}
    
    def save_config(self, ide_name, config_data):
        """Salva uma configuração de MCP para uma IDE específica"""
        if ide_name.lower() not in self.supported_ides:
            self.logger.warning(f"IDE não suportada: {ide_name}")
            return False
        
        try:
            config_path = self.config_dir / f"{ide_name.lower()}_mcp_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuração salva para {ide_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração para {ide_name}: {e}")
            return False
    
    def share_config(self, source_ide, target_ide):
        """Compartilha configuração de MCP entre IDEs"""
        if source_ide.lower() not in self.supported_ides or target_ide.lower() not in self.supported_ides:
            self.logger.warning(f"IDE não suportada: {source_ide} ou {target_ide}")
            return False
        
        source_config = self.mcp_configs.get(f"{source_ide.lower()}_mcp_config")
        if not source_config:
            self.logger.warning(f"Configuração não encontrada para {source_ide}")
            return False
        
        return self.save_config(target_ide, source_config)
    
    def get_mcp_paths(self):
        """Retorna os caminhos dos MCPs instalados"""
        mcp_paths = {}
        for ide in self.supported_ides:
            config = self.mcp_configs.get(f"{ide.lower()}_mcp_config")
            if config and "path" in config:
                mcp_paths[ide] = config["path"]
        return mcp_paths
    
    def detect_installed_mcps(self):
        """Detecta MCPs instalados no sistema"""
        installed_mcps = {}
        
        # Caminhos padrão para MCPs em diferentes IDEs
        default_paths = {
            "cline": os.path.expanduser("~/.config/cline/mcps"),
            "roocline": os.path.expanduser("~/.config/roocline/mcps"),
            "windsurf": os.path.expanduser("~/.config/windsurf/mcps"),
            "cursor": os.path.expanduser("~/AppData/Roaming/Cursor/mcps")
        }
        
        for ide, path in default_paths.items():
            if os.path.exists(path):
                try:
                    mcp_files = os.listdir(path)
                    installed_mcps[ide] = {
                        "path": path,
                        "mcps": mcp_files
                    }
                    self.logger.info(f"MCPs detectados para {ide}: {len(mcp_files)}")
                except Exception as e:
                    self.logger.error(f"Erro ao detectar MCPs para {ide}: {e}")
        
        return installed_mcps


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    manager = MCPManager()
    installed = manager.detect_installed_mcps()
    print(f"MCPs instalados: {json.dumps(installed, indent=2)}") 