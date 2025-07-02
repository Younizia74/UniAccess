#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module principal pour l'intégration avec Android
Gère l'interaction avec les applications Android via l'Accessibility Service, incluant :
- Navigation dans l'arbre d'accessibilité
- Gestion des événements d'accessibilité
- Gestion des applications
- Gestion des notifications
- Gestion des raccourcis clavier
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Tuple, Callable
from enum import Enum
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

# Configuration du logger
logger = logging.getLogger(__name__)

# Types d'événements d'accessibilité
class AccessibilityEventType(Enum):
    VIEW_CLICKED = "VIEW_CLICKED"
    VIEW_LONG_CLICKED = "VIEW_LONG_CLICKED"
    VIEW_SELECTED = "VIEW_SELECTED"
    VIEW_FOCUSED = "VIEW_FOCUSED"
    VIEW_TEXT_CHANGED = "VIEW_TEXT_CHANGED"
    WINDOW_STATE_CHANGED = "WINDOW_STATE_CHANGED"
    WINDOW_CONTENT_CHANGED = "WINDOW_CONTENT_CHANGED"
    NOTIFICATION_STATE_CHANGED = "NOTIFICATION_STATE_CHANGED"
    VIEW_SCROLLED = "VIEW_SCROLLED"
    VIEW_TEXT_SELECTION_CHANGED = "VIEW_TEXT_SELECTION_CHANGED"
    ANNOUNCEMENT = "ANNOUNCEMENT"
    GESTURE_DETECTION_START = "GESTURE_DETECTION_START"
    GESTURE_DETECTION_END = "GESTURE_DETECTION_END"
    TOUCH_INTERACTION_START = "TOUCH_INTERACTION_START"
    TOUCH_INTERACTION_END = "TOUCH_INTERACTION_END"
    TOUCH_EXPLORATION_GESTURE_START = "TOUCH_EXPLORATION_GESTURE_START"
    TOUCH_EXPLORATION_GESTURE_END = "TOUCH_EXPLORATION_GESTURE_END"
    WINDOWS_CHANGED = "WINDOWS_CHANGED"
    VIEW_CONTEXT_CLICKED = "VIEW_CONTEXT_CLICKED"
    ASSIST_READING_CONTEXT = "ASSIST_READING_CONTEXT"

# Types de nœuds d'accessibilité
class AccessibilityNodeType(Enum):
    VIEW = "VIEW"
    BUTTON = "BUTTON"
    CHECK_BOX = "CHECK_BOX"
    EDIT_TEXT = "EDIT_TEXT"
    IMAGE = "IMAGE"
    IMAGE_BUTTON = "IMAGE_BUTTON"
    LIST_ITEM = "LIST_ITEM"
    MENU = "MENU"
    MENU_ITEM = "MENU_ITEM"
    PROGRESS_BAR = "PROGRESS_BAR"
    RADIO_BUTTON = "RADIO_BUTTON"
    SCROLL_VIEW = "SCROLL_VIEW"
    SEEK_BAR = "SEEK_BAR"
    SPINNER = "SPINNER"
    SWITCH = "SWITCH"
    TAB = "TAB"
    TAB_ITEM = "TAB_ITEM"
    TEXT_VIEW = "TEXT_VIEW"
    TOOLBAR = "TOOLBAR"
    WEB_VIEW = "WEB_VIEW"

# Variables globales
_accessibility_service = None
_event_handlers = {}
_node_cache = {}
_app_cache = {}
_notification_cache = {}
_initialized = False

