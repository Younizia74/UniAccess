#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour MPV
Gère l'interaction avec MPV via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Contrôle de la lecture
- Gestion des listes de lecture
- Gestion des sous-titres et des pistes audio
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

# Rôles spécifiques à MPV
MPV_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'window': Atspi.Role.FRAME,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
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
    'list': Atspi.Role.LIST,
    'list_item': Atspi.Role.LIST_ITEM,
    'tree': Atspi.Role.TREE,
    'tree_item': Atspi.Role.TREE_ITEM,
    'combo_box': Atspi.Role.COMBO_BOX,
    'check_box': Atspi.Role.CHECK_BOX,
    'radio_button': Atspi.Role.RADIO_BUTTON,
    'text': Atspi.Role.TEXT,
    'edit': Atspi.Role.ENTRY,
    'image': Atspi.Role.IMAGE,
    'video': Atspi.Role.VIDEO,
    'audio': Atspi.Role.AUDIO,
}

# Variables globales
_accessibility_manager = None
_mpv_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec MPV."""
    global _accessibility_manager, _mpv_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance de MPV
        _mpv_instance = find_mpv_instance()
        if not _mpv_instance:
            logger.error("MPV n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration MPV initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de MPV : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _mpv_instance
    
    try:
        _mpv_instance = None
        _accessibility_manager = None
        logger.info("Intégration MPV nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de MPV : {str(e)}")

def find_mpv_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance de MPV en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() == 'mpv':
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de MPV : {str(e)}")
        return None

def get_instance() -> Optional[Atspi.Accessible]:
    """Récupère l'instance de MPV."""
    return _mpv_instance

def get_player_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance de MPV."""
    if not _mpv_instance:
        return {}
        
    try:
        return {
            'name': _mpv_instance.get_name(),
            'role': _mpv_instance.get_role_name(),
            'version': _mpv_instance.get_attributes().get('version', ''),
            'pid': _mpv_instance.get_process_id(),
            'children': len(_mpv_instance.get_children())
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations MPV : {str(e)}")
        return {}

def get_playlist() -> List[Dict[str, Any]]:
    """Récupère la liste de lecture."""
    if not _mpv_instance:
        return []
        
    try:
        playlist = []
        def find_playlist(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.LIST_ITEM:
                playlist.append({
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'duration': element.get_attributes().get('duration', ''),
                    'path': element.get_attributes().get('path', ''),
                    'type': element.get_attributes().get('type', '')
                })
            for child in element.get_children():
                find_playlist(child)
                
        find_playlist(_mpv_instance)
        return playlist
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la liste de lecture : {str(e)}")
        return []

def get_current_track() -> Dict[str, Any]:
    """Récupère les informations sur la piste en cours de lecture."""
    if not _mpv_instance:
        return {}
        
    try:
        def find_current_track(element: Atspi.Accessible) -> Optional[Dict[str, Any]]:
            if (element.get_role() == Atspi.Role.LIST_ITEM and 
                element.get_state_set().contains(Atspi.StateType.SELECTED)):
                return {
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'duration': element.get_attributes().get('duration', ''),
                    'path': element.get_attributes().get('path', ''),
                    'type': element.get_attributes().get('type', ''),
                    'position': element.get_attributes().get('position', '0'),
                    'volume': element.get_attributes().get('volume', '100')
                }
            for child in element.get_children():
                result = find_current_track(child)
                if result:
                    return result
            return None
            
        return find_current_track(_mpv_instance) or {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la piste en cours : {str(e)}")
        return {}

def get_playback_state() -> Dict[str, Any]:
    """Récupère l'état de lecture."""
    if not _mpv_instance:
        return {}
        
    try:
        def find_playback_state(element: Atspi.Accessible) -> Dict[str, Any]:
            state = {
                'playing': False,
                'paused': False,
                'stopped': True,
                'position': 0.0,
                'volume': 100,
                'muted': False,
                'repeat': False,
                'shuffle': False
            }
            
            # Parcourir les contrôles de lecture
            for child in element.get_children():
                if child.get_role() == Atspi.Role.PUSH_BUTTON:
                    name = child.get_name().lower()
                    if 'play' in name:
                        state['playing'] = child.get_state_set().contains(Atspi.StateType.PRESSED)
                    elif 'pause' in name:
                        state['paused'] = child.get_state_set().contains(Atspi.StateType.PRESSED)
                    elif 'stop' in name:
                        state['stopped'] = child.get_state_set().contains(Atspi.StateType.PRESSED)
                    elif 'repeat' in name:
                        state['repeat'] = child.get_state_set().contains(Atspi.StateType.CHECKED)
                    elif 'shuffle' in name:
                        state['shuffle'] = child.get_state_set().contains(Atspi.StateType.CHECKED)
                    elif 'mute' in name:
                        state['muted'] = child.get_state_set().contains(Atspi.StateType.CHECKED)
                        
                elif child.get_role() == Atspi.Role.SLIDER:
                    name = child.get_name().lower()
                    if 'position' in name:
                        state['position'] = float(child.get_current_value())
                    elif 'volume' in name:
                        state['volume'] = float(child.get_current_value())
                        
            return state
            
        return find_playback_state(_mpv_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état de lecture : {str(e)}")
        return {}

def play() -> bool:
    """Démarre la lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton play
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'play' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la lecture : {str(e)}")
        return False

def pause() -> bool:
    """Met en pause la lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton pause
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'pause' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la pause : {str(e)}")
        return False

def stop() -> bool:
    """Arrête la lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton stop
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'stop' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt : {str(e)}")
        return False

def next_track() -> bool:
    """Passe à la piste suivante."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton next
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'next' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du passage à la piste suivante : {str(e)}")
        return False

def previous_track() -> bool:
    """Revient à la piste précédente."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton previous
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'previous' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du retour à la piste précédente : {str(e)}")
        return False

def set_volume(volume: float) -> bool:
    """Définit le volume de lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le slider de volume
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.SLIDER and 
                'volume' in element.get_name().lower()):
                return element.set_current_value(volume)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du réglage du volume : {str(e)}")
        return False

