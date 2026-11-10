#!/bin/sh
# Usage : outils/restaure.sh sauvegardes/FICHIER.dump [--oui]
# Remplace TOUTE la base par la sauvegarde. Demande confirmation (sauf --oui), sauvegarde d'abord l'état actuel,
# et arrête l'application pendant la restauration. FICHIER_COMPOSE : docker-compose.prod.yml par défaut.
set -eu
cd "$(dirname "$0")/.."
compose="${FICHIER_COMPOSE:-docker-compose.prod.yml}"
dump="${1:?Indiquer le fichier de sauvegarde}"
[ -f "$dump" ] || { echo "Fichier introuvable : $dump" >&2; exit 1; }

if [ "${2:-}" != "--oui" ]; then
    printf 'Remplacer toute la base par %s ? Taper « oui » : ' "$dump"
    read -r reponse
    [ "$reponse" = "oui" ] || { echo "Abandon."; exit 1; }
fi

echo "== Sauvegarde de l'état actuel, au cas où"
outils/sauvegarde.sh

docker compose -f "$compose" stop web
docker compose -f "$compose" exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$dump"
docker compose -f "$compose" start web
echo "Restauration faite depuis $dump"
