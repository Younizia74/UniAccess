#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des entrées pour NVDA-Linux
Gère la capture des touches clavier et des raccourcis
"""

import os
import sys
import logging
import threading
import time
from typing import Optional, Dict, Set, Callable, List
import evdev
from evdev import categorize, ecodes
import config

logger = logging.getLogger(__name__)

class KeyState:
    """État des touches"""
    
    def __init__(self):
        self.pressed_keys: Set[int] = set()
        self.modifiers: Set[int] = set()
        self.last_key_time: float = 0
        self.key_repeat_delay: int = 500  # ms
        self.key_repeat_rate: int = 30    # ms

class InputManager:
    """Gère les entrées clavier"""
    
    def __init__(self):
        self.initialized = False
        self.devices: List[evdev.InputDevice] = []
        self.key_state = KeyState()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.key_handlers: Dict[str, List[Callable]] = {}
        self.modifier_handlers: Dict[str, List[Callable]] = {}
        self.gesture_handlers: Dict[str, List[Callable]] = {}
    
    def initialize(self) -> bool:
        """Initialise le gestionnaire d'entrées"""
        try:
            # Récupère la configuration
            self.key_state.key_repeat_delay = int(config.get_config('keyboard', 'key_repeat_delay', 500))
            self.key_state.key_repeat_rate = int(config.get_config('keyboard', 'key_repeat_rate', 30))
            
            # Trouve les périphériques clavier
            for device_path in evdev.list_devices():
                try:
                    device = evdev.InputDevice(device_path)
                    if self._is_keyboard_device(device):
                        self.devices.append(device)
                        logger.info(f"Périphérique clavier trouvé: {device.name}")
                except Exception as e:
                    logger.warning(f"Impossible d'ouvrir le périphérique {device_path}: {str(e)}")
            
            if not self.devices:
                logger.error("Aucun périphérique clavier trouvé")
                return False
            
            self.initialized = True
            logger.info("Gestionnaire d'entrées initialisé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du gestionnaire d'entrées: {str(e)}")
            return False
    
    def _is_keyboard_device(self, device: evdev.InputDevice) -> bool:
        """Vérifie si le périphérique est un clavier"""
        try:
            capabilities = device.capabilities()
            return ecodes.EV_KEY in capabilities and any(
                code in capabilities[ecodes.EV_KEY]
                for code in [ecodes.KEY_A, ecodes.KEY_SPACE, ecodes.KEY_ENTER]
            )
        except Exception:
            return False
    
    def register_key_handler(self, key: str, handler: Callable) -> bool:
        """Enregistre un gestionnaire de touche"""
        try:
            if key not in self.key_handlers:
                self.key_handlers[key] = []
            self.key_handlers[key].append(handler)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du gestionnaire de touche: {str(e)}")
            return False
    
    def register_modifier_handler(self, modifier: str, handler: Callable) -> bool:
        """Enregistre un gestionnaire de modificateur"""
        try:
            if modifier not in self.modifier_handlers:
                self.modifier_handlers[modifier] = []
            self.modifier_handlers[modifier].append(handler)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du gestionnaire de modificateur: {str(e)}")
            return False
    
    def register_gesture_handler(self, gesture: str, handler: Callable) -> bool:
        """Enregistre un gestionnaire de geste"""
        try:
            if gesture not in self.gesture_handlers:
                self.gesture_handlers[gesture] = []
            self.gesture_handlers[gesture].append(handler)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du gestionnaire de geste: {str(e)}")
            return False
    
    def _handle_key_event(self, event: evdev.InputEvent) -> None:
        """Gère un événement de touche"""
        try:
            if event.type == ecodes.EV_KEY:
                key = categorize(event)
                
                # Gère les modificateurs
                if key.keystate == evdev.KeyEvent.key_down:
                    self.key_state.pressed_keys.add(event.code)
                    if event.code in self._get_modifier_codes():
                        self.key_state.modifiers.add(event.code)
                        self._trigger_modifier_handlers(event.code, True)
                elif key.keystate == evdev.KeyEvent.key_up:
                    self.key_state.pressed_keys.discard(event.code)
                    if event.code in self._get_modifier_codes():
                        self.key_state.modifiers.discard(event.code)
                        self._trigger_modifier_handlers(event.code, False)
                
                # Gère les touches normales
                if key.keystate == evdev.KeyEvent.key_down:
                    self._trigger_key_handlers(event.code)
                    self._check_gestures()
                
                # Gère la répétition des touches
                if key.keystate == evdev.KeyEvent.key_down:
                    self.key_state.last_key_time = time.time() * 1000
                elif key.keystate == evdev.KeyEvent.key_up:
                    self.key_state.last_key_time = 0
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'événement de touche: {str(e)}")
    
    def _get_modifier_codes(self) -> Set[int]:
        """Retourne les codes des touches modificateurs"""
        return {
            ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT,
            ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
            ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
            ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA
        }
    
    def _trigger_key_handlers(self, key_code: int) -> None:
        """Déclenche les gestionnaires de touche"""
        try:
            key_name = ecodes.KEY[key_code]
            if key_name in self.key_handlers:
                for handler in self.key_handlers[key_name]:
                    handler()
        except Exception as e:
            logger.error(f"Erreur lors du déclenchement des gestionnaires de touche: {str(e)}")
    
    def _trigger_modifier_handlers(self, modifier_code: int, pressed: bool) -> None:
        """Déclenche les gestionnaires de modificateur"""
        try:
            modifier_name = ecodes.KEY[modifier_code]
            if modifier_name in self.modifier_handlers:
                for handler in self.modifier_handlers[modifier_name]:
                    handler(pressed)
        except Exception as e:
            logger.error(f"Erreur lors du déclenchement des gestionnaires de modificateur: {str(e)}")
    
    def _check_gestures(self) -> None:
        """Vérifie les gestes de touches"""
        try:
            # Ici, on pourrait implémenter la détection de gestes
            # Par exemple, Ctrl+Alt+L pour verrouiller l'écran
            pass
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des gestes: {str(e)}")
    
    def _input_loop(self) -> None:
        """Boucle principale de capture des entrées"""
        try:
            while self.running:
                for device in self.devices:
                    try:
                        for event in device.read_loop():
                            if self.running:
                                self._handle_key_event(event)
                    except Exception as e:
                        logger.error(f"Erreur lors de la lecture du périphérique {device.name}: {str(e)}")
                        time.sleep(0.1)  # Évite de surcharger le CPU en cas d'erreur
        except Exception as e:
            logger.error(f"Erreur dans la boucle de capture des entrées: {str(e)}")
        finally:
            self.running = False
    
    def start(self) -> bool:
        """Démarre la capture des entrées"""
        if not self.initialized:
            logger.error("Le gestionnaire d'entrées n'est pas initialisé")
            return False
        
        try:
            self.running = True
            self.thread = threading.Thread(target=self._input_loop)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Capture des entrées démarrée")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la capture des entrées: {str(e)}")
            self.running = False
            return False
    
    def stop(self) -> None:
        """Arrête la capture des entrées"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def cleanup(self) -> None:
        """Nettoie les ressources"""
        try:
            self.stop()
            for device in self.devices:
                try:
                    device.close()
                except Exception:
                    pass
            self.devices.clear()
            self.key_handlers.clear()
            self.modifier_handlers.clear()
            self.gesture_handlers.clear()
            self.initialized = False
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du gestionnaire d'entrées: {str(e)}")

# Instance globale du gestionnaire d'entrées
_input_manager: Optional[InputManager] = None

def initialize() -> bool:
    """Initialise le gestionnaire d'entrées"""
    global _input_manager
    
    try:
        _input_manager = InputManager()
        return _input_manager.initialize()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du gestionnaire d'entrées: {str(e)}")
        return False

