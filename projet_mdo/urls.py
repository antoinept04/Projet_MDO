from django.contrib import admin
from django.urls import path

from gui.views import custom_404_view
from gui.views import (
    home, loginPage, logoutUser,
    RoleList, RoleCreate,
    VilleList, VilleCreate, VilleDelete, VilleUpdate,
    AdresseList, create_adresse, AdresseDelete, AdresseResearch,
    PersonneList, personne_create, PersonneDelete, PersonneUpdate, PersonneResearch, PersonneSelectView,
    EditeurList, EditeurCreate, EditeurDelete, EditeurUpdate, EditeurResearch, saisir_ID_editeur,
    ContributeurList, ContributeurCreate, ContributeurDelete, ContributeurUpdate, ContributeurResearch,
    saisir_ID_contributeur,
    LivreList, create_livre, LivreDelete, LivreUpdate, LivreResearch, saisir_isbn,
    FournisseurList, fournisseur_create, FournisseurDelete, FournisseurUpdate, FournisseurResearch,
    SaisirIDFournisseurView,
    CommanderList, CommanderCreate, CommanderDelete, CommanderUpdate, CommanderResearch, saisir_ID_commande,
    terminer_commande,
    ReserverList, ReserverCreate, ReserverDelete, ReserverUpdate, ReserverResearch, saisir_ID_reservation,
    terminer_reservation,
    AchatList, AchatCreate, AchatDelete, AchatUpdate, AchatResearch, saisir_ID_achat,
    NotificationList, check_reservations, mark_notification_done, delete_notification, autres

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='homepage'),
    path('autres/', autres, name='autres'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),

    path('roles/', RoleList.as_view(), name='roles_list'),
    path('roles/create/', RoleCreate.as_view(), name='roles_create'),


    path('villes/', VilleList.as_view(), name='villes_list'),
    path('villes/create/', VilleCreate.as_view(), name='villes_create'),
    path('ville/<int:pk>/update/', VilleUpdate.as_view(), name='ville_update'),
    path('ville/<int:pk>/delete/', VilleDelete.as_view(), name='ville_delete'),

    path('adresses/', AdresseList.as_view(), name='adresses_list'),
    path('adresses/create/', create_adresse, name='adresses_create'),
    path('adresses/research/', AdresseResearch.as_view(), name='adresses_research'),
    path('adresses/delete/',AdresseDelete.as_view(), name='adresses_delete'),


    path('personnes/', PersonneList.as_view(), name='personnes_list'),
    path('personnes/create/', personne_create, name='personnes_create'),
    path('personnes/research/', PersonneResearch.as_view(), name='personnes_research'),
    path('personnes/delete/',PersonneDelete.as_view(), name='personnes_delete'),
    path('personnes/modifier/', PersonneSelectView.as_view(), name='personnes_select'),
    path('personnes/modifier/<str:email>/', PersonneUpdate.as_view(), name='personnes_update'),


    path('editeurs/', EditeurList.as_view(), name='editeurs_list'),
    path('editeurs/create/', EditeurCreate.as_view(), name='editeurs_create'),
    path('editeurs/update/<int:id>',EditeurUpdate.as_view(), name='editeurs_update'),
    path('editeurs/saisir_editeur_ID/', saisir_ID_editeur, name='saisir_editeur_ID'),
    path('editeurs/delete/',EditeurDelete.as_view(), name='editeurs_delete'),
    path('editeurs/research/', EditeurResearch.as_view(), name='editeurs_research'),


    path('contributeurs/', ContributeurList.as_view(), name='contributeurs_list'),
    path('contributeurs/create/', ContributeurCreate.as_view(), name='contributeurs_create'),
    path('contributeurs/delete/',ContributeurDelete.as_view(),name='contributeurs_delete'),
    path('contributeurs/update/<int:pk>/',ContributeurUpdate.as_view(), name='contributeurs_update'),
    path('contributeurs/research/', ContributeurResearch.as_view(), name='contributeurs_research'),
    path('contributeurs/saisir_contributeur_ID/',saisir_ID_contributeur, name='saisir_contributeur_ID'),


    path('livres/', LivreList.as_view(), name='livres_list'),
    path('livres/create/', create_livre, name='livres_create'),
    path('livres/delete/',LivreDelete.as_view(), name='livres_delete'),
    path('livres/saisir_isbn/', saisir_isbn, name='saisir_isbn'),
    path('livres/update/<str:isbn13>/', LivreUpdate.as_view(), name='livre_update'),
    path('livres/research/', LivreResearch.as_view(), name='livres_research'),

    path('achats/', AchatList.as_view(), name='achats_list'),
    path('achats/create/', AchatCreate.as_view(), name='achats_create'),
    path('achats/update/<int:pk>/', AchatUpdate.as_view(), name='achats_update'),
    path('achats/delete/', AchatDelete.as_view(), name='achats_delete'),
    path('achats/delete/<int:pk>/', AchatDelete.as_view(), name='achats_with_ID_delete'),
    path('achats/search/', AchatResearch.as_view(), name='achats_research'),
    path('achats/saisir_achat_ID/', saisir_ID_achat, name='saisir_achat_ID'),

    path('commandes/', CommanderList.as_view(), name='commandes_list'),
    path('commandes/create/', CommanderCreate.as_view(), name='commandes_create'),
    path('commandes/update/<int:pk>/', CommanderUpdate.as_view(), name='commandes_update'),
    path('commandes/delete/', CommanderDelete.as_view(), name='commandes_delete'),
    path('commandes/delete/<int:pk>/', CommanderDelete.as_view(), name='commandes_with_ID_delete'),
    path('commandes/search/', CommanderResearch.as_view(), name='commandes_research'),
    path('commandes/terminer/<int:pk>/', terminer_commande, name='terminer_commande'),
    path('commandes/saisir_commande_ID/', saisir_ID_commande, name='saisir_commande_ID'),

    path('reservations/', ReserverList.as_view(), name='reservations_list'),
    path('reservations/create/', ReserverCreate.as_view(), name='reservations_create'),
    path('reservations/update/<int:pk>/', ReserverUpdate.as_view(), name='reservations_update'),
    path('reservations/delete/', ReserverDelete.as_view(), name='reservations_delete'),
    path('reservations/delete/<int:pk>/', ReserverDelete.as_view(), name='reservations_with_ID_delete'),
    path('reservations/search/', ReserverResearch.as_view(), name='reservations_research'),
    path('reservations/terminer/<int:pk>/', terminer_reservation, name='terminer_reservation'),
    path('reservations/saisir_reservation_ID/', saisir_ID_reservation, name='saisir_reservation_ID'),



    path('fournisseurs/', FournisseurList.as_view(), name='fournisseurs_list'),

    path('fournisseurs/search/', FournisseurResearch.as_view(), name='fournisseurs_search'),

    path('fournisseurs/ajouter/',fournisseur_create, name='fournisseur_create'),

    path('fournisseurs/supprimer/<int:pk>', FournisseurDelete.as_view(), name='fournisseur_delete'),

    path('fournisseurs/modifier/<int:pk>/', FournisseurUpdate.as_view(), name='fournisseurs_update'),

    path('fournisseurs/saisir_id/', SaisirIDFournisseurView.as_view(), name='saisir_id_fournisseur'),


    path('notifications/', NotificationList.as_view(), name='notifications_list'),
    path('notifications/<int:notification_id>/done/', mark_notification_done, name='mark_notification_done'),
    path('notifications/<int:notification_id>/delete/', delete_notification, name='delete_notification'),
    path('check_reservations/', check_reservations, name='check_reservations'),
]


handler404 = custom_404_view