"""Usage : python manage.py purge_journal [--jours N]
Efface les événements du journal plus vieux que settings.JOURNAL_DUREE_JOURS (ou N jours).
À lancer chaque jour (tâche cron ou minuteur systemd) : le RGPD interdit de garder les traces sans limite."""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from journal.models import EvenementAcces


class Command(BaseCommand):
    help = "Efface les événements du journal d'accès plus vieux que la durée de conservation."

    def add_arguments(self, parser):
        parser.add_argument("--jours", type=int, default=settings.JOURNAL_DUREE_JOURS)

    def handle(self, *args, jours, **options):
        limite = timezone.now() - timedelta(days=jours)
        nombre, _ = EvenementAcces.objects.filter(date__lt=limite).delete()
        self.stdout.write(f"{nombre} événement(s) de plus de {jours} jours effacé(s).")
