#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion des applications système Android via l'Accessibility Service.
Gère l'accès et le contrôle des applications système comme :
- Paramètres
- Téléphone
- Contacts
- Messages
- Appareil photo
- Galerie
- Horloge
- Calculatrice
- etc.
"""

import os
import logging
import json
from enum import Enum
from typing import Dict, List, Optional, Union, Tuple
from gi.repository import GObject, Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

class SystemAppType(Enum):
    """Types d'applications système"""
    SETTINGS = "settings"
    PHONE = "phone"
    CONTACTS = "contacts"
    MESSAGES = "messages"
    CAMERA = "camera"
    GALLERY = "gallery"
    CLOCK = "clock"
    CALCULATOR = "calculator"
    CALENDAR = "calendar"
    BROWSER = "browser"
    EMAIL = "email"
    MAPS = "maps"
    PLAY_STORE = "play_store"
    MUSIC = "music"
    WEATHER = "weather"
    NOTES = "notes"
    FILES = "files"
    DOWNLOADS = "downloads"
    SHARE = "share"
    SCREENSHOT = "screenshot"
    SCREEN_RECORD = "screen_record"
    VOICE_RECORDER = "voice_recorder"
    FM_RADIO = "fm_radio"
    COMPASS = "compass"
    FLASHLIGHT = "flashlight"
    HEALTH = "health"
    PAY = "pay"
    WALLET = "wallet"
    BACKUP = "backup"
    SECURITY = "security"

class AppState(Enum):
    """États possibles d'une application"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRASHED = "crashed"
    UNKNOWN = "unknown"

class AppPermission(Enum):
    """Permissions possibles pour une application"""
    CAMERA = "camera"
    MICROPHONE = "microphone"
    LOCATION = "location"
    STORAGE = "storage"
    CONTACTS = "contacts"
    PHONE = "phone"
    SMS = "sms"
    CALENDAR = "calendar"
    SENSORS = "sensors"
    NOTIFICATIONS = "notifications"

# Variables globales
_apps_cache = {}
_current_app = None
_app_service = None
_initialized = False
_permission_cache = {}

def initialize() -> bool:
    """
    Initialise le module de gestion des applications système.
    Retourne True si l'initialisation réussit, False sinon.
    """
    global _initialized, _app_service
    
    try:
        if _initialized:
            return True
            
        # Initialisation du service d'accessibilité
        _app_service = Atspi.Accessible()
        if not _app_service:
            logger.error("Impossible d'initialiser le service d'accessibilité")
            return False
            
        # Chargement initial des applications
        _load_all_apps()
        
        # Chargement des permissions
        _load_app_permissions()
        
        _initialized = True
        logger.info("Module de gestion des applications système initialisé avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du module des applications: {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources du module des applications"""
    global _initialized, _apps_cache, _current_app, _app_service, _permission_cache
    
    try:
        if not _initialized:
            return
            
        _apps_cache.clear()
        _permission_cache.clear()
        _current_app = None
        _app_service = None
        _initialized = False
        
        logger.info("Module de gestion des applications système nettoyé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du module des applications: {str(e)}")

def _load_all_apps() -> None:
    """Charge toutes les applications système dans le cache"""
    global _apps_cache
    
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop.get_children():
            app_type = _get_app_type(app)
            if app_type:
                _apps_cache[app_type.value] = {
                    "name": app.get_name(),
                    "state": _get_app_state(app),
                    "package": _get_app_package(app),
                    "version": _get_app_version(app),
                    "node": app
                }
                
        logger.debug("Toutes les applications système chargées dans le cache")
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des applications: {str(e)}")

def _load_app_permissions() -> None:
    """Charge les permissions de toutes les applications"""
    global _permission_cache
    
    try:
        for app_type, app_info in _apps_cache.items():
            app_node = app_info["node"]
            permissions = _get_app_permissions(app_node)
            if permissions:
                _permission_cache[app_type] = permissions
                
        logger.debug("Permissions des applications chargées dans le cache")
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des permissions: {str(e)}")

