#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module principal pour la gestion des terminaux
Gère l'intégration avec divers terminaux via AT-SPI, notamment :
- GNOME Terminal
- Konsole
- XTerm
- Terminator
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

# Modules de terminaux supportés
TERMINAL_MODULES = {
    'gnome_terminal': 'nvda_linux.apps.terminals.gnome_terminal',
    'konsole': 'nvda_linux.apps.terminals.konsole',
    'xterm': 'nvda_linux.apps.terminals.xterm',
    'terminator': 'nvda_linux.apps.terminals.terminator'
}

# Variables globales
_terminal_instances = {}
_initialized = False

def initialize() -> bool:
    """Initialise les modules de terminaux."""
    global _initialized
    
    try:
        if _initialized:
            return True
            
        # Initialiser AT-SPI
        Atspi.init()
        
        # Charger les modules de terminaux
        for terminal_name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'initialize'):
                    if module.initialize():
                        logger.info(f"Module {terminal_name} initialisé avec succès")
                    else:
                        logger.warning(f"Échec de l'initialisation du module {terminal_name}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement du module {terminal_name} : {str(e)}")
                
        _initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des modules de terminaux : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par les modules de terminaux."""
    global _initialized, _terminal_instances
    
    try:
        # Nettoyer les modules de terminaux
        for terminal_name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'cleanup'):
                    module.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du module {terminal_name} : {str(e)}")
                
        _terminal_instances = {}
        _initialized = False
        logger.info("Modules de terminaux nettoyés")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des modules de terminaux : {str(e)}")

def get_instances() -> Dict[str, Any]:
    """Récupère les instances de terminaux en cours d'exécution."""
    global _terminal_instances
    
    try:
        instances = {}
        for terminal_name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_instance'):
                    instance = module.get_instance()
                    if instance:
                        instances[terminal_name] = instance
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'instance {terminal_name} : {str(e)}")
                
        _terminal_instances = instances
        return instances
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des instances de terminaux : {str(e)}")
        return {}

def is_supported(terminal_name: str) -> bool:
    """Vérifie si un terminal est supporté."""
    return terminal_name.lower() in TERMINAL_MODULES

def get_terminal_info(terminal_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur le terminal spécifié ou tous les terminaux."""
    try:
        if terminal_name:
            if not is_supported(terminal_name):
                return {}
                
            module = importlib.import_module(TERMINAL_MODULES[terminal_name])
            if hasattr(module, 'get_terminal_info'):
                return module.get_terminal_info()
            return {}
            
        # Récupérer les informations pour tous les terminaux
        info = {}
        for name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_terminal_info'):
                    info[name] = module.get_terminal_info()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des informations de {name} : {str(e)}")
                
        return info
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de terminal : {str(e)}")
        return {}

def get_tabs(terminal_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère la liste des onglets ouverts."""
    try:
        if terminal_name:
            if not is_supported(terminal_name):
                return {}
                
            module = importlib.import_module(TERMINAL_MODULES[terminal_name])
            if hasattr(module, 'get_tabs'):
                return {terminal_name: module.get_tabs()}
            return {}
            
        # Récupérer les onglets pour tous les terminaux
        tabs = {}
        for name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_tabs'):
                    tabs[name] = module.get_tabs()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des onglets de {name} : {str(e)}")
                
        return tabs
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des onglets : {str(e)}")
        return {}

def get_current_tab(terminal_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'onglet actif."""
    try:
        if terminal_name:
            if not is_supported(terminal_name):
                return {}
                
            module = importlib.import_module(TERMINAL_MODULES[terminal_name])
            if hasattr(module, 'get_current_tab'):
                return module.get_current_tab()
            return {}
            
        # Récupérer l'onglet actif pour tous les terminaux
        tabs = {}
        for name, module_path in TERMINAL_MODULES.items():
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_current_tab'):
                    tab = module.get_current_tab()
                    if tab:
                        tabs[name] = tab
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de l'onglet actif de {name} : {str(e)}")
                
        return tabs
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'onglet actif : {str(e)}")
        return {}

def get_cursor_position(terminal_name: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
    """Récupère la position du curseur."""
    try:
        if terminal_name:
            if not is_supported(terminal_name):
                return {}
                
            module = importlib.import_module(TERMINAL_MODULES[terminal_name])
            if hasattr(module, 'get_cursor_position'):
                return {terminal_name: module.get_cursor_position()}
            return {}
            
        # Récupérer la position du curseur pour tous les terminaux
        positions = {}
        for name, module_path in TERMINAL_MODULES.items():
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

def get_selection(terminal_name: Optional[str] = None) -> Dict[str, Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Récupère la sélection actuelle."""
    try:
        if terminal_name:
            if not is_supported(terminal_name):
                return {}
                
            module = importlib.import_module(TERMINAL_MODULES[terminal_name])
            if hasattr(module, 'get_selection'):
                return {terminal_name: module.get_selection()}
            return {}
            
        # Récupérer la sélection pour tous les terminaux
        selections = {}
        for name, module_path in TERMINAL_MODULES.items():
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

def execute_action(terminal_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans le terminal spécifié."""
    try:
        if not is_supported(terminal_name):
            return False
            
        module = importlib.import_module(TERMINAL_MODULES[terminal_name])
        if hasattr(module, 'execute_action'):
            return module.execute_action(action, **kwargs)
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} dans {terminal_name} : {str(e)}")
        return False 