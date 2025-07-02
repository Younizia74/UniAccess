#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour les jeux via Proton
Gère l'interaction avec les jeux Windows via Proton, incluant :
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

# Rôles spécifiques aux jeux Proton
PROTON_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'window': Atspi.Role.FRAME,
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
    'canvas': Atspi.Role.CANVAS,
    'image': Atspi.Role.IMAGE,
    'link': Atspi.Role.LINK,
    'form': Atspi.Role.FORM,
    'form_field': Atspi.Role.ENTRY,
}

# Variables globales
_accessibility_manager = None
_proton_instances = {}
_steam_install_path = None

def initialize() -> bool:
    """Initialise l'intégration avec les jeux Proton."""
    global _accessibility_manager, _proton_instances, _steam_install_path
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver le chemin d'installation de Steam
        _steam_install_path = find_steam_install_path()
        if not _steam_install_path:
            logger.error("Steam n'est pas installé")
            return False
            
        # Trouver les instances de jeux Proton
        _proton_instances = find_proton_instances()
        if not _proton_instances:
            logger.warning("Aucun jeu Proton n'est en cours d'exécution")
            return False
            
        logger.info(f"Intégration Proton initialisée avec succès pour {len(_proton_instances)} jeux")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Proton : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _proton_instances, _steam_install_path
    
    try:
        _proton_instances.clear()
        _steam_install_path = None
        _accessibility_manager = None
        logger.info("Intégration Proton nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Proton : {str(e)}")

def find_steam_install_path() -> Optional[str]:
    """Trouve le chemin d'installation de Steam."""
    try:
        # Vérifier les chemins courants
        steam_paths = [
            os.path.expanduser('~/.steam/steam'),
            os.path.expanduser('~/.local/share/Steam'),
            '/usr/share/steam',
            '/opt/steam'
        ]
        
        for path in steam_paths:
            if os.path.exists(path):
                return path
                
        # Essayer de trouver via which
        result = subprocess.run(['which', 'steam'], capture_output=True, text=True)
        if result.returncode == 0:
            steam_bin = result.stdout.strip()
            # Suivre le lien symbolique
            steam_path = os.path.realpath(steam_bin)
            # Remonter jusqu'au dossier Steam
            while os.path.basename(steam_path) != 'steam':
                steam_path = os.path.dirname(steam_path)
                if steam_path == '/':
                    break
            if os.path.exists(steam_path):
                return steam_path
                
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du chemin d'installation de Steam : {str(e)}")
        return None

def find_proton_instances() -> Dict[str, Atspi.Accessible]:
    """Trouve les instances de jeux Proton en cours d'exécution."""
    instances = {}
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            # Vérifier si l'application est un jeu Proton
            if is_proton_game(app):
                instances[app.get_name()] = app
        return instances
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des jeux Proton : {str(e)}")
        return {}

def is_proton_game(app: Atspi.Accessible) -> bool:
    """Vérifie si une application est un jeu Proton."""
    try:
        # Vérifier les attributs spécifiques aux jeux Proton
        attrs = app.get_attributes()
        if not attrs:
            return False
            
        # Vérifier le processus
        pid = app.get_process_id()
        if not pid:
            return False
            
        # Lire le fichier /proc/<pid>/cmdline pour vérifier si c'est un jeu Proton
        try:
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read().lower()
                # Vérifier les indicateurs Proton
                proton_indicators = [
                    'proton', 'steam', 'wine', 'dxvk', 'vkd3d',
                    'steamapps', 'compatdata', 'pfx'
                ]
                return any(ind in cmdline for ind in proton_indicators)
        except:
            return False
            
    except Exception:
        return False

def get_proton_info(game_name: Optional[str] = None) -> Dict[str, Any]:
    """Récupère les informations sur l'instance de jeu Proton spécifiée ou toutes les instances."""
    if game_name:
        game = _proton_instances.get(game_name)
        if not game:
            return {}
            
        try:
            # Récupérer les informations de base
            info = {
                'name': game.get_name(),
                'role': game.get_role_name(),
                'version': game.get_attributes().get('version', ''),
                'pid': game.get_process_id(),
                'children': len(game.get_children())
            }
            
            # Ajouter les informations spécifiques à Proton
            pid = game.get_process_id()
            if pid:
                try:
                    # Lire les informations du processus
                    with open(f'/proc/{pid}/environ', 'r') as f:
                        env = f.read()
                        # Extraire les variables d'environnement pertinentes
                        for var in ['STEAM_APPID', 'STEAM_RUNTIME', 'PROTON_VERSION']:
                            if var in env:
                                info[var] = env.split(f'{var}=')[1].split('\0')[0]
                except:
                    pass
                    
            return info
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations pour {game_name} : {str(e)}")
            return {}
    else:
        return {name: get_proton_info(name) for name in _proton_instances.keys()}

