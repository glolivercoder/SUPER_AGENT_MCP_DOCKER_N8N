#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module (Módulo de Voz)
---------------------------
Módulo responsável pela síntese de voz e reconhecimento de comandos de voz
para o SUPER_AGENT_MCP_DOCKER_N8N.

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

# Vosk - Speech Recognition GRATUITO/OPENSOURCE
try:
    import vosk
    import json as vosk_json
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk não disponível. Reconhecimento offline desabilitado.")

# Coqui STT - Speech-to-Text OPENSOURCE
try:
    import stt
    COQUI_STT_AVAILABLE = True
except ImportError:
    COQUI_STT_AVAILABLE = False
    logging.warning("Coqui STT não disponível. STT avançado desabilitado.")

# PocketSphinx - CMU Sphinx OPENSOURCE
try:
    import pocketsphinx
    POCKETSPHINX_AVAILABLE = True
except ImportError:
    POCKETSPHINX_AVAILABLE = False
    logging.warning("PocketSphinx não disponível. CMU Sphinx desabilitado.")

logger = logging.getLogger("VOICE_MODULE")

class VoiceModule:
    """Módulo de voz para síntese e reconhecimento de fala"""
    
    def __init__(self, config_dir="config", memories_file="MEMORIES.json"):
        self.config_dir = Path(config_dir)
        self.memories_file = Path(memories_file)
        self.logger = logger
        self.voice_config = {}
        self.memories = {}
        
        # Engines de voz
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.azure_synthesizer = None
        self.azure_recognizer = None
        
        # Estado do módulo
        self.is_listening = False
        self.voice_enabled = False
        self.wake_word_active = False
        
        # Callbacks
        self.command_callback = None
        self.wake_word_callback = None
        
        # Thread para escuta contínua
        self.listen_thread = None
        self.stop_listening = False
        
        # Carregar configurações
        self._load_config()
        self._load_memories()
        self._initialize_engines()
        
        self.logger.info("Voice Module inicializado")
    
    def _load_config(self):
        """Carrega configurações do Voice Module"""
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
        """Cria configuração padrão do Voice Module"""
        self.voice_config = {
            "enabled": True,
            "tts_engine": "pyttsx3",  # pyttsx3, azure, system
            "tts_voice": "default",
            "tts_rate": 200,
            "tts_volume": 0.8,
            "stt_engine": "google",  # google, azure, sphinx
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
            },
            "azure_config": {
                "speech_key": "",
                "service_region": "eastus",
                "voice_name": "pt-BR-FranciscaNeural"
            }
        }
        
        # Salvar configuração padrão
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config_file = self.config_dir / "voice_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_config, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuração padrão do Voice Module criada")
        except Exception as e:
            self.logger.error(f"Erro ao criar configuração padrão: {e}")
    
    def _load_memories(self):
        """Carrega memórias de voz"""
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                self.logger.info("Memórias de voz carregadas")
            except Exception as e:
                self.logger.error(f"Erro ao carregar memórias: {e}")
                self.memories = {}
    
    def _initialize_engines(self):
        """Inicializa engines de voz e reconhecimento"""
        # Inicializar TTS (Text-to-Speech)
        if self.voice_config.get("enabled", True):
            self._initialize_tts()
            self._initialize_stt()
    
    def _initialize_tts(self):
        """Inicializa engine de síntese de voz"""
        tts_engine = self.voice_config.get("tts_engine", "pyttsx3")
        
        if tts_engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                
                # Configurar propriedades
                rate = self.voice_config.get("tts_rate", 200)
                volume = self.voice_config.get("tts_volume", 0.8)
                
                self.tts_engine.setProperty('rate', rate)
                self.tts_engine.setProperty('volume', volume)
                
                # Configurar voz se especificada
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                
                self.logger.info("Engine pyttsx3 inicializada com sucesso")
                
            except Exception as e:
                self.logger.error(f"Erro ao inicializar pyttsx3: {e}")
                self.tts_engine = None
        
        elif tts_engine == "azure" and AZURE_SPEECH_AVAILABLE:
            self._initialize_azure_tts()
    
    def _initialize_azure_tts(self):
        """Inicializa Azure Speech TTS"""
        try:
            speech_key = self.voice_config.get("azure_config", {}).get("speech_key", "")
            service_region = self.voice_config.get("azure_config", {}).get("service_region", "eastus")
            
            if not speech_key:
                self.logger.warning("Azure Speech Key não configurada")
                return
            
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
            speech_config.speech_synthesis_voice_name = self.voice_config.get("azure_config", {}).get("voice_name", "pt-BR-FranciscaNeural")
            
            self.azure_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
            self.logger.info("Azure Speech TTS inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Azure TTS: {e}")
            self.azure_synthesizer = None
    
    def _initialize_stt(self):
        """Inicializa engine de reconhecimento de voz"""
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Ajustar para ruído ambiente
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.logger.info("Speech Recognition inicializado com sucesso")
                
            except Exception as e:
                self.logger.error(f"Erro ao inicializar Speech Recognition: {e}")
                self.recognizer = None
                self.microphone = None
    
    def speak(self, text: str, interrupt_current: bool = False) -> bool:
        """Sintetiza texto em voz"""
        if not self.voice_config.get("enabled", True):
            return False
        
        try:
            tts_engine = self.voice_config.get("tts_engine", "pyttsx3")
            
            if tts_engine == "pyttsx3" and self.tts_engine:
                if interrupt_current:
                    self.tts_engine.stop()
                
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
                self.logger.info(f"Texto sintetizado: {text[:50]}...")
                return True
            
            elif tts_engine == "azure" and self.azure_synthesizer:
                if interrupt_current:
                    # Azure não tem método stop direto, usar SSML para interromper
                    pass
                
                result = self.azure_synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    self.logger.info(f"Azure TTS: Texto sintetizado: {text[:50]}...")
                    return True
                else:
                    self.logger.error(f"Azure TTS erro: {result.reason}")
                    return False
            
            else:
                self.logger.warning("Nenhuma engine TTS disponível")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            return False
    
    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Escuta um comando único"""
        if not self.recognizer or not self.microphone:
            self.logger.warning("Reconhecimento de voz não disponível")
            return None
        
        try:
            with self.microphone as source:
                self.logger.info("Escutando...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Reconhecer usando Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.voice_config.get("language", "pt-BR"))
            self.logger.info(f"Comando reconhecido: {text}")
            
            return text.lower()
            
        except sr.WaitTimeoutError:
            self.logger.info("Timeout na escuta")
            return None
        except sr.UnknownValueError:
            self.logger.info("Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Erro no serviço de reconhecimento: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return None
    
    def start_continuous_listening(self):
        """Inicia escuta contínua em thread separada"""
        if self.is_listening:
            self.logger.warning("Escuta contínua já está ativa")
            return
        
        if not self.recognizer or not self.microphone:
            self.logger.warning("Reconhecimento de voz não disponível")
            return
        
        self.is_listening = True
        self.stop_listening = False
        
        def listen_continuously():
            wake_word = self.voice_config.get("wake_word", "super agent").lower()
            
            while not self.stop_listening:
                try:
                    command = self.listen_once(timeout=1)
                    
                    if command:
                        # Verificar wake word se ativo
                        if self.voice_config.get("wake_word_enabled", True):
                            if wake_word in command:
                                self.wake_word_active = True
                                if self.wake_word_callback:
                                    self.wake_word_callback()
                                self.speak("Sim, estou escutando.")
                                continue
                        
                        # Processar comando se wake word foi ativada ou não é obrigatória
                        if self.wake_word_active or not self.voice_config.get("wake_word_enabled", True):
                            self._process_voice_command(command)
                            self.wake_word_active = False
                    
                    time.sleep(0.1)  # Pequena pausa para não sobrecarregar CPU
                    
                except Exception as e:
                    self.logger.error(f"Erro na escuta contínua: {e}")
                    time.sleep(1)
            
            self.is_listening = False
            self.logger.info("Escuta contínua finalizada")
        
        self.listen_thread = threading.Thread(target=listen_continuously, daemon=True)
        self.listen_thread.start()
        
        self.logger.info("Escuta contínua iniciada")
    
    def stop_continuous_listening(self):
        """Para a escuta contínua"""
        if not self.is_listening:
            return
        
        self.stop_listening = True
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        
        self.is_listening = False
        self.logger.info("Escuta contínua parada")
    
    def _process_voice_command(self, command: str):
        """Processa comando de voz reconhecido"""
        voice_commands = self.voice_config.get("voice_commands", {})
        
        # Verificar comandos configurados
        for trigger, action in voice_commands.items():
            if trigger.lower() in command:
                self.logger.info(f"Comando de voz executado: {action}")
                
                if action == "stop_listening":
                    self.stop_continuous_listening()
                    self.speak("Parando escuta.")
                elif action == "start_listening":
                    if not self.is_listening:
                        self.start_continuous_listening()
                        self.speak("Iniciando escuta.")
                elif action == "get_status":
                    status = "escutando" if self.is_listening else "parado"
                    self.speak(f"Status do módulo de voz: {status}")
                elif action == "show_help":
                    self.speak("Comandos disponíveis: parar, iniciar, status, ajuda, configurar")
                
                # Chamar callback personalizado se definido
                if self.command_callback:
                    self.command_callback(command, action)
                
                return
        
        # Se não encontrou comando específico, chamar callback geral
        if self.command_callback:
            self.command_callback(command, "unknown")
    
    def set_command_callback(self, callback: Callable[[str, str], None]):
        """Define callback para comandos de voz"""
        self.command_callback = callback
    
    def set_wake_word_callback(self, callback: Callable[[], None]):
        """Define callback para wake word"""
        self.wake_word_callback = callback
    
    def get_voice_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do módulo de voz"""
        voice_prefs = self.memories.get("voice_preferences", {})
        
        stats = {
            "voice_enabled": self.voice_config.get("enabled", False),
            "tts_engine": self.voice_config.get("tts_engine", "none"),
            "is_listening": self.is_listening,
            "wake_word_active": self.wake_word_active,
            "wake_word": self.voice_config.get("wake_word", ""),
            "current_voice": voice_prefs.get("voice_name", "default"),
            "engines_available": {
                "pyttsx3": PYTTSX3_AVAILABLE,
                "speech_recognition": SPEECH_RECOGNITION_AVAILABLE,
                "azure_speech": AZURE_SPEECH_AVAILABLE
            }
        }
        
        return stats
    
    def test_voice_system(self) -> Dict[str, bool]:
        """Testa o sistema de voz"""
        results = {
            "tts_test": False,
            "stt_test": False,
            "microphone_test": False
        }
        
        # Teste TTS
        try:
            results["tts_test"] = self.speak("Testando síntese de voz.")
        except Exception as e:
            self.logger.error(f"Erro no teste TTS: {e}")
        
        # Teste microfone
        if self.microphone:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                results["microphone_test"] = True
            except Exception as e:
                self.logger.error(f"Erro no teste do microfone: {e}")
        
        # Teste STT
        if results["microphone_test"]:
            try:
                self.speak("Diga algo para testar o reconhecimento de voz.")
                command = self.listen_once(timeout=5)
                results["stt_test"] = command is not None
            except Exception as e:
                self.logger.error(f"Erro no teste STT: {e}")
        
        return results


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    voice_module = VoiceModule()
    
    # Teste do sistema
    test_results = voice_module.test_voice_system()
    print(f"Resultados dos testes: {test_results}")
    
    # Teste de comando
    def command_handler(command, action):
        print(f"Comando recebido: {command} -> Ação: {action}")
    
    voice_module.set_command_callback(command_handler)
    
    # Exemplo de uso
    voice_module.speak("Módulo de voz inicializado com sucesso!")
    
    # Escutar um comando
    print("Diga algo:")
    command = voice_module.listen_once()
    if command:
        print(f"Você disse: {command}") 