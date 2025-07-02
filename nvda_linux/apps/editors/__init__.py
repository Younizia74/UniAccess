#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module principal pour la gestion des éditeurs de texte
Gère l'intégration avec divers éditeurs de texte via AT-SPI, notamment :
- Gedit
- Kate
- VSCode
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, List, Tuple
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

# Modules d'éditeurs supportés
EDITOR_MODULES = {
    'gedit': 'nvda_linux.apps.editors.gedit',
    'kate': 'nvda_linux.apps.editors.kate',
    'vscode': 'nvda_linux.apps.editors.vscode'
}

# Variables globales
_editor_instances = {}
_initialized = False

def initialize() -> bool:
    """Initialise les modules d'éditeurs de texte."""
    global _initialized
    
    try:
        if _initialized:
            return True
            
        # Initialiser AT-SPI
        Atspi.init()
        
        # Charger les modules d'éditeurs
        for editor_name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'initialize'):
                    if module.initialize():
                        logger.info(f"Module {editor_name} initialisé avec succès")
                    else:
                        logger.warning(f"Échec de l'initialisation du module {editor_name}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du module {editor_name} : {str(e)}")
                
        _initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modules d'éditeurs : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par les modules d'éditeurs."""
    global _initialized, _editor_instances
    
    try:
        # Nettoyer les modules d'éditeurs
        for editor_name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'cleanup'):
                    module.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du module {editor_name} : {str(e)}")
                
        _editor_instances = {}
        _initialized = False
        logger.info("Modules d'éditeurs nettoyés")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modules d'éditeurs : {str(e)}")

def get_instances() -> Dict[str, Any]:
    """Récupère les instances d'éditeurs en cours d'exécution."""
    global _editor_instances
    
    try:
        instances = {}
        for editor_name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_instance'):
                    instance = module.get_instance()
                    if instance:
                        instances[editor_name] = instance
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'instance {editor_name} : {str(e)}")
                
        _editor_instances = instances
        return instances
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des instances d'éditeurs : {str(e)}")
        return {}

def is_supported(editor_name: str) -> bool:
    """Vérifie si un éditeur est supporté."""
    return editor_name.lower() in EDITOR_MODULES

def get_editor_info(editor_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'éditeur spécifié ou tous les éditeurs."""
    try:
        if editor_name:
            if not is_supported(editor_name):
                return {}
                
            module = importlib.import_module(EDITOR_MODULES[editor_name])
            if hasattr(module, 'get_editor_info'):
                return module.get_editor_info()
            return {}
            
        # Récupérer les informations pour tous les éditeurs
        info = {}
        for name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_editor_info'):
                    info[name] = module.get_editor_info()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des informations de {name} : {str(e)}")
                
        return info
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations d'éditeur : {str(e)}")
        return {}

def get_documents(editor_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère la liste des documents ouverts."""
    try:
        if editor_name:
            if not is_supported(editor_name):
                return {}
                
            module = importlib.import_module(EDITOR_MODULES[editor_name])
            if hasattr(module, 'get_documents'):
                return {editor_name: module.get_documents()}
            return {}
            
        # Récupérer les documents pour tous les éditeurs
        documents = {}
        for name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_documents'):
                    documents[name] = module.get_documents()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des documents de {name} : {str(e)}")
                
        return documents
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des documents : {str(e)}")
        return {}

def get_current_document(editor_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur le document actif."""
    try:
        if editor_name:
            if not is_supported(editor_name):
                return {}
                
            module = importlib.import_module(EDITOR_MODULES[editor_name])
            if hasattr(module, 'get_current_document'):
                return module.get_current_document()
            return {}
            
        # Récupérer le document actif pour tous les éditeurs
        documents = {}
        for name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_current_document'):
                    doc = module.get_current_document()
                    if doc:
                        documents[name] = doc
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du document actif de {name} : {str(e)}")
                
        return documents
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du document actif : {str(e)}")
        return {}

def get_cursor_position(editor_name: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
    """Récupère la position du curseur."""
    try:
        if editor_name:
            if not is_supported(editor_name):
                return {}
                
            module = importlib.import_module(EDITOR_MODULES[editor_name])
            if hasattr(module, 'get_cursor_position'):
                return {editor_name: module.get_cursor_position()}
            return {}
            
        # Récupérer la position du curseur pour tous les éditeurs
        positions = {}
        for name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_cursor_position'):
                    pos = module.get_cursor_position()
                    if pos:
                        positions[name] = pos
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la position du curseur de {name} : {str(e)}")
                
        return positions
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la position du curseur : {str(e)}")
        return {}

def get_selection(editor_name: Optional[str] = None) -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Récupère la sélection actuelle."""
    try:
        if editor_name:
            if not is_supported(editor_name):
                return {}
                
            module = importlib.import_module(EDITOR_MODULES[editor_name])
            if hasattr(module, 'get_selection'):
                return {editor_name: module.get_selection()}
            return {}
            
        # Récupérer la sélection pour tous les éditeurs
        selections = {}
        for name, module_path in EDITOR_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_selection'):
                    sel = module.get_selection()
                    if sel:
                        selections[name] = sel
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la sélection de {name} : {str(e)}")
                
        return selections
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection : {str(e)}")
        return {}

def execute_action(editor_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans l'éditeur spécifié."""
    try:
        if not is_supported(editor_name):
            return False
            
        module = importlib.import_module(EDITOR_MODULES[editor_name])
        if hasattr(module, 'execute_action'):
            return module.execute_action(action, **kwargs)
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans {editor_name} : {str(e)}")
        return False 