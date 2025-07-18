# Registre de Passage Numérique

Cette application Flask permet d'enregistrer les visiteurs et d'exporter le registre hebdomadaire au format PDF. Les données sont stockées dans le fichier `visitors.json` à la racine du projet.

## Installation locale

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

L'application écoute alors sur le port `8000`.

## Déploiement Apache

Un fichier `wsgi.py` expose l'objet `application` attendu par mod_wsgi. Un exemple de configuration est fourni dans `apache.conf` :

```apache
<VirtualHost *:80>
    ServerName example.com
    WSGIDaemonProcess rpn user=www-data group=www-data \
        python-home=/var/www/rpn/venv \
        python-path=/var/www/rpn
    WSGIScriptAlias / /var/www/rpn/wsgi.py
    <Directory /var/www/rpn>
        Require all granted
    </Directory>
</VirtualHost>
```

Le script `setup.sh` crée l'environnement virtuel, installe les dépendances, applique les droits nécessaires sur `visitors.json` et redémarre Apache.

## Utilisation

- Accéder à la page d'accueil pour choisir une **Entrée** ou une **Sortie**.
- La page d'administration `/admin` permet d'exporter le registre de la semaine en PDF.
