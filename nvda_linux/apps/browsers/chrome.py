#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour Chrome
Gère l'interaction avec Chrome via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu
- Gestion des onglets
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

# Rôles spécifiques à Chrome
CHROME_ROLES = {
    'browser': Atspi.Role.FRAME,
    'tab': Atspi.Role.PAGE_TAB,
    'toolbar': Atspi.Role.TOOL_BAR,
    'address_bar': Atspi.Role.ENTRY,
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
}

# Variables globales
_accessibility_manager = None
_chrome_instances = {}

def initialize() -> bool:
    """Initialise l'intégration avec Chrome."""
    global _accessibility_manager, _chrome_instances
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver les instances de Chrome
        _chrome_instances = find_chrome_instances()
        if not _chrome_instances:
            logger.warning("Aucune instance de Chrome n'est en cours d'exécution")
            return False
            
        logger.info(f"Intégration Chrome initialisée avec succès pour {len(_chrome_instances)} instances")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Chrome : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _chrome_instances
    
    try:
        _chrome_instances.clear()
        _accessibility_manager = None
        logger.info("Intégration Chrome nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Chrome : {str(e)}")

def find_chrome_instances() -> Dict[str, Atspi.Accessible]:
    """Trouve les instances de Chrome en cours d'exécution."""
    instances = {}
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            # Vérifier si l'application est Chrome
            if is_chrome_instance(app):
                instances[app.get_name()] = app
        return instances
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des instances de Chrome : {str(e)}")
        return {}

def is_chrome_instance(app: Atspi.Accessible) -> bool:
    """Vérifie si une application est une instance de Chrome."""
    try:
        # Vérifier le nom et le rôle
        if app.get_name().lower() not in ['google chrome', 'chrome']:
            return False
            
        # Vérifier le processus
        pid = app.get_process_id()
        if not pid:
            return False
            
        # Lire le fichier /proc/<pid>/cmdline pour vérifier
        try:
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().lower()
                return 'chrome' in cmdline
        except:
            return False
            
    except Exception:
        return False

def get_chrome_info(instance_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'instance de Chrome spécifiée ou toutes les instances."""
    if instance_name:
        instance = _chrome_instances.get(instance_name)
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
            
            # Ajouter les informations sur les onglets
            tabs = get_tabs(instance)
            info['tabs'] = [{
                'title': tab.get_name(),
                'url': tab.get_attributes().get('url', ''),
                'is_active': tab.get_state_set().contains(Atspi.StateType.FOCUSED)
            } for tab in tabs]
            
            return info
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations pour {instance_name} : {str(e)}")
            return {}
    else:
        return {name: get_chrome_info(name) for name in _chrome_instances.keys()}

def get_tabs(instance: Atspi.Accessible) -> List[Atspi.Accessible]:
    """Récupère la liste des onglets d'une instance de Chrome."""
    tabs = []
    try:
        def find_tabs(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.PAGE_TAB:
                tabs.append(element)
            for child in element.get_children():
                find_tabs(child)
                
        find_tabs(instance)
        return tabs
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des onglets : {str(e)}")
        return []

def get_accessibility_tree(instance_name: str) -> Dict[str, Any]:
    """Récupère l'arbre d'accessibilité d'une instance de Chrome."""
    instance = _chrome_instances.get(instance_name)
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
    """Récupère l'élément actuellement focalisé dans une instance de Chrome."""
    instance = _chrome_instances.get(instance_name)
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
    """Récupère la sélection actuelle dans une instance de Chrome."""
    instance = _chrome_instances.get(instance_name)
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
    """Exécute une action dans une instance de Chrome."""
    instance = _chrome_instances.get(instance_name)
    if not instance:
        return False
        
    try:
        if action == 'new_tab':
            # Trouver le bouton nouveau onglet
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.PUSH_BUTTON and 'nouvel onglet' in element.get_name().lower():
                    return element.do_action(0)
                    
        elif action == 'close_tab':
            # Trouver l'onglet actif et son bouton de fermeture
            focused = Atspi.get_focused()
            if focused and is_child_of(focused, instance):
                tab = focused
                while tab and tab.get_role() != Atspi.Role.PAGE_TAB:
                    tab = tab.get_parent()
                if tab:
                    for element in tab.get_children():
                        if element.get_role() == Atspi.Role.PUSH_BUTTON and 'fermer' in element.get_name().lower():
                            return element.do_action(0)
                            
        elif action == 'next_tab':
            # Trouver la barre d'onglets et naviguer
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.PAGE_TAB_LIST:
                    focused = Atspi.get_focused()
                    if focused and is_child_of(focused, element):
                        current_index = element.get_children().index(focused)
                        if current_index < len(element.get_children()) - 1:
                            return element.get_children()[current_index + 1].do_action(0)
                            
        elif action == 'previous_tab':
            # Trouver la barre d'onglets et naviguer
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.PAGE_TAB_LIST:
                    focused = Atspi.get_focused()
                    if focused and is_child_of(focused, element):
                        current_index = element.get_children().index(focused)
                        if current_index > 0:
                            return element.get_children()[current_index - 1].do_action(0)
                            
        elif action == 'reload':
            # Trouver le bouton de rechargement
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.PUSH_BUTTON and 'recharger' in element.get_name().lower():
                    return element.do_action(0)
                    
        elif action == 'focus_address_bar':
            # Trouver la barre d'adresse
            for element in instance.get_children():
                if element.get_role() == Atspi.Role.ENTRY and 'adresse' in element.get_name().lower():
                    return element.do_action(0)
                    
        elif action == 'click':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element and is_child_of(element, instance):
                return element.do_action(0)
                
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} pour {instance_name} : {str(e)}")
        return False 