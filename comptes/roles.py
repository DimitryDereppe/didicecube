"""Rôles des utilisateurs.

Un rôle = un groupe Django portant le nom du rôle. Un utilisateur peut en avoir un seul
(Cocon : administrateur, editrice ou client) ou plusieurs (AppProject : auxiliaire ET employeur).

Utilisation dans une vue :
    @role_requis("editrice")              -> fonction
    class MaVue(RoleRequisMixin, View):   -> classe, avec roles_requis = ("editrice",)
Dans un gabarit HTML : {% if user|a_le_role:"editrice" %} (charger {% load roles %}).
"""
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied


def cree_groupes_des_roles(**kwargs):
    """Crée les groupes manquants pour chaque rôle déclaré dans settings.ROLES."""
    for role in settings.ROLES:
        Group.objects.get_or_create(name=role)


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
