from django.urls import path

from . import views

app_name = "cube"

urlpatterns = [
    path("", views.atelier, name="atelier"),
    path("solution/", views.solution, name="solution"),
    path("enregistrer/", views.enregistrer, name="enregistrer"),
    path("progressions/", views.progressions, name="progressions"),
    path("progressions/<int:pk>/supprimer/", views.progression_supprimer, name="progression_supprimer"),
    path("skins/", views.skins, name="skins"),
    path("skins/<int:pk>/supprimer/", views.skin_supprimer, name="skin_supprimer"),
    path("skins/image/<int:pk>/", views.image_skin, name="image_skin"),
]
