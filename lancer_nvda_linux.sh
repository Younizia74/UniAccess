#!/bin/bash
# Script de lancement NVDA-Linux sous Linux
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements_linux.txt
cd src
python3 main.py
cd .. 