#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour l'accessibilité
Teste les fonctionnalités d'accessibilité (contraste, raccourcis, etc.)
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.accessibility import contrast, shortcuts, braille, magnifier

class MockContrast:
    def __init__(self):
        self.initialized = False
        self.contrast_ratio = 1.0
        self.last_foreground = None
        self.last_background = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        return True
        
    def compute_contrast_ratio(self, fg, bg):
        self.last_foreground = fg
        self.last_background = bg
        # Simuler un calcul de contraste
        self.contrast_ratio = 4.5  # Ratio de contraste par défaut (conforme WCAG AA)
        return self.contrast_ratio
        
    def is_accessible(self, fg, bg, level="AA"):
        ratio = self.compute_contrast_ratio(fg, bg)
        if level == "A":
            return ratio >= 3.0
        elif level == "AA":
            return ratio >= 4.5
        elif level == "AAA":
            return ratio >= 7.0
        return False

class MockShortcuts:
    def __init__(self):
        self.initialized = False
        self.shortcuts = {}
        self.last_shortcut = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        self.shortcuts = {}
        return True
        
    def register_shortcut(self, key, callback, description):
        self.shortcuts[key] = (callback, description)
        return True
        
    def unregister_shortcut(self, key):
        if key in self.shortcuts:
            del self.shortcuts[key]
            return True
        return False
        
    def trigger_shortcut(self, key):
        self.last_shortcut = key
        if key in self.shortcuts:
            callback, _ = self.shortcuts[key]
            callback()
            return True
        return False

class MockBraille:
    def __init__(self):
        self.initialized = False
        self.connected = False
        self.last_text = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        self.connected = False
        return True
        
    def connect(self):
        self.connected = True
        return True
        
    def disconnect(self):
        self.connected = False
        return True
        
    def display_text(self, text):
        self.last_text = text
        return True
        
    def clear_display(self):
        self.last_text = ""
        return True

class MockMagnifier:
    def __init__(self):
        self.initialized = False
        self.enabled = False
        self.zoom_level = 1.0
        self.last_region = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        self.enabled = False
        return True
        
    def enable(self):
        self.enabled = True
        return True
        
    def disable(self):
        self.enabled = False
        return True
        
    def set_zoom(self, level):
        self.zoom_level = level
        return True
        
    def magnify_region(self, region):
        self.last_region = region
        return True

@pytest.fixture
def mock_contrast():
    """Fixture fournissant un mock de gestion du contraste"""
    return MockContrast()

@pytest.fixture
def mock_shortcuts():
    """Fixture fournissant un mock de gestion des raccourcis"""
    return MockShortcuts()

@pytest.fixture
def mock_braille():
    """Fixture fournissant un mock d'affichage braille"""
    return MockBraille()

@pytest.fixture
def mock_magnifier():
    """Fixture fournissant un mock de loupe"""
    return MockMagnifier()

def test_contrast_initialization(mock_contrast):
    """Test l'initialisation de la gestion du contraste"""
    with patch('nvda_linux.accessibility.contrast._contrast', mock_contrast):
        assert contrast.initialize()
        assert mock_contrast.initialized
        assert contrast.cleanup()
        assert not mock_contrast.initialized

def test_contrast_computation(mock_contrast):
    """Test le calcul du contraste"""
    with patch('nvda_linux.accessibility.contrast._contrast', mock_contrast):
        contrast.initialize()
        
        # Test de différentes combinaisons de couleurs
        color_pairs = [
            ((0, 0, 0), (255, 255, 255)),  # Noir sur blanc
            ((255, 0, 0), (0, 255, 0)),    # Rouge sur vert
            ((0, 0, 255), (255, 255, 0))   # Bleu sur jaune
        ]
        
        for fg, bg in color_pairs:
            ratio = contrast.compute_contrast_ratio(fg, bg)
            assert ratio is not None
            assert ratio > 0
            
            # Vérifier l'accessibilité selon différents niveaux
            assert contrast.is_accessible(fg, bg, "A")   # Niveau A
            assert contrast.is_accessible(fg, bg, "AA")  # Niveau AA
            assert not contrast.is_accessible(fg, bg, "AAA")  # Niveau AAA (plus strict)
        
        contrast.cleanup()

def test_shortcuts_initialization(mock_shortcuts):
    """Test l'initialisation de la gestion des raccourcis"""
    with patch('nvda_linux.accessibility.shortcuts._shortcuts', mock_shortcuts):
        assert shortcuts.initialize()
        assert mock_shortcuts.initialized
        assert shortcuts.cleanup()
        assert not mock_shortcuts.initialized

def test_shortcut_registration(mock_shortcuts):
    """Test l'enregistrement des raccourcis"""
    with patch('nvda_linux.accessibility.shortcuts._shortcuts', mock_shortcuts):
        shortcuts.initialize()
        
        # Fonction de test
        def test_callback():
            pass
        
        # Enregistrer des raccourcis
        assert shortcuts.register_shortcut("Ctrl+A", test_callback, "Sélectionner tout")
        assert shortcuts.register_shortcut("Ctrl+C", test_callback, "Copier")
        
        # Vérifier l'enregistrement
        assert "Ctrl+A" in mock_shortcuts.shortcuts
        assert "Ctrl+C" in mock_shortcuts.shortcuts
        
        # Désenregistrer un raccourci
        assert shortcuts.unregister_shortcut("Ctrl+A")
        assert "Ctrl+A" not in mock_shortcuts.shortcuts
        
        shortcuts.cleanup()

