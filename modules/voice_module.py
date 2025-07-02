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
            "tts_language": "en",
            "tts_model": "v3_en",
            "speaker": "en_0",
            "sample_rate": 48000,
            "pitch": 1.0,
            "speed": 1.0,
            "volume": 1.0,
            "device": "cpu"
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
        """Inicializa o Silero TTS"""
        try:
            self.tts_model = SileroTTS(
                language=self.voice_config["tts_language"],
                model_id=self.voice_config["tts_model"],
                device=self.voice_config["device"]
            )
            
            # Obter speakers disponíveis
            self.available_speakers = self.tts_model.get_available_speakers()
            
            # Definir speaker padrão se não estiver definido
            if not self.current_speaker and self.available_speakers:
                self.current_speaker = self.available_speakers[0]
                self.voice_config["speaker"] = self.current_speaker
            
            self.logger.info(f"Silero TTS inicializado - Modelo: {self.voice_config['tts_model']}")
            self.logger.info(f"Speakers disponíveis: {len(self.available_speakers)}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Silero TTS: {e}")
            self.tts_model = None

    def _init_stt(self):
        """Inicializa o Vosk STT"""
        try:
            # Usar Vosk para STT (open source)
            model_path = "vosk-model-small-en-us-0.15"  # Baixar se necessário
            if not os.path.exists(model_path):
                self.logger.warning("Modelo Vosk não encontrado. STT pode não funcionar.")
                return
                
            self.stt_model = vosk.Model(model_path)
            self.logger.info("Vosk STT inicializado")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Vosk STT: {e}")
            self.stt_model = None

    def get_speakers(self) -> List[str]:
        """Retorna lista de speakers disponíveis"""
        return self.available_speakers

    def set_voice(self, speaker: str):
        """Define o speaker/voz atual"""
        if speaker in self.available_speakers:
            self.current_speaker = speaker
            self.voice_config["speaker"] = speaker
            self._save_config()
            self.logger.info(f"Voz alterada para: {speaker}")
        else:
            self.logger.warning(f"Speaker não encontrado: {speaker}")

    def set_pitch(self, pitch: float):
        """Define o tom (pitch) da voz"""
        self.voice_config["pitch"] = max(0.5, min(2.0, pitch))
        self._save_config()
        self.logger.info(f"Pitch alterado para: {self.voice_config['pitch']}")

    def set_speed(self, speed: float):
        """Define a velocidade da fala"""
        self.voice_config["speed"] = max(0.5, min(2.0, speed))
        self._save_config()
        self.logger.info(f"Velocidade alterada para: {self.voice_config['speed']}")

    def set_volume(self, volume: float):
        """Define o volume da voz"""
        self.voice_config["volume"] = max(0.1, min(2.0, volume))
        self._save_config()
        self.logger.info(f"Volume alterado para: {self.voice_config['volume']}")

    def speak(self, text: str) -> bool:
        """Converte texto em fala usando Silero TTS"""
        if not self.tts_model or not text.strip():
            return False
        
        try:
            # Gerar áudio temporário com Silero TTS
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.close()
            
            # Definir speaker se disponível
            if self.current_speaker:
                self.tts_model.change_speaker(self.current_speaker)
            
            # Gerar áudio
            self.tts_model.tts(
                text=text,
                output_file=temp_file.name
            )
            
            # Carregar áudio
            audio, sample_rate = sf.read(temp_file.name)
            
            # Aplicar modificações de volume e speed
            audio = self._apply_voice_effects(audio)
            
            # Reproduzir áudio usando abordagem mais robusta
            try:
                # Tentar reproduzir com configurações padrão
                sd.play(audio, samplerate=sample_rate, blocking=True)
            except Exception as playback_error:
                self.logger.warning(f"Erro na reprodução direta: {playback_error}")
                try:
                    # Fallback: usar sistema de áudio do Windows
                    import subprocess
                    subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{temp_file.name}").PlaySync()'], 
                                   check=True, capture_output=True)
                except Exception as fallback_error:
                    self.logger.error(f"Erro no fallback de reprodução: {fallback_error}")
                    # Usar abordagem mais simples
                    import winsound
                    winsound.PlaySound(temp_file.name, winsound.SND_FILENAME)
            
            # Limpar arquivo temporário
            os.unlink(temp_file.name)
            
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
        """Captura áudio e converte para texto usando Vosk STT"""
        if not self.stt_model:
            self.logger.warning("STT não inicializado")
            return None
        
        try:
            # Configurações de gravação
            duration = 5  # segundos
            sample_rate = 16000  # Vosk recomenda 16kHz
            
            self.logger.info("Iniciando gravação...")
            
            # Gravar áudio
            audio_data = sd.rec(
                int(duration * sample_rate), 
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
            
            if text:
                self.logger.info(f"Texto reconhecido: {text}")
                return text
            else:
                self.logger.info("Nenhum texto reconhecido")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao reconhecer fala: {e}")
            return None

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
            "tts_ready": self.tts_model is not None,
            "stt_ready": self.stt_model is not None,
            "current_speaker": self.current_speaker,
            "available_speakers": len(self.available_speakers),
            "is_listening": self.is_listening,
            "config": self.voice_config
        }
