from django.db import models
import pycountry
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.core.validators import MinValueValidator

class CustomUser(models.Model):
    name = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=100)
    email = models.EmailField()
    entreprise = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Services(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Pays(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Justification(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Adresse(models.Model):
    TYPE_LOGEMENT_CHOICES = [
        ('APP', 'Appartement'),
        ('MAI', 'Maison'),
        ('BUR', 'Bureau'),
    ]
    rue = models.CharField(max_length=200)
    numero_rue = models.CharField(max_length=10)
    code_postal = models.CharField(max_length=10)
    commune = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=True)
    type_logement = models.CharField(max_length=3, choices=TYPE_LOGEMENT_CHOICES)
    etage = models.IntegerField(default=0)


class MovingRequest(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    adresse_depart = models.ForeignKey(Adresse, related_name='adresses_depart', on_delete=models.CASCADE)
    adresse_arrivee = models.ForeignKey(Adresse, related_name='adresses_arrivee', on_delete=models.CASCADE)
    date_dispo_debut = models.DateField()
    date_dispo_fin = models.DateField()
    volume_estime = models.FloatField(validators=[MinValueValidator(0)])
    recommendation = models.TextField(blank=True)
    national = models.BooleanField(default=False)
    international = models.BooleanField(default=False)
    service = models.ManyToManyField(Services)
    total_send = models.IntegerField(default=0)
    limits_reached = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Calendar(models.Model):
    name = models.CharField(max_length=100)

class Dispo(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='disponibilites')
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=30, blank=True, null=True)
    def __str__(self):
        return f"Disponible du {self.start} au {self.end}"

class Event(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=30)
    all_day = models.BooleanField(default=False)
    dispo = models.ForeignKey(Dispo, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    def __str__(self):
        return self.title

class MovingCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #directement modif depuis settings
    companyname = models.CharField(max_length=100)
    rue = models.CharField(max_length=200)
    numero_rue = models.CharField(max_length=14)
    post_zip = models.CharField(max_length=20)
    TVA = models.CharField(max_length=14)
    #number_employe = models.CharField(max_length=100)
    phonenumber = models.CharField(max_length=100)
    national = models.BooleanField(default=False)
    international = models.BooleanField(default=False)
    region = models.ManyToManyField(Region)
    pays = models.ManyToManyField(Pays)
    service = models.ManyToManyField(Services)
    abonnement = models.IntegerField(default=0)
    total_devis = models.IntegerField(default=0)
    limits_reached = models.BooleanField(default=False)
    devis = models.ManyToManyField(MovingRequest, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    calendar = models.OneToOneField(Calendar, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.companyname

class Complaint(models.Model):
    moving_request = models.ForeignKey(MovingRequest, on_delete=models.CASCADE, related_name='complaints')
    moving_company = models.ForeignKey(MovingCompany, on_delete=models.CASCADE, related_name='complaints')
    justification = models.ManyToManyField(Justification)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plainte de {self.moving_company.companyname} contre Devis #{self.moving_request.id}"

class Review(models.Model):
    company = models.ForeignKey(MovingCompany, on_delete=models.CASCADE, related_name="review")
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="review")
    rating = models.IntegerField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class Presentation(models.Model):
    company = models.OneToOneField(MovingCompany, on_delete=models.CASCADE)
    description = models.TextField()
    #photo = models.ImageField(upload_to='path/to/save/')

class Links(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()
    platform_name = models.CharField(max_length=100)
