# Guide de contribution à NVDA Linux

Ce document détaille les étapes à suivre afin de contribuer au projet NVDA Linux. Il s'adresse aux développeurs qui souhaitent améliorer ou étendre le projet (par exemple, corriger un bug, ajouter une fonctionnalité, améliorer la documentation, etc.).

## Prérequis

- Git installé sur votre système (pour cloner le dépôt et gérer les branches).
- Python 3.6 (ou supérieur) installé (pour exécuter le projet et les tests).
- Un gestionnaire de paquets (par exemple, apt, pip) pour installer les dépendances (par exemple, espeak, brltty, etc.).
- Un compte GitHub (pour soumettre une pull request).

## Étapes de contribution

### 1. Cloner le dépôt

Ouvrez un terminal et exécutez la commande suivante afin de cloner le dépôt NVDA Linux (par exemple, dans le répertoire courant) :

```bash
git clone https://github.com/your-org/nvda-linux.git
cd nvda-linux
```

### 2. Créer une branche

Créez une nouvelle branche (par exemple, nommée « fix‑bug‑123 » ou « feature‑new‑module ») afin d'isoler vos modifications. Par exemple, exécutez la commande suivante :

```bash
git checkout -b fix-bug-123
```

### 3. Installer les dépendances

Installez les dépendances (par exemple, espeak, brltty) à l'aide de votre gestionnaire de paquets (par exemple, apt sous Linux ou pkg sous Termux) :

```bash
# Sous Linux (par exemple, Ubuntu)
sudo apt-get update
sudo apt-get install espeak brltty

# Sous Android (par exemple, via Termux)
pkg update
pkg install espeak brltty
```

Ensuite, installez les dépendances Python (par exemple, PIL, numpy, etc.) à l'aide de pip (ou utilisez le Makefile) :

```bash
# Via pip
pip install -r requirements.txt

# Ou via le Makefile
make install
```

### 4. Exécuter les tests

Afin de vérifier que votre environnement est correctement configuré, exécutez les tests (unitaires, intégration, accessibilité) à l'aide de pytest (ou utilisez le Makefile) :

```bash
# Via pytest
pytest tests/

# Ou via le Makefile
make test
```

### 5. Apporter vos modifications

Modifiez le code (par exemple, corriger un bug, ajouter une fonctionnalité, améliorer la documentation, etc.) dans votre branche. N'hésitez pas à consulter la documentation (par exemple, le schéma d'architecture, le guide d'utilisation avancée, la documentation des API internes, les exemples de code) afin de comprendre l'organisation du projet.

### 6. Exécuter les tests (à nouveau)

Après avoir apporté vos modifications, exécutez à nouveau les tests afin de vérifier que votre contribution n'introduit pas de régression :

```bash
# Via pytest
pytest tests/

# Ou via le Makefile
make test
```

### 7. Soumettre une pull request

Commitez vos modifications (par exemple, avec un message clair et concis) puis poussez votre branche sur GitHub :

```bash
git add .
git commit -m "Fix bug 123: … (ou Feature: ajout d'un nouveau module …)"
git push origin fix-bug-123
```

Ensuite, ouvrez une pull request (PR) sur GitHub (par exemple, depuis l'interface web de GitHub) afin que les mainteneurs puissent revoir votre contribution. N'hésitez pas à détailler (par exemple, dans la description de la PR) les modifications apportées et à lier (par exemple, via un numéro d'issue) votre contribution.

### 8. Attendre la revue et intégration

Les mainteneurs (ou d'autres contributeurs) reviendront sur votre PR. Ils pourront vous demander des modifications (par exemple, corriger un bug, améliorer la documentation, ajouter des tests, etc.). Une fois la PR validée, elle sera intégrée (merge) dans la branche principale (par exemple, main).

## Conclusion

Ce guide de contribution constitue une base pour que d'autres développeurs puissent contribuer au projet NVDA Linux. N'hésitez pas à consulter la documentation (par exemple, le schéma d'architecture, le guide d'utilisation avancée, la documentation des API internes, les exemples de code, le guide d'installation) pour plus de détails sur l'organisation, l'utilisation et l'extension du projet. 