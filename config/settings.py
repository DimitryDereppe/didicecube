"""Réglages du projet.

Tout ce qui change d'une machine à l'autre (secrets, base, mode debug) vient des
variables d'environnement, lues depuis le fichier .env (voir .env.example).
Rien de secret n'est écrit dans ce fichier.
"""
import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _charge_fichier_env(chemin):
    """Lit un fichier .env simple (CLE=valeur) sans dépendance supplémentaire.

    Une variable déjà définie dans l'environnement (Docker, serveur) garde la priorité.
    """
    if not chemin.exists():
        return
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        os.environ.setdefault(cle.strip(), valeur.strip().strip('"').strip("'"))


_charge_fichier_env(BASE_DIR / ".env")


def env(cle, defaut=None):
    """Renvoie une variable d'environnement ; erreur claire si elle manque et n'a pas de valeur par défaut."""
    valeur = os.environ.get(cle, defaut)
    if valeur is None:
        raise ImproperlyConfigured(f"Variable d'environnement manquante : {cle} (voir .env.example)")
    return valeur


def env_bool(cle, defaut=False):
    return env(cle, str(defaut)).lower() in ("1", "true", "oui", "yes")


def env_liste(cle, defaut=""):
    return [element.strip() for element in env(cle, defaut).split(",") if element.strip()]


# --- Identité du site (utilisée dans les gabarits HTML) -----------------------
SITE_NOM = env("SITE_NOM", "Mon projet")

# --- Sécurité de base ----------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_liste("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_liste("CSRF_TRUSTED_ORIGINS", "")

# --- Applications --------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Connexion, mot de passe oublié et double authentification (module MFA) : django-allauth
    "allauth",
    "allauth.account",
    "allauth.mfa",
    # Applications du socle commun
    "comptes",
    "journal",
    "pages",
    # Application du projet
    "cube",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Requis par django-allauth (suivi des étapes de connexion).
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Renvoie vers l'activation de la double authentification quand elle est obligatoire et pas encore faite.
    # Après MessageMiddleware : il affiche un message pour expliquer la redirection.
    "comptes.middleware.DoubleAuthMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pages.contexte.site",
            ],
        },
    },
]

# --- Base de données : PostgreSQL uniquement ----------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cache : dans la base, partagé par tous les processus ---------------------
# Il sert aux limites d'essais d'allauth (codes de double authentification) et à l'anti-rejeu des codes.
# Un cache en mémoire serait propre à chaque processus gunicorn : avec 3 processus, 3 fois plus d'essais permis.
# La table est créée par « python manage.py createcachetable » (lancé au démarrage, et par les tests).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "cache_django"}}

# --- Comptes -------------------------------------------------------------------
AUTH_USER_MODEL = "comptes.Utilisateur"

# Rôles du projet : un groupe Django par rôle, créé automatiquement après "migrate".
# Chaque projet remplace cette liste par la sienne (ex. Cocon : administrateur, editrice, client).
ROLES = env_liste("ROLES", "administrateur,client")

# Rôles pour lesquels la double authentification est obligatoire (les superutilisateurs l'ont toujours).
# Les autres utilisateurs peuvent l'activer d'eux-mêmes depuis « Mon compte ».
DOUBLE_AUTH_ROLES = env_liste("DOUBLE_AUTH_ROLES", "administrateur")

# Moteur d'authentification : celui de Django, avec la limitation des essais en série en plus.
AUTHENTICATION_BACKENDS = ["comptes.limite_connexion.ModeleAvecLimiteBackend"]
# Par couple (email tapé, adresse IP) : nombre d'essais libres (0 = pas de limite), puis blocage
# qui double à chaque nouvel échec, sans dépasser le plafond. Compteur oublié après une journée sans essai.
CONNEXION_ESSAIS_MAX = int(env("CONNEXION_ESSAIS_MAX", "5"))
CONNEXION_BLOCAGE_SECONDES = int(env("CONNEXION_BLOCAGE_SECONDES", "60"))
CONNEXION_BLOCAGE_MAX_SECONDES = int(env("CONNEXION_BLOCAGE_MAX_SECONDES", "3600"))
CONNEXION_OUBLI_SECONDES = int(env("CONNEXION_OUBLI_SECONDES", str(60 * 60 * 24)))

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "pages:accueil"
LOGOUT_REDIRECT_URL = "pages:accueil"

# --- django-allauth : connexion -------------------------------------------------
# Connexion par email et mot de passe ; le modèle Utilisateur n'a pas de nom d'utilisateur.
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = "comptes.adaptateurs.AdaptateurComptes"
# Formulaire de connexion qui affiche le temps d'attente après trop d'essais (comptes/limite_connexion.py).
ACCOUNT_FORMS = {"login": "comptes.forms.ConnexionForm"}
# Inscription libre fermée par défaut : les comptes sont créés par un administrateur.
INSCRIPTION_OUVERTE = env_bool("INSCRIPTION_OUVERTE", False)
# "optional" : un compte créé par un administrateur peut se connecter sans avoir confirmé son email.
# Un projet qui ouvre l'inscription passe à "mandatory".
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION", "optional")
# Une seule adresse par compte : la changer remplace l'ancienne (après confirmation).
ACCOUNT_CHANGE_EMAIL = True
# Pas de case « Rester connecté » : la session dure SESSION_COOKIE_AGE (8 heures), comme avant.
ACCOUNT_SESSION_REMEMBER = True
# Le mot de passe oublié ne dit pas si l'adresse a un compte.
ACCOUNT_PREVENT_ENUMERATION = True

