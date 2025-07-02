#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module - Módulo de Voz Gratuito para SUPER_AGENT_MCP_DOCKER_N8N
---------------------------------------------------------------------
Módulo responsável por funcionalidades de voz usando apenas bibliotecas gratuitas:
- Reconhecimento de voz: SpeechRecognition + Google Speech API (gratuita)
- Síntese de voz: pyttsx3 (local, gratuito)
- Comandos de voz personalizados
- Integração com outros módulos

Autor: [Seu Nome]
Data: 01/07/2025
Versão: 0.1.0
"""

import os
import json
import logging
import threading
import time
import queue
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime

# Bibliotecas gratuitas para voz
try:
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    print(f"Aviso: Módulos de voz não instalados: {e}")
    print("Execute: pip install SpeechRecognition pyttsx3 pyaudio")

class VoiceModule:
    """Módulo de voz para reconhecimento e síntese usando bibliotecas gratuitas"""
    
    def __init__(self):
        self.logger = logging.getLogger("VoiceModule")
        self.config_dir = Path("config")
        self.voice_config = self._load_voice_config()
        
        # Inicializar componentes de voz
        self.recognizer = None
        self.engine = None
        self.microphone = None
        self.is_listening = False
        self.listen_thread = None
        self.command_callback = None
        self.audio_queue = queue.Queue()
        
        # Comandos de voz padrão
        self.voice_commands = {
            "ajuda": "help",
            "status": "status",
            "docker": "docker_status",
            "mcp": "mcp_status",
            "parar": "stop_listening",
            "iniciar": "start_listening",
            "gerar prd": "generate_prd",
            "gerar tasks": "generate_tasks",
            "gerar n8n": "generate_n8n",
            "gerar deploy": "generate_deploy",
            "buscar rag": "search_rag",
            "limpar chat": "clear_chat"
        }
        
        # Wake words em português
        self.wake_words = ["assistente", "super agent", "hey", "oi", "olá"]
        
        if VOICE_AVAILABLE:
            self._initialize_voice_components()
        else:
            self.logger.warning("Módulos de voz não disponíveis")
    
    def _load_voice_config(self) -> Dict[str, Any]:
        """Carrega configuração de voz"""
        config_file = self.config_dir / "voice_config.json"
        
        default_config = {
            "enabled": True,
            "language": "pt-BR",
            "voice_rate": 150,
            "voice_volume": 0.9,
            "wake_word": "assistente",
            "timeout": 5,
            "phrase_time_limit": 10,
            "energy_threshold": 4000,
            "dynamic_energy_threshold": True,
            "ambient_noise_duration": 1
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Mesclar com configuração padrão
                    default_config.update(config)
                    self.logger.info("Configuração de voz carregada")
            except Exception as e:
                self.logger.error(f"Erro ao carregar configuração de voz: {e}")
        else:
            # Criar arquivo de configuração padrão
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                self.logger.info("Arquivo de configuração de voz criado")
            except Exception as e:
                self.logger.error(f"Erro ao criar configuração de voz: {e}")
        
        return default_config
    
    def _initialize_voice_components(self):
        """Inicializa componentes de reconhecimento e síntese de voz"""
        try:
            # Inicializar reconhecedor
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.voice_config.get("energy_threshold", 4000)
            self.recognizer.dynamic_energy_threshold = self.voice_config.get("dynamic_energy_threshold", True)
            
            # Inicializar microfone
            self.microphone = sr.Microphone()
            
            # Ajustar para ruído ambiente
            with self.microphone as source:
                self.logger.info("Ajustando para ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(
                    source, 
                    duration=self.voice_config.get("ambient_noise_duration", 1)
                )
            
            # Inicializar engine de síntese
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.voice_config.get("voice_rate", 150))
            self.engine.setProperty('volume', self.voice_config.get("voice_volume", 0.9))
            
            # Configurar voz em português se disponível
            voices = self.engine.getProperty('voices')
            portuguese_voice = None
            
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                
                # Procurar por vozes em português
                if any(lang in voice_name or lang in voice_id for lang in ['portuguese', 'pt', 'br', 'brazil']):
                    portuguese_voice = voice.id
                    break
            
            if portuguese_voice:
                self.engine.setProperty('voice', portuguese_voice)
                self.logger.info(f"Voz em português configurada: {portuguese_voice}")
            else:
                self.logger.info("Voz em português não encontrada, usando voz padrão")
            
            self.logger.info("Componentes de voz inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar componentes de voz: {e}")
            VOICE_AVAILABLE = False
    
    def speak(self, text: str) -> bool:
        """Sintetiza texto em voz"""
        if not VOICE_AVAILABLE or not self.engine:
            self.logger.warning("Síntese de voz não disponível")
            print(f"Voz: {text}")
            return False
        
        try:
            self.logger.info(f"Sintetizando: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            return False
    
    def listen(self, timeout: Optional[int] = None) -> Optional[str]:
        """Escuta e reconhece voz usando Google Speech API (gratuita)"""
        if not VOICE_AVAILABLE or not self.recognizer or not self.microphone:
            self.logger.warning("Reconhecimento de voz não disponível")
            return None
        
        timeout = timeout or self.voice_config.get("timeout", 5)
        
        try:
            with self.microphone as source:
                self.logger.info("Escutando...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=self.voice_config.get("phrase_time_limit", 10)
                )
            
            # Reconhecer áudio usando Google Speech API (gratuita)
            text = self.recognizer.recognize_google(
                audio, 
                language=self.voice_config.get("language", "pt-BR")
            )
            
            self.logger.info(f"Reconhecido: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            self.logger.info("Timeout - nenhum áudio detectado")
            return None
        except sr.UnknownValueError:
            self.logger.info("Áudio não reconhecido")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Erro na requisição de reconhecimento: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return None
    
    def start_continuous_listening(self):
        """Inicia escuta contínua em thread separada"""
        if self.is_listening:
            self.logger.info("Escuta contínua já está ativa")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._continuous_listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self.logger.info("Escuta contínua iniciada")
    
    def stop_continuous_listening(self):
        """Para a escuta contínua"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        self.logger.info("Escuta contínua parada")
    
    def _continuous_listen_loop(self):
        """Loop principal de escuta contínua"""
        wake_word = self.voice_config.get("wake_word", "assistente")
        
        while self.is_listening:
            try:
                # Escutar por comando
                text = self.listen()
                
                if text:
                    # Verificar wake word
                    if any(wake in text.lower() for wake in self.wake_words):
                        self.logger.info(f"Wake word detectada: {wake_word}")
                        self.speak("Sim, estou ouvindo")
                        
                        # Escutar comando
                        command = self.listen()
                        if command:
                            self._process_voice_command(command)
                
                time.sleep(0.1)  # Pequena pausa para não sobrecarregar
                
            except Exception as e:
                self.logger.error(f"Erro no loop de escuta: {e}")
                time.sleep(1)
    
    def _process_voice_command(self, command: str):
        """Processa comando de voz"""
        self.logger.info(f"Processando comando: {command}")
        
        # Verificar comandos padrão
        for cmd, action in self.voice_commands.items():
            if cmd in command.lower():
                if self.command_callback:
                    self.command_callback(command, action)
                else:
                    self._execute_default_command(action)
                return
        
        # Comando não reconhecido
        if self.command_callback:
            self.command_callback(command, "unknown")
        else:
            self.speak("Comando não reconhecido. Diga 'ajuda' para ver os comandos disponíveis.")
    
    def _execute_default_command(self, action: str):
        """Executa comandos padrão"""
        if action == "help":
            help_text = """
            Comandos disponíveis:
            - Ajuda: mostra esta lista
            - Status: status do sistema
            - Docker: status do Docker
            - MCP: status dos MCPs
            - Gerar PRD: gera um PRD
            - Gerar Tasks: gera tasks
            - Gerar N8N: gera workflow N8N
            - Gerar Deploy: gera script de deploy
            - Buscar RAG: busca na base de conhecimento
            - Limpar Chat: limpa o chat
            - Parar: para a escuta
            - Iniciar: inicia a escuta
            """
            self.speak(help_text)
        elif action == "status":
            self.speak("Sistema funcionando normalmente")
        elif action == "docker_status":
            self.speak("Verificando status do Docker")
        elif action == "mcp_status":
            self.speak("Verificando status dos MCPs")
        elif action == "generate_prd":
            self.speak("Gerando PRD")
        elif action == "generate_tasks":
            self.speak("Gerando tasks")
        elif action == "generate_n8n":
            self.speak("Gerando workflow N8N")
        elif action == "generate_deploy":
            self.speak("Gerando script de deploy")
        elif action == "search_rag":
            self.speak("Buscando na base de conhecimento")
        elif action == "clear_chat":
            self.speak("Chat limpo")
        elif action == "stop_listening":
            self.stop_continuous_listening()
            self.speak("Escuta parada")
        elif action == "start_listening":
            self.start_continuous_listening()
            self.speak("Escuta iniciada")
    
    def set_command_callback(self, callback: Callable[[str, str], None]):
        """Define callback para processamento de comandos"""
        self.command_callback = callback
        self.logger.info("Callback de comandos configurado")
    
    def add_voice_command(self, trigger: str, action: str):
        """Adiciona novo comando de voz"""
        self.voice_commands[trigger] = action
        self.logger.info(f"Comando de voz adicionado: {trigger} -> {action}")
    
    def remove_voice_command(self, trigger: str):
        """Remove comando de voz"""
        if trigger in self.voice_commands:
            del self.voice_commands[trigger]
            self.logger.info(f"Comando de voz removido: {trigger}")
    
    def is_available(self) -> bool:
        """Verifica se o módulo de voz está disponível"""
        return VOICE_AVAILABLE and self.recognizer and self.engine
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do módulo de voz"""
        return {
            "available": self.is_available(),
            "enabled": self.voice_config.get("enabled", False),
            "listening": self.is_listening,
            "language": self.voice_config.get("language", "pt-BR"),
            "wake_word": self.voice_config.get("wake_word", "assistente"),
            "commands_count": len(self.voice_commands),
            "wake_words": self.wake_words
        }
    
    def toggle_listening(self):
        """Alterna entre iniciar e parar a escuta"""
        if self.is_listening:
            self.stop_continuous_listening()
            return False
        else:
            self.start_continuous_listening()
            return True 