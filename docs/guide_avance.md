# Guide d'utilisation avancée de NVDA Linux

## Contexte du projet

**Note importante :** Ce projet a été initié par quelqu'un qui n'est pas développeur de métier, mais qui a une vision claire de l'accessibilité universelle. L'utilisation de Cursor et de l'IA a permis de créer cette base, mais nous reconnaissons qu'il y a encore beaucoup d'améliorations possibles.

**Notre objectif :** Créer une solution d'accessibilité complète et innovante, même si cela signifie confier le développement technique à des mains plus expérimentées.

**Votre contribution :** Si vous êtes développeur et que ce projet vous intéresse, n'hésitez pas à proposer des améliorations, à prendre l'initiative ou même à devenir mainteneur du projet.

## Fonctionnalités avancées

Ce guide détaille les fonctionnalités avancées de NVDA Linux et explique comment les utiliser afin de personnaliser et d'améliorer l'expérience d'accessibilité.

## 1. Gestion du contraste

Le module de gestion du contraste (contrast) permet de calculer le ratio de contraste entre deux couleurs (par exemple, texte et fond) afin de garantir une accessibilité conforme aux normes WCAG (A, AA, AAA).

### Exemple d'utilisation

- Utilisez la fonction `contrast.compute_contrast_ratio(fg, bg)` pour calculer le ratio de contraste entre la couleur de premier plan (fg) et celle de l'arrière‑plan (bg).
- Utilisez la fonction `contrast.is_accessible(fg, bg, level)` pour vérifier si le contraste est suffisant (par exemple, niveau "AA" pour un ratio supérieur ou égal à 4,5).

## 2. Gestion des raccourcis

Le module de gestion des raccourcis (shortcuts) permet d'enregistrer, de désenregistrer et de déclencher des raccourcis (par exemple, Ctrl+A, Ctrl+C) afin de lancer des actions (callback) associées.

### Exemple d'utilisation

- Utilisez la fonction `shortcuts.register_shortcut(key, callback, description)` pour enregistrer un raccourci (par exemple, "Ctrl+A" associé à une fonction de sélection).
- Utilisez la fonction `shortcuts.unregister_shortcut(key)` pour désenregistrer un raccourci.
- Utilisez la fonction `shortcuts.trigger_shortcut(key)` pour déclencher manuellement le raccourci (par exemple, lors d'un test ou d'une simulation).

## 3. Affichage braille

Le module d'affichage braille (braille) permet de piloter un afficheur braille (par exemple, via BRLTTY) afin de traduire le texte en braille.

### Exemple d'utilisation

- Utilisez la fonction `braille.connect()` pour établir la connexion avec l'afficheur braille.
- Utilisez la fonction `braille.display_text(text)` pour afficher un texte en braille.
- Utilisez la fonction `braille.clear_display()` pour effacer l'affichage.
- Utilisez la fonction `braille.disconnect()` pour fermer la connexion.

## 4. Retour haptique

Le module de retour haptique (haptics) permet de fournir un retour tactile (vibrations, retour tactile) afin de renforcer l'interaction (par exemple, lors d'un clic ou d'une notification).

### Exemple d'utilisation

- Utilisez la fonction `haptics.vibrate(duration, intensity)` pour déclencher une vibration (par exemple, lors d'un clic sur un bouton).
- Utilisez la fonction `haptics.stop_vibration()` pour arrêter la vibration.

## 5. Audio spatial

Le module d'audio spatial (audio_spatial) permet de restituer des sons en 3D (spatialisation) afin d'indiquer la position d'un élément dans l'espace (par exemple, un élément à gauche, à droite, en haut, en bas).

### Exemple d'utilisation

- Utilisez la fonction `audio_spatial.spatializer.initialize()` pour initialiser le système d'audio spatial.
- Utilisez la fonction `audio_spatial.spatializer.set_sound_position(x, y, z)` pour définir la position d'un son (par exemple, (1, 0, 0) pour un son à droite).
- Utilisez la fonction `audio_spatial.spatializer.play_sound(sound_id, position)` pour jouer un son à la position définie.
- Utilisez la fonction `audio_spatial.spatializer.cleanup()` pour nettoyer le système.

## 6. IA et reconnaissance d'image

Le module d'IA (ai) intègre des fonctionnalités de reconnaissance d'image (OCR, reconnaissance d'objets, description d'interface) afin d'analyser et de décrire l'environnement (par exemple, décrire une image ou une interface).

### Exemple d'utilisation

- Utilisez la fonction `ai.recognition.recognize_objects(image)` pour reconnaître les objets présents dans une image (par exemple, détecter une personne, une chaise, etc.).
- Utilisez la fonction `ai.ocr.recognize_text(image, language)` pour extraire le texte d'une image (par exemple, extraire le texte d'un document scanné).
- Utilisez la fonction `ai.description.describe_element(element)` pour décrire un élément d'interface (par exemple, décrire un bouton, un champ de texte, etc.).

## 7. Synthèse vocale

Le module de synthèse vocale (speech_backend) permet de lire à voix haute les informations (textes, notifications, etc.) afin de restituer l'information à l'utilisateur.

### Exemple d'utilisation

- Utilisez la fonction `speech_backend.speak(text, interrupt=True)` pour lire un texte (par exemple, lors d'une notification ou d'un changement d'élément).
- Utilisez la fonction `speech_backend.stop()` pour interrompre la lecture.

## 8. Gestion des entrées (input_listener)

Le module de gestion des entrées (input_listener) intercepte les entrées (clavier, souris) et les transmet au backend AT-SPI afin de communiquer avec les applications (par exemple, LibreOffice, éditeurs, applications Android).

### Exemple d'utilisation

- Utilisez la fonction `input_listener.start()` pour démarrer l'écoute des entrées (par exemple, lors du démarrage de NVDA Linux).
- Utilisez la fonction `input_listener.stop()` pour arrêter l'écoute (par exemple, lors de l'arrêt de NVDA Linux).

## 9. Backend AT-SPI (atspi_backend)

Le module backend AT-SPI (atspi_backend) communique avec les applications (par exemple, LibreOffice, éditeurs, applications Android) afin de récupérer les informations (textes, éléments, états, etc.) et de les transmettre aux modules de sortie (synthèse vocale, braille, retour haptique, audio spatial, IA).

### Exemple d'utilisation

- Utilisez la fonction `atspi_backend.get_application_info(app_name)` pour récupérer les informations d'une application (par exemple, le titre de la fenêtre, les éléments, etc.).
- Utilisez la fonction `atspi_backend.get_element_info(element)` pour récupérer les informations d'un élément (par exemple, le rôle, le nom, l'état, etc.).

## 10. Configuration et accessibilité (config, accessibility)

Le module de configuration et d'accessibilité (config, accessibility) regroupe les fonctionnalités d'accessibilité (contraste, raccourcis, loupe, etc.) afin de personnaliser le comportement de NVDA Linux.

### Exemple d'utilisation

- Utilisez la fonction `config.load_settings()` pour charger les paramètres (par exemple, depuis un fichier de configuration).
- Utilisez la fonction `config.save_settings(settings)` pour enregistrer les paramètres (par exemple, après une modification par l'utilisateur).

## Conclusion

Ce guide d'utilisation avancée constitue une base pour personnaliser et améliorer l'expérience d'accessibilité de NVDA Linux. N'hésitez pas à consulter la documentation des API internes (par exemple, dans le fichier `docs/api.md`) pour plus de détails sur les fonctions et les paramètres. 