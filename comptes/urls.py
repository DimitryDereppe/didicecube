from django.urls import path

from . import views

app_name = "comptes"

urlpatterns = [
    path("mes-donnees/", views.mes_donnees, name="mes_donnees"),
    path("mes-donnees/export/", views.export_donnees, name="export_donnees"),
    path("supprimer/", views.supprimer_compte, name="supprimer_compte"),
]
