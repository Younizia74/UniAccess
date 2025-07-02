#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour le support haptique
Teste les fonctionnalités de retour tactile
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.haptics import controller, feedback

class MockHapticController:
    def __init__(self):
        self.connected = False
        self.vibration_active = False
        self.intensity = 0
        self.pattern = None
        self.last_command = None
        
    def connect(self):
        self.connected = True
        return True
        
    def disconnect(self):
        self.connected = False
        return True
        
    def vibrate(self, pattern, intensity=1.0, duration=100):
        if not self.connected:
            return False
        self.vibration_active = True
        self.pattern = pattern
        self.intensity = intensity
        return True
        
    def stop(self):
        if not self.connected:
            return False
        self.vibration_active = False
        self.pattern = None
        self.intensity = 0
        return True
        
    def execute_command(self, command):
        self.last_command = command
        return True

class MockHapticFeedback:
    def __init__(self):
        self.patterns = {
            'click': [100],  # 100ms de vibration
            'double_click': [100, 50, 100],  # Double clic
            'error': [200, 100, 200],  # Erreur
            'success': [100, 100, 100],  # Succès
            'scroll': [50] * 3,  # Défilement
            'notification': [150, 100, 150]  # Notification
        }
        
    def get_pattern(self, name):
        return self.patterns.get(name, [100])
        
    def create_pattern(self, pattern):
        return pattern

@pytest.fixture
def mock_haptic_controller():
    """Fixture fournissant un mock de contrôleur haptique"""
    return MockHapticController()

@pytest.fixture
def mock_haptic_feedback():
    """Fixture fournissant un mock de retour haptique"""
    return MockHapticFeedback()

def test_haptic_initialization(mock_haptic_controller):
    """Test l'initialisation du contrôleur haptique"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        assert controller.initialize()
        assert mock_haptic_controller.connected
        assert controller.cleanup()
        assert not mock_haptic_controller.connected

def test_haptic_patterns(mock_haptic_controller, mock_haptic_feedback):
    """Test les patterns de vibration"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller), \
         patch('nvda_linux.haptics.feedback._feedback', mock_haptic_feedback):
        
        controller.initialize()
        
        # Test des patterns prédéfinis
        patterns = [
            'click',
            'double_click',
            'error',
            'success',
            'scroll',
            'notification'
        ]
        
        for pattern_name in patterns:
            pattern = mock_haptic_feedback.get_pattern(pattern_name)
            assert controller.vibrate(pattern)
            assert mock_haptic_controller.pattern == pattern
            assert mock_haptic_controller.vibration_active
            
            controller.stop()
            assert not mock_haptic_controller.vibration_active
        
        controller.cleanup()

def test_haptic_intensity(mock_haptic_controller):
    """Test le contrôle de l'intensité"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        controller.initialize()
        
        # Test de différentes intensités
        intensities = [0.25, 0.5, 0.75, 1.0]
        
        for intensity in intensities:
            assert controller.vibrate([100], intensity=intensity)
            assert mock_haptic_controller.intensity == intensity
            controller.stop()
        
        controller.cleanup()

def test_haptic_commands(mock_haptic_controller):
    """Test les commandes du contrôleur haptique"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        controller.initialize()
        
        # Test des commandes de base
        commands = [
            'calibrate',
            'reset',
            'test',
            'status'
        ]
        
        for command in commands:
            assert controller.execute_command(command)
            assert mock_haptic_controller.last_command == command
        
        controller.cleanup()

def test_haptic_error_handling(mock_haptic_controller):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        # Test avec un contrôleur non connecté
        mock_haptic_controller.connected = False
        assert not controller.vibrate([100])
        
        # Test avec une commande invalide
        controller.initialize()
        assert not controller.execute_command("commande_invalide")
        
        # Test avec un pattern invalide
        assert not controller.vibrate(None)
        assert not controller.vibrate([])
        
        controller.cleanup()

def test_haptic_custom_patterns(mock_haptic_controller, mock_haptic_feedback):
    """Test la création de patterns personnalisés"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller), \
         patch('nvda_linux.haptics.feedback._feedback', mock_haptic_feedback):
        
        controller.initialize()
        
        # Test de création de pattern personnalisé
        custom_pattern = [50, 100, 50, 200]  # Pattern personnalisé
        pattern = mock_haptic_feedback.create_pattern(custom_pattern)
        
        assert controller.vibrate(pattern)
        assert mock_haptic_controller.pattern == custom_pattern
        
        controller.cleanup()

def test_haptic_configuration(mock_haptic_controller):
    """Test la configuration du contrôleur haptique"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        controller.initialize()
        
        # Test de la configuration
        config = {
            'intensity': 0.8,
            'duration': 150,
            'patterns': {
                'custom1': [100, 200],
                'custom2': [50, 50, 50]
            }
        }
        
        assert controller.configure(config)
        assert mock_haptic_controller.intensity == config['intensity']
        
        controller.cleanup()

def test_haptic_performance(mock_haptic_controller):
    """Test les performances du contrôleur haptique"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        controller.initialize()
        
        # Test de performance avec des vibrations rapides
        import time
        
        start_time = time.time()
        
        for _ in range(100):  # 100 itérations
            controller.vibrate([50])
            controller.stop()
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que le temps d'exécution est raisonnable
        assert duration < 1.0  # Moins d'une seconde pour 100 itérations
        
        controller.cleanup()

def test_haptic_synchronization(mock_haptic_controller):
    """Test la synchronisation des vibrations"""
    with patch('nvda_linux.haptics.controller._controller', mock_haptic_controller):
        controller.initialize()
        
        # Test de synchronisation avec des patterns complexes
        complex_pattern = [100, 50, 100, 50, 100]
        
        # Démarrer la vibration
        assert controller.vibrate(complex_pattern)
        
        # Vérifier que le pattern est correctement exécuté
        assert mock_haptic_controller.pattern == complex_pattern
        assert mock_haptic_controller.vibration_active
        
        # Arrêter la vibration
        assert controller.stop()
        assert not mock_haptic_controller.vibration_active
        
        controller.cleanup() 