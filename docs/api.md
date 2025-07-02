# Documentation des API internes de NVDA Linux

Ce document détaille les fonctions, classes et paramètres des modules internes de NVDA Linux afin de faciliter l'intégration et l'extension du projet.

## 1. Module de gestion du contraste (contrast)

Ce module permet de calculer le ratio de contraste entre deux couleurs (par exemple, texte et fond) afin de garantir une accessibilité conforme aux normes WCAG (A, AA, AAA).

### Fonctions

- **contrast.initialize()**  
  Initialise le module de gestion du contraste.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **contrast.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **contrast.compute_contrast_ratio(fg, bg)**  
  Calcule le ratio de contraste entre la couleur de premier plan (fg) et celle de l'arrière‑plan (bg).  
  Paramètres :  
  - fg (tuple) : Couleur de premier plan (par exemple, (0, 0, 0) pour le noir).  
  - bg (tuple) : Couleur d'arrière‑plan (par exemple, (255, 255, 255) pour le blanc).  
  Retourne un nombre (ratio de contraste).

- **contrast.is_accessible(fg, bg, level="AA")**  
  Vérifie si le ratio de contraste est suffisant (par exemple, niveau "AA" pour un ratio supérieur ou égal à 4,5).  
  Paramètres :  
  - fg (tuple) : Couleur de premier plan (par exemple, (0, 0, 0) pour le noir).  
  - bg (tuple) : Couleur d'arrière‑plan (par exemple, (255, 255, 255) pour le blanc).  
  - level (str) : Niveau d'accessibilité (par exemple, "A", "AA", "AAA").  
  Retourne un booléen (True si le contraste est suffisant, False sinon).

## 2. Module de gestion des raccourcis (shortcuts)

Ce module permet d'enregistrer, de désenregistrer et de déclencher des raccourcis (par exemple, Ctrl+A, Ctrl+C) afin de lancer des actions (callback) associées.

### Fonctions

