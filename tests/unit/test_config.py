#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests unitaires pour le module de configuration
"""

import pytest
import os
import tempfile
import json
from pathlib import Path
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import config

def test_default_config():
    """Test la configuration par défaut"""
    default_config = config.get_config()
    assert 'voix' in default_config
    assert 'braille' in default_config
    assert 'haptique' in default_config
    assert 'audio_spatial' in default_config
    assert 'ia' in default_config
    assert 'plateformes' in default_config

def test_config_validation():
    """Test la validation de la configuration"""
    # Configuration valide
    valid_config = {
        'voix': {
            'moteur': 'espeak',
            'langue': 'fr',
            'vitesse': 180,
            'volume': 100
        }
    }
    assert config.validate_config(valid_config)
    
    # Configuration invalide (types incorrects)
    invalid_config = {
        'voix': {
            'moteur': 123,  # Devrait être une chaîne
            'vitesse': '180'  # Devrait être un nombre
        }
    }
    assert not config.validate_config(invalid_config)

def test_config_persistence():
    """Test la persistance de la configuration"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / 'config.json'
        
        # Configuration de test
        test_config = {
            'voix': {
                'moteur': 'test_engine',
                'langue': 'test_lang',
                'vitesse': 150,
                'volume': 80
            }
        }
        
        # Sauvegarder la configuration
        assert config.save_config(test_config, config_path)
        
        # Charger la configuration
        loaded_config = config.load_config(config_path)
        assert loaded_config is not None
        assert loaded_config['voix']['moteur'] == 'test_engine'
        assert loaded_config['voix']['langue'] == 'test_lang'
        assert loaded_config['voix']['vitesse'] == 150
        assert loaded_config['voix']['volume'] == 80

def test_config_merge():
    """Test la fusion de configurations"""
    base_config = {
        'voix': {
            'moteur': 'espeak',
            'langue': 'fr',
            'vitesse': 180
        }
    }
    
    override_config = {
        'voix': {
            'vitesse': 200,
            'volume': 90
        },
        'braille': {
            'afficheur': 'test'
        }
    }
    
    merged = config.merge_configs(base_config, override_config)
    assert merged['voix']['moteur'] == 'espeak'  # Non écrasé
    assert merged['voix']['langue'] == 'fr'  # Non écrasé
    assert merged['voix']['vitesse'] == 200  # Écrasé
    assert merged['voix']['volume'] == 90  # Nouveau
    assert merged['braille']['afficheur'] == 'test'  # Nouveau

def test_config_environment():
    """Test la configuration via les variables d'environnement"""
    with patch.dict(os.environ, {
        'NVDA_VOIX_MOTEUR': 'test_engine',
        'NVDA_VOIX_VITESSE': '200',
        'NVDA_BRAILLE_AFFICHEUR': 'test_display'
    }):
        env_config = config.get_config_from_env()
        assert env_config['voix']['moteur'] == 'test_engine'
        assert env_config['voix']['vitesse'] == 200
        assert env_config['braille']['afficheur'] == 'test_display'

def test_config_error_handling():
    """Test la gestion des erreurs de configuration"""
    # Test avec un fichier inexistant
    assert config.load_config('fichier_inexistant.json') is None
    
    # Test avec un fichier invalide
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
        f.write('invalid json')
        f.flush()
        assert config.load_config(f.name) is None
    
    # Test avec une configuration invalide
    invalid_config = {
        'voix': {
            'moteur': 123,  # Type invalide
            'vitesse': 'invalid'  # Type invalide
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
        json.dump(invalid_config, f)
        f.flush()
        assert not config.validate_config(config.load_config(f.name))

def test_config_platform_specific():
    """Test la configuration spécifique à la plateforme"""
    # Configuration de base
    base_config = config.get_config()
    
    # Configuration Linux
    linux_config = config.get_platform_config('linux')
    assert 'linux' in linux_config['plateformes']
    assert linux_config['plateformes']['linux'] is True
    
    # Configuration Windows
    windows_config = config.get_platform_config('windows')
    assert 'windows' in windows_config['plateformes']
    assert windows_config['plateformes']['windows'] is True
    
    # Configuration Android
    android_config = config.get_platform_config('android')
    assert 'android' in android_config['plateformes']
    assert android_config['plateformes']['android'] is True 