# Exemples de code d’utilisation des API internes de NVDA Linux

Ce document fournit des exemples de code afin de montrer comment utiliser les API internes (contrast, shortcuts, braille, haptics, audio_spatial, ai, speech_backend, input_listener, atspi_backend, config) dans des cas concrets.

## 1. Exemple de calcul de contraste (contrast)

```python
# Exemple de calcul du ratio de contraste entre deux couleurs (par exemple, texte noir sur fond blanc)
import nvda_linux.accessibility.contrast as contrast

contrast.initialize()
fg = (0, 0, 0)  # Couleur de premier plan (noir)
bg = (255, 255, 255)  # Couleur d’arrière‑plan (blanc)
ratio = contrast.compute_contrast_ratio(fg, bg)
print("Ratio de contraste :", ratio)  # Par exemple, 21.0 (conforme WCAG AAA)
accessible = contrast.is_accessible(fg, bg, level="AA")
print("Accessible (niveau AA) :", accessible)  # Par exemple, True
contrast.cleanup()
```

## 2. Exemple d’enregistrement et de déclenchement d’un raccourci (shortcuts)

```python
# Exemple d’enregistrement d’un raccourci (par exemple, Ctrl+A) associé à une fonction (callback) et une description
import nvda_linux.accessibility.shortcuts as shortcuts

def on_select_all():
    print("Raccourci Ctrl+A déclenché : Sélectionner tout")

shortcuts.initialize()
shortcuts.register_shortcut("Ctrl+A", on_select_all, "Sélectionner tout")
# Déclenchement manuel (par exemple, lors d’un test)
shortcuts.trigger_shortcut("Ctrl+A")  # Affiche "Raccourci Ctrl+A déclenché : Sélectionner tout"
shortcuts.cleanup()
```

## 3. Exemple d’affichage braille (braille)

```python
# Exemple d’affichage d’un texte en braille (par exemple, via BRLTTY)
import nvda_linux.accessibility.braille as braille

braille.initialize()
if braille.connect():
    braille.display_text("Hello, world !")
    # Effacer l’affichage après un délai (par exemple, 2 secondes)
    import time
    time.sleep(2)
    braille.clear_display()
    braille.disconnect()
braille.cleanup()
```

## 4. Exemple de retour haptique (haptics)

```python
# Exemple de déclenchement d’une vibration (par exemple, lors d’un clic sur un bouton)
import nvda_linux.accessibility.haptics as haptics

haptics.vibrate(duration=0.5, intensity=0.8)  # Vibration de 0,5 seconde avec une intensité de 0,8
# Arrêter la vibration après un délai (par exemple, 0,5 seconde)
import time
time.sleep(0.5)
haptics.stop_vibration()
```

## 5. Exemple d’audio spatial (audio_spatial)

```python
# Exemple de lecture d’un son spatial (par exemple, un son à droite)
import nvda_linux.accessibility.audio_spatial.spatializer as spatializer

spatializer.initialize()
spatializer.set_sound_position(x=1, y=0, z=0)  # Son à droite
spatializer.play_sound("click", position=(1, 0, 0))  # Jouer le son "click" à droite
# Arrêter le son après un délai (par exemple, 1 seconde)
import time
time.sleep(1)
spatializer.stop_sound("click")
spatializer.cleanup()
```

## 6. Exemple de reconnaissance d’objets (ai.recognition)

```python
# Exemple de reconnaissance d’objets dans une image (par exemple, détecter une personne, une chaise, etc.)
import nvda_linux.ai.recognition as recognition
from PIL import Image

recognition.initialize()
# Charger une image (par exemple, une image de test)
image = Image.new("RGB", (100, 100), color="white")
# Reconnaître les objets présents dans l’image
results = recognition.recognize_objects(image)
for obj in results:
    print("Objet :", obj["label"], "Confiance :", obj["confidence"], "Boîte :", obj["box"])
recognition.cleanup()
```

## 7. Exemple d’OCR (ai.ocr)

```python
# Exemple d’extraction de texte d’une image (par exemple, extraire le texte d’un document scanné)
import nvda_linux.ai.ocr as ocr
from PIL import Image

ocr.initialize()
# Charger une image (par exemple, une image de test)
image = Image.new("RGB", (100, 100), color="white")
# Extraire le texte de l’image (par exemple, en français)
text = ocr.recognize_text(image, language="fr")
print("Texte extrait :", text)  # Par exemple, "Texte de test"
ocr.cleanup()
```

## 8. Exemple de description d’élément (ai.description)

```python
# Exemple de description d’un élément d’interface (par exemple, décrire un bouton, un champ de texte, etc.)
import nvda_linux.ai.description as description

description.initialize()
element = {"role": "button", "name": "OK", "state": "enabled"}
desc = description.describe_element(element)
print("Description de l’élément :", desc)  # Par exemple, "Description de test"
description.cleanup()
```

## 9. Exemple de synthèse vocale (speech_backend)

```python
# Exemple de lecture d’un texte (par exemple, lors d’une notification ou d’un changement d’élément)
import nvda_linux.accessibility.speech_backend as speech_backend

speech_backend.speak("Hello, world !", interrupt=True)  # Lire le texte "Hello, world !" (interrompre la lecture en cours)
# Interrompre la lecture après un délai (par exemple, 2 secondes)
import time
time.sleep(2)
speech_backend.stop()
```

## 10. Exemple de gestion des entrées (input_listener)

```python
# Exemple de démarrage et d’arrêt de l’écoute des entrées (par exemple, lors du démarrage ou de l’arrêt de NVDA Linux)
import nvda_linux.accessibility.input_listener as input_listener

input_listener.start()  # Démarrer l’écoute des entrées (clavier, souris)
# Simuler un délai (par exemple, 5 secondes) avant d’arrêter l’écoute
import time
time.sleep(5)
input_listener.stop()  # Arrêter l’écoute des entrées
```

## 11. Exemple de récupération d’informations d’application (atspi_backend)

```python
# Exemple de récupération des informations d’une application (par exemple, le titre de la fenêtre, les éléments, etc.)
import nvda_linux.accessibility.atspi_backend as atspi_backend

app_info = atspi_backend.get_application_info("LibreOffice")
print("Informations de l’application :", app_info)  # Par exemple, {'title': 'Document - LibreOffice', 'elements': [...]}
```

## 12. Exemple de gestion de la configuration (config)

```python
# Exemple de chargement et d’enregistrement des paramètres (par exemple, depuis un fichier de configuration)
import nvda_linux.accessibility.config as config

settings = config.load_settings()
print("Paramètres chargés :", settings)  # Par exemple, {'contrast': {'level': 'AA'}, 'shortcuts': {'Ctrl+A': 'Sélectionner tout'}, ...}
# Modifier un paramètre (par exemple, changer le niveau de contraste)
settings["contrast"]["level"] = "AAA"
config.save_settings(settings)  # Enregistrer les paramètres modifiés
```

## Conclusion

Ces exemples de code constituent une base pour comprendre comment utiliser les API internes de NVDA Linux dans des cas concrets. N’hésitez pas à consulter la documentation des API internes (par exemple, dans le fichier `docs/api.md`) pour plus de détails sur les fonctions et les paramètres. 