- **shortcuts.initialize()**  
  Initialise le module de gestion des raccourcis.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **shortcuts.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **shortcuts.register_shortcut(key, callback, description)**  
  Enregistre un raccourci (par exemple, "Ctrl+A") associé à une fonction (callback) et une description.  
  Paramètres :  
  - key (str) : Raccourci (par exemple, "Ctrl+A").  
  - callback (callable) : Fonction à appeler lors du déclenchement du raccourci.  
  - description (str) : Description du raccourci (par exemple, "Sélectionner tout").  
  Retourne un booléen (True si l'enregistrement a réussi, False sinon).

- **shortcuts.unregister_shortcut(key)**  
  Désenregistre un raccourci (par exemple, "Ctrl+A").  
  Paramètres :  
  - key (str) : Raccourci (par exemple, "Ctrl+A").  
  Retourne un booléen (True si le raccourci a été désenregistré, False sinon).

- **shortcuts.trigger_shortcut(key)**  
  Déclenche manuellement le raccourci (par exemple, lors d'un test ou d'une simulation).  
  Paramètres :  
  - key (str) : Raccourci (par exemple, "Ctrl+A").  
  Retourne un booléen (True si le raccourci a été déclenché, False sinon).

## 3. Module d'affichage braille (braille)

Ce module permet de piloter un afficheur braille (par exemple, via BRLTTY) afin de traduire le texte en braille.

### Fonctions

- **braille.initialize()**  
  Initialise le module d'affichage braille.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **braille.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **braille.connect()**  
  Établit la connexion avec l'afficheur braille (par exemple, via BRLTTY).  
  Retourne un booléen (True si la connexion a réussi, False sinon).

- **braille.disconnect()**  
  Ferme la connexion avec l'afficheur braille.  
  Retourne un booléen (True si la déconnexion a réussi, False sinon).

- **braille.display_text(text)**  
  Affiche un texte en braille sur l'afficheur.  
  Paramètres :  
  - text (str) : Texte à afficher (par exemple, "Hello, world !").  
  Retourne un booléen (True si l'affichage a réussi, False sinon).

- **braille.clear_display()**  
  Efface l'affichage braille.  
  Retourne un booléen (True si l'effacement a réussi, False sinon).

## 4. Module de retour haptique (haptics)

Ce module permet de fournir un retour tactile (vibrations, retour tactile) afin de renforcer l'interaction (par exemple, lors d'un clic ou d'une notification).

### Fonctions

- **haptics.vibrate(duration, intensity)**  
  Déclenche une vibration (par exemple, lors d'un clic sur un bouton).  
  Paramètres :  
  - duration (float) : Durée de la vibration (en secondes).  
  - intensity (float) : Intensité de la vibration (par exemple, entre 0 et 1).  
  Retourne un booléen (True si la vibration a été déclenchée, False sinon).

- **haptics.stop_vibration()**  
  Arrête la vibration en cours.  
  Retourne un booléen (True si la vibration a été arrêtée, False sinon).

## 5. Module d'audio spatial (audio_spatial)

Ce module permet de restituer des sons en 3D (spatialisation) afin d'indiquer la position d'un élément dans l'espace (par exemple, un élément à gauche, à droite, en haut, en bas).

### Fonctions

- **audio_spatial.spatializer.initialize()**  
  Initialise le système d'audio spatial.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **audio_spatial.spatializer.cleanup()**  
  Nettoie le système (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **audio_spatial.spatializer.set_sound_position(x, y, z)**  
  Définit la position d'un son (par exemple, (1, 0, 0) pour un son à droite).  
  Paramètres :  
  - x (float) : Position sur l'axe x (par exemple, 1 pour droite, -1 pour gauche).  
  - y (float) : Position sur l'axe y (par exemple, 1 pour avant, -1 pour arrière).  
  - z (float) : Position sur l'axe z (par exemple, 1 pour haut, -1 pour bas).  
  Retourne un booléen (True si la position a été définie, False sinon).

- **audio_spatial.spatializer.play_sound(sound_id, position=None)**  
  Joue un son (identifié par sound_id) à la position définie (par exemple, (1, 0, 0) pour un son à droite).  
  Paramètres :  
  - sound_id (str) : Identifiant du son (par exemple, "click", "notification").  
  - position (tuple, optionnel) : Position (x, y, z) du son (par exemple, (1, 0, 0)).  
  Retourne un booléen (True si le son a été joué, False sinon).

- **audio_spatial.spatializer.stop_sound(sound_id)**  
  Arrête le son (identifié par sound_id).  
  Paramètres :  
  - sound_id (str) : Identifiant du son (par exemple, "click", "notification").  
  Retourne un booléen (True si le son a été arrêté, False sinon).

## 6. Module d'IA et reconnaissance d'image (ai)

Ce module intègre des fonctionnalités de reconnaissance d'image (OCR, reconnaissance d'objets, description d'interface) afin d'analyser et de décrire l'environnement (par exemple, décrire une image ou une interface).

### Fonctions

- **ai.recognition.initialize()**  
  Initialise le module de reconnaissance d'image.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **ai.recognition.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **ai.recognition.recognize_objects(image)**  
  Reconnaît les objets présents dans une image (par exemple, détecter une personne, une chaise, etc.).  
  Paramètres :  
  - image (PIL.Image) : Image à analyser (par exemple, une image chargée via PIL).  
  Retourne une liste de dictionnaires (par exemple, [{'label': 'person', 'confidence': 0.95, 'box': [x, y, w, h]}, ...]).

- **ai.ocr.initialize()**  
  Initialise le module d'OCR.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **ai.ocr.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **ai.ocr.recognize_text(image, language="fr")**  
  Extrait le texte d'une image (par exemple, extraire le texte d'un document scanné).  
  Paramètres :  
  - image (PIL.Image) : Image à analyser (par exemple, une image chargée via PIL).  
  - language (str, optionnel) : Langue du texte (par exemple, "fr", "en").  
  Retourne une chaîne (le texte extrait).

- **ai.description.initialize()**  
  Initialise le module de description d'interface.  
  Retourne un booléen (True si l'initialisation a réussi, False sinon).

- **ai.description.cleanup()**  
  Nettoie le module (par exemple, libère les ressources).  
  Retourne un booléen (True si le nettoyage a réussi, False sinon).

- **ai.description.describe_element(element)**  
  Décrit un élément d'interface (par exemple, décrire un bouton, un champ de texte, etc.).  
  Paramètres :  
  - element (dict) : Élément à décrire (par exemple, {'role': 'button', 'name': 'OK', 'state': 'enabled'}).  
  Retourne une chaîne (la description de l'élément).

- **ai.description.describe_interface(elements)**  
  Décrit une interface complète (par exemple, décrire une fenêtre, une boîte de dialogue, etc.).  
  Paramètres :  
  - elements (list) : Liste d'éléments (par exemple, [{'role': 'window', 'name': 'Test Window'}, {'role': 'button', 'name': 'OK'}, ...]).  
  Retourne une chaîne (la description de l'interface).

## 7. Module de synthèse vocale (speech_backend)

Ce module permet de lire à voix haute les informations (textes, notifications, etc.) afin de restituer l'information à l'utilisateur.

### Fonctions

- **speech_backend.speak(text, interrupt=True)**  
  Lit un texte (par exemple, lors d'une notification ou d'un changement d'élément).  
  Paramètres :  
  - text (str) : Texte à lire (par exemple, "Hello, world !").  
  - interrupt (bool, optionnel) : Indique si la lecture en cours doit être interrompue (par défaut, True).  
  Retourne un booléen (True si la lecture a été lancée, False sinon).

- **speech_backend.stop()**  
  Interrompt la lecture en cours.  
  Retourne un booléen (True si la lecture a été interrompue, False sinon).

## 8. Module de gestion des entrées (input_listener)

Ce module intercepte les entrées (clavier, souris) et les transmet au backend AT-SPI afin de communiquer avec les applications (par exemple, LibreOffice, éditeurs, applications Android).

### Fonctions

- **input_listener.start()**  
  Démarre l'écoute des entrées (par exemple, lors du démarrage de NVDA Linux).  
  Retourne un booléen (True si l'écoute a été démarrée, False sinon).

- **input_listener.stop()**  
  Arrête l'écoute des entrées (par exemple, lors de l'arrêt de NVDA Linux).  
  Retourne un booléen (True si l'écoute a été arrêtée, False sinon).

## 9. Module backend AT-SPI (atspi_backend)

Ce module communique avec les applications (par exemple, LibreOffice, éditeurs, applications Android) afin de récupérer les informations (textes, éléments, états, etc.) et de les transmettre aux modules de sortie (synthèse vocale, braille, retour haptique, audio spatial, IA).

### Fonctions

- **atspi_backend.get_application_info(app_name)**  
  Récupère les informations d'une application (par exemple, le titre de la fenêtre, les éléments, etc.).  
  Paramètres :  
  - app_name (str) : Nom de l'application (par exemple, "LibreOffice", "Gedit", "Android").  
  Retourne un dictionnaire (par exemple, {'title': 'Document - LibreOffice', 'elements': [...]}).

- **atspi_backend.get_element_info(element)**  
  Récupère les informations d'un élément (par exemple, le rôle, le nom, l'état, etc.).  
  Paramètres :  
  - element (dict) : Élément à interroger (par exemple, {'role': 'button', 'name': 'OK'}).  
  Retourne un dictionnaire (par exemple, {'role': 'button', 'name': 'OK', 'state': 'enabled'}).

## 10. Module de configuration et d'accessibilité (config, accessibility)

Ce module regroupe les fonctionnalités d'accessibilité (contraste, raccourcis, loupe, etc.) afin de personnaliser le comportement de NVDA Linux.

### Fonctions

- **config.load_settings()**  
  Charge les paramètres (par exemple, depuis un fichier de configuration).  
  Retourne un dictionnaire (les paramètres chargés).

- **config.save_settings(settings)**  
  Enregistre les paramètres (par exemple, après une modification par l'utilisateur).  
  Paramètres :  
  - settings (dict) : Dictionnaire des paramètres (par exemple, {'contrast': {'level': 'AA'}, 'shortcuts': {'Ctrl+A': 'Sélectionner tout'}, ...}).  
  Retourne un booléen (True si l'enregistrement a réussi, False sinon).

## Conclusion

Cette documentation des API internes constitue une base pour faciliter l'intégration et l'extension du projet NVDA Linux. N'hésitez pas à consulter le guide d'utilisation avancée (par exemple, dans le fichier `docs/guide_avance.md`) pour des exemples d'utilisation et des cas d'usage. 