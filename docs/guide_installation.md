# Guide d'installation de NVDA Linux

Ce document détaille les étapes pour installer NVDA Linux sur votre système (par exemple, sous Linux ou Android).

## Prérequis

- Python 3.6 (ou supérieur) installé sur votre système.
- Un gestionnaire de paquets (par exemple, apt, pip) pour installer les dépendances.
- Git (pour cloner le dépôt).

## Étapes d'installation

### 1. Installer les dépendances

Sous Linux (par exemple, Ubuntu), vous pouvez installer les dépendances (par exemple, espeak, BRLTTY, etc.) à l'aide de votre gestionnaire de paquets. Par exemple, exécutez la commande suivante dans un terminal :

```bash
sudo apt-get update
sudo apt-get install espeak brltty python3-pip
```

Sous Android, vous pouvez installer les dépendances (par exemple, via Termux) en exécutant (par exemple) :

```bash
pkg update
pkg install espeak brltty python
```

### 2. Cloner le dépôt

Ouvrez un terminal et exécutez la commande suivante afin de cloner le dépôt NVDA Linux (par exemple, dans le répertoire courant) :

```bash
git clone https://github.com/your-org/nvda-linux.git
cd nvda-linux
```

### 3. Installer les dépendances Python (via pip)

Dans le répertoire cloné, exécutez la commande suivante afin d'installer les dépendances Python (par exemple, PIL, numpy, etc.) :

```bash
pip install -r requirements.txt
```

### 4. Exécuter les tests

Afin de vérifier que l'installation est correcte, vous pouvez exécuter les tests (unitaires, intégration, accessibilité) à l'aide de pytest. Par exemple, exécutez la commande suivante dans le répertoire racine du projet :

```bash
pytest tests/
```

### 5. Lancer l'application

Une fois les tests passés, vous pouvez lancer NVDA Linux. Par exemple, exécutez la commande suivante dans le répertoire racine du projet :

```bash
python -m nvda_linux
```

## Conclusion

Ce guide d'installation constitue une base pour installer NVDA Linux sur votre système. N'hésitez pas à consulter la documentation (par exemple, le schéma d'architecture, le guide d'utilisation avancée, la documentation des API internes, les exemples de code) pour plus de détails sur l'utilisation et l'extension du projet. 