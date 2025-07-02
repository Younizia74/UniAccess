#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests unitaires pour le backend de synthèse vocale
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import speech_backend

def test_initialization(mock_speech_engine, test_config):
    """Test l'initialisation du backend de synthèse vocale"""
    with patch('speech_backend._speech_engine', mock_speech_engine):
        assert speech_backend.initialize(test_config['voix'])
        assert speech_backend.cleanup()

def test_say_text(mock_speech_engine):
    """Test la fonction de synthèse vocale"""
    with patch('speech_backend._speech_engine', mock_speech_engine):
        text = "Test de synthèse vocale"
        assert speech_backend.say(text)
        assert mock_speech_engine.last_spoken == text

def test_stop_speech(mock_speech_engine):
    """Test l'arrêt de la synthèse vocale"""
    with patch('speech_backend._speech_engine', mock_speech_engine):
        # D'abord dire quelque chose
        speech_backend.say("Test")
        assert mock_speech_engine.last_spoken is not None
        
        # Puis arrêter
        assert speech_backend.stop()
        assert mock_speech_engine.last_spoken is None

def test_invalid_config():
    """Test avec une configuration invalide"""
    invalid_config = {
        'moteur': 'invalid_engine',
        'langue': 'invalid_lang'
    }
    assert not speech_backend.initialize(invalid_config)

def test_error_handling(mock_speech_engine):
    """Test la gestion des erreurs"""
    with patch('speech_backend._speech_engine', mock_speech_engine):
        # Simuler une erreur dans le moteur
        mock_speech_engine.speak = MagicMock(return_value=False)
        assert not speech_backend.say("Test")
        
        # Simuler une erreur lors de l'arrêt
        mock_speech_engine.stop = MagicMock(return_value=False)
        assert not speech_backend.stop()

def test_multiple_initialization(mock_speech_engine, test_config):
    """Test l'initialisation multiple"""
    with patch('speech_backend._speech_engine', mock_speech_engine):
        # Première initialisation
        assert speech_backend.initialize(test_config['voix'])
        
        # Deuxième initialisation (devrait retourner True car déjà initialisé)
        assert speech_backend.initialize(test_config['voix'])
        
        # Nettoyage
        assert speech_backend.cleanup()
        
        # Réinitialisation après nettoyage
        assert speech_backend.initialize(test_config['voix']) 