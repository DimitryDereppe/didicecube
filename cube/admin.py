from django.contrib import admin

from .models import ImageSkin, Progression, Skin


@admin.register(Progression)
class ProgressionAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "etape_courante", "date_maj")
    readonly_fields = ("date_creation", "date_maj")


class ImageSkinEnLigne(admin.TabularInline):
    model = ImageSkin
    extra = 0


@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ("nom_skin", "utilisateur", "date_ajout")
    inlines = [ImageSkinEnLigne]
