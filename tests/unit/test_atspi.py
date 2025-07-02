#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests unitaires pour le backend AT-SPI
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import atspi_backend

class MockAccessible:
    def __init__(self, name="", role=None, children=None):
        self._name = name
        self._role = role
        self._children = children or []
        self._state = MagicMock()
        self._state.contains.return_value = False
        
    def get_name(self):
        return self._name
        
    def get_role(self):
        return self._role
        
    def get_children(self):
        return self._children
        
    def get_state(self):
        return self._state
        
    def get_parent(self):
        return None

@pytest.fixture
def mock_desktop():
    """Fixture fournissant un mock du bureau"""
    root = MockAccessible("Desktop", atspi_backend.Atspi.Role.DESKTOP)
    app1 = MockAccessible("App1", atspi_backend.Atspi.Role.APPLICATION)
    app2 = MockAccessible("App2", atspi_backend.Atspi.Role.APPLICATION)
    root._children = [app1, app2]
    return root

def test_initialization(mock_atspi):
    """Test l'initialisation du backend AT-SPI"""
    with patch('atspi_backend.Atspi', mock_atspi):
        assert atspi_backend.initialize()
        assert atspi_backend.cleanup()

def test_get_desktop(mock_atspi, mock_desktop):
    """Test la récupération du bureau"""
    with patch('atspi_backend.Atspi.get_desktop', return_value=mock_desktop):
        desktop = atspi_backend.get_desktop()
        assert desktop is not None
        assert desktop.get_name() == "Desktop"
        assert len(desktop.get_children()) == 2

def test_find_application(mock_atspi, mock_desktop):
    """Test la recherche d'application"""
    with patch('atspi_backend.Atspi.get_desktop', return_value=mock_desktop):
        app = atspi_backend.find_application("App1")
        assert app is not None
        assert app.get_name() == "App1"
        
        # Test avec une application inexistante
        app = atspi_backend.find_application("Inexistant")
        assert app is None

def test_get_focused_element(mock_atspi):
    """Test la récupération de l'élément focalisé"""
    focused = MockAccessible("Focused", atspi_backend.Atspi.Role.PUSH_BUTTON)
    focused._state.contains.return_value = True
    
    with patch('atspi_backend.Atspi.get_desktop', return_value=MockAccessible(children=[focused])):
        element = atspi_backend.get_focused_element()
        assert element is not None
        assert element.get_name() == "Focused"

def test_get_element_info(mock_atspi):
    """Test la récupération des informations d'un élément"""
    element = MockAccessible(
        name="Test Element",
        role=atspi_backend.Atspi.Role.PUSH_BUTTON,
        children=[
            MockAccessible("Child1"),
            MockAccessible("Child2")
        ]
    )
    
    info = atspi_backend.get_element_info(element)
    assert info is not None
    assert info['name'] == "Test Element"
    assert info['role'] == atspi_backend.Atspi.Role.PUSH_BUTTON
    assert len(info['children']) == 2

def test_find_element_by_role(mock_atspi):
    """Test la recherche d'élément par rôle"""
    button = MockAccessible("Button", atspi_backend.Atspi.Role.PUSH_BUTTON)
    menu = MockAccessible("Menu", atspi_backend.Atspi.Role.MENU)
    root = MockAccessible(children=[button, menu])
    
    elements = atspi_backend.find_elements_by_role(root, atspi_backend.Atspi.Role.PUSH_BUTTON)
    assert len(elements) == 1
    assert elements[0].get_name() == "Button"

def test_error_handling(mock_atspi):
    """Test la gestion des erreurs"""
    with patch('atspi_backend.Atspi.get_desktop', side_effect=Exception("Erreur de test")):
        # Les erreurs ne devraient pas faire planter le programme
        desktop = atspi_backend.get_desktop()
        assert desktop is None
        
        app = atspi_backend.find_application("Test")
        assert app is None
        
        element = atspi_backend.get_focused_element()
        assert element is None

def test_cleanup(mock_atspi):
    """Test le nettoyage des ressources"""
    with patch('atspi_backend.Atspi') as mock:
        atspi_backend.initialize()
        assert atspi_backend.cleanup()
        
        # Vérifier que le nettoyage a été appelé
        mock.cleanup.assert_called_once() 