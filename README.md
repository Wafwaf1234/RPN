# Registre de Passage Numérique

Ce projet propose une application web simple permettant de saisir les entrées de visiteurs. Les données sont stockées dans le fichier `visitors.json` et il est possible d'exporter automatiquement le registre hebdomadaire au format PDF.

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

Aucune base de données n'est nécessaire, l'ensemble des enregistrements est conservé dans un fichier JSON côté serveur.

## Utilisation

- Rendez-vous sur la page d'accueil pour remplir le formulaire et signer.
- Une interface d'administration est disponible sur `/admin` pour exporter le registre de la semaine au format PDF.
