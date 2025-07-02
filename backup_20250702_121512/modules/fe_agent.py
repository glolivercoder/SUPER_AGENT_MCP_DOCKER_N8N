#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fê Agent (Assistente de Desenvolvimento)
----------------------------------------
Módulo especializado para comandos de desenvolvimento via speech-to-text,
incluindo comandos Git, análise de projeto e automação de tarefas.

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import json
import logging
import subprocess
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("FE_AGENT")

class FeAgent:
    """Agente Fê para comandos de desenvolvimento e automação Git"""
    
    def __init__(self, config_dir="config", memories_file="MEMORIES.json"):
        self.config_dir = Path(config_dir)
        self.memories_file = Path(memories_file)
        self.logger = logger
        self.fe_config = {}
        self.memories = {}
        self.current_project_path = Path.cwd()
        
        # Carregar configurações e memórias
        self._load_config()
        self._load_memories()
        
        # Comandos Git disponíveis
        self.git_commands = {
            "status": ["status", "situacao", "estado"],
            "add": ["add", "adicionar", "incluir"],
            "commit": ["commit", "salvar", "confirmar"],
            "push": ["push", "enviar", "subir"],
            "pull": ["pull", "baixar", "atualizar"],
            "branch": ["branch", "ramo", "galho"],
            "checkout": ["checkout", "mudar", "trocar"],
            "merge": ["merge", "mesclar", "juntar"],
            "log": ["log", "historico", "registro"],
            "diff": ["diff", "diferenca", "comparar"]
        }
        
        # Comandos compostos
        self.composite_commands = {
            "commit_push": ["commit e push", "commit push", "salvar e enviar", "confirmar e subir"],
            "add_commit": ["add e commit", "adicionar e salvar", "incluir e confirmar"],
            "add_commit_push": ["add commit push", "adicionar salvar enviar", "workflow completo"]
        }
        
        self.logger.info("Fê Agent inicializado")
    
    def _load_config(self):
        """Carrega configurações do Fê Agent"""
        config_file = self.config_dir / "fe_agent_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.fe_config = json.load(f)
                self.logger.info("Configurações do Fê Agent carregadas")
            except Exception as e:
                self.logger.error(f"Erro ao carregar configurações: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Cria configuração padrão do Fê Agent"""
        self.fe_config = {
            "enabled": True,
            "auto_add_all": True,
            "default_commit_message": "Atualização automática via Fê Agent",
            "confirm_before_push": False,
            "git_auto_setup": True,
            "project_analysis": True,
            "voice_feedback": True,
            "supported_languages": ["python", "javascript", "java", "c++", "go"],
            "wake_words": ["fê", "fe", "hey fê"]
        }
        
        # Salvar configuração padrão
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config_file = self.config_dir / "fe_agent_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.fe_config, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuração padrão do Fê Agent criada")
        except Exception as e:
            self.logger.error(f"Erro ao criar configuração padrão: {e}")
    
    def _load_memories(self):
        """Carrega memórias do Fê Agent"""
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                self.logger.info("Memórias do Fê Agent carregadas")
            except Exception as e:
                self.logger.error(f"Erro ao carregar memórias: {e}")
                self.memories = {}
    
    def _save_memories(self):
        """Salva memórias do Fê Agent"""
        try:
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
            self.logger.info("Memórias do Fê Agent salvas")
        except Exception as e:
            self.logger.error(f"Erro ao salvar memórias: {e}")
    
    def _run_git_command(self, command: List[str], working_dir: Path = None) -> Dict[str, Any]:
        """Executa comando Git e retorna resultado"""
        if working_dir is None:
            working_dir = self.current_project_path
        
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
                "command": " ".join(["git"] + command)
            }
        except Exception as e:
            self.logger.error(f"Erro ao executar comando Git: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "command": " ".join(["git"] + command)
            }
    
    def process_voice_command(self, command_text: str) -> Dict[str, Any]:
        """Processa comando de voz e executa ação correspondente"""
        command_lower = command_text.lower().strip()
        
        # Remover palavras de ativação
        for wake_word in self.fe_config.get("wake_words", ["fê"]):
            if command_lower.startswith(wake_word):
                command_lower = command_lower[len(wake_word):].strip()
                break
        
        self.logger.info(f"Processando comando: {command_lower}")
        
        # Verificar comandos compostos primeiro
        for composite_cmd, variants in self.composite_commands.items():
            if any(variant in command_lower for variant in variants):
                return self._execute_composite_command(composite_cmd, command_lower)
        
        # Verificar comandos Git individuais
        for git_cmd, variants in self.git_commands.items():
            if any(variant in command_lower for variant in variants):
                return self._execute_git_command(git_cmd, command_lower)
        
        # Comandos especiais
        if any(word in command_lower for word in ["analise", "analisar", "projeto"]):
            return self.analyze_project()
        
        if any(word in command_lower for word in ["ajuda", "help", "comandos"]):
            return self.get_help()
        
        return {
            "success": False,
            "message": f"Comando não reconhecido: {command_text}",
            "suggestions": ["Tente: 'status', 'commit e push', 'analisar projeto', 'ajuda'"]
        }
    
    def _execute_git_command(self, git_cmd: str, full_command: str) -> Dict[str, Any]:
        """Executa comando Git individual"""
        try:
            if git_cmd == "status":
                result = self._run_git_command(["status", "--porcelain"])
                if result["success"]:
                    files_changed = len([line for line in result["stdout"].split('\n') if line.strip()])
                    return {
                        "success": True,
                        "message": f"Status: {files_changed} arquivos modificados",
                        "details": result["stdout"]
                    }
            
            elif git_cmd == "add":
                if self.fe_config.get("auto_add_all", True):
                    result = self._run_git_command(["add", "."])
                else:
                    result = self._run_git_command(["add", "-A"])
                
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Arquivos adicionados ao staging",
                        "details": result["stdout"]
                    }
            
            elif git_cmd == "commit":
                # Extrair mensagem do comando se existir
                commit_msg = self._extract_commit_message(full_command)
                if not commit_msg:
                    commit_msg = self.fe_config.get("default_commit_message", "Atualização automática via Fê Agent")
                
                result = self._run_git_command(["commit", "-m", commit_msg])
                if result["success"]:
                    return {
                        "success": True,
                        "message": f"Commit realizado: {commit_msg}",
                        "details": result["stdout"]
                    }
            
            elif git_cmd == "push":
                result = self._run_git_command(["push"])
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Push realizado com sucesso",
                        "details": result["stdout"]
                    }
            
            elif git_cmd == "pull":
                result = self._run_git_command(["pull"])
                if result["success"]:
                    return {
                        "success": True,
                        "message": "Pull realizado com sucesso",
                        "details": result["stdout"]
                    }
            
            # Outros comandos Git
            else:
                result = self._run_git_command([git_cmd])
                return {
                    "success": result["success"],
                    "message": f"Comando {git_cmd} executado",
                    "details": result["stdout"] if result["success"] else result["stderr"]
                }
            
            return {
                "success": False,
                "message": f"Erro ao executar {git_cmd}",
                "details": result.get("stderr", "Erro desconhecido")
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar comando Git {git_cmd}: {e}")
            return {
                "success": False,
                "message": f"Erro interno ao executar {git_cmd}",
                "details": str(e)
            }
    
    def _execute_composite_command(self, composite_cmd: str, full_command: str) -> Dict[str, Any]:
        """Executa comandos Git compostos"""
        results = []
        
        try:
            if composite_cmd == "commit_push":
                # 1. Add (se configurado)
                if self.fe_config.get("auto_add_all", True):
                    add_result = self._execute_git_command("add", full_command)
                    results.append(add_result)
                    if not add_result["success"]:
                        return {
                            "success": False,
                            "message": "Erro ao adicionar arquivos",
                            "details": results
                        }
                
                # 2. Commit
                commit_result = self._execute_git_command("commit", full_command)
                results.append(commit_result)
                if not commit_result["success"]:
                    return {
                        "success": False,
                        "message": "Erro ao fazer commit",
                        "details": results
                    }
                
                # 3. Push
                push_result = self._execute_git_command("push", full_command)
                results.append(push_result)
                
                return {
                    "success": push_result["success"],
                    "message": "Workflow commit e push concluído!" if push_result["success"] else "Erro no push",
                    "details": results
                }
            
            elif composite_cmd == "add_commit":
                add_result = self._execute_git_command("add", full_command)
                results.append(add_result)
                
                if add_result["success"]:
                    commit_result = self._execute_git_command("commit", full_command)
                    results.append(commit_result)
                    
                    return {
                        "success": commit_result["success"],
                        "message": "Add e commit concluídos!" if commit_result["success"] else "Erro no commit",
                        "details": results
                    }
            
            elif composite_cmd == "add_commit_push":
                # Workflow completo
                commands = ["add", "commit", "push"]
                all_success = True
                
                for cmd in commands:
                    result = self._execute_git_command(cmd, full_command)
                    results.append(result)
                    if not result["success"]:
                        all_success = False
                        break
                
                return {
                    "success": all_success,
                    "message": "Workflow completo concluído!" if all_success else "Erro no workflow",
                    "details": results
                }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar comando composto {composite_cmd}: {e}")
            return {
                "success": False,
                "message": f"Erro interno no comando composto",
                "details": str(e)
            }
    
    def _extract_commit_message(self, command: str) -> Optional[str]:
        """Extrai mensagem de commit do comando de voz"""
        # Padrões para identificar mensagem de commit
        patterns = [
            r'commit\s+["\'](.+)["\']',
            r'commit\s+(.+?)(?:\s+e\s+push|\s+push|$)',
            r'mensagem\s+["\'](.+)["\']',
            r'mensagem\s+(.+?)(?:\s+e\s+push|\s+push|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analisa o projeto atual"""
        try:
            analysis = {
                "project_path": str(self.current_project_path),
                "git_status": {},
                "file_stats": {},
                "suggestions": []
            }
            
            # Verificar se é repositório Git
            git_status = self._run_git_command(["status", "--porcelain"])
            if git_status["success"]:
                changes = [line for line in git_status["stdout"].split('\n') if line.strip()]
                analysis["git_status"] = {
                    "is_git_repo": True,
                    "files_changed": len(changes),
                    "changes": changes
                }
                
                if len(changes) > 0:
                    analysis["suggestions"].append("Há arquivos modificados. Considere fazer commit.")
            else:
                analysis["git_status"]["is_git_repo"] = False
                analysis["suggestions"].append("Este diretório não é um repositório Git.")
            
            # Estatísticas de arquivos
            file_types = {}
            for file_path in self.current_project_path.rglob("*"):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            analysis["file_stats"] = file_types
            
            # Detectar tipo de projeto
            if "package.json" in [f.name for f in self.current_project_path.iterdir()]:
                analysis["project_type"] = "Node.js/JavaScript"
            elif "requirements.txt" in [f.name for f in self.current_project_path.iterdir()]:
                analysis["project_type"] = "Python"
            elif "pom.xml" in [f.name for f in self.current_project_path.iterdir()]:
                analysis["project_type"] = "Java (Maven)"
            else:
                analysis["project_type"] = "Desconhecido"
            
            return {
                "success": True,
                "message": f"Análise do projeto {analysis['project_type']} concluída",
                "details": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar projeto: {e}")
            return {
                "success": False,
                "message": "Erro ao analisar projeto",
                "details": str(e)
            }
    
    def get_help(self) -> Dict[str, Any]:
        """Retorna ajuda com comandos disponíveis"""
        help_text = {
            "comandos_git": {
                "básicos": ["status", "add", "commit", "push", "pull"],
                "compostos": ["commit e push", "add e commit", "workflow completo"]
            },
            "exemplos": [
                "Fê, fazer status",
                "Fê, commit e push",
                "Fê, analisar projeto",
                "Fê, commit 'mensagem personalizada' e push"
            ],
            "configuração": "Use 'Fê' como palavra de ativação antes dos comandos"
        }
        
        return {
            "success": True,
            "message": "Comandos disponíveis no Fê Agent",
            "details": help_text
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do Fê Agent"""
        fe_memories = self.memories.get("fe_memories", {})
        
        stats = {
            "commands_executed": len(fe_memories.get("commands_history", [])),
            "git_operations": len([cmd for cmd in fe_memories.get("commands_history", []) if "git" in cmd.get("command", "")]),
            "last_command": fe_memories.get("commands_history", [{}])[-1].get("command") if fe_memories.get("commands_history") else None,
            "current_project": str(self.current_project_path),
            "agent_enabled": self.fe_config.get("enabled", False)
        }
        
        return stats


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    fe_agent = FeAgent()
    
    # Teste de comando
    result = fe_agent.process_voice_command("Fê, fazer status")
    print(f"Resultado: {result}")
    
    # Teste de análise
    analysis = fe_agent.analyze_project()
    print(f"Análise: {analysis}")
    
    # Teste de ajuda
    help_info = fe_agent.get_help()
    print(f"Ajuda: {help_info}") 