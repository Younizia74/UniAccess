#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de synthèse vocale pour NVDA-Linux
Supporte plusieurs moteurs de synthèse vocale (espeak-ng, speech-dispatcher, etc.)
"""

import os
import logging
import subprocess
from typing import Optional, Dict, Any
import config

logger = logging.getLogger(__name__)

class SpeechEngine:
    """Classe de base pour les moteurs de synthèse vocale"""
    
    def __init__(self):
        self.initialized = False
        self.current_voice = None
        self.rate = 50
        self.pitch = 50
        self.volume = 100
    
    def initialize(self) -> bool:
        """Initialise le moteur de synthèse vocale"""
        raise NotImplementedError
    
    def speak(self, text: str) -> bool:
        """Fait parler le texte"""
        raise NotImplementedError
    
    def stop(self) -> bool:
        """Arrête la synthèse vocale"""
        raise NotImplementedError
    
    def set_voice(self, voice: str) -> bool:
        """Change la voix"""
        raise NotImplementedError
    
    def set_rate(self, rate: int) -> bool:
        """Change la vitesse de parole"""
        raise NotImplementedError
    
    def set_pitch(self, pitch: int) -> bool:
        """Change la hauteur de la voix"""
        raise NotImplementedError
    
    def set_volume(self, volume: int) -> bool:
        """Change le volume"""
        raise NotImplementedError

class EspeakEngine(SpeechEngine):
    """Moteur de synthèse vocale utilisant espeak-ng"""
    
    def __init__(self):
        super().__init__()
        self.process: Optional[subprocess.Popen] = None
    
    def initialize(self) -> bool:
        try:
            # Vérifie si espeak-ng est installé
            subprocess.run(['which', 'espeak-ng'], check=True, capture_output=True)
            self.initialized = True
            logger.info("Moteur espeak-ng initialisé avec succès")
            return True
        except subprocess.CalledProcessError:
            logger.error("espeak-ng n'est pas installé")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation d'espeak-ng: {str(e)}")
            return False
    
    def speak(self, text: str) -> bool:
        if not self.initialized:
            logger.error("Le moteur n'est pas initialisé")
            return False
        
        try:
            # Arrête toute synthèse en cours
            self.stop()
            
            # Construit la commande espeak-ng
            cmd = [
                'espeak-ng',
                '-v', self.current_voice or 'fr',
                '-s', str(self.rate * 2),  # Conversion du taux (0-100) en WPM
                '-p', str(self.pitch),
                '-a', str(self.volume),
                text
            ]
            
            # Lance la synthèse
            self.process = subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse vocale: {str(e)}")
            return False
    
    def stop(self) -> bool:
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
                self.process = None
                return True
            except Exception as e:
                logger.error(f"Erreur lors de l'arrêt de la synthèse: {str(e)}")
                return False
        return True
    
    def set_voice(self, voice: str) -> bool:
        try:
            # Vérifie si la voix existe
            result = subprocess.run(
                ['espeak-ng', '--voices=' + voice],
                capture_output=True,
                text=True
            )
            if voice in result.stdout:
                self.current_voice = voice
                return True
            logger.error(f"Voix '{voice}' non trouvée")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du changement de voix: {str(e)}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        if 0 <= rate <= 100:
            self.rate = rate
            return True
        return False
    
    def set_pitch(self, pitch: int) -> bool:
        if 0 <= pitch <= 100:
            self.pitch = pitch
            return True
        return False
    
    def set_volume(self, volume: int) -> bool:
        if 0 <= volume <= 100:
            self.volume = volume
            return True
        return False

class SpeechDispatcherEngine(SpeechEngine):
    """Moteur de synthèse vocale utilisant speech-dispatcher"""
    
    def initialize(self) -> bool:
        try:
            # Vérifie si speech-dispatcher est installé
            subprocess.run(['which', 'spd-say'], check=True, capture_output=True)
            self.initialized = True
            logger.info("Moteur speech-dispatcher initialisé avec succès")
            return True
        except subprocess.CalledProcessError:
            logger.error("speech-dispatcher n'est pas installé")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de speech-dispatcher: {str(e)}")
            return False
    
    def speak(self, text: str) -> bool:
        if not self.initialized:
            logger.error("Le moteur n'est pas initialisé")
            return False
        
        try:
            # Arrête toute synthèse en cours
            self.stop()
            
            # Construit la commande spd-say
            cmd = [
                'spd-say',
                '-t', self.current_voice or 'fr',
                '-r', str(self.rate),
                '-p', str(self.pitch),
                '-i', str(self.volume),
                text
            ]
            
            # Lance la synthèse
            self.process = subprocess.Popen(cmd)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse vocale: {str(e)}")
            return False
    
    def stop(self) -> bool:
        try:
            subprocess.run(['spd-say', '--stop'], check=True)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la synthèse: {str(e)}")
            return False
    
    def set_voice(self, voice: str) -> bool:
        try:
            # Vérifie si la voix existe
            result = subprocess.run(
                ['spd-say', '--list-voices'],
                capture_output=True,
                text=True
            )
            if voice in result.stdout:
                self.current_voice = voice
                return True
            logger.error(f"Voix '{voice}' non trouvée")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du changement de voix: {str(e)}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        if 0 <= rate <= 100:
            self.rate = rate
            return True
        return False
    
    def set_pitch(self, pitch: int) -> bool:
        if 0 <= pitch <= 100:
            self.pitch = pitch
            return True
        return False
    
    def set_volume(self, volume: int) -> bool:
        if 0 <= volume <= 100:
            self.volume = volume
            return True
        return False

# Instance globale du moteur de synthèse vocale
_speech_engine: Optional[SpeechEngine] = None

def initialize() -> bool:
    """Initialise le moteur de synthèse vocale"""
    global _speech_engine
    
    try:
        # Récupère la configuration
        engine_type = config.get_config('speech', 'engine', 'espeak')
        
        # Crée l'instance appropriée
        if engine_type == 'espeak':
            _speech_engine = EspeakEngine()
        elif engine_type == 'speech-dispatcher':
            _speech_engine = SpeechDispatcherEngine()
        else:
            logger.error(f"Moteur de synthèse vocale inconnu: {engine_type}")
            return False
        
        # Initialise le moteur
        if not _speech_engine.initialize():
            return False
        
        # Configure le moteur selon les préférences
        _speech_engine.set_voice(config.get_config('speech', 'voice', 'fr'))
        _speech_engine.set_rate(int(config.get_config('speech', 'rate', 50)))
        _speech_engine.set_pitch(int(config.get_config('speech', 'pitch', 50)))
        _speech_engine.set_volume(int(config.get_config('speech', 'volume', 100)))
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la synthèse vocale: {str(e)}")
        return False

def say(text: str) -> bool:
    """Fait parler le texte"""
    global _speech_engine
    
    if not _speech_engine:
        logger.error("Le moteur de synthèse vocale n'est pas initialisé")
        return False
    
    return _speech_engine.speak(text)

def stop() -> bool:
    """Arrête la synthèse vocale"""
    global _speech_engine
    
    if not _speech_engine:
        return False
    
    return _speech_engine.stop()

def cleanup() -> None:
    """Nettoie les ressources"""
    global _speech_engine
    
    if _speech_engine:
        _speech_engine.stop()
        _speech_engine = None 