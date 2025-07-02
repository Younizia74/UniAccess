#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion des paramètres système Android via l'Accessibility Service.
Gère l'accès et la modification des paramètres système comme :
- Réseau (WiFi, Bluetooth, Données mobiles)
- Affichage (Luminosité, Rotation, Taille du texte)
- Son (Volume, Mode silencieux, Vibrations)
- Batterie (Mode économie, État de charge)
- Sécurité (Verrouillage, Empreintes)
- Accessibilité (TalkBack, Contraste, Taille des éléments)
"""

import os
import logging
import json
from enum import Enum
from typing import Dict, List, Optional, Union
from gi.repository import GObject, Atspi

# Configuration du logger
logger = logging.getLogger(__name__)

class SettingsCategory(Enum):
    """Catégories de paramètres système"""
    NETWORK = "network"
    DISPLAY = "display"
    SOUND = "sound"
    BATTERY = "battery"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    SYSTEM = "system"
    STORAGE = "storage"
    APPS = "apps"
    USERS = "users"

class NetworkType(Enum):
    """Types de connexion réseau"""
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    MOBILE_DATA = "mobile_data"
    AIRPLANE_MODE = "airplane_mode"
    HOTSPOT = "hotspot"
    VPN = "vpn"

class DisplaySetting(Enum):
    """Paramètres d'affichage"""
    BRIGHTNESS = "brightness"
    AUTO_ROTATE = "auto_rotate"
    TEXT_SIZE = "text_size"
    DISPLAY_SIZE = "display_size"
    NIGHT_MODE = "night_mode"
    SCREEN_TIMEOUT = "screen_timeout"
    SCREEN_RESOLUTION = "screen_resolution"
    REFRESH_RATE = "refresh_rate"

class SoundSetting(Enum):
    """Paramètres sonores"""
    MEDIA_VOLUME = "media_volume"
    RING_VOLUME = "ring_volume"
    ALARM_VOLUME = "alarm_volume"
    VIBRATION = "vibration"
    DO_NOT_DISTURB = "do_not_disturb"
    SOUND_EFFECTS = "sound_effects"

class BatterySetting(Enum):
    """Paramètres de batterie"""
    BATTERY_SAVER = "battery_saver"
    ADAPTIVE_BATTERY = "adaptive_battery"
    BATTERY_PERCENTAGE = "battery_percentage"
    POWER_MANAGEMENT = "power_management"

class SecuritySetting(Enum):
    """Paramètres de sécurité"""
    SCREEN_LOCK = "screen_lock"
    FINGERPRINT = "fingerprint"
    FACE_UNLOCK = "face_unlock"
    SMART_LOCK = "smart_lock"
    ENCRYPTION = "encryption"
    SECURITY_PATCH = "security_patch"

class AccessibilitySetting(Enum):
    """Paramètres d'accessibilité"""
    TALKBACK = "talkback"
    CONTRAST = "contrast"
    TEXT_SIZE = "text_size"
    TOUCH_TARGET_SIZE = "touch_target_size"
    COLOR_CORRECTION = "color_correction"
    COLOR_INVERSION = "color_inversion"
    ANIMATION_SCALE = "animation_scale"

# Variables globales
_settings_cache = {}
_current_settings = None
_settings_service = None
_initialized = False

def initialize() -> bool:
    """
    Initialise le module des paramètres système.
    Retourne True si l'initialisation réussit, False sinon.
    """
    global _initialized, _settings_service
    
    try:
        if _initialized:
            return True
            
        # Initialisation du service d'accessibilité
        _settings_service = Atspi.Accessible()
        if not _settings_service:
            logger.error("Impossible d'initialiser le service d'accessibilité")
            return False
            
        # Chargement initial des paramètres
        _load_all_settings()
        
        _initialized = True
        logger.info("Module des paramètres système initialisé avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du module des paramètres: {str(e)}")
        return False

def cleanup() -> None:
    """Nettoie les ressources du module des paramètres"""
    global _initialized, _settings_cache, _current_settings, _settings_service
    
    try:
        if not _initialized:
            return
            
        _settings_cache.clear()
        _current_settings = None
        _settings_service = None
        _initialized = False
        
        logger.info("Module des paramètres système nettoyé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du module des paramètres: {str(e)}")

