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
from gui.models import Editeur, Illustrateur, Commander
from gui.views import (
    VilleList, VilleCreate,
    AdresseList, create_adresse,
    RoleList, RoleCreate,
    PersonneList, personne_create, PersonneDelete, PersonneUpdate, PersonneSelectView,
    FournisseurList, FournisseurCreate,
    EditeurList, EditeurCreate,
    AuteurList, AuteurCreate,
    LivreList, create_livre, LivreDelete, LivreUpdate, LivreResearch, saisir_isbn, PersonneResearch, AdresseResearch,
    AdresseList, AdresseDelete,
    EcrireList, EcrireCreate,
    CommanderList, CommanderCreate, CommanderUpdate, CommanderDelete, CommanderSearchResult, terminer_commande, saisir_ID_commande,
    NotificationList,
    AchatList, AchatCreate, AchatUpdate, AchatDelete, AchatSearchResult,
    ReserverList, ReserverCreate, ReserverUpdate, ReserverDelete, ReserverSearchResult, terminer_reservation,
    loginPage, logoutUser,
    home, create_livre, EditeurUpdate, EditeurDelete, AuteurDelete, AuteurUpdate, saisir_ID_auteur,
    AuteurResearch, EditeurResearch, saisir_ID_editeur, IllustrateurList, IllustrateurCreate, IllustrateurResearch,
    IllustrateurDelete, IllustrateurUpdate, saisir_ID_illustrateur, TraducteurList, TraducteurCreate,
    TraducteurResearch, TraducteurDelete, TraducteurUpdate, saisir_ID_traducteur,
    FournisseurResearch, FournisseurDelete, FournisseurUpdate, SaisirIDFournisseurView, FournisseurCreate,
    FournisseurList, saisir_ID_commande,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='homepage'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),


    path('villes/', VilleList.as_view(), name='villes_list'),
    path('villes/create/', VilleCreate.as_view(), name='villes_create'),


    path('adresses/', AdresseList.as_view(), name='adresses_list'),
    path('adresses/create/', create_adresse, name='adresses_create'),
    path('adresses/research/', AdresseResearch.as_view(), name='adresses_research'),
    path('adresses/delete/',AdresseDelete.as_view(), name='adresses_delete'),


    path('roles/', RoleList.as_view(), name='roles_list'),
    path('roles/create/', RoleCreate.as_view(), name='roles_create'),


    path('personnes/', PersonneList.as_view(), name='personnes_list'),
    path('personnes/create/', personne_create, name='personnes_create'),
    path('personnes/research/', PersonneResearch.as_view(), name='personnes_research'),
    path('personnes/delete/',PersonneDelete.as_view(), name='personnes_delete'),
    path('personnes/modifier/', PersonneSelectView.as_view(), name='personnes_select'),  # Sélection de la personne à modifier
    path('personnes/modifier/<str:email>/', PersonneUpdate.as_view(), name='personnes_update'),  # Modification de la personne






    path('editeurs/', EditeurList.as_view(), name='editeurs_list'),
    path('editeurs/create/', EditeurCreate.as_view(), name='editeurs_create'),
    path('editeurs/update/<int:id>',EditeurUpdate.as_view(), name='editeurs_update'),
    path('editeurs/saisir_editeur_ID/', saisir_ID_editeur, name='saisir_editeur_ID'),
    path('editeurs/delete/',EditeurDelete.as_view(), name='editeurs_delete'),
    path('editeurs/research/', EditeurResearch.as_view(), name='editeurs_research'),


    path('auteurs/', AuteurList.as_view(), name='auteurs_list'),
    path('auteurs/create/', AuteurCreate.as_view(), name='auteurs_create'),
    path('auteurs/delete/',AuteurDelete.as_view(),name='auteurs_delete'),
    path('auteurs/update/<int:auteur_id>/',AuteurUpdate.as_view(), name='auteurs_update'),
    path('auteurs/research/', AuteurResearch.as_view(), name='auteurs_research'),
    path('auteurs/saisir_auteur_ID/',saisir_ID_auteur, name='saisir_auteur_ID'),


    path('livres/', LivreList.as_view(), name='livres_list'),
    path('livres/create/', create_livre, name='livres_create'),
    path('livres/delete/',LivreDelete.as_view(), name='livres_delete'),
    path('livres/saisir_isbn/', saisir_isbn, name='saisir_isbn'),  # Page pour saisir l'ISBN
    path('livres/update/<str:isbn13>/', LivreUpdate.as_view(), name='livre_update'),  # Page pour modifier le livre
    path('livres/research/', LivreResearch.as_view(), name='livres_research'),


    path('ecrits/', EcrireList.as_view(), name='ecrits_list'),
    path('ecrits/create/', EcrireCreate.as_view(), name='ecrits_create'),


    path('illustrateurs/', IllustrateurList.as_view(), name='illustrateurs_list'),
    path('illustrateurs/create/', IllustrateurCreate.as_view(), name='illustrateurs_create'),
    path('illustrateurs/delete/', IllustrateurDelete.as_view(), name='illustrateurs_delete'),
    path('illustrateurs/update/<int:illustrateur_id>/', IllustrateurUpdate.as_view(), name='illustrateurs_update'),
    path('illustrateurs/research/', IllustrateurResearch.as_view(), name='illustrateurs_research'),
    path('illustrateurs/saisir_illustrateur_ID/', saisir_ID_illustrateur, name='saisir_illustrateur_ID'),


    path('traducteurs/', TraducteurList.as_view(), name='traducteurs_list'),
    path('traducteurs/create/', TraducteurCreate.as_view(), name='traducteurs_create'),
    path('traducteurs/delete/', TraducteurDelete.as_view(), name='traducteurs_delete'),
    path('traducteurs/update/<int:traducteur_id>/', TraducteurUpdate.as_view(), name='traducteurs_update'),
    path('traducteurs/research/', TraducteurResearch.as_view(), name='traducteurs_research'),
    path('traducteurs/saisir_traducteur_ID/', saisir_ID_traducteur, name='saisir_traducteur_ID'),

    path('achats/', AchatList.as_view(), name='achats_list'),
    path('achats/create/', AchatCreate.as_view(), name='achats_create'),
    path('achats/update/<int:pk>/', AchatUpdate.as_view(), name='achats_update'),
    path('achats/delete/<int:pk>/', AchatDelete.as_view(), name='achats_delete'),
    path('achats/search/', AchatSearchResult.as_view(), name='search_achats_result'),

    path('commandes/', CommanderList.as_view(), name='commandes_list'),
    path('commandes/create/', CommanderCreate.as_view(), name='commandes_create'),
    path('commandes/update/<int:pk>/', CommanderUpdate.as_view(), name='commandes_update'),
    path('commandes/delete/', CommanderDelete.as_view(), name='commandes_delete'),
    path('commandes/delete/<int:pk>/', CommanderDelete.as_view(), name='commandes_with_ID_delete'),
    path('commandes/search/', CommanderSearchResult.as_view(), name='search_commandes_result'),
    path('commandes/terminer/<int:pk>/', terminer_commande, name='terminer_commande'),
    path('commandes/saisir_commande_ID/', saisir_ID_commande, name='saisir_commande_ID'),



    path('reservations/', ReserverList.as_view(), name='reservations_list'),
    path('reservations/create/', ReserverCreate.as_view(), name='reservations_create'),
    path('reservations/update/<int:pk>/', ReserverUpdate.as_view(), name='reservations_update'),
    path('reservations/delete/<int:pk>/', ReserverDelete.as_view(), name='reservations_delete'),
    path('reservations/search/', ReserverSearchResult.as_view(), name='reservations_search'),

    path('reservations/<int:pk>/terminer/', terminer_reservation, name='terminer_reservation'),

    # Liste des fournisseurs avec possibilité de recherche
    path('fournisseurs/', FournisseurList.as_view(), name='fournisseurs_list'),

    # Vue de recherche des fournisseurs
    path('fournisseurs/search/', FournisseurResearch.as_view(), name='fournisseurs_search'),

    # Création d'un nouveau fournisseur
    path('fournisseurs/ajouter/', FournisseurCreate.as_view(), name='fournisseur_create'),

    # Suppression d'un fournisseur
    path('fournisseurs/supprimer/', FournisseurDelete.as_view(), name='fournisseur_delete'),

    # Modification d'un fournisseur spécifique identifié par 'nom_fournisseur'
    path('fournisseurs/modifier/<str:nom_fournisseur>/', FournisseurUpdate.as_view(), name='fournisseurs_update'),

    # Saisie du nom du fournisseur pour redirection vers la modification
    path('fournisseurs/saisir_id/', SaisirIDFournisseurView.as_view(), name='saisir_id_fournisseur'),


    path('notifications/', NotificationList.as_view(), name='notifications_list')
]
