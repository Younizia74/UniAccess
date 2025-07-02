#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'intégration pour Kate
Gère l'interaction avec Kate via AT-SPI, incluant :
- Navigation dans l'arbre d'accessibilité
- Gestion des documents
- Gestion du curseur et des sélections
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

# Rôles spécifiques à Kate
KATE_ROLES = {
    'application': Atspi.Role.APPLICATION,
    'window': Atspi.Role.FRAME,
    'menu': Atspi.Role.MENU,
    'menu_item': Atspi.Role.MENU_ITEM,
    'button': Atspi.Role.PUSH_BUTTON,
    'text': Atspi.Role.TEXT,
    'edit': Atspi.Role.ENTRY,
    'document': Atspi.Role.DOCUMENT_FRAME,
    'panel': Atspi.Role.PANEL,
    'scroll_bar': Atspi.Role.SCROLL_BAR,
    'scroll_pane': Atspi.Role.SCROLL_PANE,
    'status_bar': Atspi.Role.STATUS_BAR,
    'toolbar': Atspi.Role.TOOL_BAR,
    'tooltip': Atspi.Role.TOOL_TIP,
    'tree': Atspi.Role.TREE,
    'tree_item': Atspi.Role.TREE_ITEM,
    'tab': Atspi.Role.PAGE_TAB,
    'tab_list': Atspi.Role.PAGE_TAB_LIST,
    'combo_box': Atspi.Role.COMBO_BOX,
    'check_box': Atspi.Role.CHECK_BOX,
    'radio_button': Atspi.Role.RADIO_BUTTON,
    'image': Atspi.Role.IMAGE,
    'separator': Atspi.Role.SEPARATOR,
    'dialog': Atspi.Role.DIALOG,
    'alert': Atspi.Role.ALERT,
    'notification': Atspi.Role.NOTIFICATION,
    'terminal': Atspi.Role.TERMINAL,
    'splitter': Atspi.Role.SPLIT_PANE
}

# Variables globales
_accessibility_manager = None
_kate_instance = None