def _load_all_settings() -> None:
    """Charge tous les paramètres système dans le cache"""
    global _settings_cache
    
    try:
        for category in SettingsCategory:
            _settings_cache[category.value] = _get_category_settings(category)
            
        logger.debug("Tous les paramètres système chargés dans le cache")
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des paramètres: {str(e)}")

def _get_category_settings(category: SettingsCategory) -> Dict:
    """
    Récupère les paramètres d'une catégorie spécifique.
    
    Args:
        category: La catégorie de paramètres à récupérer
        
    Returns:
        Dict contenant les paramètres de la catégorie
    """
    try:
        # Navigation dans l'arbre d'accessibilité pour trouver la catégorie
        category_node = _find_settings_category(category)
        if not category_node:
            return {}
            
        # Récupération des paramètres de la catégorie
        settings = {}
        for child in category_node.get_children():
            if child.get_role() == Atspi.Role.TOGGLE_BUTTON:
                settings[child.get_name()] = child.get_state().contains(Atspi.StateType.CHECKED)
            elif child.get_role() == Atspi.Role.SLIDER:
                settings[child.get_name()] = child.get_value()
            elif child.get_role() == Atspi.Role.COMBO_BOX:
                settings[child.get_name()] = child.get_text()
                
        return settings
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres {category.value}: {str(e)}")
        return {}

def _find_settings_category(category: SettingsCategory) -> Optional[Atspi.Accessible]:
    """
    Trouve le nœud d'accessibilité correspondant à une catégorie de paramètres.
    
    Args:
        category: La catégorie à trouver
        
    Returns:
        Le nœud d'accessibilité de la catégorie ou None si non trouvé
    """
    try:
        # Recherche de l'application Paramètres
        settings_app = _find_settings_app()
        if not settings_app:
            return None
            
        # Recherche de la catégorie dans l'arbre
        for node in settings_app.get_children():
            if (node.get_role() == Atspi.Role.LIST_ITEM and 
                category.value.lower() in node.get_name().lower()):
                return node
                
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de la catégorie {category.value}: {str(e)}")
        return None

def _find_settings_app() -> Optional[Atspi.Accessible]:
    """
    Trouve l'application Paramètres dans l'arbre d'accessibilité.
    
    Returns:
        Le nœud d'accessibilité de l'application Paramètres ou None si non trouvé
    """
    try:
        desktop = Atspi.get_desktop(0)
        for app in desktop.get_children():
            if "paramètres" in app.get_name().lower():
                return app
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de l'application Paramètres: {str(e)}")
        return None

def get_setting(category: SettingsCategory, setting_name: str) -> Union[bool, int, str, None]:
    """
    Récupère la valeur d'un paramètre spécifique.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        La valeur du paramètre ou None si non trouvé
    """
    try:
        if not _initialized:
            if not initialize():
                return None
                
        category_settings = _settings_cache.get(category.value, {})
        return category_settings.get(setting_name)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du paramètre {setting_name}: {str(e)}")
        return None

def set_setting(category: SettingsCategory, setting_name: str, value: Union[bool, int, str]) -> bool:
    """
    Modifie la valeur d'un paramètre spécifique.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        value: La nouvelle valeur
        
    Returns:
        True si la modification réussit, False sinon
    """
    try:
        if not _initialized:
            if not initialize():
                return False
                
        # Trouver le nœud du paramètre
        category_node = _find_settings_category(category)
        if not category_node:
            return False
            
        # Trouver le contrôle du paramètre
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return False
            
        # Modifier la valeur selon le type de contrôle
        if setting_node.get_role() == Atspi.Role.TOGGLE_BUTTON:
            if isinstance(value, bool):
                if value != setting_node.get_state().contains(Atspi.StateType.CHECKED):
                    setting_node.do_action(0)  # Action de basculement
        elif setting_node.get_role() == Atspi.Role.SLIDER:
            if isinstance(value, (int, float)):
                setting_node.set_value(value)
        elif setting_node.get_role() == Atspi.Role.COMBO_BOX:
            if isinstance(value, str):
                setting_node.set_text(value)
                
        # Mettre à jour le cache
        _settings_cache[category.value][setting_name] = value
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la modification du paramètre {setting_name}: {str(e)}")
        return False

