#!/bin/sh
# Usage : lancé par Dockerfile.prod au démarrage du conteneur (pas à la main).
# Applique les migrations, crée la table du cache, copie les fichiers statiques (servis par Caddy), puis lance gunicorn.
set -eu
python manage.py migrate --noinput
python manage.py createcachetable
python manage.py collectstatic --noinput
# --forwarded-allow-ips "*" : seul Caddy joint ce conteneur (aucun port ouvert vers l'extérieur).
exec gunicorn config.wsgi \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile - \
    --forwarded-allow-ips "*"
