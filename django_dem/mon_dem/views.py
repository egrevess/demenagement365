from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchVector
from datetime import datetime
from .models import CustomUser, MovingCompany, MovingRequest, Adresse, Services, Review , Calendar, Dispo, Event
from .forms import MovingRequestForm, AdresseForm, ClientForm, MovingCompanyForm, UserRegistrationForm, ComplaintForm, SearchForm, DispoForm
from django.template.loader import render_to_string
import json

def search_company(request):
    query = request.GET.get('query', '')
    if query:
        companies = MovingCompany.objects.filter(companyname__icontains=query).values('id', 'companyname')[:6]
    else:
        companies = None
    companies_list = list(companies)  # obliger de transformer pour ajax 
    return JsonResponse(companies_list, safe=False) #safe=False parce que je n'envoie pas 
    #un dico mais une liste et que json s'attend a recevoir un dico

def company_info(request, company_id):
    company = get_object_or_404(MovingCompany, id=company_id)
    reviews = company.review.filter(active=True).order_by('?')[:3]
    services = company.service.all()
    email = company.user.email
    template = {'company' : company, 'reviews' : reviews, 'services' : services, 'email' : email}
    return render(request, 'company_info.html', template)

def page_accueil(request):
    services =  Services.objects.all()# Redirigez vers une URL après succès. 
    reviews_pot = Review.objects.filter(active=True)
    reviews = reviews_pot.order_by('?')[:3]
    return render(request, 'page_accueil.html', {'services' : services, 'reviews' : reviews})

def client_register_view(request):
    print("ok")
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            client, created = CustomUser.objects.get_or_create(email=email, defaults=form.cleaned_data)
            if created:
                client_id = client.id
            else:
                client_id = client.id
            return redirect('add_devis', client_id = client_id)  # Redirection après le succès
    else:
        form = ClientForm()  # Formulaire vide pour un GET request
    return render(request, 'client_request.html', {'form': form})

  
def company_register_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        form = MovingCompanyForm(request.POST)
        if all([user_form.is_valid(), form.is_valid()]):
            user = user_form.save()
            calendar = Calendar.objects.create(name="Calendrier de {}".format(form.cleaned_data.get('companyname')))
            moving_company = form.save(commit=False)
            moving_company.user = user
            moving_company.calendar = calendar
            moving_company.save()  # Sauvegarde l'instance MovingCompany
            form.save_m2m()  # Important pour sauvegarder les relations ManyToMany
            #calendar = Calendar.objects.create(company=moving_company)
            #login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('login') #changer par après en login 
    else:
        user_form = UserRegistrationForm()
        form = MovingCompanyForm()
    context = {'form': form, 
                'user_form' : user_form}
    return render(request, 'company_register.html', context)


@login_required
def devis_available(request):
    try:
        company = request.user.movingcompany
        devis_list = company.devis.all()
    except ObjectDoesNotExist:
        company = None
        devis_list = []
    return render(request,'devis_available.html', {'company' : company, 'devis_list': devis_list, 'section' : 'connected'})

@login_required
def submit_complaint(request, request_id):
    moving_request = get_object_or_404(MovingRequest, id=request_id)
    company = request.user.movingcompany
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.moving_request = moving_request
            complaint.moving_company = company
            complaint.save()
            company.devis.remove(moving_request)
            if company.limits_reached == True:
                company.limits_reached = False
            company.total_devis -= 1
            if moving_request.limits_reached == True:
                moving_request.limits_reached = False
            moving_request.total_send -= 1
            company.save()
            moving_request.save()
            # Optionnel : Supprimer le devis après soumission de la plainte
            # est ce que dans ce cas la , company est bien supprimé de devis aussi ? 
            return JsonResponse({'success': True})
        #else :
            #print(form.errors)
            #return JsonResponse({'errors': form.errors.as_json()}, status=400)
    else:
        form = ComplaintForm()
    form_html = render_to_string('complaint_form.html', {'form': form}, request=request)
    return JsonResponse({'form': form_html})

