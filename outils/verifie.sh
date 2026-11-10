#!/bin/sh
# Usage : outils/verifie.sh [rapide|complet|installe-hook]
#   rapide        : ruff + tests (c'est ce que lance le hook avant chaque commit)
#   complet       : rapide + check --deploy (réglages de production) + pip-audit (failles connues des dépendances)
#   installe-hook : installe le hook git pre-commit qui lance « verifie.sh rapide »
# Tout tourne dans le conteneur « web » (docker compose) : il faut un fichier .env.
# Contourner le hook une fois, en connaissance de cause : git commit --no-verify
set -eu
cd "$(dirname "$0")/.."

mode="${1:-complet}"

if [ "$mode" = "installe-hook" ]; then
    racine="$(git rev-parse --show-toplevel)"
    hook="$racine/.git/hooks/pre-commit"
    # Chemin du projet Django relatif à la racine git (le projet peut être dans un sous-dossier).
    relatif="$(git rev-parse --show-prefix)"
    printf '#!/bin/sh\nexec "%s/%soutils/verifie.sh" rapide\n' "$racine" "$relatif" > "$hook"
    chmod +x "$hook"
    echo "Hook installé : $hook"
    exit 0
fi

lance() { docker compose run --rm --no-deps -T "$@"; }

echo "== ruff (style et erreurs courantes)"
lance web ruff check .

echo "== tests"
docker compose up -d --wait db >/dev/null
lance web python manage.py test --noinput

if [ "$mode" = "complet" ]; then
    echo "== check --deploy (réglages de production)"
    lance -e DEBUG=false web python manage.py check --deploy --fail-level WARNING
    echo "== pip-audit (failles connues des dépendances)"
    lance web pip-audit -r requirements.txt --progress-spinner off
fi

echo "== Tout est bon."
