#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des navigateurs pour NVDA-Linux
=============================================

Gère l'intégration avec différents navigateurs web :
- Firefox (via AT-SPI)
- Chrome/Chromium (via AT-SPI)
- Edge (via AT-SPI)
- Applications Electron (via AT-SPI)
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, List

from ...core.config import get, set

logger = logging.getLogger(__name__)

# Importation dynamique des modules de navigateurs
BROWSER_MODULES = {
    "firefox": "nvda_linux.apps.browsers.firefox",
    "chrome": "nvda_linux.apps.browsers.chrome",
    "edge": "nvda_linux.apps.browsers.edge",
    "electron": "nvda_linux.apps.browsers.electron"
}

# Cache des instances de navigateurs
_browser_instances: Dict[str, Any] = {}

def initialize() -> bool:
    """Initialise les modules de navigateurs"""
    try:
        for browser, module_path in BROWSER_MODULES.items():
            if get("apps", f"browsers.{browser}", False):
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "initialize"):
                        if module.initialize():
                            logger.info(f"Module {browser} initialisé avec succès")
                            _browser_instances[browser] = module
                        else:
                            logger.warning(f"Échec de l'initialisation du module {browser}")
                except ImportError as e:
                    logger.error(f"Impossible de charger le module {browser}: {str(e)}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation du module {browser}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des navigateurs: {str(e)}")
        return False

def cleanup() -> bool:
    """Nettoie les ressources des navigateurs"""
    try:
        for browser, instance in _browser_instances.items():
            try:
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du module {browser}: {str(e)}")
        
        _browser_instances.clear()
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des navigateurs: {str(e)}")
        return False

def get_browser_instance(browser: str) -> Optional[Any]:
    """Récupère l'instance d'un navigateur"""
    return _browser_instances.get(browser)

def get_active_browsers() -> List[str]:
    """Récupère la liste des navigateurs actifs"""
    return list(_browser_instances.keys())

def is_browser_supported(browser: str) -> bool:
    """Vérifie si un navigateur est supporté"""
    return browser in BROWSER_MODULES

def get_browser_info(browser: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations sur un navigateur"""
    try:
        instance = get_browser_instance(browser)
        if instance and hasattr(instance, "get_info"):
            return instance.get_info()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du navigateur {browser}: {str(e)}")
        return None

def get_browser_accessibility_tree(browser: str) -> Optional[Any]:
    """Récupère l'arbre d'accessibilité d'un navigateur"""
    try:
        instance = get_browser_instance(browser)
        if instance and hasattr(instance, "get_accessibility_tree"):
            return instance.get_accessibility_tree()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité du navigateur {browser}: {str(e)}")
        return None

def get_browser_focused_element(browser: str) -> Optional[Any]:
    """Récupère l'élément focalisé dans un navigateur"""
    try:
        instance = get_browser_instance(browser)
        if instance and hasattr(instance, "get_focused_element"):
            return instance.get_focused_element()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé du navigateur {browser}: {str(e)}")
        return None

def get_browser_selection(browser: str) -> Optional[str]:
    """Récupère la sélection dans un navigateur"""
    try:
        instance = get_browser_instance(browser)
        if instance and hasattr(instance, "get_selection"):
            return instance.get_selection()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection du navigateur {browser}: {str(e)}")
        return None

def execute_browser_action(browser: str, action: str, **kwargs) -> bool:
    """Exécute une action dans un navigateur"""
    try:
        instance = get_browser_instance(browser)
        if instance and hasattr(instance, "execute_action"):
            return instance.execute_action(action, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans le navigateur {browser}: {str(e)}")
        return False 