def initialize() -> bool:
    """Initialise l'intégration avec Kate."""
    global _accessibility_manager, _kate_instance
    
    try:
        # Initialiser AT-SPI
        _accessibility_manager = Atspi.Accessible()
        
        # Trouver l'instance de Kate
        _kate_instance = find_kate_instance()
        if not _kate_instance:
            logger.error("Kate n'est pas en cours d'exécution")
            return False
            
        logger.info("Intégration Kate initialisée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Kate : {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources utilisées par l'intégration."""
    global _accessibility_manager, _kate_instance
    
    try:
        _kate_instance = None
        _accessibility_manager = None
        logger.info("Intégration Kate nettoyée")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de Kate : {str(e)}")

def find_kate_instance() -> Optional[Atspi.Accessible]:
    """Trouve l'instance de Kate en cours d'exécution."""
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop:
            if app.get_name().lower() == 'kate':
                return app
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de Kate : {str(e)}")
        return None

def get_instance() -> Optional[Atspi.Accessible]:
    """Récupère l'instance de Kate."""
    return _kate_instance

def get_editor_info() -> Dict[str, Any]:
    """Récupère les informations sur l'instance de Kate."""
    if not _kate_instance:
        return {}
        
    try:
        return {
            'name': _kate_instance.get_name(),
            'role': _kate_instance.get_role_name(),
            'version': _kate_instance.get_attributes().get('version', ''),
            'pid': _kate_instance.get_process_id(),
            'children': len(_kate_instance.get_children())
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations Kate : {str(e)}")
        return {}

def get_documents() -> List[Dict[str, Any]]:
    """Récupère la liste des documents ouverts."""
    if not _kate_instance:
        return []
        
    try:
        documents = []
        def find_documents(element: Atspi.Accessible) -> None:
            if element.get_role() == Atspi.Role.DOCUMENT_FRAME:
                documents.append({
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'path': element.get_attributes().get('path', ''),
                    'modified': element.get_attributes().get('modified', 'false') == 'true',
                    'readonly': element.get_attributes().get('readonly', 'false') == 'true',
                    'encoding': element.get_attributes().get('encoding', ''),
                    'language': element.get_attributes().get('language', ''),
                    'line_count': int(element.get_attributes().get('line_count', '0')),
                    'word_count': int(element.get_attributes().get('word_count', '0')),
                    'char_count': int(element.get_attributes().get('char_count', '0')),
                    'mode': element.get_attributes().get('mode', ''),
                    'eol': element.get_attributes().get('eol', ''),
                    'indent': element.get_attributes().get('indent', ''),
                    'tab_width': int(element.get_attributes().get('tab_width', '4')),
                    'wrap': element.get_attributes().get('wrap', 'false') == 'true'
                })
            for child in element.get_children():
                find_documents(child)
                
        find_documents(_kate_instance)
        return documents
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des documents : {str(e)}")
        return []

def get_current_document() -> Dict[str, Any]:
    """Récupère les informations sur le document actif."""
    if not _kate_instance:
        return {}
        
    try:
        def find_current_document(element: Atspi.Accessible) -> Optional[Dict[str, Any]]:
            if (element.get_role() == Atspi.Role.DOCUMENT_FRAME and 
                element.get_state_set().contains(Atspi.StateType.FOCUSED)):
                return {
                    'id': element.get_attributes().get('id', ''),
                    'title': element.get_name(),
                    'path': element.get_attributes().get('path', ''),
                    'modified': element.get_attributes().get('modified', 'false') == 'true',
                    'readonly': element.get_attributes().get('readonly', 'false') == 'true',
                    'encoding': element.get_attributes().get('encoding', ''),
                    'language': element.get_attributes().get('language', ''),
                    'line_count': int(element.get_attributes().get('line_count', '0')),
                    'word_count': int(element.get_attributes().get('word_count', '0')),
                    'char_count': int(element.get_attributes().get('char_count', '0')),
                    'cursor_line': int(element.get_attributes().get('cursor_line', '0')),
                    'cursor_column': int(element.get_attributes().get('cursor_column', '0')),
                    'mode': element.get_attributes().get('mode', ''),
                    'eol': element.get_attributes().get('eol', ''),
                    'indent': element.get_attributes().get('indent', ''),
                    'tab_width': int(element.get_attributes().get('tab_width', '4')),
                    'wrap': element.get_attributes().get('wrap', 'false') == 'true'
                }
            for child in element.get_children():
                result = find_current_document(child)
                if result:
                    return result
            return None
            
        return find_current_document(_kate_instance) or {}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du document actif : {str(e)}")
        return {}

def get_cursor_position() -> Tuple[int, int]:
    """Récupère la position du curseur."""
    if not _kate_instance:
        return (0, 0)
        
    try:
        def find_cursor_position(element: Atspi.Accessible) -> Optional[Tuple[int, int]]:
            if element.get_role() == Atspi.Role.DOCUMENT_FRAME:
                line = int(element.get_attributes().get('cursor_line', '0'))
                column = int(element.get_attributes().get('cursor_column', '0'))
                return (line, column)
            for child in element.get_children():
                result = find_cursor_position(child)
                if result:
                    return result
            return None
            
        return find_cursor_position(_kate_instance) or (0, 0)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la position du curseur : {str(e)}")
        return (0, 0)

def get_selection() -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Récupère la sélection actuelle."""
    if not _kate_instance:
        return ((0, 0), (0, 0))
        
    try:
        def find_selection(element: Atspi.Accessible) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
            if element.get_role() == Atspi.Role.DOCUMENT_FRAME:
                start_line = int(element.get_attributes().get('selection_start_line', '0'))
                start_column = int(element.get_attributes().get('selection_start_column', '0'))
                end_line = int(element.get_attributes().get('selection_end_line', '0'))
                end_column = int(element.get_attributes().get('selection_end_column', '0'))
                return ((start_line, start_column), (end_line, end_column))
            for child in element.get_children():
                result = find_selection(child)
                if result:
                    return result
            return None
            
        return find_selection(_kate_instance) or ((0, 0), (0, 0))
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la sélection : {str(e)}")
        return ((0, 0), (0, 0))

def execute_action(action: str, **kwargs) -> bool:
    """Exécute une action dans Kate."""
    if not _kate_instance:
        return False
        
    try:
        if action == 'new':
            # Créer un nouveau document
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'new' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'open':
            # Ouvrir un document
            path = kwargs.get('path', '')
            if not path:
                return False
                
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'open' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le chemin du fichier
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            child.set_text_contents(path)
                            break
                            
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'save':
            # Enregistrer le document
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'save' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'save_as':
            # Enregistrer le document sous
            path = kwargs.get('path', '')
            if not path:
                return False
                
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'save as' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le chemin du fichier
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            child.set_text_contents(path)
                            break
                            
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'close':
            # Fermer le document
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'close' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'undo':
            # Annuler la dernière action
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'undo' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'redo':
            # Rétablir la dernière action annulée
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'redo' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'cut':
            # Couper la sélection
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'cut' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'copy':
            # Copier la sélection
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'copy' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'paste':
            # Coller le contenu du presse-papiers
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'paste' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'delete':
            # Supprimer la sélection
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'delete' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'select_all':
            # Tout sélectionner
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'select all' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'find':
            # Rechercher du texte
            text = kwargs.get('text', '')
            if not text:
                return False
                
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'find' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le texte à rechercher
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            child.set_text_contents(text)
                            break
                            
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'replace':
            # Remplacer du texte
            find_text = kwargs.get('find_text', '')
            replace_text = kwargs.get('replace_text', '')
            if not find_text or not replace_text:
                return False
                
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'replace' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le texte à rechercher et à remplacer
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            if 'find' in child.get_name().lower():
                                child.set_text_contents(find_text)
                            elif 'replace' in child.get_name().lower():
                                child.set_text_contents(replace_text)
                                
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'goto_line':
            # Aller à une ligne spécifique
            line = kwargs.get('line', 0)
            if line < 0:
                return False
                
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'goto line' in element.get_name().lower()):
                    if not element.do_action(0):  # Action par défaut (clic)
                        return False
                        
                    # Attendre que la boîte de dialogue s'ouvre
                    # Entrer le numéro de ligne
                    for child in element.get_children():
                        if child.get_role() == Atspi.Role.ENTRY:
                            child.set_text_contents(str(line))
                            break
                            
                    # Valider
                    for child in element.get_children():
                        if (child.get_role() == Atspi.Role.PUSH_BUTTON and 
                            'ok' in child.get_name().lower()):
                            return child.do_action(0)
                            
        elif action == 'toggle_terminal':
            # Afficher/masquer le terminal intégré
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'terminal' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'toggle_side_panel':
            # Afficher/masquer le panneau latéral
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'side panel' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
        elif action == 'toggle_fullscreen':
            # Passer en plein écran
            for element in _kate_instance.get_children():
                if (element.get_role() == Atspi.Role.PUSH_BUTTON and 
                    'fullscreen' in element.get_name().lower()):
                    return element.do_action(0)  # Action par défaut (clic)
                    
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