#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour le support braille
Teste les fonctionnalités de traduction et d'affichage braille
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.braille import display, translator

class MockBrailleDisplay:
    def __init__(self):
        self.connected = False
        self.cells = [0] * 40  # 40 cellules par défaut
        self.last_text = None
        self.last_command = None
        
    def connect(self):
        self.connected = True
        return True
        
    def disconnect(self):
        self.connected = False
        return True
        
    def write_cells(self, cells):
        if len(cells) <= len(self.cells):
            self.cells = cells + [0] * (len(self.cells) - len(cells))
            return True
        return False
        
    def execute_command(self, command):
        self.last_command = command
        return True

class MockBrailleTranslator:
    def __init__(self):
        self.table = {
            'a': [1],
            'b': [1, 2],
            'c': [1, 4],
            ' ': [0],
            '\n': [0, 0, 0, 0]
        }
        
    def translate(self, text):
        result = []
        for char in text.lower():
            if char in self.table:
                result.extend(self.table[char])
            else:
                result.extend([0])
        return result
        
    def translate_reverse(self, cells):
        # Implémentation simplifiée pour les tests
        return "".join(chr(cell + ord('a') - 1) for cell in cells if cell > 0)

@pytest.fixture
def mock_braille_display():
    """Fixture fournissant un mock d'afficheur braille"""
    return MockBrailleDisplay()

@pytest.fixture
def mock_braille_translator():
    """Fixture fournissant un mock de traducteur braille"""
    return MockBrailleTranslator()

def test_braille_display_initialization(mock_braille_display):
    """Test l'initialisation de l'afficheur braille"""
    with patch('nvda_linux.braille.display._display', mock_braille_display):
        assert display.initialize()
        assert mock_braille_display.connected
        assert display.cleanup()
        assert not mock_braille_display.connected

def test_braille_translation(mock_braille_translator):
    """Test la traduction en braille"""
    with patch('nvda_linux.braille.translator._translator', mock_braille_translator):
        # Test de traduction simple
        text = "abc"
        cells = translator.translate(text)
        assert cells == [1, 1, 2, 1, 4]
        
        # Test avec des espaces
        text = "a b"
        cells = translator.translate(text)
        assert cells == [1, 0, 1, 2]
        
        # Test avec des retours à la ligne
        text = "a\nb"
        cells = translator.translate(text)
        assert cells == [1, 0, 0, 0, 0, 1, 2]

def test_braille_display_output(mock_braille_display, mock_braille_translator):
    """Test l'affichage sur l'afficheur braille"""
    with patch('nvda_linux.braille.display._display', mock_braille_display), \
         patch('nvda_linux.braille.translator._translator', mock_braille_translator):
        
        # Initialiser
        display.initialize()
        
        # Test d'affichage simple
        text = "abc"
        assert display.show_text(text)
        assert mock_braille_display.last_text == text
        
        # Vérifier les cellules
        expected_cells = translator.translate(text)
        assert mock_braille_display.cells[:len(expected_cells)] == expected_cells
        
        # Test avec un texte plus long que l'afficheur
        long_text = "a" * 50  # Plus long que les 40 cellules
        assert display.show_text(long_text)
        assert len(mock_braille_display.cells) == 40  # Vérifier la troncature
        
        display.cleanup()

def test_braille_commands(mock_braille_display):
    """Test les commandes de l'afficheur braille"""
    with patch('nvda_linux.braille.display._display', mock_braille_display):
        display.initialize()
        
        # Test des commandes de base
        commands = [
            'clear',
            'scroll_left',
            'scroll_right',
            'home',
            'end'
        ]
        
        for command in commands:
            assert display.execute_command(command)
            assert mock_braille_display.last_command == command
        
        display.cleanup()

def test_braille_error_handling(mock_braille_display, mock_braille_translator):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.braille.display._display', mock_braille_display), \
         patch('nvda_linux.braille.translator._translator', mock_braille_translator):
        
        # Test avec un afficheur non connecté
        mock_braille_display.connected = False
        assert not display.show_text("test")
        
        # Test avec une commande invalide
        display.initialize()
        assert not display.execute_command("commande_invalide")
        
        # Test avec un texte invalide
        assert not display.show_text(None)
        assert not display.show_text("")
        
        display.cleanup()

def test_braille_reverse_translation(mock_braille_translator):
    """Test la traduction inverse (braille vers texte)"""
    with patch('nvda_linux.braille.translator._translator', mock_braille_translator):
        # Test de traduction inverse simple
        cells = [1, 1, 2, 1, 4]  # "abc" en braille
        text = translator.translate_reverse(cells)
        assert text == "abc"
        
        # Test avec des cellules vides
        cells = [1, 0, 1, 2]  # "a b" en braille
        text = translator.translate_reverse(cells)
        assert " " in text

def test_braille_configuration(mock_braille_display):
    """Test la configuration de l'afficheur braille"""
    with patch('nvda_linux.braille.display._display', mock_braille_display):
        display.initialize()
        
        # Test de la configuration du nombre de cellules
        assert display.configure({'cells': 20})
        assert len(mock_braille_display.cells) == 20
        
        # Test de la configuration de la table de traduction
        config = {
            'table': 'fr',
            'contraction': True,
            'dots': 8
        }
        assert display.configure(config)
        
        display.cleanup()

def test_braille_performance(mock_braille_display, mock_braille_translator):
    """Test les performances de l'afficheur braille"""
    with patch('nvda_linux.braille.display._display', mock_braille_display), \
         patch('nvda_linux.braille.translator._translator', mock_braille_translator):
        
        display.initialize()
        
        # Test de performance avec un long texte
        import time
        
        long_text = "a" * 1000
        start_time = time.time()
        
        for _ in range(100):  # 100 itérations
            display.show_text(long_text)
            
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que le temps d'exécution est raisonnable
        assert duration < 1.0  # Moins d'une seconde pour 100 itérations
        
        display.cleanup() 