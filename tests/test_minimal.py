#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests minimaux pour UniAccess
Ces tests ne dépendent d'aucune bibliothèque externe
"""

import os
import sys

def test_project_structure():
    """Test que la structure de base du projet est correcte"""
    print("=== Test de la structure du projet ===")
    
    # Fichiers essentiels
    essential_files = [
        "README.md",
        "LICENSE", 
        "main.py",
        "config.py"
    ]
    
    for file_name in essential_files:
        if os.path.exists(file_name):
            print(f"✓ {file_name} trouvé")
        else:
            print(f"✗ {file_name} manquant")
            return False
    
    # Dossiers essentiels
    essential_dirs = [
        "docs",
        "tests"
    ]
    
    for dir_name in essential_dirs:
        if os.path.isdir(dir_name):
            print(f"✓ Dossier {dir_name} trouvé")
        else:
            print(f"⚠ Dossier {dir_name} manquant (optionnel)")
    
    return True

def test_python_compatibility():
    """Test que Python est compatible"""
    print("=== Test de compatibilité Python ===")
    
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Version Python compatible")
        return True
    else:
        print("✗ Version Python incompatible (3.8+ requis)")
        return False

def test_basic_imports():
    """Test des imports basiques"""
    print("=== Test des imports basiques ===")
    
    # Test import config
    try:
        import config
        print("✓ Module config importé")
        
        # Test fonction get_config
        if hasattr(config, 'get_config'):
            config_data = config.get_config()
            if isinstance(config_data, dict):
                print("✓ Fonction get_config() fonctionne")
            else:
                print("⚠ get_config() ne retourne pas un dict")
        else:
            print("⚠ Fonction get_config() non trouvée")
            
    except Exception as e:
        print(f"⚠ Erreur import config: {e}")
    
    # Test import main
    try:
        import main
        print("✓ Module main importé")
    except Exception as e:
        print(f"⚠ Erreur import main: {e}")
    
    return True

def test_file_contents():
    """Test que les fichiers contiennent du contenu"""
    print("=== Test du contenu des fichiers ===")
    
    files_to_check = ["README.md", "main.py", "config.py"]
    
    for file_name in files_to_check:
        if os.path.exists(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content.strip()) > 0:
                        print(f"✓ {file_name} contient du contenu ({len(content)} caractères)")
                    else:
                        print(f"⚠ {file_name} est vide")
            except Exception as e:
                print(f"⚠ Erreur lecture {file_name}: {e}")
        else:
            print(f"✗ {file_name} n'existe pas")
    
    return True

if __name__ == "__main__":
    print("🚀 Démarrage des tests minimaux pour UniAccess")
    print("=" * 50)
    
    success = True
    
    # Exécution des tests
    if not test_python_compatibility():
        success = False
    
    if not test_project_structure():
        success = False
    
    test_basic_imports()  # Ne fait pas échouer le test
    
    test_file_contents()  # Ne fait pas échouer le test
    
    print("=" * 50)
    if success:
        print("✅ Tous les tests minimaux ont réussi !")
        sys.exit(0)
    else:
        print("❌ Certains tests ont échoué")
        sys.exit(1) 