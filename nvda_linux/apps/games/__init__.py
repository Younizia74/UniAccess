#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des jeux pour NVDA-Linux
======================================

Gère l'intégration avec différents jeux et plateformes :
- Jeux natifs Linux (via AT-SPI)
- Jeux Steam (via Steam Runtime)
- Jeux Windows via Proton
- Jeux Windows via Wine
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, List

from ...core.config import get, set

logger = logging.getLogger(__name__)

# Importation dynamique des modules de jeux
GAME_MODULES = {
    "steam": "nvda_linux.apps.games.steam",
    "proton": "nvda_linux.apps.games.proton",
    "wine": "nvda_linux.apps.games.wine",
    "native": "nvda_linux.apps.games.native"
}

# Cache des instances de jeux
_game_instances: Dict[str, Any] = {}

def initialize() -> bool:
    """Initialise les modules de jeux"""
    try:
        for platform, module_path in GAME_MODULES.items():
            if get("apps", f"games.{platform}", False):
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "initialize"):
                        if module.initialize():
                            logger.info(f"Module {platform} initialisé avec succès")
                            _game_instances[platform] = module
                        else:
                            logger.warning(f"Échec de l'initialisation du module {platform}")
                except ImportError as e:
                    logger.error(f"Impossible de charger le module {platform}: {str(e)}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation du module {platform}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des jeux: {str(e)}")
        return False

def cleanup() -> bool:
    """Nettoie les ressources des jeux"""
    try:
        for platform, instance in _game_instances.items():
            try:
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du module {platform}: {str(e)}")
        
        _game_instances.clear()
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des jeux: {str(e)}")
        return False

def get_platform_instance(platform: str) -> Optional[Any]:
    """Récupère l'instance d'une plateforme de jeux"""
    return _game_instances.get(platform)

def get_active_platforms() -> List[str]:
    """Récupère la liste des plateformes actives"""
    return list(_game_instances.keys())

def is_platform_supported(platform: str) -> bool:
    """Vérifie si une plateforme est supportée"""
    return platform in GAME_MODULES

def get_platform_info(platform: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations sur une plateforme"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_info"):
            return instance.get_info()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de la plateforme {platform}: {str(e)}")
        return None

def get_running_games(platform: str) -> List[Dict[str, Any]]:
    """Récupère la liste des jeux en cours d'exécution"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_running_games"):
            return instance.get_running_games()
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des jeux en cours d'exécution pour la plateforme {platform}: {str(e)}")
        return []

def get_game_info(platform: str, game_id: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations sur un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_info"):
            return instance.get_game_info(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None

def launch_game(platform: str, game_id: str, **kwargs) -> bool:
    """Lance un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "launch_game"):
            return instance.launch_game(game_id, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du lancement du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return False

def terminate_game(platform: str, game_id: str) -> bool:
    """Termine un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "terminate_game"):
            return instance.terminate_game(game_id)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la terminaison du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return False

def get_game_accessibility_tree(platform: str, game_id: str) -> Optional[Any]:
    """Récupère l'arbre d'accessibilité d'un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_accessibility_tree"):
            return instance.get_game_accessibility_tree(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None

def get_game_focused_element(platform: str, game_id: str) -> Optional[Any]:
    """Récupère l'élément focalisé dans un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_focused_element"):
            return instance.get_game_focused_element(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None

def execute_game_action(platform: str, game_id: str, action: str, **kwargs) -> bool:
    """Exécute une action dans un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "execute_game_action"):
            return instance.execute_game_action(game_id, action, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans le jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return False

def get_game_audio_info(platform: str, game_id: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations audio d'un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_audio_info"):
            return instance.get_game_audio_info(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations audio du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None

def get_game_input_info(platform: str, game_id: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations d'entrée d'un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_input_info"):
            return instance.get_game_input_info(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations d'entrée du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None

def get_game_performance_info(platform: str, game_id: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations de performance d'un jeu"""
    try:
        instance = get_platform_instance(platform)
        if instance and hasattr(instance, "get_game_performance_info"):
            return instance.get_game_performance_info(game_id)
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de performance du jeu {game_id} sur la plateforme {platform}: {str(e)}")
        return None 