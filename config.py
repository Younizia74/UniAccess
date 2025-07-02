#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fichier de configuration centralisé pour tous les supports (voix, braille, haptique, IA, etc.)
"""

CONFIG = {
    'voix': {
        'moteur': 'espeak',
        'langue': 'fr',
        'vitesse': 180,
        'volume': 100,
        'personnalisation': True
    },
    'braille': {
        'afficheur': 'brltty',
        'traduction_temps_reel': True,
        'paramètres': {}
    },
    'haptique': {
        'contrôleur': 'default',
        'retour_personnalisé': True
    },
    'audio_spatial': {
        'casque': 'default',
        'calibration': True
    },
    'ia': {
        'reconnaissance_image': True,
        'ocr': True,
        'description_interface': True,
        'navigation_contextuelle': True
    },
    'plateformes': {
        'linux': True,
        'windows': True,
        'android': True,
        'console': True
    }
}

def get_config():
    return CONFIG 