def _find_setting_control(category_node: Atspi.Accessible, setting_name: str) -> Optional[Atspi.Accessible]:
    """
    Trouve le contrôle d'un paramètre spécifique dans une catégorie.
    
    Args:
        category_node: Le nœud de la catégorie
        setting_name: Le nom du paramètre
        
    Returns:
        Le nœud du contrôle ou None si non trouvé
    """
    try:
        for node in category_node.get_children():
            if setting_name.lower() in node.get_name().lower():
                return node
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du contrôle {setting_name}: {str(e)}")
        return None

def get_all_settings() -> Dict:
    """
    Récupère tous les paramètres système.
    
    Returns:
        Dict contenant tous les paramètres par catégorie
    """
    try:
        if not _initialized:
            if not initialize():
                return {}
                
        return _settings_cache.copy()
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de tous les paramètres: {str(e)}")
        return {}

def get_category_settings(category: SettingsCategory) -> Dict:
    """
    Récupère tous les paramètres d'une catégorie.
    
    Args:
        category: La catégorie de paramètres
        
    Returns:
        Dict contenant les paramètres de la catégorie
    """
    try:
        if not _initialized:
            if not initialize():
                return {}
                
        return _settings_cache.get(category.value, {}).copy()
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres {category.value}: {str(e)}")
        return {}

def reset_setting(category: SettingsCategory, setting_name: str) -> bool:
    """
    Réinitialise un paramètre à sa valeur par défaut.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        True si la réinitialisation réussit, False sinon
    """
    try:
        # Trouver le nœud du paramètre
        category_node = _find_settings_category(category)
        if not category_node:
            return False
            
        # Trouver le contrôle du paramètre
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return False
            
        # Trouver et cliquer sur le bouton de réinitialisation
        reset_button = _find_reset_button(setting_node)
        if reset_button:
            reset_button.do_action(0)  # Action de clic
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du paramètre {setting_name}: {str(e)}")
        return False

def _find_reset_button(setting_node: Atspi.Accessible) -> Optional[Atspi.Accessible]:
    """
    Trouve le bouton de réinitialisation pour un paramètre.
    
    Args:
        setting_node: Le nœud du paramètre
        
    Returns:
        Le nœud du bouton de réinitialisation ou None si non trouvé
    """
    try:
        for node in setting_node.get_children():
            if (node.get_role() == Atspi.Role.PUSH_BUTTON and 
                "réinitialiser" in node.get_name().lower()):
                return node
        return None
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche du bouton de réinitialisation: {str(e)}")
        return None

