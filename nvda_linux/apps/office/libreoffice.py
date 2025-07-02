#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration avec LibreOffice pour NVDA-Linux
================================================

Gère l'interaction avec LibreOffice via AT-SPI :
- Navigation dans l'arbre d'accessibilité
- Lecture du contenu
- Gestion des documents
- Gestion des formulaires
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

# Constantes pour LibreOffice
LIBREOFFICE_ROLES = {
    "application": Atspi.Role.APPLICATION,
    "document": Atspi.Role.DOCUMENT_FRAME,
    "toolbar": Atspi.Role.TOOL_BAR,
    "menu": Atspi.Role.MENU,
    "menu_item": Atspi.Role.MENU_ITEM,
    "button": Atspi.Role.PUSH_BUTTON,
    "edit": Atspi.Role.ENTRY,
    "combo_box": Atspi.Role.COMBO_BOX,
    "list": Atspi.Role.LIST,
    "list_item": Atspi.Role.LIST_ITEM,
    "table": Atspi.Role.TABLE,
    "table_cell": Atspi.Role.TABLE_CELL,
    "paragraph": Atspi.Role.PARAGRAPH,
    "text": Atspi.Role.TEXT,
    "link": Atspi.Role.LINK,
    "checkbox": Atspi.Role.CHECK_BOX,
    "radio": Atspi.Role.RADIO_BUTTON,
    "slider": Atspi.Role.SLIDER,
    "spinbutton": Atspi.Role.SPIN_BUTTON,
    "statusbar": Atspi.Role.STATUS_BAR
}

# Instance du gestionnaire d'accessibilité
_accessibility_manager: Optional[AccessibilityManager] = None

# Cache de l'instance LibreOffice
_libreoffice_instance: Optional[Atspi.Accessible] = None

# Cache du document actif
_active_document: Optional[Atspi.Accessible] = None

def initialize() -> bool:
    """Initialise l'intégration avec LibreOffice"""
    try:
        global _accessibility_manager, _libreoffice_instance
        
        # Initialise le gestionnaire d'accessibilité
        _accessibility_manager = AccessibilityManager()
        if not _accessibility_manager.initialize():
            logger.error("Impossible d'initialiser le gestionnaire d'accessibilité")
            return False
        
        # Recherche l'instance LibreOffice
        _libreoffice_instance = _find_libreoffice_instance()
        if not _libreoffice_instance:
            logger.error("Impossible de trouver l'instance LibreOffice")
            return False
        
        # Recherche le document actif
        _update_active_document()
        
        logger.info("Intégration LibreOffice initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de l'intégration LibreOffice: {str(e)}")
        return False

def cleanup() -> bool:
    """Nettoie les ressources de l'intégration LibreOffice"""
    try:
        global _accessibility_manager, _libreoffice_instance, _active_document
        
        if _accessibility_manager:
            _accessibility_manager.cleanup()
            _accessibility_manager = None
        
        _libreoffice_instance = None
        _active_document = None
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de l'intégration LibreOffice: {str(e)}")
        return False

def _find_libreoffice_instance() -> Optional[Atspi.Accessible]:
    """Recherche l'instance LibreOffice via AT-SPI"""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if "libreoffice" in app.get_name().lower():
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de LibreOffice: {str(e)}")
        return None

def _update_active_document() -> bool:
    """Met à jour le document actif"""
    try:
        global _active_document
        
        if not _libreoffice_instance:
            return False
        
        # Recherche le document actif
        for i in range(_libreoffice_instance.get_child_count()):
            child = _libreoffice_instance.get_child_at_index(i)
            if child.get_role() == LIBREOFFICE_ROLES["document"]:
                _active_document = child
                return True
        
        _active_document = None
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du document actif: {str(e)}")
        return False

