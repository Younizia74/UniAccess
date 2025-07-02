#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests d'intégration pour les applications Office
Teste l'interaction entre les différents composants pour LibreOffice, Microsoft Office et OnlyOffice
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.apps.office import libreoffice, msoffice, onlyoffice
from nvda_linux.apps.office import get_app_instance, execute_app_action, get_app_document_info

class MockOfficeApp:
    def __init__(self, name, doc_type="document"):
        self.name = name
        self.doc_type = doc_type
        self._document = None
        self._focused = None
        
    def get_document_info(self):
        if not self._document:
            return None
        return {
            'name': self._document.get('name', ''),
            'type': self.doc_type,
            'modified': self._document.get('modified', False)
        }
        
    def execute_action(self, action, **kwargs):
        if action == 'new_document':
            self._document = {'name': 'Nouveau document', 'modified': False}
            return True
        elif action == 'save_document':
            if self._document:
                self._document['modified'] = False
                return True
        return False

@pytest.fixture
def mock_office_apps():
    """Fixture fournissant des mocks pour les applications Office"""
    apps = {
        'libreoffice': MockOfficeApp('LibreOffice'),
        'msoffice': MockOfficeApp('Microsoft Office'),
        'onlyoffice': MockOfficeApp('OnlyOffice')
    }
    return apps

def test_office_app_initialization(mock_office_apps):
    """Test l'initialisation des applications Office"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps):
        # Test LibreOffice
        assert libreoffice.initialize()
        app = get_app_instance('libreoffice')
        assert app is not None
        assert app.name == 'LibreOffice'
        
        # Test Microsoft Office
        assert msoffice.initialize()
        app = get_app_instance('msoffice')
        assert app is not None
        assert app.name == 'Microsoft Office'
        
        # Test OnlyOffice
        assert onlyoffice.initialize()
        app = get_app_instance('onlyoffice')
        assert app is not None
        assert app.name == 'OnlyOffice'

def test_document_operations(mock_office_apps):
    """Test les opérations sur les documents"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps):
        # Test création de document
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            assert execute_app_action(app_name, 'new_document')
            doc_info = get_app_document_info(app_name)
            assert doc_info is not None
            assert doc_info['name'] == 'Nouveau document'
            assert not doc_info['modified']
            
            # Test sauvegarde
            assert execute_app_action(app_name, 'save_document')
            doc_info = get_app_document_info(app_name)
            assert not doc_info['modified']

def test_app_interaction(mock_office_apps, mock_speech_engine):
    """Test l'interaction entre les applications et la synthèse vocale"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps), \
         patch('speech_backend._speech_engine', mock_speech_engine):
        
        # Initialiser les applications
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            app = get_app_instance(app_name)
            assert app is not None
            
            # Créer un document
            assert execute_app_action(app_name, 'new_document')
            
            # Vérifier que la synthèse vocale est appelée
            doc_info = get_app_document_info(app_name)
            assert doc_info is not None
            assert mock_speech_engine.last_spoken is not None

def test_error_handling(mock_office_apps):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps):
        # Test avec une application inexistante
        assert not execute_app_action('inexistant', 'new_document')
        assert get_app_document_info('inexistant') is None
        
        # Test avec une action invalide
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            assert not execute_app_action(app_name, 'action_invalide')
            
        # Test avec une application non initialisée
        mock_office_apps['libreoffice']._document = None
        assert get_app_document_info('libreoffice') is None

def test_multiple_documents(mock_office_apps):
    """Test la gestion de plusieurs documents"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps):
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            # Créer plusieurs documents
            for i in range(3):
                assert execute_app_action(app_name, 'new_document')
                doc_info = get_app_document_info(app_name)
                assert doc_info is not None
                assert doc_info['name'] == 'Nouveau document'
                
                # Sauvegarder chaque document
                assert execute_app_action(app_name, 'save_document')
                doc_info = get_app_document_info(app_name)
                assert not doc_info['modified']

def test_app_cleanup(mock_office_apps):
    """Test le nettoyage des applications"""
    with patch('nvda_linux.apps.office._office_instances', mock_office_apps):
        # Initialiser les applications
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            assert get_app_instance(app_name) is not None
        
        # Nettoyer
        from nvda_linux.apps.office import cleanup
        assert cleanup()
        
        # Vérifier que les instances sont nettoyées
        for app_name in ['libreoffice', 'msoffice', 'onlyoffice']:
            assert get_app_instance(app_name) is None 