def _get_app_type(app_node: Atspi.Accessible) -> Optional[SystemAppType]:
    """
    Détermine le type d'une application à partir de son nœud.
    
    Args:
        app_node: Le nœud de l'application
        
    Returns:
        Le type de l'application ou None si non reconnue
    """
    try:
        app_name = app_node.get_name().lower()
        package = _get_app_package(app_node)
        
        # Mapping des noms/paquets vers les types d'applications
        app_mapping = {
            "paramètres": SystemAppType.SETTINGS,
            "téléphone": SystemAppType.PHONE,
            "contacts": SystemAppType.CONTACTS,
            "messages": SystemAppType.MESSAGES,
            "appareil photo": SystemAppType.CAMERA,
            "galerie": SystemAppType.GALLERY,
            "horloge": SystemAppType.CLOCK,
            "calculatrice": SystemAppType.CALCULATOR,
            "calendrier": SystemAppType.CALENDAR,
            "navigateur": SystemAppType.BROWSER,
            "gmail": SystemAppType.EMAIL,
            "maps": SystemAppType.MAPS,
            "play store": SystemAppType.PLAY_STORE,
            "musique": SystemAppType.MUSIC,
            "météo": SystemAppType.WEATHER,
            "notes": SystemAppType.NOTES,
            "fichiers": SystemAppType.FILES,
            "téléchargements": SystemAppType.DOWNLOADS,
            "partager": SystemAppType.SHARE,
            "capture d'écran": SystemAppType.SCREENSHOT,
            "enregistrement d'écran": SystemAppType.SCREEN_RECORD,
            "enregistreur vocal": SystemAppType.VOICE_RECORDER,
            "radio fm": SystemAppType.FM_RADIO,
            "boussole": SystemAppType.COMPASS,
            "lampe de poche": SystemAppType.FLASHLIGHT,
            "santé": SystemAppType.HEALTH,
            "pay": SystemAppType.PAY,
            "portefeuille": SystemAppType.WALLET,
            "sauvegarde": SystemAppType.BACKUP,
            "sécurité": SystemAppType.SECURITY
        }
        
        # Recherche par nom
        for name, app_type in app_mapping.items():
            if name in app_name:
                return app_type
                
        # Recherche par package
        if package:
            package_mapping = {
                "com.android.settings": SystemAppType.SETTINGS,
                "com.android.phone": SystemAppType.PHONE,
                "com.android.contacts": SystemAppType.CONTACTS,
                "com.android.messaging": SystemAppType.MESSAGES,
                "com.android.camera": SystemAppType.CAMERA,
                "com.android.gallery": SystemAppType.GALLERY,
                "com.android.deskclock": SystemAppType.CLOCK,
                "com.android.calculator": SystemAppType.CALCULATOR,
                "com.android.calendar": SystemAppType.CALENDAR,
                "com.android.chrome": SystemAppType.BROWSER,
                "com.google.android.gm": SystemAppType.EMAIL,
                "com.google.android.apps.maps": SystemAppType.MAPS,
                "com.android.vending": SystemAppType.PLAY_STORE,
                "com.google.android.music": SystemAppType.MUSIC,
                "com.google.android.apps.weather": SystemAppType.WEATHER,
                "com.google.android.keep": SystemAppType.NOTES,
                "com.android.documentsui": SystemAppType.FILES,
                "com.android.providers.downloads": SystemAppType.DOWNLOADS,
                "com.android.share": SystemAppType.SHARE,
                "com.android.systemui.screenshot": SystemAppType.SCREENSHOT,
                "com.android.systemui.screenrecord": SystemAppType.SCREEN_RECORD,
                "com.android.soundrecorder": SystemAppType.VOICE_RECORDER,
                "com.android.fmradio": SystemAppType.FM_RADIO,
                "com.android.compass": SystemAppType.COMPASS,
                "com.android.flashlight": SystemAppType.FLASHLIGHT,
                "com.google.android.apps.fitness": SystemAppType.HEALTH,
                "com.google.android.apps.wallet": SystemAppType.WALLET,
                "com.google.android.backup": SystemAppType.BACKUP,
                "com.google.android.apps.security": SystemAppType.SECURITY
            }
            
            for pkg, app_type in package_mapping.items():
                if pkg in package:
                    return app_type
                    
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la détermination du type d'application: {str(e)}")
        return None

def _get_app_state(app_node: Atspi.Accessible) -> AppState:
    """
    Détermine l'état d'une application à partir de son nœud.
    
    Args:
        app_node: Le nœud de l'application
        
    Returns:
        L'état de l'application
    """
    try:
        if not app_node:
            return AppState.UNKNOWN
            
        # Vérification de l'état via les attributs d'accessibilité
        if app_node.get_state().contains(Atspi.StateType.ACTIVE):
            return AppState.RUNNING
        elif app_node.get_state().contains(Atspi.StateType.SENSITIVE):
            return AppState.PAUSED
        elif app_node.get_state().contains(Atspi.StateType.DEFUNCT):
            return AppState.CRASHED
        else:
            return AppState.STOPPED
            
    except Exception as e:
        logger.error(f"Erreur lors de la détermination de l'état de l'application: {str(e)}")
        return AppState.UNKNOWN

def _get_app_package(app_node: Atspi.Accessible) -> Optional[str]:
    """
    Récupère le package d'une application.
    
    Args:
        app_node: Le nœud de l'application
        
    Returns:
        Le package de l'application ou None si non trouvé
    """
    try:
        if not app_node:
            return None
            
        # Recherche du package dans les attributs
        package = app_node.get_attributes().get("package")
        if package:
            return package
            
        # Recherche dans les enfants
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.LABEL:
                text = child.get_text()
                if text and "." in text:
                    return text
                    
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du package de l'application: {str(e)}")
        return None

