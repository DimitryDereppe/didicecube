from django.contrib import admin

from .models import EvenementAcces


@admin.register(EvenementAcces)
class EvenementAccesAdmin(admin.ModelAdmin):
    """Lecture seule : personne, pas même l'administrateur, ne peut créer, modifier ou effacer un événement à la main."""

    list_display = ("date", "action", "utilisateur", "email_saisi", "objet", "adresse_ip")
    list_filter = ("action", "date")
    search_fields = ("utilisateur__email", "email_saisi", "objet", "adresse_ip")
    date_hierarchy = "date"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
