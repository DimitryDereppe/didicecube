#!/bin/sh
# Usage : outils/sauvegarde.sh   -> copie de la base dans sauvegardes/AAAA-MM-JJ_HHMMSS.dump (pg_dump, format custom)
# Garde SAUVEGARDE_JOURS jours (30 par défaut). À lancer chaque nuit par cron (voir README, « Mise en production »).
# FICHIER_COMPOSE : docker-compose.prod.yml par défaut. Les copies ne sont lisibles que par l'utilisateur courant.
set -eu
cd "$(dirname "$0")/.."
compose="${FICHIER_COMPOSE:-docker-compose.prod.yml}"
jours="${SAUVEGARDE_JOURS:-30}"

umask 077
mkdir -p sauvegardes
horodatage="$(date +%Y-%m-%d_%H%M%S)"
# Jamais deux sauvegardes sous le même nom (ex. copie de sécurité lancée par restaure.sh dans la même seconde).
while [ -e "sauvegardes/$horodatage.dump" ]; do sleep 1; horodatage="$(date +%Y-%m-%d_%H%M%S)"; done
fichier="sauvegardes/$horodatage.dump"
trap 'rm -f "$fichier.partiel"' EXIT

docker compose -f "$compose" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$fichier.partiel"
# Vérifie que la copie est lisible avant de la garder.
docker compose -f "$compose" exec -T db pg_restore --list < "$fichier.partiel" > /dev/null
mv "$fichier.partiel" "$fichier"

find sauvegardes -name '*.dump' -mtime +"$jours" -delete
echo "Sauvegarde : $fichier ($(du -h "$fichier" | cut -f1))"