# --- django-allauth : double authentification (module MFA) ---------------------
# Ordre de préférence : clé de sécurité ou passkey (WebAuthn, résiste à l'hameçonnage), puis application
# d'authentification (code à 6 chiffres), puis codes de secours. Voir comptes/double_auth.py.
MFA_SUPPORTED_TYPES = ["webauthn", "totp", "recovery_codes"]
MFA_ADAPTER = "comptes.double_auth.AdaptateurDoubleAuth"
# Nom affiché dans l'application d'authentification du téléphone.
MFA_TOTP_ISSUER = SITE_NOM
# Codes de secours montrés une seule fois, à la création.
MFA_RECOVERY_CODES_SHOW_ONCE = True
# Connexion par passkey sans mot de passe : désactivée, la clé sert de second facteur après le mot de passe.
MFA_PASSKEY_LOGIN_ENABLED = False
# WebAuthn exige HTTPS, sauf sur localhost en développement.
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG
# Clés de chiffrement des secrets de double authentification (secret de l'application, graine des codes de secours).
# Une ou plusieurs clés Fernet séparées par des virgules : la première chiffre, toutes déchiffrent (rotation).
# Indépendantes de SECRET_KEY : changer SECRET_KEY ne casse pas la double authentification.
# Obligatoire : env() s'arrête avec un message clair si la variable manque.
MFA_CLES_CHIFFREMENT = [cle.strip() for cle in env("MFA_CLES_CHIFFREMENT").split(",") if cle.strip()]

# argon2 en premier : les nouveaux mots de passe sont hachés avec, les anciens restent lisibles.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Export RGPD : fonctions qui ajoutent les données propres au projet à l'export "Mes données".
# Chaque fonction reçoit l'utilisateur et renvoie un dictionnaire. Ex. : "rendezvous.rgpd.export".
EXPORT_DONNEES_FONCTIONS = env_liste("EXPORT_DONNEES_FONCTIONS", "cube.rgpd.donnees_cube")

# --- Journal d'accès -----------------------------------------------------------
# Durée de conservation des événements, en jours (commande : python manage.py purge_journal).
JOURNAL_DUREE_JOURS = int(env("JOURNAL_DUREE_JOURS", "365"))

# --- Courriels -----------------------------------------------------------------
# En développement, les courriels (mot de passe oublié) s'affichent dans la console.
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "ne-pas-repondre@localhost")
EMAIL_HOST = env("EMAIL_HOST", "localhost")
EMAIL_PORT = int(env("EMAIL_PORT", "25"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", False)

# --- Langue et heure -----------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques --------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
if not DEBUG:
    # Production : noms de fichiers avec empreinte (style.3f2a1c.css), pour un cache long sans risque.
    # Demande un collectstatic avant de servir les pages (fait par outils/demarre-production.sh).
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
    }

# Images des skins : jamais servies directement, seulement par la vue cube:image_skin (propriétaire seul).
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))

# --- Sessions et en-têtes de sécurité ------------------------------------------
SESSION_COOKIE_AGE = int(env("SESSION_COOKIE_AGE", str(60 * 60 * 8)))  # 8 heures
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"

if not DEBUG:
    # En production, tout passe par HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Préchargement HSTS volontairement désactivé : une inscription dans la liste des navigateurs
    # est très difficile à annuler. À activer seulement quand le domaine est définitif.
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
    SILENCED_SYSTEM_CHECKS = [] if SECURE_HSTS_PRELOAD else ["security.W021"]
    # Derrière un proxy (Caddy, Nginx) qui termine HTTPS : mettre DERRIERE_PROXY=true.
    if env_bool("DERRIERE_PROXY", False):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Journalisation des erreurs ------------------------------------------------
# Par défaut, Django n'écrit les erreurs dans la console qu'en mode debug : en production, une erreur 500
# serait perdue. Ici, tout part sur la sortie standard (lue par `docker compose logs`), en debug ou non.
# ADMINS (emails séparés par des virgules) reçoit en plus chaque erreur 500 par courriel, hors debug.
# Pendant les tests, la console se tait : les erreurs 403 et 404 provoquées exprès noieraient le résultat.
_EN_TEST = len(sys.argv) > 1 and sys.argv[1] == "test"
ADMINS = [(email, email) for email in env_liste("ADMINS", "")]
SERVER_EMAIL = DEFAULT_FROM_EMAIL
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{asctime} {levelname} {name} : {message}", "style": "{"},
    },
    "filters": {
        "hors_debug": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "CRITICAL" if _EN_TEST else "DEBUG",
        },
        "courriel_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "filters": ["hors_debug"],
        },
    },
    "root": {"handlers": ["console"], "level": env("LOG_NIVEAU", "INFO")},
    "loggers": {
        # Remplace la configuration par défaut de Django (sinon, messages en double en debug).
        "django": {"handlers": ["console", "courriel_admins"], "level": "INFO", "propagate": False},
        # Erreurs des requêtes (500) et de sécurité (CSRF, hôte refusé) : console et courriel.
        "django.request": {"handlers": ["console", "courriel_admins"], "level": "WARNING", "propagate": False},
        "django.security": {"handlers": ["console", "courriel_admins"], "level": "WARNING", "propagate": False},
        # Requêtes SQL : seulement si LOG_NIVEAU=DEBUG et DEBUG=true.
        "django.db.backends": {"level": env("LOG_NIVEAU_SQL", "INFO")},
    },
}
