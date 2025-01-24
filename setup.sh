#!/bin/bash en amont lancé cette commande (chmod +x setup.sh)
echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/Scripts/activate
echo "Installation des dépendances..."
pip install -r requirements.txt
echo "Configuration terminée !"
