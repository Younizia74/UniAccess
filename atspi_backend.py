#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'accessibilité AT-SPI pour NVDA-Linux
Utilise pyatspi pour interagir avec l'accessibilité Linux
"""

import os
import logging
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi
from typing import Optional, List, Dict, Any, Callable
import config

logger = logging.getLogger(__name__)

class AccessibilityNode:
    """Représente un nœud accessible dans l'arbre d'accessibilité"""
    
    def __init__(self, accessible: Atspi.Accessible):
        self.accessible = accessible
        self.role = accessible.get_role_name()
        self.name = accessible.get_name()
        self.description = accessible.get_description()
        self.states = accessible.get_state_set()
        self.children = []
        self.parent = None
    
    def get_text(self) -> str:
        """Récupère le texte du nœud"""
        try:
            if self.accessible.get_text():
                return self.accessible.get_text().get_text(0, -1)
        except Exception:
            pass
        return ""
    
    def is_focused(self) -> bool:
        """Vérifie si le nœud a le focus"""
        return self.states.contains(Atspi.StateType.FOCUSED)
    
    def is_visible(self) -> bool:
        """Vérifie si le nœud est visible"""
        return self.states.contains(Atspi.StateType.VISIBLE)
    
    def is_enabled(self) -> bool:
        """Vérifie si le nœud est activé"""
        return not self.states.contains(Atspi.StateType.SENSITIVE)
    
    def get_actions(self) -> List[str]:
        """Récupère les actions disponibles"""
        try:
            return [action.get_name() for action in self.accessible.get_action_iface().get_actions()]
        except Exception:
            return []
    
    def perform_action(self, action_name: str) -> bool:
        """Exécute une action"""
        try:
            actions = self.accessible.get_action_iface().get_actions()
            for i, action in enumerate(actions):
                if action.get_name() == action_name:
                    self.accessible.get_action_iface().do_action(i)
                    return True
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'action {action_name}: {str(e)}")
        return False

class AccessibilityManager:
    """Gère l'accessibilité du système"""
    
    def __init__(self):
        self.initialized = False
        self.root = None
        self.focused_node = None
        self.event_listeners = {}
        self.braille_display = None
    
    def initialize(self) -> bool:
        """Initialise le gestionnaire d'accessibilité"""
        try:
            # Initialise AT-SPI
            Atspi.init()
            
            # Récupère le bureau
            self.root = AccessibilityNode(Atspi.get_desktop(0))
            
            # Initialise le braille si nécessaire
            if config.get_config('braille', 'enabled', False):
                self.initialize_braille()
            
            self.initialized = True
            logger.info("Gestionnaire d'accessibilité initialisé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du gestionnaire d'accessibilité: {str(e)}")
            return False
    
    def initialize_braille(self) -> bool:
        """Initialise le support braille"""
        try:
            # Ici, on initialiserait le support braille
            # Pour l'instant, c'est une simulation
            self.braille_display = True
            logger.info("Support braille initialisé")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du support braille: {str(e)}")
            return False
    
    def get_focused_node(self) -> Optional[AccessibilityNode]:
        """Récupère le nœud qui a le focus"""
        try:
            focused = Atspi.get_focused()
            if focused:
                return AccessibilityNode(focused)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du nœud focalisé: {str(e)}")
        return None
    
    def get_node_at_point(self, x: int, y: int) -> Optional[AccessibilityNode]:
        """Récupère le nœud à la position spécifiée"""
        try:
            accessible = Atspi.get_desktop(0).get_accessible_at_point(x, y, Atspi.CoordType.SCREEN)
            if accessible:
                return AccessibilityNode(accessible)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du nœud à la position ({x}, {y}): {str(e)}")
        return None
    
    def get_application_list(self) -> List[Dict[str, Any]]:
        """Récupère la liste des applications accessibles"""
        try:
            apps = []
            for i in range(Atspi.get_desktop_count()):
                desktop = Atspi.get_desktop(i)
                for j in range(desktop.get_child_count()):
                    app = desktop.get_child_at_index(j)
                    if app and app.get_role() == Atspi.Role.APPLICATION:
                        node = AccessibilityNode(app)
                        apps.append({
                            'name': node.name,
                            'pid': app.get_process_id(),
                            'role': node.role,
                            'description': node.description
                        })
            return apps
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des applications: {str(e)}")
            return []
    
    def register_event_listener(self, event_type: str, callback: Callable) -> bool:
        """Enregistre un écouteur d'événements"""
        try:
            if event_type not in self.event_listeners:
                self.event_listeners[event_type] = []
            self.event_listeners[event_type].append(callback)
            
            # Enregistre l'événement auprès d'AT-SPI
            Atspi.register_keystroke_listener(
                callback,
                mask=Atspi.KeyMaskType.all,
                kind=Atspi.KeyEventType.PRESSED_RELEASED
            )
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'écouteur d'événements: {str(e)}")
            return False
    
    def unregister_event_listener(self, event_type: str, callback: Callable) -> bool:
        """Désenregistre un écouteur d'événements"""
        try:
            if event_type in self.event_listeners and callback in self.event_listeners[event_type]:
                self.event_listeners[event_type].remove(callback)
                Atspi.deregister_keystroke_listener(callback)
                return True
        except Exception as e:
            logger.error(f"Erreur lors du désenregistrement de l'écouteur d'événements: {str(e)}")
        return False
    
    def cleanup(self) -> None:
        """Nettoie les ressources"""
        try:
            # Désenregistre tous les écouteurs
            for event_type, listeners in self.event_listeners.items():
                for listener in listeners:
                    Atspi.deregister_keystroke_listener(listener)
            self.event_listeners.clear()
            
            # Nettoie AT-SPI
            Atspi.shutdown()
            
            self.initialized = False
            self.root = None
            self.focused_node = None
            self.braille_display = None
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage du gestionnaire d'accessibilité: {str(e)}")