def seek(position: float) -> bool:
    """Se positionne à un moment précis de la lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le slider de position
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.SLIDER and 
                'position' in element.get_name().lower()):
                return element.set_current_value(position)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du positionnement : {str(e)}")
        return False

def add_to_playlist(file_path: str) -> bool:
    """Ajoute un fichier à la liste de lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver le bouton d'ajout
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'add' in element.get_name().lower()):
                if not element.do_action(0):  # Action par défaut (clic)
                    return False
                    
                # Attendre que la boîte de dialogue s'ouvre
                # Sélectionner le fichier
                for child in element.get_children():
                    if child.get_role() == Atspi.Role.ENTRY:
                        child.set_text_contents(file_path)
                        break
                        
                # Valider
                for child in element.get_children():
                    if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                        'ok' in child.get_name().lower()):
                        return child.do_action(0)
                        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout à la liste de lecture : {str(e)}")
        return False

def remove_from_playlist(track_id: str) -> bool:
    """Retire une piste de la liste de lecture."""
    if not _mpv_instance:
        return False
        
    try:
        # Trouver la piste dans la liste
        def find_track(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.LIST_ITEM and 
                element.get_attributes().get('id', '') == track_id):
                return element
            for child in element.get_children():
                result = find_track(child)
                if result:
                    return result
            return None
            
        track = find_track(_mpv_instance)
        if not track:
            return False
            
        # Sélectionner la piste
        if not track.do_action(0):  # Action par défaut (sélection)
            return False
            
        # Trouver le bouton de suppression
        for element in _mpv_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'remove' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la liste de lecture : {str(e)}")
        return False

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans MPV."""
    if not _mpv_instance:
        return False
        
    try:
        if action == 'play':
            return play()
            
        elif action == 'pause':
            return pause()
            
        elif action == 'stop':
            return stop()
            
        elif action == 'next':
            return next_track()
            
        elif action == 'previous':
            return previous_track()
            
        elif action == 'volume':
            volume = kwargs.get('volume', 100.0)
            return set_volume(volume)
            
        elif action == 'seek':
            position = kwargs.get('position', 0.0)
            return seek(position)
            
        elif action == 'add':
            file_path = kwargs.get('file_path', '')
            return add_to_playlist(file_path)
            
        elif action == 'remove':
            track_id = kwargs.get('track_id', '')
            return remove_from_playlist(track_id)
            
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