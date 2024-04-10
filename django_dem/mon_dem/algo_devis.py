from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MovingRequest, MovingCompany, Complaint, Calendar, Dispo
from django.db.models import Q
from django.db.models import Count

def upload_company(entreprise):
    #if entreprise.exist():
    entreprise.total_devis += 1
    if entreprise.total_devis == entreprise.abonnement:
        entreprise.limits_reached = True
    entreprise.save()

def add_devis(entreprises, moving_request):
    entreprises_aleatoires = entreprises.order_by('?')[:7]
    for entreprise in entreprises_aleatoires:
            entreprise.devis.add(moving_request)
            upload_company(entreprise)
            moving_request.total_send += 1
            if moving_request.total_send == 7:
                break
    if moving_request.total_send == 7:
        moving_request.limits_reached = True
    moving_request.save() 
    # if moving_request n'a pas sa limit reached a True , elle doit etre recup comme demande en attente 
        
# Définition de la fonction réceptrice
@receiver(post_save, sender=MovingRequest)
def assigner_devis(sender, instance, created, **kwargs):
    if created:
        # Ce code est exécuté après la création d'un nouvel objet MovingRequest
        national = instance.national
        date_debut_client = instance.date_dispo_debut
        date_fin_client = instance.date_dispo_fin
        entreprises_disponibles = MovingCompany.objects.filter( 
        #vérifie si la disponibilité de l'entreprise commence avant ou est égale à la date de début du client et se termine après ou est égale à cette même date.
        Q(calendar__disponibilites__start__lte=date_debut_client, calendar__disponibilites__end__gte=date_debut_client) | 
		Q(calendar__disponibilites__start__lte=date_fin_client, calendar__disponibilites__end__gte=date_fin_client) |
		Q(calendar__disponibilites__start__gte=date_debut_client, calendar__disponibilites__end__lte=date_fin_client),
        Q(limits_reached=False)).distinct()
        for i in entreprises_disponibles:
            print(i)
        if entreprises_disponibles.exists():
            region_devis = instance.adresse_depart.region
            entreprises_region = entreprises_disponibles.filter(region__name=region_devis)
            if entreprises_region.exists():
                services = instance.service.all()
                services_ids = services.values_list('id', flat=True)
                entreprises_services_all = entreprises_region.annotate(
                    nombre_services_correspondants=Count(
                        'service', filter=Q(service__id__in=services_ids)
                    )
                ).filter(nombre_services_correspondants__gte=len(services_ids)) 
                if entreprises_services_all.exists():
                    entreprises_selectionnees = entreprises_services_all
                else:
                    entreprises_avec_un_service = entreprises_region.filter(service__id__in=services_ids).distinct()
                    entreprises_selectionnees = entreprises_avec_un_service
                if entreprises_selectionnees.exists():
                    if national == True:
                        entreprises = entreprises_selectionnees.filter(national=True)
                        if entreprises.exists():
                            add_devis(entreprises, instance)
                    else:
                        entreprises = entreprises_selectionnees.filter(pays=instance.adresse_arrivee.pays)
                        if entreprises.exists():
                            add_devis(entreprises, instance)
            

# Il faut que je change l'algo de tri des dates, et mette directement dans les modeles un Daterangefield,
# je dois donc juste rajouter dans les forms des dates de dipos et directemnt les implémentées dans daterange.
# 
