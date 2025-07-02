#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests pour l'IA et la reconnaissance d'image
Teste les fonctionnalités d'IA, OCR et description d'interface
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.ai import recognition, ocr, description

class MockImageRecognition:
    def __init__(self):
        self.initialized = False
        self.models_loaded = {}
        self.last_image = None
        self.last_results = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        self.models_loaded = {}
        return True
        
    def load_model(self, model_name):
        self.models_loaded[model_name] = True
        return True
        
    def recognize_objects(self, image):
        self.last_image = image
        # Simuler des résultats de reconnaissance
        self.last_results = [
            {'label': 'person', 'confidence': 0.95, 'box': [100, 100, 200, 300]},
            {'label': 'chair', 'confidence': 0.85, 'box': [300, 200, 400, 400]}
        ]
        return self.last_results
        
    def estimate_depth(self, image):
        self.last_image = image
        # Simuler une carte de profondeur
        return np.zeros((100, 100), dtype=np.float32)

class MockOCR:
    def __init__(self):
        self.initialized = False
        self.languages = ['fr', 'en']
        self.last_image = None
        self.last_text = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        return True
        
    def recognize_text(self, image, language='fr'):
        self.last_image = image
        self.last_text = "Texte de test"
        return self.last_text
        
    def get_available_languages(self):
        return self.languages

class MockInterfaceDescription:
    def __init__(self):
        self.initialized = False
        self.last_element = None
        self.last_description = None
        
    def initialize(self):
        self.initialized = True
        return True
        
    def cleanup(self):
        self.initialized = False
        return True
        
    def describe_element(self, element):
        self.last_element = element
        self.last_description = "Description de test"
        return self.last_description
        
    def describe_interface(self, elements):
        return "Description de l'interface de test"

@pytest.fixture
def mock_image_recognition():
    """Fixture fournissant un mock de reconnaissance d'image"""
    return MockImageRecognition()

@pytest.fixture
def mock_ocr():
    """Fixture fournissant un mock d'OCR"""
    return MockOCR()

@pytest.fixture
def mock_interface_description():
    """Fixture fournissant un mock de description d'interface"""
    return MockInterfaceDescription()

@pytest.fixture
def test_image():
    """Fixture fournissant une image de test"""
    return Image.new('RGB', (100, 100), color='white')

def test_image_recognition_initialization(mock_image_recognition):
    """Test l'initialisation de la reconnaissance d'image"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition):
        assert recognition.initialize()
        assert mock_image_recognition.initialized
        assert recognition.cleanup()
        assert not mock_image_recognition.initialized

def test_object_recognition(mock_image_recognition, test_image):
    """Test la reconnaissance d'objets"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition):
        recognition.initialize()
        
        # Charger le modèle
        assert recognition.load_model('object_detection')
        
        # Reconnaître les objets
        results = recognition.recognize_objects(test_image)
        assert results is not None
        assert len(results) > 0
        assert 'label' in results[0]
        assert 'confidence' in results[0]
        assert 'box' in results[0]
        
        recognition.cleanup()

