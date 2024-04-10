from django.core.management.base import BaseCommand
from mon_dem.models import Pays  # Remplacez par le chemin correct de votre modèle
import pycountry

class Command(BaseCommand):
    help = 'Populates the database with countries from pycountry'

    def handle(self, *args, **kwargs):
        for country in pycountry.countries:
            Pays.objects.get_or_create(name=country.name)
        self.stdout.write(self.style.SUCCESS('Successfully populated countries'))
