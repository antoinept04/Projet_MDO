"""
URL configuration for projet_mdo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from gui.models import Editeur
from gui.views import (
    VilleList, VilleCreate,
    AdresseList, AdresseCreate,
    RoleList, RoleCreate,
    PersonneList, personne_create,
    FournisseurList, FournisseurCreate,
    EditeurList, EditeurCreate,
    AuteurList, AuteurCreate,
    LivreList, create_livre, LivreDelete, LivreUpdate, LivreResearch, saisir_isbn,
    EcrireList, EcrireCreate,
    CommanderList, CommanderCreate,
    NotifierList, NotifierCreate,
    AchatList, AchatCreate,
    ReserverList, ReserverCreate,
    loginPage, logoutUser,
    home, create_livre, saisir_nom_editeur, EditeurUpdate, EditeurDelete, AuteurDelete, AuteurUpdate, saisir_ID_auteur, AuteurResearch, EditeurResearch
)

urlpatterns = [
    path('admin/', admin.site.urls),
# Villes
    path('villes/', VilleList.as_view(), name='villes_list'),
    path('villes/create/', VilleCreate.as_view(), name='villes_create'),

    # Adresses
    path('adresses/', AdresseList.as_view(), name='adresses_list'),
    path('adresses/create/', AdresseCreate.as_view(), name='adresses_create'),

    # Roles
    path('roles/', RoleList.as_view(), name='roles_list'),
    path('roles/create/', RoleCreate.as_view(), name='roles_create'),

    # Personnes
    path('personnes/', PersonneList.as_view(), name='personnes_list'),
    path('personnes/create/', personne_create, name='personnes_create'),

    # Fournisseurs
    path('fournisseurs/', FournisseurList.as_view(), name='fournisseurs_list'),
    path('fournisseurs/create/', FournisseurCreate.as_view(), name='fournisseurs_create'),

    # Editeurs
    path('editeurs/', EditeurList.as_view(), name='editeurs_list'),
    path('editeurs/create/', EditeurCreate.as_view(), name='editeurs_create'),
    path('editeurs/update/<str:nom>',EditeurUpdate.as_view(), name='editeurs_update'),
    path('editeurs/saisir_editeur_nom/', saisir_nom_editeur, name='saisir_editeur_nom'),
    path('editeurs/delete/',EditeurDelete.as_view(), name='editeurs_delete'),
    path('editeurs/research/', EditeurResearch.as_view(), name='editeurs_research'),
    # Auteurs
    path('auteurs/', AuteurList.as_view(), name='auteurs_list'),
    path('auteurs/create/', AuteurCreate.as_view(), name='auteurs_create'),
    path('auteurs/delete/',AuteurDelete.as_view(),name='auteurs_delete'),
    path('auteurs/update/<int:auteur_id>/',AuteurUpdate.as_view(), name='auteurs_update'),
    path('auteurs/research/', AuteurResearch.as_view(), name='auteurs_research'),
    path('auteurs/saisir_auteur_ID/',saisir_ID_auteur, name='saisir_auteur_ID'),
    # Livres
    path('livres/', LivreList.as_view(), name='livres_list'),
    path('livres/create/', create_livre, name='livres_create'),
    path('livres/delete/',LivreDelete.as_view(), name='livres_delete'),
    path('livres/saisir_isbn/', saisir_isbn, name='saisir_isbn'),  # Page pour saisir l'ISBN
    path('livres/update/<str:isbn13>/', LivreUpdate.as_view(), name='livre_update'),  # Page pour modifier le livre
    path('livres/research/', LivreResearch.as_view(), name='livres_research'),

    # Ecrire
    path('ecrits/', EcrireList.as_view(), name='ecrits_list'),
    path('ecrits/create/', EcrireCreate.as_view(), name='ecrits_create'),

    # Commander
    path('commandes/', CommanderList.as_view(), name='commandes_list'),
    path('commandes/create/', CommanderCreate.as_view(), name='commandes_create'),

    # Notifier
    path('notifications/', NotifierList.as_view(), name='notifications_list'),
    path('notifications/create/', NotifierCreate.as_view(), name='notifications_create'),

    # Achat
    path('achats/', AchatList.as_view(), name='achats_list'),
    path('achats/create/', AchatCreate.as_view(), name='achats_create'),

    # Reserver
    path('reservations/', ReserverList.as_view(), name='reservations_list'),
    path('reservations/create/', ReserverCreate.as_view(), name='reservations_create'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),
    path('', home, name='homepage')  # Route pour la page d'accueil

]
