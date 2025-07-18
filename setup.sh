#!/bin/bash
set -e

# create virtualenv if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# ensure data file exists with correct permissions
if [ ! -f visitors.json ]; then
    touch visitors.json
fi
chown www-data:www-data visitors.json
chmod 664 visitors.json

# restart apache
systemctl restart apache2
