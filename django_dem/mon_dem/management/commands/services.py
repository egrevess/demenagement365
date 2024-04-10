from django.core.management.base import BaseCommand
from mon_dem.models import Services  # Assurez-vous que le chemin d'importation est correct

class Command(BaseCommand):
    help = 'Populates the database with regions of Belgium'

    def handle(self, *args, **kwargs):
        services = [
            'lift', 'transport', 'garde_meuble', 'location_vehicule'
        ]
        for service in services:
            Services.objects.get_or_create(name=service)
        self.stdout.write(self.style.SUCCESS('Successfully added services'))
