from django.core.management.base import BaseCommand
from mon_dem.models import Region  # Assurez-vous que le chemin d'importation est correct

class Command(BaseCommand):
    help = 'Populates the database with regions of Belgium'

    def handle(self, *args, **kwargs):
        regions = [
            'Bruxelles-Capitale', 'Flandre', 'Wallonie'
        ]
        for region_name in regions:
            Region.objects.get_or_create(name=region_name)
        self.stdout.write(self.style.SUCCESS('Successfully populated regions'))
