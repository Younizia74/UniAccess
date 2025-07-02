#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour Microsoft Office via Wine
Gère l'interaction avec Microsoft Office via Wine et AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu des documents
- Gestion des documents
- Gestion des formulaires
- Gestion des raccourcis clavier
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional, List, Tuple
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

# Rôles spécifiques à Microsoft Office
MSOFFICE_ROLES = {
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

# Applications Microsoft Office
MSOFFICE_APPS = {
    'word': 'WINWORD.EXE',
    'excel': 'EXCEL.EXE',
    'powerpoint': 'POWERPNT.EXE',
    'outlook': 'OUTLOOK.EXE',
    'access': 'MSACCESS.EXE',
    'publisher': 'MSPUB.EXE',
    'visio': 'VISIO.EXE',
    'project': 'WINPROJ.EXE',
}

# Variables globales
_accessibility_manager = None
_msoffice_instances = {}

def initialize() -> bool:
    """Initialise l'intégration avec Microsoft Office."""
    global _accessibility_manager, _msoffice_instances
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Vérifier si Wine est installé
        if not is_wine_installed():
            logger.error("Wine n'est pas installé")
            return False
            
        # Trouver les instances de Microsoft Office
        _msoffice_instances = find_msoffice_instances()
        if not _msoffice_instances:
            logger.warning("Aucune application Microsoft Office n'est en cours d'exécution")
            return False
            
        logger.info(f"Intégration Microsoft Office initialisée avec succès pour {len(_msoffice_instances)} applications")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Microsoft Office : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _msoffice_instances
    
    try:
        _msoffice_instances.clear()
        _accessibility_manager = None
        logger.info("Intégration Microsoft Office nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Microsoft Office : {str(e)}")

def is_wine_installed() -> bool:
    """Vérifie si Wine est installé."""
    try:
        result = subprocess.run(['which', 'wine'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'installation de Wine : {str(e)}")
        return False

def find_msoffice_instances() -> Dict[str, Atspi.Accessible]:
    """Trouve les instances de Microsoft Office en cours d'exécution."""
    instances = {}
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            # Vérifier si l'application est une application Microsoft Office
            if is_msoffice_app(app):
                instances[app.get_name()] = app
        return instances
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des applications Microsoft Office : {str(e)}")
        return {}

def is_msoffice_app(app: Atspi.Accessible) -> bool:
    """Vérifie si une application est une application Microsoft Office."""
    try:
        # Vérifier les attributs spécifiques aux applications Microsoft Office
        attrs = app.get_attributes()
        if not attrs:
            return False
            
        # Vérifier le processus
        pid = app.get_process_id()
        if not pid:
            return False
            
        # Lire le fichier /proc/<pid>/cmdline pour vérifier si c'est une app MS Office
        try:
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().lower()
                return any(exe.lower() in cmdline for exe in MSOFFICE_APPS.values())
        except:
            return False
            
    except Exception:
        return False

def get_msoffice_info(app_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'instance de Microsoft Office spécifiée ou toutes les instances."""
    if app_name:
        app = _msoffice_instances.get(app_name)
        if not app:
            return {}
            
        try:
            return {
                'name': app.get_name(),
                'role': app.get_role_name(),
                'version': app.get_attributes().get('version', ''),
                'pid': app.get_process_id(),
                'children': len(app.get_children())
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations pour {app_name} : {str(e)}")
            return {}
    else:
        return {name: get_msoffice_info(name) for name in _msoffice_instances.keys()}

def get_accessibility_tree(app_name: str) -> Dict[str, Any]:
    """Récupère l'arbre d'accessibilité d'une application Microsoft Office."""
    app = _msoffice_instances.get(app_name)
    if not app:
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
        return get_element_info(app)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité pour {app_name} : {str(e)}")
        return {}

def get_focused_element(app_name: str) -> Dict[str, Any]:
    """Récupère l'élément actuellement focalisé dans une application Microsoft Office."""
    app = _msoffice_instances.get(app_name)
    if not app:
        return {}
        
    try:
        focused = Atspi.get_focused()
        if not focused:
            return {}
            
        # Vérifier si l'élément focalisé appartient à l'application
        if not is_child_of(focused, app):
            return {}
            
        return {
            'name': focused.get_name(),
            'role': focused.get_role_name(),
            'description': focused.get_description(),
            'attributes': focused.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé pour {app_name} : {str(e)}")
        return {}

def is_child_of(element: Atspi.Accessible, parent: Atspi.Accessible) -> bool:
    """Vérifie si un élément est un enfant d'un parent donné."""
    try:
        current = element
        while current:
            if current == parent:
                return True
            current = current.get_parent()
        return False
    except Exception:
        return False

def get_current_selection(app_name: str) -> List[Dict[str, Any]]:
    """Récupère la sélection actuelle dans une application Microsoft Office."""
    app = _msoffice_instances.get(app_name)
    if not app:
        return []
        
    try:
        focused = Atspi.get_focused()
        if not focused or not is_child_of(focused, app):
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
        logger.error(f"Erreur lors de la récupération de la sélection pour {app_name} : {str(e)}")
        return []

def get_active_document(app_name: str) -> Dict[str, Any]:
    """Récupère les informations sur le document actif."""
    app = _msoffice_instances.get(app_name)
    if not app:
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
            
        doc = find_document(app)
        if not doc:
            return {}
            
        return {
            'name': doc.get_name(),
            'role': doc.get_role_name(),
            'description': doc.get_description(),
            'attributes': doc.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du document actif pour {app_name} : {str(e)}")
        return {}

def get_document_content(app_name: str) -> str:
    """Récupère le contenu du document actif."""
    doc = get_active_document(app_name)
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
            
        app = _msoffice_instances.get(app_name)
        if not app:
            return ""
            
        return extract_text(app)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du document pour {app_name} : {str(e)}")
        return ""

def execute_action(app_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans une application Microsoft Office."""
    app = _msoffice_instances.get(app_name)
    if not app:
        return False
        
    try:
        if action == 'new_document':
            # Simuler Ctrl+N
            return app.do_action(0)  # Action par défaut pour nouveau document
            
        elif action == 'open_document':
            # Simuler Ctrl+O
            return app.do_action(1)  # Action par défaut pour ouvrir
            
        elif action == 'save_document':
            # Simuler Ctrl+S
            return app.do_action(2)  # Action par défaut pour sauvegarder
            
        elif action == 'print_document':
            # Simuler Ctrl+P
            return app.do_action(3)  # Action par défaut pour imprimer
            
        elif action == 'click':
            element = kwargs.get('element')
            if element and is_child_of(element, app):
                return element.do_action(0)  # Action par défaut (clic)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element and is_child_of(element, app):
                return element.do_action(1)  # Action par défaut (focus)
                
        elif action == 'scroll':
            element = kwargs.get('element')
            direction = kwargs.get('direction', 'down')
            if element and is_child_of(element, app):
                if direction == 'up':
                    return element.do_action(2)  # Action par défaut (scroll up)
                else:
                    return element.do_action(3)  # Action par défaut (scroll down)
                    
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} pour {app_name} : {str(e)}")
        return False 