# Instance globale du gestionnaire d'accessibilité
_accessibility_manager: Optional[AccessibilityManager] = None

def initialize() -> bool:
    """Initialise le gestionnaire d'accessibilité"""
    global _accessibility_manager
    
    try:
        _accessibility_manager = AccessibilityManager()
        return _accessibility_manager.initialize()
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de l'accessibilité: {str(e)}")
        return False

def initialize_braille() -> bool:
    """Initialise le support braille"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return False
    
    return _accessibility_manager.initialize_braille()

def get_focused_node() -> Optional[AccessibilityNode]:
    """Récupère le nœud qui a le focus"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return None
    
    return _accessibility_manager.get_focused_node()

def get_node_at_point(x: int, y: int) -> Optional[AccessibilityNode]:
    """Récupère le nœud à la position spécifiée"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return None
    
    return _accessibility_manager.get_node_at_point(x, y)

def get_application_list() -> List[Dict[str, Any]]:
    """Récupère la liste des applications accessibles"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return []
    
    return _accessibility_manager.get_application_list()

def register_event_listener(event_type: str, callback: Callable) -> bool:
    """Enregistre un écouteur d'événements"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return False
    
    return _accessibility_manager.register_event_listener(event_type, callback)

def unregister_event_listener(event_type: str, callback: Callable) -> bool:
    """Désenregistre un écouteur d'événements"""
    global _accessibility_manager
    
    if not _accessibility_manager:
        logger.error("Le gestionnaire d'accessibilité n'est pas initialisé")
        return False
    
    return _accessibility_manager.unregister_event_listener(event_type, callback)

def cleanup() -> None:
    """Nettoie les ressources"""
    global _accessibility_manager
    
    if _accessibility_manager:
        _accessibility_manager.cleanup()
        _accessibility_manager = None

def print_accessible_tree():
    print("[AT-SPI] (Simulation) Arborescence accessible affichée.")
    # Ici, on utiliserait pyatspi pour parcourir l'arbre des objets accessibles. 