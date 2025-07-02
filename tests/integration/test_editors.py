#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests d'intégration pour les éditeurs de texte
Teste l'interaction entre les différents composants pour Gedit, Kate et autres éditeurs
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from nvda_linux.apps.editors import gedit, kate
from nvda_linux.apps.editors import get_editor_instance, execute_editor_action, get_document_info

class MockEditor:
    def __init__(self, name):
        self.name = name
        self._documents = []
        self._current_doc = None
        self._focused = None
        
    def get_documents(self):
        return self._documents
        
    def get_current_document(self):
        return self._current_doc
        
    def execute_action(self, action, **kwargs):
        if action == 'new_document':
            doc = {
                'name': 'Nouveau document',
                'path': '',
                'modified': False,
                'language': 'plain text',
                'encoding': 'UTF-8'
            }
            self._documents.append(doc)
            self._current_doc = doc
            return True
        elif action == 'save_document':
            if self._current_doc:
                self._current_doc['modified'] = False
                return True
        return False

@pytest.fixture
def mock_editors():
    """Fixture fournissant des mocks pour les éditeurs"""
    editors = {
        'gedit': MockEditor('Gedit'),
        'kate': MockEditor('Kate')
    }
    return editors

def test_editor_initialization(mock_editors):
    """Test l'initialisation des éditeurs"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        # Test Gedit
        assert gedit.initialize()
        editor = get_editor_instance('gedit')
        assert editor is not None
        assert editor.name == 'Gedit'
        
        # Test Kate
        assert kate.initialize()
        editor = get_editor_instance('kate')
        assert editor is not None
        assert editor.name == 'Kate'

def test_document_operations(mock_editors):
    """Test les opérations sur les documents"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        for editor_name in ['gedit', 'kate']:
            # Créer un nouveau document
            assert execute_editor_action(editor_name, 'new_document')
            doc_info = get_document_info(editor_name)
            assert doc_info is not None
            assert doc_info['name'] == 'Nouveau document'
            assert not doc_info['modified']
            
            # Sauvegarder le document
            assert execute_editor_action(editor_name, 'save_document')
            doc_info = get_document_info(editor_name)
            assert not doc_info['modified']

def test_editor_interaction(mock_editors, mock_speech_engine):
    """Test l'interaction entre les éditeurs et la synthèse vocale"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors), \
         patch('speech_backend._speech_engine', mock_speech_engine):
        
        for editor_name in ['gedit', 'kate']:
            editor = get_editor_instance(editor_name)
            assert editor is not None
            
            # Créer un document
            assert execute_editor_action(editor_name, 'new_document')
            
            # Vérifier que la synthèse vocale est appelée
            doc_info = get_document_info(editor_name)
            assert doc_info is not None
            assert mock_speech_engine.last_spoken is not None

def test_multiple_documents(mock_editors):
    """Test la gestion de plusieurs documents"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        for editor_name in ['gedit', 'kate']:
            # Créer plusieurs documents
            for i in range(3):
                assert execute_editor_action(editor_name, 'new_document')
                doc_info = get_document_info(editor_name)
                assert doc_info is not None
                assert doc_info['name'] == 'Nouveau document'
                
                # Sauvegarder chaque document
                assert execute_editor_action(editor_name, 'save_document')
                doc_info = get_document_info(editor_name)
                assert not doc_info['modified']

def test_error_handling(mock_editors):
    """Test la gestion des erreurs"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        # Test avec un éditeur inexistant
        assert not execute_editor_action('inexistant', 'new_document')
        assert get_document_info('inexistant') is None
        
        # Test avec une action invalide
        for editor_name in ['gedit', 'kate']:
            assert not execute_editor_action(editor_name, 'action_invalide')
            
        # Test avec un éditeur non initialisé
        mock_editors['gedit']._current_doc = None
        assert get_document_info('gedit') is None

def test_editor_cleanup(mock_editors):
    """Test le nettoyage des éditeurs"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        # Initialiser les éditeurs
        for editor_name in ['gedit', 'kate']:
            assert get_editor_instance(editor_name) is not None
        
        # Nettoyer
        from nvda_linux.apps.editors import cleanup
        assert cleanup()
        
        # Vérifier que les instances sont nettoyées
        for editor_name in ['gedit', 'kate']:
            assert get_editor_instance(editor_name) is None

def test_editor_features(mock_editors):
    """Test les fonctionnalités spécifiques des éditeurs"""
    with patch('nvda_linux.apps.editors._editor_instances', mock_editors):
        for editor_name in ['gedit', 'kate']:
            editor = get_editor_instance(editor_name)
            
            # Test de la coloration syntaxique
            assert execute_editor_action(editor_name, 'set_language', language='python')
            doc_info = get_document_info(editor_name)
            assert doc_info['language'] == 'python'
            
            # Test de l'encodage
            assert execute_editor_action(editor_name, 'set_encoding', encoding='UTF-8')
            doc_info = get_document_info(editor_name)
            assert doc_info['encoding'] == 'UTF-8'
            
            # Test de la recherche
            assert execute_editor_action(editor_name, 'find', text='test')
            
            # Test du remplacement
            assert execute_editor_action(editor_name, 'replace', 
                                      find_text='test', 
                                      replace_text='replacement') 