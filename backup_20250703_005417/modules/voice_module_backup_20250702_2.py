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
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import torch
import sounddevice as sd
import numpy as np
import soundfile as sf
from silero_tts.silero_tts import SileroTTS
import vosk
import tempfile

logger = logging.getLogger("VOICE_MODULE")

class VoiceModule:
    """Módulo de voz usando Silero TTS/STT (padrão open source funcional)"""
    
    def __init__(self, config_dir="config", memories_file="MEMORIES.json"):
        self.config_dir = Path(config_dir)
        self.memories_file = Path(memories_file)
        self.logger = logger
        
        # Configurações padrão
        self.voice_config = {
            "tts_language": "es",
            "tts_model": "v3_es",
            "speaker": "es_0",
            "sample_rate": 48000,
            "pitch": 1.0,
            "speed": 1.0,
            "volume": 1.0,
            "device": "cpu",
            "language": "pt-BR",
            "energy_threshold": 4000,
            "dynamic_energy_threshold": True,
            "input_device_index": None
        }
        
        self.memories = {}
        
        # Modelos TTS/STT
        self.tts_model = None
        self.stt_model = None
        
        # Speakers disponíveis
        self.available_speakers = []
        
        # Estado atual
        self.current_speaker = None
        self.is_listening = False
        
        self._init_voice_module()

    def _init_voice_module(self):
        """Inicializa o módulo de voz"""
        try:
            self._load_config()
            self._load_memories()
            self._init_tts()
            self._init_stt()
            self.logger.info("Voice Module inicializado com Silero TTS/STT")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Voice Module: {e}")

    def _load_config(self):
        """Carrega configurações do arquivo JSON"""
        config_file = self.config_dir / "voice_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.voice_config.update(saved_config)
                self.logger.info("Configurações do Voice Module carregadas")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar configurações: {e}")
        else:
            self._save_config()

    def _save_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            config_file = self.config_dir / "voice_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")

    def _load_memories(self):
        """Carrega memórias de voz"""
        try:
            if self.memories_file.exists():
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    all_memories = json.load(f)
                    self.memories = all_memories.get("voice_memories", {})
            self.logger.info("Memórias de voz carregadas")
        except Exception as e:
            self.logger.warning(f"Erro ao carregar memórias: {e}")

    def _save_memories(self):
        """Salva memórias de voz"""
        try:
            all_memories = {}
            if self.memories_file.exists():
                with open(self.memories_file, 'r', encoding='utf-8') as f:
                    all_memories = json.load(f)
            
            all_memories["voice_memories"] = self.memories
            
            with open(self.memories_file, 'w', encoding='utf-8') as f:
                json.dump(all_memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar memórias: {e}")

    def _init_tts(self):
        """Inicializa o pyttsx3 TTS e filtra apenas vozes em português brasileiro"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            voices = self.tts_engine.getProperty('voices')
            self.available_speakers = []
            for i, voice in enumerate(voices):
                # Filtrar apenas vozes em português brasileiro
                if ('portuguese' in voice.name.lower() or 'pt-br' in voice.id.lower() or 'brazil' in voice.name.lower()):
                    voice_info = {
                        'id': voice.id,
                        'name': voice.name,
                        'index': i,
                        'language': voice.languages[0] if voice.languages else 'unknown'
                    }
                    self.available_speakers.append(voice_info)
            if self.available_speakers:
                self.current_speaker = self.available_speakers[0]
                self.tts_engine.setProperty('voice', self.current_speaker['id'])
                self.logger.info(f"Voz portuguesa selecionada: {self.current_speaker['name']}")
            else:
                self.logger.error("Nenhuma voz em português brasileiro encontrada no sistema!")
                self.tts_engine = None
            self.tts_engine.setProperty('rate', int(self.voice_config.get('speed', 1.0) * 200))
            self.tts_engine.setProperty('volume', self.voice_config.get('volume', 1.0))
            self.logger.info(f"pyttsx3 TTS inicializado com {len(self.available_speakers)} vozes em português brasileiro")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar pyttsx3 TTS: {e}")
            self.tts_engine = None

    def _init_stt(self):
        """Inicializa o STT com fallback para SpeechRecognition em português brasileiro"""
        try:
            import speech_recognition as sr
            self.stt_recognizer = sr.Recognizer()
            self.stt_recognizer.energy_threshold = self.voice_config.get("energy_threshold", 4000)
            self.stt_recognizer.dynamic_energy_threshold = self.voice_config.get("dynamic_energy_threshold", True)
            self.stt_type = "speech_recognition"
            self.logger.info("SpeechRecognition STT inicializado para português brasileiro")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar SpeechRecognition STT: {e}")
            self.stt_type = None

    def get_speakers(self) -> List[str]:
        """Retorna lista de speakers disponíveis"""
        return [voice['name'] for voice in self.available_speakers]

    def set_voice(self, speaker: str):
        """Define o speaker/voz atual"""
        # Procurar por nome ou ID da voz
        for voice in self.available_speakers:
            if speaker in voice['name'] or speaker in voice['id']:
                self.current_speaker = voice
                if hasattr(self, 'tts_engine') and self.tts_engine:
                    self.tts_engine.setProperty('voice', voice['id'])
                self.voice_config["speaker"] = voice['name']
                self._save_config()
                self.logger.info(f"Voz alterada para: {voice['name']}")
                return
        
        self.logger.warning(f"Speaker não encontrado: {speaker}")

    def set_pitch(self, pitch: float):
        """Define o tom (pitch) da voz"""
        self.voice_config["pitch"] = max(0.5, min(2.0, pitch))
        self._save_config()
        self.logger.info(f"Pitch alterado para: {self.voice_config['pitch']}")

    def set_speed(self, speed: float):
        """Define a velocidade da fala"""
        self.voice_config["speed"] = max(0.5, min(2.0, speed))
        if hasattr(self, 'tts_engine') and self.tts_engine:
            self.tts_engine.setProperty('rate', int(speed * 200))
        self._save_config()
        self.logger.info(f"Velocidade alterada para: {self.voice_config['speed']}")

    def set_volume(self, volume: float):
        """Define o volume da voz"""
        self.voice_config["volume"] = max(0.1, min(2.0, volume))
        if hasattr(self, 'tts_engine') and self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
        self._save_config()
        self.logger.info(f"Volume alterado para: {self.voice_config['volume']}")

    def speak(self, text: str) -> bool:
        """Converte texto em fala usando pyttsx3 TTS"""
        if not hasattr(self, 'tts_engine') or not self.tts_engine or not text.strip():
            return False
        
        try:
            # Falar diretamente com pyttsx3
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            self.logger.info(f"Texto falado: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao falar texto: {e}")
            return False

    def _apply_voice_effects(self, audio: np.ndarray) -> np.ndarray:
        """Aplica efeitos de volume e speed ao áudio (versão simplificada)"""
        try:
            # Aplicar volume
            audio = audio * self.voice_config["volume"]
            
            # Aplicar speed (mudança de velocidade) - versão simplificada
            if self.voice_config["speed"] != 1.0:
                new_length = int(len(audio) / self.voice_config["speed"])
                audio = np.interp(
                    np.linspace(0, len(audio) - 1, new_length),
                    np.arange(len(audio)),
                    audio
                )
            
            # Clipping para evitar distorção
            audio = np.clip(audio, -1.0, 1.0)
            
            return audio
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar efeitos de voz: {e}")
            return audio

    def listen(self) -> Optional[str]:
        """Captura áudio e converte para texto usando STT disponível"""
        return self.listen_once(timeout=5)

    def start_listening(self):
        """Inicia escuta contínua em thread separada"""
        if self.is_listening:
            return
        
        self.is_listening = True
        thread = threading.Thread(target=self._continuous_listen)
        thread.daemon = True
        thread.start()
        self.logger.info("Escuta contínua iniciada")

    def stop_listening(self):
        """Para a escuta contínua"""
        self.is_listening = False
        self.logger.info("Escuta contínua parada")

    def _continuous_listen(self):
        """Loop de escuta contínua"""
        while self.is_listening:
            try:
                text = self.listen()
                if text:
                    # Aqui você pode processar o texto reconhecido
                    # Por exemplo, enviar para o chat ou executar comandos
                    self.memories["last_recognized"] = text
                    self._save_memories()
            except Exception as e:
                self.logger.error(f"Erro na escuta contínua: {e}")

    def get_voice_config(self) -> Dict[str, Any]:
        """Retorna configurações atuais de voz"""
        return self.voice_config.copy()

    def test_voice(self, text: str = "Olá, este é um teste de voz.") -> bool:
        """Testa a síntese de voz com texto padrão"""
        return self.speak(text)

    def set_command_callback(self, callback: Callable):
        """Define callback para comandos de voz"""
        self.command_callback = callback
        self.logger.info("Callback de comandos de voz configurado")

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do módulo de voz"""
        return {
            "tts_ready": hasattr(self, 'tts_engine') and self.tts_engine is not None,
            "stt_ready": hasattr(self, 'stt_model') and self.stt_model is not None or hasattr(self, 'stt_recognizer'),
            "stt_type": getattr(self, 'stt_type', None),
            "current_speaker": self.current_speaker['name'] if isinstance(self.current_speaker, dict) else self.current_speaker,
            "available_speakers": len(self.available_speakers),
            "is_listening": self.is_listening,
            "config": self.voice_config
        }

    def get_speakers_by_language(self) -> Dict[str, List[str]]:
        """Retorna lista de speakers agrupados por idioma"""
        speakers_by_lang = {}
        
        for voice in self.available_speakers:
            lang_code = voice.get('language', 'unknown')
            if lang_code not in speakers_by_lang:
                speakers_by_lang[lang_code] = []
            speakers_by_lang[lang_code].append(voice['name'])
            
        return speakers_by_lang
        
    def get_speaker_gender(self, speaker: str) -> str:
        """Tenta identificar o gênero da voz pelo nome do speaker"""
        # Procurar a voz pelo nome
        for voice in self.available_speakers:
            if voice['name'] == speaker:
                # Lógica simples baseada no nome da voz
                voice_lower = voice['name'].lower()
                
                # Vozes femininas típicas
                female_indicators = ['female', 'woman', 'girl', 'lady', 'maria', 'ana', 'sofia', 'zira']
                male_indicators = ['male', 'man', 'boy', 'guy', 'joao', 'pedro', 'carlos']
                
                for indicator in female_indicators:
                    if indicator in voice_lower:
                        return "Feminino"
                
                for indicator in male_indicators:
                    if indicator in voice_lower:
                        return "Masculino"
                
                break
        
        return "Desconhecido"
        
    def get_input_devices(self) -> List[str]:
        """Retorna lista de microfones disponíveis (nome)"""
        try:
            import speech_recognition as sr
            return sr.Microphone.list_microphone_names()
        except Exception:
            return []

    def set_input_device(self, index: int):
        """Define o índice do microfone a ser usado pelo STT"""
        self.input_device_index = index
        self.voice_config["input_device_index"] = index
        self._save_config()
        self.logger.info(f"Microfone definido para índice {index}")

    def listen_once(self, timeout=5) -> Optional[str]:
        """Captura áudio uma vez e converte para texto"""
        if not hasattr(self, 'stt_type') or not self.stt_type:
            self.logger.warning("STT não inicializado")
            return None
        
        try:
            if self.stt_type == "vosk" and hasattr(self, 'stt_model') and self.stt_model:
                # Usar Vosk STT
                sample_rate = 16000
                
                self.logger.info(f"Iniciando gravação por {timeout} segundos...")
                
                # Gravar áudio
                audio_data = sd.rec(
                    int(timeout * sample_rate), 
                    samplerate=sample_rate, 
                    channels=1,
                    dtype=np.int16
                )
                sd.wait()
                
                # Converter para formato Vosk
                rec = vosk.KaldiRecognizer(self.stt_model, sample_rate)
                rec.AcceptWaveform(audio_data.tobytes())
                
                # Obter resultado
                result = json.loads(rec.FinalResult())
                text = result.get('text', '').strip()
                
            elif self.stt_type == "speech_recognition" and hasattr(self, 'stt_recognizer') and self.stt_recognizer:
                # Usar SpeechRecognition
                import speech_recognition as sr
                
                self.logger.info(f"Iniciando gravação por {timeout} segundos...")
                
                mic_kwargs = {}
                if self.input_device_index is not None:
                    mic_kwargs["device_index"] = self.input_device_index
                with sr.Microphone(**mic_kwargs) as source:
                    self.stt_recognizer.adjust_for_ambient_noise(source, duration=1)
                    try:
                        audio = self.stt_recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
                        text = self.stt_recognizer.recognize_google(audio, language='pt-BR')
                    except sr.WaitTimeoutError:
                        self.logger.info("Timeout na gravação")
                        return None
                    except sr.UnknownValueError:
                        self.logger.info("Fala não reconhecida")
                        return None
                    except sr.RequestError as e:
                        self.logger.error(f"Erro na API de reconhecimento: {e}")
                        return None
            else:
                self.logger.error("Tipo de STT não suportado")
                return None
            
            if text:
                self.logger.info(f"Texto reconhecido: {text}")
                return text
            else:
                self.logger.info("Nenhum texto reconhecido")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao reconhecer fala: {e}")
            return None
