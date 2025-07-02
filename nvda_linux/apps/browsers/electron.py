#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour les applications Electron
Gère l'interaction avec les applications Electron via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu
- Gestion des fenêtres
- Gestion des contrôles
- Gestion des raccourcis clavier
"""

import os
import logging
import subprocess
import json
from typing import Dict, Any, Optional, List, Tuple
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

# Rôles spécifiques aux applications Electron
ELECTRON_ROLES = {
    'application': Atspi.Role.FRAME,
    'window': Atspi.Role.FRAME,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
    'link': Atspi.Role.LINK,
    'heading': Atspi.Role.HEADING,
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
    'canvas': Atspi.Role.CANVAS,
    'image': Atspi.Role.IMAGE,
    'form': Atspi.Role.FORM,
    'form_field': Atspi.Role.ENTRY,
    'web_view': Atspi.Role.DOCUMENT_WEB,
    'web_area': Atspi.Role.DOCUMENT_WEB,
}

# Variables globales
_accessibility_manager = None
_electron_instances = {}

def initialize() -> bool:
    """Initialise l'intégration avec les applications Electron."""
    global _accessibility_manager, _electron_instances
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver les instances d'applications Electron
        _electron_instances = find_electron_instances()
        if not _electron_instances:
            logger.warning("Aucune application Electron n'est en cours d'exécution")
            return False
            
        logger.info(f"Intégration Electron initialisée avec succès pour {len(_electron_instances)} applications")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation d'Electron : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _electron_instances
    
    try:
        _electron_instances.clear()
        _accessibility_manager = None
        logger.info("Intégration Electron nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage d'Electron : {str(e)}")

def find_electron_instances() -> Dict[str, Atspi.Accessible]:
    """Trouve les instances d'applications Electron en cours d'exécution."""
    instances = {}
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            # Vérifier si l'application est une application Electron
            if is_electron_instance(app):
                instances[app.get_name()] = app
        return instances
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des applications Electron : {str(e)}")
        return {}

def is_electron_instance(app: Atspi.Accessible) -> bool:
    """Vérifie si une application est une instance d'Electron."""
    try:
        # Vérifier le processus
        pid = app.get_process_id()
        if not pid:
            return False
            
        # Lire le fichier /proc/<pid>/cmdline pour vérifier
        try:
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().lower()
                # Vérifier les indicateurs Electron
                electron_indicators = [
                    'electron', 'node', 'chromium', 'chrome',
                    '--type=renderer', '--type=browser'
                ]
                return any(ind in cmdline for ind in electron_indicators)
        except:
            return False
            
    except Exception:
        return False

def get_electron_info(instance_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'instance d'application Electron spécifiée ou toutes les instances."""
    if instance_name:
        instance = _electron_instances.get(instance_name)
        if not instance:
            return {}
            
        try:
            # Récupérer les informations de base
            info = {
                'name': instance.get_name(),
                'role': instance.get_role_name(),
                'version': instance.get_attributes().get('version', ''),
                'pid': instance.get_process_id(),
                'children': len(instance.get_children())
            }
            
            # Ajouter les informations sur les fenêtres
            windows = get_windows(instance)
            info['windows'] = [{
                'title': window.get_name(),
                'role': window.get_role_name(),
                'is_active': window.get_state_set().contains(Atspi.StateType.FOCUSED)
            } for window in windows]
            
            return info
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations pour {instance_name} : {str(e)}")
            return {}
    else:
        return {name: get_electron_info(name) for name in _electron_instances.keys()}

def get_windows(instance: Atspi.Accessible) -> List[Atspi.Accessible]:
    """Récupère la liste des fenêtres d'une instance d'application Electron."""
    windows = []
    try:
        def find_windows(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.FRAME:
                windows.append(element)
            for child in element.get_children():
                find_windows(child)
                
        find_windows(instance)
        return windows
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fenêtres : {str(e)}")
        return []

def get_accessibility_tree(instance_name: str) -> Dict[str, Any]:
    """Récupère l'arbre d'accessibilité d'une instance d'application Electron."""
    instance = _electron_instances.get(instance_name)
    if not instance:
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
        return get_element_info(instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité pour {instance_name} : {str(e)}")
        return {}

def get_focused_element(instance_name: str) -> Dict[str, Any]:
    """Récupère l'élément actuellement focalisé dans une instance d'application Electron."""
    instance = _electron_instances.get(instance_name)
    if not instance:
        return {}
        
    try:
        focused = Atspi.get_focused()
        if not focused:
            return {}
            
        # Vérifier si l'élément focalisé appartient à l'instance
        if not is_child_of(focused, instance):
            return {}
            
        return {
            'name': focused.get_name(),
            'role': focused.get_role_name(),
            'description': focused.get_description(),
            'attributes': focused.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé pour {instance_name} : {str(e)}")
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

def get_current_selection(instance_name: str) -> List[Dict[str, Any]]:
    """Récupère la sélection actuelle dans une instance d'application Electron."""
    instance = _electron_instances.get(instance_name)
    if not instance:
        return []
        
    try:
        focused = Atspi.get_focused()
        if not focused or not is_child_of(focused, instance):
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
        logger.error(f"Erreur lors de la récupération de la sélection pour {instance_name} : {str(e)}")
        return []

def execute_action(instance_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans une instance d'application Electron."""
    instance = _electron_instances.get(instance_name)
    if not instance:
        return False
        
    try:
        if action == 'new_window':
            # Trouver le bouton nouvelle fenêtre
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.PUSH_BUTTON and 'nouvelle fenêtre' in element.get_name().lower():
                    return element.do_action(0)
                    
        elif action == 'close_window':
            # Trouver la fenêtre active et son bouton de fermeture
            focused = Atspi.get_focused()
            if focused and is_child_of(focused, instance):
                window = focused
                while window and window.get_role() != Atspi.Role.FRAME:
                    window = window.get_parent()
                if window:
                    for element in window.get_children():
                        if element.get_role() == Atspi.Role.PUSH_BUTTON and 'fermer' in element.get_name().lower():
                            return element.do_action(0)
                            
        elif action == 'next_window':
            # Trouver la liste des fenêtres et naviguer
            windows = get_windows(instance)
            if windows:
                focused = Atspi.get_focused()
                if focused:
                    current_window = focused
                    while current_window and current_window.get_role() != Atspi.Role.FRAME:
                        current_window = current_window.get_parent()
                    if current_window:
                        current_index = windows.index(current_window)
                        if current_index < len(windows) - 1:
                            return windows[current_index + 1].do_action(0)
                            
        elif action == 'previous_window':
            # Trouver la liste des fenêtres et naviguer
            windows = get_windows(instance)
            if windows:
                focused = Atspi.get_focused()
                if focused:
                    current_window = focused
                    while current_window and current_window.get_role() != Atspi.Role.FRAME:
                        current_window = current_window.get_parent()
                    if current_window:
                        current_index = windows.index(current_window)
                        if current_index > 0:
                            return windows[current_index - 1].do_action(0)
                            
        elif action == 'click':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        elif action == 'menu':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        elif action == 'context_menu':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} pour {instance_name} : {str(e)}")
        return False 