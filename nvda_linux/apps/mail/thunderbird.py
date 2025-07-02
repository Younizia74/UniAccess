#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour Thunderbird
Gère l'interaction avec Thunderbird via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Lecture des messages
- Gestion des dossiers
- Gestion des contacts
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

# Rôles spécifiques à Thunderbird
THUNDERBIRD_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'window': Atspi.Role.FRAME,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
    'tree': Atspi.Role.TREE,
    'tree_item': Atspi.Role.TREE_ITEM,
    'table': Atspi.Role.TABLE,
    'table_cell': Atspi.Role.TABLE_CELL,
    'table_row': Atspi.Role.TABLE_ROW,
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
    'link': Atspi.Role.LINK,
    'heading': Atspi.Role.HEADING,
    'list': Atspi.Role.LIST,
    'list_item': Atspi.Role.LIST_ITEM,
    'image': Atspi.Role.IMAGE,
    'form': Atspi.Role.FORM,
    'form_field': Atspi.Role.ENTRY,
}

# Variables globales
_accessibility_manager = None
_thunderbird_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec Thunderbird."""
    global _accessibility_manager, _thunderbird_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance de Thunderbird
        _thunderbird_instance = find_thunderbird_instance()
        if not _thunderbird_instance:
            logger.error("Thunderbird n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration Thunderbird initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Thunderbird : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _thunderbird_instance
    
    try:
        _thunderbird_instance = None
        _accessibility_manager = None
        logger.info("Intégration Thunderbird nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Thunderbird : {str(e)}")

def find_thunderbird_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance de Thunderbird en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() in ['thunderbird', 'mozilla thunderbird']:
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de Thunderbird : {str(e)}")
        return None

def get_mail_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance de Thunderbird."""
    if not _thunderbird_instance:
        return {}
        
    try:
        return {
            'name': _thunderbird_instance.get_name(),
            'role': _thunderbird_instance.get_role_name(),
            'version': _thunderbird_instance.get_attributes().get('version', ''),
            'pid': _thunderbird_instance.get_process_id(),
            'children': len(_thunderbird_instance.get_children())
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations Thunderbird : {str(e)}")
        return {}

def get_folders() -> List[Dict[str, Any]]:
    """Récupère la liste des dossiers de messagerie."""
    if not _thunderbird_instance:
        return []
        
    try:
        folders = []
        def find_folders(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.TREE_ITEM:
                folders.append({
                    'name': element.get_name(),
                    'role': element.get_role_name(),
                    'description': element.get_description(),
                    'attributes': element.get_attributes()
                })
            for child in element.get_children():
                find_folders(child)
                
        find_folders(_thunderbird_instance)
        return folders
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des dossiers : {str(e)}")
        return []

def get_messages(folder: str) -> List[Dict[str, Any]]:
    """Récupère la liste des messages d'un dossier."""
    if not _thunderbird_instance:
        return []
        
    try:
        messages = []
        def find_messages(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.TABLE_ROW:
                # Vérifier si le message appartient au dossier spécifié
                parent = element.get_parent()
                if parent and parent.get_name() == folder:
                    messages.append({
                        'id': element.get_attributes().get('id', ''),
                        'subject': element.get_name(),
                        'sender': element.get_attributes().get('sender', ''),
                        'date': element.get_attributes().get('date', ''),
                        'read': element.get_state_set().contains(Atspi.StateType.CHECKED),
                        'has_attachment': element.get_attributes().get('has_attachment', 'false') == 'true'
                    })
            for child in element.get_children():
                find_messages(child)
                
        find_messages(_thunderbird_instance)
        return messages
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des messages : {str(e)}")
        return []

def get_message_content(message_id: str) -> Dict[str, Any]:
    """Récupère le contenu d'un message."""
    if not _thunderbird_instance:
        return {}
        
    try:
        def find_message(element: Atspi.Accessible) -> Optional[Dict[str, Any]]:
            if (element.get_role() == Atspi.Role.TABLE_ROW and 
                element.get_attributes().get('id', '') == message_id):
                # Récupérer le contenu du message
                content = {
                    'id': message_id,
                    'subject': element.get_name(),
                    'sender': element.get_attributes().get('sender', ''),
                    'recipients': element.get_attributes().get('recipients', ''),
                    'date': element.get_attributes().get('date', ''),
                    'body': '',
                    'attachments': []
                }
                
                # Parcourir les enfants pour trouver le corps du message et les pièces jointes
                for child in element.get_children():
                    if child.get_role() == Atspi.Role.TEXT:
                        content['body'] += child.get_text(0, -1)
                    elif child.get_role() == Atspi.Role.LIST_ITEM:
                        content['attachments'].append({
                            'name': child.get_name(),
                            'type': child.get_attributes().get('type', ''),
                            'size': child.get_attributes().get('size', '')
                        })
                        
                return content
                
            for child in element.get_children():
                result = find_message(child)
                if result:
                    return result
                    
            return None
            
        return find_message(_thunderbird_instance) or {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contenu du message : {str(e)}")
        return {}

def compose_message(**kwargs) -> bool:
    """Compose un nouveau message."""
    if not _thunderbird_instance:
        return False
        
    try:
        # Trouver le bouton "Nouveau message"
        for element in _thunderbird_instance.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'nouveau message' in element.get_name().lower()):
                if not element.do_action(0):  # Action par défaut (clic)
                    return False
                    
                # Attendre que la fenêtre de composition s'ouvre
                # Remplir les champs du message
                for field, value in kwargs.items():
                    if field == 'to':
                        # Trouver le champ destinataire
                        for child in element.get_children():
                            if child.get_role() == Atspi.Role.ENTRY:
                                child.set_text_contents(value)
                                break
                    elif field == 'subject':
                        # Trouver le champ sujet
                        for child in element.get_children():
                            if child.get_role() == Atspi.Role.ENTRY:
                                child.set_text_contents(value)
                                break
                    elif field == 'body':
                        # Trouver le champ corps du message
                        for child in element.get_children():
                            if child.get_role() == Atspi.Role.TEXT:
                                child.set_text_contents(value)
                                break
                                
                return True
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la composition du message : {str(e)}")
        return False

def reply_to_message(message_id: str, reply_all: bool = False) -> bool:
    """Répond à un message."""
    if not _thunderbird_instance:
        return False
        
    try:
        # Trouver le message
        def find_message(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TABLE_ROW and 
                element.get_attributes().get('id', '') == message_id):
                return element
            for child in element.get_children():
                result = find_message(child)
                if result:
                    return result
            return None
            
        message = find_message(_thunderbird_instance)
        if not message:
            return False
            
        # Trouver le bouton de réponse approprié
        action = 'répondre à tous' if reply_all else 'répondre'
        for element in message.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                action in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la réponse au message : {str(e)}")
        return False

def forward_message(message_id: str) -> bool:
    """Transmet un message."""
    if not _thunderbird_instance:
        return False
        
    try:
        # Trouver le message
        def find_message(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TABLE_ROW and 
                element.get_attributes().get('id', '') == message_id):
                return element
            for child in element.get_children():
                result = find_message(child)
                if result:
                    return result
            return None
            
        message = find_message(_thunderbird_instance)
        if not message:
            return False
            
        # Trouver le bouton de transmission
        for element in message.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'transmettre' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la transmission du message : {str(e)}")
        return False

def delete_message(message_id: str) -> bool:
    """Supprime un message."""
    if not _thunderbird_instance:
        return False
        
    try:
        # Trouver le message
        def find_message(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TABLE_ROW and 
                element.get_attributes().get('id', '') == message_id):
                return element
            for child in element.get_children():
                result = find_message(child)
                if result:
                    return result
            return None
            
        message = find_message(_thunderbird_instance)
        if not message:
            return False
            
        # Trouver le bouton de suppression
        for element in message.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                'supprimer' in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du message : {str(e)}")
        return False

def mark_message_read(message_id: str, read: bool = True) -> bool:
    """Marque un message comme lu/non lu."""
    if not _thunderbird_instance:
        return False
        
    try:
        # Trouver le message
        def find_message(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if (element.get_role() == Atspi.Role.TABLE_ROW and 
                element.get_attributes().get('id', '') == message_id):
                return element
            for child in element.get_children():
                result = find_message(child)
                if result:
                    return result
            return None
            
        message = find_message(_thunderbird_instance)
        if not message:
            return False
            
        # Vérifier l'état actuel
        current_state = message.get_state_set().contains(Atspi.StateType.CHECKED)
        if current_state == read:
            return True  # Déjà dans l'état souhaité
            
        # Trouver le bouton de marquage
        action = 'marquer comme lu' if read else 'marquer comme non lu'
        for element in message.get_children():
            if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                action in element.get_name().lower()):
                return element.do_action(0)  # Action par défaut (clic)
                
        return False
    except Exception as e:
        logger.error(f"Erreur lors du marquage du message : {str(e)}")
        return False

def search_messages(query: str, folder: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recherche des messages."""
    if not _thunderbird_instance:
        return []
        
    try:
        # Trouver le champ de recherche
        def find_search_field(element: Atspi.Accessible) -> Optional[Atspi.Accessible]:
            if element.get_role() == Atspi.Role.ENTRY and 'rechercher' in element.get_name().lower():
                return element
            for child in element.get_children():
                result = find_search_field(child)
                if result:
                    return result
            return None
            
        search_field = find_search_field(_thunderbird_instance)
        if not search_field:
            return []
            
        # Entrer la requête de recherche
        search_field.set_text_contents(query)
        
        # Si un dossier est spécifié, le sélectionner d'abord
        if folder:
            for element in _thunderbird_instance.get_children():
                if (element.get_role() == Atspi.Role.TREE_ITEM and 
                    element.get_name() == folder):
                    element.do_action(0)  # Action par défaut (sélection)
                    break
                    
        # Attendre les résultats et les récupérer
        messages = []
        def find_messages(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.TABLE_ROW:
                # Vérifier si le message correspond à la recherche
                if (query.lower() in element.get_name().lower() or
                    query.lower() in element.get_attributes().get('sender', '').lower() or
                    query.lower() in element.get_attributes().get('body', '').lower()):
                    messages.append({
                        'id': element.get_attributes().get('id', ''),
                        'subject': element.get_name(),
                        'sender': element.get_attributes().get('sender', ''),
                        'date': element.get_attributes().get('date', ''),
                        'read': element.get_state_set().contains(Atspi.StateType.CHECKED),
                        'has_attachment': element.get_attributes().get('has_attachment', 'false') == 'true'
                    })
            for child in element.get_children():
                find_messages(child)
                
        find_messages(_thunderbird_instance)
        return messages
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de messages : {str(e)}")
        return []

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans Thunderbird."""
    if not _thunderbird_instance:
        return False
        
    try:
        if action == 'new_message':
            return compose_message(**kwargs)
            
        elif action == 'reply':
            message_id = kwargs.get('message_id')
            reply_all = kwargs.get('reply_all', False)
            return reply_to_message(message_id, reply_all)
            
        elif action == 'forward':
            message_id = kwargs.get('message_id')
            return forward_message(message_id)
            
        elif action == 'delete':
            message_id = kwargs.get('message_id')
            return delete_message(message_id)
            
        elif action == 'mark_read':
            message_id = kwargs.get('message_id')
            read = kwargs.get('read', True)
            return mark_message_read(message_id, read)
            
        elif action == 'search':
            query = kwargs.get('query', '')
            folder = kwargs.get('folder')
            return bool(search_messages(query, folder))
            
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