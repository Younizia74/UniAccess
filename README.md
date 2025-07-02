# UniAccess

[![CI/CD](https://github.com/your-username/uniaccess/workflows/CI/CD/badge.svg)](https://github.com/your-username/uniaccess/actions)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/License-MIT%20OR%20Apache--2.0-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Accessibility](https://img.shields.io/badge/Accessibility-Enabled-green.svg)](https://github.com/your-username/uniaccess)

## 🚀 **Opportunité de leadership technique !**

**Nous cherchons des développeurs passionnés par l'accessibilité pour prendre la direction technique de ce projet !**

Ce projet d'accessibilité universelle a été créé avec une vision claire mais le créateur reconnaît ses limites techniques. Si vous êtes un développeur expérimenté passionné par l'accessibilité, nous vous invitons à :

- **Prendre la direction technique** du projet
- **Améliorer l'architecture** et les bonnes pratiques  
- **Guider la communauté** de contributeurs
- **Faire évoluer le projet** selon votre expertise

**Pourquoi rejoindre ce projet ?**
- Impact significatif sur l'accessibilité numérique
- Reconnaissance dans la communauté open source
- Liberté technique pour innover
- Projet avec une base solide déjà établie

**Comment commencer ?**
- Consultez notre [guide de contribution](CONTRIBUTING.md#leadership-technique-et-prise-de-responsabilité)
- Créez une issue avec le label `leadership`
- Présentez votre vision et votre plan d'action

---

Ce projet vise à fournir une solution d'accessibilité universelle (par exemple, synthèse vocale, affichage braille, retour haptique, audio spatial, IA et reconnaissance d'image, etc.) sous Linux (et, à terme, sous Android et Windows) afin de faciliter l'utilisation des applications (par exemple, LibreOffice, éditeurs, applications Android, etc.) par les utilisateurs en situation de handicap.

## Fonctionnalités

- **Synthèse vocale** (via le module speech_backend) : lire à voix haute les informations (textes, notifications, etc.).
- **Affichage braille** (via le module braille) : traduire le texte en braille (par exemple, via BRLTTY).
- **Retour haptique** (via le module haptics) : fournir un retour tactile (vibrations, retour tactile) afin de renforcer l'interaction.
- **Audio spatial** (via le module audio_spatial) : restituer des sons en 3D (spatialisation) afin d'indiquer la position d'un élément dans l'espace.
- **IA et reconnaissance d'image** (via le module ai) : analyser et décrire l'environnement (par exemple, décrire une image ou une interface) à l'aide de l'OCR, de la reconnaissance d'objets, etc.
- **Gestion des entrées** (via le module input_listener) : intercepter les entrées (clavier, souris) et les transmettre au backend AT-SPI afin de communiquer avec les applications.
- **Backend AT-SPI** (via le module atspi_backend) : communiquer avec les applications (par exemple, LibreOffice, éditeurs, applications Android) afin de récupérer les informations (textes, éléments, états, etc.).
- **Configuration et accessibilité** (via le module config, accessibility) : personnaliser le comportement (contraste, raccourcis, loupe, etc.) afin de s'adapter à l'environnement (Linux, Android, Windows).

## Installation

Consultez le [guide d'installation](docs/guide_installation.md) afin de détailler les étapes (par exemple, installer les dépendances, cloner le dépôt, exécuter les tests, lancer l'application, etc.).

## Documentation

- [Schéma d'architecture](docs/architecture.md) : détaille le diagramme et les interactions entre les modules (par exemple, l'interface utilisateur, input_listener, speech_backend, braille, haptics, audio_spatial, ai, atspi_backend, config, accessibility, etc.).
- [Guide d'utilisation avancée](docs/guide_avance.md) : explique comment utiliser les fonctionnalités avancées (contraste, raccourcis, braille, retour haptique, audio spatial, IA, synthèse vocale, etc.).
- [Documentation des API internes](docs/api.md) : détaille les fonctions, classes et paramètres des modules afin de faciliter l'intégration et l'extension du projet.
- [Exemples de code](docs/examples.md) : montre comment utiliser ces API dans des cas concrets (par exemple, calculer le contraste, enregistrer un raccourci, afficher un texte en braille, déclencher une vibration, jouer un son spatial, reconnaître des objets, lire un texte, etc.).
- [Guide de contribution](docs/contributing.md) : détaille les étapes (cloner le dépôt, installer les dépendances, exécuter les tests, soumettre une pull request, etc.) afin que d'autres développeurs puissent contribuer au projet.

## Intégration continue

Le projet intègre un workflow d'intégration continue (CI) (dans [.github/workflows/ci.yml](.github/workflows/ci.yml)) qui lance automatiquement les tests (unitaires, intégration, accessibilité) à chaque push (ou pull request) sur la branche main (via GitHub Actions).

## Système de build

Le projet intègre un Makefile (dans le répertoire racine) qui définit les cibles (install, test, package, clean) afin de faciliter la mise en place du système de build (par exemple, installer les dépendances, exécuter les tests, générer un paquet, nettoyer les fichiers générés).

## À propos du créateur

**Important :** Je ne suis pas développeur de métier, mais j'ai une vision claire de ce que ce projet peut apporter à la communauté de l'accessibilité. J'ai découvert Cursor et l'IA qui m'ont permis de créer cette base, mais je reconnais mes limites techniques.

**Ma vision :** Rendre le monde numérique accessible à tous, peu importe les handicaps. Ce projet vise à combiner IA, multimodalité (voix, braille, haptique, audio spatial) et accessibilité universelle.

**Mon rôle :** Je reste ouvert aux suggestions, aux améliorations et à laisser des développeurs compétents prendre la direction technique du projet. Mon objectif est que ce projet serve la communauté, même si cela signifie le confier à des mains plus expérimentées.

**Pourquoi cette transparence ?** Je préfère être honnête sur mes compétences et mes attentes. Si vous êtes développeur et que ce projet vous intéresse, n'hésitez pas à contribuer ou même à prendre un rôle de leadership technique.

## Contribution

Consultez le [guide de contribution](docs/contributing.md) afin de détailler les étapes (cloner le dépôt, installer les dépendances, exécuter les tests, soumettre une pull request, etc.) pour que d'autres développeurs puissent contribuer au projet.

## Idée d'amélioration (IA semi-autonome)

À terme, nous envisageons d'intégrer une IA (par exemple, via un bot ou un service) qui apprenne (par exemple, via du machine learning ou de l'apprentissage par renforcement) à partir des contributions (par exemple, des commits, des PR, des revues, etc.) afin d'aider (par exemple, en suggérant des améliorations, en détectant des bugs, en générant des tests, en mettant à jour la documentation, etc.) les développeurs et, à terme, d'améliorer le projet de façon semi-autonome. Cette piste (par exemple, en analysant les commits, les PR, les revues, etc. et en proposant des suggestions) pourrait, à terme, faciliter le maintien et accroître la compatibilité du projet.

## Licence

Ce projet est sous licence **MIT** ET **Apache 2.0** (licence duale). Vous pouvez choisir la licence qui vous convient le mieux :

- [Licence MIT](LICENSE) - Simple et permissive
- [Licence Apache 2.0](LICENSE-APACHE) - Avec protection des brevets

Cette approche duale offre une flexibilité maximale aux utilisateurs et contributeurs.

# UniAccess – Accessibilité universelle

## Objectif
Ce projet vise à rendre le monde numérique accessible à tous, sur Linux, Windows, Android, consoles de jeux, et plus encore. Il regroupe des modules pour la gestion de l'accessibilité (voix, braille, haptique, IA, etc.), l'intégration d'applications, et la configuration centralisée.

## Structure du projet

```
uniaccess/
  core/ ...
  apps/ ...
  ...
uniaccess_android/
  apps/
    system/
    user/
    accessibility/
    input_method/
    notification/
    widget/
    service/
    content/
console/
haptics/
spatial_audio/
braille/
models/
docs/
```

## Modules principaux
- **Linux/Windows** : accessibilité, applications, braille, voix, etc.
- **Android** : gestion des apps système, utilisateur, accessibilité, widgets, etc.
- **Console** : support HDMI, manettes, analyse d'interface.
- **Haptique** : retour tactile, contrôleurs personnalisés.
- **Audio spatial** : son 3D, calibration, casques audio.
- **Braille** : afficheurs, traduction, configuration.
- **IA/Models** : reconnaissance d'images, OCR, description d'interface.

## Configuration centralisée
Un fichier de configuration permet de gérer tous les supports (voix, braille, haptique, IA, etc.) et d'adapter l'expérience utilisateur.

## Documentation
Voir le dossier `docs/` pour les guides d'installation, la documentation technique, les tutoriels vidéo, etc.

## Contribution
Toute aide est la bienvenue pour rendre le numérique accessible et digne pour tous !

## Vision
Rendre accessible n'importe quel contenu numérique (PC, Linux, Android, consoles, jeux vidéo...) à tous, grâce à l'IA, la multimodalité (voix, braille, haptique, son spatial...) et des solutions portables, non-invasives et open source.

## Objectifs
- Accessibilité universelle, même pour les jeux vidéo non accessibles
- Solution portable (clé USB, Raspberry Pi, Android...)
- IA pour l'analyse d'image, OCR, description d'interface
- Restitution personnalisable : voix, braille, haptique, son spatial
- Modularité : chaque brique peut être utilisée séparément
- Ouverture à la communauté : chacun peut contribuer, adapter, enrichir

## Cas d'usage
- Lire et naviguer dans des jeux vidéo non accessibles
- Rendre accessible une console de jeux via une carte d'acquisition HDMI
- Utiliser l'IA pour décrire une interface graphique ou un menu
- Restituer l'information par la voix, le braille, le retour haptique ou le son spatial

## Comment contribuer ?
- Forkez le projet, proposez vos modules, corrigez la doc, partagez vos idées !
- Toute contribution (code, doc, tests, matériel, idées) est la bienvenue.

## Pour aller plus loin
- Voir les dossiers spécifiques pour chaque modalité
- Guides d'installation et d'utilisation dans `docs/`
- Exemples de code dans chaque sous-dossier

---

**Ce projet est ouvert, évolutif, et attend vos idées pour rendre le numérique vraiment accessible à tous !** 