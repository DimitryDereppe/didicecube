"""Filtre de gabarit : {% load roles %} puis {% if user|a_le_role:"editrice" %}."""
from django import template

from comptes import roles as outils_roles

register = template.Library()


@register.filter
def a_le_role(utilisateur, role):
    return outils_roles.a_le_role(utilisateur, role)
