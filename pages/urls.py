from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "pages"

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/accueil.html"), name="accueil"),
    path("mentions-legales/", TemplateView.as_view(template_name="pages/mentions_legales.html"), name="mentions_legales"),
    path("sante/", views.sante, name="sante"),
    path("accessibilite/", TemplateView.as_view(template_name="pages/accessibilite.html"), name="accessibilite"),
    path("confidentialite/", TemplateView.as_view(template_name="pages/confidentialite.html"), name="confidentialite"),
]
