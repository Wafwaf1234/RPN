# Registre de Passage Numérique

Ce projet propose une application web simple permettant de saisir les entrées de visiteurs et d'exporter le registre hebdomadaire au format PDF.

## Installation

1. Installer les dépendances Python:
   ```bash
   pip install -r requirements.txt
   ```
2. Lancer le serveur Flask:
   ```bash
   python main.py
   ```

L'application écoute par défaut sur le port `8000`.

## Utilisation

- Rendez-vous sur la page d'accueil pour remplir le formulaire et signer.
- La page `/export` permet de télécharger le registre de la semaine courante au format PDF.