def get_info() -> Dict[str, Any]:
    """Récupère les informations sur LibreOffice"""
    try:
        if not _libreoffice_instance:
            return {}
        
        return {
            "name": _libreoffice_instance.get_name(),
            "version": _libreoffice_instance.get_toolkit_name(),
            "pid": _libreoffice_instance.get_process_id(),
            "role": _libreoffice_instance.get_role_name(),
            "state": _libreoffice_instance.get_state().to_string(),
            "children_count": _libreoffice_instance.get_child_count(),
            "has_active_document": _active_document is not None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations LibreOffice: {str(e)}")
        return {}

def get_accessibility_tree() -> Optional[Atspi.Accessible]:
    """Récupère l'arbre d'accessibilité de LibreOffice"""
    return _libreoffice_instance

def get_focused_element() -> Optional[Atspi.Accessible]:
    """Récupère l'élément focalisé dans LibreOffice"""
    try:
        if not _libreoffice_instance:
            return None
        
        focused = _libreoffice_instance.get_focused()
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
        
        return _find_focused(_libreoffice_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé: {str(e)}")
        return None

def get_selection() -> Optional[str]:
    """Récupère la sélection dans LibreOffice"""
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
    """Exécute une action dans LibreOffice"""
    try:
        if not _libreoffice_instance:
            return False
        
        focused = get_focused_element()
        if not focused:
            return False
        
        # Actions spécifiques à LibreOffice
        if action == "new_document":
            # Recherche le menu Fichier > Nouveau
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "fichier" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "nouveau" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "open_document":
            # Recherche le menu Fichier > Ouvrir
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "fichier" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "ouvrir" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "save_document":
            # Recherche le menu Fichier > Enregistrer
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "fichier" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "enregistrer" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "print_document":
            # Recherche le menu Fichier > Imprimer
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "fichier" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "imprimer" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
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

def get_document_info() -> Optional[Dict[str, Any]]:
    """Récupère les informations sur le document actif"""
    try:
        if not _active_document:
            return None
        
        return {
            "name": _active_document.get_name(),
            "role": _active_document.get_role_name(),
            "state": _active_document.get_state().to_string(),
            "children_count": _active_document.get_child_count(),
            "has_focus": _active_document.get_state().contains(Atspi.StateType.FOCUSED)
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations du document: {str(e)}")
        return None

def get_document_content() -> Optional[str]:
    """Récupère le contenu du document actif"""
    try:
        if not _active_document:
            return None
        
        # Recherche récursive du contenu textuel
        def _get_text_content(element: Atspi.Accessible) -> str:
            text = ""
            
            # Récupère le texte de l'élément
            if element.get_role() in [LIBREOFFICE_ROLES["text"], LIBREOFFICE_ROLES["paragraph"]]:
                text += element.get_text(0, -1) + "\n"
            
            # Récupère le texte des enfants
            for i in range(element.get_child_count()):
                child = element.get_child_at_index(i)
                if child:
                    text += _get_text_content(child)
            
            return text
        
        return _get_text_content(_active_document)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du document: {str(e)}")
        return None

def get_document_selection() -> Optional[str]:
    """Récupère la sélection dans le document actif"""
    try:
        if not _active_document:
            return None
        
        # Recherche récursive de la sélection
        def _find_selection(element: Atspi.Accessible) -> Optional[str]:
            # Vérifie si l'élément a une sélection
            if element.get_state().contains(Atspi.StateType.SELECTED):
                return element.get_text(0, -1)
            
            # Vérifie si l'élément a une sélection de texte
            if hasattr(element, "get_selection"):
                selection = element.get_selection(0)
                if selection:
                    return selection.get_text(0, -1)
            
            # Recherche dans les enfants
            for i in range(element.get_child_count()):
                child = element.get_child_at_index(i)
                if child:
                    selection = _find_selection(child)
                    if selection:
                        return selection
            
            return None
        
        return _find_selection(_active_document)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection du document: {str(e)}")
        return None

def execute_document_action(action: str, **kwargs) -> bool:
    """Exécute une action sur le document actif"""
    try:
        if not _active_document:
            return False
        
        # Actions spécifiques au document
        if action == "select_all":
            # Recherche le menu Édition > Tout sélectionner
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "tout sélectionner" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "copy":
            # Recherche le menu Édition > Copier
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "copier" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "cut":
            # Recherche le menu Édition > Couper
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "couper" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "paste":
            # Recherche le menu Édition > Coller
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "coller" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "undo":
            # Recherche le menu Édition > Annuler
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "annuler" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        elif action == "redo":
            # Recherche le menu Édition > Rétablir
            for i in range(_libreoffice_instance.get_child_count()):
                child = _libreoffice_instance.get_child_at_index(i)
                if child.get_role() == LIBREOFFICE_ROLES["menu"] and "édition" in child.get_name().lower():
                    for j in range(child.get_child_count()):
                        menu_item = child.get_child_at_index(j)
                        if menu_item.get_role() == LIBREOFFICE_ROLES["menu_item"] and "rétablir" in menu_item.get_name().lower():
                            return menu_item.do_action(0)  # Action click
        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} sur le document: {str(e)}")
        return False 