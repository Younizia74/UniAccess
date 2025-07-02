#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration globale des tests
Contient les fixtures partagées entre tous les tests
"""

import pytest
import logging
import sys
from pathlib import Path

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

@pytest.fixture(scope="session")
def test_config():
    """Fixture fournissant une configuration de test"""
    return {
        'voix': {
            'moteur': 'espeak',
            'langue': 'fr',
            'vitesse': 180,
            'volume': 100,
            'personnalisation': False  # Désactivé pour les tests
        },
        'braille': {
            'afficheur': 'test',
            'traduction_temps_reel': False,
            'paramètres': {}
        },
        'haptique': {
            'contrôleur': 'test',
            'retour_personnalisé': False
        },
        'audio_spatial': {
            'casque': 'test',
            'calibration': False
        },
        'ia': {
            'reconnaissance_image': False,
            'ocr': False,
            'description_interface': False,
            'navigation_contextuelle': False
        }
    }

@pytest.fixture(scope="session")
def test_logger():
    """Fixture fournissant un logger configuré pour les tests"""
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture fournissant le chemin vers le dossier de données de test"""
    return Path(__file__).parent / 'data'

@pytest.fixture(scope="session")
def mock_atspi():
    """Fixture fournissant un mock de l'interface AT-SPI"""
    class MockAtspi:
        class Role:
            PUSH_BUTTON = 1
            MENU = 2
            MENU_ITEM = 3
            DOCUMENT_FRAME = 4
            TEXT = 5
            ENTRY = 6
            
        class StateType:
            FOCUSED = 1
            
        @staticmethod
        def get_desktop(index):
            return MockDesktop()
            
    class MockDesktop:
        def get_children(self):
            return []
            
    return MockAtspi()

@pytest.fixture(scope="session")
def mock_speech_engine():
    """Fixture fournissant un mock du moteur de synthèse vocale"""
    class MockSpeechEngine:
        def __init__(self):
            self.last_spoken = None
            
        def speak(self, text):
            self.last_spoken = text
            return True
            
        def stop(self):
            self.last_spoken = None
            return True
            
    return MockSpeechEngine()

@pytest.fixture(scope="session")
def mock_input_manager():
    """Fixture fournissant un mock du gestionnaire d'entrées"""
    class MockInputManager:
        def __init__(self):
            self.is_listening = False
            self.last_key = None
            
        def start(self):
            self.is_listening = True
            return True
            
        def stop(self):
            self.is_listening = False
            return True
            
        def simulate_key(self, key):
            self.last_key = key
            return True
            
    return MockInputManager() 