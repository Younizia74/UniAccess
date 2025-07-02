#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de gestion d'un widget horloge Android (exemple)
"""

def get_clock_info():
    """Retourne l'heure actuelle (exemple)."""
    from datetime import datetime
    return {
        'heure': datetime.now().strftime('%H:%M'),
        'format': '24h'
    } 