def export_settings(file_path: str) -> bool:
    """
    Exporte tous les paramètres dans un fichier JSON.
    
    Args:
        file_path: Le chemin du fichier d'export
        
    Returns:
        True si l'export réussit, False sinon
    """
    try:
        if not _initialized:
            if not initialize():
                return False
                
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(_settings_cache, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Paramètres exportés avec succès dans {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des paramètres: {str(e)}")
        return False

def import_settings(file_path: str) -> bool:
    """
    Importe les paramètres depuis un fichier JSON.
    
    Args:
        file_path: Le chemin du fichier d'import
        
    Returns:
        True si l'import réussit, False sinon
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        if not isinstance(settings, dict):
            logger.error("Format de fichier invalide")
            return False
            
        # Appliquer les paramètres
        for category, category_settings in settings.items():
            try:
                category_enum = SettingsCategory(category)
                for setting_name, value in category_settings.items():
                    set_setting(category_enum, setting_name, value)
            except ValueError:
                logger.warning(f"Catégorie inconnue ignorée: {category}")
                continue
                
        logger.info(f"Paramètres importés avec succès depuis {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import des paramètres: {str(e)}")
        return False

def get_available_settings() -> Dict[str, List[str]]:
    """
    Récupère la liste des paramètres disponibles par catégorie.
    
    Returns:
        Dict contenant les paramètres disponibles par catégorie
    """
    try:
        if not _initialized:
            if not initialize():
                return {}
                
        available = {}
        for category in SettingsCategory:
            category_node = _find_settings_category(category)
            if category_node:
                settings = []
                for node in category_node.get_children():
                    if node.get_role() in (Atspi.Role.TOGGLE_BUTTON, 
                                         Atspi.Role.SLIDER,
                                         Atspi.Role.COMBO_BOX):
                        settings.append(node.get_name())
                available[category.value] = settings
                
        return available
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des paramètres disponibles: {str(e)}")
        return {}

def is_setting_available(category: SettingsCategory, setting_name: str) -> bool:
    """
    Vérifie si un paramètre est disponible.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        True si le paramètre est disponible, False sinon
    """
    try:
        if not _initialized:
            if not initialize():
                return False
                
        category_node = _find_settings_category(category)
        if not category_node:
            return False
            
        return _find_setting_control(category_node, setting_name) is not None
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la disponibilité du paramètre {setting_name}: {str(e)}")
        return False

def get_setting_description(category: SettingsCategory, setting_name: str) -> Optional[str]:
    """
    Récupère la description d'un paramètre.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        La description du paramètre ou None si non trouvée
    """
    try:
        if not _initialized:
            if not initialize():
                return None
                
        category_node = _find_settings_category(category)
        if not category_node:
            return None
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return None
            
        # Recherche de la description dans les attributs ou les enfants
        description = setting_node.get_description()
        if not description:
            for node in setting_node.get_children():
                if node.get_role() == Atspi.Role.LABEL:
                    description = node.get_text()
                    break
                    
        return description
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la description du paramètre {setting_name}: {str(e)}")
        return None

def get_setting_type(category: SettingsCategory, setting_name: str) -> Optional[str]:
    """
    Récupère le type d'un paramètre (booléen, entier, texte, etc.).
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        Le type du paramètre ou None si non trouvé
    """
    try:
        if not _initialized:
            if not initialize():
                return None
                
        category_node = _find_settings_category(category)
        if not category_node:
            return None
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return None
            
        role = setting_node.get_role()
        if role == Atspi.Role.TOGGLE_BUTTON:
            return "boolean"
        elif role == Atspi.Role.SLIDER:
            return "number"
        elif role == Atspi.Role.COMBO_BOX:
            return "string"
        else:
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du type du paramètre {setting_name}: {str(e)}")
        return None

def get_setting_range(category: SettingsCategory, setting_name: str) -> Optional[Dict[str, Union[int, float]]]:
    """
    Récupère les valeurs min/max d'un paramètre numérique.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        Dict contenant min et max ou None si non applicable
    """
    try:
        if not _initialized:
            if not initialize():
                return None
                
        category_node = _find_settings_category(category)
        if not category_node:
            return None
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node or setting_node.get_role() != Atspi.Role.SLIDER:
            return None
            
        return {
            "min": setting_node.get_minimum_value(),
            "max": setting_node.get_maximum_value()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des limites du paramètre {setting_name}: {str(e)}")
        return None

def get_setting_options(category: SettingsCategory, setting_name: str) -> Optional[List[str]]:
    """
    Récupère les options disponibles pour un paramètre de type liste.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        Liste des options disponibles ou None si non applicable
    """
    try:
        if not _initialized:
            if not initialize():
                return None
                
        category_node = _find_settings_category(category)
        if not category_node:
            return None
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node or setting_node.get_role() != Atspi.Role.COMBO_BOX:
            return None
            
        options = []
        for node in setting_node.get_children():
            if node.get_role() == Atspi.Role.LIST_ITEM:
                options.append(node.get_text())
                
        return options
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des options du paramètre {setting_name}: {str(e)}")
        return None

def monitor_setting(category: SettingsCategory, setting_name: str, callback: callable) -> bool:
    """
    Surveille les changements d'un paramètre.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        callback: Fonction appelée lors d'un changement
        
    Returns:
        True si la surveillance est activée, False sinon
    """
    try:
        if not _initialized:
            if not initialize():
                return False
                
        category_node = _find_settings_category(category)
        if not category_node:
            return False
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return False
            
        # Ajouter un listener pour les changements d'état
        listener = Atspi.EventListener.new(callback)
        setting_node.add_state_change_listener(listener)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la mise en surveillance du paramètre {setting_name}: {str(e)}")
        return False

def stop_monitoring(category: SettingsCategory, setting_name: str) -> bool:
    """
    Arrête la surveillance d'un paramètre.
    
    Args:
        category: La catégorie du paramètre
        setting_name: Le nom du paramètre
        
    Returns:
        True si l'arrêt réussit, False sinon
    """
    try:
        if not _initialized:
            return False
            
        category_node = _find_settings_category(category)
        if not category_node:
            return False
            
        setting_node = _find_setting_control(category_node, setting_name)
        if not setting_node:
            return False
            
        # Supprimer tous les listeners
        setting_node.remove_state_change_listeners()
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt de la surveillance du paramètre {setting_name}: {str(e)}")
        return False 