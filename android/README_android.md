# NVDA-Linux pour Android (prototype)

## Présentation
Prototype d'un lecteur d'écran inspiré de NVDA, pour Android, en Python (Kivy).

## Installation et lancement

1. Installe Python 3 et Kivy sur ton PC.
2. Installe Buildozer (pour packager l'app sur Android).
3. Place-toi dans le dossier `android/` et lance :
   ```bash
   buildozer android debug deploy run
   ```

## Synthèse vocale réelle (TTS)
- Le bouton "Dire Bonjour" utilise la synthèse vocale Android via pyjnius.
- Si pyjnius n'est pas disponible, un message de simulation s'affiche dans la console.
- Pour la vraie synthèse vocale, il faut que l'app tourne sur un appareil Android.

## Accessibilité avancée (exploration de l'UI)
- Pour interagir avec l'accessibilité Android (comme TalkBack), il faut développer un Accessibility Service en Java/Kotlin.
- On peut ensuite faire communiquer ce service avec l'app Python via des sockets, fichiers, ou une API locale.
- Exemple de squelette Java fourni dans `AccessibilityServiceSkeleton.java` (à créer).

## Structure du dossier
- `main.py` : point d'entrée Kivy
- `requirements_android.txt` : dépendances Python pour Android
- `buildozer.spec` : configuration Buildozer

## Pour aller plus loin
- Ajouter un service d'accessibilité natif (voir doc Android)
- Faire communiquer le service avec l'app Python
- Ajouter des tests 