def test_shortcut_triggering(mock_shortcuts):
    """Test le déclenchement des raccourcis"""
    with patch('nvda_linux.accessibility.shortcuts._shortcuts', mock_shortcuts):
        shortcuts.initialize()
        
        # Variable pour suivre l'appel
        called = False
        
        def test_callback():
            nonlocal called
            called = True
        
        # Enregistrer un raccourci
        shortcuts.register_shortcut("Ctrl+Space", test_callback, "Test")
        
        # Déclencher le raccourci
        assert shortcuts.trigger_shortcut("Ctrl+Space")
        assert called
        assert mock_shortcuts.last_shortcut == "Ctrl+Space"
        
        # Test avec un raccourci non enregistré
        assert not shortcuts.trigger_shortcut("Invalid")
        
        shortcuts.cleanup()

def test_braille_initialization(mock_braille):
    """Test l'initialisation de l'affichage braille"""
    with patch('nvda_linux.accessibility.braille._braille', mock_braille):
        assert braille.initialize()
        assert mock_braille.initialized
        assert braille.cleanup()
        assert not mock_braille.initialized

def test_braille_connection(mock_braille):
    """Test la connexion à l'afficheur braille"""
    with patch('nvda_linux.accessibility.braille._braille', mock_braille):
        braille.initialize()
        
        # Test de connexion
        assert braille.connect()
        assert mock_braille.connected
        
        # Test d'affichage de texte
        test_text = "Test braille"
        assert braille.display_text(test_text)
        assert mock_braille.last_text == test_text
        
        # Test d'effacement
        assert braille.clear_display()
        assert mock_braille.last_text == ""
        
        # Test de déconnexion
        assert braille.disconnect()
        assert not mock_braille.connected
        
        braille.cleanup()

def test_magnifier_initialization(mock_magnifier):
    """Test l'initialisation de la loupe"""
    with patch('nvda_linux.accessibility.magnifier._magnifier', mock_magnifier):
        assert magnifier.initialize()
        assert mock_magnifier.initialized
        assert magnifier.cleanup()
        assert not mock_magnifier.initialized

def test_magnifier_control(mock_magnifier):
    """Test le contrôle de la loupe"""
    with patch('nvda_linux.accessibility.magnifier._magnifier', mock_magnifier):
        magnifier.initialize()
        
        # Test d'activation
        assert magnifier.enable()
        assert mock_magnifier.enabled
        
        # Test de niveau de zoom
        zoom_levels = [1.5, 2.0, 3.0, 4.0]
        for level in zoom_levels:
            assert magnifier.set_zoom(level)
            assert mock_magnifier.zoom_level == level
        
        # Test de grossissement d'une région
        test_region = (100, 100, 300, 300)  # (x, y, width, height)
        assert magnifier.magnify_region(test_region)
        assert mock_magnifier.last_region == test_region
        
        # Test de désactivation
        assert magnifier.disable()
        assert not mock_magnifier.enabled
        
        magnifier.cleanup()

def test_error_handling(mock_contrast, mock_shortcuts, mock_braille, mock_magnifier):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.accessibility.contrast._contrast', mock_contrast), \
         patch('nvda_linux.accessibility.shortcuts._shortcuts', mock_shortcuts), \
         patch('nvda_linux.accessibility.braille._braille', mock_braille), \
         patch('nvda_linux.accessibility.magnifier._magnifier', mock_magnifier):
        
        # Test avec des systèmes non initialisés
        mock_contrast.initialized = False
        mock_shortcuts.initialized = False
        mock_braille.initialized = False
        mock_magnifier.initialized = False
        
        assert not contrast.compute_contrast_ratio((0, 0, 0), (255, 255, 255))
        assert not shortcuts.register_shortcut("Ctrl+A", lambda: None, "Test")
        assert not braille.display_text("Test")
        assert not magnifier.set_zoom(2.0)
        
        # Test avec des entrées invalides
        contrast.initialize()
        shortcuts.initialize()
        braille.initialize()
        magnifier.initialize()
        
        assert not contrast.compute_contrast_ratio(None, (255, 255, 255))
        assert not shortcuts.register_shortcut(None, lambda: None, "Test")
        assert not braille.display_text(None)
        assert not magnifier.set_zoom(-1.0)
        
        contrast.cleanup()
        shortcuts.cleanup()
        braille.cleanup()
        magnifier.cleanup()

def test_performance(mock_contrast, mock_shortcuts):
    """Test les performances"""
    with patch('nvda_linux.accessibility.contrast._contrast', mock_contrast), \
         patch('nvda_linux.accessibility.shortcuts._shortcuts', mock_shortcuts):
        
        contrast.initialize()
        shortcuts.initialize()
        
        import time
        
        # Test de performance du calcul de contraste
        start_time = time.time()
        for _ in range(100):  # 100 itérations
            contrast.compute_contrast_ratio((0, 0, 0), (255, 255, 255))
        end_time = time.time()
        contrast_duration = end_time - start_time
        
        # Test de performance des raccourcis
        def dummy_callback():
            pass
        
        start_time = time.time()
        for i in range(100):  # 100 itérations
            shortcuts.register_shortcut(f"Ctrl+{i}", dummy_callback, f"Test {i}")
        end_time = time.time()
        shortcuts_duration = end_time - start_time
        
        # Vérifier que les temps d'exécution sont raisonnables
        assert contrast_duration < 1.0  # Moins d'une seconde pour 100 itérations
        assert shortcuts_duration < 1.0  # Moins d'une seconde pour 100 itérations
        
        contrast.cleanup()
        shortcuts.cleanup() 