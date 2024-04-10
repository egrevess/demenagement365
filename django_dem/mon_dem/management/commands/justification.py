from django.core.management.base import BaseCommand
from mon_dem.models import Justification  # Assurez-vous que le chemin d'importation est correct

class Command(BaseCommand):
    help = 'Justifications of devis complaint'

    def handle(self, *args, **kwargs):
        justifications = [
            'Wrong service', 'Wrong geograpic zone', 'Wrong time', 'Wrong country'
        ]
        for justification in justifications:
            Justification.objects.get_or_create(name=justification)
        self.stdout.write(self.style.SUCCESS('Successfully added justifications'))