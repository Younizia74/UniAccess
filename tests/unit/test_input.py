#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests unitaires pour le backend de gestion des entrées
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import input_listener

def test_initialization(mock_input_manager):
    """Test l'initialisation du gestionnaire d'entrées"""
    with patch('input_listener._input_manager', mock_input_manager):
        assert input_listener.initialize()
        assert mock_input_manager.is_listening
        assert input_listener.cleanup()
        assert not mock_input_manager.is_listening

def test_key_listening(mock_input_manager):
    """Test l'écoute des touches"""
    with patch('input_listener._input_manager', mock_input_manager):
        input_listener.initialize()
        
        # Simuler quelques touches
        test_keys = ['a', 'b', 'c', 'Enter', 'Escape']
        for key in test_keys:
            mock_input_manager.simulate_key(key)
            assert mock_input_manager.last_key == key
        
        input_listener.cleanup()

def test_key_callback(mock_input_manager):
    """Test les callbacks de touches"""
    with patch('input_listener._input_manager', mock_input_manager):
        # Créer un mock pour le callback
        callback_called = False
        last_key = None
        
        def test_callback(key):
            nonlocal callback_called, last_key
            callback_called = True
            last_key = key
        
        # Enregistrer le callback
        input_listener.register_key_callback(test_callback)
        input_listener.initialize()
        
        # Simuler une touche
        test_key = 'a'
        mock_input_manager.simulate_key(test_key)
        
        # Vérifier que le callback a été appelé
        assert callback_called
        assert last_key == test_key
        
        input_listener.cleanup()

def test_multiple_callbacks(mock_input_manager):
    """Test l'enregistrement de plusieurs callbacks"""
    with patch('input_listener._input_manager', mock_input_manager):
        callbacks_called = []
        
        def callback1(key):
            callbacks_called.append(('callback1', key))
        
        def callback2(key):
            callbacks_called.append(('callback2', key))
        
        # Enregistrer les callbacks
        input_listener.register_key_callback(callback1)
        input_listener.register_key_callback(callback2)
        input_listener.initialize()
        
        # Simuler une touche
        test_key = 'b'
        mock_input_manager.simulate_key(test_key)
        
        # Vérifier que les deux callbacks ont été appelés
        assert len(callbacks_called) == 2
        assert ('callback1', test_key) in callbacks_called
        assert ('callback2', test_key) in callbacks_called
        
        input_listener.cleanup()

def test_error_handling(mock_input_manager):
    """Test la gestion des erreurs"""
    with patch('input_listener._input_manager', mock_input_manager):
        # Simuler une erreur dans le gestionnaire
        mock_input_manager.start = MagicMock(return_value=False)
        assert not input_listener.initialize()
        
        # Réinitialiser le mock
        mock_input_manager.start = MagicMock(return_value=True)
        assert input_listener.initialize()
        
        # Simuler une erreur lors de l'arrêt
        mock_input_manager.stop = MagicMock(return_value=False)
        assert not input_listener.cleanup()

def test_callback_error_handling(mock_input_manager):
    """Test la gestion des erreurs dans les callbacks"""
    with patch('input_listener._input_manager', mock_input_manager):
        def error_callback(key):
            raise Exception("Erreur de test")
        
        # Le callback ne devrait pas faire planter le programme
        input_listener.register_key_callback(error_callback)
        input_listener.initialize()
        
        # Simuler une touche
        mock_input_manager.simulate_key('a')
        
        # Le programme devrait toujours fonctionner
        assert mock_input_manager.is_listening
        
        input_listener.cleanup() 