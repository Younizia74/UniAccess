#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour OnlyOffice
Gère l'interaction avec OnlyOffice via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu des documents
- Gestion des documents
- Gestion des formulaires
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

# Rôles spécifiques à OnlyOffice
ONLYOFFICE_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'document': Atspi.Role.DOCUMENT_FRAME,
    'toolbar': Atspi.Role.TOOL_BAR,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
    'text': Atspi.Role.TEXT,
    'edit': Atspi.Role.ENTRY,
    'combo_box': Atspi.Role.COMBO_BOX,
    'check_box': Atspi.Role.CHECK_BOX,
    'radio_button': Atspi.Role.RADIO_BUTTON,
    'slider': Atspi.Role.SLIDER,
    'progress_bar': Atspi.Role.PROGRESS_BAR,
    'status_bar': Atspi.Role.STATUS_BAR,
    'scroll_bar': Atspi.Role.SCROLL_BAR,
    'scroll_pane': Atspi.Role.SCROLL_PANE,
    'panel': Atspi.Role.PANEL,
    'dialog': Atspi.Role.DIALOG,
    'alert': Atspi.Role.ALERT,
    'notification': Atspi.Role.NOTIFICATION,
    'tooltip': Atspi.Role.TOOL_TIP,
    'table': Atspi.Role.TABLE,
    'table_cell': Atspi.Role.TABLE_CELL,
    'table_row': Atspi.Role.TABLE_ROW,
    'table_column': Atspi.Role.TABLE_COLUMN,
    'table_header': Atspi.Role.TABLE_HEADER,
    'table_header_row': Atspi.Role.TABLE_HEADER_ROW,
    'table_header_cell': Atspi.Role.TABLE_HEADER_CELL,
    'paragraph': Atspi.Role.PARAGRAPH,
    'heading': Atspi.Role.HEADING,
    'list': Atspi.Role.LIST,
    'list_item': Atspi.Role.LIST_ITEM,
    'image': Atspi.Role.IMAGE,
    'link': Atspi.Role.LINK,
    'form': Atspi.Role.FORM,
    'form_field': Atspi.Role.ENTRY,
}

# Variables globales
_accessibility_manager = None
_onlyoffice_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec OnlyOffice."""
    global _accessibility_manager, _onlyoffice_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance d'OnlyOffice
        _onlyoffice_instance = find_onlyoffice_instance()
        if not _onlyoffice_instance:
            logger.error("OnlyOffice n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration OnlyOffice initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation d'OnlyOffice : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _onlyoffice_instance
    
    try:
        _onlyoffice_instance = None
        _accessibility_manager = None
        logger.info("Intégration OnlyOffice nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage d'OnlyOffice : {str(e)}")

def find_onlyoffice_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance d'OnlyOffice en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() in ['onlyoffice', 'onlyoffice-desktopeditors']:
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'OnlyOffice : {str(e)}")
        return None

def get_onlyoffice_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance d'OnlyOffice."""
    if not _onlyoffice_instance:
        return {}
        
    try:
        return {
            'name': _onlyoffice_instance.get_name(),
            'role': _onlyoffice_instance.get_role_name(),
            'version': _onlyoffice_instance.get_attributes().get('version', ''),
            'pid': _onlyoffice_instance.get_process_id(),
            'children': len(_onlyoffice_instance.get_children())
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations OnlyOffice : {str(e)}")
        return {}

def get_accessibility_tree() -> Dict[str, Any]:
    """Récupère l'arbre d'accessibilité d'OnlyOffice."""
    if not _onlyoffice_instance:
        return {}
        
    def get_element_info(element: Atspi.Accessible) -> Dict[str, Any]:
        try:
            info = {
                'name': element.get_name(),
                'role': element.get_role_name(),
                'description': element.get_description(),
                'children': []
            }
            
            for child in element.get_children():
                info['children'].append(get_element_info(child))
                
            return info
        except Exception:
            return {}
            
    try:
        return get_element_info(_onlyoffice_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité : {str(e)}")
        return {}

def get_focused_element() -> Dict[str, Any]:
    """Récupère l'élément actuellement focalisé dans OnlyOffice."""
    try:
        focused = Atspi.get_focused()
        if not focused:
            return {}
            
        return {
            'name': focused.get_name(),
            'role': focused.get_role_name(),
            'description': focused.get_description(),
            'attributes': focused.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé : {str(e)}")
        return {}

def get_current_selection() -> List[Dict[str, Any]]:
    """Récupère la sélection actuelle dans OnlyOffice."""
    try:
        focused = Atspi.get_focused()
        if not focused:
            return []
            
        selection = focused.get_selection()
        if not selection:
            return []
            
        return [{
            'name': item.get_name(),
            'role': item.get_role_name(),
            'description': item.get_description()
        } for item in selection]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection : {str(e)}")
        return []

def get_active_document() -> Dict[str, Any]:
    """Récupère les informations sur le document actif."""
    if not _onlyoffice_instance:
        return {}
        
    try:
        # Parcourir l'arbre pour trouver le document actif
        def find_document(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if element.get_role() == Atspi.Role.DOCUMENT_FRAME:
                return element
            for child in element.get_children():
                doc = find_document(child)
                if doc:
                    return doc
            return None
            
        doc = find_document(_onlyoffice_instance)
        if not doc:
            return {}
            
        return {
            'name': doc.get_name(),
            'role': doc.get_role_name(),
            'description': doc.get_description(),
            'attributes': doc.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du document actif : {str(e)}")
        return {}

def get_document_content() -> str:
    """Récupère le contenu du document actif."""
    doc = get_active_document()
    if not doc:
        return ""
        
    try:
        # Parcourir l'arbre pour extraire le texte
        def extract_text(element: Atspi.Accessible) -> str:
            text = ""
            if element.get_role() == Atspi.Role.TEXT:
                text += element.get_text(0, -1)
            for child in element.get_children():
                text += extract_text(child)
            return text
            
        return extract_text(_onlyoffice_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du document : {str(e)}")
        return ""

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans OnlyOffice."""
    if not _onlyoffice_instance:
        return False
        
    try:
        if action == 'new_document':
            # Simuler Ctrl+N
            return _onlyoffice_instance.do_action(0)  # Action par défaut pour nouveau document
            
        elif action == 'open_document':
            # Simuler Ctrl+O
            return _onlyoffice_instance.do_action(1)  # Action par défaut pour ouvrir
            
        elif action == 'save_document':
            # Simuler Ctrl+S
            return _onlyoffice_instance.do_action(2)  # Action par défaut pour sauvegarder
            
        elif action == 'print_document':
            # Simuler Ctrl+P
            return _onlyoffice_instance.do_action(3)  # Action par défaut pour imprimer
            
        elif action == 'click':
            element = kwargs.get('element')
            if element:
                return element.do_action(0)  # Action par défaut (clic)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element:
                return element.do_action(1)  # Action par défaut (focus)
                
        elif action == 'scroll':
            element = kwargs.get('element')
            direction = kwargs.get('direction', 'down')
            if element:
                if direction == 'up':
                    return element.do_action(2)  # Action par défaut (scroll up)
                else:
                    return element.do_action(3)  # Action par défaut (scroll down)
                    
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} : {str(e)}")
        return False 