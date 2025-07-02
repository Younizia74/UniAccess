#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests d'intégration pour Android
Teste l'interaction entre les différents composants sur Android
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_android.apps.system import settings
from nvda_android.apps.accessibility import service
from nvda_android.apps.input_method import keyboard

class MockAndroidApp:
    def __init__(self, name, package_name):
        self.name = name
        self.package_name = package_name
        self._focused = None
        self._window = None
        
    def get_focused_element(self):
        return self._focused
        
    def get_window(self):
        return self._window
        
    def execute_action(self, action, **kwargs):
        if action == 'click':
            return True
        elif action == 'focus':
            return True
        return False

@pytest.fixture
def mock_android_apps():
    """Fixture fournissant des mocks pour les applications Android"""
    apps = {
        'settings': MockAndroidApp('Paramètres', 'com.android.settings'),
        'accessibility': MockAndroidApp('Accessibilité', 'com.android.accessibility'),
        'keyboard': MockAndroidApp('Clavier', 'com.android.inputmethod')
    }
    return apps

def test_android_initialization(mock_android_apps):
    """Test l'initialisation des composants Android"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']), \
         patch('nvda_android.apps.input_method.keyboard._keyboard_app', mock_android_apps['keyboard']):
        
        # Test des paramètres
        assert settings.initialize()
        app = settings.get_settings_app()
        assert app is not None
        assert app.name == 'Paramètres'
        
        # Test du service d'accessibilité
        assert service.initialize()
        app = service.get_accessibility_service()
        assert app is not None
        assert app.name == 'Accessibilité'
        
        # Test du clavier
        assert keyboard.initialize()
        app = keyboard.get_keyboard_app()
        assert app is not None
        assert app.name == 'Clavier'

def test_android_interaction(mock_android_apps, mock_speech_engine):
    """Test l'interaction entre les composants Android et la synthèse vocale"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']), \
         patch('nvda_android.apps.input_method.keyboard._keyboard_app', mock_android_apps['keyboard']), \
         patch('speech_backend._speech_engine', mock_speech_engine):
        
        # Test des paramètres
        settings_app = settings.get_settings_app()
        assert settings_app is not None
        assert settings.execute_action('settings', 'click')
        assert mock_speech_engine.last_spoken is not None
        
        # Test du service d'accessibilité
        accessibility_app = service.get_accessibility_service()
        assert accessibility_app is not None
        assert service.execute_action('accessibility', 'focus')
        assert mock_speech_engine.last_spoken is not None
        
        # Test du clavier
        keyboard_app = keyboard.get_keyboard_app()
        assert keyboard_app is not None
        assert keyboard.execute_action('keyboard', 'click')
        assert mock_speech_engine.last_spoken is not None

def test_android_gestures(mock_android_apps):
    """Test la gestion des gestes Android"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']):
        
        # Test des gestes de base
        gestures = [
            'swipe_left',
            'swipe_right',
            'swipe_up',
            'swipe_down',
            'tap',
            'double_tap',
            'long_press'
        ]
        
        for gesture in gestures:
            assert service.execute_gesture(gesture)
            
        # Test des gestes personnalisés
        custom_gestures = {
            'next_item': 'swipe_right',
            'previous_item': 'swipe_left',
            'activate': 'double_tap',
            'context_menu': 'long_press'
        }
        
        for action, gesture in custom_gestures.items():
            assert service.execute_custom_gesture(action)

def test_android_accessibility_features(mock_android_apps):
    """Test les fonctionnalités d'accessibilité Android"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']):
        
        # Test de l'exploration de l'interface
        assert service.explore_interface()
        
        # Test de la navigation
        navigation_actions = [
            'next',
            'previous',
            'first',
            'last',
            'parent',
            'child'
        ]
        
        for action in navigation_actions:
            assert service.navigate(action)
        
        # Test de la lecture
        assert service.read_current()
        assert service.read_from_top()
        assert service.read_from_cursor()

def test_error_handling(mock_android_apps):
    """Test la gestion des erreurs"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']):
        
        # Test avec une application inexistante
        assert not service.execute_action('inexistant', 'click')
        
        # Test avec une action invalide
        assert not service.execute_action('settings', 'action_invalide')
        
        # Test avec un geste invalide
        assert not service.execute_gesture('geste_invalide')
        
        # Test avec une navigation invalide
        assert not service.navigate('direction_invalide')

def test_android_cleanup(mock_android_apps):
    """Test le nettoyage des composants Android"""
    with patch('nvda_android.apps.system.settings._settings_app', mock_android_apps['settings']), \
         patch('nvda_android.apps.accessibility.service._accessibility_service', mock_android_apps['accessibility']), \
         patch('nvda_android.apps.input_method.keyboard._keyboard_app', mock_android_apps['keyboard']):
        
        # Initialiser les composants
        settings.initialize()
        service.initialize()
        keyboard.initialize()
        
        # Nettoyer
        assert settings.cleanup()
        assert service.cleanup()
        assert keyboard.cleanup()
        
        # Vérifier que les instances sont nettoyées
        assert settings.get_settings_app() is None
        assert service.get_accessibility_service() is None
        assert keyboard.get_keyboard_app() is None 