def get_accessibility_tree(game_name: str) -> Dict[str, Any]:
    """Récupère l'arbre d'accessibilité d'un jeu Proton."""
    game = _proton_instances.get(game_name)
    if not game:
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
        return get_element_info(game)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'arbre d'accessibilité pour {game_name} : {str(e)}")
        return {}

def get_focused_element(game_name: str) -> Dict[str, Any]:
    """Récupère l'élément actuellement focalisé dans un jeu Proton."""
    game = _proton_instances.get(game_name)
    if not game:
        return {}
        
    try:
        focused = Atspi.get_focused()
        if not focused:
            return {}
            
        # Vérifier si l'élément focalisé appartient au jeu
        if not is_child_of(focused, game):
            return {}
            
        return {
            'name': focused.get_name(),
            'role': focused.get_role_name(),
            'description': focused.get_description(),
            'attributes': focused.get_attributes()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'élément focalisé pour {game_name} : {str(e)}")
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

def get_current_selection(game_name: str) -> List[Dict[str, Any]]:
    """Récupère la sélection actuelle dans un jeu Proton."""
    game = _proton_instances.get(game_name)
    if not game:
        return []
        
    try:
        focused = Atspi.get_focused()
        if not focused or not is_child_of(focused, game):
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
        logger.error(f"Erreur lors de la récupération de la sélection pour {game_name} : {str(e)}")
        return []

def get_game_state(game_name: str) -> Dict[str, Any]:
    """Récupère l'état actuel du jeu Proton."""
    game = _proton_instances.get(game_name)
    if not game:
        return {}
        
    try:
        # Parcourir l'arbre pour trouver les éléments d'état
        def find_state_elements(element: Atspi.Accessible) -> Dict[str, Any]:
            state = {}
            
            # Vérifier les éléments d'état courants
            if element.get_role() in [Atspi.Role.STATUS_BAR, Atspi.Role.PROGRESS_BAR]:
                state[element.get_name()] = element.get_description()
                
            # Vérifier les éléments de menu
            if element.get_role() == Atspi.Role.MENU:
                state['menu'] = {
                    'name': element.get_name(),
                    'items': [item.get_name() for item in element.get_children()]
                }
                
            # Vérifier les dialogues
            if element.get_role() == Atspi.Role.DIALOG:
                state['dialog'] = {
                    'name': element.get_name(),
                    'content': element.get_description()
                }
                
            # Parcourir les enfants
            for child in element.get_children():
                child_state = find_state_elements(child)
                state.update(child_state)
                
            return state
            
        return find_state_elements(game)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état du jeu pour {game_name} : {str(e)}")
        return {}

def execute_action(game_name: str, action: str, **kwargs) -> bool:
    """Exécute une action dans un jeu Proton."""
    game = _proton_instances.get(game_name)
    if not game:
        return False
        
    try:
        if action == 'click':
            element = kwargs.get('element')
            if element and is_child_of(element, game):
                return element.do_action(0)  # Action par défaut (clic)
                
        elif action == 'focus':
            element = kwargs.get('element')
            if element and is_child_of(element, game):
                return element.do_action(1)  # Action par défaut (focus)
                
        elif action == 'menu':
            element = kwargs.get('element')
            if element and is_child_of(element, game):
                return element.do_action(2)  # Action par défaut (menu)
                
        elif action == 'context_menu':
            element = kwargs.get('element')
            if element and is_child_of(element, game):
                return element.do_action(3)  # Action par défaut (menu contextuel)
                
        elif action == 'scroll':
            element = kwargs.get('element')
            direction = kwargs.get('direction', 'down')
            if element and is_child_of(element, game):
                if direction == 'up':
                    return element.do_action(4)  # Action par défaut (scroll up)
                else:
                    return element.do_action(5)  # Action par défaut (scroll down)
                    
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'action {action} pour {game_name} : {str(e)}")
        return False 