@login_required
def add_event(request):
    company = request.user.movingcompany
    if request.method == "POST":
        form = DispoForm(request.POST)
        if form.is_valid():
            dispo = form.save(commit=False)
            dispo.calendar = company.calendar
            dispo.save()
            
            new_event = Event.objects.create(
                calendar=request.user.movingcompany.calendar,
                title=dispo.description,
                dispo=dispo,
            )
            return JsonResponse({'success': True, 'event_id': new_event.id})
        else:
            return JsonResponse({'errors': form.errors.as_json()}, status=400)
    else:
        form = DispoForm()
    form_html = render_to_string(('form/event_form.html'), {'form' : form}, request=request)
    return JsonResponse({'form': form_html})

@login_required
def calendar_data(request):
    try:
        company = request.user.movingcompany
        calendar = company.calendar
    except MovingCompany.DoesNotExist:
        return HttpResponseBadRequest("L'entreprise de déménagement associée à cet utilisateur n'existe pas.")
    except AttributeError:
        return HttpResponseBadRequest("Cet utilisateur n'a pas de calendrier associé.")
    all_dispo = calendar.disponibilites.all()
    disponibilites_data = [
        {
            "start": dispo.start.isoformat(),
            "end": dispo.end.isoformat(),
            "description": dispo.description
        } for dispo in all_dispo.exclude(events__isnull=False)
    ]

    events_data = [
        {
            "title": event.title,
            "all_day": event.all_day,
            "start": event.dispo.start.isoformat() if event.dispo else None,
            "end": event.dispo.end.isoformat() if event.dispo else None,
            "description": event.dispo.description if event.dispo else None
        } for event in calendar.events.all()
    ]

    data = {
        "calendar_name": calendar.name,
        "disponibilites": disponibilites_data,
        "events": events_data
    }
    return JsonResponse(data, safe=False)


@login_required
def company_page(request):
    try:
        company = request.user.movingcompany
        reviews_pot = company.review.all()
        reviews = reviews_pot.order_by('?')[:3]
    except ObjectDoesNotExist:
        company = None
        reviews = []
    return render(request, 'company_page.html', {'company' : company, 'reviews' : reviews})

@login_required
@require_POST
def review_activate(request):
    review_id = request.POST.get('id')
    action = request.POST.get('action')
    if review_id and action:
        try:
            review = Review.objects.get(id=review_id)
            if action == 'activate':
                review.active = True
            else :
                review.active = False
            review.save()
            return JsonResponse({'status': 'ok'})
        except Review.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


def add_devis(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id)
    if request.method == 'POST':
        moving_request_form = MovingRequestForm(request.POST)
        adresse_depart_form = AdresseForm(request.POST, prefix='depart')
        adresse_arrivee_form = AdresseForm(request.POST, prefix='arrivee')

        if all([
            moving_request_form.is_valid(), 
            adresse_depart_form.is_valid(), 
            adresse_arrivee_form.is_valid()
        ]):
            adresse_depart = adresse_depart_form.save()
            adresse_arrivee = adresse_arrivee_form.save()

            moving_request = moving_request_form.save(commit=False)
            moving_request.adresse_depart = adresse_depart
            moving_request.adresse_arrivee = adresse_arrivee
            moving_request.client = client
            moving_request.save()
            moving_request_form.save_m2m()  # Important pour sauvegarder les données ManyToMany
            return redirect('page_accueil')  # Rediriger vers une page de succès ou autre
    else:
        moving_request_form = MovingRequestForm()
        adresse_depart_form = AdresseForm(prefix='depart')
        adresse_arrivee_form = AdresseForm(prefix='arrivee')

        context = {
            'client': client,
            'moving_request_form': moving_request_form,
            'adresse_depart_form': adresse_depart_form,
            'adresse_arrivee_form': adresse_arrivee_form
        }
    return render(request, 'devis.html', context)

class CustomPasswordChangeView(auth_views.PasswordChangeView):
    def form_valid(self, form):
        # Change le mot de passe
        super().form_valid(form)
        # Déconnecte l'utilisateur
        logout(self.request)
        # Redirige vers la page de connexion ou une autre page
        # rajouter un message pour dire qu'on a bien changé de mot de passe et qu'il faut se reconnecter
        return redirect('login')


        