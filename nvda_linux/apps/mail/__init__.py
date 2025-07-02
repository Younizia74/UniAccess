#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des applications de messagerie pour NVDA-Linux
===========================================================

Gère l'intégration avec différentes applications de messagerie :
- Thunderbird (via AT-SPI)
- Evolution (via AT-SPI)
- Geary (via AT-SPI)
- KMail (via AT-SPI)
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, List

from ...core.config import get, set

logger = logging.getLogger(__name__)

# Importation dynamique des modules d'applications
MAIL_MODULES = {
    "thunderbird": "nvda_linux.apps.mail.thunderbird",
    "evolution": "nvda_linux.apps.mail.evolution",
    "geary": "nvda_linux.apps.mail.geary",
    "kmail": "nvda_linux.apps.mail.kmail"
}

# Cache des instances d'applications
_mail_instances: Dict[str, Any] = {}

def initialize() -> bool:
    """Initialise les modules d'applications de messagerie"""
    try:
        for app, module_path in MAIL_MODULES.items():
            if get("apps", f"mail.{app}", False):
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "initialize"):
                        if module.initialize():
                            logger.info(f"Module {app} initialisé avec succès")
                            _mail_instances[app] = module
                        else:
                            logger.warning(f"Échec de l'initialisation du module {app}")
                except ImportError as e:
                    logger.error(f"Impossible de charger le module {app}: {str(e)}")
                except Exception as e:
                    logger.error(f"Erreur lors de l'initialisation du module {app}: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des applications de messagerie: {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par les modules de messagerie"""
    try:
        for app, module in _mail_instances.items():
            if hasattr(module, "cleanup"):
                try:
                    module.cleanup()
                    logger.info(f"Module {app} nettoyé")
                except Exception as e:
                    logger.error(f"Erreur lors du nettoyage du module {app}: {str(e)}")
        
        _mail_instances.clear()
        logger.info("Modules de messagerie nettoyés")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modules de messagerie: {str(e)}")

def get_mail_instance(app: str) -> Optional[Any]:
    """Récupère une instance d'application de messagerie"""
    return _mail_instances.get(app)

def is_app_supported(app: str) -> bool:
    """Vérifie si une application de messagerie est supportée"""
    return app in MAIL_MODULES

def get_supported_apps() -> List[str]:
    """Récupère la liste des applications de messagerie supportées"""
    return list(MAIL_MODULES.keys())

def execute_action(app: str, action: str, **kwargs) -> bool:
    """Exécute une action dans une application de messagerie"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "execute_action"):
        return False
        
    try:
        return instance.execute_action(action, **kwargs)
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans {app}: {str(e)}")
        return False

def get_mail_info(app: str) -> Dict[str, Any]:
    """Récupère les informations sur une application de messagerie"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "get_mail_info"):
        return {}
        
    try:
        return instance.get_mail_info()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de {app}: {str(e)}")
        return {}

def get_folders(app: str) -> List[Dict[str, Any]]:
    """Récupère la liste des dossiers d'une application de messagerie"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "get_folders"):
        return []
        
    try:
        return instance.get_folders()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des dossiers de {app}: {str(e)}")
        return []

def get_messages(app: str, folder: str) -> List[Dict[str, Any]]:
    """Récupère la liste des messages d'un dossier"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "get_messages"):
        return []
        
    try:
        return instance.get_messages(folder)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des messages de {folder} dans {app}: {str(e)}")
        return []

def get_message_content(app: str, message_id: str) -> Dict[str, Any]:
    """Récupère le contenu d'un message"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "get_message_content"):
        return {}
        
    try:
        return instance.get_message_content(message_id)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du message {message_id} dans {app}: {str(e)}")
        return {}

def compose_message(app: str, **kwargs) -> bool:
    """Compose un nouveau message"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "compose_message"):
        return False
        
    try:
        return instance.compose_message(**kwargs)
    except Exception as e:
        logger.error(f"Erreur lors de la composition d'un message dans {app}: {str(e)}")
        return False

def reply_to_message(app: str, message_id: str, reply_all: bool = False) -> bool:
    """Répond à un message"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "reply_to_message"):
        return False
        
    try:
        return instance.reply_to_message(message_id, reply_all)
    except Exception as e:
        logger.error(f"Erreur lors de la réponse au message {message_id} dans {app}: {str(e)}")
        return False

def forward_message(app: str, message_id: str) -> bool:
    """Transmet un message"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "forward_message"):
        return False
        
    try:
        return instance.forward_message(message_id)
    except Exception as e:
        logger.error(f"Erreur lors de la transmission du message {message_id} dans {app}: {str(e)}")
        return False

def delete_message(app: str, message_id: str) -> bool:
    """Supprime un message"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "delete_message"):
        return False
        
    try:
        return instance.delete_message(message_id)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du message {message_id} dans {app}: {str(e)}")
        return False

def mark_message_read(app: str, message_id: str, read: bool = True) -> bool:
    """Marque un message comme lu/non lu"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "mark_message_read"):
        return False
        
    try:
        return instance.mark_message_read(message_id, read)
    except Exception as e:
        logger.error(f"Erreur lors du marquage du message {message_id} dans {app}: {str(e)}")
        return False

def search_messages(app: str, query: str, folder: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recherche des messages"""
    instance = get_mail_instance(app)
    if not instance or not hasattr(instance, "search_messages"):
        return []
        
    try:
        return instance.search_messages(query, folder)
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de messages dans {app}: {str(e)}")
        return [] 