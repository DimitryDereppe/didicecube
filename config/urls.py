from allauth.account.decorators import secure_admin_login
from django.contrib import admin
from django.urls import include, path

# La page de connexion de l'admin renvoie vers celle du site (allauth) : sinon, on pourrait entrer
# dans l'admin avec le seul mot de passe, sans passer par la double authentification.
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Connexion, déconnexion, mot de passe oublié ou à changer, double authentification (sous compte/2fa/) : allauth.
    path("compte/", include("allauth.urls")),
    # Mon compte, export et suppression des données (RGPD).
    path("compte/", include("comptes.urls")),
    path("cube/", include("cube.urls")),
    path("", include("pages.urls")),
]
