#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de configuration pour NVDA-Linux
=====================================

Gère le chargement et la sauvegarde des préférences utilisateur,
incluant les paramètres d'IA et d'accessibilité.
"""

import os
import json
import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration par défaut
DEFAULT_CONFIG = {
    "general": {
        "language": "fr",
        "startup_sound": True,
        "debug_mode": False,
        "log_level": "INFO"
    },
    "speech": {
        "enabled": True,
        "voice": "fr",
        "rate": 50,
        "pitch": 50,
        "volume": 100,
        "punctuation_level": "some"
    },
    "braille": {
        "enabled": False,
        "display": "auto",
        "translation_table": "fr-bfu-comp8.utb",
        "cursor_blink": True,
        "cursor_style": "block"
    },
    "keyboard": {
        "caps_lock_as_modifier": True,
        "num_lock_as_modifier": False,
        "keyboard_layout": "fr",
        "key_repeat_delay": 500,
        "key_repeat_rate": 30
    },
    "sound": {
        "enabled": True,
        "volume": 100,
        "beep_volume": 50,
        "beep_frequency": 1000
    },
    "interface": {
        "theme": "system",
        "high_contrast": False,
        "font_size": "medium",
        "show_toolbar": True
    },
    "ai": {
        "enabled": True,
        "device": "auto",  # auto, cpu, cuda
        "models_dir": "~/.nvda_linux/models",
        "cache_size": 1024,  # MB
        "vision": {
            "enabled": True,
            "image_captioning": True,
            "object_detection": True,
            "scene_understanding": True,
            "confidence_threshold": 0.7
        },
        "nlp": {
            "enabled": True,
            "text_summarization": True,
            "translation": True,
            "question_answering": True,
            "max_text_length": 512
        },
        "ar": {
            "enabled": True,
            "depth_estimation": True,
            "pose_estimation": True,
            "navigation_guidance": True,
            "update_interval": 1.0  # secondes
        }
    },
    "platforms": {
        "linux": {
            "enabled": True,
            "atspi": True,
            "speech_dispatcher": True,
            "brltty": True
        },
        "windows": {
            "enabled": False,
            "wine": False,
            "proton": False,
            "nvda_path": ""
        },
        "android": {
            "enabled": False,
            "accessibility_service": True,
            "speech_service": True,
            "braille_service": True
        }
    },
    "apps": {
        "browsers": {
            "firefox": True,
            "chrome": True,
            "edge": True,
            "electron": True
        },
        "office": {
            "libreoffice": True,
            "onlyoffice": True,
            "microsoft_office": False
        },
        "games": {
            "enabled": True,
            "steam": True,
            "proton": True,
            "wine": True,
            "native": True
        }
    }
}

# Instance du parser de configuration
_config = configparser.ConfigParser()

def initialize(config_path: Optional[str] = None) -> bool:
    """Initialise la configuration"""
    try:
        global _config
        
        # Définit les valeurs par défaut
        for section, options in DEFAULT_CONFIG.items():
            if not _config.has_section(section):
                _config.add_section(section)
            for option, value in options.items():
                if isinstance(value, dict):
                    # Gère les sous-sections
                    for sub_option, sub_value in value.items():
                        _config.set(section, f"{option}.{sub_option}", str(sub_value))
                else:
                    _config.set(section, option, str(value))
        
        # Charge la configuration si un chemin est fourni
        if config_path:
            if os.path.exists(config_path):
                _config.read(config_path)
            else:
                # Crée le répertoire si nécessaire
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                # Sauvegarde la configuration par défaut
                with open(config_path, 'w') as f:
                    _config.write(f)
        
        logger.info("Configuration initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la configuration: {str(e)}")
        return False

def get(section: str, option: str, default: Any = None) -> Any:
    """Récupère une valeur de configuration"""
    try:
        if "." in option:
            # Gère les options avec sous-sections
            main_option, sub_option = option.split(".", 1)
            value = _config.get(section, f"{main_option}.{sub_option}", fallback=str(default))
        else:
            value = _config.get(section, option, fallback=str(default))
        
        # Convertit la valeur au type approprié
        if isinstance(default, bool):
            return _config.getboolean(section, option, fallback=default)
        elif isinstance(default, int):
            return _config.getint(section, option, fallback=default)
        elif isinstance(default, float):
            return _config.getfloat(section, option, fallback=default)
        else:
            return value
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration {section}.{option}: {str(e)}")
        return default

def set(section: str, option: str, value: Any) -> bool:
    """Définit une valeur de configuration"""
    try:
        if not _config.has_section(section):
            _config.add_section(section)
        
        if "." in option:
            # Gère les options avec sous-sections
            main_option, sub_option = option.split(".", 1)
            _config.set(section, f"{main_option}.{sub_option}", str(value))
        else:
            _config.set(section, option, str(value))
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la définition de la configuration {section}.{option}: {str(e)}")
        return False

def save(config_path: str) -> bool:
    """Sauvegarde la configuration"""
    try:
        with open(config_path, 'w') as f:
            _config.write(f)
        logger.info(f"Configuration sauvegardée dans {config_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
        return False

def get_all() -> Dict[str, Dict[str, Any]]:
    """Récupère toute la configuration"""
    try:
        config_dict = {}
        for section in _config.sections():
            config_dict[section] = {}
            for option in _config.options(section):
                if "." in option:
                    # Gère les options avec sous-sections
                    main_option, sub_option = option.split(".", 1)
                    if main_option not in config_dict[section]:
                        config_dict[section][main_option] = {}
                    config_dict[section][main_option][sub_option] = get(section, option)
                else:
                    config_dict[section][option] = get(section, option)
        return config_dict
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration complète: {str(e)}")
        return {}

def reset() -> bool:
    """Réinitialise la configuration aux valeurs par défaut"""
    try:
        global _config
        _config = configparser.ConfigParser()
        return initialize()
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de la configuration: {str(e)}")
        return False 