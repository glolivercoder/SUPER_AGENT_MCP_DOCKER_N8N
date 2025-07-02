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
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# Importações condicionais para motores de voz GRATUITOS/OPENSOURCE
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logging.warning("pyttsx3 não disponível. Síntese de voz local desabilitada.")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logging.warning("speech_recognition não disponível. Reconhecimento de voz desabilitado.")

logger = logging.getLogger("VOICE_MODULE")

class VoiceModule:
    """Módulo de voz para síntese e reconhecimento de fala"""
    def __init__(self, config_dir="config", memories_file="MEMORIES.json"):
        self.config_dir = Path(config_dir)
        self.memories_file = Path(memories_file)
        self.logger = logger
        self.voice_config = {}
        self.memories = {}
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.voice_enabled = False
        self.wake_word_active = False
        self.command_callback = None
        self.wake_word_callback = None
        self.listen_thread = None
        self.stop_listening = False
        self._load_config()
        self._load_memories()
        self._initialize_engines()
        self.logger.info("Voice Module inicializado")

    def _load_config(self):
        config_file = self.config_dir / "voice_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.voice_config = json.load(f)
                self.logger.info("Configurações do Voice Module carregadas")
            except Exception as e:
                self.logger.error(f"Erro ao carregar configurações: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        self.voice_config = {
            "enabled": True,
            "tts_engine": "pyttsx3",
            "tts_voice": "default",
            "tts_rate": 200,
            "tts_volume": 0.8,
            "stt_engine": "google",
            "language": "pt-BR",
            "wake_word": "Super Agent",
            "wake_word_enabled": True,
            "continuous_listening": False,
            "voice_commands": {
                "parar": "stop_listening",
                "iniciar": "start_listening",
                "status": "get_status",
                "ajuda": "show_help",
                "configurar": "open_config"
            }
        }
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config_file = self.config_dir / "voice_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_config, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuração padrão do Voice Module criada")
        except Exception as e:
            self.logger.error(f"Erro ao criar configuração padrão: {e}")

    def _load_memories(self):
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                self.logger.info("Memórias de voz carregadas")
            except Exception as e:
                self.logger.error(f"Erro ao carregar memórias: {e}")
                self.memories = {}

    def _initialize_engines(self):
        if self.voice_config.get("enabled", True):
            self._initialize_tts()
            self._initialize_stt()

    def _initialize_tts(self):
        tts_engine = self.voice_config.get("tts_engine", "pyttsx3")
        if tts_engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                rate = self.voice_config.get("tts_rate", 200)
                volume = self.voice_config.get("tts_volume", 0.8)
                self.tts_engine.setProperty('rate', rate)
                self.tts_engine.setProperty('volume', volume)
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    voice_name = self.voice_config.get("tts_voice", "default")
                    for v in voices:
                        if voice_name.lower() in v.name.lower():
                            self.tts_engine.setProperty('voice', v.id)
                            break
                self.logger.info("pyttsx3 inicializado para TTS")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar pyttsx3: {e}")
                self.tts_engine = None

    def _initialize_stt(self):
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.logger.info("SpeechRecognition inicializado para STT")
            except Exception as e:
                self.logger.error(f"Erro ao inicializar SpeechRecognition: {e}")
                self.recognizer = None
                self.microphone = None

    def speak(self, text: str, interrupt_current: bool = False) -> bool:
        if not self.tts_engine:
            self.logger.warning("Engine de TTS não inicializada.")
            return False
        try:
            if interrupt_current:
                self.tts_engine.stop()
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao falar: {e}")
            return False

    def listen_once(self, timeout: int = 5) -> Optional[str]:
        if not self.recognizer or not self.microphone:
            self.logger.warning("Reconhecimento de voz não inicializado.")
            return None
        with self.microphone as source:
            self.logger.info("Aguardando fala...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language=self.voice_config.get("language", "pt-BR"))
                self.logger.info(f"Reconhecido: {text}")
                return text
            except sr.WaitTimeoutError:
                self.logger.warning("Tempo de escuta esgotado.")
            except sr.UnknownValueError:
                self.logger.warning("Não foi possível entender o áudio.")
            except Exception as e:
                self.logger.error(f"Erro no reconhecimento de voz: {e}")
        return None

    def listen_continuous(self, callback: Optional[Callable[[str], None]] = None):
        if not self.recognizer or not self.microphone:
            self.logger.warning("Reconhecimento de voz não inicializado.")
            return
        self.is_listening = True
        def listen_loop():
            while self.is_listening:
                text = self.listen_once()
                if text and callback:
                    callback(text)
                time.sleep(0.5)
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        self.logger.info("Escuta contínua parada.")

    def set_command_callback(self, callback: Callable[[str], None]):
        self.command_callback = callback

    def set_wake_word_callback(self, callback: Callable[[], None]):
        self.wake_word_callback = callback

    def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.voice_config.get("enabled", True),
            "tts_engine": self.voice_config.get("tts_engine", "pyttsx3"),
            "stt_engine": self.voice_config.get("stt_engine", "google"),
            "is_listening": self.is_listening
        }

    def add_voice_command(self, trigger: str, action: str):
        self.voice_config["voice_commands"][trigger] = action
        self.logger.info(f"Comando de voz adicionado: {trigger} -> {action}")

    def remove_voice_command(self, trigger: str):
        if trigger in self.voice_config["voice_commands"]:
            del self.voice_config["voice_commands"][trigger]
            self.logger.info(f"Comando de voz removido: {trigger}")
