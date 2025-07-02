#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module principal pour la gestion des lecteurs multimédias
Gère l'intégration avec différents lecteurs multimédias via AT-SPI, incluant :
- VLC
- MPV
- Rhythmbox
- Amarok
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import importlib
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

# Modules de lecteurs multimédias supportés
MEDIA_MODULES = {
    'vlc': 'nvda_linux.apps.media.vlc',
    'mpv': 'nvda_linux.apps.media.mpv',
    'rhythmbox': 'nvda_linux.apps.media.rhythmbox',
    'amarok': 'nvda_linux.apps.media.amarok'
}

# Variables globales
_media_instances = {}
_initialized = False

def initialize() -> bool:
    """Initialise les modules de lecteurs multimédias."""
    global _media_instances, _initialized
    
    try:
        if _initialized:
            return True
            
        # Initialiser AT-SPI
        Atspi.init()
        
        # Charger et initialiser chaque module
        for app_name, module_path in MEDIA_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'initialize') and module.initialize():
                    _media_instances[app_name] = module
                    logger.info(f"Module {app_name} initialisé avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du module {app_name} : {str(e)}")
                
        _initialized = True
        logger.info("Modules de lecteurs multimédias initialisés")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modules : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par les modules."""
    global _media_instances, _initialized
    
    try:
        for app_name, module in _media_instances.items():
            if hasattr(module, 'cleanup'):
                module.cleanup()
                logger.info(f"Module {app_name} nettoyé")
                
        _media_instances.clear()
        _initialized = False
        logger.info("Modules de lecteurs multimédias nettoyés")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modules : {str(e)}")

def get_instances() -> Dict[str, Any]:
    """Récupère les instances des lecteurs multimédias en cours d'exécution."""
    instances = {}
    for app_name, module in _media_instances.items():
        if hasattr(module, 'get_instance'):
            instance = module.get_instance()
            if instance:
                instances[app_name] = instance
    return instances

def is_supported(app_name: str) -> bool:
    """Vérifie si une application est supportée."""
    return app_name.lower() in MEDIA_MODULES

def get_player_info(app_name: str) -> Dict[str, Any]:
    """Récupère les informations sur un lecteur multimédia."""
    if app_name not in _media_instances:
        return {}
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'get_player_info'):
            return module.get_player_info()
        return {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de {app_name} : {str(e)}")
        return {}

def get_playlist(app_name: str) -> List[Dict[str, Any]]:
    """Récupère la liste de lecture d'un lecteur multimédia."""
    if app_name not in _media_instances:
        return []
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'get_playlist'):
            return module.get_playlist()
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la liste de lecture de {app_name} : {str(e)}")
        return []

def get_current_track(app_name: str) -> Dict[str, Any]:
    """Récupère les informations sur la piste en cours de lecture."""
    if app_name not in _media_instances:
        return {}
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'get_current_track'):
            return module.get_current_track()
        return {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la piste en cours de {app_name} : {str(e)}")
        return {}

def get_playback_state(app_name: str) -> Dict[str, Any]:
    """Récupère l'état de lecture d'un lecteur multimédia."""
    if app_name not in _media_instances:
        return {}
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'get_playback_state'):
            return module.get_playback_state()
        return {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état de lecture de {app_name} : {str(e)}")
        return {}

def play(app_name: str) -> bool:
    """Démarre la lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'play'):
            return module.play()
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la lecture dans {app_name} : {str(e)}")
        return False

def pause(app_name: str) -> bool:
    """Met en pause la lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'pause'):
            return module.pause()
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la pause dans {app_name} : {str(e)}")
        return False

def stop(app_name: str) -> bool:
    """Arrête la lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'stop'):
            return module.stop()
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt dans {app_name} : {str(e)}")
        return False

def next_track(app_name: str) -> bool:
    """Passe à la piste suivante."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'next_track'):
            return module.next_track()
        return False
    except Exception as e:
        logger.error(f"Erreur lors du passage à la piste suivante dans {app_name} : {str(e)}")
        return False

def previous_track(app_name: str) -> bool:
    """Revient à la piste précédente."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'previous_track'):
            return module.previous_track()
        return False
    except Exception as e:
        logger.error(f"Erreur lors du retour à la piste précédente dans {app_name} : {str(e)}")
        return False

def set_volume(app_name: str, volume: float) -> bool:
    """Définit le volume de lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'set_volume'):
            return module.set_volume(volume)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du réglage du volume dans {app_name} : {str(e)}")
        return False

def seek(app_name: str, position: float) -> bool:
    """Se positionne à un moment précis de la lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'seek'):
            return module.seek(position)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du positionnement dans {app_name} : {str(e)}")
        return False

def add_to_playlist(app_name: str, file_path: str) -> bool:
    """Ajoute un fichier à la liste de lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'add_to_playlist'):
            return module.add_to_playlist(file_path)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout à la liste de lecture dans {app_name} : {str(e)}")
        return False

def remove_from_playlist(app_name: str, track_id: str) -> bool:
    """Retire une piste de la liste de lecture."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'remove_from_playlist'):
            return module.remove_from_playlist(track_id)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la liste de lecture dans {app_name} : {str(e)}")
        return False

def execute_action(app_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans un lecteur multimédia."""
    if app_name not in _media_instances:
        return False
        
    try:
        module = _media_instances[app_name]
        if hasattr(module, 'execute_action'):
            return module.execute_action(action, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans {app_name} : {str(e)}")
        return False 