#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour XTerm
Gère l'interaction avec XTerm via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Gestion du curseur et des sélections
- Gestion des raccourcis clavier
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

# Rôles spécifiques à XTerm
XTERM_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'window': Atspi.Role.FRAME,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
    'text': Atspi.Role.TEXT,
    'terminal': Atspi.Role.TERMINAL,
    'panel': Atspi.Role.PANEL,
    'scroll_bar': Atspi.Role.SCROLL_BAR,
    'scroll_pane': Atspi.Role.SCROLL_PANE,
    'status_bar': Atspi.Role.STATUS_BAR,
    'toolbar': Atspi.Role.TOOL_BAR,
    'tooltip': Atspi.Role.TOOL_TIP,
    'combo_box': Atspi.Role.COMBO_BOX,
    'check_box': Atspi.Role.CHECK_BOX,
    'radio_button': Atspi.Role.RADIO_BUTTON,
    'image': Atspi.Role.IMAGE,
    'separator': Atspi.Role.SEPARATOR,
    'dialog': Atspi.Role.DIALOG,
    'alert': Atspi.Role.ALERT,
    'notification': Atspi.Role.NOTIFICATION
}

# Variables globales
_accessibility_manager = None
_xterm_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec XTerm."""
    global _accessibility_manager, _xterm_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance de XTerm
        _xterm_instance = find_xterm_instance()
        if not _xterm_instance:
            logger.error("XTerm n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration XTerm initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de XTerm : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _xterm_instance
    
    try:
        _xterm_instance = None
        _accessibility_manager = None
        logger.info("Intégration XTerm nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de XTerm : {str(e)}")

def find_xterm_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance de XTerm en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() == 'xterm':
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de XTerm : {str(e)}")
        return None

def get_instance() -> Optional[Atspi.Accessible]:
    """Récupère l'instance de XTerm."""
    return _xterm_instance

def get_terminal_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance de XTerm."""
    if not _xterm_instance:
        return {}
        
    try:
        return {
            'name': _xterm_instance.get_name(),
            'role': _xterm_instance.get_role_name(),
            'version': _xterm_instance.get_attributes().get('version', ''),
            'pid': _xterm_instance.get_process_id(),
            'children': len(_xterm_instance.get_children()),
            'rows': int(_xterm_instance.get_attributes().get('rows', '24')),
            'columns': int(_xterm_instance.get_attributes().get('columns', '80')),
            'font': _xterm_instance.get_attributes().get('font', ''),
            'colors': _xterm_instance.get_attributes().get('colors', ''),
            'encoding': _xterm_instance.get_attributes().get('encoding', ''),
            'shell': _xterm_instance.get_attributes().get('shell', ''),
            'working_dir': _xterm_instance.get_attributes().get('working_dir', '')
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations XTerm : {str(e)}")
        return {}

def get_cursor_position() -> Tuple[int, int]:
    """Récupère la position du curseur."""
    if not _xterm_instance:
        return (0, 0)
        
    try:
        def find_cursor_position(element: Atspi.Accessible) -> Optional[Tuple[int, int]]:
            if element.get_role() == Atspi.Role.TERMINAL:
                line = int(element.get_attributes().get('cursor_line', '0'))
                column = int(element.get_attributes().get('cursor_column', '0'))
                return (line, column)
            for child in element.get_children():
                result = find_cursor_position(child)
                if result:
                    return result
            return None
            
        return find_cursor_position(_xterm_instance) or (0, 0)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la position du curseur : {str(e)}")
        return (0, 0)

def get_selection() -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Récupère la sélection actuelle."""
    if not _xterm_instance:
        return ((0, 0), (0, 0))
        
    try:
        def find_selection(element: Atspi.Accessible) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
            if element.get_role() == Atspi.Role.TERMINAL:
                start_line = int(element.get_attributes().get('selection_start_line', '0'))
                start_column = int(element.get_attributes().get('selection_start_column', '0'))
                end_line = int(element.get_attributes().get('selection_end_line', '0'))
                end_column = int(element.get_attributes().get('selection_end_column', '0'))
                return ((start_line, start_column), (end_line, end_column))
            for child in element.get_children():
                result = find_selection(child)
                if result:
                    return result
            return None
            
        return find_selection(_xterm_instance) or ((0, 0), (0, 0))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection : {str(e)}")
        return ((0, 0), (0, 0))

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans XTerm."""
    if not _xterm_instance:
        return False
        
    try:
        if action == 'copy':
            # Copier la sélection
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'copy' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'paste':
            # Coller le contenu du presse-papiers
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'paste' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'select_all':
            # Tout sélectionner
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'select all' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'find':
            # Rechercher du texte
            text = kwargs.get('text', '')
            if not text:
                return False
                
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'find' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le texte à rechercher
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            child.set_text_contents(text)
                            break
                            
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'preferences':
            # Ouvrir les préférences
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'preferences' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'zoom_in':
            # Agrandir le texte
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'zoom in' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'zoom_out':
            # Réduire le texte
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'zoom out' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'zoom_reset':
            # Réinitialiser le zoom
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'zoom reset' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'fullscreen':
            # Passer en plein écran
            for element in _xterm_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'fullscreen' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'click':
            element = kwargs.get('element')
            if element:
                return element.do_action(0)  # Action par défaut (clic)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element:
                return element.do_action(1)  # Action par défaut (focus)
                
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} : {str(e)}")
        return False 