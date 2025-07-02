#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour Amarok
Gère l'interaction avec Amarok via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Contrôle de la lecture
- Gestion des bibliothèques et des listes de lecture
- Gestion des métadonnées
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

# Rôles spécifiques à Amarok
AMAROK_ROLES = {
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
    'audio': Atspi.Role.AUDIO,
}

# Variables globales
_accessibility_manager = None
_amarok_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec Amarok."""
    global _accessibility_manager, _amarok_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance de Amarok
        _amarok_instance = find_amarok_instance()
        if not _amarok_instance:
            logger.error("Amarok n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration Amarok initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Amarok : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _amarok_instance
    
    try:
        _amarok_instance = None
        _accessibility_manager = None
        logger.info("Intégration Amarok nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Amarok : {str(e)}")

def find_amarok_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance de Amarok en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() == 'amarok':
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de Amarok : {str(e)}")
        return None

def get_instance() -> Optional[Atspi.Accessible]:
    """Récupère l'instance de Amarok."""
    return _amarok_instance

def get_player_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance de Amarok."""
    if not _amarok_instance:
        return {}
        
    try:
        return {
            'name': _amarok_instance.get_name(),
            'role': _amarok_instance.get_role_name(),
            'version': _amarok_instance.get_attributes().get('version', ''),
            'pid': _amarok_instance.get_process_id(),
            'children': len(_amarok_instance.get_children())
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations Amarok : {str(e)}")
        return {}

def get_library() -> List[Dict[str, Any]]:
    """Récupère la bibliothèque musicale."""
    if not _amarok_instance:
        return []
        
    try:
        library = []
        def find_library(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.TREE_ITEM:
                library.append({
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'artist': element.get_attributes().get('artist', ''),
                    'album': element.get_attributes().get('album', ''),
                    'genre': element.get_attributes().get('genre', ''),
                    'duration': element.get_attributes().get('duration', ''),
                    'path': element.get_attributes().get('path', ''),
                    'type': element.get_attributes().get('type', '')
                })
            for child in element.get_children():
                find_library(child)
                
        find_library(_amarok_instance)
        return library
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la bibliothèque : {str(e)}")
        return []

def get_playlists() -> List[Dict[str, Any]]:
    """Récupère la liste des playlists."""
    if not _amarok_instance:
        return []
        
    try:
        playlists = []
        def find_playlists(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.TREE_ITEM:
                playlists.append({
                    'id': element.get_attributes().get('id', ''),
                    'name': element.get_name(),
                    'type': element.get_attributes().get('type', ''),
                    'tracks': int(element.get_attributes().get('tracks', '0')),
                    'duration': element.get_attributes().get('duration', '')
                })
            for child in element.get_children():
                find_playlists(child)
                
        find_playlists(_amarok_instance)
        return playlists
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des playlists : {str(e)}")
        return []

def get_current_track() -> Dict[str, Any]:
    """Récupère les informations sur la piste en cours de lecture."""
    if not _amarok_instance:
        return {}
        
    try:
        def find_current_track(element: Atspi.Accessible) -> Optional[Dict[str, Any]]:
            if (element.get_role() == Atspi.Role.TREE_ITEM and 
                element.get_state_set().contains(Atspi.StateType.SELECTED)):
                return {
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'artist': element.get_attributes().get('artist', ''),
                    'album': element.get_attributes().get('album', ''),
                    'genre': element.get_attributes().get('genre', ''),
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
            
        return find_current_track(_amarok_instance) or {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la piste en cours : {str(e)}")
        return {}

def get_playback_state() -> Dict[str, Any]:
    """Récupère l'état de lecture."""
    if not _amarok_instance:
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
            
        return find_playback_state(_amarok_instance)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état de lecture : {str(e)}")
        return {}

def play() -> bool:
    """Démarre la lecture."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton play
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'play' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la lecture : {str(e)}")
        return False

def pause() -> bool:
    """Met en pause la lecture."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton pause
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'pause' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la pause : {str(e)}")
        return False

def stop() -> bool:
    """Arrête la lecture."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton stop
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'stop' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt : {str(e)}")
        return False

def next_track() -> bool:
    """Passe à la piste suivante."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton next
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'next' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du passage à la piste suivante : {str(e)}")
        return False

