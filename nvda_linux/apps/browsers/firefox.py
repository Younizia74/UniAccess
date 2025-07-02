#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec Firefox pour NVDA-Linux
=============================================

Gère l'interaction avec Firefox via AT-SPI :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu
- Gestion des formulaires
- Navigation par onglets
- Gestion des raccourcis clavier
"""

import os
import logging
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
from typing import Dict, Any, Optional, List, Tuple

from ...core.config import get
from ...core.accessibility import AccessibilityManager

logger = logging.getLogger(__name__)

# Constantes pour Firefox
FIREFOX_ROLES = {
    "browser": Atspi.Role.FRAME,
    "tab": Atspi.Role.PAGE_TAB,
    "tab_list": Atspi.Role.PAGE_TAB_LIST,
    "toolbar": Atspi.Role.TOOL_BAR,
    "address_bar": Atspi.Role.ENTRY,
    "content": Atspi.Role.DOCUMENT_WEB,
    "link": Atspi.Role.LINK,
    "button": Atspi.Role.PUSH_BUTTON,
    "checkbox": Atspi.Role.CHECK_BOX,
    "combobox": Atspi.Role.COMBO_BOX,
    "edit": Atspi.Role.ENTRY,
    "list": Atspi.Role.LIST,
    "list_item": Atspi.Role.LIST_ITEM,
    "menu": Atspi.Role.MENU,
    "menu_item": Atspi.Role.MENU_ITEM,
    "radio": Atspi.Role.RADIO_BUTTON,
    "slider": Atspi.Role.SLIDER,
    "spinbutton": Atspi.Role.SPIN_BUTTON,
    "statusbar": Atspi.Role.STATUS_BAR
}

# Instance du gestionnaire d'accessibilité
_accessibility_manager: Optional[AccessibilityManager] = None

# Cache de l'instance Firefox
_firefox_instance: Optional[Atspi.Accessible] = None

def initialize() -> bool:
    """Initialise l'intégration avec Firefox"""
    try:
        global _accessibility_manager, _firefox_instance
        
        # Initialise le gestionnaire d'accessibilité
        _accessibility_manager = AccessibilityManager()
        if not _accessibility_manager.initialize():
            logger.error("Impossible d'initialiser le gestionnaire d'accessibilité")
            return False
        
        # Recherche l'instance Firefox
        _firefox_instance = _find_firefox_instance()
        if not _firefox_instance:
            logger.error("Impossible de trouver l'instance Firefox")
            return False
        
        logger.info("Intégration Firefox initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de l'intégration Firefox: {str(e)}")
        return False

def cleanup() -> bool:
    """Nettoie les ressources de l'intégration Firefox"""
    try:
        global _accessibility_manager, _firefox_instance
        
        if _accessibility_manager:
            _accessibility_manager.cleanup()
            _accessibility_manager = None
        
        _firefox_instance = None
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de l'intégration Firefox: {str(e)}")
        return False

def _find_firefox_instance() -> Optional[Atspi.Accessible]:
    """Recherche l'instance Firefox via AT-SPI"""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() == "firefox":
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de Firefox: {str(e)}")
        return None

