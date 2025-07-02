#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module principal de NVDA-Linux
Gère l'initialisation et la coordination des différents composants
"""

import sys
import logging
import argparse
from pathlib import Path
import atspi_backend
import speech_backend
import input_listener
import config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nvda_linux.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(description='NVDA-Linux - Lecteur d\'écran pour Linux')
    parser.add_argument('--debug', action='store_true', help='Active le mode debug')
    parser.add_argument('--config', type=str, help='Chemin vers le fichier de configuration')
    parser.add_argument('--no-speech', action='store_true', help='Désactive la synthèse vocale')
    parser.add_argument('--no-braille', action='store_true', help='Désactive le support braille')
    return parser.parse_args()

def initialize_components(args):
    """Initialise les différents composants du système"""
    try:
        # Chargement de la configuration
        config_path = args.config or Path.home() / '.config' / 'nvda_linux' / 'config.ini'
        config.load_config(config_path)
        
        # Initialisation des composants
        if not args.no_speech:
            speech_backend.initialize()
        if not args.no_braille:
            atspi_backend.initialize_braille()
        
        atspi_backend.initialize()
        input_listener.initialize()
        
        logger.info("Tous les composants ont été initialisés avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {str(e)}")
        return False

def main():
    """Fonction principale"""
    try:
        args = parse_arguments()
        
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        logger.info("Démarrage de NVDA-Linux...")
        
        if not initialize_components(args):
            logger.error("Échec de l'initialisation, arrêt du programme")
            return 1
        
        # Message de bienvenue
        if not args.no_speech:
            speech_backend.say("Bienvenue sur NVDA-Linux !")
        
        # Démarrage de l'écoute des entrées
        input_listener.listen_keys()
        
        return 0
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return 1
    finally:
        # Nettoyage
        try:
            speech_backend.cleanup()
            atspi_backend.cleanup()
            input_listener.cleanup()
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 