def previous_track() -> bool:
    """Revient à la piste précédente."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton previous
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'previous' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du retour à la piste précédente : {str(e)}")
        return False

def set_volume(volume: float) -> bool:
    """Définit le volume de lecture."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le slider de volume
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.SLIDER and 
                'volume' in element.get_name().lower()):
                return element.set_current_value(volume)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du réglage du volume : {str(e)}")
        return False

def seek(position: float) -> bool:
    """Se positionne à un moment précis de la lecture."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le slider de position
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.SLIDER and 
                'position' in element.get_name().lower()):
                return element.set_current_value(position)
        return False
    except Exception as e:
        logger.error(f"Erreur lors du positionnement : {str(e)}")
        return False

def create_playlist(name: str) -> bool:
    """Crée une nouvelle playlist."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver le bouton de création de playlist
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'new playlist' in element.get_name().lower()):
                if not element.do_action(0):  # Action par défaut (clic)
                    return False
                    
                # Attendre que la boîte de dialogue s'ouvre
                # Entrer le nom de la playlist
                for child in element.get_children():
                    if child.get_role() == Atspi.Role.ENTRY:
                        child.set_text_contents(name)
                        break
                        
                # Valider
                for child in element.get_children():
                    if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                        'ok' in child.get_name().lower()):
                        return child.do_action(0)
                        
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la création de la playlist : {str(e)}")
        return False

def add_to_playlist(playlist_id: str, track_id: str) -> bool:
    """Ajoute une piste à une playlist."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver la playlist
        def find_playlist(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TREE_ITEM and 
                element.get_attributes().get('id', '') == playlist_id):
                return element
            for child in element.get_children():
                result = find_playlist(child)
                if result:
                    return result
            return None
            
        playlist = find_playlist(_amarok_instance)
        if not playlist:
            return False
            
        # Sélectionner la playlist
        if not playlist.do_action(0):  # Action par défaut (sélection)
            return False
            
        # Trouver la piste
        def find_track(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TREE_ITEM and 
                element.get_attributes().get('id', '') == track_id):
                return element
            for child in element.get_children():
                result = find_track(child)
                if result:
                    return result
            return None
            
        track = find_track(_amarok_instance)
        if not track:
            return False
            
        # Sélectionner la piste
        if not track.do_action(0):  # Action par défaut (sélection)
            return False
            
        # Trouver le bouton d'ajout
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'add' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout à la playlist : {str(e)}")
        return False

def remove_from_playlist(playlist_id: str, track_id: str) -> bool:
    """Retire une piste d'une playlist."""
    if not _amarok_instance:
        return False
        
    try:
        # Trouver la playlist
        def find_playlist(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TREE_ITEM and 
                element.get_attributes().get('id', '') == playlist_id):
                return element
            for child in element.get_children():
                result = find_playlist(child)
                if result:
                    return result
            return None
            
        playlist = find_playlist(_amarok_instance)
        if not playlist:
            return False
            
        # Sélectionner la playlist
        if not playlist.do_action(0):  # Action par défaut (sélection)
            return False
            
        # Trouver la piste dans la playlist
        def find_track(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TREE_ITEM and 
                element.get_attributes().get('id', '') == track_id):
                return element
            for child in element.get_children():
                result = find_track(child)
                if result:
                    return result
            return None
            
        track = find_track(playlist)
        if not track:
            return False
            
        # Sélectionner la piste
        if not track.do_action(0):  # Action par défaut (sélection)
            return False
            
        # Trouver le bouton de suppression
        for element in _amarok_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'remove' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la playlist : {str(e)}")
        return False

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans Amarok."""
    if not _amarok_instance:
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
            
        elif action == 'create_playlist':
            name = kwargs.get('name', '')
            return create_playlist(name)
            
        elif action == 'add_to_playlist':
            playlist_id = kwargs.get('playlist_id', '')
            track_id = kwargs.get('track_id', '')
            return add_to_playlist(playlist_id, track_id)
            
        elif action == 'remove_from_playlist':
            playlist_id = kwargs.get('playlist_id', '')
            track_id = kwargs.get('track_id', '')
            return remove_from_playlist(playlist_id, track_id)
            
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