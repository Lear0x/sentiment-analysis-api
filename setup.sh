#!/bin/bash
echo "Création de l'environnement virtuel..."
python -m venv venv
source venv/Scripts/activate
echo "Installation des dépendances..."
pip install -r requirements.txt
echo "Configuration terminée !"