def listen_keys() -> bool:
    """Démarre l'écoute des touches"""
    global _input_manager
    
    if not _input_manager:
        logger.error("Le gestionnaire d'entrées n'est pas initialisé")
        return False
    
    return _input_manager.start()

def register_key_handler(key: str, handler: Callable) -> bool:
    """Enregistre un gestionnaire de touche"""
    global _input_manager
    
    if not _input_manager:
        logger.error("Le gestionnaire d'entrées n'est pas initialisé")
        return False
    
    return _input_manager.register_key_handler(key, handler)

def register_modifier_handler(modifier: str, handler: Callable) -> bool:
    """Enregistre un gestionnaire de modificateur"""
    global _input_manager
    
    if not _input_manager:
        logger.error("Le gestionnaire d'entrées n'est pas initialisé")
        return False
    
    return _input_manager.register_modifier_handler(modifier, handler)

def register_gesture_handler(gesture: str, handler: Callable) -> bool:
    """Enregistre un gestionnaire de geste"""
    global _input_manager
    
    if not _input_manager:
        logger.error("Le gestionnaire d'entrées n'est pas initialisé")
        return False
    
    return _input_manager.register_gesture_handler(gesture, handler)

def cleanup() -> None:
    """Nettoie les ressources"""
    global _input_manager
    
    if _input_manager:
        _input_manager.cleanup()
        _input_manager = None 