def _get_app_version(app_node: Atspi.Accessible) -> Optional[str]:
    """
    Récupère la version d'une application.
    
    Args:
        app_node: Le nœud de l'application
        
    Returns:
        La version de l'application ou None si non trouvée
    """
    try:
        if not app_node:
            return None
            
        # Recherche de la version dans les attributs
        version = app_node.get_attributes().get("version")
        if version:
            return version
            
        # Recherche dans les enfants
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.LABEL:
                text = child.get_text()
                if text and any(c.isdigit() for c in text):
                    return text
                    
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la version de l'application: {str(e)}")
        return None

def _get_app_permissions(app_node: Atspi.Accessible) -> List[AppPermission]:
    """
    Récupère les permissions d'une application.
    
    Args:
        app_node: Le nœud de l'application
        
    Returns:
        Liste des permissions de l'application
    """
    try:
        if not app_node:
            return []
            
        permissions = []
        
        # Recherche des permissions dans les attributs
        attrs = app_node.get_attributes()
        if attrs:
            for perm in AppPermission:
                if perm.value in attrs.get("permissions", "").lower():
                    permissions.append(perm)
                    
        # Recherche dans les enfants
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.LIST_ITEM:
                text = child.get_text().lower()
                for perm in AppPermission:
                    if perm.value in text and perm not in permissions:
                        permissions.append(perm)
                        
        return permissions
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des permissions de l'application: {str(e)}")
        return []

def get_app(app_type: Union[str, SystemAppType]) -> Optional[Dict]:
    """
    Récupère les informations d'une application système.
    
    Args:
        app_type: Le type d'application (chaîne ou énumération)
        
    Returns:
        Un dictionnaire contenant les informations de l'application ou None si non trouvée
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        return _apps_cache.get(app_type.value)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'application {app_type}: {str(e)}")
        return None

def get_all_apps() -> Dict[str, Dict]:
    """
    Récupère toutes les applications système.
    
    Returns:
        Un dictionnaire contenant toutes les applications système
    """
    return _apps_cache.copy()

def get_running_apps() -> Dict[str, Dict]:
    """
    Récupère toutes les applications en cours d'exécution.
    
    Returns:
        Un dictionnaire contenant les applications en cours d'exécution
    """
    return {
        app_type: app_info 
        for app_type, app_info in _apps_cache.items()
        if app_info["state"] == AppState.RUNNING
    }

def get_current_app() -> Optional[Dict]:
    """
    Récupère l'application actuellement active.
    
    Returns:
        Un dictionnaire contenant les informations de l'application active ou None
    """
    global _current_app
    
    try:
        if not _current_app:
            desktop = Atspi.get_desktop(0)
            focused = desktop.get_focused()
            if focused:
                app_node = focused.get_application()
                if app_node:
                    app_type = _get_app_type(app_node)
                    if app_type:
                        _current_app = _apps_cache.get(app_type.value)
                        
        return _current_app
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'application active: {str(e)}")
        return None

def launch_app(app_type: Union[str, SystemAppType]) -> bool:
    """
    Lance une application système.
    
    Args:
        app_type: Le type d'application à lancer
        
    Returns:
        True si l'application a été lancée avec succès, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Tentative de lancement via le service d'accessibilité
        if app_node.do_action(0):  # Action 0 = launch
            logger.info(f"Application {app_type.value} lancée avec succès")
            return True
            
        # Fallback: recherche du bouton de lancement
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.PUSH_BUTTON:
                if child.do_action(0):
                    logger.info(f"Application {app_type.value} lancée via bouton")
                    return True
                    
        logger.error(f"Impossible de lancer l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application {app_type}: {str(e)}")
        return False

def stop_app(app_type: Union[str, SystemAppType]) -> bool:
    """
    Arrête une application système.
    
    Args:
        app_type: Le type d'application à arrêter
        
    Returns:
        True si l'application a été arrêtée avec succès, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Tentative d'arrêt via le service d'accessibilité
        if app_node.do_action(1):  # Action 1 = stop
            logger.info(f"Application {app_type.value} arrêtée avec succès")
            return True
            
        # Fallback: recherche du bouton d'arrêt
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.PUSH_BUTTON:
                if "arrêter" in child.get_name().lower() or "stop" in child.get_name().lower():
                    if child.do_action(0):
                        logger.info(f"Application {app_type.value} arrêtée via bouton")
                        return True
                        
        logger.error(f"Impossible d'arrêter l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt de l'application {app_type}: {str(e)}")
        return False

def pause_app(app_type: Union[str, SystemAppType]) -> bool:
    """
    Met en pause une application système.
    
    Args:
        app_type: Le type d'application à mettre en pause
        
    Returns:
        True si l'application a été mise en pause avec succès, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Tentative de mise en pause via le service d'accessibilité
        if app_node.do_action(2):  # Action 2 = pause
            logger.info(f"Application {app_type.value} mise en pause avec succès")
            return True
            
        # Fallback: recherche du bouton de mise en pause
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.PUSH_BUTTON:
                if "pause" in child.get_name().lower():
                    if child.do_action(0):
                        logger.info(f"Application {app_type.value} mise en pause via bouton")
                        return True
                        
        logger.error(f"Impossible de mettre en pause l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise en pause de l'application {app_type}: {str(e)}")
        return False

