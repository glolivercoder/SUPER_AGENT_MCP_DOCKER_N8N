#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MÃ³dulo de Gerenciamento de Docker
--------------------------------
ResponsÃ¡vel por gerenciar contÃªineres Docker para o SUPER_AGENT_MCP_DOCKER_N8N.

Autor: [Seu Nome]
Data: 01/07/2025
VersÃ£o: 0.1.0
"""

import os
import json
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("DOCKER_MANAGER")

class DockerManager:
    """Gerenciador de contÃªineres Docker"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.docker_config_file = self.config_dir / "docker_config.json"
        self.docker_compose_file = Path("docker-compose.yml")
        self.logger = logger
        self.containers = {}
        
    def check_docker_installed(self):
        """Verifica se o Docker estÃ¡ instalado no sistema"""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode == 0:
                self.logger.info(f"Docker instalado: {result.stdout.strip()}")
                return True
            else:
                self.logger.error("Docker nÃ£o estÃ¡ instalado ou acessÃ­vel")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar instalaÃ§Ã£o do Docker: {e}")
            return False
    
    def load_config(self):
        """Carrega a configuraÃ§Ã£o do Docker"""
        if not self.docker_config_file.exists():
            self.logger.warning(f"Arquivo de configuraÃ§Ã£o nÃ£o encontrado: {self.docker_config_file}")
            return {}
        
        try:
            with open(self.docker_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info("ConfiguraÃ§Ã£o do Docker carregada")
            return config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuraÃ§Ã£o do Docker: {e}")
            return {}
    
    def save_config(self, config):
        """Salva a configuraÃ§Ã£o do Docker"""
        try:
            with open(self.docker_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info("ConfiguraÃ§Ã£o do Docker salva")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuraÃ§Ã£o do Docker: {e}")
            return False
    
    def list_containers(self):
        """Lista os contÃªineres Docker em execuÃ§Ã£o"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.Ports}}"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container_id, name, status, ports = line.split('|')
                    containers.append({
                        "id": container_id,
                        "name": name,
                        "status": status,
                        "ports": ports
                    })
            
            self.containers = {c["name"]: c for c in containers}
            self.logger.info(f"ContÃªineres em execuÃ§Ã£o: {len(containers)}")
            return containers
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao listar contÃªineres: {e.stderr}")
            return []
        except Exception as e:
            self.logger.error(f"Erro ao listar contÃªineres: {e}")
            return []
    
    def start_container(self, container_name, image, ports=None, volumes=None, env_vars=None):
        """Inicia um contÃªiner Docker"""
        if not self.check_docker_installed():
            return False
        
        try:
            cmd = ["docker", "run", "-d", "--name", container_name]
            
            # Adicionar mapeamentos de porta
            if ports:
                for host_port, container_port in ports.items():
                    cmd.extend(["-p", f"{host_port}:{container_port}"])
            
            # Adicionar volumes
            if volumes:
                for host_path, container_path in volumes.items():
                    cmd.extend(["-v", f"{host_path}:{container_path}"])
            
            # Adicionar variÃ¡veis de ambiente
            if env_vars:
                for key, value in env_vars.items():
                    cmd.extend(["-e", f"{key}={value}"])
            
            # Adicionar a imagem
            cmd.append(image)
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                self.logger.info(f"ContÃªiner {container_name} iniciado com sucesso")
                return True
            else:
                self.logger.error(f"Erro ao iniciar contÃªiner {container_name}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao iniciar contÃªiner {container_name}: {e}")
            return False
    
    def stop_container(self, container_name):
        """Para um contÃªiner Docker"""
        try:
            result = subprocess.run(
                ["docker", "stop", container_name], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                self.logger.info(f"ContÃªiner {container_name} parado com sucesso")
                return True
            else:
                self.logger.error(f"Erro ao parar contÃªiner {container_name}: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao parar contÃªiner {container_name}: {e}")
            return False
    
    def start_n8n(self, port=5678, data_dir="./n8n_data"):
        """Inicia um contÃªiner com N8N"""
        ports = {str(port): "5678"}
        volumes = {os.path.abspath(data_dir): "/home/node/.n8n"}
        
        return self.start_container(
            container_name="n8n",
            image="n8nio/n8n:latest",
            ports=ports,
            volumes=volumes
        )


if __name__ == "__main__":
    # Teste bÃ¡sico
    logging.basicConfig(level=logging.INFO)
    manager = DockerManager()
    if manager.check_docker_installed():
        containers = manager.list_containers()
        print(f"ContÃªineres em execuÃ§Ã£o: {json.dumps(containers, indent=2)}") 
