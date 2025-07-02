#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests basiques pour UniAccess
Ces tests vérifient que les modules principaux peuvent être importés
"""

import sys
import os

# Ajoute le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_config():
    """Test que le module config peut être importé"""
    try:
        import config
        assert config is not None
        print("✓ Module config importé avec succès")
    except ImportError as e:
        print(f"✗ Erreur d'import config: {e}")
        raise

def test_import_main():
    """Test que le module main peut être importé"""
    try:
        import main
        assert main is not None
        print("✓ Module main importé avec succès")
    except ImportError as e:
        print(f"✗ Erreur d'import main: {e}")
        raise

def test_config_structure():
    """Test que la configuration a la structure attendue"""
    try:
        import config
        config_data = config.get_config()
        assert isinstance(config_data, dict)
        assert 'voix' in config_data
        assert 'braille' in config_data
        print("✓ Structure de configuration valide")
    except Exception as e:
        print(f"✗ Erreur de structure config: {e}")
        raise

def test_project_files():
    """Test que les fichiers principaux du projet existent"""
    required_files = [
        'README.md',
        'LICENSE',
        'main.py',
        'config.py',
        'requirements.txt'
    ]
    
    for file_name in required_files:
        assert os.path.exists(file_name), f"Fichier {file_name} manquant"
        print(f"✓ Fichier {file_name} trouvé")

def test_python_version():
    """Test que la version Python est compatible"""
    version = sys.version_info
    assert version.major == 3, "Python 3 requis"
    assert version.minor >= 8, "Python 3.8+ requis"
    print(f"✓ Version Python compatible: {version.major}.{version.minor}.{version.micro}")

if __name__ == "__main__":
    print("Démarrage des tests basiques pour UniAccess...")
    
    test_python_version()
    test_project_files()
    test_import_config()
    test_import_main()
    test_config_structure()
    
    print("✅ Tous les tests basiques ont réussi !") 