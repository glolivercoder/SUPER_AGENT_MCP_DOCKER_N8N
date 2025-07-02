#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MÃ³dulo de Gerenciamento de MCPs
------------------------------
ResponsÃ¡vel por gerenciar MCPs (Model Context Protocols) de diferentes IDEs
como Cline, RooCline, Windsurf e Cursor.

Autor: [Seu Nome]
Data: 01/07/2025
VersÃ£o: 0.1.0
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
        """Carrega as configuraÃ§Ãµes de MCPs de diferentes IDEs"""
        try:
            config_files = list(self.config_dir.glob("*.json"))
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.mcp_configs[config_file.stem] = config
            self.logger.info(f"ConfiguraÃ§Ãµes de MCP carregadas: {list(self.mcp_configs.keys())}")
            return self.mcp_configs
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuraÃ§Ãµes de MCP: {e}")
            return {}
    
    def save_config(self, ide_name, config_data):
        """Salva uma configuraÃ§Ã£o de MCP para uma IDE especÃ­fica"""
        if ide_name.lower() not in self.supported_ides:
            self.logger.warning(f"IDE nÃ£o suportada: {ide_name}")
            return False
        
        try:
            config_path = self.config_dir / f"{ide_name.lower()}_mcp_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"ConfiguraÃ§Ã£o salva para {ide_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuraÃ§Ã£o para {ide_name}: {e}")
            return False
    
    def share_config(self, source_ide, target_ide):
        """Compartilha configuraÃ§Ã£o de MCP entre IDEs"""
        if source_ide.lower() not in self.supported_ides or target_ide.lower() not in self.supported_ides:
            self.logger.warning(f"IDE nÃ£o suportada: {source_ide} ou {target_ide}")
            return False
        
        source_config = self.mcp_configs.get(f"{source_ide.lower()}_mcp_config")
        if not source_config:
            self.logger.warning(f"ConfiguraÃ§Ã£o nÃ£o encontrada para {source_ide}")
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
        
        try:
            # Caminhos padrão para MCPs em diferentes IDEs no Windows
            home_dir = os.path.expanduser("~")
            appdata_roaming = os.path.join(home_dir, "AppData", "Roaming")
            appdata_local = os.path.join(home_dir, "AppData", "Local")
            
            # Definir caminhos específicos para cada IDE
            ide_paths = {
                "cursor": [
                    os.path.join(appdata_roaming, "Cursor", "User", "globalStorage", "rooveterinaryinc.roo-cline"),
                    os.path.join(appdata_roaming, "Cursor", "User", "settings.json"),
                    os.path.join(appdata_roaming, "Cursor", "logs"),
                ],
                "cline": [
                    os.path.join(appdata_roaming, "Code", "User", "globalStorage", "saoudrizwan.claude-dev"),
                    os.path.join(appdata_local, "cline"),
                    os.path.join(home_dir, ".cline"),
                ],
                "roocline": [
                    os.path.join(appdata_roaming, "Code", "User", "globalStorage", "rooveterinaryinc.roo-cline"),
                    os.path.join(appdata_local, "roocline"),
                ],
                "windsurf": [
                    os.path.join(appdata_roaming, "Windsurf", "User", "globalStorage"),
                    os.path.join(appdata_local, "Windsurf"),
                ],
                "trae": [
                    os.path.join(appdata_roaming, "Trae", "User", "globalStorage"),
                    os.path.join(appdata_local, "Trae"),
                ]
            }
            
            # Verificar cada IDE
            for ide, paths in ide_paths.items():
                detected_mcps = []
                ide_found = False
                
                for path in paths:
                    if os.path.exists(path):
                        ide_found = True
                        try:
                            if os.path.isfile(path):
                                # Verificar arquivo de configuração
                                if path.endswith('.json'):
                                    try:
                                        with open(path, 'r', encoding='utf-8') as f:
                                            config = json.load(f)
                                            # Procurar por configurações de MCP
                                            if 'mcp' in str(config).lower():
                                                detected_mcps.append(f"Configuração MCP encontrada em {os.path.basename(path)}")
                                    except json.JSONDecodeError:
                                        self.logger.warning(f"Arquivo JSON inválido: {path}")
                                    except Exception as e:
                                        self.logger.warning(f"Erro ao ler arquivo {path}: {e}")
                            else:
                                # Verificar diretório
                                try:
                                    items = os.listdir(path)
                                    for item in items:
                                        try:
                                            item_path = os.path.join(path, item)
                                            if os.path.isfile(item_path):
                                                # Verificar arquivos relacionados a MCP
                                                if any(keyword in item.lower() for keyword in ['mcp', 'server', 'config']):
                                                    detected_mcps.append(item)
                                            elif os.path.isdir(item_path):
                                                # Verificar subdiretórios
                                                try:
                                                    sub_items = os.listdir(item_path)
                                                    if sub_items:
                                                        detected_mcps.append(f"Pasta: {item} ({len(sub_items)} itens)")
                                                except Exception:
                                                    pass
                                        except Exception as e:
                                            self.logger.debug(f"Erro ao processar item {item} em {path}: {e}")
                                except Exception as e:
                                    self.logger.warning(f"Erro ao listar diretório {path}: {e}")
                                        
                        except Exception as e:
                            self.logger.warning(f"Erro ao verificar {path}: {e}")
                
                # Adicionar MCPs padrão conhecidos se a IDE foi encontrada
                if ide_found:
                    known_mcps = self._get_known_mcps_for_ide(ide)
                    detected_mcps.extend(known_mcps)
                    
                    installed_mcps[ide.upper()] = {
                        "status": "Detectado",
                        "paths": [p for p in paths if os.path.exists(p)],
                        "mcps": list(set(detected_mcps)) if detected_mcps else ["Nenhum MCP específico detectado"]
                    }
                    self.logger.info(f"IDE {ide.upper()} detectada com {len(detected_mcps)} MCPs")
                else:
                    installed_mcps[ide.upper()] = {
                        "status": "Não encontrado",
                        "paths": [],
                        "mcps": []
                    }
            
            return installed_mcps
            
        except Exception as e:
            self.logger.error(f"Erro geral na detecção de MCPs: {e}")
            # Retornar pelo menos um resultado para não quebrar a interface
            return {
                "ERRO": {
                    "status": "Falha na detecção",
                    "paths": [],
                    "mcps": [f"Erro: {str(e)}"]
                }
            }
    
    def _get_known_mcps_for_ide(self, ide):
        """Retorna lista de MCPs conhecidos para uma IDE específica"""
        known_mcps = {
            "cursor": [
                "claude-dev (Anthropic)",
                "github-copilot",
                "cursor-ai",
                "code-completion"
            ],
            "cline": [
                "claude-3-sonnet",
                "file-explorer",
                "terminal-integration"
            ],
            "roocline": [
                "roo-cline-server",
                "anthropic-integration",
                "code-analysis"
            ],
            "windsurf": [
                "windsurf-ai",
                "code-assistant",
                "project-navigator"
            ],
            "trae": [
                "trae-assistant",
                "code-suggestions"
            ]
        }
        
        return known_mcps.get(ide, [])


if __name__ == "__main__":
    # Teste bÃ¡sico
    logging.basicConfig(level=logging.INFO)
    manager = MCPManager()
    installed = manager.detect_installed_mcps()
    print(f"MCPs instalados: {json.dumps(installed, indent=2)}") 
