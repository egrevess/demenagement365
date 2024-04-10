from django.urls import path
from . import views
from django.urls import include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('page_accueil/', views.page_accueil, name='page_accueil'),
	path('page_accueil/company_info/<int:company_id>/', views.company_info, name='company_info'),
	path('company_register_view/', views.company_register_view, name='company_register'),
	path('client_register_view/', views.client_register_view, name='client_register'),
	path('add_devis/<int:client_id>/', views.add_devis, name='add_devis'),
	path('devis_available/', views.devis_available, name='devis_available'),
	# login / logout urls de Django (pas besoin de les créer moi même)
	path('', include('django.contrib.auth.urls')),
	path('devis_available/complaint/<int:request_id>/', views.submit_complaint, name='submit_complaint'),
	path('home/', views.company_page, name='company_page'),
	path('activate/', views.review_activate, name='review_activate'),
	path('search/', views.search_company, name='search_company'),
	path('calendar_data/', views.calendar_data, name='calendar_data'),
	path('add_event/', views.add_event, name='add_event'),
    # Ajoutez d'autres URL ici
]