def initialize() -> bool:
    """Initialise le service d'accessibilité Android."""
    global _accessibility_service, _initialized
    
    try:
        # Vérifier si le service d'accessibilité est disponible
        if not Gio.Application.get_default():
            logger.error("Le service d'accessibilité n'est pas disponible")
            return False
            
        # Initialiser le service
        _accessibility_service = Gio.Application.get_default()
        
        # Enregistrer les gestionnaires d'événements par défaut
        register_default_event_handlers()
        
        _initialized = True
        logger.info("Service d'accessibilité Android initialisé avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du service d'accessibilité : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par le service d'accessibilité."""
    global _accessibility_service, _event_handlers, _node_cache, _app_cache, _notification_cache, _initialized
    
    try:
        # Désenregistrer tous les gestionnaires d'événements
        _event_handlers.clear()
        
        # Vider les caches
        _node_cache.clear()
        _app_cache.clear()
        _notification_cache.clear()
        
        # Arrêter le service
        if _accessibility_service:
            _accessibility_service.quit()
            _accessibility_service = None
            
        _initialized = False
        logger.info("Service d'accessibilité Android nettoyé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du service d'accessibilité : {str(e)}")

def register_default_event_handlers() -> None:
    """Enregistre les gestionnaires d'événements par défaut."""
    try:
        # Gestionnaire pour les clics
        register_event_handler(
            AccessibilityEventType.VIEW_CLICKED,
            lambda event: handle_view_clicked(event)
        )
        
        # Gestionnaire pour les changements de fenêtre
        register_event_handler(
            AccessibilityEventType.WINDOW_STATE_CHANGED,
            lambda event: handle_window_state_changed(event)
        )
        
        # Gestionnaire pour les changements de contenu
        register_event_handler(
            AccessibilityEventType.WINDOW_CONTENT_CHANGED,
            lambda event: handle_window_content_changed(event)
        )
        
        # Gestionnaire pour les notifications
        register_event_handler(
            AccessibilityEventType.NOTIFICATION_STATE_CHANGED,
            lambda event: handle_notification_state_changed(event)
        )
        
        logger.info("Gestionnaires d'événements par défaut enregistrés")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des gestionnaires d'événements : {str(e)}")

def register_event_handler(event_type: AccessibilityEventType, handler: Callable) -> None:
    """Enregistre un gestionnaire d'événements."""
    try:
        if event_type not in _event_handlers:
            _event_handlers[event_type] = []
        _event_handlers[event_type].append(handler)
        logger.debug(f"Gestionnaire enregistré pour l'événement {event_type.value}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du gestionnaire d'événements : {str(e)}")

def unregister_event_handler(event_type: AccessibilityEventType, handler: Callable) -> None:
    """Désenregistre un gestionnaire d'événements."""
    try:
        if event_type in _event_handlers and handler in _event_handlers[event_type]:
            _event_handlers[event_type].remove(handler)
            logger.debug(f"Gestionnaire désenregistré pour l'événement {event_type.value}")
    except Exception as e:
        logger.error(f"Erreur lors du désenregistrement du gestionnaire d'événements : {str(e)}")

def handle_view_clicked(event: Dict[str, Any]) -> None:
    """Gère les événements de clic sur une vue."""
    try:
        node = event.get('node', {})
        logger.debug(f"Vue cliquée : {node.get('text', '')}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du clic : {str(e)}")

def handle_window_state_changed(event: Dict[str, Any]) -> None:
    """Gère les changements d'état de fenêtre."""
    try:
        window = event.get('window', {})
        logger.debug(f"État de fenêtre changé : {window.get('title', '')}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du changement d'état de fenêtre : {str(e)}")

def handle_window_content_changed(event: Dict[str, Any]) -> None:
    """Gère les changements de contenu de fenêtre."""
    try:
        window = event.get('window', {})
        logger.debug(f"Contenu de fenêtre changé : {window.get('title', '')}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du changement de contenu de fenêtre : {str(e)}")

def handle_notification_state_changed(event: Dict[str, Any]) -> None:
    """Gère les changements d'état des notifications."""
    try:
        notification = event.get('notification', {})
        logger.debug(f"État de notification changé : {notification.get('title', '')}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du changement d'état de notification : {str(e)}")

def get_current_app() -> Dict[str, Any]:
    """Récupère les informations sur l'application en cours."""
    try:
        if not _accessibility_service:
            return {}
            
        # Récupérer l'application active
        app = _accessibility_service.get_active_window()
        if not app:
            return {}
            
        return {
            'package': app.get_package_name(),
            'activity': app.get_activity_name(),
            'title': app.get_title(),
            'window_id': app.get_window_id(),
            'is_focused': app.is_focused(),
            'is_active': app.is_active()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'application en cours : {str(e)}")
        return {}

def get_current_window() -> Dict[str, Any]:
    """Récupère les informations sur la fenêtre en cours."""
    try:
        if not _accessibility_service:
            return {}
            
        # Récupérer la fenêtre active
        window = _accessibility_service.get_active_window()
        if not window:
            return {}
            
        return {
            'id': window.get_window_id(),
            'title': window.get_title(),
            'bounds': window.get_bounds(),
            'is_focused': window.is_focused(),
            'is_active': window.is_active(),
            'is_fullscreen': window.is_fullscreen(),
            'is_modal': window.is_modal()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la fenêtre en cours : {str(e)}")
        return {}

def get_current_node() -> Dict[str, Any]:
    """Récupère les informations sur le nœud en cours."""
    try:
        if not _accessibility_service:
            return {}
            
        # Récupérer le nœud actif
        node = _accessibility_service.get_focused_node()
        if not node:
            return {}
            
        return {
            'id': node.get_node_id(),
            'text': node.get_text(),
            'description': node.get_description(),
            'type': node.get_type(),
            'bounds': node.get_bounds(),
            'is_clickable': node.is_clickable(),
            'is_focused': node.is_focused(),
            'is_selected': node.is_selected(),
            'is_enabled': node.is_enabled(),
            'is_editable': node.is_editable(),
            'is_password': node.is_password(),
            'is_checkable': node.is_checkable(),
            'is_checked': node.is_checked(),
            'is_scrollable': node.is_scrollable(),
            'is_long_clickable': node.is_long_clickable(),
            'is_context_clickable': node.is_context_clickable()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du nœud en cours : {str(e)}")
        return {}

def get_notifications() -> List[Dict[str, Any]]:
    """Récupère la liste des notifications actives."""
    try:
        if not _accessibility_service:
            return []
            
        # Récupérer les notifications
        notifications = _accessibility_service.get_notifications()
        if not notifications:
            return []
            
        return [{
            'id': notification.get_id(),
            'package': notification.get_package(),
            'title': notification.get_title(),
            'text': notification.get_text(),
            'subtext': notification.get_subtext(),
            'ticker': notification.get_ticker(),
            'time': notification.get_time(),
            'is_ongoing': notification.is_ongoing(),
            'is_clearable': notification.is_clearable(),
            'is_removed': notification.is_removed()
        } for notification in notifications]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des notifications : {str(e)}")
        return []

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action d'accessibilité."""
    try:
        if not _accessibility_service:
            return False
            
        if action == 'click':
            # Cliquer sur un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('click')
                
        elif action == 'long_click':
            # Cliquer longuement sur un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('long_click')
                
        elif action == 'focus':
            # Donner le focus à un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('focus')
                
        elif action == 'clear_focus':
            # Enlever le focus d'un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('clear_focus')
                
        elif action == 'select':
            # Sélectionner un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('select')
                
        elif action == 'clear_selection':
            # Désélectionner un nœud
            node = kwargs.get('node')
            if node:
                return node.perform_action('clear_selection')
                
        elif action == 'scroll_forward':
            # Faire défiler vers l'avant
            node = kwargs.get('node')
            if node:
                return node.perform_action('scroll_forward')
                
        elif action == 'scroll_backward':
            # Faire défiler vers l'arrière
            node = kwargs.get('node')
            if node:
                return node.perform_action('scroll_backward')
                
        elif action == 'copy':
            # Copier le texte
            node = kwargs.get('node')
            if node:
                return node.perform_action('copy')
                
        elif action == 'paste':
            # Coller le texte
            node = kwargs.get('node')
            if node:
                return node.perform_action('paste')
                
        elif action == 'cut':
            # Couper le texte
            node = kwargs.get('node')
            if node:
                return node.perform_action('cut')
                
        elif action == 'set_selection':
            # Définir la sélection
            node = kwargs.get('node')
            start = kwargs.get('start', 0)
            end = kwargs.get('end', 0)
            if node:
                return node.perform_action('set_selection', start, end)
                
        elif action == 'set_text':
            # Définir le texte
            node = kwargs.get('node')
            text = kwargs.get('text', '')
            if node:
                return node.perform_action('set_text', text)
                
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} : {str(e)}")
        return False 