def test_depth_estimation(mock_image_recognition, test_image):
    """Test l'estimation de profondeur"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition):
        recognition.initialize()
        
        # Charger le modèle
        assert recognition.load_model('depth_estimation')
        
        # Estimer la profondeur
        depth_map = recognition.estimate_depth(test_image)
        assert depth_map is not None
        assert isinstance(depth_map, np.ndarray)
        assert depth_map.shape == (100, 100)
        
        recognition.cleanup()

def test_ocr_initialization(mock_ocr):
    """Test l'initialisation de l'OCR"""
    with patch('nvda_linux.ai.ocr._ocr', mock_ocr):
        assert ocr.initialize()
        assert mock_ocr.initialized
        assert ocr.cleanup()
        assert not mock_ocr.initialized

def test_text_recognition(mock_ocr, test_image):
    """Test la reconnaissance de texte"""
    with patch('nvda_linux.ai.ocr._ocr', mock_ocr):
        ocr.initialize()
        
        # Reconnaître le texte
        text = ocr.recognize_text(test_image)
        assert text is not None
        assert isinstance(text, str)
        
        # Test avec différentes langues
        for language in mock_ocr.languages:
            text = ocr.recognize_text(test_image, language=language)
            assert text is not None
        
        ocr.cleanup()

def test_interface_description_initialization(mock_interface_description):
    """Test l'initialisation de la description d'interface"""
    with patch('nvda_linux.ai.description._description', mock_interface_description):
        assert description.initialize()
        assert mock_interface_description.initialized
        assert description.cleanup()
        assert not mock_interface_description.initialized

def test_element_description(mock_interface_description):
    """Test la description d'éléments d'interface"""
    with patch('nvda_linux.ai.description._description', mock_interface_description):
        description.initialize()
        
        # Créer un élément de test
        test_element = {
            'role': 'button',
            'name': 'Test Button',
            'state': 'enabled'
        }
        
        # Décrire l'élément
        desc = description.describe_element(test_element)
        assert desc is not None
        assert isinstance(desc, str)
        
        description.cleanup()

def test_interface_description(mock_interface_description):
    """Test la description d'une interface complète"""
    with patch('nvda_linux.ai.description._description', mock_interface_description):
        description.initialize()
        
        # Créer une interface de test
        test_interface = [
            {'role': 'window', 'name': 'Test Window'},
            {'role': 'button', 'name': 'OK'},
            {'role': 'text', 'name': 'Test Text'}
        ]
        
        # Décrire l'interface
        desc = description.describe_interface(test_interface)
        assert desc is not None
        assert isinstance(desc, str)
        
        description.cleanup()

def test_error_handling(mock_image_recognition, mock_ocr, mock_interface_description):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition), \
         patch('nvda_linux.ai.ocr._ocr', mock_ocr), \
         patch('nvda_linux.ai.description._description', mock_interface_description):
        
        # Test avec des systèmes non initialisés
        mock_image_recognition.initialized = False
        mock_ocr.initialized = False
        mock_interface_description.initialized = False
        
        assert not recognition.recognize_objects(None)
        assert not ocr.recognize_text(None)
        assert not description.describe_element(None)
        
        # Test avec des entrées invalides
        recognition.initialize()
        ocr.initialize()
        description.initialize()
        
        assert not recognition.recognize_objects("invalid")
        assert not ocr.recognize_text("invalid")
        assert not description.describe_element("invalid")
        
        recognition.cleanup()
        ocr.cleanup()
        description.cleanup()

def test_model_management(mock_image_recognition):
    """Test la gestion des modèles"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition):
        recognition.initialize()
        
        # Test de chargement de différents modèles
        models = [
            'object_detection',
            'depth_estimation',
            'pose_estimation',
            'face_detection'
        ]
        
        for model in models:
            assert recognition.load_model(model)
            assert model in mock_image_recognition.models_loaded
        
        recognition.cleanup()

def test_performance(mock_image_recognition, mock_ocr, test_image):
    """Test les performances"""
    with patch('nvda_linux.ai.recognition._recognition', mock_image_recognition), \
         patch('nvda_linux.ai.ocr._ocr', mock_ocr):
        
        recognition.initialize()
        ocr.initialize()
        
        import time
        
        # Test de performance de la reconnaissance d'objets
        start_time = time.time()
        for _ in range(10):  # 10 itérations
            recognition.recognize_objects(test_image)
        end_time = time.time()
        recognition_duration = end_time - start_time
        
        # Test de performance de l'OCR
        start_time = time.time()
        for _ in range(10):  # 10 itérations
            ocr.recognize_text(test_image)
        end_time = time.time()
        ocr_duration = end_time - start_time
        
        # Vérifier que les temps d'exécution sont raisonnables
        assert recognition_duration < 5.0  # Moins de 5 secondes pour 10 itérations
        assert ocr_duration < 5.0  # Moins de 5 secondes pour 10 itérations
        
        recognition.cleanup()
        ocr.cleanup() 