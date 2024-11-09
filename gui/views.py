from django.http import  HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from gui.models import Ville, Adresse, Role, Personne, Fournisseur, Editeur, Auteur, Livre, Ecrire, Commander, Notifier, Achat, Reserver

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

# 1. Classe Ville
class VilleList(ListView):
    model = Ville
    template_name = 'gui/lister_villes.html'

class VilleCreate(CreateView):
    model = Ville
    fields = ['nom', 'code_postal', 'pays']
    template_name = 'gui/ajouter_ville.html'
    success_url = reverse_lazy('villes_list')



# 2. Classe Adresse
class AdresseList(ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'


class AdresseCreate(CreateView):
    model = Adresse
    fields = ['rue', 'n_rue', 'ville']
    template_name = 'gui/ajouter_adresse.html'
    success_url = reverse_lazy('adresses_list')

# 3. Classe Role
class RoleList(ListView):
    model = Role
    template_name = 'gui/lister_roles.html'

class RoleCreate(CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')

# 4. Classe Personne
class PersonneList(ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'

class PersonneCreate(CreateView):
    model = Personne
    fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'mot_de_passe', 'solde', 'adresse', 'role']
    template_name = 'gui/ajouter_personne.html'
    success_url = reverse_lazy('personnes_list')

# 5. Classe Fournisseur
class FournisseurList(ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'

class FournisseurCreate(CreateView):
    model = Fournisseur
    fields = ['nom']
    template_name = 'gui/ajouter_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

# 6. Classe Editeur
class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

class EditeurCreate(CreateView):
    model = Editeur
    fields = ['nom']
    template_name = 'gui/ajouter_editeur.html'
    success_url = reverse_lazy('editeurs_list')

# 7. Classe Auteur
class AuteurList(ListView):
    model = Auteur
    template_name = 'gui/lister_auteurs.html'

class AuteurCreate(CreateView):
    model = Auteur
    fields = ['nom', 'prenom', 'date_naissance']
    template_name = 'gui/ajouter_auteur.html'
    success_url = reverse_lazy('auteurs_list')

# 8. Classe Livre
class LivreList(ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

class LivreCreate(CreateView):
    model = Livre
    fields = ['isbn13', 'titre', 'type', 'genre_litteraire', 'sous_genre', 'illustrateur', 'langue', 'format',
              'nombre_pages', 'dimensions', 'date_parution', 'localisation', 'synopsis', 'prix', 'url_reference',
              'traducteur', 'quantite_disponible', 'quantite_totale', 'quantite_minimale', 'editeur']
    template_name = 'gui/ajouter_livre.html'
    success_url = reverse_lazy('livres_list')

# 9. Classe Ecrire
class EcrireList(ListView):
    model = Ecrire
    template_name = 'gui/lister_ecrits.html'

class EcrireCreate(CreateView):
    model = Ecrire
    fields = ['livre', 'auteur']
    template_name = 'gui/ajouter_ecrire.html'
    success_url = reverse_lazy('ecrits_list')

# 10. Classe Commander
class CommanderList(ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'

class CommanderCreate(CreateView):
    model = Commander
    fields = ['personne', 'livre', 'date_commande', 'quantite', 'statut']
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')

# 11. Classe Notifier
class NotifierList(ListView):
    model = Notifier
    template_name = 'gui/lister_notifications.html'

class NotifierCreate(CreateView):
    model = Notifier
    fields = ['personne', 'livre', 'quantite', 'type', 'commentaire']
    template_name = 'gui/ajouter_notification.html'
    success_url = reverse_lazy('notifications_list')

# 12. Classe Achat
class AchatList(ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'

class AchatCreate(CreateView):
    model = Achat
    fields = ['personne', 'livre', 'quantite', 'date_achat']
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')

# 13. Classe Reserver
class ReserverList(ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'

class ReserverCreate(CreateView):
    model = Reserver
    fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')


