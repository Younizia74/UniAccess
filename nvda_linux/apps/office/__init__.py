#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des applications de bureau pour NVDA-Linux
=======================================================

Gère l'intégration avec différentes applications de bureau :
- LibreOffice (via AT-SPI)
- OnlyOffice (via AT-SPI)
- Microsoft Office (via Wine/Proton)
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, List

from ...core.config import get, set

logger = logging.getLogger(__name__)

# Importation dynamique des modules d'applications
OFFICE_MODULES = {
    "libreoffice": "nvda_linux.apps.office.libreoffice",
    "onlyoffice": "nvda_linux.apps.office.onlyoffice",
    "microsoft_office": "nvda_linux.apps.office.microsoft_office"
}

# Cache des instances d'applications
_office_instances: Dict[str, Any] = {}

def initialize() -> bool:
    """Initialise les modules d'applications de bureau"""
    try:
        for app, module_path in OFFICE_MODULES.items():
            if get("apps", f"office.{app}", False):
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "initialize"):
                        if module.initialize():
                            logger.info(f"Module {app} initialisé avec succès")
                            _office_instances[app] = module
                        else:
                            logger.warning(f"Échec de l'initialisation du module {app}")
                except ImportError as e:
                    logger.error(f"Impossible de charger le module {app}: {str(e)}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation du module {app}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des applications de bureau: {str(e)}")
        return False

def cleanup() -> bool:
    """Nettoie les ressources des applications de bureau"""
    try:
        for app, instance in _office_instances.items():
            try:
                if hasattr(instance, "cleanup"):
                    instance.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du module {app}: {str(e)}")
        
        _office_instances.clear()
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des applications de bureau: {str(e)}")
        return False

def get_app_instance(app: str) -> Optional[Any]:
    """Récupère l'instance d'une application"""
    return _office_instances.get(app)

def get_active_apps() -> List[str]:
    """Récupère la liste des applications actives"""
    return list(_office_instances.keys())

def is_app_supported(app: str) -> bool:
    """Vérifie si une application est supportée"""
    return app in OFFICE_MODULES

def get_app_info(app: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations sur une application"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_info"):
            return instance.get_info()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de l'application {app}: {str(e)}")
        return None

def get_app_accessibility_tree(app: str) -> Optional[Any]:
    """Récupère l'arbre d'accessibilité d'une application"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_accessibility_tree"):
            return instance.get_accessibility_tree()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité de l'application {app}: {str(e)}")
        return None

def get_app_focused_element(app: str) -> Optional[Any]:
    """Récupère l'élément focalisé dans une application"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_focused_element"):
            return instance.get_focused_element()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé de l'application {app}: {str(e)}")
        return None

def get_app_selection(app: str) -> Optional[str]:
    """Récupère la sélection dans une application"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_selection"):
            return instance.get_selection()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection de l'application {app}: {str(e)}")
        return None

def execute_app_action(app: str, action: str, **kwargs) -> bool:
    """Exécute une action dans une application"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "execute_action"):
            return instance.execute_action(action, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans l'application {app}: {str(e)}")
        return False

def get_app_document_info(app: str) -> Optional[Dict[str, Any]]:
    """Récupère les informations sur le document actif"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_document_info"):
            return instance.get_document_info()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du document de l'application {app}: {str(e)}")
        return None

def get_app_document_content(app: str) -> Optional[str]:
    """Récupère le contenu du document actif"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_document_content"):
            return instance.get_document_content()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du document de l'application {app}: {str(e)}")
        return None

def get_app_document_selection(app: str) -> Optional[str]:
    """Récupère la sélection dans le document actif"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "get_document_selection"):
            return instance.get_document_selection()
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection du document de l'application {app}: {str(e)}")
        return None

def execute_app_document_action(app: str, action: str, **kwargs) -> bool:
    """Exécute une action sur le document actif"""
    try:
        instance = get_app_instance(app)
        if instance and hasattr(instance, "execute_document_action"):
            return instance.execute_document_action(action, **kwargs)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} sur le document de l'application {app}: {str(e)}")
        return False 