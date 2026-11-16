"""Rôles des utilisateurs.

Un rôle = un groupe Django portant le nom du rôle. Un utilisateur peut en avoir un seul
(Cocon : administrateur, editrice ou client) ou plusieurs (AppProject : auxiliaire ET employeur).

Utilisation dans une vue :
    @role_requis("editrice")              -> fonction
    class MaVue(RoleRequisMixin, View):   -> classe, avec roles_requis = ("editrice",)
Dans un gabarit HTML : {% if user|a_le_role:"editrice" %} (charger {% load roles %}).
"""
import logging
from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied


def cree_groupes_des_roles(**kwargs):
    """Crée les groupes manquants pour chaque rôle déclaré dans settings.ROLES."""
    for role in settings.ROLES:
        Group.objects.get_or_create(name=role)


def cree_comptes_admins(**kwargs):
    """Garantit que chaque email de settings.COMPTES_ADMINS a un compte superutilisateur.

    Mot de passe : celui de settings.COMPTES_ADMINS_HASH (hash Django) s'il est rempli, remis à chaque
    passage ; sinon compte créé sans mot de passe (« Mot de passe oublié ») et mot de passe existant gardé.
    """
    Utilisateur = get_user_model()
    empreinte = settings.COMPTES_ADMINS_HASH
    if empreinte:
        try:
            identify_hasher(empreinte)
        except ValueError:
            logging.getLogger(__name__).warning("COMPTES_ADMINS_HASH n'est pas un hash Django valide : ignoré.")
            empreinte = ""
    for email in settings.COMPTES_ADMINS:
        utilisateur = Utilisateur.objects.filter(email__iexact=email).first()
        if utilisateur is None:
            utilisateur = Utilisateur.objects.create_superuser(email=email, password=None)
        elif not (utilisateur.is_staff and utilisateur.is_superuser):
            utilisateur.is_staff = utilisateur.is_superuser = True
            utilisateur.save(update_fields=["is_staff", "is_superuser"])
        if empreinte and utilisateur.password != empreinte:
            utilisateur.password = empreinte
            utilisateur.save(update_fields=["password"])
        if "administrateur" in settings.ROLES:
            donne_role(utilisateur, "administrateur")


def roles_de(utilisateur):
    """Liste des rôles d'un utilisateur (vide s'il n'est pas connecté)."""
    if not utilisateur.is_authenticated:
        return []
    return list(utilisateur.groups.filter(name__in=settings.ROLES).values_list("name", flat=True))


def a_le_role(utilisateur, *roles):
    """Vrai si l'utilisateur a au moins un des rôles demandés."""
    inconnus = set(roles) - set(settings.ROLES)
    if inconnus:
        # Une faute de frappe dans un nom de rôle ne doit pas ouvrir ni fermer l'accès en silence.
        raise ValueError(f"Rôle(s) inconnu(s) : {', '.join(sorted(inconnus))}. Voir settings.ROLES.")
    if not utilisateur.is_authenticated or not utilisateur.is_active:
        return False
    return utilisateur.groups.filter(name__in=roles).exists()


def donne_role(utilisateur, role):
    """Ajoute un rôle à un utilisateur (utile dans les tests et les scripts)."""
    if role not in settings.ROLES:
        raise ValueError(f"Rôle inconnu : {role}. Voir settings.ROLES.")
    groupe, _ = Group.objects.get_or_create(name=role)
    utilisateur.groups.add(groupe)


def role_requis(*roles):
    """Décorateur de vue : connexion obligatoire, puis erreur 403 si aucun des rôles n'est présent."""

    def decorateur(vue):
        @wraps(vue)
        @login_required
        def vue_protegee(request, *args, **kwargs):
            if not a_le_role(request.user, *roles):
                raise PermissionDenied
            return vue(request, *args, **kwargs)

        return vue_protegee

    return decorateur


class RoleRequisMixin(LoginRequiredMixin):
    """Même chose que role_requis, pour les vues sous forme de classe."""

    roles_requis = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not a_le_role(request.user, *self.roles_requis):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
