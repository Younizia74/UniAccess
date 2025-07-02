#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour l'audio spatial
Teste les fonctionnalités de son 3D et de spatialisation
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path
import numpy as np

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.audio_spatial import spatializer, calibration

class MockSpatialAudio:
    def __init__(self):
        self.initialized = False
        self.calibrated = False
        self.sound_position = (0, 0, 0)  # (x, y, z)
        self.listener_position = (0, 0, 0)
        self.listener_orientation = (0, 0, 0)  # (yaw, pitch, roll)
        self.volume = 1.0
        self.last_command = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        return True
        
    def calibrate(self):
        self.calibrated = True
        return True
        
    def set_sound_position(self, x, y, z):
        self.sound_position = (x, y, z)
        return True
        
    def set_listener_position(self, x, y, z):
        self.listener_position = (x, y, z)
        return True
        
    def set_listener_orientation(self, yaw, pitch, roll):
        self.listener_orientation = (yaw, pitch, roll)
        return True
        
    def play_sound(self, sound_id, position=None):
        if position:
            self.set_sound_position(*position)
        return True
        
    def stop_sound(self, sound_id):
        return True

class MockAudioCalibration:
    def __init__(self):
        self.profiles = {
            'default': {
                'head_radius': 0.1,
                'ear_distance': 0.2,
                'room_size': (5, 5, 3),
                'reverb': 0.3
            }
        }
        self.current_profile = 'default'
        
    def calibrate(self, profile_name=None):
        if profile_name:
            self.current_profile = profile_name
        return True
        
    def get_profile(self, profile_name):
        return self.profiles.get(profile_name)
        
    def save_profile(self, profile_name, settings):
        self.profiles[profile_name] = settings
        return True

@pytest.fixture
def mock_spatial_audio():
    """Fixture fournissant un mock d'audio spatial"""
    return MockSpatialAudio()

@pytest.fixture
def mock_audio_calibration():
    """Fixture fournissant un mock de calibration audio"""
    return MockAudioCalibration()

def test_spatial_audio_initialization(mock_spatial_audio):
    """Test l'initialisation de l'audio spatial"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        assert spatializer.initialize()
        assert mock_spatial_audio.initialized
        assert spatializer.cleanup()
        assert not mock_spatial_audio.initialized

def test_audio_calibration(mock_spatial_audio, mock_audio_calibration):
    """Test la calibration audio"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio), \
         patch('nvda_linux.audio_spatial.calibration._calibration', mock_audio_calibration):
        
        spatializer.initialize()
        
        # Test de calibration par défaut
        assert calibration.calibrate()
        assert mock_spatial_audio.calibrated
        
        # Test de calibration avec un profil personnalisé
        custom_profile = {
            'head_radius': 0.12,
            'ear_distance': 0.22,
            'room_size': (6, 6, 4),
            'reverb': 0.4
        }
        
        assert calibration.save_profile('custom', custom_profile)
        assert calibration.calibrate('custom')
        
        profile = calibration.get_profile('custom')
        assert profile == custom_profile
        
        spatializer.cleanup()

def test_sound_positioning(mock_spatial_audio):
    """Test le positionnement des sons"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        spatializer.initialize()
        
        # Test de différentes positions
        positions = [
            (1, 0, 0),   # Droite
            (-1, 0, 0),  # Gauche
            (0, 1, 0),   # Avant
            (0, -1, 0),  # Arrière
            (0, 0, 1),   # Haut
            (0, 0, -1)   # Bas
        ]
        
        for pos in positions:
            assert spatializer.set_sound_position(*pos)
            assert mock_spatial_audio.sound_position == pos
        
        spatializer.cleanup()

def test_listener_positioning(mock_spatial_audio):
    """Test le positionnement de l'auditeur"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        spatializer.initialize()
        
        # Test de différentes positions d'auditeur
        positions = [
            (0, 0, 0),    # Centre
            (1, 1, 0),    # Coin avant droit
            (-1, -1, 0),  # Coin arrière gauche
            (0, 0, 1.5)   # Debout
        ]
        
        for pos in positions:
            assert spatializer.set_listener_position(*pos)
            assert mock_spatial_audio.listener_position == pos
        
        spatializer.cleanup()

def test_listener_orientation(mock_spatial_audio):
    """Test l'orientation de l'auditeur"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        spatializer.initialize()
        
        # Test de différentes orientations
        orientations = [
            (0, 0, 0),     # Face à l'avant
            (90, 0, 0),    # Tourné à droite
            (-90, 0, 0),   # Tourné à gauche
            (0, 45, 0),    # Regardant en haut
            (0, -45, 0)    # Regardant en bas
        ]
        
        for orient in orientations:
            assert spatializer.set_listener_orientation(*orient)
            assert mock_spatial_audio.listener_orientation == orient
        
        spatializer.cleanup()

def test_sound_playback(mock_spatial_audio):
    """Test la lecture des sons"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        spatializer.initialize()
        
        # Test de lecture de sons à différentes positions
        sounds = [
            ('click', (1, 0, 0)),
            ('notification', (0, 1, 0)),
            ('alert', (0, 0, 1))
        ]
        
        for sound_id, position in sounds:
            assert spatializer.play_sound(sound_id, position)
            assert mock_spatial_audio.sound_position == position
            assert spatializer.stop_sound(sound_id)
        
        spatializer.cleanup()

def test_error_handling(mock_spatial_audio):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        # Test avec un système non initialisé
        mock_spatial_audio.initialized = False
        assert not spatializer.set_sound_position(1, 0, 0)
        
        # Test avec des positions invalides
        spatializer.initialize()
        assert not spatializer.set_sound_position(None, 0, 0)
        assert not spatializer.set_listener_position(0, None, 0)
        assert not spatializer.set_listener_orientation(None, 0, 0)
        
        # Test avec un son invalide
        assert not spatializer.play_sound(None)
        
        spatializer.cleanup()

def test_audio_profiles(mock_audio_calibration):
    """Test la gestion des profils audio"""
    with patch('nvda_linux.audio_spatial.calibration._calibration', mock_audio_calibration):
        # Test de création de profils
        profiles = {
            'small_room': {
                'head_radius': 0.1,
                'ear_distance': 0.2,
                'room_size': (3, 3, 2),
                'reverb': 0.2
            },
            'large_room': {
                'head_radius': 0.1,
                'ear_distance': 0.2,
                'room_size': (10, 10, 5),
                'reverb': 0.5
            }
        }
        
        for name, settings in profiles.items():
            assert calibration.save_profile(name, settings)
            profile = calibration.get_profile(name)
            assert profile == settings

def test_performance(mock_spatial_audio):
    """Test les performances de l'audio spatial"""
    with patch('nvda_linux.audio_spatial.spatializer._spatial_audio', mock_spatial_audio):
        spatializer.initialize()
        
        import time
        
        # Test de performance avec des mises à jour rapides
        start_time = time.time()
        
        for _ in range(100):  # 100 itérations
            spatializer.set_sound_position(1, 0, 0)
            spatializer.set_listener_position(0, 1, 0)
            spatializer.set_listener_orientation(45, 0, 0)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que le temps d'exécution est raisonnable
        assert duration < 1.0  # Moins d'une seconde pour 100 itérations
        
        spatializer.cleanup() 