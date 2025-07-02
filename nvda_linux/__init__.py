#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NVDA-Linux - Lecteur d'écran adapté pour Linux
=============================================

Un lecteur d'écran moderne et puissant, inspiré de NVDA,
offrant une expérience d'accessibilité complète sur Linux.
"""

__version__ = "0.1.0"
__author__ = "NVDA-Linux Team"
__license__ = "MIT"

from .core import (
    accessibility,
    speech,
    braille,
    input,
    config,
)

from .platforms import (
    linux,
    windows,
    android,
)

from .ai import (
    vision,
    nlp,
    ar,
)

from .apps import (
    browsers,
    office,
    games,
)

from .ui import (
    gui,
    cli,
)

def initialize():
    """Initialise tous les composants de NVDA-Linux"""
    from .core.config import initialize as init_config
    from .core.accessibility import initialize as init_accessibility
    from .core.speech import initialize as init_speech
    from .core.braille import initialize as init_braille
    from .core.input import initialize as init_input
    
    # Initialisation dans l'ordre
    init_config()
    init_accessibility()
    init_speech()
    init_braille()
    init_input()
    
    # Initialisation des composants IA si activés
    if config.get("ai", "enabled", False):
        from .ai import initialize as init_ai
        init_ai()
    
    # Initialisation des modules spécifiques
    from .apps import initialize as init_apps
    init_apps()
    
    # Initialisation de l'interface
    from .ui import initialize as init_ui
    init_ui()

def cleanup():
    """Nettoie toutes les ressources"""
    from .core import cleanup as cleanup_core
    from .ai import cleanup as cleanup_ai
    from .apps import cleanup as cleanup_apps
    from .ui import cleanup as cleanup_ui
    
    cleanup_ui()
    cleanup_apps()
    cleanup_ai()
    cleanup_core() 