def resume_app(app_type: Union[str, SystemAppType]) -> bool:
    """
    Reprend une application système en pause.
    
    Args:
        app_type: Le type d'application à reprendre
        
    Returns:
        True si l'application a été reprise avec succès, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Tentative de reprise via le service d'accessibilité
        if app_node.do_action(3):  # Action 3 = resume
            logger.info(f"Application {app_type.value} reprise avec succès")
            return True
            
        # Fallback: recherche du bouton de reprise
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.PUSH_BUTTON:
                if "reprendre" in child.get_name().lower() or "resume" in child.get_name().lower():
                    if child.do_action(0):
                        logger.info(f"Application {app_type.value} reprise via bouton")
                        return True
                        
        logger.error(f"Impossible de reprendre l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la reprise de l'application {app_type}: {str(e)}")
        return False

def get_app_permissions(app_type: Union[str, SystemAppType]) -> List[AppPermission]:
    """
    Récupère les permissions d'une application.
    
    Args:
        app_type: Le type d'application
        
    Returns:
        Liste des permissions de l'application
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        return _permission_cache.get(app_type.value, [])
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des permissions de l'application {app_type}: {str(e)}")
        return []

def has_permission(app_type: Union[str, SystemAppType], permission: Union[str, AppPermission]) -> bool:
    """
    Vérifie si une application a une permission spécifique.
    
    Args:
        app_type: Le type d'application
        permission: La permission à vérifier
        
    Returns:
        True si l'application a la permission, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        if isinstance(permission, str):
            permission = AppPermission(permission)
            
        permissions = get_app_permissions(app_type)
        return permission in permissions
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la permission {permission} pour l'application {app_type}: {str(e)}")
        return False

def request_permission(app_type: Union[str, SystemAppType], permission: Union[str, AppPermission]) -> bool:
    """
    Demande une permission pour une application.
    
    Args:
        app_type: Le type d'application
        permission: La permission à demander
        
    Returns:
        True si la permission a été accordée, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        if isinstance(permission, str):
            permission = AppPermission(permission)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Recherche du dialogue de permission
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.DIALOG:
                # Recherche du bouton d'accord
                for button in child.get_children():
                    if button.get_role() == Atspi.Role.PUSH_BUTTON:
                        if "accepter" in button.get_name().lower() or "allow" in button.get_name().lower():
                            if button.do_action(0):
                                logger.info(f"Permission {permission.value} accordée pour l'application {app_type.value}")
                                return True
                                
        logger.error(f"Impossible de demander la permission {permission.value} pour l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la demande de permission {permission} pour l'application {app_type}: {str(e)}")
        return False

def revoke_permission(app_type: Union[str, SystemAppType], permission: Union[str, AppPermission]) -> bool:
    """
    Révoque une permission d'une application.
    
    Args:
        app_type: Le type d'application
        permission: La permission à révoquer
        
    Returns:
        True si la permission a été révoquée, False sinon
    """
    try:
        if isinstance(app_type, str):
            app_type = SystemAppType(app_type)
            
        if isinstance(permission, str):
            permission = AppPermission(permission)
            
        app_info = _apps_cache.get(app_type.value)
        if not app_info:
            logger.error(f"Application {app_type.value} non trouvée")
            return False
            
        app_node = app_info["node"]
        if not app_node:
            logger.error(f"Nœud de l'application {app_type.value} non trouvé")
            return False
            
        # Recherche du dialogue de permission
        for child in app_node.get_children():
            if child.get_role() == Atspi.Role.DIALOG:
                # Recherche du bouton de révocation
                for button in child.get_children():
                    if button.get_role() == Atspi.Role.PUSH_BUTTON:
                        if "révoquer" in button.get_name().lower() or "revoke" in button.get_name().lower():
                            if button.do_action(0):
                                logger.info(f"Permission {permission.value} révoquée pour l'application {app_type.value}")
                                return True
                                
        logger.error(f"Impossible de révoquer la permission {permission.value} pour l'application {app_type.value}")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la révocation de la permission {permission} pour l'application {app_type}: {str(e)}")
        return False 