def get_info() -> Dict[str, Any]:
    """Récupère les informations sur Firefox"""
    try:
        if not _firefox_instance:
            return {}
        
        return {
            "name": _firefox_instance.get_name(),
            "version": _firefox_instance.get_toolkit_name(),
            "pid": _firefox_instance.get_process_id(),
            "role": _firefox_instance.get_role_name(),
            "state": _firefox_instance.get_state().to_string(),
            "children_count": _firefox_instance.get_child_count()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations Firefox: {str(e)}")
        return {}

def get_accessibility_tree() -> Optional[Atspi.Accessible]:
    """Récupère l'arbre d'accessibilité de Firefox"""
    return _firefox_instance

def get_focused_element() -> Optional[Atspi.Accessible]:
    """Récupère l'élément focalisé dans Firefox"""
    try:
        if not _firefox_instance:
            return None
        
        focused = _firefox_instance.get_focused()
        if focused:
            return focused
        
        # Recherche récursive de l'élément focalisé
        def _find_focused(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if element.get_state().contains(Atspi.StateType.FOCUSED):
                return element
            
            for i in range(element.get_child_count()):
                child = element.get_child_at_index(i)
                if child:
                    focused = _find_focused(child)
                    if focused:
                        return focused
            
            return None
        
        return _find_focused(_firefox_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé: {str(e)}")
        return None

def get_selection() -> Optional[str]:
    """Récupère la sélection dans Firefox"""
    try:
        focused = get_focused_element()
        if not focused:
            return None
        
        # Vérifie si l'élément a une sélection
        if focused.get_state().contains(Atspi.StateType.SELECTED):
            return focused.get_text(0, -1)
        
        # Vérifie si l'élément a une sélection de texte
        if hasattr(focused, "get_selection"):
            selection = focused.get_selection(0)
            if selection:
                return selection.get_text(0, -1)
        
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection: {str(e)}")
        return None

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans Firefox"""
    try:
        if not _firefox_instance:
            return False
        
        focused = get_focused_element()
        if not focused:
            return False
        
        # Actions spécifiques à Firefox
        if action == "new_tab":
            # Recherche le bouton "Nouvel onglet"
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["tab_list"]:
                    for j in range(child.get_child_count()):
                        tab = child.get_child_at_index(j)
                        if tab.get_role() == FIREFOX_ROLES["button"] and "nouvel onglet" in tab.get_name().lower():
                            return tab.do_action(0)  # Action click
        
        elif action == "close_tab":
            # Recherche l'onglet actif
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["tab_list"]:
                    for j in range(child.get_child_count()):
                        tab = child.get_child_at_index(j)
                        if tab.get_role() == FIREFOX_ROLES["tab"] and tab.get_state().contains(Atspi.StateType.SELECTED):
                            # Recherche le bouton de fermeture
                            for k in range(tab.get_child_count()):
                                close_button = tab.get_child_at_index(k)
                                if close_button.get_role() == FIREFOX_ROLES["button"] and "fermer" in close_button.get_name().lower():
                                    return close_button.do_action(0)  # Action click
        
        elif action == "next_tab":
            # Recherche la liste des onglets
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["tab_list"]:
                    current_index = -1
                    for j in range(child.get_child_count()):
                        tab = child.get_child_at_index(j)
                        if tab.get_role() == FIREFOX_ROLES["tab"] and tab.get_state().contains(Atspi.StateType.SELECTED):
                            current_index = j
                            break
                    
                    if current_index >= 0 and current_index < child.get_child_count() - 1:
                        next_tab = child.get_child_at_index(current_index + 1)
                        return next_tab.do_action(0)  # Action click
        
        elif action == "previous_tab":
            # Recherche la liste des onglets
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["tab_list"]:
                    current_index = -1
                    for j in range(child.get_child_count()):
                        tab = child.get_child_at_index(j)
                        if tab.get_role() == FIREFOX_ROLES["tab"] and tab.get_state().contains(Atspi.StateType.SELECTED):
                            current_index = j
                            break
                    
                    if current_index > 0:
                        prev_tab = child.get_child_at_index(current_index - 1)
                        return prev_tab.do_action(0)  # Action click
        
        elif action == "reload":
            # Recherche le bouton de rechargement
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["toolbar"]:
                    for j in range(child.get_child_count()):
                        button = child.get_child_at_index(j)
                        if button.get_role() == FIREFOX_ROLES["button"] and "recharger" in button.get_name().lower():
                            return button.do_action(0)  # Action click
        
        elif action == "back":
            # Recherche le bouton retour
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["toolbar"]:
                    for j in range(child.get_child_count()):
                        button = child.get_child_at_index(j)
                        if button.get_role() == FIREFOX_ROLES["button"] and "retour" in button.get_name().lower():
                            return button.do_action(0)  # Action click
        
        elif action == "forward":
            # Recherche le bouton suivant
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["toolbar"]:
                    for j in range(child.get_child_count()):
                        button = child.get_child_at_index(j)
                        if button.get_role() == FIREFOX_ROLES["button"] and "suivant" in button.get_name().lower():
                            return button.do_action(0)  # Action click
        
        elif action == "focus_address_bar":
            # Recherche la barre d'adresse
            for i in range(_firefox_instance.get_child_count()):
                child = _firefox_instance.get_child_at_index(i)
                if child.get_role() == FIREFOX_ROLES["toolbar"]:
                    for j in range(child.get_child_count()):
                        address_bar = child.get_child_at_index(j)
                        if address_bar.get_role() == FIREFOX_ROLES["address_bar"]:
                            return address_bar.do_action(0)  # Action focus
        
        # Actions génériques
        elif action == "click":
            return focused.do_action(0)  # Action click
        
        elif action == "press":
            return focused.do_action(1)  # Action press
        
        elif action == "release":
            return focused.do_action(2)  # Action release
        
        elif action == "focus":
            return focused.do_action(0)  # Action focus
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action}: {str(e)}")
        return False 